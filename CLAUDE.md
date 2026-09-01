# CLAUDE.md — Agent Adapter (Claude Code)

## STOP — read `AGENTS.md` first

`AGENTS.md` at the repository root is the **canonical AI entry point**. This file is an
**ADAPTER**. It holds no independent governance authority.

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

Governance version in force: **AI Engineering V4.3 (overlay) over V3.2 base**.
See `docs/decisions/ADOPTION-V4_3-migration-record.md`.

## Compact Directory Layout

This package stores static governance under `governance/` to keep the repository root thin.

- `AGENTS.md` = canonical AI entry point at root.
- `CLAUDE.md` / `CODEX.md` = agent adapters at root.
- `PROJECT/` = current project state.
- `docs/` = runtime tasks, sessions, reviews, ADRs.
- `governance/` = static rules, templates, validators, references.
- `governance/v4/CORE/` = V4.3 CORE (project-agnostic).

Do not move governance files back to root.

## Core Principle

Do not code first and organize later.

The repository is the shared memory:
- V4.3 CORE rules → `governance/v4/CORE/`
- V3.2 base rules → `governance/core/`, `governance/product/`, `governance/audit/`
- Capabilities → `PROJECT/CAPABILITY_REGISTRY.md`
- Current state → `PROJECT/PROJECT_PROGRESS.md`
- Non-technical progress view → `PROJECT/LO_TRINH_DE_HIEU.md` (generated automatically)
- Project profile → `PROJECT/PROJECT_PROFILE.md`
- Production paths → `PROJECT/PRODUCTION_PATHS.md`
- Review/repair budget → `PROJECT/REVIEW_BUDGET_LEDGER.md`
- Hardening findings → `PROJECT/HARDENING_BACKLOG.md`
- Tactical decisions → `PROJECT/PROJECT_DECISIONS.md`
- Architecture decisions → `docs/adr/`
- Task definitions → `docs/tasks/`
- Session history/handoffs → `docs/sessions/`
- Reusable forms → `templates/`

## Task Lifecycle (V3.2 base, unchanged)

NOT_PLANNED
→ PLANNED
→ READY
→ IN_PROGRESS
→ IMPLEMENTED
→ VERIFYING
→ DONE

Alternative states:
BLOCKED / DEFERRED / CANCELLED

Task Modes MICRO / MAJOR / SPIKE remain as defined in
`governance/core/TASK_MODE_STANDARD.md`. Ready Gate, Completion Gate freeze, Evidence
levels, routing via `routing_engine.py` + `validate_routing.py`, escalation and roadmap
sync all remain in force — see `AGENTS.md` §4.

## Progress Questions

If the user asks about current progress, current step, remaining work, next step or a
checklist, READ `PROJECT/PROJECT_PROGRESS.md` FIRST.

Do not answer from conversational memory.

## Scope Expansion

Do not silently edit outside a task's Scope Lock.

If required:

SCOPE EXPANSION REQUIRED

Then reassess impact before continuing. Note the V4.3 constraint: a locked Scope Lock is
never by itself a sufficient reason to create a new task —
see `governance/v4/CORE/CAPABILITY_MODEL.md`.

## Conflict Rule

If documentation, implementation, data, security, or current behavior conflict:

CONFLICT DETECTED

Documentation:
...

Implementation:
...

Risk:
...

Recommended resolution:
...

Do not guess silently. Resolve genuine rule conflicts with
`governance/core/RULE_PRECEDENCE.md`.

## Language Rule

All user-facing responses produced during every session must be written in Vietnamese.
All files whose purpose is to explain, summarize, report, or update project progress, session progress, current status, completed work, remaining work, next steps, handoffs, or other human-readable progress information must be written in Vietnamese.
Technical tokens that must remain unchanged for system correctness — including code, terminal commands, variable names, enums, identifiers, file paths, filenames, schema values, and IDs such as `READY`, `DONE`, `MAJOR`, `S000`, `S001`, and `S002` — must remain unchanged when translation could affect system behavior.

## Governance File Index (pointers only — no rules live here)

Kept in this adapter purely for navigation. Authority lives in the files themselves and in
the order declared by `AGENTS.md` §1.

### V4.3 CORE
- `governance/v4/CORE/CAPABILITY_MODEL.md`
- `governance/v4/CORE/GOVERNANCE_V4.md`
- `governance/v4/CORE/DELIVERY_LOOP.md`
- `governance/v4/CORE/REVIEW_PROTOCOL.md`
- `governance/v4/CORE/RISK_MODEL.md`
- `governance/v4/CORE/PRODUCTION_PATH_RULE.md`
- `governance/v4/CORE/STATE_AUTHORITY.md`

### Session / Planning (V3.2 base)
- `governance/core/00_SESSION_ORCHESTRATION.md`
- `governance/core/PROJECT_PROFILE_STANDARD.md`
- `governance/core/TASK_MODE_STANDARD.md`
- `governance/core/TASK_READY_GATE_STANDARD.md`
- `governance/core/TASK_COMPLETION_GATE_STANDARD.md`
- `governance/core/PHASE_RELEASE_GATE_STANDARD.md`
- `governance/core/AGENT_CAPABILITY_MATRIX.md`
- `governance/core/ESCALATION_PROTOCOL.md`
- `governance/core/RULE_PRECEDENCE.md`
- `governance/core/EVIDENCE_STANDARD.md`
- `governance/core/ROADMAP_SYNC_STANDARD.md`

### Engineering
- `governance/core/01_PROJECT_ARCHITECTURE_RULES.md`
- `governance/core/02_ROUTING_RULES.md`
- `governance/core/03_DATA_MODEL_RULES.md`
- `governance/core/04_SECURITY_RULES.md`
- `governance/core/05_BUSINESS_LOGIC_RULES.md`
- `governance/core/06_DATABASE_API_RULES.md`
- `governance/core/07_CODING_RULES.md`
- `governance/core/08_CHANGE_MANAGEMENT_RULES.md`
- `governance/core/09_TESTING_RULES.md`
- `governance/core/10_AI_AGENT_EXECUTION_PROTOCOL.md`
- `governance/core/11_FORBIDDEN_ACTIONS.md`

### Product / Operations
- `governance/product/12_PRODUCT_REQUIREMENTS_RULES.md` … `governance/product/23_DOCUMENTATION_STANDARDS.md`
  (activation per `PROJECT/PROJECT_PROFILE.md` § Conditional Governance)

### Audit / Enforcement
- `governance/audit/DISCOVERY_BASELINE_TEMPLATE.md`
- `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`
- `governance/reference/OPTIONAL_ENFORCEMENT_LAYER.md`

## Roadmap Synchronization

`PROJECT/PROJECT_PROGRESS.md` is the only roadmap source of truth;
`PROJECT/LO_TRINH_DE_HIEU.md` is generated. Never edit the generated file by hand. After
any roadmap/status/Tier/Effort/dependency change, follow
`governance/core/ROADMAP_SYNC_STANDARD.md`; run routing validation before roadmap sync.

## Final Rule

The agent must prove completion through artifacts and evidence, not through narrative
confidence.
