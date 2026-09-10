# cozy_clickup

Your ClickUp tasks, displayed on a wooden quest board in a cozy 8-bit
night scene — twinkling stars, a pixel moon, drifting snow, and a
flickering lantern. Built with Gleam (Erlang target) driving a
pygame/SDL2 renderer.

## What it looks like

The window shows up to 12 tasks as quest cards: a checkbox that fills in
for completed tasks, the task name, a colored status pill, red hearts for
priority (urgent = 3, high = 2, normal = 1), and the due date when set.

## Requirements

- Gleam + Erlang/OTP 26+
- Python 3 with `pygame` (`pip install pygame`)
- A display (the window is a real SDL window, not a web page)

## Quick start (sample data)

```sh
cp tasks.sample.json tasks.json
gleam run
```

Close the window or press ESC to quit.

## With real ClickUp tasks

1. Create a ClickUp personal API token: avatar → **Settings** → **Apps** →
   **API Token** → **Generate** (tokens start with `pk_`).
2. Find your list id: open the list in ClickUp, the id is the number in the URL.
3. Run:

```sh
CLICKUP_LIST_ID=123456789 ./run.sh
```

`run.sh` fetches your tasks through the `clickup` skill (the token is kept
in secure storage and never printed), writes `tasks.json`, and opens the
window. For a fully hands-free refresh on a schedule, ask your assistant to
set it up.

## Reminders (Linux desktop notifications)

`tools/remind.py` watches `tasks.json` and pops a system notification
for tasks that are overdue or due within the next 36 hours
(`--within HOURS` to change that). It needs `due_iso` on each task — an
ISO 8601 date or datetime like `"2026-09-10"` or
`"2026-09-10T14:30:00-04:00"` (the ClickUp fetcher writes this; the
sample file shows the shape). Completed tasks are skipped.

You need `notify-send` (`libnotify-bin` on Debian/Ubuntu). Try it:

```sh
python3 tools/remind.py --demo          # test notification
python3 tools/remind.py --dry-run       # preview without notifying
```

To get reminded automatically every 30 minutes, install the systemd
user units on the machine where you run the board:

```sh
mkdir -p ~/.config/systemd/user
cp tools/cozy-clickup-remind.service tools/cozy-clickup-remind.timer \
   ~/.config/systemd/user/
# edit the service file: fix the WorkingDirectory/ExecStart paths and
# set CLICKUP_LIST_ID to your list id
systemctl --user daemon-reload
systemctl --user enable --now cozy-clickup-remind.timer
```

Prefer cron? This works too, but `notify-send` needs your desktop
session bus, so keep the `DBUS_SESSION_BUS_ADDRESS` line:

```cron
*/30 * * * * DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus /path/to/cozy_clickup/tools/remind.sh
```

## How it works

- `src/cozy_clickup.gleam` — reads `tasks.json`, keeps the first 12 tasks,
  writes a compact `render.json`.
- `src/renderer_ffi.erl` — tiny Erlang FFI that spawns the renderer as a
  subprocess and blocks until its window closes.
- `renderer/cozy.py` — the cozy scene: gradient night sky, twinkling stars,
  cratered moon, drifting snow, wooden quest board, animated lantern. Text
  uses a hand-drawn 5×7 pixel font, so everything stays crunchy.
- `tasks.sample.json` — the normalized task format: `{"tasks": [{"name",
  "status", "priority", "due"}]}`.

## Layout tweaks

Open `renderer/cozy.py` and adjust the palette at the top, or the board
geometry in `draw_board`. The renderer also honours `COZY_FRAMES` (quit
after N frames) and `COZY_SHOT` (save a screenshot) for headless testing.
