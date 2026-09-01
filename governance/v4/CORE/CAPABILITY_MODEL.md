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
