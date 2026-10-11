"""Blind first reviews and source-matched judge comparison; never infer human gold."""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from evals.judge import digest, judge_input
from evals.tracking import ROOT


def load_judge_batches(root=ROOT):
    batches={}
    for folder in sorted((root/'evals/judge_runs').glob('*'),reverse=True):
        if not (folder/'manifest.json').is_file():continue
        manifest=json.loads((folder/'manifest.json').read_text())
        if manifest.get('status')!='complete':continue
        rows=[json.loads(line) for line in (folder/'traces.jsonl').read_text().splitlines() if line.strip()]
        results={r['run_id']:r for r in map(json.loads,(folder/'results.jsonl').read_text().splitlines())}
        rubric=(folder/'rubric.md').read_text()
        if digest(rubric)!=manifest['rubric_hash']:raise ValueError('Judge rubric snapshot changed')
        if digest([judge_input(r) for r in rows])!=manifest['dataset_hash']:raise ValueError('Judge dataset snapshot changed')
        for row in rows:
            if row['input_hash']!=digest(judge_input(row)):raise ValueError('Judge input snapshot changed')
            if results.get(row['case_id'],{}).get('input_hash')!=row['input_hash']:raise ValueError('Judge result/input mismatch')
        batches['judge:'+folder.name]={'rows':rows,'manifest':manifest,'judgments':results,
            'rubric':rubric,'folder':folder,'cases':{},'comments':{},'blind':True}
    return batches


class CalibrationStore:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS blind_reviews (
                batch TEXT, run_id TEXT, input_hash TEXT, rubric_hash TEXT,
                verdict TEXT, reason TEXT, correction TEXT, independent INTEGER,
                created_at TEXT, PRIMARY KEY(batch,run_id,input_hash,rubric_hash))''')
            db.execute('''CREATE TABLE IF NOT EXISTS judge_exposures (
                run_id TEXT, input_hash TEXT, exposed_at TEXT, PRIMARY KEY(run_id,input_hash))''')

    def connect(self):
        db=sqlite3.connect(self.path,timeout=10);db.row_factory=sqlite3.Row;return db

    def get(self,batch,row,rubric_hash):
        with self.connect() as db:
            item=db.execute('SELECT * FROM blind_reviews WHERE batch=? AND run_id=? AND input_hash=? AND rubric_hash=?',
                            (batch,row['case_id'],row['input_hash'],rubric_hash)).fetchone()
        return dict(item) if item else None

    def exposed(self,row):
        with self.connect() as db:
            return bool(db.execute('SELECT 1 FROM judge_exposures WHERE run_id=? AND input_hash=?',
                                   (row['case_id'],row['input_hash'])).fetchone())

    def save(self,batch,row,rubric_hash,verdict,reason,correction,independent):
        if verdict not in ('pass','fail'):raise ValueError('Choose Pass or Fail.')
        if verdict=='fail' and not reason.strip():raise ValueError('A failure requires a reason.')
        if digest(judge_input(row))!=row['input_hash']:raise ValueError('Trace snapshot changed.')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            exposed=db.execute('SELECT 1 FROM judge_exposures WHERE run_id=? AND input_hash=?',
                               (row['case_id'],row['input_hash'])).fetchone()
            try:
                db.execute('INSERT INTO blind_reviews VALUES (?,?,?,?,?,?,?,?,?)',
                    (batch,row['case_id'],row['input_hash'],rubric_hash,verdict,reason.strip(),correction.strip(),
                     int(bool(independent) and not exposed),datetime.now(timezone.utc).isoformat()))
            except sqlite3.IntegrityError as exc:
                raise ValueError('Your first review is locked for comparison; it cannot be overwritten after saving.') from exc

    def reveal(self,batch,row,rubric_hash):
        if not self.get(batch,row,rubric_hash):raise ValueError('Save your own review before revealing the judge.')
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO judge_exposures VALUES (?,?,?)',
                       (row['case_id'],row['input_hash'],datetime.now(timezone.utc).isoformat()))


def comparison(batch_id,batch,store):
    matrix={'tp':0,'fp':0,'fn':0,'tn':0};disagreements=[]
    missing=nonindependent=abstentions=errors=0
    for row in batch['rows']:
        human=store.get(batch_id,row,batch['manifest']['rubric_hash'])
        if not human:missing+=1;continue
        if not human['independent']:nonindependent+=1;continue
        result=batch['judgments'].get(row['case_id'],{})
        if result.get('status')!='ok':errors+=1;continue
        verdict=result['judgment']['verdict']
        if verdict is None:abstentions+=1;continue
        hf=human['verdict']=='fail';jf=verdict=='fail'
        matrix['tp' if hf and jf else 'fp' if jf else 'fn' if hf else 'tn']+=1
        if hf!=jf:disagreements.append(row['case_id'])
    tp,fp,fn,tn=(matrix[k] for k in ('tp','fp','fn','tn'))
    divide=lambda a,b:a/b if b else None
    return {'positive_class':'fail','matched_binary_reviews':tp+fp+fn+tn,'confusion_matrix':matrix,
            'precision':divide(tp,tp+fp),'recall':divide(tp,tp+fn),
            'agreement':divide(tp+tn,tp+fp+fn+tn),'unreviewed':missing,
            'excluded_nonindependent':nonindependent,'judge_abstentions':abstentions,'judge_errors':errors,
            'disagreements':disagreements,
            'scope':'Pilot, not held-out validation. Independence is self-reported; expertise is not established. Metrics exclude abstentions/errors; report these counts too.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',required=True,help='Batch directory name under evals/judge_runs')
    parser.add_argument('--db',type=Path,default=ROOT/'evals/labels/calibration.sqlite3')
    args=parser.parse_args();key='judge:'+args.batch
    batches=load_judge_batches()
    if key not in batches:parser.error('Unknown or incomplete batch')
    print(json.dumps(comparison(key,batches[key],CalibrationStore(args.db)),ensure_ascii=False,indent=2))
