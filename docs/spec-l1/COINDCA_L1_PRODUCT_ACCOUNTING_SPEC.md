# CoinDCA L-1 Product + Accounting Spec

**SINGLE-USER • MANUAL ENTRY • VND ACCOUNTING / USDT EXECUTION • EVENT-SOURCED LEDGER**

Status: `CANONICAL — APPROVED` (Owner Decision `DEC-042`, 2026-09-05; các câu hỏi §21 đã QUYẾT)
Thẩm quyền nền: `DEC-040`, `DEC-041` (A, B, C, D, J, K), `DEC-042`, `H-41`, `H-42`
Ngày soạn: 2026-09-05 · Ngày duyệt: 2026-09-05 (`DEC-042`)
Tu chỉnh oracle SC-04: 2026-09-05 (`DEC-044`); giữ nguyên input, WAC và ngữ nghĩa `DEC-042`.

## Tóm tắt Thi hành (Executive Summary)

**Owner Decision `DEC-042` chấp thuận DEVIATION-1** (spec dài hơn kỳ vọng "≤ 5 trang" của
`DEC-041` J) với điều kiện: giữ **một** tài liệu canonical duy nhất, không dựng khung governance
mới để tóm tắt nó. Mục này là bản tóm tắt đó — chỉ để định hướng cài đặt; **chi tiết và ràng buộc
chuẩn nằm ở các mục đánh số bên dưới**, mục này không tự đứng làm thẩm quyền.

**Định nghĩa sản phẩm (§1).** Sổ cái + công cụ lập kế hoạch tích luỹ crypto cá nhân, một người
dùng: đặt ngân sách/lịch DCA, ghi giao dịch P2P và crypto thật (ngày người dùng nhập), biết chính
xác giá vốn và holdings. Không dự đoán giá, không recommendation, không tự động hoá (§3).

**Mô hình sự thật tài chính (§4, §9).** `openingPosition + events[]` → **tính lại toàn bộ** mỗi
lần render; không biến cộng dồn. Sự kiện là nguồn thẩm quyền; mọi holdings/giá vốn/ngân sách là
dẫn xuất và không được lưu (`INV-1`).

**Thực thể lõi (§5).** `plan` (versioned) · `openingPosition` (tối đa một) · `events[]` đa hình:
`TREASURY` (P2P VND↔USDT) · `TRADE` (USDT↔crypto) · `RESERVE` (nạp/rút quỹ dự phòng) · `PRICE`
(định giá hiển thị, không phải dữ liệu tài chính).

**Quyết định đã duyệt (`DEC-042`, chi tiết §21):**

| # | Câu hỏi | Quyết định |
|---|---|---|
| `OD-L1-1` | Mô hình lịch DCA | Số tiền cố định/tháng + `scheduleDays` (mặc định `[3, 13, 23]`) |
| `OD-L1-2` | Ngân sách chưa dùng hết | `CAPPED_CARRY`, `carryCapMonths = 1` |
| `OD-L1-3` | Quỹ dự phòng | Tách hẳn khỏi ngân sách DCA; chỉ giải ngân thủ công, không tính vào tuân thủ kế hoạch |
| `OD-L1-4` | Giá vốn VND khi thiếu nguồn gốc P2P | STRICT / FAIL-VISIBLE: WAC trên một pool USDT; khi basis thật sự không biết → lan truyền `UNKNOWN`, **không** bịa tỷ giá, **không** có ô override theo từng lệnh |

**Chỉ mục Invariant (§20, chi tiết đầy đủ ở đó):** `INV-1` chỉ dẫn xuất · `INV-2` tất định ·
`INV-3` bảo toàn giá vốn · `INV-4` không âm · `INV-5` tiền là số nguyên · `INV-6` ngày sạch (chỉ
`businessDate` vào phép tính) · `INV-7` ranh giới đầu kỳ · `INV-8` P2P không phải đầu tư ·
`INV-9` cách ly dự phòng · `INV-10` tín hiệu không được chạm tiền · `INV-11` không biết ≠ 0, và
không có fallback tỷ giá ẩn theo từng lệnh · `INV-12` migration nguyên tử · `INV-13` làm tròn đối
chiếu được · `INV-14` snapshot trước phá huỷ · `INV-15` định danh ổn định.

**Chỉ mục Golden Scenario (§19, chi tiết đầy đủ ở đó):** `SC-01` số dư đầu kỳ · `SC-02` P2P
VND→USDT · `SC-03` mua ETH bằng USDT · `SC-04` nhiều tỷ giá P2P rồi mua ETH · `SC-05` sửa giao
dịch cũ · `SC-06` xoá giao dịch · `SC-07` nhập muộn theo ngày thật · `SC-08` ranh giới tháng
`Asia/Ho_Chi_Minh` · `SC-09` mua thêm ngoài kế hoạch · `SC-10` giải ngân dự phòng thủ công ·
`SC-11` dữ liệu tháng tương lai · `SC-12` migration với giá vốn không xác định → hoàn tất kèm
cờ `UNKNOWN`, không hoá thành số bịa (§17.4).

**Lát cắt chấp nhận MVP (§22):** ngân sách tháng → lịch mua đã lên kế hoạch → giao dịch thật có
ngày người dùng nhập → sổ cái + giá vốn tính lại → 4 con số dashboard (ngân sách · đã đầu tư ·
còn lại · ngày mua kế tiếp) → lưu bền qua reload/restart. Điều kiện chấp nhận đầy đủ: `A-1`…`A-6`.

---

---

## 0. Vị trí của tài liệu này trong bộ thẩm quyền

Tài liệu này là **nguồn yêu cầu sản phẩm canonical cho CoinDCA L-1**, thay `docs/spec/*_V2_1_5.md`
ở đúng vai trò đó (`DEC-041` J). Nó **không** thay thế, không sửa, không hạ giá trị bộ spec
V2.1.5 — bộ đó vẫn là **frozen historical research authority** (`DEC-041` A) và `docs/spec/`
diff = 0.

Thứ tự thẩm quyền nội bộ của phiên soạn spec này, đúng theo yêu cầu đóng khung:

    FINANCIAL TRUTH -> DATA MODEL -> DERIVED ACCOUNTING -> USER ACTIONS
      -> PRODUCT JOURNEY -> UI REQUIREMENTS

Hệ quả bắt buộc: mô hình dữ liệu dưới đây được rút ra từ dòng tiền thật, **không** từ giao diện
V2.1.5 đang tồn tại. Cấu trúc `Base` / `Smart` / `Opportunity`, `ladder`, `zone`, `oppFund`
**không** được giữ lại chỉ vì chúng đã tồn tại; §17 nói rõ số phận từng cái.

**`DEVIATION-1` — ĐÃ DUYỆT (`DEC-042`).** `DEC-041` J đặt kỳ vọng spec L-1 *"≤ 5 trang"*; tài
liệu này dài hơn vì bề mặt deliverable (24 mục + 12 kịch bản kế toán) do chính chỉ thị phiên của
Owner quy định, và mô hình giá vốn hai tiền tệ không thể đặc tả đủ chặt trong 5 trang. Owner đã
duyệt sai lệch này với điều kiện: giữ **một** tài liệu canonical duy nhất (không tách thành pack
nhiều tài liệu như V2.1.5), và bổ sung một **tóm tắt thi hành gọn** ở đầu chính tài liệu này —
xem mục "Tóm tắt Thi hành" ngay phía trên §0. **Đây không phải giấy phép mở rộng phạm vi về sau**
(nguyên văn Owner); bản spec chi tiết hiện tại là thẩm quyền kế toán canonical.

---

## 1. Product Definition

CoinDCA L-1 là **sổ cái và công cụ lập kế hoạch tích luỹ crypto cá nhân, một người dùng**.

Nó giúp chủ sở hữu:

- đặt kế hoạch đầu tư hằng tháng;
- biết **phải** đầu tư bao nhiêu;
- biết **đã** đầu tư bao nhiêu;
- biết **còn lại** bao nhiêu;
- biết **hành động kế tiếp** theo kế hoạch;
- ghi giao dịch P2P và giao dịch crypto **thật**, với ngày do người dùng nhập;
- biết đang nắm giữ bao nhiêu;
- biết **giá vốn trung bình theo USDT và theo VND**;
- phân biệt mua theo kế hoạch, giải ngân quỹ dự phòng, và mua thêm ngoài kế hoạch;
- giữ một sổ lịch sử **sửa được**;
- dùng app qua nhiều phiên mà không cần terminal hay AI.

## 2. Scope

Trong phạm vi L-1 MVP:

| # | Hạng mục |
|---|---|
| S-1 | Kế hoạch DCA hằng tháng (ngân sách + lịch) |
| S-2 | Số dư đầu kỳ (opening position) |
| S-3 | Treasury / P2P: VND ↔ USDT |
| S-4 | Giao dịch crypto: USDT ↔ tài sản (L-1 MVP: ETH) |
| S-5 | Giá vốn hai tiền tệ (USDT và VND) |
| S-6 | Quỹ dự phòng (reserve) do người dùng điều khiển hoàn toàn thủ công |
| S-7 | Mua thêm ngoài kế hoạch (extra purchase) |
| S-8 | Sổ lịch sử: xem, sửa, xoá |
| S-9 | Dashboard: 4 con số + 1 hành động kế tiếp |
| S-10 | Migration từ dữ liệu app hiện tại |
| S-11 | Lưu bền, export/import, snapshot trước thao tác phá huỷ |

## 3. Non-Goals

CoinDCA L-1 **không** hứa và **không** làm:

| # | Không làm | Neo thẩm quyền |
|---|---|---|
| N-1 | Dự đoán giá | `DEC-041` B |
| N-2 | Bắt đáy / phát hiện đáy | `DEC-041` B |
| N-3 | Timing thắng thị trường | `DEC-040` |
| N-4 | Recommendation / Buy Score đã kiểm chứng | `DEC-041` A, B — V2.1.5 = `FAILED`, verdict `DO_NOT_BUILD` |
| N-5 | Giao dịch tự động, đặt lệnh tự động | `DEC-041` B |
| N-6 | Ladder / zone / unlock / spacing sinh ra hành động | `DEC-041` B |
| N-7 | Quỹ dự phòng tự giải ngân theo tín hiệu | `DEC-041` B, §12, `INV-10` |
| N-8 | Tuyên bố bất kỳ edge nào | `DEC-041` B |
| N-9 | Kế toán thuế, tax lot (FIFO/LIFO/specific-ID) | §8 — không cần cho app cá nhân |
| N-10 | Đa người dùng, phân quyền vai trò | `PROJECT_PROFILE.md` § Not Applicable |

---

## 4. Financial Truth Model

### 4.1 Nguyên tắc gốc

**Sự thật tài chính = `openingPosition` + chuỗi `events` do người dùng nhập.**
Mọi con số khác là **dẫn xuất** và được **tính lại toàn bộ** mỗi lần render.

Đây là ràng buộc **kiến trúc**, không phải sở thích cài đặt. Nó là lời giải trực tiếp cho
`H-41` ràng buộc số 2: chỉ mô hình tính-lại mới làm `edit` / `delete` / nhập muộn an toàn, và nó
xoá **cả một lớp** lỗi cộng dồn (`B1`, `B2`, `B5`, `B6`) thay vì vá từng lỗi một.

Cụ thể, app hiện tại giữ `state.eth`, `state.costUsdt`, `state.costVnd`, `state.treasury` là
**biến cộng dồn** (`webapp/app_logic.js:250-256`). Dưới L-1 các trường đó **không tồn tại trong
state được lưu**. Chúng là hàm của event log.

### 4.2 Hai loại tiền, ba loại tài sản

| Ký hiệu | Vai trò | Đơn vị lưu |
|---|---|---|
| VND | **Accounting currency** — đơn vị của kế hoạch, ngân sách, giá vốn cuối cùng | integer đồng |
| USDT | **Monetary asset trung gian** — có số lượng VÀ có giá vốn VND riêng | integer micro-USDT (1e-6) |
| ETH (và crypto khác) | **Investment asset** — mục tiêu tích luỹ | integer 1e-8 đơn vị |

Điểm mấu chốt của toàn bộ mô hình: **USDT không phải là tiền mặt trung tính. USDT là một tài sản
có giá vốn VND.** Mọi khó khăn của kế toán hai tiền tệ ở §8 đều là hệ quả của sự thật này.

### 4.3 Bảng thực thể tối thiểu

| Thực thể | Có phải "chi phí đầu tư" không? | Ghi chú |
|---|---|---|
| `plan` | không | cấu hình, không phải sự kiện tiền |
| `openingPosition` | **không** | §14 — không bao giờ là một giao dịch |
| `treasuryTx` (P2P) | **không** — chuyển đổi giữa hai tài sản tiền tệ | `INV-8` |
| `assetTrade` (USDT→ETH) | **có** — đây là hành vi "đầu tư" duy nhất | §7 |
| `reserveTx` | không | §12 — chỉ dịch chuyển earmark |
| `priceMark` | không | §16 — chỉ để định giá hiển thị |

---

## 5. Entities

Schema id mới: `coindca.ledger/2`. **Không** tương thích ngược với `ethdca.tracker/1`; đường đi
duy nhất là migration ở §17.

### 5.1 `plan` — kế hoạch DCA (versioned)

```
plan: {
  versions: [
    {
      id:            string,            // ổn định, không tái sử dụng
      effectiveFrom: "YYYY-MM",         // tháng đầu tiên áp dụng
      asset:         "ETH",             // L-1 MVP: một tài sản
      monthlyBudgetVnd: integer,        // đồng
      scheduleDays:  [3, 13, 23],       // ngày trong tháng, 1..31, tăng dần, không trùng
      carryPolicy:   "CAPPED_CARRY",    // FORFEIT | CARRY | CAPPED_CARRY  -- DEC-042 câu 2 (QUYẾT)
      carryCapMonths: 1                 // chỉ có nghĩa khi CAPPED_CARRY
    }
  ],
  startMonth: "YYYY-MM"                 // tháng đầu tiên kế hoạch có hiệu lực
}
```

Kế hoạch **áp dụng cho tháng `m`** = version có `effectiveFrom` lớn nhất mà `≤ m`. Không có
version nào thoả → tháng đó **không có kế hoạch**; mọi đại lượng kế hoạch trả `UNKNOWN`, không
trả 0 (`INV-11`).

`scheduleDays` với ngày lớn hơn số ngày của tháng được **kẹp về ngày cuối tháng**; nếu việc kẹp
làm hai ngày trùng nhau thì gộp thành một mốc.

### 5.2 `openingPosition` — số dư đầu kỳ (tối đa một, có thể vắng)

```
openingPosition: {
  asOf: "YYYY-MM-DD",                   // ranh giới; xem INV-7
  assets: [
    { symbol: "ETH",
      qty:       integer,               // 1e-8
      costUsdt:  integer | null,        // 1e-6; null = KHÔNG BIẾT
      costVnd:   integer | null }       // đồng; null = KHÔNG BIẾT
  ],
  usdt: { qty: integer, costVnd: integer | null },
  vnd:  { qty: integer },               // tiền VND sẵn sàng cho kế hoạch (tuỳ chọn)
  reserveVnd: integer,                  // earmark dự phòng đầu kỳ (mặc định 0)
  note: string
}
```

`null` ở `costUsdt` / `costVnd` là **hợp lệ và có ý nghĩa**: nó lan truyền thành `UNKNOWN` chứ
không bị thay bằng 0 hay bằng một tỷ giá thị trường (`INV-11`).

### 5.3 `events[]` — một mảng duy nhất, đa hình

Trường chung của **mọi** event:

```
{
  id:           string,        // ổn định, duy nhất, KHÔNG BAO GIỜ tái sử dụng
  seq:          integer,       // tăng đơn điệu, cấp lúc TẠO, không đánh số lại khi sửa
  kind:         "TREASURY" | "TRADE" | "RESERVE" | "PRICE",
  businessDate: "YYYY-MM-DD",  // NGƯỜI DÙNG NHẬP -- trường tài chính duy nhất về thời gian
  createdAt:    "<ISO-8601 UTC>",   // metadata, KHÔNG BAO GIỜ vào phép tính tài chính
  updatedAt:    "<ISO-8601 UTC>",   // metadata
  note:         string
}
```

`kind = "TREASURY"` (P2P):

```
{ dir: "VND_TO_USDT" | "USDT_TO_VND",
  vndAmount:  integer,   // VND thực sự RỜI (hoặc VỀ) tài khoản ngân hàng -- xem §6.2
  usdtAmount: integer,   // USDT thực sự NHẬN (hoặc RỜI) ví -- xem §6.2
  counterparty: string } // tuỳ chọn
```

`kind = "TRADE"` (giao dịch crypto):

```
{ side:   "BUY" | "SELL",
  symbol: "ETH",
  usdtNotional: integer,          // USDT khớp lệnh, chưa gồm phí
  feeUsdt:      integer,          // phí tính bằng USDT; 0 nếu phí đã trừ vào lượng nhận
  qty:          integer,          // lượng crypto THỰC NHẬN (đã trừ phí bằng coin) 1e-8
  source: "PLAN" | "EXTRA" | "RESERVE"
}
```

**Không có trường tỷ giá nhập tay trên từng lệnh.** Giá vốn VND của một `TRADE` luôn đến từ
pool USDT (§8), không bao giờ từ một con số gõ riêng cho lệnh đó — đây là quyết định canonical
của `DEC-042` §4 (*"Do NOT create a hidden per-trade FX fallback"*).

`kind = "RESERVE"`:

```
{ type: "CONTRIBUTE" | "WITHDRAW",
  vndAmount: integer }
```

`kind = "PRICE"` (chỉ để định giá hiển thị, §16):

```
{ symbol: "ETH", priceUsdt: integer, usdVndRate: integer | null }
```

`price` **không phải** là dữ liệu tài chính: nó không đổi holdings, không đổi giá vốn, không
đổi bất kỳ đại lượng nào của kế hoạch. Nó chỉ vào ô "định giá hiện tại".

### 5.4 Thứ tự tất định

    ORDER = sort by (businessDate ASC, seq ASC)

`seq` cấp lúc tạo và **không** đổi khi sửa. Hệ quả (được kiểm bởi `SC-07`): hai event khác ngày →
ngày quyết định; hai event **cùng ngày** → event nhập sau đứng sau. Kết quả không phụ thuộc
`createdAt`, không phụ thuộc múi giờ máy, không phụ thuộc thứ tự thao tác của người dùng.

---

## 6. Treasury / P2P Accounting

### 6.1 P2P KHÔNG phải chi phí đầu tư

Đây là quy tắc phân loại, không phải chi tiết cài đặt. Mua USDT bằng VND **không** làm tăng
"đã đầu tư tháng này", **không** tiêu ngân sách kế hoạch, **không** đổi holdings. Nó chuyển
giá trị từ tài sản tiền tệ này sang tài sản tiền tệ khác (`INV-8`).

Lý do nó quan trọng: nếu P2P bị tính là đầu tư thì mọi lần nạp USDT sẽ giả vờ là một lần DCA,
và cả bốn con số của dashboard sai cùng lúc.

### 6.2 Hai chân của một giao dịch P2P là SỐ THỰC TẾ

Người dùng nhập **VND thực sự rời tài khoản** và **USDT thực sự vào ví**. Không nhập "tỷ giá"
và không nhập "phí" như hai trường riêng.

Hệ quả — mọi ngữ nghĩa phí biến mất khỏi mô hình:

- phí thu bên VND → `vndAmount` vốn đã lớn hơn → giá vốn USDT cao lên, **đúng**;
- phí thu bên USDT → `usdtAmount` vốn đã nhỏ hơn → giá vốn USDT cao lên, **đúng**;
- không còn khả năng nhập phí hai lần hoặc quên phí.

`rate` hiển thị = `vndAmount / usdtAmount`, là **dẫn xuất**, không lưu.

### 6.3 Pool USDT — trọng số bình quân (WAC)

Trạng thái dẫn xuất của pool USDT sau mỗi event:

    usdtQty      -- tổng USDT đang nắm
    usdtCostVnd  -- tổng VND đã bỏ ra để có số USDT đó
    usdtAvgVnd   -- = usdtCostVnd / usdtQty   (DẪN XUẤT, không lưu)

Quy tắc:

| Event | Tác động |
|---|---|
| opening | `usdtQty = opening.usdt.qty`; `usdtCostVnd = opening.usdt.costVnd` |
| `VND_TO_USDT` | `usdtQty += usdtAmount`; `usdtCostVnd += vndAmount` |
| `USDT_TO_VND` | giải phóng theo bình quân — xem §6.4 |
| `TRADE BUY` | giải phóng theo bình quân — xem §7 |
| `TRADE SELL` | `usdtQty += thu về`; `usdtCostVnd += thu về × usdtAvgVnd` (giữ nguyên bình quân) |

**Nhiều lô P2P ở các tỷ giá khác nhau được xử lý xong ngay tại đây**: WAC trộn chúng lại, không
cần lô, không cần FIFO, không cần ghép cặp.

### 6.4 Bán USDT lấy VND

    vndRelieved      = ROUND_VND( usdtAmount × usdtCostVnd / usdtQty )
    usdtQty         -= usdtAmount
    usdtCostVnd     -= vndRelieved
    realizedFxVnd    = vndAmount − vndRelieved      // DẪN XUẤT, chỉ để hiển thị

`realizedFxVnd` là lãi/lỗ tỷ giá đã thực hiện. Nó **được báo cáo**, **không** đổi giá vốn ETH,
**không** vào "đã đầu tư". L-1 dừng ở mức mô tả — không có sổ lãi lỗ riêng.

### 6.5 Quy tắc làm tròn và cạn pool

    ROUND_VND(x) = làm tròn nửa lên tới đồng nguyên

Khi `usdtQty` về đúng 0, **ép `usdtCostVnd = 0`** và ghi phần dư (nếu có) vào `realizedFxVnd` của
chính event làm cạn pool. Không có phần dư nào được phép sống sót (`INV-3`).

---

## 7. Crypto Trade Accounting

### 7.1 Trường của một lệnh mua

Người dùng nhập: `businessDate`, `symbol`, `usdtNotional`, `feeUsdt`, `qty` (lượng **thực nhận**),
`source`, `note`.

**`price` KHÔNG phải trường nhập.** `price = usdtNotional / qty` là dẫn xuất. Lý do: nhập cả ba
(`usdt`, `price`, `qty`) tạo ba nguồn sự thật cho một sự kiện và mở đường cho mâu thuẫn nội tại —
app hiện tại nhập `usdt` và `price` rồi suy ra `eth` (`app_logic.js:250`), nghĩa là lượng ETH
thật trên sàn không bao giờ vào được sổ.

### 7.2 Ngữ nghĩa phí

| Sàn thu phí bằng | Người dùng nhập | Xử lý |
|---|---|---|
| USDT | `feeUsdt` > 0 | cộng vào giá vốn: `usdtOut = usdtNotional + feeUsdt` |
| chính coin mua | `feeUsdt = 0`, `qty` = lượng **thực nhận** sau phí | tự động đúng |
| token thứ ba (BNB…) | `feeUsdt = 0` + ghi `note` | **KHÔNG** vào giá vốn ở L-1 MVP; ghi rõ giới hạn này trong UI |

### 7.3 Áp dụng vào holdings và giá vốn

    usdtOut      = usdtNotional + feeUsdt
    vndRelieved  = ROUND_VND( usdtOut × usdtCostVnd / usdtQty )     // §8.4

    ethQty      += qty
    ethCostUsdt += usdtOut
    ethCostVnd  += vndRelieved
    usdtQty     -= usdtOut
    usdtCostVnd -= vndRelieved

Bán crypto (`side = SELL`) giải phóng giá vốn theo **cùng một phương pháp WAC**:

    ethRelievedUsdt = ROUND( qty × ethCostUsdt / ethQty )
    ethRelievedVnd  = ROUND_VND( qty × ethCostVnd  / ethQty )

và cộng USDT thu về vào pool ở đúng bình quân VND hiện hành (§6.3), để việc bán không tự tạo ra
hay huỷ đi giá vốn VND.

### 7.4 Quy VND (`VND attribution`)

Xem §8. Tóm tắt một dòng: **VND cost của ETH = VND cost của số USDT đã tiêu để mua nó**, chứ
không phải `usdtOut × một tỷ giá tuỳ ý tại thời điểm nào đó`.

### 7.5 `source` — ba giá trị, một hệ quả

| `source` | Ý nghĩa | Vào `investedThisMonth`? | Vào `planInvested`? |
|---|---|---|---|
| `PLAN` | mua theo kế hoạch DCA | có | **có** |
| `EXTRA` | mua thêm ngoài kế hoạch (§13) | có | không |
| `RESERVE` | giải ngân quỹ dự phòng (§12) | có | không |

Mặc định `PLAN`. `RESERVE` **bắt buộc** có `note` không rỗng (đó chính là "reason" mà quỹ dự
phòng đòi hỏi).

---

## 8. VND + USDT Cost Basis

Đây là phần cốt lõi của tài liệu.

### 8.1 Bài toán

Dòng tiền thật:

    VND --(P2P, tỷ giá A)--> USDT --(để dành)--> USDT --(mua)--> ETH

Câu hỏi: khi mua ETH bằng USDT, **VND đã bỏ ra cho lượng ETH đó là bao nhiêu?**

Câu trả lời **SAI** (và là cách app hiện tại đang làm, `app_logic.js:251`):

    vndCost = usdt × vndRate          // vndRate do người dùng gõ tại thời điểm mua ETH

Sai vì: `vndRate` lúc mua ETH là **tỷ giá thị trường hôm đó**, không phải **giá đã trả** khi mua
số USDT đó. Nếu USDT được mua từ tháng trước ở tỷ giá khác, con số này bịa ra một giá vốn chưa
từng tồn tại. Nếu người dùng bỏ trống thì `vndCost = 0` và giá vốn VND **âm thầm biến mất**.

### 8.2 Phương pháp được chọn: WAC trên một pool USDT duy nhất

**Một pool USDT, bình quân gia quyền, giải phóng theo bình quân tại thời điểm chi.**

    usdtAvgVnd(t) = usdtCostVnd(t) / usdtQty(t)

Khi chi `usdtOut` để mua ETH:

    vndRelieved = ROUND_VND( usdtOut × usdtCostVnd / usdtQty )

Giá vốn VND đó **đi vào ETH**. Không có VND nào được tạo ra hay mất đi (`INV-3`).

Vì sao WAC chứ không phải tax lot: L-1 là app cá nhân, một người dùng, **không có nghĩa vụ thuế
hay kiểm toán bên ngoài** (`PROJECT_PROFILE.md` § Compliance). FIFO/LIFO/specific-ID chỉ khác WAC
ở phân bổ **lãi lỗ đã thực hiện** — thứ L-1 không tính. WAC cho cùng một tổng giá vốn, cần một
cặp số duy nhất `(qty, costVnd)` thay vì một bảng lô, và **bất biến dưới việc nhập muộn hay sửa
lô** — điều kiện sống còn cho §9. Đây là phương pháp đơn giản nhất còn bảo vệ được.

### 8.3 Sáu tình huống mà phương pháp phải trả lời

| # | Tình huống | Lời giải |
|---|---|---|
| 1 | Nhiều lô P2P khác tỷ giá | WAC trộn tự động (§6.3). Không cần ghép cặp. `SC-04` |
| 2 | Đã có sẵn USDT đầu kỳ | `openingPosition.usdt = {qty, costVnd}` nạp thẳng vào pool. `SC-01` |
| 3 | Chỉ dùng một phần USDT | Giải phóng theo tỷ lệ; bình quân **không đổi**. `SC-03` |
| 4 | Phí sàn | §7.2 — phí USDT cộng vào `usdtOut` nên vào cả hai giá vốn |
| 5 | Nguồn gốc USDT không xác định (không cần ghép lô — WAC đã giải quyết ở mục 1; nhưng nếu basis THẬT SỰ không biết) | §8.5 — chính sách STRICT / FAIL-VISIBLE (`DEC-042`) |
| 6 | Không biết giá vốn VND đầu kỳ | `costVnd = null` → mọi số VND của tài sản đó = `UNKNOWN`, hiển thị `—`. **Không** thay bằng 0, **không** thay bằng tỷ giá thị trường (`INV-11`) |

### 8.4 Pool thiếu USDT — thất bại phải NHÌN THẤY ĐƯỢC

Khi replay gặp `usdtOut > usdtQty` (thường do thiếu một event P2P chưa nhập, hoặc nhập nhầm ngày):

1. Trạng thái dẫn xuất được đánh dấu `LEDGER_INCONSISTENT`, kèm **id và ngày của event đầu tiên
   gây ra**;
2. dashboard hiện banner cảnh báo thường trực, **không** ẩn được;
3. phần USDT bị thiếu (`usdtOut` vượt `usdtQty`) được xử lý theo đúng §8.5: **không** suy diễn
   tỷ giá nào cho phần thiếu — giá vốn VND của phần đó là `UNKNOWN`, lan truyền theo `INV-11`;
   phần đã được pool phủ vẫn tính bằng bình quân như bình thường;
4. app **không** tự sửa dữ liệu, **không** tự thêm event bù, **không** tự bịa một tỷ giá cho
   riêng lệnh gây thiếu hụt (`DEC-042` §4 — cấm fallback FX ẩn theo từng lệnh).

Đây là hiện thực hoá `DEC-011` Owner Acceptance điểm 9 (`DEC-041` D giữ nguyên): sai tiền phải
`fail visibly`.

### 8.5 Khi giá vốn VND không xác định — chính sách STRICT / FAIL-VISIBLE (`DEC-042`, QUYẾT ĐỊNH)

**Mô hình canonical**, đúng nguyên văn Owner Decision `DEC-042` §4: USDT là một tài sản có giá
vốn VND riêng. Các khoản mua USDT đã biết (P2P, opening) đi vào **một** pool WAC duy nhất (§8.2).
Khi USDT được chi để mua crypto: lượng USDT rời pool; giá vốn VND tương ứng được giải phóng theo
bình quân của pool (§8.2); giá vốn đó trở thành một phần giá vốn VND của crypto. **Không cần**
ghép chính xác lô P2P với lệnh mua — WAC đã tự giải quyết (§8.3-1).

**Khi giá vốn VND của USDT thật sự không biết** (ví dụ: số dư USDT đầu kỳ không rõ giá vốn lịch
sử — `openingPosition.usdt.costVnd = null`, hoặc phần USDT thiếu ở §8.4), spec **CẤM**:

- dùng tỷ giá thị trường hiện tại;
- dùng tỷ giá thị trường tại ngày giao dịch crypto;
- dùng 0;
- bịa một tỷ giá lịch sử ngụ ý (implied historical rate);
- tạo bất kỳ ô nhập tỷ giá nào theo từng lệnh để "vá" trường hợp này (**cấm hidden per-trade FX
  fallback** — đây là lý do trường `vndRateOverride` bị loại khỏi schema `TRADE` ở §5.3).

**Thay vào đó, spec YÊU CẦU:**

1. giữ nguyên số lượng USDT/crypto — không đụng tới phần định lượng;
2. giữ nguyên phần giá vốn USDT đã biết (`ethCostUsdt` không bị ảnh hưởng);
3. lan truyền phần giá vốn VND bị ảnh hưởng thành `UNKNOWN` (`INV-11`);
4. hiển thị điều kiện này **thấy được** — banner + cờ `UNKNOWN_VND_BASIS` (§16.4), không âm thầm.

**Đường sửa duy nhất:** Owner có thể sau đó cung cấp giá vốn VND đúng của USDT đầu kỳ qua một
**thao tác sửa `openingPosition` tường minh** (§14, §15 — đã sẵn có, sửa được) hoặc bằng cách bổ
sung event `TREASURY` còn thiếu nếu nguyên nhân là dữ liệu chưa nhập đủ. Đây **không** phải một
event mới, không phải một cơ chế mới — chỉ là dùng đúng khả năng sửa/nhập đã có trong sổ.

---

## 9. Event Ledger & Derived State

### 9.1 Hàm dẫn xuất duy nhất

    derive(openingPosition, plan, events, asOfDate) -> DerivedState

`derive` là **hàm thuần**: không đọc đồng hồ (ngày "hôm nay" là **tham số** `asOfDate`), không
đọc múi giờ máy, không đọc `createdAt`. Đây là điều kiện để test được và là điều kiện để `SC-08`
có nghĩa.

### 9.2 `DerivedState` — không có trường nào trong đây được lưu

```
{
  holdings: { ETH: { qty, costUsdt, costVnd|UNKNOWN,
                     avgCostUsdt, avgCostVnd|UNKNOWN } },
  usdt:     { qty, costVnd, avgVnd },
  vnd:      { balance },
  reserve:  { balance },
  month: {                                  // cho tháng của asOfDate
    monthlyBudgetVnd, carryInVnd, plannedBudgetVnd,
    investedThisMonthVnd,                   // MỌI source
    planInvestedVnd,                        // chỉ source = PLAN
    remainingPlannedBudgetVnd,
    nextPlannedDate, nextPlannedAmountVnd
  },
  flags: [ "LEDGER_INCONSISTENT" | "FUTURE_DATED_EVENTS" | "UNKNOWN_VND_BASIS" | ... ],
  firstOffendingEventId: string | null
}
```

### 9.3 Vì sao không cộng dồn

`edit`, `delete`, và **nhập muộn** đều là thao tác chèn/sửa vào **giữa** chuỗi thời gian. Với
state cộng dồn, chúng đòi một phép "hoàn tác" chính xác cho mọi loại event — và phép hoàn tác đó
sai bất cứ khi nào thứ tự đã ảnh hưởng tới kết quả (WAC thì luôn ảnh hưởng). Với replay, cả ba
thao tác là **cùng một** thao tác: đổi mảng, chạy lại. Không có đường nào cho hỏng state tăng dần.

Chi phí: replay toàn bộ mỗi lần render. Với quy mô cá nhân (bậc `10^3` event trong nhiều năm),
đây là vài mili-giây. Không cần tối ưu ở L-1 MVP.

### 9.4 Trường dẫn xuất không được trở thành nguồn sự thật cạnh tranh

Cấm lưu vào durable state: `price`, `rate`, `avgCost*`, `ethQty`, `costUsdt`, `costVnd`,
`treasury.*`, `reserveBalance`, `invested*`, `remaining*`, `next*`. Nếu một con số dẫn xuất cần
xuất hiện trong file export, nó nằm trong khối `derivedSnapshot` được đánh dấu rõ **`INFORMATIONAL
— NOT IMPORTED`**, và import **bỏ qua** khối đó (`INV-1`).

---

## 10. Date / Time / Currency Semantics

Mục này giải quyết dứt điểm `H-41` (`B3`, `B4`, `B7`, `B9`).

### 10.1 Hai loại thời gian, tách hẳn

| Trường | Kiểu | Dùng cho |
|---|---|---|
| `businessDate` | `"YYYY-MM-DD"`, **chuỗi**, người dùng nhập | **mọi** phép tính tài chính |
| `createdAt` / `updatedAt` | ISO-8601 UTC instant | metadata, sắp xếp hiển thị "mới nhập", chẩn đoán |

`businessDate` **không** được chuyển sang `Date` rồi tính. Tháng = `businessDate.slice(0,7)`.
So sánh ngày = so sánh chuỗi. Không có `getMonth()`, không có `toISOString()` trong đường tính
tiền (`INV-6`).

### 10.2 Múi giờ canonical

    TZ = "Asia/Ho_Chi_Minh"

Múi giờ chỉ xuất hiện ở **đúng một chỗ**: hàm tính "hôm nay".

    today() = Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Ho_Chi_Minh" }).format(new Date())

Kết quả đưa vào `derive()` dưới dạng tham số `asOfDate`. Không có chỗ thứ hai nào trong mã được
phép hỏi giờ hệ thống. Điều này diệt `B7` (`monthKey` giờ local trộn với `today` UTC) ở gốc.

### 10.3 Tháng = tháng lịch

    currentMonth = asOfDate.slice(0, 7)

**Không phải** khoá tháng lớn nhất trong dữ liệu (`B3`). Một tháng không có event vẫn là một
tháng có kế hoạch, có `plannedBudget`, có `carryOut`.

### 10.4 Tiền — số nguyên, không float

| Đại lượng | Đơn vị lưu | Trần an toàn |
|---|---|---|
| VND | integer đồng | `9.0e15` đồng |
| USDT | integer micro-USDT (1e-6) | `9.0e9` USDT |
| crypto qty | integer 1e-8 | `9.0e7` coin |

Mọi giá trị nằm sâu trong `Number.MAX_SAFE_INTEGER` với quy mô cá nhân. **Không** giá trị float
nào được ghi xuống durable state (`INV-5`) — diệt `B9` (`102000.00000000001`).

**Giới hạn phải nói rõ:** lượng crypto lưu ở 8 chữ số thập phân, không phải 18. Fill của sàn được
niêm yết ở ≤ 8 chữ số và người dùng nhập tay, nên đây là mức đủ; nhưng nếu sau này cần nhập một
số dư on-chain đầy đủ 18 chữ số thì đơn vị lưu phải đổi, và đó là một thay đổi schema.

### 10.5 Làm tròn và đối chiếu

Chia một khoản VND thành `n` phần: `n−1` phần đầu làm tròn nửa lên, phần **cuối** nhận phần dư,
để tổng khớp **chính xác** khoản gốc (`INV-13`). Quy tắc này áp cho `plannedAmount` mỗi mốc lịch
và cho mọi phép phân bổ khác.

### 10.6 Nhập cho tháng tương lai

**Cho phép**, kèm cảnh báo. Event có `businessDate > asOfDate`:

- **vẫn** vào holdings và giá vốn (sổ là sổ; một đường tính duy nhất, không tách chân trời);
- **không** vào `investedThisMonth` của tháng hiện tại — nó thuộc tháng của chính nó;
- **không** sinh `carryOut` (chỉ tháng đã đóng mới sinh, §11.4);
- kích hoạt cờ `FUTURE_DATED_EVENTS` và một badge trên từng dòng lịch sử.

Lý do cho phép thay vì chặn: ngày ghi trước là **gần như luôn** một lỗi gõ (nhầm năm, đảo
ngày/tháng), và một banner nhìn thấy được sửa được lỗi đó tốt hơn một thông báo từ chối làm người
dùng gõ đại một ngày khác cho qua.

### 10.7 Định danh ổn định

`id` duy nhất toàn cục, cấp một lần, **không bao giờ tái sử dụng** kể cả sau khi xoá. `seq` tăng
đơn điệu, cấp lúc tạo, **không** đánh số lại. Sửa event **giữ nguyên** cả `id` lẫn `seq`.

---

## 11. Monthly DCA Plan

### 11.1 Mô hình — QUYẾT ĐỊNH (`DEC-042`, câu 1)

**QUYẾT ĐỊNH: số tiền cố định hằng tháng + danh sách ngày trong tháng** (`scheduleDays`), mặc
định `[3, 13, 23]`. Owner đổi `scheduleDays` được, chỉ áp dụng **về sau** (không hồi tố — một
version `plan` mới với `effectiveFrom` ở tháng thay đổi, §5.1).

    plannedPerSlot = SPLIT_VND(monthlyBudgetVnd, scheduleDays.length)   // §10.5

Một cơ chế duy nhất phủ được cả nhu cầu "hằng tuần" (`[1, 8, 15, 22]`) lẫn "ngày tuỳ chọn", nên
spec **không** thêm cơ chế lịch thứ hai. **Không** có timing thuật toán (`N-3`, `INV-10`) — lịch
tất định hoàn toàn theo `scheduleDays`, không đổi theo Buy Score, regime hay tín hiệu thị trường.

**Ràng buộc tường minh của Owner:** `plannedPerSlot`/`plannedAmount` **phải** dẫn xuất từ chính
`plan` (§5.1, §10.5) — **không** được ghép hay tính lại qua các pool `Base`/`Smart`/`Opportunity`
cũ của V2.1.5. Các pool đó đã `DROP_LEGACY_ONLY` tại §17.2 và không tồn tại trong schema L-1.

### 11.2 Các đại lượng

| Đại lượng | Định nghĩa |
|---|---|
| `monthlyBudgetVnd` | từ version kế hoạch áp dụng cho tháng đó |
| `carryInVnd` | §11.4 |
| `plannedBudgetVnd` | `monthlyBudgetVnd + carryInVnd` |
| `investedThisMonthVnd` | Σ `vndRelieved` của **mọi** `TRADE BUY` trong tháng, mọi `source` |
| `planInvestedVnd` | Σ `vndRelieved` của `TRADE BUY` có `source = PLAN` trong tháng |
| `remainingPlannedBudgetVnd` | `max(0, plannedBudgetVnd − planInvestedVnd)` |
| `nextPlannedDate` | §11.3 |
| `nextPlannedAmountVnd` | §11.3 |

**Đơn vị đo mức tuân thủ kế hoạch là VND cost basis của lệnh mua crypto** — không phải USDT chi
ra, không phải VND nạp P2P. Điều này bám đúng §6.1: P2P không phải đầu tư.

### 11.3 Hành động kế tiếp — theo SỐ TIỀN, không theo Ô LỊCH

    cumulativePlannedThrough(d) = Σ plannedPerSlot cho mọi mốc lịch ≤ d trong tháng

    nextPlannedDate = mốc lịch d nhỏ nhất trong tháng hiện tại thoả
                        cumulativePlannedThrough(d) > planInvestedVnd
                      và d >= asOfDate;
                      nếu không có -> mốc lịch đầu tiên của tháng kế tiếp

    nextPlannedAmountVnd = clamp( cumulativePlannedThrough(nextPlannedDate) − planInvestedVnd,
                                  0, remainingPlannedBudgetVnd )

Vì sao **không** ghép từng lệnh mua với từng ô lịch: ghép cặp là giòn (mua sớm một ngày, mua
tách làm hai lần, nhập muộn — mỗi cái đều phá ghép cặp) và nó tạo một trạng thái "ô đã dùng" phải
lưu, tức là một nguồn sự thật cạnh tranh (`INV-1`). Mô hình theo số tiền không lưu gì cả và tự
sinh ra hành vi bắt kịp trong tháng một cách tự nhiên.

### 11.4 Carry — QUYẾT ĐỊNH (`DEC-042`, câu 2)

**QUYẾT ĐỊNH: `CAPPED_CARRY`, `carryCapMonths = 1`** (carry tối đa = một tháng ngân sách bình
thường). Công thức:

    carryOut(m)  = max(0, plannedBudgetVnd(m) − planInvestedVnd(m))     // CHỈ tháng đã đóng
    carryIn(m)   = min( carryOut(m−1), monthlyBudgetVnd(m) × carryCapMonths )

Ràng buộc: `carry` chỉ tích luỹ từ các tháng `≥ plan.startMonth` và `≥ openingPosition.asOf`.
Tháng hiện tại và tháng tương lai **không** sinh `carryOut` (chúng chưa đóng).

**Ràng buộc tường minh của Owner:** cài đặt phải giữ **tách biệt** ba đại lượng — ngân sách
tháng hiện hành (`monthlyBudgetVnd`), phần carry-forward (`carryInVnd`), và số tiền đã đầu tư
thật (`investedThisMonthVnd`/`planInvestedVnd`) — **không** được gộp thành một số dư mờ. Ba
trường này đã tách sẵn trong `DerivedState.month` (§9.2); đây là xác nhận, không phải thay đổi
schema.

### 11.5 Mua thêm ngoài kế hoạch ảnh hưởng thế nào

| Đại lượng | `EXTRA` / `RESERVE` có ảnh hưởng? |
|---|---|
| `investedThisMonthVnd` | **có** — đó là tiền thật đã xuống |
| holdings, giá vốn | **có** |
| `planInvestedVnd` | **không** |
| `remainingPlannedBudgetVnd` | **không** |
| `carryOut` | **không** |
| `nextPlannedDate` / `nextPlannedAmountVnd` | **không** |

Đây là lời giải cho câu hỏi "extra ảnh hưởng gì tới adherence": **một** con số đo tuân thủ
(`planInvestedVnd`), **một** con số đo dòng tiền thật (`investedThisMonthVnd`), và chúng được
phép khác nhau.

---

## 12. Reserve

### 12.1 Tách bạch

    ngân sách DCA hằng tháng   -- kỷ luật, tiêu theo lịch
    vốn dự phòng (reserve)     -- vốn cơ động, tiêu khi NGƯỜI DÙNG quyết định

Hai thứ này **không** thông nhau. `reserve` không được cấp vốn từ ngân sách chưa tiêu, và giải
ngân `reserve` không bù cho một tháng đã hụt kế hoạch (`INV-9`). **QUYẾT ĐỊNH (`DEC-042`, câu
3):** tách bạch hoàn toàn — quỹ dự phòng do người dùng điều khiển, nạp thủ công, và giải ngân
**không** tính vào tuân thủ kế hoạch DCA.

### 12.2 Reserve là một EARMARK dẫn xuất, không phải một ví riêng

    reserveBalanceVnd = openingPosition.reserveVnd
                      + Σ RESERVE(CONTRIBUTE).vndAmount
                      − Σ RESERVE(WITHDRAW).vndAmount
                      − Σ vndRelieved của TRADE BUY có source = RESERVE

Ba thao tác người dùng, không có thao tác thứ tư:

| Thao tác | Cách ghi |
|---|---|
| nạp dự phòng | `RESERVE(CONTRIBUTE, vndAmount, businessDate)` |
| rút dự phòng ra (không mua) | `RESERVE(WITHDRAW, vndAmount, businessDate)` |
| **giải ngân dự phòng** | một `TRADE BUY` với `source = RESERVE` và `note` **bắt buộc** |

Vì sao không có event `DEPLOY` riêng: một `DEPLOY` riêng phải khớp số với lệnh mua tương ứng, tạo
ra hai nguồn sự thật cho cùng một hành động và một lớp lỗi lệch số. Gộp làm một, `reason` sống
trên `note` bắt buộc của chính lệnh mua.

`reserveTarget` (mục tiêu) là **cấu hình hiển thị**, không tham gia phép tính nào.

### 12.3 Cấm tuyệt đối

**Không** Buy Score, regime, ladder, Opportunity Score, Crash logic, hay bất kỳ tín hiệu/đại
lượng dẫn xuất nào của V2.1.5 được tạo, gợi ý, hay định cỡ một `TRADE BUY` `source = RESERVE`
(`DEC-042` §3, nguyên văn). Giải ngân dự phòng **chỉ** tồn tại như một event do người dùng nhập
tay (`INV-10`, `DEC-041` B). Ngữ nghĩa `Opportunity Score` / `Crash` của V2.1.5 **không** được
mang sang dưới bất kỳ tên gọi nào.

---

## 13. Extra Purchases

Mua ngoài kế hoạch được ghi bằng `source = EXTRA`, giữ **định danh riêng vĩnh viễn** trong sổ.

Hệ quả đã nêu ở §11.5. Bổ sung: bộ lọc lịch sử phải lọc được theo `source`, và báo cáo tháng phải
tách được `planInvested` / `extra` / `reserve` — nếu không, con số "đã đầu tư" trở nên không giải
thích được và người dùng mất khả năng biết mình có giữ kỷ luật hay không.

---

## 14. Opening Position

### 14.1 Mục đích

Cho phép chủ sở hữu **bắt đầu dùng CoinDCA mà không phải dựng lại nhiều năm lịch sử**. Đây là
điều kiện để app dùng được thật, không phải một tiện ích.

### 14.2 Thông tin tối thiểu

| Bắt buộc | Trường |
|---|---|
| có | `asOf` |
| có | mỗi tài sản: `symbol`, `qty` |
| nên có | mỗi tài sản: `costUsdt`, `costVnd` (hoặc `avgCostUsdt` / `avgCostVnd` — app nhân ra) |
| nên có | `usdt.qty`, `usdt.costVnd` |
| tuỳ chọn | `vnd.qty`, `reserveVnd`, `note` |

Thiếu `costVnd` → `null`, không phải 0 (§8.3 tình huống 6; `INV-11`).

### 14.3 Opening KHÔNG phải một giao dịch

| | opening | trade |
|---|---|---|
| vào `investedThisMonth` | **không** | có |
| vào `planInvested` / adherence | **không** | tuỳ `source` |
| xuất hiện trong lịch sử giao dịch | **không** — là một dòng "Số dư đầu kỳ" riêng | có |
| vào holdings và giá vốn | **có** | có |
| sửa được | có, một chỗ duy nhất | có |

`INV-7`: không event nào được có `businessDate < openingPosition.asOf`. Vi phạm → từ chối lưu,
nêu rõ lý do (nếu chấp nhận, event đó sẽ bị đếm hai lần: một lần trong opening, một lần trong sổ).

---

## 15. Edit / Delete

### 15.1 Mọi event tài chính đều có

- `id` ổn định;
- `businessDate` do người dùng nhập;
- `createdAt` / `updatedAt`;
- sửa được **mọi** trường nghiệp vụ, kể cả `businessDate`;
- xoá được.

Điều này bao trùm `TREASURY`, `TRADE`, `RESERVE`, `PRICE`, và `openingPosition` — diệt `B5`,
`B6`.

### 15.2 Sửa

Sửa **giữ nguyên** `id` và `seq`, cập nhật `updatedAt`, rồi `derive()` chạy lại toàn bộ. Không có
phép "hoàn tác tác động cũ" nào tồn tại trong mã (`SC-05`).

### 15.3 Xoá — HARD DELETE, kèm snapshot bắt buộc

Quyết định: **xoá cứng**, không tombstone.

Lý do: tombstone tạo ra một lớp trạng thái thứ hai mà **mọi** phép dẫn xuất phải nhớ lọc — quên
lọc ở một chỗ là một lỗi tiền im lặng, đúng loại lỗi mà §9 sinh ra để diệt. Nhu cầu truy vết
được đáp ứng đủ bởi ba thứ rẻ hơn nhiều:

1. `createdAt` / `updatedAt` trên mọi event;
2. **snapshot export đầy đủ, tự động, trước mọi thao tác phá huỷ** — import, wipe, migration
   (`INV-14`) — diệt `B8` (`app_logic.js:1420` hiện chỉ `confirm()` một lần rồi ghi state rỗng);
3. export thủ công bất cứ lúc nào.

L-1 là sổ cá nhân, không có nghĩa vụ kiểm toán bên ngoài; nếu nghĩa vụ đó xuất hiện, tombstone là
một thay đổi schema về sau, không phải chi phí phải trả bây giờ.

Xoá `openingPosition` được phép nhưng cảnh báo riêng: nó thường làm mọi giá vốn thành `UNKNOWN`.

---

## 16. Dashboard Contract

**Đây là hợp đồng THÔNG TIN. Không thiết kế thị giác trong tài liệu này.**

### 16.1 Khối chính — 4 con số + 1 hành động

| # | Nhãn | Nguồn | Ghi chú |
|---|---|---|---|
| 1 | Ngân sách tháng | `plannedBudgetVnd` | phụ đề khi `carryInVnd > 0`: "gồm `X` chuyển từ tháng trước" |
| 2 | Đã đầu tư tháng này | `investedThisMonthVnd` | phụ đề khi ≠ `planInvestedVnd`: tách `kế hoạch / thêm / dự phòng` |
| 3 | Còn lại theo kế hoạch | `remainingPlannedBudgetVnd` | |
| 4 | Số dư dự phòng | `reserveBalanceVnd` | |
| 5 | **Mua kế tiếp** | `nextPlannedDate` + `nextPlannedAmountVnd` | **một hành động, không phải một khuyến nghị** |

Ô số 5 nói **kế hoạch của chính người dùng nói gì**. Nó **không** nói nên mua hay nên đợi, không
có `GO` / `WAIT`, không có `Action box` (`DEC-041` B; `N-4`, `N-6`).

### 16.2 Khối dưới

| Nhãn | Nguồn |
|---|---|
| Đang nắm giữ | `holdings.ETH.qty` |
| Giá vốn TB (USDT) | `avgCostUsdt` |
| Giá vốn TB (VND) | `avgCostVnd`, hoặc `—` khi `UNKNOWN` |
| Định giá hiện tại | chỉ khi có `priceMark` **hợp lệ** — xem §16.3 |

### 16.3 "Giá thị trường hợp lệ"

Một `priceMark` hợp lệ khi `businessDate ≥ asOfDate − 1 ngày`. Ngoài ngưỡng đó: hiển thị `—` kèm
tuổi của giá ("giá gần nhất: 12 ngày trước"). **Không** ngoại suy, **không** dùng giá cũ như giá
hiện tại. Định giá là `DESCRIPTIVE` và không vào bất kỳ phép tính giá vốn hay kế hoạch nào.

### 16.4 Banner bắt buộc

`LEDGER_INCONSISTENT` (§8.4), `FUTURE_DATED_EVENTS` (§10.6), `UNKNOWN_VND_BASIS` (§8.3-6), trạng
thái persistence chưa xác nhận. Không banner nào ẩn được bằng một lần bấm.

---

## 17. Migration From Legacy State

### 17.1 Nguyên tắc

Dữ liệu app hiện tại **không được âm thầm trở thành sự thật tài chính L-1**, vì `B1`–`B10` tồn
tại (`DEC-041` K.2, `H-41`). Migration là một thủ tục có kiểm chứng, không phải một phép đổi tên
trường.

### 17.2 Phân loại từng trường legacy

| Trường legacy (`ethdca.tracker/1`) | Phân loại | Xử lý |
|---|---|---|
| `p2p[].{vnd, usdt}` | `OWNER_CONFIRMATION_REQUIRED` | trở thành `TREASURY`; nhưng `ts` là **thời điểm bấm nút**, không phải ngày giao dịch (`B4`) → Owner xác nhận `businessDate` từng dòng |
| `p2p[].{fee, rate}` | `RECALCULATE` | bỏ; §6.2 chỉ dùng hai chân thực tế. `vndAmount = vnd + fee` cho `VND_TO_USDT`, `= vnd − fee` cho `USDT_TO_VND` |
| `trades[].{usdt, fee, eth}` | `OWNER_CONFIRMATION_REQUIRED` | trở thành `TRADE`; `businessDate` xác nhận từng dòng (`B4`) |
| `trades[].price` | `DROP_LEGACY_ONLY` | dẫn xuất ở L-1 (§7.1) |
| `trades[].{vndRate, vndCost}` | `RECALCULATE` | **bỏ hoàn toàn**; giá vốn VND tính lại bằng WAC (§8.2). Đây chính là con số sai mô tả ở §8.1 |
| `trades[].src` (`BASE`/`SMART`/`OPPORTUNITY`) | `DROP_LEGACY_ONLY` | không có nghĩa dưới L-1; **mọi** trade legacy nhận `source = EXTRA` — chúng có trước kế hoạch L-1 nên không được tiêu ngân sách kế hoạch L-1 |
| `trades[].{recPrice, shortfallBps, zone}` | `DROP_LEGACY_ONLY` | khái niệm V2.1.5 |
| `eth`, `costUsdt`, `costVnd` | `RECALCULATE` | **không** import; dùng làm **oracle đối chiếu** — xem §17.3 |
| `treasury.{vnd, usdt}` | `RECALCULATE` | tính lại; dùng làm oracle; float → integer, chênh lệch làm tròn phải báo cáo |
| `months[].contribution` | `OWNER_CONFIRMATION_REQUIRED` | có thể là bản ghi duy nhất về VND đã nạp; Owner chọn: nhập thành `openingPosition.vnd` hay bỏ |
| `months[].{base, smart, oppAdded, oppOverflow}`, `oppFund` | `DROP_LEGACY_ONLY` | pool Base/Smart/Opportunity không tồn tại dưới L-1 |
| `ladders[]`, `zones` | `DROP_LEGACY_ONLY` | `DEC-041` B cấm ladder/zone sinh hành động; `WP-C3` `CANCELLED` |
| `extraDays[]`, `seed.history` | `SAFE_TO_MIGRATE` | vào kho giá `RESEARCH_ONLY`; **không** phải sự thật tài chính |
| `ledger[]` | `SAFE_TO_MIGRATE` | lưu trữ **chỉ đọc**, gắn nhãn `LEGACY_ARCHIVE`; **không** phép dẫn xuất nào được đọc |
| `schema`, `rev` | `DROP_LEGACY_ONLY` | schema mới `coindca.ledger/2` |
| Buy Score / regime / unlock / spacing (dẫn xuất lúc chạy) | `NOT_IN_L1_MVP` | §18 |

### 17.3 Đối chiếu bắt buộc

Sau khi dựng sổ mới, replay và so với accumulator legacy:

    |ethQty_new − legacy.eth|             <= 1e-8
    |usdtQty_new − legacy.treasury.usdt|  <= 1e-6
    |vndBalance_new − legacy.treasury.vnd| <= 1 đồng
    |ethCostUsdt_new − legacy.costUsdt|   <= 1e-6

Lệch quá ngưỡng = **thất bại migration**, không phải cảnh báo. Cách này biến chính các
accumulator có lỗi thành một phép kiểm tra độc lập: nếu chúng khớp, `B1`/`B2` chưa từng phát tác
trên dữ liệu thật; nếu lệch, người dùng cần biết **trước khi** tin vào sổ mới.

Ngoại lệ có chủ đích: `costVnd` **không** đối chiếu, vì công thức legacy (§8.1) sai theo thiết kế
và lệch là điều **được kỳ vọng**. Chênh lệch được báo cáo cho Owner như một con số cần biết,
không phải một điều kiện thất bại.

### 17.4 Hai loại kết quả bất thường — DỪNG hẳn, hay TIẾP TỤC kèm cờ THẤY ĐƯỢC

`DEC-042` §4 phân biệt rõ hai việc: (a) dữ liệu **không toàn vẹn** (số lượng có thể sai) — migration
phải **dừng**; (b) chỉ **giá vốn VND không xác định** được (số lượng vẫn đúng) — migration
**hoàn tất**, không hoá thân trường thiếu thành một số bịa, nhưng cờ lên **thấy được** để Owner
sửa sau qua `openingPosition` (§8.5). Owner tường minh: *"Owner may later supply a valid opening
USDT VND basis through an explicit correction/opening-position action"* — nghĩa là migration
không cần chờ số đó mới hoàn tất.

**A. Điều kiện DỪNG — migration không ghi gì, xuất báo cáo:**

| # | Điều kiện |
|---|---|
| `M-1` | một event thiếu `businessDate` mà Owner không xác nhận |
| `M-2` | replay làm `usdtQty` hoặc `ethQty` âm ở bất kỳ bước nào — dữ liệu tự mâu thuẫn về SỐ LƯỢNG, không chỉ thiếu giá vốn |
| `M-3` | đối chiếu §17.3 vượt ngưỡng |
| `M-4` | tồn tại ladder/zone có `filled_vnd > 0` — nghĩa là `B1`/`B2` đã phát tác và số tiền pool không đáng tin |

**B. Điều kiện TIẾP TỤC kèm cờ — migration hoàn tất, không dừng:**

| # | Điều kiện | Xử lý |
|---|---|---|
| `W-1` | một `TRADE` hoặc `openingPosition` có phần USDT chi ra mà giá vốn VND không truy được (không có phủ pool, không có opening cost) | nhập số lượng bình thường; `ethCostVnd`/`usdtCostVnd` phần đó = `UNKNOWN` (§8.5); ghi vào báo cáo migration **và** cờ `UNKNOWN_VND_BASIS` trên dashboard; **không** dừng, **không** bịa tỷ giá |

Đây **không** làm yếu nguyên tắc "migration phải fail visibly khi ý nghĩa tài chính mơ hồ": một
con số bị đánh dấu `UNKNOWN` và hiển thị thường trực **là** thất bại thấy được — chỉ khác ở chỗ
nó không chặn quyền truy cập vào phần dữ liệu còn lại (số lượng) mà spec **biết chắc** là đúng.

### 17.5 Tính nguyên tử

Migration ghi **toàn bộ** sổ mới hoặc **không ghi gì** (`INV-12`). Trước khi chạy: snapshot đầy
đủ dữ liệu legacy (`INV-14`). Dữ liệu legacy **không bị xoá** bởi migration.

---

## 18. Firebase / Auth Readiness Constraint

**Tài liệu này KHÔNG thi hành `H-42`.** Nó ghi ràng buộc, đúng theo `DEC-041` K.1.

    TRƯỚC KHI DÙNG VỚI TIỀN THẬT, CoinDCA PHẢI:

    R-1  có project Firebase RIÊNG cho CoinDCA;
    R-2  KHÔNG dùng chung ranh giới Hosting / Firestore rules với Tín Phát Content
         (FB-1: Anonymous Auth + rules `signedIn()` của Content mở cửa ghi cho khách vô danh;
          FB-2: `firebase.json` thiếu khoá `site` -> deploy đè Hosting site của Content);
    R-3  có xác thực cho danh tính MỘT CHỦ SỞ HỮU, BỀN qua đổi thiết bị và reset trình duyệt
         (FB-4: Anonymous UID nằm trong IndexedDB -> xoá site data = mất dữ liệu của chính mình);
    R-4  mọi thao tác import / wipe / migration có snapshot khôi phục được trước khi ghi
         (INV-14);
    R-5  `firestore.rules` không còn placeholder `OWNER_UID_REQUIRED` khi deploy
         (FB-3: deploy lại từ repo sẽ tự khoá chính chủ dự án ra ngoài).

Google Sign-in **có thể** là lựa chọn được khuyến nghị cho `R-3`, nhưng việc chọn và cài đặt
thuộc một capability sau (§24 bước C). Tài liệu này không chọn thay.

**Cảnh báo còn hiệu lực:** *"dừng dùng app với tiền thật"* vẫn còn hiệu lực cho tới khi pivot L-1
hoàn tất (`H-41`, `DEC-041` K.2).

---

## 19. Golden Accounting Scenarios

Toàn bộ số liệu dưới đây là **tổng hợp (synthetic)**, không phải dữ liệu thật của chủ dự án
(`DEC-041` C). **Không cài đặt test trong phiên này** — đây là hợp đồng mà cài đặt tương lai phải
vượt qua.

Trạng thái nền dùng chung cho `SC-01`…`SC-08`:

    plan: monthlyBudgetVnd = 20.000.000; scheduleDays = [3, 13, 23];
          carryPolicy = CAPPED_CARRY, carryCapMonths = 1; startMonth = 2026-01

### SC-01 — Opening ETH position

    INPUT   openingPosition asOf = 2026-01-01
              ETH  qty 0,5      costUsdt 1.200,000000   costVnd 30.000.000
              USDT qty 200,000000                       costVnd  5.000.000
    EXPECT  ethQty 0,5 · ethCostUsdt 1.200 · avgCostUsdt 2.400/ETH
            ethCostVnd 30.000.000 · avgCostVnd 60.000.000/ETH
            usdtQty 200 · usdtCostVnd 5.000.000 · usdtAvgVnd 25.000
            investedThisMonth(2026-01) = 0 · planInvested(2026-01) = 0
    INV     INV-1 · opening KHÔNG BAO GIỜ là "đã đầu tư" (§14.3)

### SC-02 — VND → USDT P2P purchase

    INPUT   TREASURY 2026-01-05 VND_TO_USDT vndAmount 25.600.000 usdtAmount 1.000,000000
    EXPECT  usdtQty 1.200 · usdtCostVnd 30.600.000 · usdtAvgVnd 25.500
            ethQty, ethCostUsdt, ethCostVnd KHÔNG ĐỔI
            investedThisMonth(2026-01) = 0
    INV     INV-8 — P2P không phải chi phí đầu tư (§6.1)

### SC-03 — USDT → ETH purchase (có phí bằng USDT)

    INPUT   TRADE 2026-01-06 BUY ETH
              usdtNotional 600,000000 · feeUsdt 0,600000 · qty 0,25 · source PLAN
    EXPECT  usdtOut 600,6 · vndRelieved = ROUND(600,6 × 25.500) = 15.315.300
            ethQty 0,75 · ethCostUsdt 1.800,6 · avgCostUsdt 2.400,8/ETH
            ethCostVnd 45.315.300 · avgCostVnd 60.420.400/ETH
            usdtQty 599,4 · usdtCostVnd 15.284.700 · usdtAvgVnd 25.500 (KHÔNG ĐỔI)
            investedThisMonth(2026-01) = planInvested = 15.315.300
            remainingPlannedBudget = 4.684.700
    INV     giải phóng theo bình quân KHÔNG làm đổi bình quân (§6.3) · phí USDT vào cả hai
            giá vốn (§7.2)

### SC-04 — Multiple P2P rates then ETH purchase

    INPUT   TREASURY 2026-02-03 VND_TO_USDT vndAmount 13.100.000 usdtAmount 500,000000
            TRADE    2026-02-05 BUY ETH usdtNotional 500,000000 feeUsdt 0 qty 0,20 source PLAN
    EXPECT  sau P2P:  usdtQty 1.099,4 · usdtCostVnd 28.384.700 · usdtAvgVnd ~25.818,35547
            vndRelieved = ROUND(500 × 28.384.700 / 1.099,4) = 12.909.178
            ethQty 0,95 · ethCostUsdt 2.300,6
            ethCostVnd 58.224.478 · avgCostVnd ~61.288.924,21/ETH
            usdtQty 599,4 · usdtCostVnd 15.475.522
            carryInVnd(2026-02) = 4.684.700 · plannedBudgetVnd(2026-02) = 24.684.700
            planInvested(2026-02) = 12.909.178 · remainingPlannedBudgetVnd(2026-02) = 11.775.522
    INV     hai tỷ giá khác nhau được trộn bởi WAC, KHÔNG cần ghép lô (§8.3-1)

### SC-05 — Edit past trade and recompute

    INPUT   sửa SC-03: qty 0,25 -> 0,24 (fill thật trên sàn); id và seq GIỮ NGUYÊN
    EXPECT  ethQty 0,94 · ethCostUsdt 2.300,6 (KHÔNG ĐỔI) · ethCostVnd 58.224.478 (KHÔNG ĐỔI)
            avgCostUsdt ~2.447,4468/ETH · avgCostVnd ~61.940.934,04/ETH
            pool USDT KHÔNG ĐỔI · planInvested KHÔNG ĐỔI
    INV     sửa lượng NHẬN đổi số lượng và giá bình quân, KHÔNG đổi tổng giá vốn — vì giá vốn
            do lượng USDT CHI quyết định (§7.3) · INV-1 (không có phép hoàn tác nào tồn tại)

### SC-06 — Delete/void trade and recompute

    INPUT   xoá TREASURY 2026-02-03 của SC-04 (xoá cứng, §15.3), snapshot đã ghi trước đó
    EXPECT  tại 2026-02-05 pool = 599,4 USDT / 15.284.700 VND / bình quân 25.500
            vndRelieved = ROUND(500 × 25.500) = 12.750.000
            ethCostVnd 58.065.300 · usdtQty 99,4 · usdtCostVnd 2.534.700
    INV     INV-3 (không VND nào còn sót) · xoá TƯƠNG ĐƯƠNG CHÍNH XÁC với chưa từng nhập ·
            INV-14 (snapshot trước thao tác phá huỷ)

### SC-07 — Purchase entered days late

    INPUT   ngày 2026-02-20 người dùng nhập TRADE với businessDate 2026-02-04
              usdtNotional 100,000000 · feeUsdt 0 · qty 0,04 · source PLAN
              (createdAt = 2026-02-20T…Z, seq lớn hơn mọi event hiện có)
    EXPECT  replay đặt event này TRƯỚC lệnh 2026-02-05 vì businessDate nhỏ hơn
            nó tiêu USDT ở bình quân của 2026-02-03, và lệnh 2026-02-05 thấy pool đã nhỏ hơn
            cả hai lệnh vào tháng 2026-02 · investedThisMonth(2026-02) gồm cả hai
    INV     INV-6 — createdAt KHÔNG BAO GIỜ vào phép tính · thứ tự = (businessDate, seq) (§5.4)

### SC-08 — Month boundary Asia/Ho_Chi_Minh

    INPUT   người dùng bấm lưu tại instant UTC 2026-02-28T18:30:00Z
              (= 2026-03-01 01:30 giờ Asia/Ho_Chi_Minh) với businessDate 2026-03-01
    EXPECT  asOfDate = "2026-03-01" · currentMonth = "2026-03"
            event thuộc tháng 2026-03, KHÔNG phải 2026-02
            carryOut(2026-02) được chốt vì 2026-02 nay là tháng ĐÃ ĐÓNG
    INV     INV-6 · §10.2 (một chỗ duy nhất hỏi giờ) · diệt B3 và B7

### SC-09 — Extra purchase

    INPUT   asOfDate = 2026-03-18; tháng 2026-03, plannedBudget 20.000.000 (giả định carryIn = 0)
            TRADE 2026-03-03 BUY source PLAN  -> vndRelieved 6.000.000
            TRADE 2026-03-13 BUY source PLAN  -> vndRelieved 6.000.000
            TRADE 2026-03-17 BUY source EXTRA -> vndRelieved 5.000.000
    EXPECT  plannedPerSlot = [6.666.667, 6.666.667, 6.666.666]  (tổng ĐÚNG 20.000.000, INV-13)
            investedThisMonth      = 17.000.000
            planInvested           = 12.000.000
            remainingPlannedBudget =  8.000.000   (EXTRA KHÔNG làm giảm)
            nextPlannedDate = 2026-03-23 · nextPlannedAmount = 8.000.000
            carryOut(2026-03) = 8.000.000 -> carryIn(2026-04) = min(8.000.000, 20.000.000) = 8.000.000
    INV     INV-9 · §11.5 — hai con số được phép khác nhau

### SC-10 — Manual reserve deployment

    INPUT   tiếp SC-09, asOfDate = 2026-03-21
            RESERVE 2026-03-02 CONTRIBUTE vndAmount 10.000.000
            TRADE   2026-03-20 BUY source RESERVE note "giải ngân dự phòng, giá giảm sâu"
                    -> vndRelieved 4.000.000
    EXPECT  reserveBalance = 10.000.000 − 4.000.000 = 6.000.000
            investedThisMonth      = 21.000.000
            planInvested           = 12.000.000  (KHÔNG ĐỔI)
            remainingPlannedBudget =  8.000.000  (KHÔNG ĐỔI)
            carryOut(2026-03)      =  8.000.000  (KHÔNG ĐỔI)
    INV     INV-9 · INV-10 — không score/regime nào được tạo hay định cỡ event này ·
            note BẮT BUỘC (§12.2)

### SC-11 — Future-month data

    INPUT   asOfDate = 2026-03-15
            TRADE 2026-04-03 BUY ETH usdtNotional 200,000000 qty 0,08 source PLAN
    EXPECT  investedThisMonth(2026-03) KHÔNG ĐỔI
            holdings và giá vốn CÓ tính event này
            planInvested(2026-04) = vndRelieved của nó
            carryOut(2026-03) chưa được chốt (2026-03 chưa đóng)
            flags chứa "FUTURE_DATED_EVENTS" · dòng lịch sử có badge
    INV     §10.6 — một đường tính duy nhất, cảnh báo thấy được thay cho việc chặn

### SC-12 — Migration with unknown VND cost basis → complete, flagged, not fabricated

    INPUT   legacy state có: trades[3] = { ts: "2026-01-09T…Z", usdt: 300, price: 2400,
                                           eth: 0,125, vndRate: null, vndCost: 0 }
            và KHÔNG có bản ghi p2p nào phủ được lượng USDT đó (số lượng ETH/USDT vẫn nhất quán —
            KHÔNG có pool nào âm, chỉ THIẾU nguồn gốc giá vốn VND của khoản USDT đó)
    EXPECT  migration HOÀN TẤT theo `W-1` (§17.4-B) — KHÔNG dừng, vì đây là thiếu GIÁ VỐN, không
            phải mâu thuẫn SỐ LƯỢNG:
              ethQty và usdtQty nhập đúng, không đổi
              ethCostUsdt nhập đúng (khoản USDT đã biết, không phụ thuộc VND)
              phần ethCostVnd tương ứng với 300 USDT này = UNKNOWN, lan truyền theo INV-11
              KHÔNG dùng tỷ giá hiện tại, KHÔNG dùng tỷ giá ngày giao dịch, KHÔNG dùng 0,
              KHÔNG có ô nhập tỷ giá riêng cho lệnh này (DEC-042 §4 — cấm hidden per-trade
              FX fallback; vì vậy trường vndRateOverride không tồn tại, xem §5.3)
            báo cáo migration nêu rõ: chỉ số legacy (`trades[3]`), lý do (không phủ pool P2P),
            và đường sửa DUY NHẤT: Owner sửa/bổ sung `openingPosition.usdt.costVnd` hoặc nhập
            thêm event P2P còn thiếu — qua đúng cơ chế edit đã có (§14, §15), KHÔNG qua fallback
            theo từng lệnh
            dashboard hiện cờ `UNKNOWN_VND_BASIS` thường trực (§16.4) cho tới khi Owner sửa
            dữ liệu legacy KHÔNG bị đụng · snapshot đã tồn tại (INV-14)
    INV     INV-11 (thiếu ≠ 0, không fallback ẩn) · INV-12 (nguyên tử — sổ mới được ghi TRỌN VẸN,
            không một phần) · INV-14 · §17.4-B

---

## 20. Invariants

| # | Bất biến |
|---|---|
| `INV-1` | **Chỉ dẫn xuất.** `ethQty`, `ethCost*`, `usdtQty`, `usdtCostVnd`, `reserveBalance`, `invested*`, `remaining*`, `next*`, mọi `avg*`, mọi `price`/`rate` **không bao giờ** được lưu vào durable state. Chúng được tính lại từ `(openingPosition + events)` mỗi lần render |
| `INV-2` | **Tất định.** Cùng một tập event → cùng một `DerivedState`, độc lập với thứ tự nhập, đồng hồ, và múi giờ máy |
| `INV-3` | **Bảo toàn.** `usdtCostVnd = 0` khi và chỉ khi `usdtQty = 0`. Giá vốn VND chỉ được tạo bởi `openingPosition` và P2P mua, chỉ được huỷ bởi giải phóng theo bình quân |
| `INV-4` | **Không âm.** `usdtQty ≥ 0`, mọi `assetQty ≥ 0`, `reserveBalance ≥ 0` tại **mọi tiền tố** của replay. Vi phạm → `LEDGER_INCONSISTENT` + id event đầu tiên gây ra |
| `INV-5` | **Tiền là số nguyên.** Không giá trị float nào được ghi xuống durable state |
| `INV-6` | **Ngày sạch.** Mọi phép tính tài chính chỉ đọc `businessDate`. `createdAt`/`updatedAt` không bao giờ vào phép tính tài chính |
| `INV-7` | **Ranh giới đầu kỳ.** Không event nào có `businessDate < openingPosition.asOf` |
| `INV-8` | **P2P không phải đầu tư.** Không `TREASURY` event nào đóng góp vào `investedThisMonth`, `planInvested`, `assetQty`, hay `assetCost*` |
| `INV-9` | **Cách ly dự phòng.** Không `RESERVE` event nào và không `TRADE` có `source ∈ {EXTRA, RESERVE}` nào làm đổi `planInvested`, `remainingPlannedBudget`, hay `carryOut` |
| `INV-10` | **Tín hiệu không được chạm tiền.** Không chỉ báo, score, regime, hay giá nào được tạo, sửa, hay định cỡ bất kỳ event nào. Event chỉ sinh ra từ thao tác nhập tay của người dùng |
| `INV-11` | **Không biết ≠ 0, không fallback ẩn.** Một đại lượng không biết hiển thị `—` và lan truyền thành `UNKNOWN`; không bao giờ bị thay bằng 0, tỷ giá thị trường, hay bất kỳ tỷ giá nào nhập riêng theo từng lệnh (`DEC-042` §4 — cấm hidden per-trade FX fallback) |
| `INV-12` | **Migration nguyên tử.** Migration ghi toàn bộ sổ mới hoặc không ghi gì |
| `INV-13` | **Làm tròn đối chiếu được.** Một khoản VND chia thành `n` phần luôn cộng lại **đúng bằng** khoản gốc |
| `INV-14` | **Snapshot trước khi phá huỷ.** `import`, `wipe`, `migration` mỗi cái ghi một snapshot export đầy đủ **trước** khi đụng durable state |
| `INV-15` | **Định danh ổn định.** `id` và `seq` cấp một lần, không tái sử dụng, không đánh số lại; sửa event giữ nguyên cả hai |

---

## 21. Owner-Approved Decisions (`DEC-042`)

Bốn câu, **đã QUYẾT** bằng Owner Decision `DEC-042` (2026-09-05). Giữ nguyên bảng phương án và
lập luận làm hồ sơ thể chế; mục "QUYẾT ĐỊNH" là kết quả cuối, canonical, không còn là câu hỏi mở.

### OD-L1-1 — Mô hình lịch DCA — **QUYẾT ĐỊNH: Phương án A**

| Phương án | Nội dung |
|---|---|
| **A — ĐÃ CHỌN** | Số tiền cố định hằng tháng + `scheduleDays` (mặc định `[3, 13, 23]`); mỗi mốc = `monthlyBudget / số mốc` |
| B | Số tiền cố định hằng tháng, **một** mốc duy nhất |
| C | Lịch hằng tuần (thứ trong tuần) |

Lý do (giữ làm hồ sơ): A phủ được B (`scheduleDays = [3]`) và gần đúng C (`[1, 8, 15, 22]`) bằng
**một** cơ chế, nên spec không phải mang hai bộ lịch. C thật sự (thứ trong tuần) làm số mốc thay
đổi giữa các tháng (4 hoặc 5), khiến `plannedPerSlot` không ổn định.

**Ý nghĩa quyết định:** ngân sách tháng là ràng buộc tài chính; `scheduleDays` định ngày thực thi
đã lên kế hoạch; lịch **tất định**; Buy Score/regime/tín hiệu thị trường **không** đổi lịch;
Owner đổi `scheduleDays` được, **chỉ về sau** (§11.1). `plannedAmount` dẫn xuất từ `plan`, không
ghép với pool Base/Smart/Opportunity cũ (§11.1, §17.2).

### OD-L1-2 — Ngân sách tháng chưa dùng hết — **QUYẾT ĐỊNH: `CAPPED_CARRY`**

| Phương án | Nội dung |
|---|---|
| `FORFEIT` | Phần chưa dùng **mất**; mỗi tháng bắt đầu lại từ `monthlyBudget` |
| `CARRY` | Phần chưa dùng chuyển sang tháng sau **không giới hạn** |
| **`CAPPED_CARRY` — ĐÃ CHỌN** | Chuyển sang tháng sau nhưng `carryIn ≤ 1 × monthlyBudget` (`carryCapMonths = 1`) |

Lý do (giữ làm hồ sơ): `FORFEIT` phạt oan chính hành vi mà L-1 sinh ra để hỗ trợ — nhập giao dịch
muộn. `CARRY` không giới hạn để tồn đọng lớn dần rồi biến thành một cú xuống tiền dựa trên thời
điểm — đúng thứ L-1 từ chối trở thành (`N-3`). `CAPPED_CARRY` cứu được một tháng lỡ mà không biến
kế hoạch thành công cụ timing.

**Ý nghĩa quyết định:** phần ngân sách chưa dùng có thể carry-forward, nhưng carry tích luỹ
**không bao giờ** vượt một tháng ngân sách bình thường; phần vượt cap hết hiệu lực khỏi kế hoạch.
Đây là **luật kỷ luật**, không phải cơ chế timing thị trường. Cài đặt phải giữ tách biệt: ngân
sách tháng hiện hành · carry-forward · số tiền đã đầu tư thật (§11.4) — không gộp thành một số dư
mờ.

### OD-L1-3 — Cách đối xử với quỹ dự phòng — **QUYẾT ĐỊNH: Phương án A**

| Phương án | Nội dung |
|---|---|
| **A — ĐÃ CHỌN** | Quỹ **tách hẳn** khỏi ngân sách DCA; nạp thủ công; giải ngân **không** tính vào tuân thủ kế hoạch |
| B | Quỹ được cấp vốn bằng ngân sách tháng chưa dùng (điểm đến của carry) |
| C | Giải ngân quỹ **tính** vào tuân thủ kế hoạch (coi như bù tháng hụt) |

Lý do (giữ làm hồ sơ): A giữ **một** thước đo kỷ luật duy nhất (`planInvested`). B trộn hai câu
hỏi vào nhau và ràng buộc chéo với `OD-L1-2`. C khiến một lần giải ngân dự phòng làm một tháng lỡ
**trông như** đạt kế hoạch — thước đo kỷ luật tự nói dối.

**Ý nghĩa quyết định:** quỹ dự phòng do người dùng điều khiển hoàn toàn; có số dư tường minh; có
thể nhận đóng góp thủ công; chỉ được giải ngân bằng hành động tường minh của Owner, **bắt buộc**
kèm lý do/ghi chú (`source = RESERVE`, §12.2); **không bao giờ** được Buy Score, regime,
Opportunity Score, Crash logic, hay bất kỳ tín hiệu V2.1.5 nào tự động kích hoạt (`INV-10`,
§12.3). Giải ngân dự phòng **không** âm thầm làm giảm mức tuân thủ DCA thông thường — `investedThisMonth`
và `planInvested` được phép khác nhau và dashboard hiện phần tách khi chúng khác (§16.1 ô 2).

### OD-L1-4 — Giá vốn VND khi nguồn gốc P2P không đầy đủ — **QUYẾT ĐỊNH: STRICT / FAIL-VISIBLE**

**Mô hình canonical (đã quyết, không còn là phương án cạnh tranh):** USDT là một tài sản có giá
vốn VND riêng. Các khoản mua USDT đã biết đi vào **một** pool WAC (§8.2). Khi USDT được chi để
mua crypto: lượng USDT rời pool; giá vốn VND tương ứng được giải phóng theo bình quân của pool;
giá vốn đó trở thành một phần giá vốn VND của crypto. **Không cần** ghép chính xác lô P2P với
lệnh mua.

**Khi giá vốn VND của USDT thật sự không biết** (ví dụ số dư USDT đầu kỳ không rõ giá vốn lịch
sử) — spec **CẤM** dùng tỷ giá thị trường hiện tại, tỷ giá ngày giao dịch crypto, số 0, hoặc bịa
một tỷ giá lịch sử ngụ ý. **CẤM** tạo bất kỳ ô nhập tỷ giá riêng theo từng lệnh để vá trường hợp
này (không có `vndRateOverride` trong schema, §5.3).

**Thay vào đó:** giữ nguyên số lượng USDT/crypto; giữ nguyên phần giá vốn USDT đã biết; lan
truyền phần giá vốn VND bị ảnh hưởng thành `UNKNOWN` (`INV-11`); hiển thị điều kiện này **thấy
được** trên dashboard (§16.4, cờ `UNKNOWN_VND_BASIS`). Owner sửa sau bằng cách cập nhật
`openingPosition` một cách tường minh (§8.5, §14, §15) — không phải qua một fallback ẩn theo
từng giao dịch.

Lý do (giữ làm hồ sơ so với hai phương án bị loại): `MANUAL_RATE` bắt gõ một con số ở **mọi**
lệnh kể cả khi sổ đã biết câu trả lời, và một lần gõ sai thì im lặng vào thẳng giá vốn.
`MARKET_RATE` đưa một phụ thuộc dữ liệu ngoài vào giá vốn — một con số lịch sử bất biến bỗng phụ
thuộc nguồn giá, đúng loại trôi âm thầm của `B10`. Cả hai vi phạm tinh thần `INV-10`.

---

## 22. L-1 MVP Acceptance Slice

Lát cắt (giữ nguyên `DEC-041` C, `CAPABILITY_REGISTRY.md` §1.A):

    Ngân sách tháng do người dùng đặt
      -> lịch mua đã lên kế hoạch
        -> người dùng ghi một giao dịch thật (có NGÀY do người dùng nhập)
          -> sổ cái + giá vốn tính lại từ (số dư đầu kỳ + toàn bộ trades)
            -> 4 con số dashboard (ngân sách · đã đầu tư · còn lại · ngày mua kế tiếp)
              -> lưu bền qua reload/restart

Điều kiện chấp nhận L-1 MVP:

| # | Điều kiện |
|---|---|
| `A-1` | `SC-01` … `SC-12` **PASS** trên dữ liệu tổng hợp |
| `A-2` | `INV-1` … `INV-15` được kiểm bằng test, không phải bằng lời |
| `A-3` | Lát cắt trên chạy end-to-end trên dữ liệu tổng hợp |
| `A-4` | Migration từ state legacy hoặc thành công có đối chiếu (§17.3), hoặc thất bại thấy được (§17.4) |
| `A-5` | Fixture `OWNER_LOCAL_ACCEPTANCE` (§22.1) chạy được trên máy Owner và khớp oracle của Owner |
| `A-6` | `R-1` … `R-5` (§18) thoả **trước khi** ghi tiền thật |

### 22.1 `OWNER_LOCAL_ACCEPTANCE` — giao diện fixture

Repo chứa **schema và một ví dụ tổng hợp**. File dữ liệu thật của Owner **không bao giờ** vào
repo (`DEC-041` C).

    đường dẫn dự kiến:  private/owner_local_acceptance.json      (phải nằm trong .gitignore)

```
{
  "asOfDate": "YYYY-MM-DD",
  "plan": { ... },                  // §5.1
  "openingPosition": { ... },       // §5.2
  "events": [ ... ],                // §5.3
  "expected": {
    "ethQty": integer,
    "avgCostUsdt": integer,
    "avgCostVnd": integer | "UNKNOWN",
    "investedThisMonthVnd": integer,
    "planInvestedVnd": integer,
    "remainingPlannedBudgetVnd": integer,
    "reserveBalanceVnd": integer,
    "nextPlannedDate": "YYYY-MM-DD",
    "nextPlannedAmountVnd": integer
  },
  "tolerance": { "vnd": 0, "usdt": 0, "qty": 0 }
}
```

Bộ chạy so `derive(...)` với `expected` và in bảng lệch. Owner cần cung cấp tối thiểu **một** con
số oracle (giá vốn trung bình kỳ vọng) — đó chính là `MISSING_DATA` mà
`CAPABILITY_REGISTRY.md` §1.A đang chờ. Việc chạy diễn ra **cục bộ**; chỉ kết quả `PASS`/`FAIL`
mới được ghi vào repo, không kèm số liệu.

---

## 23. Explicitly Deferred

| # | Hạng mục | Phân loại | Ghi chú |
|---|---|---|---|
| `D-1` | Buy Score, OSCORE, regime, crash ladder, unlock, spacing, recommendation V2.1.5 | **`NOT_IN_L1_MVP`** | `DEC-041` B; `INV-10` |
| `D-2` | Tab Research hiển thị Buy Score hồi cứu | `RESEARCH_ONLY`, hoãn | Nếu bật: chỉ `DESCRIPTIVE`, và `H-43` + `B10` trở thành điều kiện tiên quyết |
| `D-3` | Thi hành `H-42` (Firebase riêng, Google Sign-in, backup) | hoãn | §18 ghi ràng buộc; cài đặt ở §24 bước C |
| `D-4` | Nhiều tài sản ngoài ETH | hoãn | Schema đã đa tài sản; UI L-1 MVP chỉ một |
| `D-5` | Tax lot (FIFO/LIFO/specific-ID), báo cáo lãi lỗ đã thực hiện | hoãn | §8.2 — WAC là đủ cho L-1 |
| `D-6` | Nhắc lịch / thông báo (di sản `T-08`/`T-10`) | hoãn | `DEC-041` F/G: phải do spec L-1 chi phối, **không** kế thừa bề mặt quyết định `T-08` cũ |
| `D-7` | Lấy giá tự động, nguồn dữ liệu thị trường | hoãn | `PRICE` là event nhập tay ở L-1 MVP |
| `D-8` | Tombstone / audit trail đầy đủ cho xoá | hoãn | §15.3 — snapshot + export là đủ hiện nay |
| `D-9` | Đối chiếu lịch sử DESCRIPTIVE (giá mua TB thực tế vs DCA thuần) | hoãn | Được phép theo `DEC-041` B, nhưng ngoài MVP |
| `D-10` | Đồng bộ nhiều thiết bị, chế độ offline nâng cao | hoãn | Sau `R-3` |

---

## 24. Proposed Implementation Sequence

**KHÔNG task ID nào được tạo trong tài liệu này** (`DEC-041` J, `AGENTS.md` §3 — *"A finding is
not a task"*). Bốn câu Owner Decision ở §21 đã được trả lời (`DEC-042`); đây vẫn chỉ là **thứ tự
đề xuất** — việc mở task ID cho bước A thuộc một phiên riêng, không phải hệ quả tự động của
`DEC-042`.

| Bước | Nội dung | Vì sao đứng ở đây |
|---|---|---|
| **A** | Ledger / Data Model v2 (§5) + `derive()` (§9) + migration (§17) + test kế toán (`SC-01`…`SC-12`, `INV-1`…`INV-15`) | Sự thật tài chính phải đúng **trước** khi có gì hiển thị nó. Không có bước A thì mọi bước sau xây trên số sai |
| **B** | Dashboard (§16) + UX nhập/sửa/xoá + lịch sử (§15) | Biến sổ đúng thành công cụ dùng được hằng ngày |
| **C** | Firebase isolation + auth bền + backup/snapshot (§18, `R-1`…`R-5`) | Chặn cứng trước khi ghi tiền thật; **không** chặn A/B trên dữ liệu tổng hợp |
| **D** | Chấp nhận dùng thật: `OWNER_LOCAL_ACCEPTANCE` (§22.1) trên máy Owner | Chỉ có nghĩa sau A + B + C |

Ghi chú định tuyến (không phải quyết định): bước A và mọi phần của B/C chạm lớp tính tiền mang
category `accounting_financial` → hard floor `Tier ≥ C`, `Effort ≥ high`
(`PROJECT_PROFILE.md` § Hệ quả bắt buộc 2; `DEC-041` J). Việc UI thuần không chạm lớp tính tiền
**không** tự động mang category đó. `E2` bắt buộc cho: tính đúng tài chính, bất biến sổ cái,
migration, persistence (`DEC-041` J).

Tính năng nghiên cứu / lịch / lịch sử mở rộng vẫn **tuỳ chọn** trừ khi một phiên sau chứng minh
được chúng thuộc MVP — spec này **không** chứng minh điều đó.

---

## Phụ lục A — Truy vết `H-41` (`B1`–`B10`)

Mỗi hạng mục phải được spec **trả lời hoặc bác bỏ tường minh** (`H-41` `RE_TRIGGER_CONDITION`).

| # | Hiện tượng | Được giải quyết ở |
|---|---|---|
| `B1` | Fill zone không tỷ giá → `amount = remaining`, zone `EXECUTED` sai | §17.2 — ladder/zone `DROP_LEGACY_ONLY`; khái niệm không tồn tại dưới L-1. `M-4` chặn migration khi zone đã phát tác |
| `B2` | Mua không tỷ giá → `deducted = 0`, "available" ảo | §9 (không cộng dồn) + §11.2 (`planInvested` là dẫn xuất từ `vndRelieved`, không từ pool) |
| `B3` | `currentMonth()` = khoá tháng lớn nhất | §10.3 — tháng lịch từ `asOfDate`. `SC-08` |
| `B4` | Ngày giao dịch = lúc bấm nút | §10.1 — `businessDate` người dùng nhập, bắt buộc. `SC-07` |
| `B5` | Không sửa/xoá được giao dịch | §15 — mọi event sửa và xoá được. `SC-05`, `SC-06` |
| `B6` | Không nhập được số dư đầu kỳ | §14 — `openingPosition`. `SC-01` |
| `B7` | `monthKey` giờ local trộn với `today` UTC | §10.2 — một chỗ duy nhất hỏi giờ, `Asia/Ho_Chi_Minh`. `SC-08` |
| `B8` | Wipe không snapshot | §15.3 + `INV-14` |
| `B9` | VND lưu float | §10.4 + `INV-5` |
| `B10` | Rolling window đếm số dòng, không theo lịch | `D-1`/`D-2` — chỉ báo **ngoài** đường quyết định của L-1 MVP; nếu bật tab Research thì `B10` là điều kiện tiên quyết (`H-43`) |

## Phụ lục B — Truy vết `H-42` (`FB-1`–`FB-4`)

| # | Ràng buộc | Được ghi ở |
|---|---|---|
| `FB-1` | Anonymous Auth mở cửa ghi cho khách vô danh vào dữ liệu của app Content | §18 `R-2` |
| `FB-2` | `firebase.json` thiếu khoá `site` → deploy đè Hosting của Content | §18 `R-2` |
| `FB-3` | `firestore.rules:101` còn placeholder `OWNER_UID_REQUIRED` | §18 `R-5` |
| `FB-4` | Anonymous UID trong IndexedDB → mất quyền truy cập dữ liệu của chính mình | §18 `R-3` |

**KHÔNG hạng mục nào được thi hành trong phiên soạn spec này.**
