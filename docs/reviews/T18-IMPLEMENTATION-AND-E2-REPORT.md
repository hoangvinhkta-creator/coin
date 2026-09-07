# T-18 — Báo cáo gộp (implementation + bằng chứng E2) — 4 tab thật, điều hướng lên header

**Phiên:** 2026-09-07 · **Nhánh:** `claude/coincda-ui-reorganize-2ykjse`
**Nguồn yêu cầu:** chỉ thị phiên trực tiếp của Owner ("hãy cho 4 mục hiện tại là tổng quan - lịch
sử - kế hoạch - cài đặt thành 4 tab riêng biệt thay vì nằm trên 1 trang tĩnh như hiện tại... cho
4 card chọn của 4 tab này lên header thay vì footer").
**Task:** `docs/tasks/T-18-tab-that-va-dieu-huong-header.md` · **Quyết định:** `DEC-054`

Báo cáo này GỘP implementation report + bằng chứng E2 vào một file theo đúng ngân sách artifact
cứng đã dùng cho `T-15`…`T-17`. Không có evidence log (`.txt`/`.json`/`.log`) nào được commit.

---

## 1. Xác nhận trước khi sửa: rủi ro thật của yêu cầu này

Khối comment ngay tại `routeTo()` cũ trong `ledger_ui.js` viết thẳng lý do KHÔNG dùng
`display:none`/tab thật trước đây: *"history/plan/settings phải luôn tương tác được cho
test_t12_browser.js vốn không bao giờ bấm điều hướng trước khi thao tác trên form"*. Đây là một
ràng buộc kiến trúc đã ghi lại từ `T-13`, và yêu cầu của Owner lần này **đảo ngược đúng ràng buộc
đó** — chuyển 4 mục thành tab THẬT nghĩa là 3 mục không active sẽ bị ẩn thật (`hidden`), nên mọi
hành động Playwright chạm một phần tử NẰM TRONG mục không active sẽ hết tương tác được trừ khi
test tự chuyển tab trước.

Grep xác nhận `#bottomNav` (id thanh điều hướng cũ) không được bất kỳ test nào tham chiếu trực
tiếp — an toàn để đổi vị trí/tên. Việc còn lại là xác định CHÍNH XÁC những dòng test nào cần một
lệnh chuyển tab mới, không đoán, không sửa quá tay.

**Phát hiện quan trọng qua thực nghiệm (không đoán từ tài liệu API):** Playwright phân biệt rõ hai
nhóm phương thức trên `.view-sec` bị ẩn:
- **Hành động** (`click`, `fill`, `selectOption`, `isHidden`/`isVisible`) — CHỜ actionability, bắt
  buộc phần tử (và mọi tổ tiên) đang hiển thị. Bị ẩn → timeout hoặc sai kết quả.
- **Đọc thuần** (`evaluateAll`, `textContent`, `count`, `inputValue`) — KHÔNG chờ actionability,
  hoạt động đúng bất kể phần tử đang bị `hidden` hay không (đã tự kiểm bằng cách chạy test thật và
  quan sát PASS/FAIL, không suy diễn suông — xem §3).

Hệ quả: các hàm tổng hợp số liệu dùng để so sánh trước/sau (`dash()`, `ui()`, `summary()`,
`dashCards()`, `dashBottom()`, `histCount()`) trong cả 4 file test **không cần sửa** — chúng vẫn
đọc đúng số liệu dù tab tương ứng không active. Chỉ các HÀNH ĐỘNG thật mới cần đúng tab.

---

## 2. Thay đổi thực tế (đo trực tiếp, không cộng tay)

    git diff --stat 563fda3..HEAD -- webapp/ledger_ui.js webapp/app_shell.html webapp/test_firebase_harness.js webapp/test_t12_browser.js webapp/test_stepb_ui.js webapp/test_t14_backup_restore.js webapp/test_t14_persistence.js
      webapp/app_shell.html             | 64 ++++++++++++++++++++++-----------
      webapp/ledger_ui.js               | 16 ++++++----
      webapp/test_firebase_harness.js   | 13 ++++++--
      webapp/test_stepb_ui.js           |  3 ++
      webapp/test_t12_browser.js        |  7 +++++
      webapp/test_t14_backup_restore.js |  5 +++
      webapp/test_t14_persistence.js    |  2 ++
      7 files changed, 74 insertions(+), 36 deletions(-)

    # lớp tính toán — PHẢI RỖNG
    git diff --stat 563fda3..HEAD -- webapp/ledger.js src/eth_dca_os docs/spec firestore.rules
      (rỗng)

Trong ước lượng change budget (≤ 8 file, ≤ 150 dòng).

### 2.1 Production: `webapp/ledger_ui.js`

`routeTo(view, behavior)` viết lại: thay vì chỉ `el.scrollIntoView(...)`, nay
`document.querySelectorAll('.view-sec').forEach(sec => { sec.hidden = sec !== el; })` — ẩn thật 3
mục không active qua thuộc tính `hidden` (không CSS tuỳ biến nào đè `display` của `.view-sec`, nên
UA stylesheet mặc định `[hidden]{display:none}` áp dụng đúng). Cuộn về đầu trang
(`window.scrollTo`) thay vì cuộn tới phần tử (không còn cần thiết vì tab là toàn bộ nội dung nhìn
thấy). Tham chiếu `#bottomNav` đổi thành `#tabNav` (2 chỗ: gắn `onclick` và cập nhật
`aria-current`) — cùng `data-view`/hành vi, chỉ đổi id cho đúng vai trò mới. `#l1Entry` ("+ Ghi
giao dịch") **không đụng tới** — vẫn là sibling của 4 `.view-sec`, không nằm trong danh sách bị
ẩn/hiện, giữ nguyên mở sẵn theo mặc định.

### 2.2 Production: `webapp/app_shell.html`

Header tách 2 hàng: `.hdr-top` (tiêu đề + trạng thái lưu, y hệt bố cục cũ) + `<nav class="tabnav"
id="tabNav">` ngay dưới, trong cùng `<header class="top">`. Markup `<nav>` này CHÍNH LÀ
`#bottomNav` cũ dời vào header (đổi id, xoá khỏi vị trí cũ sau `.wrap`) — cùng 4 `<button
data-view="...">`. CSS: `.tabnav` = hàng flex 4 nút "card" viền/bo góc (`aria-current="true"` tô
nền `--accent-soft`), thay cho `.bottomnav` cố định ở đáy màn hình. `.fab` dời từ `bottom:74px`
(từng chừa chỗ cho thanh điều hướng cũ) xuống `bottom:16px` (mobile `12px`) vì đáy màn hình không
còn thanh cố định nào khác. `.wrap{padding-bottom}` giảm từ `96px` xuống `32px` cùng lý do.

### 2.3 Test: `webapp/test_firebase_harness.js`

Thêm `async function goTab(p, view) { await p.click('#tabNav button[data-view="' + view +
'"]'); }`, export qua `module.exports`. `googleSignOut()` gọi `goTab(p, 'settings')` trước khi bấm
nút "Đăng xuất" — phát hiện qua chạy thật (không đoán): lúc `ONLINE`, nút đăng xuất CHỈ chắc chắn
tồn tại trong mục Cài đặt (`#fbBox`); banner đăng nhập/đăng xuất ở `#banners` chỉ hiện lúc
`SIGNED_OUT`/`UNRECOGNIZED`, không phải lúc `ONLINE`.

### 2.4 Test: 4 file gọi `H.goTab()` đúng điểm cần

Danh sách đầy đủ các điểm được CHÈN THÊM (không có điểm nào bị xoá/sửa nội dung assertion):

| File | Điểm chèn | Tab cần | Vì sao |
|---|---|---|---|
| `test_t12_browser.js` | đầu `setPlan()`, `setOpening()` | `plan` | field Kế hoạch/Số dư đầu kỳ nằm trong `view-plan` |
| `test_t12_browser.js` | trước 2 nút Sửa/Xoá trong Lịch sử | `history` | nút nằm trong `view-history` |
| `test_t12_browser.js` | trước `#l1Export`/`#l1Import` (2 chỗ) | `settings` | 2 nút/`input[type=file]` nằm trong `view-settings` |
| `test_t12_browser.js` | trước kiểm `#l1MigrationV3`/`#l1Migration`.`isHidden()` | `plan` | migration block nằm trong `view-plan`; `isHidden()` là HÀNH ĐỘNG, cần tổ tiên hiển thị |
| `test_t12_browser.js` | trước `#l1Wipe` | `settings` | nút nằm trong `view-settings` |
| `test_stepb_ui.js` | đầu `setOpening()`, `setPlan()` | `plan` | như trên |
| `test_stepb_ui.js` | trước nút Sửa (AS-05)/Xoá (AS-06) | `history` | như trên |
| `test_t14_backup_restore.js` | đầu `uiSetPlan()`, `uiSetOpening()` | `plan` | như trên |
| `test_t14_backup_restore.js` | đầu `importFile()` (`#l1Import`) | `settings` | như trên |
| `test_t14_backup_restore.js` | trước `#l1Export` (CHECK-T14-06) | `settings` | như trên |
| `test_t14_backup_restore.js` | trước `#l1Wipe` (CHECK-T14-10) | `settings` | như trên |
| `test_t14_persistence.js` | đầu `uiSetPlan()`, `uiSetOpening()` | `plan` | như trên |

`uiEvent()`/`enter()` (điền form trong `#l1Entry`) và mọi hàm đọc tổng hợp (`dash`/`ui`/`summary`/
`dashCards`) **không đổi** — không cần tab, theo phát hiện ở §1.

---

## 3. Bằng chứng: từng file chạy độc lập rồi chạy cả chuỗi

Chạy TRƯỚC khi sửa test (chỉ sửa production) để xác nhận đúng giả thuyết ở §1 bằng lỗi thật, không
đoán: `googleSignOut` timeout đúng vì `#fbSignOut` "element is not visible" (Settings tab không
active) — xác nhận hành động cần tab, đọc thuần thì không (nhiều `dash()`/`ui()` gọi ngay TRƯỚC/
SAU đó vẫn PASS trong khi tab không phải Dashboard).

Sau khi sửa đủ, từng file PASS 100% KHÔNG sửa/xoá assertion nào:

    node test_t12_browser.js        -> toàn bộ PASS (P-1..P-6, Migration M-1..M-4, T-16 v2->v3,
                                        Persistence offline/rejected/stale/corrupt/restart), exit 0
    node test_stepb_ui.js           -> toàn bộ PASS (AS-01..AS-12, PR-1..PR-6, T-16), exit 0
    node test_t14_backup_restore.js -> 47/47 assertion PASS (CHECK-T14-06..10, C-AS-09b), exit 0
    node test_t14_persistence.js    -> 60/60 assertion PASS (PR-AUTH-0/1, C-AS-01..07, CHECK-T14-01,
                                        T14-CONFLICT/CORRUPT/WRITE-DENIED/RESTART/CLEAR-STORAGE), exit 0

Số lượng assertion mỗi file **khớp đúng số trước khi sửa** (không có case nào biến mất) — xác nhận
bằng cách so file trước/sau chỉ thêm dòng `H.goTab(...)`, không đổi dòng `assert`/`A.*` nào
(`git diff` mỗi file ở §2.4, mỗi file chỉ +2..+7 dòng chèn thêm).

### `npm test` đầy đủ (10 file, kể cả 6 suite không cần emulator)

    npm test  -> exit 0. test_t12_ledger (32/32), test_l1_fixes (15/15), test_t16_multiasset
                 (14/14, mutation survivors=0), test_t12_mutations (7/7 KILLED),
                 test_t14_deploy_isolation (18/18), test_t14_rules (31/31),
                 test_t14_persistence (60/60), test_t14_backup_restore (47/47),
                 test_t12_browser (toàn bộ PASS), test_stepb_ui (toàn bộ PASS). Không suite nào
                 bị bỏ qua vì thiếu emulator/Chromium — môi trường phiên này có đủ cả hai.

---

## 4. Xác nhận trực tiếp bằng Playwright thủ công (KHÔNG commit vào repo)

Ngoài `npm test`, chạy thêm một kịch bản xác nhận đúng hành vi TAB (không phải chỉ "test cũ không
vỡ") — dùng `test_firebase_harness.js` thật, qua `app_final.html` + Firestore Emulator +
Chromium thật:

1. `#tabNav` nằm trong `<header class="top">`; `#bottomNav` không còn tồn tại trong DOM.
2. Mặc định chỉ `#view-dashboard` không có thuộc tính `hidden` — 3 mục còn lại đều `hidden`.
3. Bấm lần lượt 4 nút: mỗi lần, **đúng một** `.view-sec` không `hidden` (đúng mục vừa bấm), URL
   hash cập nhật `#/<view>`, nút vừa bấm có `aria-current="true"`, `#l1Entry` vẫn luôn có mặt
   trong DOM bất kể tab nào đang active.
4. Chuyển tới Lịch sử rồi `page.reload()` — sau reload, `#view-history` vẫn là mục duy nhất hiện
   (refresh-safe qua hash, không đổi so với hành vi cũ).
5. Chuyển tới Cài đặt — nút FAB "+ Ghi giao dịch" vẫn hiển thị/bấm được (không bị gate theo tab).
6. Đo layout thật ở viewport 390px: `getComputedStyle('#tabNav').flexWrap === 'nowrap'`,
   `overflowX === 'auto'`, nhưng cả 4 nút vẫn nằm trên **cùng một hàng** (`boundingClientRect.top`
   giống nhau cho cả 4) và `tabNav.scrollWidth === tabNav.getBoundingClientRect().width` (không
   tràn) — xác nhận layout đúng như thiết kế dù ảnh chụp màn hình đã nén/co lại gây cảm giác sai
   là "2 hàng" khi nhìn bằng mắt; số đo `getComputedStyle`/`getBoundingClientRect` mới là bằng
   chứng, không phải ảnh chụp co giãn.

Ảnh chụp desktop (1280px, tab Tổng quan + Lịch sử) và mobile (390px) đã xem trực quan để đối chiếu
bố cục cuối cùng — xác nhận đúng thiết kế: 4 card trong header, chỉ nội dung tab đang chọn hiện
bên dưới, "+ Ghi giao dịch" luôn có mặt. Kịch bản và ảnh chụp không commit vào repo.

---

## 5. HARDENING — không phát sinh mục mới

Task không chạm lớp tính toán, không mở validation mới, không đổi hình dạng dữ liệu bền. Không có
finding `HARDENING` mới nào phát sinh từ phiên này.

---

## 6. Ngân sách artifact của chính phiên này

| Hạng mục | Cho phép | Thực tế |
|---|---|---|
| Task file | 1 | 1 — `docs/tasks/T-18-tab-that-va-dieu-huong-header.md` |
| Báo cáo | 1 (gộp implementation + E2) | 1 — chính file này |
| DEC | 1 (closure) | 1 — `DEC-054` |
| Evidence log commit (`.txt`/`.json`/`.log`) | 0 | **0** |

Ngoài bốn mục trên, phiên chỉ cập nhật **state surface** đã tồn tại (`PROJECT_PROGRESS.md`,
`REVIEW_BUDGET_LEDGER.md`) — bắt buộc theo `STATE_AUTHORITY.md`, không phải artifact mới. Kịch
bản Playwright xác minh thủ công và ảnh chụp màn hình ở §4 chạy ngoài repo, không commit.
