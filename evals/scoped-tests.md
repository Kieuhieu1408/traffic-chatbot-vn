# Level 1 — Step 1: Write Scoped Tests

Trạng thái hiện tại: đã sửa bộ lọc trùng; 5 scoped tests pass, toàn bộ 26 tests pass. Phần tái hiện lỗi bên dưới ghi lại kết quả trước khi sửa.

## Tính năng đầu tiên: tìm nguồn tài liệu

**Goal:** xác định các hành vi nhỏ có thể kiểm tra, để khi test trượt biết điều gì bị vi phạm. Không lấy số lượng nguồn trả về làm bằng chứng nguồn đó trả lời đúng câu hỏi.

Phạm vi: `VectorRetriever.search(query, k, min_score)` trong `rag_traffic/retriever.py`. Đầu ra là danh sách nguồn có rank, score, ID, nội dung. Chưa bao gồm generation hoặc cách API xác thực đầu vào.

## Bản đồ tình huống ban đầu

| Tình huống | Kỳ vọng cần kiểm tra | Assertion dự kiến | Goal | Giới hạn |
|---|---|---|---|---|
| Query rỗng hoặc chỉ khoảng trắng | Không truy xuất | `results == []`, không gọi encoder/index | Không thực hiện tìm kiếm vô nghĩa | Hành vi tại hàm; API có quy tắc đầu vào riêng |
| Không ứng viên nào vượt ngưỡng | Danh sách rỗng | `results == []` | Thể hiện đúng kết quả lọc, không tự thêm nguồn để đủ k | Không chứng minh corpus thiếu căn cứ |
| Có một ứng viên đủ ngưỡng | Trả đúng ứng viên đó | ID kết quả bằng ID đã chuẩn bị | Kiểm tra logic chọn nguồn không bỏ sai đối tượng | Dùng ứng viên kiểm soát, chưa đo chất lượng embedding |
| Có nhiều ứng viên đủ ngưỡng | Danh sách tuân theo giới hạn sản phẩm | `len(results) <= k`; nếu chỉ còn 2 ứng viên hợp lệ thì trả đúng 2 ID đó | Làm rõ k là hạn mức hay cam kết số lượng | Đủ số lượng không đồng nghĩa đủ căn cứ |
| Hai bản PDF/DOCX chứa cùng căn cứ | Tránh lặp thông tin không cần thiết | Cần định nghĩa tương đương trước khi chọn assertion | Dành chỗ cho bằng chứng khác | Cùng tên điều chưa chắc cùng nội dung |
| Một điều chia nhiều chunk, mỗi chunk có ý khác nhau | Không đánh đồng phần bổ sung với bản trùng | Giữ cả A và B nếu nội dung bổ sung, đều qua ngưỡng và k đủ chỗ | Tránh loại mất điều kiện quan trọng | Code hiện loại trùng theo văn bản + điều; không mặc định đó là yêu cầu đúng |

Các fixture và đầu vào cụ thể sẽ được tạo ở Step 2. Không yêu cầu model sinh câu trả lời cho các phép kiểm tra logic này.

## Assertion dùng chung đã thống nhất

Người dùng đã đồng ý ba quy tắc về tính toàn vẹn của kết quả:

| Quy tắc | Goal | Assertion dự kiến |
|---|---|---|
| Mọi chunk ID trả về tồn tại trong dữ liệu đã nạp | Không trả nguồn không tồn tại | Tập ID kết quả là tập con của tập ID đã nạp |
| Nội dung và metadata khớp chunk được chọn | Không gắn nội dung vào sai văn bản/điều | So sánh content, document_id, article, source_file với chunk theo ID |
| Rank liên tục từ 1 đến số kết quả | Trích dẫn có đích rõ ràng, không thiếu hoặc lặp thứ hạng | Danh sách rank bằng `list(range(1, len(results) + 1))` |

Các quy tắc này bảo vệ tính toàn vẹn, chưa chứng minh nguồn liên quan đúng câu hỏi. Quy tắc về số lượng tối đa và ngưỡng score nằm trong các quyết định bên dưới.

Đã gắn assertion toàn vẹn vào các ca có kết quả trong `tests/test_retriever.py`.

## Đối chiếu nền tảng hiện có

- `tests/test_indexing.py`: từ chối ID trùng khi nạp chunks; bảo vệ dữ liệu đầu vào, chưa kiểm tra hành vi search.
- `tests/test_generation.py`: nguồn trong fallback và hành vi gọi API giả lập; không chứng minh retrieval lấy nguồn đúng.
- Chưa có `tests/test_retriever.py` trong repo ở thời điểm mở bước này.
- Runner seed chạy model embedding và index thật: hữu ích để đánh giá tìm nguồn, khác test logic với ứng viên kiểm soát.

## Quyết định đã thống nhất: k là giới hạn tối đa

Người dùng chọn trả 2 đoạn khi k=6 nhưng chỉ có 2 đoạn qua bộ lọc. Không thêm đoạn dưới min_score để đủ k.

**Goal:** giữ đúng điều kiện chọn nguồn khi số ứng viên ít; không ưu tiên lấp đầy danh sách hơn chất lượng lọc.

Assertion dùng chung, với k hợp lệ (k ≥ 1):

```python
assert len(results) <= k
assert all(r.score >= min_score for r in results)
```

Assertion riêng cho tình huống có đúng hai ứng viên hợp lệ, khác nhau theo quy tắc loại trùng:

```python
assert len(results) == 2
assert {r.chunk_id for r in results} == expected_ids
```

Đủ điều kiện qua bộ lọc không đồng nghĩa đủ căn cứ trả lời. Các assertion trên bảo vệ logic chọn nguồn, chưa đánh giá mức liên quan ngữ nghĩa.

Step 2 đã có fixture kiểm soát cho tình huống này.

## Quyết định đã thống nhất: không có ứng viên đạt ngưỡng

Người dùng chọn trả danh sách rỗng `[]` nếu không còn ứng viên nào qua ngưỡng. Không trả đoạn có score cao nhất chỉ để luôn có kết quả.

**Goal:** biểu diễn trung thực việc không có ứng viên đạt điều kiện lọc, để tầng sau xử lý thiếu bằng chứng phù hợp.

```python
assert results == []
```

Giới hạn: kết quả rỗng không chứng minh corpus không có căn cứ. Căn cứ có thể bị bỏ sót khi truy xuất hoặc có điểm dưới ngưỡng. Cách thông báo cho người dùng thuộc tầng generation.

## Tình huống tiếp theo: nguồn trùng và phần bổ sung

Hai file PDF/DOCX có cùng nội dung căn cứ khác với hai chunk cùng một điều nhưng chứa các khoản khác nhau. Cần xác định nội dung nào có thể loại mà không mất bằng chứng trước khi viết assertion chống trùng.

**Goal:** giảm nguồn lặp mà không loại mất điều kiện/ngoại lệ cần để trả lời.

Người dùng đã đồng ý: không loại B chỉ vì cùng điều với A nếu hai đoạn chứa thông tin bổ sung. Ví dụ A chứa bảng khoảng cách khi khô ráo, B chứa điều kiện khi trời mưa.

Với ca kiểm soát có A và B đều qua ngưỡng, đủ chỗ trong k và không có ứng viên cạnh tranh làm chúng rơi khỏi giới hạn:

```python
assert {"chunk_A", "chunk_B"} <= {r.chunk_id for r in results}
```

Code hiện loại trùng theo văn bản + điều, nên có nguy cơ vi phạm kỳ vọng. Step 2 đã tái hiện: kết quả chỉ chứa A, mất B. Chưa sửa code.

Hai bản có nội dung căn cứ giống nhau có thể giữ một. Tiêu chí triển khai để nhận diện nội dung tương đương cần xác định riêng; không mặc định cùng văn bản/điều là đủ.

## Step 2 — Ba test cases đã tạo

| Ca | Dữ liệu kiểm soát | Kết quả |
|---|---|---|
| Chỉ hai nguồn qua ngưỡng | A=0,90; B=0,80; C=0,40; ngưỡng=0,55; k=6; ba điều khác nhau | Pass: trả A, B |
| Không nguồn nào qua ngưỡng | A=0,50; B=0,40; ngưỡng=0,55 | Pass: trả [] |
| Hai đoạn bổ sung cùng điều | A=0,90; B=0,80; cùng Điều 11; nội dung khác nhau; k=6 | Lỗi đã tái hiện: chỉ trả A |

**Goal:** cố định dữ liệu đầu vào của bộ lọc để kiểm tra hành vi lựa chọn, không phụ thuộc model embedding hoặc corpus thật.

Hàm search thật được giữ nguyên; chỉ thay encoder và FAISS bằng đối tượng giả trả dữ liệu xác định. Fixture không cần hiểu câu hỏi; nó chỉ cung cấp ứng viên và score để cô lập logic đang kiểm tra.

Test lỗi đã biết dùng `xfail(strict=True)` để ghi rõ còn thiếu hành vi và không làm các test khác bị lẫn. `xfailed` không phải pass. Khi sửa lỗi, phải bỏ dấu này; strict khiến test báo lỗi nếu bất ngờ pass mà chưa cập nhật trạng thái.

```bash
# Xem hai ca pass và một lỗi đã biết
.venv/bin/python -m pytest tests/test_retriever.py -rx

# Bỏ qua dấu xfail để thấy trực tiếp lỗi assertion của B
.venv/bin/python -m pytest tests/test_retriever.py --runxfail
```

Đây mới là ba ca logic cho các quyết định đã chốt, không phải hoàn thành mọi phần của Step 2 hoặc đo chất lượng RAG thực tế.

## Vòng sửa lỗi đầu tiên — đã hoàn thành

- Trước sửa: chạy với `--runxfail` cho kết quả 4 pass, 1 fail (mất đoạn B bổ sung).
- Thay đổi: khóa loại trùng là document_id và nội dung chuẩn hóa khoảng trắng. Không loại đoạn chỉ vì cùng điều; không gộp nội dung giống nhau thuộc hai văn bản khác nhau.
- Ca bảo vệ bổ sung: PDF/DOCX chỉ khác khoảng trắng vẫn giữ một bản; bản có điểm cao hơn được giữ và còn chỗ cho nguồn khác. Nội dung giống nhau ở hai văn bản khác nhau vẫn được giữ.
- Sau sửa: 5 scoped tests pass; toàn bộ suite 26 pass. Đã bỏ dấu xfail.

**Goal đạt được:** giữ các đoạn bổ sung mà không bỏ khả năng loại bản sao giống nội dung sau chuẩn hóa khoảng trắng.

**Giới hạn:** chưa loại được mọi bản tương đương về nghĩa hoặc bản OCR khác chữ. Các đoạn có phần chồng lấn vẫn có thể cùng xuất hiện và chiếm chỗ trong top k. Đã chạy lại 10 câu thật: exact-ID tăng nhưng đủ căn cứ chính vẫn 9/10; chưa kết luận chất lượng RAG tổng thể tăng. Xem [đối chiếu trước/sau](runs/dedup-before-after.md). Các trace và nhãn cũ vẫn thuộc phiên bản retrieval trước thay đổi.

Lệnh hiện tại: `.venv/bin/python -m pytest tests/test_retriever.py`.
