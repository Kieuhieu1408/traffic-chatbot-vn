# Đối chiếu nhãn trợ lý với LLM judge

**Goal:** tìm nơi hai người chấm AI hiểu rubric khác nhau, để làm rõ tiêu chuẩn trước khi tin vào điểm tự động.

Đã lưu 10 nhãn `reviewer=assistant` trước khi mở kết quả judge trong lượt này. Trợ lý đã biết một số nhận xét cũ từ hội thoại; đây không phải blind review độc lập hay nhãn chuyên gia. Chấm theo nguồn trong trace, không xác nhận pháp luật hiện hành. Không ghi vào kho human calibration hoặc thay nhãn LangSmith cũ.

| Ca | Câu hỏi | Trợ lý | Judge |
|---|---|---|---|
| 1 | Tôi là người nước ngoài có thẻ tạm trú ở Việt Nam và bằng lái Việt Nam bằng thẻ PET còn hạn. Như vậy tôi đã đủ điều kiện xin bằng lái xe quốc tế chưa? | pass | pass |
| 2 | Tôi đi xe mô tô ngoài khu dân cư, trên đường có dải phân cách giữa, không phải cao tốc và không có biển hạn chế tốc độ riêng. Mức tối đa là 60 hay 70 km/h? | fail | pass |
| 3 | Tôi đi xe gắn máy điện trên đường thường, không phải cao tốc. Tôi chạy 50 km/h có vượt mức tối đa không? | pass | pass |
| 4 | Nếu trời mưa, vẫn chạy 80 km/h thì giữ 55 mét với xe trước có đủ không? Có phải cứ nhân đôi khoảng cách là được không? | pass | pass |
| 5 | Tôi chạy ô tô đúng 80 km/h, đường khô ráo và không có biển cự ly tối thiểu. Giữ cách xe trước 50 mét đã đủ chưa? | pass | pass |
| 6 | Vậy tôi dùng bằng quốc tế đó để lái xe ở Việt Nam, khỏi mang bằng Việt Nam được không? | fail | pass |
| 7 | Thế có bằng quốc tế rồi thì khi lái xe ở nước ngoài tôi có cần mang bằng Việt Nam nữa không? | pass | pass |
| 8 | Bằng lái Việt Nam của tôi còn hạn 1 năm. Nếu giờ xin bằng lái xe quốc tế thì có được cấp thời hạn 3 năm không? | pass | pass |
| 9 | Bằng lái Việt Nam của tôi còn hạn 1 năm. Nếu giờ xin bằng lái xe quốc tế thì có được cấp thời hạn 3 năm không? | pass | pass |
| 10 | Theo Thông tư 31/2019 trong tài liệu, đường chỉ chia hai chiều bằng vạch sơn có phải đường đôi không? | pass | pass |

## Ý nghĩa kết quả

Đồng thuận 8/10 (80%). Nếu tạm dùng trợ lý làm tham chiếu và Trượt là lớp dương: TP=0, FP=0, FN=2, TN=8; recall phát hiện Trượt=0/2, precision không xác định vì judge không dự đoán Trượt nào. Đây chỉ là phép so sánh với nhãn AI tham chiếu còn có thể sai, không phải độ chính xác thực tế. Hai câu hỏi IDP thời hạn trùng nhau và các lượt cùng hội thoại cũng không độc lập.

## Hai bất đồng cần phân xử

### `01a08037-7dbd-7450-a1be-568f87a41cae`

Tôi đi xe mô tô ngoài khu dân cư, trên đường có dải phân cách giữa, không phải cao tốc và không có biển hạn chế tốc độ riêng. Mức tối đa là 60 hay 70 km/h?

**Trợ lý:** Bảng [3] hỗ trợ 70/60 và [5] hỗ trợ 40 cho xe gắn máy. Nhưng câu “thì phải đi theo biển báo đó” dẫn [4], vốn quy định việc đặt biển, chưa cung cấp quy định trực tiếp về nghĩa vụ chấp hành biển trên đường thường. Đây là lỗi căn cứ trích dẫn theo rubric v1; không kết luận nghĩa vụ đó sai về luật. Thiếu định nghĩa đường đôi trong retrieval là vấn đề riêng; phản hồi có điều kiện khi thiếu định nghĩa không tự động là lỗi.

**Judge:** The answer is supported by the provided sources and correctly frames the speed limit as dependent on road type under Article 7, with the separate-sign caveat supported by Article 10.

### `01a0802e-9db2-74b2-ac9b-51a9c8942962`

Vậy tôi dùng bằng quốc tế đó để lái xe ở Việt Nam, khỏi mang bằng Việt Nam được không?

**Trợ lý:** Kết luận IDP Việt Nam không có giá trị sử dụng tại Việt Nam đúng theo [1][2]. Tuy nhiên phần hướng dẫn sử dụng IDP nước ngoài bỏ điều kiện GPLX quốc gia phải phù hợp hạng xe điều khiển có trong [6]. Điều kiện này có ý nghĩa khi đưa hướng dẫn sử dụng. Không lấy riêng việc dòng tóm tắt rút gọn “Công ước Viên” làm lỗi, vì phần mở đầu đã giới hạn phạm vi.

**Judge:** The answer is supported by the provided sources: it correctly states that a Vietnam-issued IDP has no use in Vietnam, and that an IDP from a Vienna Convention country used in Vietnam must be carried together with the national driving license.

## Bước tiếp theo và mục tiêu

1. Làm rõ tiêu chuẩn căn cứ: nghĩa của “biển hạn chế tốc độ” có đủ hỗ trợ nghĩa vụ chấp hành, hay rubric cần đoạn quy định trực tiếp? **Goal:** phân biệt suy luận hợp lý với dẫn nguồn không đủ, tránh ép judge đồng ý với trợ lý.
2. Làm rõ điều kiện quan trọng: khi chỉ trả lời cần mang giấy tờ gì, việc bỏ hạng xe có làm câu trả lời thiếu nghiêm trọng không? Nếu chủ động mở rộng thành hướng dẫn sử dụng IDP, ngưỡng có khác không? **Goal:** chấm nhất quán theo phạm vi câu trả lời.
3. Sau khi chốt, thêm cặp ví dụ đạt/trượt thể hiện ranh giới vào rubric/prompt có phiên bản, rồi chạy thử. **Goal:** kiểm tra judge hiểu tiêu chuẩn, không chỉ nhớ hai ca này.
4. Đánh giá lại trên các trace mới chưa dùng chỉnh prompt; khi có người chuyên môn, nhờ phân xử các ca biên. **Goal:** đo khả năng áp dụng tiêu chuẩn ngoài bộ đã xem.

## Ghi chú về nhãn trước đây

Ca mang IDP ra nước ngoài được lượt này chấm Đạt: người dùng đã nói GPLX Việt Nam còn hạn một năm, nên nhắc “bằng còn hiệu lực” trong ngữ cảnh đó không đủ để kết luận lỗi. Nhận xét Trượt trước đây quá chặt ở điểm này. Nhãn cũ được giữ nguyên để truy vết; nhãn mới nằm trong `assistant-review.jsonl`.

Chưa chỉnh prompt, chưa gọi thêm API trả phí, chưa hoàn tất human calibration.
