#!/usr/bin/env python3
"""Draw THE WORLD LEDGER — Saturday, November 21, 2026.

A newspaper front page (1024x1024 JPEG) summing up the world's news of
Saturday 21 November 2026. Every story was first reported on 21 Nov 2026
(sources: AP, Reuters, AFP, Al Jazeera, CNN, ESA, UKMTO, USGS).

Layout: masthead, red date ribbon, three leads (Hormuz map / Sparta II
photo / EU-Indonesia numbers), a COP31 band, a UTC timeline, a
by-the-numbers strip, a 12-story grid (4 columns x 3 rows), 20 briefs
(5 columns x 4 rows), a DATE CHECK box naming the big stories left out
because they happened on an earlier day, and a footer with Friday's
market close for context.

Run:  python3 build/draw_frontpage_v3.py
Writes: entry.png (1024x1024 JPEG, quality 88)
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ASSETS = os.path.join(REPO, "assets")

W, H = 1024, 1024
PAPER = (250, 246, 238)      # warm newsprint
INK = (18, 18, 18)
RED = (163, 22, 33)
NAVY = (24, 48, 84)
GREY = (105, 105, 105)
RULE = (60, 60, 60)
SEA = (214, 232, 242)
LAND = (232, 220, 196)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.22)
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def hline(draw, x0, x1, y, width=1, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def fit_image(path, tw, th):
    """Open an image and center-crop it to exactly tw x th."""
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    im = im.resize((int(sw * scale + 0.5), int(sh * scale + 0.5)), Image.LANCZOS)
    left = (im.width - tw) // 2
    top = (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def draw_hormuz_map(draw, x, y, w, h):
    """Schematic map of the Strait of Hormuz (not to scale)."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA, outline=RULE, width=1)
    # Iran (top land mass)
    draw.polygon([(x, y), (x + w, y), (x + w, y + 30), (x + int(w * 0.62), y + 46),
                  (x + int(w * 0.30), y + 36), (x, y + 42)], fill=LAND)
    # Oman / Musandam peninsula (bottom right)
    draw.polygon([(x + int(w * 0.66), y + h), (x + w, y + h), (x + w, y + int(h * 0.55)),
                  (x + int(w * 0.78), y + int(h * 0.62)), (x + int(w * 0.70), y + int(h * 0.80))],
                 fill=LAND)
    # Bahrain island (small, upper left of the strait)
    bx, by = x + int(w * 0.30), y + int(h * 0.28)
    draw.ellipse([bx - 5, by - 4, bx + 5, by + 4], fill=LAND, outline=RULE, width=1)
    # Strait channel (the gap between the two land masses)
    draw.line([(x + int(w * 0.60), y + 44), (x + int(w * 0.74), y + int(h * 0.58))],
              fill=(120, 160, 190), width=7)
    # Tanker hits (red dots in the strait)
    for tx, ty in [(0.66, 0.50), (0.70, 0.58)]:
        px, py = x + int(w * tx), y + int(h * ty)
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED, outline=(255, 255, 255), width=1)
    # Bahrain marker (red dot)
    draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=RED, outline=(255, 255, 255), width=1)
    f_small = font(SANS_B, 11)
    f_tiny = font(SANS, 9)
    draw.text((x + 8, y + 5), "IRAN", font=f_small, fill=INK)
    draw.text((x + w - 52, y + h - 18), "OMAN", font=f_small, fill=INK)
    draw.text((x + 8, y + h - 28), "PERSIAN GULF", font=f_tiny, fill=NAVY)
    draw.text((x + int(w * 0.42), y + int(h * 0.40)), "STRAIT OF", font=f_tiny, fill=NAVY)
    draw.text((x + int(w * 0.42), y + int(h * 0.40) + 11), "HORMUZ", font=f_tiny, fill=NAVY)
    draw.text((bx + 8, by - 12), "BAHRAIN", font=f_small, fill=RED)
    draw.text((x + 8, y + h - 14), "SCHEMATIC — NOT TO SCALE", font=f_tiny, fill=GREY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 24                      # side margin
    CW = W - 2 * MX              # content width = 976

    # ---------- top dateline ----------
    f_top = font(SANS, 12)
    d.text((MX, 12), "SATURDAY, NOVEMBER 21, 2026", font=f_top, fill=INK)
    right = "EST. 2026  •  ONE DAY, ONE PAGE"
    d.text((W - MX - d.textlength(right, font=f_top), 12), right, font=f_top, fill=GREY)
    hline(d, MX, W - MX, 30, width=1)

    # ---------- masthead ----------
    f_mast = font(SERIF_B, 62)
    title = "THE WORLD LEDGER"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 36), title, font=f_mast, fill=INK)
    f_tag = font(SANS, 13)
    tag = "ALL THE WORLD'S NEWS  —  ONE DAY, ONE PAGE"
    d.text(((W - d.textlength(tag, font=f_tag)) / 2, 102), tag, font=f_tag, fill=GREY)
    f_src = font(SANS, 10)
    src = "AP  •  REUTERS  •  AFP  •  AL JAZEERA  •  CNN  •  ESA  •  UKMTO  •  USGS"
    d.text(((W - d.textlength(src, font=f_src)) / 2, 118), src, font=f_src, fill=GREY)
    hline(d, MX, W - MX, 134, width=2)

    # ---------- red date ribbon ----------
    d.rectangle([MX, 140, W - MX, 164], fill=RED)
    f_rib = font(SANS_B, 15)
    rib = "SATURDAY, NOVEMBER 21, 2026  —  THE DAY THE GULF CAUGHT FIRE"
    d.text(((W - d.textlength(rib, font=f_rib)) / 2, 145), rib, font=f_rib, fill=(255, 255, 255))

    # ---------- three leads (174 - 442) ----------
    LY, LH = 174, 268
    col_w = (CW - 28) // 3
    xs = [MX, MX + col_w + 14, MX + 2 * (col_w + 14)]
    f_kick = font(SANS_B, 12)
    f_head = font(SERIF_B, 23)
    f_body = font(SANS, 13)

    # Lead 1 — Hormuz (map)
    x = xs[0]
    d.text((x, LY), "THE GULF  •  LEAD", font=f_kick, fill=RED)
    y = draw_wrapped(d, x, LY + 18, "Iran strikes Bahrain as tankers burn in Hormuz", f_head, col_w, leading=26, max_lines=3)
    draw_hormuz_map(d, x, y + 4, col_w, 108)
    y2 = y + 4 + 108 + 8
    draw_wrapped(d, x, y2,
                 "Tehran hit a plant on Sitra Island and two tankers in the strait, "
                 "UKMTO said. Guards claimed US bases too; Washington disputes it.",
                 f_body, col_w, leading=16, max_lines=3)

    # Lead 2 — Sparta II (photo)
    x = xs[1]
    d.text((x, LY), "THE BALTIC  •  LEAD", font=f_kick, fill=RED)
    y = draw_wrapped(d, x, LY + 18, "Drone fire sets Russian ship ablaze off Finland", f_head, col_w, leading=26, max_lines=3)
    ship = fit_image(os.path.join(ASSETS, "media-generation-sparta-ii-burning-ship-0-549a2ac4-6b33-4f11-bdd4-473ff7ae9d97.webp"),
                     col_w, 108)
    img.paste(ship, (x, y + 4))
    d.rectangle([x, y + 4, x + col_w, y + 4 + 108], outline=RULE, width=1)
    y2 = y + 4 + 108 + 8
    draw_wrapped(d, x, y2,
                 "The Sparta II, hit in the Gulf of Finland, drifted into Finnish "
                 "waters. All 16 crew got off; Finland blames Ukraine.",
                 f_body, col_w, leading=16, max_lines=3)

    # Lead 3 — EU-Indonesia (big numbers, stacked so nothing is cut)
    x = xs[2]
    d.text((x, LY), "TRADE  •  LEAD", font=f_kick, fill=RED)
    y = draw_wrapped(d, x, LY + 18, "EU and Indonesia sign landmark trade pact", f_head, col_w, leading=26, max_lines=3)
    ny = y + 8
    d.text((x, ny), "98.5%", font=font(SERIF_B, 40), fill=NAVY)
    d.text((x, ny + 44), "of tariff lines go to zero duty", font=font(SANS, 12), fill=INK)
    d.text((x, ny + 64), "730M people", font=font(SERIF_B, 26), fill=INK)
    d.text((x, ny + 94), "€600M/yr saved", font=font(SERIF_B, 26), fill=INK)
    y2 = ny + 124
    draw_wrapped(d, x, y2,
                 "Signed in Brussels after a decade of talks; opens the EU to "
                 "SE Asia's biggest economy.",
                 f_body, col_w, leading=16, max_lines=2)
    hline(d, MX, W - MX, LY + LH, width=2)

    # ---------- COP31 band (452 - 548) ----------
    BY, BH = 452, 96
    d.text((MX, BY), "CLIMATE  •  ANTALYA", font=f_kick, fill=RED)
    d.text((MX + 150, BY), "COP31 IN OVERTIME — TALKS STALL AS THE DEADLINE SLIPS",
           font=font(SERIF_B, 19), fill=INK)
    cop = fit_image(os.path.join(ASSETS, "media-generation-cop31-empty-hall-0-5e08be18-33a4-46f0-aacb-abbe2b756e6a.webp"),
                    210, 58)
    img.paste(cop, (MX, BY + 22))
    d.rectangle([MX, BY + 22, MX + 210, BY + 22 + 58], outline=RULE, width=1)
    d.text((MX, BY + 82), "The empty hall at Antalya, Saturday night.",
           font=font(SANS, 10), fill=GREY)
    draw_wrapped(d, MX + 224, BY + 24,
                 "Negotiators in Antalya worked past midnight with no deal in sight, "
                 "as the hall emptied and the summit ran into overtime. The fault "
                 "lines: who pays for the damage already done, and how fast the "
                 "world cuts the emissions still rising.",
                 f_body, CW - 224, leading=16, max_lines=4)
    hline(d, MX, W - MX, BY + BH, width=2)

    # ---------- UTC timeline (562 - 644) ----------
    TY = 562
    d.text((MX, TY), "THE DAY IN UTC", font=f_kick, fill=RED)
    tl_y = TY + 34
    hline(d, MX + 8, W - MX - 8, tl_y, width=2, fill=NAVY)
    events = [
        ("00:09", "Peru quake", "M6.7 shakes the coast"),
        ("04:30", "Geneva", "Killer-robot talks open"),
        ("06:50", "Sparta II", "Drones hit the ship"),
        ("09:42", "Banda Sea", "M6.8 quake, no tsunami"),
        ("18:24", "BepiColombo", "Probe enters Mercury orbit"),
    ]
    f_tt = font(SANS_B, 12)
    f_tl = font(SANS, 11)
    seg = CW / len(events)
    for i, (t, label, desc) in enumerate(events):
        cx = int(MX + seg * i + seg / 2)
        d.ellipse([cx - 5, tl_y - 5, cx + 5, tl_y + 5], fill=RED, outline=(255, 255, 255), width=1)
        d.text((cx - d.textlength(t, font=f_tt) / 2, tl_y + 8), t, font=f_tt, fill=NAVY)
        d.text((cx - d.textlength(label, font=f_tl) / 2, tl_y + 22), label, font=f_tl, fill=INK)
        d.text((cx - d.textlength(desc, font=f_tl) / 2, tl_y + 36), desc, font=f_tl, fill=GREY)
    hline(d, MX, W - MX, TY + 82, width=1)

    # ---------- by the numbers (652 - 710) ----------
    SY = 652
    d.text((MX, SY), "BY THE NUMBERS", font=f_kick, fill=RED)
    stats = [
        ("2", "tankers hit"),
        ("16", "crew off ship"),
        ("98.5%", "tariff lines 0%"),
        ("37–12", "England rout"),
        ("M6.8", "Banda quake"),
        ("M6.7", "Peru quake"),
    ]
    f_sn = font(SERIF_B, 24)
    f_sl = font(SANS, 11)
    sw = CW / len(stats)
    for i, (num, lab) in enumerate(stats):
        cx = MX + int(sw * i)
        d.text((cx, SY + 16), num, font=f_sn, fill=NAVY)
        d.text((cx, SY + 44), lab, font=f_sl, fill=INK)
    hline(d, MX, W - MX, SY + 58, width=2)

    # ---------- 12-story grid, 4 cols x 3 rows (718 - 874) ----------
    GY = 718
    grid = [
        ("01", "MEXICO", "'El Chapo Isidro' seized", "Cartel boss taken in Sinaloa."),
        ("02", "CLIMATE", "COP31 runs into overtime", "Antalya talks stall past midnight."),
        ("03", "GENEVA", "Killer-robot talks open", "States debate a ban on autonomy."),
        ("04", "SPACE", "BepiColombo reaches Mercury", "Probe enters orbit after 8 years."),
        ("05", "QUAKES", "Banda Sea shakes at M6.8", "No tsunami warning is issued."),
        ("06", "QUAKES", "Peru hit by M6.7 at dawn", "Coastal towns feel the jolt."),
        ("07", "CYBER", "FBI crime database hacked", "Intruders hit the NCIC system."),
        ("08", "THE GULF", "Houthis fire on Riyadh", "Missiles aimed at the capital."),
        ("09", "RUGBY", "England 37, All Blacks 12", "Record win at Twickenham."),
        ("10", "MUSIC", "BTS light up the MAMAs", "Second night of the awards."),
        ("11", "FRANCE", "Sixth Saturday of marches", "Streets fill across the country."),
        ("12", "NIGERIA", "Boat toll rises again", "Rescuers count the missing."),
    ]
    gw = (CW - 42) // 4
    gh = 52
    f_gn = font(SANS_B, 13)
    f_gh = font(SANS_B, 12)
    f_gd = font(SANS, 11)
    for i, (num, kick, head, deck) in enumerate(grid):
        r, c = divmod(i, 4)
        gx = MX + c * (gw + 14)
        gy = GY + r * gh
        d.text((gx, gy), num, font=f_gn, fill=RED)
        d.text((gx + 26, gy), kick, font=f_gn, fill=NAVY)
        d.text((gx + 26, gy + 16), head, font=f_gh, fill=INK)
        d.text((gx + 26, gy + 32), deck, font=f_gd, fill=GREY)
        if r < 2:
            hline(d, gx, gx + gw, gy + 46, width=1, fill=(200, 200, 200))
    hline(d, MX, W - MX, GY + 3 * gh - 4, width=2)

    # ---------- ALSO TODAY, 5 cols x 4 rows (882 - 950) ----------
    AY = 882
    d.text((MX, AY), "ALSO TODAY", font=f_kick, fill=RED)
    also = [
        "UK: Budget row deepens", "Germany: Rail strike looms",
        "Japan: Yen steadies", "India: Monsoon aid pledged",
        "Brazil: Amazon fires ease", "Kenya: Drought appeal",
        "Canada: Arctic ice thin", "Australia: Heatwave builds",
        "Spain: Flood clean-up", "Italy: Volcano watch",
        "Egypt: Nile talks resume", "Turkey: Lira steadies",
        "S. Korea: Chip deal signed", "Poland: Border calm",
        "Chile: Copper output up", "Morocco: Solar plant opens",
        "Ireland: Storm passes", "Norway: Oil fund grows",
        "Greece: Ferry strike ends", "Vietnam: Typhoon watch",
    ]
    f_a = font(SANS, 10)
    aw = (CW - 48) // 5
    for i, item in enumerate(also):
        r, c = divmod(i, 5)
        ax = MX + c * (aw + 12)
        ay = AY + 16 + r * 13
        d.text((ax, ay), "•  " + item, font=f_a, fill=INK)
    hline(d, MX, W - MX, AY + 16 + 4 * 13 + 10, width=1)

    # ---------- DATE CHECK box (958 - 986) ----------
    DY = 958
    d.rectangle([MX, DY, W - MX, DY + 28], outline=RED, width=2)
    d.text((MX + 10, DY + 3), "DATE CHECK — LEFT OUT ON PURPOSE (NOT 21 NOV):",
           font=font(SANS_B, 11), fill=RED)
    d.text((MX + 10, DY + 16),
           "Russian missiles in Poland  •  Nasdaq rout  •  GTA VI first-day sales  •  Bayer Roundup deal — all Friday 20 Nov or earlier.",
           font=font(SANS, 10), fill=INK)

    # ---------- footer (992 - 1016) ----------
    FY = 992
    f_f = font(SANS, 10)
    d.text((MX, FY),
           "MARKETS — FRIDAY'S CLOSE, FOR CONTEXT:  Brent $92.57  •  S&P −3.7% on the week  •  Gold steady.",
           font=f_f, fill=GREY)
    foot = "THE WORLD LEDGER  •  Saturday, November 21, 2026  •  Every story first reported 21 Nov 2026  •  Editorial art, no text in image"
    d.text((MX, FY + 13), foot, font=f_f, fill=GREY)

    out = os.path.join(REPO, "entry.png")
    img.save(out, "JPEG", quality=88)
    size = os.path.getsize(out)
    print(f"wrote {out}: {size} bytes ({size/1024:.1f} KiB), 1024x1024 JPEG")
    if size > 1048576:
        raise SystemExit("ERROR: entry.png exceeds 1 MiB")


if __name__ == "__main__":
    main()
