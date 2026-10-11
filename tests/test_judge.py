import json
import httpx
import pytest
from evals.judge import evaluate, judge_input, validate_judgment

ROW={'query':'Question','history':[],'answer':'The limit is 70 [1].',
     'results':[{'rank':1,'content':'Limit 60'}],
     'review_reason':'SECRET LABEL','verdict':'pass','correction':'SECRET CORRECTION'}

def failure(**kwargs):
    return dict(verdict='fail',needs_human_review=False,reason='Wrong limit',
                issues=[{'claim':'The limit is 70','category':'wrong_answer','source_ranks':[1],'explanation':'Source says 60'}],**kwargs)


def test_judge_never_sends_old_reviews_or_credentials_in_inputs():
    def post(url,**kwargs):
        body=kwargs['json']
        assert 'SECRET LABEL' not in json.dumps(body) and 'SECRET CORRECTION' not in json.dumps(body)
        assert 'api-secret' not in json.dumps(body)
        assert body['response_format']['json_schema']['strict']
        assert kwargs['headers']['Authorization']=='Bearer api-secret'
        return httpx.Response(200,request=httpx.Request('POST','https://api.openai.com/v1/chat/completions'),json={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(failure())}}], 'usage':{'total_tokens':42}})
    assert evaluate(ROW,'rubric','api-secret','gpt-5.4-mini',post=post)['judgment']['verdict']=='fail'


@pytest.mark.parametrize('kind',['bad_rank','invented_quote','no_issues','contradiction'])
def test_invalid_judgment_does_not_become_a_label(kind):
    raw=failure()
    if kind=='bad_rank':raw['issues'][0]['source_ranks']=[99]
    if kind=='invented_quote':raw['issues'][0]['claim']='Not in answer'
    if kind=='no_issues':raw['issues']=[]
    if kind=='contradiction':raw['needs_human_review']=True
    with pytest.raises(ValueError):validate_judgment(raw,judge_input(ROW))


def test_abstention_is_not_failure_or_pass():
    result=validate_judgment({'verdict':None,'needs_human_review':True,'reason':'Needs specialist','issues':[]},judge_input(ROW))
    assert result['verdict'] is None


def test_refusal_and_truncation_are_errors():
    def post(*args,**kwargs):return httpx.Response(200,request=httpx.Request('POST','https://api.openai.com/v1/chat/completions'),json={'choices':[{'finish_reason':'length','message':{'content':'{}'}}]})
    with pytest.raises(ValueError):evaluate(ROW,'rubric','key','model',post=post)


def test_exact_excerpt_with_quote_wrapper():
    data = {'answer': 'A is false.', 'sources': [{'rank': 1}]}
    raw = {'verdict': 'fail', 'needs_human_review': False, 'reason': 'Contradiction',
           'issues': [{'claim': '"A is false."', 'category': 'wrong_answer',
                       'source_ranks': [1], 'explanation': 'Source says otherwise'}]}
    result = validate_judgment(raw, data)
    assert result['issues'][0]['claim'] == 'A is false.'
    raw['issues'][0]['claim'] = '"A is true."'
    import pytest
    with pytest.raises(ValueError):
        validate_judgment(raw, data)
