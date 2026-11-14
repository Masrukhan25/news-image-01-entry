#!/usr/bin/env python3
"""news-image-01 v1 entry: draw the world's news of Friday 13 November 2026.

This program draws a premium international-newspaper infographic,
1024 by 1024 pixels, that sums up the day's world news. The layout
is a front page: a big date masthead, one feature story, ten
secondary stories with small flat illustrations, and a digest of the
remaining seventeen headlines. Every story is a real event reported
on 13 November 2026; disputed claims are attributed with "says" or
"claims" and nothing is invented.

Python 3.13, Pillow only, no network, no randomness, no timestamps:
the same code always writes the same bytes. All fonts are bundled in
the fonts/ folder beside this file, so the program does not depend on
any system font. Run it with:

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import hashlib
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
MX = 28                      # side margin; content width is 1024 - 2*28
CW = W - 2 * MX              # 968

# ---------------------------------------------------------------- colours
IVORY = (246, 241, 232)      # newspaper paper
CARD = (255, 255, 255)       # story card paper
INK = (22, 22, 22)           # headline ink
MUTED = (74, 74, 74)         # body grey
RULE = (22, 22, 22)          # divider and card borders
PANEL = (238, 234, 224)      # illustration panel tint
SKY = (214, 226, 235)        # pale sky for illustration panels
SEA = (146, 178, 205)        # sea blue
SAND = (226, 205, 160)       # desert sand

# Category accent colours, keyed by story number.
ACCENT = {
    1: (178, 34, 34),    # US / tech & politics — red
    2: (31, 73, 125),    # Ukraine / diplomacy — blue
    3: (31, 73, 125),    # Ukraine / war — blue
    4: (200, 90, 20),    # Middle East / conflict — orange
    5: (103, 58, 140),   # Cybercrime / tech — purple
    6: (178, 34, 34),    # US / immigration — red
    7: (70, 110, 150),   # US / aviation — steel blue
    8: (40, 60, 120),    # Diplomacy / Middle East — navy
    9: (0, 110, 110),    # Africa / politics — teal
    10: (140, 40, 60),   # Gaza / humanitarian — maroon
    11: (34, 120, 60),   # Sport / football — green
}

# ---------------------------------------------------------------- fonts
BASE = Path(__file__).resolve().parent
FONTS = {
    "serif_bold": BASE / "fonts" / "DejaVuSerif-Bold.ttf",
    "serif": BASE / "fonts" / "DejaVuSerif.ttf",
    "sans_bold": BASE / "fonts" / "DejaVuSans-Bold.ttf",
    "sans": BASE / "fonts" / "DejaVuSans.ttf",
}
_cache = {}


def font(kind, size):
    """A bundled font at the given size, cached."""
    key = (kind, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(str(FONTS[kind]), size)
    return _cache[key]


# ---------------------------------------------------------------- text tools
def text_w(fnt, text):
    """Width of a string in a font."""
    return fnt.getlength(text)


def wrap(fnt, text, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = cur + " " + word
        if text_w(fnt, trial) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def fit_lines(fnt, text, max_w, max_lines):
    """Wrap text and clip to max_lines, adding an ellipsis if clipped."""
    lines = wrap(fnt, text, max_w)
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines]
    last = kept[-1]
    while last and text_w(fnt, last + " ...") > max_w:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    kept[-1] = (last + " ...") if last else "..."
    return kept


def draw_lines(drw, lines, fnt, x, y, lh, fill):
    """Draw lines top to bottom; returns the y below the last line."""
    for line in lines:
        drw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def shrink_to_fit(fnt_kind, text, start_size, max_w, max_lines, min_size=9):
    """Largest size (from start_size down to min_size) whose wrapped text
    fits in max_lines; returns (font, lines)."""
    size = start_size
    while size >= min_size:
        fnt = font(fnt_kind, size)
        lines = wrap(fnt, text, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(fnt_kind, min_size)
    return fnt, fit_lines(fnt, text, max_w, max_lines)


def label(drw, x, y, number, category, accent, size=11):
    """A coloured number chip plus an upper-case category label."""
    chip = " %02d " % number
    fnt = font("sans_bold", size)
    cw = text_w(fnt, chip)
    drw.rectangle([x, y, x + cw, y + size + 6], fill=accent)
    drw.text((x, y + 3), chip, font=fnt, fill=(255, 255, 255))
    drw.text((x + cw + 6, y + 3), category, font=fnt, fill=accent)
    return x + cw + 6 + text_w(fnt, category)

# ---------------------------------------------------------------- the news
# All 28 stories are real events reported on Friday 13 November 2026.
# Disputed claims are attributed ("says", "claims"); nothing is invented.

FEATURE = {
    "n": 1,
    "cat": "US · TECH & POLITICS",
    "headline": "Senate summons Nvidia chief Huang and Lutnick",
    "summary": "The US Senate Banking Committee calls the Nvidia CEO and "
               "the Commerce Secretary to testify.",
    "art": "senate",
}

SECONDARY = [
    {
        "n": 2,
        "cat": "UKRAINE · DIPLOMACY",
        "headline": "Zelensky meets US envoys as Europe joins talks",
        "summary": "Ukraine's president meets American envoys with European "
                   "allies brought into the negotiations.",
        "art": "flags",
    },
    {
        "n": 3,
        "cat": "UKRAINE · WAR",
        "headline": "Ukrainian drone hits Russian warship",
        "summary": "A Ukrainian drone strikes a Russian warship in the "
                   "Gulf of Finland.",
        "art": "warship",
    },
    {
        "n": 4,
        "cat": "MIDDLE EAST · CONFLICT",
        "headline": "Iran says it struck US radar site in Bahrain",
        "summary": "Tehran says it hit an American radar installation "
                   "in Bahrain.",
        "art": "radar",
    },
    {
        "n": 5,
        "cat": "CYBERCRIME · TECH",
        "headline": "FBI: North Korean hackers stole $400m in crypto",
        "summary": "The FBI says North Korean hackers took $400 million in "
                   "crypto through fake video calls.",
        "art": "laptop",
    },
    {
        "n": 6,
        "cat": "US · IMMIGRATION",
        "headline": "US reports record 483,200 deportations in 2026",
        "summary": "Washington reports a record number of deportations "
                   "and arrests this year.",
        "art": "chart",
    },
    {
        "n": 7,
        "cat": "US · AVIATION",
        "headline": "FAA orders nationwide ground stop",
        "summary": "The FAA grounds flights across the US after a "
                   "communications outage.",
        "art": "plane",
    },
    {
        "n": 8,
        "cat": "DIPLOMACY · MIDDLE EAST",
        "headline": "Turkiye and Qatar sign mutual defence pact",
        "summary": "Ankara and Doha formalise a mutual defence agreement.",
        "art": "treaty",
    },
    {
        "n": 9,
        "cat": "AFRICA · POLITICS",
        "headline": "South Sudan's Kiir dissolves government",
        "summary": "President Kiir dissolves the government ahead of the "
                   "country's first national elections.",
        "art": "ballot",
    },
    {
        "n": 10,
        "cat": "GAZA · HUMANITARIAN",
        "headline": "Gaza storms flood camps; 106,000 affected",
        "summary": "Storms flood displacement camps in Gaza, affecting "
                   "106,000 people, UNICEF says.",
        "art": "flood",
    },
    {
        "n": 11,
        "cat": "SPORT · FOOTBALL",
        "headline": "Kane breaks England caps record",
        "summary": "Harry Kane sets a new England appearances record "
                   "with his 126th cap.",
        "art": "football",
    },
]

# The remaining seventeen stories, as short headlines for the digest.
DIGEST = [
    (12, "Salah breaks Egypt scoring record in 5-0 win"),
    (13, "Man Utd appoint Pochettino as manager"),
    (14, "UN extends Abyei peacekeeping mandate to 2027"),
    (15, "Pakistan: 74 militants killed near Afghan border"),
    (16, "Six killed as building collapses near Nairobi"),
    (17, "Tens of thousands join Poland's nationalist march"),
    (18, "UK police investigate Walliams allegations"),
    (19, "Tanzania opposition leader Lissu jailed"),
    (20, "Niger says army regained control after mutiny"),
    (21, "Somalia security forces seize top court"),
    (22, "NGOs demand probe into Guinea mass grave"),
    (23, "Cameroon attackers kill officer, kidnap teachers"),
    (24, "UK curbs DRC visas; deals with Angola, Namibia"),
    (25, "7,400+ migrants reach Canary Islands in 10 days"),
    (26, "Pope Leo XIV welcomed by 1.5m in Chiclayo"),
    (27, "Nigeria clears 62 Ebola contacts; none fell ill"),
    (28, "Gaza baby dies of cold; WHO warns of infections"),
]

# ---------------------------------------------------------------- pictures
# Every illustration is drawn from simple flat shapes, clipped to the
# box it is given (x, y, w, h). No image files are used.

def _flag(drw, x, y, w, h, top, bottom):
    """A two-band horizontal flag."""
    drw.rectangle([x, y, x + w, y + h / 2], fill=top)
    drw.rectangle([x, y + h / 2, x + w, y + h], fill=bottom)


def _pole(drw, x, y, h):
    """A thin flagpole."""
    drw.line([x, y, x, y + h], fill=INK, width=2)


def art_senate(drw, x, y, w, h):
    """Senate hearing desk, empty witness chair, microchip."""
    drw.rectangle([x, y, x + w, y + h], fill=SKY)
    # microchip, top right
    cx, cy, s = x + w - 78, y + 10, 56
    drw.rectangle([cx - 6, cy + 8, cx - 2, cy + 16], fill=(180, 150, 60))
    drw.rectangle([cx - 6, cy + 32, cx - 2, cy + 40], fill=(180, 150, 60))
    drw.rectangle([cx + s + 2, cy + 8, cx + s + 6, cy + 16], fill=(180, 150, 60))
    drw.rectangle([cx + s + 2, cy + 32, cx + s + 6, cy + 40], fill=(180, 150, 60))
    drw.rectangle([cx, cy, cx + s, cy + s], fill=(40, 40, 48))
    drw.rectangle([cx + 12, cy + 12, cx + s - 12, cy + s - 12],
                  fill=(90, 110, 140))
    drw.text((cx + 18, cy + 20), "AI", font=font("sans_bold", 13),
             fill=(255, 255, 255))
    # empty witness chair, centre left: backrest, seat, legs
    chx = x + 52
    drw.rectangle([chx, y + 14, chx + 58, y + 46], fill=(146, 104, 66),
                  outline=(90, 64, 40))
    drw.rectangle([chx + 6, y + 20, chx + 52, y + 40], fill=(172, 128, 84))
    drw.rectangle([chx + 4, y + 46, chx + 54, y + 58], fill=(146, 104, 66),
                  outline=(90, 64, 40))
    drw.rectangle([chx + 8, y + 58, chx + 14, y + 76], fill=(90, 64, 40))
    drw.rectangle([chx + 44, y + 58, chx + 50, y + 76], fill=(90, 64, 40))
    # hearing desk
    drw.rectangle([x + 8, y + h - 32, x + w - 8, y + h - 6],
                  fill=(122, 84, 52))
    drw.rectangle([x + 8, y + h - 32, x + w - 8, y + h - 26],
                  fill=(146, 104, 66))
    # microphone on the desk
    drw.line([x + 150, y + h - 32, x + 150, y + h - 52], fill=INK, width=3)
    drw.ellipse([x + 144, y + h - 60, x + 156, y + h - 48], fill=INK)
    # name plate
    drw.rectangle([x + 190, y + h - 30, x + 260, y + h - 12],
                  fill=(240, 235, 220))
    drw.rectangle([x + 190, y + h - 30, x + 260, y + h - 12],
                  outline=INK, width=1)


def art_flags(drw, x, y, w, h):
    """Three flags (Ukraine, US, EU) over a round negotiating table."""
    drw.rectangle([x, y, x + w, y + h], fill=PANEL)
    fw, fh = 34, 22
    # Ukraine, left
    _pole(drw, x + 12, y + 8, fh + 26)
    _flag(drw, x + 12, y + 8, fw, fh, (0, 87, 183), (255, 215, 0))
    # United States, centre
    _pole(drw, x + w // 2 - 17, y + 4, fh + 30)
    ux = x + w // 2 - 17
    for i in range(4):
        drw.rectangle([ux, y + 4 + i * 6, ux + fw, y + 4 + i * 6 + 3],
                      fill=(178, 34, 34) if i % 2 == 0 else (255, 255, 255))
    drw.rectangle([ux, y + 4, ux + 14, y + 4 + 12], fill=(60, 59, 110))
    # European Union, right
    _pole(drw, x + w - 48, y + 8, fh + 26)
    ex = x + w - 48
    drw.rectangle([ex, y + 8, ex + fw, y + 8 + fh], fill=(0, 51, 153))
    for dx, dy in ((6, 4), (18, 4), (12, 10), (6, 15), (18, 15)):
        drw.ellipse([ex + dx, y + 8 + dy, ex + dx + 4, y + 8 + dy + 4],
                    fill=(255, 209, 0))
    # round table
    drw.ellipse([x + 6, y + h - 34, x + w - 6, y + h - 6], fill=(146, 104, 66))
    drw.rectangle([x + 6, y + h - 22, x + w - 6, y + h - 14],
                  fill=(122, 84, 52))


def art_warship(drw, x, y, w, h):
    """Grey warship with smoke on a cold northern sea."""
    drw.rectangle([x, y, x + w, y + h], fill=SKY)
    # smoke from the funnel
    for i, (sx, sy, sr) in enumerate(((58, 18, 9), (70, 10, 11), (84, 16, 8))):
        drw.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr],
                    fill=(120, 120, 120))
    # hull and superstructure
    drw.polygon([(x + 8, y + h - 38), (x + w - 8, y + h - 38),
                 (x + w - 22, y + h - 18), (x + 20, y + h - 18)],
                fill=(90, 96, 104))
    drw.rectangle([x + 34, y + h - 58, x + 74, y + h - 38], fill=(110, 116, 124))
    drw.rectangle([x + 52, y + h - 68, x + 58, y + h - 58], fill=(70, 76, 84))
    drw.line([x + 55, y + h - 68, x + 55, y + h - 80], fill=INK, width=2)
    # sea
    drw.rectangle([x, y + h - 18, x + w, y + h], fill=SEA)
    drw.line([x + 6, y + h - 10, x + w - 30, y + h - 10], fill=(255, 255, 255),
             width=2)
    drw.line([x + 30, y + h - 5, x + w - 6, y + h - 5], fill=(255, 255, 255),
             width=2)


def art_radar(drw, x, y, w, h):
    """Radar dome under a missile streak, desert coast."""
    drw.rectangle([x, y, x + w, y + h], fill=SKY)
    # missile streak, top right, thicker and with a flame head
    drw.line([x + w - 12, y + 6, x + w - 54, y + 32], fill=(220, 80, 30),
             width=5)
    drw.polygon([(x + w - 54, y + 32), (x + w - 68, y + 26),
                 (x + w - 68, y + 40)], fill=(220, 80, 30))
    drw.ellipse([x + w - 72, y + 28, x + w - 64, y + 38], fill=(255, 180, 40))
    # radar dome, larger
    drw.pieslice([x + 10, y + h - 66, x + 70, y + h - 6], 180, 360,
                 fill=(235, 235, 235), outline=INK, width=2)
    drw.rectangle([x + 18, y + h - 12, x + 62, y + h - 6], fill=(120, 120, 120))
    drw.line([x + 40, y + h - 66, x + 40, y + h - 80], fill=INK, width=2)
    drw.ellipse([x + 35, y + h - 84, x + 45, y + h - 74], fill=INK)
    # desert ground
    drw.rectangle([x, y + h - 10, x + w, y + h], fill=SAND)


def art_laptop(drw, x, y, w, h):
    """Laptop showing a masked face on a video call, coins spilling out."""
    drw.rectangle([x, y, x + w, y + h], fill=PANEL)
    # laptop screen
    drw.rectangle([x + 12, y + 8, x + w - 12, y + h - 26], fill=(30, 30, 36))
    drw.rectangle([x + 16, y + 12, x + w - 16, y + h - 30], fill=(120, 180, 220))
    # masked face, larger and centred
    fx, fy = x + w // 2, y + 28
    drw.ellipse([fx - 18, fy - 12, fx + 18, fy + 22], fill=(232, 190, 150),
                outline=(160, 120, 90))
    drw.rectangle([fx - 18, fy - 5, fx + 18, fy + 7], fill=(20, 20, 20))
    drw.ellipse([fx - 12, fy - 1, fx - 5, fy + 4], fill=(255, 255, 255))
    drw.ellipse([fx + 5, fy - 1, fx + 12, fy + 4], fill=(255, 255, 255))
    drw.arc([fx - 8, fy + 8, fx + 8, fy + 18], 0, 180, fill=(120, 70, 50),
            width=2)
    # laptop base
    drw.polygon([(x + 6, y + h - 26), (x + w - 6, y + h - 26),
                 (x + w - 2, y + h - 16), (x + 2, y + h - 16)],
                fill=(60, 60, 66))
    # coins spilling out
    for i, (cx, cy) in enumerate(((24, h - 12), (40, h - 8), (58, h - 12),
                                  (w - 40, h - 8), (w - 24, h - 12))):
        drw.ellipse([x + cx - 6, y + cy - 6, x + cx + 6, y + cy + 6],
                    fill=(212, 175, 55), outline=(150, 110, 20))


def art_chart(drw, x, y, w, h):
    """Rising bar chart with an upward arrow."""
    drw.rectangle([x, y, x + w, y + h], fill=PANEL)
    base = y + h - 14
    bars = [16, 24, 30, 38, 52]
    bw, gap = 14, 8
    bx = x + 14
    for i, bh in enumerate(bars):
        col = (178, 34, 34) if i == len(bars) - 1 else (31, 73, 125)
        drw.rectangle([bx, base - bh, bx + bw, base], fill=col)
        bx += bw + gap
    # axes
    drw.line([x + 8, base, x + w - 8, base], fill=INK, width=2)
    drw.line([x + 8, y + 8, x + 8, base], fill=INK, width=2)
    # rising arrow
    drw.line([x + 12, y + 26, x + w - 16, y + 8], fill=(34, 120, 60), width=3)
    drw.polygon([(x + w - 16, y + 8), (x + w - 28, y + 8),
                 (x + w - 16, y + 18)], fill=(34, 120, 60))

def art_plane(drw, x, y, w, h):
    """Aircraft grounded on the runway, under a red no-fly mark."""
    drw.rectangle([x, y, x + w, y + h], fill=SKY)
    # runway
    drw.rectangle([x, y + h - 20, x + w, y + h], fill=(120, 120, 120))
    for i in range(5):
        drw.rectangle([x + 8 + i * 22, y + h - 11, x + 18 + i * 22, y + h - 9],
                      fill=(255, 255, 255))
    # aircraft side view
    px, py = x + 16, y + h - 52
    drw.ellipse([px, py, px + 78, py + 18], fill=(40, 70, 120))
    drw.polygon([(px + 58, py + 2), (px + 78, py - 14), (px + 84, py - 14),
                 (px + 70, py + 4)], fill=(40, 70, 120))
    drw.polygon([(px + 30, py + 14), (px + 44, py + 26), (px + 52, py + 26),
                 (px + 44, py + 14)], fill=(30, 55, 95))
    drw.rectangle([px + 20, py + 18, px + 24, py + 30], fill=INK)
    drw.rectangle([px + 58, py + 18, px + 62, py + 30], fill=INK)
    # red no-fly mark, top right
    cx, cy, r = x + w - 22, y + 18, 12
    drw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(178, 34, 34),
                width=3)
    drw.line([cx - r + 3, cy + r - 3, cx + r - 3, cy - r + 3],
             fill=(178, 34, 34), width=3)


def art_treaty(drw, x, y, w, h):
    """Two flags above a signed treaty document with a wax seal."""
    drw.rectangle([x, y, x + w, y + h], fill=PANEL)
    # Turkiye flag (red, white crescent)
    tx, ty = x + 12, y + 8
    drw.rectangle([tx, ty, tx + 36, ty + 22], fill=(227, 10, 23))
    drw.ellipse([tx + 10, ty + 5, tx + 22, ty + 17], fill=(255, 255, 255))
    drw.ellipse([tx + 13, ty + 7, tx + 22, ty + 15], fill=(227, 10, 23))
    # Qatar flag (maroon, white serrated band)
    qx, qy = x + w - 48, y + 8
    drw.rectangle([qx, qy, qx + 36, qy + 22], fill=(138, 21, 56))
    drw.polygon([(qx, qy), (qx + 10, qy + 3), (qx, qy + 6), (qx + 10, qy + 9),
                 (qx, qy + 12), (qx + 10, qy + 15), (qx, qy + 18),
                 (qx + 10, qy + 21), (qx, qy + 22), (qx, qy)],
                fill=(255, 255, 255))
    # treaty document, with ruled lines and a signature
    drw.rectangle([x + 18, y + 36, x + w - 18, y + h - 8], fill=(255, 255, 255),
                  outline=INK)
    for i in range(4):
        drw.line([x + 26, y + 44 + i * 7, x + w - 52, y + 44 + i * 7],
                 fill=(120, 120, 120), width=1)
    drw.line([x + 26, y + h - 16, x + 56, y + h - 20], fill=INK, width=1)
    drw.line([x + 56, y + h - 20, x + 66, y + h - 14], fill=INK, width=1)
    # wax seal
    sx, sy = x + w - 34, y + h - 22
    drw.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=(178, 34, 34))


def art_ballot(drw, x, y, w, h):
    """Government building with columns, and a ballot box."""
    drw.rectangle([x, y, x + w, y + h], fill=PANEL)
    # building
    bx, by = x + 10, y + 12
    drw.polygon([(bx, by + 16), (bx + 52, by), (bx + 104, by + 16)],
                fill=(90, 96, 104))
    drw.rectangle([bx + 6, by + 16, bx + 98, by + 52], fill=(150, 150, 145))
    for i in range(4):
        drw.rectangle([bx + 12 + i * 24, by + 20, bx + 18 + i * 24, by + 48],
                      fill=(235, 235, 235))
    # ballot box
    qx, qy = x + w - 42, y + h - 34
    drw.rectangle([qx, qy, qx + 30, qy + 24], fill=(31, 73, 125))
    drw.rectangle([qx + 4, qy - 8, qx + 26, qy], fill=(255, 255, 255),
                  outline=INK)
    drw.line([qx + 8, qy + 2, qx + 22, qy + 2], fill=INK, width=2)


def art_flood(drw, x, y, w, h):
    """Tents flooded under rain."""
    drw.rectangle([x, y, x + w, y + h], fill=(200, 205, 210))
    # rain
    for i in range(8):
        rx = x + 8 + i * 13
        drw.line([rx, y + 6, rx - 4, y + 18], fill=(90, 110, 140), width=2)
    # tents, larger
    for tx, tc in ((10, (226, 205, 160)), (56, (240, 235, 220))):
        drw.polygon([(x + tx, y + h - 26), (x + tx + 22, y + h - 56),
                     (x + tx + 44, y + h - 26)], fill=tc, outline=INK)
        drw.line([x + tx + 22, y + h - 56, x + tx + 22, y + h - 26],
                 fill=(150, 130, 100), width=1)
    # flood water
    drw.rectangle([x, y + h - 26, x + w, y + h], fill=SEA)
    drw.line([x + 6, y + h - 16, x + w - 30, y + h - 16],
             fill=(255, 255, 255), width=2)
    drw.line([x + 30, y + h - 8, x + w - 6, y + h - 8],
             fill=(255, 255, 255), width=2)


def art_football(drw, x, y, w, h):
    """Footballer in white raising his arms, ball at his feet."""
    drw.rectangle([x, y, x + w, y + h], fill=PANEL)
    # pitch
    drw.rectangle([x, y + h - 18, x + w, y + h], fill=(60, 140, 70))
    # footballer, larger: head, raised arms, white shirt, dark shorts
    cx = x + w // 2 - 14
    drw.ellipse([cx + 10, y + 6, cx + 26, y + 22], fill=(232, 190, 150),
                outline=(120, 80, 50))
    drw.line([cx + 2, y + 32, cx - 8, y + 12], fill=(255, 255, 255), width=5)
    drw.line([cx + 30, y + 32, cx + 40, y + 12], fill=(255, 255, 255), width=5)
    drw.rectangle([cx + 4, y + 24, cx + 28, y + 46], fill=(255, 255, 255),
                  outline=(178, 34, 34), width=2)
    drw.rectangle([cx + 8, y + 46, cx + 24, y + 56], fill=(20, 20, 60))
    drw.line([cx + 12, y + 56, cx + 8, y + h - 18], fill=(20, 20, 60), width=5)
    drw.line([cx + 20, y + 56, cx + 26, y + h - 18], fill=(20, 20, 60), width=5)
    # ball, larger
    bx, by = x + w - 30, y + h - 30
    drw.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=(255, 255, 255),
                outline=INK, width=2)
    drw.polygon([(bx - 4, by - 6), (bx + 4, by - 6), (bx + 6, by),
                 (bx, by + 6), (bx - 6, by)], fill=INK)


ART = {
    "senate": art_senate,
    "flags": art_flags,
    "warship": art_warship,
    "radar": art_radar,
    "laptop": art_laptop,
    "chart": art_chart,
    "plane": art_plane,
    "treaty": art_treaty,
    "ballot": art_ballot,
    "flood": art_flood,
    "football": art_football,
}

# ---------------------------------------------------------------- layout
# Header 0-118; main 128-842; digest 852-1012. All coordinates in px.
HEADER_H = 118
MAIN_Y = 128
FEATURE_BOX = (MX, MAIN_Y, 532, 302)          # x, y, w, h
WIDE_BOXES = [(572, MAIN_Y, 424, 145), (572, 285, 424, 145)]
GRID_X = [MX, 273, 518, 763]                   # four columns, 233 wide
GRID_Y = [442, 648]                            # two rows, 194 tall
GRID_W, GRID_H = 233, 194
DIGEST_Y = 852


def draw_header(drw):
    """Masthead: two small labels, the big date headline, a divider."""
    small = font("sans_bold", 13)
    drw.text((MX, 20), "THE WORLD'S NEWS IN ONE PICTURE",
             font=small, fill=INK)
    right = "28 STORIES · FRIDAY EDITION"
    drw.text((W - MX - text_w(small, right), 20), right,
             font=small, fill=INK)
    head = font("serif_bold", 54)
    title = "FRIDAY 13 NOVEMBER 2026"
    tw = text_w(head, title)
    drw.text(((W - tw) / 2, 46), title, font=head, fill=INK)
    drw.line([MX, 110, W - MX, 110], fill=RULE, width=3)
    drw.line([MX, 116, W - MX, 116], fill=(178, 34, 34), width=1)


def _card_frame(drw, x, y, w, h):
    drw.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=1)


def draw_feature(drw, story):
    """The largest card: category, big headline, summary, illustration."""
    x, y, w, h = FEATURE_BOX
    _card_frame(drw, x, y, w, h)
    accent = ACCENT[story["n"]]
    label(drw, x + 16, y + 14, story["n"], story["cat"], accent, size=13)
    fnt, lines = shrink_to_fit("serif_bold", story["headline"], 30,
                               w - 32, 3, min_size=22)
    hy = y + 44
    hy = draw_lines(drw, lines, fnt, x + 16, hy, fnt.size + 6, INK)
    sfont = font("sans", 14)
    slines = fit_lines(sfont, story["summary"], w - 32, 3)
    draw_lines(drw, slines, sfont, x + 16, hy + 8, 19, MUTED)
    ill_y = y + h - 118
    drw.rectangle([x + 16, ill_y, x + w - 16, y + h - 10], fill=PANEL,
                  outline=RULE, width=1)
    ART[story["art"]](drw, x + 17, ill_y + 1, w - 34, 106)


def draw_wide(drw, story, x, y, w, h):
    """A wide secondary card: illustration left, text right."""
    _card_frame(drw, x, y, w, h)
    accent = ACCENT[story["n"]]
    drw.rectangle([x + 8, y + 8, x + 120, y + h - 8], fill=PANEL,
                  outline=RULE, width=1)
    ART[story["art"]](drw, x + 9, y + 9, 110, h - 18)
    tx, tw = x + 132, w - 144
    label(drw, tx, y + 12, story["n"], story["cat"], accent, size=10)
    fnt, lines = shrink_to_fit("serif_bold", story["headline"], 17,
                               tw, 2, min_size=13)
    hy = draw_lines(drw, lines, fnt, tx, y + 34, fnt.size + 4, INK)
    sfont = font("sans", 11)
    slines = fit_lines(sfont, story["summary"], tw, 3)
    draw_lines(drw, slines, sfont, tx, hy + 5, 14, MUTED)


def draw_small(drw, story, x, y, w, h):
    """A small secondary card: illustration on top, text below."""
    _card_frame(drw, x, y, w, h)
    accent = ACCENT[story["n"]]
    drw.rectangle([x + 8, y + 8, x + w - 8, y + 64], fill=PANEL,
                  outline=RULE, width=1)
    ART[story["art"]](drw, x + 9, y + 9, w - 18, 54)
    label(drw, x + 10, y + 72, story["n"], story["cat"], accent, size=10)
    fnt, lines = shrink_to_fit("serif_bold", story["headline"], 15,
                               w - 20, 2, min_size=11)
    hy = draw_lines(drw, lines, fnt, x + 10, y + 92, fnt.size + 3, INK)
    sfont = font("sans", 10)
    slines = fit_lines(sfont, story["summary"], w - 20, 3)
    draw_lines(drw, slines, sfont, x + 10, hy + 4, 13, MUTED)


def draw_digest(drw):
    """Bottom digest: title plus seventeen short headlines, 3 columns."""
    title = font("sans_bold", 14)
    drw.rectangle([MX, DIGEST_Y + 2, MX + 12, DIGEST_Y + 14],
                  fill=(178, 34, 34))
    drw.text((MX + 20, DIGEST_Y), "ALSO ON FRIDAY 13 NOVEMBER",
             font=title, fill=INK)
    drw.line([MX, DIGEST_Y + 24, W - MX, DIGEST_Y + 24], fill=RULE, width=1)
    palette = [(178, 34, 34), (31, 73, 125), (200, 90, 20),
               (103, 58, 140), (34, 120, 60), (0, 110, 110)]
    cols = [DIGEST[i:i + 6] for i in range(0, len(DIGEST), 6)]
    col_x = [MX, 358, 688]
    head = font("sans", 11)
    numf = font("sans_bold", 9)
    for ci, items in enumerate(cols):
        cx = col_x[ci]
        for ri, (num, text) in enumerate(items):
            iy = DIGEST_Y + 34 + ri * 21
            accent = palette[(num - 12) % len(palette)]
            drw.rectangle([cx, iy, cx + 17, iy + 15], fill=accent)
            ntxt = "%02d" % num
            drw.text((cx + (17 - text_w(numf, ntxt)) / 2, iy + 3),
                     ntxt, font=numf, fill=(255, 255, 255))
            shown = text
            while shown and text_w(head, shown) > 282:
                shown = shown.rsplit(" ", 1)[0] if " " in shown else shown[:-1]
            if shown != text:
                shown = shown + " ..."
            drw.text((cx + 23, iy + 2), shown, font=head, fill=INK)


def build():
    """Assemble the whole front page and return the image."""
    img = Image.new("RGB", (W, H), IVORY)
    drw = ImageDraw.Draw(img)
    draw_header(drw)
    draw_feature(drw, FEATURE)
    for story, box in zip(SECONDARY[:2], WIDE_BOXES):
        draw_wide(drw, story, *box)
    idx = 2
    for gy in GRID_Y:
        for gx in GRID_X:
            draw_small(drw, SECONDARY[idx], gx, gy, GRID_W, GRID_H)
            idx += 1
    draw_digest(drw)
    return img


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    img = build()
    dest = out_dir / "entry.png"
    img.save(dest, format="PNG", compress_level=6, optimize=False)
    data = dest.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    check = Image.open(dest)
    if check.size != (W, H) or check.format != "PNG":
        print("error: output is not a 1024x1024 PNG", file=sys.stderr)
        return 1
    if len(data) >= 1_048_576:
        print("error: output is %d bytes, over the 1 MiB limit"
              % len(data), file=sys.stderr)
        return 1
    print("wrote %s (%d bytes, 1024x1024) sha256 %s"
          % (dest, len(data), digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
