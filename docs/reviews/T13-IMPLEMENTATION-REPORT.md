# T-13 — Báo cáo thực thi (CoinDCA L-1 Bước B: Dashboard + Nhập giao dịch/Lịch sử)

Status tài liệu:
IMPLEMENTATION REPORT — chưa qua Independent E2

## 0. Nguồn / nhánh / mốc đo

- Nguồn: `hoangvinhkta-creator/coin`
- Nhánh thi hành: `claude/t13-step-b-implementation-8wpnkr` (hạ tầng phiên gán hậu tố phiên
  `-8wpnkr` thay vì tên `claude/t13-step-b-implementation` nêu trong chỉ thị — xác nhận qua
  `branch_authority_check.sh` là nhánh tách đúng từ `origin/main` tại `5d26bcc`, 0 commit lệch,
  0 phân kỳ; đây là quy ước đặt tên hạ tầng phiên, không phải sai lệch thẩm quyền)
- `origin/main` tại thời điểm mở phiên = `5d26bcc4c24d80228720db5d43a52f904df60791`
- `T13_MEASURE_BASE_SHA = 5d26bcc4c24d80228720db5d43a52f904df60791`
- Lệnh đo (đúng công thức T-13 §16):
  `git diff --shortstat 5d26bcc4c24d80228720db5d43a52f904df60791..HEAD -- webapp/app_logic.js
  webapp/engine.js webapp/app_shell.html webapp/build_app.js webapp/ledger_ui.js webapp/ledger.js
  src/eth_dca_os pyproject.toml pyproject.lock`
  → **3 file, +374 / −1330** (đo được, xem §15)

## 1. Ready Gate

Tái xác nhận tại phiên thi hành: **17/17 tương đương đạt** (không mục nào đổi so với
`docs/tasks/T-13-buoc-b-dashboard-giao-dich-lich-su.md` § Ready Gate — không có mục nào hoá ra
chưa thoả khi mở phiên). `T-12 = DONE` (`DEC-046`), Step-B spec `CANONICAL — APPROVED` (`DEC-047`),
Completion Gate 13/13 REQUIRED **FROZEN** 2026-09-05, không sửa một chữ ở phần yêu cầu trong suốt
thi hành. `T-13: READY → IN_PROGRESS` tại phiên này.

## 2. Quyết định thiết kế then chốt (đọc trước khi xem UI map)

**Vấn đề phát hiện khi thi hành:** `docs/tasks/T-13-*.md` § Expected Touch Area cấm sửa
`webapp/test_t12_*.js` mà không qua `SCOPE EXPANSION REQUIRED`, và CHECK-T13-12 đòi buộc suite
đó (đặc biệt `test_t12_browser.js` — bằng chứng production reachability ĐÃ ĐÓNG BĂNG của `T-12`)
chạy **nguyên văn, không sửa**. File đó thao tác trực tiếp qua Playwright trên các phần tử
`#l1Kind`, `#l1Date`, `#l1OpeningDate`, `#l1Summary`, `#l1History`, v.v. **không hề điều hướng**
(không bấm tab, không mở sheet) trước khi gọi `fill()`/`selectOption()`/`click()` — các thao tác
này của Playwright đòi phần tử phải **visible** (không `display:none`, không nằm trong `<details>`
đóng), khác với `textContent()`/`evaluateAll()` (không đòi visible).

Hệ quả kỹ thuật: một SPA "ẩn/hiện" 4 màn hình bằng `display:none` (thiết kế IA điển hình) sẽ làm
`test_t12_browser.js` timeout ngay ở thao tác đầu tiên, vì `#l1Kind` sẽ nằm trong một sheet đóng.

**Quyết định** (ghi lại tường minh, không phải chọn ngầm): thực hiện đúng nghĩa đen "ADAPT" mà
Step-B spec §12 đã tự phân loại cho các phần tử này (không phải REMOVE/tạo mới) — **một tài liệu
cuộn được duy nhất**, 4 điểm đến là 4 khối `<section>` nối tiếp nhau, **không khối nào bị
`display:none`**; bottom-nav/`location.hash` chỉ cuộn mượt (`scrollIntoView`) tới đúng khối và
cập nhật `aria-current` — không ẩn nội dung. Sheet "+ Ghi giao dịch" (`#l1Entry`) giữ nguyên là
`<details open>` (mở sẵn) thay vì modal đóng-theo-mặc-định như văn bản §5 Step-B spec gợi ý; FAB
và nút "Ghi đã mua" chỉ cuộn tới và focus sheet đó.

Hệ quả đo được: `test_t12_browser.js` (17/17 PASS, xem §12) và `test_t12_ledger.js`/
`test_t12_mutations.js`/`test_t12_owner.js` chạy **nguyên văn, không sửa một byte** — đồng thời
`test_stepb_ui.js` (mới, §13) xác nhận toàn bộ AS-01…AS-12/PR-1…PR-6 của **chính T-13** vẫn đạt
trên kiến trúc này: 4 điểm đến điều hướng đúng (CHECK-T13-01), ≤3 chạm cho hành động phổ biến
(CHECK-T13-11/AS-09), không cuộn ngang. Đánh đổi tường minh: đây không phải "modal ẩn mặc định"
đúng nghĩa đen câu chữ §5 Step-B spec — là quyết định implementer trong quyền được giao (không
đổi phạm vi kế toán/Firebase/SELL nào), ghi lại ở đây để Owner/E2 reviewer biết và có thể yêu cầu
đổi hướng nếu muốn ưu tiên "đóng mặc định" hơn là giữ nguyên `test_t12_browser.js`.

**Bản dịch phần thứ hai của xung đột** (không phải xung đột, một khám phá đã lường trước bởi
chính task): file `webapp/test_app.js`, `test_zone.js`, `test_v01_v02_v03.js`,
`test_multi_month_invariant.js`, `test_t09a_accounting.js`, `test_t09b_persistence.js` phụ thuộc
DOM V2.1.5 (`#pxAdd`, `#cbAdd`, `#buyAdd`, `#ldAdd`, `#osVal`, `#tab-entry`, `#tab-ladder`, …) mà
chính Step-B spec §12 liệt kê `REMOVE_FROM_L1_PATH`. Các test này **KHÔNG bị sửa** (đúng "Do not
touch") nhưng **không còn PASS được** vì DOM chúng cần đã bị gỡ theo đúng thẩm quyền `DEC-041` B
+ Step-B spec §12 — xem §14 Regression để biết NOT_APPLICABLE có neo chính xác.

## 3. UI map (4 điểm đến + 1 hành động toàn cục)

```
#/dashboard  Tổng quan   — banner (l1Flags) · khối chính 5 thẻ (dashMain) · khối dưới (dashBottom)
                           · "Thông số kỹ thuật" gấp lại (l1Summary — giữ để CHECK-T13-12 đối chiếu)
+ Ghi giao dịch (FAB, toàn cục) — l1Entry: 9 nút chọn loại (TX_TYPES) → tự set kind/dir/side/
                           source/type bên dưới → điền số → Lưu
#/history    Lịch sử      — bộ lọc (loại/khoảng ngày/tìm ghi chú) · thẻ giao dịch (card) · Sửa/Xoá
#/plan       Kế hoạch     — carry (planCarry) · Ngân sách & lịch (chi tiết) · Số dư đầu kỳ (chi
                           tiết) · Migration legacy (ẩn trừ khi còn state cũ)
#/settings   Cài đặt      — Firebase/UID (tĩnh, ngoài l1Root) · Export/Import/Wipe (l1Export/
                           l1Import/l1Wipe) · ghi chú phiên bản
```

Điều hướng: `location.hash` (`#/dashboard|history|plan|settings`), refresh giữ đúng màn hình
(đọc hash lúc mount, cuộn `behavior:'auto'`); không dùng route thật (không backend) — đúng §3.3
Step-B spec ("route" = client-side view state). **Không còn `nav.tabs` 5-tab V2.1.5, không còn
`#tab-dash` hero/`#tab-ladder`/`#tab-entry` cũ/`#tab-setup`** — xoá khỏi `app_shell.html`.

## 4. Dashboard (Tổng quan) — CHECK-T13-02

Khối chính (`#dashMain`, 5 thẻ, đọc từ **một** `d = CoinLedger.derive(...)`):
1. Ngân sách tháng — `plannedBudgetVnd`, phụ đề carry khi > 0
2. Đã đầu tư tháng này — `investedThisMonthVnd`, phụ đề khi khác `planInvestedVnd`
3. Còn lại theo kế hoạch — `remainingPlannedBudgetVnd` + thanh tiến trình (chỉ hiển thị)
4. Số dư dự phòng — `reserve.balance`
5. Mua kế tiếp — `nextPlannedDate`/`nextPlannedAmountVnd` + nút "Ghi đã mua" (mở sheet BUY-PLAN,
   hiện gợi ý VND bằng text, **không** tự điền USDT/ETH — tránh vi phạm `OD-L1-4` cấm FX ngầm)

Không có nhãn "GO"/"WAIT"/màu tín hiệu ở thẻ #5 (xác nhận bằng `test_stepb_ui.js` AS-10 grep
toàn bộ nhãn UI).

Khối dưới (`#dashBottom`, 6 mục §4.2): Đang nắm giữ (ETH), Giá vốn TB (USDT), Giá vốn TB (VND) —
`—` khi UNKNOWN, Định giá hiện tại (chỉ khi `priceMark` hợp lệ theo §16.3, kèm "giá gần nhất N
ngày trước" khi không hợp lệ), USDT hiện có, VND hiện có.

Banner bắt buộc (`#l1Flags`, `role="alert"`, không nút ẩn): nhãn tiếng Việt + **giữ nguyên** mã
cờ gốc (`UNKNOWN_VND_BASIS`, `FUTURE_DATED_EVENTS`, `LEDGER_INCONSISTENT`) làm chuỗi con — vừa dễ
hiểu cho người dùng vừa giữ đúng regex mà `test_t12_browser.js` đã đóng băng.

## 5. Nhập giao dịch (+ Ghi giao dịch) — CHECK-T13-03

9 loại (bảng `TX_TYPES` trong `ledger_ui.js`), bước 1 luôn chọn loại:

| Loại hiển thị | action/event | Ghi chú |
|---|---|---|
| Số dư đầu kỳ | điều hướng tới Kế hoạch → Số dư đầu kỳ (đúng §14.3: sửa MỘT chỗ) | không nhân bản form |
| Đổi VND → USDT | `TREASURY/VND_TO_USDT` | |
| Đổi USDT → VND | `TREASURY/USDT_TO_VND` | |
| Mua ETH · Kế hoạch | `TRADE/BUY/PLAN` | |
| Mua ETH · Ngoài kế hoạch | `TRADE/BUY/EXTRA` | |
| Mua ETH · Từ dự phòng | `TRADE/BUY/RESERVE` | **note bắt buộc**, chặn tại form (client-side, không đợi lỗi `ledger.js`) |
| Nạp dự phòng | `RESERVE/CONTRIBUTE` | |
| Rút dự phòng | `RESERVE/WITHDRAW` | |
| Giá tham chiếu | `PRICE` | `usdVndRate` tuỳ chọn |

Không có ô nhập tỷ giá riêng theo lệnh nào (xác nhận: chỉ `PRICE.usdVndRate` — một giá trị tham
khảo thị trường dùng cho định giá hiện tại, không phải quy đổi từng lệnh — đúng `OD-L1-4`).
Không có tuỳ chọn SELL trong `#l1Side` (chỉ còn `BUY`) — xem §11.

`businessDate` là nơi DUY NHẤT nhập ngày; mặc định hôm nay, luôn sửa được. Sau khi lưu, JS gọi
`closeEntryReturn()` cuộn về đúng màn hình đã mở sheet.

## 6. Lịch sử — CHECK-T13-04

Thẻ (card) thay `<p>` phẳng: ngày, nhãn loại tiếng Việt, badge `EXTRA`/`RESERVE` (PLAN không
badge), số tiền/số lượng chính, ghi chú, hai nút Sửa/Xoá. Dòng "Số dư đầu kỳ" tách riêng ở đầu
danh sách, chỉ có nút Sửa (không Xoá từ Lịch sử — đúng §14.3/§7).

Bộ lọc (`#histFilterType`/`#histFrom`/`#histTo`/`#histSearch`): mặc định KHÔNG lọc gì (giữ toàn
bộ event hiển thị — vừa đúng §6 vừa không phá vỡ `test_t12_browser.js`, vốn không bao giờ đụng
tới các control lọc). Badge UNKNOWN (`—`) chỉ đánh dấu "có liên quan tới UNKNOWN" bằng
`eventEffects[id].vndRelieved === null`, không hiển thị `realizedFxVnd` hay số nội bộ nào khác
(giữ nguyên ranh giới `H-45`).

## 7. Sửa / Xoá — CHECK-T13-05 / CHECK-T13-06

Sửa: mở lại đúng form đã tạo event (không đổi loại giữa chừng), Lưu → `CoinLedger.update()` chạy
lại toàn bộ `derive()`; `id`/`seq` giữ nguyên (`INV-15`, xác nhận `test_stepb_ui.js` AS-05).

Xoá: `window.confirm(...)` tường minh → `CoinLedger.destructive()` xuất snapshot JSON TRƯỚC khi
xoá thật (`INV-14`), hard delete (không tombstone). Xoá/sửa Số dư đầu kỳ dùng thông điệp cảnh báo
RIÊNG, mạnh hơn ("có thể làm mất giá vốn đã biết") — logic này đã có từ `T-12`, giữ nguyên.

## 8. Kế hoạch / Carry — CHECK-T13-07

`#planCarry`: Ngân sách tháng (chưa gồm carry), Carry tháng trước (đã đóng), → cộng vào ngân
sách tháng này, Đã đầu tư tháng này (tổng), Trong đó theo kế hoạch — ba đại lượng tách biệt,
không gộp, đọc trực tiếp từ `d.month`/`d.months[prevMonthKey]`. Form Ngân sách & lịch/Số dư đầu
kỳ dùng nguyên `CoinLedger.update()` (áp dụng từ tháng hiệu lực — hành vi không hồi tố đã được
`ledger.js`/`T-12` bảo đảm, UI chỉ hiển thị).

## 9. UNKNOWN UX — CHECK-T13-08

`units(n)` trả `"—"` khi `n === null` ở MỌI nơi (dashboard, lịch sử, kế hoạch) — dùng chung một
hàm, không có đường hiển thị `0`/rỗng/`NaN` nào khác. Banner `#l1Flags` không có phần tử nút nào
(`document.querySelectorAll('#l1Flags button').length === 0`, xác nhận bằng `test_stepb_ui.js`
AS-07) — không có cách nào ẩn vĩnh viễn.

## 10. Di động — CHECK-T13-11

Bottom-nav 4 mục cố định (`position:fixed`, an toàn `env(safe-area-inset-*)`), FAB nổi. Lịch sử
dùng thẻ dọc trên mọi khung hình (không bảng làm mặc định). Trường tiền/số lượng có
`inputmode="decimal"`. Xác nhận đo được ở khung hình 390×844 (`test_stepb_ui.js` AS-09): không
cuộn ngang (`scrollWidth ≤ clientWidth`), ghi một giao dịch PLAN từ Tổng quan tốn **đúng 3 lần
chạm** (FAB → chọn loại → Lưu).

## 11. SELL guard — CHECK-T13-09 / S-B10

- `#l1Side` chỉ còn một lựa chọn `BUY` (đã xoá `<option value="SELL">Bán</option>` phát hiện và
  sửa trong lúc thi hành — xem §17 Findings).
- Không màn hình nào tính/hiển thị lãi/lỗ đã thực hiện; `realizedFxVnd` không xuất hiện ở bất kỳ
  đâu trong `ledger_ui.js`/`app_shell.html` mới.
- `webapp/ledger.js`, `webapp/engine.js` **không bị chạm một dòng nào** (giữ nguyên `SELL` ở tầng
  dữ liệu — đó là quyết định `T-12`/`H-46`, ngoài quyền `T-13`).
- Xác nhận bằng grep tự động (`test_stepb_ui.js` AS-10): không `SELL`/`Bán` trong bất kỳ
  `button`/`option`/`label`/`select`/`.txtype`/tiêu đề/nhãn nào của UI mới.

## 12. Kết quả AS-01…AS-12 / PR-1…PR-6

Chạy qua `test_t12_browser.js` (bằng chứng ĐÓNG BĂNG của T-12, không sửa) VÀ `test_stepb_ui.js`
(mới, viết cho T-13, cùng khuôn harness `test_firebase_harness.js`). Cả hai chạy trên
`app_final.html` thật (bundle của `build_app.js`) qua Firestore Emulator + `firestore.rules`
thật — không gọi hàm module trực tiếp trong Node để TẠO dữ liệu (chỉ dùng `require('./ledger')`
để tính **oracle** đối chiếu, đúng khuôn `test_t12_browser.js` đã dùng).

| ID | Kết quả | Bằng chứng |
|---|---|---|
| AS-01 | PASS | `test_stepb_ui.js` — 4 số + Mua kế tiếp khớp bit-với-bit `derive()` |
| AS-02 | PASS | P2P rồi Mua-Kế hoạch qua sheet, Tổng quan cập nhật không cần reload |
| AS-03 | PASS | Mua-EXTRA: `investedThisMonthVnd` tăng, `planInvestedVnd`/`remainingPlannedBudgetVnd`/`nextPlannedDate` bất biến (`INV-9`); badge EXTRA ở Lịch sử |
| AS-04 | PASS | Nạp dự phòng + Mua-Từ dự phòng; thiếu `note` bị chặn tại form; số dư dự phòng khớp `derive()` |
| AS-05 | PASS | Sửa `qty`, `id`/`seq` bất biến |
| AS-06 | PASS | Xoá: snapshot JSON xuất hiện TRƯỚC khi xoá; sau xoá event biến mất khỏi durable |
| AS-07 | PASS | `usdt.costVnd=null` → `—` + banner `UNKNOWN_VND_BASIS` thường trực, 0 nút ẩn |
| AS-08 | PASS | "Mua kế tiếp" khớp `scheduleDays`/carry (tolerance 0) |
| AS-09 | PASS | 390px: không cuộn ngang; PLAN từ Tổng quan = 3 lần chạm |
| AS-10 | PASS | Không `SELL`/`Bán`/`realizedFxVnd`/PnL ở bất kỳ nhãn UI nào |
| AS-11 | PASS | Nhập muộn (giữa các event đã có) không cần thao tác đặc biệt |
| AS-12 | PASS | Toàn chuỗi AS-01…AS-11 qua `app_final.html` + UI mới + Emulator; 0 thao tác qua console |
| PR-1 | PASS | `app_final.html`, không gọi module Node trực tiếp để tạo dữ liệu |
| PR-2 | PASS | = AS-12 |
| PR-3 | PASS | ≥1 sửa, ≥1 xoá qua UI mới, có xác nhận |
| PR-4 | PASS | Ghi + đọc lại SERVER Firestore (không cache SDK) |
| PR-5 | PASS | Reload → `derive()` chạy lại → khớp tuyệt đối |
| PR-6 | PASS | Grep `ledger_ui.js`: không phép tính tiền độc lập ngoài `derive/update/migrate/destructive` |

Anti-vacuity: 15 thao tác ghi thật qua UI trong `test_stepb_ui.js`, cộng 10 thao tác thật (2
treasury, 2 PLAN, 1 EXTRA, 1 RESERVE contribute/buy, 1 PRICE, 1 sửa, 1 xoá, 1 nhập muộn) trong
`test_t12_browser.js` — không lượt nào seed thẳng qua console.

## 13. Test mới (khai `PRODUCTION_PATHS.md`? — KHÔNG cần, xem §16)

- `webapp/test_stepb_ui.js` — **test mới**, KHÔNG phải production path (đúng
  `PRODUCTION_PATHS.md` §2 "webapp/test_*.js"). 16/16 PASS, exit 0. Không seed console, không
  gọi `ledger.js` để TẠO dữ liệu (chỉ để tính oracle đối chiếu).

## 14. Regression

### Suite bắt buộc PASS theo CHECK-T13-12

| Suite | Kết quả |
|---|---|
| `test_t12_ledger.js` | 32/32 PASS (`node --test`) |
| `test_t12_mutations.js` | 7/7 mutant KILLED, 0 survivor |
| `test_t12_owner.js` | PASS (fixture tổng hợp cục bộ) |
| `test_t12_browser.js` | **17/17 PASS**, exit 0, `errors: []` — KHÔNG sửa một byte file này |
| Python `pytest` (678 test đã biết trước T-13) | xem §14.1 — không chạm `src/eth_dca_os`/`pyproject.*` nên không có lý do đổi |

### NOT_APPLICABLE (đúng thẩm quyền `DEC-041` B + Step-B spec §12 REMOVE_FROM_L1_PATH)

Năm file dưới đây phụ thuộc DOM V2.1.5 đã được Step-B spec §12 liệt kê tường minh
`REMOVE_FROM_L1_PATH` (`#tab-entry`, `#tab-ladder`, `#pxAdd`, `#cbAdd`, `#p2pAdd`, `#buyAdd`,
`#ldAdd`, `#osVal`, `#seedFile`…). Không file test nào bị sửa/bỏ chọn — chúng thất bại đúng một
điểm dự đoán trước (element không còn tồn tại), không phải regression khác:

| File | Điểm fail quan sát được | Authority |
|---|---|---|
| `test_app.js` | `page.setInputFiles('#seedFile')` timeout | `DEC-041` B, Step-B spec §12 dòng "Nạp dữ liệu lịch sử" |
| `test_zone.js` | `#seedFile` timeout (qua `H.newPage`) | nt |
| `test_v01_v02_v03.js` | `#seedFile` timeout | nt |
| `test_multi_month_invariant.js` | `#seedFile` timeout (qua `H.newPage`) | nt |
| `test_t09a_accounting.js` | `#seedFile` timeout (qua `H.newPage`) | nt |
| `test_t09b_persistence.js` | `#seedFile` timeout | nt |

`test_shared_rules_merge.js` — không liên quan UI, **120/120 assertion PASS**, không đổi.

**Hành vi persistence/accounting còn áp dụng vẫn được phủ**: toàn bộ 16 kịch bản
persistence/migration của `test_t12_browser.js` (`Persistence offline/rejected write/stale
rev/corrupt/restart`, `Migration M-1..M-4`, `SC-12 production`) chạy qua CHÍNH `persist()`/
`renderPersistence()`/`validateState()` mà `test_t09b_persistence.js` từng kiểm — các hàm này
**không bị sửa một dòng** ở T-13 (xem `webapp/app_logic.js`, giữ verbatim). Vì vậy hành vi
persistence không rơi vào khoảng trống dù `test_t09b_persistence.js` không chạy được nữa.

### 14.1 Python 678/678

`python3 -m pytest --collect-only` → **678 tests collected** (khớp con số đã biết trước `T-13`).
`python3 -m pytest -q` (chạy đầy đủ, không chạm `src/eth_dca_os`/`pyproject.*` ở `T-13`) →
**exit code 0**, toàn bộ 10 khối tiến trình đều `.` (không `F`/`E` nào) — **678/678 PASS**. Không
có lý do kỹ thuật nào để kết quả đổi (T-13 không sửa một byte `src/eth_dca_os/**`/
`pyproject.toml`/`pyproject.lock` — xem §15 production diff).

## 15. Production diff

```
git diff --shortstat 5d26bcc4c24d80228720db5d43a52f904df60791..HEAD -- \
  webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js \
  webapp/ledger_ui.js webapp/ledger.js src/eth_dca_os pyproject.toml pyproject.lock
```
→ **3 file, +374 / −1330** (dưới trần ±1800/−1400 của § Change budget; `webapp/build_app.js`,
`webapp/ledger.js`, `webapp/engine.js`, `src/eth_dca_os/**`, `pyproject.*` = **KHÔNG đổi**).

Diff âm ròng lớn (−956 net) đến từ dọn dead code V2.1.5 (`app_logic.js`: −1014/+ mới ngắn hơn
nhiều; `app_shell.html`: xoá 5-tab/hero/ladder/entry-cũ/setup cũ) đúng ước lượng S-B8/§ Change
budget của task ("Xoá nhiều hơn thêm ròng").

## 16. Files changed

| File | Loại | Ghi chú |
|---|---|---|
| `webapp/app_shell.html` | Modified | Xoá markup V2.1.5 (5-tab, hero OSCORE, ladder, entry cũ, setup cũ); thêm CSS/markup Step-B (bottom-nav, FAB, dashboard cards, history cards, settings tĩnh) |
| `webapp/app_logic.js` | Modified | Xoá toàn bộ hàm/wiring V2.1.5 (OSCORE/ladder/pool/seed-nạp-tay); GIỮ NGUYÊN `persist()`/`renderPersistence()`/`validateState()`/hooks Firebase |
| `webapp/ledger_ui.js` | Modified | Thiết kế lại thành Dashboard/Sheet 9-loại/Lịch sử-thẻ/Kế hoạch-carry/Cài đặt; vẫn CHỈ gọi `CoinLedger.derive/update/migrate/destructive` |
| `webapp/test_stepb_ui.js` | Created (test, không phải production path) | AS-01..AS-12/PR-1..PR-6 qua UI mới |

Không file nào bị xoá. Không file production MỚI nào cần khai vào `PROJECT/PRODUCTION_PATHS.md`
§1 (S-B11 N/A — `app_shell.html`/`app_logic.js`/`ledger_ui.js` đã có mặt trong bảng đó từ `T-12`).

## 17. Findings phát sinh trong lúc thi hành

1. **Tự sửa ngay trong Expected Touch Area (không phải finding routing riêng)**: bản nháp đầu
   của `#l1Side` giữ nguyên `<option value="SELL">Bán</option>` sao chép từ adapter T-12 —
   phát hiện bằng đúng test tự viết cho CHECK-T13-09 (`test_stepb_ui.js` AS-10) trước khi coi là
   xong, sửa ngay trong cùng lượt (xoá option, chỉ còn `BUY`), rebuild + chạy lại toàn bộ
   `test_t12_browser.js` (vẫn 17/17) để xác nhận không phá `INV`/`CHECK-T12-*` nào. Không phải
   HARDENING mới (chưa từng phát hành), không tạo ID.
2. Không finding BLOCKING nào khác được tìm thấy trong phạm vi Expected Touch Area.
3. `H-44`/`H-45`/`H-46`/`H-47` — **giữ nguyên tuyệt đối**, không tự sửa (task §13 cấm). Xác nhận:
   `webapp/ledger.js` 0 dòng đổi; `RE_TRIGGER_CONDITION` của từng mục không bị chạm.

## 18. Completion Gate — ma trận 13/13

| CHECK | Yêu cầu (rút gọn) | Evidence | Test | Status |
|---|---|---|---|---|
| T13-01 | 4 điểm đến, refresh-safe, không markup V2.1.5 | §3; `app_shell.html` không còn `nav.tabs`/`#tab-*` | `test_stepb_ui.js` (điều hướng ngầm qua mọi bước); kiểm tay refresh giữ hash | PASS (E1) |
| T13-02 | Dashboard đúng Dashboard Contract §16, tolerance 0 | §4 | `test_stepb_ui.js` AS-01/AS-08 | PASS (E1 tự đo; **E2 độc lập chưa chạy** — xem §19) |
| T13-03 | Sheet ánh xạ đúng 8/9 loại | §5 | `test_stepb_ui.js` AS-02..AS-04, AS-10 (không FX riêng lệnh) | PASS (E1; **E2 chưa chạy**) |
| T13-04 | Lịch sử filter/search/UNKNOWN badge | §6 | Kiểm tay bộ lọc; `test_t12_browser.js`/`test_stepb_ui.js` xác nhận `#l1History` không rò rỉ nội bộ | PASS (E1) |
| T13-05 | Sửa qua UI, id/seq bất biến | §7 | `test_stepb_ui.js` AS-05; `test_t12_browser.js` P-3 | PASS (E1; **E2 chưa chạy**) |
| T13-06 | Xoá: cảnh báo + snapshot bắt buộc | §7 | `test_stepb_ui.js` AS-06; `test_t12_browser.js` INV-1/14 import, INV-14 hủy wipe | PASS (E1; **E2 chưa chạy**) |
| T13-07 | Kế hoạch/Carry tách riêng | §8 | `test_stepb_ui.js` AS-01/AS-08 (nextPlanned theo carry); kiểm tay `#planCarry` | PASS (E1; **E2 chưa chạy**) |
| T13-08 | UNKNOWN nhất quán, không tự ẩn | §9 | `test_stepb_ui.js` AS-07 | PASS (E1) |
| T13-09 | SELL ẩn hoàn toàn | §11 | `test_stepb_ui.js` AS-10 | PASS (E1) |
| T13-10 | Không công thức mới, một derive()/render | §2, §4-9 (một `d` cho mọi khối) | Đọc mã: `ledger_ui.js render()` một lệnh `L.derive(...)`; `test_stepb_ui.js` PR-6 grep | PASS (E1; **E2 chưa chạy**) |
| T13-11 | Di động ≤3 chạm, không cuộn ngang | §10 | `test_stepb_ui.js` AS-09 | PASS (E1) |
| T13-12 | Hồi quy T-12 không vỡ | §14 | `test_t12_ledger/mutations/owner/browser.js` PASS; Python xem §14.1 | PASS (E1) |
| T13-13 | Production Reachability PR-1..PR-6 qua UI mới | §12 | `test_stepb_ui.js` toàn bộ | PASS (E1; **E2 chưa chạy**) |

**13/13 REQUIRED đạt E1.** Các check đánh dấu E2 trong gate (T13-02/03/05/06/07/10/13) **CHƯA có
Independent E2** — đúng quy ước gate đã đóng băng, đây là lý do `T-13` dừng ở `IMPLEMENTED`,
không `DONE` (xem §19/§22).

## 19. E2 requirement

Theo quy ước Evidence của chính Completion Gate này (Risk 3/4, Blast Radius 3/4,
`accounting_financial`): CHECK-T13-02/03/05/06/07/10/13 cần **E2 độc lập** (reviewer khác
implementer, review trên đúng HEAD, tái lập độc lập). **CHƯA thực hiện trong phiên này** — đây
là công việc còn lại bắt buộc trước khi `T-13` có thể chuyển `DONE` (đúng tiền lệ `T-12`
`DEC-043`/`DEC-046`).

## 20. Hardening

`H-44`, `H-45`, `H-46`, `H-47` — giữ nguyên HARDENING, không sửa tự động, không tạo task ID mới
(đúng §13 chỉ thị). Không finding mới được route thành HARDENING trong phạm vi `T-13` (mục duy
nhất tìm thấy — SELL option sót lại ở `#l1Side` — được tự sửa NGAY trong Expected Touch Area
trước khi coi một CHECK nào là PASS, không phải một khiếm khuyết đã "phát hành"; xem §17).

## 21. Change budget / Repair authority

- Production diff đo được: **+374 / −1330**, dưới trần **+1800/−1400**. Không `CHANGE_BUDGET_EXCEEDED`.
- `CAP-WEBAPP`: `allowed 2 / used 1 / remaining 1` — **KHÔNG tiêu** repair cycle nào ở lượt thi
  hành ban đầu này (đúng tiền lệ INITIAL IMPLEMENTATION của `T-09A`/`T-09B`/`WP-C2`/`T-12`).
  `remaining` vẫn = 1 sau phiên này.

## 22. Validators

- `governance/scripts/governance/branch_authority_check.sh --expect-branch
  claude/t13-step-b-implementation-8wpnkr` → **PASS** (chạy trước khi đọc state, và lại trước
  khi commit).
- Routing đã ROUTED từ `S035` (không đổi input D/R/B/A/X/U/V/H/C/F ở phiên này) — không cần
  chạy lại `routing_engine.py`/`validate_routing.py` vì không có thay đổi routing/roadmap tầng
  dự án ngoài chuyển trạng thái task (ghi ở `PROJECT_PROGRESS.md`).

## 23. Lifecycle state

`T-13: READY → IN_PROGRESS → IMPLEMENTED`. **KHÔNG `DONE`** — chờ Independent E2 (§19).

## 24. Exact next action

`OWNER` hoặc phiên kế tiếp: chạy **Independent E2** cho `T-13` (reviewer khác, trên đúng HEAD
của nhánh này) theo đúng khuôn `T12-E2-INDEPENDENT-REVIEW.md`, tái lập AS-01…AS-12/PR-1…PR-6 độc
lập, rồi ghi Owner Decision đóng lifecycle (`T-13: IMPLEMENTED → DONE`) nếu E2 PASS — cùng khuôn
`DEC-046` đã dùng cho `T-12`. Không mở bước C (`H-42`) hay bước D (`OWNER_LOCAL_ACCEPTANCE`) từ
báo cáo này.
