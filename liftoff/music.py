"""Original ambient bed for Liftoff Daily Reels: a soft impact on frame 1, warm detuned pad, sub drone,
a slow heartbeat pulse and a sparkle of bell notes. Generated from scratch every time (no samples, nothing
another track could match), so Instagram's audio matching has nothing to flag."""
import math
import random
import struct
import wave

RATE = 22050
TAU = 2 * math.pi
KEYS = [50, 52, 45, 47, 48]                 # D, E, A, B, C (MIDI roots, low register)
MINOR_PENTA = [0, 3, 5, 7, 10, 12, 15, 17, 19, 22, 24]
PROGRESSIONS = [[(0, 3, 7, 14), (-4, 0, 3, 10)],     # i → VI (add9 colors)
                [(0, 3, 7, 10), (-2, 2, 5, 9)],      # i7 → VII
                [(0, 7, 14, 15), (-5, 2, 7, 10)]]    # open fifths → v


def _hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def make_ambient(path, seconds, seed="liftoffdaily", pulse_bpm=96):
    rnd = random.Random(seed)
    n = int(seconds * RATE)
    mix = [0.0] * n
    root = rnd.choice(KEYS)
    prog = rnd.choice(PROGRESSIONS)
    half = n // 2

    # pad: each chord tone = 3 slightly detuned sines, slow attack, cross-fade between the two chords
    for ci, chord in enumerate(prog):
        start, end = (0, half + RATE // 2) if ci == 0 else (half - RATE // 2, n)
        for iv in chord:
            f = _hz(root + 12 + iv)
            for det in (-0.004, 0.0, 0.0045):
                ff = f * (1 + det)
                ph = rnd.random() * TAU
                for i in range(start, end):
                    t = i / RATE
                    a_in = min(1.0, (i - start) / (RATE * (0.25 if ci == 0 else 1.0)))
                    a_out = min(1.0, (end - i) / (RATE * 1.0))
                    mix[i] += 0.035 * a_in * a_out * math.sin(TAU * ff * t + ph)

    # sub drone + soft impact on frame 1 (the "hook" hit)
    fsub = _hz(root - 12)
    for i in range(n):
        t = i / RATE
        mix[i] += 0.09 * min(1.0, t / 0.05) * math.sin(TAU * fsub * t)
        if t < 1.2:
            env = math.exp(-t * 4.5)
            mix[i] += 0.55 * env * math.sin(TAU * (48 + 60 * math.exp(-t * 18)) * t)

    # heartbeat pulse: two soft low thumps per beat, from 0.4s
    beat = 60 / pulse_bpm
    t0 = 0.4
    while t0 < seconds - 0.3:
        for off, amp in ((0.0, 0.32), (0.18, 0.18)):
            s = int((t0 + off) * RATE)
            for j in range(int(0.25 * RATE)):
                if s + j >= n:
                    break
                tt = j / RATE
                mix[s + j] += amp * math.exp(-tt * 16) * math.sin(TAU * (55 + 40 * math.exp(-tt * 30)) * tt)
        t0 += beat

    # sparkle: bell notes on the pentatonic scale, sparse and quiet
    t = 0.6
    while t < seconds - 0.8:
        f = _hz(root + 36 + rnd.choice(MINOR_PENTA))
        s = int(t * RATE)
        for j in range(int(1.6 * RATE)):
            if s + j >= n:
                break
            tt = j / RATE
            env = math.exp(-tt * 2.6) * min(1.0, tt / 0.004)
            mix[s + j] += 0.045 * env * (math.sin(TAU * f * tt) + 0.3 * math.sin(TAU * f * 2.76 * tt))
        t += rnd.choice((0.5, 0.75, 1.0)) * beat * 2

    # fades + normalize
    fade = int(0.35 * RATE)
    for i in range(fade):
        mix[n - 1 - i] *= i / fade
    peak = max(abs(x) for x in mix) or 1
    gain = 0.85 / peak
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x * gain)) * 32767)) for x in mix))
    return path
