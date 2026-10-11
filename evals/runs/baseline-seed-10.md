# Kết quả baseline retrieval — 10 câu từ corpus

Cấu hình: top_k=6, min_score=0.55. Gọi trực tiếp VectorRetriever.search, cùng đường retrieval mà UI/API sử dụng. Không chạy qua trình duyệt hoặc HTTP endpoint. Chưa cấu hình LLM nên không đánh giá generation.

## Kết quả

- Đối chiếu ID chính xác: 6/10 ca đủ tất cả gold ID; recall trung bình 0,65; MRR 0,575.
- Trợ lý đọc các ca thiếu ID và đối chiếu nội dung: 9/10 ca có căn cứ hỗ trợ các ý cần trả lời trong top 6. Đây là nhãn đánh giá của trợ lý, chờ người dùng duyệt; không phải tỷ lệ câu trả lời đúng.
- Câu 008 thiếu căn cứ. Câu 001 có căn cứ nhưng đầu đoạn bị cắt.
- Không thay đổi gold dataset để làm tăng điểm; giữ kết quả ID tự động và nhận xét nội dung riêng.

| Ca | Đủ gold ID | Đối chiếu nội dung | Nhận xét |
|---|---|---|---|
| 001 | Không | Có căn cứ | Top 1 là chunk chồng lấn efec83cbecf7f82735737fe5: có mệnh đề vạch sơn không phải đường đôi và tiêu chí dải phân cách. Đầu câu bị cắt; đủ ý cho câu hỏi cụ thể nhưng chất lượng chunk cần cải thiện. |
| 002 | Có | Có căn cứ | Tìm đủ gold đã đối chiếu từ corpus. |
| 003 | Có | Có căn cứ | Tìm đủ gold đã đối chiếu từ corpus. Nguồn đúng ở hạng 4; evidence_only_answer chỉ trích 3 kết quả đầu nên phần answer fallback có thể không hiển thị căn cứ này, dù results có chứa. |
| 004 | Có | Có căn cứ | Tìm đủ gold đã đối chiếu từ corpus. |
| 005 | Có | Có căn cứ | Tìm đủ gold đã đối chiếu từ corpus. |
| 006 | Có | Có căn cứ | Tìm đủ gold đã đối chiếu từ corpus. |
| 007 | Có | Có căn cứ | Tìm đủ gold đã đối chiếu từ corpus. |
| 008 | Không | Thiếu căn cứ | Không có Điều 6 về đối tượng được cấp IDP trong top 6. Các đoạn về sử dụng/thủ tục không đủ thay thế điều kiện PET và đối tượng cấp. |
| 009 | Không | Có căn cứ | Top 1 là bản PDF a619cafb6419190e2764107b của Điều 10; nội dung hỗ trợ đầy đủ như bản DOCX đã gán nhãn. |
| 010 | Không | Có căn cứ | Top 1 chứa Điều 10 bản PDF tương đương; top 2 chứa Điều 11. Đủ hai căn cứ. |

## Việc nên làm tiếp

1. Người dùng xem câu 008 và đối chiếu Điều 6 để xác nhận lỗi retrieval.
2. Điều tra thứ hạng ứng viên của Điều 6 trước/sau lọc, rồi thử thay đổi có kiểm soát. Chưa có bằng chứng để quy lỗi cho ngưỡng 0,55.
3. Bổ sung nhóm nguồn tương đương đã duyệt vào cách chấm; không coi mọi chunk cùng điều là tương đương nếu chưa đọc nội dung.
4. Khi có cấu hình LLM, chạy cả 10 câu và chấm riêng câu trả lời/trích dẫn. Bộ này nhỏ và đã nêu tên thông tư, chưa đại diện chất lượng tổng thể.

## Chạy lại

```bash
.venv/bin/python -m evals.run_seed_retrieval
```

[Trace đầy đủ của lần chạy](20260907T142623622128Z/retrieval.json).
