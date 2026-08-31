"""
Malla y STL binario de las dos piezas, por marching cubes sobre el SDF.

Para que sirve: el costeo de aqui es ESTIMADO porque no hay CuraEngine en este
entorno. Con estos STL abiertos en Bambu Studio salen los gramos y las horas
MEDIDOS, y entonces:

    python3 costeo_figuras.py --medido A <g> <h> --medido B <g> <h>

y la cotizacion deja de ser una estimacion.

    python3 exportar_stl.py [--res 0.5]

Cada archivo se verifica releyendolo: triangulos, caja envolvente y volumen
por el teorema de la divergencia. Si el STL reescrito no coincide con la malla
que salio del campo, el script lo dice en vez de callarselo.
"""

import argparse
import os
import struct

import numpy as np
from skimage import measure

import figuras_sdf as S

AQUI = os.path.dirname(os.path.abspath(__file__))


def mallar(key, res=0.5, margen=2.0):
    P = S.PIEZAS[key]
    fn = P["f"]
    W, D, H = P["w"], P["d"], P["h"]
    xs = np.arange(-W / 2 - margen, W / 2 + margen + res, res, dtype=np.float32)
    ys = np.arange(-D / 2 - margen, D / 2 + margen + res, res, dtype=np.float32)
    zs = np.arange(-margen, H + margen + res, res, dtype=np.float32)

    X, Y = np.meshgrid(xs, ys, indexing="ij")
    pts = np.empty((len(xs), len(ys), 3), np.float32)
    pts[..., 0] = X
    pts[..., 1] = Y
    campo = np.empty((len(xs), len(ys), len(zs)), np.float32)
    for k, z in enumerate(zs):
        pts[..., 2] = z
        campo[..., k] = fn(pts)

    v, f, _, _ = measure.marching_cubes(campo, level=0.0, spacing=(res, res, res))
    v += np.array([xs[0], ys[0], zs[0]], np.float32)
    return v.astype(np.float32), f.astype(np.int64)


def volumen(v, f):
    """Volumen por el teorema de la divergencia sobre los triangulos."""
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return float(np.abs((a * np.cross(b, c)).sum() / 6.0))


def escribir_stl(path, v, f):
    n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.maximum(ln, 1e-12)
    tri = np.zeros((len(f), 12), np.float32)
    tri[:, 0:3] = n
    tri[:, 3:6] = v[f[:, 0]]
    tri[:, 6:9] = v[f[:, 1]]
    tri[:, 9:12] = v[f[:, 2]]
    with open(path, "wb") as fh:
        fh.write(b"forge-connectia figurin desde foto".ljust(80, b"\0"))
        fh.write(struct.pack("<I", len(f)))
        buf = np.zeros((len(f), 50), np.uint8)
        buf[:, :48] = tri.view(np.uint8).reshape(len(f), 48)
        fh.write(buf.tobytes())


def leer_stl(path):
    with open(path, "rb") as fh:
        fh.read(80)
        n = struct.unpack("<I", fh.read(4))[0]
        raw = np.frombuffer(fh.read(n * 50), np.uint8).reshape(n, 50)
    tri = np.frombuffer(raw[:, :48].tobytes(), np.float32).reshape(n, 12)
    v = tri[:, 3:12].reshape(n * 3, 3)
    f = np.arange(n * 3).reshape(n, 3)
    return v, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=float, default=0.5,
                    help="mm de la retícula; 0.35 da mas detalle y mas peso")
    a = ap.parse_args()

    for key in ("A", "B"):
        P = S.PIEZAS[key]
        v, f = mallar(key, a.res)
        lo, hi = v.min(0), v.max(0)
        vol = volumen(v, f)
        path = os.path.join(AQUI, f"pieza-{key}.stl")
        escribir_stl(path, v, f)

        v2, f2 = leer_stl(path)
        vol2 = volumen(v2, f2)
        lo2, hi2 = v2.min(0), v2.max(0)
        dv = abs(vol2 - vol) / max(vol, 1e-9)
        dbb = float(np.abs((hi2 - lo2) - (hi - lo)).max())
        ok = len(f2) == len(f) and dv < 1e-4 and dbb < 1e-3

        print(f"PIEZA {key} — {P['nombre']}")
        print(f"  retícula                {a.res} mm")
        print(f"  triangulos              {len(f):,}")
        print(f"  caja envolvente         {hi[0]-lo[0]:.1f} x {hi[1]-lo[1]:.1f}"
              f" x {hi[2]-lo[2]:.1f} mm")
        print(f"  volumen macizo          {vol/1000:.1f} cm3")
        print(f"  archivo                 {os.path.basename(path)}  "
              f"({os.path.getsize(path)/1e6:.1f} MB)")
        print(f"  verificacion al releer  {'OK' if ok else 'NO COINCIDE'}"
              f"   (dV {dv:.2e}, dBB {dbb:.2e} mm)\n")

    print("Malla de MAQUETA, no de venta: define volumen, escala y pose.")
    print("El parecido facial lo pone el escultor encima. Sirve para rebanar")
    print("en Bambu Studio y convertir el costeo de ESTIMADO a MEDIDO.")


if __name__ == "__main__":
    main()
