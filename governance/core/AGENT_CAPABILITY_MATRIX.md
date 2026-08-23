# Agent Capability Matrix

## Purpose
Assign work by required capability and reasoning effort in a way that is explicit in the roadmap, cost-aware, and still reviewable when model generations change.

The roadmap MUST record two separate decisions for every implementation task:

1. **Capability Tier** — which class of model/agent should own the task.
2. **Effort Level** — how much reasoning/tool-use effort that model should spend.

Do not collapse Tier and Effort into one field. A Tier B task at `high` effort is not the same thing as a Tier C task at `low` effort.

## Default Capability Tiers

### Tier A — Lightweight / Fast
Best for:
- trivial edits,
- documentation updates,
- repetitive bounded changes,
- simple test additions,
- low-risk UI corrections,
- mechanical repository maintenance.

Default current model class:
**Haiku**.

### Tier B — Standard Implementation
Best default for:
- CRUD,
- forms,
- routes,
- service implementation,
- standard API work,
- bounded refactors,
- normal test work,
- well-specified feature implementation.

Default current model class:
**Sonnet**.

### Tier C — Advanced Reasoning
Use for:
- architecture,
- authentication/authorization,
- complex migrations,
- high-risk data changes,
- cross-module refactors,
- difficult debugging,
- root-cause analysis,
- production incidents,
- business logic where mistakes have material consequences.

Default current model class:
**Opus**.

### Tier D — Frontier / Long-Horizon
Use only when the task genuinely requires frontier capability, sustained autonomy, unusually large context, or long-horizon multi-stage reasoning, for example:
- complex multi-agent orchestration,
- large migrations spanning many modules,
- difficult architecture work with many interacting constraints,
- long-running autonomous coding sessions,
- high-ambiguity problems where repeated planning, tool use, validation, and self-correction are required,
- tasks that have already failed or stalled at Tier C despite correct effort and context.

Default current model class:
**Fable**.

Tier D is NOT a synonym for UI/design work. Visual/design tasks should be assigned by actual task difficulty and available model capability.

## Effort Levels

Canonical effort vocabulary for roadmap planning:

- `low` — fastest/cheapest; bounded, obvious work.
- `medium` — balanced; routine implementation with some reasoning.
- `high` — complex work where quality matters more than speed/cost.
- `xhigh` — extra-high; demanding coding/agentic work requiring extended exploration.
- `max` — maximum effort; reserve for genuinely frontier or highly consequential work.

`xhigh` is the canonical spelling. Do not write `extra`, `extra-high`, or `extra_high` in machine-readable roadmap fields.

### ULTRACODE

`ULTRACODE` is NOT a canonical provider reasoning-effort level. It may be used only as an optional **Execution Profile** when the actual runtime/agent harness explicitly supports such a mode.

If `ULTRACODE` is used:
- keep the canonical Effort Level separately (`low|medium|high|xhigh|max`),
- record `Execution Profile: ULTRACODE`,
- do not assume every model/provider supports it,
- do not use it as a substitute for Tier or Effort.


## Deterministic Model + Effort Routing Algorithm

Tier/model and Effort are two independent routing decisions. Agents MUST NOT type a Tier/Effort from intuition and then treat it as authoritative. For MAJOR tasks, routing MUST be reproducible from scored metadata and MUST pass the routing validator.

### Canonical scoring scale

Every routing input uses the SAME integer scale **0–4**:

- `0` = absent / trivial
- `1` = low
- `2` = moderate
- `3` = high
- `4` = extreme

`1/5`, `3/5`, percentages, free-text substitutes, or mixed scales are invalid machine-readable routing input.

### Stage 1 — Select capability Tier / model class

Score five inputs, each 0–4:

- `D` Task Difficulty — total cognitive/technical difficulty of producing a correct result. This is NOT limited to how many lines of code are changed. Cross-document reasoning, subtle review, diagnosis, architecture analysis, and difficult research can have high D even when no production code is touched.
- `R` Risk — consequence if the result is wrong.
- `B` Blast Radius — how much of the system/business can be affected.
- `A` Ambiguity — how incomplete, conflicting, or interpretation-heavy the requirements are.
- `X` Cross-system complexity — modules, agents, data sources, documents, services, or architectural boundaries that must remain coherent.

Compute the base score:

`MODEL_SCORE_BASE = 0.25D + 0.25R + 0.20B + 0.15A + 0.15X`

Base routing:

| MODEL_SCORE_BASE | Tier | Default model class |
|---|---|---|
| 0.00–0.99 | A | Haiku |
| 1.00–1.99 | B | Sonnet |
| 2.00–2.99 | C | Opus |
| 3.00–4.00 | D | Fable |

#### Cognitive-complexity floor

The base weighted score alone is not sufficient for high-ambiguity, cross-system work. Apply these floors inside the routing algorithm:

- `A >= 3 AND X >= 3` → minimum Tier C.
- `A == 4 AND X == 4 AND (D >= 3 OR expected_horizon >= 3)` → minimum Tier D.
- `D >= 4 AND X >= 3` → minimum Tier C even when production Blast Radius is low.

This prevents analysis/review/orchestration work from being under-routed merely because it changes little or no production code.

#### Safety/business hard floors — mandatory algorithm step

Hard floors are NOT advisory prose. The router MUST evaluate them after the base score and before emitting a result:

- authentication/authorization, security-sensitive logic, destructive migration, payroll/KPI/accounting logic, material financial calculation, or sensitive-data access control → minimum Tier C;
- active security incident, architecture spanning multiple subsystems with high ambiguity, long-horizon autonomous orchestration, or repeated capability-ceiling failure at Tier C → minimum Tier D when the stated conditions are met;
- purely mechanical edits MUST NOT be promoted only because the repository is large.

Final Tier is the highest of: **base Tier, cognitive-complexity floor, safety/business hard floor**. The router MUST record which floor, if any, changed the result.

### Stage 2 — Select Effort independently inside the chosen model

Score reasoning demand on five inputs, each 0–4:

- `U` Uncertainty — how much must be inferred or investigated.
- `V` Verification burden — amount of checking/testing/evidence required.
- `H` Horizon — number of dependent reasoning/tool steps expected.
- `C` Context burden — amount and dispersion of context that must stay coherent.
- `F` Failure cost — cost of a plausible wrong answer/change.

Compute:

`EFFORT_SCORE = 0.20U + 0.20V + 0.20H + 0.15C + 0.25F`

| EFFORT_SCORE | Canonical Effort | Human label |
|---|---|---|
| 0.00–0.79 | low | Low |
| 0.80–1.59 | medium | Medium |
| 1.60–2.39 | high | High |
| 2.40–3.19 | xhigh | Extra / Extra High |
| 3.20–4.00 | max | Max |

#### Effort hard floors

Apply after the numeric Effort score:

- payroll/KPI/accounting/material-financial calculation, destructive migration, authentication/authorization, or security-sensitive logic → minimum `high`;
- active security incident, irreversible/destructive operation without proven rollback, or a REQUIRED verification whose plausible failure can materially corrupt sensitive/financial data → minimum `xhigh`;
- `max` remains exceptional and is selected only by score or an explicit project/runtime policy.

Final Effort is the higher of numeric Effort and any applicable Effort floor. Record the applied floor.

The runtime MUST clamp the requested Effort to levels actually supported by the selected model/provider/session. If the exact level is unavailable, use the nearest supported level that does not silently reduce a mandatory floor; otherwise mark routing `BLOCKED_RUNTIME_CAPABILITY`. Provider UI labels may differ; roadmap metadata keeps canonical spelling.

### Stage 3 — Sanity checks

Before execution:

- Tier C/D with `low` effort → WARN and require explicit re-check of U/V/H/C/F. It may still be valid after re-check.
- Tier D with `medium` or lower → WARN and require explicit routing evidence.
- a safety/business hard-floor category with Tier below its floor or Effort below its floor → ERROR, not warning.
- missing any required score for a MAJOR task → routing status `INCOMPLETE`; execution MUST NOT start.

Warnings do not force artificial coupling between Model and Effort; they catch likely scoring mistakes.

### Stage 4 — Deterministic escalation / de-escalation

After a failed attempt, classify the failure using evidence:

1. `MISSING_INPUT` — required data, decision, permission, tool, or acceptance criterion is absent. → `BLOCKED`; do not raise Tier/Effort.
2. `VERIFICATION_DEPTH` — implementation concept is coherent, but evidence/test coverage/exploration is insufficient or a failure is found that can be addressed without changing the core approach. → raise Effort one supported step, then retry.
3. `CAPABILITY_CEILING` — two materially different attempts at the current Tier (with at least `high` effort when supported) fail for the same conceptual/architectural reason; or the agent cannot produce a coherent plan satisfying known constraints. → raise Tier one step and recompute Effort.
4. `SCOPE_CHANGED` — new scope materially changes D/R/B/A/X or U/V/H/C/F. → stop and recompute routing from scratch.

Do not infer `CAPABILITY_CEILING` from one ordinary test failure. Do not spend a larger model to compensate for `MISSING_INPUT`.

### Canonical router implementation

For MAJOR tasks, the executable reference is:

```bash
python governance/scripts/governance/routing_engine.py --help
```

The router receives the ten 0–4 scores plus category flags and emits Tier, model class, Effort, scores, floors, warnings, and routing status. Validators MUST compare recorded routing metadata against this calculation.

### Selection examples

- A difficult but well-specified isolated algorithm can be `C / Opus / medium`.
- A normal implementation requiring extensive regression verification can be `B / Sonnet / high`.
- A small payroll formula change is at least `C / Opus / high` because both model and effort floors apply.
- A cross-document review with high cognitive difficulty can route above Haiku even with Blast Radius 0.
- A long multi-agent migration can be `D / Fable / xhigh` or `max` only when supported and justified.

## Default Tier + Effort Guidance

| Work pattern | Primary Tier | Default model class | Suggested effort |
|---|---|---|---|
| Mechanical docs/config cleanup, tiny safe edit | A | Haiku | low |
| Small bounded code change, straightforward tests | A or B | Haiku / Sonnet | medium |
| Normal feature implementation with clear spec | B | Sonnet | medium |
| Multi-file implementation, moderate ambiguity | B | Sonnet | high |
| Difficult debugging, architecture-sensitive change | C | Opus | high |
| Security/data-critical or high blast-radius reasoning | C | Opus | xhigh |
| Long-horizon autonomous work, frontier complexity | D | Fable | xhigh |
| Exceptional frontier problem where failure cost is very high | D | Fable | max |

This table is guidance, not a substitute for task-specific judgment.

## Scoring Inputs
Agent assignment should consider:

- Difficulty: 0–4
- Risk: 0–4
- Blast Radius: 0–4
- Ambiguity
- Security impact
- Data impact
- Architecture impact
- Expected context size
- Expected session duration / horizon
- Cost/latency constraints

## Assignment Rules

Every MAJOR task MUST define:
- Primary Tier
- Primary Effort
- Escalation Tier
- Escalation Effort
- Escalation triggers

MICRO tasks may inherit the project default only when their risk is bounded and obvious.

Do not automatically choose the most expensive model or `max` effort. Choose the lowest Tier/Effort combination that is reasonably expected to satisfy the frozen Completion Gate.

If verification fails because of reasoning/capability limits rather than a bad requirement, escalate effort first when appropriate; escalate Tier when the task exceeds the model class or repeated failure indicates a capability ceiling.

## Provider Mapping Rule

Model names change faster than governance. The A→Haiku, B→Sonnet, C→Opus, D→Fable mapping is the current default mapping for this package, not an eternal identity.

During S000, confirm the actually available models. If a named class is unavailable or superseded, record the replacement in `PROJECT/PROJECT_PROGRESS.md` without changing the semantic meaning of Tier A/B/C/D.
