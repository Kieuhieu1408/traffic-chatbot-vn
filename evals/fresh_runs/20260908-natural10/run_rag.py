import json,httpx,hashlib
from pathlib import Path
p=Path('evals/fresh_runs/20260908-natural10')
qs=['Bằng lái quốc tế của tôi bị mất. Tôi có xin cấp lại được không, hay phải thi lại?', 'Bằng lái Việt Nam của tôi bị nhòe mất một số thông tin. Tôi dùng bằng đó để xin bằng quốc tế được không?', 'Nếu hồ sơ xin bằng lái quốc tế không được chấp nhận thì cơ quan cấp có phải nói lý do không?', 'Nếu bị phát hiện gian dối để lấy bằng lái quốc tế thì bao lâu mới được xin cấp lại?', 'Bằng lái quốc tế của Việt Nam có phải một thẻ nhựa như bằng trong nước không?', 'Đi ngang trường học mà tôi vẫn đang chạy dưới tốc độ tối đa thì có cần giảm tốc nữa không?', 'Có đàn bò đang ăn cỏ sát mép đường, chưa bước ra đường. Tôi có cần giảm tốc độ không?', 'Khi cho xe phía sau vượt, tôi có phải giảm tốc không?', 'Đến gần điểm xe buýt đang đón trả khách thì tôi cần điều chỉnh tốc độ thế nào?', 'Tôi sắp tới đỉnh dốc, đường vẫn khô và không có biển hạn chế riêng. Có cần giảm tốc không?']
(p/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2))
for f in ['evals/rubric.md','evals/judge.py']:(p/Path(f).name).write_text(Path(f).read_text())
for i,q in enumerate(qs,1):
 r=httpx.post('http://127.0.0.1:8000/search',json={'query':q,'session_id':f'fresh-eval-20260908-{i}'},timeout=120);r.raise_for_status();d=r.json()
 with (p/'rag.jsonl').open('a') as f:f.write(json.dumps({'case_id':f'fresh-{i:02}','query':q,'output':d},ensure_ascii=False)+'\n')
 print(i,d.get('mode'),flush=True)
