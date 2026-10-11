"""Provisional v3 judge scores; never label as human/expert evaluation."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from evals.judge import evaluate,PROMPT,digest
from rag_traffic.config import Settings
ROOT=Path(__file__).resolve().parent

def main():
 out=ROOT/'runs/pilot-v1';settings=Settings.from_env();rubric=(ROOT.parent/'evals/rubric.md').read_text()
 (out/'judge-rubric.md').write_text(rubric);(out/'judge-prompt.txt').write_text(PROMPT)
 data={}
 for split in ['dev','test','end-to-end']:
  for line in (ROOT/'data'/f'{split}.jsonl').read_text().splitlines():
   r=json.loads(line);data[(split,r['case_id'])]=r
 tasks=[]
 for stage in ['baseline','after']:
  for line in (out/(stage+'.jsonl')).read_text().splitlines():tasks.append((stage,json.loads(line)))
 def score(task):
  stage,r=task;original=data[(r['split'],r['case_id'])]
  row=dict(query=original['query'],history=[],answer=r['answer'],results=r['sources'])
  try:result=evaluate(row,rubric,settings.openai_api_key,settings.openai_model)
  except Exception as e:result=dict(status='error',error_type=type(e).__name__)
  return dict(stage=stage,split=r['split'],case_id=r['case_id'],topic=original['group'],capability=original['capability'],reviewer='llm_judge_not_human',input_hash=digest(row),**result)
 with (out/'judge-results.jsonl').open('x') as f,ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(score,tasks):
   f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush()
   print(result['stage'],result['case_id'],result.get('judgment',{}).get('verdict',result.get('status')),flush=True)
if __name__=='__main__':main()
