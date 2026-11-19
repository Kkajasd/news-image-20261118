#!/usr/bin/env python3
"""Draw the front page for news-image-20261118: 'THE WORLD TODAY'.

A newspaper front page summing up Wednesday 18 November 2026 in one
1024x1024 image, drawn with PIL (Liberation Serif / DejaVu Sans).
15 verified stories: a lead (Iran strikes Kuwait and Bahrain), two
featured stories (Kerch Bridge span falls; Trump arrives in Shenzhen),
three panels (Nvidia, OpenAI, EU Ukraine loan), six briefs and an
'Also today' strip, plus the day in figures. Every story was checked
against reporting dated 18 Nov 2026 (Just Security, One Turn, AP,
Reuters, Al Jazeera, BBC, RNZ, Fiji Met Service, Nvidia, OpenAI).

Layout (the legible v1 style from 17 Nov, moderate density): masthead
+ date line, lead story with a drawn illustration, two right-column
stories, a row of three panels, a briefs band, and a figures footer.
Text stays readable at ~300px: no dense grid.

Run:  python3 tools/draw_frontpage.py   -> writes entry.png (1024x1024)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (28, 58, 96)
GREY = (96, 96, 96)
RULE = (18, 18, 18)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, fill=INK):
    """Draw wrapped paragraph; return y just below the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def headline(draw, x, y, text, size, max_w, leading=None):
    """Serif-bold headline, wrapped; returns y below it."""
    fnt = font(SERIF, size)
    return para(draw, x, y, text, fnt, max_w, leading or int(size * 1.08))


def kicker(draw, x, y, text, size=17):
    fnt = font(SANS_B, size)
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + size + 8


def rule(draw, x0, y, x1, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- gulf scene
def draw_gulf(draw, x0, y0, x1, y1):
    """Night over the Gulf: an air base under a drone attack."""
    w, h = x1 - x0, y1 - y0
    horizon = y0 + int(h * 0.66)
    # night sky gradient: deep blue -> ember orange at the horizon
    for i in range(horizon - y0):
        t = i / max(1, horizon - y0)
        r = int(16 + (214 - 16) * t)
        g = int(24 + (120 - 24) * t)
        b = int(52 + (70 - 52) * t)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))
    # stars
    for sx, sy in [(0.08, 0.12), (0.22, 0.06), (0.38, 0.16), (0.55, 0.08),
                   (0.70, 0.18), (0.86, 0.06), (0.94, 0.22), (0.47, 0.04)]:
        draw.ellipse([x0 + sx * w - 2, y0 + sy * (horizon - y0) - 2,
                      x0 + sx * w + 2, y0 + sy * (horizon - y0) + 2],
                     fill=(235, 235, 220))
    # moon
    draw.ellipse([x0 + int(w * 0.82), y0 + 10, x0 + int(w * 0.82) + 34,
                  y0 + 44], fill=(240, 235, 205))
    # sea
    draw.rectangle([x0, horizon, x1, y1], fill=(30, 52, 78))
    for k in range(3):
        wy = horizon + 10 + k * 12
        draw.arc([x0 + 20 + k * 40, wy, x0 + 110 + k * 40, wy + 10],
                 200, 340, fill=(110, 140, 175), width=2)
    # air base silhouette: hangars, tower, radar dome
    base_y = horizon
    draw.rectangle([x0 + 30, base_y - 26, x0 + 130, base_y], fill=(20, 20, 20))
    draw.rectangle([x0 + 150, base_y - 38, x0 + 200, base_y], fill=(20, 20, 20))
    draw.rectangle([x0 + 215, base_y - 58, x0 + 231, base_y], fill=(20, 20, 20))
    draw.ellipse([x0 + 245, base_y - 46, x0 + 285, base_y - 6], fill=(20, 20, 20))
    draw.rectangle([x0 + 262, base_y - 6, x0 + 268, base_y], fill=(20, 20, 20))
    # runway lights
    for i in range(9):
        lx = x0 + 40 + i * 60
        draw.ellipse([lx - 3, base_y + 8, lx + 3, base_y + 14],
                     fill=(240, 200, 60))
    # drones with red trails crossing the sky
    for dx, dy, ln in [(0.30, 0.22, 90), (0.55, 0.34, 70), (0.72, 0.16, 100)]:
        px, py = x0 + dx * w, y0 + dy * (horizon - y0)
        draw.line([(px - ln, py + 12), (px, py)], fill=(240, 90, 60), width=3)
        draw.polygon([(px - 14, py), (px + 14, py), (px, py + 8)],
                     fill=(24, 24, 24))
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(240, 90, 60))
    # explosion glow over the base
    ex, ey = x0 + int(w * 0.42), base_y - 30
    for r, c in [(34, (240, 120, 40)), (22, (250, 170, 60)), (12, (255, 220, 120))]:
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=c)
    # interceptor streaks rising from the base
    for sx in (x0 + 320, x0 + 420):
        draw.line([(sx, base_y - 10), (sx + 26, base_y - 66)],
                  fill=(255, 220, 120), width=3)
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


# ---------------------------------------------------------------- bridge scene
def draw_bridge(draw, x0, y0, x1, y1):
    """Stylised dusk scene: the Kerch Bridge, one span collapsed."""
    w, h = x1 - x0, y1 - y0
    horizon = y0 + int(h * 0.62)
    for i in range(horizon - y0):
        t = i / max(1, horizon - y0)
        r = int(52 + (232 - 52) * t)
        g = int(72 + (164 - 72) * t)
        b = int(108 + (110 - 108) * t)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))
    draw.rectangle([x0, horizon, x1, y1], fill=(38, 62, 88))
    draw.ellipse([x0 + 20, horizon - 26, x0 + 52, horizon + 6],
                 fill=(240, 170, 90))
    deck_y = y0 + int(h * 0.52)
    draw.rectangle([x0, deck_y, x0 + int(w * 0.52), deck_y + 8], fill=(24, 24, 24))
    draw.rectangle([x0 + int(w * 0.86), deck_y, x1, deck_y + 8], fill=(24, 24, 24))
    cx = x0 + int(w * 0.52)
    draw.polygon([(cx, deck_y + 2), (cx + 90, deck_y + 44),
                  (cx + 90, deck_y + 52), (cx, deck_y + 10)], fill=(40, 40, 40))
    sx, sy = cx + 72, horizon + 4
    for dx, dy, r in [(-10, 0, 8), (0, -6, 10), (10, 0, 8)]:
        draw.ellipse([sx + dx - r, sy + dy - r, sx + dx + r, sy + dy + r],
                     fill=(210, 225, 240))
    for px in (x0 + int(w * 0.18), x0 + int(w * 0.88)):
        draw.rectangle([px - 4, deck_y - 52, px + 4, deck_y], fill=(24, 24, 24))
        draw.line([(px, deck_y - 52), (px - 46, deck_y)], fill=(24, 24, 24), width=2)
        draw.line([(px, deck_y - 52), (px + 46, deck_y)], fill=(24, 24, 24), width=2)
    draw.ellipse([cx - 5, deck_y - 10, cx + 15, deck_y + 10], fill=(240, 120, 40))
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


def draw_route(draw, x0, y0, x1, y1):
    """Manila -> Shenzhen route strip for the Asia story."""
    draw.rectangle([x0, y0, x1, y1], fill=(226, 236, 244))
    mid = (y0 + y1) // 2 - 6
    draw.line([(x0 + 24, mid), (x1 - 24, mid)], fill=BLUE, width=2)
    fnt = font(SANS_B, 13)
    stops = [(0.12, "MANILA"), (0.52, "APEC"), (0.88, "SHENZHEN")]
    for frac, label in stops:
        sx = x0 + int((x1 - x0) * frac)
        draw.ellipse([sx - 5, mid - 5, sx + 5, mid + 5], fill=RED, outline=INK, width=1)
        tw = draw.textlength(label, font=fnt)
        draw.text((min(max(sx - tw / 2, x0 + 2), x1 - tw - 2), mid + 10),
                  label, font=fnt, fill=INK)
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


def draw_chart(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(238, 238, 232))
    bars = [(26, 52, (34, 139, 34)), (52, 34, (178, 34, 34)), (40, 62, (34, 139, 34)),
            (62, 30, (178, 34, 34)), (48, 70, (34, 139, 34))]
    bw = (x1 - x0 - 20) // len(bars)
    for i, (up, dn, col) in enumerate(bars):
        bx = x0 + 12 + i * bw
        draw.line([(bx + bw // 2, y0 + 12), (bx + bw // 2, y1 - 12)],
                  fill=INK, width=2)
        top = y0 + 12 + up // 4
        bot = y1 - 14 - dn // 4
        draw.rectangle([bx + 4, top, bx + bw - 4, max(bot, top + 6)],
                       fill=col)
    cx, cy = x1 - 30, y0 + 12
    draw.rectangle([cx - 13, cy - 10, cx + 13, cy + 10], fill=INK)
    draw.rectangle([cx - 6, cy - 4, cx + 6, cy + 4], fill=(240, 120, 40))
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


def draw_chip(draw, x0, y0, x1, y1):
    """AI chip: dark square, pins, glowing core."""
    draw.rectangle([x0, y0, x1, y1], fill=(28, 58, 96))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for k in range(5):
        px = x0 + 12 + k * ((x1 - x0 - 24) // 4)
        draw.line([(px, y0), (px, y0 + 10)], fill=(200, 200, 200), width=3)
        draw.line([(px, y1 - 10), (px, y1)], fill=(200, 200, 200), width=3)
        py = y0 + 12 + k * ((y1 - y0 - 24) // 4)
        draw.line([(x0, py), (x0 + 10, py)], fill=(200, 200, 200), width=3)
        draw.line([(x1 - 10, py), (x1, py)], fill=(200, 200, 200), width=3)
    draw.rectangle([cx - 26, cy - 26, cx + 26, cy + 26], fill=(18, 18, 18),
                   outline=(200, 200, 200), width=2)
    draw.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], fill=(240, 120, 40))
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


def draw_eu(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(28, 58, 120))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 14
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(255, 210, 60))
    draw.rectangle([x0, y0, x1, y1], outline=INK, width=2)


# ---------------------------------------------------------------- briefs
BRIEFS = [
    ("GAZA", "Board of Peace warns truce may collapse",
     "Both sides fall short; aid still blocked."),
    ("ALASKA", "Peltola wins; Democrats take 56-44",
     "Democrat beats Sullivan; majority flips."),
    ("ISRAEL", "Kahana elected speaker in Eisenkot win",
     "Netanyahu camp loses the chair."),
    ("CYCLONE XAVIER", "Category 5 storm hits Cook Islands",
     "Gusts to 315 km/h; shelters activated."),
    ("SIBERIA", "Russian military plane crashes; 19 killed",
     "Crash in Kemerovo; fault suspected."),
    ("BRITAIN", "UK pledges 1,000 missiles to Kyiv",
     "More help as Russia hits Kyiv bridges."),
]


def brief_item(draw, x, y, w, kick, head, deck):
    """One brief: 'KICK — headline' bold on one line, grey deck below."""
    f_k = font(SANS_B, 14)
    f_h = font(SANS_B, 15)
    f_d = font(SANS, 13)
    kw = draw.textlength(kick + " — ", font=f_k)
    draw.text((x, y), kick + " — ", font=f_k, fill=RED)
    draw.text((x + kw, y), head, font=f_h, fill=INK)
    d = deck
    while d and draw.textlength(d + "...", font=f_d) > w:
        d = d.rsplit(" ", 1)[0] if " " in d else d[:-1]
    if d != deck:
        d += "..."
    draw.text((x, y + 19), d, font=f_d, fill=(60, 60, 60))
    return y + 40


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)

    # masthead
    f_mast = font(SERIF, 86)
    d.text(((W - d.textlength("THE WORLD TODAY", font=f_mast)) / 2, 24),
           "THE WORLD TODAY", font=f_mast, fill=INK)
    rule(d, 24, 118, W - 24, 3)
    f_date = font(SANS_B, 21)
    d.text((24, 128), "WEDNESDAY, 18 NOVEMBER 2026", font=f_date, fill=INK)
    right = "15 STORIES  ·  SIX CONTINENTS  ·  ONE DAY"
    d.text((W - 24 - d.textlength(right, font=f_date), 128), right,
           font=f_date, fill=RED)
    rule(d, 24, 158, W - 24, 2)

    # ---- lead story: Iran strikes Kuwait and Bahrain -------------------
    lx, lw = 24, 628
    y = kicker(d, lx, 172, "MIDDLE EAST  ·  WAR IN THE GULF")
    draw_gulf(d, lx, y, lx + lw, y + 168)
    y = y + 168 + 12
    y = headline(d, lx, y, "IRAN STRIKES KUWAIT AND BAHRAIN", 32, lw)
    y += 4
    para(d, lx, y,
         "Drones hit a US air base in Kuwait and targets in Bahrain "
         "after American jets struck a missile site on Iran's Qeshm "
         "Island. Both Gulf states say their defences intercepted "
         "the attacks.",
         font(SANS, 19), lw, 25)

    # ---- right column --------------------------------------------------
    rx, rw = 676, 324
    y = kicker(d, rx, 172, "UKRAINE  ·  WAR IN EUROPE")
    draw_bridge(d, rx, y, rx + rw, y + 62)
    y = y + 62 + 8
    y = headline(d, rx, y, "KERCH BRIDGE FALLS", 23, rw)
    y += 2
    y = para(d, rx, y,
             "Second day of Ukrainian strikes; a road span collapses "
             "into the strait.",
             font(SANS, 16), rw, 20)
    rule(d, rx, y + 8, rx + rw, 1)
    y = kicker(d, rx, y + 20, "ASIA  ·  DIPLOMACY")
    draw_route(d, rx, y, rx + rw, y + 40)
    y = y + 40 + 6
    y = headline(d, rx, y, "TRUMP IN SHENZHEN", 23, rw)
    y += 2
    para(d, rx, y,
         "Xi greets him at the airport; three-way talks with Putin "
         "set for Thursday.",
         font(SANS, 16), rw, 19)

    # ---- second row ----------------------------------------------------
    rule(d, 24, 528, W - 24, 2)
    panels = [
        ("MARKETS  ·  TECH", draw_chart,
         "NVIDIA POSTS RECORD $115.8BN QUARTER",
         "Revenue up 103%; board rules out Jensen Huang's return "
         "as chief executive."),
        ("TECH  ·  AI", draw_chip,
         "OPENAI LAUNCHES GPT-6.2 ASTRA AND SOL",
         "Flagship prices cut 20%; Sol becomes ChatGPT's default "
         "engine."),
        ("EUROPE", draw_eu,
         "EU PROPOSES \u20ac45BN LOAN FOR UKRAINE",
         "\u20ac25bn military, \u20ac20bn budget support for 2027; "
         "Parliament must approve."),
    ]
    pxs = [(24, 324), (360, 324), (696, 304)]
    for (kick, icon, head, deck), (px, pw) in zip(panels, pxs):
        y = kicker(d, px, 540, kick)
        icon(d, px, y, px + pw, y + 72)
        y = y + 72 + 10
        y = headline(d, px, y, head, 25, pw)
        y += 2
        para(d, px, y, deck, font(SANS, 16), pw, 21)

    # ---- briefs --------------------------------------------------------
    rule(d, 24, 758, W - 24, 2)
    y = kicker(d, 24, 770, "THE DAY IN BRIEF")
    col_w = 480
    for idx, (kick, head, deck) in enumerate(BRIEFS):
        col, row = idx % 2, idx // 2
        x = 24 + col * (col_w + 16)
        yy = 800 + row * 40
        brief_item(d, x, yy, col_w, kick, head, deck)
        if col == 0:
            d.line([(x + col_w + 8, yy + 2), (x + col_w + 8, yy + 36)],
                   fill=(200, 195, 180), width=1)

    # ---- also today + figures ------------------------------------------
    rule(d, 24, 926, W - 24, 2)
    f_b = font(SANS, 15)
    line = ("ALSO TODAY:  Sanaa strikes kill 17  ·  Infant dies of cold in a "
            "Gaza camp  ·  Houthis fire drones at a Saudi pipeline.")
    d.text((24, 936), line, font=f_b, fill=INK)
    rule(d, 24, 962, W - 24, 1)
    f_fig = font(SANS_B, 14)
    figs = ("THE DAY IN FIGURES — Nvidia $115.8bn  ·  Ebola 11,000  ·  "
            "Xavier 315 km/h  ·  Senate 56-44  ·  141 drones")
    d.text(((W - d.textlength(figs, font=f_fig)) / 2, 972), figs,
           font=f_fig, fill=BLUE)
    f_foot = font(SERIF_R, 14)
    foot = ("All events of Wednesday 18 November 2026 — as reported by Just "
            "Security, One Turn, AP, Reuters, Al Jazeera, BBC and RNZ.")
    d.text(((W - d.textlength(foot, font=f_foot)) / 2, 994), foot,
           font=f_foot, fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "entry.png")
    out = os.path.normpath(out)
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
