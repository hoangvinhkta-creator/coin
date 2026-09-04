# WP-C2 — Làm rõ và đặt tên trạng thái thực thi của hệ thống

## Metadata
Status:
IMPLEMENTED — 2026-09-04, phiên `S024` (nhánh `claude/wp-c2-execution-state-y4rraf`, tách từ
`origin/main` `2189a8f`). Ready Gate được xác nhận lại đầy đủ khi mở task; `READY → IN_PROGRESS
→ IMPLEMENTED`. **8/8 REQUIRED check PASS** (`CHECK-C2-01`…`CHECK-C2-08`), kết quả backtest
trùng khớp bit-for-bit trước–sau, full suite PASS. Bằng chứng đầy đủ:
`docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md`.

**CHƯA `DONE`.** `governance/v4/CORE/STATE_AUTHORITY.md` § "The State Machine And Who May
Write It" quy định `DONE` do **chủ dự án hoặc một completion authority được chỉ định** ghi —
tiền lệ trong dự án này là `WP-B1` (`DEC-034`, "Owner-authorized lifecycle closure"). Agent
thực thi không tự ghi `DONE`. Việc còn lại là **đúng một quyết định đóng vòng đời của chủ dự
án**: `OWNER_DECISION_REQUIRED`.

Trước đó: READY — 2026-09-04 (`DEC-035` RESOLVED, phương án PA-A; `ADR-001` Accepted), theo
hợp đồng `docs/reviews/WP-C2-SCOPE-ADR-DEC005-REPORT.md` §14.

Phase:
Phase 5 — Lớp C: bắt buộc sửa trước khi đưa vào dùng thật

Task Mode:
MAJOR

Lớp (RCP-001):
C — MUST FIX BEFORE PRODUCTIZATION

Completion Gate Freeze:
FROZEN — 2026-08-23 (T-04 / S002)

Routing Status:
ROUTED

Routing Inputs (all integers 0-4):
D: 3
R: 2
B: 3
A: 3
X: 3
U: 3
V: 2
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
2.75

Effort Routing Score:
2.55

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
2/4

Blast Radius:
3/4

Project Profile:
PRODUCT

## Objective

Đặt tên, hợp nhất và lưu vết **hành vi đã có** thành sáu Execution State mà Strategy §16/§19 định
nghĩa, sao cho backtest và app mô tả cùng một tình huống bằng **cùng một ngôn ngữ**.

## Hiện trạng đã được S001 xác định — không phải "thiếu hoàn toàn"

| Trạng thái | Hiện trạng | Vị trí |
|---|---|---|
| `WAIT` | Tồn tại ngầm — không có candidate action. Không đặt tên, không lưu | — |
| `FUNDING_REQUIRED` | **THIẾU THẬT** như một trạng thái phân biệt được | — |
| `READY_TO_BUY` | Tồn tại ngầm — điều kiện `ts >= execute_at` | `engine.py:431` |
| `ACTION_PENDING` | Tồn tại tường minh nhưng ở `Zone.status`, không phải Execution State | `engine.py:235` |
| `COOLDOWN` | Tồn tại như biến cục bộ `in_cooldown`; hành vi được cưỡng chế đúng | `engine.py:422, 517` |
| `DATA_BLOCKED` | Hành vi tồn tại (chặn khi `dq == INVALID`) nhưng không đặt tên, không lưu | `engine.py:452, 506` |

`FUNDING_REQUIRED` thiếu thật vì Backtest §5 định nghĩa `funding_delay = 0 nếu USDT treasury đã đủ`,
nhưng engine **không mô hình hoá treasury USDT**, và `docs/CONVENTIONS.md` #8 chốt quy ước
"ON_DEMAND: mọi zone action đều cần funding" — nên nhánh điều kiện đó không bao giờ được thực thi.

Hệ quả cho remediation: **phần lớn công việc là đặt tên và lưu vết**, không phải viết logic mới.

## Câu hỏi phạm vi phải quyết trước khi bắt đầu

Backtest có cần mô hình hoá treasury USDT để `FUNDING_REQUIRED` có nghĩa không, hay trạng thái đó
chỉ thuộc tầng app?

Câu hỏi này cần một **ADR** và liên quan tới **DEC-005** (phạm vi công cụ trước verdict). Đó là lý
do gói này BLOCKED cho tới khi T-05 chốt DEC-005.

**Cập nhật 2026-09-04 — RESOLVED:** chủ dự án phê duyệt `DEC-035` (phương án PA-A — phân xử HẸP
chỉ cho `WP-C2`, không chờ `DEC-005` chốt theo nghĩa rộng cho webapp) và chấp nhận
`docs/adr/ADR-001-wp-c2-execution-state-scope.md` (`FUNDING_REQUIRED` = `NOT_APPLICABLE` ở tầng
backtest). Cả hai dòng Ready Gate dưới đây nay đã thoả. `DEC-005` **vẫn PENDING** — vẫn tiếp tục
chặn `T-08`; quyết định này KHÔNG đóng `DEC-005`. Chi tiết đầy đủ:
`docs/reviews/WP-C2-SCOPE-ADR-DEC005-REPORT.md`.

## Đóng finding

- F-006 — Execution State machine không được cài đặt

## Scope

- `docs/adr/` — ADR quyết định phạm vi Execution State
- `src/eth_dca_os/engine.py` — đặt tên, hợp nhất, lưu vết trạng thái đã có
- `src/eth_dca_os/` — sinh `market_snapshots` với `execution_state` nếu ADR quyết định thuộc phạm vi
- `tests/`
- `docs/CONVENTIONS.md`

## Out of Scope

- **Thay đổi hành vi thực thi.** Gói này đặt tên cho hành vi đã có; nó không được làm đổi kết quả
  backtest
- Market Regime — chiều đó thuộc **WP-A3**; hai gói không được cùng định nghĩa lại một chiều
- Partial fill (WP-C3)
- `decision_log` (WP-B3) — WP-B3 **tiêu thụ** enum do gói này định nghĩa
- Sửa V2.1.5 để hợp thức hoá lựa chọn phạm vi; nếu cần thì chuyển sang **WP-D2**

## Dependencies
- T-04 (DONE)
- **T-05 / DEC-005** (DONE) — quyết định phạm vi công cụ trước verdict

## Blocks
- WP-C3
- WP-B3 (phần ngữ nghĩa `previous_state` / `new_state`)
- T-11

## Parallel-Safe With
- WP-C1, WP-C4, WP-D1, WP-D2

## Expected Touch Area

Allowed:
- `docs/adr/`
- `src/eth_dca_os/engine.py` — phần đặt tên và lưu trạng thái
- `tests/`, `docs/CONVENTIONS.md`

Do not touch without Scope Expansion:
- `src/eth_dca_os/regime.py` — Market Regime thuộc WP-A3
- `src/eth_dca_os/capital.py`, `score.py`, `ladders.py`, `verdict.py`
- `webapp/`, `docs/spec/`

## Subtasks
- [x] C2.1 Viện dẫn `ADR-001` (đã Accepted — quyết định: backtest không mô hình hoá treasury USDT)
      — viện dẫn tại `engine.BACKTEST_NOT_APPLICABLE_STATES`, `docs/CONVENTIONS.md` #22(d) và
      `docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md` §9. Không tạo ADR thứ hai.
- [x] C2.2 Đặt tên và lưu sáu trạng thái theo phạm vi đã quyết — `engine.ExecutionState`
      (`StrEnum`, đúng sáu giá trị ST §16/§19); năm trạng thái thuộc phạm vi được quan sát từ
      `run_engine` thật, `FUNDING_REQUIRED` `NOT_APPLICABLE` tường minh theo `ADR-001`.
- [x] C2.3 Hợp nhất `Zone.status`, `in_cooldown`, `dq` về một chiều Execution State nhất quán
      — `engine.derive_execution_state`, hàm thuần, điểm đo cố định (bước 12b). Ba nguồn cũ giữ
      nguyên vai trò; chiều mới là DẪN XUẤT, không cạnh tranh (`CONVENTIONS` #22(a)).
- [x] C2.4 Lưu `execution_state` vào snapshot nếu thuộc phạm vi (DM §4 yêu cầu NOT NULL)
      — `RunResult.market_snapshots` (một bản ghi mỗi accounting day) và
      `RunResult.execution_state_timeline` (ghi-khi-đổi, độ phân giải nến).
- [x] C2.5 Chứng minh kết quả backtest **không đổi** — `tests/wp_c2_invariance_tool.py`,
      payload chuẩn tắc trước–sau trùng khớp `sha256`; thêm bốn fingerprint kịch bản đóng băng
      trong `tests/test_wp_c2_execution_state.py`.
- [x] C2.6 Ghi quy ước vào `docs/CONVENTIONS.md` — mục **#22** (bảy tiểu mục a–g).

## Ready Gate

- [x] Objective rõ ràng
- [x] Scope được định nghĩa
- [x] Out-of-scope được định nghĩa
- [x] **DEC-005 đã được chủ dự án quyết định tại T-05.** — thoả qua phân xử HẸP `DEC-035`
      (PA-A, Owner-approved 2026-09-04): phạm vi đã đóng băng của `WP-C2` không chạm `webapp/`
      nên không thể vi phạm bất kỳ phương án nào của `DEC-005`; `DEC-005` nghĩa rộng (webapp)
      vẫn PENDING, không bị đóng bởi dòng này.
- [x] **ADR phạm vi Execution State tồn tại và được chủ dự án chấp nhận** — `docs/adr/ADR-001-wp-c2-execution-state-scope.md`,
      Status: Accepted (2026-09-04).
- [x] Expected touch area được xác định
- [x] Requirement liên quan được hiểu — ST §16, §19; DM §4, §11; BT §5; Product Spec §6, §11
- [x] Data impact được biết — thêm chiều trạng thái vào snapshot; không đổi dữ liệu thị trường
- [x] Security impact được biết — không có
- [x] Difficulty / Risk / Blast Radius được chấm
- [x] Escalation triggers được định nghĩa
- [x] Completion Gate được finalize
- [x] Completion Gate được đóng băng trước khi thực thi
- [x] **Xác nhận lại toàn bộ Ready Gate khi mở task** — thực hiện tại phiên `S024`
      (2026-09-04) TRƯỚC khi sửa một dòng production nào, đọc từ nguồn canonical chứ không
      từ báo cáo: `DEC-035` RESOLVED/APPROVED PA-A (`PROJECT/PROJECT_DECISIONS.md` dòng
      2613–2643), `ADR-001` `Status: Accepted` (`docs/adr/ADR-001-wp-c2-execution-state-scope.md`),
      `WP-C2 = READY` (`PROJECT/PROJECT_PROGRESS.md` bảng roadmap; `PROJECT/CAPABILITY_REGISTRY.md`
      `CAP-WEBAPP`), Completion Gate vẫn FROZEN 2026-08-23 với đúng 8 REQUIRED check nguyên
      văn. Kết luận: **Ready Gate THOẢ** — không có `READY_GATE_FAIL`, và không dòng governance
      nào bị sửa để làm nó thoả.

**Ghi chú quan trọng:** việc DEC-005 còn PENDING **không được dùng để chặn lớp A**. RCP-001 và
DEC-007 đã xác định DEC-005 không nằm trên đường găng tới verdict; nó chỉ chặn nhánh T-08 và nhánh
lớp C này.

## Completion Gate

Risk = 2 → E1 cho các check kiểm chứng được.

### Architecture

#### CHECK-C2-01 — ADR quyết định phạm vi tồn tại và được viện dẫn
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: file ADR trong `docs/adr/` trả lời dứt khoát câu hỏi treasury USDT, nêu phương án đã chọn,
phương án bị loại và lý do. Không có ADR thì gói không được bắt đầu.

**Kết quả (PASS):**

`docs/adr/ADR-001-wp-c2-execution-state-scope.md` tồn tại, `Status: Accepted` (2026-09-04,
Owner approval nguyên văn *"APPROVE PA-A CHO DEC-035, VÀ CHẤP NHẬN ADR-001."*, ghi tại
`PROJECT/PROJECT_DECISIONS.md` `DEC-035`). ADR trả lời DỨT KHOÁT câu hỏi treasury USDT
(§Decision), nêu phương án được chọn và HAI phương án bị loại kèm lý do (§Alternatives
Considered 1–3). ADR được **viện dẫn từ mã production** —
`src/eth_dca_os/engine.py::BACKTEST_NOT_APPLICABLE_STATES` — và từ `docs/CONVENTIONS.md` #22(d).
Không tạo ADR thứ hai. Test khoá viện dẫn:
`tests/test_wp_c2_execution_state.py::test_c2_03_funding_required_is_declared_not_applicable_at_backtest_layer`.

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

#### CHECK-C2-02 — Sáu Execution State được đặt tên và lưu vết theo phạm vi đã quyết
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: chạy thật và đọc ra được trạng thái tại từng thời điểm cho các trạng thái thuộc phạm vi.
Với trạng thái ngoài phạm vi (nếu ADR quyết định như vậy), phải có ghi nhận tường minh — không im
lặng bỏ.

**Kết quả (PASS):**

Vốn từ vựng: `engine.ExecutionState` (`StrEnum`) mang ĐÚNG sáu giá trị ST §16/§19, đối chiếu
trực tiếp với văn bản spec trong
`test_c2_02_vocabulary_is_exactly_the_six_spec_states` (parse `docs/spec/02_STRATEGY_SPEC_V2_1_5.md`).

Đọc được trạng thái TẠI TỪNG THỜI ĐIỂM: `RunResult.execution_state_timeline` ghi-khi-đổi ở độ
phân giải nến 15m; phép đọc "mốc gần nhất <= t" được kiểm không mất mát bởi
`test_c2_timeline_is_a_lossless_transition_log`.

Chạy THẬT (E1) — `python tests/wp_c2_reachability_tool.py --raw <synth 7,5 năm>`, 13 lần chạy
qua đúng hàm production (`metrics.window_metrics` × 9 window của Gate 1;
`engine.run_engine` toàn kỳ 2019-01-01 → OOS end × 2 execution config; cùng hai lần đó trên
dataset bị xoá MỘT hàng daily `2020-06-15` để dựng cửa sổ INVALID thật):

    states_observed_union      = ACTION_PENDING, COOLDOWN, DATA_BLOCKED, READY_TO_BUY, WAIT
    states_never_observed      = FUNDING_REQUIRED   (đúng ADR-001)
    total_snapshots            = 17.532
    total_null_execution_state = 0

Năm trạng thái thuộc phạm vi đều quan sát được từ runtime thật, KHÔNG dựng bằng tay. Trạng thái
ngoài phạm vi được ghi nhận tường minh — xem `CHECK-C2-03`.

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

#### CHECK-C2-03 — `FUNDING_REQUIRED` được xử lý tường minh, không im lặng vắng mặt
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: hoặc (a) trạng thái được mô hình hoá cùng treasury USDT và có test chứng minh nó phát sinh
được; hoặc (b) được tuyên bố `NOT_APPLICABLE` cho tầng backtest, kèm lý do trong ADR và mục trong
`docs/CONVENTIONS.md`, và kèm ghi nhận rằng tầng app vẫn phải có nó theo Product Spec §6/§11.

**Kết quả (PASS):**

Nhánh **(b)** của yêu cầu, đúng như `ADR-001` đã quyết:

1. **Tuyên bố trong mã**: `engine.BACKTEST_NOT_APPLICABLE_STATES = (ExecutionState.FUNDING_REQUIRED,)`
   kèm chú thích nêu lý do và viện dẫn `ADR-001`/`DEC-035`; giá trị VẪN nằm trong enum.
2. **Lý do trong ADR**: `ADR-001` §Decision + §Rationale (engine không mô hình hoá số dư USDT
   treasury; `funding_delay` là hàm tất định của `funding_policy` — `docs/CONVENTIONS.md` #8).
3. **Mục trong `docs/CONVENTIONS.md`**: #22(d), nêu cả hệ quả phải biết khi đọc output backtest.
4. **Ghi nhận tầng app vẫn phải có**: `CONVENTIONS` #22(d) và docstring của `ExecutionState`
   viện dẫn Product Spec §6/§7/§11 (`CHECK TREASURY → [FUNDING_REQUIRED] → READY_TO_BUY`).

Bằng chứng nó không âm thầm phát sinh: vét cạn 16 tổ hợp đầu vào của hàm dẫn xuất
(`test_c2_03_funding_required_is_unreachable_by_construction`); 0 lần xuất hiện trên MỌI lần
chạy thật (`total_funding_required = 0` trên 13 lần chạy, `states_never_observed =
['FUNDING_REQUIRED']`); và không định danh nào trong `engine.py`/`execution.py` mang khái niệm
treasury (`test_c2_03_engine_never_models_a_usdt_treasury_balance`, quét bằng `ast` nên không
tính comment).

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

#### CHECK-C2-04 — Market Regime và Execution State được lưu riêng
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: Strategy §16 đòi hai chiều độc lập và "phải được lưu riêng". Chứng minh bằng cấu trúc dữ
liệu thật, và chứng minh không gói nào định nghĩa lại chiều của gói kia (ranh giới với WP-A3).

**Kết quả (PASS):**

Cấu trúc dữ liệu THẬT: mỗi bản ghi `RunResult.market_snapshots` mang HAI trường riêng biệt —
`market_regime` (nhãn §16 do `RegimeTracker` cấp, thuộc WP-A3) và `execution_state` (WP-C2).
Trên kịch bản `crash_regime_cycle`, `market_regime` biến thiên qua bốn nhãn
(`NORMAL/STRESSED/CRASH/RECOVERY`) trong khi `execution_state` biến thiên độc lập
(`test_c2_04_regime_and_execution_state_are_stored_as_separate_fields`).

Không gói nào định nghĩa lại chiều của gói kia:
- không giá trị Execution State nào mang token regime — cấm `CRASH_READY_TO_BUY`
  (`test_c2_04_no_execution_state_value_encodes_a_regime`);
- `src/eth_dca_os/regime.py` KHÔNG ĐỔI một dòng (`git diff` rỗng) và không nhắc tới enum này
  (`test_c2_04_regime_module_is_untouched_by_the_execution_state_dimension`);
- không nhánh execution nào ĐỌC Execution State — chứng minh bằng HÀNH VI: ép
  `derive_execution_state` trả giá trị sai rồi chạy lại, fingerprint engine vẫn trùng khớp cây
  mã trước WP-C2 (`test_c2_07_forcing_a_wrong_execution_state_changes_no_behaviour`, 4/4 kịch
  bản).

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

#### CHECK-C2-05 — `market_snapshots.execution_state` NOT NULL nếu thuộc phạm vi
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: nếu ADR đưa snapshot vào phạm vi, chứng minh trường luôn có giá trị theo DM §4. Nếu ngoài
phạm vi, ghi `NOT_APPLICABLE` kèm lý do — không để trống im lặng.

**Kết quả (PASS):**

Thuộc phạm vi. `RunResult.market_snapshots` sinh một bản ghi mỗi accounting day (cùng nhịp và
cùng vị trí với `cash_samples` sẵn có), `execution_state` LUÔN có giá trị:

    total_snapshots            = 17.532   (13 lần chạy production-realistic)
    total_null_execution_state = 0

Test khoá: `test_c2_05_execution_state_is_never_null_in_any_snapshot` (kiểm cả tập trường,
`market_regime` ∈ enum §16, `data_quality` ∈ {GOOD, DEGRADED, INVALID}, và chống PASS rỗng bằng
`assert total > 0`); `test_c2_05_one_snapshot_per_accounting_day`;
`test_c2_05_snapshot_execution_state_serialises_as_a_plain_string`.

Giới hạn phạm vi được TUYÊN BỐ, không bỏ trống im lặng: bản ghi mang các nhóm DM §4 mà engine
đã có tại điểm đo (identity/market `eth_price`/score/capital/state); KHÔNG mang `btc_price` và
ba nhóm indicator (price location, market stress, relative value) vì sinh chúng đòi kéo thêm
cột chỉ báo vào `engine.py` — ngoài phạm vi đã đóng băng của gói ĐẶT TÊN này. Ghi tại
`docs/CONVENTIONS.md` #22(f) và §18 của báo cáo.

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

### Regression

#### CHECK-C2-06 — Kết quả backtest không đổi
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: cùng seed và dataset, metric trước–sau **trùng khớp hoàn toàn**. Đây là ràng buộc định
nghĩa của gói: đặt tên cho hành vi đã có không được làm đổi hành vi. Bất kỳ sai lệch nào là dấu hiệu
gói đã viết logic mới thay vì đặt tên.

**Kết quả (PASS):**

**Trùng khớp bit-for-bit.** Công cụ `tests/wp_c2_invariance_tool.py` sinh một payload JSON
chuẩn tắc gồm: Gate 1 đầy đủ (chín window + OOS + diagnostics + bootstrap + concentration +
cash_ratio + opportunity_cap_hit + regime_advantage + `counters_w5` + benchmarks + xirr),
Gate 2 (8 config), Gate 3 (8 config + realistic + shortfall attribution), Control F/G
(200 sim), verdict, và HAI lần chạy engine toàn kỳ (`gate1_low_friction`, `gate3_realistic`)
với TOÀN BỘ bản ghi purchase/ledger/sample.

    BEFORE #1 (HEAD 2189a8f, cây mã nguyên bản)  sha256 = e0492a58f67e9fab0105216713ed9ca3dfecbae1608d91089ca48eef380fdbba  (1.340.788 byte)
    BEFORE #2 (chạy lại, cùng cây mã)            sha256 = e0492a58f67e9fab0105216713ed9ca3dfecbae1608d91089ca48eef380fdbba  (1.340.788 byte)
    AFTER     (sau khi sửa engine.py)            sha256 = e0492a58f67e9fab0105216713ed9ca3dfecbae1608d91089ca48eef380fdbba  (1.340.788 byte)

Hai lần chạy BEFORE độc lập cho cùng hash — chứng minh phép đo TỰ NÓ tất định, nên phép so
trước–sau có nghĩa (không phải một phép so luôn luôn trùng). Cùng dataset (`dataset_hash
3ffcefbe04…`), cùng config hash, cùng `MASTER_SEED`.

Trường metadata KHÔNG ngữ nghĩa bị loại TƯỜNG MINH và đầy đủ (`NON_SEMANTIC_RUN_RECORD_KEYS`):
`run_id` (uuid4), `created_at` (đồng hồ), `metrics_path` (đường dẫn tmp), `code_commit` (SHA
của chính commit đang đo). Không trường nào khác bị loại; không khác biệt có nghĩa nào bị
"normalize" đi. Hai trường WP-C2 thêm (`market_snapshots`, `execution_state_timeline`) nằm ở
khối `wp_c2_observability` TÁCH RIÊNG — chúng là trường MỚI, không phải trường bị đổi.

Ở quy mô kịch bản, bốn fingerprint hành vi chụp trên cây mã TRƯỚC WP-C2 được đóng băng trong
`tests/test_wp_c2_execution_state.py::FROZEN_PRE_WP_C2_FINGERPRINTS` và kiểm mỗi lần chạy suite
(`test_c2_06_engine_behaviour_is_bit_identical_to_pre_wp_c2`, 4/4) — phủ vòng đời zone, thời
điểm cooldown, hành vi chặn dữ liệu xấu và chu kỳ regime.

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

#### CHECK-C2-07 — Không tạo class `StateMachine` chỉ để khớp tên trong spec
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E0

Evidence:
Yêu cầu: thiết kế được biện minh trong ADR theo tiêu chí "hợp nhất hành vi đã có", không theo tiêu
chí "khớp danh từ trong spec". Đây là check thiết kế, E0 là mức phù hợp — nhưng nó vẫn REQUIRED vì
RCP-001 nêu tường minh.

**Kết quả (PASS):**

Thiết kế được biện minh theo tiêu chí "hợp nhất hành vi đã có", không theo "khớp danh từ":

- Toàn bộ chiều mới = **một enum giá trị** (`ExecutionState`) + **một hàm thuần**
  (`derive_execution_state`, 5 câu lệnh `if`). Không class, không đối tượng có vòng đời, không
  bảng chuyển trạng thái, không biến trạng thái mới trong engine.
- `Zone.status`, `in_cooldown`, `data_quality` GIỮ NGUYÊN vai trò nguồn sự thật; chiều mới là
  DẪN XUẤT đọc từ chúng tại một điểm đo cố định (bước 12b), nên không sinh ra nguồn sự thật
  cạnh tranh — đúng yêu cầu "tránh parallel sources of truth".
- Diff production: **1 file, +128/−0** — không xoá hay sửa MỘT DÒNG hành vi nào đang có.

Test khoá (E0 là mức gate đòi; ở đây có thêm bằng chứng E1):
`test_c2_07_no_state_machine_class_was_created` (quét mọi `class` trong `src/eth_dca_os/`,
khẳng định không tên nào chứa `StateMachine`; enum không mang phương thức tự viết),
`test_c2_07_execution_state_adds_no_engine_state_variable`, và
`test_c2_07_forcing_a_wrong_execution_state_changes_no_behaviour`.

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

#### CHECK-C2-08 — Toàn bộ test suite PASS
Priority:
REQUIRED

Status:
PASS

Evidence Level:
E1

Evidence:
Yêu cầu: output test suite đầy đủ.

**Kết quả (PASS):**

Toàn bộ suite Python, không deselect, không skip, không đổi/nới một test nào đang có:

    $ python -m pytest tests/ -p no:cacheprovider -rN --tb=short
    494 passed in 1402.46s (0:23:22)
    PYTEST_EXIT=0

    collected = 494   passed = 494   failed = 0   errors = 0   skipped = 0   xfail = 0   exit code = 0

Nền so sánh: 461 test trên cây mã trước gói này (`WP-B1`/`DEC-034` ghi 461/461 tại `9ac01b8`;
hai commit sau đó tới `2189a8f` là governance-only, không đổi test nào), cộng đúng 33 test mới
của `tests/test_wp_c2_execution_state.py` = 494. Không file test cũ nào bị sửa
(`git status` chỉ báo `docs/CONVENTIONS.md` và `src/eth_dca_os/engine.py` thay đổi).

Executed By:
S024 — phiên thực thi WP-C2 (implementer), nhánh `claude/wp-c2-execution-state-y4rraf`

Timestamp:
2026-09-04

## Exit Criteria
- [x] 100% REQUIRED checks PASS — 8/8 (`CHECK-C2-01`…`CHECK-C2-08`)
- [x] Mức evidence yêu cầu được thoả — E1 cho bảy check, E0 cho `CHECK-C2-07` đúng như gate
      FROZEN quy định (và `CHECK-C2-07` còn có thêm bằng chứng E1 không bắt buộc)
- [x] ADR tồn tại và được viện dẫn từ file task — `ADR-001`, viện dẫn ở Metadata, `CHECK-C2-01`,
      `CHECK-C2-03` và trong mã production
- [x] Kết quả backtest không đổi — bit-for-bit, `sha256 e0492a58…` (xem `CHECK-C2-06`)
- [x] Enum Execution State sẵn sàng cho WP-B3 và WP-C3 tiêu thụ — `from eth_dca_os.engine import
      ExecutionState`; `StrEnum` nên serialize thành chuỗi thuần, dùng trực tiếp cho
      `previous_state`/`new_state` (DM §11);
      `test_c2_downstream_contract_is_consumable_without_a_second_enum`
- [x] `PROJECT/PROJECT_PROGRESS.md` được cập nhật — mục `Last Updated` và dòng roadmap `WP-C2`
- [x] Session handoff được viết — `docs/sessions/S024-wp-c2-execution-state.md`
- [x] Không hạ REQUIRED check nào để đạt DONE — Completion Gate giữ NGUYÊN VĂN bản FROZEN
      2026-08-23; chỉ điền `Status` / `Kết quả` / `Executed By` / `Timestamp`, không sửa một chữ
      nào của phần `Yêu cầu`

**Trạng thái đóng vòng đời:** mọi Exit Criteria đã thoả, nhưng bước `IMPLEMENTED → DONE` KHÔNG
thuộc thẩm quyền của agent thực thi (`governance/v4/CORE/STATE_AUTHORITY.md`). Còn lại đúng một
việc: **quyết định đóng vòng đời của chủ dự án** — `OWNER_DECISION_REQUIRED`.

## Escalation Triggers

- ~~DEC-005 chưa được chốt → `MISSING_INPUT`, giữ BLOCKED.~~ — RESOLVED cho riêng `WP-C2` qua
  `DEC-035` (PA-A, 2026-09-04); `DEC-005` nghĩa rộng vẫn PENDING, không áp dụng escalation này cho
  `WP-C2` nữa.
- Việc đặt tên trạng thái làm đổi kết quả backtest → DỪNG. Đó là dấu hiệu gói đã vượt ra ngoài
  "đặt tên hành vi đã có", `SCOPE_CHANGED`, tính lại routing và phân lớp (có thể phải lên lớp A).
- Mô hình hoá treasury USDT hoá ra đòi đổi Backtest §5 → `CONFLICT DETECTED`, chuyển sang **WP-D2**,
  không vá V2.1.5.
- Sáu trạng thái của spec không phủ hết hành vi thật của engine → ghi nhận khoảng trống, trình chủ
  dự án; không tự thêm trạng thái thứ bảy vào enum của spec.

## Ảnh hưởng nếu gói này thất bại

WP-C3 và phần ngữ nghĩa của WP-B3 không hoàn tất được; T-11 không mở. Khi sang giai đoạn app,
Product Spec §6/§11 đòi hiển thị đúng sáu trạng thái — nếu backtest không mô hình hoá chúng thì live
và backtest sẽ mô tả cùng một tình huống bằng hai ngôn ngữ khác nhau, đúng loại trôi lệch mà
Implementation Plan §1 muốn chặn.

## Changed Files Registry

Thực tế tại `S024` (2026-09-04). Production path (`PROJECT/PRODUCTION_PATHS.md` §1) chỉ có
**một** file thay đổi, và là **thuần thêm mới**:

    git diff --shortstat 2189a8f -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    1 file changed, 128 insertions(+)

Created:
- `tests/test_wp_c2_execution_state.py` — 33 test bám 8 REQUIRED check
- `tests/wp_c2_scenarios.py` — kịch bản engine tất định + fingerprint hành vi trước WP-C2
- `tests/wp_c2_invariance_tool.py` — công cụ đo bất biến backtest (`CHECK-C2-06`)
- `tests/wp_c2_reachability_tool.py` — công cụ bằng chứng production reachability
- `docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md` — báo cáo bàn giao
- `docs/sessions/S024-wp-c2-execution-state.md` — biên bản phiên

Modified:
- `src/eth_dca_os/engine.py` (**production**, +128/−0)
- `docs/CONVENTIONS.md` (mục #22)
- `docs/tasks/WP-C2-execution-state-machine.md` (chính file này — vòng đời + evidence)
- `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/LO_TRINH_DE_HIEU.md` (sinh lại),
  `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/REVIEW_BUDGET_LEDGER.md`

**KHÔNG chạm** (đúng Do-not-touch): `src/eth_dca_os/regime.py`, `capital.py`, `score.py`,
`ladders.py`, `verdict.py`, toàn bộ `webapp/`, `docs/spec/`, `docs/adr/ADR-001-*` (không sửa
một chữ nào của quyết định đã Accepted), `pyproject.toml`, `pyproject.lock`. `data/` (untracked,
có chủ ý của chủ dự án) không bị đụng tới.

Deleted:
- Không

Migration Impact:
- Snapshot mang thêm chiều trạng thái; không có dữ liệu bền cần migrate ở tầng backtest

## Notes

RCP-001 nêu rõ: **không tạo một class `StateMachine` chỉ để khớp tên trong spec**. Việc cần quyết
định trước tiên là phạm vi, và phạm vi cần một ADR. Đây là một trong hai gói trong toàn bộ chương
trình mà quyết định kiến trúc phải có trước khi viết dòng mã đầu tiên.
