import json
from pathlib import Path
import tarfile
import io
import pytest
from infrastructure_archive import execute,verify,sha


def params(tmp_path,action,**kw):
    return dict(action=action,backup_root=str(tmp_path/'backups'),confirmed=False,retention_days=7,**kw)


def test_round_trip_preserves_content_and_refuses_overwrite(tmp_path):
    source=tmp_path/'source'; source.mkdir(); (source/'data.txt').write_text('recoverable')
    result=execute(params(tmp_path,'backup',source=str(source)))
    backup_id=result['backup']['backup_id']
    assert execute(params(tmp_path,'verify',backup_id=backup_id))['verified']
    restore_root=tmp_path/'recovery'; destination=restore_root/'one'
    p=params(tmp_path,'restore',backup_id=backup_id,destination=str(destination),restore_root=str(restore_root))
    with pytest.raises(ValueError,match='confirmation'): execute(p)
    p['confirmed']=True; execute(p)
    assert (destination/'data/data.txt').read_text()=='recoverable'
    with pytest.raises(ValueError,match='already exists'): execute(p)


def test_corrupt_archive_fails_before_restore(tmp_path):
    source=tmp_path/'source'; source.mkdir(); (source/'a').write_text('a')
    manifest=execute(params(tmp_path,'backup',source=str(source)))['backup']
    (tmp_path/'backups'/manifest['file']).write_bytes(b'corrupted')
    with pytest.raises(ValueError,match='checksum|truncated'): verify(tmp_path/'backups',manifest['backup_id'])


def test_traversal_manifest_rejected(tmp_path):
    root=tmp_path/'backups'; root.mkdir(); backup_id='20260101T000000Z-0123456789ab'
    (root/(backup_id+'.json')).write_text(json.dumps({'schema_version':1,'kind':'files','backup_id':backup_id,'file':'../outside'}))
    with pytest.raises(ValueError,match='children'): verify(root,backup_id)


def test_tar_traversal_is_rejected_even_with_matching_checksum(tmp_path):
    root=tmp_path/'backups'; root.mkdir(); backup_id='20260101T000000Z-0123456789ab'; archive=root/(backup_id+'.tar.gz')
    with tarfile.open(archive,'w:gz') as tf:
        member=tarfile.TarInfo('../../escape'); member.size=4; tf.addfile(member,io.BytesIO(b'evil'))
    (root/(backup_id+'.json')).write_text(json.dumps({'schema_version':1,'kind':'files','backup_id':backup_id,
        'file':archive.name,'sha256':sha(archive),'size_bytes':archive.stat().st_size}))
    with pytest.raises(ValueError,match='unsafe'): verify(root,backup_id)


def test_dry_run_does_not_create_backup(tmp_path):
    source=tmp_path/'source'; source.mkdir()
    assert execute(params(tmp_path,'backup',source=str(source)),True)['preview']
    assert not (tmp_path/'backups').exists()


def test_backup_destination_inside_source_is_refused(tmp_path):
    source=tmp_path/'source'; source.mkdir()
    p=params(tmp_path,'backup',source=str(source)); p['backup_root']=str(source/'backups')
    with pytest.raises(ValueError,match='inside'): execute(p)


def test_retention_preserves_recent_and_unmanaged_files(tmp_path):
    source=tmp_path/'source'; source.mkdir(); root=tmp_path/'backups'
    recent=execute(params(tmp_path,'backup',source=str(source)))['backup']
    old=execute(params(tmp_path,'backup',source=str(source)))['backup']
    old['created_at']='2000-01-01T00:00:00+00:00'
    (root/(old['backup_id']+'.json')).write_text(json.dumps(old))
    (root/'unmanaged.txt').write_text('keep')
    p=params(tmp_path,'retention'); p['confirmed']=True
    result=execute(p)
    assert result['removed']==[old['backup_id']]
    assert (root/recent['file']).exists() and (root/'unmanaged.txt').exists()
