# WP-A2 — Bật các hạng mục đã viết nhưng pipeline chưa chạy

## Metadata
Status:
DONE

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED — MANUAL OVERRIDE (HISTORICAL). Sau MICRO-GOVDEF-001 (2026-08-23), `routing_engine.py` tự
tính đúng Tier C cho các Routing Inputs bên dưới mà không cần override — xem ghi chú cuối trường
`Manual Override` và `Router Raw Output`. Giữ nguyên nhãn MANUAL OVERRIDE để không mất dấu vết
DEC-008, đúng yêu cầu của chủ dự án.

Routing Inputs (all integers 0-4):
D: 2
R: 2
B: 2
A: 1
X: 3
U: 1
V: 3
H: 2
C: 3
F: 2

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
high

Manual Override:
YES — DEC-008. Router thô **tại thời điểm phê duyệt DEC-008** trả Tier **B** (Sonnet) vì defect
biên dấu phẩy động GOVDEF-001: `model_score` hiển thị `2.0` nhưng giá trị nội bộ là
`1.9999999999999998`, nên `tier_from_score` (so sánh `s < 2`) rơi vào nhánh B, trong khi
`AGENT_CAPABILITY_MATRIX.md` quy định 2.00–2.99 → C. Effort `high` là giá trị router tính đúng và
**không** bị override.

**Cập nhật sau MICRO-GOVDEF-001 (2026-08-23):** `routing_engine.py` được sửa để làm tròn `model_score`
về cùng độ chính xác với giá trị hiển thị (3 chữ số thập phân) **trước khi** so sánh với các mốc
Tier, thay vì so sánh trên giá trị dấu phẩy động chưa xử lý sai số. Chạy lại router với đúng các
Routing Inputs bên dưới cho **Tier C tự nhiên**, không cần override nữa — xác nhận đúng
`Can Revisit After` của DEC-008. Trường này được **giữ nguyên, không xoá**, làm dấu vết governance:
Tier C của WP-A2 luôn có căn cứ, dù là qua override (trước fix) hay qua routing tự nhiên (sau fix).

Router Raw Output:
tier=B, model=Sonnet, base_tier=B, model_score=2.0, effort=high, effort_score=2.15,
model_floors=none, effort_floors=none, warnings=none

(Giá trị trên là router THÔ tại thời điểm DEC-008, trước MICRO-GOVDEF-001 — giữ nguyên làm bằng
chứng lịch sử của defect GOVDEF-001. Router hiện tại, sau fix, cho: tier=C, model=Opus,
base_tier=C, model_score=2.0, effort=high, effort_score=2.15 — khớp `Primary Agent Tier`/
`Primary Effort` phía trên mà không cần override.)

Model Routing Score:
2.0

Effort Routing Score:
2.15

Applied Model Floor:
none (Tier C đến từ override DEC-008 trước fix; sau MICRO-GOVDEF-001, Tier C đến từ chính router,
vẫn không qua floor nào — xem `Router Raw Output`)

Applied Effort Floor:
none

Routing Warnings:
none. **Lịch sử:** trước MICRO-GOVDEF-001, cảnh báo ở đây là
`manual_override_dec_008 — validate_routing.py hiện so khớp tuyệt đối với router nên sẽ báo FAIL
cho đúng file này`. Điều đó không còn đúng — `validate_routing.py` nay PASS cho file này (xác nhận
E1, xem Ready Gate). Giữ ghi chú lịch sử để không mất dấu vết.

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
xhigh

Difficulty:
2/4

Risk:
2/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Đấu nối vào pipeline chính những hạng mục **đã được cài đặt đúng nhưng không nơi nào gọi**, để một
official run phát ra báo cáo đầy đủ theo đúng những gì spec ghi là bắt buộc.

Đây là gói **đấu nối**, không phải gói thuật toán. Code của benchmark B/C/D, ablation, volume
z-score, coverage table và XIRR đã được S001 đối chiếu và kết luận là đúng spec khi đọc.

## Vì sao gói này ở lớp A

Chỉ **F-004** bị ràng buộc cứng vào lớp A (Strategy §2: "bắt buộc trong mọi official run") và
**F-014** (bootstrap cần purchase record tại thời điểm chạy, không lưu lại được). F-003, F-012,
F-013 về lý thuyết tính lại được từ dataset đã đóng băng. RCP-001 gộp cả năm vào lớp A vì chúng là
**cùng một sửa đổi trong cùng một file** — tách ra sẽ phải chạm `pipeline.py` hai lần cho cùng một
mục đích. Chủ dự án đã phê duyệt cách gộp này (DEC-007 quyết định 2).

Hệ quả nếu không sửa: nguyên tắc trung tâm của Backtest §22 — "luật đơn giản thắng nếu kết quả
tương đương" — **không thể áp dụng**, vì chiến lược V2.1.5 chỉ được so với Benchmark A.

## Đóng finding / risk

- F-003 — Benchmark B, C, D không bao giờ được gọi
- F-004 — ablation §2.3 và volume z-score §2.4 không được chạy
- F-012 — bảng coverage §4 không được sinh
- F-013 — XIRR §16 không được tính
- F-014 — bootstrap chạy `n_sims=200` thay vì 1000 mỗi block length
- RSK-007 — pipeline không chạy nhiều hạng mục spec ghi là bắt buộc

## Scope

- `src/eth_dca_os/pipeline.py` — lời gọi và truyền tham số
- `src/eth_dca_os/diagnostics.py` — đưa `ablation_scores` và `volume_zscore_variant` vào `run_all`
- `src/eth_dca_os/reporting.py` — payload báo cáo official
- `tests/` — test khẳng định payload official chứa đủ các mục bắt buộc

## Out of Scope

- **Sửa công thức** của bất kỳ benchmark, ablation, coverage, XIRR hay bootstrap nào
- Thêm benchmark mới hoặc đổi định nghĩa benchmark hiện có
- Đổi ngưỡng gate, cách sinh manifest, ngày split, giả định ma sát (Master Index §6)
- Sinh hoặc truyền các đại lượng Failure Signal còn thiếu — đó là **WP-A5**
- Quyết định chính sách verdict khi FS UNKNOWN — đó là **WP-B1**
- Sửa `routing_engine.py` / `validate_routing.py`

## Dependencies
- T-04 (DONE)
- ~~**BLK-003**~~ — **RESOLVED** tại `MICRO-GOVDEF-001` (2026-08-23). `validate_routing.py` được
  cập nhật để (a) làm tròn điểm số như `routing_engine.py` trước khi so sánh biên, và (b) chấp nhận
  manual override có ghi nhận (decision reference tồn tại trong `PROJECT_DECISIONS.md`, Router Raw
  Output xác thực, và chỉ được leo thang Tier/Effort chứ không được hạ). Sau fix, WP-A2 route Tier C
  **tự nhiên**, không cần nhánh override nữa. Rủi ro nền **GOV-RSK-001** đã đóng cùng lúc.
  Bằng chứng: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` (mục Resolution),
  `governance/scripts/governance/test_routing_engine.py`.

## Blocks
- WP-A5 (cần benchmark/diagnostic được chạy để đo đủ dữ liệu)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-A3, WP-C1, WP-D1, WP-D2
- **Không song song với WP-A5**: cả hai sửa `pipeline.py`, nên tuần tự hoá để tránh xung đột merge

## Expected Touch Area

Allowed:
- `src/eth_dca_os/pipeline.py`, `diagnostics.py`, `reporting.py`
- `tests/`

Do not touch without Scope Expansion:
- `src/eth_dca_os/benchmarks.py`, `metrics.py`, `windows.py`, `bootstrap.py` — **chỉ được đọc**;
  nếu phải sửa thân hàm thì gói đã đi ra ngoài phạm vi "đấu nối"
- `src/eth_dca_os/engine.py`, `verdict.py`, `failure_signals.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [x] A2.1 Gọi `run_benchmark_B`, `run_benchmark_C`, `run_benchmark_D` trong pipeline chính
- [x] A2.2 Đưa kết quả B/C/D vào payload báo cáo so sánh với chiến lược và với Benchmark A
- [x] A2.3 Đưa `ablation_scores` (ba model, §2.3) vào `run_all` và vào payload
- [x] A2.4 Đưa `volume_zscore_variant` (§2.4) vào `run_all`, báo cáo **chênh lệch kết quả**
- [x] A2.5 Sinh bảng coverage §4 trong mọi báo cáo official
- [x] A2.6 Tính XIRR §16 và đưa vào payload
- [x] A2.7 Đặt `n_sims=1000` mỗi block length cho official run
- [x] A2.8 Viết test khẳng định payload official chứa đủ các mục bắt buộc

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §2, §2.3, §2.4; BT §4, §4.1, §12, §13, §16, §22
- [x] Data impact được biết — không đổi dữ liệu; đổi **nội dung payload báo cáo**
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] **Dependency T-04 DONE** — thoả sau S002
- [x] **BLK-003 được gỡ:** `python governance/scripts/governance/validate_routing.py` PASS —
      xác nhận E1: `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual
      override(s))`. WP-A2 route Tier C tự nhiên sau fix, không cần nhánh override.
      **Không hạ Tier WP-A2 về B** — Tier vẫn là C, đúng ràng buộc của DEC-008.
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — S006 2026-08-24: routing tái xác nhận
      bằng `routing_engine.py` với đúng Routing Inputs của file này → `base_tier=C, tier=C,
      model=Opus, model_score=2.0, effort=high, effort_score=2.15, model_floors=[none],
      warnings=[none]` — **Tier C đến tự nhiên từ router, KHÔNG qua nhánh override**, xác
      nhận MICRO-GOVDEF-001 không hồi quy; `validate_routing.py` PASS (17 file MAJOR,
      0 accepted manual override). T-04 DONE; BLK-003 vẫn RESOLVED. Branch
      `claude/wp-a3-regime-ladder-3wqw66`, HEAD `0f2a2ab` = origin, working tree sạch;
      WP-D1 DONE xác nhận trên chính branch này; không nhánh remote nào đụng
      `pipeline.py`/`diagnostics.py`/`reporting.py`.

## Completion Gate

Risk = 2 → REQUIRED check kiểm chứng được ưu tiên E1 ở nơi thực thi được. Vì gói này quyết định
báo cáo official có đủ căn cứ so sánh hay không, toàn bộ REQUIRED check dưới đây đặt ở mức E1.

### Functional

#### CHECK-A2-01 — Benchmark B, C, D thực sự được chạy trong pipeline và có mặt trong payload
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chạy pipeline đầy đủ trên dữ liệu tổng hợp, in ra payload, chứng minh có kết quả của cả
B, C và D bên cạnh A. Đóng F-003.

**Kết quả (S006):** `run_gate1` nay gọi `run_benchmark_B/C/D` trên đúng chín window
pre-OOS (`pipeline._benchmark_comparison`), payload có khoá `benchmarks` với cả A, B, C, D
(mỗi mục: `ae_by_window` 9 window, `eth_by_window`, `contributed_by_window`,
`primary_median_ae`). Kiểm bằng chạy thật `tests/test_wp_a2_pipeline_wiring.py::
test_a2_01_benchmarks_bcd_run_and_present` trên pipeline đầy đủ (synth 2018-01→2026-06):
PASS. Hàng A tái lập **đúng bằng** `window_metrics.primary_median` sẵn có (97.89745920461614,
rel=1e-12) — đường so sánh mới nhất quán với đường cũ; A/B/C/D cho **bốn** giá trị khác nhau
(không phải bản sao). BEFORE: `KeyError: 'benchmarks'` (payload không có mục này).

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-02 — Ablation ba model của §2.3 có mặt trong payload official
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: payload chứa đủ ba model ablation, đủ để trả lời "P có đóng góp gì ngoài D không" và
"RSI có đóng góp gì ngoài Return7 không". Đóng F-004 phần ablation.

**Kết quả (S006):** `diagnostics.run_all` nay gọi `ablation_scores` và đưa cả ba model
đăng ký trước vào payload: `price_minimal`, `stress_minimal`, `both_minimal`. Mỗi model báo cáo
`score_distribution` + `corr_with_baseline_oscore` + `mean_oscore_delta` /
`mean_abs_oscore_delta` / `max_abs_oscore_delta` / `n_common_days` — đủ để trả lời "P có đóng
góp gì ngoài D không" và "RSI có đóng góp gì ngoài Return7 không" bằng số. Kiểm bằng chạy thật
`::test_a2_02_ablation_three_models_in_payload`: PASS. BEFORE: FAIL (`run_all` không trả khoá
`ablation`).

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-03 — Diagnostic volume z-score §2.4 được chạy và **chênh lệch kết quả** được báo cáo
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: payload chứa cả kết quả biến thể z-score lẫn **bảng chênh lệch** so với bản gốc — §2.4
đòi "báo cáo chênh lệch kết quả", không chỉ chạy. Đóng F-004 phần volume z-score.

**Kết quả (S006):** `run_all` nay gọi `volume_zscore_variant` và báo cáo **cả hai** phần:
`variant.score_distribution` và `delta_vs_baseline` (`mean_oscore_delta`,
`mean_abs_oscore_delta`, `max_abs_oscore_delta`, `corr_with_baseline_oscore`,
`n_common_days`) — đúng chữ "báo cáo chênh lệch kết quả" của ST §2.4, không chỉ chạy. Payload
kèm `note` khẳng định đây là DIAGNOSTIC, không thay factor production. Kiểm bằng chạy thật
`::test_a2_03_volume_zscore_variant_with_delta`, có assertion chống suy biến: phân bố của biến
thể phải KHÁC bản gốc (nếu trùng khít nghĩa là biến thể chưa thực sự được áp dụng): PASS.
BEFORE: FAIL.

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-04 — Bảng coverage weight §4 được sinh trong mọi báo cáo official
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: bảng coverage có mặt trong báo cáo, và có mặt **trong mọi** báo cáo official chứ không chỉ
khi bật cờ. Đóng F-012.

**Kết quả (S006):** `run_gate1` nay luôn sinh `payload["window_metrics"]["coverage_table"]`
bằng `windows.coverage_table()` — đặt ở nhánh chính, **không sau bất kỳ cờ nào**, nên có trong
MỌI báo cáo (official lẫn dev). Kiểm bằng chạy thật `::test_a2_04_coverage_table_always_present`
(bảng không rỗng, mỗi hàng có `month`/`windows`, có tháng thuộc ≥2 window — phản ánh đúng
window chồng lấn): PASS. BEFORE: FAIL (khoá không tồn tại).

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-05 — XIRR / money-weighted return §16 được tính và có trong payload
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: giá trị XIRR có mặt và được kiểm bằng một ca có đáp số biết trước. Đóng F-013.

**Kết quả (S006):** `run_gate1` nay tính XIRR từ full-period run sẵn có
(`pipeline._xirr_payload`): dòng tiền = mỗi contribution ngoài (âm) + giá trị ETH cuối kỳ theo
giá đóng cửa cuối dataset (dương), gọi `metrics.xirr` **không sửa công thức**. Payload:
`xirr`, `n_cashflows`, `final_eth`, `final_price`, `total_contributed`, `final_value_usdt`.
Kiểm bằng chạy thật `::test_a2_05_xirr_present_in_payload` (giá trị hữu hạn, ≥2 dòng tiền):
PASS. **Ca có đáp số biết trước** `::test_a2_05b_xirr_known_answer`: nộp 100 → nhận 110 sau
đúng 1 năm ⇒ XIRR = 10% (abs=1e-6) — PASS ở CẢ BEFORE lẫn AFTER, xác nhận hàm vốn đã đúng và
finding đúng là "không được gọi", không phải "tính sai".

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-06 — Bootstrap chạy 1000 mô phỏng mỗi block length trong official run
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh `n_sims=1000` được dùng cho mỗi block length khi `official` là true, và pipeline
không còn ghi đè xuống 200. Đóng F-014.

**Kết quả (S006):** thêm `pipeline._bootstrap_sims(dev_limit)` — official (`dev_limit=None`)
→ **1000**, dev/smoke → 200; `run_gate1` truyền giá trị này xuống `block_bootstrap_ae`, không
còn hằng số 200. Cùng quy ước dev/official với `run_gate2`/`run_gate3`/`run_controls`.
**Bằng chứng đo trực tiếp** (không suy luận từ đọc code): fixture test thay
`pipeline.block_bootstrap_ae` bằng spy ghi lại `n_sims` thực nhận —
BEFORE `{'n_sims': 200}` → AFTER `{'n_sims': 1000}`
(`::test_a2_06_bootstrap_uses_1000_sims_for_official`: PASS). Đường dev vẫn tồn tại và khác
official: `::test_a2_06b_dev_limit_keeps_smoke_fast` khẳng định
`_bootstrap_sims(None)==1000` và `_bootstrap_sims(3)==200`: PASS.

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-07 — Mọi benchmark nhận đúng cùng lịch external contribution
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: equal capital rule được kiểm cho **cả B, C, D**, không chỉ A như hiện nay. Đây là điều kiện
để phép so sánh của BT §22 có nghĩa.

**Kết quả (S006):** `_benchmark_comparison` gọi cả bốn benchmark với **cùng** `(start, end,
contribution, exec_cfg)` của từng window — cùng lịch external contribution với engine.
Payload ghi `contributed_by_window` cho từng benchmark để kiểm được, không phải tin lời.
Kiểm bằng chạy thật `::test_a2_07_equal_capital_rule_for_bcd`: với **mọi** window trong chín
window, `contributed` của B, C, D bằng đúng của A: PASS. BEFORE: FAIL (không có dữ liệu B/C/D
để kiểm — chính là lỗ hổng khiến phép so sánh BT §22 vô nghĩa).

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

### Regression / Scope

#### CHECK-A2-08 — Không công thức nào bị sửa; diff chỉ là đấu nối
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` cho thấy thân hàm của `benchmarks.py`, `metrics.py`, `windows.py`,
`bootstrap.py` không đổi (trừ sửa mặc định `n_sims` nếu chọn cách đó, phải nêu rõ). Nếu một công
thức phải đổi thì gói đã ra ngoài phạm vi → xem Escalation.

**Kết quả (S006):** `git diff --stat` trên các module **chỉ được đọc** —
`benchmarks.py`, `metrics.py`, `windows.py`, `bootstrap.py` — trả **rỗng: 0 dòng đổi**.
Cũng không đụng `engine.py`, `verdict.py`, `failure_signals.py`, `gates.py`.
Toàn bộ diff mã nguồn: `pipeline.py` (+lời gọi/tổng hợp), `diagnostics.py` (+gọi hai hàm sẵn
có và tổng hợp delta), `cli.py` (**đúng 1 dòng**: truyền `dev_limit=args.dev_limit` xuống
`run_gate1`). Không công thức nào bị sửa; `n_sims` mặc định của `bootstrap.py` giữ nguyên 1000
(pipeline thôi ghi đè, không sửa mặc định của hàm).

**Ghi chú ranh giới scope (khai báo minh bạch, không giấu):** `cli.py` không nằm trong danh
sách Allowed cũng không nằm trong danh sách "Do not touch" của Expected Touch Area. Thay đổi
là **một dòng truyền tham số**, cùng bản chất "đấu nối", không chạm công thức/ngưỡng/định
nghĩa benchmark. Không có nó, phân biệt dev/official không tới được điểm vào thật và
`ethdca run --dev-limit` sẽ chạy 1000 mô phỏng trái với chính ngữ nghĩa `--dev-limit` mà CLI
công bố (gate2/gate3/controls đã dùng đúng quy ước này). Trình chủ dự án ghi nhận.

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-09 — Kết quả của chiến lược và Benchmark A không đổi sau khi đấu nối
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric của chiến lược và của Benchmark A trước–sau trùng khớp.
Đấu nối thêm mục báo cáo **không được** làm đổi kết quả đã có.

**Kết quả (S006):** đo thực nghiệm BEFORE/AFTER trên **cùng dataset tổng hợp cố định**
(synth 2018-01-01→2026-06-30, cùng seed). BEFORE chạy qua `git worktree` tại `0f2a2ab` với
assert provenance (`code_path` phải thuộc worktree). So sánh **159 trường** metric của chiến
lược và Benchmark A — `ae_by_window` (9 window), `anchor_set_medians`, `primary_median`,
`pooled_median_descriptive`, `gate1`, `oos_ae`/`oos_months`, `_full_run_eth`,
`monthly_deployments`, `concentration`, `cash_ratio`, `counters_w5`, và toàn bộ diagnostic
sẵn có (`score_distribution`, `vif.any_severe`, `redundancy_flags`):

**Số trường khác nhau = 0.** `primary_median` 97.89745920461614 (trùng khít),
`_full_run_eth` 22.177077553955925 (trùng khít), `oos_ae` 104.8556473248996 (trùng khít).

Đây là phép kiểm có ý nghĩa thật, không phải hình thức: diagnostic mới gọi `sub_factors(ind)`
và `volume_zscore_variant(ind, sf)` trên cùng `prep.indicators`, nên nếu chúng mutate đầu vào
thì score/engine sẽ đổi — kết quả 0/159 chứng minh không có mutation nào.

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T08:40Z

#### CHECK-A2-10 — Toàn bộ test suite Python PASS
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; không test nào bị skip hoặc nới lỏng để gói này đi qua.

**Kết quả (S006):** `python -m pytest tests/` → **108 passed in 525.31s (0:08:45)** —
0 failed, 0 skipped, 0 xfail, exit code 0 (99 test trước WP-A2 + 9 test wiring mới).
**Không test cũ nào bị sửa, skip hay nới lỏng** để gói này đi qua: diff `tests/` chỉ THÊM
đúng một file mới (`test_wp_a2_pipeline_wiring.py`), không đụng file test nào có sẵn.
Thời gian suite tăng (431s → 525s) là do official run nay chạy bootstrap 1000 mô phỏng mỗi
block length thay vì 200 — đúng yêu cầu BT §13 và chính là hành vi mà CHECK-A2-06 đòi hỏi.

Executed By:
Agent phiên S006 (Tier C / high)

Timestamp:
2026-08-24T09:05Z

## Exit Criteria
- [x] 100% REQUIRED checks PASS (10/10: CHECK-A2-01..10)
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ)
- [x] Không công thức nào bị sửa ngoài phạm vi đấu nối (CHECK-A2-08: 4 module chỉ-đọc
      0 dòng đổi; ranh giới `cli.py` +1 dòng đã khai báo minh bạch)
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-007 cập nhật trạng thái
      (GIẢM THIỂU MỘT PHẦN — phần Failure Signal còn lại thuộc WP-A5)
- [x] Session handoff được viết (`docs/sessions/S006-wp-a2-pipeline-wiring.md`)
- [x] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- BLK-003 chưa được gỡ khi mở task → `MISSING_INPUT`, giữ BLOCKED. KHÔNG nâng Tier, KHÔNG hạ Tier.
- Đấu nối một hạng mục làm đổi kết quả của chiến lược hoặc Benchmark A → `SCOPE_CHANGED`: dừng, xác
  định nguyên nhân; nếu nguyên nhân là công thức sai thì đó là **finding mới**, không được sửa im
  lặng trong gói đấu nối.
- Một hàm được cho là "đã đúng" hoá ra sai khi chạy thật → mở finding mới, trình chủ dự án qua
  `COMPLETION GATE CHANGE PROPOSAL`; không tự mở rộng gói.
- Bootstrap 1000 × mỗi block length vượt ngân sách thời gian chấp nhận được → `CONFLICT DETECTED`
  giữa BT §13 và ràng buộc vận hành; trình chủ dự án, **không tự hạ xuống 200**.

## Ảnh hưởng nếu gói này thất bại

Official run sẽ phát verdict mà chưa từng đối chiếu chiến lược với ba benchmark đơn giản hơn, không
có ablation, không có chẩn đoán z-score, không có bảng coverage, không có XIRR, và bootstrap dưới
chuẩn. Theo Master Index §6 không được chạy lại official run để bổ sung — nghĩa là **khiếm khuyết
này không sửa được sau khi T-06 đã chạy**. GATE-A không đóng.

## Changed Files Registry

Created:
- `tests/test_wp_a2_pipeline_wiring.py` — 9 test wiring test-first
- `docs/sessions/S006-wp-a2-pipeline-wiring.md` — session handoff

Modified:
- `src/eth_dca_os/pipeline.py` — `_bootstrap_sims`, `_benchmark_comparison`, `_xirr_payload`;
  `run_gate1` nhận `dev_limit`, payload thêm `benchmarks`/`coverage_table`/`xirr`/`official`
- `src/eth_dca_os/diagnostics.py` — `run_all` gọi ablation + volume z-score; `_oscore_delta_summary`
- `src/eth_dca_os/cli.py` — 1 dòng truyền `dev_limit` (ranh giới scope đã khai báo)
- `docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md` — evidence + Status DONE
- `PROJECT/PROJECT_PROGRESS.md` (+ `PROJECT/LO_TRINH_DE_HIEU.md` sinh tự động)
- `reporting.py` — KHÔNG cần sửa: `write_report`/`save_run` đã truyền payload nguyên vẹn nên
  các mục mới tự có mặt trong report official

Deleted:
- Không

Migration Impact:
- Payload báo cáo mở rộng; không có consumer nào ngoài repo phụ thuộc định dạng này ở thời điểm hiện tại

## Notes

Ghi nhận về routing: Tier C của gói này là **ghi đè thủ công có phê duyệt** (DEC-008), không phải
kết quả router. Việc `validate_routing.py` báo FAIL cho file này là hệ quả đã được DEC-008 dự đoán
trước, không phải một defect mới. Xem `docs/reviews/GOVDEF-001-routing-engine-boundary.md` và
BLK-003. **Không sửa `routing_engine.py` từ bên trong gói này**, và tuyệt đối không hard-code ngoại
lệ riêng cho WP-A2.

Ghi nhận về thứ tự: WP-A2 và WP-A5 cùng sửa `pipeline.py`. Không có phụ thuộc logic hai chiều —
WP-A5 phụ thuộc WP-A2 — nhưng nên tuần tự hoá để tránh xung đột merge.
