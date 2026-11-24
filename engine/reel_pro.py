"""Pro re-edit: real footage + voiceover + word-synced captions for @theimpactstory."""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = "/home/claude/reel2"
RAW = f"{R}/raw"
SEG = f"{R}/seg"
REPO = "/home/claude/impactstory-posts._"
FONTS = f"{REPO}/engine/fonts"
W, H, FPS = 1080, 1920, 30
TEAL = (0, 91, 80)
GOLD = (232, 176, 75)
os.makedirs(SEG, exist_ok=True)

# (source, start-in-source, scene start, scene end, push direction)
SCENES = [
    ("eatery", 0.3, 0.00, 2.30, 1),
    ("bangalore", 0.5, 2.30, 6.00, -1),
    ("station", 0.0, 6.00, 9.60, 1),
    ("street1643", 1.0, 9.60, 12.30, -1),
    ("street1643", 8.5, 12.30, 15.25, 1),
    ("villagefood", 1.0, 15.25, 18.75, -1),
    ("odisha", 10.0, 18.75, 21.95, 1),
    ("dosa", 0.5, 21.95, 25.00, -1),
    ("eatery", 8.5, 25.00, 29.95, 1),
    ("jalebi", 8.0, 29.95, 33.95, -1),
]
END_START, TOTAL = 33.95, 37.6

ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def run(cmd):
    subprocess.run(cmd, check=True)


def render_scenes():
    files = []
    for i, (src, ss, a, b, d) in enumerate(SCENES):
        dur = b - a
        out = f"{SEG}/s{i:02d}.mp4"
        tmp = f"{SEG}/s{i:02d}.tmp.mp4"
        z = "1.0+0.06*t/%.3f" % dur if d > 0 else "1.06-0.06*t/%.3f" % dur
        vf = (f"fps={FPS},scale=-2:{H}:flags=lanczos,crop={W}:{H},"
              f"scale=w='trunc({W}*({z})/2)*2':h=-2:eval=frame:flags=bicubic,crop={W}:{H},"
              "eq=contrast=1.05:saturation=1.08:gamma=0.98,vignette=angle=PI/5,setsar=1,"
              f"trim=duration={dur:.3f},setpts=PTS-STARTPTS")
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", f"{dur + 0.5:.2f}", "-i", f"{RAW}/{src}.mp4",
             "-vf", vf, "-an", *ENC, tmp])
        os.replace(tmp, out)
        files.append(out)
    # end card: teal + logo, rendered as still with gentle fade-in
    end = end_card()
    out = f"{SEG}/s99.mp4"
    tmp = f"{SEG}/s99.tmp.mp4"
    dur = TOTAL - END_START
    run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", end, "-vf",
         f"format=yuv420p,loop=-1:1,trim=duration={dur:.3f},fade=t=in:st=0:d=0.35,setsar=1", *ENC, tmp])
    os.replace(tmp, out)
    files.append(out)
    with open(f"{SEG}/list.txt", "w") as f:
        for p in files:
            f.write(f"file '{p}'\n")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{SEG}/list.txt", "-c", "copy", f"{R}/picture.mp4"])


def font(w, s):
    return ImageFont.truetype(f"{FONTS}/Poppins-{w}.ttf", s)


def end_card():
    img = Image.new("RGB", (W, H), TEAL)
    d = ImageDraw.Draw(img)
    logo = Image.open(f"{REPO}/assets/logos/theimpactstory_horizontal_white.png").convert("RGBA")
    lw = 780
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.paste(logo, ((W - lw) // 2, 640), logo)
    y = 640 + logo.height + 110
    for t, c in (("Small acts.", (255, 255, 255)), ("Big change.", GOLD)):
        f = font("Bold", 64)
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=c)
        y += 84
    f = font("Medium", 40)
    t = "Follow for more good news"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 36, y + 70, (W + tw) / 2 + 36, y + 150), radius=40, outline=GOLD, width=3)
    d.text(((W - tw) / 2, y + 86), t, font=f, fill=(255, 255, 255))
    f = font("Light", 28)
    t = "Representative footage, not of the people named"
    d.text(((W - d.textlength(t, font=f)) / 2, 1560), t, font=f, fill=(190, 222, 215))
    p = f"{R}/end.png"
    img.save(p)
    return p


# ---------------- captions ----------------
SKIP = {"[warm,", "sincere", "storytelling]", "[softly]"}
GOLD_WORDS = {"million", "student...", "2016,", "hungry.", "feeding", "Humanity", "First", "Foundation",
              "breakfast", "small", "every", "single", "day."}


PHRASES = [4, 3, 3, 4, 2, 4, 2, 2, 2, 4, 3, 4, 4, 3, 4, 4, 3, 2, 4, 3, 2, 3, 4]


def caption_chunks():
    words = [w for w in json.load(open(f"{R}/words.json"))["words"] if w.get("type") == "word" and w["text"] not in SKIP]
    words = [w for w in words if w["start"] < END_START - 0.05]
    chunks, i = [], 0
    for n in PHRASES:
        chunks.append(words[i:i + n])
        i += n
    assert i == len(words), (i, len(words))
    return chunks


def clean(t):
    t = t.replace("...", "").replace("Mohd", "Mohd")
    return t.rstrip(",.") if t not in ("2016,",) else "2016"


CAP_F = font("Bold", 84)
HOOK_F = font("Bold", 118)


def draw_chunk(chunk, active, hook=False):
    """RGBA layer with chunk text centred; active word in gold."""
    f = HOOK_F if hook else CAP_F
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    toks = [clean(w["text"]) for w in chunk]
    # wrap into lines max width
    lines, line = [], []
    for i, t in enumerate(toks):
        test = " ".join(toks[j] for j in line + [i])
        if line and d.textlength(test, font=f) > W - 160:
            lines.append(line)
            line = [i]
        else:
            line.append(i)
    lines.append(line)
    lh = int(f.size * 1.2)
    y0 = (1180 if not hook else 760) - (len(lines) - 1) * lh // 2
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    for li, ln in enumerate(lines):
        text = " ".join(toks[i] for i in ln)
        x = (W - d.textlength(text, font=f)) / 2
        y = y0 + li * lh
        for i in ln:
            t = toks[i] + " "
            col = GOLD if (i == active or chunk[i]["text"] in GOLD_WORDS and hook) else (255, 255, 255)
            sd.text((x + 4, y + 6), toks[i], font=f, fill=(0, 0, 0, 200))
            d.text((x, y), toks[i], font=f, fill=col, stroke_width=3, stroke_fill=(0, 0, 0, 110))
            x += d.textlength(t, font=f)
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    return Image.alpha_composite(shadow, layer)


def static_layer():
    """bottom/top gradients for legibility, tag pill, handle."""
    a = np.zeros((H, W, 4), dtype=np.uint8)
    ys = np.arange(H)
    bot = np.clip((ys - 900) / 900, 0, 1) ** 1.6 * 150
    top = np.clip((260 - ys) / 260, 0, 1) ** 1.5 * 110
    a[..., 3] = np.maximum(bot, top)[:, None]
    a[..., 0:3] = (0, 40, 35)
    img = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(img)
    f = font("Bold", 30)
    t = "UNSUNG HERO"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle((64, 130, 64 + tw + 48, 190), radius=30, fill=GOLD)
    d.text((88, 138), t, font=f, fill=TEAL)
    logo = Image.open(f"{REPO}/assets/logos/theimpactstory_horizontal_white.png").convert("RGBA")
    lw = 250
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(logo, (W - lw - 64, 132))
    return img


def overlay_stream():
    base = static_layer()
    chunks = caption_chunks()
    events = []  # (start, end, img)
    cache = {}
    for ci, ch in enumerate(chunks):
        nxt = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else END_START
        for wi, w in enumerate(ch):
            s = w["start"]
            e = ch[wi + 1]["start"] if wi + 1 < len(ch) else min(nxt, ch[-1]["end"] + 0.6)
            events.append((s, e, (ci, wi)))
    hook_end = 2.3
    n = int(TOTAL * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", f"{R}/overlay.mov"], stdin=subprocess.PIPE)
    blank = np.zeros((H, W, 4), dtype=np.uint8).tobytes()
    for k in range(n):
        t = k / FPS
        if t >= END_START:
            proc.stdin.write(blank)
            continue
        key = None
        for s, e, ref in events:
            if s <= t < e:
                key = ref
        ck = (key, t < hook_end)
        if ck not in cache:
            img = base.copy()
            if key is not None:
                ci, wi = key
                img = Image.alpha_composite(img, draw_chunk(chunks[ci], wi, hook=t < hook_end))
            cache[ck] = img.tobytes()
        proc.stdin.write(cache[ck])
    proc.stdin.close()
    proc.wait()


def mix_audio():
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/vo.mp3", "-i", f"{R}/piano.wav", "-filter_complex",
         "[0:a]aresample=44100,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
         "loudnorm=I=-15:TP=-1.5:LRA=7,apad,asplit=2[vo][vk];"
         "[1:a]volume=0.22,afade=t=out:st=35.2:d=2.3[m];"
         "[m][vk]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=400[duck];"
         "[duck][vo]amix=inputs=2:weights='1 1':normalize=0,atrim=0:%.2f[a]" % TOTAL,
         "-map", "[a]", "-c:a", "aac", "-b:a", "192k", f"{R}/audio.m4a"])


def final():
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{R}/picture.mp4", "-i", f"{R}/overlay.mov", "-i", f"{R}/audio.m4a",
         "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-map", "2:a",
         *ENC, "-c:a", "copy", "-movflags", "+faststart", "-t", f"{TOTAL:.2f}", f"{R}/final.tmp.mp4"])
    os.replace(f"{R}/final.tmp.mp4", f"{R}/theimpactstory_reel_sujathullah_v2.mp4")


if __name__ == "__main__":
    steps = sys.argv[1:] or ["scenes", "overlay", "audio", "final"]
    if "scenes" in steps:
        render_scenes()
    if "overlay" in steps:
        overlay_stream()
    if "audio" in steps:
        mix_audio()
    if "final" in steps:
        final()
    print("done", steps)
