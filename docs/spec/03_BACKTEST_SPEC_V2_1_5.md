# ETH DCA Operating System V2.1.5 — Backtest Specification

**ANCHOR-BALANCED GATES • SEPARATE OOS • FIXED MANIFESTS • FULL PROCESSING ORDER**

## 1. Core principle

Backtest phải mô phỏng đúng sản phẩm manual-execution, không mô phỏng resting limit order. Khi không xác định được thứ tự intraday, dùng giả định BẢO THỦ HƠN cho strategy. Backtest tồn tại để bác bỏ chiến lược, không phải để trang trí cho nó.

**NO LOOKAHEAD | NO FUTURE DATA | NO PERFECT FILL | NO POST-HOC PARAMETER FITTING | NO SYNTHETIC P2P AS REAL P2P**

## 2. Data and chronology

- Primary performance origin: 2019-01-01, với điều kiện warm-up 365 ngày hợp lệ trước ngày đó; nếu không, lấy ngày đầu tiên có đủ toàn bộ indicator bắt buộc.
- Pre-OOS gate cutoff: 2024-12-31.
- Hard OOS: 2025-01-01 đến frozen end date.
- Indicator data: Binance Spot ETHUSDT và BTCUSDT, khung 1D.
- Execution data: Binance Spot ETHUSDT, khung 15m.
- Market timestamp lưu UTC; accounting và reporting theo Asia/Ho_Chi_Minh.
- Daily score của ngày D chỉ được áp dụng SAU khi nến daily nguồn đã đóng hoàn toàn.

### 2.1 VND accounting trong backtest [F6]

Quy tắc hạch toán VND của toàn bộ backtest, gom về một chỗ:

- Gate 1 và Gate 2 chạy trên **đơn vị danh nghĩa**: 1 USDT = 1 đơn vị kế toán. Contribution VND được biểu diễn bằng đơn vị danh nghĩa này; không dùng bất kỳ chuỗi tỷ giá VND/P2P lịch sử nào làm input mô phỏng hay điều kiện gate (nhất quán Product §14).
- Gate 3: chi phí funding được mô hình bằng funding_delay và funding_policy, KHÔNG bằng tỷ giá VND. VND/P2P spread lịch sử (nếu có dữ liệu) chỉ được dùng như **overlay sensitivity** trong reporting §16 — cộng/trừ spread lên kết quả đã có, không chạy lại engine, không tham gia điều kiện PASS.
- Ý nghĩa: mọi metric gate (AccumulationEfficiency, NetEdgePct) đo bằng ETH tích lũy trên cùng contribution danh nghĩa, không phụ thuộc ước lượng tỷ giá.

## 3. Multi-anchor pre-OOS gate windows

Với chỉ khoảng 6 năm dữ liệu pre-OOS, số block 24 tháng không chồng lấn là rất ít và ranh giới block phụ thuộc hoàn toàn vào một ngày neo tùy chọn. Để loại bỏ sự tùy tiện đó, Gate 1 dùng bốn anchor offset. Trong mỗi anchor set, các block KHÔNG chồng lấn nhau.

| Anchor | Các block 24M hoàn chỉnh, kết thúc <= 2024-12-31 | Số block |
|---|---|---|
| +0M | W1 2019-01–2020-12; W2 2021-01–2022-12; W3 2023-01–2024-12 | 3 |
| +6M | W4 2019-07–2021-06; W5 2021-07–2023-06 | 2 |
| +12M | W6 2020-01–2021-12; W7 2022-01–2023-12 | 2 |
| +18M | W8 2020-07–2022-06; W9 2022-07–2024-06 | 2 |
| **TỔNG** | | **9** |

Các window thuộc anchor set khác nhau CÓ chồng lấn nhau. Chúng KHÔNG được coi là chín quan sát độc lập. Không được tính p-value giả từ n = 9.

## 4. Window coverage weighting

Chín window không phủ dữ liệu đều nhau. Bảng dưới đây là bắt buộc trong mọi báo cáo official.

| Giai đoạn | Xuất hiện trong bao nhiêu window |
|---|---|
| 2019-01 – 2019-06 | 1 |
| 2019-07 – 2019-12 | 2 |
| 2020-01 – 2020-06 | 3 |
| 2020-07 – 2023-06 | 4 |
| 2023-07 – 2023-12 | 3 |
| 2024-01 – 2024-06 | 2 |
| 2024-07 – 2024-12 | 1 |

Phần giữa của mẫu được đếm gấp bốn lần so với hai đầu. Giai đoạn 2020-07 đến 2023-06 chứa trọn đợt sụt giảm 2022, tức là giai đoạn thuận lợi nhất cho một chiến lược mua khi giá giảm. Vì vậy median gộp trên chín window bị thiên vị có hệ thống về phía có lợi cho strategy.

### 4.1 Chỉ số chính chống thiên vị

```
AnchorSetMedian_k = MEDIAN(AccumulationEfficiency của các window thuộc anchor set k),  k in {0, 6, 12, 18}
PrimaryMedian     = MEDIAN(AnchorSetMedian_0, AnchorSetMedian_6, AnchorSetMedian_12, AnchorSetMedian_18)
PooledMedian      = MEDIAN(AccumulationEfficiency của cả 9 window)   // DESCRIPTIVE ONLY
```

PrimaryMedian cho mỗi anchor set trọng số bằng nhau, nên loại bỏ hiệu ứng đếm gấp bốn của phần giữa. Ngưỡng cứng của Gate 1 và Gate 3 áp lên PrimaryMedian. PooledMedian chỉ được báo cáo kèm nhãn descriptive.

Báo cáo bắt buộc: bảng chín window, bốn AnchorSetMedian, PrimaryMedian, PooledMedian và bảng coverage ở trên.

## 5. Manual and funding delay model

```
Smart trigger:        LOW[T] <= zone_price   -> ACTION_PENDING tạo tại close của nến T
Opportunity trigger:  CLOSE[T] <= zone_price -> ACTION_PENDING tạo tại close của nến T
```

KHÔNG có fill tại zone_price. Execution proxy = OPEN của nến 15m đầu tiên tại hoặc sau (user_delay + funding_delay), với điều kiện action vẫn còn trong TTL và chưa bị invalidated.

```
total_delay = user_delay + funding_delay   (funding_delay = 0 nếu USDT treasury đã đủ)
```

| User delay scenario | Giá trị |
|---|---|
| Gate 1 deterministic | 15m |
| Fast | 1h |
| Realistic baseline | 4h |
| Slow | 12h |

| Funding delay scenario | Giá trị |
|---|---|
| BULK / pre-funded | 0 |
| Fast P2P | 15m |
| ON_DEMAND baseline | 1h |
| Slow P2P | 4h |

P2P-unavailable-in-crash là stress scenario riêng: khi ở CRASH và action cần funding, funding có thể không khả dụng suốt TTL và action trở thành MISSED. Scenario này báo cáo riêng, không trộn vào denominator của manifest ma sát tất định.

## 6. Behavioral simulation

Behavioral simulation KHÔNG áp dụng cho Gate 1. Gate 1 dùng delay tất định. Behavioral simulation chỉ thuộc robustness của Gate 3.

| Trigger local time | Phân phối hành vi |
|---|---|
| 07:00 – 22:59 | 50% xử lý trong <= 1h; 30% <= 4h; 15% <= 12h; 5% MISSED. |
| 23:00 – 06:59 | 10% <= 1h; 25% <= 4h; 45% thực thi tại OPEN của nến 15m đầu tiên tại hoặc sau 07:00 local nếu vẫn còn TTL; 20% MISSED. |

- ACTION_TTL = 12h baseline. Trigger ban đêm có thể hết hạn trước khi người dùng xử lý.
- N = 1000 simulations, seed cố định. Báo cáo median, P10, P90.
- Lý do tách ngày/đêm: zone trigger tập trung vào giờ giao dịch Mỹ, tức ban đêm ở Việt Nam.

## 7. Gate 1 — structural value

Giả định thực thi của Gate 1: user_delay = 15m tất định, pre-funded/BULK nên funding_delay = 0, spot fee = 0.10%, slippage = 0, behavioral simulation OFF.

| Điều kiện cứng | PASS | STRONG |
|---|---|---|
| PrimaryMedian AccumulationEfficiency (§4.1) | >= 102% | >= 105% |
| Tỷ lệ window trong 9 window có AccumulationEfficiency >= 100% | >= 2/3 (tức >= 6/9) | >= 3/4 (tức >= 7/9) |
| Window xấu nhất, Accumulation Delta | >= -5% | >= -3% |
| Không anchor set nào có TOÀN BỘ window dưới 100% | Bắt buộc | Bắt buộc |

Điều kiện cuối chặn trường hợp một anchor offset mâu thuẫn hoàn toàn với kết luận chung.

## 8. OOS hard condition

| Giai đoạn | PASS | STRONG |
|---|---|---|
| 2025-01-01 -> frozen end | AccumulationEfficiency >= 100% | >= 102% |

- OOS KHÔNG nằm trong chín window pre-OOS và luôn được báo cáo riêng.
- Bắt buộc báo cáo OOS_Months = số tháng thực tế của giai đoạn OOS.
- Nếu OOS_Months < 24, đánh dấu SHORT_OOS. Khi đó OOS là MỘT quan sát ngắn duy nhất và KHÔNG được diễn giải ngang hàng với một gate window 24 tháng. Ngưỡng vẫn áp dụng, nhưng báo cáo phải nêu rõ độ dài và cảnh báo phương sai cao hơn.

## 9. Gate 2 — strategy-parameter robustness

Gate 2 CHỈ thay strategy parameter. KHÔNG thay user delay, funding delay, fee, slippage hoặc funding policy — những chiều đó thuộc Gate 3. Giả định thực thi low-friction của Gate 1 được giữ cố định trong toàn bộ Gate 2.

| Strategy dimension | Levels |
|---|---|
| base_pct | 0.50 / 0.60 / 0.70 |
| opportunity_pct | 0.10 / 0.20 / 0.30 |
| opportunity_cap_months | 2 / 3 / 4 / 6 |
| cooldown_hours | 24 / 48 / 72 |
| cooldown_override_pct | 0.05 / 0.07 / 0.10 |
| smart_spacing_factor | 1.5 / 2.0 / 2.5 |
| score weights (PL/MS/RV) | 50/30/20 ; 55/25/20 ; 45/35/20 ; 50/25/25 ; 50/35/15 |
| smart_unlock_mode | HWM / NO_HWM / DECAY_HWM |

```
Validity constraint:  smart_pct = 1 - base_pct - opportunity_pct >= 0.15
```

### 9.1 Gate 2 manifest generation — phương pháp khóa cứng

1. Tạo baseline config theo Strategy §21.
2. Sinh ứng viên OFAT: với mỗi chiều trong tám chiều, thay chiều đó qua tất cả level khác baseline, các chiều còn lại giữ nguyên baseline. Tổng số ứng viên = tổng (số level − 1) = 2+2+3+2+2+2+4+2 = 19.
3. Loại ứng viên vi phạm smart_pct >= 0.15. Đúng MỘT ứng viên vi phạm: base_pct = 0.70 với opportunity_pct baseline 0.20 cho smart_pct = 0.10. Số OFAT hợp lệ = 18. Ứng viên bị loại được ghi vào manifest metadata và KHÔNG BAO GIỜ nằm trong denominator.
4. Sinh đúng 200 config interaction duy nhất bằng constrained maximin Latin-hypercube / stratified sampling trên tám chiều, master_seed = 42. Chiều rời rạc được snap về level hợp lệ và cân bằng. Cặp base/opportunity dùng rejection sampling cho tới khi smart_pct >= 0.15. Score weights lấy từ năm tuple đã đăng ký trước. smart_unlock_mode cân bằng qua ba nhóm.
5. Khử trùng lặp với baseline và với OFAT. Nếu sau khử trùng lặp còn dưới 200, tiếp tục sinh tất định trên cùng luồng RNG cho tới khi đủ đúng 200 config duy nhất và hợp lệ.
6. Đóng băng manifest có thứ tự ra CSV/JSON và hash trước khi chạy official run.

```
Denominator kỳ vọng = 1 baseline + 18 OFAT hợp lệ + 200 interaction = 219 config
```

Implementation phải TÍNH và báo cáo số lượng thực tế từ manifest đã đóng băng, không hard-code 219. Không được loại bỏ config sau khi đã thấy kết quả.

### 9.2 Gate 2 pass rule

Ngưỡng CỨNG của Gate 2 chỉ áp điều kiện pre-OOS. Lý do: OOS đã là một gate riêng ở §8; nếu buộc mỗi config phải qua OOS thì Gate 2 sẽ đo lại một giai đoạn 20 tháng duy nhất thay vì đo robustness theo tham số, và giai đoạn OOS bị đếm hai lần.

| Chỉ số | PASS | STRONG |
|---|---|---|
| Gate2_PreOOS_PassShare: tỷ lệ config trong manifest thỏa TOÀN BỘ điều kiện pre-OOS của Gate 1 (§7) | >= 75% | >= 80% |
| Gate2_OOS_PassShare: tỷ lệ config có OOS AccumulationEfficiency >= 100% | Báo cáo riêng, không phải ngưỡng cứng | Báo cáo riêng |

Gate2_OOS_PassShare dưới 50% kích hoạt Failure Signal FS-10. Báo cáo cũng phải nêu combined pass share để tham khảo.

## 10. Gate 3 — implementation robustness

Gate 3 giữ cố định strategy parameter ở baseline và CHỈ thay ma sát và hành vi thực thi.

| Friction dimension | Levels và ràng buộc |
|---|---|
| user_delay | 15m / 1h / 4h / 12h |
| funding_policy | ON_DEMAND / BULK_MONTHLY |
| funding_delay | 0 / 15m / 1h / 4h. RÀNG BUỘC: nếu funding_policy = BULK_MONTHLY thì funding_delay BẮT BUỘC = 0. |
| spot_fee | 0 / 0.05% / 0.10% / 0.20% |
| slippage | 0 / 5 / 10 / 20 bps |

### 10.1 Gate 3 manifest

- Realistic baseline: user_delay = 4h; funding_policy = ON_DEMAND; funding_delay = 1h khi FUNDING_REQUIRED; spot_fee = 0.10%; slippage = 5 bps.
- OFAT quanh realistic baseline: user_delay 3 phương án khác; funding_delay dưới ON_DEMAND 3 phương án khác; spot_fee 3; slippage 3; và funding policy đổi MỘT lần dưới dạng cặp ghép (BULK_MONTHLY, funding_delay = 0). Cùng baseline cho 14 config tất định.
- Sinh thêm đúng 100 config ma sát duy nhất bằng constrained stratified sampling, seed = 43. Mọi mẫu BULK bị ép funding_delay = 0; không config BULK + delay > 0 nào được vào manifest.
- Kích thước manifest tất định kỳ vọng = 114 config duy nhất.
- Behavioral local-hour simulation và P2P-unavailable-in-crash báo cáo như stress test riêng, không nằm trong denominator này.

### 10.2 Net Edge và pass rule

```
AccumulationEfficiency = ETH_strategy / ETH_MonthlyDCA x 100
NetEdgePct             = ETH_V2_realistic / ETH_MonthlyDCA - 1
```

Benchmark cho Net Edge là Benchmark A Monthly DCA, dưới CÙNG giả định ma sát áp dụng được cho thực thi spot thông thường. Hiệu ứng của funding policy được so sánh theo cặp ghép khi liên quan.

| Điều kiện | PASS | STRONG |
|---|---|---|
| Realistic baseline: PrimaryMedian NetEdgePct trên 9 window pre-OOS | > 0 | >= +1.5% |
| Realistic baseline: OOS AccumulationEfficiency | >= 100% | >= 102% |
| Tỷ lệ config trong manifest 114 có PrimaryMedian NetEdgePct > 0 | >= 60% | >= 70% |

## 11. Implementation shortfall measurement

Chênh lệch giữa Gate 1 và Gate 3 là chi phí triển khai thực tế. Trước V2.1.4 nó chưa bao giờ có ngưỡng, khiến Failure Signal về ma sát không đánh giá được.

```
ImplementationShortfallPP = Gate1_PrimaryMedian_AE - Gate3_Realistic_PrimaryMedian_AE     [điểm phần trăm]
```

Nếu ImplementationShortfallPP > 3.0 điểm phần trăm, Failure Signal FS-09 = TRUE.

Delta Gate1 -> Gate3 TRỘN ba thứ: manual delay, funding policy/delay, và slippage. Không được gọi toàn bộ delta này là chi phí manual delay.

Bắt buộc attribution riêng bằng paired run: (a) chỉ đổi user_delay; (b) chỉ đổi funding policy/delay; (c) chỉ đổi slippage/fee. Báo cáo ba thành phần riêng biệt.

## 12. Benchmarks and null controls

| ID | Luật chính xác |
|---|---|
| A — Monthly DCA | 100% contribution của tháng, mua vào Day 3 lúc 12:00 local. |
| B — Weekly DCA | Chia contribution tháng thành 4 phần bằng nhau, mua vào Thứ Hai 12:00 local. Thứ Hai thứ năm trong tháng không nhận thêm contribution. |
| C — Simple Dip Reserve | 70% contribution mua cố định hàng tháng; 30% vào reserve. Khi DD365 <= -30%, giải ngân 50% reserve hiện có. Khi DD365 <= -45%, giải ngân 50% reserve còn lại. **[F4] Ngữ nghĩa chu kỳ:** mỗi trigger (-30%, -45%) bắn tối đa MỘT lần trong một chu kỳ; sau khi ít nhất một trigger đã bắn, chu kỳ hiện tại kết thúc và chu kỳ mới bắt đầu (hai trigger được nạp lại) tại daily close đầu tiên có Price >= MA200; reserve không bao giờ âm. |
| D — MA200 DCA | Mỗi tháng contribution C. Nếu tại ngày lịch Price >= MA200: giải ngân 0.70C và cộng 0.30C vào reserve. Nếu Price < MA200: giải ngân C + MIN(0.30C, reserve hiện có), trừ phần thêm khỏi reserve. RESERVE CAP = 6C: nếu sau khi cộng mà reserve vượt 6C, phần vượt được giải ngân ngay trong tháng đó. Không leverage, reserve không âm. |
| E — ETH DCA OS V2.1.5 | Toàn bộ engine. |
| F — Random Timing control | Giữ nguyên tháng, kích thước tranche và profile giải ngân theo tháng của V2; chỉ random hóa timestamp mua trong cùng tháng. N = 1000, seed từ master_seed. Lightweight replay dùng lịch giải ngân đã tính sẵn, KHÔNG chạy lại full engine. |
| G — Random Anchor control | Giữ nguyên toàn bộ luật vốn; random hóa ngày tạo anchor của ladder trong phạm vi tháng cho phép. N = 1000, seeded. Lightweight replay, không tính lại daily indicator. |

Reserve cap của Benchmark D là bắt buộc. Không có trần, reserve phình vô hạn trong thị trường tăng kéo dài và D trở thành đối thủ bù nhìn — điều đó làm vô hiệu nguyên tắc ở §22 rằng benchmark đơn giản hơn thắng nếu kết quả tương đương.

### 12.1 Equal capital rule

- Mọi strategy phải nhận CÙNG cumulative external contribution tại mọi comparison date.
- Tiền mặt chưa đầu tư (USDT hoặc VND) vẫn là một phần của portfolio và không được bỏ qua khi tính giá trị.

### 12.2 Giới hạn diễn giải của Random controls

Control F đo lẫn cả hiệu ứng cơ học của việc điều kiện hóa trên giá đã giảm, chứ không thuần kỹ năng dự báo. Nếu V2 không vượt phân vị P95 của phân phối random, kết luận là chưa có bằng chứng mạnh cho tín hiệu timing. Control G bổ sung bằng cách random hóa điểm neo thay vì thời điểm mua.

## 13. Bootstrap, seeds và số lần chạy

| Thành phần | N | Seed |
|---|---|---|
| Block bootstrap (block length 30 / 60 / 90 ngày) | 1000 mỗi block length | derive từ master_seed |
| Behavioral local-hour simulation | 1000 | derive từ master_seed |
| Random Timing control F | 1000 | derive từ master_seed |
| Random Anchor control G | 1000 | derive từ master_seed |
| Gate 2 LHS sampling | 200 config | master_seed = 42 |
| Gate 3 stratified friction sampling | 100 config | seed = 43 |

```
Stochastic run seed = deterministic_hash(master_seed, run_id, simulation_id)
```

Block bootstrap là chẩn đoán bất định, KHÔNG thay thế các gate cứng trên window không chồng lấn. Không shuffle từng daily return riêng lẻ vì điều đó phá cấu trúc thị trường.

## 14. Walk-forward references

- Development reference: 2019–2021.
- Validation reference: 2022–2023.
- Hard OOS: 2025-01-01 trở đi. BUILD yêu cầu OOS AccumulationEfficiency >= 100%.
- Rolling walk-forward bổ sung: 36 tháng hypothesis/reference + 12 tháng test kế tiếp.
- Các mốc dev/validation là tham chiếu mô tả; ngưỡng cứng chỉ nằm ở §7, §8, §9.2 và §10.2.

## 15. Regime labeling for analysis

| Label | Rule |
|---|---|
| Bull | Price > MA200 VÀ MA200 slope dương |
| Bear | Price < MA200 VÀ MA200 slope âm |
| Sideways / Recovery | Các trường hợp còn lại |
| Crash | CRASH regime của strategy, báo cáo riêng |

Nhãn regime chỉ dùng cho reporting và KHÔNG được feed ngược vào live strategy trừ khi được khai báo tường minh ở một version sau. (Nhãn Bull/Bear ở đây độc lập với nhãn STRESSED của Strategy §17.3 — STRESSED phục vụ phân rã metric theo Market Regime enum, Bull/Bear phục vụ phân rã theo cấu trúc xu hướng.)

## 16. Required metrics

- ETH accumulated; AccumulationEfficiency; average ETH cost USDT; XIRR / money-weighted return.
- Bảng chín window pre-OOS, bốn AnchorSetMedian, PrimaryMedian, PooledMedian (nhãn descriptive), bảng coverage weight.
- OOS 2025+ kèm OOS_Months và cờ SHORT_OOS nếu có.
- Rolling 12/24/36/48M chồng lấn kèm block-bootstrap CI — ghi rõ nhãn DESCRIPTIVE.
- Capital utilization; average và max cash ratio; tổng số lệnh mua.
- Bull / Bear / Sideways và CRASH attribution.
- Missed Opportunity Rate = MissedActions / TriggeredActions.
- ImplementationShortfallPP kèm attribution ba thành phần (§11).
- Manual-delay shortfall và funding-delay shortfall riêng biệt.
- P2P transaction count, tổng chi phí spread P2P, average ticket size — chỉ thuộc VND overlay sensitivity (§2.1).
- Cooldown override count và rate theo NORMAL / STRESSED / CRASH / RECOVERY (STRESSED theo định nghĩa Strategy §17.3).
- Concentration: tính lại AccumulationEfficiency sau khi loại tháng có lợi thế ETH tăng thêm lớn nhất, VÀ sau khi loại quý có lợi thế lớn nhất.
- Redundancy diagnostics: correlation matrix, VIF, ablation, score distribution theo bucket 0-20/20-40/40-60/60-80/80-100 kèm mean, median, std, P10/P25/P75/P90.
- Attribution vốn theo Base / Smart / Opportunity / Crash: ETH tích lũy và giá vào trung bình theo từng nguồn.

## 17. Failure Signals và verdict cap

Với chỉ khoảng ba block dữ liệu độc lập, Failure Signals mang nhiều thông tin hơn chính các Decision Gate, vì chúng chẩn đoán CƠ CHẾ chứ không chỉ đo kết quả.

| ID | Failure Signal |
|---|---|
| FS-01 | V2 tích lũy ít ETH hơn Monthly DCA ở phần lớn gate window. |
| FS-02 | Opportunity reserve thường xuyên chạm cap và nằm im không được dùng. |
| FS-03 | Lợi thế biến mất sau khi loại một tháng HOẶC một quý có đóng góp lớn nhất. |
| FS-04 | Redundancy nghiêm trọng: VIF > 10 ở bất kỳ nhóm nào, hoặc corr sub-factor > 0.85 trên phần lớn lịch sử. |
| FS-05 | Score lưỡng cực: hơn 70% quan sát nằm trong chỉ hai bucket score. |
| FS-06 | Config tham số kề nhau đảo ngược kết luận. |
| FS-07 | Average cash ratio cao nhưng không có accumulation benefit tương ứng. |
| FS-08 | Random Timing hoặc Random Anchor control bao trùm hoặc vượt kết quả của V2 (V2 không vượt P95). |
| FS-09 | ImplementationShortfallPP > 3.0 điểm phần trăm (§11). |
| FS-10 | Gate2_OOS_PassShare < 50% (§9.2). |
| FS-11 | OOS AccumulationEfficiency < 100%. |
| FS-12 | Phần lớn lợi thế tập trung vào một crash hoặc một regime duy nhất. |

**QUY TẮC CHẶN:** nếu Gate 1, Gate 2 và Gate 3 đều PASS nhưng BẤT KỲ Failure Signal nào = TRUE, verdict cuối cùng bị giới hạn ở BUILD WITH MODIFICATIONS. BUILD là không thể khi còn bất kỳ Failure Signal nào TRUE.

## 18. Data gaps

- Nến 15m thiếu: KHÔNG interpolate OHLC để trigger zone; gắn tag EXECUTION_DATA_GAP.
- Base nằm trong khoảng gap: execute ở nến hợp lệ đầu tiên sau gap; gắn tag DELAYED_DATA_FILL (xem Strategy §9 [F3]).
- Indicator daily bắt buộc thiếu: giữ score hợp lệ trước đó tối đa 24h, sau đó đóng băng mọi Smart/Opportunity unlock mới và đánh dấu DEGRADED hoặc INVALID theo Strategy §3.
- Báo cáo: số nến kỳ vọng, số nến thiếu, tỷ lệ thiếu, gap dài nhất, và danh sách gap theo ngày.

## 19. Processing order — bắt buộc, cho mỗi nến 15m

Thứ tự này quyết định kết quả. Mọi implementation phải tuân thủ đúng thứ tự và unit-test được thứ tự đó.

1. Tiến đồng hồ tới nến 15m kế tiếp.
2. Phát hiện accounting month mới.
3. Cho hết hạn các Smart ladder của tháng trước và xử lý đóng sổ cuối tháng.
4. Reset trạng thái Smart HWM / mode theo smart_unlock_mode.
5. Áp dụng monthly contribution.
6. Áp trần Opportunity Fund và overflow phần vượt sang Smart của tháng đó.
7. Reset các bộ đếm theo accounting day nếu đã sang ngày mới (00:00 Asia/Ho_Chi_Minh).
8. Kích hoạt daily score và data-quality snapshot mới nếu nến daily nguồn đã đóng.
9. Xử lý các sự kiện Base theo lịch, bao gồm Base execute sớm.
10. Cập nhật Market Regime và bộ đếm Crash-Exit / Recovery (bao gồm nhãn STRESSED theo Strategy §17.3).
11. Kiểm tra hết hạn cooldown và điều kiện cooldown override.
12. Xử lý các pending action đã tới thời điểm thực thi (user_delay + funding_delay); áp TTL, đánh dấu MISSED nếu quá hạn.
13. Kiểm tra trigger Smart mới (LOW <= zone) và confirmation Opportunity mới (CLOSE <= zone); sắp thứ tự zone theo Strategy §15.1 [F2].
14. Tạo hoặc điều chỉnh reservation, tuân thủ pool availability và max_zones_per_cycle (áp SAU khi đã sắp thứ tự theo §15.1).
15. Giải quyết funding state và execution priority (Base -> Smart -> Opportunity).
16. Thực thi các fill đủ điều kiện tại execution proxy; áp fee và slippage.
17. Cập nhật capital ledger, portfolio và cooldown.
18. Kiểm tra ladder completion, suspension, expiry và bullish invalidation; ghi decision log, purchase log và diagnostic snapshot.

## 20. Reproducibility

- Lưu run_id, strategy_version, backtest_spec_version, strategy_config_hash, execution_config_hash, sensitivity_manifest_hash, dataset_hash, start/end date, master_seed, simulation_seed và code commit nếu có.
- Cùng input phải cho cùng output, bit-for-bit ở mức metric.
- Raw data giữ nguyên bất biến trong /data/raw/; không sửa raw data. Processed data tách riêng.
- Manifest generator được unit-test tách biệt khỏi simulation.

## 21. Test suite

### 21.1 Score và diagnostics

- Biên chuẩn hóa của D, M, P, R, S7, V, W, RP tại các điểm clamp 0 và 1.
- ScoreMultiplier piecewise: khớp chính xác tại anchor 40, 60, 70, 80, 90 và nội suy đúng tại các điểm giữa.
- Allocation Opportunity ladder luôn tổng đúng 100% với mọi t, và bằng 0/15/20/25/40 tại OSCORE <= 70 và 10/15/20/25/30 tại OSCORE >= 80.
- DEGRADED: sub-component thiếu đóng góp đúng 0 và OSCORE KHÔNG bị rescale lên.
- No-lookahead: score của ngày D không dùng bất kỳ dữ liệu nào sau khi nến daily D đóng.

### 21.2 Capital và ladder

- Smart unlock, Opportunity unlock và hysteresis, bao gồm trạng thái hợp lệ ACTIVE với unlock = 0 trong vùng 62–65.
- Ngữ nghĩa HWM, NO_HWM và DECAY_HWM, bao gồm decay 0.10 mỗi 7 ngày với sàn bằng SMART_UNLOCK hiện tại.
- Lịch Base Day 3/13/23; Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và Day 28.
- Opportunity cap và overflow sang Smart; ràng buộc smart_pct >= 0.15.
- Reserve, release, partial fill giữ phần dư ở RESERVED tới hết TTL, không số dư âm, không double reservation.
- Bullish invalidation cần đúng hai daily close liên tiếp; anchor và spacing bất biến.
- Expiry: Smart cuối tháng, Opportunity 90 ngày, Crash suspend rồi cancel sau 72h Recovery.
- Crash eligible-capital snapshot [F5]: đo sau cancel/release, bất biến trong đời Crash ladder.

### 21.3 Execution và regime

- Một, hai và ba zone bị xuyên trong cùng một nến; giới hạn tối đa hai zone mỗi cycle; thứ tự tie-break theo Strategy §15.1 [F2].
- Opportunity cần confirmation bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW.
- Manual delay, funding delay, proxy ban đêm tại 07:00 local, TTL, action MISSED.
- Crash funding unavailable scenario.
- Cooldown và override, bao gồm tần suất override trong CRASH.
- Crash entry qua cả điều kiện 24h và 7D; không entry nếu OSCORE < 75; exit chỉ sau 48h; Recovery 72h; re-entry.
- Chuyển đổi Opportunity ladder sang Crash ladder không tạo double reservation.
- Nhãn STRESSED [F1]: đúng điều kiện, không có hiệu ứng execution.

### 21.4 Accounting và evaluation

- VND -> USDT, weighted USDT cost basis, USDT -> ETH, dual cost basis USDT và VND.
- Data gap và delayed Base fill.
- Manifest Gate 2 tất định: đúng 19 ứng viên OFAT, đúng 1 bị loại, đúng 18 hợp lệ, đúng 200 LHS duy nhất.
- Manifest Gate 3 tất định: đúng 114 config; không tồn tại config BULK_MONTHLY với funding_delay > 0.
- Chọn cửa sổ: đúng chín window pre-OOS theo bốn anchor; không window nào kết thúc sau 2024-12-31; OOS tách hoàn toàn.
- PrimaryMedian tính đúng theo §4.1 và khác PooledMedian khi phân phối lệch.
- Mọi benchmark nhận đúng cùng external contribution schedule.
- Benchmark C: mỗi trigger bắn tối đa một lần mỗi chu kỳ, chu kỳ reset đúng luật [F4].
- Random Timing và Random Anchor tái lập được từ seed.
- Bảng verdict và Failure-signal cap được áp dụng tự động.

## 22. Backtest philosophy

- Bác bỏ trước, chứng minh sau.
- Nếu Simple DCA hoặc một luật dip một dòng cho kết quả tương đương với độ phức tạp thấp hơn nhiều, luật đơn giản thắng.
- Không coi cửa sổ chồng lấn là quan sát độc lập.
- Multi-anchor window là chẩn đoán độ nhạy theo điểm neo, không phải chín mẫu độc lập.
- Không thay đổi ngưỡng gate, phương pháp sinh manifest, ngày split hoặc giả định ma sát sau khi đã thấy kết quả official.
- Nếu V2.1.5 fail, tạo V2.2 thay vì vá tại chỗ.
