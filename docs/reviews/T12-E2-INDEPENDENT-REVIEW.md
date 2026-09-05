# T-12 Independent E2 Review

## 1. Executive Summary

Đây là **independent E2** cho `T-12` (sổ cái L-1 `coindca.ledger/2`), thực hiện trên nhánh
`codex/t12-l1-ledger-impl` tại `0cf24cad98e342a9070168d321461772ea0021e4`. Người review
**không** thi hành `T-12` và **không** kế thừa kết luận của implementer: mọi con số dưới đây
được tái lập lại từ đầu trong phiên này bằng oracle và harness do chính người review viết,
cộng với việc chạy lại toàn bộ evidence của implementer.

    E2_VERDICT = PASS

Chín check E2 bắt buộc (`CHECK-T12-02`, `-03`, `-04`, `-05`, `-06`, `-09`, `-10`, `-11`, `-12`)
đều PASS trên bằng chứng độc lập. `T12_GOLDEN_ACCOUNTING_BASELINE` toàn vẹn; fixture không
đổi một byte sau freeze. Không phát hiện sai lệch số tiền nào. Bốn finding được ghi, **không
finding nào là BLOCKING** theo `governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing:
không finding nào đòi sửa production code, đòi đổi ngữ nghĩa kế toán, hay đòi thêm repair cycle.

`T-12` giữ nguyên `IMPLEMENTED`. Người review **không** đặt `DONE` — đó là quyền của Owner.

Số liệu tái lập độc lập trong phiên này:

| Hạng mục | Kết quả người review đo được |
|---|---|
| Differential test WAC (oracle Python độc lập) | 400/400 case trùng tuyệt đối, `tolerance = 0` |
| Property test đường lành (bảo toàn VND, ROUND, cạn pool) | 300 case / 1.154 phép giải phóng, 0 vi phạm |
| Golden `SC-01`…`SC-12` | 12/12 PASS, đối chiếu tuyệt đối |
| `INV-1`…`INV-15` unit suite | 32/32 PASS |
| Mutation của implementer | 7/7 KILLED (chạy lại) |
| Mutation **độc lập** của người review | 14 mutant: 11 bị unit suite diệt, 2 bị production harness diệt, 1 chỉ khác baseline ở ca UNKNOWN cạn pool (→ `F-E2-02`) |
| Hoán vị thứ tự nhập | 300 hoán vị → `DerivedState` trùng bit |
| Múi giờ tiến trình | 6 giá trị `TZ` → digest trùng nhau |
| `P-1`…`P-6` (harness của implementer) | PASS, exit 0, 10 event thật |
| `P-1`…`P-6` (**kịch bản riêng của người review**) | PASS, exit 0, 10 event thật tạo qua UI, 9 event cuối |
| Python regression | 678 ca thu thập lại đúng bằng claim; bề mặt Python **0 thay đổi** trong `T-12`; xem §22 |

## 2. Reviewer Independence

- Người review **không** viết một dòng nào của `webapp/ledger.js` / `webapp/ledger_ui.js`.
- Working tree sạch trong suốt phiên; `git status --porcelain` rỗng sau khi review xong.
  Không sửa production code, không sửa golden fixture, không sửa spec, không sửa `DEC-041`…`045`.
- Mọi mutation thử nghiệm chạy trên **bản sao** trong scratchpad
  (`/tmp/.../scratchpad/e2/mut`, `/tmp/.../scratchpad/mutroot`), không trên repo.
- Oracle đối chiếu là **hai nguồn độc lập với cài đặt**:
  1. một bản replay viết bằng Python thuần chỉ từ công thức spec §6.3/§6.4/§6.5/§7.3;
  2. tính tay số nguyên cho toàn bộ kịch bản production của người review (§20).
- `test_t12_fixtures.js` chỉ được dùng làm **input**; số kỳ vọng được kiểm lại từng dòng
  đối chiếu nguyên văn spec §19 (§4).

## 3. Source / Branch / Commit

    repository            hoangvinhkta-creator/coin
    branch                codex/t12-l1-ledger-impl
    HEAD reviewed         0cf24cad98e342a9070168d321461772ea0021e4
    implementation/repair 2a2ab3f52c38eb30a0a8e0ee1791a95254ee9847
    golden freeze         c610a299ed6b66dea3cd63372a0943967c93e95d
    main                  KHÔNG đọc, KHÔNG merge

Branch authority check (`governance/scripts/governance/branch_authority_check.sh
--expect-branch codex/t12-l1-ledger-impl`):

    behind upstream   = 0
    ahead of default  = 6 commit(s)
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: PASS

Công cụ dùng cho bằng chứng phiên này: Node v22.22.2, Python 3.11.15, Playwright 1.56.1 +
Chromium `/opt/pw-browsers/chromium`, Firebase CLI 15.28.2 / SDK 12.18.0 theo `package-lock.json`,
JRE hệ thống cho Firestore Emulator, project `demo-ethdca`, `firestore.rules` **thật** của repo.
Không chạm Firebase production. Chỉ dữ liệu tổng hợp; không dùng dữ liệu tài chính thật của Owner.

Ranh giới đã kiểm lại độc lập:

    firestore.rules / firebase.json diff 91cfbba..HEAD   = RỖNG
    production diff 91cfbba..HEAD (5 file khai báo)      = +460 / -7
    document Firestore                                   = ethdca/state, ethdca/seed (không tạo mới)
    ENGINE / engine.js trong ledger.js, ledger_ui.js      = 0 tham chiếu
    PRODUCTION_PATHS.md §1                                = có webapp/ledger.js và webapp/ledger_ui.js

## 4. Golden Baseline Integrity

`T12_GOLDEN_ACCOUNTING_BASELINE = c610a299ed6b66dea3cd63372a0943967c93e95d` — **XÁC NHẬN**.

Định nghĩa trong task: "SHA của commit ĐẦU TIÊN trên nhánh thi hành `T-12` đưa đủ 12 fixture
`SC-01`…`SC-12` (dữ liệu vào + số kỳ vọng, khớp NGUYÊN VĂN spec §19) vào dưới dạng file test
đã commit."

    git log --all -- webapp/test_t12_fixtures.js
      -> đúng MỘT commit: c610a29

    git rev-parse c610a29:webapp/test_t12_fixtures.js  = e4c709843ee58e85c5a496ec7083e71330f1f8a4
    git rev-parse HEAD:webapp/test_t12_fixtures.js     = e4c709843ee58e85c5a496ec7083e71330f1f8a4
    git diff --stat c610a29..0cf24ca -- webapp/test_t12_fixtures.js  -> RỖNG

Fixture **không đổi một byte** sau freeze.

Kiểm toàn vẹn nội dung `SC-01`…`SC-12` (đối chiếu từng dòng với spec §19, `DEC-044`, `DEC-045`;
người review tự quy đổi đơn vị: VND đồng nguyên, micro-USDT, ETH 1e-8):

| SC | Kỳ vọng spec §19 | Fixture | Kết luận |
|---|---|---|---|
| SC-01 | ETH 0,5 / 1.200 USDT / 30.000.000; USDT 200 / 5.000.000; avg 2.400, 60.000.000, 25.000 | 50000000 / 1200000000 / 30000000; 200000000 / 5000000; ratio đúng | TRÙNG |
| SC-02 | usdtQty 1.200 · cost 30.600.000 · avg 25.500 | 1200000000 / 30600000 | TRÙNG |
| SC-03 | relief 15.315.300 · ETH 0,75 / 1.800,6 / 45.315.300 · pool 599,4 / 15.284.700 · remaining 4.684.700 | y hệt | TRÙNG |
| SC-04 | relief 12.909.178 · ETH 0,95 / 2.300,6 / 58.224.478 · pool 599,4 / 15.475.522 · carryIn 4.684.700 · planned 24.684.700 · remaining 11.775.522 (`DEC-044`) | y hệt | TRÙNG |
| SC-05 | ETH 0,94 · costUsdt/costVnd KHÔNG đổi · pool KHÔNG đổi | y hệt | TRÙNG |
| SC-06 | relief 12.750.000 · ETH costVnd 58.065.300 · pool 99,4 / 2.534.700 | y hệt | TRÙNG |
| SC-07 | relief muộn 2.581.836 và 12.909.178 · pool 499,4 · invested T2 15.491.014 | y hệt | TRÙNG |
| SC-08 | currentMonth 2026-03 · invested 6.000.000 · carryOut(2026-02) 20.000.000 · carryIn 20.000.000 | y hệt | TRÙNG |
| SC-09 | perSlot [6.666.667, 6.666.667, 6.666.666] · 17.000.000 / 12.000.000 / 8.000.000 · next 2026-03-23 · A: carryOut null · B: 8.000.000 (`DEC-045`) | y hệt, hai evaluation | TRÙNG |
| SC-10 | reserve 6.000.000 · 21.000.000 / 12.000.000 / 8.000.000 · A carryOut null · B 8.000.000 | y hệt, hai evaluation | TRÙNG |
| SC-11 | invested T3 17.000.000 · ETH 0,36 · planInvested T4 5.000.000 · carryOut null · flag FUTURE_DATED_EVENTS | y hệt | TRÙNG |
| SC-12 | ETH 0,275 / 660 USDT / costVnd UNKNOWN · USDT 340 / UNKNOWN · flag UNKNOWN_VND_BASIS | y hệt (`costVnd: null`) | TRÙNG |

Người review **không** viết lại fixture, **không** nới `tolerance`. `tolerance = 0` được xác
nhận là ràng buộc thật: mọi so sánh trong `test_t12_ledger.js` và trong harness của người
review dùng `assert.deepStrictEqual` / so sánh số nguyên, không có epsilon.

Kiểm bổ sung: `test_t12_owner.js` từ chối chạy nếu `tolerance` khác 0; chạy với fixture tổng hợp
`tests/fixtures/t12/owner-example.synthetic.json` → `OWNER_LOCAL_ACCEPTANCE: PASS`, exit 0.
Không dùng dữ liệu thật của Owner.

## 5. CHECK-T12-02 — `openingPosition + events -> derive()` tất định

**Yêu cầu (nguyên văn task).** `derive()` là hàm thuần (không `new Date()` bên trong, không đọc
`createdAt`), cùng tập event cho cùng `DerivedState` dưới ≥ 100 hoán vị thứ tự nhập và ≥ 2 `TZ`
tiến trình khác nhau. Phủ `INV-2`, `INV-6`. Golden `SC-04`, `SC-07`, `SC-08`.

**Phương pháp độc lập.**

1. Đọc mã: trích riêng thân `derive()` và grep `new Date|Date.now|getMonth|toISOString` → 0 kết quả.
2. **Đầu độc đồng hồ**: thay `global.Date` bằng constructor ném lỗi và `Date.now` ném lỗi, rồi
   gọi `derive()` trên một ledger 10 event (TREASURY hai chiều, BUY PLAN/EXTRA/RESERVE, RESERVE
   CONTRIBUTE, PRICE) — `derive()` chạy xong và trả đúng kết quả nền.
3. **300 hoán vị** ngẫu nhiên mảng event (gấp 3 lần ngưỡng 100) → `deepStrictEqual` với nền, 300/300.
4. **6 giá trị `TZ` tiến trình** (`UTC`, `America/Los_Angeles`, `Pacific/Kiritimati`,
   `Pacific/Midway`, `Asia/Ho_Chi_Minh`, `Europe/Berlin`; offset từ −840 đến +660) chạy trong
   **6 tiến trình Node riêng**, băm SHA-256 `DerivedState` của 13 cặp (scenario × asOfDate).
5. Kiểm `derive()` không mutate input (so chuỗi JSON trước/sau).
6. Đổi `createdAt`/`updatedAt` của mọi event sang giá trị bất kỳ (`2999-…`, `1971-…`) → không đổi.

**Bằng chứng quan sát được.**

    Date bị đầu độc            -> derive() không gọi -> PASS
    300 hoán vị                -> 300/300 trùng bit
    6 TZ × 13 digest           -> tất cả digest bằng nhau
    clock('2026-02-28T18:30Z') -> '2026-03-01' ở CẢ 6 TZ tiến trình
    derive() mutate input      -> KHÔNG

**Ca đối kháng.** Mutant độc lập `E2-M-I` (đổi khoá sắp xếp thành `createdAt`) — xem §16 và §23.
Mutant `E2-M-C` (currentMonth = tháng lớn nhất trong dữ liệu) bị `SC-09`/`SC-10`/`SC-11` diệt.

**Kết luận: PASS.**

## 6. CHECK-T12-03 — Giá vốn VND: WAC trên một pool USDT, đúng số

**Yêu cầu.** `vndRelieved = ROUND_VND(usdtOut × usdtCostVnd / usdtQty)`; giữ bình quân lý thuyết
**trước** lượng tử VND; sau `ROUND_VND` bình quân dẫn xuất từ `(C − vndRelieved) / (Q − usdtOut)`
(`DEC-045` Group A); không lưu bình quân cũ; không phần dư ẩn; không tolerance bổ sung; phí USDT
vào cả hai giá vốn; bán crypto/bán USDT giải phóng theo cùng phương pháp; cạn pool ép
`usdtCostVnd = 0` và đẩy phần dư vào `realizedFxVnd`. `tolerance = 0` với `SC-01`…`SC-04`, `SC-06`.
Phủ `INV-3`.

**Phương pháp độc lập.**

1. **Oracle Python viết lại từ spec**, không import `ledger.js`, dùng số nguyên Python vô hạn
   và `ROUND_VND` tự cài (nửa lên theo độ lớn).
2. **Differential test 400 case** sinh ngẫu nhiên (seed cố định 20260905): opening ngẫu nhiên
   (kể cả pool rỗng, cost `null`), 1–10 event trộn TREASURY hai chiều, BUY (PLAN/EXTRA/RESERVE)
   có/không phí, SELL, RESERVE CONTRIBUTE/WITHDRAW. So sánh 8 đại lượng cuối kỳ **và** toàn bộ
   `eventEffects` từng event.
3. **Property test 300 case đường lành** (không over-draw, basis biết): kiểm bốn tính chất
   **không** lấy từ cài đặt mà từ định nghĩa kế toán:
   - `ROUND_VND` từng phép: `vndRelieved == ROUND(out × C_trước / Q_trước)` tính lại độc lập;
   - bảo toàn: `C_cuối + Σ relief BUY + Σ relief USDT_TO_VND + Σ phần dư khi cạn == C_đầu + Σ vndAmount vào`;
   - `realizedFxVnd == Σ vndAmount(USDT_TO_VND) − Σ relief(USDT_TO_VND) + Σ phần dư cạn pool`;
   - `usdtQty == 0 ⟺ usdtCostVnd == 0`.
4. Tính tay `SC-04` bằng BigInt độc lập trong test riêng.
5. Kiểm `DEC-045`: `usdt.avgVnd` sau `SC-04` phải đúng bằng `{15.475.522 × 10^6 ; 599.400.000}`
   và `canonical(state)` không chứa bất kỳ khoá `avg`/`Avg` nào.

**Bằng chứng quan sát được.**

    Differential 400 case      -> 0 sai lệch, 0 exception
      độ phủ: 24 case cạn pool, 217 case có SELL, 316 case UNKNOWN, 348 case LEDGER_INCONSISTENT
    Property 300 case          -> 1.154 phép giải phóng kiểm ROUND, 0 vi phạm
      43 case cạn pool -> C == 0 tuyệt đối, phần dư = 0, không đồng nào sống sót
    SC-04 tính tay             -> (2×500.000.000×28.384.700 + 1.099.400.000) / (2×1.099.400.000)
                                  = 12.909.178 ; C' = 15.475.522 ; Q' = 599.400.000
    DEC-045 avg sau ROUND      -> numerator/denominator đúng C'/Q', không lưu bình quân cũ
    khoá 'avg' trong durable   -> 0
    phí USDT                   -> SC-03 usdtOut = 600,6 -> relief 15.315.300 (mutant bỏ phí bị diệt)

**Ca đối kháng.**

- Mutant `E2-M-A` (`ROUND_VND` → cắt cụt) bị `SC-04`/`SC-05`/`SC-06`/`SC-07` diệt.
- Mutant `E2-M-J` (phí USDT không vào giá vốn) bị `SC-03`…`SC-06` diệt.
- Cạn pool bằng `USDT_TO_VND` đúng bằng số dư: `usdtCostVnd = 0`, `realizedFxVnd = 100.000`.
- Bán ETH khi pool USDT rỗng: xem finding `F-E2-03` (§23) — hành vi **đúng spec**, không phải lỗi cài đặt.

**Kết luận: PASS.**

## 7. CHECK-T12-04 — `UNKNOWN` lan truyền thấy được, không bao giờ bị ép về 0

**Yêu cầu.** `openingPosition.usdt.costVnd = null` → `qty` và `costUsdt` giữ nguyên đúng, phần
`costVnd` liên quan = `UNKNOWN`, hiển thị `—`, cờ `UNKNOWN_VND_BASIS` thường trực và **không ẩn
được bằng một lần bấm**. Grep schema chứng minh **không tồn tại** trường tỷ giá nhập theo từng
lệnh. Phủ `INV-11`. Golden `SC-12`.

**Phương pháp độc lập.**

1. `derive()` với `usdt.costVnd = null` + một BUY có phí → kiểm 8 trường.
2. Chuỗi 40 event (P2P + BUY xen kẽ) trên pool UNKNOWN → kiểm `null` không bị "chữa" ở đâu.
3. Thêm event `PRICE` có `usdVndRate` → kiểm `PRICE` **không** được dùng làm FX fallback.
4. Grep `vndRateOverride|fxOverride|rateOverride|impliedRate` trong `ledger.js` và `ledger_ui.js`.
5. Grep `canonical()` allowlist: thử tiêm 7 khoá dẫn xuất/FX vào state và vào event.
6. Đọc `ledger_ui.js`: cờ được render lại ở **mỗi lần** `render()` vào `#l1Flags` (role=alert),
   không có nút ẩn/đóng, không có `dismiss`/`hidden` cho phần tử này.
7. Migration `W-1` (§18) — `SC-12` chạy qua đường production thật (§20).

**Bằng chứng quan sát được.**

    UNKNOWN + BUY 600,6 USDT:
      ETH.qty        = 25.000.000        (đúng, không đổi)
      ETH.costUsdt   = 600.600.000       (đúng, không đổi)
      ETH.costVnd    = null              (KHÔNG bị ép 0)
      ETH.avgCostVnd = null
      usdt.costVnd   = null
      month.investedThisMonthVnd     = null
      month.planInvestedVnd          = null
      month.remainingPlannedBudgetVnd= null
      flags          = ["UNKNOWN_VND_BASIS"]
    40 event trên pool UNKNOWN     -> vẫn null, qty và costUsdt vẫn đúng, cờ vẫn còn
    PRICE(usdVndRate = 25.500)     -> costVnd vẫn null (KHÔNG có FX fallback)
    grep trường FX theo lệnh       -> 0 kết quả ở cả hai module
    tiêm vndRateOverride vào event -> canonical() ném "Trường không canonical"
    UI                             -> units(null) trả '—'; avg(null) trả '—'

**Ca đối kháng.** Mutant `E2-M-E` (ép `null → 0` trong `portion`) bị `SC-12` **và** test `INV-11`
diệt. Một ca biên được ghi lại làm finding `F-E2-02` (§23): sau khi **cạn sạch** một pool
UNKNOWN bằng `USDT_TO_VND`, cờ biến mất — hệ quả hẹp, không làm sai một con số nào đang hiển thị.

**Kết luận: PASS** (kèm finding HARDENING `F-E2-02`).

## 8. CHECK-T12-05 — Sửa / xoá / nhập muộn tính lại đúng, không trôi

**Yêu cầu.** Sửa giữ `id`+`seq`, cập nhật `updatedAt`, chạy lại toàn bộ; **không tồn tại** phép
"hoàn tác tác động cũ" trong mã; xoá cứng TƯƠNG ĐƯƠNG CHÍNH XÁC với chưa từng nhập; nhập muộn xếp
theo `businessDate` chứ không theo lúc nhập. Phủ `INV-1`, `INV-15`. Golden `SC-05`, `SC-06`, `SC-07`.

**Phương pháp độc lập.**

1. 20 lần `update({type:'event', id})` liên tiếp → kiểm `id`, `seq`, `createdAt` bất biến,
   `updatedAt` đổi, giá trị cuối đúng.
2. Grep `revert|undo|reverse|rollbackEffect|unapply` trong `ledger.js` → 0 kết quả; đọc lại
   `derive()` xác nhận nó **replay toàn bộ** từ `openingPosition` mỗi lần, không cộng dồn.
3. **Xoá cứng ≡ chưa từng nhập**: với **từng** event trong ledger 10 event, xoá event đó rồi so
   `deepStrictEqual(derive(sau xoá), derive(tập không có event đó))` — 10/10 trùng tuyệt đối;
   đồng thời kiểm `nextSeq` **không** bị hạ.
4. Xoá rồi tạo mới → `id` mới ≠ id đã xoá, `seq` mới = watermark, không tái sử dụng.
5. **Ca nhập muộn có tính phân biệt** (điều mà `SC-07` một mình không phân biệt được — xem §23
   `F-E2-01`): pool 100 USDT @25.000; BUY 10/01; **P2P 20/01 ở tỷ giá 30.000**; BUY nhập muộn
   `businessDate = 15/01` với `seq` lớn nhất. Nếu xếp theo `seq`/`createdAt`, lệnh muộn sẽ giải
   phóng ở bình quân đã trộn.
6. Lặp lại ca nhập muộn **qua đường production thật** (§20).

**Bằng chứng quan sát được.**

    20 edit                -> id, seq, createdAt bất biến; updatedAt đổi; qty cuối đúng
    grep phép hoàn tác     -> 0
    xoá từng event (10 ca) -> DerivedState trùng tuyệt đối với "chưa từng nhập"; nextSeq giữ 11
    xoá rồi tạo            -> seq 11, id mới, id cũ không quay lại
    nhập muộn phân biệt:
      xếp theo businessDate (thực tế)  -> relief lệnh muộn = 1.250.000 (bình quân 25.000 TRƯỚC P2P)
      xếp theo seq/createdAt (mutant)  -> relief lệnh muộn = 1.416.667, pool cuối 2.833.333
      => cài đặt đúng: 1.250.000, pool cuối 3.000.000
    production path (§20)  -> lệnh muộn 16/01 nhập SAU CÙNG vẫn giải phóng ở bình quân
                              25.666,6667 của thời điểm 16/01, TRƯỚC P2P 18/01

**Ca đối kháng.** Mutant `E2-M-B` (bỏ `businessDate` khỏi khoá sắp xếp) và `E2-M-I` (sắp theo
`createdAt`) — cả hai **bị `test_t12_browser.js` diệt** tại oracle `P-4`
(`holdings.ETH.costVnd` = `null` thay vì `64.351.292`), nhưng **sống sót** unit suite; ghi lại
làm `F-E2-01`. Mutant `E2-M-H` (sửa cấp lại `seq`) bị `INV-15` diệt.

**Kết luận: PASS** (kèm finding HARDENING `F-E2-01`).

## 9. CHECK-T12-06 — Ngày nghiệp vụ, `Asia/Ho_Chi_Minh`, tháng lịch

**Yêu cầu.** `businessDate` là chuỗi, so sánh chuỗi, `month = slice(0,7)`; **đúng một** chỗ trong
toàn bộ mã hỏi giờ hệ thống và nó trả ngày theo `Asia/Ho_Chi_Minh`; `currentMonth` = tháng của
`asOfDate`, KHÔNG phải khoá tháng lớn nhất trong dữ liệu; `carryOut` chỉ chốt cho tháng đã đóng;
grep chứng minh không còn `getMonth()`/`toISOString()` trong đường tính tiền. Phủ `INV-6`.
Golden `SC-08`, `SC-11`. Đóng `B3`, `B4`, `B7` của `H-41`.

**Phương pháp độc lập.**

1. Grep `new Date|Date.now|getMonth()|getFullYear()|toISOString()|toLocaleDate` trong
   `ledger.js` + `ledger_ui.js`.
2. Truy vết mọi `new Date()`/`getMonth()` còn lại trong `app_logic.js`: liệt kê mọi lời gọi
   `canWrite(...)` và kiểm cổng khoá.
3. `clock()` với 4 instant biên, chạy dưới **6 `TZ` tiến trình**.
4. `currentMonth` với dữ liệu tháng 5 nhưng `asOfDate` tháng 2.
5. `carryOut` mở/đóng tháng: `SC-09`/`SC-10` evaluation A và B (`DEC-045` Group B).
6. Trần `CAPPED_CARRY` qua 5 tháng rỗng.
7. Tháng nhuận + clamp `scheduleDays` + `nextMonth('2026-12')`.

**Bằng chứng quan sát được.**

    ledger.js/ledger_ui.js: DUY NHẤT ledger.js:58-59 hỏi giờ hệ thống, và nó dùng
      Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Ho_Chi_Minh' })
    derive(): 0 kết quả cho new Date | Date.now | getMonth | toISOString
    app_logic.js: ba hàm mutator legacy duy nhất — addP2P():206, addBuy():246, addDay():298 —
      chỉ có đúng ba call site: :1295, :1320, :1334, và cả ba nằm SAU canWrite("pxMsg"),
      canWrite("p2pMsg"), canWrite("buyMsg"); seed :1362 và import/wipe :1422/:1442 cũng vậy.
      canWrite() nay có 'if (msgId) return false;' -> toàn bộ đường ghi tài chính legacy CHẾT,
      nên mọi new Date()/getMonth()/toISOString() còn lại trong app_logic.js là mã không
      tới được từ đường tính tiền L-1.
      render() mount CoinLedgerUI rồi 'return' TRƯỚC recompute()/renderDash() legacy.
      persist() bỏ qua nếu state.schema !== coindca.ledger/2.
    clock, ở CẢ 6 TZ tiến trình:
      2026-02-28T16:29:59Z -> 2026-02-28
      2026-02-28T17:00:00Z -> 2026-03-01   (biên UTC+7 chính xác)
      2026-02-28T18:30:00Z -> 2026-03-01   (SC-08)
      2026-12-31T17:00:00Z -> 2027-01-01
    currentMonth: dữ liệu 2026-05, asOfDate 2026-02-15 -> currentMonth = '2026-02',
      invested tháng 2 = 0, months['2026-05'].planInvestedVnd = 6.000.000,
      months['2026-05'].carryInVnd = null (tháng tương lai KHÔNG ăn carry),
      month.carryOutVnd = null, flags chứa FUTURE_DATED_EVENTS
    carryOut: SC-09 A (18/03) và SC-10 A (21/03) -> carryOutVnd = null, remaining 8.000.000
              SC-09 B / SC-10 B (01/04)          -> carryOut(2026-03) = 8.000.000,
                                                    carryIn(2026-04) = 8.000.000
    CAPPED_CARRY: 5 tháng rỗng -> carryIn luôn = 20.000.000 (đúng trần 1×), planned 40.000.000
    2028-02 (nhuận), scheduleDays [3,29,31] -> slot clamp+dedup = 2 mốc, split [15,15]
    nextMonth('2026-12') = '2027-01'

**Ca đối kháng.** Mutant `E2-M-K` (đổi múi giờ sang `UTC`) bị `SC-08` và test `INV-6` diệt.
Mutant `E2-M-C` (currentMonth = tháng lớn nhất) bị `SC-09`/`SC-10`/`SC-11` diệt.
Mutant `E2-M-D` (chốt `carryOut` cho tháng đang mở) bị `SC-09`/`SC-10` diệt.

**Kết luận: PASS.**

## 10. CHECK-T12-09 — `INV-1`…`INV-15` được phủ, không bất biến REQUIRED nào bỏ trống

**Yêu cầu.** Mỗi dòng của ma trận `INV` có **ít nhất một test nhắm đích thực sự đỏ khi bất biến
bị phá**, chứng minh bằng mutation/nghịch đảo có chủ đích cho tối thiểu `INV-1`, `INV-3`, `INV-4`,
`INV-9`, `INV-11`, `INV-12`, `INV-14`. Không `INV` nào chỉ được phủ gián tiếp bởi một `SC`.

**Phương pháp độc lập.**

1. Chạy lại `node --test webapp/test_t12_ledger.js` → 32/32 PASS.
2. Chạy lại mutation harness của implementer → 7/7 KILLED, 0 survivor.
3. **Viết 14 mutant riêng** (không trùng bộ 7 của implementer), áp vào **bản sao** `ledger.js`
   trong scratchpad, chạy toàn bộ unit suite trên bản sao.
4. Với mutant sống sót: dựng probe để chứng minh mutant **không tương đương**, rồi chạy mutant
   qua `test_t12_browser.js` (bản sao repo trong scratchpad, có build lại `app_final.html`).
5. Đối chiếu từng dòng ma trận `INV` với tên test cụ thể.

**Bằng chứng quan sát được.**

    Bộ 7 mutation bắt buộc (chạy lại độc lập):
      INV-1  KILLED   INV-3  KILLED   INV-4  KILLED   INV-9  KILLED
      INV-11 KILLED   INV-12 KILLED   INV-14 KILLED     -> 7/7, 0 survivor

    Bộ 14 mutant ĐỘC LẬP của người review:
      E2-M-A ROUND_VND -> cắt cụt                 KILLED (SC-04/05/06/07)
      E2-M-B bỏ businessDate khỏi khoá sắp xếp    sống sót unit suite, KILLED bởi test_t12_browser.js
      E2-M-C currentMonth = tháng lớn nhất        KILLED (SC-09/10/11)
      E2-M-D chốt carryOut cho tháng đang mở      KILLED (SC-09/10)
      E2-M-E ép UNKNOWN về 0 khi giải phóng       KILLED (SC-12, INV-11)
      E2-M-F bỏ quy tắc phần dư khi cạn pool      sống sót — xem phân tích dưới
      E2-M-G nhận event trước openingPosition     KILLED (INV-7)
      E2-M-H sửa cấp lại seq                      KILLED (INV-15)
      E2-M-I sắp xếp theo createdAt               sống sót unit suite, KILLED bởi test_t12_browser.js
      E2-M-J phí USDT không vào giá vốn           KILLED (SC-03..06)
      E2-M-K múi giờ -> UTC                       KILLED (SC-08, INV-6)
      E2-M-L SPLIT_VND bỏ phần dư                 KILLED (SC-09, INV-13)
      E2-M-M tôn trọng derivedSnapshot khi import KILLED (INV-1)
      E2-M-N ghi trước khi snapshot               KILLED (INV-14)

    Phân tích `E2-M-F`: quy tắc §6.5 ép `usdtCostVnd = 0` khi cạn pool là **thừa** trong đường
    basis-biết, vì `portion(out, C, Q)` với `out == Q` cho đúng `C` (BigInt: `(2QC+Q)/(2Q) = C`),
    nên `C − relief = 0` sẵn. Mutant chỉ khác baseline khi pool có basis UNKNOWN — đó chính là
    finding `F-E2-02`. Nó KHÔNG chứng tỏ `INV-3` thiếu test: `INV-3` được kiểm cả bằng
    mutation bắt buộc (KILLED) lẫn 43 ca cạn pool trong property test của người review.

    Ma trận INV -> test nhắm đích trực tiếp (không chỉ qua SC):
      INV-1  test 13   INV-2  test 14   INV-3  test 15   INV-4  test 16   INV-5  test 17
      INV-6  test 18   INV-7  test 19   INV-8  test 20   INV-9  test 21   INV-10 test 22
      INV-11 test 23   INV-12 test 24   INV-13 test 25   INV-14 test 26   INV-15 test 27
      (SC-01..SC-12 = test 1..12; test 28..32 là các ca bổ sung update/calendar/migration)
    15/15 dòng có phép khẳng định trực tiếp; không dòng nào chỉ dựa vào một SC.

**Ca đối kháng.** Hai mutant sống sót unit suite (`E2-M-B`, `E2-M-I`) đều bị **diệt** bởi
`test_t12_browser.js`, tức khoá sắp xếp `(businessDate, seq)` **có** được một test trong bộ
evidence `T-12` giữ. Điểm yếu là nó chỉ được giữ ở tầng harness chậm (emulator + Playwright),
không ở unit suite — ghi lại làm `F-E2-01` (HARDENING, `RE_TRIGGER_CONDITION` ở §23).
Theo `REVIEW_PROTOCOL.md` § "The BLOCKING Test, Stated Negatively": *"only makes the evidence
nicer -> not BLOCKING"*. Hành vi production đã được xác nhận ĐÚNG bằng ca phân biệt độc lập ở §8.

**Kết luận: PASS** (kèm finding HARDENING `F-E2-01`).

## 11. CHECK-T12-10 — Hợp đồng migration PASS, gồm dữ liệu mơ hồ

**Yêu cầu.** (a) snapshot legacy được ghi TRƯỚC mọi thao tác ghi; (b) phát hiện version tất định;
(c) phân loại §17.2 áp đúng, `trades[].vndRate/vndCost` bị bỏ và tính lại; (d) đối chiếu §17.3
trong ngưỡng, vượt ngưỡng ⇒ FAIL; (e) `M-1`…`M-4` ⇒ DỪNG, durable không đổi một byte;
(f) `W-1` ⇒ HOÀN TẤT kèm cờ `UNKNOWN_VND_BASIS`, không bịa tỷ giá; (g) legacy không bị xoá,
`ledger[]` chỉ đọc; (h) không `Base`/`Smart`/`Opportunity`/`ladder`/`zone`/`score` nào lọt vào
sự thật tài chính L-1.

**Phương pháp độc lập.** 9 ca đối kháng viết riêng trên `L.migrate` + `L.destructive`, cộng với
kịch bản migration chạy **qua đường production thật** (§20).

**Bằng chứng quan sát được.**

    W-1 (fixture SC-12):
      ok = true, warnings = ['W-1','UNKNOWN_VND_BASIS']
      ETH.qty 27.500.000 · ETH.costUsdt 660.000.000 · ETH.costVnd null
      usdt.qty 340.000.000 · usdt.costVnd null · flags [UNKNOWN_VND_BASIS]
      unknownBasis: 4 dòng, mỗi dòng nêu chỉ số legacy (`trades[0..3]`), lý do
        "USDT pool thiếu giá vốn VND đã biết; không suy tỷ giá từ legacy hay PRICE."
        và đường sửa DUY NHẤT "Sửa openingPosition.usdt.costVnd tường minh hoặc bổ sung
        event TREASURY còn thiếu; không nhập FX riêng từng lệnh."
      LEGACY_ARCHIVE.raw === legacy nguyên văn (deepStrictEqual)
      Quét chuỗi JSON của {plan, openingPosition, events}: 0 lần xuất hiện
        src, recPrice, shortfallBps, zone, ladder, score, BASE, SMART, OPPORTUNITY,
        oppFund, vndRate, vndCost
      Mọi TRADE migrate đều source = 'EXTRA'

    M-1 thiếu `contributions`                    -> STOP, không state
    M-1 thiếu xác nhận ngày một dòng             -> STOP
    M-1 ngày sai định dạng (2026-13-40)          -> STOP
    M-1 `order` không nguyên (1.5)               -> STOP
    M-1 `order` trùng nhau                       -> STOP
    M-2 over-draw pool (trades[0].usdt = 900)    -> STOP, errors[0] bắt đầu bằng 'M-2'
    M-3 lệch oracle ETH (0,275 -> 0,9)           -> STOP, deltas.eth.deltaUnits ≠ 0
    M-4 zone đã phát tác (filled_vnd = 1)        -> STOP
    Nguyên tử: chạy M-1 / M-3 / M-4 qua L.destructive
      -> commit gọi 0 lần; snapshot gọi 3/3 lần; nguồn legacy không đổi một byte (so chuỗi JSON)
    Thứ tự bắt buộc: snapshot -> confirm -> (commit); huỷ ở confirm vẫn giữ snapshot,
      order quan sát được = ['snapshot','confirm'] và KHÔNG có 'commit'
    Schema legacy không hỗ trợ                   -> STOP ngay ('Schema legacy không hỗ trợ')

    Qua đường production (§20 và harness implementer):
      putDoc legacy -> reload -> UI khoá ghi L-1, hiện form xác nhận ngày/thứ tự
      -> snapshot tải về TRƯỚC -> migrate -> server ACK -> reload
      M-1/M-2/M-3/M-4: getDoc('state') sau mỗi lần thử == legacy raw, không đổi một byte

**Ca đối kháng.** Mutant `E2-M-N` (ghi trước snapshot) bị `INV-14` diệt.

**Kết luận: PASS.**

## 12. CHECK-T12-11 — Round-trip persistence giữ nguyên sự thật sổ cái

**Yêu cầu.** Ghi → máy chủ xác nhận → đọc lại từ SERVER → `derive()` cho `DerivedState` trùng
tuyệt đối; payload durable không chứa khoá dẫn xuất bị cấm; file export có `derivedSnapshot` thì
import **bỏ qua** khối đó (kiểm bằng file export bị sửa tay); sổ nằm trong `ethdca/state` đã
allow-list, **không** tạo document mới.

**Phương pháp độc lập.** Người review viết **harness riêng** (`e2_browser.js`) dùng
`test_firebase_harness.js` chỉ như hạ tầng (emulator + `firestore.rules` thật + `app_final.html`
đã build), với kịch bản và oracle của riêng mình; đọc lại state qua **REST admin của emulator**
(Node → emulator), không qua promise của SDK trong trang.

**Bằng chứng quan sát được.**

    ghi 9 event + opening qua UI -> waitSaved (durableRev == rev) -> getDoc REST
      deepStrictEqual(server, mirror trong trang)                       -> TRÙNG TUYỆT ĐỐI
    reload -> replay -> readState                                        -> TRÙNG TUYỆT ĐỐI
    Object.keys(payload server).sort()
      = ['events','nextSeq','openingPosition','plan','rev','schema']     -> đúng allowlist
    quét 21 khoá dẫn xuất bị cấm trong payload server                    -> 0
      (avgCostVnd, avgCostUsdt, usdtAvgVnd, investedThisMonthVnd, remainingPlannedBudgetVnd,
       plannedBudgetVnd, carryInVnd, carryOutVnd, realizedFxVnd, vndRelieved, holdings,
       eventEffects, derivedSnapshot, vndRateOverride, price, rate, recPrice, zone,
       ladders, oppFund, src)
    quét đệ quy float trong payload server                               -> 0
    file export SỬA TAY có derivedSnapshot {ETH.qty 999999999}
      -> snapshot đầy đủ được ghi TRƯỚC import
      -> payload server sau import KHÔNG có 'derivedSnapshot'
      -> dashboard sau import trùng từng chuỗi với trước import          -> tiền KHÔNG trôi
    document Firestore chạm tới: ethdca/state, ethdca/seed (có sẵn)      -> không tạo mới
    firestore.rules diff 91cfbba..HEAD                                   -> RỖNG

Bốn ca tấn công persistence còn lại được tái lập bằng cách chạy lại harness của implementer
(exit 0 trong phiên này, xem §20):

    rev cũ (stale rev)     tab cũ ghi -> lastError 'stale-durable'; server giữ revision mới hơn
    schema hỏng            'unsupported/999' -> phase CORRUPT, khoá ghi, export raw đầy đủ,
                           KHÔNG wipe, KHÔNG backfill
    rules từ chối          permission-denied -> app KHÔNG báo đã lưu; REST không đổi;
                           retry sau khi khôi phục rules -> ACK, event tăng đúng 1
    reload / restart trình duyệt cùng profile -> giữ UID Anonymous, nạp lại từ server bit-exact
    offline                chỉ xem mirror, chip 'KHÔNG GHI SỔ', server không đổi

**Ca đối kháng.** Event dị dạng và event trước `openingPosition.asOf` được đẩy qua **đường ghi
thật của app**: bị từ chối tại `#l1Message`, và `getDoc('state')` **không đổi một byte** (§21).
Mutant `E2-M-M` (tôn trọng `derivedSnapshot`) bị `INV-1` diệt.

**Kết luận: PASS.**

## 13. CHECK-T12-12 — Production Reachability PASS

**Yêu cầu.** `P-1`…`P-6` đo trên `app_final.html` đã build qua `webapp/test_firebase_harness.js`
(Playwright + Firestore Emulator + rules thật). Báo cáo phải nêu **số event thật** và **số case**.
`0 event / 0 case = FAIL`. Mọi file runtime MỚI phải được khai vào `PRODUCTION_PATHS.md` §1.

**Phương pháp độc lập.** Hai lần đo, **không** thay bằng unit test:

- (A) chạy lại nguyên harness của implementer `webapp/test_t12_browser.js`;
- (B) chạy **kịch bản riêng của người review** (`e2_browser.js`) với oracle **tính tay** riêng.

**Bằng chứng quan sát được — (A) harness implementer, chạy lại trong phiên này, exit 0:**

    [harness] emulators up (auth :9099, firestore :8080, rules = firestore.rules)
    PASS P-1/P-2, P-3, P-4, P-5, P-6
    PASS INV-1/14 import · SC-12 production · Migration M-1, M-2, M-3, M-4
    PASS INV-14 hủy wipe · Persistence offline · rejected write/retry · stale rev
    PASS Persistence corrupt/version · Persistence browser restart
    realEventsCreated = 10 · pageErrors = []

**Bằng chứng quan sát được — (B) kịch bản độc lập của người review, exit 0:**

    P-1  app_final.html phục vụ qua HTTP, Firebase SDK compat thật, emulator + rules thật.
         Kịch bản (B) KHÔNG `require('./ledger')` một lần nào: mọi giá trị đo đến từ DOM đã
         render và từ REST của emulator, oracle đến từ Python/tính tay. Nhờ vậy (B) khép luôn
         mọi nghi ngờ còn lại về P-1 ở kịch bản (A) — nơi `L.derive` được dùng làm phép đối
         chiếu phụ BÊN CẠNH một oracle hằng số tính tay và bên cạnh chuỗi hiển thị trên DOM.
    P-2  10 event thật tạo qua đường ghi của chính app (9 còn lại sau khi xoá 1):
           1 × openingPosition
           3 × TREASURY  (2 × VND_TO_USDT, 1 × USDT_TO_VND)
           3 × TRADE source=PLAN   (gồm 1 nhập muộn)
           1 × TRADE source=EXTRA
           1 × TRADE source=RESERVE (có note "giai ngan du phong E2")
           1 × RESERVE CONTRIBUTE
           1 × PRICE (đã xoá ở P-3)
    P-3  1 sửa (qty 0,08 -> 0,075: id/seq/createdAt bất biến),
         1 xoá cứng (snapshot tải về TRƯỚC khi durable đổi),
         1 nhập muộn businessDate 2026-01-16 nhập sau cùng, TRƯỚC P2P 2026-01-18.
    P-4  Mọi thao tác chờ server ACK (durableRev == rev), rồi đọc lại
         ethdca/state qua REST admin: deepStrictEqual với mirror -> TRÙNG TUYỆT ĐỐI.
    P-5  reload -> derive() chạy lại -> dashboard so với oracle TÍNH TAY (tolerance = 0):
           Ngân sách tháng          20.000.000    (oracle 20.000.000)
           Carry từ tháng trước              0    (0)
           Đã đầu tư                25.425.400    (25.425.400)
           Theo kế hoạch            21.575.400    (21.575.400)
           Còn lại theo kế hoạch             0    (max(0, 20.000.000 − 21.575.400) = 0)
           Dự phòng                 12.433.333    (15.000.000 − 2.566.667)
           ETH                           0,701    (0,3+0,25+0,04+0,075+0,02+0,016)
           Giá vốn TB ETH (USDT)  2.411,69757489  (1.690,6 / 0,701)
           Giá vốn TB ETH (VND) 61.234.522,11126962 (42.925.400 / 0,701)
           USDT                          609,4    (609,4)
           Giá vốn pool USDT (VND)  16.385.764    (16.385.764)
           VND                     171.000.000    (200.000.000 − 26.000.000 − 6.000.000 + 3.000.000)
         Chuỗi giải phóng tính tay, khớp từng đồng:
           05/01 P2P +1000 USDT / +26.000.000 -> 1.500 USDT / 38.500.000 (25.666,6667)
           06/01 BUY out 600,6  -> 15.415.400
           09/01 BUY 100 RESERVE ->  2.566.667
           13/01 BUY 200 (đã sửa qty) -> 5.133.333
           15/01 BUY  50 EXTRA  ->  1.283.333
           16/01 BUY  40 (NHẬP MUỘN) -> 1.026.667   <- bình quân TRƯỚC P2P 18/01
           18/01 P2P +200 USDT / +6.000.000 -> 709,4 / 19.074.600
           20/01 P2P-out 100 USDT -> 2.688.836 ; realizedFx 311.164
           pool cuối 609,4 USDT / 16.385.764 VND
    P-6  payload durable đọc từ SERVER: 6 khoá allowlist, 0 khoá dẫn xuất bị cấm, 0 float.

    Số event thật qua đường production: 10 (A) + 10 (B) = 20. Số case: 17 (A) + 6 (B).
    0 event / 0 case: KHÔNG xảy ra.

    File runtime MỚI đã khai trong PRODUCTION_PATHS.md §1:
      webapp/ledger.js      -> có
      webapp/ledger_ui.js   -> có
    Không file runtime mới nào chưa khai (khiếm khuyết H-32 KHÔNG lặp lại).

**Kết luận: PASS.**

## 14. WAC Adversarial Review

Ngoài §6, các mũi tấn công riêng và kết quả:

| Mũi tấn công | Kết quả |
|---|---|
| Pool USDT WAC nhiều lô nhiều tỷ giá | 400 case differential, 0 sai lệch; WAC trộn đúng, không cần ghép lô |
| `ROUND_VND` chính xác | 1.154 phép giải phóng kiểm lại bằng số nguyên Python, 0 sai |
| `DEC-045` bình quân sau lượng tử | `avgVnd` luôn dẫn xuất từ `(C−relief)/(Q−out)`; không lưu bình quân; 0 khoá `avg` trong durable |
| Cạn pool một phần | 300 case property, `C` giảm đúng phần giải phóng, không phần dư |
| Cạn pool hoàn toàn | 43 + 24 case; `usdtCostVnd = 0` tuyệt đối; phần dư vào `realizedFxVnd`; toán học cho thấy phần dư luôn = 0 khi basis biết |
| SELL ETH | 217 case; giải phóng theo cùng WAC; `ethCostUsdt`/`ethCostVnd` giảm theo tỷ lệ; USDT thu về nhập pool ở bình quân hiện hành đúng spec §6.3 |
| `USDT_TO_VND` | `realizedFxVnd = vndAmount − vndRelieved` đúng công thức §6.4 trên mọi case |
| Phí USDT | vào `usdtOut` và **cả hai** giá vốn; mutant bỏ phí bị diệt |
| Phần dư ẩn | Không tồn tại tài khoản dư nào; đẳng thức bảo toàn VND đúng tuyệt đối trên 300 case |
| Bình quân lưu trữ | `canonical()` allowlist chặn; tiêm `avgCostVnd`/`usdtAvgVnd` bị ném lỗi |
| Tràn số | `integer()` chặn `> 9×10^15` và mọi giá trị không `Number.isSafeInteger`; trung gian dùng `BigInt` nên không mất chính xác; `round(9e15 × 8999999999999999, 9e15)` trả đúng |
| Bán ETH khi pool USDT rỗng | Basis mới = `UNKNOWN` (không bịa tỷ giá) — **đúng `DEC-042`**; ghi nhận `F-E2-03` |
| `round()` với tử số âm | Làm tròn nửa **ra xa 0**, spec ghi "nửa lên"; chỉ chạm được khi cost âm, tức đã `LEDGER_INCONSISTENT`; ghi nhận `F-E2-04` |

## 15. UNKNOWN Adversarial Review

| Mũi tấn công | Kết quả |
|---|---|
| `UNKNOWN` bị ép về 0 | Không, trên mọi đường: `add`/`sub`/`portion`/`ratio` đều lan `null` |
| FX hiện hành làm fallback | Không có mã đọc tỷ giá hiện hành ở đâu trong `derive()` |
| FX theo từng lệnh | `vndRateOverride`/`fxOverride`/`rateOverride`/`impliedRate` = 0 kết quả; allowlist chặn khi tiêm |
| `PRICE.usdVndRate` bị dùng chữa basis | Không; `PRICE` chỉ vào `valuation`, không vào cost |
| `qty` sai khi UNKNOWN | Không; `qty` và `costUsdt` giữ đúng qua 40 event |
| Cờ `UNKNOWN_VND_BASIS` ẩn được | Không có nút ẩn; render lại mỗi lần `render()`; `role="alert"` |
| Cờ biến mất sau khi cạn pool UNKNOWN | **CÓ** trong một ca hẹp — `F-E2-02` |
| `UNKNOWN` trong migration | `W-1` hoàn tất, không bịa tỷ giá, báo cáo từng dòng legacy (§11) |
| `openingPosition.usdt.costVnd = 0` với `qty > 0` | Được chấp nhận (0 là khai báo tường minh của người dùng, UI phân biệt rõ "để trống = chưa biết" với "0"). Không phải fallback ẩn; ghi nhận là quan sát, không phải khiếm khuyết |

## 16. Edit/Delete/Late Entry

Xem §8. Bổ sung:

- **Replay toàn phần, không mutation gia tăng**: `derive()` dựng lại từ `openingPosition` mỗi lần
  gọi; không có biến trạng thái nào sống ngoài lời gọi; grep không tìm thấy phép hoàn tác.
- **`nextSeq` là high-watermark**: `canonical()` từ chối `e.seq >= s.nextSeq`; `delete` không hạ
  watermark (kiểm 10/10 ca); `update` chỉ tăng.
- **`id` không tái sử dụng**: `crypto.randomUUID()` trong `ledger_ui.meta()`, và `canonical()`
  từ chối `id` trùng.
- **Sửa `openingPosition` vượt event**: `update({type:'opening'})` chạy `canonical()` cuối cùng,
  nên đặt `asOf` sau `businessDate` của một event đang có sẽ **bị từ chối**, không âm thầm nhận.

## 17. Timezone/Calendar

Xem §9. Bổ sung: `businessDate` được so sánh **bằng chuỗi** (`localeCompare`) và tháng lấy bằng
`slice(0,7)`; toàn bộ số học lịch (`daysInMonth`, `nextMonth`, `previousDay`, năm nhuận) viết
bằng số nguyên trên chuỗi, không dựng `Date` nào. `dateValid` từ chối `2026-02-30`, `2026-13-01`,
`2026-1-6`, `0000-01-01`, `2026-01-32` và chấp nhận `2028-02-29`.

## 18. Migration

Xem §11. Kết luận riêng cho từng yêu cầu (a)–(h) của `CHECK-T12-10`:

    (a) snapshot trước mọi ghi        PASS — thứ tự quan sát được: snapshot -> confirm -> commit
    (b) phát hiện version tất định    PASS — chỉ nhận `ethdca.tracker/1`, khác thì STOP ngay
    (c) phân loại §17.2               PASS — vndRate/vndCost/recPrice/shortfallBps/zone bị bỏ và
                                      tính lại; trade legacy luôn source = EXTRA
    (d) đối chiếu §17.3               PASS — 4 oracle (eth, usdt, vnd, costUsdt), ngưỡng ±1 đơn vị
                                      nhỏ nhất; fixture cố ý lệch -> M-3 FAIL
    (e) M-1..M-4                      PASS — 8 ca, durable/nguồn không đổi một byte, 0 commit
    (f) W-1                           PASS — hoàn tất + UNKNOWN_VND_BASIS + 4 dòng chẩn đoán
    (g) legacy giữ nguyên             PASS — LEGACY_ARCHIVE.raw === legacy; ledger[] chỉ đọc
    (h) không rò rỉ chiến lược        PASS — 12 chuỗi cấm quét trên phần tài chính -> 0

## 19. Persistence

Xem §12. Bổ sung: `ledger_ui.destroy()` luôn chụp `hooks.raw() || hooks.state()`, tức snapshot là
**payload durable thô**, không phải bản đã chuẩn hoá — đúng cho ca legacy/corrupt. `L.destructive`
không bao giờ gọi `commit` khi `operation()` trả `ok: false`, và không bao giờ gọi `commit`
khi người dùng huỷ ở `confirm()`.

## 20. Production Reachability

Xem §13. Ghi rõ theo yêu cầu của gate:

    Số event thật chạy qua đường production trong phiên E2 này = 20
      (10 từ harness implementer chạy lại + 10 từ kịch bản riêng của người review)
    Số case chạy qua đường production trong phiên E2 này       = 23
    Anti-vacuity: KHÔNG có 0 event / 0 case.
    Unit suite KHÔNG được dùng để thay thế P-1..P-6.

## 21. Malformed/Range Cases

13 nhóm ca, tất cả PASS:

| Nhóm | Ca | Kết quả |
|---|---|---|
| Thiếu trường bắt buộc | 13 trường bị xoá lần lượt | 13/13 bị từ chối |
| Trường tài chính lạ | `vndRate`, `vndCost`, `price`, `avgCostVnd`, `zone`, `src`, `score`, … | 8/8 bị từ chối (allowlist, không phải blocklist) |
| Enum sai | `kind`, `side`, `source=BASE`, `symbol=BTC`, `dir`, `RESERVE.type` | 6/6 bị từ chối |
| Lượng âm/0/thập phân/ngoài miền | `-1`, `0`, `0.5`, `NaN`, `Infinity`, `1e17`, `MAX_SAFE_INTEGER`, `'100'`, `null`, `undefined` | 10/10 bị từ chối; phí âm/thập phân/ngoài miền 3/3 bị từ chối |
| Ngày dị dạng | 10 chuỗi gồm `2026-02-30`, `2026-13-01`, `2026-1-6`, `0000-01-01`, ISO đầy đủ | 10/10 bị từ chối; `2028-02-29` được nhận |
| Trùng `id` / trùng `seq` / vượt watermark | 3 ca | 3/3 bị từ chối |
| `INV-7` event trước `openingPosition.asOf` | qua `derive` và qua `canonical` | 2/2 bị từ chối, có lý do |
| Opening không đầy đủ | cost khi qty = 0 (ETH và USDT), `asOf` sai, symbol lạ, note sai kiểu, qty âm | 6/6 bị từ chối |
| `source = RESERVE` không note | note toàn khoảng trắng | bị từ chối |
| Thiếu tiền tố (INV-4) | over-draw ở giữa nhưng cuối sổ dương | `LEDGER_INCONSISTENT` + `firstOffendingEventId` = event ĐẦU TIÊN, app KHÔNG tự sửa dữ liệu |
| `SPLIT_VND` | 120 số × `n = 1..12` (1.440 phép), cùng `n = 0`, `n = 32`, `amount` thập phân | tổng đúng tuyệt đối 1.440/1.440; 3 ca biên bị từ chối |
| Float trong durable | quét đệ quy toàn bộ 12 state fixture + payload server thật | 0 float |
| Qua đường ghi THẬT của app | `qty = -1`; `businessDate` trước opening | bị từ chối tại UI, `getDoc('state')` **không đổi một byte** |

## 22. Regression/N-A Review

`CHECK-T12-13` **không** nằm trong chín check E2 bắt buộc của phiên này, nhưng §8 của yêu cầu
review đòi đánh giá phê phán claim regression. Người review đã làm ba việc.

### 22.1 Bề mặt Python KHÔNG đổi — kiểm bằng git, không bằng lời

    git diff --name-status 91cfbba..HEAD -- src/eth_dca_os tests pyproject.toml pyproject.lock
      A  tests/fixtures/t12/owner-acceptance.schema.json
      A  tests/fixtures/t12/owner-example.synthetic.json
      (KHÔNG có dòng M/D nào)

`src/eth_dca_os/**` = 0 thay đổi. `pyproject.toml` / `pyproject.lock` = 0 thay đổi, nên
`addopts`, `testpaths` và bản ghim dependency giữ nguyên. Không có `pytest.ini` / `setup.cfg` /
`tox.ini` / `conftest.py` ở gốc. Hai file thêm vào là **fixture JSON**, không phải module test,
không được pytest thu thập. Kết luận: **không test Python nào bị sửa, xoá, `skip`, `xfail` hay
`deselect`**; claim "không đổi test nào của `src/eth_dca_os`" đứng vững.

### 22.2 Số ca thu thập — tái lập độc lập

    PYTHONPATH=src pytest --collect-only -q  ->  total collected = 678

Đúng bằng con số implementer báo (678). Chạy đầy đủ `pytest` được khởi động trong phiên E2 này
bằng venv riêng (`pip install -e ".[dev]"`); tại thời điểm chốt báo cáo, lượt chạy vẫn đang tiếp
diễn với **0 `F` và 0 `E`** trong output tiến trình. Người review **không** tuyên bố đã tự tay
xác nhận 678/678 PASS; điều đã xác nhận độc lập là (a) 678 ca được thu thập, (b) bề mặt Python
byte-identical với baseline trước `T-12`, (c) không có failure nào trong phần đã chạy. Vì
`T-12` không chạm một dòng Python nào, kết quả suite không thể khác baseline vì `T-12`.

### 22.3 Npm — người review KHÔNG chấp nhận N/A trọn gói

Chạy lại **cả sáu** script của `npm test` độc lập trong phiên này:

| Script | Exit | Điểm dừng quan sát được |
|---|---|---|
| `test_app.js` | 1 | `test_app.js:36` — bước 1 "nạp seed" (`#seedFile`), `durableRev: null` |
| `test_zone.js` | 1 | `newPage(..., {seed:true})` — `waitSaved timeout`, `durableRev: null` |
| `test_v01_v02_v03.js` | 1 | `V-02 — unlock vs reserve` — cùng chữ ký |
| `test_multi_month_invariant.js` | 1 | `newPage(..., {seed:true})` — cùng chữ ký |
| `test_t09a_accounting.js` | 1 | `CA 1 — release đa tháng` — cùng chữ ký |
| `test_t09b_persistence.js` | 1 | `test_t09b_persistence.js:148` — cùng chữ ký |

**Cùng MỘT chữ ký ở cả sáu**: `waitSaved timeout` với `phase: ONLINE`, `lastError: null`,
`durableRev: null` — tức app **online, không lỗi**, chỉ là **không có gì được ghi**. Nguyên nhân
gốc đã truy được đến đúng một dòng: `canWrite(msgId)` nay trả `false` cho mọi `msgId`, nên seed
legacy và mọi handler tài chính legacy không ghi nữa (§9). Đây là **tiền đề legacy**, không phải
một khẳng định về persistence hay kế toán bị đỏ. Sáu log lưu trong
`docs/reviews/evidence/T12/npm-after-*.txt` mang đúng chữ ký này.

**Neo quyết định.** 22 dòng N/A ở báo cáo implementer §20 đều có phạm vi **từng ca** (không N/A
cả file) và đều mô tả hành vi đã bị `DEC-041` B/F/K.2 và `DEC-042` §3/§4 gỡ bỏ: pool
Base/Smart/Opportunity, ladder/zone, OSCORE/parity, `recPrice`, `vndRate` theo từng lệnh,
Smart unlock. Đó đúng là hành vi V2.1.5 đã đóng băng; không được đòi nó PASS
(`AGENTS.md` §4, `DEC-041` A.2 "không còn là spec sản phẩm").

**Phần persistence CÒN áp dụng không bị bỏ trắng.** Mọi ngữ nghĩa `T-09B` còn hiệu lực dưới
schema mới đã được người review **chạy thật** trong phiên này (§12, §13): server ACK + đọc lại
từ SERVER qua REST, `rev`/stale rev, `permission-denied` + retry, offline chỉ xem mirror, khởi
động lại trình duyệt cùng profile, schema lạ → `CORRUPT` + export raw không wipe, và
import/wipe/migration/delete đều có snapshot trước. Không ngữ nghĩa persistence nào bị chuyển
thành N/A mà thiếu bằng chứng thay thế **chạy được**.

**Đánh giá.** Cách phân loại N/A của implementer **đứng vững** dưới kiểm tra độc lập. Người
review không thấy lý do phản đối trạng thái PASS đã ghi cho `CHECK-T12-13`.

## 23. Findings

Không finding nào là `BLOCKING`. Phân loại theo `governance/v4/CORE/REVIEW_PROTOCOL.md`
§ Finding Routing. **Finding không phải task.** Người review **không** tạo task ID, **không**
tự sửa, **không** tiêu repair cycle thứ hai.

---

### `F-E2-01` — Khoá sắp xếp `(businessDate, seq)` chỉ được unit suite giữ gián tiếp

    Phân loại        HARDENING
    Trạng thái       CONFIRMED (bằng mutation trên bản sao, không sửa repo)
    Production path  webapp/ledger.js (derive, khoá sắp xếp)
    Hậu quả hiện tại KHÔNG — hành vi production đã được xác nhận ĐÚNG (§8, §13)

**Mô tả.** Hai mutant độc lập — `E2-M-B` (sắp xếp chỉ theo `seq`) và `E2-M-I` (sắp xếp theo
`createdAt` rồi `seq`) — **sống sót cả 32 test** của `webapp/test_t12_ledger.js`. Nguyên nhân:

- fixture `SC-07` không phân biệt được thứ tự, vì giải phóng WAC theo tỷ lệ **giữ nguyên bình
  quân**, nên hai lệnh mua rút từ cùng một pool cho cùng con số dù đảo thứ tự (đã kiểm: cả hai
  thứ tự đều cho `2.581.836` và `12.909.178`);
- test `INV-6` gán `createdAt = '2001-01-0<i>'` **theo đúng thứ tự mảng**, tức trùng thứ tự `seq`,
  nên "đổi `createdAt` sang giá trị bất kỳ" không thực sự đảo thứ tự.

**Tái lập.**

    # ca phân biệt (không có trong fixture đã đóng băng)
    opening: 100 USDT / 2.500.000 VND (25.000)
    seq 1  2026-01-10  BUY 50 USDT
    seq 2  2026-01-20  P2P +100 USDT / +3.000.000 VND (30.000)
    seq 3  2026-01-15  BUY 50 USDT      <- nhập muộn, seq lớn nhất
    thực tế (đúng):      relief(seq 3) = 1.250.000 ; pool cuối 3.000.000
    E2-M-B / E2-M-I:     relief(seq 3) = 1.416.667 ; pool cuối 2.833.333

**Giảm nhẹ đã có.** Cả hai mutant **bị `webapp/test_t12_browser.js` diệt** tại oracle `P-4`
(`holdings.ETH.costVnd`: `null` thay vì `64.351.292`, exit 1). Nên khoá sắp xếp **có** được một
test trong bộ evidence `T-12` giữ — nhưng chỉ ở tầng harness emulator + Playwright.

**Điều làm rủi ro này lớn hơn vẻ ngoài của nó.** `webapp/package.json` § scripts.test vẫn chỉ
liệt kê sáu script legacy; **không script `test_t12_*.js` nào được nối vào `npm test`**. Nghĩa là
hôm nay: (i) `npm test` không chạy một test kế toán L-1 nào; (ii) test duy nhất giữ khoá sắp xếp
là script chậm nhất, phải gọi tay và cần emulator + Chromium. Người review nêu điều này như một
sự thật quan sát được, **không** đề xuất sửa `package.json` trong phiên E2 (đó là thay đổi
production/tooling, ngoài thẩm quyền review).

**Vì sao KHÔNG BLOCKING.** `REVIEW_PROTOCOL.md` § "The BLOCKING Test, Stated Negatively":
*"only makes the evidence nicer -> not BLOCKING"*. Không có hậu quả nghiệp vụ hiện tại;
`derive()` sắp xếp đúng và điều đó đã được xác nhận cả bằng probe trực tiếp lẫn qua đường
production.

    RE_TRIGGER_CONDITION
      (a) bất kỳ thay đổi nào chạm biểu thức sắp xếp trong derive(); HOẶC
      (b) test_t12_browser.js bị gỡ khỏi bộ evidence bắt buộc của T-12 / khỏi CI, hoặc bộ
          test_t12_*.js vẫn nằm ngoài npm test khi CAP-WEBAPP có lượt thi hành kế tiếp; HOẶC
      (c) lần tới có repair budget hợp lệ cho CAP-WEBAPP chạm webapp/ledger.js.
    KHẮC PHỤC ĐỀ XUẤT (khi có thẩm quyền): thêm ĐÚNG MỘT ca unit dùng ledger phân biệt ở trên.
      Không đổi fixture SC đã đóng băng, không đổi ngữ nghĩa kế toán.

---

### `F-E2-02` — Cờ `UNKNOWN_VND_BASIS` biến mất sau khi cạn sạch một pool UNKNOWN

    Phân loại        HARDENING
    Trạng thái       CONFIRMED (runtime, derive() trên production module)
    Production path  webapp/ledger.js (release/drain §6.5 + biểu thức đặt cờ)
    Hậu quả hiện tại HẸP — không con số nào đang hiển thị bị sai

**Mô tả.** Quy tắc §6.5 ép `usdtCostVnd = 0` khi `usdtQty` về 0. Khi basis là `UNKNOWN` (`null`),
quy tắc này biến `null` thành `0` và đẩy phần "dư" `null` vào `realizedFxVnd`. Nếu ledger không
có lệnh mua nào rút từ pool UNKNOWN (nên `invested` không có `null`) thì sau khi cạn pool,
biểu thức đặt cờ `[usdt.costVnd, eth.costVnd, reserve, ...invested].some(x => x === null)`
không còn phần tử `null` nào → `flags = []`, banner thường trực biến mất, trong khi
`realizedFxVnd = null` (thật sự không biết) **không** nằm trong biểu thức đặt cờ và cũng không
được UI hiển thị.

**Tái lập.**

    opening: usdt { qty: 100.000.000, costVnd: null }, ETH 0, reserve 0
    event:   2026-01-10 TREASURY USDT_TO_VND vndAmount 2.600.000 usdtAmount 100.000.000
    derive(..., '2026-02-01') ->
      usdt.costVnd   = 0      (UNKNOWN bị ép về 0 bởi quy tắc cạn pool)
      realizedFxVnd  = null   (thật sự UNKNOWN, không hiển thị ở đâu)
      flags          = []     (banner UNKNOWN_VND_BASIS biến mất)

**Vì sao KHÔNG BLOCKING.** Tại thời điểm đó mọi vị thế đều bằng 0, nên `costVnd = 0` không phải
một con số sai; đại lượng duy nhất còn UNKNOWN là lãi/lỗ tỷ giá đã thực hiện, mà spec §6.4 tuyên
bố L-1 chỉ "dừng ở mức mô tả" và `ledger_ui.js` không hiển thị `realizedFxVnd`. Không có Completion
Gate nào yêu cầu hiển thị đại lượng này. Chữ trong `CHECK-T12-04` ("phần `costVnd` **liên quan**"
và "cờ không ẩn được bằng một lần bấm") vẫn được thoả.

    RE_TRIGGER_CONDITION
      (a) L-1 (hoặc bước B/C/D) bắt đầu hiển thị realizedFxVnd hay bất kỳ P&L VND nào; HOẶC
      (b) xuất hiện yêu cầu "UNKNOWN phải nhìn thấy được kể cả khi vị thế = 0"; HOẶC
      (c) lần tới có repair budget hợp lệ chạm webapp/ledger.js.
    KHẮC PHỤC ĐỀ XUẤT (khi có thẩm quyền): thêm realizedFxVnd vào biểu thức đặt cờ. Một dòng.

---

### `F-E2-03` — Bán ETH có thể tạo/huỷ giá vốn VND; pool rỗng đẩy toàn bộ basis thành UNKNOWN

    Phân loại        HARDENING (khiếm khuyết ĐẶC TẢ, không phải lỗi cài đặt)
    Trạng thái       CONFIRMED
    Production path  webapp/ledger.js — nhưng hành vi ĐÚNG spec §6.3/§7.3 và ĐÚNG DEC-042
    Hậu quả hiện tại chỉ khi Owner thực sự bán ETH

**Mô tả.** Spec §6.3 quy định `TRADE SELL`: `usdtCostVnd += thu về × usdtAvgVnd`, và §7.3 phát
biểu **ý định** "để việc bán không tự tạo ra hay huỷ đi giá vốn VND". Hai điều này mâu thuẫn
với nhau khi `ethAvgVnd ≠ usdtAvgVnd`: công thức lấy bình quân của **pool USDT**, không phải giá
vốn VND vừa giải phóng khỏi ETH. Cài đặt **theo đúng công thức**, nên đây không phải lỗi
implementation.

**Tái lập.**

    opening: ETH 1,0 costVnd 50.000.000 ; USDT 1,0 costVnd 26.000
    bán 0,5 ETH lấy 1.200 USDT
      -> giải phóng khỏi ETH: 25.000.000 VND
      -> tạo trong pool USDT: 31.200.000 VND   (chênh 6.200.000 VND, không vào realizedFx)

    opening: ETH 1,0 costVnd 50.000.000 ; USDT 0 (pool RỖNG)
    bán 0,5 ETH lấy 1.200 USDT
      -> usdt.costVnd = null (bình quân của pool rỗng không xác định)
      -> flags = [UNKNOWN_VND_BASIS]

**Vì sao KHÔNG BLOCKING và vì sao E2 KHÔNG sửa.** Trường hợp pool rỗng: `DEC-042` §4 cấm tuyệt
đối bịa tỷ giá, nên `UNKNOWN` là câu trả lời **tuân thủ**, và nó fail-visible. Trường hợp chênh
lệch: sửa nó **là đổi ngữ nghĩa kế toán**, tức vượt hẳn thẩm quyền E2 và vượt điều kiện repair
của `DEC-043` ("no financial semantics from DEC-042/spec need to change"). Đây là hạng mục cho
Owner cân nhắc ở bước sau, không phải cho `T-12`.

    RE_TRIGGER_CONDITION
      (a) Owner bắt đầu dùng nghiệp vụ SELL trên dữ liệu thật; HOẶC
      (b) L-1 bước B/C/D mở sổ lãi/lỗ; HOẶC
      (c) một Owner Decision mở lại ngữ nghĩa §6.3/§7.3.
    KHÔNG được sửa trong T-12.

---

### `F-E2-04` — `ROUND_VND` với tử số âm làm tròn "nửa ra xa 0", spec ghi "nửa lên"

    Phân loại        HARDENING (defense-in-depth)
    Trạng thái       CONFIRMED
    Production path  webapp/ledger.js:19-25
    Hậu quả hiện tại KHÔNG — không đường dữ liệu hợp lệ nào tạo được tử số âm

**Mô tả.** `round(n, d)` tách dấu rồi làm tròn theo độ lớn, nên `round(-5, 2) = -3`; "nửa lên"
(§6.5) cho `-2`. Chỉ chạm được khi `usdtCostVnd` hoặc `ethCostVnd` âm, mà điều đó chỉ xảy ra sau
một tiền tố đã bị đánh cờ `LEDGER_INCONSISTENT` (`INV-4`), tức trạng thái đã fail-visible.

    RE_TRIGGER_CONDITION
      lần tới có thay đổi cho phép cost basis âm tồn tại hợp lệ (ví dụ rebate, điều chỉnh âm).

---

**Ghi chú thẩm quyền.** Bốn finding trên **chưa** được người review ghi vào
`PROJECT/HARDENING_BACKLOG.md`. `REVIEW_PROTOCOL.md` § Verdict: *"A reviewer does not modify the
repository during an independent review without separate delegation"*, và phiên này chỉ được
quyền ghi báo cáo review. Việc chuyển bốn dòng này vào Hardening Backlog là **hành động của
Owner** (xem §26).

## 24. Completion Gate Matrix

| Check | Priority | Trạng thái trước E2 | Bằng chứng độc lập của người review | Kết luận E2 |
|---|---|---|---|---|
| `CHECK-T12-01` | REQUIRED | PASS (E1) | quét khoá trên payload durable **thật đọc từ server**: 6 khoá allowlist, 0 khoá cấm, 0 field chiến lược; `LEGACY_ARCHIVE` có nhãn và không đường dẫn xuất nào đọc | không phải E2-required; không thấy phản chứng |
| `CHECK-T12-02` | REQUIRED | E2_REQUIRED | §5 — Date bị đầu độc, 300 hoán vị, 6 TZ tiến trình | **PASS** |
| `CHECK-T12-03` | REQUIRED | E2_REQUIRED | §6 — oracle Python độc lập 400 case, property 300 case / 1.154 phép, `DEC-045` | **PASS** |
| `CHECK-T12-04` | REQUIRED | E2_REQUIRED | §7 — lan truyền `null`, 0 trường FX theo lệnh, cờ thường trực | **PASS** (+`F-E2-02`) |
| `CHECK-T12-05` | REQUIRED | E2_REQUIRED | §8 — 20 edit, 10 ca xoá ≡ chưa nhập, ca nhập muộn **có tính phân biệt** | **PASS** (+`F-E2-01`) |
| `CHECK-T12-06` | REQUIRED | E2_REQUIRED | §9 — một clock duy nhất, biên UTC+7, carry đóng/mở, năm nhuận | **PASS** |
| `CHECK-T12-07` | REQUIRED | PASS (E1) | 0 float trong durable thật; `SPLIT_VND` 1.440 phép đúng tuyệt đối; khoá `ORDER` xác nhận đúng bằng probe, nhưng xem `F-E2-01` | không phải E2-required; không thấy phản chứng |
| `CHECK-T12-08` | REQUIRED | PASS (E1) | 12/12 SC chạy lại PASS; số kỳ vọng đối chiếu nguyên văn spec §19 (§4) | không phải E2-required; xác nhận |
| `CHECK-T12-09` | REQUIRED | E2_REQUIRED | §10 — 7/7 mutation bắt buộc chạy lại KILLED + 14 mutant độc lập | **PASS** (+`F-E2-01`) |
| `CHECK-T12-10` | REQUIRED | E2_REQUIRED | §11/§18 — 8 ca `M-1`…`M-4`, `W-1`, nguyên tử, không rò rỉ chiến lược | **PASS** |
| `CHECK-T12-11` | REQUIRED | E2_REQUIRED | §12 — ghi→ACK→REST→derive→reload→derive trùng tuyệt đối; export sửa tay bị bỏ qua | **PASS** |
| `CHECK-T12-12` | REQUIRED | E2_REQUIRED | §13/§20 — hai lần đo trên `app_final.html`, 20 event thật, 23 case | **PASS** |
| `CHECK-T12-13` | REQUIRED | PASS (E1) | §22 — bề mặt Python 0 thay đổi + 678 ca thu thập lại; **cả 6** script npm chạy lại, cùng một chữ ký dừng ở tiền đề legacy | không phải E2-required; phân loại N/A đứng vững |
| `CHECK-T12-14` | REQUIRED | PASS (E1) | 0 tham chiếu `ENGINE`/`engine.js` trong module sổ cái; đổi `PRICE`/chỉ báo → phần tiền không đổi; `source = RESERVE` bắt buộc note | không phải E2-required; xác nhận |

    9/9 E2-REQUIRED CHECK = PASS

Ràng buộc phạm vi cũng được kiểm lại và **giữ nguyên**:

    production file chạm       5  (<= 7)
    production diff            +460 / -7 từ 91cfbba (trong trần đã đóng băng)
    firestore.rules/firebase.json  KHÔNG đổi
    document Firestore mới     KHÔNG có
    task ID mới                KHÔNG có
    capability mới             KHÔNG có
    repair cycle tiêu thêm     KHÔNG (REPAIR_CYCLE_1 vẫn là chu kỳ duy nhất đã dùng)

## 25. Final E2 Verdict

    E2_VERDICT = PASS
    ELIGIBLE_FOR_FREEZE (advisory — reviewer KHÔNG tự ghi FROZEN/DONE)

    T-12 = IMPLEMENTED, chờ Owner đóng.
    KHÔNG hard-stop nào được kích hoạt.
    KHÔNG cần repair cycle thứ hai.
    KHÔNG cần Owner Decision mới để đóng T-12.

Bốn finding đều là `HARDENING` kèm `RE_TRIGGER_CONDITION`; không finding nào chặn việc đóng
`T-12`, và không finding nào được phép biến thành task mới
(`AGENTS.md` §3: "A finding is not a task").

## 26. Exact Owner Next Action

Owner cần làm **đúng bốn việc**, theo thứ tự:

1. **Đóng `T-12`.** Chuyển `docs/tasks/T-12-so-cai-l1-v2-va-derive.md` § Metadata
   `Status: IMPLEMENTED → DONE`, và đặt `Status` của chín check `CHECK-T12-02`, `-03`, `-04`,
   `-05`, `-06`, `-09`, `-10`, `-11`, `-12` từ `E2_REQUIRED` thành `PASS` với
   `Evidence Level: E2`, `Executed By: Claude Opus / E2 độc lập`,
   `Timestamp: 2026-09-05`, trỏ tới `docs/reviews/T12-E2-INDEPENDENT-REVIEW.md`.
   Người review **không** tự làm bước này.

2. **Ghi bốn finding vào `PROJECT/HARDENING_BACKLOG.md`** — `F-E2-01`, `F-E2-02`, `F-E2-03`,
   `F-E2-04`, **kèm nguyên văn `RE_TRIGGER_CONDITION`** ở §23. Không tạo task ID cho bất kỳ dòng
   nào (`AGENTS.md` §3).

3. **Đồng bộ roadmap** theo `governance/core/ROADMAP_SYNC_STANDARD.md`: cập nhật
   `PROJECT/PROJECT_PROGRESS.md` (T-12 DONE, E2 PASS) rồi sinh lại
   `PROJECT/LO_TRINH_DE_HIEU.md` — **không sửa tay file sinh ra**. Chạy validate routing trước
   khi sync. `PROJECT/REVIEW_BUDGET_LEDGER.md` **không đổi**: E2 không tiêu repair cycle;
   `CAP-WEBAPP` giữ ALLOWED 2 / USED 1 / REMAINING 1.

4. **Quyết định bước kế tiếp của chuỗi L-1** (spec §24, bước B). `F-E2-03` là hạng mục **đặc tả**
   cần Owner cân nhắc **trước** khi mở nghiệp vụ SELL trên dữ liệu thật; nó KHÔNG được sửa trong
   `T-12` và KHÔNG được biến thành task ở phiên này.

`OWNER_LOCAL_ACCEPTANCE` (spec §22.1, dữ liệu thật, ngoài repo) vẫn là bước D, **không** là điều
kiện đóng `T-12` — đúng như `DEC-043` §2 đã ghi.
