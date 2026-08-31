"""
Rebanado simulado y costeo de las dos piezas.

Los gramos y las horas NO son un numero inventado: se rebana el SDF capa por
capa y se separa perimetro, cascara solida y relleno disperso, igual que en
3d/molde-caballo-mecedora/costeo.py. Aun asi son ESTIMADO — aqui no hay
CuraEngine. En cuanto Bambu Studio de los numeros reales:

    python3 costeo_figuras.py --medido A 214.8 19.4 --medido B 158.2 14.1

Diferencia clave contra el molde: un figurin de retrato NO se vende por el
plastico. Se vende por las horas de escultura. El PLA es menos del 5% del
precio; el modelador es mas del 70%. Por eso aqui el costeo separa
INGENIERIA (una vez) de PRODUCCION (cada copia).

Filamento PLA a $300/kg = $0.30/g, dato del cliente.
"""

import argparse
import hashlib
import json
import os
import sys

import numpy as np
from scipy import ndimage

import figuras_sdf as S

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(AQUI, ".rebanado.json")

# --- proceso -----------------------------------------------------------------
LAYER_H = 0.20          # 0.4 mm de boquilla, calidad de figurin
LINE_W = 0.42
WALLS = 3
TOP_LAYERS = 5
BOTTOM_LAYERS = 4
INFILL = 0.12           # gyroid: un figurin decorativo no carga nada
RES = 0.60              # mm de la retícula del rebanado

DENS_PLA = 1.24         # g/cm3
COSTO_MAT = 0.30        # $/g  <- PLA $300/kg, dato del cliente
COSTO_MAQ = 2.54        # $/h  depreciacion P1S (5 anos, 2000 h/ano)
COSTO_LUZ = 0.24        # $/h
MERMA = 1.08

# Un figurin lleva soporte si o si: axilas, barbilla, hocico, visera, asas de
# las bolsas y la cubierta volada de la mesa. El soporte de arbol se lleva
# entre 12% y 22% del volumen de la pieza; tomo 0.17 y lo declaro.
SOPORTE = 0.17

# Fallo: una torre esbelta de 150 mm falla mas que una placa. 8%, no 5%.
TASA_FALLO = 0.08

# --- mano de obra de taller (por copia) --------------------------------------
POSPROCESO_H = {"A": 1.60, "B": 0.90}   # quitar soporte, lijar, sellar, pegar
COSTO_HORA_TALLER = 120.0
EMPAQUE = {"A": 65.0, "B": 45.0}        # caja rigida, foam, blister

# --- ingenieria (una sola vez, no se repite por copia) -----------------------
# Lo que de verdad cuesta: horas de escultor sacando volumen y parecido de una
# foto plana. Tarifa de freelance 3D en Mexico, no de estudio de VFX.
# La pieza A no son 4 x B: el cuerpo base se reusa entre las cuatro figuras y
# solo la cabeza, el pelo y la ropa se esculpen desde cero en cada una.
MODELADO_H = {"A": 16.0, "B": 8.0}
COSTO_HORA_MODELADO = 260.0

# Dos margenes distintos a proposito. La ingenieria es un servicio que se
# entrega una vez y no se puede revender: se cobra cerca de costo. La copia
# impresa si es producto y aguanta margen de producto.
MARGEN_ING = 0.35
MARGEN_PROD = 0.55

# Atajo de catalogo MPMX: $1000 de PV por cada 150 g. Sirve de piso cuando la
# ingenieria ya esta pagada y la pieza vive como SKU repetible.
GRAMOS_POR_MIL = 150.0

VEL = {
    "lento":  dict(ext=55, int=85, solido=100, disperso=120, over=1.30),
    "rapido": dict(ext=95, int=160, solido=175, disperso=200, over=1.12),
}


# -----------------------------------------------------------------------------
def _huella(key, res):
    """Identidad del rebanado: geometria + parametros de proceso. Si cambia
    cualquiera de los dos, el cache no sirve y hay que volver a rebanar."""
    geo = open(os.path.join(AQUI, "figuras_sdf.py"), "rb").read()
    firma = (f"{key}|{res}|{LAYER_H}|{LINE_W}|{WALLS}|{TOP_LAYERS}|"
             f"{BOTTOM_LAYERS}|{INFILL}|{SOPORTE}").encode()
    return hashlib.sha256(geo + firma).hexdigest()[:16]


def rebanar_cache(key, res=RES, forzar=False):
    """rebanar() cuesta minutos. El resultado solo depende de la huella."""
    h = _huella(key, res)
    db = {}
    if os.path.exists(CACHE):
        try:
            db = json.load(open(CACHE))
        except Exception:
            db = {}
    if not forzar and db.get(key, {}).get("huella") == h:
        return db[key]["v"], True
    v = rebanar(key, res)
    db[key] = dict(huella=h, v=v)
    json.dump(db, open(CACHE, "w"), indent=1)
    return v, False


def rebanar(key, res=RES):
    """Rebana el SDF y devuelve mm3 de filamento por tipo de linea."""
    P = S.PIEZAS[key]
    fn = P["f"]
    W, D, H = P["w"], P["d"], P["h"]

    xs = np.arange(-W / 2 - 1, W / 2 + 1 + res, res, dtype=np.float32)
    ys = np.arange(-D / 2 - 1, D / 2 + 1 + res, res, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    zs = np.arange(LAYER_H / 2, H + LAYER_H, LAYER_H, dtype=np.float32)
    nz = len(zs)
    nx, ny = X.shape

    pts = np.empty((nx, ny, 3), np.float32)
    pts[..., 0] = X
    pts[..., 1] = Y

    capas = np.zeros((nz, nx, ny), bool)
    for j, z in enumerate(zs):
        pts[..., 2] = z
        capas[j] = fn(pts) < 0.0

    banda = WALLS * LINE_W
    celda = res * res
    v_per = v_sol = v_dis = 0.0
    contorno = 0.0
    area_capa = np.zeros(nz)

    for j in range(nz):
        capa = capas[j]
        if not capa.any():
            continue
        # cascara: le faltan menos de N capas para tocar aire arriba o abajo
        arr = np.zeros_like(capa)
        for k in range(1, TOP_LAYERS + 1):
            arr |= ~capas[j + k] if j + k < nz else True
        aba = np.zeros_like(capa)
        for k in range(1, BOTTOM_LAYERS + 1):
            aba |= ~capas[j - k] if j - k >= 0 else True
        cascara = arr | aba

        dist = ndimage.distance_transform_edt(capa, sampling=res)
        es_per = capa & (dist <= banda)
        resto = capa & ~es_per
        v_per += es_per.sum() * celda
        v_sol += (resto & cascara).sum() * celda
        v_dis += (resto & ~cascara).sum() * celda
        borde = capa & ~ndimage.binary_erosion(capa)
        contorno += borde.sum() * res * (np.pi / 4)   # correccion de pixelado
        area_capa[j] = capa.sum() * celda

    v_per *= LAYER_H
    v_sol *= LAYER_H
    v_dis *= LAYER_H * INFILL
    pieza = v_per + v_sol + v_dis
    return dict(perimetros=v_per, cascaras=v_sol, relleno=v_dis,
                pieza=pieza, soporte=pieza * SOPORTE,
                total=pieza * (1 + SOPORTE),
                capas=nz, contorno=contorno,
                volumen_solido=area_capa.sum() * LAYER_H)


def horas(v):
    """Banda de tiempo desde la longitud de trayectoria por tipo de linea."""
    seccion = LINE_W * LAYER_H
    l_ext = v["contorno"]
    l_per = v["perimetros"] / seccion
    l_int = max(l_per - l_ext, 0.0)
    l_sol = v["cascaras"] / seccion
    l_dis = (v["relleno"] + v["soporte"]) / seccion
    out = {}
    for nombre, s in VEL.items():
        t = (l_ext / s["ext"] + l_int / s["int"]
             + l_sol / s["solido"] + l_dis / s["disperso"]) * s["over"]
        out[nombre] = t / 3600.0
    out["m"] = dict(ext=l_ext / 1000, int=l_int / 1000,
                    sol=l_sol / 1000, dis=l_dis / 1000)
    return out


def costo_produccion(key, g, h):
    """COGS de UNA copia, sin ingenieria."""
    mat = g * COSTO_MAT
    maq = h * COSTO_MAQ
    luz = h * COSTO_LUZ
    directo = (mat + maq + luz) * MERMA
    # margen de reimpresion: 8% de fallo son 1/(1-0.08) intentos, no 1.08
    directo /= (1.0 - TASA_FALLO)
    obra = POSPROCESO_H[key] * COSTO_HORA_TALLER
    emp = EMPAQUE[key]
    return dict(material=mat, maquina=maq, luz=luz,
                reimpresion=directo - (mat + maq + luz) * MERMA,
                merma=(mat + maq + luz) * 0.08,
                directo=directo, mano_obra=obra, empaque=emp,
                total=directo + obra + emp)


def precio(key, c_prod, ing, tiraje):
    """Precio unitario. La ingenieria se reparte entre el tiraje y lleva su
    propio margen; la copia lleva el de producto."""
    ing_u = ing / tiraje
    pv = ing_u / (1 - MARGEN_ING) + c_prod / (1 - MARGEN_PROD)
    costo = ing_u + c_prod
    return costo, pv, pv - costo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--medido", nargs=3, action="append", metavar=("PIEZA", "G", "H"),
                    help="gramos y horas MEDIDOS por Bambu Studio")
    ap.add_argument("--tirajes", type=int, nargs="+", default=[1, 4, 10, 25],
                    help="copias entre las que se reparte la ingenieria")
    ap.add_argument("--rebanar", action="store_true",
                    help="ignora el cache y vuelve a rebanar (tarda minutos)")
    a = ap.parse_args()

    medidos = {m[0]: (float(m[1]), float(m[2])) for m in (a.medido or [])}
    resumen = {}

    for key in ("A", "B"):
        P = S.PIEZAS[key]
        med = key in medidos
        et = "MEDIDO" if med else "ESTIMADO"
        print("=" * 74)
        print(f"PIEZA {key} — {P['nombre']}")
        print(f"  {P['w']:.0f} x {P['d']:.0f} x {P['h']:.0f} mm  ·  PLA  ·  "
              f"capa {LAYER_H} mm  ·  {WALLS} paredes  ·  relleno {INFILL:.0%}")
        print("=" * 74)

        v, cacheado = rebanar_cache(key, forzar=a.rebanar)
        if med:
            g, h = medidos[key]
            banda = None
        else:
            g = v["total"] / 1000.0 * DENS_PLA
            banda = horas(v)
            h = 0.5 * (banda["lento"] + banda["rapido"])

        print(f"\nConsumo  [{et}]{'   (cache)' if cacheado else ''}")
        print(f"  capas de {LAYER_H} mm                     {v['capas']:>8}")
        print(f"  volumen envolvente macizo         {v['volumen_solido']/1000:8.1f} cm3")
        print(f"  perimetros ({WALLS} x {LINE_W} mm)           {v['perimetros']/1000:8.2f} cm3")
        print(f"  cascaras solidas ({TOP_LAYERS}/{BOTTOM_LAYERS})".ljust(36)
              + f"{v['cascaras']/1000:8.2f} cm3")
        print(f"  relleno gyroid al {INFILL:.0%}             {v['relleno']/1000:8.2f} cm3")
        print(f"  soporte de arbol ({SOPORTE:.0%})            {v['soporte']/1000:8.2f} cm3")
        print(f"  {'-'*50}")
        print(f"  filamento                         {v['total']/1000:8.2f} cm3")
        print(f"  masa                              {g:8.1f} g")
        if banda:
            m = banda["m"]
            print(f"  trayectoria                       {sum(m.values()):8.0f} m")
            print(f"  tiempo de maquina                 {h:8.2f} h   "
                  f"banda {banda['lento']:.1f} – {banda['rapido']:.1f} h")
        else:
            print(f"  tiempo de maquina                 {h:8.2f} h")

        c = costo_produccion(key, g, h)
        print(f"\nCOSTO DE PRODUCCION — por copia  [{et}]")
        print(f"  filamento PLA {g:.0f} g @ ${COSTO_MAT:.2f}/g".ljust(36)
              + f"${c['material']:9.2f}")
        print(f"  depreciacion de maquina           ${c['maquina']:9.2f}")
        print(f"  energia                           ${c['luz']:9.2f}")
        print(f"  merma 8%                          ${c['merma']:9.2f}")
        print(f"  reimpresion ({TASA_FALLO:.0%} de fallo)".ljust(36)
              + f"${c['reimpresion']:9.2f}")
        print(f"  posproceso {POSPROCESO_H[key]:.1f} h @ ${COSTO_HORA_TALLER:.0f}/h".ljust(36)
              + f"${c['mano_obra']:9.2f}")
        print(f"  empaque                           ${c['empaque']:9.2f}")
        print(f"  {'-'*50}")
        print(f"  COSTO DE PRODUCCION               ${c['total']:9.2f}")
        print(f"     el PLA es el {c['material']/c['total']:.0%} de este costo. "
              f"El resto es taller.")

        ing = MODELADO_H[key] * COSTO_HORA_MODELADO
        print(f"\nCOSTO DE INGENIERIA — una sola vez, no se repite por copia")
        print(f"  escultura desde foto {MODELADO_H[key]:.0f} h @ "
              f"${COSTO_HORA_MODELADO:.0f}/h".ljust(38) + f"${ing:9.2f}")

        print(f"\nPRECIO  (ingenieria al {MARGEN_ING:.0%}, produccion al {MARGEN_PROD:.0%})")
        print(f"  {'tiraje':>7}{'ing/pieza':>12}{'costo':>11}{'PRECIO':>11}"
              f"{'utilidad':>11}{'margen':>9}")
        for t in a.tirajes:
            costo, pv, u = precio(key, c["total"], ing, t)
            print(f"  {t:>7}{ing/t:>12,.0f}{costo:>11,.0f}{pv:>11,.0f}"
                  f"{u:>11,.0f}{u/pv:>9.0%}")
        piso = g / GRAMOS_POR_MIL * 1000
        print(f"  piso de catalogo por gramaje ({GRAMOS_POR_MIL:.0f} g/$1000): "
              f"${piso:,.0f}  <- solo aplica con la ingenieria ya pagada")

        costo1, pv1, _ = precio(key, c["total"], ing, 1)
        resumen[key] = dict(g=g, h=h, prod=c["total"], ing=ing,
                            costo1=costo1, pv1=pv1)

    print("\n" + "=" * 74)
    print("RESUMEN — las dos piezas por separado, UNA copia de cada una")
    print("=" * 74)
    print(f"  {'':<5}{'g':>7}{'h':>7}{'produccion':>13}{'ingenieria':>13}"
          f"{'COSTO':>11}{'PRECIO':>11}")
    tot_c = tot_p = 0.0
    for key in ("A", "B"):
        r = resumen[key]
        tot_c += r["costo1"]
        tot_p += r["pv1"]
        print(f"  {key:<5}{r['g']:>7.0f}{r['h']:>7.1f}{r['prod']:>13,.0f}"
              f"{r['ing']:>13,.0f}{r['costo1']:>11,.0f}{r['pv1']:>11,.0f}")
    print(f"  {'-'*67}")
    print(f"  {'A+B':<5}{'':>7}{'':>7}{'':>13}{'':>13}{tot_c:>11,.0f}{tot_p:>11,.0f}")
    print(f"\n  Precios sin IVA. Si van con factura, suma 16%: "
          f"${tot_p*1.16:,.0f} con IVA.")

    if not medidos:
        print("\n⚠  ESTIMADO, no MEDIDO. El rebanado es una simulacion sobre el")
        print("   campo, no CuraEngine. Antes de mandarle esto a un cliente como")
        print("   cotizacion en firme: rebana el STL en Bambu Studio y corre")
        print("   --medido A <g> <h> --medido B <g> <h>.")
        print("   Las horas de escultura son un supuesto de taller, no una")
        print("   medicion: ajustalas al modelador que vayas a usar.")


if __name__ == "__main__":
    sys.exit(main())
