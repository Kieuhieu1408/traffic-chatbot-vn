# Qwen3-1.7B QLoRA pilot

Goal: học vòng dữ liệu → baseline → train → eval. Nhãn dưới đây do LLM judge v3, chưa phải chuyên gia.

| Chế độ | Trước: Đạt/tổng | Sau: Đạt/tổng |
|---|---|---|
| dev | 5/5 (fail 0, abstain 0, error 0) | 4/5 (fail 1, abstain 0, error 0) |
| test | 4/6 (fail 2, abstain 0, error 0) | 5/6 (fail 1, abstain 0, error 0) |
| end-to-end | 3/7 (fail 4, abstain 0, error 0) | 3/7 (fail 4, abstain 0, error 0) |

Một phản hồi judge đầu tiên bị lỗi kỹ thuật, được giữ trong judge-results.jsonl và thử lại một lần trong judge-retries.jsonl; bảng dùng kết quả hợp lệ cuối, không đếm retry thành mẫu mới.

End-to-end gồm cả câu dev/test có nguồn; không cộng các chế độ thành số câu độc lập. Context và decoding giữ nguyên, chỉ thêm adapter. Test không dùng tối ưu; cấu hình 3 epochs được chốt trước khi chạy.

Bộ quá nhỏ để kết luận chất lượng tổng thể. Việc chia văn bản làm khác phân phối chủ đề; train thiếu bài đọc bảng. Labels do assistant/LLM, không human calibration. Không tuyên bố tốt hơn GPT hoặc đúng luật hiện hành. Xem metrics.json để đọc theo capability/topic; nhóm ít mẫu chưa đủ kết luận.

Loss giảm chỉ chứng minh model khớp dữ liệu train hơn, không tự chứng minh đáp án tốt hơn. Adapter lưu riêng và chưa đưa vào ứng dụng GPT. Cần thêm dữ liệu đa dạng và review chuyên môn trước khi dùng sản phẩm.

baseline: 0/18 output không kết thúc bằng EOS trong ngân sách; thời gian tổng 9.1s.

after: 0/18 output không kết thúc bằng EOS trong ngân sách; thời gian tổng 19.4s.
