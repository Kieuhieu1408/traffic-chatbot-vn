import json
from review.data import LabelStore, load_runs


def test_labels_persist_and_are_isolated_by_run_and_trace(tmp_path):
    path=tmp_path/'labels.sqlite3'
    store=LabelStore(path)
    store.save('run1','case1','hash1','fail','Nguồn không hỗ trợ',['retrieval'],'Câu sửa')
    reopened=LabelStore(path)
    assert reopened.get('run1','case1','hash1')['verdict']=='fail'
    assert reopened.get('run2','case1','hash1') is None
    assert reopened.get('run1','case1','changed') is None
    assert reopened.export()[0]['errors']==['retrieval']


def test_label_requires_reason(tmp_path):
    import pytest
    store=LabelStore(tmp_path/'labels.sqlite3')
    with pytest.raises(ValueError):store.save('r','c','h','fail',' ',[],'')
    assert store.export()==[]


def test_dataset_mismatch_does_not_show_wrong_gold(tmp_path):
    folder=tmp_path/'evals/runs/run1';folder.mkdir(parents=True)
    (tmp_path/'evals/corpus-seed-10.jsonl').write_text(json.dumps({'case_id':'c'}))
    (folder/'answers.jsonl').write_text(json.dumps({'case_id':'c','answer':'answer'}))
    (folder/'manifest.json').write_text(json.dumps({'dataset_sha256':'different'}))
    runs=load_runs(tmp_path)
    assert runs['run1']['cases']=={}
    assert not runs['run1']['dataset_matches']


def test_binary_labels_allow_pass_without_reason_and_reject_review(tmp_path):
    import pytest
    store=LabelStore(tmp_path/'labels.sqlite3')
    store.save('r','c','h','pass','',[],'')
    assert store.get('r','c','h')['verdict']=='pass'
    for verdict in ('review',''):
        with pytest.raises(ValueError):store.save('r','other','h',verdict,'Ghi chú',[],'')
