"""Summarize pilot outcomes and diagnostic slices without claiming expert quality."""
import json
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parent

def main():
 p=ROOT/'runs/pilot-v1';scores=[json.loads(l) for l in (p/'judge-results.jsonl').read_text().splitlines()]
 retry_path=p/'judge-retries.jsonl'
 if retry_path.exists():
  latest={(r['stage'],r['split'],r['case_id']):r for r in scores}
  for line in retry_path.read_text().splitlines():
   r=json.loads(line);latest[(r['stage'],r['split'],r['case_id'])]=r
  scores=list(latest.values())
 groups=defaultdict(lambda:dict(pass_count=0,fail_count=0,abstain=0,error=0,total=0))
 for r in scores:
  for kind,value in [('split',r['split']),('capability',r['capability']),('topic',r['topic'])]:
   key=(r['stage'],kind,value);g=groups[key];g['total']+=1
   v=r.get('judgment',{}).get('verdict')
   k='error' if 'judgment' not in r else 'abstain' if v is None else v+'_count'
   g[k]+=1
 result=[dict(stage=k[0],slice_type=k[1],slice=k[2],**v) for k,v in groups.items()]
 (p/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 lines=['# Qwen3-1.7B QLoRA pilot','','Goal: học vòng dữ liệu → baseline → train → eval. Nhãn dưới đây do LLM judge v3, chưa phải chuyên gia.','','| Chế độ | Trước: Đạt/tổng | Sau: Đạt/tổng |','|---|---|---|']
 for split in ['dev','test','end-to-end']:
  values=[groups[(stage,'split',split)] for stage in ['baseline','after']]
  lines.append('| '+split+' | '+' | '.join(f"{g['pass_count']}/{g['total']} (fail {g['fail_count']}, abstain {g['abstain']}, error {g['error']})" for g in values)+' |')
 lines+=['','Một phản hồi judge đầu tiên bị lỗi kỹ thuật, được giữ trong judge-results.jsonl và thử lại một lần trong judge-retries.jsonl; bảng dùng kết quả hợp lệ cuối, không đếm retry thành mẫu mới.','','End-to-end gồm cả câu dev/test có nguồn; không cộng các chế độ thành số câu độc lập. Context và decoding giữ nguyên, chỉ thêm adapter. Test không dùng tối ưu; cấu hình 3 epochs được chốt trước khi chạy.','','Bộ quá nhỏ để kết luận chất lượng tổng thể. Việc chia văn bản làm khác phân phối chủ đề; train thiếu bài đọc bảng. Labels do assistant/LLM, không human calibration. Không tuyên bố tốt hơn GPT hoặc đúng luật hiện hành. Xem metrics.json để đọc theo capability/topic; nhóm ít mẫu chưa đủ kết luận.','','Loss giảm chỉ chứng minh model khớp dữ liệu train hơn, không tự chứng minh đáp án tốt hơn. Adapter lưu riêng và chưa đưa vào ứng dụng GPT. Cần thêm dữ liệu đa dạng và review chuyên môn trước khi dùng sản phẩm.']
 for stage in ['baseline','after']:
  rows=[json.loads(l) for l in (p/(stage+'.jsonl')).read_text().splitlines()]
  lines.append(f"\n{stage}: {sum(r['truncated'] for r in rows)}/{len(rows)} output không kết thúc bằng EOS trong ngân sách; thời gian tổng {sum(r['seconds'] for r in rows):.1f}s.")
 (p/'report.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':main()
