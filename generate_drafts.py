#!/usr/bin/env python3
"""Evaluation drafts for make.fun news-image-20261120 (v2).
Draft A: one big lead. Draft B: two leads side by side. Same news set.
All stories verified as 20 Nov 2026 events (see sources.md).
Icons are drawn normalized to their box so nothing spills into text.
Briefs are enforced single-line so the block can never overflow.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PAPER = (246, 241, 231)
CARD = (255, 253, 247)
INK = (20, 22, 26)
RED = (178, 32, 42)
NAVY = (29, 78, 137)
GOLD = (190, 130, 30)
GREY = (96, 96, 92)
LIGHT = (226, 219, 203)

_fc = {}
def F(path, size):
    key = (path, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]

def fit_font(d, text, path, max_w, start):
    s = start
    while s > 10 and d.textlength(text, font=F(path, s)) > max_w:
        s -= 1
    return F(path, s)

def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------- icons: all coordinates are fractions of the box ----------------
def _xy(b, fx, fy):
    return (b[0] + fx*(b[2]-b[0]), b[1] + fy*(b[3]-b[1]))

def icon_bridge(d, b, c):
    w = max(4, int(0.05*(b[2]-b[0])))
    d.line([_xy(b, .04, .72), _xy(b, .96, .72)], fill=c, width=w)
    for fx in (.18, .78):
        d.line([_xy(b, fx, .72), _xy(b, fx, .22)], fill=c, width=w)
    d.arc([b[0]+.06*(b[2]-b[0]), b[1]+.02*(b[3]-b[1]), b[0]+.94*(b[2]-b[0]), b[1]+.78*(b[3]-b[1])], 180, 335, fill=c, width=max(3, w-2))
    for i in range(3):
        x = b[0] + (.06+i*.3)*(b[2]-b[0]); y = b[1] + .84*(b[3]-b[1])
        d.arc([x, y-6, x+.22*(b[2]-b[0]), y+6], 0, 180, fill=NAVY, width=4)
    d.line([_xy(b, .68, .06), _xy(b, .88, .26)], fill=RED, width=w+3)
    d.polygon([_xy(b, .63, .02), _xy(b, .72, .07), _xy(b, .65, .13)], fill=GOLD)

def icon_chart(d, b, c):
    w = max(4, int(0.06*(b[2]-b[0])))
    d.line([_xy(b, .1, .06), _xy(b, .1, .9)], fill=c, width=w)
    d.line([_xy(b, .1, .9), _xy(b, .94, .9)], fill=c, width=w)
    pts = [_xy(b, .16, .18), _xy(b, .38, .36), _xy(b, .55, .28), _xy(b, .74, .6), _xy(b, .9, .84)]
    d.line(pts, fill=RED, width=w+2)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex-16, ey-3), (ex-4, ey-15)], fill=RED)

def icon_cyclone(d, b, c):
    cx, cy = _xy(b, .5, .5); R = .44*(b[2]-b[0])
    for r, a0 in ((R, 200), (R*.68, 20), (R*.36, 230)):
        d.arc([cx-r, cy-r, cx+r, cy+r], a0, a0+250, fill=c, width=max(4, int(R*.16)))
    d.ellipse([cx-6, cy-6, cx+6, cy+6], fill=RED)

def icon_stars(d, b, c):
    cx, cy = _xy(b, .5, .5); R = .37*(b[2]-b[0]); s = .085*(b[2]-b[0])
    for k in range(8):
        a = math.radians(k*45)
        sx, sy = cx+R*math.cos(a), cy+R*math.sin(a)
        d.polygon([(sx, sy-s), (sx+s*.35, sy-s*.25), (sx+s, sy-s*.2), (sx+s*.45, sy+s*.25),
                   (sx+s*.65, sy+s), (sx, sy+s*.45), (sx-s*.65, sy+s), (sx-s*.45, sy+s*.25),
                   (sx-s, sy-s*.2), (sx-s*.35, sy-s*.25)], fill=GOLD)
    r2 = .19*(b[2]-b[0])
    d.arc([cx-r2, cy-r2, cx+r2, cy+r2], 300, 130, fill=c, width=5)
    d.arc([cx-r2, cy-r2, cx+r2, cy+r2], 120, 310, fill=c, width=5)

def icon_thermo(d, b, c):
    cx, _ = _xy(b, .5, .5)
    top, bot = _xy(b, 0, .06)[1], _xy(b, 0, .94)[1]
    d.rounded_rectangle([cx-8, top, cx+8, bot-22], 8, outline=c, width=5)
    d.ellipse([cx-15, bot-38, cx+15, bot-8], outline=c, width=5)
    d.ellipse([cx-7, bot-30, cx+7, bot-16], fill=RED)
    d.line([cx, bot-28, cx, top+22], fill=RED, width=5)
    for fx, fy in ((.14, .16), (.86, .16), (.08, .38), (.92, .38)):
        x, y = _xy(b, fx, fy)
        d.line([x, y, cx+(x-cx)*.55, y+5], fill=GOLD, width=4)

def icon_ship(d, b, c):
    d.polygon([_xy(b, .06, .68), _xy(b, .94, .68), _xy(b, .82, .86), _xy(b, .18, .86)], outline=c, width=5)
    d.rectangle([_xy(b, .26, .5), _xy(b, .5, .66)], outline=c, width=4)
    d.rectangle([_xy(b, .54, .54), _xy(b, .74, .66)], outline=c, width=4)
    fx, fy = _xy(b, .5, .08)
    d.polygon([(fx, fy), (fx-10, fy+20), (fx, fy+14), (fx+10, fy+20)], fill=RED)
    d.polygon([(fx, fy+9), (fx-5, fy+19), (fx+5, fy+19)], fill=GOLD)
    for i in range(3):
        x = b[0] + (.08+i*.3)*(b[2]-b[0]); y = b[1] + .93*(b[3]-b[1])
        d.arc([x, y-4, x+.2*(b[2]-b[0]), y+4], 0, 180, fill=NAVY, width=3)

def icon_banner(d, b, c):
    d.line([_xy(b, .14, .06), _xy(b, .14, .94)], fill=c, width=6)
    d.polygon([_xy(b, .14, .1), _xy(b, .94, .18), _xy(b, .84, .34), _xy(b, .94, .48), _xy(b, .14, .44)], outline=RED, width=5)
    d.line([_xy(b, .26, .23), _xy(b, .78, .28)], fill=c, width=4)
    d.line([_xy(b, .26, .33), _xy(b, .74, .37)], fill=c, width=4)
    for fx in (.36, .58, .8):
        x, _ = _xy(b, fx, 0)
        d.line([x, b[1]+.78*(b[3]-b[1]), x, b[1]+.94*(b[3]-b[1])], fill=c, width=4)
        d.ellipse([x-4, b[1]+.66*(b[3]-b[1]), x+4, b[1]+.74*(b[3]-b[1])], fill=c)

def icon_drill(d, b, c):
    cx, _ = _xy(b, .5, .5)
    d.polygon([_xy(b, .24, .74), _xy(b, .5, .08), _xy(b, .76, .74)], outline=c, width=5)
    d.line([_xy(b, .36, .5), _xy(b, .64, .5)], fill=c, width=4)
    d.line([_xy(b, .43, .3), _xy(b, .57, .3)], fill=c, width=4)
    d.line([cx, b[1]+.08*(b[3]-b[1]), cx, b[1]+.7*(b[3]-b[1])], fill=RED, width=4)
    for i in range(3):
        x = b[0] + (.08+i*.3)*(b[2]-b[0]); y = b[1] + .86*(b[3]-b[1])
        d.arc([x, y-5, x+.22*(b[2]-b[0]), y+5], 0, 180, fill=NAVY, width=4)

def icon_records(d, b, c):
    # archive/records box: lid, box body, label slot and handle
    d.rectangle([_xy(b, .08, .16), _xy(b, .92, .42)], outline=c, width=5)
    d.rectangle([_xy(b, .15, .42), _xy(b, .85, .92)], outline=c, width=5)
    d.line([_xy(b, .38, .29), _xy(b, .62, .29)], fill=RED, width=5)
    d.line([_xy(b, .4, .64), _xy(b, .6, .64)], fill=c, width=5)

def icon_shield(d, b, c):
    cx, _ = _xy(b, .5, .5)
    d.polygon([_xy(b, .14, .1), _xy(b, .86, .1), _xy(b, .86, .62), _xy(b, .5, .94), _xy(b, .14, .62)], outline=c, width=5)
    my = b[1] + .44*(b[3]-b[1])
    d.line([cx-13, my, cx-4, my+11], fill=RED, width=5)
    d.line([cx-4, my+11, cx+15, my-13], fill=RED, width=5)

def icon_scales(d, b, c):
    cx, _ = _xy(b, .5, .5)
    d.line([cx, b[1]+.1*(b[3]-b[1]), cx, b[1]+.86*(b[3]-b[1])], fill=c, width=5)
    d.line([_xy(b, .12, .18), _xy(b, .88, .18)], fill=c, width=5)
    d.line([_xy(b, .28, .88), _xy(b, .72, .88)], fill=c, width=5)
    for fx in (.22, .78):
        px, py = _xy(b, fx, .18)
        d.line([px, py, px-11, py+20], fill=c, width=3)
        d.line([px, py, px+11, py+20], fill=c, width=3)
        d.arc([px-14, py+13, px+14, py+30], 0, 180, fill=RED, width=4)

ICONS = {"bridge": icon_bridge, "chart": icon_chart, "cyclone": icon_cyclone,
         "stars": icon_stars, "thermo": icon_thermo, "ship": icon_ship,
         "banner": icon_banner, "drill": icon_drill, "shield": icon_shield,
         "scales": icon_scales, "records": icon_records}

# ---------------- content (verified 20 Nov 2026 — see sources.md) ----------------
CARDS = [
    (1, "KYIV", "bridge",
     "Russia's biggest barrage of the year: 110+ missiles & 400+ drones; "
     "3 Dnipro bridges hit, power cut — 9 dead, Kyiv says"),
    (2, "TOKYO", "chart",
     "AI sell-off sinks Asia stocks: Nikkei −4.8%, Taiwan's worst week "
     "since 1990 — Asia set for its worst week since 2020"),
    (3, "GOPALPUR", "cyclone",
     "Cyclone Akvan comes ashore on India's Odisha coast; 300,000+ "
     "evacuated — no major loss of life, officials say"),
    (4, "BRUSSELS", "stars",
     "UK & EU seal Brexit 'reset' deal: food checks end, 100,000 youth "
     "visas — tuition talks go on"),
    (5, "ANTALYA", "thermo",
     "COP31 endgame: draft deal drops fossil-fuel phase-out; talks "
     "spill past the deadline"),
    (6, "STRAIT OF HORMUZ", "ship",
     "Tanker ablaze after projectile strike off Oman; Iran's Guards "
     "say it hit a mine"),
    (7, "ROME", "banner",
     "General strike: workers & students march in 100+ cities over "
     "pay & public services"),
    (8, "WASHINGTON", "drill",
     "US auctions first-ever deep-sea mining leases, defying a "
     "court ruling"),
    (9, "RABAT", "shield",
     "Morocco commits €366m to build a national defence industry "
     "by 2035"),
    (10, "JOHANNESBURG", "scales",
     "High Court examines asylum seekers' detention at the Lindela "
     "centre"),
]

# Single-line briefs (width-checked in briefs_block; legibility beats count)
BRIEFS = [
    (11, "Kyiv", "UNICEF: 1,144 child casualties in 2026, most in 3 yrs"),
    (12, "Tatarstan", "Ukraine hits Druzhba oil station, Kyiv says"),
    (13, "Poland", "Russian missiles & a drone fell on Polish soil"),
    (14, "Moscow", "Ryabkov rules out NATO for Ukraine — via TASS"),
    (15, "Tallinn", "Estonia: Russia border shut 6+ months from 1 Dec"),
    (16, "Kharg Island", "Iran readies convoy to test US blockade"),
    (17, "Washington", "Protesters demand human control of AI"),
    (18, "New York", "Anthropic shares slide after record IPO"),
    (19, "New York", "Global stocks fall 7th day, worst run since 2023"),
    (20, "Jakarta", "Fire losses could reach $30bn, researchers say"),
    (21, "Antarctica", "Giant ancient supermountains under the ice"),
    (22, "Wellington", "Debate: NZ as Australia's seventh state?"),
    (23, "Berlin", "Merz: no great-power deal over Europe's head"),
    (24, "Quito", "US defence secretary Hegseth lands in Ecuador"),
    (25, "Across Europe", "Students protest living costs in 6 lands"),
]

FOOTER = ("EVALUATION DRAFT — NOT SUBMITTED · news-image-20261120 · "
          "Sources: Reuters, BBC, CNN, AP, IMD, UN News, France 24, Euronews, The Hindu (see sources.md)")

# ---------------- drawing helpers ----------------
def chip(d, cx, cy, num, r=14):
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=RED)
    t = str(num); f = F(SANS_B, 17 if r < 15 else 19)
    d.text((cx - d.textlength(t, font=f)/2, cy-r+3), t, font=f, fill=(255, 255, 255))

def card(d, box, num, place, body, icon, big=False):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=3)
    iw = 112 if big else 58
    ICONS[icon](d, (x0+10, y0+10, x0+10+iw, y0+10+iw), INK)
    chip(d, x1-24, y0+24, num, r=15 if big else 13)
    tx = x0 + 20 + iw
    ps = 46 if big else 25
    pf = fit_font(d, place, SANS_B, x1-tx-44, ps)
    d.text((tx, y0+9), place, font=pf, fill=INK)
    body_top = y0 + 14 + pf.size
    avail_h = y1 - body_top - 6
    bs = 27 if big else 19
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, x1-tx-10)
        if len(lines) * (bs+6) <= avail_h:
            break
        bs -= 1
    f = F(SANS, bs)
    yy = body_top
    for ln in wrap(d, body, f, x1-tx-10):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 6

def lead_card(d, box, num, place, body, icon):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=4)
    ICONS[icon](d, (x0+16, y0+30, x0+186, y0+200), INK)
    chip(d, x1-28, y0+28, num, r=16)
    tx = x0 + 206
    d.text((tx, y0+14), place, font=F(SANS_B, 56), fill=RED)
    bs = 29
    while bs > 14:
        f = F(SANS, bs)
        lines = wrap(d, body, f, x1-tx-14)
        if len(lines) * (bs+8) <= y1-y0-96:
            break
        bs -= 1
    f = F(SANS, bs)
    yy = y0 + 86
    for ln in wrap(d, body, f, x1-tx-14):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 8

def masthead(d, W=1024):
    d.text((W/2, 16), "T H E   W O R L D   I N   O N E   I M A G E",
           font=F(SANS_B, 21), fill=NAVY, anchor="ma")
    df = fit_font(d, "FRIDAY · 20 NOVEMBER 2026", SERIF_B, W-70, 74)
    d.text((W/2, 44), "FRIDAY · 20 NOVEMBER 2026", font=df, fill=INK, anchor="ma")
    d.line([28, 128, W-28, 128], fill=INK, width=5)
    d.line([28, 136, W-28, 136], fill=INK, width=2)

def briefs_block(d, top, items):
    d.text((28, top), "IN BRIEF — THE REST OF THE DAY", font=F(SANS_B, 19), fill=NAVY)
    d.line([28, top+27, 996, top+27], fill=LIGHT, width=2)
    col_x = [28, 524]; col_w = 462
    per = (len(items)+1)//2
    cols = [items[:per], items[per:]]
    bf = F(SANS, 14); bfb = F(SANS_B, 14)
    for ci, col in enumerate(cols):
        yy = top + 36
        for num, place, text in col:
            head = f"{num}. {place} — "
            w_head = d.textlength(head, font=bfb)
            w_rest = d.textlength(text, font=bf)
            assert w_head + w_rest <= col_w, f"brief too wide: {head}{text}"
            d.text((col_x[ci], yy), head, font=bfb, fill=INK)
            d.text((col_x[ci] + w_head, yy), text, font=bf, fill=INK)
            yy += 17
        assert yy <= 984, f"briefs overflow: col {ci} ends {yy}"
    d.line([28, 986, 996, 986], fill=INK, width=2)
    ff = fit_font(d, FOOTER, SANS, 968, 14)
    d.text((512, 991), FOOTER, font=ff, fill=GREY, anchor="ma")

def base():
    img = Image.new("RGB", (1024, 1024), PAPER)
    return img, ImageDraw.Draw(img)

ROWS = [(388, 528), (538, 668), (678, 798)]

def draft_a():
    img, d = base()
    masthead(d)
    n, p, ic, body = CARDS[0]
    lead_card(d, (28, 148, 996, 378), n, p, body, ic)
    idx = 1
    for (ry0, ry1) in ROWS:
        for c in range(3):
            n, p, ic, body = CARDS[idx]
            x0 = 28 + c*328
            card(d, (x0, ry0, x0+312, ry1), n, p, body, ic)
            idx += 1
    briefs_block(d, 812, BRIEFS)
    return img

def draft_b():
    img, d = base()
    masthead(d)
    n, p, ic, body = CARDS[0]
    card(d, (28, 148, 500, 378), n, p, body, ic, big=True)
    n, p, ic, body = CARDS[1]
    card(d, (524, 148, 996, 378), n, p, body, ic, big=True)
    idx = 2
    for ri, (ry0, ry1) in enumerate(ROWS):
        cnt = 3 if ri < 2 else 2
        w = 312 if cnt == 3 else 472
        step = 328 if cnt == 3 else 496
        for c in range(cnt):
            n, p, ic, body = CARDS[idx]
            x0 = 28 + c*step
            card(d, (x0, ry0, x0+w, ry1), n, p, body, ic)
            idx += 1
    briefs_block(d, 812, BRIEFS)
    return img

# ---------------- REVISED DRAFT B (user revision spec, 21 Nov) ----------------
# No ranking chips, no process notes on the image; headlines enlarged.
# Kyiv/Asia lead text is the user's exact wording; Asia panel carries ONE number.
REV_CARDS = [
    ("GOPALPUR", "cyclone",
     "Cyclone Akvan comes ashore on India's Odisha coast; about 300,000 "
     "evacuated — no major loss of life, officials say"),
    ("BRUSSELS", "stars",
     "UK & EU seal Brexit 'reset' deal: food checks end, 100,000 youth "
     "visas — tuition talks go on"),
    ("ANTALYA", "thermo",
     "COP31 endgame: draft deal drops fossil-fuel phase-out; talks "
     "spill past the deadline"),
    ("STRAIT OF HORMUZ", "ship",
     "Tanker catches fire off Oman. UKMTO reports a projectile strike. "
     "Iran's Guards say the tanker hit a mine. No casualties reported."),
    ("ROME", "banner",
     "General strike: workers & students march in 100+ cities over "
     "pay & public services"),
    ("WASHINGTON", "drill",
     "US auctions first-ever deep-sea mining leases, defying a "
     "court ruling"),
    ("RABAT", "shield",
     "Morocco commits €366m to build a national defence industry "
     "by 2035"),
    ("JOHANNESBURG", "scales",
     "High Court examines asylum seekers' detention at the Lindela "
     "centre"),
]

# Six strongest briefs; Quito dropped (see sources-rev.md), Uruguay is the
# verified 20 Nov Latin America item; Wellington keeps Oceania.
REV_BRIEFS = [
    ("Kyiv", "UNICEF: 1,144 child casualties in Ukraine in 2026, most in 3 years"),
    ("Tallinn", "Estonia: Russia border shut 6+ months from 1 Dec"),
    ("Jakarta", "Fire losses could reach $30bn, researchers say"),
    ("New York", "Anthropic shares slide after record IPO"),
    ("Uruguay", "Korea seeks its help to restart Mercosur trade talks"),
    ("Wellington", "Debate: NZ as Australia's seventh state?"),
]

REV_FOOTER = ("Sources: Reuters · BBC · CNN · AP · Yonhap · IMD · UN News · "
              "France 24 · Euronews · The Hindu · The Post · Kyiv Independent")

def rev_lead(d, box, place, headline, subhead, body, icon, accent):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=4)
    ICONS[icon](d, (x0+16, y0+16, x0+106, y0+106), INK)
    plf = fit_font(d, place, SANS_B, x1-(x0+122)-12, 44)
    d.text((x0+122, y0+26), place, font=plf, fill=accent)
    tx = x0 + 18; tw = x1 - tx - 14
    hf = fit_font(d, headline, SERIF_B, tw, 41)
    yy = y0 + 122
    for ln in wrap(d, headline, hf, tw):
        d.text((tx, yy), ln, font=hf, fill=INK)
        yy += hf.size + 7
    sf = fit_font(d, subhead, SANS_B, tw, 27)
    yy += 2
    d.text((tx, yy), subhead, font=sf, fill=accent)
    yy += sf.size + 12
    bs = 21
    while bs > 12:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if yy + len(lines) * (bs + 7) <= y1 - 8:
            break
        bs -= 1
    f = F(SANS, bs)
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 7

def rev_card(d, box, place, body, icon):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=3)
    ICONS[icon](d, (x0+10, y0+10, x0+52, y0+52), INK)
    pf = fit_font(d, place, SANS_B, x1-x0-70, 27)
    d.text((x0+62, y0+16), place, font=pf, fill=INK)
    tx = x0 + 12; tw = x1 - tx - 10
    bs = 17
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if 62 + len(lines) * (bs + 5) <= y1 - y0 - 6:
            break
        bs -= 1
    f = F(SANS, bs)
    yy = y0 + 62
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 5

def rev_briefs(d, top, items):
    d.text((28, top), "IN BRIEF — THE REST OF THE DAY", font=F(SANS_B, 21), fill=NAVY)
    d.line([28, top+30, 996, top+30], fill=LIGHT, width=2)
    bf = F(SANS, 20); bfb = F(SANS_B, 20)
    yy = top + 42
    for place, text in items:
        head = f"{place} — "
        w_head = d.textlength(head, font=bfb)
        assert w_head + d.textlength(text, font=bf) <= 968, f"brief too wide: {head}{text}"
        d.text((28, yy), head, font=bfb, fill=INK)
        d.text((28 + w_head, yy), text, font=bf, fill=INK)
        yy += 28
    d.line([28, 980, 996, 980], fill=INK, width=2)
    ff = fit_font(d, REV_FOOTER, SANS, 968, 14)
    d.text((512, 986), REV_FOOTER, font=ff, fill=GREY, anchor="ma")

def draft_b_rev():
    img, d = base()
    masthead(d)
    rev_lead(d, (28, 152, 500, 432), "KYIV",
             "Russian strikes hit three Kyiv bridges",
             "At least 9 killed across Ukraine.",
             "110+ missiles & 400+ drones in the year's biggest barrage. "
             "The bridges are in Kyiv; the toll covers all of Ukraine "
             "(Ukrainian authorities).",
             "bridge", RED)
    rev_lead(d, (524, 152, 996, 432), "ASIA MARKETS",
             "Tech sell-off hits Asian markets",
             "Taiwan stocks fell 17% over the week.",
             "Shares tumbled across the region as investors dumped AI "
             "stocks, a day after Anthropic's record IPO debut.",
             "chart", NAVY)
    idx = 0
    for ri, ry0 in enumerate((446, 610)):
        for c in range(4):
            p, ic, body = REV_CARDS[idx]
            x0 = 28 + c*244
            rev_card(d, (x0, ry0, x0+228, ry0+150), p, body, ic)
            idx += 1
    rev_briefs(d, 768, REV_BRIEFS)
    return img

# ---------------- FINAL DRAFT (user final revision, 21 Nov) ----------------
# Top-panel headlines are the LARGEST text in their panels and use the user's
# exact wording. Kyiv body no longer repeats the casualty scope. Akvan gets a
# double-width panel. Anthropic brief removed; Uruguay/Wellington expanded.
import sys

FIN_FOOTER = ("Sources: Reuters · BBC · CNN · AP · Yonhap · IMD · UN News · "
              "France 24 · Euronews · The Hindu · The Post · Kyiv Independent")

def final_lead(d, box, place, headline, subhead, body, icon, accent):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=4)
    ICONS[icon](d, (x0+14, y0+12, x0+66, y0+64), INK)
    d.text((x0+80, y0+20), place, font=F(SANS_B, 24), fill=accent)
    tx = x0 + 18; tw = x1 - tx - 16
    hf = fit_font(d, headline, SERIF_B, tw, 52)
    yy = y0 + 70
    for ln in wrap(d, headline, hf, tw):
        d.text((tx, yy), ln, font=hf, fill=INK)
        yy += hf.size + 6
    yy += 2
    sf = fit_font(d, subhead, SANS_B, tw, 25)
    d.text((tx, yy), subhead, font=sf, fill=accent)
    yy += sf.size + 10
    bs = 19
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if yy + len(lines) * (bs + 7) <= y1 - 8:
            break
        bs -= 1
    f = F(SANS, bs)
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 7

def final_lead_kyiv(d, box, place, headline, subhead, body, icon, accent):
    # Kyiv variant: the headline names the actor ("RUSSIAN STRIKES HIT KYIV
    # BRIDGES") and wraps to two lines; compact spacing keeps it the panel's
    # largest text while the subhead and body still fit.
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=4)
    ICONS[icon](d, (x0+14, y0+10, x0+54, y0+50), INK)
    d.text((x0+68, y0+16), place, font=F(SANS_B, 22), fill=accent)
    tx = x0 + 18; tw = x1 - tx - 16
    hs = 36
    while hs > 20:
        hf = F(SERIF_B, hs)
        if len(wrap(d, headline, hf, tw)) <= 2:
            break
        hs -= 1
    hf = F(SERIF_B, hs)
    yy = y0 + 56
    for ln in wrap(d, headline, hf, tw):
        d.text((tx, yy), ln, font=hf, fill=INK)
        yy += hs + 3
    yy += 2
    sf = fit_font(d, subhead, SANS_B, tw, 22)
    d.text((tx, yy), subhead, font=sf, fill=accent)
    yy += sf.size + 5
    bs = 15
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if yy + len(lines) * (bs + 4) <= y1 - 6:
            break
        bs -= 1
    f = F(SANS, bs)
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 4

def final_wide(d, box, place, body, icon, headline=None):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=3)
    ICONS[icon](d, (x0+12, y0+12, x0+52, y0+52), INK)
    pf = fit_font(d, place, SANS_B, x1-x0-80, 24)
    d.text((x0+64, y0+20), place, font=pf, fill=INK)
    tx = x0 + 14; tw = x1 - tx - 12
    yy = y0 + 58
    if headline:
        hf = fit_font(d, headline, SERIF_B, tw, 30)
        for ln in wrap(d, headline, hf, tw):
            d.text((tx, yy), ln, font=hf, fill=INK)
            yy += hf.size + 5
        yy += 3
    bs = 18
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if yy + len(lines) * (bs + 6) <= y1 - 6:
            break
        bs -= 1
    f = F(SANS, bs)
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 6

def final_akvan(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=3)
    ICONS["cyclone"](d, (x0+14, y0+20, x0+110, y0+116), INK)
    tx = x0 + 126; tw = x1 - tx - 12
    hf = fit_font(d, "CYCLONE AKVAN HITS INDIA", SERIF_B, tw, 36)
    d.text((tx, y0+14), "CYCLONE AKVAN HITS INDIA", font=hf, fill=INK)
    body = ("Comes ashore near Gopalpur, on India's Odisha coast; about "
            "300,000 evacuated — no major loss of life, officials say")
    bs = 17
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if y0 + 58 + len(lines) * (bs + 6) <= y1 - 6:
            break
        bs -= 1
    f = F(SANS, bs)
    yy = y0 + 58
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 6

def final_card(d, box, place, body, icon):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD, outline=INK, width=3)
    ICONS[icon](d, (x0+10, y0+10, x0+50, y0+50), INK)
    pf = fit_font(d, place, SANS_B, x1-x0-66, 24)
    d.text((x0+60, y0+16), place, font=pf, fill=INK)
    tx = x0 + 12; tw = x1 - tx - 10
    bs = 17
    while bs > 11:
        f = F(SANS, bs)
        lines = wrap(d, body, f, tw)
        if 56 + len(lines) * (bs + 5) <= y1 - y0 - 6:
            break
        bs -= 1
    f = F(SANS, bs)
    yy = y0 + 56
    for ln in wrap(d, body, f, tw):
        d.text((tx, yy), ln, font=f, fill=INK)
        yy += bs + 5

FIN_BRIEFS = [
    ("Kyiv", "UNICEF: At least 1,144 children killed or injured in Ukraine, Jan–Oct 2026."),
    ("Tallinn", "Estonia to suspend road crossings with Russia from 1 Dec"),
    ("Indonesia", "Fire losses could reach $30bn, researchers say"),
    ("Uruguay", "Korea seeks its help, as Mercosur chair, to restart trade talks stalled since 2021"),
    ("Wellington", "NZ columnist David Farrar argues for joining Australia."),
]

def final_briefs(d, top, items):
    d.text((28, top), "IN BRIEF — THE REST OF THE DAY", font=F(SANS_B, 20), fill=NAVY)
    d.line([28, top+26, 996, top+26], fill=LIGHT, width=2)
    bf = F(SANS, 19); bfb = F(SANS_B, 19)
    yy = top + 36
    for place, text in items:
        head = f"{place} — "
        w_head = d.textlength(head, font=bfb)
        assert w_head + d.textlength(text, font=bf) <= 968, f"brief too wide: {head}{text}"
        d.text((28, yy), head, font=bfb, fill=INK)
        d.text((28 + w_head, yy), text, font=bf, fill=INK)
        yy += 24
    d.line([28, 960, 996, 960], fill=INK, width=2)
    ff = fit_font(d, FIN_FOOTER, SANS, 968, 14)
    d.text((512, 966), FIN_FOOTER, font=ff, fill=GREY, anchor="ma")

def draft_final():
    img, d = base()
    masthead(d)
    final_lead_kyiv(d, (28, 146, 500, 356), "KYIV",
                    "RUSSIAN STRIKES HIT KYIV BRIDGES",
                    "At least 9 killed across Ukraine.",
                    "110+ missiles & 400+ drones in one of the year's largest "
                    "barrages (Ukrainian authorities).",
                    "bridge", RED)
    final_lead(d, (524, 146, 996, 356), "ASIA MARKETS", "ASIAN TECH SELL-OFF",
               "Taiwan stocks fell 17% over the week.",
               "Shares tumbled as investors dumped AI stocks, a day after "
               "Anthropic's record IPO debut.",
               "chart", NAVY)
    # Row A: Akvan (wide) + Brussels (wide)
    final_akvan(d, (28, 368, 506, 508))
    final_wide(d, (522, 368, 996, 508), "BRUSSELS",
               "Brexit 'reset' sealed: youth scheme: up to 100,000 places "
               "each way per year, emissions link — tuition talks go on",
               "stars", headline="UK and EU agree to ease food checks")
    # Row B: Hormuz (wide) + Antalya (wide)
    final_wide(d, (28, 520, 506, 652), "STRAIT OF HORMUZ",
               "Tanker catches fire off Oman. UKMTO reports a projectile "
               "strike. Iran's Guards say the tanker hit a mine. "
               "No casualties reported.",
               "ship")
    final_wide(d, (522, 520, 996, 652), "ANTALYA",
               "COP31 endgame: draft deal drops fossil-fuel phase-out; "
               "talks spill past the deadline",
               "thermo")
    # Row C: four standard cards
    final_card(d, (28, 664, 261, 788), "ROME",
               "General strike: workers & students march in 100+ cities "
               "over pay & public services", "banner")
    final_card(d, (273, 664, 506, 788), "WASHINGTON",
               "Rep. Raskin warns Justice & Homeland Security chiefs to "
               "preserve all records, incl. Signal chats", "records")
    final_card(d, (518, 664, 751, 788), "RABAT",
               "Morocco commits €366m to build a national defence industry "
               "by 2035", "shield")
    final_card(d, (763, 664, 996, 788), "JOHANNESBURG",
               "High Court examines asylum seekers' detention at the "
               "Lindela centre", "scales")
    final_briefs(d, 796, FIN_BRIEFS)
    return img

def save_final():
    im = draft_final()
    p = os.path.join(OUT, "draft-final.png")
    im.save(p, optimize=True)
    if os.path.getsize(p) > 1024*1024:
        im.convert("P", palette=Image.ADAPTIVE, colors=256).save(p, optimize=True)
    outdir = os.path.join(OUT, "output")
    os.makedirs(outdir, exist_ok=True)
    ep = os.path.join(outdir, "entry.png")
    with open(p, "rb") as fsrc:
        data = fsrc.read()
    with open(ep, "wb") as fdst:
        fdst.write(data)
    # Preview MUST be a resize of the finished entry.png file itself.
    fin = Image.open(ep)
    prev = fin.resize((300, 300), Image.LANCZOS)
    pp = os.path.join(OUT, "draft-final-300.png")
    prev.save(pp, optimize=True)
    prev.save(os.path.join(outdir, "draft-final-300.png"), optimize=True)
    chk = Image.open(p); chkp = Image.open(pp)
    print("draft-final.png", chk.size, os.path.getsize(p), "bytes")
    print("output/entry.png", Image.open(ep).size, os.path.getsize(ep), "bytes")
    print("draft-final-300.png", chkp.size, os.path.getsize(pp), "bytes")

if __name__ == "__main__":
    if "final" in sys.argv:
        save_final()
        sys.exit(0)
    for name, fn in (("draft-a", draft_a), ("draft-b", draft_b), ("draft-b-rev", draft_b_rev)):
        im = fn()
        p = os.path.join(OUT, name + ".png")
        im.save(p, optimize=True)
        if os.path.getsize(p) > 1024*1024:
            im.convert("P", palette=Image.ADAPTIVE, colors=256).save(p, optimize=True)
        im.resize((300, 300), Image.LANCZOS).save(os.path.join(OUT, name + "-300.png"), optimize=True)
        print(name, im.size, os.path.getsize(p), "bytes")
