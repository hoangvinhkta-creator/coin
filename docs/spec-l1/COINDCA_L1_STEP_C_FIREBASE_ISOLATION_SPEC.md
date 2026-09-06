# CoinDCA L-1 — STEP C: Firebase Isolation / Owner Auth / Backup / Recovery Spec

Status:
CANONICAL — APPROVED (`DEC-049`)

Phase:
CoinDCA L-1 — bước **C** (chặn cứng trước khi ghi tiền thật: isolation + auth bền + backup/
snapshot) của chuỗi A → B → C → D
(`docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §24)

Nguồn thẩm quyền (KHÔNG lặp lại, chỉ tham chiếu):
- `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §18 (ràng buộc R-1…R-5), §24, Phụ lục B
  (truy vết FB-1…FB-4) — **KHÔNG sửa** tài liệu đó ở đây; tài liệu này là nơi R-1…R-5 được
  **thi hành**.
- `PROJECT/HARDENING_BACKLOG.md` `H-42` (Firebase isolation), `H-49` (persistence evidence gap).
- `PROJECT/PROJECT_DECISIONS.md` `DEC-019`/`DEC-020`/`DEC-021` (Firebase = fixed owner
  constraint; Hosting/Firestore/Anonymous Auth baseline; Personal Tool Simplification
  Principle), `DEC-023` (shared project `tinphatcontent`, rules safe-merge), `DEC-041` K.1
  (mở lại câu hỏi recovery dưới L-1), `DEC-043` (ranh giới persistence bên trong `ethdca/state`
  — LOCKED), `DEC-049` (Owner Decision mở bước C này).
- `firestore.rules`, `firebase.json`, `webapp/firebase_config.js`, `webapp/app_logic.js`,
  `webapp/ledger_ui.js` — trạng thái hiện tại của hạ tầng Firebase, không suy luận lại.

Task định nghĩa việc thi hành:
`docs/tasks/T-14-buoc-c-firebase-isolation-auth-backup.md`

## Nguyên tắc bất di dịch của tài liệu này

1. Tài liệu này KHÔNG mở lại kế toán. Không công thức nào của `derive()`/`update()`/`migrate()`/
   `destructive()` (`webapp/ledger.js`, T-12) bị chạm. Không schema `coindca.ledger/2` nào đổi.
2. Tài liệu này KHÔNG chọn Firebase project mới. `DEC-019` ("Firebase = FIXED OWNER CONSTRAINT")
   và Owner Decision mở đầu bước C (§1 dưới đây, "Shared Firebase Project with Strong Logical
   Isolation") đã đóng câu hỏi provider/project — dự án Firebase riêng là **DEFERRED**, không
   phải câu hỏi mở của bước C.
3. Mọi thay đổi persistence PHẢI ở bên trong ranh giới `ethdca/state`/`ethdca/seed` đã LOCKED bởi
   `DEC-043`. Không di dời document, không đổi tên namespace, không thêm collection CoinDCA mới
   ngoài hai document này trừ khi §3 dưới đây chứng minh cần thiết (nó không cần).
4. SELL / realized P&L: vẫn **KHÔNG xuất hiện** trong bất kỳ đường nào mà tài liệu này mở ra.
   `H-46` chưa có Owner Decision xử lý — bước C không phải là nơi xử lý nó và không được coi là
   điều kiện tiên quyết đã thoả cho SELL.
5. Bước C giải quyết **isolation logic bên trong project dùng chung**, không phải cô lập vật lý.
   Bất kỳ câu nào trong tài liệu này ngụ ý "project Firebase riêng" là lỗi soạn thảo.

---

## 1. Owner Decision — chiến lược Firebase (tóm tắt, đầy đủ ở `DEC-049`)

> **"Shared Firebase Project with Strong Logical Isolation"**
>
> - Dự án Firebase riêng (`tinphatcontent-coindca` hoặc tương đương) **KHÔNG bắt buộc** cho bước C.
> - Tách project vật lý là **DEFERRED**, chuyển thành HARDENING tương lai, không phải blocker
>   hiện tại (xem §12 dưới đây — disposition mới của `H-42`).
> - CoinDCA vẫn là công cụ cá nhân, tần suất thấp, một chủ sở hữu duy nhất.
> - Namespace logic / Firestore rules / danh tính Owner / deploy isolation / backup / recovery
>   là **BẮT BUỘC** — đây chính là nội dung tài liệu này.
> - Ưu tiên đơn giản hơn là nhân bản project/tài khoản Google, nhưng **không đánh đổi** tính
>   đúng đắn bảo mật/toàn vẹn dữ liệu để đạt sự đơn giản đó.

---

## 2. Data isolation — giữ nguyên `ethdca/*`, không di dời

**Quyết định: KHÔNG di dời `ethdca/state`/`ethdca/seed`.** Lý do, theo đúng yêu cầu "ưu tiên
migration nhỏ nhất":

- `DEC-043` đã **LOCK** ranh giới persistence "bên trong `ethdca/state`" như một ràng buộc kiến
  trúc của `T-12` — di dời document là một `ARCHITECTURE_CHANGE_REQUIRED` không có lợi ích an
  toàn tương xứng.
- Cô lập dữ liệu hiện tại **không** dựa vào tên namespace — nó dựa vào `firestore.rules`: khối
  `ethdca/*` đã là allow-list tường minh (chỉ đúng hai document), độc lập hoàn toàn với các khối
  Content (`users`, `contents`, `schedules`, `groups`, `config`, `fb_queue`, `audit_logs`) — đã
  verify bằng Firestore Rules Emulator tại `DEC-023` (53 probe, 0 deviation). Đổi TÊN namespace
  (`ethdca` → `coindca`) không tăng thêm cô lập nào; nó chỉ tạo rủi ro migration không cần thiết
  (phải viết migration atomic mới, phải test lại toàn bộ persistence, vi phạm nguyên tắc 3 ở
  trên).
- Rủi ro cô lập thật sự nằm ở **danh tính** (ai được coi là `isCoinDcaOwner()`), không nằm ở
  **đường dẫn**. §4/§5 dưới đây xử lý đúng chỗ đó.

Kết luận: `ethdca/state` (ledger, tier 1) và `ethdca/seed` (price-history seed, tier 2) giữ
nguyên là hai document CoinDCA duy nhất. Không collection CoinDCA mới nào được thêm bởi bước C.

---

## 3. Owner identity — Google Sign-In thay thế Anonymous Auth làm thẩm quyền bền vững

### 3.1 Vì sao Anonymous Auth không còn đủ (FB-4)

Anonymous Auth UID sống trong IndexedDB của **một** browser profile. Bốn kịch bản
(`docs/spec-l1/...ACCOUNTING_SPEC.md` §18, `RSK-001`) đều sinh UID mới bị `firestore.rules` từ
chối: cửa sổ riêng tư, đổi máy, đổi trình duyệt, xoá site data. `DEC-021` (OD-C = R2) đã CHẤP
NHẬN giới hạn này cho V1-của-V2.1.5 bằng một Owner Scope Decision (không phải bằng chứng kỹ
thuật bị đảo ngược). Dưới L-1 — nơi app là sản phẩm chính chứ không còn phụ trợ — `DEC-041` K.1
mở lại câu hỏi này, và Owner Decision mở đầu bước C (§1) chọn hướng giải quyết: **Google Sign-In**.

### 3.2 Thiết kế

    Owner mở app -> chưa có phiên Google -> hiện nút "Đăng nhập bằng Google"
      -> firebase.auth().signInWithPopup(new firebase.auth.GoogleAuthProvider())
      -> cred.user.uid = UID CỦA TÀI KHOẢN GOOGLE ĐÓ (KHÔNG đổi qua browser/máy/thiết bị)
      -> UID này là giá trị được gán cho `OWNER_UID_REQUIRED` trong firestore.rules khi Owner
         deploy (đúng cơ chế placeholder đã có, không đổi hình dạng)

- **Không còn `signInAnonymously()`** trong đường khởi động persistence
  (`webapp/app_logic.js::initPersistence()`). Client gọi thẳng Google Sign-In.
- UID ổn định qua: reload, restart, đổi máy, đổi trình duyệt, xoá `localStorage`/`IndexedDB`,
  cửa sổ riêng tư — vì nó gắn với tài khoản Google, không gắn với thiết bị. Đây là cách duy nhất
  thoả cả bốn yêu cầu của bản chỉ thị phiên §5 ("Owner identity survives browser/device change",
  "losing local browser storage does not lose ownership") mà không cần cơ chế recovery credential
  phụ (loại bỏ luôn phương án R1 phức tạp hơn của `DEC-020`: link email/password vào Anonymous
  UID — không cần nữa vì không còn Anonymous UID để link).
- **Không tạo hệ thống multi-user.** Rules vẫn khoá cứng đúng MỘT UID
  (`request.auth.uid == "OWNER_UID_REQUIRED"`). Đăng nhập bằng một tài khoản Google KHÔNG PHẢI
  UID đó vẫn bị từ chối y hệt cơ chế hiện tại — chỉ khác nguồn UID.
- **Đăng xuất/đăng nhập lại không đổi danh tính sổ cái**: vì UID là thuộc tính của tài khoản
  Google, không phải của phiên đăng nhập, logout → login lại (cùng tài khoản) cho lại đúng UID
  đó, đọc lại đúng `ethdca/state`.
- Không thêm Cloud Functions, không thêm bảng `users`/hồ sơ, không thêm role — đúng "Firebase
  Scope Principle" (`DEC-019` điểm 3).

### 3.3 Vì sao KHÔNG cần đổi hình dạng `firestore.rules`

`isCoinDcaOwner()` hiện tại:

```
function isCoinDcaOwner() {
  return request.auth != null && request.auth.uid == "OWNER_UID_REQUIRED";
}
```

so sánh đúng MỘT UID cố định — bất kể UID đó có nguồn gốc từ Anonymous Auth hay từ Google
Sign-In. **Không cần sửa logic rules.** Thay đổi cần thiết chỉ có hai phần: (a) giá trị Owner
thật sự deploy vào `OWNER_UID_REQUIRED` đổi từ một Anonymous UID sang UID của tài khoản Google
Owner (hành động Owner thực hiện khi deploy, y hệt quy trình hiện tại — xem `webapp/README.md`);
(b) comment/tài liệu trong `firestore.rules` cập nhật để không còn nói "Anonymous Auth" là nguồn
danh tính. Đây là bằng chứng cho "smallest migration": thay đổi thật sự nằm ở **client** (§3.2),
không nằm ở rules.

### 3.4 Hệ quả phụ có lợi — đường đóng khả dĩ cho FB-1

`H-42`/FB-1 ghi: bật Anonymous Auth cho project dùng chung khiến rules Content
(`signedIn() = request.auth != null`) mở cửa cho khách vô danh, vì Content không phân biệt
Anonymous với tài khoản thật. Một khi CoinDCA không còn cần Anonymous Auth (§3.2), **Anonymous
Sign-in Provider có thể được tắt hẳn trong Firebase Console** mà không ảnh hưởng CoinDCA — đóng
FB-1 tại nguồn, không cần sửa một dòng rules Content nào. Đây là một khuyến nghị vận hành cho
Owner (thao tác Console, ngoài phạm vi commit repo), ghi ở đây để không bị quên; **không** bắt
buộc để bước C DONE (xem Completion Gate — khuyến nghị, không REQUIRED, vì việc đó cần Owner xác
nhận Content không có luồng nào khác đang dựa vào Anonymous, ngoài phạm vi audit của CoinDCA).

---

## 4. Firestore rules isolation — giữ shape, xác nhận lại bằng emulator

Không đổi shape khối `COINDCA` của `firestore.rules` (§3.3). Yêu cầu Completion Gate: chạy lại
**toàn bộ** bộ probe safe-merge (`webapp/test_shared_rules_merge.js`, kế thừa từ `DEC-023`) trên
rules hiện hành + xác nhận thêm năm kịch bản danh tính mới (Google UID thay vì Anonymous UID):

| # | Actor | Hành động | Kết quả kỳ vọng |
|---|---|---|---|
| 1 | Owner (Google UID đúng) | read/create/update `ethdca/state`, `ethdca/seed` | ALLOW |
| 2 | Ẩn danh (không đăng nhập) | read/write `ethdca/state` | DENY |
| 3 | Tài khoản Google KHÁC (UID sai) đã đăng nhập | read/write `ethdca/state` | DENY |
| 4 | Bất kỳ actor nào | `delete` trên `ethdca/state` hoặc `ethdca/seed` | DENY (không có rule `delete` — mặc định deny) |
| 5 | Owner (UID đúng) | đọc/ghi bất kỳ collection Content nào (`users`, `contents`, ...) | Hành vi Content KHÔNG đổi (so với baseline `DEC-023`) — không có quyền đặc biệt nào phát sinh từ việc là CoinDCA Owner |

Bốn dòng đầu ánh xạ trực tiếp `C-AS-01`…`C-AS-03` (§15). Dòng 5 là regression bắt buộc: xác nhận
namespace CoinDCA không "leak" quyền ngược vào Content.

---

## 5. Deploy isolation

### 5.1 Hosting — target tường minh

`firebase.json` hiện thiếu khoá `hosting.target` (FB-2). Thiết kế:

```json
"hosting": {
  "target": "coindca",
  "public": "webapp/public",
  ...
}
```

Yêu cầu vận hành (Owner thực hiện một lần, ngoài phạm vi session này — không có Firebase CLI
authority ở đây):

```
firebase target:apply hosting coindca <site-id-coindca>
```

Ghi nhận thực tế đã xác nhận tại `DEC-023`: Content **chưa từng** deploy Hosting site nào trong
project `tinphatcontent` (Owner tự xác nhận qua Console) — nên rủi ro FB-2 hiện tại là **lý
thuyết**, không phải đang treo lơ lửng trên một site thật. Khai `target` là phòng thủ có chi phí
gần bằng không (một khoá JSON + một lệnh CLI một lần), không phải sửa chữa một sự cố đang xảy ra.

### 5.2 Firestore rules — không thể target-hoá, phải procedural

Firestore chỉ có **một** ruleset cho toàn bộ database — không có khái niệm "deploy rules chỉ cho
CoinDCA". Cô lập deploy rules vì vậy KHÔNG THỂ đạt được bằng cấu hình; nó phải là **quy trình bắt
buộc trước mỗi lần deploy**:

    TRƯỚC MỌI `firebase deploy --only firestore:rules`:
    1. `npm run test:rules-merge` (hoặc lệnh kế thừa) PHẢI PASS trên rules SẮP deploy, đối
       chiếu với hành vi Content đã biết (đúng cơ chế `DEC-023`).
    2. Diff `firestore.rules` PHẢI được đọc thủ công: mọi thay đổi ngoài khối `COINDCA` là
       tín hiệu dừng lại và hỏi Owner trước khi deploy.
    3. Chỉ deploy SAU khi (1) và (2) đều pass.

Ghi vào `webapp/README.md` (hoặc file vận hành tương đương) như một runbook ba bước, không phải
tự động hoá bằng CI (dự án không có CI, `DEC-019`/Personal Tool Simplification Principle không
đòi hỏi CI cho một công cụ cá nhân).

### 5.3 Lệnh deploy khuyến nghị (tách rời, không dùng `firebase deploy` trần)

```
firebase deploy --only hosting:coindca --project tinphatcontent
firebase deploy --only firestore:rules --project tinphatcontent   # chỉ sau khi §5.2 pass
```

Không đề xuất bất kỳ CI/CD pipeline nào (ngoài phạm vi, §7/§15 của chỉ thị phiên).

---

## 6. Auth isolation — phân tích hệ quả dùng chung Auth

Firebase Auth là project-wide: bật một provider ảnh hưởng toàn bộ project, không chỉ CoinDCA.
Hệ quả phải phân tích tường minh (không được ngầm định "authenticated == CoinDCA Owner"):

| Hệ quả | Phân tích | Giảm thiểu |
|---|---|---|
| Người dùng Content đã đăng nhập (bất kỳ tài khoản nào) mở app CoinDCA | `request.auth != null` đúng, nhưng `isCoinDcaOwner()` so UID cụ thể — SAI trừ khi trùng đúng UID Owner | Rules (§3.3), không đổi |
| Owner đăng nhập Google cho CoinDCA rồi mở app Content | Auth session dùng chung theo project — Owner CÓ THỂ vô tình có một phiên Content dưới cùng trình duyệt | Không phải lỗi bảo mật (Owner là chính chủ), nhưng cần lưu ý UX: hai app độc lập, không có "logout CoinDCA" tự động logout Content và ngược lại — ghi nhận, không sửa (ngoài phạm vi CoinDCA) |
| Anonymous Auth bật cho CoinDCA (V1 cũ) mở cửa Content (FB-1) | Đã phân tích §3.4 | Ngừng dùng Anonymous ở client (§3.2) + khuyến nghị tắt provider (§3.4) |
| Một tài khoản Google thứ hai (không phải Owner) vô tình trùng cấu hình | Không thể — UID Firebase là duy nhất per tài khoản per project, không đoán được, không cấu hình sai kiểu này | N/A |

Kết luận bắt buộc ghi lại: **"authenticated == CoinDCA Owner" là SAI** và không đường nào của
thiết kế này giả định điều đó — mọi quyền truy cập CoinDCA đi qua so sánh UID tường minh
(`isCoinDcaOwner()`), không đi qua "đã đăng nhập".

---

## 7. Backup

### 7.1 Yêu cầu

Theo `governance/product/16_BACKUP_DISASTER_RECOVERY.md`, dự án phải khai RPO/RTO cụ thể (không
dùng số ví dụ của chuẩn):

    RPO (Recovery Point Objective) = 30 ngày kể từ lần export gần nhất, khuyến nghị export
      sau mỗi phiên nhập giao dịch (tần suất DCA cá nhân thấp — vài giao dịch/tháng —
      nên cửa sổ mất dữ liệu thực tế nhỏ hơn nhiều con số này trong thực hành bình thường).
    RTO (Recovery Time Objective) = trong một phiên sử dụng (khôi phục là thao tác UI vài
      bước + xác nhận derive() khớp — không có bước vận hành hạ tầng nào).

Dữ liệu canonical **đã** nằm bền trong Firestore (`ethdca/state`) — "backup" ở đây là lớp **thứ
hai**, độc lập với Firestore, phòng trường hợp mất quyền truy cập Firestore hoặc dữ liệu Firestore
bị hỏng bởi chính thao tác của Owner (import sai, wipe nhầm).

### 7.2 Thiết kế (mở rộng cơ chế đã có, không viết lại)

`webapp/ledger_ui.js` đã có `download()` + nút "Tải về JSON" (`l1Export`). Yêu cầu bổ sung cho
bước C:

1. **Timestamp bắt buộc**: tên file và nội dung export PHẢI mang thời điểm xuất, dạng
   `coindca-ledger-<ISO8601>.json` (ví dụ `coindca-ledger-2026-09-06T10-00-00Z.json`), và trường
   `exportedAt` (ISO 8601) trong chính JSON.
2. **Schema/version tường minh trong export**: JSON export PHẢI chứa `schemaVersion` (giá trị
   `CoinLedger.SCHEMA`, hiện `coindca.ledger/2`) ở cấp cao nhất — không suy luận ngầm.
3. **Chỉ export nguồn sự thật canonical**: `state` (openingPosition + trades[] + events[] +
   plan/carry) và `seed` — KHÔNG export bất kỳ trường dẫn xuất nào (`derive()` output) làm nguồn
   phục hồi. Nếu hiển thị số dẫn xuất trong file cho mục đích tham khảo con người, nó PHẢI nằm
   trong khối riêng đánh dấu `derivedSnapshot: { ..., "_meta": "INFORMATIONAL — NOT IMPORTED" }`
   đúng `INV-1`/spec kế toán §9.4 — import bỏ qua khối này vô điều kiện.
4. **Không commit dữ liệu Owner thật vào Git** — export là hành động client-side, tải xuống máy
   Owner; không có đường nào trong thiết kế này ghi export vào repository.

---

## 8. Recovery / Restore

### 8.1 Yêu cầu tối thiểu (theo chỉ thị phiên §10)

```
backup hợp lệ -> durable state rỗng/hỏng -> restore -> server ACK -> reload -> derive()
  -> đúng y hệt trạng thái tài chính canonical trước đó
```

### 8.2 Thiết kế — mở rộng `l1Import` hiện có

`webapp/ledger_ui.js` hiện có `l1Import` (nạp file → `confirm()` → ghi trực tiếp qua
`L.canonical()`). Bổ sung bắt buộc cho bước C:

1. **Preview trước khi ghi** (mới): sau khi đọc file và `JSON.parse` thành công, hiển thị một
   bản tóm tắt (không ghi gì) TRƯỚC dialog xác nhận: `schemaVersion` của file, số lượng
   `events`, khoảng ngày (min/max), và **KẾT QUẢ VALIDATE** (pass/fail) chạy qua
   `CoinLedger.canonical()`/`validate()` ở chế độ dry-run (không mutate state hiện tại). Owner
   xác nhận dựa trên bản tóm tắt này, không dựa trên "tin tưởng file".
2. **Từ chối schema dị dạng, KHÔNG mutate** (`INV`-class): nếu `schemaVersion` không khớp hoặc
   `canonical()` ném lỗi validate, restore DỪNG trước khi chạm `ethdca/state` — thông báo lỗi cụ
   thể (trường nào sai), state hiện tại giữ nguyên 100%. Đây là REQUIRED check, không phải best
   effort.
3. **Snapshot trước khi ghi đè** (đã có, xác nhận lại là bắt buộc cho đường restore): tự động
   `download('coindca-before-restore-<ISO8601>.json', state hiện tại)` + ghi
   `localStorage['coindca-last-snapshot']` **trước** khi gọi `destructive()`/ghi Firestore — tên
   riêng cho nhánh restore (phân biệt với snapshot "before-change" tổng quát) để Owner nhận ra
   đúng ngữ cảnh khi cần dùng lại.
4. **Ghi nguyên tử**: `destructive()` (đã có từ T-12, `INV-12`-style) ghi toàn bộ state mới hoặc
   không ghi gì — không có trạng thái nửa vời. Bước C không viết lại cơ chế này, chỉ xác nhận nó
   được gọi đúng trên đường restore và có test phủ đường lỗi (restore thất bại giữa chừng do mất
   mạng → state Firestore không đổi, vì ghi Firestore tự nó là atomic ở cấp document).
5. **`derivedSnapshot` không được import**: nếu file backup chứa khối `derivedSnapshot`
   (§7.2 mục 3), import PHẢI bỏ qua nó vô điều kiện — chỉ `openingPosition`/`trades`/`events`/
   `plan`/`carry` được ghi.

---

## 9. Multi-device

Với Google Sign-In (§3), multi-device đơn giản hơn hẳn thiết kế Anonymous cũ — không cần cơ chế
link/recovery credential:

    Device A: Owner đăng nhập Google -> ghi giao dịch -> Firestore ethdca/state cập nhật
    Device B: Owner đăng nhập CÙNG tài khoản Google -> CÙNG UID -> đọc ĐÚNG document đó

Kịch bản bắt buộc kiểm (ánh xạ `C-AS-06`/`C-AS-07`, §15):

| Kịch bản | Kỳ vọng |
|---|---|
| Reload cùng thiết bị | Đọc lại y hệt server state (`source: "server"`, không dùng cache SDK — hành vi đã có, giữ nguyên) |
| Logout → login lại (cùng tài khoản) | Cùng UID → cùng document → cùng dữ liệu |
| Trình duyệt/hồ sơ hoàn toàn mới, `localStorage` trống | Đăng nhập Google → CÙNG UID → tải đúng `ethdca/state` từ server, KHÔNG hiện trạng thái rỗng như một chủ sở hữu mới |
| `localStorage` cũ/lệch (`rev` cũ hơn server) | Server thắng — mirror cũ KHÔNG được ghi đè server (hành vi `reconcileMirror()`/`pushDiverged`/`dropDiverged` đã có từ T-09B, xác nhận lại — đây chính là nội dung H-49 cần bằng chứng chạy lại được) |
| Ghi xung đột (revision cũ hơn khi ghi) | Từ chối ghi đè, báo lỗi rõ ràng, không mất dữ liệu server |

**KHÔNG** xây đồng bộ hoá cộng tác thời gian thực (không presence, không merge nhiều writer đồng
thời) — một Owner, dùng thỉnh thoảng nhiều thiết bị, không phải nhiều người dùng đồng thời.

---

## 10. Shared-project failure modes — bảng bảo vệ

| Failure mode | Bảo vệ trong thiết kế này |
|---|---|
| Content deploy đè Hosting CoinDCA | N/A hiện tại (Content không deploy Hosting) — §5.1 hosting target là phòng thủ hướng ngược (CoinDCA đè Content), xem dòng dưới |
| CoinDCA deploy đè Hosting Content | `firebase.json` khai `hosting.target=coindca` (§5.1); deploy dùng `--only hosting:coindca` (§5.3) |
| Sửa rules project-wide vô tình mở CoinDCA | Runbook bắt buộc §5.2 (test safe-merge trước mọi deploy rules) |
| Anonymous UID đổi giữa các thiết bị | Không còn áp dụng — Google UID không phụ thuộc thiết bị (§3) |
| Người dùng Content đã xác thực bị nhầm là CoinDCA Owner | Rules so UID tường minh, không so `signedIn()` (§3.3, §6) |
| Sai đường dẫn Firestore | Namespace không đổi, không có đường mới để sai (§2) |
| Cache local đè server | `source: "server"` bắt buộc khi đọc (đã có) + `reconcileMirror()` server-wins (đã có, xác nhận lại bằng test — H-49) |
| Xoá/reset nhầm | Không có `delete` rule (đã có); export/backup thủ công (§7) + snapshot tự động trước mọi thao tác phá huỷ (§8.2 mục 3) |
| Restore nhầm schema | Validate + preview trước khi ghi, từ chối im lặng-không-mutate khi sai (§8.2 mục 2) |

---

## 11. H-42 — disposition mới (thay thế phần "hướng cần đánh giá sau" cũ)

Xem `PROJECT/HARDENING_BACKLOG.md` `H-42` (bản cập nhật đi kèm bước C này) cho văn bản chính
thức. Tóm tắt:

**REQUIRED CHO BƯỚC C (T-14, tài liệu này thi hành):**
- Owner identity bền vững, sống sót qua đổi thiết bị/trình duyệt (§3).
- Rules khoá đúng một Owner (§3.3, §4) — hình dạng giữ nguyên, danh tính đổi nguồn.
- Deploy isolation logic (hosting target + runbook rules, §5).
- Backup + recovery có snapshot/validate/atomic (§7, §8).
- Bằng chứng persistence chạy lại được — hấp thụ `H-49` (§12 dưới đây).

**DEFERRED / OPTIONAL (KHÔNG thuộc bước C, không mở task):**
- Firebase project vật lý riêng cho CoinDCA.
- Tắt Anonymous Auth provider ở Console (khuyến nghị vận hành, §3.4 — không REQUIRED vì cần
  Owner tự xác nhận Content không phụ thuộc, ngoài phạm vi audit CoinDCA).
- Bất kỳ hệ thống multi-user/role nào cho Content hay CoinDCA.

---

## 12. H-49 — hấp thụ vào bước C

`H-49` (bằng chứng persistence `T-09B` không còn chạy lại được sau khi Step B gỡ `#tab-setup`) tự
nêu tên bước C trong `RE_TRIGGER_CONDITION` của chính nó: *"bước C (H-42, Firebase isolation) bắt
đầu — bước đó cần bằng chứng persistence chạy lại được."* Vì Completion Gate của T-14 (§ dưới
task file) đã BẮT BUỘC test multi-device/reconcile/persist chạy qua UI Step B hiện hành (§9 ở
trên), yêu cầu này TỰ NHIÊN thay thế 118 assertion legacy đã mất khả năng chạy — không cần một
task riêng. `C-AS-14` (§15) là tiêu chí đóng `H-49`.

---

## 13. Out of scope (nhắc lại tường minh, không suy diễn thêm)

Không: Firebase project riêng · tài khoản Google thứ hai · hệ thống multi-user/SaaS ·
roles/admin panel · hạ tầng billing · enterprise backup · disaster recovery cluster · SELL ·
realized P&L · Research/Buy Score · `OWNER_LOCAL_ACCEPTANCE` (bước D). Không sửa ngữ nghĩa kế
toán T-12. Không redesign UX T-13 ngoài một điểm vào nhỏ cho đăng nhập/backup/restore.

---

## 14. Acceptance scenarios (đồng bộ với Completion Gate của `T-14`)

Dữ liệu tổng hợp (synthetic) trong mọi kịch bản dưới đây, đúng `DEC-041` C.

| ID | Kịch bản |
|---|---|
| C-AS-01 | Owner đăng nhập Google (UID đúng) → truy cập được dữ liệu CoinDCA |
| C-AS-02 | Không đăng nhập → đọc/ghi tài chính CoinDCA bị từ chối |
| C-AS-03 | UID xác thực khác (không phải Owner) → bị từ chối |
| C-AS-04 | Hành vi namespace Content không đổi (regression safe-merge) |
| C-AS-05 | Owner ghi → server ACK → reload → khớp chính xác |
| C-AS-06 | Trình duyệt/hồ sơ mới → đăng nhập → cùng sổ cái |
| C-AS-07 | Mirror local cũ không ghi đè được sự thật server |
| C-AS-08 | Export backup chứa nguồn sự thật canonical (không chứa trường dẫn xuất làm nguồn phục hồi) |
| C-AS-09 | Restore backup hợp lệ → `derive()` cho đúng trạng thái tài chính như trước |
| C-AS-10 | Backup dị dạng → không có mutation bền nào xảy ra |
| C-AS-11 | Restore thực hiện snapshot trước khi ghi đè phá huỷ |
| C-AS-12 | Deploy CoinDCA có mục tiêu (targeted) không sửa bề mặt deploy Content |
| C-AS-13 | Giả định cấu hình liên quan Content không đổi sau các thay đổi của bước C |
| C-AS-14 | Bằng chứng persistence executable thay thế/khoả lấp đúng chỗ `H-49` |

---

## 15. Production reachability — định nghĩa PASS

```
app CoinDCA thật (Step B UI)
  -> Firebase SDK thật
  -> Auth Emulator + Firestore Emulator (rules thật của repo)
  -> đăng nhập Google (giả lập bằng Auth Emulator identity platform / test provider)
  -> ghi giao dịch qua UI
  -> logout/login lại HOẶC hồ sơ trình duyệt mới (xoá localStorage/IndexedDB)
  -> reload
  -> derive() cho đúng số liệu như trước
```

kèm các ca âm (§14 C-AS-02/03) chạy trên **cùng** hạ tầng emulator + rules thật — không mock
thuần rules, không mock thuần client. Đây là cùng chuẩn production reachability mà `T-09B`/`T-12`/
`T-13` đã dùng, áp lại cho bước C.

---

## 16. Change budget — ước lượng (chi tiết đầy đủ ở `docs/tasks/T-14-...md` § Change budget)

| File | Loại | Ước lượng LOC |
|---|---|---|
| `webapp/app_logic.js` | Modify — thay `signInAnonymously()` bằng Google Sign-In, UI trạng thái đăng nhập | ~80–180 |
| `webapp/ledger_ui.js` | Modify — timestamp export, preview/validate trước restore, tên snapshot riêng | ~60–150 |
| `firestore.rules` | Modify — comment/tài liệu, KHÔNG đổi shape logic | ~10–30 |
| `firebase.json` | Modify — thêm `hosting.target` | ~3–5 |
| `webapp/firebase_config.js` | Modify nhỏ hoặc không đổi | 0–10 |
| `webapp/README.md` (hoặc file vận hành tương đương) | Modify — runbook deploy 3 bước, hướng dẫn tạo hosting target | ~40–100 (docs, không phải production path) |
| Test mới (rules + persistence + multi-device qua UI) | New, non-production path | ~200–450 |

Ước lượng production diff (loại trừ test/docs, theo `PRODUCTION_PATHS.md`): **~150–380 dòng**,
nằm trong biên độ các initial implementation trước đó của `CAP-WEBAPP` (T-12/T-13 dùng trần
+1800/−1400). Không cần `OWNER_EXTENSION` budget mới.
