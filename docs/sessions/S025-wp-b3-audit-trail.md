# S025 — Thực thi WP-B3: audit trail / decision_log

Ngày: 2026-09-04
Nhánh: `claude/wp-b3-audit-trail-impl-3covtf` (tách từ `origin/main` `04f77ac`)
Vai trò phiên: **implementer** (không phải rà soát độc lập)
Báo cáo đầy đủ: `docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md`

---

## 1. Phiên này đã làm gì

Thực thi `WP-B3` — đóng `F-024` và `F-033`. Gói **ghi lại** quyết định của engine; nó không đổi
một quyết định nào.

- `WP-B3`: `READY → IN_PROGRESS → IMPLEMENTED`. **Chưa `DONE`** (xem §4).
- 8/8 REQUIRED check PASS (`CHECK-B3-01`…`CHECK-B3-08`), E1 toàn bộ.
- Đầu ra tài chính/chiến lược **không đổi bit-for-bit**.
- Diff production: **1 file, +266/−15** (`src/eth_dca_os/engine.py`).
- Test mới: 43 (`tests/test_wp_b3_audit_trail.py`).
- Task ID mới: **0**. Repair cycle tiêu: **0**. Budget `CAP-VERDICT`: `2 / 0 / 2` — không đổi.

## 2. Thiết kế đã chốt (một câu mỗi ý)

- **Một audit trail duy nhất:** `RunResult.decision_log` được tiến hoá tại chỗ thành bảng
  DM §11 — 19 trường của bảng + đúng một trường `tags`. Không log song song.
- **Tiêu thụ WP-C2, không tạo hợp đồng thứ hai:** `previous_state`/`new_state` là chính thành
  viên `ExecutionState`; bản ghi chuyển trạng thái sinh trong CHÍNH nhánh đã ghi
  `execution_state_timeline` → `số bản ghi chuyển = số mốc timeline − 1`.
- **Lý do chỉ từ ST §20:** mã của dữ kiện quyết định trạng thái MỚI, theo đúng thứ tự ưu tiên
  đã đóng băng của WP-C2; `WAIT` mang mã của dữ kiện vừa CHẤM DỨT. Không phát minh mã mới.
- **Nhãn ST §9:** `EXECUTED_EARLY` nằm trên bản ghi audit, **không** trên `purchases[].tags`
  (đó là nhãn chất lượng dữ liệu BT §18 và là đầu ra tài chính phải bất biến).
- **Hết cờ:** `log_decisions` bị gỡ khỏi `run_engine` — audit trail của official run không thể
  là tuỳ chọn.
- Quy ước đầy đủ: `docs/CONVENTIONS.md` **#23** (a)–(h).

## 3. Bằng chứng chốt (số, không phải lời)

| Việc | Số đo |
|---|---|
| Bất biến tài chính | payload chuẩn tắc 3.728.853 byte, `sha256 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7` — TRÙNG ở lần chạy TRƯỚC (HEAD `04f77ac`) và lần chạy SAU |
| Log không điều khiển hành vi | gỡ HẲN lớp ghi log rồi chạy lại: fingerprint vẫn trùng bốn giá trị chụp trước bản sửa |
| Production reachability | 12 lần chạy `run_engine` thật; **5.614 bản ghi**; trước gói **0 bản ghi** trên đường production |
| Phạm vi sự kiện | 3 loại → **25 loại** trên một run toàn kỳ; 32/36 mã ST §20 được ghi, 4 mã còn lại có lý do canonical |
| Chuyển trạng thái | 1.043 = 1.044 − 1 và 1.077 = 1.078 − 1 (khớp từng cặp với timeline WP-C2) |
| Test của gói | 43 test, phủ A–L của danh sách đối kháng |
| Regression | xem §16 của báo cáo |
| Validator | 9 công cụ chạy; 2 validator PASS **vacuous** (`H-08`, không sửa trong phiên này) |

Công cụ tái lập được, đã commit:

    python tests/wp_b3_invariance_tool.py --raw <raw> --out <payload.json>
    python tests/wp_b3_scenarios.py
    python -m pytest tests/test_wp_b3_audit_trail.py

## 4. Việc còn lại — đúng một, và thuộc chủ dự án

    OWNER_DECISION_REQUIRED — đóng vòng đời: WP-B3: IMPLEMENTED -> DONE

`STATE_AUTHORITY.md` quy định `DONE` do chủ dự án ghi (tiền lệ `WP-B1`/`DEC-034`,
`WP-C2`/`DEC-036`). Gate của `WP-B3` **không đòi E2** ở check nào (`Risk = 2 → E1`), nên không
có `E2_REQUIRED`.

## 5. Downstream — KHÔNG đổi

`GATE-B` (= `WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`) **VẪN CHƯA MỞ**: `WP-B2` mới `READY`,
`WP-B3` mới `IMPLEMENTED`. `T-07` vẫn `NOT READY`; `T-11` vẫn `BLOCKED`.
Giữ nguyên: `T-06 = DONE`, V2.1.5 validation = `FAILED`, verdict = `DO_NOT_BUILD`,
`can_proceed_to_app = false`, `DEC-005 = PENDING` (vẫn chặn `T-08`), `WP-C3 = READY` (chưa mở).

Phiên này KHÔNG chạy `WP-B2`/`WP-C3`, KHÔNG mở `GATE-B`/`T-07`, KHÔNG rerun `T-06`, KHÔNG điều
tra AE, KHÔNG đổi threshold/strategy/verdict/benchmark, KHÔNG đụng `webapp/` hay `docs/spec/`,
KHÔNG merge `main`, KHÔNG đụng `data/` (untracked).

## 6. Hardening phát sinh (finding ≠ task)

- **H-36** — nhánh `ACTION_TTL_EXPIRED` không tới lượt khi `action_ttl_seconds % 900 == 0`
  (`CAP-ENGINE`/`WP-A3`; cấu trúc sẵn có của engine, `WP-B3` chỉ làm nó quan sát được).
- **H-37** — ST §20 thiếu mã cho `COOLDOWN → WAIT` (hết hạn) và `DATA_BLOCKED → WAIT` (dữ liệu
  trở lại GOOD) (`CAP-SPEC`/`WP-D2`; khiếm khuyết ĐẶC TẢ, không vá V2.1.5).
- **H-38** — `task_registry_snapshot.sh` bỏ sót `IMPLEMENTED`/`VERIFYING` khi đếm SET A
  (`CAP-GOVTOOL`, `OWNER_ASSIGNMENT_REQUIRED`; không sửa tooling governance trong phiên thực thi).

Cả ba đều có `RE_TRIGGER_CONDITION` cụ thể trong `PROJECT/HARDENING_BACKLOG.md`.
