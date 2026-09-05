# T-07 — Evidence Investigation (RQ-1 / RQ-2 / RQ-3 / RQ-4 / RQ-5)

Authorized by: `DEC-039` (Owner Decision, phản hồi `docs/reviews/T07-OWNER-DECISION-BRIEF.md`).
Mode: **SPIKE / EXPLORATORY** (`TASK_MODE_STANDARD.md` Mode 3) — mục tiêu giảm bất định, KHÔNG
phải work package sản xuất. Capability: `CAP-VERDICT` (lineage root `WP-B1`).

**CẬP NHẬT (Owner-run replay nhận được)**: Owner đã chạy script §6 trên dataset official T-06 đã
bảo toàn. `STEP_0 = PASS` (reproduce bit-for-bit). Toàn văn output đã bảo toàn tại
`docs/reviews/T07-RQ-REPLAY-EVIDENCE-RECORD.md` (kèm 8 phép kiểm nhất quán cơ học, không phát
hiện mâu thuẫn nào). §1/§2/§3/§4/§5 dưới đây đã được **tái đánh giá** theo evidence đó — phần nào
là REPLAY (không phải official) được dán nhãn tường minh ở mỗi chỗ dùng.

**Đây KHÔNG phải một official T-06 run mới, KHÔNG đổi verdict, KHÔNG mở `T-11`/`WP-D2`, KHÔNG
sửa `src/`. Production diff = EMPTY.** Mục tiêu — nguyên văn Owner: hiểu thất bại đủ tốt để tránh
(1) bỏ một hypothesis còn tín hiệu hữu ích chỉ vì sai objective/capital treatment, hoặc (2) mở
V2.2 và tiếp tục tối ưu một hypothesis thực tế không có edge.

## 0. Nhãn dùng trong file này

Kế thừa ba nhãn của `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §1, cộng hai nhãn mới cho phiên SPIKE
này:

| Nhãn | Ý nghĩa |
|---|---|
| **[R]** REPOSITORY-VERIFIED | Tái lập được từ chính repository này trong phiên này |
| **[O]** OWNER-REPORTED | Owner khai báo / tự verify trên máy có dataset official |
| **REPLAY** | Số derived, tính bằng script ở §6, chạy trên dataset official đã bảo toàn (KHÔNG
  phải một official run mới) — theo đúng khuôn `CHECK-B1-03` Addendum 3 |
| **MISSING_INPUT** | Không tính được trong sandbox agent vì thiếu dataset official — chờ Owner |
| **SMOKE (KHÔNG PHẢI EVIDENCE)** | Chạy trên dataset SYNTHETIC chỉ để xác nhận script không lỗi
  cú pháp/API — số liệu tuyệt đối không được dùng làm kết luận |

---

## 1. RQ-2 — Buy Score có kỹ năng timing ở mức vốn triển khai bằng nhau không?

**Không chạy gì mới** — dùng lại evidence đã canonical tại `WP-B1`
(`docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md::CHECK-B1-03` Addendum 3), theo đúng
chỉ thị Owner.

**[O]** Post-`F-017` WP-B1 Evidence Replay (Owner-supplied, đã canonicalize):

    dataset_hash    = 3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5
    master_seed     = 42, n_sims = 1000
    v2_eth          = 14.910758150139896 (khớp frozen official)
    control_f_p95   = 14.887400583487747   -> beats_f = true
    control_g_p95   = 14.813546903782814   -> beats_g = true
    FS-08 (post-F-017) = FALSE

**Diễn giải bắt buộc theo đúng chỉ thị Owner — KHÔNG được vượt quá:**
- V2 vượt P95 của cả hai control **ở mức AGGREGATE toàn kỳ pre-OOS+OOS** (một con số gộp).
- BT §251 (nguyên văn): *"Control F đo lẫn cả hiệu ứng cơ học của việc điều kiện hóa trên giá đã
  giảm, chứ không thuần kỹ năng dự báo."* Vượt P95 vì vậy **KHÔNG chứng minh** kỹ năng dự báo giá.
- Biên vượt mỏng: +0,157 % so với Control F P95 (`14,910758 / 14,887401 − 1 ≈ 0,00157`).
- Đây là **MỘT** cấu hình baseline, không phải quét toàn bộ manifest Gate 2/Gate 3.

### 1.1 CẬP NHẬT sau replay RQ-3 (REPLAY, Owner-run, `docs/reviews/T07-RQ-REPLAY-EVIDENCE-RECORD.md`)

Phân rã theo window/OOS (RQ-3, §4) nay có sẵn và **làm YẾU đi đáng kể** ấn tượng "có timing edge"
mà con số aggregate một mình gợi ý:

- Chỉ **2/9 window pre-OOS** (`W1`, `W4`) vượt Control F P95 — **22 %**.
- Chỉ **3/9 window pre-OOS** (`W1`, `W4`, `W6`) vượt Control G P95 — **33 %**.
- **`OOS` — giai đoạn kiểm định thật sự (forward-test) — THUA cả Control F lẫn Control G, ở CẢ
  median LẪN P95** (bốn phép so đều âm). Đây là kết quả period QUAN TRỌNG NHẤT để đánh giá "có
  edge hay không" (pre-OOS window được dùng để chọn/kiểm chiến lược, OOS mới là kiểm định độc
  lập), và ở đúng period đó, V2 không những không vượt P95 mà còn thua cả **median** của cả hai
  random control.

**Đúng theo guardrail bắt buộc**: kết quả vượt P95 ở mức AGGREGATE **KHÔNG được nâng cấp** thành
"đã chứng minh có kỹ năng dự báo" khi per-window/OOS không ủng hộ phát biểu mạnh đó — và ở đây,
per-window/OOS **không ủng hộ**, thậm chí đi ngược lại ở OOS.

**Kết luận RQ-2 (CẬP NHẬT — vẫn PARTIALLY ESTABLISHED, nhưng thu hẹp và làm rõ)**: sự kiện hẹp
"V2 vượt P95 ở mức AGGREGATE toàn kỳ" vẫn ĐÚNG (đã reproduce bit-for-bit, không đổi). Nhưng phát
biểu rộng hơn mà RQ-2 thực sự hỏi — "Buy Score có kỹ năng timing ở mức vốn triển khai bằng nhau"
như một tính chất ỔN ĐỊNH/khái quát — **KHÔNG được evidence hỗ trợ**: chỉ 2-3/9 window cho thấy
dấu hiệu đó, và period kiểm định độc lập (`OOS`) cho kết quả NGƯỢC LẠI hoàn toàn (thua ở cả bốn
phép so). Xem §9 mục 5 để giải thích vì sao aggregate-thắng và window/OOS-đa-số-thua **không mâu
thuẫn nhau về mặt kỹ thuật** (khác engine-run scope, xem chi tiết).

---

## 2. RQ-5 — Evidence hiện có hỗ trợ đến đâu việc phân biệt "thiếu timing edge" và "objective/
capital-allocation mismatch"?

Đây là câu hỏi **tổng hợp** — trả lời được ngay bằng evidence đã canonical, **không cần dataset
official mới** (không script, không rerun).

### 2.1 FACTS đã thiết lập, liên quan trực tiếp tới câu hỏi

- **F-A** Gate 1 FAIL (PrimaryMedian AE 97,48 % < 102) và OOS FAIL (AE 92,94 % < 100) — V2 tích
  luỹ ÍT ETH hơn benchmark cả hai chế độ dữ liệu. (`T06_OFFICIAL_EVIDENCE_RECORD.md` §6.2)
- **F-B** Gate 2 = 0,00 % — **không config nào trong 219 config đã đóng băng** vượt ngưỡng. Đây
  là bằng chứng MẠNH rằng thất bại **không phải "chọn sai tham số trong không gian đã khai"** —
  toàn bộ neighborhood tham số đã thử đều thất bại như nhau.
- **F-C** FS-02 = TRUE, `opportunity_cap_hit_share = 0,8961` — Opportunity reserve chạm cap và
  **nằm im** ở 89,61 % số quan sát. Đây là bằng chứng trực tiếp về **capital sitting idle** —
  tức một phần vốn không tham gia đầu tư trong phần lớn thời gian.
- **F-D** FS-07 = FALSE với ngưỡng `avg_cash_ratio > 0,30 AND gate1_primary_ae < 102,0`; vì
  `AE = 97,48 < 102` đúng, FS-07 = FALSE **buộc về mặt logic** `avg_cash_ratio ≤ 0,30` — tức tỷ
  lệ tiền mặt trung bình so với portfolio KHÔNG cao (dưới 30 %), dù reserve nội bộ (F-C, đo trên
  `Pool` riêng của Opportunity Fund, không phải tổng portfolio) thường chạm cap.
- **F-E** RQ-2 (§1): V2 vượt P95 Control F/G ở AGGREGATE toàn kỳ, biên mỏng (+0,157 %), với
  caveat BT §251 rằng phép so này đo lẫn hiệu ứng cơ học lẫn kỹ năng dự báo — **không phải bằng
  chứng đã chứng minh không có edge, cũng không phải bằng chứng đã chứng minh có edge mạnh**.
- **F-F** FS-01 = TRUE — V2 tích luỹ ít ETH hơn Monthly DCA ở phần lớn gate window (benchmark
  đơn giản nhất, không có logic phân bổ vốn động).

### 2.2 INTERPRETATIONS (suy luận, không phải đo lường)

- **I-A** F-B (Gate 2 = 0,00 %) là bằng chứng gián tiếp nghiêng về phía **"thất bại mang tính hệ
  thống"** hơn là "một hypothesis đúng nhưng chọn nhầm tham số" — nếu chỉ là vấn đề tham số, một
  phần đáng kể trong 219 config lân cận baseline lẽ ra phải PASS.
- **I-B** F-C (reserve chạm cap 89,61 % và nằm im) + F-D (`avg_cash_ratio ≤ 0,30` ở tầng
  portfolio) cùng chỉ ra: vấn đề **không phải "giữ quá nhiều tiền mặt tổng thể"** (F-D bác bỏ) mà
  là **cấu trúc phân bổ nội bộ của Opportunity Fund** — vốn dành riêng cho cơ hội bị khoá/nằm im
  thay vì được tái phân bổ. Đây nghiêng về phía **capital-allocation mismatch trong CÁCH cấu trúc
  reserve**, không phải "giữ tiền mặt nói chung".
- **I-C** F-E (V2 vượt P95 aggregate, biên mỏng, với caveat cơ học) là bằng chứng **YẾU và không
  đủ** để kết luận về hướng nào trong hai hướng của RQ-5: nó không loại trừ "thiếu timing edge"
  (biên quá mỏng, có thể là hiệu ứng cơ học) nhưng cũng không xác nhận "có mismatch" (nó KHÔNG đo
  objective/capital-allocation, nó đo timing).
- **I-D** F-F (thua cả Monthly DCA — logic phân bổ đơn giản nhất) là dấu hiệu đáng chú ý: nếu một
  chiến lược PHỨC TẠP HƠN (V2, có logic động) thua một benchmark KHÔNG có logic phân bổ động ở
  phần lớn window, điều đó nghiêng nhẹ về phía **cấu trúc phân bổ vốn (objective/capital
  treatment) là một phần của vấn đề** — không chỉ đơn thuần "thiếu kỹ năng dự báo giá timing".

### 2.3 Kết luận RQ-5 — mức độ được thiết lập

**PARTIALLY ESTABLISHED — nghiêng có chứng cứ về phía "capital-allocation/objective mismatch góp
phần", nhưng KHÔNG loại trừ được "cũng thiếu timing edge", và KHÔNG có phép đo nào tách bạch
tách rời hai thành phần này bằng một con số duy nhất.**

Cụ thể:
- Bằng chứng hiện có (F-B, F-C, F-D, F-F) nghiêng về hướng: **một phần đáng kể của thất bại nằm ở
  cách vốn được cấu trúc/phân bổ** (Opportunity Fund reserve, không phải cash tổng thể) —
  KHÔNG NHẤT THIẾT ở việc thiếu khả năng dự báo giá.
- Bằng chứng RQ-2/F-E (Control F/G) **không đủ mạnh** để nói ngược lại rằng "hoàn toàn không có
  timing edge" — biên vượt P95 dù mỏng vẫn tồn tại ở mức aggregate.
- **KHÔNG có evidence nào tách được hai thành phần bằng một con số phân rã duy nhất** (ví dụ:
  "X điểm AE mất vì objective sai, Y điểm AE mất vì thiếu timing edge"). Yêu cầu đó vượt quá
  những gì BT §17 đo (12 Failure Signal là chẩn đoán từng mặt riêng lẻ, không phải một phép quy
  trách nhiệm tổng hợp).
- RQ-1/RQ-3/RQ-4 (§3-§5 dưới đây), khi có output official, sẽ bổ sung bằng chứng — đặc biệt RQ-4
  (phân rã ETH theo nguồn SMART/OPPORTUNITY/CRASH/BASE) trực tiếp đo mức đóng góp và hiệu quả
  giá của phần vốn chịu trách nhiệm cho "mismatch" nghi ngờ ở I-B.

**Điều RQ-5 KHÔNG kết luận**: không đủ căn cứ để nói "V2.1.5 có timing edge thật" hay "V2.1.5
hoàn toàn không có timing edge" — cả hai đều là diễn giải quá mức so với evidence hiện có.

### 2.4 CẬP NHẬT sau replay RQ-1/RQ-3/RQ-4 (REPLAY, `T07-RQ-REPLAY-EVIDENCE-RECORD.md`)

Ba mảnh evidence mới (§3-§5 dưới đây, tóm tắt số liệu ở §9) làm SẮC NÉT thêm §2.3, theo hai
hướng riêng biệt — **không đảo ngược kết luận PARTIALLY ESTABLISHED, nhưng thu hẹp KHÔNG GIAN
GIẢI THÍCH đáng kể**:

- **F-G (mới)** RQ-3 replay: chỉ 2-3/9 window pre-OOS vượt P95, và `OOS` thua CẢ HAI control ở
  CẢ median lẫn P95 (§1.1, §9 mục 1-4). Đây là bằng chứng MỚI, cụ thể hơn F-E, và nó nghiêng rõ
  hơn về phía **LÀM YẾU** giả thuyết "có timing edge ổn định" — không chỉ "chưa đủ mạnh để xác
  nhận" như F-E đã nói, mà giờ có bằng chứng TRỰC TIẾP đi ngược lại ở đúng period kiểm định độc
  lập nhất (`OOS`).
- **F-H (mới)** RQ-4 replay: `OPPORTUNITY` + `CRASH` gộp lại chỉ chiếm **1,56 %** tổng vốn danh
  nghĩa đã triển khai (`14,54 + 128,03` trên tổng `9.160,05`) và **3,20 %** tổng ETH tích luỹ,
  dù giá mua bình quân của hai nguồn này (`345,37` và `294,55`) thấp hơn rõ rệt so với
  `SMART`/`BASE` (`648,16`/`603,78`). Đồng thời, Opportunity pool có `mean_idle_ratio = 0,5917`
  — tức trung bình **59,17 % CAP CỦA RIÊNG POOL ĐÓ** (KHÔNG phải 59,17% tiền mặt toàn danh mục —
  xem phân biệt bắt buộc ở §5) nằm chưa dùng, và `at_cap_share = share = 0,9679` (hai số bằng
  NHAU — mọi lần chạm cap trong replay này đều đồng thời nằm im). Đây là bằng chứng CỤ THỂ (quy
  mô + chất lượng giá) cho nghi vấn cấu trúc phân bổ ở I-B — cơ chế "mua rẻ khi có cơ hội" hoạt
  động ĐÚNG HƯỚNG về mặt giá, nhưng **quy mô vốn thực sự chảy qua kênh đó quá nhỏ** để có thể tạo
  ảnh hưởng vật chất lên AE toàn danh mục, VÀ phần lớn vốn phân bổ cho kênh đó không được dùng.
- **F-I (mới)** RQ-1 replay: tương quan QUAN SÁT giữa cash_ratio trung bình và AE theo 9 window
  là **DƯƠNG** (`pearson=+0,546`, `spearman=+0,5`) — chiều NGƯỢC với một câu chuyện đơn giản
  "tiền mặt nằm im gây ra AE thấp" (nếu đúng vậy, tương quan phải ÂM). Đây **KHÔNG PHẢI** bằng
  chứng nhân quả (n=9, window chồng lấn, không có counterfactual) và **KHÔNG được** diễn giải là
  "tiền mặt giúp ích" hay "tiền mặt gây hại" — nhưng nó làm cho câu chuyện nhân quả đơn giản
  "reserve/cash → AE thấp" trở nên KÉM THUYẾT PHỤC HƠN so với trước khi có số liệu này (trước đó
  hoàn toàn MISSING_INPUT, không có gì để đối chiếu).

**Kết luận RQ-5 (CẬP NHẬT)**: vẫn **PARTIALLY ESTABLISHED** — vẫn không có một phép đo tách bạch
hai thành phần bằng một con số duy nhất, và câu hỏi nhân quả gốc vẫn NOT ESTABLISHED. Nhưng ba
mảnh evidence mới cùng chiều làm bức tranh SẮC NÉT hơn nhiều so với trước: bằng chứng nghiêng
RÕ RÀNG HƠN về phía **cấu trúc/quy mô phân bổ vốn của Opportunity Fund là một yếu tố góp phần cụ
thể, đo được** (F-H), ĐỒNG THỜI bằng chứng cũng nghiêng RÕ RÀNG HƠN về phía **KHÔNG có timing
edge ổn định** (F-G, đặc biệt tại OOS) — tức CẢ HAI vế của RQ-5 đều nhận thêm bằng chứng, không
phải chỉ một vế. Xem §10 (Decision Impact) cho đánh giá đầy đủ.

---

## 3. RQ-1 — Cách xử lý reserve/cash có ảnh hưởng vật chất tới AE không?

**MISSING_INPUT** trong sandbox agent (không có dataset official). Thiết kế REPLAY dưới đây tính
**tương quan quan sát mô tả** giữa `cash_ratio` trung bình và AE, theo từng window trong 9 gate
window — **KHÔNG PHẢI phép đo nhân quả**: câu hỏi nhân quả thật ("nếu đổi cách xử lý reserve thì
AE đổi bao nhiêu") đòi hỏi một counterfactual run với `StrategyConfig`/`ExecutionConfig` khác —
bị cấm tường minh bởi ranh giới Owner (`không sửa strategy/threshold`). Vì vậy câu hỏi nhân quả
của RQ-1 **giữ nguyên NOT ESTABLISHED** cho tới khi Owner uỷ quyền một phiên counterfactual riêng
(nếu có).

Phần quan sát được (tương quan mô tả, script §6 mục RQ-1):
- Trích `cash_ratio_stats(result)["avg"]` và `ae` cho từng W1..W9 (đã có sẵn hạ tầng từ
  `window_metrics`/`run_gate1`, không cần công thức mới).
- Tính Pearson `r` và Spearman `ρ` giữa 9 cặp (`cash_ratio_avg`, `ae`).

### 3.1 REPLAY — kết quả thật (Owner-run, dataset official, `T07-RQ-REPLAY-EVIDENCE-RECORD.md`)

    per_window_cash_ratio_avg = {W1:0,1317, W2:0,1467, W3:0,1610, W4:0,1375, W5:0,1676,
                                  W6:0,1061, W7:0,1500, W8:0,1200, W9:0,1351}
    per_window_ae             = {W1:98,24, W2:97,88, W3:92,97, W4:99,94, W5:100,97,
                                  W6:92,99, W7:101,16, W8:85,86, W9:94,88}
    pearson_r  = +0,5462761737147702
    spearman_r = +0,5

**Diễn giải bắt buộc (KHÔNG được vượt quá)**:
- Đây là **tương quan quan sát trên 9 window CHỒNG LẤN** (các anchor set 0/6/12/18 tháng chia sẻ
  nhiều tháng chung) — KHÔNG phải 9 mẫu độc lập, và KHÔNG PHẢI bằng chứng nhân quả.
- **KHÔNG được diễn giải** thành "tiền mặt/reserve cải thiện hiệu năng" — chiều DƯƠNG không
  chứng minh cash có lợi, nó chỉ là một tương quan observational với n hiệu dụng nhỏ.
- **KHÔNG được diễn giải** thành "tiền mặt/reserve gây ra thất bại AE" — nếu có bất kỳ diễn giải
  nhân quả đơn giản nào theo hướng "cash nằm im → AE thấp", tương quan phải ÂM; ở đây nó DƯƠNG,
  tức dữ liệu **không ủng hộ** câu chuyện nhân quả đơn giản đó theo chiều đó, và **cũng không
  chứng minh chiều ngược lại** — không có counterfactual run nào được thực hiện.
- Đây là **portfolio-level cash_ratio** (`cash / (cash + eth*price)`, đo trên TOÀN danh mục) —
  KHÔNG được nhầm với `mean_idle_ratio` của riêng Opportunity pool (§5.1) — hai đại lượng khác
  nhau, khác mẫu số, khác độ lớn (xem phân biệt bắt buộc ở §5).

**Trạng thái RQ-1**: câu hỏi NHÂN QUẢ gốc ("cách xử lý reserve/cash có ảnh hưởng vật chất tới AE
không") **vẫn NOT ESTABLISHED** — trả lời nó đòi hỏi một counterfactual run (đổi
`StrategyConfig`/`ExecutionConfig`), bị cấm tường minh trong ranh giới `DEC-039`. Phần quan sát
mô tả (tương quan) nay **có số liệu thật** (không còn MISSING_INPUT) nhưng bản thân số liệu đó
**không xác lập được** hướng nhân quả nào — chỉ cho thấy hướng nhân quả "cash đơn thuần gây hại"
là kém hợp lý hơn trước khi có số liệu này (không loại trừ hoàn toàn, không xác nhận).

---

## 4. RQ-3 — Control F theo từng W1-W9 và OOS (thay vì chỉ số aggregate)

**MISSING_INPUT** trong sandbox agent. Thiết kế REPLAY (script §6 mục RQ-3): với mỗi window
`W1..W9` (`windows.gate_windows()`) và riêng `OOS`, xây `monthly_tranches` CHỈ từ các purchase
thật sự nằm trong window đó (không dùng lại `monthly_tranches` toàn kỳ), gọi
`random_timing_control`/`random_anchor_control` (n_sims=1000, master_seed=42 — ĐÚNG tham số đã
đóng băng, không đổi) trên đúng khoảng `[window.start, window.end)`, so `v2_eth` của window đó
với `p95`.

**Bắt buộc trước khi tin kết quả**: script tự động reproduce con số aggregate toàn kỳ đã biết
(`v2_eth = 14,910758150139896`, `control_f_p95 = 14,887400583487747`,
`control_g_p95 = 14,813546903782814`) bit-for-bit ở STEP 0 trước khi in bất kỳ số per-window nào;
nếu không khớp, script DỪNG và in `STEP_0: FAIL`.

**Smoke test PASS** trên dataset SYNTHETIC — script chạy hết 9 window + OOS, không lỗi, mỗi
window trả về `v2_eth`/`control_f_p95`/`control_g_p95`/`beats_f`/`beats_g` đúng kiểu (xem log
đầy đủ ở §7). **Không có kết luận nào rút ra từ số synthetic.**

### 4.1 REPLAY — kết quả thật (Owner-run, dataset official, `T07-RQ-REPLAY-EVIDENCE-RECORD.md`)

`STEP_0 = PASS` (reproduce bit-for-bit). Toàn văn JSON đã bảo toàn tại
`T07-RQ-REPLAY-EVIDENCE-RECORD.md` §1, 10/10 boolean đã tái kiểm tra khớp số học (§2 của file
đó). Bảng tóm tắt:

| Window | `v2_eth` | Control F P95 | beats F | Control G P95 | beats G |
|---|---|---|---|---|---|
| W1 | 11,7983 | 11,7713 | **true** | 11,7017 | **true** |
| W2 | 1,1901 | 1,2039 | false | 1,1971 | false |
| W3 | 1,0361 | 1,0501 | false | 1,0494 | false |
| W4 | 8,4643 | 8,4500 | **true** | 8,3921 | **true** |
| W5 | 1,2228 | 1,2483 | false | 1,2499 | false |
| W6 | 5,1466 | 5,1676 | false | 5,1463 | **true** (biên rất mỏng, +0,0003) |
| W7 | 1,3691 | 1,3987 | false | 1,4017 | false |
| W8 | 2,0887 | 2,1643 | false | 2,1542 | false |
| W9 | 1,2713 | 1,2820 | false | 1,2812 | false |
| **OOS** | 0,7945 | P95=0,8159 / P50=0,8045 | **false (cả P95 lẫn P50)** | P95=0,8141 / P50=0,8041 | **false (cả P95 lẫn P50)** |

**Đếm chính xác** (yêu cầu bắt buộc của mission): **2/9 window pre-OOS vượt Control F P95** (`W1`,
`W4`); **3/9 window pre-OOS vượt Control G P95** (`W1`, `W4`, `W6`). `OOS` thua CẢ HAI control ở
CẢ HAI ngưỡng (median VÀ P95) — không có phép so nào trong bốn phép so của `OOS` là thắng.

**Diễn giải bắt buộc**: kết quả AGGREGATE (§1, V2 vượt P95 toàn kỳ) **KHÔNG được nâng cấp** thành
"đã chứng minh có kỹ năng dự báo giá ổn định" — per-window/OOS ở đây **không ủng hộ** phát biểu
đó: đa số window (7/9) không vượt Control F P95, đa số (6/9) không vượt Control G P95, và `OOS`
— period kiểm định độc lập duy nhất — thua tuyệt đối cả bốn phép so.

**Vì sao aggregate-thắng và window/OOS-đa-số-thua KHÔNG mâu thuẫn nhau (giải thích kỹ thuật,
không phải diễn giải chiến lược)**: đây là hai PHÉP TÍNH khác nhau về mặt cấu trúc, không phải
"tổng" và "thành phần" của cùng một phép tính.
1. **Khác phạm vi run engine.** Con số AGGREGATE (§1) đến từ **một lần chạy `run_engine` liên tục
   duy nhất** từ `2019-01-01` tới `oos_end` — vốn/ladder/regime KHÔNG reset giữa chừng. Con số
   PER-WINDOW (bảng trên) đến từ **chín lần chạy `run_engine` ĐỘC LẬP**, mỗi lần bắt đầu lại từ
   đầu tại `window.start` riêng của nó (đúng phương pháp luận multi-anchor của BT §4.1/§8 —
   `window_metrics()`/`run_window()`), cộng một lần chạy riêng cho `OOS`. Đây là hai đối tượng
   toán học khác nhau: liên tục-không-reset so với độc lập-reset-nhiều-lần — không có quan hệ
   "tổng = tổng các phần" giữa chúng.
2. **Ngay cả khi bỏ qua (1)**, về mặt thống kê thuần t, một chiến lược có thể thắng ở tổng gộp
   trong khi thua ở đa số cửa sổ con nếu lợi thế TẬP TRUNG mạnh vào một vài giai đoạn (ở đây rõ
   ràng là `W1`/`W4`, biên thắng lớn: `W1` thắng F 2,3 %, `W4` thắng F 1,7 %) trong khi các cửa
   sổ còn lại thua sát nút hoặc rõ ràng. Đây không phải nghịch lý — nó CHÍNH XÁC là lý do BT §4.1
   dùng `PrimaryMedian` (không phải tổng/trung bình) để đo AE chính thức, và tương tự là lý do
   phân rã theo window có giá trị chẩn đoán riêng mà con số aggregate một mình che khuất.

**Trạng thái RQ-3**: **ESTABLISHED (như REPLAY evidence)** — câu hỏi gốc ("Control F/G theo từng
W1-W9 và OOS trông như thế nào, thay vì chỉ số aggregate") nay có câu trả lời đầy đủ, nhất quán
nội bộ, không mâu thuẫn (`T07-RQ-REPLAY-EVIDENCE-RECORD.md` §2). Đây là REPLAY (không phải
official Gate 1 record) nhưng dùng đúng tham số đã đóng băng (`n_sims=1000, master_seed=42`) và
đúng phương pháp luận window của BT §4.1.

---

## 5. RQ-4 — Opportunity Fund tạo optionality đo được hay chủ yếu tạo cash drag?

**MISSING_INPUT** trong sandbox agent cho số liệu THẬT. Thiết kế REPLAY (script §6 mục RQ-4):

1. **Phân rã ETH theo nguồn purchase** (`purchases[].source` — trường sẵn có trong `EngineResult`,
   không phát minh field mới): tổng `nominal`/`eth`/`n`/giá mua bình quân cho từng nguồn
   `BASE`/`SMART`/`OPPORTUNITY`/`CRASH`. Đây đo trực tiếp: Opportunity Fund đóng góp BAO NHIÊU
   ETH so với các nguồn khác, và ở mức giá TRUNG BÌNH nào — nếu giá mua bình quân của
   `OPPORTUNITY` thấp hơn đáng kể so với `SMART`/`BASE` (mua được giá tốt hơn khi cơ hội xuất
   hiện), đó là bằng chứng optionality có giá trị dù khối lượng nhỏ; nếu tỷ trọng ETH từ
   `OPPORTUNITY` không đáng kể VÀ giá mua không tốt hơn, nghiêng về phía cash drag thuần.
2. **Thống kê idle capital đã có sẵn** (`opportunity_cap_hit_share()` — hàm production của
   WP-A5, KHÔNG sửa): `at_cap_share`, `mean_idle_ratio`, `share_idle_ge_1pct_cap`,
   `share_idle_ge_10pct_cap`. FS-02 chính thức (0,8961) chỉ là MỘT trong các số này (`share` —
   `at_cap AND idle` đồng thời); các số phụ trợ đo ĐỘ SÂU của phần nằm im, chưa từng được công
   bố trong `T06_OFFICIAL_EVIDENCE_RECORD.md`.

**Smoke test PASS** trên dataset SYNTHETIC (§7): ví dụ minh hoạ cấu trúc output — trên dữ liệu
synthetic, `OPPORTUNITY` đóng góp 16/547 purchase, 0,0154 ETH / tổng ~22,19 ETH (≈ 0,07 %) với
giá mua bình quân **thấp hơn** `SMART`/`CRASH` nhưng KHÔNG khác biệt nhiều so với `BASE`; đây
**chỉ minh hoạ shape của output, KHÔNG phải kết luận** (dataset synthetic không có regime CRASH
đúng đặc tính giống Binance thật).

### 5.1 REPLAY — kết quả thật (Owner-run, dataset official, `T07-RQ-REPLAY-EVIDENCE-RECORD.md`)

**Phân rã ETH theo nguồn (toàn kỳ 2019-01-01 → oos_end, một lần chạy `run_engine` liên tục —
CÙNG run dùng cho STEP 0/aggregate ở §1, KHÔNG phải chín run per-window của §4.1):**

| Nguồn | Số lệnh | Nominal (đơn vị tiền) | % tổng nominal | ETH tích luỹ | % tổng ETH | Giá mua bình quân |
|---|---|---|---|---|---|---|
| `BASE` | 276 | 4.600,00 | 50,22 % | 7,6186 | 51,09 % | 603,78 |
| `SMART` | 221 | 4.417,49 | 48,23 % | 6,8154 | 45,71 % | 648,16 |
| `CRASH` | 20 | 128,03 | 1,40 % | 0,4346 | 2,92 % | **294,55** |
| `OPPORTUNITY` | 20 | 14,54 | 0,16 % | 0,0421 | 0,28 % | **345,37** |
| **Tổng** | 537 | 9.160,05 | 100 % | 14,9108 | 100 % | — |

(Tổng ETH `14,910758150139898` khớp `1,78×10⁻¹⁵` với `v2_eth` aggregate đã biết từ trước — xác
nhận nhất quán độc lập, xem `T07-RQ-REPLAY-EVIDENCE-RECORD.md` §2 mục 5.)

**Thống kê idle capital của riêng Opportunity pool** (`opportunity_cap_hit_share()`, toàn kỳ):

    share (at_cap AND idle đồng thời) = 0,9679   [FS-02 chính thức đã công bố = 0,8961 — khác kỳ đo/lát cắt code, KHÔNG phải cùng một con số, xem cảnh báo dưới]
    at_cap_share                      = 0,9679   (BẰNG NHAU với `share` — mọi lần chạm cap trong replay này đều đồng thời idle)
    mean_idle_ratio                   = 0,5917
    share_idle_ge_1pct_cap            = 1,0
    share_idle_ge_10pct_cap           = 1,0

**⚠ Cảnh báo cần biết**: `share = 0,9679` ở đây (replay, toàn kỳ 2019→oos_end, một run liên tục)
**KHÁC** con số FS-02 chính thức đã công bố (`0,8961`, official Gate 1, tính trên chín window
độc lập rồi gộp bằng PrimaryMedian — `opportunity_cap_hit.per_window` trong `pipeline.run_gate1`,
không phải một run liên tục). Đây là **cùng một hiện tượng đo trên hai phạm vi run khác nhau**
(giống hệt lý do ở §4.1 mục "khác phạm vi run engine"), **KHÔNG phải bằng chứng đối lập với FS-02
official** — cả hai đều hợp lệ trong phạm vi của chính chúng, và cả hai đều xác nhận cùng một kết
luận định tính: reserve chạm cap và nằm im ở phần lớn tuyệt đối thời gian quan sát (>89 % theo cả
hai phép đo).

**Phân biệt BẮT BUỘC (theo đúng guardrail Owner) — hai đại lượng, hai mẫu số, hai độ lớn:**

| | `cash_ratio_full_period.avg` (§3) | `mean_idle_ratio` (mục này) |
|---|---|---|
| Mẫu số | **TOÀN DANH MỤC** (`cash + eth×price`) | **CAP CỦA RIÊNG Opportunity pool** |
| Giá trị | **0,0369** (3,69 %) | **0,5917** (59,17 %) |
| Ý nghĩa | Tỷ lệ tiền mặt trên TOÀN portfolio | Tỷ lệ vốn `available` chưa dùng SO VỚI trần riêng của MỘT sub-pool nhỏ |

**KHÔNG được đọc `mean_idle_ratio = 0,5917` thành "59,17 % tiền mặt toàn danh mục"** — đó là một
con số hoàn toàn khác, đo trên một mẫu số nhỏ hơn nhiều bậc (Opportunity pool chỉ từng triển khai
`14,54` trên tổng `9.160,05`, tức `0,16 %` tổng vốn).

**Diễn giải bắt buộc (KHÔNG được vượt quá — theo đúng guardrail G của mission)**:
- Giá mua bình quân của `OPPORTUNITY` (345,37) và `CRASH` (294,55) **thấp hơn rõ rệt** so với
  `SMART`/`BASE` (648,16/603,78) — về mặt HƯỚNG, đây là bằng chứng cơ chế "mua rẻ hơn khi có cơ
  hội/crash" hoạt động ĐÚNG THIẾT KẾ định tính.
- Nhưng **giá thấp một mình KHÔNG chứng minh giá trị ở tầng portfolio** — phải xét cùng QUY MÔ
  vốn triển khai: `OPPORTUNITY + CRASH` gộp lại chỉ **1,56 % tổng nominal** và **3,20 % tổng ETH**.
  Dù mỗi đơn vị vốn qua hai kênh này mua được ETH rẻ hơn ~1,7-2,2 lần so với `SMART`/`BASE`, tổng
  khối lượng đi qua đó quá nhỏ để có thể tạo chênh lệch AE vật chất ở cấp portfolio.
- Đồng thời, phần lớn vốn được CẤP cho Opportunity pool (đo qua `mean_idle_ratio`/`at_cap_share`)
  **không được triển khai** — tức pool này vừa triển khai RẤT ÍT vốn (quy mô nhỏ) vừa giữ phần
  lớn vốn được cấp trong trạng thái nằm im (không tận dụng ngay cả trong phạm vi nhỏ của chính
  nó). Hai sự kiện này **cùng tồn tại, không loại trừ nhau**: cơ chế giá đúng hướng NHƯNG bị giới
  hạn kép bởi (a) quy mô phân bổ quá nhỏ và (b) tỷ lệ sử dụng nội bộ thấp.

**Trạng thái RQ-4**: **PARTIALLY ESTABLISHED** — nay có bằng chứng REPLAY cụ thể về CẢ quy mô lẫn
chất lượng giá của Opportunity Fund (trước đây chỉ có FS-02 official, một con số duy nhất). Bằng
chứng ủng hộ đồng thời cả hai vế của câu hỏi gốc theo cách không loại trừ nhau: cơ chế "mua rẻ"
có tín hiệu định tính đúng hướng (không phải thuần cash drag vô nghĩa), NHƯNG quy mô + tỷ lệ nằm
im cho thấy nó chưa tạo được optionality VẬT CHẤT ở cấp portfolio. KHÔNG có phép đo giá trị ròng
(ví dụ đóng góp XIRR, hay counterfactual với vốn phân bổ khác) để kết luận ESTABLISHED đầy đủ.

---

## 6. Script REPLAY (KHÔNG sửa `src/` — script sống ngoài production path)

Chạy với `python <script>.py <RAW_DIR> <FROZEN_PATH>` trên máy có dataset official T-06 đã bảo
toàn. `RAW_DIR` = thư mục `data/raw` chứa ba file parquet + `lineage.json` gốc (backup của
Owner). `FROZEN_PATH` = đường dẫn tới `results/random_control_21b7d88e9691_metrics.json` backup
(dùng để verify STEP 0). Yêu cầu môi trường: `pip install -e ".[dev]"` tại đúng `code_commit`
hiện hành của nhánh này (không cần checkout về `5228130` — đây là REPLAY `current HEAD code +
dataset official`, đúng khuôn `CHECK-B1-03` Addendum 3).

**Nếu STEP 0 in `FAIL`: DỪNG NGAY, không dùng bất kỳ số nào phía dưới, báo cáo lại nguyên văn
output cho phiên canonicalize kế tiếp — KHÔNG tự suy diễn.**

```python
"""
T-07 EVIDENCE INVESTIGATION (DEC-039) — RQ-1 / RQ-3 / RQ-4 deterministic replay.

CHỈ chạy trên dataset official T-06 đã bảo toàn (Owner). KHÔNG sửa file này.
KHÔNG phải một official T-06 run mới — đây là READ-ONLY post-hoc analysis trên
cùng engine đã đóng băng, dùng lại đúng hàm production KHÔNG sửa gì. Production
diff của repository = 0 khi chạy script này (script không nằm trong src/).

BẮT BUỘC: nếu STEP 0 (reproduce baseline) không khớp bit-for-bit, DỪNG NGAY —
không dùng bất kỳ số nào dưới đây làm evidence, báo cáo NOT ESTABLISHED.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from eth_dca_os.pipeline import Prepared
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.engine import run_engine, TZ_OFFSET
from eth_dca_os.metrics import window_metrics, oos_metrics, cash_ratio_stats, opportunity_cap_hit_share
from eth_dca_os.benchmarks import random_timing_control, random_anchor_control
from eth_dca_os.windows import gate_windows, OOS_START

RAW_DIR = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
FROZEN_PATH = sys.argv[2] if len(sys.argv) > 2 else "results/random_control_21b7d88e9691_metrics.json"
SMOKE = "--smoke" in sys.argv  # bỏ qua STEP 0 khi chạy trên dataset synthetic (KHÔNG evidence)

MASTER_SEED = 42


def monthly_tranches_of(purchases):
    out = {}
    for p in purchases:
        mk = pd.Timestamp(p["ts"] + TZ_OFFSET, unit="s").strftime("%Y-%m")
        out.setdefault(mk, []).append(p["nominal"])
    return out


def spearman(a, b):
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


prep = Prepared(RAW_DIR)
cfg, exec_cfg = BASELINE_STRATEGY, GATE1_LOW_FRICTION
scores = prep.scores(cfg.score_weights)
start, end = pd.Timestamp("2019-01-01"), prep.oos_end()

full = run_engine(prep.dataset, scores, cfg, exec_cfg, start, end)
full_tranches = monthly_tranches_of(full.purchases)
v2_eth = float(full.eth_total)

f_full = random_timing_control(prep.dataset, full_tranches, start, end, n_sims=1000, master_seed=MASTER_SEED)
g_full = random_anchor_control(prep.dataset, full_tranches, start, end, n_sims=1000, master_seed=MASTER_SEED)

step0 = {
    "v2_eth": v2_eth,
    "control_f_p95": f_full["p95"],
    "control_g_p95": g_full["p95"],
    "beats_f": bool(v2_eth > f_full["p95"]),
    "beats_g": bool(v2_eth > g_full["p95"]),
}

if not SMOKE:
    frozen = json.loads(Path(FROZEN_PATH).read_text())
    ok_v2 = abs(v2_eth - frozen["v2_eth"]) < 1e-6
    ok_f = abs(f_full["p95"] - 14.887400583487747) < 1e-6
    ok_g = abs(g_full["p95"] - 14.813546903782814) < 1e-6
    if not (ok_v2 and ok_f and ok_g):
        print(json.dumps({"STEP_0": "FAIL — KHONG khop official baseline. DUNG. "
                                     "KHONG dung bat ky so nao duoi day lam evidence.",
                           "computed": step0}, indent=2, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({"STEP_0": "PASS — reproduced official baseline bit-for-bit"}, indent=2))
else:
    print(json.dumps({"STEP_0": "SMOKE MODE (synthetic dataset) — KHONG PHAI evidence",
                       "computed": step0}, indent=2))

# ---------------- RQ-3: Control F/G theo tung W1..W9 va OOS ----------------
wm = window_metrics(prep.dataset, scores, cfg, exec_cfg)
rq3 = {}
for w in gate_windows():
    wr = wm["windows"][w.window_id]
    w_start = pd.Timestamp(w.start)
    w_end = pd.Timestamp(w.end) + pd.Timedelta(days=1)
    w_tranches = monthly_tranches_of(wr["result"].purchases)
    if not w_tranches:
        rq3[w.window_id] = {"reason": "no_purchases_in_window"}
        continue
    wf = random_timing_control(prep.dataset, w_tranches, w_start, w_end, n_sims=1000, master_seed=MASTER_SEED)
    wg = random_anchor_control(prep.dataset, w_tranches, w_start, w_end, n_sims=1000, master_seed=MASTER_SEED)
    v2 = float(wr["result"].eth_total)
    rq3[w.window_id] = {
        "v2_eth": v2, "control_f_p50": wf["p50"], "control_f_p95": wf["p95"],
        "control_g_p50": wg["p50"], "control_g_p95": wg["p95"],
        "beats_f": bool(v2 > wf["p95"]), "beats_g": bool(v2 > wg["p95"]),
    }

oos = oos_metrics(prep.dataset, scores, cfg, exec_cfg, prep.oos_end())
oos_result = oos["detail"]["result"]
oos_tranches = monthly_tranches_of(oos_result.purchases)
if oos_tranches:
    oos_start_ts = pd.Timestamp(OOS_START)
    oos_end_ts = pd.Timestamp(prep.oos_end()) + pd.Timedelta(days=1)
    of = random_timing_control(prep.dataset, oos_tranches, oos_start_ts, oos_end_ts, n_sims=1000, master_seed=MASTER_SEED)
    og = random_anchor_control(prep.dataset, oos_tranches, oos_start_ts, oos_end_ts, n_sims=1000, master_seed=MASTER_SEED)
    v2_oos = float(oos_result.eth_total)
    rq3["OOS"] = {
        "v2_eth": v2_oos, "control_f_p50": of["p50"], "control_f_p95": of["p95"],
        "control_g_p50": og["p50"], "control_g_p95": og["p95"],
        "beats_f": bool(v2_oos > of["p95"]), "beats_g": bool(v2_oos > og["p95"]),
    }
else:
    rq3["OOS"] = {"reason": "no_purchases_in_oos"}

print(json.dumps({"RQ-3_control_by_window": rq3}, indent=2))

# ---------------- RQ-1: tuong quan mo ta cash_ratio vs AE theo 9 window (KHONG nhan qua) ----------------
cash_by_w = {w: cash_ratio_stats(wm["windows"][w]["result"])["avg"] for w in wm["windows"]}
ae_by_w = wm["ae_by_window"]
common = sorted(set(cash_by_w) & set(ae_by_w))
cash_vals = [cash_by_w[w] for w in common]
ae_vals = [ae_by_w[w] for w in common]
pearson_r = float(np.corrcoef(cash_vals, ae_vals)[0, 1]) if len(common) >= 2 else None
spearman_r = spearman(cash_vals, ae_vals) if len(common) >= 2 else None

print(json.dumps({"RQ-1_cash_vs_ae": {
    "per_window_cash_ratio_avg": cash_by_w,
    "per_window_ae": ae_by_w,
    "pearson_r": pearson_r,
    "spearman_r": spearman_r,
    "n_windows": len(common),
    "CAVEAT": ("TUONG QUAN QUAN SAT tren 9 window CHONG LAN, KHONG PHAI bang chung "
               "nhan qua. Khong counterfactual run nao duoc thuc hien (cam sua "
               "strategy/threshold theo chi thi Owner DEC-039)."),
}}, indent=2))

# ---------------- RQ-4: phan ra ETH theo nguon purchase (source) tren toan ky ----------------
by_source = {}
for p in full.purchases:
    s = p["source"]
    d = by_source.setdefault(s, {"n": 0, "nominal": 0.0, "eth": 0.0})
    d["n"] += 1
    d["nominal"] += p["nominal"]
    d["eth"] += p["eth"]
rq4_by_source = {s: {**d, "avg_price": (d["nominal"] / d["eth"]) if d["eth"] > 0 else None}
                 for s, d in by_source.items()}

opp_stats = opportunity_cap_hit_share(full)
cash_stats = cash_ratio_stats(full)

print(json.dumps({
    "RQ-4_eth_by_source": rq4_by_source,
    "RQ-4_opportunity_cap_hit": opp_stats,
    "RQ-4_cash_ratio_full_period": cash_stats,
}, indent=2))

print(json.dumps({"DONE": True, "SMOKE_MODE": SMOKE}, indent=2))
```

### 6.1 Smoke test đã chạy (sandbox agent, dataset SYNTHETIC, KHÔNG PHẢI evidence)

Lệnh: `python rq_evidence_script.py <synth_raw_dir> "" --smoke`

Kết quả: **exit code 0**, không exception, toàn bộ RQ-1/RQ-3/RQ-4 in ra JSON hợp lệ với kiểu dữ
liệu đúng (`bool` thuần Python cho `beats_f`/`beats_g`, `float` cho mọi số đo — cùng chuẩn
`_flag()`/`float()` mà `F-S015-01` đòi hỏi). Trích đoạn đại diện (KHÔNG PHẢI evidence):

```json
{
  "STEP_0": "SMOKE MODE (synthetic dataset) — KHONG PHAI evidence",
  "computed": {"v2_eth": 22.188701669097636, "control_f_p95": 22.497273082578715,
               "control_g_p95": 22.602527380413928, "beats_f": false, "beats_g": false}
}
```

```json
{"RQ-1_cash_vs_ae": {"pearson_r": 0.3363436281189256, "spearman_r": 0.5, "n_windows": 9}}
```

```json
{"RQ-4_opportunity_cap_hit": {"share": 0.9784435513335769, "at_cap_share": 0.9784435513335769,
                               "mean_idle_ratio": 0.7399426168134015,
                               "share_idle_ge_10pct_cap": 1.0}}
```

Toàn bộ output đầy đủ (RQ-3 9 window + OOS, RQ-4 by-source) đã được xem trong phiên soạn tài
liệu này, không lặp lại toàn văn ở đây (dung lượng lớn, KHÔNG phải evidence nên không cần bảo
toàn bit-for-bit).

---

## 7. Hướng dẫn cho Owner — ĐÃ HOÀN TẤT

Owner đã thực hiện đủ các bước 1-6 dưới đây và cung cấp lại output đầy đủ. Giữ nguyên mục này
làm hồ sơ thủ tục (không xoá) — không còn hành động nào cần Owner làm cho RQ-1/RQ-3/RQ-4 nữa.

1. Trên máy có dataset official T-06 đã bảo toàn (backup `CoinDCA_T06_OFFICIAL_BACKUP`), tại
   đúng `code_commit` của nhánh `claude/t-07-decision-prep-1oprq1` (hoặc HEAD hiện hành sau khi
   merge — script không phụ thuộc thay đổi nào ngoài phạm vi này):
2. `pip install -e ".[dev]"`
3. Lưu script §6 ra file (ví dụ `rq_evidence_script.py`).
4. Chạy: `python rq_evidence_script.py data/raw results/random_control_21b7d88e9691_metrics.json`
5. Nếu `STEP_0: PASS` — dán TOÀN BỘ output còn lại (RQ-1/RQ-3/RQ-4 JSON) vào phiên canonicalize
   kế tiếp. Nếu `STEP_0: FAIL` — dán nguyên output đó, KHÔNG chạy tiếp, KHÔNG tự sửa script.
6. Không cần chạy trên toàn bộ manifest Gate 2/Gate 3 — script chỉ dùng baseline config
   (`BASELINE_STRATEGY` + `GATE1_LOW_FRICTION`), đúng cấu hình mà Gate 1 chính thức đã dùng.

**Kết quả nhận được**: `STEP_0 = PASS`, `SMOKE_MODE = false`. Toàn văn bảo toàn tại
`docs/reviews/T07-RQ-REPLAY-EVIDENCE-RECORD.md`. Xem §9/§10 dưới đây cho tóm tắt định lượng và
đánh giá tác động lên `T-07`.

---

## 8. Tổng hợp trạng thái (CẬP NHẬT sau replay)

| RQ | Trạng thái | Ghi chú |
|---|---|---|
| RQ-1 (nhân quả reserve/cash → AE) | **NOT ESTABLISHED** (không đổi — ngoài phạm vi được phép, cần counterfactual run) | Owner Decision riêng cho phép counterfactual, nếu muốn |
| RQ-1 (tương quan mô tả) | Có số liệu thật — **quan sát KHÔNG PHẢI nhân quả**: `pearson=+0,546`, `spearman=+0,5` | Không upgrade thành nhân quả; xem §3.1 |
| RQ-2 | **PARTIALLY ESTABLISHED** — thu hẹp đáng kể: sự kiện aggregate đứng vững, nhưng "kỹ năng timing ổn định" KHÔNG được ủng hộ (2-3/9 window, `OOS` thua cả bốn phép so) | Xem §1.1 |
| RQ-3 | **ESTABLISHED** (như REPLAY evidence) — phân rã đầy đủ 9 window + OOS, nhất quán nội bộ | Xem §4.1, `T07-RQ-REPLAY-EVIDENCE-RECORD.md` |
| RQ-4 | **PARTIALLY ESTABLISHED** — có bằng chứng cụ thể về quy mô (1,56 % tổng vốn) và chất lượng giá (thấp hơn rõ rệt), không có phép đo giá trị ròng portfolio-level | Xem §5.1 |
| RQ-5 | **PARTIALLY ESTABLISHED** — cả hai vế đều nhận thêm bằng chứng (không phải chỉ một vế); vẫn không có phép đo tách bạch bằng một con số duy nhất | Xem §2.4 |

**Bước tiếp theo**: RQ-1/RQ-3/RQ-4 đã nhận đủ evidence hiện có thể thu thập trong ranh giới đã
cho (RQ-1 causal vẫn chờ một uỷ quyền counterfactual riêng nếu Owner muốn theo đuổi). **Quay lại
`T-07`** để Owner chọn giữa L-1/L-2 (`docs/reviews/T07-OWNER-DECISION-BRIEF.md` §7/§14) — quyết
định đó vẫn PENDING, KHÔNG được đưa ra ở đây.

Tài liệu này KHÔNG phải Owner Decision, KHÔNG đổi verdict, KHÔNG đổi `can_proceed_to_app`, KHÔNG
mở `T-11`/`WP-D2`, KHÔNG resolve `DEC-005`. `T-07` giữ `READY`.

---

## 9. Tóm tắt định lượng bắt buộc (từ số liệu §1/§4.1/§5.1, không tính lại gì mới)

1. **Số window W1-W9 vượt Control F P95**: **2/9** (`W1`, `W4`).
2. **Số window W1-W9 vượt Control G P95**: **3/9** (`W1`, `W4`, `W6` — biên `W6` rất mỏng, chỉ
   `+0,0003`).
3. **Danh sách chính xác**: F = `{W1, W4}`; G = `{W1, W4, W6}`.
4. **`OOS` so với Control F/G, cả median lẫn P95** — **THUA CẢ BỐN**:
   - `OOS` vs Control F median (`0,7945` vs `0,8045`): **thua**.
   - `OOS` vs Control F P95 (`0,7945` vs `0,8159`): **thua**.
   - `OOS` vs Control G median (`0,7945` vs `0,8041`): **thua**.
   - `OOS` vs Control G P95 (`0,7945` vs `0,8141`): **thua**.
5. **Aggregate post-`F-017` (thắng cả hai P95) và per-window/OOS (đa số thua) có mâu thuẫn nhau
   không?** **KHÔNG** — xem giải thích đầy đủ ở §4.1 ("Vì sao aggregate-thắng và
   window/OOS-đa-số-thua KHÔNG mâu thuẫn nhau"): (a) hai phép tính dùng phạm vi `run_engine` khác
   nhau về cấu trúc (một run liên tục 2019→oos_end, không reset, so với chín run độc lập tự
   reset tại từng `window.start` + một run OOS riêng — đúng phương pháp luận BT §4.1/§8, KHÔNG
   phải một lỗi hay một điều chỉnh tuỳ tiện); (b) ngay cả bỏ qua (a), thắng ở tổng gộp trong khi
   thua ở đa số cửa sổ con là hiện tượng thống kê bình thường khi lợi thế tập trung mạnh ở một
   vài giai đoạn (đây chính xác là lý do BT §4.1 bắt buộc dùng `PrimaryMedian` — không phải tổng
   — để đo AE chính thức).
6. **Tóm tắt SMART/BASE/OPPORTUNITY/CRASH** (bảng đầy đủ ở §5.1): `BASE` 276 lệnh/4.600,00
   nominal/7,6186 ETH/giá BQ 603,78; `SMART` 221 lệnh/4.417,49/6,8154/648,16; `CRASH` 20
   lệnh/128,03/0,4346/294,55; `OPPORTUNITY` 20 lệnh/14,54/0,0421/345,37. `OPPORTUNITY+CRASH`
   gộp = 1,56 % tổng nominal, 3,20 % tổng ETH — giá mua thấp hơn rõ rệt (294-345 so với 604-648)
   nhưng ở quy mô rất nhỏ.
7. **Diễn giải Opportunity cap metrics, KHÔNG lẫn với tổng portfolio cash** (chi tiết §5.1): `mean_idle_ratio = 0,5917` là **59,17 % CAP CỦA RIÊNG Opportunity pool** (một sub-pool chỉ từng
   triển khai 0,16 % tổng vốn), **KHÔNG PHẢI** 59,17 % tiền mặt toàn danh mục — con số tiền mặt
   toàn danh mục là `cash_ratio_full_period.avg = 0,0369` (3,69 %), một đại lượng khác hẳn về
   mẫu số và độ lớn.

---

## 10. Tác động tới quyết định `T-07` (Decision Impact)

**Evidence mới có làm đổi diễn giải khả dụng cho `T-07` không? CÓ — làm SẮC NÉT, KHÔNG làm đổi
bất kỳ trạng thái đóng băng nào** (`verdict`, `can_proceed_to_app`, `V2.1.5 validation` — tất cả
giữ nguyên tuyệt đối, xem §11 STATE PRESERVATION bên dưới).

**Với giả thuyết "V2.1.5 có timing edge ổn định":** evidence mới **LÀM YẾU ĐI** (weakens). Trước
replay, mức đánh giá chỉ dựa trên MỘT con số aggregate (thắng P95 cả hai control, biên mỏng
+0,157 %). Sau replay: chỉ 2-3/9 window pre-OOS cho thấy dấu hiệu đó, và `OOS` — period kiểm
định độc lập duy nhất, period gần với "sẽ hoạt động ra sao trong tương lai" nhất — **thua tuyệt
đối** cả hai control ở cả hai ngưỡng. Đây là bằng chứng cụ thể, không phải suy luận, đi ngược lại
hướng "có kỹ năng dự báo ổn định".

**Với giả thuyết "cấu trúc/phân bổ vốn (objective/capital-allocation) góp phần gây ra thất bại
chính thức":** evidence mới **HỖ TRỢ MỘT PHẦN** (partially supports — KHÔNG establish đầy đủ).
Trước replay, bằng chứng chỉ có FS-02 (một con số duy nhất, 0,8961) và suy luận gián tiếp từ đối
chiếu với FS-07. Sau replay: có bằng chứng CỤ THỂ về quy mô (Opportunity+Crash chỉ 1,56 % tổng
vốn) VÀ chất lượng giá (thấp hơn rõ rệt khi có triển khai) VÀ tỷ lệ nằm im nội bộ
(`mean_idle_ratio=0,5917` trên CAP riêng của pool đó). Ba mảnh này cùng khớp với câu chuyện "cơ
chế đúng hướng về mặt giá nhưng bị giới hạn bởi quy mô phân bổ và tỷ lệ sử dụng" — nhưng vẫn
KHÔNG có phép đo giá trị ròng ở cấp portfolio (ví dụ đóng góp AE/XIRR nếu vốn được phân bổ khác
đi) để nói ESTABLISHED đầy đủ.

**RQ-1 (tương quan cash×AE, dương, không nhân quả)** không đẩy mạnh diễn giải nào theo hướng
nhân quả — nó chỉ làm cho một câu chuyện nhân quả ĐƠN GIẢN "tiền mặt/reserve trực tiếp gây ra AE
thấp" trở nên kém thuyết phục hơn (chiều tương quan ngược lại), mà KHÔNG xác lập chiều nhân quả
nào.

**Tóm lại cho `T-07`**: evidence mới không đổi bất kỳ fact đóng băng nào, không giải quyết câu
hỏi objective A/C, không chọn L-1/L-2 — nhưng nó cho Owner một cơ sở SẮC NÉT HƠN nhiều để cân
nhắc khi tự chọn: bằng chứng hiện có nghiêng về phía "thất bại có yếu tố cấu trúc/phân bổ vốn cụ
thể, đo được, KHÔNG chỉ đơn thuần thiếu kỹ năng dự báo" — nhưng KHÔNG đủ để khẳng định V2.1.5 có
edge thật nếu sửa cấu trúc phân bổ, và KHÔNG đủ để khẳng định hoàn toàn không có edge. Việc chọn
L-1 (benchmark đơn giản hơn) hay L-2 (mở V2.2 với hypothesis mới, ví dụ cấu trúc capital khác)
**vẫn là quyết định của Owner** — phiên này không và sẽ không thay Owner chọn.
