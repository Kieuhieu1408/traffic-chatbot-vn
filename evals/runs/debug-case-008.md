# Debug câu 008: đối tượng được cấp IDP

## 1. Xác nhận căn cứ tồn tại

Chunk `f0477521c68def1a31f8fdd6`, Điều 6, Thông tư 29/2015/TT-BGTVT có trong index và đã được đối chiếu DOCX nguồn khi tạo bộ ca. Đây không phải trường hợp thiếu corpus.

## 2. Xem thứ hạng trước lọc

Mã chẩn đoán dùng cùng model, query prefix, chuẩn hóa vector và FAISS index như VectorRetriever, nhưng yêu cầu toàn bộ thứ hạng để tìm vị trí gold.

Với câu hỏi nguyên bản, chunk đúng đứng thứ **55**, score **0,88328**. Mặc định k=6 nên chỉ lấy 24 ứng viên (4 × k). Chunk đúng không vào tập ứng viên; điểm của nó cao hơn min_score=0,55. Hạ ngưỡng không giải quyết nút thắt này.

Các kết quả đầu là Điều 10 (sử dụng IDP), Điều 11 (IDP nước ngoài tại Việt Nam) và văn bản sửa đổi thủ tục. Chúng gần chủ đề nhưng không trả lời đủ điều kiện cấp IDP tại Điều 6. Đây là vấn đề xếp hạng cho ca này; chưa đủ bằng chứng quy kết nguyên nhân sâu hơn cho model, dữ liệu hay cách biểu diễn truy vấn.

## 3. Thử một thay đổi và đo lại

Giữ nguyên 10 câu, model, corpus và min_score; chỉ đặt biến môi trường RAG_TOP_K=20 cho tiến trình thử nghiệm:

```bash
HF_HUB_OFFLINE=1 RAG_TOP_K=20 .venv/bin/python -m evals.run_seed_retrieval
```

Lúc này FAISS lấy tối đa 80 ứng viên trước lọc, nhưng kết quả cuối vẫn không chứa gold của câu 008. Tăng kích thước tập ứng viên chưa bảo đảm đoạn đúng nằm trong danh sách cuối được giới hạn bởi k.

| Chỉ số đối chiếu gold ID chính xác | k=6 | k=20 |
|---|---:|---:|
| Ca đủ tất cả gold ID | 6/10 | 6/10 |
| Recall gold trung bình | 0,65 | 0,65 |
| MRR gold | 0,575 | 0,575 |
| Câu 008 tìm đúng gold | Không | Không |

Chỉ số này chưa chấp nhận các bản nguồn tương đương; xem bản baseline để biết phân tích nội dung. Không suy ra chất lượng generation vì chưa chạy LLM. Không thay đổi cấu hình mặc định của sản phẩm.

## 4. Điều học được và hướng tiếp theo

- Xác nhận lỗi ở khâu retrieval trước khi sửa prompt sinh câu trả lời.
- Đừng mặc định score cao nghĩa là đoạn trả lời đúng câu hỏi.
- Một lần tăng k không cải thiện chỉ số vẫn có ích: loại bỏ một cách sửa chưa hiệu quả.
- Câu này nêu rõ cả số văn bản và Điều 6. Thử nghiệm tiếp theo hợp lý là tận dụng tham chiếu chính xác để tìm theo metadata, kết hợp với tìm ngữ nghĩa cho câu không có tham chiếu. Cần thiết kế sao cho không nhầm điều được trích trong văn bản sửa đổi với điều gốc.
- Khi thử cách đó, phải thêm câu không nêu văn bản/điều để tránh chỉ tối ưu cho bộ 10 câu có gợi ý nguồn rất rõ. Chưa triển khai thay đổi retrieval này.

Trace baseline: `20260907T142623622128Z/retrieval.json`.
Trace k=20: `20260907T142918722370Z/retrieval.json`.
