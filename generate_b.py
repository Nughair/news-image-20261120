#!/usr/bin/env python3
"""generate_b.py — comparison draft B of the news-image-20261120 page.

A variant of generate_v2.py printing the SAME 36 stories, re-slotted:
DR Congo (Ebola) and Peru (quake) are promoted from briefs to pictured
cards; Japan inflation and the Italy strike move down to the briefs.
The Akvan lead carries "440,000+ evacuated" on its art by Gopalpur;
the markets lead is a bar chart of Friday's close (Taiwan -6.2%,
Seoul -5.2%, Tokyo -5.1% from one zero baseline); each lead names its
sources on the panel; the cricket card shows 118 exactly once (the
numbers strip now carries Nicholls' 175* instead). DRAFT ONLY.

Usage:
    python3 generate_b.py final     # writes ./output/entry.png

The `final` stage is the only stage: it renders the complete page.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- fonts

FONT_DIR = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = f"{FONT_DIR}/NotoSerif-Black.ttf"
SERIF_BOLD = f"{FONT_DIR}/NotoSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/NotoSerif-Regular.ttf"
SERIF_IT = f"{FONT_DIR}/NotoSerif-Italic.ttf"
SANS_BLACK = f"{FONT_DIR}/NotoSans-Black.ttf"
SANS_XB = f"{FONT_DIR}/NotoSans-ExtraBold.ttf"
SANS_BOLD = f"{FONT_DIR}/NotoSans-Bold.ttf"
SANS = f"{FONT_DIR}/NotoSans-Regular.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- colours

PAPER = (247, 242, 231)
PAPER_DARK = (238, 231, 214)
INK = (24, 22, 19)
INK_SOFT = (58, 54, 48)
GREY = (122, 114, 100)
RULE = (196, 188, 168)
RED = (178, 34, 26)
RED_DARK = (140, 26, 20)
NAVY = (17, 36, 58)
NAVY_2 = (27, 55, 84)
TEAL = (24, 102, 106)
SKY = (168, 205, 224)
SEA = (140, 188, 205)
LAND = (222, 205, 165)
GOLD = (199, 148, 44)
RUST = (176, 92, 44)
GREEN = (74, 116, 62)
SLATE = (84, 106, 132)
WHITE = (252, 250, 244)

W = 1024
M = 24                      # page margin
CW = W - 2 * M              # content width (976)


# ---------------------------------------------------------------- helpers

def tw(d, s, f):
    """Text width in px."""
    return d.textlength(s, font=f)


def fit(d, s, path, max_w, start, floor=8):
    """Largest font (<= start) whose rendering of s fits max_w."""
    size = start
    while size > floor and tw(d, s, F(path, size)) > max_w:
        size -= 1
    return F(path, size)


def wrap(d, s, f, max_w):
    """Greedy word wrap; returns a list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else f"{cur} {word}"
        if tw(d, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def ctext(d, cx, y, s, f, fill=INK):
    """Centre text horizontally on cx at top y."""
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)


def chip(d, cx, cy, num, r=11):
    """Red numbered disc with a white numeral, centred on (cx, cy)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f = F(SANS_BOLD, 12 if num < 10 else 11)
    label = str(num)
    bbox = d.textbbox((0, 0), label, font=f)
    d.text((cx - (bbox[2] - bbox[0]) / 2 - bbox[0],
            cy - (bbox[3] - bbox[1]) / 2 - bbox[1]), label, font=f, fill=WHITE)


def banner_tag(d, box, text):
    """Small dark source tag at a banner's bottom-right corner."""
    f = F(SANS_BOLD, 9.5)
    w = tw(d, text, f) + 12
    x1, y1 = box[2] - w, box[3] - 17
    d.rectangle([x1, y1, box[2], box[3]], fill=(20, 20, 20))
    d.text((x1 + 6, y1 + 3), text, font=f, fill=WHITE)


# ---------------------------------------------------------------- data

NUMBERS = [
    ("3", "bridges hit over the Dnipro"),
    ("440,000+", "people evacuated ahead of Cyclone Akvan"),
    ("-6.2%", "Taiwan's Taiex on Friday; -17.5% on the week"),
    ("Up to 100,000", "youth-scheme places each way per year, UK–EU"),
    ("175*", "runs by Henry Nicholls against India"),
    ("At least 1,144", "children killed or injured in Ukraine, Jan–Oct"),
]

REGIONS = [
    ("EUROPE", 8, NAVY),
    ("ASIA", 8, TEAL),
    ("MIDDLE EAST", 4, GOLD),
    ("AFRICA", 6, RUST),
    ("AMERICAS", 7, SLATE),
    ("OCEANIA", 2, GREEN),
    ("GLOBAL", 1, GREY),
]

LEADS = [
    {
        "num": 1, "place": "KYIV, UKRAINE", "field": "WAR",
        "headline": "Russian strikes hit Kyiv bridges",
        "body": ("110+ missiles and 400+ drones — one of the year's "
                 "largest barrages, Kyiv says — kill at least nine "
                 "people across Ukraine."),
        "illus": "kyiv",
    },
    {
        "num": 2, "place": "ODISHA, INDIA", "field": "CYCLONE",
        "headline": "Cyclone Akvan comes ashore in Odisha",
        "body": ("The storm crosses the coast near Gopalpur. Odisha "
                 "officials say more than 440,000 people were moved "
                 "to safety. No major loss of life is reported."),
        "illus": "akvan",
    },
    {
        "num": 3, "place": "TAIPEI · SEOUL · TOKYO", "field": "MARKETS",
        "headline": "AI sell-off sinks Asia's markets",
        "body": ("Taiwan's Taiex fell 6.2% on Friday and 17.5% for "
                 "the week. Seoul loses 5.2%, Tokyo 5.1% as "
                 "chipmakers lead the slide."),
        "illus": "selloff",
    },
]

# num, banner label, banner kind, source tag, kicker, headline, sub
CARDS = [
    (4, "COP31: OVERTIME", "globe", "Reuters", "ANTALYA · CLIMATE",
     "COP31 deadlocked into overtime",
     "Draft drops fossil-fuel phase-out as talks run past deadline."),
    (5, "UK–EU DEAL", "flags", "Reuters", "BRUSSELS · DIPLOMACY",
     "UK and EU agree to ease food checks",
     "Youth scheme: up to 100,000 places each way per year."),
    (6, "POLAND: MISSILE", "missile", "Reuters", "EASTERN POLAND · SECURITY",
     "Russian missile lands in Poland",
     "A Kh-101 falls near Nowy Lipowiec; two airports suspended."),
    (7, "HORMUZ: TANKER FIRE", "tanker", "Reuters", "HORMUZ · SECURITY",
     "Tanker catches fire off Oman",
     "UKMTO reports a projectile strike; Iran's Guards say a mine."),
    (8, "IRAQ: ARMY IN", "convoy", "Reuters", "CENTRAL IRAQ · SECURITY",
     "Army enters militia stronghold",
     "State forces deploy in Jurf al-Sakhar under a withdrawal deal."),
    (9, "DR CONGO: EBOLA", "virus", "WHO", "DR CONGO · HEALTH",
     "Ebola outbreak grows in DR Congo",
     "WHO reports 945 more confirmed Ebola cases since its 6 Nov update."),
    (10, "PERU: M6.8", "quake", "Reuters", "CENTRAL PERU · EARTHQUAKE",
     "M6.8 quake hits Junín, felt in Lima",
     "No casualties immediately reported; residents ran into the streets."),
    (11, "SEOUL: IMPEACH", "court", "Korea JoongAng Daily", "SEOUL · POLITICS",
     "Party moves to impeach top judge",
     "Cho Hee-dae push adopted as party stance — a first in 41 years."),
    (12, "KENYA: OIL", "derrick", "KBC", "TURKANA, KENYA · ENERGY",
     "Kenya begins production drilling in Turkana",
     "Production drilling starts at the Amosing field."),
    (13, "NZ: 368", "cricket", "ICC", "WELLINGTON · CRICKET",
     "Nicholls 175*, Phillips 118",
     "NZ 368 on day two; India reply 159 for 1 at stumps."),
]

# Briefs grouped by region: (group, colour, [(num, place, text, source)])
# Printed as: num Place — text (source), in two wide columns, numbered
# in column order. Column split (final corrections): the left column
# carries Europe, Asia, the Middle East and Oceania; the right column
# carries the Americas and Africa — the two columns end within ~40 px
# of each other and the brief text auto-fits a full point larger than
# the old Europe/Asia/Americas split allowed. The DATE CHECK list no
# longer appears on the page; it lives in STORIES.md with the sources.
BRIEF_GROUPS = [
    ("EUROPE", NAVY, [
        (14, "Lviv", "Rail-station strike kills two", "Reuters"),
        (15, "Kyiv", "UNICEF: at least 1,144 children killed or hurt, Jan–Oct", "UNICEF"),
        (16, "Tallinn", "Estonia suspends Russia road crossings 1 Dec", "Reuters"),
        (17, "Frankfurt", "STOXX 600 ends worst week since Mar 2025", "Reuters"),
        (18, "Italy", "General strike: workers and students march in "
         "100+ cities over pay, services", "Reuters"),
    ]),
    ("ASIA", TEAL, [
        (19, "New Delhi", "Pakistan's climate minister visits for SCO forum", "IANS"),
        (20, "Beijing", "Loan prime rates held an 18th month", "Xinhua"),
        (21, "Indonesia", "Government plans tighter controls on soybean "
         "imports, official says", "Reuters"),
        (22, "Myanmar", "rejects ICJ ruling on Rohingya genocide", "Reuters"),
        (23, "Tokyo", "Inflation rises to 2.3% in October; core +2.2%, "
         "December rise in view", "Statistics Bureau"),
    ]),
    ("MIDDLE EAST", GOLD, [
        (24, "Gaza", "Strikes kill six despite the truce", "AFP"),
        (25, "Hodeidah", "Coalition strikes hit the port", "Reuters"),
    ]),
    ("OCEANIA", GREEN, [
        (26, "New Zealand", "Drug offences account for 7.5% of all "
         "charges, a 10-year high", "NZ Drug Foundation"),
    ]),
    ("AMERICAS", SLATE, [
        (27, "Washington", "Raskin: save every record, incl. apps", "Reuters"),
        (28, "Washington", "Fed's Cook argues for more rate hikes", "Reuters"),
        (29, "Washington", "Second judge moves to block Trump's arch", "AP"),
        (30, "New York", "Anthropic -8.5% day two, still above $83 debut", "Reuters"),
        (31, "Santa Clara", "Nvidia -14%; SEC eyes its accounting", "Reuters"),
        (32, "Uruguay", "In Seoul, South Korea asks Uruguay to help "
         "restart Mercosur trade talks", "Yonhap"),
    ]),
    ("AFRICA", RUST, [
        (33, "South Africa", "Former deputy president and UN Women chief "
         "Phumzile Mlambo-Ngcuka dies", "SA Presidency"),
        (34, "Rabat", "Morocco plans €366m defence industry", "Euronews"),
        (35, "Kimberley", "Council elects Isaac Ruiter mayor of Sol Plaatje",
         "Diamond Fields Advertiser"),
        (36, "Nigeria", "At least four die as funeral boat capsizes in "
         "Bayelsa, police say", "Reuters"),
    ]),
]


# ---------------------------------------------------------------- illustrations

def illus_kyiv(d, box):
    """Night sky over a bridge: dashed missile trails, burst stars."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(13, 26, 46))
    # stars
    for sx, sy in [(0.06, 0.18), (0.16, 0.08), (0.30, 0.22), (0.44, 0.10),
                   (0.58, 0.20), (0.70, 0.07), (0.84, 0.16), (0.93, 0.30),
                   (0.24, 0.34), (0.66, 0.34)]:
        px, py = x0 + sx * (x1 - x0), y0 + sy * (y1 - y0)
        d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=(210, 220, 235))
    # missile trails (dashed arcs falling to the right)
    import math
    for k, (ax, ay, bx, by) in enumerate([
            (0.30, 0.04, 0.62, 0.52), (0.52, 0.02, 0.80, 0.48),
            (0.10, 0.06, 0.44, 0.55)]):
        pts = []
        for t in [i / 26 for i in range(27)]:
            px = x0 + (ax + (bx - ax) * t) * (x1 - x0)
            py = y0 + (ay + (by - ay) * t * t) * (y1 - y0)
            pts.append((px, py))
        for i in range(0, len(pts) - 1, 2):
            d.line([pts[i], pts[i + 1]], fill=(240, 190, 90), width=3)
        ex, ey = pts[-1]
        for ang in range(0, 360, 45):
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            d.line([ex, ey, ex + dx * 13, ey + dy * 13], fill=(245, 150, 60), width=3)
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(250, 190, 90))
    # river + bridge silhouette
    ry = y0 + 0.80 * (y1 - y0)
    d.rectangle([x0, ry, x1, y1], fill=(10, 20, 34))
    by = y0 + 0.78 * (y1 - y0)
    d.rectangle([x0, by, x1, by + 5], fill=(4, 8, 14))
    for fx in (0.30, 0.66):
        px = x0 + fx * (x1 - x0)
        d.rectangle([px - 4, by - 44, px + 4, by + 4], fill=(4, 8, 14))
        d.line([px, by - 44, x0 + (fx - 0.22) * (x1 - x0), by], fill=(4, 8, 14), width=3)
        d.line([px, by - 44, x0 + (fx + 0.22) * (x1 - x0), by], fill=(4, 8, 14), width=3)
    for fx in (0.10, 0.48, 0.86):
        px = x0 + fx * (x1 - x0)
        d.rectangle([px, by + 5, px + 3, y1], fill=(4, 8, 14))
    # flames on the deck
    for fx, fh in [(0.44, 16), (0.80, 12)]:
        px, py = x0 + fx * (x1 - x0), by
        d.polygon([(px - 8, py), (px, py - fh), (px + 8, py)], fill=(240, 130, 40))
        d.polygon([(px - 4, py), (px, py - fh * 0.6), (px + 4, py)], fill=(250, 200, 90))
    f = F(SANS_BLACK, 25)
    d.rectangle([x0 + 10, y0 + 10, x0 + 10 + tw(d, "KYIV", f) + 18, y0 + 48], fill=RED)
    d.text((x0 + 19, y0 + 15), "KYIV", font=f, fill=WHITE)
    f2 = F(SANS_BOLD, 13)
    label = "3 bridges hit"
    d.rectangle([x0 + 10, y0 + 54, x0 + 10 + tw(d, label, f2) + 14, y0 + 78],
                fill=(10, 16, 26))
    d.text((x0 + 17, y0 + 58), label, font=f2, fill=WHITE)
    banner_tag(d, box, "Ukrainian officials · Reuters")


def illus_akvan(d, box):
    """A cyclone spiral making landfall on a coast."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=SEA)
    # land mass on the left
    land = [(x0, y0), (x0 + 0.42 * (x1 - x0), y0),
            (x0 + 0.36 * (x1 - x0), y0 + 0.30 * (y1 - y0)),
            (x0 + 0.44 * (x1 - x0), y0 + 0.58 * (y1 - y0)),
            (x0 + 0.34 * (x1 - x0), y1), (x0, y1)]
    d.polygon(land, fill=LAND)
    d.line(land + [land[0]], fill=(150, 128, 84), width=2)
    f = F(SANS_BOLD, 11)
    d.text((x0 + 14, y0 + 12), "ODISHA", font=f, fill=(90, 74, 40))
    d.text((x0 + 14, y0 + 27), "INDIA", font=f, fill=(90, 74, 40))
    # spiral
    import math
    cx, cy = x0 + 0.60 * (x1 - x0), y0 + 0.46 * (y1 - y0)
    for arm in range(3):
        pts = []
        for i in range(46):
            t = i / 45
            ang = arm * 2.1 + t * 4.6
            r = 8 + t * 62
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.82))
        d.line(pts, fill=WHITE, width=7)
        d.line(pts, fill=(226, 238, 242), width=3)
    d.ellipse([cx - 10, cy - 9, cx + 10, cy + 9], fill=WHITE)
    d.ellipse([cx - 5, cy - 4.5, cx + 5, cy + 4.5], fill=(120, 170, 190))
    # sea label drawn after the spiral so its arms never cross the text
    d.text((x0 + 0.46 * (x1 - x0), y1 - 27), "BAY OF BENGAL",
           font=F(SANS_BOLD, 10), fill=(52, 96, 116))
    # landfall marker on the coast
    mx, my = x0 + 0.40 * (x1 - x0), y0 + 0.52 * (y1 - y0)
    d.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=RED)
    f2 = F(SANS_BOLD, 11)
    tag = "Gopalpur · landfall"
    d.rectangle([mx + 10, my - 10, mx + 10 + tw(d, tag, f2) + 10, my + 12],
                fill=(20, 20, 20))
    d.text((mx + 15, my - 5), tag, font=f2, fill=WHITE)
    # the evacuation total, printed on the art beside the landfall point
    ev = "440,000+ evacuated"
    d.rectangle([mx + 10, my + 16, mx + 10 + tw(d, ev, f2) + 10, my + 38],
                fill=(20, 20, 20))
    d.text((mx + 15, my + 21), ev, font=f2, fill=WHITE)
    f3 = F(SANS_BLACK, 24)
    label = "CYCLONE AKVAN"
    w = tw(d, label, f3)
    d.rectangle([x1 - w - 28, y0 + 10, x1 - 10, y0 + 46], fill=RED)
    d.text((x1 - w - 19, y0 + 15), label, font=f3, fill=WHITE)
    banner_tag(d, box, "PTI")


def illus_selloff(d, box):
    """Friday's falls as a bar chart: three bars from one zero baseline."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 22, 26))
    f2 = F(SANS_BLACK, 25)
    d.rectangle([x0 + 10, y0 + 10, x0 + 10 + tw(d, "AI SELL-OFF", f2) + 18, y0 + 48],
                fill=RED)
    d.text((x0 + 19, y0 + 15), "AI SELL-OFF", font=f2, fill=WHITE)
    # caption + the sources, top-right of the art
    fc = F(SANS_BOLD, 12.5)
    cap = "Friday close"
    d.text((x1 - 12 - tw(d, cap, fc), y0 + 12), cap, font=fc,
           fill=(225, 222, 214))
    fs = F(SANS, 9.5)
    src = "Reuters · Yonhap"
    d.text((x1 - 12 - tw(d, src, fs), y0 + 29), src, font=fs,
           fill=(168, 164, 156))
    # bars: every bar starts at the same zero baseline (zx) and runs
    # left; lengths are proportional to the day's fall.
    bars = [("TAIPEI", 6.2), ("SEOUL", 5.2), ("TOKYO", 5.1)]
    zx = x0 + 238
    scale = 25.8            # px per percentage point
    fn = F(SANS_BOLD, 11.5)
    fv = F(SANS_XB, 12)
    by = y0 + 52
    for name, val in bars:
        d.text((x0 + 12, by), name, font=fn, fill=(225, 222, 214))
        d.rectangle([zx - val * scale, by + 1, zx, by + 12],
                    fill=(240, 92, 77))
        d.text((zx + 7, by), f"-{val}%", font=fv, fill=(240, 92, 77))
        by += 16
    d.line([zx, y0 + 48, zx, y0 + 98], fill=(190, 188, 180), width=2)


LEAD_ILLUS = {"kyiv": illus_kyiv, "akvan": illus_akvan, "selloff": illus_selloff}


def card_banner(d, box, label, kind, tag):
    """A small illustrated banner for a feature card."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # background by kind
    bg = {"flags": (38, 64, 110), "globe": (30, 84, 92), "missile": (96, 104, 88),
          "tanker": (44, 84, 108), "convoy": (104, 96, 74), "crowd": (150, 52, 44),
          "sunbars": (196, 120, 52), "court": (88, 80, 96), "derrick": (58, 92, 84),
          "cricket": (52, 104, 66), "virus": (94, 40, 56),
          "quake": (38, 72, 94)}[kind]
    d.rectangle(box, fill=bg)
    cx, cy = x0 + w * 0.72, y0 + h * 0.46
    if kind == "flags":
        # EU circle of stars + UK cross, abstracted
        import math
        for i in range(8):
            a = i * math.pi / 4
            sx, sy = cx - 26 + 13 * math.cos(a), cy + 13 * math.sin(a)
            d.ellipse([sx - 2.4, sy - 2.4, sx + 2.4, sy + 2.4], fill=GOLD)
        d.rectangle([cx + 11, cy - 17, cx + 45, cy + 17], fill=WHITE)
        d.rectangle([cx + 12, cy - 16, cx + 44, cy + 16], fill=(36, 52, 120))
        d.rectangle([cx + 24, cy - 16, cx + 32, cy + 16], fill=WHITE)
        d.rectangle([cx + 12, cy - 4, cx + 44, cy + 4], fill=WHITE)
        d.rectangle([cx + 25, cy - 16, cx + 31, cy + 16], fill=RED)
        d.rectangle([cx + 12, cy - 3, cx + 44, cy + 3], fill=RED)
    elif kind == "globe":
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=WHITE, width=3)
        d.ellipse([cx - 8, cy - 20, cx + 8, cy + 20], outline=WHITE, width=2)
        d.line([cx - 20, cy, cx + 20, cy], fill=WHITE, width=2)
        d.arc([cx + 26, cy - 18, cx + 58, cy + 14], start=300, end=120,
              fill=(250, 210, 90), width=4)
        d.polygon([(cx + 54, cy - 14), (cx + 62, cy - 2), (cx + 48, cy - 2)],
                  fill=(250, 210, 90))
    elif kind == "missile":
        d.polygon([(cx - 30, cy + 14), (cx + 18, cy - 16), (cx + 26, cy - 8),
                   (cx - 20, cy + 20)], fill=(226, 226, 220))
        d.polygon([(cx + 18, cy - 16), (cx + 30, cy - 18), (cx + 26, cy - 8)],
                  fill=RED)
        d.polygon([(cx - 30, cy + 14), (cx - 40, cy + 22), (cx - 26, cy + 24)],
                  fill=(250, 170, 70))
        d.rectangle([x0, y1 - 8, x1, y1], fill=(70, 84, 58))
    elif kind == "tanker":
        d.rectangle([x0, y0 + h * 0.68, x1, y1], fill=(30, 62, 84))
        d.polygon([(cx - 42, cy + 8), (cx + 42, cy + 8), (cx + 34, cy + 20),
                   (cx - 34, cy + 20)], fill=(30, 30, 34))
        d.rectangle([cx - 30, cy - 2, cx + 30, cy + 8], fill=(120, 44, 36))
        d.rectangle([cx + 16, cy - 12, cx + 26, cy - 2], fill=(220, 218, 210))
        d.polygon([(cx - 6, cy - 2), (cx, cy - 18), (cx + 6, cy - 2)],
                  fill=(240, 130, 40))
        d.polygon([(cx - 3, cy - 2), (cx, cy - 11), (cx + 3, cy - 2)],
                  fill=(250, 200, 90))
    elif kind == "convoy":
        for k, ox in enumerate((-38, 6)):
            bx, by = cx + ox, cy + 2
            d.rectangle([bx, by - 10, bx + 34, by + 4], fill=(52, 54, 44))
            d.rectangle([bx + 22, by - 16, bx + 32, by - 10], fill=(52, 54, 44))
            for wx in (bx + 7, bx + 26):
                d.ellipse([wx - 5, by + 1, wx + 5, by + 11], fill=(24, 24, 22))
        d.rectangle([x0, y1 - 8, x1, y1], fill=(84, 76, 56))
    elif kind == "crowd":
        for i in range(7):
            px = cx - 42 + i * 14
            py = cy + 8 + (4 if i % 2 else -2)
            d.ellipse([px - 4.5, py - 12, px + 4.5, py - 3], fill=(250, 236, 220))
            d.rectangle([px - 5, py - 3, px + 5, py + 10], fill=(250, 236, 220))
        # the placard sits at the banner's bottom-left, clear of the
        # red label block at top-left
        ft = F(SANS_BLACK, 9.5)
        d.rectangle([x0 + 7, y1 - 17, x0 + 7 + tw(d, "SCIOPERO", ft) + 10,
                     y1 - 3], fill=WHITE)
        d.text((x0 + 12, y1 - 15), "SCIOPERO", font=ft, fill=RED_DARK)
    elif kind == "sunbars":
        d.ellipse([cx - 34, cy - 15, cx - 4, cy + 15], fill=(250, 214, 110))
        for k, bh in enumerate((10, 18, 27)):
            bx = cx + 4 + k * 14
            d.rectangle([bx, cy + 15 - bh, bx + 10, cy + 15], fill=(120, 44, 32))
    elif kind == "court":
        d.polygon([(cx - 34, cy - 18), (cx + 34, cy - 18), (cx + 28, cy - 10),
                   (cx - 28, cy - 10)], fill=(226, 222, 210))
        for k in range(4):
            px = cx - 27 + k * 18
            d.rectangle([px, cy - 8, px + 7, cy + 12], fill=(226, 222, 210))
        d.rectangle([cx - 34, cy + 12, cx + 34, cy + 17], fill=(226, 222, 210))
    elif kind == "derrick":
        d.polygon([(cx - 6, cy - 24), (cx + 6, cy - 24), (cx + 16, cy + 16),
                   (cx - 16, cy + 16)], outline=(240, 238, 228), width=3)
        d.line([cx - 11, cy - 6, cx + 11, cy - 6], fill=(240, 238, 228), width=2)
        d.line([cx - 13, cy + 5, cx + 13, cy + 5], fill=(240, 238, 228), width=2)
        d.ellipse([cx + 22, cy - 20, cx + 38, cy - 4], fill=(250, 214, 110))
        d.rectangle([x0, y1 - 8, x1, y1], fill=(40, 66, 56))
    elif kind == "cricket":
        d.polygon([(cx - 30, cy + 16), (cx - 22, cy + 18), (cx + 8, cy - 14),
                   (cx + 2, cy - 18)], fill=(232, 204, 150))
        d.ellipse([cx + 18, cy + 2, cx + 32, cy + 16], fill=(196, 40, 34))
        d.arc([cx + 19, cy + 3, cx + 31, cy + 15], start=90, end=270,
              fill=WHITE, width=2)
    elif kind == "virus":
        import math
        for i in range(8):
            a = i * math.pi / 4
            ex, ey = cx + 17 * math.cos(a), cy + 17 * math.sin(a)
            d.line([cx, cy, ex, ey], fill=(240, 198, 200), width=3)
            d.ellipse([ex - 3.4, ey - 3.4, ex + 3.4, ey + 3.4],
                      fill=(240, 198, 200))
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(203, 92, 104))
        for dx, dy in [(-4, -3), (3, 2), (-1, 5), (4, -5)]:
            d.ellipse([cx + dx - 1.8, cy + dy - 1.8, cx + dx + 1.8,
                       cy + dy + 1.8], fill=(110, 28, 40))
    elif kind == "quake":
        # a small map: tan landmass on the sea ground; Junín inland
        # (epicentre rings), Lima on the coast south-west of it.
        land = [(x0 + 110, y0 + 3), (x0 + 150, y0 + 1), (x0 + 183, y0 + 8),
                (x0 + 185, y0 + 32), (x0 + 158, y0 + 41), (x0 + 116, y0 + 39),
                (x0 + 106, y0 + 22)]
        d.polygon(land, fill=LAND)
        d.line(land + [land[0]], fill=(150, 128, 84), width=1)
        jx, jy = x0 + 156, y0 + 15          # Junín, inland
        for r in (8, 4.5):
            d.ellipse([jx - r, jy - r, jx + r, jy + r], outline=RED, width=2)
        d.ellipse([jx - 2.2, jy - 2.2, jx + 2.2, jy + 2.2], fill=RED)
        fl = F(SANS_BOLD, 8.5)
        d.text((jx - 32, jy - 6), "Junín", font=fl, fill=(60, 48, 24))
        lx, ly = x0 + 118, y0 + 24          # Lima, on the coast
        d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=NAVY)
        d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], outline=WHITE, width=1)
        # the label rides on a small dark chip below the dot: plain
        # text there would sit half on the sea and be clipped by the
        # banner's red label block above it.
        lw = tw(d, "Lima", fl)
        d.rectangle([lx - 22, ly + 6, lx - 22 + lw + 8, ly + 17],
                    fill=(20, 20, 20))
        d.text((lx - 18, ly + 8), "Lima", font=fl, fill=WHITE)
    # label, top-left
    f = fit(d, label, SANS_BLACK, w - 16, 15, floor=10)
    d.rectangle([x0 + 7, y0 + 6, x0 + 7 + tw(d, label, f) + 12,
                 y0 + 6 + f.size + 9], fill=RED)
    d.text((x0 + 13, y0 + 10), label, font=f, fill=WHITE)
    banner_tag(d, box, tag)


# ---------------------------------------------------------------- sections

def masthead(d):
    f = F(SANS_BLACK, 13)
    d.text((M, 8), "THE WORLD IN ONE DAY", font=f, fill=RED)
    right = "36 STORIES · 7 REGIONS · EVERY ONE FROM FRIDAY 20 NOVEMBER 2026"
    fr = F(SANS_BOLD, 12)
    d.text((W - M - tw(d, right, fr), 9), right, font=fr, fill=INK)
    d.rectangle([M, 30, W - M, 33], fill=INK)
    title = "Friday 20 November 2026"
    ft = fit(d, title, SERIF_BLACK, CW, 60)
    ctext(d, W / 2, 38, title, ft)
    # No italic strap under the date: it repeated the three lead
    # headlines printed directly below. Its space went to the briefs
    # (every section below sits higher than in the previous draft).
    d.line([M, 112, W - M, 112], fill=RULE, width=1)


def numbers_strip(d):
    y0, y1 = 362, 418
    cell = CW / 6
    fc = F(SANS, 10.5)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + cell * i + cell / 2
        colour = RED if num.startswith("-") else INK
        # qualified figures ("Up to 100,000", "At least 1,144") are
        # longer than bare numerals: fit each figure to its cell.
        fn = fit(d, num, SERIF_BLACK, cell - 10, 28, floor=14)
        ctext(d, cx, y0, num, fn, fill=colour)
        lines = wrap(d, cap, fc, cell - 14)
        ly = y0 + 32
        for line in lines[:2]:
            ctext(d, cx, ly, line, fc, fill=INK_SOFT)
            ly += 11
        if i:
            d.line([M + cell * i, y0 + 4, M + cell * i, y1 - 4],
                   fill=RULE, width=1)
    d.line([M, y1, W - M, y1], fill=RULE, width=1)


def region_bar(d):
    y0, y1 = 424, 440
    labels = [(f"{name} {n}", n, colour) for name, n, colour in REGIONS]
    f = F(SANS_BOLD, 11)
    bases = [tw(d, label, f) + 18 for label, _, _ in labels]
    extra = CW - sum(bases)
    total = sum(n for _, n, _ in labels)
    x = M
    for (label, n, colour), base in zip(labels, bases):
        wseg = base + extra * n / total
        d.rectangle([x, y0, x + wseg, y1], fill=colour)
        ctext(d, x + wseg / 2, y0 + 2.5, label, f, fill=WHITE)
        x += wseg


def leads(d):
    # leads sit directly under the masthead: at the 300 px preview the
    # three lead headlines must dominate, ahead of the numbers strip.
    y0 = 118
    col_w, gap = 318, 11
    for i, lead in enumerate(LEADS):
        x = M + i * (col_w + gap)
        box = (x, y0, x + col_w, y0 + 100)
        LEAD_ILLUS[lead["illus"]](d, box)
        ky = y0 + 108
        chip(d, x + 11, ky + 7, lead["num"])
        fk = F(SANS_BOLD, 12.5)
        d.text((x + 28, ky), lead["place"], font=fk, fill=RED)
        pw = tw(d, lead["place"], fk)
        d.text((x + 28 + pw + 6, ky), "· " + lead["field"], font=fk, fill=INK)
        fh = fit(d, lead["headline"], SERIF_BOLD, col_w, 27, floor=20)
        lines = wrap(d, lead["headline"], fh, col_w)
        hy = ky + 20
        for line in lines[:2]:
            d.text((x, hy), line, font=fh, fill=INK)
            hy += 30
        fb = F(SANS, 13)
        by = ky + 20 + 2 * 30 + 4
        for line in wrap(d, lead["body"], fb, col_w)[:3]:
            d.text((x, by), line, font=fb, fill=INK_SOFT)
            by += 16.5


def cards(d):
    rows_y = [448, 565]
    col_w, gap = 187, 10
    for idx, (num, label, kind, tag, kicker, headline, sub) in enumerate(CARDS):
        row, col = divmod(idx, 5)
        x = M + col * (col_w + gap)
        y = rows_y[row]
        card_banner(d, (x, y, x + col_w, y + 42), label, kind, tag)
        ky = y + 47
        chip(d, x + 8, ky + 6, num, r=8.5)
        fk = fit(d, kicker, SANS_BOLD, col_w - 22, 10.5, floor=8.5)
        d.text((x + 21, ky), kicker, font=fk, fill=RED)
        # headline: largest size (<= 16) that wraps to at most 2 lines,
        # so a long headline (Kenya) shrinks instead of overflowing.
        # The cricket card starts larger (18): its banner no longer
        # carries the 118, so the headline gets the room instead.
        size = 18 if num == 13 else 16
        fh = F(SANS_XB, size)
        hlines = wrap(d, headline, fh, col_w)
        while len(hlines) > 2 and size > 11:
            size -= 1
            fh = F(SANS_XB, size)
            hlines = wrap(d, headline, fh, col_w)
        hy = ky + 12
        for line in hlines[:2]:
            d.text((x, hy), line, font=fh, fill=INK)
            hy += fh.size + 0.5
        fs = F(SANS, 10.5)
        sy = hy + 1
        for line in wrap(d, sub, fs, col_w)[:2]:
            d.text((x, sy), line, font=fs, fill=INK_SOFT)
            sy += 10


BRIEF_SIZES = [15, 14.5, 14, 13.5, 13, 12.5, 12, 11.5]


def brief_lines(d, size, max_w, num, place, text, source):
    """Wrap one brief at the given size; returns (lines, indent).
    Continuation lines hang-indent under the place name."""
    fn = F(SANS_BOLD, size)
    ft = F(SANS, size)
    segs = [(str(num), fn, RED), (place, fn, INK),
            ("— " + text, ft, INK_SOFT), (f"({source})", ft, GREY)]
    words = []
    for t, f, c in segs:
        for w in t.split():
            words.append((w, f, c))
    space = tw(d, " ", ft)
    indent = tw(d, f"{num} ", fn)
    lines, cur, curw = [], [], 0.0
    limit = max_w
    for w, f, c in words:
        ww = tw(d, w, f)
        add = ww if not cur else ww + space
        if cur and curw + add > limit:
            lines.append(cur)
            cur, curw = [], 0.0
            limit = max_w - indent
            add = ww
        cur.append((w, f, c))
        curw += add
    if cur:
        lines.append(cur)
    return lines, indent


def bottom(d):
    # The world map and the DATE CHECK box are gone: the briefs take
    # the whole width in two columns, grouped by region under small
    # coloured headers. The brief size auto-fits: the largest size
    # whose tallest column still ends above the footer is used, so
    # the text is as big as the page allows.
    hy = 685
    fh = F(SANS_BLACK, 13)
    d.text((M, hy), "ALSO ON FRIDAY 20 NOVEMBER", font=fh, fill=RED)
    right = "23 MORE STORIES · GROUPED BY REGION"
    d.text((W - M - tw(d, right, fh), hy), right, font=fh, fill=INK)
    d.line([M, 705, W - M, 705], fill=RULE, width=1)
    top, limit_y = 711, 1002
    # left column: Europe, Asia, Middle East, Oceania (BRIEF_GROUPS[:4]);
    # right column: Americas, Africa — the balanced split.
    col_groups = [BRIEF_GROUPS[:4], BRIEF_GROUPS[4:]]
    col_x = [M, 518]
    col_w = 482
    header_h, gap = 15, 1.0

    def layout(size):
        pitch = size + 0.7
        cols, bottoms = [], []
        for groups in col_groups:
            y = top
            col = []
            for name, colour, items in groups:
                y += header_h
                for num, place, text, source in items:
                    lines, indent = brief_lines(d, size, col_w,
                                                num, place, text, source)
                    col.append((lines, indent))
                    y += len(lines) * pitch
                y += gap
            cols.append(col)
            bottoms.append(y)
        return cols, bottoms

    size, cols = BRIEF_SIZES[-1], None
    for cand in BRIEF_SIZES:
        trial, bottoms = layout(cand)
        cols = trial
        if max(bottoms) <= limit_y:
            size = cand
            break
    pitch = size + 0.7
    space = tw(d, " ", F(SANS, size))
    for groups, x, col in zip(col_groups, col_x, cols):
        y = top
        li = 0
        for name, colour, items in groups:
            d.rectangle([x, y + 2, x + 9, y + 11], fill=colour)
            d.text((x + 14, y), name, font=F(SANS_BLACK, 12.5), fill=INK)
            y += header_h
            for _ in items:
                lines, indent = col[li]
                li += 1
                for k, line in enumerate(lines):
                    lx = x if k == 0 else x + indent
                    for w, f, c in line:
                        d.text((lx, y), w, font=f, fill=c)
                        lx += tw(d, w, f) + space
                    y += pitch
            y += gap


def footer(d):
    f = F(SANS, 10)
    left = ("Every story here happened, or was first reported, on Friday "
            "20 November 2026. Contested claims are attributed.")
    d.text((M, 1009), left, font=f, fill=GREY)
    right = "Sources named beside each story · Original drawings"
    d.text((W - M - tw(d, right, f), 1009), right, font=f, fill=GREY)


def build():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    leads(d)
    numbers_strip(d)
    region_bar(d)
    cards(d)
    bottom(d)
    footer(d)
    return img


def main(argv):
    stage = argv[1] if len(argv) > 1 else "final"
    if stage != "final":
        print(f"generate_b.py: unknown stage {stage!r} (only 'final')",
              file=sys.stderr)
        return 2
    img = build()
    out = Path("output")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "entry.png"
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {path} ({path.stat().st_size} bytes, {img.size[0]}x{img.size[1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
