# WP-A7 — Sửa phạm vi kế toán vốn Smart theo tháng

## Metadata
Status:
IN_PROGRESS

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-002):
A — MUST FIX BEFORE OFFICIAL RUN · **nằm trên đường găng**

Completion Gate Freeze:
FROZEN — 2026-08-24 (bước đóng băng gate sau khi RCP-002 được áp dụng)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 4
B: 3
A: 3
X: 3
U: 3
V: 4
H: 3
C: 3
F: 4

Routing Categories:
accounting_financial

Primary Agent Tier:
D

Primary Effort:
max

Model Routing Score:
3.25

Effort Routing Score:
3.45

Applied Model Floor:
cognitive:A>=3&X>=3, safety_business:min_C

Applied Effort Floor:
safety_business:min_high

Routing Warnings:
none

Runtime Supported Effort Levels:
low / medium / high / xhigh / max

Execution Profile:
DEFAULT

Escalation Tier:
D

Escalation Effort:
max

Difficulty:
3/4

Risk:
4/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Đưa kế toán vốn Smart về **đúng phạm vi accounting month** theo mô hình canonical, sao cho
`monthly Smart budget / unlock / available / reserved / deployed` được xử lý theo **tháng kế
toán**, và **vốn đã deployed ở các tháng trước không còn bóp quyền unlock của tháng sau**.

Đây là yêu cầu về **phạm vi kế toán (accounting scope)**, không phải yêu cầu "tăng số Smart
ladder". Số ladder chỉ là **hậu quả quan sát được** của phạm vi sai; nó là triệu chứng, không
phải mục tiêu.

## Root cause (giữ nguyên nguyên văn theo triage — không được làm mờ)

`month_smart_budget × effective_unlock` là đại lượng **theo tháng** (`month_smart_budget` được
gán lại ở mỗi accounting month mới). Nhưng implementation hiện trừ khỏi nó:

```
pool.reserved + pool.deployed        # capital.py:184-185
```

trong đó `pool.deployed` là **cumulative lifetime** — `Pool` không có bất kỳ vòng đời tháng nào
(toàn repo chỉ có `SmartUnlockState.month_reset` reset *peak* và `BaseScheduleState.month_reset`
reset *ngân sách Base*; **không tồn tại** `Pool.month_reset`).

Vì Month-End (ST §10) giải ngân hết phần Smart còn lại mỗi tháng, `pool.deployed` tăng ≈ một
ngân sách tháng mỗi tháng và không bao giờ giảm ⇒ từ tháng thứ ba, `smart_reservable` trả **0
một cách tất định, vĩnh viễn, không phụ thuộc dữ liệu**, kể cả ở `SMART_UNLOCK = 1.00`.

**Cấm diễn giải lại finding thành** "Smart ladder hoạt động ít" hoặc "cần tăng số ladder".

## Requirement canonical

Điều khoản **quyết định** — **Data Model §5 `monthly_budgets`**: bản ghi khoá bằng `month_local`,
có `status OPEN / CLOSED` và `opened_at / closed_at`, **bắt buộc** chứa
`smart_available_vnd / smart_reserved_vnd / smart_deployed_vnd`. Tức bộ ba A/R/D của Smart là
đại lượng **thuộc một accounting month** có vòng đời mở–đóng.

Củng cố (đã kiểm precedence Master Index §2 — **không phát hiện mâu thuẫn**, mọi tầng cùng hướng):

| Tài liệu | Precedence | Nội dung |
|---|---|---|
| **BT §19** bước 3, 4, 6 | **1** | "xử lý **đóng sổ cuối tháng**"; "**Reset** trạng thái Smart HWM / mode"; "overflow phần vượt sang **Smart của tháng đó**" — tài liệu precedence cao nhất coi ngân sách Smart là đại lượng theo tháng |
| **ST §4** | 2 | `SMART_UNLOCK = CLAMP((OSCORE−35)/35, 0, 1)`; "Unlock là **quyền sử dụng vốn**" — quyền áp lên ngân sách Smart của tháng |
| **ST §6** | 2 | HWM: peak "lớn nhất **trong tháng hiện tại**", "**Peak reset khi sang accounting month mới**"; "Vốn đã execute không bao giờ relock" là mệnh đề **trong phạm vi một tháng** |
| **ST §10** | 2 | Month-End xử lý "**Smart còn lại**" — luật xử lý **phần dư của tháng** |
| **ST §12** | 2 | Ladder chia 33/33/34% "phần Smart **THỰC SỰ đã unlock**" |
| **DM §6** | 3 | `capital_ledger` là **audit trail append-only** (`available_after/reserved_after/deployed_after` = Audit; "quản lý bằng ledger, không phải balance mutable") ⇒ lịch sử toàn đời **phải được giữ**, song song với trạng thái theo tháng |
| **DM §14** | 3 | `TOTAL = AVAILABLE + RESERVED + DEPLOYED`; không số dư âm; không double reservation |

**Không phát hiện CONFLICT.** Bốn tầng tài liệu (BT precedence 1, ST 2, DM 3, IM 5) đều nhất
quán: trạng thái kế toán theo tháng và lịch sử audit toàn đời là **hai vai trò khác nhau, cùng
tồn tại**.

## Đóng finding / risk

- **F-035** — Smart unlock đo trên ngân sách THÁNG nhưng trừ deployed LUỸ KẾ TOÀN ĐỜI; Smart
  ladder ngừng hình thành từ tháng thứ ba (severity **HIGH**, evidence E1, xác nhận độc lập kế
  thừa từ reviewer E2-WP-A3-001)
- **RSK-010** — CONFIRMED DEFECT, do gói này sở hữu và sẽ đóng khi gói DONE

Triage đầy đủ: `docs/reviews/PH-03-triage-smart-unlock-scope.md`.
Quyết định roadmap: `PROJECT/ROADMAP_CHANGE_PROPOSAL_002.md` (APPROVED WITH CONDITIONS, applied).

## Vì sao gói này nằm trên đường găng

Ba hệ quả đo được, mỗi hệ quả đủ để chặn official run:

1. **99,98%** vốn Smart bỏ qua cơ chế ladder (ST §12) và chảy qua luật phần dư cuối tháng
   (ST §10) — cấu trúc thực thi bị đẩy về gần Benchmark A cho toàn bộ 30% vốn Smart.
2. **Chiều `smart_unlock_mode` — 1 trong 8 chiều BẮT BUỘC của Gate 2 (BT §9) — trơ hoàn toàn**:
   ba mode HWM / NO_HWM / DECAY_HWM cho `eth_total` trùng khít **bit-for-bit**, trong khi ST §6
   yêu cầu "báo cáo đóng góp riêng" của từng mode. `Gate2_PreOOS_PassShare` (ngưỡng cứng ≥ 75%)
   sẽ được tính trên manifest có một chiều chứng minh được là không tồn tại.
3. Snapshot eligible capital **[F5]** của Crash ladder mất phần Smart từ tháng 3, che khuất ~78%
   tác dụng thật của remediation F-021 vừa hoàn tất ở WP-A3.

Master Index §6 cấm chạy lại official run để làm đẹp kết quả ⇒ lần chạy đầu tiên phải đúng.

## Scope

- `src/eth_dca_os/capital.py` — phạm vi kế toán của Smart (`smart_reservable` và cấu trúc trạng
  thái theo tháng mà nó dựa vào)
- `src/eth_dca_os/engine.py` — **chỉ** phần tích hợp trực tiếp với thay đổi trên: hai lời gọi
  `smart_reservable` (tạo Smart ladder; thành phần Smart của snapshot [F5]) và vòng đời tháng
  (mở/đóng sổ) nếu cần
- `tests/` — test WP-A7 (multi-month, mode divergence, invariants, non-regression)
- `docs/CONVENTIONS.md` — ghi quyết định thiết kế nếu spec để ngỏ chi tiết triển khai

## Out of Scope

- **Opportunity Fund accounting** — quỹ **xuyên tháng** theo ST §7; chỉ được đụng ở mức
  *non-regression check*, không đổi ngữ nghĩa
- Vòng đời Crash / regime — đã đóng ở **WP-A3** (DONE, gate FROZEN)
- Ngữ nghĩa dữ liệu thiếu/hỏng — **WP-A4**
- Thứ tự 18 bước — **WP-A6**
- Chính sách và đo Failure Signal — **WP-A5** / **WP-B1**
- Parity JS/Python — **WP-C4**; `webapp/`; lớp alert
- Official backtest, verdict, gate run
- **Đổi công thức `SMART_UNLOCK`, mọi ngưỡng (ST §4, §21), luật Month-End (ST §10)** — cấm tuyệt
  đối; sửa spec để khớp code cũng bị cấm (Master Index §6)

Không mở rộng scope chỉ vì các vùng trên dùng chung `engine.py`.

## Dependencies
- T-04 (DONE)
- **WP-A3** (DONE) — cùng chạm `engine.py`; vòng đời regime/ladder phải đã chốt trước
- **RCP-002** APPLIED (2026-08-24) — điều kiện tồn tại của gói này

## Blocks
- **WP-A5** — measurement tạo trước khi F-035 được sửa không phải canonical evidence
- **WP-A6** — Completion Gate cuối cùng không được chạy trước khi gói này DONE
- **WP-C4** — không đóng băng parity trên hành vi Smart capital đã xác nhận là sai
- **GATE-A → T-06**

## Parallel-Safe With
- WP-A1, WP-A2, WP-C1, WP-D1, WP-D2
- **WP-A4** — song song **về roadmap** (RCP-002): không có phụ thuộc ngữ nghĩa hai chiều; WP-A4
  sở hữu ST §3 / BT §18 (`score.py`), gói này sở hữu DM §5 / ST §4-§6-§10-§12 (`capital.py`).
  **Ba điều kiện bắt buộc khi chạy song song:**
  1. Thao tác trên `engine.py` phải được **tuần tự hoá khi merge**; bắt buộc **branch
     isolation** — không cho hai agent đồng thời sửa/merge cùng vùng.
  2. Không hard-code kỳ vọng VND/ETH nhiều tháng dựa trên hành vi lỗi F-035.
  3. Fixture của WP-A4 chạm đường Smart phải **assert tiền đề không suy biến**.
  WP-A4 **không** phải dependency ngữ nghĩa của gói này (RCP-002 không quy định vậy).

## Expected Touch Area

Allowed:
- `src/eth_dca_os/capital.py`
- `src/eth_dca_os/engine.py` (chỉ phần tích hợp trực tiếp nêu ở Scope)
- `tests/`
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/score.py`, `verdict.py`, `failure_signals.py`, `gates.py`, `benchmarks.py`,
  `metrics.py`, `windows.py`, `bootstrap.py`, `manifests.py`, `diagnostics.py`, `reporting.py`,
  `pipeline.py`, `regime.py`, `ladders.py`
- `src/eth_dca_os/data/`
- `webapp/` (kể cả `engine.js`), `docs/spec/`
- Test của gói khác — chỉ được **chạy**, không được sửa kỳ vọng

Nếu remediation cần vượt scope: **ESCALATE trước** bằng `SCOPE_CHANGED` +
`COMPLETION GATE CHANGE PROPOSAL`, không tự mở rộng.

## Subtasks
- [x] A7.1 Chốt **quyết định thiết kế** phạm vi kế toán (hai ranh giới ứng viên đã nêu ở triage:
      PA-A đưa vòng đời tháng vào tầng kế toán theo DM §5, hay PA-B đưa tử số về cùng phạm vi
      luỹ kế); ghi quyết định + lý do vào `docs/CONVENTIONS.md`. Không chọn im lặng
      → **chọn PA-A**, ghi tại CONVENTIONS #17 (S004)
- [x] A7.2 Viết test-first bộ A–G (xem Completion Gate CHECK-A7-08) và ghi nhận FAIL trước fix
- [x] A7.3 Cài đặt phạm vi kế toán theo tháng cho Smart, **giữ nguyên** ledger audit toàn đời
- [x] A7.4 Bảo đảm Month-End và ranh giới đóng/mở sổ không để trạng thái tháng cũ chui sang phép
      tính unlock của tháng mới
- [x] A7.5 Dựng kịch bản tất định chứng minh `smart_unlock_mode` không còn trơ
- [x] A7.6 Non-regression Opportunity Fund (cumulative, cap, rollover, overflow)
- [x] A7.7 Chạy regression WP-A3 và toàn bộ suite
- [x] A7.8 Đo impact BEFORE/AFTER trên cùng dataset/seed, quy từng sai lệch về requirement
- [ ] A7.9 Phiên rà soát độc lập E2

## Ready Gate

Use `governance/core/TASK_READY_GATE_STANDARD.md`.

- [x] Objective rõ ràng — phạm vi kế toán theo tháng, không phải "tăng số ladder"
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] **T-04 = DONE** (12/12 REQUIRED check PASS tại S002)
- [x] **RCP-002 = APPLIED** (2026-08-24, APPROVED WITH CONDITIONS)
- [x] **F-035 = CONFIRMED** (triage E1 + xác nhận độc lập kế thừa)
- [x] **RSK-010 = OPEN, ownership = WP-A7**
- [x] **Requirement canonical xác định được và KHÔNG mâu thuẫn** — DM §5 quyết định; BT §19,
      ST §4/§6/§10/§12, DM §6/§14 cùng hướng; kiểm precedence Master Index §2: no conflict
- [x] **WP-A3 = DONE và evidence WP-A3 không cần reopen** — F-035 tồn tại trước WP-A3, làm giảm
      *độ lớn* một số quan sát Smart nhưng không invalidate correctness findings của WP-A3
- [x] **Không dependency bắt buộc nào BLOCKED** — T-04 DONE, WP-A3 DONE; BLK-001 không chặn gói
      này (mọi kiểm chứng chạy trên dữ liệu tổng hợp theo DEC-003)
- [x] **Routing metadata xác nhận lại bằng router hiện hành** — `routing_engine.py`:
      model_score 3.25 → **D (Fable)**, effort_score 3.45 → **max**, floors như trên, warnings none
- [x] **Source file cần remediation thay đổi được trong scope mà không vi phạm Scope Lock** —
      `capital.py` không thuộc Allowed của bất kỳ task nào khác đang mở; Scope Lock của WP-A3/A4
      liệt kê `capital.py` là "do not touch" **cho chính chúng**, không mâu thuẫn với việc gói
      này sở hữu file đó
- [x] Expected touch area được xác định
- [x] Data impact được biết — **gói này làm đổi kết quả mô phỏng**; áp DEC-009 (xem Gate staleness)
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] **Completion Gate được ĐÓNG BĂNG trước khi implementation bắt đầu** — FROZEN 2026-08-24
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — S004 2026-08-24, 20/20 PASS
      (kèm kiểm tra không có push WP-A4 song song trên remote trước khi mở)

## Completion Gate

Use `governance/core/TASK_COMPLETION_GATE_STANDARD.md` and `governance/core/EVIDENCE_STANDARD.md`.

Risk = 4 + category `accounting_financial` → **E1 bắt buộc** cho mọi REQUIRED check kiểm chứng
được, và **E2 bắt buộc** cho CHECK-A7-12 trước khi DONE. **Không được hạ E2.**

Nguyên tắc bằng chứng riêng của gói này:
- "đọc code thấy hợp lý" **không** được dùng làm bằng chứng hoàn thành cho bất kỳ REQUIRED check nào;
- mọi mệnh đề về phạm vi kế toán phải được chứng minh trên **kịch bản nhiều tháng**, không phải
  một tháng rồi suy luận;
- **không** được dùng "ETH tăng nhiều hơn" làm bằng chứng fix đúng.

### Functional / Accounting Scope

#### CHECK-A7-01 — Vốn deployed tháng trước KHÔNG bóp quyền unlock của tháng sau
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test **nhiều tháng** (tối thiểu ba tháng liên tiếp) chứng minh bằng chạy thật:
- **Tháng 1** — Smart được unlock và deploy bình thường; ghi lại `smart_reservable` đầu tháng.
- **Tháng 2** — ngân sách Smart mới + unlock mới; khẳng định phần vốn đã deployed ở tháng 1
  **không** làm giảm quyền unlock của tháng 2. Ca chuẩn: `unlock = 1.00` ⇒ `smart_reservable`
  của tháng 2 phải bằng đúng phần unlocked của ngân sách tháng 2 trừ đi phần đã reserve/deploy
  **trong chính tháng 2**, kẹp trên bởi `available`.
- **Tháng 3 trở đi** — hành vi tiếp tục đúng, không suy biến dần theo số tháng.
Không chấp nhận test một tháng. Đây là check trực tiếp đóng **F-035**.

**Kết quả (S004):**
- `tests/test_wp_a7_monthly_scope.py::test_a` (unit, BA tháng): tháng 1 deploy trọn 30.0
  (reserve→deploy + Month-End); mở sổ tháng 2/3 → `smart_reservable(unlock=1.0)` = **30.0
  đúng ngân sách tháng mới** ở cả tháng 2 và tháng 3, trong khi lifetime deployed bảo toàn
  30.0/60.0. `::test_b` (engine, BỐN tháng liên tiếp oscore 60): 4/4 tháng đều tạo Smart
  ladder, không suy biến theo số tháng.
- BEFORE (HEAD 68bd8be): cùng test FAIL đúng cách — tháng 2+ reservable=0
  (log test-first `FFFFF.FF`; probe cấu trúc: tháng 2→5 đều 0.000 ở unlock 1.00).
- AFTER: 8/8 PASS (`python -m pytest tests/test_wp_a7_monthly_scope.py`).

Status cụ thể: PASS — E1 (pytest chạy thật, FAIL-before/PASS-after).

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-02 — Hành vi tương đương mô hình canonical DM §5 `monthly_budgets`
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh bằng chạy thật rằng trạng thái Smart được scope theo `month_local` với ba
đại lượng `smart_available / smart_reserved / smart_deployed` **của tháng**, và vòng đời tháng có
điểm mở và điểm đóng (tương đương `status OPEN/CLOSED`, `opened_at/closed_at`).
**Không bắt buộc kiến trúc phải trùng tên schema**, nhưng behavior phải tương đương mô hình
canonical. Nếu implementation vẫn giữ một `Pool` cumulative cho mục đích khác (audit/cost basis —
DM §6), phải chứng minh **bằng chạy thật hoặc bằng kiểm tra chương trình** rằng giá trị cumulative
đó **KHÔNG** được dùng sai phạm vi để tính monthly Smart unlock.

**Kết quả (S004):**
- Tương đương hành vi: `Pool` SMART mang bộ đếm THEO THÁNG `month_reserved` (≙
  `smart_reserved_vnd`), `month_deployed` (≙ `smart_deployed_vnd`); phần available của tháng
  = `unlocked − month_reserved − month_deployed` kẹp bởi `available` — đúng bộ ba DM §5.
  Vòng đời tháng có điểm mở/đóng: `open_accounting_month(ts)` tại rollover (ts được lưu ở
  `month_opened_at` ≙ `opened_at`; mở sổ tháng mới đồng nghĩa đóng sổ tháng cũ ≙
  OPEN/CLOSED — engine chỉ có đúng một tháng OPEN tại mọi thời điểm).
- Cumulative không dùng sai phạm vi: kiểm tra chương trình — `smart_reservable`
  (capital.py) sau fix CHỈ đọc `month_reserved`/`month_deployed`, không còn đọc
  `reserved`/`deployed` lifetime; xác nhận bằng chạy thật `::test_a` (lifetime deployed
  30/60 không ảnh hưởng quyền tháng mới) và `::test_f` (ledger lifetime vẫn append-only,
  `ledger_conservation_ok` PASS mọi pool — DM §6 giữ nguyên vai trò audit).
- Bộ đếm tháng reconcile tất định từ ledger + mốc mở sổ (`::test_f` có replayer độc lập
  khớp từng giá trị). Quyết định thiết kế PA-A ghi tại `docs/CONVENTIONS.md` #17.

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-03 — `smart_unlock_mode` không còn mechanically dead
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Bài kiểm tra sống/chết bắt buộc của gói này. Trước remediation, triage đã chứng minh HWM /
NO_HWM / DECAY_HWM cho `eth_total` trùng khít **bit-for-bit** vì Smart ladder bị bóp chết.

Yêu cầu sau remediation: dựng **kịch bản tất định** mà ngữ nghĩa canonical của ba mode (ST §6)
dẫn tới khác biệt **hợp lý** (ví dụ: OSCORE lên đỉnh rồi tụt trong cùng tháng ⇒ HWM giữ peak,
NO_HWM bám unlock hiện tại, DECAY_HWM giảm dần theo `hwm_decay_days`/`hwm_decay_step`), và
chứng minh chiều strategy này **không còn chết cơ học**.

Báo cáo tối thiểu cho từng mode: Smart unlock path; `smart_reservable`; số lượng và giá trị
ladder; Smart deployed; downstream execution nếu có.

**Không** được kiểm bằng "ba mode chạy không crash". **Không** yêu cầu ba mode phải khác nhau về
`eth_total` trên **mọi** dataset — chỉ yêu cầu chứng minh chiều này không còn trơ.

**Kết quả (S004):**
Kịch bản tất định `::test_c` (2 tháng — tháng 2: ladder tạo ở unlock 0.714, bullish
invalidation +13% hai daily close → release, OSCORE tụt 40, 13 ngày để DECAY chạy ≥2 bậc),
chạy engine run thật cho từng mode với unlock path được ghi lại:

| Mode | Smart unlock path (điểm cuối) | `smart_reservable` cuối | Ladder (số/giá trị) | Smart deployed (tháng) | Downstream |
|---|---|---|---|---|---|
| HWM | eff giữ peak **0.714286** (25/35) | **14.357143** | 2 ladder; ladder tháng 2 eligible 30×0.714=21.43, INVALIDATED→release | 7.071429 | không có execution thêm sau release (kịch bản dừng ở quyền vốn) |
| DECAY_HWM | eff tụt bậc 0.10/7 ngày → **0.614286** | **11.357143** | như trên | 7.071429 | như trên |
| NO_HWM | eff bám hiện tại **0.142857** (5/35) | **0.000000** | như trên | 7.071429 | như trên |

Ba mode cho ba unlock path KHÁC NHAU và ba giá trị quyền vốn KHÁC NHAU, đúng thứ tự
semantics ST §6 (HWM > DECAY_HWM > NO_HWM ≥ 0, HWM > 1.0) — chiều không còn chết cơ học.
BEFORE (68bd8be): cùng kịch bản, mọi mode reservable = 0 từ tháng 2 (test FAIL đúng cách);
trên full synth 90 tháng, 3 mode trùng bit-for-bit eth_total 21.480751489892.
Ghi chú trung thực: trên full synth AFTER, 3 mode vẫn trùng `eth_total` ở tầng OUTCOME vì
engine chỉ tiêu thụ eff tại tạo ladder one-shot (peak==current) và crash snapshot
(OSCORE≥75⇒1.0) — ghi nhận **PH-04** (ngoài scope, chờ owner; xem handoff S004). Điều này
không vi phạm câu chữ frozen của check ("không yêu cầu khác nhau về eth_total trên mọi
dataset — chỉ yêu cầu chứng minh chiều này không còn trơ").

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-04 — Ngữ nghĩa reset theo tháng của cả ba unlock mode
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu, chứng minh bằng chạy thật:
- **HWM** — peak reset đúng khi sang accounting month mới (ST §6);
- **NO_HWM** — không mang peak của tháng trước sang tháng mới;
- **DECAY_HWM** — không mang accounting state trái spec qua ranh giới tháng; sàn peak vẫn là
  `SMART_UNLOCK` hiện tại;
- reserved/deployed của tháng trước **không** bóp unlock của tháng mới (liên thông CHECK-A7-01);
- vốn chưa fill / còn lại được xử lý đúng theo Month-End canonical policy (ST §10).

Ràng buộc: **không** được tạo một "reset pool" làm mất lịch sử audit hoặc làm hỏng Opportunity Fund.

**Kết quả (S004):**
- `::test_c2` (month reset, chạy CẢ BA mode): tháng 1 OSCORE 80 (peak cao) 30 ngày; ngày 31
  data quality INVALID chặn tạo ladder sớm; sang tháng 2 OSCORE 45 → ladder tháng 2 eligible
  `30×(10/35)` **cho cả ba mode** — peak 80 của tháng cũ KHÔNG vắt sang (HWM reset đúng;
  NO_HWM không mang peak; DECAY_HWM không mang accounting state; sàn peak = SMART_UNLOCK
  hiện tại). Reset peak dùng `su.month_reset(ts)` sẵn có (ST §6), gọi ngay SAU
  `open_accounting_month` tại rollover.
- reserved/deployed tháng trước không bóp unlock tháng mới: `::test_a`/`::test_a2`
  (liên thông CHECK-A7-01).
- Vốn còn lại xử lý theo Month-End canonical: `::test_e` (ST §10 — xem CHECK-A7-05).
- Không "reset pool" phá audit: `open_accounting_month` không dịch chuyển vốn, không
  ghi/đổi ledger (kiểm tra chương trình — hàm chỉ gán bộ đếm tháng); ledger lifetime
  nguyên vẹn (`::test_f`); Opportunity Fund không đổi (`::test_d`).

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-05 — Tương tác với Month-End Policy và ranh giới đóng/mở sổ
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu, chứng minh bằng chạy thật trên kịch bản bắc qua ít nhất hai ranh giới tháng:
- phần Smart còn lại được xử lý đúng cuối tháng theo ST §10 (OSCORE ≥ 45 mua hết; < 45 mua 50%,
  chuyển 50% sang Opportunity Fund trong giới hạn cap);
- **deployment cuối tháng KHÔNG làm tháng sau mất quyền Smart unlock** — đây chính là vòng lặp
  đóng kín của F-035;
- phần chuyển sang Opportunity Fund vẫn đúng (số tiền, hướng, cap);
- month close/open **không để stale reserved/deployed chui sang phép tính monthly unlock**.

**Kết quả (S004):**
- `::test_e` (bắc qua ranh giới tháng, Day-28 12:00 OSCORE 40 < 45): mua **50%** phần Smart
  còn lại, chuyển **50%** vào Opportunity Fund trong cap (ledger OVERFLOW_OUT/OVERFLOW_IN,
  reason `MONTH_END_SMART`, số tiền hai vế khớp nhau); tháng kế tiếp vẫn tạo ladder với
  quyền đầy đủ `30×(25/35)`=21.4286 — **deployment cuối tháng không làm tháng sau mất quyền
  unlock** (đóng đúng vòng lặp F-035). Nhánh OSCORE ≥ 45 (mua hết) phủ trong `::test_a`/
  `::test_b` (mỗi tháng deploy trọn ngân sách qua Month-End mà tháng sau vẫn đủ quyền).
- Stale reserve tại ranh giới: `::test_f` — crash zone giữ vốn SMART vắt tháng trở thành
  `carry_reserved` tại mở sổ; carry **không ăn và không trả** quyền unlock tháng mới
  (quy tắc carry-first, CONVENTIONS #17); release/deploy carry rút carry trước, không làm
  âm/đội `month_reserved`. Không phát hiện đường rò stale nào khác (nguồn reserve vắt
  tháng duy nhất là crash zone — Smart ladder luôn hết hạn cuối tháng, ST §18.3).
- Ranh giới đặt đúng BT §19 bước 3→5: settle Month-End (bước 3) → `open_accounting_month`
  + `su.month_reset` (bước 4) → contribution tháng mới (bước 5) — kiểm bằng vị trí hook
  trong `engine.py` + toàn bộ test rollover PASS.

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

### Data Integrity

#### CHECK-A7-06 — Bất biến vốn qua nhiều tháng; lịch sử audit toàn đời được bảo toàn
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: trên kịch bản nhiều tháng (có fill, có cancel, có Month-End, có ranh giới tháng),
khẳng định theo ngữ nghĩa kế toán canonical:
- `TOTAL = AVAILABLE + RESERVED + DEPLOYED` tại **mọi** thời điểm có dịch chuyển vốn (replay
  từng entry ledger, không chỉ kiểm cuối run);
- không số dư âm ở bất kỳ pool nào (DM §14);
- **không double reservation** và **không double deployment**;
- không tạo vốn, không mất vốn (tổng khớp tổng contribution);
- không release về sai pool;
- **KHÔNG reset/xoá ledger hoặc lịch sử cumulative chỉ để test pass**;
- **trạng thái kế toán theo tháng và lịch sử audit toàn đời cùng tồn tại đúng vai trò**
  (DM §5 vs DM §6): sửa F-035 **không** được thực hiện bằng cách xoá/reset lịch sử deployed toàn
  đời nếu lịch sử đó còn cần cho audit hoặc cost basis.

**Kết quả (S004):**
- `::test_f` (3 tháng, có fill, có INVALIDATED→release, có Month-End, có crash vắt ranh
  giới tháng): `ledger_conservation_ok` PASS cho **mọi pool** — replay TỪNG entry ledger
  khẳng định `TOTAL = AVAILABLE + RESERVED + DEPLOYED` tại mọi thời điểm dịch chuyển vốn,
  không số dư âm, `available_after/reserved_after/deployed_after` khớp trạng thái tính lại.
- Không tạo/mất vốn: tổng `pool.total` các pool == tổng contribution danh nghĩa.
- Không double reservation/deployment: bộ đếm tháng của SMART reconcile **tất định** từ
  ledger + mốc mở sổ — replayer độc lập trong test (áp lại đúng quy tắc carry-first trên
  chuỗi entry, mốc mở sổ nhận diện bằng timestamp CONTRIBUTION) khớp từng giá trị
  `month_reserved/month_deployed/carry_reserved`; mọi reserve đều release/deploy về đúng
  pool nguồn theo map (pool, amount) của zone (cơ chế WP-A3 giữ nguyên).
- Lifetime ledger KHÔNG bị xoá/reset ở bất kỳ nhánh code hay test nào: fix chỉ THÊM bộ đếm
  tháng; `reserved/deployed/available/total` lifetime và ledger append-only giữ nguyên
  (diff `capital.py` không đụng `_ledger_append` và các trường lifetime; `::test_a` khẳng
  định lifetime deployed 30/60 tồn tại song song quyền tháng).
- Toàn suite còn `tests/test_capital.py` (invariants sẵn có) PASS không sửa.

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-07 — Opportunity Fund không bị regression sang ngữ nghĩa theo tháng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Opportunity Fund là quỹ **xuyên tháng** (ST §7). Sửa phạm vi kế toán Smart **không** được vô
tình biến kế toán Opportunity thành reset theo tháng.

Yêu cầu, chứng minh bằng chạy thật:
- ngữ nghĩa cumulative của Opportunity Fund giữ nguyên;
- `opportunity_reservable` **không bị thay đổi ngoài requirement** (nếu có thay đổi bất kỳ, phải
  nêu rõ requirement nào bắt buộc và chứng minh không đổi hành vi ngoài phạm vi đó);
- cap `OpportunityCapVND = monthly_opp_contribution × opportunity_cap_months` vẫn đúng;
- rollover / overflow sang Smart **của tháng đó** vẫn đúng (ST §7; BT §19 bước 6);
- daily limit 20% giữ nguyên hành vi đã chốt ở WP-A3 (CONVENTIONS #4).

**Kết quả (S004):**
- Diff `capital.py`: hàm `opportunity_reservable` **không đổi một ký tự** — vẫn lifetime
  semantics trên `fund.total` (ST §7 xuyên tháng); pool OPPORTUNITY **không** được engine
  gọi `open_accounting_month` (bộ đếm tháng của nó đứng yên, không tham gia phép tính nào).
- `::test_d` (guard hai chiều, PASS cả BEFORE lẫn AFTER — 4 tháng): Opportunity Fund
  tích luỹ đúng cumulative qua các tháng; cap 80 = `20 × 4` được tôn trọng; overflow phần
  vượt cap chuyển sang Smart của tháng đó (BT §19 bước 6); `opportunity_reservable` trả
  đúng số học lifetime ở nhiều trạng thái reserved/deployed.
- Daily limit 20%: hành vi WP-A3 (CONVENTIONS #4 — enforce tại bước 14 cho crash zone)
  không đổi — 16/16 test WP-A3 liên quan PASS; impact `daily_limit_blocks` = 0 cả
  BEFORE/AFTER trên cùng dataset.
- Impact toàn kỳ: OPPORTUNITY total giữ 80.0 (cap) cả BEFORE/AFTER; khác biệt duy nhất
  available/deployed (44.41/35.59 → 41.82/38.18) do crash fill dùng nguồn Opportunity
  nhiều hơn — hệ quả [F5] snapshot sống lại, không phải đổi ngữ nghĩa quỹ.

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

### Regression

#### CHECK-A7-08 — Baseline BEFORE được tái tạo; test bắt lỗi FAIL trước fix, PASS sau fix
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu **test-first**. Baseline BEFORE phải được tái tạo từ **code trước remediation** và tối
thiểu tái hiện:
- ở `unlock = 1.00`: **tháng 1** `smart_reservable > 0`; **tháng 2 trở đi** bị bóp về **0** do
  cumulative deployed;
- triệu chứng long-run: Smart ladder gần như không xuất hiện.

Bộ test bắt buộc (viết TRƯỚC khi sửa; báo cáo phải phân biệt rõ **BEFORE = FAIL đúng cách** và
**AFTER = PASS**, khi khả thi theo governance):

| Test | Nội dung |
|---|---|
| **A** | Vốn deployed tháng 1 không bóp unlock tháng 2 |
| **B** | Nhiều tháng: Smart ladder vẫn có khả năng được tạo khi score/unlock cho phép |
| **C** | `smart_unlock_mode` diverge trong kịch bản tất định được dựng có chủ đích |
| **D** | Opportunity Fund vẫn cumulative (không reset theo tháng) |
| **E** | Month-End → tháng kế tiếp: không để trạng thái cũ chui sang unlock mới |
| **F** | Bất biến kế toán qua nhiều tháng |
| **G** | Regression WP-A3 (xem CHECK-A7-10) |

**Kết quả (S004):**
- Baseline BEFORE tái tạo tại HEAD 68bd8be (2026-08-24T03:45Z, log lưu phiên +
  handoff S004): probe cấu trúc dùng hàm thật — unlock=1.00, tháng 1 reservable **30.0**,
  tháng 2→5 **0.000** (lifetime deployed 30→120); trên synth 90 tháng: **2** Smart ladder
  toàn kỳ, 135 249/135 251 lần gọi trả 0, tỷ lệ Smart qua ladder **0.0208%**.
- Test-first: `tests/test_wp_a7_monthly_scope.py` viết TRƯỚC fix; chạy tại 68bd8be:
  **`FFFFF.FF` — 7 FAIL đúng cách + 1 PASS** (test_d là guard Opportunity, phải PASS cả
  hai phía). FAIL messages đúng bản chất từng finding (vd test_a2: "mỗi tháng phải có một
  Smart ladder khi unlock > 0; có 1"; test_b: "assert 1 == 4"). Mapping A–G:
  A=test_a+test_a2 · B=test_b · C=test_c (+test_c2 reset) · D=test_d · E=test_e ·
  F=test_f · G=CHECK-A7-10.
- AFTER: **8/8 PASS** (`python -m pytest tests/test_wp_a7_monthly_scope.py` — 8 passed).

Status cụ thể: PASS — E1 (FAIL-before/PASS-after phân biệt rõ).

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-09 — Thay đổi kết quả mô phỏng được định lượng và quy về requirement
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Gói này **được phép** làm đổi kết quả mô phỏng; nó **không** được phép làm đổi kết quả theo cách
không giải thích được. Yêu cầu: cùng dataset/seed/cửa sổ, đo BEFORE và AFTER, **giải thích từng
sai lệch bằng một điều khoản spec cụ thể**.

Metric tối thiểu: số Smart ladder; `smart_reservable` theo tháng; Smart deployed **qua ladder**;
Smart deployment **qua Month-End**; capital utilization; số lệnh thực thi; ETH accumulated; và
mọi metric trung gian liên quan gate bị ảnh hưởng (tối thiểu tổng snapshot [F5] của Crash ladder,
avg cash ratio).

Ràng buộc: dữ liệu tổng hợp **chỉ** dùng để đo impact — **không tuyên bố strategy có edge**,
không official verdict (DEC-003). Sai lệch không giải thích được ⇒ dấu hiệu defect mới ⇒ dừng.

**Kết quả (S004):**
Cùng dataset/seed/cửa sổ (synth SEED 20260822, 2019-01→2026-06), tool đã commit
`tests/wp_a3_impact_tool.py`; BEFORE = tag `WP_A7_BEFORE` chạy qua git worktree tại
68bd8be với `--src` + assert provenance `code_path`; AFTER = tag `WP_A7_AFTER`.
Metric tối thiểu theo yêu cầu:

| Metric | BEFORE | AFTER | Điều khoản |
|---|---|---|---|
| Smart ladder | 2 | 67 | DM §5 (F-035 fix) → ST §12 sống lại |
| `smart_reservable` theo tháng | 135 249/135 251 lần = 0 | 6/88 lần = 0; mỗi tháng có quyền dương khi unlock > 0 | DM §5 |
| Smart qua ladder / qua Month-End | 0.9106 / 4369.09 (0.0208%) | 1045.97 / 3224.24 (24.49%) | ST §12 vs ST §10 |
| Capital utilization (avg cash ratio) | 0.06826 | 0.06635 | vốn Smart làm việc qua ladder |
| Số lệnh thực thi (executed/purchases) | 36 / 392 | 193 / 543 | hệ quả ladder sống |
| ETH accumulated | 21.480751 | 21.637035 (+0.73%) | HỆ QUẢ — không dùng làm bằng chứng đúng; cùng bậc ước lượng triage +0.79% |
| Tổng snapshot [F5] Crash | 111.13 | 492.07 | ST §14 — thành phần Smart của snapshot sống lại (khuếch đại fix F-021/WP-A3) |
| avg cash ratio | 0.06826 | 0.06635 | như trên |

Bảng truy vết ĐẦY ĐỦ từng sai lệch (crash/opp ladder, releases theo reason,
cooldown_override, final pools, BASE bất biến, state/label transitions bất biến...) —
xem handoff `docs/sessions/S004-wp-a7-monthly-smart-scope.md`, mục "Impact BEFORE →
AFTER"; **mọi dòng khác biệt đều quy về một điều khoản spec cụ thể, không còn sai lệch
không giải thích được**. Dữ liệu tổng hợp chỉ dùng đo impact — không tuyên bố edge,
không verdict (DEC-003; BLK-001 giữ nguyên).

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-10 — WP-A3 không bị regression
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
WP-A3 đã DONE với E2. Gói này **không** được invalidate hành vi đã sửa ở đó. Yêu cầu: chạy lại
đầy đủ bộ test WP-A3 (`tests/test_wp_a3_lifecycle.py`) và khẳng định vẫn PASS, phủ:
vòng đời reserve của Crash ladder; ngữ nghĩa `None`; **[F1]** (STRESSED không hiệu ứng trên năm
bề mặt); **[F5]** (snapshot đúng nghĩa đen, daily limit ở khâu triển khai); pool labeling;
bất biến kế toán đã chứng minh.

Nếu WP-A7 làm FAIL bất kỳ test nào của WP-A3: **WP-A7 không DONE** cho tới khi regression được
giải quyết **đúng requirement**. **Không reopen WP-A3 và không sửa expected value của WP-A3** để
làm test xanh.

**Kết quả (S004):**
- `python -m pytest tests/test_wp_a3_lifecycle.py tests/test_capital.py tests/test_engine.py`
  → **34 passed** — KHÔNG sửa một expected value nào, không reopen WP-A3. Phủ đủ: vòng đời
  reserve Crash ladder, ngữ nghĩa `None`, [F1] năm bề mặt, [F5] snapshot + daily limit tại
  khâu triển khai, pool labeling, bất biến kế toán.
- Bằng chứng độc lập từ impact trên cùng dataset: `state_transitions` và
  `label_transitions` **giống hệt** BEFORE/AFTER (regime layer không bị chạm);
  BASE bất biến hoàn toàn; `daily_limit_blocks`/`missed`/`stuck_crash_reserve` = 0 cả
  hai phía. `crash_snapshots_sum` tăng 111.13→492.07 là hành vi ĐÚNG được khuếch đại
  (thành phần Smart của snapshot [F5] sống lại nhờ F-035 fix — chính là hệ quả mà triage
  dự báo: F-035 che ~78% tác dụng fix F-021), không phải hành vi mới của regime/ladder.

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

#### CHECK-A7-11 — Toàn bộ test suite Python PASS; không test nào bị nới lỏng hoặc skip
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ. Nếu một test hiện có phải sửa vì hành vi đổi, phải nêu rõ test
nào, đổi gì, và **vì sao hành vi mới mới là hành vi đúng theo spec** — kèm điều khoản. Không
skip, không nới lỏng, không xoá test để đạt xanh.

**Kết quả (S004):**
- `python -m pytest` (toàn repo): **95 passed in 354.34s** — 87 test có sẵn (S003 baseline)
  + 8 test WP-A7 mới; 0 failed, 0 skipped, 0 xfail.
- **KHÔNG test hiện có nào phải sửa**: hành vi đổi duy nhất là phạm vi tính
  `smart_reservable`, và test khoá hành vi đó duy nhất
  (`tests/test_capital.py::test_smart_reservable_no_relock`) dùng khung MỘT tháng nên đúng
  với cả hai phạm vi (đã dự báo trong Notes của gate frozen) — pass nguyên trạng.
  Không skip/nới lỏng/xoá test nào.

Status cụ thể: PASS — E1.

Executed By:
Agent phiên S004 (Tier D / max)

Timestamp:
2026-08-24T04:05Z

### Audit độc lập

#### CHECK-A7-12 — Rà soát độc lập E2
Priority:
REQUIRED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
Yêu cầu: phiên reviewer **độc lập** theo "Solo Independent Review Procedure"
(`EVIDENCE_STANDARD.md`), bắt đầu từ **trạng thái repo** (không từ tuyên bố của implementer),
đọc gate đã đóng băng, xem diff thật, và **tự chạy lại** kiểm chứng.

Reviewer phải kiểm độc lập **tối thiểu năm nội dung**:
1. **Monthly scope** — phạm vi kế toán theo tháng thực sự đúng (CHECK-A7-01/02);
2. **Multi-month capital conservation** — bất biến vốn qua nhiều tháng (CHECK-A7-06);
3. **`smart_unlock_mode` no longer dead** — tự dựng hoặc tự kiểm kịch bản divergence (CHECK-A7-03);
4. **Opportunity Fund non-regression** (CHECK-A7-07);
5. **No new capital lock/leak path** — tự tìm ít nhất một kịch bản khoá vốn/rò vốn mới ngoài
   những kịch bản implementer đã thử.

Lưu tại `docs/reviews/` theo `governance/templates/E2_INDEPENDENT_REVIEW_TEMPLATE.md`.
**Không được hạ E2 xuống E1 vì "test đã đủ".** Nếu môi trường không tạo được E2 đúng governance:
gói **không** được DONE; ghi BLOCKED và nêu chính xác thiếu gì.

Executed By:
...

Timestamp:
...

## Gate staleness (DEC-009)

WP-A7 thay đổi hành vi có khả năng ảnh hưởng **capital allocation, Smart ladder creation,
execution behavior, deployed capital, ETH accumulated** ⇒ ảnh hưởng **Gate 1 / Gate 2 / Gate 3**.

Do đó **mọi Gate result sinh trước remediation F-035 phải được coi là STALE / INVALIDATED khi
dùng cho verdict**.

Hiện trạng ghi rõ: **NO CURRENT OFFICIAL RESULT TO INVALIDATE** — repo chưa từng có official run
(`results/` không tồn tại; BLK-001 vẫn mở). Về sau **không** được dùng lại kết quả cũ nếu có.
Dependency bảo đảm: **WP-A7 DONE trước T-06**.

## Exit Criteria
- [ ] 100% REQUIRED checks PASS (12/12)
- [ ] Không REQUIRED check nào ở trạng thái UNKNOWN / NOT_TESTED / BLOCKED
- [ ] Mức evidence được thoả: **E1** toàn bộ; **E2 PASS** cho CHECK-A7-12
- [ ] Full regression PASS (suite Python đầy đủ + bộ test WP-A3)
- [ ] Governance validators PASS
- [ ] Impact BEFORE/AFTER được ghi lại và quy về requirement
- [ ] **F-035 resolved**
- [ ] **RSK-010 đủ điều kiện đóng**
- [ ] Không finding HIGH/CRITICAL mới chưa xử lý **trong phạm vi WP-A7**
- [ ] Không Gate result nào bị dùng lại sai sau quy tắc staleness
- [ ] Quyết định thiết kế phạm vi kế toán được ghi lại (`docs/CONVENTIONS.md`)
- [ ] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-010 cập nhật trạng thái
- [ ] Session handoff được viết
- [ ] Không hạ REQUIRED check nào để đạt DONE

## Escalation Triggers

- Hai phương án thiết kế phạm vi kế toán khác nhau đều không đạt đồng thời DM §5 và bảo toàn
  lịch sử audit DM §6 → `CAPABILITY_CEILING`. Gói đã ở Tier D — khi đó **dừng và trình chủ dự
  án** kèm phân tích, không chồng thêm bản vá.
- Phát hiện mâu thuẫn nội tại của spec về phạm vi kế toán mà precedence không giải quyết được →
  `CONFLICT DETECTED`; nếu là điểm để ngỏ hợp lệ thì ghi `docs/CONVENTIONS.md`; nếu là khiếm
  khuyết đặc tả thì chuyển **WP-D2** (đề xuất V2.2), **không vá V2.1.5**.
- Phải chạm file ngoài Scope Lock (đặc biệt `score.py`, `ladders.py`, `regime.py`, `pipeline.py`)
  → `SCOPE_CHANGED` + `COMPLETION GATE CHANGE PROPOSAL`, trình trước khi sửa.
- Sửa xong nhưng metric đổi theo hướng làm chiến lược trông tốt hơn mà **không giải thích được**
  → DỪNG, không nghiệm thu. Đây đúng loại thiên lệch mà stopping rule tồn tại để chặn.
- Regression WP-A3 fail và cách duy nhất nghĩ ra là sửa expected value của WP-A3 → DỪNG và
  escalate; **cấm** reopen WP-A3.

## Ảnh hưởng nếu gói này thất bại

GATE-A không đóng ⇒ T-06 không mở ⇒ toàn bộ đường tới verdict dừng. WP-A5 sẽ đo trên engine có
phân phối vốn Smart sai (FS-02/FS-07 lệch), WP-A6 sẽ khoá test thứ tự vào các đường xử lý Smart
suy biến, WP-C4 sẽ đóng băng parity trên hành vi sai. Nếu bỏ qua và vẫn chạy official run:
verdict dựa trên engine mà 30% vốn không đi qua cơ chế được đặc tả và một chiều bắt buộc của
Gate 2 bị vô hiệu — và Master Index §6 không cho chạy lại để sửa.

## Changed Files Registry

Created:
- `tests/test_wp_a7_monthly_scope.py` — 8 test A–G test-first
- `docs/sessions/S004-wp-a7-monthly-smart-scope.md` — session handoff
- `docs/reviews/E2-WP-A7-*.md` — (sau phiên E2)

Modified:
- `src/eth_dca_os/capital.py` — Pool: bộ đếm tháng (`month_reserved`, `month_deployed`,
  `carry_reserved`, `month_opened_at`) + `open_accounting_month`; reserve/release/deploy
  cập nhật bộ đếm theo quy tắc carry-first; `smart_reservable` chuyển phạm vi tháng.
  Ledger lifetime và `opportunity_reservable` KHÔNG đổi
- `src/eth_dca_os/engine.py` — MỘT hook `smart_pool.open_accounting_month(ts)` tại
  rollover (sau Month-End settle, trước contribution, trước `su.month_reset`)
- `docs/CONVENTIONS.md` — thêm quy ước #17 (PA-A)
- `docs/tasks/WP-A7-pham-vi-ke-toan-smart-theo-thang.md` — evidence + status
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/LO_TRINH_DE_HIEU.md` (sinh tự động)

Deleted:
- Không

Migration Impact:
- Không có dữ liệu bền cần migrate. Nhưng **mọi kết quả chạy thử trước gói này không còn so sánh
  được** với kết quả sau, vì phạm vi kế toán đã đổi. Lịch sử ledger audit **phải được giữ**.

## Notes

Triage đã nêu **hai ranh giới ứng viên** cho remediation; việc chọn là **quyết định thiết kế của
gói này**, phải ghi lại, **không được chọn im lặng**:

- **PA-A** — đưa vòng đời tháng vào tầng kế toán: theo dõi `smart_reserved/deployed` theo
  accounting month đúng như DM §5 mô tả. Bám canonical nhất, nhưng chạm cấu trúc
  `Pool` / `MonthlyCapital`.
- **PA-B** — giữ `Pool` luỹ kế và đưa tử số về **ngân sách Smart luỹ kế** để hai vế cùng phạm vi.
  Thay đổi nhỏ hơn, nhưng làm ngữ nghĩa "unlock theo tháng" (ST §6) trở nên gián tiếp và cần
  chứng minh tương đương ở **mọi** tháng.

Ghi chú tương thích ngược: `tests/test_capital.py::test_smart_reservable_no_relock` dùng khung
**một tháng** (`budget_total=100`, pool contribute 100) nên **đúng với cả hai phạm vi** —
remediation **không cần** nới lỏng hay sửa test hiện có này. Không test nào trong repo khoá chặt
hành vi luỹ kế xuyên tháng.

Phối hợp: WP-A7 sở hữu **phạm vi kế toán vốn Smart**; WP-A3 (DONE) sở hữu **Market Regime và
vòng đời Crash ladder**; WP-A4 sở hữu **ngữ nghĩa dữ liệu xấu**; WP-A6 sở hữu **thứ tự 18 bước**.
Không gói nào được định nghĩa lại phần của gói khác.
