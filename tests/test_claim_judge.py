import pytest
from evals.claim_judge import aggregate

DATA={'answer':'A. B.', 'sources':[{'rank':1}]}

def claim(quote,status):
    return dict(quote=quote,source_ranks=[1],status=status,evidence_assessment='Evidence comparison')

@pytest.mark.parametrize('status,expected',[('supported','pass'),('unsupported','fail'),('contradicted','fail'),('unresolved',None)])
def test_extra_claim_controls_aggregate(status,expected):
    out=aggregate({'claims':[claim('A.','supported'),claim('B.',status)],'answer_issues':[]},DATA)
    assert out['verdict']==expected

def test_audit_rejects_invented_quote():
    with pytest.raises(ValueError):aggregate({'claims':[claim('C.','supported')],'answer_issues':[]},DATA)

def test_wrong_request_can_fail_supported_claims():
    out=aggregate({'claims':[claim('A.','supported')],'answer_issues':['Does not answer request']},DATA)
    assert out['verdict']=='fail'
