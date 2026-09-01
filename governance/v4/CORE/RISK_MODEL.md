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
