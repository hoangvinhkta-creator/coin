# T-17 — Báo cáo gộp (implementation + bằng chứng E2) — sắp xếp lại giao diện CoinDCA L-1

**Phiên:** 2026-09-06 · **Nhánh:** `claude/coincda-ui-reorganize-2ykjse`
**Nguồn yêu cầu:** chỉ thị phiên trực tiếp của Owner sau khi tự nhập kế hoạch + 102 sự kiện thật
vào production, phát hiện hai vấn đề usability trên giao diện `T-16` đã deploy.
**Task:** `docs/tasks/T-17-sap-xep-lai-giao-dien-coindca.md` · **Quyết định:** `DEC-053`

Báo cáo này GỘP implementation report + bằng chứng E2 vào một file theo đúng ngân sách artifact
cứng đã dùng cho `T-15`/`T-16` (Owner nhắc lại trong chỉ thị). Không có evidence log
(`.txt`/`.json`/`.log`) nào được commit; mọi số liệu tóm tắt nằm ngay trong file này và tái lập
được bằng các lệnh ghi kèm.

---

## 1. Xác nhận mô tả so với code thật (làm TRƯỚC mỗi sửa)

Đã đọc toàn bộ `webapp/ledger_ui.js` (kể cả khối comment id hợp đồng ở đầu file),
`webapp/app_shell.html` phần `<style>`, và grep trực tiếp `test_t12_browser.js`/
`test_stepb_ui.js` để xác nhận những gì hai test này thực sự thao tác trước khi đổi bất kỳ dòng
nào.

| Mô tả trong chỉ thị | Code thật | Nhận xét |
|---|---|---|
| `renderDashBottom` nối `holdingRows()` + 4 dòng thành một mảng, render bằng `.stat` | đúng — `ledger_ui.js` (trước sửa) dòng ~311-321 | khớp |
| `.txtype`/`.txtype.aria-pressed` là mẫu nút pill có sẵn dùng cho form nhập | đúng — `app_shell.html` `.txtypes`/`.txtype`, dùng bởi `TX_TYPES` trong `mount()` | khớp |
| `.histfilter` hiện chứa 1 select + 2 input date + 1 input search | đúng — `mount()` dòng ~370 (trước sửa) | khớp |
| Khối comment đầu `ledger_ui.js` liệt kê id hợp đồng cho `test_t12_browser.js` | đúng, nhưng **danh sách đó KHÔNG gồm `histFilterType`/`histFrom`/`histTo`/`histSearch`/`dashBottom`/`dashMain`** — grep trực tiếp `test_t12_browser.js` xác nhận file này không chạm bốn id lọc lịch sử, còn `dashBottom`/`dashMain` chỉ được `test_stepb_ui.js` dùng qua `#dashBottom .stat`/`#dashMain .dcard` (descendant selector, không phụ thuộc cấu trúc lồng bên trong) | quan trọng cho quyết định ở §3 — không lệch với chỉ thị, chỉ là chi tiết chỉ thị không nêu rõ |

Không có chỗ nào mô tả trong chỉ thị lệch với code thật tới mức phải DỪNG.

---

## 2. Thay đổi thực tế (đo trực tiếp, không cộng tay)

    git diff --stat 4819a13..HEAD -- webapp/ledger_ui.js webapp/app_shell.html
      webapp/app_shell.html | 39 +++++++++++++++++++---
      webapp/ledger_ui.js   | 90 +++++++++++++++++++++++++++++++++++++++------------
      2 files changed, 104 insertions(+), 25 deletions(-)

    # lớp tính toán — PHẢI RỖNG theo Ràng buộc bắt buộc #1 của chỉ thị
    git diff --stat 4819a13..HEAD -- webapp/ledger.js src/eth_dca_os docs/spec firestore.rules
      (rỗng)

    # toàn bộ webapp/ — xác nhận đúng hai file, không file thứ ba nào bị chạm
    git diff --stat 4819a13..HEAD -- webapp
      (giống hệt hai dòng đầu tiên ở trên)

Trong ước lượng change budget của task (≤ 2 file, ≤ 200 dòng). Không `CHANGE_BUDGET_EXCEEDED`.
Không file test nào bị sửa (xem §4).

### 2.1 Nội dung từng phần

**Mục 1 — `renderDashBottom`/`holdingRows` tách 3 khối.** `holdingRows(d,s,today)` giữ nguyên
100% (không đổi một ký tự). `renderDashBottom` nay dựng ba khối `<div class="dashgroup">` bên
trong `#dashBottom` (id container ngoài giữ nguyên): "Đang nắm giữ" (nội dung = đúng
`holdingRows()`, hoặc `<p class="empty">Chưa có coin nào.</p>` khi rỗng), "Tiền mặt & USDT"
(USDT/VND hiện có, không đổi nhãn/số), "Lãi/lỗ đã thực hiện" (2 dòng USDT/VND, thêm `class="chip
g"` khi > 0, `"chip r"` khi < 0, không class khi = 0 — dùng `.stat` gốc không đổi, chỉ thêm class
lên `<div>` giá trị). Chú thích "hai đơn vị khác nhau, không cộng chung" dời xuống thành
`<p class="dashgroup-note">` dưới khối P&L, không bị xoá.

**Mục 2 — tiêu đề nhóm cho `renderDashMain`.** Không sửa một dòng nào trong hàm
`renderDashMain()`. Thêm đúng một `<h3 class="dashgroup-title">Kế hoạch tháng này</h3>` tĩnh
trong `mount()`, ngay trên `<div class="dashmain" id="dashMain">`.

**Mục 3 — bộ lọc lịch sử dạng nút có đếm.** Thêm hằng `HIST_FILTERS` (9 loại + "Tất cả loại", copy
nguyên nhãn từ các `<option>` cũ) và hàm `matchesHistType(e, type)` — trích XUẤT nguyên logic
if/else-if đã có trong `filterHistory` (không viết lại, không đổi ngữ nghĩa; xem diff — mỗi nhánh
map 1-1 sang một `return` trong hàm mới). `filterHistory` gọi lại hàm này. `renderHistFilterButtons
(events)` build 9 nút `.histtype` với text `"<nhãn> (<n>)"`, `n` đếm trên TOÀN BỘ `s.events` qua
`matchesHistType`, không lọc theo ngày/tìm-kiếm. `#histFilterType` (select) **giữ nguyên id**,
chuyển `hidden` — xem lựa chọn kiến trúc ở §3.

**Mục 4 — icon/màu theo loại giao dịch.** Hàm `KIND_BADGE(e)` mới, độc lập với `KIND_LABEL` đã
có (không sửa `KIND_LABEL`): TRADE/BUY → `.hc-kind-buy` (xanh lá, "↑"); TRADE/SELL →
`.hc-kind-sell` (đỏ, "↓"); CASH → `.hc-kind-cash` (xanh dương, "$", dùng biến CSS mới
`--cash`/`--cash-bg`); TREASURY → `.hc-kind-treasury` (xám/trung tính, "⇄"); PRICE →
`.hc-kind-price` (viền nhạt, "≈"); RESERVE → chuỗi rỗng (giữ nguyên như trước task này, đúng yêu
cầu "RESERVE giữ như hiện tại — không đổi"). Badge output được chèn cạnh `hc-date` trong
`hc-top`, TRƯỚC các badge/chip cũ (nguồn EXTRA/RESERVE, TƯƠNG LAI, UNKNOWN) — không xoá badge nào.

**Mục 5 — responsive.** `.dashbottom-groups{grid-template-columns:1fr 1fr}` (base, desktop) +
`@media (max-width:860px){.dashbottom-groups{grid-template-columns:1fr}}` — khớp breakpoint
`.hero` đã dùng sẵn trong file. **Một lỗi tự phát hiện và tự sửa trước khi coi là xong:** lần đầu
đặt override 1-cột vào TRONG khối `@media(max-width:860px)` đã có sẵn ở gần đầu file (cho
`.hero`/`.fbar`), nhưng rule base 2-cột lại nằm SAU nó trong nguồn (ở khối Step B) — CSS cùng độ
cụ thể thắng theo thứ tự nguồn, nên rule base luôn đè rule trong media query bất kể viewport,
khiến mobile không bao giờ chuyển 1 cột. Phát hiện bằng đo `getComputedStyle` thật (không chỉ đọc
CSS nguồn — đúng yêu cầu Completion Gate CHECK-T17-09), sửa bằng cách đặt `@media` override NGAY
SAU rule base trong cùng khối Step B. Xem §5.5 để có bằng chứng đã đo lại sau khi sửa.

---

## 3. Quyết định bắt buộc phải nêu rõ (ràng buộc #3 của chỉ thị): `#histFilterType`

**Đã chọn: GIỮ `#histFilterType`, chuyển thành `<select hidden aria-hidden="true">` đồng bộ giá
trị với bộ nút `.histtype` mới.** Không chọn phương án "đổi hẳn sang nút + sửa test".

Lý do:

1. Grep trực tiếp `test_t12_browser.js` và `test_stepb_ui.js` (toàn bộ 2 file, không chỉ tìm theo
   từ khoá) xác nhận **không dòng nào** của cả hai test thao tác `#histFilterType`,
   `#histFrom`, `#histTo`, hay `#histSearch` — không `selectOption`, không `.value`, không
   `.fill()`. Khối comment id hợp đồng đầu `ledger_ui.js` cũng không liệt kê bốn id này (§1).
2. Vì vậy phương án "giữ id, đồng bộ qua select ẩn" không cần sửa một dòng test nào — rủi ro thấp
   nhất, và tự động tương thích ngược nếu sau này một test khác gọi `selectOption('#histFilterType',
   ...)`: `.value` vẫn đúng ngữ nghĩa cũ, `filterHistory()` đọc `$('histFilterType').value` không
   đổi.
3. Bấm nút `.histtype` set `$('histFilterType').value = ...` rồi gọi `render()` trực tiếp (không
   dựa vào sự kiện `change` — set `.value` bằng JS không tự bắn `change`), nên hành vi lọc không
   phụ thuộc việc listener `change` cũ có được kích hay không.

Xác nhận bằng manual verification (§5.4): bấm nút "Bán coin" → `#histFilterType` đọc được giá trị
`SELL` qua `p.locator('#histFilterType').inputValue()`, và nút đó có `aria-pressed="true"`.

---

## 4. Test cũ — không sửa một dòng nào, chạy PASS nguyên văn

    git diff --stat 4819a13..HEAD -- webapp/test_t12_browser.js webapp/test_stepb_ui.js webapp/test_t12_ledger.js webapp/test_l1_fixes.js webapp/test_t16_multiasset.js webapp/test_t12_mutations.js webapp/test_t12_fixtures.js webapp/test_t14_deploy_isolation.js
      (rỗng — không file test nào bị đổi)

Do đó KHÔNG có mục nào trong "Test bắt buộc" của chỉ thị đòi sửa test — cả 3 nhánh khả năng nêu
trong chỉ thị mục "Bộ lọc lịch sử ... PHẢI giữ cùng id" đều dẫn tới "không cần sửa test" theo lựa
chọn ở §3.

---

## 5. Bằng chứng chạy

### 5.1 Baseline TRƯỚC khi sửa (để so sánh)

Chạy trước khi đổi `ledger_ui.js`/`app_shell.html`: `test_t12_ledger.js`, `test_l1_fixes.js`,
`test_t16_multiasset.js`, `test_t12_mutations.js`, `test_t14_deploy_isolation.js`,
`test_t12_browser.js`, `test_stepb_ui.js` — toàn bộ PASS, exit 0 (baseline xác nhận môi trường
Firebase Emulator + Chromium **có tải được** trong phiên này, không phải giả định).

### 5.2 Sau khi sửa — từng suite không cần emulator

    node test_t12_ledger.js       -> 32/32 pass, exit 0
    node test_l1_fixes.js         -> 15/15 pass, exit 0
    node test_t16_multiasset.js   -> 14/14 pass, exit 0
    node test_t12_mutations.js    -> 7/7 mutant KILLED, exit 0
    node test_t14_deploy_isolation.js -> 18/18 assertion PASS, exit 0

### 5.3 Sau khi sửa — hai suite cần Firebase Emulator + Chromium thật

    node build_app.js
      BODY 136093 FULL 136248 -> app_final.html + public/index.html
    node test_t12_browser.js      -> toàn bộ PASS (P-1..P-6, migration M-1..M-4, T-16 v2->v3,
                                      Persistence offline/rejected/stale/corrupt/restart), exit 0
    node test_stepb_ui.js         -> toàn bộ PASS (AS-01..AS-12, PR-1..PR-6, T-16), exit 0

`test_t12_browser.js` là Completion Gate `CHECK-T13-12` gốc — chạy **nguyên văn, không sửa test**,
PASS toàn bộ. `test_stepb_ui.js` dùng `dashBottom()` helper đọc `#dashBottom .stat` — vẫn khớp vì
selector là descendant, không phụ thuộc độ lồng mới.

### 5.4 `npm test` đầy đủ (10 file, kể cả hai suite emulator ở trên)

    npm test  -> exit 0, toàn bộ PASS. Không suite nào bị bỏ qua vì emulator không tải được —
                 môi trường phiên này tải được Firebase Emulator (Auth :9099, Firestore :8080)
                 + Chromium (/opt/pw-browsers/chromium) đầy đủ.

### 5.5 Xác nhận trực tiếp 4 tiêu chí "Test mới" của chỉ thị (Playwright thủ công, KHÔNG commit vào repo)

Chạy một kịch bản Playwright bổ sung ngoài repo (dùng lại `test_firebase_harness.js` +
`test_t12_fixtures.js` thật, qua `app_final.html` + Firestore Emulator + Chromium thật — cùng
đường thi hành với `test_stepb_ui.js`, không gọi hàm module trực tiếp) để đo đúng 4 điều
"Test mới" mà chỉ thị liệt kê, với dữ liệu có đủ mọi loại (P2P, BUY nguồn PLAN + EXTRA, SELL,
CASH cả hai chiều, RESERVE cả hai chiều, PRICE):

1. **`#dashBottom` 3 khối đúng tiêu đề chữ:**
   `p.locator('#dashBottom .dashgroup-title').evaluateAll(...)` →
   `["Đang nắm giữ", "Tiền mặt & USDT", "Lãi/lỗ đã thực hiện"]` — khớp bit-với-bit chữ yêu cầu.

2. **Bộ đếm nút lọc khớp đúng số event thật từng loại**, đo trên một sổ có 9 event (1 mỗi loại,
   trừ `RESERVE_BUY` = 0):
   `{"TREASURY":"P2P VND/USDT (1)","PLAN":"Mua · Kế hoạch (1)","EXTRA":"Mua · Ngoài kế hoạch (1)",
   "RESERVE_BUY":"Mua · Dự phòng (0)","SELL":"Bán coin (1)","CASH":"Tiền mặt VND (2)",
   "RESERVE":"Dự phòng nạp/rút (2)","PRICE":"Giá tham chiếu (1)"}` — khớp đúng tay đếm.
   Bấm nút "Bán coin" → danh sách thẻ còn lại đúng 1 thẻ, `hc-main = "Bán ETH"`;
   `#histFilterType` đọc ra `SELL`; nút đó có `aria-pressed="true"`.

3. **Class icon đúng theo loại**, đọc trực tiếp `class` trên phần tử (không kiểm màu pixel):
   `Mua ETH/Mua BTC → hc-kind-buy`, `Bán ETH → hc-kind-sell`, `Nạp/Rút tiền mặt → hc-kind-cash`,
   `Đổi VND → USDT → hc-kind-treasury`, `Giá tham chiếu ETH → hc-kind-price`,
   `Nạp/Rút dự phòng → không có phần tử .hc-kind` (đúng yêu cầu "RESERVE giữ nguyên").

4. **Resize qua ngưỡng desktop/mobile, đọc `getComputedStyle` thật:**
   1200px → `getComputedStyle('#dashBottom').gridTemplateColumns` tách thành **2** cột;
   500px → tách thành **1** cột. (Đây là phép đo đã bắt được lỗi thứ tự CSS ở §2.1 mục 5 — chạy
   LẦN ĐẦU trước khi sửa thứ tự cho ra 2/2, tức bug thật; chạy LẠI sau khi sửa cho ra 2/1 như kỳ
   vọng.)

Ảnh chụp màn hình desktop (1280px) và mobile (390px) đã xem trực quan để đối chiếu bố cục — xác
nhận 2 cột/1 cột, tiêu đề nhóm, chip màu lãi (xanh), pill lọc, icon màu trên thẻ lịch sử đều hiện
đúng như thiết kế. Kịch bản và ảnh chụp **không commit vào repo** (đúng ngân sách artifact —
không phải file `.md`/task/report được liệt kê, và không phải evidence log `.txt/.json/.log` nhưng
vẫn là artifact ngoài ngân sách nếu giữ lại, nên bị loại bỏ sau khi xác nhận).

### 5.6 Vì sao báo cáo này thay cho một vòng E2 riêng

Task không chạm `webapp/ledger.js` (§2, diff rỗng) — không mang category `accounting_financial`
của `PROJECT_PROFILE.md`, nên không kích hoạt yêu cầu "tìm E2 qua phiên reviewer độc lập" (mục đó
áp cho check thuộc nhóm dữ liệu/tài chính). Rủi ro còn lại là rủi ro trình bày/regression UI,
được phủ bằng: (a) toàn bộ 10 suite test hiện có PASS nguyên văn không sửa; (b) 4 phép đo trực
tiếp trên trình duyệt thật + Firestore Emulator xác nhận đúng 4 tiêu chí "Test mới" chỉ thị nêu;
(c) đối chiếu trực quan qua ảnh chụp màn hình hai kích thước viewport. Mức bằng chứng E1 toàn bộ
là đủ cho gate `T-17`.

---

## 6. HARDENING — không phát sinh mục mới

Task không chạm lớp tính toán, không mở validation mới, không đổi hình dạng dữ liệu bền. Không có
finding `HARDENING` mới nào phát sinh từ phiên này.

---

## 7. Ngân sách artifact của chính phiên này

| Hạng mục | Cho phép | Thực tế |
|---|---|---|
| Task file | 1 | 1 — `docs/tasks/T-17-sap-xep-lai-giao-dien-coindca.md` |
| Báo cáo | 1 (gộp implementation + E2) | 1 — chính file này |
| DEC | 1 (closure) | 1 — `DEC-053` |
| Evidence log commit (`.txt`/`.json`/`.log`) | 0 | **0** |

Ngoài bốn mục trên, phiên chỉ cập nhật **state surface** đã tồn tại (`PROJECT_PROGRESS.md`,
`CAPABILITY_REGISTRY.md`, `REVIEW_BUDGET_LEDGER.md`) — bắt buộc theo `STATE_AUTHORITY.md`, không
phải artifact mới. Kịch bản Playwright xác minh thủ công và ảnh chụp màn hình ở §5.5 chạy ngoài
repo (thư mục scratch của phiên), không commit.
