"""
Render CAD del molde por ray marching directo sobre el SDF.

No usa la malla: traza el campo analitico, asi que las sombras dentro de la
cavidad y el bisel de las aristas son los de la geometria real, no una
aproximacion. Material mate gris claro, luz de estudio, fondo blanco puro.

    python3 render_molde.py [--w 1600] [--ss 2]
"""

import argparse
import os

import numpy as np
from PIL import Image

import molde_sdf as M

OUT = os.path.dirname(os.path.abspath(__file__))

# --- campos 2D precomputados (el ray marching solo interpola) ---------------
GRID = 0.10
GX0, GX1 = -M.PLATE_W / 2 - 2.0, M.PLATE_W / 2 + 2.0
GY0, GY1 = -M.PLATE_H / 2 - 2.0, M.PLATE_H / 2 + 2.0

_gx = np.arange(GX0, GX1 + GRID, GRID)
_gy = np.arange(GY0, GY1 + GRID, GRID)
_GXX, _GYY = np.meshgrid(_gx, _gy, indexing="ij")
_D2, _ZF, _ = M.fields_2d(_GXX, _GYY)
_D2 = _D2.astype(np.float32)
_ZF = _ZF.astype(np.float32)
_NX, _NY = _D2.shape


def _bilinear(F, x, y):
    fx = np.clip((x - GX0) / GRID, 0, _NX - 1.001)
    fy = np.clip((y - GY0) / GRID, 0, _NY - 1.001)
    i0 = fx.astype(np.int32)
    j0 = fy.astype(np.int32)
    tx = fx - i0
    ty = fy - j0
    i1 = i0 + 1
    j1 = j0 + 1
    return ((F[i0, j0] * (1 - tx) + F[i1, j0] * tx) * (1 - ty)
            + (F[i0, j1] * (1 - tx) + F[i1, j1] * tx) * ty)


def sdf(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    d2 = _bilinear(_D2, x, y)
    zf = _bilinear(_ZF, x, y)
    plate2d = M.sd_rounded_rect(x, y, M.PLATE_W, M.PLATE_H, M.CORNER_R)

    plate = np.maximum(plate2d, np.abs(z - M.PLATE_T * 0.5) - M.PLATE_T * 0.5)
    wall = d2 + np.float32(M.TAN_DRAFT) * (np.float32(M.PLATE_T) - z)
    cav = M.op_intersect_round(wall, zf - z, np.float32(M.FILLET_R))
    cav = np.maximum(cav, z - np.float32(M.PLATE_T + M.CAV_TOP_EXT))
    return np.maximum(plate, -cav).astype(np.float32)


# ----------------------------------------------------------------------------
def march(ro, rd, tmin, tmax, steps=220, eps=0.0022):
    t = tmin.copy()
    alive = np.ones(t.shape, bool)
    hit = np.zeros(t.shape, bool)
    for _ in range(steps):
        if not alive.any():
            break
        idx = np.where(alive)[0]
        p = ro[idx] + rd[idx] * t[idx][:, None]
        d = sdf(p)
        t[idx] += np.maximum(d * 0.85, 1e-3)
        h = d < eps
        hit[idx[h]] = True
        alive[idx[h]] = False
        alive[idx[t[idx] > tmax[idx]]] = False
    return t, hit


def normals(p, e=0.035):
    n = np.empty_like(p)
    for k in range(3):
        o = np.zeros(3, np.float32)
        o[k] = e
        n[:, k] = sdf(p + o) - sdf(p - o)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)


def soft_shadow(p, ld, k=11.0, steps=64, tmax=220.0):
    t = np.full(len(p), 0.35, np.float32)
    res = np.ones(len(p), np.float32)
    alive = np.ones(len(p), bool)
    for _ in range(steps):
        if not alive.any():
            break
        idx = np.where(alive)[0]
        d = sdf(p[idx] + ld * t[idx][:, None])
        res[idx] = np.minimum(res[idx], k * d / np.maximum(t[idx], 1e-4))
        t[idx] += np.clip(d, 0.05, 6.0)
        alive[idx[(res[idx] < 0.002) | (t[idx] > tmax)]] = False
    return np.clip(res, 0.0, 1.0)


def ambient_occlusion(p, n, samples=7, span=3.6):
    occ = np.zeros(len(p), np.float32)
    w = 1.0
    total = 0.0
    for i in range(1, samples + 1):
        h = span * i / samples
        d = sdf(p + n * h)
        occ += w * np.maximum(h - d, 0.0) / h
        total += w
        w *= 0.72
    return np.clip(1.0 - occ / total * 1.25, 0.0, 1.0)


# ----------------------------------------------------------------------------
def render(width, ss, az_deg, el_deg, dist, fov_deg, target, aspect=4 / 3):
    W = width * ss
    H = int(width / aspect) * ss

    az = np.radians(az_deg)
    el = np.radians(el_deg)
    tgt = np.array(target, np.float32)
    eye = tgt + dist * np.array(
        [np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)], np.float32
    )

    fwd = tgt - eye
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0, 0, 1], np.float32))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)

    px = (np.arange(W) + 0.5) / W * 2 - 1
    py = 1 - (np.arange(H) + 0.5) / H * 2
    PX, PY = np.meshgrid(px, py, indexing="xy")
    scale = np.tan(np.radians(fov_deg) * 0.5)
    rd = (fwd[None, None, :]
          + right[None, None, :] * (PX * scale * aspect)[:, :, None]
          + up[None, None, :] * (PY * scale)[:, :, None])
    rd = (rd / np.linalg.norm(rd, axis=2, keepdims=True)).reshape(-1, 3).astype(np.float32)
    ro = np.repeat(eye[None, :], len(rd), 0).astype(np.float32)

    # recorte contra la caja envolvente de la placa
    lo = np.array([-M.PLATE_W / 2 - 1, -M.PLATE_H / 2 - 1, -1.0], np.float32)
    hi = np.array([M.PLATE_W / 2 + 1, M.PLATE_H / 2 + 1, M.PLATE_T + 1.0], np.float32)
    inv = 1.0 / np.where(np.abs(rd) < 1e-8, 1e-8, rd)
    t1 = (lo - ro) * inv
    t2 = (hi - ro) * inv
    tn = np.maximum.reduce(np.minimum(t1, t2), axis=1)
    tf = np.minimum.reduce(np.maximum(t1, t2), axis=1)
    box = tf > np.maximum(tn, 0.0)

    img = np.ones((len(rd), 3), np.float32)  # fondo blanco puro
    idx = np.where(box)[0]
    tmin = np.maximum(tn[idx], 0.0).astype(np.float32)
    tmax = tf[idx].astype(np.float32) + 1.0

    t, hit = march(ro[idx], rd[idx], tmin, tmax)
    hidx = idx[hit]
    if len(hidx) == 0:
        return img.reshape(H, W, 3)

    p = (ro[hidx] + rd[hidx] * t[hit][:, None]).astype(np.float32)
    n = normals(p)

    # --- iluminacion de estudio ---------------------------------------------
    key = np.array([-0.48, -0.58, 0.66], np.float32)     # principal, alta izq.
    key /= np.linalg.norm(key)
    fill = np.array([0.80, -0.26, 0.54], np.float32)     # relleno derecha
    fill /= np.linalg.norm(fill)
    rim = np.array([0.10, 0.88, 0.46], np.float32)       # contra desde el fondo
    rim /= np.linalg.norm(rim)

    ao = ambient_occlusion(p + n * 0.02, n)
    sh = soft_shadow(p + n * 0.10, key)

    nk = np.maximum(n @ key, 0.0)
    nf = np.maximum(n @ fill, 0.0)
    nr = np.maximum(n @ rim, 0.0)
    sky = 0.5 + 0.5 * n[:, 2]

    albedo = np.array([0.735, 0.740, 0.752], np.float32)   # gris claro mate
    lit = (0.70 * nk * sh
           + 0.16 * nf * (0.30 + 0.70 * ao)
           + 0.08 * nr * ao
           + (0.14 + 0.14 * sky) * ao)

    # especular mate ancho
    v = -rd[hidx]
    hv = key + v
    hv /= np.linalg.norm(hv, axis=1, keepdims=True)
    spec = np.power(np.maximum((n * hv).sum(1), 0.0), 38.0) * 0.10 * sh

    col = albedo[None, :] * lit[:, None] + spec[:, None]
    col = np.power(np.clip(col, 0.0, 1.0), 1 / 2.2)
    img[hidx] = np.clip(col, 0.0, 1.0)

    out = img.reshape(H, W, 3)
    if ss > 1:
        out = out.reshape(H // ss, ss, W // ss, ss, 3).mean(axis=(1, 3))
    return out


def save(arr, path):
    Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)
    print("  ->", os.path.basename(path))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", type=int, default=1600)
    ap.add_argument("--ss", type=int, default=2)
    a = ap.parse_args()

    views = [
        # tres cuartos superior: camara inclinada 30 grados respecto a la
        # vertical, que es la que ensena que el caballo esta hundido
        ("render-molde-3-4.png", dict(az_deg=-73, el_deg=58, dist=400,
                                      fov_deg=22, target=(0, 0, 7.5))),
        ("render-molde-cenital.png", dict(az_deg=-90, el_deg=74, dist=410,
                                          fov_deg=21, target=(0, 0, 7.5))),
        ("render-molde-rasante.png", dict(az_deg=-56, el_deg=31, dist=405,
                                          fov_deg=22, target=(0, 0, 6.5))),
    ]
    for name, kw in views:
        print("Trazando", name, "...")
        img = render(a.w, a.ss, **kw)
        save(img, os.path.join(OUT, name))


if __name__ == "__main__":
    main()
