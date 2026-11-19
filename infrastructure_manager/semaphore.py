"""Reconcile Semaphore 2.19.12 resources using its supported HTTP API.

No resources are removed. Existing same-name credentials are reused, not rotated.
All created templates refer to real catalog playbooks. Execution is separate.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .cli import project_root, load_catalog

GROUPS={'system':'Ubuntu Server Management','docker':'Docker Infrastructure','odoo':'Odoo Management',
        'postgresql':'PostgreSQL Administration','networking':'Traefik & Networking','django':'Django Applications',
        'jenkins':'Jenkins Integration','backup':'Backup & Recovery','monitoring':'Monitoring & Health Checks'}


class APIError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise APIError('API redirects are refused to protect the authorization token')


class Client:
    def __init__(self,url,token,timeout=30):
        parsed=urlparse(url)
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('API URL must not contain credentials, query or fragment')
        if parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1','::1')):
            raise ValueError('Use HTTPS or an SSH tunnel to a loopback HTTP endpoint')
        if not token: raise ValueError('SEMAPHORE_API_TOKEN is required')
        self.url=url.rstrip('/')+'/api'; self.token=token; self.timeout=timeout
        self.opener=build_opener(NoRedirect())

    def request(self,method,path,data=None):
        if not path.startswith('/') or '..' in path: raise ValueError('Invalid API path')
        request=Request(self.url+path,data=json.dumps(data).encode() if data is not None else None,
                        headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json'},method=method)
        try:
            with self.opener.open(request,timeout=self.timeout) as response:
                raw=response.read()
                return json.loads(raw) if raw else None
        except HTTPError as exc:
            # Server bodies can echo secret request fields. Do not log them.
            raise APIError(f'Semaphore {method} {path} returned HTTP {exc.code}') from None
        except (URLError,TimeoutError,json.JSONDecodeError):
            raise APIError(f'Semaphore {method} {path} failed: connection, timeout or invalid response') from None


def same(actual,desired):
    for key,value in desired.items():
        current=actual.get(key)
        if key in ('json','env','arguments'):
            try:
                if json.loads(current or '{}')!=json.loads(value): return False
            except (TypeError,ValueError): return False
        elif current!=value: return False
    return True


class Provisioner:
    def __init__(self,client,config,catalog):
        self.client=client; self.config=config; self.catalog=catalog; self.changes=[]

    def ensure(self,path,desired,key='name',secret=False):
        resources=self.client.request('GET',path)
        if not isinstance(resources,list): raise APIError('Expected a resource list at '+path)
        matches=[r for r in resources if r.get(key)==desired[key]]
        if len(matches)>1: raise APIError('Duplicate managed resource name; resolve manually: '+desired[key])
        if matches:
            current=matches[0]
            if secret: return current
            # List responses may omit details such as template surveys.
            if path.endswith('/templates'):
                current=self.client.request('GET',path+'/'+str(current['id']))
            if not same(current,desired):
                self.client.request('PUT',path+'/'+str(current['id']),dict(desired,id=current['id']))
                self.changes.append({'resource':desired[key],'action':'updated'})
            return dict(current,**desired)
        created=self.client.request('POST',path,desired)
        if not isinstance(created,dict) or 'id' not in created:
            raise APIError('Create response has no resource ID: '+path)
        self.changes.append({'resource':desired[key],'action':'created'})
        return created

    def key(self,path,project,name,kind,env_name=None):
        existing=self.client.request('GET',path)
        matches=[k for k in existing if k['name']==name]
        if len(matches)>1: raise APIError('Duplicate credential name')
        if matches:
            if matches[0]['type']!=kind: raise APIError('Existing credential type mismatch')
            return matches[0]['id']
        body={'name':name,'type':kind,'project_id':project}
        if kind!='none':
            secret=os.environ.get(env_name or '')
            if not secret: raise ValueError('Credential environment variable is missing: '+str(env_name))
            body['ssh' if kind=='ssh' else 'login_password']=(
                {'private_key':secret,'login':self.config.get('ssh_login','')} if kind=='ssh' else {'password':secret})
        result=self.client.request('POST',path,body)
        return result['id']

    def apply(self,enable_schedules=False):
        reported=self.client.request('GET','/info').get('version','')
        version=re.sub(r'^\D*', '', reported).split('-',1)[0].split('+',1)[0]
        if version!='2.19.12':
            raise APIError('Provisioner contract is pinned to Semaphore 2.19.12; observed '+reported)
        projects=self.client.request('GET','/projects')
        name=self.config.get('project_name','Infrastructure Automation')
        matches=[p for p in projects if p['name']==name]
        if len(matches)>1: raise APIError('Duplicate project name')
        project=matches[0] if matches else self.client.request('POST','/projects',{
            'name':name,'alert':False,'max_parallel_tasks':1,'demo':False})
        pid=project['id']; base=f'/project/{pid}'
        none_id=self.key(base+'/keys',pid,'Infrastructure - No credentials','none')
        ssh_id=self.key(base+'/keys',pid,'Infrastructure - SSH','ssh',self.config['ssh_private_key_env']) if self.config.get('ssh_private_key_env') else none_id
        vault_id=self.key(base+'/keys',pid,'Infrastructure - Vault','login_password',self.config['vault_password_env']) if self.config.get('vault_password_env') else None
        git_id=self.config.get('git_key_id',none_id)
        repository=self.ensure(base+'/repositories',{'project_id':pid,'name':'InstallingAnsibleDeployment',
            'git_url':self.config['repository_url'],'git_branch':self.config.get('repository_branch','main'),'ssh_key_id':git_id})
        views={group:self.ensure(base+'/views',{'project_id':pid,'title':title,'position':index},key='title')['id']
               for index,(group,title) in enumerate(GROUPS.items(),1)}
        inventories={}; environments={}; templates={}
        selected_envs=self.config.get('environments',['build','dev','staging','prod'])
        if not selected_envs or any(e not in ['build','dev','staging','prod'] for e in selected_envs):
            raise ValueError('Invalid environment selection')
        selected_ops=self.config.get('operations',list(self.catalog))
        if any(o not in self.catalog for o in selected_ops): raise ValueError('Unknown catalog operation')
        for env in selected_envs:
            inventories[env]=self.ensure(base+'/inventory',{'project_id':pid,'name':'Infrastructure - '+env,
                'type':'file','inventory':f'inventories/{env}/hosts.yml','repository_id':repository['id'],
                'ssh_key_id':ssh_id})['id']
            variables={'infrastructure_environment':env,'confirm_operation':False,'confirm_production':False,
                       'confirm_destructive_operation':False,'confirm_reboot':False}
            variables.update(self.config.get('environment_variables',{}).get(env,{}))
            if any(k.startswith('confirm_') and v for k,v in variables.items()):
                raise ValueError('Confirmation flags cannot be enabled permanently in an environment')
            task_env={'ANSIBLE_CONFIG':'ansible.cfg'}
            task_env.update(self.config.get('task_environment',{}))
            report_dir=self.config.get('report_dir','/reports')
            if report_dir:
                task_env['INFRASTRUCTURE_REPORT_DIR']=report_dir
            environments[env]=self.ensure(base+'/environment',{'project_id':pid,'name':'Infrastructure - '+env,
                'json':json.dumps(variables,sort_keys=True),'env':json.dumps(task_env,sort_keys=True)})['id']
            for operation_id in selected_ops:
                operation=self.catalog[operation_id]
                surveys=[]
                for key,spec in operation['inputs'].items():
                    survey={'name':key,'title':key,'description':spec.get('description',''),'required':spec['required'],'type':'text'}
                    if spec.get('choices'):
                        survey['type']='enum'; survey['values']=[{'name':str(v),'value':str(v)} for v in spec['choices']]
                    surveys.append(survey)
                confirmations=[]
                if operation['risk']!='read': confirmations.append('confirm_operation')
                if operation['risk']=='destructive': confirmations.append('confirm_destructive_operation')
                if env=='prod' and operation['risk']!='read': confirmations.append('confirm_production')
                for key in confirmations:
                    if not any(s['name']==key for s in surveys):
                        surveys.append({'name':key,'title':key,'type':'enum','required':True,
                                        'values':[{'name':'No','value':'false'},{'name':'Yes','value':'true'}]})
                payload={'project_id':pid,'name':operation['name']+' ['+env+']','app':'ansible',
                    'playbook':operation['playbook'],'repository_id':repository['id'],'inventory_id':inventories[env],
                    'environment_id':environments[env],'view_id':views[operation['group']],
                    'arguments':'[]','allow_override_args_in_task':False,'autorun':False,'type':'',
                    'description':'Managed catalog: '+operation_id+'. '+operation['risk']+' operation.',
                    'survey_vars':surveys,'vaults':[{'name':'default','type':'password','vault_key_id':vault_id}] if vault_id else [],
                    'task_params':{'skip_galaxy_install':bool(self.config.get('skip_galaxy_install',False))}}
                templates[(env,operation_id)]=self.ensure(base+'/templates',payload)['id']
        for schedule in self.config.get('schedules',[]):
            key=(schedule['environment'],schedule['operation'])
            if key not in templates: raise ValueError('Schedule references an unconfigured template')
            op=self.catalog[key[1]]
            values=schedule.get('variables',{})
            if op['risk']=='destructive': raise ValueError('Destructive schedules are refused')
            if op['risk']!='read' and not schedule.get('approved',False):
                raise ValueError('Mutating schedules need explicit configuration approval')
            if op['risk']!='read' and str(values.get('confirm_operation','')).lower()!='true':
                raise ValueError('Approved backup schedule must explicitly confirm its operation')
            if key[0]=='prod' and op['risk']!='read' and str(values.get('confirm_production','')).lower()!='true':
                raise ValueError('Production schedule needs explicit production confirmation')
            self.ensure(base+'/schedules',{'project_id':pid,'name':schedule['name'],'template_id':templates[key],
                'cron_format':schedule['cron'],'active':bool(enable_schedules and schedule.get('enabled',False)),
                'task_params':{'environment':json.dumps(values)}})
        actual=self.client.request('GET',base+'/templates')
        actual_ids={t['id'] for t in actual}
        if any(t not in actual_ids for t in templates.values()): raise APIError('Template read-back failed')
        return {'project_id':pid,'server_version':version,'catalog_operations':len(selected_ops),
                'templates_linked':len(templates),'templates_read_back':len(templates),
                'templates_executed_successfully':0,'browser_ui_observed':False,'changes':self.changes,
                'smoke_template_id':templates.get(('build','system.verify'))}

    def smoke(self,project_id,template_id,timeout=300):
        base=f'/project/{project_id}'
        task=self.client.request('POST',base+'/tasks',{'template_id':template_id,'message':'Read-only installation verification'})
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            status=self.client.request('GET',base+'/tasks/'+str(task['id']))
            if status['status'] in ('success','error','stopped'):
                return {'task_id':task['id'],'status':status['status'],'success':status['status']=='success'}
            time.sleep(3)
        return {'task_id':task['id'],'status':'timeout','success':False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project'); parser.add_argument('--config',required=True)
    parser.add_argument('--apply',action='store_true'); parser.add_argument('--enable-schedules',action='store_true')
    parser.add_argument('--smoke',action='store_true'); parser.add_argument('--report',default='reports/semaphore-provisioning.json')
    args=parser.parse_args(argv)
    try:
        root=project_root(args.project); config=json.loads(Path(args.config).read_text()); catalog=load_catalog(root)
        if not args.apply:
            operations=config.get('operations',list(catalog))
            print(json.dumps({'mode':'plan','project_name':config.get('project_name','Infrastructure Automation'),
                'catalog_operations':len(operations),'template_count':len(operations)*len(config.get('environments',['build','dev','staging','prod'])),
                'executed':False},indent=2)); return 0
        client=Client(config['url'],os.environ.get('SEMAPHORE_API_TOKEN',''))
        provisioner=Provisioner(client,config,catalog); report=provisioner.apply(args.enable_schedules)
        failed=False
        if args.smoke:
            if report['smoke_template_id'] is None: raise ValueError('Smoke test requires build/system.verify')
            report['smoke']=provisioner.smoke(report['project_id'],report['smoke_template_id'])
            report['templates_executed_successfully']=int(report['smoke']['success']); failed=not report['smoke']['success']
        path=Path(args.report)
        if not path.is_absolute(): path=root/path
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
        with os.fdopen(fd,'w') as stream: json.dump(report,stream,indent=2)
        print(json.dumps(report,indent=2)); return 1 if failed else 0
    except (ValueError,OSError,APIError,KeyError) as exc:
        print('Semaphore setup failed: '+str(exc),file=sys.stderr); return 2


if __name__=='__main__': sys.exit(main())
