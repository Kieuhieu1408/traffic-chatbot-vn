# Kiểm tra khả năng bắt lỗi và độ ổn định

Goal: đóng băng tiêu chuẩn, đo kết quả lặp trên câu trả lời mới thay vì sửa prompt theo từng ca.

Tám câu trả lời giả lập mới (4 Pass/4 Fail theo assistant), nguồn rút gọn từ Điều 8 về cấp IDP; ba lượt, 24 calls. Bộ mới chưa dùng chỉnh prompt nhưng chủ đề quen thuộc, nguồn rút gọn và lỗi rõ ràng. Không phải phân phối production, expert gold hoặc 24 mẫu độc lập.

| Lượt | TP | FP | FN | TN | Precision | Recall | Abstain | Lỗi |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 0 | 0 | 4 | 100% | 100% | 0 | 0 |
| 2 | 4 | 0 | 0 | 4 | 100% | 100% | 0 | 0 |
| 3 | 4 | 0 | 0 | 4 | 100% | 100% | 0 | 0 |

Trượt là lớp dương. 8/8 ca giữ nguyên nhãn qua ba lần. Coverage 100%. Đo trên 8 ca không đủ suy ra độ chính xác tổng thể. Các ca khó đã biết từng đổi nhãn chưa được giải quyết bởi kết quả này.

## Quyết định sử dụng

Giữ judge v3 mặc định như công cụ hỗ trợ review, không dùng một mình để quyết định câu trả lời đúng về luật hoặc phát hành thay đổi. Claim audit tiếp tục ở mức thí nghiệm. Khi đổi model/prompt/rubric, chạy lại bộ regression và thêm dữ liệu chưa dùng phát triển. Giữ cả lỗi kỹ thuật và abstain; không ép thành Pass/Fail. Các bất đồng và ca phạm vi pháp lý cần review riêng.

## Phần nào hoàn tất, phần nào chưa

Đã có pipeline, rubric phiên bản, trace, nhãn assistant trước judge, thí nghiệm bất đồng, cặp đối chứng, dữ liệu mới, đo precision/recall và độ ổn định. Đây là phần thực hành tự động đã làm được.

Chưa có nhãn người chuyên môn độc lập; chưa đo trên bộ thực tế đa dạng đủ lớn; chưa có bằng chứng judge ổn định ở mọi ca khó. Vì vậy human calibration và mức tin cậy để vận hành tự động chưa hoàn tất. Không gọi AI-vs-AI là human agreement.

Tái tính không gọi API: `.venv/bin/python -m evals.summarize_repeats evals/judge_experiments/20260908-stability`. cases.json/results.jsonl/prompt.txt/rubric.md/manifest.json giữ dữ liệu và cấu hình. 64 tests kỹ thuật qua.
