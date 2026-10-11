# Thí nghiệm suy luận loại trừ

Goal: phân biệt nguồn nói tại X với khẳng định chỉ tại X, không đánh giá theo từ khóa.

Nhãn kỳ vọng do assistant gán trước lượt chạy. Sáu probe giả lập, một output RAG thật đã biết lỗi; không phải holdout hoặc human calibration.

| Ca | Kỳ vọng | v2 | v3 |
|---|---|---|---|
| idp-without-only | pass | pass | pass |
| idp-with-only | fail | pass | fail |
| idp-exclusion-paraphrase | fail | fail | fail |
| idp-scoped-uncertainty | pass | pass | pass |
| only-supported | pass | pass | pass |
| no-only-unsupported | fail | fail | fail |
| Output RAG đầy đủ | fail | pass (lượt trước) | pass |

v2 khớp 5/6 probe; v3 khớp 6/6. V3 vẫn bỏ sót lỗi trong câu trả lời RAG dài, dù phát hiện trong câu ngắn. Không diễn giải 6/6 là độ chính xác tổng quát.

Hai phản hồi đầu bị ValueError (v2 idp-without-only và v3 only-supported), mỗi ca được thử lại một lần và có kết quả hợp lệ. Giữ cả lần lỗi trong JSONL, không tính lỗi kỹ thuật thành nhãn Pass/Fail. Không đủ dữ liệu thô ở hai lần đầu để xác định nguyên nhân; chưa sửa validator trong thí nghiệm này.

Bước tiếp theo: thử đánh giá từng nhận định của câu trả lời đầy đủ và ghi căn cứ trước khi tổng hợp nhãn; cần kiểm tra trên ca khác để tránh tối ưu chỉ cho ví dụ này. Rubric v3 hiện là tiêu chuẩn phát triển, chưa đủ tin cậy để thay review.

Artifacts: cases.json lưu câu hỏi/nguồn/answer/nhãn kỳ vọng; v2/v3 prompt/rubric là snapshot, JSONL giữ các lần gọi. Original input: ../../runs/idp-query-expansion/judge-new-failure/input.json.
