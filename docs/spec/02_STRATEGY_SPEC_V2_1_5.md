# ETH DCA Operating System V2.1.5 — Strategy Specification

**SELF-CONTAINED LOCKED STRATEGY CORE**

## 1. Opportunity Score

OSCORE nằm trong 0–100 và bằng tổng ba factor: Price Location 0–50, Market Stress 0–30, Relative Value 0–20. Score cao nghĩa là điều kiện tích lũy hấp dẫn hơn theo rule V2.1.5. KHÔNG được diễn giải OSCORE như xác suất tăng giá.

Capital Engine phải dùng giá trị raw. UI có thể làm tròn để hiển thị.

### 1.1 Price Location — 0 đến 50

```
DD365     = CurrentPrice / High365 - 1
D         = CLAMP((-DD365 - 0.05) / 0.55, 0, 1)
MA_RATIO  = CurrentPrice / MA200
M         = CLAMP((1.05 - MA_RATIO) / 0.40, 0, 1)
P         = CLAMP((0.90 - Percentile365) / 0.80, 0, 1)
PRICE_LOCATION_SCORE = 50 x (0.50*D + 0.30*M + 0.20*P)
```

High365 = giá đóng cửa ngày cao nhất trong 365 ngày gần nhất. Percentile365 tính theo tỷ lệ 0–1 của số daily close thấp hơn giá hiện tại trong 365 ngày.

### 1.2 Market Stress — 0 đến 30

```
R   = CLAMP((55 - RSI14) / 30, 0, 1)
S7  = CLAMP((-RETURN7 - 0.02) / 0.18, 0, 1)
VR  = AVG(volume, 7) / AVG(volume, 90)
V   = 0 if RETURN7 >= 0 else CLAMP((VR - 1) / 1.5, 0, 1)
MARKET_STRESS_SCORE = 30 x (0.50*R + 0.30*S7 + 0.20*V)
```

RSI14 theo công thức Wilder chuẩn trên daily close.

### 1.3 Relative Value — 0 đến 20

```
ETHBTC = ETHUSDT / BTCUSDT
R30    = ETHBTC_today / ETHBTC_30d_ago - 1
W      = CLAMP((-R30 - 0.02) / 0.18, 0, 1)
RP     = CLAMP((0.70 - ETHBTC_Percentile180) / 0.60, 0, 1)
RELATIVE_VALUE_SCORE = 20 x (0.60*W + 0.40*RP)
```

### 1.4 Tổng hợp

```
OSCORE = PRICE_LOCATION_SCORE + MARKET_STRESS_SCORE + RELATIVE_VALUE_SCORE
```

## 2. Redundancy diagnostics — bắt buộc, không phải input chiến lược

Phần lớn trọng số của OSCORE phái sinh từ cùng một tín hiệu giá. Các chẩn đoán dưới đây là bắt buộc trong mọi official run; chúng không được đưa ngược vào công thức của V2.1.5. Mọi thay đổi công thức phải sang V2.2.

### 2.1 Correlation matrix

Tính ma trận tương quan Pearson và Spearman trên toàn bộ chuỗi lịch sử cho tám sub-factor D, M, P, R, S7, V, W, RP và cho ba top-level factor.

Cảnh báo HIGH_REDUNDANCY nếu bất kỳ cặp sub-factor nào trong cùng một factor có |corr| > 0.85 trên phần lớn lịch sử, hoặc nếu corr(PRICE_LOCATION, MARKET_STRESS) > 0.85.

### 2.2 Variance Inflation Factor

| Nhóm | Biến | Ngưỡng |
|---|---|---|
| Price Location | D, M, P | VIF > 5 = WARNING; VIF > 10 = SEVERE |
| Market Stress | R, S7, V | VIF > 5 = WARNING; VIF > 10 = SEVERE |

Kết quả SEVERE ở bất kỳ nhóm nào kích hoạt Failure Signal FS-04.

### 2.3 Pre-registered ablation models

| Model | Định nghĩa | Mục đích |
|---|---|---|
| Price Minimal | PRICE_LOCATION = 50 x (0.70*D + 0.30*M); bỏ P | Kiểm tra P có đóng góp gì ngoài D không |
| Stress Minimal | MARKET_STRESS = 30 x (0.60*S7 + 0.40*V); bỏ R | Kiểm tra RSI có đóng góp gì ngoài Return7 không |
| Both Minimal | Áp dụng đồng thời cả hai | Kiểm tra mô hình rút gọn tổng thể |

Nếu model rút gọn cho kết quả tương đương trong sai số của gate, kết luận là ưu tiên mô hình đơn giản hơn ở version SAU. Không sửa V2.1.5 trong cùng official test.

### 2.4 Volume structural-trend diagnostic

Thị phần Binance biến động qua các năm nên VR = AVG(volume,7)/AVG(volume,90) có thể nhiễm xu hướng cấu trúc không liên quan tới stress thị trường.

Bắt buộc chạy diagnostic song song với V thay bằng rolling z-score của volume trong cửa sổ 365 ngày, và báo cáo chênh lệch kết quả. Đây là diagnostic và ablation; KHÔNG thay factor production của V2.1.5.

## 3. Data degradation rule

| State | Quy tắc |
|---|---|
| GOOD | Toàn bộ OHLCV ETH/BTC và các indicator bắt buộc hợp lệ. |
| DEGRADED | Một sub-component không khả dụng. KHÔNG rescale và KHÔNG chuẩn hóa lên. Sub-component thiếu nhận contribution = 0. OSCORE là tổng phần còn lại theo đúng trọng số gốc. Opportunity unlock không được tăng do đầu vào DEGRADED. |
| INVALID | Giá/lịch sử ETH hoặc indicator bắt buộc không hợp lệ. Chặn mọi action Smart và Opportunity mới. Base schedule vẫn có thể chạy theo fallback được ghi nhận. |

Nguyên tắc: dữ liệu xấu phải kéo score xuống, không bao giờ đẩy score lên.

## 4. Monthly capital allocation

```
BASE = 50%   |   SMART = 30%   |   OPPORTUNITY CONTRIBUTION = 20%   (baseline)
SMART_UNLOCK       = CLAMP((OSCORE - 35) / 35, 0, 1)
OPPORTUNITY_UNLOCK = 0.60 x CLAMP((OSCORE - 65) / 30, 0, 1)
```

Unlock là quyền sử dụng vốn, không phải lệnh mua. Ladder mới quyết định execution.

## 5. Opportunity hysteresis

- ACTIVATE trạng thái Opportunity khi OSCORE >= opportunity_activate_score (baseline 68).
- SUSPEND trạng thái Opportunity khi OSCORE <= opportunity_suspend_score (baseline 62).
- Trong vùng 62 < OSCORE < 68, giữ nguyên trạng thái trước đó.
- ACTIVE với unlock = 0 trong vùng 62–65 là trạng thái HỢP LỆ, không phải lỗi: ladder và state cũ vẫn tồn tại theo lifecycle, nhưng không được reserve vốn Opportunity mới.
- Suspended zone giữ reserve tối đa 7 accounting day, sau đó cancel và release.

## 6. Smart unlock modes

| Mode | Định nghĩa |
|---|---|
| HWM (baseline) | smart_unlock_peak = giá trị SMART_UNLOCK lớn nhất quan sát được trong tháng hiện tại. Vốn đã execute không bao giờ relock. Peak reset khi sang accounting month mới. |
| NO_HWM | Smart available bám theo SMART_UNLOCK hiện tại theo lifecycle bình thường, có hysteresis, không mang peak qua ngày. Vốn đã execute không relock. |
| DECAY_HWM | smart_unlock_peak là tỷ lệ trên thang 0–1. Cứ mỗi hwm_decay_days (baseline 7) x 24h mà peak không được revalidate bởi một SMART_UNLOCK bằng hoặc cao hơn, peak giảm tuyệt đối hwm_decay_step (baseline 0.10, tức 10 điểm phần trăm trên thang 0–1). Sàn của peak là SMART_UNLOCK hiện tại. Vốn đã execute không relock. |

HWM là baseline vì nó giữ đúng hypothesis ban đầu, nhưng nó bất đối xứng và luôn nghiêng về phía cho chiến lược tiêu vốn nhiều hơn. Vì vậy cả ba mode BẮT BUỘC nằm trong ablation của Gate 2 và phải được báo cáo đóng góp riêng vào accumulation, cash drag và hành vi cuối tháng.

## 7. Opportunity Fund cap

```
OpportunityCapVND = MonthlyOpportunityContributionVND x opportunity_cap_months
```

- Baseline opportunity_cap_months = 4.
- Phần Opportunity không dùng được rollover sang tháng sau.
- Khi fund đã đạt cap, contribution Opportunity mới của tháng overflow sang Smart của chính tháng đó, thay vì tiếp tục tăng reserve.
- Quỹ phải được quản lý bằng ledger, không phải một balance mutable.

## 8. Capital accounting và partial fill

```
TOTAL = AVAILABLE + RESERVED + DEPLOYED
```

| Sự kiện | Hạch toán |
|---|---|
| Tạo zone / reservation | AVAILABLE -= amount; RESERVED += amount. Chỉ được tạo nếu requested_reserve <= AVAILABLE. |
| Full fill | RESERVED -= filled; DEPLOYED += filled. |
| Partial fill | Chỉ phần đã fill chuyển RESERVED -> DEPLOYED. Phần còn lại TIẾP TỤC ở RESERVED cho tới hết ACTION_TTL. |
| TTL expiry / MISSED | Phần chưa fill chuyển RESERVED -> AVAILABLE. |
| Cancel / invalidation / expiry | Toàn bộ phần còn lại chuyển RESERVED -> AVAILABLE. |

- Không được double reservation giữa Smart, Opportunity và Crash.
- VND allocation là source of truth. Lượng USDT được derive tại thời điểm funding hoặc execution; zone được coi là hoàn thành theo phân bổ VND, không theo mục tiêu USDT cố định.

## 9. Base DCA schedule

| Accounting day | Local time | % Base |
|---|---|---|
| Day 3 | 12:00 Asia/Ho_Chi_Minh | 40% |
| Day 13 | 12:00 Asia/Ho_Chi_Minh | 30% |
| Day 23 | 12:00 Asia/Ho_Chi_Minh | 30% |

- Base luôn phải được giải ngân trong tháng, độc lập với OSCORE.
- Nếu OSCORE >= 70 tại thời điểm daily score mới được activate, tranche Base kế tiếp có thể execute sớm; phải đánh dấu EXECUTED_EARLY và không lặp lại vào ngày gốc.
- Tối đa một tranche Base được kéo sớm tại mỗi lần score mới active.
- **[F3]** Nếu nến 15m tại 12:00 local của ngày trigger nằm trong data gap, tranche được execute tại nến 15m hợp lệ đầu tiên sau gap và gắn tag DELAYED_DATA_FILL (Backtest §18). Tranche Base không bao giờ bị bỏ vì gap dữ liệu.

## 10. Month-End policy

- Không tạo Smart ladder mới sau Day 24.
- Day 25–27: settle 50% phần Base còn lại nếu còn.
- Day 28: giải ngân 100% phần Base còn lại.
- Smart còn lại, nếu OSCORE >= 45: giải ngân toàn bộ phần còn lại.
- Smart còn lại, nếu OSCORE < 45: mua 50% phần còn lại, chuyển 50% sang Opportunity Fund.
- Opportunity Fund không bao giờ bị ép mua cuối tháng.
- Month-End settlement KHÔNG chịu giới hạn max_zones_per_cycle.

## 11. ADR30 và continuous spacing

```
ADR30 = AVG(abs(daily_return), 30)
```

ScoreMultiplier dùng nội suy tuyến tính từng đoạn qua các anchor dưới đây. Đây là bản làm mượt giữ đúng hypothesis gốc; không dùng một đường thẳng duy nhất.

| OSCORE anchor | Multiplier |
|---|---|
| <= 40 | 0.80 |
| 60 | 0.90 |
| 70 | 1.00 |
| 80 | 1.15 |
| >= 90 | 1.30 |

Giữa hai anchor liền kề: nội suy tuyến tính. Ngoài hai đầu: clamp.

```
SmartSpacing       = CLAMP(ADR30 x smart_spacing_factor x ScoreMultiplier, smart_spacing_min, smart_spacing_max)
OpportunitySpacing = CLAMP(SmartSpacing x opportunity_spacing_multiplier, 6%, 15%)
```

Baseline: smart_spacing_factor = 2.0; smart_spacing_min = 4%; smart_spacing_max = 12%; opportunity_spacing_multiplier = 1.25.

## 12. Smart ladder

```
S0 = Anchor
S1 = Anchor x (1 - SmartSpacing)
S2 = Anchor x (1 - 2 x SmartSpacing)
```

- Allocation tối đa ba tranche: 33% / 33% / 34% của phần Smart THỰC SỰ đã unlock.
- Không được reserve vốn chưa unlock.
- AnchorPrice = giá ETHUSDT có thể thực thi tại thời điểm ladder được tạo.

## 13. Opportunity ladder

Chỉ chuyển weight giữa O4 và O0 để giữ đúng hai điểm đầu cuối của hypothesis gốc; không normalize lại toàn bộ.

```
t  = CLAMP((OSCORE - 70) / 10, 0, 1)
O0 = 10% x t;  O1 = 15%;  O2 = 20%;  O3 = 25%;  O4 = 40% - 10% x t
```

| OSCORE | O0 | O1 | O2 | O3 | O4 | Tổng |
|---|---|---|---|---|---|---|
| <= 70 | 0% | 15% | 20% | 25% | 40% | 100% |
| 75 | 5% | 15% | 20% | 25% | 35% | 100% |
| >= 80 | 10% | 15% | 20% | 25% | 30% | 100% |

```
On = Anchor x (1 - n x OpportunitySpacing)
```

## 14. Crash ladder

Crash KHÔNG tạo tiền mới. Chỉ dùng phần Smart/Opportunity đã unlock và đủ điều kiện.

Tại thời điểm vào CRASH: cancel các Opportunity zone chưa execute đang xung đột, release reserve của chúng, RỒI mới tạo Crash ladder. Thứ tự này bắt buộc để tránh double count.

**[F5] Định nghĩa eligible capital:** eligible capital của Crash ladder = snapshot tổng vốn Smart AVAILABLE + Opportunity AVAILABLE (tức đã unlock và chưa nằm trong reservation nào) đo NGAY SAU bước cancel/release ở trên. Allocation C0–C3 áp lên snapshot này; snapshot là bất biến trong suốt vòng đời Crash ladder, không tính lại khi unlock thay đổi sau đó.

```
CrashAnchor  = CurrentPrice tại thời điểm Crash Mode bắt đầu
CrashSpacing = MAX(OpportunitySpacing, 7%)
```

| Crash zone | Allocation của phần vốn đủ điều kiện |
|---|---|
| C0 | 20% |
| C1 | 25% |
| C2 | 25% |
| C3 | 30% |

Toàn bộ daily limit, single-buy limit, cooldown và max-zones-per-cycle vẫn áp dụng trong Crash.

## 15. Execution limits

| Limit | Baseline |
|---|---|
| Opportunity max daily deployment | 20% Opportunity Fund hiện tại; reset 00:00 Asia/Ho_Chi_Minh |
| Max normal zones per execution cycle | 2 (không áp dụng cho Base schedule và Month-End settlement) |
| Capital priority khi cùng trigger | Base -> Smart -> Opportunity |
| Cooldown sau execution Smart/Opportunity/Crash | 48h |
| Cooldown override | Khi CurrentPrice <= LastExecutionPrice x (1 - 7%) |

Crash KHÔNG bypass cooldown, nhưng cooldown override vẫn có hiệu lực và trong một cú sập thực sự sẽ kích hoạt nhiều lần. Vì vậy backtest BẮT BUỘC báo cáo tần suất cooldown override theo từng regime; nếu không, câu "Crash không bypass cooldown" sẽ gây hiểu nhầm.

### 15.1 Thứ tự thực thi khi nhiều zone cùng trigger [F2]

Khi nhiều zone bị xuyên trong cùng một nến 15m, thứ tự thực thi xác định như sau, và max_zones_per_cycle áp SAU khi đã sắp thứ tự:

1. Giữa các pool: Base -> Smart -> Opportunity (Crash ladder xếp theo pool nguồn vốn của nó, sau Smart/Opportunity thường).
2. Trong cùng pool, giữa hai ladder khác nhau: ladder có created_at sớm hơn xử lý trước.
3. Trong cùng ladder: zone_index tăng dần (S0 trước S1, C0 trước C1...).

Zone hợp lệ nhưng bị chặn bởi max_zones_per_cycle giữ nguyên trạng thái TRIGGERED và được xét lại ở cycle kế tiếp theo cùng quy tắc.

## 16. Market Regime và Execution State

| Loại | Enum |
|---|---|
| Market Regime | NORMAL / STRESSED / CRASH / RECOVERY |
| Execution State | WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED |

Market Regime và Execution State là hai chiều độc lập và phải được lưu riêng. Mọi Market Regime đều dùng chung tập Execution State.

## 17. Regime rules

### 17.1 Crash entry

```
ENTER CRASH if (Return7D <= -15% OR Return24H <= -10%) AND OSCORE >= 75
```

### 17.2 Crash exit và Recovery

```
EXIT candidate if Return24H > -5% AND Return7D > -10% liên tục trong 48h
CRASH -> RECOVERY trong 72h -> NORMAL nếu không re-enter
```

Trong backtest, Return24H nội ngày được tính trên 96 nến 15m liền trước.

### 17.3 STRESSED label [F1]

STRESSED là **nhãn dẫn xuất chỉ dùng cho reporting và phân rã metric** (ví dụ tần suất cooldown override theo regime, Backtest §16). STRESSED KHÔNG có bất kỳ hiệu ứng nào lên unlock, ladder, cooldown, limit hay execution trong V2.1.x.

```
STRESSED if (Return7D <= -10% OR Return24H <= -7%) AND regime hiện tại không phải CRASH và không phải RECOVERY
NORMAL   = phần còn lại (không CRASH, không RECOVERY, không STRESSED)
```

Return7D và Return24H dùng cùng định nghĩa với §17.1 (Return24H trên 96 nến 15m trong backtest). Nhãn được đánh giá lại mỗi nến sau khi cập nhật trạng thái CRASH/RECOVERY (Backtest §19 bước 10).

## 18. Ladder lifecycle: immutability, invalidation, expiry

### 18.1 Immutability

- AnchorPrice và spacing_pct là BẤT BIẾN trong suốt vòng đời ladder.
- Không regenerate ladder mỗi khi giá thay đổi.
- Buy zone KHÔNG BAO GIỜ được dịch chuyển lên trên. Zone chỉ được chuyển giữa các trạng thái trong enum §19.

### 18.2 Bullish invalidation

```
InvalidationPrice = Anchor x (1 + MAX(12%, 2 x spacing))
```

Cần HAI daily close hoàn chỉnh liên tiếp lớn hơn InvalidationPrice thì ladder chuyển INVALIDATED và các zone còn lại chuyển CANCELLED, reserve được release.

### 18.3 Expiry

| Ladder | Quy tắc hết hạn |
|---|---|
| Smart | Hết hạn cuối accounting month. |
| Opportunity | Hết hạn sau 90 ngày kể từ khi tạo. |
| Crash | Khi CRASH -> RECOVERY, các Crash zone chưa execute chuyển SUSPENDED. Sau 72h Recovery nếu vẫn chưa hit thì CANCEL và release reserve. |

Ladder đã expired hoặc invalidated phải được ARCHIVE, không được xóa.

## 19. Status enums

| Enum | Giá trị |
|---|---|
| Zone status | ACTIVE / SUSPENDED / TRIGGERED / ACTION_PENDING / PARTIALLY_FILLED / EXECUTED / CANCELLED / EXPIRED / MISSED |
| Ladder status | ACTIVE / SUSPENDED / COMPLETED / INVALIDATED / EXPIRED / CANCELLED |
| Execution state | WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED |
| Market regime | NORMAL / STRESSED / CRASH / RECOVERY |
| Data quality | GOOD / DEGRADED / INVALID |

## 20. Reason codes

Mọi state transition và recommendation phải log reason code để audit và backtest.

```
BASE_SCHEDULE / BASE_ADVANCE_SCORE / MONTH_END_BASE / MONTH_END_SMART
SMART_ZONE_S0 / S1 / S2
OPPORTUNITY_O0 / O1 / O2 / O3 / O4
CRASH_ENTRY_7D / CRASH_ENTRY_24H / CRASH_ZONE_C0..C3 / CRASH_EXIT / RECOVERY_END
COOLDOWN_START / COOLDOWN_OVERRIDE / DAILY_LIMIT_BLOCK / MAX_ZONES_BLOCK
FUNDING_REQUIRED / FUNDING_COMPLETE / ACTION_TTL_EXPIRED / ACTION_MISSED / PARTIAL_FILL
BULLISH_INVALIDATION / LADDER_EXPIRED / OPPORTUNITY_SUSPENDED / CAP_OVERFLOW_TO_SMART
DATA_DEGRADED / DATA_INVALID / DELAYED_DATA_FILL
```

## 21. Complete baseline strategy_config

Bảng này là nguồn duy nhất cho baseline config. **[F7]** Nó phải khớp với schema strategy_config ở Data Model §2 theo quy tắc: mọi field dưới đây tồn tại trong schema, và schema chỉ được phép có thêm đúng BA field metadata: `config_name`, `created_at`, `strategy_config_hash` (xem Section Inventory XC-1).

| Field | Baseline |
|---|---|
| strategy_version | V2.1.5 |
| base_pct | 0.50 |
| smart_pct | 0.30 |
| opportunity_pct | 0.20 |
| opportunity_cap_months | 4 |
| smart_unlock_mode | HWM |
| hwm_decay_step | 0.10 |
| hwm_decay_days | 7 |
| opportunity_activate_score | 68 |
| opportunity_suspend_score | 62 |
| smart_spacing_factor | 2.0 |
| smart_spacing_min | 0.04 |
| smart_spacing_max | 0.12 |
| opportunity_spacing_multiplier | 1.25 |
| opportunity_daily_limit_pct | 0.20 |
| max_zones_per_cycle | 2 |
| cooldown_hours | 48 |
| cooldown_override_pct | 0.07 |
| suspended_zone_hold_days | 7 |
| accounting_timezone | Asia/Ho_Chi_Minh |

Lưu ý: spot_fee, slippage, delay và funding policy KHÔNG thuộc strategy_config. Chúng nằm ở execution_config (Data Model §3) vì Gate 2 và Gate 3 biến thiên hai nhóm khác nhau.
