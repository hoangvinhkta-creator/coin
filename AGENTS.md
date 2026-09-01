# AGENTS.md — Canonical AI Entry Point

**Every AI agent, reviewer and new session reads THIS FILE FIRST.**

`CLAUDE.md` and `CODEX.md` are adapters. They are read *after* this file and hold no
independent governance authority.

Governance version: **AI Engineering V4.3 (overlay) on top of V3.2 base governance**
Adopted: 2026-09-01 — see `docs/decisions/ADOPTION-V4_3-migration-record.md`

---

## 1. Authority Order

Read in this order. Lower numbers win on conflict.

| # | Authority | Canonical file in THIS repo |
|---|---|---|
| 1 | CORE — Capability Model | `governance/v4/CORE/CAPABILITY_MODEL.md` |
| 2 | CORE — Governance V4.3 | `governance/v4/CORE/GOVERNANCE_V4.md` |
| 3 | CORE — Delivery Loop | `governance/v4/CORE/DELIVERY_LOOP.md` |
| 4 | CORE — Review Protocol | `governance/v4/CORE/REVIEW_PROTOCOL.md` |
| 5 | CORE — Risk Model | `governance/v4/CORE/RISK_MODEL.md` |
| 6 | CORE — Production Path Rule | `governance/v4/CORE/PRODUCTION_PATH_RULE.md` |
| 6b | CORE — State Authority | `governance/v4/CORE/STATE_AUTHORITY.md` — binding across rows 1–6; it says which file holds which state, so it is read alongside CORE rather than ranked against it |
| 7 | PROJECT profile / capability / state | `PROJECT/PROJECT_PROFILE.md`, `PROJECT/CAPABILITY_REGISTRY.md`, `PROJECT/PROJECT_PROGRESS.md` |
| 8 | Production paths | `PROJECT/PRODUCTION_PATHS.md` |
| 9 | Risk register | `PROJECT/PROJECT_PROGRESS.md` § Active Risks |
| 10 | Completion gates | `docs/tasks/*.md` (FROZEN 2026-08-23) |
| 11 | Review budget ledger | `PROJECT/REVIEW_BUDGET_LEDGER.md` |
| 12 | Project decisions | `PROJECT/PROJECT_DECISIONS.md` |
| 13 | Current task / spec | `docs/tasks/`, `docs/spec/` |

An **Owner Decision** in `PROJECT/PROJECT_DECISIONS.md` outranks any session prompt.
A session prompt NEVER outranks canonical governance.

Also in force (V3.2 base, unchanged by this overlay): `governance/core/*`,
`governance/product/*`, `governance/audit/*` as selected by `PROJECT/PROJECT_PROFILE.md`.
Where V4.3 and the V3.2 base differ, see §4.

---

## 2. CORE / PROJECT Boundary

`governance/v4/CORE/` is **project-agnostic**. It contains no task ID, no branch name, no
finding ID, no symbol name, no exchange name, no strategy concept. Anything specific to
this repository lives in `PROJECT/` or in task artifacts under `docs/`.

Do not add project values to CORE. Do not restate CORE rules inside PROJECT files.

---

## 3. V4.3 Rules An Agent Must Not Get Wrong

**A finding is not a task.** Reclassification never mints an ID. See
`governance/v4/CORE/REVIEW_PROTOCOL.md` § Finding Routing.

**BLOCKING requires all three:** a current production path, a business consequence inside
a Completion Gate or the risk register, and reproducible evidence. Otherwise the default
is HARDENING with a `RE_TRIGGER_CONDITION`.

**Budget does not reset.** Not across session, branch, repair cycle, subtask, work
package, child task or sibling task. See `PROJECT/REVIEW_BUDGET_LEDGER.md`.

**CONTINUE is the default.** Only five hard-stops are valid:
`OWNER_DECISION_REQUIRED`, `ARCHITECTURE_CHANGE_REQUIRED`, `DATA_INTEGRITY_RISK`,
`CHANGE_BUDGET_EXCEEDED`, `GOLDEN_PASS`. Anything else is `UNAUTHORIZED_STOP`.

**Capability first.** Before proposing new work, run the five-question order in
`governance/v4/CORE/CAPABILITY_MODEL.md`. A locked Scope Lock, unclear ownership, or a
fresh reviewer finding are never sufficient reasons to create a task.

**Absorption has a limit.** Four thresholds; on contact record
`ABSORPTION_LIMIT_REACHED` and go to Owner Decision — do not auto-create a task.

---

## 4. Legacy Compatibility (V3.2 base remains in force)

This is an **overlay**, not a rewrite. The V3.2 mechanisms below are unchanged and still
binding:

- S000 session orchestration procedure — `governance/core/00_SESSION_ORCHESTRATION.md`
- Task Modes MICRO / MAJOR / SPIKE — `governance/core/TASK_MODE_STANDARD.md`
- Task lifecycle `NOT_PLANNED → PLANNED → READY → IN_PROGRESS → IMPLEMENTED → VERIFYING → DONE`
- Ready Gate / Completion Gate freeze — `governance/core/TASK_*_GATE_STANDARD.md`
- Evidence levels E0/E1/E2 — `governance/core/EVIDENCE_STANDARD.md`
- Routing via `routing_engine.py` + `validate_routing.py` — Tier/Effort are computed
- Rule precedence — `governance/core/RULE_PRECEDENCE.md`
- Escalation — `governance/core/ESCALATION_PROTOCOL.md`
- Roadmap sync — `governance/core/ROADMAP_SYNC_STANDARD.md`

**Completion Gates frozen on 2026-08-23 keep their original semantics.** V4.3 governs new
routing and governance decisions; it does not retroactively rewrite a frozen contract. If
applying V4.3 would change a frozen gate's meaning, record
`LEGACY_GATE_COMPATIBILITY_REQUIRED` and leave the gate in force until the Owner disposes
of it.

---

## 5. Language Rule (project-level, unchanged)

All user-facing responses in every session are written in Vietnamese. All files whose
purpose is to explain, summarize, report or update project progress, session progress,
current status, completed work, remaining work, next steps or handoffs are written in
Vietnamese.

Technical tokens stay unchanged where translation could affect behaviour: code, terminal
commands, variable names, enums, identifiers, file paths, filenames, schema values, and
IDs such as `READY`, `DONE`, `MAJOR`, `S000`, `BLOCKING`, `HARDENING`.

CORE rule files follow the existing `governance/` convention and are written in English;
they are rules, not progress reports.

---

## 6. Structural Note — where CORE lives

The V4.3 portable pack places CORE at repository root. This repository has a standing rule
(`CLAUDE.md`, "Compact Directory Layout") that static governance lives under `governance/`
to keep the root thin, and that governance files must not be moved back to root.

Resolution, recorded in `docs/decisions/ADOPTION-V4_3-migration-record.md`: CORE is placed
at `governance/v4/CORE/` and **this file** is the single canonical entry point at root.
Names and authority order match V4.3; only the path prefix differs. Per the V4.3 overlay
principle, no existing file was renamed or moved.

---

## 7. Reading Order For A New Session

**Step 0 — before reading ANY state file.** Run the branch authority check:

```bash
bash governance/scripts/governance/branch_authority_check.sh --expect-branch <authorised branch>
```

Reading `PROJECT_PROGRESS.md` or any roadmap/current-state artifact from a stale or
un-authoritative branch is a defect that has already recurred in this repository. If the
check does not pass, STOP and confirm before reading state. If it reports
`INTEGRATION_DECISION_REQUIRED`, that is an Owner Decision, not a warning to walk past.

1. This file.
2. `governance/v4/CORE/` in authority order (§1 rows 1–6), plus `STATE_AUTHORITY.md`.
3. `PROJECT/PROJECT_PROFILE.md`, `PROJECT/CAPABILITY_REGISTRY.md`.
4. `PROJECT/PROJECT_PROGRESS.md` — current state, roadmap, risks, blockers.
5. `PROJECT/PRODUCTION_PATHS.md`, `PROJECT/REVIEW_BUDGET_LEDGER.md`,
   `PROJECT/HARDENING_BACKLOG.md`.
6. `PROJECT/PROJECT_DECISIONS.md`.
7. The task file of the current work package under `docs/tasks/`.
8. Then execute the S000 procedure in `governance/core/00_SESSION_ORCHESTRATION.md`.

Never answer a progress question from conversational memory.
