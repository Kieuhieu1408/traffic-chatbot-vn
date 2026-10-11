# Đối chiếu retrieval sau sửa loại trùng

Goal: kiểm tra sửa lỗi logic có cải thiện căn cứ thực tế hoặc làm mất căn cứ ở câu khác.

- Trước: [retrieval.json](20260907T142623622128Z/retrieval.json).
- Sau: [retrieval.json](20260907T162205596793Z/retrieval.json).
- Cùng dataset, corpus, index manifest, k=6 và min_score=0,55 (đã đối chiếu hash/config).
- Chỉ chạy retrieval offline; không gọi GPT và không chấm lại câu trả lời hay sửa nhãn người dùng.
- Thay đổi: loại bản trùng theo văn bản + nội dung chuẩn hóa khoảng trắng, thay vì văn bản + điều.

| Chỉ số | Trước | Sau |
|---|---:|---:|
| Câu tìm đủ ID gold | 6/10 | 8/10 |
| Câu tìm ít nhất một ID gold | 7/10 | 8/10 |
| Recall gold trung bình theo câu | 0,65 | 0,80 |
| MRR theo ID gold | 0,575 | 0,625 |
| Đủ căn cứ chính theo đối chiếu nội dung của trợ lý | 9/10 | 9/10 |

## Vì sao điểm tăng nhưng chưa chứng minh chất lượng tăng?

- Câu 001–006: danh sách nguồn không đổi. Câu 001 vẫn có đoạn chứa căn cứ cần thiết ở hạng 1 dù khác ID gold.
- Câu 007: giữ nguồn chuẩn hạng 1; thay đổi các nguồn phụ.
- Câu 008: vẫn không tìm được Điều 6 về đối tượng được cấp IDP. Nguồn thủ tục cấp không thay thế đầy đủ điều kiện về đối tượng và giấy phép PET. Lỗi retrieval này chưa được sửa.
- Câu 009: thêm bản DOCX Điều 10 đúng ID gold ở hạng 2; bản PDF tương đương đã có ở hạng 1 từ trước.
- Câu 010: thêm bản DOCX Điều 10 ở hạng 3; trước đó bản PDF Điều 10 và Điều 11 đã đủ căn cứ chính.

Các bản PDF có thêm số trang/header Công báo nên chuẩn hóa khoảng trắng chưa gộp được với DOCX. Chúng chiếm thêm chỗ trong top k. Mức tăng exact-ID chủ yếu phản ánh lấy thêm bản tương đương, không phải tìm thêm kiến thức cần trả lời.

Chưa thấy mất căn cứ chính trên 10 câu này. Đây là đối chiếu của trợ lý trên bộ seed nhỏ có gợi ý tên điều/văn bản, không phải nhãn người dùng hoặc bằng chứng tổng quát cho câu hỏi thực tế. Chưa chạy generation sau sửa nên không kết luận tỷ lệ câu trả lời Đạt tăng.

## Quyết định và bước học tiếp

Giữ sửa lỗi vì 5 test kiểm soát xác nhận hành vi đã thống nhất: không bỏ đoạn bổ sung chỉ vì cùng điều. Toàn suite đã đạt 26 test trước lượt benchmark này. Tách kết luận đó khỏi kết luận chất lượng retrieval thực tế.

Bước kế tiếp theo Level 1, Step 3 của blog: đưa các test vào nhịp chạy lặp lại và lưu kết quả gắn phiên bản. Goal là phát hiện hồi quy khi thay đổi tiếp theo; chưa cần chuyển sang LLM judge. Lượt benchmark này đã lưu dữ liệu/config nhưng chưa tự ghi hash code retriever tại thời điểm chạy, nên khả năng truy nguyên phiên bản còn thiếu.
