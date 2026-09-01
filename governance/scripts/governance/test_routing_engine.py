#!/usr/bin/env python3
"""Self-contained regression tests for GOVDEF-001 (routing_engine.py floating-point
boundary defect) and for the manual-override verification mechanism added to
validate_routing.py at MICRO-GOVDEF-001.

No external test framework required (mirrors the style of the other
governance/scripts/governance/validate_*.py scripts): run directly with

    python governance/scripts/governance/test_routing_engine.py

Exits 0 and prints 'ROUTING ENGINE TESTS: PASS (<n> checks)' on success;
prints every failing assertion and exits 1 otherwise.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from routing_engine import route, tier_from_score, effort_from_score
import validate_routing as vr

ROOT = Path(__file__).resolve().parents[3]

failures = []
checks = 0


def check(label, condition):
    global checks
    checks += 1
    if not condition:
        failures.append(label)


# ---------------------------------------------------------------------------
# 1. GOVDEF-001 boundary regression: model_score (Tier) boundaries at 1/2/3
# ---------------------------------------------------------------------------

# The originally reported case (WP-A2): D=2,R=2,B=2,A=1,X=3.
# Raw float value is 1.9999999999999998; displayed value is 2.0.
# AGENT_CAPABILITY_MATRIX.md: 2.00-2.99 -> Tier C. Must route to C, not B.
out = route(2, 2, 2, 1, 3, 0, 0, 0, 0, 0)
check("GOVDEF-001 original case (D2R2B2A1X3) model_score displays 2.0", out['model_score'] == 2.0)
check("GOVDEF-001 original case routes to Tier C (was B pre-fix)", out['tier'] == 'C')
check("GOVDEF-001 original case base_tier is C", out['base_tier'] == 'C')

# Just below the Tier B/C boundary (true value 1.99, no float noise): must stay B.
# D=1,R=3,B=2,A=1,X=1 -> .25+.75+.40+.15+.15 = 1.70 -- pick an exact sub-2 combo instead.
out = route(1, 2, 2, 1, 1, 0, 0, 0, 0, 0)  # .25+.50+.40+.15+.15 = 1.45
check("just below Tier boundary (1.45) stays Tier B", out['tier'] == 'B')

# Exactly at the boundary with NO float noise (D2R2B2A2X0 -> ms=2.0 exact, e.g. WP-B3's case).
out = route(2, 2, 2, 2, 2, 0, 0, 0, 0, 0)  # .5+.5+.4+.3+.3 = 2.0
check("exact-representation 2.0 (no noise) still routes to Tier C", out['tier'] == 'C')

# Another float-noise-affected combo at the Tier C/D boundary (3.0): D3R4B4A1X2 -> raw 2.9999999999999996.
out = route(3, 4, 4, 1, 2, 0, 0, 0, 0, 0)
check("Tier C/D boundary float-noise case (raw 2.999...6) displays 3.0", out['model_score'] == 3.0)
check("Tier C/D boundary float-noise case routes to Tier D, not C", out['tier'] == 'D')

# Just above a boundary, well clear of any float noise (D3R2B3A1X1 -> .75+.5+.6+.15+.15 = 2.15).
out = route(3, 2, 3, 1, 1, 0, 0, 0, 0, 0)
check("just above Tier B/C boundary (2.15) is Tier C", out['tier'] == 'C')

# ---------------------------------------------------------------------------
# 2. GOVDEF-001 boundary regression: effort_score boundaries at .8/1.6/2.4/3.2
# ---------------------------------------------------------------------------

# Float-noise-affected effort boundary: U1V4H1C1F1 -> raw 1.5999999999999999, displays 1.6.
out = route(0, 0, 0, 0, 0, 1, 4, 1, 1, 1)
check("effort boundary float-noise case (raw 1.5999...9) displays 1.6", out['effort_score'] == 1.6)
check("effort boundary float-noise case routes to 'high', not 'medium'", out['effort'] == 'high')

# Exact effort boundaries reachable with integer inputs, no float noise possible.
out = route(0, 0, 0, 0, 0, 4, 0, 0, 0, 0)  # es = .20*4 = 0.8 exactly
check("effort exactly at 0.8 boundary is 'medium'", out['effort'] == 'medium')
out = route(0, 0, 0, 0, 0, 0, 0, 0, 4, 4)  # .15*4 + .25*4 = 0.6+1.0 = 1.6 exactly
check("effort exactly at 1.6 boundary (no noise) is 'high'", out['effort'] == 'high')
out = route(0, 0, 0, 0, 0, 4, 4, 4, 0, 0)  # .2*4*3 = 2.4 exactly
check("effort exactly at 2.4 boundary is 'xhigh'", out['effort'] == 'xhigh')
out = route(0, 0, 0, 0, 0, 4, 4, 4, 2, 2)  # .2*4*3 + .15*2 + .25*2 = 2.4+0.3+0.5 = 3.2 exactly
check("effort exactly at 3.2 boundary is 'max'", out['effort'] == 'max')

# ---------------------------------------------------------------------------
# 3. Full-space boundary sweep: displayed value and decided tier/effort must
#    NEVER disagree, across the entire valid input space (not just the
#    originally-reported case). This is the general regression that proves
#    the fix is not a special case for WP-A2.
# ---------------------------------------------------------------------------

mismatches = 0
for D in range(5):
    for R in range(5):
        for B in range(5):
            for A in range(5):
                for X in range(5):
                    out = route(D, R, B, A, X, 0, 0, 0, 0, 0)
                    if tier_from_score(out['model_score']) != out['base_tier']:
                        mismatches += 1
check("full D/R/B/A/X space: displayed model_score always agrees with decided base_tier", mismatches == 0)

mismatches = 0
for U in range(5):
    for V in range(5):
        for H in range(5):
            for C in range(5):
                for F in range(5):
                    out = route(0, 0, 0, 0, 0, U, V, H, C, F)
                    if effort_from_score(out['effort_score']) != out['effort']:
                        mismatches += 1
check("full U/V/H/C/F space: displayed effort_score always agrees with decided effort", mismatches == 0)

# ---------------------------------------------------------------------------
# 4. check_override(): valid manual override is accepted
# ---------------------------------------------------------------------------

router_out = route(2, 2, 2, 1, 3, 1, 3, 2, 3, 2)  # WP-A2's real inputs; router now says C/high natively
# Force a synthetic mismatch scenario: pretend the router still said B, to
# exercise the override path independently of whether WP-A2 itself still
# needs one after the fix.
synthetic_router_out = dict(router_out)
synthetic_router_out['tier'] = 'B'
synthetic_router_out['base_tier'] = 'B'
synthetic_router_out['model'] = 'Sonnet'

decisions_text_valid = "## DEC-999 — A synthetic decision for testing\n\nDecision:\nTest.\n"

valid_override_text = (
    "Manual Override:\n"
    "YES — DEC-999. Router thô trả Tier B do defect biên dấu phẩy động.\n\n"
    "Router Raw Output:\n"
    f"tier={synthetic_router_out['base_tier']}, model={synthetic_router_out['model']}, "
    f"base_tier={synthetic_router_out['base_tier']}, model_score={synthetic_router_out['model_score']}, "
    f"effort={synthetic_router_out['effort']}, effort_score={synthetic_router_out['effort_score']}, "
    f"model_floors=none, effort_floors=none, warnings=none\n"
)

accepted, messages = vr.check_override(valid_override_text, synthetic_router_out, 'C', synthetic_router_out['effort'], decisions_text_valid)
check("valid manual override (documented decision, authentic raw output, escalation only) is ACCEPTED", accepted)
check("accepted override returns exactly one acceptance message", len(messages) == 1)

# ---------------------------------------------------------------------------
# 5. check_override(): invalid manual override cases -- each must be rejected
# ---------------------------------------------------------------------------

# 5a. No override declared at all -- check_override must report "not declared" (empty messages).
accepted, messages = vr.check_override("Nothing here.", synthetic_router_out, 'C', synthetic_router_out['effort'], decisions_text_valid)
check("no Manual Override field -> not accepted", accepted is False)
check("no Manual Override field -> no messages (caller falls back to plain mismatch)", messages == [])

# 5b. Decision reference cited but not documented in PROJECT_DECISIONS.md.
undocumented_text = valid_override_text  # cites DEC-999
accepted, messages = vr.check_override(undocumented_text, synthetic_router_out, 'C', synthetic_router_out['effort'], "")  # empty decisions file
check("override citing an undocumented decision -> rejected", accepted is False)
check("undocumented decision produces an explanatory reason", any('DEC-999' in m and 'heading' in m for m in messages))

# 5c. Router Raw Output missing entirely.
no_raw_text = "Manual Override:\nYES — DEC-999. Some reason.\n"
accepted, messages = vr.check_override(no_raw_text, synthetic_router_out, 'C', synthetic_router_out['effort'], decisions_text_valid)
check("override with missing Router Raw Output -> rejected", accepted is False)
check("missing Router Raw Output produces an explanatory reason", any('Router Raw Output' in m for m in messages))

# 5d. Router Raw Output present but stale/fabricated (doesn't match fresh computation).
fabricated_text = (
    "Manual Override:\n"
    "YES — DEC-999. Fabricated baseline.\n\n"
    "Router Raw Output:\n"
    "tier=A, model=Haiku, base_tier=A, model_score=0.5, effort=low, effort_score=0.5, "
    "model_floors=none, effort_floors=none, warnings=none\n"
)
accepted, messages = vr.check_override(fabricated_text, synthetic_router_out, 'C', synthetic_router_out['effort'], decisions_text_valid)
check("override with fabricated/stale Router Raw Output -> rejected", accepted is False)
check("fabricated Router Raw Output produces an explanatory reason", any('stale or fabricated' in m for m in messages))

# 5e. Override attempts to DE-ESCALATE (claimed tier below the router's tier) -- must always fail,
#     even though the decision reference and raw output are otherwise perfectly valid.
deescalate_router_out = dict(router_out)
deescalate_router_out['tier'] = 'C'
deescalate_router_out['base_tier'] = 'C'
deescalate_router_out['model'] = 'Opus'
deescalate_text = (
    "Manual Override:\n"
    "YES — DEC-999. Attempt to downgrade.\n\n"
    "Router Raw Output:\n"
    f"tier=C, model=Opus, base_tier=C, model_score={deescalate_router_out['model_score']}, "
    f"effort={deescalate_router_out['effort']}, effort_score={deescalate_router_out['effort_score']}, "
    f"model_floors=none, effort_floors=none, warnings=none\n"
)
accepted, messages = vr.check_override(deescalate_text, deescalate_router_out, 'B', deescalate_router_out['effort'], decisions_text_valid)
check("override attempting to DE-ESCALATE Tier (C router -> claimed B) -> rejected", accepted is False)
check("de-escalation produces an explanatory reason", any('DE-ESCALATE' in m for m in messages))

# 5f. Malformed decision reference (does not match DEC-### pattern) is caught by the regex
#     itself -- the 'Manual Override: YES — ...' line simply won't match, so no override
#     is recognized and the plain mismatch path applies.
malformed_text = "Manual Override:\nYES — NOT-A-DECISION. bla\n"
accepted, messages = vr.check_override(malformed_text, synthetic_router_out, 'C', synthetic_router_out['effort'], decisions_text_valid)
check("malformed decision reference -> not recognized as an override", accepted is False)
check("malformed decision reference -> no messages (falls back to plain mismatch)", messages == [])

# ---------------------------------------------------------------------------
# 6. WP-A2 regression: still declares Tier C / Opus / high, override trace intact,
#    and the file now validates (with or without the override branch triggering).
# ---------------------------------------------------------------------------

wp_a2 = ROOT / 'docs/tasks/WP-A2-dau-noi-hang-muc-vao-pipeline.md'
if wp_a2.exists():
    text = wp_a2.read_text(errors='ignore')
    check("WP-A2 still declares Primary Agent Tier: C", bool(vr.re.search(r'Primary Agent Tier:\s*\nC\s*$', text, vr.re.M)))
    check("WP-A2 still declares Primary Effort: high", bool(vr.re.search(r'Primary Effort:\s*\nhigh\s*$', text, vr.re.M)))
    check("WP-A2 still declares Manual Override: YES — DEC-008", 'YES — DEC-008' in text)
    check("WP-A2 still declares its Router Raw Output trace", 'Router Raw Output:' in text)
    decisions_text = (ROOT / 'PROJECT/PROJECT_DECISIONS.md').read_text(encoding='utf-8', errors='ignore')
    file_errors, override_note, was_checked = vr.validate_file(wp_a2, decisions_text)
    check("WP-A2 validates with zero errors after the fix", file_errors == [])
else:
    check("WP-A2 task file exists", False)

# ---------------------------------------------------------------------------
# 7. Whole-roadmap regression: every real MAJOR task file must validate cleanly,
#    and routing must be unchanged for every task EXCEPT WP-A2 (Tier B -> C).
# ---------------------------------------------------------------------------

decisions_text = (ROOT / 'PROJECT/PROJECT_DECISIONS.md').read_text(encoding='utf-8', errors='ignore')
all_errors = []
checked_files = 0
for p in sorted((ROOT / 'docs/tasks').glob('*.md')):
    file_errors, override_note, was_checked = vr.validate_file(p, decisions_text)
    all_errors += file_errors
    if was_checked:
        checked_files += 1
check("every real MAJOR task file under docs/tasks/ validates with zero errors", all_errors == [])
check("at least the 16 known MAJOR task files were checked", checked_files >= 16)

# ---------------------------------------------------------------------------

if failures:
    print("ROUTING ENGINE TESTS: FAIL")
    for f in failures:
        print(f"- {f}")
    sys.exit(1)
print(f"ROUTING ENGINE TESTS: PASS ({checks} checks)")
