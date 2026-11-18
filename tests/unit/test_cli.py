from pathlib import Path
import json
import pytest
from infrastructure_manager.cli import load_catalog,resolve_operation,parse_values,main

ROOT=Path(__file__).resolve().parents[2]


def test_unknown_shell_command_is_not_an_operation():
    with pytest.raises(ValueError): resolve_operation(['bash','-c','evil'],load_catalog(ROOT))


def test_extra_ansible_escape_hatches_refused():
    operation=load_catalog(ROOT)['system.info']
    with pytest.raises(ValueError): parse_values(['ansible_connection=evil'],operation,[])


def test_mutation_requires_confirmation(capsys):
    assert main(['docker','start','test','--project',str(ROOT),'--plan'])==2
    assert 'confirm_operation' in capsys.readouterr().err


def test_plan_uses_argv_without_execution(capsys):
    assert main(['docker','start','test','--project',str(ROOT),'--set','confirm_operation=true','--plan'])==0
    report=json.loads(capsys.readouterr().out)
    assert report['executed'] is False
    assert report['argv'][0]=='ansible-playbook'


def test_invalid_inventory_fails(tmp_path):
    assert main(['system','info','--project',str(ROOT),'--inventory',str(tmp_path/'missing'),'--plan'])==2


def test_false_string_cannot_approve_changes():
    assert main(['docker','start','test','--project',str(ROOT),'--set','confirm_operation="false"','--plan'])==2
