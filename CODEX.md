# CODEX.md — Agent Adapter (Codex / other AI coding agents)

## STOP — read `AGENTS.md` first

`AGENTS.md` at the repository root is the **canonical AI entry point**. This file is an
**ADAPTER**. It holds no independent governance authority, and it carries exactly the same
authority semantics as `CLAUDE.md` — neither adapter grants a permission the other lacks.

Read order:

1. `AGENTS.md`
2. `governance/v4/CORE/` in the authority order declared by `AGENTS.md` §1
3. `PROJECT/` (profile, capability registry, state, production paths, budget ledger,
   hardening backlog, decisions)
4. The current task file under `docs/tasks/`
5. Then execute the S000 procedure in `governance/core/00_SESSION_ORCHESTRATION.md`

## Adapter Constraints

As an adapter, this file and the agent reading it must NOT:

- become a second source of governance authority;
- derive rules of its own that are not in CORE or PROJECT;
- treat a session prompt as outranking an Owner Decision or canonical governance;
- create tasks;
- grant itself repair or review budget;
- duplicate the body of CORE or PROJECT governance here.

## Non-Negotiables Before Any Change

- Tier and Effort are **computed** (`governance/scripts/governance/routing_engine.py`),
  never chosen by intuition; `validate_routing.py` must PASS before execution.
- Completion Gates frozen on 2026-08-23 must not be deleted or weakened. Use a
  `COMPLETION GATE CHANGE PROPOSAL` per
  `governance/core/TASK_COMPLETION_GATE_STANDARD.md`.
- A finding is not a task. Route it per
  `governance/v4/CORE/REVIEW_PROTOCOL.md`; never invent a task ID.
- Budget does not reset. See `PROJECT/REVIEW_BUDGET_LEDGER.md`.
- `CONTINUE` is the default; only the five canonical hard-stops in
  `governance/v4/CORE/DELIVERY_LOOP.md` may stop delivery.
- Never invent evidence. If a check was not executed, its status is `NOT_TESTED`.

## Language Rule

All user-facing responses produced during every session must be written in Vietnamese.
All files whose purpose is to explain, summarize, report, or update project progress,
session progress, current status, completed work, remaining work, next steps, handoffs, or
other human-readable progress information must be written in Vietnamese.
Technical tokens that must remain unchanged for system correctness — including code,
terminal commands, variable names, enums, identifiers, file paths, filenames, schema
values, and IDs such as `READY`, `DONE`, `MAJOR`, `S000` — must remain unchanged when
translation could affect system behavior.

## Final Rule

The agent must prove completion through artifacts and evidence, not through narrative
confidence.
