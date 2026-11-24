"""Soft felt-piano arpeggio bed, I-V-vi-IV in C, ~72 bpm, written note by note."""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

SR = 44100
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
BPM = 72
beat = 60 / BPM
eighth = beat / 2


def midi(n):
    return 440 * 2 ** ((n - 69) / 12)


def note(f, length, vel):
    t = np.arange(int(SR * length)) / SR
    # additive piano-ish partials with slight inharmonicity and per-partial decay
    s = np.zeros_like(t)
    for k, a in enumerate([1.0, 0.45, 0.22, 0.12, 0.06, 0.03], start=1):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        s += a * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1.6 + 1.1 * k))
    att = np.minimum(1, t / 0.006)
    rel = np.exp(-np.maximum(0, t - (length - 0.25)) * 12)
    return vel * s * att * rel


# chords: (bass, [arp notes])
prog = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69])]
pattern = [0, 1, 2, 3, 2, 1, 2, 1]  # 8 eighths per bar
bar = 8 * eighth
out = np.zeros(int(SR * (DUR + 4)))
t0, i = 0.0, 0
rng = np.random.default_rng(7)
while t0 < DUR:
    bass, arp = prog[i % 4]
    seg = note(midi(bass), bar + 1.5, 0.30)
    a = int(t0 * SR)
    out[a:a + len(seg)] += seg[: len(out) - a]
    seg = note(midi(bass + 12), bar + 1.0, 0.12)
    out[a:a + len(seg)] += seg[: len(out) - a]
    for j, p in enumerate(pattern):
        tt = t0 + j * eighth + rng.uniform(-0.008, 0.008)
        seg = note(midi(arp[p]), 2.2, 0.16 + 0.05 * (j % 4 == 0) + rng.uniform(-0.02, 0.02))
        a = int(tt * SR)
        out[a:a + len(seg)] += seg[: len(out) - a]
    # gentle top melody note on bar start every other bar
    if i % 2 == 0:
        seg = note(midi(arp[3] + 12), 3.0, 0.07)
        a = int((t0 + 2 * beat) * SR)
        out[a:a + len(seg)] += seg[: len(out) - a]
    t0 += bar
    i += 1

# simple room reverb: exponentially decaying noise impulse
ir_t = np.arange(int(SR * 2.2)) / SR
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.2)
ir[0] = 1.0
wet = fftconvolve(out, ir)[: len(out)]
wet /= np.max(np.abs(wet)) + 1e-9
dry = out / (np.max(np.abs(out)) + 1e-9)
mix = 0.65 * dry + 0.35 * wet
# soft low-pass by moving average for warmth
k = 6
mix = np.convolve(mix, np.ones(k) / k, mode="same")
mix = mix[: int(SR * DUR)]
fade = int(SR * 2.5)
mix[-fade:] *= np.linspace(1, 0, fade)
mix[: int(SR * 0.3)] *= np.linspace(0, 1, int(SR * 0.3))
mix = 0.8 * mix / np.max(np.abs(mix))
st = np.stack([mix, np.roll(mix, 220)], axis=1)
wavfile.write("piano.wav", SR, (st * 32767).astype(np.int16))
print("piano.wav", DUR)
