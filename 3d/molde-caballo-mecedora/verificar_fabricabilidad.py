"""
Compuertas de fabricabilidad del molde. Nada aqui es una opinion: cada numero
sale de medir el campo o la malla.

    python3 verificar_fabricabilidad.py

G1  sin socavados          la cavidad debe ser un molde abierto en Z+
G2  angulo de salida       3 grados medidos sobre la pared
G3  pared minima de molde  plastico entre dos zonas de cavidad
G4  grosor minimo de pieza el chocolate mas delgado que sale del molde
G5  fondo solido           material bajo el punto mas profundo
G6  malla                  cerrada, orientada y de una sola pieza
"""

import os

import numpy as np
from scipy import ndimage
from skimage.morphology import skeletonize

import molde_sdf as M

OUT = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(OUT, "molde-caballo-mecedora-120x90x15.stl")

MIN_WALL = 1.0      # mm de plastico entre cavidades (2.5 x boquilla de 0.4)
MIN_PART = 3.0      # mm de chocolate: por debajo se rompe al desmoldar

ok = True


def gate(name, passed, detail):
    global ok
    ok = ok and passed
    print(f"  [{'PASA' if passed else 'FALLA'}] {name:<26} {detail}")


def main():
    print("Compuertas de fabricabilidad\n")

    res = 0.10
    xs = np.arange(-M.PLATE_W / 2, M.PLATE_W / 2, res)
    ys = np.arange(-M.PLATE_H / 2, M.PLATE_H / 2, res)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    d2, zf, _ = M.fields_2d(X, Y)
    inside = d2 <= 0
    depth = M.PLATE_T - zf

    # --- G1 sin socavados ---------------------------------------------------
    zs = np.arange(0.05, M.PLATE_T, 0.10)
    vol = M.solid_sdf(X[::3, ::3], Y[::3, ::3], zs)
    void = vol > 0                                    # hueco dentro de la placa
    # el hueco de cada columna tiene que ser un intervalo que llega hasta arriba
    cum = np.cumprod(void[:, :, ::-1], axis=2)[:, :, ::-1].astype(bool)
    bad = int((void & ~cum).sum())
    gate("G1 sin socavados", bad == 0,
         f"{bad} celdas de hueco con material encima "
         f"(de {int(void.sum()):,})")

    # --- G2 angulo de salida ------------------------------------------------
    # El campo de la cavidad solo depende de (x,y) a traves de d2, asi que el
    # contorno a la altura z es exactamente la curva d2 = -c(z). Se busca c(z)
    # por biseccion sobre el campo real, sin suponer nada.
    def cav_at(c, z):
        cc = np.atleast_1d(np.asarray(c, float))
        zz = np.full_like(cc, float(z))
        t = np.clip(cc / M.DOME_R, 0.0, 1.0)
        dome = M.DOME_MAX * np.sqrt(np.maximum(0.0, 1.0 - (1.0 - t) ** 2))
        zfl = M.PLATE_T - np.minimum(dome, M.CAV_DEPTH)
        wall = -cc + M.TAN_DRAFT * (M.PLATE_T - zz)
        cav = M.op_intersect_round(wall, zfl - zz, M.FILLET_R)
        return np.maximum(cav, zz - (M.PLATE_T + M.CAV_TOP_EXT))

    def inset(z):
        lo, hi = 0.0, 8.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if cav_at(mid, z)[0] < 0.0:
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)

    za, zb = 14.9, 12.9
    ca, cb = inset(za), inset(zb)
    ang = np.degrees(np.arctan((cb - ca) / (za - zb)))
    retiro = inset(M.PLATE_T - M.DOME_MAX + 0.05)
    gate("G2 angulo de salida", abs(ang - M.DRAFT_DEG) < 0.15,
         f"{ang:.2f} grados medidos en la pared entre Z={zb} y Z={za} "
         f"(nominal {M.DRAFT_DEG:.1f})")
    print(f"         retiro total del contorno al fondo: {retiro:.2f} mm "
          f"= pared de {M.DRAFT_DEG:.0f} grados + radio interior de {M.FILLET_R:.0f} mm")

    # --- G3 pared minima de molde -------------------------------------------
    outside = ~inside
    dist_out = ndimage.distance_transform_edt(outside, sampling=res)
    sk = skeletonize(outside)
    margen = (np.abs(X) < M.PLATE_W / 2 - 11.5) & (np.abs(Y) < M.PLATE_H / 2 - 11.5)
    w = 2 * dist_out[sk & margen]
    gate("G3 pared minima", w.min() >= MIN_WALL,
         f"{w.min():.2f} mm  (p5 {np.percentile(w,5):.2f} · minimo exigido "
         f"{MIN_WALL:.1f})")

    # --- G4 grosor minimo de la pieza ---------------------------------------
    dist_in = ndimage.distance_transform_edt(inside, sampling=res)
    t = 2 * dist_in[skeletonize(inside)]
    gate("G4 grosor de la pieza", t.min() >= MIN_PART,
         f"{t.min():.2f} mm  (p5 {np.percentile(t,5):.2f} · minimo exigido "
         f"{MIN_PART:.1f})")

    # --- G5 fondo solido ----------------------------------------------------
    gate("G5 fondo solido", abs(zf.min() - M.FLOOR) < 0.02,
         f"{zf.min():.3f} mm bajo el punto mas profundo "
         f"(profundidad max {depth[inside].max():.3f} mm)")

    # --- G6 malla -----------------------------------------------------------
    vol_mesh = None
    if os.path.exists(STL):
        import trimesh

        m = trimesh.load(STL, force="mesh")
        vol_mesh = m.volume / 1000.0
        good = (m.is_watertight and m.is_winding_consistent
                and m.body_count == 1 and m.euler_number == 2 and m.volume > 0)
        gate("G6 malla", good,
             f"cerrada={m.is_watertight} cuerpos={m.body_count} "
             f"euler={m.euler_number} vol={m.volume/1000:.2f} cm3")
    else:
        gate("G6 malla", False, "falta el STL; corre generar_molde.py")

    # --- datos de proceso ---------------------------------------------------
    print("\nDatos de proceso")
    solid = (M.PLATE_W * M.PLATE_H * M.PLATE_T
             - (4 - np.pi) * M.CORNER_R ** 2 * M.PLATE_T) / 1000.0
    print(f"  area de cavidad            {inside.sum()*res*res:6.1f} mm2")
    if vol_mesh is not None:
        cav = solid - vol_mesh
        print(f"  volumen de cavidad         {cav:6.2f} cm3   "
              f"~{cav*1.29:.0f} g de chocolate por colada  (medido sobre la malla)")
        print(f"  volumen de material        {vol_mesh:6.2f} cm3   "
              f"(placa maciza sin cavidad {solid:.2f} cm3)")
    print("  gasto de filamento y tiempo: ESTIMADO, no medido — aqui no hay slicer")

    print("\n" + ("TODAS LAS COMPUERTAS PASAN" if ok else "HAY COMPUERTAS EN FALLO"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
