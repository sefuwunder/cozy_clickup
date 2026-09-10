#!/bin/sh
# Refresh tasks.json (when the ClickUp fetcher is configured) and then
# send desktop reminders for tasks that are due soon.
#
# Environment:
#   CLICKUP_LIST_ID   your ClickUp list id (enables the refresh step)
#   CLICKUP_FETCH     path to the fetcher script
#                     (default: $HOME/workspace/skills/clickup/bin/clickup_tasks.py)
set -u
cd "$(dirname "$0")/.."

FETCH="${CLICKUP_FETCH:-$HOME/workspace/skills/clickup/bin/clickup_tasks.py}"
if [ -n "${CLICKUP_LIST_ID:-}" ] && [ -x "$FETCH" ]; then
    "$FETCH" --list "$CLICKUP_LIST_ID" --out tasks.json || echo "task refresh failed; using existing tasks.json"
fi

exec python3 tools/remind.py "$@"
