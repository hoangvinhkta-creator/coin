# CORE — GOVERNANCE V4.3

Status: CANONICAL (V4.3 overlay)
Layer: CORE — project-agnostic.

## What V4.3 Changes

V4.3 does not loosen safety gates. It changes how *work is routed* so that a correct
review culture does not turn into an unbounded repair loop.

| Concern | Pre-V4.3 default | V4.3 rule |
|---|---|---|
| A new finding | tends to become a task | a finding is not a task (`FINDING_ROUTING`) |
| Review breadth | narrowed to protect scope | review stays broad; **repair** is narrow |
| Budget | resets per task/session/branch | accrues to capability lineage root |
| Stopping | any obstacle can stop delivery | only five canonical hard-stops |
| Realism | "could happen" justifies blocking | production path required to block |

## Overlay Principle

When V4.3 is adopted into a repository that already has governance:

    ADOPT -> MAP -> BRIDGE -> DEPRECATE GRADUALLY

never

    DELETE -> REBUILD

Specifically forbidden during adoption:

- mass deletion or mass rename of existing governance;
- moving files such that paths referenced by existing tasks/sessions break;
- rewriting decision history;
- editing historical tasks so they appear to have been created under V4.3;
- changing product code.

## Legacy Gate Compatibility

V4.3 applies to NEW routing and governance decisions. It does not retroactively rewrite a
contract that has already been FROZEN.

If applying V4.3 would change the semantics of a FROZEN task or gate, do NOT edit it.
Record:

    LEGACY_GATE_COMPATIBILITY_REQUIRED

and keep the existing gate in force for that task until the Owner disposes of it.

## Authority Order

Every agent reads in this order. Lower numbers win:

1. `CORE/CAPABILITY_MODEL.md`
2. `CORE/GOVERNANCE_V4.md`
3. `CORE/DELIVERY_LOOP.md`
4. `CORE/REVIEW_PROTOCOL.md`
5. `CORE/RISK_MODEL.md`
6. `CORE/PRODUCTION_PATH_RULE.md`
7. PROJECT profile / capability / state
8. production paths
9. risk register
10. completion gates
11. review budget ledger
12. project decisions
13. current task / spec

An Owner Decision recorded in the project decision log outranks any session prompt. A
session prompt never outranks canonical governance.

## Agent Adapters

`CLAUDE.md`, `CODEX.md` and any equivalent are ADAPTERS. An adapter:

- points at the canonical entry point and is read after it;
- must not become an independent source of governance authority;
- must not derive its own rules;
- must not create tasks;
- must not grant itself repair budget;
- must not duplicate the body of CORE or PROJECT governance.

## Artifact Budget

Governance adoption and routing must not generate document sprawl. Do not create:

- one report per finding;
- one decision file per edge case;
- one task file per hardening item.

Prefer canonical files plus mapping. One adoption/migration record is sufficient for an
adoption.

---

# Part II — The Proof Layer

Part I above states what V4.3 *changes* about routing. Part II states what V4.3 requires
you to *prove*. Both are canonical. Reconciled against the `AI_ENGINEERING_V4_3_PORTABLE`
source pack on 2026-09-01; see `docs/decisions/ADOPTION-V4_3-migration-record.md`.

## II.0 Standards That Must Not Be Lost

Adopting V4.3 never removes any of these. A project that already has them keeps them:

- exact branch / full SHA / remote SHA / tracked-worktree checkpoint;
- Scope Lock, Ready Gate, Completion Gate, Evidence Standard;
- implementer/reviewer separation wherever a risk area needs independent review;
- immutable provenance / raw input wherever the business needs traceability;
- Human/Owner Decision for business ambiguity;
- default-deny at boundaries that genuinely need it;
- business rules configurable where the business changes over time;
- non-regression / reconciliation appropriate to the project;
- the history of decisions, handoffs, reviews, repairs and evidence.

An adoption is never a licence to open a governance cleanup epic.

## II.1 Risk Follows The Data Path

Risk is never scored by module name (`helper`, `framework`, `internal`, `UI`). It is scored
by one question: **if this path is wrong, which business output is wrong, and what is the
consequence?** One file may carry several data paths at different Blast Radius.

    Effective Risk = MAX(Local Risk, Blast Radius of the data path being changed)

A Golden Baseline may reduce Blast Radius by **one level only** when a *specific* Golden
test covers that exact path. Never infer a reduction from the mere existence of a Golden.
Details and level examples: `RISK_MODEL.md`.

## II.2 Review / Repair Budget — Numbers

Budget attaches to the **lineage root** (`CAPABILITY_MODEL.md`), never to a task, and does
not reset on either axis — vertical (`R1 → R1-A → R1-A1`, subtask, work package) or
horizontal (sibling tasks inside one capability). The horizontal axis is the same evasion
turned sideways; policy alone is not enough, the ledger's shape must not reward splitting.

Defaults, when the Owner has set no explicit value:

| Effective Risk | Blocking repair cycles |
|---|---|
| LOW | 1 |
| MEDIUM | 2 |
| HIGH | 2 |

The Owner may raise or lower this before implementation, with a recorded reason.

**One repair cycle** = one round of fixes after the reviewer has returned *every* BLOCKING
finding identifiable for that review scope. A reviewer who serialises blocking findings
across rounds has committed a process failure, not thoroughness.

A finding that lies inside the **cumulative repair diff** of the current cycle is a defect
of that same repair and does **not** open a new cycle. A new cycle may be considered only
for a finding outside the cumulative repair diff of every repair recorded in the ledger,
and only if budget remains or an Owner Extension exists.

When budget is exhausted the only moves are:

    ACCEPT_AS_IS | DESCOPE | OWNER_EXTENSION

Creating a new unit of work — including a sibling at the same level — is not among them.

    task creation approval != repair-budget allocation approval

## II.3 Branch Authority — Machine First

Before reading any project state, roadmap or current-state artifact:

- `git fetch origin --prune`;
- resolve the default branch **dynamically**; never hardcode `main`;
- attached branch: check upstream exists and that local is not behind;
- detached HEAD: must match the reviewed `TARGET_SHA`;
- print how many commits ahead of the default branch HEAD is;
- confirm the tracked worktree is clean.

Wrong authority → STOP and confirm. Reading state from a stale branch is a defect that has
already recurred; it is not a formality.

### Integration Decision thresholds

    ahead of default branch  > 10 commits;  or
    age of first unintegrated commit > 3 days;  or
    cumulative diff > 5,000 LOC

Crossing any threshold raises `INTEGRATION_DECISION_REQUIRED`. The Owner then chooses:
integrate/merge early, cut scope, or accept the divergence with a stated reason and a
re-evaluation date. Continuing silently is not an option.

Enforced by `governance/scripts/governance/branch_authority_check.sh`.

## II.4 Merge Gate Blocked

A merge gate BLOCKED for more than 30 days forces an Owner Decision:

(a) supply the missing dependency/data; (b) convert it into a post-merge production
acceptance gate; or (c) remove it from the gate set with a reason.

It may not hang indefinitely.

## II.5 Artifact Budget

By default a task needs only four artifacts: SPEC/TASK, PROGRESS/STATE, REVIEW, and a
shared DECISIONS file. A **fifth** artifact requires Owner approval. Pre-existing
historical artifacts are grandfathered and are never retro-fitted.

## II.6 Artifact Internal Precedence

This does not replace system or project safety/rule precedence. *Within a single artifact*:

1. an identity/normative table declared to be normative;
2. machine-readable state;
3. explanatory prose.

On conflict the higher source wins **and** a reconciliation finding must be raised. Never
silently repair the semantics when you lack Owner authority.

## II.7 Clean Worktree Semantics

Test-runner caches (`__pycache__`, `.pytest_cache`, `.coverage`) are not repository
modifications while untracked or ignored. CLEAN means: no tracked file modified, staged or
deleted outside the permitted scope. Record status before and after.

## II.8 Interpreter / Environment Differences

Where an evidence record pins an interpreter or tool version, a version mismatch is by
itself:

    ENVIRONMENT_REVERIFY_REQUIRED

Re-verify the invariant. Only an invariant failure is BLOCKING. A version mismatch whose
semantics still hold is not a correctness failure.

## II.9 Adoption Governs Itself

A V4.3 adoption is bound by V4.3: Effective Risk defaults to MEDIUM; at most one blocking
repair cycle for the adoption task; no production code changes; no governance cleanup epic.
If it cannot be achieved in one cycle, DESCOPE to a minimal overlay.

    POLICY_ADOPTED   policy + canonical entry point + ledger + branch check all working
    FULLY_ENFORCED   the above, plus an executable Golden Baseline and the project's guards

Governance CI automation is hardening. It does not block starting product work once the
minimum bootstrap/adoption check has passed.

## II.10 Conditions For Convergence

A task may converge when all of the following hold:

- its Completion Gate PASSes, or the Owner has dispositioned it;
- no BLOCKING finding with a current production path remains;
- the appropriate regression PASSes;
- evidence is sufficient to reproduce at the declared risk level;
- budget has not been evaded;
- every HARDENING item has a backlog entry and a re-trigger;
- the review target and branch authority are unambiguous;
- there is no scope violation;
- no new task ID was registered without Owner approval;
- the work done sits inside the vertical slice, or was explicitly routed off the critical
  path.

Do not continue reviewing merely to make governance look perfect.
