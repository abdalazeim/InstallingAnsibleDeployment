#!/usr/bin/python
"""Confined file backups with manifests, checksums and new-directory restore."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile
import uuid

ID = re.compile(r'^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{12}$')


def sha(path):
    result=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            result.update(block)
    return result.hexdigest()


def child(root,name):
    p=root/name
    if p.is_symlink() or p.resolve().parent != root.resolve():
        raise ValueError('Backup paths must be direct children of backup_root')
    return p


def verify(root,backup_id):
    if not ID.fullmatch(backup_id):
        raise ValueError('Invalid backup ID')
    manifest=json.loads(child(root,backup_id+'.json').read_text())
    if manifest.get('kind')!='files' or manifest.get('backup_id')!=backup_id or manifest.get('schema_version')!=1:
        raise ValueError('Invalid file backup manifest')
    archive=child(root,manifest['file'])
    if not archive.is_file() or archive.stat().st_size!=manifest['size_bytes'] or sha(archive)!=manifest['sha256']:
        raise ValueError('Backup missing, truncated or checksum mismatch')
    with tarfile.open(archive,'r:gz') as tf:
        for member in tf:
            path=PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts or not (member.isfile() or member.isdir()):
                raise ValueError('Archive contains unsafe paths, links or special files')
    return manifest,archive


def execute(p,check_mode=False):
    root=Path(p['backup_root'])
    if not root.is_absolute() or root.resolve()==Path('/') or root.is_symlink():
        raise ValueError('A dedicated absolute backup directory is required')
    action=p['action']
    if action=='list':
        entries=[]
        if root.exists():
            for path in sorted(root.glob('*.json')):
                if ID.fullmatch(path.stem) and not path.is_symlink():
                    data=json.loads(path.read_text())
                    if data.get('kind')=='files':
                        entries.append({k:data[k] for k in ['backup_id','created_at','size_bytes','sha256']})
        return {'changed':False,'backups':entries}
    if action=='verify':
        manifest,_=verify(root,p['backup_id'])
        return {'changed':False,'backup':manifest,'verified':True}
    if action=='backup':
        source=Path(p['source'])
        if not source.is_absolute() or not source.is_dir() or source.is_symlink() or source.resolve()==Path('/'):
            raise ValueError('Backup source must be an existing dedicated directory')
        if root.resolve().is_relative_to(source.resolve()):
            raise ValueError('Backup root cannot be inside the source tree')
        if check_mode:
            return {'changed':True,'preview':True}
        root.mkdir(parents=True,exist_ok=True,mode=0o700)
        backup_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-')+uuid.uuid4().hex[:12]
        target=child(root,backup_id+'.tar.gz')
        fd,tmp=tempfile.mkstemp(prefix='.partial-',dir=root)
        os.close(fd)
        def safe_member(info):
            if not (info.isfile() or info.isdir()):
                raise ValueError('Source contains a symlink or special file; choose a regular-file source')
            return info
        try:
            with tarfile.open(tmp,'w:gz',dereference=False) as tf:
                tf.add(source,arcname='data',filter=safe_member)
            os.replace(tmp,target)
            manifest={'schema_version':1,'kind':'files','backup_id':backup_id,'file':target.name,
                      'created_at':datetime.now(timezone.utc).isoformat(),'size_bytes':target.stat().st_size,
                      'sha256':sha(target)}
            fd=os.open(child(root,backup_id+'.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w') as stream:
                json.dump(manifest,stream,indent=2)
            verify(root,backup_id)
            return {'changed':True,'backup':manifest}
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    if action=='restore':
        if not p['confirmed']: raise ValueError('Explicit restore confirmation required')
        manifest,archive=verify(root,p['backup_id'])
        destination=Path(p['destination']); allowed=Path(p['restore_root']).resolve()
        if (not destination.is_absolute() or not allowed.is_absolute() or allowed==Path('/') or
                destination.is_symlink() or not destination.resolve().is_relative_to(allowed) or destination.resolve()==allowed):
            raise ValueError('Restore destination must be a new child of restore_root')
        if destination.exists(): raise ValueError('Restore destination already exists; in-place restore refused')
        if not check_mode:
            destination.mkdir(parents=True,mode=0o700)
            with tarfile.open(archive,'r:gz') as tf:
                # verify() rejected all links and traversal. Exclusive new directory avoids replacing files.
                tf.extractall(destination)
        return {'changed':True,'backup_id':manifest['backup_id'],'destination':str(destination),'preview':check_mode}
    if action=='retention':
        if not p['confirmed']: raise ValueError('Explicit retention deletion confirmation required')
        days=p['retention_days']
        if days<1: raise ValueError('Retention must be at least one day')
        cutoff=datetime.now(timezone.utc)-timedelta(days=days); removed=[]
        if root.exists():
            candidates=sorted(root.glob('*.json'))
            for path in candidates:
                if not ID.fullmatch(path.stem) or path.is_symlink(): continue
                raw=json.loads(path.read_text())
                if raw.get('kind')!='files': continue
                manifest,archive=verify(root,path.stem)
                if datetime.fromisoformat(manifest['created_at']) < cutoff:
                    removed.append(path.stem)
                    if not check_mode:
                        archive.unlink(); path.unlink()
        return {'changed':bool(removed),'removed':removed,'preview':check_mode}
    raise ValueError('Unsupported archive operation')


def main():
    from ansible.module_utils.basic import AnsibleModule
    m=AnsibleModule(argument_spec={
        'action':{'type':'str','required':True,'choices':['backup','verify','restore','list','retention']},
        'backup_root':{'type':'path','required':True},'backup_id':{'type':'str','default':''},
        'source':{'type':'path','default':''},'destination':{'type':'path','default':''},
        'restore_root':{'type':'path','default':'/var/lib/infrastructure/restores'},
        'confirmed':{'type':'bool','default':False},'retention_days':{'type':'int','default':7}},supports_check_mode=True)
    try: m.exit_json(**execute(m.params,m.check_mode))
    except (ValueError,OSError,KeyError,tarfile.TarError,json.JSONDecodeError) as exc:
        m.fail_json(msg=str(exc) if isinstance(exc,ValueError) else 'Archive operation failed; inspect file permissions and backup metadata')


if __name__=='__main__': main()
