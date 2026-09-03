# S023 — WP-B1 (verdict correctness): IN_PROGRESS, 7/10 REQUIRED PASS, 2 BLOCKED, 1 NOT_TESTED

Ngày: 2026-09-03
Nhánh: `claude/wp-b1-verdict-correctness-j9d390`
Base canonical xác nhận đầu phiên: `origin/main` = `fa6422c469f5e2ae5da3390de271ecace4b505b4`
Task: `docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md` — `PLANNED → READY (DEC-031) →
IN_PROGRESS` (phiên này)
Capability: `CAP-VERDICT` (lineage root `WP-B1`, baseline `28b0255`) — **implementation ban đầu
tiếp nối** (task chưa từng DONE nên chưa có repair cycle nào để mở), KHÔNG tiêu repair cycle.
Model/Effort canonical: Tier D / max.

## 0. Trạng thái canonical đầu phiên (đã xác nhận, không tự suy)

`T-06 = DONE` (historical disposition, `DEC-031`) · `V2.1.5 validation = FAILED` · official
verdict = `DO_NOT_BUILD` (Gate 1 FAIL, OOS hard condition FAIL) · `can_proceed_to_app = false` ·
`BLK-001 = RESOLVED` · `WP-B1 = READY` · `WP-B2 = READY` · `WP-B3 = BLOCKED` bởi `WP-C2` ·
`GATE-B` chưa mở · `T-07 NOT READY`. Official tag `v2.1.5-official-T06` peel = `5228130`.
Lát cắt pre-T06 (`DEC-026`, S016) đã đóng `F-S015-01` và phần cơ chế của `CHECK-B1-01` — KHÔNG
làm lại trong phiên này.

## 1. Việc đã làm trong phiên (DISCOVER → CLASSIFY → REPAIR, trong phạm vi WP-B1)

### CHECK-B1-02 (DEC-009) — PASS, kết luận KHÔNG
Đọc `src/eth_dca_os/pipeline.py::run_gate1` xác nhận Gate 1 (`evaluate_gate1`) và OOS
(`evaluate_oos`) được tính XONG và ghi vào `payload` **trước** khi `full = run_engine(...)` (dùng
riêng cho Control F/G) được gọi; Gate 2/Gate 3 nằm ở hai hàm khác không đọc `full`/
`monthly_tranches` bao giờ. Output duy nhất của Control F/G đi vào FS-08 — một Failure Signal,
không phải Gate/OOS. Vì `verdict.py` xét Gate1/OOS ở nhánh **đầu tiên**, FS không ảnh hưởng verdict
khi Gate1/OOS đã FAIL (đúng ca T-06). Kết luận: Gate 1 KHÔNG cần chạy lại.

### CHECK-B1-03 (F-017) — PASS
`random_timing_control`/`random_anchor_control` (`benchmarks.py`) trước đây gộp TOÀN BỘ nominal
một tháng vào MỘT lệnh tại một timestamp ngẫu nhiên — sai chữ BT §12. Sửa: `run_gate1` (`
pipeline.py`) nhóm `full.purchases` (bản ghi tranche thật, ĐÃ CÓ SẴN, không sửa `engine.py`) theo
tháng thành `monthly_tranches: {thang: [nominal_tranche, ...]}`; Control F/G nay lặp và random hóa
ĐỘC LẬP cho từng tranche. `cli.py`/`test_e2e.py` cập nhật theo khoá payload mới
(`_full_run_monthly_tranches`, đổi tên từ `_full_run_monthly_deployments`).

Test mới (`tests/test_benchmarks.py`): đếm số lần `_fill` thật (đúng số tranche, không phải số
tháng) + so sánh phương sai many-tranche vs one-lump (hệ quả tất yếu của randomize độc lập).

### CHECK-B1-05 / CHECK-B1-06 — PASS
`docs/CONVENTIONS.md` mục #21(a)-(d): ánh xạ gate-fail→verdict (đóng F-026), chính sách UNKNOWN
(chốt B1.1 — giữ `BUILD_WITH_MODIFICATIONS`, không thêm nhãn mới), `shift_days=10` của Control G,
và quy ước Control F/G per-tranche mới. Phạm vi window FS-03/FS-07 xác nhận đã đủ từ WP-A5 #20(d).

### CHECK-B1-07 — PASS
`tests/test_wp_b1_verdict_policy.py` (12 test mới): precedence khi nhiều gate FAIL đồng thời
(Gate1/OOS luôn thắng Gate2/3/FS), `can_proceed_to_app` đúng nghĩa qua 6 tổ hợp, numpy.bool_/bool
ở tầng `gates.py` (họ H-26) không làm verdict sai (kiểm bằng input `numpy.float64` thật qua
`evaluate_gate1`/`evaluate_oos`), determinism (input giống hệt, kể cả mang numpy type → output
giống hệt).

### CHECK-B1-01 — addendum (không đổi status PASS đã có từ lát cắt DEC-026)
Câu hỏi chính sách B1.1 còn mở (UNKNOWN → BWM hay INCONCLUSIVE) nay CHỐT bằng #21(b): giữ BWM,
không sửa `verdict.py`.

## 2. Không làm được trong phiên — lý do cụ thể, không phải lười

### CHECK-B1-04 (ngưỡng FS-02/FS-07/FS-12) — `BLOCKED`
Cần quyết định chủ dự án. Escalation Trigger của chính task cấm agent tự phê chuẩn thay. Không
đổi hằng số nào trong `failure_signals.py`.

### CHECK-B1-08 (tính lại verdict từ `pipeline_state.json` official) — `BLOCKED / MISSING_INPUT`
File này là 1 trong 16 artifact official được chủ dự án bảo toàn **bên ngoài repository**
(`docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §4). `find` toàn repo xác nhận không tồn tại trong
`/home/user/coin`. Agent không có quyền/khả năng lấy file này, và không được rerun official run
(Master Index §6). Cần chủ dự án cung cấp file hoặc tự chạy `ethdca verdict` và dán lại kết quả.

### CHECK-B1-09 (E2 độc lập) — `NOT_TESTED`
Đòi một phiên reviewer KHÁC, chưa đọc kết luận implementer. Cùng một agent/phiên không thể tự cấp
E2 cho chính mình.

## 3. Finding mới phát sinh, đã ghi nhận đúng phân loại

`HARDENING_BACKLOG.md` H-26 (`gates.py` trả `numpy.bool`, cùng họ `F-S015-01`): RE_TRIGGER_CONDITION
thứ hai ("WP-B1 đầy đủ mở đường verdict, B1.1/B1.5") ĐÃ KÍCH HOẠT trong phiên này. Nhưng `gates.py`
nằm trong "Do not touch without Scope Expansion" của Expected Touch Area — agent KHÔNG tự ý sửa,
chỉ ghi nhận điều kiện đã kích hoạt và để lại cho một quyết định Scope Expansion tường minh. Vẫn
CONFIRMED HARDENING (không có hậu quả nghiệp vụ — consumer đọc bằng truthiness).

Không có finding BLOCKING mới nào khác phát sinh trong phạm vi capability này.

## 4. Bằng chứng test

Targeted: `pytest tests/test_benchmarks.py tests/test_e2e.py tests/test_gates_verdict.py
tests/test_wp_b1_verdict_policy.py -v` → **26/26 PASS**.

Full suite (`pytest tests/ -q -p no:cacheprovider`): **391 collected, 391 PASS, 0 FAIL/ERROR/SKIP,
`EXIT=0`.** (Lần chạy đầu tiên trong phiên phát hiện 1 FAIL không liên quan đến WP-B1:
`test_a1_08_lockfile_matches_installed_environment` — venv sạch dựng trong phiên này lệch phiên
bản transitive dependency của `requests` so với `pyproject.lock` do PyPI có bản patch mới hơn từ
lúc lockfile được sinh. Đây là artifact môi trường của phiên, không phải regression code — xác
nhận bằng cách ghim lại đúng phiên bản theo `pyproject.lock` [không sửa file production/lockfile
nào] rồi chạy lại full suite sạch, PASS 391/391.) → **CHECK-B1-10 PASS**.

Production diff phiên này (đo bằng lệnh, không suy diễn):
`git diff --shortstat fa6422c -- src/eth_dca_os` → 3 file (`benchmarks.py`, `cli.py`,
`pipeline.py`), +46/−25. Không chạm `gates.py`, `engine.py`, `verdict.py`, `regime.py`,
`ladders.py`, `capital.py`, `score.py`. Không đổi hằng số ngưỡng nào.

## 5. Production reachability

`test_e2e.py::test_full_pipeline_smoke`/`test_gate1_reproducible` chạy nguyên pipeline
(`Prepared` → `run_gate1` → `run_gate2`/`run_gate3` (dev-limit) → `run_controls` → `run_verdict`)
qua CLI thật (`eth_dca_os.cli`) trên dữ liệu synthetic — xác nhận `monthly_tranches` mới đấu nối
đúng từ `run_gate1` qua `run_controls` tới `run_verdict` không lỗi runtime, verdict vẫn nằm trong
bốn giá trị hợp lệ. Đây là bằng chứng CƠ CHẾ (mechanism), KHÔNG phải bằng chứng cho số liệu
official — số liệu official cần CHECK-B1-08 (BLOCKED).

## 6. State preservation — xác nhận KHÔNG đổi

`T-06 = DONE`, `V2.1.5 = FAILED`, verdict = `DO_NOT_BUILD`, `can_proceed_to_app = false`,
`BLK-001 = RESOLVED` — không đổi. `WP-B2 = READY`, `WP-B3 = BLOCKED` (WP-C2), `GATE-B` chưa mở,
`T-07 NOT READY` — không đổi. Official tag `v2.1.5-official-T06` không bị chạm, vẫn peel về
`5228130`. Không mở WP-B2/WP-B3/GATE-B/T-07. Không merge `main`. Không tạo task ID mới (0 task
mới — chỉ cập nhật check/subtask có sẵn trong `WP-B1`).

## 7. Khuyến nghị (tại thời điểm phần 1-6 ở trên)

**WP-B1 REMAINS IN PROGRESS.** 7/10 REQUIRED PASS (01, 02, 03, 05, 06, 07, 10) trong phạm vi agent
có thể tự thực hiện. 2 check `BLOCKED` cần input/quyết định của chủ dự án (CHECK-B1-04: phê chuẩn
ngưỡng; CHECK-B1-08: cung cấp `pipeline_state.json` official hoặc tự chạy `ethdca verdict`). 1
check `NOT_TESTED` cần một phiên E2 độc lập riêng (CHECK-B1-09). Không đề xuất DONE.

---

## Addendum — Owner Decision `DEC-033` + CHECK-B1-08 Owner-supplied evidence (cùng phiên, tiếp nối)

### A. CHECK-B1-04 — Owner Decision `DEC-033` (`OD-B1-02`)

Chủ dự án APPROVE AS-IS toàn bộ ba ngưỡng, không đổi giá trị nào:

    FS-02: opportunity_cap_hit_share > 0.5
    FS-07: avg_cash_ratio > 0.30 AND gate1_primary_ae < 102.0
    FS-12: regime_advantage_share > 0.80

Lý do (nguyên văn Owner): "Giữ nguyên các threshold đã được sử dụng trong V2.1.5 vì đây là
semantics implementation ban đầu và hiện chưa có evidence độc lập đủ mạnh để biện minh cho
threshold thay thế." Không tuyên bố ngưỡng là tối ưu thực nghiệm; không tự động cho phép mang
sang V2.2. Canonical hóa tại `docs/CONVENTIONS.md` #21(e) và `PROJECT/PROJECT_DECISIONS.md`
`DEC-033`. **Production diff của phần này = 0** (đúng chỉ thị "Không sửa threshold trong
production code" — giá trị số y hệt từ trước). Vì verdict T-06 quyết ở nhánh Gate 1/OOS FAIL,
trước khi FS cap được xét (CHECK-B1-02), quyết định này không đổi semantics đã dùng ở T-06.
`CHECK-B1-04: BLOCKED → PASS`. `F-015` ĐÓNG.

### B. CHECK-B1-08 — Owner-supplied official evidence

Owner thực hiện read-only verification trên COPY của frozen official T-06 backup
(`/Users/hoangvinh/Documents/CoinDCA_T06_OFFICIAL_BACKUP_2026-09-03`), chạy
`ethdca verdict --out-dir results`. Kết quả:

- `pipeline_state.json`: `verdict=DO_NOT_BUILD`, `can_proceed_to_app=false`, `reasons` hiển thị
  dưới dạng chuỗi literal `"[2 items]"`.
- Xác nhận bằng đọc code: đây là hành vi THIẾT KẾ có sẵn (`cli.py::_strip()` nén MỌI list thành
  `"[N items]"` khi ghi state "gọn"; `reporting.py::write_report()` tự ghi rõ trong docstring:
  "Khác `pipeline_state.json` ở chỗ KHÔNG rút gọn list... còn file này giữ nguyên số liệu
  (reasons...)") — không phải lỗi mới, không phải mất dữ liệu.
- Full reasons cross-verified từ hai artifact KHÁC cùng gói frozen official evidence, cả hai đã
  canonical hoá SHA-256 tại `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` §4:
  `results/baseline_808b61fa5ffe_metrics.json` và `results/report.json` — cả hai đều
  `verdict=DO_NOT_BUILD`, `reasons=["Gate 1 FAIL", "OOS hard condition FAIL"]`,
  `can_proceed_to_app=false`. `backtest_runs.jsonl` (`run_id=baseline_808b61fa5ffe`) corroborate:
  `code_commit=5228130677e9e9875335eef890b6ed748a384603` (khớp official commit), `official=true`.
- Đánh giá acceptance criteria: `report.json`/`baseline_*_metrics.json` không phải "nguồn khác"
  hay dữ liệu suy diễn — chúng là companion file được CHÍNH THIẾT KẾ HỆ THỐNG (`save_run()`/
  `write_report()`, không qua `_strip()`) chỉ định là bản đầy đủ, sinh cùng lúc, từ cùng phép
  tính, thuộc cùng gói official evidence đã canonical hoá. Kết luận: **CHO PHÉP** cross-artifact
  evidence trong trường hợp cụ thể này.
- Không rerun T-06. Không sửa artifact nào (Owner thao tác trên bản copy; `ethdca verdict` xác
  nhận read-only qua đọc code ở phiên trước).

`CHECK-B1-08: BLOCKED → PASS`, ghi rõ cả bốn điểm trên trong evidence (không tuyên bố
`pipeline_state.json` tự nó chứa full reasons).

### C. H-26

Giữ nguyên `HARDENING`. Không Scope Expansion, không sửa `gates.py` trong lượt này.

### D. Test/validator chạy trong lượt này

Lượt này KHÔNG sửa bất kỳ file production nào (`git status` xác nhận: chỉ
`PROJECT/PROJECT_DECISIONS.md`, `docs/CONVENTIONS.md`, `docs/tasks/WP-B1-*.md` thay đổi — 0 file
dưới `src/`/`tests/`). Không cần chạy lại test suite vì không có code nào để hỏng. Không rerun
official T-06. Không chạy CHECK-B1-09.

### E. Production diff của lượt này

`git diff --shortstat -- src/eth_dca_os tests` = rỗng (0 file). Toàn bộ thay đổi là docs/state:
`PROJECT/PROJECT_DECISIONS.md` (+`DEC-033`), `docs/CONVENTIONS.md` (+#21(e)),
`docs/tasks/WP-B1-*.md` (evidence CHECK-B1-04/08, subtask B1.4/B1.8, Exit Criteria),
`PROJECT/PROJECT_PROGRESS.md`, `docs/sessions/S023-*.md` (addendum này).

### F. WP-B1 REQUIRED checks sau lượt này

9/10 PASS (01, 02, 03, 04, 05, 06, 07, 08, 10). 1/10 `NOT_TESTED`: CHECK-B1-09 (E2 độc lập) — check
REQUIRED DUY NHẤT còn lại trước khi WP-B1 có thể đạt Completion Gate 100%.

### G. WP-B1 technical/lifecycle state

Technical: 9/10 REQUIRED PASS, 1 NOT_TESTED. Lifecycle: `IN_PROGRESS` (không đổi, chưa DONE —
CHECK-B1-09 chưa PASS).

### H. Requirement còn lại trước Completion Gate

Duy nhất: một phiên "Solo Independent Review Procedure" độc lập cho `CHECK-B1-09`, rà soát đặc
biệt CHECK-B1-01/02/07 (và nay có thể mở rộng xem xét CHECK-B1-04/08 vì đây là hai check vừa
đóng), lưu tại `docs/reviews/E2-WP-B1-*.md`.

### Khuyến nghị cập nhật

**WP-B1 REMAINS IN PROGRESS.** 9/10 REQUIRED PASS — tiến bộ đáng kể so với phần 1-6 (7/10).
Không còn `BLOCKED` nào. Chỉ còn một việc duy nhất chặn Completion Gate: phiên E2 độc lập
(`CHECK-B1-09`). Không đề xuất DONE.
