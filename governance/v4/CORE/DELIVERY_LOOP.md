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
