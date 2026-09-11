"""
Version ligera del STL, la que se versiona en el repo.

    python3 aligerar.py duo-175x93x191.stl --caras 200000

La malla que sale de generar.py trae 600 000 triangulos y pesa 30 MB. Para
enseniar la pieza, cotizarla o abrirla en el slicer sobra con 200 000, que
pesa 10 MB y conserva la silueta y todas las cotas.

Para IMPRIMIR de verdad conviene la malla sin diezmar:

    python3 generar.py duo --res 0.25 --caras 0

Como todo lo que exporta este proyecto, se verifica releyendo el archivo.
"""

import argparse

import numpy as np
import trimesh

import generar as G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stl")
    ap.add_argument("--caras", type=int, default=200000)
    a = ap.parse_args()

    m = trimesh.load(a.stl, process=True)
    print(f"{a.stl}: {len(m.faces):,} tri · {m.volume/1000:.2f} cm3")

    import fast_simplification
    v, f = fast_simplification.simplify(
        np.asarray(m.vertices, dtype=np.float32),
        np.asarray(m.faces, dtype=np.int32),
        1.0 - a.caras / len(m.faces))
    lig = G._limpiar(trimesh.Trimesh(vertices=np.asarray(v, dtype=np.float64),
                                     faces=np.asarray(f), process=True))
    if lig.volume < 0:
        lig.invert()

    ruta = a.stl.replace(".stl", "-ligero.stl")
    r = G.exportar_y_verificar(lig, ruta)
    dv = abs(r.volume - m.volume) / abs(m.volume)
    db = np.abs(r.bounds - m.bounds).max()
    print(f"    contra la malla completa: volumen {dv:+.3%} · "
          f"caja {db:+.3f} mm · cerrada {r.is_watertight}")


if __name__ == "__main__":
    main()
