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

Full suite: xem `EXIT`/tổng kết cuối file này (chạy `pytest tests/ -q -p no:cacheprovider`,
tương tự lệnh dùng ở lát cắt S016).

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

## 7. Khuyến nghị

**WP-B1 REMAINS IN PROGRESS.** 7/10 REQUIRED PASS trong phạm vi agent có thể tự thực hiện. 2 check
`BLOCKED` cần input/quyết định của chủ dự án (CHECK-B1-04: phê chuẩn ngưỡng; CHECK-B1-08: cung cấp
`pipeline_state.json` official hoặc tự chạy `ethdca verdict`). 1 check `NOT_TESTED` cần một phiên
E2 độc lập riêng (CHECK-B1-09). Không đề xuất DONE.
