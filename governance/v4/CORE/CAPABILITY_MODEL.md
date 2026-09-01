# CORE — CAPABILITY MODEL (V4.3)

Status: CANONICAL (V4.3 overlay)
Layer: CORE — project-agnostic. No project value, task ID, branch name or finding ID
belongs in this file. Project values live in `PROJECT/`.

## Purpose

Work is organised by **capability**, not by document. A capability is a slice of system
behaviour that can be accepted end to end by someone who does not read the code.

This model exists to stop three failure modes:

1. one technical finding spawning an unbounded chain of tasks, sessions and repair cycles;
2. review budget resetting every time a new unit of work is created;
3. delivery stalling because ownership of a small piece of work is not yet pretty.

## Definitions

**Capability** — a named, owned slice of system behaviour with a lineage root, a budget,
and a set of tasks that have implemented it over time.

**Lineage root** — the first task that established the capability. Budget accrues to the
lineage root, never to the individual task, session, branch or work package.

**Vertical Acceptance Slice** — the shortest end-to-end path that produces an outcome the
owner can accept. It crosses module boundaries by definition. A capability is not
delivered because its unit tests pass; it is delivered when the Vertical Acceptance Slice
runs correctly through it.

**Owner** — the task or capability accountable for a piece of work. Ownership is a
routing fact, not a formality: work without an owner is `OWNER_ASSIGNMENT_REQUIRED`,
never an invented task.

## Capability-First Question Order

Before proposing ANY new unit of work, answer in this order and stop at the first
question that resolves it:

1. Is it required for the current Vertical Acceptance Slice to run correctly?
2. Does it belong to a capability that already exists?
3. Which existing task/owner is nearest to owning it?
4. Would absorbing it into that owner exceed the Absorption Limit?
5. Only if 1–4 do not resolve it, put it to the Owner.

## Reasons That Are NEVER Sufficient To Create A New Task

- the current task has a locked Scope Lock;
- the work falls outside the current task's scope;
- ownership is not yet clear;
- adding the work would change the Scope Lock;
- a reviewer has just produced a new finding.

Each of these is a routing problem. None of them is a licence to mint an ID.

## Absorption Limit

Avoiding task proliferation must not create a mega-task. Absorption into an existing
owner is refused when ANY of the following is true:

| Threshold | Condition |
|---|---|
| A | Effective Risk rises by ≥ 1 level because of the absorbed work |
| B | More than 3 new items absorbed into an already-approved baseline task |
| C | REQUIRED checks in the Completion Gate increase by more than 50% |
| D | Work outside the Vertical Slice is being pulled onto the critical path |

On contact with any threshold, record:

    ABSORPTION_LIMIT_REACHED

and route to Owner Decision. Do NOT auto-create a task.

## Minimal Fix

A minimal fix — doing only what the current runtime / Golden needs — is permitted and is
often correct. It is permitted ONLY with an explicit declaration recorded in the owning
task or the capability ledger:

    DEFERRED_BY_MINIMAL_FIX
    Owner:
    Implemented:
    Intentionally deferred:
    Reason:
    Re-trigger:
    Evidence:

Do not create a new artifact to hold the deferred item. Do not convert the deferred item
into a task at the moment of deferral.

## Production Reachability

A capability's Completion Gate must cover:

    Correctness
    + Contract compliance
    + Regression safety
    + Production Reachability
    + Business acceptance

Production Reachability evidence must originate from an execution path OUTSIDE the
module/capability boundary. A large number of unit tests is not a substitute. If a Golden
trace already demonstrates reachability, do not build a separate per-module reachability
test.

---

# Part II — Reconciled Against The Source Pack (2026-09-01)

## II.1 Vertical Acceptance Slice — Mandatory Coordinates

`END_TO_END_ACCEPTANCE` must never be an abstract workflow description. It must carry
enough business coordinates to be checked **by hand**:

- the identity of a real record (ID, date, quantities, every input to the formula);
- the real entities involved (source code/name, the expected canonical identity);
- the real data source (vendor/source, the period it applies to, the reference record);
- the expected result: a **concrete number**, its unit, the resolution path, the
  provenance chain;
- the oracle: the business formula, the substituted values, the steps, the final number.

"Business-description level" means: no code, no test, no fixture, and it authorises no
downstream task. It does **not** mean abstract, and it does not mean without numbers.

The slice ends at the **capability's own output**. If the final business result is produced
by a consumer outside the boundary, stop at the output and compute the final result by hand
as the oracle. A capability must be able to prove itself without depending on a task
outside its boundary.

## II.2 When The Data Is Missing

Never invent business data. Record instead:

    END_TO_END_ACCEPTANCE = PENDING_OWNER_DATA
    MISSING_DATA:          <each field>
    REQUIRED_SOURCE:       where each missing value must come from
    OWNER_INPUT_REQUIRED:  exactly what the Owner must supply or confirm

Do not mark DEFINED / READY / COMPLETE without the coordinates and the expected number.
`PENDING_OWNER_DATA` plus a precise list of what is missing is a **valid** outcome, and is
usually worth more than a complete-looking but empty description.

## II.3 Acceptance Is The Seed Of The Golden, Not A Second Ground Truth

    END_TO_END_ACCEPTANCE -> a concrete business truth
                          -> a runnable Golden fixture/case
                          -> the Golden baseline strategy

Never build an acceptance framework parallel to the Golden. Until it is made executable,
the concrete case is *business* acceptance evidence, not executable Golden evidence.

## II.4 Creating A Sibling Task — Three Conditions, All Required

The reasons listed above as never sufficient are the negative test. This is the positive
one. A sibling task may be created only when **all three** hold:

1. **INDEPENDENT CAPABILITY** — it produces an independent output that is meaningful to a
   user or another system;
2. **INDEPENDENT LIFECYCLE** — it can be specced, built, tested, reviewed and shipped
   independently;
3. **OUTSIDE THE CURRENT CAPABILITY** — it lies outside the **capability** boundary, not
   merely outside one member task's boundary.

Condition 3 is judged against the capability. "Outside task X" does not satisfy it. Missing
any one condition → no sibling task.

An ownership gap **never** creates a task. Record it against the capability in the project
state file as `OWNER_ASSIGNMENT_REQUIRED`, noting the work, why ownership is unclear, the
candidate owners, the scope impact, the Effective Risk impact, whether it blocks, and a
recommendation. Do not create a separate artifact just to hold an ownership gap.

## II.5 What "Registered" Means

A task is **registered** in exactly two ways:

1. an entry in the official task-registry region of the project state file; or
2. a conforming Task Spec under `docs/tasks/`.

Mentioning a task ID in an analysis, a finding, a proposal, historical evidence or session
minutes is **not** registration. There is no naming exemption: every prefix, suffix and
namespace obeys the same rule.

On discovering a genuinely independent capability: **do not register a task.** Raise a
proposal for the Owner, using this repository's existing change-proposal mechanism
(`PROJECT/ROADMAP_CHANGE_PROPOSAL_*.md`). A proposal is not a task.

## II.6 Module Is Not Task

Architectural decomposition does not imply governance decomposition. The following exist by
default as a module, interface or work package — **not** as sibling tasks: resolver,
router, adapter, fallback selector, provenance mechanism, replay mechanism, persistence
helper, validation helper, audit helper, orchestration component, concurrency mechanism,
resolver stage.

Default representations: module | subtask | work package | hardening | finding | acceptance
criterion.

## II.7 Absorption — Prerequisite And Procedure

Automatic absorption is permitted **only** into a task that already has an Owner-approved or
frozen scope baseline, so that the change can be measured. A task without a baseline (not
yet authorised, no Scope Lock) absorbs nothing automatically; record
`OWNER_ASSIGNMENT_REQUIRED` with
`absorption_status = DEFERRED_UNTIL_<TASK_ID>_SCOPE_APPROVED`. Thresholds B and C are
measured from the **approved baseline**, never from an inferred scope.

When absorbing, all nine steps are mandatory: identify the nearest owner; write the
absorbed scope explicitly into the Task Spec; recompute Local Risk; recompute downstream
Blast Radius; recompute Effective Risk; assess the Completion Gate impact; assess the
review-depth impact; assess the repair-budget impact; check it against the vertical slice.

On `ABSORPTION_LIMIT_REACHED` the Owner chooses: **(A)** approve the widened scope and its
governance/risk consequences; **(B)** descope/defer to hardening or backlog; or **(C)**
approve a new task as an exception. C is never selected automatically, and a larger scope
does **not** automatically earn additional repair cycles.

Threshold D is a classification-dispute trigger. Work being outside the slice does not by
itself escalate — it routes to hardening/backlog as normal.

## II.8 Capability-Level Budget — Ledger Shape

```yaml
lineage_root: CAP-<NAME>
capability_repair_cycles_allowed: <N>      # an Owner governance decision
members: [<task>, <task>, ...]
consumed:
  - {task: <task>, cycle: RC-1, base_sha: <full 40>, head_sha: <full 40>}
capability_repair_cycles_used: <n>
capability_repair_cycles_remaining: <n>
migration_status: PROPOSED | ADOPTED | BLOCKED_PENDING_OWNER
```

`base_sha` / `head_sha` are what make the cumulative-repair-diff rule enforceable. Without
them, "inside or outside this cycle's diff" collapses back into opinion.

`capability_repair_cycles_allowed` is an **Owner governance decision**, not the sum of the
member tasks' cycles. Granting an arbitrarily larger pool reintroduces the split-for-budget
defect by another route.

**Migration.** When moving from a per-task ledger to capability lineage: reconstruct *every*
repair cycle already consumed with its base/head SHA; preserve history — no deletion, no
reset, no silent transfer; no task gains capacity merely because a sibling exists; and where
authority is missing, record `migration_status: BLOCKED_PENDING_OWNER` plus a change
proposal.

**Transition rule.** Until `migration_status = ADOPTED`, the existing per-task ledger
remains in force, and inside that window:

> No new task within the capability receives repair budget without its own Owner Decision —
> even when creating that task was itself approved.
>
>     task creation approval != repair-budget allocation approval

## II.9 Anti-Proliferation Is Measured, Not Asserted

Never self-certify "guard respected = YES". Measure on the **registry**, not by grepping the
whole repository:

    SET A = task IDs in the official registry region of the project state file
    SET B = task IDs holding a Task Spec under docs/tasks/

Compare BEFORE/AFTER for both sets, and additionally report `new_registered_task_ids`,
`proposals_created` (with names), and `owner_assignment_required_entries_added`.

Tool: `governance/scripts/governance/task_registry_snapshot.sh`.
