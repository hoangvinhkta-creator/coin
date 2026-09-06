# T-16 — CoinDCA L-1: sổ đa tài sản (BTC/ETH/ADA), SELL đúng, CASH DEPOSIT/WITHDRAW

## Metadata

Status:
DONE

Lịch sử trạng thái: `NOT_PLANNED → READY → IN_PROGRESS → IMPLEMENTED → DONE` trong cùng một
phiên `S043` (2026-09-06, nhánh `claude/fix-7-ledger-errors-91dybv`, nối tiếp `T-15`). Thẩm
quyền: chỉ thị phiên trực tiếp của Owner ("Mở rộng sổ L-1 sang đa tài sản… làm đúng lại lệnh
BÁN… thêm CASH DEPOSIT"), ghi lại thành `DEC-052`. Cùng khuôn `STATE_AUTHORITY.md` đã dùng cho
`T-12`/`T-13`/`T-14`/`T-15`.

Điều kiện tiên quyết đã kiểm:
`DEC-051` tồn tại (`PROJECT/PROJECT_DECISIONS.md`), `docs/tasks/T-15-*.md` `Status: DONE`,
commit `2fd5711`/`322f009`/`72d8eee` có trong `git log`. Đủ điều kiện bắt đầu.

Phase:
CoinDCA L-1 — **mở rộng phạm vi sổ**, chèn giữa `T-15` và bước D. Không phải bước mới của chuỗi
A → B → C → D; đây là mở rộng từ vựng sự kiện + hình dạng nắm giữ để chuẩn bị nhập sổ Excel
theo dõi thủ công từ 08/10/2025.

Task Mode:
MAJOR — `Risk 3`, `Blast Radius 3`, có bump schema bền (`coindca.ledger/2 → /3`).

Capability:
`CAP-WEBAPP` (lineage root `WP-C1`). **KHÔNG** tạo capability mới. Tách một capability riêng chỉ
để thoát ngân sách sửa đã cạn chính là thứ `GOVERNANCE_V4.md` §II.2 cấm
(*"Creating a new unit of work — including a sibling at the same level — is not among them"*).

Loại tiêu thụ budget:
**INITIAL IMPLEMENTATION — tiêu 0 repair cycle.** `T-16` là công việc MỚI (mở rộng phạm vi), không
phải lượt sửa sau một finding trên mã đã `DONE` — khác hẳn `T-15`. Theo tiền lệ đã dùng cho
`T-09A`/`T-09B`/`WP-C2`/`WP-B1`, implementation ban đầu của một task chưa từng `DONE` không tiêu
repair cycle. `USED` giữ nguyên **2**.
**Nhưng `REMAINING = 0`** sau `T-15`, nghĩa là nếu `T-16` cần một lượt sửa thì không còn gì để
tiêu. Owner đã uỷ quyền tường minh trong chỉ thị phiên; ghi nhận thành **`OWNER_EXTENSION` +2**
(`ALLOWED 2 → 4`, `REMAINING 0 → 2`) tại `DEC-052` §E. Budget **không** được reset — chỉ được
Owner cấp thêm, có ghi ngày và lý do.

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
C: 1
F: 3

Routing Categories:
accounting_financial

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.7

Effort Score:
2.5

Routing Floors:
model `safety_business:min_C`; effort `safety_business:min_high` (không ràng buộc — điểm tự
nhiên đã là `xhigh`). Lệnh tái lập:
`python3 governance/scripts/governance/routing_engine.py --d 3 --r 3 --b 3 --a 2 --x 2 --u 2
--v 3 --h 3 --c 1 --f 3 --category accounting_financial`

## Objective

Mở sổ L-1 sang ba tài sản (BTC/ETH/ADA) ở tầng nắm giữ, thiết kế đúng lệnh BÁN, và thêm loại sự
kiện tiền mặt — đủ để nhập một sổ Excel theo dõi thủ công có sẵn mà không phải bịa dữ liệu và
không bị cờ bắn oan.

## Product consequence

Không có ba việc này thì sổ Excel nguồn **không nhập được**: nó có nhiều coin (sổ chỉ nhận ETH),
có lệnh bán (`T-15` chặn `SELL` ở cổng vào), và không có sự kiện nào ghi việc bỏ tiền mặt vào ví
nên `vnd.balance` âm ngay từ giao dịch đầu tiên và `LEDGER_INCONSISTENT` bắn oan trên dữ liệu
hoàn toàn hợp lệ.

## Scope IN

- `webapp/ledger.js` — bump `SCHEMA` v2→v3 + `migrateV3()`; whitelist tài sản; `openingCheck`
  N tài sản; `eventCheck` đa symbol + kind `CASH` + mở lại `SELL`; `planCheck` đơn tài sản
  không hardcode ETH; `derive()` holdings theo bản đồ symbol, SELL đúng, `realizedPnlUsdt`,
  định giá theo từng symbol.
- `webapp/ledger_ui.js` — ô chọn tài sản (số dư đầu kỳ / TRADE / PRICE / kế hoạch), mở lại
  `SELL` + nhãn "Bán", form CASH, dashboard theo từng coin, hai ô lãi/lỗ tách đơn vị, nút nâng
  cấp v2→v3.
- `webapp/app_logic.js` — `validateState()` nhận diện `coindca.ledger/2` là bản HỢP LỆ chờ nâng
  cấp (nếu không, Owner không tới được nút nâng cấp).
- `webapp/test_t16_multiasset.js` (MỚI) + cập nhật test cũ giả định hình dạng cũ.

## Scope OUT (Non-goals tường minh)

- **KHÔNG** nhập file legacy thật (bước riêng, chạy ngoài repo sau khi task này merge).
- **KHÔNG** thêm khái niệm ngân sách/kế hoạch đa tài sản.
- **KHÔNG** thêm coin ngoài `BTC/ETH/ADA`; danh sách cố định trong code.
- **KHÔNG** thiết kế lại UI ngoài các điểm ở Scope IN.
- **KHÔNG** chạm `src/eth_dca_os/`, `docs/spec/*_V2_1_5.md`, khối rules app Content.
- **KHÔNG** đóng `H-46`/`H-58` toàn phần — chỉ đóng đúng phần được sửa ở đây (xem báo cáo §7).

## Ràng buộc kiến trúc đã khoá (implementer KHÔNG được quyết lại)

1. **Đa tài sản ở tầng NẮM GIỮ, đơn tài sản ở tầng KẾ HOẠCH.** Mua asset khác luôn `EXTRA`,
   không bao giờ `PLAN`, và không bao giờ cộng vào `planInvestedVnd`/`investedThisMonthVnd`.
2. Whitelist `['BTC','ETH','ADA']` cố định trong code, không mở tuỳ ý.
3. **Không migration tự động âm thầm.** Bump schema phải qua `migrate()`-style có oracle đối
   chiếu, y hệt cách v1→v2 đã làm.
4. `derive()` vẫn là hàm thuần; INV-1 không đổi; mọi phép tính tiền qua số nguyên tuyệt đối.
5. Cờ `vnd.balance < 0` của `T-15` **giữ nguyên**, không nới lỏng — `CASH DEPOSIT` mới là cách
   sửa đúng.
6. Fixture Owner `tests/fixtures/t12/owner-example.synthetic.json` là oracle đóng băng.
7. Ngân sách artifact CỨNG (`DEC-051` §B, `DEC-052` §B): 1 task file, 1 báo cáo gộp, 1 DEC
   closure, 0 evidence log commit.

## Change budget (ước lượng có ràng buộc)

Ước lượng: ≤ 12 file, ≤ 700 dòng. Thực tế đo được ghi ở báo cáo §2.

## Ready Gate

| # | Điều kiện | Trạng thái |
|---|---|---|
| RG-1 | Điều kiện tiên quyết `DEC-051`/`T-15 DONE` đã kiểm bằng `git log` + file | PASS |
| RG-2 | Phân loại budget + `OWNER_EXTENSION` xử lý xong TRƯỚC dòng mã đầu tiên | PASS — `DEC-052` §E |
| RG-3 | Ranh giới đa tài sản / đơn kế hoạch phát biểu được thành một luật kiểm được | PASS |
| RG-4 | Đường nâng cấp schema có oracle, fail-closed, không tự chạy | PASS |
| RG-5 | Oracle không đổi được xác định (fixture Owner, mutation suite) | PASS |
| RG-6 | Đọc lại code thật quanh mọi vị trí trước khi sửa; ghi mọi chỗ mô tả lệch | PASS — báo cáo §1 |
| RG-7 | Ngân sách artifact được khai và kiểm được | PASS |

## Completion Gate

FROZEN 2026-09-06. Tất cả REQUIRED.

| # | Check | Evidence | Kết quả |
|---|---|---|---|
| CHECK-T16-01 | Bump `coindca.ledger/2 → /3`; sổ v2 KHÔNG tự động được nhận là v3 | E1 — `T16-1` | PASS |
| CHECK-T16-02 | `migrateV3()` có oracle số học ĐỘC LẬP (replay v2 không gọi `derive()`) + oracle hình dạng; lệch là từ chối, không ghi | E1 — `T16-1`, `T16-2` | PASS |
| CHECK-T16-03 | `openingCheck` nhận 0..N tài sản trong whitelist; từ chối symbol lạ và symbol trùng | E1 — `T16-3` | PASS |
| CHECK-T16-04 | `TRADE.symbol` / `PRICE.symbol` nhận cả ba coin; từ chối symbol lạ | E1 — `T16-4` | PASS |
| CHECK-T16-05 | `planCheck` nhận plan BTC/ADA; từ chối plan có hai version khác asset | E1 — `T16-5` | PASS |
| CHECK-T16-06 | `derive()` cho holding tách biệt từng coin; KHÔNG tạo entry rỗng cho coin không ai chạm tới | E1 — `T16-6` | PASS |
| CHECK-T16-07 | Định giá theo TỪNG symbol, dùng PRICE của chính symbol đó, giữ hạn dùng 1 ngày và `usdVndRate` tuỳ chọn | E1 — `T16-7` | PASS |
| CHECK-T16-08 | Mua coin khác không lọt vào `planInvestedVnd`/`investedThisMonthVnd`; `source PLAN` sai asset bị chặn Ở VALIDATION | E1 — `T16-8` | PASS |
| CHECK-T16-09 | `CASH DEPOSIT/WITHDRAW` đổi đúng `vnd.balance`, không chạm usdt/holdings/reserve | E1 — `T16-9` | PASS |
| CHECK-T16-10 | `WITHDRAW` vượt số dư vẫn bật `LEDGER_INCONSISTENT` (bảo vệ `T-15` giữ nguyên) | E1 — `T16-10` | PASS |
| CHECK-T16-11 | Kịch bản gốc: `CASH DEPOSIT` + `VND_TO_USDT` cùng số tiền → `vnd = 0`, KHÔNG cờ; bỏ `CASH` đi thì cờ bật lại | E1 — `T16-11`, `test_stepb_ui` T-16 | PASS |
| CHECK-T16-12 | SELL — ca cụ thể tính TAY khớp tuyệt đối, gồm `realizedPnlUsdt` | E1 — `T16-12` | PASS |
| CHECK-T16-13 | SELL chỉ CHUYỂN giá vốn: tổng giá vốn VND không đổi; bán cạn về đúng 0; bán quá tay fail-closed | E1 — `T16-13` | PASS |
| CHECK-T16-14 | Property test ≥ 50 chuỗi ngẫu nhiên hợp lệ: bảo toàn giá vốn VND + số dư tiền mặt | E1 — `T16-14` (60 chuỗi) | PASS |
| CHECK-T16-15 | Đường UI thật: nâng cấp v2→v3 qua nút, có snapshot, nội dung không đổi; sổ v2 không bị ghi đè trước khi Owner bấm | E1 — `test_t12_browser` "T-16 v2->v3" | PASS |
| CHECK-T16-16 | Đường UI thật: CASH + mua BTC + bán ETH qua đúng control mới; dashboard theo từng coin; hai ô lãi/lỗ tách đơn vị | E1 — `test_stepb_ui` "T-16" | PASS |
| CHECK-T16-17 | Toàn bộ test `T-12`/`T-14`/`T-15` vẫn PASS sau khi đổi hình dạng `holdings` | E1 — `npm test` exit 0 | PASS |
| CHECK-T16-18 | Fixture Owner khớp **bit-exact** 9/9, tolerance `{vnd:0,usdt:0,qty:0}`; mutation 7/7 KILLED | E1 | PASS |
| CHECK-T16-19 | Không chạm `src/eth_dca_os/`, `docs/spec/*_V2_1_5.md`, khối rules Content | E1 — `git diff --stat` | PASS |
| CHECK-T16-20 | Đúng ngân sách artifact: 1 task file, 1 báo cáo gộp, 1 DEC, 0 evidence log | E1 — `git show --stat` | PASS |

Mức bằng chứng: E1 toàn bộ, cùng lý do đã ghi ở `DEC-051` §C và nhắc lại ở `DEC-052` §C — cộng
thêm: task này có **property test** và **hai đường UI thật trên emulator + trình duyệt thật**,
là mức phủ cao hơn `T-15`.

## Exit Criteria

- 20/20 REQUIRED PASS. Fixture Owner không đổi một bit. `npm test` exit 0.
- Báo cáo nêu rõ: cách lấy "asset của kế hoạch", mọi chỗ mô tả lệch với code thật, xác nhận
  điều kiện tiên quyết, và cách xử lý ngân sách/`OWNER_EXTENSION`.
- `branch_authority_check.sh` chạy trước khi kết thúc.

## Stop conditions

- Fixture Owner lệch → DỪNG, báo (KHÔNG cập nhật fixture).
- Mô tả trong chỉ thị lệch với code thật → DỪNG, báo (KHÔNG đoán).
- Oracle của `migrateV3` lệch → KHÔNG ghi, trả `ok:false`.

## Implementation authority

`DEC-052` (Owner Direction + Lifecycle Closure). Không quyết định kiến trúc mới nào ngoài ba
lựa chọn đã ghi ở `DEC-052` §D.
