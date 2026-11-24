"""v3 Reel for @theimpactstory: real footage, voiceover, animated captions & graphics.

Shots and captions are set from the voiceover word timings in v3_plan.json:
{"shots": [[src, ss, start, end], ...],
 "phrases": [[n_words, gold_word_index_or_-1], ...],
 "counter": [start, end],            # animated 10,000,000+ meals counter
 "stamp": [start, end],              # 2016 . Secunderabad Railway Station
 "name": [start, end],               # lower third with the name
 "pin": [start, end],                # Hyderabad pin
 "end_start": t, "total": t}
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = "/home/claude/reel2"
RAW = f"{R}/raw"
SEG = f"{R}/seg3"
REPO = "/home/claude/impactstory-posts._"
FONTS = f"{REPO}/engine/fonts"
W, H, FPS = 1080, 1920, 30
TEAL = (0, 91, 80)
GOLD = (232, 176, 75)
WHITE = (255, 255, 255)
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]
os.makedirs(SEG, exist_ok=True)
PLAN = json.load(open(f"{R}/v3_plan.json"))
END_START, TOTAL = PLAN["end_start"], PLAN["total"]


def run(cmd):
    subprocess.run(cmd, check=True)


def font(w, s):
    return ImageFont.truetype(f"{FONTS}/Poppins-{w}.ttf", s)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# ---------------- picture ----------------
def photo_shot(path, opt, nframes, out):
    """Ken Burns on a still photo. opt: focus0/focus1 [x,y] 0..1, z0/z1 zoom, fit (blurred bg)."""
    from PIL import ImageEnhance
    src = Image.open(f"{R}/{path}").convert("RGB")
    src = ImageEnhance.Sharpness(src).enhance(1.25)
    sw, sh = src.size
    f0, f1 = opt.get("focus0", [0.5, 0.45]), opt.get("focus1", opt.get("focus0", [0.5, 0.45]))
    z0, z1 = opt.get("z0", 1.0), opt.get("z1", 1.1)
    bg = None
    if opt.get("fit"):
        cs = max(W / sw, H / sh)
        bg = src.resize((int(sw * cs) + 1, int(sh * cs) + 1), Image.BILINEAR)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.55)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", *ENC, out], stdin=subprocess.PIPE)
    for k in range(nframes):
        u = k / max(1, nframes - 1)
        e = u * u * (3 - 2 * u)
        z = z0 + (z1 - z0) * e
        fx = f0[0] + (f1[0] - f0[0]) * e
        fy = f0[1] + (f1[1] - f0[1]) * e
        if bg is not None:
            fw = int(W * z)
            fh = int(sh * fw / sw)
            fg = src.resize((fw, fh), Image.LANCZOS)
            frame = bg.copy()
            frame.paste(fg, ((W - fw) // 2, int(H * 0.40 - fh / 2)))
        else:
            cs = max(W / sw, H / sh) * z
            cw, ch = W / cs, H / cs
            x0 = min(max(fx * sw - cw / 2, 0), sw - cw)
            y0 = min(max(fy * sh - ch / 2, 0), sh - ch)
            frame = src.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    proc.wait()


def render_shots():
    files = []
    for i, (src, ss, a, b) in enumerate(PLAN["shots"]):
        dur = b - a
        if src.startswith("photo:"):
            out = f"{SEG}/s{i:02d}.mp4"
            n = round(b * FPS) - round(a * FPS)
            photo_shot(src[6:], ss, n, f"{SEG}/s{i:02d}.tmp.mp4")
            os.replace(f"{SEG}/s{i:02d}.tmp.mp4", out)
            files.append(out)
            continue
        n = round(b * FPS) - round(a * FPS)
        out, tmp = f"{SEG}/s{i:02d}.mp4", f"{SEG}/s{i:02d}.tmp.mp4"
        z = f"1.0+0.07*t/{dur:.3f}" if i % 2 == 0 else f"1.07-0.07*t/{dur:.3f}"
        vf = (f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
              f"scale=w='trunc({W}*({z})/2)*2':h=-2:eval=frame:flags=bicubic,crop={W}:{H},"
              "eq=contrast=1.04:saturation=1.10:gamma=1.04:brightness=0.01,unsharp=5:5:0.4,setsar=1,"
              f"trim=end_frame={n},setpts=PTS-STARTPTS")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{dur + 0.6:.2f}", "-i", f"{R}/{src}.mp4",
             "-vf", vf, "-an", *ENC, tmp])
        os.replace(tmp, out)
        files.append(out)
    # last real frame -> background for animated end card
    run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.05", "-i", files[-1], "-frames:v", "1", f"{R}/v3_lastframe.png"])
    with open(f"{SEG}/list.txt", "w") as f:
        for p in files:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{SEG}/list.txt", "-c", "copy",
         f"{R}/v3_picture_shots.mp4"])


# ---------------- graphics ----------------
LOGO = Image.open(f"{REPO}/assets/logos/theimpactstory_horizontal_white.png").convert("RGBA")


def logo(width):
    return LOGO.resize((width, int(LOGO.height * width / LOGO.width)), Image.LANCZOS)


def static_layer(label="Representative footage"):
    a = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.arange(H)
    bot = np.clip((ys - 1000) / 920, 0, 1) ** 1.5 * 120
    top = np.clip((300 - ys) / 300, 0, 1) ** 1.5 * 95
    a[..., 3] = np.maximum(bot, top)[:, None]
    a[..., 0:3] = (0, 35, 30)
    img = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(img)
    f = font("Bold", 30)
    t = "UNSUNG HERO"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle((64, 128, 64 + tw + 48, 188), radius=30, fill=GOLD)
    d.text((88, 136), t, font=f, fill=TEAL)
    fr = font("Medium", 24)
    rw = d.textlength(label, font=fr)
    d.rounded_rectangle((60, 200, 60 + rw + 24, 236), radius=18, fill=(0, 0, 0, 120))
    d.text((72, 203), label, font=fr, fill=(240, 244, 242))
    lg = logo(250)
    d.rounded_rectangle((W - 250 - 84, 118, W - 44, 132 + lg.height + 14), radius=26, fill=(0, 0, 0, 110))
    img.alpha_composite(lg, (W - 250 - 64, 132))
    return img


def chunks():
    return [([{"text": t} for t in txt.split()], g, st, en) for txt, st, en, g in PLAN["captions"]]


def clean(t):
    return t


CAP = font("Bold", 82)


def caption_img(ch, gold, prog):
    """prog 0..1 entrance animation (pop + rise)."""
    toks = [clean(w["text"]) for w in ch]
    toks = ["22-year-old" if t.lower().startswith("twenty-two") else t for t in toks]
    s = 0.86 + 0.14 * ease_out(prog)
    alpha = ease_out(prog * 1.4)
    f = font("Bold", max(10, int(82 * s)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lines, line = [], []
    for i, t in enumerate(toks):
        test = " ".join(toks[j] for j in line + [i])
        if line and d.textlength(test, font=CAP) > W - 170:
            lines.append(line)
            line = [i]
        else:
            line.append(i)
    lines.append(line)
    lh = int(f.size * 1.18)
    y0 = 1200 - (len(lines) - 1) * lh // 2 + int(24 * (1 - ease_out(prog)))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for li, ln in enumerate(lines):
        text = " ".join(toks[i] for i in ln)
        x = (W - d.textlength(text, font=f)) / 2
        y = y0 + li * lh
        for i in ln:
            col = GOLD if i == gold else WHITE
            sd.text((x + 3, y + 5), toks[i], font=f, fill=(0, 0, 0, 190))
            d.text((x, y), toks[i], font=f, fill=col, stroke_width=2, stroke_fill=(0, 0, 0, 90))
            x += d.textlength(toks[i] + " ", font=f)
    out = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), layer)
    if alpha < 1:
        a = np.array(out)
        a[..., 3] = (a[..., 3] * alpha).astype(np.uint8)
        out = Image.fromarray(a, "RGBA")
    return out


def hook_img(prog):
    """frame-0 hook: big '10 MILLION' + 'free meals' (visible before the voice starts)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = 0.9 + 0.1 * ease_out(prog)
    f1, f2 = font("Bold", int(150 * s)), font("Bold", int(76 * s))
    t1, t2 = "10 MILLION", "free meals"
    y = 640
    bw = int(860 * s)
    d.rounded_rectangle(((W - bw) // 2, y - 30, (W + bw) // 2, y + int(290 * s)), radius=40,
                        fill=(0, 91, 80, int(200 * min(1, prog * 1.5))))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for t, f, c, dy in ((t1, f1, GOLD, 0), (t2, f2, WHITE, int(170 * s))):
        x = (W - d.textlength(t, font=f)) / 2
        sd.text((x + 4, y + dy + 6), t, font=f, fill=(0, 0, 0, 200))
        d.text((x, y + dy), t, font=f, fill=c, stroke_width=2, stroke_fill=(0, 0, 0, 100))
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)), layer)


def counter_img(t, a, b):
    p = (t - a) / (b - a)
    inn = ease_out(min(1, (t - a) / 0.35))
    out = 1 - ease_out(max(0, (t - (b - 0.3)) / 0.3))
    vis = inn * out
    val = int(10_000_000 * ease_out(min(1, p / 0.75)))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cy = 640 - int(40 * (1 - inn))
    d.rounded_rectangle((110, cy - 40, W - 110, cy + 250), radius=36, fill=(0, 91, 80, int(215 * vis)))
    f = font("Bold", 112)
    txt = f"{val:,}" + ("+" if p >= 0.75 else "")
    d.text(((W - d.textlength(txt, font=f)) / 2, cy - 10), txt, font=f, fill=GOLD + (int(255 * vis),))
    f2 = font("Medium", 44)
    t2 = "free meals served"
    d.text(((W - d.textlength(t2, font=f2)) / 2, cy + 150), t2, font=f2, fill=WHITE + (int(255 * vis),))
    return layer


def stamp_img(t, a, b):
    inn = ease_out((t - a) / 0.4)
    out = 1 - ease_out(max(0, (t - (b - 0.3)) / 0.3))
    vis = inn * out
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = 64 - int(700 * (1 - inn))
    y = 420
    d.rounded_rectangle((x - 10, y - 30, x + 640, y + 196), radius=24, fill=(0, 91, 80, int(205 * vis)))
    d.rectangle((x, y, x + 12, y + 170), fill=GOLD + (int(255 * vis),))
    d.text((x + 36, y - 14), "2016", font=font("Bold", 120), fill=WHITE + (int(255 * vis),))
    d.text((x + 40, y + 128), "SECUNDERABAD RAILWAY STATION", font=font("Bold", 33), fill=GOLD + (int(255 * vis),))
    return layer


def name_img(t, a, b):
    inn = ease_out((t - a) / 0.45)
    out = 1 - ease_out(max(0, (t - (b - 0.3)) / 0.3))
    vis = inn * out
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f1, f2 = font("Bold", 58), font("Medium", 32)
    t1, t2 = "Mohd Sujathullah", "Founder, Humanity First Foundation"
    w = max(d.textlength(t1, font=f1), d.textlength(t2, font=f2)) + 80
    x = 64 - int((w + 80) * (1 - inn))
    y = 860
    d.rounded_rectangle((x, y, x + w, y + 150), radius=20, fill=(0, 91, 80, int(225 * vis)))
    d.rectangle((x, y, x + 10, y + 150), fill=GOLD + (int(255 * vis),))
    d.text((x + 40, y + 14), t1, font=f1, fill=WHITE + (int(255 * vis),))
    d.text((x + 40, y + 92), t2, font=f2, fill=GOLD + (int(255 * vis),))
    return layer


def pin_img(t, a, b):
    inn = ease_out((t - a) / 0.4)
    out = 1 - ease_out(max(0, (t - (b - 0.3)) / 0.3))
    vis = inn * out
    bounce = abs(math.sin(min(1, (t - a) / 0.6) * math.pi)) * 26 * (1 - min(1, (t - a) / 0.6))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = 130, 520 - int(bounce)
    al = int(255 * vis)
    d.rounded_rectangle((70, 450, 640, 600), radius=26, fill=(0, 91, 80, int(210 * vis)))
    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=GOLD + (al,))
    d.polygon([(cx - 26, cy + 18), (cx + 26, cy + 18), (cx, cy + 74)], fill=GOLD + (al,))
    d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=TEAL + (al,))
    d.text((cx + 60, cy - 46), "Hyderabad", font=font("Bold", 64), fill=WHITE + (al,))
    d.text((cx + 62, cy + 30), "Outside government hospitals", font=font("Bold", 30), fill=GOLD + (al,))
    return layer


def end_frame(t, bg):
    """animated end card: teal wipe up, logo scale-in, lines fade in."""
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
    for k, (txt, col, fs, y) in enumerate((("Small acts.", WHITE, 66, 900), ("Big change.", GOLD, 66, 985))):
        p = ease_out((e - 0.7 - 0.15 * k) / 0.4)
        if p > 0:
            f = font("Bold", fs)
            d.text(((W - d.textlength(txt, font=f)) / 2, y + int(20 * (1 - p))), txt, font=f, fill=col + (int(255 * p),))
    p = ease_out((e - 1.15) / 0.4)
    if p > 0:
        f = font("Medium", 42)
        txt = "Follow for more good news"
        tw = d.textlength(txt, font=f)
        s = 0.9 + 0.1 * p
        x0, x1 = (W - tw) / 2 - 40 * s, (W + tw) / 2 + 40 * s
        d.rounded_rectangle((x0, 1130, x1, 1216), radius=43, fill=GOLD + (int(255 * p),))
        d.text(((W - tw) / 2, 1146), txt, font=f, fill=TEAL + (int(255 * p),))
    p = ease_out((e - 1.4) / 0.4)
    if p > 0:
        f = font("Light", 28)
        txt = "Photos: Humanity First Foundation · other footage representative"
        d.text(((W - d.textlength(txt, font=f)) / 2, 1560), txt, font=f, fill=(190, 222, 215, int(255 * p)))
    return img


def overlay_stream():
    base_stock = static_layer()
    base_photo = static_layer("Photo: Humanity First Foundation")
    photo_ranges = [(a, b) for src, _, a, b in PLAN["shots"] if src.startswith("photo:")]
    chs = [(c[0], c[1]) for c in chunks()]
    events = [(c[2], c[3], i) for i, c in enumerate(chunks())]
    hook_end = PLAN["hook"][1]
    bg = Image.open(f"{R}/v3_lastframe.png").convert("RGBA")
    n = round(TOTAL * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", f"{R}/v3_overlay.mov"], stdin=subprocess.PIPE)
    cache = {}
    for k in range(n):
        t = k / FPS
        if t >= END_START:
            proc.stdin.write(end_frame(t, bg).tobytes())
            continue
        parts = []
        if t < hook_end:
            parts.append(("hook", min(1, k / 8)))
        else:
            for s, e, ci in events:
                if s <= t < e:
                    parts.append(("cap", ci, round(min(1, (t - s) / 0.2), 2)))
        for key in ("counter", "stamp", "name", "pin"):
            if key in PLAN:
                a, b = PLAN[key]
                if a <= t < b:
                    parts.append((key, round(t, 3)))
        is_photo = any(a <= t < b for a, b in photo_ranges)
        base = base_photo if is_photo else base_stock
        ck = (is_photo,) + tuple(parts)
        if ck in cache:
            proc.stdin.write(cache[ck])
            continue
        img = base.copy()
        for p in parts:
            if p[0] == "hook":
                img = Image.alpha_composite(img, hook_img(p[1]))
            elif p[0] == "cap":
                ch, g = chs[p[1]]
                img = Image.alpha_composite(img, caption_img(ch, g, p[2]))
            elif p[0] == "counter":
                img = Image.alpha_composite(img, counter_img(t, *PLAN["counter"]))
            elif p[0] == "stamp":
                img = Image.alpha_composite(img, stamp_img(t, *PLAN["stamp"]))
            elif p[0] == "name":
                img = Image.alpha_composite(img, name_img(t, *PLAN["name"]))
            elif p[0] == "pin":
                img = Image.alpha_composite(img, pin_img(t, *PLAN["pin"]))
        b = img.tobytes()
        if not any(p[0] in ("counter", "stamp", "name", "pin") for p in parts):
            cache[ck] = b
        proc.stdin.write(b)
    proc.stdin.close()
    proc.wait()


def picture():
    """shots + a black-free tail under the end card (end card is fully drawn in the overlay)."""
    dur = TOTAL - END_START
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{R}/v3_lastframe.png", "-vf",
         f"format=yuv420p,loop=-1:1,trim=duration={dur:.3f},setsar=1", *ENC, f"{SEG}/tail.mp4"])
    with open(f"{SEG}/list2.txt", "w") as f:
        f.write(f"file '{R}/v3_picture_shots.mp4'\nfile '{SEG}/tail.mp4'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{SEG}/list2.txt", "-c", "copy",
         f"{R}/v3_picture.mp4"])


def mix_audio():
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/vo_v3.mp3", "-i", f"{R}/piano_v3.wav", "-filter_complex",
         "[0:a]aresample=44100,adelay=%d|%d,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
         "loudnorm=I=-15:TP=-1.5:LRA=7,apad,asplit=2[vo][vk];"
         "[1:a]volume=0.34[m];[m][vk]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=500[duck];"
         "[duck][vo]amix=inputs=2:normalize=0,atrim=0:%.2f,afade=t=out:st=%.2f:d=1.2[a]"
         % (PLAN.get("vo_delay_ms", 0), PLAN.get("vo_delay_ms", 0), TOTAL, TOTAL - 1.2),
         "-map", "[a]", "-c:a", "aac", "-b:a", "192k", f"{R}/v3_audio.m4a"])


def final():
    out = f"{R}/theimpactstory_reel_sujathullah_v3.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/v3_picture.mp4", "-i", f"{R}/v3_overlay.mov", "-i",
         f"{R}/v3_audio.m4a", "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]",
         "-map", "[v]", "-map", "2:a", *ENC, "-c:a", "copy", "-movflags", "+faststart", "-t", f"{TOTAL:.2f}",
         f"{R}/v3.tmp.mp4"])
    os.replace(f"{R}/v3.tmp.mp4", out)


if __name__ == "__main__":
    steps = sys.argv[1:] or ["shots", "overlay", "picture", "audio", "final"]
    if "shots" in steps:
        render_shots()
    if "overlay" in steps:
        overlay_stream()
    if "picture" in steps:
        picture()
    if "audio" in steps:
        mix_audio()
    if "final" in steps:
        final()
    print("done", steps)
