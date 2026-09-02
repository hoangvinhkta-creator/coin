# S011 — Owner Authority / Ready-Gate Preparation cho T-09B (Firebase)

## Nhận dạng phiên

Ngày:
2026-09-02

Loại phiên:
OWNER AUTHORITY / READY-GATE PREPARATION. **Không phải phiên thực thi.**

Branch:
`claude/t09b-firebase-decision-nnoony`

Baseline SHA:
`c7bf96341032e09f540fe7a00527975714c2331c` (= `origin/main` tại lúc mở phiên)

Task:
`T-09B` — Dựng lưu trữ dữ liệu bền · capability `CAP-WEBAPP` · lineage root `WP-C1`

Owner Decision ghi tại phiên:
`DEC-019` (`OD-WEBAPP-02`)

Ràng buộc phiên (chủ dự án nêu tường minh):
KHÔNG implement Firebase · KHÔNG sửa production code · KHÔNG tạo task ID mới ·
KHÔNG mở repair cycle. **Cả bốn đều được giữ.**

---

## Branch Authority (S000 bước 0)

Chạy `governance/scripts/governance/branch_authority_check.sh` trước khi đọc bất kỳ file state
nào, đúng `AGENTS.md` §7.

Lần chạy đầu: **FAIL** — `attached branch has no upstream`. Nhánh vừa được tạo cục bộ, chưa có
đối ứng trên remote (`git branch --set-upstream-to` báo `origin/claude/t09b-firebase-decision-nnoony
does not exist`, và `git fetch origin` xác nhận nó chưa tồn tại). Đây là thiếu upstream thật, không
phải nhánh cũ hay nhánh sai — nên xử lý bằng cách **tạo upstream**, không bằng cách bỏ qua check.

Sau `git push -u origin claude/t09b-firebase-decision-nnoony`:

    branch            = claude/t09b-firebase-decision-nnoony
    default branch    = main (resolved, not assumed)
    ahead of default  = 0 commit(s)
    divergence age    = 0 day(s) · divergence LOC = 0
    integration       = INTEGRATION_DECISION_REQUIRED = NO
    tracked worktree  = CLEAN
    production diff   = EMPTY

Lưu ý cho phiên sau: nhánh `main` **cục bộ** đang đứng ở `cb75f9d`, cũ hơn `origin/main`
(`c7bf963`). Mọi phép đo delivery budget phải lấy baseline là `origin/main`, không phải `main`
cục bộ — đo nhầm sẽ ra "3 files changed, +170/−25" của phiên T-09A thay vì 0 của phiên này.

---

## Việc đã làm

### 1. Đọc chuỗi thẩm quyền đầy đủ

`AGENTS.md` → `governance/v4/CORE/` (7 file, theo authority order §1) → `PROJECT/PROJECT_PROFILE.md`,
`CAPABILITY_REGISTRY.md`, `PROJECT_PROGRESS.md`, `PRODUCTION_PATHS.md`, `REVIEW_BUDGET_LEDGER.md`,
`HARDENING_BACKLOG.md`, `PROJECT_DECISIONS.md` → `docs/tasks/T-09A-*`, `docs/tasks/WP-C1-*` →
`governance/core/00_SESSION_ORCHESTRATION.md`, `TASK_MODE_STANDARD.md`,
`TASK_READY_GATE_STANDARD.md`, `TASK_COMPLETION_GATE_STANDARD.md`.

Không trả lời câu hỏi trạng thái nào từ trí nhớ hội thoại.

### 2. Đọc production state schema **thật**, không đọc tài liệu mô tả

- `webapp/app_logic.js::emptyState()` (dòng 15-30) — 13 khoá gốc
- `webapp/engine.js::buildLadder()` — schema `ladders[]` và `zones[]`
- `webapp/build_app.js` — `initialState` (đối chiếu chéo, khớp)
- `demo/results3/live_seed.json` — schema `seed` (7 khoá; `history` 420 ngày, `parity` 40 ngày)
- Khối persistence `app_logic.js:820-889`, khối khởi tạo `32-59`, `renderBanners()` `465-508`

### 3. Lập Task Spec cho một ID **đã tồn tại**

`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`. `T-09B` có trong bảng registry chính thức của
`PROJECT_PROGRESS.md` từ RCP-001 (2026-08-23) — đó là hình thức đăng ký thứ nhất theo
`CAPABILITY_MODEL.md` §II.5; file này là hình thức thứ hai cho cùng ID.

    new_registered_task_ids = 0
    proposals_created = 0
    owner_assignment_required_entries_added = 0

`task_registry_snapshot.sh`: `count_roadmap_task_ids = 28`, gồm `T-09B` — đã có trước phiên này.

### 4. Ghi `DEC-019` và cập nhật state canonical

| File | Thay đổi |
|---|---|
| `PROJECT/PROJECT_DECISIONS.md` | Thêm `DEC-019` (append-only, không sửa quyết định cũ) |
| `PROJECT/PROJECT_PROGRESS.md` | Row `T-09B` (giữ `PLANNED`, ghi ràng buộc Firebase + `OWNER_DECISION_REQUIRED`); `Last Updated`; ghi chú cập nhật cho `RSK-001` |
| `PROJECT/CAPABILITY_REGISTRY.md` | Thêm §7 (đính chính danh sách thành viên `CAP-WEBAPP`). Bảng §2 **không đổi**, theo tiền lệ §5/§6 |
| `PROJECT/REVIEW_BUDGET_LEDGER.md` | Thêm `T-09B` vào THÀNH VIÊN §2.2; thêm §2.2.1 xác nhận budget **không đổi** |
| `PROJECT/LO_TRINH_DE_HIEU.md` | **Sinh lại** bằng `sync_easy_roadmap.py`, không sửa tay |

---

## Kết luận kỹ thuật quyết định trạng thái phiên

### Firebase không với tới được từ nơi app đang chạy

Bằng chứng dựng từ nguồn canonical 1 + 2 của `PRODUCTION_PATH_RULE.md` (production
schema/inventory hiện tại + repo config hiện tại), **không** dựa vào lập luận "có thể xảy ra
trong tương lai" mà § Forbidden Justification cấm:

| # | Bằng chứng | Nguồn |
|---|---|---|
| 1 | *"Trang artifact chạy dưới CSP chặn mọi host ngoài (Google Fonts là ngoại lệ duy nhất)"* | `webapp/README.md:13` |
| 2 | *"CSP của trang artifact chặn mọi host ngoài trừ Google Fonts."* | `docs/reviews/S001-discovery-baseline.md:94-95` |
| 3 | Cả file `app_shell.html` chỉ có **một** tham chiếu host ngoài, là `fonts.googleapis.com` | `webapp/app_shell.html:2` |
| 4 | "Lưu lên đám mây" hiện có là capability do host cấp (`window.claude.use(...)`), **không phải** lời gọi mạng | `app_logic.js:863`, `1022`, `1066` |

Hệ quả: Completion Gate **A, B, C, D** (ghi/đọc bền, xoá localStorage vẫn phục hồi, đóng/mở lại
vẫn phục hồi) **không thể PASS** chừng nào app còn chạy trên host hiện tại.

Điều quan trọng phải nói cho đúng: **đây không phải giới hạn của Firebase**, mà là giới hạn của
nơi app chạy. Nó **không** là lý do để đổi khỏi Firebase, và phiên này không đề xuất đổi.

### Vì sao giữ `PLANNED`

`STATE_AUTHORITY.md` dành cho chủ dự án các rào sau, và cả ba đều đang mở:

1. **Runtime host** — quyết định kiến trúc, không phải quyết định thi hành.
2. **Thành phần Firebase** — chỉ thị §12 yêu cầu trả recommendation để duyệt trước implementation.
3. **Danh tính tối thiểu cho security rules** — không có nó thì lựa chọn còn lại là ghi công khai.

Chỉ thị §17 quy định READY chỉ khi *"không còn Owner Decision cần thiết"*. Còn ba → giữ `PLANNED`.

---

## Kết quả kiểm chứng

| Phép đo | Lệnh | Kết quả |
|---|---|---|
| Production diff (khai báo §1 + loại trừ §2) | `git diff --shortstat origin/main -- webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js src/eth_dca_os pyproject.toml pyproject.lock` | **0** |
| Production diff (glob §1 nguyên văn, H-21) | `git diff --shortstat origin/main -- src/eth_dca_os webapp pyproject.toml pyproject.lock` | **0** |
| Routing `T-09B` | `routing_engine.py --d 3 --r 3 --b 3 --a 3 --x 3 --u 3 --v 3 --h 3 --c 3 --f 3 --category accounting_financial --category material_sensitive_data_corruption` | `tier D` / `effort xhigh` — **khớp** metadata lịch sử `PROJECT_PROGRESS.md` dòng 1137 |
| `validate_routing.py` | — | PASS (19 MAJOR task file, 0 manual override) |
| `validate_governance.py` | — | PASS (22 task file, 26 source invariant, 3 budget lineage root, 22 hardening) |
| `validate_structure.py` | — | PASS (27 required path) |
| `validate_project_state.py` | — | PASS |
| `sync_easy_roadmap.py` | — | PASS — ghi `PROJECT/LO_TRINH_DE_HIEU.md` |
| `validate_easy_roadmap.py` | — | PASS |
| `task_registry_snapshot.sh` | — | 28 task ID, `new_registered_task_ids = 0` |

Ghi chú vacuous-validation (`STATE_AUTHORITY.md` § Vacuous Validation): `validate_governance.py`
tự báo `task_files_matching_legacy_glob = 0` — `validate_evidence.py` và
`validate_task_completion.py` vẫn glob `TASK-*.md` nên kiểm **0 bản ghi** trên 22 file task đang
có. Đây là **H-08**, đã có backlog và chưa có owner; phiên này KHÔNG coi nó là PASS và KHÔNG mở
owner mới cho nó.

---

## Bàn giao — việc kế tiếp

### NEXT SMALLEST ACTION

Chủ dự án trả lời **`OD-A`** (runtime host): chọn Firebase Hosting, `file://` cục bộ, hay một
phương án khác. Đây là quyết định **duy nhất** đang chặn; `OD-B` và `OD-B2` chỉ có nghĩa sau khi
`OD-A` được chốt.

Chi tiết ba phương án + bằng chứng: `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md`
§ OWNER_DECISION_REQUIRED. Khuyến nghị của phiên: **A1 — Firebase Hosting**.

### Sau khi có cả ba quyết định

1. Cập nhật §OWNER_DECISION_REQUIRED của Task Spec bằng quyết định thật.
2. Đóng ba ô Ready Gate còn hở (security impact, migration prerequisite, freeze gate).
3. Đóng băng Completion Gate 16/16 REQUIRED **trước** khi viết dòng code đầu tiên.
4. `T-09B`: `PLANNED → READY` (`STATE_AUTHORITY.md`: `READY` do Implementer/Owner viết).
5. Mở phiên thực thi riêng — `MAJOR` mode, Tier D / xhigh, batch review bắt buộc cuối phiên.

### Ràng buộc phiên thực thi phải mang theo

- Firebase là FIXED (`DEC-019`). Nếu gặp giới hạn thật ngăn gate → `OWNER_DECISION_REQUIRED` kèm
  evidence, **không** silently đổi architecture.
- `webapp/engine.js` đổi **0 dòng** (giữ parity, `RSK-002`).
- Không sửa hàm kế toán nào trong danh sách Out of Scope của Task Spec.
- Không backfill `ladders[].month`, không migrate historical state (`DEC-019` điểm 6).
- Không dựng provider abstraction / generic repository "để sau này đổi database" (chỉ thị §11).
- Implementation là **INITIAL IMPLEMENTATION**, không tiêu repair cycle. Budget `CAP-WEBAPP` giữ
  2/0/2 — **đọc** từ `REVIEW_BUDGET_LEDGER.md` §2.2, không tự khai lại.

### Rủi ro mang sang

- `RSK-001` (mất lịch sử giao dịch, mức cao) **chưa giảm**: chưa một dòng production nào đổi.
  Khuyến nghị xuất JSON định kỳ vẫn còn nguyên hiệu lực.
- Cảnh báo historical state của `T-09A`/`DEC-018` vẫn mở và **không** được T-09B đóng.
- `H-08` (glob validator) vẫn chưa có owner.
