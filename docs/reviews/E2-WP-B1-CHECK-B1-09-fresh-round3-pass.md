# E2 INDEPENDENT REVIEW — WP-B1 / CHECK-B1-09 (vòng BA, sau bounded repair #2)

Review ID:
`E2-WP-B1-004-FRESH-ROUND3-2026-09-04`

Task / Release:
`WP-B1 — Chính sách verdict và stopping rule`, frozen REQUIRED check `CHECK-B1-09`
(Audit độc lập, Evidence Level **E2**).

Reviewer Session:
Phiên reviewer E2 MỚI, độc lập với phiên implementer `S023` và với hai reviewer trước
(`E2-WP-B1-002-FRESH`, `E2-WP-B1-003-FRESH-AFTER-REPAIR`). REVIEW-ONLY. Mọi nhãn PASS,
báo cáo implementer, tóm tắt test và kết luận reviewer trước đều được coi là **narrative
chưa tin được** cho tới khi tự tái lập trên production code.

Executed By:
Fresh Independent E2 Reviewer (Opus, effort High)

Timestamp:
2026-09-04

---

## Scope

Rà soát đúng HEAD `9ac01b8d3df19a68244b05f14a66f8a4ff9b90c0` (bounded repair #2): hai
blocker `E2-B1-F01`/`E2-B1-F02`, toàn bộ frozen `CHECK-B1-01/02/03/04/07/08/09/10`, F-017,
post-F-017 evidence, production reachability, sibling fail-open search và H-26.

KHÔNG repair production code. KHÔNG đổi threshold/strategy/spec. KHÔNG rerun official T-06.
KHÔNG rerun 1000 mô phỏng Control F/G. KHÔNG mở WP-B2/V2.2. KHÔNG merge `main`.

## Source Isolation

    source branch      = origin/claude/wp-b1-verdict-correctness-j9d390
    reviewed HEAD      = 9ac01b8d3df19a68244b05f14a66f8a4ff9b90c0
    expected prefix    = 9ac01b8                    -> KHỚP
    worktree           = detached, isolated, `git worktree add --detach` tại đúng SHA
    tracked worktree   = CLEAN (trước và sau review)
    production diff do chính lượt E2 này gây ra = **ZERO** (`git status --porcelain` rỗng;
                         `git diff -- src/` rỗng)
    Owner workspace    = KHÔNG checkout, KHÔNG chạm; `data/` untracked giữ nguyên
    môi trường         = Python 3.11.15, numpy 2.4.6, pandas 3.0.5, pytest 9.1.1
                         (ghim đúng `pyproject.lock`; drift transitive của `requests` là
                         artifact môi trường phiên, KHÔNG sửa file production nào)

## Inputs Read

`AGENTS.md`; `governance/v4/CORE/{STATE_AUTHORITY,REVIEW_PROTOCOL,PRODUCTION_PATH_RULE,
GOVERNANCE_V4,CAPABILITY_MODEL}.md`; `PROJECT/{PROJECT_PROGRESS,PROJECT_DECISIONS,
REVIEW_BUDGET_LEDGER,HARDENING_BACKLOG}.md`; `docs/CONVENTIONS.md`;
`docs/tasks/WP-B1-chinh-sach-verdict-va-stopping-rule.md`;
`docs/sessions/S023-*.md`; `docs/T06_OFFICIAL_EVIDENCE_RECORD.md`; hai artifact E2 FAIL
trước tại `docs/reviews/`; production: `failure_signals.py`, `verdict.py`, `pipeline.py`,
`benchmarks.py`, `gates.py`, `metrics.py`, `reporting.py`, `cli.py`, `data/dataset.py`.

## Yêu cầu FROZEN của `CHECK-B1-09` (tái lập độc lập)

> Phiên reviewer độc lập theo "Solo Independent Review Procedure", kiểm lại **đặc biệt**
> CHECK-B1-01, CHECK-B1-02 và CHECK-B1-07, coi mọi tuyên bố PASS của người cài đặt là
> narrative chưa tin được. Reviewer phải tự trả lời: *có đường nào để một verdict BUILD lọt
> qua khi bằng chứng chưa đủ không?* Lưu tại `docs/reviews/`.

Canonical interpretation **A** (giữ nguyên từ vòng E2 trước, không diễn giải lại cho hợp
với implementation): evidence REQUIRED non-official phải chặn **CẢ HAI** `verdict = BUILD`
**VÀ** `can_proceed_to_app = true`.

**Câu trả lời độc lập của lượt này cho câu hỏi frozen: KHÔNG.** Không tìm được đường
production-realistic nào để `BUILD` lọt qua khi bằng chứng REQUIRED thiếu, invalid,
non-official hoặc chưa phân giải được provenance.

## Independent Verification

| Check ID | Status | Evidence Level | Bằng chứng độc lập | Timestamp |
|---|---|---|---|---|
| CHECK-B1-01 | **PASS** | E2 | TRUE (`bool` + `numpy.bool_`), FALSE, UNKNOWN, all-UNKNOWN, TRUE+UNKNOWN precedence, gate-fail precedence, FS-08 thiếu/invalid/±inf — tất cả fail-closed. Mọi signal ra `bool` THUẦN Python. | 2026-09-04 |
| CHECK-B1-02 | **PASS** | E2 | Call graph: repair chỉ chạm `full.purchases → monthly_tranches → Control F/G → FS-08` và nhánh officiality. `engine.py`/`gates.py`/`score.py`/`regime.py`/`capital.py` KHÔNG đổi; `run_gate1` chỉ THÊM một dẫn xuất read-only từ `full` đã chạy sẵn — Gate 1 input/calculation/execution không đổi. **DEC-009 KHÔNG kích hoạt; không cần rerun Gate1/T-06.** | 2026-09-04 |
| CHECK-B1-03 | **PASS** | E2 | F-017 còn đúng: `monthly_tranches` dựng từ `full.purchases`, giữ NGUYÊN từng `nominal` (list, không sum), random hóa ĐỘC LẬP mỗi tranche; ngữ nghĩa F/G nguyên vẹn; repair #2 chỉ chạm xử lý evidence invalid/incomplete, không đổi kết quả replay hợp lệ. | 2026-09-04 |
| CHECK-B1-04 | **PASS** | E2 | Ngưỡng nguyên văn: FS-02 `>0.5`, FS-07 `>0.30 AND <102.0`, FS-12 `>0.80`. Exact boundary + one-ULP hai chiều đúng cả 11 ca. Không ngưỡng nào đổi trong hai repair. DEC-033 nguyên vẹn; không có tuyên bố tối ưu thực nghiệm; không có uỷ quyền tự động cho V2.2. | 2026-09-04 |
| CHECK-B1-07 | **PASS** | E2 | Bất biến stopping rule giữ được trên toàn bộ ma trận: thiếu F/G/cả hai, NaN, ±inf, kiểu không hợp lệ, `bool`/`numpy.bool_`, từng nguồn officiality false, nhiều nguồn, tất cả, provenance chưa phân giải. Cả `verdict` LẪN `can_proceed_to_app` đều fail-closed. | 2026-09-04 |
| CHECK-B1-08 | **PASS** | E2 | Replay historical qua CODE HIỆN TẠI cho đúng `DO_NOT_BUILD` / `["Gate 1 FAIL", "OOS hard condition FAIL"]` / `can_proceed_to_app=false`. Artifact lịch sử KHÔNG bị mutate (diff rỗng so `origin/main`); annotated tag `v2.1.5-official-T06` nguyên vẹn, peel đúng `5228130677e9…`. | 2026-09-04 |
| **CHECK-B1-09** | **PASS** | E2 | Lượt E2 độc lập này; xem toàn bộ artifact. | 2026-09-04 |
| CHECK-B1-10 | **PASS** | E2 | Full suite tự chạy: **461 collected / 461 passed / 0 failed / 0 error / 0 skipped / 0 xfailed / EXIT=0**, 1005.38s. | 2026-09-04 |

CHECK-B1-05 / CHECK-B1-06 nằm ngoài phạm vi bắt buộc của lượt này và không bị lượt này hạ.

## Findings — hai blocker lịch sử

### `E2-B1-F01` — **ĐÓNG** (CLOSED)

`_numeric_and_finite()` nay là `isinstance(x, numbers.Real)` + loại `bool` tường minh +
`math.isfinite(float(x))`. Probe độc lập trên chính hàm production:

- 19/19 giá trị INVALID → `False`: `None`, NaN, `±inf`, `np.nan`, `np.float64(±inf)`,
  chuỗi số `"10.0"`, chuỗi thường, object, `True`/`False`, **`numpy.bool_(True)`/
  `numpy.bool_(False)`**, list, dict, complex, `Decimal`.
- 8/8 giá trị VALID → `True`: `int`, `float`, `np.float64`, `np.float32`, `np.int64`,
  `Fraction`, `0.0`, số âm.
- Ma trận FS-08 theo TỪNG vị trí (`v2_eth`, F P95, G P95) × 19 ca invalid = **57/57 ca cho
  `FS-08 = None` (UNKNOWN)**, `cap_cause = "UNKNOWN"`, không ca nào thành FALSE/0/fallback.
- `numpy.bool_` bị loại vì KHÔNG phải instance của `numbers.Real` — **đã kiểm thực nghiệm**,
  không tin theo docstring.

Công thức đầu vào hợp lệ giữ nguyên: `beats_f = v2_eth > random_timing_p95`,
`beats_g = v2_eth > random_anchor_p95`, `FS-08 = not (beats_f and beats_g)`. So sánh `>`
NGHIÊM NGẶT, đúng chiều, không ngưỡng mới, không fallback (5/5 ca biên gồm hai ca hoà).

### `E2-B1-F02` — **ĐÓNG** (CLOSED)

`official` nay AND đủ **bốn** nguồn (Gate1, Gate2, Gate3, Controls, kèm `bool(controls)`).
Khi `not official` và verdict là `BUILD`, verdict bị **hạ nhãn** về `INCONCLUSIVE` đồng thời
`can_proceed_to_app=False`. Kiểm trên **năm biểu diễn** (in-memory, `backtest_runs.jsonl`,
`*_metrics.json`, `report.json`, `pipeline_state.json` qua `cli._strip`):

| Tổ hợp officiality | verdict (cả 5 biểu diễn) | can_proceed | Canonical A |
|---|---|---|---|
| cả bốn official | `BUILD` | `true` | PASS (positive control) |
| chỉ Gate1 false | `INCONCLUSIVE` | `false` | PASS |
| chỉ Gate2 false | `INCONCLUSIVE` | `false` | PASS |
| chỉ Gate3 false | `INCONCLUSIVE` | `false` | PASS |
| chỉ Controls false | `INCONCLUSIVE` | `false` | PASS |
| Gate1+Gate3 false | `INCONCLUSIVE` | `false` | PASS |
| Gate2+Controls false | `INCONCLUSIVE` | `false` | PASS |
| tất cả false | `INCONCLUSIVE` | `false` | PASS |
| controls vắng mặt | `BUILD_WITH_MODIFICATIONS` | `false` | PASS |
| provenance chưa phân giải + official | `ProvenanceUnresolvedError` | n/a | PASS fail-loud, **0 file được ghi** |

Không biểu diễn persist/report nào khôi phục lại `BUILD` sau guard.

## Ngữ nghĩa `INCONCLUSIVE`

- **Có sẵn trong từ vựng canonical**: `VERDICTS` và nhánh `INCONCLUSIVE` được giới thiệu tại
  commit gốc `a582ea5`. `src/eth_dca_os/verdict.py` **chưa từng bị sửa** kể từ đó
  (`git log -- src/eth_dca_os/verdict.py` chỉ có một commit) — nhãn này KHÔNG được phát minh
  để repair #2 pass.
- `can_proceed_to_app` chỉ được dựng ở đúng một chỗ (`verdict.py:37`, `v == "BUILD"`), nên
  `INCONCLUSIVE` ⇒ `false` theo cấu trúc, không phải theo quy ước.
- **Không consumer production nào** đọc `verdict`/`can_proceed_to_app` để cho phép tiến tiếp:
  grep toàn repo (trừ `tests/`, `docs/`) không có consumer nào ngoài chính `verdict.py`/
  `pipeline.py`. `webapp/`, `demo/` không đọc hai trường này.
- Không tạo đường tiến tương đương, không nới bất kỳ stopping rule nào (`INCONCLUSIVE` đã là
  nhãn của nhánh Gate 2/3 FAIL sẵn có, vốn cũng chặn tiến).

## Post-F-017 official evidence

Không rerun 1000 mô phỏng. Xác minh logic hiện tại trên đúng bộ số official:

    14.910758150139896 > 14.887400583487747  -> beats_f = true
    14.910758150139896 > 14.813546903782814  -> beats_g = true
    FS-08 = not (true and true)              -> false      (tái lập được)

Bounded repair #2 KHÔNG làm mất hiệu lực evidence này.

## Sibling Fail-Open Search (hẹp, đúng biên verdict)

Phạm vi: required failure-signal evidence → official eligibility → verdict →
`can_proceed_to_app` → persistence/reporting. **Không** mở sang module engine khác, UI,
security, WP-B2.

Bơm NaN/±inf/chuỗi TRỰC TIẾP vào payload `g1/g2/g3` cho thấy 9 vị trí non-FS-08 mà NaN sẽ
biến thành FALSE. Nhưng ba tiêu chí BLOCKING của V4.3 đòi **production path thật**, và kiểm
từng đường cho thấy **không đường nào tới được** `evaluate_failure_signals` ở dạng NaN:

- FS-02 / FS-03 / FS-07(`avg_cash_ratio`): đi qua `metrics.aggregate_over_windows()`, hàm
  này coi `None` **và** NaN là thiếu → trả `value=None` + `reason` → **UNKNOWN, fail-closed**
  (kiểm thực nghiệm: `float('nan')`, `None`, `np.float64('nan')` đều ra `None`).
  `run_gate1` còn đặt `concentration = None` khi có `reason`.
- FS-12 (`regime_advantage.share`): `_advantage_share()` trả `share=None` khi
  `positive_mass <= 0` → UNKNOWN.
- FS-01, FS-07(`gate1_primary_ae`), FS-09, FS-11: một NaN ở đây buộc chính gate tương ứng
  FAIL (`NaN >= 100` là `False`) → `DO_NOT_BUILD`/`INCONCLUSIVE`, **không bao giờ** `BUILD`
  (kiểm end-to-end qua `run_verdict`).
- FS-10 (`oos_pass_share_reported_separately`): là tỷ lệ đếm `count/n`, không thể là NaN.
- Chuỗi ở vị trí ngưỡng: `TypeError` trước verdict — fail-loud, không leak.

**Kết luận: không có sibling fail-open BLOCKING.** Ghi nhận HARDENING bên dưới.

## Production Reachability

| Case | Kịch bản | Kết quả tái lập |
|---|---|---|
| A | complete + finite + official + đủ điều kiện BUILD | `BUILD`, `can_proceed=true`, giữ `BUILD` ở cả 5 biểu diễn |
| B | FS-08 evidence invalid (NaN/±inf/str/bool) | `FS-08=UNKNOWN`, `cap_cause=UNKNOWN`, không leak BUILD |
| C | FS-08 evidence thiếu (F, G, hoặc cả hai) | `FS-08=UNKNOWN`, không leak BUILD |
| D | required evidence non-official (8 tổ hợp) | `verdict != BUILD`, `can_proceed=false` |
| E | provenance REQUIRED chưa phân giải | `ProvenanceUnresolvedError` TRƯỚC mọi lần ghi file — không payload BUILD nào thoát ra |
| F | biểu diễn persist/report | không khôi phục được `BUILD` sau guard |

Fixture tổng hợp CHỈ dùng làm bằng chứng CƠ CHẾ, **không** phải xác nhận tài chính.

## Test Evidence

Adversarial (probe review-only, độc lập với file regression của implementer) — báo cáo
TÁCH RIÊNG khỏi test suite:

    P1 finite/FS-08 ma trận      : 19 invalid + 8 valid + 57 ca theo vị trí + 5 ca biên  -> ALL PASS
    P2 officiality/persistence   : 1 positive control + 8 tổ hợp + 9 ca FS-08 × 5 biểu diễn -> ALL PASS
    P3 sibling injection         : 9 leak khi bơm thẳng  -> P4 chứng minh KHÔNG production-reachable
    P4 reachability guard        : aggregate_over_windows / _advantage_share / gate coupling -> ALL PASS
    P5 CHECK-B1-01 + B1-04       : 37 assertion (bool, numpy.bool_, precedence, ULP) -> ALL PASS
    P6 provenance                : fail-loud, 0 file ghi                 -> PASS
    P7 T-06 replay               : DO_NOT_BUILD + 2 reasons + false      -> PASS
    P8 H-26                      : latent, không fail-open hiện hành     -> xác nhận

18 counterexample mà vòng E2 trước chứng minh (±inf ba vị trí, bool-as-number, 7 tổ hợp
non-official phát nhãn BUILD) đã được **tái lập độc lập và đều bị giết** tại HEAD này.

Test suite:

    targeted WP-B1  : 127 collected / 127 passed / 0 failed / EXIT=0 (7.94s)
    full suite      : 461 collected / 461 passed / 0 failed / 0 error /
                      0 skipped / 0 xfailed / 0 deselected / EXIT=0 (1005.38s)

Không test nào bị skip, xfail, deselect hay nới lỏng trong lượt review này.

## H-26

Tái kiểm theo đúng ba tiêu chí BLOCKING của V4.3, KHÔNG promote chỉ vì `numpy.bool_` tồn
tại. Xác nhận `evaluate_oos(...)['pass']` vẫn là `numpy.bool_` (`x is True` → `False`),
nhưng consumer DUY NHẤT (`verdict.py:14`) đọc bằng **truthiness** (`if not gate1["pass"]`),
và ca FAIL vẫn cho đúng `DO_NOT_BUILD`. **Không có hậu quả nghiệp vụ ở hiện trạng** →
giữ **CONFIRMED HARDENING**, nằm ngoài repair critical của WP-B1.

## Findings mới

**BLOCKING: KHÔNG CÓ.**

**HARDENING (không chặn, không tạo task mới — ghi nhận theo §24 convergence):**

- `H-27 (đề xuất)` — `evaluate_failure_signals()` tự nó KHÔNG validate hữu hạn cho các input
  số ngoài FS-08; nó dựa vào caller (`aggregate_over_windows`/`_advantage_share`) đã lọc
  NaN. Hiện KHÔNG có đường production nào lách được lớp lọc đó (đã kiểm), nên đây là
  defense-in-depth, không phải fail-open. Cùng họ với H-26.
- `aggregate_over_windows()` lọc `None`/NaN nhưng KHÔNG lọc `±inf`. Không production-realistic
  ở hiện trạng (mọi window là 24 tháng, mẫu số ETH lớn và dương; ca suy biến đã được chặn
  bằng `ex_m_a > 0` → NaN → None), nên giữ mức HARDENING.

Theo `REVIEW_PROTOCOL.md`, không mục nào ở trên đạt đủ ba tiêu chí BLOCKING
(production path + hậu quả nghiệp vụ + evidence production-realistic tái lập được).

## Mismatches With Implementer Claims

Không có. Mọi tuyên bố kiểm được của repair #2 đều tái lập độc lập đúng. Một điểm được
**xác minh thực nghiệm chứ không chấp nhận theo docstring**: khẳng định `numpy.bool_` không
phải instance `numbers.Real` — đúng.

## Conclusion

    CHECK-B1-09                 = PASS
    WP-B1 REQUIRED PASS count   = 10/10
    Completion Gate             = THOẢ về mặt evidence
    E2 verdict (advisory)       = ELIGIBLE_FOR_FREEZE

## Required Follow-up

Theo `governance/v4/CORE/STATE_AUTHORITY.md`:

- Verdict của reviewer là **advisory**; reviewer KHÔNG viết `FROZEN`, KHÔNG viết `DONE`.
- `DONE` = **Owner, hoặc một completion authority được chỉ định**.
- `FROZEN` = phiên freeze có uỷ quyền tường minh.

Hành động tiếp theo thuộc Owner: ghi `CHECK-B1-09 = PASS` (E2, artifact này) vào
`docs/tasks/WP-B1-*.md`, cập nhật Exit Criteria 10/10, `PROJECT/PROJECT_PROGRESS.md` +
`REVIEW_BUDGET_LEDGER.md`, rồi quyết định đóng lifecycle WP-B1. Lượt review này KHÔNG sửa
production code, KHÔNG sửa state file, KHÔNG tiêu repair cycle.
