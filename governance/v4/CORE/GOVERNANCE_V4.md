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
