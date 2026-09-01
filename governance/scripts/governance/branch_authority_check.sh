#!/usr/bin/env bash
# Branch authority check (AI Engineering V4.3 overlay).
#
# Confirms, before reading project state and before a commit, that:
#   1. work is on the authorised branch (not the default branch);
#   2. the branch is not BEHIND its upstream, and a detached HEAD matches TARGET_SHA;
#   3. the tracked worktree is clean;
#   4. divergence from the DYNAMICALLY resolved default branch is within the three
#      Integration Decision thresholds (governance/v4/CORE/GOVERNANCE_V4.md II.3);
#   5. production paths declared in PROJECT/PRODUCTION_PATHS.md are unchanged,
#      unless the caller explicitly allows production changes.
#
# Checks 2-4 were reconciled in from the V4.3 source pack on 2026-09-01.
#
# Usage:
#   branch_authority_check.sh [--expect-branch <name>] [--allow-production-diff] [--base <sha>]
#
# Env:
#   TARGET_SHA           required when HEAD is detached
#   STRICT_DIVERGENCE=1  turn INTEGRATION_DECISION_REQUIRED into a failure
#   AHEAD_MAX            default 10
#   AGE_DAYS_MAX         default 3
#   LOC_MAX              default 5000
#
# Exit 0 = PASS, 1 = FAIL.
#
# The default branch is resolved from origin/HEAD. It is NEVER assumed to be 'main'.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "BRANCH AUTHORITY: FAIL"
    echo "- not inside a git repository"
    exit 1
}
cd "$REPO_ROOT" || exit 1

PRODUCTION_PATHS=(src/eth_dca_os webapp pyproject.toml pyproject.lock)

AHEAD_MAX="${AHEAD_MAX:-10}"
AGE_DAYS_MAX="${AGE_DAYS_MAX:-3}"
LOC_MAX="${LOC_MAX:-5000}"

EXPECT_BRANCH=""
ALLOW_PROD_DIFF=0
BASE=""

while [ $# -gt 0 ]; do
    case "$1" in
        --expect-branch) EXPECT_BRANCH="${2:-}"; shift 2 ;;
        --allow-production-diff) ALLOW_PROD_DIFF=1; shift ;;
        --base) BASE="${2:-}"; shift 2 ;;
        *) echo "unknown argument: $1" >&2; exit 1 ;;
    esac
done

ERRORS=()
CURRENT="$(git rev-parse --abbrev-ref HEAD)"

echo "branch            = $CURRENT"

if [ -n "$EXPECT_BRANCH" ] && [ "$CURRENT" != "$EXPECT_BRANCH" ]; then
    ERRORS+=("on branch '$CURRENT' but authorised branch is '$EXPECT_BRANCH'")
fi

case "$CURRENT" in
    main|master)
        ERRORS+=("working directly on '$CURRENT'; feature work must not commit to the default branch")
        ;;
esac

# --- Branch authority proper (V4.3 source pack semantics) --------------------
# Fetch so that "behind upstream" and "ahead of default" are measured, not assumed.
if git remote get-url origin >/dev/null 2>&1; then
    if ! git fetch origin --prune --quiet 2>/dev/null; then
        echo "MODE_NOTE        = STALE_REMOTE (fetch failed; offline or no permission)"
    fi

    DEFAULT_REF="$(git symbolic-ref -q refs/remotes/origin/HEAD || true)"
    if [ -z "$DEFAULT_REF" ]; then
        git remote set-head origin --auto >/dev/null 2>&1 || true
        DEFAULT_REF="$(git symbolic-ref -q refs/remotes/origin/HEAD || true)"
    fi

    if [ -z "$DEFAULT_REF" ]; then
        ERRORS+=("BRANCH AUTHORITY UNRESOLVED: origin/HEAD is undefined. Run 'git remote set-head origin --auto'. Do not guess 'main'.")
    else
        DEFAULT_BRANCH="${DEFAULT_REF#refs/remotes/origin/}"
        echo "default branch    = $DEFAULT_BRANCH (resolved, not assumed)"

        if git symbolic-ref -q HEAD >/dev/null; then
            if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
                BEHIND="$(git rev-list --count HEAD..@{u})"
                echo "behind upstream   = $BEHIND"
                if [ "$BEHIND" -ne 0 ]; then
                    ERRORS+=("local branch is BEHIND upstream by $BEHIND commit(s); project state must not be read in this condition")
                fi
            else
                ERRORS+=("attached branch has no upstream")
            fi
        else
            echo "mode              = detached"
            if [ -z "${TARGET_SHA:-}" ]; then
                ERRORS+=("detached HEAD requires TARGET_SHA")
            else
                TARGET_FULL="$(git rev-parse "$TARGET_SHA" 2>/dev/null || true)"
                if [ -z "$TARGET_FULL" ] || [ "$(git rev-parse HEAD)" != "$TARGET_FULL" ]; then
                    ERRORS+=("detached HEAD does not match TARGET_SHA")
                fi
            fi
        fi

        # Integration Decision thresholds - all three, measured against origin/<default>.
        DEFBASE="origin/$DEFAULT_BRANCH"
        AHEAD="$(git rev-list --count "$DEFBASE..HEAD" 2>/dev/null || echo 0)"
        AGE_DAYS=0
        LOC=0
        if [ "$AHEAD" -gt 0 ]; then
            FIRST="$(git rev-list "$DEFBASE..HEAD" | tail -1)"
            FIRST_TS="$(git show -s --format=%ct "$FIRST")"
            AGE_DAYS=$(( ( $(date +%s) - FIRST_TS ) / 86400 ))
            SHORTSTAT="$(git diff --shortstat "$DEFBASE...HEAD" 2>/dev/null || true)"
            INS="$(printf '%s' "$SHORTSTAT" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+' || true)"
            DEL="$(printf '%s' "$SHORTSTAT" | grep -oE '[0-9]+ deletion'  | grep -oE '[0-9]+' || true)"
            LOC=$(( ${INS:-0} + ${DEL:-0} ))
        fi
        echo "ahead of default  = $AHEAD commit(s)"
        echo "divergence age    = $AGE_DAYS day(s)"
        echo "divergence LOC    = $LOC"

        TRIGGERED=""
        [ "$AHEAD"    -gt "$AHEAD_MAX"    ] && TRIGGERED="$TRIGGERED ahead>$AHEAD_MAX"
        [ "$AGE_DAYS" -gt "$AGE_DAYS_MAX" ] && TRIGGERED="$TRIGGERED age>${AGE_DAYS_MAX}d"
        [ "$LOC"      -gt "$LOC_MAX"      ] && TRIGGERED="$TRIGGERED loc>$LOC_MAX"

        if [ -n "$TRIGGERED" ]; then
            echo "INTEGRATION_DECISION_REQUIRED:$TRIGGERED"
            echo "    Owner must choose: integrate/merge | cut scope | accept the divergence"
            echo "    with a stated reason and a re-evaluation date. Do not continue silently."
            if [ "${STRICT_DIVERGENCE:-0}" = "1" ]; then
                ERRORS+=("INTEGRATION_DECISION_REQUIRED and STRICT_DIVERGENCE=1")
            fi
        else
            echo "integration       = INTEGRATION_DECISION_REQUIRED=NO"
        fi
    fi
else
    echo "remote            = none (LOCAL_ONLY)"
fi

# Tracked worktree must be clean; runner caches are untracked and do not count.
WT_STATUS="$(git status --short --untracked-files=no)"
if [ -n "$WT_STATUS" ]; then
    echo "tracked worktree  = DIRTY"
    echo "$WT_STATUS" | sed 's/^/    /'
else
    echo "tracked worktree  = CLEAN"
fi

# Production-path diff, measured not asserted.
if [ -n "$BASE" ]; then
    RANGE="$BASE..HEAD"
    PROD_DIFF="$(git diff --shortstat "$BASE"..HEAD -- "${PRODUCTION_PATHS[@]}")"
else
    RANGE="working tree + index"
    PROD_DIFF="$(git status --porcelain -- "${PRODUCTION_PATHS[@]}")"
fi

echo "production range  = $RANGE"
echo "production paths  = ${PRODUCTION_PATHS[*]}"

if [ -n "$PROD_DIFF" ]; then
    echo "production diff   = NON-EMPTY"
    echo "$PROD_DIFF" | sed 's/^/    /'
    if [ "$ALLOW_PROD_DIFF" -eq 0 ]; then
        ERRORS+=("production paths changed but --allow-production-diff was not passed")
    fi
else
    echo "production diff   = EMPTY"
fi

if [ "${#ERRORS[@]}" -gt 0 ]; then
    echo "BRANCH AUTHORITY: FAIL"
    for e in "${ERRORS[@]}"; do echo "- $e"; done
    exit 1
fi

echo "BRANCH AUTHORITY: PASS"
exit 0
