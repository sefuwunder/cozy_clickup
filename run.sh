#!/bin/sh
# Cozy ClickUp: fetch tasks, then show them in a cozy 8-bit SDL window.
set -e
cd "$(dirname "$0")"

if [ -z "$CLICKUP_LIST_ID" ]; then
  echo "Set CLICKUP_LIST_ID to your ClickUp list id first."
  echo "(Open the list in ClickUp; the id is the number in the URL.)"
  exit 1
fi

# 1. Fetch tasks via the clickup skill (holds the API token, never prints it).
python3 "$HOME/workspace/skills/clickup/bin/clickup_tasks.py" \
  --list "$CLICKUP_LIST_ID" --out tasks.json

# 2. Gleam reads tasks.json and opens the SDL window.
export PATH="$HOME/otp/bin:$HOME/workspace/bin:$PATH"
gleam run
