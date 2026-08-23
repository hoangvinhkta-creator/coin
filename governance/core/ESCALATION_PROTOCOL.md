# Escalation Protocol

## Purpose
Prevent repeated patching and force root-cause review when a task exceeds the current agent/session capability.

## Escalation Triggers
Escalate when any of the following occurs:

- two materially different implementation attempts fail;
- architecture conflict is discovered;
- security behavior is ambiguous;
- unexpected migration/data-loss risk appears;
- scope must expand across major modules;
- required completion gate cannot be satisfied safely;
- regression spreads beyond expected Blast Radius;
- production behavior differs materially from documented assumptions.

## Required Action

STOP IMPLEMENTATION
→ preserve evidence
→ document blocker
→ perform root-cause review
→ escalate agent tier / architecture review
→ update plan if needed

## Prohibited Behavior
Do not:
- continue stacking speculative fixes;
- disable failing checks;
- weaken Completion Gate;
- broaden scope silently;
- perform unrelated refactors.

## Escalation Record

Reason:
...

Attempts made:
...

Observed evidence:
...

Suspected root cause:
...

Affected scope:
...

Recommended agent tier:
...

Recommended next action:
...


## Deterministic Failure Classification

Before escalation, classify the failed attempt with evidence:

- `MISSING_INPUT`: required data/decision/permission/tool/acceptance criterion is absent → BLOCKED; no Tier/Effort increase.
- `VERIFICATION_DEPTH`: core approach remains coherent; more investigation/testing/evidence is needed → raise Effort one supported step.
- `CAPABILITY_CEILING`: two materially different attempts at the same Tier, with at least high effort when supported, fail for the same conceptual/architectural reason; or no coherent plan can satisfy known constraints → raise Tier one step.
- `SCOPE_CHANGED`: new facts materially alter routing inputs → recompute routing from scratch.

One ordinary test failure is not evidence of a capability ceiling. Every escalation record MUST include `Failure Classification` and evidence supporting it.
