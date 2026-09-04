# WP-C2 Implementation Report

Phiên: `S024` · Ngày: 2026-09-04 · Vai trò: **implementer** (không phải phiên rà soát độc lập)
Nhánh: `claude/wp-c2-execution-state-y4rraf` · Tách từ: `origin/main` `2189a8f8`

---

## 1. Executive Summary

`WP-C2` đã được thực thi trọn vẹn trong đúng phạm vi đã đóng băng. Gói này **đặt tên** cho hành
vi đã có, không viết logic thực thi mới.

**Kết quả một dòng:** 8/8 REQUIRED check PASS · kết quả backtest **không đổi bit-for-bit** ·
diff production **1 file, +128/−0** · full suite **494/494 PASS** · `WP-C2`: `READY →
IN_PROGRESS → IMPLEMENTED` · **chưa `DONE`** vì `DONE` là quyền của chủ dự án.

Việc đã làm, gọn trong bốn ý:

1. **Một vốn từ vựng duy nhất.** `src/eth_dca_os/engine.py::ExecutionState` — `StrEnum` mang
   đúng sáu giá trị mà Strategy §16/§19 liệt kê, đối chiếu trực tiếp với văn bản spec bằng test.
2. **Một hàm thuần hợp nhất.** `derive_execution_state(...)` gộp bốn dữ kiện engine ĐÃ CÓ
   (`Zone.status` đang mở/tới hạn, `data_quality`, cooldown/override) thành đúng một trạng thái,
   đo tại một điểm cố định trong chu kỳ 15m. **Không có class `StateMachine`** — `RCP-001` /
   `CHECK-C2-07` cấm dựng kiến trúc chỉ để khớp danh từ trong spec.
3. **Lưu vết ở hai hình dạng, cùng một nguồn.** `execution_state_timeline` (ghi-khi-đổi, đọc
   lại được trạng thái ở TỪNG nến — và đúng là hình dạng `previous_state`/`new_state` mà
   `WP-B3` cần) và `market_snapshots` (một bản ghi mỗi accounting day, `execution_state` **NOT
   NULL** theo Data Model §4).
4. **`FUNDING_REQUIRED` được xử lý tường minh**, đúng `ADR-001`: `NOT_APPLICABLE` ở tầng
   backtest, nhưng VẪN nằm trong enum vì Product Spec §6/§7/§11 bắt buộc nó ở tầng app.

**Điều quan trọng nhất cần chủ dự án tin được:** con số backtest không nhúc nhích. Một payload
chuẩn tắc 1.340.788 byte (Gate 1 chín window + OOS + Gate 2/3 + Control F/G + verdict + hai lần
chạy engine toàn kỳ, kèm từng bản ghi purchase) cho **cùng một `sha256`** ở hai lần chạy baseline
TRƯỚC khi sửa và ở lần chạy SAU khi sửa.

**Việc còn lại: đúng một quyết định của chủ dự án** — đóng vòng đời `IMPLEMENTED → DONE`.
Xem §22 và §26.

---

## 2. Source / Branch / Commit

| Mục | Giá trị |
|---|---|
| Canonical source | `origin/main` |
| Expected HEAD (theo đề bài) | `2189a8f817ad8acaa2433c5be9d9afead9059f92` |
| `git rev-parse origin/main` đo được | `2189a8f817ad8acaa2433c5be9d9afead9059f92` ✅ khớp |
| Nhánh thực thi | `claude/wp-c2-execution-state-y4rraf` (tách từ đúng SHA trên, 0 commit lệch) |
| Commit thực thi | `148f9011c0d4198aa942c5f85a57a164e652e722` (1 commit trên nhánh) |
| Interpreter | Python 3.11.15 |
| Dependency | đúng theo `pyproject.lock`: numpy 2.4.6 · pandas 3.0.5 · pyarrow 25.0.1 · pytest 9.1.1 |
| `data/` (untracked, chủ dự án giữ có chủ ý) | **KHÔNG đụng tới** — không clean, không stash, không commit |

Branch authority check (`governance/scripts/governance/branch_authority_check.sh`) chạy TRƯỚC
khi đọc bất kỳ file trạng thái nào:

    branch            = claude/wp-c2-execution-state-y4rraf
    default branch    = main (resolved, not assumed)
    ahead of default  = 0 commit(s)
    divergence LOC    = 0
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: FAIL
    - attached branch has no upstream

**Duy nhất một lý do FAIL: nhánh chưa có upstream** — đúng như mong đợi với một nhánh vừa tạo
chưa push. Điều kiện thực chất mà check này bảo vệ (đọc trạng thái từ nhánh cũ/lệch) **được
thoả**: nhánh trùng khớp `origin/main` 0 commit, 0 LOC lệch, worktree sạch. Không có
`INTEGRATION_DECISION_REQUIRED`.

Chạy lại SAU khi push (upstream đã tồn tại):

    behind upstream   = 0
    ahead of default  = 1 commit(s)
    divergence age    = 0 day(s)
    integration       = INTEGRATION_DECISION_REQUIRED=NO
    tracked worktree  = CLEAN
    production diff   = EMPTY
    BRANCH AUTHORITY: PASS

---

## 3. Ready Gate

Xác nhận lại TOÀN BỘ Ready Gate **trước khi sửa một dòng production nào**, đọc từ nguồn canonical
chứ không từ báo cáo:

| Dòng Ready Gate | Nguồn đã đọc | Kết quả |
|---|---|---|
| `DEC-005` đã được chủ dự án quyết định tại T-05 | `PROJECT/PROJECT_DECISIONS.md` `DEC-035` (RESOLVED / APPROVED PA-A, 2026-09-04) | THOẢ qua phân xử HẸP |
| ADR phạm vi Execution State tồn tại và được chấp nhận | `docs/adr/ADR-001-wp-c2-execution-state-scope.md`, `Status: Accepted` | THOẢ |
| `WP-C2 = READY` | `PROJECT/PROJECT_PROGRESS.md` bảng roadmap; `PROJECT/CAPABILITY_REGISTRY.md` `CAP-WEBAPP` | THOẢ |
| Completion Gate đã finalize và đóng băng | `docs/tasks/WP-C2-execution-state-machine.md` — FROZEN 2026-08-23, đúng 8 REQUIRED check | THOẢ |
| Các dòng còn lại (objective / scope / out-of-scope / touch area / requirement / data / security / D-R-B / escalation) | file task | THOẢ, đã `[x]` từ trước |

**Kết luận: Ready Gate THOẢ — không có `READY_GATE_FAIL`.** Không một dòng governance nào bị
sửa để làm nó thoả. Dòng cuối "Xác nhận lại toàn bộ Ready Gate khi mở task" nay `[x]`.

Trạng thái vòng đời đã ghi: `READY → IN_PROGRESS → IMPLEMENTED` (cả hai bước này thuộc thẩm
quyền Implementer theo `STATE_AUTHORITY.md`).

Cũng đã kiểm chứng và **KHÔNG đổi**: `DEC-005` vẫn `PENDING`; `T-08` vẫn bị `DEC-005` chặn.

---

## 4. Canonical Scope

Đọc theo thứ tự thẩm quyền `AGENTS.md` §1: CORE V4.3 → `PROJECT/` → task/ADR → spec.

**Trong phạm vi (đã làm):** đặt tên/hợp nhất `WAIT`, `READY_TO_BUY`, `ACTION_PENDING`,
`COOLDOWN`, `DATA_BLOCKED` trong `engine.py`; lưu `execution_state` vào `market_snapshots`;
viện dẫn `ADR-001`; ghi quy ước `docs/CONVENTIONS.md` #22; test.

**Ngoài phạm vi (đã KHÔNG làm):** mô hình hoá treasury USDT động; Market Regime (WP-A3);
partial fill (WP-C3); `decision_log` (WP-B3); mọi thay đổi `webapp/`; sửa `docs/spec/`; đổi bất
kỳ kết quả backtest nào.

**Không chạm** (đúng Do-not-touch của task và của đề bài): `regime.py`, `capital.py`, `score.py`,
`ladders.py`, `verdict.py`, `benchmarks.py`, `gates.py`, `failure_signals.py`, toàn bộ `webapp/`,
`docs/spec/`, `pyproject.toml`, `pyproject.lock`, ngưỡng Gate, ngưỡng failure-signal, evidence
T-06, tag official. Không chạy lại T-06. Không chạy lại Control F/G ngoài phép đo bất biến.
Không điều tra AE. Không thiết kế V2.2. Không sửa một chữ nào của `ADR-001` đã Accepted.

---

## 5. Pre-Implementation Behavior Map

Đọc `engine.py` trước khi sửa, đối chiếu bảng hiện trạng S001 với mã thật:

| Execution State | Hành vi ĐÃ CÓ trong engine (trước gói này) | Đo bằng gì trong bản sửa |
|---|---|---|
| `WAIT` | Ngầm — không điều kiện thực thi nào đang hiệu lực | mặc định khi ba vế còn lại đều sai |
| `READY_TO_BUY` | Ngầm — bước 12: `z.execute_at is not None and ts >= z.execute_at` và còn TTL → vào `due_fills` | `action_due = bool(due_fills)` |
| `ACTION_PENDING` | Tường minh nhưng ở **chiều khác** (`Zone.status`, enum 9 giá trị của ST §19) | `action_open` — zone `ACTION_PENDING` chưa tới hạn và chưa hết TTL, đếm ngay trong vòng lặp bước 12 đã có |
| `COOLDOWN` | Biến cục bộ bước 11: `in_cooldown = ts < cooldown_until`, cùng `override_ok` | `cooldown_blocking = in_cooldown and not override_ok` |
| `DATA_BLOCKED` | Hành vi có (`dq != "INVALID"` chặn action mới ở bước 14c) nhưng không tên, không lưu | `data_invalid = dq == "INVALID"` |
| `FUNDING_REQUIRED` | **Không có hành vi để đặt tên** — engine không giữ số dư USDT treasury; `funding_delay` là hàm của `funding_policy` (`CONVENTIONS` #8) | không đo — `NOT_APPLICABLE` theo `ADR-001` |

**Khoảng trống ngữ nghĩa nhỏ nhất** rút ra từ bảng trên: thiếu (a) một cái tên chung, (b) một
điểm đo chung, (c) một thứ tự ưu tiên khi nhiều điều kiện cùng đúng, (d) một nơi lưu. Bốn thứ đó
là toàn bộ nội dung của bản sửa. **Không thiếu một hành vi nào.**

Sáu trạng thái của spec **PHỦ HẾT** hành vi thật của engine — không có tình huống nào phải viện
tới một trạng thái thứ bảy. Không phát sinh `SCOPE_CHANGED`.

---

## 6. Change Budget

**Trước khi sửa (dự kiến):** 1 file production (`engine.py`), ước ~120 LOC thêm mới, không xoá;
capability owner `CAP-WEBAPP` (lineage root `WP-C1`); budget hiện hành `ALLOWED 2 / USED 0 /
REMAINING 2` (`DEC-018`/`OD-WEBAPP-01`).

**Sau khi sửa (đo trực tiếp bằng lệnh chuẩn `PRODUCTION_PATHS.md` §1, không cộng tay):**

    git diff --shortstat 2189a8f -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> 1 file changed, 128 insertions(+)

| Hạng mục | Đo được |
|---|---|
| File production đổi | **1** — `src/eth_dca_os/engine.py` |
| +LOC / −LOC production | **+128 / −0** (thuần thêm mới — không một dòng hành vi cũ nào bị xoá hay sửa) |
| `webapp/` | 0 dòng (không mở rộng bề mặt trôi parity `RSK-002`) |
| `pyproject.toml` / `pyproject.lock` | 0 dòng (`dependency_lock_hash` của run record không đổi) |
| Test thêm mới | 4 file, 942 dòng (`tests/` **không** phải production path — `PRODUCTION_PATHS.md` §2) |
| Docs / PROJECT đổi | `docs/CONVENTIONS.md` +82, `docs/tasks/WP-C2-*.md` +299/−54, `PROJECT/*` (progress, registry, ledger, hardening, roadmap sinh lại) |
| Repair cycle tiêu | **0** — `WP-C2` chưa từng `DONE` nên chưa có chu kỳ nào để mở; đây là INITIAL IMPLEMENTATION, cùng quy ước `WP-A4`/`T-09A`/`T-09B`/`WP-B1` |
| Budget sau phiên | `ALLOWED 2 / USED 0 / REMAINING 2` — **không đổi** |
| Task ID mới tạo | **0** |

Bốn ngưỡng Absorption Limit (`CAPABILITY_MODEL.md`): không ngưỡng nào bị chạm — chi tiết ở
`PROJECT/REVIEW_BUDGET_LEDGER.md` §8. Không `CHANGE_BUDGET_EXCEEDED`, không `SCOPE_CHANGED`.

---

## 7. Implementation

Toàn bộ thay đổi production nằm trong `src/eth_dca_os/engine.py`, ba mảnh:

**(1) Vốn từ vựng** — `class ExecutionState(StrEnum)` với đúng sáu giá trị, cộng hằng
`BACKTEST_NOT_APPLICABLE_STATES = (ExecutionState.FUNDING_REQUIRED,)` để `ADR-001` được viện dẫn
**trong chính mã**, không chỉ trong tài liệu. `StrEnum` để giá trị vừa là hằng có kiểu (không gõ
nhầm được) vừa là `str` thuần khi serialize.

**(2) Hàm thuần** — `derive_execution_state(*, action_due, action_open, data_invalid,
cooldown_blocking)`: năm câu `if`, không đọc và không ghi state nào của engine.

**(3) Điểm đo + lưu vết** — trong vòng lặp chính:

- bước 12 (đã có) được thêm đúng một nhánh `else: open_actions += 1` — đếm zone còn mở **ngay
  trong vòng lặp đang chạy**, nên không quét lại toàn bộ ladder mỗi nến (7,5 năm × hàng trăm
  zone sẽ là chi phí thật);
- **bước 12b** (mới): gọi hàm thuần, và append vào `execution_state_timeline` **chỉ khi đổi** —
  cùng khuôn với `regime_timeline` mà WP-A5 đã dùng;
- tại điểm snapshot theo ngày sẵn có (cạnh `cash_samples` / `opp_cap_samples`): append một bản
  ghi `market_snapshots`.

**Vì sao điểm đo là bước 12b.** Đó là nơi duy nhất cả bốn dữ kiện vừa đủ và chưa bị chính nến đó
làm nhoè: bước 8 đã chốt `data_quality`, bước 11 đã chốt cooldown/override, bước 12 vừa phân loại
xong action tới hạn — và `READY_TO_BUY` **chỉ tồn tại ở đó**, vì tới bước 16–17 fill đã xong và
zone đã `EXECUTED`. Action MỚI của nến này chưa được tạo (bước 14c), nên nó xuất hiện dưới dạng
`ACTION_PENDING` từ nến kế tiếp.

**Thiết kế tối thiểu, có chủ ý.** Không class, không đối tượng có vòng đời, không bảng chuyển
trạng thái, không biến trạng thái mới trong engine. `Zone.status`, `in_cooldown`, `data_quality`
**giữ nguyên** vai trò nguồn sự thật; chiều mới là **dẫn xuất** đọc từ chúng — nên không sinh ra
nguồn sự thật cạnh tranh.

---

## 8. Execution State Semantics

Ngữ nghĩa tường minh của từng trạng thái, và thứ tự ưu tiên khi nhiều điều kiện cùng đúng.

| Trạng thái | Nghĩa | Điều kiện |
|---|---|---|
| `READY_TO_BUY` | Một action đủ điều kiện thực thi NGAY tại nến này | có zone `ACTION_PENDING` đã tới `execute_at` và còn TTL |
| `ACTION_PENDING` | Action tồn tại nhưng chưa tới hạn thực thi | có zone `ACTION_PENDING` chưa tới hạn, chưa hết TTL |
| `DATA_BLOCKED` | Không tạo được action mới vì dữ liệu không an toàn để quyết | `data_quality == INVALID` (ST §3) |
| `COOLDOWN` | Không tạo được action mới vì cooldown đang chặn | trong cooldown và override KHÔNG kích hoạt |
| `WAIT` | Không có điều kiện thực thi nào đang hiệu lực | bốn vế trên đều sai |
| `FUNDING_REQUIRED` | Trạng thái canonical của sản phẩm — **`NOT_APPLICABLE` ở tầng backtest** | không phát sinh (§9) |

**Thứ tự ưu tiên:** `READY_TO_BUY > ACTION_PENDING > DATA_BLOCKED > COOLDOWN > WAIT`.

Thứ tự này **lấy từ chính hành vi engine**, không phải thẩm mỹ:

- Hai trạng thái đầu mô tả một action **đã tồn tại**. Bước 12 và 16–17 KHÔNG đọc `dq` cũng không
  đọc `in_cooldown`, nên một action đã tạo vẫn fill kể cả khi dữ liệu INVALID hoặc đang cooldown
  → khi có action mở thì chính nó LÀ trạng thái thực thi.
- Hai trạng thái sau mô tả vì sao **không tạo được action mới**, và bước 14c kiểm
  `dq != "INVALID"` **trước** rồi mới kiểm cooldown → `DATA_BLOCKED` đứng trước `COOLDOWN`.

Bảng quyết định đầy đủ 16 tổ hợp được đóng băng bằng test
(`test_c2_02_derivation_precedence_table_is_frozen`) và ghi ở `docs/CONVENTIONS.md` #22(c).

**Sáu trạng thái phủ hết hành vi thật** — không phát sinh trạng thái thứ bảy, không phát sinh
`SCOPE_CHANGED` (`test_c2_02_no_seventh_state_can_be_produced_by_the_derivation` duyệt vét cạn
không gian đầu vào).

---

## 9. ADR-001 Compliance

`ADR-001` (Accepted 2026-09-04, `DEC-035`) **không bị mở lại, không bị sửa một chữ**. Nội dung
của nó được thi hành đúng ở bốn nơi:

1. **Trong mã production:** `BACKTEST_NOT_APPLICABLE_STATES = (ExecutionState.FUNDING_REQUIRED,)`
   kèm chú thích nêu lý do và viện dẫn `ADR-001`/`DEC-035`.
2. **Trong quy ước:** `docs/CONVENTIONS.md` #22(d).
3. **Bằng cấu trúc:** engine không mô hình hoá số dư treasury — quét `ast` trên `engine.py` và
   `execution.py` xác nhận không định danh nào mang khái niệm treasury (quét định danh thật, bỏ
   qua comment).
4. **Bằng số đo:** `FUNDING_REQUIRED` xuất hiện **0 lần** trên 13 lần chạy production-realistic
   và 4 kịch bản; `states_never_observed = ['FUNDING_REQUIRED']`.

**Tầng app KHÔNG bị thu hẹp.** Trạng thái vẫn nằm trong enum, và cả docstring lẫn `CONVENTIONS`
#22(d) viện dẫn Product Spec §6/§7/§11 (`CHECK TREASURY → [FUNDING_REQUIRED] → READY_TO_BUY`) để
tầng live sau này không đánh rơi nó. Đây là **tuyên bố `NOT_APPLICABLE`**, không phải vắng mặt
im lặng.

Không phát hiện xung đột nào giữa `ADR-001` và spec canonical. Không `CONFLICT DETECTED`, không
cần chuyển `WP-D2`.

---

## 10. Market Regime Separation

Strategy §16 đòi Execution State và Market Regime là **hai chiều độc lập, phải được lưu riêng**.
Đã chứng minh bằng bốn cách, không cách nào dựa vào lời kể:

1. **Cấu trúc dữ liệu thật:** mỗi bản ghi `market_snapshots` có HAI trường riêng biệt —
   `market_regime` (nhãn §16 do `RegimeTracker` cấp, thuộc WP-A3) và `execution_state`.
2. **Biến thiên độc lập:** ở kịch bản `crash_regime_cycle`, `market_regime` chạy qua bốn nhãn
   `NORMAL / STRESSED / CRASH / RECOVERY` trong khi `execution_state` biến thiên theo nhịp riêng.
3. **Không trộn nhãn:** không giá trị Execution State nào chứa token regime — thiết kế kiểu
   `CRASH_READY_TO_BUY` / `STRESSED_WAIT` / `RECOVERY_COOLDOWN` bị test cấm.
4. **`regime.py` KHÔNG ĐỔI một dòng** (`git diff` rỗng) và không nhắc tới enum mới. WP-A3 vẫn là
   `DONE` lịch sử, hành vi regime không bị định nghĩa lại.

**Và chiều mới không thể tác động ngược vào hành vi** — chứng minh bằng HÀNH VI chứ không bằng
đọc mã: ép `derive_execution_state` trả một giá trị SAI rồi chạy lại engine trên cả bốn kịch bản
→ fingerprint kết quả vẫn trùng khớp cây mã trước WP-C2. Nếu có bất kỳ nhánh execution nào đọc
Execution State, phép ép này phải làm kết quả đổi.

---

## 11. Persistence / market_snapshots

Data Model §4 xếp `market_regime`, `execution_state`, `data_quality` vào nhóm **LUÔN NOT NULL**.
`RunResult.market_snapshots` sinh một bản ghi mỗi accounting day, cùng nhịp và cùng vị trí với
`cash_samples` sẵn có. Trường của một bản ghi:

`ts` · `accounting_date_local` · `eth_price` · `opportunity_score_raw` · `smart_unlock` ·
`opportunity_unlock` · `smart_unlock_peak` · `opportunity_fund_balance_vnd` ·
`opportunity_fund_available_vnd` · `opportunity_fund_reserved_vnd` · `market_regime` ·
`execution_state` · `data_quality`

**Đo được: 17.532 bản ghi trên 13 lần chạy production-realistic, `execution_state` NULL = 0.**

Không thêm kiến trúc lưu trữ nào khác: không đụng Firestore, không đụng `webapp/`, không thêm
file production nào.

**Giới hạn phạm vi được TUYÊN BỐ (không phải ô trống im lặng).** Bản ghi mang các nhóm DM §4 mà
engine đã có tại điểm đo (identity / market `eth_price` / score / capital / state); **chưa** mang
`btc_price` và ba nhóm indicator (price location, market stress, relative value) — sinh chúng đòi
kéo cột chỉ báo mới vào `engine.py`, tức mở rộng phạm vi production ngoài Scope Lock. Ghi ở
`docs/CONVENTIONS.md` #22(f) và `PROJECT/HARDENING_BACKLOG.md` **H-34** kèm điều kiện tái kích
hoạt. Định danh cấp run (`strategy_version`, `strategy_config_hash`) không lặp trên từng dòng —
đã có trong run record (DM §12), cùng quy ước với dòng `capital_ledger`.

Bổ sung cho `market_snapshots`: `execution_state_timeline` ghi `(ts, state)` **chỉ khi đổi**, nên
đọc lại được trạng thái **tại từng nến 15m** (mốc gần nhất `<=` thời điểm cần hỏi) mà chi phí bộ
nhớ vẫn nhỏ (1.044–1.078 mốc cho 7,5 năm).

---

## 12. WP-B3 Downstream Contract

`WP-B3` cần `previous_state` / `new_state` (DM §11) theo **enum của WP-C2**, không được tự định
nghĩa enum thứ hai (`CHECK-B3-02` nói rõ điều này). Hợp đồng WP-C2 cấp:

```python
from eth_dca_os.engine import ExecutionState        # sáu giá trị canonical
```

- `StrEnum` nên mỗi giá trị **là** một `str`: `json.dumps({"new_state": ExecutionState.READY_TO_BUY})`
  cho `{"new_state": "READY_TO_BUY"}` — không rò rỉ `repr` của enum, không cần adapter.
- Đọc ngược: `ExecutionState("READY_TO_BUY")` trả về đúng thành viên.
- **Chuỗi chuyển trạng thái đã có sẵn:** `RunResult.execution_state_timeline` là danh sách
  `(ts, state)` ghi-khi-đổi, tức mỗi cặp liên tiếp CHÍNH LÀ một `(previous_state, new_state)`.
  `WP-B3` không phải tự phát hiện chuyển trạng thái.
- Test khoá hợp đồng: `test_c2_downstream_contract_is_consumable_without_a_second_enum`.

**KHÔNG làm trong phiên này** (đúng phạm vi): không cài `decision_log`, không mở `WP-B3`, không
đổi trường nào của `decision_log` hiện có. `RunResult.decision_log` giữ nguyên nội dung — đây là
một trong các trường được so bit-for-bit ở §14.

---

## 13. Adversarial Tests

`tests/test_wp_c2_execution_state.py` — **33 test, tất cả PASS**. Mọi trạng thái được quan sát
qua `run_engine` THẬT trên kịch bản tất định (`tests/wp_c2_scenarios.py`), **không dựng bằng
tay**, rồi đối chiếu với nguồn sự thật đã có (bản ghi purchase, tham số delay của
`execution_config`, `cooldown_hours`, cửa sổ dữ liệu INVALID).

| Yêu cầu đối kháng | Đã kiểm bằng | Kết quả |
|---|---|---|
| **A** — đường `WAIT` | `wait_only`: 576/576 nến là `WAIT`, timeline đúng một mốc | PASS |
| **B** — đường `READY_TO_BUY` | tập nến `READY_TO_BUY` **trùng khớp tuyệt đối** với tập nến có fill zone thật, ở cả 4 kịch bản | PASS |
| **C** — đường `ACTION_PENDING` | số nến = ĐÚNG `total_delay` của config: 20 nến với `gate3_realistic` (4h+1h), 1 nến với `gate1_low_friction` (15′) | PASS |
| **D** — đường `COOLDOWN` | phủ đúng cửa sổ `cooldown_hours` sau fill trừ chính nến fill: nến đầu = fill+15′, nến cuối = fill+47h45′, tổng 191 | PASS |
| **E** — đường `DATA_BLOCKED` | phủ đúng cửa sổ hai ngày daily INVALID, biên chính xác 07:00 local Day 3 → 07:00 local Day 5, 192 nến | PASS |
| **F** — `FUNDING_REQUIRED` không im lặng phát sinh | vét cạn 16 tổ hợp đầu vào + 0 lần trên mọi lần chạy (timeline và snapshot) + quét `ast` không có khái niệm treasury | PASS |
| **G** — Regime ⟂ Execution State | hai trường riêng, ≥3 nhãn regime cùng ≥2 execution state trong một lần chạy; không giá trị nào mang token regime; `regime.py` không đổi | PASS |
| **H** — không bao giờ NULL | 17.532 snapshot, 0 null; kiểm cả `market_regime` ∈ enum §16 và `data_quality` ∈ {GOOD, DEGRADED, INVALID}; chống PASS rỗng bằng `assert total > 0` | PASS |
| **I** — vòng đời Zone không đổi | fingerprint kịch bản `smart_action_cycle` chụp TRƯỚC WP-C2 | PASS |
| **J** — thời điểm cooldown không đổi | fingerprint `smart_action_cycle` + `crash_regime_cycle` | PASS |
| **K** — chặn dữ liệu xấu không đổi | fingerprint `data_invalid_window` | PASS |
| **L** — không có trạng thái thứ bảy | enum đối chiếu TỪNG GIÁ TRỊ với văn bản `docs/spec/02_STRATEGY_SPEC_V2_1_5.md`; hàm dẫn xuất vét cạn không sinh giá trị ngoài enum | PASS |

Hai test đáng chú ý vì chúng là loại khó lừa nhất:

- `test_c2_02_ready_to_buy_coincides_exactly_with_zone_fills` — nếu chiều mới trở thành một
  nguồn sự thật thứ hai (lệch dù một nến) thì test đỏ.
- `test_c2_07_forcing_a_wrong_execution_state_changes_no_behaviour` — ép hàm dẫn xuất trả giá
  trị sai; fingerprint vẫn phải trùng cây mã cũ. Đây là bằng chứng HÀNH VI cho "dẫn xuất, không
  phải nguồn sự thật", mạnh hơn mọi phép soi văn bản.

---

## 14. Backtest Invariance

**Đây là ràng buộc định nghĩa của gói (`CHECK-C2-06`), và nó PASS ở mức mạnh nhất có thể: trùng
khớp bit-for-bit.**

**Cách đo.** `tests/wp_c2_invariance_tool.py` chạy đúng pipeline production và serialize toàn bộ
đầu ra ngữ nghĩa thành một chuỗi JSON chuẩn tắc (khoá sắp xếp, `repr` float của Python round-trip
đúng bit), rồi lấy `sha256`. Phạm vi payload:

- **Gate 1 đầy đủ** — chín window 24 tháng + OOS + diagnostics + bootstrap + concentration +
  cash_ratio + opportunity_cap_hit + regime_advantage + `counters_w5` + benchmarks + XIRR;
- **Gate 2** — 8 config (baseline + OFAT);
- **Gate 3** — 8 config + realistic + shortfall attribution;
- **Control F/G** — 200 sim, `MASTER_SEED`;
- **verdict** — đầy đủ, gồm 12 Failure Signal;
- **hai lần chạy engine TOÀN KỲ** (`gate1_low_friction`, `gate3_realistic`) với **từng bản ghi**
  purchase / contribution / counter / monthly_deployment / cash_sample / decision_log /
  opp_cap_sample / regime_timeline — đây là lát cắt nhạy nhất, một sai lệch ULP cũng lộ.

Cùng dataset (`dataset_hash 3ffcefbe04…`), cùng config hash, cùng seed, cùng interpreter.

**Kết quả.**

| Lần chạy | Cây mã | `sha256` payload bất biến | Kích thước |
|---|---|---|---|
| BEFORE #1 | `2189a8f` nguyên bản | `e0492a58f67e9fab0105216713ed9ca3dfecbae1608d91089ca48eef380fdbba` | 1.340.788 byte |
| BEFORE #2 | `2189a8f` nguyên bản (chạy lại độc lập) | `e0492a58…fdbba` | 1.340.788 byte |
| AFTER | sau khi sửa `engine.py` | `e0492a58…fdbba` | 1.340.788 byte |

**Hai lần BEFORE độc lập cho cùng hash.** Đây là **control của phép đo**: nó chứng minh phép so
tự nó tất định, nên "trùng khớp" ở lần AFTER là một kết quả có nghĩa, không phải một phép so
luôn luôn trùng bất kể đầu vào.

**Trường bị loại khỏi phép so — đầy đủ và tường minh.** Đúng bốn trường metadata KHÔNG mang ngữ
nghĩa chiến lược/backtest, khai trong `NON_SEMANTIC_RUN_RECORD_KEYS`: `run_id` (uuid4 mỗi lần
chạy), `created_at` (đồng hồ), `metrics_path` (đường dẫn thư mục tạm), `code_commit` (SHA của
chính commit đang đo). **Không trường nào khác bị loại**, và không một khác biệt có nghĩa nào bị
"normalize" đi. Hai trường WP-C2 thêm (`market_snapshots`, `execution_state_timeline`) nằm ở khối
`wp_c2_observability` TÁCH RIÊNG — chúng là trường **mới**, không phải trường bị đổi; phần
`invariance` không hề biết tới chúng.

**Khoá lại trong suite, vĩnh viễn.** Bốn fingerprint hành vi chụp trên cây mã TRƯỚC WP-C2 được
đóng băng trong `tests/test_wp_c2_execution_state.py::FROZEN_PRE_WP_C2_FINGERPRINTS`, phủ vòng
đời zone, thời điểm cooldown, chặn dữ liệu xấu và chu kỳ regime. Ai đổi hành vi engine về sau sẽ
làm đỏ ngay, không cần chạy lại phép đo lớn.

**Không phát sinh `SCOPE_CHANGED` và không phát sinh `SPEC_CONFLICT`.**

---

## 15. Production Reachability

Unit test một mình không đủ, nên đây là bằng chứng chạy thật ở quy mô thật:
`tests/wp_c2_reachability_tool.py` trên dataset tổng hợp 7,5 năm, **13 lần chạy qua đúng hàm
production**.

| Lát cắt | Đường chạy | Kết quả |
|---|---|---|
| 9 window Gate 1 | `metrics.window_metrics` — chính hàm `pipeline.run_gate1` gọi | mỗi window 731–732 snapshot, 173–340 mốc đổi, 0 null |
| Toàn kỳ × 2 config | `engine.run_engine`, 2019-01-01 → OOS end | 2.737 snapshot mỗi lần, 1.044 / 1.078 mốc đổi |
| Toàn kỳ × 2 config, dataset **xoá một hàng daily** `2020-06-15` | cùng đường chạy — thủ thuật đã dùng ở WP-A6 để dựng cửa sổ `INVALID` ~31 ngày | 992 / 1.012 mốc đổi, **quan sát được `DATA_BLOCKED`** |

Tổng hợp:

    states_observed_union      = ACTION_PENDING, COOLDOWN, DATA_BLOCKED, READY_TO_BUY, WAIT
    states_never_observed      = FUNDING_REQUIRED
    total_snapshots            = 17.532
    total_null_execution_state = 0
    total_funding_required     = 0

**Cả năm trạng thái thuộc phạm vi đều quan sát được từ runtime thật**, không trạng thái nào chỉ
tồn tại trong unit test. `DATA_BLOCKED` cần một lát cắt riêng vì dataset tổng hợp mặc định có
`data_quality = GOOD` xuyên suốt — nói rõ điều đó ở đây thay vì để người đọc tự đoán.

`FUNDING_REQUIRED`: **`NOT_APPLICABLE` ở tầng backtest theo thẩm quyền `ADR-001`** — ghi nhận
tường minh, đúng nhánh (b) của `CHECK-C2-03`, không phải "không quan sát được nên bỏ qua".

---

## 16. Full Regression

Toàn bộ suite Python, **không deselect, không skip, không nới hay sửa một test cũ nào**:

    $ python -m pytest tests/ -p no:cacheprovider -rN --tb=short
    494 passed in 1402.46s (0:23:22)
    PYTEST_EXIT=0

| Chỉ số | Giá trị |
|---|---|
| collected | 494 |
| passed | **494** |
| failed | 0 |
| errors | 0 |
| skipped | 0 |
| xfail / xpass | 0 / 0 |
| exit code | **0** |

**Nền so sánh:** 461 test trên cây mã trước gói này (`WP-B1` / `DEC-034` ghi 461/461 tại
`9ac01b8`; hai commit sau đó tới `2189a8f` là governance-only, không đổi test nào), cộng đúng 33
test mới của `tests/test_wp_c2_execution_state.py` = **494**. `git status` xác nhận không file
test cũ nào bị sửa.

**Không có test nào FAIL, nên không có lỗi tồn tại từ trước nào phải chứng minh.**

---

## 17. Completion Gate Matrix

Dùng ĐÚNG 8 REQUIRED check đã đóng băng, **nguyên văn**. Không thêm, không bớt, không hạ mức,
không đánh `NOT_APPLICABLE` cho tiện. Evidence đầy đủ nằm trong
`docs/tasks/WP-C2-execution-state-machine.md`; bảng dưới là bản tóm cho chủ dự án.

| Check | Yêu cầu (rút gọn) | Mức | Bằng chứng chính | Kết quả |
|---|---|---|---|---|
| **C2-01** | ADR phạm vi tồn tại và được viện dẫn | E1 | `ADR-001` `Status: Accepted`; viện dẫn từ **mã production** (`BACKTEST_NOT_APPLICABLE_STATES`) và `CONVENTIONS` #22(d) | **PASS** |
| **C2-02** | Sáu trạng thái được đặt tên và lưu vết, đọc được tại từng thời điểm | E1 | enum đối chiếu văn bản spec; `execution_state_timeline` độ phân giải nến; 13 lần chạy thật quan sát đủ 5 trạng thái trong phạm vi | **PASS** |
| **C2-03** | `FUNDING_REQUIRED` xử lý tường minh, không im lặng vắng mặt | E1 | nhánh (b): tuyên bố trong mã + lý do trong ADR + mục `CONVENTIONS` #22(d) + ghi nhận tầng app vẫn phải có; 0 lần phát sinh, vét cạn 16 tổ hợp | **PASS** |
| **C2-04** | Regime và Execution State lưu riêng | E1 | hai trường riêng trong `market_snapshots`; biến thiên độc lập; `regime.py` 0 dòng đổi; ép giá trị sai không đổi hành vi | **PASS** |
| **C2-05** | `market_snapshots.execution_state` NOT NULL | E1 | 17.532 bản ghi, **0 null**; giới hạn phạm vi được tuyên bố (H-34), không bỏ trống im lặng | **PASS** |
| **C2-06** | Kết quả backtest không đổi | E1 | `sha256 e0492a58…` trùng khớp bit-for-bit; hai baseline BEFORE độc lập cùng hash; 4 fingerprint đóng băng trong suite | **PASS** |
| **C2-07** | Không tạo class `StateMachine` chỉ để khớp tên | E0 | một enum + một hàm thuần; quét mọi `class` trong `src/eth_dca_os/`; diff +128/−0; thêm bằng chứng E1 (ép giá trị sai) | **PASS** |
| **C2-08** | Toàn bộ test suite PASS | E1 | 494/494, exit 0, output đầy đủ ở §16 | **PASS** |

    REQUIRED: 8/8 PASS · FAIL: 0 · BLOCKED: 0 · NOT_APPLICABLE: 0 · NOT_TESTED: 0

Mức evidence: bảy check E1 + một check E0 — **đúng như gate FROZEN quy định** (Risk = 2 → E1 cho
các check kiểm chứng được; `CHECK-C2-07` là check thiết kế nên E0 là mức phù hợp). `CHECK-C2-07`
còn có thêm bằng chứng E1 không bắt buộc. Gate KHÔNG đòi check E2 nào.

---

## 18. Findings

Phiên này **không phát sinh finding BLOCKING nào**. Không finding nào được biến thành task ID
mới (`REVIEW_PROTOCOL.md` § "A Finding Is Not A Task"). Số task ID mới = **0**.

Hai quan sát non-blocking, cả hai đều là **giới hạn phạm vi được tuyên bố** chứ không phải khiếm
khuyết im lặng, đã route sang `PROJECT/HARDENING_BACKLOG.md` kèm `RE_TRIGGER_CONDITION`:

- **H-34** — `market_snapshots` chỉ phủ một phần các nhóm trường của DM §4 (thiếu `btc_price` và
  ba nhóm indicator). Không BLOCKING vì check duy nhất nói về bảng này là `CHECK-C2-05`
  (`execution_state` NOT NULL) và nó PASS; sinh thêm đòi mở rộng phạm vi production ngoài Scope
  Lock.
- **H-35** — trong một dòng `market_snapshots`, `execution_state` đo ở bước 12b còn khối vốn đo ở
  cuối nến. Đã cân nhắc và ghi lại hai phương án bị loại: đọc tất cả ở 12b sẽ làm
  `market_snapshots` mâu thuẫn với `cash_samples`/`opp_cap_samples` tại cùng `ts` (khiếm khuyết
  rộng hơn); đo `execution_state` ở cuối nến sẽ làm `READY_TO_BUY` không bao giờ quan sát được
  (mất một trạng thái mà `CHECK-C2-02` đòi).

**Một khiếm khuyết validator có sẵn, không do phiên này gây ra, xin nêu lại để không bị đọc nhầm
thành PASS thật:** `validate_evidence.py` và `validate_task_completion.py` glob `TASK-*.md` nên
kiểm **0 bản ghi** trên repo này ("Checked 0 REQUIRED PASS evidence record(s)"). Theo
`STATE_AUTHORITY.md` § Vacuous Validation, một PASS trên tập rỗng không phải PASS có nghĩa. Đây
là `H-08` đã có trong backlog, thuộc `CAP-GOVTOOL`, **chưa có owner** — phiên này không tự sửa
và không tự nhận (`OWNER_ASSIGNMENT_REQUIRED` vẫn đứng nguyên).

---

## 19. Hardening

`H-34` và `H-35` — nội dung ở §18, chi tiết đầy đủ kèm điều kiện tái kích hoạt ở
`PROJECT/HARDENING_BACKLOG.md`.

Cả hai **không nằm trên đường găng**, **không sinh task anh em**, và **không được sửa trong
phiên này** vì không check REQUIRED nào của `WP-C2` đòi hỏi. Không mục nào là `BLOCKING`: không
mục nào đồng thời có đường production hiện hành + hậu quả nghiệp vụ nằm trong một Completion Gate
hoặc risk register + bằng chứng tái lập được (ba điều kiện của `REVIEW_PROTOCOL.md`).

---

## 20. Production Diff

    git diff --shortstat 2189a8f -- src/eth_dca_os webapp pyproject.toml pyproject.lock
      -> 1 file changed, 128 insertions(+)

    git diff --numstat 2189a8f -- src/eth_dca_os
      -> 128    0    src/eth_dca_os/engine.py

**Thuần thêm mới: 128 dòng thêm, 0 dòng xoá.** Không một dòng hành vi cũ nào bị xoá hay sửa —
đây tự nó đã là một dấu hiệu mạnh cho "đặt tên, không thiết kế lại". Ba mảnh của diff:

| Mảnh | Dòng | Nội dung |
|---|---|---|
| Vốn từ vựng | ~48 | `ExecutionState`, `BACKTEST_NOT_APPLICABLE_STATES`, docstring |
| Hàm thuần | ~29 | `derive_execution_state` + biện minh thứ tự ưu tiên |
| Điểm đo + lưu vết | ~51 | 2 trường `RunResult`; nhánh `else` ở bước 12; bước 12b; bản ghi `market_snapshots` |

File production **không đổi** (xác minh bằng `git status`): `regime.py`, `capital.py`, `score.py`,
`ladders.py`, `verdict.py`, `benchmarks.py`, `gates.py`, `failure_signals.py`, `pipeline.py`,
`metrics.py`, `reporting.py`, `cli.py`, toàn bộ `webapp/`, `pyproject.toml`, `pyproject.lock`.

---

## 21. Validators

Chạy toàn bộ validator áp dụng được (sau khi cập nhật roadmap, và chạy `validate_routing.py`
TRƯỚC khi sync roadmap đúng thứ tự `ROADMAP_SYNC_STANDARD.md`):

| Validator | Exit | Dòng đầu |
|---|---|---|
| `validate_governance.py` | 0 | `GOVERNANCE V4.3: PASS` |
| `validate_structure.py` | 0 | `GOVERNANCE STRUCTURE: PASS` (27 required path) |
| `validate_project_state.py` | 0 | `PROJECT STATE: PASS` |
| `validate_routing.py` | 0 | `ROUTING VALIDATION: PASS` (19 MAJOR task file, 0 manual override) |
| `sync_easy_roadmap.py` | 0 | `ROADMAP SYNC: PASS - wrote PROJECT/LO_TRINH_DE_HIEU.md` |
| `validate_easy_roadmap.py` | 0 | `EASY ROADMAP: PASS` |
| `validate_evidence.py` | 0 | `EVIDENCE VALIDATION: PASS` — **nhưng "Checked 0 record"**, xem §18 (`H-08`) |
| `validate_task_completion.py` | 0 | `TASK COMPLETION: PASS` — **cũng "Checked 0 task"**, cùng `H-08` |

`validate_refactor_preservation.py` cần tham số là thư mục bản V3.2 non-compact — **không áp
dụng** cho phiên này.

**Không routing nào bị đổi để làm validator xanh.** `WP-C2` giữ nguyên Routing Inputs, Tier C,
Effort `xhigh` như đã ROUTED từ trước; `validate_routing.py` xác nhận giá trị khớp router tất
định.

`PROJECT/LO_TRINH_DE_HIEU.md` được **sinh lại bằng generator**, không sửa tay — diff đúng một
dòng (dòng `WP-C2`).

---

## 22. Lifecycle State

    WP-C2:  READY  ->  IN_PROGRESS  ->  IMPLEMENTED        (đã ghi)
            IMPLEMENTED  ->  DONE                          (CHƯA ghi — không thuộc thẩm quyền)

`governance/v4/CORE/STATE_AUTHORITY.md` § "The State Machine And Who May Write It" ghi rõ:
`DONE` do **chủ dự án, hoặc một completion authority được chỉ định** viết. Tiền lệ ngay trong dự
án này: `WP-B1` chỉ chuyển `DONE` khi có `DEC-034` — "Owner-authorized lifecycle closure".
`IN_PROGRESS` và `READY_FOR_REVIEW`/`IMPLEMENTED` thì Implementer được phép ghi, và đó là đúng
những gì phiên này đã ghi.

**Không có thẩm quyền nào được cấp tường minh cho phiên này để đóng `DONE`**, nên trạng thái
dừng ở `IMPLEMENTED`. Không giả vờ `DONE`.

**Còn lại đúng một việc — `OWNER_DECISION_REQUIRED`:**

> Chủ dự án đọc báo cáo này, xác nhận 8/8 REQUIRED PASS và Exit Criteria đã thoả, rồi ra quyết
> định đóng vòng đời `WP-C2: IMPLEMENTED → DONE` (ghi vào `PROJECT/PROJECT_DECISIONS.md` như
> `DEC-034` đã làm cho `WP-B1`).

Có cần rà soát độc lập (E2) trước khi đóng không? **Completion Gate đã đóng băng của `WP-C2`
KHÔNG đòi check E2 nào** — bảy check E1 và một check E0, khác với `WP-B1` (có `CHECK-B1-09` đòi
E2 độc lập). Nói thẳng cho rõ: báo cáo này là của **implementer**, không phải một rà soát độc
lập. Nếu chủ dự án muốn một vòng E2 cho yên tâm thì đó là **lựa chọn thêm**, không phải điều
kiện mà gate đòi — và `CAP-WEBAPP` còn `REMAINING = 2 repair cycle` nếu E2 phát hiện gì cần sửa.

---

## 23. Downstream State

**Không khởi động task downstream nào.** Chỉ báo cáo mức sẵn sàng:

| Task / Gate | Trạng thái sau phiên này | Ghi chú |
|---|---|---|
| `WP-B1` | `DONE` | không đổi (`DEC-034`) |
| `WP-B2` | `READY` | không đổi — chạy song song được, không phụ thuộc `WP-C2` |
| `WP-B3` | **`BLOCKED`** | **không đổi.** Dependency `WP-C2 DONE` vẫn CHƯA thoả — `WP-C2` mới `IMPLEMENTED`. Chỉ trở thành `READY` sau khi `WP-C2` `DONE` một cách canonical |
| `GATE-B` | **chưa mở** | đòi `WP-B1 ∧ WP-B2 ∧ WP-B3` đều `DONE`; hiện `WP-B2` `READY`, `WP-B3` `BLOCKED` |
| `T-07` | **NOT READY** | chờ `GATE-B` |
| `WP-C3` | `PLANNED` | phụ thuộc `WP-C2` `DONE` (tiêu thụ enum) — enum đã sẵn sàng về mặt kỹ thuật, nhưng vòng đời chưa đóng |
| `DEC-005` | `PENDING` | **không đổi** — vẫn chặn `T-08`. Phiên này KHÔNG đóng `DEC-005` |
| `T-08` | vẫn bị chặn | bởi `DEC-005` |

**Lịch sử KHÔNG đổi, không một chữ:** `T-06 = DONE`, V2.1.5 validation = `FAILED`, verdict =
`DO_NOT_BUILD`, `can_proceed_to_app = false`, tag `v2.1.5-official-T06`, evidence T-06.

---

## 24. Files Changed

**Production (1 file):**

- `src/eth_dca_os/engine.py` — +128 / −0

**Tài liệu & trạng thái dự án:**

- `docs/CONVENTIONS.md` — mục **#22** mới (bảy tiểu mục a–g)
- `docs/tasks/WP-C2-execution-state-machine.md` — vòng đời, Ready Gate, Subtasks, 8 khối
  evidence, Exit Criteria, Changed Files Registry
- `PROJECT/PROJECT_PROGRESS.md` — `Last Updated` + dòng roadmap `WP-C2`
- `PROJECT/LO_TRINH_DE_HIEU.md` — **sinh lại bằng generator**, không sửa tay
- `PROJECT/CAPABILITY_REGISTRY.md` — trạng thái `CAP-WEBAPP`
- `PROJECT/REVIEW_BUDGET_LEDGER.md` — §2.2 + §8 mới (budget không đổi)
- `PROJECT/HARDENING_BACKLOG.md` — `H-34`, `H-35`

**Test & công cụ đo (không phải production path — `PRODUCTION_PATHS.md` §2):**

- `tests/test_wp_c2_execution_state.py` — 33 test (447 dòng)
- `tests/wp_c2_scenarios.py` — kịch bản tất định + fingerprint hành vi trước WP-C2 (173 dòng)
- `tests/wp_c2_invariance_tool.py` — công cụ đo bất biến backtest (177 dòng)
- `tests/wp_c2_reachability_tool.py` — công cụ bằng chứng production reachability (145 dòng)

**Mới tạo trong `docs/`:**

- `docs/reviews/WP-C2-IMPLEMENTATION-REPORT.md` (file này)
- `docs/sessions/S024-wp-c2-execution-state.md`

**Không đụng:** `data/` (untracked, chủ dự án giữ có chủ ý), `webapp/`, `docs/spec/`,
`docs/adr/ADR-001-*`, `pyproject.toml`, `pyproject.lock`, nhánh khác, tag.

---

## 25. Commit / Push

- Commit bounded trên **đúng một nhánh**: `claude/wp-c2-execution-state-y4rraf`.
- **KHÔNG** merge `main`. **KHÔNG** push `main`. **KHÔNG** xoá nhánh nào. **KHÔNG** dọn dẹp gì.
- `data/` không được thêm, không stash, không clean.
Kết quả:

    commit  148f9011c0d4198aa942c5f85a57a164e652e722
            "WP-C2: đặt tên, hợp nhất và lưu vết Execution State (đóng F-006)"
    push    git push -u origin claude/wp-c2-execution-state-y4rraf  -> OK ([new branch])

Sau khi push, `branch_authority_check.sh` chạy lại cho **`BRANCH AUTHORITY: PASS`**
(`behind upstream = 0`, `ahead of default = 1`, `INTEGRATION_DECISION_REQUIRED=NO`,
worktree CLEAN) — xem §2.

Một commit phụ sau đó chỉ cập nhật §2/§25 của chính báo cáo này để ghi SHA và kết quả push
(diff production = 0).

---

## 26. Exact Next Action

**Một việc, dành cho chủ dự án:**

> Đọc báo cáo này (đặc biệt §14 — bất biến backtest, §17 — ma trận 8/8, §22 — thẩm quyền vòng
> đời), rồi ra **một** quyết định: đóng vòng đời `WP-C2: IMPLEMENTED → DONE`, ghi vào
> `PROJECT/PROJECT_DECISIONS.md` (mẫu: `DEC-034` của `WP-B1`).

Khi và chỉ khi `WP-C2` `DONE` một cách canonical, chuỗi downstream mới được đi tiếp:
`WP-B3: BLOCKED → READY` (rồi cần một phiên thực thi riêng) → cùng `WP-B2` `DONE` → `GATE-B` mở
→ `T-07`. `WP-C3` cũng chỉ mở sau đó.

Nếu chủ dự án muốn thêm một vòng **rà soát độc lập (E2)** trước khi đóng: đó là lựa chọn thêm,
KHÔNG phải điều kiện của Completion Gate đã đóng băng (§22). Nếu chọn, hãy nói rõ để một phiên
reviewer độc lập được mở — phiên này là phiên implementer.

**Không có việc nào khác đang chờ.** Không có blocker kỹ thuật. Không có test đỏ. Không có
khoản nợ nào phải trả trước.
