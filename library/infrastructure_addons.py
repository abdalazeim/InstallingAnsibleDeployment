#!/usr/bin/python
"""Validate addon manifests and Python syntax without importing untrusted code."""
import ast
from pathlib import Path


def validate(path):
    root=Path(path)
    if not root.is_absolute() or not root.is_dir():
        raise ValueError('An existing absolute addon directory is required')
    addons=[]
    for manifest in sorted(root.glob('*/__manifest__.py')):
        data=ast.literal_eval(manifest.read_text(encoding='utf-8'))
        if not isinstance(data,dict) or not data.get('name') or not (manifest.parent/'__init__.py').is_file():
            raise ValueError('Addon must contain name metadata and __init__.py: '+manifest.parent.name)
        if not isinstance(data.get('depends',[]),list):
            raise ValueError('Addon dependencies must be a list')
        for source in manifest.parent.rglob('*.py'):
            if source.is_symlink(): raise ValueError('Addon source symlinks are not permitted')
            ast.parse(source.read_text(encoding='utf-8'),filename=str(source))
        addons.append({'name':manifest.parent.name,'version':str(data.get('version',''))})
    if not addons: raise ValueError('No addon manifests were found')
    return addons


def main():
    from ansible.module_utils.basic import AnsibleModule
    m=AnsibleModule(argument_spec={'path':{'type':'path','required':True}},supports_check_mode=True)
    try: m.exit_json(changed=False,addons=validate(m.params['path']))
    except (OSError,ValueError,SyntaxError) as exc: m.fail_json(msg=str(exc))


if __name__=='__main__': main()
