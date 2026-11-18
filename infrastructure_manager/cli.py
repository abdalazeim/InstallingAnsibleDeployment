"""Allowlisted CLI; execution always uses argv and never a shell."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ALIASES = {
    'system users list':'system.users_list', 'system firewall status':'system.firewall_status',
    'docker list':'docker.list_containers','docker start':'docker.start_container',
    'docker stop':'docker.stop_container','docker restart':'docker.restart_container',
    'odoo list':'odoo.list_instances','odoo status':'odoo.health_check','odoo backup':'odoo.backup_full',
    'postgres databases list':'postgresql.list_databases','postgres backup':'postgresql.backup',
    'traefik status':'networking.traefik_status','monitoring health':'monitoring.server_health'}
GLOBAL_INPUTS = {'confirm_operation','confirm_production','confirm_destructive_operation','confirm_reboot',
                 'deployment_backup_verified','confirm_downtime','target_hosts'}


def project_root(value=None):
    candidates=[value,os.environ.get('INFRASTRUCTURE_PROJECT'),str(Path.cwd()),str(Path(__file__).resolve().parents[1])]
    config=Path('/etc/infrastructure-manager/project-path')
    if config.is_file(): candidates.append(config.read_text().strip())
    for candidate in candidates:
        if candidate and (Path(candidate)/'semaphore/templates/catalog.json').is_file():
            return Path(candidate).resolve()
    raise ValueError('Project not found; use --project or INFRASTRUCTURE_PROJECT')


def load_catalog(root):
    operations=json.loads((root/'semaphore/templates/catalog.json').read_text())['operations']
    result={}
    for operation in operations:
        path=(root/operation['playbook']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError('Catalog points outside the project or to a missing playbook')
        if operation['id'] in result: raise ValueError('Duplicate operation ID')
        result[operation['id']]=operation
    return result


def resolve_operation(words, catalog):
    for count in range(len(words),0,-1):
        phrase=' '.join(words[:count]); key=ALIASES.get(phrase,phrase.replace(' ','.'))
        if key in catalog:
            return catalog[key],words[count:]
    raise ValueError('Unknown operation. Use infrastructure-manager catalog')


def parse_values(items, operation, positional):
    values={}
    for item in items:
        if '=' not in item: raise ValueError('--set requires key=value')
        key,value=item.split('=',1)
        if key not in operation['inputs'] and key not in GLOBAL_INPUTS:
            raise ValueError('Input is not allowed for this operation: '+key)
        try: value=json.loads(value)
        except json.JSONDecodeError: pass
        values[key]=value
    if positional:
        selectors=[x for x in ['container_name','odoo_instance','django_application','database_name'] if x in operation['inputs']]
        if len(positional)!=1 or len(selectors)!=1: raise ValueError('Use explicit --set inputs for this operation')
        values[selectors[0]]=positional[0]
    missing=[key for key,spec in operation['inputs'].items() if spec['required'] and key not in values]
    if missing: raise ValueError('Missing operation inputs: '+', '.join(missing))
    for key,spec in operation['inputs'].items():
        if key in values and spec.get('choices') and values[key] not in spec['choices']:
            raise ValueError('Invalid choice for '+key)
    return values


def secure_json(path, data):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream: json.dump(data,stream,indent=2)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',nargs='+')
    parser.add_argument('--project'); parser.add_argument('--inventory',default='inventories/dev/hosts.yml')
    parser.add_argument('--limit'); parser.add_argument('--check',action='store_true'); parser.add_argument('--diff',action='store_true')
    parser.add_argument('--verbose',action='count',default=0); parser.add_argument('--timeout',type=int,default=3600)
    parser.add_argument('--json',action='store_true'); parser.add_argument('--set',action='append',default=[])
    parser.add_argument('--plan',action='store_true',help='Validate inputs and print a command preview without running Ansible')
    args=parser.parse_args(argv)
    try:
        root=project_root(args.project); catalog=load_catalog(root)
        if args.operation==['catalog']:
            print(json.dumps(list(catalog.values()),indent=2) if args.json else '\n'.join(f'{k}: {v["name"]}' for k,v in catalog.items()))
            return 0
        operation,positional=resolve_operation(args.operation,catalog)
        values=parse_values(args.set,operation,positional)
        if args.timeout<1: raise ValueError('Timeout must be positive')
        if operation['risk']!='read' and values.get('confirm_operation') is not True:
            raise ValueError('Changes require --set confirm_operation=true (including check mode)')
        if operation['risk']=='destructive' and values.get('confirm_destructive_operation') is not True:
            raise ValueError('This operation also requires confirm_destructive_operation=true')
        inventory=Path(args.inventory)
        if not inventory.is_absolute(): inventory=root/inventory
        inventory=inventory.resolve()
        if not inventory.is_file(): raise ValueError('Inventory file does not exist')
        command=['ansible-playbook','-i',str(inventory),str(root/operation['playbook'])]
        if args.limit: command+=['--limit',args.limit]
        if args.check: command+=['--check']
        if args.diff: command+=['--diff']
        if args.verbose: command+=['-'+'v'*min(args.verbose,3)]
        if args.plan:
            print(json.dumps({'operation':operation['id'],'argv':command,'input_names':sorted(values),'executed':False},indent=2))
            return 0
        if os.name!='posix': raise ValueError('Execution requires Ubuntu; use --plan on other platforms')
        report_dir=root/'reports'; report_dir.mkdir(mode=0o700,exist_ok=True)
        run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-')+uuid.uuid4().hex[:12]
        varfile=report_dir/(run_id+'.vars.json'); secure_json(varfile,values)
        command+=['--extra-vars','@'+str(varfile)]
        started=time.monotonic(); started_at=datetime.now(timezone.utc).isoformat()
        env=dict(os.environ,ANSIBLE_CONFIG=str(root/'ansible.cfg'),INFRASTRUCTURE_RUN_ID=run_id,
                 INFRASTRUCTURE_REPORT_DIR=str(report_dir),INFRASTRUCTURE_OPERATION=operation['id'])
        log=report_dir/(run_id+'.log'); exit_code=1
        try:
            fd=os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'w') as stream:
                try:
                    result=subprocess.run(command,cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT,
                                          timeout=args.timeout,check=False)
                    exit_code=result.returncode
                except subprocess.TimeoutExpired: exit_code=124
                except FileNotFoundError: exit_code=127
        finally: varfile.unlink(missing_ok=True)
        stats_path=report_dir/(run_id+'.stats.json')
        stats=json.loads(stats_path.read_text()) if stats_path.is_file() else {'hosts':{}}
        if not stats['hosts'] and exit_code==0: exit_code=3
        report={'run_id':run_id,'operation':operation['id'],'inventory':str(inventory),'limit':args.limit,
                'started_at':started_at,'finished_at':datetime.now(timezone.utc).isoformat(),
                'duration_seconds':round(time.monotonic()-started,3),'exit_code':exit_code,
                'status':'passed' if exit_code==0 else 'failed','check_mode':args.check,'hosts':stats['hosts'],'log':str(log)}
        secure_json(report_dir/(run_id+'.json'),report)
        print(json.dumps(report,indent=2) if args.json else f'{operation["name"]}: {report["status"]}; report: {report_dir / (run_id+".json")}')
        return exit_code
    except (ValueError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({'status':'error','message':str(exc)}) if args.json else str(exc),file=sys.stderr)
        return 2


if __name__=='__main__': sys.exit(main())
