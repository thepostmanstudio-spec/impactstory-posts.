"""Turn a rendered carousel into a 9:16 Reel with gentle motion and a soft music bed.

usage: python3 engine/reel.py posts/YYYY-MM-DD/batch.json <post_id> [out.mp4]

Needs the carousel PNGs already rendered by build.py. Uses ffmpeg only.
Sound rule: calm, warm and quiet — a soft pad, never a beat or loud effects.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import story_frame  # noqa: E402

FPS = 30
XF = 0.5  # crossfade seconds

# warm major chords (Hz) that change every slide: I – V – vi – IV
CHORDS = [(261.63, 329.63, 392.00), (196.00, 246.94, 293.66),
          (220.00, 261.63, 329.63), (174.61, 220.00, 261.63)]


def durations(n):
    d = [3.6] + [5.2] * (n - 2) + [4.2]
    return d


def pad_expr(durs):
    """aevalsrc expression: soft sine chord per slide with slow swell."""
    parts, t0 = [], 0.0
    for i, d in enumerate(durs):
        a, b, c = CHORDS[i % len(CHORDS)]
        t1 = t0 + d
        env = f"(between(t,{t0:.2f},{t1:.2f}))*(0.6+0.4*sin(PI*(t-{t0:.2f})/{d:.2f}))"
        tone = (f"(0.05*sin(2*PI*{a}*t)+0.035*sin(2*PI*{b}*t)+0.03*sin(2*PI*{c}*t)"
                f"+0.02*sin(2*PI*{a / 2}*t))")
        parts.append(f"{env}*{tone}")
        t0 = t1
    return "+".join(parts)


def main(batch_path, pid, out=None):
    d = os.path.dirname(os.path.abspath(batch_path))
    with open(os.path.join(d, "manifest.json")) as f:
        files = json.load(f)[pid]
    out = out or os.path.join(d, f"{pid}_reel.mp4")
    tmp = tempfile.mkdtemp()
    frames = []
    for i, fn in enumerate(files):
        fp = os.path.join(tmp, f"f{i}.png")
        story_frame(os.path.join(d, fn), fp, label=None if i < len(files) - 1 else "FOLLOW @THEIMPACTSTORY")
        frames.append(fp)
    durs = durations(len(frames))
    total = sum(durs) - XF * (len(durs) - 1)

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for fp, du in zip(frames, durs):
        cmd += ["-loop", "1", "-t", f"{du:.2f}", "-i", fp]
    cmd += ["-f", "lavfi", "-t", f"{total:.2f}", "-i",
            f"aevalsrc='{pad_expr(durs)}':s=44100"]
    fc = []
    for i, du in enumerate(durs):
        # slow push-in: 100% -> 104%
        fc.append(f"[{i}:v]scale=w='trunc(1080*(1+0.04*t/{du:.2f})/2)*2':h=-2:eval=frame,"
                  f"crop=1080:1920,setsar=1,fps={FPS},format=yuv420p[v{i}]")
    last, off = "v0", 0.0
    for i in range(1, len(durs)):
        off += durs[i - 1] - XF
        fc.append(f"[{last}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.2f}[x{i}]")
        last = f"x{i}"
    na = len(durs)
    fc.append(f"[{na}:a]lowpass=f=1800,volume=0.9,afade=t=in:d=1.2,"
              f"afade=t=out:st={total - 1.5:.2f}:d=1.5[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{last}]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-t", f"{total:.2f}", out]
    subprocess.run(cmd, check=True)
    print(out, f"{total:.1f}s")
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
