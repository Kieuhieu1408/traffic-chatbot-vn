import json
from pathlib import Path
from datetime import datetime,timezone
from evals.judge import evaluate,PROMPT,digest
from evals.claim_judge import evaluate_claims,AUDIT_PROMPT
from rag_traffic.config import Settings
p=Path('evals/judge_experiments')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-claims');p.mkdir(parents=True)
r=json.loads(Path('evals/runs/idp-query-expansion/judge-new-failure/input.json').read_text())
cs=[dict(row=r,id='original-idp-long',expected='fail'),dict(row={**r,'answer':r['answer'].replace('**chỉ dùng khi','**dùng khi')},id='corrected-idp-long',expected='pass')]
assert cs[1]['row']['answer']!=r['answer']
old=json.loads(Path('evals/judge_experiments/20260908T103022Z-scope/cases.json').read_text())
for c in old[-2:]:cs.append(dict(row=c,id=c['id'],expected=c['expected']))
fresh=[json.loads(l) for l in Path('evals/fresh_runs/20260908-natural10/traces.jsonl').read_text().splitlines()]
r=fresh[8];cs.append(dict(row=r,id='bus-stop-long',expected='pass'))
cs.append(dict(row={**r,'answer':r['answer']+'\nBạn luôn phải giảm xuống đúng 20 km/h tại mọi điểm xe buýt. [6]'},id='bus-stop-invented-number',expected='fail'))
(p/'cases.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2));rubric=Path('evals/rubric.md').read_text();(p/'rubric.md').write_text(rubric);(p/'baseline-prompt.txt').write_text(PROMPT);(p/'claim-prompt.txt').write_text(AUDIT_PROMPT)
(p/'manifest.json').write_text(json.dumps(dict(scope='Assistant-labeled development cases, not expert calibration',cases_hash=digest(cs),status='running'),indent=2));print(p,flush=True)
s=Settings.from_env()
for c in cs:
 for name,fn in [('baseline',evaluate),('claims',evaluate_claims)]:
  try:o=fn(c['row'],rubric,s.openai_api_key,s.openai_model)
  except Exception as e:o={'status':'error','error_type':type(e).__name__}
  o.update(case_id=c['id'],evaluator=name)
  with (p/'results.jsonl').open('a') as f:f.write(json.dumps(o,ensure_ascii=False)+'\n')
  print(c['id'],name,o.get('audit',o.get('judgment',{})).get('verdict',o.get('status')),flush=True)
