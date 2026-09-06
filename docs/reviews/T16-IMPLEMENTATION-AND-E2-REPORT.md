# T-16 — Báo cáo gộp (implementation + bằng chứng E2) — sổ đa tài sản, SELL, CASH

**Phiên:** `S043` · **Ngày:** 2026-09-06 · **Nhánh:** `claude/fix-7-ledger-errors-91dybv`
**Task:** `docs/tasks/T-16-so-da-tai-san-sell-cash.md` · **Quyết định:** `DEC-052`

Báo cáo GỘP implementation + bằng chứng E2 vào một file theo ngân sách artifact cứng
(`DEC-051` §B, nhắc lại ở `DEC-052` §B). Không commit evidence log nào; mọi số liệu tái lập
được bằng các lệnh ghi kèm.

---

## 0. Điều kiện tiên quyết — đã kiểm, không suy đoán

    grep -n "^## DEC-051" PROJECT/PROJECT_DECISIONS.md   -> 4677
    sed -n '5,6p' docs/tasks/T-15-sua-7-loi-ke-toan-l1.md -> "Status:" / "DONE"
    git log --oneline -4  -> 72d8eee, 322f009, 2fd5711 (T-15) trên 6c1d894 (T-14 closure)

`DEC-051` tồn tại, `T-15 = DONE`. Đủ điều kiện bắt đầu. `origin/main` vẫn ở `6c1d894` (chuỗi
`T-15`+`T-16` chưa merge), nên `T-16` nối tiếp trên cùng nhánh được uỷ quyền.

---

## 1. Xác nhận mô tả so với code thật

Chỉ thị phiên nói rõ "đừng tin số dòng trong bản mô tả này (đã cũ so với T-15)" — đúng, và đã đọc
lại toàn bộ `ledger.js` / `ledger_ui.js` / `app_logic.js` trước khi sửa. Các điểm cần nói chính
xác hơn so với chỉ thị:

| Chỉ thị nói | Code thật | Xử lý |
|---|---|---|
| "`planCheck` hiện đòi `p.asset === 'ETH'` cố định" | Đúng, nằm chung một biểu thức với kiểm `id`/`effectiveFrom` ở dòng `81` | Tách thành hai câu riêng để thông báo lỗi nói đúng nguyên nhân |
| "`derive()` … `holdings: { ETH: eth }`" | Đúng, nhưng `eth` còn được dùng ở **7** chỗ khác trong `derive()` và ở **4** chỗ trong `migrate()` (oracle legacy v1) | Đổi hết; `migrate()` nay chịu được trường hợp **không có** entry ETH (sổ legacy 0 trade — có thật trong test "Migration P2P hai chân") |
| "`eventEffects` … `ethQty`" | Chỉ thị không nêu, nhưng `ethQty` là một trường của `eventEffects` và là chốt `M-2` của migration | Đổi thành `symbol` + `holdingQty`; `M-2` dùng `holdingQty` |
| "Thêm chọn tài sản ở form số dư đầu kỳ và form TRADE" | Còn **form PRICE** cũng hardcode `symbol:'ETH'` | Thêm `l1PriceSymbol` — không có nó thì không định giá được BTC/ADA, tức tính năng đa tài sản không dùng được. Ghi rõ ở đây vì đây là phần **vượt** danh sách của chỉ thị |
| "planSpent/invested CHỈ cộng trade có symbol === plan asset **VÀ** source === 'PLAN'" | Đọc nguyên văn sẽ làm `investedThisMonthVnd === planInvestedVnd` mãi mãi, xoá mất phân biệt "tổng đã đầu tư" vs "phần theo kế hoạch" và phá `SC-09`/`SC-10` (17.000.000 vs 12.000.000) | Diễn giải theo ngữ nghĩa đang có: **cả hai** giới hạn theo asset của kế hoạch; bộ lọc `source` giữ nguyên như cũ (`invested` = mọi nguồn, `planSpent` = chỉ `PLAN`). Xem §3.2 |
| — | **Không nêu trong chỉ thị:** `app_logic.js::validateState()` từ chối mọi schema không phải `coindca.ledger/3` hoặc `ethdca.tracker/1` | Sổ v2 sẽ bị coi là **bản durable hỏng** và Owner không bao giờ tới được nút nâng cấp. Đã sửa — xem §3.4 |

Không có chỗ nào lệch tới mức phải DỪNG.

---

## 2. Thay đổi thực tế (đo trực tiếp)

    git diff --stat <T-15 head>..HEAD -- webapp
      webapp/app_logic.js               |   9 +
      webapp/ledger.js                  | 197 +++++++++++++++++++++-----
      webapp/ledger_ui.js               | 145 +++++++++++++-----
      webapp/package.json               |   4 +-
      webapp/test_l1_fixes.js           |  28 +--
      webapp/test_stepb_ui.js           |  60 ++++++--
      webapp/test_t12_browser.js        |  17 ++
      webapp/test_t12_fixtures.js       |   2 +-
      webapp/test_t12_ledger.js         |  14 +-
      webapp/test_t14_backup_restore.js |   2 +-
      10 files changed, 362 insertions(+), 116 deletions(-)
      + webapp/test_t16_multiasset.js (MỚI)

    git diff --stat <T-15 head>..HEAD -- src/eth_dca_os docs/spec firestore.rules
      (rỗng)

Trong ước lượng change budget của task (≤ 12 file, ≤ 700 dòng).

---

## 3. Quyết định thiết kế

### 3.1 "Asset của kế hoạch" — SUY TỪ `plan.versions[0].asset`, không thêm trường `plan.asset`

Đây là câu hỏi được yêu cầu trả lời rõ. Chọn suy từ version đầu tiên, vì:

1. `planCheck()` đã ép **mọi** version trong một plan cùng một asset, nên version đầu tiên là
   nguồn canonical duy nhất — thêm `plan.asset` chỉ tạo một chỗ thứ hai để hai giá trị lệch nhau
   và một luật mới để giữ chúng bằng nhau.
2. Thêm một trường ở cấp `plan` là **đổi hình dạng sổ**: `keys(plan, 'versions startMonth')` phải
   nới ra, và mọi sổ đã lưu thiếu trường đó → thêm một migration nữa. Không đáng cho một giá trị
   suy được.
3. `plan.versions` rỗng (`L.empty()`) → asset của kế hoạch là `null`, và khi đó không có ngân
   sách nào để bảo vệ, nên cả hai luật (`validation` và `derive`) tự bỏ qua.

Cài đặt: một hàm thuần `planAssetOf(plan)` dùng chung cho `eventCheck` và `derive`.

### 3.2 Ranh giới "đa tài sản ở tầng nắm giữ / đơn tài sản ở tầng kế hoạch" — hai lớp

- **Lớp validation (cổng vào):** `eventCheck` từ chối `TRADE` có `source === 'PLAN'` mà
  `symbol !== planAsset`. Chặn ở đây chứ không chỉ ở `derive` là yêu cầu tường minh của chỉ thị —
  một event sai không được phép TỒN TẠI trong sổ, chứ không phải chỉ bị bỏ qua khi tính.
- **Lớp derive (phòng thủ):** `invested[m]` và `planSpent[m]` chỉ cộng khi `symbol === planAsset`.
  `invested` **giữ nguyên** ngữ nghĩa cũ "mọi nguồn" và `planSpent` **giữ nguyên** "chỉ `PLAN`";
  cái mới là **cả hai đều giới hạn theo coin của kế hoạch**. Đọc chỉ thị theo nghĩa đen (`invested`
  cũng đòi `source === 'PLAN'`) sẽ làm hai con số trùng nhau vĩnh viễn và phá `SC-09`/`SC-10`;
  đây là chỗ diễn giải, đã nêu ở §1.
- `reserve` **không** bị giới hạn theo asset: dự phòng là một hũ VND, tiêu vào coin nào cũng phải
  trừ. Giữ nguyên.

### 3.3 SELL — bán CHUYỂN giá vốn, không định giá lại

    proceeds  = usdtNotional − feeUsdt
    relievedU = portion(qty, h.costUsdt, h.qty)
    relievedV = portion(qty, h.costVnd,  h.qty)
    h.qty −= qty ; h.costUsdt −= relievedU ; h.costVnd −= relievedV
    usdt.qty += proceeds ; usdt.costVnd += relievedV        <- CHUYỂN, không phải `basis`
    realizedPnlUsdt += proceeds − relievedU                 <- ĐƠN VỊ micro-USDT

Lỗi cũ (`T-12`) cộng `basis = proceeds × usdt.costVnd / usdt.qty` — giá trung bình của **chính
pool nhận tiền**, một con số không liên quan tới lô coin vừa bán. Hệ quả: tổng giá vốn VND đổi
tuỳ ý, không cờ nào báo.

Hai đơn vị **không bao giờ gộp**: `realizedPnlUsdt` (micro-USDT) sinh khi bán coin lấy USDT;
`realizedFxVnd` (VND) sinh khi USDT đổi ngược ra VND — cơ chế `TREASURY USDT_TO_VND` giữ nguyên,
không sửa một dòng. UI hiện hai ô riêng, có ghi đơn vị.

Bán CẠN một holding: `portion(qty, cost, qty)` trả đúng `cost`, nên `costUsdt`/`costVnd` về đúng
0 — luật zero-out sẵn có không xoá mất phần dư nào. Bán quá số đang giữ: `portion` trả `null` và
`inconsistent()` bật cờ — fail-closed như cũ, không đổi.

### 3.4 `migrateV3` — hình thức, nhưng phải CHỨNG MINH được là hình thức

v3 chỉ **nới** validation, nên mọi tài liệu v2 hợp lệ đã là tài liệu v3 hợp lệ sau khi đổi nhãn.
Đúng vì thế mà nó nguy hiểm: một migration "chắc chắn không đổi gì" là loại không ai kiểm. Ba cổng:

1. `guardV2()` — từ chối tài liệu tự nhận là v2 mà không có hình dạng v2 (nhiều tài sản, coin
   khác ETH, `SELL`, kind `CASH`). Không có nó thì một tài liệu v3 bị đổi nhãn ngược thành v2 sẽ
   đi thẳng qua.
2. `v2Oracle()` — replay lại **ngữ nghĩa v2** bằng một vòng lặp riêng, **không gọi `derive()`**,
   rồi so 8 đại lượng (`ethQty`, `ethCostUsdt`, `ethCostVnd`, `usdtQty`, `usdtCostVnd`,
   `vndBalance`, `reserveBalance`, `realizedFxVnd`) với `derive()` v3, tolerance 0.
   **Giới hạn đã biết, nói thẳng:** oracle này dùng chung bốn phép số nguyên (`add`/`sub`/`round`/
   `portion`) với `derive()`, nên nó **không** độc lập về số học. Nó độc lập về **duyệt và hình
   dạng** — đúng chỗ một lỗi migration sẽ nằm. Phần số học đã có mutation suite riêng
   (`INV-3`/`INV-11`), không cần và không nên viết lại lần thứ ba.
3. Oracle hình dạng — ngoài đúng trường `schema`, `JSON.stringify` của sổ trước/sau phải trùng.

Lệch bất kỳ cổng nào → `ok:false`, **không ghi gì**. Chạy qua `L.destructive` nên có snapshot
trước, đúng như mọi thao tác phá huỷ khác.

**Phát hiện ngoài chỉ thị:** `app_logic.js::validateState()` chỉ nhận `coindca.ledger/3` và
`ethdca.tracker/1`. Một sổ v2 nằm trên Firestore sẽ rơi vào nhánh "bản durable không hợp lệ" —
app khoá ghi, không nạp, và Owner **không bao giờ tới được nút nâng cấp**. Đã thêm nhánh nhận
diện v2 ở chế độ chỉ đọc (kiểm `rev`/`plan`/`events` tối thiểu); validate đầy đủ vẫn nằm ở
`migrateV3`. Đường này nay có test chạy trên trình duyệt thật (§5.2, `T-16 v2->v3`).

### 3.5 Hình dạng `holdings` và `eventEffects`

`holdings` là bản đồ theo symbol, chỉ tạo entry cho coin thật sự có mặt (số dư đầu kỳ hoặc một
event `TRADE`/`PRICE`) — cùng nguyên tắc `months` chỉ chứa tháng có dữ liệu. `valuation` cũng
thành bản đồ theo symbol, mỗi coin dùng `PRICE` mới nhất **của chính nó**, giữ nguyên hạn dùng
1 ngày và `usdVndRate` tuỳ chọn của `T-15`.

`eventEffects[id].ethQty` → `symbol` + `holdingQty`. Trong một sổ đa tài sản không còn khái niệm
"số lượng ETH của event này"; chốt `M-2` của migration nay đọc `holdingQty`.

---

## 4. Bằng chứng chạy

### 4.1 Bộ test mới

`webapp/test_t16_multiasset.js` — 14 ca, **14/14 PASS**:

| Ca | Nội dung |
|---|---|
| T16-1 | migrate v2→v3: oracle số học 8/8 khớp, oracle hình dạng khớp, sổ v2 KHÔNG tự được nhận là v3 |
| T16-2 | migrateV3 từ chối: đầu vào v3, `null`, thiếu `today`, sổ v2 dị dạng (2 tài sản) |
| T16-3 | openingCheck: 3 tài sản cùng lúc OK; `DOGE`/`eth`/`USDT`/`''` bị từ chối; symbol trùng bị từ chối; luật "giá vốn khi lượng 0" giữ nguyên |
| T16-4 | TRADE/PRICE nhận cả `BTC`/`ETH`/`ADA`; `DOGE` bị từ chối |
| T16-5 | plan `BTC`/`ADA` hợp lệ; hai version khác asset bị từ chối; hai version cùng asset vẫn hợp lệ |
| T16-6 | opening BTC+ETH + 1 trade BTC + 1 trade ETH → hai holding tách biệt đúng số; **không** entry `ADA` |
| T16-7 | định giá theo từng symbol; `usdVndRate` chỉ áp cho coin có nó; PRICE quá hạn → không định giá |
| T16-8 | mua BTC không lọt vào ngân sách ETH; `BTC + source PLAN` bị chặn ở `canonical` **và** `derive`; kế hoạch BTC thì ngược lại |
| T16-9 | CASH DEPOSIT/WITHDRAW đổi đúng `vnd.balance`, không chạm usdt/holdings/reserve; type sai và số 0 bị từ chối |
| T16-10 | WITHDRAW vượt số dư → `LEDGER_INCONSISTENT` + `firstOffendingEventId` |
| T16-11 | **kịch bản gốc**: `CASH DEPOSIT` + `VND_TO_USDT` cùng số tiền → `vnd = 0`, `flags = []`; bỏ CASH đi → cờ bật lại |
| T16-12 | **SELL tính TAY**: 5 con số holding/pool + `realizedPnlUsdt 74.575.000` + `realizedFxVnd 0` |
| T16-13 | SELL chỉ chuyển giá vốn (tổng không đổi 50.000.000); bán cạn → 0 sạch; bán quá tay → fail-closed |
| T16-14 | **property test 60 chuỗi ngẫu nhiên** CASH/TREASURY/BUY/SELL trên 3 coin |

Ca `T16-12` tính tay, để đối chiếu:

    CASH DEPOSIT 100.000.000 ₫ -> vnd 100.000.000
    VND->USDT 50.000.000 ₫ / 2.000 USDT -> pool 2.000 USDT @ 50.000.000 ₫ ; vnd 50.000.000
    BUY  ETH 400 USDT + 0,4 phí, 0,2 ETH  -> giải phóng 400,4/2.000 × 50.000.000 = 10.010.000 ₫
    BUY  ETH 300 USDT + 0,3 phí, 0,12 ETH -> giải phóng 300,3/1.599,6 × 39.990.000 = 7.507.500 ₫
      => ETH 0,32 · costUsdt 700,7 USDT · costVnd 17.517.500 ₫ ; pool 1.299,3 USDT / 32.482.500 ₫
    SELL ETH 0,08 (= 1/4 lượng đang giữ), 250 USDT − 0,25 phí
      giải phóng USDT 700,7/4 = 175,175 · VND 17.517.500/4 = 4.379.375
      => ETH 0,24 · costUsdt 525,525 · costVnd 13.138.125
      => pool 1.549,05 USDT · costVnd 32.482.500 + 4.379.375 = 36.861.875
      => realizedPnlUsdt = 249,75 − 175,175 = 74,575 USDT ; realizedFxVnd = 0
    Bảo toàn: 13.138.125 + 36.861.875 = 50.000.000 = đúng số VND đã bơm vào hệ

Property test khẳng định ba điều trên mỗi chuỗi:
1. `vnd.balance == Σ CASH DEPOSIT − Σ CASH WITHDRAW − Σ VND_TO_USDT + Σ USDT_TO_VND`;
2. bảo toàn giá vốn VND: `Σ holding.costVnd + usdt.costVnd + Σ giá-vốn-giải-phóng-khi-đổi-ra-VND
   + quét-đáy-pool == Σ VND_TO_USDT` (số hạng quét đáy được tính từ
   `realizedFxVnd − Σ(vndAmount − vndRelieved)` và **khẳng định luôn bằng 0** trên chuỗi hợp lệ —
   `portion()` trả đúng toàn bộ giá vốn khi rút cạn, nên không có dư nào để quét);
3. bỏ hết event `CASH` đi thì tổng giá vốn **không đổi** — CASH không bao giờ chạm giá vốn.

### 4.2 Đường UI thật

| Suite | Nội dung mới | Kết quả |
|---|---|---|
| `test_t12_browser.js` — `T-16 v2->v3` | Đặt một sổ `coindca.ledger/2` lên Firestore → app nạp CHỈ ĐỌC (banner "SCHEMA 2"), nút nâng cấp hiện, luồng migration legacy v1 **không** hiện, sổ **không bị ghi đè** trước khi bấm; bấm → snapshot xuất trước → nâng cấp → nội dung không đổi một byte ngoài `schema`/`rev` | PASS |
| `test_stepb_ui.js` — `T-16` | Qua đúng control mới: `CASH DEPOSIT` 40.000.000 ₫, mua **BTC** (EXTRA, chọn ở dropdown `l1Symbol`), **bán ETH**; Tổng quan có dòng nắm giữ riêng cho BTC và ETH; hai ô lãi/lỗ tách đơn vị khớp bit-với-bit `derive()`; `planInvestedVnd` chỉ gồm lệnh mua ETH theo kế hoạch; Lịch sử hiện nhãn "Bán ETH" và "Nạp tiền mặt" | PASS |
| `test_stepb_ui.js` — `AS-10` | **Đảo chiều** so với T-13: UI **phải** có đường bán và **phải** hiện lãi/lỗ đã thực hiện tách hai đơn vị | PASS |

Trong ca `test_stepb_ui` T-16, khẳng định về CASH được phát biểu chính xác thay vì "không cờ
nào": sổ ở bước đó còn **một cờ khác không liên quan tới T-16** (`AS-06` đã xoá lệnh nạp dự phòng
nên lệnh "mua từ dự phòng" ngày 20/03 làm `reserve` âm — hành vi có sẵn từ trước, không phải hồi
quy). Ca này vì vậy khẳng định: **bỏ `CASH` đi thì `vnd` âm + cờ bật; có `CASH` thì `vnd` dương**,
và cờ còn lại đến từ `2026-03-20` (reserve), không phải tiền mặt.

### 4.3 Toàn bộ bộ test

| Suite | Cần emulator | Kết quả |
|---|---|---|
| `test_t12_ledger.js` (+ `test_t12_fixtures.js`) | không | **PASS** 32/32 |
| `test_l1_fixes.js` (T-15) | không | **PASS** 15/15 |
| `test_t16_multiasset.js` (MỚI) | không | **PASS** 14/14 |
| `test_t12_mutations.js` | không | **PASS** 7/7 mutant KILLED, 0 survivor |
| `test_t14_deploy_isolation.js` | không | **PASS** 18 assertion |
| `test_t14_rules.js` | có | **PASS** 120 assertion |
| `test_t14_persistence.js` | có | **PASS** 60 assertion |
| `test_t14_backup_restore.js` | có | **PASS** 47 assertion |
| `test_t12_browser.js` | có | **PASS** (gồm `T-16 v2->v3`) |
| `test_stepb_ui.js` | có | **PASS** 0 mục `"status": "FAIL"` |

**`npm --prefix webapp test` → exit 0.** Firestore/Auth Emulator chạy thật trong phiên này;
Chromium `/opt/pw-browsers/chromium`. **Không suite nào bị bỏ qua.**

### 4.4 Fixture Owner — không đổi

    node test_t12_owner.js ../tests/fixtures/t12/owner-example.synthetic.json
      OWNER_LOCAL_ACCEPTANCE: PASS

9/9 trường khớp bit-exact, tolerance 0. Fixture là ETH-only nên nó chứng minh đường cũ không bị
phá bởi việc đổi `holdings` sang bản đồ. File **không bị sửa** (`git diff -- tests/fixtures` rỗng).

---

## 5. Test cũ giả định hình dạng cũ — đã cập nhật, không né

Nguyên tắc của chỉ thị: cập nhật test cho đúng hình dạng mới, không viết lại logic để né test.

| Test | Trước | Sau | Vì sao |
|---|---|---|---|
| `test_t12_ledger` `INV-3` | `A.throws(…/H-46/)` (T-15 chặn SELL) | khẳng định 6 con số ĐÚNG của SELL + bảo toàn tổng | H-46 phần bán chính là task này |
| `test_l1_fixes` `L4` | "SELL bị từ chối" | "SELL được nhận và KHÔNG phá bảo toàn VND (lỗi cũ 50.000.000 → 49.995.000)" | Giữ nguyên giá trị hồi quy của ca gốc, đảo chiều khẳng định |
| `test_l1_fixes` `L7f` | `d.valuation.usdt` | `d.valuation.ETH.usdt` | valuation nay theo symbol |
| `test_t12_fixtures` | `schema: 'coindca.ledger/2'` | `/3` | bump schema |
| `test_stepb_ui` `AS-07` | `bottom['Giá vốn TB (VND)']` | `bottom['Giá vốn TB ETH (VND)']` | nhãn phải nói rõ coin nào khi có nhiều coin |
| `test_stepb_ui` `AS-10` | "không SELL / không P&L" | "phải có SELL và P&L tách hai đơn vị" | T-13 đặt luật đó vì lúc đó bán chưa được thiết kế |
| `test_t14_backup_restore` | `derivedSnapshot.ethQty` | `derivedSnapshot.holdings.ETH.qty` | khối tham khảo nay theo bản đồ |

Không test nào bị **xoá**; không assertion nào bị làm yếu để lấy màu xanh.

---

## 6. Rủi ro còn lại / điều Owner cần biết trước khi nhập sổ thật

1. **Sổ production hiện tại là `coindca.ledger/2`.** Sau khi deploy bản này, app sẽ hiện
   "SCHEMA 2 — CHỈ ĐỌC" cho tới khi Owner bấm **Kế hoạch → Nâng cấp sổ → Đối chiếu và nâng cấp**.
   Đây là hành vi CỐ Ý (không migration âm thầm). Có snapshot trước khi ghi.
2. **Nhập sổ Excel là một bước riêng, chưa làm ở đây** (Scope OUT). `derive()` nay đủ từ vựng;
   việc dựng event từ file nguồn chạy ngoài repo.
3. `H-41` (**chưa nên dùng tiền thật**) **giữ nguyên**: nhóm việc vận hành ngoài repo của bản rà
   soát T-14 vẫn chưa làm.
4. **`CAP-WEBAPP` `REMAINING = 2`** sau `OWNER_EXTENSION` của `DEC-052` §E. `T-16` tiêu 0.

---

## 7. HARDENING — ghi nhận, KHÔNG sửa trong task này

| ID | Trạng thái sau T-16 |
|---|---|
| `H-46` (SELL / P&L thực hiện) | **ĐÓNG MỘT PHẦN.** Phần "bán coin lấy USDT" đã được thiết kế và cài đặt: giá vốn chuyển đúng, `realizedPnlUsdt` ghi bằng đơn vị USDT, bất biến bảo toàn VND có test property. **CÒN MỞ:** (a) P&L thực hiện quy ra **VND** cho một lượt bán (cần chốt tỷ giá nào là "giá vốn VND của USDT thu về" — hiện chỉ có FX khi USDT ra VND thật); (b) báo cáo lãi/lỗ theo lô/theo kỳ; (c) thuế/chi phí. Không đóng dứt điểm ở đây |
| `H-58` (guard `startMonth`) | **KHÔNG ĐỔI.** T-16 không chạm luật đó |
| `H-54` (`RESERVE CONTRIBUTE` không trừ `vnd.balance`) | **KHÔNG ĐỔI** — và nay dễ thấy hơn: một sổ có nạp dự phòng vẫn đếm hai lần trên Dashboard. Ngoài phạm vi |
| `H-59` (MỚI) | `derive()` cho phép `TRADE side='SELL'` mang `source='PLAN'`/`'RESERVE'`. Vô hại về số học (bán không chạm `invested`/`planSpent`/`reserve`), nhưng là tổ hợp vô nghĩa mà validation không chặn. UI mặc định `EXTRA` cho lệnh bán. Ghi nhận, không thêm luật ngoài chỉ thị |
| `H-60` (MỚI) | `realizedPnlUsdt` thành `null` khi holding có `costUsdt` chưa biết (số dư đầu kỳ để trống giá vốn USDT). Hiển thị "—", nhất quán với `UNKNOWN_VND_BASIS`, nhưng KHÔNG có cờ riêng cho "giá vốn USDT chưa biết". Cân nhắc khi nhập sổ thật nếu số dư đầu kỳ thiếu giá vốn USDT |
| `H-61` (MỚI) | Form số dư đầu kỳ sửa **một coin mỗi lần lưu** (dropdown chọn coin, các coin khác giữ nguyên; lượng 0 + giá vốn trống = xoá coin đó). Đủ dùng và giữ nguyên hợp đồng id `l1Eth*` với bộ test, nhưng không phải một trình soạn thảo N-dòng thật sự. Nâng cấp khi Owner thấy vướng |

---

## 8. Ngân sách artifact của phiên này

| Hạng mục | Cho phép | Thực tế |
|---|---|---|
| Task file | 1 | 1 — `docs/tasks/T-16-so-da-tai-san-sell-cash.md` |
| Báo cáo | 1 (gộp) | 1 — chính file này |
| DEC | 1 (closure) | 1 — `DEC-052` |
| Evidence log commit | 0 | **0** |

Ngoài bốn mục trên chỉ cập nhật state surface đã tồn tại (`PROJECT_PROGRESS.md`,
`REVIEW_BUDGET_LEDGER.md`, `HARDENING_BACKLOG.md`) theo `STATE_AUTHORITY.md`.
