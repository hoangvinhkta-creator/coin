# S039 — Thi hành `T-14`: CoinDCA L-1 Bước C (Firebase Isolation / Owner Auth / Backup / Recovery)

Phiên: `S039` · Ngày: 2026-09-06 · Nhánh: `claude/t14-step-c-firebase-isolation-xu6nxb`
Loại phiên: **IMPLEMENTATION** — thi hành `T-14`, production diff **KHÔNG** rỗng.
Kết thúc phiên: **`T-14` = IMPLEMENTED — E2_REQUIRED** (KHÔNG `DONE`).

---

## 1. Nguồn thẩm quyền và xác minh trước khi đọc state

    SOURCE HEAD (khởi phiên) = 97434d0ff9eecf1bf70fa167fe362f8d972885ce   (origin/main, khớp
    đúng "Expected main HEAD" của chỉ thị phiên)

`branch_authority_check.sh --expect-branch claude/t14-step-c-firebase-isolation-xu6nxb` (chạy
TRƯỚC khi đọc bất kỳ state file nào, đúng `AGENTS.md` §7 Step 0):

    branch            = claude/t14-step-c-firebase-isolation-xu6nxb
    default branch    = main (resolved, not assumed)
    ahead of default  = 0 commit(s)
    divergence age    = 0 day(s)
    divergence LOC    = 0
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: FAIL — attached branch has no upstream

`FAIL` có **đúng một** nguyên nhân: nhánh mới chưa `git push -u`. Không phải divergence, không
phải `INTEGRATION_DECISION_REQUIRED`. State đọc được đúng là state của `origin/main`.

| Điều kiện | Kết quả | Nguồn (đọc từ file, không từ trí nhớ) |
|---|---|---|
| `T-12` = DONE | ✅ | `PROJECT/PROJECT_PROGRESS.md` § Overall Roadmap; `DEC-046` |
| `T-13` = DONE | ✅ | `PROJECT/PROJECT_PROGRESS.md` § Overall Roadmap; `DEC-048` |
| `T-14` = READY | ✅ | `docs/tasks/T-14-...md` § Metadata; `DEC-049` |
| Không task nào khác đang mở trong `CAP-WEBAPP` | ✅ | `PROJECT/PROJECT_PROGRESS.md` § Current Task Snapshot |
| Ready Gate `T-14` còn hiệu lực | ✅ | 17/17, đối chiếu lại với repo — `docs/reviews/T14-IMPLEMENTATION-REPORT.md` §3 |
| Completion Gate FROZEN 2026-09-06 | ✅ | không sửa một câu chữ nào trong phiên này |

## 2. Việc đã làm

1. Đọc đủ chuỗi thẩm quyền theo `AGENTS.md` §1/§7: `AGENTS.md` → `CLAUDE.md` →
   `PROJECT/PROJECT_PROFILE.md`, `CAPABILITY_REGISTRY.md` (§16), `PROJECT_PROGRESS.md`,
   `PRODUCTION_PATHS.md`, `REVIEW_BUDGET_LEDGER.md` (§2.2.10/§2.2.11), `HARDENING_BACKLOG.md`
   (`H-42`, `H-44`…`H-50`), `PROJECT_DECISIONS.md` (`DEC-049` đầy đủ), spec bước C, task file
   `T-14`, `firestore.rules`, `firebase.json`, `webapp/firebase_config.js`,
   `webapp/app_logic.js`, `webapp/ledger_ui.js`, `webapp/ledger.js`, bộ test hiện có.
2. `T-14`: `READY → IN_PROGRESS` sau khi xác nhận lại Ready Gate.
3. Thi hành bốn khối production (chi tiết: `docs/reviews/T14-IMPLEMENTATION-REPORT.md` §4–§9):
   danh tính Google Sign-In · rules chỉ đổi tài liệu · deploy isolation · backup/recovery.
4. Viết bốn bộ test mới (838 dòng) + mở rộng harness; đưa `npm --prefix webapp test` thành cổng
   release của đường L-1 và làm nó **exit 0** (hấp thụ `H-49`).
5. Chạy toàn bộ regression: T-12 unit + mutation + browser, T-13 Step B UI, safe-merge rules,
   Python `pytest`.
6. `T-14`: `IN_PROGRESS → IMPLEMENTED`; cập nhật task file, PROJECT state, hardening backlog,
   budget ledger, capability registry; viết báo cáo thi hành.

## 3. Quyết định kỹ thuật đáng ghi (không mở lại quyết định đã khoá)

- **Một điểm vào danh tính duy nhất.** Bản đầu cho `signIn()` tự nạp sổ sau khi popup resolve —
  cách đó tạo HAI đường nạp (khôi phục phiên vs đăng nhập mới) có thể lệch nhau. Bản cuối cho
  `onAuthStateChanged` làm chủ; `signIn()`/`signOut()` chỉ đổi trạng thái auth. Kèm bộ đếm
  `authGen` chống đua giữa hai lần đổi danh tính liên tiếp.
- **Không chạm `webapp/app_shell.html`.** File đó KHÔNG nằm trong Expected Touch Area của `T-14`.
  Nút "Đăng nhập bằng Google"/"Đăng xuất" được render từ JS vào `#banners` và `#fbBox` — hai vùng
  vốn đã do JS sinh nội dung — và bắt sự kiện theo uỷ quyền. Không cần sửa vỏ HTML.
- **`firestore.rules`: chỉ khối `COINDCA`, và chỉ comment.** Ghi chú lịch sử ở đầu file (H-23,
  "cross-device OUT OF SCOPE V1") **không** bị sửa dù nay đã lỗi thời — sửa nó sẽ chạm vùng ngoài
  khối `COINDCA` mà `CHECK-T14-02` cấm. Thông tin cập nhật được đặt trong chính khối `COINDCA`,
  nơi nó thuộc về, và trong `webapp/README.md`.
- **`webapp/package.json` phải đổi.** Không nằm trong danh sách "Allowed non-production" viết tay
  của task, nhưng `CHECK-T14-11` gọi đích danh `npm --prefix webapp test` và đòi lệnh đó exit 0
  khi bao gồm suite mới — không có cách nào thoả check mà không sửa `scripts.test`. Thay đổi
  **bắt buộc bởi chính gate**, không phải mở rộng phạm vi tự phát. `package-lock.json` được
  **hoàn nguyên về đúng bản `origin/main`** sau khi `npm install` chạm vào nó.
- **Sáu file test V2.1.5 nghỉ hưu, không xoá, không resurrect UI cũ.** Chuyển sang script
  `test:legacy-v215`; hành vi chúng bảo vệ được phủ lại trên UI Step B bởi
  `webapp/test_t14_persistence.js`. Đúng vế 4 `RE_TRIGGER_CONDITION` của `H-49` và đúng chỉ thị
  phiên §11 ("không resurrect UI V2.1.5 chỉ để làm test cũ xanh").

## 4. Giới hạn bằng chứng — nói thẳng, không che

1. **Emulator ≠ project Firebase thật** của chủ dự án. Cùng giới hạn đã ghi ở `T-09B`/`T-12`/
   `T-13`, không phải giới hạn mới.
2. **Cửa sổ popup Google không hoàn tất được trong sandbox này.** `signInWithPopup()` bắt buộc
   nạp `https://apis.google.com/js/api.js` trước khi mở popup; sandbox chặn toàn bộ mạng ra ngoài
   (đo được: `apis.google.com`, `gstatic.com`, `cdnjs`, `unpkg`, `jsdelivr` đều `000`). Xử lý:
   `PR-AUTH-1` kiểm đúng điều đó (app gọi THẬT đường popup → fail closed), và phiên đăng nhập cho
   các kịch bản còn lại được cấp qua chính SDK thật bằng `GoogleAuthProvider.credential()` +
   `signInWithCredential()` — cơ chế test provider chính thức của Emulator Suite mà Step-C spec
   §15 cho phép. Ghi thành `H-52`.
3. **`C-AS-12` không deploy thật.** Không có Firebase CLI authority trong phiên, và deploy thật
   lên project dùng chung là chính thứ runbook cấm. Cái được chứng minh là cấu hình + tài liệu.

## 5. Bằng chứng chạy (số thật, không dự đoán)

    npm --prefix webapp test                     -> EXIT 0
      node test_t12_ledger.js                    -> PASS
      node test_t12_mutations.js                 -> PASS (7/7 mutant bị diệt, 0 survivor)
      node test_t14_deploy_isolation.js          -> PASS (18 assertion, 0 FAIL)
      node test_t14_rules.js                     -> PASS (31 assertion, 0 FAIL)
        └─ test_shared_rules_merge.js (con)      -> PASS (120 assertion, 0 deviation)
      node test_t14_persistence.js               -> PASS (60 assertion, 14/14 kịch bản)
      node test_t14_backup_restore.js            -> PASS (47 assertion, 6/6 kịch bản)
      node test_t12_browser.js                   -> PASS (17 record, 0 error)
      node test_stepb_ui.js                      -> PASS (AS-01…AS-12, PR-1…PR-6)
    Log đầy đủ (một lần chạy duy nhất, cuối phiên): docs/reviews/evidence/T14/npm-test.log

    Python: .venv (đúng pyproject.lock) -> python -m pytest -q
      -> EXIT 0 — 678/678 test PASS, 0 FAIL
      (678 = tổng `pytest --collect-only -q`; `src/eth_dca_os/**`, `pyproject.toml`,
       `pyproject.lock` đều 0 dòng đổi trong phiên này)
    Log: docs/reviews/evidence/T14/pytest.log

    Validators:
      validate_governance.py        -> PASS
      validate_project_state.py     -> PASS
      validate_structure.py         -> PASS
      validate_routing.py           -> PASS
      validate_easy_roadmap.py      -> PASS
      validate_task_completion.py   -> PASS
      sync_easy_roadmap.py          -> PASS (LO_TRINH_DE_HIEU.md sinh lại)
      branch_authority_check.sh     -> BRANCH_AUTHORITY_PLACEHOLDER

    Change budget (đo bằng git, không cộng tay):
      production (4 file)  -> +194 / −23     (trần frozen +600 / −400 -> TRONG TRẦN)
      lệnh chuẩn PRODUCTION_PATHS.md -> 6 files changed, 462 insertions(+), 77 deletions(-)

## 6. Trạng thái sau phiên

| Mục | Trước `S039` | Sau `S039` |
|---|---|---|
| `T-14` | READY | **IMPLEMENTED — E2_REQUIRED** |
| Completion Gate `T-14` | 12 REQUIRED, NOT_TESTED | **12/12 PASS (E1)** |
| `CAP-WEBAPP` budget | allowed 2 / used 1 / remaining 1 | **KHÔNG ĐỔI** (2/1/1) |
| `H-42` | REQUIRED có owner = `T-14`, chưa đóng | phần REQUIRED đóng ở mức E1; `FB-3` giữ HARDENING; `FB-1` DEFERRED. **`H-42` chưa đóng** |
| `H-49` | hấp thụ vào `CHECK-T14-11`, chưa đóng | `CHECK-T14-11` PASS; suite thay thế đã có; **`H-49` chưa đóng** (chờ `T-14 DONE`) |
| `H-44`…`H-48`, `H-50` | ACTIVE | **nguyên trạng, không chạm** |
| `H-46` (SELL) | ACTIVE | **ACTIVE** — không đường nào của bước C mở SELL |
| `H-41` (cảnh báo tiền thật) | còn hiệu lực | **còn hiệu lực** |
| Hardening mới | — | `H-51`, `H-52` (finding, không phải task) |
| Task ID mới / capability / lineage / proposal | — | **0 / 0 / 0 / 0** |

## 7. Hành động kế tiếp

    NEXT SMALLEST ACTION = mở phiên INDEPENDENT E2 REVIEW cho T-14 (reviewer độc lập, KHÔNG phải
    phiên này), đúng tiền lệ T-12/T-13. Sau E2 PASS: chủ dự án ra Owner Closure
    (IMPLEMENTED -> DONE) — thẩm quyền chủ dự án, không phải của agent.

Chi tiết ràng buộc cho phiên E2: `PROJECT/PROJECT_PROGRESS.md` § Next Session.
