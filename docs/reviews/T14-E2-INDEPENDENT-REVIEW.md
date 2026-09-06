# T-14 Independent E2 Review

Phiên: `S040` (2026-09-06) — phiên **review độc lập**, không thi hành.
Endpoint: **E2_VERDICT = PASS · T-14 giữ nguyên `IMPLEMENTED` — chờ Owner Closure.**

---

## 1. Executive Summary

12/12 REQUIRED check đóng băng của `T-14` **PASS** ở mức **E1 + E2**. Reviewer tái lập độc lập
toàn bộ cổng release (`npm --prefix webapp test` → **exit 0**) và bổ sung **37 assertion do
reviewer tự viết**, dùng danh tính và ma trận kỳ vọng của riêng reviewer, không dùng lại một
assertion nào của implementer.

Ba kết quả mạnh nhất, kiểm chứng độc lập chứ không nhận lời implementer:

1. **`firestore.rules` không đổi một byte thi hành nào.** Reviewer băm SHA-256 phần phi-comment
   của ruleset trước và sau `T-14`: `78a2bae0…5114b` ở cả hai phía. Diff hoàn toàn là
   comment, và chỉ nằm trong khối `COINDCA`.
2. **Ma trận phân quyền độc lập 20/20 PASS**, gồm cả những dòng implementer **không** kiểm:
   document `ethdca/*` ngoài allowlist bị DENY cho chính Owner; tài khoản Content role `ADMIN`
   vẫn DENY trên sổ cái CoinDCA; ruleset còn placeholder không cấp quyền cho bất kỳ ai.
3. **Restore không thể làm tiền xuất hiện.** Trên sổ tổng hợp do reviewer tự dựng, backup
   round-trip cho state **byte-identical** và `derive()` **byte-identical** (tolerance 0);
   `derivedSnapshot` bị `canonical()` loại bỏ vô điều kiện; mọi trường dẫn xuất chèn thêm ở
   cấp cao nhất bị **từ chối cứng**, không phải âm thầm giữ lại.

`H-52` được xác nhận là **giới hạn môi trường (phương án A)**, không phải khiếm khuyết sản phẩm.
`H-51` được xác nhận là finding thật, đúng mức **HARDENING**, không ảnh hưởng tính đúng đắn của
bằng chứng `T-14`.

Reviewer **không sửa một dòng mã production nào** và **không tiêu repair authority**.

## 2. Reviewer Independence

- Reviewer **không** thi hành `T-14`. Phiên thi hành là `S039`; phiên này là `S040`.
- Mọi kết luận của `docs/reviews/T14-IMPLEMENTATION-REPORT.md` được xử lý như **CLAIM cần kiểm**.
- Bằng chứng của reviewer nằm ở `docs/reviews/evidence/T14-E2/`, chạy lại được:
  - `reviewer-e2-rules-matrix.js` — ma trận phân quyền do reviewer tự viết (20 assertion).
  - `reviewer-e2-restore-semantics.js` — ngữ nghĩa restore/derive trên sổ tổng hợp của reviewer
    (17 assertion).
  - `reviewer-e2-npm-test.log` — log cổng release do **reviewer** chạy, không phải log của `S039`.
- Danh tính dùng trong ma trận của reviewer (`e2-reviewer-owner-9f3a`,
  `e2-reviewer-intruder-71bc`) **khác hẳn** danh tính của implementer (`coindca-owner-sub`,
  `other-google-user-sub`) — không kế thừa trạng thái nào của phiên thi hành.

## 3. Source / Branch / Commit

| Mục | Giá trị | Khớp kỳ vọng |
|---|---|---|
| Repository | `hoangvinhkta-creator/coin` | ĐÚNG |
| Nhánh review | `claude/t14-step-c-firebase-isolation-xu6nxb` | ĐÚNG |
| HEAD được review | `8ad0f13` | ĐÚNG |
| Base thi hành | `origin/main` = `97434d0ff9eecf1bf70fa167fe362f8d972885ce` | ĐÚNG |
| Đã review `main` thay nhánh? | KHÔNG | — |
| Merge `main` vào nhánh? | KHÔNG | — |

Branch authority check (`AGENTS.md` §7 bước 0), chạy TRƯỚC khi đọc bất kỳ state file nào:

    branch            = claude/t14-step-c-firebase-isolation-xu6nxb
    default branch    = main (resolved, not assumed)
    behind upstream   = 0
    ahead of default  = 2 commit(s)
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: PASS

Trạng thái đọc từ file (không từ trí nhớ): `T-12 = DONE` (`DEC-046`), `T-13 = DONE` (`DEC-048`),
`T-14 = IMPLEMENTED` (`S039`), Independent E2 = REQUIRED.

## 4. Scope

Review độc lập E2 cho `T-14` đã đóng băng. Reviewer **KHÔNG**: sửa mã production, thiết kế lại
auth/Firebase, di dời sang project Firebase riêng, bật SELL, đổi kế toán `T-12`, đổi `T-13`, mở
bước D, tạo task ID, tiêu repair authority. Finding ≠ task.

Diff production của chính phiên review = **0** (chỉ thêm `docs/reviews/**`).

## 5. Completion Gate Matrix

Yêu cầu lấy nguyên văn từ `docs/tasks/T-14-buoc-c-firebase-isolation-auth-backup.md` (FROZEN
2026-09-06), không lấy từ chỉ thị phiên.

### CHECK-T14-01 — Google Sign-In thay thế Anonymous Auth làm thẩm quyền danh tính

- **Yêu cầu (nguyên văn, rút gọn):** `initPersistence()` không còn gọi `signInAnonymously()`;
  đăng nhập qua `GoogleAuthProvider`; UID phiên đăng nhập là UID so sánh trong `firestore.rules`;
  đăng xuất/đăng nhập lại cùng tài khoản trả về đúng UID và đọc đúng `ethdca/state` cũ.
- **Tái lập độc lập:** `grep -rn "signInAnonymously" webapp/` → **0 kết quả** trong mã production
  lẫn `app_final.html` đã build (chỉ còn trong chính assertion phủ định của test).
  `webapp/app_logic.js:503` = `signInWithPopup(new firebase.auth.GoogleAuthProvider())`.
  `webapp/app_logic.js:470` = `onAuthStateChanged` là **điểm vào danh tính duy nhất**.
  Kịch bản `CHECK-T14-01` chạy lại: đăng xuất → đăng nhập lại → đúng UID cũ → sổ cũ y hệt.
- **Ca đối kháng:** reviewer grep toàn bộ `app_logic.js` + `ledger_ui.js` tìm nhánh rẽ theo
  `isAnonymous` / `providerId` / `providerData` / `credential` → **không có nhánh nào**. Nghĩa là
  không tồn tại đường hậu-auth thứ hai cho một provider ưu đãi, và cũng chính vì vậy đường
  `signInWithCredential()` của test đi **đúng cùng mã** với `signInWithPopup()` (xem §7).
- **Bằng chứng:** `reviewer-e2-npm-test.log` (`PR-AUTH-0`, `C-AS-01`, `CHECK-T14-01`).
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-02 — `isCoinDcaOwner()` giữ nguyên shape, không mở rộng quyền

- **Yêu cầu:** diff `firestore.rules` chỉ chạm khối `COINDCA` (comment/tài liệu); logic vẫn là
  một biểu thức UID duy nhất; không thêm `delete`; khối Content không đổi một ký tự.
- **Tái lập độc lập (mạnh hơn assertion của implementer):** reviewer băm SHA-256 **toàn bộ phần
  phi-comment, phi-rỗng** của ruleset ở hai commit:

      git show 97434d0:firestore.rules | grep -v '^\s*//' | grep -v '^\s*$' | sha256sum
        -> 78a2bae04068fd8cbf3889f8d8fd7e89455d453ea7b2a44e336add1d1335114b
      git show HEAD:firestore.rules      | grep -v '^\s*//' | grep -v '^\s*$' | sha256sum
        -> 78a2bae04068fd8cbf3889f8d8fd7e89455d453ea7b2a44e336add1d1335114b

  **Trùng khít.** Toàn bộ 21 dòng diff là comment, và `git diff` xác nhận chúng nằm trọn trong
  khối `COINDCA` (hunk duy nhất bắt đầu tại dòng 96).
- **Ca đối kháng:** đọc trực tiếp ruleset — đúng **một** biểu thức so UID
  (`request.auth.uid == "OWNER_UID_REQUIRED"`), **0** rule `delete` trên toàn file, không role,
  không bảng hồ sơ Owner, không `allow write: if request.auth != null` ở bất kỳ đâu trong khối
  CoinDCA.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-03 — Emulator rules matrix 5 kịch bản danh tính PASS

- **Yêu cầu:** Owner ALLOW; ẩn danh DENY; UID xác thực khác DENY; `delete` DENY; hành vi Content
  không đổi so với baseline `DEC-023` (0 deviation).
- **Tái lập độc lập:** reviewer **tự viết** ma trận riêng
  (`reviewer-e2-rules-matrix.js`), nạp **chính `firestore.rules` của repo** vào Firestore Rules
  Emulator với UID của reviewer thay vào placeholder, rồi probe bằng ID token **thật** do Auth
  Emulator ký. **20/20 PASS**:

  | Nhóm | Kịch bản | Kết quả |
  |---|---|---|
  | A | Owner (google.com, đúng UID) READ / UPDATE | ALLOW / ALLOW |
  | A | Owner DELETE | **DENY** |
  | A | Không đăng nhập READ / WRITE | DENY / DENY |
  | A | Ẩn danh READ / WRITE | DENY / DENY |
  | A | Tài khoản Google khác READ / WRITE | DENY / DENY |
  | B | Owner WRITE `ethdca/seed` | ALLOW |
  | B | Owner READ/WRITE `ethdca/rogue` (ngoài allowlist) | **DENY / DENY** |
  | C | Tài khoản Content role `ADMIN` READ/WRITE sổ CoinDCA | **DENY / DENY** |
  | D | Owner CoinDCA DELETE user Content (admin-only) | DENY |
  | E | Ruleset còn placeholder: Owner READ / ẩn danh READ | **DENY / DENY** |

- **Ca đối kháng vượt yêu cầu:** ba nhóm B/C/E là **do reviewer thêm**, implementer không kiểm.
  Nhóm B chứng minh namespace thực sự **bounded** (default-deny hoạt động đúng, không có
  catch-all ngầm). Nhóm C chứng minh vai trò mạnh nhất của Content vẫn không chạm được tiền.
  Nhóm E chứng minh checkout sạch chưa deploy UID thật thì **fail-closed**, không fail-open.
- **Regression Content:** `test_shared_rules_merge.js` chạy lại nguyên văn — **120 assertion,
  0 deviation**, `CONTENT_BEHAVIOR_PRESERVED = YES`, CoinDCA matrix 12/12.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-04 — `firebase.json` khai `hosting.target`

- **Yêu cầu:** khối `hosting` có `target: "coindca"`; tài liệu vận hành ghi lệnh
  `firebase target:apply hosting coindca <site-id>`.
- **Tái lập độc lập:** `git diff 97434d0 HEAD -- firebase.json` = **đúng +1 dòng**
  (`"target": "coindca"`), không dòng nào khác đổi. `webapp/README.md` § Runbook deploy ghi đúng
  lệnh `target:apply`.
- **Ca đối kháng:** reviewer kiểm `hosting.public = "webapp/public"` có tồn tại không —
  `npm run build` (exit 0) sinh `webapp/public/index.html`. Không phải cấu hình treo.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-05 — Runbook deploy rules 3 bước được ghi lại

- **Yêu cầu:** tài liệu mô tả đúng ba bước (test safe-merge → đọc diff thủ công → deploy có điều
  kiện); lệnh khuyến nghị `--only hosting:coindca` / `--only firestore:rules`, không dùng
  `firebase deploy` trần.
- **Tái lập độc lập:** reviewer đọc trực tiếp `webapp/README.md` § Runbook deploy. Ba bước đúng
  thứ tự, đúng nội dung; câu **"không bao giờ chạy `firebase deploy` trần"** hiện diện tường
  minh; cả hai lệnh khuyến nghị đều có scope. Runbook còn ghi thẳng giới hạn thật:
  *"Firestore chỉ có một ruleset cho toàn bộ database — không thể deploy rules riêng cho CoinDCA.
  Cô lập ở đây là thủ tục, không phải cấu hình."*
- **Kết quả: PASS · E2-grade: CÓ.** (phân tích đối kháng đầy đủ ở §10)

### CHECK-T14-06 — Export mang timestamp + schema version + chỉ chứa nguồn sự thật

- **Yêu cầu:** tên file `coindca-ledger-<ISO8601>.json`; JSON có `exportedAt` (ISO 8601) và
  `schemaVersion` (= `CoinLedger.SCHEMA`); `derivedSnapshot` nếu có thì nằm trong khối
  `_meta: "INFORMATIONAL — NOT IMPORTED"`.
- **Tái lập độc lập:** đọc `webapp/ledger_ui.js:62` — `exportPayload()` lấy **cùng một** giá trị
  `L.clock().instant` cho `exportedAt` và cho `stamp()` tên file, nên tên file và nội dung
  **không thể lệch nhau về mặt cấu trúc** (không đọc đồng hồ lần hai). `schemaVersion` lấy từ
  `st.schema` thật, **không mượn** `L.SCHEMA` — nghĩa là backup của một bản durable hỏng vẫn tự
  mô tả trung thực thay vì giả dạng hợp lệ. Đây là lựa chọn thiết kế đúng và reviewer xác nhận
  nó có ý nghĩa thật ở CHECK-T14-08.
- **Ca đối kháng:** reviewer kiểm allowlist canonical trong `webapp/ledger.js:127` —
  `'schema rev nextSeq plan openingPosition events LEGACY_ARCHIVE RESEARCH_ONLY'`. Không có
  đường nào để dữ liệu Content hoặc trường lạ lọt vào `state`.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-07 — Preview + validate bắt buộc trước khi restore ghi đè

- **Yêu cầu:** sau khi đọc file, hiển thị tóm tắt (schemaVersion, số event, khoảng ngày, kết quả
  validate) **TRƯỚC** dialog xác nhận ghi.
- **Tái lập độc lập:** đọc luồng `l1Import.onchange` (`ledger_ui.js:353`). Thứ tự trong mã là bất
  biến: `restorePreview()` (dry-run thuần) → `message(preview.summary)` → `if (!preview.ok)
  return` → `L.destructive(... confirm ...)`. `window.confirm` **không thể** chạy trước
  `message()` vì nằm trong callback của `destructive()` được gọi sau. Suite của implementer đọc
  `#l1Message` đúng tại thời điểm hộp thoại bật lên và thấy đủ bốn thành phần.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-08 — Backup dị dạng bị từ chối, không mutate

- **Yêu cầu:** `schemaVersion` sai hoặc field bắt buộc thiếu/hỏng → restore dừng **TRƯỚC** khi
  ghi Firestore/`localStorage` chính; state hiện tại không đổi (bit-for-bit).
- **Tái lập độc lập:** reviewer viết ma trận dị dạng **của riêng mình** trên `ledger.js` thật
  (`reviewer-e2-restore-semantics.js` nhóm C) — **6/6 bị từ chối**: schema sai, thiếu `events`,
  số vượt miền hợp lệ, `kind` không hợp lệ, trường phi-canonical thừa, `openingPosition` không
  phải object. Tất cả đều ném lỗi từ **chính `L.canonical()`/`L.derive()` của `T-12`**, không
  phải từ một validator thứ hai.
- **Ca đối kháng cấu trúc:** vì `restorePreview()` trả `ok:false` **trước** khi `L.destructive()`
  được gọi, đường dị dạng không bao giờ chạm tới `snapshot`, `confirm` hay `commit`. Suite
  implementer xác nhận đúng điều đó ở tầng UI: **không hộp thoại xác nhận nào bật lên**, durable
  + mirror + `coindca-last-snapshot` đều không đổi một byte.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-09 — Snapshot tự động trước khi restore ghi đè

- **Yêu cầu:** trước `destructive()`/ghi Firestore trên đường restore, tự động tải
  `coindca-before-restore-<ISO8601>.json` chứa state hiện tại + ghi
  `localStorage['coindca-last-snapshot']`.
- **Tái lập độc lập:** đọc `webapp/ledger.js:289`:

      async function destructive(current, operation, hooks) {
        await hooks.snapshot(clone(current));          // <- TRƯỚC
        if (!await hooks.confirm()) return { ok: false, cancelled: true };
        ...

  Reviewer kiểm bằng test riêng (nhóm D): snapshot nhận **đúng** state hiện tại và được gọi
  **trước** `confirm`; huỷ confirm vẫn giữ snapshot. Nghĩa là ngay cả khi Owner đổi ý, đường lùi
  vẫn tồn tại.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-10 — Restore hợp lệ tái tạo đúng trạng thái tài chính canonical

- **Yêu cầu:** `backup hợp lệ → state rỗng/hỏng → restore → ACK → reload → derive()` cho đúng y
  hệt bốn con số dashboard + toàn bộ `DerivedState` (tolerance 0 trên số nguyên VND).
- **Tái lập độc lập:** reviewer dựng **sổ tổng hợp của riêng mình** (opening ETH/USDT/VND/reserve,
  plan `CAPPED_CARRY`, 4 event: `TREASURY`, `TRADE BUY`, `RESERVE`, `PRICE`), derive một lần làm
  baseline:

      ETH qty=136500000  costVnd=88615181  USDT qty=571200000  VND=19000000  reserve=5500000

  Sau serialize → JSON → `L.canonical()`: state **byte-identical**, và `derive()` **byte-identical**
  (`JSON.stringify` bằng nhau, tolerance 0). Ở tầng UI, suite implementer chạy chuỗi đầy đủ
  `backup → Xóa sổ → restore → ACK máy chủ → reload → derive()` và cũng trùng khít.
- **Ca đối kháng — restore có thể làm tiền xuất hiện không?** Reviewer nhồi
  `derivedSnapshot = { ethQty: 999999999, vndBalance: 999999999 }` vào state: `canonical()` xoá nó
  vô điều kiện (`delete s.derivedSnapshot`), state khôi phục vẫn **byte-identical** với bản sạch,
  và `derive()` cho **đúng cùng số tiền**. Nhồi thêm `holdings`/`derived` ở cấp cao nhất: bị
  **từ chối cứng** (không phải âm thầm giữ). Không có đường nào để trường dẫn xuất trở thành thẩm
  quyền phục hồi.
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-11 — Multi-device/mirror-reconcile chạy lại được qua UI Step B

- **Yêu cầu:** kịch bản Step-C spec §9 chạy được bằng một suite executable trỏ vào UI Step B
  hiện hành, và `npm --prefix webapp test` **thoát mã 0** khi bao gồm suite mới.
- **Tái lập độc lập:** reviewer chạy `npm --prefix webapp test` từ `node_modules` cài mới trong
  môi trường của chính mình → **`NPM_TEST_EXIT=0`**, 8 suite, **0 FAIL**.
- **Ca đối kháng — có che giấu gì không?**
  - Sáu file V2.1.5 được kiểm diff so với base: **cả sáu UNCHANGED**. Không file nào bị sửa để
    lấy suite xanh.
  - Grep `.skip` / `xit` / `xdescribe` / `todo` / `deselect` trên toàn bộ suite của cổng release:
    **không có**. Chỉ khớp các dòng `process.exit(1)` xử lý lỗi.
  - `test:legacy-v215` tách riêng đúng như khai báo, sáu file vẫn nằm trên đĩa.
  - Reviewer chạy thử `test_t09b_persistence.js` để xác nhận việc nghỉ hưu là chính đáng: nó thật
    sự không chạy được (`LEGACY_EXIT=1`). **Ghi nhận sai lệch tài liệu — xem `F-T14-E2-01` §20.**
- **Kết quả: PASS · E2-grade: CÓ.**

### CHECK-T14-12 — Production reachability qua Auth Emulator + Firestore Emulator + rules thật

- **Yêu cầu:** kịch bản Step-C spec §15 chạy trên app thật (Step B UI) + Firebase SDK thật + Auth
  Emulator + Firestore Emulator (rules thật của repo, không mock) + ít nhất một ca âm (`C-AS-02`
  hoặc `C-AS-03`) trên cùng hạ tầng.
- **Tái lập độc lập:** reviewer build `app_final.html` (`npm run build`, exit 0), phục vụ qua HTTP
  như Hosting, chạy trên Chromium thật với Firebase SDK compat 12.18.0 thật, Auth Emulator 9099 +
  Firestore Emulator 8080 nạp **đúng `firestore.rules` của repo**. Cả hai ca âm `C-AS-02` (chưa
  đăng nhập) và `C-AS-03` (tài khoản Google khác) chạy trên **cùng** hạ tầng đó và đều DENY với
  app fail-closed. **0 pageerror / 0 console error** trong toàn phiên.
- **Kết quả: PASS · E2-grade: CÓ** (với phân định emulator-substitution ghi rõ ở §18).

---

**Endpoint Completion Gate: 12/12 REQUIRED PASS ở mức E1 + E2.**

## 6. Owner Auth

Kiểm chứng từng điểm bắt buộc của chỉ thị review:

| Yêu cầu | Kết quả | Bằng chứng độc lập |
|---|---|---|
| `signInAnonymously()` không còn là thẩm quyền bền | ĐẠT | 0 lần gọi trong `app_logic.js` và trong `app_final.html` đã build |
| `signInWithPopup(new GoogleAuthProvider())` là đường đăng nhập người dùng | ĐẠT | `app_logic.js:503`; `PR-AUTH-1` bắt được request thật tới `apis.google.com` |
| `onAuthStateChanged` là điểm vào danh tính | ĐẠT | `app_logic.js:470`, điểm vào **duy nhất**; không có đường nạp sổ thứ hai |
| Đăng xuất về trạng thái `SIGNED_OUT` an toàn | ĐẠT | `onAuthChanged(null)` → `resetLedger()` → `SIGNED_OUT`; `hooksCanWrite()` sai |
| Cùng Owner UID nối lại đúng sổ | ĐẠT | `CHECK-T14-01`; UID là hàm của (`providerId`,`sub`), không của IndexedDB |
| Mất `localStorage` không đổi quyền sở hữu | ĐẠT | `T14-CLEAR-STORAGE`, `C-AS-06` (hồ sơ trình duyệt mới) |
| Người dùng xác thực khác KHÔNG được coi là Owner | ĐẠT | `C-AS-03`; ma trận reviewer nhóm A và C (kể cả Content `ADMIN`) |
| Chưa xác thực không đọc/ghi được dữ liệu tài chính | ĐẠT | `C-AS-02`; ma trận reviewer nhóm A |

**Tấn công đã thực hiện và kết quả:**

- **Auth state race.** `onAuthChanged()` tăng `authGen` và truyền `gen` xuống `loadDurable(gen)`;
  hàm này kiểm `live()` (`gen === authGen`) **trước mọi lần đặt phase**. Một lệnh nạp sổ của danh
  tính cũ về muộn **không thể** ghi phase đè lên danh tính mới. Reviewer đọc trực tiếp mã và xác
  nhận `live()` được kiểm ở cả nhánh lỗi lẫn nhánh thành công.
- **Stale auth generation.** `resetLedger()` chạy **ngay đầu** mỗi lần đổi danh tính, xoá sạch
  `state`, `seed`, `durableRev`, `rawDurable`, `diverged`, `staleRev`, `lastAck`. Sổ của UID
  trước không sống sót sang phiên sau (`CHECK-T14-01` khẳng định điều này ở tầng UI).
- **Logout/login nhanh.** Cùng cơ chế `authGen`; `signOut()` không chạm Firestore nên đăng nhập
  lại cho đúng UID và đúng sổ.
- **Sai UID.** `UNRECOGNIZED` — **không** phải "sổ trống". Phân biệt này quan trọng: app không
  bao giờ mời người lạ bắt đầu ghi lên một sổ trống rồi đè lên sổ thật.
- **Credential ẩn danh.** DENY ở rules (ma trận reviewer nhóm A), và app không còn tạo credential
  ẩn danh nào.
- **Thiếu auth.** DENY; `loadDurable()` không được gọi khi `user` là `null`.
- **Auth failure.** `AUTH_FAILED` + khoá ghi. `hooksCanWrite()` đòi `phase === "ONLINE"`, nên mọi
  phase lỗi đều fail-closed.

**Fail-closed được xác nhận:** không tồn tại phase nào cho phép ghi ngoài `ONLINE`, và `ONLINE`
chỉ đạt được sau khi đọc thành công `ethdca/state` với `source: "server"` — cache của SDK **không**
được chấp nhận làm nguồn bền.

## 7. Google Popup / H-52

**Kết luận độc lập: phương án A — giới hạn môi trường, KHÔNG phải khiếm khuyết sản phẩm.**

Reviewer không nhận phân loại của implementer mà kiểm bốn điều:

1. **Lời gọi popup có thật không?** `app_logic.js:503` gọi
   `fb.auth.signInWithPopup(new firebase.auth.GoogleAuthProvider())` — API sản phẩm thật, provider
   thật, không wrapper, không cờ test. `PR-AUTH-1` bấm **đúng nút của app** và bắt được request
   đi tới `apis.google.com/js/api.js`, chứng minh đường popup thật sự được kích hoạt.
2. **Môi trường có chặn thật không?** Reviewer đo trực tiếp, không tin lời:

       apis.google.com/js/api.js  -> HTTP 000   (chặn)
       accounts.google.com        -> HTTP 302   (tới được)
       registry.npmjs.org         -> HTTP 200   (tới được)

   Chỉ đúng host `gapi` bị chặn. Đây là giới hạn mạng của sandbox, không phải lỗi mạng chung và
   cũng không phải cấu hình Firebase sai.
3. **Thất bại có cấp quyền không?** KHÔNG. Bắt lỗi → `AUTH_FAILED` → `hooksCanWrite()` sai → khoá
   ghi, không ghi gì lên Firebase. **Fail closed, không fail open.**
4. **Đường credential của test có bypass authorization không?** KHÔNG.
   `GoogleAuthProvider.credential()` + `signInWithCredential()` là cơ chế test-provider chính
   thức của Emulator Suite; nó cấp một **danh tính federated `google.com` thật** do Auth Emulator
   ký, rồi **vẫn** phải đi qua `firestore.rules` thật. Bằng chứng: trên **cùng** hạ tầng credential
   đó, `C-AS-02`/`C-AS-03` và toàn bộ ma trận 20 dòng của reviewer vẫn DENY đúng chỗ. Credential
   cấp *danh tính*, không cấp *quyền*.

**Có khác biệt hành vi giữa `signInWithCredential()` và `signInWithPopup()` không?** KHÔNG.
Reviewer grep toàn bộ mã production tìm nhánh rẽ theo `providerId` / `isAnonymous` /
`providerData` / `credential`: **không có nhánh nào**. Cả hai đường đều kết thúc ở cùng
`onAuthStateChanged` → `onAuthChanged()` → `loadDurable()`. Sau thời điểm cấp credential, mã chạy
là **cùng một mã**, từng dòng.

**Có fallback ẩn làm yếu danh tính Owner không?** KHÔNG. Reviewer đọc toàn bộ khối auth: chỉ có
`signIn()`, `signOut()`, `onAuthChanged()`, `loadDurable()`. Không có đường vòng, không có
"nếu popup hỏng thì dùng ẩn danh", không có ghi đè UID từ `localStorage`, không có tham số URL
nào đặt được danh tính.

**Phân loại chính xác:** khả năng tới được của sản phẩm thật **được thiết lập tới mức bằng chứng
môi trường cho phép** — mã đúng, provider đúng, thất bại fail-closed đúng. Phần **không** phủ được
bằng bằng chứng tự động là chặng "bấm nút → màn hình đồng ý thật của Google → chọn tài khoản →
popup đóng". Đó là bước Owner phải tự xác nhận **một lần** khi thiết lập. Giữ nguyên
`H-52 = CONFIRMED HARDENING` với `RE_TRIGGER_CONDITION` như đã ghi. Reviewer **không sửa**.

## 8. Firestore Rules

Ma trận độc lập đã trình bày ở §5 (CHECK-T14-03), **20/20 PASS**. Bổ sung bốn xác nhận mà chỉ thị
review đòi riêng:

- **Khối Content có bị đổi ngoài ý muốn không?** KHÔNG — SHA-256 phần thi hành của **toàn bộ file**
  trùng khít trước/sau, nên riêng khối Content chắc chắn không đổi.
- **Có rule permissive toàn project nào được thêm không?** KHÔNG — diff chỉ có comment; không
  `match /{document=**}`, không `allow read, write: if true`, không rule mới nào.
- **Auth CoinDCA có phải Owner-specific, không phải `request.auth != null` không?** ĐÚNG là
  Owner-specific. `isCoinDcaOwner()` = `request.auth != null && request.auth.uid == "<UID>"`. Phần
  `!= null` chỉ là guard chống null-deref, **không** phải điều kiện cấp quyền. Reviewer chứng minh
  bằng thực nghiệm: ba loại danh tính khác nhau đều `request.auth != null` (ẩn danh, Google khác,
  Content `ADMIN`) và **cả ba đều DENY**.
- **`ethdca/state` và `ethdca/seed` còn bounded không?** CÒN. Reviewer probe `ethdca/rogue` với
  chính token Owner: **DENY** cho cả read lẫn write. Default-deny hoạt động; không có catch-all.

`DELETE` giữ nguyên ngữ nghĩa đóng băng: **0** rule `delete` trên toàn file; Owner DELETE bị từ
chối trong thực nghiệm. Đường restore không cần `delete` (dùng `update`/`create`), nên việc giữ
DENY không tạo mâu thuẫn chức năng.

## 9. Content Isolation

| Câu hỏi | Kết quả | Bằng chứng |
|---|---|---|
| Thay đổi rules CoinDCA có phá hành vi Content không? | KHÔNG | `test_shared_rules_merge.js`: 120 assertion, **0 deviation**, `CONTENT_BEHAVIOR_PRESERVED = YES` + SHA-256 trùng khít |
| Người dùng Content có giành được quyền CoinDCA không? | KHÔNG | Reviewer dựng tài khoản Content role `ADMIN` → DENY cả read lẫn write trên `ethdca/state` |
| Có path overlap rộng nào không? | KHÔNG | Khối CoinDCA chỉ match hai document tường minh; Content không có collection tên `ethdca` |
| Có wildcard mới nào đổi collection khác không? | KHÔNG | Diff = comment thuần |

**Quan sát cần ghi trung thực (nhóm D của ma trận reviewer):** Owner CoinDCA — vì đã xác thực —
**đọc được** `users/*` của Content, do chính rules Content khai `allow read: if signedIn()`.
Reviewer kiểm tiếp và xác nhận đây **không** phải hệ quả của `T-14`: danh tính **ẩn danh** trước
`T-14` cũng `signedIn()` và cũng có **đúng** quyền đọc đó. `T-14` đổi *nguồn* UID, không đổi *lớp*
quyền Content mà một danh tính CoinDCA nắm. Owner cũng **không** leo thang được: DELETE user
Content (admin-only) vẫn DENY. Đây là thuộc tính có sẵn của project dùng chung theo `DEC-023`,
không phải hồi quy của bước C. Ghi thành `F-T14-E2-03` (§20), **không BLOCKING**.

## 10. Deploy Isolation

- **`hosting.target = coindca` cấu hình đúng chưa?** RỒI — `firebase.json` khai đúng một khối
  `hosting` gắn target `coindca`.
- **Lệnh deploy khuyến nghị có scope chưa?** RỒI — `--only hosting:coindca` và
  `--only firestore:rules`.
- **`firebase deploy` trần có bị cấm tường minh không?** CÓ — runbook viết thẳng *"không bao giờ
  chạy `firebase deploy` trần"*.
- **Giới hạn rules có được ghi chính xác không?** CÓ — runbook nói đúng sự thật: một ruleset
  project-wide, không target-hoá được, cô lập là **thủ tục** chứ không phải cấu hình. Không tô hồng.

**Phân tích đối kháng — một operator bình thường theo đúng runbook có còn đè được hosting của
Content không?**

Reviewer kết luận **thực tế là không**, vì ba lớp:

1. `firebase.json` khai **đúng một** hosting config và nó **gắn target**. Deploy hosting của repo
   này chỉ có thể trỏ tới site đã map cho target `coindca`.
2. Nếu Owner **chưa** chạy `target:apply`, lệnh `--only hosting:coindca` **báo lỗi và không deploy**
   — fail-closed, không âm thầm rơi về site mặc định.
3. Site của Content được deploy từ cấu hình khác, không nằm trong repo này.

**Rủi ro dư thật sự nằm ở Firestore rules, không ở hosting** — và runbook thừa nhận đúng chỗ đó.
Với dự án cá nhân một người, không CI (`PROJECT_PROFILE.md`), quy trình ba bước (safe-merge test
trên chính ruleset sắp deploy → đọc diff bằng mắt → chỉ deploy khi cả hai đạt) là **tương xứng**
với mức rủi ro hiện tại. Reviewer đồng ý giữ `FB-3` ở mức HARDENING.

**Rủi ro dư thứ hai, đã được runbook nêu và reviewer xác nhận bằng thực nghiệm:** deploy lại từ
checkout sạch mà quên thay `OWNER_UID_REQUIRED` sẽ **tự khoá Owner ra ngoài**. Nhóm E của ma trận
reviewer chứng minh ruleset placeholder không cấp quyền cho bất kỳ ai. Hậu quả là **mất quyền
truy cập tạm thời (fail-closed), không phải lộ dữ liệu**, và khắc phục được bằng một lần deploy
lại. Bước 2 của runbook là chỗ bắt lỗi này.

**Reviewer KHÔNG thực hiện deploy thật lên project Firebase dùng chung.** Không có uỷ quyền Owner
cho việc đó. `C-AS-12` được chấm theo bằng chứng cấu hình + runbook, đúng hợp đồng đóng băng.

## 11. Backup

Reviewer tạo backup từ trạng thái bền tổng hợp do chính mình dựng và kiểm từng điểm hợp đồng:

| Yêu cầu | Kết quả | Ghi chú |
|---|---|---|
| Timestamp tên file khớp `exportedAt` | ĐẠT | `stamp()` nhận **chính** giá trị `exportedAt`, không đọc đồng hồ lần hai — không thể lệch |
| `schemaVersion` tồn tại | ĐẠT | lấy từ `st.schema` thật, không mượn `L.SCHEMA` |
| `exportedAt` là ISO 8601 hợp lệ | ĐẠT | `L.clock().instant` = `Date.toISOString()` |
| Canonical state được giữ **chính xác** | ĐẠT | round-trip **byte-identical** (`JSON.stringify` bằng nhau) |
| `derivedSnapshot` chỉ mang tính tham khảo | ĐẠT | nhãn `_meta: "INFORMATIONAL — NOT IMPORTED"` |
| Không trường dẫn xuất nào thành thẩm quyền phục hồi | ĐẠT | `canonical()` xoá `derivedSnapshot`; trường dẫn xuất khác bị **từ chối cứng** |
| Backup không lẫn dữ liệu Content | ĐẠT | allowlist canonical 8 khoá; không đường nào cho dữ liệu ngoài `ethdca/*` lọt vào |
| Backup không ghi vào repo | ĐẠT | `git status` sạch; backup đi qua `URL.createObjectURL` → tải xuống trình duyệt; `README` cấm commit tường minh |

**So sánh bit-for-bit ở chỗ hợp đồng đòi chính xác:** state khôi phục so với nguồn bền —
`JSON.stringify(L.canonical(wire.state)) === JSON.stringify(s)` → **true**.

## 12. Restore / Recovery

**Đường hợp lệ** được xác nhận đầy đủ và đúng thứ tự:
`backup → preview/validate (dry-run) → snapshot bản hiện tại → ghi bền → ACK máy chủ → reload →
derive() → trạng thái tài chính chính xác`.

**Đường dị dạng** dừng **trước** mọi mutation bền. Reviewer tấn công đủ bảy hướng chỉ thị yêu cầu:

| Tấn công | Kết quả | Nơi bị chặn |
|---|---|---|
| `schemaVersion` sai | TỪ CHỐI | `restorePreview()` trước `destructive()` |
| JSON/object dị dạng | TỪ CHỐI | `JSON.parse` / `keys()` allowlist |
| Event không hợp lệ | TỪ CHỐI | `eventCheck()` của `T-12` |
| Canonical state không đầy đủ | TỪ CHỐI | `canonical()` (thiếu `events`, `openingPosition` sai kiểu) |
| Payload chỉ có phần dẫn xuất | TỪ CHỐI | không có `state`/`schema` hợp lệ → `no(...)` |
| Stale revision | TỪ CHỐI | ghi có điều kiện `rev`; `T14-CONFLICT` PASS |
| Huỷ xác nhận | KHÔNG MUTATE | `destructive()` return trước `operation()`/`commit()` |

Xác nhận bốn điều kiện bắt buộc:

- **Durable không đổi khi restore không hợp lệ:** ĐÚNG — 4 ca dị dạng ở tầng UI cho durable
  "không đổi một byte"; ở tầng Node, 6 ca đều ném lỗi trước khi có state để commit.
- **Mirror không đổi ở nơi cần:** ĐÚNG — `coindca-last-snapshot` và mirror đều không đổi trên
  đường dị dạng (không tới được `restoreSnapshot()`).
- **Snapshot tồn tại trước lệnh ghi phá huỷ:** ĐÚNG — `destructive()` gọi `snapshot` **trước**
  `confirm`, nên snapshot có mặt kể cả khi Owner huỷ.
- **Restore không bỏ qua validate của `T-12`:** ĐÚNG — dùng **chính** `L.canonical()` + `L.derive()`.
  Reviewer grep xác nhận `ledger_ui.js` **không** có phép cộng/trừ/nhân tiền độc lập nào ngoài
  `derive()/update()/migrate()/destructive()` (`PR-6` cũng kiểm điều này).

**Ngữ nghĩa kế toán không đổi.** Không có engine kế toán thứ hai trong mã backup/restore/auth.

## 13. Multi-Device

Reviewer tái lập hành vi đa phiên đóng băng:

| Kịch bản | Kết quả |
|---|---|
| Session A: Owner đăng nhập và ghi dữ liệu canonical | `C-AS-05` PASS — ghi có ACK máy chủ |
| Session B: context/hồ sơ **mới hoàn toàn**, cùng danh tính Owner | `C-AS-06` PASS — cùng sổ máy chủ |
| Reload chính xác | PASS — đọc `source: "server"`, derive lại, trùng khít |
| Logout/login chính xác | `CHECK-T14-01` PASS — đúng UID, đúng sổ |
| `localStorage` bị xoá sạch (+ `sessionStorage`) | `T14-CLEAR-STORAGE` PASS — khôi phục đủ từ Firestore |
| Mirror cục bộ cũ **không** đè được máy chủ | `C-AS-07` PASS |
| Xung đột stale revision bị từ chối | `T14-CONFLICT` PASS |
| Đóng hẳn trình duyệt, mở lại cùng hồ sơ | `T14-RESTART` PASS — phiên Google còn |

**Reviewer KHÔNG chấp nhận "mirror bằng nhau" làm bằng chứng.** Điểm quyết định là `C-AS-07`: khi
mirror cục bộ có `rev` **cao hơn** bản bền và nội dung khác hẳn, app **không** âm thầm để mirror
thắng — nó phát hiện phân kỳ, **khoá ghi**, hiển thị số liệu **của máy chủ**, và chờ người dùng
chọn tường minh. Bản bền phía Firebase **không** bị mirror ghi đè. Máy chủ là thẩm quyền.

Cơ chế nền cũng đúng: `loadDurable()` đọc với `source: "server"` nên cache SDK không bao giờ được
nhận nhầm làm nguồn bền; offline thì báo lỗi rõ và chỉ cho xem mirror ở chế độ **read-only đã đánh
dấu chưa xác nhận**.

## 14. H-49 Persistence Evidence

| Yêu cầu kiểm | Kết quả |
|---|---|
| `npm --prefix webapp test` exit 0 | **ĐẠT** — reviewer chạy độc lập, `NPM_TEST_EXIT=0`, 8 suite, 0 FAIL |
| Luồng persistence Step-B/T-14 hiện hành được diễn tập | **ĐẠT** — 14 kịch bản / 60 assertion qua UI Step B thật |
| UI V2.1.5 **không** bị hồi sinh để lấy test xanh | **ĐẠT** — không file V2.1.5 nào bị sửa; `#tab-setup` vẫn đã gỡ |
| Không skip/deselect hàng loạt che hành vi còn liên quan | **ĐẠT** — grep sạch; sáu file legacy **UNCHANGED** so với base |
| `test:legacy-v215` tách đúng khỏi test sản phẩm hiện hành | **ĐẠT** — script riêng trong `package.json` |

**H-49 có thể đóng chính đáng khi `T-14` đạt `DONE` không? — Có, theo đánh giá của reviewer**, với
một điều kiện về tính chính xác tài liệu:

Điều được khôi phục là **năng lực chạy lại được của bằng chứng persistence trên đường sản phẩm
hiện tại** — đúng vế 4 của `RE_TRIGGER_CONDITION`. Suite mới phủ lại đúng nhóm hành vi mà
`CHECK-T09B-01/02/03/04/10/12/16` bảo vệ (ghi có ACK, reload khớp chính xác, xoá storage, mở lại
trình duyệt, ghi bị rules từ chối, durable hỏng fail-closed, mirror không âm thầm thắng, xung đột
stale). Suite mới **không** sao chép từng assertion của 118 assertion cũ, và điều đó **đúng đắn**:
nhiều assertion cũ đo đại lượng V2.1.5 (pool/ladder/OSCORE) đã bị gỡ khỏi đường sản phẩm theo
thẩm quyền `REMOVE_FROM_L1_PATH`. Implementer đã ghi giới hạn này thẳng thắn.

Điều kiện: cập nhật chữ ký lỗi đã lỗi thời trong `H-49` (xem `F-T14-E2-01` §20).

**Reviewer KHÔNG đóng `H-49`.** Đóng là hệ quả của `T-14 DONE`, thuộc thẩm quyền chủ dự án.

## 15. Accounting Non-Regression

| Yêu cầu | Kết quả | Bằng chứng |
|---|---|---|
| `webapp/ledger.js` không đổi | **ĐẠT — 0 dòng** | `git diff 97434d0 HEAD -- webapp/ledger.js` rỗng |
| Golden fixture không đổi | **ĐẠT — 0 dòng** | `webapp/test_t12_fixtures.js` rỗng; `test_t12_ledger.js`, `test_t12_mutations.js` cũng rỗng |
| SC-01…SC-12 PASS | **ĐẠT** | 13 subtest `ok`, 0 `not ok` |
| INV-1…INV-15 PASS | **ĐẠT** | 15 subtest `ok` |
| Mutation suite diệt đủ mutant | **ĐẠT** | `"killed": 7` / 7 |
| Backup/restore/auth **không** cài engine kế toán thứ hai | **ĐẠT** | restore dùng chính `L.canonical()`/`L.derive()`; `PR-6` xác nhận `ledger_ui.js` không có số học tiền độc lập |
| Restore dùng lại ngữ nghĩa validate/derive canonical | **ĐẠT** | reviewer tái lập ở tầng Node: 6/6 ca dị dạng bị chặn bởi chính validator của `T-12` |

Bổ sung độc lập: reviewer kiểm cả `webapp/engine.js`, `webapp/app_shell.html`,
`webapp/build_app.js` — **cả ba UNCHANGED**.

**Hành vi kế toán KHÔNG đổi. Không FAIL, không STOP.**

## 16. T-13 Non-Regression

`test_stepb_ui.js` (AS-01…AS-12) chạy lại độc lập trong cổng release: **PASS**, 18 dòng PASS,
15 thao tác UI thật được ghi nhận (anti-vacuity), 0 pageerror.

| Điểm kiểm | Kết quả |
|---|---|
| Dashboard còn dùng được sau đăng nhập | ĐẠT — `AS-01/AS-08` bốn số khớp bit-với-bit `derive()` |
| Nhập giao dịch còn dùng được | ĐẠT — `AS-04`, `AS-09` (3 lần chạm từ Tổng quan) |
| Lịch sử còn dùng được | ĐẠT — `AS-05` sửa/xoá qua Lịch sử, `id`/`seq` bất biến (INV-15) |
| Plan/carry còn đúng | ĐẠT — `AS-01/AS-08` gồm `nextPlannedDate/Amount` theo `scheduleDays`/carry |
| Đăng xuất cho trạng thái an toàn | ĐẠT — `SIGNED_OUT`, sổ xoá khỏi bộ nhớ trang, khoá ghi |
| Đăng nhập khôi phục đúng trạng thái UI | ĐẠT — `CHECK-T14-01` |
| SELL vẫn ẩn/không khả dụng | ĐẠT — `AS-10`: grep toàn bộ DOM, **không** tuỳ chọn SELL/Bán ở form hay menu nào; **không** hiển thị realized P&L |

Thay đổi duy nhất chạm suite `T-13` là `test_t12_browser.js` (+5/−1) và đó là **giàn giáo**:
context mới nay bắt đầu ở `SIGNED_OUT` nên phải đăng nhập trước khi tới nhánh OFFLINE. Reviewer
đọc diff và xác nhận **không assertion nào bị đổi hoặc bỏ**.

## 17. C-AS-01…C-AS-14

Tái lập bằng trạng thái/hành động do reviewer kiểm soát, không chỉ chạy lại assertion của
implementer. Cột "Bằng chứng reviewer" ghi phần reviewer **tự dựng**.

| ID | Nội dung | Kết quả | Bằng chứng reviewer |
|---|---|---|---|
| C-AS-01 | Owner đăng nhập Google → truy cập được dữ liệu CoinDCA | PASS | Ma trận riêng nhóm A: UID Owner của reviewer READ/UPDATE ALLOW trên rules thật |
| C-AS-02 | Không đăng nhập → đọc/ghi bị từ chối | PASS | Ma trận riêng nhóm A: unauth READ/WRITE DENY; `C-AS-02` ở tầng UI |
| C-AS-03 | UID xác thực khác → bị từ chối | PASS | Ma trận riêng nhóm A + nhóm C (kể cả Content `ADMIN`) |
| C-AS-04 | Hành vi Content không đổi (safe-merge) | PASS | 120 assertion, 0 deviation + SHA-256 phần thi hành trùng khít |
| C-AS-05 | Owner ghi → ACK → reload → khớp chính xác | PASS | Chạy lại trên hạ tầng của reviewer, 0 pageerror |
| C-AS-06 | Hồ sơ trình duyệt mới → đăng nhập → cùng sổ | PASS | Chạy lại; UID là hàm của (`providerId`,`sub`), không của IndexedDB |
| C-AS-07 | Mirror cũ không đè được sự thật server | PASS | Chạy lại; durable phía Firebase không bị ghi đè |
| C-AS-08 | Export chứa nguồn sự thật canonical, không chứa trường dẫn xuất làm nguồn phục hồi | PASS | Nhóm B của reviewer: `canonical()` xoá `derivedSnapshot`; trường dẫn xuất khác bị từ chối cứng |
| C-AS-09 | Restore hợp lệ → `derive()` đúng như trước | PASS | Sổ tổng hợp của reviewer: state + `derive()` **byte-identical** |
| C-AS-10 | Backup dị dạng → không mutation bền | PASS | Nhóm C của reviewer: 6/6 ca bị từ chối bởi validator `T-12` |
| C-AS-11 | Restore snapshot trước khi ghi đè phá huỷ | PASS | Nhóm D của reviewer: `snapshot` gọi **trước** `confirm`, nội dung = state hiện tại |
| C-AS-12 | Deploy CoinDCA có target không sửa bề mặt deploy Content | PASS | Chấm theo cấu hình + runbook (§10). **KHÔNG deploy thật** — không có uỷ quyền Owner |
| C-AS-13 | Giả định cấu hình liên quan Content không đổi | PASS | `firebase.json` diff = +1 dòng; rules thi hành SHA-256 trùng khít |
| C-AS-14 | Bằng chứng persistence executable thay đúng chỗ `H-49` | PASS | `npm test` exit 0 do reviewer chạy; 6 file legacy UNCHANGED; không skip |

## 18. Production Reachability

Reviewer tái lập đường sản phẩm hiện tại **từ đầu**, trong môi trường của chính mình
(`node_modules` cài mới, build mới, emulator mới):

    app_final.html (build từ app_shell + app_logic + ledger + ledger_ui)
      -> phục vụ qua HTTP như Hosting
      -> Firebase SDK compat 12.18.0 THẬT
      -> Auth Emulator 127.0.0.1:9099 + Firestore Emulator 127.0.0.1:8080
      -> ĐÚNG firestore.rules của repo (không mock, không nới lỏng)
      -> danh tính Owner (federated google.com)
      -> ghi qua UI -> ACK máy chủ
      -> logout/login + hồ sơ trình duyệt mới
      -> reload -> derive() chính xác

**Số liệu báo cáo:**

| Chỉ số | Số lượng |
|---|---|
| Thao tác tài chính qua UI | ≥ 15 thao tác thật ghi nhận (anti-vacuity `AS-12/PR-2`), cộng thêm các lệnh ghi của 14 kịch bản persistence và 6 kịch bản backup/restore |
| Ca auth | 8 (`PR-AUTH-0`, `PR-AUTH-1`, `C-AS-01`, `C-AS-02`, `C-AS-03`, `CHECK-T14-01`, `C-AS-06`, `T14-RESTART`) |
| Ca từ chối phân quyền | 5 (implementer) + **20 (ma trận độc lập của reviewer)** + 12/12 CoinDCA matrix trong safe-merge |
| Ca reload/phiên | 5 (`C-AS-05`, `C-AS-06`, `T14-RESTART`, `T14-CLEAR-STORAGE`, `CHECK-T14-10`) |
| Page error | **0** (console + pageerror rỗng ở cả hai suite trình duyệt của T-14) |
| Persistence equality | Byte-exact ở cả hai tầng: durable ↔ hiển thị (UI) và backup ↔ `derive()` (Node) |
| Tổng assertion cổng release do reviewer chạy | 8 suite, **0 FAIL**, exit 0 |
| Assertion do **reviewer tự viết** | **37** (20 rules matrix + 17 restore semantics), 0 FAIL |

**0 meaningful case = FAIL → KHÔNG áp dụng.** Số ca có nghĩa lớn hơn 0 rất nhiều.

**Phân định ba loại bằng chứng, tách bạch tường minh:**

- **Bằng chứng đường sản phẩm thật:** mã production (`app_logic.js`, `ledger_ui.js`,
  `ledger.js`), `firestore.rules` thật của repo, `firebase.json` thật, `app_final.html` do
  `build_app.js` sinh, Firebase SDK thật, UI Step B thật, và **lời gọi `signInWithPopup` thật**.
- **Thay thế bằng emulator:** Firebase Auth và Cloud Firestore chạy trên Emulator Suite thay vì
  project `tinphatcontent` thật. Danh tính Google cấp qua test-provider chính thức của emulator
  (`GoogleAuthProvider.credential()` + `signInWithCredential()`) thay vì popup hoàn tất.
  Rules là rules thật; chỉ placeholder `OWNER_UID_REQUIRED` được thay bằng UID thử nghiệm — đó
  chính là thao tác Owner làm khi deploy.
- **Giới hạn sandbox/mạng:** `apis.google.com` trả HTTP `000` (đo trực tiếp), nên chặng "màn hình
  đồng ý thật của Google" **không** phủ được bằng bằng chứng tự động. Hành vi khi bị chặn là
  **fail-closed** (`AUTH_FAILED`, khoá ghi, không ghi gì). Xem `H-52` §7.
- **Không thực hiện:** deploy thật lên project Firebase dùng chung (không có uỷ quyền Owner).

## 19. H-51

**Xác nhận finding là THẬT.** Reviewer đọc trực tiếp `PROJECT/PRODUCTION_PATHS.md`:

- §1 (production paths) liệt kê `src/eth_dca_os/**`, `webapp/ledger.js`, `ledger_ui.js`,
  `app_logic.js`, `engine.js`, `app_shell.html`, `build_app.js`, `pyproject.toml`,
  `pyproject.lock` — **không** có `firestore.rules`, **không** có `firebase.json`.
- §2 (không phải production path) cũng **không** liệt kê hai file đó. Chúng đơn giản là **chưa
  được phân loại**.
- Lệnh đo budget chuẩn của chính tài liệu (`-- src/eth_dca_os webapp pyproject.toml
  pyproject.lock`) **loại trừ** cả hai.
- Trong khi đó Step-C spec §16 **tính cả hai** vào ước lượng production. Hai tài liệu vì vậy
  không khớp nhau.

**Có ảnh hưởng tính đúng đắn của bằng chứng `T-14` không? — KHÔNG.** Hai lý do độc lập:

1. Implementer đã đo theo cách **chặt hơn** (gộp cả hai file): `4 files changed, 194 insertions,
   23 deletions`, xa dưới trần `+600/−400`. Loại trừ hai file thì con số chỉ nhỏ đi. Kết luận
   change budget không phụ thuộc cách giải quyết sai khác này.
2. `firestore.rules` đã được **Completion Gate đóng băng phủ trực tiếp** qua `CHECK-T14-02` và
   `CHECK-T14-03`. Bảo hiểm gate độc lập với bảng production path, nên không có khoảng trống
   bằng chứng nào cho `T-14`.

**Phân loại: HARDENING, không BLOCKING.** Không thoả điều kiện thứ hai của `BLOCKING`
(`AGENTS.md` §3): không có hậu quả nghiệp vụ nào nằm trong một Completion Gate hay risk register
phụ thuộc vào việc phân loại này. Reviewer **đồng ý** với disposition của implementer.

**Reviewer KHÔNG sửa `PROJECT/PRODUCTION_PATHS.md`** — bảng đó là authority row 8 của
`AGENTS.md` §1; sửa nó là quyết định governance của chủ dự án, không phải dọn dẹp của reviewer.
Mặc định: **report only.** `RE_TRIGGER_CONDITION` hiện có vẫn đúng và đủ.

## 20. Findings

Finding ≠ task. Không finding nào tạo task ID. Không finding nào tiêu repair authority.

### F-T14-E2-01 — Chữ ký lỗi của bộ test legacy ghi trong `H-49` đã lỗi thời trên nhánh `T-14`

Capability: `CAP-WEBAPP` · Phân loại: **HARDENING (chính xác tài liệu)**

`PROJECT/HARDENING_BACKLOG.md` `H-49` mô tả sáu file V2.1.5 "timeout tại đúng một điểm
(`page.setInputFiles: … waiting for locator('#seedFile')`)". Reviewer chạy thử
`test_t09b_persistence.js` trên HEAD `8ad0f13` và quan sát chữ ký **khác**:

    T-09B PERSISTENCE: ERROR Error: waitPhase UNRECOGNIZED,ONLINE timeout;
      now {"phase":"SIGNED_OUT", "uid":null, ...}
    LEGACY_EXIT=1

Nguyên nhân: sau `T-14`, app khởi động ở `SIGNED_OUT` (không còn tự đăng nhập ẩn danh), nên bộ
legacy hỏng **sớm hơn** — ở chặng auth thay vì chặng `#seedFile`.

**Vì sao KHÔNG BLOCKING:** bộ legacy **đã** không chạy được từ trước `T-14` (chính là nội dung của
`H-49`); `T-14` không phá vỡ thứ gì đang chạy. Sáu file **UNCHANGED** so với base và đã chính thức
nghỉ hưu khỏi cổng release sang `test:legacy-v215`. Không REQUIRED check nào phụ thuộc vào chúng —
`CHECK-T14-11` đòi suite **mới** chạy được và `npm test` exit 0, cả hai reviewer đã tái lập.
Đây là sai lệch **mô tả**, không phải sai lệch **hành vi**.

    RE_TRIGGER_CONDITION:
    - `H-49` được sửa đổi hoặc đóng vì bất kỳ lý do nào — nhân dịp đó cập nhật chữ ký lỗi cho
      khớp HEAD hiện tại; HOẶC
    - một phiên tương lai dùng chữ ký `#seedFile` làm căn cứ chẩn đoán và đi tới kết luận sai.

### F-T14-E2-02 — `H-51` xác nhận độc lập là finding thật, giữ HARDENING

Capability: `CAP-WEBAPP` · Phân loại: **HARDENING** — trùng disposition của implementer.

Chi tiết đầy đủ ở §19. Reviewer xác nhận sự không khớp giữa `PRODUCTION_PATHS.md` §1/§2 và
Step-C spec §16 là có thật, đồng thời xác nhận nó **không** ảnh hưởng tính đúng đắn của bằng
chứng `T-14`. Không đổi phân loại, không sửa tài liệu authority.

### F-T14-E2-03 — Owner CoinDCA đọc được `users/*` của Content (thuộc tính có sẵn, không do `T-14`)

Capability: `CAP-WEBAPP` · Phân loại: **HARDENING (quan sát, không hồi quy)**

Ma trận độc lập nhóm D cho thấy Owner CoinDCA — vì đã xác thực — đọc được `users/*` của Content,
do chính rules Content khai `allow read: if signedIn()`.

**Vì sao KHÔNG phải khiếm khuyết của `T-14`:** reviewer kiểm bằng thực nghiệm rằng danh tính
**ẩn danh** trước `T-14` có **đúng cùng** quyền đọc đó. `T-14` đổi *nguồn* UID (Anonymous →
Google), không đổi *lớp* quyền Content mà một danh tính CoinDCA nắm. Không có leo thang: Owner
vẫn DENY trên thao tác admin-only của Content. Đây là thuộc tính có sẵn của quyết định dùng chung
project (`DEC-023`), nằm ngoài Scope IN của `T-14` (mục `O-2` cấm hệ thống multi-user/roles).

Hướng quan trọng — **người dùng Content KHÔNG giành được quyền CoinDCA** — đã được kiểm và DENY
kể cả với role `ADMIN`.

    RE_TRIGGER_CONDITION:
    - dữ liệu Content trở nên nhạy cảm tới mức "mọi người dùng đã đăng nhập đọc được" là rủi ro
      thật; HOẶC
    - CoinDCA và Content được tách sang hai project Firebase (`O-1`, hiện DEFERRED) — khi đó mục
      này tự tiêu biến.

### Dispositions hardening được bảo toàn

Reviewer **không** đổi và **không** đóng bất kỳ mục nào dưới đây:

| ID | Trạng thái sau review E2 |
|---|---|
| `H-42` | GIỮ NGUYÊN — phần REQUIRED đóng ở E1, nay được E2 xác nhận; `FB-3` giữ HARDENING; phần DEFERRED giữ nguyên |
| `H-44` | GIỮ NGUYÊN |
| `H-45` | GIỮ NGUYÊN |
| `H-46` | GIỮ NGUYÊN — SELL vẫn khoá tuyệt đối; `AS-10` xác nhận không lối vào nào trong DOM |
| `H-47` | GIỮ NGUYÊN |
| `H-48` | GIỮ NGUYÊN |
| `H-49` | GIỮ NGUYÊN **HARDENING** — reviewer KHÔNG đóng; đóng là hệ quả của `T-14 DONE` (thẩm quyền Owner). Bổ sung `F-T14-E2-01` |
| `H-50` | GIỮ NGUYÊN |
| `H-51` | GIỮ NGUYÊN **HARDENING** — xác nhận độc lập (`F-T14-E2-02`) |
| `H-52` | GIỮ NGUYÊN **CONFIRMED HARDENING** — reviewer KHÔNG resolve; phân loại A xác nhận (§7) |

Không mục nào đủ ba điều kiện `BLOCKING` (`AGENTS.md` §3: production path hiện hành + hậu quả
nghiệp vụ trong Completion Gate/risk register + bằng chứng tái lập được).

## 21. Final Completion Gate

| Check | Yêu cầu | Kết quả | E1 | E2 |
|---|---|---|---|---|
| CHECK-T14-01 | Google Sign-In thay Anonymous Auth | **PASS** | ✔ | ✔ |
| CHECK-T14-02 | `isCoinDcaOwner()` giữ shape, không mở quyền | **PASS** | ✔ | ✔ |
| CHECK-T14-03 | Emulator rules matrix 5 kịch bản danh tính | **PASS** | ✔ | ✔ |
| CHECK-T14-04 | `firebase.json` khai `hosting.target` | **PASS** | ✔ | ✔ |
| CHECK-T14-05 | Runbook deploy rules 3 bước | **PASS** | ✔ | ✔ |
| CHECK-T14-06 | Export timestamp + schemaVersion + chỉ nguồn sự thật | **PASS** | ✔ | ✔ |
| CHECK-T14-07 | Preview + validate trước khi ghi đè | **PASS** | ✔ | ✔ |
| CHECK-T14-08 | Backup dị dạng bị từ chối, không mutate | **PASS** | ✔ | ✔ |
| CHECK-T14-09 | Snapshot tự động trước khi ghi đè | **PASS** | ✔ | ✔ |
| CHECK-T14-10 | Restore hợp lệ tái tạo đúng trạng thái canonical | **PASS** | ✔ | ✔ |
| CHECK-T14-11 | Multi-device/mirror-reconcile chạy lại được | **PASS** | ✔ | ✔ |
| CHECK-T14-12 | Production reachability qua emulator + rules thật | **PASS** | ✔ | ✔ |

**12/12 REQUIRED PASS ở mức E1 + E2.**

Exit Criteria phụ trợ cũng đạt: 0 defect nghiêm trọng chưa xử lý; 0 REQUIRED security check chưa
xử lý; regression `T-12`/`T-13`/Content đều PASS; `webapp/ledger.js` diff = 0 dòng.

Change budget: production diff `194/−23` trên 4 file, trong trần `+600/−400`. Không
`CHANGE_BUDGET_EXCEEDED`.

Budget review/repair `CAP-WEBAPP`: `allowed 2 / used 1 / remaining 1` — **KHÔNG ĐỔI**. Phiên
review này có production diff = 0 nên không tiêu repair cycle.

## 22. Final E2 Verdict

    E2_VERDICT = PASS

`T-14` giữ nguyên trạng thái **`IMPLEMENTED`**, chờ Owner Closure.

Reviewer **KHÔNG** chuyển `T-14` sang `DONE` — chuyển `IMPLEMENTED → DONE` thuộc thẩm quyền chủ
dự án (`STATE_AUTHORITY.md`), đúng tiền lệ `T-09B`/`T-12`/`T-13`.

Không hard-stop nào được kích hoạt. Không `OWNER_DECISION_REQUIRED` phát sinh từ một REQUIRED
check thất bại (không check nào thất bại). Không repair authority nào được tiêu.

## 23. Exact Owner Next Action

Chủ dự án cần thực hiện **đúng một** quyết định lifecycle, cộng ba việc vận hành đã biết:

1. **Quyết định lifecycle (bắt buộc, chỉ Owner):** ghi một Owner Decision mới trong
   `PROJECT/PROJECT_DECISIONS.md` chuyển **`T-14`: `IMPLEMENTED` → `DONE`**, viện dẫn báo cáo này
   (`docs/reviews/T14-E2-INDEPENDENT-REVIEW.md`, `E2_VERDICT = PASS`, 12/12 REQUIRED ở E1+E2),
   rồi đồng bộ `PROJECT/PROJECT_PROGRESS.md` theo `governance/core/ROADMAP_SYNC_STANDARD.md`.
   Kèm theo đó, `H-49` đủ điều kiện đóng như **hệ quả** của `T-14 DONE` (nên cập nhật luôn chữ ký
   lỗi theo `F-T14-E2-01` khi đóng).

2. **Thao tác thiết lập một lần (ngoài repo, chỉ Owner làm được):**
   - Lấy UID Google thật của mình từ app (nút chép UID), thay vào `OWNER_UID_REQUIRED` trong
     `firestore.rules`, rồi deploy theo **đúng** runbook ba bước
     (`npm --prefix webapp run test:rules-merge` → `git diff -- firestore.rules` → chỉ deploy khi
     cả hai đạt). Reviewer đã chứng minh bằng thực nghiệm rằng quên bước này sẽ **tự khoá Owner
     ra ngoài** (fail-closed, khắc phục được bằng deploy lại).
   - Chạy một lần `firebase target:apply hosting coindca <site-id-coindca>` trước khi deploy
     hosting.
   - **Không bao giờ** chạy `firebase deploy` trần.

3. **Xác nhận thủ công một lần cho `H-52`:** mở app trên trình duyệt thật có mạng, bấm "Đăng nhập
   bằng Google", đi qua màn hình đồng ý thật và xác nhận popup đóng đúng. Đây là chặng duy nhất
   bằng chứng tự động **không** phủ được trong môi trường sandbox, và là chẩn đoán đầu tiên nếu
   sau này không đăng nhập được.

**Lưu ý ranh giới:** cảnh báo "dừng dùng app với tiền thật không giới hạn" (`H-41`, `DEC-041` K.2)
**KHÔNG** tự động được gỡ bởi `T-14 DONE`. Bước C chỉ đóng nhóm điều kiện Firebase/auth/backup.
Bước D (`OWNER_LOCAL_ACCEPTANCE`) và guard SELL (`H-46`) vẫn nằm ngoài và chưa được mở.

---

## Phụ lục A — `INTEGRATION_DECISION_REQUIRED` phát sinh sau khi push báo cáo này

Sau commit của phiên review, `branch_authority_check.sh` báo:

    behind upstream   = 0
    ahead of default  = 3 commit(s)
    divergence age    = 0 day(s)
    divergence LOC    = 5258
    INTEGRATION_DECISION_REQUIRED: loc>5000
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: PASS

**Nguyên nhân:** ngưỡng `loc > 5000` bị vượt bởi **chính artifact của phiên review này**
(báo cáo + log bằng chứng + hai script reviewer). **Production diff = EMPTY** và
`tracked worktree = CLEAN`, nên đây **không** phải khiếm khuyết tích hợp của mã sản phẩm:
`T-14` chỉ đóng góp `194/−23` dòng production, phần còn lại là tài liệu và bằng chứng.

Theo `AGENTS.md` §7, đây là **Owner Decision, không phải cảnh báo được đi qua im lặng**.
Reviewer **không** tự quyết và **không** merge `main`. Chủ dự án cần chọn một trong ba, đúng
khuôn mà script nêu:

1. **integrate/merge** — tích hợp nhánh `T-14` vào `main` sau khi ghi Owner Decision chuyển
   `T-14 → DONE` (lựa chọn tự nhiên nhất: nhánh đã xong việc và đã qua E2);
2. **cut scope** — không áp dụng ở đây (không còn hạng mục nào để cắt);
3. **accept the divergence** kèm lý do và ngày đánh giá lại.

Ghi chú kỹ thuật cho quyết định: divergence LOC ở đây đo **toàn bộ** dòng thay đổi, kể cả
`docs/**` và `PROJECT/**`. Nếu chủ dự án muốn ngưỡng này phản ánh rủi ro tích hợp **mã**, đó là
cùng một câu hỏi phân loại mà `H-51` đã nêu (§19) — có thể xử lý một lần cho cả hai.
