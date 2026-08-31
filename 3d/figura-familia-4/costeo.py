#!/usr/bin/env python3
"""
Costeo de la figura familiar personalizada (4 integrantes sobre base).
Impresa en GRIS + pintada a mano aparte. Incluye empaque y envio en CDMX.

Modelo: las 7 capas de costo del taller CreaLab (v2.1, 18-ago-2026).

    COSTO DIRECTO   = MATERIAL + LUZ + MANO DE OBRA + MAQUINA + EMPAQUE + GESTION
    COSTO CON MERMA = COSTO DIRECTO x (1 + merma)
    PISO DE PRECIO  = COSTO CON MERMA + (h-maquina desatendida x tarifa de oportunidad)
    PRECIO          = MAX( COSTO CON MERMA / (1 - margen) , PISO DE PRECIO )
    PRECIO FINAL    = PRECIO + ENVIO

Los gramos y las horas son ESTIMADO geometrico: NO salieron de Bambu Studio.
En cuanto haya slice real:

    python3 costeo.py --gramos 210 --horas 27      # pasa a MEDIDO
    python3 costeo.py --sin-pintura                # variante gris crudo
    python3 costeo.py --ocupacion 0.85             # taller saturado -> piso de precio
"""

import argparse

# --- inputs del taller (Parte II y III de taller-crealab) --------------------
COSTO_G_PLA_MATTE = 0.429      # Bambu PLA Matte, precio de lista ML 18-ago-2026
LUZ_P1S_PLA       = 0.78       # $/h a 6.50 $/kWh (DAC)
MAQ_P1S           = 4.00       # $/h amortizacion + desgaste
HORA_HOMBRE       = 71.00      # $/h costo patronal real (10k nominal x 1.36 / 192 h)
MIN_HOMBRE        = HORA_HOMBRE / 60

MERMA             = 0.20       # pieza nueva, alta, delgada, con soportes (20-25%)
MARGEN_MIXTO      = 0.60       # 3D + acabado manual = trabajo mixto
MARGEN_3D         = 0.55       # 3D puro (variante sin pintar)

EMPAQUE_K4        = 34.11      # bolsa + burbuja 0.20 m2 + caja 30x20x20 + cinta + etiqueta
EMPAQUE_CUNA      = 15.00      # cuna de foam: pieza pintada y fragil, K4 solo no basta
GESTION           = 59.17      # pedido con diseno: brief + preview + aprobacion (50 min)

# Envio CDMX local. Volumetrico manda: 30x20x20 / 5000 = 2.4 kg cobrables.
ENVIO_FLETE       = 195.00     # terrestre local + 20.7% cargo por combustible
ENVIO_GUIA        = 9.47       # generar guia + etiquetar + agendar (8 min)
ENVIO_TRASLADO    = 11.00      # 45 min a sucursal, prorrateado entre ~5 envios

OPORTUNIDAD_P1S   = 30.00      # tarifa base; el factor lo da la ocupacion real (CHECK A)

# --- geometria estimada -----------------------------------------------------
# Adultos 15 cm, ninos 11 cm, base circular 12 cm x 2.5 cm con relieve "FAMILIA".
# 0.12 mm de capa en las figuras (la cara es el entregable), 0.20 mm en la base.
GRAMOS_DEFAULT = 210           # 45 g x2 adultos + 22 g x2 ninos + 60 g base + soportes
HORAS_DEFAULT  = 27            # 8 h x2 + 4 h x2 + 3 h base; ~9 h de reloj en 4 maquinas

# --- consumibles de pintura -------------------------------------------------
PINTURA = {
    "Primer gris en aerosol (prorrateo ~7 usos por lata)": 25.00,
    "Acrilicos (piel, cabello, ropa, ojos)":               20.00,
    "Barniz mate de sellado":                              15.00,
    "Masilla, pinceles y consumibles amortizados":         10.00,
}

# --- tabulador de tiempos humanos (minutos) ---------------------------------
MO_BASE = [
    ("Modelado 3D desde la foto (escultura + retopo + preparar impresion)", 90),
    ("Preparar archivo + slicing de pieza nueva",                            25),
    ("Cargar filamento + arrancar 4 corridas + verificar primera capa",      21),
    ("Retirar piezas + limpiar cama (4 corridas)",                           12),
    ("Post-proceso: quitar soportes, lijar, masilla (4 fig + base)",         90),
]
MO_PINTURA = [
    ("Imprimacion + manejo de secado",                                       15),
    ("Pintura a mano (adultos 70 min c/u, ninos 50 min c/u)",               240),
    ("Barniz + ensamble en la base + QA",                                    30),
]
MO_SIN_PINTURA = [
    ("Barniz opcional + ensamble en la base + QA",                           15),
]


def costear(gramos, horas, con_pintura=True, ocupacion=None, medido=False):
    material_fil = gramos * COSTO_G_PLA_MATTE
    material_pin = sum(PINTURA.values()) if con_pintura else 0.0
    luz = horas * LUZ_P1S_PLA
    maquina = horas * MAQ_P1S
    tareas = MO_BASE + (MO_PINTURA if con_pintura else MO_SIN_PINTURA)
    minutos = sum(m for _, m in tareas)
    mo = minutos * MIN_HOMBRE
    empaque = EMPAQUE_K4 + EMPAQUE_CUNA
    envio = ENVIO_FLETE + ENVIO_GUIA + ENVIO_TRASLADO

    directo = material_fil + material_pin + luz + mo + maquina + empaque + GESTION
    con_merma = directo * (1 + MERMA)

    if ocupacion is None:
        factor, etiqueta = None, "SIN VERIFICACION DE CAPACIDAD (CHECK A no corrido)"
    elif ocupacion < 0.40:
        factor, etiqueta = 0.0, "taller vacio (<40%)"
    elif ocupacion <= 0.70:
        factor, etiqueta = 0.5, "operacion normal (40-70%)"
    elif ocupacion <= 0.90:
        factor, etiqueta = 1.0, "taller saturado (>70%)"
    else:
        factor, etiqueta = 1.5, "saturado con lista de espera (>90%)"

    margen = MARGEN_MIXTO if con_pintura else MARGEN_3D
    precio_margen = con_merma / (1 - margen)
    pisos = {
        "taller vacio (x0)":            con_merma,
        "operacion normal (x0.5)":      con_merma + horas * OPORTUNIDAD_P1S * 0.5,
        "taller saturado (x1.0)":       con_merma + horas * OPORTUNIDAD_P1S * 1.0,
        "saturado c/espera (x1.5)":     con_merma + horas * OPORTUNIDAD_P1S * 1.5,
    }
    piso = con_merma if factor is None else con_merma + horas * OPORTUNIDAD_P1S * factor
    precio = max(precio_margen, piso)
    final = precio + envio

    ancho = 62
    tag = "MEDIDO (slicer)" if medido else "PRELIMINAR (estimado geometrico, sin slicer)"
    print("=" * ancho)
    print(f"FIGURA FAMILIAR 4 INTEGRANTES {'GRIS + PINTADA A MANO' if con_pintura else 'GRIS SIN PINTAR'}")
    print(f"{tag} · {gramos} g · {horas} h-maquina · PLA Matte gris · P1S")
    print("=" * ancho)

    def fila(k, v):
        print(f"  {k:<52}{v:>9,.2f}")

    print("\nCAPA 1 · MATERIAL")
    fila(f"Filamento PLA Matte gris {gramos} g x ${COSTO_G_PLA_MATTE}/g", material_fil)
    if con_pintura:
        for k, v in PINTURA.items():
            fila(k, v)
    fila("SUBTOTAL", material_fil + material_pin)

    print("\nCAPA 2 · LUZ")
    fila(f"{horas} h P1S x ${LUZ_P1S_PLA}/h (DAC 6.50 $/kWh)", luz)

    print("\nCAPA 3 · MANO DE OBRA @ $71/h")
    for k, m in tareas:
        fila(f"{k} ({m} min)", m * MIN_HOMBRE)
    fila(f"SUBTOTAL ({minutos} min = {minutos/60:.2f} h-hombre)", mo)

    print("\nCAPA 4 · MAQUINA")
    fila(f"{horas} h P1S x ${MAQ_P1S}/h (amortizacion + desgaste)", maquina)

    print("\nCAPA 5 · EMPAQUE")
    fila("Kit K4 envio individual grande", EMPAQUE_K4)
    fila("Cuna de foam (pieza pintada, fragil)", EMPAQUE_CUNA)

    print("\nCAPA 6 · GESTION COMERCIAL")
    fila("Pedido con diseno (50 min)", GESTION)

    print("\n" + "-" * ancho)
    fila("COSTO DIRECTO", directo)
    fila(f"COSTO CON MERMA ({MERMA:.0%})", con_merma)
    print("-" * ancho)

    print("\nCAPA 7 · PISO DE PRECIO POR OCUPACION (no se suma al costo)")
    for k, v in pisos.items():
        fila(k, v)
    print(f"  Ocupacion aplicada: {etiqueta}")

    print("\nPRECIO")
    fila(f"Costo con merma / (1 - {margen:.0%})", precio_margen)
    fila("Piso de precio aplicado", piso)
    fila("PRECIO DE VENTA (sin envio, sin IVA)", precio)
    fila(f"Envio CDMX (flete {ENVIO_FLETE:.0f} + guia + traslado)", envio)
    fila("PRECIO FINAL SIN IVA", final)
    fila("PRECIO FINAL CON IVA 16%", final * 1.16)

    print("\nKPI INTERNO (nunca va en la cotizacion)")
    fila("Contribucion por hora-maquina", (precio - con_merma) / horas)
    fila("Margen real sobre venta sin envio", (precio - con_merma) / precio * 100)
    print("=" * ancho)
    return dict(directo=directo, con_merma=con_merma, precio=precio, final=final)


def figura_adicional(gramos=45, horas=8, minutos=102):
    """Costo marginal de un integrante adulto extra en el mismo pedido."""
    d = gramos * COSTO_G_PLA_MATTE + horas * (LUZ_P1S_PLA + MAQ_P1S) + minutos * MIN_HOMBRE + 20.0
    cm = d * (1 + MERMA)
    p = cm / (1 - MARGEN_MIXTO)
    print(f"\nINTEGRANTE ADICIONAL (adulto, {gramos} g, {horas} h, {minutos} min-hombre)")
    print(f"  Costo directo        {d:>9,.2f}")
    print(f"  Costo con merma      {cm:>9,.2f}")
    print(f"  Precio sin IVA       {p:>9,.2f}")
    print(f"  Precio con IVA       {p*1.16:>9,.2f}")
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gramos", type=float, default=GRAMOS_DEFAULT)
    ap.add_argument("--horas", type=float, default=HORAS_DEFAULT)
    ap.add_argument("--ocupacion", type=float, default=None,
                    help="ocupacion real de las impresoras vivas, 0.0-1.0 (CHECK A)")
    ap.add_argument("--sin-pintura", action="store_true")
    ap.add_argument("--medido", action="store_true",
                    help="marcar que gramos y horas vienen de Bambu Studio")
    a = ap.parse_args()
    costear(a.gramos, a.horas, con_pintura=not a.sin_pintura,
            ocupacion=a.ocupacion, medido=a.medido)
    if not a.sin_pintura:
        figura_adicional()
