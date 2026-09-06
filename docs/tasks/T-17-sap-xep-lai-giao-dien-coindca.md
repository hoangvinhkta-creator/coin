# T-17 — CoinDCA L-1: sắp xếp lại giao diện (Tổng quan theo nhóm, bộ lọc Lịch sử dạng nút, icon/màu theo loại giao dịch)

## Metadata

Status:
DONE

Lịch sử trạng thái: `NOT_PLANNED → READY → IN_PROGRESS → IMPLEMENTED → DONE` trong cùng một
phiên (2026-09-06, nhánh `claude/coincda-ui-reorganize-2ykjse`, nối tiếp `T-16`). Thẩm quyền:
chỉ thị phiên trực tiếp của Owner ("Sắp xếp lại giao diện CoinDCA L-1 cho gọn và dễ dùng hơn —
KHÔNG đổi bất kỳ logic kế toán/tính toán nào"), ghi lại thành `DEC-053`. Cùng khuôn
`STATE_AUTHORITY.md` đã dùng cho `T-12`…`T-16`.

Điều kiện tiên quyết đã kiểm:
`T-16 = DONE` (`docs/tasks/T-16-so-da-tai-san-sell-cash.md`, `DEC-052`), `CAP-WEBAPP` =
`ALLOWED 4 / USED 2 / REMAINING 2` tại `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.15 — khớp đúng
con số Owner nêu trong chỉ thị. Đủ điều kiện bắt đầu.

Phase:
CoinDCA L-1 — thuần trình bày (presentation only), không phải bước mới của chuỗi A → B → C → D.
Không mở rộng từ vựng sự kiện, không đổi hình dạng sổ, không đổi `derive()`.

Task Mode:
MAJOR — nhiều điểm chạm UI (dashboard, bộ lọc lịch sử, thẻ lịch sử, CSS responsive), có Ready
Gate/Completion Gate riêng và ràng buộc hợp đồng id với `test_t12_browser.js`/`test_stepb_ui.js`,
dù điểm routing D/R/B không tự nó đòi Tier cao (xem Routing Inputs bên dưới).

Capability:
`CAP-WEBAPP` (lineage root `WP-C1`). **KHÔNG** tạo capability mới.

Loại tiêu thụ budget:
**INITIAL IMPLEMENTATION — tiêu 0 repair cycle.** `T-17` là công việc MỚI (đổi cách trình bày),
không phải một lượt sửa sau một finding trên mã production đã `DONE` — khác nhóm với `T-15`
(repair cycle #2). `webapp/ledger.js` (lớp tính toán) hoàn toàn không bị chạm — xem
`docs/reviews/T17-IMPLEMENTATION-AND-E2-REPORT.md` §2. `USED` giữ nguyên **2**, `ALLOWED` giữ
nguyên **4** (đã đủ dư `REMAINING 2` từ `OWNER_EXTENSION` của `DEC-052`, không cần xin thêm).

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 2
R: 2
B: 2
A: 1
X: 1
U: 1
V: 3
H: 2
C: 2
F: 3

Routing Categories:
(none) — task này KHÔNG chạm lớp tính toán tài chính (`webapp/ledger.js`), nên KHÔNG mang
category `accounting_financial` của `PROJECT_PROFILE.md` § Hệ quả bắt buộc mục 2 (hard floor đó
áp dụng cho task "chạm lớp tính toán tài chính" — task này bị cấm chạm lớp đó theo đúng yêu cầu
Owner ở Ràng buộc bắt buộc mục 1 của chỉ thị). Đây là điểm khác `T-12`/`T-13`/`T-16` (đều mang
category này vì đụng `derive()`/schema) — ghi rõ để phiên sau không tự động gán lại.

Primary Agent Tier:
B

Primary Effort:
high

Model Routing Score:
1.7

Effort Score:
2.25

Routing Floors:
model: none; effort: none (không hard floor nào áp dụng — xem Routing Categories ở trên).
Lệnh tái lập:
`python3 governance/scripts/governance/routing_engine.py --d 2 --r 2 --b 2 --a 1 --x 1 --u 1
--v 3 --h 2 --c 2 --f 3`

## Objective

Sắp xếp lại giao diện CoinDCA L-1 cho gọn và dễ dùng hơn sau khi Owner tự nhập kế hoạch + lịch sử
thật (102 sự kiện) vào production và phát hiện hai vấn đề usability: (1) khối "Tổng quan" phần
dưới render mọi con số thành một lưới `.stat` phẳng, không phân nhóm theo ý nghĩa; (2) Lịch sử chỉ
có một bộ lọc dropdown, danh sách thẻ không phân biệt trực quan theo loại giao dịch.

## Product consequence

Không sửa thì Owner phải tự đọc/đếm nhãn `<small>` trong một lưới phẳng để tách "đang giữ" khỏi
"tiền mặt" khỏi "lãi/lỗ", và phải mở dropdown + đọc từng thẻ lịch sử để tìm đúng loại giao dịch
giữa 102 sự kiện thật — chậm và dễ đọc nhầm khi kiểm tra sổ hằng ngày.

## Scope IN

- `webapp/ledger_ui.js` — `renderDashBottom`/`holdingRows` tách 3 khối có tiêu đề; `filterHistory`
  refactor dùng chung `matchesHistType` với bộ đếm nút lọc mới (`renderHistFilterButtons`); nhãn
  `#histFilterType` (select ẩn) giữ nguyên id/hợp đồng giá trị; `renderHistoryCards` thêm
  `KIND_BADGE` (icon/màu theo loại) cạnh `hc-date`; markup tĩnh trong `mount()` thêm tiêu đề nhóm
  "Kế hoạch tháng này" phía trên `dashMain`.
- `webapp/app_shell.html` — CSS thuần: `.dashgroup`/`.dashgroup-title`/`.dashbottom-groups` (lưới
  2 cột desktop / 1 cột mobile ở breakpoint 860px sẵn có), `.histtypes`/`.histtype` (tái dùng style
  `.txtype`), `.histfilter-row`, `.hc-kind` + 5 biến thể màu, biến CSS mới `--cash`/`--cash-bg`
  (light + cả hai khối dark).

## Scope OUT (Non-goals tường minh, theo đúng Ràng buộc bắt buộc của chỉ thị)

- **KHÔNG** đổi `webapp/ledger.js` — không đổi bất kỳ phép tính, field nào của `derive()`.
- **KHÔNG** đổi/xoá bất kỳ id nào trong danh sách hợp đồng ở đầu `webapp/ledger_ui.js`.
- **KHÔNG** thêm thư viện/CDN ngoài.
- **KHÔNG** đổi cấu trúc Kế hoạch/Số dư đầu kỳ/Cài đặt.
- **KHÔNG** đổi hành vi lọc theo ngày/tìm-kiếm ghi chú — chỉ đổi phần lọc-theo-loại.
- **KHÔNG** đổi bảng màu/theme tổng thể ngoài phần icon/màu giao dịch (mục 4 của chỉ thị).
- **KHÔNG** đổi badge/chip nguồn (EXTRA/RESERVE), TƯƠNG LAI, UNKNOWN đã có — chỉ THÊM icon loại.
- **KHÔNG** thêm icon/màu riêng cho `RESERVE` — giữ nguyên như trước task này (chỉ thị mục 4).

## Ràng buộc kiến trúc đã khoá (implementer KHÔNG được quyết lại)

1. `#histFilterType` (select) tiếp tục là nguồn sự thật cho GIÁ TRỊ loại đang lọc — chọn phương án
   "select ẩn + bộ nút `.histtype` đồng bộ giá trị" (ràng buộc #3 của chỉ thị, lựa chọn A). Lý do
   chọn A thay vì B (đổi hẳn sang nút + sửa test): không test nào trong
   `test_t12_browser.js`/`test_stepb_ui.js` đang thao tác `#histFilterType` (đã grep xác nhận —
   xem báo cáo §1), nên A là lựa chọn không rủi ro và không cần sửa test nào, còn B sẽ đổi hợp
   đồng mà không có lợi ích tương ứng.
2. Đếm số lượng mỗi loại trong nút lọc tính trên TOÀN BỘ `s.events` (không phụ thuộc bộ lọc ngày/
   tìm-kiếm đang áp), đúng logic type-matching đã có trong `filterHistory` — refactor thành một
   hàm `matchesHistType` dùng chung, không viết lại logic hai lần.
3. `renderDashMain()` KHÔNG bị sửa nội dung/logic — tiêu đề nhóm "Kế hoạch tháng này" chỉ là
   markup tĩnh thêm vào `mount()`, đặt phía trên `#dashMain`.
4. `#dashBottom` giữ nguyên là id container ngoài duy nhất; 3 khối con là div lồng bên trong,
   không đổi cấu trúc mà `test_stepb_ui.js` phụ thuộc (`#dashBottom .stat` — descendant selector,
   không phụ thuộc độ sâu lồng).

## Change budget (ước lượng có ràng buộc)

Ước lượng: ≤ 2 file, ≤ 200 dòng. Thực tế đo được: 2 file, +104/−25 (`git diff --shortstat`) — xem
báo cáo §2.

## Ready Gate

| # | Điều kiện | Trạng thái |
|---|---|---|
| RG-1 | Điều kiện tiên quyết `T-16 DONE` + budget `CAP-WEBAPP` đã kiểm bằng file thật | PASS |
| RG-2 | Phân loại budget (INITIAL IMPLEMENTATION, 0 repair cycle) xử lý xong TRƯỚC dòng mã đầu tiên | PASS |
| RG-3 | Đọc toàn bộ khối comment id hợp đồng đầu `ledger_ui.js` + `test_t12_browser.js`/`test_stepb_ui.js` trước khi sửa | PASS — báo cáo §1 |
| RG-4 | Lựa chọn cho `#histFilterType` (ràng buộc #3) đã quyết TRƯỚC khi viết markup | PASS — mục "Ràng buộc kiến trúc" #1 |
| RG-5 | Baseline test (không emulator + có emulator) chạy PASS TRƯỚC khi sửa, để so sánh | PASS — báo cáo §2 |
| RG-6 | Ngân sách artifact được khai và kiểm được | PASS |

## Completion Gate

FROZEN 2026-09-06. Tất cả REQUIRED.

| # | Check | Evidence | Kết quả |
|---|---|---|---|
| CHECK-T17-01 | `webapp/ledger.js` không đổi một dòng nào (`git diff --stat`) | E1 — `T17-1` | PASS |
| CHECK-T17-02 | Không id nào trong danh sách hợp đồng đầu `ledger_ui.js` bị đổi tên/gỡ | E1 — `T17-2` | PASS |
| CHECK-T17-03 | `#dashBottom` render đúng 3 khối con, đúng tiêu đề chữ ("Đang nắm giữ"/"Tiền mặt & USDT"/"Lãi/lỗ đã thực hiện") | E1 — `T17-3` | PASS |
| CHECK-T17-04 | Holdings rỗng hiện thông báo "Chưa có coin nào" thay vì trống im lặng | E1 — `T17-4` | PASS |
| CHECK-T17-05 | Nút lọc lịch sử đếm đúng số lượng mỗi loại trên toàn bộ `s.events`, không phụ thuộc lọc ngày/tìm-kiếm | E1 — `T17-5` | PASS |
| CHECK-T17-06 | Bấm "Bán coin" chỉ hiện đúng giao dịch SELL; `#histFilterType` đồng bộ giá trị; `aria-pressed` đúng nút đang chọn | E1 — `T17-6` | PASS |
| CHECK-T17-07 | Mỗi loại giao dịch (BUY/SELL/CASH/TREASURY/RESERVE/PRICE) có đúng class icon theo quy tắc mục 4 của chỉ thị; RESERVE không có icon mới | E1 — `T17-7` | PASS |
| CHECK-T17-08 | Badge/chip cũ (nguồn EXTRA/RESERVE, TƯƠNG LAI, UNKNOWN) vẫn còn nguyên, không bị xoá | E1 — `test_stepb_ui.js` AS-03 (badge EXTRA) | PASS |
| CHECK-T17-09 | Responsive: `#dashBottom` 2 cột ở >860px, 1 cột ở ≤860px, đo bằng `getComputedStyle` thật (không chỉ đọc CSS nguồn) | E1 — `T17-8` | PASS |
| CHECK-T17-10 | Không thư viện/CDN ngoài mới; build 1 file HTML duy nhất qua `build_app.js` vẫn chạy | E1 — `node build_app.js` | PASS |
| CHECK-T17-11 | `test_t12_browser.js` (CHECK-T13-12) PASS nguyên văn, không sửa test | E1 — `npm run test:t12` | PASS |
| CHECK-T17-12 | `test_stepb_ui.js` PASS nguyên văn, không sửa test | E1 — `npm run test:stepb` | PASS |
| CHECK-T17-13 | Toàn bộ `npm test` (10 file, gồm emulator + browser) PASS, exit 0 | E1 — `npm test` | PASS |
| CHECK-T17-14 | Đúng ngân sách artifact: 1 task file, 1 báo cáo gộp, 1 DEC, 0 evidence log | E1 — `git show --stat` | PASS |

Mức bằng chứng: E1 toàn bộ. Task thuần trình bày, tiêu thụ 0 dòng thay đổi ở lớp tính toán
(`webapp/ledger.js` diff rỗng) — không mở vòng E2 độc lập vì không chạm `accounting_financial`
category (xem Routing Categories ở trên); rủi ro còn lại là rủi ro UI/regression, đã phủ bằng
toàn bộ 10 file test hiện có (không suite nào bị bỏ qua, kể cả hai suite cần Firebase Emulator +
Chromium thật) cộng một kịch bản Playwright xác nhận bổ sung chạy thủ công (báo cáo §4) — không
commit vào repo theo đúng ngân sách artifact.

## Exit Criteria

- 14/14 REQUIRED PASS. `npm test` exit 0, không suite nào bị bỏ qua.
- Báo cáo nêu rõ: lựa chọn cho `#histFilterType` (ràng buộc #3) và lý do, mọi chỗ mô tả lệch với
  code thật (nếu có), xác nhận điều kiện tiên quyết + phân loại ngân sách.
- `branch_authority_check.sh` chạy trước khi kết thúc.

## Stop conditions

- Mô tả trong chỉ thị lệch với code thật → DỪNG, báo (KHÔNG đoán). (Không xảy ra — xem báo cáo §1.)
- Một id trong danh sách hợp đồng cần đổi mà không có đường nào giữ được → DỪNG, hỏi Owner.
- `webapp/ledger.js` cần sửa để đạt mục tiêu trình bày → DỪNG — ngoài phạm vi được phép của task này.

## Implementation authority

`DEC-053` (Owner Direction + Lifecycle Closure). Không quyết định kiến trúc mới nào ngoài lựa
chọn đã ghi ở mục "Ràng buộc kiến trúc đã khoá" #1.
