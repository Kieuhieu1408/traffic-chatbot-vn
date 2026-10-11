# Rubric chấm câu trả lời RAG — v2

## Phạm vi

Chấm toàn bộ câu trả lời theo câu hỏi, lịch sử và căn cứ của ca kiểm tra. Không chỉ chấm ý chính. Với bộ corpus-seed-10, phạm vi là bản văn bản được nêu trong câu hỏi, không phải xác nhận pháp luật hiện hành.

Tiêu chuẩn được thống nhất với người dùng: mọi nhận định có ý nghĩa đối với người dùng phải đúng và có căn cứ. Không đánh Trượt chỉ vì văn phong chưa đẹp.

## Nhãn nhị phân

**Đạt** khi thỏa cả bốn tiêu chí:

1. Đúng yêu cầu: đúng đối tượng, hành vi, tình huống và phạm vi câu hỏi.
2. Có căn cứ: nhận định được tài liệu hỗ trợ; nguồn trích dẫn thực sự hỗ trợ ý được dẫn. Nhận xét về hệ thống phải nằm trong phạm vi thông tin quan sát được.
3. Đủ ý quan trọng: không bỏ điều kiện hoặc ngoại lệ làm thay đổi kết luận.
4. Biết giới hạn: không đoán khi thiếu thông tin/căn cứ; không tự suy đoán hiệu lực; phân biệt các đoạn truy xuất với toàn bộ corpus.

**Trượt** nếu có ít nhất một vi phạm ảnh hưởng ý nghĩa hoặc độ tin cậy của câu trả lời. Ý chính đúng không bù cho một nhận định phụ sai hoặc thiếu căn cứ có ý nghĩa với người dùng.

**Chưa chấm** là trạng thái, không phải nhãn chất lượng. Nếu người chấm chưa đủ căn cứ hoặc chuyên môn, bỏ qua để xem lại; không ép thành Đạt hoặc Trượt.

## Ví dụ đã thống nhất: câu 001

- Ý chính về đường chỉ phân chia bằng vạch sơn được nguồn hỗ trợ.
- Nhận định “corpus chưa cung cấp trọn vẹn toàn văn điều khoản” suy rộng từ các đoạn truy xuất sang toàn bộ kho dữ liệu, trong khi không đủ bằng chứng về kho.
- Kết luận: **Trượt** theo rubric v1, vì vi phạm Biết giới hạn.
- Lý do: “Kết luận chính đúng, nhưng model suy từ context thiếu sang corpus thiếu.”

Cách diễn đạt phù hợp hơn: “Các đoạn được cung cấp chưa chứa đầy đủ điều khoản”, nếu điều này đúng với context thực tế.

## Phân biệt lỗi hệ thống và lỗi câu trả lời

- Chunk bị cắt đầu hoặc căn cứ đúng đứng hạng 4 là tín hiệu cần điều tra ingestion/retrieval. Không tự động làm câu trả lời Trượt nếu nội dung vẫn đủ, đúng và có căn cứ.
- Retrieval thiếu nguồn nhưng model phản hồi thiếu căn cứ một cách phù hợp có thể đạt về hành vi phản hồi; tác vụ tìm nguồn vẫn có thể thất bại. Ghi rõ đối tượng đang đánh giá.
- Trích dẫn [n] tồn tại không chứng minh nguồn đó hỗ trợ nhận định.

## Cách ghi lý do

Khi Trượt, nêu nhận định sai/thiếu, căn cứ đối chiếu và tiêu chí vi phạm. Khi Đạt, lý do không bắt buộc. Nhóm lỗi và câu trả lời sửa là thông tin tùy chọn.

## Phiên bản và nhãn cũ

Rubric v1 thay thế cách đánh giá sơ bộ trước đây chỉ tập trung ý chính. Nhãn/báo cáo cũ không tự động được sửa và cần được duyệt lại nếu muốn so sánh theo v1. Không coi các lần chấm theo hai tiêu chuẩn là cùng một phép đo.

## Làm rõ v2 — 2026-09-08

**Goal:** đánh lỗi làm thay đổi ý nghĩa sử dụng, không phạt diễn đạt tương đương hoặc bắt mọi câu trả lời chép đủ điều luật.

- Cho phép suy luận hợp lý từ nội dung và nghĩa thông thường của nguồn. Không bắt buộc nguồn dùng nguyên văn nhận định. Không được tự thêm con số, quyền, ngoại lệ hoặc điều kiện không suy ra được.
- Đánh giá điều kiện trong toàn bộ câu trả lời và tình huống người dùng. “Phải mang A và B” là điều kiện cần, không tự động khẳng định “chỉ cần A và B là được phép”. Bỏ chi tiết khác chỉ là lỗi nếu làm thay đổi kết luận hoặc tạo hướng dẫn sai cho tình huống đang hỏi.
- Nếu câu trả lời khẳng định đủ điều kiện/được phép mà bỏ một điều kiện có thể làm đảo kết luận, chấm Trượt. Nếu chưa thể phân xử bằng nguồn, để chưa chấm.
- Dữ kiện người dùng cung cấp trong lịch sử có thể được dùng cho tình huống. Lời assistant cũ không phải nguồn thẩm quyền pháp lý.

### Phân xử hai ca phát triển (nhãn trợ lý, không phải expert gold)

1. Mô tô 60/70: **Đạt**. Bảng tốc độ được dẫn đúng; trả lời có điều kiện vì nguồn chưa có định nghĩa đường đôi là hành vi phù hợp. Điều đặt biển hạn chế tốc độ hỗ trợ cách hiểu thông thường rằng biển hạn chế tốc độ riêng chi phối tốc độ; không cần phạt chỉ vì thiếu một câu nghĩa vụ nguyên văn. Retrieval vẫn chưa giải quyết trọn nhu cầu xác định loại đường.
2. IDP dùng ở Việt Nam: **Đạt**. Kết luận IDP Việt Nam không có giá trị sử dụng tại Việt Nam đúng. Phần IDP nước ngoài nói phải mang cả hai giấy tờ, không khẳng định chỉ cần mang là đủ điều kiện. Phạm vi Công ước Viên đã nêu ở đầu. Nếu viết “chỉ cần hai giấy tờ, bất kể hạng xe”, phải Trượt vì trái điều kiện trong nguồn.

Đây là quyết định vận hành để học, có thể sửa khi có người chuyên môn phân xử. Nhãn v1 và kết quả judge cũ giữ nguyên; không gộp thành một phép đo cùng phiên bản.
