import json,hashlib
from pathlib import Path
from evals.judge import evaluate,PROMPT,digest
from rag_traffic.config import Settings
p=Path('evals/judge_experiments/20260908-stability')
# New controlled cases from a different provision. Labels frozen before inference.
source={'rank':1,'content':'Điều 8. Thủ tục cấp giấy phép lái xe quốc tế\nTrong thời hạn không quá 05 ngày làm việc, kể từ ngày nhận được đơn đề nghị cấp IDP, cơ quan cấp thực hiện việc cấp IDP; trường hợp không cấp IDP thì phải trả lời và nêu rõ lý do. Trường hợp đơn đề nghị không đúng theo quy định thì hướng dẫn thực hiện ngay khi tiếp nhận.\nTrường hợp IDP bị mất hoặc hư hỏng, cá nhân lập đơn đề nghị cấp lại.\nKhông cấp IDP nếu giấy phép lái xe quốc gia bị tẩy xóa, hư hỏng không còn đủ các thông tin cần thiết hoặc có sự khác biệt về nhận dạng.'}
items=[('Nộp đơn xin IDP thì bao lâu được giải quyết?','Theo nguồn [1], thời hạn không quá 5 ngày làm việc kể từ ngày nhận đơn; nếu không cấp phải trả lời và nêu lý do.','pass'),('Nộp đơn xin IDP thì bao lâu được giải quyết?','Bạn chắc chắn nhận IDP trong đúng 5 ngày theo lịch, kể cả cuối tuần. [1]','fail'),('Đơn IDP điền chưa đúng thì cơ quan tiếp nhận làm gì?','Nguồn yêu cầu hướng dẫn thực hiện ngay khi tiếp nhận đơn chưa đúng quy định. [1]','pass'),('Đơn IDP điền chưa đúng thì cơ quan tiếp nhận làm gì?','Cơ quan bắt buộc giữ đơn 30 ngày rồi mới hướng dẫn sửa. [1]','fail'),('IDP bị rách thì có cách xử lý không?','Bạn có thể lập đơn đề nghị cấp lại khi IDP hư hỏng theo nguồn [1]. Nguồn được cung cấp chưa nêu mức lệ phí.','pass'),('IDP bị rách thì có cách xử lý không?','Bạn có thể lập đơn đề nghị cấp lại khi IDP hư hỏng. Thủ tục này được miễn toàn bộ lệ phí. [1]','fail'),('Bằng quốc gia hỏng đến mức thiếu thông tin cần thiết có xin IDP được không?','Không cấp IDP trong trường hợp bằng quốc gia hư hỏng không còn đủ thông tin cần thiết theo [1].','pass'),('Bằng quốc gia hỏng đến mức thiếu thông tin cần thiết có xin IDP được không?','Vẫn được cấp IDP; chỉ cần khai tên bằng miệng, không cần kiểm tra bằng quốc gia. [1]','fail')]
cs=[dict(case_id=f'stability-{i:02}',query=q,answer=a,history=[],results=[source],expected=e,reviewer='assistant') for i,(q,a,e) in enumerate(items,1)]
(p/'cases.json').write_text(json.dumps(cs,ensure_ascii=False,indent=2));rubric=Path('evals/rubric.md').read_text();(p/'rubric.md').write_text(rubric);(p/'prompt.txt').write_text(PROMPT)
s=Settings.from_env();m=dict(status='running',model=s.openai_model,repeats=3,cases=8,scope='New synthetic assistant-authored answers from known corpus provision; not independent human gold or production distribution',cases_hash=digest(cs),rubric_hash=digest(rubric),prompt_hash=digest(PROMPT));(p/'manifest.json').write_text(json.dumps(m,indent=2))
for repeat in range(1,4):
 for c in cs:
  try:o=evaluate(c,rubric,s.openai_api_key,s.openai_model)
  except Exception as e:o=dict(status='error',error_type=type(e).__name__)
  o.update(case_id=c['case_id'],repeat=repeat)
  with (p/'results.jsonl').open('a') as f:f.write(json.dumps(o,ensure_ascii=False)+'\n')
  print(repeat,c['case_id'],o.get('judgment',{}).get('verdict',o.get('status')),flush=True)
