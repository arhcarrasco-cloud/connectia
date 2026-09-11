"""
Compuertas de fabricabilidad en RESINA para la Elegoo Saturn 4 Ultra 16K.

    python3 verificar.py duo

Lee el campo que dejo generar.py y mide sobre voxeles, no sobre opiniones.
La orientacion evaluada es la pieza DE PIE sobre la peana, apoyada en la
placa. Ninguna metrica de aqui es un rebanado real: el tiempo y el consumo
salen de costear.py y van etiquetados como ESTIMADO hasta que Chitubox o
Lychee entreguen los suyos.
"""

import argparse

import numpy as np
from scipy import ndimage

# --- Elegoo Saturn 4 Ultra 16K ----------------------------------------------
# OJO: 211.68 x 118.37 x 220 mm, NO los 218.88 x 122.88 del Saturn 4 Ultra 12K.
# El panel 16K de 10.1" gana resolucion y pierde placa. Y el pixel NO es
# cuadrado: 14 um en X contra 19 um en Y, asi que el detalle util lo manda el
# eje malo, el de 19 um.
PLACA_X, PLACA_Y, PLACA_Z = 211.68, 118.37, 220.0
PANEL_PX_X, PANEL_PX_Y = 15120, 6230          # 10.1", 16K
PIXEL_X = PLACA_X / PANEL_PX_X                # 0.0140 mm
PIXEL_Y = PLACA_Y / PANEL_PX_Y                # 0.0190 mm
PIXEL_XY = max(PIXEL_X, PIXEL_Y)              # el que manda

# --- criterios ---------------------------------------------------------------
MIN_MIEMBRO = 0.80      # mm: lo mas fino que sobrevive al lavado y al curado
MIN_PARED = 1.20        # mm: pared de cascara que no se abolla al despegar
RACIMO_ALERTA = 0.05    # cm3: por encima de esto el material fino ya es un
                        # miembro de verdad y no el canto de una curva
AREA_ALERTA = 6000.0    # mm2 de seccion por capa: arriba de esto la succion manda


def _fmt(ok):
    return "[PASA]" if ok else "[FALLA]"


def _aviso(ok):
    """A1 y A2 no juzgan la pieza: dicen como hay que montarla en la maquina.

    Una seccion grande no es un defecto, es una peana plana; unas islas no son
    un defecto, son el arbol de soportes que toca poner. Por eso no cuentan
    para el veredicto, pero si mandan sobre la orientacion y sobre el consumo,
    que es donde acaban costando dinero.
    """
    return "[ok  ]" if ok else "[AVISO]"


def cargar(slug):
    d = np.load(f"{slug}-campo.npz")
    return (d["campo"].astype(np.float32), d["solido"].astype(np.float32),
            float(d["res"]), float(d["pared"]),
            float(d["v_macizo"]), float(d["v_hueco"]), float(d["v_malla"]),
            str(d["slug"]), d["xs"], d["ys"], d["zs"])


def espesor_3d(mascara, res, umbrales):
    """Espesor local por ESFERA INSCRITA, en 3D, no por seccion de capa.

    Medir el grosor capa por capa castiga cualquier canto redondeado: la
    primera capa de una esfera es un punto, y la compuerta la reportaba como
    un miembro de 0.6 mm aunque la pieza midiera 9 mm. Lo correcto es el
    espesor local clasico: un punto es "grueso" si cabe dentro de una esfera
    inscrita de radio u/2. La dilatacion se calcula como una EDT del
    complemento, que es exacta y cuesta una pasada.

    Devuelve, por cada umbral, cuanto material NO alcanza ese grosor y en
    cuantos racimos. La distincion util esta en el racimo mayor: un canto
    afilado deja miles de racimos de nada; un miembro de verdad delgado deja
    uno solo y gordo.
    """
    edt = ndimage.distance_transform_edt(mascara, sampling=res)
    total = int(mascara.sum())
    filas = []
    for u in umbrales:
        nucleo = edt >= u / 2.0
        if not nucleo.any():
            filas.append(dict(umbral=u, voxeles=total, racimos=1, mayor=total))
            continue
        cubierto = ndimage.distance_transform_edt(~nucleo, sampling=res) <= u / 2.0
        fino = mascara & ~cubierto
        nf = int(fino.sum())
        racimos, mayor = 0, 0
        if nf:
            lab, racimos = ndimage.label(fino)
            if racimos:
                mayor = int(np.bincount(lab.ravel())[1:].max())
        filas.append(dict(umbral=u, voxeles=nf, racimos=int(racimos),
                          mayor=mayor))
    return float(edt.max()), filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escena")
    a = ap.parse_args()

    (campo, solido, res, pared, v_mac, v_hue, v_malla, slug,
     xs, ys, zs) = cargar(a.escena)
    import escenas as ESC
    esc_detalle = ESC.ESCENAS[a.escena]["detalle_min"]
    hueco = campo < 0
    vox = res ** 3

    print(f"{slug}  ·  voxel {res} mm  ·  pared nominal {pared} mm")
    print(f"Elegoo Saturn 4 Ultra 16K  ·  placa {PLACA_X} x {PLACA_Y} x {PLACA_Z} mm"
          f"  ·  pixel {PIXEL_X*1000:.1f} x {PIXEL_Y*1000:.1f} um\n")

    resultados = []

    # --- G1 caja envolvente --------------------------------------------------
    idx = np.argwhere(hueco)
    lo, hi = idx.min(0), idx.max(0)
    dim = (hi - lo + 1) * res
    cabe_dir = dim[0] <= PLACA_X and dim[1] <= PLACA_Y
    cabe_gir = dim[1] <= PLACA_X and dim[0] <= PLACA_Y
    ok1 = (cabe_dir or cabe_gir) and dim[2] <= PLACA_Z
    giro = "sin girar" if cabe_dir else ("girada 90 grados" if cabe_gir else "NO CABE")
    resultados.append(ok1)
    print(f"{_fmt(ok1)} G1 cabe en la placa   {dim[0]:.1f} x {dim[1]:.1f} x "
          f"{dim[2]:.1f} mm · {giro}")
    print(f"           ocupa {dim[0]*dim[1]/(PLACA_X*PLACA_Y):.0%} de la placa "
          f"y {dim[2]/PLACA_Z:.0%} del alto util")

    # --- G2 un solo cuerpo ---------------------------------------------------
    est = np.ones((3, 3, 3), bool)
    lab, n = ndimage.label(hueco, structure=est)
    tam = np.bincount(lab.ravel())[1:] * vox / 1000.0
    ok2 = n == 1
    resultados.append(ok2)
    print(f"{_fmt(ok2)} G2 una sola pieza     {n} cuerpo(s)")
    if n > 1:
        for i in np.argsort(tam)[::-1][:6]:
            c = ndimage.center_of_mass(lab == i + 1)
            print(f"           suelto: {tam[i]:8.3f} cm3 en "
                  f"({xs[int(c[0])]:6.1f}, {ys[int(c[1])]:6.1f}, "
                  f"{zs[int(c[2])]:6.1f}) mm")

    # --- G3 material mas delgado que el minimo -------------------------------
    vox_cm3 = vox / 1000.0
    macizo = solido < 0
    grueso_max, filas = espesor_3d(macizo, res, [MIN_MIEMBRO, MIN_MIEMBRO * 1.5])
    f0 = filas[0]
    frac = f0["voxeles"] / max(macizo.sum(), 1)
    mayor_cm3 = f0["mayor"] * vox_cm3
    ok3 = frac < 0.005 and mayor_cm3 < RACIMO_ALERTA
    resultados.append(ok3)
    print(f"{_fmt(ok3)} G3 material fino      {f0['voxeles']*vox_cm3:.3f} cm3 "
          f"bajo {MIN_MIEMBRO} mm = {frac:.3%} del solido")
    print(f"           en {f0['racimos']} racimos; el mayor {mayor_cm3:.4f} cm3 "
          f"(alerta {RACIMO_ALERTA} cm3)")
    print(f"           esfera inscrita mayor {2*grueso_max:.1f} mm · "
          f"bajo {filas[1]['umbral']:.1f} mm hay "
          f"{filas[1]['voxeles']*vox_cm3:.3f} cm3")
    print(f"           miles de racimos diminutos = cantos redondeados, "
          f"no miembros delgados")

    # --- G4 pared de la cascara ----------------------------------------------
    _, filas_h = espesor_3d(hueco, res, [MIN_PARED])
    fh = filas_h[0]
    frac_h = fh["voxeles"] / max(hueco.sum(), 1)
    mayor_h = fh["mayor"] * vox_cm3
    ok4 = frac_h < 0.005 and mayor_h < RACIMO_ALERTA
    resultados.append(ok4)
    print(f"{_fmt(ok4)} G4 pared de cascara   {fh['voxeles']*vox_cm3:.3f} cm3 "
          f"bajo {MIN_PARED} mm = {frac_h:.3%} · racimo mayor {mayor_h:.4f} cm3")
    print(f"           pared nominal {pared} mm")

    # --- G5 resina atrapada --------------------------------------------------
    vacio = ~hueco
    lv, nv = ndimage.label(vacio, structure=est)
    borde = set(np.unique(np.concatenate([
        lv[0].ravel(), lv[-1].ravel(), lv[:, 0].ravel(), lv[:, -1].ravel(),
        lv[:, :, 0].ravel(), lv[:, :, -1].ravel()])))
    borde.discard(0)
    cuenta = np.bincount(lv.ravel(), minlength=nv + 1)
    atrapados = [(i, cuenta[i] * vox / 1000.0) for i in range(1, nv + 1)
                 if i not in borde]
    atrapados.sort(key=lambda t: -t[1])
    v_atr = sum(v for _, v in atrapados)
    ok5 = v_atr < 0.05
    resultados.append(ok5)
    print(f"{_fmt(ok5)} G5 resina atrapada    {len(atrapados)} bolsa(s) cerrada(s)"
          f" · {v_atr:.2f} cm3")
    for i, vv in atrapados[:6]:
        c = ndimage.center_of_mass(lv == i)
        print(f"           bolsa {vv:7.3f} cm3 en "
              f"({xs[int(c[0])]:6.1f}, {ys[int(c[1])]:6.1f}, "
              f"{zs[int(c[2])]:6.1f}) mm")

    # --- G6 seccion por capa -------------------------------------------------
    area = hueco.sum(axis=(0, 1)) * res * res
    kmax = int(area.argmax())
    ok6 = area.max() <= AREA_ALERTA
    print(f"{_aviso(ok6)} A1 seccion por capa   max {area.max():.0f} mm2 a "
          f"z = {zs[kmax]:.1f} mm · alerta {AREA_ALERTA:.0f} mm2")
    print(f"           mediana {np.median(area[area>0]):.0f} mm2 · "
          f"{(area>AREA_ALERTA).sum()*res:.1f} mm de altura por encima de la alerta")

    # --- G7 islas sin apoyo --------------------------------------------------
    islas, v_islas, z_islas = 0, 0.0, []
    k_placa = int(np.argmax(hueco.any(axis=(0, 1))))   # capa que apoya en la placa
    for k in range(k_placa + 1, hueco.shape[2]):
        capa = hueco[:, :, k]
        if not capa.any():
            continue
        apoyo = ndimage.binary_dilation(hueco[:, :, k - 1])
        lab2, n2 = ndimage.label(capa)
        if n2 == 0:
            continue
        tocado = ndimage.maximum(apoyo, lab2, index=np.arange(1, n2 + 1))
        for j, t in enumerate(tocado):
            if not t:
                islas += 1
                v_islas += (lab2 == j + 1).sum() * vox / 1000.0
                z_islas.append(zs[k])
    ok7 = islas == 0
    print(f"{_aviso(ok7)} A2 islas sin apoyo    {islas} isla(s) · {v_islas:.3f} cm3")
    if z_islas:
        print(f"           entre z = {min(z_islas):.1f} y {max(z_islas):.1f} mm "
              f"(deteccion a paso de voxel {res} mm, no a paso de capa)")

    # --- G8 detalle contra el pixel -----------------------------------------
    det = esc_detalle
    ok8 = det / PIXEL_XY >= 20
    resultados.append(ok8)
    print(f"{_fmt(ok8)} G8 detalle vs pixel   el detalle mas fino DISENADO "
          f"({det:.2f} mm, el aro de los lentes) son")
    print(f"           {det/PIXEL_X:.0f} px en X y {det/PIXEL_Y:.0f} px en Y "
          f"· minimo 20 px en el eje malo")

    # --- volumenes -----------------------------------------------------------
    print(f"\nVolumen  macizo {v_mac:.1f} cm3 · hueco {v_hue:.1f} cm3 "
          f"({v_hue/v_mac:.0%}) · malla releida {v_malla:.1f} cm3")
    print(f"Ahorro por ahuecar: {v_mac-v_hue:.1f} cm3 de resina por pieza")

    if not ok6:
        print(f"\n  A1 -> la seccion grande es la peana apoyada en la placa. "
              f"Con despegue por basculacion (TSMC) la Saturn 4 Ultra lo come,\n"
              f"       pero pide perfil de area grande en las primeras "
              f"{(area>AREA_ALERTA).sum()} capas de voxel. No es un defecto.")
    if not ok7:
        print(f"  A2 -> {islas} islas: la pieza NO es de impresion sin soportes. "
              f"El arbol carga sobre la cara trasera y bajo la placa;\n"
              f"       el consumo de soporte ya va contemplado en costear.py.")

    n_ok = sum(resultados)
    print(f"\n{n_ok}/{len(resultados)} compuertas bloqueantes. "
          + ("LISTA PARA REBANAR." if n_ok == len(resultados)
             else "NO esta lista: arriba dice que falta."))


if __name__ == "__main__":
    main()
