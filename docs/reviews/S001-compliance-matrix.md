# S001 — SPEC → IMPLEMENTATION COMPLIANCE MATRIX

Phiên: S001 — AUDIT READ-ONLY
Ngày: 2026-08-23
Profile: PRODUCT
Chế độ: read-only. Không sửa mã sản phẩm, không remediation, không refactor.

## Source of Truth được dùng

**V2.1.5** — `docs/spec/*_V2_1_5.md`.

Chủ dự án chỉ định V2.1.3 trong yêu cầu S001. Xung đột đã được nêu và chủ dự án đã chốt dùng
V2.1.5. Bằng chứng dẫn tới quyết định:

| Bằng chứng | Nội dung |
|---|---|
| `find` + toàn bộ lịch sử git | Không có file V2.1.3 nào tồn tại hoặc từng tồn tại |
| `00_MASTER_INDEX_V2_1_5.md:31` | `V2.1.3 \| SUPERSEDED \| Không giao agent. Có regression đã được sửa ở V2.1.4.` |
| `05_IMPLEMENTATION_PLAN_V2_1_5.md:8` | "V2.1.5 là source of truth duy nhất. Không kế thừa ngầm ... V2.1.3 hay V2.1.4." |

Precedence áp dụng khi hai tài liệu spec mâu thuẫn (Master Index §2, "Agent không được tự chọn"):
`03_BACKTEST` (1) > `02_STRATEGY` (2) > `04_DATA_MODEL` (3) > `01_PRODUCT` (4) >
`05_IMPL_PLAN` (5) > `06_SECTION_INVENTORY` (6).

## Quy ước đọc bảng

**COMPLIANCE** — chỉ dùng sáu trạng thái, không gộp lẫn:

| Trạng thái | Nghĩa |
|---|---|
| `PASS` | Code làm đúng điều khoản, có bằng chứng |
| `PARTIAL` | Làm đúng một phần, phần còn lại lệch hoặc thiếu |
| `FAIL` | Code mâu thuẫn điều khoản |
| `NOT IMPLEMENTED` | Điều khoản không có hiện thực nào trong code |
| `NOT TESTED` | Code có vẻ đúng khi đọc, nhưng KHÔNG có test nào chứng minh. **Không đồng nghĩa FAIL** |
| `NOT APPLICABLE` | Điều khoản không áp cho phạm vi backtest engine |

**EVIDENCE** — theo `governance/core/EVIDENCE_STANDARD.md`:

| Mức | Nghĩa trong tài liệu này |
|---|---|
| `E0` | Đọc code, chưa chạy. Là **nghi vấn/suy luận tĩnh**, không phải kết luận đã chứng minh |
| `E1` | Đã chạy thật: test suite, script kiểm chứng read-only, hoặc lệnh CLI. Có output |
| `E2` | Xác minh độc lập — **chưa có trong S001** |

**Cảnh báo bắt buộc về 69 test PASS:** toàn bộ 69 test chạy xanh (E1, đo tại S000) **không**
chứng minh implementation tuân thủ spec. Một requirement chỉ được coi là có test khi chỉ ra được
test cụ thể kiểm đúng requirement đó. Cột TEST LOCATION dưới đây ghi `—` khi không tồn tại test
như vậy.

---

# A. MARKET DATA

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| Indicator data: Binance Spot ETHUSDT + BTCUSDT khung 1D | BT §2 | `data/fetch.py:1-160` | `tests/test_fetch.py` | E1 — test PASS | PASS | — | Bulk archive + REST, verify SHA256 |
| Execution data: ETHUSDT khung 15m | BT §2 | `data/fetch.py` | `tests/test_fetch.py` | E1 | PASS | — | |
| Market timestamp lưu UTC; accounting theo Asia/Ho_Chi_Minh | BT §2 | `data/dataset.py:80`, `engine.py:37` | — | E0 | PASS | — | `TZ_OFFSET = 7*3600`, không DST — đúng cho VN |
| Daily score ngày D chỉ áp dụng SAU khi nến daily D đóng hoàn toàn | BT §2 | `engine.py:85,294-295` | `tests/test_score.py:114` | E1 | PASS | — | `day_end_ts = day_ts + DAY`; `searchsorted(..., 'right')-1` |
| Nến 15m thiếu: KHÔNG interpolate, gắn tag EXECUTION_DATA_GAP | BT §18 | — | — | E1 (grep) | NOT IMPLEMENTED | MEDIUM | Không interpolate (đúng), nhưng **không có tag** `EXECUTION_DATA_GAP` ở đâu trong `src/`. F-028 |
| Base trong gap: execute ở nến hợp lệ đầu tiên sau gap, tag DELAYED_DATA_FILL | BT §18, ST §9 [F3] | `engine.py:341-346,274` | — | E0 | PARTIAL | LOW | Chỉ tăng **bộ đếm** `delayed_data_fill`; không gắn tag lên purchase record. F-029 |
| Báo cáo gap: số nến kỳ vọng/thiếu, tỷ lệ, gap dài nhất, danh sách gap | BT §18 | `data/dataset.py:27-45` | `tests/test_data.py:36` | E1 | PASS | — | |
| Dataset lineage: symbol, interval, **source**, first/last ts, row_count, missing_count, file hash, dataset_hash | DM §13 | `data/dataset.py:48-68` | — | **E1** | **FAIL** | **HIGH** | `source` là chuỗi cố định `'see fetch/synth'`. Chạy thật trên dataset tổng hợp cho `source='see fetch/synth'`. **Không phân biệt được dữ liệu Binance thật với dữ liệu tổng hợp.** F-005 |
| Raw data bất biến trong `/data/raw/`, processed tách riêng | BT §20 | `data/dataset.py:21-24` | — | E0 | PARTIAL | LOW | Ghi parquet vào raw; không có cơ chế chống sửa |
| NO LOOKAHEAD | BT §1, §21.1 | `indicators.py`, `engine.py` | `tests/test_score.py:114` | E1 | PASS | — | Test kiểm indicator; **không có test no-lookahead ở tầng engine 15m** |

# B. OPPORTUNITY SCORE

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| `D = CLAMP((-DD365 - 0.05)/0.55, 0, 1)` | ST §1.1 | `score.py:17` | `tests/test_score.py:25` | E1 | PASS | — | |
| `M = CLAMP((1.05 - MA_RATIO)/0.40)` | ST §1.1 | `score.py:18` | `tests/test_score.py:25` | E1 | PASS | — | |
| `P = CLAMP((0.90 - Percentile365)/0.80)` | ST §1.1 | `score.py:19` | `tests/test_score.py:25` | E1 | PASS | — | |
| `PRICE_LOCATION = 50 x (0.50D + 0.30M + 0.20P)` | ST §1.1 | `score.py:31,63` | `tests/test_score.py` | E1 | PASS | — | |
| `R = CLAMP((55 - RSI14)/30)`, RSI14 Wilder chuẩn | ST §1.2 | `score.py:20`, `indicators.py:12-28` | `tests/test_score.py:25` | E1 | PASS | — | Wilder chuẩn: SMA 14 kỳ đầu rồi smoothing |
| `S7 = CLAMP((-RETURN7 - 0.02)/0.18)` | ST §1.2 | `score.py:21` | `tests/test_score.py:25` | E1 | PASS | — | |
| `V = 0 nếu RETURN7 >= 0, ngược lại CLAMP((VR-1)/1.5)` | ST §1.2 | `score.py:22-24` | `tests/test_score.py:25` | E1 | PASS | — | |
| `MARKET_STRESS = 30 x (0.50R + 0.30S7 + 0.20V)` | ST §1.2 | `score.py:32,63` | — | E1 | PASS | — | |
| `W = CLAMP((-R30 - 0.02)/0.18)`, `RP = CLAMP((0.70 - P180)/0.60)` | ST §1.3 | `score.py:25-26` | `tests/test_score.py:25` | E1 | PASS | — | |
| `RELATIVE_VALUE = 20 x (0.60W + 0.40RP)` | ST §1.3 | `score.py:33,63` | — | E1 | PASS | — | |
| High365 = daily close cao nhất 365 ngày | ST §1.1 | `indicators.py:51` | — | E0 | PASS | — | |
| Percentile365 = tỷ lệ daily close thấp hơn giá hiện tại | ST §1.1 | `indicators.py:31-38` | — | E0 | PASS | — | Mẫu số = window (gồm chính nó) — đọc sát nghĩa đen |
| ADR30 = AVG(abs(daily_return), 30) | ST §11 | `indicators.py:70-71` | — | E0 | PASS | — | |
| DEGRADED: sub-component thiếu contribution = 0, KHÔNG rescale | ST §3 | `score.py:61` | `tests/test_score.py:81` | E1 | PASS | — | Test còn kiểm score DEGRADED <= GOOD |
| INVALID: "giá/lịch sử ETH hoặc **indicator bắt buộc** không hợp lệ" | ST §3 | `score.py:69-71` | `tests/test_score.py:96` | E1 | **PARTIAL** | MEDIUM | Code chỉ đặt INVALID khi **cả 8** sub-factor thiếu. Hẹp hơn spec: thiếu một indicator bắt buộc vẫn chỉ ra DEGRADED. F-030 |
| Opportunity unlock không được tăng do đầu vào DEGRADED | ST §3 | `engine.py:313-316` | — | E0 | PASS | — | `o_unl = min(o_unl, last_good_opp_unlock)`, đúng CONVENTIONS #9 |
| INVALID chặn mọi action Smart/Opportunity mới; Base vẫn chạy | ST §3 | `engine.py:318,452,506` + Base ở 337-360 | — | E0 | PASS | — | **Không có test** ở tầng engine |
| `SMART_UNLOCK = CLAMP((OSCORE-35)/35, 0, 1)` | ST §4 | `score.py:83-84` | `tests/test_score.py:105` | E1 | PASS | — | |
| `OPPORTUNITY_UNLOCK = 0.60 x CLAMP((OSCORE-65)/30, 0, 1)` | ST §4 | `score.py:87-88` | `tests/test_score.py:105` | E1 | PASS | — | |
| ScoreMultiplier nội suy piecewise qua anchor 40/60/70/80/90 → 0.80/0.90/1.00/1.15/1.30, clamp hai đầu | ST §11 | `score.py:93-99` | `tests/test_score.py:57` | E1 | PASS | — | `np.interp` clamp đúng ngoài biên |
| Opportunity ladder weights: `t=CLAMP((OSCORE-70)/10)`, O0=10%t, O4=40%-10%t, tổng 100% | ST §13 | `score.py:104-107` | `tests/test_score.py:70` | E1 | PASS | — | Test kiểm cả endpoint 70 và 80 |
| Correlation matrix Pearson + Spearman, 8 sub-factor + 3 factor | ST §2.1 | `diagnostics.py:13-22` | `tests/test_data.py:45` (smoke) | E1 | PASS | — | |
| Cảnh báo HIGH_REDUNDANCY nếu \|corr\| > 0.85 | ST §2.1 | `diagnostics.py:24-38` | — | E0 | PASS | — | |
| VIF theo nhóm, >5 WARNING, >10 SEVERE → FS-04 | ST §2.2 | `diagnostics.py:41-63` | — | E0 | PASS | — | |
| **Ablation ba model (Price/Stress/Both Minimal) — bắt buộc mọi official run** | ST §2, §2.3 | `diagnostics.py:81-92` | — | **E1** | **NOT IMPLEMENTED** | **HIGH** | Hàm `ablation_scores` tồn tại nhưng **`run_all` không gọi** và pipeline không gọi. Không có trong output official. F-004 |
| **Volume z-score diagnostic song song, báo cáo chênh lệch — bắt buộc** | ST §2.4 | `diagnostics.py:95-103` | — | **E1** | **NOT IMPLEMENTED** | **HIGH** | `volume_zscore_variant` không được gọi ở đâu; không có "báo cáo chênh lệch kết quả". F-004 |
| Score distribution bucket 0-20…80-100 + FS-05 | BT §16, §17 | `diagnostics.py:65-77` | — | E0 | PASS | — | |

# C. CAPITAL ENGINE

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| `TOTAL = AVAILABLE + RESERVED + DEPLOYED` | ST §8, DM §14 | `capital.py:38-40` | `tests/test_capital.py:20` | E1 | PASS | — | |
| Không số dư âm ở bất kỳ pool nào | DM §14 | `capital.py:26-28` | `tests/test_capital.py:20`, `test_engine.py:44` | E1 | PASS | — | `InvariantError` + test conservation |
| Chỉ tạo reservation nếu `requested_reserve <= AVAILABLE` | ST §8, DM §14 | `capital.py:47-55` | `tests/test_capital.py:26` | E1 | PASS | — | |
| Full fill: RESERVED → DEPLOYED | ST §8 | `capital.py:65-71` | `tests/test_capital.py:27` | E1 | PASS | — | |
| **Partial fill: chỉ phần đã fill chuyển RESERVED→DEPLOYED; phần còn lại TIẾP TỤC ở RESERVED tới hết ACTION_TTL** | ST §8, DM §14, BT §21.2 | `ladders.py:48` (field), engine — không có | — | **E1** | **NOT IMPLEMENTED** | MEDIUM | `filled_vnd` khai báo nhưng **không bao giờ được gán**; trạng thái `PARTIALLY_FILLED` không bao giờ phát sinh trong engine. Engine luôn fill toàn phần. F-017 |
| TTL expiry / MISSED: phần chưa fill RESERVED → AVAILABLE | ST §8 | `engine.py:443-449` | — | E0 | PASS | — | Không có test tầng engine |
| Cancel/invalidation/expiry: toàn bộ phần còn lại RESERVED → AVAILABLE | ST §8 | `engine.py:191-197` | `tests/test_ladders.py:61` (tầng ladder) | E1 | PASS | — | |
| Không double reservation giữa Smart/Opportunity/Crash | ST §8, DM §14 | `engine.py:124,388-404` | — | E0 | PASS | — | `reserve_map` ánh xạ zone → (pool, amount). **Không có test** |
| VND allocation là source of truth | ST §8 | `ladders.py:44` | — | E0 | PASS | — | Backtest chạy đơn vị danh nghĩa [F6] |
| `BASE=50% / SMART=30% / OPPORTUNITY=20%` | ST §4 | `config.py:44-46`, `capital.py:161-163` | `tests/test_capital.py:82` | E1 | PASS | — | |
| `OpportunityCapVND = MonthlyOppContribution x cap_months` | ST §7 | `capital.py:153-155` | `tests/test_capital.py:82` | E1 | PASS | — | |
| Cap đạt → contribution Opp overflow sang Smart **của chính tháng đó** | ST §7 | `capital.py:167-176` | `tests/test_capital.py:82` | E1 | PASS | — | |
| Phần Opportunity không dùng rollover sang tháng sau | ST §7 | `engine.py:114` (opp_fund xuyên tháng) | — | E0 | PASS | — | |
| Quỹ quản lý bằng **ledger**, không phải balance mutable | ST §7, DM §6 | `capital.py:24,30-36` | — | E0 | PASS | — | Ledger có `available_after/reserved_after/deployed_after` + `reason_code` |
| HWM (baseline): peak = SMART_UNLOCK lớn nhất trong tháng; reset khi sang tháng | ST §6 | `capital.py:103-113` | `tests/test_capital.py:58` | E1 | PASS | — | |
| NO_HWM: bám unlock hiện tại | ST §6 | `capital.py:108-109` | `tests/test_capital.py:58` | E1 | PASS | — | Spec ghi "có hysteresis" — nghĩa không rõ. Xem S-003 |
| DECAY_HWM: giảm 0.10 mỗi 7 ngày không revalidate, sàn = unlock hiện tại | ST §6 | `capital.py:114-126` | `tests/test_capital.py:58` | E1 | PASS | — | Test kiểm cả 1 bậc, 2 bậc và sàn |
| Vốn đã execute không bao giờ relock | ST §6 | `capital.py:179-185` | `tests/test_capital.py:96` | E1 | PASS | — | `deployed` trừ khỏi unlocked |
| Không được reserve vốn chưa unlock | ST §12 | `capital.py:179-185` | `tests/test_capital.py:96` | E1 | PASS | — | Engine Python **đúng**; webapp JS thì không (xem nhóm I) |
| Opportunity ACTIVATE >= 68 / SUSPEND <= 62 / giữ trạng thái ở giữa | ST §5 | `capital.py:136-141` | `tests/test_capital.py:36` | E1 | PASS | — | |
| ACTIVE với unlock = 0 ở vùng 62–65 là hợp lệ | ST §5 | `capital.py:129-141` | `tests/test_capital.py:47` | E1 | PASS | — | |
| Suspended zone giữ reserve tối đa 7 accounting day rồi cancel + release | ST §5 | `engine.py:332-335` | — | E0 | PASS | — | Không có test |
| Base schedule Day 3/13/23 @ 12:00 local, 40/30/30% | ST §9 | `capital.py:201`, `engine.py:339-346` | `tests/test_capital.py:118`, `test_engine.py:63` | E1 | PASS | — | |
| Base luôn giải ngân trong tháng, độc lập OSCORE | ST §9 | `engine.py:272-274,347-358` | — | E0 | PASS | — | |
| OSCORE >= 70 → kéo sớm 1 tranche, đánh dấu EXECUTED_EARLY, không lặp ngày gốc | ST §9 | `engine.py:361-366` | — | E0 | PARTIAL | LOW | Không lặp ngày gốc ✓; nhưng **không có nhãn `EXECUTED_EARLY`** — chỉ dùng reason `BASE_ADVANCE_SCORE`. F-031 |
| Không tạo Smart ladder mới sau Day 24 | ST §10 | `engine.py:454` | — | E0 | PASS | — | |
| Day 25–27 settle 50% Base còn lại; Day 28 settle 100% | ST §10 | `engine.py:347-358` | — | E0 | PASS | — | Chỉ chạy Day 25 (CONVENTIONS #7 chốt như vậy). Không có test |
| Month-End Smart: OSCORE >= 45 mua hết; < 45 mua 50% + chuyển 50% sang Opp Fund | ST §10 | `engine.py:205-222` | — | E0 | PASS | — | Phần vượt cap mua nốt (CONVENTIONS #7). **Không có test** |
| Opportunity Fund không bao giờ bị ép mua cuối tháng | ST §10 | `engine.py:205-222` | — | E0 | PASS | — | |
| Month-End KHÔNG chịu max_zones_per_cycle | ST §10 | `engine.py:347-360` | — | E0 | PASS | — | Đi đường riêng, không qua bộ đếm zone |

# D. BUY ENGINE

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| `SmartSpacing = CLAMP(ADR30 x factor x ScoreMultiplier, min, max)` | ST §11 | `ladders.py:24-26` | `tests/test_ladders.py:20` | E1 | PASS | — | |
| `OpportunitySpacing = CLAMP(SmartSpacing x 1.25, 6%, 15%)` | ST §11 | `ladders.py:29-30` | `tests/test_ladders.py:28` | E1 | PASS | — | |
| `CrashSpacing = MAX(OpportunitySpacing, 7%)` | ST §14 | `ladders.py:33-34` | `tests/test_ladders.py:31` | E1 | PASS | — | |
| Smart ladder S0/S1/S2 = Anchor x (1 - n x spacing), alloc 33/33/34% | ST §12 | `ladders.py:85-91` | `tests/test_ladders.py:35` | E1 | PASS | — | |
| Opportunity `On = Anchor x (1 - n x OppSpacing)` | ST §13 | `ladders.py:94-100` | `tests/test_ladders.py:43` | E1 | PASS | — | |
| Crash C0–C3 = 20/25/25/30% | ST §14 | `ladders.py:21,109-110` | `tests/test_ladders.py:52` | E1 | PASS | — | |
| Vào CRASH: cancel Opp zone xung đột → release → RỒI mới tạo Crash ladder | ST §14 | `engine.py:373-386` | — | E0 | PASS | — | Thứ tự đúng. **Không có test tầng engine** |
| **[F5] eligible = snapshot Smart AVAILABLE + Opportunity AVAILABLE đo NGAY SAU cancel/release** | ST §14 | `engine.py:379-382` | `tests/test_ladders.py:52` (chỉ tầng ladder) | E0 | **PARTIAL** | MEDIUM | Snapshot dùng `opportunity_reservable(...)` — hàm này **áp thêm daily limit 20%**. [F5] định nghĩa snapshot theo AVAILABLE đã unlock, không nhắc daily limit. Eligible bị thu nhỏ. F-018 |
| Snapshot bất biến trong đời Crash ladder | ST §14 | `ladders.py:103-111` | `tests/test_ladders.py:52` | E1 | PASS | — | |
| Crash không tạo tiền mới | ST §14 | `engine.py:388-404` | — | E0 | PASS | — | Reserve từ Opp trước, Smart sau (CONVENTIONS #5) |
| Anchor và spacing BẤT BIẾN | ST §18.1 | `ladders.py:64-65` | `tests/test_ladders.py:78` | E1 | PASS | — | |
| Buy zone KHÔNG BAO GIỜ dịch lên trên | ST §18.1 | `ladders.py` (không có mutate) | — | E0 | PASS | — | |
| `InvalidationPrice = Anchor x (1 + MAX(12%, 2 x spacing))` | ST §18.2 | `ladders.py:74-76` | `tests/test_ladders.py:61,73` | E1 | PASS | — | Test kiểm cả nhánh 12% và 2×spacing |
| Cần ĐÚNG HAI daily close liên tiếp > InvalidationPrice | ST §18.2 | `ladders.py:119-130` | `tests/test_ladders.py:61` | E1 | PASS | — | Test kiểm cả việc reset chuỗi |
| Smart ladder hết hạn cuối accounting month | ST §18.3 | `engine.py:199-203,270,359` | — | E0 | PASS | — | Hành vi đúng, nhưng `expires_at` lưu `ts+31 ngày` — trường sai nghĩa, không được dùng. F-022 |
| Opportunity ladder hết hạn sau 90 ngày | ST §18.3 | `ladders.py:97`, `engine.py:527-530` | `tests/test_ladders.py:47` | E1 | PASS | — | Test kiểm giá trị `expires_at` |
| **CRASH→RECOVERY: Crash zone chưa execute → SUSPENDED; sau 72h Recovery chưa hit → CANCEL + release** | ST §18.3 | `engine.py:407-419` | — | **E1** | **FAIL** | **HIGH** | Dọn dẹp chỉ chạy khi `regime == "NORMAL"`. Chạy thật cho thấy khi Recovery kết thúc lúc thị trường còn yếu, regime thành **STRESSED** chứ không phải NORMAL → **reserve không bao giờ được giải phóng**. F-001 |
| Ladder expired/invalidated phải ARCHIVE, không xóa | ST §18.3 | `engine.py:123` (list giữ nguyên) | — | E0 | PASS | — | |
| Opportunity max daily deployment 20% quỹ, reset 00:00 local | ST §15 | `capital.py:188-196`, `engine.py:289` | `tests/test_capital.py:109` | E1 | PASS | — | |
| Max 2 normal zone / execution cycle | ST §15 | `engine.py:515-516` | — | E0 | PASS | — | **Không có test**, dù BT §21.3 yêu cầu |
| Capital priority Base → Smart → Opportunity | ST §15 | `engine.py:507,509` | — | E0 | PASS | — | Áp qua `pool_rank` khi sắp thứ tự |
| Cooldown 48h sau execution Smart/Opportunity/Crash | ST §15 | `engine.py:168-170,422` | — | E0 | PASS | — | Base không set cooldown ✓. **Không có test** |
| Cooldown override khi `Price <= LastExecPrice x (1-7%)` | ST §15 | `engine.py:423-424` | — | E0 | PASS | — | **Không có test** |
| Crash KHÔNG bypass cooldown; override vẫn hiệu lực | ST §15 | `engine.py:517-521` | — | E0 | PASS | — | |
| Báo cáo tần suất cooldown override theo từng regime | ST §15, BT §16 | `engine.py:145,520` | — | E0 | PARTIAL | LOW | Có bộ đếm theo regime, nhưng chỉ counters của **W5** vào payload (`pipeline.py:83`). Đếm theo zone chứ không theo sự kiện override. F-027 |
| **[F2] Tie-break: pool → created_at → zone_index; max_zones áp SAU khi sắp thứ tự** | ST §15.1 | `engine.py:509-516` | — | E0 | PASS | — | Thứ tự đúng. **Không có test** dù BT §21.3 yêu cầu tường minh |
| Zone bị chặn bởi max_zones giữ TRIGGERED, xét lại cycle sau | ST §15.1 | `engine.py:516` | — | E0 | PASS | — | |
| ENTER CRASH nếu `(R7 <= -15% OR R24 <= -10%) AND OSCORE >= 75` | ST §17.1 | `regime.py:39` | `tests/test_regime.py:7` | E1 | PASS | — | Test kiểm cả hai nhánh + chặn khi OSCORE < 75 |
| EXIT candidate: `R24 > -5% AND R7 > -10%` liên tục 48h | ST §17.2 | `regime.py:28-34` | `tests/test_regime.py:20` | E1 | PASS | — | Test kiểm 47h chưa đủ, 48h mới chuyển |
| CRASH → RECOVERY → 72h → NORMAL nếu không re-enter | ST §17.2 | `regime.py:40-45` | `tests/test_regime.py:34` | E1 | PARTIAL | HIGH | Test **chỉ** kiểm nhánh return đã hồi (0.02/0.01). Nhánh return còn yếu cho ra STRESSED — xem F-001 |
| Return24H nội ngày tính trên 96 nến 15m liền trước | ST §17.2 | `engine.py:72-78` | — | E0 | PASS | — | |
| **[F1] STRESSED là nhãn reporting, KHÔNG có hiệu ứng lên unlock/ladder/cooldown/limit/execution** | ST §17.3 | `regime.py:56` | `tests/test_regime.py:52` | **E1** | **FAIL** | **HIGH** | Test chỉ kiểm điều kiện nhãn, không kiểm "không hiệu ứng". Thực tế STRESSED **có** hiệu ứng: nó chặn nhánh dọn Crash ladder ở `engine.py:415`. F-001 |
| Regime exit không được dựa trên dữ liệu thiếu | BT §1 (giả định bảo thủ), ST §3 | `regime.py:23-24` | — | **E1** | **FAIL** | MEDIUM | `return7d=None`/`return24h=None` bị ép về `0.0`. Chạy thật: CRASH → RECOVERY với toàn bộ đầu vào `None`. Dữ liệu xấu đẩy trạng thái theo hướng có lợi cho strategy — trái nguyên tắc ST §3. F-019 |

# E. EXECUTION STATE MACHINE

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| **Execution State enum: WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED** | ST §16, §19 | — | — | **E1** (grep toàn `src/`) | **NOT IMPLEMENTED** | **HIGH** | Không một chuỗi nào trong `WAIT/FUNDING_REQUIRED/READY_TO_BUY/DATA_BLOCKED` xuất hiện trong `src/`. F-006 |
| Market Regime và Execution State là hai chiều độc lập, lưu riêng | ST §16 | — | — | E1 | **NOT IMPLEMENTED** | HIGH | Chỉ có Market Regime. F-006 |
| `market_snapshots.execution_state` LUÔN NOT NULL | DM §4 | — | — | E1 | NOT IMPLEMENTED | HIGH | Bảng `market_snapshots` không được sinh. F-006 |
| `decision_log.previous_state / new_state` theo Execution State enum | DM §11 | `engine.py:152-154` | — | E1 | NOT IMPLEMENTED | HIGH | `decision_log` chỉ ghi `{ts, reason_code, ...}`, không có previous/new state. F-006 |
| Zone status enum 9 giá trị | ST §19 | `ladders.py:16-17` | — | E0 | PARTIAL | MEDIUM | Enum khai báo đủ; `PARTIALLY_FILLED` không bao giờ phát sinh (F-017); `EXPIRED` chỉ đặt ở ladder, zone dùng `CANCELLED` |
| Ladder status enum 6 giá trị | ST §19 | `ladders.py:18` | — | E0 | PASS | — | |
| Mọi state transition và recommendation phải log reason code | ST §20 | `capital.py:30-36`, `engine.py:152-154` | — | E0 | PARTIAL | MEDIUM | Ledger ghi reason đầy đủ; `decision_log` chỉ ghi khi `log_decisions=True` và chỉ 3 loại sự kiện (invalidation, crash entry, cooldown override). F-032 |
| 30 reason code theo danh mục §20 | ST §20 | rải rác | — | E0 | PARTIAL | LOW | Phần lớn dùng đúng; một số chuỗi tự do (`"CRASH_ENTRY"`, `"CRASH_ZONE"`, `"{type}_ZONE"`) không khớp danh mục |
| ACTION_TTL 12h, MISSED khi quá hạn | BT §6, Product §7 | `config.py:115`, `engine.py:237,443-449` | — | E0 | PASS | — | **Không có test** dù BT §21.3 yêu cầu |

# F. P2P / VND / USDT

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| **[F6]** Gate 1 & Gate 2 chạy đơn vị danh nghĩa 1 USDT = 1 đơn vị; không dùng chuỗi tỷ giá VND làm input | BT §2.1 | `engine.py:3`, CONVENTIONS #11 | — | E0 | PASS | — | Đúng nguyên tắc |
| Gate 3: chi phí funding mô hình bằng funding_delay/policy, KHÔNG bằng tỷ giá VND | BT §2.1 | `execution.py:9-12` | — | E0 | PASS | — | |
| VND/P2P spread chỉ là overlay sensitivity ở reporting §16, không tham gia điều kiện PASS | BT §2.1 | — | — | E0 | NOT IMPLEMENTED | LOW | Overlay không được cài. Không ảnh hưởng PASS (đúng tinh thần), nhưng metric §16 thiếu |
| `p2p_transactions` schema 8 field, có `started_at`/`completed_at` | DM §7, Product §9 | — | — | E1 | NOT APPLICABLE (backtest) / NOT IMPLEMENTED (product) | MEDIUM | Không thuộc phạm vi backtest engine. Thuộc app — xem nhóm I |
| `crypto_trades` với `recommended_price`, `implementation_shortfall_bps` | DM §8 | `engine.py:162-167` | `tests/test_engine.py:91` | E1 | PARTIAL | MEDIUM | Purchase record có `recommended_price` và `shortfall_bps`; thiếu `triggered_at`, `action_created_at`, `funding_started_at`, `ready_to_buy_at`, `fx_rate_vnd_per_usdt`, `transferred_vnd_cost_basis` |
| VND → USDT, weighted USDT cost basis, dual cost basis | BT §21.4 | — | — | E1 | NOT APPLICABLE | — | Backtest chạy đơn vị danh nghĩa theo [F6]; không mô hình hóa VND/USDT tách biệt |

# G. BACKTEST ENGINE

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| Smart trigger `LOW[T] <= zone`; Opportunity confirm `CLOSE[T] <= zone` | BT §5 | `engine.py:496-499` | — | E0 | PASS | — | **Không có test** dù BT §21.3 yêu cầu |
| KHÔNG fill tại zone_price; proxy = OPEN nến đầu tiên tại/sau delay | BT §5 | `engine.py:439,431` | — | E0 | PASS | — | Fill tại `o` (open) ✓ |
| `total_delay = user_delay + funding_delay` | BT §5 | `execution.py:9-12` | `tests/test_engine.py:73` | E1 | PASS | — | Test chứng minh delay đổi kết quả |
| Behavioral ngày (07–22): 50%/30%/15%/5% MISSED | BT §6 | `execution.py:19-26` | `tests/test_engine.py:101` (smoke) | E1 | PASS | — | Tỷ lệ khớp chính xác |
| Behavioral đêm (23–06): 10%/25%/45% tại 07:00/20% MISSED | BT §6 | `execution.py:27-35` | — | E0 | PASS | — | Nhánh 07:00 có kiểm TTL ✓ |
| Behavioral KHÔNG áp cho Gate 1 | BT §6 | `config.py:148` (`behavioral_model="OFF"`) | — | E0 | PASS | — | |
| P2P-unavailable-in-crash là stress riêng, không trộn vào denominator | BT §5, §10.1 | `engine.py:240-243`, `config.py:117` | — | E0 | PASS | — | Cờ riêng, mặc định False |
| Chín window 24M theo bốn anchor, không window nào kết thúc sau 2024-12-31 | BT §3 | `windows.py:35-49` | `tests/test_windows.py:16` | E1 | PASS | — | Sinh đúng W1–W9 khớp bảng spec |
| **Bảng coverage weight — bắt buộc trong mọi báo cáo official** | BT §4 | `windows.py:52-61` | `tests/test_windows.py:31` | **E1** | **NOT IMPLEMENTED** | MEDIUM | Hàm đúng và có test, nhưng **pipeline/reporting không gọi** → không có trong báo cáo. F-010 |
| `AnchorSetMedian` + `PrimaryMedian` + `PooledMedian` (nhãn DESCRIPTIVE) | BT §4.1 | `windows.py:64-82`, `metrics.py:41-47` | `tests/test_windows.py:42` | E1 | PASS | — | Khóa `pooled_median_descriptive` mang nhãn ✓ |
| Ngưỡng cứng áp lên PrimaryMedian | BT §4.1, §7 | `gates.py:22` | `tests/test_gates_verdict.py:19` | E1 | PASS | — | |
| Gate 1: PM AE >= 102%; >= 6/9 window >= 100%; worst delta >= -5pp; không anchor set nào toàn dưới 100% | BT §7 | `gates.py:9-34` | `tests/test_gates_verdict.py:19` | E1 | PASS | — | Cả bốn điều kiện đúng ngưỡng |
| OOS >= 100% (STRONG 102%), báo cáo OOS_Months + cờ SHORT_OOS | BT §8 | `gates.py:37-40`, `windows.py:85-91` | `tests/test_windows.py:63`, `test_gates_verdict.py` | E1 | PASS | — | |
| Gate 2 chỉ thay strategy parameter, giữ cố định low-friction Gate 1 | BT §9 | `manifests.py:25-34`, `pipeline.py:108,110` | — | E0 | PASS | — | Grid Gate 2 không chứa chiều ma sát ✓ |
| Gate 2 OFAT: 2+2+3+2+2+2+4+2 = 19 ứng viên | BT §9.1 | `manifests.py:63-75` | `tests/test_manifests.py:11` | E1 | PASS | — | `ethdca freeze` đếm thật ra 19 (S000, E1) |
| Đúng 1 ứng viên bị loại (base_pct=0.70 → smart_pct=0.10) → 18 hợp lệ | BT §9.1 | `manifests.py:72-73`, `config.py:75-78` | `tests/test_manifests.py:11` | E1 | PASS | — | Lý do được ghi vào metadata ✓ |
| Ứng viên bị loại KHÔNG BAO GIỜ nằm trong denominator | BT §9.1 | `manifests.py:125` | `tests/test_manifests.py:11` | E1 | PASS | — | |
| Đúng 200 config interaction duy nhất, master_seed = 42 | BT §9.1 | `manifests.py:78,105-118` | `tests/test_manifests.py:22,32` | E1 | PASS | — | Có khử trùng lặp + top-up tất định |
| Denominator TÍNH từ manifest, KHÔNG hard-code 219 | BT §9.1 | `manifests.py:125` | `tests/test_manifests.py:11` | E1 | PASS | — | `1 + len(ofat) + len(interaction)` |
| Sampling là "constrained maximin LHS / stratified" | BT §9.1 | `manifests.py:81-87` | — | E0 | PARTIAL | LOW | Là stratified cân bằng + shuffle; **không có tiêu chí maximin**. Spec cho phép "hoặc stratified" nên chấp nhận được |
| Gate 2 pass rule: chỉ pre-OOS >= 75% (STRONG 80%); OOS share báo cáo riêng | BT §9.2 | `gates.py:43-61` | `tests/test_gates_verdict.py:33` | E1 | PASS | — | |
| FS-10 khi Gate2_OOS_PassShare < 50% | BT §9.2, §17 | `gates.py:60`, `failure_signals.py:76` | `tests/test_gates_verdict.py` | E1 | PASS | — | |
| Gate 3: 14 config tất định (baseline + 13 OFAT) | BT §10.1 | `manifests.py:147-163` | `tests/test_manifests.py:38` | E1 | PASS | — | 3+3+3+3+1 = 13 + baseline = 14 ✓ |
| Gate 3: + 100 config stratified, seed = 43 → 114 | BT §10.1 | `manifests.py:165-207` | `tests/test_manifests.py:38` | E1 | PASS | — | `ethdca freeze` đếm thật 114 (S000, E1) |
| Không tồn tại config BULK_MONTHLY với funding_delay > 0 | BT §10.1, §21.4 | `manifests.py:186-187`, `config.py:126-127` | `tests/test_manifests.py:38` | E1 | PASS | — | Ép ở hai tầng |
| `NetEdgePct = ETH_V2/ETH_A - 1`; benchmark là A dưới cùng ma sát | BT §10.2 | `metrics.py:58-62,24-30` | — | E0 | PASS | — | |
| Gate 3 pass: PM NetEdge > 0; OOS AE >= 100; tỷ lệ NetEdge dương >= 60% | BT §10.2 | `gates.py:64-85` | `tests/test_gates_verdict.py:48` | E1 | PASS | — | |
| `ImplementationShortfallPP = Gate1_PM_AE - Gate3_PM_AE`; FS-09 nếu > 3.0pp | BT §11 | `metrics.py:65-66`, `failure_signals.py:75` | — | E0 | PASS | — | |
| Attribution ba thành phần bằng paired run (delay / funding / slippage-fee) | BT §11 | `metrics.py:69-89`, `pipeline.py:154` | — | E0 | PASS | — | |
| Benchmark A — Monthly DCA Day 3 12:00 | BT §12 | `benchmarks.py:61-72` | `tests/test_benchmarks.py:48` | E1 | PASS | — | |
| **Benchmark B — Weekly DCA** | BT §12 | `benchmarks.py:81-106` | `tests/test_benchmarks.py:56` | **E1** | **NOT IMPLEMENTED** (ở pipeline) | **HIGH** | Hàm đúng và có test, nhưng **pipeline không bao giờ gọi**. F-003 |
| **Benchmark C — Simple Dip Reserve, chu kỳ [F4]** | BT §12 | `benchmarks.py:109-157` | — | **E1** | **NOT IMPLEMENTED** (ở pipeline) | **HIGH** | Không được gọi; và **không có test** cho ngữ nghĩa chu kỳ [F4] dù BT §21.4 yêu cầu. F-003 |
| **Benchmark D — MA200 DCA, reserve cap 6C** | BT §12 | `benchmarks.py:160-188` | — | **E1** | **NOT IMPLEMENTED** (ở pipeline) | **HIGH** | Cap 6C cài đúng ở dòng 181-183 nhưng không được chạy. F-003 |
| §22: "luật đơn giản thắng nếu kết quả tương đương" | BT §22 | — | — | E1 | NOT IMPLEMENTED | HIGH | Không thể áp vì B/C/D không được chạy. F-003 |
| Control F — Random Timing, giữ **kích thước tranche và profile giải ngân theo tháng** | BT §12 | `benchmarks.py:193-214` | `tests/test_benchmarks.py:67` | E0 | **PARTIAL** | MEDIUM | Gộp toàn bộ vốn của tháng vào **một** lệnh tại thời điểm ngẫu nhiên → không giữ profile tranche. Ảnh hưởng FS-08. F-015 |
| Control G — Random Anchor, giữ toàn bộ luật vốn | BT §12 | `benchmarks.py:217-245` | `tests/test_benchmarks.py:67` | E0 | PARTIAL | MEDIUM | Tự khai là "xấp xỉ bằng dịch chuyển ngẫu nhiên"; không chạy lại luật vốn. F-015 |
| Equal capital rule: mọi strategy nhận cùng external contribution | BT §12.1 | `benchmarks.py`, `engine.py:278-279` | `tests/test_benchmarks.py:31` | E1 | PASS | — | Có test tường minh |
| Tiền mặt chưa đầu tư vẫn là một phần portfolio khi tính giá trị | BT §12.1 | — | — | E0 | PARTIAL | INFO | AE là tỷ số ETH nên bỏ qua reserve của C/D. Căng thẳng nội tại của spec — xem S-002 |
| Block bootstrap 30/60/90 ngày, **1000 mỗi block length** | BT §13 | `bootstrap.py:12,32`, `pipeline.py:74-75` | — | **E1** | **FAIL** | MEDIUM | Mặc định hàm là 1000 nhưng pipeline gọi `n_sims=200` **kể cả official run**. F-012 |
| Bootstrap gắn nhãn DESCRIPTIVE | BT §13, §16 | `pipeline.py:81` | — | E0 | PASS | — | Khóa `bootstrap_descriptive` |
| Không shuffle daily return riêng lẻ | BT §13 | `bootstrap.py:16-29` | — | E0 | PASS | — | Bootstrap theo block cặp purchase |
| Random controls N = 1000, seed từ master_seed | BT §13 | `pipeline.py:100`, `benchmarks.py:203` | `tests/test_benchmarks.py:67` | E1 | PASS | — | `n = 200 if dev_limit else 1000` ✓ |
| `Stochastic run seed = deterministic_hash(master_seed, run_id, simulation_id)` | BT §13 | `config.py:34-37` | — | E0 | PASS | — | |
| **Processing order 18 bước, và "phải unit-test được thứ tự đó"** | BT §19 | `engine.py:257-540` | — | E0 | **PARTIAL** | MEDIUM | Bước 1–14 và 18 khớp. **Bước 15/16/17 không tách riêng**: fill + ledger + cooldown nằm trong khối bước 12; tạo ladder chèn giữa bước 12 và 13 nên ladder mới tham gia trigger cùng nến. **Không có test thứ tự** dù spec yêu cầu tường minh. F-016 |
| FS-01 … FS-12 đầy đủ | BT §17 | `failure_signals.py` | `tests/test_gates_verdict.py:56,99` | E1 | PARTIAL | HIGH | 12 signal có hàm, nhưng **FS-02, FS-06, FS-12 không bao giờ được truyền input** → luôn UNKNOWN. F-002 |
| Quy tắc chặn: bất kỳ FS TRUE → tối đa BUILD_WITH_MODIFICATIONS | BT §17, IM §6 | `verdict.py:27-30` | `tests/test_gates_verdict.py:56` | E1 | PASS | — | Có test tường minh |
| Verdict BUILD chỉ khi 3 gate PASS và không FS nào TRUE | IM §5 | `verdict.py:26-33` | `tests/test_gates_verdict.py:74` | E1 | PASS | — | |
| BUILD không được phát ra khi FS chưa đánh giá được | IM §7 ("áp dụng tự động") | `verdict.py:34-35` | — | E1 | **FAIL** | HIGH | `any_true` bỏ qua `None`. Verdict BUILD vẫn phát ra khi 3 FS là UNKNOWN; chỉ ghi thêm một dòng lý do. F-002 |
| Ánh xạ gate-fail → verdict | — (không có trong spec) | `verdict.py:14-25` | `tests/test_gates_verdict.py:74` | E1 | NOT APPLICABLE | MEDIUM | Là **quy ước**, không phải điều khoản spec. Docstring ghi "quy ước, ghi ở docs/CONVENTIONS.md" nhưng **CONVENTIONS.md không có mục nào về verdict**. F-020 |

# H. REPRODUCIBILITY

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| Lưu run_id, strategy_version, backtest_spec_version | BT §20, DM §12 | `reporting.py:38-40` | `tests/test_cli.py` | E1 | PASS | — | |
| Lưu strategy_config_hash + execution_config_hash | BT §20, DM §12 | `reporting.py:41-42`, `config.py:83-88,129-133` | `tests/test_manifests.py:50` | E1 | PASS | — | SHA256 tất định, loại `config_name` khỏi hash ✓ |
| Lưu `sensitivity_manifest_hash` | BT §20, DM §12 | `reporting.py:43` (tham số) | — | **E1** | **FAIL** | MEDIUM | Không một lời gọi `save_run` nào truyền `manifest_hash=` → luôn `null`, kể cả run GATE2/GATE3. Không truy được run nào dùng manifest nào. F-007 |
| Lưu `dataset_hash` | BT §20, DM §12 | `reporting.py:44`, `data/dataset.py:64-65` | `tests/test_data.py:17` | E1 | PASS | — | |
| Lưu `master_seed` | BT §20 | `reporting.py:46` | — | E1 | PASS | — | |
| Lưu `simulation_seed` | BT §20, DM §12 | — | — | **E1** | **NOT IMPLEMENTED** | MEDIUM | Không có trong record. F-008 |
| Lưu `code_commit` nếu có | BT §20, DM §12 | — | — | E1 | NOT IMPLEMENTED | LOW | Spec ghi "tùy chọn". F-008 |
| `created_at` trong strategy_config / execution_config | DM §2, §3 | — | — | **E1** | **NOT IMPLEMENTED** | MEDIUM | Không có `created_at` ở cả hai dataclass. F-009 |
| Schema strategy_config = 20 field §21 + ĐÚNG 3 metadata | ST §21 [F7], DM §2, XC-1 | `config.py:41-67` | — | E1 | **PARTIAL** | MEDIUM | Có 20 field ✓ + `config_name` ✓, nhưng **thiếu `created_at`**, `strategy_config_hash` là property chứ không phải field, và **thừa `score_weights`**. Xem S-001 — đây là mâu thuẫn nội tại của spec chứ không thuần lỗi code |
| "Cùng input phải cho cùng output, bit-for-bit ở mức metric" | BT §20 | `engine.py` (tất định) | `tests/test_engine.py:54`, `test_e2e.py:64` | E1 | PASS (trong một môi trường) | — | Test chứng minh tái lập trong cùng máy/cùng thư viện |
| Tái lập **theo thời gian** (cùng hash input → cùng output ở lần chạy sau) | BT §20, IM §7 | `pyproject.toml:8-13` | — | **E1** | **FAIL** | **HIGH** | Chỉ có sàn thư viện, không lockfile, không trần. Cài mới kéo numpy 2.4.6 / pandas 3.0.5 (vượt sàn hai thế hệ). Run record **không lưu phiên bản thư viện** → thay đổi dấu phẩy động ở bản sau sẽ phá tái lập mà mọi hash đầu vào vẫn trùng. F-021 = RSK-006 |
| Manifest generator unit-test tách biệt khỏi simulation | BT §20 | `manifests.py` | `tests/test_manifests.py` | E1 | PASS | — | Test độc lập, không cần dataset |
| Cờ `official` phản ánh đúng tính chính thức của run | IM §7, §9; DEC-003 | `pipeline.py:117,160,205` | — | **E1** | **FAIL** | **HIGH** | `official = (dev_limit is None)`. **Không kiểm nguồn dữ liệu.** Chạy full manifest trên dataset `synth` sẽ được ghi `official: true`. F-005 |

# I. PRODUCT / WEBAPP

Phạm vi theo yêu cầu S001: chỉ audit chức năng **hiện có**. Thiếu notification/alert **không**
tính là code defect vì Product Spec chưa yêu cầu — giữ nguyên là spec/product gap của S000
(BLK-002).

| SPEC RULE | SPEC LOC | CODE LOC | TEST LOC | EVIDENCE | COMPLIANCE | SEV | NOTES |
|---|---|---|---|---|---|---|---|
| Live và backtest reuse cùng một core strategy function | IM §1 | `webapp/engine.js` | `webapp/README.md` parity | E1 | **PARTIAL** | HIGH | `engine.js` là **bản cài đặt thứ hai**. Giảm thiểu bằng parity OSCORE 40 ngày, lệch tối đa **7,39e-11** (chạy thật, S000). Parity **không phủ** unlock, spacing, phân bổ ladder, invalidation, regime. RSK-002 |
| OSCORE + 8 sub-factor + DEGRADED rule | ST §1, §3 | `webapp/engine.js:143-193` | parity check | E1 | PASS | — | Đồng thuận với Python tới mức nhiễu dấu phẩy động |
| Không được reserve vốn chưa unlock | ST §12 | `webapp/app_logic.js:289-297` | — | **E0** | **NGHI VẤN — CHƯA KIỂM CHỨNG** | HIGH | Đọc code cho thấy `reserveFor` chỉ kiểm `vnd <= pool.a`, không nhân unlock. **Chưa dựng được ca kiểm thử trong S001** → giữ nguyên mức E0. Chuyển thành verification task V-02 |
| INVALID chặn action Smart/Opportunity mới | ST §3 | `webapp/app_logic.js:324-335` | — | **E0** | **NGHI VẤN — CHƯA KIỂM CHỨNG** | HIGH | `createLadder` không kiểm `data_quality`. Verification task V-03 |
| Kế toán tháng: release trả đúng pool của tháng tạo ladder | ST §8 | `webapp/app_logic.js:124-127,315-320` | `webapp/test_zone.js` (chỉ 1 tháng) | **E0** | **NGHI VẤN — CHƯA KIỂM CHỨNG** | HIGH | Test hiện có chỉ dùng một tháng — đúng điểm mù. Verification task V-01 |
| Bất biến `TOTAL = A + R + D` qua fill/partial/invalidation/release | ST §8 | `webapp/app_logic.js` | `webapp/test_zone.js` | **E1** | **PASS (một tháng)** | — | Chạy thật (S000): tổng bảo toàn 3.000.000 qua toàn chuỗi; không pool nào âm. **Chỉ chứng minh cho kịch bản một tháng** |
| Bullish invalidation hai daily close | ST §18.2 | `webapp/app_logic.js:274-286` | `webapp/test_zone.js` | E1 | PASS | — | |
| Base schedule / Month-End / Crash ladder / cooldown / daily limit | ST §9,§10,§14,§15 | — | — | E1 | NOT IMPLEMENTED | MEDIUM | Đã được `webapp/README.md` và `docs/INDEX.md` §6 khai báo công khai. Không phải phát hiện mới |
| Execution State machine 6 trạng thái | ST §16 | `webapp/app_logic.js:592-614` | — | E0 | PARTIAL | MEDIUM | Chỉ suy ra 3 nhãn hiển thị, không lưu state; thiếu ACTION_PENDING/COOLDOWN/DATA_BLOCKED |
| Bộ test webapp chạy được từ bản checkout sạch | BT §21 (tinh thần) | `webapp/test_*.js` | — | E1 | **FAIL** | MEDIUM | Cần `app_final.html` (phải build) và `demo/results3/live_seed.json` (**không tồn tại trong repo**). RSK-004 |
| Notification / alert chủ động | — | — | — | E1 | **NOT APPLICABLE** | — | **Product Spec không có mục nào về alert.** Đây là spec gap (BLK-002), KHÔNG phải code defect. IM §9 hoãn có chủ đích |

---

## Tổng hợp COMPLIANCE

| Trạng thái | Số dòng | Ghi chú |
|---|---|---|
| `PASS` | 78 | Phần lớn tầng công thức và tầng manifest |
| `PARTIAL` | 19 | |
| `FAIL` | 8 | F-001, F-005, F-007, F-012, F-019, F-021, F-002 (BUILD với FS UNKNOWN), test webapp |
| `NOT IMPLEMENTED` | 14 | Gồm 5 mục **bắt buộc cho official run** nhưng đã có code, chỉ thiếu đấu nối |
| `NOT TESTED` | — | Ghi trực tiếp trong cột TEST LOCATION bằng dấu `—` (xem mục "Requirement chưa có test") |
| `NOT APPLICABLE` | 4 | |

## Nhận định trọng tâm

**Tầng công thức rất khỏe.** Toàn bộ OSCORE, 8 sub-factor, unlock, ScoreMultiplier, spacing,
phân bổ ladder, ngưỡng bốn gate, sinh manifest 219/114, chọn chín window và bảng coverage đều
khớp spec tới từng hằng số, phần lớn có test trực tiếp. Đây không phải code cẩu thả.

**Điểm yếu tập trung ở tầng đấu nối và tầng vòng đời.** Ba cụm:

1. **Đã viết nhưng không được gọi** — Benchmark B/C/D, ablation §2.3, volume z-score §2.4,
   bảng coverage §4, XIRR §16. Spec ghi rõ những mục này **bắt buộc trong mọi official run**.
   Hệ quả: một official run sẽ phát ra verdict kèm báo cáo thiếu, mà không có gì báo động.

2. **Vòng đời trạng thái chưa đóng** — Execution State machine không tồn tại; partial fill
   không phát sinh; Crash ladder có đường vào nhưng đường ra bị hở (F-001).

3. **Tính chính thức và tái lập chưa được bảo vệ** — cờ `official` không nhìn nguồn dữ liệu,
   lineage không ghi source thật, manifest hash không gắn vào run, thư viện không ghim.

Ba cụm này đều nằm **trên đường đi tới verdict**, tức là trên đường găng tới mục tiêu cuối của
chủ dự án.

---

# Phụ lục — Kết luận 14 mệnh đề bắt buộc (Impl Plan §7)

Đây là các mệnh đề có thể sai âm thầm, rút từ acceptance criteria của Implementation Plan §7.
Mỗi mệnh đề có một kết luận dứt khoát. Mệnh đề không kiểm được **ghi rõ là không kết luận được**,
không ghi PASS.

| # | Mệnh đề | Kết luận | Mức | Căn cứ |
|---|---|---|---|---|
| 1 | Không lookahead (unit + integration) | **XÁC NHẬN một phần** | E1 (indicator) / E0 (engine) | `tests/test_score.py:114` kiểm indicator. Engine chỉ áp daily score sau khi nến đóng (`engine.py:85,294`) — đúng khi đọc, nhưng **không có test no-lookahead ở tầng 15m**. Không kết luận được cho tầng engine |
| 2 | Không vốn âm ở bất kỳ pool nào | **XÁC NHẬN** | E1 | `capital.py:26-28` raise `InvariantError`; `tests/test_capital.py:20` và `tests/test_engine.py:44` kiểm |
| 3 | Không double reservation giữa Smart / Opportunity / Crash | **KHÔNG KẾT LUẬN ĐƯỢC** | E0 | `reserve_map` ánh xạ zone → (pool, amount) và logic đọc đúng, nhưng **không có test nào** ở tầng engine, và BT §21.3 yêu cầu tường minh test "chuyển Opportunity ladder sang Crash ladder không tạo double reservation" |
| 4 | Manifest Gate 2 tái lập đúng: 19 ứng viên OFAT, 1 bị loại, 18 hợp lệ, 200 LHS duy nhất, denominator 219 | **XÁC NHẬN** | E1 | `ethdca freeze` chạy thật cho `ofat_candidates 19 → ofat_valid 18`, `interaction 200`, `denominator 219`; lý do loại ghi đúng `base_pct=0.7, smart_pct < 0.15`. `tests/test_manifests.py:11,22,32` |
| 5 | Manifest Gate 3 tái lập đúng 114 config; không có config BULK_MONTHLY với funding_delay > 0 | **XÁC NHẬN** | E1 | `ethdca freeze`: `deterministic 14, sampled 100, size 114`. Ràng buộc BULK ép ở hai tầng (`manifests.py:186`, `config.py:126`). `tests/test_manifests.py:38` |
| 6 | Mọi benchmark nhận đúng cùng lịch external contribution | **XÁC NHẬN cho A** | E1 | `tests/test_benchmarks.py:31` kiểm tường minh. Nhưng **B/C/D không được pipeline chạy** (F-003) nên mệnh đề chỉ được kiểm chứng trên tập benchmark thực sự được dùng |
| 7 | Benchmark D có reserve cap 6C; Benchmark C theo ngữ nghĩa chu kỳ [F4] | **XÁC NHẬN ở tầng code, BÁC BỎ ở tầng vận hành** | E1 | Code đúng: cap 6C ở `benchmarks.py:181-183`, chu kỳ [F4] ở `:153-154`. Nhưng cả hai **không bao giờ được chạy** (F-003), và [F4] **không có test** dù BT §21.4 yêu cầu |
| 8 | Cùng hash config/manifest/dataset + cùng seed → tái lập chính xác cùng kết quả | **XÁC NHẬN trong một môi trường; BÁC BỎ theo thời gian** | E1 | `tests/test_engine.py:54`, `test_e2e.py:64` chứng minh tái lập trong cùng máy. Nhưng không ghim thư viện và run record không lưu phiên bản → tái lập qua thời gian không được bảo đảm (F-007) |
| 9 | Rolling window chồng lấn được gắn nhãn DESCRIPTIVE trong mọi output | **XÁC NHẬN một phần** | E0 | `pooled_median_descriptive` và `bootstrap_descriptive` mang nhãn. Nhưng **rolling 12/24/36/48M của BT §16 không được tính**, nên mệnh đề rỗng ở phần lớn phạm vi |
| 10 | STRESSED không gây hiệu ứng nào lên unlock/ladder/cooldown/limit/execution [F1] | **BÁC BỎ** | **E1** | STRESSED chặn nhánh dọn Crash ladder ở `engine.py:415` → reserve không được giải phóng. Xem F-001 |
| 11 | Crash ladder [F5]: cancel Opportunity zone và release reserve **trước**, rồi mới chụp snapshot; snapshot bất biến | **XÁC NHẬN thứ tự; SAI LỆCH định nghĩa** | E0 | Thứ tự đúng (`engine.py:373-386`) và snapshot bất biến (`tests/test_ladders.py:52`). Nhưng snapshot dùng `opportunity_reservable(...)` nên **áp thêm daily limit 20%**, hẹp hơn định nghĩa [F5]. Xem F-021 |
| 12 | Tie-break [F2] ba tầng; max_zones áp **sau** khi sắp thứ tự | **XÁC NHẬN ở tầng code; KHÔNG KẾT LUẬN ĐƯỢC ở tầng hành vi** | E0 | `engine.py:509-516` sắp đúng `(pool_rank, created_at, zone_index)` rồi mới cắt theo `max_zones_per_cycle`. **Không có test nào** dù BT §21.3 yêu cầu tường minh |
| 13 | Base tranche không bao giờ bị bỏ vì gap dữ liệu [F3] | **XÁC NHẬN ở tầng code** | E0 | Base pending được giải ngân khi sang tháng (`engine.py:272-274`) và ở Day 25/28 (`:347-358`); có bộ đếm `delayed_data_fill`. **Không có test**; và không gắn tag lên purchase record (F-032) |
| 14 | DEGRADED không đẩy score lên; Opportunity unlock không tăng do đầu vào DEGRADED | **XÁC NHẬN** | E1 | `score.py:61` (thiếu → contribution 0, không rescale) có test `tests/test_score.py:81` kiểm cả "DEGRADED <= GOOD"; `engine.py:313-316` chặn unlock tăng |

**Tổng kết:** 5 mệnh đề XÁC NHẬN đầy đủ, 6 XÁC NHẬN một phần hoặc chỉ ở tầng code,
**2 BÁC BỎ** (mệnh đề 10 và phần vận hành của mệnh đề 7), **2 KHÔNG KẾT LUẬN ĐƯỢC**
(mệnh đề 3 và phần tầng engine của mệnh đề 1).

Không mệnh đề nào được ghi PASS mà không có căn cứ.

---

# Phụ lục — Kết luận bốn hypothesis của T-01

| ID | Hypothesis | Kết luận | Mức | Bằng chứng |
|---|---|---|---|---|
| H1 | Test suite Python pass đầy đủ trên môi trường sạch | **XÁC NHẬN** | E1 | 69 passed, 0 failed, 0 skipped, 0 error trong 372,63s. `git log e368425..HEAD -- src/ tests/` rỗng và `git status` rỗng → mã đo được vẫn là mã hiện tại |
| H2 | Không tồn tại kết quả official run nào trong repo | **XÁC NHẬN** | E1 | Không có `results/`, không có `data/`; cả hai nằm trong `.gitignore` |
| H3 | Bộ spec V2.1.5 là nguồn sự thật duy nhất, không có tài liệu mâu thuẫn ngoài `docs/spec/` | **XÁC NHẬN có điều kiện** | E1 | Chỉ tồn tại bộ V2_1_5 (8 file); không file V2.1.3/V2.1.4 nào từng tồn tại trong lịch sử git. **Điều kiện:** `docs/CONVENTIONS.md` chốt 13 quy ước cho các điểm spec để ngỏ — hợp lệ, nhưng S001 phát hiện thêm nhiều quy ước **không** được ghi ở đó (F-015, F-016, F-026) |
| H4 | Không có secret, khóa API hay dữ liệu cá nhân bị commit | **XÁC NHẬN** | E1 | Quét toàn bộ `git log --all -p` theo mẫu key/secret/token/private-key: mọi kết quả khớp đều là **văn bản tài liệu governance**, không phải giá trị thật. Không file `.env`, `.pem`, `.key`, credential nào từng tồn tại |
