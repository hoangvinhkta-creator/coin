# Finance × CoinDCA — Shared Product Roadmap

**Document type:** Cross-project product roadmap / coordination overlay  
**Applies to repositories:** `Finance` and `coin` (product name: **CoinDCA**)  
**Created:** 2026-09-02  
**Activation mode:** staged; see §2  
**Authority:** coordination document only; it does **not** replace either repository's existing canonical specification, governance, frozen gates, active task authority, or current session instructions.

---

## 1. Purpose

This document defines how **Finance** and **CoinDCA** should evolve independently, converge visually, and later integrate into one personal-finance experience without disrupting work already in progress.

The target architecture is:

- **One user-facing entry point eventually.**
- **Two independently owned product modules underneath.**
- Finance owns the overall personal-finance picture.
- CoinDCA owns crypto strategy and investment accounting; its first active strategy is ETH.
- Binance may later provide read-only market/account facts; it must not be used by this roadmap to introduce direct trading.
- Integration happens through a small, explicit data contract, not by allowing one module to freely mutate the other's internal state.

This roadmap is intentionally incremental. A new idea, finding, or integration opportunity does not automatically create a task or alter the current critical path.

---

## 2. Activation and non-conflict rules

### 2.1 Effective date

This document may be committed to both repositories immediately on **2026-09-02**, but its implementation is **staged**.

### 2.2 What becomes effective immediately

The following are coordination/naming decisions and may be used immediately without changing current implementation scope:

1. Product name going forward: **CoinDCA**.
2. ETH Strategy V2.1.5 was evaluated and **FAILED validation** (official verdict `DO_NOT_BUILD`, coin repo `DEC-031`, 2026-09-03). It is a **frozen historical research authority**, not the active product strategy. CoinDCA's product direction is **L-1** — a simpler DCA/benchmark discipline (`DEC-040`, 2026-09-05). Corrected by `DEC-041` H; see the Reconciliation block in §12.
3. Existing technical names such as `eth_dca_os`, existing state keys, Firestore paths, tests, IDs, task names, and historical artifacts are **legacy-compatible technical identifiers** and must not be mass-renamed merely for branding.
4. Finance and CoinDCA remain separate repositories and separate capability ownership boundaries for now.
5. Finance's visual language is the reference direction for future cross-product design convergence.

### 2.3 What must NOT interrupt current work

This roadmap MUST NOT, by itself:

- modify an active task's frozen Ready Gate or Completion Gate;
- reopen a completed task;
- create repair work from non-blocking findings;
- change current accounting, Buy Score, regime, recommendation, persistence, or data algorithms;
- merge the `Finance` and `coin` repositories;
- start multi-coin strategy generalization;
- introduce Binance account/trade synchronization;
- start a shared portal;
- trigger broad file/module renames;
- cause an agent to leave its current branch/session to implement this roadmap.

If an active repository governance rule conflicts with this document, the active repository's canonical authority wins until the current task/session is safely completed. The conflict should then be reconciled explicitly rather than silently changing scope.

### 2.4 Current-work protection

**CoinDCA:** while T-09B production verification is still active, T-09B remains the priority. This roadmap is informational only. Do not implement design convergence, product-wide rename, Binance integration, Finance integration, or multi-coin work inside T-09B.

**Finance:** the current Finance Phase 1 scope remains the priority. Do not pull CoinDCA requirements into Phase 1 merely because this roadmap exists. Phase 1 should first become a dependable replacement for the user's current day-to-day personal-finance tracking workflow.

### 2.5 Promotion rule

A roadmap phase becomes implementation-authoritative only when:

1. its prerequisites below are satisfied;
2. the current active task/phase is closed or reaches a safe boundary;
3. the owner explicitly starts/promotes that phase under the target repository's normal governance.

**Roadmap item ≠ active task.**

---

## 3. Product boundaries

### 3.1 Finance

Finance is the source of truth for the user's **overall personal-finance picture**.

Expected ownership includes:

- income and expense;
- receivables/payables and personal debts;
- asset holdings across categories;
- net worth;
- monthly snapshots/history;
- cash/liquidity picture;
- portfolio allocation at the aggregate level.

Finance may display crypto assets, but it should not own CoinDCA's strategy engine.

### 3.2 CoinDCA

CoinDCA is the source of truth for **crypto accumulation strategy and strategy-specific accounting**.

For the current product generation (corrected by `DEC-041` H — see §12 Reconciliation):

- Product: **CoinDCA**.
- Active strategy: **none.** Product direction = **L-1**, a simpler DCA/benchmark discipline
  (`DEC-040`). ETH Strategy V2.1.5 = **frozen historical research authority**; validation
  **FAILED**; verdict `DO_NOT_BUILD`; `can_proceed_to_app = false` permanently.
- ETH remains the asset the L-1 ledger tracks. It is **not** a validated strategy asset.

The ownership list immediately below was written for the V2.1.5 product generation. Under L-1,
`Buy Score`, `regime`, `buy zones/ladders` and `ETH strategy recommendations` are **superseded**
— retained here only as a record of the previous generation.
- BTC or other market series may be used as signals/reference data without implying that a BTC/SOL/ADA strategy exists.

Expected ownership includes:

- market-data processing for strategy purposes;
- indicators;
- Buy Score;
- regime;
- budget/deployment logic;
- buy zones/ladders;
- ETH strategy recommendations;
- strategy trade history;
- ETH holdings/average cost/accounting required by the strategy;
- persistence of CoinDCA state.

### 3.3 Binance

Future Binance integration has two distinct roles:

**Market data**
- public prices/candles/volume and other explicitly approved market inputs;
- belongs primarily to CoinDCA's DATA stream;
- may become part of CoinDCA V1 production completion if required by its canonical acceptance criteria.

**Account/trade facts**
- balances;
- executed trades;
- fees;
- timestamps/quantities/prices;
- read-only use only under this roadmap.

Account/trade synchronization is a later integration phase and must not be pulled into current T-09B or Finance Phase 1.

---

## 4. Multi-coin truth and naming policy

### 4.1 Current truth

Renaming the product to **CoinDCA** is a product-direction decision, not a claim that the current strategy engine already supports arbitrary coins.

Current semantic model:

```text
CoinDCA
└── ETH Strategy V2.1.5   [ACTIVE / current]

Future possibilities
├── BTC Strategy          [NOT IMPLEMENTED]
├── SOL Strategy          [NOT IMPLEMENTED]
└── Other strategies      [NOT IMPLEMENTED]
```

### 4.2 Forbidden shortcut

Do not convert the existing ETH strategy into a generic strategy merely by replacing `ETH` with a `coinSymbol` variable or adding an asset dropdown.

A new strategy asset must earn its own evidence where its financial logic depends on asset behavior, thresholds, indicators, backtests, or accounting assumptions.

### 4.3 Multi-coin portfolio view may precede multi-coin strategies

A later CoinDCA version may safely display multiple crypto holdings without claiming strategy support for them:

```text
BTC — holding/value — Strategy: NONE
ETH — holding/value — Strategy: ACTIVE
ADA — holding/value — Strategy: NONE
```

Portfolio visibility and strategy recommendation are separate capabilities.

---

## 5. Shared design direction

### 5.1 Reference language

Finance is the reference visual language for future convergence because it is suited to a calm, personal-finance application rather than a trading terminal.

Shared direction:

- neutral light background;
- white/neutral cards;
- restrained borders and small radii;
- compact information density;
- clear left navigation on desktop;
- mobile navigation appropriate to small screens;
- consistent form controls, buttons, tables, spacing, and typography hierarchy;
- color used primarily to communicate meaning, not decoration.

### 5.2 CoinDCA-specific identity that should remain

CoinDCA may retain stronger semantic treatment for:

- Buy Score;
- regime;
- GO/WAIT or equivalent decision state;
- risk/warning/failure states;
- ladder status;
- financial numeric presentation;
- monospace typography where it improves numerical scanning.

### 5.3 Convergence rule

Design convergence is a **presentation-layer project**. It must not silently modify:

- financial algorithms;
- accounting behavior;
- persistence semantics;
- data contracts;
- Buy Score/regime logic;
- validation rules.

Do not begin CoinDCA design convergence until T-09B reaches DONE or an equivalent safe production-persistence boundary.

---

## 6. Parallel delivery roadmap

## Stage 0 — Protect current work

**Status:** ACTIVE NOW

### CoinDCA

Finish the current T-09B production verification under its existing authority.

Target outcome:

```text
T-09B IMPLEMENTED
        ↓
production verification
        ↓
T-09B DONE (if gates/evidence pass)
```

No roadmap-driven feature expansion is allowed inside this stage.

### Finance

Continue Finance Phase 1 according to its existing specification and current task authority.

Target: a dependable personal daily-use workflow for the already-defined Finance Phase 1 scope.

### Exit condition

Each repository reaches a safe boundary where new product work can be opened without contaminating an active task.

---

## Stage 1 — Establish stable standalone products

**Activation:** after the relevant repository exits Stage 0. The two repositories do not need to finish on the same day.

### Finance Stream — Phase 1 completion

Priorities remain the Finance canonical Phase 1 scope, including the already-defined areas such as:

- income/expense workflow;
- pending/realized handling where specified;
- debts/receivables;
- assets/holdings;
- month closing/snapshots/history;
- durable storage and normal daily usability where required by Finance's own spec.

Success criterion:

> Finance can be used independently for its intended day-to-day personal-finance workflow without needing CoinDCA.

### CoinDCA Stream — V1 production completion

After T-09B closes:

1. adopt **CoinDCA** as presentation/product branding;
2. preserve legacy technical identifiers unless a separate migration is justified;
3. complete the real market-data production path required by the ETH strategy;
4. connect DATA and WEB streams through the existing validated boundaries;
5. run the canonical end-to-end Golden path;
6. prove normal browser usage without terminal/AI assistance for ordinary use.

Conceptual path:

```text
Real market data
      ↓
validation
      ↓
indicators
      ↓
Buy Score / regime
      ↓
recommendation / budget
      ↓
web
      ↓
record trade
      ↓
accounting
      ↓
durable persistence
```

### Important DATA × WEB clarification

CoinDCA has two streams that may progress independently:

```text
DATA STREAM                     WEB STREAM
market sources                  browser UI
validation                      accounting workflow
indicators                      interaction
Buy Score/regime                persistence
recommendation                  history/settings
        \                         /
         \                       /
          └── end-to-end integration
```

Neither stream should be mistaken for the whole product. V1 requires their production-realistic integration.

---

## Stage 2 — Design convergence

**Activation:** CoinDCA persistence is stable and Finance's base visual language is stable enough to act as reference. Prefer doing this after Stage 1 functionality is no longer moving rapidly.

Create a small shared design specification/tokens document covering only presentation primitives such as:

- page background/surface;
- card;
- spacing scale;
- border/radius;
- typography hierarchy;
- navigation;
- form controls;
- buttons;
- tables;
- responsive behavior;
- semantic status colors.

Then adapt CoinDCA's shell to that language while preserving CoinDCA-specific decision semantics.

**Explicitly out of scope:** algorithm refactors, accounting refactors, persistence changes, multi-coin architecture.

---

## Stage 3 — Real-use stabilization

**Activation:** each standalone product can perform its intended primary workflow.

Use both products independently in real daily/as-needed workflows before designing deep integration.

Observe only actionable product facts, for example:

- which screens are actually used;
- repeated manual input;
- duplicated facts across products;
- confusing ownership of data;
- recurring reconciliation needs;
- missing information that materially affects decisions.

Do not create work for every observation. Promote only recurring or material problems.

Finance's own staged-development principle remains authoritative for its later phases.

---

## Stage 4 — Binance read-only integration

### Stage 4A — Market data

**Timing:** may occur earlier as part of CoinDCA Stage 1 if required to complete its real-data V1 path.

Purpose: supply real strategy market data.

### Stage 4B — Account/trade facts

**Timing:** only after CoinDCA's standalone V1 Golden path is stable and real use shows that automatic reconciliation is valuable.

Allowed direction:

```text
Binance
  ↓ read-only
balances / executions / fees / timestamps
  ↓
CoinDCA reconciliation/import
```

No direct trading is part of this roadmap.

The first implementation should prefer the smallest useful workflow (for example, importing/synchronizing new ETH executions) rather than building a generalized exchange synchronization platform.

---

## Stage 5 — Finance ↔ CoinDCA integration contract

**Activation:** Finance and CoinDCA are both independently usable and duplicated/shared facts have been observed in real use.

Do not begin by sharing databases or internal objects. Define a narrow versioned contract.

Illustrative CoinDCA → Finance facts:

```text
CryptoInvestmentFacts
- asset
- quantity
- current value
- deployed capital where meaningful
- average cost where authoritative
- last_updated_at
- source
```

Illustrative Finance → CoinDCA context:

```text
PersonalFinanceContext
- net worth
- liquid assets
- monthly investable surplus
- crypto allocation
- last_updated_at
```

These are examples, not frozen schemas. Freeze the real contract only after observing actual integration needs.

### Ownership rule

- Finance must not calculate CoinDCA's Buy Score or mutate its ladders.
- CoinDCA must not mutate Finance's income/expense ledger or net-worth history.
- Shared facts must have one clear authoritative owner/source.

---

## Stage 6 — Unified Personal Finance Hub

**Activation:** the integration contract is stable enough that a shared home adds value without becoming a third source of truth.

Target user experience:

```text
Personal Finance
│
├── Tổng quan
│   ├── Net worth
│   ├── Cash/liquidity
│   ├── Monthly cash flow
│   ├── Crypto allocation
│   └── CoinDCA decision summary
│
├── Tài chính
│   ├── Sổ tháng
│   ├── Công nợ
│   ├── Tài sản
│   └── Lịch sử
│
└── Đầu tư
    └── CoinDCA
        ├── ETH Strategy
        ├── Buy Score / Regime
        ├── Budget / Ladder
        └── Strategy history
```

The hub is a **presentation/composition layer**, not a new owner of Finance or CoinDCA business logic.

### Repository policy

Until this stage is actually approved:

- keep `Finance` and `coin` separate;
- do not create a monorepo merely in anticipation of integration;
- do not create a third portal repository until there is a concrete implementation need.

The eventual deployment can feel like one web app even if modules remain independently owned underneath.

---

## Stage 7 — Multi-coin expansion

**Activation:** only after ETH Strategy is stable in real use and the owner explicitly wants another asset strategy or multi-coin portfolio capability.

Recommended order:

1. multi-coin **portfolio visibility** if useful;
2. choose one additional strategy asset;
3. define its strategy hypothesis/spec;
4. validate its indicators/thresholds/backtest/accounting assumptions;
5. only then expose strategy recommendations for that asset.

Do not infer that an ETH strategy is valid for BTC/SOL/ADA simply because the software can accept another symbol.

---

## 7. Priority order across both products

When roadmap items compete, use this order unless a repository's canonical active authority requires otherwise:

1. prevent incorrect financial/accounting results;
2. prevent incorrect strategy/algorithm decisions;
3. prevent important data loss or false durable-save states;
4. complete normal standalone daily/as-needed workflows;
5. complete real production data paths;
6. stabilize real use;
7. reduce duplicate manual work;
8. integrate Finance and CoinDCA;
9. converge secondary UX details;
10. expand to additional coins/features;
11. hardening/scale work without a production-realistic trigger.

---

## 8. Idea intake during active development

New ideas are welcome but must not silently enter active scope.

Classify them as:

```text
V1_CRITICAL
PRODUCT_BACKLOG
EXPERIMENT
HARDENING
OUT_OF_SCOPE
```

Use these questions:

1. Does the idea fix a realistic risk of wrong money, wrong strategy decision, wrong accounting, important data loss, or inability to perform the current primary workflow?
2. Is it required by an already-frozen current acceptance gate?
3. Is it inside the current capability boundary?
4. Can it wait until the current task reaches a safe boundary?

If it can wait, record it rather than implementing it inside the active task.

---

## 9. Explicit non-goals for the current roadmap

Unless separately promoted later, this roadmap does not authorize:

- direct Binance trading;
- automatic order placement/cancellation;
- withdrawal permissions;
- generic exchange platform architecture;
- generic multi-user SaaS;
- enterprise IAM;
- premature provider abstraction;
- multi-coin strategy cloning;
- merging Finance and CoinDCA databases;
- monorepo migration;
- mass renaming of legacy ETH technical identifiers;
- rebuilding stable financial logic for design consistency;
- speculative scalability work.

---

## 10. Target end state

The desired long-term relationship is:

```text
                   PERSONAL FINANCE HUB
                           │
             ┌─────────────┴─────────────┐
             │                           │
          FINANCE                     COINDCA
             │                           │
 overall personal finance          crypto strategy
 cash flow / debts                 market analysis
 assets / net worth                Buy Score / regime
 portfolio allocation              ladders / accounting
             │                           │
             └──────────┬────────────────┘
                        │
                 shared facts only
                        │
                    BINANCE
                 read-only facts
```

In plain language:

- **Finance answers:** “My overall financial position is what?”
- **CoinDCA answers:** “Given the validated crypto strategy, what is the current investment context and how is my strategy capital/accounting positioned?”
- **Binance answers:** “What market/account executions actually exist on the exchange?”
- **The Hub answers:** “Show me the useful combined picture in one place.”

---

## 11. Agent start rule

When an AI agent reads this file during an existing session:

> **Do not implement this roadmap automatically.** First identify the repository's current active task/session and canonical authority. If current work is unfinished, continue that work unchanged. Treat this document as future coordination context until the prerequisites and owner promotion rule for the relevant stage are satisfied.

When starting new work from this roadmap:

> Select only the next eligible stage for the current repository. Do not create tasks for later stages, do not expand scope because future integrations are described here, and do not modify the other repository unless the owner has explicitly opened an integration phase.

---

## 12. Current checkpoint

### Reconciliation — 2026-09-05 (`DEC-041`)

This roadmap predates coin-repo `DEC-031` (official verdict `DO_NOT_BUILD`) and `DEC-040`
(Owner selects **L-1**). Per §2.3 (last paragraph) and §12 below, the coin repository's canonical
authority wins, and the conflict is reconciled **explicitly** here rather than by silently
changing scope.

**Superseded for CoinDCA** (no longer implementation-authoritative):

- §2.2(2) — "current verified strategy" (corrected in place above);
- §3.2 — "Active strategy: ETH Strategy V2.1.5" and "validated" (corrected in place above);
- §3.2 ownership list — `Buy Score`, `regime`, `buy zones/ladders`,
  `ETH strategy recommendations`;
- §5.2 — `Buy Score`, `regime`, `GO/WAIT`, `ladder status` as CoinDCA identity;
- Stage 1, "CoinDCA Stream — V1 production completion", items 3–6 and its `Conceptual path`
  block (`Real market data → … → Buy Score / regime → recommendation / budget → web`) — this
  defined V1 as V2.1.5 strategy productization, which `DO_NOT_BUILD` prohibits;
- §10 — "Given the **validated** crypto strategy…" (false premise);
- §12 CoinDCA checkpoint — "Current active strategy: ETH Strategy V2.1.5".

**Unchanged and still in force:** §7 priority order (its item 1, *prevent incorrect
financial/accounting results*, is L-1's top priority too); §8 idea intake; §9 non-goals; §11
agent start rule; §2.2(3) and §9 prohibition on mass-renaming legacy technical identifiers
(`eth_dca_os` and friends stay); and **all Finance-stream content**, which this reconciliation
does not touch.

**Active CoinDCA direction:** a personal DCA-discipline ledger — monthly budget · purchase
schedule · user-dated trade recording · cost basis recomputed from (opening balance + trades) ·
durable persistence. Buy Score may appear only as **descriptive, retrospective** research, never
as a recommendation.

Authority: coin repo `PROJECT/PROJECT_DECISIONS.md` `DEC-041`
(report: `docs/reviews/L1-CANONICAL-TRANSITION-PROPOSAL.md`).

---

### Checkpoint — 2026-09-02 (historical)

This checkpoint is descriptive and must not override newer repository evidence.
Superseded in part by the Reconciliation block above.

### CoinDCA

- Product direction: rename presentation from ETH DCA OS / ETH DCA Tracker to **CoinDCA**.
- Current active strategy: **ETH Strategy V2.1.5**.
- Multi-coin strategy: **not implemented**.
- DATA and WEB remain distinct streams that later meet at the end-to-end Golden path.
- T-09B durable Firebase persistence is at production-verification stage; do not contaminate it with roadmap expansion.
- Real market-data production completion remains a major next standalone-product milestone after persistence is safely closed.

### Finance

- Finance remains an independent personal-finance product.
- Current priority: its existing Phase 1 scope and real daily usability.
- Its neutral, compact personal-finance UI language is the reference direction for later CoinDCA visual convergence.
- Do not add CoinDCA strategy/accounting responsibilities to Finance Phase 1.

### Integration

- No shared database, portal, Binance account sync, or multi-coin strategy work should start merely because this document has been committed.
- Integration begins only after the staged prerequisites above are met and the owner explicitly promotes the relevant phase.

---

**End of roadmap.**
