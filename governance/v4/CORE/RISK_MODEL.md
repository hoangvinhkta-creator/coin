# CORE — RISK MODEL (V4.3)

Status: CANONICAL (V4.3 overlay)
Layer: CORE — project-agnostic.

## Effective Risk

Effective Risk is the risk of the work as it will actually be executed, including anything
absorbed into it. It is recomputed whenever absorption changes the shape of a task — this
is what makes Absorption Limit threshold A measurable rather than rhetorical.

## Inputs

Effective Risk is derived from the project's existing routing metadata and risk register.
V4.3 does not replace an existing routing engine; it constrains how its output is used:

- Tier and Effort are computed, never chosen by intuition;
- hard floors are applied inside the routing calculation;
- routing validation must PASS before execution.

## Risk And Blocking

A finding's risk level does not by itself make it BLOCKING. `REVIEW_PROTOCOL.md` requires
a production path AND a consequence inside a Completion Gate or the risk register AND
reproducible evidence. A high-severity finding with no current production path is
HARDENING with a re-trigger, not a blocker.

Conversely, a low-severity finding IS blocking when it violates a FROZEN contract that a
Completion Gate depends on. Severity and blocking status are separate axes.

## Data Integrity

`DATA_INTEGRITY_RISK` is one of the five canonical hard-stops. It is reserved for
situations where continuing risks losing or corrupting real data or real provenance — not
for ordinary defects that are recoverable by re-running.

## Risk Register Authority

The risk register is a PROJECT artifact. CORE does not enumerate project risks. A finding
that maps to a registered risk inherits that risk's standing for blocking purposes; a
finding that maps to no registered risk and no Completion Gate does not become blocking by
assertion.

---

## Local Risk And Blast Radius

Reconciled against the source pack on 2026-09-01. Two independent inputs, never merged:

**Local Risk** — the complexity of the change and the likelihood of getting it wrong at the
point of change.

**Blast Radius** — the business consequence if the error passes every control layer that
exists today.

    Effective Risk = MAX(Local Risk, Blast Radius)

A small change on a high-consequence path is HIGH. Size is not the input; the data path is.

### Blast Radius — HIGH

- wrong identity, ownership or permission;
- wrong money, KPI, payroll, tax or settlement;
- corrupted source data that cannot be recovered;
- a wrong aggregation feeding an important decision;
- a security/privacy boundary with a real consequence.

### Blast Radius — MEDIUM

- a wrong business output that still passes a reconciliation or human gate before use;
- a workflow fault that interrupts work without silently producing a wrong decision.

### Blast Radius — LOW

- presentation, diagnostics or helpers that do not change business value;
- auxiliary enforcement with no current production consequence.

## Golden Reduction — One Level, Four Conditions

Blast Radius may be reduced by exactly one level, and only when **all four** hold:

1. a specific Golden test exists;
2. it covers that exact path;
3. a failure of that path turns the Golden red;
4. the test name and its evidence are recorded in the risk register.

No specific test → no reduction. The existence of "a Golden" proves nothing about a path it
does not execute.

## HIGH Does Not Mean STOP

HIGH sets the **depth of review**, not the right to continue. Implementation may continue
inside the delivery loop when authority is clear and the change is MEDIUM or below; a
change on a HIGH Blast Radius path requires a mandatory batch review at end of session,
however small the change. Only `source data mutation`, `contract/interface semantics` and
`integrity-sensitive persistence` escalate to a genuine hard-stop — `DATA_INTEGRITY_RISK`
or `ARCHITECTURE_CHANGE_REQUIRED`.
