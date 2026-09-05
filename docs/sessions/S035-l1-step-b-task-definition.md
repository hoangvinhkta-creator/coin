# S035 — CoinDCA L-1 Bước B: Task Definition

Phiên: `S035` · Ngày: 2026-09-05 · Nhánh: `claude/coindca-l1-step-b-definition-xvq3b1`
Loại phiên: **PRODUCT / CAPABILITY DEFINITION ONLY** — không thi hành, production diff = EMPTY.

---

## 1. Nguồn thẩm quyền

    SOURCE HEAD (khởi phiên) = c34b801   (origin/main, khớp HEAD kỳ vọng của chỉ thị phiên)

Xác minh trước khi đọc state (`AGENTS.md` §7 Step 0):

| Điều kiện | Kết quả | Nguồn |
|---|---|---|
| `T-12` = DONE | ✅ | `docs/tasks/T-12-so-cai-l1-v2-va-derive.md`, `DEC-046` |
| Independent E2 của `T-12` = PASS | ✅ | `docs/reviews/T12-E2-INDEPENDENT-REVIEW.md` |
| Completion Gate `T-12` = 14/14 PASS | ✅ | `docs/reviews/T12-OWNER-CLOSURE.md` |
| Spec kế toán L-1 = `CANONICAL — APPROVED` | ✅ | header `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` |
| Bước B chưa mở, là Owner decision | ✅ | `docs/reviews/T12-OWNER-CLOSURE.md` §7 |

`branch_authority_check.sh` (đầu phiên): `BRANCH AUTHORITY: FAIL — attached branch has no
upstream`. Tình trạng nhánh mới chưa push, không phải divergence: `ahead of default = 0`,
`divergence LOC = 0`, `INTEGRATION_DECISION_REQUIRED = NO`, worktree CLEAN, production diff
EMPTY. Upstream thiết lập ở lệnh `git push -u` cuối phiên.

## 2. Việc đã làm

1. Đọc đầy đủ chuỗi thẩm quyền: `AGENTS.md`, `PROJECT/PROJECT_PROFILE.md`,
   `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/PROJECT_PROGRESS.md`,
   `PROJECT/HARDENING_BACKLOG.md` (H-42…H-47), `PROJECT/PROJECT_DECISIONS.md` (DEC-040…DEC-046),
   `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2, `PROJECT/PRODUCTION_PATHS.md`,
   `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` (toàn văn), `docs/tasks/T-12-so-cai-l1-v2-
   va-derive.md`, `docs/reviews/T12-OWNER-CLOSURE.md`.
2. Kiểm kê thật UI hiện có (`webapp/app_shell.html`, `webapp/app_logic.js`, `webapp/ledger_ui.js`,
   `webapp/engine.js`) — xác nhận `ledger_ui.js` là panel L-1 tối giản đang chạy thật, phần lớn
   `app_logic.js`/`app_shell.html` là dead code/markup V2.1.5 không còn được render.
3. Soạn `docs/spec-l1/COINDCA_L1_STEP_B_UX_SPEC.md` (mới) — spec sản phẩm/UX cho Bước B, phủ đủ
   15 mục theo chỉ thị phiên (Navigation, Dashboard, Transaction Entry, History, Edit/Delete,
   Plan/Carry UX, UNKNOWN UX, Mobile, Out of Scope, Acceptance Scenarios, Production
   Reachability), cộng bảng phân loại UI hiện có (REUSE/ADAPT/REMOVE_FROM_L1_PATH/DEFER).
4. Chấm routing bằng `routing_engine.py`: `D3 R3 B3 A2 X3 U2 V3 H3 C3 F3` →
   `tier=C model=Opus effort=xhigh` (category `accounting_financial`).
5. Mở `docs/tasks/T-13-buoc-b-dashboard-giao-dich-lich-su.md` (mới) — Task Mode MAJOR, Scope
   IN/OUT, Expected Touch Area, ràng buộc kiến trúc khoá, change budget, Ready Gate (17/17 tương
   đương), Completion Gate 13 REQUIRED check FROZEN.
6. Ghi `DEC-047` (`PROJECT/PROJECT_DECISIONS.md`) — formalize chỉ thị phiên Owner thành Owner
   Decision: duyệt Step-B spec, mở đúng một task ID (`T-13`).
7. Cập nhật state surfaces: `PROJECT/PROJECT_PROGRESS.md` (Last Updated, roadmap row `T-13`,
   Current Task Snapshot, Session History, Recent Decisions, Next Session),
   `PROJECT/CAPABILITY_REGISTRY.md` §15, `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.9.
8. KHÔNG sửa `PROJECT/PRODUCTION_PATHS.md` — chưa có file runtime mới nào được tạo trong phiên
   này (phiên định nghĩa, không implementation).

## 3. Kết quả

    TASK ID     T-13
    TÊN         CoinDCA L-1 Bước B: Dashboard hằng ngày + Nhập giao dịch/Lịch sử
    FILE        docs/tasks/T-13-buoc-b-dashboard-giao-dich-lich-su.md
    SPEC UX     docs/spec-l1/COINDCA_L1_STEP_B_UX_SPEC.md (CANONICAL — APPROVED, DEC-047)
    MODE        MAJOR
    STATE       NOT_PLANNED -> READY (Ready Gate 17/17 tương đương)
    GATE        Completion Gate 13/13 REQUIRED, FROZEN 2026-09-05
    ROUTING     C / Opus / xhigh — model_score 2.85, effort_score 2.8
                inputs D3 R3 B3 A2 X3 · U2 V3 H3 C3 F3 · category accounting_financial
                floors safety_business:min_C, safety_business:min_high
    CAPABILITY  CAP-WEBAPP (lineage root WP-C1) — không capability mới, không lineage mới
    BUDGET      allowed 2 / used 1 / remaining 1 — KHÔNG đổi (mở task không tiêu chu kỳ)

**Vì sao `T-13` chứ không tách nhỏ thêm.** Owner chỉ thị §11 rõ ràng: "Định nghĩa MỘT capability
Step-B... Đừng tách mỗi màn hình thành một task riêng." Dashboard/History/Entry/Edit-Delete/Plan
UX đều dùng chung một API đã đóng băng (`derive/update/migrate/destructive`) và cùng một IA — bốn
điều kiện của `CAPABILITY_MODEL.md` §II.4 (Independent Capability, Independent Lifecycle, Outside
Capability) KHÔNG thoả cho bất kỳ tách nhỏ nào trong số đó, nên chúng ở lại trong `T-13`.

**Vì sao routing không đạt Tier D như `T-12`.** `T-12` phát minh mô hình kế toán (WAC hai tiền
tệ, lan truyền UNKNOWN, migration nguyên tử) — D=4. `T-13` chỉ tiêu thụ API đó qua UI — không có
công thức tài chính mới, nên D=3, và base score (2.85) đã đủ cho Tier C mà không cần floor nhận
thức (`A>=3&X>=3` không thoả vì A=2).

## 4. Điều KHÔNG làm trong phiên này (đúng chỉ thị "definition only")

- KHÔNG viết một dòng code sản phẩm nào (`webapp/**` không đổi).
- KHÔNG chuyển `T-13` sang `IN_PROGRESS`.
- KHÔNG giải quyết `H-46` (SELL) hay `H-42` (Firebase) — cả hai vẫn mở, Step B chỉ ẩn SELL và
  không chạm Firebase.
- KHÔNG tái sinh Buy Score/regime/ladder/recommendation/tab Research.
- KHÔNG đổi schema `coindca.ledger/2`, ranh giới persistence `ethdca/state`, hay bất kỳ bất biến
  `INV-1`…`INV-15` nào.
- KHÔNG hỏi Owner các câu hỏi thẩm mỹ — mọi lựa chọn UX không đổi phạm vi kế toán/sản phẩm đã
  được quyết trong Step-B spec §16 và ghi vào `DEC-047`.

## 5. Validators chạy trong phiên

Xem log cuối phiên (mục "Validator output" bên dưới, được điền sau khi chạy). Kỳ vọng: PASS trên
routing/roadmap/project-state/governance/structure; `validate_evidence.py`/
`validate_task_completion.py` PASS-vacuous (0 record, glob `TASK-*.md` không khớp quy ước
`T-*.md`/`WP-*.md` của repo — khiếm khuyết đã biết `H-08`, không phải bằng chứng closure cho
phiên này).

## 6. Đường dẫn tiếp theo

`NEXT SMALLEST ACTION` = mở một phiên thi hành riêng cho `T-13` (đúng tiền lệ `T-12` tại S034).
Điều kiện đầy đủ: `PROJECT/PROJECT_PROGRESS.md` § Next Session.
