"""Draw the 18 November 2026 world-news front page as one 1024x1024 PNG.

Six stories of the day on a single editorial page: a navy masthead carrying
the date as the largest type on the page, one lead story with a drawn Gulf
panel, and five further stories below it, each with a small flat icon.
Everything is standard-library Python plus Pillow; no photos, no network and
no randomness, so two runs write the same bytes.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

# Palette: ink navy, paper, one scarlet accent, slate for body copy, muted gold.
NAVY = (20, 33, 61)
PAPER = (253, 251, 247)
SCARLET = (214, 40, 40)
SLATE = (74, 85, 104)
GOLD = (233, 180, 76)
RULE = (222, 218, 209)
SAND = (243, 235, 219)
WATER = (226, 238, 242)
LAND = (206, 196, 176)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_FONT_CACHE = {}


def font(path, size):
    """Return a cached font of the given file and pixel size."""
    key = (path, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


def text_width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_width):
    """Break text into lines that each fit inside max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(draw, trial, fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_block(draw, text, path, max_size, min_size, max_width, max_lines):
    """Pick the largest size whose wrapped text fits the line budget."""
    size = max_size
    while size > min_size:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 2
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_width)[:max_lines]


def draw_lines(draw, lines, fnt, x, y, fill, gap):
    """Draw pre-wrapped lines from the top left and return the next free y."""
    step = fnt.size + gap
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def masthead(draw):
    """Navy band: the paper's name, the weekday, then the date, largest of all."""
    draw.rectangle((0, 0, W, 186), fill=NAVY)

    label = font(BOLD, 21)
    draw.text((56, 26), "THE WORLD TODAY", font=label, fill=PAPER)
    weekday = "WEDNESDAY"
    draw.text((W - 56 - text_width(draw, weekday, label), 26), weekday,
              font=label, fill=GOLD)

    date = font(BOLD, 82)
    text = "18 NOVEMBER 2026"
    while text_width(draw, text, date) > W - 112 and date.size > 40:
        date = font(BOLD, date.size - 2)
    draw.text((56, 60), text, font=date, fill=PAPER)

    draw.rectangle((56, 158, 132, 164), fill=SCARLET)
    draw.text((148, 148), "THE DAY IN SIX STORIES", font=font(BOLD, 19),
              fill=(198, 205, 218))


def star(draw, cx, cy, radius, fill):
    """Eight-point burst marker used for the strike points."""
    points = []
    for i in range(16):
        r = radius if i % 2 == 0 else radius * 0.42
        angle = (math.pi / 8.0) * i
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=fill)


def gulf_panel(draw, box):
    """Flat drawn map of the Gulf: two coastlines, the water, two strike arcs."""
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=10, fill=SAND)
    inner = (left + 12, top + 12, right - 12, bottom - 12)
    draw.rounded_rectangle(inner, radius=6, fill=WATER)

    # Iran to the north-east, the Arabian shore to the south-west.
    draw.polygon([(inner[0], inner[1]), (inner[2] - 30, inner[1]),
                  (inner[2] - 84, inner[1] + 70), (inner[2] - 150, inner[1] + 122),
                  (inner[2], inner[1] + 168)], fill=LAND)
    draw.polygon([(inner[0], inner[3]), (inner[0] + 150, inner[3]),
                  (inner[2] - 70, inner[3] - 90), (inner[2] - 215, inner[1] + 146),
                  (inner[0], inner[1] + 118)], fill=LAND)

    draw.text((inner[0] + 44, inner[1] + 92), "GULF", font=font(BOLD, 15),
              fill=(118, 148, 166))

    mid_y = (inner[1] + inner[3]) // 2
    draw.arc((inner[0] + 40, mid_y - 84, inner[2] - 90, mid_y + 84),
             start=198, end=342, fill=SCARLET, width=3)
    draw.arc((inner[0] + 90, mid_y - 44, inner[2] - 40, mid_y + 122),
             start=20, end=160, fill=NAVY, width=3)

    star(draw, inner[2] - 92, inner[1] + 58, 13, SCARLET)
    star(draw, inner[0] + 112, inner[3] - 58, 13, NAVY)


def lead_story(draw):
    """The day's biggest story, with the drawn Gulf panel beside it."""
    top = 226
    draw.text((56, top), "LEAD STORY", font=font(BOLD, 18), fill=SCARLET)

    head_font, head_lines = fit_block(
        draw, "US AND IRAN TRADE STRIKES ACROSS THE GULF", BOLD, 42, 30, 500, 3)
    y = draw_lines(draw, head_lines, head_font, 56, top + 32, NAVY, 8)

    body_font, body_lines = fit_block(
        draw,
        "US jets struck a missile site on Iran's Qeshm Island. Iran answered "
        "by hitting US bases in Kuwait and Bahrain.",
        REGULAR, 21, 17, 500, 3)
    draw_lines(draw, body_lines, body_font, 56, y + 12, SLATE, 9)

    gulf_panel(draw, (600, top, 968, top + 236))
    draw.line((56, 512, 968, 512), fill=RULE, width=2)


def icon(draw, kind, x, y, size):
    """Small flat icon tiles, one drawing per story."""
    draw.rounded_rectangle((x, y, x + size, y + size), radius=8, fill=(240, 238, 232))
    cx, cy = x + size / 2.0, y + size / 2.0
    s = size / 2.0

    if kind == "summit":
        # Two delegations across a table.
        draw.ellipse((cx - s * 0.78, cy - s * 0.62, cx - s * 0.22, cy - s * 0.06), fill=SCARLET)
        draw.ellipse((cx + s * 0.22, cy - s * 0.62, cx + s * 0.78, cy - s * 0.06), fill=NAVY)
        draw.rectangle((cx - s * 0.74, cy + s * 0.18, cx + s * 0.74, cy + s * 0.44), fill=NAVY)
        draw.rectangle((cx - s * 0.1, cy + s * 0.44, cx + s * 0.1, cy + s * 0.78), fill=NAVY)

    elif kind == "ballot":
        # Ballot box with a marked paper going in.
        draw.rectangle((cx - s * 0.78, cy - s * 0.02, cx + s * 0.78, cy + s * 0.74), fill=NAVY)
        draw.rectangle((cx - s * 0.42, cy + s * 0.1, cx + s * 0.42, cy + s * 0.22), fill=PAPER)
        draw.rectangle((cx - s * 0.36, cy - s * 0.78, cx + s * 0.36, cy + s * 0.02), fill=PAPER)
        draw.line((cx - s * 0.2, cy - s * 0.5, cx - s * 0.04, cy - s * 0.28), fill=SCARLET, width=4)
        draw.line((cx - s * 0.04, cy - s * 0.28, cx + s * 0.24, cy - s * 0.62), fill=SCARLET, width=4)

    elif kind == "bridge":
        # A suspension span with a broken deck.
        draw.line((cx - s * 0.86, cy + s * 0.02, cx + s * 0.86, cy + s * 0.02), fill=NAVY, width=5)
        draw.line((cx - s * 0.44, cy - s * 0.7, cx - s * 0.44, cy + s * 0.6), fill=NAVY, width=5)
        draw.line((cx + s * 0.44, cy - s * 0.7, cx + s * 0.44, cy + s * 0.6), fill=NAVY, width=5)
        draw.arc((cx - s * 0.44, cy - s * 0.86, cx + s * 0.44, cy + s * 0.1),
                 start=180, end=360, fill=NAVY, width=4)
        draw.line((cx - s * 0.16, cy + s * 0.02, cx + s * 0.1, cy + s * 0.62), fill=SCARLET, width=5)

    elif kind == "probe":
        # A deep-space probe: dish, bus, solar wings.
        draw.polygon([(cx - s * 0.1, cy - s * 0.5), (cx + s * 0.78, cy - s * 0.86),
                      (cx + s * 0.78, cy + s * 0.02), (cx - s * 0.1, cy + s * 0.22)], fill=PAPER)
        draw.polygon([(cx - s * 0.1, cy - s * 0.5), (cx + s * 0.78, cy - s * 0.86),
                      (cx + s * 0.78, cy - s * 0.62), (cx - s * 0.1, cy - s * 0.28)], fill=NAVY)
        draw.rectangle((cx - s * 0.62, cy - s * 0.3, cx - s * 0.12, cy + s * 0.34), fill=NAVY)
        draw.rectangle((cx - s * 0.98, cy - s * 0.5, cx - s * 0.68, cy + s * 0.05), fill=SCARLET)
        draw.line((cx - s * 0.4, cy + s * 0.34, cx - s * 0.4, cy + s * 0.74), fill=SLATE, width=3)

    elif kind == "virus":
        for angle in range(0, 360, 45):
            rad = math.pi * angle / 180.0
            draw.line((cx + s * 0.56 * math.cos(rad), cy + s * 0.56 * math.sin(rad),
                       cx + s * 0.86 * math.cos(rad), cy + s * 0.86 * math.sin(rad)),
                      fill=SCARLET, width=3)
        draw.ellipse((cx - s * 0.56, cy - s * 0.56, cx + s * 0.56, cy + s * 0.56), fill=NAVY)


def story_block(draw, story, x, y, width):
    """One story: icon tile at the left, headline and summary to its right."""
    kind, headline, summary = story
    tile = 56
    icon(draw, kind, x, y, tile)

    text_x = x + tile + 16
    text_w = width - tile - 16

    head_font, head_lines = fit_block(draw, headline, BOLD, 25, 19, text_w, 2)
    y_after = draw_lines(draw, head_lines, head_font, text_x, y - 1, NAVY, 3)

    body_font, body_lines = fit_block(draw, summary, REGULAR, 18, 14, text_w, 2)
    draw_lines(draw, body_lines, body_font, text_x, y_after + 5, SLATE, 5)


def grid(draw):
    """Five remaining stories: two rows of two, then the day's last story wide."""
    left = 56
    gutter = 44
    col = (W - 2 * left - gutter) // 2

    rows = [
        [("summit", "XI AND PUTIN MEET AT APEC IN SHENZHEN",
          "China and Russia's leaders meet a day before trilateral talks with Trump."),
         ("ballot", "DEMOCRATS TAKE THE ALASKA SENATE SEAT",
          "Mary Peltola beats Dan Sullivan; Democrats hold a 56-44 majority.")],
        [("bridge", "UKRAINE HITS THE KERCH BRIDGE AGAIN",
          "Part of the road span collapsed; drones over Dnipro injured six."),
         ("probe", "VOYAGER 1 REACHES ONE LIGHT-DAY OUT",
          "NASA's probe is about 16 billion miles away, 50 years after launch.")],
    ]

    y = 540
    for row in rows:
        for i, story in enumerate(row):
            story_block(draw, story, left + i * (col + gutter), y, col)
        draw.line((left, y + 126, W - left, y + 126), fill=RULE, width=2)
        y += 152

    story_block(draw, ("virus", "CONGO EBOLA OUTBREAK PASSES 11,000 CASES",
                       "The second-largest Ebola outbreak on record keeps spreading in eastern Congo."),
                left, y, W - 2 * left)


def footer(draw):
    draw.line((56, 962, W - 56, 962), fill=RULE, width=2)
    fnt = font(BOLD, 18)
    text = "WEDNESDAY 18 NOVEMBER 2026  -  WORLD NEWS"
    draw.text(((W - text_width(draw, text, fnt)) / 2.0, 976), text,
              font=fnt, fill=SLATE)


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    masthead(draw)
    lead_story(draw)
    grid(draw)
    footer(draw)
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "entry.png")
    render(out)
    print("wrote %s (%d bytes)" % (out, os.path.getsize(out)))
