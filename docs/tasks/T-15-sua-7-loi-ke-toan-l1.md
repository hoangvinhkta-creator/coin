# T-15 — CoinDCA L-1: sửa 7 lỗi kế toán do rà soát độc lập tái lập

## Metadata

Status:
DONE

Lịch sử trạng thái: `NOT_PLANNED → READY → IN_PROGRESS → IMPLEMENTED → DONE` trong cùng một
phiên `S042` (2026-09-06, nhánh `claude/fix-7-ledger-errors-91dybv`). Thẩm quyền: chỉ thị phiên
trực tiếp của Owner ("COINDCA — SỬA 7 LỖI KẾ TOÁN L-1", kèm bản rà soát độc lập
`COINDCA_L1_REVIEW_T12_T14.md` ngày 2026-09-06, repo @ `6c1d894`), ghi lại thành `DEC-051`.
Cùng khuôn thẩm quyền `STATE_AUTHORITY.md` đã dùng cho `T-09B`/`T-12`/`T-13`/`T-14`.

Phase:
CoinDCA L-1 — **sửa lỗi sau bước C**, chèn giữa C và D. Không phải bước mới của chuỗi
A → B → C → D; đây là repair cycle của chính lát cắt đã chạy.

Task Mode:
MAJOR — `Risk 3 > 2` và `Blast Radius 3 > 2` (đường tiền production), nên KHÔNG đủ điều kiện
MICRO theo `governance/core/TASK_MODE_STANDARD.md` Mode 1.

Lớp (RCP-001):
Không thuộc RCP-001.

Completion Gate Freeze:
FROZEN — 2026-09-06 (`S042`, cùng phiên tạo task).

Capability:
`CAP-WEBAPP` (lineage root `WP-C1`). **KHÔNG** tạo capability mới, **KHÔNG** tạo lineage root
mới, **KHÔNG** tạo task ID nào ngoài `T-15`.

Loại tiêu thụ budget:
**REPAIR CYCLE #2 của `CAP-WEBAPP`.** Đây KHÔNG phải implementation ban đầu: 7 lỗi nằm trong
mã production đã `DONE` (`T-12`/`T-13`/`T-14`), do một rà soát độc lập tái lập SAU khi các
task đó đóng — đúng tình huống `REVIEW_BUDGET_LEDGER.md` §4.3 mô tả ("không phải khiếm khuyết
của một lượt sửa đã tiêu, nên sửa nó SẼ tiêu một repair cycle mới").
`ALLOWED 2 / USED 1 → 2 / REMAINING 1 → 0`.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 3
A: 1
X: 1
U: 1
V: 3
H: 3
C: 1
F: 2

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
high

Model Routing Score:
2.4

Effort Score:
2.05

Routing Floors:
model `safety_business:min_C`; effort `safety_business:min_high`. Lệnh tái lập:
`python3 governance/scripts/governance/routing_engine.py --d 3 --r 3 --b 3 --a 1 --x 1 --u 1
--v 3 --h 3 --c 1 --f 2 --category accounting_financial`

## Objective

Sửa đúng 7 lỗi kế toán mà rà soát độc lập tái lập được bằng harness nạp trực tiếp
`webapp/ledger.js`, không mở rộng phạm vi, và bổ sung test tái lập cho từng lỗi (đỏ trước,
xanh sau).

## Product consequence

Lỗi L1 hỏng đúng tính năng lõi của L-1 ("Mua kế tiếp") vào **mỗi cuối tháng**; L2 khiến tiền
carry của `CAPPED_CARRY` không bao giờ lên lịch mua; L4 cho phép một bất biến kế toán
(bảo toàn tổng giá vốn VND) vỡ trong im lặng; L5 cho sửa hồi tố ngân sách tháng đã đóng;
L6 khoá vĩnh viễn mọi sổ cũ có phí giao dịch ở chế độ LEGACY chỉ-đọc. Không sửa thì không
được dùng với tiền thật (`H-41`).

## Scope IN

- `webapp/ledger.js` — 7 nhóm sửa L1…L7 (chi tiết ở Completion Gate).
- `webapp/ledger_ui.js` — hint kế hoạch sai sự thật; nhãn "(Bán)" chết; `try/catch` cho
  snapshot cục bộ; hiển thị định giá quy đổi VND.
- `webapp/build_app.js` — gỡ `engine.js` khỏi bundle, đổi assertion.
- `webapp/test_l1_fixes.js` (MỚI) — test tái lập 7 lỗi.
- Cập nhật test cũ đã khẳng định hành vi SAI (`test_t12_ledger.js`, `test_t12_browser.js`).
- `webapp/package.json` — nối suite mới vào `npm test`.

## Scope OUT (Non-goals tường minh)

- **KHÔNG** thiết kế P&L thực hiện (`H-46`) — L4 chỉ chặn đường vào.
- **KHÔNG** chạm `src/eth_dca_os/` và `docs/spec/*_V2_1_5.md` (frozen research, `DEC-041` A).
- **KHÔNG** chạm khối rules của app Content trong `firestore.rules`.
- **KHÔNG** xử lý các mục Nhóm 2 (vận hành: `firebase target:apply`, UID thật, deploy,
  tắt Anonymous provider) — nằm ngoài repo.
- **KHÔNG** xử lý các mục 🟡 còn lại của bản rà soát không nằm trong 7 lỗi được giao
  (`RESERVE CONTRIBUTE` không trừ `vnd.balance`; trần 1 MiB; `startMonth = '0001-01'`;
  `LEGACY_ARCHIVE`/`RESEARCH_ONLY` không giới hạn kích thước) — ghi vào HARDENING.

## Dependencies

`T-12`, `T-13`, `T-14` đều `DONE`. Không phụ thuộc gì khác.

## Expected Touch Area

`webapp/ledger.js`, `webapp/ledger_ui.js`, `webapp/build_app.js`, `webapp/package.json`,
`webapp/test_l1_fixes.js`, `webapp/test_t12_ledger.js`, `webapp/test_t12_browser.js`.

## Ràng buộc kiến trúc đã khoá (implementer KHÔNG được quyết lại)

1. `derive()` vẫn là hàm thuần; INV-1 (không lưu trường dẫn xuất) không đổi.
2. Mọi phép tính tiền vẫn qua `BigInt`/số nguyên tuyệt đối; không float.
3. `OD-L1-4 STRICT` giữ nguyên: không biết giá vốn VND thì lan `null` + cờ, **cấm bịa tỷ giá**.
4. Fixture Owner `tests/fixtures/t12/owner-example.synthetic.json` là oracle đóng băng.
   Nếu một bản sửa làm fixture lệch → DỪNG và báo, KHÔNG cập nhật fixture.
5. Ngân sách artifact CỨNG (`DEC-051` §B): 1 task file, 1 báo cáo gộp, 1 DEC closure,
   0 evidence log commit.

## Change budget (ước lượng có ràng buộc)

Ước lượng: ≤ 8 file production/test, ≤ 300 dòng. Thực tế đo được ghi ở báo cáo §2.

## Budget review/repair

REPAIR CYCLE #2 của `CAP-WEBAPP` (xem Metadata). Sau lượt này `REMAINING = 0` — mọi lượt sửa
tiếp theo cho `CAP-WEBAPP` cần `OWNER_EXTENSION`.

## Ready Gate

| # | Điều kiện | Trạng thái |
|---|---|---|
| RG-1 | 7 lỗi được mô tả kèm số liệu tái lập cụ thể | PASS — bản rà soát §2 + chỉ thị phiên |
| RG-2 | Ranh giới Scope OUT tường minh (H-46, frozen artifact, rules Content) | PASS |
| RG-3 | Oracle không đổi được xác định (fixture Owner, 9 trường, tolerance 0) | PASS |
| RG-4 | Xác nhận số dòng/mô tả khớp code thật trước mỗi sửa | PASS — báo cáo §1 ghi mọi chỗ lệch |
| RG-5 | Đường chạy test không cần emulator được liệt kê | PASS |
| RG-6 | Ngân sách artifact được khai và có thể kiểm | PASS — `DEC-051` §B |
| RG-7 | Capability/lineage/loại tiêu thụ budget đã xác định trước dòng mã đầu tiên | PASS |

## Completion Gate

FROZEN 2026-09-06. Tất cả REQUIRED.

| # | Check | Evidence | Kết quả |
|---|---|---|---|
| CHECK-T15-01 | L1: `asOf` 2026-01-14 / 24 / 31 cho đúng `nextPlannedDate` **và** `nextPlannedAmountVnd` (9.990.000 / 6.666.667 / 6.666.667) | E1 — `test_l1_fixes.js` "L1 …" | PASS |
| CHECK-T15-02 | L2: `sum(plannedPerSlot) == plannedBudgetVnd` ở tháng có carry-in | E1 — "L2 …" | PASS |
| CHECK-T15-03 | L3a: `planCheck` từ chối `startMonth` < `effectiveFrom` nhỏ nhất, thông báo tiếng Việt | E1 — "L3a …" | PASS |
| CHECK-T15-04 | L3b: tháng thiếu version cho `carryOut = 0`, không đầu độc chuỗi tháng sau | E1 — "L3b …" | PASS |
| CHECK-T15-05 | L3c: `plannedBudgetVnd = null` luôn bật cờ | E1 — "L3c …" | PASS |
| CHECK-T15-06 | L4: event `TRADE side=SELL` bị từ chối ở `canonical`/`derive`/`update`, thông báo dẫn `H-46` | E1 — "L4 …" | PASS |
| CHECK-T15-07 | L5: đổi `monthlyBudgetVnd` (và mọi trường trọng yếu) của version cũ bị chặn | E1 — "L5 …" | PASS |
| CHECK-T15-08 | L6: sổ legacy `fee = 0,5 USDT` migrate THÀNH CÔNG; lệch `costVnd` lớn là cờ cứng | E1 — hai test "L6 …" | PASS |
| CHECK-T15-09 | L7a/c/d/e: `__proto__` own-property; VND âm bật cờ; `priceUsdt = 0` bị từ chối; BUY `feeUsdt > usdtNotional` bị từ chối | E1 — bốn test "L7…" | PASS |
| CHECK-T15-10 | L7f: `usdVndRate` được `derive()` dùng thật (định giá), không còn trường chết | E1 — "L7f …" | PASS |
| CHECK-T15-11 | L7g: `engine.js` không còn trong bundle; assertion build đổi chiều | E1 — "L7g …" + `node build_app.js` | PASS |
| CHECK-T15-12 | Fixture Owner khớp **bit-exact** cả 9 trường, tolerance `{vnd:0,usdt:0,qty:0}` | E1 — `test_t12_owner.js` | PASS |
| CHECK-T15-13 | Mutation suite `test_t12_mutations.js`: 7/7 mutant KILLED, 0 survivor | E1 | PASS |
| CHECK-T15-14 | `npm --prefix webapp test` exit 0 với Firestore Emulator + Playwright thật | E1 | PASS |
| CHECK-T15-15 | Không chạm `src/eth_dca_os/`, `docs/spec/*_V2_1_5.md`, khối rules Content | E1 — `git diff --stat` | PASS |
| CHECK-T15-16 | Đúng ngân sách artifact: 1 task file, 1 báo cáo gộp, 1 DEC, 0 evidence log | E1 — `git show --stat` | PASS |

Mức bằng chứng: E1 toàn bộ. Gate này KHÔNG đòi vòng E2 độc lập — công việc là sửa 7 lỗi đã
được một rà soát ĐỘC LẬP (không phải implementer) tái lập và mô tả bằng số liệu; test tái lập
đỏ-trước/xanh-sau đóng vai trò oracle độc lập với người sửa. Quyết định này thuộc `DEC-051` §C.

## Exit Criteria

- 16/16 REQUIRED PASS.
- Fixture Owner không đổi một bit.
- Báo cáo gộp nêu rõ ba lựa chọn (L1 carry tháng sau, L7f dùng/bỏ `usdVndRate`, L7g gỡ/giữ
  `engine.js`) và mọi chỗ mô tả lệch với code thật.
- `branch_authority_check.sh` chạy trước khi kết thúc phiên.

## Stop conditions

- Fixture Owner lệch → DỪNG, báo Owner (KHÔNG cập nhật fixture).
- Mô tả lỗi lệch với code thật → DỪNG, báo (KHÔNG đoán).
- Có state/fixture production chứa `SELL` → DỪNG, báo trước khi chặn.

## Changed Files Registry

Xem `docs/reviews/T15-IMPLEMENTATION-AND-E2-REPORT.md` §2 (đo trực tiếp, không cộng tay).

## Implementation authority

`DEC-051` (Owner Direction + Lifecycle Closure). Không quyết định kiến trúc mới nào được tạo
trong task này.
