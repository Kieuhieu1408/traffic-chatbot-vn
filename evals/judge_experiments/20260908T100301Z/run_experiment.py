import json,asyncio
from pathlib import Path
from datetime import datetime,timezone
from evals.judge import evaluate,judge_input,digest,PROMPT
from rag_traffic.config import Settings
base=Path('evals/judge_runs/20260908T093514688801Z')
rows=[json.loads(l) for l in (base/'traces.jsonl').read_text().splitlines()]
p=Path('evals/judge_experiments')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');p.mkdir(parents=True)
rubric=Path('evals/rubric.md').read_text();(p/'rubric.md').write_text(rubric);(p/'prompt.txt').write_text(PROMPT)
cases=[]
for r in rows:cases.append(dict(row=r,expected='pass',kind='previously_seen_development'))
# New synthetic probes: author labels fixed before judging, no production-trace claim.
probes=[(4,'Tôi chạy đúng 80 km/h trên đường khô, không có biển cự ly. Cách 50 m đủ chưa?','Chưa đủ: 80 km/h thuộc khoảng 60 < V ≤ 80, cần ít nhất 55 m. [1]','pass'),(4,'Tôi chạy đúng 80 km/h trên đường khô, không có biển cự ly. Cách 50 m đủ chưa?','Đủ, vì 80 km/h chỉ cần giữ 35 m. [1]','fail'),(3,'Trời mưa chạy 80 km/h thì giữ 110 m chắc chắn đủ chưa?','Nguồn yêu cầu khoảng cách thích hợp lớn hơn mức trong bảng; không thể bảo đảm 110 m luôn đủ trong mọi điều kiện. [1]','pass'),(3,'Trời mưa chạy 80 km/h thì giữ 110 m chắc chắn đủ chưa?','Có, cứ nhân đôi 55 m là luôn đủ an toàn trong mọi điều kiện mưa. [1]','fail'),(0,'Tôi là người nước ngoài chỉ có thẻ tạm trú, bằng Việt Nam PET còn hạn. Đủ điều kiện cấp IDP chưa?','Theo điều kiện tại nguồn [1], người nước ngoài cần thẻ thường trú; dữ kiện thẻ tạm trú của bạn chưa đáp ứng điều kiện đó.','pass'),(0,'Tôi là người nước ngoài chỉ có thẻ tạm trú, bằng Việt Nam PET còn hạn. Đủ điều kiện cấp IDP chưa?','Đủ, thẻ tạm trú được coi như thẻ thường trú nên bạn đủ điều kiện xin IDP. [1]','fail')]
for n,(idx,q,a,e) in enumerate(probes,1):
 r={**rows[idx],'case_id':f'synthetic-v2-{n:02}','query':q,'answer':a,'history':[]}
 cases.append(dict(row=r,expected=e,kind='synthetic_probe_not_holdout'))
(p/'cases.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases))
settings=Settings.from_env();out=[]
manifest=dict(status='running',scope='Assistant-authored development and synthetic probes, not human calibration or independent holdout',cases=16,model=settings.openai_model,rubric_hash=digest(rubric),prompt_hash=digest(PROMPT),dataset_hash=digest([judge_input(c['row']) for c in cases]))
(p/'manifest.json').write_text(json.dumps(manifest,indent=2))
for c in cases:
 r=c['row']
 try: result=evaluate(r,rubric,settings.openai_api_key,settings.openai_model)
 except Exception as exc:
  manifest.update(status='incomplete',error_type=type(exc).__name__);break
 result.update(case_id=r['case_id'],expected=c['expected'],kind=c['kind'],input_hash=digest(judge_input(r)))
 out.append(result)
 with (p/'results.jsonl').open('a') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
 print(len(out),r['case_id'],result['judgment']['verdict'],flush=True)
else:manifest['status']='complete'
manifest['completed']=len(out);manifest['usage']={k:sum(r.get('usage',{}).get(k,0) for r in out) for k in ['prompt_tokens','completion_tokens','total_tokens']}
(p/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(p,flush=True)
