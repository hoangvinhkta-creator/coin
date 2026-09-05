# T-12 Owner Closure

Concise closure record. Full detail lives in the two reports it closes over — this file does
not restate their evidence, only the disposition.

## 1. Checkpoints

| Item | Value |
|---|---|
| Implementation/repair checkpoint | `2a2ab3f52c38eb30a0a8e0ee1791a95254ee9847` |
| Reviewed checkpoint (independent E2) | `0cf24cad98e342a9070168d321461772ea0021e4` |
| `T12_GOLDEN_ACCOUNTING_BASELINE` | `c610a299ed6b66dea3cd63372a0943967c93e95d` — unchanged throughout E2 and this closure |
| Implementation report | `docs/reviews/T12-IMPLEMENTATION-REPORT.md` |
| Independent E2 report | `docs/reviews/T12-E2-INDEPENDENT-REVIEW.md` — `E2_VERDICT = PASS` |
| Owner Decision | `DEC-046` (`PROJECT/PROJECT_DECISIONS.md`) |
| Branch | `codex/t12-l1-ledger-impl` |

## 2. Lifecycle Transition

    T-12: IMPLEMENTED -> DONE   (DEC-046, Owner-authorized Lifecycle Closure)

Completion Gate — **14/14 REQUIRED PASS**:

| Group | Checks | Evidence |
|---|---|---|
| E1-only (unchanged) | `CHECK-T12-01`, `-07`, `-08`, `-13`, `-14` | E1, as implemented at S034 |
| E1 + independent E2 (upgraded) | `CHECK-T12-02`, `-03`, `-04`, `-05`, `-06`, `-09`, `-10`, `-11`, `-12` | E1 (implementer, kept) + E2 (independent reviewer, `T12-E2-INDEPENDENT-REVIEW.md` §5–§13/§24) |

No REQUIRED check text or semantics rewritten. No evidence downgraded.

## 3. HARDENING Findings (from independent E2)

Four findings, all `HARDENING`, 0 `BLOCKING`, routed to `PROJECT/HARDENING_BACKLOG.md`
`H-44`…`H-47` — findings, not tasks (`AGENTS.md` §3):

| ID | Backlog | Summary | `RE_TRIGGER_CONDITION` (see backlog for full text) |
|---|---|---|---|
| `F-E2-01` | `H-44` | Sorting lock `(businessDate, seq)` is exercised by `test_t12_browser.js`; unit suite alone does not distinguish it | ordering logic changes; browser harness removed/rewritten; a future capability depends on deterministic ordering |
| `F-E2-02` | `H-45` | `UNKNOWN_VND_BASIS` flag disappears once a fully-UNKNOWN pool drains to zero | historical/audit visibility of prior UNKNOWN required; transaction UI exposes basis provenance; audit semantics require persistent warning |
| `F-E2-03` | `H-46` | **SELL VND cost-basis creation/release semantics are under-specified** — a specification gap, not a `T-12` implementation defect | **must retrigger BEFORE** enabling real-money SELL; before implementing realized P&L; before exposing sale accounting to Owner production data |
| `F-E2-04` | `H-47` | `ROUND_VND` on a negative numerator rounds away from zero, not half-up | negative monetary numerator becomes production-reachable; refund/reversal/signed accounting introduced; `ROUND_VND` generalized |

None repaired in this closure session. None consumed repair budget.

## 4. Real-Money SELL Guard

**`T-12 DONE` does NOT authorize real-money SELL usage.**

`F-E2-03` / `H-46` is a specification gap in spec §6.3 vs §7.3 (VND cost-basis
creation/release on SELL), confirmed present in the approved spec and correctly implemented
as specified — not a `T-12` code defect, and not this task's to fix. It must be resolved by a
separate Owner Decision **before** SELL becomes a real-money production workflow, before
realized P&L is implemented, or before sale accounting is exposed to Owner production data.

Also unchanged by this closure: `H-42` (Firebase isolation / durable auth — spec §24 step C)
and other product-readiness constraints (backup/rollback, `OWNER_LOCAL_ACCEPTANCE` §22.1 —
step D). `T-12 DONE` means the Step-A ledger capability (`openingPosition + events -> derive()`)
passed its frozen contract. It does **not** mean the CoinDCA product is ready for unrestricted
real-money use.

## 5. Budget — Unchanged

    CAP-WEBAPP:  allowed = 2 · used = 1 · remaining = 1
    REPAIR_CYCLE_1 = CONSUMED (at 2a2ab3f, DEC-043) — unchanged by E2 or this closure.
    No second repair cycle used. No task ID created.

Production diff for the independent E2 session and for this closure session, measured against
`PRODUCTION_PATHS.md` §1 paths (`src/eth_dca_os webapp pyproject.toml pyproject.lock`):
**EMPTY** in both.

## 6. State Surfaces Updated

`docs/tasks/T-12-so-cai-l1-v2-va-derive.md` (Status → `DONE`; 9 checks → `PASS`/`E2`; Exit
Criteria 14/14) · `PROJECT/PROJECT_PROGRESS.md` (Last Updated, Current Task, Current Task
Snapshot, roadmap row) · `PROJECT/CAPABILITY_REGISTRY.md` §14 · `PROJECT/HARDENING_BACKLOG.md`
`H-44`…`H-47` · `PROJECT/REVIEW_BUDGET_LEDGER.md` · `PROJECT/PROJECT_DECISIONS.md` `DEC-046` ·
`PROJECT/LO_TRINH_DE_HIEU.md` (regenerated via `sync_easy_roadmap.py`, not hand-edited).

Validators run this session: `validate_routing.py` PASS · `validate_easy_roadmap.py` PASS ·
`validate_project_state.py` PASS · `validate_governance.py` PASS (47 hardening items counted) ·
`validate_structure.py` PASS · `branch_authority_check.sh` — `BRANCH AUTHORITY: PASS`,
production diff EMPTY. `validate_evidence.py` and `validate_task_completion.py` also report
PASS but check **0 records** (`H-08`: both glob `TASK-*.md`, which matches none of this
project's `T-*.md`/`WP-*.md` task files) — not treated as meaningful confirmation of anything
in this closure.

**Observed, not resolved here:** `branch_authority_check.sh` reports
`INTEGRATION_DECISION_REQUIRED=loc>5000` (cumulative branch divergence vs. `main`, driven by
review documentation — production diff itself is EMPTY). This is an integration/merge-timing
question, out of scope for this closure and explicitly not actioned (`main` not touched, not
merged). Recorded in `DEC-046` item (6) for the Owner to pick up separately.

## 7. Next Product Step

No task opened by this closure (`AGENTS.md` §3 — a finding is not a task, and neither is a
closure). Step B (dashboard/UX, spec-l1 §24) is an Owner decision, not an automatic consequence
of `T-12 DONE`. Before any step touches real-money SELL: `H-46`/`F-E2-03` needs its own Owner
Decision. Steps C (`H-42` — Firebase isolation/durable auth) and D (`OWNER_LOCAL_ACCEPTANCE`,
real Owner data, outside this repo) remain open product-readiness constraints, unchanged by
this closure.
