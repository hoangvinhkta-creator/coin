# T-18 — CoinDCA L-1: 4 mục thành tab thật, chuyển bộ chọn tab lên header

## Metadata

Status:
DONE

Lịch sử trạng thái: `NOT_PLANNED → READY → IN_PROGRESS → IMPLEMENTED → DONE` trong cùng một
phiên (2026-09-07, nhánh `claude/coincda-ui-reorganize-2ykjse`, nối tiếp `T-17`). Thẩm quyền: chỉ
thị phiên trực tiếp của Owner ("hãy cho 4 mục hiện tại là tổng quan - lịch sử - kế hoạch - cài đặt
thành 4 tab riêng biệt thay vì nằm trên 1 trang tĩnh như hiện tại... cho 4 card chọn của 4 tab này
lên header thay vì footer"), ghi lại thành `DEC-054`.

Điều kiện tiên quyết đã kiểm:
`T-17 = DONE` (`DEC-053`), `CAP-WEBAPP` = `ALLOWED 4 / USED 2 / REMAINING 2` (không đổi bởi
`T-17`, xem `REVIEW_BUDGET_LEDGER.md` §2.2.16).

Phase:
CoinDCA L-1 — thuần điều hướng/trình bày. Không mở rộng từ vựng sự kiện, không đổi hình dạng sổ,
không đổi `derive()`.

Task Mode:
MAJOR — đổi mô hình điều hướng lõi (4 section cuộn chung một trang → 4 tab ẩn/hiện thật) và bắt
buộc sửa 4 file test đang phụ thuộc một giả định kiến trúc đã ghi rõ trong code
(`ledger_ui.js` cũ: "không display:none các section... test_t12_browser.js vốn không bao giờ bấm
điều hướng trước khi thao tác trên form").

Capability:
`CAP-WEBAPP` (lineage root `WP-C1`). **KHÔNG** tạo capability mới.

Loại tiêu thụ budget:
**INITIAL IMPLEMENTATION — tiêu 0 repair cycle.** Đây là công việc MỚI theo yêu cầu Owner (đổi mô
hình điều hướng), không phải sửa một finding trên mã production đã `DONE`. `webapp/ledger.js`
diff **RỖNG** — không chạm lớp tính toán. `USED` giữ nguyên **2**, `ALLOWED` giữ nguyên **4**.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 3
A: 2
X: 2
U: 2
V: 3
H: 3
C: 3
F: 3

Routing Categories:
(none) — không chạm lớp tính toán tài chính (`webapp/ledger.js` diff rỗng), giống `T-17`.

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.7

Effort Score:
2.8

Routing Floors:
model: none; effort: none. Lệnh tái lập:
`python3 governance/scripts/governance/routing_engine.py --d 3 --r 3 --b 3 --a 2 --x 2 --u 2
--v 3 --h 3 --c 3 --f 3`

Điểm cao hơn `T-17` (Tier B) dù cùng không chạm lớp tính toán: **Blast Radius** (đổi mô hình điều
hướng lõi, ảnh hưởng toàn bộ 4 khu vực UI, không chỉ trình bày một khối) và **Failure cost** (rủi
ro làm hỏng `test_t12_browser.js` — hợp đồng Completion Gate `CHECK-T13-12` đã FROZEN từ `T-13`)
cao hơn hẳn một thay đổi CSS/nhóm hiển thị thuần tuý.

## Objective

Chuyển 4 mục Tổng quan/Lịch sử/Kế hoạch/Cài đặt từ 4 khối cuộn chung một trang (điều hướng chỉ là
cuộn tới + đổi `aria-current`) thành 4 tab THẬT (chỉ một khối hiện tại một thời điểm, dùng thuộc
tính `hidden`), và chuyển bộ 4 nút chọn tab từ thanh cố định ở đáy màn hình lên header.

## Product consequence

Với sổ đã có nhiều tháng dữ liệu thật, trang cuộn dài khiến người dùng phải kéo qua toàn bộ Lịch
sử để tới Kế hoạch/Cài đặt (hoặc ngược lại) dù chỉ cần xem một mục. 4 tab thật giải quyết đúng
việc đó; đưa bộ chọn lên header giữ nó luôn thấy được không cần cuộn xuống đáy, và giải phóng
thanh cố định ở đáy màn hình cho riêng nút "+ Ghi giao dịch" (FAB).

## Scope IN

- `webapp/ledger_ui.js` — `routeTo()` viết lại: ẩn/hiện thật các `.view-sec` qua thuộc tính
  `hidden` thay vì chỉ `scrollIntoView`; đổi tham chiếu `#bottomNav` → `#tabNav` (cùng
  `data-view`/`aria-current`, chỉ đổi id cho đúng vai trò mới — không test nào phụ thuộc id cũ,
  đã grep xác nhận). `#l1Entry` ("+ Ghi giao dịch") **KHÔNG** bị gate theo tab — giữ nguyên là
  sibling luôn hiện, mở sẵn theo mặc định (quyết định gốc T-13, không đổi).
- `webapp/app_shell.html` — CSS/markup thuần: gộp header thành `.hdr-top` (tiêu đề + trạng thái
  lưu) + `.tabnav` (4 nút dạng "card") ngay dưới; gỡ `.bottomnav` cố định ở đáy; `.fab` dời về sát
  đáy (không còn phải chừa chỗ cho thanh điều hướng cũ); `.wrap` giảm `padding-bottom`.
- `webapp/test_firebase_harness.js` — thêm helper dùng chung `goTab(p, view)`; `googleSignOut`
  gọi `goTab(p, 'settings')` trước khi bấm nút Đăng xuất (nút đó, lúc ONLINE, chỉ chắc chắn có
  trong mục Cài đặt — banner auth chỉ hiện lúc SIGNED_OUT/UNRECOGNIZED).
- `webapp/test_t12_browser.js`, `webapp/test_stepb_ui.js`, `webapp/test_t14_backup_restore.js`,
  `webapp/test_t14_persistence.js` — thêm đúng các lệnh `H.goTab(p, ...)` TRƯỚC mỗi tương tác
  (`click`/`fill`/`selectOption`/`isHidden`) chạm một phần tử nằm trong `.view-sec` không phải
  tab đang active. KHÔNG xoá/nới lỏng một assertion nào; KHÔNG đổi oracle/fixture nào.

## Scope OUT (Non-goals tường minh)

- **KHÔNG** đổi `webapp/ledger.js` — diff rỗng, xác nhận bằng `git diff --stat`.
- **KHÔNG** gate `#l1Entry` theo tab — nó vẫn luôn hiện/mở sẵn bất kể tab nào đang active (quyết
  định T-13 giữ nguyên; đổi nó sẽ phá `enter()`/`saveEvent()` của cả 2 file test cũ).
- **KHÔNG** đổi nội dung/nhãn/số liệu hiển thị bên trong bất kỳ tab nào (thừa kế nguyên trạng từ
  `T-17`).
- **KHÔNG** thêm thư viện/CDN ngoài; vẫn build 1 file HTML qua `build_app.js`.
- **KHÔNG** nới lỏng, xoá, hay comment-out một assertion nào trong 4 file test bị sửa — chỉ CHÈN
  THÊM bước chuyển tab trước tương tác vốn đã cần nó.

## Ràng buộc kiến trúc đã khoá (implementer KHÔNG được quyết lại)

1. Điều hướng vẫn refresh-safe qua URL hash (`#/dashboard`, `#/history`, `#/plan`, `#/settings`)
   — `viewFromHash()` giữ nguyên logic, chỉ `routeTo()` đổi CÁCH thể hiện view đang chọn (ẩn/hiện
   thật thay vì chỉ cuộn).
2. Chỉ CHÈN THÊM lệnh chuyển tab vào test hiện có tại đúng điểm cần nó — không viết lại luồng test,
   không đổi oracle, không đổi assertion. Xác nhận bằng cách mỗi test PASS nguyên số lượng
   assertion cũ (xem báo cáo §4).
3. Phương thức Playwright chỉ ĐỌC (không phải hành động — `evaluateAll`, `textContent`, `count`,
   `inputValue`) không yêu cầu phần tử đang hiển thị, nên các hàm tổng hợp số liệu (`dash()`,
   `ui()`, `summary()`) không cần sửa. Chỉ các hành động thật (`click`, `fill`, `selectOption`,
   `setInputFiles`, `isHidden`/`isVisible`) mới cần đúng tab đang active — kiểm chứng bằng chính
   việc chạy test và quan sát lỗi thật (không đoán suông), ghi ở báo cáo §3.

## Change budget (ước lượng có ràng buộc)

Ước lượng: ≤ 8 file, ≤ 150 dòng. Thực tế đo được: 7 file, +74/−36 (`git diff --shortstat`) — xem
báo cáo §2.

## Ready Gate

| # | Điều kiện | Trạng thái |
|---|---|---|
| RG-1 | Điều kiện tiên quyết `T-17 DONE` + budget `CAP-WEBAPP` đã kiểm | PASS |
| RG-2 | Phân loại budget (INITIAL IMPLEMENTATION, 0 repair cycle) xử lý xong TRƯỚC dòng mã đầu tiên | PASS |
| RG-3 | Xác định trước: `#l1Entry` không bị gate theo tab (giữ nguyên hợp đồng `enter()`) | PASS |
| RG-4 | Baseline test (4 suite cần emulator + 6 suite không cần) PASS TRƯỚC khi sửa | PASS — kế thừa baseline `T-17` |
| RG-5 | Xác định trước bằng grep: không test nào phụ thuộc id `#bottomNav` cũ | PASS — báo cáo §1 |
| RG-6 | Ngân sách artifact được khai và kiểm được | PASS |

## Completion Gate

FROZEN 2026-09-07. Tất cả REQUIRED.

| # | Check | Evidence | Kết quả |
|---|---|---|---|
| CHECK-T18-01 | `webapp/ledger.js` không đổi một dòng nào | E1 — `git diff --stat` | PASS |
| CHECK-T18-02 | 4 `.view-sec` — đúng MỘT hiện tại một thời điểm (`hidden` trên 3 mục còn lại), đo bằng Playwright thật | E1 — `T18-1` | PASS |
| CHECK-T18-03 | 4 nút chọn tab nằm trong `<header>`, không còn thanh cố định ở đáy màn hình | E1 — `T18-2` | PASS |
| CHECK-T18-04 | Điều hướng vẫn refresh-safe qua URL hash | E1 — kế thừa `test_stepb_ui.js`/quan sát thủ công | PASS |
| CHECK-T18-05 | `#l1Entry` vẫn tương tác được bất kể tab nào đang active (không bị gate) | E1 — toàn bộ `enter()`/`saveEvent()` của test cũ PASS không sửa | PASS |
| CHECK-T18-06 | `test_t12_browser.js` (Completion Gate gốc `CHECK-T13-12`) PASS nguyên số assertion, không xoá/nới lỏng case nào | E1 — `T18-3` | PASS |
| CHECK-T18-07 | `test_stepb_ui.js` PASS nguyên số assertion | E1 — `T18-3` | PASS |
| CHECK-T18-08 | `test_t14_backup_restore.js` PASS nguyên số assertion | E1 — `T18-3` | PASS |
| CHECK-T18-09 | `test_t14_persistence.js` PASS nguyên số assertion | E1 — `T18-3` | PASS |
| CHECK-T18-10 | Toàn bộ `npm test` (10 file, gồm emulator + browser) PASS, exit 0 | E1 — `T18-4` | PASS |
| CHECK-T18-11 | Đúng ngân sách artifact: 1 task file, 1 báo cáo gộp, 1 DEC, 0 evidence log | E1 — `git show --stat` | PASS |

Mức bằng chứng: E1 toàn bộ — không chạm `accounting_financial`, cùng lý do đã lập tại `T-17`.

## Exit Criteria

- 11/11 REQUIRED PASS. `npm test` exit 0, không suite nào bị bỏ qua, không assertion nào bị xoá/
  nới lỏng ở 4 file test bị sửa.
- Báo cáo nêu rõ: cách xác định phương thức Playwright nào cần tab active (đọc vs hành động), mọi
  điểm bị sửa trong 4 file test và lý do, xác nhận điều kiện tiên quyết + ngân sách.
- `branch_authority_check.sh` chạy trước khi kết thúc.

## Stop conditions

- Một hành động test cần sửa mà không có cách giữ assertion nguyên vẹn → DỪNG, hỏi Owner.
- `webapp/ledger.js` cần sửa để đạt mục tiêu điều hướng → DỪNG — ngoài phạm vi được phép.

## Implementation authority

`DEC-054` (Owner Direction + Lifecycle Closure).
