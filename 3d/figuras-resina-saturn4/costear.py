"""
Costo y precio de las figuras impresas en resina en una Elegoo Saturn 4 Ultra 16K.

    python3 costear.py duo
    python3 costear.py duo --ml 96 --horas 3.4     # pasa de ESTIMADO a MEDIDO
    python3 costear.py ambas                        # las dos y el comparativo

La diferencia de fondo contra el costeo de FDM: en MSLA la maquina expone una
capa COMPLETA de una sola vez, asi que el tiempo depende de la ALTURA de la
pieza y no de su volumen. Dos figuras en la misma tirada tardan lo mismo que
la mas alta de las dos -- si caben juntas en la placa. Ahi es donde se gana o
se pierde dinero, no en el gramaje.

Modelo (mismo esqueleto que el costeo MPMX de FDM, con las lineas propias de
resina):
    COGS = [(ml*costo_resina + h*costo_maq + h*luz) * merma
            + lavado + consumibles + mano_obra + empaque] / (1 - tasa_falla)
"""

import argparse

import numpy as np

# --- maquina -----------------------------------------------------------------
# Saturn 4 Ultra 16K: 211.68 x 118.37 x 220 mm. NO confundir con los
# 218.88 x 122.88 del Saturn 4 Ultra 12K -- el panel 16K de 10.1" da mas
# resolucion y menos placa, y aqui esos 4.5 mm de menos en Y deciden si dos
# piezas caben en una tirada o en dos.
PLACA_X, PLACA_Y, PLACA_Z = 211.68, 118.37, 220.0
VEL_MAX_MMH = 150.0       # tope declarado por el fabricante
MARGEN_PLACA = 5.0        # mm libres al borde que pide el fabricante

PRECIO_MAQUINA = 9500.0   # MXN, cuerpo completo
PRECIO_LCD = 2600.0       # panel 10.1" 16K de repuesto
VIDA_LCD_H = 2000.0       # horas de exposicion
PRECIO_FEP = 280.0        # pelicula nFEP
VIDA_FEP_H = 150.0
VIDA_CUERPO_H = 3600.0    # 3 anios x 1200 h
POTENCIA_KW = 0.120
PRECIO_KWH = 2.00

# --- resina ------------------------------------------------------------------
DENSIDAD = 1.10           # g/cm3
RESINAS = {               # MXN por kg, y exposicion tipica a 0.05 mm
    "Estandar 8K":   (600.0, 2.4),
    "ABS-Like":      (700.0, 2.6),
    "Lavable agua":  (650.0, 2.2),
    "Alta velocidad": (780.0, 1.1),
}

# --- proceso -----------------------------------------------------------------
CAPA = 0.05               # mm
CAPAS_BASE, EXP_BASE = 5, 28.0     # capas de arranque y su exposicion
CICLO = {"rapido": 0.7, "lento": 2.2}   # s de subida/bajada por capa (TSMC)
SOPORTE_PCT = 0.09        # volumen de soportes sobre el de la pieza
MERMA = 1.08              # resina que se queda en la cuba, escurre o se cuela
TASA_FALLA = 0.08         # 1/(1-p) intentos, no (1+p)

LAVADO = 10.30            # IPA amortizado por pieza
CONSUMIBLES = 8.00        # guantes, papel, filtros
EMPAQUE = 35.0            # caja y burbuja para una pieza de 180 mm
TARIFA_MO = 80.0          # MXN/hora de taller
MANO_OBRA_H = 0.90        # preparar, despegar, lavar, cortar soportes, curar

# --- canales (identicos al costeo MPMX de FDM) -------------------------------
COMISION = {
    "Shopify / Pinterest / directa": (0.0, 0.0),
    "TikTok Shop": (0.09, 0.0),
    "Walmart": (0.13, 0.0),
    "Amazon": (0.15, 0.0),
    "Mercado Libre": (0.165, 25.0),
}
ENVIO_COSTO, ENVIO_COBRADO, UMBRAL_ENVIO_GRATIS = 95.0, 79.0, 499.0


# =============================================================================
def costo_maquina_hora():
    cuerpo = (PRECIO_MAQUINA - PRECIO_LCD) / VIDA_CUERPO_H
    lcd = PRECIO_LCD / VIDA_LCD_H
    fep = PRECIO_FEP / VIDA_FEP_H
    return cuerpo + lcd + fep, (cuerpo, lcd, fep)


def horas(altura_mm, resina, area_max_mm2):
    """Banda de tiempo. En MSLA la manda la altura; el area solo frena el ciclo."""
    n = int(np.ceil(altura_mm / CAPA))
    exp = RESINAS[resina][1]
    # una seccion grande obliga a despegar mas despacio, aun con basculacion
    frac = area_max_mm2 / (PLACA_X * PLACA_Y)
    penal = 1.0 + 0.35 * max(frac - 0.25, 0.0) / 0.75
    out = {}
    for nombre, ciclo in CICLO.items():
        t = (n - CAPAS_BASE) * (exp + ciclo * penal) + CAPAS_BASE * (EXP_BASE + ciclo)
        out[nombre] = t / 3600.0
    out["capas"] = n
    return out


def cogs(ml, h, resina):
    costo_res = RESINAS[resina][0] * DENSIDAD / 1000.0      # MXN por ml
    maq_h, _ = costo_maquina_hora()
    material = ml * costo_res
    maquina = h * maq_h
    luz = h * POTENCIA_KW * PRECIO_KWH
    mo = MANO_OBRA_H * TARIFA_MO
    directo = (material + maquina + luz) * MERMA
    bruto = directo + LAVADO + CONSUMIBLES + mo + EMPAQUE
    total = bruto / (1.0 - TASA_FALLA)
    return dict(material=material, maquina=maquina, luz=luz,
                merma=(material + maquina + luz) * (MERMA - 1),
                lavado=LAVADO, consumibles=CONSUMIBLES, mano_obra=mo,
                empaque=EMPAQUE, reimpresion=total - bruto, total=total,
                costo_res_ml=costo_res)


def utilidad(pv, ml, h, resina, canal):
    c = cogs(ml, h, resina)
    iva = (pv - (c["material"] + c["maquina"] + EMPAQUE)) * 16 / 116
    pct, fijo = COMISION[canal]
    com = pv * pct + (fijo if (fijo and pv < 299) else 0.0)
    envio = ENVIO_COSTO if pv >= UMBRAL_ENVIO_GRATIS else (ENVIO_COSTO - ENVIO_COBRADO)
    return (pv - c["total"] - iva - com - envio) * 0.97, c["total"]


def pv_objetivo(ml, h, resina, canal, obj_hora):
    lo, hi = 50.0, 40000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if utilidad(mid, ml, h, resina, canal)[0] / h < obj_hora:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def caben_juntas(f1, f2):
    """Empaquetado de dos rectangulos en la placa, con el margen del fabricante."""
    ux, uy = PLACA_X - 2 * MARGEN_PLACA, PLACA_Y - 2 * MARGEN_PLACA
    for a in ((f1[0], f1[1]), (f1[1], f1[0])):
        for b in ((f2[0], f2[1]), (f2[1], f2[0])):
            if a[0] + b[0] <= ux and max(a[1], b[1]) <= uy:
                return True, "lado a lado en X"
            if max(a[0], b[0]) <= ux and a[1] + b[1] <= uy:
                return True, "una delante de la otra en Y"
    return False, None


def cabe_sola(f):
    ux, uy = PLACA_X - 2 * MARGEN_PLACA, PLACA_Y - 2 * MARGEN_PLACA
    return (f[0] <= ux and f[1] <= uy) or (f[1] <= ux and f[0] <= uy)


# =============================================================================
def datos(escena):
    d = np.load(f"{escena}-campo.npz")
    campo = d["campo"].astype(np.float32)
    res = float(d["res"])
    hueco = campo < 0
    idx = np.argwhere(hueco)
    lo, hi = idx.min(0), idx.max(0)
    dim = (hi - lo + 1) * res
    area = hueco.sum(axis=(0, 1)) * res * res
    return dict(slug=str(d["slug"]), ml=float(d["v_malla"]),
                ml_macizo=float(d["v_macizo"]),
                dim=dim, area_max=float(area.max()))


def informe(escena, resina, ml_medido, h_medido):
    D = datos(escena)
    ml_pieza = ml_medido if ml_medido else D["ml"]
    ml_sop = 0.0 if ml_medido else ml_pieza * SOPORTE_PCT
    ml = ml_pieza + ml_sop
    b = horas(D["dim"][2], resina, D["area_max"])
    h = h_medido if h_medido else 0.5 * (b["rapido"] + b["lento"])
    etiqueta = "MEDIDO" if (ml_medido and h_medido) else "ESTIMADO"

    print(f"\n{'='*74}\n{D['slug']}  ·  {resina}  ·  [{etiqueta}]\n{'='*74}")
    print(f"  caja envolvente        {D['dim'][0]:.1f} x {D['dim'][1]:.1f} x "
          f"{D['dim'][2]:.1f} mm")
    ux, uy = PLACA_X - 2 * MARGEN_PLACA, PLACA_Y - 2 * MARGEN_PLACA
    print(f"  huella en placa        {D['dim'][0]*D['dim'][1]/100:.0f} cm2 de "
          f"{ux*uy/100:.0f} cm2 utiles ({ux:.1f} x {uy:.1f} mm)  ·  "
          f"{'CABE' if cabe_sola(D['dim'][:2]) else 'NO CABE'}")
    print(f"  resina de la pieza     {ml_pieza:7.1f} ml  "
          f"(maciza serian {D['ml_macizo']:.0f} ml)")
    if ml_sop:
        print(f"  soportes al {SOPORTE_PCT:.0%}         {ml_sop:7.1f} ml")
    print(f"  resina total           {ml:7.1f} ml = {ml*DENSIDAD:.0f} g")
    print(f"  capas de {CAPA} mm       {b['capas']:7d}")
    v_rap, v_len = D["dim"][2] / b["rapido"], D["dim"][2] / b["lento"]
    print(f"  tiempo de maquina      {h:7.2f} h   banda "
          f"{b['rapido']:.2f} - {b['lento']:.2f} h  "
          f"({v_len:.0f} - {v_rap:.0f} mm/h, tope de fabrica {VEL_MAX_MMH:.0f})")

    c = cogs(ml, h, resina)
    maq_h, (cu, lc, fe) = costo_maquina_hora()
    print(f"\n  COGS  [{etiqueta}]")
    print(f"    resina {ml:.0f} ml a ${c['costo_res_ml']:.3f}/ml    "
          f"${c['material']:8.2f}")
    print(f"    maquina {h:.2f} h a ${maq_h:.2f}/h        ${c['maquina']:8.2f}"
          f"   (cuerpo {cu:.2f} + LCD {lc:.2f} + FEP {fe:.2f})")
    print(f"    luz                            ${c['luz']:8.2f}")
    print(f"    merma {MERMA-1:.0%}                       ${c['merma']:8.2f}")
    print(f"    lavado IPA                     ${c['lavado']:8.2f}")
    print(f"    consumibles                    ${c['consumibles']:8.2f}")
    print(f"    mano de obra {MANO_OBRA_H:.2f} h a ${TARIFA_MO:.0f}/h  "
          f"${c['mano_obra']:8.2f}")
    print(f"    empaque                        ${c['empaque']:8.2f}")
    print(f"    reimpresion {TASA_FALLA:.0%}                 "
          f"${c['reimpresion']:8.2f}")
    print(f"    {'-'*46}")
    print(f"    COGS                           ${c['total']:8.2f}")
    return D, ml, h, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escena", choices=["duo", "diploma", "ambas"])
    ap.add_argument("--resina", default="ABS-Like", choices=list(RESINAS))
    ap.add_argument("--ml", type=float, default=None, help="ml MEDIDOS por el slicer")
    ap.add_argument("--horas", type=float, default=None, help="horas MEDIDAS")
    a = ap.parse_args()

    escenas = ["duo", "diploma"] if a.escena == "ambas" else [a.escena]
    acc = []
    for e in escenas:
        acc.append((e,) + informe(e, a.resina, a.ml, a.horas))

    # --- precio ---------------------------------------------------------------
    for e, D, ml, h, c in acc:
        print(f"\n  Precio de {D['slug']}  — KPI sano $48–$77/hora de maquina")
        print(f"    {'canal':<32}{'PV $48/h':>12}{'PV $77/h':>12}")
        for canal in COMISION:
            print(f"    {canal:<32}"
                  f"{pv_objetivo(ml, h, a.resina, canal, 48.0):>12,.0f}"
                  f"{pv_objetivo(ml, h, a.resina, canal, 77.0):>12,.0f}")

    # --- las dos juntas -------------------------------------------------------
    if len(acc) == 2:
        (_, D1, ml1, h1, c1), (_, D2, ml2, h2, c2) = acc
        print(f"\n{'='*74}\nLAS DOS\n{'='*74}")
        print(f"  COGS por separado      ${c1['total']:.2f} + ${c2['total']:.2f}"
              f" = ${c1['total']+c2['total']:.2f}")
        print(f"  resina                 {ml1+ml2:.0f} ml = "
              f"{(ml1+ml2)*DENSIDAD:.0f} g")
        print(f"  tiempo en dos tiradas  {h1+h2:.2f} h")
        ok, como = caben_juntas(D1["dim"][:2], D2["dim"][:2])
        if ok:
            h_j = max(h1, h2)
            mlj = ml1 + ml2
            cj = cogs(mlj, h_j, a.resina)
            print(f"\n  Caben juntas en la placa ({como}): una sola tirada de "
                  f"{h_j:.2f} h")
            print(f"  COGS de la tirada unica       ${cj['total']:.2f}"
                  f"  -> ahorra ${c1['total']+c2['total']-cj['total']:.2f}")
        else:
            print(f"\n  NO caben juntas en la placa de "
                  f"{PLACA_X:.1f} x {PLACA_Y:.1f} mm "
                  f"(margen {MARGEN_PLACA:.0f} mm).")
            print(f"  Son dos tiradas: {h1:.2f} h + {h2:.2f} h = {h1+h2:.2f} h "
                  f"de maquina.")
            print(f"  La mano de obra ({MANO_OBRA_H:.2f} h por pieza) tampoco se "
                  f"comparte: son dos lavados y dos cortes de soporte.")

    if not (a.ml and a.horas):
        print("\n⚠  ESTIMADO. El consumo sale del volumen MEDIDO sobre la malla,")
        print("   pero el tiempo y el soporte salen de un modelo, no de un corte")
        print("   real. Rebana en Chitubox o Lychee y vuelve a correr esto con")
        print("   --ml y --horas antes de mandarselo a un cliente.")


if __name__ == "__main__":
    main()
