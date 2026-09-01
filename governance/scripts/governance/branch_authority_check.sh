#!/usr/bin/env bash
# Branch authority check (AI Engineering V4.3 overlay).
#
# Confirms, before a commit, that:
#   1. work is on the authorised branch (not the default branch);
#   2. production paths declared in PROJECT/PRODUCTION_PATHS.md are unchanged,
#      unless the caller explicitly allows production changes.
#
# Usage:
#   branch_authority_check.sh [--expect-branch <name>] [--allow-production-diff] [--base <sha>]
#
# Exit 0 = PASS, 1 = FAIL.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "BRANCH AUTHORITY: FAIL"
    echo "- not inside a git repository"
    exit 1
}
cd "$REPO_ROOT" || exit 1

PRODUCTION_PATHS=(src/eth_dca_os webapp pyproject.toml pyproject.lock)

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
