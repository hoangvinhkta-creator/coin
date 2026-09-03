# WP-A5 — Đo đủ dữ liệu cho ba tín hiệu cảnh báo hỏng chiến lược

## Metadata
Status:
**IMPLEMENTED — 9/9 REQUIRED PASS (E1) tại S015 (2026-09-03)**. Đóng phần đo lường của F-002 và
toàn bộ F-016. Sau run đủ phase: `UNKNOWN: []` — không Failure Signal nào còn UNKNOWN. Không hạ
REQUIRED check nào. Phát sinh `F-S015-01` (BLOCKING): phần thuộc WP-A5 đã sửa trong gói; phần gốc
ở `failure_signals.py` định tuyến sang `WP-B1` vì nằm ngoài Expected Touch Area và `CHECK-A5-07`
(FROZEN) bắt buộc chứng minh file đó KHÔNG đổi.
Chuyển `DONE` là hành động của chủ dự án (`STATE_AUTHORITY.md`).

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 2
A: 3
X: 3
U: 3
V: 3
H: 3
C: 3
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.8

Effort Routing Score:
3.0

Applied Model Floor:
cognitive:A>=3&X>=3

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
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Sinh ra **dữ liệu đo lường** mà ba Failure Signal hiện không bao giờ nhận được, và mở rộng phạm vi
tính FS-03/FS-07 ra toàn bộ chín window thay vì chỉ một window đại diện.

## Ranh giới trách nhiệm — đọc trước khi làm

Gói này chịu trách nhiệm **ĐO LƯỜNG (measurement)**. Gói này **KHÔNG** chịu trách nhiệm **CHÍNH SÁCH
VERDICT (verdict policy)**.

| Câu hỏi | Thuộc gói nào |
|---|---|
| Làm sao sinh ra `opportunity_cap_hit_share`, `regime_advantage_share`, `adjacent_config_flip`? | **WP-A5** |
| FS-03/FS-07 tính trên bao nhiêu window? | **WP-A5** |
| UNKNOWN có được phép cho ra BUILD không? | **WP-B1** |
| Ngưỡng số của FS-02/FS-07/FS-12 có hợp lệ không? | **WP-B1** |
| Gate 1 có phải chạy lại sau remediation không (DEC-009)? | **WP-B1** |

Nguyên tắc từ S001 — "không được phép BUILD nếu REQUIRED Failure Signal còn UNKNOWN" — **thuộc
WP-B1**, không thuộc gói này. WP-A5 chỉ có nghĩa vụ làm cho trạng thái UNKNOWN **không còn lý do
tồn tại** vì thiếu đo lường. Không trộn hai trách nhiệm.

## Vì sao gói này ở lớp A

Ba đại lượng này chỉ sinh ra được **khi engine đang chạy**. `ethdca verdict` đọc lại
`pipeline_state.json` nên chính sách sửa được sau; nhưng dữ liệu chưa từng được đo thì không đọc lại
được từ đâu. Đó là tiêu chí phân lớp A của RCP-001.

Phụ thuộc WP-A3 là bắt buộc chứ không phải khuyến nghị: nếu vốn còn bị khoá do F-001 thì FS-02
(cap-hit share) và FS-07 (`avg_cash_ratio`) **đo ra số sai lệch** — đo đúng quy trình nhưng sai bản
chất.

## Đóng finding

- F-002 — **phần đo lường**: ba Failure Signal FS-02, FS-06, FS-12 không bao giờ được truyền input
- F-016 — FS-03 và FS-07 chỉ tính trên một window đại diện (W5), không trên toàn mẫu

Phần chính sách của F-002 thuộc WP-B1.

## Scope

- `src/eth_dca_os/pipeline.py` — sinh và truyền ba đại lượng còn thiếu; mở rộng phạm vi window
- `src/eth_dca_os/engine.py` — chỉ ở mức **thu thập số liệu**, không đổi hành vi thực thi
- `src/eth_dca_os/metrics.py` — tính đại lượng phái sinh nếu cần
- `tests/` — test khẳng định không FS nào còn UNKNOWN vì thiếu input

## Out of Scope

- **Mọi thay đổi trong `verdict.py`** — ngưỡng, ánh xạ, chính sách UNKNOWN đều thuộc WP-B1
- Thay đổi ngưỡng số của FS-02 / FS-07 / FS-12 (WP-B1)
- Thay đổi hành vi thực thi của engine (WP-A3, WP-A4)
- Đấu nối benchmark/chẩn đoán (WP-A2)
- Sửa Control F / Control G (WP-B1)

## Dependencies
- T-04 (DONE)
- **WP-A2** (DONE) — cần các hạng mục đã đấu nối để đo được đầy đủ
- **WP-A3** (DONE) — bắt buộc: vốn không bị khoá thì FS-02/FS-07 mới đo đúng
- **WP-A7** (DONE) — bắt buộc, thêm bởi **RCP-002** (2026-08-24): F-035 làm chiều
  `smart_unlock_mode` trơ và làm sai phân phối vốn qua Smart ladder. Measurement tạo TRƯỚC khi
  F-035 được sửa **không** được coi là canonical evidence cho engine cuối cùng.

## Blocks
- GATE-A → T-06
- Gián tiếp: WP-B1 (không có dữ liệu thì chính sách không kiểm chứng được)

## Parallel-Safe With
- WP-A1, WP-C1, WP-D1, WP-D2
- **Không song song với WP-A2**: cả hai sửa `pipeline.py`

## Expected Touch Area

Allowed:
- `src/eth_dca_os/pipeline.py`, `metrics.py`
- `src/eth_dca_os/engine.py` — **chỉ thêm điểm thu thập số liệu**
- `tests/`
- `docs/CONVENTIONS.md` — ghi phạm vi tính của từng FS

Do not touch without Scope Expansion:
- `src/eth_dca_os/verdict.py`, `failure_signals.py` (phần ngưỡng và chính sách), `gates.py`
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `score.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [x] A5.1 Sinh `opportunity_cap_hit_share` (FS-02) tại thời điểm chạy — `RunResult.opp_cap_samples` (mẫu theo ngày, cùng nhịp `cash_samples`) + `metrics.opportunity_cap_hit_share`
- [x] A5.2 Sinh `regime_advantage_share` (FS-12) tại thời điểm chạy — `RunResult.regime_timeline` (mốc đổi nhãn) + `metrics.regime_advantage` / `regime_advantage_pooled`
- [x] A5.3 Sinh `adjacent_config_flip` (FS-06) tại thời điểm chạy — `metrics.adjacent_config_flip`, dựng từ manifest Gate 2 đã chạy (config OFAT = kề nhau)
- [x] A5.4 Truyền cả ba vào `evaluate_failure_signals` — `pipeline.run_verdict`
- [x] A5.5 Mở rộng tính FS-03 và FS-07 ra toàn bộ chín window — `pipeline.run_gate1`, gộp bằng PrimaryMedian (BT §4.1); giá trị W5 cũ giữ ở `w5_only_legacy`
- [x] A5.6 Ghi rõ phạm vi tính của từng FS vào `docs/CONVENTIONS.md` — quy ước **#20 (a)–(f)**
- [x] A5.7 Viết test khẳng định sau khi chạy đầy đủ, không FS nào còn UNKNOWN vì thiếu input — `tests/test_wp_a5_failure_signal_instrumentation.py` (22 test)
- [x] A5.8 Chứng minh gói không đụng chính sách verdict (scope guard) — `git diff` rỗng trên `verdict.py`/`failure_signals.py` + test khoá hành vi ngưỡng tại biên

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa, và **ranh giới đo lường / chính sách được nêu tường minh**
- [x] Out-of-scope được định nghĩa
- [x] **Dependency WP-A2 DONE** (S006)
- [x] **Dependency WP-A3 DONE** — bắt buộc, không miễn trừ (S003; và `WP-A7` DONE tại S004 theo RCP-002)
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — BT §16, §17; IM §7
- [x] Data impact được biết — thêm trường đo lường vào `pipeline_state.json`
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — S015 (2026-09-03): `WP-A2` ✅, `WP-A3` ✅, `WP-A7` ✅ đều DONE trong `PROJECT_PROGRESS.md`; `branch_authority_check.sh` PASS trên nhánh `claude/coindca-data-stream-vv0vwv`; ràng buộc "không song song với WP-A2 trên `pipeline.py`" hết hiệu lực vì WP-A2 đã DONE

## Completion Gate

Risk = 3 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được.

### Functional / Instrumentation

#### CHECK-A5-01 — `opportunity_cap_hit_share` được sinh và truyền vào FS-02
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chạy pipeline đầy đủ, chứng minh FS-02 nhận giá trị số (không phải `None`). Kèm một ca có
đáp số biết trước để chứng minh đại lượng được **tính đúng**, không chỉ được truyền.

Kết quả (S015). **Đáp số biết trước** — `test_a5_01_cap_hit_share_known_answer`: 10 mẫu dựng tay
trong đó đúng 3 mẫu thoả CẢ HAI vế (`at_cap` ∧ `idle`), gồm ba ca đối chứng dễ nhầm — at_cap nhưng
hết idle, idle nhưng chưa chạm cap, và **sát cap mà chưa tới** (199/200) — khẳng định
`share == 0.3` chính xác, `n_hit == 3`. Hai thống kê phụ trợ cũng khớp tay
(`at_cap_share == 0.6`, `share_idle_ge_10pct_cap == 0.4`). **Sinh ra thật** —
`test_a5_01_engine_emits_cap_samples`: engine chạy 2019→2021 sinh `opp_cap_samples` đúng bằng số
`cash_samples` (cùng nhịp ngày), và `share` không phải `None`. **Truyền tới FS-02** — run đủ phase
tại CHECK-A5-04. **Không đo được thì báo là không đo được** —
`test_a5_01_cap_hit_share_no_samples_is_unknown_not_zero`: 0 mẫu → `None` +
`reason="no_opp_cap_samples"`, không quy về 0.0.
Số đo trên dữ liệu tổng hợp 2018-01→2026-06: **0,9063** (PrimaryMedian 9 window; từng window
0,874–0,919). Giới hạn ngữ nghĩa của vế `at_cap` (bão hoà do `Pool.total` không giảm) được ghi
tường minh ở `docs/CONVENTIONS.md` #20(a) kèm bốn thống kê phụ trợ cho WP-B1.

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-02 — `regime_advantage_share` được sinh và truyền vào FS-12
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: như trên, cho FS-12.

Kết quả (S015). **Đáp số biết trước** — `test_a5_02_regime_advantage_known_answer`: chiến lược mua
CRASH 3,0 + NORMAL 1,0 ETH, benchmark CRASH 1,0 + NORMAL 2,0 → lợi thế CRASH +2,0, NORMAL −1,0;
khối lợi thế dương = 2,0 → `share == 1.0` (trong khi mẫu số "lợi thế ròng" sẽ cho 2,0 — vượt 1 và
vô nghĩa, đây chính là lý do chọn mẫu số ở CONVENTIONS #20(b)). Ca hai regime cùng dương
(`test_a5_02_regime_advantage_two_regimes_share`): 6/(6+2) → `0.75` khớp tay. **Quy purchase của
benchmark về regime** — `test_a5_02_benchmark_purchase_attributed_by_timeline` kiểm `_regime_at`
tại sáu mốc, gồm biên trái (trước mốc đầu tiên) và đúng thời điểm đổi nhãn. **Sinh ra thật** —
`test_a5_02_engine_emits_regime_timeline`: timeline không rỗng, tăng dần theo thời gian, KHÔNG có
hai mốc liên tiếp trùng nhãn, và thưa hơn mẫu ngày. **Không đo được thì báo** —
`test_a5_02_no_positive_advantage_is_unknown_not_zero`: `None` +
`reason="no_positive_advantage_in_any_regime"`, KHÔNG quy về 0.0 (0.0 sẽ bị đọc thành "không tập
trung" — khẳng định sai).
Số đo trên dữ liệu tổng hợp: **1,0** — chỉ regime STRESSED có lợi thế dương (+3,179), còn NORMAL
−3,893, CRASH −0,602, RECOVERY −0,238.

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-03 — `adjacent_config_flip` được sinh và truyền vào FS-06
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: như trên, cho FS-06.

Kết quả (S015). **Đáp số biết trước** — `test_a5_03_adjacent_config_flip_known_answer`: baseline
PASS, hai config OFAT (một PASS một FAIL) và một config `lhs_*` FAIL → `flip is True`,
`n_adjacent == 2` (config `lhs_*` đổi nhiều chiều cùng lúc nên KHÔNG kề nhau, không được tính),
`flipped_configs == ["ofat_base_pct=0.5"]`. **Cả hai chiều** —
`test_a5_03_flip_detected_in_both_directions`: FAIL→PASS cũng là "đảo ngược" theo đúng chữ §17.
**Không có flip thì phải là False, không phải None** —
`test_a5_03_no_flip_when_all_adjacent_agree`. **Không đo được thì báo** —
`test_a5_03_lhs_config_alone_never_counts_as_adjacent`: manifest không có config kề nhau nào →
`None` + `reason="no_adjacent_config_in_manifest"`. **Khoá vào manifest THẬT** —
`test_a5_03_real_manifest_names_are_recognised_as_adjacent` gọi `generate_gate2_manifest()` thật và
khẳng định mọi config OFAT được nhận diện; nếu quy ước đặt tên của manifest đổi, test đỏ thay vì âm
thầm đếm 0 config kề nhau.
Đại lượng dựng từ chính manifest Gate 2 đã chạy nên KHÔNG tốn thêm lần chạy engine nào.

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-04 — Sau một run đầy đủ, không Failure Signal nào còn UNKNOWN vì thiếu input
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: in ra trạng thái của cả FS-01…FS-12 sau một run đầy đủ và chứng minh không mục nào là
`None`. Nếu một FS vẫn `None` vì lý do khác (ví dụ dữ liệu đầu vào không đủ dài), lý do đó phải được
ghi rõ và **không được che bằng một giá trị mặc định**.

Kết quả (S015). Run đủ phase trên dữ liệu tổng hợp 2018-01-01 → 2026-06-30 (`run_gate1` →
`run_gate2` → `run_gate3` → `run_controls` → `run_verdict`, dev_limit 25, tổng 1029 s):

    SIGNALS: {"FS-01": false, "FS-02": true,  "FS-03": true,  "FS-04": true,
              "FS-05": false, "FS-06": false, "FS-07": false, "FS-08": true,
              "FS-09": false, "FS-10": false, "FS-11": "False", "FS-12": true}
    UNKNOWN: []

**`UNKNOWN` rỗng — không Failure Signal nào còn UNKNOWN.** Và đạt ở nghĩa mạnh: không mục nào được
che bằng giá trị mặc định, mọi đại lượng đều có đường sinh ra thật. FS-06 nhận đúng **18** config
OFAT từ manifest Gate 2 (`n_adjacent = 18`, khớp số OFAT manifest sinh ra), `flip = false`.

Khối `failure_signal_inputs_wp_a5` trong run record ghi phạm vi + lý do của cả năm đại lượng WP-A5
chạm tới, nên nếu về sau một signal quay lại UNKNOWN thì record tự nói được vì sao.

**Chính run này phát hiện `F-S015-01`** (xem `PROJECT/PROJECT_PROGRESS.md` § RSK-007 và
`docs/sessions/S015-wp-a5-do-failure-signal.md` §6b): lần chạy TRƯỚC khi sửa kiểu ghi ra
`"FS-11": "False"` và `"FS-12": "True"` dạng **chuỗi** — dấu vết `numpy.bool_`, mà
`np.bool_(True) is True` cho `False`, nên signal đó vô hình với cờ chặn `any_true` của BT §17.
Bằng chứng trước/sau của lần chạy này: `FS-12` chuyển từ `"True"` (chuỗi) sang `true` (bool JSON)
sau khi WP-A5 ép kiểu tại `metrics.py`, trong khi `FS-11` **vẫn** là `"False"` — đúng ranh giới
phạm vi: phần WP-A5 sở hữu đã đóng, phần gốc trong `failure_signals.py` định tuyến sang `WP-B1`.
Mười signal còn lại giữ nguyên giá trị giữa hai lần chạy ⇒ sửa kiểu chỉ đổi KIỂU, không đổi một
kết luận nào.

Verdict của run: `DO_NOT_BUILD` (lý do: `Gate 1 FAIL`) — đúng như kỳ vọng trên dữ liệu tổng hợp và
KHÔNG phải verdict official (`DEC-003`; cờ `official = false` vì dữ liệu synthetic + dev_limit).

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-05 — FS-03 và FS-07 được tính trên toàn bộ chín window
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh phạm vi tính đã mở rộng khỏi W5, và phạm vi mới được ghi tường minh ở
`docs/CONVENTIONS.md`. Đóng F-016 phần đo lường.

Kết quả (S015). `test_a5_05_fs03_fs07_computed_over_nine_windows`: cả `concentration` và
`cash_ratio_stats` được tính trên **9/9 window**, và phép gộp trùng khớp `primary_median` tính
ĐỘC LẬP trong test (không gọi lại hàm của sản phẩm để tự xác nhận chính mình).
`test_a5_05_fs12_pooled_scope_covers_nine_windows`: FS-12 phủ 9 window, `share` không `None`, và
tổng khối lợi thế gộp bằng tổng lợi thế ròng từng window (phép CỘNG, không phải median).
`test_a5_05_missing_window_is_unknown_not_silently_dropped`: thiếu window (`None` hoặc `NaN`) →
`None` kèm TÊN window thiếu, không âm thầm bỏ window để "còn tính được".

**Mở rộng phạm vi KHÔNG phải thay đổi hình thức — nó làm FS-03 LẬT.**
`test_a5_05_nine_window_scope_differs_from_w5_only` khoá điều này lại. Số đo trên dữ liệu tổng hợp
2018-01→2026-06:

| Đại lượng | W5-only (trước) | 9 window PrimaryMedian (sau) | FS-03 |
|---|---|---|---|
| `ae_ex_month` | 100,637 | **96,046** | FALSE → **TRUE** |
| `ae_ex_quarter` | 101,170 | **95,251** | FALSE → **TRUE** |
| `cash_ratio.avg` (FS-07) | 0,16608 | **0,15347** | không đổi kết luận |

Tức trước WP-A5, một window đại diện đã **che mất** một Failure Signal đang TRUE. Đây đúng là hại
mà F-016 cảnh báo. Thay đổi này đến từ **DỮ LIỆU ĐO MỚI**, không từ chính sách mới — ngưỡng 100,0
trong `failure_signals.py` không bị đụng (xem CHECK-A5-07). Giá trị W5 cũ được giữ trong run record
dưới khoá `w5_only_legacy` để đối chiếu lịch sử. Phạm vi mới ghi tại `docs/CONVENTIONS.md` #20(d),
(e).

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-06 — Số đo FS-02 và FS-07 không bị bóp méo bởi vốn bị khoá
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chứng minh dependency WP-A3 đã thoả bằng một ca chạy kịch bản
CRASH → RECOVERY → STRESSED, khẳng định cap-hit share và cash ratio phản ánh vốn thực sự khả dụng,
không phải vốn bị treo. Đây là lý do WP-A5 phụ thuộc WP-A3.

Kết quả (S015). `test_a5_06_cap_hit_and_cash_see_released_capital` chạy một window thật
2021-01→2023-01 và khẳng định ba điều trên chính mẫu đo:
(1) không mẫu nào có `available` âm và `total >= available` — vốn không bị kế toán sai;
(2) tồn tại ít nhất một lần `available` **TĂNG** so với mẫu ngày trước đó. Đây là phép kiểm cốt
lõi: vốn được release sau recovery-end / huỷ zone phải QUAY LẠI số đo. Nếu F-001 chưa được WP-A3
sửa và vốn bị khoá vĩnh viễn trong `reserved`, chuỗi `available` sẽ đơn điệu giảm và test đỏ —
tức test này thực sự phụ thuộc vào WP-A3 đã DONE, đúng lý do dependency tồn tại;
(3) window đi qua **nhiều hơn một** regime (khẳng định tường minh trước khi kết luận, chặn "pass
rỗng" trên một ca không có chuyển regime nào), và `cash_ratio.avg` là số hữu hạn trong [0, 1].

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

### Scope / Regression

#### CHECK-A5-07 — Gói không thay đổi chính sách verdict
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: `git diff` chứng minh không đổi ngưỡng, không đổi ánh xạ gate-fail → verdict, không đổi
quy tắc UNKNOWN trong `verdict.py` / `failure_signals.py`. Nếu gói này vô tình làm verdict đổi kết
quả trên cùng dữ liệu, phải giải thích được rằng nguyên nhân là **dữ liệu đo mới**, không phải chính
sách mới.

Kết quả (S015). `git diff --stat b095874..HEAD -- src/eth_dca_os/verdict.py
src/eth_dca_os/failure_signals.py` → **output RỖNG**, hai file chính sách không đổi một dòng.
`test_a5_07_no_diff_in_policy_files` chạy đúng lệnh này trong test nên guard không phụ thuộc trí
nhớ người viết. Ngoài ra `test_a5_07_verdict_policy_thresholds_unchanged` khoá **HÀNH VI** ngưỡng
bằng cách gọi `evaluate_failure_signals` tại biên chứ không đọc văn bản mã nguồn: FS-02 tại
0,50/0,51; FS-12 tại 0,80/0,81; FS-03 tại 100,0/99,9; FS-07 tại cặp (0,30 & 102,0) với cả ba tổ
hợp biên. `test_a5_07_unknown_policy_untouched` khẳng định gọi hàm KHÔNG tham số vẫn cho đủ 12
signal và **tất cả** là `None` — tức WP-A5 không thêm giá trị mặc định nào vào đường UNKNOWN.

**Verdict CÓ ĐỔI trên cùng dữ liệu, và nguyên nhân là dữ liệu đo mới, không phải chính sách mới.**
Ba signal trước đây luôn UNKNOWN nay có giá trị (FS-02 = TRUE, FS-12 = TRUE trên dữ liệu tổng hợp),
và FS-03 lật FALSE → TRUE do phạm vi tính mở từ W5 ra 9 window (CHECK-A5-05). Cả ba đều đi qua
đúng ngưỡng cũ, không sửa. Đây chính là mục đích của gói: quy tắc chặn của BT §17 chỉ có hiệu lực
khi signal có dữ liệu để bật.

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-08 — Hành vi thực thi của engine không đổi vì việc thêm điểm thu thập số liệu
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, so metric của chiến lược trước–sau. Instrumentation không được làm
đổi hành vi.

Kết quả (S015). `test_a5_08_instrumentation_does_not_change_engine_behaviour` nạp `engine.py` tại
`b095874` (commit WP-A6 DONE, ngay TRƯỚC WP-A5) trực tiếp từ git bằng `load_engine_from_source` —
tiện ích do WP-A6 để lại — rồi chạy song song với engine hiện tại trên cùng dataset, cùng cửa sổ
2019-01-01 → 2022-01-01, cùng config. So sánh **bit-for-bit**: `eth_total` bằng nhau tuyệt đối,
`len(purchases)` bằng nhau, **từng bản ghi purchase** so bằng `==` trên cả dict (giá, ETH, tag,
regime, shortfall…), `counters` bằng nhau, `cash_samples` bằng nhau, `monthly_deployments` bằng
nhau. Test cũng khẳng định bản cũ **đúng là bản chưa có instrumentation**
(`opp_cap_samples`/`regime_timeline` rỗng) và bản mới có — nếu không, phép so sẽ vô nghĩa vì có thể
đang so hai bản giống hệt nhau.

Cơ chế bảo đảm: hai điểm thu thập chỉ ĐỌC property (`opp_fund.total/available`,
`mc.opportunity_cap`, `regime.regime`) và append vào list trên `RunResult`; không nhánh execution
nào đọc hai list đó. Chúng cũng không lọt vào harness thứ tự của WP-A6 (harness bọc phương thức
`Pool`/`Zone`/`Ladder`/`apply_fill`/`RegimeTracker.update`, không bọc phép đọc property), nên thứ
tự 18 bước đã khoá tại WP-A6 giữ nguyên — xác nhận thêm bằng CHECK-A5-09.

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

#### CHECK-A5-09 — Toàn bộ test suite Python PASS
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ; không test nào bị skip hoặc nới lỏng.

Kết quả (S015). `python -m pytest tests/ -q -p no:cacheprovider --durations=10`:
**330 test collected · 330 PASS · 0 FAIL · 0 ERROR · 0 skip/xfail · exit code 0.**
Đếm độc lập: `--collect-only` = 330 = **308 (nền trước WP-A5) + 22 (test mới của WP-A5)**;
`grep -cE "^(FAILED|ERROR)"` = 0.

Không test cũ nào bị sửa, nới lỏng hay skip — `git diff --stat b095874..HEAD -- tests/` chỉ có
**một file MỚI** (`test_wp_a5_failure_signal_instrumentation.py`). Các bộ test khoá hành vi engine
(`test_engine.py`, `test_wp_a3_lifecycle.py`, `test_wp_a4_*`, `test_wp_a6_processing_order.py`,
`test_wp_a7_*`, `test_e2e.py`, `test_cli.py`) PASS nguyên trạng — đặc biệt **22 test thứ tự 18
bước của WP-A6 vẫn xanh**, xác nhận hai điểm thu thập số liệu không lọt vào chuỗi side-effect mà
harness thứ tự quan sát.

`test_a1_09_reproducibility_same_seed_same_metrics` PASS (73,37 s) dù phiên có một commit
checkpoint (`75c79e5`) trong lúc suite chạy — lần này không tái hiện artefact `code_commit` đổi
giữa chừng đã gặp ở S014.

Executed By:
S015 (Opus 5, Tier C / xhigh)

Timestamp:
2026-09-03

## Exit Criteria
- [x] 100% REQUIRED checks PASS — **9/9** (CHECK-A5-01…09)
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ) — gói này không có check nào đòi E2
- [x] Phạm vi tính của từng Failure Signal được ghi ở `docs/CONVENTIONS.md` — quy ước **#20 (a)–(f)**
- [x] Không quyết định chính sách verdict nào được đưa ra trong gói này — `git diff` rỗng trên `verdict.py`/`failure_signals.py`; `F-S015-01` được định tuyến sang WP-B1 chứ không tự sửa
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật; RSK-007 được cập nhật — RSK-007 hạ từ "cao" xuống "trung bình", ghi phần dư và `F-S015-01`
- [x] Session handoff được viết — `docs/sessions/S015-wp-a5-do-failure-signal.md`
- [x] Không hạ REQUIRED check nào để đạt DONE — 9 check giữ nguyên câu chữ

## Escalation Triggers

- Một trong ba đại lượng không định nghĩa được rõ ràng từ spec → `CONFLICT DETECTED`: chốt quy ước
  và ghi vào `docs/CONVENTIONS.md`, hoặc chuyển sang WP-D2 nếu là khiếm khuyết đặc tả. **Không tự
  sáng tạo định nghĩa rồi im lặng.**
- Muốn "xử lý" một FS còn UNKNOWN bằng cách gán giá trị mặc định → DỪNG. Đó là quyết định chính
  sách, thuộc WP-B1, và mặc định hoá một tín hiệu chưa đo được chính là điều stopping rule tồn tại
  để chặn.
- WP-A3 chưa DONE mà vẫn muốn đo → `MISSING_INPUT`, giữ PLANNED. Số đo sẽ sai.
- Đo lường đòi đổi hành vi engine → `SCOPE_CHANGED`, mở `COMPLETION GATE CHANGE PROPOSAL`.

## Ảnh hưởng nếu gói này thất bại

GATE-A không đóng. Nếu bỏ qua và vẫn chạy official run: ba trong mười hai Failure Signal vĩnh viễn
UNKNOWN trên official run, và dữ liệu để đo chúng **không tồn tại ở đâu để tính lại**. Khi đó WP-B1
sẽ đứng trước lựa chọn giữa một verdict không đầy đủ hoặc chạy lại official run — mà Master Index §6
cấm chạy lại để cải thiện kết quả.

## Changed Files Registry

Created:
- (dự kiến) test mới trong `tests/`

Modified:
- (dự kiến) `src/eth_dca_os/pipeline.py`, `metrics.py`, `engine.py` (chỉ điểm thu thập)
- (dự kiến) `tests/`, `docs/CONVENTIONS.md`

Deleted:
- Không

Migration Impact:
- `pipeline_state.json` mang thêm trường; `ethdca verdict` đọc lại được nên WP-B1 sau này không cần chạy lại engine

## Notes

Backtest §17 nói rõ vì sao các Failure Signal quan trọng hơn chính các gate: "chỉ có khoảng ba block
dữ liệu độc lập ... Failure Signal chẩn đoán cơ chế và đáng tin hơn". Bỏ qua 3/12 signal rồi kết
luận BUILD là bỏ đúng phần bằng chứng mà spec coi là mạnh nhất. Gói này tồn tại để phần bằng chứng
đó **có dữ liệu**; việc nó **được dùng thế nào** là WP-B1.
