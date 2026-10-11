import json
from pathlib import Path


def test_pilot_splits_are_disjoint_and_references_have_evidence():
    root=Path(__file__).resolve().parents[1]/'finetune/data'
    groups={};ids=set()
    for split in ['train','dev','test']:
        rows=[json.loads(l) for l in (root/(split+'.jsonl')).read_text().splitlines()]
        groups[split]={r['group'] for r in rows}
        for r in rows:
            assert r['case_id'] not in ids;ids.add(r['case_id'])
            assert r['reviewer']=='assistant'
            if r['sources']:assert '[1]' in r['answer']
            else:assert r['capability']=='missing_evidence'
    assert not groups['train'] & (groups['dev']|groups['test'])
    assert not groups['dev'] & groups['test']
