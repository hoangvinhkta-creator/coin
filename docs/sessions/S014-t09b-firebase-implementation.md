# S014 — Thực thi T-09B: persistence bền trên Firebase (`READY → IN_PROGRESS → IMPLEMENTED`)

## Nhận dạng phiên

Session ID:
S014

Task:
`T-09B` — Dựng lưu trữ dữ liệu bền (Firebase) · capability `CAP-WEBAPP` · lineage root `WP-C1`

Task Mode:
MAJOR (Tier D / xhigh, Effective Risk HIGH → batch review bắt buộc cuối phiên)

Project Profile:
PRODUCT

Ngày:
2026-09-02

Branch:
`claude/t09b-firebase-implementation-nz50is` — tạo từ `origin/main` @ BASE
`4502ea6c364910004aebae0cfd046cfd97c0358d` (đúng SHA kỳ vọng của chỉ thị, xác nhận sau `git fetch`).
Branch authority check: lần đầu FAIL vì chưa có upstream → `git push -u` nhánh rỗng tại BASE → PASS
(cùng cách xử lý đã ghi ở S011).

Commit:
`a19d3ad` production · `0d4917a` test/harness/README · (commit state/governance = HEAD của nhánh)

Status:
**IMPLEMENTED.** 16/16 REQUIRED check PASS (E1, Firebase Emulator Suite); batch review PASS,
0 BLOCKING còn lại. **Chưa `DONE`** — thẩm quyền chủ dự án, và cần xác nhận trên project Firebase
thật (chưa tồn tại).

Ràng buộc phiên (tất cả được giữ): không mở lại architecture decision · không sửa Product
Principle · không thêm task ID (29 → 29 theo danh sách trạng thái đầy đủ; công cụ báo 28 → 27 vì `H-22`) · không mở repair cycle ·
không mở rộng scope vì security/enterprise best practice · không merge `main`.

---

## Result

Đường sản phẩm mới, đúng baseline FROZEN của `DEC-020`/`DEC-021`, chạy được end-to-end:

    Browser → Firebase Hosting (firebase.json) → Firebase Anonymous Auth (một owner UID trong
    firestore.rules) → Cloud Firestore ethdca/state + ethdca/seed → app.
    localStorage/sessionStorage = mirror/cache; bản mirror mới hơn được cất riêng chờ chọn.

Nói theo ngôn ngữ chủ dự án: mở web lên là dùng được; mỗi thao tác ghi sổ được đẩy lên Firestore và
chỉ báo *Đã lưu bền · rev N* khi máy chủ đã xác nhận; đóng rồi mở lại (cùng trình duyệt) vẫn tiếp
tục; xoá dữ liệu site (localStorage) không mất sổ; mọi lỗi (chưa cấu hình, không xác thực được,
không nhận diện thiết bị, không đọc được, bản bền hỏng, ghi thất bại, mất mạng) hiện rõ và **khoá ghi
sổ**; không bao giờ ghi đè bản bền bằng bản cũ hơn.

## Subtasks Completed

- Đọc chuỗi thẩm quyền đầy đủ (AGENTS → CORE 7 file → PROJECT → DEC-011/018/019/020/021 →
  Task Spec T-09B → S011/S012/S013 → governance core liên quan). Đọc production source thật để
  xác minh State Inventory: `emptyState()` 13 khoá, `buildLadder()` schema ladder/zone, seed 7 khoá
  — inventory canonical **vẫn khớp**, không drift.
- Production: `webapp/app_logic.js` (khối persistence/init/banner/guard/export-import-wipe; 0 hàm
  kế toán bị chạm), `webapp/app_shell.html`, `webapp/build_app.js`, mới `webapp/firebase_config.js`,
  `firestore.rules`, `firebase.json`, `.gitignore`.
- Test: `webapp/test_firebase_harness.js` (mới), `webapp/test_t09b_persistence.js` (mới), năm test
  cũ chuyển sang harness với `readState()` đọc bản durable + đối chiếu bit-exact; `package.json`
  ghim `firebase 12.18.0`, `firebase-tools 15.28.2`; `webapp/README.md` mục Thiết lập Firebase.
- Batch review: `docs/reviews/T-09B-batch-review.md` — 1 finding CONFIRMED sửa cùng lượt
  (`F-T09B-01`, hai tab stale ghi đè → transaction có điều kiện rev), 4 HARDENING (`H-29..H-32`).
- State canonical: Task Spec (Status + 16 evidence), `PROJECT_PROGRESS.md`, `REVIEW_BUDGET_LEDGER.md`
  §2.2 hàng `0'` + §2.2.4, `CAPABILITY_REGISTRY.md` §10, `HARDENING_BACKLOG.md` H-29..H-32,
  `LO_TRINH_DE_HIEU.md` sinh lại.

## Subtasks Remaining

- **REAL FIREBASE SETUP REQUIRED (chủ dự án):** tạo project, bật Anonymous, tạo Firestore, điền
  `webapp/firebase_config.js`, `node webapp/build_app.js`, `firebase deploy`, mở app ở trình duyệt
  dùng hằng ngày, chép UID vào `firestore.rules`, deploy rules — `webapp/README.md` § Thiết lập
  Firebase. Rồi lặp lại bằng tay CHECK-01/02/03/04/14 trên app thật.
- Chuyển `DONE` (chủ dự án) sau khi xác nhận trên project thật. Không tự đóng `RSK-001`.

## Completion Gate Summary

Required: 16 · PASS: 16 (E1, emulator) · FAIL: 0 · BLOCKED: 0 · NOT_TESTED: 0 trong gate;
**production reachability trên project thật = NOT_TESTED** (ngoài 16 check, ghi ở Task Spec
mục "Thực thi — S014").

## Verification Evidence

| Check ID | Status | Evidence Level | Evidence | Executed By | Timestamp |
|---|---|---|---|---|---|
| CHECK-T09B-01..08, 10, 11, 12, 14, 15, 16 | PASS | E1 (Firebase Emulator Suite) | `node webapp/test_t09b_persistence.js` → 14/14, 285 assertion / 0 FAIL, 0 page error; bằng chứng phía Firebase đọc qua REST độc lập | S014 (agent) | 2026-09-02 |
| CHECK-T09B-09 | PASS | E1 | `test_t09a_accounting.js` 68/68; `test_multi_month_invariant.js` PASS; `test_v01_v02_v03.js` V-01/V-02/V-03 BÁC BỎ — tất cả trên state đã round-trip Firestore (`readState` = durable, bit-exact) | S014 | 2026-09-02 |
| CHECK-T09B-13 | PASS | E1 | `npm --prefix webapp test` 6/6 exit 0 (2m31s); `git diff --stat 4502ea6 -- webapp/engine.js` rỗng | S014 | 2026-09-02 |
| Validators | PASS | E1 | `validate_governance.py` · `validate_structure.py` · `validate_project_state.py` · `validate_routing.py` (19 MAJOR, 0 override) · `sync_easy_roadmap.py` + `validate_easy_roadmap.py` | S014 | 2026-09-02 |

Ghi chú vacuous-validation (`H-08`): `validate_evidence.py`/`validate_task_completion.py` vẫn glob
`TASK-*.md` → kiểm 0 bản ghi; không coi là PASS. `task_registry_snapshot.sh` báo 28 → 27 vì bỏ sót
trạng thái `IMPLEMENTED` (`H-22`, có trước phiên); đếm lại bằng tay với danh sách trạng thái đầy đủ:
**BEFORE 29 = AFTER 29**, diff rỗng — không task ID mới (S013 báo 28 vì dùng chính công cụ này).

## Files Changed

Created:
- `webapp/firebase_config.js`, `firestore.rules`, `firebase.json`
- `webapp/test_firebase_harness.js`, `webapp/test_t09b_persistence.js`
- `docs/reviews/T-09B-batch-review.md`, `docs/sessions/S014-t09b-firebase-implementation.md`

Modified:
- `webapp/app_logic.js`, `webapp/app_shell.html`, `webapp/build_app.js`, `.gitignore`
- `webapp/test_helpers.js`, `webapp/test_app.js`, `webapp/test_zone.js`,
  `webapp/test_v01_v02_v03.js`, `webapp/test_multi_month_invariant.js`,
  `webapp/test_t09a_accounting.js`, `webapp/package.json`, `webapp/package-lock.json`, `webapp/README.md`
- `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` (Status, 16 evidence, Exit Criteria, mục Thực thi)
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/REVIEW_BUDGET_LEDGER.md`, `PROJECT/CAPABILITY_REGISTRY.md`,
  `PROJECT/HARDENING_BACKLOG.md`, `PROJECT/LO_TRINH_DE_HIEU.md` (sinh lại)

Deleted:
- (không)

Không đụng: `webapp/engine.js`, `src/eth_dca_os/**`, `pyproject.*`, `docs/spec/**`, `governance/**`,
`PROJECT/PROJECT_DECISIONS.md`, `PROJECT/PROJECT_PROFILE.md`, `PROJECT/PRODUCTION_PATHS.md`.

## Key Decisions (thi hành, không phải Owner Decision mới)

- **Rules khoá cứng UID + placeholder `OWNER_UID_REQUIRED`**: đúng "khoá cứng một owner UID" của
  `DEC-020`; trước khi Owner điền UID mọi truy cập bị từ chối (mặc định deny). Chuỗi thiết lập: deploy
  → mở app → app hiện UID → chép vào rules → deploy rules. Harness test lặp đúng chuỗi này.
- **Ghi có điều kiện `rev` (transaction)**: sửa `F-T09B-01`; không phải conflict-resolution framework.
- **Bỏ nhúng state/quine trong trang**: nằm trong "phạm vi cần thiết" — giữ chúng là giữ nguồn state
  thứ ba trái CHECK-T09B-16; export chuyển sang `<a download>` (host capability cũ không còn).
- **`validateState()`** = schema + kiểu + không âm + bất biến bảo toàn (contribution = Σbase + Σsmart
  + oppAdded; oppFund = Σ oppAdded) — KHÔNG backfill, KHÔNG suy luận `month` (H-31 ghi giả định).
- **Seed** là tầng 2: nếu nguồn bền chưa có seed nhưng mirror có, dùng mirror và ghi lên ở lần lưu
  kế tiếp (banner "SEED CHƯA BỀN"); seed durable không hợp lệ bị bỏ qua, không ghi đè.
- **Emulator thay project thật** cho E1 vì project chưa tồn tại; phân loại trung thực, không suy ra
  production reachability.

## Risks / Blockers

- `RSK-001`: giảm thiểu **đã được cài đặt và kiểm chứng trên emulator**; **chưa giảm trên thực tế** cho
  tới khi Owner thiết lập project thật và dùng app Firebase thay bản artifact. Kịch bản "đổi máy" vẫn
  mở theo `H-23` (export/import JSON). Không tự đóng risk.
- `H-29` (trần 1 MiB), `H-30` (stale change chỉ trong bộ nhớ), `H-31` (giả định tổng tỷ lệ = 1 khi
  validate), `H-32` (production paths chưa khai ba file mới) — HARDENING có re-trigger.
- Bản artifact cũ vẫn mở được nhưng KHÔNG còn là bản dùng thật; dữ liệu ở đó phải export → import.

## Regression Items

- `npm --prefix webapp test` 6/6; `engine.js` 0 dòng; Python `src/eth_dca_os` 0 dòng (không chạy
  lại pytest vì không đụng — 286 passed tại T-09A vẫn là baseline).
- V-01/V-02/V-03 giữ BÁC BỎ; 68/68 bất biến T-09A trên state đã round-trip.

## Do Not Change Yet

- `webapp/engine.js` (parity `RSK-002`), hàm kế toán trong Out of Scope của T-09B.
- Câu chữ 16 REQUIRED check (FROZEN). `firestore.rules` ngoài việc điền UID.
- Không thêm email/password, Google Sign-In, Cloud Functions, App Check, Analytics (`DEC-021`).

## Next Recommended Session

**NEXT SMALLEST ACTION (chủ dự án, không cần agent):** tạo project Firebase và làm 5 bước trong
`webapp/README.md` § Thiết lập Firebase, rồi lặp lại bằng tay CHECK-01/02/03/04/14 trên app thật.
Sau đó: Owner Decision chuyển `T-09B: IMPLEMENTED → DONE` (kèm cập nhật `RSK-001`), và khai ba
file runtime mới vào `PRODUCTION_PATHS.md` (`H-32`, gom với `H-12`/`H-21`).

Không mở task tiếp theo trong phiên này (chỉ thị §23).

## Files Next Agent Should Read

- `AGENTS.md` → `governance/v4/CORE/` → `PROJECT/PROJECT_PROGRESS.md`
- `docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` (mục "Thực thi — S014" + 16 evidence)
- `docs/reviews/T-09B-batch-review.md`
- `webapp/README.md` § Thiết lập Firebase · `webapp/test_firebase_harness.js`
- `PROJECT/HARDENING_BACKLOG.md` H-23..H-32
