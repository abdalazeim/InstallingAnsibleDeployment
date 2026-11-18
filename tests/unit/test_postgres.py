import pytest
from infrastructure_postgres import PostgreSQL,identifier,execute


@pytest.mark.parametrize('value',['bad;DROP DATABASE x','--option','a\nb','',"a'b",'a'*64])
def test_identifier_injection_refused(value):
    with pytest.raises(ValueError): identifier(value)


def test_password_never_in_command(tmp_path):
    db=PostgreSQL({'mode':'docker','container':'database','password':'secret-unique'},str(tmp_path))
    command=db.command('pg_dump',['--dbname','app'])
    assert 'secret-unique' not in ' '.join(command)
    assert command[:5]==['docker','exec','-i','--env','PGPASSWORD']


def test_existing_database_never_overwritten(tmp_path,monkeypatch):
    db=PostgreSQL({},str(tmp_path))
    monkeypatch.setattr(db,'verify',lambda _:({'server_version':'15.1'},tmp_path/'unused'))
    calls=[]
    def sql(statement,*args): calls.append(statement); return '1'
    monkeypatch.setattr(db,'sql',sql)
    with pytest.raises(ValueError,match='NEW database'): db.restore('irrelevant','existing')
    assert not any('DROP' in x or 'CREATE' in x for x in calls)


def test_failed_dump_does_not_create_success_manifest(tmp_path,monkeypatch):
    db=PostgreSQL({},str(tmp_path/'backups'))
    def fail(*a,**kw): raise RuntimeError('pg_dump failed')
    monkeypatch.setattr(db,'run',fail)
    with pytest.raises(RuntimeError): db.backup('application')
    assert not list((tmp_path/'backups').glob('*.json'))
    assert not list((tmp_path/'backups').glob('.partial-*'))


def test_delete_requires_confirmation_even_when_database_exists(tmp_path,monkeypatch):
    monkeypatch.setattr(PostgreSQL,'sql',lambda *a:'1')
    with pytest.raises(ValueError,match='confirmation'):
        execute({'connection':{},'backup_root':str(tmp_path),'action':'delete','database':'app','confirmed':False})
