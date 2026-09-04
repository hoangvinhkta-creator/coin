# S024 — Thực thi WP-C2: đặt tên và lưu vết Execution State

Ngày: 2026-09-04
Nhánh: `claude/wp-c2-execution-state-y4rraf` (tách từ `origin/main` `2189a8f8`)
Vai trò phiên: **implementer** (không phải rà soát độc lập)
Báo cáo đầy đủ: `docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md`

---

## 1. Phiên này đã làm gì

Thực thi `WP-C2` — đóng `F-006`. Gói **đặt tên** cho hành vi đã có, không viết logic thực thi
mới.

- `WP-C2`: `READY → IN_PROGRESS → IMPLEMENTED`. **Chưa `DONE`** (xem §4).
- 8/8 REQUIRED check PASS (`CHECK-C2-01`…`CHECK-C2-08`).
- Kết quả backtest **không đổi bit-for-bit**.
- Diff production: **1 file, +128/−0** (`src/eth_dca_os/engine.py`).
- Full suite: **494/494 PASS**, exit 0.
- Task ID mới: **0**. Repair cycle tiêu: **0**. Budget `CAP-WEBAPP`: `2 / 0 / 2` — không đổi.

## 2. Thiết kế đã chốt (một câu mỗi ý)

- **Vốn từ vựng:** `engine.ExecutionState` — `StrEnum`, đúng sáu giá trị ST §16/§19.
- **Hợp nhất:** `engine.derive_execution_state(...)` — hàm thuần, gộp `Zone.status` /
  `data_quality` / cooldown thành một chiều; **không có class `StateMachine`** (`CHECK-C2-07`).
- **Điểm đo:** bước **12b** của BT §19 — nơi duy nhất `READY_TO_BUY` tồn tại (tới bước 16–17
  fill đã xong).
- **Thứ tự ưu tiên:** `READY_TO_BUY > ACTION_PENDING > DATA_BLOCKED > COOLDOWN > WAIT`, lấy từ
  chính thứ tự kiểm của engine, không phải thẩm mỹ.
- **Lưu vết:** `RunResult.execution_state_timeline` (ghi-khi-đổi, độ phân giải nến) và
  `RunResult.market_snapshots` (mỗi accounting day, `execution_state` NOT NULL — DM §4).
- **`FUNDING_REQUIRED`:** `NOT_APPLICABLE` ở tầng backtest theo `ADR-001`; vẫn nằm trong enum vì
  Product Spec §6/§7/§11 đòi nó ở tầng app.
- Quy ước đầy đủ: `docs/CONVENTIONS.md` **#22** (a)–(g).

## 3. Bằng chứng chốt (số, không phải lời)

| Việc | Số đo |
|---|---|
| Bất biến backtest | payload chuẩn tắc 1.340.788 byte, `sha256 e0492a58f67e9fab0105216713ed9ca3dfecbae1608d91089ca48eef380fdbba` — TRÙNG ở hai lần chạy BEFORE độc lập và ở lần chạy AFTER |
| Production reachability | 13 lần chạy qua hàm production; 17.532 snapshot; **0 null**; đủ 5 trạng thái trong phạm vi; `FUNDING_REQUIRED` = 0 |
| Test của gói | 33 test, phủ A–L của danh sách đối kháng |
| Regression | 494 passed / 0 failed / 0 error / 0 skipped, exit 0 |
| Validator | 7/7 PASS (kèm ghi chú `H-08` về hai validator kiểm 0 bản ghi) |

Công cụ tái lập được, đã commit:

    python tests/wp_c2_invariance_tool.py   --raw <raw> --out <payload.json>
    python tests/wp_c2_reachability_tool.py --raw <raw>
    python tests/wp_c2_scenarios.py

## 4. Việc còn lại — ĐÚNG MỘT

**`OWNER_DECISION_REQUIRED`** — chủ dự án đóng vòng đời `WP-C2: IMPLEMENTED → DONE`, ghi vào
`PROJECT/PROJECT_DECISIONS.md` (mẫu `DEC-034` của `WP-B1`).

Lý do agent không tự ghi: `governance/v4/CORE/STATE_AUTHORITY.md` quy định `DONE` do chủ dự án
hoặc completion authority được chỉ định viết.

Completion Gate đã đóng băng của `WP-C2` **không đòi check E2 nào** (bảy E1, một E0), khác
`WP-B1`. Một vòng rà soát độc lập là **lựa chọn thêm** của chủ dự án, không phải điều kiện.

## 5. Trạng thái downstream (không đổi, không tự mở)

`WP-B2` `READY` · `WP-B3` vẫn **`BLOCKED`** (chờ `WP-C2` thật sự `DONE`) · `GATE-B` chưa mở ·
`T-07` NOT READY · `WP-C3` `PLANNED` · `DEC-005` vẫn `PENDING`, vẫn chặn `T-08`.

Lịch sử không đổi: `T-06 = DONE`, V2.1.5 validation `FAILED`, verdict `DO_NOT_BUILD`,
`can_proceed_to_app = false`.

## 6. Hardening ghi nhận (không nằm trên đường găng, không sinh task)

- **H-34** — `market_snapshots` chỉ phủ một phần các nhóm trường DM §4 (thiếu `btc_price` và ba
  nhóm indicator). Giới hạn được tuyên bố, không phải ô trống im lặng.
- **H-35** — trong một dòng snapshot, `execution_state` đo ở bước 12b còn khối vốn đo ở cuối
  nến; hai phương án thay thế đều tệ hơn, đã ghi lý do.

Nhắc lại một khiếm khuyết CÓ SẴN, không do phiên này gây ra: `validate_evidence.py` và
`validate_task_completion.py` glob `TASK-*.md` nên kiểm **0 bản ghi** — `H-08`, thuộc
`CAP-GOVTOOL`, **chưa có owner**. Phiên này không tự sửa và không tự nhận.

## 7. Nếu phiên sau tiếp nhận

Đọc theo thứ tự: `AGENTS.md` → `governance/v4/CORE/` → `PROJECT/PROJECT_PROGRESS.md` →
`docs/tasks/WP-C2-execution-state-machine.md` → `docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md`.

Không có blocker kỹ thuật, không có test đỏ, không có nợ phải trả trước. Điểm vào duy nhất là
quyết định ở §4.
