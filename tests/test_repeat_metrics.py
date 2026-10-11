from evals.summarize_repeats import summarize


def test_abstention_does_not_inflate_detection_rate():
    cases=[{'case_id':'a','expected':'fail'},{'case_id':'b','expected':'fail'},{'case_id':'c','expected':'pass'}]
    rows=[{'case_id':id,'repeat':1,'judgment':{'verdict':v}} for id,v in [('a','fail'),('b',None),('c','pass')]]
    result=summarize(cases,rows,1)['per_repeat'][0]
    assert result['recall_among_binary']==1
    assert result['detected_fail_fraction']==0.5
    assert result['coverage']==2/3


def test_error_or_changed_label_is_not_stable():
    cases=[{'case_id':'a','expected':'pass'}]
    rows=[{'case_id':'a','repeat':1,'judgment':{'verdict':'pass'}},{'case_id':'a','repeat':2,'status':'error'}]
    assert summarize(cases,rows,2)['stable_binary_cases']==0
