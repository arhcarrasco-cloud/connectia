#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SITIOS CONNECTIA · Generador del file de venta (PDF)
────────────────────────────────────────────────────
Lee data/oportunidades.json (la ÚNICA fuente de verdad) y arma
Sitios-Connectia-File-de-Venta.pdf: portada + índice + 1 página por sitio.

Uso:
    python3 build_pdf.py

Para agregar un sitio nuevo: agrega un objeto a data/oportunidades.json,
deja su foto en assets/sitios/ y vuelve a correr este script.
"""
import json, os, textwrap
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas as rl_canvas

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "oportunidades.json")
OUT  = os.path.join(HERE, "Sitios-Connectia-File-de-Venta.pdf")
LOGO = os.path.join(HERE, "assets", "connectia-white.png")

W, H = landscape(letter)          # 792 x 612

# ── Tokens de marca Connectia V3 ──
INDIGO   = HexColor("#201040")
VIOLET   = HexColor("#6030A0")
HOT      = HexColor("#7B3FF2")
MAGENTA  = HexColor("#E01C8A")
CITRUS   = HexColor("#FF6A1A")
LIME     = HexColor("#C8FF00")
SPARK    = HexColor("#FFC220")
MIST     = HexColor("#E9E6F0")
WHITE    = HexColor("#FFFFFF")
INK      = HexColor("#0A0118")

CAT_LBL = {"landmark": "Landmark", "muro": "Muro / espectacular",
           "mega": "Mega valla", "dooh": "Pantalla DOOH 3D"}


def mxn(n):
    return "$" + format(int(n), ",d") if n else "Cotizar"


def imp(n):
    if not n:
        return "—"
    return (f"{n/1e6:.1f}".rstrip("0").rstrip(".") + " M") if n >= 1e6 else f"{round(n/1e3)} K"


def vgrad(c, x, y, w, h, top, bottom, steps=140):
    """Degradado vertical simple."""
    for i in range(steps):
        t = i / (steps - 1)
        col = Color(top.red + (bottom.red - top.red) * t,
                    top.green + (bottom.green - top.green) * t,
                    top.blue + (bottom.blue - top.blue) * t)
        c.setFillColor(col)
        c.rect(x, y + h - (i + 1) * h / steps, w, h / steps + 0.7, stroke=0, fill=1)


def fit_cover(c, path, x, y, w, h):
    """Dibuja la imagen cubriendo el rect (recorte centrado)."""
    try:
        img = ImageReader(path)
        iw, ih = img.getSize()
    except Exception:
        c.setFillColor(INDIGO); c.rect(x, y, w, h, stroke=0, fill=1); return
    scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)
    c.drawImage(img, x - (dw - w) / 2, y - (dh - h) / 2, dw, dh, mask="auto")
    c.restoreState()


def eyebrow(c, txt, x, y, col=HOT, size=8):
    c.setFillColor(col); c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, " ".join(txt.upper()))


def wrap(c, txt, x, y, width, font="Helvetica", size=10, lead=13.5, col=MIST, maxlines=99):
    c.setFillColor(col); c.setFont(font, size)
    approx = int(width / (size * 0.5))
    lines = textwrap.wrap(txt, approx)[:maxlines]
    for ln in lines:
        c.drawString(x, y, ln); y -= lead
    return y


def stat_box(c, x, y, w, h, label, value, accent=HOT):
    c.setFillColor(HexColor("#2A1A4E")); c.roundRect(x, y, w, h, 7, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#4B2E86")); c.setLineWidth(0.7)
    c.roundRect(x, y, w, h, 7, stroke=1, fill=0)
    c.setFillColor(accent); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(x + 9, y + h - 14, " ".join(label.upper()))
    # el valor se encoge hasta caber en la caja (audiencias largas)
    size = 12.5
    while size > 6.5 and c.stringWidth(value, "Helvetica-Bold", size) > w - 18:
        size -= 0.5
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", size)
    c.drawString(x + 9, y + 10 + (12.5 - size) * 0.35, value)


def logo(c, x, y, h=15):
    try:
        img = ImageReader(LOGO); iw, ih = img.getSize()
        c.drawImage(img, x, y, h * iw / ih, h, mask="auto")
    except Exception:
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 13); c.drawString(x, y, "connectia")


# ═══════════ PORTADA ═══════════
def cover(c, sitios):
    vgrad(c, 0, 0, W, H, HexColor("#1A0B3D"), HexColor("#FF6A1A"))
    c.setFillColor(Color(0, 0, 0, alpha=0.20)); c.rect(0, 0, W, H, stroke=0, fill=1)

    import random
    random.seed(7)
    for i in range(70):
        r = random.uniform(0.5, 1.9)
        c.setFillColor(Color(1, 1, 1, alpha=random.uniform(0.15, 0.55)))
        c.circle(random.uniform(0, W), random.uniform(H * 0.35, H), r, stroke=0, fill=1)

    logo(c, 52, H - 62, 19)
    eyebrow(c, "Portafolio OOH · CDMX y Área Metropolitana", 52, H - 148, WHITE, 9)

    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 62)
    c.drawString(52, H - 222, "SITIOS CONNECTIA")
    c.setFont("Helvetica", 15.5)
    c.drawString(52, H - 252, "Landmarks · Mega vallas · Pantallas DOOH 3D")

    y = H - 300
    for ln in ["Inventario de alto impacto en los cruces de mayor aforo del Valle de México.",
               "Cada sitio con medidas verificadas, impactos mensuales, audiencia y mockup de campaña."]:
        c.setFont("Helvetica", 11); c.setFillColor(Color(1, 1, 1, alpha=.94))
        c.drawString(52, y, ln); y -= 17

    total_imp = sum(s.get("impMes") or 0 for s in sitios)
    cards = [("Sitios", str(len(sitios))),
             ("Impactos / mes", imp(total_imp)),
             ("Formatos", str(len({s.get("cat") for s in sitios}))),
             ("Cobertura", "CDMX + AMCM")]
    bx, bw, bh = 52, 152, 56
    for i, (l, v) in enumerate(cards):
        x = bx + i * (bw + 13)
        c.setFillColor(Color(0, 0, 0, alpha=.26)); c.roundRect(x, 96, bw, bh, 9, stroke=0, fill=1)
        c.setStrokeColor(Color(1, 1, 1, alpha=.35)); c.setLineWidth(.8)
        c.roundRect(x, 96, bw, bh, 9, stroke=1, fill=0)
        c.setFillColor(Color(1, 1, 1, alpha=.82)); c.setFont("Helvetica-Bold", 6.5)
        c.drawString(x + 12, 96 + bh - 17, " ".join(l.upper()))
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 21)
        c.drawString(x + 12, 96 + 13, v)

    c.setFillColor(Color(1, 1, 1, alpha=.85)); c.setFont("Helvetica", 8)
    c.drawString(52, 58, "Connectia · Facilitadores Publicitarios HS, S.A. de C.V.  ·  hola@connectia.mx  ·  connectia.mx")
    c.drawString(52, 44, "Tarifas mensuales en MXN sin IVA. Disponibilidad sujeta a confirmación.")
    c.showPage()


# ═══════════ ÍNDICE ═══════════
def index_page(c, sitios):
    """Índice paginado: 15 sitios por hoja."""
    PER = 15
    bloques = [sitios[i:i + PER] for i in range(0, len(sitios), PER)]
    for bi, bloque in enumerate(bloques):
        c.setFillColor(INDIGO); c.rect(0, 0, W, H, stroke=0, fill=1)
        vgrad(c, 0, H - 5, W, 5, HOT, MAGENTA)
        logo(c, 52, H - 52, 14)
        sufijo = f" · {bi+1} de {len(bloques)}" if len(bloques) > 1 else ""
        eyebrow(c, "Índice del inventario" + sufijo, 52, H - 92)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 30)
        c.drawString(52, H - 126, "SITIOS DISPONIBLES")

        y = H - 172
        c.setFillColor(HOT); c.setFont("Helvetica-Bold", 7)
        for lbl, x in [("#", 52), ("SITIO", 78), ("FORMATO", 356), ("MEDIDAS", 468),
                       ("IMP/MES", 604), ("TARIFA", 678)]:
            c.drawString(x, y, lbl)
        y -= 8
        c.setStrokeColor(HexColor("#4B2E86")); c.setLineWidth(.8); c.line(52, y, W - 52, y)
        y -= 18

        for j, s in enumerate(bloque):
            i = bi * PER + j + 1
            if i % 2 == 0:
                c.setFillColor(HexColor("#2A1A4E")); c.rect(48, y - 6, W - 96, 19, stroke=0, fill=1)
            c.setFillColor(HOT); c.setFont("Helvetica-Bold", 8.5); c.drawString(52, y, f"{i:02d}")
            c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 9)
            c.drawString(78, y, s["titulo"][:48])
            c.setFillColor(MIST); c.setFont("Helvetica", 8)
            c.drawString(356, y, CAT_LBL.get(s.get("cat"), "—"))
            c.drawString(468, y, s.get("medidas", "")[:26])
            c.setFillColor(LIME); c.setFont("Helvetica-Bold", 8.5)
            c.drawString(604, y, imp(s.get("impMes")))
            c.setFillColor(SPARK); c.drawString(678, y, mxn(s.get("tarifa")))
            y -= 24

        if bi == len(bloques) - 1:
            tot_t = sum(s.get("tarifa") or 0 for s in sitios)
            tot_i = sum(s.get("impMes") or 0 for s in sitios)
            c.setStrokeColor(HexColor("#4B2E86")); c.line(52, y + 12, W - 52, y + 12)
            c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 9.5)
            c.drawString(78, y - 4, "TOTAL DEL PORTAFOLIO")
            c.setFillColor(LIME); c.drawString(604, y - 4, imp(tot_i))
            c.setFillColor(SPARK); c.drawString(678, y - 4, mxn(tot_t))

        c.setFillColor(HexColor("#8A7FA8")); c.setFont("Helvetica", 7.5)
        c.drawString(52, 34, "Sitios Connectia · Índice")
        c.showPage()


# ═══════════ PÁGINA DE SITIO ═══════════
def site_page(c, s, n, total):
    c.setFillColor(INDIGO); c.rect(0, 0, W, H, stroke=0, fill=1)

    # foto: mitad superior a sangre
    ph = H * 0.505
    foto = s.get("fotoWm") or s.get("foto") or ""
    fit_cover(c, os.path.join(HERE, foto), 0, H - ph, W, ph)
    # velo inferior para el título
    for i in range(60):
        t = i / 59
        c.setFillColor(Color(0.125, 0.063, 0.251, alpha=t * 0.92))
        c.rect(0, H - ph + i * 62 / 60, W, 62 / 60 + .8, stroke=0, fill=1)

    logo(c, 52, H - 44, 13)
    c.setFillColor(Color(1, 1, 1, alpha=.85)); c.setFont("Helvetica-Bold", 8)
    c.drawRightString(W - 52, H - 38, f"{n:02d} / {total:02d}")

    # título sobre la foto
    ty = H - ph + 26
    c.setFillColor(SPARK); c.setFont("Helvetica-Bold", 7.5)
    c.drawString(52, ty + 30, " ".join((CAT_LBL.get(s.get("cat"), "SITIO") + " · " + s.get("medidas", "")).upper()))
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 25)
    c.drawString(52, ty + 4, s["titulo"][:56])

    # ── zona de datos ──
    top = H - ph - 22
    c.setFillColor(MIST); c.setFont("Helvetica", 10)
    c.drawString(52, top, s.get("ubic", ""))

    bw, bh, gap = 168, 46, 12
    by = top - bh - 14
    stats = [("Tarifa mensual", mxn(s.get("tarifa")), SPARK),
             ("Impactos / mes", imp(s.get("impMes")), LIME),
             ("Audiencia", (s.get("aud") or "—"), HOT),
             ("Nivel de impacto", (s.get("imp") or "alto").replace("tactico", "Táctico").capitalize(), MAGENTA)]
    for i, (l, v, col) in enumerate(stats):
        stat_box(c, 52 + i * (bw + gap), by, bw, bh, l, v, col)

    # ficha técnica (una tira de specs bajo las métricas)
    sp = s.get("specs") or {}
    filas = [(l, v) for l, v in [("Material", sp.get("material")), ("Vista", sp.get("vista")),
                                 ("Orientación", sp.get("orientacion")), ("NSE", sp.get("nse")),
                                 ("Iluminación", sp.get("iluminacion")),
                                 ("Clasificación", sp.get("clasificacion"))] if v]
    sy = by - 12
    if filas:
        sw = (W - 104) / len(filas)
        for k, (l, v) in enumerate(filas):
            x = 52 + k * sw
            c.setFillColor(HOT); c.setFont("Helvetica-Bold", 6)
            c.drawString(x, sy - 10, " ".join(l.upper()))
            c.setFillColor(MIST); c.setFont("Helvetica-Bold", 9)
            c.drawString(x, sy - 23, str(v))
        c.setStrokeColor(HexColor("#3A2568")); c.setLineWidth(.7)
        c.line(52, sy - 32, W - 52, sy - 32)
        sy -= 44

    # dos columnas de copy
    cy = sy - 8
    colw = (W - 104 - 30) / 2
    eyebrow(c, "Por qué funciona", 52, cy)
    y1 = wrap(c, s.get("beneficio", ""), 52, cy - 16, colw, size=9.5, lead=13, maxlines=4)
    if s.get("obj"):
        eyebrow(c, "Objetivo", 52, y1 - 6)
        wrap(c, s["obj"], 52, y1 - 22, colw, size=9.5, lead=13, maxlines=2)

    x2 = 52 + colw + 30
    y2 = cy
    if s.get("dir"):
        eyebrow(c, "Dirección", x2, cy)
        y2 = wrap(c, s["dir"], x2, cy - 16, colw, size=9.5, lead=13, maxlines=2)
    if sp.get("anchor"):
        eyebrow(c, "Anchor cercano", x2, y2 - 6, SPARK)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 10)
        c.drawString(x2, y2 - 21, sp["anchor"][:52])
        y2 -= 21
        if sp.get("marcas"):
            c.setFillColor(MIST); c.setFont("Helvetica", 8.5)
            c.drawString(x2, y2 - 13, sp["marcas"][:74])
            y2 -= 13
        y2 -= 12   # aire antes del bloque de campañas
    camp = s.get("campanas") or []
    if camp:
        eyebrow(c, "Campañas sugeridas", x2, y2 - 6)
        cx, cyy = x2, y2 - 34
        for t in camp:
            tw = c.stringWidth(t, "Helvetica-Bold", 7.5) + 18
            if cx + tw > x2 + colw:
                cx = x2; cyy -= 20
            c.setFillColor(HexColor("#3A2568")); c.roundRect(cx, cyy, tw, 15, 7.5, stroke=0, fill=1)
            c.setFillColor(SPARK); c.setFont("Helvetica-Bold", 7.5)
            c.drawString(cx + 9, cyy + 4.6, t)
            cx += tw + 7

    # estatus
    est = s.get("estatus", "disponible")
    col = {"disponible": HexColor("#22C55E"), "bloqueada": CITRUS}.get(est, HexColor("#EF4444"))
    lbl = {"disponible": "DISPONIBLE", "bloqueada": "BLOQUEADA"}.get(est, "NO DISPONIBLE")
    c.setFillColor(col); c.circle(56, 44, 4.2, stroke=0, fill=1)
    c.setFillColor(MIST); c.setFont("Helvetica-Bold", 7.5); c.drawString(66, 41, lbl)

    c.setFillColor(HexColor("#8A7FA8")); c.setFont("Helvetica", 7.5)
    c.drawRightString(W - 52, 41, "hola@connectia.mx · connectia.mx/SitiosConnectia")
    vgrad(c, 0, 0, W, 3.5, HOT, MAGENTA)
    c.showPage()


# ═══════════ CIERRE ═══════════
def closing(c):
    vgrad(c, 0, 0, W, H, HexColor("#201040"), HexColor("#6030A0"))
    logo(c, 52, H - 62, 19)
    eyebrow(c, "Siguiente paso", 52, H / 2 + 62, WHITE, 9)
    c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 40)
    c.drawString(52, H / 2 + 20, "ARMEMOS TU PLAN")
    c.setFont("Helvetica", 13); c.setFillColor(Color(1, 1, 1, alpha=.93))
    c.drawString(52, H / 2 - 12, "Selecciona los sitios en connectia.mx/SitiosConnectia y te enviamos")
    c.drawString(52, H / 2 - 32, "la cotización formal con disponibilidad y calendario de producción.")
    c.setFont("Helvetica-Bold", 12); c.setFillColor(LIME)
    c.drawString(52, H / 2 - 76, "hola@connectia.mx")
    c.setFillColor(Color(1, 1, 1, alpha=.8)); c.setFont("Helvetica", 8)
    c.drawString(52, 48, "Connectia · Facilitadores Publicitarios HS, S.A. de C.V. · RFC FPH181203KA8")
    c.showPage()


def main():
    with open(DATA, encoding="utf-8") as f:
        sitios = json.load(f)
    order = {"landmark": 0, "muro": 1, "mega": 2, "dooh": 3}
    sitios.sort(key=lambda s: (order.get(s.get("cat"), 9), -(s.get("impMes") or 0)))

    c = rl_canvas.Canvas(OUT, pagesize=landscape(letter))
    c.setTitle("Sitios Connectia · File de venta")
    c.setAuthor("Connectia")
    cover(c, sitios)
    index_page(c, sitios)
    for i, s in enumerate(sitios, 1):
        site_page(c, s, i, len(sitios))
    closing(c)
    c.save()
    print(f"OK  {OUT}  ·  {len(sitios)} sitios  ·  {len(sitios)+3} páginas")


if __name__ == "__main__":
    main()
