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
