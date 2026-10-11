"""Read-only descriptive A/B report; no winner or significance claim."""
import argparse
import json
import sqlite3
from pathlib import Path
from rag_traffic.ab import EXPERIMENT


def report(path):
    if not path.exists():
        return {'experiment':EXPERIMENT,'status':'no_data','arms':{}}
    with sqlite3.connect(f'file:{path.resolve()}?mode=ro',uri=True) as db:
        rows=db.execute('SELECT session,arm,helpful,elapsed,mode FROM events WHERE experiment=? ORDER BY rowid',(EXPERIMENT,)).fetchall()
    first={}
    for row in rows:first.setdefault(row[0],row)
    out={}
    for arm in ['A','B']:
        selected=[r for r in first.values() if r[1]==arm];n=len(selected)
        feedback=[r[2] for r in selected if r[2] is not None];yes=sum(feedback)
        latency=sorted(r[3] for r in selected)
        out[arm]={'sessions':n,'feedback_count':len(feedback),'helpful_count':yes,
            'response_rate':len(feedback)/n if n else None,
            'helpful_among_respondents':yes/len(feedback) if feedback else None,
            'confirmed_helpful_per_session':yes/n if n else None,
            'missing_feedback':n-len(feedback),
            'first_answer_latency_p95_seconds':latency[max(0,(__import__('math').ceil(.95*n)-1))] if n else None,
            'evidence_only_count':sum(r[4]!='rag' for r in selected)}
    return {'experiment':EXPERIMENT,'unit':'first eligible response per session','arms':out,
            'interpretation':'Descriptive pilot only. Missing feedback is not a negative rating; no winner inferred.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=Path('data/ab/events.sqlite3'))
    args=parser.parse_args();print(json.dumps(report(args.db),indent=2))
