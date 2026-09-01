# CORE — REVIEW PROTOCOL (V4.3)

Status: CANONICAL (V4.3 overlay)
Layer: CORE — project-agnostic.

## Principle

    REVIEW WIDE — REPAIR NARROW

A reviewer may be adversarial, may hunt edge cases, may probe security and integrity
weakness, and may review well beyond the diff. None of that grants the right to repair.

## Reviewer Obligations

1. Return **all** BLOCKING findings identifiable in a single review pass. Serialising
   blocking findings across sessions is a process failure, not thoroughness.
2. Classify every finding (see FINDING ROUTING below). An unclassified finding is an
   incomplete finding.
3. State evidence at the level actually achieved. Never assert an evidence level that was
   not executed.

## CONFIRMED vs PROVISIONAL

    CONFIRMED    runtime / production-path evidence with sufficient authority
    PROVISIONAL  diagnostic or theoretical finding whose production path is not proven

Only CONFIRMED findings are direct grounds for repair, unless an Owner Decision says
otherwise. Diagnostic and adversarial discovery does not by itself authorise a code change.

## Finding Routing

    BLOCKING

requires ALL THREE simultaneously:

- a current production path;
- a business consequence that sits inside a Completion Gate or the risk register;
- reproducible evidence.

Missing any one of the required canonical grounds: the finding must NOT default to
BLOCKING.

    HARDENING

- no current production path; or
- defense-in-depth; or
- future grammar; or
- a hypothetical/adversarial case not constructible from a valid production source.

Every HARDENING finding MUST carry:

    RE_TRIGGER_CONDITION

A hardening item without a re-trigger condition is an item that will be lost.

    OUT_OF_SCOPE

Route to the appropriate owner/capability. `OUT_OF_SCOPE` does **not** mean "new task".

    OWNER_ASSIGNMENT_REQUIRED

Used when there is a genuine ownership gap. Never invent a task ID to fill it.

## A Finding Is Not A Task

Reclassifying findings never produces tasks as a side effect:

- HARDENING -> Hardening Backlog, with re-trigger;
- OUT_OF_SCOPE -> routed to an owner/capability;
- ownership gap -> `OWNER_ASSIGNMENT_REQUIRED`;
- BLOCKING inside the current capability -> identify repair ownership and remaining
  capability budget, then stop. Opening the repair cycle is not automatic.

## Evidence

An independent review verdict is authoritative over the implementer's narrative. The
implementer may not dismiss a reviewer finding unilaterally. Completion is proven by
artifacts and evidence, never by narrative confidence.

---

## Before The Review Starts

Reconciled against the source pack on 2026-09-01. Six steps, in order, before reading
anything else:

1. lock the exact full SHA and the remote SHA;
2. run the branch authority check;
3. record the interpreter / tool versions the evidence will pin;
4. record the tracked worktree status;
5. read the Task Spec, Completion Gate, production paths, risk register and budget ledger;
6. determine the **cumulative repair diff** from the ledger.

Step 6 is what makes the same-cycle rule enforceable rather than a matter of opinion.

## The BLOCKING Test, Stated Negatively

    insufficient production path   -> not BLOCKING
    insufficient consequence       -> not BLOCKING
    only makes the evidence nicer  -> not BLOCKING
    inside the cumulative repair diff -> same cycle, not a new one

A finding inside the current cycle's cumulative repair diff is a defect of that same
repair. It does not open a new repair cycle and does not consume new budget.

## Verdict

    PASS  -> ELIGIBLE_FOR_FREEZE
    FAIL  -> NOT_ELIGIBLE_FOR_FREEZE

The verdict is advisory on state: the reviewer records it, and does not write `FROZEN`. A
reviewer does not modify the repository during an independent review without separate
delegation.
