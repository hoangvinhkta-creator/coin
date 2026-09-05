# T-12 Implementation Report

**Hiện hành sau DEC-044:** carry SC-04 đã sửa đúng 11.775.522 VND; một lượt preflight đủ 12 SC
phát hiện hai nhóm CONTRACT_CONFLICT khác. T-12 vẫn BLOCKED, chưa implementation.
Xem phần **Bổ sung S034 — DEC-044 và lượt golden consistency preflight duy nhất** cuối báo cáo.
Phần 1–29 dưới đây giữ bản ghi lịch sử của lượt S034 trước DEC-044.

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

## Bổ sung S034 — DEC-044 và lượt golden consistency preflight duy nhất (2026-09-05)

**Kết quả hiện hành: OWNER_DECISION_REQUIRED.** Đã canonicalize sửa carry SC-04 theo DEC-044.
Một lượt preflight đã đối chiếu đủ 12 SC với DEC-042, spec, 15 INV và 14 CHECK:
**9 CONSISTENT / 3 CONTRACT_CONFLICT**, gom thành **hai nhóm** bên dưới. T-12 giữ BLOCKED.
Không implementation, không fixture run, không thí nghiệm mới, không Completion Gate evidence.
Không tạo fixture hay freeze baseline, không tiêu repair cycle.

### 1. Phạm vi / checkpoint / quyết định đã áp dụng

Source HEAD: `2642c8e9908d63e8bb1f266432d67be073e51c20`.
Nhánh: `codex/t12-l1-ledger-impl`. Base implementation Owner chỉ định giữ nguyên
`7d1985aaf306294df49c9508078d5425da10f47e`; mốc đo task vẫn `91cfbba5e3af01d432c64369bb5a286f6461ab6a`.
Branch Authority chạy trước state: PASS, tracked CLEAN, behind upstream 0, ahead 1;
fetch trong sandbox lúc mở lượt báo STALE_REMOTE. Kiểm tra có mạng được ghi ở mục validator cuối.

DEC kế tiếp đã kiểm tra từ canonical log là **DEC-044**. Quyết định chỉ sửa oracle carry SC-04:
carryInVnd = 4.684.700, plannedBudgetVnd = 24.684.700,
remainingPlannedBudgetVnd = **11.775.522**. Giữ nguyên input/WAC/planInvested tháng 2 = 12.909.178.
Không áp dụng min/cap của ví dụ tháng 1 thành luật carryOut mới; công thức tổng quát §11.4 giữ nguyên.
Không sửa SC khác hoặc 14 block Completion Gate. §29 của báo cáo S034 ban đầu ở trên nay
**đã được Owner duyệt và áp dụng**, không còn là yêu cầu chờ quyết định.

### 2. SC preflight — mỗi SC đúng một phân loại

Đây là phân loại tính nhất quán của hợp đồng, không phải PASS/FAIL của test.
Các số có dấu `~` trong spec được đọc đúng là giá trị xấp xỉ để diễn giải; không biến chúng
thành oracle số thực exact, cũng không áp tolerance mới. Khi số nguyên được ghi tường minh,
phép đối chiếu giữ tuyệt đối.

| SC | Phân loại | Đối chiếu bounded |
|---|---|---|
| SC-01 | CONSISTENT | 1.200/0,5 = 2.400 USDT/ETH; 30.000.000/0,5 = 60.000.000 VND/ETH; 5.000.000/200 = 25.000; opening không vào invested. INV-1/7; CHECK-01/03 |
| SC-02 | CONSISTENT | Pool 1.200 USDT / 30.600.000 VND = 25.500; P2P không vào invested/holdings ETH. INV-3/8; CHECK-03 |
| SC-03 | CONSISTENT | 600,6 × 25.500 = 15.315.300 nguyên; pool 599,4 / 15.284.700 vẫn chính xác 25.500; ETH 0,75 / 1.800,6 / 45.315.300; remaining 4.684.700. INV-3/5; CHECK-03 |
| SC-04 | CONTRACT_CONFLICT | Oracle carry **đã đúng** theo DEC-044. Các số WAC nguyên cũng đúng; nhưng chúng không thể đồng thời thoả mệnh đề bình quân không đổi của CHECK-T12-03. Nhóm A bên dưới |
| SC-05 | CONSISTENT | Đổi riêng qty 0,25→0,24: qty tổng 0,94; costUsdt 2.300,6/costVnd 58.224.478 giữ nguyên; avg 2.447,446808…/61.940.934,04255…; id/seq giữ. INV-1/2/15; CHECK-05. Không tạo xung đột độc lập ngoài nhóm A ở bước replay SC-04 dùng chung |
| SC-06 | CONSISTENT | Bỏ P2P tháng 2: relief 12.750.000; ETH cost 58.065.300; USDT 99,4/cost 2.534.700; snapshot theo tiền đề. INV-3/14; CHECK-03/05 |
| SC-07 | CONSISTENT | Replay 03/02→04/02→05/02; relief lần nhập muộn 2.581.836, lần tiếp 12.909.178; invested tháng 2 = 15.491.014; createdAt không ảnh hưởng. INV-2/6/15; CHECK-02/05. Kết luận về thứ tự không tạo xung đột độc lập ngoài nhóm A |
| SC-08 | CONSISTENT | 28/02 18:30 UTC = 01/03 01:30 Asia/Ho_Chi_Minh; tháng 2 đã đóng, event 01/03 vào tháng 3. INV-2/6; CHECK-02/06 |
| SC-09 | CONTRACT_CONFLICT | Split [6.666.667,6.666.667,6.666.666], invested 17 triệu, plan 12 triệu, remaining/nextAmount 8 triệu đều đúng. carryOut tháng 3 = 8 triệu không thể là số đã chốt tại asOfDate 18/03. Nhóm B |
| SC-10 | CONTRACT_CONFLICT | Reserve 6 triệu, invested 21 triệu, plan 12 triệu, remaining 8 triệu đúng. carryOut tháng 3 = 8 triệu không thể là số đã chốt tại asOfDate 21/03. Cùng nhóm B, không tách thành quyết định thứ ba |
| SC-11 | CONSISTENT | 03/04 nằm sau 15/03; holdings có event, tháng 3 không nhận invested của tháng 4, không carryOut tháng 3, có FUTURE_DATED_EVENTS. INV-6; CHECK-06 |
| SC-12 | CONSISTENT | 300/2.400 = 0,125 ETH; theo tiền đề explicit qty không âm, chỉ VND basis thiếu: W-1 + UNKNOWN, giữ qty/costUsdt. Điều kiện M-1 xác nhận ngày và M-2 không âm vẫn áp dụng, không được suy ngày từ ts hay bịa opening quantity để vượt gate. INV-11/12/14; CHECK-04/10/11 |

Không dùng SC-09/10 như phần nối của ngân sách tháng 1–2: SC-09 tự ghi rõ carryIn=0, nên không
có xung đột carryIn với chuỗi SC-01…08. Không kết luận thiếu input chi tiết cho SC-08/09/10/12
là xung đột: chúng cho phép dựng synthetic input thoả đúng các tiền đề, không cần Owner data.

### 3. Nhóm A — bình quân bất biến chính xác không tương thích số nguyên SC-04

Neo: spec §6.3/§6.5/§7.3/§8.3; CHECK-T12-03 nguyên văn:

> giải phóng theo bình quân **không** làm đổi bình quân

Với chính các số SC-04 (không thêm event giả):

    trước BUY:  Q = 1.099,4 USDT; C = 28.384.700 VND
    relief = ROUND_HALF_UP(500 × C / Q) = 12.909.178 VND
    sau BUY:    Q' = 599,4 USDT; C' = 15.475.522 VND

    avg_before = 141923500 / 5497 VND/USDT
    avg_after  = 77377610 / 2997 VND/USDT
    avg_after − avg_before = -7330 / 16474509 VND/USDT ≠ 0

Đối chiếu hoàn toàn bằng số nguyên, tránh mọi tranh cãi về sai số float:

    15.475.522 × 10.994 = 170.137.888.868
    28.384.700 ×  5.994 = 170.137.891.800
    hai tích chéo KHÔNG bằng nhau (lệch 2.932)

Đây là hệ quả làm tròn VND ở chính oracle canonical, **không phải lỗi WAC của implementation**.
Mệnh đề giữ bình quân đúng trước làm tròn; sau ROUND_VND, lượng cost còn lại chia cho lượng USDT
còn lại lệch một phân số rất nhỏ. Không thể vừa giữ các số nguyên đúng, vừa bảo toàn ratio exact.
Không được tự giữ avg cũ làm một trạng thái nguồn khác; không được dùng tolerance để che lệch.

**Đề xuất chờ Owner:** giữ nguyên tuyệt đối mọi số nguyên/WAC/oracle SC-04, DEC-042, INV-3,
INV-5 và tolerance=0; làm rõ câu invariant bình quân trong CHECK-T12-03/đoạn spec liên quan là
bất biến của phép giải phóng **trước làm tròn**, còn tỷ lệ sau event được dẫn xuất đúng từ
`(C − ROUND_VND(out × C / Q)) / (Q − out)`; sai khác chỉ được là hệ quả tất định của ROUND_VND.
Đối chiếu relief/cost/qty vẫn exact, không thêm epsilon và không cất avg riêng. Chưa áp dụng.

### 4. Nhóm B — SC-09/SC-10 gán carryOut cho tháng đang mở

Neo: spec §10.6, §11.4, CHECK-T12-06 (*carryOut chỉ chốt cho tháng đã đóng*), đối chứng SC-11.

| asOfDate được chỉ định | currentMonth | 2026-03 đã đóng? | carryOut tháng 3 đã chốt |
|---|---|---|---|
| 2026-03-18 (SC-09) | 2026-03 | không | không được sinh |
| 2026-03-21 (SC-10) | 2026-03 | không | không được sinh |
| 2026-04-01 (minh hoạ thời điểm hợp lệ) | 2026-04 | có | 8.000.000 nếu giữ cùng events |

**Đã xét cách diễn giải canonical asOfDate.** 8.000.000 là con số đúng **khi tháng đã đóng**.
Tuy nhiên SC-09/10 đặt asOfDate trong tháng 3 và đưa carryOut=8.000.000 vào cùng khối EXPECT,
không khai một lượt đánh giá thứ hai ở tháng 4, không gắn nhãn dự phóng. Đổi timezone không làm
18/03 hoặc 21/03 thành tháng đã đóng. Đọc carryOut như remaining/projection là đổi nghĩa đã
được §11.4/CHECK-06 khoá; tự thêm một asOfDate tháng 4 để coi oracle hiện tại PASS sẽ ngầm sửa
contract thời gian của scenario. Vì chỉ thị Owner cấm tự sửa SC khác, phân loại cả hai là
CONTRACT_CONFLICT cho **kỳ vọng cùng lần đánh giá như đang viết**, không bác số 8.000.000.

**Đề xuất chờ Owner, một tu chỉnh chung cho cả hai SC:** tại asOfDate 18/03 và 21/03, ghi rõ
carryOut tháng 3 **chưa chốt**; thêm bước đánh giá tường minh cùng ledger với asOfDate=2026-04-01,
không thêm event, lúc đó carryOut tháng 3/carryIn tháng 4 = 8.000.000. Giữ nguyên input giao dịch,
ngân sách, reserve/extra isolation và mọi số còn lại. Không cần chức năng projection mới.
Không thay CHECK-T12-06, không nới tolerance. Chưa áp dụng.

### 5. Đối chiếu toàn bộ INV / CHECK trong đúng preflight

| Bề mặt | Kết luận preflight (không phải evidence kiểm thử) |
|---|---|
| INV-1/2/5/6/7/15 | Schema/nguồn truth, integer, ngày và identity không đòi đổi input SC. Nhóm A phải được giải quyết mà không lưu avg riêng hay float tiền |
| INV-3/4/8 | Các pool số lượng SC01…07 không âm; opening/P2P/buy giữ bảo toàn số nguyên; P2P không vào đầu tư. Chưa thử mutation hay edge case ngoài SC |
| INV-9/10/13 | Phép cộng/split của SC09/10 đúng; sự tách nguồn đúng. Nhóm B chỉ liên quan thời điểm chốt carry |
| INV-11/12/14 | SC12 được đọc đúng tiền đề quantity consistent và yêu cầu snapshot/no-write; UNKNOWN không bị 0. Không chạy migration/snapshot để chứng minh |
| CHECK-01/02/04/05/07/09/10/11/12/13/14 | Không thấy mâu thuẫn độc lập nào khác trong 12 SC được xét; các yêu cầu runtime/mutation/persistence/regression vẫn NOT_TESTED |
| CHECK-03/08 | Nhóm A: cùng oracle số nguyên SC04 và mệnh đề avg bất biến exact không đồng thời thoả |
| CHECK-06/08 | Nhóm B: thời điểm EXPECT carryOut trong SC09/10 không đồng thời thoả |

Đây là **một batch cuối cùng trong phạm vi chỉ thị**, không tiếp tục tìm edge case mới,
không làm thử implementation để dò thêm. Không chứng nhận gate từ việc chỉ đọc contract.

### 6. Phép tính tái lập đã chạy

Một lần Python 3.9.6 dùng fractions.Fraction cho WAC/carry/split, datetime + ZoneInfo cho SC08;
đọc spec/task để đếm 12 SC, 15 INV và 14 CHECK. Exit 0. Đầu ra chính:

    SC03: relieved=15315300; pool=2997/5,15284700; remaining=4684700
    SC04: relieved=12909178; costETH=58224478; costUSDT=15475522;
          carryIn=4684700; plannedBudget=24684700; remaining=11775522
    SC04 avg_after-avg_before = -7330/16474509; equal=False
    SC05 avgUsdt=2447.446808510638; avgVnd=61940934.042553194
    SC06: relief=12750000; costETH=58065300; pool=497/5,2534700
    SC07: lateRelief=2581836; followingRelief=12909178; investedFeb=15491014
    SC08: 2026-03-01T01:30:00+07:00
    SC09: split=[6666667,6666667,6666666]; invested=17000000; plan=12000000
    SC10: reserve=6000000; invested=21000000; plan=12000000
    2026-03-18 / 2026-03-21: March closed=False
    2026-04-01: March closed=True; carryOut=8000000
    SC11: future=True; March closed=False
    SC12: 300/2400=1/8; VND basis UNKNOWN theo tiền đề

Phép tính độc lập ngắn để tái lập **hai nhóm**, không là fixture/test implementation:

```python
from fractions import Fraction as F
C, Q, out = 28_384_700, F(10994, 10), 500
x = out*C/Q
relief = (2*x.numerator+x.denominator)//(2*x.denominator)
print(relief, F(C-relief)/(Q-out)-F(C)/Q)
for as_of in ('2026-03-18','2026-03-21','2026-04-01'):
    print(as_of, '2026-03' < as_of[:7])
```

### 7. Ready / budget / triển khai / yêu cầu Owner gộp

Điều kiện §4 của chỉ thị mới chưa đạt (còn CONTRACT_CONFLICT), nên **không** tái xác nhận READY
17/17, không chuyển BLOCKED → READY → IN_PROGRESS. Không bịa READY_GATE_PASS hay đếm test đỏ.
T-12 giữ BLOCKED — OWNER_DECISION_REQUIRED; 14 REQUIRED check vẫn NOT_TESTED.
SC04 carry đã đóng bằng DEC-044; không xin Owner duyệt lại việc đó.

**Một yêu cầu Owner duy nhất:** duyệt/bác **cả nhóm A và nhóm B** ở mục 3–4 như một batch
contract-consistency clarification trước implementation. Quyết định này chưa được cấp;
DEC-044 chỉ cho phép sửa carry SC04. Không cấp DEC mới thay Owner cho hai nhóm còn lại.

REPAIR_CYCLE_1=NOT_CONSUMED; CAP-WEBAPP 2/0/2; production +0/−0; không fixture/baseline,
không Firebase/auth/Hosting/research/data thay đổi. Chưa có E2; preflight không phải E2 hay
Completion Gate evidence. Không chạy npm test/pytest vì chưa implementation; không skip test.

### 8. Validators / bảo toàn hợp đồng / giao nhận

Đã chạy, exit 0: structure PASS (27 paths), project_state PASS, governance PASS (7 CORE,
7 PROJECT, 2 adapter, 5 hard-stop, 26 invariant, 3 lineage, 43 hardening, 23 task), routing PASS
(20 MAJOR/0 override), sync_easy_roadmap PASS (không diff), easy_roadmap PASS.
Evidence/task_completion in PASS nhưng quét 0 record vì H-08 có sẵn; **không** tính là
PASS có ý nghĩa và không sửa validator ngoài scope.

Kiểm bảo toàn tài liệu đã thực thi: 11/11 SC khác trùng source HEAD, input SC-04 trùng,
14/14 block Completion Gate (và phần task sau gate) trùng, PROJECT_DECISIONS chỉ append.
Đây là kiểm diff tài liệu, không phải lượt preflight thứ hai. `git diff --check` PASS.
Task registry trước/sau giữ SET A=30, SET B=23, ID mới=0, proposal file mới=0,
owner_assignment_required mới=0. Đề xuất Owner dùng chính báo cáo hiện có.

Branch Authority trước commit với fetch ngoài sandbox: PASS, đúng nhánh, behind=0, ahead=1,
không INTEGRATION_DECISION_REQUIRED. Tracked DIRTY chỉ đúng 8 tệp tài liệu của lượt này.
Production diff từ T12_MEASURE_BASE_SHA đến working tree: 0 file, +0/−0.
Không thay src/, webapp/, tests/, docs/spec/, Firebase/auth/Hosting hoặc pyproject.*.

Tệp đổi trong lượt này: PROJECT_DECISIONS, PROJECT_PROGRESS, CAPABILITY_REGISTRY,
REVIEW_BUDGET_LEDGER, spec L-1 (chỉ SC04+ghi chú authority), task T-12 (chỉ metadata),
báo cáo T12 và session S034 hiện có. Không tạo artifact/file mới, không đọc data/.
Commit/push chỉ nhánh codex/t12-l1-ledger-impl theo quyền đã có; commit tài liệu không phải
T12_GOLDEN_ACCOUNTING_BASELINE freeze point.
