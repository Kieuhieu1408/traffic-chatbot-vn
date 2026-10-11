# Kết quả chạy GPT-5.4 mini — 10 câu seed

Cả 10 yêu cầu OpenAI thành công, mode `rag`. Cấu hình retrieval: k=6, min_score=0,55. Gọi trực tiếp các hàm retrieval/generation ứng dụng sử dụng, không kiểm thử giao diện trình duyệt.

**Đánh giá sơ bộ của trợ lý, chờ người dùng duyệt:** 9/10 câu đáp ứng ý chính của đáp án kỳ vọng; câu 008 trượt. Đây không phải xác nhận toàn bộ câu chữ hoặc hiệu lực pháp luật. Các nhận xét phụ về corpus/thiếu văn bản cần kiểm tra riêng; model chỉ thấy top 6, không thấy toàn bộ corpus.

Tất cả số trích dẫn dạng [n] đều trỏ tới rank tồn tại. Phép kiểm tra này không chứng minh nguồn hỗ trợ mọi nhận định. Câu 008 minh họa rõ sự khác biệt.

## Lỗi cần ưu tiên: câu 008

- Retrieval không đưa Điều 6 vào context.
- Model thay câu hỏi về đối tượng được cấp bằng nội dung thủ tục ở Điều 8, thiếu điều kiện giấy phép PET và mô tả đúng đối tượng.
- Model nói Điều 6 không xuất hiện trong corpus. Thực tế chỉ thiếu trong context được truy xuất; nguồn gốc đã xác nhận có điều đó.
- Đề xuất: sửa retrieval cho tham chiếu văn bản/điều rõ ràng; bổ sung hướng dẫn phân biệt context và corpus, không dùng điều khác để thay thế khi chưa đủ căn cứ. Chưa áp dụng các thay đổi này.

## Đối chiếu từng câu

### corpus_seed_001

**Câu hỏi:** Theo bản Thông tư 31/2019/TT-BGTVT trong corpus, đường có hai chiều đi và về chỉ phân chia bằng vạch sơn có được coi là đường đôi không?

**Đáp án kỳ vọng:** Không. Đường đôi phải có chiều đi và chiều về được phân biệt bằng dải phân cách giữa; phân biệt bằng vạch sơn thì không phải đường đôi.

**Câu trả lời thực tế:**

Theo nội dung trích dẫn trong Thông tư 31/2019/TT-BGTVT, **không**. Nếu đường có hai chiều đi và về **chỉ phân biệt bằng vạch sơn** thì **không phải đường đôi**; Thông tư nêu rõ trường hợp phân biệt bằng vạch sơn thì không phải đường đôi [1].

Ngoài ra, tài liệu còn phân biệt:
- **Đường đôi** là đường có chiều đi và chiều về được phân biệt bằng **dải phân cách giữa**; nếu chỉ phân biệt bằng vạch sơn thì không phải đường đôi [1].
- **Đường hai chiều** là đường có cả hai chiều đi và về trên cùng một phần đường xe chạy, **không được phân biệt bằng dải phân cách giữa** [1].

Lưu ý: Tôi chỉ dựa trên đoạn tài liệu được cung cấp; nếu cần đối chiếu đầy đủ câu chữ của Điều 3 hoặc xem văn bản sửa đổi liên quan, corpus hiện chưa cung cấp trọn vẹn toàn văn điều khoản [1][2].

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ. Model mô tả giới hạn toàn văn bằng từ corpus thay vì chỉ rõ context được cung cấp; cần diễn đạt chính xác hơn.

**Nguồn được lấy về:**

- [1] 31/2019/TT-BGTVT, Điều 3. Giải thích từ ngữ — `efec83cbecf7f82735737fe5`
- [2] 06/2023/TT-BGTVT, Điều 15. Sửa đổi, bổ sung một số điều của Thông tư số 31/2019/TT- BGTVT ngày 29 tháng 08 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ — `02b05b5ef174227dc7770eb0`
- [3] 50/2015/TT-BGTVT, Điều 65. Tổ chức thực hiện — `1b81611c0570ec87a61fd54d`
- [4] 43/2021/TT-BGTVT, Điều 2. Bãi bỏ khoản 1 Điều 6 Thông tư số 03/2019/TT-BGTVT ngày 11 tháng 01 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về công tác phòng, chống và khắc phục hậu quả thiên tai trong lĩnh vực đường bộ. — `c9cdc69afa7e443110d564f1`
- [5] TT79.signed, Điều 3. Chánh Văn phòng Bộ, Chánh Thanh tra Bộ, các Vụ trưởng, Tổng — `d498321d5206d4745019a8b3`
- [6] 50/2015/TT-BGTVT, Điều 21. Khoảng cách tối thiểu giữa hai điểm đấu nối vào quốc lộ — `8933134f2c74de943a3e3534`

### corpus_seed_002

**Câu hỏi:** Theo bảng tại Điều 6 của bản Thông tư 31/2019/TT-BGTVT trong corpus, ô tô con đi trong khu vực đông dân cư trên đường hai chiều, không phải cao tốc và không có biển hạn chế tốc độ riêng, có tốc độ tối đa bao nhiêu?

**Đáp án kỳ vọng:** Tốc độ tối đa theo bảng là 50 km/h trong các điều kiện đã nêu.

**Câu trả lời thực tế:**

Theo bảng tại Điều 6 của Thông tư 31/2019/TT-BGTVT, **ô tô con** đi trong **khu vực đông dân cư**, trên **đường hai chiều** (hoặc đường một chiều có một làn xe cơ giới), **không phải đường cao tốc**, có tốc độ tối đa là **50 km/h**. [1]

Lưu ý: trong tài liệu cung cấp, Điều 15 của Thông tư 06/2023/TT-BGTVT chỉ sửa một số cụm từ khác, không cho thấy sửa đổi trực tiếp bảng tốc độ tại Điều 6; tuy nhiên tôi không suy đoán thêm về hiệu lực ngoài phạm vi tài liệu đã cho. [2]

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 31/2019/TT-BGTVT, Điều 6. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông trong khu vực đông dân cư (trừ đường cao tốc) — `ef44bfa6d2c11cba430ba2d4`
- [2] 06/2023/TT-BGTVT, Điều 15. Sửa đổi, bổ sung một số điều của Thông tư số 31/2019/TT- BGTVT ngày 29 tháng 08 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ — `02b05b5ef174227dc7770eb0`
- [3] 31/2019/TT-BGTVT, Điều 9. Tốc độ của các loại xe cơ giới, xe máy chuyên dùng trên đường cao tốc — `328b2cc296345d2f0abd91f4`
- [4] 31/2019/TT-BGTVT, Điều 10. Đặt biển báo hạn chế tốc độ — `b51aa0688d37f1c3cc380014`
- [5] 31/2019/TT-BGTVT, Điều 7. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông ngoài khu vực đông dân cư (trừ đường cao tốc) — `4749485a68eb10b081da85ef`
- [6] 43/2021/TT-BGTVT, Điều 2. Bãi bỏ khoản 1 Điều 6 Thông tư số 03/2019/TT-BGTVT ngày 11 tháng 01 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về công tác phòng, chống và khắc phục hậu quả thiên tai trong lĩnh vực đường bộ. — `c9cdc69afa7e443110d564f1`

### corpus_seed_003

**Câu hỏi:** Theo bảng tại Điều 7 của bản Thông tư 31/2019/TT-BGTVT trong corpus, xe mô tô đi ngoài khu vực đông dân cư trên đường đôi, không phải cao tốc và không có biển hạn chế tốc độ riêng, có tốc độ tối đa bao nhiêu?

**Đáp án kỳ vọng:** Tốc độ tối đa theo bảng là 70 km/h đối với xe mô tô trong các điều kiện đã nêu.

**Câu trả lời thực tế:**

Theo bảng tại Điều 7 của Thông tư 31/2019/TT-BGTVT, **xe mô tô đi ngoài khu vực đông dân cư trên đường đôi, không phải cao tốc, và không có biển hạn chế tốc độ riêng** có tốc độ tối đa là **70 km/h**. [4]

Vì tại đoạn đường **không bố trí biển báo hạn chế tốc độ**, người điều khiển phải áp dụng quy định tại Điều 7. [5]

Đây là thông tin tra cứu từ tài liệu cung cấp, không thay thế tư vấn pháp lý chuyên nghiệp.

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 31/2019/TT-BGTVT, Điều 6. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông trong khu vực đông dân cư (trừ đường cao tốc) — `ef44bfa6d2c11cba430ba2d4`
- [2] 06/2023/TT-BGTVT, Điều 15. Sửa đổi, bổ sung một số điều của Thông tư số 31/2019/TT- BGTVT ngày 29 tháng 08 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ — `02b05b5ef174227dc7770eb0`
- [3] 31/2019/TT-BGTVT, Điều 9. Tốc độ của các loại xe cơ giới, xe máy chuyên dùng trên đường cao tốc — `328b2cc296345d2f0abd91f4`
- [4] 31/2019/TT-BGTVT, Điều 7. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông ngoài khu vực đông dân cư (trừ đường cao tốc) — `4749485a68eb10b081da85ef`
- [5] 31/2019/TT-BGTVT, Điều 4. Nguyên tắc chấp hành quy định về tốc độ và khoảng cách khi điều khiển phương tiện trên đường bộ — `f37ec483ecba460eb8825c25`
- [6] 31/2019/TT-BGTVT, Điều 10. Đặt biển báo hạn chế tốc độ — `b51aa0688d37f1c3cc380014`

### corpus_seed_004

**Câu hỏi:** Theo Điều 8 của bản Thông tư 31/2019/TT-BGTVT trong corpus, tốc độ tối đa của xe gắn máy, kể cả xe máy điện, trên đường bộ không phải cao tốc là bao nhiêu?

**Đáp án kỳ vọng:** Đối với xe gắn máy, kể cả xe máy điện, tốc độ tối đa được nêu là không quá 40 km/h; Điều 8 loại trừ đường cao tốc.

**Câu trả lời thực tế:**

Theo Điều 8 của Thông tư 31/2019/TT-BGTVT, đối với **xe máy chuyên dùng, xe gắn máy (kể cả xe máy điện) và các loại xe tương tự** khi tham gia giao thông trên **đường bộ (trừ đường cao tốc)**, **tốc độ tối đa không quá 40 km/h**. [1]

Lưu ý: Tôi chỉ dựa trên các đoạn tài liệu được cung cấp; nếu bạn cần kiểm tra tình trạng sửa đổi/hiệu lực hiện hành của quy định này, corpus hiện chỉ cho thấy Thông tư 31/2019/TT-BGTVT có hiệu lực từ 15/10/2019 và có một thông tư năm 2023 sửa đổi một số nội dung khác, nhưng đoạn trích không nêu sửa đổi Điều 8. [2][5]

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 31/2019/TT-BGTVT, Điều 8. Tốc độ tối đa cho phép đối với xe máy chuyên dùng, xe gắn máy (kể cả xe máy điện) và các loại xe tương tự trên đường bộ (trừ đường cao tốc) — `d6268f059648c95245c4b14f`
- [2] 06/2023/TT-BGTVT, Điều 15. Sửa đổi, bổ sung một số điều của Thông tư số 31/2019/TT- BGTVT ngày 29 tháng 08 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ — `02b05b5ef174227dc7770eb0`
- [3] 31/2019/TT-BGTVT, Điều 9. Tốc độ của các loại xe cơ giới, xe máy chuyên dùng trên đường cao tốc — `328b2cc296345d2f0abd91f4`
- [4] 31/2019/TT-BGTVT, Điều 6. Tốc độ tối đa cho phép xe cơ giới tham gia giao thông trong khu vực đông dân cư (trừ đường cao tốc) — `ef44bfa6d2c11cba430ba2d4`
- [5] 31/2019/TT-BGTVT, Điều 12. Hiệu lực thi hành — `7eab6aab13fc0b00f441c0fc`
- [6] 31/2019/TT-BGTVT, Điều 1. Phạm vi điều chỉnh — `0c30afbb129fc9d4dd99867a`

### corpus_seed_005

**Câu hỏi:** Theo Điều 11 của bản Thông tư 31/2019/TT-BGTVT trong corpus, khi mặt đường khô ráo và không có biển cự ly tối thiểu riêng, xe chạy đúng 60 km/h và đúng 80 km/h cần giữ khoảng cách tối thiểu với xe trước lần lượt bao nhiêu?

**Đáp án kỳ vọng:** Theo bảng trong điều kiện mặt đường khô ráo: đúng 60 km/h là 35 m; đúng 80 km/h thuộc khoảng 60 < V ≤ 80 nên là 55 m.

**Câu trả lời thực tế:**

Theo Điều 11 Thông tư 31/2019/TT-BGTVT, trong điều kiện **mặt đường khô ráo** và **không có biển “Cự ly tối thiểu giữa hai xe”**, xe chạy:

- **60 km/h**: phải giữ khoảng cách an toàn tối thiểu **35 mét** [1].
- **80 km/h**: thuộc khoảng **60 < V ≤ 80**, nên phải giữ khoảng cách an toàn tối thiểu **55 mét** [1].

Lưu ý: Điều 11 còn quy định nếu có biển báo “Cự ly tối thiểu giữa hai xe” thì phải giữ khoảng cách không nhỏ hơn trị số trên biển; và khi điều kiện xấu hơn (mưa, sương mù, trơn trượt, tầm nhìn hạn chế...) thì phải giữ khoảng cách lớn hơn mức ở điểm a [1]. Thông tư 31/2019/TT-BGTVT được nêu là có hiệu lực từ 15/10/2019 [3], nhưng corpus cũng có văn bản sửa đổi năm 2023 chỉ sửa một số điều khác, không thấy sửa Điều 11 trong tài liệu cung cấp [2].

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 31/2019/TT-BGTVT, Điều 11. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường — `d9a189322b5af7963da4b1d0`
- [2] 06/2023/TT-BGTVT, Điều 15. Sửa đổi, bổ sung một số điều của Thông tư số 31/2019/TT- BGTVT ngày 29 tháng 08 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ — `02b05b5ef174227dc7770eb0`
- [3] 31/2019/TT-BGTVT, Điều 12. Hiệu lực thi hành — `7eab6aab13fc0b00f441c0fc`
- [4] 22/2023/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 03/2019/TT-BGTVT ngày 11 tháng 01 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về công tác phòng, chống và khắc phục hậu quả thiên tai trong lĩnh vực đường bộ (sau đây gọi là Thông tư số 03/2019/TT-BGTVT) và Thông tư số 43/2021/TT-BGTVT ngày 31 tháng 12 năm 2021 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều của Thông tư số 03/2019/TT-BGTVT (sau đây gọi là Thông tư số 43/2021/TT-BGTVT) — `f89878fa57c3a1462e8c47af`
- [5] 50/2015/TT-BGTVT, Điều 6. Phạm vi bảo vệ trên không của công trình đường bộ — `1afa62b880678dfd2f7c5105`
- [6] 03/2019/TT-BGTVT, Phần mở đầu — `54776afbac7cea35617ccbb4`

### corpus_seed_006

**Câu hỏi:** Theo Điều 11 của bản Thông tư 31/2019/TT-BGTVT trong corpus, khi trời mưa hoặc mặt đường trơn trượt, có thể giữ nguyên khoảng cách tối thiểu trong bảng dành cho mặt đường khô ráo không?

**Đáp án kỳ vọng:** Không. Người lái xe phải điều chỉnh khoảng cách an toàn thích hợp lớn hơn trị số ghi trên biển báo hoặc trị số trong bảng tại điểm a khoản 2. Điều này không nêu một hệ số tăng cố định.

**Câu trả lời thực tế:**

Không. Theo Điều 11, **khi trời mưa hoặc mặt đường trơn trượt, người lái xe phải điều chỉnh khoảng cách an toàn thích hợp lớn hơn** trị số ghi trên biển báo hoặc trị số quy định tại điểm a khoản 2; vì vậy **không thể giữ nguyên khoảng cách tối thiểu áp dụng cho mặt đường khô ráo** trong bảng. [1]

Cụ thể:
- Bảng tại điểm a khoản 2 chỉ áp dụng **trong điều kiện mặt đường khô ráo**. [1]
- Khi **trời mưa, có sương mù, mặt đường trơn trượt...**, phải giữ khoảng cách **lớn hơn** các trị số đó. [1]

Lưu ý: Tài liệu bạn cung cấp chưa cho thấy có sửa đổi nào đối với riêng quy định này trong các văn bản trích xuất kèm theo. [2][5]

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 31/2019/TT-BGTVT, Điều 11. Khoảng cách an toàn giữa hai xe khi tham gia giao thông trên đường — `d9a189322b5af7963da4b1d0`
- [2] 06/2023/TT-BGTVT, Điều 15. Sửa đổi, bổ sung một số điều của Thông tư số 31/2019/TT- BGTVT ngày 29 tháng 08 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ — `02b05b5ef174227dc7770eb0`
- [3] 43/2021/TT-BGTVT, Điều 2. Bãi bỏ khoản 1 Điều 6 Thông tư số 03/2019/TT-BGTVT ngày 11 tháng 01 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về công tác phòng, chống và khắc phục hậu quả thiên tai trong lĩnh vực đường bộ. — `c9cdc69afa7e443110d564f1`
- [4] 22/2023/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 03/2019/TT-BGTVT ngày 11 tháng 01 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về công tác phòng, chống và khắc phục hậu quả thiên tai trong lĩnh vực đường bộ (sau đây gọi là Thông tư số 03/2019/TT-BGTVT) và Thông tư số 43/2021/TT-BGTVT ngày 31 tháng 12 năm 2021 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều của Thông tư số 03/2019/TT-BGTVT (sau đây gọi là Thông tư số 43/2021/TT-BGTVT) — `f89878fa57c3a1462e8c47af`
- [5] 43/2021/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 03/2019/TT-BGTVT ngày 11 tháng 01 năm 2019 của Bộ trưởng Bộ Giao thông vận tải quy định về công tác phòng, chống và khắc phục hậu quả thiên tai trong lĩnh vực đường bộ — `9da74a7bf18c154dac2270a0`
- [6] 03/2019/TT-BGTVT, Phần mở đầu — `54776afbac7cea35617ccbb4`

### corpus_seed_007

**Câu hỏi:** Theo Điều 5 của bản Thông tư 29/2015/TT-BGTVT trong corpus, giấy phép lái xe quốc tế (IDP) có phải luôn được cấp với thời hạn đủ 3 năm không?

**Đáp án kỳ vọng:** Không. IDP có thời hạn không quá 3 năm kể từ ngày cấp và phải phù hợp với thời hạn còn hiệu lực của giấy phép lái xe quốc gia.

**Câu trả lời thực tế:**

Không. Theo Điều 5 của Thông tư 29/2015/TT-BGTVT, IDP chỉ có thời hạn **không quá 03 năm** kể từ ngày cấp và còn phải **phù hợp với thời hạn còn hiệu lực của giấy phép lái xe quốc gia**. Vì vậy, IDP **không phải lúc nào cũng được cấp đủ 3 năm**; thời hạn thực tế có thể ngắn hơn nếu giấy phép lái xe quốc gia còn hiệu lực ngắn hơn. [1]

Ngoài ra, tài liệu cũng cho biết Thông tư 05/2024/TT-BGTVT có sửa đổi một số điều của Thông tư 29/2015/TT-BGTVT, nhưng trong phần trích xuất được cung cấp, chưa có nội dung sửa trực tiếp Điều 5, nên từ corpus này chỉ xác định chắc được quy định tại Điều 5 nêu trên. [4]

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 29/2015/TT-BGTVT, Điều 5. Thời hạn và hạng xe điều khiển của giấy phép lái xe quốc tế — `23ccd2cc53b64be089cf8a05`
- [2] 29/2015/TT-BGTVT, Điều 8. Thủ tục cấp giấy phép lái xe quốc tế — `e85b959216ecec3d583def89`
- [3] 05/2024/TT-BGTVT, Điều 4. Sửa đổi, bổ sung một số điều của Thông tư số 12/2017/TT-BGTVT ngày 15 tháng 4 năm 2017 của Bộ trưởng Bộ Giao thông vận tải quy định về đào tạo, sát hạch, cấp giấy phép lái xe cơ giới đường bộ (sau đây gọi là Thông tư số 12/2017/TT-BGTVT), Thông tư số 38/2019/TT-BGTVT ngày 08 tháng 10 năm 2019 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều Thông tư số 12/2017/TT-BGTVT ngày 15 tháng 4 năm 2017 của Bộ trưởng Bộ Giao thông vận tải quy định về đào tạo, sát hạch, cấp giấy phép lái xe cơ giới đường bộ (sau đây gọi là Thông tư số 38/2019/TT-BGTVT), Thông tư số 01/2021/TT-BGTVT ngày 27 tháng 01 năm 2021 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế và Thông tư số 12/2017/TT-BGTVT ngày 15 tháng 4 năm 2017 của Bộ trưởng Bộ Giao thông vận tải quy định về đào tạo, sát hạch, cấp giấy phép lái xe cơ giới đường bộ (sau đây gọi là Thông tư số 01/2021/TT-BGTVT), Thông tư số 04/2022/TT-BGTVT ngày 22 tháng 4 năm 2022 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều Thông tư số 12/2017/TT-BGTVT ngày 15 tháng 4 năm 2017 của Bộ trưởng Bộ Giao thông vận tải quy định về đào tạo, sát hạch, cấp giấy phép lái xe cơ giới đường bộ (sau đây gọi là Thông tư số 04/2022/TT-BGTVT), Thông tư số 05/2023/TT-BGTVT ngày 27 tháng 4 năm 2023 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều của các Thông tư liên quan đến lĩnh vực vận tải đường bộ, dịch vụ hỗ trợ vận tải đường bộ, phương tiện và người lái (sau đây gọi là Thông tư số 05/2023/TT-BGTVT) — `f99ae438910b8a9a601db5e3`
- [4] 05/2024/TT-BGTVT, Điều 3. Sửa đổi, bổ sung một số điều của Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế (sau dây gọi là Thông tư số 29/2015/TT-BGTVT), Thông tư số 01/2021/TT-BGTVT ngày 27 tháng 01 năm 2021 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế và Thông tư số 12/2017/TT-BGTVT ngày 15 tháng 4 năm 2017 của Bộ trưởng Bộ Giao thông vận tải quy định về đào tạo, sát hạch, cấp giấy phép lái xe cơ giới đường bộ (sau đây gọi là Thông tư số 01/2021/TT-BGTVT) — `1b54debf612aca306d2832d3`
- [5] Thông tu 05.2024.TTB-GTVT, Điều 3. Sửa đổi, bổ sung một số điều của Thông tư số 29/2015/TT- — `f7a1429f2191261f311dabb9`
- [6] 29/2015/TT-BGTVT, Điều 3. Giải thích từ ngữ — `c77d501e0d3debeae61c0a6c`

### corpus_seed_008

**Câu hỏi:** Theo Điều 6 của bản Thông tư 29/2015/TT-BGTVT trong corpus, những người nào thuộc đối tượng được cấp IDP và giấy phép lái xe quốc gia của họ phải đáp ứng điều kiện gì?

**Đáp án kỳ vọng:** Người Việt Nam và người nước ngoài có thẻ thường trú tại Việt Nam, có giấy phép lái xe quốc gia do Việt Nam cấp bằng vật liệu PET còn giá trị sử dụng.

**Câu trả lời thực tế:**

Theo **Điều 8 của Thông tư 29/2015/TT-BGTVT** trong corpus, **đối tượng được cấp IDP** là **cá nhân nộp đơn đề nghị cấp IDP** theo mẫu quy định. Khi nộp đơn, người đó phải **xuất trình bản chính giấy phép lái xe quốc gia do Việt Nam cấp, hộ chiếu, thẻ thường trú (đối với người nước ngoài) còn giá trị để kiểm tra, đối chiếu**. [4]

Ngoài ra, nếu tài liệu của bạn đang hỏi về **điều kiện đối với giấy phép lái xe quốc gia** để được cấp IDP thì Thông tư quy định:
- **Không cấp IDP** nếu giấy phép lái xe quốc gia **bị tẩy xóa, hư hỏng không còn đủ thông tin cần thiết hoặc có sự khác biệt về nhận dạng**; hoặc
- **Không do cơ quan có thẩm quyền cấp theo quy định**. [4]

Lưu ý: Trong corpus bạn cung cấp, **Điều 6 không xuất hiện**; nội dung liên quan trực tiếp đến điều kiện cấp IDP nằm ở **Điều 8** của Thông tư 29/2015/TT-BGTVT. [4] Đây là tra cứu từ tài liệu cung cấp, không thay thế tư vấn pháp lý chuyên nghiệp.

**Nhận xét:** Trượt: trả lời bằng Điều 8 thay Điều 6; không nêu đủ điều kiện PET/đối tượng; khẳng định sai phạm vi quan sát rằng corpus không có Điều 6.

**Nguồn được lấy về:**

- [1] 29/2015/TT-BGTVT, Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp — `a619cafb6419190e2764107b`
- [2] 29/2015/TT-BGTVT, Điều 11. Sử dụng giấy phép lái xe quốc tế do các nước tham gia Công ước Viên cấp tại Việt Nam — `2c6f7b9a1210ffd8b30dfb75`
- [3] 01/2021/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế như sau: — `6bf208f1914853db6f23b48b`
- [4] 29/2015/TT-BGTVT, Điều 8. Thủ tục cấp giấy phép lái xe quốc tế — `86bd46debdd0fbd7b9b12df1`
- [5] 29/2015/TT-BGTVT, Điều 3. Giải thích từ ngữ — `c77d501e0d3debeae61c0a6c`
- [6] 05/2024/TT-BGTVT, Điều 3. Sửa đổi, bổ sung một số điều của Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế (sau dây gọi là Thông tư số 29/2015/TT-BGTVT), Thông tư số 01/2021/TT-BGTVT ngày 27 tháng 01 năm 2021 của Bộ trưởng Bộ Giao thông vận tải sửa đổi, bổ sung một số điều Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế và Thông tư số 12/2017/TT-BGTVT ngày 15 tháng 4 năm 2017 của Bộ trưởng Bộ Giao thông vận tải quy định về đào tạo, sát hạch, cấp giấy phép lái xe cơ giới đường bộ (sau đây gọi là Thông tư số 01/2021/TT-BGTVT) — `1b54debf612aca306d2832d3`

### corpus_seed_009

**Câu hỏi:** Theo Điều 10 của bản Thông tư 29/2015/TT-BGTVT trong corpus, người có IDP do Việt Nam cấp khi lái xe tại nước tham gia Công ước Viên chỉ mang IDP đã đủ chưa?

**Đáp án kỳ vọng:** Chưa. Khi điều khiển phương tiện cơ giới tại nước tham gia Công ước Viên, phải mang theo cả IDP và giấy phép lái xe quốc gia, đồng thời tuân thủ pháp luật giao thông đường bộ của nước sở tại.

**Câu trả lời thực tế:**

Chưa đủ. Theo Điều 10 Thông tư 29/2015/TT-BGTVT, người có IDP do Việt Nam cấp khi điều khiển phương tiện cơ giới tham gia giao thông trên lãnh thổ nước tham gia Công ước Viên **phải mang theo cả IDP và giấy phép lái xe quốc gia**; đồng thời phải tuân thủ pháp luật giao thông đường bộ của nước sở tại. Vì vậy, **chỉ mang IDP là không đủ**. [1]

Lưu ý: tài liệu bạn cung cấp chỉ cho thấy quy định của Thông tư 29/2015/TT-BGTVT; không có thêm đoạn nào cho thấy Điều 10 đã được sửa đổi trực tiếp. Tôi không suy đoán hiệu lực ngoài corpus. [1][3]

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 29/2015/TT-BGTVT, Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp — `a619cafb6419190e2764107b`
- [2] 29/2015/TT-BGTVT, Điều 11. Sử dụng giấy phép lái xe quốc tế do các nước tham gia Công ước Viên cấp tại Việt Nam — `2c6f7b9a1210ffd8b30dfb75`
- [3] 01/2021/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế như sau: — `6bf208f1914853db6f23b48b`
- [4] 29/2015/TT-BGTVT, Điều 7. Trách nhiệm cấp và quản lý giấy phép lái xe quốc tế — `f68614b9b6ddd8fa975e30e2`
- [5] 29/2015/TT-BGTVT, Điều 8. Thủ tục cấp giấy phép lái xe quốc tế — `86bd46debdd0fbd7b9b12df1`
- [6] 29/2015/TT-BGTVT, Điều 1. Phạm vi điều chỉnh — `d4f0b6cf329c0ce359b99e81`

### corpus_seed_010

**Câu hỏi:** Theo Điều 10 và Điều 11 của bản Thông tư 29/2015/TT-BGTVT trong corpus, việc sử dụng tại Việt Nam khác nhau thế nào giữa IDP do Việt Nam cấp và IDP do nước khác tham gia Công ước Viên cấp?

**Đáp án kỳ vọng:** IDP do Việt Nam cấp không có giá trị sử dụng trong lãnh thổ Việt Nam. Người có IDP do nước khác tham gia Công ước Viên cấp khi lái xe ở Việt Nam phải mang theo IDP và giấy phép lái xe quốc gia được cấp phù hợp với hạng xe điều khiển, đồng thời tuân thủ pháp luật giao thông đường bộ Việt Nam.

**Câu trả lời thực tế:**

Theo Điều 10 và Điều 11 của Thông tư 29/2015/TT-BGTVT, việc sử dụng IDP tại Việt Nam khác nhau như sau:

- **IDP do Việt Nam cấp**: Người có IDP này **không được sử dụng trong lãnh thổ Việt Nam**; Thông tư chỉ quy định người mang IDP do Việt Nam cấp khi đi ở **nước tham gia Công ước Viên** thì phải mang theo cả IDP và giấy phép lái xe quốc gia, và tuân thủ pháp luật nước sở tại. [1]

- **IDP do nước khác tham gia Công ước Viên cấp**: Người có IDP này **được sử dụng tại Việt Nam** khi điều khiển phương tiện giao thông cơ giới đường bộ trên lãnh thổ Việt Nam, nhưng phải mang theo **cả IDP và giấy phép lái xe quốc gia phù hợp với hạng xe điều khiển**, đồng thời phải tuân thủ pháp luật giao thông đường bộ của Việt Nam. [2]

- Ngoài ra, nếu người có IDP do nước khác cấp vi phạm pháp luật giao thông đường bộ Việt Nam và bị tước quyền sử dụng IDP có thời hạn, thì thời hạn tước **không quá thời gian được phép cư trú tại Việt Nam**. [2]

Tóm lại: **IDP do Việt Nam cấp không có giá trị sử dụng trong Việt Nam, còn IDP do nước khác tham gia Công ước Viên cấp thì có thể dùng tại Việt Nam, kèm giấy phép lái xe quốc gia phù hợp.** [1][2]

Lưu ý: Tôi chỉ dựa trên đúng các đoạn tài liệu bạn cung cấp; corpus không cho biết thêm về hiệu lực hiện hành của các quy định này.

**Nhận xét:** Các ý chính phù hợp đáp án kỳ vọng. Không đánh đồng kết quả này với kiểm chứng mọi nhận xét phụ.

**Nguồn được lấy về:**

- [1] 29/2015/TT-BGTVT, Điều 10. Sử dụng giấy phép lái xe quốc tế do Việt Nam cấp — `a619cafb6419190e2764107b`
- [2] 29/2015/TT-BGTVT, Điều 11. Sử dụng giấy phép lái xe quốc tế do các nước tham gia Công ước Viên cấp tại Việt Nam — `2c6f7b9a1210ffd8b30dfb75`
- [3] 01/2021/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều Thông tư số 29/2015/TT-BGTVT ngày 06 tháng 7 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về cấp, sử dụng giấy phép lái xe quốc tế như sau: — `6bf208f1914853db6f23b48b`
- [4] 29/2015/TT-BGTVT, Điều 7. Trách nhiệm cấp và quản lý giấy phép lái xe quốc tế — `f68614b9b6ddd8fa975e30e2`
- [5] 42/2018/TT-BGTVT, Điều 9. Sửa đổi, bổ sung một số Điều của Thông tư số 49/2015/TT-BGTVT ngày 22 tháng 9 năm 2015 của Bộ trưởng Bộ Giao thông vận tải quy định về tiêu chuẩn, nhiệm vụ, quyền hạn của lãnh đạo, đăng kiểm viên, nhân viên nghiệp vụ của đơn vị đăng kiểm phương tiện thủy nội địa (sau đây viết tắt là Thông tư số 49/2015/TT-BGTVT) — `03afc9e15ed0bb9355be577d`
- [6] 39/2021/TT-BGTVT, Điều 1. Sửa đổi, bổ sung một số điều của Thông tư số 50/2015/TT-BGTVT ngày 23 tháng 9 năm 2015 của Bộ trưởng Bộ Giao thông vận tải hướng dẫn thực hiện một số điều của Nghị định số 11/2010/NĐ-CP ngày 24 tháng 02 năm 2010 của Chính phủ quy định về quản lý và bảo vệ kết cấu hạ tầng giao thông đường bộ — `284f72e7577bc87ff388cd60`

## Tái lập

```bash
.venv/bin/python -m evals.run_seed_answers
```

Lệnh thực hiện các cuộc gọi OpenAI có tính phí theo tài khoản đã cấu hình; kết quả model có thể thay đổi giữa các lần chạy.

[Trace đầy đủ](20260907T143434457585Z/answers.jsonl) · [Cấu hình và hash phiên bản](20260907T143434457585Z/manifest.json).
