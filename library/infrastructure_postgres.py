#!/usr/bin/python
"""PostgreSQL operations for a native server or a Docker container.

Passwords are module secrets and travel through environment, never command argv.
Backups are confined to a dedicated root and verified before restore.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]{0,62}$")
BACKUP_ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{12}$")


def identifier(value):
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise ValueError("Invalid database or role identifier")
    return '"' + value + '"'


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def contained(root, name):
    root = Path(root).resolve()
    path = root / name
    if path.is_symlink() or path.resolve().parent != root:
        raise ValueError("Backup path must be a regular child of backup_root")
    return path


class PostgreSQL:
    def __init__(self, connection, root, timeout=1800):
        self.connection = connection
        self.root = Path(root)
        if not self.root.is_absolute() or self.root == Path('/'):
            raise ValueError("A dedicated absolute backup_root is required")
        if connection.get('mode', 'native') not in ('native', 'docker'):
            raise ValueError('Connection mode must be native or docker')
        self.timeout = timeout

    def command(self, tool, args):
        c = self.connection
        argv = [tool]
        if tool not in ('pg_restore',) or '--list' not in args:
            argv += ['--host', str(c.get('host', '/var/run/postgresql')),
                     '--port', str(c.get('port', 5432)), '--username', str(c.get('user', 'postgres'))]
        argv += args
        if c.get('mode', 'native') == 'docker':
            container = c.get('container', '')
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', container):
                raise ValueError('Invalid PostgreSQL container name')
            argv = ['docker', 'exec', '-i', '--env', 'PGPASSWORD', container] + argv
        elif c.get('os_user'):
            if not re.fullmatch(r'[a-z_][a-z0-9_-]*', c['os_user']):
                raise ValueError('Invalid native OS user')
            argv = ['runuser', '--preserve-environment', '-u', c['os_user'], '--'] + argv
        return argv

    def run(self, tool, args, *, source=None, destination=None, text=None):
        env = dict(os.environ)
        env['PGPASSWORD'] = str(self.connection.get('password', ''))
        env['PGCONNECT_TIMEOUT'] = '10'
        result = subprocess.run(self.command(tool, args), input=text.encode() if text else None,
                                stdin=source, stdout=destination or subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env, timeout=self.timeout, check=False)
        if result.returncode:
            # SQL text and server errors can contain secrets; never forward them.
            raise RuntimeError(f'{tool} failed (exit {result.returncode}); inspect protected server logs')
        return (result.stdout or b'').decode('utf-8', errors='replace')

    def sql(self, sql, database='postgres'):
        # SQL travels on stdin, keeping role passwords out of process arguments.
        return self.run('psql', ['--no-psqlrc', '--no-password', '--tuples-only', '--no-align',
                                '--set', 'ON_ERROR_STOP=1', '--dbname', database], text=sql)

    def verify(self, backup_id):
        if not BACKUP_ID.fullmatch(backup_id):
            raise ValueError('Invalid backup ID')
        manifest_path = contained(self.root, backup_id + '.json')
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('schema_version') != 1 or manifest.get('kind') != 'postgresql':
            raise ValueError('Unsupported backup manifest')
        if manifest.get('backup_id') != backup_id or manifest.get('format') not in ('custom','sql'):
            raise ValueError('Manifest identity/format mismatch')
        path = contained(self.root, manifest['file'])
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError('Missing or empty backup')
        if path.stat().st_size != manifest['size_bytes'] or digest(path) != manifest['sha256']:
            raise ValueError('Backup checksum or size mismatch')
        if manifest['format'] == 'custom':
            with path.open('rb') as stream:
                self.run('pg_restore', ['--list'], source=stream)
        return manifest, path

    def backup(self, database, format='custom'):
        identifier(database)
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        backup_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:12]
        target = contained(self.root, backup_id + ('.dump' if format == 'custom' else '.sql'))
        descriptor, tmp = tempfile.mkstemp(prefix='.partial-', dir=self.root)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                self.run('pg_dump', ['--no-password','--format', 'c' if format == 'custom' else 'p',
                                    '--dbname', database], destination=stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, target)
            manifest = {'schema_version':1,'kind':'postgresql','backup_id':backup_id,'database':database,
                        'format':format,'file':target.name,'sha256':digest(target),
                        'size_bytes':target.stat().st_size,'created_at':datetime.now(timezone.utc).isoformat(),
                        'server_version':self.sql('SHOW server_version;').strip()}
            mp = contained(self.root, backup_id + '.json')
            fd = os.open(mp, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
            with os.fdopen(fd,'w') as stream:
                json.dump(manifest, stream, indent=2)
            self.verify(backup_id)
            return manifest
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def restore(self, backup_id, database, check_mode=False):
        quoted = identifier(database)
        manifest, path = self.verify(backup_id)
        exists = self.sql("SELECT 1 FROM pg_database WHERE datname = '" + database + "';").strip()
        if exists:
            raise ValueError('Restore requires a NEW database; overwriting existing databases is refused')
        source_major = manifest['server_version'].split('.')[0]
        dest_major = self.sql('SHOW server_version;').strip().split('.')[0]
        if source_major != dest_major:
            raise ValueError('Cross-major restore requires a separately validated migration procedure')
        if check_mode:
            return {'changed':True,'backup_id':backup_id,'database':database,'preview':True}
        self.sql(f'CREATE DATABASE {quoted} TEMPLATE template0;')
        # Keep a failed new database for diagnosis. Never drop it automatically.
        with path.open('rb') as stream:
            if manifest['format'] == 'custom':
                self.run('pg_restore', ['--exit-on-error','--single-transaction','--no-owner',
                                       '--no-privileges','--dbname',database], source=stream)
            else:
                self.run('psql', ['--no-psqlrc','--set','ON_ERROR_STOP=1','--single-transaction',
                                 '--dbname',database], source=stream)
        self.sql('SELECT 1;', database)
        return {'changed':True,'backup_id':backup_id,'database':database,'connection_verified':True}


def execute(p, check_mode=False):
    db=PostgreSQL(p['connection'],p['backup_root'],p.get('timeout',1800))
    action=p['action']; name=p.get('database','')
    queries={
        'health':'SELECT json_build_object(\'version\', version(), \'ready\', true);',
        'list':"SELECT coalesce(json_agg(t),'[]'::json) FROM (SELECT datname AS name, pg_database_size(oid) AS size_bytes FROM pg_database WHERE NOT datistemplate) t;",
        'connections':"SELECT coalesce(json_agg(t),'[]'::json) FROM (SELECT datname, usename, state, count(*) FROM pg_stat_activity GROUP BY datname,usename,state) t;"}
    if action in queries:
        return {'changed':False,'data':json.loads(db.sql(queries[action]))}
    if action=='info':
        identifier(name)
        return {'changed':False,'data':json.loads(db.sql("SELECT json_build_object('name', current_database(), 'size_bytes', pg_database_size(current_database()));",name))}
    if action=='verify':
        manifest,_=db.verify(p['backup_id'])
        return {'changed':False,'backup':manifest,'verified':True}
    if action=='backup':
        if check_mode:
            return {'changed':True,'preview':True}
        return {'changed':True,'backup':db.backup(name,p.get('format','custom'))}
    if action=='restore':
        if not p.get('confirmed'):
            raise ValueError('Explicit destructive confirmation required')
        return db.restore(p['backup_id'],name,check_mode)
    if action=='user':
        role=p['username']; quoted_role=identifier(role)
        if role in ('postgres',db.connection.get('user','postgres')):
            raise ValueError('Refusing changes to the connection or postgres administrator role')
        present=bool(db.sql("SELECT 1 FROM pg_roles WHERE rolname = '"+role+"';").strip())
        absent=p.get('user_state','present')=='absent'
        if absent:
            if not p.get('confirmed'): raise ValueError('Explicit destructive confirmation required')
            if present and not check_mode: db.sql(f'DROP ROLE {quoted_role};')
            return {'changed':present,'username':role}
        password=p.get('user_password','')
        if not present and not password: raise ValueError('A new login role requires a password')
        if not check_mode:
            if not present: db.sql(f'CREATE ROLE {quoted_role} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;')
            if password and (not present or p.get('rotate_password',False)):
                literal="'"+password.replace("'","''")+"'"
                db.sql(f'ALTER ROLE {quoted_role} PASSWORD {literal};')
        return {'changed':not present or bool(password and p.get('rotate_password',False)),'username':role}
    if action=='privileges':
        role=identifier(p['username']); database=identifier(name)
        privilege=p.get('privilege','CONNECT')
        if privilege not in ('CONNECT','CREATE','TEMPORARY'):
            raise ValueError('Only CONNECT, CREATE and TEMPORARY database privileges are supported')
        verb='REVOKE' if p.get('revoke',False) else 'GRANT'
        if not check_mode:
            db.sql(f'{verb} {privilege} ON DATABASE {database} '+('FROM ' if verb=='REVOKE' else 'TO ')+role+';')
        return {'changed':True,'database':name,'username':p['username']}
    quoted=identifier(name)
    exists=bool(db.sql("SELECT 1 FROM pg_database WHERE datname = '"+name+"';").strip())
    if action=='create':
        if not exists and not check_mode:
            db.sql(f'CREATE DATABASE {quoted};')
        return {'changed':not exists,'database':name}
    if action=='delete':
        if not p.get('confirmed') or name in ('postgres','template0','template1'):
            raise ValueError('Protected database or missing destructive confirmation')
        if exists and not check_mode:
            db.sql(f'DROP DATABASE {quoted};')
        return {'changed':exists,'database':name}
    raise ValueError('Unsupported operation')


def main():
    from ansible.module_utils.basic import AnsibleModule
    module=AnsibleModule(argument_spec={
        'action':{'type':'str','required':True,'choices':['health','list','info','connections','create','delete','backup','restore','verify','user','privileges']},
        'connection':{'type':'dict','required':True,'no_log':True},
        'backup_root':{'type':'path','default':'/var/backups/infrastructure/postgresql'},
        'database':{'type':'str','default':''},'backup_id':{'type':'str','default':''},
        'format':{'type':'str','choices':['custom','sql'],'default':'custom'},
        'confirmed':{'type':'bool','default':False},'timeout':{'type':'int','default':1800},
        'username':{'type':'str','default':''},'user_state':{'type':'str','choices':['present','absent'],'default':'present'},
        'user_password':{'type':'str','no_log':True,'default':''},'rotate_password':{'type':'bool','default':False},
        'privilege':{'type':'str','default':'CONNECT'},'revoke':{'type':'bool','default':False}},supports_check_mode=True)
    try:
        module.exit_json(**execute(module.params,module.check_mode))
    except (ValueError,RuntimeError,OSError,KeyError,json.JSONDecodeError,subprocess.TimeoutExpired) as exc:
        module.fail_json(msg=str(exc) if isinstance(exc,(ValueError,RuntimeError)) else 'Database operation failed; inspect protected server logs')


if __name__=='__main__':
    main()
