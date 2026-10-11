import pytest
from evals.calibration import CalibrationStore, comparison
from evals.judge import digest, judge_input


def row(identity='r'):
    r={'case_id':identity,'query':'q','answer':'a','history':[],'results':[]}
    r['input_hash']=digest(judge_input(r));return r


def test_cannot_reveal_before_save_and_first_review_is_immutable(tmp_path):
    s=CalibrationStore(tmp_path/'labels.db');r=row()
    with pytest.raises(ValueError):s.reveal('b',r,'rubric')
    s.save('b',r,'rubric','pass','human reason','',True)
    s.reveal('b',r,'rubric')
    with pytest.raises(ValueError):s.save('b',r,'rubric','fail','judge influenced','',True)
    assert s.get('b',r,'rubric')['verdict']=='pass'
    assert s.get('b',r,'rubric')['independent']==1


def test_exposure_follows_the_trace_across_judge_batches(tmp_path):
    s=CalibrationStore(tmp_path/'labels.db');r=row()
    s.save('b',r,'rubric','pass','','',True);s.reveal('b',r,'rubric')
    s.save('new-batch',r,'rubric','fail','reason','',True)
    assert s.get('new-batch',r,'rubric')['independent']==0
    assert s.get('b',r,'different-rubric') is None


def test_metrics_use_fail_as_positive_and_exclude_nonindependent(tmp_path):
    s=CalibrationStore(tmp_path/'labels.db');rows=[row(str(i)) for i in range(6)]
    # TP, FP, FN, TN, non-independent, unreviewed
    humans=['fail','pass','fail','pass','pass']
    judges=['fail','fail','pass','pass','fail','pass']
    for i,h in enumerate(humans):s.save('b',rows[i],'rubric',h,'reason','',i!=4)
    batch={'rows':rows,'manifest':{'rubric_hash':'rubric'},'judgments':{
        str(i):{'status':'ok','judgment':{'verdict':j}} for i,j in enumerate(judges)}}
    report=comparison('b',batch,s)
    assert report['confusion_matrix']==dict(tp=1,fp=1,fn=1,tn=1)
    assert report['precision']==report['recall']==.5
    assert report['excluded_nonindependent']==1 and report['unreviewed']==1


def test_no_human_labels_means_undefined_metrics_not_perfect_agreement(tmp_path):
    s=CalibrationStore(tmp_path/'labels.db')
    batch={'rows':[row()],'manifest':{'rubric_hash':'r'},'judgments':{}}
    report=comparison('b',batch,s)
    assert report['precision'] is report['recall'] is report['agreement'] is None


def test_abstention_is_excluded_and_reported(tmp_path):
    s=CalibrationStore(tmp_path/'labels.db');r=row()
    s.save('b',r,'rubric','fail','reason','',True)
    batch={'rows':[r],'manifest':{'rubric_hash':'rubric'},'judgments':{'r':{'status':'ok','judgment':{'verdict':None}}}}
    report=comparison('b',batch,s)
    assert report['judge_abstentions']==1 and report['matched_binary_reviews']==0


def test_modified_snapshot_cannot_receive_old_human_label(tmp_path):
    s=CalibrationStore(tmp_path/'labels.db');r=row();r['answer']='changed'
    with pytest.raises(ValueError):s.save('b',r,'rubric','pass','','',True)
