# T-14 Owner Closure

Concise closure record. Full detail lives in the two reports it closes over — this file does
not restate their evidence, only the disposition.

## 1. Checkpoints

| Item | Value |
|---|---|
| Implementation checkpoint | `3a6dc25` (`S039`) |
| Reviewed checkpoint (independent E2) | `8ad0f13` (E2 documentation commits `af8b70d` + `37c4a48`, `S040`) |
| `T14_MEASURE_BASE_SHA` | `97434d0ff9eecf1bf70fa167fe362f8d972885ce` (`origin/main`) |
| Implementation report | `docs/reviews/T14-IMPLEMENTATION-REPORT.md` |
| Independent E2 report | `docs/reviews/T14-E2-INDEPENDENT-REVIEW.md` — `E2_VERDICT = PASS` |
| Owner Decision | `DEC-050` (`PROJECT/PROJECT_DECISIONS.md`) |
| Branch | `claude/t14-step-c-firebase-isolation-xu6nxb` |

## 2. Lifecycle Transition

    T-14: IMPLEMENTED -> DONE   (DEC-050, Owner-authorized Lifecycle Closure)

Completion Gate — **12/12 REQUIRED PASS**, all twelve upgraded from `PASS (E1; E2 độc lập chưa
chạy)` to `PASS (E1 + E2 độc lập)`:

| Group | Checks | Evidence |
|---|---|---|
| E1 (implementer, `S039`) + independent E2 (`S040`) | `CHECK-T14-01` … `CHECK-T14-12` (all 12) | E1 (implementer, kept) + E2 (independent reviewer, `T14-E2-INDEPENDENT-REVIEW.md` §5) |

No REQUIRED check text or semantics rewritten. No evidence downgraded. The independent E2
reviewer did not reuse the implementer's test assertions — it wrote 37 of its own (a 20-line
authorization matrix with reviewer-chosen identities, and 17 restore/derive semantics assertions
against a reviewer-built synthetic ledger), and independently re-ran `npm --prefix webapp test`
(exit 0) in its own environment against a fresh `npm ci` install and freshly built
`app_final.html`. 14/14 `C-AS` scenarios reproduced with reviewer-controlled state/actions.

## 3. HARDENING Findings (from independent E2)

Three findings from independent E2, all `HARDENING`, 0 `BLOCKING`, routed to
`PROJECT/HARDENING_BACKLOG.md` — findings, not tasks (`AGENTS.md` §3):

| ID | Backlog | Summary | Disposition at closure |
|---|---|---|---|
| `F-T14-E2-01` | `H-49` | The legacy V2.1.5 test failure signature recorded in `H-49` ("timeout at `#seedFile`") is stale on the current HEAD — the app now starts in `SIGNED_OUT`, so the retired suite fails earlier, at the auth step | Description corrected in `H-49`; **CLOSED** as a consequence of `T-14 DONE` |
| `F-T14-E2-02` | `H-51` | `PROJECT_PATHS.md` §1/§2 does not classify `firestore.rules`/`firebase.json` — confirmed independently as real but not affecting `T-14` evidence correctness | **Confirmed, kept HARDENING** — not resolved, not rewritten |
| `F-T14-E2-03` | `H-53` (new) | CoinDCA Owner can read Content's `users/*` — reviewer confirmed by experiment this is a pre-existing property of the shared project (the pre-`T-14` Anonymous identity had the exact same read access), not a `T-14` regression | New backlog entry, **HARDENING (observation, not a regression)** |

None repaired in this closure session. None consumed repair budget.

## 4. Real-Money Guards

**`T-14 DONE` does NOT authorize unrestricted real-money use, and does NOT authorize SELL.**

`H-41` ("stop using the app with unlimited real money") remains **ACTIVE** — `T-14 DONE` closes
the Firebase isolation / durable auth / backup-recovery product-readiness gap that step C was
scoped to close (spec §18/§24), nothing more. `H-46` (SELL VND cost-basis spec gap, confirmed and
unresolved since `T-12`) is unchanged by this closure — `T-14` did not touch it and was not asked
to. Step D (`OWNER_LOCAL_ACCEPTANCE`, spec §22.1) remains **CLOSED** (not opened) — it is only
meaningful after the Owner completes the real-world setup in §7, and opening it is a separate
Owner decision, not an automatic consequence of this closure.

## 5. `H-42` Disposition

The REQUIRED portion of `H-42` (`FB-2`, `FB-4`, backup/recovery, executable persistence evidence)
is **CLOSED** as a direct consequence of `T-14 DONE`, confirmed independently by E2. Two items
remain **HARDENING, not closed**, both requiring an Owner-executed action outside this repo:

- `FB-3` (placeholder `OWNER_UID_REQUIRED`) — cannot self-close in-repo; the real UID is an
  Owner-deploy-time value. The 3-step runbook is a mitigation (catches the mistake before it
  locks the Owner out), not a closure.
- `FB-1` (Anonymous Auth still enabled, opening Content to unauthenticated writers) — provider
  disable is an Owner Console action; requires the Owner to first confirm Content does not
  depend on Anonymous Auth.

The original **DEFERRED** portion of `H-42` (a dedicated Firebase project for CoinDCA) is
untouched by this closure and remains HARDENING with no owner, per `DEC-049` A.

## 6. `H-49` Closure

**CLOSED.** `CHECK-T14-11` PASS at E1+E2: reviewer independently re-ran
`npm --prefix webapp test` (exit 0) in its own environment; the six retired V2.1.5 files are
byte-identical to base (not edited to force green); `test:legacy-v215` is correctly separated
from the active release gate; no blanket skip/deselect hides any still-relevant behavior. The
stale failure-signature description (`F-T14-E2-01`) has been corrected in the backlog entry.

## 7. Real-World Owner Setup Still Required

**This closure session did not perform live deployment and does not authorize it.** Before real
use, the Owner still must, outside this repo:

1. Replace `OWNER_UID_REQUIRED` in `firestore.rules` with the real Google account UID (copied
   from the app's UID-copy button).
2. Run `firebase target:apply hosting coindca <site-id-coindca>` once.
3. Deploy following the documented 3-step runbook exactly
   (`npm --prefix webapp run test:rules-merge` → read the `firestore.rules` diff by eye → deploy
   only after both pass) — never a bare `firebase deploy`.
4. Manually confirm a real Google Sign-In once, in a real browser with outbound internet access
   (this is the one chain of evidence the sandbox genuinely cannot produce — see `H-52`). Success
   here is the trigger condition that lets `H-52` close.

Skipping step 1 before a rules deploy will **lock the Owner out** (fail-closed, recoverable by
redeploying) — the E2 report verified this by experiment (§10 of the E2 report).

## 8. Integration Decision — `INTEGRATION_DECISION_REQUIRED: loc>5000`

`branch_authority_check.sh` reports:

    behind upstream   = 0
    ahead of default  = 4 commit(s)
    divergence LOC    = 5291
    INTEGRATION_DECISION_REQUIRED: loc>5000
    tracked worktree  = CLEAN (before this closure's edits) / DIRTY (index of this closure)
    production diff   = EMPTY
    BRANCH AUTHORITY: PASS

**Owner decision: ACCEPT INTEGRATION / MERGE** (`DEC-050` §E). The threshold is exceeded
primarily by review/evidence/governance artifacts accumulated across `S039` (implementation
report + evidence log), `S040` (E2 report + evidence log), and this closure's own state updates —
not by product code: `T-14`'s implementation production diff remains `194/−23` on 4 files, inside
the frozen `+600/−400` ceiling, and E2 + closure production diff is EMPTY in both. Independent
E2 = PASS, 0 unresolved BLOCKING finding, no semantic divergence requiring redesign was found.

**This decision is recorded, not executed.** No `git merge` into `main` was performed in this or
any prior session. Merging the branch is a separate integration action, decoupled from closing
the task lifecycle — consistent with `STATE_AUTHORITY.md` (closing a task ≠ merging a branch) and
with the explicit instruction not to merge `main` in this session.

## 9. Budget — Unchanged

    CAP-WEBAPP:  allowed = 2 · used = 1 · remaining = 1
    REPAIR_CYCLE_1 = CONSUMED (at 2a2ab3f, T-12, DEC-043) — unchanged by T-14's implementation,
    E2, or this closure.
    No second repair cycle used. No task ID created.

Production diff for the `S039` implementation session, measured against `PRODUCTION_PATHS.md`
§1 paths: **4 files, +194/−23**, under the `+600/−400` ceiling. Production diff for the
independent E2 session (`8ad0f13` → `af8b70d`/`37c4a48`) and for this closure session: **EMPTY**
in both.

## 10. State Surfaces Updated

`docs/tasks/T-14-buoc-c-firebase-isolation-auth-backup.md` (Status → `DONE`; 12 checks →
`PASS (E1+E2)`; Exit Criteria complete — `H-49` CLOSED, `H-42` REQUIRED portion CLOSED) ·
`PROJECT/PROJECT_PROGRESS.md` (Last Updated, Current Task Snapshot, roadmap row, Recent
Decisions, Session History `S040`+`S041`, Next Session) · `PROJECT/CAPABILITY_REGISTRY.md`
§17.1 (appended) · `PROJECT/HARDENING_BACKLOG.md` (`H-42` REQUIRED-portion closure, `H-49`
closed + description corrected, `H-51`/`H-52` confirmation notes, `H-53` new) ·
`PROJECT/REVIEW_BUDGET_LEDGER.md` §2.2.13 (appended) · `PROJECT/PROJECT_DECISIONS.md` `DEC-050`
(appended) · `PROJECT/LO_TRINH_DE_HIEU.md` (regenerated via `sync_easy_roadmap.py`, not
hand-edited).

Validators run this session: `validate_routing.py` PASS (22 MAJOR task files, 0 manual
overrides) · `validate_easy_roadmap.py` PASS · `validate_project_state.py` PASS ·
`validate_governance.py` PASS (53 hardening items counted, up from 52) · `validate_structure.py`
PASS (27 required paths) · `branch_authority_check.sh` — `BRANCH AUTHORITY: PASS`, production
diff EMPTY.

**Observed, not resolved here:** `branch_authority_check.sh` reports
`INTEGRATION_DECISION_REQUIRED=loc>5000` (cumulative branch divergence vs. `main`, driven by
review/governance documentation across the implementation + E2 + closure sessions — production
diff itself is EMPTY). Same category of observation as `T-12`'s and `T-13`'s own closures
(`T12-OWNER-CLOSURE.md` §6, `T13-OWNER-CLOSURE.md` §6). Unlike those two prior closures, this one
carries an explicit Owner decision on it: **ACCEPT INTEGRATION/MERGE**, recorded at `DEC-050`
§E — but, per this session's explicit instruction, not executed (no merge into `main` in this
session).

## 11. Next Product Step

No task opened by this closure (`AGENTS.md` §3 — a finding is not a task, and neither is a
closure). Step D (`OWNER_LOCAL_ACCEPTANCE`, real Owner data, outside this repo) is the next
product-readiness step, but it remains closed — opening it is an Owner decision that only makes
sense after the Owner completes the real-world setup in §7 (real UID deployed, rules deployed via
the runbook, a real Google Sign-In manually confirmed). This closure does not open it
automatically. Before any step touches real-money SELL: `H-46` needs its own Owner Decision.
