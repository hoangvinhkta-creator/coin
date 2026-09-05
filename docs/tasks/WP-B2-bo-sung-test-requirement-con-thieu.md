# WP-B2 — Bổ sung test cho các yêu cầu đặc tả còn thiếu

## Metadata
Status:
**IMPLEMENTED — 2026-09-05, phiên `S026`** (nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`). Ready Gate được xác nhận lại đầy đủ khi mở task;
`READY → IN_PROGRESS → IMPLEMENTED`. **10/10 REQUIRED check PASS** (`CHECK-B2-01`…`CHECK-B2-10`,
E1 toàn bộ — Completion Gate đóng băng 2026-08-23 KHÔNG bị sửa một chữ nào ở phần yêu cầu).

Bổ sung **141 ca test** (4 file test + 1 module quan sát), **0 dòng `src/eth_dca_os/` bị sửa**
(`git diff` rỗng trên mọi production path), full suite **678/678 PASS** (trước gói: 537/537).
Bảng đối chiếu **31/31 requirement §21** nằm ở `docs/CONVENTIONS.md` và được một bộ test giữ cho
không trôi khỏi văn bản spec. Sinh hai mục HARDENING `H-39`, `H-40` (không nâng đường găng,
không tạo task ID nào).

`IMPLEMENTED → DONE` là quyết định của chủ dự án theo
`governance/v4/CORE/STATE_AUTHORITY.md` — implementer KHÔNG tự chuyển. Bằng chứng đầy đủ:
`docs/reviews/WP-B2-IMPLEMENTATION-REPORT.md`.

Trước đó: READY — cập nhật tại `DEC-031` (2026-09-03): dependency `T-06 DONE` nay thoả. Mục
"Xác nhận lại toàn bộ Ready Gate khi mở task" còn `[ ]` — thực hiện bởi phiên mở `IN_PROGRESS`.

Phase:
Phase 4 — Lớp B: bắt buộc sửa trước verdict

Task Mode:
MAJOR

Lớp (RCP-001):
B — MUST FIX BEFORE VERDICT

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 2
B: 1
A: 2
X: 3
U: 2
V: 3
H: 3
C: 3
F: 2

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.2

Effort Routing Score:
2.55

Applied Model Floor:
none

Applied Effort Floor:
none

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
2/4

Blast Radius:
1/4

Project Profile:
PRODUCT

## Objective

Đóng khoảng trống độ phủ test cho những yêu cầu mà Backtest §21 liệt kê là **bắt buộc** nhưng hiện
không có gì kiểm chứng — đặc biệt §21.3, hiện gần như trống.

Mục tiêu không phải là "tăng số test". Mục tiêu là: mỗi requirement §21 hoặc **có test**, hoặc
**được ghi rõ vì sao không thể có test** — không requirement nào rơi vào im lặng.

## Vì sao gói này ở lớp B

Test không đổi kết quả official run đã chạy, nhưng nó quyết định mức tin cậy đặt vào kết quả đó, và
nó là lưới an toàn cho mọi thay đổi sau này (lớp C, T-10, T-11).

## Đóng finding / đề xuất

- R-09 — bổ sung test cho các requirement §19/§21 chưa có test
- Toàn bộ danh sách "Requirement của spec CHƯA CÓ TEST" trong `docs/reviews/S001-audit-findings.md`

Không đóng F-019 (thứ tự 18 bước) — mục đó thuộc **WP-A6** và phải xong trước T-06.

## Scope

- `tests/` — bổ sung test
- `docs/CONVENTIONS.md` — ghi lý do cho các mục NOT_APPLICABLE

## Out of Scope

- **Sửa mã sản phẩm để test đi qua.** Nếu một test mới thất bại, đó là **finding**, không phải lý do
  sửa `src/`. Mở finding và xử lý theo lớp phù hợp
- Test thứ tự 18 bước (WP-A6)
- Test cho partial fill ở tầng engine — không thể có, vì partial fill không phát sinh trong backtest
  (F-020); phần sản phẩm thuộc WP-C3
- Chính sách verdict (WP-B1)

## Dependencies
- T-04 (DONE)
- **T-06** (DONE)

## Blocks
- GATE-B → T-07

## Parallel-Safe With
- WP-B1, WP-B3

## Expected Touch Area

Allowed:
- `tests/`
- `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- Toàn bộ `src/eth_dca_os/` — gói này **chỉ viết test**
- `webapp/`, `docs/spec/`

## Subtasks
- [x] B2.1 §21.2 — Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và Day 28 — `test_b2_01a`…`test_b2_01d`
- [x] B2.2 §21.2 — không double reservation giữa Smart / Opportunity / Crash ở tầng engine — `test_b2_02a`, `test_b2_02b` (bất biến đo ở MỌI nến)
- [x] B2.3 §21.2 — Crash eligible-capital snapshot [F5] đo **sau** cancel/release — `test_b2_01e`, `test_b2_01f`
- [x] B2.4 §21.3 — một, hai và ba zone bị xuyên trong cùng một nến; giới hạn tối đa hai zone mỗi cycle — `test_b2_03a` (4 ca: một/hai/ba/bốn zone)
- [x] B2.5 §21.3 — tie-break §15.1 [F2]; `max_zones` áp sau khi sắp thứ tự — `test_b2_03b`, `test_b2_03c`
- [x] B2.6 §21.3 — Opportunity confirm bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW — `test_b2_04a`, `test_b2_04b`
- [x] B2.7 §21.3 — proxy ban đêm tại 07:00 local; TTL; action MISSED — `test_b2_04c`…`test_b2_04f`
- [x] B2.8 §21.3 — Crash funding unavailable scenario — `test_b2_05c`
- [x] B2.9 §21.3 — cooldown và override, gồm tần suất override trong CRASH — `test_b2_05a`, `test_b2_05b`
- [x] B2.10 §21.3 — chuyển Opportunity ladder sang Crash ladder không tạo double reservation — `test_b2_02a`
- [x] B2.11 §21.3 — [F1] STRESSED không có hiệu ứng execution (test hồi quy thường trực) — `test_b2_06` (thường trực, độc lập và NGƯỢC CHIỀU với test WP-A3)
- [x] B2.12 §21.4 — data gap và delayed Base fill — `test_b2_07a`, `test_b2_07b`
- [x] B2.13 §21.4 — Benchmark C [F4]: mỗi trigger bắn tối đa một lần mỗi chu kỳ, chu kỳ reset đúng luật — `test_b2_07c`…`test_b2_07e`
- [x] B2.14 Ghi nhận các mục NOT_APPLICABLE kèm lý do — `docs/CONVENTIONS.md` § đối chiếu §21 + `test_wp_b2_spec21_coverage_matrix.py`

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa — **đặc biệt: không sửa `src/` để test đi qua**
- [x] **Dependency T-06 DONE** — `DEC-031` (2026-09-03): official run thật đã chạy, verdict `DO_NOT_BUILD`
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §21.2, §21.3, §21.4
- [x] Data impact được biết — không có
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — thực hiện tại `S026` (2026-09-05):
  mười hai mục trên được rà lại từng mục trên trạng thái repo thật tại `b778dc1`; dependency
  `T-04 DONE` và `T-06 DONE` xác nhận lại từ `PROJECT/PROJECT_PROGRESS.md`; Completion Gate
  vẫn nguyên vẹn từ bản đóng băng 2026-08-23 (không REQUIRED check nào bị thêm/bớt/đổi yêu
  cầu, không evidence level nào bị hạ)

## Completion Gate

Risk = 2 → E1 cho các check kiểm chứng được (bản chất gói này là chạy test, nên E1 là mức tự nhiên).

### Testing

#### CHECK-B2-01 — §21.2 capital và ladder có test đầy đủ
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test tồn tại và PASS cho — Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và
Day 28; snapshot [F5] đo sau cancel/release.

**Kết quả (PASS):**

Sáu test trong `tests/test_wp_b2_spec21_2_capital_ladder.py`, tất cả chạy `run_engine` THẬT:

- `test_b2_01a_base_advance_does_not_repeat_the_original_scheduled_day` — OSCORE 75 từ 07:00
  Day 1 kéo sớm tranche Day 3 (20,0 = 40% × ngân sách Base 50); **Day 3 12:00 KHÔNG có bản ghi
  Base nào**, trong khi run đối chứng (OSCORE 20, cùng dataset) CÓ, đúng 20,0. Tổng Base cả
  tháng bằng nhau ở hai đường đi: **50,0** — ngày gốc không lặp lại và cũng không mất tiền.
- `test_b2_01b_base_advance_at_most_one_tranche_per_new_daily_score` — OSCORE 75 ba ngày liền
  kéo đúng ba tranche (20/15/15) tại 07:00 Day 1/2/3, **0 bản ghi `BASE_SCHEDULE`**.
- `test_b2_01c_month_end_day25_settles_half_and_day28_settles_the_rest` — sổ mở từ Day 5 nên
  tranche Day 3 treo tới cuối tháng: Day 13 = 15,0; Day 23 = 15,0; **Day 25 12:00 = 10,0 (50%
  của 20 còn lại)**; **Day 28 12:00 = 10,0 (phần còn lại)**; cửa sổ Day 25–27 settle ĐÚNG MỘT
  LẦN; `BASE.available` cuối tháng = 0.
- `test_b2_01d_month_end_day28_is_reached_even_without_a_day25_leftover` — đối chứng: lịch
  3/13/23 chạy đủ thì Month-End Base KHÔNG phát sinh (nó là đường DỌN, không phải tranche thứ tư),
  trong khi Month-End **Smart** vẫn chạy ở Day 28.
- `test_b2_01e_crash_snapshot_is_measured_after_cancel_and_release` — kịch bản có Opportunity
  ladder ĐANG GIỮ reservation tại crash entry (điểm mù của bộ test WP-A3, vốn không có ladder
  Opportunity mở lúc đó). Release tại `CRASH_ENTRY` = **3,8**; snapshot [F5] engine dùng =
  **5,8**; snapshot phản chứng "nếu đo TRƯỚC cancel/release", tính bằng ĐÚNG công thức ST §14
  trên trạng thái pool của nến liền trước = **2,0**. Chênh lệch 5,8 − 2,0 = 3,8 = đúng lượng
  vừa release.
- `test_b2_01f_crash_snapshot_is_immutable_for_the_life_of_the_ladder` — `eligible_capital_vnd`
  chụp ở **cả 1.344 nến** của kịch bản chỉ có duy nhất một giá trị, qua cả fill, Recovery và
  cancel cuối Recovery.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-02 — Không double reservation giữa Smart / Opportunity / Crash được kiểm ở tầng engine
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test phủ cả ca chuyển Opportunity ladder sang Crash ladder. Mệnh đề 3 của Impl Plan §7
hiện **KHÔNG KẾT LUẬN ĐƯỢC** vì không có test nào ở tầng engine; gói này phải đưa nó về kết luận
(nếu WP-A3 chưa đóng phần này).

**Kết quả (PASS):**

Mệnh đề 3 của Impl Plan §7 nay **KẾT LUẬN ĐƯỢC** ở tầng engine. Bất biến được kiểm:

    tổng RESERVED của mọi pool  ==  tổng `reserved_vnd` của mọi zone ĐANG MỞ

đo tại **MỌI nến**, không chỉ cuối run (điểm đo là bước 12b của §19 — xem `tests/wp_b2_probe.py`).
Double reservation là đúng trạng thái làm hai vế lệch nhau.

- `test_b2_02a_no_double_reservation_when_opportunity_becomes_crash` — ca chuyển
  Opportunity → Crash có thật (ladder Opportunity `CANCELLED`, Crash ladder được cấp vốn từ
  chính pool đó): 0/1.344 nến lệch; reserve Crash rút từ pool OPPORTUNITY (**5,8**) ≤ available
  sau release (**19,8**); mọi zone Opportunity `CANCELLED` giữ `reserved_vnd = 0`.
- `test_b2_02b_no_double_reservation_across_smart_and_opportunity` — đường đi KHÔNG có Crash,
  hai accounting month, ba ladder / 11 zone, ≥3 fill Smart và ≥2 fill Opportunity: 0/3.936 nến lệch.
- `test_b2_02c_probe_does_not_change_engine_behaviour` — tiền đề của mọi khẳng định trên:
  cùng kịch bản chạy CÓ và KHÔNG instrumentation cho đầu ra tài chính trùng khớp bit-for-bit.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-03 — §21.3 execution: đa zone, giới hạn cycle, tie-break [F2]
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test cho một/hai/ba zone bị xuyên trong cùng nến; tối đa hai zone mỗi cycle; tie-break ba
tầng theo §15.1 và `max_zones` áp **sau** khi sắp thứ tự. Mệnh đề 12 hiện chỉ xác nhận ở tầng code.

**Kết quả (PASS):**

`tests/test_wp_b2_spec21_3_execution.py`. Số zone "bị xuyên trong cùng một nến" được tính
ĐỘC LẬP với engine, từ OHLC của nến và luật BT §5 (`Smart: LOW <= zone`,
`Opportunity: CLOSE <= zone`) — không hỏi engine rồi mô tả lại câu trả lời của nó.

- `test_b2_03a_zones_pierced_in_one_candle_and_max_two_per_cycle` (4 ca tham số hoá) — tại nến
  `2023-04-05 00:00`: **một** zone (1 action, 0 chặn), **hai** zone (2 action, 0 chặn), **ba**
  zone (2 action, 1 `MAX_ZONES_BLOCK`), **bốn** zone (2 action, 2 chặn). Mọi zone bị xuyên đều
  hoặc có action hoặc bị chặn (không zone nào rơi vào im lặng); zone bị chặn GIỮ `TRIGGERED` và
  được cấp action ở một cycle sau.
- `test_b2_03b_max_zones_is_applied_after_ordering_not_before` — kịch bản hai tháng dựng đúng
  tình huống **thứ tự duyệt thô ≠ thứ tự §15.1**: Opportunity ladder (tháng 3, TTL 90 ngày)
  đứng TRƯỚC Smart ladder tháng 4 trong danh sách `ladders`. Test khẳng định hai thứ tự thật sự
  khác nhau (nếu không, nó tự tuyên bố mình vô nghĩa) rồi kiểm engine chọn đúng hai zone
  **SMART** theo §15.1 và chặn hai zone **OPPORTUNITY**.
- `test_b2_03c_tiebreak_orders_fills_inside_one_candle_base_smart_opportunity` — tầng 1 (pool)
  và tầng 3 (`zone_index` tăng dần) của khoá §15.1 quan sát trên THỨ TỰ GHI SỔ các fill trong
  cùng một nến (§19 bước 15).

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-04 — §21.3 trigger và proxy: CLOSE/LOW, proxy 07:00, TTL, MISSED
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test cho Opportunity confirm bằng CLOSE và thực thi ở nến sau; Smart trigger bằng LOW;
proxy ban đêm tại 07:00 local; TTL hết hạn; action chuyển MISSED.

**Kết quả (PASS):**

- `test_b2_04a_smart_triggers_on_low_while_opportunity_ignores_the_same_wick` — nến `LOW = 88`,
  `CLOSE = 100`: hai zone Smart (94,06 và 88,12) bị xuyên; zone Opportunity tại 90,81 — **thấp
  hơn LOW nhưng cao hơn CLOSE** — KHÔNG được confirm. Đây chính là phép phân biệt LOW/CLOSE:
  nếu Opportunity đọc LOW thì zone đó đã trigger.
- `test_b2_04b_opportunity_confirms_on_close_and_executes_on_a_later_candle` — với mọi fill
  Opportunity, thời điểm fill ≥ nến confirm + một nến; không fill nào rơi vào chính nến confirm.
- `test_b2_04c_night_trigger_executes_at_the_first_candle_at_or_after_07_00_local` — trigger tại
  `2023-03-05 00:00` (giờ ĐÊM theo BT §6), RNG tất định u = 0,5 rơi vào nhánh 45% → fill tại
  **đúng `2023-03-05 07:00`**, tức `close(T) + seconds_to_7am`. `behavioral_rng` là tham số công
  khai của `run_engine`, không phải cửa hậu dựng riêng cho test.
- `test_b2_04d_behavioral_missed_releases_the_reservation_at_ttl` — u = 0,97 → mọi action MISSED:
  0 fill Smart, `missed_actions` khớp số bản ghi `ACTION_MISSED`, zone ở trạng thái `MISSED` với
  `reserved_vnd = 0`, và mốc MISSED đầu tiên đúng `trigger 07:15 → close 07:30 + TTL 12h = 19:30`.
- `test_b2_04e_behavioral_distribution_matches_the_spec_table` (17 ca) — bảng phân phối BT §6 đọc
  theo đúng các mốc xác suất của spec (50/30/15/5 ban ngày; 10/25/45/20 ban đêm), kiểm trên chính
  hàm production `execution.behavioral_delay_seconds`.
- `test_b2_04f_night_proxy_becomes_missed_when_it_would_outlive_the_ttl` — nhánh "còn TTL" và
  nhánh vượt TTL, kể cả điểm biên `seconds_to_7am == ttl`.

Giới hạn được ghi TƯỜNG MINH thay vì im lặng: ở TTL baseline 12h, nhánh "proxy 07:00 vượt TTL"
không tới lượt chạy trên đường production (giờ đêm cho `seconds_to_7am` tối đa 8h) — `H-40`.
Và không cấu hình nào trong `manifests.GATE3_GRID` bật `behavioral_model = LOCAL_HOUR` — `H-39`.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-05 — §21.3 cooldown, override và Crash funding unavailable
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test cho cooldown, override, tần suất override trong CRASH, và kịch bản Crash funding
unavailable.

**Kết quả (PASS):**

- `test_b2_05a_cooldown_holds_a_pierced_zone_and_override_releases_it_in_crash` — TRONG CRASH:
  `CRASH_ZONE_0` fill ở `2023-03-05 07:45` (giá 100,5) mở cooldown 48h; nến `2023-03-06 00:00`
  xuyên `CRASH_ZONE_1` nhưng OPEN còn 100,5 nên zone **GIỮ `TRIGGERED`**; nến 00:15 có OPEN = 90
  ≤ 100,5 × (1 − 7%) = 93,465 → override → fill ở 00:45, **trong cửa sổ cooldown**.
  `counters["cooldown_override"]["CRASH"] == 1` và tổng override == 1 (đếm theo SỰ KIỆN một
  cycle, không theo từng zone — ST §15 / `F-031`), dù hai zone cùng được ghi `COOLDOWN_OVERRIDE`.
- `test_b2_05b_without_override_the_cooldown_blocks_the_fill_entirely` — đối chứng mức giảm 3,5%
  < 7%: 0 override, `CRASH_ZONE_1..3` kết thúc `CANCELLED` ở cuối Recovery, `OPPORTUNITY.reserved`
  về 0 (cooldown không tạo kênh khoá vốn).
- `test_b2_05c_crash_funding_unavailable_turns_every_crash_action_into_missed` — BT §5, stress
  scenario riêng: cùng dataset và cùng ma sát (`ON_DEMAND`, user_delay 4h, funding_delay 1h),
  chỉ khác cờ `p2p_unavailable_in_crash`. Cờ TẮT → có fill Crash; cờ BẬT → **0 fill Crash**, action
  Crash kết thúc `MISSED`, `OPPORTUNITY.reserved` về 0 (vốn không bị khoá), và
  `executed_actions` giảm so với đối chứng.

Ghi nhận đi kèm: không cấu hình nào trong `manifests.GATE3_GRID` bật cờ stress này, nên kịch bản
BT §5 chưa có đường chạy trong pipeline — **`H-39`**, định tuyến `OUT_OF_SCOPE` về `CAP-PIPELINE`,
KHÔNG sửa trong gói này.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-06 — [F1] STRESSED không có hiệu ứng execution có test hồi quy thường trực
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test tồn tại lâu dài trong `tests/`, độc lập với test tạm thời của WP-A3. Đây là mệnh đề đã
từng BÁC BỎ; nó cần một lưới an toàn thường trực.

**Kết quả (PASS):**

`test_b2_06_stressed_label_has_no_execution_effect_permanent_regression` —
`tests/test_wp_b2_spec21_3_execution.py`, một file test thường trực của `tests/`, độc lập với
test của WP-A3 cả về kịch bản lẫn CHIỀU phản chứng:

- WP-A3 (`test_check_a3_03_...`) **ÉP** nhãn STRESSED bật lên cho toàn bộ thời gian nền NORMAL.
- WP-B2 đi chiều NGƯỢC LẠI: nhãn STRESSED phát sinh **tự nhiên** từ dữ liệu, và run đối chứng
  **LOẠI BỎ** nó (STRESSED → NORMAL). Hai chiều bắt được hai lớp lỗi khác nhau; một trong hai
  bị xoá thì lớp còn lại vẫn có lưới.

Tiền đề chống PASS rỗng: run A thật sự có nhãn STRESSED (run B không có), và có fill của **cả
bốn** nguồn BASE/SMART/OPPORTUNITY/CRASH, ≥1 sự kiện cooldown override, đủ ba loại ladder.

Bề mặt so sánh rộng hơn WP-A3: purchase (bỏ trường nhãn reporting), `eth_total`, contribution,
`monthly_deployments`, `cash_samples`, `opp_cap_samples`, mọi `counters` (riêng override so
TỔNG vì phân rã theo nhãn chính là reporting decomposition BT §16), cấu trúc + kết cục của mọi
ladder/zone, ledger từng pool, **`execution_state_timeline`** (chiều WP-C2) và
**`market_snapshots`** (bỏ trường `market_regime`). Tất cả trùng khớp.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-07 — §21.4 data gap, delayed Base fill và Benchmark C [F4]
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: test cho data gap và delayed Base fill; và test [F4] cho Benchmark C — mỗi trigger bắn tối
đa một lần mỗi chu kỳ, chu kỳ reset đúng luật. BT §21.4 đòi tường minh test [F4] nhưng hiện chưa có.

**Kết quả (PASS):**

`tests/test_wp_b2_spec21_4_accounting.py`.

Data gap và delayed Base fill — gói này KHÔNG viết lại phần WP-A4 đã phủ (nhãn
`EXECUTION_DATA_GAP`/`DELAYED_DATA_FILL` trên bản ghi, tranche Base không bị bỏ); nó đóng đúng
câu ĐẦU của BT §18 mà chưa test nào chạm tới:

- `test_b2_07a_a_missing_candle_window_is_not_interpolated_into_a_trigger` — cùng một `day_specs`,
  hai dataset: đầy đủ (672 nến) và bị khoét trọn ngày có cú dip (576 nến, đúng −96). Dataset đầy
  đủ: `SMART_ZONE_1` bị xuyên và `EXECUTED`. Dataset bị khoét: zone **còn nguyên `ACTIVE`**, 0
  fill — engine KHÔNG dựng lại cú dip từ hai đầu lỗ hổng. Mọi nến engine duyệt đều có thật trong
  dataset.
- `test_b2_07b_delayed_base_fill_lands_on_a_real_candle_after_the_gap` — khoét 12:00–12:45 Day 3:
  fill rơi vào `13:00` với `missing_candles_before = 4`, giá bằng **OPEN thật** của nến đó, và
  khoảng cách tới nến trước đúng 5 nến. Đối chứng dataset liên tục: fill tại 12:00, không nhãn,
  **cùng số tiền** — lỗ hổng đổi thời điểm, không đổi ngân sách.

Benchmark C [F4] — indicator daily được điều khiển tay để dựng ba chu kỳ có kiểm soát:

- `test_b2_07c_benchmark_c_each_trigger_fires_once_per_cycle_and_resets_by_rule` — đúng **bốn**
  lần bắn trên toàn cửa sổ: `2023-02-10` (−30%, chu kỳ 1), `2023-03-04` (−30%, chu kỳ 2 sau reset
  `2023-03-02`), `2023-03-22` (−45%, **cùng chu kỳ 2, trigger KHÁC**), `2023-04-03` (−30%, chu kỳ
  3 sau reset `2023-04-01`). Chu kỳ 1 kéo 20 ngày liên tục thoả điều kiện mà chỉ bắn MỘT lần.
  Bảo toàn vốn: `spent + final_reserve == contributed == 500`.
- `test_b2_07d_benchmark_c_without_a_reset_each_trigger_fires_at_most_once_ever` — bỏ mọi lần
  `close >= ma200`: chỉ còn **hai** lần bắn (một mỗi trigger) dù dd thoả suốt 90 ngày.
- `test_b2_07e_benchmark_c_reset_needs_a_fired_trigger_first` — một lần `close >= ma200` khi chưa
  trigger nào bắn KHÔNG tạo thêm chu kỳ nào: chuỗi lần bắn và `eth` không đổi.

Lần bắn dip được tách khỏi lệnh mua theo tháng bằng mốc thời gian của **Benchmark A** (cùng
`_monthly_buy_points`), không bằng một bản dựng lại của chính hàm đang kiểm.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

### Documentation / Integrity

#### CHECK-B2-08 — Mọi requirement §21 không thể test được ghi NOT_APPLICABLE kèm lý do
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: bảng đối chiếu đầy đủ requirement §21 → test tương ứng, hoặc → NOT_APPLICABLE kèm lý do.
Ví dụ đã biết: partial fill giữ phần dư ở RESERVED tới hết TTL — không test được ở tầng backtest vì
partial fill không phát sinh (F-020), thuộc WP-C3; VND → USDT dual cost basis — NOT_APPLICABLE theo
[F6]. **Không mục nào được im lặng bỏ qua.**

**Kết quả (PASS):**

Bảng đối chiếu nằm ở `docs/CONVENTIONS.md` § "Đối chiếu requirement Backtest §21 → test (WP-B2)":
**31 hàng — đúng 31 gạch đầu dòng của §21.1–§21.4**, không thiếu, không thừa.

- 29 hàng `TESTED`, 1 hàng `MIXED` (§21.2 "Reserve, release, partial fill …": phần reserve/
  release/không double reservation có test; phần **partial fill phát sinh trong backtest** là
  `NOT_APPLICABLE` — engine fill NGUYÊN ZONE, partial fill không phát sinh ở tầng backtest,
  `F-020`, phần sản phẩm thuộc `WP-C3`), 1 hàng `NOT_APPLICABLE` (§21.4 "VND → USDT … dual cost
  basis": BT §2.1 [F6] chốt đơn vị danh nghĩa 1 USDT = 1 đơn vị nên không tồn tại bước quy đổi
  nào ở tầng backtest; lớp kế toán VND thuộc app web / `T-09A`).
- Bảng KHÔNG được để tự trôi: `tests/test_wp_b2_spec21_coverage_matrix.py` (96 ca) đối chiếu
  cột requirement với **chính văn bản** `docs/spec/03_BACKTEST_SPEC_V2_1_5.md` §21 theo nguyên
  văn, kiểm mọi trạng thái thuộc `{TESTED, NOT_APPLICABLE, MIXED}`, kiểm **mọi tên test được
  viện dẫn có thật trong `tests/`** (đọc bằng AST, không grep), và kiểm chiều ngược lại: mọi
  hàm test do WP-B2 viết phải có đường về một requirement §21 — không test nào tồn tại chỉ để
  tăng số đếm.

Sửa một câu trong spec, đổi tên một test, hay thêm một test WP-B2 không gắn requirement nào đều
làm bộ test này ĐỎ.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-09 — Test mới thất bại được ghi thành finding, không được sửa `src/` để đi qua
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh gói này không sửa `src/eth_dca_os/`. Nếu có test mới FAIL, phải tồn
tại finding tương ứng đã được ghi nhận và phân lớp, kèm quyết định xử lý ở gói nào.

**Kết quả (PASS):**

    git diff --stat b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    -> (rỗng)

Không dòng mã sản phẩm nào bị sửa. `Expected Touch Area` được tôn trọng tuyệt đối: thay đổi chỉ
nằm ở `tests/`, `docs/`, `PROJECT/`.

**Không test mới nào FAIL.** Vì vậy điều kiện "nếu có test mới FAIL thì phải tồn tại finding
tương ứng" không phát sinh. Tuy vậy gói này vẫn phát hiện hai điều đáng ghi, và cả hai đã được
ghi nhận + phân lớp thay vì bỏ qua:

- **`H-39`** (CONFIRMED HARDENING, ánh xạ `RSK-007`) — hai kịch bản robustness Gate 3 mà Impl
  Plan §8 ghi là bắt buộc (behavioral simulation BT §6; stress P2P-unavailable BT §5) không có
  đường chạy trong pipeline: `GATE3_GRID` không biến thiên `behavioral_model` /
  `p2p_unavailable_in_crash`, nên cả 114 config đều `OFF/False`. Định tuyến `OUT_OF_SCOPE` về
  `CAP-PIPELINE` (`WP-A2` đã DONE → `OWNER_ASSIGNMENT_REQUIRED`). KHÔNG sửa ở đây: ngoài Expected
  Touch Area, và sửa rồi chạy lại Gate 3 chính là "chạy lại để làm đẹp kết quả official" mà BT §22
  / Master Index §6 cấm. Không đổi verdict: `DO_NOT_BUILD` đã do Gate/Failure Signal quyết.
- **`H-40`** (CONFIRMED HARDENING) — nhánh "proxy 07:00 vượt TTL → MISSED" của BT §6 không tới
  lượt chạy ở TTL baseline 12h (giờ đêm cho `seconds_to_7am` tối đa 8h). Cùng họ `H-36`. Được
  kiểm ở tầng hàm và ghi rõ giới hạn, thay vì tuyên bố một độ phủ mà đường production không có.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

#### CHECK-B2-10 — Toàn bộ test suite PASS hoặc mọi FAIL đều là finding đã ghi nhận
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ. Không test hiện có nào bị skip, xoá hay nới lỏng để nhường chỗ
cho test mới.

**Kết quả (PASS):**

Toàn bộ suite Python, không deselect, không `-k`, không đánh dấu skip/xfail nào được thêm:

    $ python -m pytest -p no:cacheprovider
    ...
    678 passed in 1153.20s (0:19:13)
    exit code 0

    collected  678
    passed     678
    failed       0
    errors       0
    skipped      0
    xfail/xpass  0
    exit code    0

Trước gói: **537 passed**, exit 0 (đo trên đúng HEAD `b778dc1`, cùng interpreter và cùng bộ thư
viện). Sau gói: **678 passed** — chênh lệch **+141** đúng bằng số ca WP-B2 thêm vào
(9 + 31 + 5 + 96).

Không test hiện có nào bị xoá, đổi tên, nới lỏng hay bỏ chọn: `git diff --stat b778dc1..HEAD --
tests/` chỉ có **file mới**, 0 dòng bị xoá khỏi file test cũ.

Executed By:
Phiên `S026` (implementer) — nhánh `claude/wp-b2-implementation-u9y68k`, tách từ
`origin/main` `b778dc1`. Python 3.11.15 · numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 ·
pytest 9.1.1 (khớp `pyproject.lock`).

Timestamp:
2026-09-05

## Exit Criteria
- [x] 100% REQUIRED checks PASS — 10/10 (`CHECK-B2-01`…`CHECK-B2-10`)
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ) — không check nào đòi E2, không mức nào bị hạ
- [x] Bảng đối chiếu requirement §21 → test/NOT_APPLICABLE hoàn chỉnh — 31/31 hàng,
      `docs/CONVENTIONS.md`, có test giữ cho bảng không trôi khỏi spec
- [x] Không mã sản phẩm nào bị sửa trong gói này — `git diff b778dc1..HEAD -- src/eth_dca_os
      webapp pyproject.toml pyproject.lock` rỗng
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [x] Session handoff được viết — `docs/sessions/S026-wp-b2-bo-sung-test-spec21.md`
- [x] Không hạ REQUIRED check nào để đạt DONE — phần "Yêu cầu:" của cả mười check giữ nguyên
      nguyên văn bản đóng băng 2026-08-23

## Escalation Triggers

- Một test mới phát hiện hành vi sai → **không sửa trong gói này**. Mở finding, phân lớp theo tiêu
  chí RCP-001 (ảnh hưởng official run / verdict / productization), trình chủ dự án.
- Một requirement §21 không thể test được nếu không tái cấu trúc `src/` → ghi NOT_APPLICABLE kèm lý
  do kỹ thuật, và mở đề xuất cho gói phù hợp. Không tự tái cấu trúc.
- Số requirement chưa có test vượt khả năng đóng trong một phiên → chia phiên, KHÔNG nâng Tier, và
  KHÔNG đóng gói khi danh sách chưa hết.

## Ảnh hưởng nếu gói này thất bại

GATE-B không đóng → T-07 không mở. Rủi ro dài hạn lớn hơn: mọi thay đổi sau này ở lớp C, T-10, T-11
sẽ không có lưới an toàn cho §21.3 — đúng vùng hành vi phức tạp nhất của engine.

## Changed Files Registry

Created:
- `tests/wp_b2_probe.py` (299 dòng) — dụng cụ QUAN SÁT: chụp Pool/Ladder/trạng thái zone theo
  từng nến qua `derive_execution_state` (bước 12b §19). Quan sát thuần, được
  `test_b2_02c` khoá bằng phép so bit-for-bit có/không instrumentation
- `tests/test_wp_b2_spec21_2_capital_ladder.py` (312 dòng, 9 ca) — §21.2
- `tests/test_wp_b2_spec21_3_execution.py` (538 dòng, 31 ca) — §21.3
- `tests/test_wp_b2_spec21_4_accounting.py` (220 dòng, 5 ca) — §21.4
- `tests/test_wp_b2_spec21_coverage_matrix.py` (158 dòng, 96 ca) — giữ bảng đối chiếu §21
  không trôi khỏi văn bản spec
- `docs/reviews/WP-B2-IMPLEMENTATION-REPORT.md` — báo cáo thực thi
- `docs/sessions/S026-wp-b2-bo-sung-test-spec21.md` — session handoff

Modified:
- `docs/CONVENTIONS.md` — thêm mục "Đối chiếu requirement Backtest §21 → test (WP-B2)" (31 hàng)
- `PROJECT/HARDENING_BACKLOG.md` — thêm `H-39`, `H-40`
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/CAPABILITY_REGISTRY.md`,
  `PROJECT/REVIEW_BUDGET_LEDGER.md`, `PROJECT/LO_TRINH_DE_HIEU.md` (sinh tự động)
- chính file task này (trạng thái + kết quả Completion Gate)

Deleted:
- Không

Migration Impact:
- Không. `src/eth_dca_os/`, `webapp/`, `pyproject.toml`, `pyproject.lock` KHÔNG đổi một dòng.

## Notes

Rủi ro đặc trưng của gói viết test cho code đã có: viết test **mô tả hành vi hiện tại** thay vì
**kiểm chứng yêu cầu spec**. Test kiểu đó luôn PASS và không bảo vệ gì cả. Mỗi test ở đây phải bắt
đầu từ một câu trong §21, không phải từ một hàm trong `engine.py`.
