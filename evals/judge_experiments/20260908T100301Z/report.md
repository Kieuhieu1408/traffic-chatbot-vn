# Rubric v2: phân xử và kiểm tra judge

Goal: phân biệt lỗi có ý nghĩa với thiếu chi tiết vô hại; kiểm tra judge có bắt được câu trả lời sai.

Hai ca bất đồng cũ được assistant phân xử thành Pass: nghĩa thông thường của biển hạn chế tốc độ cho phép suy luận về việc theo biển; yêu cầu mang hai giấy tờ không đồng nghĩa hai giấy tờ là đủ mọi điều kiện. Giữ nguyên nhãn v1 và không sửa feedback LangSmith.

Kết quả cuối: 10/10 ca phát triển Pass; 6/6 probe giả lập khớp nhãn assistant đã lưu trước khi chạy (3 Pass, 3 Fail). Các lỗi được bắt: sai ô bảng khoảng cách; bịa quy tắc nhân đôi luôn an toàn; đánh đồng tạm trú với thường trú. Đây không phải human calibration hoặc holdout độc lập.

Phát hiện kỹ thuật: judge bọc câu trích nguyên văn trong ngoặc kép làm validator từ chối. Đã cho phép bỏ đúng một cặp ngoặc ngoài khi nội dung bên trong thực sự có trong answer; vẫn từ chối câu trích sai. 54 tests qua, gồm regression cho hai trường hợp này. Ba probe Fail được chạy lại sau sửa; các lần thất bại không được âm thầm tính thành nhãn chất lượng. Token usage trong manifest là mức tối thiểu vì một số phản hồi bị từ chối ban đầu chưa lưu usage.

Nguồn: cases.jsonl chứa câu hỏi, nguồn, answer và nhãn kỳ vọng assistant; rubric.md/prompt.txt là snapshot; results.jsonl giữ các kết quả đã lưu; final-results.jsonl chọn kết quả hợp lệ cuối.

Bước tiếp theo: thu thập và chấm trace thực mới, trước khi xem judge. Goal: kiểm tra tiêu chuẩn ngoài các ví dụ đã dùng phát triển. Chưa có đánh giá chuyên gia, chưa chứng minh độ đúng pháp luật hiện hành.
