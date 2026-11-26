"""Animated India map clips for Reels (datameet Admin2 state boundaries).
python3 india_map.py kerala OUT.mp4 SECONDS   -> India, Kerala lights up gold, zoom in, Kottayam pin
python3 india_map.py patna  OUT.mp4 SECONDS   -> Kerala + Bihar gold, arc Kottayam -> Patna, Patna pin
"""
import math
import subprocess
import sys

import numpy as np
import shapefile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = "/home/claude/impactstory-posts._"
SHP = "/home/claude/reel27/map/Admin2"
W, H, FPS = 1080, 1920, 30
TEAL, GOLD, WHITE = (0, 91, 80), (232, 176, 75), (255, 255, 255)
PPD = 110  # pixels per degree in the base map
LON0, LAT1 = 67.5, 37.6
COSL = math.cos(math.radians(22))
PLACES = {"Kottayam": (76.52, 9.59), "Patna": (85.14, 25.59)}


def font(w, s):
    return ImageFont.truetype(f"{REPO}/engine/fonts/Poppins-{w}.ttf", s)


def xy(lon, lat):
    return ((lon - LON0) * PPD * COSL, (LAT1 - lat) * PPD)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def base_map(gold_states):
    r = shapefile.Reader(SHP)
    bw, bh = int(31 * PPD * COSL), int(31.5 * PPD)
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    shapes = []
    for sr in r.iterShapeRecords():
        name = sr.record[0]
        pts = sr.shape.points
        parts = list(sr.shape.parts) + [len(pts)]
        rings = [[xy(*p) for p in pts[parts[i]:parts[i + 1]]] for i in range(len(parts) - 1)]
        shapes.append((name, rings))
    for name, rings in shapes:  # fills
        col = (16, 120, 106, 255)
        for ring in rings:
            if len(ring) > 2:
                d.polygon(ring, fill=col)
    for name, rings in shapes:  # state borders
        for ring in rings:
            if len(ring) > 2:
                d.line(ring + [ring[0]], fill=(120, 200, 185, 200), width=2)
    gold = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gold)
    for name, rings in shapes:
        if name in gold_states:
            for ring in rings:
                if len(ring) > 2:
                    gd.polygon(ring, fill=GOLD + (255,))
                    gd.line(ring + [ring[0]], fill=(255, 236, 190, 255), width=3)
    glow = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    glow.paste(Image.new("RGBA", (bw, bh), (0, 0, 0, 120)), (0, 0), img.split()[3])
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    return Image.alpha_composite(glow, img), gold


def background():
    ys = np.linspace(0, 1, H)[:, None]
    top, bot = np.array([0, 70, 62]), np.array([0, 38, 34])
    a = (top + (bot - top) * ys)[:, None, :].repeat(W, 1).reshape(H, W, 3).astype(np.uint8)
    return Image.fromarray(a, "RGB").convert("RGBA")


def camera(img, cx, cy, scale):
    """crop the base map so (cx,cy) lands at screen centre, at `scale` screen px per base px."""
    sw, sh = W / scale, H / scale
    box = (cx - sw / 2, cy - sh / 2, cx + sw / 2, cy + sh / 2)
    return img.transform((W, H), Image.EXTENT, box, Image.BICUBIC), box


def to_screen(px, py, box):
    return ((px - box[0]) / (box[2] - box[0]) * W, (py - box[1]) / (box[3] - box[1]) * H)


def pin(d, x, y, prog, label, sub):
    if prog <= 0:
        return
    drop = (1 - ease_out(prog / 0.6)) * 120
    bounce = abs(math.sin(min(1, prog / 0.8) * math.pi)) * 18 * (1 - min(1, prog / 0.8))
    py = y - drop - bounce
    al = int(255 * min(1, prog / 0.3))
    r = 26
    d.ellipse((x - r, py - 2.4 * r, x + r, py - 0.4 * r), fill=GOLD + (al,), outline=WHITE + (al,), width=4)
    d.polygon([(x - r * 0.75, py - 1.0 * r), (x + r * 0.75, py - 1.0 * r), (x, py)], fill=GOLD + (al,))
    d.ellipse((x - 9, py - 1.4 * r - 9, x + 9, py - 1.4 * r + 9), fill=TEAL + (al,))
    lp = ease_out((prog - 0.35) / 0.4)
    if lp > 0:
        f1, f2 = font("Bold", 56), font("Medium", 32)
        tw = max(d.textlength(label, font=f1), d.textlength(sub, font=f2))
        bx = x + 44 if x + 44 + tw + 60 < W - 110 else x - 44 - tw - 60
        by = py - 120
        a2 = int(235 * lp)
        d.rounded_rectangle((bx, by, bx + tw + 56, by + 128), radius=22, fill=(0, 91, 80, a2))
        d.rectangle((bx, by, bx + 8, by + 128), fill=GOLD + (int(255 * lp),))
        d.text((bx + 30, by + 8), label, font=f1, fill=WHITE + (int(255 * lp),))
        d.text((bx + 30, by + 78), sub, font=f2, fill=GOLD + (int(255 * lp),))


def render(mode, out, dur):
    golds = ["Kerala"] if mode == "kerala" else ["Kerala", "Bihar"]
    bmap, gold = base_map(golds)
    bg = background()
    full_cx, full_cy = xy(82.5, 22.5)
    full_scale = (W - 60) / bmap.width
    ker = xy(76.3, 10.4)
    kot, pat = xy(*PLACES["Kottayam"]), xy(*PLACES["Patna"])
    n = round(dur * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                             "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        if mode == "kerala":
            gp = ease_out((t - 0.15) / 0.45)             # Kerala lights up
            z = ease((t - 0.55) / max(0.6, dur - 1.0))   # then camera moves in
            cx = full_cx + (ker[0] - full_cx) * z
            cy = full_cy + (ker[1] - full_cy) * z
            scale = full_scale * (1 + 2.3 * z)
        else:
            gp = 1.0
            z = 0.12 * ease(t / dur)
            mid = ((kot[0] + pat[0]) / 2, (kot[1] + pat[1]) / 2)
            cx, cy = full_cx + (mid[0] - full_cx) * 0.5, full_cy + (mid[1] - full_cy) * 0.5
            scale = full_scale * (1.08 + z)
        frame = bg.copy()
        layer = Image.alpha_composite(bmap, Image.blend(Image.new("RGBA", gold.size, (0, 0, 0, 0)), gold, gp)) \
            if gp < 1 else Image.alpha_composite(bmap, gold)
        view, box = camera(layer, cx, cy, scale)
        frame = Image.alpha_composite(frame, view)
        d = ImageDraw.Draw(frame)
        if mode == "kerala":
            # state label
            lp = ease_out((t - 0.4) / 0.4)
            if lp > 0:
                f = font("Bold", 64)
                sx, sy = to_screen(*xy(77.2, 12.6), box)
                tx = "KERALA"
                d.text((sx + 40, sy - 40), tx, font=f, fill=GOLD + (int(255 * lp),), stroke_width=4,
                       stroke_fill=(0, 40, 35, int(220 * lp)))
            px, py = to_screen(*kot, box)
            pin(d, px, py, (t - (dur - 1.0)) / 0.9, "Kottayam", "Kerala")
        else:
            ax, ay = to_screen(*kot, box)
            bx, by = to_screen(*pat, box)
            ap = ease((t - 0.25) / 1.1)
            if ap > 0:
                ctrl = ((ax + bx) / 2 - 260, (ay + by) / 2 - 60)
                pts = []
                for i in range(int(60 * ap) + 1):
                    s = i / 60
                    x = (1 - s) ** 2 * ax + 2 * (1 - s) * s * ctrl[0] + s * s * bx
                    y = (1 - s) ** 2 * ay + 2 * (1 - s) * s * ctrl[1] + s * s * by
                    pts.append((x, y))
                for i in range(0, len(pts) - 1, 2):
                    d.line([pts[i], pts[i + 1]], fill=WHITE + (235,), width=7)
                d.ellipse((ax - 12, ay - 12, ax + 12, ay + 12), fill=GOLD, outline=WHITE, width=3)
            pin(d, bx, by, (t - 1.2) / 0.9, "Patna", "Bihar")
        proc.stdin.write(frame.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], float(sys.argv[3]))
