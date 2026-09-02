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
