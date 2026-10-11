from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from review.langsmith_data import LangSmithReview, fingerprint, label_from_feedback


class Feedback:
    def __init__(self,data): self.data=data
    def model_dump(self,**kwargs): return deepcopy(self.data)


class FakeClient:
    def __init__(self): self.items=[];self.fail_reason=False;self.creates=[]
    def list_feedback(self,**kwargs): return [Feedback(f) for f in self.items]
    def create_feedback(self,**kwargs):
        self.creates.append(kwargs)
        self.items.append({'id':str(kwargs['feedback_id']),'key':kwargs['key'],
                           'run_id':kwargs['run_id'],'score':kwargs.get('score'),
                           'value':kwargs['value'],'correction':kwargs.get('correction'),
                           'comment':kwargs.get('comment'),'modified_at':'2026-09-08T00:00:00Z'})
    def update_feedback(self,identity,**kwargs):
        if self.fail_reason: raise OSError('network unavailable')
        next(f for f in self.items if f['id']==identity).update(kwargs)


def gateway():
    client=FakeClient()
    g=LangSmithReview(client=client)
    g.project_id='project-uuid'
    g.rows={'trace':{'trace_hash':'hash','start_time':'2026-09-08T00:00:00+00:00'}}
    g.feedback={'trace':[]}
    return g,client


def test_create_and_update_feedback_preserve_run_identity_and_use_smithdb_keys():
    g,c=gateway()
    g.save('trace','hash','fail','Missing condition','Corrected answer')
    assert len(c.items)==2
    assert all(x['run_id']=='trace' and x['session_id']=='project-uuid' and isinstance(x['start_time'],datetime) for x in c.creates)
    assert g.get('trace')['verdict']=='fail'
    g.save('trace','hash','pass','Now supported','')
    assert len(c.items)==2  # updates, not duplicate feedback
    assert g.get('trace')['verdict']=='pass'
    assert g.get('trace')['correction']==''


def test_external_feedback_change_is_not_silently_overwritten():
    g,c=gateway();g.save('trace','hash','pass','Supported','')
    c.items[0]['value']='External reviewer changed this'
    with pytest.raises(ValueError,match='Feedback changed'):
        g.save('trace','hash','fail','New decision','')
    assert c.items[0]['value']=='External reviewer changed this'


def test_failed_save_does_not_update_local_snapshot():
    g,c=gateway();g.save('trace','hash','pass','Supported','')
    c.fail_reason=True
    with pytest.raises(OSError):g.save('trace','hash','fail','New decision','')
    assert g.get('trace')['verdict']=='pass'


def test_fail_requires_reason_and_wrong_trace_hash_is_rejected():
    g,c=gateway()
    with pytest.raises(ValueError):g.save('trace','hash','fail',' ','')
    with pytest.raises(ValueError):g.save('trace','different','pass','','')
    assert not c.creates


def test_pass_with_empty_reason_does_not_turn_provenance_comment_into_reason():
    g,c=gateway()
    g.save('trace','hash','pass','','')
    assert g.get('trace')['verdict']=='pass'
    assert g.get('trace')['reason']==''


def test_existing_vietnamese_categories_and_optional_correction_are_read():
    label=label_from_feedback([
        {'key':'answer_pass','value':'Trượt ','score':0,'correction':{'answer':'Correction'},
         'feedback_source':{'type':'api','metadata':{'reviewer':'assistant'}}},
        {'key':'review_reason','value':'Unsupported claim'},
    ])
    assert label['verdict']=='fail' and label['reason']=='Unsupported claim'
    assert label['reviewer']=='assistant' and label['correction']=='Correction'
