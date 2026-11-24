"""The Impact Story — vector logo builder (outlined text, no font dependency in output)."""
import math
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

GOLD = "#E8B04B"
TEAL = "#005B50"      # "the" / "story"
TEAL_ICON = "#086654"  # icon arcs
WHITE = "#FFFFFF"

import os
FONTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/"
_fonts = {}


def font(name):
    if name not in _fonts:
        _fonts[name] = TTFont(FONTDIR + f"Poppins-{name}.ttf")
    return _fonts[name]


def text_path(txt, weight, size, x, y, fill, tracking=0.0):
    """Return (svg, advance_width) for txt with baseline at y, left at x."""
    f = font(weight)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    hmtx = f["hmtx"]
    s = size / upm
    out, pen_x = [], 0.0
    for ch in txt:
        g = cmap.get(ord(ch)) or cmap[32]
        pen = SVGPathPen(gs)
        gs[g].draw(pen)
        d = pen.getCommands()
        if d:
            out.append(f'<path transform="translate({x + pen_x * s:.2f},{y:.2f}) scale({s:.5f},{-s:.5f})" d="{d}"/>')
        pen_x += hmtx[g][0] + tracking * upm
    pen_x -= tracking * upm
    return f'<g fill="{fill}">' + "".join(out) + "</g>", pen_x * s


def text_width(txt, weight, size, tracking=0.0):
    return text_path(txt, weight, size, 0, 0, "#000", tracking)[1]


def ink_bounds(txt, weight, size):
    """Ink bbox (x0, y0_up, x1, y1_up) in px relative to origin/baseline (y up)."""
    f = font(weight)
    upm = f["head"].unitsPerEm
    cmap, gs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    s = size / upm
    xmin = ymin = 1e9
    xmax = ymax = -1e9
    px = 0
    for ch in txt:
        g = cmap.get(ord(ch)) or cmap[32]
        bp = BoundsPen(gs)
        gs[g].draw(bp)
        if bp.bounds:
            a, b, c, d = bp.bounds
            xmin, ymin = min(xmin, px + a), min(ymin, b)
            xmax, ymax = max(xmax, px + c), max(ymax, d)
        px += hmtx[g][0]
    return xmin * s, ymin * s, xmax * s, ymax * s


def brush_arc(cx, cy, rx, ry, t_start, t_end, w_start, w_mid, w_end, fill, n=160):
    """Tapered brush-style arc. Angles in degrees, y-down (90 = bottom)."""
    outer, inner = [], []
    for i in range(n + 1):
        u = i / n
        t = math.radians(t_start + (t_end - t_start) * u)
        base = w_start + (w_end - w_start) * u
        w = base + (w_mid - base) * math.sin(math.pi * u) ** 0.8
        ct, st = math.cos(t), math.sin(t)
        outer.append((cx + (rx + w / 2) * ct, cy + (ry + w / 2) * st))
        inner.append((cx + (rx - w / 2) * ct, cy + (ry - w / 2) * st))
    pts = outer + inner[::-1]
    d = "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"
    caps = []
    for t, w in ((t_start, w_start), (t_end, w_end)):
        tr = math.radians(t)
        caps.append(f'<circle cx="{cx + rx * math.cos(tr):.2f}" cy="{cy + ry * math.sin(tr):.2f}" r="{w / 2:.2f}"/>')
    return f'<g fill="{fill}"><path d="{d}"/>{"".join(caps)}</g>'


# ---------------------------------------------------------------- icon
# Native icon box: x 0..500, y 0..420 (sun on top, two arcs cradling it)
ICON_W, ICON_H = 500, 420


def icon(sun=GOLD, inner=TEAL_ICON, outer=TEAL):
    cx = 250
    parts = [
        brush_arc(cx, 185, 245, 222, -24, 196, 28, 46, 18, outer),
        brush_arc(cx - 3, 180, 158, 140, 10, 194, 24, 34, 11, inner),
        f'<circle cx="{cx - 5}" cy="112" r="100" fill="{sun}"/>',
    ]
    return "".join(parts)


# ---------------------------------------------------------------- wordmark
def stacked_wordmark(the_c=TEAL, impact_c=GOLD, story_c=TEAL):
    """Returns (svg, w, h), mirroring the approved logo's proportions."""
    s_imp = 240
    x0, _, x1, i_top = ink_bounds("impact", "Bold", s_imp)
    W = x1 - x0
    sx0, _, sx1, _ = ink_bounds("story", "Regular", 100)
    s_small = 100 * (0.60 * W) / (sx1 - sx0)
    tx0, _, tx1, _ = ink_bounds("the", "Regular", 100)
    s_the = 100 * (0.27 * W) / (tx1 - tx0)
    t_x0, _, _, t_top = ink_bounds("the", "Regular", s_the)
    base1 = t_top
    base2 = base1 + 0.225 * W
    base3 = base2 + 0.179 * W
    s_x0, s_desc, s_x1, _ = ink_bounds("story", "Regular", s_small)
    parts = [
        text_path("the", "Regular", s_the, W * 0.095 - t_x0, base1, the_c)[0],
        text_path("impact", "Bold", s_imp, -x0, base2, impact_c)[0],
        text_path("story", "Regular", s_small, (W - (s_x1 - s_x0)) / 2 - s_x0, base3, story_c)[0],
    ]
    return "".join(parts), W, base3 - s_desc


def stacked_logo(dark=False):
    """Icon over wordmark. Returns (svg_group, w, h)."""
    if dark:
        ic = icon(GOLD, WHITE, WHITE)
        wm, W, H = stacked_wordmark(WHITE, GOLD, WHITE)
    else:
        ic = icon()
        wm, W, H = stacked_wordmark()
    sc = 0.63 * W / ICON_W
    ih = ICON_H * sc
    gap = -0.02 * W
    g = (f'<g transform="translate({(W - ICON_W * sc) / 2:.1f},0) scale({sc:.4f})">{ic}</g>'
         f'<g transform="translate(0,{ih + gap:.1f})">{wm}</g>')
    return g, W, ih + gap + H


def horizontal_logo(dark=False, one_line=True):
    """Icon left + 'the impact story' on one line. Returns (svg, w, h)."""
    tc = WHITE if dark else TEAL
    ic = icon(GOLD, WHITE, WHITE) if dark else icon()
    size = 170
    a, _ = text_path("the ", "Regular", size, 0, 0, tc)
    w_the = text_width("the ", "Regular", size)
    w_imp = text_width("impact ", "Bold", size)
    _, desc, _, asc = ink_bounds("the impact story", "Regular", size)
    icon_scale = 300 / ICON_H
    ih = ICON_H * icon_scale
    iw = ICON_W * icon_scale
    gap = 50
    # vertically centre the x-height-ish block against the icon
    base = ih * 0.70
    tx = iw + gap
    parts = [f'<g transform="scale({icon_scale:.4f})">{ic}</g>',
             text_path("the", "Regular", size, tx, base, tc)[0],
             text_path("impact", "Bold", size, tx + w_the, base, GOLD)[0],
             text_path("story", "Regular", size, tx + w_the + w_imp, base, tc)[0]]
    total_w = tx + w_the + w_imp + text_width("story", "Regular", size)
    h = max(ih, base - desc)
    return "".join(parts), total_w, h


def svg_doc(w, h, body, bg=None):
    bgr = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="0 0 {w:.2f} {h:.2f}">{bgr}{body}</svg>')


def place(g, gw, gh, box_x, box_y, box_w, box_h):
    """Fit group (gw x gh) centred inside a box."""
    s = min(box_w / gw, box_h / gh)
    x = box_x + (box_w - gw * s) / 2
    y = box_y + (box_h - gh * s) / 2
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.5f})">{g}</g>'
