# Thử judge đối chiếu từng nhận định

Goal: phát hiện ý phụ vượt nguồn trong câu trả lời dài mà không đánh oan câu đúng. Rubric v3 giữ nguyên; evaluator mới ở module riêng, chưa thay mặc định.

| Ca | Assistant kỳ vọng | Judge v3 | Claim audit |
|---|---|---|---|
| original-idp-long | fail | fail | fail |
| corrected-idp-long | pass | pass | pass |
| only-supported | pass | pass | pass |
| no-only-unsupported | fail | fail | fail |
| bus-stop-long | pass | pass | None |
| bus-stop-invented-number | fail | fail | fail |

Trong lượt này v3 khớp 6/6, audit khớp 5/6 và abstain 1/6. Trên 5 ca audit quyết định nhị phân, khớp 5/5; luôn báo kèm coverage 5/6 để tránh ẩn ca chưa kết luận. Các số này chỉ so với nhãn assistant trong bộ phát triển.

Audit bắt được ý loại trừ IDP và mức 20 km/h bịa thêm; bản bỏ ý loại trừ được Pass. Tuy nhiên câu xe buýt đúng bị abstain vì audit gắn unresolved cho disclaimer “chỉ áp dụng trong phạm vi nội dung tài liệu được cung cấp”. Ý không nêu km/h cụ thể thực tế được audit chấm supported. Đây là vấn đề phân biệt lời giới hạn phạm vi trả lời với nhận định pháp lý cần nguồn, không phải retrieval.

Judge v3 từng Pass ca IDP này ở lượt trước, nay Fail với cùng input/rubric. Vì vậy không kết luận audit tốt hơn chỉ từ một lượt; có biến thiên giữa các lần gọi. Chi tiết audit còn cho thấy cách đánh giá disclaimer thiếu nhất quán giữa hai bản IDP.

Giữ evaluator mới là thí nghiệm. Chưa sửa rubric v3, generation, feedback LangSmith hay judge mặc định. 62 tests kỹ thuật qua. Chưa có bảo đảm liệt kê đủ mọi claim; validator kiểm tra tính có thật của trích dẫn nhưng không chứng minh bao phủ đầy đủ hoặc đánh giá đúng.

Bước tiếp theo: làm rõ cách xử lý disclaimer và đo lặp trên bộ đa dạng, giữ tập kiểm tra riêng. Goal: giảm abstain không cần thiết và đo độ ổn định, thay vì chỉ tối ưu một ca lỗi.
