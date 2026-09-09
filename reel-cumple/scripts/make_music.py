#!/usr/bin/env python3
"""Genera una pieza de piano emotiva, libre de regalías (sintetizada), para el reel.

Uso: python3 make_music.py salida.wav [duracion_segundos]
"""
import sys, math
import numpy as np
from scipy.signal import fftconvolve, butter, lfilter

SR = 48000
BPM = 64.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

def piano_note(n, dur, vel=0.8):
    """Nota de piano por síntesis aditiva con decaimiento y ligera inarmonicidad."""
    f = midi(n)
    length = int(SR * (dur + 2.5))
    t = np.arange(length) / SR
    out = np.zeros(length)
    tau = 0.9 + 3.0 * (1 - min(n, 96) / 96)  # graves resuenan más
    for k in range(1, 9):
        inh = 1 + 0.0004 * k * k
        amp = (1.0 / k ** 1.35) * (1.0 if k < 5 else 0.6)
        if f * k * inh > SR / 2.2:
            break
        env = np.exp(-t / (tau / (1 + 0.35 * (k - 1))))
        out += amp * env * np.sin(2 * math.pi * f * k * inh * t + rng.uniform(0, 6.28))
    # ataque
    att = int(SR * 0.006)
    out[:att] *= np.linspace(0, 1, att)
    # ruido de martillo muy suave
    hn = rng.normal(0, 1, int(SR * 0.02)) * np.linspace(1, 0, int(SR * 0.02)) * 0.02
    out[:len(hn)] += hn
    # liberación: al soltar la tecla decae más rápido
    rel_start = int(SR * dur)
    if rel_start < length:
        rel = np.exp(-np.arange(length - rel_start) / (SR * 0.35))
        out[rel_start:] *= rel
    # brillo según velocidad
    b, a = butter(1, min(0.99, (1200 + 5000 * vel) / (SR / 2)))
    out = lfilter(b, a, out)
    return out * vel * 0.32

def pad_chord(notes, dur):
    length = int(SR * (dur + 1.5))
    t = np.arange(length) / SR
    out = np.zeros(length)
    for n in notes:
        f = midi(n)
        for det in (-0.6, 0.0, 0.6):
            ff = f * 2 ** (det / 1200 * 4)
            out += 0.5 * np.sin(2 * math.pi * ff * t) + 0.18 * np.sin(2 * math.pi * 2 * ff * t)
    env = np.minimum(1, t / 1.6) * np.where(t < dur, 1, np.exp(-(t - dur) / 0.9))
    b, a = butter(2, 900 / (SR / 2))
    out = lfilter(b, a, out * env)
    return out * 0.012

def place(buf, sig, start):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]

def build(total):
    # Progresión (2 compases por acorde no; 1 compás por acorde), 8 compases por vuelta
    # C  G/B  Am  Em/G | F  C/E  Dm7  G  (canon descendente)
    prog = [
        (48, [60, 64, 67]), (47, [59, 62, 67]), (45, [57, 60, 64]), (43, [55, 59, 64]),
        (41, [53, 57, 60]), (40, [52, 55, 60]), (38, [50, 53, 57, 60]), (43, [55, 59, 62, 65]),
    ]
    melody_a = [72, 71, 69, 67, 65, 64, 62, 67]   # una nota larga por compás (pasada 1)
    melody_b = [76, 74, 72, 71, 69, 72, 71, 67]   # variación (pasada 2)
    melody_c = [79, 78, 76, 74, 72, 76, 74, 72]   # clímax (pasada 3)
    n_bars = int(math.ceil(total / BAR)) + 2
    buf = np.zeros(int(SR * (total + 6)))
    for bar in range(n_bars):
        t0 = bar * BAR
        root, chord = prog[bar % 8]
        pas = bar // 8
        # Pad de cuerdas suave desde el compás 0 (crece en pasadas siguientes)
        pad_gain = [0.7, 1.0, 1.15, 1.0, 0.8][min(pas, 4)]
        place(buf, pad_chord([c - 12 for c in chord[:3]], BAR) * pad_gain, t0)
        # Bajo: raíz en negra 1 y 3 (octava grave)
        place(buf, piano_note(root - 12, BEAT * 2, 0.55), t0)
        place(buf, piano_note(root, BEAT * 2, 0.45), t0 + 2 * BEAT)
        # Arpegio en corcheas (salvo la primera pasada, que es más quieta)
        pattern = chord + chord[::-1][1:-1] if len(chord) == 3 else chord + chord[::-1][1:-1]
        if pas == 0:
            steps = [0, 2, 4, 6]  # negras
            for s in steps:
                place(buf, piano_note(chord[(s // 2) % len(chord)], BEAT * 0.95, 0.5 + rng.uniform(-0.05, 0.05)), t0 + s * BEAT / 2)
        else:
            for s in range(8):
                nn = pattern[s % len(pattern)]
                vel = 0.55 + 0.12 * (s % 2 == 0) + rng.uniform(-0.05, 0.05)
                place(buf, piano_note(nn, BEAT * 0.6, vel), t0 + s * BEAT / 2 + rng.uniform(-0.006, 0.006))
        # Melodía
        mel = [None, melody_a, melody_b, melody_c, melody_b][min(pas, 4)]
        if mel is not None:
            m = mel[bar % 8]
            place(buf, piano_note(m, BAR * 0.9, 0.85), t0 + rng.uniform(0, 0.01))
            # nota de paso a mitad del compás en compases pares
            if bar % 2 == 1:
                place(buf, piano_note(m - 2 if m - 2 in (60,62,64,65,67,69,71,72,74,76,77,79) else m - 1, BEAT * 1.2, 0.6), t0 + 2.5 * BEAT)
    # Acorde final de C mayor resonando
    t_end = n_bars * BAR
    for n in (36, 48, 55, 60, 64, 67, 72):
        place(buf, piano_note(n, 5.0, 0.7), t_end)
    return buf

def reverb(sig):
    ir_len = int(SR * 2.4)
    t = np.arange(ir_len) / SR
    irs = []
    for seed in (1, 2):
        r = np.random.default_rng(seed).normal(0, 1, ir_len) * np.exp(-t / 0.75)
        b, a = butter(2, 3500 / (SR / 2)); r = lfilter(b, a, r)
        irs.append(r / np.sqrt(np.sum(r ** 2)))
    wet_l = fftconvolve(sig, irs[0])[: len(sig)]
    wet_r = fftconvolve(sig, irs[1])[: len(sig)]
    return np.stack([sig + 0.55 * wet_l, sig + 0.55 * wet_r], axis=1)

def main():
    out = sys.argv[1]
    total = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0
    mono = build(total)
    st = reverb(mono)
    # normalizar y fundir final
    st = st / (np.max(np.abs(st)) + 1e-9) * 0.85
    n = len(st)
    fade = int(SR * 5.0)
    tail = int(SR * (total))
    if tail < n:
        env = np.ones(n)
        env[tail - fade: tail] = np.linspace(1, 0, fade)
        env[tail:] = 0
        st = st * env[:, None]
        st = st[:tail]
    import wave
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"música: {out} ({len(st)/SR:.1f}s)")

if __name__ == "__main__":
    main()
