#!/usr/bin/env bash
# Task registry snapshot (AI Engineering V4.3 overlay).
#
# Prints a deterministic snapshot of the task registry so that a session can be
# checked for "no task ID was invented" by diffing a before/after pair.
#
# Usage:
#   task_registry_snapshot.sh              # snapshot the working tree
#   task_registry_snapshot.sh <sha>        # snapshot the tree at <sha>

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "not inside a git repository" >&2
    exit 1
}
cd "$REPO_ROOT" || exit 1

REF="${1:-}"

if [ -n "$REF" ]; then
    echo "# task registry snapshot @ $REF"
    FILES="$(git ls-tree -r --name-only "$REF" -- docs/tasks | grep -E '\.md$' | grep -v 'README\.md$' | sort)"
    ROADMAP="$(git show "$REF:PROJECT/PROJECT_PROGRESS.md" 2>/dev/null)"
else
    echo "# task registry snapshot @ working tree"
    FILES="$(find docs/tasks -name '*.md' ! -name 'README.md' | sort)"
    ROADMAP="$(cat PROJECT/PROJECT_PROGRESS.md 2>/dev/null)"
fi

echo
echo "## task definition files"
echo "$FILES"
echo
echo "count_task_files = $(printf '%s\n' "$FILES" | grep -c . )"

echo
echo "## task IDs in the roadmap table"
IDS="$(printf '%s\n' "$ROADMAP" \
    | grep -E '^\| *(DONE|PLANNED|READY|BLOCKED|IN_PROGRESS|DEFERRED|CANCELLED|NOT_PLANNED) *\|' \
    | awk -F'|' '{gsub(/^ +| +$/, "", $3); print $3}' \
    | sort -u)"
printf '%s\n' "$IDS"
echo
echo "count_roadmap_task_ids = $(printf '%s\n' "$IDS" | grep -c . )"
