# App theo dõi trên web

App single-user để theo dõi vốn, ladder và danh mục theo ETH DCA OS V2.1.5.

**Từ T-09B (2026-09-02):** app chạy trên **Firebase Hosting**, sổ kế toán lưu bền trên **Cloud
Firestore** (`ethdca/state` + `ethdca/seed`) (`DEC-019`/`DEC-020`/`DEC-021`).

**Từ T-14 (2026-09-06, bước C — `DEC-049`):** danh tính chủ sở hữu là **Google Sign-In**, KHÔNG
còn Anonymous Auth. UID gắn với **tài khoản Google**, nên đổi máy / đổi trình duyệt / cửa sổ
riêng tư / xoá dữ liệu trình duyệt **không** làm mất quyền truy cập sổ. Xem
"§ Danh tính chủ sở hữu", "§ Runbook deploy" và "§ Sao lưu và khôi phục" bên dưới. Bản artifact cũ
(<https://claude.ai/code/artifact/ee1cc5bf-b66c-438f-9aee-ca229b0e1d95>) chạy dưới CSP chặn
Firebase nên **không còn là bản dùng thật**; dữ liệu ở đó phải được *Tải về JSON* rồi *Nạp lại
từ JSON* trên bản Firebase. Xem "Thiết lập Firebase" bên dưới.

> **App này nằm sau một cổng chưa mở.** Implementation Plan §9 chỉ cho phép dựng app MVP sau
> khi backtest cho verdict BUILD. Verdict chưa chạy trên dữ liệu Binance thật, nên app được
> xây theo yêu cầu của chủ dự án như một **công cụ ghi chép và tính toán**, không phải bằng
> chứng rằng chiến lược đã được chứng thực. Banner cảnh báo này hiển thị thường trực trên app.

## Vì sao app không tự lấy giá

App là trang tĩnh trong trình duyệt, không có backend riêng, và `api.binance.com` không cho
trình duyệt gọi trực tiếp (CORS). App **không thể** tự lấy giá. Hệ quả:

1. Lịch sử 365+ ngày đến từ file seed do engine Python thật sinh ra: `ethdca export-live`.
2. Mỗi ngày bạn nhập giá đóng cửa ETH/BTC và volume ở tab **Nhập số liệu**.

Chỉ nhập nến **đã đóng** — dùng nến đang chạy là vi phạm luật no-lookahead (Backtest §1–2).

## Vấn đề hai bản cài đặt, và cách xử lý

Impl Plan §1 yêu cầu live và backtest dùng chung một core strategy function. Một trang tĩnh
không chạy được Python, nên `engine.js` là **bản cài đặt thứ hai** của cùng đặc tả — và hai
bản cài đặt thì trôi khỏi nhau.

Cách chặn: mỗi seed mang theo OSCORE do Python tính cho 40 ngày gần nhất (`parity`). App tính
lại các ngày đó bằng JS và so; lệch quá dung sai thì hiện banner đỏ và bạn không nên tin số
trên trang. Kết quả đối chiếu hiển thị ở tab **Thiết lập**.

Lần kiểm gần nhất: lệch tối đa 7.4e-11 trên 40 ngày — hai bản đồng thuận.

## Thiết lập Firebase (T-09B — một lần, cần terminal; sau đó chỉ dùng trình duyệt)

Kiến trúc cố định (`DEC-020`): Browser → Firebase Hosting → Firebase Anonymous Auth → Cloud
Firestore. `localStorage` chỉ là bản sao/cache; mất nó không mất sổ (CHECK-T09B-03).

**Nếu project Firebase đang DÙNG CHUNG với một ứng dụng khác** (trường hợp thật của dự án này —
project `tinphatcontent` trước đó phục vụ ứng dụng "TinphatContent"/Content, Firestore đang có
dữ liệu Content cũ): **KHÔNG** chạy lệnh `firebase deploy` (không scope) hay
`firebase deploy --only firestore:rules` với nguyên văn `firestore.rules`/`firebase.json` của
repo này. Firestore chỉ có MỘT rules document cho cả database, và Hosting site mặc định chỉ
phục vụ MỘT bộ nội dung — deploy thẳng có thể xoá quyền truy cập của Content hoặc ghi đè site
đang chạy. Xem cảnh báo chi tiết ở đầu `firestore.rules` trước khi làm bước 3-4 dưới đây.

1. Tạo project trên <https://console.firebase.google.com> (gói Spark/free đủ cho một người dùng).
   Bật **Authentication → Sign-in method → Google** (từ T-14; trước đó là *Anonymous* — không còn
   cần cho CoinDCA). Tạo **Firestore Database** (production
   mode — rules của repo sẽ được deploy đè lên). Thêm một **Web app** trong Project settings và
   chép khối config (`apiKey`, `authDomain`, `projectId`, `appId`).
2. Điền config vào `webapp/firebase_config.js` (đây là public client config, không phải secret;
   KHÔNG bao giờ đưa service account/private key vào repo). Build lại:
   `node webapp/build_app.js` → sinh `webapp/public/index.html`.
3. Deploy (cần `npm --prefix webapp install` để có `firebase` CLI trong `webapp/node_modules/.bin`,
   và `firebase login` một lần). **Từ T-14: luôn deploy có scope**, không bao giờ `firebase deploy`
   trần — xem "§ Runbook deploy" bên dưới cho lệnh đầy đủ và ba bước bắt buộc trước khi deploy
   rules.
4. Mở URL Hosting bằng trình duyệt của chủ sở hữu và đăng nhập Google — xem
   "§ Danh tính chủ sở hữu" bên dưới cho luồng đầy đủ (trước T-14 bước này là nhận diện thiết bị
   bằng Anonymous UID; nay là UID tài khoản Google).
5. Tải lại app → chip đầu trang hiện *Chưa có bản bền — sổ trống*. Nếu có dữ liệu cũ:
   **Cài đặt → Nạp lại từ JSON** (xem "§ Sao lưu và khôi phục"). Từ đây mỗi thao tác ghi sổ được
   đẩy lên Firestore và chỉ hiện **Đã lưu bền · rev N** khi máy chủ đã xác nhận.

Sau bước 5, việc dùng hằng ngày không cần terminal. Chỉ deploy lại khi đổi code
(`node webapp/build_app.js` rồi `firebase deploy --only hosting:coindca` — xem "§ Runbook deploy").

> **LỊCH SỬ — đã được T-14 xử lý.** Giới hạn V1 (`DEC-021`, `H-23`) từng là: *đổi máy / đổi trình
> duyệt / cửa sổ riêng tư sinh UID mới và bị rules từ chối*. Với Google Sign-In (T-14) điều này
> **không còn đúng** — UID là của tài khoản Google, không của thiết bị. Các bước 1/4 ở trên đọc
> theo bản cập nhật ở "§ Danh tính chủ sở hữu" ngay dưới đây. Vẫn nên *Tải về JSON* định kỳ:
> backup là lớp phòng thủ độc lập với Firestore, không phải cách khắc phục mất danh tính.

Trạng thái persistence luôn hiện ở chip đầu trang và banner: *Đang lưu…*, *Đã lưu bền*, *CHƯA
LƯU* (máy chủ từ chối), *CHƯA XÁC NHẬN* (mất mạng — đừng đóng trang), *KHÔNG GHI SỔ* (chưa nạp
được nguồn bền: chưa cấu hình / không xác thực được / không nhận diện thiết bị / không đọc được /
bản bền không hợp lệ). Ở mọi trạng thái lỗi, app **khoá ghi sổ** và **không ghi đè** bản bền.

## Danh tính chủ sở hữu — Google Sign-In (T-14, bước C)

Kiến trúc sau T-14: Browser → Firebase Hosting → **Firebase Auth (Google Sign-In)** → Cloud
Firestore. `localStorage` vẫn chỉ là bản sao/cache; mất nó không mất sổ.

Thay đổi so với các bước 1 và 4 của "Thiết lập Firebase" ở trên:

- Bước 1: bật **Authentication → Sign-in method → Google** (thay cho *Anonymous*). Không cần bật
  Anonymous nữa cho CoinDCA.
- Bước 4: mở app → banner *CHƯA ĐĂNG NHẬP* → bấm **Đăng nhập bằng Google** và chọn tài khoản
  Google của chủ sở hữu. App báo *TÀI KHOẢN GOOGLE NÀY KHÔNG PHẢI CHỦ SỞ HỮU SỔ* ở lần đầu — đó
  là đúng: `firestore.rules` còn `OWNER_UID_REQUIRED`. Vào **Cài đặt** → *Chép UID*, dán vào
  `firestore.rules` thay `OWNER_UID_REQUIRED`, rồi deploy rules theo runbook dưới đây.
- Từ đó về sau: đăng nhập **cùng tài khoản Google** đó trên bất kỳ máy/trình duyệt nào cho lại
  ĐÚNG UID đó và mở ĐÚNG sổ đó. Đăng xuất rồi đăng nhập lại cũng vậy.

Hai điều KHÔNG được suy diễn sai:

- **"Đã đăng nhập" ≠ "là chủ sở hữu".** Firebase Auth là project-wide và project này dùng chung
  với app Content: một người dùng Content đã đăng nhập (kể cả bằng Google) vẫn bị từ chối vì
  `firestore.rules` so ĐÚNG MỘT UID tường minh, không so `signedIn()`.
- **Không có hệ thống nhiều người dùng.** Một chủ sở hữu, một UID. Muốn đổi chủ sở hữu = đổi UID
  trong `firestore.rules` và deploy lại rules theo runbook.

Khuyến nghị vận hành (KHÔNG bắt buộc để bước C hoàn tất, `H-42` DEFERRED): một khi CoinDCA không
còn cần Anonymous Auth, có thể **tắt hẳn Anonymous Sign-in provider** trong Firebase Console —
việc đó đóng `FB-1` tại nguồn. Chỉ làm sau khi tự xác nhận app Content không có luồng nào dựa
vào Anonymous; đó là thao tác Console, ngoài phạm vi repo này.

## Runbook deploy (T-14, bước C — bắt buộc)

Project Firebase dùng chung với app Content. Deploy **không scope** có thể đè site của Content
hoặc khoá quyền truy cập của Content. Vì vậy: **không bao giờ chạy `firebase deploy` trần**.

### Một lần: gán hosting target

`firebase.json` khai `hosting.target = "coindca"`. Ánh xạ target → site thật là thao tác một lần
của chủ sở hữu (không nằm trong repo được vì phụ thuộc site id thật):

```bash
webapp/node_modules/.bin/firebase target:apply hosting coindca <site-id-coindca> --project <PROJECT_ID>
```

### Lệnh deploy (luôn có scope)

```bash
# Hosting — chỉ site CoinDCA, không chạm site nào khác
webapp/node_modules/.bin/firebase deploy --only hosting:coindca --project <PROJECT_ID>

# Firestore rules — CHỈ SAU KHI ba bước dưới đây đều đạt
webapp/node_modules/.bin/firebase deploy --only firestore:rules --project <PROJECT_ID>
```

### Ba bước bắt buộc TRƯỚC mọi `firebase deploy --only firestore:rules`

Firestore chỉ có **một** ruleset cho toàn bộ database — không thể "deploy rules riêng cho
CoinDCA". Cô lập ở đây là **thủ tục**, không phải cấu hình:

1. **Test safe-merge PASS trên chính ruleset sắp deploy.**
   ```bash
   npm --prefix webapp run test:rules-merge
   ```
   Bộ này chạy lại toàn bộ probe hành vi Content (baseline `DEC-023`) trên Firestore Rules
   Emulator và đòi BEFORE == AFTER từng probe. Đỏ = **dừng**, không deploy.
2. **Đọc diff `firestore.rules` bằng mắt.**
   ```bash
   git diff -- firestore.rules
   ```
   Mọi thay đổi **ngoài khối `COINDCA`** là tín hiệu dừng lại và hỏi chủ sở hữu trước khi deploy.
3. **Chỉ deploy sau khi (1) và (2) đều đạt.** Không tự động hoá bằng CI (dự án cá nhân, không có
   CI — `DEC-019`/Personal Tool Simplification Principle).

Lưu ý `FB-3`: `firestore.rules` trong repo luôn giữ placeholder `OWNER_UID_REQUIRED`. Deploy lại
từ một bản checkout sạch mà quên thay UID thật sẽ **tự khoá chủ sở hữu ra ngoài**. Bước 2 của
runbook là chỗ bắt lỗi đó.

## Sao lưu và khôi phục (T-14, bước C)

Mục tiêu đã khai (Step-C spec §7.1): **RPO = 30 ngày** kể từ lần *Tải về JSON* gần nhất (khuyến
nghị xuất sau mỗi phiên nhập giao dịch); **RTO = trong một phiên sử dụng** (khôi phục là vài
thao tác trên UI, không có bước hạ tầng nào).

**Sao lưu** — **Cài đặt → Tải về JSON**. File tên `coindca-ledger-<thời-điểm>.json`, bên trong có
`schemaVersion`, `exportedAt` (ISO 8601), `state` (nguồn sự thật canonical) và `seed`. Nếu có
khối `derivedSnapshot`, nó mang nhãn `_meta: "INFORMATIONAL — NOT IMPORTED"` — **chỉ để người đọc
tham khảo, không bao giờ được nhập lại**. KHÔNG commit file backup vào Git: đó là dữ liệu tài
chính của chủ sở hữu.

**Khôi phục** — **Cài đặt → Nạp lại từ JSON**, chọn file. Trình tự bắt buộc:

1. App đọc file và **xem trước** (không ghi gì): `schemaVersion`, số giao dịch, khoảng ngày, kết
   quả validate. Bản tóm tắt hiện ở dòng thông báo TRƯỚC hộp thoại xác nhận.
2. File sai schema/hỏng → **từ chối ngay**, không snapshot, không ghi Firestore, sổ hiện tại giữ
   nguyên 100%.
3. File hợp lệ → app **tự tải xuống** `coindca-before-restore-<thời-điểm>.json` (sổ hiện tại) và
   ghi `localStorage['coindca-last-snapshot']` **trước** khi hỏi xác nhận.
4. Xác nhận → ghi nguyên tử toàn bộ sổ mới → chờ máy chủ xác nhận (*Đã lưu bền · rev N*).
5. Tải lại trang để đối chiếu: các con số phải khớp đúng bản đã sao lưu.

## Từ một bản checkout sạch (F-027)

Toàn bộ dưới đây chạy được chỉ bằng lệnh có trong repo, không cần thao tác thủ công ngoài repo.

`demo/results3/live_seed.json` **đã có sẵn trong repo** (dữ liệu DEMO/SYNTHETIC, xem
"Demo/synthetic vs Real/official" bên dưới) nên bước sinh seed KHÔNG bắt buộc — chỉ cần khi
muốn làm mới seed.

```bash
# 1. cài dependency test: Playwright + firebase (SDK compat cùng version với app_shell.html)
#    + firebase-tools (CLI deploy + Emulator Suite). package.json riêng cho webapp/, không publish.
#    Nếu môi trường đã có Chromium cài sẵn (biến PLAYWRIGHT_BROWSERS_PATH trỏ tới đó — kiểm
#    tra bằng `echo $PLAYWRIGHT_BROWSERS_PATH`), đặt PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 để
#    postinstall không tải lại; nếu chưa có, bỏ biến này để postinstall tự tải Chromium.
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm --prefix webapp install
# Emulator Firestore cần Java 11+ và tải JAR một lần (~130 MB) vào ~/.cache/firebase/emulators:
webapp/node_modules/.bin/firebase setup:emulators:firestore

# 2. build app_final.html + public/index.html (ghép shell + firebase_config + engine + logic)
node webapp/build_app.js

# 3. chạy toàn bộ cổng test của đường L-1 — mỗi test tự khởi động Auth + Firestore emulator
#    nếu chưa chạy. Đây là cổng release: nó phải thoát mã 0.
npm --prefix webapp test
```

`build_app.js` và các file `test_*.js` tự định vị đường dẫn theo `__dirname` (không theo
`process.cwd()`), nên chạy đúng bất kể gọi từ gốc repo (`node webapp/build_app.js`) hay từ
trong `webapp/` (`node build_app.js`).

### Làm mới `demo/results3/live_seed.json` (tuỳ chọn)

```bash
# cần cài engine Python trước — xem README.md ở gốc repo, mục "Cài đặt"
# (venv + `pip install -e ".[dev]"`)
ethdca --raw-dir data/raw synth --start 2024-01-01 --end 2026-06-30
ethdca --raw-dir data/raw --out-dir demo/results3 export-live
```

`webapp/app_final.html`, `webapp/public/`, `webapp/node_modules/`, log của emulator và ảnh
chụp màn hình do test sinh ra (`webapp/app-dash.png`, `webapp/app-zone.png`) là artifact sinh ra
được, không commit vào repo (`.gitignore`) — trừ `webapp/package.json`,
`webapp/package-lock.json` (ghim version) và `demo/results3/live_seed.json` (fixture demo cho
test), ba file này ĐƯỢC commit. `webapp/firebase_config.js`, `firebase.json`, `firestore.rules`
là mã nguồn, ĐƯỢC commit (config Firebase là public client config; `.firebaserc` — alias
project cục bộ — thì không).

Playwright cần một Chromium đã cài sẵn; môi trường CI/sandbox của dự án set
`PLAYWRIGHT_BROWSERS_PATH` trỏ tới bản đã cài và các test tự truyền
`executablePath: '/opt/pw-browsers/chromium'` khi khởi động trình duyệt — không gọi
`playwright install` tải lại.

## Demo/synthetic vs Real/official

`demo/results3/live_seed.json` do bước 2 ở trên sinh ra là dữ liệu **DEMO/SYNTHETIC**
(`ethdca synth`, có seed cố định, không phải Binance thật) — dùng để chứng minh app và bộ
test chạy được, KHÔNG phải bằng chứng về hiệu năng chiến lược. Muốn seed REAL/OFFICIAL, chạy
`ethdca fetch` (cần mạng Binance) trước `ethdca export-live` — xem Backtest §2. App tự nó
không phân biệt hai nguồn này trong UI (ngoài chuỗi `dataset_hash`/`strategy_config_hash`
trong file); đó là giới hạn đã biết, nằm ngoài phạm vi WP-C1 (WP-C1 chỉ kiểm chứng kế toán,
không thêm tính năng UI).

## Test

### Cổng release của đường L-1 (`npm --prefix webapp test`)

```bash
node webapp/test_t12_ledger.js              # T-12 — SC-01…SC-12 + INV-1…INV-15 trên CoinLedger
node webapp/test_t12_mutations.js           # T-12 — 7 mutant trên mã production, mỗi mutant phải bị diệt
node webapp/test_t14_deploy_isolation.js    # T-14 — hosting.target + runbook deploy 3 bước (CHECK-T14-04/05)
node webapp/test_t14_rules.js               # T-14 — rules giữ shape + ma trận danh tính 5 kịch bản (CHECK-T14-02/03)
node webapp/test_t14_persistence.js         # T-14 — Google Sign-In, multi-device, mirror-reconcile (CHECK-T14-01/11/12)
node webapp/test_t14_backup_restore.js      # T-14 — export/preview/validate/snapshot/restore (CHECK-T14-06…10)
node webapp/test_t12_browser.js             # T-12 — production reachability P-1…P-6 qua UI thật
node webapp/test_stepb_ui.js                # T-13 — production reachability Step B (AS-01…AS-12)
```

Lệnh phụ trợ:

```bash
npm --prefix webapp run test:rules-merge    # chỉ probe safe-merge rules Content (bước 1 của runbook deploy)
npm --prefix webapp run test:t14            # chỉ bốn bộ của bước C
node webapp/test_t12_owner.js <fixture.json>  # OWNER_LOCAL_ACCEPTANCE (bước D) — cần fixture local của
                                              # chủ sở hữu, KHÔNG nằm trong repo và KHÔNG nằm trong npm test
```

### Bộ test V2.1.5 đã nghỉ hưu khỏi cổng release (`npm run test:legacy-v215`)

`test_app.js`, `test_zone.js`, `test_v01_v02_v03.js`, `test_multi_month_invariant.js`,
`test_t09a_accounting.js`, `test_t09b_persistence.js` lái giao diện 5-tab của V2.1.5 (`#seedFile`
nằm trong `#tab-setup`). Bề mặt đó đã được Step-B spec §12 (`REMOVE_FROM_L1_PATH`) gỡ khỏi đường
L-1 tại `T-13`, nên sáu file này **không còn chạy lại được** — đó chính là `H-49`. Chúng **được
giữ nguyên trên đĩa** để truy vết lịch sử, nhưng **không** còn nằm trong `npm test`.

Hành vi mà chúng bảo vệ **không bị bỏ rơi**: `webapp/test_t14_persistence.js` phủ lại đúng các
kịch bản của `CHECK-T09B-01/02/03/04/10/12/16` (ghi có xác nhận máy chủ, tải lại khớp chính xác,
xoá `localStorage`, đóng/mở trình duyệt, ghi bị từ chối hiện rõ, durable hỏng fail-closed, mirror
không âm thầm thắng nguồn bền) — đo trên UI Step B hiện hành và trên danh tính Google của bước C
(`T-14`, `CHECK-T14-11`).

Các bộ chạy trên trình duyệt đều dùng `app_final.html` đã build, qua
`webapp/test_firebase_harness.js`: trang được phục vụ qua HTTP (như Hosting), Firebase SDK
**thật** (bản local cùng version, vì môi trường CI/agent chặn `gstatic.com`), Auth + Firestore
**emulator** với đúng `firestore.rules` của repo. Bản **durable** được đọc từ emulator qua REST
(độc lập với SDK trong trang) và đối chiếu bit-exact với bản trong bộ nhớ trang.

Hai giới hạn phải nói thẳng, không được coi là đã chứng minh:

1. Emulator là Firebase chạy cục bộ, **không phải** project thật của chủ dự án. Kết quả trên
   project thật/Hosting thật phải được chủ dự án tự xác nhận sau khi thiết lập.
2. `signInWithPopup()` của Firebase Auth bắt buộc nạp `https://apis.google.com/js/api.js` trước
   khi mở cửa sổ popup. Sandbox chạy test chặn mọi kết nối ra ngoài, nên **cửa sổ popup không
   hoàn tất được ở đó**. `test_t14_persistence.js` kiểm đúng điều này (`PR-AUTH-1`): app gọi
   THẬT đường popup và **fail closed** khi môi trường chặn. Phiên đăng nhập dùng cho các kịch bản
   còn lại được cấp qua chính SDK thật bằng `GoogleAuthProvider.credential()` +
   `signInWithCredential()` — cơ chế test provider chính thức của Emulator Suite — nên UID vẫn là
   UID federated `google.com` do Auth Emulator ký. Việc bấm nút và chọn tài khoản trên màn hình
   đồng ý THẬT của Google là bước chủ dự án phải tự xác nhận một lần khi thiết lập.

## Những gì app CHƯA làm

Có chủ đích, để không giả vờ đầy đủ hơn thực tế:

- **Return24H dùng daily return làm xấp xỉ.** Spec tính trên 96 nến 15m; app chỉ có dữ liệu
  daily. Nhãn regime vì vậy là gần đúng.
- **Base schedule Day 3/13/23 và Month-End chưa tự động.** Bạn tự nạp vốn và tự mua.
- **Crash ladder chưa tự sinh.** Chỉ có Smart và Opportunity ladder tạo thủ công.
- **Cooldown 48h và daily limit 20% chưa cưỡng chế** trong app.

Những phần đó đã có trong engine Python (`src/eth_dca_os/engine.py`) và chạy đúng trong
backtest; app chỉ chưa port sang.
