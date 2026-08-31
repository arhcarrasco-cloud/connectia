"""
Render de las dos piezas por ray marching directo sobre el SDF.

No rebana ni mallea: traza el campo analitico, asi que la silueta y las
sombras son las de la geometria real. Material resina/PLA mate, luz de
estudio de tres puntos, fondo blanco con sombra de contacto.

    python3 render_figuras.py [--w 1500] [--ss 2]
"""

import argparse
import os

import numpy as np
from PIL import Image

import figuras_sdf as S

OUT = os.path.dirname(os.path.abspath(__file__))
F = np.float32


def normal(fn, p, e=0.25):
    ex = np.zeros_like(p); ex[..., 0] = e
    ey = np.zeros_like(p); ey[..., 1] = e
    ez = np.zeros_like(p); ez[..., 2] = e
    n = np.stack([fn(p + ex) - fn(p - ex),
                  fn(p + ey) - fn(p - ey),
                  fn(p + ez) - fn(p - ez)], -1)
    return n / np.maximum(np.sqrt((n ** 2).sum(-1, keepdims=True)), 1e-6)


def caja(ro, rd, lo, hi):
    """Entrada y salida del rayo en la AABB. Ahorra el 80% de los pasos: sin
    esto se marcha por el aire vacio que rodea la pieza."""
    inv = 1.0 / np.where(np.abs(rd) < 1e-8, 1e-8, rd)
    t0 = (F(lo) - ro) * inv
    t1 = (F(hi) - ro) * inv
    tn = np.minimum(t0, t1).max(-1)
    tf = np.maximum(t0, t1).min(-1)
    return np.maximum(tn, 0.0), tf


def march(fn, ro, rd, lo, hi, steps=160, eps=0.05):
    """Marcha compactando: cada paso solo evalua los rayos todavia vivos."""
    t0, t1 = caja(ro, rd, lo, hi)
    shape = rd.shape[:-1]
    t = t0.copy()
    hit = np.zeros(shape, bool)
    idx = np.flatnonzero((t0 < t1).ravel())
    ro_f = ro.reshape(-1, 3)
    rd_f = rd.reshape(-1, 3)
    t_f = t.ravel()
    tmax_f = t1.ravel()
    hit_f = hit.ravel()
    for _ in range(steps):
        if idx.size == 0:
            break
        p = ro_f[idx] + rd_f[idx] * t_f[idx][:, None]
        d = fn(p).astype(np.float32)
        golpe = d < eps
        hit_f[idx[golpe]] = True
        t_f[idx] += np.maximum(d, 0.015) * 0.9
        vivo = (~golpe) & (t_f[idx] < tmax_f[idx])
        idx = idx[vivo]
    return t_f.reshape(shape), hit_f.reshape(shape)


def sombra(fn, p, ldir, lo, hi, k=9.0, steps=40):
    """Sombra suave por la distancia minima al ocluyente, tambien compactada."""
    n = p.shape[0]
    ld = np.broadcast_to(ldir, p.shape).astype(np.float32) if ldir.ndim == 1 else ldir
    t0, t1 = caja(p, ld, lo, hi)
    t = np.maximum(t0, 1.2).astype(np.float32)
    res = np.ones(n, np.float32)
    idx = np.flatnonzero(t < t1)
    for _ in range(steps):
        if idx.size == 0:
            break
        q = p[idx] + ld[idx] * t[idx][:, None]
        d = np.maximum(fn(q).astype(np.float32), 0.0)
        res[idx] = np.minimum(res[idx], k * d / np.maximum(t[idx], 1e-3))
        t[idx] += np.clip(d, 0.7, 12.0)
        idx = idx[(res[idx] > 0.004) & (t[idx] < t1[idx])]
    return np.clip(res, 0.0, 1.0)


def render(key, width=1400, ss=2, yaw=-31.0, pitch=9.0):
    P = S.PIEZAS[key]
    fn = P["f"]
    W, D, H = P["w"], P["d"], P["h"]

    W_px = int(width * ss)
    H_px = int(width * 0.92 * ss)
    # el encuadre lo fija la cota mas larga vista de 3/4, no la caja
    target = np.array([0.0, 0.0, H * 0.48], np.float32)
    radio = max(W, H) * 1.58
    a, b = np.radians(yaw), np.radians(pitch)
    eye = target + np.array([np.sin(a) * np.cos(b) * radio,
                             -np.cos(a) * np.cos(b) * radio,
                             np.sin(b) * radio], np.float32)

    fwd = target - eye
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0, 0, 1.0], np.float32))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)

    fov = np.radians(23.0)
    xs = (np.arange(W_px) + 0.5) / W_px * 2 - 1
    ys = 1 - (np.arange(H_px) + 0.5) / H_px * 2
    X, Y = np.meshgrid(xs, ys, indexing="xy")
    asp = W_px / H_px
    rd = (fwd + right * (X * asp * np.tan(fov))[..., None]
          + up * (Y * np.tan(fov))[..., None]).astype(np.float32)
    rd /= np.sqrt((rd ** 2).sum(-1, keepdims=True))
    ro = np.broadcast_to(eye, rd.shape).astype(np.float32)

    lo = np.array([-W / 2 - 2, -D / 2 - 2, -1.0], np.float32)
    hi = np.array([W / 2 + 2, D / 2 + 2, H + 4.0], np.float32)
    t, hit = march(fn, ro, rd, lo, hi)

    # suelo z=0 para la sombra de contacto
    denom = np.where(np.abs(rd[..., 2]) < 1e-6, 1e-6, rd[..., 2])
    tp = -ro[..., 2] / denom
    piso = (tp > 0) & (~hit)

    L1 = np.array([-0.45, -0.72, 0.53], np.float32); L1 /= np.linalg.norm(L1)
    L2 = np.array([0.78, -0.35, 0.28], np.float32); L2 /= np.linalg.norm(L2)
    L3 = np.array([0.15, 0.85, 0.24], np.float32); L3 /= np.linalg.norm(L3)

    img = np.ones((H_px, W_px, 3), np.float32)

    # --- sombra proyectada sobre el piso
    if piso.any():
        pp = ro[piso] + rd[piso] * tp[piso][..., None]
        sh = sombra(fn, pp, L1, lo, hi, k=5.0, steps=34)
        r = np.sqrt((pp[..., :2] ** 2).sum(-1))
        vig = np.clip(1.0 - (r - max(W, D) * 0.55) / (max(W, D) * 1.5), 0.0, 1.0)
        g = 1.0 - (1.0 - sh) * 0.30 * vig
        img[piso] = np.stack([g, g, g * 1.004], -1)

    # --- la pieza
    if hit.any():
        ph = ro[hit] + rd[hit] * t[hit][..., None]
        n = normal(fn, ph)
        vd = -rd[hit]
        alb = np.array([0.905, 0.898, 0.878], np.float32)   # PLA marfil mate

        def lam(L):
            return np.clip((n * L).sum(-1), 0.0, 1.0)

        sh1 = sombra(fn, ph + n * 0.6, L1, lo, hi)
        dif = (lam(L1) * 1.00 * sh1 + lam(L2) * 0.34 + lam(L3) * 0.20)
        amb = 0.30 + 0.16 * np.clip(n[..., 2] * 0.5 + 0.5, 0, 1)

        h = L1 + vd
        h /= np.maximum(np.sqrt((h ** 2).sum(-1, keepdims=True)), 1e-6)
        spec = np.clip((n * h).sum(-1), 0, 1) ** 26 * 0.17 * sh1
        fres = (1.0 - np.clip((n * vd).sum(-1), 0, 1)) ** 3.2 * 0.10

        c = alb * (dif * 0.62 + amb)[..., None] + (spec + fres)[..., None]
        img[hit] = np.clip(c, 0, 1)

    img = np.clip(img, 0, 1) ** (1 / 1.9)
    im = Image.fromarray((img * 255 + 0.5).astype(np.uint8))
    if ss > 1:
        im = im.resize((W_px // ss, H_px // ss), Image.LANCZOS)
    path = os.path.join(OUT, f"render-pieza-{key}.png")
    im.save(path, optimize=True)
    print(f"  {path}   {im.size[0]}x{im.size[1]}")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=1400)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--pieza", default="AB")
    a = ap.parse_args()
    print("Render por ray marching sobre el SDF")
    for k in a.pieza:
        P = S.PIEZAS[k]
        print(f"Pieza {k} — {P['nombre']}  "
              f"{P['w']:.0f} x {P['d']:.0f} x {P['h']:.0f} mm")
        render(k, a.w, a.ss)


if __name__ == "__main__":
    main()
