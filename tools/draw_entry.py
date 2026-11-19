#!/usr/bin/env python3
"""Compose the 18 November 2026 front page (development tool, needs Pillow).

    python3 tools/draw_entry.py    ->    entry.png at the repository root

The graded program is main.py; it only copies that PNG into /output.  Everything
on the page is drawn from flat shapes and type: no photographs, no downloads.
The page is composed at twice its final size and reduced once with Lanczos, so
glyph edges and hairlines stay clean at 1024 px.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

SIDE = 1024
MARGIN = 44
SS = 2                      # supersampling factor

NAVY = (20, 33, 61)
PAPER = (253, 251, 247)
SCARLET = (214, 40, 40)
SLATE = (74, 85, 104)
GOLD = (233, 180, 76)
INK = (23, 30, 44)
SAND = (234, 222, 199)
TINT = (241, 236, 226)
HAIRLINE = (223, 215, 201)
SOFT = (120, 132, 152)
WHITE = (255, 255, 255)
SEA = (38, 56, 88)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FAULTS = []


def font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), int(round(size * SS)))


def text_w(text, f):
    return f.getlength(text) / SS


def fit_size(text, size, max_width, bold=True, floor=12):
    """Largest size at or under `size` whose line still fits `max_width`."""
    while size > floor and text_w(text, font(size, bold)) > max_width:
        size -= 1
    return size


def wrap(text, f, max_width):
    out, line = [], ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if text_w(candidate, f) <= max_width:
            line = candidate
        else:
            if line:
                out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def limited(text, f, max_width, max_lines, tag):
    rows = wrap(text, f, max_width)
    if len(rows) > max_lines:
        FAULTS.append("%s: %d lines (max %d): %s" % (tag, len(rows), max_lines, text))
    return rows


class Sheet:
    """Draws in page coordinates on a supersampled canvas."""

    def __init__(self, draw):
        self.d = draw

    def _p(self, *values):
        return [int(round(v * SS)) for v in values]

    def fill_rect(self, x0, y0, x1, y1, color):
        self.d.rectangle(self._p(x0, y0, x1, y1), fill=color)

    def rounded(self, x0, y0, x1, y1, radius, color):
        self.d.rounded_rectangle(self._p(x0, y0, x1, y1), radius=radius * SS, fill=color)

    def disc(self, cx, cy, r, color):
        self.d.ellipse(self._p(cx - r, cy - r, cx + r, cy + r), fill=color)

    def ring(self, cx, cy, r, width, color):
        self.d.ellipse(self._p(cx - r, cy - r, cx + r, cy + r),
                       outline=color, width=max(1, int(width * SS)))

    def polygon(self, points, color):
        flat = []
        for px, py in points:
            flat.extend(self._p(px, py))
        self.d.polygon(flat, fill=color)

    def stroke(self, points, color, width):
        self.d.line(self._p(*[v for point in points for v in point]),
                    fill=color, width=max(1, int(width * SS)), joint="curve")

    def curve(self, x0, y0, x1, y1, start, end, color, width):
        self.d.arc(self._p(x0, y0, x1, y1), start, end,
                   fill=color, width=max(1, int(width * SS)))

    def write(self, x, y, text, f, color):
        self.d.text(self._p(x, y), text, font=f, fill=color)

    def spaced(self, x, y, text, f, color, gap, right=None):
        """Letter-spaced capitals, left-aligned at x or flush to `right`."""
        span = sum(text_w(ch, f) for ch in text) + gap * (len(text) - 1)
        if right is not None:
            x = right - span
        for ch in text:
            self.write(x, y, ch, f, color)
            x += text_w(ch, f) + gap
        return span


# --------------------------------------------------------------------- icons

def badge(sh, x, y, size, color=TINT):
    sh.rounded(x, y, x + size, y + size, size * 0.21, color)


def icon_talks(sh, x, y, size):
    """Two speech bubbles: the leaders in talks."""
    badge(sh, x, y, size)
    sh.rounded(x + size * 0.10, y + size * 0.19, x + size * 0.60, y + size * 0.51,
               size * 0.10, NAVY)
    sh.polygon([(x + size * 0.18, y + size * 0.48), (x + size * 0.33, y + size * 0.48),
                (x + size * 0.17, y + size * 0.63)], NAVY)
    for i in range(3):
        cx = x + size * (0.22 + i * 0.12)
        sh.disc(cx, y + size * 0.35, size * 0.035, PAPER)
    sh.rounded(x + size * 0.44, y + size * 0.43, x + size * 0.90, y + size * 0.72,
               size * 0.10, SCARLET)
    sh.polygon([(x + size * 0.66, y + size * 0.70), (x + size * 0.80, y + size * 0.70),
                (x + size * 0.83, y + size * 0.85)], SCARLET)


def icon_ballot(sh, x, y, size):
    """A ballot going into the box: the Senate result."""
    badge(sh, x, y, size)
    bx0, bx1 = x + size * 0.18, x + size * 0.82
    by0, by1 = y + size * 0.50, y + size * 0.82
    sh.rounded(bx0, by0, bx1, by1, size * 0.06, NAVY)
    sh.fill_rect(bx0 + size * 0.16, by0 - size * 0.02, bx1 - size * 0.16,
                 by0 + size * 0.05, PAPER)
    # the slip, half in the slot
    sh.fill_rect(x + size * 0.30, y + size * 0.16, x + size * 0.70, by0 + size * 0.16, PAPER)
    sh.stroke([(x + size * 0.30, y + size * 0.16), (x + size * 0.70, y + size * 0.16)],
              SOFT, size * 0.02)
    sh.stroke([(x + size * 0.30, y + size * 0.16), (x + size * 0.30, by0 + size * 0.16)],
              SOFT, size * 0.02)
    sh.stroke([(x + size * 0.70, y + size * 0.16), (x + size * 0.70, by0 + size * 0.16)],
              SOFT, size * 0.02)
    sh.stroke([(x + size * 0.38, y + size * 0.28), (x + size * 0.46, y + size * 0.36),
               (x + size * 0.63, y + size * 0.20)], SCARLET, size * 0.055)


def icon_bridge(sh, x, y, size):
    """A bridge deck with a broken span: the Kerch strike."""
    badge(sh, x, y, size)
    deck_y = y + size * 0.44
    sh.fill_rect(x + size * 0.08, deck_y, x + size * 0.44, deck_y + size * 0.06, NAVY)
    sh.fill_rect(x + size * 0.60, deck_y, x + size * 0.92, deck_y + size * 0.06, NAVY)
    for px in (x + size * 0.18, x + size * 0.82):
        sh.fill_rect(px, deck_y, px + size * 0.055, y + size * 0.78, NAVY)
    sh.fill_rect(x + size * 0.46, deck_y + size * 0.03, x + size * 0.58,
                 deck_y + size * 0.14, SCARLET)
    sh.polygon([(x + size * 0.50, deck_y + size * 0.16), (x + size * 0.55, deck_y + size * 0.16),
                (x + size * 0.52, deck_y + size * 0.26)], SCARLET)
    for i in range(2):
        wy = y + size * (0.80 + i * 0.055)
        sh.stroke([(x + size * 0.10, wy), (x + size * 0.28, wy)], (168, 184, 208), size * 0.03)
        sh.stroke([(x + size * 0.72, wy), (x + size * 0.90, wy)], (168, 184, 208), size * 0.03)


def icon_probe(sh, x, y, size):
    """Voyager's dish and booms."""
    badge(sh, x, y, size)
    cx = x + size * 0.50
    sh.disc(cx, y + size * 0.40, size * 0.30, NAVY)
    sh.disc(cx, y + size * 0.40, size * 0.23, (58, 76, 110))
    sh.disc(cx, y + size * 0.40, size * 0.05, SCARLET)
    sh.fill_rect(cx - size * 0.08, y + size * 0.66, cx + size * 0.08,
                 y + size * 0.78, NAVY)
    sh.stroke([(cx - size * 0.07, y + size * 0.74), (cx - size * 0.34, y + size * 0.88)],
              NAVY, size * 0.045)
    sh.stroke([(cx + size * 0.07, y + size * 0.74), (cx + size * 0.32, y + size * 0.86)],
              NAVY, size * 0.045)
    sh.curve(cx - size * 0.06, y + size * 0.06, cx + size * 0.50, y + size * 0.40,
             285, 8, SCARLET, size * 0.035)


def icon_virus(sh, x, y, size):
    """A virus particle: the Ebola outbreak."""
    badge(sh, x, y, size)
    cx, cy, r = x + size * 0.50, y + size * 0.50, size * 0.25
    for k in range(8):
        angle = k * 3.14159265 / 4
        import math
        ex, ey = cx + math.cos(angle) * r, cy + math.sin(angle) * r
        sh.stroke([(ex, ey),
                   (cx + math.cos(angle) * r * 1.42, cy + math.sin(angle) * r * 1.42)],
                  SCARLET, size * 0.055)
    sh.disc(cx, cy, r, SCARLET)
    for dx, dy, rr in ((-0.10, -0.06, 0.07), (0.09, 0.05, 0.055), (-0.02, 0.13, 0.04)):
        sh.disc(cx + size * dx, cy + size * dy, size * rr, PAPER)


# ---------------------------------------------------------------- lead art

def gulf_map(sh, x0, y0, x1, y1):
    """The Gulf between Iran and Arabia, with strikes crossing the water."""
    w, h = x1 - x0, y1 - y0
    sh.rounded(x0, y0, x1, y1, 10, SEA)
    # Iran: the far shore, upper right
    sh.polygon([(x0 + w * 0.34, y0 + h * 0.06), (x1 + 4, y0 - 4), (x1 + 4, y0 + h * 0.42),
                (x0 + w * 0.70, y0 + h * 0.40), (x0 + w * 0.52, y0 + h * 0.26)],
               SAND)
    # Arabia: the near shore, lower left
    sh.polygon([(x0 - 4, y0 + h * 0.34), (x0 + w * 0.30, y0 + h * 0.42),
                (x0 + w * 0.55, y0 + h * 0.74), (x0 + w * 0.50, y1 + 4), (x0 - 4, y1 + 4)],
               SAND)
    # the two firing arcs
    sh.curve(x0 + w * 0.44, y0 + h * 0.12, x0 + w * 0.94, y0 + h * 0.82,
             150, 250, SCARLET, w * 0.016)
    sh.curve(x0 + w * 0.16, y0 + h * 0.24, x0 + w * 0.70, y0 + h * 0.92,
             10, 95, GOLD, w * 0.014)
    # impact bursts, one off each shore
    for bx, by, s in ((0.72, 0.26, 1.0), (0.34, 0.62, 0.8)):
        cx, cy, r = x0 + w * bx, y0 + h * by, w * 0.045 * s
        for k in range(6):
            import math
            a = k * 3.14159 / 3
            sh.stroke([(cx, cy), (cx + math.cos(a) * r * 2.05, cy + math.sin(a) * r * 2.05)],
                      SCARLET, w * 0.012)
        sh.disc(cx, cy, r, SCARLET)
        sh.disc(cx, cy, r * 0.45, PAPER)
    # two base dots on the Arabian shore
    for dx, dy in ((0.16, 0.52), (0.24, 0.66)):
        sh.disc(x0 + w * dx, y0 + h * dy, w * 0.012, WHITE)
        sh.ring(x0 + w * dx, y0 + h * dy, w * 0.026, w * 0.006, WHITE)


# --------------------------------------------------------------- text blocks

def block_icon_top(sh, x, y, width, headline, summary, icon, h_size, s_size, i_size):
    """Icon, then headline, then summary, all flush left in one column."""
    icon(sh, x, y, i_size)
    ty = y + i_size + 12
    head = font(h_size)
    body = font(s_size, bold=False)
    for row in limited(headline, head, width, 3, "headline: " + headline):
        sh.write(x, ty, row, head, INK)
        ty += h_size * 1.17
    ty += 6
    for row in limited(summary, body, width, 3, "summary: " + headline):
        sh.write(x, ty, row, body, SLATE)
        ty += s_size * 1.34
    return ty - y


def build(path):
    canvas = Image.new("RGB", (SIDE * SS, SIDE * SS), PAPER)
    sh = Sheet(ImageDraw.Draw(canvas))

    # ---------------------------------------------------------- masthead
    sh.fill_rect(0, 0, SIDE, 198, NAVY)
    sh.spaced(MARGIN, 25, "THE WORLD TODAY", font(25), WHITE, 2.6)
    sh.spaced(0, 31, "WEDNESDAY", font(17), GOLD, 2.4, right=SIDE - MARGIN)
    date = "18 NOVEMBER 2026"
    d_size = fit_size(date, 82, 928)
    sh.spaced(MARGIN - 2, 50, date, font(d_size), WHITE, -0.8)
    sh.fill_rect(MARGIN, 164, MARGIN + 52, 170, SCARLET)
    sh.spaced(MARGIN + 68, 156, "THE DAY IN SIX STORIES", font(15), (170, 182, 202), 1.8)

    # ---------------------------------------------------------- lead story
    sh.spaced(MARGIN, 214, "LEAD STORY", font(13), SCARLET, 2.2)
    head = font(38)
    y = 238
    lead_head = "US AND IRAN TRADE STRIKES ACROSS THE GULF"
    for row in limited(lead_head, head, 540, 3, "lead headline"):
        sh.write(MARGIN, y, row, head, INK)
        y += 44
    y += 10
    body = font(19, bold=False)
    lead_body = ("Iran hit US bases in Kuwait and Bahrain after US jets struck a "
                 "missile site on Iran's Qeshm Island.")
    for row in limited(lead_body, body, 540, 3, "lead summary"):
        sh.write(MARGIN, y, row, body, SLATE)
        y += 26
    art_bottom = max(452, y + 6)
    gulf_map(sh, 612, 206, 980, art_bottom)
    sh.fill_rect(MARGIN, art_bottom + 26, SIDE - MARGIN, art_bottom + 28, HAIRLINE)

    # ---------------------------------------------------------- middle pair
    top = art_bottom + 46
    col = 450
    block_icon_top(sh, MARGIN, top, col,
                   "XI AND PUTIN MEET AT APEC IN SHENZHEN",
                   "The two met at the summit, ahead of talks with Trump on Thursday.",
                   icon_talks, 25, 17.5, 52)
    block_icon_top(sh, MARGIN + 486, top, col,
                   "DEMOCRATS WIN ALASKA, 56-44 SENATE",
                   "Mary Peltola beat Dan Sullivan; the widest Senate majority since 2009.",
                   icon_ballot, 25, 17.5, 52)

    rule_two = top + 232
    sh.fill_rect(MARGIN, rule_two, SIDE - MARGIN, rule_two + 2, HAIRLINE)

    # ---------------------------------------------------------- three briefs
    top = rule_two + 20
    cw, gap = 293, 28
    briefs = (
        ("UKRAINE HITS KERCH BRIDGE AGAIN",
         "Part of the road span collapsed; drones over Dnipro injured six.",
         icon_bridge),
        ("VOYAGER 1 IS ONE LIGHT-DAY OUT",
         "NASA's probe is 16 billion miles from Earth, 50 years after launch.",
         icon_probe),
        ("CONGO EBOLA CASES PASS 11,000",
         "The second-largest Ebola outbreak on record, health agencies say.",
         icon_virus),
    )
    for i, (headline, summary, icon) in enumerate(briefs):
        used = block_icon_top(sh, MARGIN + i * (cw + gap), top, cw,
                              headline, summary, icon, 21, 15.5, 44)
        if used > 196:
            FAULTS.append("brief %d runs %.0f px past 196" % (i, used))

    # ---------------------------------------------------------- footer
    sh.fill_rect(MARGIN, 962, SIDE - MARGIN, 964, HAIRLINE)
    foot = "WEDNESDAY 18 NOVEMBER 2026 \u00b7 WORLD NEWS"
    ff = font(16)
    span = sum(text_w(c, ff) for c in foot) + 1.4 * (len(foot) - 1)
    sh.spaced((SIDE - span) / 2, 976, foot, ff, SLATE, 1.4)

    canvas.resize((SIDE, SIDE), Image.Resampling.LANCZOS).save(path, "PNG", optimize=True)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target = os.path.join(root, "entry.png")
    build(target)
    print("wrote %s (%d bytes)" % (target, os.path.getsize(target)))
    for fault in FAULTS:
        print("FAULT:", fault)
    sys.exit(1 if FAULTS else 0)
