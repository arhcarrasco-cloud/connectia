"""
Renders trazados sobre el campo analitico, sin pasar por la malla.

    python3 render.py duo --w 1100
    python3 render.py diploma --vista frente

Traza por esferas contra el SDF. Los rayos se recortan primero contra la caja
envolvente: sin eso, los dos tercios de pixeles que no tocan la figura marchan
hasta el limite y el render tarda diez veces mas.

El acabado es resina gris sin pintar, que es como sale de la maquina.
"""

import argparse
import time

import numpy as np

import escenas as E

FONDO_ALTO = np.array([0.855, 0.855, 0.870])
FONDO_BAJO = np.array([0.700, 0.700, 0.720])
RESINA = np.array([0.660, 0.645, 0.625])
PISO = np.array([0.600, 0.598, 0.605])

LUZ_KEY = np.array([-0.55, -0.72, 0.62])
LUZ_FILL = np.array([0.78, -0.42, 0.24])
LUZ_RIM = np.array([0.10, 0.86, 0.34])


def _n(v):
    return v / (np.linalg.norm(v) + 1e-12)


def aabb(ro, rd, lo, hi):
    """Rango [t0, t1] en que cada rayo cruza la caja. t1 < t0 = no la toca."""
    inv = 1.0 / np.where(np.abs(rd) < 1e-9, 1e-9, rd)
    ta = (lo - ro) * inv
    tb = (hi - ro) * inv
    t0 = np.maximum.reduce(np.minimum(ta, tb), axis=1)
    t1 = np.minimum.reduce(np.maximum(ta, tb), axis=1)
    return np.maximum(t0, 0.0), t1


def trazar(campo, ro, rd, lo, hi, pasos=110, eps=0.012, tmax=1400.0):
    n = len(rd)
    t = np.zeros(n)
    vivo = np.zeros(n, bool)
    t0, t1 = aabb(ro, rd, lo, hi)
    tocan = t1 > t0
    t[tocan] = t0[tocan]
    vivo[tocan] = True
    golpe = np.zeros(n, bool)
    for _ in range(pasos):
        if not vivo.any():
            break
        idx = np.flatnonzero(vivo)
        p = ro + rd[idx] * t[idx, None]
        d = campo(p[:, 0], p[:, 1], p[:, 2])
        t[idx] += np.maximum(d, eps * 0.25)
        hit = d < eps
        golpe[idx[hit]] = True
        vivo[idx[hit]] = False
        vivo[idx[(t[idx] > np.minimum(t1[idx] + 2.0, tmax))]] = False
    return t, golpe


def normal(campo, p, h=0.05):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    nx = campo(x + h, y, z) - campo(x - h, y, z)
    ny = campo(x, y + h, z) - campo(x, y - h, z)
    nz = campo(x, y, z + h) - campo(x, y, z - h)
    v = np.stack([nx, ny, nz], 1)
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-12)


def oclusion(campo, p, nrm, muestras=6, paso=3.2):
    """AO por muestreo del campo a lo largo de la normal."""
    oc, w = np.zeros(len(p)), 0.0
    for i in range(1, muestras + 1):
        h = paso * i / muestras
        d = campo(*(p + nrm * h).T)
        oc += (h - np.maximum(d, 0.0)) / (2.0 ** i)
        w += 1.0 / (2.0 ** i)
    return np.clip(1.0 - 1.5 * oc / (w * paso), 0.18, 1.0)


def sombra(campo, p, ldir, lo, hi, pasos=42, k=14.0):
    ro = p + ldir * 0.7
    t = np.full(len(p), 0.6)
    s = np.ones(len(p))
    vivo = np.ones(len(p), bool)
    for _ in range(pasos):
        if not vivo.any():
            break
        idx = np.flatnonzero(vivo)
        q = ro[idx] + ldir * t[idx, None]
        d = campo(q[:, 0], q[:, 1], q[:, 2])
        s[idx] = np.minimum(s[idx], k * d / np.maximum(t[idx], 1e-3))
        t[idx] += np.clip(d, 0.35, 14.0)
        vivo[idx[(d < 0.01) | (t[idx] > 420.0)]] = False
    return np.clip(s, 0.0, 1.0)


# El FOV va calculado para que la figura llene el encuadre: con la mira a
# ~540 mm, medio cuadro son 540*tan(fov), y la figura mide 190 mm de alto.
VISTAS = {
    "frente": dict(ojo=(0.0, -540.0, 112.0), mira=(0.0, 0.0, 94.0), fov=11.5),
    "tres-cuartos": dict(ojo=(-330.0, -430.0, 176.0), mira=(0.0, 0.0, 92.0),
                         fov=12.0),
    "tres-cuartos-der": dict(ojo=(330.0, -430.0, 176.0), mira=(0.0, 0.0, 92.0),
                             fov=12.0),
    "perfil": dict(ojo=(-470.0, -250.0, 128.0), mira=(0.0, 0.0, 94.0), fov=12.0),
    "busto": dict(ojo=(-105.0, -290.0, 166.0), mira=(-6.0, 0.0, 142.0), fov=9.5),
}


def render(escena, vista, w, alto_rel, ss, fov=None):
    esc = E.ESCENAS[escena]
    (x0, x1), (y0, y1), (z0, z1) = esc["caja"]
    lo = np.array([x0, y0, -0.2])
    hi = np.array([x1, y1, z1])

    def figura(X, Y, Z):
        return esc["f"](X, Y, Z)

    def escena_render(X, Y, Z):
        return np.minimum(figura(X, Y, Z), Z)      # figura + piso en z = 0

    V = dict(VISTAS[vista])
    if fov:
        V["fov"] = fov
    ojo = np.array(V["ojo"])
    fwd = _n(np.array(V["mira"]) - ojo)
    der = _n(np.cross(fwd, np.array([0.0, 0.0, 1.0])))
    arr = np.cross(der, fwd)

    W, Hh = w * ss, int(w * alto_rel) * ss
    px = (np.arange(W) + 0.5) / W * 2 - 1
    py = (np.arange(Hh) + 0.5) / Hh * 2 - 1
    PX, PY = np.meshgrid(px, py, indexing="xy")
    esc_t = np.tan(np.radians(V["fov"]))
    ar = W / Hh
    rd = (fwd + der * (PX.ravel()[:, None] * esc_t * ar)
          - arr * (PY.ravel()[:, None] * esc_t))
    rd = rd / np.linalg.norm(rd, axis=1, keepdims=True)

    t0 = time.time()
    # el piso obliga a marchar tambien fuera de la caja de la figura
    lo_s, hi_s = lo - np.array([600, 600, 0.0]), hi + np.array([600, 600, 0.0])
    t, golpe = trazar(escena_render, ojo, rd, lo_s, hi_s)
    print(f"    trazado {golpe.sum()/len(rd):.0%} de {len(rd)/1e6:.1f} M rayos "
          f"en {time.time()-t0:.0f}s", flush=True)

    # fondo: barrido de estudio
    grad = (PY.ravel() + 1) / 2
    img = FONDO_ALTO * (1 - grad[:, None]) + FONDO_BAJO * grad[:, None]

    idx = np.flatnonzero(golpe)
    if len(idx):
        p = ojo + rd[idx] * t[idx, None]
        nrm = normal(escena_render, p)
        es_piso = figura(p[:, 0], p[:, 1], p[:, 2]) > 0.06
        alb = np.where(es_piso[:, None], PISO, RESINA)

        # Las tres luces se presupuestan para que la suma no reviente el blanco:
        # ambiente 0.22 + key 0.62 + relleno 0.20 + contra 0.16 = 1.20 en el
        # peor caso, y ~0.7 en una superficie tipica.
        ao = oclusion(escena_render, p, nrm)
        col = alb * (0.22 * ao)[:, None]
        for ldir, inten, sombrea in ((_n(LUZ_KEY), 0.62, True),
                                     (_n(LUZ_FILL), 0.20, False),
                                     (_n(LUZ_RIM), 0.16, False)):
            lam = np.maximum(nrm @ ldir, 0.0)
            if sombrea:
                s = sombra(escena_render, p, ldir, lo, hi)
                col += alb * (lam * inten * ao * s)[:, None]
                # especular por pixel, no contra la direccion media de la camara
                hd = ldir - rd[idx]
                hd = hd / (np.linalg.norm(hd, axis=1, keepdims=True) + 1e-12)
                esp = np.maximum((nrm * hd).sum(1), 0.0) ** 36
                col += (esp * 0.07 * s)[:, None]
            else:
                col += alb * (lam * inten * ao)[:, None]
        # niebla suave para que el piso se funda con el fondo
        f = np.clip((t[idx] - 380.0) / 420.0, 0.0, 1.0)[:, None]
        col = col * (1 - f) + FONDO_BAJO * f
        img[idx] = col

    img = np.clip(img, 0, 1).reshape(Hh, W, 3)
    img = img ** (1 / 2.2)
    if ss > 1:
        img = img.reshape(Hh // ss, ss, W // ss, ss, 3).mean(axis=(1, 3))
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escena", choices=list(E.ESCENAS))
    ap.add_argument("--vista", default="tres-cuartos", choices=list(VISTAS))
    ap.add_argument("--w", type=int, default=900)
    ap.add_argument("--alto", type=float, default=1.30)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--fov", type=float, default=None,
                    help="anula el de la vista; la escena del duo es "
                         "mas ancha y pide encuadre apaisado")
    a = ap.parse_args()
    print(f"render {a.escena} · {a.vista} · {a.w}x{int(a.w*a.alto)} · ss{a.ss}")
    img = render(a.escena, a.vista, a.w, a.alto, a.ss, a.fov)
    from PIL import Image
    ruta = f"render-{a.escena}-{a.vista}.png"
    Image.fromarray(img).save(ruta)
    print(f"    {ruta}  {img.shape[1]}x{img.shape[0]}")


if __name__ == "__main__":
    main()
