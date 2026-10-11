# 10 câu hỏi eval đầu tiên từ corpus

Bộ ca kiểm tra khả năng đọc và trả lời theo **bản văn bản cụ thể có trong corpus**, không xác nhận quy định hiện hành. Đáp án do trợ lý soạn và đối chiếu đoạn nguồn, **chờ bạn duyệt**, chưa phải ground truth được chuyên gia xác nhận. Chưa chạy retrieval hoặc generation.

- Dữ liệu máy đọc: [corpus-seed-10.jsonl](corpus-seed-10.jsonl).
- Phiên bản corpus: [manifest](corpus-seed-10.manifest.json).
- Chọn 6 ca về tốc độ/khoảng cách và 4 ca về IDP; gồm đọc bảng, biên số, điều kiện, phân biệt đối tượng và tổng hợp hai điều. Đây là bộ khởi đầu hẹp, không đại diện toàn bộ corpus.
- Các câu có tên văn bản giúp cố định phạm vi và dễ tìm nguồn hơn câu hỏi tự nhiên; sau khi duyệt, nên thêm biến thể không nêu tên văn bản với phạm vi đánh giá được quy định rõ.
- `must_include` chấm theo ý nghĩa, không bắt khớp từng chữ. Câu trả lời phải có trích dẫn hỗ trợ các ý chính và không tự khẳng định hiệu lực hiện tại.
- Mỗi mục `gold_evidence` là căn cứ cần cho ca. Bản PDF/DOCX khác hỗ trợ đầy đủ cùng ý có thể được chấp nhận sau khi đối chiếu. Không dùng số ID liệt kê ở đây như danh sách đầy đủ mọi chunk liên quan để tính Recall một cách máy móc.

## corpus_seed_001 — definition

**Câu hỏi:** Theo bản Thông tư 31/2019/TT-BGTVT trong corpus, đường có hai chiều đi và về chỉ phân chia bằng vạch sơn có được coi là đường đôi không?

**Đáp án kỳ vọng:** Không. Đường đôi phải có chiều đi và chiều về được phân biệt bằng dải phân cách giữa; phân biệt bằng vạch sơn thì không phải đường đôi.

**Ý bắt buộc:**

- Không coi đường chỉ phân chia bằng vạch sơn là đường đôi
- Nêu tiêu chí dải phân cách giữa

**Lỗi cần tránh:**

- Đồng nhất vạch sơn với dải phân cách giữa

**Căn cứ đã đọc:**

- 31/2019/TT-BGTVT, Điều 3. Giải thích từ ngữ; tệp `TT.31.2019.TT.BGTVT.docx`; chunk `00d10ef85c589909593d64cf`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 3. Giải thích từ ngữ
Trong Thông tư này, các từ ngữ dưới đây được hiểu như sau:
1. Đường bộ trong khu đông dân cư là đoạn đường bộ nằm trong khu vực nội thành phố, nội thị xã, nội thị trấn (gọi chung là nội đô thị) và những đoạn đường có đông dân cư sinh sống sát dọc theo đường, có các hoạt động ảnh hưởng đến an toàn giao thông; được xác định bằng biển báo hiệu là đường qua khu đông dân cư.
2. Xe cơ giới gồm xe ô tô; máy kéo; rơ moóc hoặc sơ mi rơ moóc được kéo bởi xe ô tô, máy kéo; xe mô tô hai bánh; xe mô tô ba bánh; xe gắn máy (kể cả xe máy điện) và các loại xe tương tự.
3. Ô tô chuyên dùng là ô tô có kết cấu và trang bị để thực hiện một chức năng công dụng đặc biệt, bao gồm: ô tô quét đường, ô tô tưới nước; ô tô hút chất thải, ô tô ép rác; ô tô trộn vữa; ô tô trộn bê tông; ô tô bơm bê tông; ô tô cần cẩu; ô tô thang; ô tô khoan; ô tô cứu hộ giao thông; ô tô truyền hình lưu động, ô tô đo sóng truyền hình lưu động, ô tô kiểm tra và bảo dưỡng cầu, ô tô kiểm tra cáp điện ngầm, ô tô chụp X-quang, ô tô phẫu thuật lưu động và các loại ô tô tương tự.
4. Xe máy chuyên dùng gồm xe máy thi công, xe máy nông nghiệp, lâm nghiệp và các loại xe đặc chủng khác sử dụng vào mục đích quốc phòng, an ninh có tham gia giao thông đường bộ.
5. Dải phân cách giữa là bộ phận của đường mà xe không chạy trên đó, được dùng để phân chia mặt đường thành hai phần xe chạy ngược chiều riêng biệt (các dạng chủ yếu: bó vỉa, dải phân cách kết cấu bê tông, dải phân cách kết cấu thép, hộ lan tôn sóng hoặc dải đất dự trữ).
6. Đường đôi là đường có chiều đi và chiều về được phân biệt bằng dải phân cách giữa (trường hợp phân biệt bằng vạch sơn thì không phải đường đôi).
7. Đường một chiều là đường chỉ cho đi một chiều.
8.
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_002 — table_lookup

**Câu hỏi:** Theo bảng tại Điều 6 của bản Thông tư 31/2019/TT-BGTVT trong corpus, ô tô con đi trong khu vực đông dân cư trên đường hai chiều, không phải cao tốc và không có biển hạn chế tốc độ riêng, có tốc độ tối đa bao nhiêu?

**Đáp án kỳ vọng:** Tốc độ tối đa theo bảng là 50 km/h trong các điều kiện đã nêu.

**Ý bắt buộc:**

- 50 km/h
- Áp dụng đúng đường hai chiều trong khu vực đông dân cư

**Lỗi cần tránh:**

- Lấy 60 km/h của cột đường đôi
- Áp dụng kết quả cho đường cao tốc

**Căn cứ đã đọc:**

- 31/2019/TT-BGTVT, Điều 6. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông trong khu vực đông dân cư (trừ đường cao tốc); tệp `TT.31.2019.TT.BGTVT.docx`; chunk `ef44bfa6d2c11cba430ba2d4`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 6. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông trong khu vực đông dân cư (trừ đường cao tốc)
Loại xe cơ giới đường bộ | Tốc độ tối đa (km/h) | Tốc độ tối đa (km/h)
Loại xe cơ giới đường bộ | Đường đôi; đường một chiều có từ hai làn xe cơ giới trở lên | Đường hai chiều; đường một chiều có một làn xe cơ giới
Các phương tiện xe cơ giới, trừ các xe được quy định tại Điều 8 Thông tư này. | 60 | 50
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_003 — vehicle_distinction

**Câu hỏi:** Theo bảng tại Điều 7 của bản Thông tư 31/2019/TT-BGTVT trong corpus, xe mô tô đi ngoài khu vực đông dân cư trên đường đôi, không phải cao tốc và không có biển hạn chế tốc độ riêng, có tốc độ tối đa bao nhiêu?

**Đáp án kỳ vọng:** Tốc độ tối đa theo bảng là 70 km/h đối với xe mô tô trong các điều kiện đã nêu.

**Ý bắt buộc:**

- 70 km/h
- Đúng hàng xe mô tô và cột đường đôi

**Lỗi cần tránh:**

- Nhầm xe mô tô với xe gắn máy để trả 40 km/h
- Lấy mức 90 km/h của ô tô con

**Căn cứ đã đọc:**

- 31/2019/TT-BGTVT, Điều 7. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông ngoài khu vực đông dân cư (trừ đường cao tốc); tệp `TT.31.2019.TT.BGTVT.docx`; chunk `4749485a68eb10b081da85ef`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 7. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông ngoài khu vực đông dân cư (trừ đường cao tốc)
Loại xe cơ giới đường bộ | Tốc độ tối đa (km/h) | Tốc độ tối đa (km/h)
Loại xe cơ giới đường bộ | Đường đôi; đường một chiều có từ hai làn xe cơ giới trở lên | Đường hai chiều; đường một chiều có một làn xe cơ giới
Xe ô tô con, xe ô tô chở người đến 30 chỗ (trừ xe buýt); ô tô tải có trọng tải nhỏ hơn hoặc bằng 3,5 tấn. | 90 | 80
Xe ô tô chở người trên 30 chỗ (trừ xe buýt); ô tô tải có trọng tải trên 3,5 tấn (trừ ô tô xi téc). | 80 | 70
Ô tô buýt; ô tô đầu kéo kéo sơ mi rơ moóc; xe mô tô; ô tô chuyên dùng (trừ ô tô trộn vữa, ô tô trộn bê tông). | 70 | 60
Ô tô kéo rơ moóc; ô tô kéo xe khác; ô tô trộn vữa, ô tô trộn bê tông, ô tô xi téc. | 60 | 50
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_004 — exception

**Câu hỏi:** Theo Điều 8 của bản Thông tư 31/2019/TT-BGTVT trong corpus, tốc độ tối đa của xe gắn máy, kể cả xe máy điện, trên đường bộ không phải cao tốc là bao nhiêu?

**Đáp án kỳ vọng:** Đối với xe gắn máy, kể cả xe máy điện, tốc độ tối đa được nêu là không quá 40 km/h; Điều 8 loại trừ đường cao tốc.

**Ý bắt buộc:**

- Không quá 40 km/h
- Phạm vi xe gắn máy kể cả xe máy điện, trừ đường cao tốc

**Lỗi cần tránh:**

- Suy rộng mức này cho mọi xe mô tô
- Suy ra xe gắn máy được phép đi cao tốc

**Căn cứ đã đọc:**

- 31/2019/TT-BGTVT, Điều 8. Tốc độ tối đa cho phép đối với xe máy chuyên dùng, xe gắn máy (kể cả xe máy điện) và các loại xe tương tự trên đường bộ (trừ đường cao tốc); tệp `TT.31.2019.TT.BGTVT.docx`; chunk `d6268f059648c95245c4b14f`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 8. Tốc độ tối đa cho phép đối với xe máy chuyên dùng, xe gắn máy (kể cả xe máy điện) và các loại xe tương tự trên đường bộ (trừ đường cao tốc)
Đối với xe máy chuyên dùng, xe gắn máy (kể cả xe máy điện) và các loại xe tương tự khi tham gia giao thông tốc độ tối đa không quá 40 km/h.
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_005 — numeric_boundary

**Câu hỏi:** Theo Điều 11 của bản Thông tư 31/2019/TT-BGTVT trong corpus, khi mặt đường khô ráo và không có biển cự ly tối thiểu riêng, xe chạy đúng 60 km/h và đúng 80 km/h cần giữ khoảng cách tối thiểu với xe trước lần lượt bao nhiêu?

**Đáp án kỳ vọng:** Theo bảng trong điều kiện mặt đường khô ráo: đúng 60 km/h là 35 m; đúng 80 km/h thuộc khoảng 60 < V ≤ 80 nên là 55 m.

**Ý bắt buộc:**

- 60 km/h: 35 m
- 80 km/h: 55 m
- Giữ điều kiện mặt đường khô ráo

**Lỗi cần tránh:**

- Xếp 80 km/h vào khoảng 80 < V ≤ 100 rồi trả 70 m
- Áp dụng bảng khô ráo nguyên trạng cho thời tiết xấu

**Căn cứ đã đọc:**

- 31/2019/TT-BGTVT, Điều 11. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường; tệp `TT.31.2019.TT.BGTVT.docx`; chunk `d9a189322b5af7963da4b1d0`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 11. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường
1. Khi điều khiển xe tham gia giao thông trên đường bộ, người lái xe, người điều khiển xe máy chuyên dùng phải giữ một khoảng cách an toàn đối với xe chạy liền trước xe của mình; ở nơi có biển báo "Cự ly tối thiểu giữa hai xe" phải giữ khoảng cách không nhỏ hơn trị số ghi trên biển báo.
2. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường
a) Trong điều kiện mặt đường khô ráo, khoảng cách an toàn ứng với mỗi tốc độ được quy định như sau:
Tốc độ lưu hành (km/h) | Khoảng cách an toàn tối thiểu (m)
V= 60 | 35
60 < V ≤80 | 55
80 < V ≤ 100 | 70
100 < V ≤ 120 | 100
Khi điều khiển xe chạy với tốc độ dưới 60 km/h, người lái xe phải chủ động giữ khoảng cách an toàn phù hợp với xe chạy liền trước xe của mình; khoảng cách này tùy thuộc vào mật độ phương tiện, tình hình giao thông thực tế để đảm bảo an toàn giao thông.
b) Khi trời mưa, có sương mù, mặt đường trơn trượt, đường có địa hình quanh co, đèo dốc, tầm nhìn hạn chế, người lái xe phải điều chỉnh khoảng cách an toàn thích hợp lớn hơn trị số ghi trên biển báo hoặc trị số được quy định tại điểm a Khoản này.
Chương III
TỔ CHỨC THỰC HIỆN
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_006 — conditional_reasoning

**Câu hỏi:** Theo Điều 11 của bản Thông tư 31/2019/TT-BGTVT trong corpus, khi trời mưa hoặc mặt đường trơn trượt, có thể giữ nguyên khoảng cách tối thiểu trong bảng dành cho mặt đường khô ráo không?

**Đáp án kỳ vọng:** Không. Người lái xe phải điều chỉnh khoảng cách an toàn thích hợp lớn hơn trị số ghi trên biển báo hoặc trị số trong bảng tại điểm a khoản 2. Điều này không nêu một hệ số tăng cố định.

**Ý bắt buộc:**

- Điều chỉnh khoảng cách thích hợp lớn hơn trị số trên biển hoặc trong bảng
- Không tự đặt số mét hay hệ số tăng cố định

**Lỗi cần tránh:**

- Khẳng định chỉ cần giữ đúng mức trong bảng khô ráo
- Bịa quy tắc tăng gấp đôi

**Căn cứ đã đọc:**

- 31/2019/TT-BGTVT, Điều 11. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường; tệp `TT.31.2019.TT.BGTVT.docx`; chunk `d9a189322b5af7963da4b1d0`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 11. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường
1. Khi điều khiển xe tham gia giao thông trên đường bộ, người lái xe, người điều khiển xe máy chuyên dùng phải giữ một khoảng cách an toàn đối với xe chạy liền trước xe của mình; ở nơi có biển báo "Cự ly tối thiểu giữa hai xe" phải giữ khoảng cách không nhỏ hơn trị số ghi trên biển báo.
2. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường
a) Trong điều kiện mặt đường khô ráo, khoảng cách an toàn ứng với mỗi tốc độ được quy định như sau:
Tốc độ lưu hành (km/h) | Khoảng cách an toàn tối thiểu (m)
V= 60 | 35
60 < V ≤80 | 55
80 < V ≤ 100 | 70
100 < V ≤ 120 | 100
Khi điều khiển xe chạy với tốc độ dưới 60 km/h, người lái xe phải chủ động giữ khoảng cách an toàn phù hợp với xe chạy liền trước xe của mình; khoảng cách này tùy thuộc vào mật độ phương tiện, tình hình giao thông thực tế để đảm bảo an toàn giao thông.
b) Khi trời mưa, có sương mù, mặt đường trơn trượt, đường có địa hình quanh co, đèo dốc, tầm nhìn hạn chế, người lái xe phải điều chỉnh khoảng cách an toàn thích hợp lớn hơn trị số ghi trên biển báo hoặc trị số được quy định tại điểm a Khoản này.
Chương III
TỔ CHỨC THỰC HIỆN
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_007 — duration_constraint

**Câu hỏi:** Theo Điều 5 của bản Thông tư 29/2015/TT-BGTVT trong corpus, giấy phép lái xe quốc tế (IDP) có phải luôn được cấp với thời hạn đủ 3 năm không?

**Đáp án kỳ vọng:** Không. IDP có thời hạn không quá 3 năm kể từ ngày cấp và phải phù hợp với thời hạn còn hiệu lực của giấy phép lái xe quốc gia.

**Ý bắt buộc:**

- Không quá 3 năm kể từ ngày cấp
- Phải phù hợp với thời hạn còn hiệu lực của giấy phép lái xe quốc gia

**Lỗi cần tránh:**

- Khẳng định mọi IDP đều có thời hạn đúng 3 năm
- Bỏ qua ràng buộc thời hạn giấy phép quốc gia

**Căn cứ đã đọc:**

- 29/2015/TT-BGTVT, Điều 5. Thời hạn và hạng xe điều khiển của giấy phép lái xe quốc tế; tệp `29.2015.TT.BGTVT.docx`; chunk `23ccd2cc53b64be089cf8a05`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 5. Thời hạn và hạng xe điều khiển của giấy phép lái xe quốc tế
1. IDP có thời hạn không quá 03 năm, kể từ ngày cấp và phải phù hợp với thời hạn còn hiệu lực của giấy phép lái xe quốc gia.
2. Hạng xe được phép điều khiển của IDP tương ứng với các hạng xe của giấy phép lái xe quốc gia do Việt Nam cấp quy định tại Phụ lục II ban hành kèm theo Thông tư này.
Chương II
CẤP VÀ QUẢN LÝ GIẤY PHÉP LÁI XE QUỐC TẾ
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_008 — eligibility

**Câu hỏi:** Theo Điều 6 của bản Thông tư 29/2015/TT-BGTVT trong corpus, những người nào thuộc đối tượng được cấp IDP và giấy phép lái xe quốc gia của họ phải đáp ứng điều kiện gì?

**Đáp án kỳ vọng:** Người Việt Nam và người nước ngoài có thẻ thường trú tại Việt Nam, có giấy phép lái xe quốc gia do Việt Nam cấp bằng vật liệu PET còn giá trị sử dụng.

**Ý bắt buộc:**

- Người Việt Nam hoặc người nước ngoài có thẻ thường trú tại Việt Nam
- Giấy phép quốc gia do Việt Nam cấp
- Vật liệu PET và còn giá trị sử dụng

**Lỗi cần tránh:**

- Thay điều kiện thường trú bằng bất kỳ người nước ngoài nào
- Chấp nhận mọi giấy phép do nước ngoài cấp

**Căn cứ đã đọc:**

- 29/2015/TT-BGTVT, Điều 6. Đối tượng được cấp giấy phép lái xe quốc tế; tệp `29.2015.TT.BGTVT.docx`; chunk `f0477521c68def1a31f8fdd6`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 6. Đối tượng được cấp giấy phép lái xe quốc tế
Người Việt Nam, người nước ngoài có thẻ thường trú tại Việt Nam, có giấy phép lái xe quốc gia do Việt Nam cấp bằng vật liệu PET. còn giá trị sử dụng.
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_009 — required_documents

**Câu hỏi:** Theo Điều 10 của bản Thông tư 29/2015/TT-BGTVT trong corpus, người có IDP do Việt Nam cấp khi lái xe tại nước tham gia Công ước Viên chỉ mang IDP đã đủ chưa?

**Đáp án kỳ vọng:** Chưa. Khi điều khiển phương tiện cơ giới tại nước tham gia Công ước Viên, phải mang theo cả IDP và giấy phép lái xe quốc gia, đồng thời tuân thủ pháp luật giao thông đường bộ của nước sở tại.

**Ý bắt buộc:**

- Mang cả IDP và giấy phép lái xe quốc gia
- Tuân thủ pháp luật giao thông đường bộ nước sở tại

**Lỗi cần tránh:**

- Khẳng định IDP thay thế hoàn toàn giấy phép quốc gia
- Mở rộng phạm vi thành mọi quốc gia

**Căn cứ đã đọc:**

- 29/2015/TT-BGTVT, Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp; tệp `29.2015.TT.BGTVT.docx`; chunk `e4cc5177cef207e66f4170fe`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp
1. Người có IDP do Việt Nam cấp khi điều khiển phương tiện cơ giới tham gia giao thông trên lãnh thổ nước tham gia Công ước Viên phải mang theo IDP và giấy phép lái xe quốc gia; tuân thủ pháp luật giao thông đường bộ của nước sở tại.
2. IDP do Việt Nam cấp không có giá trị sử dụng trong lãnh thổ Việt Nam.
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.

## corpus_seed_010 — multi_evidence_comparison

**Câu hỏi:** Theo Điều 10 và Điều 11 của bản Thông tư 29/2015/TT-BGTVT trong corpus, việc sử dụng tại Việt Nam khác nhau thế nào giữa IDP do Việt Nam cấp và IDP do nước khác tham gia Công ước Viên cấp?

**Đáp án kỳ vọng:** IDP do Việt Nam cấp không có giá trị sử dụng trong lãnh thổ Việt Nam. Người có IDP do nước khác tham gia Công ước Viên cấp khi lái xe ở Việt Nam phải mang theo IDP và giấy phép lái xe quốc gia được cấp phù hợp với hạng xe điều khiển, đồng thời tuân thủ pháp luật giao thông đường bộ Việt Nam.

**Ý bắt buộc:**

- IDP do Việt Nam cấp không có giá trị sử dụng tại Việt Nam
- Với IDP do nước khác tham gia Công ước Viên cấp: mang IDP và giấy phép quốc gia phù hợp hạng xe
- Tuân thủ pháp luật giao thông đường bộ Việt Nam

**Lỗi cần tránh:**

- Nói mọi IDP đều không có giá trị tại Việt Nam
- Nói mọi IDP đều đủ để lái xe tại Việt Nam mà không cần giấy phép quốc gia

**Căn cứ đã đọc:**

- 29/2015/TT-BGTVT, Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp; tệp `29.2015.TT.BGTVT.docx`; chunk `e4cc5177cef207e66f4170fe`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp
1. Người có IDP do Việt Nam cấp khi điều khiển phương tiện cơ giới tham gia giao thông trên lãnh thổ nước tham gia Công ước Viên phải mang theo IDP và giấy phép lái xe quốc gia; tuân thủ pháp luật giao thông đường bộ của nước sở tại.
2. IDP do Việt Nam cấp không có giá trị sử dụng trong lãnh thổ Việt Nam.
```

</details>

- 29/2015/TT-BGTVT, Điều 11. Sử dụng giấy phép lái xe quốc tế do các nước tham gia Công ước Viên cấp tại Việt Nam; tệp `29.2015.TT.BGTVT.docx`; chunk `2c6f7b9a1210ffd8b30dfb75`.

<details><summary>Đọc nguyên văn chunk</summary>

```text
Điều 11. Sử dụng giấy phép lái xe quốc tế do các nước tham gia Công ước Viên cấp tại Việt Nam
1. Người có IDP do các nước tham gia Công ước Viên cấp khi điều khiển phương tiện giao thông cơ giới đường bộ trên lãnh thổ Việt Nam phải mang theo IDP và giấy phép lái xe quốc gia được cấp phù hợp với hạng xe điều khiển; phải tuân thủ pháp luật giao thông đường bộ của Việt Nam.
2. Người có IDP vi phạm pháp luật về giao thông đường bộ Việt Nam mà bị tước quyền sử dụng IDP có thời hạn thì thời hạn bị tước không quá thời gian người lái xe được phép cư trú tại lãnh thổ Việt Nam.
Chương IV
ĐIỀU KHOẢN THI HÀNH
```

</details>

**Duyệt của bạn:** ☐ Đáp án đúng theo nguồn ☐ Điều kiện đủ ☐ Chấp nhận làm ca eval

**Kết quả chạy:** chưa chạy.
