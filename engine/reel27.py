"""27 Nov Reel: Gopal Ratna Best Dairy Farmer. Stock footage + ElevenLabs VO + animated captions/graphics.
usage: python3 reel27.py [shots] [overlay] [audio] [final]
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = "/home/claude/reel27"
RAW = f"{R}/raw"
SEG = f"{R}/seg"
REPO = "/home/claude/impactstory-posts._"
FONTS = f"{REPO}/engine/fonts"
W, H, FPS = 1080, 1920, 30
TEAL, GOLD, WHITE = (0, 91, 80), (232, 176, 75), (255, 255, 255)
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]
os.makedirs(SEG, exist_ok=True)

VO = f"{R}/vo/el_b.mp3"
END_START, TOTAL = 31.45, 35.5

# [clip, source start, reel start, reel end, focus x 0..1, pan dx]
SHOTS = [
    ["pb_294427", 1.0, 0.0, 1.95, 0.30, 0.04],
    ["map_kerala", 0.0, 1.95, 4.0, 0.50, 0.0],
    ["pb_144868", 0.0, 4.0, 7.0, 0.30, 0.06],
    ["pb_294427", 5.0, 7.0, 10.7, 0.35, 0.03],
    ["pb_127177", 2.0, 10.7, 14.3, 0.50, 0.05],
    ["pb_127175", 1.0, 14.3, 18.9, 0.55, -0.05],
    ["pb_134471", 2.0, 18.9, 20.4, 0.24, 0.03],
    ["pb_93317", 18.0, 20.4, 22.6, 0.50, 0.0],
    ["pb_127878", 1.0, 22.6, 23.95, 0.50, 0.05],
    ["map_patna", 0.0, 23.95, 25.9, 0.50, 0.0],
    ["pb_304786", 3.0, 25.9, 29.0, 0.50, -0.08],
    ["pb_243239", 4.0, 29.0, TOTAL, 0.45, 0.05],
]

# phrase text, start, end, gold word (or None). Words get time by character share.
PHRASES = [  # chunks separated by " | "
    ("He chose to raise | India's own | indigenous cattle breeds.", 6.99, 10.35, "indigenous"),
    ("Today, his farm | has nearly 500 | of them.", 10.74, 13.89, "500"),
    ("Out of 1,583 | applicants across India,", 14.33, 18.63, "1,583"),
    ("he came FIRST.", 18.95, 20.11, "FIRST."),
    ("On National Milk Day, | he was honoured | with the National | Gopal Ratna Award | in Patna,", 20.42, 25.49,
     "Gopal"),
    ("with a first prize | of ₹5 lakh.", 25.88, 28.59, "₹5"),
    ("Small farms. | Big dreams.", 29.0, 31.22, "Big"),
]
GOLD_EXTRA = {"Ratna", "Award", "lakh.", "dreams.", "FIRST.", "No."}
HOOK = (0.0, 1.95)
NAME = (3.9, 6.95)
COUNTERS = [  # start, end, value, prefix, label, indian format
    (10.9, 14.1, 500, "~", "indigenous cattle", False),
    (14.4, 18.8, 1583, "", "applicants across India", False),
    (25.95, 28.9, 500000, "₹", "first prize", True),
]
STAMP = (22.65, 23.95)
MILKDAY = (20.45, 22.6)
NO_LABEL = [(1.95, 4.0), (23.95, 25.9)]


def run(cmd):
    subprocess.run(cmd, check=True)


def font(w, s):
    return ImageFont.truetype(f"{FONTS}/Poppins-{w}.ttf", s)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def vis(t, a, b, fin=0.35, fout=0.3):
    return ease_out((t - a) / fin) * (1 - ease_out(max(0, (t - (b - fout)) / fout)))


# ---------------- picture ----------------
def render_shots():
    files = []
    for i, (clip, ss, a, b, fx, dx) in enumerate(SHOTS):
        dur = b - a
        out, tmp = f"{SEG}/s{i:02d}.mp4", f"{SEG}/s{i:02d}.tmp.mp4"
        sh = 2016  # 5% oversize for pan room
        # scaled width depends on aspect; compute x with expression on iw
        x0 = f"(iw-{W})*{fx}"
        xexpr = f"max(0,min(iw-{W},{x0}+(iw*{dx})*t/{dur:.3f}))"
        vf = (f"fps={FPS},scale=-2:{sh}:flags=lanczos,crop={W}:{H}:'{xexpr}':(ih-{H})/2,"
              f"eq=saturation=1.08:contrast=1.03,setsar=1,format=yuv420p")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{dur:.3f}", "-i", f"{RAW}/{clip}.mp4", "-an",
             "-vf", vf, *ENC, "-t", f"{dur:.3f}", tmp])
        os.replace(tmp, out)
        files.append(out)
    with open(f"{SEG}/list.txt", "w") as f:
        f.writelines(f"file '{p}'\n" for p in files)
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{SEG}/list.txt", "-c", "copy",
         f"{R}/picture.mp4"])
    run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", f"{R}/picture.mp4", "-frames:v", "1",
         f"{R}/lastframe.png"])


# ---------------- graphics ----------------
LOGO = Image.open(f"{REPO}/assets/logos/theimpactstory_horizontal_white.png").convert("RGBA")


def logo(width):
    return LOGO.resize((width, int(LOGO.height * width / LOGO.width)), Image.LANCZOS)


def static_layer(label=True):
    a = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.arange(H)
    bot = np.clip((ys - 1000) / 920, 0, 1) ** 1.5 * 125
    top = np.clip((300 - ys) / 300, 0, 1) ** 1.5 * 95
    a[..., 3] = np.maximum(bot, top)[:, None]
    a[..., 0:3] = (0, 35, 30)
    img = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(img)
    f = font("Bold", 30)
    t = "NATIONAL AWARD"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle((64, 128, 64 + tw + 48, 188), radius=30, fill=GOLD)
    d.text((88, 136), t, font=f, fill=TEAL)
    fr = font("Medium", 24)
    if label:
        label = "Representative footage"
        rw = d.textlength(label, font=fr)
        d.rounded_rectangle((60, 200, 60 + rw + 24, 236), radius=18, fill=(0, 0, 0, 120))
        d.text((72, 203), label, font=fr, fill=(240, 244, 242))
    lg = logo(250)
    d.rounded_rectangle((W - 250 - 84, 118, W - 44, 132 + lg.height + 14), radius=26, fill=(0, 0, 0, 110))
    img.alpha_composite(lg, (W - 250 - 64, 132))
    return img


def build_chunks():
    out = []
    for text, a, b, gold in PHRASES:
        groups = [c.split() for c in text.split(" | ")]
        total = sum(len(c) + 1 for c in text.replace(" | ", " ").split())
        t = a
        for g in groups:
            share = sum(len(w) + 1 for w in g) / total * (b - a)
            gi = [i for i, w in enumerate(g) if w == gold or w in GOLD_EXTRA]
            out.append((g, gi, t, t + share))
            t += share
    # hold each chunk until the next one starts (no flicker in short gaps)
    fixed = []
    for i, (g, gi, s, e) in enumerate(out):
        nxt = out[i + 1][2] if i + 1 < len(out) else e
        fixed.append((g, gi, s, nxt if nxt - e < 0.45 else e + 0.15))
    return fixed


def caption_img(toks, gold, prog, big=False):
    base = 96 if big else 80
    s = 0.86 + 0.14 * ease_out(prog)
    alpha = ease_out(prog * 1.4)
    f = font("Bold", max(10, int(base * s)))
    fref = font("Bold", base)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lines, line = [], []
    for i in range(len(toks)):
        test = " ".join(toks[j] for j in line + [i])
        if line and d.textlength(test, font=fref) > W - 170:
            lines.append(line)
            line = [i]
        else:
            line.append(i)
    lines.append(line)
    lh = int(f.size * 1.18)
    y0 = 1230 - (len(lines) - 1) * lh // 2 + int(24 * (1 - ease_out(prog)))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for li, ln in enumerate(lines):
        text = " ".join(toks[i] for i in ln)
        x = (W - d.textlength(text, font=f)) / 2
        y = y0 + li * lh
        for i in ln:
            col = GOLD if i in gold else WHITE
            sd.text((x + 3, y + 5), toks[i], font=f, fill=(0, 0, 0, 190))
            d.text((x, y), toks[i], font=f, fill=col, stroke_width=4, stroke_fill=(0, 30, 25, 170))
            x += d.textlength(toks[i] + " ", font=f)
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), layer)
    if alpha < 1:
        a = np.array(out)
        a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
        out = Image.fromarray(a, "RGBA")
    return out


def shadowed(layer, draws):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    d = ImageDraw.Draw(layer)
    for x, y, t, f, c in draws:
        sd.text((x + 4, y + 6), t, font=f, fill=(0, 0, 0, min(200, c[3] if len(c) > 3 else 200)))
    for x, y, t, f, c in draws:
        d.text((x, y), t, font=f, fill=c, stroke_width=2, stroke_fill=(0, 0, 0, 90))
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)), layer)


def hook_img(t):
    a, b = HOOK
    p = min(1, (t - a) / 0.3)
    v = 1 - ease_out(max(0, (t - (b - 0.3)) / 0.3))
    s = 0.9 + 0.1 * ease_out(p)
    al = int(255 * v)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y = 600
    bw = int(900 * s)
    d.rounded_rectangle(((W - bw) // 2, y - 40, (W + bw) // 2, y + int(420 * s)), radius=40,
                        fill=(0, 91, 80, int(205 * min(1, p * 1.5) * v)))
    f0, f1, f2 = font("Bold", int(64 * s)), font("Bold", int(150 * s)), font("Bold", int(70 * s))
    rows = [("INDIA'S", f0, WHITE, 0), ("No. 1", f1, GOLD, int(70 * s)),
            ("dairy farmer", f2, WHITE, int(240 * s))]
    draws = [((W - d.textlength(tx, font=f)) / 2, y + dy, tx, f, c + (al,)) for tx, f, c, dy in rows]
    # "is from Kerala" appears with the voice
    k = 0
    if k > 0:
        f3 = font("Medium", 48)
        tx = "is from Kerala"
        draws.append(((W - d.textlength(tx, font=f3)) / 2, y + int(345 * s) + int(15 * (1 - k)), tx, f3,
                      GOLD + (int(al * k),)))
    return shadowed(layer, draws)


def name_img(t):
    a, b = NAME
    inn = ease_out((t - a) / 0.45)
    v = vis(t, a, b, 0.45)
    al = int(255 * v)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f1, f2 = font("Bold", 64), font("Medium", 34)
    t1, t2 = "Muralidharan Nair", "Dairy farmer"
    w = max(d.textlength(t1, font=f1), d.textlength(t2, font=f2)) + 90
    x = 64 - int((w + 80) * (1 - inn))
    y = 1150
    d.rounded_rectangle((x, y, x + w, y + 160), radius=20, fill=(0, 91, 80, int(225 * v)))
    d.rectangle((x, y, x + 10, y + 160), fill=GOLD + (al,))
    d.text((x + 42, y + 14), t1, font=f1, fill=WHITE + (al,))
    d.text((x + 42, y + 98), t2, font=f2, fill=GOLD + (al,))
    # pin: Kottayam, Kerala (drops in a beat later)
    pa = a + 0.9
    if t >= pa:
        pv = vis(t, pa, b, 0.4)
        bounce = abs(math.sin(min(1, (t - pa) / 0.6) * math.pi)) * 26 * (1 - min(1, (t - pa) / 0.6))
        pal = int(255 * pv)
        cx, cy = 130, 1400 - int(bounce)
        d.rounded_rectangle((70, 1335, 620, 1475), radius=26, fill=(0, 91, 80, int(210 * pv)))
        d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=GOLD + (pal,))
        d.polygon([(cx - 23, cy + 16), (cx + 23, cy + 16), (cx, cy + 64)], fill=GOLD + (pal,))
        d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=TEAL + (pal,))
        d.text((cx + 56, cy - 42), "Kottayam", font=font("Bold", 58), fill=WHITE + (pal,))
        d.text((cx + 58, cy + 26), "Kerala", font=font("Bold", 30), fill=GOLD + (pal,))
    return layer


def fmt(v, indian):
    if not indian:
        return f"{v:,}"
    s = str(v)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail


def counter_img(t, c):
    a, b, val, pre, label, indian = c
    inn = ease_out((t - a) / 0.35)
    v = vis(t, a, b)
    p = (t - a) / (b - a)
    cur = int(val * ease_out(min(1, p / 0.6)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cy = 600 - int(40 * (1 - inn))
    d.rounded_rectangle((120, cy - 40, W - 120, cy + 250), radius=36, fill=(0, 91, 80, int(215 * v)))
    f = font("Bold", 118)
    txt = pre + fmt(cur, indian)
    d.text(((W - d.textlength(txt, font=f)) / 2, cy - 14), txt, font=f, fill=GOLD + (int(255 * v),))
    f2 = font("Medium", 44)
    d.text(((W - d.textlength(label, font=f2)) / 2, cy + 150), label, font=f2, fill=WHITE + (int(255 * v),))
    return layer


def stamp_img(t):
    a, b = STAMP
    inn = ease_out((t - a) / 0.4)
    v = vis(t, a, b, 0.4)
    al = int(255 * v)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = 64 - int(760 * (1 - inn))
    y = 470
    d.rounded_rectangle((x - 10, y - 30, x + 700, y + 300), radius=24, fill=(0, 91, 80, int(210 * v)))
    d.rectangle((x, y, x + 12, y + 270), fill=GOLD + (al,))
    d.text((x + 36, y - 10), "26 NOV 2026", font=font("Bold", 40), fill=GOLD + (al,))
    d.text((x + 36, y + 44), "National", font=font("Bold", 64), fill=WHITE + (al,))
    d.text((x + 36, y + 118), "Gopal Ratna Award", font=font("Bold", 64), fill=WHITE + (al,))
    d.text((x + 38, y + 206), "BEST DAIRY FARMER · 2026", font=font("Bold", 32), fill=GOLD + (al,))
    return layer


def milkday_img(t):
    a, b = MILKDAY
    inn = ease_out((t - a) / 0.4)
    v = vis(t, a, b, 0.4)
    al = int(255 * v)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = 64 - int(760 * (1 - inn))
    y = 470
    d.rounded_rectangle((x - 10, y - 30, x + 760, y + 300), radius=24, fill=(0, 91, 80, int(215 * v)))
    d.rectangle((x, y, x + 12, y + 270), fill=GOLD + (al,))
    d.text((x + 36, y - 10), "26 NOVEMBER", font=font("Bold", 40), fill=GOLD + (al,))
    d.text((x + 36, y + 44), "National Milk Day", font=font("Bold", 68), fill=WHITE + (al,))
    d.text((x + 38, y + 140), "Birth anniversary of Dr Verghese Kurien,", font=font("Medium", 32), fill=WHITE + (al,))
    d.text((x + 38, y + 186), "Father of India's White Revolution", font=font("Bold", 32), fill=GOLD + (al,))
    return layer


def end_frame(t, bg):
    e = t - END_START
    img = bg.copy()
    wipe = ease_out(e / 0.5)
    top = int(H * (1 - wipe))
    panel = Image.new("RGBA", (W, H), TEAL + (255,))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rectangle((0, top, W, H), fill=255)
    img.paste(panel, (0, 0), mask)
    if top > 0:
        ImageDraw.Draw(img).rectangle((0, top - 10, W, top), fill=GOLD)
    d = ImageDraw.Draw(img)
    lp = ease_out((e - 0.35) / 0.5)
    if lp > 0:
        lw = int(800 * (0.85 + 0.15 * lp))
        lg = logo(lw)
        a = np.array(lg)
        a[..., 3] = (a[..., 3] * lp).astype(np.uint8)
        img.alpha_composite(Image.fromarray(a, "RGBA"), ((W - lw) // 2, 650 - int(30 * (1 - lp))))
    for k, (txt, col, y) in enumerate((("Small farms.", WHITE, 900), ("Big dreams.", GOLD, 985))):
        p = ease_out((e - 0.7 - 0.15 * k) / 0.4)
        if p > 0:
            f = font("Bold", 66)
            d.text(((W - d.textlength(txt, font=f)) / 2, y + int(20 * (1 - p))), txt, font=f,
                   fill=col + (int(255 * p),))
    p = ease_out((e - 1.0) / 0.4)
    if p > 0:
        f = font("Medium", 42)
        txt = "Follow for more good news"
        tw = d.textlength(txt, font=f)
        d.rounded_rectangle(((W - tw) / 2 - 40, 1130, (W + tw) / 2 + 40, 1216), radius=43,
                            fill=GOLD + (int(255 * p),))
        d.text(((W - tw) / 2, 1146), txt, font=f, fill=TEAL + (int(255 * p),))
    p = ease_out((e - 1.3) / 0.4)
    if p > 0:
        f = font("Light", 28)
        txt = "Footage: Pixabay · representative"
        d.text(((W - d.textlength(txt, font=f)) / 2, 1560), txt, font=f, fill=(190, 222, 215, int(255 * p)))
    return img


def overlay_stream():
    base = static_layer()
    base_nolabel = static_layer(label=False)
    chs = build_chunks()
    bg = Image.open(f"{R}/lastframe.png").convert("RGBA")
    n = round(TOTAL * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", f"{R}/overlay.mov"], stdin=subprocess.PIPE)
    cache = {}
    for k in range(n):
        t = k / FPS
        if t >= END_START:
            proc.stdin.write(end_frame(t, bg).tobytes())
            continue
        nolab = any(a <= t < b for a, b in NO_LABEL)
        animated = (MILKDAY[0] <= t < MILKDAY[1]) or (HOOK[0] <= t < HOOK[1]) or (NAME[0] <= t < NAME[1]) or (STAMP[0] <= t < STAMP[1]) or any(
            c[0] <= t < c[1] for c in COUNTERS)
        cap = None
        for ci, (g, gi, s, e) in enumerate(chs):
            if s <= t < e:
                cap = (ci, round(min(1, (t - s) / 0.2), 2))
        ck = (cap, nolab)
        if not animated and ck in cache:
            proc.stdin.write(cache[ck])
            continue
        img = (base_nolabel if nolab else base).copy()
        if MILKDAY[0] <= t < MILKDAY[1]:
            img = Image.alpha_composite(img, milkday_img(t))
        if HOOK[0] <= t < HOOK[1]:
            img = Image.alpha_composite(img, hook_img(t))
        if NAME[0] <= t < NAME[1]:
            img = Image.alpha_composite(img, name_img(t))
        if STAMP[0] <= t < STAMP[1]:
            img = Image.alpha_composite(img, stamp_img(t))
        for c in COUNTERS:
            if c[0] <= t < c[1]:
                img = Image.alpha_composite(img, counter_img(t, c))
        if cap:
            g, gi, s, e = chs[cap[0]]
            big = g[0] in ("Small", "Big")
            img = Image.alpha_composite(img, caption_img(g, gi, cap[1], big))
        b = img.tobytes()
        if not animated:
            cache[ck] = b
        proc.stdin.write(b)
    proc.stdin.close()
    proc.wait()


def mix_audio():
    subprocess.run(["python3", f"{REPO}/engine/piano_bed.py", str(TOTAL + 1)], cwd=R, check=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", VO, "-i", f"{R}/piano.wav", "-filter_complex",
         "[0:a]aresample=44100,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
         "loudnorm=I=-15:TP=-1.5:LRA=7,apad,asplit=2[vo][vk];"
         "[1:a]volume=0.36[m];[m][vk]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=450[duck];"
         f"[duck][vo]amix=inputs=2:normalize=0,afade=t=in:d=0.3,atrim=0:{TOTAL:.2f},"
         f"afade=t=out:st={TOTAL - 1.4:.2f}:d=1.4[a]",
         "-map", "[a]", "-c:a", "aac", "-b:a", "192k", f"{R}/audio.m4a"])


def final():
    out = f"{R}/theimpactstory_reel_gopal_ratna.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/picture.mp4", "-i", f"{R}/overlay.mov", "-i",
         f"{R}/audio.m4a", "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
         "-map", "[v]", "-map", "2:a", *ENC, "-c:a", "copy", "-movflags", "+faststart", "-t", f"{TOTAL:.2f}",
         f"{R}/final.tmp.mp4"])
    os.replace(f"{R}/final.tmp.mp4", out)


if __name__ == "__main__":
    steps = sys.argv[1:] or ["shots", "overlay", "audio", "final"]
    if "shots" in steps:
        render_shots()
    if "overlay" in steps:
        overlay_stream()
    if "audio" in steps:
        mix_audio()
    if "final" in steps:
        final()
