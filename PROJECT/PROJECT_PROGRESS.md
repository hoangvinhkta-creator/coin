# PROJECT PROGRESS

## Project Summary
Project:
ETH DCA Operating System — V2.1.5

Objective:
Xây một công cụ chạy trên trình duyệt, dùng được như bảng tính, để chủ dự án theo dõi quá trình
hold/trade coin và nhận cảnh báo dựa trên các chỉ báo phân tích của bộ spec V2.1.5
(OSCORE, regime, ladder zone, giới hạn thực thi, chất lượng dữ liệu).

Ràng buộc chi phối mục tiêu này: Implementation Plan đặt cổng chặn — app MVP đầy đủ chỉ được
dựng sau khi backtest cho verdict BUILD. Xem `PROJECT/PROJECT_DECISIONS.md` DEC-005.

Project Type:
LEGACY

Profile:
PRODUCT

Governance Version:
V3.2 (compact) + **AI Engineering V4.3 overlay** (adopted 2026-09-01).
Canonical AI entry point: `AGENTS.md`. CORE V4.3: `governance/v4/CORE/`.
Adoption record: `docs/decisions/ADOPTION-V4_3-migration-record.md`.
Adoption KHÔNG đổi trạng thái task nào, KHÔNG tạo task ID nào, KHÔNG sửa production code.

Last Updated:
2026-09-04 — **OWNER DECISION `DEC-035` — APPROVE PA-A + CHẤP NHẬN `ADR-001`: `WP-C2: BLOCKED →
READY`.** Tiếp nối phiên chuẩn bị (nhánh `claude/wp-c2-scope-adr-dec005-8o6fvr`). Chủ dự án phê
duyệt nguyên văn qua chat: *"APPROVE PA-A CHO DEC-035, VÀ CHẤP NHẬN ADR-001."* — phân xử HẸP cho
Ready Gate của `WP-C2` (không chờ `DEC-005` chốt theo nghĩa rộng cho webapp) và chấp nhận
`docs/adr/ADR-001-wp-c2-execution-state-scope.md` (`FUNDING_REQUIRED` = `NOT_APPLICABLE` ở tầng
backtest). Cả hai dòng Ready Gate còn `[ ]` của `WP-C2` nay `[x]`. **`WP-C2`: `BLOCKED` →
`READY`.** `DEC-005` (nghĩa rộng, webapp) **VẪN PENDING**, tiếp tục chặn `T-08` — quyết định này
KHÔNG đóng `DEC-005`. `WP-C2` **CHƯA `IN_PROGRESS`, CHƯA `DONE`** — mở/thực thi task (subtask
C2.1–C2.6, Completion Gate 8/8 REQUIRED, FROZEN không đổi) cần một phiên riêng, theo hợp đồng
`docs/reviews/WP-C2-SCOPE-ADR-DEC005-REPORT.md` §14. `WP-B3` KHÔNG tự động đổi (vẫn `BLOCKED`,
chờ `WP-C2` thật sự `DONE`). `GATE-B`, `T-07`, `T-11` không đổi. Không production code nào bị
sửa (`docs/adr/`, `docs/tasks/`, `PROJECT/*.md`). Không task ID mới, không tiêu review/repair
budget nào. Chi tiết: `DEC-035` (`PROJECT_DECISIONS.md`), `docs/tasks/WP-C2-execution-state-machine.md`,
`docs/adr/ADR-001-wp-c2-execution-state-scope.md`.

Trước đó, cùng ngày — **WP-C2 SCOPE ADR / DEC-005 RESOLUTION (phiên chuẩn bị quyết định, nhánh
`claude/wp-c2-scope-adr-dec005-8o6fvr`) — KHÔNG có quyết định nào được chốt, chỉ chuẩn bị.**
Phiên tái dựng canonical blocker của `WP-C2` (BLOCKED, hai dòng Ready Gate chưa `[x]`: (1)
`DEC-005` chưa chốt tại `T-05`, (2) ADR phạm vi Execution State chưa tồn tại), xác nhận lại
`DEC-030` (`T-05` chỉ chặn `T-08` và `WP-C2`, không nằm trên đường găng tới `T-06`/verdict).
Kết luận: phạm vi ĐÃ ĐÓNG BĂNG của `WP-C2` không chạm `webapp/` và không xây tầng tự động hoá,
nên dòng Ready Gate (1) có thể được phân xử bằng một quyết định HẸP hơn toàn bộ `DEC-005`
(webapp scope PA-1/2/3) — ghi đề xuất tại `DEC-035` (PENDING), kèm bản soạn
`docs/adr/ADR-001-wp-c2-execution-state-scope.md` (Status: Proposed — `FUNDING_REQUIRED` =
`NOT_APPLICABLE` ở tầng backtest, khớp quy ước đã canonical `docs/CONVENTIONS.md` #8) cho dòng
Ready Gate (2). Báo cáo đầy đủ (bằng chứng, phương án, khuyến nghị, hợp đồng phiên thực thi
tương lai của `WP-C2`, đường găng sau quyết định):
`docs/reviews/WP-C2-SCOPE-ADR-DEC005-REPORT.md`.

**`OWNER_DECISION_REQUIRED`** — chưa có quyết định nào được Owner phê chuẩn. `WP-C2` **VẪN
BLOCKED**. `DEC-005` **VẪN PENDING**, tiếp tục chặn `T-08`. Không đổi trạng thái bất kỳ task nào
khác (`WP-B1` DONE, `WP-B2` READY, `WP-B3` BLOCKED, `GATE-B` CHƯA MỞ, `T-07` NOT READY, `T-11`
BLOCKED — tất cả giữ nguyên). Production diff phiên này = **ZERO** (chỉ `docs/adr/`,
`PROJECT/PROJECT_DECISIONS.md`, `PROJECT/PROJECT_PROGRESS.md`,
`docs/reviews/WP-C2-SCOPE-ADR-DEC005-REPORT.md`). Không implement `WP-C2`. Không chạy
WP-B2/WP-B3, không mở GATE-B/T-07, không rerun T-06, không đổi threshold/strategy, không merge
`main`.

Trước đó, 2026-09-04 — **LIFECYCLE CLOSURE: `WP-B1: IN_PROGRESS → DONE`** (`DEC-034`, phiên Lifecycle
Closure, nhánh `claude/wp-b1-verdict-correctness-j9d390`). Chủ dự án uỷ quyền tường minh chấp
nhận fresh Independent E2 vòng BA (`E2-WP-B1-004-FRESH-ROUND3-2026-09-04`,
`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-round3-pass.md`) làm completion evidence: reviewer mới,
độc lập với implementer VÀ với hai reviewer trước, review đúng HEAD
`9ac01b8d3df19a68244b05f14a66f8a4ff9b90c0`, tái lập độc lập cả hai finding lịch sử
`E2-B1-F01`/`E2-B1-F02` là ĐÃ ĐÓNG, CHECK-B1-01/02/03/04/07/08/10 PASS, không tìm BLOCKING mới
(hai quan sát `H-27`/`aggregate_over_windows ±inf` ghi HARDENING-only), full suite tự chạy
461/461 PASS. Artifact tích hợp vào nhánh canonical bằng fast-forward merge
(`9ac01b8..f3fb81e`), production diff của lượt tích hợp = **ZERO**.

`CHECK-B1-09: NOT_TESTED → PASS`. **`WP-B1` nay `10/10 REQUIRED PASS`** (01-10). Completion
Gate = PASS. `WP-B1: IN_PROGRESS → DONE`. Không tiêu repair cycle mới (production diff phiên
đóng lifecycle = 0). Verdict lịch sử `T-06` (`DO_NOT_BUILD`,
`["Gate 1 FAIL","OOS hard condition FAIL"]`, `can_proceed_to_app=false`) hoàn toàn KHÔNG đổi —
`WP-B1 DONE` nghĩa là năng lực Verdict Correctness đạt Completion Gate, KHÔNG phải `V2.1.5`
chứng minh được investment edge. Không rerun T-06, không replay Control F/G, không đổi
threshold/strategy, không merge `main`, không xoá branch.

**Downstream KHÔNG đổi tự động chỉ vì WP-B1 đóng:** `WP-B2` giữ `READY`; `WP-B3` giữ `BLOCKED`
(dependency `WP-C2` chưa DONE); `GATE-B` (đòi cả `WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`) **VẪN CHƯA
MỞ** vì `WP-B2`/`WP-B3` chưa `DONE`; `T-07` vẫn `NOT READY` (chờ `GATE-B`); `T-11` vẫn `BLOCKED`.
Phiên này KHÔNG chạy WP-B2/WP-B3, KHÔNG mở GATE-B, KHÔNG chạy T-07. Chi tiết đầy đủ: `DEC-034`,
`docs/tasks/WP-B1-*.md` (CHECK-B1-09), `docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-round3-pass.md`,
`docs/sessions/S023-*.md` (addendum đóng lifecycle).

Trước đó, 2026-09-04 — **Fresh Independent E2 VÒNG HAI (`E2-WP-B1-003-FRESH-AFTER-REPAIR-2026-09-04`,
`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-after-repair-fail.md`) FAIL trên chính bản sửa vòng 1 →
repair batch 2 → `CHECK-B1-01`/`CHECK-B1-07` phục hồi `PASS` lần thứ hai.** Reviewer độc lập
(khác cả implementer lẫn reviewer vòng 1) review đúng HEAD mang bản sửa vòng 1
(`82ff39c94685151f94764c158b0b3b10c53d7d6f`) và tái lập được CẢ HAI finding CHƯA đóng hết
(không phải finding mới, cùng ID `E2-B1-F01`/`E2-B1-F02`):

1. **`E2-B1-F01` (còn hở):** `_numeric_and_finite()` (Addendum 4/repair batch 1) chỉ loại
   `None`/NaN bằng `not math.isnan(float(x))` — công thức này KHÔNG loại `+inf`/`-inf`
   (`math.isnan(inf)` là `False`). Tái lập trước sửa: `evaluate_failure_signals(v2_eth=10.0,
   random_timing_p95=float("-inf"), random_anchor_p95=9.5)` → `FS-08=False` (đúng như finding
   mô tả) → `decide_verdict` → `verdict=BUILD`, `can_proceed_to_app=True`.
2. **`E2-B1-F02` (còn hở):** repair batch 1 chỉ ép `can_proceed_to_app=False` khi
   `official=False`, nhưng ĐỂ NGUYÊN `v["verdict"]="BUILD"` — cả trong giá trị trả về LẪN bản
   ghi đã persist (`backtest_runs.jsonl`, `*_metrics.json` qua `save_run(...,
   verdict=v["verdict"])`). Reviewer tái dựng canonical interpretation A trực tiếp từ frozen
   text (Objective + CHECK-B1-01/07/09): evidence non-official phải ngăn CẢ `verdict=BUILD`
   LẪN `can_proceed_to_app=true` — không phải chỉ progression flag. Tái lập trước sửa: 6/6 tổ
   hợp non-official (từng nguồn/nhiều nguồn/tất cả) đều `official=False`,
   `can_proceed_to_app=False` NHƯNG `verdict` vẫn in ra literal `"BUILD"`.

Chấp nhận nguyên vẹn cả hai, không tranh cãi/bypass — đây là dạng "sibling fail-open path tại
cùng verdict boundary" mà quy trình review đòi tìm, không phải finding ngoài phạm vi.

**Repair batch 2** (cùng CAP-VERDICT/WP-B1, hai file y hệt batch 1):
`src/eth_dca_os/failure_signals.py::_numeric_and_finite()` viết lại: loại `None`; loại tường
minh `bool` (Python `bool` là subclass của `int` nên `float(True)==1.0` sẽ lọt nếu không chặn
riêng); `numpy.bool_` tự động bị loại vì KHÔNG phải instance của `numbers.Real` (khác
`numpy.float64`, có đăng ký ABC này); kiểm `isinstance(x, numbers.Real)` TRƯỚC khi ép kiểu
(loại chuỗi/object mà không cần dựa vào exception); cuối cùng `math.isfinite(float(x))` — loại
ĐÚNG cả NaN lẫn `±inf`. `src/eth_dca_os/pipeline.py::run_verdict`: khi
`not official and v["verdict"] == "BUILD"`, hạ **verdict** về `"INCONCLUSIVE"` (tái dùng đúng
một trong bốn nhãn có sẵn — `BUILD`/`BUILD_WITH_MODIFICATIONS`/`INCONCLUSIVE`/`DO_NOT_BUILD`,
không phát minh trạng thái thứ năm) VÀ ép `can_proceed_to_app=False`; các nhánh verdict khác
vốn đã có `can_proceed_to_app=False` nên không cần chạm (hợp đồng `decide_verdict`:
`can_proceed_to_app` chỉ `True` khi `verdict=="BUILD"`). `decide_verdict()` không đổi cho
evidence official — case toàn official vẫn `verdict=BUILD`/`can_proceed_to_app=True` y hệt
trước, xác nhận repair không "xoá BUILD khỏi hệ thống".

70 regression test tổng cộng qua hai batch (`tests/test_wp_b1_e2_fresh_fail_repair.py` 21 +
`tests/test_wp_b1_e2_fresh_fail_repair_v2.py` 49 mới): ma trận `_numeric_and_finite` đầy đủ
(số hợp lệ kể cả `numpy.float64`/`numpy.int64`; loại `None`/NaN/`±inf` dạng Python lẫn
`numpy.float64`/`bool`/`numpy.bool_`/chuỗi số/chuỗi bất kỳ/object), ma trận FS-08 cho từng vị
trí input × mọi giá trị invalid, end-to-end đúng counterexample `-inf` của reviewer, ma trận
officiality B-G (từng nguồn/nhiều nguồn/tất cả false) khẳng định CẢ `verdict != "BUILD"` LẪN
`can_proceed_to_app=False` — kiểm cả payload trả về VÀ bản ghi `backtest_runs.jsonl` đã persist,
case toàn official giữ nguyên hành vi, và unresolved provenance vẫn fail-loud
(`ProvenanceUnresolvedError`) như cũ, cộng test khoá nguyên post-F-017 owner replay (complete
finite input, không rerun 1000 sim) chứng minh repair không chạm formula hợp lệ.

Targeted: 151 test PASS (`test_benchmarks.py`, `test_gates_verdict.py`,
`test_wp_b1_verdict_policy.py`, `test_wp_b1_slice_failure_signal_cap.py`,
`test_wp_b1_e2_fresh_fail_repair.py`, `test_wp_b1_e2_fresh_fail_repair_v2.py`,
`test_wp_a5_failure_signal_instrumentation.py`) + `test_e2e.py` 2/2 PASS riêng (430s). Full
suite: xem `docs/sessions/S023-*.md`/`EXIT` cuối log.

`CHECK-B1-01: FAIL → PASS`; `CHECK-B1-07: FAIL → PASS` (lần thứ hai). Verdict lịch sử T-06
(`DO_NOT_BUILD`, `Gate 1 FAIL`/`OOS hard condition FAIL`, `can_proceed_to_app=false`) KHÔNG đổi
— quyết định ở nhánh Gate 1/OOS FAIL, trước cả FS-08 lẫn officiality gate. Post-F-017 owner
replay (dataset official, complete finite input, `FS-08=false`) KHÔNG bị chạm, KHÔNG rerun 1000
simulation. **WP-B1 nay 9/10 REQUIRED PASS** (01,02,03,04,05,06,07,08,10). **`CHECK-B1-09` GIỮ
NGUYÊN `NOT_TESTED`/FAIL lịch sử** — KHÔNG tự chạy lại E2 trong phiên này, cần một phiên độc lập
MỚI (vòng 3). Production diff batch 2: 2 file (`failure_signals.py`, `pipeline.py`), +37/−13;
cộng dồn cả phiên (vs `fa6422c`): 4 file, +108/−33 — trong ngân sách canonical, không
`CHANGE_BUDGET_EXCEEDED`, 0 repair cycle tiêu (WP-B1 chưa từng DONE). Không rerun T-06. Không mở
WP-B2/WP-B3/GATE-B/T-07. Không merge `main`. Không đổi threshold/strategy. WP-B1 **VẪN
IN_PROGRESS**, không đề xuất DONE. Chi tiết:
`docs/reviews/E2-WP-B1-CHECK-B1-09-fresh-after-repair-fail.md`,
`docs/tasks/WP-B1-*.md` (CHECK-B1-01 Addendum 3, CHECK-B1-07 Addendum 5),
`docs/sessions/S023-*.md`.

Trước đó, 2026-09-04 — **Fresh Independent E2 (`E2-WP-B1-002-FRESH-2026-09-04`, `docs/reviews/E2-WP-B1-
CHECK-B1-09-fresh-fail.md`) FAIL → repair batch E2-B1-F01/F02 → `CHECK-B1-01`/`CHECK-B1-07` phục
hồi `PASS`.** Reviewer độc lập (không phải phiên implementer) tái lập được HAI đường production
counterexample thật, cả hai đã được xác nhận độc lập lại lần nữa trong phiên này TRƯỚC khi sửa:

**E2-B1-F01** — `src/eth_dca_os/failure_signals.py:91-96` (trước sửa): FS-08 chỉ đòi MỘT trong
hai Control P95 hiện diện, coi control còn thiếu là "V2 tự động beat". Repro: `v2_eth=10.0`,
Control F P95=`None`, Control G P95=`9.5`, 11 signal khác sạch → `run_verdict` ra
`verdict=BUILD`, `can_proceed_to_app=true`. **Sửa**: FS-08 nay đòi ĐỦ CẢ BA input (`v2_eth` +
hai P95) hợp lệ (không `None`, không NaN/non-numeric qua helper mới `_numeric_and_finite()`) —
thiếu/invalid bất kỳ input nào → `None` (UNKNOWN). Không đổi chiều so sánh, không đổi ngưỡng.

**E2-B1-F02** — `pipeline.run_verdict` (trước sửa): `official` chỉ AND Gate 2/Gate 3 (bỏ sót
Gate 1 + Controls), và dù đủ bốn cũng CHỈ tạo dòng `warning` text — không chặn
`can_proceed_to_app`. Repro: Gate1/Gate2/Gate3/Controls đều `official=False`, gates/FS sạch →
`verdict=BUILD`, `can_proceed_to_app=true`, chỉ có warning. **Sửa**: `official` nay AND đủ CẢ
BỐN nguồn (tái dùng nguyên cờ có sẵn ở từng thành phần, không phát minh provenance mới); khi
không official mà `can_proceed_to_app` đang `True` → ép về `False` kèm lý do trong `reasons`.
`verdict.py::decide_verdict` KHÔNG bị sửa (giữ thuần chính sách gate/FS, officiality chặn đúng
MỘT chỗ ở `run_verdict`, nơi đã có sẵn đủ bốn cờ).

Test mới: `tests/test_wp_b1_e2_fresh_fail_repair.py` (21 test — ma trận đầy đủ F/G present/
missing/invalid cho FS-08, CASE A-E cho officiality gồm thiếu từng thành phần riêng lẻ và
provenance-unresolved qua cơ chế `ProvenanceUnresolvedError` có sẵn từ WP-A1, retained adversarial
coverage tie/exact-boundary/one-ULP). Sửa 1 test cũ (`test_gates_verdict.py::
test_fs08_random_control`) vốn vô tình mã hoá đúng hành vi lỗi. Targeted: 104/104 PASS. Full
suite: xem kết quả cuối phiên. CAP-VERDICT budget: trong ngân sách canonical, diff production
cộng dồn phiên (vs `fa6422c`) = 4 file, +84/−33 — không `CHANGE_BUDGET_EXCEEDED`.
`CHECK-B1-01: FAIL → PASS`, `CHECK-B1-07: FAIL → PASS`. **`CHECK-B1-09` GIỮ NGUYÊN `NOT_TESTED`/
FAIL lịch sử** — KHÔNG tự chạy lại E2, cần một phiên độc lập MỚI. H-26: giữ nguyên
`CONFIRMED HARDENING` (xác nhận lại bởi chính reviewer E2). Verdict lịch sử T-06 (`DO_NOT_BUILD`,
`can_proceed_to_app=false`) hoàn toàn không đổi — đã dừng ở Gate 1/OOS FAIL trước khi FS-08/
officiality-gate mới được xét tới, và T-06 vốn official=true. **WP-B1 nay lại 9/10 REQUIRED
PASS** (01,02,03,04,05,06,07,08,10); chỉ còn CHECK-B1-09. Không rerun T-06/Gate1/Gate2/Gate3.
Không đổi threshold/strategy. Không mở WP-B2/V2.2. Không merge `main`. WP-B1 **VẪN IN_PROGRESS**.

Trước đó, 2026-09-04 — **POST-F-017 WP-B1 EVIDENCE REPLAY (Owner-supplied) canonical hoá: `CHECK-B1-03`/
`CHECK-B1-07` phục hồi `BLOCKED → PASS`.** Chủ dự án tự chạy đúng script replay tối thiểu (đã viết
sẵn tại phiên trước, không sửa) trên máy Mac giữ dataset official T-06, cung cấp lại output. Xác
minh cơ học 8/8 điều kiện — **KHỚP TOÀN BỘ, không cần STOP**: `source_head=702b940` (hậu duệ trực
tiếp của commit F-017, 0 production diff giữa hai commit); `dataset_hash` khớp nguyên văn official
(`3150860cb...`); `master_seed=42`, `n_sims=1000` (official, không phải dev-limit); `v2_eth`
KHỚP BIT-FOR-BIT `frozen_v2_eth` (`14.910758150139896`, đọc từ `random_control_21b7d88e9691_
metrics.json` — validity check chống lệch dataset/strategy); `beats_f`/`beats_g` đúng công thức
(`v2_eth > control_f_p95`/`control_g_p95`, cả hai `True`); `FS-08 = not(True and True) = False`
đúng cơ học. Kết quả dán nhãn tường minh **"POST-F-017 WP-B1 EVIDENCE REPLAY"** — KHÔNG phải một
official T-06 run mới, không mutate artifact official, không rerun T-06/Gate1/Gate2/Gate3.
`CHECK-B1-03: BLOCKED → PASS` (đủ chữ hoàn toàn — production repair F-017 + evidence FS-08
post-repair). `CHECK-B1-07: BLOCKED → PASS` (phạm vi hẹp đúng như đã cam kết ở lần đảo trước —
năm gạch đầu dòng khác không bị viết lại). **`CHECK-B1-09` GIỮ NGUYÊN `NOT_TESTED`/FAIL lịch sử**
— KHÔNG tự chạy lại E2 trong phiên này, cần một phiên độc lập mới. Verdict lịch sử T-06
(`DO_NOT_BUILD`, `Gate 1 FAIL`/`OOS hard condition FAIL`, `can_proceed_to_app=false`) **KHÔNG
đổi** — FS-08 chỉ được `verdict.py` xét ở nhánh cuối khi cả 4 gate PASS, T-06 đã dừng ở Gate
1/OOS trước đó. **WP-B1 nay 9/10 REQUIRED PASS** (01,02,03,04,05,06,07,08,10); chỉ còn CHECK-B1-09
(E2 độc lập mới) `NOT_TESTED`. Production diff = 0 (chỉ docs/state). Không rerun T-06. Không mở
WP-B2/WP-B3/GATE-B/T-07. Không merge `main`. WP-B1 **VẪN IN_PROGRESS**, không đề xuất DONE. Chi
tiết: `docs/tasks/WP-B1-*.md` (CHECK-B1-03/07 Addendum 3), `docs/sessions/S023-*.md`.

Trước đó, 2026-09-04 — **INDEPENDENT E2 (`CHECK-B1-09`) FAILED trên `WP-B1`: `CHECK-B1-03`/`CHECK-B1-07`
đảo `PASS → BLOCKED`.** Finding: `CHECK-B1-03` (frozen) đòi "Kết quả FS-08 (do Control F nuôi)
phải được tính lại sau khi sửa [F-017]" — check này đã bị đóng khung `PASS` ở phiên trước dù
chính evidence của nó tự nói FS-08 post-repair chưa tính được (thiếu dataset official). Finding
ĐƯỢC CHẤP NHẬN NGUYÊN VẸN, không tranh cãi/bypass (ghi chú minh bạch: không tìm thấy artifact
`docs/reviews/E2-WP-B1-*.md` nào trong repo tại thời điểm nhận finding — nội dung vẫn được xác
nhận ĐÚNG độc lập bằng đối chiếu trực tiếp với câu chữ frozen của CHECK-B1-03 và evidence agent tự
viết trước đó). `CHECK-B1-03: PASS → BLOCKED — EVIDENCE INCOMPLETE` (production repair F-017 tự
nó vẫn ĐÚNG, không bị nghi ngờ — chỉ THIẾU evidence FS-08 post-repair). `CHECK-B1-07: PASS →
BLOCKED — pending CHECK-B1-03` (phạm vi hẹp, năm/sáu gạch đầu dòng còn lại không đổi, có bằng
chứng riêng). Owner authorize một minimal deterministic replay: thiết kế đầy đủ (dùng
`run_engine()` + `random_timing_control`/`random_anchor_control` đã sửa, KHÔNG gọi
`evaluate_gate1/2/3`, KHÔNG rerun Gate1/2/3), smoke-test PASS trên dataset SYNTHETIC (chỉ để xác
nhận script không lỗi cú pháp/API — KHÔNG dùng làm evidence). **MISSING_INPUT**: môi trường agent
không có dataset official (`data/raw` gitignored, chưa từng tồn tại ở đây; không được fetch dữ
liệu mới thay thế). Exact replay command đã ghi đầy đủ tại `docs/tasks/WP-B1-*.md::CHECK-B1-03`,
chờ Owner chạy trên máy có dataset official (`data/` từ lần fetch trước, hoặc backup
`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03`) rồi dán lại output.
**WP-B1 nay 7/10 REQUIRED PASS** (01,02,04,05,06,08,10); 2/10 `BLOCKED` (03,07); 1/10
`NOT_TESTED`/FAIL (09, chờ chạy lại E2 sau khi 03/07 có evidence). Không rerun T-06. Không sửa
production code (F-017 fix giữ nguyên, không bị nghi ngờ). Không mở H-26/WP-B2/WP-B3/GATE-B/T-07.
`CHECK-B1-09` KHÔNG được tự ý đánh dấu PASS. WP-B1 **VẪN IN_PROGRESS**. Chi tiết đầy đủ:
`docs/tasks/WP-B1-*.md` (CHECK-B1-03/07), `docs/sessions/S023-*.md` (addendum tiếp theo).

Trước đó, 2026-09-03 — **OWNER DECISION `DEC-033` (`OD-B1-02`) — APPROVE AS-IS ba ngưỡng FS-02/FS-07/
FS-12; CHECK-B1-08 PASS bằng evidence Owner cung cấp từ frozen official T-06 backup.** Tiếp nối
phiên `WP-B1 IN_PROGRESS` (nhánh `claude/wp-b1-verdict-correctness-j9d390`). (1) Chủ dự án phê
chuẩn giữ nguyên `opportunity_cap_hit_share > 0.5` (FS-02), `avg_cash_ratio > 0.30 AND
gate1_primary_ae < 102.0` (FS-07), `regime_advantage_share > 0.80` (FS-12) — không đổi giá trị
nào, lý do: "semantics implementation ban đầu, chưa có evidence độc lập đủ mạnh để biện minh
threshold thay thế"; không tuyên bố tối ưu thực nghiệm, không tự động cho V2.2. Canonical hóa:
`docs/CONVENTIONS.md` #21(e), `PROJECT/PROJECT_DECISIONS.md` `DEC-033`. Production diff = 0.
**CHECK-B1-04: BLOCKED → PASS.** `F-015` ĐÓNG. (2) Owner tự thực hiện read-only verification
trên COPY của frozen official T-06 backup
(`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03`): `ethdca verdict --out-dir
results` xác nhận `verdict=DO_NOT_BUILD`, `can_proceed_to_app=false` từ `pipeline_state.json`
(trường `reasons` bị compact thành chuỗi `"[2 items]"` — xác nhận đây là hành vi THIẾT KẾ có sẵn
của `cli.py::_strip()`/`reporting.py::write_report()`, không phải lỗi mới); full reasons
(`["Gate 1 FAIL", "OOS hard condition FAIL"]`) cross-verified từ hai artifact KHÁC cùng gói
frozen official evidence đã canonical hoá SHA-256 (`baseline_808b61fa5ffe_metrics.json`,
`report.json`), corroborate bởi `backtest_runs.jsonl` (`code_commit=5228130...`, `official=true`,
khớp `DEC-031`/`T06_OFFICIAL_EVIDENCE_RECORD.md`). Không rerun T-06, không sửa artifact nào.
**CHECK-B1-08: BLOCKED → PASS.** **WP-B1 nay 9/10 REQUIRED PASS** — chỉ còn CHECK-B1-09 (E2 độc
lập) `NOT_TESTED`. `H-26` giữ nguyên HARDENING, không Scope Expansion. Không chạy WP-B2/WP-B3,
không mở GATE-B, không chạy T-07, không rerun T-06, không chạy CHECK-B1-09. WP-B1 **VẪN
IN_PROGRESS**, chưa DONE. Chi tiết đầy đủ: file task `WP-B1-*.md` (CHECK-B1-04/08), báo cáo
phiên tiếp nối `docs/sessions/S023-wp-b1-verdict-correctness-in-progress.md`.

Trước đó, 2026-09-03 — **`WP-B1` mở `IN_PROGRESS`, phiên WP-B1-verdict-correctness (nhánh
`claude/wp-b1-verdict-correctness-j9d390`).** Ready Gate xác nhận lại đủ 15/15. Kết quả: **7/10
REQUIRED check PASS** — CHECK-B1-01 (đã PASS từ lát cắt `DEC-026`, addendum chốt B1.1), CHECK-B1-02
(DEC-009: **KẾT LUẬN KHÔNG** — Control F/G remediation không giao đường mã với Gate 1/OOS/Gate
2/Gate 3, bằng chứng thứ tự lệnh trong `pipeline.py::run_gate1`, kiểm lại được độc lập; Gate 1
KHÔNG cần chạy lại), CHECK-B1-03 (F-017 ĐÓNG: `random_timing_control`/`random_anchor_control`
sửa để giữ đúng kích thước tranche/profile theo tháng, dùng lại `full.purchases` có sẵn — KHÔNG
sửa `engine.py`), CHECK-B1-05 (ánh xạ gate-fail→verdict ghi tại `docs/CONVENTIONS.md` #21(a), đóng
F-026), CHECK-B1-06 (`shift_days=10` ghi tại #21(c); phạm vi window FS-03/FS-07 xác nhận đã đủ từ
WP-A5 #20(d)), CHECK-B1-07 (stopping rule integrity — 12 test mới
`tests/test_wp_b1_verdict_policy.py`: precedence nhiều gate-fail đồng thời, `can_proceed_to_app`
đúng nghĩa, numpy.bool_/bool tại tầng `gates.py` [họ H-26] không làm sai verdict, determinism).
**2/10 `BLOCKED` chờ Owner input**: CHECK-B1-04 (ba ngưỡng FS-02/FS-07/FS-12 chưa được chủ dự án
phê chuẩn — agent KHÔNG tự phê chuẩn thay), CHECK-B1-08 (thiếu `pipeline_state.json` official —
artifact được chủ dự án bảo toàn ngoài repository, agent không truy cập được, KHÔNG được rerun
official run). **1/10 `NOT_TESTED`**: CHECK-B1-09 (E2 độc lập — không thể tự cấp cho chính phiên
vừa cài đặt). Production diff: `src/eth_dca_os/{benchmarks.py,pipeline.py,cli.py}` (+~70/−~40,
không chạm `gates.py`/`engine.py`/`verdict.py`/ngưỡng nào). Test mới/sửa: 26 test targeted PASS
(`test_benchmarks.py` +2, `test_wp_b1_verdict_policy.py` +12 mới, `test_e2e.py`/
`test_gates_verdict.py` không đổi hành vi). Full suite: **391/391 PASS, 0 FAIL, `EXIT=0`**
(→ CHECK-B1-10 PASS; báo cáo đầy đủ tại `docs/sessions/S023-wp-b1-verdict-correctness-in-progress.md`). **WP-B1 CHƯA DONE** — `T-06 DONE`/`V2.1.5 FAILED`/verdict
`DO_NOT_BUILD`/`can_proceed_to_app=false`/`BLK-001 RESOLVED` GIỮ NGUYÊN không đổi. `WP-B2`
(READY), `WP-B3` (BLOCKED bởi `WP-C2`), `GATE-B` (chưa mở), `T-07` (NOT READY) — không đổi. Không
merge `main`. Không mở task mới. `CAP-VERDICT` budget: xem `REVIEW_BUDGET_LEDGER.md` §2.

Trước đó, 2026-09-03 — **OWNER DECISION `DEC-024` (`OD-WEBAPP-07`) — phê chuẩn hoàn thành `T-09B`:
`IMPLEMENTED → DONE`.** Chủ dự án xác nhận tường minh chấp nhận Completion Gate 16/16 REQUIRED
PASS cùng evidence hai tầng (E1 Firebase Emulator Suite toàn bộ + E1 production thật cho
CHECK-01/02/03/04/14 trên `https://tinphatcontent.web.app`, Owner tự báo cáo — không phải E2 độc
lập, chủ dự án chấp nhận rõ mức này). `CAP-WEBAPP` budget KHÔNG đổi: 2/0/2 — toàn chuỗi phiên từ
S014 là INITIAL IMPLEMENTATION, không tiêu repair cycle. `RSK-001`: ghi nhận phần V1 durable
persistence đã kiểm chứng trên production, KHÔNG tuyên bố đóng hẳn; `H-23` tiếp tục HARDENING/
OUT OF SCOPE V1 theo `DEC-021`, không đổi. `ELIGIBLE_FOR_INTEGRATION = NO` giữ nguyên theo
`DEC-022` — không merge `main`. Không mở task mới.

Trước đó, 2026-09-03 — **PRODUCTION VERIFICATION PASS — CHECK-T09B-01/02/03/04/14 trên hạ tầng thật.**
Chủ dự án tự tay lặp lại toàn bộ chuỗi trên `https://tinphatcontent.web.app` (project Firebase
thật, rules đã merge với Owner UID thật): nhập giá đóng cửa synthetic → nạp vốn tháng → P2P →
mua ETH (rev 1→4, đúng dự đoán) → đóng hẳn trình duyệt/mở lại (CHECK-02+04 PASS) → xoá
localStorage+sessionStorage/mở lại (CHECK-03 PASS). Một lần thử ban đầu bị chặn ở bước P2P
("Không đủ VND trong kho") — xác nhận đây là accounting guard ĐÚNG (`addP2P` cần `treasury.vnd`
đã nạp qua `addContribution` trước, `webapp/app_logic.js:209`), không phải defect; sửa QUY
TRÌNH test (thêm bước nạp vốn tháng), không sửa code. **CHECK-T09B-14 PASS** — chuỗi hằng ngày
chạy trọn vẹn qua trình duyệt thật, không terminal/AI agent. Evidence đầy đủ:
`docs/reviews/T-09B-production-verification.md` (E1, Owner báo cáo trực tiếp — môi trường agent
bị chặn mạng tới `*.web.app`, không tự tái xác nhận độc lập được). `docs/tasks/T-09B-*.md`: 5
CHECK cập nhật thêm evidence production; Status ghi nhận production reachability PASS,
**ELIGIBLE_FOR_COMPLETION** làm khuyến nghị — vẫn `IMPLEMENTED`, chuyển `DONE` là hành vi của
chủ dự án (`STATE_AUTHORITY.md`, tiền lệ `DEC-018`). `RSK-001`: giảm đáng kể trên thực tế cho
kịch bản trong scope V1 (xoá site data, ghi/đọc Firestore) — kịch bản "đổi máy" vẫn mở theo
`H-23`, không đổi. Không phát hiện defect production. Không mở task mới. Không merge main.
`CAP-WEBAPP` budget không đổi: 2/0/2.

Trước đó, 2026-09-02 — **Owner UID production thật xác minh (checkpoint tiếp nối `DEC-023`)**: Owner
deploy Hosting thành công (`https://tinphatcontent.web.app`), mở bằng trình duyệt hằng ngày,
Anonymous Auth sinh UID `XWUo6IvUqhULI1v1EBrfndEDrE13`. Xác minh trực tiếp UID này qua emulator
(mint token bằng Auth Emulator custom-token, không sửa `firestore.rules` — file đó là test
fixture dùng chung cho 285+ assertion, thay placeholder cố định sẽ làm gãy toàn bộ owner-flow
test): 16/16 PASS — unauthenticated/wrong-UID deny, UID thật đọc/ghi state+seed allow, document
lạ + xoá đều deny, Content không đổi hành vi. Git diff checkpoint này = 0 file. Đưa Owner lệnh
deploy chính xác (thay UID cục bộ, không commit, rồi deploy `firestore.rules`). Evidence:
`docs/reviews/T-09B-shared-rules-merge.md` § Addendum. CHƯA deploy rules — chờ Owner tự chạy
lệnh. `CAP-WEBAPP` budget không đổi (2/0/2).

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-023` (`OD-WEBAPP-06`) — Firebase project thật DÙNG CHUNG
với ứng dụng "Content"; merge `firestore.rules` an toàn; Hosting RESOLVED.** Project thật
(`tinphatcontent`, display "CoinDCA") KHÔNG dành riêng cho ETH DCA OS — Firestore đang có dữ
liệu Content (`users`, `contents`, `schedules`, `groups`, `config`, `fb_queue`, `audit_logs`).
Kiến trúc T-09B (`DEC-020`) KHÔNG đổi — chỉ thêm bước merge rules an toàn. `firestore.rules`
nay là rules Content THẬT (giữ nguyên văn) + khối CoinDCA riêng biệt (`isCoinDcaOwner()`, đổi
tên khỏi `isOwner()` để không trùng hàm sẵn có của Content). Kiểm bằng Firestore Rules
Emulator (`webapp/test_shared_rules_merge.js`, `npm run test:rules-merge`): battery 53 probe
phủ toàn bộ 8 collection Content, BEFORE (rules Content nguyên văn) == AFTER (đã merge) —
**0 lệch** → `CONTENT_BEHAVIOR_PRESERVED = YES`. Ma trận CoinDCA 12 ca (§8) PASS 12/12. Evidence
đầy đủ: `docs/reviews/T-09B-shared-rules-merge.md`. Hosting: Owner tự kiểm Console — chưa
setup, không có site Content cần bảo toàn → dùng site mặc định, không cần multi-site. **CHƯA
DEPLOY** — owner UID trong rules còn placeholder, chờ Owner lấy UID thật từ trình duyệt hằng
ngày rồi tự deploy (agent không có Firebase CLI authority). `CAP-WEBAPP` budget không đổi:
2/0/2. Không tiêu repair cycle. Chi tiết: `PROJECT/PROJECT_DECISIONS.md` `DEC-023`.

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-022` (`OD-WEBAPP-05`) — Integration size disposition cho
`T-09B`: ACCEPT THE DIVERGENCE.** Phiên tiếp nối S014 trên cùng branch
`claude/t09b-firebase-implementation-nz50is` báo `INTEGRATION_DECISION_REQUIRED: loc>5000`
(divergence LOC = 12.272). Chủ dự án xác nhận CHẤP NHẬN kích thước hiện tại — KHÔNG merge `main`,
KHÔNG cut scope, KHÔNG rewrite dependency management chỉ để hạ số đo. Đo lại cho thấy phần lớn
divergence (~11.550/12.272 dòng) là generated dependency metadata (`webapp/package-lock.json`
+9.482 dòng ghim `firebase`/`firebase-tools`) + test/harness (~1.063 dòng, không phải production
path); production implementation thật theo khai báo chỉ +560/−162 (khớp `REVIEW_BUDGET_LEDGER.md`
§2.2.4). Sanity check dependency (`DEC-022` §11): 723 package mới, toàn bộ là transitive dependency
của `firebase`/`firebase-tools`, không có gói lạ — thêm `HARDENING_BACKLOG.md` **H-33** (footprint
`firebase-tools` rộng hơn phạm vi dùng thật: chỉ dùng emulator Auth+Firestore và deploy
hosting+firestore rules, nhưng CLI kéo theo Cloud SQL/Pub-Sub/App Hosting/Data Connect — tầng
tooling, không phải sản phẩm, không sửa). Chi tiết: `PROJECT/PROJECT_DECISIONS.md` `DEC-022`.

Trước đó, 2026-09-02 — **T-09B IMPLEMENTED (S014)**: persistence bền trên Firebase đã được **cài đặt và kiểm
chứng** trên branch `claude/t09b-firebase-implementation-nz50is` (BASE `4502ea6`, production commit
`a19d3ad`, test commit `0d4917a`). Kiến trúc đúng baseline FROZEN `DEC-020`/`DEC-021`: Browser →
Firebase Hosting → Firebase Anonymous Auth (một owner UID trong `firestore.rules`) → Cloud
Firestore `ethdca/state` + `ethdca/seed`; `localStorage` = mirror/cache. Trang không còn nhúng
state, không còn quine/publish của host cũ. Save flow: mỗi thao tác → mirror → ghi Firestore qua
transaction có điều kiện `rev`, UI chỉ báo "Đã lưu bền · rev N" khi máy chủ xác nhận; timeout →
"CHƯA XÁC NHẬN"; từ chối/mất mạng → "CHƯA LƯU", giữ bản local, Lưu lại/tự ghi lại khi có mạng.
Load flow: init → Anonymous Auth → đọc từ SERVER → `validateState` → ONLINE, hoặc một trong
UNCONFIGURED / AUTH_FAILED / UNRECOGNIZED ("không nhận diện được thiết bị/trình duyệt này", H-23)
/ OFFLINE (mirror chỉ để xem, đánh dấu chưa xác nhận) / CORRUPT (không nạp, không ghi đè, tải bản
thô để cứu) — mọi phase lỗi **khoá ghi sổ**. Mirror mới hơn nguồn bền không âm thầm thắng (cất
riêng + chọn tường minh). **16/16 REQUIRED check PASS (E1)** trên Firebase Emulator Suite (Auth +
Firestore, đúng `firestore.rules` repo, SDK thật, trang build thật qua HTTP; bằng chứng phía Firebase
đọc độc lập qua REST): `test_t09b_persistence.js` 285 assertion / 0 FAIL; ba test kế toán T-09A chạy
trên state đã round-trip Firestore (68/68; V-01/V-02/V-03 BÁC BỎ như trước); `npm --prefix webapp
test` 6/6. `engine.js`, `src/eth_dca_os/**`, `pyproject.*` = 0 dòng. Batch review bắt buộc → **PASS,
0 CONFIRMED BLOCKING còn lại** (1 finding hai-tab-stale-overwrite phát hiện trong phiên, sửa cùng
lượt), 4 HARDENING mới `H-29..H-32`. `CAP-WEBAPP` budget **2/0/2 không đổi** (implementation ban
đầu). Task ID mới = 0. **Giới hạn bằng chứng, ghi trung thực:** project Firebase THẬT chưa tồn tại
→ production reachability trên hạ tầng thật = NOT_TESTED; CODE IMPLEMENTATION COMPLETE, **REAL
FIREBASE SETUP REQUIRED** (chủ dự án: `webapp/README.md` § Thiết lập Firebase). Chuyển `DONE` là hành
vi của chủ dự án. `RSK-001`: giảm thiểu đã cài đặt, **chưa giảm trên thực tế** cho tới khi app
Firebase thật được dùng thay bản artifact. Handoff: `docs/sessions/S014-t09b-firebase-implementation.md`.

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-021` (`OD-WEBAPP-04`) — Personal Tool Simplification
Principle; `OD-C` = R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)**, phiên tiếp nối trên nhánh thẩm
quyền `claude/t09b-firebase-decision-nnoony`. Chủ dự án phát biểu một nguyên tắc sản phẩm bao
trùm: ETH DCA OS là công cụ cá nhân, ưu tiên Financial correctness > Algorithm correctness >
Decision usefulness > Accounting correctness > không mất dữ liệu quan trọng > Daily usability
> Implementation simplicity > Low operational burden > Cost > Security hardening > Scalability
(11 mục, khai triển từ `DEC-011`/`DEC-019`, ghi tại `PROJECT/PROJECT_DECISIONS.md` `DEC-021` —
KHÔNG tạo artifact riêng, cùng vị trí đã giữ `DEC-011`). Kèm Critical Product Question (A–F, đối
chiếu `DEC-011`), Security Philosophy (security không phải trọng tâm V1) và Minimum Security
Floor (chống public write vô tình, chống commit secret, chống hiểu nhầm dữ liệu sai là hợp lệ,
chống UI báo "đã lưu" khi chưa lưu, chống security cơ chế quá yếu tới mức làm sai/mất
accounting state).

`OD-C` (khe recovery semantics mở tại `DEC-020`) được đóng bằng **R2 — SIMPLIFIED
PERSONAL-TOOL RECOVERY**: KHÔNG xây recovery credential (email/password) chỉ để đóng edge case
đổi máy/browser; cross-device/cross-browser/lost-identity recovery = **OUT OF SCOPE V1**,
ghi `PROJECT/HARDENING_BACKLOG.md` **H-23**. Đây là Owner Scope Decision dựa trên Product
Intent mới — khe kỹ thuật ghi tại `DEC-020` (Anonymous UID mới sau đổi máy bị Firestore rules
từ chối) vẫn ĐÚNG và KHÔNG bị phủ nhận, chỉ có phạm vi CHẤP NHẬN của V1 thay đổi.
`CHECK-T09B-04` được tái phạm vi bằng audit trail bắt buộc (OLD REQUIREMENT → OWNER PRODUCT
INTENT CHANGE → NEW V1 REQUIREMENT, ghi ngay tại chính check trong Task Spec) — KHÔNG được mô
tả là bug fix hay evidence PASS. `CHECK-T09B-03` và toàn bộ 15 REQUIRED check khác — bao gồm
mọi check thuộc financial/algorithm/accounting/persistence correctness — **KHÔNG đổi, KHÔNG bị
làm yếu**.

Đánh giá lại toàn bộ Ready Gate (không auto-PASS chỉ vì OD-C được quyết): **15/15 ĐẠT** — không
còn Owner Decision hay architecture ambiguity nào chặn. **Completion Gate 16/16 REQUIRED
FROZEN.** **`T-09B: PLANNED → READY`.** `CAP-WEBAPP` budget KHÔNG đổi: allowed 2 / used 0 /
remaining 2 — chuyển `READY` không phải implementation, không tiêu repair cycle. **Production
file bị sửa = 0.**

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-020` (`OD-WEBAPP-03`) — giải quyết `OD-A`/`OD-B`/`OD-B2` cho
T-09B; phát hiện khe mới `OD-C`**, phiên tiếp nối trên nhánh thẩm quyền
`claude/t09b-firebase-decision-nnoony`. Chủ dự án APPROVED: `OD-A` = **Firebase Hosting**
(runtime host); `OD-B` = **Cloud Firestore** (document `ethdca/state` + `ethdca/seed`);
`OD-B2` = **Firebase Anonymous Auth**, rules khoá cứng một owner UID. Kiến trúc baseline:
Browser → Firebase Hosting → Firebase Authentication → Cloud Firestore → durable state;
`localStorage`/`sessionStorage` vẫn là mirror/cache. Đánh giá lại Ready Gate phát hiện khe MỚI
**`OD-C`**: Anonymous Auth session sống trong `IndexedDB` của một browser profile — ba trong
bốn kịch bản mất dữ liệu mà `RSK-001` nêu tên (cửa sổ riêng tư, đổi máy, đổi trình duyệt) tạo
`IndexedDB` trống → Anonymous UID mới → Firestore rules (khoá một UID cố định) từ chối. Đây là
khe giữa *durable STATE persistence* (đã giải quyết bằng Hosting+Firestore) và *khả năng
AUTHENTICATE lại làm owner sau khi mất local browser identity* (CHƯA). `CHECK-T09B-03` (xoá
localStorage/sessionStorage) KHÔNG bị ảnh hưởng; `CHECK-T09B-04` nhánh "profile/cửa sổ khác"
KHÔNG PASS được trung thực với Anonymous Auth đơn thuần. KHÔNG làm yếu check này. Hai phương
án chờ chủ dự án: **R1** (khuyến nghị) link recovery credential (email/password) vào UID nặc
danh, chỉ dùng khi đổi máy/browser, không đổi trải nghiệm hằng ngày; **R2** chấp nhận giới
hạn, thu hẹp phạm vi "recover" của check xuống same-browser-profile, để hở kịch bản "đổi máy".
**T-09B GIỮ `PLANNED`** — 14/15 dòng Ready Gate ✅ (đếm cả dòng "+"), chỉ dòng "+" (architecture
ambiguity) còn ❌ vì `OD-C`. Completion Gate 16/16 REQUIRED vẫn FINALIZED, KHÔNG sửa yếu, CHƯA
frozen (freeze chỉ xảy ra khi Ready Gate đủ). `CAP-WEBAPP` budget KHÔNG đổi: allowed 2 / used 0
/ remaining 2. Không mở repair cycle. Không chuyển `IN_PROGRESS`. **Production file bị sửa = 0.**

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-019` (`OD-WEBAPP-02`) — Firebase là ràng buộc kiến trúc cố định cho
T-09B**, phiên Owner Authority / Ready-Gate Preparation. Chủ dự án bổ sung Product Intent (công cụ cá nhân,
single-user, dùng khi cần, tần suất thấp; ưu tiên correctness → usability → low operational burden →
implementation simplicity → cost → technical elegance → scalability) và chốt **Firebase** làm nền tảng
persistence — KHÔNG so sánh lại với Supabase/SQLite/PostgreSQL/D1/JSON Server. Lập Task Spec
`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` cho ID **đã tồn tại** (Task ID mới = **0**). State inventory
đọc từ schema thật (`app_logic.js::emptyState()`, `engine.js::buildLadder()`, `live_seed.json`), phân loại
MUST_PERSIST (hai tầng) / CAN_RECOMPUTE / EPHEMERAL. Completion Gate **FINALIZED** 16/16 REQUIRED, tất cả
`NOT_TESTED`. **T-09B GIỮ `PLANNED`** — Ready Gate KHÔNG đạt vì còn `OWNER_DECISION_REQUIRED`: `OD-A`
(runtime host — CSP của host hiện tại chặn mọi host ngoài trừ Google Fonts, nên Firebase không với tới được
và gate A/B/C/D không thể PASS; khuyến nghị Firebase Hosting), `OD-B` (Firestore vs Realtime Database —
khuyến nghị Cloud Firestore), `OD-B2` (danh tính tối thiểu cho security rules). `CAP-WEBAPP` budget KHÔNG
đổi: allowed 2 / used 0 / remaining 2. Không mở repair cycle. **Production file bị sửa = 0.**

Trước đó, 2026-09-02 — **OWNER DECISION `DEC-018` (`OD-WEBAPP-01`) — T-09A chuyển `DONE`**: chủ dự án
phê chuẩn hoàn thành T-09A và ratify hạn mức repair `CAP-WEBAPP`. **T-09A: IMPLEMENTED →
DONE.** Completion Gate GIỮ NGUYÊN 12/12 REQUIRED PASS (E1) — không sửa câu chữ/ngữ nghĩa.
`CAP-WEBAPP` budget: allowed 2 / used 0 / remaining 2 — nay là **Owner-ratified** (`DEC-018`),
không còn ở trạng thái default V4.3 chưa khai; xác nhận lượt implementation ban đầu của T-09A
KHÔNG tiêu repair cycle nào. Không mở repair cycle mới. Kết quả T-09A giữ nguyên: V-01 =
FIXED/không còn tái hiện, V-02 = FIXED/không còn tái hiện, V-03 = REJECTED, H-18 = DEFERRED,
H-19..H-22 = HARDENING với RE_TRIGGER_CONDITION, `F-T09A-03` = OUT_OF_SCOPE → WP-C4. Cảnh báo
historical state (dữ liệu lưu TRƯỚC bản vá V-01/V-02 có thể đã sai sẵn) GIỮ NGUYÊN, CHƯA đóng.
Task ID mới = 0.

Trước đó, 2026-09-02 — **T-09A IMPLEMENTED**: hai lỗi kế toán app web mà `WP-C1` đã XÁC NHẬN nay đã
được vá và kiểm chứng trên đường sản phẩm thật. **V-01** (release trả nhầm pool tháng) và
**V-02** (unlock không giới hạn reserve) đều **không còn tái hiện** — reproduction của WP-C1
chạy lại cho BÁC BỎ ở cả hai. 12/12 REQUIRED check PASS (E1). Batch review bắt buộc (Effective
Risk HIGH) → **PASS, 0 CONFIRMED BLOCKING**; sinh 4 HARDENING mới (H-19, H-20, H-21, H-22) và 1
`OUT_OF_SCOPE` định tuyến sang `WP-C4`. `CAP-WEBAPP` budget: allowed 2 (default V4.3) / used 0
/ remaining 2 — lượt vừa rồi là implementation ban đầu, không phải repair cycle. Task ID mới
= 0. `webapp/engine.js` và `src/eth_dca_os/**` 0 dòng đổi. **Chuyển T-09A sang `DONE` là hành
vi của chủ dự án** (`STATE_AUTHORITY.md`).

Trước đó, 2026-09-01 — S010 hoàn tất: **CAP-DATA REPAIR CYCLE #1** thi hành `DEC-016`. `F-S009-01`
ĐÃ ĐÓNG bằng `CHECK-A4-11` (REQUIRED, E1) — indicator daily nay neo cửa sổ vào NGÀY LỊCH,
ngày thiếu ra NaN → DEGRADED/INVALID thay vì một số hữu hạn sai. **WP-A4 trở lại DONE**
với 10/10 REQUIRED check PASS. Batch review bắt buộc (Effective Risk HIGH) → PASS, 0
BLOCKING; 2 HARDENING mới (H-16, H-17) và 1 `OUT_OF_SCOPE` định tuyến sang `WP-C4`.
`CAP-DATA` budget: allowed 2 / **used 1** / remaining 1. Task ID mới được tạo = 0.

Trước đó, 2026-09-01 — S009: **WP-A4 DONE** lần đầu (9/9 REQUIRED check PASS gồm
`CHECK-A4-10` do chủ dự án bổ sung qua `DEC-014`/`OD-A4-01`; đóng F-023, F-025, F-032 và
**F-E2A1R3-05**), kèm phát hiện `F-S009-01` mà S010 vừa đóng.

Overall Status:
IN_PROGRESS

Current Phase:
Phase 2 — Lớp A (bắt buộc sửa trước official run) **HOÀN TẤT**. Cả bảy gói lớp A đã DONE:
WP-A1, WP-A2, WP-A3, WP-A4, WP-A5, WP-A6, WP-A7 (+ WP-D1 lớp D). **`GATE-A = CLOSED`**
(`DEC-028`, 2026-09-03). Kế tiếp trên đường găng: gỡ `BLK-001` — điều kiện DUY NHẤT còn lại
của `T-06` (`T-06 = GATE-A ∧ BLK-001`, theo `RCP-002` điểm 9, đã áp dụng; `T-05` KHÔNG phải
điều kiện của `T-06` — xác nhận tại `DEC-029`, đóng inconsistency trước đó). `T-05`/`DEC-005`
vẫn `PENDING`, nhưng chỉ chặn `T-08` và `WP-C2`, không nằm trên đường tới `T-06`.

Current Task:
`WP-B1` — `IN_PROGRESS` (phiên hiện tại, nhánh `claude/wp-b1-verdict-correctness-j9d390`).
HAI vòng fresh Independent E2 liên tiếp, mỗi vòng tìm ra lỗ hở thật trong CÙNG cơ chế
`E2-B1-F01`(FS-08 fail-open)/`E2-B1-F02`(officiality không chặn verdict) — vòng 1 sửa
None/NaN + progression flag, vòng 2 (review đúng bản sửa vòng 1) sửa thêm `±inf`/`bool` +
nhãn verdict. Cả hai batch trong `failure_signals.py`/`pipeline.py`, 70 regression test mới
tổng cộng (`tests/test_wp_b1_e2_fresh_fail_repair.py` +
`tests/test_wp_b1_e2_fresh_fail_repair_v2.py`) → `CHECK-B1-01`/`CHECK-B1-07` phục hồi
`FAIL → PASS` cả hai lần. **9/10 REQUIRED PASS** (01,02,03,04,05,06,07,08,10); chỉ còn
`CHECK-B1-09` (cần một phiên Independent E2 MỚI, vòng 3 — không tự chạy trong phiên này). DỪNG
đúng phạm vi WP-B1 theo chỉ thị phiên — không mở WP-B2/WP-B3, không mở GATE-B, không chạy T-07,
không merge `main`, không tự chạy CHECK-B1-09, không rerun T-06, không đổi threshold/strategy.

Current Task Mode:
MAJOR

Next Recommended Task:
**WP-A6** nay đã đủ dependency (WP-A3 ✅ + WP-A4 ✅ + WP-A7 ✅) và là mắt xích tiếp theo
trên đường găng; nó cũng phải trả lời H-15 (zone TRIGGERED trong chu kỳ INVALID).
Các gói READY khác: **WP-A5** (đủ dependency từ S004; cùng sửa `pipeline.py` với WP-A2 đã
push xong), **WP-A1** (chờ quyết định của chủ dự án về budget/legacy gate — KHÔNG mở được
bằng agent), **WP-C1** (song song, độc lập — xem "Song song" bên dưới), **WP-D2**.

Hai quyết định từng chặn ở đây nay đã ĐÓNG cả hai (2026-09-01, phiên Integration):
`DEC-013` (integration → phương án A, trunk = `main`, integration SHA `febc2ec`) và
`DEC-016`/`DEC-017` (`F-S009-01` → REOPEN WP-A4 một repair cycle; budget CAP-DATA
allowed 2 / used 0 / remaining 2). `DEC-016` **đã được THI HÀNH tại S010**: chu kỳ 1 tiêu
xong, `used` = 1, `remaining` = 1 (`REVIEW_BUDGET_LEDGER.md` §2.1). Không mở chu kỳ #2.
Branch authority từ đây: mọi phiên mới branch từ `origin/main` sau khi fetch.

## Overall Roadmap

Canonical format: see `governance/core/ROADMAP_SYNC_STANDARD.md`.
After every roadmap change run `python governance/scripts/governance/sync_easy_roadmap.py`.

Toàn bộ Tier/Effort dưới đây được tính bằng `governance/scripts/governance/routing_engine.py`,
không chọn bằng cảm tính, **trừ một ngoại lệ có ghi nhận rõ ràng**: WP-A2 dùng Tier ghi đè thủ
công (C thay vì B do router trả) theo phê duyệt của chủ dự án — xem DEC-008 và
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`. Bằng chứng routing của từng task nằm trong
file task tương ứng dưới `docs/tasks/` (với task đã có file) hoặc ở mục "Routing sơ bộ" cuối
tài liệu này.

Roadmap này áp dụng **RCP-001** (`PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`), được chủ dự án phê
duyệt ngày 2026-08-23 kèm bốn điều kiện — xem mục "Roadmap Change Applied" bên dưới.

**Cập nhật S002:** 15 work package không còn là roadmap sơ bộ. Mỗi gói đã có file định nghĩa task
đầy đủ dưới `docs/tasks/`, với Ready Gate, Completion Gate (REQUIRED checks + Evidence Level),
Exit Criteria và Escalation Triggers **đã đóng băng** ngày 2026-08-23. Theo
`TASK_COMPLETION_GATE_STANDARD.md` mục "After Freeze", agent **không được xoá hoặc làm yếu REQUIRED
check** để task đi qua; mọi thay đổi phải dùng khối `COMPLETION GATE CHANGE PROPOSAL`.
Bản đối chiếu độ phủ: `docs/reviews/S002-coverage-regression-check.md`.

| Status | Task ID | Tên việc | Mục đích | Tier | Effort | Thứ tự/phụ thuộc |
|---|---|---|---|---|---|---|
| DONE | T-00 | Mở dự án và dựng bộ điều hành | Chọn profile, khởi tạo trạng thái dự án, lập kế hoạch khảo sát và lộ trình sơ bộ | C | xhigh | Không phụ thuộc. Mở đường cho T-01 |
| DONE | T-01 | Kiểm kê hiện trạng toàn repo | Biết chính xác dự án đang có gì và đang đứng ở đâu, trước khi đụng vào bất cứ thứ gì | C | xhigh | Sau T-00. Chế độ AUDIT read-only |
| DONE | T-02 | Đối chiếu engine Python với spec | Xác minh bộ máy tính toán làm đúng như đặc tả, vì verdict sẽ dựa vào nó | C | xhigh | Sau T-01. Song song được với T-03 |
| VERIFYING | T-03 | Soát app web và rủi ro mất dữ liệu | Xác nhận 3 lỗi kế toán nghi vấn và đánh giá nguy cơ mất lịch sử giao dịch thật | C | high | Sau T-01. **CHECK-03-01 PASS tại WP-C1 (2026-09-02)** — gỡ BLOCKED; tất cả REQUIRED/RECOMMENDED check đều PASS. Chuyển DONE cần phiên riêng xác nhận Exit Criteria đầy đủ |
| DONE | T-04 | Chốt lộ trình và đóng băng tiêu chí | Soạn Ready Gate + Completion Gate cho 15 work package của RCP-001, đóng băng trước khi thực thi | C | xhigh | Sau T-01, T-02, T-03. HOÀN TẤT tại S002 — 15 file task đã đóng băng gate |
| PLANNED | T-05 | DUYỆT — phạm vi công cụ trước verdict | Chủ dự án quyết định được xây tới đâu khi cổng verdict chưa mở | DUYET | - | Sau T-04. KHÔNG nằm trên đường găng tới `T-06`/verdict (`RCP-002` điểm 9, đã áp dụng; xác nhận `DEC-029`) — chỉ chặn T-08 và WP-C2 |
| DONE | WP-A1 | Chứng minh nguồn gốc và khả năng tái lập của lần chạy chính thức | Để sau này còn chứng minh được kết quả chạy từ dữ liệu thật, đúng môi trường, và tái lập lại được | C | xhigh | Sau T-04. Song song với WP-A2, WP-A3, WP-C1. Thay thế T-06A cũ (đóng F-005, F-007, F-009, F-010, F-011). S017 (`DEC-027`, `OWNER_EXTENSION` +1): ba hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED` đã ĐÓNG — `F-E2A1-03` (official run bị TỪ CHỐI khi không phân giải được provenance, 0 artifact; non-official ghi `provenance_resolved`/`provenance_unresolved` tường minh), `F-E2A1R3-03` (case 13: `dev_limit` → `official_reason='dev_limit_set'` tại cả `run_gate1/2/3`), `F-E2A1R3-06`+`F-E2A1-08` (docs-only, production diff = 0). `CAP-PROV`: allowed 3 / used 3 / remaining 0. **CHECK-A1-11 = PASS/E2 tại E2 vòng BỐN** (`docs/reviews/E2-WP-A1-CHECK-A1-11-round4.md`, HEAD `990a6bb`, artifact `d24db30`/`6ca82f7`) — reviewer độc lập tự dựng venv sạch/non-editable, positive control từ git checkout thật, 17 probe eligibility, mutation testing xác nhận oracle hợp lệ, payload sha256 trước/sau repair giống hệt, full suite 377/377 (2 lần chạy độc lập). Bốn finding mới (N-01..N-04) đều HARDENING/docs-only, không BLOCKING. **DONE do Owner xác nhận tại Owner Checkpoint 2026-09-03 (`DEC-028`)**, đóng luôn `GATE-A`. Ràng buộc vận hành cho T-06: official run phải chạy từ canonical git checkout có lockfile hợp lệ, provenance không phân giải được thì fail loudly/fail closed. Biên bản: `docs/sessions/S017-wp-a1-repair-cycle-cuoi.md` |
| DONE | WP-A2 | Bật các hạng mục đã viết nhưng pipeline chưa chạy | Báo cáo chính thức hiện thiếu nhiều mục mà đặc tả bắt buộc phải có, dù code đã đúng | C | high | **DONE tại S006** (10/10 REQUIRED PASS; đấu nối thuần tuý — 4 module chỉ-đọc 0 dòng đổi; chiến lược + Benchmark A không đổi 159/159 trường) (đóng F-003, F-004, F-012, F-013, F-014). Tier C route tự nhiên sau MICRO-GOVDEF-001, xác nhận lại tại S006 |
| DONE | WP-A3 | Sửa vòng đời trạng thái thị trường và ladder khẩn cấp | Vốn có thể bị khoá vĩnh viễn khi thị trường hồi phục một phần rồi yếu lại | D | max | Sau T-04. HOÀN TẤT tại S003 (đóng F-001, F-021, F-022, F-030; 10/10 REQUIRED PASS, E2 PASS) |
| DONE | WP-A4 | Xử lý đúng khi dữ liệu thiếu hoặc hỏng | Dữ liệu Binance thật có lỗ hổng; xử lý sai sẽ làm sai kết quả mô phỏng | C | xhigh | **DONE lại tại S010** sau CAP-DATA REPAIR CYCLE #1 (`DEC-016`): 10/10 REQUIRED PASS (CHECK-A4-01…08 FROZEN + CHECK-A4-10 do `DEC-014` + **CHECK-A4-11** do `DEC-016`). Đóng F-023, F-025, F-032, **F-E2A1R3-05**, **F-S009-01**. Hết chặn WP-A6/WP-C4 về phía A4. Budget CAP-DATA: allowed 2 / used 1 / remaining 1. Batch review S010 PASS, 0 BLOCKING; sinh H-16, H-17 (hardening) và F-S010-03 (`OUT_OF_SCOPE` → WP-C4) |
| DONE | WP-A5 | Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược | Ba tín hiệu hiện không bao giờ được đo dù vẫn cho ra kết luận cuối cùng | C | xhigh | **IMPLEMENTED tại S015 (2026-09-03)** — 9/9 REQUIRED PASS (E1), đóng phần đo lường của **F-002** và toàn bộ **F-016**. Ba đại lượng chưa từng được sinh nay có đường sinh thật: `opportunity_cap_hit_share` (FS-02), `regime_advantage_share` (FS-12), `adjacent_config_flip` (FS-06, dựng từ 18 config OFAT của manifest Gate 2). FS-03/FS-07 mở phạm vi từ W5 ra 9 window gộp PrimaryMedian — **làm FS-03 lật FALSE → TRUE** (`ae_ex_month` 100,64 → 96,05), tức một window đại diện từng che mất một Failure Signal đang bật. Run đủ phase: **`UNKNOWN: []`**. Instrumentation so bit-for-bit với engine trước gói = trùng khớp; `git diff` trên `verdict.py`/`failure_signals.py` = rỗng. Suite 330/330. Quy ước đo lường: `docs/CONVENTIONS.md` #20 (a)–(f). Phát sinh **`F-S015-01`** (BLOCKING) — phần thuộc gói đã sửa, phần gốc → `WP-B1` (xem RSK-007). Biên bản: `docs/sessions/S015-wp-a5-do-failure-signal.md`. **DONE do chủ dự án phê chuẩn tại Owner Checkpoint S015 (2026-09-03)**, xác nhận không yêu cầu E2 bổ sung vì Completion Gate của gói không đòi E2 |
| DONE | WP-A6 | Chốt và kiểm chứng đúng thứ tự các bước tính toán | Thứ tự sai nghĩa là con số chính thức không đại diện đúng cho chiến lược đã đặc tả | D | max | **DONE tại S014 (2026-09-03)** — 8/8 REQUIRED PASS: test thứ tự viết từ chữ BT §19 đỏ trên engine cũ (F-019 đóng, F-018 nâng lên E1: cả ba quan sát XÁC NHẬN về thứ tự, quan sát 3 BÁC BỎ về hệ quả), tác động đo từng sai lệch trên dataset synth 7,5 năm (chỉ "tạo ladder sau bước 13" đổi kết quả: +0,054 %/+0,064 % ETH, −2/543 fill, nominal Base/Smart/Crash không đổi), quyết định SỬA `engine.py` theo chữ §19 (chỉ thứ tự), 22/22 test A6 PASS, thử phá có chủ đích bị bắt, no-lookahead 15m XÁC NHẬN (Impl Plan §7 mệnh đề 1). H-15 trả lời: GIỮ NGUYÊN (CONVENTIONS #19, 0 lần xảy ra trên dataset có cửa sổ INVALID 31 ngày; vế thứ ba của RE_TRIGGER_CONDITION còn mở, chờ T-06). **CHECK-A6-08 PASS (E2 độc lập)** — `docs/reviews/E2-WP-A6-thu-tu-18-buoc.md`, reviewer tự tái lập mọi con số trước khi đọc kết luận implementer, đồng ý toàn bộ quyết định. Hai finding non-blocking phát sinh từ E2 route sang `HARDENING_BACKLOG.md` H-24/H-25 (không mở lại Scope Lock — thuộc `ladders.py`/lifecycle, ngoài touch area). Đóng F-018, F-019. Biên bản: `docs/sessions/S014-wp-a6-thu-tu-18-buoc.md` |
| DONE | WP-A7 | Sửa phạm vi kế toán vốn Smart theo tháng | Vốn Smart gần như không bao giờ đi qua cơ chế ladder từ tháng thứ ba, và một chiều bắt buộc của Gate 2 bị vô hiệu | D | max | **DONE tại S004** (12/12 REQUIRED PASS; E2 PASS WITH FOLLOW-UPS; F-035 RESOLVED, RSK-010 CLOSED). Đã hết chặn WP-A5/WP-A6/WP-C4/GATE-A về phía A7; các gói đó còn chờ dependency khác (đóng F-035) |
| DONE | T-06 | Chạy backtest chính thức trên dữ liệu thật | Mở cổng verdict — đây là đường găng tới mục tiêu cuối | C | xhigh | **DONE tại `DEC-031`, 2026-09-03 — historical governance disposition, KHÔNG phải validation PASS.** Official verdict = **`DO_NOT_BUILD`** (Gate 1 FAIL, OOS hard condition FAIL). `can_proceed_to_app=false`. `V2.1.5` validation = **FAILED**. `DONE` ở đây chỉ có nghĩa: official execution lifecycle đã hoàn tất và evidence đã được canonicalize (`docs/T06_OFFICIAL_EVIDENCE_RECORD.md`) — KHÔNG có Ready Gate/Completion Gate task-level (khoảng trống governance lịch sử, đã dispositioned tại `DEC-031`, historical exception, KHÔNG tạo precedent). Code commit `5228130677e9e9875335eef890b6ed748a384603`, tag `v2.1.5-official-T06`. Cả hai nhóm prerequisite trước đây đã thoả: (A) GATE-A CLOSED (`DEC-028`); (B) BLK-001 RESOLVED (`DEC-031`) |
| DONE | WP-B1 | Chốt chính sách ra kết luận cuối (verdict) và ngưỡng cảnh báo | Không cho phép kết luận thuận lợi khi vẫn còn tín hiệu cảnh báo chưa đo được | D | max | **DONE (`DEC-034`, Lifecycle Closure 2026-09-04, sau `READY` tại `DEC-031`)** — **10/10 REQUIRED PASS** (CHECK-B1-01…10). Sau HAI vòng fresh Independent E2 liên tiếp FAIL (`E2-WP-B1-002`: `E2-B1-F01`/`E2-B1-F02` — sửa batch 1, 21 test; `E2-WP-B1-003`: cả hai finding CHƯA đóng hết — sửa batch 2, 49 test, `_numeric_and_finite()` viết lại triệt để + `run_verdict` hạ verdict về `INCONCLUSIVE` khi non-official), vòng E2 độc lập thứ BA (`E2-WP-B1-004-FRESH-ROUND3`) PASS trên đúng HEAD `9ac01b8`: tái lập độc lập cả hai finding lịch sử ĐÃ ĐÓNG, không BLOCKING mới, full suite 461/461 PASS. `CHECK-B1-09: NOT_TESTED → PASS`. Completion Gate = PASS. Verdict lịch sử T-06 (`DO_NOT_BUILD`) không đổi. Downstream KHÔNG tự mở: `GATE-B` vẫn chưa mở (`WP-B2` READY, `WP-B3` BLOCKED bởi `WP-C2`), `T-07` vẫn NOT READY. Xem file task để có evidence đầy đủ |
| READY | WP-B2 | Bổ sung test cho các yêu cầu đặc tả còn thiếu | Nhiều yêu cầu của BT §21 hiện không có gì kiểm chứng | C | xhigh | **READY tại `DEC-031`** — dependency `T-06 DONE` nay thoả, mọi mục khác đã `[x]` từ trước. Song song với WP-B1, WP-B3 |
| BLOCKED | WP-B3 | Hoàn thiện nhật ký quyết định để truy vết được | Cần truy vết được vì sao hệ thống ra quyết định như vậy tại từng thời điểm | C | high | Dependency `T-06 DONE` nay thoả (`DEC-031`); dependency `WP-C2 DONE` **CHƯA thoả** (`WP-C2` nay `READY` tại `DEC-035`, nhưng chưa `DONE`) — đây là lý do chặn DUY NHẤT còn lại. Ngữ nghĩa `previous_state/new_state` phụ thuộc WP-C2 (đóng F-024, F-033) |
| PLANNED | T-07 | DUYỆT — đọc verdict và chọn hướng đi | Verdict quyết định được xây app đầy đủ hay phải mở V2.2 | DUYET | - | `T-06` nay DONE (`DEC-031`, verdict `DO_NOT_BUILD`) nhưng **GATE-B CHƯA MỞ** (WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE — hiện cả ba đều chưa DONE, chỉ READY/BLOCKED). NOT READY. Chặn T-11 |
| DONE | WP-C1 | Kiểm chứng ba nghi vấn ở app web và khôi phục bộ test | App đang có thể dùng để ghi tiền thật; ba nghi vấn về sai sổ vẫn chưa có kết luận | C | xhigh | **DONE 2026-09-02** (8/8 REQUIRED PASS, E1). V-01 XÁC NHẬN, V-02 XÁC NHẬN, V-03 BÁC BỎ (an toàn tình cờ, HARDENING). Harness khôi phục (F-027 đóng). Gỡ BLOCKED cho T-03 (CHECK-03-01 PASS) |
| READY | WP-C2 | Làm rõ và đặt tên trạng thái thực thi của hệ thống | Cần biết rõ hệ thống đang ở trạng thái nào trước khi đưa vào dùng thật | C | xhigh | **READY tại `DEC-035`** (2026-09-04, PA-A) — phân xử HẸP cho Ready Gate, không chờ `DEC-005` chốt theo nghĩa rộng cho webapp (`DEC-005` vẫn PENDING, vẫn chặn T-08). `ADR-001` Accepted (`FUNDING_REQUIRED` = NOT_APPLICABLE ở tầng backtest). Chưa IN_PROGRESS — cần phiên thực thi riêng (đóng F-006) |
| PLANNED | WP-C3 | Xử lý mua một phần ở tầng sản phẩm | Mua một phần là tình huống thật ngoài đời, tầng ghi sổ hiện chưa xử lý đúng | C | xhigh | Sau WP-C2 (đóng F-020) |
| PLANNED | WP-C4 | Mở rộng phạm vi đối chiếu giữa hai bản cài đặt (Python/JS) | Hai bản cài đặt có thể trôi khỏi nhau khi thêm tính năng mới vào JS | C | xhigh | Sau WP-A3, WP-A4, WP-A6, **WP-A7** (không khoá parity vào hành vi Smart capital đã xác nhận là sai). Chặn T-10, T-11 (đóng F-008) |
| PLANNED | T-08 | Đặc tả lớp cảnh báo | Viết đặc tả còn thiếu cho tính năng cảnh báo mà chủ dự án muốn | C | xhigh | Sau T-05 |
| DONE | T-09A | Sửa lỗi kế toán trong app web | Vá lỗi WP-C1 xác nhận là có thật (V-01, V-02), trước khi app được dùng với tiền thật | C | high | **Phạm vi xác định tại WP-C1 (2026-09-02)**: (1) sửa `releaseLadder()` (`webapp/app_logic.js:302-322`) dùng đúng tháng gốc của ladder thay vì `currentMonth()`; (2) `reserveFor()`/`createLadder()` (`webapp/app_logic.js:289-297,324-335`) phải nhân giới hạn theo `view.smartUnlock`/`view.oppUnlock` trước khi cho reserve. V-03 BÁC BỎ nên không bắt buộc sửa, có thể cân nhắc thêm check `data_quality` tường minh như HARDENING phòng thủ (không bắt buộc). Sau WP-C1 (DONE). **IMPLEMENTED 2026-09-02** — 12/12 REQUIRED PASS (E1), V-01 và V-02 không còn tái hiện, batch review PASS 0 BLOCKING; Task Spec `docs/tasks/T-09A-sua-loi-ke-toan-app-web.md`. **DONE 2026-09-02** theo Owner Decision `DEC-018` (`OD-WEBAPP-01`) — Completion Gate giữ nguyên 12/12 REQUIRED PASS (E1), không sửa câu chữ/ngữ nghĩa |
| DONE | T-09B | Dựng lưu trữ dữ liệu bền (Firebase) | Chống mất lịch sử giao dịch — rủi ro lớn nhất của công cụ hiện tại | D | xhigh | **DONE 2026-09-03 (`DEC-024`)** — 16/16 REQUIRED PASS E1 (emulator + production CHECK-01/02/03/04/14 trên `tinphatcontent.web.app` thật). Sau T-04, WP-C1 (DONE), T-09A (DONE). Nên làm trước T-10. **Nền tảng persistence = Firebase — FIXED OWNER CONSTRAINT (`DEC-019`)**. Kiến trúc baseline `DEC-020`/`DEC-021`: Firebase Hosting → Firebase Anonymous Auth → Cloud Firestore (document `ethdca/state` + `ethdca/seed`). Task Spec: `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` (Task ID mới = 0). **`DEC-021` (Personal Tool Simplification Principle) đóng `OD-C` = R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)**: cross-device/cross-browser/lost-identity recovery KHÔNG phải V1 requirement (`H-23`, OUT OF SCOPE V1); `CHECK-T09B-04` tái phạm vi xuống same-browser-profile qua audit trail tường minh (OLD → OWNER PRODUCT INTENT CHANGE → NEW), KHÔNG phải bug fix. Ready Gate **15/15 ĐẠT**. Completion Gate 16/16 REQUIRED **FROZEN** 2026-09-02. **`T-09B: PLANNED → READY`.** Không còn Owner Decision nào chặn. `CAP-WEBAPP` budget KHÔNG đổi: 2/0/2 — chưa tiêu, chuyển READY không phải implementation. **S014 (2026-09-02): `READY → IN_PROGRESS → IMPLEMENTED`** — 16/16 REQUIRED PASS (E1, Firebase Emulator Suite), batch review PASS 0 BLOCKING, `H-29..H-32`; production commit `a19d3ad`, test `0d4917a`. **Chưa `DONE`**: project Firebase thật chưa tồn tại (REAL FIREBASE SETUP REQUIRED — `webapp/README.md`), chuyển `DONE` là hành vi chủ dự án. Budget 2/0/2 không đổi |
| PLANNED | T-10 | Triển khai lớp cảnh báo | Đưa cảnh báo theo chỉ báo vào app — thứ chủ dự án muốn nhất | C | xhigh | Sau T-08, T-09B, WP-C4 |
| DONE | WP-D1 | Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả | Dọn cho sạch, không ảnh hưởng gì tới kết quả hiện tại | B | medium | **DONE tại S005** (6/6 REQUIRED PASS; kết quả mô phỏng trùng khớp bit-for-bit, chỉ counter chẩn đoán đổi theo ngoại lệ khai báo) (đóng F-028, F-029, F-031, F-034) |
| READY | WP-D2 | Chuẩn bị đề xuất mở phiên bản đặc tả mới cho các điểm mâu thuẫn | Một số mâu thuẫn thuộc về chính bộ đặc tả, cần chủ dự án quyết định mở V2.2 | C | xhigh | Không phụ thuộc. Đầu ra là đề xuất, KHÔNG sửa V2.1.5 (đóng S-001, S-002, S-003) |
| PLANNED | T-11 | Tầng tự động hóa chiến lược đầy đủ | Hoàn thiện app MVP theo spec — phần bị cổng verdict khóa | D | max | Sau T-07, WP-C2, WP-C3, WP-C4, và chỉ khi verdict = BUILD |

## Roadmap Change Applied — RCP-001

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md` ngày 2026-08-23 kèm bốn quyết định.
Toàn bộ bốn quyết định đã được phản ánh vào bảng roadmap chuẩn ở trên. Chi tiết đầy đủ ghi ở
`PROJECT/PROJECT_DECISIONS.md` DEC-007, DEC-008, DEC-009.

1. **Cấu trúc 15 work package** — APPROVED nguyên trạng.
2. **Phân lớp A/B/C/D** — APPROVED WITH CONDITION: nếu remediation của F-017 (nằm trong WP-B1)
   ảnh hưởng tới input/calculation/execution behavior/dataset interpretation/strategy behavior/
   backtest behavior có khả năng tác động Gate 1, thì **mọi kết quả Gate 1 tạo trước đó bị coi
   là STALE/INVALIDATED và Gate 1 phải chạy lại** trước khi dùng cho verdict. Điều kiện này được
   ghi trực tiếp vào dependency column của WP-B1 ở bảng trên, và thành quy tắc chính thức ở
   DEC-009.
3. **Bỏ T-06A** — APPROVED. Toàn bộ phạm vi của T-06A được hấp thụ vào WP-A1, không mất
   requirement nào. WP-A1 vẫn là điều kiện bắt buộc trước T-06.
4. **WP-A2 routing** — OVERRIDE ROUTER. Tier C/Opus (không dùng B/Sonnet mà router trả), effort
   giữ nguyên `high` (giá trị router tính đúng, không bị ảnh hưởng bởi việc override Tier).
   Ghi tại DEC-008.

### Governance defect mới phát hiện trong quá trình duyệt

`routing_engine.py` dùng so sánh dấu phẩy động không có epsilon tại các mốc biên nguyên
(0/1/2/3). Với WP-A2, `model_score` hiển thị đúng `2.0` nhưng giá trị nội bộ là
`1.9999999999999998`, khiến `tier_from_score` (so sánh `s < 2`) trả về Tier B thay vì Tier C như
bảng `AGENT_CAPABILITY_MATRIX.md` quy định cho khoảng 2.00–2.99.

Đây là **defect của công cụ governance dùng chung, không phải finding của sản phẩm ETH DCA**.
Theo yêu cầu của chủ dự án, defect này được xử lý bằng ba artifact riêng, tách khỏi 33 finding
của S001:

- **Artifact:** `docs/reviews/GOVDEF-001-routing-engine-boundary.md`
- **Task:** `MICRO-GOVDEF-001` — xem mục "Micro Tasks (Inline)" bên dưới
- **Risk:** `GOV-RSK-001` — xem mục "Active Risks — Governance / Tooling" bên dưới

Không sửa `routing_engine.py` trong bước áp dụng roadmap này. Giải pháp sau này phải tổng quát
hoá cách so sánh (dùng epsilon hoặc làm tròn trước khi so sánh), không hard-code ngoại lệ riêng
cho WP-A2 hay bất kỳ task nào khác.

## Roadmap Change Applied — RCP-002

### Trạng thái: APPROVED WITH CONDITIONS — ĐÃ ÁP DỤNG (2026-08-24)

Chủ dự án phê duyệt `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md` kèm điều kiện bổ sung. Nguồn:
triage `docs/reviews/PH-03-triage-smart-unlock-scope.md` (PH-03 = **DEFECT** → **F-035**, HIGH).
Roadmap chuẩn tăng từ **28 → 29 task**.

Nội dung đã áp dụng:

1. **Thêm WP-A7** — "Sửa phạm vi kế toán vốn Smart theo tháng", lớp **A — MUST FIX BEFORE
   OFFICIAL RUN**, sở hữu **F-035**. Status `PLANNED` (chưa có file định nghĩa/gate → chưa
   READY). Routing xác nhận lại bằng `routing_engine.py` tại thời điểm áp dụng: **D / Fable / max**.
2. **Dependency bắt buộc mới** — WP-A7 là prerequisite của **WP-A5, WP-A6, WP-C4, GATE-A, T-06**.
3. **WP-A6** — Completion Gate cuối cùng **không được chạy** trước khi WP-A7 DONE; không được
   dùng test fixture suy biến hiện tại để né dependency này.
4. **WP-A5** — measurement tạo trước khi F-035 được sửa **không** được coi là canonical evidence
   cho engine cuối cùng.
5. **WP-C4** — không đóng băng parity JS/Python trên hành vi Smart capital đã xác nhận là sai.
6. **GATE-A** — định nghĩa lại thành `WP-A1…WP-A7 đều DONE`.
7. **T-06** — ghi rõ **hai nhóm prerequisite ĐỘC LẬP**: (A) nội tại = GATE-A gồm WP-A7;
   (B) hạ tầng = BLK-001. Gỡ BLK-001 **không** cho phép chạy T-06 khi GATE-A chưa PASS.
8. **WP-A4** — `MAY PROCEED IN PARALLEL` với WP-A7 về mặt semantic dependency, kèm ba điều kiện
   (xem RCP-002). "Parallel" ở đây là **roadmap parallelism**: không cho phép hai agent đồng thời
   sửa/merge cùng vùng `engine.py` mà không có branch isolation và merge ordering rõ ràng.
9. **WP-A3 giữ nguyên DONE** — không reopen, không sửa Completion Gate đã FROZEN, không làm mất
   evidence E1/E2. Ghi nhận: F-035 tồn tại **trước** WP-A3 và làm giảm **độ lớn** của một số quan
   sát liên quan Smart, nhưng **không invalidate** các kết luận đúng đắn mà WP-A3 đã chứng minh
   trong phạm vi của nó.

### Gate staleness (DEC-009 áp cho F-035)

F-035 có khả năng thay đổi capital allocation, Smart ladder creation, execution behavior,
deployed capital, ETH accumulated và kết quả Gate 1/2/3. Vì vậy **mọi Gate result tạo trước
remediation F-035 phải được coi là STALE / INVALIDATED khi dùng cho verdict**.

Trạng thái hiện tại: **NO CURRENT OFFICIAL RESULT TO INVALIDATE** — chưa từng có official run.
Điều kiện vì thế chuyển thành dependency bắt buộc: **WP-A7 phải DONE trước T-06**.

### Critical path sau RCP-002

```
T-04 ✅
 └─> WP-A3 ✅
      ├─> WP-A4 ✅ ─┐   (DONE tại S009)
      └─> WP-A7 ✅ ─┤
                    └─> WP-A6 ✅ (S014) ──> GATE-A ✅ ──> T-06 ✅ ──> WP-B1 (READY) ──┐
                                                    (DO_NOT_BUILD, DEC-031)  WP-B2 (READY) ─┤
                                                                             WP-B3 (BLOCKED: WP-C2) ─┘
                                                                                       │
                                                                              GATE-B (CHƯA MỞ) ──> T-07 (BLOCKED) ──> T-11 (BLOCKED)
WP-A1 ✅ (DONE, `DEC-028`), WP-A2 ✅, WP-A5 ✅ (S015) — tất cả prerequisite của GATE-A đã DONE.
GATE-A = WP-A1 ∧ WP-A2 ∧ WP-A3 ∧ WP-A4 ∧ WP-A5 ∧ WP-A6 ∧ WP-A7 đều DONE — **CLOSED** (`DEC-028`,
2026-09-03). **T-05 KHÔNG phải điều kiện của T-06** (`RCP-002` điểm 9, đã áp dụng; xác nhận
`DEC-029`).
T-06 = GATE-A ∧ BLK-001(resolved) — **CẢ HAI ĐÃ THOẢ, T-06 = DONE tại `DEC-031`** (historical
governance disposition; verdict `DO_NOT_BUILD`; KHÔNG phải validation PASS — xem `DEC-031`).
GATE-B = WP-B1 ∧ WP-B2 ∧ WP-B3 đều DONE — CHƯA MỞ (cả ba mới READY/BLOCKED, chưa DONE gói nào).
T-07 chờ GATE-B. T-11 còn cần thêm `verdict=BUILD` — verdict hiện là `DO_NOT_BUILD`.
```

## Current Task Snapshot

Task:
WP-D1 — Dọn các khoản nợ kỹ thuật không ảnh hưởng kết quả (S005)

Task Mode:
MAJOR (đủ điều kiện MICRO nhưng nâng lên MAJOR theo ghi chú frozen của file task)

Status:
DONE — 6/6 REQUIRED PASS (E1 toàn bộ); Exit Criteria 6/6.

File định nghĩa:
`docs/tasks/WP-D1-no-ky-thuat-khong-anh-huong-hanh-vi.md`

Required Gate Progress:
6 / 6 PASS. Chi tiết evidence trong file task và biên bản
`docs/sessions/S005-wp-d1-debt-cleanup.md`.

Kết quả chính của S005:
- Baseline E0/E1 (HEAD 1f4c2b7) tái hiện đủ 4 finding đúng như S001 mô tả: F-028
  (`expires_at` Smart ladder = `ts+31 ngày`, sai nghĩa nhưng không được đọc), F-029
  (`ladder_completed()` coi PARTIALLY_FILLED là kết thúc, zero caller), F-031 (bộ đếm
  cooldown override đếm theo zone thay vì sự kiện, chỉ dùng chẩn đoán), F-034
  (`_noon_candles` dead code).
- Kiểm tra rủi ro hành vi TRƯỚC khi sửa: xác nhận không finding nào chạm OSCORE/ladder/
  capital/execution/backtest/gate/verdict — không escalation nào kích hoạt.
- Test-first 4 test viết TRƯỚC fix: 4/4 FAIL đúng kỳ vọng → sau fix 4/4 PASS
  (`tests/test_wp_d1_debt_cleanup.py`).
- Remediation tối thiểu: `expires_at` tính đúng cuối accounting month (local);
  `ladder_completed()` bỏ PARTIALLY_FILLED khỏi tập kết thúc; `cooldown_override` đếm
  theo cycle (cờ `override_counted_this_cycle`); xoá `_noon_candles`.
- Toàn suite: **99 passed, 0 failed, 0 skipped** (95 cũ + 4 mới).
- Impact BEFORE/AFTER cùng dataset synth cố định: **toàn bộ 543 purchase record trùng
  khớp bit-for-bit** (so sánh `==` python); `eth_total` không đổi; mọi pool/ladder/
  transition/release giống hệt; **khác biệt DUY NHẤT** là `counters.cooldown_override`
  (tổng sự kiện 35→31) — đúng ngoại lệ đã khai báo trong Completion Gate.
- Không phát hiện finding/risk mới nào.

Primary Agent Tier:
B

Primary Effort:
medium

Model Routing Score:
1.0 (D1 R1 B1 A1 X1) → không floor → B

Effort Routing Score:
1.0 (U1 V1 H1 C1 F1) → không floor → medium

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Escalation Triggers:
- Theo file task WP-A3 (CAPABILITY_CEILING / CONFLICT DETECTED / metric đổi không giải thích
  được / phải chạm capital.py|score.py). Không trigger nào kích hoạt trong S003: một phương án
  thiết kế duy nhất (tách state/label) đạt đồng thời [F1] và vòng đời đóng; mọi sai lệch metric
  giải thích được; không chạm capital.py/score.py.

## Micro Tasks (Inline)

Use this section only when `governance/core/TASK_MODE_STANDARD.md` allows MICRO mode.

Canonical checklist:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Do NOT duplicate or rewrite the checklist here.

### MICRO-GOVDEF-001 — Sửa lỗi so sánh boundary trong routing_engine.py
Status:
DONE

Checklist Reference:
`governance/templates/MICRO_TASK_CHECKLIST.md`

Mô tả ngắn:
`tier_from_score`/`effort_from_score` trong `governance/scripts/governance/routing_engine.py`
dùng so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn, nên một điểm số ở đúng biên
nguyên (ví dụ 2.0) có thể bị tính sai một bậc Tier/Effort do sai số biểu diễn nhị phân
(`1.9999999999999998` thay vì `2.0`). Chi tiết đầy đủ, bằng chứng tái lập:
`docs/reviews/GOVDEF-001-routing-engine-boundary.md`.

Phạm vi được làm rõ tại T-04 (S002), theo đúng câu đã có sẵn trong DEC-008 mục Impact
("`validate_routing.py` cần được cập nhật ở một task riêng — MICRO-GOVDEF-001 hoặc kế tiếp"):
task này bao gồm **cả** `validate_routing.py`, để công cụ chấp nhận một manual override **có ghi
nhận** (kèm `Manual Override` và `Router Raw Output` trong file task) thay vì báo lỗi khớp tuyệt
đối. Đây là làm rõ phạm vi đã được DEC-008 dự liệu, không phải quyết định mới. Việc mở task này
vẫn cần chỉ thị của chủ dự án — xem BLK-003 và DEC-010.

Ràng buộc bắt buộc khi sửa: tổng quát hoá cách so sánh (làm tròn trước khi so sánh, hoặc dùng
epsilon nhất quán với `EPS` đã dùng ở nơi khác trong codebase, ví dụ `capital.py`).
**Không hard-code ngoại lệ riêng cho bất kỳ task nào** (kể cả WP-A2, task đã kích hoạt phát hiện
này).

Đánh giá MICRO eligibility (`TASK_MODE_STANDARD.md`): Difficulty <= 2, Risk <= 2, Blast Radius
<= 2 — không đổi kiến trúc, không đổi auth, không migration, không thao tác phá huỷ dữ liệu.
Đủ điều kiện MICRO. Chấm điểm tham khảo (không bắt buộc với MICRO): D1 R2 B2 A1 X1 → 1.45 → B;
U1 V2 H1 C1 F2 → 1.45 → medium.

Evidence Summary (2026-08-23, chủ dự án phê duyệt PA-1 cho DEC-010):

**Compact Ready Gate** (`MICRO_TASK_CHECKLIST.md`) — đủ điều kiện, xác nhận lại khi mở: yêu cầu rõ
ràng (sửa boundary comparison + validator override); Risk 2 <= 2; Blast Radius 2 <= 2; không đổi
kiến trúc/auth/schema/thao tác phá huỷ; phạm vi hẹp và đã biết (`routing_engine.py`,
`validate_routing.py`, test governance mới); phương pháp kiểm chứng đã biết (brute-force toàn không
gian đầu vào + test override tổng hợp).

**Compact Completion Gate:**
- [x] Hành vi dự định đã cài đặt — `routing_engine.py` làm tròn `model_score`/`effort_score` về 3
  chữ số **trước khi** so sánh biên (căn cứ: trọng số chỉ có tối đa 2 chữ số thập phân, nên làm
  tròn 3 chữ số loại bỏ đúng nhiễu IEEE-754 ~1e-15, không đổi giá trị thật) — không phải epsilon
  tuỳ tiện, không hard-code WP-A2 hay bất kỳ task nào.
- [x] `validate_routing.py` chấp nhận manual override có ghi nhận (decision reference tồn tại
  trong `PROJECT_DECISIONS.md`, `Router Raw Output` xác thực khớp router hiện tại, chỉ được leo
  thang Tier/Effort chứ không hạ) — hàm `check_override`, tổng quát cho mọi `DEC-###`.
- [x] Verification thực sự chạy: brute-force toàn bộ 5^5 × 5^5 tổ hợp đầu vào cho **0** lệch còn
  lại; `governance/scripts/governance/test_routing_engine.py` — **37/37 check PASS**, gồm 6 ca
  override hợp lệ/không hợp lệ tổng hợp (không phụ thuộc WP-A2).
- [x] Evidence ghi theo `EVIDENCE_STANDARD.md`, mức E1 (chạy thật): xem
  `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- [x] Không mở rộng phạm vi ngoài dự kiến — `git diff` xác nhận chỉ chạm
  `governance/scripts/governance/routing_engine.py`, `validate_routing.py` (thêm), file task
  `WP-A2` (chỉ bổ sung ghi chú, không xoá dấu vết), và các artifact governance liên quan. Không
  chạm `src/`, `webapp/`, `tests/`, `docs/spec/`.
- [x] Regression liên quan đã PASS: `routing_engine.py`/`validate_routing.py` chạy lại trên toàn bộ
  16 file MAJOR task hiện có — **đúng một dòng đổi** (WP-A2, Tier B → C), không task nào khác đổi
  Tier/Effort. `ROUTING VALIDATION: PASS (16 MAJOR task file(s) checked, 0 accepted manual
  override(s))`.
- [x] `PROJECT/PROJECT_PROGRESS.md` inline Micro Task entry được cập nhật — mục này.

**Kết quả:** BLK-003 RESOLVED. GOV-RSK-001 CLOSED. WP-A2 chuyển `BLOCKED` → `READY`, giữ nguyên
Tier C / Opus / Effort high (nay route tự nhiên, không cần override — nhưng dấu vết DEC-008/Manual
Override/Router Raw Output trong file WP-A2 được **giữ nguyên**, không xoá).

Chi tiết đầy đủ: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
Test: `governance/scripts/governance/test_routing_engine.py`.

## Active Blockers

### BLK-001 — RESOLVED (Không có đường tới dữ liệu Binance từ môi trường phát triển)
Trạng thái: **RESOLVED — 2026-09-03, tại `DEC-031`.** Production-realistic Mac environment
của Owner có kết nối Binance (`api.binance.com`/`data.binance.vision` → HTTP 200); official
fetch đã thực hiện thành công; official real Binance dataset đã tạo (`dataset_hash` tái tính
REPOSITORY-VERIFIED khớp tuyệt đối, `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §3.2); `T-06` đã
thực thi trên dữ liệu thật. Lịch sử blocker dưới đây được GIỮ NGUYÊN, không xoá.

Ảnh hưởng (lịch sử, tại thời điểm còn ACTIVE): **chỉ T-06** (RCP-001 xác định lại: không work package nào trong 15 gói lớp A/B/C/D
cần dữ liệu Binance thật — toàn bộ phát triển và kiểm chứng được trên dữ liệu tổng hợp theo
DEC-003). T-06 là điểm duy nhất trên đường găng cần blocker này được gỡ; T-07 và T-11 chỉ bị
chặn gián tiếp qua chuỗi phụ thuộc vào T-06, không phải trực tiếp bởi BLK-001.

Mô tả: Repo chưa từng có official run (`results/` không tồn tại và nằm trong `.gitignore`).
Môi trường phát triển bị chặn egress tới Binance, nên mọi kiểm chứng trong repo chạy trên dữ
liệu tổng hợp và tự gắn cờ `official: false`.
Đường xử lý đã được `docs/DATA_SOURCES.md` chấp nhận: chạy `ethdca fetch` trên máy của chủ dự án
hoặc VPS nước ngoài, copy `data/raw/` về, rồi xác minh bằng cách chạy `ethdca freeze` ở cả hai
máy và đối chiếu hash manifest phải trùng khớp.
Cần từ chủ dự án: một máy hoặc VPS truy cập được `data.binance.vision` và `api.binance.com`.

Bằng chứng E1 thu tại S000 (2026-08-23): cả ba host đều bị chặn ở tầng proxy, không phải lỗi
cấu hình phía repo.
`api.binance.com` → `curl: (56) CONNECT tunnel failed, response 403`
`data-api.binance.vision` → `curl: (56) CONNECT tunnel failed, response 403`
`api.coingecko.com` → `curl: (56) CONNECT tunnel failed, response 403`
PyPI thì thông, nên đây là chặn có chọn lọc theo host, không phải mất mạng.

Không bypass BLK-001. Không đổi nguồn dữ liệu. Không dùng dữ liệu tổng hợp để tạo official
verdict.

### BLK-003 — RESOLVED (`validate_routing.py` chưa biểu diễn được manual override đã được phê duyệt)
Trạng thái: **RESOLVED — 2026-08-23, tại MICRO-GOVDEF-001.**
Ảnh hưởng khi còn mở: **chỉ WP-A2**.

Mô tả: `governance/scripts/governance/validate_routing.py` so khớp **tuyệt đối** giữa
`Primary Agent Tier` trong file task và kết quả của `routing_engine.py`. Khi T-04 soạn file định
nghĩa cho WP-A2 với Tier C theo DEC-008, validator báo:

```
ROUTING VALIDATION: FAIL
- docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md: Tier 'C' != router B
```

Đây **không phải defect mới**. DEC-008 mục Impact đã ghi trước rằng tình huống này sẽ xảy ra và
rằng `validate_routing.py` "cần được cập nhật ở một task riêng (MICRO-GOVDEF-001 hoặc kế tiếp) để
chấp nhận override có ghi nhận thay vì báo lỗi khớp tuyệt đối". T-04 làm đúng phần được giao và
không làm phần được giao cho task khác.

Vì sao nó chặn WP-A2: `CLAUDE.md` mục "Every Implementation Session" điểm 9 yêu cầu
`validate_routing.py` **PASS trước khi thực thi** một MAJOR task; `ROADMAP_SYNC_STANDARD.md` cũng
yêu cầu chạy validator này trước roadmap sync. Vì vậy WP-A2 giữ trạng thái `BLOCKED` cho tới khi
điều kiện được gỡ.

Đường gỡ (cần chủ dự án quyết định — xem DEC-010):
1. Cho phép mở `MICRO-GOVDEF-001` (đã mở rộng phạm vi để phủ cả `validate_routing.py`), hoặc
2. Miễn trừ bằng văn bản, ghi vào `PROJECT/PROJECT_DECISIONS.md`.

**Không được gỡ bằng cách hạ Tier WP-A2 về B** — DEC-008 cấm, và làm vậy là hạ tiêu chuẩn để
validator xanh.

Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-02.

**Cách đã gỡ (2026-08-23):** chủ dự án phê duyệt **PA-1**. `routing_engine.py` được sửa tổng quát
(làm tròn điểm số về cùng độ chính xác hiển thị trước khi so sánh biên); `validate_routing.py` được
bổ sung cơ chế chấp nhận manual override có ghi nhận. Sau fix, `validate_routing.py` PASS cho toàn
bộ 16 file MAJOR task, và WP-A2 route Tier C **tự nhiên** (không cần nhánh override nữa, dù nhánh đó
đã được xây và kiểm chứng độc lập cho các trường hợp tương lai). Không hạ Tier WP-A2 về B.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution";
`MICRO-GOVDEF-001` ở mục "Micro Tasks (Inline)".

### BLK-002 — Tính năng cảnh báo chưa được đặc tả
Ảnh hưởng: T-10, và là lý do T-08 tồn tại.
Mô tả: `docs/spec/01_PRODUCT_SPEC_V2_1_5.md` không có mục nào về alert/cảnh báo/notification.
Product Spec chỉ quy định trạng thái hiển thị thụ động trên hero khi mở trang (§11–§13).
Implementation Plan §9 hoãn có chủ đích: "không cần cron cho tới khi thực sự cần notification".
Điều kiện kích hoạt thì đã có đầy đủ trong Strategy Spec (§3, §4, §5, §9, §10, §15, §17, §18)
và danh mục 30 reason code ở Strategy §20 chính là bộ khung tự nhiên cho danh sách cảnh báo.
Nghĩa là: đây là khoảng trống ĐẶC TẢ, không phải khoảng trống code. Không thể triển khai đúng
trước khi đặc tả xong (T-08).

## Active Risks

### RSK-001 — Mất lịch sử giao dịch thật (mức: cao)
App web hiện lưu state trong localStorage của trình duyệt cộng cơ chế tự xuất bản lại trang.
Đây không phải "một database" như Implementation Plan §9 yêu cầu. Xóa dữ liệu site, dùng cửa sổ
riêng tư, đổi máy, hoặc publish thất bại đều có thể làm mất dữ liệu chưa xuất ra ngoài.
Giảm thiểu: T-09B. Cho tới khi T-09B xong, chủ dự án nên xuất file JSON định kỳ.
**Cập nhật 2026-09-02 (`DEC-019`)**: nền tảng giảm thiểu đã được chốt là **Firebase**; T-09B có Task Spec
và Completion Gate FINALIZED (`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`). Risk **CHƯA giảm** — chưa
một dòng production nào đổi. T-09B vẫn `PLANNED`, chờ `OD-A`/`OD-B`/`OD-B2`. Khuyến nghị xuất JSON định kỳ
vẫn còn nguyên hiệu lực.
**Cập nhật 2026-09-02 (`DEC-020`)**: `OD-A`/`OD-B`/`OD-B2` đã RESOLVED (Firebase Hosting · Cloud
Firestore · Anonymous Auth). Phát hiện khe mới `OD-C`: kịch bản **"đổi máy"** nêu tên ngay trong risk này
cần thêm một quyết định (recovery credential hay chấp nhận giới hạn) trước khi coi là được đóng bằng
đường Firebase Auth thuần. Risk **VẪN CHƯA giảm** — chưa một dòng production nào đổi. Khuyến nghị xuất
JSON định kỳ vẫn còn nguyên hiệu lực, đặc biệt trước khi đổi máy.
**Cập nhật 2026-09-02 (`DEC-021`)**: `OD-C` đóng = **R2 (SIMPLIFIED PERSONAL-TOOL RECOVERY)** — chủ dự
án chấp nhận rằng kịch bản **"đổi máy"** (và đổi trình duyệt, mất browser profile) sẽ **KHÔNG** tự phục
hồi qua Firebase Auth trong V1 (`H-23`, OUT OF SCOPE V1). Lối thoát cho kịch bản này VẪN LÀ xuất JSON
thủ công — khuyến nghị này **không đổi và quan trọng hơn trước**, vì đây nay là cách DUY NHẤT đóng đúng
kịch bản "đổi máy" ở V1. Kịch bản "xoá dữ liệu site (chỉ localStorage/sessionStorage)" và "publish thất
bại" (nay là "Firebase write thất bại") vẫn được T-09B đóng qua đường Firestore một khi implementation
hoàn tất — risk **VẪN CHƯA giảm** cho tới khi đó, vì chưa một dòng production nào đổi. `T-09B` nay
`READY`, Completion Gate FROZEN 16/16 REQUIRED.
**Cập nhật 2026-09-02 (S014 — T-09B IMPLEMENTED)**: giảm thiểu đã được **cài đặt** (`a19d3ad`) và
**kiểm chứng E1 trên Firebase Emulator Suite**: xoá `localStorage`+`sessionStorage` vẫn phục hồi sổ
từ Firestore (CHECK-03); đóng/mở lại trình duyệt cùng profile vẫn tiếp tục (CHECK-04); ghi thất bại
/ mất mạng hiện rõ, không báo "đã lưu" giả, giữ bản local để cứu (CHECK-10); bản bền hỏng không bị
nạp, không bị ghi đè (CHECK-12); hai tab không ghi đè lẫn nhau (CHECK-16). Risk **CHƯA giảm trên
thực tế** vì project Firebase thật chưa tồn tại và chủ dự án vẫn đang ở bản artifact cũ — giảm khi
(a) thiết lập xong theo `webapp/README.md`, (b) dữ liệu cũ được export/import sang app Firebase,
(c) chuỗi CHECK-01/02/03/04/14 được lặp lại bằng tay trên app thật. Kịch bản "đổi máy" vẫn mở theo
`H-23` (export/import JSON). Risk KHÔNG tự đóng — thẩm quyền chủ dự án.
**Cập nhật 2026-09-03 (production verification PASS)**: cả ba điều kiện (a)/(c) ở trên nay ĐẠT —
chủ dự án đã tạo project Firebase thật (`tinphatcontent`, dùng chung với Content, `DEC-023`),
deploy Hosting + rules với Owner UID thật, và tự tay lặp lại CHECK-01/02/03/04/14 trên
`https://tinphatcontent.web.app` thật — **PASS cả 5, E1** (Owner báo cáo trực tiếp; agent không
tự tới được `*.web.app` để tái xác nhận độc lập — xem giới hạn trung thực đầy đủ ở
`docs/reviews/T-09B-production-verification.md`). Kịch bản chính risk này nêu tên — **xoá dữ
liệu site (localStorage/sessionStorage) và mất khả năng ghi (nay đã chuyển sang Firestore)** —
nay có bằng chứng giảm thiểu **trên hạ tầng thật**, không chỉ emulator. (b) "dữ liệu cũ được
export/import sang app Firebase" **chưa áp dụng** — sổ Owner test trên production hiện là
synthetic (rev 4), Owner chưa nạp dữ liệu tài chính thật; đây là bước Owner tự làm sau khi dọn
dữ liệu test, không thuộc phạm vi risk này. Kịch bản "đổi máy"/"cửa sổ riêng tư" **vẫn mở**
theo `H-23` (OUT OF SCOPE V1, `DEC-021`) — không đổi bởi cập nhật này; khuyến nghị xuất JSON
định kỳ vẫn còn hiệu lực cho đúng kịch bản đó. **Risk giảm đáng kể trên thực tế cho phần trong
scope V1; đóng hẳn (`DONE`) vẫn là quyết định của chủ dự án** (`STATE_AUTHORITY.md`).
**Cập nhật 2026-09-03 (`DEC-024`, Owner Confirmation)**: chủ dự án xác nhận tường minh disposition
trên — ghi nhận phần V1 durable persistence đã kiểm chứng trên production, `H-23` tiếp tục
HARDENING/OUT OF SCOPE V1 theo `DEC-021`, không mở task mới từ risk này. `T-09B: IMPLEMENTED →
DONE`. Risk KHÔNG được tuyên bố đóng hẳn (`CLOSED`) — chỉ disposition trên được xác nhận.

### RSK-002 — Hai bản cài đặt chiến lược trôi khỏi nhau (mức: cao) — S001 XÁC NHẬN (E1)
Implementation Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Trang
tĩnh không chạy được Python nên `webapp/engine.js` là bản cài đặt thứ hai của cùng đặc tả.
Cơ chế chặn hiện có là parity check OSCORE 40 ngày (lệch tối đa 7.4e-11 lần kiểm gần nhất),
nhưng parity chỉ phủ OSCORE tổng — chưa phủ unlock, spacing, phân bổ ladder, invalidation,
regime. Mỗi tính năng port thêm sang JS sẽ mở rộng bề mặt trôi nhanh hơn khả năng phát hiện.
Giảm thiểu: **WP-C4** (RCP-001) — mở rộng phạm vi parity trước khi port thêm.

### RSK-003 — Ba lỗi kế toán trong app web (mức: CAO — hai trong ba XÁC NHẬN LÀ LỖI THẬT) — WP-C1 XÁC NHẬN (E1)
Ghi nhận ban đầu từ việc đọc code: (a) hàm chọn tháng hiện hành trả về tháng có key lớn nhất
chứ không phải tháng của ladder, nên release vốn có thể trả nhầm pool khi có nhiều tháng;
(b) mức unlock không giới hạn số vốn được reserve; (c) trạng thái dữ liệu INVALID không chặn
tạo action mới như Strategy §3 yêu cầu.

**Cập nhật WP-C1 (2026-09-02) — kết luận E1 bằng ca kiểm thử chạy thật, không đọc code suông**
(`webapp/test_v01_v02_v03.js`, `webapp/test_multi_month_invariant.js` — output đầy đủ trong
`docs/tasks/WP-C1-xac-minh-webapp-va-khoi-phuc-harness.md`):

- **(a) V-01 — XÁC NHẬN LÀ LỖI THẬT.** Ca kiểm thử đa tháng (ladder tháng A + ladder riêng
  tháng B, huỷ ladder tháng A khi tháng B đang là `currentMonth()`) cho thấy `releaseLadder()`
  (`webapp/app_logic.js:302-322`) cộng nhầm vốn vào `smart.a` tháng B đồng thời rút nhầm từ
  `smart.r` đang backing ladder RIÊNG, còn ACTIVE, của tháng B — trong khi `smart.r` của tháng
  A (nơi vốn thực sự bị reserve) không hề giảm, tức KẸT VĨNH VIỄN. Tái hiện được cả bằng thao
  tác Hủy thủ công lẫn qua luồng invalidation tự động (2 daily close liên tiếp trên
  invalidation price).
- **(b) V-02 — XÁC NHẬN LÀ LỖI THẬT.** Với Smart unlock đo được = 0,0% (OSCORE thật của seed),
  `reserveFor()` (`webapp/app_logic.js:289-297`) vẫn cho reserve 100% Smart available — không
  hề so sánh với `view.smartUnlock`. Vi phạm trực tiếp Strategy §12 "Không được reserve vốn
  chưa unlock".
- **(c) V-03 — BÁC BỎ về hành vi quan sát được, nhưng an toàn một cách TÌNH CỜ, không phải do
  chủ đích.** Toán học của `engine.js` khiến `data_quality = INVALID` (cần <7 ngày lịch sử) và
  `adr30` hữu hạn (cần ≥30 ngày) không bao giờ cùng đúng, nên `createLadder()` luôn bị chặn bởi
  guard ADR30 trước khi có cơ hội tạo ladder khi INVALID — dù `createLadder()` không hề kiểm
  tra `data_quality`. Ghi HARDENING (không BLOCKING) vì cơ chế bảo vệ này dễ vỡ nếu spacing
  logic thay đổi độc lập với data quality sau này — xem `PROJECT/HARDENING_BACKLOG.md`.

**Escalation đã kích hoạt theo đúng trigger của WP-C1 và T-03**: NV-1/NV-2 (=V-01/V-02) là lỗi
thật → nếu app đang được dùng để ghi tiền thật, phải dừng dùng hoặc xuất dữ liệu ra ngoài trước
khi tiếp tục, cho tới khi **T-09A** vá xong. Severity nâng lên **HIGH**.

Sửa: **T-09A** (đã có phạm vi xác định — xem mục T-09A trong roadmap).

**Cập nhật T-09A (2026-09-02) — hai lỗi ĐÃ VÁ, escalation GỠ; risk hạ xuống mức thấp, CHƯA
đóng.** Bằng chứng E1 chạy thật trên đường sản phẩm
(`webapp/test_t09a_accounting.js`, 68 assertion — **17 FAIL trước vá, 0 FAIL sau vá**;
`docs/tasks/T-09A-sua-loi-ke-toan-app-web.md`; `docs/reviews/T-09A-batch-review.md`):

- **(a) V-01 — ĐÃ VÁ.** Ladder nay mang tháng sở hữu tường minh (`L.month`) ghi ngay tại lúc
  reserve; release VÀ deploy đều quay về đúng pool tháng đó. Reproduction gốc của WP-C1
  (`test_v01_v02_v03.js::testV01`) chạy lại cho **BÁC BỎ**: huỷ ladder tháng A trả 1.000.000 đ
  về đúng `smart.a` tháng A, pool tháng B (đang backing một ladder ACTIVE riêng) không đổi một
  đồng. Ca đa tháng của `test_multi_month_invariant.js` cũng hết kẹt vốn (`smart.r` tháng 1 về
  0 sau invalidation, trước đây kẹt 1.755.550 đ).
- **(b) V-02 — ĐÃ VÁ.** `reserveFor()` nay áp đúng công thức của
  `capital.py::smart_reservable`. Với Smart unlock = 0,0% thì reserve bị TỪ CHỐI hoàn toàn và
  pool không bị đụng (fail closed, không side effect); biên trên kiểm tại 101% / 99,9% hạn
  mức; hạn mức trừ dần phần đã reserve/deploy trong tháng. Reproduction gốc cho **BÁC BỎ**.
- **(c) V-03 — KHÔNG ĐỔI.** Vẫn BÁC BỎ, `H-18` giữ nguyên DEFERRED: ba điều kiện re-trigger
  đều không xảy ra (`webapp/engine.js` 0 dòng đổi).

Vì sao **chưa đóng RSK-003** ở phiên này: `STATE_AUTHORITY.md` dành `DONE` cho chủ dự án, và
risk này gắn với `T-09A` + `T-03` — cả hai chưa được chủ dự án chuyển trạng thái. Escalation
"dừng dùng app với tiền thật" thì **gỡ được ngay**: hai đường làm sai sổ đã bị chặn và có test
hồi quy giữ chúng. Lưu ý dữ liệu cũ: state đã lưu TRƯỚC bản vá có thể đã sai sẵn do V-01/V-02;
bản vá KHÔNG migrate và KHÔNG sửa lịch sử — chủ dự án cần tự đối chiếu sổ. Ladder tạo trước
bản vá được suy luận tháng sở hữu và ĐƯỢC BÁO HIỆN bằng banner trên app.

### RSK-004 — Bộ test app web không chạy được từ bản checkout sạch (mức: trung bình) — S001 XÁC NHẬN (E1); **ĐÃ KHẮC PHỤC tại WP-C1 (2026-09-02)**
Bằng chứng E1 tại S000: hai test webapp **chạy được và cho kết quả đúng**, nhưng chỉ sau khi
dựng thủ công hai thứ không có trong repo — `webapp/app_final.html` (phải build) và
`demo/results3/live_seed.json` (**không tồn tại ở bất kỳ đâu trong repo**).
Nghĩa là không ai clone repo về mà chạy được test của app, và không có gì bảo vệ hồi quy tự động.

Ghi nhận thêm: hai test ghi ảnh chụp màn hình vào thư mục làm việc hiện hành. Nếu chạy từ trong
`webapp/` sẽ để lại `app-dash.png` và `app-zone.png` trong repo, mà hai file này không nằm trong
`.gitignore`.

**Cập nhật WP-C1 (2026-09-02) — RESOLVED, bằng chứng E1 chạy thật từ bản checkout sạch mô
phỏng** (xoá toàn bộ artifact sinh ra, làm lại từ đầu chỉ bằng lệnh trong repo):
`webapp/package.json` (mới, ghim `playwright@1.56.1`) + `npm --prefix webapp install` →
`ethdca synth` + `ethdca export-live --out-dir demo/results3` (dữ liệu DEMO/SYNTHETIC) →
`node webapp/build_app.js` → `npm --prefix webapp test` (4 test: `test_app.js`, `test_zone.js`,
`test_v01_v02_v03.js` mới, `test_multi_month_invariant.js` mới) — exit code 0, không page
error. `build_app.js`/`test_*.js` chuyển từ path tương đối theo `process.cwd()` sang
`__dirname` nên chạy đúng dù gọi từ gốc repo hay từ trong `webapp/`. Ảnh chụp màn hình
(`app-dash.png`, `app-zone.png`) và `app_final.html` nay nằm trong `.gitignore`;
`git status --porcelain` sau khi chạy test không xuất hiện file nào trong số đó. Đóng F-027.

### RSK-005 — Quy ước không thuộc spec đang nằm trong đường ra verdict (mức: trung bình) — S001 XÁC NHẬN VÀ MỞ RỘNG (E1)
S001 xác nhận và phát hiện quy ước không được ghi ở nhiều chỗ hơn dự kiến: ngoài ánh xạ
gate-fail → verdict, còn có ngưỡng số tự đặt của FS-02/FS-07/FS-12, phạm vi tính FS-03/FS-07 chỉ
trên window W5, và tham số `shift_days=10` của Control G. `verdict.py` còn ghi rằng ánh xạ được
tài liệu hoá ở `docs/CONVENTIONS.md`, nhưng file đó không có mục nào về verdict.
Xem finding F-015, F-016, F-026. Giảm thiểu: **WP-B1** (RCP-001).

`src/eth_dca_os/verdict.py` ánh xạ "gate nào trượt → verdict nào". Implementation Plan §5 không
quy định ánh xạ này; đây là quy ước triển khai. Cần ghi nhận rõ để không bị coi nhầm là điều
khoản spec. Nếu muốn nâng thành chuẩn thì phải qua V2.2, không vá tại chỗ V2.1.5.

### RSK-006 — Không ghim phiên bản thư viện, nên kết quả không tái lập được theo thời gian (mức: cao) — S001 XÁC NHẬN (E1)
Bằng chứng E1 tại S000: `pyproject.toml` chỉ đặt sàn (`numpy>=1.26`, `pandas>=2.1`,
`pyarrow>=14`), không có lockfile và không có trần. Khi cài mới, pip kéo về `numpy 2.4.6`,
`pandas 3.0.5`, `pyarrow 25.0.1` — vượt xa sàn tới hai thế hệ lớn. Toàn bộ 69 test vẫn PASS
trên bộ này, đó là tín hiệu tốt về độ bền, nhưng là **may mắn chứ không phải bảo đảm**.

Vì sao mức cao: Implementation Plan §7 đặt tính tái lập làm tiêu chí nghiệm thu —
"cùng dataset hash + config hash + manifest hash + seed thì tái lập chính xác cùng kết quả".
Run record hiện lưu hash của config, manifest, dataset và seed, **nhưng không lưu phiên bản thư
viện**. Một thay đổi dấu phẩy động trong numpy/pandas ở phiên bản sau có thể làm official run
không tái lập được, mà không ai phát hiện — vì mọi hash đầu vào vẫn trùng khớp.

Giảm thiểu: **WP-A1** (RCP-001) — thay thế T-06A, đóng đủ cả 8 trường provenance yêu cầu
(Python version, dependency/lock hash, git commit SHA, dataset hash, strategy config hash,
execution config hash, manifest hash, seed), không chỉ ghim thư viện.

**Cập nhật S017 (2026-09-03) — mức: cao → trung bình.** Tám trường provenance đã được ghi và
khoá bằng test từ S007/S008 (`CHECK-A1-01` PASS, có assertion CỨNG bác hai giá trị suy biến).
Repair cycle cuối của WP-A1 (`DEC-027`, đóng `F-E2A1-03`) bổ sung vế còn thiếu: một run được
ghi `official` mà KHÔNG phân giải được `code_commit` hoặc `dependency_lock_hash` nay **bị từ
chối ngay, chưa file nào được tạo** (`ProvenanceUnresolvedError`), thay vì ghi im lặng. Run
không official vẫn chạy được nhưng mang `provenance_resolved: false` và danh sách
`provenance_unresolved` tường minh trên record.
**Phần dư:** ghi được phiên bản thư viện KHÔNG đồng nghĩa với việc kết quả bất biến theo thời
gian — trôi phiên bản vẫn có thể đổi số ở mức dấu phẩy động. Điều đã đạt là trôi phiên bản nay
**phát hiện được** (`GOVERNANCE_V4.md` §II.8: lệch phiên bản ⇒ `ENVIRONMENT_REVERIFY_REQUIRED`),
chứ không phải bị loại trừ.

### RSK-007 — Pipeline không chạy nhiều hạng mục mà spec ghi là bắt buộc cho official run (mức: cao → **trung bình**) — **ĐÃ GIẢM THIỂU: S006 (WP-A2 DONE) + S015 (WP-A5 DONE)**; phần dư = giá trị official chờ T-06, chính sách chờ WP-B1
**Cập nhật S006 (2026-08-24):** WP-A2 (DONE) đã đấu nối **toàn bộ** phần thuộc quyền sở hữu của
nó: Benchmark B/C/D (F-003), ablation §2.3 + volume z-score §2.4 kèm bảng chênh lệch (F-004),
bảng coverage §4 (F-012), XIRR §16 (F-013), bootstrap 1000/block length cho official (F-014).
Bằng chứng E1: 9 test wiring chạy `run_gate1` thật (8 FAIL trước fix → 9/9 PASS sau fix), spy
đo trực tiếp `n_sims` 200→1000; đấu nối KHÔNG đổi kết quả chiến lược/Benchmark A (159 trường
metric, 0 khác biệt). Nguyên tắc BT §22 nay áp dụng được.
**Cập nhật S015 (2026-09-03) — WP-A5 DONE, RSK-007 ĐÓNG phần đo lường:** ba Failure Signal
FS-02, FS-06, FS-12 nay được sinh và truyền thật (`opportunity_cap_hit_share`,
`adjacent_config_flip`, `regime_advantage_share`), và phạm vi tính của FS-03/FS-07 đã mở từ
một window đại diện (W5) ra cả chín window bằng PrimaryMedian (đóng **F-016**). Quy ước đo
lường của cả năm đại lượng: `docs/CONVENTIONS.md` #20. Sau một run đủ phase không còn Failure
Signal nào UNKNOWN vì thiếu đo lường; mọi trường hợp không tính được đều mang `reason` ghi
trong run record (`failure_signal_inputs_wp_a5`).
**Phần CÒN LẠI của risk (không thuộc WP-A5):** giá trị số của các signal chỉ mới đo trên dữ
liệu tổng hợp — số official phải chờ `T-06` (BLK-001). Việc *dùng* các signal này (ngưỡng,
chính sách UNKNOWN, quy tắc chặn BUILD) thuộc **WP-B1**.

**`F-S015-01` — quy tắc chặn BT §17 không nhìn thấy signal mang kiểu `numpy.bool_`
(BLOCKING, owner = `WP-B1`, phát hiện tại S015).** `failure_signals.py` gộp cờ chặn bằng
`any_true = any(v is True for v in fs.values())`, và `verdict.py:27` đọc đúng cờ đó. Nhưng
`numpy.bool_(True) is True` cho **False**, nên một Failure Signal TRUE mang kiểu numpy sẽ
**vô hình** với quy tắc chặn — trong khi BT §17 nói dứt khoát *"BUILD là không thể khi còn
bất kỳ Failure Signal nào TRUE"*. Hệ quả nghiệp vụ: nếu Gate 1/2/3 đều PASS và signal TRUE
duy nhất mang kiểu numpy, verdict sẽ ra **BUILD** kèm lý do "không Failure Signal nào TRUE",
mở đường sang phase app (T-07 → T-11) sai.
Bằng chứng E1 tại S015: (a) `np.bool_(True) is True` → `False`; (b) run đủ phase TRƯỚC khi
WP-A5 sửa kiểu ghi ra `"FS-11": "False"`, `"FS-12": "True"` dạng **chuỗi** — dấu vết của
`numpy.bool_` đi qua `json.dumps(default=str)`; (c) test
`test_a5_04_numpy_typed_signal_would_be_invisible` tái lập cơ chế và sẽ ĐỎ khi khiếm khuyết
được đóng.
Phạm vi đã xử lý trong WP-A5: hai đại lượng do gói này cấp (FS-02, FS-12) nay được ép về
`float` thuần Python tại `metrics.py`, có test kiểu và test "cờ chặn nhìn thấy được".
**Phần CÒN MỞ (ngoài Expected Touch Area của WP-A5):** `FS-11` vẫn nhận `numpy.bool_` từ
`oos_ae`, và bản thân `any_true` vẫn mong manh với mọi đầu vào numpy trong tương lai. Sửa
gốc nằm ở `failure_signals.py` — file mà WP-A5 bị cấm chạm và `CHECK-A5-07` bắt buộc chứng
minh là KHÔNG đổi. Định tuyến: **`WP-B1`** (sở hữu chính sách verdict, đóng phần chính sách
của F-002). **Lưu ý trình tự cần chủ dự án quyết:** roadmap đặt `WP-B1` SAU `T-06`, nhưng
chính `T-06` mới là nơi phát ra verdict official — nên khiếm khuyết này phải được đóng
TRƯỚC khi verdict của `T-06` được coi là có thẩm quyền. Đây là quyết định trình tự của chủ
dự án; phiên S015 KHÔNG tự đổi roadmap và KHÔNG tạo task mới.

Nội dung gốc S001 (giữ nguyên để audit) — S001 phát hiện (E1): Benchmark B/C/D, ablation §2.3, volume z-score §2.4, bảng coverage §4 và
XIRR §16 đều đã được cài đặt đúng nhưng **không nơi nào trong pipeline gọi chúng**. Hệ quả: một
official run sẽ phát ra verdict kèm báo cáo thiếu, và nguyên tắc Backtest §22 ("luật đơn giản
thắng nếu kết quả tương đương") không thể áp dụng vì không có B/C/D để so.
Ngoài ra ba Failure Signal (FS-02, FS-06, FS-12) không bao giờ được truyền input nên luôn UNKNOWN,
trong khi verdict BUILD vẫn phát ra bình thường.
Xem finding F-002, F-003, F-004, F-012, F-013. Giảm thiểu: **WP-A2, WP-A5** (RCP-001).

### RSK-008 — Run trên dữ liệu tổng hợp vẫn được ghi nhận là official (mức: cao) — S001 XÁC NHẬN (E1)
S001 xác nhận (E1): cờ `official` chỉ phụ thuộc việc có dùng `--dev-limit` hay không, hoàn toàn
không kiểm nguồn dữ liệu; và `lineage.json` ghi `source` là chuỗi cố định `'see fetch/synth'` cho
cả dữ liệu thật lẫn dữ liệu tổng hợp. Chạy `ethdca synth && ethdca run all` sẽ tạo record mang
`official: true` trên dữ liệu nhân tạo, không có trường nào cho phép phát hiện về sau.
Đây là rủi ro thẳng vào tính toàn vẹn của verdict — tức vào chính cổng mở đường cho app.
Xem finding F-005. Giảm thiểu: **WP-A1** (RCP-001).

**Cập nhật S017 (2026-09-03) — mức: cao → thấp.** Cờ `official` nay là **hàm dẫn xuất** từ
lineage đã verify checksum, không còn phụ thuộc `--dev-limit`: `official_eligibility` kiểm
nguồn **trên từng series** với `REAL_SOURCES = {binance_bulk_archive, binance_rest}`, nên
`synthetic` và `unknown` không bao giờ đủ tư cách (`CHECK-A1-07`, và
`test_a1_07_no_cli_or_env_surface_can_force_official` khẳng định không có flag CLI/biến môi
trường nào ép được). Chuỗi cố định `'see fetch/synth'` đã bị loại bỏ và có test cấm nó quay
lại. Repair cycle cuối (`DEC-027`, đóng `F-E2A1R3-03`) bịt nốt khe **diễn giải**: khi
`dev_limit` là thứ hạ cờ official, `official_reason` nay ghi đúng `dev_limit_set` theo contract
case 13 thay vì để `'verified'` che nguyên nhân.
**Phần dư:** vận hành viên sửa TAY `lineage.json` vẫn nằm ngoài tầm của mã — đối trọng là
`ethdca freeze` hai máy theo `DEC-003`, đã công bố tại `docs/CONVENTIONS.md` và `H-06`/`H-13`.

### RSK-009 — Vòng đời Crash ladder hở, vốn có thể bị khoá vĩnh viễn (mức: cao) — ĐÃ REMEDIATE tại S003 (WP-A3)
S001 phát hiện và kiểm chứng bằng chạy thật (E1): khi giai đoạn RECOVERY kết thúc lúc thị trường
còn yếu, regime chuyển thành STRESSED chứ không phải NORMAL, nên nhánh dọn Crash ladder ở
`engine.py:415` không bao giờ chạy. Reserve của Crash zone không được giải phóng, kéo theo không
tạo được ladder mới và cash ratio tăng giả tạo — có thể bóp méo chính FS-02 và FS-07.
Đây đồng thời là vi phạm [F1] (STRESSED phải không có hiệu ứng execution).
Xem finding F-001. Giảm thiểu: **WP-A3** (RCP-001).

**Cập nhật S003 (2026-08-23): CLOSED.** WP-A3 (DONE) đã tách trạng thái nền khỏi nhãn STRESSED
(`RegimeTracker.state`/`.label`, CONVENTIONS #14) và nhánh dọn chạy cho MỌI kết cục kết thúc
Recovery; bằng chứng E1: baseline tái hiện lock 27.2 đơn vị trước fix → 0 sau fix, chuỗi test
CHECK-A3-01/02, suite 87 PASS; E2 độc lập PASS — reviewer tự dựng kịch bản khác (kẹt 18.7 trên
code cũ, release đủ trên code mới) và không tìm thấy đường khoá vốn mới sau 4 kịch bản tự nghĩ.

### RSK-010 — Phạm vi kế toán của Smart unlock sai: Smart ladder ngừng hình thành từ tháng thứ ba (mức: cao) — **CLOSED (F-035 RESOLVED tại S004)**
Trạng thái: **CLOSED 2026-08-24** — WP-A7 DONE qua Completion Gate frozen (12/12 REQUIRED
PASS, E2 độc lập PASS WITH FOLLOW-UPS). Lịch sử xác nhận defect giữ nguyên bên dưới.

**Cập nhật S004 (2026-08-24): CLOSED.** WP-A7 (DONE) đưa kế toán Smart về đúng phạm vi
accounting month (PA-A — bộ đếm tháng trong `Pool` + một hook mở sổ tại rollover;
CONVENTIONS #17), giữ nguyên ledger audit lifetime DM §6. Bằng chứng E1: unit+engine
nhiều tháng (quyền tháng mới trọn vẹn ở unlock 1.0, 4/4 rồi 5/5 tháng đều tạo ladder),
suite 95 PASS; impact: Smart qua ladder 0.0208% → 24.49%, snapshot [F5] sống lại phần
Smart; E2 độc lập tái lập toàn bộ và tự dựng counterexample (probe3, probe5a/b): không
đường khoá/rò vốn mới, worst over-grant = +0.000000. Chiều `smart_unlock_mode` hết chết
cơ học (phân kỳ quyền vốn ở test C; phân kỳ tới tận eth_total ở probe3 của reviewer).
Giới hạn còn lại ở tầng outcome trên full synth → PH-04 (ngoài scope, chờ chủ dự án).

Nội dung dưới đây là hồ sơ trạng thái TRƯỚC khi đóng (giữ nguyên để audit):
Finding chính thức: **F-035** · Severity **HIGH** · Evidence **E1** (chứng minh cấu trúc + chạy
thật), có xác nhận độc lập kế thừa từ reviewer E2-WP-A3-001.

`smart_reservable` so ngân sách Smart **theo tháng** với `pool.deployed` **luỹ kế toàn đời**
(`Pool` không có vòng đời tháng, trong khi Data Model §5 `monthly_budgets` định nghĩa
`smart_available/reserved/deployed_vnd` là trường của bản ghi **tháng** có `status OPEN/CLOSED`).
Vì Month-End (ST §10) giải ngân hết phần Smart mỗi tháng, `deployed` tăng ~một ngân sách tháng
mỗi tháng ⇒ từ tháng thứ ba hàm trả **0 tất định, vĩnh viễn, không phụ thuộc dữ liệu**, kể cả ở
`SMART_UNLOCK = 1.00`.

Hệ quả đo được (90 tháng dữ liệu tổng hợp): **2** Smart ladder; **99,98%** vốn Smart bỏ qua cơ
chế ladder (ST §12) và chảy qua luật phần dư cuối tháng; **chiều `smart_unlock_mode` — 1 trong 8
chiều bắt buộc của Gate 2 (BT §9) — trơ hoàn toàn**, ba mode HWM/NO_HWM/DECAY_HWM cho kết quả
**trùng khít bit-for-bit** trong khi ST §6 yêu cầu báo cáo đóng góp riêng từng mode; snapshot
[F5] của Crash ladder bị triệt tiêu phần Smart (che ~78% tác dụng thật của remediation F-021 vừa
xong ở WP-A3).

**Official backtest KHÔNG đáng tin trước khi sửa** (Gate 1/2/3 đều đo trên engine mà 30% vốn
không đi qua cơ chế được đặc tả). Áp dụng **DEC-009**: mọi kết quả Gate 1 tạo trước remediation
là STALE/INVALIDATED — hiện `no current result to invalidate` (chưa từng có official run), nên
điều kiện chuyển thành dependency bắt buộc: **phải DONE trước T-06**.

Tồn tại **trước** WP-A3, **không phải hồi quy** của WP-A3; WP-A3 giữ nguyên DONE và gate FROZEN.
Ownership: **WP-A7** (lớp A, đường găng, D/Fable/max) — **ĐÃ CHỐT**: RCP-002 được chủ dự án phê
duyệt kèm điều kiện và **đã áp dụng** vào bảng roadmap chuẩn ngày 2026-08-24. WP-A7 là
prerequisite của WP-A5, WP-A6, WP-C4, GATE-A, T-06.
Trạng thái risk (lịch sử): CONFIRMED DEFECT — OPEN, sẽ đóng khi WP-A7 DONE → **đã đóng
tại S004 như ghi ở đầu mục**.

Triage đầy đủ (requirement canonical, root cause, bằng chứng, phân lớp, ảnh hưởng gate, đánh giá
WP-A4): `docs/reviews/PH-03-triage-smart-unlock-scope.md`.

### PH-04 — Ba mode `smart_unlock` phân kỳ ở tầng quyền vốn nhưng vẫn trùng kết quả cuối trên full run (GHI NHẬN S004 — chờ chủ dự án, CHƯA triage, KHÔNG remediation)

Phát hiện trong S004 (WP-A7), **ngoài Scope Lock**, ghi nhận theo đúng quy trình
"phát hiện mới không sửa trong phiên":

Sau khi F-035 được sửa, ba mode HWM / NO_HWM / DECAY_HWM đã **phân kỳ thật** ở tầng
unlock path và quyền vốn (`smart_reservable` cuối kịch bản tất định: 14.36 / 11.36 / 0.00
— test C của WP-A7), tức chiều ablation không còn chết cơ học theo đúng câu chữ
CHECK-A7-03. Tuy nhiên trên **full synthetic run 90 tháng**, ba mode vẫn cho `eth_total`
trùng **bit-for-bit** (21.637034604792). Nguyên nhân cấu trúc (E1, đã xác minh bằng probe):
engine hiện chỉ **tiêu thụ** `effective_unlock` tại đúng hai điểm — (a) tạo Smart ladder
one-shot ở lần eff > 0 đầu tiên trong tháng, nơi peak == current nên ba mode cho cùng giá
trị (CONVENTIONS #1); (b) crash snapshot [F5], nơi OSCORE ≥ 75 ⇒ smart_unlock = 1.0 ở mọi
mode. ST §6 yêu cầu ba mode nằm trong Gate-2 ablation với "báo cáo đóng góp riêng" (BT §9)
— muốn chiều này phân biệt được ở tầng OUTCOME cần một kênh tiêu thụ unlock **liên tục
trong tháng** (ví dụ top-up/resize ladder khi eff tăng), là thay đổi hành vi engine nằm
ngoài phạm vi WP-A7 (phạm vi kế toán) và không được đặc tả tường minh trong V2.1.5.

Phương án thuộc thẩm quyền chủ dự án: (1) mở WP mới trong lớp A/B; (2) chuyển WP-D2 đề
xuất V2.2; (3) chấp nhận như giới hạn đã biết của Gate-2 ablation dimension này. Chi tiết:
`docs/sessions/S004-wp-a7-monthly-smart-scope.md` mục "PH-04".

**Tinh chỉnh của reviewer E2 (F-E2A7-03, 2026-08-24):** hai mệnh đề đỡ của PH-04 là
thuộc tính CỦA DATASET, không phải bất biến cấu trúc — reviewer tự dựng được kịch bản
(crash chiếm vốn làm hoãn tạo ladder qua thời điểm phân kỳ) trong đó 3 mode phân kỳ tới
tận `eth_total` NGAY với engine hiện tại; và "crash snapshot ⇒ 1.0 mọi mode" cần thêm
điều kiện `dq != INVALID` tại nến entry. Vậy sức phân giải của chiều này trên dataset
chính thức là câu hỏi EMPIRICAL — nên ĐO trước khi diễn giải `Gate2_PreOOS_PassShare`,
không mặc định chiều này trơ ở tầng outcome. (probe3 trong
`docs/reviews/E2-WP-A7-monthly-smart-scope.md` là mẫu kịch bản tái lập.)

## Active Risks — Governance / Tooling

Rủi ro của bản thân bộ công cụ governance dùng chung, **tách khỏi rủi ro sản phẩm ETH DCA** ở
mục trên. Không tính vào 33 finding của S001.

### GOV-RSK-001 — Sai số biên dấu phẩy động trong routing_engine.py có thể under-route task đúng biên (mức: trung bình) — CLOSED
Phát hiện khi áp dụng RCP-001 (2026-08-23), tái lập được (E1): `tier_from_score` và
`effort_from_score` so sánh `<` trực tiếp trên giá trị dấu phẩy động chưa làm tròn/chưa có
epsilon. Một task có điểm nền đúng bằng 2.0 (biên Tier B/C) có thể nhận `model_score` nội bộ là
`1.9999999999999998` do cách `0.25*D+0.25*R+0.20*B+0.15*A+0.15*X` cộng dồn sai số nhị phân, và
bị route xuống Tier B thay vì Tier C.

Trường hợp cụ thể đã xác nhận: WP-A2 (D2 R2 B2 A1 X3) — hiển thị `model_score: 2.0` nhưng nội bộ
`1.9999999999999998`, router trả Tier B trong khi bảng `AGENT_CAPABILITY_MATRIX.md` quy định
2.00–2.99 → Tier C.

Ảnh hưởng: bất kỳ task nào (không riêng dự án này) có điểm nền rơi đúng vào các mốc nguyên
0/1/2/3 đều có nguy cơ tương tự, theo cả hai chiều (có thể over-route hoặc under-route tuỳ dấu
sai số). Mức trung bình vì hệ quả là chọn sai một bậc Tier/Effort, không phải sai kết quả tính
toán nghiệp vụ.

Giảm thiểu tạm thời đã áp dụng cho WP-A2: **manual override** theo DEC-008, ghi nhận công khai
trong bảng roadmap.
Giảm thiểu triệt để: **MICRO-GOVDEF-001** — **HOÀN TẤT 2026-08-23**. `routing_engine.py` làm tròn
điểm số về cùng độ chính xác hiển thị trước khi so sánh biên; xác nhận bằng quét toàn bộ 5^5 × 5^5
tổ hợp đầu vào cho 0 lệch còn lại (`test_routing_engine.py`, 37/37 PASS). WP-A2 nay route Tier C tự
nhiên, không cần override. Không task nào khác trong 16 file MAJOR hiện có bị ảnh hưởng.
Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".

## Open Regression Items
- None ở tầng mã nguồn. S001 không phát hiện code nào bám theo hành vi của V2.1.1–V2.1.4 trái với
  V2.1.5; bảy sửa đổi F1–F7 đều có dấu vết hiện thực.
- **PH-01 (tài liệu, không phải mã nguồn)** — bảng "Tổng hợp" của `docs/reviews/S001-audit-findings.md`
  ghi MEDIUM 15 và Tổng 33, nhưng đếm thật trên chính danh mục được liệt kê cho **34 định danh
  `F-xxx`** (HIGH 8 + MEDIUM 19 + LOW 7) cộng 3 `S-xxx`. Con số 33 đã được chép sang tài liệu này và
  sang RCP-001. **Không finding nào bị rơi** — RCP-001 §2 và §6 phân đủ 34 `F-xxx` vào 15 gói, và
  T-04 xác nhận 40/40 định danh có nơi thuộc về. T-04 **không tự sửa** con số trong biên bản audit
  của phiên đã đóng; chờ chủ dự án quyết định cách đính chính.
  Bằng chứng E1: `docs/reviews/S002-coverage-regression-check.md` mục PH-01.

## Recent Decisions
- DEC-001 — Chọn profile PRODUCT
- DEC-002 — Phiên S001 chạy chế độ AUDIT read-only
- DEC-003 — Dữ liệu tổng hợp không bao giờ dùng để ra verdict
- DEC-004 — Xác nhận provider mapping Tier A/B/C/D
- DEC-005 — PENDING: phạm vi công cụ trước verdict (chờ chủ dự án duyệt tại T-05)
- DEC-006 — Source of Truth cho compliance audit là V2.1.5, không phải V2.1.3
- DEC-007 — RCP-001 được phê duyệt và áp dụng kèm bốn điều kiện
- DEC-008 — Ghi đè thủ công routing của WP-A2 (Tier C, không dùng Tier B từ router)
- DEC-009 — Quy tắc Gate 1 staleness: remediation ảnh hưởng Gate 1 bắt buộc chạy lại Gate 1
- DEC-010 — RESOLVED: PA-1 phê duyệt cho BLK-003; `routing_engine.py`/`validate_routing.py` đã sửa
- DEC-011 — Owner Product Intent và V1 Daily-Use Acceptance (tiêu chí A–F)
- DEC-012 — Hạn mức repair budget cho CAP-PROV: allowed 2 / used 2 / remaining 0
- DEC-013 — **RESOLVED / INTEGRATED**: phương án A (INTEGRATE NOW); canonical trunk = `main`;
  integration SHA `febc2ec` (merge commit thường, 0 xung đột, tree kết quả TRÙNG KHÍT tree source)
- DEC-014 — `OD-A4-01`: bổ sung MỘT REQUIRED check cho WP-A4 (`CHECK-A4-10`) và làm rõ
  Expected Touch Area; `F-E2A1R3-05` → `CAP-DATA`, hấp thụ vào WP-A4, 0 task ID mới
- DEC-015 — `F-S009-01` → capability owner `CAP-DATA`; spec verdict `IMPLEMENTATION_DEFECT`;
  CONFIRMED BLOCKING V1 giữ nguyên; 0 task ID mới. `OWNER_ASSIGNMENT_REQUIRED` ĐÓNG, còn
  `OWNER_DECISION_REQUIRED` cho phương tiện thi hành
- DEC-016 — `OD-DATA-01`: `F-S009-01` = CONFIRMED BLOCKING V1; phương tiện thi hành được
  duyệt = **REOPEN WP-A4 cho ĐÚNG MỘT repair cycle**, mở touch area tối thiểu sang
  `indicators.py` + wiring/test trực tiếp; 0 task ID mới, 0 WP mới. **GHI NHẬN, CHƯA THI
  HÀNH** — `OWNER_DECISION_REQUIRED` của `DEC-015` nhờ đó ĐÓNG
- DEC-017 — `OD-DATA-02`: `CAP-DATA` Effective Risk = **HIGH**; hạn mức repair budget
  allowed 2 / used 0 / remaining 2 (khai hạn mức, KHÔNG reset). Bản sửa `F-S009-01` sẽ là
  repair cycle **#1**

Chi tiết: `PROJECT/PROJECT_DECISIONS.md`.

## Session History
- S022 — DEC-029 INTEGRATION CLOSURE (`DEC-032`) — 2026-09-03 — branch
  `claude/coindca-data-stream-vv0vwv`. Governance/state-sync session, KHÔNG thực hiện thêm
  integration. Owner đã tự fast-forward `main` lên đúng DATA head TRƯỚC phiên này (không force
  push, không rebase, không reset, không squash, không cherry-pick). Đo lại độc lập bằng git:
  `origin/main` = `origin/claude/coindca-data-stream-vv0vwv` = `3284371131935f518952feb95ef0235df0b48cfc`;
  ahead/behind = 0/0; merge-base = cùng SHA đó (true fast-forward); tag
  `v2.1.5-official-T06` không đổi, vẫn peel `5228130677e9e9875335eef890b6ed748a384603`;
  `branch_authority_check.sh` PASS (`INTEGRATION_DECISION_REQUIRED=NO`, production diff =
  EMPTY). Ghi `DEC-032` (`OD-INT-02`): `DEC-029` chuyển `INTEGRATION_REVIEW_REQUIRED` (ghi tại
  `DEC-031`) → **`RESOLVED / INTEGRATED`** (nhãn tái sử dụng từ tiền lệ `DEC-013`, không tự
  phát minh state mới). KHÔNG đổi `T-06` (`DONE`), `V2.1.5` validation (`FAILED`), verdict
  (`DO_NOT_BUILD`), `can_proceed_to_app` (`false`), `BLK-001` (`RESOLVED`), `WP-B1`/`WP-B2`
  (`READY`), `WP-B3` (`BLOCKED` bởi `WP-C2`), `GATE-B` (chưa mở), `T-07` (`NOT READY`), `T-11`
  (`BLOCKED`). Không chạy WP-B1/B2/B3, không resolve WP-C2, không mở GATE-B/T-07/V2.2, không AE
  audit, không Control F, không rerun T-06, không move/recreate tag, không thêm merge/rebase/
  reset/squash/cherry-pick nào. Production diff = 0; không sửa `src/`/`tests/`/`webapp/`/
  lockfile/task files/evidence record. 7 validator governance liên quan PASS (`Checked 0` ở
  `validate_evidence`/`validate_task_completion` là vacuous đã biết, KHÔNG dùng làm bằng chứng
  closure — bằng chứng đến từ số đo git). Chi tiết đầy đủ:
  `docs/sessions/S022-dec029-integration-closure.md`.
- S020 — T-06 HISTORICAL GOVERNANCE DISPOSITION (`DEC-031`) — 2026-09-03 — branch
  `claude/coindca-data-stream-vv0vwv`. Owner ban hành **`DEC-031`** (`OD-T06DISP-01`,
  `PROJECT/PROJECT_DECISIONS.md`) sau khi review S018/S019: **`T-06: PLANNED → DONE`**
  (historical governance disposition, KHÔNG phải validation PASS — verdict giữ nguyên
  `DO_NOT_BUILD`, `can_proceed_to_app=false`, `V2.1.5` validation = FAILED) và
  **`BLK-001: ACTIVE → RESOLVED`**.

  (1) **Cơ sở governance** — đọc đầy đủ 6 file CORE (`AGENTS.md` §1 hàng 1–6) trước khi ghi
  quyết định; không tìm thấy rule nào cấm. `GOVERNANCE_V4.md` § II.10 Conditions For
  Convergence: *"its Completion Gate PASSes, **or the Owner has dispositioned it**"* — đúng
  cơ chế Owner dùng ở đây, không phải ngoại lệ ngoài governance. `STATE_AUTHORITY.md`: `DONE`
  = "Owner, hoặc completion authority được chỉ định" — đúng thẩm quyền.

  (2) **Owner KHÔNG cho phép** tạo Ready Gate/Completion Gate hậu nghiệm cho `T-06` (từ chối
  PHƯƠNG ÁN A ở `OD-T06-03`, chọn PHƯƠNG ÁN B). Lý do: retrospective freeze sau khi biết kết
  quả làm suy yếu nguyên tắc pre-commit/freeze. Đây là **historical exception, phạm vi ĐÚNG
  T-06, KHÔNG tạo precedent** cho task tương lai — mọi task tương lai vẫn tuân thủ Ready
  Gate/frozen Completion Gate TRƯỚC execution như hiện hành.

  (3) **BLK-001 RESOLVED** — dựa trên: production-realistic Mac environment của Owner có kết
  nối Binance, official fetch thành công, dataset thật đã tạo (`dataset_hash` tái tính
  REPOSITORY-VERIFIED khớp tuyệt đối tại S019), đường hai máy `DEC-003` là countermeasure cho
  kịch bản copy chứ không phải acceptance criterion bắt buộc khi fetch+run cùng máy. Lịch sử
  blocker giữ nguyên trong § Active Blockers, chỉ thêm nhãn RESOLVED.

  (4) **Dependency re-evaluation** (chỉ cập nhật readiness, KHÔNG thực thi, KHÔNG tự đánh dấu
  DONE) — `WP-B1`: `PLANNED → READY` (cả `Dependency T-06 DONE` và `Dependency WP-A5 DONE`
  nay đúng; `WP-A5 DONE` là fact đã có từ `DEC-025`/S015, checkbox task file chỉ chưa được
  đồng bộ trước đây, nay đồng bộ). `WP-B2`: `PLANNED → READY`. `WP-B3`: `PLANNED → BLOCKED`
  (dependency `T-06 DONE` nay đúng, nhưng `Dependency WP-C2 DONE` VẪN sai — `WP-C2` vẫn
  `BLOCKED`, không đổi bởi quyết định này — lý do chặn DUY NHẤT còn lại). `GATE-B` (= cả ba
  gói B đều DONE) **CHƯA MỞ** — READY không phải DONE. `T-07` (đòi `T-06 ∧ GATE-B`) **VẪN
  PLANNED, NOT READY**. `T-11` không chỉ bị chặn theo chuỗi mà còn cần `verdict=BUILD` —
  verdict là `DO_NOT_BUILD`, không applicable trừ khi hoàn cảnh đổi (ngoài phạm vi).

  (5) **Disposition `OD-T06-01`…`OD-T06-10`** (từ S018, không tự động đóng hết) — bảng đầy đủ
  trong `DEC-031`: `RESOLVED_BY_S019` (`OD-T06-01`, `OD-T06-02`); `RESOLVED_BY_THIS_DECISION`
  (`OD-T06-03`, `OD-T06-05` — `H-06` `ACCEPT_AS_IS`, `OD-T06-10` — Python patch mismatch
  routed `CAP-PROV`/`H-02`, `ENVIRONMENT_REVERIFY_REQUIRED` theo `GOVERNANCE_V4.md` § II.8,
  KHÔNG sửa lockfile); `STILL_OPEN` (`OD-T06-04` `H-13`, `OD-T06-06` `H-16`, `OD-T06-08`
  `H-24`/`H-25`, `OD-T06-09` `H-27`/`H-04`/`H-14`/`H-28`); `ROUTED_HARDENING` (`OD-T06-07`
  `H-01`, đã đủ, không cần thêm input). Ghi chú disposition thêm vào `H-06`/`H-02` — phân loại
  HARDENING và `RE_TRIGGER_CONDITION` của cả hai GIỮ NGUYÊN. `H-13`/`H-01`/`H-16`/`H-24`/
  `H-25`/`H-27`/`H-28` **KHÔNG bị chạm**.

  (6) **`DEC-029` integration trigger** — review deadline condition ("BLK-001 removed AND
  T-06 ready/executed") nay đã thoả. Ghi nhận **`INTEGRATION_REVIEW_REQUIRED`** — session
  **KHÔNG** tự merge/rebase/reset/squash; quyết định integration thuộc Owner.

  Đồng bộ thêm: `PROJECT/CAPABILITY_REGISTRY.md` (§ Vertical Acceptance Slice — đã chạy 1 lần,
  `DO_NOT_BUILD`, không phải Golden trace tái lập được vì cấm rerun; dòng `CAP-VERDICT`),
  `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` (§Trạng thái/§11/§12 sync sau `DEC-031`).

  Validator: `branch_authority_check.sh` **PASS** (`production diff = EMPTY`), 7/7 governance
  validator **PASS**, đọc **không vacuous** (`validate_evidence`/`validate_task_completion`
  vẫn `Checked 0` do `H-08`, KHÔNG được đọc như bằng chứng T-06 hợp lệ — hợp lệ đến từ
  `DEC-031`, không từ validator rỗng). `sync_easy_roadmap.py` regenerate
  `LO_TRINH_DE_HIEU.md` phản ánh đúng thay đổi trên.

  Không sửa `src/`/`tests/`/`webapp/`/lockfile. Production diff = 0. Official run KHÔNG bị
  chạy lại. Không mở `V2.2`, không chọn Objective A/C, không AE audit, không Control F
  investigation, không tạo task ID mới. Biên bản đầy đủ:
  `docs/sessions/S020-t06-historical-disposition-dec031.md`.
- S019 — T-06 EVIDENCE PRESERVATION / CANONICALIZATION — 2026-09-03 — branch
  `claude/coindca-data-stream-vv0vwv` @ `f7f98a9` → thêm evidence-only commit. **KHÔNG state
  nào bị đổi**: `T-06` giữ `PLANNED`, `BLK-001` giữ ACTIVE trong sổ, không Owner Decision nào
  được ban hành, không task ID mới, `production diff = EMPTY`. Tiếp nối trực tiếp S018.

  Owner đã thực hiện bảo toàn evidence bên ngoài container: backup 16/16 raw artifact (3
  parquet + `lineage.json` + toàn bộ `results/`) ra vị trí độc lập trên máy đã chạy `T-06`,
  tự verify SHA-256 khớp, và tạo + push **annotated git tag `v2.1.5-official-T06`**.

  (1) **Xác nhận tag** — `git ls-remote --tags origin` + `git cat-file -p` xác nhận tag là
  annotated (object riêng) và peel **đúng** về `5228130677e9e9875335eef890b6ed748a384603`
  (= `code_commit` của official run). Message tag mang `dataset_hash`/verdict khớp khai báo.

  (2) **Canonical evidence package** — tạo `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` (một file,
  không tạo subsystem `docs/evidence/` mới, đặt cạnh `CONVENTIONS.md`/`DATA_SOURCES.md`,
  tham chiếu thêm vào `docs/INDEX.md`). Package phân biệt tường minh
  **REPOSITORY-VERIFIED** / **OWNER-REPORTED / EXTERNALLY-VERIFIED** / **NOT PRESENT IN
  REPOSITORY** cho từng khẳng định, không nâng nhãn.

  (3) **Phát hiện mới** (nâng chất lượng evidence so với S018): `dataset_hash` khai báo
  (`3150860cb379…`) được **tái tính REPOSITORY-VERIFIED** — đưa ba `file_hash` Owner-reported
  vào ĐÚNG thuật toán `_dataset_hash()` (`src/eth_dca_os/data/dataset.py`, thứ tự
  `sorted(glob("*.parquet"))`: `BTCUSDT_1d`, `ETHUSDT_15m`, `ETHUSDT_1d`) cho kết quả khớp
  tuyệt đối với khai báo. Đây là bằng chứng NHẤT QUÁN THUẬT TOÁN — bốn con số (3 file_hash +
  1 dataset_hash) tự OK với nhau theo đúng mã đang chạy — **không** phải xác thực byte gốc:
  vẫn cần Owner-reported cho việc ba `file_hash` đó có thật là sha256 của dữ liệu Binance
  thật (repository không có byte để đối chiếu độc lập).

  (4) Pre-T06 manifest freeze và phép toán FS-12 (đã tái lập tại S018) được **dẫn chiếu lại**,
  không tính lại. 16/16 raw artifact SHA-256 Owner khai được ghi làm bảng trong evidence
  record — **không copy raw data vào git**, không bypass `.gitignore`.

  Validator: `branch_authority_check.sh` **PASS** (`production diff = EMPTY`),
  `validate_governance`/`validate_project_state`/`validate_structure`/`validate_routing`/
  `validate_evidence`/`validate_task_completion`/`validate_easy_roadmap` **PASS** (7/7).
  `sync_easy_roadmap.py` regenerate `LO_TRINH_DE_HIEU.md` **KHÔNG có diff** — xác nhận không
  roadmap/state nào bị đổi bởi phiên này.

  Không xử lý `H-13` hay hardening khác. Không tạo `docs/tasks/T-06-*.md`. Không ban hành
  Owner Decision — Owner đã báo dự kiến chọn hướng (B) mô tả trong prompt (ghi nhận T-06 thực
  thi trước khi phát hiện thiếu gate; không retrospective-freeze acceptance criteria; verdict
  giữ `DO_NOT_BUILD`) trong một phiên riêng, **chưa** ban hành ở đây. `OD-T06-01`…`OD-T06-10`
  từ S018 vẫn treo, chờ Owner. Biên bản đầy đủ:
  `docs/sessions/S019-t06-evidence-preservation.md`.
- S018 — POST-T06 EVIDENCE CLOSURE / GOVERNANCE BOOKKEEPING — 2026-09-03 — branch
  `claude/coindca-data-stream-vv0vwv` @ `5228130`. **Kết thúc ở `OWNER_DECISION_REQUIRED`**
  (hard-stop hợp lệ theo `AGENTS.md` §3). **KHÔNG state nào bị đổi**: `T-06` giữ `PLANNED`,
  `BLK-001` giữ ACTIVE trong sổ, không task ID mới, không work package mới, không repair cycle
  bị tiêu, `production diff = EMPTY`, không sửa `src/`/`tests/`.

  (1) **Kiểm chứng độc lập được (E1, tái lập tại HEAD `5228130`)** — `code_commit` khớp HEAD
  canonical và `origin`; `dependency_lock_hash` tái tính `sha256(pyproject.lock)` khớp
  `9ea0150fcf27…`; **pre-T06 manifest freeze tái lập CHÍNH XÁC cả 10 giá trị và cả 2 hash**
  (Gate 2: 19/1/18/200/219 + `e34f92ae…`; Gate 3: 14/100/114 + `ef30f657…`) — kiểm được vì
  manifest chỉ phụ thuộc mã + seed, không cần dataset và **không cần chạy lại `T-06`**; FS-12
  `net_advantage` tái tính khớp tới bit cuối (`-1.0935215802236702`, `share = 0.5806…` ⇒ FALSE).
  Bốn kết quả gate, FS-02/FS-10/FS-11, verdict `DO_NOT_BUILD` cùng đúng hai reason và
  `can_proceed_to_app=false` đều **nhất quán** với ngưỡng đã đóng băng trong
  `gates.py`/`verdict.py`/`failure_signals.py`.

  (2) **KHÔNG có finding nào làm mất hiệu lực official run.** Thêm một quan sát làm GIẢM rủi ro:
  `decide_verdict` vào nhánh `not gate1["pass"] or not oos["pass"]` **trước** khi đọc
  `fs["any_true"]`, nên khiếm khuyết `F-S015-01` (`numpy.bool_` vô hình với `v is True`)
  **không thể** đã ảnh hưởng verdict này — cờ FS chưa từng được hỏi tới, và chiều sai của nó là
  "để BUILD lọt qua" trong khi verdict thực tế là `DO_NOT_BUILD`. Thu hẹp phần dư `RSK-007` cho
  riêng run này, KHÔNG đóng `RSK-007`.

  (3) **Ba vật cản ĐỘC LẬP khiến `T-06` → `DONE` không thực hiện được ở phiên này** — đều là
  *thiếu gate / thiếu evidence trong repo*, KHÔNG phải *bằng chứng sai*:
  **(a)** `T-06` **không có file định nghĩa** ⇒ không Ready Gate, không frozen Completion Gate,
  không REQUIRED check nào (`task_registry_snapshot.sh`: 22 task file / 28 roadmap ID;
  `CHECK-T06*` → 0 kết quả). `TASK_MODE_STANDARD` Mode 2 đòi cả ba; `TASK_READY_GATE_STANDARD`
  cấm `PLANNED` → `IN_PROGRESS` và đòi Completion Gate **đóng băng trước khi thực thi** — official
  run đã chạy trước khi có gate để đóng băng. Viết acceptance criteria bây giờ, sau khi đã biết
  kết quả, đúng là thứ cơ chế freeze tồn tại để ngăn.
  **(b)** Artifact và evidence official **không nằm trong repository**: 5/5 record ID → 0 file,
  `dataset_hash` → 0 file, không `data/`/`results/`/`evidence/`. `results/` bị `.gitignore` nên
  artifact thô vắng mặt là hợp lệ, nhưng **không** có evidence record ở `docs/` hay `PROJECT/`.
  `EVIDENCE_STANDARD` cấm ghi PASS từ narrative; `STATE_AUTHORITY`: *"narrative does not move
  state"*.
  **(c)** Thẩm quyền: `STATE_AUTHORITY` ghi `DONE` = **Owner hoặc completion authority được chỉ
  định**; tiền lệ `WP-A1` → `DONE` đi qua `DEC-028`. Session prompt không phải Owner Decision và
  agent không được tự mint một cái.

  (4) **`DEC-003` / đối chiếu hai máy — KHÔNG làm invalid `T-06`.** Cái `DEC-003` bắt buộc là
  *chạy trên dữ liệu Binance thật*; phần hai máy là đường đi **được chấp nhận khi IP bị chặn**,
  tức quy trình cho tình huống **copy** dữ liệu (`docs/DATA_SOURCES.md` xác nhận khung đó). Owner
  khai fetch và run cùng trên máy production-realistic ⇒ không có bước copy để đối chiếu. Nó là
  **biện pháp đối trọng**, không phải acceptance criterion — và ở vai trò đó nó kích hoạt `H-06`.

  (5) **Hardening retrigger** (rà đủ 28 mục / 32 khối `RE_TRIGGER_CONDITION`; 15 mục có vế chạm
  `T-06`/official/dữ liệu thật/môi trường): **KÍCH HOẠT** — `H-13` vế 1 (**re-trigger BẮT BUỘC**:
  giới hạn `row_count` vẫn CHƯA công bố ở `docs/CONVENTIONS.md`, kiểm trực tiếp — file công bố
  giới hạn `source` và giới hạn độ phủ nhưng không công bố `row_count`; disposition (b) diff = 0
  nên KHÔNG tiêu repair cycle), `H-06` vế 1, `H-01` vế 1 (worktree có `?? data/` lúc chạy ⇒
  `git status --porcelain` không rỗng). **ĐIỀU KIỆN THOẢ, phép kiểm chứng ĐẾN HẠN nhưng chưa chạy
  được vì thiếu dataset/artifact** — `H-16` (nếu có ngày daily thiếu và một lệch ULP lật được
  ngưỡng ⇒ thành **BLOCKING**, về `CAP-DATA`), `H-24`, `H-25`, `H-27` vế 1, và vế "thao tác tay
  `lineage.json`" của `H-04`/`H-14` (quy trình vận hành `T-06` chưa bao giờ thành văn — `H-28`
  vế 2). **GIỮ HARDENING, không kích hoạt** — `H-02`, `H-03` (vế 2 không thoả vì
  `official_reason=verified`; vế 3 đã disposition tại `DEC-028`), `H-05`, `H-07`. Năm mục
  `H-01`/`H-06`/`H-13`/`H-16`/`H-27` được **ghi nhận** trong `HARDENING_BACKLOG.md` với **phân
  loại KHÔNG đổi**, chờ Owner disposition. **Không finding nào bị biến thành task.**

  (6) **Quan sát mới, KHÔNG phải task** — `pyproject.lock` chú thích `# Python: 3.11.15` trong khi
  official run khai Python `3.11.16`; `test_a1_08_*` bỏ qua dòng `#` nên không test nào bắt được.
  Không làm `dependency_lock_hash` sai (hash của chính file, đã kiểm khớp). Đề xuất route
  `CAP-PROV`, cùng lớp `H-02`. Và: `validate_evidence.py`/`validate_task_completion.py` báo
  `Checked 0` (`H-08`) — theo `STATE_AUTHORITY` § Vacuous Validation, **PASS của hai validator này
  không được đọc là xác nhận** evidence `T-06` đầy đủ.

  (7) **Trạng thái sau `T-06`**, đọc từ Ready Gate đã đóng băng: `WP-B1` **BLOCKED**
  (`Dependency T-06 DONE` chưa tick; `WP-A5 DONE` đã thoả), `WP-B2` **BLOCKED**, `WP-B3`
  **BLOCKED** (thêm `Dependency WP-C2 DONE`, mà `WP-C2` đang `BLOCKED` ⇒ `CHECK-B3-02` sẽ
  `BLOCKED`), **`GATE-B` CHƯA MỞ** (đòi cả ba `DONE`), `T-07` `PLANNED` bị chặn (đòi `T-06` ∧
  `GATE-B`), chặn tiếp `T-11`. Cả ba gói B bị chặn bởi **đúng một** mắt xích: `T-06`. Phiên này
  KHÔNG thực thi `WP-B1/B2/B3`.

  (8) **CẤP BÁCH** — `Master Index §6` **cấm chạy lại official run**, nên artifact official trên
  máy Owner (`data/` untracked + `results/` gitignored + `stash@{0} pre-T06-local-artifacts`) là
  **không thể thay thế**: mất chúng trước khi ghi vào repo thì `T-06` không bao giờ hợp thức hoá
  được, và cũng không được phép chạy lại để tạo lại. Phiên này không delete/stash/commit/drop bất
  cứ thứ gì.

  Validator: `branch_authority_check.sh` **PASS** (`INTEGRATION_DECISION_REQUIRED` đã xử lý tại
  `DEC-029`), `validate_governance` **PASS** (28 hardening, 22 task file), `validate_project_state`
  **PASS**, `validate_structure` **PASS** (27 path), `validate_routing` **PASS** (19 MAJOR, 0
  override), `validate_easy_roadmap` **PASS**, `validate_evidence`/`validate_task_completion`
  **PASS nhưng RỖNG**. Test suite `NOT_TESTED` (container thiếu `pandas`/`pyarrow`/`pytest`; chỉ
  cài `numpy==2.4.6` đúng pin lockfile để tái lập manifest hash).

  Mười quyết định chờ Owner (`OD-T06-01`…`OD-T06-10`), ưu tiên: **`OD-T06-01`** bảo toàn
  artifact ngay; **`OD-T06-02`** cơ chế đưa evidence vào repo (`results/` đang bị gitignore);
  **`OD-T06-03`** hợp thức hoá gate cho `T-06` — đường (A) tạo file task + Completion Gate viết
  **từ tiêu chí đã đóng băng ở `T-04`/BT §7–§10** rồi Owner đóng băng, hoặc đường (B) Owner ghi
  `DEC-0xx` dispositioning tường minh sự vắng mặt của gate (kiểu
  `LEGACY_GATE_COMPATIBILITY_REQUIRED`); **`OD-T06-04`** thi hành `H-13` (docs-only, diff = 0).
  Agent KHÔNG được tự chọn giữa (A) và (B).
  Biên bản đầy đủ: `docs/sessions/S018-post-t06-evidence-closure.md`.
- T-09B (OWNER CONFIRMATION — `DEC-024`) — 2026-09-03 — cùng branch
  `claude/t09b-firebase-implementation-nz50is` @ HEAD `4e80522`. Chủ dự án xác nhận tường minh
  chấp nhận toàn bộ evidence production (CHECK-01/02/03/04/14 PASS, E1, Owner tự báo cáo — không
  phải E2 độc lập, chấp nhận rõ mức này) và ra quyết định `DEC-024` (`OD-WEBAPP-07`):
  `T-09B: IMPLEMENTED → DONE`. `RSK-001` ghi nhận phần V1 durable persistence đã kiểm chứng trên
  production, KHÔNG tuyên bố đóng hẳn; `H-23` tiếp tục HARDENING/OUT OF SCOPE V1 theo `DEC-021`,
  không đổi, không mở task mới từ risk này. `ELIGIBLE_FOR_INTEGRATION = NO` giữ nguyên theo
  `DEC-022` — không merge `main` trong bước này. Cập nhật: `docs/tasks/T-09B-*.md` (Status →
  `DONE`), `PROJECT/PROJECT_PROGRESS.md` (roadmap row → `DONE`, Current Task, RSK-001),
  `PROJECT/CAPABILITY_REGISTRY.md` §11, `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.5 (budget 2/0/2
  không đổi). Sau đó hướng dẫn Owner dọn dữ liệu synthetic bằng workflow hiện có ("Xoá toàn bộ
  dữ liệu", tab Thiết lập) trước khi nạp dữ liệu thật. Không mở task mới.
- T-09B (PRODUCTION VERIFICATION — tiếp nối) — 2026-09-03 — cùng branch
  `claude/t09b-firebase-implementation-nz50is` @ HEAD `7f5dc94`. Chủ dự án báo đã deploy Hosting
  thật + rules đã merge với Owner UID thật, mở app bằng trình duyệt hằng ngày. Agent thiết kế quy
  trình verification tối thiểu bằng dữ liệu synthetic (không dùng dữ liệu tài chính thật), đưa
  hướng dẫn từng bước + expected result trước khi Owner thao tác. Lần thử đầu bị chặn ở P2P
  ("Không đủ VND trong kho") — phân tích code (`addP2P`/`addContribution`) xác nhận đây là
  accounting guard đúng (P2P cần treasury.vnd đã nạp qua contribution trước), sửa quy trình
  (thêm bước "Nạp vốn tháng"), không sửa code. Owner chạy lại, báo PASS toàn bộ: CHECK-01 (rev
  1→4 khớp dự đoán), CHECK-02+04 (đóng/mở lại trình duyệt, state+lịch sử nguyên vẹn), CHECK-03
  (xoá localStorage/sessionStorage, phục hồi từ Firestore), CHECK-14 (chuỗi hằng ngày trọn vẹn
  qua trình duyệt). Cập nhật `docs/tasks/T-09B-*.md` (5 CHECK + Status + Exit Criteria #1),
  `docs/reviews/T-09B-production-verification.md` (mới, evidence đầy đủ + giới hạn trung thực),
  `RSK-001` (giảm đáng kể trên thực tế cho scope V1). Không phát hiện defect. Không mở
  hardening/task mới. `T-09B` vẫn `IMPLEMENTED` — `ELIGIBLE_FOR_COMPLETION` là khuyến nghị,
  chuyển `DONE` chờ xác nhận tường minh của chủ dự án.
- T-09B (SHARED FIREBASE PROJECT / RULES SAFE MERGE — tiếp nối) — 2026-09-02 — cùng branch
  `claude/t09b-firebase-implementation-nz50is` @ HEAD `f9330eb`. Owner xác nhận project thật
  (`tinphatcontent`) dùng chung với ứng dụng Content, cung cấp nguyên văn rules Content đang
  chạy. Phân tích: không có collection nào tên `ethdca`, không có catch-all sẵn có — merge an
  toàn bằng cách CHỈ thêm hai khối `match /ethdca/state`/`match /ethdca/seed` (hàm đổi tên
  `isCoinDcaOwner()`), không đụng bất kỳ match/function nào của Content. Dựng
  `webapp/test_shared_rules_merge.js` trên `test_firebase_harness.js` đã có: battery 53 probe
  Content (đọc từ chính rules text, phủ cả 8 collection — vượt yêu cầu tối thiểu `audit_logs`/
  `config`/`users`) chạy trên Firestore Rules Emulator, so BEFORE (rules Content nguyên văn) ==
  AFTER (đã merge) — **0 lệch**, cả 53 probe khớp đúng phân tích rules text. Ma trận CoinDCA 12
  ca (§8 chỉ thị) PASS 12/12, gồm xác nhận owner UID KHÔNG có thêm quyền Content nào ngoài đúng
  mức "signedIn thường" mà Content vốn đã cấp cho MỌI actor. `DEC-023` ghi quyết định + Hosting
  RESOLVED (Owner tự kiểm Console: chưa setup, dùng site mặc định). CHƯA deploy — chờ owner UID
  thật. Evidence: `docs/reviews/T-09B-shared-rules-merge.md`.
- T-09B (REAL FIREBASE SETUP — tiếp nối S014) — 2026-09-02 — cùng branch
  `claude/t09b-firebase-implementation-nz50is` @ HEAD `7f78c14`. Mục tiêu: thiết lập Firebase
  project thật + xác minh production reachability. Bước đầu gặp
  `INTEGRATION_DECISION_REQUIRED: loc>5000` (branch authority check) → chủ dự án ACCEPT THE
  DIVERGENCE (`DEC-022`, không merge, không cut scope). Kiểm tra thẩm quyền Firebase CLI:
  `firebase login:list` → "No authorized accounts" — môi trường agent KHÔNG có Firebase
  Console/CLI authority (không trình duyệt, không credential). Theo đúng chỉ thị phiên §3: DỪNG
  ở bước đầu tiên cần Owner thao tác, không tự invent project ID/config/UID. Xem yêu cầu gửi chủ
  dự án ở cuối báo cáo phiên này.
- T-09B (IMPLEMENTATION — S014) — 2026-09-02 — branch `claude/t09b-firebase-implementation-nz50is`
  từ `origin/main` @ `4502ea6`. **IMPLEMENTED** — 16/16 REQUIRED check PASS (E1), toàn bộ qua đường
  sản phẩm (trang build thật → Firebase SDK compat 12.18.0 thật → Firebase Emulator Suite Auth +
  Firestore với đúng `firestore.rules` của repo → nạp lại), bằng chứng phía Firebase đọc độc lập qua
  REST của emulator.
  (1) **Kiến trúc đúng baseline FROZEN**, không thêm thành phần: Hosting (`firebase.json`) · Anonymous
  Auth · Firestore `ethdca/state` + `ethdca/seed` · rules khoá cứng một owner UID (placeholder
  `OWNER_UID_REQUIRED` = mặc định deny), không delete. `localStorage` = mirror/cache.
  (2) **Production diff theo khai báo**: 3 file, +560 / −162 (`app_logic.js` khối persistence/init/
  banner/guard/export-import-wipe; `app_shell.html`; `build_app.js` bỏ nhúng state/quine) + 3 file
  runtime mới chưa trong khai báo (`webapp/firebase_config.js`, `firestore.rules`, `firebase.json` —
  `H-32`). `engine.js`, `src/eth_dca_os/**`, `pyproject.*` = **0 dòng**. Không hàm kế toán nào bị chạm.
  (3) **Test**: `test_firebase_harness.js` (mới) + `test_t09b_persistence.js` (mới, 285 assertion /
  0 FAIL, 14 check trực tiếp); `test_helpers.readState()` đọc bản durable + đối chiếu bit-exact →
  ba test kế toán T-09A chạy nguyên văn trên state đã round-trip (CHECK-09: 68/68; V-01/V-02/V-03
  BÁC BỎ). `npm --prefix webapp test` **6/6 exit 0**.
  (4) **Batch review bắt buộc** → **PASS, 0 CONFIRMED BLOCKING còn lại**: `F-T09B-01` (hai tab cùng
  profile, tab stale ghi đè bản mới hơn — mất dữ liệu âm thầm) phát hiện trong phiên và sửa TRƯỚC
  commit bằng transaction có điều kiện `rev` (cùng lượt, không repair cycle); 4 HARDENING `H-29`
  (trần 1 MiB/document), `H-30` (stale change chỉ trong bộ nhớ tab), `H-31` (`validateState` giả
  định tổng tỷ lệ = 1), `H-32` (ba file runtime mới chưa khai production path). Biên bản:
  `docs/reviews/T-09B-batch-review.md`.
  (5) **Giới hạn bằng chứng (chỉ thị §14)**: project Firebase thật CHƯA tồn tại; emulator không suy
  ra production reachability. CODE IMPLEMENTATION COMPLETE · REAL FIREBASE SETUP REQUIRED · real
  deploy = KHÔNG. Chủ dự án làm 5 bước ở `webapp/README.md` rồi lặp lại CHECK-01/02/03/04/14 bằng
  tay trên app thật trước khi `DONE`.
  (6) Budget `CAP-WEBAPP` 2/0/2 **không đổi** (implementation ban đầu). Task ID mới = 0 (29 = 29 theo danh sách trạng thái đầy đủ; `task_registry_snapshot.sh` báo 28 → 27 vì bỏ sót `IMPLEMENTED` — `H-22`).
  `H-19`, `H-20`, `H-23` không đổi. Không sửa Product Principle, không mở lại quyết định kiến trúc.
  Handoff: `docs/sessions/S014-t09b-firebase-implementation.md`.
- T-09A (REPAIR V-01/V-02) — 2026-09-02 — branch `claude/t09a-accounting-repair-v4ewhq` từ
  `origin/main` @ `814d185`. **IMPLEMENTED** — 12/12 REQUIRED check PASS (E1), toàn bộ bằng
  chứng chạy thật qua đường sản phẩm (UI → `app_logic` → `engine` → state), không gọi trực
  tiếp hàm engine.
  (1) **Test trước, vá sau.** Chạy lại reproduction WP-C1 trên `origin/main` @ `814d185`:
  `BEFORE V-01 = XÁC NHẬN`, `BEFORE V-02 = XÁC NHẬN`. Dựng
  `webapp/test_t09a_accounting.js` (68 assertion, sáu bất biến A–F) và chứng minh nó **FAIL 17
  assertion trên cây chưa vá** trước khi sửa một dòng production nào.
  (2) **Root cause V-01**: ladder không mang tháng kế toán sở hữu vốn; `releaseLadder()` **và**
  `poolFor()` trong `addBuy()` đều dùng `currentMonth()` (key tháng lớn nhất) làm pool đích.
  Sửa: `L.month` ghi tường minh ngay tại lúc reserve; release và deploy đều quay về đúng pool
  đó. Ladder tạo trước bản vá được suy luận tháng từ `L.created` và **được báo hiện bằng
  banner** — không migrate, không ghi đè state.
  (3) **Root cause V-02**: `reserveFor()` chỉ so với available, không tham chiếu unlock. Sửa:
  `smartReservable()`/`oppReservable()` dùng đúng công thức của `capital.py::smart_reservable`
  (unlocked(tháng) − đã reserve − đã deploy trong tháng, kẹp trên bởi available), fail closed
  khi chưa có `view`.
  (4) Bút toán `RELEASE` nay ghi số **thực sự dịch chuyển** (trước ghi số cam kết) và đánh dấu
  `LADDER_RELEASE_SHORTFALL` khi hai số lệch nhau.
  (5) `AFTER V-01 = BÁC BỎ`, `AFTER V-02 = BÁC BỎ` (reproduction gốc của WP-C1, không sửa logic
  kết luận). `test_t09a_accounting.js` **0 FAIL / 68**. `npm --prefix webapp test` 5/5 exit 0.
  `python3 -m pytest -q` **286 passed, exit 0**.
  (6) Diff production theo KHAI BÁO: **1 file, +88 / −16** (`webapp/app_logic.js`).
  `webapp/engine.js`, `src/eth_dca_os/**`, `pyproject.*` = **0 dòng đổi**.
  (7) **Batch review bắt buộc** (Effective Risk HIGH) → **PASS, 0 CONFIRMED BLOCKING**,
  `ELIGIBLE_FOR_FREEZE` (advisory). 4 HARDENING mới: `H-19` (`monthKey()` dùng giờ địa phương),
  `H-20` (đường mua trực tiếp không bị giới hạn unlock), `H-21` (lệnh đo budget trong
  `PRODUCTION_PATHS.md` §1 nuốt file test mà §2 loại trừ), `H-22`
  (`task_registry_snapshot.sh` bỏ sót `IMPLEMENTED`/`VERIFYING` — khiếm khuyết CÓ TRƯỚC phiên
  này, `T-03` đã vắng mặt trong ảnh chụp từ trước). 1 `OUT_OF_SCOPE` → `WP-C4`
  (`F-T09A-03`: thiếu HWM §6 / hysteresis §5 / daily limit §11 — lệch theo chiều CHẶT HƠN).
  Biên bản: `docs/reviews/T-09A-batch-review.md`.
  (8) `H-18` / V-03: **giữ nguyên DEFERRED**, không re-trigger.
  (9) Budget `CAP-WEBAPP`: allowed 2 (default V4.3 theo Effective Risk HIGH — chủ dự án CHƯA
  đặt con số tường minh) / used **0** / remaining 2. Lượt `814d185..d125fe5` là implementation
  ban đầu, không phải repair cycle. Ledger §2.2 mới khởi lập.
  (10) **Task ID mới = 0.** `docs/tasks/T-09A-sua-loi-ke-toan-app-web.md` là Task Spec cho ID
  **đã đăng ký sẵn** trong registry (`CAPABILITY_MODEL.md` §II.5 hình thức 1). Registry đo lại
  bằng tay với danh sách trạng thái ĐẦY ĐỦ: **BEFORE 29 → AFTER 29 task ID, diff RỖNG**; file
  task 20 → 21. (`task_registry_snapshot.sh` báo 28 → 27 vì nó bỏ sót `IMPLEMENTED` và
  `VERIFYING` — `H-22`, khiếm khuyết có trước phiên này.)
  (11) KHÔNG đụng: `WP-A4` (`DONE`), `F-S009-01` (`CLOSED`), `CAP-DATA` (allowed 2 / used 1 /
  remaining 1), `F-S010-03` (`OUT_OF_SCOPE` → `WP-C4`). KHÔNG mở dashboard, `WP-C2`, `WP-A6`,
  KHÔNG chạy `T-06`.
  (12) **Escalation "dừng dùng app với tiền thật" được GỠ** — xem `RSK-003`. Cảnh báo còn lại:
  state đã lưu TRƯỚC bản vá có thể đã sai sẵn; bản vá không sửa lịch sử.
- WP-C1 (STREAM WEB) — 2026-09-02 — branch `claude/wp-c1-web-skeleton-b3oieq` từ `origin/main`
  @ `cb75f9d`. **DONE** — 8/8 REQUIRED check PASS (E1), evidence chạy thật, không đọc code suông.
  (1) F-027 đóng: harness khôi phục từ bản checkout sạch — `webapp/package.json` mới (ghim
  `playwright@1.56.1`), `webapp/build_app.js` + `webapp/test_app.js` + `webapp/test_zone.js`
  chuyển path tương đối theo `__dirname` (trước đó phụ thuộc `process.cwd()`, gãy khi gọi từ
  gốc repo — chính là root cause của F-027 đúng như tên gọi). `demo/results3/live_seed.json`
  sinh bằng `ethdca synth` + `ethdca export-live` (DEMO/SYNTHETIC, không phải Binance thật).
  Ảnh chụp màn hình test (`app-dash.png`, `app-zone.png`) và `app_final.html` thêm vào
  `.gitignore`. (2) Ba nghi vấn kết luận E1 bằng hai test mới —
  `webapp/test_v01_v02_v03.js`, `webapp/test_multi_month_invariant.js`: **V-01 XÁC NHẬN**
  (release đa tháng trả nhầm pool VÀ/HOẶC kẹt vốn vĩnh viễn, tái hiện cả qua Hủy thủ công lẫn
  invalidation tự động), **V-02 XÁC NHẬN** (reserve không bị giới hạn theo unlock — reserve
  100% available dù unlock đo được = 0%), **V-03 BÁC BỎ** (INVALID luôn trùng với ADR30 NaN
  theo toán học của `engine.js` nên `createLadder()` vẫn bị chặn trong mọi trạng thái quan sát
  được — nhưng KHÔNG do một kiểm tra `data_quality` tường minh; ghi HARDENING). (3) `git diff`
  xác nhận `webapp/app_logic.js` và `webapp/engine.js` không đổi một dòng nào (CHECK-C1-07).
  (4) Cập nhật: `RSK-003` (mức trung bình → **CAO**, escalation NV-1/NV-2 = lỗi thật), `RSK-004`
  (RESOLVED), `T-03` `CHECK-03-01` `BLOCKED` → `PASS`, `Status` `BLOCKED` → `VERIFYING`
  (KHÔNG tự đóng `DONE` — ngoài scope WP-C1), `T-09A` `PLANNED` → `READY` với phạm vi xác định
  (sửa `releaseLadder()` dùng đúng tháng gốc của ladder; `reserveFor()`/`createLadder()` phải
  nhân giới hạn unlock). (5) 0 task ID mới tạo, 0 WP mới mở, không mở WP-C2/C3/C4/UI polish/
  auth/mobile/chart task. (6) DATA stream dependency = **KHÔNG** — không chạm
  `src/eth_dca_os/**`, không pull/cherry-pick branch DATA. (7) **Escalation kích hoạt**: V-01 và
  V-02 là lỗi thật — nếu app đang ghi tiền thật, dừng dùng hoặc xuất dữ liệu ra ngoài cho tới
  khi T-09A vá xong.
- Integration (DEC-013) — 2026-09-01 — **governance-only**, integration SHA `febc2ec`.
  KHÔNG sửa production code, KHÔNG sửa test code, KHÔNG mở WP, KHÔNG mở repair cycle,
  KHÔNG tạo task ID, KHÔNG chạy T-06. Kết quả:
  (1) `DEC-013` **RESOLVED / INTEGRATED** theo phương án **A — INTEGRATE NOW**; canonical
  trunk từ đây = **`main`**.
  (2) Đo lại toàn bộ bằng git ngay trước merge: source `claude/wp-a1-provenance-v67k9h` @
  `6372783`; default cũ `claude/plan-tool-from-docs-qijx5m` @ `4a46b3c` (giải bằng GitHub
  API `default_branch`, KHÔNG giả định); merge base `e368425`; ahead 33 / behind 1.
  Chứng minh commit "behind" duy nhất không mang nội dung: `4a46b3c` là merge commit có
  **cả hai parent** (`aef0220`, `e368425`) là ancestor của source, và
  `tree(4a46b3c) = tree(e368425) = 57e0876`, `git diff e368425 4a46b3c` **RỖNG**.
  (3) Tích hợp bằng **merge commit thường** (`--no-ff`), KHÔNG rebase / squash /
  cherry-pick / rewrite history. `MERGE CONFLICTS = 0`;
  source tree `633b4c3` == main result tree `633b4c3` → **TREE IDENTICAL = YES**;
  `git diff febc2ec 6372783` RỖNG → **CONTENT LOST = 0**.
  (4) Cả 11 SHA baseline/evidence quy chiếu vẫn là ancestor của `main`, gồm hai neo ledger
  `666de14` (CAP-PROV) và `06b381c` (CAP-DATA). Baseline SHA KHÔNG đổi, budget KHÔNG reset,
  WP state KHÔNG đổi.
  (5) Ghi nhận (KHÔNG thi hành) hai quyết định của chủ dự án cho phiên sau: `DEC-016`
  (`OD-DATA-01`) và `DEC-017` (`OD-DATA-02`).
  (6) Validators trên `main`: `validate_governance` **PASS** · `validate_project_state`
  **PASS** · `validate_structure` **PASS** (27 path) · `validate_routing` **PASS** (17 MAJOR
  task file) · `validate_easy_roadmap` **PASS** · `sync_easy_roadmap` PASS, file sinh ra
  KHÔNG đổi (không có status/Tier/Effort nào thay đổi).
  `branch_authority_check.sh --expect-branch main` báo **FAIL** — ghi đúng như nó là, và
  **hai nguyên nhân đều KHÔNG phải khiếm khuyết tích hợp**:
  (a) script hard-code `case main|master` = "feature work must not commit to the default
  branch" (dòng 66–70). Đây là quy tắc bảo vệ trunk, đúng theo thiết kế, và chính là hành vi
  mong muốn từ đây trở đi: phiên sau phải branch từ `origin/main` chứ không commit thẳng lên
  `main`. Phiên Integration buộc phải commit lên trunk vì việc của nó LÀ lập trunk.
  (b) `INTEGRATION_DECISION_REQUIRED: ahead of default 35` — script giải default branch từ
  remote và remote vẫn đang trỏ vào `claude/plan-tool-from-docs-qijx5m`. Con số này về 0 ngay
  khi chủ dự án đổi GitHub default branch sang `main`
  (`REMOTE_DEFAULT_SWITCH_REQUIRED = YES`). Không có cách nào đóng nó từ phía git.
  `production diff = EMPTY` và `tracked worktree = CLEAN` trong cùng lần chạy đó.
  KHÔNG chạy lại chiến dịch verification lớn: tree kết quả TRÙNG KHÍT tree source, nên phép
  tích hợp không đổi working tree và không có gì để regression lại. Không tạo report mới:
  bằng chứng và số đo đầy đủ nằm trong `PROJECT/PROJECT_DECISIONS.md` § `DEC-013`.
  (7) `WP-C1` giữ nguyên `PARALLEL_READY = YES`, KHÔNG mở trong phiên này.
- Integration Recheck / Owner Disposition — 2026-09-01 — **governance-only**, HEAD
  `07bb241`. KHÔNG sửa production code, KHÔNG sửa test code, KHÔNG mở WP, KHÔNG mở repair
  cycle, KHÔNG tạo task ID, KHÔNG merge. Kết quả:
  (1) `DEC-015` — `F-S009-01` → owner `CAP-DATA`, verdict `IMPLEMENTATION_DEFECT`,
  `OWNER_ASSIGNMENT_REQUIRED` ĐÓNG; bốn ngưỡng Absorption Limit đều KHÔNG chạm; còn lại đúng
  MỘT `OWNER_DECISION_REQUIRED` về phương tiện thi hành (`WP-A4` đang DONE + gate FROZEN +
  `indicators.py` ngoài touch area — ba rào đều thuộc thẩm quyền chủ dự án).
  (2) Bằng chứng E1 tái lập độc lập trên chính hàm production `compute_daily_indicators`,
  môi trường trùng khớp `pyproject.lock` (Python 3.11.15 / numpy 2.4.6 / pandas 3.0.5):
  một ngày lịch thiếu làm `return7` **đổi dấu** (+0,0187 → −0,0365; lệch 295%) và làm sai
  thêm `ethbtc_return30`, `adr30`, `rsi14` — **không cái nào NaN**. Cơ chế: `score.py::
  invalid_mask` chỉ bắt giá trị KHÔNG HỮU HẠN, mà cửa sổ theo vị trí luôn sinh số hữu hạn
  nhưng sai, nên nhánh DEGRADED/INVALID mà BT §18 bắt buộc không bao giờ chạy.
  (3) `DEC-013` đo lại toàn bộ bằng git (số cũ tại `d63c222` đã hết giá trị): default branch
  giải được là `claude/plan-tool-from-docs-qijx5m` (remote KHÔNG có `main`); ahead 32 /
  behind 1 / age 9 ngày; total 95 files +27857/−372; production 15 files +940/−145; test 11
  files +3150; governance/doc 69 files +23767/−227. `merge-tree` → **0 xung đột**, tree kết
  quả `605b621` **trùng khít** tree của HEAD; nội dung thiếu ở branch hiện tại = **0**; ở
  default = 95 file. Mọi baseline SHA (`666de14`, `06b381c`, `85fa30f`, `d63c222`, `e368425`)
  đều còn là tổ tiên của HEAD. Khuyến nghị giữ **phương án A**; C bị loại vì phá neo baseline
  của ledger mà lợi ích đúng bằng 0.
  (4) Ledger đối chiếu khớp git; `CAP-DATA` used = 0 (lượt đầu là implementation, không phải
  repair cycle), `ALLOWED` vẫn CHƯA LƯỢNG HOÁ (gốc: `H-10`). `CAP-PROV` 2/2/0 không đổi.
  (5) `WP-C1` xác nhận lại read-only: `PARALLEL_READY = YES`.
- S009 — WP-A4 — 2026-09-01 — **DONE.** Ngữ nghĩa dữ liệu thiếu/hỏng + độ phủ theo khoảng
  ĐƯỢC YÊU CẦU. 9/9 REQUIRED check PASS (232/232 test suite PASS): chín check FROZEN
  2026-08-23 giữ nguyên câu chữ,
  cộng đúng MỘT check `CHECK-A4-10` do chủ dự án phê duyệt TRƯỚC khi implementation
  (`DEC-014` / `OD-A4-01`). Đóng **F-023** (định nghĩa INVALID hẹp hơn ST §3 — nay INVALID
  khi giá/lịch sử ETH **hoặc** một indicator bắt buộc `close`/`return7`/`adr30` hỏng, quy
  ước ghi ở `docs/CONVENTIONS.md`), **F-025** (`EXECUTION_DATA_GAP` nay là tag TRÊN BẢN GHI
  kèm `missing_candles_before`), **F-032** (`DELAYED_DATA_FILL` nay là tag, không chỉ bộ
  đếm), và **F-E2A1R3-05** (fetch cắt cụt vẫn đủ tư cách official).
  Root cause của F-E2A1R3-05: `gap_report` neo số nến kỳ vọng vào khoảng QUAN SÁT ĐƯỢC nên
  phần thiếu ở hai đầu vô hình; `official_eligibility` không có khái niệm "khoảng đã được
  yêu cầu". Sửa tối thiểu: khai `requested_range` tại nơi sản xuất dataset (`fetch_all`,
  `synth.generate`) → ghi vào `lineage.json` → cổng đọc. KHÔNG redesign fetch, KHÔNG đổi
  chữ ký `official_eligibility(raw_dir, lineage)`, KHÔNG đổi `dataset_hash`.
  BEFORE: yêu cầu 2020-01-01…2021-01-01, archive chỉ có tới 2020-01, REST bị chặn →
  31/366 ngày (8,5%), `missing_count = 0`, `official_eligibility -> (True,'verified')`.
  AFTER: `missing_count = 335`, `(False, 'incomplete_coverage:ETHUSDT_1d=31/366 head=0
  internal=0 tail=335')`, `Prepared.official_eligible = False`. CASE A–F đều đúng kỳ vọng.
  Định lượng trên dataset có gap (cùng seed, BEFORE=`06b381c`): INVALID 0 → 37 ngày,
  action 17 → 13, `eth_total` −0,19%, nominal BASE 600.0 → 600.0 (Base không bao giờ bị bỏ),
  bản ghi mang tag 0 → 3. Trên dataset sạch: trùng khớp từng chữ số, không drift nền.
  Phát hiện mới NGOÀI gate: **`F-S009-01`** — CONFIRMED BLOCKING,
  `OWNER_ASSIGNMENT_REQUIRED` — indicator daily tính theo VỊ TRÍ, không theo LỊCH; một ngày
  daily thiếu làm `return7` sai 14,29% mà không NaN/DEGRADED/INVALID, và dataset vẫn qua
  cổng official (0,27% < ngưỡng 1%). KHÔNG làm FAIL check nào của WP-A4; phải đóng trước
  T-06. Hardening mới: **H-14**, **H-15**.
  Không tạo task ID mới. Không mở repair cycle WP-A1. Không đụng budget `CAP-PROV`. Không
  chạm `regime.py`/`ladders.py`/`capital.py`/`verdict.py`/`failure_signals.py`/`webapp/`/
  `docs/spec/`. Không merge default branch. Không mở WP-C1/WP-A5/WP-A6, không chạy T-06.
  Tài liệu: `docs/sessions/S009-wp-a4-ngu-nghia-du-lieu-xau.md`,
  `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md`.
- S006 — WP-A2 — 2026-08-24 — **DONE.** Đấu nối các hạng mục đã viết nhưng pipeline chưa
  gọi (đóng **F-003, F-004, F-012, F-013, F-014**; RSK-007 giảm thiểu một phần). Routing
  xác nhận lại: router trả **Tier C tự nhiên**, không qua override — MICRO-GOVDEF-001 không
  hồi quy. Ready Gate 13/13 → baseline BEFORE tái hiện đủ 5 finding với phân biệt
  A/B/C/D/E (code tồn tại / có test / pipeline gọi / output chứa / downstream dùng) →
  test-first 9 test wiring (8 FAIL + 1 PASS đúng kỳ vọng: hàm `xirr` vốn đã đúng) →
  remediation THUẦN ĐẤU NỐI trong `pipeline.py` + `diagnostics.py` (+1 dòng `cli.py`
  truyền `dev_limit`, đã khai báo ranh giới scope) → 9/9 PASS → **CHECK-A2-08: 4 module
  chỉ-đọc (`benchmarks/metrics/windows/bootstrap`) 0 dòng đổi** → **CHECK-A2-09: 159
  trường metric của chiến lược + Benchmark A, 0 khác biệt** (đo qua worktree, assert
  provenance) → full regression PASS → Completion Gate 10/10. Payload official nay có
  `benchmarks` A–D, `diagnostics.ablation` (3 model), `volume_zscore_variant` + bảng
  chênh lệch, `coverage_table`, `xirr`, và bootstrap **1000/block length** (spy đo trực
  tiếp 200→1000). Không finding/risk mới. Artifact:
  `docs/sessions/S006-wp-a2-pipeline-wiring.md`, `tests/test_wp_a2_pipeline_wiring.py`.
- S005 — WP-D1 — 2026-08-24 — **DONE.** Dọn 4 khoản nợ kỹ thuật không ảnh hưởng hành vi
  (đóng **F-028, F-029, F-031, F-034**). Ready Gate 12/12 xác nhận lại (routing B/Sonnet/
  medium khớp roadmap) → baseline E0/E1 tái hiện đủ 4 finding tại 1f4c2b7 → kiểm tra rủi
  ro hành vi bắt buộc (không finding nào chạm OSCORE/ladder/capital/execution/backtest/
  gate/verdict — không escalation) → test-first 4 test (4 FAIL đúng cách) → remediation
  tối thiểu: `expires_at` Smart ladder đúng cuối accounting month (engine.py), bỏ
  PARTIALLY_FILLED khỏi `ladder_completed()` (ladders.py), `cooldown_override` đếm theo
  sự kiện thay vì zone (engine.py), xoá dead code `_noon_candles` (benchmarks.py) → 4/4
  PASS → toàn suite **99/99 PASS** → impact BEFORE/AFTER cùng dataset: **543 purchase
  record trùng khớp bit-for-bit**, chỉ `cooldown_override` đổi (35→31 sự kiện, đúng
  ngoại lệ khai báo) → Completion Gate 6/6 PASS. Không finding/risk mới. Artifact:
  `docs/sessions/S005-wp-d1-debt-cleanup.md`, `tests/test_wp_d1_debt_cleanup.py`.
- S004 — WP-A7 — 2026-08-24 — **DONE.** Sửa phạm vi kế toán vốn Smart theo accounting
  month (đóng **F-035**, CLOSED **RSK-010**). Ready Gate 20/20 xác nhận lại → baseline
  BEFORE tái hiện root cause tại 68bd8be (tháng 2+ reservable=0 ở unlock 1.0; 2 ladder/
  90 tháng; 3 mode trùng bit-for-bit) → test-first A–G (7 FAIL đúng cách + 1 guard PASS)
  → PA-A: bộ đếm tháng trong `Pool` + `open_accounting_month`, carry-first cho reserve
  vắt tháng, MỘT hook engine tại rollover (BT §19 bước 3→5); ledger lifetime +
  `opportunity_reservable` không đổi (CONVENTIONS #17) → 8/8 + 34/34 + toàn suite
  **95/95 PASS** → impact cùng dataset: ladder 2→67, Smart qua ladder 0.0208%→24.49%,
  [F5] 111.13→492.07, BASE/regime bất biến, mọi dòng truy về spec → E2 độc lập
  **PASS WITH FOLLOW-UPS** (5/5 nội dung, probe tự dựng, over-grant = 0; follow-up
  trong thẩm quyền thực hiện ngay: F-E2A7-02 → CONVENTIONS #17) → Completion Gate
  12/12 PASS. Phát hiện mới ngoài scope: **PH-04** (+ tinh chỉnh F-E2A7-03) chờ chủ
  dự án. Artifact: `docs/sessions/S004-wp-a7-monthly-smart-scope.md`,
  `docs/reviews/E2-WP-A7-monthly-smart-scope.md`, `tests/test_wp_a7_monthly_scope.py`.
- WP-A7 — TASK DEFINITION & GATE FREEZE — 2026-08-24 — Soạn và **đóng băng** task definition cho
  WP-A7 theo `TASK_DEFINITION_TEMPLATE.md`: `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md`.
  **20 mục Ready Gate** (19 đã xác nhận, 1 để xác nhận lại khi mở task) và **12 REQUIRED
  Completion check** — E1 toàn bộ, **E2 bắt buộc** cho CHECK-A7-12 (Risk 4 + `accounting_financial`).
  Kiểm precedence Master Index §2 trên bốn tầng tài liệu: **không phát hiện CONFLICT** — BT §19
  (precedence 1) bước 3/4/6 nói "đóng sổ cuối tháng", "reset trạng thái Smart HWM/mode", "overflow
  sang **Smart của tháng đó**", cùng hướng với DM §5 (`monthly_budgets` keyed by `month_local`) và
  ST §4/§6/§10/§12; DM §6 (`capital_ledger` append-only, audit) là căn cứ bắt buộc **giữ lịch sử
  toàn đời** song song với trạng thái theo tháng. Root cause được giữ nguyên văn (tử số theo tháng
  trừ `pool.deployed` cumulative lifetime), kèm lệnh cấm diễn giải lại finding thành "cần tăng số
  ladder". Routing xác nhận lại bằng router: **D / Fable / max**; `validate_routing.py` PASS trên
  **17** MAJOR task file. Coverage regression: 22/22 requirement của RCP-002 có mặt trong gate,
  không dependency nào bị làm yếu (A7 → A5/A6/C4/GATE-A/T-06 giữ nguyên). **WP-A7: PLANNED →
  READY.** Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`; không remediation F-035; không bắt
  đầu WP nào.
- RCP-002 — ROADMAP CHANGE APPLIED — 2026-08-24 — Chủ dự án phê duyệt RCP-002 kèm điều kiện bổ
  sung. Áp dụng vào bảng roadmap chuẩn: **28 → 29 task**. Thêm **WP-A7** ("Sửa phạm vi kế toán vốn
  Smart theo tháng", lớp A, sở hữu **F-035**, status `PLANNED`, routing **D/Fable/max** xác nhận
  lại bằng `routing_engine.py` tại thời điểm áp dụng: model_score 3.25, effort_score 3.45,
  floors `cognitive:A>=3&X>=3` + `safety_business:min_C` + `safety_business:min_high`). Dependency
  bắt buộc: WP-A7 là prerequisite của **WP-A5, WP-A6, WP-C4, GATE-A, T-06**; WP-A6 không được chạy
  Completion Gate cuối trước khi WP-A7 DONE; WP-A5 measurement trước F-035 không phải canonical
  evidence; WP-C4 không đóng băng parity trên hành vi Smart capital sai. **GATE-A** định nghĩa lại
  = WP-A1…WP-A7 đều DONE. **T-06** ghi rõ hai nhóm prerequisite độc lập (nội tại GATE-A / hạ tầng
  BLK-001) — gỡ BLK-001 không cho phép chạy T-06 khi GATE-A chưa PASS. **WP-A4** giữ READY, song
  song roadmap với WP-A7 kèm ba điều kiện. **WP-A3 giữ nguyên DONE**, không reopen, gate FROZEN,
  evidence E1/E2 nguyên vẹn. DEC-009 áp cho F-035: mọi Gate result trước remediation là
  STALE/INVALIDATED — hiện **NO CURRENT OFFICIAL RESULT TO INVALIDATE**, chuyển thành dependency
  WP-A7 DONE trước T-06. Toàn bộ 35 finding, 11 risk, 3 blocker được bảo toàn. Không sửa `src/`,
  `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, đặc biệt không bắt đầu WP-A7.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`,
  `docs/reviews/PH-03-triage-smart-unlock-scope.md`.
- S003-TRIAGE — PH-03 / RSK-010 — 2026-08-24 — Triage governance + kỹ thuật, **không remediation**.
  Kết luận: PH-03 = **DEFECT**, cấp finding chính thức **F-035** (HIGH, E1). Requirement canonical
  bị vi phạm: **DM §5** (`monthly_budgets` định nghĩa `smart_deployed_vnd` là trường của bản ghi
  THÁNG), củng cố bởi ST §4/§6/§12 và ST §10. Root cause: `smart_reservable` trừ `pool.deployed`
  luỹ kế toàn đời khỏi một tử số theo tháng; `Pool` không có vòng đời tháng. Chứng minh cấu trúc:
  ở `unlock = 1.00`, hàm trả **0.000 từ tháng thứ hai sau khi tháng đầu đóng sổ**, tất định và
  không phụ thuộc dữ liệu. Quan sát 90 tháng: 2 Smart ladder; 135.249/135.251 lời gọi trả 0;
  **99,98%** vốn Smart đi qua Month-End thay vì ladder. Hệ quả nặng nhất: **chiều
  `smart_unlock_mode` của Gate 2 (BT §9) trơ hoàn toàn** — ba mode cho kết quả trùng khít
  bit-for-bit, vi phạm ST §6. Kết luận official run: **không đáng tin trước khi sửa**; DEC-009 áp
  dụng phòng ngừa (`no current result to invalidate`). Phân lớp: **A — MUST FIX BEFORE OFFICIAL
  RUN**, chứng minh bằng dependency. Ownership đề xuất: **WP-A7 mới** (RCP-002, chờ phê duyệt) —
  không nhét vào WP-A3 đã DONE, không sửa gate FROZEN của WP-A4/WP-A6. **WP-A4 MAY PROCEED IN
  PARALLEL** kèm 3 điều kiện (assert tiền đề không suy biến; không hard-code kỳ vọng vốn/ETH nhiều
  tháng; tuần tự hoá thao tác trên `engine.py`). Không sửa `src/`, `tests/`, `webapp/`,
  `docs/spec/`; không chạy official backtest; không mở WP nào.
  Artifact: `docs/reviews/PH-03-triage-smart-unlock-scope.md`,
  `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`.
- S003 — WP-A3: REGIME & VÒNG ĐỜI CRASH LADDER — 2026-08-23 — Gói đầu tiên của lớp A và là gói
  duy nhất lớp A làm đổi kết quả mô phỏng. Ready Gate xác nhận lại (T-04 DONE, routing D/Fable/max
  tự nhiên, validator PASS). Baseline E1 tái hiện đủ 4 finding TRƯỚC khi sửa (F-001: kẹt 27.2
  SMART vĩnh viễn sau CRASH→RECOVERY→STRESSED; F-021: snapshot [F5] 34 thay vì 36; F-030: mọi
  crash zone dán nhãn OPPORTUNITY dù 30/34 vốn SMART; F-022: thoát CRASH sau 49h toàn None).
  Test-first: 18 test mới, 12 FAIL đúng kỳ vọng trước fix. Remediation: tách
  `RegimeTracker.state`/`.label` (CONVENTIONS #14 — [F1] bảo đảm bằng cấu trúc), None không
  được coi là bằng chứng transition (CONVENTIONS #15), snapshot [F5] đúng nghĩa đen + daily
  limit cưỡng chế ở khâu triển khai với `DAILY_LIMIT_BLOCK` (CONVENTIONS #4/#5), pool label
  theo đa số nguồn vốn + `zone_order_key` bổ sung vế "crash sau ladder thường" (CONVENTIONS
  #16). Chỉ chạm `regime.py`, `engine.py`, `tests/`, `docs/CONVENTIONS.md` — đúng Scope Lock,
  không chạm `capital.py`/`score.py`/`webapp/`/`docs/spec/`. Suite 87/87 PASS, không test cũ
  nào bị sửa/nới lỏng. Impact BEFORE/AFTER cùng seed/dataset: mọi sai lệch quy về [F5] ST §14
  và ST §18.3+[F1]; nhãn label_transitions identical; công cụ đo commit tại
  `tests/wp_a3_impact_tool.py` (tái lập HOÀN TOÀN, kể cả BEFORE qua git worktree). E2 độc lập:
  **E2 PASS** (`docs/reviews/E2-WP-A3-regime-ladder.md`) — reviewer tự dựng kịch bản khác chứng
  minh khoá vốn trước fix (kẹt 18.7, release 0) và giải phóng đủ sau fix; 4 kịch bản khoá vốn
  tự nghĩ + long-run: không đường khoá vốn mới; 2 finding hạ tầng test (F-E2-01 đơn vị
  datetime64 trong harness, F-E2-02 script đo chưa commit) được xử lý ngay trong phiên và chạy
  lại xanh. Phát hiện mới ngoài scope: PH-03 → RSK-010 (nghi vấn `smart_reservable` trừ
  deployed xuyên tháng — chờ chủ dự án). WP-A4 chuyển PLANNED → READY. BLK-001 giữ nguyên;
  không official run, không verdict; số liệu synthetic chỉ phục vụ verification (DEC-003).
  Kết luận: **WP-A3 DONE — 10/10 REQUIRED PASS, E2 PASS**.
  Biên bản: `docs/sessions/S003-wp-a3-regime-ladder.md`.
- MICRO-GOVDEF-001 — SỬA BOUNDARY DEFECT + OVERRIDE MECHANISM — 2026-08-23 — Chủ dự án phê duyệt
  PA-1 cho DEC-010. Sửa tổng quát `routing_engine.py` (làm tròn `model_score`/`effort_score` về
  cùng độ chính xác hiển thị **trước khi** so sánh biên Tier/Effort — không epsilon tuỳ tiện, không
  hard-code task nào). Bổ sung cơ chế `check_override` vào `validate_routing.py`: chấp nhận manual
  override chỉ khi có decision reference tồn tại thật trong `PROJECT_DECISIONS.md`, `Router Raw
  Output` xác thực khớp router hiện tại, và override chỉ được leo thang chứ không hạ Tier/Effort.
  Thêm `governance/scripts/governance/test_routing_engine.py` (37 check, gồm quét toàn bộ 5^5×5^5
  tổ hợp đầu vào — 0 lệch còn lại — và 6 ca override hợp lệ/không hợp lệ tổng hợp). Kết quả: WP-A2
  route Tier C **tự nhiên** (giữ nguyên Model Opus, Effort high), không cần override — chuyển
  `BLOCKED` → `READY`. BLK-003 RESOLVED, GOV-RSK-001 CLOSED. Đối chiếu trước/sau trên toàn bộ 16
  file MAJOR task: đúng một dòng đổi (WP-A2, Tier B → C), không task nào khác bị ảnh hưởng. Không
  sửa `src/`, `webapp/`, `tests/`, `docs/spec/`. Không bắt đầu WP nào, không mở S003.
  Kết luận: **MICRO-GOVDEF-001 DONE**.
  Chi tiết: `docs/reviews/GOVDEF-001-routing-engine-boundary.md` mục "Resolution".
- S002 — ROADMAP FINALIZATION / GATE FREEZE (T-04) — 2026-08-23 — Soạn và đóng băng Ready Gate +
  Completion Gate đầy đủ cho toàn bộ 15 work package của RCP-001 (**125 REQUIRED check**), cộng file
  định nghĩa cho chính T-04 (12 REQUIRED check). Chính thức hoá DEC-009 thành `CHECK-B1-02`
  (REQUIRED) của WP-B1. Bảo toàn override DEC-008 cho WP-A2 (Tier C / Opus / high) kèm giá trị
  router thô. Bảo toàn đủ 8 trường provenance của T-06A cũ trong WP-A1. Tách rõ trách nhiệm đo lường
  (WP-A5) khỏi trách nhiệm chính sách verdict (WP-B1). Đối chiếu độ phủ bằng script: 40/40 định danh
  finding có nơi thuộc về. Phát hiện PH-01 (sai số đếm trong tóm tắt S001) và PH-02 → **BLK-003**.
  Không sửa `src/`, `webapp/`, `tests/`, `docs/spec/`, `governance/`. Không bắt đầu work package nào.
  Kết luận: **T-04 DONE — PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S002-t04-gate-freeze.md`.
  Đối chiếu: `docs/reviews/S002-coverage-regression-check.md`.
- RCP-001 — ROADMAP CHANGE APPLIED — 2026-08-23 — Chủ dự án phê duyệt RCP-001 kèm bốn điều kiện
  (cấu trúc 15 work package; phân lớp A/B/C/D với quy tắc Gate 1 staleness cho F-017; bỏ T-06A,
  hấp thụ vào WP-A1; ghi đè routing của WP-A2 lên Tier C). Bảng roadmap chuẩn được cập nhật từ
  14 lên 28 task. Phát hiện và ghi nhận riêng một governance/tooling defect (GOVDEF-001) trong
  chính `routing_engine.py`, tách khỏi finding sản phẩm. Không sửa `src/`, `webapp/`, `tests/`,
  `docs/spec/`. Không bắt đầu thực thi work package nào. Không bắt đầu S002.
  Tài liệu: `PROJECT/ROADMAP_CHANGE_PROPOSAL_001.md`, `docs/reviews/GOVDEF-001-routing-engine-boundary.md`.
- RCP-001 — ROADMAP CHANGE PROPOSAL (trình) — 2026-08-23 — Chuyển 33 finding của S001 thành 15
  work package có dependency graph và phân lớp A/B/C/D. Trình để chủ dự án phê duyệt.
- S001 — DISCOVERY & BASELINE (AUDIT READ-ONLY) — 2026-08-23 — Đối chiếu toàn bộ implementation
  với spec V2.1.5 theo chín nhóm A–I. Sinh Compliance Matrix, Audit Findings (33 finding: 0
  CRITICAL, 8 HIGH, 15 MEDIUM, 7 LOW, 3 spec defect; 18/33 có bằng chứng chạy thật) và Discovery
  Baseline. Không sửa một dòng mã sản phẩm nào. Kết luận: **S001 PASS WITH FINDINGS**.
  Biên bản: `docs/sessions/S001-discovery-baseline.md`.
- S000 — PROJECT OPEN — 2026-08-23 — Chọn profile PRODUCT, khởi tạo trạng thái dự án, lập kế
  hoạch khảo sát (T-01..T-03) và lộ trình sơ bộ 14 task. Không sửa một dòng code sản phẩm nào.
  Biên bản: `docs/sessions/S000-project-open.md`.

## Bằng chứng nền thu tại S000

Đây là bằng chứng **E1 — chạy thật**, khác với các quan sát đọc code (E0) đã nêu ở mục rủi ro.

| Hạng mục | Kết quả | Mức |
|---|---|---|
| Test suite Python | **69 passed, 0 failed, 0 skipped, 0 error** trong 372,63s | E1 |
| Môi trường | Python 3.11.15, node v22.22.2, git 2.43.0 | E1 |
| Thư viện thực cài | numpy 2.4.6, pandas 3.0.5, pyarrow 25.0.1, pytest 9.1.1 | E1 |
| Mạng tới Binance/CoinGecko | Cả ba host trả 403 ở tầng proxy; PyPI thông | E1 |
| `ethdca synth` | 2,0s — 262.748 nến 15m, 3.102 nến ngày | E1 |
| `ethdca freeze` Gate 2 | 19 ứng viên OFAT → loại 1 (`base_pct=0.7`, lý do `smart_pct < 0.15`) → 18 hợp lệ; 200 interaction; **mẫu số 219** | E1 |
| `ethdca freeze` Gate 3 | 14 deterministic + 100 sampled = **114 config** | E1 |
| Parity engine JS ↔ Python | Lệch tối đa **7,39e-11** trên 40 ngày — hai bản đồng thuận | E1 |
| Bất biến kế toán ladder (một tháng) | Tổng bảo toàn 3.000.000 qua fill toàn phần → fill một phần → invalidation → release; không pool nào âm | E1 |
| Build quine của webapp | Self-check đạt, template giải mã lại được | E1 |
| CLI | 6 lệnh: `fetch`, `synth`, `freeze`, `run`, `verdict`, `export-live` | E1 |
| `results/`, `data/`, `.venv/` trong repo | Không tồn tại — xác nhận chưa từng có official run | E1 |

Điều này làm đổi đánh giá ban đầu theo hướng tốt hơn: **mã nguồn khỏe hơn tài liệu gợi ý**.
S001 xác nhận: tầng công thức rất khỏe; tầng đấu nối và tầng vòng đời thì không (xem RCP-001).

Cảnh báo quan trọng về ý nghĩa của các validator governance: chúng đang PASS trên **tập rỗng** —
0 evidence record, 0 MAJOR task file, 0 task DONE. Khung đã có, nội dung thì chưa. Không được
đọc các dòng PASS đó như bằng chứng chất lượng dự án.

## Routing sơ bộ cho task chưa có file định nghĩa

**Cập nhật S002:** mục này không còn là nguồn routing cho 15 work package — cả 15 đã có file định
nghĩa đầy đủ dưới `docs/tasks/`, và file task là nguồn routing chính thức theo
`ROADMAP_SYNC_STANDARD.md`. Các giá trị dưới đây được **giữ lại làm dấu vết lịch sử** và đã được
T-04 xác minh lại bằng `routing_engine.py` (E1): 15/15 khớp, ngoại lệ duy nhất là override DEC-008
của WP-A2. Task còn lại chưa có file định nghĩa (T-05…T-11) vẫn dùng mục này.

Ghi lại để lộ trình có bằng chứng routing, sẽ soạn thành file task đầy đủ và đóng băng tại T-04.
Ký hiệu: D/R/B/A/X = Difficulty, Risk, Blast Radius, Ambiguity, Cross-system.
U/V/H/C/F = Uncertainty, Verification, Horizon, Context, Failure cost.

### Task gốc (S000)

- T-00 — D3 R2 B1 A3 X3 → 2.35 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C4 F2 → 2.7 → xhigh
- T-04 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U2 V2 H3 C3 F3 → 2.60 → xhigh
- T-06 — D2 R3 B3 A1 X3 → 2.45 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-08 — D3 R3 B2 A3 X3 → 2.80 → C (2 floor); U3 V2 H3 C3 F3 → 2.80 → xhigh
- T-09A — D3 R3 B2 A1 X2 → 2.35 → C (floor `safety_business:min_C`); U1 V3 H2 C2 F3 → 2.25 → high
- T-09B — D3 R3 B3 A3 X3 → 3.00 → D (2 floor); U3 V3 H3 C3 F3 → 3.00 → xhigh
- T-10 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
- T-11 — D4 R4 B3 A2 X4 → 3.50 → D (2 floor); U3 V4 H4 C4 F4 → 3.80 → max

Category `accounting_financial` được gắn cho T-06, T-08, T-09A, T-09B, T-10, T-11 vì chúng chạm
lớp tính toán dẫn tới quyết định xuống tiền thật. T-09B gắn thêm
`material_sensitive_data_corruption` vì thao tác chuyển đổi lưu trữ có thể làm hỏng sổ tài chính.

**T-06A đã bị loại khỏi roadmap theo RCP-001** (hấp thụ vào WP-A1). Routing gốc của nó vẫn được
lưu lại để đối chiếu lịch sử: D2 R2 B2 A1 X2 → 1.85 → B; U1 V2 H2 C2 F2 → 1.80 → high.

### Work package của RCP-001 (2026-08-23)

- WP-A1 — D2 R3 B3 A2 X3 → 2.60 → C (không floor); U2 V3 H3 C3 F3 → 2.80 → xhigh
- **WP-A2** — D2 R2 B2 A1 X3 → **model_score = 2.0 (hiển thị), 1.9999999999999998 (nội bộ)** →
  router trả **B** (Sonnet). **GHI ĐÈ THỦ CÔNG theo DEC-008 → Tier C (Opus)**, lý do: defect biên
  dấu phẩy động của router (GOVDEF-001), không phải lỗi chấm điểm đầu vào.
  Effort: U1 V3 H2 C3 F2 → 2.15 → high (giữ nguyên, không bị override)
- WP-A3 — D4 R4 B3 A3 X3 → 3.50 → D (floor `cognitive:A>=3&X>=3`, `cognitive:D>=4&X>=3`,
  `safety_business:min_C`); U3 V4 H4 C3 F4 → 3.65 → max (floor `safety_business:min_high`)
  · category `accounting_financial`
- WP-A4 — D3 R3 B2 A3 X2 → 2.65 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-A5 — D3 R3 B2 A3 X3 → 2.80 → C (floor `cognitive:A>=3&X>=3`); U3 V3 H3 C3 F3 → 3.00 → xhigh
- WP-A6 — D4 R3 B3 A2 X3 → 3.10 → D (floor `cognitive:D>=4&X>=3`); U3 V4 H3 C3 F3 → 3.20 → max
- WP-B1 — D3 R4 B3 A4 X3 → 3.40 → D (floor `cognitive:A>=3&X>=3`, `safety_business:min_C`);
  U3 V3 H3 C3 F4 → 3.25 → max (floor `safety_business:min_high`) · category `accounting_financial`
- WP-B2 — D3 R2 B1 A2 X3 → 2.20 → C (không floor); U2 V3 H3 C3 F2 → 2.55 → xhigh
- WP-B3 — D2 R2 B2 A2 X2 → 2.00 → C (không floor); U1 V2 H2 C2 F2 → 1.80 → high
- WP-C1 — D2 R3 B2 A1 X2 → 2.10 → C (không floor); U2 V3 H2 C2 F3 → 2.45 → xhigh
- WP-C2 — D3 R2 B3 A3 X3 → 2.75 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh
- WP-C3 — D3 R3 B2 A2 X2 → 2.50 → C (floor `safety_business:min_C`); U2 V3 H2 C2 F3 → 2.45 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-C4 — D3 R3 B2 A2 X3 → 2.65 → C (floor `safety_business:min_C`); U2 V4 H3 C3 F3 → 3.00 → xhigh
  (floor `safety_business:min_high`) · category `accounting_financial`
- WP-D1 — D1 R1 B1 A1 X1 → 1.00 → B (không floor); U1 V1 H1 C1 F1 → 1.00 → medium
- WP-D2 — D3 R2 B2 A4 X3 → 2.70 → C (floor `cognitive:A>=3&X>=3`); U3 V2 H3 C3 F2 → 2.55 → xhigh

- **WP-A7** — D3 R4 B3 A3 X3 → **3.25** → **D** (floor `cognitive:A>=3&X>=3`,
  `safety_business:min_C`); U3 V4 H3 C3 F4 → **3.45** → **max** (floor `safety_business:min_high`)
  · category `accounting_financial` · warnings: none.
  **Đã có file định nghĩa** `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` (2026-08-24)
  → **file task là nguồn routing chính thức**; giá trị ở đây giữ làm dấu vết lịch sử và đã được
  `validate_routing.py` kiểm khớp (17 MAJOR task file).

**GOVDEF-001 / MICRO-GOVDEF-001** — không bắt buộc full routing (MICRO). Chấm điểm tham khảo:
D1 R2 B2 A1 X1 → 1.45 → B; U1 V2 H1 C1 F2 → 1.45 → medium.

## Next Session

**Cập nhật sau T-09B (2026-09-02, S014).** `T-09B` = `IMPLEMENTED`. **NEXT SMALLEST ACTION (chủ dự
án, không cần agent):** tạo project Firebase và làm 5 bước ở `webapp/README.md` § Thiết lập Firebase
(tạo project + bật Anonymous + tạo Firestore → điền `webapp/firebase_config.js` → `node
webapp/build_app.js` → `firebase deploy` → mở app ở trình duyệt dùng hằng ngày → chép UID vào
`firestore.rules` → deploy rules), export JSON từ bản artifact cũ và *Nạp lại từ JSON*, rồi lặp lại
bằng tay CHECK-01/02/03/04/14 trên app thật. Sau đó Owner Decision `T-09B: IMPLEMENTED → DONE` kèm
cập nhật `RSK-001`, và khai ba file runtime mới vào `PRODUCTION_PATHS.md` (`H-32`). Không mở task
tiếp theo trong S014.

**Cập nhật sau T-09A (2026-09-02).** Mục "Recommended Session" bên dưới được viết trước
S010/T-09A và giữ nguyên làm dấu vết. Trạng thái hiện tại và hành động nhỏ nhất kế tiếp:

- `WP-A4` **DONE** (S010, `CAP-DATA` repair cycle #1 đã tiêu).
- `WP-C1` **DONE**; `T-09A` **DONE** (2026-09-02, Owner Decision `DEC-018`/`OD-WEBAPP-01`).
  `CAP-WEBAPP` budget Owner-ratified: allowed 2 / used 0 / remaining 2. DỪNG theo chỉ thị chủ
  dự án ở phiên Integration này — không mở task tiếp theo, không chạy T-06, không xây dashboard.
- **NEXT SMALLEST ACTION** — chủ dự án chọn giữa hai đường đang mở trên GATE-A:
  `WP-A1` (`CAP-PROV` budget = 0, cần Owner Decision để mở `OWNER_EXTENSION`), `WP-A5`, `WP-A6`.
  Lưu ý cảnh báo historical state ở mục V-01/V-02 bên dưới — chưa có evidence dữ liệu lịch sử
  sạch, việc code T-09A DONE không tự động xác minh điều đó.
- Blocker V1 còn lại **không đổi** vì T-09A: `WP-A1` (`CAP-PROV` budget = 0, cần Owner
  Decision), `WP-A5`, `WP-A6` trên đường găng GATE-A; `BLK-001` (mạng Binance); `T-09B`
  (RSK-001, lưu trữ bền) cho phần V1 "dữ liệu tồn tại sau reload/restart" ở mức bền vững.

Branch authority (bắt buộc, từ `DEC-013` 2026-09-01):

    Canonical trunk = main.
    Mọi phiên product mới: git fetch origin && git checkout -b <branch> origin/main
    KHÔNG dùng claude/wp-a1-provenance-v67k9h làm long-running integration branch nữa.
    Branch đó được GIỮ cho provenance/history, KHÔNG xoá.

Sau tích hợp, **hai stream chạy độc lập, branch riêng từ `origin/main`**. Repo không có
dependency thật giữa hai stream, nên KHÔNG tạo dependency giả:

- **STREAM DATA** — thi hành `DEC-016`: mở lại `WP-A4` cho **đúng một** repair cycle để sửa
  `F-S009-01`. Budget: `CAP-DATA` allowed 2 / used 0 / remaining 2 (`DEC-017`) — bản sửa này
  là repair cycle **#1**, KHÔNG được reset. Effective Risk = HIGH ⇒ **mandatory batch review
  cuối phiên** theo `RISK_MODEL.md`.
- **STREAM WEB** — `WP-C1` (C/xhigh), `PARALLEL_READY = YES`. Expected Touch Area
  (`webapp/`, `demo/`, `.gitignore`) KHÔNG giao với vùng của STREAM DATA
  (`src/eth_dca_os/**`).

Recommended Session:
S010 — chủ dự án quyết định:

- **Theo đường găng — ưu tiên cao nhất:** `WP-A6` (D/max) — mắt xích cuối của chuỗi
  T-04 → WP-A3 ✅ → {WP-A4 ✅ ∥ WP-A7 ✅} → **WP-A6** → GATE-A → T-06. Nay đủ dependency
  sau khi WP-A4 DONE tại S009. Gói này phải trả lời `HARDENING_BACKLOG.md` **H-15** (số
  phận zone TRIGGERED trong chu kỳ INVALID) — re-trigger BẮT BUỘC, không được bỏ qua.
- **Song song, đủ dependency từ S004:** `WP-A5` (C/xhigh). Lưu ý tuần tự hoá: WP-A5 cùng
  sửa `pipeline.py` với WP-A2 (đã push xong, không còn phiên nào giữ file).
- **Độc lập hoàn toàn với lớp A:** `WP-C1` (C/xhigh). Xác nhận read-only tại S009: Status
  `READY`, dependency T-01 ✅ + T-04 ✅, Expected Touch Area (`webapp/`, `demo/`,
  `.gitignore`) **không giao** với vùng WP-A4 vừa sửa (`src/eth_dca_os/**`). WP-A4 không
  chạm một dòng nào trong `webapp/`. → **WP-C1 vẫn READY và độc lập.**
- `WP-A4`, `WP-D1` đã **DONE** — không còn trong danh sách READY.
- ~~**Trước khi mở bất kỳ gói nào ở trên**, hai hard-stop governance đang chờ quyết định~~ —
  **CẢ HAI ĐÃ ĐÓNG** (2026-09-01, phiên Integration): `DEC-013` đã thi hành (trunk = `main`,
  integration SHA `febc2ec`), và khe thẩm hành của `F-S009-01` đã được `DEC-016` đóng. Không
  còn hard-stop governance nào chặn việc mở gói.

Task đang READY (đủ điều kiện bắt đầu, chưa bắt đầu):
`WP-A5`, `WP-A6` (mới đủ dependency từ S009), `WP-C1`, `WP-D2`.
`WP-A1` đang `IN_PROGRESS` và bị chặn bởi quyết định của chủ dự án, không phải bởi kỹ thuật.

Task đang PLANNED, chưa đủ điều kiện READY:
- `WP-C4` — chờ WP-A6 (WP-A3 ✅, WP-A4 ✅, WP-A7 ✅)

Task đang BLOCKED và lý do:
- `WP-C2` — DEC-005 còn PENDING (thuộc T-05, thẩm quyền chủ dự án)
- `T-03` — chờ WP-C1 (giữ nguyên, không hạ Completion Gate)

Cần chủ dự án quyết định:
1. **DEC-005** — phạm vi công cụ trước verdict (T-05). Không chặn lớp A.
2. **PH-01** — cách đính chính số đếm finding trong biên bản S001.
3. **BLK-001** — máy/VPS truy cập được `data.binance.vision` và `api.binance.com`, cần cho T-06.
   Không gói nào trong 15 gói cần nó, nên chưa gấp.
4. **PH-04** — kênh tiêu thụ unlock liên tục để ba mode `smart_unlock` phân biệt được ở tầng
   outcome (mở WP mới / đề xuất V2.2 qua WP-D2 / chấp nhận giới hạn). Kèm tinh chỉnh
   F-E2A7-03 của reviewer E2: sức phân giải trên dataset chính thức là câu hỏi empirical
   — nên đo trước khi diễn giải Gate-2. Xem mục PH-04 ở Active Risks.
5. **Glob validator** (follow-up #3 của E2-WP-A7-001; tồn đọng từ S003) —
   `validate_evidence.py` / `validate_task_completion.py` quét `TASK-*.md` không khớp
   quy ước `WP-*.md` → hiện PASS trên tập rỗng; cần một gói governance-tooling mở rộng
   glob để Exit Criteria "validators PASS" có nghĩa thực chất.
6. ~~**`F-E2A1R3-05` — phê duyệt COMPLETION GATE CHANGE PROPOSAL cho WP-A4**~~ —
   **ĐÃ QUYẾT** (`DEC-014` / `OD-A4-01`, 2026-09-01) và **ĐÃ ĐÓNG** tại S009:
   `CHECK-A4-10` PASS. Không còn là mục chờ quyết định.
6b. ~~**`F-S009-01` — ownership**~~ — **ĐÃ QUYẾT phần ownership** (`DEC-015`, 2026-09-01,
   phiên Integration Recheck): capability owner = **`CAP-DATA`**; spec verdict =
   **`IMPLEMENTATION_DEFECT`** (BT §18 buộc DEGRADED/INVALID khi indicator daily bắt buộc
   thiếu, và ST §1.1/§1.3/§17 + BT §2 phát biểu cửa sổ theo NGÀY LỊCH — trong khi ST §17.2
   cho thấy spec nói "96 nến" khi muốn đếm theo nến). `OWNER_ASSIGNMENT_REQUIRED` ĐÓNG.
   Số task ID mới = 0.

   **ĐÃ QUYẾT — `OWNER_DECISION_REQUIRED` ĐÓNG** (`DEC-016` / `OD-DATA-01`, 2026-09-01,
   phiên Integration): chủ dự án chọn **phương án (A)** — REOPEN `WP-A4` cho ĐÚNG MỘT repair
   cycle, mở touch area tối thiểu sang `indicators.py` + wiring/test trực tiếp cần thiết;
   KHÔNG tạo WP mới, 0 task ID mới. Chi phí đã được chủ dự án nhìn thấy trước khi quyết:
   bản sửa tiêu repair cycle **#1** của `CAP-DATA` (`DEC-017`: allowed 2 / used 0 /
   remaining 2). Phiên Integration **KHÔNG thi hành** quyết định này. Đoạn dưới giữ nguyên
   để đọc được bối cảnh lúc quyết định.

   **ĐÃ THI HÀNH và ĐÃ ĐÓNG tại S010** (2026-09-01, CAP-DATA REPAIR CYCLE #1):
   `CHECK-A4-11` PASS ở E1, `WP-A4` trở lại `DONE` với 10/10 REQUIRED. Diff production của
   chu kỳ đo bằng lệnh — `git diff --shortstat cb75f9d..ef8cdbb -- <production paths>` →
   `1 file, +74 / −5`, đúng một file `src/eth_dca_os/indicators.py`. `CAP-DATA` budget nay
   allowed 2 / **used 1** / remaining 1 (`REVIEW_BUDGET_LEDGER.md` §2.1 và §4.2). Batch
   review bắt buộc: PASS, 0 BLOCKING —
   `docs/reviews/S010-batch-review-calendar-indicator.md`. `MAX_MISSING_RATIO` KHÔNG đổi.
   Số task ID mới = 0. `F-S009-01` không còn là mục chờ quyết định.

   Bối cảnh lúc còn mở — đúng MỘT quyết định, ưu tiên cao nhất. Đây không
   còn là khe ownership mà là khe **thẩm quyền thi hành**: `CAP-DATA` chỉ có một thành viên
   là `WP-A4`, đang `DONE` với Completion Gate FROZEN, và `indicators.py` nằm ngoài Expected
   Touch Area. Bốn ngưỡng Absorption Limit đều **KHÔNG chạm** (A: Effective Risk `MAX(3,2)=3`
   không đổi; B: 2/3 mục; C: +11,1%; D: nằm trên vertical slice), nên đây **không** phải
   `ABSORPTION_LIMIT_REACHED`. Ba lựa chọn của chủ dự án — (A) mở lại `WP-A4` + gate change
   proposal + mở touch area sang `indicators.py` *(khuyến nghị)*; (B) DESCOPE *(mâu thuẫn
   `DEC-011` điểm 9)*; (C) task ngoại lệ *(chủ dự án tự đặt ID)*. Chi tiết + bằng chứng E1
   tái lập tại phiên: `docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md` PHẦN II.

   Dữ kiện budget cho quyết định: `git log 666de14..HEAD -- src/eth_dca_os/indicators.py`
   = **0 commit**, nên finding nằm NGOÀI mọi cumulative repair diff và bản sửa **sẽ tiêu một
   repair cycle mới** của owner nhận nó.
7. **WP-A1 — disposition cho 3 hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED`**
   (`F-E2A1-03`, `F-E2A1R3-03`, `F-E2A1R3-06`+`F-E2A1-08`): mỗi hạng mục chọn
   `ACCEPT_AS_IS` / `DESCOPE` / `OWNER_EXTENSION`. Budget CAP-PROV đã hết
   (`DEC-012`: allowed 2 / used 2 / remaining 0). Lưu ý: 2 trong 3 hạng mục đóng được ở
   chi phí budget = 0 vì chỉ cần tài liệu. Xem bản disposition §4.
8. ~~**Integration decision** (`DEC-013`)~~ — **ĐÃ QUYẾT và ĐÃ THI HÀNH** (2026-09-01,
   phiên Integration): phương án **A — INTEGRATE NOW**; canonical trunk = **`main`**; tích
   hợp bằng merge commit thường `febc2ec`; 0 xung đột; tree kết quả TRÙNG KHÍT tree source;
   content lost = 0; 11/11 baseline SHA vẫn reachable. Hard-stop
   `INTEGRATION_DECISION_REQUIRED` **ĐÓNG**. Không còn là mục chờ quyết định.

   Còn lại đúng **một thao tác của chủ dự án trên GitHub**, không phải quyết định kỹ thuật:
   `REMOTE_DEFAULT_SWITCH_REQUIRED` — đổi default branch của repository sang `main` (GitHub
   → Settings → General → Default branch → Switch to `main`). `origin/main` đã tồn tại và
   đúng nội dung; việc chưa đổi `origin/HEAD` KHÔNG làm phép tích hợp thất bại.
9. **Trình tự V1** — T-06/GATE-A có thật sự là điều kiện tiên quyết của V1 daily-use không,
   hay đường web app (`CAP-WEBAPP`, WP-C1 đang READY và độc lập với lớp A) chạy song song
   được? `DEC-011` định nghĩa V1 theo web app dùng hàng ngày, trong khi
   `CAPABILITY_REGISTRY` xếp `CAP-WEBAPP` ngoài Vertical Slice. Câu này đổi đường găng một
   cách vật chất. Xem bản disposition §8.1.

Owner Decision đã ghi tại phiên Owner Disposition (2026-09-01):
`DEC-011` (Product Intent + V1 Daily-Use Acceptance), `DEC-012` (hạn mức budget CAP-PROV),
`DEC-013` (integration — nay **RESOLVED / INTEGRATED** tại phiên Integration cùng ngày). Phân loại lại toàn bộ finding đang mở, đề xuất capability
owner cho `F-E2A1R3-05`, và Integration Decision Check đầy đủ nằm ở
`docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md`.

Trạng thái WP-A1 KHÔNG đổi sau phiên đó: `IN_PROGRESS`, CHECK-A1-01…10 `PASS`,
CHECK-A1-11 `FAIL`, GATE-A KHÔNG ĐÓNG, T-06 KHÔNG MỞ. Không task ID mới, không WP mới,
production/test diff = 0.

**S009 cũng KHÔNG đổi trạng thái WP-A1.** WP-A4 đóng `F-E2A1R3-05` ở `CAP-DATA`, nên
finding đó chuyển từ "đang mở, chưa có chủ" sang "đã đóng, chủ = CAP-DATA". WP-A1 vẫn
`IN_PROGRESS`, CHECK-A1-11 vẫn `FAIL`, repair cycle của WP-A1 vẫn = 2 (KHÔNG tăng), budget
`CAP-PROV` REMAINING vẫn = 0, và ba hạng mục `LEGACY_GATE_DISPOSITION_REQUIRED` vẫn chờ chủ
dự án — S009 KHÔNG tự đóng mục nào trong đó.

Purpose:
Tiếp tục chương trình remediation lớp A trên đường găng tới official run, với Completion Gate đã
đóng băng từ T-04.

KHÔNG tự mở — chủ dự án sẽ ra chỉ thị riêng.

Files to read first:
1. `CLAUDE.md`
2. `PROJECT/PROJECT_PROFILE.md`
3. `PROJECT/PROJECT_PROGRESS.md` (file này)
4. `PROJECT/PROJECT_DECISIONS.md`
5. File định nghĩa của work package được chọn, dưới `docs/tasks/`
6. `docs/sessions/S004-wp-a7-monthly-smart-scope.md` (phiên gần nhất; kế toán Smart theo
   tháng mới) và `docs/sessions/S003-wp-a3-regime-ladder.md` (ngữ nghĩa regime/ladder)
7. `docs/CONVENTIONS.md` #14–#17 (nếu gói chạm engine/regime/capital)
8. `docs/reviews/S001-audit-findings.md` — phần finding mà gói đó đóng
9. `docs/spec/` — các điều khoản được viện dẫn trong Completion Gate của gói

Nhắc trước khi mở S005:
Completion Gate của cả 15 gói đã **đóng băng** ngày 2026-08-23. Không được xoá hay làm yếu bất kỳ
REQUIRED check nào để gói đi qua. Nếu một check hoá ra sai hoặc bất khả thi, dùng khối
`COMPLETION GATE CHANGE PROPOSAL` theo `TASK_COMPLETION_GATE_STANDARD.md` và trình chủ dự án —
không sửa im lặng.
