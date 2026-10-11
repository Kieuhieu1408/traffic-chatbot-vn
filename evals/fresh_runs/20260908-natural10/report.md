# Kiểm tra trên 10 câu hỏi mới

Goal: kiểm tra rubric v2 và judge trên đầu ra RAG mới, giữ nguyên tiêu chuẩn trong cả lượt.

10 câu hỏi do assistant thiết kế từ corpus, chạy endpoint /search thật, mỗi câu một session mới. Đây là câu hỏi mới nhưng chỉ tập trung hai chủ đề và ba điều khoản; không đại diện đầy đủ người dùng thực. Không phải human calibration.

| Ca | Assistant | Judge |
|---|---|---|
| fresh-01 | pass | pass |
| fresh-02 | pass | pass |
| fresh-03 | pass | pass |
| fresh-04 | pass | pass |
| fresh-05 | pass | pass |
| fresh-06 | pass | pass |
| fresh-07 | pass | pass |
| fresh-08 | pass | pass |
| fresh-09 | pass | pass |
| fresh-10 | pass | pass |

Đồng thuận: 10/10. Trợ lý không gán ca Trượt nào nên chưa đo được recall phát hiện lỗi so với nhãn trợ lý. Không diễn giải điểm đồng thuận thành độ chính xác pháp lý.

## Bất đồng

Không có bất đồng nhãn.

## Phát hiện hữu ích hơn điểm số

- fresh-01: hỏi cấp lại IDP bị mất nhưng retrieval trả về thủ tục GPLX trong nước. Corpus có Điều 8, khoản 3 trong chunk e85b959216ecec3d583def89. Model thừa nhận thiếu căn cứ: hành vi trả lời có thể Đạt, nhưng tìm nguồn chưa đạt mục đích.
- fresh-05: hỏi hình thức IDP nhưng retrieval không lấy Điều 4 mô tả quyển sổ A6 (chunk eb67accf99d67f008179560d). Model cuối cùng nói chưa đủ căn cứ; câu mở đầu “Không” nên viết rõ hơn.
- Năm tình huống giảm tốc đều dựa cùng Điều 5; không coi chúng là năm chủ đề độc lập.

## Tiếp theo

Goal: sửa lỗi người dùng thực sự gặp. Dùng hai ca retrieval thiếu nguồn làm ví dụ điều tra truy xuất; giữ riêng việc chấm hành vi trả lời và khả năng hoàn thành nhu cầu. Cần bổ sung ca lỗi tự nhiên trước khi đánh giá độ nhạy bắt lỗi của judge. Không sửa rubric chỉ để tạo bất đồng hoặc ép có nhãn Trượt.
