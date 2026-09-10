#!/usr/bin/env python3
"""Desktop reminders for ClickUp tasks that are due soon.

Reads tasks.json (normalized format: {"tasks": [{"name", "status",
"priority", "due", "due_iso"}]}) and pops a Linux desktop notification
via `notify-send` for tasks that are overdue or due within --within
hours (default 36). Completed tasks are ignored.

`due_iso` should be an ISO 8601 date or datetime, e.g. "2026-09-10" or
"2026-09-10T14:30:00-04:00". A bare date is treated as end of that day,
local time.

Exit status is always 0 so systemd timers don't error-spam; problems
are printed to stdout instead.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta

DONE_WORDS = ("complete", "done", "closed")


def parse_due(value):
    """Return an aware datetime for an ISO date/datetime string, or None."""
    if not value or not str(value).strip():
        return None
    value = str(value).strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        if len(value) <= 10:  # date-only: deadline is the end of that day
            dt = dt.replace(hour=23, minute=59, second=59)
        dt = dt.astimezone()
    return dt


def is_done(status):
    status = str(status or "").lower()
    return any(word in status for word in DONE_WORDS)


def friendly(dt, now):
    """'today 14:30', 'tomorrow 09:00', or 'Sep 12, 09:00'."""
    time_part = dt.strftime("%H:%M")
    day = dt.date()
    today = now.date()
    if day == today:
        return f"today {time_part}"
    if day == today + timedelta(days=1):
        return f"tomorrow {time_part}"
    return dt.strftime("%b %d, ") + time_part


def send_notification(title, body, urgent, dry_run):
    if dry_run or shutil.which("notify-send") is None:
        where = "dry run" if dry_run else "notify-send not found"
        print(f"[{where}] {title}\n{body}")
        return
    cmd = [
        "notify-send",
        "-a", "CozyClickUp",
        "-u", "critical" if urgent else "normal",
        "-i", "appointment-soon",
        title,
        body,
    ]
    try:
        subprocess.run(cmd, check=True, timeout=15)
    except Exception as exc:  # no session bus, etc: don't crash the timer
        print(f"notify-send failed ({exc}); the message was:\n{title}\n{body}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tasks", default="tasks.json",
                    help="normalized tasks file (default: tasks.json)")
    ap.add_argument("--within", type=float, default=36,
                    help="hours ahead that count as 'due soon' (default: 36)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the notification instead of sending it")
    ap.add_argument("--demo", action="store_true",
                    help="send a test notification and exit")
    args = ap.parse_args()

    if args.demo:
        send_notification(
            "Cozy ClickUp",
            "Reminders are working! Your quest board is watching the clock.",
            urgent=False,
            dry_run=args.dry_run,
        )
        return

    try:
        with open(args.tasks, encoding="utf-8") as fh:
            tasks = json.load(fh).get("tasks", [])
    except FileNotFoundError:
        print(f"{args.tasks} not found; fetch your tasks first (see README).")
        return
    except (json.JSONDecodeError, AttributeError) as exc:
        print(f"could not read {args.tasks}: {exc}")
        return

    now = datetime.now().astimezone()
    horizon = now + timedelta(hours=args.within)
    overdue, soon = [], []
    for task in tasks:
        if is_done(task.get("status")):
            continue
        due = parse_due(task.get("due_iso"))
        if due is None:
            continue
        if due < now:
            overdue.append((task, due))
        elif due <= horizon:
            soon.append((task, due))

    if not overdue and not soon:
        if args.dry_run:
            print("No tasks due soon.")
        return

    lines = [f"OVERDUE: {t['name']} (was due {friendly(d, now)})"
             for t, d in overdue]
    lines += [f"{t['name']} (due {friendly(d, now)})" for t, d in soon]
    body = "\n".join(f"\u2022 {line}" for line in lines[:8])
    if len(lines) > 8:
        body += f"\n\u2022 \u2026and {len(lines) - 8} more"

    total = len(lines)
    if overdue and soon:
        title = f"{total} quests need you ({len(overdue)} overdue)"
    elif overdue:
        title = f"{total} quest{'s' if total != 1 else ''} overdue"
    else:
        title = f"{total} quest{'s' if total != 1 else ''} due soon"

    send_notification(title, body, urgent=bool(overdue), dry_run=args.dry_run)


if __name__ == "__main__":
    main()
