# WP-B3 Implementation Report

Phiên: `S025` · Ngày: 2026-09-04 · Vai trò: **implementer** (không phải phiên rà soát độc lập)
Nhánh: `claude/wp-b3-audit-trail-impl-3covtf` · Tách từ: `origin/main` `04f77ac`

---

## 1. Executive Summary

`WP-B3` đã được thực thi trọn vẹn trong đúng phạm vi đã đóng băng. Gói này **ghi lại** quyết
định của engine; nó không đổi một quyết định nào.

**Kết quả một dòng:** 8/8 REQUIRED check PASS · đầu ra tài chính/chiến lược **không đổi
bit-for-bit** · diff production **1 file, +266/−15** · 43 test mới · `WP-B3`:
`READY → IN_PROGRESS → IMPLEMENTED` · **chưa `DONE`** vì `DONE` là quyền của chủ dự án.

Việc đã làm, gọn trong bốn ý:

1. **Một audit trail canonical duy nhất.** `RunResult.decision_log` được **tiến hoá tại chỗ**
   thành bảng `decision_log` của Data Model §11: đúng 19 trường của bảng, cộng đúng một trường
   `tags` mang nhãn ST §9 / BT §18. Không có `decision_log_v2` / `audit_log` / `state_log` song
   song; dịch chuyển vốn thuần tuý vẫn ở `Pool.ledger` (DM §6) và không bị chép lại.
2. **Tiêu thụ hợp đồng `WP-C2`, không tạo hợp đồng thứ hai.** `previous_state`/`new_state` là
   chính thành viên `engine.ExecutionState`. Bản ghi chuyển trạng thái được sinh trong **CHÍNH
   nhánh mã** đã ghi `execution_state_timeline`, từ **cùng một giá trị** — đo được:
   `số bản ghi chuyển = số mốc timeline − 1` (1.043 = 1.044 − 1 và 1.077 = 1.078 − 1).
3. **Phạm vi sự kiện theo ST §20.** Từ **3 loại** (chỉ khi bật cờ) lên **25 loại quan sát được
   trên một lần chạy toàn kỳ thật**; 32/36 mã của danh mục được ghi, bốn mã còn lại đều có lý
   do canonical ghi trong mã nguồn.
4. **Audit trail hết là tuỳ chọn.** Cờ `log_decisions` bị **gỡ khỏi hợp đồng `run_engine`**.
   Trước gói này, đường production ghi **0 bản ghi**; sau gói: **2.441 / 2.478 bản ghi**.

**Điều quan trọng nhất cần chủ dự án tin được:** con số tài chính không nhúc nhích. Một payload
chuẩn tắc **3.728.853 byte** (Gate 1 chín window + OOS + Gate 2/3 + Control F/G + verdict + hai
lần chạy engine toàn kỳ kèm TỪNG bản ghi purchase, **cộng cả `execution_state_timeline` và
`market_snapshots` của WP-C2**) cho **cùng một `sha256`** ở lần chạy TRƯỚC khi sửa và ở lần
chạy SAU khi sửa.

**Việc còn lại: đúng một quyết định của chủ dự án** — đóng vòng đời `IMPLEMENTED → DONE`.
Xem §22 và §26.

---

## 2. Source / Branch / Commit

| Mục | Giá trị |
|---|---|
| Canonical source | `origin/main` |
| Expected HEAD (theo đề bài) | `04f77ac` |
| `git rev-parse origin/main` đo được | `04f77ac57d42b115098d32798874a5851d10e53a` ✅ khớp |
| Nhánh thực thi | `claude/wp-b3-audit-trail-impl-3covtf` (tách từ đúng SHA trên, 0 commit lệch khi mở phiên) |
| Interpreter | Python 3.11.15 |
| Dependency | đúng theo `pyproject.lock`: numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1 |
| `data/` (untracked, chủ dự án giữ có chủ ý) | **KHÔNG đụng tới** — không clean, không stash, không commit. Thư mục này không tồn tại trong container phiên; dataset dùng cho phép đo là synthetic sinh vào thư mục tạm ngoài repo |

Branch authority check (`governance/scripts/governance/branch_authority_check.sh`) chạy TRƯỚC
khi đọc bất kỳ file trạng thái nào:

    branch            = claude/wp-b3-audit-trail-impl-3covtf
    default branch    = main (resolved, not assumed)
    ahead of default  = 0 commit(s)
    divergence age    = 0 day(s)
    divergence LOC    = 0
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: FAIL
    - attached branch has no upstream

**Duy nhất một lý do FAIL: nhánh chưa có upstream** — đúng như mong đợi với một nhánh vừa tạo
chưa push (cùng tình huống đã ghi ở `WP-C2`/`S024` §2). Điều kiện thực chất mà check này bảo vệ
— đọc trạng thái từ một nhánh cũ/lệch — **được thoả**: nhánh trùng khớp `origin/main` 0 commit,
0 LOC lệch, worktree sạch, không `INTEGRATION_DECISION_REQUIRED`. Kết quả chạy lại SAU khi push
được ghi ở §25.

**Xác minh trạng thái canonical trước khi thực thi** (đọc từ `PROJECT/PROJECT_PROGRESS.md`,
`PROJECT/PROJECT_DECISIONS.md`, `PROJECT/CAPABILITY_REGISTRY.md`, bảng roadmap và file task —
không đọc từ báo cáo):

| Mục đề bài yêu cầu | Đo được | Khớp |
|---|---|---|
| `WP-B1 = DONE` | DONE (`DEC-034`) | ✅ |
| `WP-B2 = READY` | READY (`DEC-031`) | ✅ |
| `WP-C2 = DONE` | DONE (`DEC-036`) | ✅ |
| `WP-B3 = READY` | READY (`DEC-036`) | ✅ |
| `WP-C3 = READY` | READY (`DEC-036`) | ✅ |
| `Gate-B = CLOSED` (chưa mở) | CHƯA MỞ — đòi cả ba gói B đều DONE | ✅ |
| `T-07 = NOT READY` | NOT READY | ✅ |
| `DEC-005 = PENDING` | PENDING (vẫn chặn `T-08`) | ✅ |
| `T-08` vẫn bị chặn | PLANNED, chặn bởi `T-05`/`DEC-005` | ✅ |
| `T-06 = DONE` | DONE (`DEC-031`) | ✅ |
| V2.1.5 validation = `FAILED` | FAILED | ✅ |
| verdict = `DO_NOT_BUILD` | DO_NOT_BUILD | ✅ |
| `can_proceed_to_app = false` | false | ✅ |

Không có sai lệch. Không phát sinh `SOURCE_STATE_REVIEW_REQUIRED`.

---

## 3. Ready Gate

Xác nhận lại TOÀN BỘ Ready Gate **trước khi sửa một dòng production nào**, đọc từ nguồn
canonical:

| Dòng Ready Gate | Nguồn đã đọc | Kết quả |
|---|---|---|
| Objective / Scope / Out-of-scope rõ ràng | file task | THOẢ (đã `[x]` từ trước) |
| **Dependency `T-06 DONE`** | `PROJECT_PROGRESS` bảng roadmap; `DEC-031` | THOẢ |
| **Dependency `WP-C2 DONE`** | `DEC-036` (Owner-authorized Lifecycle Closure); bảng roadmap; `CAPABILITY_REGISTRY` | **THOẢ** |
| Expected touch area được xác định | file task | THOẢ |
| Requirement liên quan được hiểu — DM §11; ST §9, §20 | `docs/spec/04_*.md` §11, `docs/spec/02_*.md` §9/§16/§19/§20 | THOẢ |
| Data impact / Security impact được biết | file task | THOẢ |
| Difficulty / Risk / Blast Radius được chấm | file task (2/4, 2/4, 2/4) | THOẢ |
| Escalation triggers được định nghĩa | file task | THOẢ |
| Completion Gate finalize + đóng băng trước khi thực thi | file task, FROZEN 2026-08-23 (T-04/S002), đúng 8 REQUIRED check | THOẢ |
| Xác nhận lại toàn bộ Ready Gate khi mở task | phiên này | THOẢ → `[x]` |

**Điểm phải kiểm riêng theo đề bài §4** — hợp đồng `ExecutionState` mà `CHECK-B3-02` cần
**thật sự tồn tại và production-reachable**, không phải chỉ tồn tại trên giấy:

- `src/eth_dca_os/engine.py::ExecutionState` — `StrEnum`, sáu giá trị ST §16/§19. ✅
- `src/eth_dca_os/engine.py::derive_execution_state(...)` — hàm thuần, gọi ở bước 12b. ✅
- `RunResult.execution_state_timeline` — ghi-khi-đổi; đo trên run toàn kỳ: **1.044 / 1.078 mốc**. ✅
- `RunResult.market_snapshots[*].execution_state` — NOT NULL; `CHECK-C2-05` đã PASS với 17.532
  bản ghi, 0 null. ✅

**Kết luận: Ready Gate THOẢ — không có `READY_GATE_FAIL`.** Không một dòng governance nào bị
sửa để làm nó thoả.

Trạng thái vòng đời đã ghi: `READY → IN_PROGRESS → IMPLEMENTED` (cả hai bước thuộc thẩm quyền
Implementer theo `governance/v4/CORE/STATE_AUTHORITY.md`).

Cũng đã kiểm chứng và **KHÔNG đổi**: `DEC-005` vẫn `PENDING`; `T-08` vẫn bị chặn.

---

## 4. Canonical Scope

Đọc theo thứ tự thẩm quyền `AGENTS.md` §1: CORE V4.3 → `PROJECT/` → task/ADR → spec.

**Trong phạm vi (đã làm):** nội dung và phạm vi ghi `decision_log` trong
`src/eth_dca_os/engine.py`; test trong `tests/`; quy ước trong `docs/CONVENTIONS.md` (#23).

**Ngoài phạm vi (đã KHÔNG làm):** định nghĩa Execution State enum (thuộc `WP-C2`, đã DONE —
gói này chỉ TIÊU THỤ); đổi hành vi quyết định của engine; chính sách verdict (`WP-B1`); lớp lưu
trữ bền cho app (`T-09B`); partial fill (`WP-C3`); bổ sung test requirement (`WP-B2`).

**Không chạm** (đúng Do-not-touch của task và của đề bài): `verdict.py`, `failure_signals.py`,
`gates.py`, `regime.py`, `ladders.py`, `capital.py`, `score.py`, `benchmarks.py`, toàn bộ
`webapp/`, `docs/spec/`, `pyproject.toml`, `pyproject.lock`, ngưỡng Gate, ngưỡng
failure-signal, ngưỡng chiến lược, công thức Buy Score, ngữ nghĩa regime, phân bổ vốn, hành vi
opportunity fund, evidence T-06, tag official, kết quả validation V2.1.5. Không rerun T-06.
Không điều tra AE. Không chạy thí nghiệm chiến lược mới. Không thiết kế lại Control F/G. Không
thiết kế V2.2. Không mở `WP-B2`/`WP-C3`. Không merge `main`.

`git diff --stat 04f77ac -- webapp docs/spec pyproject.toml pyproject.lock` = **rỗng**.

---

## 5. Pre-Implementation decision_log Map

Bước bắt buộc theo đề bài §11 — **khảo sát trước khi sửa**. `decision_log` **đã tồn tại** từ
trước; gói này tiến hoá nó, không dựng mới.

### 5.1 Nhà sản xuất (producers)

Đúng **một** producer: closure `log(ts, reason, **kw)` tại `engine.py:274-276` (SHA `04f77ac`),
được gọi từ **ba** vị trí:

| Vị trí | Bước BT §19 | Mã ghi | Điều kiện |
|---|---|---|---|
| `engine.py:636` | 14a — tạo Crash ladder | `regime.last_entry_reason` (`CRASH_ENTRY_7D`/`24H`) | **chỉ khi** `crash_snapshot is not None` (snapshot > 0 và `adr30` không NaN) |
| `engine.py:705` | 14c — daily limit chặn Crash zone | `DAILY_LIMIT_BLOCK` | zone vượt headroom |
| `engine.py:715` | 14c — cooldown override | `COOLDOWN_OVERRIDE` | mỗi zone được tạo action trong cycle override |
| `engine.py:746` | 18a — bullish invalidation | `BULLISH_INVALIDATION` | ladder bị INVALIDATED |

Toàn bộ bốn lời gọi nằm sau `if log_decisions:` — **mặc định `False`**.

### 5.2 Người tiêu thụ (consumers)

`grep -rn "decision_log" src/ webapp/ demo/` → **không có consumer production nào**. Toàn bộ
tiêu thụ nằm ở `tests/`:

| Nơi | Đọc gì |
|---|---|
| `tests/test_wp_a3_lifecycle.py:286,446,479-481` | đếm/so `DAILY_LIMIT_BLOCK` |
| `tests/test_wp_d1_debt_cleanup.py:84` | hai dòng `COOLDOWN_OVERRIDE` cùng `ts` |
| `tests/test_wp_a6_processing_order.py:364-372` | so tiền tố log (bỏ `zone`/`ladder`) |
| `tests/wp_a3_impact_tool.py:159` | đếm `daily_limit_blocks` |
| `tests/wp_c2_scenarios.py:29` | `decision_log` nằm trong fingerprint bất biến của WP-C2 |
| `tests/wp_c2_invariance_tool.py:81` | `decision_log` nằm trong khối bất biến của công cụ WP-C2 |

Không có tầng lưu trữ: `reporting.save_run` **không** ghi `decision_log` ra đĩa;
`pipeline.py`/`metrics.py` gọi `run_engine` **không truyền `log_decisions`**. Hệ quả đo được:
audit trail của mọi lần chạy production là **rỗng**.

### 5.3 Schema hiện có so với yêu cầu DM §11

Bản ghi cũ: `{"ts": float, "reason_code": str, **kw}` với `kw` ∈ {`zone`, `ladder`}.

| Trường DM §11 | Trước gói | Khoảng trống |
|---|---|---|
| `decision_id` | ✗ | thiếu hoàn toàn |
| `timestamp_utc` | có, tên `ts` | **đổi tên** |
| `previous_state` / `new_state` | ✗ | thiếu — cần enum WP-C2 (`F-006`) |
| `market_regime` / `data_quality` | ✗ | thiếu |
| `trigger_type` | ✗ | thiếu |
| `reason_code` | ✅ | giữ nguyên |
| `opportunity_score` | ✗ | thiếu |
| `recommended_price` / `_vnd` / `_usdt_est` | ✗ | thiếu |
| `zone_id` / `ladder_id` | có, tên `zone`/`ladder`, **chỉ ở một số dòng** | **đổi tên** |
| `available_vnd` / `reserved_vnd` / `deployed_vnd` | ✗ | thiếu (snapshot bắt buộc) |
| `strategy_config_hash` / `execution_config_hash` | ✗ | thiếu |

Phạm vi sự kiện: **3/36** mã ST §20 (và cả ba đều có điều kiện).
Nhãn ST §9 `EXECUTED_EARLY`: **không tồn tại ở đâu** (`F-033`).

### 5.4 Khoảng trống ngữ nghĩa NHỎ NHẤT

Rút ra từ bảng trên, đúng năm việc — không hơn:

1. đổi hình dạng bản ghi sang đúng DM §11 (đổi tên 3 trường, thêm 16 trường);
2. nối `previous_state`/`new_state` vào **giá trị `ExecutionState` đã có** ở bước 12b;
3. mở phạm vi ghi tới các sự kiện engine **đã xảy ra sẵn** (không thêm hành vi nào);
4. bỏ cờ;
5. gắn nhãn `EXECUTED_EARLY` ở nơi engine **đã biết** đó là tranche kéo sớm.

### 5.5 Thông tin sự kiện có sẵn để dùng lại

| Nguồn engine ĐÃ CÓ | Dùng cho trường DM §11 |
|---|---|
| `regime.regime` (nhãn báo cáo §16) | `market_regime` |
| `dq` (bước 8, ST §3) | `data_quality` |
| `oscore` (bước 8) | `opportunity_score` |
| `base_pool`/`smart_pool`/`opp_fund` `.available/.reserved/.deployed` | snapshot vốn |
| `cfg.hash` / `exec_cfg.hash` (`config.py`, DM §14) | hai hash cấu hình |
| `Zone.zone_id` / `Zone.ladder_id` / `Zone.target_price` / `Zone.reserved_vnd` | `zone_id`, `ladder_id`, `recommended_price`, `recommended_vnd` |
| `zone_meta[zone_id]["recommended"]` (giá close lúc tạo action) | `recommended_price` của bản ghi fill |
| `counters["base_early"]`, nhánh `BASE_ADVANCE_SCORE` | nhãn `EXECUTED_EARLY` |
| `regime.last_entry_reason` | `CRASH_ENTRY_7D` / `CRASH_ENTRY_24H` |
| `br["opportunity_overflow_to_smart"]` | `CAP_OVERFLOW_TO_SMART` |

**Không một giá trị nào phải tính mới.** Mọi trường đều là phép ĐỌC một dữ kiện engine đã có
tại đúng thời điểm sự kiện xảy ra.

### 5.6 `previous_state` / `new_state` lấy từ đâu

Từ **đúng một chỗ**: biến `exec_state` do `derive_execution_state(...)` trả về ở bước 12b —
cùng giá trị mà `WP-C2` append vào `execution_state_timeline`. Bản ghi chuyển trạng thái được
sinh **bên trong chính khối `if` đã append timeline**, nên hai hình dạng không thể trôi khỏi
nhau. Chi tiết ngữ nghĩa: §6 và `docs/CONVENTIONS.md` #23(b)/(c).

### 5.7 Test được đóng băng TRƯỚC bản sửa

`tests/wp_c2_scenarios.py::fingerprint` được chụp trên cây mã tại HEAD `04f77ac` **trước khi
viết một dòng production nào**, sau khi `decision_log` rời khỏi `PRE_WP_C2_RESULT_FIELDS`
(lý do canonical: `WP-B3` sở hữu và cố ý đổi bề mặt đó). Bốn giá trị đóng băng:

    wait_only           = 6f39973c361124fd8174847c6543648fa4f0df0b56c1dac69811a36a51d3869a
    smart_action_cycle  = 9b273c446c71c367665ec79af9e429cb51e3b7c81357c24e922534c439b34f82
    data_invalid_window = b5d04b9bbfb0908500d4369ac1c8ef75020c7e35577475d318bcc23aa741c880
    crash_regime_cycle  = 206ab6d838bdbe507d9239ef0d8ba021c9952a0843266f4fce270aefc7b4f355

Đây là điều làm cho `CHECK-B3-07` là một phép so TRƯỚC–SAU thật, không phải một giá trị chép
lại từ kết quả sau khi sửa.

---

## 6. WP-C2 Contract Consumption

`WP-C2` là `DONE`. `WP-B3` **tiêu thụ**, không sửa:

| Thành phần WP-C2 | WP-B3 dùng như thế nào | Có sửa không |
|---|---|---|
| `ExecutionState` (6 giá trị) | giá trị của `previous_state`/`new_state` | **KHÔNG** |
| `derive_execution_state(...)` | không gọi thêm lần nào; chỉ đọc kết quả ở bước 12b | **KHÔNG** |
| Thứ tự ưu tiên `READY_TO_BUY > ACTION_PENDING > DATA_BLOCKED > COOLDOWN > WAIT` | dùng nguyên để đặt lý do cho trạng thái mới | **KHÔNG** |
| Điểm đo bước 12b (CONVENTIONS #22(b)) | dùng nguyên; không thêm điểm đo thứ hai | **KHÔNG** |
| `execution_state_timeline` | bản ghi chuyển trạng thái sinh trong CHÍNH nhánh append timeline | **KHÔNG** |
| `market_snapshots.execution_state` | không đụng tới; nằm trong khối BẤT BIẾN của phép đo | **KHÔNG** |
| `BACKTEST_NOT_APPLICABLE_STATES` (`ADR-001`) | dùng để khẳng định `FUNDING_REQUIRED` không bị bịa | **KHÔNG** |

Thay đổi DUY NHẤT chạm vào vùng mã WP-C2, và vì sao nó không phải sửa ngữ nghĩa:

    trước: open_actions = 0 ... open_actions += 1 ... action_open=open_actions > 0
    sau:   open_pairs   = [] ... open_pairs.append((z, lad)) ... action_open=bool(open_pairs)

`bool(danh sách)` ≡ `đếm > 0`, nên **giá trị đưa vào `derive_execution_state` không đổi**;
`WP-B3` chỉ cần thêm DANH TÍNH của action đang mở để đặt được mã zone ST §20 cho trạng thái
`ACTION_PENDING`. Bằng chứng: bốn fingerprint hành vi của `WP-C2` (chụp trước bản sửa) vẫn
trùng khớp, và 33 test `tests/test_wp_c2_execution_state.py` vẫn PASS nguyên.

**Không có `CONTRACT_CONFLICT`.** Sáu trạng thái đủ dùng; không tình huống nào đòi trạng thái
thứ bảy.

---

## 7. Change Budget

### 7.1 Trước khi sửa (dự kiến)

| Mục | Giá trị |
|---|---|
| File production dự kiến | `src/eth_dca_os/engine.py` — **1 file** (đúng Expected Touch Area) |
| LOC ước tính | ~200–280 dòng thêm, ~15 dòng đổi (đổi tên trường + bỏ cờ + mở phạm vi ghi) |
| Capability owner | `CAP-VERDICT` (lineage root `WP-B1`); `WP-B3` là thành viên thứ ba |
| Budget khả dụng | `CAP-VERDICT`: allowed theo bảng RISK MEDIUM = **2** · used = **0** · remaining = **2** |
| Loại thay đổi | **Implementation ban đầu** — `WP-B3` chưa từng `DONE` nên chưa có repair cycle nào để mở |

### 7.2 Sau khi sửa (đo, không cộng tay)

    git diff --shortstat 04f77ac -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    => 1 file changed, 266 insertions(+), 15 deletions(-)

| Mục | Số đo |
|---|---|
| File production đổi | **1** (`src/eth_dca_os/engine.py`) |
| +LOC / −LOC production | **+266 / −15** |
| Test mới | 3 file, 946 dòng (`test_wp_b3_audit_trail.py` 607, `wp_b3_scenarios.py` 156, `wp_b3_invariance_tool.py` 183) |
| Test thích ứng (không đổi ngữ nghĩa) | 9 file, +43/−27 |
| Docs / PROJECT | `docs/CONVENTIONS.md` +82; `docs/tasks/WP-B3-*.md` +269/−45; `PROJECT/HARDENING_BACKLOG.md` +108; `PROJECT/PROJECT_PROGRESS.md` +42/−2; ba file PROJECT khác +1/−1 mỗi file |
| **Repair cycle tiêu** | **0** — implementation ban đầu, không phải chu kỳ sửa |
| `CAP-VERDICT` budget sau phiên | allowed 2 · used **0** · remaining **2** (không đổi) |

Không REQUIRED check nào được thêm (vẫn 8). Effective Risk không tăng (Risk 2/4, Blast Radius
2/4 giữ nguyên — đầu ra tài chính bất biến bit-for-bit). Không kéo việc ngoài vertical slice.
**Không `CHANGE_BUDGET_EXCEEDED`.**

---

## 8. Implementation

Tất cả nằm trong `src/eth_dca_os/engine.py`. Bốn nhóm:

### 8.1 Vốn từ vựng (module level, thuần khai báo)

- `TRIGGER_TYPE_BY_REASON` — **một bảng tra tất định** `reason_code → trigger_type`, và là
  nguồn DUY NHẤT sinh ra `STRATEGY_REASON_CODES` (36 mã ST §20). Không chép danh mục hai lần.
- `TRIGGER_TYPES` — bảy giá trị DM §11.
- `DECISION_LOG_FIELDS` (20) và `DECISION_LOG_NOT_NULL_FIELDS` (11).
- `BACKTEST_NOT_EMITTED_REASONS` — ba mã không bao giờ ghi, **kèm lý do** (cùng khuôn với
  `BACKTEST_NOT_APPLICABLE_STATES` của WP-C2).
- `REASON_CODES_RECORDED_AS_TAG`, `AUDIT_TAGS`.
- `zone_reason_code(ladder_type, zone_index)` — mã zone ST §20, **cùng vốn từ vựng** mà
  `Pool._log` đã ghi khi reserve.

### 8.2 `log(...)` — bản ghi canonical

Chữ ký mới: `log(ts, reason, *, zone_id, ladder_id, recommended_price, recommended_vnd,
previous_state, new_state, tags)`. Thuần quan sát: chỉ ĐỌC trạng thái engine, append vào
`res.decision_log`. `decision_id = len(res.decision_log) + 1` (khoá theo run, tất định).
`previous_state`/`new_state` mặc định = trạng thái đang hiệu lực (`exec_state_now`).
Hai hash cấu hình tính **một lần mỗi run**, không tính lại mỗi dòng.

### 8.3 `state_entry_reason(...)` — lý do của một lần chuyển trạng thái

Hàm thuần, trả `(reason_code, zone_id, ladder_id)` theo đúng thứ tự ưu tiên đã đóng băng của
`WP-C2`. Với `READY_TO_BUY` / `ACTION_PENDING`, action được chọn bằng **`zone_order_key`** —
đúng khoá thứ tự canonical mà bước 15 dùng để sắp fill, không phải một quy tắc mới.

### 8.4 Điểm ghi (chỉ thêm lời gọi, không đổi nhánh nào)

| Bước BT §19 | Sự kiện | Mã ghi |
|---|---|---|
| 5–6 | contribution vượt cap Opportunity | `CAP_OVERFLOW_TO_SMART` |
| 8 | nhãn chất lượng dữ liệu đổi | `DATA_INVALID` / `DATA_DEGRADED` |
| 9 / 16–17 (qua `record_purchase`) | mọi purchase | `BASE_SCHEDULE`, `BASE_ADVANCE_SCORE`, `MONTH_END_BASE`, `MONTH_END_SMART`, `SMART_ZONE_S*`, `OPPORTUNITY_O*`, `CRASH_ZONE_C*` |
| 16–17 (qua `record_purchase`) | fill mở cooldown | `COOLDOWN_START` |
| 10 | chuyển trạng thái NỀN của regime | `CRASH_ENTRY_7D` / `CRASH_ENTRY_24H` / `CRASH_EXIT` / `RECOVERY_END` |
| 12 | action hết hạn / lỡ hẹn | `ACTION_TTL_EXPIRED` / `ACTION_MISSED` |
| **12b** | **chuyển Execution State** | mã của dữ kiện quyết định trạng thái mới (§10) |
| 14a / 14b | zone được reserve (recommendation) | `CRASH_ZONE_C*` / `SMART_ZONE_S*` / `OPPORTUNITY_O*` |
| 14c | chặn bởi trần zone / daily limit / override | `MAX_ZONES_BLOCK`, `DAILY_LIMIT_BLOCK`, `COOLDOWN_OVERRIDE` |
| 18a / 18b / 18d + month rollover | vòng đời ladder/zone | `BULLISH_INVALIDATION`, `OPPORTUNITY_SUSPENDED`, `LADDER_EXPIRED` |

**Không một nhánh `if` nào của engine bị đổi điều kiện.** Chỗ duy nhất cấu trúc thay đổi là
`for z in candidates` → `for k, z in enumerate(candidates)` để ghi được `MAX_ZONES_BLOCK` cho
đúng những zone bị trần chặn; `break` giữ nguyên vị trí.

### 8.5 Bỏ cờ

`run_engine(..., log_decisions=False)` → tham số **bị gỡ**. Tám vị trí trong `tests/` truyền cờ
được cập nhật; **không đường production nào truyền nó**, nên không consumer nào bị ảnh hưởng.

---

## 9. Canonical Audit Record

Hình dạng một bản ghi (`engine.DECISION_LOG_FIELDS`) — 19 trường DM §11 + `tags`:

| Trường | Nguồn | Null được? |
|---|---|---|
| `decision_id` | bộ đếm 1..N theo run | KHÔNG |
| `timestamp_utc` | `ts` của nến (epoch giây) | KHÔNG |
| `previous_state` / `new_state` | `ExecutionState` (WP-C2) | chỉ trước lần đo đầu tiên — **0 lần** trên production |
| `market_regime` | `regime.regime` (nhãn ST §16) | KHÔNG |
| `data_quality` | `dq` (bước 8) | KHÔNG |
| `trigger_type` | tra từ `reason_code` | KHÔNG |
| `reason_code` | danh mục ST §20 | KHÔNG |
| `opportunity_score` | `oscore` thô | có (chưa có snapshot daily) |
| `recommended_price` | giá mục tiêu zone / giá close lúc tạo action | có |
| `recommended_vnd` / `recommended_usdt_est` | lượng vốn quyết định cam kết; bằng nhau (BT §2.1 [F6]) | có |
| `zone_id` / `ladder_id` | danh tính zone/ladder | có |
| `available_vnd` / `reserved_vnd` / `deployed_vnd` | tổng ba pool tại thời điểm sự kiện | KHÔNG |
| `strategy_config_hash` / `execution_config_hash` | `cfg.hash` / `exec_cfg.hash` (DM §14) | KHÔNG |
| `tags` | `EXECUTED_EARLY` (ST §9), `DELAYED_DATA_FILL`, `EXECUTION_DATA_GAP` (BT §18) | luôn là list |

Năm bản ghi thật, đọc nguyên văn từ run toàn kỳ `gate3_realistic` (dataset synthetic 7,5 năm):

    id=689  2021-12-20T00:00:00Z  CRASH_ENTRY_7D (regime)
      WAIT -> WAIT | regime=CRASH dq=GOOD oscore=83,876
      zone=None ladder=None
      A/R/D = 108,9564 / 0,0000 / 3491,0436
      cfg = f782f99077fe… / 789bd885640f…   tags=[]

    id=423  2020-10-02T00:00:00Z  BASE_ADVANCE_SCORE (base)
      COOLDOWN -> COOLDOWN | regime=STRESSED dq=GOOD oscore=71,445 | rec_vnd=20,0
      A/R/D = 123,2622 / 27,1765 / 2049,5613
      cfg = f782f99077fe… / 789bd885640f…   tags=['EXECUTED_EARLY']

    id=6    2019-01-04T05:30:00Z  SMART_ZONE_S0 (zone)
      ACTION_PENDING -> READY_TO_BUY | regime=STRESSED dq=GOOD oscore=35,812
      zone=16339 ladder=4566
      A/R/D = 79,3038 / 0,6962 / 20,0000
      cfg = f782f99077fe… / 789bd885640f…   tags=[]

    id=425  2020-10-10T00:15:00Z  OPPORTUNITY_SUSPENDED (zone)
      WAIT -> WAIT | regime=NORMAL dq=GOOD oscore=49,734 | rec_price=410,5420 rec_vnd=0,0
      A/R/D = 123,2622 / 27,1765 / 2049,5613

    id=51   2019-02-28T17:00:00Z  CAP_OVERFLOW_TO_SMART (month_end)
      COOLDOWN -> COOLDOWN | regime=NORMAL dq=GOOD oscore=20,346 | rec_vnd=9,7528
      A/R/D = 169,7528 / 0,0000 / 130,2472

Mỗi dòng tự trả lời đủ năm câu hỏi của `CHECK-B3-06` mà không cần chạy lại engine.

**Ba trường được đổi tên, không mất thông tin:** `ts → timestamp_utc`, `zone → zone_id`,
`ladder → ladder_id`. Log cũ phân biệt được với log mới vì thiếu
`strategy_config_hash`/`execution_config_hash` — đúng cơ chế mà mục "Migration Impact" của file
task yêu cầu.

---

## 10. Reason / Trigger Semantics

**Nguyên tắc: mọi lý do đến từ một dữ kiện engine có thật, và mọi mã đến từ ST §20.**
`WP-B3` không phát minh mã nào — `test_b3_03_reason_code_catalogue_matches_the_spec_text` đối
chiếu tập mã với **chính văn bản spec**.

### 10.1 Lý do của một sự kiện

Mã của chính sự kiện đó, như engine đã gọi nó: một purchase Base theo lịch là `BASE_SCHEDULE`,
một zone Smart được reserve là `SMART_ZONE_S{i}` (đúng mã ledger đã dùng), một lần override
cooldown là `COOLDOWN_OVERRIDE`. Không có lớp diễn giải nào ở giữa.

### 10.2 Lý do của một lần CHUYỂN trạng thái

Dữ kiện quyết định trạng thái **MỚI**, theo đúng thứ tự ưu tiên đã đóng băng ở CONVENTIONS
#22(c) — tức theo hành vi engine, không theo thẩm mỹ:

| `new_state` | Dữ kiện quyết định | `reason_code` |
|---|---|---|
| `READY_TO_BUY` | một action tới hạn và còn TTL | mã zone của action đó (`zone_order_key` chọn) |
| `ACTION_PENDING` | một action đang mở, chưa tới hạn | mã zone của action đó (cùng khoá) |
| `DATA_BLOCKED` | `dq == "INVALID"` | `DATA_INVALID` |
| `COOLDOWN` | trong cooldown và override không kích hoạt | `COOLDOWN_START` |
| `WAIT` | mọi điều kiện trên đều hết hiệu lực | mã của dữ kiện vừa CHẤM DỨT |

Khi nhiều nguyên nhân cùng đúng, thứ tự đã có sẵn của engine quyết định — **không có lớp chính
sách mới**. Chiều VÀO hay RA đọc được không nhập nhằng từ cặp (`previous_state`, `new_state`)
trên chính bản ghi.

`WAIT` là trạng thái "không điều kiện nào còn hiệu lực" nên không có dữ kiện nào để đặt tên.
ST §20 **không có mã** cho "cooldown hết hạn" và "chất lượng dữ liệu trở lại GOOD" — đây là
khiếm khuyết ĐẶC TẢ, không phải khiếm khuyết mã, và gói này **không lấp nó bằng mã tự chế**.
Ghi nhận: `PROJECT/HARDENING_BACKLOG.md` **H-37**, owner `CAP-SPEC`/`WP-D2` (Master Index §6
cấm vá V2.1.5).

### 10.3 `trigger_type`

Bảng tra tất định `engine.TRIGGER_TYPE_BY_REASON`; mỗi mã ST §20 thuộc đúng một trong bảy
nhóm DM §11. Phân bố đo được trên run toàn kỳ `gate3_realistic` (2.478 bản ghi):
`cooldown` 1.019 · `zone` 955 · `base` 270 · `month_end` 172 · `regime` 62 · `funding` **0**
(đúng `ADR-001`) · `data` 0 (dataset synthetic không có ngày INVALID).

---

## 11. Execution State Transitions

Số đo trên run toàn kỳ (đường production thật):

| Run | Mốc `execution_state_timeline` | Bản ghi chuyển trạng thái | Khớp |
|---|---|---|---|
| `gate1_low_friction` | 1.044 | 1.043 | = mốc − 1 ✅ |
| `gate3_realistic` | 1.078 | 1.077 | = mốc − 1 ✅ |

`test_b3_02_every_wp_c2_transition_has_exactly_one_audit_record` kiểm **từng cặp**
`(ts, previous, new)` khớp đúng mốc timeline tương ứng — không thừa, không thiếu, không lệch
thứ tự.

Các chuyển trạng thái đại diện, tất cả sinh bởi hành vi engine THẬT:

| Chuyển | Kịch bản | Lý do ghi |
|---|---|---|
| `WAIT → ACTION_PENDING` | `smart_action_cycle` (WP-C2) | `SMART_ZONE_S0` |
| `ACTION_PENDING → READY_TO_BUY` | `smart_action_cycle` | `SMART_ZONE_S0` |
| `READY_TO_BUY → COOLDOWN` | `smart_action_cycle` | `COOLDOWN_START` |
| `COOLDOWN → WAIT` | `smart_action_cycle` | `COOLDOWN_START` (dữ kiện chấm dứt) |
| `COOLDOWN → DATA_BLOCKED` | `data_invalid_window` (WP-C2) | `DATA_INVALID` |
| `DATA_BLOCKED → WAIT` | `data_invalid_window` | `DATA_INVALID` (dữ kiện chấm dứt) |

Không chuyển trạng thái nào được dựng bằng tay để lấy độ phủ.

---

## 12. ADR-001 Compliance

`ADR-001` (Accepted 2026-09-04, `DEC-035`) giữ nguyên hiệu lực và **không bị sửa một chữ**.

- `FUNDING_REQUIRED` **không bao giờ** xuất hiện trong `decision_log`: không ở
  `previous_state`/`new_state`, không ở `reason_code`, và `trigger_type == "funding"` có
  **0 bản ghi** trên toàn bộ 5.614 bản ghi quan sát được
  (`test_b3_03_funding_required_is_never_fabricated_in_backtest`).
- Hai mã ST §20 tương ứng (`FUNDING_REQUIRED`, `FUNDING_COMPLETE`) được **tuyên bố tường minh**
  trong `engine.BACKTEST_NOT_EMITTED_REASONS` kèm lý do, chứ không vắng mặt im lặng — cùng
  khuôn với `BACKTEST_NOT_APPLICABLE_STATES` mà `WP-C2` đã lập.
- Giá trị `FUNDING_REQUIRED` **vẫn nằm trong enum** vì Product Spec §6/§7/§11 bắt buộc nó ở
  tầng app; test khẳng định lại điều đó.
- Không transition nào bị bịa ra chỉ để lấy độ phủ test.

---

## 13. Adversarial Tests

`tests/test_wp_b3_audit_trail.py` — **43 test**. Ánh xạ tới danh sách A–L của đề bài §17:

| # | Yêu cầu đối kháng | Test | Kết quả |
|---|---|---|---|
| A | Không có enum ExecutionState thứ hai | `test_b3_02_no_second_execution_state_vocabulary` — quét TOÀN BỘ `src/eth_dca_os/` | PASS |
| B | Hai trường serialize bằng giá trị canonical WP-C2 | `test_b3_02_states_serialise_as_plain_strings`, `..._are_the_wp_c2_enum_itself` | PASS |
| C | Ghi log không thể đổi hành vi tài chính | `test_b3_07_removing_the_audit_layer_changes_no_behaviour` (gỡ hẳn lớp log) | PASS |
| D | Chuyển trạng thái thật sinh bản ghi | `test_b3_02_every_wp_c2_transition_has_exactly_one_audit_record` | PASS |
| E | Nhiều chuyển trạng thái giữ đúng thứ tự thời gian | cùng test trên + `test_b3_07_records_are_chronological_and_uniquely_keyed` | PASS |
| F | Trường bắt buộc không âm thầm null | `test_b3_01_mandatory_fields_are_never_null` (11 trường × 5.614 bản ghi) | PASS |
| G | `DATA_BLOCKED` quy được về hành vi chất lượng dữ liệu thật | `test_b3_03_data_blocked_is_attributable_to_real_data_quality` | PASS |
| H | Vòng đời `ACTION_PENDING → READY_TO_BUY` được biểu diễn đúng | `test_b3_03_action_lifecycle_is_represented_for_one_zone` | PASS |
| I | Chuyển trạng thái liên quan cooldown đúng | `test_b3_03_cooldown_transition_follows_a_real_cooldown_event` | PASS |
| J | Không bịa `FUNDING_REQUIRED` trong backtest | `test_b3_03_funding_required_is_never_fabricated_in_backtest` | PASS |
| K | Quan sát lặp lại không sinh sự kiện nghiệp vụ giả | `test_b3_07_audit_trail_is_deterministic_across_replays`, `..._uniquely_keyed` | PASS |
| L | Thông tin `decision_log` cũ không mất | `test_b3_03_legacy_events_survive_the_migration` | PASS |

Thêm ba phép thử không nằm trong danh sách nhưng cần cho tính đúng đắn:

- `test_b3_01_capital_snapshot_reconciles_with_the_contribution_ledger` — snapshot vốn không
  chỉ khác null mà **đúng**: `A + R + D` = (số contribution) × 100 tại **mọi** bản ghi (DM §14).
- `test_b3_zone_reason_code_matches_the_pool_ledger_vocabulary` — audit trail và `Pool.ledger`
  (DM §6) nói **cùng một thứ tiếng**, nên đối chiếu được với nhau.
- `test_b3_action_ttl_expired_is_unreachable_when_ttl_is_a_multiple_of_the_candle` — khoá lại
  quan sát H-36 về chính engine.

Mọi khẳng định "không có X" đều đi kèm khẳng định "có Y" tương ứng (chống PASS rỗng): ví dụ
test gỡ lớp log khẳng định `decision_log == []` để chứng minh phép gỡ có hiệu lực, và test
`FUNDING_REQUIRED` khẳng định enum VẪN giữ giá trị đó cho tầng app.

---

## 14. Financial / Strategy Invariance

Công cụ: `tests/wp_b3_invariance_tool.py` — cùng họ với `wp_a3_impact_tool.py`,
`wp_a6_impact_tool.py`, `wp_c2_invariance_tool.py`. Chạy được ở CẢ HAI phía của thay đổi, ghi
payload JSON chuẩn tắc để so **bit-for-bit**.

**Khối BẤT BIẾN** (phải trùng khớp tuyệt đối):

- `dataset_hash`, `strategy_config_hash`, hai `execution_config_hash`;
- **Gate 1** — chín window, AE từng window, AnchorSetMedian / PrimaryMedian / PooledMedian, OOS,
  benchmark, diagnostics, bootstrap, concentration, cash ratio, opportunity-cap-hit,
  regime-advantage, counters, lineage, run record;
- **Gate 2**, **Gate 3**, **Control F/G**, **verdict**;
- **hai lần chạy engine toàn kỳ** (2019-01-01 → OOS end, cả hai execution config đã commit) với
  TỪNG bản ghi: `purchases`, `contributions`, `counters`, `monthly_deployments`,
  `cash_samples`, `opp_cap_samples`, `regime_timeline`, `eth_total`, `contributed_total`;
- **cộng thêm** `execution_state_timeline` và `market_snapshots` — đầu ra của `WP-C2`, mà
  `WP-B3` tiêu thụ chứ không được đổi.

**Ngoài khối bất biến:** `decision_log` — đúng bề mặt gói này cố ý thay đổi. Không trường nào
khác bị loại; metadata không ngữ nghĩa (`run_id`, `created_at`, `metrics_path`, `code_commit`)
bị loại tường minh và có danh sách đầy đủ trong mã công cụ.

Cùng dataset (synthetic seed cố định `synth.SYNTH_SEED`, cùng thư mục raw), cùng config, cùng
seed, cùng đường production:

    TRƯỚC (HEAD 04f77ac, production chưa sửa)
      invariance_sha256 = 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7
      invariance_bytes  = 3.728.853
      decision_log      = 0 bản ghi (cả hai run toàn kỳ)

    SAU (bản sửa WP-B3)
      invariance_sha256 = 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7
      invariance_bytes  = 3.728.853
      decision_log      = 2.441 / 2.478 bản ghi

**TRÙNG KHỚP BIT-FOR-BIT.** Không có `BEHAVIOR_CHANGED`. Không một khác biệt nào bị
"normalize" đi.

Hai phép thử độc lập ở tầng test, không dùng công cụ trên:

1. `test_b3_07_engine_behaviour_is_identical_with_the_audit_layer` — bốn fingerprint kịch bản
   bằng đúng giá trị **chụp trước bản sửa** (§5.7).
2. `test_b3_07_removing_the_audit_layer_changes_no_behaviour` — **gỡ bỏ hoàn toàn lớp ghi log**
   (`RunResult.decision_log` thay bằng danh sách nuốt mọi `append`) rồi chạy lại: fingerprint
   vẫn trùng khớp, và `decision_log == []` chứng minh phép gỡ thực sự có hiệu lực. Đây là bằng
   chứng HÀNH VI cho "log quan sát, không điều khiển" — không phụ thuộc vào cách viết mã.

**Hiệu năng** (đo trong chính hai lần chạy trên): pipeline gates 261,9s → 277,1s (+5,8%); engine
toàn kỳ 7,17s → 6,68s / 5,96s. Không phát sinh escalation `SCOPE_CHANGED` về hiệu năng; không
cần cắt trường bắt buộc nào của DM §11.

---

## 15. Production Reachability

Unit test là không đủ. Bằng chứng dưới đây đến từ **đường production thật**.

### 15.1 Đường chạy đã dùng

| Đường | Gọi qua | Kết quả |
|---|---|---|
| Pipeline đầy đủ (Gate 1/2/3 + controls + verdict) | `tests/wp_b3_invariance_tool.py` → `pipeline.run_gate1/2/3`, `run_controls`, `run_verdict` | chạy trọn, không cờ nào được bật |
| Engine toàn kỳ × 2 execution config | `engine.run_engine` | 2.441 / 2.478 bản ghi |
| Window path của Gate 1 | `metrics.run_window` (ĐÚNG hàm Gate 1 gọi cho từng window) | `test_b3_04_production_window_path_writes_the_log` |
| Sáu kịch bản engine tất định | `tests/wp_b3_scenarios.py` → `engine.run_engine` | các loại sự kiện còn lại |
| Bốn kịch bản của WP-C2 | `tests/wp_c2_scenarios.py` → `engine.run_engine` | vòng đời action, cửa sổ INVALID, crash |

**Tổng: 12 lần chạy `run_engine` thật, 5.614 bản ghi audit.** Không bản ghi nào được dựng bằng
tay trong test.

### 15.2 Anti-vacuity

- Trước gói: **0 bản ghi** trên đường production → chứng minh `F-024` bằng số, không bằng lời.
- Sau gói: **2.441 / 2.478 bản ghi**, **25 loại sự kiện** khác nhau.
- Mọi test đếm đều có ngưỡng dưới tường minh (`> 1000` bản ghi, `> 100` bản ghi mang lượng vốn,
  `>= 100` bản ghi fill khớp purchase, `> 20` bản ghi trên window path).

### 15.3 Phân bố mã trên run toàn kỳ

| `reason_code` | `gate1_low_friction` | `gate3_realistic` |
|---|---|---|
| `BASE_ADVANCE_SCORE` | 66 | 66 |
| `BASE_SCHEDULE` | 204 | 204 |
| `BULLISH_INVALIDATION` | 21 | 21 |
| `CAP_OVERFLOW_TO_SMART` | 88 | 88 |
| `COOLDOWN_OVERRIDE` | 34 | 37 |
| `COOLDOWN_START` | 946 | 982 |
| `CRASH_ENTRY_24H` | 4 | 4 |
| `CRASH_ENTRY_7D` | 17 | 17 |
| `CRASH_EXIT` | 21 | 21 |
| `CRASH_ZONE_C0` … `C3` | 66 / 27 / 23 / 17 | 66 / 27 / 23 / 17 |
| `LADDER_EXPIRED` | 12 | 12 |
| `MONTH_END_SMART` | 84 | 84 |
| `OPPORTUNITY_O0` … `O4` | 39 / 23 / 17 / 14 / 14 | 39 / 23 / 17 / 14 / 14 |
| `OPPORTUNITY_SUSPENDED` | 21 | 21 |
| `RECOVERY_END` | 20 | 20 |
| `SMART_ZONE_S0` … `S2` | 265 / 220 / 178 | 265 / 220 / 176 |
| **TỔNG** | **2.441** | **2.478** |

Bảy mã còn lại được quan sát trên kịch bản tất định: `MAX_ZONES_BLOCK`, `ACTION_MISSED`,
`ACTION_TTL_EXPIRED`, `DATA_DEGRADED`, `DATA_INVALID`, `MONTH_END_BASE`, `DAILY_LIMIT_BLOCK`.

### 15.4 Kiểm chứng nguồn gốc giá trị

- `previous_state`/`new_state` khớp **từng cặp** với `execution_state_timeline` của `WP-C2`.
- `reason_code` của bản ghi zone khớp mã mà `Pool.ledger` đã ghi khi reserve.
- snapshot vốn thoả bất biến DM §14 tại **mọi** bản ghi.
- bản ghi fill khớp đúng purchase (cùng `ts`, cùng lượng vốn) — ≥100 cặp.

---

## 16. Full Regression

Toàn bộ suite Python áp dụng được, **không skip, không deselect, không `-k`**:

    $ python -m pytest --color=no -p no:cacheprovider -rA --durations=10

    ........................................................................ [ 13%]
    ........................................................................ [ 26%]
    ........................................................................ [ 40%]
    ........................................................................ [ 53%]
    ........................................................................ [ 67%]
    ........................................................................ [ 80%]
    ........................................................................ [ 93%]
    ...................................                                      [100%]

    ==================================== PASSES ====================================
    ============================= slowest 10 durations =============================
    168.36s call     tests/test_e2e.py::test_full_pipeline_smoke
     84.68s call     tests/test_wp_a1_provenance.py::test_a1_02_manifest_hash_gate2_gate3
     83.72s call     tests/test_wp_a1_provenance.py::test_a1_06_synthetic_not_official_in_gate2_gate3
     70.65s call     tests/test_e2e.py::test_gate1_reproducible
     61.08s call     tests/test_wp_a1_provenance.py::test_a1_09_reproducibility_same_seed_same_metrics
     53.19s call     tests/test_cli.py::test_cli_full_flow
     36.14s setup    tests/test_wp_a2_pipeline_wiring.py::test_a2_01_benchmarks_bcd_run_and_present
     29.60s setup    tests/test_wp_a1_provenance.py::test_a1_01_run_record_has_all_provenance_fields
     16.56s call     tests/test_wp_a1_provenance.py::test_a1_07_dev_limit_still_forces_non_official
     15.34s setup    tests/test_wp_b3_audit_trail.py::test_b3_01_record_shape_is_exactly_the_data_model_table
    =========================== short test summary info ============================
    537 passed in 754.35s (0:12:34)
    EXIT_CODE=0

| Mục | Số |
|---|---|
| collected | **537** |
| passed | **537** |
| failed | **0** |
| errors | **0** |
| skipped | **0** |
| xfail / xpass | **0 / 0** |
| exit code | **0** |
| thời gian | 754,35s (12:34) |

Đối chiếu số: baseline tại HEAD `04f77ac` (đo TRƯỚC bản sửa, cùng interpreter, cùng lockfile)
= **494 passed, exit 0**. Sau bản sửa = **537** = 494 + **43 test mới** của
`tests/test_wp_b3_audit_trail.py`. **Không test cũ nào bị xoá, bị đổi ngữ nghĩa, hay bị bỏ
qua**: chín file test được sửa chỉ để thích ứng với hai thay đổi hợp đồng (bỏ tham số
`log_decisions`; ba trường đổi tên sang tên canonical DM §11) — mọi khẳng định của chúng giữ
nguyên.

Riêng `tests/test_wp_c2_execution_state.py` có bốn giá trị fingerprint được **chụp lại trên cây
mã TRƯỚC bản sửa** sau khi `decision_log` rời tập trường bất biến (lý do canonical ở §5.7);
33/33 test của `WP-C2` vẫn PASS nguyên, gồm cả bốn test `CHECK-C2-06` "hành vi bit-identical"
và bốn test `CHECK-C2-07` "ép trạng thái sai không đổi hành vi".

Runtime dài không phải lý do để làm yếu suite: không một test nào bị `-k`, `--deselect`,
`skip` hay `xfail` để lấy màu xanh.

---

## 17. Completion Gate Matrix

Tám REQUIRED check, ĐÚNG như đã đóng băng 2026-08-23 (T-04/S002). Không check nào bị viết lại,
bị hạ mức evidence, hay bị đánh `NOT_APPLICABLE`. Gate của gói này **không đòi E2 ở bất kỳ
check nào** (`Risk = 2 → E1`), nên không có check nào bị tự chứng nhận E2.

| Check | Yêu cầu (nguyên văn rút gọn) | Evidence level | Evidence | Kết quả | Artifact / test |
|---|---|---|---|---|---|
| **B3-01** | `decision_log` chứa đủ trường theo DM §11 | E1 | 19 trường DM §11 + `tags`, đối chiếu THẲNG với bảng spec; 0 null trên 11 trường bắt buộc × 5.614 bản ghi; snapshot vốn thoả bất biến DM §14 | **PASS** | `test_b3_01_*` (4 test) |
| **B3-02** | `previous_state`/`new_state` dùng đúng enum WP-C2 | E1 | `isinstance(ExecutionState)`; chỉ MỘT vốn từ vựng trạng thái trong toàn `src/`; bản ghi chuyển = mốc timeline − 1 (1.043/1.077) | **PASS** | `test_b3_02_*` (5 test) |
| **B3-03** | Phạm vi loại sự kiện phủ đủ theo ST §20 | E1 | danh mục đọc từ văn bản spec = 36 mã; **32 mã được ghi**; 4 mã còn lại có lý do canonical trong mã nguồn | **PASS** | `test_b3_03_*` (13 test) |
| **B3-04** | Official run luôn ghi log, không phụ thuộc cờ | E1 | cờ bị GỠ khỏi chữ ký; `metrics.run_window` ghi log không cờ; production 0 → 2.441/2.478 bản ghi | **PASS** | `test_b3_04_*` (2 test) |
| **B3-05** | Base execute sớm mang nhãn `EXECUTED_EARLY` | E1 | 3/3 bản ghi kéo sớm mang nhãn, khớp `counters["base_early"]`; ngày gốc không lặp lại; nhãn KHÔNG lên purchase record | **PASS** | `test_b3_05_*` (3 test) |
| **B3-06** | Từ log tái dựng được lý do một quyết định | E1 | ba quyết định ở ba `trigger_type`, mỗi câu trả lời đối chiếu với nguồn ĐỘC LẬP; ≥100 bản ghi fill khớp purchase | **PASS** | `test_b3_06_*` (2 test) |
| **B3-07** | Hành vi quyết định của engine không đổi | E1 | payload 3.728.853 byte, `sha256 3ea7c8d7…` TRÙNG trước–sau; gỡ hẳn lớp log vẫn trùng fingerprint chụp trước bản sửa | **PASS** | `wp_b3_invariance_tool.py`, `test_b3_07_*` (11 test) |
| **B3-08** | Toàn bộ test suite PASS | E1 | xem §16 | **PASS** | output đầy đủ ở §16 |

**8/8 REQUIRED PASS. 0 FAIL. 0 BLOCKED.**

---

## 18. Findings

Phân loại theo `governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing. **Finding không phải
task; không task ID nào được tạo.**

| ID | Nội dung | Phân lớp | Định tuyến |
|---|---|---|---|
| `F-024` | `decision_log` thiếu trường và thiếu loại sự kiện theo DM §11 / ST §20 | **ĐÓNG** | `CHECK-B3-01`, `-03`, `-04` PASS |
| `F-033` | Base execute sớm không mang nhãn `EXECUTED_EARLY` theo ST §9 | **ĐÓNG** | `CHECK-B3-05` PASS |
| `H-36` | Nhánh `ACTION_TTL_EXPIRED` không tới lượt khi TTL là bội số của nến 15m | CONFIRMED **HARDENING** | `CAP-ENGINE`/`WP-A3`; có RE_TRIGGER |
| `H-37` | ST §20 thiếu mã cho hai lần chuyển trạng thái có thật | CONFIRMED **HARDENING** | `CAP-SPEC`/`WP-D2`; có RE_TRIGGER |
| `H-38` | `task_registry_snapshot.sh` bỏ sót `IMPLEMENTED`/`VERIFYING` khi đếm SET A | CONFIRMED **HARDENING** | `CAP-GOVTOOL`, `OWNER_ASSIGNMENT_REQUIRED` (cùng khe `H-08`); có RE_TRIGGER |

**Không finding nào đạt BLOCKING.** Phép thử canonical đòi đồng thời ba điều: đường production
hiện tại, hậu quả nghiệp vụ nằm trong một Completion Gate hoặc risk register, và bằng chứng tái
lập được. `H-36` không đổi một con số tài chính nào và không REQUIRED check nào phân biệt hai
mã; `H-37` là khiếm khuyết đặc tả, không phải khiếm khuyết mã, và mọi chuyển trạng thái vẫn có
bản ghi hợp lệ; `H-38` là tooling governance, không nằm trong `PRODUCTION_PATHS.md`.

**Không sửa vấn đề không liên quan chỉ vì nó ở gần.** Cụ thể đã KHÔNG làm: không sửa
`task_registry_snapshot.sh`; không sửa hai validator kiểm 0 bản ghi (`H-08`); không đụng
`ACTION_TTL_EXPIRED`; không mở rộng `market_snapshots` theo `H-34`.

---

## 19. Hardening

Ba mục mới, mỗi mục có `RE_TRIGGER_CONDITION` cụ thể (bắt buộc theo `REVIEW_PROTOCOL.md`):

**H-36** — `ACTION_TTL_EXPIRED` không tới lượt khi `action_ttl_seconds % 900 == 0`.
Re-trigger: (a) một cấu hình production có TTL lệch lưới nến được đưa vào lưới sensitivity hoặc
cấu hình chạy thật; (b) tầng app/live phân biệt "hết TTL" với "lỡ hẹn" ở mức nghiệp vụ; (c)
nhịp nến execution đổi khỏi 15m.

**H-37** — ST §20 thiếu mã cho `COOLDOWN → WAIT` (hết hạn) và `DATA_BLOCKED → WAIT` (dữ liệu
trở lại GOOD). Re-trigger: (a) `WP-D2` mở phiên soạn đề xuất V2.2; (b) một tiêu dùng thật đòi
phân biệt VÀO/RA chỉ bằng `reason_code`; (c) Owner Decision cho phép mở rộng danh mục trong
phạm vi V2.1.5.

**H-38** — `task_registry_snapshot.sh` bỏ sót hai trạng thái vòng đời hợp lệ. Re-trigger:
(a) `CAP-GOVTOOL` được cấp owner; (b) một quyết định governance dựa trực tiếp vào
`count_roadmap_task_ids`; (c) vòng đời task được sửa đổi.

Toàn văn: `PROJECT/HARDENING_BACKLOG.md`.

---

## 20. Production Diff

    git diff --shortstat 04f77ac -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    1 file changed, 266 insertions(+), 15 deletions(-)

Đúng **một** file production: `src/eth_dca_os/engine.py` — nằm trọn trong Expected Touch Area
("`src/eth_dca_os/engine.py` — phần ghi log").

15 dòng bị đổi/xoá, liệt kê đủ:

| Dòng cũ | Vì sao đổi |
|---|---|
| 3 dòng chữ ký `run_engine` (`log_decisions`) | bỏ cờ — `CHECK-B3-04` |
| 3 dòng thân `log()` cũ | thay bằng bản ghi canonical DM §11 |
| 1 dòng `open_actions = 0` | → `open_pairs = []` (cần danh tính action, giá trị đưa vào WP-C2 không đổi) |
| 1 dòng `open_actions += 1` | → `open_pairs.append(...)` |
| 1 dòng `action_open=open_actions > 0` | → `action_open=bool(open_pairs)` |
| 1 dòng `log(ts, regime.last_entry_reason, ladder=...)` | tách sự kiện regime (bước 10) khỏi sự kiện reservation (bước 14a) |
| 3 dòng `log(..., zone=...)` / `ladder=...` | đổi tên tham số sang `zone_id`/`ladder_id` (DM §11) |
| 1 dòng `for z in candidates:` | → `for k, z in enumerate(candidates)` để ghi được `MAX_ZONES_BLOCK` |
| 1 dòng `release_zone` (18b) | thêm đọc `amt` TRƯỚC release |

Không dòng nào đổi điều kiện của một nhánh execution.

Ngoài production: `docs/CONVENTIONS.md` (+82, quy ước #23), `docs/tasks/WP-B3-*.md` (+269/−45,
điền evidence vào gate đã đóng băng — không sửa câu chữ yêu cầu), `PROJECT/*` (+153/−5),
`tests/` (3 file mới 946 dòng + 9 file thích ứng +43/−27), báo cáo và biên bản phiên.

`webapp/`, `docs/spec/`, `pyproject.toml`, `pyproject.lock`: **diff rỗng**.

---

## 21. Validators

| Validator | Kết quả | Ghi chú |
|---|---|---|
| `branch_authority_check.sh` | xem §2 và §25 | FAIL trước push chỉ vì thiếu upstream; PASS sau push |
| `validate_structure.py` | **PASS** | 27 required path |
| `validate_governance.py` | **PASS** | 7 CORE file, 7 PROJECT file, 5 hard-stop, 26 source invariant, 37 hardening item, 13 production path row, 22 task file |
| `validate_project_state.py` | **PASS** | |
| `validate_routing.py` | **PASS** | 19 MAJOR task file, 0 manual override |
| `validate_evidence.py` | PASS **nhưng VACUOUS** | "Checked 0 REQUIRED PASS evidence record(s)" — validator glob `TASK-*.md` trong khi task file của repo tên `WP-*`/`T-*`. Đây là `H-08` đã ghi nhận từ trước; theo `STATE_AUTHORITY.md` § Vacuous Validation, **không tính là bằng chứng có ý nghĩa**. Phiên này KHÔNG sửa tooling governance (đề bài §24) |
| `validate_task_completion.py` | PASS **nhưng VACUOUS** | "Checked 0 DONE task(s)" — cùng nguyên nhân `H-08` |
| `validate_easy_roadmap.py` | **PASS** sau khi chạy `sync_easy_roadmap.py` | File `PROJECT/LO_TRINH_DE_HIEU.md` là file SINH RA — được regenerate bằng generator, không sửa tay (`ROADMAP_SYNC_STANDARD.md`) |
| `task_registry_snapshot.sh` | chạy, xem §18 `H-38` | công cụ under-count vì thiếu `IMPLEMENTED`/`VERIFYING` |

**Chống sinh sôi task, đo trên registry (`CAPABILITY_MODEL.md` §II.9):**

| Đại lượng | TRƯỚC (`04f77ac`) | SAU |
|---|---|---|
| SET B — task spec dưới `docs/tasks/` | 22 | **22** |
| SET A — dòng task trong bảng roadmap | **29** = 28 khớp regex (gồm `WP-B3` READY) + `T-03` VERIFYING | **29** = 27 khớp regex + `T-03` VERIFYING + `WP-B3` IMPLEMENTED |
| `new_registered_task_ids` | — | **0** |
| `proposals_created` | — | **0** |
| `owner_assignment_required_entries_added` | — | **1** (`H-38`, ghi vào HARDENING_BACKLOG, KHÔNG phải task) |

---

## 22. Lifecycle State

    WP-B3:  READY  ->  IN_PROGRESS  ->  IMPLEMENTED

Cả hai bước đều thuộc thẩm quyền Implementer theo
`governance/v4/CORE/STATE_AUTHORITY.md` § "The State Machine And Who May Write It".

**`WP-B3` KHÔNG được đánh `DONE` trong phiên này.** `DONE` do **chủ dự án** (hoặc completion
authority được chỉ định) ghi — cùng tiền lệ đã áp cho `WP-B1` (`DEC-034`) và `WP-C2`
(`DEC-036`).

    OWNER_DECISION_REQUIRED

**Không `E2_REQUIRED`.** Completion Gate đã đóng băng của `WP-B3` đặt `Evidence Level: E1` cho
cả tám REQUIRED check (`Risk = 2`); không check nào đòi rà soát độc lập. Vì vậy phiên này không
tự chứng nhận E2 cho bất cứ thứ gì — nó không cần, và không được phép nếu cần.

Nếu chủ dự án muốn thêm một lượt E2 độc lập (tuỳ chọn, không do gate đòi), vật liệu đã sẵn:
công cụ bất biến tái lập được, bốn fingerprint đóng băng, và 43 test.

---

## 23. Downstream State

**Không bắt đầu bất kỳ việc downstream nào. Chỉ báo cáo.**

    GATE-B = WP-B1 DONE  ∧  WP-B2 DONE  ∧  WP-B3 DONE

| Mục | Trạng thái sau phiên | Đổi bởi phiên này? |
|---|---|---|
| `WP-B1` | DONE | không |
| `WP-B2` | **READY** (chưa DONE) | không |
| `WP-B3` | **IMPLEMENTED** (chưa DONE) | có — `READY → IMPLEMENTED` |
| **`GATE-B`** | **VẪN CHƯA MỞ** — `WP-B2` mới READY, `WP-B3` mới IMPLEMENTED | không |
| `T-07` | **VẪN NOT READY** (chờ GATE-B) | không |
| `T-11` | BLOCKED | không |
| `T-06` | **DONE** | không |
| V2.1.5 validation | **FAILED** | không |
| verdict lịch sử | **`DO_NOT_BUILD`** | không |
| `can_proceed_to_app` | **false** | không |
| `DEC-005` | **PENDING** (vẫn chặn `T-08`) | không |
| `T-08` | vẫn bị chặn | không |
| `WP-C3` | READY (chưa mở) | không |
| tag official `v2.1.5-official-T06` | không đụng | không |

Ngay cả khi chủ dự án đóng `WP-B3 → DONE`, **`GATE-B` vẫn chưa mở** vì `WP-B2` mới chỉ `READY`.

---

## 24. Files Changed

**Created (5):**

    tests/test_wp_b3_audit_trail.py      607 dòng — 43 test cho 8 REQUIRED check + đối kháng A–L
    tests/wp_b3_scenarios.py             156 dòng — 6 kịch bản engine tất định
    tests/wp_b3_invariance_tool.py       183 dòng — công cụ đo bất biến trước–sau
    docs/reviews/WP-B3-IMPLEMENTATION-REPORT.md
    docs/sessions/S025-wp-b3-audit-trail.md

**Modified — production (1):**

    src/eth_dca_os/engine.py             +266 / −15

**Modified — governance / trạng thái (6):**

    docs/CONVENTIONS.md                  +82        (quy ước #23)
    docs/tasks/WP-B3-audit-trail-decision-log.md  +269 / −45  (evidence vào gate đã đóng băng)
    PROJECT/PROJECT_PROGRESS.md          +42 / −2
    PROJECT/HARDENING_BACKLOG.md         +108       (H-36, H-37, H-38)
    PROJECT/CAPABILITY_REGISTRY.md       +1 / −1
    PROJECT/REVIEW_BUDGET_LEDGER.md      +1 / −1
    PROJECT/LO_TRINH_DE_HIEU.md          +1 / −1    (SINH RA bằng sync_easy_roadmap.py)

**Modified — test thích ứng, không đổi ngữ nghĩa test (9):**

    tests/wp_c2_scenarios.py             +13 / −5   (`decision_log` rời fingerprint; bỏ cờ)
    tests/test_wp_c2_execution_state.py  +15 / −8   (chụp lại 4 fingerprint TRƯỚC bản sửa)
    tests/test_wp_a6_processing_order.py +6 / −6    (tên trường mới; bỏ cờ)
    tests/wp_a3_harness.py               +2 / −2    (bỏ cờ)
    tests/wp_a6_order_harness.py         +2 / −2    (bỏ cờ)
    tests/test_wp_d1_debt_cleanup.py     +2 / −1    (`ts` → `timestamp_utc`)
    tests/test_wp_a4_bad_data_semantics.py +1 / −1  (bỏ cờ)
    tests/wp_a3_impact_tool.py           +1 / −1    (bỏ cờ)
    tests/wp_a6_impact_tool.py           +1 / −1    (bỏ cờ)

**Deleted:** không.

**KHÔNG đụng tới:** `webapp/`, `docs/spec/`, `pyproject.toml`, `pyproject.lock`,
`src/eth_dca_os/` mọi module khác `engine.py`, `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`,
`docs/adr/ADR-001-*.md`, `docs/tasks/WP-C2-*.md`, `data/` (untracked).

Lệnh tái lập phép đo, đã commit:

    python tests/wp_b3_invariance_tool.py --raw <raw_dir> --out <payload.json>
    python tests/wp_b3_scenarios.py
    python -m pytest tests/test_wp_b3_audit_trail.py

---

## 25. Commit / Push

<!--COMMIT_PUSH-->

---

## 26. Exact Next Action

**Đúng MỘT việc, và nó thuộc chủ dự án.**

    OWNER_DECISION_REQUIRED — đóng vòng đời: WP-B3: IMPLEMENTED -> DONE

Vật liệu để quyết định đã đủ và nằm cả trong báo cáo này: 8/8 REQUIRED check PASS ở đúng mức
evidence mà gate đã đóng băng đòi (E1), đầu ra tài chính trùng khớp bit-for-bit, production
reachability đo bằng số trên đường chạy thật, 0 finding BLOCKING, 0 task ID mới, 0 repair cycle
tiêu.

Nếu chủ dự án đồng ý, hành động là ghi một Owner Decision mới trong
`PROJECT/PROJECT_DECISIONS.md` (cùng khuôn `DEC-034` cho `WP-B1` và `DEC-036` cho `WP-C2`) và
cập nhật `PROJECT/PROJECT_PROGRESS.md` + `PROJECT/CAPABILITY_REGISTRY.md`.

**Sau đó — và chỉ sau đó — `GATE-B` vẫn chưa mở.** Mắt xích còn lại là `WP-B2` (đang `READY`,
chưa mở). Phiên này cố ý KHÔNG bắt đầu `WP-B2`.

Ba việc **không** cần làm ngay, đã được định tuyến đúng chỗ và có điều kiện tái kích hoạt:
`H-36`, `H-37`, `H-38` trong `PROJECT/HARDENING_BACKLOG.md`.
