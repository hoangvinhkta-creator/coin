# WP-B2 Implementation Report

Gói: `WP-B2` — Bổ sung test cho các yêu cầu đặc tả còn thiếu (Backtest §21)
Phiên: `S026` · Ngày: 2026-09-05 · Vai trò: **implementer** (không phải rà soát độc lập)
Task file: `docs/tasks/WP-B2-bo-sung-test-requirement-con-thieu.md` (Completion Gate FROZEN 2026-08-23)

---

## 1. Executive Summary

`WP-B2` là mắt xích cuối còn thiếu của `GATE-B`. Gói này **chỉ viết test**: nó không đổi một
dòng mã sản phẩm nào, và mục tiêu không phải "tăng số test" mà là **không requirement nào của
Backtest §21 còn rơi vào im lặng**.

Kết quả:

- `WP-B2`: `READY → IN_PROGRESS → IMPLEMENTED`. **10/10 REQUIRED check PASS** (E1 toàn bộ).
- **141 ca test mới** trong 4 file test + 1 module quan sát (`tests/wp_b2_probe.py`).
- **0 dòng mã sản phẩm bị sửa** — `git diff b778dc1..HEAD -- src/eth_dca_os webapp
  pyproject.toml pyproject.lock` **rỗng**.
- **Bất biến tài chính/chiến lược tuyệt đối**: payload chuẩn tắc 3.728.853 byte,
  `sha256 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7` — TRÙNG ở lần chạy
  TRƯỚC và SAU trong chính phiên này, và trùng cả giá trị mà `WP-B3` đã ghi ở phiên trước.
- **Bảng đối chiếu 31/31** gạch đầu dòng §21 (`docs/CONVENTIONS.md`), được một bộ test giữ cho
  không trôi khỏi văn bản spec.
- Full suite: **678/678 PASS**, exit 0 (trước gói: 537/537).
- Phát sinh **`H-39`** và **`H-40`** (HARDENING, có `RE_TRIGGER_CONDITION`). **0 task ID mới.**
  **0 repair cycle tiêu.**

Điều gói này KHÔNG làm, và cố ý không làm: không sửa `src/` để test đi qua; không rerun hay
chạm bằng chứng official `T-06`; không đổi ngưỡng Gate / ngưỡng Failure Signal / bảng verdict;
không mở `GATE-B`; không mở `T-07`, `WP-C3`, `T-08`. Verdict lịch sử `DO_NOT_BUILD` và
`can_proceed_to_app = false` **không đổi**.

Việc còn lại đúng một, và thuộc chủ dự án:

    OWNER_DECISION_REQUIRED — đóng vòng đời: WP-B2: IMPLEMENTED -> DONE

## 2. Source / Branch / Commit

| Mục | Giá trị |
|---|---|
| HEAD nguồn | `b778dc1` — `Owner Decision DEC-037: WP-B3 Lifecycle Closure — IMPLEMENTED -> DONE` |
| `origin/main` tại lúc mở phiên | `b778dc161356ee9b422c15a238bc994a266556ae` (trùng HEAD) |
| Nhánh phiên | `claude/wp-b2-implementation-u9y68k` (mới, 0 commit trước phiên) |
| Tracked worktree lúc mở | CLEAN |
| Interpreter | Python 3.11.15 |
| Thư viện (khớp `pyproject.lock`) | numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1 |
| Tag official | `v2.1.5-official-T06` — **không chạm, không di chuyển** |

**Branch authority check** (`governance/scripts/governance/branch_authority_check.sh`), chạy
trước khi đọc bất kỳ file trạng thái nào:

    branch            = claude/wp-b2-implementation-u9y68k
    default branch    = main (resolved, not assumed)
    ahead of default  = 0 commit(s)
    divergence age    = 0 day(s)
    divergence LOC    = 0
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY

Kết quả lúc mở phiên là `FAIL` với lý do DUY NHẤT `attached branch has no upstream` — đúng
trạng thái của một nhánh mới chưa push. Mọi chỉ số khác (default branch phân giải động, 0 commit
ahead, worktree CLEAN) đều đúng. Kiểm tra được chạy lại **sau khi push** (§25).

**Xác minh trạng thái canonical trước khi thực thi.** Đối chiếu với kỳ vọng của đề bài, đọc từ
`PROJECT/PROJECT_PROGRESS.md` và `PROJECT/PROJECT_DECISIONS.md` tại `b778dc1`:

| Mục | Kỳ vọng | Thực tế | |
|---|---|---|---|
| `WP-B1` | DONE | DONE (`DEC-034`) | ✔ |
| `WP-B2` | READY | READY (`DEC-031`) | ✔ |
| `WP-B3` | DONE | DONE (`DEC-037`) | ✔ |
| `WP-C2` | DONE | DONE (`DEC-036`) | ✔ |
| `WP-C3` | READY | READY (`DEC-036`) | ✔ |
| `GATE-B` | CLOSED | CHƯA MỞ | ✔ |
| `T-07` | NOT READY | NOT READY | ✔ |
| `T-06` | DONE | DONE (`DEC-031`) | ✔ |
| V2.1.5 validation | FAILED | FAILED | ✔ |
| verdict | `DO_NOT_BUILD` | `DO_NOT_BUILD` | ✔ |
| `can_proceed_to_app` | false | false | ✔ |
| `DEC-005` | PENDING | PENDING | ✔ |
| `T-08` | bị `DEC-005` chặn | bị `DEC-005` chặn | ✔ |

Không có sai lệch vật chất → **không** `SOURCE_STATE_REVIEW_REQUIRED`.

## 3. Ready Gate

Ready Gate của `WP-B2` có 13 mục; 12 mục đã `[x]` từ `T-04`/`DEC-031`, mục thứ 13 ("Xác nhận lại
toàn bộ Ready Gate khi mở task") theo thiết kế do chính phiên mở `IN_PROGRESS` thực hiện. Rà lại
từng mục trên trạng thái repo THẬT tại `b778dc1`:

| Mục | Xác nhận tại `S026` |
|---|---|
| Objective rõ ràng | ✔ — "mỗi requirement §21 hoặc có test, hoặc được ghi rõ vì sao không thể có test" |
| Scope được định nghĩa | ✔ — `tests/`, `docs/CONVENTIONS.md` |
| Out-of-scope được định nghĩa | ✔ — đặc biệt: **không sửa `src/` để test đi qua** |
| Dependency `T-06 DONE` | ✔ — `DEC-031`, verdict `DO_NOT_BUILD`; `T-04` cũng DONE |
| Expected touch area | ✔ — `src/eth_dca_os/`, `webapp/`, `docs/spec/` là vùng cấm |
| Requirement liên quan được hiểu | ✔ — BT §21.2/§21.3/§21.4 đọc nguyên văn; 31 gạch đầu dòng được liệt kê máy móc |
| Data impact | ✔ — không có (gói không sinh/không sửa dữ liệu; test dùng dataset tổng hợp trong `tmp_path`) |
| Security impact | ✔ — không có |
| Difficulty / Risk / Blast Radius | ✔ — 3/4, 2/4, 1/4 (không đổi) |
| Escalation triggers | ✔ — ba trigger đã khai; trigger "test mới phát hiện hành vi sai" KHÔNG kích hoạt (không test mới nào FAIL) |
| Completion Gate finalize | ✔ — 10 REQUIRED check |
| Completion Gate đóng băng trước thực thi | ✔ — FROZEN 2026-08-23 (T-04/S002), **không sửa một chữ nào ở phần "Yêu cầu:"** |
| **Xác nhận lại toàn bộ Ready Gate khi mở task** | ✔ — chính bảng này |

**Không** `READY_GATE_FAIL`. Chuyển `READY → IN_PROGRESS` theo `STATE_AUTHORITY.md` (implementer
được phép ghi `IN_PROGRESS`).

## 4. Canonical WP-B2 Scope

Nguồn thẩm quyền là file task đóng băng, không phải prompt phiên. Trích những ràng buộc quyết
định cách làm:

- **Scope**: `tests/` (bổ sung test) và `docs/CONVENTIONS.md` (ghi lý do NOT_APPLICABLE).
- **Out of Scope**: sửa mã sản phẩm để test đi qua (*"Nếu một test mới thất bại, đó là finding,
  không phải lý do sửa `src/`"*); test thứ tự 18 bước (thuộc `WP-A6`); test partial fill ở tầng
  engine (không thể có — `F-020`); chính sách verdict (`WP-B1`).
- **Expected Touch Area — vùng cấm**: toàn bộ `src/eth_dca_os/`, `webapp/`, `docs/spec/`.
- **14 subtask** B2.1–B2.14 và **10 REQUIRED check** `CHECK-B2-01`…`CHECK-B2-10`.
- **Ghi chú của chính file task** — rủi ro đặc trưng của gói: *"viết test mô tả hành vi hiện tại
  thay vì kiểm chứng yêu cầu spec. Test kiểu đó luôn PASS và không bảo vệ gì cả. Mỗi test ở đây
  phải bắt đầu từ một câu trong §21, không phải từ một hàm trong `engine.py`."*

Ghi chú về vùng chạm ngoài "Allowed": phiên có sửa `PROJECT/*` (roadmap, capability registry,
budget ledger, hardening backlog), `docs/tasks/` (chính file task), `docs/reviews/` và
`docs/sessions/`. Đó **không** phải Scope Expansion: chính Exit Criteria của gói yêu cầu
("`PROJECT/PROJECT_PROGRESS.md` được cập nhật", "Session handoff được viết"), và ghi finding vào
Hardening Backlog là thủ tục bắt buộc của `REVIEW_PROTOCOL.md`. Vùng **sản phẩm** thì tuyệt đối
không chạm — xem §20.

## 5. Pre-Implementation Behavior Map

Bản đồ hiện trạng dựng TRƯỚC khi viết dòng test đầu tiên. Câu hỏi chi phối: cái gì đã có, cái gì
thật sự thiếu?

**Producer (đường sinh hành vi cần kiểm)**

| Thành phần | Vai trò với §21 |
|---|---|
| `src/eth_dca_os/engine.py::run_engine` | vòng lặp 15m theo 18 bước §19; nơi phát sinh mọi hành vi §21.2/§21.3 |
| `engine.zone_order_key` | khoá tie-break §15.1 [F2] (pool → is_crash → created_at → zone_index) |
| `engine.create_action` | TRIGGERED → ACTION_PENDING; nhánh `p2p_unavailable_in_crash`; nhánh behavioral |
| `engine.derive_execution_state` | gọi ĐÚNG MỘT LẦN mỗi nến ở bước 12b — điểm móc quan sát của gói này |
| `src/eth_dca_os/execution.py` | `behavioral_delay_seconds` (bảng BT §6), `apply_fill`, `MISSED` |
| `src/eth_dca_os/capital.py` | `Pool` (ledger A/R/D), `BASE_SCHEDULE`, `smart_reservable`, `opportunity_reservable` |
| `src/eth_dca_os/ladders.py` | `create_*_ladder`, `Zone`/`Ladder`, `OPEN_ZONE_STATUSES` |
| `src/eth_dca_os/benchmarks.py::run_benchmark_C` | ngữ nghĩa chu kỳ [F4] |
| `src/eth_dca_os/regime.py` | `state` (nền) vs `label` (nhãn §16, gồm STRESSED) |

**Consumer / persistence hiện có**

`RunResult` mang `purchases`, `contributions`, `counters`, `monthly_deployments`,
`cash_samples`, `opp_cap_samples`, `regime_timeline` (WP-A5), `execution_state_timeline` +
`market_snapshots` (WP-C2), `decision_log` (WP-B3). **`RunResult` KHÔNG trả ra `Pool`, `Ladder`,
`Zone` hay trạng thái theo từng nến** — đó chính là lý do phần lớn câu §21.2/§21.3 chưa có test:
không có bề mặt để khẳng định.

**Test đã có (không viết lại)**

`test_score.py` (§21.1), `test_capital.py`, `test_ladders.py`, `test_regime.py`,
`test_manifests.py`, `test_windows.py`, `test_benchmarks.py`, `test_gates_verdict.py`,
`test_wp_a3_lifecycle.py` (F5 snapshot vs daily limit, tie-break ở tầng hàm, STRESSED chiều ÉP
BẬT), `test_wp_a4_bad_data_semantics.py` (nhãn gap / delayed fill), `test_wp_a6_processing_order.py`
(thứ tự 18 bước, `LADDER_EXPIRED`), `test_wp_d1_debt_cleanup.py` (override đếm theo sự kiện),
`test_wp_b1_*`, `test_wp_b3_audit_trail.py`, `test_wp_c2_execution_state.py`.

**Hành vi CÒN THIẾU đúng nghĩa** (đối chiếu `docs/reviews/S001-audit-findings.md` § "Requirement
của spec CHƯA CÓ TEST"): xem §17 — mỗi mục ánh xạ 1–1 vào một `CHECK-B2-*`.

**File dự kiến đổi** (dự kiến TRƯỚC khi làm, đối chiếu thực tế ở §7): 4 file test mới + 1 module
harness mới trong `tests/`; `docs/CONVENTIONS.md`. Không file nào trong `src/`.

**Điều KHÔNG được suy luận sai**: "WP-B2 READY" không phải bằng chứng rằng mã sản phẩm thiếu.
Rà soát cho thấy **mã sản phẩm đã đúng ở mọi điểm gói này kiểm** — cái thiếu là **bằng chứng**,
không phải hành vi. Không một test mới nào FAIL.

## 6. Dependency / Contract Map

| Hợp đồng | WP-B2 tiêu thụ thế nào | Rủi ro phá vỡ |
|---|---|---|
| `WP-B1` — chính sách verdict, officiality, quy tắc finite, hạ verdict khi non-official | KHÔNG chạm. Gói không gọi `verdict.py`/`failure_signals.py`, không tạo run record | Không |
| `WP-B3` — audit trail `decision_log` (DM §11) | **Đọc**, không ghi: dùng `reason_code` (`MAX_ZONES_BLOCK`, `COOLDOWN_OVERRIDE`, `ACTION_MISSED`, …) làm bề mặt quan sát | Không — chỉ đọc |
| `WP-C2` — vốn từ vựng `ExecutionState`, `derive_execution_state`, `execution_state_timeline` | **Bọc** `derive_execution_state` để chụp khung ảnh mỗi nến; bản bọc trả về ĐÚNG giá trị hàm thật. So sánh `execution_state_timeline` giữa hai run trong test STRESSED | Không — `test_b2_02c` chứng minh instrumentation không đổi hành vi |
| `WP-A3` — tách `state`/`label`, vòng đời Crash ladder, snapshot [F5] | Bổ sung kịch bản mà WP-A3 KHÔNG có (Opportunity ladder đang giữ reservation lúc crash entry); không sửa/không phủ định test nào của WP-A3 | Không |
| `WP-A4` — nhãn `EXECUTION_DATA_GAP` / `DELAYED_DATA_FILL` | Không viết lại; chỉ bổ sung câu ĐẦU của BT §18 ("không interpolate") mà WP-A4 chưa phủ | Không |
| `WP-A6` — thứ tự 18 bước | Ngoài scope (task file nói rõ). Điểm đo bước 12b của gói này bám đúng thứ tự WP-A6 đã chốt | Không |

**Không có `CONTRACT_CONFLICT`.** Không hợp đồng nào của gói đã `DONE` bị viết lại.

## 7. Change Budget

**Trước (dự kiến)**

| Mục | Dự kiến |
|---|---|
| File production dự kiến đổi | **0** (task file cấm) |
| LOC production dự kiến | **0** |
| Capability owner | `CAP-VERDICT`, lineage root `WP-B1` |
| Budget khả dụng | `CAP-VERDICT`: **used = 0** (giá trị ĐÃ GHI trong `PROJECT/REVIEW_BUDGET_LEDGER.md` §2). `ALLOWED` chưa được chủ dự án đặt tường minh cho lineage này; mặc định V4.3 cho Effective Risk MEDIUM là **2** (`GOVERNANCE_V4.md` §II.2) — nêu ở đây như một mặc định, không phải một con số Owner đã ghi |
| File test dự kiến | 4–6 file mới trong `tests/` |

**Sau (thực tế, đo bằng lệnh — không cộng tay)**

    git diff --shortstat b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    -> (rỗng)

| Mục | Thực tế |
|---|---|
| File production đổi | **0** · +0 / −0 |
| File test mới | 5 (4 file test + 1 module quan sát) — 1.527 dòng |
| Docs / state đổi | `docs/CONVENTIONS.md` (+57), `PROJECT/HARDENING_BACKLOG.md` (+83), `PROJECT/PROJECT_PROGRESS.md`, `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/REVIEW_BUDGET_LEDGER.md`, `PROJECT/LO_TRINH_DE_HIEU.md` (sinh tự động), file task |
| Repair cycle tiêu | **0** |

Vì sao **0 repair cycle**: `DELIVERY_LOOP.md` đo Delivery Change Budget trên **production path**
(`PROJECT/PRODUCTION_PATHS.md`), và diff production của gói này bằng 0. Tiền lệ đã ghi trong
ledger §1 ("Decision pack PRE-S008", `2f20e6c..bd7c5ff`) và được `DEC-012` khẳng định: hạng mục
có diff production path = 0 **không tiêu repair cycle**. Ngoài ra `WP-B2` chưa từng `DONE` nên
chưa có chu kỳ nào để mở.

Absorption Limit (`CAPABILITY_MODEL.md`): A — Effective Risk không tăng (Risk 2/4, Blast Radius
1/4 giữ nguyên; đầu ra tài chính bất biến bit-for-bit); B — 0 hạng mục được hấp thụ thêm vào
baseline; C — số REQUIRED check giữ nguyên **10** (không thêm, không bớt); D — không kéo việc
ngoài vertical slice lên đường găng (`H-39`/`H-40` ở HARDENING). **Không**
`ABSORPTION_LIMIT_REACHED`, **không** `CHANGE_BUDGET_EXCEEDED`, **không** `SCOPE_CHANGED`.

## 8. Implementation

Năm file, tất cả trong `tests/`.

**`tests/wp_b2_probe.py` (299 dòng) — dụng cụ QUAN SÁT.**
Phần lớn câu §21.2/§21.3 nói về những thứ `RunResult` không trả ra. Module này lấp đúng khoảng
đó mà **không mô phỏng**:

- `Pool` và `create_*_ladder` được patch trong namespace `eth_dca_os.engine` để giữ tham chiếu
  tới đúng đối tượng engine thật đang dùng (cùng khuôn `wp_a3_harness.instrument`).
- `derive_execution_state` — hàm engine gọi **đúng một lần mỗi nến** ở bước 12b §19 — được bọc
  lại để chụp một `Frame` mỗi nến: số dư ba pool, trạng thái + `reserved_vnd` + `target_price`
  của mọi zone, `eligible_capital_vnd` của mọi ladder, bốn dữ kiện đầu vào và trạng thái đầu ra.
  Bản bọc trả về ĐÚNG giá trị hàm thật.
- Lưới thời gian của khung ảnh được dựng **độc lập từ dataset**, không hỏi engine; số khung ảnh
  phải bằng số nến, nếu không test ĐỎ ngay tại đó.
- `Probe.pierced_zones(ts)` tính tập zone "bị xuyên" từ OHLC của nến và luật BT §5 — **độc lập
  với engine**, để phép đối chiếu không biến thành phép chép lại câu trả lời của engine.
- Dataset builder dùng lại `wp_a3_harness.build_dataset`; bộ khoét lỗ hổng dùng lại
  `wp_b3_scenarios._drop_candles`. **Không dựng builder thứ hai** (trùng nguồn sự thật là khiếm
  khuyết, không phải dự phòng).
- `FixedRng` — RNG tất định thay `numpy.random.Generator`, đi vào engine qua tham số **công
  khai** `run_engine(..., behavioral_rng=...)`, không phải cửa hậu dựng riêng cho test.

**`tests/test_wp_b2_spec21_2_capital_ladder.py` (312 dòng, 9 ca)** — §21.2: Base execute sớm,
Month-End Day 25–27/Day 28, snapshot Crash [F5], không double reservation.

**`tests/test_wp_b2_spec21_3_execution.py` (538 dòng, 31 ca)** — §21.3: đa zone + `max_zones` +
tie-break, LOW/CLOSE, proxy đêm/TTL/MISSED, cooldown + override, Crash funding unavailable,
STRESSED [F1].

**`tests/test_wp_b2_spec21_4_accounting.py` (220 dòng, 5 ca)** — §21.4: không interpolate qua lỗ
hổng, delayed Base fill rơi vào nến có thật, Benchmark C [F4].

**`tests/test_wp_b2_spec21_coverage_matrix.py` (158 dòng, 96 ca)** — biến bảng đối chiếu §21
thành hợp đồng kiểm được (xem `CHECK-B2-08`).

**`docs/CONVENTIONS.md`** — thêm mục "Đối chiếu requirement Backtest §21 → test (WP-B2)": 31
hàng, mỗi hàng là một gạch đầu dòng §21 nguyên văn + trạng thái + test/lý do.

## 9. Core Semantics

Bốn nguyên tắc quyết định chất lượng của gói này; mỗi nguyên tắc là một cách chống lại một kiểu
test vô nghĩa cụ thể.

1. **Bắt đầu từ câu spec, không từ hàm.** Mỗi test mở đầu bằng câu §21/§5/§6/§18 mà nó phục vụ.
   Chống: test mô tả hành vi hiện tại rồi luôn PASS.
2. **Tính kỳ vọng độc lập với engine.** Tập zone "bị xuyên" tính từ OHLC + luật §5; snapshot [F5]
   phản chứng tính lại bằng công thức §14 trên trạng thái pool của nến trước. Chống: hỏi engine
   rồi khẳng định lại câu trả lời của nó.
3. **Mệnh đề phải phân biệt được hai khả năng.** Test `max_zones áp SAU khi sắp thứ tự` tự khẳng
   định trước rằng thứ tự duyệt thô KHÁC thứ tự §15.1; nếu không, nó ĐỎ và tuyên bố mình vô
   nghĩa. Chống: kịch bản degenerate (bài học `F-E2-01`).
4. **Mọi test có tiền đề chống rỗng.** Có đúng N zone bị xuyên; có fill của cả bốn nguồn; có
   ≥1 override; nhãn STRESSED thật sự xuất hiện ở run A và biến mất ở run B; đối chứng âm cho mọi
   nhãn dữ liệu. Chống: `0 bản ghi` được đọc thành PASS (`STATE_AUTHORITY.md` § Vacuous Validation).

## 10. Compatibility With WP-B1

Không chạm. Gói không import `verdict.py` hay `failure_signals.py`, không tạo run record, không
gọi `run_verdict`/`decide_verdict`, không đọc/ghi cờ `official`.

Ngữ nghĩa được bảo toàn (kiểm gián tiếp qua full suite: 12 ca `test_wp_b1_verdict_policy.py`,
21 + 49 ca hai file repair E2, 33 ca `test_wp_b1_slice_failure_signal_cap.py` — tất cả PASS):
đúng đắn verdict, xử lý officiality, quy tắc finite, hạ verdict khi non-official, ngữ nghĩa
Control F/G sau `F-017`.

**Không đường nào trong gói này có thể lật `DO_NOT_BUILD` hay `can_proceed_to_app`**: gói không
sinh verdict, và bất biến tài chính bit-for-bit (§14) chứng minh đầu vào của verdict không đổi.

## 11. Compatibility With WP-B3

`decision_log` được **đọc** làm bề mặt quan sát (`MAX_ZONES_BLOCK`, `DAILY_LIMIT_BLOCK`,
`COOLDOWN_OVERRIDE`, `ACTION_MISSED`, `ACTION_TTL_EXPIRED`). Không bản ghi nào được tạo bằng tay,
không trường nào bị sửa, không audit trail thứ hai được dựng.

Bằng chứng bất biến: khối `wp_b3_observability` của payload (3.191.972 byte,
`sha256 c2d8f4d583bb3f7e330623c6735623a4562fdc75e6690b4631e3583b85b6bbd9`) **trùng bit-for-bit**
trước–sau; 25 loại `reason_code` trên mỗi run toàn kỳ, 2.441 / 2.478 bản ghi — không đổi.

## 12. Compatibility With WP-C2

Gói **tiêu thụ** hợp đồng WP-C2 theo hai đường, không mở rộng nó:

- Bọc `derive_execution_state` để quan sát. Không đổi tham số, không đổi giá trị trả về, không
  thêm giá trị `ExecutionState` nào. Điểm đo (bước 12b) và thứ tự ưu tiên giữ nguyên.
- So sánh `execution_state_timeline` và `market_snapshots` giữa hai run trong test STRESSED —
  tức dùng chiều WP-C2 làm **bề mặt kiểm chứng bổ sung**, chứng minh nhãn regime không rò rỉ sang
  chiều Execution State (ST §16 đòi hai chiều "lưu riêng").

`test_b2_02c_probe_does_not_change_engine_behaviour` là tiền đề của mọi khẳng định dùng probe:
cùng kịch bản chạy CÓ và KHÔNG instrumentation cho đầu ra tài chính trùng khớp bit-for-bit.
33 ca `test_wp_c2_execution_state.py` (gồm bốn fingerprint đóng băng) vẫn PASS.

## 13. Adversarial Tests

Danh sách đối kháng được dựng từ chính ngữ nghĩa WP-B2 và gate đóng băng, không từ mã.

| # | Ca đối kháng | Test |
|---|---|---|
| A | Đường hợp lệ thường: lịch Base 3/13/23 chạy đủ | `test_b2_01d`, `test_b2_01a` (đối chứng) |
| B | Biên: `max_zones` chạm đúng trần (2 zone bị xuyên → 2 action, 0 chặn) | `test_b2_03a[hai zone]` |
| C | Biên: vượt trần (3 và 4 zone) | `test_b2_03a[ba zone]`, `[bốn zone]` |
| D | Biên: zone Opportunity nằm GIỮA `LOW` và `CLOSE` | `test_b2_04a` |
| E | Biên: `seconds_to_7am == ttl` (đúng dấu `<=`) | `test_b2_04f` |
| F | Biên: mọi mốc xác suất của bảng BT §6 (0,49/0,50/0,79/0,80/0,94/0,95; 0,09/0,10/0,34/0,35/0,79/0,80) | `test_b2_04e` (17 ca) |
| G | Biên: override đúng ngưỡng 7% (giảm 3,5% KHÔNG override) | `test_b2_05a`, `test_b2_05b` |
| H | Đầu vào thiếu: khoét trọn ngày có cú dip → zone không được trigger | `test_b2_07a` |
| I | Đầu vào thiếu: khoét nến 12:00 → Base fill trễ, rơi vào nến CÓ THẬT | `test_b2_07b` |
| J | Trạng thái cũ/không xác định: zone bị chặn GIỮ `TRIGGERED` và được xét lại cycle sau | `test_b2_03a` |
| K | Round-trip lưu trữ: replay ledger từng pool, TOTAL = A+R+D, không âm | `test_b2_02a`, `test_b2_02b` |
| L | Không PASS rỗng: mọi test có tiền đề khẳng định sự kiện cần kiểm THỰC SỰ xảy ra | toàn bộ |
| M | Không nguồn sự thật thứ hai: dùng lại `build_dataset` / `_drop_candles`; tập zone bị xuyên tính độc lập | `wp_b2_probe.py` |
| N | Không hồi quy WP-B1/WP-B3/WP-C2 | §10–§12 + full suite |
| O | Không đường nào lật `DO_NOT_BUILD` / `can_proceed_to_app` | §14 (bất biến bit-for-bit) |
| P | Phản chứng ngược chiều cho STRESSED (loại bỏ nhãn thay vì ép bật) | `test_b2_06` |
| Q | Đối chứng âm cho mọi nhãn dữ liệu (dataset sạch không sinh nhãn nào) | `test_b2_07b` |
| R | Bảng đối chiếu không được trỏ vào hư không / không được trôi khỏi spec | `test_b2_08a`…`test_b2_08f` |

## 14. Financial / Strategy Invariance

Gói này là **thuần test**, nên bất biến tài chính về nguyên tắc là hệ quả cấu trúc (diff
production = 0). Vẫn đo, vì "về nguyên tắc" không phải bằng chứng.

Công cụ: `tests/wp_b3_invariance_tool.py` (đã commit từ `WP-B3`), chạy **cùng dataset synthetic
seed cố định, cùng config, cùng seed, cùng đường production** ở hai phía:

    PYTHONPATH=tests python tests/wp_b3_invariance_tool.py --raw <raw> --out <payload.json>

Phạm vi payload: Gate 1 chín window + OOS, Gate 2, Gate 3, Control F/G, verdict, và **hai lần
chạy `run_engine` toàn kỳ** (2019-01-01 → OOS end) ở cả hai execution config đã commit, kèm từng
purchase / từng sample ledger / `execution_state_timeline` / `market_snapshots`.

    TRƯỚC (HEAD b778dc1):   invariance_sha256 = 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7
                            invariance_bytes  = 3.728.853
    SAU  (HEAD phiên này):  invariance_sha256 = 3ea7c8d7d6d439fdc54470b1677ef5f783cb1c383f33cdc0c5dc1f32aae59dd7
                            invariance_bytes  = 3.728.853

Khối `wp_b3_observability` (audit trail) cũng trùng: `sha256 c2d8f4d5…`, 3.191.972 byte. Chỉ khối
`timing` khác — đó là đồng hồ tường, không mang ngữ nghĩa; **không** normalize gì khác.

Đáng ghi thêm: giá trị `3ea7c8d7…` **trùng đúng con số `WP-B3` ghi ở phiên trước** — tức bất biến
này tái lập được qua phiên, qua máy, qua nhánh, không chỉ trong một lần chạy.

**Không** `BEHAVIOR_CHANGED`.

## 15. Production Reachability

`CAPABILITY_MODEL.md` đòi bằng chứng reachability đến từ đường chạy NGOÀI ranh giới module.
Với một gói test, câu hỏi đúng là: **test chạy trên mã production thật hay trên bản mô phỏng?**

| Bề mặt | Đường production được dùng | Anti-vacuity |
|---|---|---|
| §21.2 Base / Month-End | `run_engine` trọn accounting month (2.400–2.880 nến/kịch bản) | 4 bản ghi Base ở đúng bốn mốc; tổng = 50,0 |
| §21.2 snapshot [F5] | `run_engine`, crash entry thật sinh từ `RegimeTracker` | release 3,8 ≠ 0; snapshot 5,8 ≠ phản chứng 2,0 |
| §21.2 double reservation | `run_engine`, bất biến đo ở **1.344 và 3.936 nến** | 3 ladder / 11–12 zone, ≥5 fill; 0 nến lệch |
| §21.3 đa zone / max_zones | `run_engine` hai tháng (3.936 nến) | 1/2/3/4 zone bị xuyên, đo độc lập với engine |
| §21.3 proxy / TTL / MISSED | `run_engine` (672 nến) với `behavioral_model=LOCAL_HOUR` qua tham số công khai `behavioral_rng` | fill tại đúng 07:00; 2 action MISSED tại đúng mốc `close(trigger) + TTL` |
| §21.3 cooldown / override | `run_engine` trong CRASH | 2 fill Crash, 1 sự kiện override, 2 bản ghi `COOLDOWN_OVERRIDE` |
| §21.3 funding unavailable | `run_engine` với `p2p_unavailable_in_crash=True` | 0 fill Crash (stress) vs ≥1 fill (đối chứng) |
| §21.3 STRESSED | hai lần `run_engine` toàn kịch bản | fill của cả BASE/SMART/OPPORTUNITY/CRASH; STRESSED có ở A, không có ở B |
| §21.4 data gap | hai dataset thật, 672 vs 576 nến | −96 nến; zone `EXECUTED` vs `ACTIVE` |
| §21.4 Benchmark C | `run_benchmark_C` + `run_benchmark_A` thật | 4 lần bắn vs 2 lần bắn (đối chứng không reset) |
| §21.1 / §21.4 còn lại | test đã có từ gói trước, chạy trong cùng suite | 678 ca PASS |

**Không ca nào PASS bằng tập rỗng.** Mọi test có ít nhất một khẳng định tiền đề rằng sự kiện cần
kiểm thực sự xảy ra.

Giới hạn được ghi tường minh thay vì im lặng: hai cờ `behavioral_model=LOCAL_HOUR` và
`p2p_unavailable_in_crash=True` là cấu hình HỢP LỆ của `ExecutionConfig` (DM §3) và hành vi engine
đúng khi bật; nhưng **không cấu hình nào trong `manifests.GATE3_GRID` bật chúng**, nên hai kịch
bản robustness Impl Plan §8 đòi chưa từng chạy trong pipeline — `H-39` (§18, §19).

## 16. Full Regression

    $ python -m pytest -p no:cacheprovider     (không deselect, không -k, không thêm skip/xfail)
    ...
    678 passed in 1153.20s (0:19:13)

| Chỉ số | Trước gói (`b778dc1`) | Sau gói |
|---|---|---|
| collected | 537 | **678** |
| passed | 537 | **678** |
| failed | 0 | **0** |
| errors | 0 | **0** |
| skipped | 0 | **0** |
| xfail / xpass | 0 / 0 | **0 / 0** |
| exit code | 0 | **0** |

Chênh lệch **+141** đúng bằng số ca WP-B2 thêm vào: 9 (§21.2) + 31 (§21.3) + 5 (§21.4) + 96
(bảng đối chiếu). Không test hiện có nào bị xoá, đổi tên, nới lỏng hay bỏ chọn —
`git diff --stat b778dc1..HEAD -- tests/` chỉ có **file mới**.

Con số 537 của mốc TRƯỚC được đo trong CHÍNH phiên này trên đúng `b778dc1`, cùng interpreter và
cùng bộ thư viện ghim ở `pyproject.lock` — không chép lại từ báo cáo của phiên trước.

## 17. Completion Gate Matrix

Dùng ĐÚNG mười REQUIRED check đã đóng băng; không diễn giải lại thành gate mới. Evidence đầy đủ
nằm trong chính file task (`docs/tasks/WP-B2-bo-sung-test-requirement-con-thieu.md`).

| Check | Requirement (rút gọn) | Evidence level | Bằng chứng | Kết quả | Test / artifact |
|---|---|---|---|---|---|
| **CHECK-B2-01** | §21.2: Base execute sớm không lặp lại ngày gốc; Month-End Day 25–27 và Day 28; snapshot [F5] đo sau cancel/release | E1 (không hạ) | 6 test trên `run_engine` thật; ngày gốc 0 bản ghi vs đối chứng 20,0; Day 25 = 10,0 và Day 28 = 10,0; snapshot 5,8 vs phản chứng 2,0 (chênh = 3,8 vừa release); snapshot bất biến trên 1.344 nến | **PASS** | `test_b2_01a`…`test_b2_01f` |
| **CHECK-B2-02** | Không double reservation Smart/Opportunity/Crash ở TẦNG ENGINE, phủ ca Opportunity → Crash | E1 | bất biến `tổng RESERVED pool == tổng reserved_vnd zone đang mở` đo ở **mọi nến**: 0/1.344 và 0/3.936 lệch; ca chuyển có thật (ladder Opportunity `CANCELLED`, Crash được cấp 5,8 ≤ available 19,8) | **PASS** | `test_b2_02a`, `test_b2_02b`, `test_b2_02c` |
| **CHECK-B2-03** | §21.3: một/hai/ba zone cùng nến; trần hai zone mỗi cycle; tie-break §15.1, `max_zones` áp SAU khi sắp thứ tự | E1 | 4 ca tham số hoá (1/2/3/4 zone), tập zone bị xuyên tính độc lập với engine; kịch bản hai tháng dựng đúng tình huống hai thứ tự KHÁC nhau và engine chọn theo §15.1 | **PASS** | `test_b2_03a`, `test_b2_03b`, `test_b2_03c` |
| **CHECK-B2-04** | §21.3: Opportunity confirm bằng CLOSE + thực thi nến sau; Smart bằng LOW; proxy 07:00; TTL; MISSED | E1 | zone Opportunity giữa LOW và CLOSE KHÔNG confirm; fill Opportunity luôn ở nến sau; fill proxy tại đúng `2023-03-05 07:00`; MISSED tại đúng `trigger + TTL`; 17 ca bảng phân phối BT §6 | **PASS** | `test_b2_04a`…`test_b2_04f` |
| **CHECK-B2-05** | §21.3: cooldown, override, tần suất override trong CRASH, Crash funding unavailable | E1 | trong CRASH: zone giữ `TRIGGERED` rồi override mở khoá, `cooldown_override["CRASH"] == 1` (đếm theo sự kiện); đối chứng 3,5% → 0 override; cờ P2P bật → 0 fill Crash, tắt → có fill | **PASS** | `test_b2_05a`, `test_b2_05b`, `test_b2_05c` |
| **CHECK-B2-06** | [F1] STRESSED không có hiệu ứng execution — test thường trực, độc lập với WP-A3 | E1 | phản chứng NGƯỢC CHIỀU WP-A3 (loại bỏ nhãn phát sinh tự nhiên thay vì ép bật); so purchase/ladder/ledger/counter + `execution_state_timeline` + `market_snapshots`; tiền đề: fill của cả bốn nguồn, ≥1 override | **PASS** | `test_b2_06` |
| **CHECK-B2-07** | §21.4: data gap và delayed Base fill; Benchmark C [F4] | E1 | khoét trọn ngày dip (−96 nến) → zone còn `ACTIVE` (không interpolate); Base fill trễ rơi vào nến CÓ THẬT, giá = OPEN thật, cùng số tiền; Benchmark C: 4 lần bắn có reset vs 2 lần bắn không reset | **PASS** | `test_b2_07a`…`test_b2_07e` |
| **CHECK-B2-08** | Mọi requirement §21 không test được ghi NOT_APPLICABLE kèm lý do; bảng đối chiếu đầy đủ | E1 | 31/31 hàng khớp NGUYÊN VĂN §21; 29 TESTED / 1 MIXED / 1 NOT_APPLICABLE; 96 ca kiểm bảng không trôi khỏi spec, mọi tên test viện dẫn có thật (AST), và mọi test WP-B2 gắn với một requirement | **PASS** | `docs/CONVENTIONS.md` + `test_b2_08a`…`test_b2_08f` |
| **CHECK-B2-09** | `git diff` chứng minh không sửa `src/eth_dca_os/`; test mới FAIL phải thành finding | E1 | `git diff b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock` **rỗng**; 0 test mới FAIL; hai quan sát phát sinh đã ghi + phân lớp (`H-39`, `H-40`) | **PASS** | §20, `PROJECT/HARDENING_BACKLOG.md` |
| **CHECK-B2-10** | Toàn bộ suite PASS; không test nào bị skip/xoá/nới lỏng | E1 | 678/678 PASS, exit 0, 0 skip/xfail; +141 đúng bằng số ca thêm vào; diff `tests/` chỉ có file mới | **PASS** | §16 |

    REQUIRED: 10/10 PASS
    Evidence level: E1 toàn bộ — không check nào bị hạ mức, không check nào bị đánh NOT_APPLICABLE
    E2 required: KHÔNG (Risk = 2 → gate của gói không đòi E2 ở check nào)

## 18. Findings

Không test mới nào FAIL, nên Escalation Trigger "test mới phát hiện hành vi sai" **không kích
hoạt**. Hai quan sát vẫn được ghi và phân lớp thay vì bỏ qua.

**F-B2-01 → `H-39` — hai kịch bản robustness Gate 3 bắt buộc chưa có đường chạy trong pipeline.**

- *Hiện tượng:* BT §5 khai stress `P2P-unavailable-in-crash`; BT §6 khai behavioral simulation là
  robustness Gate 3; Impl Plan §8 nói thẳng *"Chạy behavioral robustness và stress P2P-unavailable"*.
  Cả hai cờ tồn tại và hoạt động đúng trong engine (WP-B2 chứng minh bằng test), nhưng
  `manifests.GATE3_GRID` không biến thiên chúng nên **cả 114 config Gate 3 đều `OFF/False`**, và
  `pipeline.run_gate3` chỉ chạy config của manifest đó.
- *Phân lớp:* **CONFIRMED**, ánh xạ risk đã đăng ký **`RSK-007`**. Có đường production, có bằng
  chứng tái lập. Định tuyến `OUT_OF_SCOPE` → `CAP-PIPELINE` (`WP-A2` đã DONE →
  `OWNER_ASSIGNMENT_REQUIRED`), giữ ở **HARDENING**.
- *Vì sao KHÔNG sửa ở đây:* (a) ngoài Expected Touch Area của `WP-B2` — task file cấm chạm `src/`;
  (b) `T-06` đã official với verdict `DO_NOT_BUILD`, nên bổ sung hai lượt chạy Gate 3 rồi báo cáo
  lại chính là "chạy lại để làm đẹp kết quả official" mà **BT §22** và **Master Index §6** cấm —
  hướng đúng là đưa vào **V2.2** (`WP-D2`); (c) không thể đổi verdict theo chiều có lợi.
- *Không nâng đường găng:* `H-39` KHÔNG là điều kiện của `GATE-B` và không chặn `WP-B2`.

**F-B2-02 → `H-40` — nhánh "proxy 07:00 vượt TTL → MISSED" không tới lượt chạy ở TTL baseline.**

- *Hiện tượng:* giờ đêm (23:00–06:59) cho `seconds_to_7am` tối đa 8h < TTL baseline 12h, và
  `GATE3_GRID` không biến thiên `action_ttl_seconds`. Cùng họ `H-36`.
- *Phân lớp:* **CONFIRMED HARDENING**, không hậu quả nghiệp vụ ở cấu hình hiện tại (nhánh không
  chạy nên không thể sai). Nhánh được kiểm ở tầng hàm và giới hạn được ghi rõ.

**Quan sát không thành finding:** ba mục §21 chỉ có test ở tầng dataclass/hàm chứ chưa có test
riêng ở tầng engine (mốc `expires_at` của Smart/Opportunity ladder) đã được phủ ở tầng engine bởi
`tests/wp_a6_order_harness.py` (sự kiện `LADDER_EXPIRED` bước 3 và bước 18) — ghi rõ trong bảng
đối chiếu, không cần mục hardening.

## 19. Hardening

| ID | Nội dung | Capability / owner | Phân lớp | RE_TRIGGER_CONDITION (tóm tắt) |
|---|---|---|---|---|
| `H-39` | Behavioral robustness + stress P2P-unavailable chưa đấu nối pipeline | `CAP-PIPELINE` / `WP-A2` (DONE) → `OWNER_ASSIGNMENT_REQUIRED` | CONFIRMED HARDENING (ánh xạ `RSK-007`) | V2.2 được mở (`WP-D2`); HOẶC chủ dự án cho phép một lượt Gate 3 mới có thẩm quyền tường minh (không phải rerun official `T-06`); HOẶC `RSK-007` được rà soát lại |
| `H-40` | Nhánh proxy-07:00-vượt-TTL không tới lượt ở TTL baseline 12h | `CAP-ENGINE` / `WP-A3` (DONE) | CONFIRMED HARDENING | `action_ttl_seconds` vào không gian biến thiên của manifest Gate 3 (V2.2); HOẶC `behavioral_model=LOCAL_HOUR` được đấu nối (xem `H-39`); HOẶC TTL baseline đổi khỏi 12h |

Toàn văn: `PROJECT/HARDENING_BACKLOG.md`. **Không mục nào được nâng lên đường găng của `GATE-B`**:
cả hai đều thiếu điều kiện "hậu quả nghiệp vụ nằm trong một Completion Gate đang mở" theo
`REVIEW_PROTOCOL.md`, và cả hai đều đụng vùng bị BT §22 / Master Index §6 đóng băng.
**Không sửa finding không liên quan nào khác.**

## 20. Production Diff

    $ git diff --stat b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    (không có output)

    $ git diff --shortstat b778dc1..HEAD -- src/eth_dca_os webapp pyproject.toml pyproject.lock
    (không có output)

**0 file, 0 dòng.** Production path đọc từ `PROJECT/PRODUCTION_PATHS.md` §1, không suy luận tại
thời điểm chạy.

Cũng không chạm: `docs/spec/**` (0 byte đổi), `webapp/**` (0), tag `v2.1.5-official-T06` (không
di chuyển, không tạo lại), `docs/T06_OFFICIAL_EVIDENCE_RECORD.md` (0), `DEC-005` (0). Về `data/`:
thư mục này KHÔNG tồn tại trong container của phiên (repo được clone mới), và không lệnh nào của
phiên tạo, xoá, clean, stash hay commit nó; mọi dataset dùng cho test/replay nằm ngoài repo
(`tmp_path` của pytest và thư mục scratch của phiên).

Phân biệt loại bằng chứng dùng trong báo cáo này:

- **official evidence** — chỉ ĐỌC (`DEC-031`, verdict `DO_NOT_BUILD`); không tái tạo, không diễn giải lại.
- **replay evidence** — payload bất biến §14, sinh từ dataset synthetic seed cố định qua chính
  pipeline production; dùng để so TRƯỚC–SAU, **không** dùng làm số official.
- **test evidence** — 141 ca của gói, chạy trên dataset dựng bằng `wp_a3_harness.build_dataset`.

## 21. Validators

Chạy tại HEAD của phiên, từ gốc repo:

| Validator | Kết quả | Kích thước tập được kiểm |
|---|---|---|
| `validate_structure.py` | **PASS** | 27 required path |
| `validate_project_state.py` | **PASS** | — |
| `validate_governance.py` | **PASS** | 7 CORE ref, 7 CORE file, 7 PROJECT file, 2 adapter, 5 hard-stop, 26 source invariant, 3 lineage root, **40 hardening item**, 13 production path row, 22 task file |
| `validate_routing.py` | **PASS** | 19 task MAJOR, 0 manual override |
| `sync_easy_roadmap.py` | **PASS** | ghi lại `PROJECT/LO_TRINH_DE_HIEU.md` (file sinh — không sửa tay) |
| `validate_easy_roadmap.py` | **PASS** | — |
| `validate_evidence.py` | PASS **VACUOUS** | *"Checked 0 REQUIRED PASS evidence record(s)"* |
| `validate_task_completion.py` | PASS **VACUOUS** | *"Checked 0 DONE task(s)"* |

Hai PASS cuối **không phải bằng chứng có ý nghĩa** (`STATE_AUTHORITY.md` § Vacuous Validation):
hai script glob `TASK-*.md` trong khi repo dùng `WP-*.md`/`T-*.md`, nên chúng kiểm 0 bản ghi.
Đây là khiếm khuyết ĐÃ ĐƯỢC GHI (`H-08`, `CAP-GOVTOOL` chưa có owner) và chính
`validate_governance.py` in cảnh báo về nó. Phiên này **không sửa governance tooling** theo đúng
đề bài.

**Chống sinh sôi task** (`CAPABILITY_MODEL.md` §II.9, `task_registry_snapshot.sh`):

    SET B (task file dưới docs/tasks/)   : 22  ->  22
    SET A (task ID trong vùng registry)  : 29  ->  29     (đếm đủ 10 trạng thái vòng đời)
    new_registered_task_ids              : 0
    proposals_created                    : 0
    owner_assignment_required_entries    : +1 (trong H-39, không phải task ID)

Lưu ý đo lường: `task_registry_snapshot.sh` báo `count_roadmap_task_ids` **28 → 27** vì biểu thức
lọc của nó thiếu `IMPLEMENTED` và `VERIFYING` — đúng khiếm khuyết đã ghi ở **`H-38`**, không phải
task bị mất. Con số SET A đúng (29 → 29) đo bằng cách bổ sung hai trạng thái đó vào biểu thức.

## 22. Lifecycle State

    WP-B2:  READY  ->  IN_PROGRESS  ->  IMPLEMENTED

`STATE_AUTHORITY.md` § "The State Machine And Who May Write It": implementer được ghi
`IN_PROGRESS`, `IMPLEMENTED` (ánh xạ `READY_FOR_REVIEW`); `DONE` là quyền của chủ dự án hoặc một
completion authority được chỉ định. Tiền lệ trong chính repo: `WP-B1`/`DEC-034`,
`WP-C2`/`DEC-036`, `WP-B3`/`DEC-037`.

    OWNER_DECISION_REQUIRED — đóng vòng đời: WP-B2: IMPLEMENTED -> DONE

**Không** `E2_REQUIRED`: gate đóng băng của `WP-B2` đặt `Risk = 2 → E1` và không check nào yêu
cầu E2. Gói cũng không tự chứng nhận bất kỳ mức nào cao hơn mức thực sự chạy.

Không hard-stop nào khác được viện dẫn: không `READY_GATE_FAIL`, không `SPEC_OR_OWNER_CONFLICT`,
không `CONTRACT_CONFLICT`, không `BEHAVIOR_CHANGED`, không `CHANGE_BUDGET_EXCEEDED`, không
`SCOPE_CHANGED`, không `SOURCE_STATE_REVIEW_REQUIRED`.

## 23. Gate-B Readiness

    GATE-B  =  WP-B1 DONE  ∧  WP-B2 DONE  ∧  WP-B3 DONE

| Gói | Trạng thái sau phiên này |
|---|---|
| `WP-B1` | **DONE** (`DEC-034`) |
| `WP-B2` | **IMPLEMENTED** — chưa `DONE` |
| `WP-B3` | **DONE** (`DEC-037`) |

**`GATE-B` VẪN CHƯA MỞ.** Phiên này KHÔNG mở `GATE-B` và không đề nghị mở: điều kiện đòi `DONE`,
và `IMPLEMENTED` không phải `DONE`. Đúng một mắt xích còn thiếu, và mắt xích đó là một **quyết
định đóng vòng đời của chủ dự án**, không phải thêm việc kỹ thuật.

`T-07` vẫn `NOT READY` (chờ `GATE-B`) và KHÔNG được bắt đầu trong phiên này. `T-11` vẫn
`BLOCKED`. `WP-C3` giữ `READY`, KHÔNG mở. `T-08` vẫn bị `DEC-005` (`PENDING`) chặn.
`T-06 = DONE`, V2.1.5 validation = `FAILED`, verdict = `DO_NOT_BUILD`,
`can_proceed_to_app = false` — **không đổi**.

## 24. Files Changed

**Tạo mới**

    tests/wp_b2_probe.py                              299 dòng   dụng cụ quan sát từng nến
    tests/test_wp_b2_spec21_2_capital_ladder.py       312 dòng    9 ca  — §21.2
    tests/test_wp_b2_spec21_3_execution.py            538 dòng   31 ca  — §21.3
    tests/test_wp_b2_spec21_4_accounting.py           220 dòng    5 ca  — §21.4
    tests/test_wp_b2_spec21_coverage_matrix.py        158 dòng   96 ca  — bảng đối chiếu §21
    docs/reviews/WP-B2-IMPLEMENTATION-REPORT.md                  báo cáo này
    docs/sessions/S026-wp-b2-bo-sung-test-spec21.md              session handoff

**Sửa**

    docs/CONVENTIONS.md                    +57   mục "Đối chiếu requirement Backtest §21 → test"
    PROJECT/HARDENING_BACKLOG.md           +83   H-39, H-40
    PROJECT/PROJECT_PROGRESS.md            +56/-…  Last Updated, dòng roadmap WP-B2, cây phụ thuộc, GATE-B
    PROJECT/CAPABILITY_REGISTRY.md          +1/-1  CAP-VERDICT
    PROJECT/REVIEW_BUDGET_LEDGER.md         +1/-1  CAP-VERDICT (0 repair cycle, diff production = 0)
    PROJECT/LO_TRINH_DE_HIEU.md             +1/-1  SINH TỰ ĐỘNG bởi sync_easy_roadmap.py (không sửa tay)
    docs/tasks/WP-B2-...con-thieu.md      +398/-…  trạng thái, subtask, Ready Gate, kết quả 10 check,
                                                  Exit Criteria, Changed Files Registry

**KHÔNG chạm**: `src/eth_dca_os/**`, `webapp/**`, `pyproject.toml`, `pyproject.lock`,
`docs/spec/**`, `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`, tag `v2.1.5-official-T06`, `data/`.

## 25. Commit / Push

Xem cuối tài liệu — mục này được điền bằng SHA thật sau khi commit và push.

## 26. Exact Next Action

Đúng một hành động, và nó thuộc chủ dự án:

> **Xem xét bằng chứng của `WP-B2` và quyết định `IMPLEMENTED → DONE`.**
> Nếu chấp thuận, ghi một Owner Decision mới trong `PROJECT/PROJECT_DECISIONS.md` (tiếp nối
> `DEC-037`) và cập nhật `PROJECT/PROJECT_PROGRESS.md` + `PROJECT/CAPABILITY_REGISTRY.md`.

Sau đó — và **chỉ sau đó** — `GATE-B` mới đủ điều kiện được đánh giá theo thẩm quyền canonical
(`WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`). `T-07` vẫn là một bước DUYỆT của con người, không phải việc
của agent.

Hai việc **không** nằm trong hành động kế tiếp: sửa `H-39`/`H-40` (đã định tuyến HARDENING kèm
re-trigger), và mở `WP-C3`/`T-07`/`T-08`.
