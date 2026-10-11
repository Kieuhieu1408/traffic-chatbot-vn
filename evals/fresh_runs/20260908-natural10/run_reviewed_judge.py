import json
from pathlib import Path
from datetime import datetime,timezone
from evals.judge import evaluate,digest,judge_input,PROMPT
from rag_traffic.config import Settings
p=Path('evals/fresh_runs/20260908-natural10');rs=[json.loads(l) for l in (p/'rag.jsonl').read_text().splitlines()]
reasons=['Trả lời thiếu căn cứ về cấp lại IDP trong các đoạn được cung cấp là phù hợp; phần GPLX trong nước được tách rõ và có nguồn. Retrieval bỏ lỡ Điều 8 IDP dù corpus có, nên nhiệm vụ chưa được giải quyết.','Giữ điều kiện nhòe đến mức thiếu thông tin cần thiết; [4][5] hỗ trợ kết luận và điều kiện PET.','Phân biệt không cấp IDP phải nêu lý do với đơn chưa đúng cần hướng dẫn; [2] hỗ trợ cả hai.','[1] hỗ trợ 3 năm từ ngày phát hiện và thu hồi; suy ra hết thời hạn cấm mới được xem xét nếu đủ điều kiện không phải hứa được cấp. [3] hỗ trợ phần GPLX trong nước 5 năm.','Đọc toàn câu: không khẳng định IDP là thẻ nhựa, cuối câu nói chưa đủ căn cứ; hai nguồn dẫn không mô tả hình thức. Mở đầu Không dễ gây hiểu nhầm nhưng đã được giới hạn ngay sau. Retrieval thiếu Điều 4 mô tả sổ A6.','[1] yêu cầu giảm tốc qua trường học để dừng an toàn, không đặt điều kiện vượt tốc độ tối đa.','[2] nêu súc vật chăn thả sát đường; không tự thêm ngoại lệ hoặc con số.','[2] hỗ trợ cho xe sau vượt; phần CSGT chỉ là tình huống có điều kiện riêng được [1] hỗ trợ.','[6] nêu đến gần điểm dừng có người lên xuống phải giảm để dừng an toàn; không bịa km/h.','[3] nêu gần đỉnh dốc; [4] hỗ trợ khoảng cách lớn hơn khi đèo dốc.']
rows=[]
with (p/'assistant-review.jsonl').open('x') as f:
 for x,reason in zip(rs,reasons,strict=True):
  d=x['output'];row={'case_id':x['case_id'],'query':x['query'],'history':[],'answer':d['answer'],'results':[{**s,'rank':i} for i,s in enumerate(d['results'],1)],'trace_id':d['trace_id']};rows.append(row)
  f.write(json.dumps(dict(case_id=row['case_id'],input_hash=digest(judge_input(row)),reviewer='assistant',human=False,verdict='pass',review_reason=reason,judge_seen=False,created_at=datetime.now(timezone.utc).isoformat()),ensure_ascii=False)+'\n')
(p/'traces.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));(p/'prompt.txt').write_text(PROMPT)
assert Path('evals/rubric.md').read_text()==(p/'rubric.md').read_text()
assert Path('evals/judge.py').read_text()==(p/'judge.py').read_text()
s=Settings.from_env()
for r in rows:
 try:out=evaluate(r,(p/'rubric.md').read_text(),s.openai_api_key,s.openai_model)
 except Exception as e:out={'status':'error','error_type':type(e).__name__}
 out.update(case_id=r['case_id'],input_hash=digest(judge_input(r)))
 with (p/'judge-results.jsonl').open('a') as f:f.write(json.dumps(out,ensure_ascii=False)+'\n')
 print(r['case_id'],'saved',flush=True)
 if out.get('status')=='error':break
