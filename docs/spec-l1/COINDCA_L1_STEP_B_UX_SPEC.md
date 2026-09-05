# CoinDCA L-1 — STEP B: Product/UX Spec (Dashboard hằng ngày + Nhập giao dịch/Lịch sử)

Status:
CANONICAL — APPROVED (`DEC-047`)

Phase:
CoinDCA L-1 — bước **B** (biến sổ đúng thành công cụ dùng được hằng ngày) của chuỗi A → B → C → D
(`docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` §24)

Nguồn thẩm quyền tài chính (KHÔNG lặp lại, chỉ tham chiếu):
`docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md` (`CANONICAL — APPROVED`, `DEC-042`) —
đặc biệt §5 (schema), §9 (`derive()`), §11 (Plan/Carry), §12 (Reserve), §15 (Edit/Delete), §16
(Dashboard Contract), §17 (Migration), §18 (Firebase readiness), §19–20 (Golden/Invariant).

Task định nghĩa việc thi hành:
`docs/tasks/T-13-buoc-b-dashboard-giao-dich-lich-su.md`

## Nguyên tắc bất di dịch của tài liệu này

1. Tài liệu này là **hợp đồng SẢN PHẨM/UX**. Nó KHÔNG định nghĩa lại bất kỳ công thức tài chính
   nào. Mọi con số hiển thị PHẢI đến từ `CoinLedger.derive(openingPosition, plan, events,
   asOfDate)` (`webapp/ledger.js`, T-12) — không tính lại, không xấp xỉ, không cache một bản sao.
2. Mọi hành động ghi dữ liệu PHẢI đi qua `CoinLedger.update()` / `migrate()` / `destructive()` —
   không viết trực tiếp vào state, không có "sổ cái thứ hai".
3. Không dòng nào của tài liệu này được phép mâu thuẫn với `INV-1`…`INV-15` hay các quyết định
   `DEC-042` (OD-L1-1…4). Nếu một yêu cầu UX ở đây trông như đòi một hành vi tài chính mới —
   đó là lỗi soạn thảo, không phải một thay đổi ngầm được phép.
4. SELL / realized P&L: **KHÔNG xuất hiện** trong bất kỳ đường UI nào của Step B (xem §11 Out of
   Scope). `H-46`/`F-E2-03` chưa có Owner Decision xử lý.

---

## 1. Purpose

Biến sự thật tài chính canonical đã có (`T-12` DONE) thành một công cụ **dùng được hằng ngày**
mà chủ dự án hiểu và thao tác được **không cần biết cấu trúc kỹ thuật bên dưới** (schema
`coindca.ledger/2`, hàm `derive()`, các trường JSON). Step B là lớp trình bày + lớp nhập liệu —
KHÔNG phải một bộ máy kế toán thứ hai.

---

## 2. User outcomes

Sau Step B, chủ dự án mở app và trong vài giây trả lời được:

| # | Câu hỏi | Trả lời bằng |
|---|---|---|
| 1 | "Tôi đang có gì?" | Khối dưới của Tổng quan: `holdings.ETH.qty`, `avgCostUsdt`, `avgCostVnd` (hoặc `—`), định giá nếu có `priceMark` hợp lệ; USDT hiện có; VND hiện có |
| 2 | "Tháng này đã mua bao nhiêu?" | `investedThisMonthVnd` (khối chính #2), tách được PLAN/EXTRA/RESERVE |
| 3 | "Còn được mua bao nhiêu?" | `remainingPlannedBudgetVnd` (khối chính #3) |
| 4 | "Khi nào nên thực hiện lần mua kế hoạch tiếp theo?" | `nextPlannedDate` + `nextPlannedAmountVnd` (khối chính #5 — MỘT hành động, không phải khuyến nghị) |
| 5 | "Khoản nào là DCA, EXTRA, RESERVE?" | Nhãn `source` hiển thị tường minh trên mọi dòng giao dịch liên quan tới `TRADE`, phụ đề #2 tách ba loại khi khác nhau |
| 6 | "Có dữ liệu nào chưa đủ để tin số giá vốn không?" | Banner `UNKNOWN_VND_BASIS` thường trực (§9 dưới đây) + `—` tại đúng chỗ giá vốn bị ảnh hưởng |

Không có outcome nào của Step B liên quan tới "nên mua hay nên đợi" — đó là phạm vi bị cấm
(`DEC-041` B).

---

## 3. Navigation (Information Architecture)

### 3.1 Cấu trúc được chọn — 4 điểm đến

Ví dụ 5 điểm đến trong chỉ thị Owner (Tổng quan/Giao dịch/Kế hoạch/Tài sản-Số dư/Cài đặt) **không
được chấp nhận nguyên trạng**. Lý do: "Giao dịch" và "Tài sản/Số dư" mỗi cái đều chỉ hiển thị lại
một phần dữ liệu mà "Tổng quan" và "Lịch sử" đã phủ — tách thêm điểm đến chỉ tạo thêm điều hướng
mà không thêm khả năng, ngược nguyên tắc §9 "clear > dense, daily usefulness > feature count" của
chỉ thị.

Cấu trúc chọn — **4 điểm đến** cố định (bottom nav trên di động):

| # | Điểm đến | Nội dung |
|---|---|---|
| 1 | **Tổng quan** | Dashboard Contract §16 đầy đủ (khối chính 4+1, khối dưới, banner). Nút hành động chính "+ Ghi giao dịch" nổi bật ở đây |
| 2 | **Lịch sử** | Danh sách toàn bộ event (đã thay `#l1History` dạng `<p>` phẳng bằng bảng/thẻ có filter), tap để mở chi tiết/sửa/xoá. Cũng có nút "+ Ghi giao dịch" |
| 3 | **Kế hoạch** | `monthlyBudgetVnd`, `scheduleDays`, lịch sử carry theo tháng đã đóng, Số dư đầu kỳ (`openingPosition`, sửa một chỗ duy nhất theo §14.3) |
| 4 | **Cài đặt** | Trạng thái persistence/banner đồng bộ, export/import JSON, wipe (kèm cảnh báo + snapshot bắt buộc), xác nhận migration nếu còn state legacy, thông tin phiên bản |

**"+ Ghi giao dịch"** là một hành động toàn cục (nút nổi/sheet), KHÔNG phải điểm đến riêng — mở
màn hình chọn loại sự kiện (§5) dưới dạng modal/bottom-sheet, đóng lại quay về đúng màn hình đang
đứng. Điều này giữ đúng nguyên tắc "hành động phổ biến nhất cần rất ít lần chạm" (§10) mà không
sinh thêm một tab chỉ để chứa một form.

### 3.2 Vì sao không tách "Tài sản/Số dư" riêng

`holdings`, `avgCostUsdt`, `avgCostVnd`, USDT/VND hiện có đã nằm trong khối dưới của Tổng quan
(§16.2 spec). Một màn hình thứ hai lặp lại đúng các con số đó chỉ để đổi cách trình bày không
phải nhu cầu hằng ngày đã nêu ở §2 chỉ thị — vi phạm nguyên tắc "simple > comprehensive". Nếu về
sau nhu cầu thật xuất hiện (ví dụ: biểu đồ phân bổ nhiều tài sản), đó là việc của Step ngoài phạm
vi này (đa tài sản `D-4`/`D-7` của spec §23 vẫn Deferred).

### 3.3 Route mapping (tuân `02_ROUTING_RULES.md`)

App là single-page (không có backend route) nên "route" ở đây là **client-side view state**, ghi
lại được (URL hash hoặc tương đương) để refresh không mất ngữ cảnh:

    #/dashboard   (mặc định)
    #/history
    #/history/:eventId        (chi tiết/sửa)
    #/plan
    #/settings

Đây là governance tối thiểu cho một SPA cá nhân — không cần auth guard (một chủ sở hữu, đã có ở
Firebase Anonymous Auth từ T-09B), không cần phân quyền.

---

## 4. Dashboard (Tổng quan)

Nội dung là **chính xác** Dashboard Contract §16 của spec kế toán — Step B không thêm, không bớt
đại lượng, chỉ định hình cách trình bày:

### 4.1 Khối chính (trên cùng, luôn hiện không cuộn)

| # | Thẻ | Nguồn | Trình bày |
|---|---|---|---|
| 1 | Ngân sách tháng | `plannedBudgetVnd` | số lớn; phụ đề "gồm `carryInVnd` chuyển từ tháng trước" khi `carryInVnd > 0` |
| 2 | Đã đầu tư tháng này | `investedThisMonthVnd` | số lớn; phụ đề "kế hoạch `planInvestedVnd` · thêm `EXTRA` · dự phòng `RESERVE`" khi ≠ `planInvestedVnd` |
| 3 | Còn lại theo kế hoạch | `remainingPlannedBudgetVnd` | số lớn, thanh tiến trình trực quan (đã tiêu / còn lại) — thanh này chỉ là hiển thị, không phải nguồn tính |
| 4 | Số dư dự phòng | `reserveBalanceVnd` | số lớn |
| 5 | **Mua kế tiếp** | `nextPlannedDate` + `nextPlannedAmountVnd` | thẻ nổi bật riêng, có nút tắt "Ghi đã mua" mở thẳng form BUY-PLAN (§5) điền sẵn `nextPlannedAmountVnd` làm gợi ý số tiền — người dùng vẫn sửa được, KHÔNG tự động ghi |

Cấm tuyệt đối trên thẻ #5: nhãn "GO"/"WAIT", màu đỏ/xanh theo tín hiệu, badge "cơ hội" — bất kỳ
điều gì gợi ý đây là khuyến nghị thay vì lịch của chính người dùng (`DEC-041` B).

### 4.2 Khối dưới (cuộn xuống)

| Nhãn | Nguồn | Trình bày khi UNKNOWN |
|---|---|---|
| Đang nắm giữ (ETH) | `holdings.ETH.qty` | luôn hiện — số lượng không bao giờ UNKNOWN |
| Giá vốn TB (USDT) | `avgCostUsdt` | luôn hiện |
| Giá vốn TB (VND) | `avgCostVnd` | `—` khi UNKNOWN, có icon/tooltip giải thích ngắn "thiếu tỷ giá gốc — sửa ở Kế hoạch → Số dư đầu kỳ" |
| Định giá hiện tại | chỉ khi `priceMark` hợp lệ (§16.3 spec: `businessDate ≥ asOfDate − 1 ngày`) | `—` + "giá gần nhất: N ngày trước" khi không hợp lệ; KHÔNG ngoại suy |
| USDT hiện có | `usdt.qty` | luôn hiện |
| VND hiện có | `vnd.qty` (nếu spec theo dõi) | luôn hiện |

### 4.3 Banner bắt buộc (không dismiss được)

`LEDGER_INCONSISTENT`, `FUTURE_DATED_EVENTS`, `UNKNOWN_VND_BASIS`, trạng thái persistence chưa
xác nhận (đã có sẵn cơ chế ở `app_logic.js` — REUSE). Banner nằm trên cùng, phía trên khối chính,
không có nút "x" ẩn vĩnh viễn — nhiều nhất là thu gọn tạm thời trong phiên hiện tại, KHÔNG lưu
trạng thái "đã đọc" xuống persistence.

---

## 5. Nhập giao dịch (Transaction Entry)

Một sheet/modal "+ Ghi giao dịch" dùng chung cho mọi luồng, bước 1 luôn là **chọn loại**:

| Loại hiển thị | Ánh xạ vào `update()` action | Trường tối thiểu bắt buộc |
|---|---|---|
| Số dư đầu kỳ | `action.type = 'opening'` | `asOf`, tối thiểu một trong {ETH `qty`, USDT `qty`, VND `qty`}; `costUsdt`/`costVnd` tuỳ chọn (thiếu → `null`, KHÔNG phải 0) |
| Đổi VND → USDT (P2P) | `event.kind='TREASURY', dir='VND_TO_USDT'` | `businessDate`, `vndAmount`, `usdtAmount` |
| Đổi USDT → VND (P2P) | `event.kind='TREASURY', dir='USDT_TO_VND'` | `businessDate`, `vndAmount`, `usdtAmount` |
| Mua ETH — Kế hoạch | `event.kind='TRADE', side='BUY', source='PLAN'` | `businessDate`, `usdtNotional`, `feeUsdt` (mặc định 0), `qty` |
| Mua ETH — Ngoài kế hoạch | `event.kind='TRADE', side='BUY', source='EXTRA'` | như trên |
| Nạp dự phòng | `event.kind='RESERVE', type='CONTRIBUTE'` | `businessDate`, `vndAmount` |
| Mua ETH — Từ dự phòng | `event.kind='TRADE', side='BUY', source='RESERVE'` | như PLAN/EXTRA **+ `note` bắt buộc** (validate ngay tại form, không đợi `ledger.js` từ chối) |
| Rút dự phòng (không mua) | `event.kind='RESERVE', type='WITHDRAW'` | `businessDate`, `vndAmount` |
| Giá tham chiếu | `event.kind='PRICE'` | `businessDate`, `priceUsdt`; `usdVndRate` tuỳ chọn — **chỉ hiển thị nếu người dùng cần xem định giá hiện tại** (§4.2); KHÔNG bắt buộc nhập hằng ngày |

Nguyên tắc form:

- Mỗi trường có gợi ý đơn vị (VND / USDT / ETH) ngay trong ô nhập — không để người dùng tự đoán.
- Không có ô nhập tỷ giá riêng theo từng lệnh (`OD-L1-4`) — form **không được** thêm trường này
  dù chỉ để "tiện tính toán nội bộ" rồi bỏ đi.
- `businessDate` mặc định = hôm nay (`clock().today`) nhưng luôn sửa được — đây là nơi DUY NHẤT
  nhập ngày cho giao dịch (không có "ngày tạo" hiển thị cho người dùng).
- Sau khi lưu, quay lại đúng màn hình đã mở sheet (Tổng quan hoặc Lịch sử), có toast xác nhận
  ngắn — KHÔNG tự chuyển màn hình.
- **Không có tuỳ chọn SELL** trong danh sách loại ở trên (§11 Out of Scope).

---

## 6. Lịch sử (History)

Thay thế `#l1History` (danh sách `<p>` phẳng, không kiểu dáng) bằng danh sách có cấu trúc:

- **Mặc định**: sắp theo `(businessDate DESC, seq DESC)`.
- **Mỗi dòng hiển thị**: ngày (`businessDate`), loại (nhãn Việt hoá của `kind`/`source`, ví dụ
  "Mua ETH · Kế hoạch", "Mua ETH · Dự phòng", "P2P VND→USDT", "Nạp dự phòng"), số tiền/số lượng
  chính, badge riêng cho `source ∈ {EXTRA, RESERVE}` (PLAN không cần badge — là mặc định ngầm).
- **Bộ lọc**: theo loại (P2P / Mua-Kế hoạch / Mua-Ngoài kế hoạch / Mua-Dự phòng / Dự phòng-nạp-rút
  / Giá tham chiếu), theo khoảng `businessDate`, theo tháng lịch. Tìm kiếm theo `note`.
- **Chi tiết** (tap vào dòng): hiện đầy đủ trường của event, hai nút **Sửa** / **Xoá**.
- **UNKNOWN**: dòng nào có phần giá vốn VND liên quan bị UNKNOWN được đánh dấu bằng cùng icon
  dùng ở §4.2 — CHỈ đánh dấu "có liên quan tới UNKNOWN", KHÔNG hiển thị `realizedFxVnd` hay bất
  kỳ số nội bộ nào khác (giữ `H-45` không bị kích hoạt thêm — xem §11).
- **Số dư đầu kỳ**: hiện như một dòng đặc biệt "Số dư đầu kỳ" ở đầu danh sách (không lẫn vào dòng
  giao dịch, đúng §14.3 spec — opening không phải một giao dịch), sửa được nhưng KHÔNG xoá được
  từ dòng lịch sử (xoá opening là hành động riêng ở Kế hoạch, có cảnh báo mạnh hơn — §7).

---

## 7. Sửa / Xoá (Edit / Delete)

| Hành động | UX |
|---|---|
| Sửa một giao dịch | Mở lại đúng form đã dùng để tạo nó (kind cố định, không đổi loại giữa chừng — đổi loại nghĩa là xoá + tạo mới, giữ đúng ngữ nghĩa `id`/`seq` của §15.2 spec), sửa xong bấm Lưu → `update()` chạy lại `derive()` toàn bộ, Tổng quan/Lịch sử cập nhật ngay |
| Xoá một giao dịch | Dialog cảnh báo tường minh: "Xoá vĩnh viễn — không thể hoàn tác. Một bản sao đầy đủ sẽ được xuất tự động trước khi xoá." → xác nhận → app tự gọi export snapshot (đã có ở `CoinLedger.destructive()`, INV-14) rồi mới xoá thật (hard delete, không tombstone — §15.3 spec) |
| Sửa/xoá Số dư đầu kỳ | Cảnh báo RIÊNG, mạnh hơn: "Sửa/xoá số dư đầu kỳ có thể khiến phần lớn giá vốn trở thành KHÔNG XÁC ĐỊNH." (đúng cảnh báo §15.3 spec) |
| Nhập muộn | Không có UX đặc biệt — `businessDate` nhỏ hơn hôm nay là hợp lệ, thứ tự `(businessDate, seq)` tự xử lý (§10 spec); chỉ hiện banner `FUTURE_DATED_EVENTS` nếu ngày LỚN hơn hôm nay |

Không có UX "hoàn tác sửa" hay lịch sử phiên bản — spec không có cơ chế đó (§15.2: "Không có phép
hoàn tác tác động cũ nào tồn tại trong mã"). Step B KHÔNG được tự chế một lớp undo phía UI.

---

## 8. Kế hoạch / Carry (Plan UX)

Màn "Kế hoạch":

- **Ngân sách tháng** (`monthlyBudgetVnd`) và **lịch mua** (`scheduleDays`) — sửa được, áp dụng
  từ tháng hiệu lực trở đi (không hồi tố, §11.1 spec — UI phải nói rõ "áp dụng từ tháng X" khi
  người dùng đổi).
- **Carry tháng trước**: hiển thị `carryOut` của tháng đã đóng gần nhất và cách nó cộng vào
  `carryInVnd` tháng này — người dùng **không cần tự cộng trừ gì**, chỉ đọc số đã tính sẵn từ
  `derive()`.
- Ba đại lượng `monthlyBudgetVnd` / `carryInVnd` / `investedThisMonthVnd` (hay `planInvestedVnd`)
  luôn hiển thị **tách riêng**, không gộp (yêu cầu tường minh của Owner, §11.4 spec).
- **Số dư đầu kỳ**: form sửa một chỗ duy nhất (asOf, số lượng/giá vốn từng tài sản, USDT, VND,
  reserve ban đầu) — đúng §14 spec.
- **Migration** (nếu còn state legacy `ethdca.tracker/1`): banner + nút "Xem báo cáo di trú"
  hiển thị kết quả `M-1..M-4` (dừng) hoặc `W-1` (hoàn tất kèm cờ) — REUSE luồng đã có ở
  `ledger_ui.js`, chỉ nâng cấp trình bày.

---

## 9. UNKNOWN UX

Một quy tắc trình bày duy nhất, áp dụng NHẤT QUÁN mọi nơi con số giá vốn VND xuất hiện (Tổng
quan §4.2, Lịch sử §6, Kế hoạch §8):

    UNKNOWN  ->  hiển thị "—" (không phải 0, không phải trống, không phải NaN)
             ->  banner UNKNOWN_VND_BASIS thường trực ở Tổng quan (§4.3), không tự ẩn
             ->  tooltip/ghi chú ngắn trỏ tới nơi sửa (Kế hoạch → Số dư đầu kỳ)

Cấm: mọi hình thức khiến UNKNOWN "biến mất" khỏi tầm nhìn người dùng — kể cả khi số dư USDT tạo
UNKNOWN cạn về 0 (đây là đúng nội dung `H-45`; Step B KHÔNG được vô tình làm banner biến mất theo
— nếu triển khai phát hiện banner tắt trong tình huống này, đó là điều kiện kích hoạt `H-45`,
báo cáo lại thay vì tự vá ngoài scope).

---

## 10. Mobile Workflow

Nguyên tắc: **di động là màn hình chính**, desktop chỉ cần responsive tự nhiên (CSS auto-fit grid
đã có ở `app_shell.html` — REUSE).

- Bottom nav 4 mục cố định (§3.1) — luôn trong tầm ngón cái.
- "+ Ghi giao dịch" là nút nổi (FAB) hoặc nút chính trong thanh dưới — tối đa **2 lần chạm** để
  mở đúng form loại phổ biến nhất (Mua ETH — Kế hoạch) từ Tổng quan: chạm FAB → chạm loại → điền
  → Lưu = tối đa 3 lần chạm tính cả Lưu.
  hoặc dùng thẳng nút tắt "Ghi đã mua" ở thẻ #5 (§4.1): 2 lần chạm (mở form đã điền sẵn số tiền
  gợi ý → Lưu).
- Không bảng dày đặc làm màn hình mặc định — Lịch sử dùng thẻ (card) xếp dọc trên di động, chuyển
  sang bảng khi màn hình đủ rộng (breakpoint hiện có `860px` — REUSE, mở rộng thêm breakpoint hẹp
  hơn nếu cần cho điện thoại nhỏ).
- Form dùng bàn phím số đúng loại (`inputmode="numeric"`) cho mọi trường tiền/số lượng.
- Không thao tác nào bắt buộc phải xoay ngang màn hình hay cuộn ngang.

---

## 11. Out of Scope (Step B)

| # | Không làm | Lý do / neo |
|---|---|---|
| B-1 | Bật nghiệp vụ SELL cho dữ liệu thật, hiển thị realized P&L | `H-46`/`F-E2-03` — khiếm khuyết đặc tả SELL chưa có Owner Decision xử lý. Tuỳ chọn SELL **bị ẩn hoàn toàn** khỏi mọi form/loại giao dịch của Step B (không hiển thị dạng "sắp có") — đơn giản hơn, không ngầm hứa hẹn tính năng, đúng "simple > comprehensive" |
| B-2 | Firebase project riêng, Google Sign-in, đổi `firebase.json`/`firestore.rules`/Hosting | Bước C (`H-42`), §18 spec R-1…R-5 |
| B-3 | Buy Score, Opportunity Score, regime, crash ladder, recommendation engine, gợi ý mua tự động, tab Research, UI chiến lược V2.1.5/V2.2 | `DEC-041` B, `H-43`; §12.3 spec cấm tuyệt đối |
| B-4 | Nhắc lịch / thông báo đẩy | `D-6` spec §23, thuộc `T-08`/`T-10` DEFERRED |
| B-5 | Tax lot (FIFO/LIFO/specific-ID), sổ lãi/lỗ đã thực hiện | `D-5` spec §23 |
| B-6 | Nhiều tài sản ngoài ETH ở UI, lấy giá tự động | `D-4`/`D-7` spec §23 |
| B-7 | Tombstone/audit trail đầy đủ cho xoá, undo sau khi lưu | `D-8` spec §23; §15.3 quyết định hard delete + snapshot là đủ |
| B-8 | Bất kỳ công thức tài chính mới, thay đổi `INV-1`…`INV-15`, thay đổi `derive()`/`update()`/`migrate()`/`destructive()` | Step B chỉ tiêu thụ API đã đóng băng của `T-12` |
| B-9 | Dữ liệu tài chính THẬT của Owner trong repo | `DEC-041` C |
| B-10 | Đổi schema `coindca.ledger/2`, đổi ranh giới persistence `ethdca/state` | thuộc `T-12`/bước C, KHÔNG phải Step B |

---

## 12. Existing UI Classification — REUSE / ADAPT / REMOVE_FROM_L1_PATH / DEFER

Dựa trên kiểm kê thật (`webapp/app_shell.html`, `webapp/app_logic.js`, `webapp/ledger_ui.js`,
`webapp/engine.js`):

| Thành phần | File / vùng | Phân loại | Ghi chú |
|---|---|---|---|
| Hệ thống CSS (`.card`, `.stat`, `.stats`, `.form`/`.field`, `table`+`.scroller`, `button*`, theme sáng/tối, auto-fit grid) | `app_shell.html` | **REUSE** | Đã hoàn chỉnh, responsive sẵn, chưa dùng hết ở UI hiện tại |
| Export/Import/Wipe JSON | `ledger_ui.js` | **REUSE** | Luồng đã hoạt động đúng, chỉ cần vỏ UI mới |
| Persistence status chip/banner (`app_logic.js` `persist()`, `renderPersistence()`) | `app_logic.js` | **REUSE** | Không phải dead code — đang chạy thật, giữ nguyên logic, chỉ gắn vào layout mới |
| Form nhập 4 loại event + danh sách sửa/xoá phẳng | `ledger_ui.js` `mount()`/`kindFields()` | **ADAPT** | Đúng luồng dữ liệu (hooks `state()/commit()/canWrite()`), cần thiết kế lại thành sheet theo §5 + bảng/thẻ theo §6, thêm validate `note` bắt buộc cho RESERVE ngay tại form |
| Stat grid tổng hợp từ `derive()` | `ledger_ui.js` (`.stat` cards) | **ADAPT** | Là hạt giống đúng của Dashboard §4 — thêm thẻ "Mua kế tiếp" nổi bật, thêm banner bắt buộc, thêm khối dưới |
| `nav.tabs` 5 tab cũ (dash/entry/ladder/history/setup) | `app_shell.html` | **REMOVE_FROM_L1_PATH** | Thay bằng bottom-nav 4 mục §3.1; markup ẩn hiện tại (`hidden=true`) xoá hẳn khỏi đường L-1 thay vì giữ ẩn vĩnh viễn |
| Opportunity Score hero (`#osVal`, `.hero`, `.bigscore`, `.fbar`) + `recompute()`/`renderDash()`/`deriveRegime()` | `app_shell.html`, `app_logic.js` | **REMOVE_FROM_L1_PATH** | Dead code (unreachable sau `return` ở `render()`), khái niệm V2.1.5 cấm ở L-1 (`DEC-041` B) |
| Tab Ladder (`#tab-ladder`, `renderLadder()`, `buildLadder/createLadder/releaseLadder/cancelLadder`) | `app_shell.html`, `app_logic.js` | **REMOVE_FROM_L1_PATH** | Ladder/zone không tồn tại dưới L-1 (`DEC-041` B, §17.2 spec `DROP_LEGACY_ONLY`) |
| Action box GO/WAIT/FUND (`renderAction()`, `#actionBox`) | `app_logic.js`, `app_shell.html` | **REMOVE_FROM_L1_PATH** | Chính là loại "khuyến nghị" bị cấm ở §16.1 spec |
| Engine-parity banner (`checkParity`, banner "Đối chiếu engine") | `app_shell.html`, `app_logic.js`, `engine.js` | **DEFER** | Chỉ có ý nghĩa nếu tab Research được bật lại sau này (`H-43`); không xoá `engine.js` (giữ nguyên file, chỉ gỡ đường dẫn UI dẫn tới nó khỏi L-1) |
| `engine.js` (OSCORE/regime/ladder JS engine) | `engine.js` | **DEFER** (không đụng file) | Ngoài đường tiền L-1 (`INV-10`); giữ nguyên cho khả năng Research tab tương lai, KHÔNG sửa nội dung trong Step B (`O-11` tiền lệ `T-12`) |
| Form "Nhập số liệu" cũ (daily close ETH/BTC/volume, monthly contribution, P2P, confirm buy có slippage) | `app_shell.html` `#tab-entry` | **REMOVE_FROM_L1_PATH** | Thay hoàn toàn bằng sheet §5 — các trường `recPrice`/slippage là khái niệm V2.1.5 `DROP_LEGACY_ONLY` |
| Tiêu đề/subtitle "ETH DCA Tracker ... V2.1.5" | `app_shell.html` | **REMOVE_FROM_L1_PATH** | Đổi cứng thành "CoinDCA" trong markup thay vì chỉ ghi đè lúc runtime (`ledger_ui.js` hiện đang làm việc này bằng JS — nên chuyển về đúng markup tĩnh) |

---

## 13. Daily Workflow (FLOW-1 … FLOW-7)

| Flow | Điểm vào | Input tối thiểu | Kết quả/màn hình | Cảnh báo quan trọng |
|---|---|---|---|---|
| **FLOW-1** — Mở app, hiểu trạng thái | Mở app → Tổng quan (mặc định) | Không cần nhập gì | 4 số + hành động kế tiếp + khối dưới, banner nếu có | Banner UNKNOWN/INCONSISTENT nếu có, không ẩn được |
| **FLOW-2** — Mua USDT P2P → ghi | FAB "+" từ bất kỳ đâu → chọn "Đổi VND→USDT" | `businessDate`, `vndAmount`, `usdtAmount` | Quay lại màn cũ, USDT hiện có tăng ngay | Không có |
| **FLOW-3** — Dùng USDT mua crypto (PLAN/EXTRA/RESERVE) | FAB "+" hoặc nút tắt "Ghi đã mua" ở thẻ #5 | `businessDate`, `usdtNotional`, `feeUsdt`, `qty`, (+`note` nếu RESERVE) | Tổng quan cập nhật `investedThisMonthVnd`/`planInvestedVnd` đúng theo `source` | Nếu RESERVE thiếu `note` → chặn lưu, thông báo tại chỗ |
| **FLOW-4** — Xem tiến độ DCA tháng | Tổng quan hoặc Kế hoạch | Không cần nhập | Ba đại lượng tách riêng (ngân sách/carry/đã đầu tư), thanh tiến trình | Không có |
| **FLOW-5** — Sửa giao dịch cũ | Lịch sử → tap dòng → Sửa | Sửa trường cần đổi | `derive()` chạy lại, Tổng quan/Lịch sử khớp ngay | Không cảnh báo đặc biệt (không phải destructive) trừ khi sửa Số dư đầu kỳ |
| **FLOW-6** — Xoá giao dịch sai | Lịch sử → tap dòng → Xoá | Xác nhận trong dialog | Snapshot tự động trước, sau đó dòng biến mất, số liệu như chưa từng có nó | Dialog cảnh báo tường minh "không thể hoàn tác", chờ xác nhận |
| **FLOW-7** — Mở app ngày khác, biết ngay việc kế tiếp | Mở app → Tổng quan | Không cần nhập | Thẻ #5 hiển thị đúng `nextPlannedDate`/`nextPlannedAmountVnd` của NGÀY HIỆN TẠI (`asOfDate` tính lại mỗi lần mở) | Không có |

---

## 14. Acceptance Scenarios (AS-01 … AS-12)

Oracle số học = chính `T-12` (`SC-01`…`SC-12`, `docs/spec-l1/COINDCA_L1_PRODUCT_ACCOUNTING_SPEC.md`
§19). Step B **không** tạo lại các fixture đó — nó chứng minh UI hiển thị **đúng** giá trị mà
`derive()` đã được T-12 chứng minh là đúng, qua đúng đường sản xuất.

| ID | Kịch bản | Cách xác nhận |
|---|---|---|
| AS-01 | Mở Tổng quan trên dữ liệu tương đương `SC-09`/`SC-10` | 4 số + hành động kế tiếp trên UI khớp bit-với-bit số `derive()` trả về (tolerance 0) |
| AS-02 | Ghi P2P VND→USDT rồi ghi Mua-Kế hoạch qua UI | Tổng quan cập nhật `investedThisMonthVnd`/`planInvestedVnd`/`remainingPlannedBudgetVnd`/thẻ "Mua kế tiếp" đúng ngay sau khi lưu, không cần tải lại trang |
| AS-03 | Ghi Mua-Ngoài kế hoạch (EXTRA) | `investedThisMonthVnd` tăng, `planInvestedVnd`/`remainingPlannedBudgetVnd`/`carryOut`/"Mua kế tiếp" giữ nguyên (`INV-9`); dòng Lịch sử có badge EXTRA |
| AS-04 | Nạp dự phòng rồi Mua-Từ dự phòng (note bắt buộc) | Số dư dự phòng giảm đúng, không đụng ngân sách kế hoạch; thiếu `note` bị chặn lưu tại form, không cần đợi lỗi từ `ledger.js` |
| AS-05 | Sửa một giao dịch cũ (đổi `qty`) | Sau khi lưu, Tổng quan/Lịch sử tính lại đúng theo `derive()`, `id`/`seq` không đổi |
| AS-06 | Xoá một giao dịch | Snapshot JSON được tạo tự động TRƯỚC khi xoá (kiểm bằng file export xuất hiện), sau xoá số liệu như giao dịch chưa từng tồn tại |
| AS-07 | Số dư đầu kỳ có `usdt.costVnd = null` | Giá vốn VND liên quan hiển thị `—`, banner `UNKNOWN_VND_BASIS` hiện thường trực trên Tổng quan, không có nút ẩn vĩnh viễn |
| AS-08 | Kiểm tra "Mua kế tiếp" theo `scheduleDays`/`carryIn` của một tháng có carry (`SC-09` fixture) | Số ngày/số tiền hiển thị đúng, người dùng không phải tự cộng trừ gì |
| AS-09 | Toàn bộ FLOW-1…FLOW-7 trên khung hình ≤ 400px | Không cuộn ngang, không thao tác nào cần xoay ngang; ghi một giao dịch PLAN từ Tổng quan tốn ≤ 3 lần chạm |
| AS-10 | Rà toàn bộ form/menu | Không có tuỳ chọn "SELL"/"Bán" ở bất kỳ đâu; không màn hình nào hiển thị lãi/lỗ đã thực hiện |
| AS-11 | Nhập muộn một giao dịch (`businessDate` < hôm nay, tương đương `SC-07`) | Thứ tự `(businessDate, seq)` được tôn trọng, Tổng quan/Lịch sử phản ánh đúng vị trí thời gian, không cần thao tác "chèn" đặc biệt |
| AS-12 | Toàn bộ AS-01…AS-11 chạy qua `app_final.html` thật (không gọi hàm module trực tiếp), qua Firestore Emulator + `firestore.rules` thật, tải lại trang | Số liệu sau reload khớp tuyệt đối (tolerance 0) với trước reload |

---

## 15. Production Reachability

Kế thừa đúng khuôn P-1…P-6 đã dùng cho `T-12` (`docs/tasks/T-12-so-cai-l1-v2-va-derive.md`
§ Production Reachability), mở rộng để buộc đi qua **giao diện MỚI** của Step B thay vì panel
tối giản cũ của `ledger_ui.js`:

    PRODUCTION REACHABILITY PASS (Step B)  ⟺  TẤT CẢ:

    PR-1  App nạp qua app_final.html (bundle thật do build_app.js sinh), KHÔNG gọi hàm module
          trực tiếp trong Node.
    PR-2  Toàn bộ AS-01…AS-11 (§14) được thực hiện qua ĐÚNG đường UI mới của Step B — tap/điền
          form thật, không seed thẳng vào state qua console.
    PR-3  Ít nhất 1 sửa và 1 xoá thực hiện qua UI mới (nút Sửa/Xoá ở Lịch sử), có xác nhận dialog
          xuất hiện đúng lúc.
    PR-4  Toàn bộ ghi lên Firestore Emulator (rules thật) và MÁY CHỦ xác nhận (không tính cache
          SDK), đọc lại từ SERVER.
    PR-5  Reload trang → derive() chạy lại → toàn bộ số trên Tổng quan/Lịch sử/Kế hoạch TRÙNG
          KHỚP tuyệt đối (tolerance 0) với oracle của kịch bản.
    PR-6  Không có đường nào trong UI mới gọi trực tiếp một phép tính tài chính ngoài
          derive()/update()/migrate()/destructive() của webapp/ledger.js (grep xác nhận).

    Anti-vacuity: 0 thao tác qua UI mới = FAIL, không phải PASS.

---

## 16. Điều Owner đã quyết định thay (không hỏi lại)

Theo uỷ quyền §17 của chỉ thị phiên ("Owner không cần trả lời hàng chục câu hỏi thẩm mỹ"), các
lựa chọn UX sau đã được CHỐT trong tài liệu này và không cần Owner duyệt lại từng cái:

- IA 4 điểm đến thay vì 5 (§3).
- FAB toàn cục thay vì tab "Giao dịch" riêng (§3.1).
- SELL bị **ẩn hoàn toàn**, không hiển thị dạng "sắp có" (§11 B-1).
- Card-based History trên di động, chuyển bảng khi đủ rộng (§10).
- Nút tắt "Ghi đã mua" điền sẵn số tiền gợi ý từ `nextPlannedAmountVnd` (§4.1).

Không mục nào trong tài liệu này thay đổi phạm vi kế toán, kiến trúc Firebase, hay bất kỳ quyết
định `DEC-042`/`DEC-041` nào — nên không mục nào cần escalate thành Owner Decision riêng.
