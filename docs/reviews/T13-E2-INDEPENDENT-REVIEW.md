# T-13 Independent E2 Review

Status tài liệu:
INDEPENDENT E2 REVIEW — reviewer KHÔNG phải implementer

Ngày: 2026-09-05 · Model: `claude-opus-5` (model phục vụ có thể khác — xem §2) · Effort: high

---

## 1. Executive Summary

`T-13` (CoinDCA L-1 Bước B) đã được review E2 độc lập trên đúng HEAD `cb75d6c`. Reviewer **không**
dùng lại kết luận của implementer: mọi kiểm chứng được tái lập bằng kịch bản do chính reviewer
dựng, chạy qua `app_final.html` thật + Firestore Emulator + `firestore.rules` thật, với oracle là
`CoinLedger.derive()` tính trong Node từ bản state đọc **thẳng từ máy chủ emulator** (REST, không
qua SDK của trang).

**Kết quả: `E2_VERDICT = PASS`.** Cả 7 check `E2_REQUIRED`
(`CHECK-T13-02/03/05/06/07/10/13`) đều PASS độc lập, tolerance 0.

Bằng chứng reviewer tự sinh: **45 kiểm chứng độc lập (44 PASS / 1 FAIL)**, 0 page error, khoảng
**32 thao tác ghi bền thật qua UI mới** cộng 5 thao tác âm/huỷ. Một FAIL duy nhất **không** thuộc
7 check E2 và **không** làm hỏng một REQUIRED check nào đã đóng băng — nó được định tuyến thành
`HARDENING` theo đúng `REVIEW_PROTOCOL.md` (xem §24, `F-T13-E2-01`).

Điểm quan trọng nhất reviewer bổ sung so với bằng chứng của implementer: bộ test của implementer
(`webapp/test_stepb_ui.js`) **chưa bao giờ chạy một tháng có carry** (`carryIn = 0` trong toàn bộ
fixture của nó) và **không assert `nextPlannedAmountVnd`**, dù báo cáo §12 tuyên bố AS-08 phủ
"nextPlannedDate/Amount theo scheduleDays/carry". Reviewer đã dựng kịch bản có `carryIn =
14.000.000 ₫` thật và xác nhận `CHECK-T13-02`/`CHECK-T13-07` vẫn PASS tolerance 0. Nếu không có
bước này, hai check đó sẽ là PASS rỗng.

`T-13` **giữ nguyên `IMPLEMENTED`**. Reviewer **không** chuyển `DONE` — đó là hành vi Owner
(§27).

---

## 2. Reviewer Independence

- Reviewer **không** thi hành `T-13`. Phiên này không sửa một byte production code nào.
- Không dùng lại assertion của `webapp/test_stepb_ui.js` làm bằng chứng. Bộ kiểm của reviewer là
  hai script mới, kịch bản khác, fixture khác, mốc thời gian khác:
  `docs/reviews/evidence/T13/reviewer-e2-part1.js` (25 kiểm chứng, `asOfDate = 2026-03-18`) và
  `docs/reviews/evidence/T13/reviewer-e2-part2.js` (20 kiểm chứng, `asOfDate = 2026-03-25`).
- `test_stepb_ui.js` vẫn được chạy lại **để đối chiếu tuyên bố**, không phải để thay bằng chứng
  (`docs/reviews/evidence/T13/stepb-ui-e2-rerun.txt` — 16/16 PASS, exit 0).
- Mọi tuyên bố trong `docs/reviews/T13-IMPLEMENTATION-REPORT.md` được coi là **CLAIM cần xác
  minh**. §23 dưới đây ghi rõ ba tuyên bố sai/quá lời phát hiện được.
- Không sửa production code, không tiêu repair cycle, không tạo task ID, không đánh dấu `DONE`.
- Model: phiên được cấu hình `claude-opus-5`; model thực tế phục vụ một lượt có thể khác và có thể
  đổi giữa phiên — ghi nhận đúng như vậy thay vì khẳng định.

---

## 3. Source / Branch / Commit

| Mục | Giá trị |
|---|---|
| Repository | `hoangvinhkta-creator/coin` |
| HEAD được review | `cb75d6c8ba64087b065d79a9ffbe351042a79b2a` |
| Nhánh thi hành | `claude/t13-step-b-implementation-8wpnkr` (trỏ đúng `cb75d6c`) |
| Nhánh phiên review | `claude/t13-independent-e2-review-565b5f` (cùng trỏ `cb75d6c` lúc mở phiên) |
| `T13_MEASURE_BASE_SHA` | `5d26bcc4c24d80228720db5d43a52f904df60791` |
| `T-12` | `DONE` (`DEC-046`) |
| `T-13` trước review | `IMPLEMENTED` — `E2_REQUIRED` |

Xác nhận không review nhầm `main`: `git rev-parse HEAD` = `cb75d6c…`, trùng
`claude/t13-step-b-implementation-8wpnkr`.

`branch_authority_check.sh --expect-branch claude/t13-independent-e2-review-565b5f` báo
`BRANCH AUTHORITY: FAIL — attached branch has no upstream` **tại thời điểm mở phiên** (nhánh review
chưa có upstream). Các trường quan trọng khác đều lành: `ahead of default = 1`,
`divergence age = 0 day(s)`, `INTEGRATION_DECISION_REQUIRED = NO`, `tracked worktree = CLEAN`,
`production diff = EMPTY`. Đây là hệ quả của việc nhánh chưa push, **không** phải phân kỳ trạng
thái; state được đọc trên đúng commit đang review.

**Sửa môi trường (ghi lại để tái lập được):** clone ban đầu là **shallow (54 commit)**, khiến đúng
3 test Python fail — `test_wp_a5_failure_signal_instrumentation.py::test_a5_07/test_a5_08` và
`test_wp_b1_slice_failure_signal_cap.py::test_b1_01` — tất cả với cùng nguyên nhân
`subprocess.CalledProcessError: git show 28b0255:src/eth_dca_os/failure_signals.py` exit 128, tức
**thiếu lịch sử git**, không phải sai hành vi. Sau `git fetch --unshallow`, commit `28b0255` hợp
lệ và cả ba PASS (§22). Đây là khiếm khuyết môi trường, không phải `T-13` (`T-13` đổi **0 byte**
`src/eth_dca_os/**`); cùng loại với việc `T-12` E2 phải "sửa môi trường" trước khi chốt Python.

---

## 4. Scope

E2 độc lập cho đúng capability `T-13` đã đóng băng. **KHÔNG** sửa production code, **KHÔNG**
thiết kế lại UX, **KHÔNG** đổi kế toán/`T-12`/ngữ nghĩa SELL, **KHÔNG** giải quyết `H-42`/`H-46`,
**KHÔNG** thêm Firebase/auth, **KHÔNG** tạo task ID, **KHÔNG** tiêu repair authority, **KHÔNG**
mở rộng sang bước C/D.

Finding ≠ task. Mọi finding mới ở §24 được định tuyến theo `governance/v4/CORE/REVIEW_PROTOCOL.md`
§ Finding Routing, mặc định `HARDENING` + `RE_TRIGGER_CONDITION` trừ khi hội đủ cả ba điều kiện
`BLOCKING`.

Môi trường tái lập: Node v22.22.2, Chromium `/opt/pw-browsers/chromium`, Playwright 1.56.1,
firebase-tools 15.28.2, Firebase Emulator (auth :9099, firestore :8080) nạp đúng
`firestore.rules` của repo, Python 3.11.15.

---

## 5. CHECK-T13-02 — Dashboard đúng Dashboard Contract §16

**Yêu cầu (nguyên văn gate đã đóng băng):** khối chính 4 số + 1 hành động, khối dưới, banner bắt
buộc — đối chiếu **tuyệt đối** (tolerance 0) với `derive()` trên fixture `SC-09`/`SC-10`. Không
"GO"/"WAIT"/màu tín hiệu ở thẻ "Mua kế tiếp" (`DEC-041` B).

**Tái lập độc lập.** Reviewer dựng qua UI một trạng thái tương đương `SC-09`/`SC-10` nhưng **có
tháng đã đóng sinh carry thật** (điều fixture của implementer không có): plan `startMonth =
2026-02`, budget 20.000.000 ₫, `scheduleDays [3,13,23]`; opening `2026-02-01` (4.000 USDT giá vốn
100.000.000 ₫ = 25.000 ₫/USDT); một lệnh PLAN 240 USDT ngày `2026-02-03`; một lệnh PLAN 240 USDT
ngày `2026-03-03`; `asOfDate = 2026-03-18`.

Oracle: `derive()` chạy trong Node trên state đọc từ Firestore emulator.

    carryIn = 14.000.000    plannedBudget = 34.000.000
    nextPlannedDate = 2026-03-23    nextPlannedAmountVnd = 14.000.000

**Case đối kháng.**
1. `carryIn > 0` — buộc thẻ #1 phải khác `monthlyBudgetVnd` (fixture implementer không phân biệt
   được vì `carryIn = 0`).
2. Assert **`nextPlannedAmountVnd`** trên phụ đề thẻ #5 (implementer chỉ assert ngày).
3. Assert **toàn bộ 6 mục khối dưới**, kể cả `avgCostUsdt`/`avgCostVnd` dạng phân số.
4. Quét `document.body.innerText` tìm mọi dấu vết khuyến nghị/chiến lược V2.1.5.

**Bằng chứng quan sát được.**

| Kiểm chứng | Kết quả |
|---|---|
| `CHECK-T13-02/main-4+1` | PASS — 5/5 thẻ khớp bit-với-bit `derive()`, gồm `nextPlannedAmountVnd=14000000` |
| `CHECK-T13-02/carry-subtitle` | PASS — phụ đề = `"Gồm 14.000.000 ₫ chuyển từ tháng trước"` (§16.1 bắt buộc khi `carryInVnd > 0`) |
| `CHECK-T13-02/bottom` | PASS — `{"Đang nắm giữ (ETH)":"0,2","Giá vốn TB (USDT)":"2.400","Giá vốn TB (VND)":"60.000.000","Định giá hiện tại":"—","USDT hiện có":"3.520","VND hiện có":"0"}` |
| `CHECK-T13-02/no-recommendation` | PASS — không `GO`/`WAIT`/`Opportunity Score`/`Buy Score`/`regime`/`ladder` trong toàn bộ `innerText` |
| `DASH/priceMark-valid-shows-valuation` | PASS — `"889,2 USDT (2026-03-25)"` khớp `derive().valuation` |
| `DASH/priceMark-validity-16.3` | PASS — giá `2026-03-08` với `asOf 2026-03-25` → `valuation = null`, UI hiện `—`, KHÔNG ngoại suy |

Banner bắt buộc: xác nhận ở §18 (`UNKNOWN_VND_BASIS`) và §15 (`FUTURE_DATED_EVENTS` bật đúng khi
có event ngày tương lai).

**PASS.**

Ghi chú không làm FAIL check (định tuyến `HARDENING`, `F-T13-E2-03`): khi `priceMark` không hợp
lệ, spec §16.3/§4.2 ghi hiển thị `—` kèm **tuổi** của giá ("giá gần nhất: 12 ngày trước"); UI hiện
**ngày** (`— · giá gần nhất 2026-03-08`). Yêu cầu đóng băng của `CHECK-T13-02` là khớp tolerance 0
với `derive()` + không GO/WAIT; `valuation = null` không phải một con số của `derive()` để so, và
không có ngoại suy nào xảy ra.

---

## 6. CHECK-T13-03 — Sheet nhập liệu ánh xạ đúng 8 loại sự kiện

**Yêu cầu:** mỗi loại trong bảng Step-B spec §5 sinh đúng `action.type`/`event.kind`/trường bắt
buộc; `RESERVE` buy thiếu `note` bị chặn **tại form**; không có ô nhập tỷ giá riêng theo lệnh nào
tồn tại trong DOM.

**Tái lập độc lập.** Reviewer bấm từng nút loại trong sheet, điền, Lưu, rồi đọc **durable state
từ máy chủ** và kiểm ánh xạ trên dữ liệu đã ghi bền (không kiểm trên biến trong trang).

**Case đối kháng.**
1. `RESERVE` buy với `note` là **chuỗi toàn khoảng trắng** `'   '` (không phải chuỗi rỗng) — đòi
   validate phải `trim()`, không chỉ kiểm rỗng.
2. Liệt kê **mọi** `input`/`select` trong `#l1Entry` cùng nhãn của nó và lọc theo
   `rate|tỷ giá|fx|vndRate` — bắt cả ô ẩn/nhãn khác tên.
3. Kiểm bất biến `side` trên toàn bộ event đã ghi.

**Bằng chứng quan sát được.**

| Kiểm chứng | Kết quả |
|---|---|
| `CHECK-T13-03/all-kinds-mapping` | PASS — 8/8 ánh xạ đúng trên durable state: `TREASURY VND_TO_USDT`, `TREASURY USDT_TO_VND`, `TRADE BUY PLAN`, `TRADE BUY EXTRA`, `TRADE BUY RESERVE (+note)`, `RESERVE CONTRIBUTE`, `RESERVE WITHDRAW`, `PRICE`. Loại thứ 9 ("Số dư đầu kỳ") điều hướng tới Kế hoạch → Số dư đầu kỳ, đúng §14.3 "sửa MỘT chỗ", không nhân bản form |
| `CHECK-T13-03/reserve-note-blocked` | PASS — `note = '   '` bị chặn tại form với thông điệp `"Giải ngân dự phòng cần lý do…"`; đọc lại durable: **0** event `TRADE/source=RESERVE` được ghi |
| `CHECK-T13-03/no-per-order-fx` | PASS — đúng **một** ô tỷ giá trong toàn bộ sheet: `l1MarkRate` với nhãn `"USDT/VND tham khảo (tùy chọn)"`, thuộc loại `PRICE` (giá tham chiếu thị trường), **không** phải quy đổi từng lệnh → giữ đúng `OD-L1-4` |
| bất biến `side` | PASS — mọi event đã ghi đều `side === undefined \|\| side === 'BUY'` |

**PASS.**

---

## 7. CHECK-T13-05 — Sửa qua UI tính lại đúng, `id`/`seq` không đổi

**Yêu cầu:** sửa một sự kiện qua form → `derive()` chạy lại toàn bộ, Tổng quan/Lịch sử khớp ngay;
`id`/`seq` bất biến (`INV-15`).

**Tái lập độc lập.** Mở Lịch sử → bấm **Sửa** trên đúng thẻ của một lệnh `PLAN` ngày `2026-03-03`
→ đổi `qty` từ `0,1` thành `0,09` → Lưu.

**Case đối kháng.**
1. Kiểm `seq` **và** `id` **và** `events.length` (sửa không được biến thành xoá + tạo mới).
2. Kiểm Tổng quan khớp `derive()` **ngay, không reload**.
3. Kiểm kết quả **sống sót sau reload** (implementer không kiểm điều này cho luồng sửa).
4. Kiểm form chi tiết mở ra đúng event **được chọn** (§15 dưới đây).

**Bằng chứng quan sát được.**

| Kiểm chứng | Kết quả |
|---|---|
| `CHECK-T13-05/edit-recompute-id-seq` | PASS — `id` giữ nguyên, `seq` bất biến (`INV-15`), `events.length` không đổi; `derive()` đổi theo; `Đang nắm giữ (ETH)` và `Đã đầu tư tháng này` khớp `derive()` **ngay** |
| `CHECK-T13-05/edit-survives-reload` | PASS — sau reload: `qty = 9000000`, `seq` nguyên vẹn, khối dưới khớp `derive()` |
| `HISTORY/detail-matches-selected-event` | PASS — form mở đúng `kind`/`businessDate`/`note`/`source`/`usdtNotional`/`qty` của event **được chọn** |

**PASS.**

---

## 8. CHECK-T13-06 — Xoá qua UI: cảnh báo + snapshot bắt buộc trước khi xoá

**Yêu cầu:** dialog cảnh báo tường minh xuất hiện; snapshot export tự động được tạo **TRƯỚC** khi
xoá thật (`INV-14`, gọi đúng `CoinLedger.destructive()`); sau xoá số liệu như giao dịch chưa từng
tồn tại; xoá Số dư đầu kỳ có cảnh báo RIÊNG mạnh hơn.

**Tái lập độc lập.** Bắt sự kiện `download` của trình duyệt, đọc file snapshot từ đĩa, so
bit-exact với state **trước** khi xoá.

**Case đối kháng.**
1. **Huỷ** dialog → sổ phải giữ nguyên (implementer chỉ kiểm nhánh chấp nhận).
2. So `derive()` sau xoá với `derive()` của sổ **lọc bỏ** event đó — chứng minh "như chưa từng tồn
   tại" bằng đẳng thức toàn bộ cây kết quả, không chỉ vắng mặt event.
3. Reload sau xoá.
4. Dialog xoá **Số dư đầu kỳ** phải khác dialog xoá giao dịch thường.

**Bằng chứng quan sát được.**

| Kiểm chứng | Kết quả |
|---|---|
| `CHECK-T13-06/delete-snapshot-first` | PASS — snapshot tải về **khớp bit-exact** state trước khi xoá (`INV-14`); sau xoá hard delete, `events.length − 1`; `derive(sau xoá)` **deepEqual** `derive(sổ không có event đó)`; khối dưới + thẻ dự phòng cập nhật đúng |
| `CHECK-T13-06/confirm-dialog-exists` | PASS — dialog = `"Xóa giao dịch 2026-03-18? Bản đầy đủ đã được xuất trước thao tác này."`; **huỷ ⇒ sổ giữ nguyên** |
| `CHECK-T13-06/opening-stronger-warning` | PASS — dialog riêng = `"Xóa đầu kỳ có thể làm mất giá vốn đã biết. Bản đầy đủ đã được xuất trước thao tác này."`; markup có cảnh báo `"Sửa/xoá số dư đầu kỳ có thể khiến phần lớn giá vốn trở thành KHÔNG XÁC ĐỊNH."`; huỷ ⇒ `openingPosition` còn nguyên |
| `CHECK-T13-06/delete-survives-reload` | PASS — durable state bit-exact sau reload |

Ghi nhận thêm: dòng "Số dư đầu kỳ" ở Lịch sử **không có** nút Xoá (chỉ Sửa) — đúng Step-B spec
§6/§7 (xoá opening là hành động riêng ở Kế hoạch).

**PASS.**

---

## 9. CHECK-T13-07 — Kế hoạch/Carry: ba đại lượng tách riêng

**Yêu cầu:** `monthlyBudgetVnd`/`carryInVnd`/`investedThisMonthVnd` (hoặc `planInvestedVnd`) hiển
thị tách biệt, không gộp; "Mua kế tiếp" đúng theo `scheduleDays`/carry của fixture `SC-09`
(tolerance 0); sửa `scheduleDays`/`monthlyBudgetVnd` áp dụng đúng từ tháng hiệu lực, không hồi tố.

**Đây là check mà bằng chứng E1 của implementer rỗng nhất** — xem §23. Reviewer dựng lại từ đầu.

**Case đối kháng.**
1. Kịch bản **phải** có `monthlyBudgetVnd ≠ plannedBudgetVnd` (assert tường minh), nếu không phép
   so "tách riêng" không phân biệt được gì.
2. Kiểm UI hiện `carryOut` của tháng **đã đóng**, và assert `carryOutVnd` của tháng **hiện tại**
   là `null` — tức UI không được trình bày một `carryOut` **dự phóng** như đã chốt (đúng cảnh báo
   §9 của chỉ thị review).
3. Kiểm mốc `nextPlannedDate` rơi đúng vào ngày lịch kế tiếp qua ranh giới `asOfDate` (18/03 →
   mốc 23, bỏ qua mốc 3 và 13 đã qua).

**Bằng chứng quan sát được.**

| Kiểm chứng | Kết quả |
|---|---|
| `CHECK-T13-07/three-separate` | PASS — `#planCarry` = `{"Ngân sách tháng (chưa gồm carry)":"20.000.000 ₫","Carry tháng trước (đã đóng)":"14.000.000 ₫","→ Cộng vào ngân sách tháng này":"14.000.000 ₫","Đã đầu tư tháng này (tổng)":"6.000.000 ₫","Trong đó theo kế hoạch":"6.000.000 ₫"}` — năm đại lượng **tách biệt**, không gộp, và `monthlyBudgetVnd (20tr) ≠ plannedBudgetVnd (34tr)` nên phép so có tính phân biệt |
| `CHECK-T13-07/prev-closed-carryout` | PASS — `carryOut(2026-02) = 14.000.000` (đã chốt) hiển thị đúng; `carryOut(tháng hiện tại) = null` → UI **không** trình bày carry dự phóng như đã chốt |
| `CHECK-T13-07/next-per-schedule` | PASS — `nextPlannedDate = 2026-03-23`, `nextPlannedAmountVnd = 14.000.000`, tolerance 0 |

Ranh giới lịch/tháng đóng-mở được tấn công đúng chỗ: `asOfDate = 2026-03-18` nằm **giữa** mốc 13
và mốc 23; tháng 2026-02 đã đóng; tháng 2026-03 chưa đóng.

Về "không hồi tố": UI không tự tính carry — `#planCarry` đọc thẳng `d.month`/`d.months[prevKey]`
từ `derive()`, và lưu kế hoạch đi qua `CoinLedger.update({type:'plan'})` với `effectiveFrom` do
người dùng chọn. Hành vi không-hồi-tố thuộc `ledger.js` đã đóng băng ở `T-12` (`INV`/`SC` của
`T-12` phủ, xác nhận lại ở §22). UI không thêm phép tính carry nào — xem §11.

**PASS.**

---

## 10. CHECK-T13-10 — Không công thức tài chính mới, chỉ gọi API đã đóng băng

**Yêu cầu:** (a) mọi con số hiển thị truy được về đúng **một** lệnh gọi `CoinLedger.derive()`;
(b) mọi ghi dữ liệu truy được về `CoinLedger.update()/migrate()/destructive()`; (c) không hàm nào
trong UI tự cộng/trừ/nhân tiền độc lập.

**Tái lập độc lập.** Reviewer **không** dùng regex của implementer (`PR-6` của
`test_stepb_ui.js` chỉ bắt compound-assignment `x += y` — quá hẹp, xem §23). Thay vào đó: quét
**mọi** biểu thức số học nhị phân trên định danh trong `ledger_ui.js` rồi lọc theo tên trường tiền
(`Vnd|Usdt|vndAmount|usdtAmount|usdtNotional|feeUsdt|qty|balance|costVnd|costUsdt|priceUsdt`), và
**soi tay** toàn bộ kết quả thay vì để regex tự tuyên PASS.

**Bằng chứng quan sát được.**

| Kiểm chứng | Kết quả |
|---|---|
| `CHECK-T13-10/single-derive-per-render` | PASS — `ledger_ui.js` có **đúng 1** lệnh `L.derive(` (dòng 348, trong `render()`); 9 lệnh ghi qua `L.update/migrate/destructive/canonical/empty`; **0** đường ghi thẳng vào `state`; **0** thao tác `events.push/splice/pop/shift/unshift` |
| `CHECK-T13-10/no-independent-money-math` | PASS — toàn bộ file chỉ có **1** biểu thức số học chạm trường tiền (`docs/reviews/evidence/T13/money-math-suspects.txt`) |

Biểu thức duy nhất đó, soi tay:

    ledger_ui.js:180   100 - (m.remainingPlannedBudgetVnd / m.plannedBudgetVnd) * 100

Đây là **bề rộng phần trăm của thanh tiến trình**, không phải một con số tiền được hiển thị.
Step-B spec §4.1 cho phép tường minh: *"thanh tiến trình trực quan (đã tiêu / còn lại) — thanh này
chỉ là hiển thị, không phải nguồn tính"*. Không có giá trị tiền nào rời khỏi `derive()`.

Ba vùng còn lại được soi tay và kết luận **không** phải kế toán thứ hai:
- `units()`/`avg()` — hàm trình bày (chia theo `places`, chuyển phân số `numerator/denominator`
  của `derive()` thành chuỗi). Không tạo đại lượng mới.
- `renderHistoryCards()` — in lại **nguyên văn** trường của chính event (`e.vndAmount`, `e.qty`,
  `e.usdtNotional`…), đúng Step-B spec §6 ("mỗi dòng hiển thị … số tiền/số lượng chính"). Không
  dựng lại giá vốn theo từng event — đúng yêu cầu "no misleading per-event basis reconstruction".
- `renderDashBottom()` dòng 201 — chọn PRICE event gần nhất để hiện **ngày** của giá khi
  `valuation = null`. `derive()` **không** trả về giá gần nhất khi mark hết hạn, nên đây là nguồn
  duy nhất có thể; và giá trị lấy ra là một **ngày**, không phải phép tính tiền. Đúng yêu cầu
  §16.3 "không ngoại suy".

**PASS.**

---

## 11. CHECK-T13-13 — Production Reachability PR-1…PR-6 qua UI mới

**Yêu cầu:** toàn bộ AS-01…AS-11 chạy qua `app_final.html` + Firestore Emulator +
`firestore.rules` thật, không gọi hàm module trực tiếp trong Node; reload khớp tuyệt đối
(tolerance 0). Anti-vacuity: 0 thao tác qua UI mới = FAIL.

**Tái lập độc lập.** Cả hai script của reviewer chạy trên bundle thật do `node build_app.js` sinh
(`app_final.html`, 115.432 byte), phục vụ qua HTTP server như Firebase Hosting, với
`firestore.rules` của repo nạp vào emulator và owner UID bootstrap đúng chuỗi thiết lập thật.

| PR | Tái lập của reviewer | Kết quả |
|---|---|---|
| PR-1 | App nạp qua `app_final.html` qua HTTP; `ledger.js` chỉ được `require` trong Node để **tính oracle**, không để tạo dữ liệu | PASS |
| PR-2 | Mọi thao tác tạo/sửa/xoá đều qua tap nút + `fill()` form thật của UI mới; **0** lần seed qua console | PASS |
| PR-3 | ≥1 sửa (§7) và ≥1 xoá (§8) qua nút Sửa/Xoá ở Lịch sử, có dialog xác nhận đúng lúc, **kèm** nhánh huỷ | PASS |
| PR-4 | Ghi lên emulator với rules thật; đọc lại **thẳng từ SERVER** qua REST (`H.getDoc('state')`), không qua cache SDK; `derive(server state)` khớp UI | PASS |
| PR-5 | Reload → so **toàn bộ** 5 thẻ chính (giá trị + phụ đề) + 6 mục khối dưới + 5 mục Kế hoạch/carry, trước/sau, và với `derive()` | PASS |
| PR-6 | Xem §10 — quét rộng hơn regex của implementer | PASS |

**Số liệu anti-vacuity (đo được, không phải tuyên bố):**

| Nguồn | Thao tác ghi bền thật qua UI | Kiểm chứng |
|---|---|---|
| `reviewer-e2-part1.js` | 14 (plan, opening, 2×PLAN, p2p_in, p2p_out, EXTRA, RESERVE nạp, RESERVE rút, RESERVE buy, PRICE, sửa, xoá, import) + 4 thao tác âm/huỷ | 25 |
| `reviewer-e2-part2.js` | 18 (plan, opening, 14 event, PRICE hôm nay, PLAN 3-chạm) + 1 huỷ sửa | 20 |
| `test_t12_browser.js` (chạy lại) | 10 (`realEventsCreated: 10`) | 17 |
| `test_stepb_ui.js` (chạy lại) | 15 | 16 |

Tổng của riêng reviewer: **32 thao tác ghi bền + 5 thao tác âm/huỷ, 45 kiểm chứng**. Không phải
0 event / 0 case.

**Page errors: `[]` trên cả hai script của reviewer.** Không `pageerror`, không console error
ngoài nhiễu mạng đã lọc sẵn của harness.

**PASS.**

---

## 12. Dashboard Adversarial Review

Xác nhận Dashboard là **VIEW** trên `derive()`, không phải bộ máy kế toán cạnh tranh.

| Đại lượng | Nguồn UI | Đối chiếu `derive()` | Kết quả |
|---|---|---|---|
| `holdings.ETH.qty` | `dashBottom` "Đang nắm giữ (ETH)" | `units(d.holdings.ETH.qty, 8)` | khớp |
| Giá vốn VND (ETH) | `dashBottom` | `avg(d.holdings.ETH.avgCostVnd)` (phân số) | khớp |
| Giá vốn USDT (ETH) | `dashBottom` | `avg(d.holdings.ETH.avgCostUsdt, 1e6)` | khớp |
| Số dư USDT | `dashBottom` | `units(d.usdt.qty, 6)` | khớp |
| Số dư VND | `dashBottom` | `units(d.vnd.balance)` | khớp |
| Ngân sách tháng | thẻ #1 | `d.month.plannedBudgetVnd` | khớp |
| Đã đầu tư tháng này | thẻ #2 | `d.month.investedThisMonthVnd` | khớp |
| Còn lại theo kế hoạch | thẻ #3 | `d.month.remainingPlannedBudgetVnd` | khớp |
| `carryIn` | thẻ #1 phụ đề + `#planCarry` | `d.month.carryInVnd` | khớp |
| `carryOut` (tháng đóng) | `#planCarry` | `d.months['2026-02'].carryOutVnd` | khớp |
| Số dư dự phòng | thẻ #4 | `d.reserve.balance` | khớp |
| `nextPlannedDate` | thẻ #5 | `d.month.nextPlannedDate` | khớp |
| `nextPlannedAmountVnd` | thẻ #5 phụ đề | `d.month.nextPlannedAmountVnd` | khớp |
| Định giá hiện tại | `dashBottom` | `d.valuation` (null ⇒ `—`) | khớp |

Tolerance 0 trên mọi ô tiền (so **chuỗi hiển thị** với chuỗi sinh từ `derive()` bằng đúng hàm
trình bày, nên sai một đồng là FAIL).

Không có `GO`/`WAIT`, không màu tín hiệu, không "recommendation", không strategy score, không
`Opportunity Score`/`Buy Score`/`regime`/`ladder` ở bất kỳ đâu trong `innerText`. Không có phép
tính tài chính độc lập ẩn (§10).

---

## 13. Transaction Entry

Đã thực hiện **toàn bộ** loại được Step B duyệt, qua sheet thật (§6):

| Loại | Ánh xạ quan sát trên durable state | Kết quả |
|---|---|---|
| Số dư đầu kỳ | `action.type = 'opening'` (điều hướng Kế hoạch → Số dư đầu kỳ) | đúng |
| P2P VND → USDT | `TREASURY / VND_TO_USDT` | đúng |
| P2P USDT → VND | `TREASURY / USDT_TO_VND` | đúng |
| BUY PLAN | `TRADE / BUY / PLAN` | đúng |
| BUY EXTRA | `TRADE / BUY / EXTRA` | đúng |
| BUY RESERVE | `TRADE / BUY / RESERVE` + `note` bắt buộc | đúng |
| RESERVE contribution | `RESERVE / CONTRIBUTE` | đúng |
| RESERVE withdrawal | `RESERVE / WITHDRAW` | đúng |
| PRICE | `PRICE` + `usdVndRate` tuỳ chọn | đúng |

**Tấn công đầu vào — UI có tạo được sự kiện tài chính bền KHÔNG hợp lệ không?**

| Tấn công | Quan sát |
|---|---|
| RESERVE buy thiếu `note` (chuỗi toàn khoảng trắng) | Chặn **tại form** (`trim()`), 0 event ghi bền |
| Số tiền/số lượng sai định dạng (quá số lẻ cho phép) | `L.decimal()` ném `"Sai độ chính xác số nhập"`, hiện ở `#l1Message`, không commit |
| Thiếu trường bắt buộc (`qty`/`usdtNotional` rỗng) | `eventCheck` của `ledger.js` từ chối; state không đổi |
| `businessDate` trước `openingPosition.asOf` | Từ chối `"Ngày giao dịch trước số dư đầu kỳ"` |
| `businessDate` trong tương lai | Chấp nhận (hợp lệ theo §10 spec) nhưng bật banner `FUTURE_DATED_EVENTS` + badge `TƯƠNG LAI` ở Lịch sử |
| Tổ hợp nguồn sai (`side` khác `BUY`) | Không tạo được: `#l1Side` chỉ còn một option `BUY` |
| Ô tỷ giá riêng theo lệnh | Không tồn tại (`OD-L1-4` giữ nguyên) |

Mọi ghi đều đi qua `CoinLedger.update()`; không có đường ghi thẳng vào `state`. **UI không tạo
được sự kiện tài chính bền không hợp lệ.**

---

## 14. SELL Guard

`H-46` chưa được giải quyết; Step-B PRODUCT path **không được** lộ SELL.

| Tiêu chí (§6 chỉ thị review) | Quan sát | Kết quả |
|---|---|---|
| SELL menu option | `#l1Side` chỉ còn `["BUY=Mua"]` | không có |
| SELL button | quét mọi `button` — 0 kết quả `SELL` | không có |
| "Bán" action | 0 nút/option/nhãn form-menu chứa `Bán` | không có |
| realized P&L | `innerText` không chứa `realizedFxVnd`/`lãi/lỗ`/`đã thực hiện`/`P&L`/`PnL` | không có |
| Hidden functional SELL form | Sheet chỉ dựng được `side='BUY'`; không markup SELL ẩn | không có |
| URL/hash path lộ SELL | Thử `#/sell`, `#/history/sell`, `#/trade?side=SELL` — router chỉ nhận `dashboard\|history\|plan\|settings`, không lộ gì | không có |
| Hành động UI/bàn phím bật SELL | Không tồn tại | không có |

**SELL GUARD: PASS.** UI sản phẩm Step B **không** tạo được, không phơi bày, không bật được nghiệp
vụ SELL. Đúng chỉ thị, reviewer **không** fail chỉ vì `webapp/ledger.js` (T-12, đóng băng) còn cơ
chế SELL nội bộ.

**Nhưng có một nhãn tiềm ẩn — `F-T13-E2-01` (HARDENING, §24).** `webapp/ledger_ui.js:142`:

    if (e.kind === 'TRADE') return 'Mua ETH' + (e.side === 'SELL' ? ' (Bán)' : '') + …

Reviewer tái lập được đường tới nhãn này qua **đúng UI sản phẩm** (Cài đặt → "Nạp lại từ JSON"),
`docs/reviews/evidence/T13/sell-label-reachability.txt`:

    canonicalAcceptsSELL: true
    sellStoredDurable:    true
    renderedCardsContainingBan: ["2026-03-05\nMua ETH (Bán)\n0,1 ETH · 240 USDT\nreviewer SELL\nSửa\nXoá"]
    derivedFlags: []

Vì sao **không** làm FAIL `CHECK-T13-09` (và không nằm trong 7 check E2): yêu cầu đóng băng là
*"không có tuỳ chọn SELL/Bán ở bất kỳ **form/menu** nào; không màn hình nào hiển thị lãi/lỗ đã
thực hiện"* — cả hai đều đúng. Đây là một **nhãn hiển thị** chỉ render khi sổ **đã** chứa một
`TRADE side='SELL'`, và Step-B UI không tạo được event đó; người dùng phải tự soạn JSON rồi nạp
lại. Định tuyến `HARDENING` + `RE_TRIGGER_CONDITION` (§24).

---

## 15. History

Tập dữ liệu tổng hợp của reviewer: **14 event** đủ 8 loại + 1 nhập muộn + 1 ngày tương lai (vượt
ngưỡng "≥ 12 sự kiện đủ loại" của `CHECK-T13-04`).

| Kiểm chứng | Kết quả |
|---|---|
| Hiển thị từ event nguồn canonical | PASS — số thẻ = số event của durable state |
| Thứ tự | PASS — `(businessDate DESC, seq DESC)` khớp chính xác danh sách kỳ vọng |
| `businessDate` đúng | PASS — từng thẻ khớp `businessDate` của event tương ứng |
| PLAN/EXTRA/RESERVE phân biệt được | PASS — badge `EXTRA`/`RESERVE` đúng; PLAN **không** mang badge (mặc định ngầm, đúng §6) |
| UNKNOWN hiện rõ | PASS — chip `—` đánh dấu "có liên quan tới UNKNOWN", **không** rò rỉ `realizedFxVnd` (giữ `H-45` không mở rộng) |
| Bộ lọc không đổi sự thật sổ | PASS — durable state **bit-exact** trước/sau mọi thao tác lọc |
| Lọc theo loại | PASS — `PLAN=3 EXTRA=3 RESERVE_BUY=1 RESERVE=3 TREASURY=3 PRICE=1`, từng tập khớp chính xác tập kỳ vọng |
| Lọc khoảng ngày | PASS — `2026-03-05..2026-03-13` trả đúng 7 event, bao gồm cả hai đầu mút |
| Tìm theo ghi chú | PASS — `"gamma"` trả đúng 1 kết quả (kịch bản có tính phân biệt) |
| Reset bộ lọc | PASS — xoá loại/khoảng ngày/tìm kiếm đều khôi phục đủ 14 thẻ |
| Lọc không ảnh hưởng Tổng quan | PASS — lọc `PLAN` xong, "Đã đầu tư tháng này" vẫn = `derive()` trên **toàn bộ** event |
| Chi tiết khớp event được chọn | PASS — mọi trường form khớp event đã bấm |
| Số dư đầu kỳ phân biệt | PASS — đúng 1 dòng, **ở đầu** danh sách, chỉ có Sửa, **không** có Xoá |
| Không dựng lại giá vốn theo từng event | PASS — thẻ chỉ in lại trường của chính event; không có "giá vốn dòng này" bịa ra |
| Nhập muộn | PASS — event `2026-03-10` nhập **sau cùng** xếp ở vị trí 5 theo `businessDate`, khác vị trí 1 nếu xếp theo thứ tự nhập (AS-11 có tính phân biệt) |

Ghi nhận nhỏ, không phải finding: Step-B spec §6 nêu lọc "theo tháng lịch"; UI cung cấp khoảng
`từ ngày`/`đến ngày`, đạt được lọc theo tháng bằng hai đầu mút. `CHECK-T13-04` (E1) đã PASS và
không thuộc phạm vi E2 của phiên này.

---

## 16. Edit/Delete

Thực hiện **thao tác UI thật**, không chỉ đọc mã nguồn — chi tiết ở §7 và §8.

**EDIT** — PASS: đúng event được chọn; `id`/`seq` giữ nguyên (`INV-15`); `events.length` không
đổi (không phải xoá + tạo mới); Tổng quan/Lịch sử tính lại từ `T-12` ngay không cần reload; reload
giữ nguyên kết quả.

**DELETE** — PASS: dialog cảnh báo tường minh có mặt; **huỷ ⇒ sổ giữ nguyên**; đúng event bị xoá;
snapshot JSON tải về **trước** khi xoá và khớp bit-exact state trước đó (`INV-14`); kết quả
`derive()` sau xoá **deepEqual** `derive()` của sổ như thể event chưa từng được nhập; Tổng
quan/Lịch sử cập nhật; reload giữ nguyên.

**DELETE Số dư đầu kỳ** — PASS: dialog **riêng, mạnh hơn**, khác dialog xoá giao dịch thường.

---

## 17. Plan/Carry

Xem §9. Tóm tắt số liệu tái lập độc lập (`asOfDate = 2026-03-18`):

    monthlyBudgetVnd        = 20.000.000     (hiển thị tách riêng)
    scheduleDays            = [3, 13, 23]
    carryOut(2026-02, đóng) = 14.000.000     (hiển thị tách riêng)
    carryInVnd              = 14.000.000     (hiển thị tách riêng)
    plannedBudgetVnd        = 34.000.000
    investedThisMonthVnd    =  6.000.000     (hiển thị tách riêng)
    planInvestedVnd         =  6.000.000     (hiển thị tách riêng)
    remainingPlannedBudget  = 28.000.000
    nextPlannedDate         = 2026-03-23
    nextPlannedAmountVnd    = 14.000.000
    carryOut(2026-03, mở)   = null           (UI KHÔNG trình bày như đã chốt)

Tấn công ranh giới lịch/tháng đóng-mở: PASS (§9). UI **không** tự tính lại carry, **không** trình
bày `carryOut` dự phóng như đã chốt, **không** biến "Mua kế tiếp" thành khuyến nghị thị trường
(§12).

---

## 18. UNKNOWN

Trạng thái tổng hợp hợp lệ do reviewer dựng: `openingPosition.usdt.costVnd = null` (bỏ trống ô
"Tổng giá vốn USDT (VND)") ⇒ `derive().flags` chứa `UNKNOWN_VND_BASIS`.

| Kiểm chứng | Kết quả |
|---|---|
| Banner bắt buộc | PASS — `#l1Flags` (`role="alert"`) hiện `"Một số giá vốn VND chưa xác định — … (UNKNOWN_VND_BASIS)"`, giữ cả nhãn tiếng Việt lẫn mã cờ gốc |
| Không hiển thị UNKNOWN thành 0 | PASS — "Giá vốn TB (VND)" = `"—"`, khác `"0"`, khác rỗng, khác `NaN` |
| Không thay thế FX ngầm | PASS — không ô tỷ giá riêng lệnh nào tồn tại (`OD-L1-4`); không có đường quy đổi ngầm |
| Không tắt được bằng tương tác thường | PASS — `#l1Flags button` = **0**; sau reload + 4 lần đổi màn hình banner vẫn còn |
| Không lưu trạng thái "đã đọc" | PASS — không key `localStorage` nào chứa `dismiss/banner/read/hidden` |
| Giữ ranh giới `H-45` | PASS — không rò rỉ `realizedFxVnd` hay số nội bộ nào ở Lịch sử; chip UNKNOWN chỉ đánh dấu "có liên quan" |

`H-45` **không bị mở rộng** và **không bị chạm**: reviewer không dựng thêm điều kiện kích hoạt
mới, không sửa `webapp/ledger.js` (0 dòng đổi — §22).

---

## 19. Navigation/Mobile

Khung hình mục tiêu **390 × 844**.

| Kiểm chứng | Kết quả |
|---|---|
| 4 điểm đến | PASS — `dashboard=Tổng quan, history=Lịch sử, plan=Kế hoạch, settings=Cài đặt`; đúng 4 `<section class="view-sec">` |
| Hành động toàn cục "+ Ghi giao dịch" | PASS — FAB `#fabEntry` hiện diện, ngoài `l1Root`, dùng được từ mọi màn |
| Không cuộn ngang | PASS — `scrollWidth = 390 ≤ clientWidth = 390`; quét mọi phần tử `body *` vượt mép phải: **rỗng** |
| Touch target dùng được | PASS — mọi nút bottom-nav/FAB/chọn-loại/Sửa-Xoá đều ≥ 24px ở 390px |
| Tap budget luồng PLAN | PASS — **3 lần chạm** (FAB → chọn loại → Lưu) ghi được 1 giao dịch PLAN từ Tổng quan, đúng trần đóng băng ≤ 3 |
| Hash sống sót refresh | PASS — `#/history`, `#/plan`, `#/settings`, `#/dashboard`: sau `reload()` hash giữ nguyên **và** `aria-current` trỏ đúng điểm đến |
| Back/forward không hỏng state | PASS — durable state **bit-exact** sau `goBack()`/`goForward()`; 0 page error |
| Bottom-nav/FAB định tuyến đúng | PASS — mỗi nút cuộn tới đúng `#view-*` và cập nhật hash |

Ghi nhận (quan sát chức năng, không phải thẩm mỹ, không phải finding): `routeTo()` dùng
`history.replaceState`, nên nút Back của trình duyệt **không** duyệt qua lại giữa 4 điểm đến —
nó rời ứng dụng. Không gây hỏng trạng thái (đã kiểm). Hợp đồng Step-B đóng băng chỉ đòi
"refresh giữ đúng màn hình", điều này **đạt**.

---

## 20. AS-01…AS-12

Tái lập bằng kịch bản/chuỗi hành động **do reviewer kiểm soát**, oracle = `T-12`.

| ID | Tái lập độc lập của reviewer | Kết quả |
|---|---|---|
| AS-01 | Tổng quan trên trạng thái tương đương `SC-09`/`SC-10` **có carry thật**; 5 thẻ + khối dưới khớp bit-với-bit `derive()` | PASS |
| AS-02 | P2P VND→USDT rồi Mua-Kế hoạch qua sheet; Tổng quan cập nhật ngay, không reload | PASS |
| AS-03 | Mua EXTRA: `investedThisMonthVnd` tăng; `planInvestedVnd`/`remainingPlannedBudgetVnd`/`nextPlannedDate` bất biến (`INV-9`); badge EXTRA ở Lịch sử | PASS |
| AS-04 | Nạp dự phòng → Mua-Từ dự phòng; thiếu `note` (toàn khoảng trắng) bị chặn tại form; số dư dự phòng khớp `derive()` | PASS |
| AS-05 | Sửa `qty` qua Lịch sử; `id`/`seq` bất biến; tính lại đúng; **sống sót reload** | PASS |
| AS-06 | Xoá: snapshot JSON tạo **trước**, khớp bit-exact; sau xoá = sổ chưa từng có event; **huỷ ⇒ giữ nguyên** | PASS |
| AS-07 | `usdt.costVnd = null` → `—` khắp nơi + banner `UNKNOWN_VND_BASIS` thường trực, 0 nút ẩn | PASS |
| AS-08 | "Mua kế tiếp" theo `scheduleDays`/`carryIn` **của một tháng CÓ carry** (`carryIn = 14.000.000`) — tolerance 0 | PASS |
| AS-09 | FLOW-1…FLOW-7 ở 390px: không cuộn ngang, không xoay ngang, PLAN từ Tổng quan = 3 chạm | PASS |
| AS-10 | Rà toàn bộ form/menu: 0 `SELL`/`Bán`; 0 màn hiển thị lãi/lỗ đã thực hiện | PASS |
| AS-11 | Nhập muộn `2026-03-10` **sau cùng**: xếp đúng vị trí thời gian (khác vị trí theo thứ tự nhập) | PASS |
| AS-12 | Toàn bộ AS-01…AS-11 qua `app_final.html` + Emulator + rules thật; reload khớp tuyệt đối | PASS |

**12/12 PASS.**

---

## 21. PR-1…PR-6

Xem §11. **6/6 PASS.**

- Số thao tác tài chính thật qua UI của riêng reviewer: **32 ghi bền + 5 thao tác âm/huỷ**.
- Số kiểm chứng của riêng reviewer: **45** (44 PASS / 1 FAIL — FAIL không thuộc 7 check E2).
- Bằng chứng reload: `PR-4/PR-5-reload-tolerance-0`, `CHECK-T13-05/edit-survives-reload`,
  `CHECK-T13-06/delete-survives-reload` — cả ba so bit-exact.
- Page errors: **0**.
- Đẳng thức persistence: `H.readState()` so `durable` (đọc REST từ emulator) với mirror trong bộ
  nhớ trang ở **mọi** lần đọc; lệch một giá trị là ném lỗi. Không lần nào ném.

**Không phải 0 event / 0 case.**

---

## 22. Accounting Non-Regression

`T-13` **không** được đổi ngữ nghĩa tài chính của `T-12`.

**Diff production (đo lại, không cộng tay từ báo cáo):**

    git diff --shortstat 5d26bcc4c24d80228720db5d43a52f904df60791..HEAD -- \
      webapp/app_logic.js webapp/engine.js webapp/app_shell.html webapp/build_app.js \
      webapp/ledger_ui.js webapp/ledger.js src/eth_dca_os pyproject.toml pyproject.lock
    -> 3 files changed, 374 insertions(+), 1330 deletions(-)

Dưới trần `+1800 / −1400`. Khớp con số báo cáo.

**Xác nhận file nguồn kế toán KHÔNG đổi** (`git diff --stat` trả rỗng):

`webapp/ledger.js`, `webapp/engine.js`, `webapp/test_t12_fixtures.js`, `webapp/test_t12_ledger.js`,
`webapp/test_t12_browser.js`, `webapp/test_t12_mutations.js`, `webapp/test_t12_owner.js`,
`webapp/test_firebase_harness.js`, `webapp/test_helpers.js`, `firestore.rules`, `firebase.json`,
`webapp/firebase_config.js`, `webapp/package.json`, `src/eth_dca_os/**`, `pyproject.*`.

Toàn bộ tệp thay đổi bởi `T-13` (7 file): `webapp/app_logic.js`, `webapp/app_shell.html`,
`webapp/ledger_ui.js`, `webapp/test_stepb_ui.js` (mới, không phải production path),
`PROJECT/PROJECT_PROGRESS.md`, `docs/tasks/T-13-*.md`, `docs/reviews/T13-IMPLEMENTATION-REPORT.md`.
Không file production **mới** nào ⇒ `S-B11` đúng là N/A.

**Suite kế toán chạy lại độc lập:**

| Suite | Kết quả reviewer | Ghi chú |
|---|---|---|
| `test_t12_ledger.js` (`node --test`) | **32/32 PASS**, 0 fail, 0 skip | SC-01…SC-12 + INV-1…INV-15 |
| `test_t12_mutations.js` | **7/7 mutant KILLED, 0 survivor**, exit 0 | bộ mutation vẫn còn hiệu lực |
| `test_t12_owner.js` | **PASS** với `tests/fixtures/t12/owner-example.synthetic.json` | chạy không tham số thì FAIL **theo thiết kế** (cần đường dẫn fixture) — không phải regression |
| `test_t12_browser.js` | **17/17 PASS**, exit 0, `errors: []`, `realEventsCreated: 10` | bằng chứng production reachability ĐÓNG BĂNG của `T-12`, chạy **nguyên văn không sửa** |
| Python `pytest` | **678 collected, 678/678 PASS, exit 0** | khớp con số đã biết trước `T-13`; chỉ đạt được **sau** khi `git fetch --unshallow` (§3) |

`test_t12_browser.js` chạy được nguyên văn là bằng chứng mạnh nhất cho "T-13 không chạm lớp tài
chính": file đó thao tác trực tiếp trên `#l1Kind`/`#l1Date`/`#l1Summary`/`#l1History`… và so oracle
số nguyên tolerance 0.

`SC-01…SC-12` và `INV-1…INV-15`: PASS qua `test_t12_ledger.js` (32/32) + `test_t12_browser.js`
(`INV-1/14 import`, `INV-14 hủy wipe`, `SC-12 production`, `Migration M-1…M-4`). Reviewer bổ sung
xác nhận `INV-9` (EXTRA không đụng ngân sách kế hoạch), `INV-14` (snapshot trước xoá) và `INV-15`
(`id`/`seq` bất biến) **qua đúng UI mới** (§7, §8, §20).

**Không có phép dẫn xuất tài chính thứ hai trong UI** — §10.

**`T-13` KHÔNG đổi ngữ nghĩa kế toán.** Không kích hoạt `ARCHITECTURE_CHANGE_REQUIRED`.

---

## 23. Regression / N-A Review

Implementer phân loại **sáu** file test V2.1.5 là `NOT_APPLICABLE`. Reviewer soi lại phê phán.

**(a) Điểm fail thật — tái lập độc lập.** Reviewer chạy cả sáu file. Cả sáu fail tại **đúng một
điểm dự đoán trước**:

    page.setInputFiles: Timeout 30000ms exceeded.
      - waiting for locator('#seedFile')

Không file nào fail vì một lý do khác (không phải lỗi kế toán, không phải lỗi persistence).

**(b) Thẩm quyền xoá `#seedFile` — có thật, nhưng implementer dẫn sai dòng.** `#seedFile` nằm
trong `#tab-setup` của `app_shell.html` trước `T-13` (xác minh: `git show 5d26bcc:webapp/app_shell.html`
dòng 497 `<div class="panel" id="tab-setup">` chứa dòng 505 `<input type="file" id="seedFile">`).
Step-B spec §12 có dòng cho phép tường minh:

    nav.tabs 5 tab cũ (dash/entry/ladder/history/setup) | app_shell.html | REMOVE_FROM_L1_PATH

`setup` được nêu đích danh ⇒ **việc xoá là có thẩm quyền**. Tuy nhiên báo cáo implementation §14
dẫn `Step-B spec §12 dòng "Nạp dữ liệu lịch sử"` — **dòng đó KHÔNG tồn tại** trong spec (grep xác
nhận). Dẫn nguồn sai, kết luận đúng.

**(c) Có hành vi persistence/accounting CÒN HIỆU LỰC nào bị giấu sau N/A không?** Đây là câu hỏi
trọng tâm; reviewer **không** chấp nhận lời cam đoan của implementer.

- **Kế toán V2.1.5** (`test_t09a_accounting.js`, `test_zone.js`, `test_v01_v02_v03.js`,
  `test_multi_month_invariant.js`): mô hình kế toán đó (`addBuy`/`addP2P`/`addContribution`/
  `ledger()`/`month()`/pool/ladder/zone) đã bị **thay thế** bởi `webapp/ledger.js` theo `DEC-041` +
  `DEC-042`. Đây là hành vi sản phẩm **bị gỡ có chủ ý**; đúng chỉ thị, reviewer không đòi nó sống
  sót. Kế toán còn hiệu lực (L-1) được phủ bởi 32 unit + 7 mutant + 17 browser của `T-12` (§22).
- **Persistence** (`test_t09b_persistence.js`, 118 assertion, phủ `CHECK-T09B-01…16`): reviewer
  **không** chấp nhận suy luận "hàm không đổi nên hành vi không đổi". Đã đối chiếu độ phủ:

  | CHECK-T09B | Còn hiệu lực? | Ai phủ sau T-13 |
  |---|---|---|
  | 01 ghi bền thành công | có | `test_t12_browser.js` P-4/P-5 + reviewer `PR-4/server-read-back` |
  | 02 nạp đúng state từ Firebase | có | `Persistence browser restart` + reviewer reload |
  | 03 xoá localStorage vẫn recover | có | `test_t12_browser.js` (`localStorage.clear()` + reload) |
  | 04 đóng/mở lại môi trường | có | `Persistence browser restart` |
  | 05 lịch sử giao dịch bảo toàn | có (dạng L-1) | `T-12` browser + reviewer §15 |
  | 06 holdings/giá vốn bảo toàn | có (dạng L-1) | `T-12` oracle + reviewer §12 |
  | 07 pool/reserve/release V2.1.5 | **không** — khái niệm bị gỡ (`DEC-041` B) | N/A hợp lệ |
  | 08 ladder + `ladder.month` | **không** — bị gỡ (`DEC-041` B) | N/A hợp lệ |
  | 09 bất biến kế toán T-09A | **không** — mô hình bị thay (`DEC-042`) | N/A hợp lệ |
  | 10 ghi lỗi hiện rõ | có | `Persistence rejected write/retry` |
  | 11 đọc lỗi hiện rõ | có | `Persistence offline` + bootstrap `UNRECOGNIZED` |
  | 12 state hỏng không thành state kế toán | có | `Persistence corrupt/version` |
  | 13 hành vi web sạch không regression | phần lớn bị gỡ có chủ ý | — |
  | 14 workflow cá nhân | có | thủ công / UX |
  | 15 không tuyên bố state lịch sử là sạch | có | `SC-12 production`, `Migration M-1…M-4` |
  | **16 mirror không âm thầm thắng nguồn bền** | **có** | **KHÔNG suite nào phủ sau `T-13`** |

  `CHECK-T09B-16` là hành vi **còn sống thật**: `reconcileMirror()`/`pushDiverged()`/
  `dropDiverged()`/`showMirrorReadOnly()` vẫn nằm nguyên trong `webapp/app_logic.js`. Reviewer đã
  **tự kiểm hành vi này trên UI Step B**: giả mạo mirror `localStorage` với `rev + 5` và sổ khác
  hẳn, reload, rồi đọc lại nguồn bền qua REST.

      T09B-16/mirror-never-silently-wins :: PASS
      mirror rev+5 KHÔNG thắng nguồn bền (server bit-exact như trước);
      app BÁO phân kỳ, chờ người dùng chọn tường minh.

  ⇒ **Hành vi production ĐÚNG.** Cái mất là **bằng chứng tự động chạy lại được**, không phải hành
  vi. Định tuyến `HARDENING` (`F-T13-E2-02`, §24) — cùng họ với `H-44`.

**(d) Có blanket skip/deselect nào không?** **KHÔNG.** `git diff` xác nhận không file test nào bị
sửa; `webapp/package.json` **không đổi một byte**, nên `scripts.test` vẫn liệt kê đủ sáu file —
implementer đã đúng khi **không** gỡ chúng ra để lấy suite xanh (đúng tinh thần `CHECK-T13-12` và
tiền lệ `CHECK-T12-13`). Hệ quả đo được: `npm --prefix webapp test` hiện **exit khác 0** (fail tại
`test_app.js`). Đây là phần thứ hai của `F-T13-E2-02`.

**(e) Hồi quy còn áp dụng, chạy độc lập:** `test_shared_rules_merge.js` không liên quan UI. Các
suite `T-12` và Python: §22.

**Kết luận §23:** phân loại `NOT_APPLICABLE` của implementer là **đúng về thực chất** (điểm fail
thật đúng như mô tả; thẩm quyền tồn tại; không hành vi kế toán/persistence còn hiệu lực nào bị
**hỏng**), nhưng **dẫn nguồn sai một dòng spec** và **bỏ sót một khoảng trống bằng chứng thật**
(`CHECK-T09B-16`). Không đủ điều kiện `BLOCKING`.

---

## 24. Findings

Định tuyến theo `governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing. `BLOCKING` đòi **cả
ba**: đường production hiện hành + hậu quả nghiệp vụ nằm trong một Completion Gate hoặc risk
register + bằng chứng tái lập được. Thiếu một ⇒ `HARDENING` + `RE_TRIGGER_CONDITION`.
**Finding ≠ task. Reviewer KHÔNG tạo task ID, KHÔNG cấp ID hardening mới** (đánh số `H-*` là hành
vi của phiên có thẩm quyền backlog; ở đây dùng mã finding `F-T13-E2-*`).

### F-T13-E2-01 — HARDENING — Nhãn Lịch sử render `Mua ETH (Bán)` cho TRADE `side='SELL'` nạp qua UI

- **Đường production:** `webapp/ledger_ui.js:142` (`KIND_LABEL`) — production path đã khai
  (`PROJECT/PRODUCTION_PATHS.md` §1).
- **Bằng chứng tái lập:** `docs/reviews/evidence/T13/sell-label-reachability.txt` +
  `reviewer-e2-part1.js` (`SELL/import-json-path`). Đường đi: Cài đặt → "Nạp lại từ JSON" với một
  sổ tự soạn có `TRADE side='SELL'` → `L.canonical()` chấp nhận (`ledger.js:110` cho phép `SELL`,
  đóng băng ở `T-12`) → ghi bền → Lịch sử render
  `"2026-03-05 / Mua ETH (Bán) / 0,1 ETH · 240 USDT"`.
- **Hậu quả:** nhãn **tự mâu thuẫn** ("Mua ETH (Bán)") có thể khiến người dùng hiểu sai chiều giao
  dịch. `derive().flags` **rỗng** — không cờ nào cảnh báo.
- **Vì sao KHÔNG `BLOCKING`:** `CHECK-T13-09` (đóng băng) đòi không có tuỳ chọn `SELL`/`Bán` ở
  **form/menu** và không hiển thị lãi/lỗ đã thực hiện — **cả hai đều đạt**. Không REQUIRED check
  nào bị vi phạm; không mục nào trong risk register bị chạm. UI Step B **không tạo được** event
  `SELL`; người dùng phải tự soạn JSON. Thiếu điều kiện thứ hai của `BLOCKING`.
- **RE_TRIGGER_CONDITION:**
  - `H-46` được Owner giải quyết và nghiệp vụ SELL được mở cho dữ liệu thật; **hoặc**
  - bất kỳ đường UI nào trở nên có khả năng **tạo** event `side='SELL'`; **hoặc**
  - `migrate()` bắt đầu sinh event `SELL`; **hoặc**
  - một Completion Gate tương lai mở rộng yêu cầu SELL-guard từ "form/menu" sang "mọi nhãn hiển
    thị".
- **Ghi chú độ chính xác báo cáo:** `T13-IMPLEMENTATION-REPORT.md` §11 khẳng định *"không
  `SELL`/`Bán` trong bất kỳ `button`/`option`/`label`/`select`/`.txtype`/tiêu đề/**nhãn** nào của
  UI mới"* — **sai như đã viết**: `KIND_LABEL` chính là hàm sinh nhãn và có chứa `' (Bán)'`. Test
  `AS-10` không bắt được vì nó chỉ quét DOM **tại một trạng thái không có event SELL**.

### F-T13-E2-02 — HARDENING — Bằng chứng persistence `T-09B` không còn chạy lại được; `npm test` đỏ

- **Đường production:** không có defect production. `persist()`/`renderPersistence()`/
  `validateState()`/`reconcileMirror()` **không đổi một dòng**; hành vi `CHECK-T09B-16` được
  reviewer **kiểm trực tiếp và PASS** (§23c).
- **Bằng chứng tái lập:** sáu file test V2.1.5 fail tại `#seedFile`;
  `npm --prefix webapp test` exit khác 0; `CHECK-T09B-16` không được suite nào phủ sau `T-13`.
- **Hậu quả:** một Completion Gate đã đóng băng và `DONE` (`T-09B`) mất khả năng **chạy lại** bằng
  chứng production-reachability; lệnh test mặc định đã khai của `webapp/` đỏ, nên nếu ai đó dùng
  nó làm cổng CI thì cổng đó vô nghĩa.
- **Vì sao KHÔNG `BLOCKING`:** không hành vi production nào sai (đã kiểm trực tiếp); không REQUIRED
  check nào của `T-13` bị vi phạm — `CHECK-T13-12` đòi `test_t12_*.js` + Python PASS và **không**
  test cũ nào bị bỏ chọn/skip: cả hai đều đạt. Việc gỡ `#tab-setup` có thẩm quyền (Step-B spec §12).
- **RE_TRIGGER_CONDITION:**
  - mở bước **C** (`H-42`, Firebase project riêng) — bước đó cần bằng chứng persistence chạy lại
    được để chứng minh không regression; **hoặc**
  - `npm --prefix webapp test` được dùng làm cổng release/CI; **hoặc**
  - một thay đổi chạm `reconcileMirror`/`pushDiverged`/`dropDiverged`/`persist`.
- **Quan hệ:** cùng họ với `H-44` (bằng chứng nằm ở tầng harness chậm nhất và không được nối vào
  `scripts.test`). **Không** hợp nhất, **không** đánh ID mới — Owner định đoạt.

### F-T13-E2-03 — HARDENING (nhỏ) — "Định giá hiện tại" hiện NGÀY thay vì TUỔI của giá

- **Đường production:** `webapp/ledger_ui.js:202`.
- **Bằng chứng:** `DASH/priceMark-validity-16.3` — UI hiện `"— · giá gần nhất 2026-03-08"`; spec
  kế toán §16.3 và Step-B spec §4.2 ghi hiển thị `—` kèm **tuổi** của giá ("giá gần nhất: 12 ngày
  trước").
- **Hậu quả:** người dùng phải tự tính số ngày. Không sai số, không ngoại suy, không ảnh hưởng bất
  kỳ phép tính giá vốn/kế hoạch nào (định giá là `DESCRIPTIVE`).
- **Vì sao KHÔNG `BLOCKING`, và KHÔNG làm FAIL `CHECK-T13-02`:** yêu cầu đóng băng của
  `CHECK-T13-02` là khớp tolerance 0 với `derive()` + không GO/WAIT; `valuation = null` không phải
  một con số của `derive()` để đối chiếu, và `—` đã hiện đúng.
- **RE_TRIGGER_CONDITION:** khi một Completion Gate tương lai đòi đích danh định dạng "N ngày
  trước", hoặc khi định giá thôi là `DESCRIPTIVE`.

### F-T13-E2-04 — OBSERVATION (độ chính xác tài liệu, không phải defect sản phẩm)

Ba tuyên bố trong `docs/reviews/T13-IMPLEMENTATION-REPORT.md` không đứng vững trước kiểm chứng:

1. **§14** dẫn `Step-B spec §12 dòng "Nạp dữ liệu lịch sử"` — dòng đó **không tồn tại**. Thẩm
   quyền đúng là dòng `nav.tabs 5 tab cũ (dash/entry/ladder/history/setup)` (§23b).
2. **§14** viết *"toàn bộ **16 kịch bản** persistence/migration của `test_t12_browser.js`"* — file
   đó có **17** kết quả, trong đó chỉ **5** là kịch bản persistence. Và nó **không** phủ
   `CHECK-T09B-16` (§23c).
3. **§12** ghi AS-01/AS-08 xác nhận *"nextPlannedDate/**Amount** theo scheduleDays/**carry**"* —
   `test_stepb_ui.js` **không assert `nextPlannedAmountVnd`** (chỉ assert ngày, dòng 145) và
   fixture của nó có `plan.startMonth = '2026-03'` = tháng hiện tại ⇒ **`carryIn = 0`**, tức
   **carry chưa từng được chạy**. Reviewer đã bù bằng kịch bản `carryIn = 14.000.000` (§5, §9).
   Tương tự, `PR-6` của file đó chỉ grep compound-assignment (§10).

Không định tuyến thành `HARDENING` vì không chạm production path; ghi lại để Owner biết mức tin
cậy thật của bằng chứng E1 và để phiên sau không trích dẫn lại con số sai.

### Bảo toàn hardening hiện có

`H-44`, `H-45`, `H-46`, `H-47` — **giữ nguyên tuyệt đối**. Reviewer không sửa, không gộp, không
rút gọn, không mở rộng `RE_TRIGGER_CONDITION` của mục nào. `webapp/ledger.js` = **0 dòng đổi**
(§22), nên không mục nào bị chạm ở tầng dữ liệu. `H-45` giữ nguyên biên: reviewer xác nhận UI
không rò rỉ `realizedFxVnd` và **không** dựng thêm điều kiện kích hoạt mới (§18).

---

## 25. Completion Gate Matrix

13 REQUIRED check. Cột "E2 độc lập" chỉ ghi kết quả do **reviewer** tái lập.

| CHECK | Yêu cầu (rút gọn) | E2 bắt buộc? | Tái lập độc lập của reviewer | Kết quả |
|---|---|---|---|---|
| T13-01 | IA 4 điểm đến, refresh-safe, không markup V2.1.5 | không | `NAV/4-destinations+fab`, `NAV/hash-survives-refresh`, `NAV/back-forward-no-corruption` | PASS |
| **T13-02** | Dashboard đúng Contract §16, tolerance 0 | **CÓ** | §5 — 5 thẻ + phụ đề carry + 6 mục khối dưới + không GO/WAIT, trên trạng thái **có carry thật** | **PASS (E2)** |
| **T13-03** | Sheet ánh xạ đúng các loại sự kiện | **CÓ** | §6 — 8/8 ánh xạ trên durable state; `note` toàn khoảng trắng bị chặn; 1 ô tỷ giá duy nhất thuộc `PRICE` | **PASS (E2)** |
| T13-04 | Lịch sử filter/search/chi tiết/UNKNOWN badge | không | §15 — 14 event, 6 bộ lọc loại, khoảng ngày, tìm ghi chú, reset, chi tiết | PASS |
| **T13-05** | Sửa qua UI, `id`/`seq` bất biến | **CÓ** | §7 — `id`/`seq`/`events.length` bất biến; khớp ngay; **sống sót reload** | **PASS (E2)** |
| **T13-06** | Xoá: cảnh báo + snapshot bắt buộc trước | **CÓ** | §8 — snapshot bit-exact trước xoá; `derive()` = sổ chưa từng có event; **huỷ ⇒ giữ nguyên**; cảnh báo riêng cho opening | **PASS (E2)** |
| **T13-07** | Kế hoạch/Carry ba đại lượng tách riêng | **CÓ** | §9 — `carryIn = 14.000.000` thật; `carryOut` tháng đóng vs `null` tháng mở; `nextPlanned` theo lịch, tolerance 0 | **PASS (E2)** |
| T13-08 | UNKNOWN nhất quán, không tự ẩn | không | §18 — `—`, banner thường trực, 0 nút ẩn, không key "đã đọc" | PASS |
| T13-09 | SELL ẩn hoàn toàn | không | §14 — 0 SELL/Bán ở form/menu, 0 realized P&L, 0 đường hash | PASS (kèm `F-T13-E2-01`) |
| **T13-10** | Không công thức mới, một `derive()` | **CÓ** | §10 — đúng 1 `L.derive(`; 0 ghi thẳng state; quét rộng chỉ còn 1 biểu thức = bề rộng thanh tiến trình được spec cho phép | **PASS (E2)** |
| T13-11 | Di động ≤3 chạm, không cuộn ngang | không | §19 — 390px `scrollWidth = clientWidth`, 3 chạm, touch target ≥24px | PASS |
| T13-12 | Hồi quy `T-12` không vỡ | không | §22 — 32/32, 7/7 KILLED, owner PASS, 17/17 browser, Python (§22), 0 test bị sửa/bỏ chọn | PASS (kèm `F-T13-E2-02`) |
| **T13-13** | Production Reachability PR-1…PR-6 qua UI mới | **CÓ** | §11, §21 — 32 ghi bền thật, 45 kiểm chứng, reload tolerance 0, 0 page error | **PASS (E2)** |

**13/13 REQUIRED PASS. 7/7 check `E2_REQUIRED` PASS ở mức E2 độc lập.**

---

## 26. Final E2 Verdict

    E2_VERDICT = PASS

Cả bảy check bắt buộc E2 độc lập — `CHECK-T13-02`, `CHECK-T13-03`, `CHECK-T13-05`,
`CHECK-T13-06`, `CHECK-T13-07`, `CHECK-T13-10`, `CHECK-T13-13` — PASS khi được tái lập bởi một
reviewer không phải implementer, bằng kịch bản độc lập, trên đúng HEAD `cb75d6c`, qua đúng đường
sản xuất (`app_final.html` + Firestore Emulator + `firestore.rules` thật), với oracle `T-12` và
tolerance 0.

`T-13` giữ nguyên **`IMPLEMENTED`**, chờ Owner đóng vòng đời. Reviewer **không** đánh dấu `DONE`.

Ba finding mới đều là `HARDENING` (`F-T13-E2-01/02/03`) cộng một `OBSERVATION` tài liệu
(`F-T13-E2-04`). **Không finding `BLOCKING`.** Không finding nào đòi sửa production code, nên
**không** chạm tới repair authority: `CAP-WEBAPP` vẫn `allowed = 2 / used = 1 / remaining = 1`,
**không đổi** bởi phiên này.

---

## 27. Exact Owner Next Action

Đúng một quyết định thuộc về Owner, và ba việc ghi sổ đi kèm:

1. **Đóng vòng đời `T-13`:** chấp nhận `E2_VERDICT = PASS` và ghi một Owner Decision chuyển
   `T-13: IMPLEMENTED → DONE`, cùng khuôn `DEC-046` đã dùng cho `T-12`
   (`STATE_AUTHORITY.md` § The State Machine And Who May Write It). Reviewer không được làm việc
   này.

2. **Định đoạt ba finding HARDENING.** Chúng là *finding*, **không** phải task; việc cấp mã `H-*`
   và ghi vào `PROJECT/HARDENING_BACKLOG.md` thuộc phiên có thẩm quyền backlog, không thuộc phiên
   review này:
   - `F-T13-E2-01` — nhãn `Mua ETH (Bán)` (`ledger_ui.js:142`), gắn với `H-46`;
   - `F-T13-E2-02` — mất bằng chứng persistence `T-09B` + `npm test` đỏ, cùng họ `H-44`;
   - `F-T13-E2-03` — "Định giá hiện tại" hiện ngày thay vì tuổi giá.

3. **Ghi nhận `F-T13-E2-04`** (ba tuyên bố quá lời trong `T13-IMPLEMENTATION-REPORT.md`) để phiên
   sau không trích dẫn lại, đặc biệt con số "16 kịch bản persistence" và tuyên bố AS-08 phủ carry.

4. **Nếu Owner muốn đóng luôn khoảng trống bằng chứng** (`F-T13-E2-02`) trước bước C: đó là công
   việc **mới**, cần thẩm quyền riêng — `CAP-WEBAPP` chỉ còn `remaining = 1` repair cycle và
   reviewer **không** tự cấp. Không mở bước C (`H-42`) hay bước D (`OWNER_LOCAL_ACCEPTANCE`) từ
   báo cáo này.

Cảnh báo **"dừng dùng app với tiền thật không giới hạn"** vẫn còn hiệu lực: `T-13` chỉ hoàn tất
bước **B**; bước **C** (`H-42`, Firebase isolation) và bước **D** (`OWNER_LOCAL_ACCEPTANCE`) chưa
mở.

---

## Phụ lục — Bằng chứng chạy lại được

| Tệp | Nội dung |
|---|---|
| `docs/reviews/evidence/T13/reviewer-e2-part1.js` | Script reviewer phần 1 (25 kiểm chứng): carry, dashboard, ánh xạ 9 loại, sửa/xoá, PR-4/5, `CHECK-T13-10`, SELL guard |
| `docs/reviews/evidence/T13/reviewer-e2-part2.js` | Script reviewer phần 2 (20 kiểm chứng): UNKNOWN, History 14 event, priceMark §16.3, navigation/mobile 390px, `CHECK-T09B-16` |
| `docs/reviews/evidence/T13/reviewer-e2-part1-results.json` | Kết quả phần 1 — 24 PASS / 1 FAIL, `pageErrors: []` |
| `docs/reviews/evidence/T13/reviewer-e2-part2-results.json` | Kết quả phần 2 — 20 PASS / 0 FAIL, `pageErrors: []` |
| `docs/reviews/evidence/T13/sell-label-reachability.txt` | Tái lập `F-T13-E2-01` (nhãn `Mua ETH (Bán)`) |
| `docs/reviews/evidence/T13/money-math-suspects.txt` | Toàn bộ biểu thức số học chạm trường tiền trong `ledger_ui.js` (1 dòng) |
| `docs/reviews/evidence/T13/t12-browser-e2-rerun.txt` | `test_t12_browser.js` chạy lại — 17/17 PASS, `errors: []` |
| `docs/reviews/evidence/T13/stepb-ui-e2-rerun.txt` | `test_stepb_ui.js` chạy lại — 16/16 PASS (đối chiếu tuyên bố, không thay bằng chứng) |
| `docs/reviews/evidence/T13/pytest-e2.txt` | Kết quả `pytest` sau khi sửa môi trường shallow clone |

Lệnh tái lập:

    node webapp/build_app.js
    node docs/reviews/evidence/T13/reviewer-e2-part1.js
    node docs/reviews/evidence/T13/reviewer-e2-part2.js
    node webapp/test_t12_browser.js
    node --test webapp/test_t12_ledger.js
    node webapp/test_t12_mutations.js
    node webapp/test_t12_owner.js tests/fixtures/t12/owner-example.synthetic.json
    git fetch --unshallow && python3 -m pytest -q
