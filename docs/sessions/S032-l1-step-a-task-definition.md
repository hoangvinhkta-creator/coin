# S032 — Định nghĩa task cho CoinDCA L-1 bước A (`T-12`)

Ngày: 2026-09-05
Nhánh: `claude/coindca-l1-step-a-task-1ka2zj`
SOURCE HEAD trước phiên: `91cfbba` (== `origin/main`, đầu ra `S031`/`DEC-042`)
Loại phiên: **TASK DEFINITION ONLY** — không thi hành ledger/migration/UI/Firebase/auth,
production diff = **EMPTY**, không tạo `DEC` mới.

---

## 1. Đầu vào và thẩm quyền

`DEC-042` § Consequence để lại đúng một việc cho một phiên riêng: *"Việc mở task ID cho bước A
(Ledger/Data Model v2) thuộc một phiên riêng sau `DEC-042`, không phải hệ quả tự động."* Phiên này
là phiên đó.

Đã xác minh từ thẩm quyền repo trước khi làm bất cứ gì: lát cắt ACTIVE = L-1
(`CAPABILITY_REGISTRY.md` §1.A), `app_development_allowed = true` (`PROJECT_PROFILE.md`),
`DEC-041` + `DEC-042` effective, spec L-1 = `CANONICAL — APPROVED`. Trạng thái lịch sử V2.1.5
(`FAILED` / `DO_NOT_BUILD` / `can_proceed_to_app = false`) **không bị đụng**.

## 2. Đầu ra

| Artifact | Vai trò |
|---|---|
| `docs/tasks/T-12-so-cai-l1-v2-va-derive.md` | **MỚI** — SPEC/TASK, gate FROZEN 14 REQUIRED check |
| `docs/reviews/L1-STEP-A-TASK-DEFINITION.md` | **MỚI** — REVIEW, báo cáo 12 mục |
| `docs/sessions/S032-l1-step-a-task-definition.md` | **MỚI** — handoff (bắt buộc với `MAJOR`) |
| `PROJECT/PROJECT_PROGRESS.md` | STATE — roadmap + snapshot + next session + last updated |
| `PROJECT/LO_TRINH_DE_HIEU.md` | **sinh lại** bằng generator, không sửa tay |
| `PROJECT/CAPABILITY_REGISTRY.md` | `T-12` vào `CAP-WEBAPP`; ghi lại 5 câu hỏi định tuyến |
| `PROJECT/REVIEW_BUDGET_LEDGER.md` | §2.2 THÀNH VIÊN + §2.2.6 — budget KHÔNG đổi |
| `PROJECT/HARDENING_BACKLOG.md` | `H-41` nhận owner `T-12` cho `B1`–`B9`; `H-42`/`H-43` ghi rõ không nhận |

Không tạo `DEC` mới: thẩm quyền đã nằm ở `DEC-042`, và ghi thêm một DEC sẽ là bịa ra một quyết
định Owner không tồn tại.

## 3. Quyết định định tuyến đã ghi lại (để không phải quyết lại)

- **ID = `T-12`** — dãy roadmap chính, ID kế tiếp còn trống. `WP-x` là namespace của `RCP-001`
  dùng để phân rã hạng mục V2.1.5; L-1 bước A không phân rã từ hạng mục nào.
- **Capability = `CAP-WEBAPP`**, lineage root `WP-C1`. Không tạo capability/lineage mới.
- **Hấp thụ không khả dụng** — mọi thành viên `CAP-WEBAPP` đều `DONE`/`CANCELLED`; §II.7 chỉ cho
  hấp thụ tự động vào task còn mở có baseline đã duyệt. Vì vậy câu hỏi 5 (Owner) là đường đúng,
  và Owner đã trả lời trước ở `DEC-042`.
- **Routing D / Fable / max** — tính bằng `routing_engine.py` (`D4 R3 B3 A2 X3 · U3 V4 H4 C3 F4`,
  categories `accounting_financial` + `destructive_migration`), không chọn bằng cảm tính;
  `validate_routing.py` PASS. Điểm chấm được đối chiếu với calibration sẵn có của repo
  (`WP-A6` `D=4`; `T-09A`/`T-09B` `R=3`) chứ không đặt tự do.
- **State = `READY`** — 17/17 mục MAJOR Ready Gate thoả với neo cụ thể, không mục nào thoả bằng
  lời hứa tương lai. Gate đóng băng cùng ngày, trước khi có dòng mã nào.

## 4. Phát hiện kỹ thuật đáng giữ (ảnh hưởng thẳng tới thi hành)

1. **`firestore.rules:96-105` chỉ allow-list `ethdca/state` và `ethdca/seed`.** Mọi `ethdca/*`
   khác bị từ chối. ⇒ sổ `coindca.ledger/2` **phải** nằm bên trong `ethdca/state`; tạo document
   mới sẽ kéo theo sửa rules, tức là bước C. Đã ghi thành ràng buộc + stop condition
   `ARCHITECTURE_CHANGE_REQUIRED` trong file task.
2. **Đường production reachability đã tồn tại**: `webapp/test_firebase_harness.js` (Playwright +
   Chromium + Firestore Emulator + rules thật) chạy trên `app_final.html`. `T-12` **dùng lại**
   nó, không dựng cơ chế reachability thứ hai.
3. **Persistence không tách được** khỏi capability: ledger v2 bắt buộc đổi `schema` đã lưu, nên
   phần persistence tối thiểu nằm trong cùng task, không sinh task anh em.
4. `emptyState()` (`app_logic.js:20-35`) cho biết chính xác các trường cộng dồn phải biến mất, và
   là nguồn dựng fixture legacy **tổng hợp** cho `SC-12`.

## 5. Ranh giới đã giữ

KHÔNG: sửa `src/`, `tests/`, `webapp/`, `docs/spec/`, `firebase.json`, `firestore.rules`,
`pyproject.*`; thi hành ledger/migration/UI/Firebase/auth; tạo quá một task ID; tạo epic/task
con/task anh em/task dọn dẹp; vá `B1`–`B10` riêng lẻ; chạy `T-06` hay thí nghiệm chiến lược; tự
cấp repair budget; khai `GOLDEN_BASELINE_SHA`; dùng dữ liệu tài chính thật của Owner; merge/push
`main`.

    git diff --shortstat 91cfbba..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> rỗng (production diff = EMPTY)

## 6. Validator

    validate_structure        PASS (27 required paths)
    validate_project_state    PASS
    validate_governance       PASS (23 task file, 43 hardening item, 13 production path row)
    validate_routing          PASS (20 MAJOR task file, 0 manual override)
    sync_easy_roadmap         PASS (ghi lại LO_TRINH_DE_HIEU.md)
    validate_easy_roadmap     PASS
    validate_evidence         PASS (0 record — khiếm khuyết glob đã biết, `H-08`)
    validate_task_completion  PASS (0 DONE task — cùng khiếm khuyết glob, `H-08`)

`task_registry_snapshot.sh`: task file 22 → 23; roadmap ID 29 → 30; task ID mới = **1** (`T-12`);
proposal mới = 0; `OWNER_ASSIGNMENT_REQUIRED` mới = 0.

Ghi chú `branch_authority_check.sh`: báo `FAIL — attached branch has no upstream`, đúng với một
nhánh mới chưa push (`ahead = 0`, `divergence LOC = 0`, `INTEGRATION_DECISION_REQUIRED = NO`,
worktree CLEAN, `HEAD == origin/main`). Upstream được đặt ở `git push -u` cuối phiên. Không state
nào bị đọc từ nhánh lạc hậu.

## 7. Bước kế tiếp

Mở **một** phiên thi hành riêng cho `T-12`, nhánh mới tách từ `origin/main`. Chi tiết ràng buộc:
`docs/reviews/L1-STEP-A-TASK-DEFINITION.md` §12 và `PROJECT/PROJECT_PROGRESS.md` § Next Session.

Cần Owner khi tới lúc (không chặn việc bắt đầu): repair budget cho `T-12` nếu vòng rà soát đầu
tiên FAIL (`CAPABILITY_MODEL.md` §II.8), và `IMPLEMENTED → DONE`.
