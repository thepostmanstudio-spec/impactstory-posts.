"""The Impact Story — post renderer.

Every post is 1080x1350 (4:5). Text is turned into outlines with fontTools, so the
output never depends on installed fonts. SVG is rasterised with rsvg-convert.

Inline markup in any text field:  *words*  -> gold highlight.
"""
import math
import os
import re
import subprocess

from brand import (GOLD, TEAL, TEAL_ICON, WHITE, icon, horizontal_logo, ICON_W, ICON_H,
                   text_path, text_width, ink_bounds, svg_doc, place)

W, H = 1080, 1350
M = 80                     # side margin
TW = W - 2 * M             # text width
MINT = "#CFE3DE"           # soft text on teal
SOFT = "#3D6E66"           # body text on white
PALE = "#F3F7F5"           # pale panel on white
HANDLE = "@theimpactstory"


# ------------------------------------------------------------------ text helpers
def tokens(text):
    """'a *b c*. d' -> [[('a',F)], [('b',T)], [('c',T),('.',F)], [('d',F)]]"""
    words, hi = [], False
    for raw in text.split():
        word = []
        for i, part in enumerate(raw.split("*")):
            if i > 0:
                hi = not hi
            if part:
                word.append((part, hi))
        if word:
            words.append(word)
    return words


def word_w(word, weight, size):
    return sum(text_width(t, weight, size) for t, _ in word)


def wrap(text, weight, size, width):
    lines, cur, cur_w = [], [], 0.0
    sp = text_width(" ", weight, size)
    for word in tokens(text):
        ww = word_w(word, weight, size)
        if cur and cur_w + sp + ww > width:
            lines.append(cur)
            cur, cur_w = [], 0.0
        cur_w = cur_w + (sp if cur else 0) + ww
        cur.append(word)
    if cur:
        lines.append(cur)
    return lines


def line_w(line, weight, size):
    sp = text_width(" ", weight, size)
    return sum(word_w(w, weight, size) for w in line) + sp * (len(line) - 1)


def draw_lines(lines, weight, size, x, y, color, hi_color=GOLD, lead=1.15, align="left", width=TW):
    """Draw wrapped lines; y = first baseline. Returns (svg, last_baseline)."""
    out = []
    sp = text_width(" ", weight, size)
    for ln in lines:
        lx = x
        if align == "center":
            lx = x + (width - line_w(ln, weight, size)) / 2
        for word in ln:
            for t, hi in word:
                out.append(text_path(t, weight, size, lx, y, hi_color if hi else color)[0])
                lx += text_width(t, weight, size)
            lx += sp
        y += size * lead
    return "".join(out), y - size * lead


def fit(text, weight, max_size, min_size, width, max_lines, max_h=None, lead=1.15):
    """Largest size (step 2) at which text fits in max_lines (and max_h pixels if given)."""
    size = max_size
    while size > min_size:
        lines = wrap(text, weight, size, width)
        if len(lines) <= max_lines and (max_h is None or len(lines) * size * lead <= max_h):
            break
        size -= 2
    return size, wrap(text, weight, size, width)


def block(text, weight, max_size, min_size, max_lines, x, y, color, hi=GOLD, lead=1.15,
          align="left", width=TW, max_h=None):
    size, lines = fit(text, weight, max_size, min_size, width, max_lines, max_h, lead)
    if len(lines) > max_lines or (max_h and len(lines) * size * lead > max_h * 1.02):
        raise ValueError(f"Text too long even at {min_size}px: {text[:60]}...")
    _, top = ink_top(weight, size)
    svg, last = draw_lines(lines, weight, size, x, y + top, color, hi, lead, align, width)
    return svg, last, size


def ink_top(weight, size):
    """Cap-height-ish distance from top of box to first baseline."""
    _, _, _, t = ink_bounds("Hd", weight, size)
    return 0, t


def pill(text, x, y, fill, color, size=30, pad=34, h=None, center=False):
    tw = text_width(text, "Bold", size, 0.06)
    h = h or size * 2.1
    w = tw + pad * 2
    if center:
        x = x - w / 2
    _, _, _, cap = ink_bounds("H", "Bold", size)
    base = y + h / 2 + cap / 2
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{fill}"/>'
            + text_path(text, "Bold", size, x + pad, base, color, 0.06)[0]), w


def arrow(x, y, color, s=1.0):
    return (f'<path d="M{x} {y} h{46 * s} m{-18 * s} {-18 * s} l{18 * s} {18 * s} l{-18 * s} {18 * s}" '
            f'fill="none" stroke="{color}" stroke-width="{6 * s}" stroke-linecap="round" stroke-linejoin="round"/>')


def footer(dark, page=None, on_gold=False):
    hl = horizontal_logo(dark=dark)
    if on_gold:
        g, gw, gh = hl
        hl = (g.replace(GOLD, "#FFFFFF"), gw, gh)
    col = WHITE if dark else TEAL
    out = place(*hl, M, H - 118, 300, 62)
    hw = text_width(HANDLE, "Medium", 28)
    out += text_path(HANDLE, "Medium", 28, W - M - hw, H - 76, col)[0]
    return out


def deco(dark, x=760, y=820, s=1.0, op=0.10):
    c = WHITE if dark else TEAL
    return f'<g opacity="{op}" transform="translate({x},{y}) scale({s})">{icon(c, c, c)}</g>'


# simple line icons (centre cx,cy, size ~ r)
def line_icon(name, cx, cy, r, color, accent=GOLD):
    st = f'fill="none" stroke="{color}" stroke-width="{r * 0.12:.1f}" stroke-linecap="round" stroke-linejoin="round"'
    k = r / 100
    if name == "star":
        pts = []
        for i in range(10):
            rr = r * (0.95 if i % 2 == 0 else 0.42)
            a = math.radians(-90 + i * 36)
            pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
        return f'<polygon points="{" ".join(pts)}" fill="{accent}" stroke="{accent}" stroke-width="{r * 0.1:.1f}" stroke-linejoin="round"/>'
    if name == "sun":
        rays = "".join(
            f'<line {st} x1="{cx + r * .72 * math.cos(math.radians(a)):.1f}" y1="{cy + r * .72 * math.sin(math.radians(a)):.1f}" '
            f'x2="{cx + r * .98 * math.cos(math.radians(a)):.1f}" y2="{cy + r * .98 * math.sin(math.radians(a)):.1f}"/>'
            for a in range(0, 360, 45))
        return f'<circle cx="{cx}" cy="{cy}" r="{r * .45:.1f}" fill="{accent}"/>' + rays
    if name == "heart":
        d = (f"M{cx} {cy + 85 * k} C{cx - 55 * k} {cy + 40 * k} {cx - 95 * k} {cy + 5 * k} {cx - 95 * k} {cy - 35 * k} "
             f"C{cx - 95 * k} {cy - 70 * k} {cx - 65 * k} {cy - 90 * k} {cx - 40 * k} {cy - 90 * k} "
             f"C{cx - 20 * k} {cy - 90 * k} {cx - 5 * k} {cy - 78 * k} {cx} {cy - 62 * k} "
             f"C{cx + 5 * k} {cy - 78 * k} {cx + 20 * k} {cy - 90 * k} {cx + 40 * k} {cy - 90 * k} "
             f"C{cx + 65 * k} {cy - 90 * k} {cx + 95 * k} {cy - 70 * k} {cx + 95 * k} {cy - 35 * k} "
             f"C{cx + 95 * k} {cy + 5 * k} {cx + 55 * k} {cy + 40 * k} {cx} {cy + 85 * k} Z")
        return f'<path {st} d="{d}"/><circle cx="{cx}" cy="{cy - 15 * k}" r="{14 * k:.1f}" fill="{accent}"/>'
    if name == "book":
        d = (f"M{cx} {cy - 60 * k} C{cx - 30 * k} {cy - 85 * k} {cx - 75 * k} {cy - 90 * k} {cx - 95 * k} {cy - 80 * k} "
             f"L{cx - 95 * k} {cy + 70 * k} C{cx - 75 * k} {cy + 60 * k} {cx - 30 * k} {cy + 65 * k} {cx} {cy + 90 * k} "
             f"C{cx + 30 * k} {cy + 65 * k} {cx + 75 * k} {cy + 60 * k} {cx + 95 * k} {cy + 70 * k} "
             f"L{cx + 95 * k} {cy - 80 * k} C{cx + 75 * k} {cy - 90 * k} {cx + 30 * k} {cy - 85 * k} {cx} {cy - 60 * k} Z "
             f"M{cx} {cy - 60 * k} L{cx} {cy + 90 * k}")
        return f'<path {st} d="{d}"/><path fill="{accent}" d="M{cx + 45 * k} {cy - 88 * k} h{25 * k} v{60 * k} l{-12.5 * k} {-12 * k} l{-12.5 * k} {12 * k} Z"/>'
    if name == "leaf":
        d = (f"M{cx - 80 * k} {cy + 80 * k} C{cx - 90 * k} {cy - 20 * k} {cx - 20 * k} {cy - 90 * k} {cx + 85 * k} {cy - 85 * k} "
             f"C{cx + 90 * k} {cy + 20 * k} {cx + 20 * k} {cy + 90 * k} {cx - 80 * k} {cy + 80 * k} Z")
        return f'<path {st} d="{d}"/><path fill="none" stroke="{accent}" stroke-width="{r * .12:.1f}" stroke-linecap="round" d="M{cx - 80 * k} {cy + 80 * k} L{cx + 30 * k} {cy - 30 * k}"/>'
    if name == "drop":
        d = (f"M{cx} {cy - 90 * k} C{cx + 30 * k} {cy - 40 * k} {cx + 70 * k} {cy} {cx + 70 * k} {cy + 30 * k} "
             f"A{70 * k} {70 * k} 0 0 1 {cx - 70 * k} {cy + 30 * k} C{cx - 70 * k} {cy} {cx - 30 * k} {cy - 40 * k} {cx} {cy - 90 * k} Z")
        return f'<path {st} d="{d}"/><path fill="none" stroke="{accent}" stroke-width="{r * .1:.1f}" stroke-linecap="round" d="M{cx - 35 * k} {cy + 35 * k} A{35 * k} {35 * k} 0 0 0 {cx} {cy + 70 * k}"/>'
    if name == "people":
        out = ""
        for dx, s in ((-55, .8), (55, .8), (0, 1.0)):
            out += (f'<circle {st} cx="{cx + dx * k}" cy="{cy - 35 * k * s}" r="{26 * k * s:.1f}"/>'
                    f'<path {st} d="M{cx + dx * k - 45 * k * s} {cy + 75 * k} C{cx + dx * k - 45 * k * s} {cy + 5 * k} '
                    f'{cx + dx * k + 45 * k * s} {cy + 5 * k} {cx + dx * k + 45 * k * s} {cy + 75 * k}"/>')
        return out + f'<circle cx="{cx}" cy="{cy - 35 * k}" r="{12 * k:.1f}" fill="{accent}"/>'
    if name == "school":
        d = (f"M{cx - 90 * k} {cy + 80 * k} V{cy - 10 * k} L{cx} {cy - 80 * k} L{cx + 90 * k} {cy - 10 * k} V{cy + 80 * k} Z "
             f"M{cx - 25 * k} {cy + 80 * k} V{cy + 25 * k} H{cx + 25 * k} V{cy + 80 * k}")
        return f'<path {st} d="{d}"/><circle cx="{cx}" cy="{cy - 20 * k}" r="{16 * k:.1f}" fill="{accent}"/>'
    if name == "health":
        return (f'<rect {st} x="{cx - 85 * k}" y="{cy - 85 * k}" width="{170 * k}" height="{170 * k}" rx="{40 * k}"/>'
                f'<path stroke="{accent}" stroke-width="{r * .16:.1f}" stroke-linecap="round" d="M{cx} {cy - 45 * k} V{cy + 45 * k} M{cx - 45 * k} {cy} H{cx + 45 * k}"/>')
    return line_icon("sun", cx, cy, r, color, accent)


def centre(parts, y0, last, top, bottom, desc=20):
    """Shift a content block (drawn from y0 to baseline `last`) to the middle of top..bottom."""
    h = (last + desc) - y0
    off = top + ((bottom - top) - h) / 2 - y0
    return f'<g transform="translate(0,{off:.1f})">' + "".join(parts) + "</g>"


# ------------------------------------------------------------------ formats
def cover(p, total):
    """Carousel cover — deep teal."""
    s = [deco(True, 640, 780, 1.05, 0.09)]
    s.append(pill(p.get("tag", "CHANGEMAKER").upper(), M, 96, GOLD, TEAL)[0])
    if p.get("icon"):
        s.append(line_icon(p["icon"], W - M - 70, 132, 62, WHITE))
    hl, last, size = block(p["headline"], "Bold", 100, 64, 5, M, 330, WHITE)
    s.append(hl)
    y = last + 70
    if p.get("sub"):
        sub, last, _ = block(p["sub"], "Regular", 40, 32, 3, M, y, MINT, lead=1.4)
        s.append(sub)
    # swipe cue
    s.append(text_path("Swipe", "Medium", 30, W - M - 175, H - 200, WHITE)[0])
    s.append(arrow(W - M - 70, H - 210, GOLD, 1.0))
    s.append(footer(True))
    return svg_doc(W, H, "".join(s), bg=TEAL)


def slide(sl, i, total):
    """Inner carousel slide — white."""
    s = [deco(False, 700, 860, 0.85, 0.05)]
    c = []
    kick = sl.get("kicker", "").upper()
    s.append(f'<rect x="{M}" y="112" width="56" height="8" rx="4" fill="{GOLD}"/>')
    if kick:
        s.append(text_path(kick, "Bold", 28, M + 76, 126, TEAL, 0.08)[0])
    num = f"{i}/{total}"
    s.append(text_path(num, "Medium", 28, W - M - text_width(num, "Medium", 28), 126, SOFT)[0])
    y = 250
    y0 = y
    if sl.get("stat"):
        st, last, size = block(sl["stat"], "Bold", 190, 96, 1, M, y, GOLD, width=TW)
        c.append(st)
        y = last + 60
        if sl.get("stat_label"):
            lab, last, _ = block(sl["stat_label"], "Medium", 36, 28, 2, M, y, SOFT, lead=1.3)
            c.append(lab)
            y = last + 70
    elif sl.get("icon"):
        c.append(f'<circle cx="{M + 80}" cy="{y + 80}" r="80" fill="{PALE}"/>' + line_icon(sl["icon"], M + 80, y + 80, 52, TEAL))
        y += 230
    tt, last, _ = block(sl["title"], "Bold", 74, 50, 4, M, y, TEAL)
    c.append(tt)
    y = last + 60
    if sl.get("body"):
        bd, last, _ = block(sl["body"], "Regular", 42, 30, 9, M, y, SOFT, lead=1.45, max_h=H - 190 - y)
        c.append(bd)
    s.append(centre(c, y0, last, 190, H - 170))
    s.append(footer(False))
    return svg_doc(W, H, "".join(s), bg=WHITE)


def takeaway(p, total):
    """Last carousel slide — gold."""
    s = [deco(False, 650, 770, 1.0, 0.10)]
    s.append(text_path("WHY IT MATTERS", "Bold", 30, M, 150, TEAL, 0.08)[0])
    s.append(f'<rect x="{M}" y="176" width="70" height="8" rx="4" fill="{TEAL}"/>')
    tk, last, _ = block(p["takeaway"], "Bold", 78, 52, 6, M, 300, TEAL, hi=WHITE, lead=1.18)
    c = [tk, pill("FOLLOW " + HANDLE.upper(), M, last + 110, TEAL, WHITE, 30)[0],
         text_path("Save it. Share it with someone who needs some good news.", "Medium", 30, M, last + 250, TEAL)[0]]
    s.append(centre(c, 300, last + 250, 220, H - 170))
    s.append(footer(False, on_gold=True))
    return svg_doc(W, H, "".join(s), bg=GOLD)


def hero(p):
    """Single good-news / hero card — white, icon circle."""
    s = [deco(False, 690, 860, 0.85, 0.05)]
    s.append(pill(p.get("tag", "GOOD NEWS").upper(), M, 96, GOLD, TEAL)[0])
    s.append(f'<circle cx="{W - M - 90}" cy="190" r="90" fill="{PALE}"/>' +
             line_icon(p.get("icon", "sun"), W - M - 90, 190, 58, TEAL))
    hl, last, _ = block(p["headline"], "Bold", 84, 56, 5, M, 380, TEAL)
    c = [hl]
    y = last + 70
    if p.get("body"):
        bd, last, _ = block(p["body"], "Regular", 40, 30, 9, M, y, SOFT, lead=1.45, max_h=H - 230 - y)
        c.append(bd)
    s.append(centre(c, 380, last, 320, H - 200))
    if p.get("source"):
        src = "Source: " + p["source"]
        s.append(text_path(src, "Medium", 24, M, H - 170, SOFT)[0])
    s.append(footer(False))
    return svg_doc(W, H, "".join(s), bg=WHITE)


def data(p):
    """Data / explainer card — teal, big stat."""
    s = [deco(True, 680, 820, 0.9, 0.08)]
    s.append(pill(p.get("tag", "BY THE NUMBERS").upper(), M, 96, GOLD, TEAL)[0])
    st, last, size = block(p["stat"], "Bold", 200, 100, 1, M, 260, GOLD)
    s.append(st)
    y = last + 50
    if p.get("stat_label"):
        lab, last, _ = block(p["stat_label"], "Medium", 38, 30, 2, M, y, MINT, lead=1.3)
        s.append(lab)
        y = last + 80
    hl, last, _ = block(p["headline"], "Bold", 64, 46, 3, M, y, WHITE)
    s.append(hl)
    y = last + 70
    for pt in p.get("points", [])[:3]:
        s.append(f'<circle cx="{M + 12}" cy="{y + 14}" r="10" fill="{GOLD}"/>')
        bd, last, _ = block(pt, "Regular", 36, 28, 2, M + 50, y, WHITE, lead=1.35, width=TW - 50)
        s.append(bd)
        y = last + 50
    if p.get("source"):
        s.append(text_path("Source: " + p["source"], "Medium", 24, M, H - 170, MINT)[0])
    s.append(footer(True))
    return svg_doc(W, H, "".join(s), bg=TEAL)


# ------------------------------------------------------------------ output
def to_png(svg, path):
    tmp = path[:-4] + ".svg"
    with open(tmp, "w") as f:
        f.write(svg)
    subprocess.run(["rsvg-convert", tmp, "-o", path], check=True)
    os.remove(tmp)


def render_post(p, outdir):
    """Render one post dict -> list of PNG paths."""
    pid = p["id"]
    files = []
    if p["format"] == "carousel":
        slides = p["slides"]
        total = len(slides) + 2
        pages = [cover(p, total)] + [slide(sl, i + 2, total) for i, sl in enumerate(slides)] + [takeaway(p, total)]
        for i, svg in enumerate(pages, 1):
            fp = os.path.join(outdir, f"{pid}_{i}.png")
            to_png(svg, fp)
            files.append(fp)
    else:
        fn = {"hero": hero, "data": data}[p["format"]]
        fp = os.path.join(outdir, f"{pid}.png")
        to_png(fn(p), fp)
        files.append(fp)
    return files


def story_frame(png_path, out_path, label="NEW POST ON OUR FEED"):
    """9:16 Story: the post centred on teal with logo + handle."""
    from PIL import Image, ImageDraw
    bg = Image.new("RGB", (1080, 1920), TEAL)
    im = Image.open(png_path).convert("RGB").resize((920, 1150), Image.LANCZOS)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0], im.size[1]], 36, fill=255)
    bg.paste(im, (80, 385), mask)
    hl = horizontal_logo(dark=True)
    tmp = out_path + ".top.png"
    bottom = pill(label, 540, 0, GOLD, TEAL, 30, center=True)[0] if label else ""
    to_png(svg_doc(1080, 1920, place(*hl, 290, 150, 500, 110) +
                   f'<g transform="translate(0,1640)">{bottom}</g>'), tmp)
    top = Image.open(tmp).convert("RGBA")
    bg.paste(top, (0, 0), top)
    os.remove(tmp)
    bg.save(out_path)
    return out_path
