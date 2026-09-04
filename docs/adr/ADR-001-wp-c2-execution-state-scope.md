# ADR-001 — Execution State Scope for the Backtest Engine (WP-C2)

## Status
Accepted — 2026-09-04, Owner approval ("APPROVE PA-A CHO DEC-035, VÀ CHẤP NHẬN ADR-001."),
recorded in `PROJECT/PROJECT_DECISIONS.md` `DEC-035`. This satisfies the WP-C2 Ready Gate item
"ADR phạm vi Execution State tồn tại và được chủ dự án chấp nhận" and gives evidence for
`CHECK-C2-01` and `CHECK-C2-03` in `docs/tasks/WP-C2-execution-state-machine.md`. This ADR
does **not** implement WP-C2; it only answers the scope question WP-C2's own Ready Gate says
must be answered before the package may start. Implementation (subtasks C2.1–C2.6) still
requires a separate execution session.

## Date
2026-09-04

## Context

Strategy Spec §16/§19 define six Execution States:
`WAIT / FUNDING_REQUIRED / READY_TO_BUY / ACTION_PENDING / COOLDOWN / DATA_BLOCKED`. S001
discovery (carried into `docs/tasks/WP-C2-execution-state-machine.md`) found that five of the
six already exist as unnamed behavior in `src/eth_dca_os/engine.py`. `FUNDING_REQUIRED` is the
one exception: it is not merely unnamed, it has no behavior to name.

Backtest Spec §5 defines `total_delay = user_delay + funding_delay` with
`funding_delay = 0 nếu USDT treasury đã đủ` (line 81) — a conditional on treasury
sufficiency. But `docs/CONVENTIONS.md` #8 already resolved how `funding_delay` is actually
produced: it is a deterministic function of the configured `funding_policy`
(`ON_DEMAND → funding_delay áp toàn phần`, `BULK_MONTHLY → funding_delay = 0`), not a
per-action check against a simulated treasury balance. `RELEASE_CHECK_V2_1_5.md` confirms
`funding_delay` already has a field in `execution_config` (Data Model §3) and is already one
of the four friction dimensions exercised in the frozen Gate 3 manifest (114 configs,
`docs/spec/03_BACKTEST_SPEC_V2_1_5.md` §10.1). The already-completed official run (`T-06`,
`DEC-031`, verdict `DO_NOT_BUILD`) used exactly this convention. `engine.py` therefore never
evaluates a live "is the treasury big enough" branch — that branch, as literally written in
BT §5, has never been instantiated in this codebase.

WP-C2's own scope is bounded to `docs/adr/`, `src/eth_dca_os/engine.py` (naming/consolidating
existing behavior only), `tests/`, and `docs/CONVENTIONS.md`. It explicitly excludes
`webapp/` and must not change backtest results (`CHECK-C2-06`).

## Decision

`FUNDING_REQUIRED` is **NOT_APPLICABLE** as a distinct, dynamically-triggered Execution State
at the backtest engine layer. The backtest engine does not gain a simulated USDT treasury
balance, and `funding_delay` continues to be produced exactly as `docs/CONVENTIONS.md` #8
already specifies (a deterministic function of `funding_policy`), with zero change to
`engine.py`'s numerical behavior.

The other five states — `WAIT`, `READY_TO_BUY`, `ACTION_PENDING`, `COOLDOWN`, `DATA_BLOCKED`
— are in scope for WP-C2's naming/consolidation work (subtasks C2.2–C2.4), because each
already has real, existing, name-able behavior in `engine.py` per the S001 discovery table.

This decision is scoped to the backtest engine (`src/eth_dca_os/`) only. The live/app layer
still requires `FUNDING_REQUIRED` per Product Spec §6 ("Execution State: WAIT /
FUNDING_REQUIRED / ...") and §7 (manual execution workflow: "CHECK TREASURY → [FUNDING_REQUIRED]
→ READY_TO_BUY"). This ADR does not narrow, waive, or otherwise decide that app-layer
requirement — it is out of WP-C2's scope entirely (`webapp/` is explicitly not touched by
WP-C2) and remains open for whichever future task builds live execution (subject to the
verdict gate and to `DEC-005`, see the accompanying report).

## Alternatives Considered

1. **Model a live USDT treasury balance in `engine.py`** and derive `funding_delay` from an
   actual per-action sufficiency check, matching BT §5's literal text. Rejected: this is new
   engine behavior that has never been exercised by the completed official run. Per `DEC-009`
   ("Gate 1 staleness"), any remediation touching input/calculation/execution/backtest
   behavior invalidates prior Gate 1 results and forces Gate 1 to be rerun before the result
   can be used for a verdict — a wildly disproportionate cost for what WP-C2 defines as a
   pure naming/consolidation task, and it would also violate WP-C2's own Out-of-Scope clause
   and `CHECK-C2-06` (backtest results must not change).
2. **Leave `FUNDING_REQUIRED` silently undefined.** Rejected: `CHECK-C2-03` explicitly
   requires it be handled without silent absence, and Product Spec §6/§11's app-layer
   requirement for this state would go unacknowledged in the boundary contract.
3. **(Chosen) Declare `NOT_APPLICABLE` at the backtest layer**, record the reason in this ADR
   and (at WP-C2 execution time) in `docs/CONVENTIONS.md`, and explicitly preserve the
   app-layer requirement so it is not lost.

## Rationale

`docs/CONVENTIONS.md` #8 is already canonical and was already exercised by the completed
official `T-06` run — this decision does not introduce a new interpretation, it names one
that already governs the code and the evidence on file. Choosing anything that requires new
engine behavior would risk exactly the kind of drift Implementation Plan §1 exists to
prevent (backtest and app describing the same situation in two different languages) while
also risking reopening `T-06`/Gate 1, which is out of scope for a naming task and for this
ADR-preparation session.

## Consequences

### Positive
- Closes `CHECK-C2-01` and the `(b)` branch of `CHECK-C2-03` with zero risk to backtest
  correctness, zero risk of Gate 1 staleness, and zero change to official-run evidence.
- Keeps WP-C2 to the pure naming/consolidation task RCP-001 intended ("không tạo một class
  `StateMachine` chỉ để khớp tên trong spec").

### Negative / Tradeoffs
- `FUNDING_REQUIRED` will never appear as an observed value of
  `market_snapshots.execution_state` in backtest output. Anyone reading backtest snapshots
  must know this state is app-layer-only. Mitigation: an explicit `docs/CONVENTIONS.md` entry
  (WP-C2 subtask C2.6) and a code comment at the point `execution_state` is written.

## Migration / Implementation Notes
- WP-C2 subtask C2.6 should record this decision in `docs/CONVENTIONS.md` as a new numbered
  item (items currently run through #21; the next number is #22).
- `CHECK-C2-05` (`market_snapshots.execution_state` NOT NULL) applies only to the five
  in-scope states; `FUNDING_REQUIRED` is never a value written to that field by the backtest
  engine.
- This ADR makes no claim about the live/app layer's implementation of `FUNDING_REQUIRED`;
  that is out of WP-C2's touch area and unaffected by this decision.

## Supersedes
None

## Superseded By
None
