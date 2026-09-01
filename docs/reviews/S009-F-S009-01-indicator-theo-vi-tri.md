# `F-S009-01` — Indicator daily được tính theo VỊ TRÍ, không theo LỊCH

Ngày:
2026-09-01 (phiên S009 / WP-A4)

Phân loại:
**CONFIRMED BLOCKING** — theo `governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing

Trạng thái ownership:
`OWNER_ASSIGNMENT_REQUIRED`

Task ID được tạo:
**0** — finding ≠ task.

---

## 1. Vì sao ghi ở đây, không sửa ở đây

Phát hiện trong lúc thực hiện WP-A4, nhưng **nằm ngoài** Expected Touch Area của WP-A4:
`src/eth_dca_os/indicators.py` không có trong danh sách Allowed, và chỉ thị mở gói ghi rõ
"Discovery có thể rộng. Repair phải hẹp." Sửa ở đây là `SCOPE EXPANSION` không được phép.

Nó cũng **không làm FAIL** check nào của WP-A4: chín check FROZEN cộng `CHECK-A4-10` đều
không phủ ngữ nghĩa cửa sổ indicator. Đây đúng tiền lệ mà `F-E2A1R3-05` đã tạo với WP-A1
("contract đã FROZEN không có case này, nên nó KHÔNG làm FAIL check nào").

## 2. Vấn đề

`compute_daily_indicators` tính mọi cửa sổ theo **vị trí hàng**, không theo **ngày lịch**:

```python
df["return7"]  = close / np.roll(close, 7) - 1          # 7 HÀNG, không phải 7 NGÀY
df["high365"]  = s_close.rolling(365, min_periods=365).max()
df["ma200"]    = s_close.rolling(200, min_periods=200).mean()
df["adr30"]    = daily_ret.abs().rolling(30, min_periods=30).mean()
df["ethbtc_return30"] = ethbtc / np.roll(ethbtc, 30) - 1
```

Nếu series daily thiếu MỘT ngày, mọi cửa sổ trượt qua chỗ đó bao phủ nhiều hơn một ngày
lịch so với tên gọi của nó — và kết quả **không NaN**, **không DEGRADED**, **không INVALID**.
Hệ thống không mô tả sai *thiếu bao nhiêu* (WP-A4 vừa sửa đúng chỗ đó), mà mô tả sai *nó
vừa tính cái gì*.

## 3. Bằng chứng — đường sản xuất bình thường, KHÔNG sửa tay artifact

`fetch_all` (stub HTTP dựng trên mã production thật, nguồn canonical 1 + 2 của
`PROJECT/PRODUCTION_PATHS.md` §3) → `official_eligibility` → `Prepared` →
`compute_daily_indicators`. Yêu cầu `--start 2019-01-01 --end 2020-01-01`; archive thiếu
đúng một ngày (2019-07-15) bên trong một tháng.

```
--- đầy đủ ---
  ETHUSDT_1d rows=365/365 missing=0 ratio=0.0000%
  official_eligibility -> (True, 'verified')
  return7 tại 2019-07-20  engine = 6.98993449430585e-05
  return7 đúng theo lịch      = 6.98993449430585e-05

--- thiếu 1 ngày 1D ---
  ETHUSDT_1d rows=364/365 missing=1 ratio=0.2740%
  official_eligibility -> (True, 'verified')
  return7 tại 2019-07-20  engine = 7.988576335815623e-05
  return7 đúng theo lịch      = 6.98993449430585e-05
  NaN? False   lệch tương đối = 14.29%
```

Không sửa tay `lineage.json`. Không mock eligibility/loader/indicator. Không input thù địch.
Dataset đi qua cổng official với `(True, 'verified')` và mang một indicator sai 14,29%.

## 4. Ba tiêu chí BLOCKING — đều thoả

**Production path.** `src/eth_dca_os/indicators.py` nằm trong `src/eth_dca_os/**`
(`PRODUCTION_PATHS.md` §1) và được chạy ở MỌI lần chạy, qua `Prepared.indicators`.

**Hệ quả nghiệp vụ V1 (`DEC-011`).**
- **A — CORRECT DECISION.** `return7` đi vào sub-factor S7 (0,3 × 30 điểm của
  MARKET_STRESS) và vào `RegimeTracker` với ngưỡng CRASH `r7 <= -0.15` và STRESSED
  `r7 <= -0.10`. Sai 14% quanh ngưỡng là đủ để lật regime, mà regime quyết định cooldown
  override và chính sách hành động.
- **D — REAL MARKET DATA.** Defect chỉ biểu hiện trên dữ liệu THẬT có gap — đúng điều kiện
  của T-06, và đúng tiền đề mà task file WP-A4 nêu ngay dòng đầu ("Dữ liệu Binance thật
  **có gap**").
- **F — OFFICIAL RESULT VALIDITY.** Con số official sẽ sai một cách **âm thầm**: không cờ,
  không tag, không NaN.

**Bằng chứng tái lập được.** §3 — chạy được lại bằng một lệnh, tất định.

Đối chiếu với lý do khiến H-05/H-06/H-13 bị hạ xuống HARDENING: những mục đó thiếu **đường
sinh** — counterexample chỉ dựng được bằng sửa tay artifact. Mục này CÓ đường sinh: một lần
`ethdca fetch` bình thường trên archive thiếu một ngày. Đó là khác biệt quyết định.

## 5. Tương tác với `CHECK-A4-10` vừa đóng — phải nói thẳng

`CHECK-A4-10` đặt ngưỡng `MAX_MISSING_RATIO = 0.01`. Với khoảng một năm, ngưỡng đó cho phép
tới ~3,6 ngày thiếu mà dataset **vẫn** đủ tư cách official. Mỗi ngày thiếu đó làm sai lệch
mọi cửa sổ indicator trượt qua nó.

Nói cách khác: WP-A4 đóng được lỗ hổng "thiếu NHIỀU mà không ai biết", nhưng lỗ hổng "thiếu
ÍT và tính sai âm thầm" thì không — và nó nằm ở module khác. Ngưỡng KHÔNG thể hạ về 0 để
vá điều này: dữ liệu Binance thật có gap bảo trì, ngưỡng 0 sẽ từ chối mọi dataset thật.
Đây là lý do finding phải được đóng ở đúng chỗ của nó, không phải bằng cách siết ngưỡng.

## 6. Định tuyến

`REVIEW_PROTOCOL.md`: "BLOCKING inside the current capability -> identify repair ownership
and remaining capability budget, then stop. Opening the repair cycle is not automatic."

Không capability nào hiện sở hữu ngữ nghĩa cửa sổ indicator:

| Ứng viên | Lập luận | Kết luận |
|---|---|---|
| `CAP-DATA` (WP-A4) | Cùng HÌNH DẠNG lỗi với `F-E2A1R3-05` (hệ thống mô tả sai điều nó vừa làm khi dữ liệu thiếu). Nhưng `indicators.py` không nằm trong Expected Touch Area, và Completion Gate của WP-A4 vừa được chủ dự án bổ sung ĐÚNG MỘT check với chỉ thị "Không mở rộng Completion Gate thêm". | Không tự nhận |
| `CAP-ORDER` (WP-A6) | WP-A6 sở hữu "thứ tự 18 bước", tức cách các bước tính nối vào nhau — không phải ngữ nghĩa cửa sổ của một indicator. | Không khớp chủ đề |
| `CAP-PIPELINE` (WP-A2) | DONE tại S006; đấu nối hạng mục vào pipeline, không sở hữu công thức. | Không khớp |
| `CAP-SPEC` (WP-D2) | Spec V2.1.5 KHÔNG nói rõ cửa sổ là theo hàng hay theo lịch. Nếu chủ dự án coi đây là khiếm khuyết đặc tả thì WP-D2 là nơi đúng. | Có thể |

    OWNER_ASSIGNMENT_REQUIRED

    Chủ dự án cần chọn capability owner. Hai nhánh hợp lý:
    (a) CAP-DATA — cùng chủ đề "ngữ nghĩa dữ liệu thiếu", kèm một COMPLETION GATE CHANGE
        PROPOSAL mới cho WP-A4 và mở rộng Expected Touch Area sang `indicators.py`;
    (b) CAP-SPEC (WP-D2) — nếu coi đây là điểm để ngỏ của V2.1.5 phải chốt trước.

    KHÔNG đặt task ID mới trong cả hai nhánh.

Budget: `CAP-DATA` hiện repair cycles = 0 (`REVIEW_BUDGET_LEDGER.md` §2.1), nên nhánh (a)
khả thi về budget. `CAP-PROV` REMAINING = 0 nên WP-A1 **không** phải nơi đóng.

## 7. Hệ quả với trạng thái hiện tại

- **KHÔNG** làm FAIL check nào của WP-A4; WP-A4 vẫn đạt 9/9 REQUIRED.
- **KHÔNG** làm đổi trạng thái WP-A1.
- **CÓ** là blocker phải đóng **trước T-06**: một official run trên dữ liệu thật có gap sẽ
  mang indicator sai mà không có dấu hiệu nào.
- GATE-A theo định nghĩa hiện tại (`WP-A1…WP-A7` đều DONE) không tự động bị chặn bởi mục
  này, vì nó chưa có owner nằm trong bảy gói đó. Đó chính là lý do cần một quyết định
  ownership, chứ không phải một suy luận im lặng.

## 8. Gợi ý hướng sửa (KHÔNG thực hiện ở phiên này)

Hai hướng, để chủ dự án có thứ so sánh chứ không phải bắt đầu từ trắng:

1. **Reindex theo lịch trước khi tính.** `compute_daily_indicators` reindex `eth`/`btc` về
   một `date_range` liên tục rồi tính; ngày thiếu thành NaN thật, và luật INVALID/DEGRADED
   của WP-A4 xử lý phần còn lại đúng ngữ nghĩa §3. Ưu: dùng lại cơ chế vừa dựng. Nhược:
   đổi hành vi trên mọi dataset có gap, phải định lượng lại như CHECK-A4-07.
2. **Cửa sổ theo offset thời gian** (`rolling("365D")` thay vì `rolling(365)`). Ưu: đúng
   nghĩa lịch mà không sinh NaN. Nhược: đổi `min_periods` semantics, cần rà lại từng
   indicator; và `np.roll` phải thay bằng tra cứu theo nhãn ngày.

Cả hai đều chạm lớp tính toán vật chất (`AGENT_CAPABILITY_MATRIX.md`: hard floor Tier C /
Effort `high`), nên không phải MICRO task.
