"""Build an assistant-curated learning pilot with document-disjoint splits."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
 chunks=[json.loads(l) for l in (ROOT/'data/index/chunks.jsonl').read_text().splitlines()]
 byid={c['chunk_id']:c for c in chunks}
 # Exact source spans are retained; references are assistant-written, not expert gold.
 specs=[
 ('train','a549bae4ac8c9eb35af8db62','Từ 03 tháng đến dưới 01 năm','Bằng lái quá hạn 6 tháng thì phải thi lại phần nào?','Phải sát hạch lại lý thuyết theo nguồn được cung cấp. [1]','condition'),
 ('train','a549bae4ac8c9eb35af8db62','Từ 01 năm trở lên','Bằng lái quá hạn hơn một năm thì thi lại những gì?','Phải sát hạch lại cả lý thuyết và thực hành. [1]','condition'),
 ('train','a549bae4ac8c9eb35af8db62','Người có giấy phép lái xe bị mất','Mất bằng lái còn hạn có được xét cấp lại không?','Có, người mất giấy phép lái xe còn thời hạn sử dụng được xét cấp lại. [1]','direct'),
 ('train','582b10a4f9d7e088375cae53','Người dự sát hạch lại có nhu cầu ôn tập','Thi sát hạch lại có bắt buộc học lại toàn bộ chương trình không?','Không phải học lại theo chương trình đào tạo; nếu cần ôn tập thì đăng ký để được hướng dẫn và nộp phí ôn tập. [1]','condition'),
 ('train','2995f67158f3ece21afbdf02','Người nước ngoài cư trú, làm việc','Tôi là người nước ngoài có thẻ tạm trú 6 tháng và bằng quốc gia còn hạn, muốn lái xe ở Việt Nam. Có được xét đổi bằng không?','Theo nguồn, người nước ngoài cư trú, làm việc hoặc học tập tại Việt Nam có giấy tờ cư trú từ 3 tháng trở lên và GPLX quốc gia còn hạn, nếu có nhu cầu lái xe ở Việt Nam được xét đổi sang GPLX tương ứng. [1]','condition'),
 ('train','2995f67158f3ece21afbdf02','Giấy phép lái xe tạm thời của nước ngoài','Bằng lái tạm thời nước ngoài có được đổi sang bằng Việt Nam không?','Nguồn liệt kê giấy phép lái xe tạm thời của nước ngoài trong các trường hợp không đổi giấy phép lái xe. [1]','condition'),
 ('dev','e85b959216ecec3d583def89','Trường hợp IDP bị mất hoặc hư hỏng','IDP bị hỏng thì xử lý thế nào?','Lập đơn đề nghị cấp lại theo khoản 1 Điều 8. [1]','direct'),
 ('dev','e85b959216ecec3d583def89','Trong thời hạn không quá 05 ngày','Cơ quan không cấp IDP có cần nói lý do không?','Có. Trường hợp không cấp IDP phải trả lời và nêu rõ lý do. [1]','direct'),
 ('dev','eb67accf99d67f008179560d','IDP là một quyển sổ','IDP có hình thức như thế nào?','IDP là quyển sổ A6, bìa màu xám, các trang bên trong màu trắng. [1]','direct'),
 ('test','d9a189322b5af7963da4b1d0',None,'Đường khô, chạy đúng 100 km/h, không có biển cự ly riêng thì cần cách xe trước tối thiểu bao nhiêu?','Tốc độ 100 km/h thuộc khoảng 80 < V ≤ 100, khoảng cách tối thiểu là 70 m. [1]','table'),
 ('test','d9a189322b5af7963da4b1d0',None,'Đường khô, chạy đúng 60 km/h thì khoảng cách tối thiểu là 35 hay 55 m?','Tại V=60 km/h, khoảng cách tối thiểu là 35 m theo bảng. [1]','table'),
 ('test','71daf3e77b45974a7828b0f4','Có súc vật đi trên đường','Bò chăn thả sát đường thì có cần giảm tốc không?','Có, phải giảm tốc để có thể dừng an toàn khi có súc vật đi trên đường hoặc chăn thả sát đường. [1]','condition'),
 ('test','71daf3e77b45974a7828b0f4','Qua khu vực có trường học','Qua khu vực trường học có phải giảm tốc không?','Có, phải giảm tốc để có thể dừng an toàn khi qua khu vực có trường học. [1]','condition'),
 ]
 rows=[]
 for i,(split,id,needle,q,a,cap) in enumerate(specs):
  c=byid[id];text=c['content']
  if needle:
   line=next(l for l in text.splitlines() if needle in l)
   if split=='test':line=text.splitlines()[1]+'\n'+line
   text=line
  rows.append(dict(case_id=f'pilot-{i:02}',split=split,group=c['document_id'],query=q,answer=a,capability=cap,
      sources=[dict(rank=1,chunk_id=id,document_id=c['document_id'],article=c['article'],content=text)],
      reviewer='assistant',review_status='assistant_curated_not_expert',review_reason='Reference checked against the attached exact source span; current-law validity not assessed.'))
 # Add explicit no-evidence examples in each document group before freezing.
 for split in ['train','dev','test']:
  examples=[r for r in rows if r['split']==split]
  for r in examples[:2]:
   rows.append({**r,'case_id':r['case_id']+'-missing','sources':[], 'answer':'Các đoạn được cung cấp chưa đủ căn cứ để trả lời câu hỏi này.','capability':'missing_evidence'})
 # Train-only paraphrases share the parent's document and split.
 for r in list(rows):
  if r['split']=='train':
   rows.append({**r,'case_id':r['case_id']+'-variant','query':'Giúp tôi tra cứu: '+r['query']})
 out=ROOT/'finetune/data';out.mkdir(exist_ok=True)
 groups={s:{r['group'] for r in rows if r['split']==s} for s in ['train','dev','test']}
 assert all(not groups[a]&groups[b] for a,b in [('train','dev'),('train','test'),('dev','test')])
 for r in rows:
  for src in r['sources']:
   # All source lines originate in the corpus (the speed preamble can be joined).
   assert all(line in byid[src['chunk_id']]['content'] for line in src['content'].splitlines())
 for split in groups:
  selected=[r for r in rows if r['split']==split]
  (out/(split+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in selected))
 manifest={'scope':'Small learning pilot; document-disjoint but topic distribution differs. Assistant labels, not expert gold.',
 'groups':{k:sorted(v) for k,v in groups.items()},'counts':{s:sum(r['split']==s for r in rows) for s in groups},
 'hashes':{s:hashlib.sha256((out/(s+'.jsonl')).read_bytes()).hexdigest() for s in groups},
 'known_gaps':['No comparison or multi-turn cases in this pilot','Only test contains tables; train cannot teach table-specific behavior','No production or independent expert labels','All test examples already familiar to assistant from prior work; unseen by adapter training only']}
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(manifest)
if __name__=='__main__':main()
