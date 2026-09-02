# WP-A4 — Xử lý đúng khi dữ liệu thiếu hoặc hỏng

## Metadata
Status:
DONE

Phase:
Phase 2 — Lớp A: bắt buộc sửa trước official run

Task Mode:
MAJOR

Lớp (RCP-001):
A — MUST FIX BEFORE OFFICIAL RUN · **nằm trên đường găng**

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)
AMENDED — 2026-09-01 bởi `OD-A4-01` (chủ dự án): thêm ĐÚNG MỘT REQUIRED check
`CHECK-A4-10`. Chín check FROZEN gốc giữ nguyên câu chữ và ngữ nghĩa; không check nào bị
hạ, gộp hay nới. Xem `docs/decisions/OWNER-DISPOSITION-2026-09-01-product-intent-va-integration.md`
§5.3 (đề xuất) và chỉ thị phiên S009 §0 (phê chuẩn).
AMENDED — 2026-09-01 bởi `DEC-016` / `OD-DATA-01` (chủ dự án): CAP-DATA REPAIR CYCLE #1
thêm ĐÚNG MỘT REQUIRED check `CHECK-A4-11` để đóng `F-S009-01`. Mười check trước đó giữ
nguyên câu chữ và ngữ nghĩa; không check nào bị hạ, gộp hay nới. Không phát sinh
`LEGACY_GATE_COMPATIBILITY_REQUIRED`.

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 3
B: 2
A: 3
X: 2
U: 2
V: 3
H: 2
C: 2
F: 3

Routing Categories:
none

Primary Agent Tier:
C

Primary Effort:
xhigh

Model Routing Score:
2.65

Effort Routing Score:
2.45

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
3/4

Blast Radius:
2/4

Project Profile:
PRODUCT

## Objective

Làm cho engine xử lý dữ liệu thiếu hoặc hỏng **đúng theo ngữ nghĩa của spec**, và làm cho mọi bản
ghi bị ảnh hưởng bởi lỗ hổng dữ liệu **tự khai báo điều đó**, thay vì chỉ được đếm ở một bộ đếm tổng.

## Vì sao gói này ở lớp A

Dữ liệu Binance thật **có gap**. Định nghĩa INVALID hiện hẹp hơn spec: code chỉ đặt INVALID khi
**cả 8** sub-factor thiếu, trong khi Strategy §3 nói INVALID khi "giá/lịch sử ETH **hoặc indicator
bắt buộc** không hợp lệ" (F-023). Nghĩa là trên dữ liệu thật, engine sẽ tiếp tục hành động ở những
thời điểm mà spec yêu cầu dừng — và điều đó **đổi hành vi ngay trong official run**, không sửa lại
được sau.

Song song, `EXECUTION_DATA_GAP` không tồn tại trong `src/` (F-025) và `DELAYED_DATA_FILL` chỉ là bộ
đếm, không gắn tag lên purchase record như BT §18 mô tả (F-032). Hệ quả: sau official run không ai
truy được **bản ghi nào** bị ảnh hưởng bởi gap, chỉ biết **có bao nhiêu**.

## Đóng finding

- F-023 — định nghĩa INVALID hẹp hơn Strategy §3
- F-025 — tag `EXECUTION_DATA_GAP` cho nến 15m thiếu không tồn tại
- F-032 — `DELAYED_DATA_FILL` chỉ là bộ đếm, không gắn tag lên purchase record
- **F-E2A1R3-05** — fetch bị cắt cụt vẫn đủ tư cách official; `missing_count` không phát
  hiện truncation. Được chủ dự án gán cho `CAP-DATA` và **hấp thụ** vào WP-A4 ngày
  2026-09-01 (`OD-A4-01`). Không tạo task ID mới — finding ≠ task.
- **F-S009-01** — indicator daily tính theo VỊ TRÍ HÀNG, nên một ngày lịch thiếu làm
  `return7` / rolling trả một số HỮU HẠN SAI mà không NaN, không DEGRADED, không INVALID.
  Được chủ dự án gán cho `CAP-DATA` (`DEC-015`) và thi hành bằng **CAP-DATA REPAIR CYCLE
  #1** trên chính WP-A4 (`DEC-016`). Không tạo task ID mới — finding ≠ task.

## Scope

- `src/eth_dca_os/score.py` — định nghĩa INVALID / DEGRADED
- `src/eth_dca_os/engine.py` — gắn tag lên bản ghi, hành vi khi dữ liệu INVALID
- `tests/` — test ngữ nghĩa dữ liệu xấu, test data gap
- `docs/CONVENTIONS.md` — ghi rõ danh sách "indicator bắt buộc" nếu spec để ngỏ

## Out of Scope

- Vòng đời regime và ladder — đó là **WP-A3** (phải xong trước)
- Thứ tự 18 bước — đó là **WP-A6**
- Đo Failure Signal — đó là **WP-A5**
- Sửa nguồn dữ liệu hoặc lấp gap bằng dữ liệu tự sinh
- Đổi công thức OSCORE hay trọng số sub-factor

## Dependencies
- T-04 (DONE)
- **WP-A3** (DONE) — tuần tự hoá vì cùng sửa `engine.py`, và vì hành vi khi dữ liệu xấu phải khoá
  vào vòng đời regime đã sửa

## Blocks
- WP-A6 (test thứ tự phải khoá vào hành vi cuối cùng)
- WP-C4 (không khoá parity vào hành vi sắp đổi)
- GATE-A → T-06

## Parallel-Safe With
- WP-A1, WP-A2, WP-C1, WP-D1, WP-D2
- **WP-A7** — song song **về roadmap** (không có phụ thuộc ngữ nghĩa; WP-A4 sở hữu ST §3 / BT §18,
  WP-A7 sở hữu DM §5 / ST §4-§6-§12). Ba điều kiện bắt buộc do **RCP-002** (2026-08-24) đặt ra:
  1. Test của WP-A4 phải **assert tiền đề không suy biến** nếu requirement cần Smart ladder tồn
     tại (bài học F-E2-01 của S003) — nếu không, test sẽ chứng minh ít hơn narrative của nó.
  2. **Không hard-code** kỳ vọng VND/ETH nhiều tháng phụ thuộc vào hành vi lỗi F-035.
  3. Thao tác trên `engine.py` phải được **tuần tự hoá khi merge**: "parallel" là roadmap
     parallelism, KHÔNG cho phép hai agent đồng thời sửa/merge cùng vùng `engine.py` mà không có
     branch isolation và merge ordering rõ ràng.

## Expected Touch Area

Allowed:
- `src/eth_dca_os/score.py`, `engine.py`
- `tests/`
- `docs/CONVENTIONS.md`
- (làm rõ bởi `OD-A4-01`, 2026-09-01) `src/eth_dca_os/data/dataset.py`, `fetch.py`,
  `synth.py` — **chỉ** phần ngữ nghĩa coverage/gap và khai báo khoảng thời gian được yêu cầu
- (mở rộng tối thiểu bởi `DEC-016`, 2026-09-01, CAP-DATA REPAIR CYCLE #1)
  `src/eth_dca_os/indicators.py` — **chỉ** phần ngữ nghĩa cửa sổ theo ngày lịch, cộng
  wiring/test trực tiếp bắt buộc. Thẩm quyền này KHÔNG cho phép viết lại indicator
  subsystem, thiết kế lại kiến trúc dataset, đổi time-series engine, dọn mã không liên
  quan, hay xử lý hardening

Do not touch without Scope Expansion:
- `src/eth_dca_os/regime.py`, `ladders.py`, `capital.py`, `verdict.py`, `failure_signals.py`
- **Cơ chế LẤY dữ liệu** trong `src/eth_dca_os/data/`: HTTP, retry, rate-limit, lựa chọn
  nguồn archive/REST, kiến trúc `fetch_all`. Câu loại trừ gốc ("gói này xử lý **ngữ nghĩa**
  dữ liệu xấu, không xử lý việc **lấy** dữ liệu") được `OD-A4-01` đọc đúng như nó viết:
  loại trừ là về CƠ CHẾ LẤY, KHÔNG phải về NGỮ NGHĨA COVERAGE. Ngữ nghĩa coverage / gap /
  đối chiếu khoảng được yêu cầu nằm TRONG phạm vi.
- `webapp/`, `docs/spec/`

## Subtasks
- [x] A4.1 Xác định danh sách "indicator bắt buộc" theo Strategy §3; ghi vào CONVENTIONS nếu spec để ngỏ
- [x] A4.2 Siết định nghĩa INVALID cho khớp §3: giá/lịch sử ETH **hoặc** indicator bắt buộc không hợp lệ
- [x] A4.3 Khẳng định INVALID chặn tạo action mới ở tầng engine
- [x] A4.4 Gắn tag `EXECUTION_DATA_GAP` lên bản ghi bị ảnh hưởng theo BT §18
- [x] A4.5 Gắn tag `DELAYED_DATA_FILL` lên purchase record, không chỉ đếm
- [x] A4.6 Viết test cho từng ca dữ liệu xấu, gồm ca biên giữa DEGRADED và INVALID
- [x] A4.7 Định lượng thay đổi kết quả mô phỏng trên dataset tổng hợp **có gap**
- [x] A4.8 (CAP-DATA REPAIR CYCLE #1, `DEC-016`) Neo cửa sổ indicator daily vào NGÀY LỊCH; ngày thiếu phải ra NaN → DEGRADED/INVALID, không ra số hữu hạn sai

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] **Dependency WP-A3 DONE** — xác nhận tại S009: WP-A3 DONE từ S003
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §3; BT §1, §18
- [x] Data impact được biết — **gói này làm đổi hành vi engine trên dữ liệu có gap**
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] Xác nhận lại toàn bộ Ready Gate khi mở task — S009, 2026-09-01

## Completion Gate

Risk = 3 → E1 bắt buộc cho mọi REQUIRED check kiểm chứng được.

Nguyên tắc bằng chứng riêng của gói này: mọi mệnh đề về hành vi phải được chứng minh trên **dataset
có gap thật sự**, không phải trên dataset sạch rồi suy luận.

### Functional / Data Semantics

#### CHECK-A4-01 — Định nghĩa INVALID khớp Strategy §3, không còn đòi thiếu cả 8 sub-factor
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu gốc (giữ nguyên): bảng ca kiểm thử phủ đủ ba nhóm — (a) giá/lịch sử ETH không hợp lệ,
(b) một indicator bắt buộc không hợp lệ, (c) chỉ các sub-factor không bắt buộc thiếu.

Thực hiện: `tests/test_wp_a4_bad_data_semantics.py::A4_01_CASES` — bảng 15 ca, chạy qua
`compute_scores` thật (không mock), mỗi ca khẳng định `data_quality` VÀ trạng thái NaN của
`oscore`:

| Nhóm | Ca | Kỳ vọng |
|---|---|---|
| (a) giá/lịch sử ETH | `close=NaN`, `close=0`, `close<0` | INVALID |
| (b) indicator bắt buộc | `return7=NaN`, `adr30=NaN`, `adr30=inf` | INVALID |
| (c) sub-factor không bắt buộc | `volume_ratio`, `rsi14`, `dd365`, `ma_ratio`, `percentile365`, `ethbtc_return30`, `ethbtc_percentile180`, và ca ba sub-factor cùng thiếu | DEGRADED |
| đối chứng dương | đủ hết | GOOD |

Ca biên đóng đúng khoảng cách của F-023 —
`test_a4_01_old_definition_would_have_missed_group_b`: thiếu `return7` chỉ làm **2/8**
sub-factor NaN, nên luật CŨ đọc là DEGRADED (test khẳng định điều đó bằng
`factor_scores(sf)` không truyền `ind`) trong khi luật MỚI đọc là INVALID. Nếu ai hoàn
nguyên định nghĩa, test đỏ.

Danh sách "indicator bắt buộc" (`close`, `return7`, `adr30`) được chốt ở
`score.REQUIRED_DAILY_INDICATORS` và ghi ở `docs/CONVENTIONS.md` §"Indicator daily bắt
buộc"; `test_a4_01_required_indicator_list_is_declared_once` khoá hai nơi đó không lệch nhau.
Fail-closed khi cột bắt buộc vắng mặt: `test_a4_01_missing_required_column_is_fail_closed`.

Đóng **F-023**.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-02 — Dữ liệu INVALID chặn tạo action mới ở tầng engine
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Thực hiện: `test_a4_02_invalid_blocks_new_actions_in_engine` — chạy `run_engine` THẬT trên
hai kịch bản giống hệt nhau, khác đúng một biến `data_quality` tại cú dip có trigger.

- đối chứng dương (`GOOD`): CÓ purchase SMART/OPPORTUNITY/CRASH sau thời điểm dip;
- `INVALID`: KHÔNG purchase nào, `counters["triggered_actions"] == 0`.

Đối chứng dương là bắt buộc: thiếu nó, một engine không bao giờ mua cũng "qua" được check.
Cửa sổ so sánh được cắt từ 07:00 local ngày trạng thái có hiệu lực — zone S0 chạm giá ngay
Day 1 ở CẢ HAI kịch bản khi dữ liệu còn GOOD, gộp nó vào sẽ làm mệnh đề sai chứ không mạnh hơn.

`test_a4_02_block_is_temporal_not_permanent`: chỉ RIÊNG ngày dip là INVALID → không action
nào trong ngày đó, nhưng khi dữ liệu tốt trở lại engine hoạt động bình thường. Hai vế cùng
cần: vế đầu chứng minh cổng ĐÓNG, vế sau chứng minh nó không đóng vĩnh viễn.

`test_a4_02_base_schedule_still_runs_when_invalid`: §3 nói "Base schedule vẫn có thể chạy
theo fallback được ghi nhận" — INVALID không được biến thành đứng im hoàn toàn.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-03 — Tag `EXECUTION_DATA_GAP` được gắn lên bản ghi bị ảnh hưởng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Thực hiện trên dataset CÓ GAP THẬT (xoá nến khỏi series 15m rồi chạy `run_engine`, không
suy luận từ dataset sạch).

`test_a4_03_execution_data_gap_tag_on_affected_record`: xoá 10:00–11:45 local ngày Base
(8 nến). Nến 12:00 vẫn tồn tại nên tranche chạy đúng giờ, nhưng nó là nến hợp lệ ĐẦU TIÊN
sau lỗ hổng. Test đọc BẢN GHI và khẳng định `tags` chứa `EXECUTION_DATA_GAP`,
`missing_candles_before == 8`, và KHÔNG có `DELAYED_DATA_FILL` (không phải fill trễ).

`test_a4_03_clean_dataset_has_no_gap_tag` (đối chứng âm): dataset liên tục không sinh tag
nào và `missing_candles_before == 0` ở mọi bản ghi — nếu tag xuất hiện ở đây thì nó vô nghĩa.

Đẳng thức bộ đếm ↔ số bản ghi mang tag được khoá theo cả hai chiều: "có bộ đếm là đủ" bị
bác bỏ bằng chính test.

Đóng **F-025**.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-04 — Tag `DELAYED_DATA_FILL` được gắn lên purchase record
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Thực hiện: `test_a4_04_delayed_data_fill_tag_on_purchase_record` — xoá 12:00–12:45 local
ngày Base, tức nến 12:00 nằm TRONG gap. Tranche execute ở nến hợp lệ đầu tiên sau đó
(12:45, kiểm bằng `(ts + TZ) % DAY == 12.75*3600`), đúng ST §9 [F3].

Test đọc BẢN GHI: `source == "BASE"`, `reason == "BASE_SCHEDULE"`, `tags` chứa
`DELAYED_DATA_FILL`. Bộ đếm `counters["delayed_data_fill"]` vẫn còn nhưng không còn là
nguồn thông tin duy nhất.

Đóng **F-032**.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-05 — [F3] Base tranche không bao giờ bị bỏ vì gap dữ liệu
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Thực hiện: `test_a4_05_base_tranche_never_dropped_because_of_gap` — xoá TRỌN ngày Day 23
và TRỌN các cửa quét Month-End (Day 25–28), nên tranche Day 23 chỉ còn một đường sống sót:
giải ngân khi sang accounting month mới.

Khẳng định: có bản ghi mang `DELAYED_DATA_FILL` với `reason == "MONTH_END_BASE"`, và tổng
nominal BASE trên dataset CÓ GAP **bằng đúng** tổng nominal BASE trên cùng kịch bản KHÔNG
gap (so sánh trực tiếp hai lần chạy, không hard-code con số — tránh khoá kỳ vọng vào một
giá trị có thể trôi vì lý do khác).

Đối chứng: `test_a4_05_base_budget_intact_on_clean_dataset` khẳng định dataset sạch không
sinh `DELAYED_DATA_FILL` nào.

Xác nhận độc lập ở tầng mô phỏng đầy đủ (CHECK-A4-07): nominal BASE = 600.0 ở CẢ BEFORE và
AFTER trên dataset có gap. Mệnh đề 13 của Impl Plan §7 chuyển từ "xác nhận ở tầng code,
không có test" lên **E1**.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-06 — DEGRADED không đẩy score lên; Opportunity unlock không tăng do đầu vào DEGRADED
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Thực hiện: hai bộ test tham số hoá trên CẢ TÁM input sub-factor
(`test_a4_06_degraded_never_pushes_score_up`,
`test_a4_06_opportunity_unlock_not_increased_by_degraded_input`).

Với mỗi sub-factor bị thiếu: `oscore(DEGRADED) <= oscore(GOOD)` và
`opportunity_unlock(oscore_DEGRADED) <= opportunity_unlock(oscore_GOOD)`. Ca nào rơi vào
INVALID (thiếu indicator bắt buộc) được CHECK-A4-01 phủ, không bị nuốt im lặng.

`test_a4_06_degraded_contribution_is_exactly_zero_not_rescaled`: sub-component thiếu đóng
góp ĐÚNG 0, `market_stress_score == 30*(0.5*R + 0.3*S7)` — không rescale, không chuẩn hoá
lên (BT §21.1).

Sau khi siết định nghĩa INVALID, ranh giới DEGRADED KHÔNG bị nới theo hướng có lợi cho
strategy: bảng CHECK-A4-01 khẳng định 8 ca sub-factor không bắt buộc vẫn là DEGRADED, đúng
như trước, và số ngày GOOD trên dataset đo ở CHECK-A4-07 không đổi (210 → 210).

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-07 — Thay đổi kết quả mô phỏng trên dataset có gap được định lượng và giải thích
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Thực hiện: cùng seed, cùng file parquet, cùng config (`BASELINE_STRATEGY` +
`GATE1_LOW_FRICTION`), cửa sổ 2020-01-01…2021-01-01. BEFORE = `06b381c` (git worktree
riêng), AFTER = HEAD phiên này. Chi tiết và bảng đầy đủ:
`docs/sessions/S009-wp-a4-ngu-nghia-du-lieu-xau.md` §6.

Dataset có gap được dựng bằng cách khoét ba loại lỗ hổng vào dataset synth, mỗi loại ứng
với một điều khoản: 108 nến 15m (gồm khung 12:00 ba ngày Base + hai cửa sổ bảo trì 6h/18h),
19 dòng daily BTC, 7 dòng daily ETH có `close` không hợp lệ.

| Metric | BEFORE | AFTER | Quy về |
|---|---|---|---|
| INVALID (ngày) | 0 | 37 | ST §3 — 7 ngày `close` hỏng + 30 ngày `adr30` NaN kế tiếp |
| `oscore` NaN | 0 | 37 | DM §4 |
| DEGRADED | 156 | 119 | 37 ngày chuyển sang INVALID |
| GOOD | 210 | 210 | không nới ranh giới |
| triggered/executed actions | 17 | 13 | ST §3 "chặn mọi action Smart/Opportunity mới" |
| `n_purchases` | 65 | 61 | hệ quả |
| `eth_total` | 2.1983245965 | 2.1941171636 | −0.19%, cùng số tiền, khác thời điểm/giá |
| nominal BASE | 600.0 | 600.0 | ST §9 [F3] — Base không bị bỏ |
| nominal SMART | 520.0 | 520.0 | vốn bị chặn ở zone được settle theo ST §10 |
| bản ghi mang tag | 0 | 3 | BT §18 — F-025, F-032 |
| `execution_data_gap` | (không có) | 3 | BT §18 |

Mọi sai lệch đều quy được về một điều khoản spec; không còn sai lệch dư.

Kiểm soát drift nền: trên dataset synth **không** khoét lỗ, cùng cửa sổ, cùng seed, BEFORE
và AFTER trùng khớp từng chữ số (`eth_total = 2.1995839535`, 65 purchase, 366 ngày GOOD).
Thay đổi hành vi chỉ xuất hiện đúng ở nơi dữ liệu xấu.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

#### CHECK-A4-08 — Toàn bộ test suite Python PASS; không test nào bị nới lỏng hoặc skip
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Output đầy đủ, chạy tại `/home/user/coin`, Python 3.11, pandas 3.0.5:

```
$ python -m pytest -q
........................................................................ [ 31%]
........................................................................ [ 62%]
........................................................................ [ 93%]
................                                                         [100%]
[exited with code 0]
```

**232 test PASS, 0 FAIL, 0 SKIP, 0 XFAIL.** Trước gói này suite có 157 test; 75 test mới
được thêm (57 ở `test_wp_a4_bad_data_semantics.py`, 18 ở
`test_wp_a4_requested_range_coverage.py`).

Không test hiện có nào bị nới lỏng hoặc skip — mệnh đề này được chứng minh bằng git chứ
không bằng lời:

```
$ git status --short tests/
?? tests/test_wp_a4_bad_data_semantics.py
?? tests/test_wp_a4_requested_range_coverage.py
?? tests/wp_a4_fetch_stub.py

$ git diff --stat -- tests/
(rỗng)

$ grep -rn "skip\|xfail" tests/*.py
(rỗng)
```

Tức: **không một file test cũ nào bị sửa** (chỉ thêm file mới), và toàn repo không có một
marker `skip`/`xfail` nào. Hành vi engine ĐÃ đổi (CHECK-A4-07 định lượng), nhưng không test
cũ nào phải sửa theo — vì các test cũ chạy trên dataset không có ngày INVALID.

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

### Dataset Completeness — bổ sung bởi `OD-A4-01` (2026-09-01)

Check dưới đây do chủ dự án phê duyệt qua COMPLETION GATE CHANGE PROPOSAL, TRƯỚC khi
implementation bắt đầu. Nó là REQUIRED check thứ CHÍN và là bổ sung DUY NHẤT; không check
FROZEN nào bị sửa, hạ hay gộp.

#### CHECK-A4-10 — Độ phủ được đối chiếu với khoảng thời gian ĐƯỢC YÊU CẦU, không chỉ với khoảng quan sát được
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Câu chữ Owner phê duyệt: *"Coverage phải được đối chiếu với khoảng thời gian ĐƯỢC YÊU CẦU
(start/end), không chỉ với khoảng thời gian quan sát được trong dữ liệu đã fetch."*
Đóng **F-E2A1R3-05**. V1 BLOCKING theo DEC-011 vì chạm A (CORRECT DECISION), D (REAL MARKET
DATA), F (OFFICIAL RESULT VALIDITY).

**Counterexample production-realistic.** Đi theo đường sản xuất bình thường
(`fetch_all` → `build_lineage` → `official_eligibility` → `Prepared`), chỉ lớp HTTP được
thay bằng stub dựng trên mã production thật và tham số production thật — nguồn canonical
1 + 2 của `PROJECT/PRODUCTION_PATHS.md` §3. KHÔNG sửa tay `lineage.json`, KHÔNG mock
eligibility/loader/verifier, KHÔNG input thù địch.

Kịch bản: `--start 2020-01-01 --end 2021-01-01`; archive chỉ có tới tháng 2020-01; REST bị
chặn (BLK-001).

BEFORE (`06b381c`):

```
ETHUSDT_1d   binance_bulk_archive  rows=31     missing_count=0  last=2020-01-31
BTCUSDT_1d   binance_bulk_archive  rows=31     missing_count=0  last=2020-01-31
ETHUSDT_15m  binance_bulk_archive  rows=38016  missing_count=0  last=2020-01-31
official_eligibility -> (True, 'verified')
```

Thiếu 91,5% khoảng được yêu cầu, tự khai `missing_count = 0`, đủ tư cách official.

AFTER (cùng lệnh, cùng stub):

```
ETHUSDT_1d   missing_count=335   BTCUSDT_1d missing_count=335   ETHUSDT_15m missing_count=32160
official_eligibility -> (False, 'incomplete_coverage:ETHUSDT_1d=31/366 head=0 internal=0 tail=335')
Prepared.official_eligible = False
```

**CASE A–F** (`tests/test_wp_a4_requested_range_coverage.py`, 18 test):

| Case | Kịch bản | Kết quả |
|---|---|---|
| A | phủ đủ khoảng yêu cầu | **PASS** — `(True, 'verified')`, `missing_count = 0` cả ba series |
| B | thiếu phần ĐẦU (archive chưa có tháng 01, REST chỉ có từ tháng 02) | **FAIL completeness** — `missing_head > 0`, `incomplete_coverage:ETHUSDT_1d` |
| C | thiếu phần ĐUÔI (archive trễ, REST bị chặn) | **FAIL completeness** — `missing_tail > 0`, `missing_head == 0` |
| D | gap NỘI BỘ lớn (khoét 20 ngày giữa), hai đầu phủ đủ | **FAIL completeness** — `missing_internal == 20`, head = tail = 0 |
| E | quan sát được LIÊN TỤC nhưng chỉ phủ 31/366 ≈ 8,5% | **FAIL completeness** — `missing_internal == 0`, `missing_count == 335`, lý do mang số đo `31/366` |
| F | dataset đầy đủ, hợp lệ | **KHÔNG REGRESSION** — `(True, 'verified')` qua đúng đường positive control mà contract WP-A1 đã đóng băng dùng |

**Hệ quả ở tầng quyết định.** `test_truncated_dataset_cannot_become_an_official_run`:
`Prepared.official_eligible is False` và `official_reason` bắt đầu bằng
`incomplete_coverage:`. `Prepared` là nơi DUY NHẤT mọi gate lấy cờ `official`
(WP-A1/A1.2), nên dataset cắt cụt không thể đi tiếp như dataset official để tạo daily
decision. Fail closed, fail visibly — lý do mang theo số đo.

**Fail-closed khi thiếu khai báo.** `coverage_undeclared:<series>` khi lineage không khai
được khoảng yêu cầu; `lineage_malformed` khi trường độ phủ sai kiểu.
`build_lineage` mang theo khai báo cũ khi dựng lại từ file trên đĩa — đánh rơi nó là mất
provenance, và mất provenance ở đây là mất luôn khả năng phát hiện cắt cụt.

**Không mở lại bề mặt WP-A1 vừa đóng.** Chữ ký `official_eligibility(raw_dir, lineage)`
giữ nguyên (`test_official_eligibility_signature_unchanged`); khoảng yêu cầu đi qua
LINEAGE, không qua tham số mới của cổng. `dataset_hash` không đổi
(`test_dataset_hash_is_unchanged_by_coverage_fields`), nên run record và `manifest_hash` cũ
không trôi.

**Ngưỡng.** `MAX_MISSING_RATIO = 0.01`, ghi ở `docs/CONVENTIONS.md`. Không đặt bằng 0 vì
dữ liệu Binance thật có gap bảo trì; `test_intentional_synth_gap_still_detected_and_tolerated`
khoá CẢ HAI phía của ngưỡng (gap 4 nến cố ý vẫn bị phát hiện, và vẫn dưới ngưỡng).

Executed By:
S009 — agent phiên WP-A4 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

### Calendar Semantics — bổ sung bởi `DEC-016` / `OD-DATA-01` (2026-09-01)

Check dưới đây do chủ dự án phê duyệt qua `DEC-016` khi mở **CAP-DATA REPAIR CYCLE #1**.
Nó là REQUIRED check thứ MƯỜI MỘT và là bổ sung DUY NHẤT của chu kỳ này; không check nào
trong mười check trước bị sửa, hạ hay gộp. Chỉ thị mở chu kỳ ghi rõ: "Bổ sung đúng
REQUIRED check cần thiết cho repair này. Không thêm nhiều gate hơn cần thiết."

#### CHECK-A4-11 — Indicator daily không âm thầm dùng row-position semantics khi thiếu ngày lịch bắt buộc
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Câu chữ chủ dự án phê duyệt: *"Nếu một daily candle bắt buộc bị thiếu, indicator bị ảnh
hưởng phải được tính đúng theo calendar semantics, HOẶC bị DEGRADED / INVALID / NaN theo
spec, nhưng KHÔNG được trả một giá trị hữu hạn sai rồi tiếp tục như dữ liệu bình thường."*
Đóng **F-S009-01**. V1 BLOCKING theo `DEC-011` vì chạm A (CORRECT DECISION), D (REAL MARKET
DATA), F (OFFICIAL RESULT VALIDITY) — `DEC-015`, `DEC-016`.

**BEFORE — tái lập trên đường sản xuất bình thường, KHÔNG sửa tay artifact.**
`fetch_all` (stub CHỈ thay lớp HTTP — nguồn canonical 1 + 2 của `PRODUCTION_PATHS.md` §3)
→ `build_lineage` → `official_eligibility` → `Prepared` → `compute_daily_indicators`.
Yêu cầu `--start 2019-01-01 --end 2020-01-01`; archive thiếu đúng một ngày (2019-07-15).
Không mock eligibility, loader hay indicator; không input thù địch.

```
--- FULL DAILY SERIES ---
  ETHUSDT_1d rows=365/365 missing=0 ratio=0.0000%
  official_eligibility -> (True, 'verified')
--- SAME SERIES, ONE CALENDAR DAY REMOVED (2019-07-15) ---
  ETHUSDT_1d rows=364/365 missing=1 ratio=0.2740%
  official_eligibility -> (True, 'verified')
  2019-07-15 có trong index indicators? False        <- ngày thiếu BIẾN MẤT khỏi chỉ mục

đọc tại 2019-07-20        FULL (đúng theo lịch)        GAP (engine trả về)     NaN?
  return7                 6.98993449431e-05           7.98857633582e-05       False
  ethbtc_return30        -3.33066907388e-16          -1.11022302463e-16       False
  adr30                   9.98646841002e-06           1.03194055464e-05       False
  rsi14                       99.9018663068               99.8996490166       False
  ma200                          130.378014                  130.383227       False

  data_quality = 'DEGRADED'   oscore = 9.928762762751692   invalid_mask = False
  Prepared.official_eligible = True ('verified')
```

Cơ chế đo trực tiếp: tại 2019-07-20, phần tử `i-7` của chuỗi CÓ GAP là **2019-07-12**,
trong khi lịch đòi **2019-07-13**. Năm indicator sai, không cái nào NaN, ngày vẫn đi tiếp
như dữ liệu bình thường.

**AFTER — cùng lệnh, cùng stub, cùng dữ liệu.**

```
  2019-07-15 có trong index indicators? True         <- ngày thiếu HIỆN RA thành hàng NaN
  return7                 6.98993449431e-05           6.98993449431e-05       False  <- ĐÚNG
  ethbtc_return30        -3.33066907388e-16          -3.33066907388e-16       False  <- ĐÚNG
  adr30                   9.98646841002e-06                         nan       True
  rsi14                       99.9018663068                         nan       True
  ma200                          130.378014                         nan       True

  phần tử i-7 của chuỗi CÓ GAP = 2019-07-13 == lịch đòi 2019-07-13
  data_quality = 'INVALID'   oscore = nan   invalid_mask = True
```

Hai vế của điều khoản đều được thoả, và thoả ĐÚNG CHỖ: indicator nào còn đủ đầu vào lịch
(`return7`, `ethbtc_return30` — chỉ đọc `D` và `D-7`/`D-30`) được tính **đúng**; indicator
nào có cửa sổ phủ ngày thiếu trả **NaN** → INVALID qua `score.invalid_mask` sẵn có. Không
còn giá trị hữu hạn sai nào.

**CASE A–H** — `tests/test_wp_a4_calendar_indicator_semantics.py`, 54 test, chạy trên hàm
production `compute_daily_indicators` / `compute_scores` / `invalid_mask`:

| Case | Kịch bản | Kết quả |
|---|---|---|
| A | chuỗi daily liên tục, đầy đủ | **PASS** — chỉ mục không sinh thêm hàng; 8 indicator khớp oracle tính theo NHÃN NGÀY tới `rel=1e-12` |
| B | thiếu đúng MỘT ngày trong cửa sổ `return7` | **PASS** — không indicator nào hữu-hạn-mà-sai; cửa sổ phủ gap → NaN; ngày thiếu hiện ra trong chỉ mục |
| C | thiếu một ngày NGOÀI cửa sổ đang đọc | **PASS** — `return7`/`adr30` giữ nguyên giá trị đúng; ngày đọc KHÔNG bị INVALID oan; bóng INVALID chặn ở đúng cửa sổ REQUIRED dài nhất (30), khoá cả hai phía |
| D | lỗ hổng NHIỀU ngày (3 ngày liền) | **PASS** — mọi ngày thiếu INVALID; ngày đọc INVALID; không giá trị hữu hạn sai |
| E | gap ở BIÊN ĐẦU cửa sổ | **PASS** — gap đúng `D-7` → `return7` NaN; gap `D-8` → `return7` vẫn đúng (khoá off-by-one). Tương tự `D-30`/`D-31` cho `ethbtc_return30` |
| F | gap ở BIÊN CUỐI / vùng hiện tại | **PASS** — gap trên chính ngày đọc → `close` NaN + INVALID; gap `D-1` không sinh giá trị hữu hạn sai; thiếu ở ĐUÔI không bị hàm này đoán thêm ngày (độ phủ hai đầu vẫn là việc của CHECK-A4-10, không dựng lại) |
| G | đối chứng dương, dữ liệu SẠCH | **PASS** — 13 cột khớp **từng bit** với công thức row-position cũ (`np.array_equal(..., equal_nan=True)`), cộng `percentile365` và `rsi14`; tập ngày INVALID không trôi (chỉ warm-up 30 ngày đầu) |
| H | tích hợp `Prepared` / `invalid_mask` | **PASS** — ngày bị ảnh hưởng có `data_quality = INVALID`, `oscore = NaN`, nên không tạo được quyết định official; và test đối chứng ghi lại rằng luật CŨ cho chính ngày đó một `oscore` hữu hạn với `invalid_mask = False` |

**Đường hệ quả dùng lại cơ chế đã có, không dựng hệ validity thứ hai** (`DEC-016` cấm):
`test_case_h_required_indicator_nan_is_what_drives_invalid` khẳng định INVALID đến từ
`score.REQUIRED_DAILY_INDICATORS` sẵn có (`close`, `return7`, `adr30`) chứ không từ một
cờ mới. `indicators.py` không thêm trường trạng thái nào.

**Non-regression ở tầng QUYẾT ĐỊNH trên dataset SẠCH** (§11 của chỉ thị mở chu kỳ) — chạy
`run_engine` thật, cùng seed, cùng parquet, `BASELINE_STRATEGY` + `GATE1_LOW_FRICTION`,
cửa sổ 2020-01-01…2021-01-01:

| Đầu ra quyết định | BEFORE | AFTER | |
|---|---|---|---|
| `eth_total` | 2.1967521311211984 | 2.1967521311211984 | không đổi |
| `n_purchases` | 66 | 66 | không đổi |
| nominal BASE / SMART / CRASH / OPPORTUNITY | 600.0 / 520.0 / 14.1027503435 / 0.2633261223 | y hệt | không đổi |
| `triggered` / `executed` / `base_early` | 18 / 18 / 2 | 18 / 18 / 2 | không đổi |
| `cooldown_override` | STRESSED 4 | STRESSED 4 | không đổi |
| nhãn regime (CRASH/NORMAL/STRESSED) | 140 / 169 / 57 | 140 / 169 / 57 | không đổi |
| `data_quality` | GOOD 366 | GOOD 366 | không đổi |
| tổng `oscore` | 8509.33685713 | 8509.33685713 | không đổi |

Decision output trên dữ liệu sạch **không trôi một chữ số nào**.

**Bóng của MỘT ngày lịch thiếu — đo, không suy luận.** Dataset synth 2018-01-01…2021-01-01,
bỏ đúng 2020-06-15:

- **Không hồi tố:** 896 ngày TRƯỚC ngày thiếu khớp từng bit trên MỌI cột. Bản sửa chỉ tác
  động từ ngày thiếu trở đi.
- Bóng NaN theo cột: `return7` 2 ngày (chính ngày đó và `D+7`), `ethbtc_return30` 2 ngày,
  `rsi14` 15 ngày (Wilder warm-up lại sau khi chuỗi đứt), `adr30` 31 ngày,
  `volume_ratio` 90, `ethbtc_percentile180` 180, `ma200`/`high365`/`percentile365` 200
  (tới hết dataset — cửa sổ 200/365 ngày).
- Ở tầng quyết định trên cùng dataset có gap: BEFORE = 365 ngày GOOD, 0 INVALID, 0 `oscore`
  NaN — ngày thiếu **hoàn toàn vô hình**. AFTER = 31 INVALID (2020-06-15 → 2020-07-15, đúng
  cửa sổ `adr30`), 169 DEGRADED, 166 GOOD; `nominal` BASE 600.0 và SMART 520.0 **không đổi**
  (ST §9 [F3] — vốn không bị bỏ), CRASH/OPPORTUNITY về 0 vì `oscore` thấp hơn khi
  sub-component thiếu — đúng chiều bảo thủ mà CHECK-A4-06 đã khoá ("DEGRADED không đẩy
  score lên").

Escalation trigger "siết định nghĩa làm engine dừng phần lớn thời gian" **KHÔNG kích hoạt**:
INVALID = 31/366 ≈ 8,5%, và toàn bộ vốn BASE + SMART vẫn được giải ngân đủ.

**`MAX_MISSING_RATIO` KHÔNG bị sửa.** Vẫn `= 0.01` trong `data/dataset.py`; không bị hạ về
0 và không bị nới. Hai lớp độc lập, và bằng chứng ở trên cho thấy đúng như vậy: dataset
thiếu 1/365 ngày (0,274%) vẫn **dưới** ngưỡng độ phủ và `official_eligibility` vẫn trả
`(True, 'verified')` — nhưng NGÀY bị ảnh hưởng nay là INVALID nên không tạo được quyết định
official. Ngưỡng độ phủ nói về DATASET; `CHECK-A4-11` nói về NGÀY.

**Độ lệch dư sau khi bóng gap đi qua — công bố thẳng, không giấu trong chữ "không đổi".**
Trên dataset CÓ GAP, sau khi cửa sổ đã trượt qua hẳn ngày thiếu (đo trên 134 ngày cách gap
hơn 365 ngày), bốn cột vẫn KHÔNG bằng nhau từng bit so với chuỗi đầy đủ:

| Cột | max lệch tương đối | max lệch tuyệt đối | Nguyên nhân |
|---|---|---|---|
| `ma200` | 2,11e-16 | 3,55e-15 | pandas cộng dồn rolling theo kiểu online; một `NaN` đi qua cửa sổ làm đổi thứ tự kết hợp phép cộng — sai số ở mức 1 ULP của `double` |
| `ma_ratio` | 3,04e-16 | 2,22e-16 | dẫn xuất từ `ma200` |
| `ma200_slope` | 5,83e-10 | 7,11e-15 | hiệu của hai `ma200`; lệch TUYỆT ĐỐI vẫn ở mức ULP, tỷ lệ lớn chỉ vì mẫu số gần 0 |
| `rsi14` | 7,44e-13 | 4,42e-11 | Wilder là hồi quy có bộ nhớ vô hạn; dải sau gap được warm-up lại nên mang một đuôi suy giảm theo `(13/14)^k` — sau 365 ngày còn ~3e-12, đúng bậc đo được |

`high365`, `percentile365`, `adr30`, `return7`, `volume_ratio`, `ethbtc_percentile180`
lệch **đúng bằng 0** trên cùng tập ngày.

Đây KHÔNG phải hình dạng lỗi của `F-S009-01` (lệch 14,29% ở §3 và 295% đổi dấu ở §II.2 của
`docs/reviews/S009-F-S009-01-indicator-theo-vi-tri.md`), và KHÔNG xuất hiện trên dữ liệu
sạch (CASE G khoá bit-identical). Nó được phân loại HARDENING kèm `RE_TRIGGER_CONDITION` ở
`PROJECT/HARDENING_BACKLOG.md` **H-16**, không được nuốt im lặng.

**Ranh giới KHÔNG thuộc check này.** Ngày thiếu ở HAI ĐẦU khoảng được yêu cầu không quan
sát được từ `compute_daily_indicators` (`_calendar_index` neo vào ngày đầu/cuối QUAN SÁT
ĐƯỢC). Đó là việc của `CHECK-A4-10` và cố ý không bị dựng lại ở đây — dựng lại sẽ là hệ
validity thứ hai, điều `DEC-016` cấm. `test_case_f_gap_at_series_tail_does_not_extend_the_calendar`
khoá đúng ranh giới này.

**Regression.** `python -m pytest -q` → **286 PASS, 0 FAIL, 0 SKIP, 0 XFAIL** (232 trước
chu kỳ này + 54 test mới). Chứng minh bằng git chứ không bằng lời: `git diff --stat --
tests/` rỗng (không file test cũ nào bị sửa), `git status --short tests/` chỉ có một file
`??` mới, và toàn repo không có marker `skip`/`xfail` nào.

Executed By:
S010 — agent phiên CAP-DATA REPAIR CYCLE #1 (Tier C / xhigh), 2026-09-01

Timestamp:
2026-09-01

### Audit

#### CHECK-A4-09 — Rà soát độc lập E2 cho ngữ nghĩa INVALID
Priority:
RECOMMENDED

Status:
NOT_TESTED

Evidence Level:
E2

Evidence:
RECOMMENDED, **không phải điều kiện DONE** — `EVIDENCE_STANDARD.md` yêu cầu E1 cho Risk 3
và toàn bộ REQUIRED check đã đạt E1. Phiên S009 KHÔNG tự phong E2 cho chính mình:
`REVIEW_PROTOCOL.md` nói rõ "an independent review verdict is authoritative over the
implementer's narrative", nên một reviewer độc lập là điều kiện, và phiên này không phải
reviewer độc lập của chính nó.

Nếu chủ dự án muốn E2, hai vùng đáng soát nhất: (a) bảng ca kiểm thử CHECK-A4-01, đặc biệt
ranh giới nhóm (b)/(c) và lựa chọn `REQUIRED_DAILY_INDICATORS`; (b) ngưỡng
`MAX_MISSING_RATIO = 0.01` của CHECK-A4-10 — nó là con số duy nhất trong gói không dẫn xuất
được từ spec, và `F-S009-01` cho thấy khoảng dung sai đó có tương tác thật với lớp indicator.

Budget: `CAP-DATA` đã tiêu 0 vòng E2 (`REVIEW_BUDGET_LEDGER.md` §2.1).

Executed By:
—

Timestamp:
—

## Exit Criteria
- [x] 100% REQUIRED checks PASS — **10/10** (CHECK-A4-01…08 FROZEN + CHECK-A4-10 do
      `DEC-014` bổ sung + CHECK-A4-11 do `DEC-016` bổ sung ở CAP-DATA REPAIR CYCLE #1).
      CHECK-A4-09 là RECOMMENDED, `NOT_TESTED`, không phải điều kiện DONE
- [x] Mức evidence yêu cầu được thoả (E1 toàn bộ REQUIRED)
- [x] Danh sách "indicator bắt buộc" được ghi ở nơi tra cứu được — `docs/CONVENTIONS.md`
      §"Indicator daily bắt buộc và ranh giới DEGRADED / INVALID"
- [x] Mọi sai lệch kết quả được định lượng và quy về điều khoản spec — CHECK-A4-07
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật
- [x] Session handoff được viết — `docs/sessions/S009-wp-a4-ngu-nghia-du-lieu-xau.md`
- [x] Không hạ REQUIRED check nào để đạt DONE — chín check FROZEN giữ nguyên câu chữ; hai
      bổ sung đều do chủ dự án phê duyệt TRƯỚC khi phần implementation tương ứng bắt đầu:
      CHECK-A4-10 (`OD-A4-01`) và CHECK-A4-11 (`DEC-016`)
- [x] `F-S009-01` đóng bằng CAP-DATA REPAIR CYCLE #1 — CHECK-A4-11 PASS ở E1; batch review
      bắt buộc (Effective Risk HIGH, `DEC-017`) đã chạy: `docs/reviews/S010-batch-review-calendar-indicator.md`

## Escalation Triggers

- Spec không nói rõ **indicator nào là bắt buộc** → `CONFLICT DETECTED`. Nếu là điểm để ngỏ hợp lệ:
  chốt quy ước và ghi vào `docs/CONVENTIONS.md`. Nếu là mâu thuẫn nội tại của spec: chuyển sang
  **WP-D2**, không vá V2.1.5.
- Siết định nghĩa INVALID làm engine dừng ở phần lớn thời gian trên dữ liệu thật → `SCOPE_CHANGED`:
  dừng, định lượng, trình chủ dự án. Đây có thể là dấu hiệu dữ liệu đầu vào không đủ chất lượng cho
  official run, tức một vấn đề lớn hơn gói này.
- Phải chạm `regime.py` hoặc `capital.py` để đóng gói → `SCOPE_CHANGED`, mở
  `COMPLETION GATE CHANGE PROPOSAL`.
- WP-A3 chưa DONE mà vẫn muốn mở gói → `MISSING_INPUT`, giữ PLANNED.

## Ảnh hưởng nếu gói này thất bại

Mắt xích thứ hai của đường găng. WP-A6 không khởi động được, GATE-A không đóng, T-06 không mở. Nếu
bỏ qua và vẫn chạy official run trên dữ liệu Binance thật (vốn có gap), engine sẽ hành động ở những
thời điểm spec yêu cầu dừng, và không bản ghi nào cho biết bản ghi nào bị ảnh hưởng — official
simulation sai một cách **âm thầm**.

## Changed Files Registry

Created:
- `tests/test_wp_a4_calendar_indicator_semantics.py` — CHECK-A4-11, CASE A–H (54 test,
  CAP-DATA REPAIR CYCLE #1)
- `docs/reviews/S010-batch-review-calendar-indicator.md` — batch review bắt buộc của chu kỳ
- `docs/sessions/S010-cap-data-repair-cycle-1.md` — session handoff + bằng chứng
- `tests/test_wp_a4_bad_data_semantics.py` — CHECK-A4-01…06
- `tests/test_wp_a4_requested_range_coverage.py` — CHECK-A4-10, CASE A–F
- `tests/wp_a4_fetch_stub.py` — stub I/O Binance (chỉ thay lớp HTTP)
- `docs/sessions/S009-wp-a4-ngu-nghia-du-lieu-xau.md` — session handoff + bằng chứng

Modified:
- `src/eth_dca_os/indicators.py` — (CAP-DATA REPAIR CYCLE #1) `_calendar_index`, chỉ mục
  lịch ngày liên tục trong `compute_daily_indicators`, `wilder_rsi` tách dải liên tục,
  `_rolling_percentile_of_last` trả NaN khi cửa sổ thiếu ngày
- `src/eth_dca_os/score.py` — `REQUIRED_DAILY_INDICATORS`, `invalid_mask`, `factor_scores(ind=...)`
- `src/eth_dca_os/engine.py` — `missing_before` trên nến, `tags` + `missing_candles_before`
  trên purchase record, bộ đếm `execution_data_gap`
- `src/eth_dca_os/data/dataset.py` — `gap_report` neo vào khoảng yêu cầu, `build_lineage`
  ghi/mang theo khai báo, `official_eligibility` kiểm độ phủ, `MAX_MISSING_RATIO`
- `src/eth_dca_os/data/fetch.py` — `fetch_all` khai `requested_range`
- `src/eth_dca_os/data/synth.py` — `generate` khai `requested_range`
- `docs/CONVENTIONS.md` — indicator bắt buộc, ranh giới DEGRADED/INVALID, nhãn trên purchase
  record, độ phủ theo khoảng được yêu cầu
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/REVIEW_BUDGET_LEDGER.md`,
  `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/PROJECT_DECISIONS.md`,
  `PROJECT/HARDENING_BACKLOG.md`

Deleted:
- Không

Migration Impact (CAP-DATA REPAIR CYCLE #1):
- `compute_daily_indicators` trả DataFrame indexed theo LỊCH NGÀY LIÊN TỤC. Trên dataset
  **liên tục** (mọi dataset đang có trong repo và mọi test hiện hữu) chỉ mục KHÔNG đổi và
  kết quả trùng khớp từng bit — đo ở CASE G và ở bảng non-regression tầng quyết định.
  Trên dataset **có ngày daily thiếu**, chỉ mục nay có thêm hàng cho ngày đó (giá trị NaN),
  và ngày đó là INVALID. `dataset_hash`, `manifest_hash`, chữ ký hàm public đều KHÔNG đổi.
- `wilder_rsi` nay warm-up lại sau mỗi lần chuỗi ngày lịch đứt. Chuỗi không đứt chỉ có một
  dải nên kết quả không đổi.

Migration Impact (WP-A4 gốc):
- Purchase record mang thêm `tags` và `missing_candles_before`; lineage entry mang thêm
  `requested_start`/`requested_end`/`expected_count`/`missing_head`/`missing_internal`/
  `missing_tail`. **`dataset_hash` KHÔNG đổi** (vẫn chỉ dẫn xuất từ danh sách `file_hash`),
  nên run record và `manifest_hash` đã ghi không trôi.
- Lineage sinh TRƯỚC gói này không có khai báo khoảng yêu cầu → `coverage_undeclared`,
  tức không đủ tư cách official cho tới khi được dựng lại bằng `ethdca fetch`. Đây là hành
  vi CỐ Ý (fail-closed) và không mất dữ liệu: chưa có official run nào tồn tại (T-06 chưa
  chạy), nên không có bản ghi lịch sử nào bị vô hiệu hoá.

## Escalation Triggers — kết quả kiểm tra tại S009

- **"Spec không nói rõ indicator nào là bắt buộc"** — ĐÚNG là điểm để ngỏ, không phải mâu
  thuẫn nội tại. Xử lý theo đúng nhánh đã định: chốt quy ước và ghi vào
  `docs/CONVENTIONS.md`. KHÔNG chuyển WP-D2, KHÔNG vá spec V2.1.5.
- **"Siết định nghĩa INVALID làm engine dừng phần lớn thời gian"** — KHÔNG kích hoạt. Đo
  được (CHECK-A4-07): trên dataset CÓ GAP, INVALID = 37/366 ngày ≈ 10%, và toàn bộ 37 ngày
  đó truy được về đúng 7 dòng daily có `close` không hợp lệ (cộng đuôi rolling 30 của
  `adr30`). Trên dataset sạch: 0 ngày INVALID, kết quả trùng khớp từng chữ số với BEFORE.
  Không có `SCOPE_CHANGED`.
- **"Phải chạm `regime.py` hoặc `capital.py`"** — KHÔNG xảy ra. Không file nào trong danh
  sách cấm bị chạm.
- **"WP-A3 chưa DONE"** — không áp dụng; WP-A3 DONE từ S003.

## Notes

Cạm bẫy: siết định nghĩa INVALID là việc dễ viết nhưng khó chứng minh là **đúng mức**. Quá lỏng thì
lỗi cũ còn nguyên; quá chặt thì engine đứng im trên dữ liệu thật và official run mất ý nghĩa. Đó là
lý do CHECK-A4-01 đòi bảng ca kiểm thử phủ ba nhóm, và CHECK-A4-07 đòi định lượng trên dataset có
gap thật.
