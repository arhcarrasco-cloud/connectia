"""
Costeo y precio del molde con el modelo de Market Pulse MX.

Los gramos y las horas salen de simular el rebanado sobre la geometria real
(perimetros, cascaras solidas y relleno disperso capa por capa), no de un
numero inventado. Aun asi son ESTIMADO: no hay slicer aqui. En cuanto Bambu
Studio de los numeros de verdad:

    python3 costeo.py --gramos 71.4 --horas 7.9   # pasa a MEDIDO

Modelo MPMX:
    COGS     = (g*costo_mat + h*costo_maq + h*0.24) * 1.08 + 15 + 20
    IVA neto = (PV - (material + maquina + empaque)) * 16/116
    Utilidad = (PV - COGS - IVA neto - comision - envio absorbido) * 0.97
    $/hora   = Utilidad / horas
"""

import argparse

import numpy as np
from scipy import ndimage

import molde_sdf as M

# --- parametros de proceso (los del README) ---------------------------------
LAYER_H = 0.16
LINE_W = 0.42
WALLS = 4
TOP_LAYERS = 6
BOTTOM_LAYERS = 4
INFILL = 0.25

DENS = {"PLA+": 1.24, "PETG": 1.27}       # g/cm3
COSTO_MAT = {"PLA+": 0.35, "PETG": 0.42}  # $/g
COSTO_MAQ = {"P1S": 2.54, "A1": 1.59}     # $/h

# El tiempo NO se estima con un solo numero de flujo: se calcula la longitud de
# trayectoria por tipo de linea y se corre contra dos juegos de velocidad. La
# diferencia entre los dos es la banda de incertidumbre real, y es grande.
# mm/s efectivos ya descontada la aceleracion, mas un factor de viajes.
VEL = {
    "P1S": {"lento":  dict(ext=70, int=100, solido=120, disperso=140, over=1.25),
            "rapido": dict(ext=120, int=200, solido=220, disperso=260, over=1.10)},
    "A1":  {"lento":  dict(ext=55, int=80, solido=95, disperso=110, over=1.28),
            "rapido": dict(ext=95, int=150, solido=165, disperso=190, over=1.12)},
}

MERMA = 1.08
EMPAQUE = 15.0
MANO_OBRA = 20.0
ENVIO_COSTO = 95.0
ENVIO_COBRADO = 79.0
UMBRAL_ENVIO_GRATIS = 499.0

COMISION = {
    "Shopify / Pinterest / directa": (0.0, 0.0),
    "TikTok Shop": (0.09, 0.0),
    "Walmart": (0.13, 0.0),
    "Amazon": (0.15, 0.0),
    "Mercado Libre": (0.165, 25.0),   # el fijo solo aplica si PV < 299
}


# ----------------------------------------------------------------------------
def rebanado_estimado(res=0.25):
    """Simula el rebanado sobre el campo y devuelve mm3 de filamento."""
    xs = np.arange(-M.PLATE_W / 2 - 1, M.PLATE_W / 2 + 1, res)
    ys = np.arange(-M.PLATE_H / 2 - 1, M.PLATE_H / 2 + 1, res)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    d2, zfloor, plate2d = M.fields_2d(X, Y)

    zs = np.arange(LAYER_H / 2, M.PLATE_T, LAYER_H)
    sol = M.solid_sdf(X, Y, zs, d2, zfloor, plate2d) < 0    # (nx, ny, nz)
    nz = len(zs)

    # distancia al borde de cada capa: define la banda de perimetros
    banda = WALLS * LINE_W
    perim = np.zeros(nz)
    solido = np.zeros(nz)
    disperso = np.zeros(nz)

    # una celda es cascara solida si le faltan menos de N capas para tocar hueco
    arriba = np.zeros_like(sol)
    abajo = np.zeros_like(sol)
    for k in range(1, TOP_LAYERS + 1):
        sh = np.zeros_like(sol)
        sh[:, :, :nz - k] = ~sol[:, :, k:]
        sh[:, :, nz - k:] = True                 # sobre la ultima capa hay aire
        arriba |= sh
    for k in range(1, BOTTOM_LAYERS + 1):
        sh = np.zeros_like(sol)
        sh[:, :, k:] = ~sol[:, :, :nz - k]
        sh[:, :, :k] = True                      # bajo la primera capa hay cama
        abajo |= sh
    cascara = arriba | abajo

    celda = res * res
    contorno = np.zeros(nz)      # longitud del perimetro exterior de cada capa
    for j in range(nz):
        capa = sol[:, :, j]
        if not capa.any():
            continue
        dist = ndimage.distance_transform_edt(capa, sampling=res)
        es_perim = capa & (dist <= banda)
        resto = capa & ~es_perim
        perim[j] = es_perim.sum() * celda
        cs = resto & cascara[:, :, j]
        solido[j] = cs.sum() * celda
        disperso[j] = (resto & ~cascara[:, :, j]).sum() * celda
        # el borde de la capa: celdas de material con al menos un vecino hueco
        borde = capa & ~ndimage.binary_erosion(capa)
        contorno[j] = borde.sum() * res * (np.pi / 4)   # correccion de pixelado

    v_perim = perim.sum() * LAYER_H
    v_solido = solido.sum() * LAYER_H
    v_disperso = disperso.sum() * LAYER_H * INFILL
    return dict(perimetros=v_perim, cascaras=v_solido,
                relleno=v_disperso, total=v_perim + v_solido + v_disperso,
                capas=nz, contorno=contorno.sum())


def horas_estimadas(v, maquina):
    """Banda de tiempo a partir de la longitud de trayectoria por tipo de linea."""
    seccion = LINE_W * LAYER_H            # mm2 de una linea extruida
    l_ext = v["contorno"]                 # solo el perimetro exterior
    l_per = v["perimetros"] / seccion
    l_int = max(l_per - l_ext, 0.0)
    l_sol = v["cascaras"] / seccion
    l_dis = v["relleno"] / seccion

    out = {}
    for nombre, s in VEL[maquina].items():
        t = (l_ext / s["ext"] + l_int / s["int"]
             + l_sol / s["solido"] + l_dis / s["disperso"]) * s["over"]
        out[nombre] = t / 3600.0
    out["longitudes_m"] = dict(exterior=l_ext / 1000, interior=l_int / 1000,
                               solido=l_sol / 1000, disperso=l_dis / 1000)
    return out


def cogs(g, h, material, maquina):
    mat = g * COSTO_MAT[material]
    maq = h * COSTO_MAQ[maquina]
    luz = h * 0.24
    return (mat + maq + luz) * MERMA + EMPAQUE + MANO_OBRA, mat, maq


def utilidad(pv, g, h, material, maquina, canal):
    c, mat, maq = cogs(g, h, material, maquina)
    iva = (pv - (mat + maq + EMPAQUE)) * 16 / 116
    pct, fijo = COMISION[canal]
    com = pv * pct + (fijo if (fijo and pv < 299) else 0.0)
    envio = ENVIO_COSTO if pv >= UMBRAL_ENVIO_GRATIS else (ENVIO_COSTO - ENVIO_COBRADO)
    u = (pv - c - iva - com - envio) * 0.97
    return u, c, iva, com, envio


def pv_para_objetivo(g, h, material, maquina, canal, objetivo_hora):
    """PV que deja el KPI en objetivo $/hora. Biseccion, el envio da un salto."""
    lo, hi = 50.0, 20000.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if utilidad(mid, g, h, material, maquina, canal)[0] / h < objetivo_hora:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gramos", type=float, default=None,
                    help="gramos MEDIDOS por Bambu Studio")
    ap.add_argument("--horas", type=float, default=None,
                    help="horas MEDIDAS por Bambu Studio")
    ap.add_argument("--material", default="PLA+", choices=list(COSTO_MAT))
    ap.add_argument("--maquina", default="P1S", choices=list(COSTO_MAQ))
    ap.add_argument("--chocolate-kg", type=float, default=None,
                    help="tu precio de compra de cobertura, $/kg, para la "
                         "economia del chocolate")
    a = ap.parse_args()

    medido = a.gramos is not None and a.horas is not None
    etiqueta = "MEDIDO" if medido else "ESTIMADO"

    banda = None
    if medido:
        g, h = a.gramos, a.horas
        desglose = None
    else:
        desglose = rebanado_estimado()
        vol = desglose["total"]
        g = vol / 1000.0 * DENS[a.material]
        banda = horas_estimadas(desglose, a.maquina)
        h = 0.5 * (banda["lento"] + banda["rapido"])

    print(f"MOLDE CABALLO MECEDORA 120x90x15 · {a.material} · {a.maquina}\n")
    print(f"Consumo  [{etiqueta}]")
    if desglose:
        v = desglose
        print(f"  capas de {LAYER_H} mm                {v['capas']}")
        print(f"  perimetros ({WALLS} x {LINE_W} mm)      "
              f"{v['perimetros']/1000:7.2f} cm3")
        print(f"  cascaras solidas ({TOP_LAYERS}/{BOTTOM_LAYERS})     "
              f"{v['cascaras']/1000:7.2f} cm3")
        print(f"  relleno disperso al {INFILL:.0%}        "
              f"{v['relleno']/1000:7.2f} cm3")
        print(f"  {'-'*44}")
        print(f"  filamento                    {v['total']/1000:7.2f} cm3")
    print(f"  masa                         {g:7.1f} g")
    if banda:
        L = banda["longitudes_m"]
        print(f"  trayectoria                  "
              f"{sum(L.values()):7.0f} m  (ext {L['exterior']:.0f} · "
              f"int {L['interior']:.0f} · sol {L['solido']:.0f} · "
              f"disp {L['disperso']:.0f})")
        print(f"  tiempo de maquina            {h:7.2f} h   "
              f"banda {banda['lento']:.2f} – {banda['rapido']:.2f} h")
    else:
        print(f"  tiempo de maquina            {h:7.2f} h")
    print(f"  gramaje                      {g:7.1f} g "
          f"-> minimo {g/150*1000:,.0f} de PV por la regla de 150 g/$1000")

    c, mat, maq = cogs(g, h, a.material, a.maquina)
    print(f"\nCOGS  [{etiqueta}]")
    print(f"  material                     ${mat:7.2f}")
    print(f"  maquina                      ${maq:7.2f}")
    print(f"  luz                          ${h*0.24:7.2f}")
    print(f"  merma 8%                     ${(mat+maq+h*0.24)*0.08:7.2f}")
    print(f"  empaque                      ${EMPAQUE:7.2f}")
    print(f"  mano de obra                 ${MANO_OBRA:7.2f}")
    print(f"  {'-'*44}")
    print(f"  COGS                         ${c:7.2f}")

    print(f"\nPrecio por canal  [{etiqueta}]  — KPI sano $48–$77/hora")
    print(f"  {'canal':<32}{'PV min $48/h':>14}{'PV $77/h':>12}")
    for canal in COMISION:
        p48 = pv_para_objetivo(g, h, a.material, a.maquina, canal, 48.0)
        p77 = pv_para_objetivo(g, h, a.material, a.maquina, canal, 77.0)
        print(f"  {canal:<32}{p48:>14,.0f}{p77:>12,.0f}")

    if banda:
        print(f"\nSensibilidad del KPI al tiempo (PV $699 directo)")
        for nombre in ("lento", "rapido"):
            hb = banda[nombre]
            u = utilidad(699, g, hb, a.material, a.maquina,
                         "Shopify / Pinterest / directa")[0]
            print(f"  {nombre:<10} {hb:5.2f} h  ->  ${u/hb:6.2f}/hora")

    print(f"\nEscenarios de precio  [{etiqueta}]")
    print(f"  {'PV':>7}{'canal':<34}{'COGS':>8}{'IVA':>8}{'com':>8}"
          f"{'envio':>8}{'utilidad':>10}{'margen':>8}{'$/hora':>9}")
    for pv in (399, 499, 699, 899, 1199):
        for canal in ("Shopify / Pinterest / directa", "Mercado Libre"):
            u, cc, iva, com, env = utilidad(pv, g, h, a.material, a.maquina, canal)
            print(f"  {pv:>7}{canal:<34}{cc:>8.0f}{iva:>8.0f}{com:>8.0f}"
                  f"{env:>8.0f}{u:>10.0f}{u/pv:>8.1%}{u/h:>9.2f}")

    # --- veredicto -----------------------------------------------------------
    piso_gramaje = g / 150 * 1000
    piso_kpi = pv_para_objetivo(g, h, a.material, a.maquina,
                                "Shopify / Pinterest / directa", 48.0)
    print("\nVeredicto")
    print(f"  piso por gramaje (150 g/$1000)      ${piso_gramaje:,.0f}")
    print(f"  piso por KPI ($48/hora, directo)    ${piso_kpi:,.0f}")
    print(f"  manda el mayor                      ${max(piso_gramaje, piso_kpi):,.0f}")
    if piso_gramaje > piso_kpi * 1.2:
        print("  -> aqui gramaje y $/hora NO apuntan al mismo precio: la pieza")
        print("     es pesada y rapida (placa maciza), asi que el atajo de")
        print("     150 g/$1000 pide mas del doble que el KPI. Manda gramaje.")
    print("  catalogo MPMX: contacto con alimento GRASO y LIQUIDO.")
    print("     La regla de catalogo es 'alimento solo polvo seco' -> NO pasa")
    print("     como SKU de MPMX. Vive como maestro de silicona, venta B2B")
    print("     a chocolateria, o vendiendo el chocolate en vez del molde.")
    print("  bloque B3 (marketplaces): SIN DATO. Mercado Libre esta bloqueado")
    print("     por egress en este entorno; hay que correr el RADAR desde tu")
    print("     Chrome. Sin ventas verificadas no hay banda de mercado.")

    if a.chocolate_kg:
        gr = 37.0
        costo = gr / 1000 * a.chocolate_kg
        print(f"\nEconomia del chocolate ({gr:.0f} g por colada, "
              f"cobertura a ${a.chocolate_kg:,.0f}/kg)")
        print(f"  materia prima por pieza             ${costo:,.2f}")
        print(f"  {'PV pieza':>10}{'margen bruto':>16}{'piezas/kg':>12}")
        for pv in (35, 45, 59, 79):
            print(f"  {pv:>10}{(pv-costo)/pv:>15.0%}{1000/gr:>12.0f}")

    if not medido:
        print("\n⚠  Todo lo de arriba es ESTIMADO. No lo mandes a un cliente")
        print("   como cotizacion: rebana en Bambu Studio y vuelve a correr")
        print("   esto con --gramos y --horas.")


if __name__ == "__main__":
    main()
