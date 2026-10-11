import json
from pathlib import Path
from evals.judge import evaluate,digest,judge_input
from rag_traffic.config import Settings
p=Path('evals/judge_experiments/20260908T100301Z');m=json.loads((p/'manifest.json').read_text());cs=[json.loads(l) for l in (p/'cases.jsonl').read_text().splitlines()];s=Settings.from_env()
m['retry_note']='One explicit retry after ValueError on synthetic-v2-02; first rejected response usage unavailable.'
for c in cs[11:]:
 try:r=evaluate(c['row'],(p/'rubric.md').read_text(),s.openai_api_key,m['model'])
 except ValueError as e:print(str(e),flush=True);break
 r.update(case_id=c['row']['case_id'],expected=c['expected'],kind=c['kind'],input_hash=digest(judge_input(c['row'])))
 with (p/'results.jsonl').open('a') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 print(r['case_id'],r['judgment']['verdict'],flush=True)
else:m['status']='complete'
rs=[json.loads(l) for l in (p/'results.jsonl').read_text().splitlines()];m['completed']=len(rs);m['usage']={k:sum(r.get('usage',{}).get(k,0) for r in rs) for k in ['prompt_tokens','completion_tokens','total_tokens']};(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
