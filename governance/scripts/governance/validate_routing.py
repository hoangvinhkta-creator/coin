#!/usr/bin/env python3
"""Routing validator: every MAJOR task file's declared Tier/Effort must match the
deterministic router, UNLESS the mismatch is justified by a governance-approved
manual override that this module can independently verify (see check_override).
"""
from pathlib import Path
import re, sys
sys.path.insert(0, str(Path(__file__).parent))
from routing_engine import route, TIERS, EFF

ROOT = Path(__file__).resolve().parents[3]
TASKS_DIR = ROOT / 'docs/tasks'
DECISIONS_FILE = ROOT / 'PROJECT/PROJECT_DECISIONS.md'

DECISION_REF_RE = re.compile(r'DEC-\d{3,4}')


def decision_is_documented(ref, decisions_text):
    """A cited decision reference must exist as a top-level heading in
    PROJECT_DECISIONS.md. This is a generic format/existence check -- it does
    not special-case any specific decision number."""
    return re.search(rf'(?m)^##\s+{re.escape(ref)}\b', decisions_text) is not None


def parse_router_raw_output(line):
    """Parse a 'Router Raw Output:' line of the form
    'tier=B, model=Sonnet, base_tier=B, model_score=2.0, effort=high,
    effort_score=2.15, model_floors=none, effort_floors=none, warnings=none'
    into a dict. Unknown/extra keys are ignored by callers."""
    out = {}
    for k, v in re.findall(r'(\w+)\s*=\s*([^\s,]+)', line):
        out[k] = v
    return out


def extract_routing_inputs(text):
    """Return (vals, cats, missing_field_errors) for a MAJOR task file's body."""
    vals = {}
    errors = []
    for k in 'DRBAXUVHCF':
        m = re.search(rf'^\s*{k}:\s*([0-4])\s*$', text, re.M)
        if not m:
            errors.append(f"missing/invalid {k} (must be integer 0-4)")
        else:
            vals[k] = int(m.group(1))
    cm = re.search(r'Routing Categories:\s*\n([^\n]+)', text, re.I)
    cats = [] if not cm else [x.strip() for x in cm.group(1).split(',')]
    return vals, cats, errors


def check_override(text, out, got_tier, got_effort, decisions_text):
    """Decide whether a Tier/Effort mismatch against the freshly computed
    router output (`out`) is covered by a valid manual override declared in
    the task file's own text.

    Returns (accepted, messages):
      accepted=True  -> messages is a single-element list with an acceptance note
      accepted=False -> messages lists every reason the override was rejected
                         (empty list means: no override was declared at all)

    An override is accepted ONLY if all of the following hold:
      1. A 'Manual Override:' field exists and starts with 'YES' followed by
         a decision reference matching DEC-\\d{3,4} (no hard-coded DEC number).
      2. That decision reference exists as a heading in PROJECT_DECISIONS.md
         (the override is governance-documented, not just asserted in-file).
      3. A 'Router Raw Output:' field exists and its declared tier/model_score/
         effort/effort_score exactly match what routing_engine.route() computes
         RIGHT NOW from this file's own Routing Inputs -- so the override's
         claimed baseline cannot be stale or fabricated.
      4. The override only ESCALATES: the file's declared Tier/Effort must be
         >= the router's tier/effort in the TIERS/EFF ordering, never lower.
         This mirrors the existing floor mechanism (max_tier/max_eff only ever
         raises rigor) and is the general rule that prevents an override from
         ever being used to weaken a task's routing.
    """
    mo = re.search(r'Manual Override:\s*\n\s*YES\s*[—\-]\s*(DEC-\d{3,4})', text, re.I)
    if not mo:
        return False, []

    reasons = []
    decision_ref = mo.group(1).upper()

    if not DECISION_REF_RE.fullmatch(decision_ref):
        reasons.append(f"Manual Override decision reference {decision_ref!r} is not a valid DEC-### reference")

    if not decision_is_documented(decision_ref, decisions_text):
        reasons.append(
            f"Manual Override cites {decision_ref} but no '## {decision_ref}' heading exists in "
            f"{DECISIONS_FILE.relative_to(ROOT)}"
        )

    rro = re.search(r'Router Raw Output:\s*\n([^\n]+)', text, re.I)
    if not rro:
        reasons.append("Manual Override declared but 'Router Raw Output' field is missing")
    else:
        raw = parse_router_raw_output(rro.group(1))
        expected = {
            'tier': out['base_tier'],
            'model_score': str(out['model_score']),
            'effort': out['effort'],
            'effort_score': str(out['effort_score']),
        }
        for field, actual in expected.items():
            declared = raw.get(field)
            if declared != actual:
                reasons.append(
                    f"Manual Override 'Router Raw Output' field {field}={declared!r} does not match the "
                    f"freshly computed router output {field}={actual!r} for the declared Routing Inputs "
                    f"-- override baseline is stale or fabricated"
                )

    if got_tier in TIERS and TIERS.index(got_tier) < TIERS.index(out['tier']):
        reasons.append(
            f"Manual Override attempts to DE-ESCALATE Tier ({out['tier']} -> {got_tier}); "
            f"overrides may only raise Tier, never lower it"
        )
    if got_effort in EFF and EFF.index(got_effort) < EFF.index(out['effort']):
        reasons.append(
            f"Manual Override attempts to DE-ESCALATE Effort ({out['effort']} -> {got_effort}); "
            f"overrides may only raise Effort, never lower it"
        )

    if reasons:
        return False, reasons
    return True, [f"ACCEPTED manual override {decision_ref} (router={out['tier']}/{out['effort']} -> approved {got_tier}/{got_effort})"]


def validate_file(path, decisions_text):
    """Return (errors: list[str], override_note: str|None, checked: bool)."""
    text = path.read_text(errors='ignore')
    if not re.search(r'Task Mode:\s*\nMAJOR\b', text, re.I):
        return [], None, False

    vals, cats, field_errors = extract_routing_inputs(text)
    errors = [f"{path}: {e}" for e in field_errors]
    if len(vals) != 10:
        return errors, None, True

    out = route(**vals, categories=cats)
    tm = re.search(r'Primary Agent Tier:\s*\n([^\n]+)', text, re.I)
    em = re.search(r'Primary Effort:\s*\n([^\n]+)', text, re.I)
    got_t = tm.group(1).strip() if tm else ''
    got_e = em.group(1).strip().lower() if em else ''

    if got_t == out['tier'] and got_e == out['effort']:
        return errors, None, True

    accepted, messages = check_override(text, out, got_t, got_e, decisions_text)
    if accepted:
        return errors, f"{path}: {messages[0]}", True

    if messages:
        # A Manual Override was declared but failed verification -- report exactly
        # why, do not fall back to the generic mismatch message.
        errors += [f"{path}: {m}" for m in messages]
    else:
        # No override declared at all -- plain unapproved mismatch.
        if got_t != out['tier']:
            errors.append(f"{path}: Tier {got_t!r} != router {out['tier']}")
        if got_e != out['effort']:
            errors.append(f"{path}: Effort {got_e!r} != router {out['effort']}")
    return errors, None, True


def main():
    decisions_text = DECISIONS_FILE.read_text(encoding='utf-8', errors='ignore') if DECISIONS_FILE.exists() else ''
    errors = []
    overrides = []
    checked = 0
    for p in sorted(TASKS_DIR.glob('*.md')):
        file_errors, override_note, was_checked = validate_file(p, decisions_text)
        errors += file_errors
        if was_checked:
            checked += 1
        if override_note:
            overrides.append(override_note)

    if errors:
        print('ROUTING VALIDATION: FAIL')
        print('\n'.join('- ' + e for e in errors))
        return 1

    for o in overrides:
        print('- ' + o)
    print(f'ROUTING VALIDATION: PASS ({checked} MAJOR task file(s) checked, {len(overrides)} accepted manual override(s))')
    return 0


if __name__ == '__main__':
    sys.exit(main())
