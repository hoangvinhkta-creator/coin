# T-09B — Merge firestore.rules an toàn với rules Content thật (project dùng chung)

Nguồn thẩm quyền:
`governance/v4/CORE/RISK_MODEL.md`, `PROJECT/PROJECT_DECISIONS.md` `DEC-023`,
`docs/tasks/T-09B-dung-luu-tru-du-lieu-ben.md` (OD-B, CHECK-T09B-10/11/12).

Ngày:
2026-09-02

## Bối cảnh

Firebase project thật do Owner cung cấp (`tinphatcontent`, tên hiển thị "CoinDCA") **không**
dành riêng cho ETH DCA OS — trước đó phục vụ một ứng dụng khác ("Content — Zalo Group Tín
Phát"). Firestore của project đang có dữ liệu Content thật (`users`, `contents` (+subcollection
`versions`), `schedules`, `groups`, `config`, `fb_queue`, `audit_logs`). Firestore chỉ có **một**
rules document cho toàn bộ database — deploy `firestore.rules` của CoinDCA nguyên văn (thay thế)
sẽ xoá quyền truy cập hiện tại của Content. Owner cấm tường minh việc này.

## Phương pháp

1. Owner dán nguyên văn rules Content đang chạy thật (giữ verbatim trong
   `webapp/test_shared_rules_merge.js` làm mốc BEFORE, và trong `firestore.rules` phần khối
   Content — không refactor/format lại/đổi tên/thêm bớt quyền).
2. Merge: thêm **đúng hai** khối `match /ethdca/state` / `match /ethdca/seed` + một hàm
   `isCoinDcaOwner()` (đổi tên khỏi `isOwner()` cũ để không trùng hàm `isOwner(f)` đã có sẵn
   trong rules Content — trùng tên sẽ là lỗi biên dịch rules). Không thêm catch-all
   `match /{document=**}` (Content không có sẵn cái nào; namespace `ethdca` không trùng bất kỳ
   collection nào của Content nên không cần).
3. Chạy Firestore Rules Emulator (`webapp/test_shared_rules_merge.js`, dựng trên
   `webapp/test_firebase_harness.js` đã kiểm chứng từ phiên trước): nạp **BEFORE** (rules
   Content nguyên văn) rồi **AFTER** (rules đã merge, placeholder owner UID thay bằng một UID
   Anonymous Auth thật vừa được Auth Emulator ký — cùng cơ chế `bootstrapOwner` production dùng)
   — chạy **cùng một battery 53 probe** REST (đọc/ghi trực tiếp Firestore, không qua app, không
   mock) trên cả hai, so ALLOW/DENY từng probe.

## Battery probe Content (53 ca, phủ toàn bộ 8 collection — vượt yêu cầu tối thiểu §7:
`audit_logs`, `config`, `users`)

| Collection | Số ca | Điều kiện phủ (đọc thẳng từ rules text, không suy diễn business logic) |
|---|---|---|
| `users/{uid}` | 11 | read (unauth/signedIn), create (self/wrong-uid/unauth), update (self giữ role/tự nâng role/admin/khác không phải admin), delete (non-admin/admin) |
| `contents/{id}` | 10 | read, create (self/wrong createdBy/unauth), update (owner/không phải owner-không-manager/manager), delete (non-admin/admin) |
| `contents/{id}/versions/{v}` | 6 | read, create (signedIn/unauth), update/delete (luôn deny kể cả admin) |
| `schedules/{id}` | 7 | read, create (signedIn/unauth), update (bất kỳ signedIn), delete (non-manager/manager) |
| `groups/{id}` | 4 | read, write (non-manager/manager) |
| `config/{id}` | 4 | read, write (non-manager/manager) |
| `fb_queue/{id}` | 4 | read, write (signedIn/unauth) |
| `audit_logs/{id}` | 7 | read (non-manager/manager), create (self/sai userId/unauth), update/delete (luôn deny) |

**Kết quả:** `tổng probe Content: 53 | lệch BEFORE/AFTER: 0`. Toàn bộ 53 probe khớp phân tích
rules text (BEFORE == expect) **và** khớp giữa BEFORE/AFTER (không có probe nào bị merge làm
đổi hành vi). `CONTENT_BEHAVIOR_PRESERVED = YES`.

## Ma trận CoinDCA (§8 chỉ thị, 12 ca) — chạy trên ruleset đã merge

12/12 PASS: unauthenticated deny (1-2), UID sai deny (3-4), owner UID đọc/ghi state+seed
allow (5-8), document `ethdca/*` khác `state`/`seed` bị deny dù đúng owner UID (9), xoá
`state`/`seed` bị deny dù đúng owner UID — khớp canonical T-09B "app không bao giờ xoá
document" (10-11), và owner UID **không** có thêm quyền Content nào ngoài đúng những gì MỌI
actor đã signedIn của Content vốn đã được cấp — đối chiếu trực tiếp với `config`, `audit_logs`,
`users` (12a-12c): kết quả owner UID == kết quả actor signedIn thường ở cả ba, không lệch.

## Log đầy đủ

`node webapp/test_shared_rules_merge.js` — exit 0, 120/120 assertion PASS. Có thể chạy lại bất
cứ lúc nào (`npm --prefix webapp run test:rules-merge`) để tái lập bằng chứng này.

## OBSERVATION (không phải finding của T-09B, không tự sửa)

Rules Content hiện tại cho phép **bất kỳ user đã signedIn nào** (kể cả Anonymous, không cần
profile/role) `update` `schedules/{id}` và `write` `fb_queue/{id}` — permissive hơn các
collection khác (vốn cần `isManager()`). Đây là thiết kế có sẵn của Content, không liên quan gì
tới merge của CoinDCA (đã xác nhận identical BEFORE/AFTER ở trên), và không nằm trong
`DEC-021` Critical Product Question A-F của ETH DCA OS. Không sửa. Ghi lại để Owner tự quyết
định nếu quan tâm — không tạo `HARDENING_BACKLOG.md` entry (đó là backlog của CAP-* thuộc dự án
này, không phải nơi audit một ứng dụng khác).

## Kết luận

    CONTENT_BEHAVIOR_PRESERVED = YES  (53/53 probe, 0 lệch BEFORE/AFTER)
    CoinDCA rules matrix        = PASS (12/12, §8 chỉ thị)
    Rules merged                = CÓ, tại `firestore.rules` (owner UID còn placeholder)
    Rules deployed               = CHƯA — chờ Owner UID thật + Owner deploy

---

## Addendum — Owner UID production thật (checkpoint tiếp nối, cùng ngày)

Owner deploy Hosting thành công (`https://tinphatcontent.web.app`), mở bằng trình duyệt sẽ
dùng CoinDCA hằng ngày, Anonymous Auth sinh UID:

    XWUo6IvUqhULI1v1EBrfndEDrE13

**Không sửa `firestore.rules` (git-tracked) để bake UID này vào.** Lý do: file đó đóng vai trò
kép — vừa là bản deploy, vừa là TEST FIXTURE mà `webapp/test_t09b_persistence.js` (285
assertion, 14/14 CHECK-T09B) và `webapp/test_shared_rules_merge.js` (120 assertion) đang
`.replace(/OWNER_UID_REQUIRED/g, <uid động của mỗi lượt test>)` để chạy lặp lại được. Nếu thay
placeholder bằng UID thật cố định, mọi lượt test sau (dùng UID Anonymous Auth MỚI do chính
Auth Emulator sinh mỗi lần chạy) sẽ không còn khớp owner UID trong rules → toàn bộ 14 CHECK
owner-authenticated FAIL. Giữ template là quyết định kỹ thuật đúng, không phải bỏ sót yêu cầu.
Bù lại: **xác minh trực tiếp bằng chính UID thật này qua emulator** (không phải một UID khác
đại diện) — kết quả dưới đây — rồi đưa Owner lệnh deploy tự thay UID cục bộ, không commit.

### Xác minh với UID thật (không sửa file, chỉ thay trong bộ nhớ emulator giống hệt cơ chế
`H.rulesWithUid()` mà bộ test production đang dùng)

| Kiểm | Kết quả |
|---|---|
| Định dạng UID (28 ký tự Firebase) | PASS |
| Unauthenticated → `ethdca/state`/`seed` | DENY |
| UID sai (Auth Emulator sinh ngẫu nhiên) → `ethdca/state`/`seed` | DENY |
| **UID thật** → đọc/ghi `ethdca/state` | ALLOW |
| **UID thật** → đọc/ghi `ethdca/seed` | ALLOW |
| **UID thật** → document `ethdca/other` (ngoài allow-list) | DENY |
| **UID thật** → xoá `ethdca/state`/`seed` | DENY (khớp canonical: app không bao giờ xoá) |
| Content (`config`/`audit_logs`/`users`, mẫu tối thiểu §7) với ruleset mang UID thật | không đổi hành vi |

**16/16 assertion PASS.** Cơ chế mint token: Auth Emulator `accounts:signInWithCustomToken`
với custom token KHÔNG ký (`alg: none`, chỉ Auth Emulator chấp nhận — không dùng được với
Firebase thật) mang đúng `uid` cần test — kỹ thuật chuẩn để pin UID cụ thể trong Auth Emulator
khi `accounts:signUp` không nhận `localId` tuỳ ý.

### Git diff của checkpoint này

    0 file thay đổi. Không có gì cần commit vào code/rules — xác minh xong không để lại trạng
    thái tạm nào trong worktree.

### Lệnh Owner cần chạy để deploy Firestore Rules thật

Trên máy Owner (cần `firebase login` một lần nếu chưa, và `npm --prefix webapp install` nếu
`webapp/node_modules/.bin/firebase` chưa có):

```bash
cd coin   # gốc repo

# 1. Tạo bản deploy cục bộ (KHÔNG commit) — thay OWNER_UID_REQUIRED bằng UID thật:
sed 's/OWNER_UID_REQUIRED/XWUo6IvUqhULI1v1EBrfndEDrE13/' firestore.rules > /tmp/firestore.rules.deploy

# 2. Deploy đúng file đó (KHÔNG cần sửa firebase.json — trỏ path trực tiếp qua flag):
webapp/node_modules/.bin/firebase deploy --only firestore:rules --project tinphatcontent \
  --config <(sed 's#"rules": *"firestore.rules"#"rules": "/tmp/firestore.rules.deploy"#' firebase.json)

# 3. Xoá bản tạm (không bắt buộc, /tmp tự dọn):
rm -f /tmp/firestore.rules.deploy
```

Nếu `--config <(...)` (process substitution) không chạy được trên shell của bạn, cách đơn giản
hơn: tạm thời `sed -i` thay placeholder ngay trong `firestore.rules`, deploy, rồi `git checkout
-- firestore.rules` để khôi phục template — miễn KHÔNG commit lúc file đang mang UID thật:

```bash
sed -i 's/OWNER_UID_REQUIRED/XWUo6IvUqhULI1v1EBrfndEDrE13/' firestore.rules
webapp/node_modules/.bin/firebase deploy --only firestore:rules --project tinphatcontent
git checkout -- firestore.rules   # khôi phục template ngay sau khi deploy xong
```

Sau khi rules deploy xong: quay lại đây, tôi sẽ chuẩn bị và chạy production verification
CHECK-T09B-01/02/03/04/14 trên `https://tinphatcontent.web.app` (lưu ý: môi trường agent hiện
tại chặn `*.web.app` ở tầng mạng — phần verify cần mở URL thật vẫn cần bạn thực hiện và xác nhận
lại kết quả; phần verify qua Firestore/Auth REST trực tiếp thì agent làm được).
