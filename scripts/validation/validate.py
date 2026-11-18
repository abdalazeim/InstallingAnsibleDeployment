#!/usr/bin/env python3
"""Validate catalog references locally; optionally run real Ansible syntax checks."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import yaml
from jinja2 import Environment

ROOT=Path(__file__).resolve().parents[2]


def validate():
    errors=[]; documents=0
    for folder in ['roles','playbooks','inventories','collections']:
        for path in (ROOT/folder).rglob('*.yml'):
            try:
                value=yaml.safe_load(path.read_text(encoding='utf-8')); documents+=1
                def visit(item):
                    if isinstance(item,str): Environment().parse(item)
                    elif isinstance(item,list):
                        for child in item: visit(child)
                    elif isinstance(item,dict):
                        for child in item.values(): visit(child)
                visit(value)
            except Exception as exc: errors.append(f'{path.relative_to(ROOT)}: {exc}')
    catalog=json.loads((ROOT/'semaphore/templates/catalog.json').read_text())['operations']
    seen=set()
    for entry in catalog:
        if entry['id'] in seen: errors.append('Duplicate operation '+entry['id'])
        seen.add(entry['id'])
        path=(ROOT/entry['playbook']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file(): errors.append('Missing/unsafe playbook '+entry['id'])
        else:
            play=yaml.safe_load(path.read_text())[0]
            if play['vars']['operation_risk']!=entry['risk']: errors.append('Risk mismatch '+entry['id'])
            if not any(t.get('ansible.builtin.import_role',{}).get('name')=='common' for t in play.get('pre_tasks',[])):
                errors.append('Missing safety policy '+entry['id'])
    # Resolve includes and templates in every supported role, not historical scaffolds.
    for path in (ROOT/'roles').glob('*/tasks/*.yml'):
        role=path.parents[1]
        def tasks(entries):
            for entry in entries or []:
                for section in ['block','rescue','always']: tasks(entry.get(section,[]))
                for key in ['ansible.builtin.include_tasks','ansible.builtin.import_tasks']:
                    if key in entry:
                        spec=entry[key]; name=spec if isinstance(spec,str) else spec['file']
                        if '{{' not in name and not (path.parent/name).is_file(): errors.append(f'Missing include: {path}:{name}')
                if 'ansible.builtin.include_role' in entry:
                    spec=entry['ansible.builtin.include_role']
                    target=ROOT/'roles'/spec['name']/'tasks'/(spec.get('tasks_from','main')+'.yml')
                    if not target.is_file(): errors.append('Missing role entry: '+str(target))
                if 'ansible.builtin.template' in entry:
                    source=entry['ansible.builtin.template']['src']
                    if '{{' not in source and not (role/'templates'/source).is_file(): errors.append('Missing template '+str(role/source))
        tasks(yaml.safe_load(path.read_text()))
    return {'yaml_documents':documents,'catalog_operations':len(catalog),'errors':errors}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--syntax',action='store_true'); args=p.parse_args()
    result=validate(); print(json.dumps(result,indent=2))
    if result['errors']: return 1
    if args.syntax:
        for entry in json.loads((ROOT/'semaphore/templates/catalog.json').read_text())['operations']:
            run=subprocess.run(['ansible-playbook','--syntax-check','-i','inventories/build/hosts.yml',entry['playbook']],cwd=ROOT,check=False)
            if run.returncode: return run.returncode
    return 0


if __name__=='__main__': sys.exit(main())
