# `F-S009-01` — Indicator daily được tính theo VỊ TRÍ, không theo LỊCH

Ngày:
2026-09-01 (phiên S009 / WP-A4)

Phân loại:
**CONFIRMED BLOCKING** — theo `governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing

Trạng thái ownership:
`OWNER_ASSIGNMENT_REQUIRED` — **ĐÃ ĐÓNG 2026-09-01.** Chủ dự án phê chuẩn capability owner =
`CAP-DATA` (`DEC-015`). Còn lại `OWNER_DECISION_REQUIRED` cho phương tiện thi hành — xem
PHẦN II bên dưới. Câu chữ gốc của PHẦN I giữ nguyên để đọc được lịch sử.

Spec verdict:
`IMPLEMENTATION_DEFECT` — PHẦN II §II.4.

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

---

# PHẦN II — OWNER DISPOSITION (2026-09-01, phiên Integration Recheck)

Phiên này là **governance / owner disposition**: không sửa production code, không sửa test
code, không mở WP, không mở repair cycle, không tạo task ID, không merge.

    HEAD phiên       = 07bb241 (fast-forward từ 6c11a7e để khớp Expected HEAD)
    Branch           = claude/wp-a1-provenance-v67k9h
    branch authority = PASS (production diff = EMPTY, worktree CLEAN)
    Môi trường bằng chứng = Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5
                            — TRÙNG KHỚP `pyproject.lock` từng dòng

## II.1 Quyết định của chủ dự án

    F-S009-01  ->  capability owner = CAP-DATA
    F-S009-01  =   CONFIRMED BLOCKING V1

Căn cứ `DEC-011`: đường sản xuất bình thường (yêu cầu dữ liệu daily → dataset thiếu một ngày
lịch → indicator tính theo vị trí hàng → `return7` / rolling sai → không NaN, không DEGRADED,
không INVALID → dataset vẫn official → Buy Score sai) tác động trực tiếp tới **A — CORRECT
DECISION**, **D — REAL MARKET DATA**, **F — OFFICIAL RESULT VALIDITY**.

Đây KHÔNG phải hostile tampering, KHÔNG phải theoretical hardening, KHÔNG phải security
issue. Ràng buộc đối xứng của `DEC-011` ("không được hạ một finding chỉ vì dự án cá nhân")
được tôn trọng theo chiều ngược lại: finding này giữ nguyên mức BLOCKING.

Quyết định này KHÔNG tạo task ID nào. Finding ≠ task.

## II.2 Bằng chứng độc lập tại phiên này (E1)

Chạy lại trên **chính hàm production** `compute_daily_indicators`, không mock, không sửa
artifact, không sửa một dòng nào trong repo. Chuỗi giá là tổng hợp — khiếm khuyết nằm ở
**ngữ nghĩa chỉ mục**, độc lập với giá trị dữ liệu, nên chuỗi tổng hợp đủ để chứng minh cơ
chế; nó KHÔNG thay thế chuỗi bằng chứng đi qua `fetch_all` → `official_eligibility` →
`Prepared` mà §3 đã ghi, mà xác nhận độc lập cơ chế đó và **mở rộng phạm vi hệ quả**.

Chuỗi 2019-01-01…2019-12-31, thiếu đúng một ngày lịch 2019-07-15. Đọc tại 2019-07-20:

    return7  chuỗi ĐẦY ĐỦ (engine)     =  0.018720755462305005
    return7  chuỗi CÓ GAP (engine)     = -0.03652009951964508
    return7  ĐÚNG THEO LỊCH            =  0.018720755462305005
    NaN?                               = False
    lệch tương đối                     = 295.08%   -> ĐỔI DẤU

Cơ chế, đo trực tiếp: tại 2019-07-20, phần tử `i-7` của chuỗi CÓ GAP là **2019-07-12**,
trong khi lịch đòi **2019-07-13**. `np.roll(close, 7)` lấy HÀNG thứ `i-7`, không lấy NGÀY
`D-7`.

Hệ quả rộng hơn §2 đã ghi — cùng một ngày thiếu làm sai **bốn** indicator, không một cái nào
NaN:

| Indicator | chuỗi đầy đủ | chuỗi có gap | khác | NaN |
|---|---|---|---|---|
| `return7` | 0.01872075546 | −0.03652009952 | CÓ | False |
| `ethbtc_return30` | −0.01394136598 | 0.004750689935 | CÓ | False |
| `adr30` | 0.01821423268 | 0.01680697842 | CÓ | False |
| `rsi14` | 50.44115061 | 49.84127477 | CÓ | False |

`return7` và `adr30` nằm trong `REQUIRED_DAILY_INDICATORS` của `score.py`.

## II.3 Vì sao cơ chế DEGRADED/INVALID vừa dựng ở WP-A4 KHÔNG bắt được

`src/eth_dca_os/score.py::invalid_mask` chỉ đặt INVALID khi giá trị **không hữu hạn**
(`~np.isfinite`), cộng ca `close <= 0`. Cửa sổ theo vị trí luôn sinh ra một số **hữu hạn
nhưng sai**, nên `invalid_mask` = False và ngày đó được xếp GOOD/DEGRADED chứ không INVALID.

Đây chính là điểm nối làm hỏng một điều khoản spec, xem II.4.

## II.4 SPEC VERDICT — `IMPLEMENTATION_DEFECT`

Đọc canonical spec V2.1.5 (KHÔNG sửa spec):

**Bằng chứng quyết định — BT §18 bị vô hiệu hoá.**
Backtest §18 quy định: *"Indicator daily bắt buộc thiếu: giữ score hợp lệ trước đó tối đa
24h, sau đó đóng băng mọi Smart/Opportunity unlock mới và đánh dấu DEGRADED hoặc INVALID
theo Strategy §3."* Strategy §3 định nghĩa INVALID là *"Giá/lịch sử ETH **hoặc indicator
bắt buộc** không hợp lệ."* Khi ngày `D-7` vắng mặt, `return7` tại `D` **không thể** tính hợp
lệ. Spec yêu cầu kết cục DEGRADED/INVALID. Implementation thay vào đó thay thầm lặng close
của một ngày khác và trả về một số hữu hạn — nên nhánh spec bắt buộc KHÔNG BAO GIỜ chạy.
Spec ở đây rõ ràng về **kết cục bắt buộc**; implementation làm sai kết cục đó.

**Spec dùng đơn vị NGÀY cho indicator daily, và biết cách nói "số nến" khi muốn.**

| Điều khoản | Nguyên văn | Đơn vị |
|---|---|---|
| ST §1.1 | "High365 = giá đóng cửa ngày cao nhất trong **365 ngày gần nhất**" | ngày lịch |
| ST §1.1 | "Percentile365 … **trong 365 ngày**" | ngày lịch |
| ST §1.3 | `R30 = ETHBTC_today / ETHBTC_**30d_ago** - 1` | ngày lịch, tường minh |
| ST §17.1/§17.3 | `Return**7D**`, `Return**24H**` | ngày / giờ |
| BT §2 | warm-up "**365 ngày hợp lệ**" | ngày lịch |
| ST §17.2 | "Return24H … tính trên **96 nến 15m liền trước**" | **số nến**, tường minh |

Dòng cuối là đối chứng quyết định: khi spec muốn nói "đếm theo số nến" thì nó nói thẳng
"96 nến". Với chỉ báo daily nó nói "365 ngày gần nhất" và "30d_ago". Hai cách diễn đạt cùng
tồn tại trong một tài liệu, nên đây không phải chỗ để ngỏ — đây là lựa chọn đã ghi.

    VERDICT = IMPLEMENTATION_DEFECT

**Phần dư SPEC_AMBIGUITY, phải nói rõ để không bị nuốt:** spec cho `ma200`, `adr30`
(`AVG(abs(daily_return), 30)`), `rsi14` (Wilder trên daily close), `VR = AVG(volume,7)/
AVG(volume,90)` và `ETHBTC_Percentile180` chỉ nêu một CON SỐ mà không nêu ĐƠN VỊ. Với riêng
nhóm này, spec thực sự không xác định hàng-hay-ngày. Phần dư đó thuộc chủ đề `CAP-SPEC`
(`WP-D2`).

Phần dư này **KHÔNG** đổi owner của phần BLOCKING: `return7` / `Return7D`, `high365`,
`percentile365`, `ethbtc_return30` — đúng những indicator mà spec đã phát biểu theo ngày
lịch — là đường đi tới A/D/F của `DEC-011`. Evidence không ủng hộ việc chuyển toàn bộ
finding sang `CAP-SPEC`, nên KHÔNG chuyển.

## II.5 Absorption test — năm câu hỏi `CAPABILITY_MODEL.md`

**1. Có cần cho Vertical Acceptance Slice hiện tại không?** CÓ. Lát cắt kết thúc ở VERDICT
qua `T-06`, chạy trên dữ liệu Binance THẬT vốn có gap bảo trì. Đây đúng loại lỗi mà
`DELIVERY_LOOP.md` §II.9 xếp là metric quan trọng nhất — `SILENT_ERROR_RATE`: kết quả sai mà
không bị phát hiện.

**2. Có nằm trong capability đã tồn tại không?** CÓ — `CAP-DATA`. Ranh giới đã chốt sẵn ở
`CAPABILITY_REGISTRY.md` §3: *"Ngữ nghĩa DEGRADED / INVALID, nhãn gap trên bản ghi"* thuộc
`CAP-DATA`. II.3 chứng minh finding này chính là chỗ ngữ nghĩa DEGRADED/INVALID không kích
hoạt được. Quyết định của chủ dự án khớp với ranh giới đã có; KHÔNG phải mở ranh giới mới.

**3. Owner gần nhất?** `WP-A4` — lineage root và là **thành viên duy nhất** của `CAP-DATA`.

**4. Hấp thụ vào `WP-A4` có vượt Absorption Limit không?** Đo từng ngưỡng:

| Ngưỡng | Đo | Kết luận |
|---|---|---|
| **A** — Effective Risk tăng ≥1 | Hiện `MAX(Local Risk 3, Blast Radius 2) = 3`. Blast Radius của F-S009-01 theo `RISK_MODEL.md` = HIGH ("a wrong aggregation feeding an important decision"); Golden Reduction KHÔNG áp dụng được (chưa có Golden — `H-10`). Vậy B: 2 → 3, Effective Risk = `MAX(3,3)` = **3, KHÔNG đổi**. | **KHÔNG chạm** ở B=3. **CHẠM** nếu chủ dự án chấm B=4. Con số đó là routing input của chủ dự án — phiên này KHÔNG tự chọn |
| **B** — >3 mục hấp thụ vào baseline đã duyệt | đã hấp thụ `F-E2A1R3-05` (1) + mục này = **2** | KHÔNG chạm |
| **C** — REQUIRED check tăng >50% | 9 → 10 = **+11,1%** | KHÔNG chạm |
| **D** — việc ngoài vertical slice bị kéo lên đường găng | `indicators.py` **nằm trên** vertical slice | KHÔNG chạm |

    ABSORPTION_LIMIT_REACHED = KHÔNG

**5. Chỉ khi 1–4 không cho authority mới trình chủ dự án.** Câu 4 KHÔNG chặn, nhưng authority
vẫn thiếu — vì một lý do KHÁC, không phải Absorption Limit:

## II.6 CAP-DATA còn authority không? — trả lời tách hai tầng

**Tầng capability: CÒN.** `CAPABILITY_MODEL.md` định nghĩa capability là *"a lineage root, a
budget, and a set of tasks that have implemented it over time"* — một capability sống lâu hơn
từng task thành viên. `WP-A4` DONE không xoá `CAP-DATA`.

**Tầng task/thi hành: KHÔNG, nếu không có một hành vi của chủ dự án.** `CAPABILITY_MODEL.md`
§II.7 cho phép hấp thụ tự động vào task đã có baseline được duyệt/đóng băng — `WP-A4` có.
Nhưng chín bước bắt buộc của quy trình hấp thụ đòi *ghi scope hấp thụ vào Task Spec* và *đánh
giá tác động Completion Gate*. F-S009-01 KHÔNG được phủ bởi bất kỳ check nào đang tồn tại,
nên đóng nó cần **một REQUIRED check mới**. Ba rào, cả ba đều là hành vi của chủ dự án theo
`STATE_AUTHORITY.md`:

1. **Gate.** Completion Gate của `WP-A4` đang FROZEN (2026-08-23, amended `OD-A4-01`).
   `STATE_AUTHORITY.md`: *"FROZEN gates are immutable"*, *"Changing a gate or a budget is an
   Owner action."*
2. **State.** `WP-A4` = `DONE`. `DONE` do *"Owner, or a designated completion authority"*
   viết; đưa `DONE` → `IN_PROGRESS` cũng vậy.
3. **Scope Lock.** `indicators.py` KHÔNG nằm trong danh sách Allowed của Expected Touch Area
   `WP-A4` → `SCOPE EXPANSION REQUIRED`.

Phiên này KHÔNG tự làm cả ba, và KHÔNG tự đổi trạng thái `WP-A4`.

    Trạng thái đúng theo V4.3 =  OWNER_DECISION_REQUIRED
    KHÔNG phải               =  ABSORPTION_LIMIT_REACHED
    KHÔNG còn là             =  OWNER_ASSIGNMENT_REQUIRED

Khe **ownership** đã ĐÓNG bằng quyết định ở II.1 (capability owner = `CAP-DATA`). Cái còn lại
không phải khe ownership mà là **khe thẩm quyền thi hành**: chọn phương tiện mang bản sửa bên
trong `CAP-DATA`. `OWNER_DECISION_REQUIRED` là một trong năm hard-stop canonical, không phải
state tự chế.

## II.7 Đúng MỘT quyết định còn lại của chủ dự án

Cùng hình dạng với `DEC-014` / `OD-A4-01` đã làm cho `F-E2A1R3-05`, cộng đúng một yếu tố mới
(mở lại một gói đã DONE). Ba lựa chọn của `CAPABILITY_MODEL.md` khi cần Owner:

- **(A) Mở rộng phạm vi `WP-A4`** — mở lại `WP-A4` (`DONE` → `IN_PROGRESS`), phê duyệt
  `COMPLETION GATE CHANGE PROPOSAL` thêm ĐÚNG MỘT REQUIRED check (cửa sổ indicator daily phải
  theo NGÀY LỊCH; ngày không đủ đầu vào lịch phải ra NaN/DEGRADED/INVALID theo ST §3 + BT
  §18), và mở Expected Touch Area sang `src/eth_dca_os/indicators.py`. Chín check FROZEN gốc
  giữ nguyên câu chữ. Chi phí: `WP-A4` rời trạng thái DONE, và bản sửa tiêu **một repair
  cycle** của `CAP-DATA` (xem II.8).
- **(B) DESCOPE / defer** — chuyển sang hardening backlog kèm `RE_TRIGGER_CONDITION`.
  **Hệ quả phải nói thẳng:** `T-06` sẽ chạy trên dữ liệu thật có gap và cho ra Buy Score sai
  âm thầm. Điều này mâu thuẫn trực tiếp với `DEC-011` điểm 9 ("lỗi có thể làm sai quyết định
  phải fail visibly / fail closed"). Không khuyến nghị.
- **(C) Phê duyệt một task mới như ngoại lệ** — `CAPABILITY_MODEL.md` nói rõ C **không bao
  giờ** được chọn tự động, và phạm vi lớn hơn **không** tự sinh thêm repair cycle. Phiên này
  KHÔNG tạo task ID; nếu chủ dự án chọn C thì chính chủ dự án đặt ID.

Khuyến nghị: **(A)** — cùng tiền lệ `DEC-014`, giữ số task ID mới = 0, và giữ bản sửa ở đúng
capability mà chủ dự án vừa phê chuẩn.

## II.8 Budget `CAP-DATA` — đo lại bằng git, không chép báo cáo

    Effective Risk            = 3   = MAX(Local Risk 3, Blast Radius 2)
                                      từ routing metadata ĐÃ FROZEN của WP-A4 (R:3, B:2)
    ALLOWED repair cycles     = CHƯA LƯỢNG HOÁ (V4.3 default theo Effective Risk)
    USED repair cycles        = 0
    REMAINING repair cycles   = default nguyên vẹn, KHÔNG biểu diễn được bằng một con số

`ALLOWED` chưa có con số vì `DELIVERY_LOOP.md` §II.4 nói rõ `<N>` là **PROJECT value** và tầng
dự án chưa khai. Nguyên nhân gốc đã có số hiệu: `HARDENING_BACKLOG.md` **H-10** (chưa có
Golden Baseline). Phiên này **KHÔNG** chọn một con số tiện tay.

`USED = 0`: lượt `06b381c..85fa30f` là **implementation ban đầu**, không phải repair cycle —
đúng tiền lệ mà chính ledger dùng cho `CAP-PROV` ("2 repair cycle, **ngoài lượt implementation
ban đầu**"). Đo lại tại phiên này:

    git diff --shortstat 06b381c..HEAD -- <production paths>
    -> 5 files changed, 282 insertions(+), 36 deletions(-)      (khớp ledger)
    git diff --shortstat 85fa30f..07bb241 -- <production paths>
    -> 0                                                        (commit ledger-fix, không tiêu)

Budget **KHÔNG** được reset vì `WP-A4` DONE.

**Một dữ kiện mới, có trọng lượng cho quyết định ở II.7:**

    git log --oneline 666de14..HEAD -- src/eth_dca_os/indicators.py   ->  0 commit

`indicators.py` chưa từng bị chạm kể từ baseline `666de14`. Nghĩa là F-S009-01 nằm **NGOÀI**
cumulative repair diff của cả `CAP-PROV` lẫn `CAP-DATA`. Theo `REVIEW_PROTOCOL.md` ("a finding
inside the cumulative repair diff … does not open a new repair cycle"), điều ngược lại đúng ở
đây: đây KHÔNG phải khiếm khuyết của một lượt sửa đã có, nên sửa nó **sẽ tiêu một repair cycle
mới** của owner nhận nó. Bản sửa không miễn phí — chủ dự án cần biết điều này trước khi chọn.

`CAP-PROV` bị loại làm nơi đóng, y như `DEC-014` đã kết luận: `REMAINING = 0`,
`OWNER_EXTENSION = NOT GRANTED` (`DEC-012`).

## II.9 Ảnh hưởng tới trạng thái hiện tại

- `WP-A4` vẫn **DONE**, 9/9 REQUIRED PASS. Không check nào bị thêm, hạ, gộp hay nới ở phiên
  này. Không mở lại.
- `WP-A1` không đổi. `CAP-PROV` allowed=2 / used=2 / remaining=0 không đổi.
- Số task ID mới tạo = **0**.
- `H-01`…`H-15` không bị sửa. `H-08`, `H-14`, `H-15` không mở.
