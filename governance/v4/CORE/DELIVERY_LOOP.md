# CORE — DELIVERY LOOP (V4.3)

Status: CANONICAL (V4.3 overlay)
Layer: CORE — project-agnostic.

## Scope

This loop governs execution AFTER a piece of work has been confirmed as something that
must be done. It does not authorise starting work; `CAPABILITY_MODEL.md` does that.

## The Loop

    RUN
     -> DISCOVER BATCH
     -> FIX within authority
     -> TEST
     -> RERUN

`DISCOVER BATCH` means: collect everything the run reveals in one pass. Do not stop at the
first defect, fix it, and start a new session — that anti-pattern is what this loop exists
to eliminate:

    finding #1 -> STOP -> repair -> new session
    -> finding #2 -> STOP -> repair -> new session -> ...

## Default

    CONTINUE = REQUIRED

While authority, risk classification and budget still permit it, continuing is the
default, not a judgement call.

## The Five Canonical Hard-Stops

Delivery may stop for these reasons and no others:

    OWNER_DECISION_REQUIRED
    ARCHITECTURE_CHANGE_REQUIRED
    DATA_INTEGRITY_RISK
    CHANGE_BUDGET_EXCEEDED
    GOLDEN_PASS

## Not Hard-Stops

The following do NOT justify stopping while authority, risk and budget still allow work:

- a missing function;
- a missing parameter;
- a failing local test;
- a small piece of missing wiring;
- a newly encountered boundary;
- a small adapter that must be written;
- a finding that has just appeared.

Stopping for a reason outside the five:

    UNAUTHORIZED_STOP = PROCESS_FAILURE

## Change Budget

Two budgets run simultaneously and neither resets:

**A. Review / repair budget** — accrues to the capability **lineage root**.

**B. Delivery change budget** — cumulative production-path diff measured from the Golden
baseline.

Neither budget resets across session, branch, repair cycle, subtask, work package, child
task or sibling task. Budget must never be freed by creating a new unit of work.

Budget must be MEASURED, not summed by hand from reports:

    git diff --shortstat <GOLDEN_BASELINE_SHA>..HEAD -- <production paths>

If the project has no canonical Golden baseline with sufficient authority, record:

    PENDING_OWNER_DATA / MIGRATION_REQUIRED

Never select a convenient SHA and call it the Golden baseline.

## Golden Pass

`GOLDEN_PASS` is a valid stop only when the Golden is genuinely within the scope of the
work being executed. In an adoption or migration context, it is only meaningful if the
Golden is inside the adoption check scope.

---

# Part II — Reconciled Against The Source Pack (2026-09-01)

## II.1 The Unit Of Delivery Is An Outcome

Do not steer by which task is DONE, which finding is closed, or which session you are in.
Steer by:

    How far did one REAL business record travel, from input to a correct result?

    GOLDEN #1 — <a real record>
      real input -> ... -> <the expected final value, a concrete number>

## II.2 Discovery Runs In Batch — And Diagnostics Only Yield PROVISIONAL

Do not stop at the first boundary. If a boundary blocks the runtime from going further, a
diagnostic stub or bypass may be used to see underneath — but everything seen under a stub
is **PROVISIONAL**, not production evidence.

    B1 PASS
    B2 PASS
    B3 FAIL               <- CONFIRMED, the real runtime reached it
    B4 (after a stub at B3) <- PROVISIONAL
    B5 (after a stub at B3) <- PROVISIONAL

| | CONFIRMED | PROVISIONAL |
|---|---|---|
| Source | the real runtime reached it | stub / mock / bypass / manual injection |
| Counts toward X/N | yes | no |
| May be fixed in this session | yes | no |
| May be called a production blocker | yes | no |

**Discovery exists to map, not to grant repair rights.** A PROVISIONAL finding is promoted
to CONFIRMED only once the boundary above it passes on the real runtime and that runtime
genuinely reaches it — and the promotion must carry the real trace in that same session's
report. Never promote by inference.

## II.3 What Grants The Right To Fix

    <real entry> -> pipeline -> ... -> X -> FAIL     (REAL runtime, no stub)

With that trace, X may be fixed. Without it, X is not in the current vertical scope, however
much the architecture suggests it "will surely be needed". "The task spec asks for it" is
not grounds; only a real runtime trace is.

## II.4 Change Budget — Two Tiers

    SESSION_PRODUCTION_DIFF_MAX  = <N1> LOC   (per session)
    GOLDEN_CUMULATIVE_DIFF_MAX   = <N2> LOC   (the current Golden's whole lifetime)

The cumulative figure is counted from **one fixed baseline SHA**, accumulating across
session, branch, task, subtask, repair and review — it resets on no decomposition axis
whatsoever.

    GOLDEN_BASELINE_SHA = <full SHA of the day the Golden began>
    Cumulative = git diff --shortstat <baseline>..HEAD -- <production paths>

Measured by command, never summed by hand from previous reports. Exceeding the cumulative
figure is `CHANGE_BUDGET_EXCEEDED`. More budget is not granted by default: the Owner
revisits the Golden's scope rather than reflexively issuing new budget.

Risk is scored by data path, not by change size — see `RISK_MODEL.md`. HIGH does not
automatically STOP; it sets review depth. A mandatory batch review at end of session applies
to every change on a HIGH Blast Radius path, however small.

    MEDIUM changes <= 3    per session
    MEDIUM changes <= <N3> per Golden (cumulative, never reset)

The `<N>` values are PROJECT values and are declared in the project layer, not here.

## II.5 A Golden PASS Proves One Path

    GOLDEN #N PASS = ONE end-to-end path ran correctly.
    IT IS NOT:       capability DONE, or product DONE.

Every subsequent Golden must be **intentionally different** from the last (a different
source, quantity > 1, a non-zero discount, an identity that fails to resolve, ...).
Otherwise "Golden PASS" repeats the exact error of "199 tests pass so it must be DONE": a
narrow result used as broad evidence.

## II.6 Progress Counts Only CONFIRMED

    CONFIRMED PASS        = X
    KNOWN CONFIRMED TOTAL = N
    PROGRESS              = X / N

PROVISIONAL findings never count toward N. When a PROVISIONAL is promoted (§II.2), N may
**rise** — that is normal, not a regression. Every session reports both ends:

    BEFORE = X/N
    AFTER  = Y/N   (N may have risen if something was promoted)

If Y <= X with no rise in N and no promotion, the session must explain itself with one of
the five hard-stops. An unexplainable one is a process-failure signal.

## II.7 Minimal Fix — Declaring What Was Deliberately Left Undone

The `DEFERRED_BY_MINIMAL_FIX` block (see `CAPABILITY_MODEL.md`) is a voluntary declaration;
no machine can check that it is complete — it is the same class of claim as "guard respected
= YES". The one available mitigation: when a later Golden reaches a branch that was never
declared deferred, that is evidence the earlier declaration was deficient. Record it as a
finding about **declaration quality**, not about the code.

## II.8 Exception-First — Switched On Late, Never Early

### Why not from the start

In the Golden phase — few records, each chosen by the Owner to open one path — every finding
looks like `1/1`, and therefore looks exceptional even when it is not. Enabling
Exception-First too early turns it into a new STOP gate, contradicting the five hard-stops.

    Golden phase (cases the Owner deliberately chose to open the common path):
      EXCEPTION_CANDIDATE      = DISABLED
      FREQUENCY_CLASSIFICATION = DISABLED

    A CONFIRMED boundary on the Golden path MUST be fixed, unless it genuinely touches
    one of the five hard-stops. The agent may NOT ask "is this case rare?" in this phase.

### The three enabling conditions — all required

From a real evaluation batch (>= 50 records in the test set), a case may be proposed as
`EXCEPTION_CANDIDATE` only when simultaneously:

1. it has a **real** frequency from the batch (never inferred from a single case);
2. the fail-safe path has already placed the case into the project's official Review Queue,
   reusing the existing mechanism — no second queue — so no record is lost;
3. the estimated automation cost exceeds `<threshold>` LOC of production code.

Missing any one → `EXCEPTION_CANDIDATE = INVALID`. It may not be used to legitimise an
`OWNER_DECISION_REQUIRED`; the fix continues.

### Report per batch, never per case

    NOT:  case #7 -> STOP -> ask Owner -> continue -> case #18 -> STOP -> ...
    YES:  run the whole batch -> collect every valid candidate -> ONE report
          -> the Owner decides the whole set.

Each candidate carries: the case, the observed frequency, the impact, the current safe
behaviour (PENDING/manual), the automation cost, and a recommendation of AUTOMATE or
MANUAL_EXCEPTION.

### The invariant — no record is ever lost

    AUTO_RESULT + REVIEW_QUEUE_PENDING = 100% OF INPUT RECORDS

There is no `DROPPED`, `UNKNOWN` or `SILENTLY_IGNORED` state. An exception that cannot yet
enter the Review Queue is not yet a valid fail-safe, and no `EXCEPTION_CANDIDATE` is
accepted until condition 2 above holds.

### Phase state must be persisted

`EXCEPTION_FIRST` lives in the project state file, not in a session prompt. A phase-dependent
rule that exists only in conversation is lost between sessions.

    EXCEPTION_FIRST: DISABLED | ENABLED
    ENABLE_WHEN: batch >= <N> records run, Review Queue wired,
                 the three conditions above independently checkable

## II.9 Four Metrics — In This Order, Never Swapped

Measured only from batch validation, never from single Golden cases.

1. **`SILENT_ERROR_RATE`** = auto results that are wrong but undetected / auto results
   checked by hand. Target 0% on the hand-reconciled set. **This is the most important
   metric.** "195 right + 5 silently wrong" is far worse than "195 right + 5 pending", even
   though the automation rate looks identical.

2. **`ORDER_ACCOUNTING_RATE`** = (AUTO + REVIEW_QUEUE) / TOTAL INPUT. Target 100%. It answers
   one question: did any record disappear?

3. **`AUTOMATION_RATE`** = AUTO / TOTAL INPUT. Target >= 90%, directional only. This is a
   coverage proxy, **not** the deciding metric.

4. **`MANUAL_WORK_REDUCTION`** = 1 - NewManualHandlingTime / OldManualHandlingTime.
   Target >= 90%. This is the one that measures real business value.
   `OldManualHandlingTime` MUST be measured beforehand on real data (actually timing a real
   manual batch) and the number frozen before any comparison. A retrospective estimate made
   after automation always flatters the result and voids the metric.

   95% automation whose remaining 5% costs 150 minutes still yields poor Manual Work
   Reduction. A pretty dashboard is not value.

`SILENT_ERROR_RATE = 0%` means something only if the reconciled sample is large enough and
not biased toward easy cases. Fix in advance: how many records get hand-checked, and whether
they are chosen randomly or deliberately to be hard.

## II.10 Seven Laws

    1. The outcome is the unit of delivery.
    2. The real runtime grants the right to fix. No trace -> no fix.
    3. Discovery may look far ahead, but diagnostics only produce PROVISIONAL.
    4. CONTINUE is the default. Only five hard-stops may stop delivery.
    5. Budget accumulates against the Golden and never resets per session.
    6. A minimal fix must declare what it deliberately left undone.
    7. A Golden PASS proves one path, not a whole capability.
