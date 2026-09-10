#!/usr/bin/env python3
"""Cozy 8-bit ClickUp task board.

Reads render.json (written by the Gleam program) and shows the tasks on a
wooden quest board in a cozy night scene. Pure pygame (SDL2), chunky pixels,
hand-drawn 5x7 font. Close the window or press ESC to quit.

Headless test helpers (env vars):
  COZY_FRAMES=N   quit after N frames
  COZY_SHOT=path  save a screenshot before quitting
"""

import json
import math
import os
import random
import sys

import pygame

W, H = 480, 360
FPS = 12

# ---------------------------------------------------------------- palette
SKY_TOP = (18, 18, 48)
SKY_BOT = (62, 48, 102)
STAR = (255, 250, 215)
MOON = (242, 236, 200)
MOON_DARK = (208, 198, 160)
WOOD_DARK = (70, 50, 30)
WOOD = (108, 74, 46)
WOOD_LIGHT = (128, 92, 58)
NAIL = (38, 26, 16)
PARCHMENT = (233, 216, 164)
PARCH_HI = (246, 232, 192)
INK = (74, 53, 32)
CREAM = (246, 236, 202)
HEART = (224, 74, 94)
GLOW = (255, 182, 92)

STATUS_COLORS = {
    "done": (108, 178, 108),
    "progress": (232, 178, 78),
    "review": (172, 130, 222),
    "todo": (122, 142, 182),
}

# ---------------------------------------------------------------- 5x7 font
F = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".####"),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ")": (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "..#..", ".#...", ".#..#", "#...#", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "@": (".###.", "#...#", "#.##.", "#.##.", "#.##.", "#....", ".###."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
}

CHECK = (  # tiny check mark, 7x7
    ".......",
    "......#",
    ".....##",
    "#...##.",
    "##.##..",
    ".###...",
    "..#....",
)

HEART_PX = (
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
)

FLAMES = (
    (
        "...#...",
        "...##..",
        "..###..",
        "..###..",
        ".#####.",
        ".#####.",
        "#######",
    ),
    (
        "....#..",
        "...##..",
        "...###.",
        "..####.",
        "..#####",
        ".######",
        "#######",
    ),
    (
        "..#....",
        "..##...",
        ".###...",
        ".####..",
        "#####..",
        "######.",
        "#######",
    ),
)


def smart_truncate(text, max_chars):
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 3]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "..."


def draw_text(surf, text, x, y, color, scale=2):
    text = text.upper()
    cx = x
    for ch in text:
        glyph = F.get(ch, F["?"])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "#":
                    pygame.draw.rect(
                        surf,
                        color,
                        (cx + col * scale, y + row * scale, scale, scale),
                    )
        cx += 6 * scale
    return cx - x


def text_w(text, scale=2):
    return len(text) * 6 * scale


def draw_bitmap(surf, bitmap, x, y, color, scale=1):
    for row, bits in enumerate(bitmap):
        for col, bit in enumerate(bits):
            if bit == "#":
                pygame.draw.rect(
                    surf, color, (x + col * scale, y + row * scale, scale, scale)
                )


# ---------------------------------------------------------------- scene
def sky(surf):
    bands = 12
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(
            int(SKY_TOP[j] + (SKY_BOT[j] - SKY_TOP[j]) * t) for j in range(3)
        )
        pygame.draw.rect(surf, c, (0, i * H // bands, W, H // bands + 1))


def make_stars():
    rng = random.Random(7)
    return [
        (rng.randrange(0, W), rng.randrange(0, 240), rng.randrange(0, 20))
        for _ in range(70)
    ]


def stars(surf, star_list, frame):
    for x, y, phase in star_list:
        if (frame + phase) % 22 < 15:
            bright = 140 + 115 * ((frame + phase) % 22) / 15
            c = (int(bright), int(bright), int(bright * 0.85))
            surf.set_at((x, y), c)
            if phase % 5 == 0:
                surf.set_at((x + 1, y), c)
                surf.set_at((x, y + 1), c)


def moon(surf):
    cx, cy, r = 400, 38, 20
    for dy in range(-r, r + 1):
        hw = int(math.sqrt(r * r - dy * dy))
        pygame.draw.rect(surf, MOON, (cx - hw, cy + dy, hw * 2, 1))
    for ox, oy, cr in ((-8, -6, 5), (7, 4, 4), (-2, 10, 3)):
        for dy in range(-cr, cr + 1):
            hw = int(math.sqrt(cr * cr - dy * dy))
            pygame.draw.rect(surf, MOON_DARK, (cx + ox - hw, cy + oy + dy, hw * 2, 1))


def make_snow():
    rng = random.Random(21)
    return [
        [rng.randrange(0, W), rng.randrange(0, H), rng.uniform(0.4, 1.1),
         rng.uniform(0, 6.28)]
        for _ in range(36)
    ]


def snow(surf, flakes, frame):
    for f in flakes:
        f[1] += f[2]
        f[3] += 0.05
        if f[1] > H:
            f[1] = -2
            f[0] = random.randrange(0, W)
        x = int(f[0] + math.sin(f[3]) * 6)
        surf.set_at((x % W, int(f[1])), (235, 238, 250))


def lantern(surf, frame):
    # glow
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    radius = 44 + int(4 * math.sin(frame * 0.7))
    pygame.draw.circle(glow, (*GLOW, 36), (60, 60), radius)
    surf.blit(glow, (-16, 262))
    # post + arm
    pygame.draw.rect(surf, WOOD_DARK, (16, 300, 8, 52))
    pygame.draw.rect(surf, WOOD_DARK, (16, 300, 26, 6))
    # hanging lantern
    pygame.draw.line(surf, NAIL, (38, 306), (38, 312), 2)
    lx, ly = 26, 312
    pygame.draw.rect(surf, INK, (lx, ly, 24, 30))
    pygame.draw.rect(surf, (255, 196, 110), (lx + 4, ly + 4, 16, 22))
    fire = FLAMES[(frame // 3) % 3]
    draw_bitmap(surf, fire, lx + 8, ly + 12, (232, 110, 30), 1)
    draw_bitmap(surf, fire, lx + 9, ly + 14, (255, 214, 120), 1)
    pygame.draw.rect(surf, INK, (lx - 2, ly - 3, 28, 4))
    pygame.draw.rect(surf, INK, (lx - 2, ly + 30, 28, 4))


# ---------------------------------------------------------------- board
def classify(status):
    s = status.lower()
    if any(k in s for k in ("complete", "done", "closed")):
        return "done"
    if "progress" in s:
        return "progress"
    if "review" in s:
        return "review"
    return "todo"


def hearts_for(priority):
    return {"urgent": 3, "high": 2, "normal": 1}.get(priority.lower(), 0)


def draw_board(surf, title, tasks, frame):
    bx, by, bw, bh = 50, 72, 380, 272
    pygame.draw.rect(surf, WOOD_DARK, (bx, by, bw, bh))
    pygame.draw.rect(surf, WOOD, (bx + 6, by + 6, bw - 12, bh - 12))
    for py in range(by + 30, by + bh - 6, 26):
        pygame.draw.rect(surf, WOOD_DARK, (bx + 6, py, bw - 12, 2))
    for nx, ny in ((bx + 12, by + 12), (bx + bw - 12, by + 12),
                   (bx + 12, by + bh - 12), (bx + bw - 12, by + bh - 12)):
        pygame.draw.rect(surf, NAIL, (nx - 2, ny - 2, 5, 5))

    tw = text_w(title, 3)
    draw_text(surf, title, bx + (bw - tw) // 2 + 2, by + 22, WOOD_DARK, 3)
    draw_text(surf, title, bx + (bw - tw) // 2, by + 20, CREAM, 3)
    pygame.draw.rect(surf, WOOD_DARK, (bx + 30, by + 52, bw - 60, 2))

    shown = tasks[:4]
    cy = by + 62
    for task in shown:
        draw_card(surf, bx + 16, cy, bw - 32, 40, task)
        cy += 48
    if len(tasks) > 4:
        more = "+%d MORE QUESTS" % (len(tasks) - 4)
        mw = text_w(more, 1)
        draw_text(surf, more, bx + (bw - mw) // 2, cy + 6, CREAM, 1)


def draw_card(surf, x, y, w, h, task):
    pygame.draw.rect(surf, INK, (x, y, w, h))
    pygame.draw.rect(surf, PARCHMENT, (x + 2, y + 2, w - 4, h - 4))
    pygame.draw.rect(surf, PARCH_HI, (x + 2, y + 2, w - 4, 3))

    kind = classify(task.get("status", ""))
    done = kind == "done"

    # checkbox
    pygame.draw.rect(surf, INK, (x + 8, y + 8, 13, 13))
    pygame.draw.rect(surf, CREAM, (x + 10, y + 10, 9, 9))
    if done:
        pygame.draw.rect(surf, STATUS_COLORS["done"], (x + 10, y + 10, 9, 9))
        draw_bitmap(surf, CHECK, x + 10, y + 10, (30, 80, 30), 1)

    # name
    name = smart_truncate(task.get("name", ""), 26)
    draw_text(surf, name, x + 28, y + 6, INK, 2)

    # status pill
    label = task.get("status", "").upper()[:12] or "TODO"
    px, py = x + 28, y + 25
    pw = text_w(label, 1) + 8
    pygame.draw.rect(surf, STATUS_COLORS[kind], (px, py, pw, 11))
    draw_text(surf, label, px + 4, py + 2, CREAM, 1)

    # priority hearts
    hx = px + pw + 8
    for _ in range(hearts_for(task.get("priority", ""))):
        draw_bitmap(surf, HEART_PX, hx, py + 2, HEART, 1)
        hx += 16

    # due date
    due = task.get("due", "")
    if due:
        draw_text(surf, "DUE " + due.upper()[:8], hx + 4, py + 2, INK, 1)


# ---------------------------------------------------------------- main
def main():
    with open(sys.argv[1]) as fh:
        data = json.load(fh)
    tasks = data.get("tasks", [])
    title = data.get("title", "TASKS")

    pygame.init()
    pygame.display.set_caption("Cozy ClickUp")
    surf = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    star_list = make_stars()
    flakes = make_snow()

    max_frames = int(os.environ.get("COZY_FRAMES", "0") or 0)
    shot_path = os.environ.get("COZY_SHOT", "")

    frame = 0
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                running = False

        sky(surf)
        stars(surf, star_list, frame)
        moon(surf)
        draw_board(surf, title, tasks, frame)
        snow(surf, flakes, frame)
        lantern(surf, frame)

        pygame.display.flip()
        clock.tick(FPS)
        frame += 1
        if max_frames and frame >= max_frames:
            running = False

    if shot_path:
        pygame.image.save(surf, shot_path)
    pygame.quit()


if __name__ == "__main__":
    main()
