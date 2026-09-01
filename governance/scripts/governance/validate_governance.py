#!/usr/bin/env python3
"""Validate AI Engineering V4.3 overlay invariants.

Complements — does not replace — the V3.2 validators. Those check V3.2 structure,
routing and roadmap sync; this one checks the V4.3 invariants declared in AGENTS.md
and governance/v4/CORE/.

Deliberately reports the SIZE of every set it examines. A validator that passes
while having examined nothing is not a passing validator
(governance/v4/CORE/STATE_AUTHORITY.md, "Vacuous Validation").
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "governance" / "v4" / "CORE"
PROJECT = ROOT / "PROJECT"

CORE_FILES = [
    "CAPABILITY_MODEL.md",
    "GOVERNANCE_V4.md",
    "DELIVERY_LOOP.md",
    "STATE_AUTHORITY.md",
    "RISK_MODEL.md",
    "REVIEW_PROTOCOL.md",
    "PRODUCTION_PATH_RULE.md",
]

PROJECT_FILES = [
    "PROJECT_PROFILE.md",
    "PROJECT_PROGRESS.md",
    "PROJECT_DECISIONS.md",
    "CAPABILITY_REGISTRY.md",
    "PRODUCTION_PATHS.md",
    "REVIEW_BUDGET_LEDGER.md",
    "HARDENING_BACKLOG.md",
]

ADAPTERS = ["CLAUDE.md", "CODEX.md"]

# CORE must stay project-agnostic. These tokens are project values for THIS repo.
PROJECT_LEAK_TOKENS = [
    "WP-A", "WP-B", "WP-C", "WP-D", "T-06", "GATE-A",
    "ETHUSDT", "BTCUSDT", "Binance", "binance",
    "eth_dca_os", "OSCORE", "Buy Score",
    "F-E2A1", "F-PRE008", "RSK-0", "DEC-0",
]

HARD_STOPS = [
    "OWNER_DECISION_REQUIRED",
    "ARCHITECTURE_CHANGE_REQUIRED",
    "DATA_INTEGRITY_RISK",
    "CHANGE_BUDGET_EXCEEDED",
    "GOLDEN_PASS",
]

errors: list[str] = []
notes: list[str] = []
counts: dict[str, int] = {}


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# --- 1. canonical entry point -------------------------------------------------
agents = ROOT / "AGENTS.md"
if not agents.exists():
    errors.append("AGENTS.md missing: no canonical AI entry point")
    agents_text = ""
else:
    agents_text = read(agents)
    for f in CORE_FILES:
        if f not in agents_text:
            errors.append(f"AGENTS.md does not reference CORE file in authority order: {f}")
counts["entry_point_core_refs"] = len(CORE_FILES)

# --- 2. CORE present and project-agnostic ------------------------------------
core_checked = 0
for f in CORE_FILES:
    p = CORE / f
    if not p.exists():
        errors.append(f"CORE file missing: {p.relative_to(ROOT)}")
        continue
    core_checked += 1
    body = read(p)
    for tok in PROJECT_LEAK_TOKENS:
        if tok in body:
            errors.append(
                f"CORE/PROJECT boundary violated: '{tok}' appears in {p.relative_to(ROOT)}"
            )
counts["core_files_checked"] = core_checked

# --- 3. PROJECT canonical files ----------------------------------------------
project_checked = 0
for f in PROJECT_FILES:
    p = PROJECT / f
    if not p.exists():
        errors.append(f"PROJECT file missing: PROJECT/{f}")
    else:
        project_checked += 1
counts["project_files_checked"] = project_checked

# --- 4. adapters hold no independent authority -------------------------------
adapters_checked = 0
for f in ADAPTERS:
    p = ROOT / f
    if not p.exists():
        errors.append(f"adapter missing: {f}")
        continue
    adapters_checked += 1
    body = read(p)
    if "AGENTS.md" not in body:
        errors.append(f"adapter {f} does not point at AGENTS.md")
    head = body[:1200]
    if "ADAPTER" not in head.upper():
        errors.append(f"adapter {f} does not declare itself an ADAPTER near the top")
    for phrase in ("create tasks", "repair or review budget"):
        if phrase not in body:
            errors.append(f"adapter {f} missing adapter constraint mentioning: {phrase}")
counts["adapters_checked"] = adapters_checked

# --- 5. five canonical hard-stops --------------------------------------------
loop = CORE / "DELIVERY_LOOP.md"
if loop.exists():
    body = read(loop)
    for hs in HARD_STOPS:
        if hs not in body:
            errors.append(f"DELIVERY_LOOP.md missing canonical hard-stop: {hs}")
    if "UNAUTHORIZED_STOP" not in body:
        errors.append("DELIVERY_LOOP.md missing UNAUTHORIZED_STOP rule")
counts["hard_stops_checked"] = len(HARD_STOPS)

# --- 5b. invariants reconciled from the V4.3 source pack (2026-09-01) --------
# The overlay was first authored without the source pack present, and lost normative
# content. These markers keep the restored invariants from being silently dropped again.
SOURCE_INVARIANTS = {
    "GOVERNANCE_V4.md": [
        "MAX(Local Risk, Blast Radius",
        "INTEGRATION_DECISION_REQUIRED",
        "ACCEPT_AS_IS | DESCOPE | OWNER_EXTENSION",
        "task creation approval != repair-budget allocation approval",
        "ENVIRONMENT_REVERIFY_REQUIRED",
        "POLICY_ADOPTED",
        "FULLY_ENFORCED",
    ],
    "CAPABILITY_MODEL.md": [
        "PENDING_OWNER_DATA",
        "INDEPENDENT LIFECYCLE",
        "OWNER_ASSIGNMENT_REQUIRED",
        "base_sha",
        "migration_status",
    ],
    "DELIVERY_LOOP.md": [
        "PROVISIONAL",
        "SILENT_ERROR_RATE",
        "ORDER_ACCOUNTING_RATE",
        "MANUAL_WORK_REDUCTION",
        "EXCEPTION_FIRST",
        "GOLDEN_BASELINE_SHA",
    ],
    "RISK_MODEL.md": ["Blast Radius", "MAX(Local Risk"],
    "REVIEW_PROTOCOL.md": ["cumulative repair diff", "NOT_ELIGIBLE_FOR_FREEZE"],
    "PRODUCTION_PATH_RULE.md": ["BUSINESS STATE"],
    "STATE_AUTHORITY.md": ["READY_FOR_REVIEW", "ELIGIBLE_FOR_FREEZE", "FROZEN"],
}
invariants_checked = 0
for fname, markers in SOURCE_INVARIANTS.items():
    p_inv = CORE / fname
    if not p_inv.exists():
        continue
    body_inv = read(p_inv)
    for marker in markers:
        invariants_checked += 1
        if marker not in body_inv:
            errors.append(
                f"source-pack invariant lost from {fname}: missing '{marker}'"
            )
counts["source_invariants_checked"] = invariants_checked

if agents_text and "branch_authority_check.sh" not in agents_text:
    errors.append("AGENTS.md does not require the branch authority check before reading state")

# --- 6. budget ledger must not silently reset --------------------------------
ledger = PROJECT / "REVIEW_BUDGET_LEDGER.md"
if ledger.exists():
    body = read(ledger)
    if "LINEAGE ROOT" not in body:
        errors.append("REVIEW_BUDGET_LEDGER.md declares no LINEAGE ROOT")
    if "BASELINE SHA" not in body:
        errors.append("REVIEW_BUDGET_LEDGER.md declares no BASELINE SHA")
    if not re.search(r"MIGRATION_UNCERTAINTY|CURRENT BUDGET REMAINING", body):
        errors.append(
            "REVIEW_BUDGET_LEDGER.md states neither a remaining budget nor MIGRATION_UNCERTAINTY"
        )
    lineage_roots = len(re.findall(r"LINEAGE ROOT\s*=", body))
    counts["budget_lineage_roots"] = lineage_roots
    if lineage_roots == 0:
        errors.append("REVIEW_BUDGET_LEDGER.md: 0 lineage roots recorded")

# --- 7. every hardening item carries a re-trigger ----------------------------
backlog = PROJECT / "HARDENING_BACKLOG.md"
if backlog.exists():
    body = read(backlog)
    items = re.findall(r"^## (H-\d+)\b", body, flags=re.M)
    counts["hardening_items"] = len(items)
    blocks = re.split(r"^## (?=H-\d+)", body, flags=re.M)[1:]
    for block in blocks:
        item_id = block.split(" ", 1)[0].strip()
        if "RE_TRIGGER_CONDITION" not in block:
            errors.append(f"hardening item {item_id} has no RE_TRIGGER_CONDITION")
    if not items:
        notes.append("hardening backlog is empty (0 items) — nothing to verify")

# --- 8. production paths declared --------------------------------------------
pp = PROJECT / "PRODUCTION_PATHS.md"
if pp.exists():
    body = read(pp)
    if "GOLDEN_BASELINE_SHA" not in body:
        errors.append("PRODUCTION_PATHS.md does not state GOLDEN_BASELINE_SHA (or its absence)")
    rows = [ln for ln in body.splitlines() if ln.startswith("| `") and "|" in ln[3:]]
    counts["production_path_rows"] = len(rows)
    if len(rows) == 0:
        errors.append("PRODUCTION_PATHS.md declares 0 paths")

# --- 9. vacuous-pass detection in sibling validators --------------------------
tasks_dir = ROOT / "docs" / "tasks"
task_files = [p for p in tasks_dir.glob("*.md") if p.name != "README.md"]
legacy_glob = list(tasks_dir.glob("TASK-*.md"))
counts["task_files_present"] = len(task_files)
counts["task_files_matching_legacy_glob"] = len(legacy_glob)
if task_files and not legacy_glob:
    notes.append(
        f"vacuous-pass risk: {len(task_files)} task file(s) exist but validate_evidence.py "
        "and validate_task_completion.py glob 'TASK-*.md' and therefore check 0 records "
        "(routed as HARDENING H-08; not a failure of this validator)"
    )

# --- report -------------------------------------------------------------------
print("GOVERNANCE V4.3: " + ("FAIL" if errors else "PASS"))
for k, v in counts.items():
    print(f"  checked {k} = {v}")
for n in notes:
    print(f"  NOTE: {n}")
for e in errors:
    print(f"- {e}")
sys.exit(1 if errors else 0)
