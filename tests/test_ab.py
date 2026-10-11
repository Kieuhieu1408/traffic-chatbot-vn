from rag_traffic.ab import variant, ExperimentStore, ArmRetriever


def test_assignment_stable_and_both_arms_reachable():
    assert variant('same-session') == variant('same-session')
    assert {variant(str(i)) for i in range(100)} == {'A','B'}


def test_feedback_updates_one_exposure(tmp_path):
    store=ExperimentStore(tmp_path/'ab.sqlite3')
    id=store.record('session','A','trace',1.2,'rag')
    assert not store.feedback('unknown',True)
    assert store.feedback(id,True)
    assert store.feedback(id,False)
    with store.connect() as db:
        rows=db.execute('SELECT session,helpful FROM events').fetchall()
    assert len(rows)==1 and rows[0][1]==0 and rows[0][0]!='session'


def test_arm_controls_alias_expansion():
    class Base:
        manifest={}
        def search(self,q,k,score,**kw):return kw['expand_alias']
    assert ArmRetriever(Base(),'A').search('q',6,.55) is False
    assert ArmRetriever(Base(),'B').search('q',6,.55) is True


def test_api_exposure_and_feedback_are_opt_in(monkeypatch,tmp_path):
    from fastapi.testclient import TestClient
    from rag_traffic.config import Settings
    from app import create_app
    from types import SimpleNamespace
    monkeypatch.setenv('RAG_AB_ENABLED','true')
    settings=Settings(source_dir=tmp_path/'raw',index_dir=tmp_path/'index',static_dir=tmp_path,
                      embedding_model='unused',openai_api_key=None,openai_model=None,top_k=6,min_score=.55)
    app=create_app(settings)
    arms=[]
    def run(retriever,*args):
        arms.append(getattr(retriever,'arm',None))
        return 'Evidence','evidence_only',[],None
    with TestClient(app) as client:
        app.state.retriever=SimpleNamespace(manifest={})
        app.state.tracing=SimpleNamespace(run=run,close=lambda:None)
        for _ in range(2):
            result=client.post('/search',json={'query':'Bằng lái quốc tế bị mất','session_id':'same'}).json()
            assert result['response_id']
        assert arms[0]==arms[1] and arms[0] in ('A','B')
        assert client.post('/feedback',json={'response_id':result['response_id'],'helpful':True}).json()=={'saved':True}
        assert client.post('/feedback',json={'response_id':'0'*32,'helpful':True}).status_code==404
        result=client.post('/search',json={'query':'Tốc độ tối đa','session_id':'same'}).json()
        assert result['response_id'] is None


def test_summary_uses_first_exposure_and_reports_missing(tmp_path):
    from evals.ab_report import report
    store=ExperimentStore(tmp_path/'ab.sqlite3')
    store.record('one','A',None,1,'rag')
    second=store.record('one','A',None,2,'rag');store.feedback(second,True)
    first=store.record('two','B',None,1,'rag');store.feedback(first,True)
    result=report(store.path)['arms']
    assert result['A']['sessions']==1
    assert result['A']['missing_feedback']==1
    assert result['A']['helpful_among_respondents'] is None
    assert result['B']['confirmed_helpful_per_session']==1
