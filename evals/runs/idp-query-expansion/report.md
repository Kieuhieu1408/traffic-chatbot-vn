# Sửa truy xuất thuật ngữ IDP

Goal: nối cách hỏi tự nhiên của người dùng với thuật ngữ trong corpus để lấy đúng căn cứ, không gán sẵn câu trả lời.

Nguyên nhân: embedding ưu tiên thủ tục GPLX trong nước khi câu dùng “bằng lái quốc tế”. Chẩn đoán với top 30 cho thấy nguồn cấp lại IDP đứng hạng 16; nguồn mẫu IDP đứng hạng 20 ở câu hình thức (đều ngoài top 6). Thêm thuật ngữ đầy đủ và IDP đưa nguồn đúng lên hạng 1.

Thay đổi: chuẩn hóa các cách gọi rõ ràng “bằng lái [xe] quốc tế”, “GPLX quốc tế”, “giấy phép lái xe quốc tế” thành “giấy phép lái xe quốc tế IDP” chỉ cho embedding. Không đổi câu hỏi gửi generation; không suy IDP từ “bằng lái nước ngoài”. Trace retrieve-sources ghi cả query gốc và retrieval_query.

Kiểm tra: 56 tests qua. Chạy trước/sau trên 10 seed + 10 câu mới; độ phủ chunk gold của seed không giảm (8/10 ca đủ toàn bộ ID chuẩn; hai ca còn thiếu giữ nguyên). Các câu không được chuẩn hóa có kết quả giống hệt. Hai nguồn mục tiêu mới đều hạng 1. Không tăng k hoặc đổi index/model.

Chạy RAG thật sau khi nạp code:

- fresh-01: trả lời làm đơn cấp lại IDP; giữ phạm vi “không thấy quy định phải thi lại trong tài liệu”; đối chiếu các ý phụ có nguồn. Assistant: Pass.
- fresh-05: trả lời đúng hình thức quyển sổ A6. Tuy nhiên thêm “chỉ dùng ... trên lãnh thổ nước tham gia Công ước Viên”. Nguồn quy định nghĩa vụ mang giấy tờ trong phạm vi đó, chưa chứng minh không dùng được ở tất cả nước khác. Assistant: Fail theo rubric v2 vì suy rộng độc quyền phạm vi. Đây là output mới, không thay nhãn của output trước.

Kết luận thực nghiệm: hai lỗi truy xuất mục tiêu đã sửa; chưa thể coi toàn bộ câu trả lời sau sửa đều đạt. Lỗi generation mới được giữ làm ca lỗi thực để đánh giá judge. Hai câu này từ nay là ca phát triển/regression, không còn là holdout.

Artifacts: retrieval-before-after.json chứa toàn bộ top 6 và nguồn; fresh-01-answer.json/fresh-05-answer.json chứa câu trả lời thật và trace ID; assistant-review.jsonl chứa nhãn trợ lý. Không gọi lại judge trong bước sửa retrieval này.
