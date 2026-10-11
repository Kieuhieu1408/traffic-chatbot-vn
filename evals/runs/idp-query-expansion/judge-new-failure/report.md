# Judge kiểm tra lỗi phạm vi mới

Goal: kiểm tra judge có phát hiện ý phụ suy rộng phạm vi trong một câu trả lời RAG thật hay không, giữ nguyên rubric/prompt v2.

Kết quả: assistant Fail, judge Pass. Judge lý giải ngắn rằng câu trả lời được nguồn hỗ trợ và đúng phạm vi, không bàn riêng chữ “chỉ”.

Nhận định bị assistant đánh lỗi: “IDP do Việt Nam cấp chỉ dùng khi điều khiển phương tiện cơ giới trên lãnh thổ nước tham gia Công ước Viên”. Nguồn [2][4] nói người sử dụng IDP tại nước tham gia phải mang cả hai giấy tờ, và IDP Việt Nam không dùng tại Việt Nam. Nguồn này không đủ suy ra cấm/không dùng ở mọi nước ngoài nhóm. Chấm lỗi suy luận từ nguồn, không khẳng định quy định hiện hành ở các nước đó.

Đây là một bất đồng AI-vs-AI trên ca đã biết nhãn assistant; nếu dùng assistant làm tham chiếu thì là một false negative. Không đủ để ước lượng recall tổng thể hoặc độ đúng chuyên gia. Nhãn assistant không đưa vào prompt judge; input.json chỉ có câu hỏi, lịch sử, answer và nguồn.

Bước tiếp theo: bổ sung nguyên tắc phân biệt “áp dụng tại X” với “chỉ áp dụng tại X”, tạo cặp câu trả lời có/không có khẳng định loại trừ để kiểm tra ngưỡng. Nếu sửa prompt, đây trở thành ca phát triển và cần kiểm tra thêm trên các ca khác. Lượt này chưa sửa prompt hoặc rubric và không thay feedback LangSmith.
