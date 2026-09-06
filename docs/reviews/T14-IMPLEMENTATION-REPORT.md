# T-14 — Báo cáo thi hành: CoinDCA L-1 Bước C (Firebase Isolation / Owner Auth / Backup / Recovery)

Trạng thái kết thúc phiên:
**IMPLEMENTED — E2_REQUIRED**

Phiên:
`S039` (2026-09-06) — phiên thi hành riêng của `T-14`, đúng tiền lệ `T-12` (`S034`) / `T-13`
(`S036`).

---

## 1. Nguồn / base

| Mục | Giá trị |
|---|---|
| Repository | `hoangvinhkta-creator/coin` |
| Base | `origin/main` = `97434d0ff9eecf1bf70fa167fe362f8d972885ce` (đúng HEAD kỳ vọng của chỉ thị phiên) |
| Nhánh thi hành | `claude/t14-step-c-firebase-isolation-xu6nxb` (nhánh được uỷ quyền của phiên; tách trực tiếp từ `origin/main`, 0 commit đi trước) |
| Không merge `main` | ĐÚNG — không có commit merge nào trong phiên |
| Thẩm quyền đọc | `AGENTS.md` §1 → `governance/v4/CORE/*` → `PROJECT/*` → `docs/spec-l1/COINDCA_L1_STEP_C_FIREBASE_ISOLATION_SPEC.md` → `docs/tasks/T-14-...md` |

Branch authority check (`AGENTS.md` §7 bước 0), chạy TRƯỚC khi đọc state:

    bash governance/scripts/governance/branch_authority_check.sh \
      --expect-branch claude/t14-step-c-firebase-isolation-xu6nxb

    branch            = claude/t14-step-c-firebase-isolation-xu6nxb
    default branch    = main (resolved, not assumed)
    ahead of default  = 0 commit(s)
    divergence age    = 0 day(s)
    divergence LOC    = 0
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: FAIL
    - attached branch has no upstream

`FAIL` có **đúng một** nguyên nhân: nhánh mới chưa có upstream (chưa `git push -u`). Đây **không**
phải khiếm khuyết tích hợp: `INTEGRATION_DECISION_REQUIRED = NO`, `ahead of default = 0`,
`divergence LOC = 0`, worktree sạch — nghĩa là state đọc được đúng là state của `origin/main`.
Sau khi push, kiểm tra được chạy lại — kết quả ghi ở §21.

## 2. Trạng thái task trước phiên (đọc từ file, không từ trí nhớ)

`T-12 = DONE` (`DEC-046`) · `T-13 = DONE` (`DEC-048`) · `T-14 = READY` (`DEC-049`) —
xác nhận tại `PROJECT/PROJECT_PROGRESS.md` § Overall Roadmap và § Current Task Snapshot.
Không task nào khác đang mở trong `CAP-WEBAPP`.

## 3. Ready Gate — xác nhận lại TRƯỚC dòng mã production đầu tiên

17/17 mục của Ready Gate `MAJOR` được đối chiếu lại với repo hiện tại, không mục nào phải hạ:

| Mục | Còn hiệu lực? | Đối chiếu thực tế |
|---|---|---|
| Objective / Scope IN / Scope OUT | CÓ | 10 hạng mục `S-C1…S-C10` và 10 mục `O-1…O-10` đều còn ánh xạ đúng vào repo hiện tại |
| Dependencies DONE | CÓ | `T-12`/`T-13`/`T-09B` `DONE`; spec bước C `CANONICAL — APPROVED` |
| Expected touch area | CÓ | các file được liệt kê đều tồn tại đúng đường dẫn đã khai |
| Tác động dữ liệu / bảo mật | CÓ | `ethdca/state` + `ethdca/seed` vẫn là hai document CoinDCA duy nhất trong `firestore.rules` |
| Routing / Tier / Effort | CÓ | router chạy lại cho đúng `tier=C model=Opus effort=xhigh` |
| Completion Gate FROZEN | CÓ | 12 REQUIRED check, freeze 2026-09-06, không sửa một câu chữ nào trong phiên này |

Kết luận: Ready Gate còn hiệu lực → `READY → IN_PROGRESS`. Không mục nào được đánh dấu thoả bằng
lời hứa tương lai.

## 4. Tóm tắt thi hành

Bốn khối thay đổi production, đúng năm file mà Step-C spec §16 dự kiến (một trong năm —
`webapp/firebase_config.js` — hoá ra **không cần đổi**):

1. **Danh tính** (`webapp/app_logic.js`): bỏ Anonymous Auth; `onAuthStateChanged` trở thành điểm
   vào danh tính DUY NHẤT; `signIn()` = `signInWithPopup(new GoogleAuthProvider())`; thêm
   `signOut()`, `resetLedger()`; tách `loadDurable()` khỏi `initPersistence()`; thêm phase
   `SIGNED_OUT`.
2. **Rules** (`firestore.rules`): chỉ comment/tài liệu trong khối `COINDCA`. Logic không đổi một
   ký tự.
3. **Deploy** (`firebase.json` + `webapp/README.md`): `hosting.target: "coindca"` + runbook ba
   bước bắt buộc.
4. **Backup/Recovery** (`webapp/ledger_ui.js`): export có timestamp/`schemaVersion`/khối tham
   khảo đánh dấu; restore có preview + validate dry-run + snapshot riêng + ghi nguyên tử.

Bốn bộ test mới (`webapp/test_t14_*.js`, 838 dòng) + mở rộng harness; `npm --prefix webapp test`
trở thành cổng release của đường L-1 và **thoát mã 0**.

### Ràng buộc đã tôn trọng tuyệt đối

- `webapp/ledger.js` — **0 dòng đổi** (LOCKED `DEC-042`/`DEC-043`).
- `webapp/app_shell.html` — **0 dòng đổi**. Nút "Đăng nhập bằng Google"/"Đăng xuất" được render
  từ JS vào `#banners` và `#fbBox` (hai vùng vốn đã do JS sinh nội dung), nên không cần chạm vỏ
  HTML — vốn KHÔNG nằm trong Expected Touch Area của `T-14`.
- `webapp/engine.js`, `webapp/build_app.js`, `src/eth_dca_os/**` — **0 dòng đổi**.
- Khối Content trong `firestore.rules` — **0 byte đổi** (kiểm bằng SHA-256, §6).
- Không collection/document CoinDCA mới nào (`DEC-043`).
- Không có SELL/realized P&L nào được mở (`H-46` nguyên trạng).

## 5. Owner auth — Google Sign-In

Thiết kế thi hành (Step-C spec §3.2):

    Tải trang -> initPersistence() -> firebase.initializeApp -> onAuthStateChanged(...)
       |- có phiên đã lưu (persistence LOCAL)  -> setUser -> loadDurable() -> ONLINE
       `- không có phiên                        -> SIGNED_OUT (banner + nút, KHOÁ GHI SỔ)
    Bấm "Đăng nhập bằng Google" -> signInWithPopup(new firebase.auth.GoogleAuthProvider())
       -> thành công: onAuthStateChanged bắn -> loadDurable() (KHÔNG có đường nạp thứ hai)
       -> thất bại : AUTH_FAILED, vẫn khoá ghi sổ
    Bấm "Đăng xuất" -> auth.signOut() -> onAuthStateChanged(null) -> resetLedger() -> SIGNED_OUT

Quyết định thiết kế đáng ghi: **một điểm vào danh tính duy nhất**. Ban đầu `signIn()` tự nạp sổ
sau khi popup resolve; cách đó tạo HAI đường nạp (khôi phục phiên và đăng nhập mới) có thể lệch
nhau. Bản cuối cho `onAuthStateChanged` làm chủ, `signIn()`/`signOut()` chỉ đổi trạng thái auth.
Kèm theo là bộ đếm `authGen` chống đua: một lệnh nạp sổ của UID cũ không được phép đặt phase sau
khi danh tính đã đổi.

Một chuỗi hiển thị được đổi và cần nói rõ: nhãn phase `UNRECOGNIZED` từ
`"không nhận diện thiết bị"` thành `"tài khoản không phải chủ sở hữu"` (và banner tương ứng).
Dưới Anonymous Auth, "thiết bị" là danh từ đúng; dưới Google Sign-In nó **sai** — cùng thiết bị
có thể là chủ sở hữu hoặc không, tuỳ tài khoản đăng nhập. Gate FROZEN của `T-09B`
(`CHECK-T09B-11`) đòi *phân biệt rõ* nhánh này với "sổ trống" và với lỗi mạng, và **yêu cầu đó
được giữ nguyên, thậm chí rõ hơn**: phase riêng, banner riêng, khoá ghi sổ, không ghi đè nguồn
bền. Chỉ danh từ mô tả đổi cho đúng cơ chế mới — không có `LEGACY_GATE_COMPATIBILITY_REQUIRED`
vì ngữ nghĩa của gate không bị đổi.

Bảo đảm đã kiểm bằng máy:

| Yêu cầu (chỉ thị phiên §4) | Bằng chứng |
|---|---|
| UID Owner ổn định | `C-AS-06`: cùng tài khoản Google, hồ sơ trình duyệt hoàn toàn mới → CÙNG UID |
| Cùng danh tính qua trình duyệt/thiết bị | `C-AS-06` + `T14-RESTART` |
| Đăng xuất/đăng nhập lại khôi phục đúng sổ | `CHECK-T14-01` |
| Mất `localStorage` không mất quyền sở hữu | `T14-CLEAR-STORAGE` (xoá cả `localStorage` lẫn `sessionStorage` → vẫn đúng sổ) |
| Không hard-code secret | `webapp/firebase_config.js` **0 dòng đổi**; không thêm khoá nào |
| Không coi "đã xác thực" là Owner | `C-AS-03` (tài khoản Google khác DENY) + `test_t14_rules.js` dòng 2b (ẩn danh DENY) + assertion tĩnh "không `signedIn()` trong khối COINDCA" |

Hành vi app Content **không bị chạm**: không có dòng mã Content nào trong repo này, và rules
Content giữ nguyên từng byte (§6).

## 6. Firestore rules

`firestore.rules` diff = **+20 / −1**, toàn bộ nằm trong khối `COINDCA` và toàn bộ là
comment/tài liệu. Kiểm bằng ba lớp (`webapp/test_t14_rules.js` §A):

    SHA-256(header trước khối Content) = 3e93d6a1e4a00c87… (trùng bản trước T-14)
    SHA-256(TOÀN BỘ khối Content)      = ea0489ca598c5fb4… (trùng bản trước T-14)
    Dòng THI HÀNH của khối COINDCA     = trùng đúng danh sách 11 dòng khoá cứng trong test

    function isCoinDcaOwner() {
      return request.auth != null && request.auth.uid == "OWNER_UID_REQUIRED";
    }
    match /ethdca/state { allow read, create, update: if isCoinDcaOwner(); }
    match /ethdca/seed  { allow read, create, update: if isCoinDcaOwner(); }

Ma trận danh tính 5 kịch bản, chạy trên rules THẬT của repo với ID token THẬT do Auth Emulator ký
(`webapp/test_t14_rules.js` §B, 31 assertion):

| # | Actor | `ethdca/state` + `ethdca/seed` | Kết quả |
|---|---|---|---|
| 1 | Owner — UID federated `google.com` đúng | read / create / update | **ALLOW** |
| 2 | Không đăng nhập | read / write | **DENY** |
| 2b | Đã xác thực nhưng ẩn danh | read / write | **DENY** |
| 3 | Tài khoản Google KHÁC | read / write | **DENY** |
| 4 | Mọi actor (kể cả Owner) | `delete` | **DENY** (không có rule `delete`) |
| 4b | Owner | `ethdca/other` (ngoài allow-list) | **DENY** |
| 5 | Owner CoinDCA trên 14 probe Content | read/write các collection Content | **giống hệt** một người dùng đã đăng nhập bình thường — 0 lệch |

Regression Content (`C-AS-04`): `test_shared_rules_merge.js` chạy lại **nguyên văn** như một tiến
trình con — 120 assertion, exit 0, `CONTENT_BEHAVIOR_PRESERVED = YES`, 0 deviation so với baseline
`DEC-023`.

## 7. Deploy isolation

- `firebase.json` thêm đúng MỘT khoá: `"target": "coindca"`. Toàn bộ phần còn lại của file
  (public, ignore, headers, firestore, emulators) trùng ĐÚNG bản trước T-14 — kiểm bằng so sánh
  object trong `webapp/test_t14_deploy_isolation.js` (`C-AS-13`).
- Không hard-code `site` vào repo: ánh xạ target → site là thao tác Owner một lần
  (`firebase target:apply hosting coindca <site-id-coindca>`), ghi trong runbook.
- Lệnh deploy khuyến nghị luôn có scope: `--only hosting:coindca` và `--only firestore:rules`;
  `firebase deploy` trần bị **cấm tường minh** trong tài liệu. Ba chỗ trong `webapp/README.md`
  từng khuyến nghị lệnh trần đã được sửa.
- Runbook ba bước cho rules (`webapp/README.md` § Runbook deploy), kiểm bằng máy đúng thứ tự:
  (1) `npm --prefix webapp run test:rules-merge` PASS → (2) `git diff -- firestore.rules` đọc
  bằng mắt, mọi thay đổi ngoài khối `COINDCA` = dừng và hỏi chủ sở hữu → (3) chỉ deploy sau khi
  (1) và (2) đều đạt. Con trỏ tới runbook cũng được đặt ngay trong comment khối `COINDCA` của
  `firestore.rules`.
- Không tạo CI/CD nào (`O-8`).

## 8. Backup

`webapp/ledger_ui.js::exportPayload()` — nút **Cài đặt → Tải về JSON**:

    coindca-ledger-2026-03-21T05-00-06-175Z.json
    {
      "schemaVersion": "coindca.ledger/2",
      "exportedAt":    "2026-03-21T05:00:06.175Z",
      "state":  { schema, rev, nextSeq, plan, openingPosition, events },   <- nguồn sự thật
      "seed":   ...,
      "derivedSnapshot": { "_meta": "INFORMATIONAL — NOT IMPORTED", ... }  <- KHÔNG bao giờ nhập
    }

- Tên file mang thời điểm, và timestamp trong tên khớp đúng `exportedAt` (kiểm bằng máy).
- `state` bit-exact với bản durable phía Firebase, và chỉ chứa allowlist canonical
  (`events, nextSeq, openingPosition, plan, rev, schema`) — không trường dẫn xuất nào.
- Khối `derivedSnapshot` chỉ để người đọc; `L.canonical()` xoá `derivedSnapshot` vô điều kiện nên
  ngay cả khi nó bị nhét vào trong `state` cũng không vào được nguồn bền (`C-AS-09b`).
- Export là thao tác client-side, tải về máy Owner. **Không** có đường nào ghi backup vào repo;
  `webapp/README.md` nói rõ không commit backup vào Git.
- RPO/RTO khai tường minh trong `webapp/README.md` § Sao lưu và khôi phục (RPO = 30 ngày kể từ
  lần xuất gần nhất; RTO = trong một phiên sử dụng).

## 9. Restore

Trình tự thi hành (`webapp/ledger_ui.js`, `$('l1Import').onchange`):

    đọc file -> restorePreview() [DRY-RUN: JSON.parse + schemaVersion + L.canonical + L.derive]
      |- KHÔNG hợp lệ -> message "TỪ CHỐI KHÔI PHỤC — <lý do cụ thể>"  và DỪNG
      |                  (không snapshot, không hộp thoại, không ghi Firestore, không đổi mirror)
      `- hợp lệ -> message "XEM TRƯỚC KHÔI PHỤC — schemaVersion · N giao dịch · d1 → d2 ·
                            validate PASS · xuất lúc ..."
                -> L.destructive(current, op, { snapshot: restoreSnapshot, confirm, commit })
                     1. restoreSnapshot(): tải coindca-before-restore-<ISO>.json
                        + localStorage['coindca-last-snapshot'] (reason: BEFORE_RESTORE)
                     2. confirm() dựa trên chính bản tóm tắt ở trên
                     3. ghi nguyên tử qua commit -> transaction có điều kiện rev -> ACK máy chủ

Điểm đáng ghi: **preview chạy trước cả snapshot**. Với file dị dạng, test xác nhận **không hộp
thoại xác nhận nào bật lên** — nghĩa là luồng dừng trước cả bước hỏi, chứ không phải "hỏi rồi mới
từ chối". Bốn ca dị dạng đã kiểm: `schemaVersion` sai, trường bắt buộc hỏng kiểu, thiếu mảng
`events`, không phải JSON. Sau mỗi ca: bản durable phía Firebase, mirror `localStorage`,
`coindca-last-snapshot` và số liệu trên màn hình đều **không đổi một byte**.

Khôi phục hợp lệ (`CHECK-T14-10`): backup → `Xóa sổ` (sổ rỗng trên nguồn bền) → restore → ACK →
reload → `derive()` tính ĐỘC LẬP trong Node trên bản durable **trùng khít** bản gốc; toàn bộ số
liệu dashboard/tóm tắt hiển thị y hệt. `state` canonical khớp bản gốc trừ `rev` (bộ đếm ghi bền,
không phải số liệu tài chính — nó phải tiến lên để transaction có điều kiện còn đúng).

**Không có phép tính tài chính nào mới** được thêm ở tầng auth/restore: `restorePreview()` gọi
đúng `CoinLedger.canonical()` + `CoinLedger.derive()`; ghi đi qua đúng `CoinLedger.destructive()`
đã có từ `T-12`.

## 10. Multi-device

Năm dòng của Step-C spec §9, đo qua UI Step B thật:

| Kịch bản | Kỳ vọng | Kết quả |
|---|---|---|
| Reload cùng thiết bị | đọc lại y hệt server state | PASS (`C-AS-05`) |
| Logout → login lại (cùng tài khoản) | cùng UID → cùng document → cùng dữ liệu | PASS (`CHECK-T14-01`) |
| Hồ sơ trình duyệt mới, `localStorage` trống | cùng UID, tải đúng sổ từ server, KHÔNG hiện trạng thái rỗng | PASS (`C-AS-06`) |
| Mirror cũ/lệch (`rev` cao hơn server, nội dung khác) | server thắng; mirror chờ người dùng chọn tường minh | PASS (`C-AS-07`) |
| Ghi xung đột (revision cũ hơn) | từ chối ghi đè, báo rõ, không mất dữ liệu server | PASS (`T14-CONFLICT`) |

Không xây đồng bộ cộng tác thời gian thực (`O-10`): không presence, không merge nhiều writer.

## 11. `H-42`

Disposition sau `T-14` (chi tiết ghi tại `PROJECT/HARDENING_BACKLOG.md` `H-42`):

| Mục | Trạng thái sau `S039` |
|---|---|
| `FB-4` — danh tính không bền | **ĐÓNG (E1)** — Google Sign-In; UID không gắn thiết bị |
| `FB-2` — thiếu khoá site/target | **ĐÓNG (E1)** — `hosting.target: "coindca"` + lệnh deploy có scope + runbook |
| `FB-1` — Anonymous mở cửa Content | **GIẢM THIỂU, chưa đóng** — CoinDCA không còn cần Anonymous, nên provider CÓ THỂ tắt ở Console; đó là thao tác Owner-executed ngoài repo, DEFERRED theo `DEC-049` C |
| `FB-3` — placeholder `OWNER_UID_REQUIRED` | **GIỮ HARDENING** — không tự đóng được trong repo (giá trị thật do Owner deploy); runbook bước 2 là cơ chế bắt lỗi, không phải đóng dứt điểm |
| Backup/recovery (R-4) | **ĐÓNG (E1)** — preview/validate/snapshot/atomic |
| Bằng chứng persistence chạy lại được | **ĐÓNG (E1)** — xem §12 |

**`H-42` KHÔNG được đóng bởi phiên này.** Phần REQUIRED đóng ở mức E1; đóng chính thức là hệ quả
của `T-14 DONE` (thẩm quyền chủ dự án), đúng `RE_TRIGGER_CONDITION` mới của chính `H-42`. Phần
DEFERRED (project Firebase vật lý riêng, tắt Anonymous provider, multi-user/role) **không** được
thi hành và **không** được mở task.

## 12. `H-49`

`CHECK-T14-11` là cơ chế đóng, đúng như `DEC-049` D chỉ định — không mở task riêng.

Thực tế đã làm:

- `webapp/test_t14_persistence.js` (329 dòng, 14 kịch bản, 60 assertion) phủ lại đúng nhóm hành
  vi mà `CHECK-T09B-01/02/03/04/10/12/16` bảo vệ, nhưng đo trên **UI Step B hiện hành** và trên
  danh tính Google của bước C.
- Sáu file test V2.1.5 (`test_app.js`, `test_zone.js`, `test_v01_v02_v03.js`,
  `test_multi_month_invariant.js`, `test_t09a_accounting.js`, `test_t09b_persistence.js`) **được
  giữ nguyên trên đĩa** nhưng chính thức **nghỉ hưu khỏi cổng release**: chúng chuyển sang script
  `test:legacy-v215`. Đây đúng là vế 4 của `RE_TRIGGER_CONDITION` gốc của `H-49` ("bằng chứng
  persistence legacy được nghỉ hưu/thay thế chính thức bằng một suite L-1 mới"). **Không** resurrect
  UI V2.1.5 để làm test cũ xanh — đúng chỉ thị phiên §11.
- `npm --prefix webapp test` **exit 0** với suite mới nằm trong đó
  (`docs/reviews/evidence/T14/npm-test.log`).

Ghi thẳng giới hạn: `test_t14_persistence.js` **không** tái tạo từng assertion một của 118
assertion cũ (nhiều assertion trong số đó đo các đại lượng V2.1.5 — pool/ladder/OSCORE — đã bị
`REMOVE_FROM_L1_PATH` gỡ khỏi đường sản phẩm; tái tạo chúng là chạy theo hành vi lỗi thời, đúng
thứ chỉ thị phiên §19 cấm). Cái được khôi phục là **năng lực chạy lại được của bằng chứng
persistence trên đường sản phẩm hiện tại**.

## 13. Acceptance scenarios `C-AS-01` … `C-AS-14`

| ID | Kịch bản | Kết quả | Bằng chứng |
|---|---|---|---|
| C-AS-01 | Owner đăng nhập Google (UID đúng) → truy cập được | **PASS** | `test_t14_persistence.js` `C-AS-01`; `test_t14_rules.js` dòng 1 |
| C-AS-02 | Không đăng nhập → đọc/ghi bị từ chối | **PASS** | `test_t14_persistence.js` `C-AS-02` (đường sản phẩm) + `test_t14_rules.js` dòng 2/2b (rules) |
| C-AS-03 | UID xác thực khác → bị từ chối | **PASS** | `test_t14_persistence.js` `C-AS-03` + `test_t14_rules.js` dòng 3 |
| C-AS-04 | Hành vi namespace Content không đổi | **PASS** | `test_shared_rules_merge.js` 120 assertion, 0 deviation; + SHA-256 khối Content |
| C-AS-05 | Owner ghi → ACK → reload → khớp chính xác | **PASS** | `test_t14_persistence.js` `C-AS-05` |
| C-AS-06 | Hồ sơ trình duyệt mới → đăng nhập → cùng sổ | **PASS** | `test_t14_persistence.js` `C-AS-06` |
| C-AS-07 | Mirror cũ không ghi đè sự thật server | **PASS** | `test_t14_persistence.js` `C-AS-07` |
| C-AS-08 | Export chứa nguồn sự thật canonical | **PASS** | `test_t14_backup_restore.js` `CHECK-T14-06` |
| C-AS-09 | Restore hợp lệ → `derive()` đúng như trước | **PASS** | `test_t14_backup_restore.js` `CHECK-T14-10` + `C-AS-09b` |
| C-AS-10 | Backup dị dạng → không mutation bền | **PASS** | `test_t14_backup_restore.js` `CHECK-T14-08` (4 ca) |
| C-AS-11 | Restore snapshot trước khi ghi đè | **PASS** | `test_t14_backup_restore.js` `CHECK-T14-09` |
| C-AS-12 | Deploy CoinDCA có mục tiêu, không sửa bề mặt deploy Content | **PASS (giới hạn tường minh)** | `test_t14_deploy_isolation.js`. Không thể deploy thật (không có Firebase CLI authority, và deploy thật lên project dùng chung là chính thứ runbook cấm) — cái được chứng minh là cấu hình + tài liệu, không phải một lần deploy thành công |
| C-AS-13 | Giả định cấu hình liên quan Content không đổi | **PASS** | `test_t14_deploy_isolation.js` (so object `firebase.json` với bản trước T-14) + SHA-256 khối Content trong `firestore.rules` |
| C-AS-14 | Bằng chứng persistence executable thay `H-49` | **PASS** | `test_t14_persistence.js` + `npm --prefix webapp test` exit 0 |

Toàn bộ dùng **dữ liệu tổng hợp** (`test_t12_fixtures.js`, tài khoản Google giả lập
`coindca-owner@example.test` / `other-google-user@example.test`) — không có một đồng dữ liệu thật
nào của chủ dự án trong repo hay trong log.

## 14. Production reachability

Đường chạy thực tế của `webapp/test_t14_persistence.js` và `webapp/test_t14_backup_restore.js`:

    app_final.html (do build_app.js sinh, đúng bundle sẽ deploy)
      -> phục vụ qua HTTP server như Firebase Hosting
      -> Firebase SDK compat 12.18.0 THẬT (bản local cùng version — môi trường chặn gstatic)
      -> Firebase Auth Emulator + Cloud Firestore Emulator
      -> ĐÚNG firestore.rules của repo (nạp qua REST securityRules, UID Owner thay placeholder)
      -> danh tính federated google.com do Auth Emulator ký
      -> ghi giao dịch qua UI thật (form, nút, select) -> ACK máy chủ
      -> đăng xuất/đăng nhập lại  |  hồ sơ trình duyệt mới  |  xoá localStorage+sessionStorage
      -> reload -> derive() (tính độc lập trong Node trên bản durable đọc qua REST)
    + ca âm trên CÙNG hạ tầng: C-AS-02 (chưa đăng nhập) và C-AS-03 (tài khoản Google khác)

Không mock SDK, không mock rules, không gọi hàm nội bộ của app.

### Hai giới hạn phải nói thẳng

1. **Emulator ≠ project thật.** Emulator là Firebase chạy cục bộ (rules engine, Auth, wire
   protocol thật) nhưng không phải project `tinphatcontent` của chủ dự án. Đây là cùng giới hạn
   đã ghi ở `T-09B`/`T-12`/`T-13`, không phải giới hạn mới.
2. **Cửa sổ popup của Google không chạy được trong sandbox này.**
   `signInWithPopup()` của Firebase Auth bắt buộc nạp `https://apis.google.com/js/api.js` (gapi
   iframe = auth event manager) TRƯỚC khi mở popup, kể cả khi đang trỏ vào Auth Emulator. Sandbox
   chạy bộ test chặn toàn bộ mạng ra ngoài (đo được: `apis.google.com`, `gstatic.com`,
   `cdnjs`, `unpkg`, `jsdelivr` đều trả `000`). Hệ quả và cách xử lý:
   - `PR-AUTH-1` kiểm **chính điều đó**: bấm đúng nút của app, quan sát SDK thật sự phát request
     tới `apis.google.com/js/api.js` (chứng minh đường popup production được chạy, không phải một
     nhánh giả), rồi xác nhận app **fail closed** — phase `AUTH_FAILED`, `#saveBtn` bị khoá,
     không document nào được tạo phía Firebase.
   - Phiên đăng nhập dùng cho các kịch bản còn lại được cấp qua **chính SDK thật đang chạy trong
     trang**: `firebase.auth.GoogleAuthProvider.credential(<id token>)` +
     `signInWithCredential()` — cơ chế test provider chính thức của Firebase Emulator Suite, và
     đúng thứ Step-C spec §15 cho phép ("giả lập bằng Auth Emulator identity platform / test
     provider"). App **không** bị gọi hàm nội bộ nào: nó phản ứng qua chính `onAuthStateChanged`
     của production. UID nhận về là UID federated `google.com` thật do Auth Emulator ký, hàm của
     (`providerId`, `sub`) — nên tính chất "cùng tài khoản = cùng UID trên mọi hồ sơ" được chứng
     minh thật, không phải giả định.
   - Cái **chưa** được chứng minh và cần chủ dự án tự xác nhận một lần khi thiết lập: thao tác
     bấm nút → hiện màn hình đồng ý THẬT của Google → chọn tài khoản → popup đóng. Ghi rõ trong
     `webapp/README.md` § Test.

## 15. Non-regression kế toán (T-12)

| Kiểm | Kết quả |
|---|---|
| `webapp/ledger.js` diff so với `origin/main` | **0 dòng** |
| `webapp/test_t12_ledger.js` (SC-01…SC-12, INV-1…INV-15) | PASS |
| `webapp/test_t12_mutations.js` (7 mutant trên mã production) | **7/7 bị diệt, 0 survivor** — bộ mutation vẫn hiệu lực |
| `webapp/test_t12_browser.js` (production reachability P-1…P-6) | PASS, 17/17 record, exit 0 |
| Golden fixture `test_t12_fixtures.js` | **0 dòng đổi** |
| Engine tài chính trùng lặp ở tầng auth/restore | **KHÔNG** — `restorePreview()` gọi đúng `CoinLedger.canonical/derive`; ghi qua `CoinLedger.destructive` |

Không có `ARCHITECTURE_CHANGE_REQUIRED`: không đường nào của bước C cần chạm ngữ nghĩa kế toán.

## 16. Regression khác

| Bộ | Kết quả |
|---|---|
| `webapp/test_stepb_ui.js` (T-13, AS-01…AS-12, PR-1…PR-6) | PASS, exit 0 |
| `webapp/test_shared_rules_merge.js` (DEC-023 baseline) | PASS, 120 assertion, 0 deviation |
| `npm --prefix webapp test` (cổng release L-1, 8 bước) | **exit 0** |
| Python `pytest` (678 test) | **exit 0 — 678/678 PASS, 0 FAIL** |

Ghi chú về môi trường Python: bản clone của phiên ban đầu là **shallow** (50 commit), khiến ba
test dùng `git show <sha cũ>` FAIL vì không có object; `git fetch --unshallow` xử lý dứt điểm.
Một test thứ tư (`test_a1_08_lockfile_matches_installed_environment`) FAIL vì venv tạm cài
phiên bản mới hơn `pyproject.lock`; cài lại đúng từng dòng của lock thì PASS. Cả bốn đều là
**vấn đề môi trường, không phải regression**: `T-14` đổi **0 dòng** trong `src/eth_dca_os/**`,
`pyproject.toml`, `pyproject.lock`.

Một file test cũ phải sửa **giàn giáo** (không phải assertion): `webapp/test_t12_browser.js` —
kịch bản OFFLINE dựng một browser context mới; với Google Sign-In, context mới bắt đầu ở
`SIGNED_OUT` nên phải đăng nhập trước khi tới được nhánh OFFLINE của Firestore. Thêm đúng một
dòng đăng nhập + sửa một nhãn log cho đúng sự thật ("giữ phiên Google" thay vì "giữ Anonymous
UID"). **Không assertion nào bị đổi, bỏ chọn hay làm yếu.**

## 17. Completion Gate — 12/12 REQUIRED

| Check | Trạng thái | Bằng chứng chính |
|---|---|---|
| CHECK-T14-01 — Google Sign-In thay Anonymous | **PASS** (E1) | `test_t14_persistence.js` `PR-AUTH-0`, `C-AS-01`, `CHECK-T14-01` |
| CHECK-T14-02 — rules giữ shape, không mở quyền | **PASS** (E1) | `test_t14_rules.js` §A (SHA-256 + dòng thi hành khoá cứng) |
| CHECK-T14-03 — ma trận 5 kịch bản danh tính | **PASS** (E1) | `test_t14_rules.js` §B + `test_shared_rules_merge.js` |
| CHECK-T14-04 — `firebase.json` khai `hosting.target` | **PASS** (E1) | `test_t14_deploy_isolation.js` |
| CHECK-T14-05 — runbook deploy 3 bước | **PASS** (E1) | `test_t14_deploy_isolation.js` + `webapp/README.md` |
| CHECK-T14-06 — export timestamp + schema + canonical | **PASS** (E1) | `test_t14_backup_restore.js` |
| CHECK-T14-07 — preview + validate trước khi ghi | **PASS** (E1) | `test_t14_backup_restore.js` (đọc `#l1Message` tại đúng thời điểm hộp thoại bật) |
| CHECK-T14-08 — dị dạng bị từ chối, không mutate | **PASS** (E1) | `test_t14_backup_restore.js` (4 ca, so bit-for-bit trước/sau) |
| CHECK-T14-09 — snapshot trước khi ghi đè | **PASS** (E1) | `test_t14_backup_restore.js` |
| CHECK-T14-10 — restore tái tạo đúng trạng thái | **PASS** (E1) | `test_t14_backup_restore.js` (`derive()` tolerance 0) |
| CHECK-T14-11 — persistence evidence chạy lại được | **PASS** (E1) | `test_t14_persistence.js` + `npm test` exit 0 |
| CHECK-T14-12 — production reachability | **PASS** (E1) | `test_t14_persistence.js` (+ giới hạn §14) |

Không REQUIRED check nào được diễn giải lại, làm yếu hay thay bằng tiêu chí dễ hơn. Không có
`COMPLETION GATE CHANGE PROPOSAL` nào được mở — gate giữ nguyên văn bản FROZEN 2026-09-06.

**Evidence Level: E1 cho cả 12.** Independent E2 **CHƯA** chạy → endpoint đúng là
`IMPLEMENTED — E2_REQUIRED`. **KHÔNG** chuyển `DONE`.

## 18. Production diff

    git diff --shortstat origin/main -- webapp/app_logic.js webapp/ledger_ui.js webapp/ledger.js \
      webapp/engine.js webapp/app_shell.html webapp/build_app.js webapp/firebase_config.js \
      firestore.rules firebase.json src/eth_dca_os pyproject.toml pyproject.lock
      -> 4 files changed, 194 insertions(+), 23 deletions(-)

| File | Diff |
|---|---|
| `webapp/app_logic.js` | +93 / −20 |
| `webapp/ledger_ui.js` | +80 / −2 |
| `firestore.rules` | +20 / −1 |
| `firebase.json` | +1 / −0 |
| `webapp/ledger.js`, `webapp/engine.js`, `webapp/app_shell.html`, `webapp/build_app.js`, `webapp/firebase_config.js`, `src/eth_dca_os/**`, `pyproject.*` | **0** |

Lệnh chuẩn của `PROJECT/PRODUCTION_PATHS.md` (bao gồm cả test + README trong `webapp/`, vì bảng
§1 dùng thư mục làm đơn vị đo):

    git diff --shortstat origin/main -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> 6 files changed, 462 insertions(+), 77 deletions(-)

Ghi nhận một sai khác đáng nói giữa hai tài liệu (KHÔNG tự sửa): `PROJECT/PRODUCTION_PATHS.md` §1
**không liệt kê** `firestore.rules` và `firebase.json` là production path, trong khi Step-C spec
§16 tính hai file này vào ước lượng production diff. Báo cáo này đo theo cách CHẶT HƠN (tính cả
hai file), nên kết luận budget không phụ thuộc vào việc giải quyết sai khác đó. Đây là một quan
sát tài liệu, đã ghi ở §20 dưới dạng finding, **không** phải task.

## 19. Change budget

| Mốc | Giá trị |
|---|---|
| Ước lượng frozen (spec §16) | ~150–380 dòng production, 5 file |
| Trần frozen (task § Change budget) | **+600 / −400** |
| Thực tế production | **+194 / −23**, 4 file (file thứ 5 — `firebase_config.js` — không cần đổi) |
| Tình trạng | **TRONG TRẦN** — không có `CHANGE_BUDGET_EXCEEDED` |
| File production ngoài Expected Touch Area | **0** |

Non-production (test + tài liệu + governance) không tính vào trần production: 4 file test mới
(838 dòng), harness +103/−7, `test_t12_browser.js` +5/−1 (giàn giáo), `package.json` +6/−3,
`webapp/README.md` +175/−44.

Ghi rõ một mục có thể bị chất vấn: `webapp/package.json` **không** nằm trong danh sách "Allowed
non-production" viết tay của task. Nó phải đổi vì chính `CHECK-T14-11` gọi đích danh
`npm --prefix webapp test` và đòi lệnh đó exit 0 khi bao gồm suite mới — không có cách nào thoả
check đó mà không sửa `scripts.test`. Đây là thay đổi **bắt buộc bởi gate**, không phải mở rộng
phạm vi tự phát. `package-lock.json` đã được **hoàn nguyên về đúng bản `origin/main`** sau khi
`npm install` chạm vào nó, để không đổi bất kỳ version ghim nào.

## 20. Hardening findings

**Giữ nguyên tuyệt đối, không sửa, không mở task** (đúng chỉ thị phiên §13): `H-44`, `H-45`,
`H-46`, `H-47`, `H-48`, `H-50`. `H-46` **vẫn ACTIVE** — SELL/realized P&L không xuất hiện trong
bất kỳ đường nào mà bước C mở ra; guard nguyên trạng.

**Cập nhật disposition (không đóng)**: `H-42` (§11), `H-49` (§12).

**Quan sát mới của phiên này — finding, KHÔNG phải task** (`AGENTS.md` §3 "A finding is not a
task"), ghi để không bị quên, không tự sửa:

- **`H-51`** — `PROJECT/PRODUCTION_PATHS.md` §1 không khai `firestore.rules` và `firebase.json`
  là production path, dù cả hai quyết định quyền truy cập dữ liệu tài chính và bề mặt deploy;
  Step-C spec §16 thì có tính. Không BLOCKING: báo cáo này đã đo theo cách chặt hơn (tính cả hai
  file) nên kết luận budget không phụ thuộc vào sai khác đó. **Không tự sửa** `PRODUCTION_PATHS.md`
  — đó là authority row 8 của `AGENTS.md` §1, sửa nó là quyết định governance.
- **`H-52`** — `signInWithPopup()` phụ thuộc `apis.google.com` (gapi iframe), nên luồng đăng nhập
  không hoàn tất được trong môi trường chặn mạng ra ngoài. Với người dùng thật (có mạng) đây không
  phải khiếm khuyết; hành vi khi bị chặn là **fail closed**. Hệ quả cần nhớ: bằng chứng tự động
  không bao giờ phủ được màn hình đồng ý THẬT của Google (§14).

Cả hai được ghi vào `PROJECT/HARDENING_BACKLOG.md` cùng phiên, dưới dạng **finding có
`RE_TRIGGER_CONDITION`**, không có owner, không sinh task ID (số task ID mới của phiên = 0).

## 21. Validators

| Validator | Kết quả |
|---|---|
| `validate_governance.py` | PASS |
| `validate_project_state.py` | PASS |
| `validate_structure.py` | PASS |
| `validate_routing.py` | PASS |
| `validate_easy_roadmap.py` | PASS |
| `validate_task_completion.py` (T-14) | PASS |
| `sync_easy_roadmap.py` | chạy, `PROJECT/LO_TRINH_DE_HIEU.md` sinh lại |
| `branch_authority_check.sh --expect-branch claude/t14-step-c-firebase-isolation-xu6nxb` | xem §22 (chạy lại sau khi push) |

## 22. Kết quả chạy cuối phiên

Toàn bộ con số dưới đây là **kết quả chạy thật ở cuối phiên**, sau khi mọi thay đổi đã ổn định —
không phải số đo giữa chừng.

    npm --prefix webapp test                     -> EXIT 0
      node test_t12_ledger.js                    -> PASS (SC-01…SC-12, INV-1…INV-15)
      node test_t12_mutations.js                 -> PASS (7/7 mutant bị diệt, 0 survivor)
      node test_t14_deploy_isolation.js          -> PASS (18 assertion, 0 FAIL)
      node test_t14_rules.js                     -> PASS (31 assertion, 0 FAIL)
        └─ test_shared_rules_merge.js (con)      -> PASS (120 assertion, 0 deviation)
      node test_t14_persistence.js               -> PASS (60 assertion, 14/14 kịch bản)
      node test_t14_backup_restore.js            -> PASS (47 assertion, 6/6 kịch bản)
      node test_t12_browser.js                   -> PASS (17 record, 0 error)
      node test_stepb_ui.js                      -> PASS (AS-01…AS-12, PR-1…PR-6)

    python -m pytest -q                          -> EXIT 0, 678/678 PASS

Log đầy đủ (một lần chạy duy nhất, cuối phiên): `docs/reviews/evidence/T14/npm-test.log` (chứa
toàn bộ 8 bước của cổng release, gồm cả `test_t12_browser.js` và `test_stepb_ui.js`) và
`docs/reviews/evidence/T14/pytest.log`.

Kết quả `branch_authority_check.sh` sau khi push (upstream đã có) được ghi ở
`docs/sessions/S039-t14-step-c-firebase-isolation-implementation.md` §5.

## 23. Repair authority

`CAP-WEBAPP`: `allowed 2 / used 1 / remaining 1` — **KHÔNG ĐỔI** sau phiên này.

Phiên `S039` là **INITIAL IMPLEMENTATION** của `T-14`, không phải repair cycle của `T-12`/`T-13`
và không phải repair cycle của chính `T-14`. **0 repair cycle bị tiêu.** Không có REQUIRED check
nào FAIL sau khi sửa trong phạm vi, nên không có tình huống cần dùng chu kỳ còn lại, và phiên
này **không** tự cấp thêm bất kỳ chu kỳ nào.

Ba lần sửa trong phiên (một assertion tự bắt chính comment của mình trong `test_t14_rules.js`;
một assertion đếm thẻ lịch sử quên trừ thẻ "Số dư đầu kỳ" trong `test_t14_persistence.js`; một
dòng giàn giáo đăng nhập trong `test_t12_browser.js`) đều là **sửa test trong phạm vi thi hành
bình thường**, không phải repair cycle theo nghĩa `REVIEW_BUDGET_LEDGER.md` (không có REQUIRED
check nào FAIL trên mã production).

## 24. Hard-stop

**Không có hard-stop nào được kích hoạt.** Cụ thể:

- `ARCHITECTURE_CHANGE_REQUIRED` — không: không cần collection/document mới, không cần đổi shape
  `isCoinDcaOwner()`, không cần chạm `webapp/ledger.js`.
- `CHANGE_BUDGET_EXCEEDED` — không: +194/−23 so với trần +600/−400.
- `DATA_INTEGRITY_RISK` — không: safe-merge PASS, restore hợp lệ cho `derive()` lệch 0 VND.
- `OWNER_DECISION_REQUIRED` — không: mọi lựa chọn kỹ thuật đã nằm trong § Ràng buộc kiến trúc đã
  khoá hoặc trong Step-C spec; không đường nào cần mở SELL.
- `GOLDEN_PASS` — không áp dụng.
- `ABSORPTION_LIMIT_REACHED` — không: `H-49` được hấp thụ vào chính `T-14` theo đúng `DEC-049` D,
  không mở task mới nào (số task ID mới của phiên = **0**).

## 25. Hành động kế tiếp chính xác

    NEXT SMALLEST ACTION = mở phiên INDEPENDENT E2 REVIEW cho T-14 (reviewer độc lập, không phải
    phiên thi hành này), đúng tiền lệ T-12 (docs/reviews/T12-E2-INDEPENDENT-REVIEW.md) và T-13
    (docs/reviews/T13-E2-INDEPENDENT-REVIEW.md).

Sau E2:

- E2 `PASS` → chủ dự án ra Owner Closure (`IMPLEMENTED → DONE`), đóng phần REQUIRED của `H-42`,
  đóng `H-49`. `DONE` là **thẩm quyền chủ dự án**, không phải của agent.
- E2 phát hiện REQUIRED FAIL → dùng chu kỳ repair còn lại của `CAP-WEBAPP` (`remaining 1`), và
  chỉ khi đó.

Không được suy ra từ báo cáo này: cảnh báo "dừng dùng app với tiền thật không giới hạn" (`H-41`)
**vẫn còn hiệu lực**. Bước C đóng nhóm điều kiện Firebase/auth/backup; bước D
(`OWNER_LOCAL_ACCEPTANCE`) và `H-46` (SELL) nằm ngoài `T-14` và chưa được mở.
