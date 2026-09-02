# App theo dõi trên web

App single-user để theo dõi vốn, ladder và danh mục theo ETH DCA OS V2.1.5.

**Từ T-09B (2026-09-02):** app chạy trên **Firebase Hosting**, sổ kế toán lưu bền trên **Cloud
Firestore** (`ethdca/state` + `ethdca/seed`), nhận diện trình duyệt bằng **Firebase Anonymous
Auth** (`DEC-019`/`DEC-020`/`DEC-021`). Bản artifact cũ
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
   Bật **Authentication → Sign-in method → Anonymous**. Tạo **Firestore Database** (production
   mode — rules của repo sẽ được deploy đè lên). Thêm một **Web app** trong Project settings và
   chép khối config (`apiKey`, `authDomain`, `projectId`, `appId`).
2. Điền config vào `webapp/firebase_config.js` (đây là public client config, không phải secret;
   KHÔNG bao giờ đưa service account/private key vào repo). Build lại:
   `node webapp/build_app.js` → sinh `webapp/public/index.html`.
3. Deploy (cần `npm --prefix webapp install` để có `firebase` CLI trong `webapp/node_modules/.bin`,
   và `firebase login` một lần):
   ```bash
   webapp/node_modules/.bin/firebase deploy --project <PROJECT_ID>
   ```
   Lệnh này đẩy cả Hosting (`webapp/public`) lẫn `firestore.rules`.
4. Mở URL Hosting bằng **đúng trình duyệt sẽ dùng hằng ngày**. App báo *KHÔNG NHẬN DIỆN ĐƯỢC
   THIẾT BỊ/TRÌNH DUYỆT NÀY* — đó là đúng: rules còn `OWNER_UID_REQUIRED`. Vào tab **Thiết lập**
   → *Chép UID*, dán vào `firestore.rules` thay cho `OWNER_UID_REQUIRED`, rồi:
   ```bash
   webapp/node_modules/.bin/firebase deploy --only firestore:rules --project <PROJECT_ID>
   ```
5. Tải lại app → chip đầu trang hiện *Chưa có bản bền — sổ trống*. Nạp `live_seed.json` (tab
   Thiết lập) và, nếu có dữ liệu cũ, *Nạp lại từ JSON*. Từ đây mỗi thao tác ghi sổ được đẩy lên
   Firestore và chỉ hiện **Đã lưu bền · rev N** khi máy chủ đã xác nhận.

Sau bước 5, việc dùng hằng ngày không cần terminal. Chỉ deploy lại khi đổi code
(`node webapp/build_app.js` rồi `firebase deploy`).

Giới hạn V1 đã được chủ dự án chấp nhận (`DEC-021`, `H-23`): **đổi máy / đổi trình duyệt / cửa
sổ riêng tư sinh UID mới và bị rules từ chối** — sổ vẫn nguyên trên Firestore, chỉ không đọc được
từ thiết bị đó. Lối thoát: *Tải về JSON* ở máy cũ, *Nạp lại từ JSON* ở máy mới (và đổi UID trong
rules nếu chuyển hẳn máy). Vì vậy vẫn nên *Tải về JSON* định kỳ.

Trạng thái persistence luôn hiện ở chip đầu trang và banner: *Đang lưu…*, *Đã lưu bền*, *CHƯA
LƯU* (máy chủ từ chối), *CHƯA XÁC NHẬN* (mất mạng — đừng đóng trang), *KHÔNG GHI SỔ* (chưa nạp
được nguồn bền: chưa cấu hình / không xác thực được / không nhận diện thiết bị / không đọc được /
bản bền không hợp lệ). Ở mọi trạng thái lỗi, app **khoá ghi sổ** và **không ghi đè** bản bền.

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

# 3. chạy toàn bộ test — mỗi test tự khởi động Auth + Firestore emulator nếu chưa chạy
node webapp/test_app.js
node webapp/test_zone.js
node webapp/test_v01_v02_v03.js
node webapp/test_multi_month_invariant.js
node webapp/test_t09a_accounting.js
node webapp/test_t09b_persistence.js
# hoặc gộp cả sáu:
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

```bash
node webapp/test_app.js                    # luồng: nạp seed -> vốn -> P2P -> ladder -> mua -> reload
node webapp/test_zone.js                    # zone fill, partial fill, invalidation và release đúng kế toán
node webapp/test_v01_v02_v03.js             # WP-C1 — kết luận E1 cho V-01/V-02/V-03 (xem docs/tasks/WP-C1-*.md)
node webapp/test_multi_month_invariant.js   # WP-C1 — bất biến TOTAL=A+R+D qua kịch bản đa tháng đầy đủ
node webapp/test_t09a_accounting.js         # T-09A — sáu bất biến kế toán A–F (68 assertion)
node webapp/test_t09b_persistence.js        # T-09B — 14/16 REQUIRED check persistence (09 = ba test trên, 13 = npm test)
```

Tất cả chạy trên `app_final.html` đã build, qua `webapp/test_firebase_harness.js`: trang được
phục vụ qua HTTP (như Hosting), Firebase SDK **thật** (bản local cùng version, vì môi trường
CI/agent chặn `gstatic.com`), Auth + Firestore **emulator** với đúng `firestore.rules` của repo.
`test_helpers.readState()` chờ máy chủ xác nhận rồi đọc bản **durable** từ emulator qua REST
(độc lập với SDK trong trang) và đối chiếu bit-exact với bản trong bộ nhớ — nên các test kế toán
chạy trên state đã round-trip Firestore (CHECK-T09B-09). Emulator là Firebase chạy cục bộ, **không
phải** project thật: kết quả trên project thật/Hosting thật phải được chủ dự án xác nhận sau khi
thiết lập (mục "Thiết lập Firebase").

## Những gì app CHƯA làm

Có chủ đích, để không giả vờ đầy đủ hơn thực tế:

- **Return24H dùng daily return làm xấp xỉ.** Spec tính trên 96 nến 15m; app chỉ có dữ liệu
  daily. Nhãn regime vì vậy là gần đúng.
- **Base schedule Day 3/13/23 và Month-End chưa tự động.** Bạn tự nạp vốn và tự mua.
- **Crash ladder chưa tự sinh.** Chỉ có Smart và Opportunity ladder tạo thủ công.
- **Cooldown 48h và daily limit 20% chưa cưỡng chế** trong app.

Những phần đó đã có trong engine Python (`src/eth_dca_os/engine.py`) và chạy đúng trong
backtest; app chỉ chưa port sang.
