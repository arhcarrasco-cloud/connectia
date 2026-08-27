#!/usr/bin/env python3
"""Montaje de arte sobre fotografia real — congelador Herdez x Nestle Helados.

Deforma un arte plano a la perspectiva de una cara del equipo dentro de una foto
real y lo integra conservando la iluminacion del soporte. La foto base NUNCA se
regenera: solo se reemplaza la superficie indicada por las cuatro esquinas.

    python3 tools/montaje.py foto.jpg arte.png salida.png \
        --quad 412,318 980,296 988,742 404,760

Las esquinas van en orden superior-izq, superior-der, inferior-der, inferior-izq,
en pixeles de la foto base. `--luz` conserva las sombras y brillos del soporte
original modulando el arte con la luminancia de la foto.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
from PIL import Image


def perspective_coeffs(dst_quad, src_quad):
    """Coeficientes para Image.transform(PERSPECTIVE).

    PIL mapea destino -> origen, asi que el sistema se resuelve en ese sentido.
    """
    matrix = []
    for (dx, dy), (sx, sy) in zip(dst_quad, src_quad):
        matrix.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        matrix.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
    a = np.array(matrix, dtype=np.float64)
    b = np.array(src_quad, dtype=np.float64).reshape(8)
    return np.linalg.solve(a, b)


def warp_onto(base: Image.Image, art: Image.Image, quad, luz: float = 0.0) -> Image.Image:
    """Coloca `art` dentro del cuadrilatero `quad` de `base`."""
    base = base.convert("RGBA")
    art = art.convert("RGBA")
    w, h = base.size

    src = [(0, 0), (art.width, 0), (art.width, art.height), (0, art.height)]
    coeffs = perspective_coeffs(quad, src)
    warped = art.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BICUBIC)

    if luz > 0:
        # Modula el arte con la luminancia del soporte para heredar sombras y
        # brillos reales en vez de quedar como una calca plana.
        lum = np.asarray(base.convert("L"), dtype=np.float32) / 255.0
        gain = (1.0 - luz) + luz * (lum / max(lum.mean(), 1e-6))
        gain = np.clip(gain, 0.35, 1.9)[..., None]
        px = np.asarray(warped, dtype=np.float32)
        px[..., :3] = np.clip(px[..., :3] * gain, 0, 255)
        warped = Image.fromarray(px.astype(np.uint8), "RGBA")

    out = base.copy()
    out.alpha_composite(warped)
    return out


def parse_quad(text: str):
    pts = []
    for chunk in text.replace(";", " ").split():
        x, _, y = chunk.partition(",")
        pts.append((float(x), float(y)))
    if len(pts) != 4:
        raise argparse.ArgumentTypeError("--quad necesita exactamente 4 puntos x,y")
    return pts


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("foto", help="Fotografia base del equipo real")
    ap.add_argument("arte", help="PNG del arte plano a montar")
    ap.add_argument("salida", help="Archivo de salida")
    ap.add_argument("--quad", required=True, type=parse_quad,
                    help="4 esquinas de la cara: sup-izq sup-der inf-der inf-izq")
    ap.add_argument("--luz", type=float, default=0.55,
                    help="Cuanta iluminacion del soporte hereda el arte, 0 a 1 (default 0.55)")
    args = ap.parse_args(argv)

    base = Image.open(args.foto)
    art = Image.open(args.arte)
    out = warp_onto(base, art, args.quad, args.luz)
    out.convert("RGB").save(args.salida, quality=95)
    print(f"{args.salida} · {out.width}x{out.height}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
