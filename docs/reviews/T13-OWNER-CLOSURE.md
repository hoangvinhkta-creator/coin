# T-13 Owner Closure

Concise closure record. Full detail lives in the two reports it closes over — this file does
not restate their evidence, only the disposition.

## 1. Checkpoints

| Item | Value |
|---|---|
| Implementation checkpoint | `cb75d6c8ba64087b065d79a9ffbe351042a79b2a` |
| Reviewed checkpoint (independent E2) | `cb75d6c8ba64087b065d79a9ffbe351042a79b2a` (E2 evidence committed at `f56851fe41cf637a94f9cfbfad28b07cdc612346`) |
| `T13_MEASURE_BASE_SHA` | `5d26bcc4c24d80228720db5d43a52f904df60791` |
| Implementation report | `docs/reviews/T13-IMPLEMENTATION-REPORT.md` |
| Independent E2 report | `docs/reviews/T13-E2-INDEPENDENT-REVIEW.md` — `E2_VERDICT = PASS` |
| Owner Decision | `DEC-048` (`PROJECT/PROJECT_DECISIONS.md`) |
| Branch | `claude/t13-step-b-implementation-8wpnkr` |

## 2. Lifecycle Transition

    T-13: IMPLEMENTED -> DONE   (DEC-048, Owner-authorized Lifecycle Closure)

Completion Gate — **13/13 REQUIRED PASS**:

| Group | Checks | Evidence |
|---|---|---|
| E1-only (unchanged) | `CHECK-T13-01`, `-04`, `-08`, `-09`, `-11`, `-12` | E1, as implemented at S036 |
| E1 + independent E2 (upgraded) | `CHECK-T13-02`, `-03`, `-05`, `-06`, `-07`, `-10`, `-13` | E1 (implementer, kept) + E2 (independent reviewer, `T13-E2-INDEPENDENT-REVIEW.md` §5–§11/§25) |

No REQUIRED check text or semantics rewritten. No evidence downgraded. The independent E2
reviewer did not reuse the implementer's test assertions for the seven upgraded checks — it
built its own scenarios (notably a real-carry month, `carryIn = 14,000,000 ₫`, which the
implementer's own fixture never exercised) and reproduced all 12 AS scenarios and PR-1…PR-6
through the actual UI against `app_final.html` + the Firestore Emulator with real
`firestore.rules`.

## 3. HARDENING Findings (from independent E2)

Three findings, all `HARDENING`, 0 `BLOCKING`, routed to `PROJECT/HARDENING_BACKLOG.md`
`H-48`…`H-50` — findings, not tasks (`AGENTS.md` §3):

| ID | Backlog | Summary | `RE_TRIGGER_CONDITION` (see backlog for full text) |
|---|---|---|---|
| `F-T13-E2-01` | `H-48` | History renders a self-contradictory label `"Mua ETH (Bán)"` when a `TRADE side='SELL'` event is loaded via Settings → "Nạp lại từ JSON" — the form/menu SELL guard itself (`CHECK-T13-09`) is intact and correctly reachable-through-import only | `H-46` resolved and SELL UX opened; any UI path (besides import) becomes able to *create* a `SELL` event; `migrate()` starts producing `SELL`; a future gate widens SELL-guard scope to every display label |
| `F-T13-E2-02` | `H-49` | Legacy `T-09B` persistence executable evidence (six V2.1.5 test files, `CHECK-T09B-01`…`16`) is no longer runnable after the authorized removal of `#tab-setup`/`#seedFile`; `npm --prefix webapp test` now exits non-zero. Reviewer independently re-verified the underlying behavior (mirror-divergence guard, `CHECK-T09B-16`) still works correctly by direct testing on the Step-B UI — the gap is in re-runnable evidence, not behavior | persistence layer changed; Step C begins; `npm test` used as a release/CI gate; legacy evidence formally retired/replaced |
| `F-T13-E2-03` | `H-50` | "Định giá hiện tại" shows a date instead of price-age/freshness as spec §16.3 describes | PRICE UX becomes user-critical; stale-price warning/age semantics introduced; market-price display becomes part of real daily use |

None repaired in this closure session. None consumed repair budget.

A fourth reviewer item, `F-T13-E2-04`, is an **OBSERVATION** (not a HARDENING finding) about three
overstated claims in `docs/reviews/T13-IMPLEMENTATION-REPORT.md` (a spec line that does not exist;
a persistence-scenario count that does not match `test_t12_browser.js`; an AS-08 claim of carry
coverage the implementer's own fixture never exercised). Recorded here so a future session does
not re-cite those numbers; not routed to the hardening backlog because it names no production
path defect.

## 4. Real-Money SELL Guard

**`T-13 DONE` does NOT authorize real-money SELL usage.**

`H-46` (spec §6.3 vs §7.3 gap on SELL VND cost-basis creation/release, confirmed and unresolved
since `T-12`) is unchanged by this closure — `T-13` did not touch it and was not asked to.
`H-48` (the "Mua ETH (Bán)" label finding above) is a presentation issue reachable only through
manual JSON import, not a SELL-enablement change, and does not itself open real-money SELL. Both
must be dispositioned by the Owner before SELL becomes a real-money production workflow, before
realized P&L is implemented, or before sale accounting is exposed to Owner production data.

Also unchanged by this closure: `H-42` (Firebase isolation / durable auth — spec §24 step C)
and other product-readiness constraints (backup/rollback, `OWNER_LOCAL_ACCEPTANCE` §22.1 —
step D). `T-13 DONE` means the Step-B UX capability (dashboard, transaction entry, history,
edit/delete, plan/carry UX) passed its frozen contract. It does **not** mean the CoinDCA product
is ready for unrestricted real-money use.

## 5. Budget — Unchanged

    CAP-WEBAPP:  allowed = 2 · used = 1 · remaining = 1
    REPAIR_CYCLE_1 = CONSUMED (at 2a2ab3f, T-12, DEC-043) — unchanged by T-13's implementation,
    E2, or this closure.
    No second repair cycle used. No task ID created.

Production diff for the S036 implementation session, measured against `PRODUCTION_PATHS.md` §1
paths (`src/eth_dca_os webapp pyproject.toml pyproject.lock`): **3 files, +374/−1330**, under the
`+1800/−1400` ceiling. Production diff for the independent E2 session (`cb75d6c` → `f56851f`) and
for this closure session: **EMPTY** in both.

## 6. State Surfaces Updated

`docs/tasks/T-13-buoc-b-dashboard-giao-dich-lich-su.md` (Status → `DONE`; 7 E2-required checks →
`PASS (E1+E2)`; Exit Criteria complete) · `PROJECT/PROJECT_PROGRESS.md` (Last Updated, Current
Task Snapshot, roadmap row, Recent Decisions, Session History, Next Session) ·
`PROJECT/CAPABILITY_REGISTRY.md` §15.1 (appended) · `PROJECT/HARDENING_BACKLOG.md` `H-48`…`H-50`
(appended) · `PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.10 (appended) ·
`PROJECT/PROJECT_DECISIONS.md` `DEC-048` (appended) · `PROJECT/LO_TRINH_DE_HIEU.md` (regenerated
via `sync_easy_roadmap.py`, not hand-edited).

Validators run this session: `validate_routing.py` PASS · `validate_easy_roadmap.py` PASS ·
`validate_project_state.py` PASS · `validate_governance.py` PASS (50 hardening items counted) ·
`validate_structure.py` PASS · `branch_authority_check.sh` — `BRANCH AUTHORITY: PASS`, production
diff EMPTY. `validate_evidence.py` and `validate_task_completion.py` also report PASS but check
**0 records** (`H-08`: both glob `TASK-*.md`, which matches none of this project's
`T-*.md`/`WP-*.md` task files) — not treated as meaningful confirmation of anything in this
closure.

**Observed, not resolved here:** `branch_authority_check.sh` reports
`INTEGRATION_DECISION_REQUIRED=loc>5000` (cumulative branch divergence vs. `main`, driven by
review/governance documentation across the implementation + E2 + closure sessions — production
diff itself is EMPTY). Same category of observation as `T-12`'s own closure
(`T12-OWNER-CLOSURE.md` §6). This is an integration/merge-timing question, out of scope for this
closure and explicitly not actioned (`main` not touched, not merged). Recorded here for the
Owner to pick up separately.

## 7. Next Product Step

No task opened by this closure (`AGENTS.md` §3 — a finding is not a task, and neither is a
closure). Step C (`H-42` — Firebase isolation/durable auth) and Step D
(`OWNER_LOCAL_ACCEPTANCE`, real Owner data, outside this repo) remain open product-readiness
constraints, unchanged by this closure — opening either is an Owner decision, not an automatic
consequence of `T-13 DONE`. Before any step touches real-money SELL: `H-46` needs its own Owner
Decision, and `H-48` (the SELL-label finding) should be considered alongside it since both concern
SELL visibility, even though neither blocks this closure.
