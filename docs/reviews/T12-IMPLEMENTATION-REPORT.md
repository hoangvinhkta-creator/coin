# T-12 Implementation Report

Báo cáo phiên S034 — 2026-09-05. Kết quả: **OWNER_DECISION_REQUIRED**, dừng trước implementation.

## 1. Executive Summary

T-12 **chưa được thi hành**. `STATUS = OWNER_DECISION_REQUIRED`; task `READY → BLOCKED` ở DISCOVER. SC-04 yêu cầu remainingPlannedBudget(2026-02) = 7.090.822 VND, nhưng §11.2/§11.4 và DEC-042 bắt buộc 11.775.522 VND (carryIn = 4.684.700 VND).

Đây là xung đột hợp đồng, không phải lỗi implementation hay lỗi công cụ. Không sửa spec/gate, không tạo fixture để ép xanh, không tiêu repair cycle.

## 2. Source / Branch / Base

Ngày: 2026-09-05. Agent thực thi: Codex / GPT-6 Astra. Nhánh: `codex/t12-l1-ledger-impl`.

`HEAD = origin/main = 7d1985aaf306294df49c9508078d5425da10f47e`. Kiểm tra ban đầu PASS, tracked worktree CLEAN, ahead 0, behind upstream 0. Fetch trong sandbox ban đầu thất bại (`STALE_REMOTE`); `git fetch origin --prune` ngoài sandbox sau đó exit 0 và xác nhận base không đổi. Nhánh remote T-12 chưa tồn tại lúc kiểm tra trước commit. `data/` là untracked có sẵn, không đọc nội dung, không đưa vào commit.

Runtime kiểm chứng số học: Python 3.9.6; Node v24.19.0. Không chạy emulator, không truy cập Firebase thật.

## 3. Ready Gate

17/17 là evidence lịch sử của S033. Phiên này **không tái xác nhận được Ready Gate 17/17**: không thể thực hiện đồng thời yêu cầu kế toán canonical và oracle SC-04. Không áp dụng `READY → IN_PROGRESS`. Quyền dừng nằm tại T-12 § Stop conditions: một số kỳ vọng SC mâu thuẫn spec → `OWNER_DECISION_REQUIRED` + `COMPLETION GATE CHANGE PROPOSAL`.

Các quyền persistence/dữ liệu của DEC-043 vẫn đủ; dữ liệu thật không phải blocker. Routing đã tính lại: D/max, 3.1/3.65; validator routing PASS trên 20 MAJOR task.

### Bằng chứng mâu thuẫn — E1 số học, không phải test production

SC-01…SC-04 nối tiếp nhau theo ma trận SC của task. Kế hoạch chung bắt đầu 2026-01; opening 2026-01-01; ngân sách 20.000.000; CAPPED_CARRY cap 1. SC-03 ghi planInvested tháng 1 = 15.315.300. Khi tính tháng 2, tháng 1 đã đóng.

| Đại lượng | Theo §11.2/§11.4 | SC-04 |
|---|---:|---:|
| carryOut tháng 1 | 4.684.700 | không ghi |
| carryIn tháng 2 | 4.684.700 | không ghi |
| plannedBudget tháng 2 | 24.684.700 | không ghi |
| planInvested tháng 2 | 12.909.178 | 12.909.178 |
| remainingPlannedBudget tháng 2 | **11.775.522** | **7.090.822** |

Phép tính tái lập, chỉ dùng số nguyên/phân số, không phụ thuộc FX, đồng hồ, dữ liệu thật hoặc implementation:

```python
from fractions import Fraction
budget = 20_000_000
jan_invested = 15_315_300
x = Fraction(500) * 28_384_700 / Fraction(10994, 10)
relieved = (2*x.numerator + x.denominator) // (2*x.denominator)
carry = min(max(0, budget-jan_invested), budget)
remaining = max(0, budget+carry-relieved)
print(relieved, carry, remaining, remaining-7_090_822)
assert relieved == 12_909_178
assert carry == 4_684_700
assert remaining == 11_775_522
assert remaining != 7_090_822
```

Đã chạy công thức tương đương trong phiên: `12909178 4684700 11775522 4684700`, exit 0. Con số WAC 12.909.178 của SC-04 đúng; mâu thuẫn nằm ở carry. Không tồn tại asOfDate thuộc tháng 2 vừa giữ tháng 1 chưa đóng. Không thể đổi plan.startMonth, opening.asOf hoặc thêm một trade tháng 1 để ép kỳ vọng mà vẫn giữ nguyên fixture nối SC-03.

`CHECK-T12-08` đòi đúng tuyệt đối SC-04 trong khi `CHECK-T12-06`, Scope S-A10 và DEC-042 đòi carry canonical. Chưa chạy các check production; không ghi FAIL implementation giả.

## 4. Pre-Implementation Production Map

Đã đọc mã hiện tại:

| Đường | Hiện trạng |
|---|---|
| build_app.js → app_final.html / public/index.html | Ghép shell + Firebase config + engine + app_logic |
| app_logic.js:20 emptyState | ethdca.tracker/1; accumulator eth/costUsdt/costVnd/treasury, pools và ledger legacy |
| app_logic.js:129 currentMonth | Chọn khoá tháng lớn nhất |
| app_logic.js:454 render | Hiển thị từ state/view legacy |
| app_logic.js:870 validateState | Chỉ nhận schema legacy |
| app_logic.js:972 persist | Snapshot state → runTransaction → ethdca/state; kiểm rev trước tx.set; ghi nhận server ack |
| app_logic.js:1165 initPersistence | Đọc ethdca/state và ethdca/seed với source: server, kiểm state |
| test_firebase_harness.js | Playwright + SDK thật + Firestore/Auth emulator, rules repo; REST đối chứng |

Đây là bản đồ từ đọc mã (E0), chưa phải trace P-1…P-6. Chưa có L-1 API/derive trong production.

## 5. Capability Boundary

Giữ đúng T-12 / CAP-WEBAPP / lineage WP-C1. Bước A theo spec §24; B/C/D chưa mở. Không hấp thụ hạng mục, không task ID mới, không sửa research/strategy/Firebase/auth/Hosting. Xung đột được chuyển về Owner của chính T-12; không tạo task từ finding.

## 6. Change Budget

Production **0 file, +0/−0**. Trần giữ +1.600/−450 và ≤7 file. Mốc đo task vẫn `91cfbba5e3af01d432c64369bb5a286f6461ab6a`; base phiên `7d1985a…` không thay thế nó. Không có diff production nên không tiêu budget.

## 7. Implemented Data Model

NOT_TESTED / chưa cài đặt. Không schema mới xuống durable. Hợp đồng coindca.ledger/2 giữ nguyên.

## 8. derive() Semantics

Chưa cài đặt. Contract mở ở SC-04/carry như §3; không chọn một phía bằng mã. Không tạo nguồn sự thật cạnh tranh.

## 9. USDT WAC / VND Cost Basis

Chưa cài đặt. Số học WAC riêng của SC-04 đã kiểm: ROUND_HALF_UP(500 × 28.384.700 / 1.099,4) = 12.909.178 VND. Đây không phải bằng chứng CHECK-T12-03 PASS.

## 10. UNKNOWN Semantics

Chưa cài đặt/chưa test. DEC-042 STRICT/FAIL-VISIBLE giữ nguyên; không thêm FX fallback, không chuyển UNKNOWN thành 0.

## 11. Date / Month / Ordering

Chưa cài đặt. Mâu thuẫn chính cần Owner là carry tháng 1 sang tháng 2. Khi viết fixture về sau, SC-09/SC-10 cần ghi rõ phép kiểm carryOut tháng 3 được đánh giá ở thời điểm tháng đã đóng; input hiện nêu 18/03 và 21/03. Đây là điểm cần làm rõ thời điểm đánh giá, không kết luận thêm lỗi số học hay tự sửa scenario.

## 12. Edit / Delete / Late Entry

NOT_TESTED. Chưa thêm API edit/hard-delete/late-entry. Yêu cầu id/seq ổn định và snapshot giữ nguyên.

## 13. Migration

NOT_TESTED. Không chạy migration; không có nguồn dữ liệu thật nào được đọc. M-1…M-4, W-1, bốn phân loại canonical và đối chiếu §17.3 vẫn nguyên vẹn.

## 14. Persistence

NOT_TESTED cho T-12. Không đổi serializer, Firestore document, rules, auth hoặc Hosting. Không ghi durable.

## 15. T12 Golden Accounting Baseline

**CHƯA TỒN TẠI.** 0 fixture SC được tạo/commit. T12_GOLDEN_ACCOUNTING_BASELINE_SHA là commit SHA theo DEC-043, không phải hash nội dung tuỳ chọn. Commit báo cáo của phiên này không phải freeze point vì không chứa fixture. Không đổi GOLDEN_BASELINE_SHA lịch sử T-06.

## 16. SC-01…SC-12 Results

Tất cả **NOT_TESTED** trên production; chưa có golden suite.

| SC | Kết quả |
|---|---|
| SC-01 | NOT_TESTED |
| SC-02 | NOT_TESTED |
| SC-03 | NOT_TESTED |
| SC-04 | NOT_TESTED; xung đột carry xác minh ở §3 |
| SC-05 | NOT_TESTED |
| SC-06 | NOT_TESTED |
| SC-07 | NOT_TESTED |
| SC-08 | NOT_TESTED |
| SC-09 | NOT_TESTED |
| SC-10 | NOT_TESTED |
| SC-11 | NOT_TESTED |
| SC-12 | NOT_TESTED |

Không lấy phép tính chẩn đoán làm SC PASS. Golden baseline chưa được đóng băng.

## 17. INV-1…INV-15 Coverage

INV-1…INV-15: **0/15 test nhắm đích được tạo/chạy**; tất cả NOT_TESTED. Giữ ma trận frozen; đặc biệt INV-4, INV-7, INV-14, INV-15 không được bỏ khi triển khai lại.

## 18. Mutation Evidence

NOT_TESTED; **0/7** mutation bắt buộc (INV-1/3/4/9/11/12/14). Không mutation nào được làm yếu.

## 19. Production Reachability P-1…P-6

NOT_TESTED; **0 event, 0 case** qua production L-1. Anti-vacuity: không đạt PASS. Harness chưa chạy do hard-stop trước implementation; không dùng demo tách rời thay thế.

## 20. Full Regression

**NOT_TESTED**, do dừng trước implementation, production/test diff = 0. Không chạy npm test hoặc pytest; không deselect/skip/đánh NOT_APPLICABLE bất kỳ test nào. Không rerun T-06.

| Suite | collected | passed | failed | errors | skipped | xfail/xpass | exit code |
|---|---|---|---|---|---|---|---|
| npm test | chưa đo | chưa đo | chưa đo | chưa đo | chưa đo | chưa đo | chưa chạy |
| pytest | chưa đo | chưa đo | chưa đo | chưa đo | chưa đo | chưa đo | chưa chạy |

Không ghi 0 passed/failed thay cho dữ liệu chưa đo.

## 21. Frozen Completion Gate Matrix

Ma trận dưới giữ **nguyên văn yêu cầu** từ trường Evidence của từng check; E2 theo § Evidence / E2 của task. `BLOCKED` là kết quả đánh giá giao việc hiện tại; trạng thái test thực tế trong task vẫn **NOT_TESTED**. Không một check nào có evidence implementation hay test artifact mới.

### CHECK-T12-01 — Schema L-1 canonical, không rò rỉ sự thật chiến lược legacy

Yêu cầu: durable state mang `schema = "coindca.ledger/2"`; chứa đúng `plan`, `openingPosition`,
`events[]` theo §5; **không** chứa `months[].base/smart/oppAdded/oppOverflow`, `oppFund`,
`ladders`, `zones`, `trades[].src ∈ {BASE,SMART,OPPORTUNITY}`, `recPrice`, `shortfallBps`,
`zone` như dữ liệu tài chính. `ledger[]` legacy nếu giữ thì mang nhãn `LEGACY_ARCHIVE` và
không phép dẫn xuất nào đọc. Bằng chứng: quét khoá trên payload durable thật + danh sách khoá bị
cấm.

- Evidence yêu cầu: E1.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-02 — `openingPosition + events -> derive()` tất định

Yêu cầu: `derive()` là hàm thuần (không `new Date()` bên trong, không đọc `createdAt`), cùng
tập event cho cùng `DerivedState` dưới ≥ 100 hoán vị thứ tự nhập và ≥ 2 `TZ` tiến trình khác
nhau. Phủ `INV-2`, `INV-6`. Golden: `SC-04`, `SC-07`, `SC-08`.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-03 — Giá vốn VND: WAC trên một pool USDT, đúng số

Yêu cầu: `vndRelieved = ROUND_VND(usdtOut × usdtCostVnd / usdtQty)`; giải phóng theo bình quân
**không** làm đổi bình quân; phí USDT vào cả hai giá vốn; bán crypto/bán USDT giải phóng theo
cùng phương pháp; cạn pool ép `usdtCostVnd = 0` và đẩy phần dư vào `realizedFxVnd`. Số kỳ vọng
đối chiếu **tuyệt đối** (`tolerance = 0`) với `SC-01`…`SC-04`, `SC-06`. Phủ `INV-3`.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-04 — `UNKNOWN` lan truyền thấy được, không bao giờ bị ép về 0

Yêu cầu: `openingPosition.usdt.costVnd = null` (và phần USDT thiếu phủ của §8.4) → `qty` và
`costUsdt` giữ nguyên đúng, phần `costVnd` liên quan = `UNKNOWN`, hiển thị `—`, cờ
`UNKNOWN_VND_BASIS` thường trực và **không ẩn được bằng một lần bấm**. Grep schema chứng minh
**không tồn tại** trường tỷ giá nhập theo từng lệnh (`vndRateOverride` hoặc tương đương).
Phủ `INV-11`. Golden: `SC-12`.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-05 — Sửa / xoá / nhập muộn tính lại đúng, không trôi

Yêu cầu: sửa giữ `id`+`seq`, cập nhật `updatedAt`, chạy lại toàn bộ; **không tồn tại** phép
"hoàn tác tác động cũ" trong mã; xoá cứng TƯƠNG ĐƯƠNG CHÍNH XÁC với chưa từng nhập; nhập muộn
được xếp theo `businessDate` chứ không theo lúc nhập. Phủ `INV-1`, `INV-15`. Golden: `SC-05`,
`SC-06`, `SC-07`.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-06 — Ngày nghiệp vụ, `Asia/Ho_Chi_Minh`, tháng lịch

Yêu cầu: `businessDate` là chuỗi, so sánh chuỗi, `month = slice(0,7)`; **đúng một** chỗ trong
toàn bộ mã hỏi giờ hệ thống và nó trả ngày theo `Asia/Ho_Chi_Minh`; `currentMonth` = tháng của
`asOfDate`, KHÔNG phải khoá tháng lớn nhất trong dữ liệu; `carryOut` chỉ chốt cho tháng đã đóng.
Bằng chứng gồm grep chứng minh không còn `getMonth()`/`toISOString()` trong đường tính tiền.
Phủ `INV-6`. Golden: `SC-08`, `SC-11`. Đóng `B3`, `B4`, `B7` của `H-41`.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-07 — Số nguyên VND, làm tròn đối chiếu được, thứ tự tất định

Yêu cầu: quét đệ quy payload durable — 0 giá trị float ở trường tiền/lượng; `SPLIT_VND(x, n)`
với `n = 1..12` trên ≥ 50 giá trị: `Σ phần == x` tuyệt đối; `ORDER = (businessDate ASC, seq ASC)`
được kiểm bằng test. Phủ `INV-5`, `INV-13`. Đóng `B9`.

- Evidence yêu cầu: E1.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-08 — `SC-01`…`SC-12` PASS trên dữ liệu tổng hợp

Yêu cầu: **12/12** golden scenario của spec §19 chạy được và PASS, đối chiếu tuyệt đối với số
kỳ vọng đã đóng băng ở spec (không nới `tolerance`, không làm tròn để khớp). Báo cáo phải in
bảng SC × (kỳ vọng / thực tế). Ngữ nghĩa và số kỳ vọng của SC **không được viết lại**.

- Evidence yêu cầu: E1.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-09 — `INV-1`…`INV-15` được phủ, không bất biến REQUIRED nào bỏ trống

Yêu cầu: mỗi dòng của ma trận `INV` ở trên có **ít nhất một test nhắm đích** thực sự đỏ khi bất
biến bị phá (chứng minh bằng mutation/nghịch đảo có chủ đích cho tối thiểu `INV-1`, `INV-3`,
`INV-4`, `INV-9`, `INV-11`, `INV-12`, `INV-14`). Không được để một `INV` chỉ "được phủ gián
tiếp" bởi một SC mà không có phép khẳng định trực tiếp.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-10 — Hợp đồng migration PASS, gồm dữ liệu mơ hồ

Yêu cầu, trên fixture legacy **tổng hợp**:
(a) snapshot legacy được ghi TRƯỚC mọi thao tác ghi (`INV-14`);
(b) phát hiện version tất định;
(c) phân loại §17.2 áp đúng cho từng trường; `trades[].vndRate/vndCost` bị bỏ và tính lại;
(d) đối chiếu §17.3 trong ngưỡng; vượt ngưỡng ⇒ FAIL migration (kiểm bằng một fixture cố ý lệch);
(e) `M-1`…`M-4` ⇒ **DỪNG, durable không đổi một byte** (`INV-12`);
(f) `W-1` ⇒ **HOÀN TẤT kèm cờ `UNKNOWN_VND_BASIS`**, không bịa tỷ giá (`SC-12`);
(g) dữ liệu legacy không bị xoá; `ledger[]` chỉ đọc;
(h) không `Base`/`Smart`/`Opportunity`/`ladder`/`zone`/`score` nào lọt vào sự thật tài chính L-1.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-11 — Round-trip persistence giữ nguyên sự thật sổ cái

Yêu cầu: ghi → máy chủ xác nhận → đọc lại từ SERVER → `derive()` cho `DerivedState` **trùng
tuyệt đối**; payload durable không chứa khoá dẫn xuất bị cấm (`INV-1`); nếu file export có khối
`derivedSnapshot` thì import **bỏ qua** khối đó (kiểm bằng file export bị sửa tay). Sổ nằm trong
document `ethdca/state` đã được `firestore.rules` allow-list — **không** tạo document mới.

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-12 — Production Reachability PASS

Yêu cầu: `P-1`…`P-6` của § Production Reachability, đo trên `app_final.html` đã build qua
`webapp/test_firebase_harness.js` (Playwright + Firestore Emulator + rules thật). Báo cáo phải
nêu **số event thật** và **số case** đã chạy qua đường production. `0 event / 0 case = FAIL`.
Mọi file runtime MỚI được khai vào `PROJECT/PRODUCTION_PATHS.md` §1 (khiếm khuyết `H-32` không
được lặp lại).

- Evidence yêu cầu: E1 + E2 độc lập.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-13 — Regression áp dụng được PASS, không test nào bị làm yếu

Yêu cầu: chạy đủ suite áp dụng được (`webapp/`: `npm test`; Python: `pytest`) và báo cáo con số
trước/sau. Test cũ mô tả hành vi **đã bị `DEC-041`/`DEC-042` gỡ bỏ** (ladder/zone/pool
Base-Smart-Opportunity) chỉ được đánh dấu `NOT_APPLICABLE` kèm neo quyết định tường minh, từng
file, từng ca — **không** được xoá/skip/deselect hàng loạt để lấy suite xanh, và số ca
`NOT_APPLICABLE` phải được liệt kê đích danh trong báo cáo. Không test nào của `src/eth_dca_os`
được đổi.

- Evidence yêu cầu: E1.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.

### CHECK-T12-14 — Không hồi quy productization chiến lược

Yêu cầu: Buy Score / OSCORE / regime / crash / ladder / recommendation **không** nằm trên đường
quyết định tài chính L-1: (a) module sổ cái không tham chiếu `ENGINE`/`engine.js`; (b) đổi tuỳ ý
dữ liệu chỉ báo và event `PRICE` → phần tiền của `DerivedState` **không đổi**; (c) không tín
hiệu nào tạo/gợi ý/định cỡ một `TRADE`, đặc biệt `source = RESERVE` (bắt buộc có `note` do người
dùng nhập). Phủ `INV-10`. Neo: `DEC-041` B, `DEC-042` §3, spec §12.3.

- Evidence yêu cầu: E1.
- Evidence implementation: chưa có.
- Test/artifact: NOT_TESTED; báo cáo §3 chỉ chứng minh xung đột hợp đồng.
- Đánh giá: **BLOCKED** — chưa có implementation để kiểm; Owner phải đóng xung đột trước.



## 22. Repair Cycle

`REPAIR_CYCLE_1 = NOT_CONSUMED`. CAP-WEBAPP allowed 2 / used 0 / remaining 2. T-12 pre-authorized 1 chưa dùng. Xung đột đòi quyết định ngữ nghĩa/oracle, nên không đủ điều kiện DEC-043 để dùng repair. Không có failed REQUIRED runtime check, không có bounded repair hay rerun production.

## 23. Findings / Hardening

Một xung đột hợp đồng đã xác minh: **SC-04 / carry**, Owner hiện hành T-12; phân loại `OWNER_DECISION_REQUIRED` theo Stop conditions tường minh, không tự gắn nhãn CONFIRMED production defect khi chưa có runtime L-1. Không task ID mới. H-41/H-42/H-43 không đóng và không sửa.

H-08 có sẵn: evidence/task_completion dùng glob TASK-*.md nên không phủ task T-/WP-. Chạy validator và báo rõ giới hạn; không sửa tooling ngoài scope, không nhận output 0-record làm PASS có ý nghĩa.

## 24. Production Diff

Lệnh đo bắt buộc:

```bash
git diff --shortstat 91cfbba5e3af01d432c64369bb5a286f6461ab6a -- src/eth_dca_os webapp pyproject.toml pyproject.lock
git diff --shortstat 7d1985aaf306294df49c9508078d5425da10f47e -- src/eth_dca_os webapp pyproject.toml pyproject.lock
```

Kết quả ghi tại §26 sau kiểm chứng. docs/spec/, docs/spec-l1/, tests/, Firebase config/rules phải giữ diff rỗng.

## 25. Files Changed

Tạo:

- docs/reviews/T12-IMPLEMENTATION-REPORT.md — báo cáo bắt buộc và đề xuất chờ Owner.
- docs/sessions/S034-t12-ledger-discovery-stop.md — handoff MAJOR.

Sửa:

- docs/tasks/T-12-so-cai-l1-v2-va-derive.md — trạng thái BLOCKED, ghi lý do; giữ nguyên toàn bộ gate.
- PROJECT/PROJECT_PROGRESS.md — trạng thái, blocker, bước tiếp theo, lịch sử phiên.
- PROJECT/CAPABILITY_REGISTRY.md — trạng thái thành viên T-12.
- PROJECT/REVIEW_BUDGET_LEDGER.md — chưa tiêu budget, giữ pool.
- PROJECT/LO_TRINH_DE_HIEU.md — chỉ do generator nếu nội dung dẫn xuất đổi.

Không xoá file. Không nội dung data/ nào được đọc hay commit.

## 26. Validators

Đã chạy; mọi lệnh dưới đây exit 0. Không sửa validator.

| Validator | Kết quả thực thi | Phạm vi / giới hạn |
|---|---|---|
| structure | PASS | 27 required paths |
| project_state | PASS | Đọc profile + progress hiện tại |
| governance | PASS | 7 CORE, 7 PROJECT, 2 adapter, 5 hard-stop, 26 invariant, 3 lineage, 43 hardening, 23 task |
| routing | PASS | 20 MAJOR, 0 manual override |
| sync_easy_roadmap | PASS | Generator chạy; nội dung file không đổi vì READY/BLOCKED cùng tick vàng |
| easy_roadmap | PASS | Khớp trạng thái canonical sau generator |
| evidence | In PASS, quét 0 record | **KHÔNG nhận là PASS có ý nghĩa** — H-08 có sẵn |
| task_completion | In PASS, quét 0 DONE | **KHÔNG nhận là PASS có ý nghĩa** — H-08 có sẵn |
| branch_authority trước commit | PASS | Fetch thành công ngoài sandbox; đúng nhánh, behind 0, ahead 0, production EMPTY |

Branch check dùng `--allow-production-diff --base 91cfbba5e3af01d432c64369bb5a286f6461ab6a`.
Tracked worktree trước commit DIRTY chỉ do đúng tài liệu đã ghi ở §25; không ghi CLEAN giả.
Ban đầu trước đọc state tracked worktree CLEAN. `git diff --check` PASS.

Kiểm trực tiếp bổ sung (không thay thế hay sửa validator): 14/14 block Completion Gate và toàn
bộ phần task sau tiêu đề Completion Gate trùng tuyệt đối với source HEAD; 14 trạng thái vẫn
NOT_TESTED; báo cáo có 29 mục và 14 yêu cầu nguyên văn. Số học §3 chạy lại PASS cho chẩn đoán.

Đo diff ở cả hai mốc §24: **EMPTY**, 0 production file, +0/−0. Diff trên docs/spec/, docs/spec-l1/,
tests/, firestore.rules, firebase.json cũng EMPTY. Không chạy full regression (xem §20).
Task-registry trước/sau: SET A = 30/30 roadmap ID; SET B = 23/23 task file, không ID mới.
`new_registered_task_ids = 0`; không file proposal mới (đề xuất nằm trong báo cáo này);
`owner_assignment_required_entries_added = 0`. Không làm tròn lại/đóng băng SC fixture.

## 27. Lifecycle State

T-12 **BLOCKED — OWNER_DECISION_REQUIRED**. Đi từ READY lịch sử tới BLOCKED trong DISCOVER; không đi qua IN_PROGRESS/IMPLEMENTED/DONE. Bản 17/17 lịch sử và nguyên văn 14 REQUIRED check được bảo toàn. Không tuyên bố hoàn tất capability.

## 28. Independent E2 Required

E2 vẫn bắt buộc, **chưa thực hiện**, không tự chứng nhận. Chưa sẵn sàng bàn giao E2 vì implementation/E1 chưa tồn tại. Reviewer sau này phải phủ CHECK-T12-02/03/04/05/06/09/10/11/12 và đủ tám điểm dò trong task. E2 không phải blocker duy nhất hiện tại.

## 29. Exact Next Action

**Owner quyết định đề xuất dưới đây trước khi tiếp tục implementation của chính T-12.** Chưa có quyết định mới được tạo/ghi thay Owner.

### COMPLETION GATE CHANGE PROPOSAL — CHƯA DUYỆT

**Original check:** CHECK-T12-08 bắt buộc 12/12 SC khớp tuyệt đối spec §19; SC-04 currently ghi `remainingPlannedBudget(2026-02) = 7.090.822`. CHECK-T12-06 và S-A10 yêu cầu đúng quy tắc tháng/carry của §11.4.

**Proposed change:** giữ DEC-042/CAPPED_CARRY và mọi input SC-01…SC-04, giữ nguyên phép tính WAC và planInvested tháng 2; sửa đúng kỳ vọng remaining tháng 2 của SC-04 thành **11.775.522 VND**, bổ sung tường minh `carryInVnd = 4.684.700` và `plannedBudgetVnd = 24.684.700`. Không hạ tolerance=0, không xoá check/INV, không đổi ngân sách task.

**Reason:** tính lại đúng công thức đã duyệt; bảng và script §3 cho bằng chứng tái lập.

**Risk:** nếu tự bỏ carry để khớp SC-04, sản phẩm làm mất 4.684.700 VND ngân sách chuyển tiếp. Nếu tự sửa fixture thành 11.775.522 mà Owner chưa duyệt, implementation vi phạm golden contract frozen.

**Impact:** cần Owner cho phép chỉnh spec §19 SC-04 và tham chiếu oracle của CHECK-T12-08. Không cần kiến trúc mới, Firebase/auth, task ID hay repair cycle. Golden fixture commit chưa tồn tại nên chưa có baseline phải sửa lại.

**Required decision:** duyệt hoặc bác đề xuất sửa oracle ở trên. Nếu bác, Owner cần chỉ rõ cách giải quyết để SC-04 và §11.4 đồng thời có hợp đồng thực thi; implementer không tự chọn FORFEIT hoặc đổi input.

Sau quyết định: áp dụng đúng amendment được duyệt, tái xác nhận Ready Gate 17/17, chạy branch authority rồi mới READY → IN_PROGRESS. Tiếp tục loop implementation/E1/E2 đã frozen; không tự mở việc phụ.
