"""Freeze recent cloud traces and run a bounded judge pilot; no feedback writes."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from evals.judge import PROMPT, digest, evaluate, judge_input
from evals.tracking import ROOT, version_metadata
from rag_traffic.config import Settings
from review.langsmith_data import LangSmithReview


def write_json(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


async def run(limit):
    settings=Settings.from_env()
    if not settings.openai_api_key:raise ValueError('OPENAI_API_KEY is required')
    gateway=LangSmithReview(settings)
    batch=await gateway.load(limit)
    rows=batch['rows'][:limit]
    if not rows:raise ValueError('No completed chat traces found')
    dest=ROOT/'evals/judge_runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    dest.mkdir(parents=True)
    rubric=(ROOT/'evals/rubric.md').read_text()
    # Persist only the trace input allowlist, not feedback, corrections or reviewer identities.
    frozen=[]
    for row in rows:
        item={**row,'input_hash':digest(judge_input(row))}
        frozen.append(item)
    (dest/'traces.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in frozen))
    (dest/'rubric.md').write_text(rubric)
    (dest/'prompt.txt').write_text(PROMPT)
    manifest={'created_at':datetime.now(timezone.utc).isoformat(),'status':'running',
              'model':os.getenv('OPENAI_JUDGE_MODEL',settings.openai_model or 'gpt-5.4-mini'),
              'reasoning_effort':'medium','max_completion_tokens':4000,
              'project_id':gateway.project_id,'cases':len(rows),
              'dataset_hash':digest([judge_input(r) for r in rows]),'rubric_hash':digest(rubric),
              'prompt_hash':digest(PROMPT),'version':version_metadata(),
              'scope':'Pilot on previously reviewed traces; not an independent holdout or human agreement measurement.'}
    write_json(dest/'manifest.json',manifest)
    completed=[]
    for row in frozen:
        start=perf_counter()
        result={'run_id':row['case_id'],'input_hash':row['input_hash']}
        try:
            result.update(await asyncio.to_thread(evaluate,row,rubric,settings.openai_api_key,manifest['model']))
            result['status']='ok'
        except Exception as exc:
            # Exception class only: never persist headers, API keys, or HTTP request dumps.
            result.update(status='error',error_type=type(exc).__name__)
        result['elapsed_seconds']=round(perf_counter()-start,3)
        with (dest/'results.jsonl').open('a') as stream:stream.write(json.dumps(result,ensure_ascii=False)+'\n')
        completed.append(result)
        print(f"{len(completed)}/{len(rows)} {row['case_id']} {result['status']}",flush=True)
        if result['status']=='error':break  # no silent retry, no cascade of paid failures
    manifest['status']='complete' if len(completed)==len(rows) and all(r['status']=='ok' for r in completed) else 'incomplete'
    manifest['completed']=len(completed)
    manifest['finished_at']=datetime.now(timezone.utc).isoformat()
    manifest['usage']={k:sum(r.get('usage',{}).get(k,0) for r in completed) for k in ('prompt_tokens','completion_tokens','total_tokens')}
    write_json(dest/'manifest.json',manifest)
    print('Judge batch:',dest,flush=True)
    if manifest['status']!='complete':raise RuntimeError('Judge pilot incomplete; inspect results before retrying')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit',type=int,default=10)
    args=parser.parse_args()
    if not 1<=args.limit<=50:parser.error('--limit must be between 1 and 50')
    asyncio.run(run(args.limit))
