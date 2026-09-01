# PH-03 — TRIAGE: phạm vi kế toán của Smart unlock (`smart_reservable`)

Loại: **TRIAGE + ROADMAP IMPACT** — KHÔNG remediation.
Phiên: S003-TRIAGE (sau khi WP-A3 được chủ dự án chấp nhận DONE) · Ngày: 2026-08-24
Source of Truth: **V2.1.5** (Master Index §2 precedence; DEC-006)
Trạng thái repo khi triage: HEAD `308e06e`, working tree sạch, không sửa một dòng mã sản phẩm nào.

---

## 1. Kết luận

**PH-03 = DEFECT.** Không phải hành vi chủ đích.

`smart_reservable` so một đại lượng **theo tháng** với một đại lượng **luỹ kế toàn đời**, nên từ
tháng thứ ba trở đi nó trả về `0` **một cách tất định, vĩnh viễn, không phụ thuộc dữ liệu** —
kể cả khi `SMART_UNLOCK = 1.00`. Hệ quả: cơ chế Smart ladder (Strategy §12) chết lâm sàng, và
một trong tám chiều bắt buộc của Gate 2 (`smart_unlock_mode`, Backtest §9) trở nên **trơ hoàn
toàn** — ba mode HWM / NO_HWM / DECAY_HWM cho kết quả **trùng khít bit-for-bit**.

Finding ID chính thức được cấp: **F-035**.

---

## 2. Requirement canonical bị vi phạm

Truy vết SPEC REQUIREMENT → IMPLEMENTATION → OBSERVED BEHAVIOR → CONSEQUENCE.

### 2.1 Điều khoản quyết định — Data Model §5 `monthly_budgets`

Bản ghi `monthly_budgets` được khoá bằng `month_local` (YYYY-MM), có `status OPEN / CLOSED` và
`opened_at / closed_at`, và **bắt buộc** chứa:

```
| smart_available_vnd / smart_reserved_vnd / smart_deployed_vnd | Bắt buộc |
```

Nghĩa là: trong mô hình kế toán canonical, bộ ba AVAILABLE / RESERVED / **DEPLOYED** của Smart
là đại lượng **thuộc về một accounting month** có vòng đời mở–đóng. Không tồn tại bất kỳ khái
niệm canonical nào tên "smart deployed luỹ kế toàn đời" để đem trừ khỏi unlock.

### 2.2 Các điều khoản củng cố

| Điều khoản | Nội dung | Ý nghĩa cho PH-03 |
|---|---|---|
| ST §4 | `SMART_UNLOCK = CLAMP((OSCORE−35)/35, 0, 1)`; "Unlock là **quyền sử dụng vốn**… Ladder mới quyết định execution" | Unlock áp lên **ngân sách Smart của tháng**; quyền này bị vô hiệu hoá |
| ST §6 | HWM: "peak lớn nhất **trong tháng hiện tại**… **Peak reset khi sang accounting month mới**" | Unlock là khái niệm **theo tháng**, được reset mỗi tháng — implementation có reset peak (`SmartUnlockState.month_reset`) nhưng **không** reset mẫu số đem trừ |
| ST §6 | "Vốn đã execute không bao giờ relock" | Đây là mệnh đề **trong phạm vi một tháng** (chống relock khi unlock tụt trong cùng tháng), không phải giấy phép trừ luỹ kế toàn đời |
| ST §12 | "Allocation tối đa ba tranche: 33/33/34% của phần Smart **THỰC SỰ đã unlock**" | Cơ chế này không còn cơ hội chạy từ tháng 3 |
| ST §10 | Month-End: "**Smart còn lại**…" | §10 là luật xử lý **phần dư** cuối tháng, không phải kênh giải ngân chính |
| ST §6 + BT §9 | "cả ba mode **BẮT BUỘC** nằm trong ablation của Gate 2 và **phải được báo cáo đóng góp riêng** vào accumulation, cash drag và hành vi cuối tháng"; `smart_unlock_mode` là 1 trong 8 chiều bắt buộc của Gate 2 | Không thể thoả: ba mode cho kết quả trùng khít |

### 2.3 Đối chứng nội bộ trong chính codebase

`opportunity_reservable` dùng `fund.total * unlock − fund.reserved − fund.deployed`, trong đó
`fund.total` **cũng là luỹ kế** — Opportunity Fund theo ST §7 là quỹ **xuyên tháng** có cap, nên
cả tử số lẫn mẫu số cùng phạm vi ⇒ **đúng**. `smart_reservable` dùng `month_smart_budget` (theo
tháng) trừ `smart.deployed` (toàn đời) ⇒ **lệch phạm vi**. Sự bất đối xứng này giữa hai hàm
liền kề trong cùng một file là bằng chứng nội tại rằng đây là lỗi, không phải thiết kế.

### 2.4 Trả lời câu hỏi triage bắt buộc

> `pool.deployed` có ý nghĩa (A) deployed trong tháng hiện tại, hay (B) cumulative deployed lifetime?

**Theo implementation: (B) — cumulative lifetime.** `Pool` (`capital.py:18-40`) không có bất kỳ
đường reset nào; `grep` toàn repo cho thấy chỉ `SmartUnlockState.month_reset` (reset *peak*) và
`BaseScheduleState.month_reset` (reset *ngân sách Base*) tồn tại — **không có** `Pool.month_reset`.
Ba pool `base_pool, smart_pool, opp_fund` được tạo **một lần** cho cả run (`engine.py:132`).

**Theo canonical accounting model: phải là (A)** cho mục đích đo unlock — vì DM §5 định nghĩa
`smart_deployed_vnd` là trường của bản ghi **tháng**.

⇒ Việc `smart_reservable` trừ giá trị (B) khỏi một tử số theo tháng ở những tháng tiếp theo là
**SAI**.

---

## 3. Root cause

```
month_smart_budget  = br["smart"] + br["opportunity_overflow_to_smart"]   # engine.py:300 — RESET MỖI THÁNG
        │
        ├─ engine.py:499  unlocked = smart_reservable(smart_pool, month_smart_budget, eff_smart_unlock)
        └─ engine.py:408  smart_avail = smart_reservable(smart_pool, month_smart_budget, eff_smart_unlock)
                                                          │
                                                          └─ capital.py:184-185
                                                             unlocked = budget_total * effective_unlock      # ≤ ngân sách 1 THÁNG
                                                             return max(0.0, min(smart.available,
                                                                        unlocked - smart.reserved
                                                                                 - smart.deployed))          # LUỸ KẾ TOÀN ĐỜI
```

Vòng lặp đóng kín gây bóp vốn vĩnh viễn:

1. ST §10 Month-End giải ngân **hết** phần Smart còn lại mỗi tháng (`settle_month_end_smart`).
2. ⇒ `smart_pool.deployed` tăng ≈ một ngân sách tháng **mỗi tháng**, không bao giờ giảm.
3. ⇒ Từ tháng thứ 3, `deployed_luỹ_kế ≥ 2 × ngân_sách_tháng > unlocked_tối_đa`.
4. ⇒ `smart_reservable = 0` với **mọi** giá trị OSCORE, **mọi** mode unlock, **mọi** dataset.
5. ⇒ Không tạo được Smart ladder ⇒ toàn bộ Smart lại chảy qua Month-End ⇒ quay lại bước 2.

---

## 4. Bằng chứng

Mức: **E1** (chạy thật trong phiên triage) + **E2 kế thừa** (reviewer độc lập E2-WP-A3-001 đã xác
nhận độc lập cơ chế và hiện tượng tại S003) + **E1 kế thừa** (quan sát gốc S003).
Script probe nằm ngoài repo (scratchpad); mọi output then chốt được trích nguyên văn dưới đây.

### 4.1 Chứng minh cấu trúc — số học thuần, dùng chính hàm sản phẩm

Mô phỏng đúng luật ST §10 (mỗi tháng: contribute ngân sách tháng, cuối tháng giải ngân hết phần
còn lại), hỏi `smart_reservable` ở **unlock TỐI ĐA = 1.00**:

```
  tháng 1: budget_tháng=30.0 unlock=1.00 unlocked=30.0 | available=30.0 deployed(lifetime)=  0.0 -> smart_reservable=30.000
  tháng 2: budget_tháng=30.0 unlock=1.00 unlocked=30.0 | available=30.0 deployed(lifetime)= 30.0 -> smart_reservable= 0.000
  tháng 3: budget_tháng=30.0 unlock=1.00 unlocked=30.0 | available=30.0 deployed(lifetime)= 60.0 -> smart_reservable= 0.000
  tháng 4: budget_tháng=30.0 unlock=1.00 unlocked=30.0 | available=30.0 deployed(lifetime)= 90.0 -> smart_reservable= 0.000
  tháng 5: budget_tháng=30.0 unlock=1.00 unlocked=30.0 | available=30.0 deployed(lifetime)=120.0 -> smart_reservable= 0.000
```

Đây **không phải hiện tượng phụ thuộc dữ liệu**: ngay cả trong kịch bản thuận lợi nhất có thể
(OSCORE cao nhất, vốn khả dụng đầy đủ), hàm vẫn trả 0 từ tháng thứ hai sau khi tháng đầu đóng sổ.

### 4.2 Quan sát trên dữ liệu tổng hợp (90 tháng, 2019-01 → 2026-06, baseline + GATE1_LOW_FRICTION)

| Đại lượng | Giá trị quan sát |
|---|---|
| Số Smart ladder tạo được / 90 tháng | **2** |
| Ladder #1 | 2019-01-04, eligible = 0.6962 (**2.32%** ngân sách tháng) |
| Ladder #2 | 2019-02-21, eligible = 1.3670 (**4.56%** ngân sách tháng) |
| Thời điểm bắt đầu bị bóp vốn | **tháng 2 (một phần)**; **từ tháng 3 trở đi: tuyệt đối và vĩnh viễn** |
| Số lần gọi `smart_reservable` | 135.251 |
| Số lần trả về 0 | **135.249 (99,9985%)** |
| Ví dụ lần gọi thuận lợi nhất sau đó | `deployed_life≈220, unlock=0.975, unlocked=48.76, available=50.00` → **reservable = 0.0000** |
| SMART giải ngân **qua ladder** (ST §12) | **0,9106** đơn vị danh nghĩa |
| SMART giải ngân **qua Month-End** (ST §10) | **4.369,09** đơn vị danh nghĩa |
| Tỷ lệ đi qua ladder | **0,0208%** |

Nói cách khác: **99,98% vốn Smart bỏ qua cơ chế ladder được đặc tả và chảy qua luật xử lý phần
dư cuối tháng.**

### 4.3 Hệ quả nghiêm trọng nhất — chiều `smart_unlock_mode` của Gate 2 bị trơ

Chạy cùng dataset/cửa sổ, chỉ đổi `smart_unlock_mode`:

```
  HWM        eth_total=21.480751489892  delta_vs_HWM=+0.000000000000  purchases=392  smart_via_ladder=0.9106
  NO_HWM     eth_total=21.480751489892  delta_vs_HWM=+0.000000000000  purchases=392  smart_via_ladder=0.9106
  DECAY_HWM  eth_total=21.480751489892  delta_vs_HWM=+0.000000000000  purchases=392  smart_via_ladder=0.9106
```

Ba mode **trùng khít bit-for-bit**. Nguyên nhân: `eff_smart_unlock` chỉ được tiêu thụ tại đúng
hai lời gọi `smart_reservable` — mà cả hai đều bị kẹp về 0.

Vi phạm trực tiếp:
- **ST §6**: "cả ba mode BẮT BUỘC nằm trong ablation của Gate 2 và **phải được báo cáo đóng góp
  riêng** vào accumulation, cash drag và hành vi cuối tháng" → không thể báo cáo đóng góp riêng
  của thứ không có đóng góp phân biệt được.
- **BT §9**: `smart_unlock_mode` là **1 trong 8 chiều bắt buộc**; nó đóng góp **2 trong 19 ứng
  viên OFAT** và được "cân bằng qua ba nhóm" trong 200 config LHS. Với PH-03, 2 ứng viên OFAT đó
  **trùng kết quả với baseline**, và việc cân bằng LHS qua ba nhóm mode là vô nghĩa.
- ⇒ `Gate2_PreOOS_PassShare` (ngưỡng cứng ≥ 75%) sẽ được tính trên một manifest có một chiều
  chứng minh được là trơ. Đây không phải sai số; đây là **đo robustness trên một chiều không tồn
  tại**.

### 4.4 PH-03 che khuất chính remediation của WP-A3

Tổng snapshot eligible capital [F5] của Crash ladder trên cùng run: **111,13**. WP-A3 đã nâng con
số này từ 99,30 → 111,13 (+11,9%) khi bỏ daily limit khỏi snapshot (F-021). Nhưng thành phần
Smart của snapshot ([F5] = Smart AVAILABLE + Opportunity AVAILABLE) **cũng đi qua
`smart_reservable`** (`engine.py:408`) nên **bằng 0 từ tháng 3**. Trong probe độ nhạy (§4.5),
tổng snapshot là **505,10**.

⇒ WP-A3 vẫn đúng và vẫn cần thiết, nhưng **độ lớn tác dụng thật của nó đang bị PH-03 che khuất
khoảng 78%**. Điều này KHÔNG làm sai bất kỳ evidence nào của WP-A3 (các check A3-05/A3-06 chạy
trên kịch bản tháng đầu, nơi PH-03 chưa cắn), nhưng có nghĩa là **con số impact ở tầng run của
WP-A3 sẽ đổi lần nữa sau khi F-035 được sửa** — đúng như DEC-009 dự liệu.

### 4.5 Probe độ nhạy — CHỈ để ước lượng bậc độ lớn

> **CẢNH BÁO GIỚI HẠN.** Đây **không phải** thiết kế remediation được phê duyệt, không phải bản
> vá, và không được coi là dự báo kết quả sau khi sửa. Đây là một biến thể chạy tại runtime
> ngoài repo (`deployed` tính từ mốc contribution của tháng hiện hành) chỉ nhằm trả lời câu hỏi
> "sai lệch này ở bậc độ lớn nào". Số liệu chạy trên **dữ liệu tổng hợp** — theo **DEC-003**,
> tuyệt đối không dùng để tuyên bố chiến lược có edge.

| Metric | As-is (defect) | Probe phạm vi-tháng | Ý nghĩa |
|---|---|---|---|
| Smart ladder tạo được | 2 | 67 | cơ chế ST §12 sống lại |
| SMART qua ladder | 0,9106 | 945,55 | 0,02% → 22,1% |
| SMART qua Month-End | 4.369,09 | 3.324,09 | kênh dư trở về đúng vai trò |
| Tổng snapshot [F5] Crash | 111,13 | 505,10 | +354% |
| Crash ladder | 10 | 17 | snapshot > 0 nên tạo được ladder |
| Opportunity ladder | 18 | 14 | Smart claim đúng phần của mình |
| Số lệnh mua | 392 | 542 | +38% |
| ETH accumulated | 21,480751 | 21,650668 | **+0,79%** (chỉ là bậc độ lớn) |

---

## 5. FINDING F-035

## F-035 — Smart unlock đo trên ngân sách THÁNG nhưng trừ deployed LUỸ KẾ TOÀN ĐỜI; Smart ladder ngừng hình thành từ tháng thứ ba

**Severity:** **HIGH**
(theo `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`: "HIGH = Material risk requiring priority
remediation". Không phải CRITICAL vì không có mất/lộ dữ liệu, không có phá huỷ dữ liệu, không có
production compromise — công cụ chưa vận hành thật. Nhưng ở mức HIGH cao nhất trong nhóm: nó vô
hiệu hoá một cơ chế chiến lược bắt buộc **và** một chiều gate bắt buộc.)

**Category:** Business Logic / Data (accounting model)

**Status:** OPEN

**Evidence Level:** **E1** (chứng minh cấu trúc + quan sát chạy thật trong phiên triage);
E2 kế thừa: reviewer độc lập E2-WP-A3-001 đã xác nhận cơ chế và hiện tượng độc lập tại S003.

**Affected Area:**
- `src/eth_dca_os/capital.py:179-185` — `smart_reservable` (nguồn gốc)
- `src/eth_dca_os/engine.py:499` — tạo Smart ladder
- `src/eth_dca_os/engine.py:408` — snapshot eligible capital [F5] của Crash ladder
- `src/eth_dca_os/capital.py:18-40` — `Pool` không có vòng đời theo tháng (DM §5)

**Expected Behavior:** Phần Smart có thể reserve thêm trong tháng M =
`ngân_sách_Smart(M) × effective_unlock − (Smart reserved trong M) − (Smart deployed trong M)`,
kẹp trên bởi `available` — với cả ba số hạng cùng phạm vi **tháng M** (DM §5; ST §4, §6, §12).

**Current Behavior:** Tử số theo tháng, hai số hạng trừ theo luỹ kế toàn đời ⇒ trả 0 tất định từ
tháng thứ ba trở đi ở **mọi** OSCORE và **mọi** mode unlock.

**Behavioral Consequence:**
1. Smart ladder (ST §12) không hình thành từ tháng 3 — 99,98% vốn Smart chảy qua Month-End (ST §10).
2. Chiều `smart_unlock_mode` của Gate 2 (BT §9) trơ hoàn toàn — ba mode trùng khít bit-for-bit;
   ST §6 ("báo cáo đóng góp riêng") không thể thoả.
3. Snapshot eligible capital [F5] của Crash ladder bị triệt tiêu phần Smart từ tháng 3 (che
   khuất ~78% tác dụng của remediation F-021 vừa hoàn tất ở WP-A3).
4. Cấu trúc thực thi của chiến lược bị đẩy về gần **Benchmark A (Monthly DCA)** cho toàn bộ 30%
   Smart: một lệnh gộp cuối tháng thay vì ladder mua theo nhịp giảm giá.
5. Capital utilization, cash ratio, số lệnh mua, ETH accumulated đều sai lệch (probe: +0,79% ETH).

**Whether official backtest can be trusted before remediation:** **KHÔNG.**
- Gate 1 (BT §7) đo AccumulationEfficiency trên một engine mà cơ chế Smart ladder — 30% vốn —
  không hoạt động ⇒ thứ được đo **không phải chiến lược được đặc tả**.
- Gate 2 (BT §9, §9.2) tính `Gate2_PreOOS_PassShare` trên manifest có một trong tám chiều bắt
  buộc chứng minh được là trơ.
- Gate 3 (BT §10.2) đo NetEdge trên cùng engine đó.
- BT §22 ("luật đơn giản thắng nếu tương đương") trở nên vô nghĩa khi bản thân chiến lược đã bị
  thoái hoá về gần luật đơn giản: so sánh sẽ **thiên lệch chống lại** chiến lược. Chiều thiên
  lệch bảo thủ **không** làm cho kết quả hợp lệ — verdict dù thuận hay nghịch đều không truy được
  về hypothesis V2.1.5.
- Master Index §6 cấm chạy lại official run để "làm đẹp" kết quả ⇒ lần chạy đầu tiên phải đúng.

**Risk:** RSK-010 (nâng cấp từ nghi vấn thành xác nhận).

**Remediation boundary (KHÔNG thực hiện trong triage này):**
- Bắt buộc: đưa hai vế của phép trừ về **cùng một phạm vi kế toán**, theo đúng DM §5.
- Tồn tại **hai ranh giới ứng viên**, và việc chọn là **quyết định thiết kế của task remediation**
  (cần ghi thành quyết định/ADR, không được chọn im lặng):
  - **PA-A:** đưa vòng đời tháng vào tầng kế toán — theo dõi `smart_reserved/deployed` **theo
    accounting month** đúng như DM §5 mô tả (`monthly_budgets`, `status OPEN/CLOSED`). Bám sát
    canonical nhất, nhưng chạm cấu trúc `Pool`/`MonthlyCapital`.
  - **PA-B:** giữ `Pool` luỹ kế và đổi tử số thành **ngân sách Smart luỹ kế**, để cả hai vế cùng
    là luỹ kế. Thay đổi nhỏ hơn, nhưng làm ngữ nghĩa "unlock theo tháng" (ST §6) trở nên gián
    tiếp và cần chứng minh tương đương ở mọi tháng.
- Ràng buộc bắt buộc cho mọi phương án: không được đổi công thức `SMART_UNLOCK` (ST §4), không
  đổi ngưỡng, không đổi luật Month-End (ST §10), không sửa spec để khớp code (Master Index §6).
- Phải giữ nguyên bất biến DM §14 (`TOTAL = A + R + D`, không double reservation, không âm).
- Phải chứng minh chiều `smart_unlock_mode` **hết trơ** (ba mode cho kết quả phân biệt được) —
  đây là bài kiểm tra sống/chết trực tiếp cho requirement ST §6 + BT §9.

**Ghi chú tương thích ngược:** `tests/test_capital.py::test_smart_reservable_no_relock` dùng
khung **một tháng** (`budget_total=100`, pool contribute 100) nên **đúng với cả hai phạm vi** —
remediation **không cần** nới lỏng hay sửa test hiện có này. Không có test nào trong repo khoá
chặt hành vi luỹ kế xuyên tháng.

---

## 6. Xác nhận phạm vi phát sinh và quan hệ với WP-A3

- Hành vi này **có trước WP-A3**: probe cho kết quả giống hệt trên cả commit trước remediation
  (`5645a74`) lẫn sau (`308e06e`) — S003 đã ghi nhận và reviewer E2 đã xác nhận độc lập.
  **F-035 không phải hồi quy của WP-A3.**
- **Không nhét ngược vào WP-A3.** WP-A3 đã DONE với Completion Gate FROZEN; không sửa gate đó,
  không mở lại task đó. Mọi evidence của WP-A3 vẫn đứng vững (các check chạy trên kịch bản tháng
  đầu, nơi PH-03 chưa có hiệu lực).
- Vì sao S001 không bắt được: S001 là audit **đối chiếu code với spec theo từng điều khoản**,
  còn F-035 chỉ lộ ra khi **chạy nhiều tháng liên tiếp và đếm số ladder** — đúng loại defect
  "sai âm thầm" mà Impl Plan §7 cảnh báo. Đây là bài học độ phủ, không phải lỗi của S001.

---

## 7. Ảnh hưởng Gate (DEC-009)

Remediation F-035 chắc chắn thay đổi: capital allocation, Smart ladder creation, execution count,
deployed capital, ETH accumulated ⇒ **chắc chắn ảnh hưởng Gate 1**, và ảnh hưởng ngữ nghĩa
manifest Gate 2.

Áp dụng **DEC-009**: mọi kết quả Gate 1 tạo trước remediation F-035 phải coi là
**STALE / INVALIDATED**.

**Trạng thái hiện tại: `no current result to invalidate`** — repo chưa từng có official run
(`results/` không tồn tại, BLK-001 vẫn mở; xác nhận lại tại phiên này). Vì vậy DEC-009 áp dụng
**theo hướng phòng ngừa**: dependency phải bảo đảm F-035 được đóng **trước T-06**, để official
run đầu tiên không sinh ra kết quả đã chết yểu.

---

## 8. Phân lớp roadmap — chứng minh bằng dependency

**Kết luận: LỚP A — MUST FIX BEFORE OFFICIAL RUN.** Không mặc định theo thiên hướng của chủ dự
án; chứng minh:

1. **Chặn tính hợp lệ của T-06 trực tiếp.** F-035 làm một trong tám chiều bắt buộc của Gate 2
   trơ (BT §9) và làm 30% vốn không đi qua cơ chế được đặc tả (ST §12). Chạy T-06 trước khi sửa
   tạo ra verdict không truy được về hypothesis V2.1.5.
2. **Master Index §6 khoá một chiều.** Không được chạy lại official run để sửa kết quả ⇒ chất
   lượng lần chạy đầu là điều kiện tiên quyết, không phải tối ưu hoá về sau.
3. **Chặn tính đúng của WP-A5.** WP-A5 (đo Failure Signal) đã được T-04 đặt phụ thuộc WP-A3 vì
   "đo trên một engine còn khoá vốn sẽ cho số sai lệch". F-035 khoá vốn Smart theo một cách khác
   nhưng cùng bản chất, và trực tiếp bóp méo `avg_cash_ratio` (FS-07) và cấu trúc cap-hit
   (FS-02). Cùng lập luận ⇒ cùng kết luận.
4. **Chặn WP-C4.** Nguyên tắc đã được T-04 ghi: "không khoá parity vào hành vi sắp đổi".
5. **Không thuộc lớp B/C/D.** Không phải chính sách verdict (B), không phải productization (C),
   và không thể defer (D) vì nó nằm trên đường đi tới T-06.

---

## 9. Ownership — đề xuất work package mới

**Đề xuất: tạo work package mới `WP-A7`** (nội dung chi tiết ở
`PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md`). Lý do không dùng phương án khác:

| Phương án | Đánh giá |
|---|---|
| Nhét vào WP-A3 | **Bị loại.** WP-A3 đã DONE, gate FROZEN. Governance cấm sửa gate đã đóng băng và cấm mở lại task đã hoàn tất để hấp thụ finding mới |
| Mở rộng WP-A4 | **Bị loại.** WP-A4 sở hữu ngữ nghĩa dữ liệu xấu (ST §3, BT §18); F-035 là kế toán vốn (DM §5, ST §4/§6/§12). Khác requirement, khác file gốc (`score.py` vs `capital.py`). Mở rộng sẽ phải sửa Completion Gate đã FROZEN |
| Mở rộng WP-A6 | **Bị loại.** WP-A6 sở hữu **thứ tự** 18 bước (BT §19), không sở hữu **số tiền** được tính ở bước 14. Gate cũng đã FROZEN |
| **Work package mới WP-A7** | **Chọn.** Ownership sạch, gate soạn mới và đóng băng trước khi thực thi, không đụng gate đã đóng băng nào. Đúng tiền lệ RCP-001 |

Routing tính bằng `routing_engine.py` (không chọn bằng cảm tính), inputs D3 R4 B3 A3 X3 /
U3 V4 H3 C3 F4, category `accounting_financial`:

```
model_score 3.25 → Tier D (Fable)   floors: cognitive:A>=3&X>=3, safety_business:min_C
effort_score 3.45 → max             floors: safety_business:min_high
```

---

## 10. WP-A4 có bị chặn không?

**WP-A4 MAY PROCEED IN PARALLEL** — kèm hai điều kiện bắt buộc.

| Tiêu chí | Đánh giá |
|---|---|
| **Shared files** | Có giao `engine.py`, nhưng khác vùng: WP-A4 sửa cổng data-quality + gắn tag; WP-A7 sửa hàm tính vốn (`capital.py`) và hai lời gọi của nó. WP-A4 còn sở hữu `score.py` mà WP-A7 không chạm. Xung đột là **văn bản/tuần tự**, không phải ngữ nghĩa |
| **Semantic dependency** | **Không có.** Requirement của WP-A4 (ST §3 INVALID, BT §18 tag, [F3] Base delayed fill) không phụ thuộc vào việc reserve được bao nhiêu vốn Smart. Riêng CHECK-A4-05 (Base tranche không bị bỏ) chạy hoàn toàn trên `base_pool` — PH-03 không chạm tới |
| **Test dependency** | **Rủi ro có thật nhưng chặn được.** CHECK-A4-02 ("INVALID chặn tạo action mới") nếu viết trên kịch bản nhiều tháng sẽ **rỗng** vì không có Smart ladder nào để chặn — đúng bài học F-E2-01 của S003 |
| **Risk of freezing behavior** | **Thấp.** CHECK-A4-07 đo before/after tại thời điểm thực thi và **chạy lại được**, không đóng băng hằng số vào repo |

**Điều kiện kèm theo (đưa vào phiên WP-A4, không sửa gate đã FROZEN):**
1. Mọi test của WP-A4 phải **assert tiền đề không suy biến** (ví dụ: khẳng định ladder thật sự
   tồn tại / thật sự sẽ được tạo nếu không có INVALID) — kế thừa trực tiếp bài học F-E2-01.
2. Không hard-code giá trị kỳ vọng tuyệt đối về vốn/ETH trên kịch bản nhiều tháng; nếu buộc phải
   có, ghi rõ chúng sẽ đổi sau F-035.
3. **Tuần tự hoá thao tác trên `engine.py`**: không chạy WP-A4 và WP-A7 đồng thời trên cùng cây
   làm việc; gói nào vào sau phải rebase và chạy lại toàn bộ suite.

---

## 11. Các mục giữ nguyên theo chỉ thị

- **PH-01** — giữ ngoài đường găng; không chỉnh biên bản S001 trong phiên này.
- **DEC-005** — giữ PENDING; không chặn lớp A.
- **BLK-001** — giữ nguyên; chỉ chặn T-06 / dữ liệu Binance thật; **không** dùng để chặn triage
  hay remediation F-035 (toàn bộ kiểm chứng F-035 chạy được trên dữ liệu tổng hợp theo DEC-003).

---

## 12. Điều KHÔNG làm trong phiên triage này

Không sửa `capital.py`, không sửa `engine.py`, không sửa test sản phẩm, không đổi spec, không
chạy official backtest, không mở implementation WP-A4, không mở task remediation, không tự mở
phiên tiếp theo. Chỉ tạo/cập nhật artifact governance/review/risk/roadmap-proposal.
