# WP-B1 — Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo

## Metadata
Status:
IN_PROGRESS — mở tại phiên hiện tại (2026-09-03), sau khi Ready Gate được xác nhận lại đầy đủ
(mục còn `[ ]` duy nhất nay `[x]`, xem Ready Gate bên dưới). READY trước đó tại `DEC-031`
(2026-09-03): dependency `T-06 DONE` và `WP-A5 DONE` đều thoả.
**Kết quả phiên IN_PROGRESS (cập nhật sau fresh Independent E2 `E2-WP-B1-002-FRESH-2026-09-04` +
repair batch E2-B1-F01/F02):** **9/10 REQUIRED PASS** (CHECK-B1-01, 02, 03, 04, 05, 06, 07, 08,
10). **1/10 `NOT_TESTED`/FAIL**: CHECK-B1-09 — fresh Independent E2 tái lập được 2 BLOCKING
finding mới (`E2-B1-F01`: FS-08 fail-open khi thiếu đúng một control; `E2-B1-F02`: officiality
không chặn `can_proceed_to_app`), khiến CHECK-B1-01/07/09 tạm FAIL. Cả hai finding ĐÃ ĐƯỢC SỬA
(`failure_signals.py`, `pipeline.py`) trong cùng một repair batch, có regression test mới (21
test, `tests/test_wp_b1_e2_fresh_fail_repair.py`), CHECK-B1-01/07 phục hồi `PASS`. CHECK-B1-09
vẫn `NOT_TESTED`/FAIL — **CHƯA chạy lại E2 mới trong phiên này**, cần một phiên độc lập khác. Xem
`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-fail.md` (artifact E2 gốc) và
`docs/sessions/S023-wp-b1-verdict-correctness-in-progress.md` (addendum repair). WP-B1 **CHƯA
DONE**.

Phase:
Phase 4 — Lớp B: bắt buộc sửa trước verdict

Task Mode:
MAJOR

Lớp (RCP-001):
B — MUST FIX BEFORE VERDICT · **nằm trên đường găng**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 4
B: 3
A: 4
X: 3
U: 3
V: 3
H: 3
C: 3
F: 4

Routing Categories:
accounting_financial

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.4

Effort Routing Score:
3.25

Applied Model Floor:
cognitive:A>=3&X>=3, safety_business:min_C

Applied Effort Floor:
safety_business:min_high

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Difficulty:
3/4

Risk:
4/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Chốt **chính sách** ra verdict: khi nào được kết luận BUILD, tín hiệu chưa đo được xử lý ra sao,
ngưỡng số nào là hợp lệ, và điều kiện nào bắt buộc phải chạy lại Gate 1 trước khi kết quả được dùng.

Gói này là **người gác cổng cuối cùng** trước T-07. Nó tồn tại để một verdict thuận lợi không được
phát ra trên nền bằng chứng chưa đủ.

## Lát cắt pre-T06 theo `DEC-026` (S016, 2026-09-03) — trạng thái gói VẪN `PLANNED`

Chủ dự án cho phép (ROADMAP EXCEPTION, `PROJECT/PROJECT_DECISIONS.md` DEC-026) triển khai **một
lát cắt giới hạn** của gói này TRƯỚC `T-06`, chỉ để đóng `F-S015-01` và phần tương ứng của
`CHECK-B1-01`. Phạm vi thật sự đã chạm:

- `src/eth_dca_os/failure_signals.py` — chuẩn hoá mỗi signal về `bool` thuần Python / `None`
  ngay tại nơi dựng dict; cờ chặn `any_true` bật khi có signal TRUE **hoặc** còn signal UNKNOWN;
  thêm hai khoá máy đọc được `true` và `cap_cause`. **Không đổi ngưỡng nào.**
- `tests/test_wp_b1_slice_failure_signal_cap.py` — 33 test (đỏ 25/33 trên bản trước lát cắt).
- `tests/test_wp_a5_failure_signal_instrumentation.py` — xoá test đánh dấu
  `test_a5_04_numpy_typed_signal_would_be_invisible` (đã hoàn thành vai trò); khoá
  `test_a5_07_no_diff_in_policy_files` vào đúng khoảng lịch sử của WP-A5.
- **`verdict.py` KHÔNG đổi** (không có authority mới): `git diff b095874..HEAD -- verdict.py` rỗng.

KHÔNG thuộc lát cắt (vẫn mở, theo DEC-026 mục OUT): B1.3 (Control F / F-017), B1.4 (ngưỡng),
B1.5/B1.6 (`docs/CONVENTIONS.md`), B1.8, `CHECK-B1-02…10`, E2 (`CHECK-B1-09`). Gói **không**
chuyển trạng thái; Completion Gate giữ nguyên câu chữ. Biên bản:
`docs/sessions/S016-wp-b1-lat-cat-dec026.md`.

## Ranh giới trách nhiệm

Gói này chịu trách nhiệm **CHÍNH SÁCH VERDICT (verdict policy)**. Việc **ĐO LƯỜNG** ba đại lượng
FS-02 / FS-06 / FS-12 và phạm vi tính FS-03 / FS-07 thuộc **WP-A5** và phải xong trước T-06. Không
trộn hai trách nhiệm; đặc biệt, gói này **không được** giải quyết một FS còn UNKNOWN bằng cách gán
giá trị mặc định.

## Vì sao gói này ở lớp B

`ethdca verdict` đọc lại được `pipeline_state.json`, nên chính sách sửa được **sau** khi official
run đã chạy. Đó là tiêu chí phân lớp B của RCP-001.

**Ngoại lệ đã được ghi nhận:** F-017 (Control F) cần **chạy lại Gate 1**. RCP-001 đã nêu rõ điều
này và chủ dự án đã phê duyệt giữ F-017 ở lớp B **kèm điều kiện DEC-009** — xem CHECK-B1-02.

## Đóng finding / risk

- F-002 — **phần chính sách**: verdict BUILD vẫn phát ra khi FS-02, FS-06, FS-12 là UNKNOWN
- F-015 — ngưỡng FS-02 (`>0.5`), FS-07 (`cash>0.30 và AE<102`), FS-12 (`>0.80`) do triển khai tự đặt
- F-017 — Control F gộp toàn bộ vốn của tháng vào một lệnh, không giữ profile tranche theo tháng
- F-026 — `verdict.py` viện dẫn `docs/CONVENTIONS.md` cho ánh xạ gate-fail → verdict, nhưng file đó
  không có mục nào về verdict
- RSK-005 — quy ước không thuộc spec đang nằm trong đường ra verdict

## Scope

- `src/eth_dca_os/verdict.py` — chính sách và ánh xạ
- `src/eth_dca_os/failure_signals.py` — quy tắc UNKNOWN và ngưỡng
- `src/eth_dca_os/benchmarks.py` — Control F (F-017), Control G (`shift_days`)
- `docs/CONVENTIONS.md` — ghi mọi quy ước không thuộc spec đang nằm trong đường ra verdict
- `tests/` — test chính sách verdict
- Chạy lại Gate 1 nếu DEC-009 kích hoạt

## Out of Scope

- Sinh dữ liệu đo lường Failure Signal (WP-A5)
- **Đổi ngưỡng gate của spec** (BT §7–§10) — cấm bởi Master Index §6
- Chạy lại official run để cải thiện kết quả — Master Index §6 cấm tuyệt đối. Chạy lại Gate 1 theo
  DEC-009 là chạy lại **vì tính hợp lệ**, không phải để cải thiện con số; đây là hai việc khác nhau
  và phải được ghi rõ là khác nhau
- Đọc verdict và quyết định hướng đi (đó là T-07, thẩm quyền chủ dự án)
- Sửa engine, regime, ladder, dữ liệu (lớp A)

## Dependencies
- T-04 (DONE)
- **T-06** (DONE) — official run đã chạy
- Gián tiếp: WP-A5 (dữ liệu đo lường phải tồn tại trong `pipeline_state.json`)

## Blocks
- GATE-B → T-07

## Parallel-Safe With
- WP-B2, WP-B3

## Expected Touch Area

Allowed:
- `src/eth_dca_os/verdict.py`, `failure_signals.py`, `benchmarks.py`
- `docs/CONVENTIONS.md`
- `tests/`

Do not touch without Scope Expansion:
- `src/eth_dca_os/gates.py` — ngưỡng gate là điều khoản spec
- `src/eth_dca_os/engine.py`, `regime.py`, `ladders.py`, `capital.py`, `score.py`
- `docs/spec/`, `webapp/`

## Subtasks
- [ ] B1.1 Chốt và cài đặt quy tắc: REQUIRED Failure Signal còn UNKNOWN thì không được BUILD
      *(lát cắt DEC-026/S016: CƠ CHẾ đã cài — UNKNOWN kích hoạt cap trong `failure_signals.py`,
      verdict không thể là BUILD; phần CHỐT CHÍNH SÁCH — UNKNOWN nên cho `BUILD_WITH_MODIFICATIONS`
      như hiện nay hay `INCONCLUSIVE` — còn mở vì cần chạm `verdict.py`)*
- [x] B1.2 Xác định remediation nào ảnh hưởng Gate 1 và áp DEC-009 (xem CHECK-B1-02) —
      KẾT LUẬN: KHÔNG. Bằng chứng đường mã tại CHECK-B1-02.
- [x] B1.3 Sửa Control F giữ đúng kích thước tranche và profile giải ngân theo tháng (F-017) —
      PRODUCTION REPAIR đúng, kiểm chứng bằng mechanism test; FS-08 post-F-017 nay ĐÃ TÍNH LẠI
      bằng POST-F-017 WP-B1 EVIDENCE REPLAY (Owner-supplied, dataset official thật) = `FALSE`.
      CHECK-B1-03 đủ chữ hoàn toàn, `PASS` — xem CHECK-B1-03 Addendum 3
- [x] B1.4 Phê chuẩn hoặc thay thế ngưỡng FS-02 / FS-07 / FS-12, có căn cứ ghi lại —
      APPROVE AS-IS (Owner Decision `DEC-033`), ghi tại `docs/CONVENTIONS.md` #21(e) (xem
      CHECK-B1-04)
- [x] B1.5 Ghi ánh xạ gate-fail → verdict vào `docs/CONVENTIONS.md` — mục #21(a)
- [x] B1.6 Ghi các quy ước còn lại: phạm vi window của FS-03/FS-07 (đã có ở #20(d) từ WP-A5),
      `shift_days=10` của Control G — mục #21(c)
- [x] B1.7 Viết test chính sách verdict, gồm ca "đúng một FS là None" — 12 test mới
      `tests/test_wp_b1_verdict_policy.py` (precedence, can_proceed_to_app, numpy/bool,
      determinism), cộng 33 test có sẵn từ lát cắt DEC-026/S016 (`test_wp_b1_slice_failure_
      signal_cap.py`, ca "đúng một FS là None" cho cả 12 vị trí + ca numpy TRUE) — xem CHECK-B1-07
- [x] B1.8 Tính lại verdict từ `pipeline_state.json` đã lưu và ghi nhận kết quả — Owner-supplied
      evidence chain (pipeline_state.json + baseline_metrics.json + report.json cùng gói
      official), xem CHECK-B1-08

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa, và **ranh giới chính sách / đo lường được nêu tường minh**
- [x] Out-of-scope được định nghĩa
- [x] **Dependency T-06 DONE** — `DEC-031` (2026-09-03): official run thật đã chạy, verdict
      `DO_NOT_BUILD`. Đây là dữ liệu để áp chính sách, KHÔNG phải dữ liệu tổng hợp (DEC-003)
- [x] **WP-A5 DONE** — DONE từ S015/`DEC-025`; ba đại lượng FS (bao gồm FS-02/FS-12) THỰC SỰ
      đã được đo trong official run (`docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §6–§7)
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §12, §16, §17; IM §5, §6, §7; Master Index §6; DEC-009
- [x] Data impact được biết — đổi cách diễn giải kết quả đã lưu, không đổi dữ liệu đã chạy
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task (phiên hiện tại — đọc lại `AGENTS.md`,
      `governance/v4/CORE/*`, `PROJECT/PROJECT_PROGRESS.md`/`PROJECT_DECISIONS.md`/
      `CAPABILITY_REGISTRY.md`/`HARDENING_BACKLOG.md`, `DEC-026`/`DEC-031`, file task này —
      toàn bộ 14 mục trên vẫn đúng, không phát hiện mâu thuẫn)

## Completion Gate

Risk = 4 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được; category `accounting_financial` và
vai trò gác cổng verdict → **E2 bắt buộc** cho CHECK-B1-09.

### Business Logic / Verdict Policy

#### CHECK-B1-01 — BUILD không được phép khi bất kỳ REQUIRED Failure Signal nào còn UNKNOWN
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: Backtest §17 liệt kê FS-01…FS-12 mà **không đánh dấu mục nào là tuỳ chọn**, nên cả 12 đều
REQUIRED. Test phải dựng một tập FS trong đó **đúng một** signal là `None` và khẳng định verdict trả
về **không phải** `BUILD`, đồng thời `can_proceed_to_app` là `false`. Lặp lại cho mỗi vị trí trong
12 signal, không chỉ cho một vị trí thuận tiện.

Hôm nay `any_true = any(v is True ...)` khiến `None` không kích hoạt cap và verdict BUILD vẫn phát
ra — đây là ca phải thất bại trước khi sửa. Đóng F-002 phần chính sách.

**Kết quả (S016, 2026-09-03) — PARTIAL: pre-T06 slice theo `DEC-026`.** Phần PASS dưới đây là
đúng chữ của check này (E1, test tự động); nó CHƯA qua E2 độc lập (`CHECK-B1-09` vẫn thuộc WP-B1
đầy đủ theo DEC-026 (5)) và chưa được tính lại trên official run (`CHECK-B1-08`). Chín check còn
lại giữ `NOT_TESTED`.

- Test: `tests/test_wp_b1_slice_failure_signal_cap.py` (33 test).
  `test_b1_01_exactly_one_unknown_signal_blocks_build[FS-01…FS-12]` dựng bộ input đủ 12 signal
  đều FALSE (cùng số với `test_verdict_mapping`), rồi xoá đúng input của **từng** vị trí để chỉ
  signal đó là `None`; khẳng định `unknown == [k]`, 11 signal còn lại `is False`, verdict
  `!= "BUILD"`, `can_proceed_to_app is False`, và lý do có tên signal. Thêm ca 12/12 UNKNOWN.
- **ĐỎ TRƯỚC KHI SỬA** (chạy trên `failure_signals.py` tại `28b0255`, bản trước lát cắt):
  `25 failed, 8 passed` — đỏ đủ 12/12 vị trí UNKNOWN (`AssertionError: FS-xx UNKNOWN nhưng cap
  không bật — BUILD sẽ lọt`), đỏ 9/12 vị trí numpy TRUE (FS-02/03/05/06/07/09/10/11/12; FS-01/04/08
  vốn đã ra bool thuần vì đi qua `sum`/`bool()`/`not`), đỏ ca "toàn numpy FALSE phải là bool thuần".
  Log: `tests_RED_before_fix_verbose.log` (scratchpad S016; trích trong biên bản).
- **XANH SAU KHI SỬA**: `33 passed in 0.12s`. Test đánh dấu
  `test_a5_04_numpy_typed_signal_would_be_invisible` (WP-A5) chuyển ĐỎ đúng như nó tự tiên đoán
  (`assert True is False`) → xoá theo hướng dẫn ghi trong chính test đó. F-S015-01 ĐÓNG.
- Sửa production DUY NHẤT: `src/eth_dca_os/failure_signals.py` (+45/−15, phần lớn là docstring
  hợp đồng): hàm `_flag()` ép `bool()`/giữ `None` tại nơi dựng dict; `any_true = bool(trues) or
  bool(unknown)`; thêm `true` (danh sách TRUE) và `cap_cause` ∈ {`TRUE`, `UNKNOWN`,
  `TRUE_AND_UNKNOWN`, `None`}. Ngưỡng 0.5/0.80/0.30/102.0/3.0/0.50/100.0 không đổi
  (`test_a5_07_verdict_policy_thresholds_unchanged` vẫn xanh).
- **`verdict.py` không đổi**: `git diff --stat b095874..HEAD -- src/eth_dca_os/verdict.py` = rỗng;
  working tree = HEAD (md5 `c44f6982…`). Vì vậy ca UNKNOWN đi ra `BUILD_WITH_MODIFICATIONS` (nhánh
  duy nhất không-BUILD khi ba gate PASS) — đủ cho chữ của check; việc UNKNOWN có nên là
  `INCONCLUSIVE` thay vì BWM là quyết định của WP-B1 đầy đủ (B1.1/B1.5).
- Chỉ blocking semantics đổi: `test_b1_01_only_blocking_semantics_changed_vs_pre_slice` nạp
  `failure_signals.py` tại `28b0255` từ git, chạy 35 vector input trên cả hai bản: giá trị logic
  12 signal và danh sách `unknown` trùng khớp từng vector; `any_true` chỉ khác ở đúng hai ca của
  F-S015-01/CHECK-B1-01. Ánh xạ gate-fail → verdict giữ nguyên
  (`test_b1_01_gate_fail_mapping_unchanged_regardless_of_cap`).
- Full suite: `python -m pytest tests/ -q -p no:cacheprovider` → `365 tests collected`, 365 kết quả `.` (0 `F`/`E`/`s`/`x`), `EXIT=0`, real 14m04s (pyproject `addopts="-q"` nên không in dòng tổng kết; đếm từ log). Trước lát cắt tại `28b0255`: 333 collected (orchestrator ghi 330 PASS); 333 − 1 (test đánh dấu xoá) + 33 (test lát cắt) = 365 ✓ (trước lát cắt: 330 PASS;
  −1 test đánh dấu, +33 test lát cắt).
- Run đủ phase TRƯỚC/SAU (synthetic 2018-01-01→2026-06-30, `dev_limit=25`, `n_sims=50`, KHÔNG phải
  official — DEC-003/BLK-001): `FS-11` từ chuỗi `"False"` (dấu vết `numpy.bool_`) thành bool JSON `false`; 11 signal còn lại, `UNKNOWN: []`, khối `failure_signal_inputs_wp_a5`, kết quả bốn gate và verdict `DO_NOT_BUILD` (`Gate 1 FAIL`) **y hệt** giữa hai run — nhánh cap không được chạm tới ở dataset này. Khoá mới: `true = ['FS-02','FS-03','FS-04','FS-08','FS-12']`, `cap_cause = 'TRUE'`. Bảng đầy đủ: biên bản S016 §7.
- Phần dư mỹ thuật (KHÔNG sửa vì `verdict.py` ngoài authority của lát cắt): khi cap bật CHỈ vì
  UNKNOWN, `verdict.py:30` in `"Failure-signal cap:  TRUE"` với danh sách rỗng; dòng lý do kế
  tiếp (`FS chưa đánh giá được: …`) và khoá `cap_cause = "UNKNOWN"` trong `failure_signals` mới là
  nguồn đúng. Ghi nhận cho B1.5 của WP-B1 đầy đủ.

**Addendum (phiên WP-B1 IN_PROGRESS hiện tại, 2026-09-03):** câu hỏi chính sách còn mở của B1.1
("UNKNOWN nên cho `BUILD_WITH_MODIFICATIONS` như hiện nay hay `INCONCLUSIVE`") nay ĐÃ CHỐT —
xem `docs/CONVENTIONS.md` #21(b): giữ `BUILD_WITH_MODIFICATIONS`, không thêm nhãn mới, vì bốn
verdict hiện có (BT §17) không định nghĩa trạng thái thứ năm và chữ của chính CHECK-B1-01 (verdict
≠ `BUILD`, `can_proceed_to_app=false`) đã được thoả bằng nhãn này. Không đổi code, không đổi test.
`tests/test_wp_b1_verdict_policy.py` bổ sung thêm bằng chứng thực thi độc lập với input
`numpy.bool_` ở tầng `gates.py` (họ khiếm khuyết H-26) cho thấy `verdict.py` vẫn đọc đúng bằng
truthiness — không có đường nào numpy type làm sai lệch cap.

Executed By:
Fable 5.1 (Tier D / max — đúng canonical routing của gói), phiên S016; lát cắt do chủ dự án cho
phép tại DEC-026. Addendum: Sonnet 5, phiên WP-B1 IN_PROGRESS hiện tại.

Timestamp:
2026-09-03

**Addendum 2 — Fresh Independent E2 (`E2-WP-B1-002-FRESH-2026-09-04`) FAIL, repair, phục hồi
PASS:** reviewer tái lập được một đường production KHÔNG thuộc 12 vector "đúng một FS là None"
đã có: một signal (FS-08) có BA input độc lập (`v2_eth` + hai Control P95); nếu CHỈ đúng một P95
vắng mặt (không phải cả ba), code cũ (`v2_eth is not None and (F is not None or G is not None)`)
coi control vắng mặt là "V2 tự động beat" thay vì UNKNOWN. Ví dụ tái hiện: `v2_eth=10.0`,
`random_timing_p95=None`, `random_anchor_p95=9.5`, 11 signal khác sạch → production
`run_verdict` ra `verdict=BUILD`, `can_proceed_to_app=true`. Đây LÀ đúng loại vi phạm mà
CHECK-B1-01 tồn tại để chặn ("BUILD không được phép khi bất kỳ REQUIRED FS nào còn UNKNOWN"),
dù 33 test hiện có (theo cấu trúc "toàn bộ input của một FS vắng mặt") không chạm tới ca THIẾU
MỘT PHẦN input của một FS ba-input này. Chấp nhận finding, không tranh cãi.

**Repair (E2-B1-F01, cùng phê duyệt với E2-B1-F02 — xem CHECK-B1-07):**
`src/eth_dca_os/failure_signals.py` — FS-08 nay đòi ĐỦ CẢ BA input (`v2_eth`,
`random_timing_p95`, `random_anchor_p95`) hợp lệ (không `None`, không NaN/non-numeric qua helper
mới `_numeric_and_finite()`) mới tính; thiếu/invalid BẤT KỲ input nào trong ba → `None` (UNKNOWN).
Không đổi chiều so sánh (`v2_eth > p95`, strict), không đổi bất kỳ ngưỡng nào.

Test mới (`tests/test_wp_b1_e2_fresh_fail_repair.py`, 21 test): ma trận đầy đủ F present/missing
× G present/missing × cả hai present (bao gồm ca đúng của E2-B1-F01), NaN/invalid cho từng P95,
`v2_eth` thiếu, end-to-end qua `decide_verdict` xác nhận verdict ≠ BUILD/`can_proceed_to_app=False`
cho đúng counterexample của reviewer, cộng giữ nguyên semantics tie (`>` strict) và exact-boundary/
one-ULP cho FS-02/07/12 (retained adversarial coverage). `tests/test_gates_verdict.py::
test_fs08_random_control` được SỬA (không phải nới lỏng) vì case đầu của nó vô tình mã hoá đúng
hành vi lỗi (chỉ truyền Control F, kỳ vọng `True`) — nay kỳ vọng đúng `None`.

`Status: PASS` (phục hồi từ `FAIL` do fresh E2) — production path đã fail-closed đúng, có
regression test khoá lại. Không hạ bớt phạm vi câu chữ CHECK-B1-01 (vẫn đòi UNKNOWN chặn BUILD
cho MỌI signal, không riêng 12 vector cũ).

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại) — chấp nhận fresh E2 finding, sửa
`failure_signals.py`, thêm regression test

Timestamp:
2026-09-04

#### CHECK-B1-02 — DEC-009: quy tắc Gate 1 staleness được cưỡng chế
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
**Kết quả (phiên hiện tại, sau khi B1.3 hoàn tất) — KẾT LUẬN: KHÔNG.** Remediation của F-017
(Control F/G, xem CHECK-B1-03) **không** ảnh hưởng input/calculation/execution behavior/dataset
interpretation/strategy behavior/backtest behavior của Gate 1, OOS, Gate 2 hay Gate 3. Căn cứ
đường mã (`src/eth_dca_os/pipeline.py`, kiểm lại được độc lập):

1. `run_gate1()` (dòng ~172–249) tính `wm = window_metrics(...)` → `g1 = evaluate_gate1(wm)` và
   `oos = oos_metrics(...)` → `oos_eval = evaluate_oos(oos)` **HOÀN TẤT VÀ ĐÃ GHI VÀO `payload`
   trước** khi `full = run_engine(...)` (dòng ~266, run full-period RIÊNG cho controls) được
   gọi. Thứ tự lệnh trong cùng một hàm chứng minh hai đường tính không giao nhau — Gate 1/OOS đã
   xong việc trước khi `full`/Control F/G tồn tại trong bộ nhớ.
2. `full` (và `monthly_tranches` dẫn xuất từ `full.purchases`, xem CHECK-B1-03) CHỈ được đọc bởi
   `payload["_full_run_monthly_tranches"]`/`payload["_full_run_eth"]`, và hai khoá này CHỈ được
   `run_controls()` (Control F/G) tiêu thụ (`cli.py` dòng gọi `run_controls(prep, out_dir,
   g1["_full_run_monthly_tranches"], ...)`).
3. `run_gate2()`/`run_gate3()` (hai hàm riêng biệt) không gọi `run_controls`/
   `random_timing_control`/`random_anchor_control`, không đọc `monthly_tranches`/
   `monthly_deployments`/`full` ở bất kỳ đâu — `grep -n "run_controls\|monthly_tranches\|full\."
   src/eth_dca_os/pipeline.py` xác nhận các tên này chỉ xuất hiện trong `run_gate1`/
   `run_controls`.
4. Output DUY NHẤT của Control F/G đi vào `run_verdict()` là `controls["random_timing"]["p95"]`
   và `controls["random_anchor"]["p95"]`, dùng làm input của **FS-08** trong
   `evaluate_failure_signals()` — FS-08 là một Failure Signal (cơ chế cap verdict do CHÍNH
   `WP-B1` sở hữu), không phải một Gate/OOS raw evaluation.
5. Vì `verdict.py::decide_verdict` xét `gate1["pass"]`/`oos["pass"]` ở nhánh **ĐẦU TIÊN** (dòng
   14), FS (bao gồm FS-08) chỉ được xét ở nhánh `else` cuối cùng khi cả bốn gate đã PASS — nên
   dù FS-08 có đổi giá trị sau bản sửa F-017, nó **không thể** đổi verdict `DO_NOT_BUILD` của
   T-06 (T-06 đã fail ở Gate 1/OOS, dừng trước khi FS được xét tới trong nhánh quyết định verdict).

**Hệ quả:** Gate 1 KHÔNG cần chạy lại. Kết quả Gate 1 hiện có (kể cả của official run T-06) vẫn
hợp lệ để dùng cho verdict. Không có bản ghi Gate 1 nào bị đánh dấu STALE/INVALIDATED vì không
có remediation nào trong phạm vi WP-B1 chạm tới đường mã Gate 1.

**Đây là REQUIRED check chính thức hoá DEC-009. Không được hạ xuống RECOMMENDED hay OPTIONAL, không
được biến thành ghi chú, và không được thoả bằng narrative.**

Nội dung phải chứng minh, theo hai bước:

**Bước 1 — Xác định.** Đánh giá tường minh xem remediation của F-017 (Control F) — và bất kỳ
remediation nào khác trong gói này — có thay đổi hoặc **có khả năng ảnh hưởng** một trong các yếu tố
sau hay không:
- input,
- calculation,
- execution behavior,
- dataset interpretation,
- strategy behavior,
- backtest behavior.

Kết luận phải là CÓ hoặc KHÔNG, kèm căn cứ cụ thể (đường mã dùng chung, dữ liệu dùng chung), không
phải phỏng đoán.

**Bước 2 — Hệ quả.** Nếu kết luận là CÓ và thay đổi đó có khả năng ảnh hưởng Gate 1:
- **mọi** kết quả Gate 1 được tạo **trước** remediation phải được đánh dấu `STALE / INVALIDATED`
  trong bản ghi;
- Gate 1 **bắt buộc phải chạy lại**;
- **chỉ kết quả Gate 1 mới** được dùng làm căn cứ cho verdict và cho T-07;
- bằng chứng phải gồm bản ghi lần chạy lại, không chỉ tuyên bố rằng đã chạy lại.

Nếu kết luận là KHÔNG, bằng chứng phải cho thấy **vì sao** đường mã của Control F không giao với
đường mã của Gate 1 — ở mức đủ để một reviewer độc lập kiểm lại được.

Check này FAIL nếu: bước 1 không được thực hiện; hoặc bước 1 kết luận CÓ mà Gate 1 không được chạy
lại; hoặc kết quả Gate 1 cũ vẫn được dùng cho verdict. WP-B1 **không được DONE** khi check này chưa
được chứng minh.

Executed By:
...

Timestamp:
...

#### CHECK-B1-03 — Control F giữ đúng kích thước tranche và profile giải ngân theo tháng
Priority:
REQUIRED

Status:
PASS (phục hồi từ `BLOCKED — EVIDENCE INCOMPLETE` sau khi có Owner-supplied POST-F-017 replay
evidence — xem Addendum 3)

Evidence Level:
E1

Evidence:
**Sửa production:** `src/eth_dca_os/benchmarks.py` (`random_timing_control`,
`random_anchor_control`) + `src/eth_dca_os/pipeline.py` (`run_gate1`, `run_controls`) +
`src/eth_dca_os/cli.py` (call site).

**Trước sửa:** cả hai hàm nhận `monthly_deployments: dict[thang, tong_nominal]` và, với MỖI
tháng, rút **một** timestamp/anchor ngẫu nhiên rồi fill **toàn bộ** tổng nominal của tháng đó tại
một điểm duy nhất — đúng như F-017 mô tả ("gộp toàn bộ vốn của tháng vào một lệnh tại thời điểm
ngẫu nhiên"), sai với chữ BT §12 ("giữ nguyên... kích thước tranche và profile giải ngân theo
tháng của V2; chỉ random hóa timestamp mua").

**Sau sửa:** `run_gate1()` nhóm `full.purchases` (bản ghi tranche THẬT do engine tạo sẵn — không
sửa `engine.py`, không chạy lại engine, đúng ranh giới touch area của WP-B1) theo tháng thành
`monthly_tranches: dict[thang, list[nominal_tung_tranche]]`. `random_timing_control`/
`random_anchor_control` nay lặp qua TỪNG tranche trong danh sách của tháng đó và rút một
timestamp/anchor **độc lập cho từng tranche** — giữ nguyên số tranche và kích thước từng tranche
đúng như V2 thật, chỉ random hóa thời điểm mua/anchor của từng tranche.

**Test (`tests/test_benchmarks.py`):**
- `test_random_controls_preserve_tranche_count_f017` — monkeypatch `_fill` để đếm số lần gọi
  thật: với `{"2019-07": [50,30,20], "2019-08": [80]}` (4 tranche, 2 tháng), số lần `_fill` được
  gọi mỗi sim = **4** (đúng số tranche), không phải 2 (số tháng) — đây chính là ca sẽ ĐỎ trên bản
  trước sửa (bản cũ gọi `_fill` đúng 1 lần/tháng = 2 lần). Kiểm cho cả Control F và Control G.
- `test_random_timing_many_small_tranches_lower_variance_than_one_lump` — hệ quả thống kê tất
  yếu của việc rút N lần độc lập so với gộp 1 lần (hiệu ứng lấy trung bình làm giảm phương sai):
  std(ETH) khi tách 6 tranche nhỏ < std(ETH) khi gộp 1 tranche lớn cùng tổng nominal, cùng
  seed/n_sims=400 — bằng chứng gián tiếp nhưng tất định rằng các tranche không còn dùng chung một
  timestamp bị nhân bản.
- `test_random_controls_reproducible` (cập nhật cho định dạng `monthly_tranches`) — vẫn PASS,
  reproducibility (cùng seed → cùng kết quả) không đổi.

**Kết quả test:** `pytest tests/test_benchmarks.py tests/test_e2e.py tests/test_gates_verdict.py
-v` → 14/14 PASS (bao gồm `test_full_pipeline_smoke`/`test_gate1_reproducible` chạy nguyên
pipeline qua `run_controls` với `monthly_tranches` thật).

**FS-08 sau sửa:** giá trị số của FS-08 (so `v2_eth` với p95 của Control F/G) **có thể đổi** vì
đầu vào Control F/G nay chính xác hơn (đúng chữ BT §12) — đây là hệ quả ĐÚNG mong đợi của việc
đóng F-017, không phải regression. FS-08 không ảnh hưởng Gate 1/OOS/Gate 2/Gate 3 (xem
CHECK-B1-02). Giá trị FS-08 thật của official run T-06 CHỈ tính lại được khi có
`pipeline_state.json` của official run — xem CHECK-B1-08 (MISSING_INPUT, artifact do chủ dự án
bảo toàn bên ngoài repository, agent không truy cập được trong phiên này).

**Addendum — ĐẢO NGƯỢC Status sau finding của Independent E2 (`CHECK-B1-09`):** finding nêu chính
xác câu chữ đóng khung của CHECK-B1-03 này: *"Kết quả FS-08 (do Control F nuôi) **phải được tính
lại sau khi sửa**."* Đối chiếu lại: agent đã viết ngay ở đoạn trên rằng giá trị FS-08 thật "CHỈ
tính lại được khi có `pipeline_state.json`" — tức đã tự xác nhận việc TÍNH LẠI chưa xảy ra — nhưng
vẫn để `Status: PASS`. Đây là một vi phạm thật, không phải suy diễn của reviewer: một REQUIRED
check được đóng khung PASS trong khi chính đoạn evidence của nó nói rõ một phần bắt buộc còn
thiếu. Finding được CHẤP NHẬN, không tranh cãi, không bypass.

*(Ghi chú minh bạch, không phải để giảm nhẹ: không tìm thấy artifact `docs/reviews/E2-WP-B1-*.md`
nào trong repository tại thời điểm nhận finding này — `ls docs/reviews/ | grep -i b1` rỗng. Nội
dung finding vẫn được xác nhận ĐÚNG độc lập bằng cách đối chiếu trực tiếp với câu chữ frozen của
chính CHECK-B1-03 và với evidence agent tự viết ở trên — nên được chấp nhận và sửa trên cơ sở đó,
không phải vì đã xác minh được một phiên E2 hình thức đã diễn ra.)*

**Owner-authorized minimal replay (cùng phiên tiếp nối) — thiết kế đã hoàn tất, KHÔNG tính được vì
MISSING_INPUT:**

Yêu cầu chính xác: tính lại `random_timing_control`/`random_anchor_control` (đã sửa F-017) trên
ĐÚNG dataset official T-06 (`dataset_hash = 3150860cb3799403ff40620b6834e4826681893e2e5cd2af
3ca815d2a652d2c5`), rồi áp công thức FS-08
(`fs["FS-08"] = _flag(not (beats_f and beats_g))`, `beats_f = v2_eth > random_timing_p95`,
`beats_g = v2_eth > random_anchor_p95` — cả F VÀ G đều bắt buộc vì `run_verdict()` luôn truyền cả
hai `p95` từ cùng một khối `controls`, không có đường nào chỉ dùng một trong hai).

Input bắt buộc: dataset official (Binance thật, khớp `dataset_hash` trên); `full.purchases` của
V2 (KHÔNG có sẵn trong bất kỳ artifact frozen nào — khoá bắt đầu bằng `_` bị `_strip()`/
`write_report()` loại bỏ khỏi cả `pipeline_state.json` lẫn `report.json`) → phải tái tạo bằng
`run_engine()` với `BASELINE_STRATEGY`/`GATE1_LOW_FRICTION`/`start=2019-01-01`/`end=prep.oos_end()`
— ĐÂY LÀ ĐÚNG lần gọi "full-period run" mà `run_gate1()` vốn đã làm cho Controls, **không phải**
một lần chạy Gate 1 evaluation (`evaluate_gate1`/`window_metrics` không được gọi trong thiết kế
này — xác nhận KHÔNG rerun Gate1/Gate2/Gate3). `v2_eth` (giá trị V2 ETH thật) **CÓ SẴN** không cần
tính lại: `results/random_control_21b7d88e9691_metrics.json` (đã canonical hoá SHA-256 tại
`docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §4) mang khoá `v2_eth` — dùng để đối chiếu (assert khớp
`full.eth_total` tính lại, sai lệch → STOP, không phải bằng chứng hợp lệ).

Exact replay command (Python, chạy NGOÀI `src/`, dùng nguyên production code đã sửa tại
commit này — KHÔNG sửa `src/eth_dca_os/*` để phục vụ replay):

```python
import json
from pathlib import Path
import pandas as pd
from eth_dca_os import MASTER_SEED
from eth_dca_os.config import BASELINE_STRATEGY, GATE1_LOW_FRICTION
from eth_dca_os.engine import TZ_OFFSET, run_engine
from eth_dca_os.pipeline import Prepared
from eth_dca_os.benchmarks import random_timing_control, random_anchor_control
from eth_dca_os.failure_signals import _flag

RAW_DIR = "data/raw"  # thư mục official ĐÃ fetch trước đây — KHÔNG fetch lại, KHÔNG dữ liệu mới
prep = Prepared(RAW_DIR)
assert prep.dataset_hash == "3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5", \
    f"dataset_hash lệch official: {prep.dataset_hash} — STOP, không phải dataset T-06"

cfg, exec_cfg = BASELINE_STRATEGY, GATE1_LOW_FRICTION
scores = prep.scores(cfg.score_weights)
start, end = pd.Timestamp("2019-01-01"), prep.oos_end()

full = run_engine(prep.dataset, scores, cfg, exec_cfg, start, end)  # KHÔNG evaluate_gate1/2/3

monthly_tranches = {}
for p in full.purchases:
    mk = pd.Timestamp(p["ts"] + TZ_OFFSET, unit="s").strftime("%Y-%m")
    monthly_tranches.setdefault(mk, []).append(p["nominal"])

f = random_timing_control(prep.dataset, monthly_tranches, start, end,
                           n_sims=1000, master_seed=MASTER_SEED)
g = random_anchor_control(prep.dataset, monthly_tranches, start, end,
                           n_sims=1000, master_seed=MASTER_SEED)

v2_eth = float(full.eth_total)
frozen = json.loads(Path("results/random_control_21b7d88e9691_metrics.json").read_text())
assert abs(v2_eth - frozen["v2_eth"]) < 1e-6, "V2 eth_total lệch frozen official — STOP"

beats_f, beats_g = bool(v2_eth > f["p95"]), bool(v2_eth > g["p95"])
fs08 = _flag(not (beats_f and beats_g))
print(json.dumps({"dataset_hash": prep.dataset_hash, "v2_eth": v2_eth,
                   "control_f_p95": f["p95"], "control_g_p95": g["p95"],
                   "beats_f": beats_f, "beats_g": beats_g, "FS-08": fs08}, indent=2))
```

**Smoke test (KHÔNG phải evidence — chỉ kiểm script không lỗi cú pháp/API)**: chạy đúng script trên
trên dataset SYNTHETIC (`eth_dca_os.data.synth.generate`) tại phiên này — chạy thành công, output
JSON hợp lệ, không exception, `FS-08` trả về đúng kiểu `bool` (không phải `numpy.bool_`, nhờ
`_flag()` — đúng hợp đồng F-S015-01). Dataset_hash in ra là synthetic, KHÔNG khớp official, KHÔNG
được dùng làm bằng chứng FS-08 thật.

**MISSING_INPUT — không thực thi được trên dữ liệu official trong phiên này:** môi trường agent
(sandbox phiên hiện tại) không có `data/raw/*.parquet` official (gitignored, chưa từng tồn tại ở
đây — xác nhận bằng `find` toàn repo), không có kết nối Binance, và KHÔNG được fetch dữ liệu mới
thay thế (chỉ thị Owner + Master Index §6). Dataset official thật chỉ tồn tại trên máy Owner (thư
mục `data/` từ lần fetch official trước đây, và bản backup
`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03`). **FS-08 post-F-017 = CHƯA
TÍNH ĐƯỢC — KHÔNG suy về FALSE/TRUE, giữ UNKNOWN** cho tới khi Owner chạy đúng script trên ở máy có
dataset official (từ commit hiện tại của nhánh này) và dán lại output.

Status giữ `BLOCKED — EVIDENCE INCOMPLETE` cho tới khi có output đó.

**Addendum 3 — POST-F-017 WP-B1 EVIDENCE REPLAY (Owner-supplied, cùng phiên tiếp nối) —
`BLOCKED → PASS`:**

Chủ dự án đã tự chạy đúng script replay ở trên (không sửa) trên máy Mac có dataset official T-06
được bảo toàn, và cung cấp lại output. **Đây KHÔNG phải một official T-06 run mới** — chỉ là phép
tính lại FS-08 bằng code đã sửa F-017, dán nhãn tường minh **"POST-F-017 WP-B1 EVIDENCE REPLAY"**.

Xác minh cơ học từng điểm (không suy diễn/tối ưu, đối chiếu bằng số):

| Điều kiện | Yêu cầu | Giá trị Owner cung cấp | Kết quả |
|---|---|---|---|
| `source_head` | phải là commit chứa bản sửa F-017 | `702b940` (= HEAD của nhánh này trước khi nhận evidence này; là hậu duệ trực tiếp của `fd6a514`, commit mang bản sửa F-017 — không có production diff nào giữa hai commit) | KHỚP |
| `dataset_hash` | phải khớp official T-06 | `3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5` | KHỚP nguyên văn với `dataset_hash` official đã dùng xuyên suốt WP-B1 (CHECK-B1-08, DEC-031) |
| `master_seed` | phải = 42 | `42` | KHỚP `MASTER_SEED` |
| `n_sims` | phải = 1000 (official, không phải dev-limit 200) | `1000` | KHỚP |
| `v2_eth` vs `frozen_v2_eth` | phải khớp (validity check chống lệch dataset/strategy) | `14.910758150139896` == `14.910758150139896` | KHỚP TUYỆT ĐỐI (bit-for-bit) |
| `beats_f` | `v2_eth > control_f_p95` | `14.910758150139896 > 14.887400583487747` → `True` | ĐÚNG công thức, khớp `"beats_f": true` |
| `beats_g` | `v2_eth > control_g_p95` | `14.910758150139896 > 14.813546903782814` → `True` | ĐÚNG công thức, khớp `"beats_g": true` |
| `FS-08` | `not (beats_f and beats_g)` | `not (True and True)` = `False` | ĐÚNG công thức, khớp `"FS-08": false` |

Tất cả tám điều kiện xác nhận **KHỚP**, tính toán lại độc lập bằng Python xác nhận cùng kết quả.
Không có điều kiện nào cần STOP.

**Kết quả chính thức (POST-F-017 WP-B1 EVIDENCE REPLAY, KHÔNG PHẢI một official T-06 run mới):**

    dataset_hash    = 3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5
    master_seed     = 42, n_sims = 1000
    source_head     = 702b940 (F-017 đã sửa)
    v2_eth          = 14.910758150139896 (khớp frozen official)
    control_f_p95   = 14.887400583487747
    control_g_p95   = 14.813546903782814
    beats_f = true, beats_g = true
    FS-08 (post-F-017) = FALSE

**CHECK-B1-03 nay ĐỦ CHỮ hoàn toàn**: (a) test khẳng định Control F/G không gộp tháng vào một
lệnh — PASS từ trước; (b) F-017 ĐÓNG; (c) "Kết quả FS-08 (do Control F nuôi) phải được tính lại
sau khi sửa" — **NAY ĐÃ THOẢ** bằng evidence ở trên. `Status: BLOCKED → PASS`.

**Không ảnh hưởng verdict lịch sử T-06**: FS-08 chỉ được `verdict.py` xét ở nhánh cuối cùng khi cả
bốn gate (Gate 1, OOS, Gate 2, Gate 3) đều PASS (xem CHECK-B1-02/#21(a)); verdict T-06 đã dừng ở
nhánh Gate 1 FAIL/OOS FAIL từ trước khi FS được xét. `FS-08=false` (post-F-017) không viết lại,
không mâu thuẫn với, và không được dùng để suy luận lại verdict `DO_NOT_BUILD` của T-06.

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại) — canonicalize Owner-supplied replay
evidence, xác minh cơ học 8/8 điều kiện, không rerun/không suy diễn

Timestamp:
2026-09-04

#### CHECK-B1-04 — Ngưỡng FS-02 / FS-07 / FS-12 được phê chuẩn hoặc thay thế, có căn cứ ghi lại
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: ba ngưỡng hiện do triển khai tự đặt (`>0.5`, `cash>0.30 và AE<102`, `>0.80`) phải được
(a) phê chuẩn kèm lý do, hoặc (b) thay thế kèm lý do — và trong cả hai trường hợp được ghi vào
`docs/CONVENTIONS.md` như quy ước tuyên bố, truy được về đâu ra. Đóng F-015.

**Ràng buộc:** không được nới ngưỡng theo hướng làm verdict thuận lợi hơn sau khi đã nhìn thấy kết
quả. Nếu ngưỡng cần đổi bản chất thì đó là thay đổi hypothesis và phải đi qua V2.2 (Master Index §6),
không vá tại chỗ.

**Ghi nhận:** việc phê chuẩn ngưỡng có thể cần quyết định của chủ dự án. Nếu chưa có quyết định →
check này là `BLOCKED`, không phải `PASS`.

**Kết quả (phiên WP-B1 IN_PROGRESS hiện tại):** chưa có quyết định chủ dự án về ba ngưỡng
FS-02 (`>0.5`)/FS-07 (`cash>0.30 và AE<102`)/FS-12 (`>0.80`). Theo đúng ràng buộc "không được nới
ngưỡng theo hướng làm verdict thuận lợi hơn sau khi đã nhìn thấy kết quả" và "KHÔNG tự phê chuẩn
thay chủ dự án" (Escalation Triggers), agent **không tự phê chuẩn/không tự thay** ba ngưỡng này
trong phiên này. Status = **`BLOCKED`**. Không đổi giá trị hằng số nào trong `failure_signals.py`
(xác nhận: `git diff` phiên này trên các dòng chứa `0.5|0.80|0.30|102.0` trong file đó = rỗng).

`MISSING_INPUT` / `OWNER_INPUT_REQUIRED`: chủ dự án cần (a) phê chuẩn ba ngưỡng hiện có kèm lý do,
hoặc (b) thay thế kèm lý do (lưu ý: nếu thay đổi bản chất ngưỡng thì đó là thay đổi hypothesis,
phải qua V2.2 theo Master Index §6, không vá tại chỗ ở WP-B1).

**Kết quả — ĐÃ GIẢI QUYẾT (Owner Decision `DEC-033`, `OD-B1-02`, cùng phiên):** chủ dự án
APPROVE AS-IS cả ba ngưỡng, không đổi giá trị nào — lý do nguyên văn: "Giữ nguyên các threshold
đã được sử dụng trong V2.1.5 vì đây là semantics implementation ban đầu và hiện chưa có evidence
độc lập đủ mạnh để biện minh cho threshold thay thế." Ghi rõ: approval KHÔNG tuyên bố ba ngưỡng
là tối ưu thực nghiệm; KHÔNG tự động cho phép mang sang V2.2; mục đích là cố định semantics và
tránh post-hoc tuning. Canonical hóa tại `docs/CONVENTIONS.md` #21(e) và `PROJECT/
PROJECT_DECISIONS.md` `DEC-033`. **Production diff = 0** — `git diff` trên `failure_signals.py`
(mọi dòng chứa `0.5|0.80|0.30|102.0`) vẫn rỗng, đúng chữ "Không sửa threshold trong production
code" của quyết định. Vì giá trị giữ nguyên, verdict T-06 không bị ảnh hưởng (xem CHECK-B1-02).
`F-015` ĐÓNG. Status: `BLOCKED → PASS`.

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại) — canonicalize Owner Decision `DEC-033`,
không tự phê chuẩn thay

Timestamp:
2026-09-03

#### CHECK-B1-05 — Ánh xạ gate-fail → verdict được ghi ở `docs/CONVENTIONS.md`
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`docs/CONVENTIONS.md` mục **#21(a)** (mới, phiên hiện tại) ghi đầy đủ ánh xạ gate-fail → verdict
khớp với `verdict.py::decide_verdict`: Gate 1 FAIL hoặc OOS FAIL → `DO_NOT_BUILD` (ưu tiên cao
nhất, kể cả khi Gate 2/3 PASS); Gate 2 FAIL hoặc Gate 3 FAIL (khi Gate 1/OOS PASS) →
`INCONCLUSIVE`; cả bốn PASS → xét Failure Signal cap (`BUILD_WITH_MODIFICATIONS` nếu còn TRUE/
UNKNOWN, `BUILD` nếu sạch). Ghi rõ tường minh đây là **quy ước triển khai**, không phải điều khoản
BT §17 (spec chỉ mô tả điều kiện *không được* BUILD, không cho bảng ánh xạ trạng thái cụ thể).
Đóng F-026. Mục #21(b) ghi thêm chính sách UNKNOWN (đã cài từ lát cắt `DEC-026`) dùng cùng nhãn
`BUILD_WITH_MODIFICATIONS`, giải thích vì sao không cần một nhãn `INCONCLUSIVE` riêng cho UNKNOWN.

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại)

Timestamp:
2026-09-03

#### CHECK-B1-06 — Các quy ước không thuộc spec còn lại trong đường ra verdict được ghi đầy đủ
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Phạm vi window dùng để tính FS-03/FS-07 đã được `WP-A5` ghi tại `docs/CONVENTIONS.md` mục
**#20(d)** (chín window + PrimaryMedian, không còn W5-only) — xác nhận lại là ĐỦ, không cần ghi
thêm ở WP-B1. Mục còn thiếu — `shift_days=10` của Control G — nay ghi tại mục **#21(c)** (phiên
hiện tại): biên độ ±10 ngày quanh mốc giữa tháng là tham số triển khai (spec không cho số cụ thể),
chọn để nằm trong cùng tháng lịch, clip cứng tại biên tháng nên không tràn sang tháng khác. Mục
**#21(d)** ghi thêm quy ước mới phát sinh từ CHECK-B1-03 (Control F/G random hóa độc lập theo
từng tranche, không theo tháng — đóng F-017). Sau các mục #20(d) + #21(c) + #21(d): không còn quy
ước nào ảnh hưởng verdict mà chưa truy được về một dòng tài liệu trong phạm vi WP-B1 đã xác định
(RSK-005 giảm thiểu cho phần đã đóng; ngưỡng số FS-02/FS-07/FS-12 vẫn mở — xem CHECK-B1-04).

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại)

Timestamp:
2026-09-03

### Stopping Rule Integrity

#### CHECK-B1-07 — Stopping rule không bị nới ở bất kỳ điểm nào
Priority:
REQUIRED

Status:
PASS (phục hồi từ `FAIL` sau fresh Independent E2 + repair E2-B1-F01/F02 — xem Addendum 4 cuối
check)

Evidence Level:
E1

Evidence:
Từng gạch đầu dòng, đối chiếu bằng test/diff cụ thể:

- **`UNKNOWN` không được coi là PASS ở bất kỳ đâu**: `tests/test_wp_b1_slice_failure_signal_cap.py`
  (33 test, lát cắt `DEC-026`) khẳng định đúng 1 trong 12 vị trí UNKNOWN → verdict ≠ `BUILD`,
  `can_proceed_to_app=False`, cho CẢ 12 vị trí, cộng ca 12/12 UNKNOWN. Không có thay đổi nào
  trong phiên này chạm lại cơ chế cap đó (`git diff` trên `failure_signals.py` phiên này = rỗng
  ngoài docstring — xem Changed Files Registry).
- **Thiếu bằng chứng không được coi là PASS**: CHECK-B1-04 (ngưỡng chưa phê chuẩn) và CHECK-B1-08
  (thiếu `pipeline_state.json` official) giữ `BLOCKED`/`NOT_TESTED` tường minh trong phiên này,
  KHÔNG bị gán PASS hay bị bỏ qua khỏi Completion Gate.
- **Một REQUIRED check `BLOCKED` không cho ra DONE**: mục 12 của Task Spec ("Chỉ đề xuất WP-B1
  DONE nếu ... không còn BLOCKING finding") được tuân thủ ở cuối phiên — xem báo cáo hoàn thành;
  WP-B1 KHÔNG được đề xuất DONE trong khi CHECK-B1-04/08/09 chưa PASS.
- **Run trên dữ liệu tổng hợp không được dùng thay official run (DEC-003)**: mọi test/regression
  trong phiên này (kể cả `test_e2e.py`, `test_benchmarks.py`) chạy trên `eth_dca_os.data.synth`,
  và được ghi rõ trong evidence là **mechanism/regression evidence**, KHÔNG được dùng để suy ra
  hay thay thế verdict/số liệu của official run T-06. CHECK-B1-08 (tính lại từ dữ liệu official
  thật) giữ nguyên là check RIÊNG, chưa PASS bằng bằng chứng synthetic.
- **Không finding nào bị đổi thành "sai" mà không có bằng chứng bác bỏ**: F-017 được XÁC NHẬN
  đúng như mô tả (đọc code trước sửa: một lệnh/tháng) rồi sửa — không có finding nào trong phiên
  này bị gắn nhãn "sai"/REJECTED.
- **Không ngưỡng nào bị hạ để verdict trở nên thuận lợi**: `git diff` phiên này trên
  `src/eth_dca_os/gates.py` = rỗng (file ngoài touch area, không chạm); các hằng số ngưỡng trong
  `failure_signals.py` (0.5/0.80/0.30/102.0/3.0/0.50/100.0) không đổi — xác nhận lại bằng
  `test_verdict_mapping`/`test_gate1_pass_and_fail`/`test_gate3_thresholds` (đều PASS, không sửa).
  `tests/test_wp_b1_verdict_policy.py::test_gate1_and_oos_fail_precedence_over_gate2_gate3` và
  `test_gate2_and_gate3_fail_together_is_inconclusive_not_do_not_build` chứng minh thêm precedence
  không bị đảo hay nới ở bất kỳ tổ hợp gate-fail đồng thời nào (Gate1/OOS luôn thắng, không có
  đường nào để 4-gate-FAIL vẫn ra khác `DO_NOT_BUILD`).

Test bổ sung (mới, phiên này): `tests/test_wp_b1_verdict_policy.py` — 12 test: precedence khi
nhiều gate fail đồng thời, `can_proceed_to_app` đúng nghĩa `verdict=="BUILD"` qua 6 tổ hợp
tham số hoá, numpy.bool_/bool equivalence ở tầng `gates.py` (họ H-26) không làm verdict sai,
determinism (cùng input → cùng output, kể cả input mang numpy type). 12/12 PASS.

**Addendum (cùng phiên, sau Owner Decision `DEC-033` + Owner-supplied CHECK-B1-08 evidence):**
gạch đầu dòng "Thiếu bằng chứng không được coi là PASS" ở trên mô tả đúng trạng thái TẠI THỜI
ĐIỂM viết (CHECK-B1-04/08 khi đó `BLOCKED`/thiếu input) — không phải một sự nới lỏng. Cả hai nay
đã PASS bằng bằng chứng thật (Owner Decision có thẩm quyền cho CHECK-B1-04; artifact official do
Owner cung cấp cho CHECK-B1-08), không phải bằng cách hạ tiêu chí. Xem evidence chi tiết tại
chính hai check đó.

**Addendum 2 — ĐẢO Status sau Independent E2 finding trên `CHECK-B1-03` (cùng phiên, tiếp nối):**
đây chính xác là trường hợp CHECK-B1-07 tồn tại để bắt: gạch đầu dòng "Thiếu bằng chứng không
được coi là PASS" ở trên đã bị VI PHẠM bởi chính agent — `CHECK-B1-03` được đóng khung `PASS`
trong khi evidence của chính nó nói rõ phần bắt buộc (tính lại FS-08 sau F-017) chưa thực hiện.
Đây không phải một finding từ bên ngoài không liên quan; nó là bằng chứng CHECK-B1-07 đã KHÔNG
được chứng minh đầy đủ như tuyên bố trước đó. Theo đúng chữ mục 8 của brief phiên này ("Reassess
CHECK-B1-07 only to the extent that its E2 failure was caused by missing CHECK-B1-03 evidence.
Do not broaden the scope"): PHẠM VI hẹp lại đúng gạch đầu dòng đó — năm gạch đầu dòng còn lại
(UNKNOWN không PASS, một BLOCKED không cho DONE, không dùng synthetic thay official, không đổi
finding thành sai không bằng chứng, không hạ ngưỡng) **KHÔNG bị ảnh hưởng**, vẫn đúng và có bằng
chứng riêng, không phụ thuộc CHECK-B1-03. Status hạ xuống `BLOCKED — pending CHECK-B1-03` (không
phải hạ toàn bộ nội dung) — sẽ tự động PASS lại ngay khi CHECK-B1-03 có đủ evidence (không cần
viết lại năm gạch đầu dòng kia).

**Addendum 3 — PHỤC HỒI `PASS` (cùng phiên, tiếp nối) sau khi CHECK-B1-03 có đủ evidence:**
CHECK-B1-03 nay `PASS` bằng POST-F-017 WP-B1 EVIDENCE REPLAY do Owner cung cấp (xem
CHECK-B1-03 Addendum 3) — 8/8 điều kiện xác minh cơ học khớp (`source_head`, `dataset_hash`,
`master_seed`, `n_sims`, `v2_eth` bit-for-bit khớp frozen, `beats_f`/`beats_g`/`FS-08` đúng công
thức). Đúng phạm vi hẹp đã nêu ở Addendum 2: KHÔNG viết lại năm gạch đầu dòng còn lại (chúng chưa
từng bị ảnh hưởng). `Status: BLOCKED — pending CHECK-B1-03 → PASS`.

**Addendum 4 — Fresh Independent E2 (`E2-WP-B1-002-FRESH-2026-09-04`) FAIL, repair, phục hồi
`PASS`:** reviewer tái lập được HAI đường production counterexample cho đúng câu hỏi mà
CHECK-B1-07 đặt ra ("có đường nào để BUILD/can_proceed_to_app=true lọt qua khi evidence chưa
đủ?") — CÓ, hai đường:

1. **E2-B1-F01**: FS-08 (ba input: `v2_eth` + hai Control P95) chỉ cần MỘT trong hai P95 hiện
   diện; P95 còn thiếu bị coi là "V2 tự động beat" thay vì UNKNOWN — vi phạm trực tiếp gạch đầu
   dòng "`UNKNOWN` không được coi là PASS ở bất kỳ đâu" của chính CHECK-B1-07 này (xem
   CHECK-B1-01 Addendum 2 để có repro/repair đầy đủ).
2. **E2-B1-F02**: `official` (tính trong `pipeline.run_verdict`) trước đây chỉ AND Gate 2/Gate 3
   (bỏ sót Gate 1 và Controls), và dù đủ bốn cũng CHỈ tạo một dòng `warning` — không hề chặn
   `can_proceed_to_app`. Non-official/dev-run evidence có thể mang `verdict=BUILD`,
   `can_proceed_to_app=true` — vi phạm cùng gạch đầu dòng đó theo một đường khác.

Cả hai đều là bằng chứng CHECK-B1-07 đã KHÔNG được chứng minh đầy đủ như Addendum 3 tuyên bố —
không phải finding ngoài phạm vi. Chấp nhận nguyên vẹn, không tranh cãi.

**Repair (một batch, cùng phạm vi CAP-VERDICT/WP-B1):**
- `src/eth_dca_os/failure_signals.py`: FS-08 đòi đủ cả ba input hợp lệ (không `None`, không
  NaN/non-numeric) mới tính; thiếu/invalid bất kỳ input nào → `None` (UNKNOWN). Xem chi tiết ở
  CHECK-B1-01 Addendum 2.
- `src/eth_dca_os/pipeline.py::run_verdict`: `official` nay AND đủ CẢ BỐN nguồn (Gate 1, Gate 2,
  Gate 3, Controls — mỗi cờ đã tự bao gồm điều kiện lineage đủ tư cách của nó, không phát minh
  provenance mới); khi `official=False` VÀ `can_proceed_to_app` đang `True` (từ `decide_verdict`),
  ép về `False` kèm lý do tường minh trong `reasons`. `verdict.py::decide_verdict` KHÔNG bị sửa
  (giữ nguyên là chính sách gate/FS thuần, không lẫn khái niệm officiality — officiality được
  chặn đúng một chỗ duy nhất, tại điểm `run_verdict` đã có sẵn đủ bốn cờ).

Test mới (`tests/test_wp_b1_e2_fresh_fail_repair.py`, 21 test): CASE A (official đầy đủ + BUILD-
eligible → không đổi hành vi, `can_proceed_to_app=True`), CASE B/C (thiếu từng control → FS-08
UNKNOWN → không BUILD được), CASE D (non-official toàn phần → `can_proceed_to_app=False`), thiếu
từng thành phần official riêng lẻ (Gate1/Gate2/Gate3/Controls, 4 test tham số hoá) đều buộc
`can_proceed_to_app=False`, `controls=None` không crash và không lọt `can_proceed_to_app=true`,
và CASE E (provenance unresolved trong khi tuyên bố official → `ProvenanceUnresolvedError` từ
cơ chế `save_run()` có sẵn từ WP-A1 — không cần sửa gì, chỉ xác nhận bằng test là cơ chế đó vẫn
chặn đúng, không để payload lọt ra ngoài).

`Status: FAIL → PASS`. Phạm vi vẫn hẹp đúng như Addendum 2/3 đã cam kết: năm gạch đầu dòng còn
lại (đã liệt kê ở Addendum 2) không bị viết lại, không phụ thuộc lần sửa này.

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại)

Timestamp:
2026-09-04

#### CHECK-B1-08 — Verdict được tính lại từ kết quả đã lưu và kết quả được ghi nhận
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
**Không tự phê chuẩn/không tự tổng hợp thay.** `pipeline_state.json` của official run T-06 (và
toàn bộ `results/` khác) là artifact được **chủ dự án bảo toàn ĐỘC LẬP BÊN NGOÀI repository**
(`docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §4: "16/16 file, SHA-256 verify PASS" — bảo toàn ngoài
repo; `find` toàn repo trong phiên này xác nhận file KHÔNG tồn tại tại bất kỳ đường dẫn nào trong
`/home/user/coin`). Agent trong phiên này KHÔNG có quyền truy cập môi trường của chủ dự án và
KHÔNG được rerun official run (Master Index §6 cấm tuyệt đối — xem Out of Scope).

Vì DEC-009 đã kết luận KHÔNG (CHECK-B1-02) — Gate 1 hiện có vẫn hợp lệ — việc còn thiếu DUY NHẤT
để đóng check này là: chủ dự án cung cấp `pipeline_state.json` (hoặc tự chạy `ethdca verdict
--what all` trên máy có artifact đó) để agent/reviewer tính lại verdict bằng
`src/eth_dca_os/verdict.py::decide_verdict` hiện tại (đã qua F-S015-01 + F-017) và xác nhận verdict
vẫn là `DO_NOT_BUILD` với lý do `Gate 1 FAIL`/`OOS hard condition FAIL` giống T-06 gốc — phù hợp
với regression oracle "frozen/historical verdict inputs" mà brief phiên này cho phép dùng
(§5): S016 đã làm chính xác việc này trên **synthetic** BEFORE/AFTER cho lát cắt F-S015-01 (biên
bản S016 §7, verdict `DO_NOT_BUILD` giống hệt hai bên), nhưng đó KHÔNG thay thế được việc tính lại
trên dữ liệu OFFICIAL thật mà check này đòi hỏi.

`MISSING_INPUT`:
- Cần: `pipeline_state.json` của official run T-06 (hoặc quyền chạy `ethdca verdict` trực tiếp
  trên máy đang giữ `results/` official).
- Nguồn bắt buộc: chủ dự án (người đang bảo toàn artifact này bên ngoài repo).
- `OWNER_INPUT_REQUIRED`: cung cấp file, hoặc tự chạy lệnh và dán lại output đầy đủ
  (verdict + reasons + can_proceed_to_app) để ghi vào đây.

WP-B1 **không được DONE** khi check này chưa PASS.

**Kết quả — ĐÃ THOẢ (Owner-supplied evidence, cùng phiên, read-only trên bản backup):**

Owner thực hiện read-only verification trên COPY của frozen official T-06 backup
(`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03`), chạy
`ethdca verdict --out-dir results` (đọc `results/pipeline_state.json`). Không rerun T-06. Không
sửa artifact nào.

1. **`pipeline_state.json` xác nhận verdict/can_proceed_to_app**: `ethdca verdict` in ra
   `verdict = DO_NOT_BUILD`, `can_proceed_to_app = false`. Trường `reasons` hiển thị dưới dạng
   chuỗi literal `"[2 items]"` thay vì mảng đầy đủ.

2. **`reasons` bị compact trong `pipeline_state.json` — HÀNH VI THIẾT KẾ, không phải lỗi mới
   phát sinh**: đọc `src/eth_dca_os/cli.py::_strip()` xác nhận MỌI list/tuple trong payload bị
   thay bằng `f"[{len(d)} items]"` trước khi ghi `pipeline_state.json` ("lưu state gọn để
   `verdict` đọc lại" — comment tại chỗ gọi, `cli.py` dòng ~116). `reasons` là một list nên bị
   compact. Xác nhận thêm bằng chính docstring `reporting.py::write_report()`: "Khác
   `pipeline_state.json` ở chỗ KHÔNG rút gọn list: state file chỉ để CLI đọc lại nhanh, còn
   file này giữ nguyên số liệu (reasons, per-window AE, failure signals...)." — tức là
   `pipeline_state.json` **CHƯA TỪNG được thiết kế** để là nguồn full-fidelity cho `reasons`;
   `report.json` và mỗi `*_metrics.json` (ghi bởi `save_run()`, KHÔNG qua `_strip()`) mới là
   file "đầy đủ, không rút gọn" — ghi ra từ CÙNG một lần gọi `run all`, CÙNG một object
   `verdict_payload` trong bộ nhớ, trước khi bản copy ghi vào `pipeline_state.json` bị nén.

3. **Full reasons cross-verified từ hai artifact khác CÙNG gói frozen official evidence** (cả
   hai đã được canonical hoá với SHA-256 độc lập tại `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`
   §4 — không phải dữ liệu mới/chưa kiểm chứng):
   - `results/baseline_808b61fa5ffe_metrics.json` — ghi bởi `save_run(out_dir, "BASELINE",
     payload, ...)` bên trong `pipeline.py::run_verdict()`, payload KHÔNG qua `_strip()`:
     `verdict = DO_NOT_BUILD`, `reasons = ["Gate 1 FAIL", "OOS hard condition FAIL"]`,
     `can_proceed_to_app = false`.
   - `results/report.json` — ghi bởi `write_report()` (theo đúng docstring trên): cùng
     `verdict = DO_NOT_BUILD`, cùng hai reasons, cùng `can_proceed_to_app = false`.
   - `backtest_runs.jsonl` (dòng `run_id = baseline_808b61fa5ffe`) corroborate:
     `code_commit = 5228130677e9e9875335eef890b6ed748a384603` (khớp official commit tại
     `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`/`DEC-031`), `dataset_hash =
     3150860cb3799403ff40620b6834e4826681893e2e5cd2af3ca815d2a652d2c5`,
     `python_version = 3.11.16`, `official = true` — buộc chặt bản ghi verdict này vào đúng
     official run T-06, không phải một run nào khác.

4. **Đánh giá acceptance criteria — CÓ cho phép cross-artifact evidence trong trường hợp
   này**: chữ CHECK-B1-08 ("chạy `ethdca verdict` trên `pipeline_state.json` ... ghi lại
   verdict cuối cùng cùng toàn bộ lý do") không đòi "toàn bộ lý do" phải nằm ở ĐÚNG BYTE mà
   lệnh CLI in ra — nó đòi bằng chứng verdict + lý do đầy đủ, chính xác, từ official run, làm
   đầu vào T-07. `report.json`/`baseline_*_metrics.json` không phải "nguồn khác" hay "suy diễn
   mới": chúng là companion file ĐƯỢC CHÍNH THIẾT KẾ HỆ THỐNG (`write_report()` docstring) chỉ
   định là bản đầy đủ, sinh ra cùng lúc, từ cùng phép tính, thuộc cùng gói official evidence đã
   canonical hoá. Không có suy đoán, không có tính toán mới, không có dữ liệu ngoài gói
   official. Vì vậy: **PASS**, với điều kiện ghi rõ đầy đủ bốn điểm ở trên (không được tuyên bố
   "pipeline_state.json tự nó chứa full reasons").

5. **Không rerun official experiment.** Không artifact nào bị sửa (Owner thao tác trên bản
   copy, `ethdca verdict` xác nhận read-only qua đọc code — xem đánh giá phiên trước).

**Verdict chính thức được ghi nhận làm đầu vào T-07** (nguyên văn, từ `baseline_808b61fa5ffe_
metrics.json`/`report.json`, cùng khớp `pipeline_state.json`):

    verdict            = DO_NOT_BUILD
    reasons            = ["Gate 1 FAIL", "OOS hard condition FAIL"]
    can_proceed_to_app = false

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại) — đánh giá evidence chain do chủ dự án
cung cấp, không tự tính toán/suy diễn số liệu mới

Timestamp:
2026-09-03

### Audit độc lập

#### CHECK-B1-09 — Rà soát độc lập E2 cho chính sách verdict và cho kết luận DEC-009
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: phiên reviewer độc lập theo "Solo Independent Review Procedure", kiểm lại **đặc biệt**
CHECK-B1-01, CHECK-B1-02 và CHECK-B1-07, coi mọi tuyên bố PASS của người cài đặt là narrative chưa
tin được. Reviewer phải tự trả lời câu hỏi: *có đường nào để một verdict BUILD lọt qua khi bằng
chứng chưa đủ không?* Lưu tại `docs/reviews/`.

**Ghi nhận (phiên WP-B1 IN_PROGRESS hiện tại):** check này đòi một phiên reviewer ĐỘC LẬP — cùng
một agent/phiên vừa cài đặt (CHECK-B1-02/03/05/06/07 ở trên) không thể tự cấp E2 cho chính mình
(đó chính xác là điều check này tồn tại để ngăn). Giữ **`NOT_TESTED`**, không tự nhận PASS. Cần
một phiên riêng (`docs/reviews/E2-WP-B1-*.md`), do reviewer chưa đọc kết luận implementer trước
khi tự tái lập, đúng "Solo Independent Review Procedure" đã áp dụng cho `WP-A1`/`WP-A6`.

Executed By:
(chưa — cần phiên độc lập riêng)

Timestamp:
...

### Regression

#### CHECK-B1-10 — Toàn bộ test suite PASS; không test nào bị skip hoặc nới lỏng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
`python -m pytest tests/ -q -p no:cacheprovider` (venv sạch, `pip install -e ".[dev]"`, sau đó
ghim lại đúng phiên bản transitive dependency của `requests` theo `pyproject.lock` — venv ban đầu
lệch do PyPI có bản patch mới hơn kể từ khi lockfile được sinh; đây là artifact môi trường phiên
này, KHÔNG phải regression code, xác nhận bằng `test_a1_08_lockfile_matches_installed_environment`
PASS trở lại sau khi ghim đúng phiên bản, không sửa `pyproject.lock` hay bất kỳ file production
nào để né check).

**Kết quả (lần chạy đầu, trước repair E2-B1-F01/F02): 391 tests collected, 391 PASS, 0 FAIL, 0
ERROR, 0 SKIP, 0 XFAIL. `EXIT=0`.** (addopts `-q` trong `pyproject.toml` không in dòng tổng kết
dạng "N passed" — đếm bằng số `.` trong log, đối chiếu `EXIT=$?`). Không test nào bị skip/xfail/
deselect. Không sửa/xoá/nới lỏng test nào có sẵn trong phiên này — chỉ SỬA 2 test hiện có cho
khớp chữ ký hàm mới (`test_random_controls_reproducible` trong `test_benchmarks.py`, call site
trong `test_e2e.py`) và THÊM test mới (không bớt assertion nào của hai test được sửa — số lượng
assertion tăng, phạm vi kiểm không giảm).

**Kết quả (lần chạy thứ hai, sau repair batch E2-B1-F01/F02, cùng phiên tiếp nối 2026-09-04):
412 tests collected, 412 PASS, 0 FAIL, 0 ERROR, 0 SKIP, 0 XFAIL. `EXIT=0`.** Khớp đúng số học:
391 + 21 test mới (`tests/test_wp_b1_e2_fresh_fail_repair.py`) = 412. `test_gates_verdict.py::
test_fs08_random_control` SỬA (không xoá/nới) case đầu để phản ánh đúng hành vi fail-closed mới
— xem CHECK-B1-01 Addendum 2.

Executed By:
Sonnet 5, phiên WP-B1 IN_PROGRESS (session hiện tại)

Timestamp:
2026-09-03

## Exit Criteria
- [ ] 100% REQUIRED checks PASS — **9/10 PASS** (01,02,03,04,05,06,07,08,10); `NOT_TESTED`/FAIL:
      CHECK-B1-09 (fresh Independent E2 tái lập E2-B1-F01/F02, đã sửa xong, CHƯA chạy lại E2 mới)
      — check REQUIRED duy nhất còn lại
- [ ] Mức evidence yêu cầu được thoả (E1 toàn bộ; E2 cho CHECK-B1-09) — E1 đạt cho 9 check PASS
      (gồm CHECK-B1-01/07 phục hồi bằng repair E2-B1-F01/F02 + 21 regression test mới); E2 của
      CHECK-B1-09 CHƯA chạy lại
- [x] **DEC-009 được chứng minh, không chỉ được nhắc tới** — CHECK-B1-02, kết luận KHÔNG, bằng
      chứng đường mã kiểm lại được độc lập
- [x] Mọi quy ước ảnh hưởng verdict đều truy được về `docs/CONVENTIONS.md` — #20(d) (WP-A5) +
      #21(a)-(e) (phiên này, gồm phê chuẩn ngưỡng tại #21(e)/`DEC-033`)
- [x] Verdict cuối cùng (T-06 lịch sử) được ghi nhận kèm toàn bộ lý do — CHECK-B1-08 PASS:
      `DO_NOT_BUILD` / `["Gate 1 FAIL", "OOS hard condition FAIL"]` / `can_proceed_to_app=false`,
      cross-verified từ `baseline_808b61fa5ffe_metrics.json` + `report.json` cùng gói official
      (Owner-supplied). Verdict lịch sử này KHÔNG đổi bởi FS-08 post-F-017 (đã quyết ở nhánh
      Gate 1/OOS FAIL, trước khi FS được xét — xem CHECK-B1-02)
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-005 được cập nhật
- [x] Session handoff được viết
- [x] Không hạ REQUIRED check nào để đạt DONE — mọi Independent E2 finding (CHECK-B1-03 lần 1,
      E2-B1-F01/F02 lần 2) được CHẤP NHẬN nguyên vẹn, không tranh cãi/bypass; check liên quan ĐẢO
      về `BLOCKED`/`FAIL` đúng như finding đòi hỏi, không giữ `PASS` giả; mọi lần phục hồi `PASS`
      đều SAU KHI có evidence/repair thật (evidence replay xác minh 8/8; repair E2-B1-F01/F02 xác
      minh bằng 21 regression test mới) — không tự nới; CHECK-B1-09 KHÔNG tự chạy lại/tự cấp PASS
      trong phiên này, giữ nguyên `NOT_TESTED`/FAIL lịch sử cho tới khi có phiên E2 mới

## Escalation Triggers

- Ngưỡng FS chưa được chủ dự án phê chuẩn → `MISSING_INPUT`, CHECK-B1-04 = `BLOCKED`, gói không DONE.
  KHÔNG tự phê chuẩn thay chủ dự án.
- DEC-009 kích hoạt và việc chạy lại Gate 1 kéo theo phải chạy lại cả Gate 2/3 → `SCOPE_CHANGED`,
  dừng và trình chủ dự án: đó là một vòng lặp lớn hơn về T-06, phải được quyết định chứ không tự làm.
- Phát hiện chính sách đúng đắn sẽ dẫn tới verdict không thuận lợi → **không phải escalation**. Đó là
  gói đang làm đúng việc của nó. Ghi nhận và tiếp tục.
- Muốn chạy lại official run để "làm sạch" số liệu → DỪNG. Master Index §6 cấm. Chỉ chạy lại phần
  bắt buộc theo DEC-009 và ghi rõ lý do là tính hợp lệ.
- Ba Failure Signal vẫn UNKNOWN vì WP-A5 không được thực hiện trước T-06 → `MISSING_INPUT`, BLOCKED.
  Không được gán giá trị mặc định để gỡ bí.

## Ảnh hưởng nếu gói này thất bại

GATE-B không đóng → T-07 (DUYỆT verdict) không mở → T-11 không mở. Nếu bỏ qua: verdict có thể là
BUILD trong khi ba Failure Signal chưa từng được đánh giá và ngưỡng quyết định thì không truy được
về đâu ra. Đó chính là cổng mở đường cho toàn bộ giai đoạn app
(`can_proceed_to_app = (v == "BUILD")`) — mở nhầm cổng này là hỏng ở mức nghiêm trọng nhất mà dự án
có thể hỏng.

## Changed Files Registry

Created:
- `tests/test_wp_b1_slice_failure_signal_cap.py` (lát cắt DEC-026, S016)
- `docs/sessions/S016-wp-b1-lat-cat-dec026.md` (lát cắt DEC-026, S016)
- `tests/test_wp_b1_verdict_policy.py` (phiên hiện tại — CHECK-B1-07: precedence, can_proceed,
  numpy/bool equivalence, determinism)
- `docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-fail.md` (Owner/reviewer, KHÔNG phải agent phiên
  này — artifact E2 fresh FAIL, tái lập E2-B1-F01/F02)
- `tests/test_wp_b1_e2_fresh_fail_repair.py` (phiên hiện tại — 21 test cho repair E2-B1-F01/F02)
- (dự kiến, cần phiên riêng) `docs/reviews/E2-WP-B1-*.md` khác (E2 mới cho CHECK-B1-09 sau repair)

Modified:
- `src/eth_dca_os/failure_signals.py` (lát cắt DEC-026, S016 — chuẩn hoá kiểu + cờ chặn; phiên
  hiện tại — FS-08 [E2-B1-F01] đòi đủ cả ba input hợp lệ, thêm helper `_numeric_and_finite()`)
- `tests/test_wp_a5_failure_signal_instrumentation.py` (lát cắt DEC-026, S016 — xoá test đánh dấu
  F-S015-01; khoá CHECK-A5-07 vào khoảng `b095874..d4586b8`)
- `src/eth_dca_os/benchmarks.py` (phiên hiện tại — F-017: `random_timing_control`/
  `random_anchor_control` nhận `monthly_tranches` per-tranche thay vì `monthly_deployments`
  scalar/tháng; random hóa độc lập theo từng tranche)
- `src/eth_dca_os/pipeline.py` (phiên hiện tại — `run_gate1` dựng `monthly_tranches` từ
  `full.purchases`; `run_controls` đổi tên tham số theo; `run_verdict::official` nay AND đủ 4
  nguồn [E2-B1-F02] + ép `can_proceed_to_app=False` khi không official)
- `src/eth_dca_os/cli.py` (phiên hiện tại — cập nhật call site theo khoá payload mới
  `_full_run_monthly_tranches`)
- `tests/test_benchmarks.py` (phiên hiện tại — cập nhật fixture theo định dạng tranche-list;
  thêm 2 test F-017)
- `tests/test_e2e.py` (phiên hiện tại — cập nhật call site theo khoá payload mới)
- `tests/test_gates_verdict.py` (phiên hiện tại — sửa `test_fs08_random_control` case đầu, vốn
  vô tình mã hoá đúng hành vi lỗi E2-B1-F01)
- `docs/CONVENTIONS.md` (phiên hiện tại — mục #21(a)-(e): ánh xạ gate-fail→verdict, chính sách
  UNKNOWN, `shift_days=10`, Control F/G per-tranche, phê chuẩn ngưỡng FS-02/FS-07/FS-12)
- `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md` (phiên hiện tại — evidence
  CHECK-B1-01/02/03/04/05/06/07/08/10, subtask B1.2-B1.8)
- `PROJECT/PROJECT_DECISIONS.md` (phiên hiện tại — `DEC-033`, Owner Decision APPROVE AS-IS ba
  ngưỡng FS-02/FS-07/FS-12, đóng CHECK-B1-04)

Deleted:
- Không

Migration Impact:
- DEC-009 KHÔNG kích hoạt (CHECK-B1-02: KHÔNG, có bằng chứng đường mã) — không có kết quả Gate 1
  nào bị đánh dấu STALE/INVALIDATED trong phiên này.
- `engine.py` KHÔNG bị chạm (F-017 sửa xong bằng dữ liệu `full.purchases` đã có sẵn) — không có
  migration nào cho `Result`/`engine.Result.monthly_deployments` (field này vẫn còn, dùng cho
  mục đích khác ngoài Control F/G).
- Payload key `_full_run_monthly_deployments` (dict tổng nominal/tháng) đổi tên/đổi ngữ nghĩa
  thành `_full_run_monthly_tranches` (dict tháng → list nominal từng tranche). Bất kỳ script/
  notebook nào bên ngoài `src/`/`tests/` đọc trực tiếp khoá cũ từ `GATE1` run record cần cập nhật
  theo — không có script như vậy trong repo tại thời điểm sửa (đã grep toàn `src/`, `tests/`,
  `docs/`).
- Không có migration code nào cho CHECK-B1-08: `pipeline_state.json` compact `reasons` thành
  chuỗi `"[N items]"` là hành vi THIẾT KẾ có sẵn từ trước phiên này (`cli.py::_strip()`,
  `reporting.py::write_report()` docstring) — không sửa, không cần migrate. Ghi nhận vào evidence
  CHECK-B1-08 để phiên/reviewer sau không hiểu nhầm `pipeline_state.json` là nguồn full-fidelity
  cho `reasons`.
- `DEC-033` không đổi giá trị ngưỡng nào — không có migration nào cho `failure_signals.py`.
- **E2-B1-F01 behavior change**: bất kỳ caller nào trước đây phụ thuộc vào FS-08 tự resolve
  thành TRUE/FALSE khi chỉ CÓ MỘT trong hai Control P95 (hành vi cũ, sai) nay sẽ nhận `None`
  (UNKNOWN) — đây là thay đổi HÀNH VI CÓ CHỦ ĐÍCH (fix bug fail-open), không phải regression.
  Không có call site nào khác trong repo gọi `evaluate_failure_signals` với đúng một control
  (đã grep `random_timing_p95=`/`random_anchor_p95=` toàn `src/`) — chỉ `pipeline.run_verdict`
  gọi với cả hai cùng lúc (từ cùng khối `controls`), nên thay đổi này không ảnh hưởng call site
  production nào ngoài đúng ca lỗi đang sửa.
- **E2-B1-F02 behavior change**: bất kỳ dev/non-official run nào trước đây vô tình đọc được
  `can_proceed_to_app=true` (khi verdict=BUILD nhưng dữ liệu không official) nay sẽ luôn thấy
  `false` kèm lý do trong `reasons`. Đây cũng là thay đổi HÀNH VI CÓ CHỦ ĐÍCH — không ai được
  phép coi một dev run là đủ điều kiện mở app stage. `warning` text cập nhật để nói rõ
  `can_proceed_to_app` đã bị ép về false, không chỉ cảnh báo suông.
- Verdict lịch sử T-06 (`DO_NOT_BUILD`, `can_proceed_to_app=false`, official=true) hoàn toàn
  KHÔNG bị ảnh hưởng bởi cả hai sửa — verdict đã dừng ở nhánh Gate 1/OOS FAIL từ trước khi FS-08
  hay officiality-gate được xét tới, và T-06 vốn official=true nên officiality-gate mới không
  đổi gì ở đó.

## Notes

DEC-009 tồn tại để chặn một tình huống rất cụ thể: verdict được tính trên **hỗn hợp** kết quả Gate 1
sinh bởi code cũ và kết quả Gate 3/controls sinh bởi code mới. Hai nửa đó có thể không tương thích
mà không có gì báo động. Chi phí chấp nhận được (một vòng lặp về T-06) đã được chủ dự án cân nhắc và
phê duyệt.

Lưu ý về sự khác nhau giữa hai loại "chạy lại": Master Index §6 cấm chạy lại official run **để cải
thiện kết quả**. DEC-009 yêu cầu chạy lại Gate 1 **vì kết quả cũ không còn hợp lệ**. Khi ghi nhận,
phải ghi rõ thuộc loại thứ hai, kèm lý do — nếu không, về sau sẽ không phân biệt được.
