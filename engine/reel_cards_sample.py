"""Render transparent 1080x1920 text overlays for the sample real-footage Reel."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

REPO = "/home/claude/impactstory-posts._"
OUT = os.path.join(REPO, "posts/samples/reel_sujathullah")
F = os.path.join(REPO, "engine/fonts")
TEAL = (0, 91, 80)
GOLD = (232, 176, 75)
W, H = 1080, 1920
M = 80  # side margin


def font(w, s):
    return ImageFont.truetype(os.path.join(F, f"Poppins-{w}.ttf"), s)


def wrap(draw, words, fnt, maxw):
    lines, cur = [], []
    for w in words:
        test = " ".join(t for t, _ in cur + [w])
        if cur and draw.textlength(test, font=fnt) > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def rich(draw, text, fnt, y, lh, color=(255, 255, 255)):
    """*gold* markup; returns new y."""
    words, gold = [], False
    for tok in text.split(" "):
        start = tok.startswith("*")
        end = tok.endswith("*")
        t = tok.strip("*")
        if start:
            gold = True
        words.append((t, gold))
        if end:
            gold = False
    for line in wrap(draw, words, fnt, W - 2 * M):
        x = M
        for t, g in line:
            draw.text((x, y), t, font=fnt, fill=GOLD if g else color)
            x += draw.textlength(t + " ", font=fnt)
        y += lh
    return y


def gradient(img, top=1000):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = g.load()
    for y in range(top, H):
        a = min(1.0, (y - top) / 520)
        a = int(235 * (a ** 1.4))
        for x in range(W):
            px[x, y] = (*TEAL, a)
    return Image.alpha_composite(img, g)


def pill(draw, text):
    f = font("Bold", 30)
    tw = draw.textlength(text, font=f)
    draw.rounded_rectangle((M, 150, M + tw + 48, 210), radius=30, fill=GOLD)
    draw.text((M + 24, 158), text, font=f, fill=TEAL)


def handle(draw):
    f = font("Medium", 30)
    t = "@theimpactstory"
    draw.text((W - M - draw.textlength(t, font=f), 1560), t, font=f, fill=(255, 255, 255))


def card(name, kicker, head, body, head_size=74):
    img = gradient(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    d = ImageDraw.Draw(img)
    pill(d, "UNSUNG HERO")
    y = 1110
    if kicker:
        d.text((M, y), kicker, font=font("Bold", 40), fill=GOLD)
        y += 64
    y = rich(d, head, font("Bold", head_size), y, int(head_size * 1.18))
    if body:
        y += 14
        y = rich(d, body, font("Regular", 42), y, 58)
    assert y < 1540, (name, y)
    handle(d)
    img.save(os.path.join(OUT, name))


def end_card():
    img = Image.new("RGBA", (W, H), (*TEAL, 255))
    d = ImageDraw.Draw(img)
    logo = Image.open(os.path.join(REPO, "assets/logos/theimpactstory_horizontal_white.png")).convert("RGBA")
    lw = 760
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(logo, ((W - lw) // 2, 700))
    f = font("Bold", 56)
    for i, t in enumerate(["Small acts.", "Big change."]):
        d.text(((W - d.textlength(t, font=f)) / 2, 700 + logo.height + 90 + i * 72), t,
               font=f, fill=GOLD if i else (255, 255, 255))
    f2 = font("Medium", 40)
    t = "Follow for more good news"
    d.text(((W - d.textlength(t, font=f2)) / 2, 1240), t, font=f2, fill=(255, 255, 255))
    f3 = font("Light", 28)
    t = "Representative footage, not of the people named"
    d.text(((W - d.textlength(t, font=f3)) / 2, 1500), t, font=f3, fill=(200, 225, 220))
    img.save(os.path.join(OUT, "s6_end.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    card("s1.png", None, "*10 million* free meals.", "And it started with one student.", 96)
    card("s2.png", "2016 · SECUNDERABAD STATION", "A 22-year-old pharmacy student saw people *going hungry.*", None)
    card("s3.png", None, "He bought food with his *pocket money* and started feeding them.", None)
    card("s4.png", "TODAY", "Breakfast is served *every morning* outside Hyderabad's government hospitals.", None, 66)
    card("s5.png", None, "One small act. Repeated every day for *10 years.*", "Mohd Sujathullah · Humanity First Foundation")
    end_card()
    print("ok", sorted(os.listdir(OUT)), file=sys.stderr)
