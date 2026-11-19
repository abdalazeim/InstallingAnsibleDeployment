import importlib.util
from pathlib import Path
import json
import yaml

ROOT=Path(__file__).resolve().parents[2]


def test_supported_tree_has_no_missing_references():
    spec=importlib.util.spec_from_file_location('validator',ROOT/'scripts/validation/validate.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert module.validate()['errors']==[]


def test_no_shell_and_no_ignored_errors_in_supported_roles():
    for path in (ROOT/'roles').rglob('*.yml'):
        text=path.read_text()
        assert 'ansible.builtin.shell:' not in text,path
        assert 'ignore_errors: true' not in text,path


def test_all_catalog_playbooks_enforce_policy():
    for operation in json.loads((ROOT/'semaphore/templates/catalog.json').read_text())['operations']:
        play=yaml.safe_load((ROOT/operation['playbook']).read_text())[0]
        assert play['pre_tasks'][0]['ansible.builtin.import_role']['name']=='common'
        assert play['vars']['operation_risk']==operation['risk']


def test_generated_template_documentation_is_current():
    spec=importlib.util.spec_from_file_location('render_catalog',ROOT/'scripts/reporting/render_catalog.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    catalog=json.loads((ROOT/'semaphore/templates/catalog.json').read_text())
    expected=module.render(catalog)
    actual=(ROOT/'docs/semaphore/TEMPLATES_CATALOG.md').read_text()
    assert actual==expected, 'run python3 scripts/reporting/render_catalog.py'

