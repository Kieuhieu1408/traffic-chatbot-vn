# Kế hoạch học và áp dụng Your AI Product Needs Evals

## Nguyên tắc làm việc

Đi theo thứ tự trình bày của bản blog trong `learn/Your AI Product Needs Evals.md`, theo yêu cầu của người dùng. Đây là thứ tự học được chọn, không phải khẳng định tác giả bắt buộc thực hiện tuyến tính: bài nói quá trình thực tế có thể phi tuyến.

Mỗi bước: giải thích ngắn → người dùng thực hành hoặc đưa ra quyết định → đối chiếu kết quả → ghi nhận hoàn thành. Không tự triển khai toàn bộ chặng sau khi người dùng chỉ đồng ý với kế hoạch chung.

Các tài nguyên đã tạo trước được giữ lại, nhưng có công cụ không đồng nghĩa đã hoàn thành phần học. Chưa tự đổi các nhãn người dùng đã lưu.

**Bước hiện tại: đã chạy Qwen fine-tuning pilot trước/sau; xem kết quả và mục còn mở cuối plan. Human calibration và A/B thực tế vẫn chưa hoàn tất.**

Ghi nhận giai đoạn Level 1 trước đây (các số test bên dưới là lịch sử): [scoped-tests.md](scoped-tests.md). Đã thống nhất ba tình huống về số lượng, kết quả rỗng và đoạn bổ sung, cùng ba assertion toàn vẹn dùng chung. Đã giải thích khác biệt test logic/eval thật, tái hiện và sửa lỗi loại trùng. Hiện có 5 ca kiểm soát pass trong `tests/test_retriever.py`; toàn suite 26 pass. Đã đo lại retrieval thật: tìm đủ ID gold tăng 6/10 → 8/10, nhưng đủ căn cứ chính vẫn 9/10 theo đối chiếu của trợ lý; câu 008 chưa sửa. Xem [đối chiếu trước/sau](runs/dedup-before-after.md). Bước học tiếp là Level 1, Step 3: chạy lặp lại và theo dõi kết quả theo phiên bản. Các mục chưa thực hành khác vẫn để mở.

## Cách đọc kế hoạch theo mục tiêu

**Mục tiêu chung:** tự quyết định cần kiểm tra gì, dữ liệu nào đủ để kết luận và thay đổi nào đáng giữ, dựa trên bằng chứng về chất lượng sản phẩm.

Mỗi chặng có mục tiêu chung; mỗi việc có một dòng **Goal — làm để**. Checklist mô tả hành động, goal giải thích giá trị của hành động. Các goal là cách diễn giải để học và áp dụng, không phải câu trích nguyên văn hay yêu cầu bổ sung do tác giả đặt ra.

Trước khi làm, tự trả lời ba câu:

1. Mình đang muốn giảm điều chưa biết nào hoặc ngăn loại quyết định sai nào?
2. Kết quả nào sẽ cho thấy mục tiêu đã đạt, thay vì chỉ cho thấy đã chạy công cụ?
3. Ở bài toán khác, có thể thay dữ liệu, công cụ hoặc cách làm nào mà vẫn đạt mục tiêu đó?

Ví dụ: **xây Shiny viewer** là một cách làm. Goal là **giảm công tìm và đối chiếu bằng chứng để người chấm đưa ra nhãn đáng tin**. Với dự án khác, bảng tính có thể đạt cùng goal; không cần sao chép Shiny chỉ vì repo này dùng nó.

Giữ thứ tự blog để học có hệ thống. Khi tổng quát hóa, mang theo mục tiêu và cách kiểm chứng, không mặc định mọi dự án cần cùng công cụ hay cùng mức đầu tư.


## 0. Motivation, Iterating Quickly và case study Lucy

**Goal của chặng:** Hiểu cơ chế giúp sản phẩm tiến bộ, để không đồng nhất việc sửa model với việc cải thiện chất lượng.

- [x] Đã giới thiệu vòng lặp đánh giá, debug và thay đổi hệ thống.
  - **Goal — làm để:** Biết ba loại công việc phải hỗ trợ nhau: phát hiện vấn đề, giải thích nguyên nhân và kiểm chứng cách sửa.
- [x] Đã liên hệ lỗi sửa prompt thiếu đo lường với RAG Traffic VN.
  - **Goal — làm để:** Nhận ra dấu hiệu thiếu phản hồi chất lượng trong một sản phẩm cụ thể, thay vì mặc định mọi lỗi đều cần sửa prompt.
- [ ] Người dùng tự giải thích lại vai trò của ba hoạt động trong vòng lặp.
  - **Goal — làm để:** Tự suy ra nên đánh giá, điều tra hay thay đổi ở một tình huống mới; kiểm tra mức hiểu thay vì khả năng nhớ tên bước.

## 1. The Types of Evaluation

**Goal của chặng:** Chọn phép đánh giá phù hợp với câu hỏi cần trả lời và nguồn lực có thể chi trả.

- [x] Đã giới thiệu Level 1, Level 2 và Level 3.
  - **Goal — làm để:** Nhận biết mỗi cấp cung cấp loại bằng chứng nào và không chứng minh được điều gì.
- [ ] Phân biệt mục đích, chi phí và tần suất của từng cấp bằng ví dụ trong repo.
  - **Goal — làm để:** Phân bổ công sức đánh giá: bắt lỗi rẻ sớm, dành người/model cho phần cần hiểu nghĩa, dùng thí nghiệm thực tế cho tác động sản phẩm.

## 2. Level 1 — Step 1: Write Scoped Tests

**Goal của chặng:** Biến một năng lực rộng của sản phẩm thành các hành vi cụ thể có thể kiểm tra và định vị lỗi.

- [x] Chọn tính năng đầu tiên: tìm nguồn tài liệu.
  - **Goal — làm để:** Giới hạn phạm vi đủ nhỏ để hiểu đầu vào, đầu ra và tiêu chuẩn thành công; có thể chọn bất kỳ tính năng quan trọng nào ở sản phẩm khác.
- [ ] Chia tính năng thành các tình huống cụ thể.
  - **Goal — làm để:** Làm rõ những điều kiện sử dụng khác nhau có thể làm thay đổi hành vi đúng, tránh kiểm tra chỉ một trường hợp thuận lợi.
- [ ] Viết kỳ vọng và assertion kiểm tra bằng code cho từng tình huống phù hợp.
  - **Goal — làm để:** Chuyển kỳ vọng thành tín hiệu đạt/trượt khách quan ở những phần code kiểm tra được; nhận ra phần vẫn cần người đọc hiểu.
- [x] Xác định assertion dùng chung, không phụ thuộc một câu hỏi.
  - **Goal — làm để:** Bảo vệ các ràng buộc lặp lại ở nhiều tình huống bằng cùng một phép kiểm tra, giảm bỏ sót và công sức duy trì.
- [ ] Đối chiếu test hiện có: test nào bảo vệ hành vi nào, còn bỏ sót gì?
  - **Goal — làm để:** Biết đang có bằng chứng cho hành vi nào và khoảng trống nào đáng bổ sung; không lấy số lượng test làm đại diện chất lượng.
- [ ] Phân biệt test logic offline với assertion sau khi chạy pipeline thật.
  - **Goal — làm để:** Biết lỗi nằm ở logic cục bộ hay hành vi toàn hệ thống, đồng thời chọn cách chạy phù hợp với chi phí và độ ổn định.

Kết quả cần có: danh sách **tính năng → tình huống → assertion**, giải thích được giới hạn của từng assertion. Danh sách này là đầu vào cho Step 2.

Đã có để tham khảo: `tests/`, gồm test ingest, index, session, generation, cấu hình và lưu nhãn. Chưa coi đó là bộ scoped tests đầy đủ cho nghiệp vụ RAG.

## 3. Level 1 — Step 2: Create Test Cases

**Goal của chặng:** Dùng đầu vào có chủ đích để thử thách các hành vi cần bảo vệ, thay vì gom câu hỏi chỉ để có dataset.

- [ ] Tạo đầu vào kích hoạt các tình huống ở Step 1.
  - **Goal — làm để:** Làm cho từng tình huống thực sự được thực thi; một assertion không được kích hoạt có thể tạo cảm giác an toàn giả.
- [ ] Dùng LLM sinh biến thể nếu cần; người dùng đối chiếu và duyệt.
  - **Goal — làm để:** Tăng độ đa dạng cách diễn đạt mà vẫn kiểm soát tính đúng của kỳ vọng, không coi dữ liệu sinh ra là nhãn chuẩn tự động.
- [ ] Kiểm tra đầu vào đại diện cách người dùng tương tác và đủ thách thức.
  - **Goal — làm để:** Để kết quả eval có liên hệ với trải nghiệm thực tế và phát hiện được giới hạn hệ thống, thay vì chỉ tốt trên ví dụ được gợi ý sẵn.
- [ ] Bổ sung ca từ lỗi quan sát được.
  - **Goal — làm để:** Biến phát hiện mới thành trí nhớ của hệ thống kiểm tra, giúp nhận ra khi cùng lỗi tái diễn.
- [ ] Xác định các loại thất bại sản phẩm có thể hoặc không thể chấp nhận.
  - **Goal — làm để:** Đặt tiêu chuẩn chấp nhận dựa trên hậu quả của lỗi đối với người dùng, tránh dùng một ngưỡng pass chung thiếu ý nghĩa.

Kết quả cần có: bộ ca gắn rõ với các assertion, có nguồn gốc và trạng thái duyệt.

Đã có: `corpus-seed-10.jsonl`. Bộ này nêu rõ nguồn trong câu hỏi và có nhãn đề xuất; cần xem lại mức phù hợp với các tình huống đã chọn. Không tự xóa tiền tố và giữ nguyên đáp án mà chưa kiểm tra lại phạm vi.

## 4. Level 1 — Step 3: Run & Track Your Tests Regularly

**Goal của chặng:** Tạo phản hồi chất lượng đủ nhanh và có thể so sánh để dẫn đường cho mỗi lần thay đổi.

- [x] Tổ chức chạy với ít trở ngại nhất trong stack hiện tại.
  - **Goal — làm để:** Giảm chi phí thao tác để việc kiểm tra trở thành thói quen thực tế, không bị bỏ qua vì khó chạy.
- [x] Xác định test nào chạy mỗi thay đổi, test nào chạy theo lịch.
  - **Goal — làm để:** Cân bằng tốc độ nhận phản hồi với tiền và thời gian chạy; dành tần suất cao cho kiểm tra nhanh và quan trọng.
- [x] Lưu kết quả cùng phiên bản tests, prompts và cấu hình liên quan.
  - **Goal — làm để:** Có thể giải thích, tái hiện và đối chiếu kết quả; biết điểm đổi do hệ thống hay do bộ đo đã đổi.
- [ ] Xem kết quả qua thời gian để biết đang tiến bộ hay thoái lui.
  - **Goal — làm để:** Nhận ra xu hướng cải thiện và các nhóm lỗi bị che bởi điểm tổng, thay vì chỉ nhìn một lần chạy.
- [ ] Thực hành một thay đổi và đọc kết quả trước/sau.
  - **Goal — làm để:** Tập ra quyết định giữ hay bỏ thay đổi dựa trên bằng chứng về cải thiện và thoái lui.

Kết quả cần có: chạy được bộ kiểm tra và giải thích được kết quả so sánh. CI là cách triển khai có thể dùng, không phải điều kiện bắt buộc của blog.

Đã triển khai `make check` và `make eval-retrieval`, lưu hash source/tests và metadata môi trường. Suite hiện có 28 test pass, gồm kiểm tra đổi code chưa commit và lưu lượt test thất bại. Nhịp chạy, cách đọc và giới hạn: [regular-checks.md](regular-checks.md). Chưa đặt lịch/CI hoặc dashboard so sánh tự động. Phần tự đọc xu hướng và giải thích kết quả của người học vẫn để mở.

## 5. Level 2 — Logging Traces

**Goal của chặng:** Làm cho hành vi của hệ thống quan sát được, để giải thích một đầu ra bằng các bước đã tạo ra nó.

- [ ] Hiểu trace là nhóm sự kiện của một luồng xử lý/hội thoại.
  - **Goal — làm để:** Nối các sự kiện liên quan thành một câu chuyện xử lý đầy đủ, thay vì xem những dòng log rời rạc.
- [ ] Chọn thông tin cần log để xem được hành vi của RAG.
  - **Goal — làm để:** Giữ đủ thông tin để trả lời các câu hỏi chẩn đoán quan trọng mà không thu thập mọi thứ vô mục đích.
- [x] Thu trace từ các yêu cầu sử dụng UI/API.
  - **Goal — làm để:** Phát hiện cách sử dụng và lỗi ngoài dự đoán của người tạo test, giảm điểm mù của bộ dữ liệu tổng hợp.
- [ ] Có thể tìm kiếm, lọc và đọc traces.
  - **Goal — làm để:** Tìm nhanh bằng chứng của một phản ánh và các ca tương tự để hiểu mức phổ biến của vấn đề.

Kết quả cần có: từ một yêu cầu thực tế có thể xem lại câu hỏi, nguồn truy xuất và câu trả lời.

Đã tích hợp LangSmith trực tiếp cho `/search`: trace cha và hai bước retrieval/generation, nhóm theo session_id, có nguồn và phiên bản code. 34 test pass. Ngày 2026-09-08 đã xác nhận qua API một trace từ `/search` thật, root và hai bước con hoàn tất. Phần người học tự tìm/lọc/đọc trace vẫn để mở. Xem [hướng dẫn thực hành LangSmith](langsmith-tracing.md). `run_seed_answers.py` và Shiny vẫn dùng các run cục bộ.

## 6. Level 2 — Looking At Your Traces

**Goal của chặng:** Giúp người hiểu nghiệp vụ quan sát dữ liệu và tạo phản hồi đáng tin với ít thao tác nhất.

- [x] Đã tạo Shiny viewer phù hợp dữ liệu RAG: câu hỏi, câu trả lời, nguồn và nhãn.
  - **Goal — làm để:** Đặt thông tin cần đối chiếu cạnh nhau để giảm công tìm kiếm và ghi nhớ; ở lĩnh vực khác, chọn thông tin theo quyết định người chấm phải đưa ra.
- [x] Đã có nhãn nhị phân Đạt/Trượt; chưa chấm là trạng thái.
  - **Goal — làm để:** Giữ quyết định chất lượng đơn giản và nhất quán; không trộn sự chưa chắc của người chấm với một mức chất lượng thứ ba.
- [x] Đã thực hành đối chiếu một số câu với nguồn.
  - **Goal — làm để:** Học nhận biết một kết luận được nguồn hỗ trợ như thế nào, thay vì chấm theo độ trôi chảy của câu trả lời.
- [ ] Đọc và chấm dữ liệu theo tiêu chuẩn nhất quán.
  - **Goal — làm để:** Để cùng loại lỗi được xử lý giống nhau giữa các ca và lần chạy, giúp nhãn có thể dùng để so sánh.
- [ ] Ghi lý do lỗi để phục vụ debug và điều chỉnh evaluator.
  - **Goal — làm để:** Biến nhãn thành phản hồi có thể hành động: biết sai ý nào, vì sao và evaluator cần chú ý điều gì.
- [ ] Loại bỏ tiếp những trở ngại phát hiện khi dùng công cụ.
  - **Goal — làm để:** Làm cho việc đọc thêm dữ liệu ít tốn sức hơn, thay vì tăng số chức năng không phục vụ quyết định chấm.
- [ ] Theo dõi kết quả human eval qua thời gian.
  - **Goal — làm để:** Đo được sự thay đổi chất lượng theo cách người dùng/người hiểu nghiệp vụ nhìn nhận, với tiêu chuẩn chấm được theo dõi.
- [ ] Xác định cách tiếp tục đọc dữ liệu và lấy mẫu khi dữ liệu tăng.
  - **Goal — làm để:** Duy trì khả năng phát hiện lỗi mới khi quy mô tăng; giảm khối lượng đọc mà không từ bỏ quan sát trực tiếp.

Kết quả cần có: người dùng tự đưa ra nhãn có lý do dựa trên nguồn, không chỉ chấp nhận nhãn trợ lý.

Đã có: `review/` và `rubric.md`. Rubric là tài liệu hỗ trợ của repo; blog không bắt buộc viết riêng tài liệu này trước Level 1. Các nhãn được trợ lý gợi ý không phải đánh giá độc lập của người dùng.

## 7. Level 2 — Automated Evaluation with LLMs

**Goal của chặng:** Mở rộng quy mô đánh giá ngữ nghĩa mà vẫn biết giới hạn độ tin cậy của người chấm máy.

- [x] Tạo evaluator với tiêu chí và dữ liệu cần thiết để chấm.
  - **Goal — làm để:** Để judge có cả tiêu chuẩn và bằng chứng cần thiết, không chấm bằng cảm giác hoặc kiến thức không được kiểm chứng.
- [ ] So sánh nhãn/lý do của judge với người chấm.
  - **Goal — làm để:** Đo xem judge có thực sự áp dụng tiêu chuẩn mà người chấm mong muốn hay không.
- [ ] Phân tích bất đồng và chỉnh prompt evaluator.
  - **Goal — làm để:** Phân biệt lỗi judge, nhãn người sai và tiêu chuẩn mơ hồ để sửa đúng nguyên nhân của bất đồng.
- [ ] Đo precision/recall với lớp dương được định nghĩa rõ; hiểu bẫy raw agreement trên dữ liệu lệch lớp.
  - **Goal — làm để:** Biết judge báo nhầm bao nhiêu và bỏ sót bao nhiêu lỗi, tránh tin vào tỷ lệ đồng ý cao trên dữ liệu nhiều ca tốt.
- [ ] Kiểm tra chất lượng evaluator trên dữ liệu chưa dùng để chỉnh.
  - **Goal — làm để:** Kiểm tra khả năng áp dụng tiêu chuẩn cho ví dụ mới, thay vì chỉ khớp những ca đã dùng để sửa prompt.
- [ ] Tiếp tục kiểm tra mẫu bằng người theo định kỳ.
  - **Goal — làm để:** Phát hiện độ tin cậy thay đổi khi sản phẩm, dữ liệu hoặc model đổi; không coi căn chỉnh một lần là đủ.

Kết quả cần có: biết judge bắt được và bỏ sót loại lỗi nào, thay vì chỉ biết nó đã chạy.

Đã tạo judge GPT-5.4 mini riêng, chạy 10 trace với snapshot prompt/rubric/input và lưu kết quả; UI Blind review lưu nhãn người độc lập, khóa trước khi reveal. Chưa có cặp nhãn human độc lập nên precision/recall N/A. Những ca đã được trợ lý gợi ý không tự thành human gold. Chưa căn chỉnh prompt, chưa có holdout. Xem [judge-guide.md](judge-guide.md).

## 8. Level 3 — A/B Testing

**Goal của chặng:** Xác định thay đổi có cải thiện kết quả thật của người dùng, vượt ra ngoài điểm trên bộ câu hỏi offline.

- [ ] Xác định hành vi/kết quả người dùng sản phẩm muốn cải thiện.
  - **Goal — làm để:** Định nghĩa thành công bằng lợi ích người dùng cần, tránh tối ưu một chỉ số thuận tiện nhưng không phản ánh giá trị.
- [ ] Thiết kế hai phiên bản, phân nhóm và sự kiện cần ghi.
  - **Goal — làm để:** Tạo phép so sánh có thể quy kết tác động cho thay đổi, đồng thời thu đủ dữ liệu để phân tích kết quả.
- [ ] Kiểm tra cơ chế bằng dữ liệu mô phỏng, ghi rõ đây là kiểm tra kỹ thuật.
  - **Goal — làm để:** Phát hiện lỗi phân nhóm và ghi nhận sự kiện trước khi sử dụng dữ liệu đó cho kết luận về sản phẩm.
- [ ] Chạy thử với người dùng thật khi phù hợp và có điều kiện.
  - **Goal — làm để:** Quan sát tác động trong điều kiện sử dụng thực tế, nơi hành vi có thể khác bộ test hoặc dữ liệu mô phỏng.
- [ ] Phân tích kết quả và giới hạn bằng chứng.
  - **Goal — làm để:** Ra quyết định triển khai dựa trên độ lớn tác động và mức chắc chắn, không biến nhiễu hoặc thiếu dữ liệu thành kết luận.

Kết quả cần có: thiết kế và cơ chế A/B hoạt động. Chỉ kết luận tác động thực tế khi có dữ liệu người dùng đủ phù hợp; không dùng mô phỏng thay bằng chứng thực nghiệm.

## 9. Evaluating RAG

**Goal của chặng:** Tách chất lượng từng thành phần để biết nên cải thiện khả năng tìm bằng chứng hay cách dùng bằng chứng.

Blog chỉ nhắc có thể đánh giá riêng RAG và dẫn sang bài khác; không trình bày chi tiết.

- [ ] Sau khi học các phần trước, tách một buổi mở rộng về đánh giá retrieval và generation.
  - **Goal — làm để:** Thu hẹp nơi cần can thiệp bằng các phép đo phù hợp từng thành phần; nguyên tắc tương tự áp dụng cho mọi pipeline nhiều bước.
- [ ] Hiểu Recall@k, MRR, nguồn tương đương và giới hạn gold labels của repo.
  - **Goal — làm để:** Hiểu đối tượng, mẫu số và giới hạn của mỗi metric để không kết luận sai từ điểm số hoặc ID nguồn khác nhau.

Đã có metric retrieval ban đầu. Công thức và thiết kế cụ thể thuộc phần mở rộng, không gán cho blog này.

## 10. Fine-Tuning — Data Synthesis & Curation

**Goal của chặng:** Tái sử dụng dữ liệu đánh giá đã duyệt cho cải thiện model, và chọn huấn luyện chỉ khi phù hợp nguyên nhân lỗi.

- [ ] Phân biệt fine-tuning học hành vi/cú pháp/phong cách với RAG cung cấp context/dữ kiện.
  - **Goal — làm để:** Chọn đúng loại can thiệp: thiếu dữ kiện khác với chưa thực hiện đúng hành vi, nên không mặc định huấn luyện giải quyết mọi lỗi.
- [ ] Sinh dữ liệu và tái sử dụng Level 1/2 để lọc, xem và chỉnh sửa.
  - **Goal — làm để:** Tạo thêm ví dụ tốt với cơ chế kiểm soát chất lượng sẵn có, giảm công sức mà không bỏ bước xác minh.
- [ ] Tạo một tập dữ liệu chất lượng đã duyệt và tách khỏi dữ liệu kiểm tra.
  - **Goal — làm để:** Cung cấp tín hiệu học đáng tin và giữ một phép đo độc lập để biết model có tiến bộ trên dữ liệu chưa học hay không.
- [ ] Xác định có bằng chứng cần fine-tuning hay không trước khi quyết định huấn luyện.
  - **Goal — làm để:** Tránh chi tiền và công huấn luyện khi nút thắt nằm ở dữ liệu, retrieval hoặc code; nêu rõ bằng chứng cần có để chọn fine-tuning.

Kết quả cần có: dữ liệu được tuyển chọn và giải thích được vì sao dùng hoặc chưa dùng fine-tuning. Blog không cung cấp hướng dẫn huấn luyện chi tiết trong bài này.

## 11. Debugging và Conclusion

**Goal của chặng:** Khép kín vòng cải thiện: từ một lỗi có thật đến cách sửa có bằng chứng và bài học dùng lại được.

- [ ] Từ một phản ánh/lỗi, tìm trace liên quan và xác định tầng gây lỗi.
  - **Goal — làm để:** Biến phản ánh chung chung thành nguyên nhân có thể kiểm tra, thay vì sửa ở nơi dễ sửa nhất.
- [ ] Tái sử dụng assertion, bộ ca và công cụ xem dữ liệu để sửa và kiểm tra.
  - **Goal — làm để:** Rút ngắn thời gian từ phát hiện lỗi đến kiểm chứng cách sửa bằng hạ tầng đã xây, thay vì làm quy trình riêng cho mỗi lỗi.
- [ ] Tổng kết một vòng cải thiện bằng bằng chứng trước/sau.
  - **Goal — làm để:** Giải thích được thay đổi nào có ích, bằng chứng nào hỗ trợ và giới hạn nào còn lại; đây là năng lực có thể mang sang dự án khác.
- [ ] Đối chiếu các nguyên tắc kết bài: đơn giản, đọc nhiều dữ liệu, eval riêng theo bài toán, cập nhật tests và tái sử dụng hạ tầng.
  - **Goal — làm để:** Rút ra các nguyên tắc chọn công việc có giá trị, để thay công cụ hoặc thứ tự khi bối cảnh khác mà vẫn đạt mục tiêu đánh giá.

Đã có ví dụ chẩn đoán câu 008; tăng k chưa sửa được lỗi. Vị trí mục này theo blog không có nghĩa phải trì hoãn debug khi gặp lỗi ở các bước trước.

## Theo dõi

Chỉ đánh dấu hoàn thành khi đã có bằng chứng hoặc kết quả thực hành tương ứng. Khi tiếp tục học, cập nhật bước hiện tại và checklist này; không tự chuyển chặng vì đã có sẵn công cụ.

### Cập nhật Looking At Your Traces — English Shiny reviewer

Đã nối Shiny với LangSmith: đọc root trace, lịch sử và nguồn; load/update answer_pass và review_reason; optional corrected answer. UI tiếng Anh, filter/skip/save-next, link trace, kiểm tra xung đột và xác minh save. Local eval/SQLite giữ riêng. Goal: đọc bằng chứng và chấm trên một màn hình, không cần chấm trùng ở hai công cụ. Xem `review/README.md`.

### Assistant review pilot — 2026-09-08

- [x] Chấm riêng 10 trace với provenance `assistant`, rồi đối chiếu judge đã chạy. **Goal:** tìm bất đồng trong cách áp dụng rubric. Báo cáo: [assistant-comparison.md](judge_runs/20260908T093514688801Z/assistant-comparison.md).
- Kết quả: trợ lý 8 pass/2 fail; judge 10 pass; đồng thuận AI-vs-AI 80%. Không tính lượt này vào human calibration.
- [ ] Phân xử hai ca biên về căn cứ trích dẫn và điều kiện hạng xe, rồi phiên bản hóa rubric nếu cần. **Goal:** có tiêu chuẩn nhất quán trước khi chỉnh judge; không coi nhãn trợ lý là chân lý.

### Rubric v2 — phân xử bất đồng

- [x] Làm rõ suy luận hợp lý, điều kiện cần/đủ và lỗi bỏ điều kiện có ý nghĩa. **Goal:** tránh đánh Trượt vì thiếu chi tiết không làm đổi kết luận.
- [x] Phân xử lại hai ca thành Pass theo v2; giữ nhãn v1 để truy vết. Đây là nhãn assistant, chưa phải expert gold.
- [x] Thêm hướng dẫn tương ứng vào judge prompt.
- [ ] Thu thập trace thực mới chưa dùng phát triển, chấm trước rồi đối chiếu. **Goal:** kiểm tra khả năng áp dụng ngoài ví dụ phát triển; bộ giả lập chưa thay thế bước này.
- [x] Chạy rubric v2 trên 10 ca phát triển và 6 probe giả lập; kết quả cuối khớp nhãn assistant 16/16 (probe 3 pass/3 fail). **Goal:** kiểm tra hành vi judge, chưa đo chất lượng trên dữ liệu mới độc lập. [Báo cáo](judge_experiments/20260908T100301Z/report.md).
- [x] Sửa validator với câu trích có ngoặc kép bao ngoài; 54 tests qua.

### Fresh natural questions — 2026-09-08

- [x] Chạy 10 câu hỏi mới qua RAG thật, chấm assistant trước judge, giữ nguyên rubric/prompt v2. **Goal:** kiểm tra cách áp dụng ngoài bộ ví dụ chỉnh prompt. [Báo cáo](fresh_runs/20260908-natural10/report.md).
- Kết quả: cả hai chấm Pass 10/10; chưa đo được khả năng phát hiện Fail vì không có nhãn Fail tham chiếu. Hai ca không tìm được nguồn đúng dù corpus có: mất IDP và hình thức IDP.
- [ ] Điều tra retrieval của fresh-01 và fresh-05. **Goal:** giúp hệ thống giải quyết nhu cầu thay vì chỉ từ chối có căn cứ. Không đánh đồng answer_pass với task completion.

### IDP retrieval fix

- [x] Điều tra và sửa fresh-01/fresh-05 bằng chuẩn hóa tên IDP cho embedding. **Goal:** lấy được nguồn dù câu hỏi dùng cách gọi tự nhiên. 20 ca retrieval trước/sau, 56 tests qua; hai nguồn mục tiêu lên hạng 1. [Báo cáo](runs/idp-query-expansion/report.md).
- [ ] Dùng output mới fresh-05 (thêm “chỉ dùng” tại nước Công ước Viên) làm ca lỗi generation để kiểm tra judge. **Goal:** phân biệt nguồn nói trong phạm vi X với khẳng định chỉ X; không gộp retrieval thành chất lượng toàn câu trả lời.

- [x] Cho judge v2 chấm output mới fresh-05: judge Pass, assistant Fail về từ “chỉ dùng”. **Goal:** kiểm tra khả năng nhận ra suy rộng phạm vi. [Kết quả](runs/idp-query-expansion/judge-new-failure/report.md). Đây là bất đồng trên một ca lỗi đã biết, không phải ước lượng chất lượng tổng thể.
- [ ] Làm rõ suy luận loại trừ (“tại X” không mặc nhiên là “chỉ tại X”), thử cặp đối chứng và các ca khác. **Goal:** cải thiện phát hiện lỗi phạm vi mà không phạt cách diễn đạt có căn cứ.

### Quy tắc loại trừ — rubric v3

- [x] Làm rõ “tại X” không suy ra “chỉ tại X”; dùng đối chứng có chữ chỉ nhưng đúng và không có chỉ nhưng sai. **Goal:** chấm ý nghĩa, không theo từ khóa.
- [x] Thử v2/v3: 5/6 → 6/6 probe khớp nhãn assistant; output RAG đầy đủ vẫn bị bỏ sót (judge Pass). [Báo cáo](judge_experiments/20260908T103022Z-scope/report.md). Không phải human calibration.
- [x] Cập nhật blog Markdown và HTML, bổ sung quá trình từ pilot v1/v2, 10 câu mới, sửa retrieval IDP đến thử v3.
- [ ] Thử đối chiếu từng nhận định trong câu dài trước khi tổng hợp nhãn. **Goal:** phát hiện ý phụ vượt nguồn dù ý chính đúng; kiểm tra thêm ca khác trước khi tin kết quả.

### Claim audit experiment

- [x] Thử evaluator riêng đối chiếu từng nhận định, rubric v3 giữ nguyên. **Goal:** bắt ý phụ vượt nguồn trong câu dài. 62 tests qua.
- Kết quả trên 6 ca: v3 6/6; audit 5/6 và 1 abstain do disclaimer. V3 đã đổi nhãn trên ca từng bỏ sót giữa các lần chạy; chưa kết luận audit tốt hơn. [Báo cáo](judge_experiments/20260908T120618Z-claims/report.md).
- [x] Cập nhật blog Markdown và HTML cùng kết quả, giới hạn và quyết định giữ evaluator ở mức thí nghiệm.
- [ ] Làm rõ disclaimer, đo lặp và kiểm tra các ca đa dạng hơn. **Goal:** giảm abstain không cần thiết và đo ổn định trước khi thay judge mặc định.

### Kết thúc vòng thực hành Automated Evaluation

- [x] Đóng băng v3, thử 8 câu trả lời mới cân bằng 4 Pass/4 Fail, lặp ba lần. **Goal:** đo khả năng phân biệt lỗi và độ ổn định, không sửa prompt giữa lượt.
- [x] Tính precision/recall/coverage/abstain/error và ổn định bằng `evals.summarize_repeats`. Ba lượt đều 4 TP, 4 TN, không FP/FN/abstain/error; 8/8 ổn định. Bộ nhỏ giả lập, nhãn assistant. [Báo cáo](judge_experiments/20260908-stability/report.md).
- [x] Cập nhật blog MD/HTML và quyết định giữ v3 hỗ trợ review, claim audit thử nghiệm. 64 tests qua.
- [ ] Human calibration với nhãn chuyên môn độc lập và bộ câu trả lời thực đa dạng. **Goal:** biết judge bám tiêu chuẩn đúng của người dùng/chuyên gia, không chỉ đồng thuận AI. Chưa hoàn tất; không thay bằng nhãn assistant.

### Level 3 — A/B pilot infrastructure

- [x] Ghi giả thuyết A/B, eligibility, đơn vị phiên, chỉ số và nguyên tắc dừng. **Goal:** quyết định cách đọc kết quả trước khi có dữ liệu. [Plan](ab-plan.md).
- [x] Thêm phân nhóm cố định theo phiên, routing retrieval A/B, metadata trace, feedback Yes/No và báo cáo mô tả. 69 tests qua; UI dùng mạng giả lập, không đưa vào feedback thực.
- [x] Cập nhật blog Markdown/HTML. Mặc định thí nghiệm tắt; báo cáo hiện no_data.
- [ ] Có người dùng tình nguyện, chốt lịch pilot 14 ngày rồi bật thu thập. **Goal:** đo lợi ích thực tế; không gọi kiểm tra bằng AI là A/B với người dùng.

## Bổ sung từ Jason Liu — đánh giá retrieval và generation

Nguồn: [Levels of Complexity: RAG Applications](https://jxnl.github.io/blog/writing/2024/02/28/levels-of-complexity-rag-applications/), bản đã đọc tại `/home/cong/Downloads/Levels of Complexity_ RAG Applications.md`. Đây là phần bổ sung RAG, không phải các bước do Hamel yêu cầu. Các lựa chọn chia dữ liệu, K và thứ tự dưới đây là cách áp dụng vào repo.

Trạng thái: mới lập kế hoạch. Repo đã có retrieval metrics, trace nguồn và rubric; các đầu việc dưới đây chưa được coi là hoàn tất chỉ vì có hạ tầng tương tự.

### Ưu tiên 1 — nền tảng trước khi fine-tune Qwen3-1.7B

- [ ] Chuẩn bị bộ câu hỏi tự nhiên, nguồn tham chiếu và đáp án/tiêu chí đã review; ghi provenance nhãn. Chia train/dev/test trước khi tạo biến thể, gom cùng điều khoản/chủ đề tương đương và bản PDF/DOCX trùng vào cùng nhóm chia. **Goal:** đánh giá khả năng áp dụng ngoài ví dụ đã huấn luyện, tránh rò rỉ do câu diễn đạt lại hoặc nguồn trùng. **Đầu ra:** manifest chia tập và kiểm tra trùng; giữ test khỏi curation/training/prompt tuning.
- [ ] Thiết lập phép thử generation với câu hỏi + nguồn đúng cố định, lưu baseline Qwen chưa fine-tune. Giữ prompt, nguồn và cấu hình sinh khi so trước/sau; kiểm tra nguồn có vừa context, không âm thầm cắt mất căn cứ. **Goal:** đo khả năng model sử dụng nguồn, tách khỏi lỗi retrieval. **Đầu ra:** câu trả lời baseline và nhãn theo rubric, sau này so với Qwen đã fine-tune.
- [ ] Thiết lập phép thử end-to-end trên cùng câu hỏi nhưng dùng retrieval thật; đóng băng corpus/index/cấu hình retrieval. **Goal:** biết cải thiện generation có chuyển thành cải thiện toàn hệ thống không. **Đầu ra:** báo cáo song song nguồn đúng cố định và RAG thật; tách answer_pass với khả năng giải quyết nhu cầu.
- [ ] Chuẩn hóa đánh giá nguồn theo đơn vị bằng chứng, nhận diện các chunk tương đương về nội dung thay vì chỉ ID. **Goal:** không phạt nguồn đúng ở bản PDF khác DOCX hoặc thưởng việc lấy nhiều bản trùng. **Đầu ra:** ánh xạ bằng chứng tương đương, quy tắc xử lý đoạn bổ sung và trường hợp chưa rõ.
- [ ] Đo Recall@K, Precision@K tại K=1,3,6,10 trên bộ có nhãn relevance đủ trong tập ứng viên được review; giữ MRR hiện có như chỉ số bổ sung của repo. **Goal:** đo độ phủ nguồn đúng và mức nhiễu theo số nguồn đưa vào context. **Đầu ra:** công thức/mẫu số, phạm vi nhãn và bảng trước/sau rõ ràng. Một chunk dùng sinh câu hỏi chỉ cho phép kiểm tra tìm lại nguồn đã biết, không mặc nhiên là toàn bộ gold; chưa đủ nhãn thì không báo precision như đã biết mọi nguồn liên quan.

### Ưu tiên 2 — quan sát và phân tích điểm yếu

- [ ] Tách `retrieved_chunk_ids`, `cited_chunk_ids` và citation không hợp lệ thành trường riêng trong trace, cùng query gốc/query chuẩn hóa và điểm retrieval. **Goal:** phân biệt tìm được nguồn, model chọn nguồn và trích dẫn thực sự có căn cứ. **Đầu ra:** truy được citation về đúng chunk của lượt trả lời; việc có citation không tự chứng minh nhận định được hỗ trợ.
- [ ] Báo cáo theo topic (IDP, tốc độ, khoảng cách…) và capability (tra cứu trực tiếp, đọc bảng, điều kiện/ngoại lệ, so sánh, follow-up…). **Goal:** phát hiện năng lực yếu bị điểm trung bình che khuất để tuyển chọn dữ liệu fine-tune đúng mục tiêu. **Đầu ra:** số ca, lỗi retrieval, lỗi answer và ví dụ cho từng nhóm; nhóm ít mẫu ghi rõ chưa đủ kết luận.
- [ ] Dùng cosine score để ưu tiên đọc trace, không diễn giải thành xác suất đúng; nếu có reranker sau này cũng xử lý tương tự. **Goal:** dùng score làm tín hiệu điều tra, không thay đánh giá bằng nguồn và kết quả tác vụ.

### Hoãn đến khi có bằng chứng cần thiết

- [ ] Chỉ thử reranker, nhiều truy vấn song song hoặc rewrite theo lịch sử khi nhóm lỗi cụ thể cho thấy nhu cầu; mỗi lần thử có baseline, metric và chi phí/latency. **Goal:** tăng độ phức tạp để giải quyết lỗi quan sát được, không thêm công cụ chỉ vì bài nhắc đến.
- [ ] Chỉ thêm clustering tự động khi số query đủ lớn khiến phân nhóm thủ công khó quản lý. **Goal:** khám phá mẫu lỗi trên dữ liệu, không thay thế việc đọc trace.

Thứ tự làm tiếp: chuẩn bị/chia dữ liệu → generation baseline với nguồn cố định → retrieval/end-to-end baseline → curation và fine-tune Qwen → so trước/sau trên test giữ riêng. A/B với người dùng thật vẫn hoãn; phần này không thay human calibration.

### Qwen pilot — tiến độ triển khai

- [x] Kiểm kê các bộ cũ, giữ nhãn cũ làm dữ liệu phát triển thay vì expert gold. [Inventory](../finetune/data/inventory.json).
- [x] Tạo bộ pilot chia theo văn bản: 16 train/5 dev/6 test, nguồn exact-span và nhãn assistant; manifest ghi rõ thiếu comparison/multi-turn, train thiếu bảng. **Goal:** học quy trình chia tập và curation có truy vết; chưa đáp ứng bộ đa dạng đầy đủ ở ưu tiên 1.
- [x] Đóng băng 7 context retrieval thật và kiểm tra known-evidence hit@1/3/6/10; Precision@K còn chờ relevance review đủ. **Goal:** không báo metric chính xác giả khi nguồn không khớp vẫn có thể liên quan.
- [x] Log riêng retrieved/cited/invalid citations. **Goal:** tách nguồn tìm được và nguồn model trích; không coi citation tồn tại là groundedness.
- [x] Chuẩn bị script baseline/train/after với cấu hình cố định, nguồn không bị cắt âm thầm và adapter riêng. **Goal:** so cùng model trước/sau, không đổi GPT đang phục vụ.

### Qwen pilot — kết quả đã chạy

- [x] Baseline Qwen3-1.7B 4-bit trên nguồn đúng cố định và context retrieval đóng băng; log nguồn bị bỏ theo ngân sách, không silent truncation.
- [x] QLoRA 16 mẫu train, 3 epoch cố định; adapter riêng, không thay GPT phục vụ. Loss 2,25 → 1,49.
- [x] So trước/sau: dev 5/5 → 4/5, test 4/6 → 5/6, end-to-end 3/7 → 3/7 theo judge v3; 1 lỗi judge retry có lưu lịch sử. **Goal:** kiểm tra cải thiện thực, kết luận hiện tại là pha trộn, chưa chứng minh cải thiện tổng thể.
- [x] Báo cáo theo topic/capability, spot-review assistant ba cặp trước/sau, lưu phiên bản dữ liệu/model/cấu hình/output. [Report](../finetune/runs/pilot-v1/report.md).
- [x] Cập nhật blog Markdown/HTML với quá trình và kết quả âm tính/hồi quy. 71 tests kỹ thuật qua.
- [ ] Mở rộng dữ liệu đọc bảng, comparison, multi-turn; review relevance đủ cho Precision@K và equivalence nguồn ngữ nghĩa. **Goal:** chuyển từ pilot cơ chế sang phép đo có độ bao phủ; các mục rộng ở phần Jason vẫn chưa hoàn tất.

**Trạng thái tổng kết:** xong vòng học fine-tuning pilot, không phải xong mọi mục plan. Human calibration và A/B cần người thật; không gán nhãn assistant thành human để đóng checklist.
