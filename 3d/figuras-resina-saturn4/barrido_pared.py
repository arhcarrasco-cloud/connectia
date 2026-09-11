"""
Cuanta resina cuesta cada decima de milimetro de pared.

    python3 barrido_pared.py duo

Reutiliza el campo solido que dejo generar.py, asi que se ahorra lo caro:
evaluar el campo. Cada fila si vuelve a ahuecar, lo que incluye la apertura
morfologica de la cavidad -- dos EDT sobre la rejilla completa --, asi que
tres espesores tardan unos minutos, no segundos.

Es la sensibilidad que decide si conviene apretar la pared o no.

El volumen de cada fila es MEDIDO sobre la geometria. El precio que lo
acompania hereda los supuestos de taller de costear.py.
"""

import argparse

import numpy as np

import costear as C
import escenas as E
import generar as G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escena", choices=list(E.ESCENAS))
    ap.add_argument("--resina", default="ABS-Like", choices=list(C.RESINAS))
    ap.add_argument("--paredes", default="1.6,2.2,2.8")
    a = ap.parse_args()

    d = np.load(f"{a.escena}-campo.npz")
    solido = d["solido"].astype(np.float32)
    res = float(d["res"])
    ejes = (d["xs"], d["ys"], d["zs"])
    esc = E.ESCENAS[a.escena]
    vox = res ** 3
    v_mac = float((solido < 0).sum()) * vox / 1000.0
    alto = float(d["zs"][-1]) - float(d["zs"][0])

    print(f"{str(d['slug'])}  ·  macizo {v_mac:.1f} cm3  ·  resina {a.resina}")
    print(f"{'pared':>7}{'resina':>10}{'vs macizo':>11}{'bolsas':>8}"
          f"{'$ resina':>11}{'COGS':>10}")
    campo_hueco = d["campo"].astype(np.float32)
    for p in [float(x) for x in a.paredes.split(",")]:
        sh = G.ahuecar(solido, ejes, esc["canales"], esc["respiraderos"], p)
        sh, nb, vb = G.rellenar_bolsas(sh, res)
        ml = float((sh < 0).sum()) * vox / 1000.0
        ml_tot = ml * (1 + C.SOPORTE_PCT)
        b = C.horas(alto, a.resina, 0.0)
        h = 0.5 * (b["rapido"] + b["lento"])
        cg = C.cogs(ml_tot, h, a.resina)
        print(f"{p:>7.1f}{ml:>9.1f} ml{ml/v_mac:>10.0%}{nb:>8}"
              f"{cg['material']:>10.2f}{cg['total']:>10.2f}")
    print("\n  El tiempo NO cambia con la pared: en MSLA la capa se expone")
    print("  completa, asi que la pared mueve resina y peso, nunca horas.")


if __name__ == "__main__":
    main()
