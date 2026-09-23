#!/usr/bin/env python3
"""
Generador determinista de la Plantilla Cotizador (D) de Connectia.

El DISENO esta bloqueado en este archivo. Solo cambia el CONTENIDO, que entra por JSON.
    python3 generate_cotizador.py contenido.json salida.pdf

Tokens, layout, footer y marca de agua siguen la especificacion de la skill
`plantilla-cotizador`. No editar colores ni estructura sin instruccion de Roger.
"""
import json, sys, base64, pathlib

BASE = pathlib.Path(__file__).parent
ASSETS = BASE / "assets"

# ---- TOKENS BLOQUEADOS -------------------------------------------------------
ACCENT     = "#872B90"   # Connectia Purple canonico
LAV_SOFT   = "#F1ECF9"   # cajas nota / specs / banda subtitulo
LAV_TERMS  = "#EEE6F5"   # caja de terminos y condiciones
META_BG    = "#E7DEF5"   # banda meta (referencia / fecha / vigencia)
TEXT       = "#1B1B1B"
GRAY       = "#7A7A7A"
RULE       = "#E2E2E2"

EMISOR = ("Connectia · Hacienda de Temoluco #130<br>"
          "Col. Villaquietud, Coyoacán<br>CDMX, C.P. 04960")

UNI = ("", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE", "DIEZ",
       "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO",
       "DIECINUEVE", "VEINTE")
DEC = ("", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA")
CEN = ("", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS",
       "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS")


def _cientos(n):
    if n == 0:  return ""
    if n == 100: return "CIEN"
    c, r = divmod(n, 100)
    out = CEN[c]
    if r:
        if r <= 20:                out += " " + UNI[r]
        elif r < 30:               out += " VEINTI" + UNI[r - 20].lower().upper()
        else:
            d, u = divmod(r, 10)
            out += " " + DEC[d] + (" Y " + UNI[u] if u else "")
    return out.strip()


def numero_letra(monto):
    ent = int(monto); cent = int(round((monto - ent) * 100))
    if ent == 0: pal = "CERO"
    else:
        mill, resto = divmod(ent, 1_000_000)
        mil,  uni   = divmod(resto, 1000)
        partes = []
        if mill:
            partes.append("UN MILLON" if mill == 1 else _cientos(mill) + " MILLONES")
        if mil:
            partes.append("MIL" if mil == 1 else _cientos(mil) + " MIL")
        if uni:
            partes.append(_cientos(uni))
        pal = " ".join(partes)
    return f"{pal} PESOS {cent:02d}/100 M.N."


def money(v):
    return f"${v:,.2f}"


def b64(path):
    p = pathlib.Path(path)
    if not p.is_absolute(): p = ASSETS / p
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


# ---- BLOQUES -----------------------------------------------------------------
def b_tabla(b):
    cols = b["columnas"]
    anchos = b.get("anchos") or [None] * len(cols)
    th = ""
    for i, c in enumerate(cols):
        cls = "num" if i == len(cols) - 1 else ""
        sty = " style='width:%s'" % anchos[i] if anchos[i] else ""
        th += "<th class='%s'%s>%s</th>" % (cls, sty, c)
    rows = ""
    for r in b["filas"]:
        tds = ""
        for i, c in enumerate(r):
            cls = "price" if i == len(cols) - 1 else ""
            if isinstance(c, dict):
                c = f"<b>{c['titulo']}</b><span class='sub'>{c.get('subtitulo','')}</span>"
            tds += f"<td class='{cls}'>{c}</td>"
        rows += f"<tr>{tds}</tr>"
    pie = f"<p class='pie'>{b['pie']}</p>" if b.get("pie") else ""
    return f"<table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table>{pie}"


def b_conceptos(b):
    eb = f"<p class='eyebrow'>{b['eyebrow']}</p>" if b.get("eyebrow") else ""
    sb = f"<div class='banda'>{b['subtitulo']}</div>" if b.get("subtitulo") else ""
    it = "".join(f"<div class='item'><b>{i['titulo']}</b><p>{i['texto']}</p></div>"
                 for i in b.get("items", []))
    return f"{eb}{sb}{it}"


def b_totales(b):
    fl = "".join(f"<div class='trow'><span>{l}</span><span>{money(v)}</span></div>"
                 for l, v in b["lineas"])
    return (f"<div class='tot-wrap'>{fl}"
            f"<div class='trow total'><span>TOTAL</span><span>{money(b['total'])}</span></div></div>")


def b_importe(b):
    return f"<div class='caja'><b>Importe con letra:</b> {b['texto']}</div>"


def b_nota(b):
    t = f"<b>{b['titulo']}</b><br>" if b.get("titulo") else ""
    return f"<div class='caja'>{t}{b['texto']}</div>"


def b_specs(b):
    rows = "".join(f"<div class='spec'><span class='sl'>{l}</span>"
                   f"<span class='sv'>{v}</span></div>" for l, v in b["pares"])
    t = f"<p class='eyebrow'>{b['titulo']}</p>" if b.get("titulo") else ""
    return f"{t}<div class='caja specs'>{rows}</div>"


def b_terminos(b):
    li = "".join(f"<li>{x}</li>" for x in b["puntos"])
    return (f"<div class='caja terms'><p class='tt'>{b.get('titulo','Términos y condiciones')}</p>"
            f"<ul>{li}</ul></div>")


BLOQUES = {"tabla": b_tabla, "conceptos": b_conceptos, "totales": b_totales,
           "importe_letra": b_importe, "nota": b_nota, "specs": b_specs, "terminos": b_terminos}


def build(d):
    cli = d["cliente"]
    logo_cli = (f"<span class='sep'>×</span><img class='lc' src='{b64(cli['logo'])}'>"
                if cli.get("logo") else "")
    suf = f" · {d['sufijo'].upper()}" if d.get("sufijo") else ""
    cuerpo = "".join(f"<section>{BLOQUES[b['tipo']](b)}</section>" for b in d["bloques"])
    dir_cli = "<br>".join(cli.get("direccion", []))

    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>
@page {{ size: Letter; margin: 42pt 46pt 56pt 46pt;
  @bottom-left  {{ content: "connectia"; font-family: Inter; font-weight: 800;
                   font-size: 9pt; color: {ACCENT}; width: 50%; text-align: left;
                   border-top: 1.2pt solid {ACCENT}; padding-top: 7pt;
                   vertical-align: top; white-space: nowrap; }}
  @bottom-right {{ content: "everything is connected — Página " counter(page) "/" counter(pages);
                   font-family: Inter; font-size: 7.5pt; color: {GRAY}; width: 50%;
                   text-align: right; border-top: 1.2pt solid {ACCENT}; padding-top: 8.5pt;
                   vertical-align: top; white-space: nowrap; }} }}
* {{ box-sizing: border-box; }}
body {{ font-family: Inter, "DejaVu Sans", sans-serif; font-size: 8.6pt;
        color: {TEXT}; line-height: 1.45; margin: 0; }}
.wm {{ position: fixed; top: 44%; left: 14%; width: 72%; opacity: .055;
       transform: rotate(-24deg); z-index: -1; }}
header {{ display: flex; justify-content: space-between; align-items: flex-start;
          background: #FFF; padding-bottom: 12pt; border-bottom: 1px solid {RULE}; }}
.logos {{ display: flex; align-items: center; gap: 10pt; }}
.lp {{ height: 30px; }} .lc {{ height: 34px; }}
.sep {{ color: {GRAY}; font-size: 13pt; font-weight: 300; }}
.emisor {{ text-align: right; font-size: 7.2pt; color: {GRAY}; line-height: 1.5; }}
.cliente {{ text-align: right; margin: 12pt 0 4pt; font-size: 8pt; color: {GRAY}; }}
.cliente b {{ color: {TEXT}; font-size: 9pt; display: block; margin-bottom: 1pt; }}
h1 {{ color: {ACCENT}; font-size: 21pt; font-weight: 800; margin: 14pt 0 12pt;
      letter-spacing: -.4pt; }}
.meta {{ display: flex; background: {META_BG}; border-radius: 4px; padding: 8pt 12pt;
         margin-bottom: 16pt; }}
.meta div {{ flex: 1; }}
.meta .ml {{ color: {ACCENT}; font-size: 6.6pt; font-weight: 700;
             letter-spacing: .7pt; text-transform: uppercase; display: block; }}
.meta .mv {{ font-size: 8.6pt; font-weight: 600; }}
section {{ margin-bottom: 15pt; break-inside: avoid; }}
table {{ width: 100%; border-collapse: collapse; }}
th {{ background: {ACCENT}; color: #FFF; font-size: 6.8pt; font-weight: 700;
      letter-spacing: .6pt; text-transform: uppercase; padding: 7pt 9pt; text-align: left; }}
th.num {{ text-align: right; }}
th {{ white-space: nowrap; }}
td {{ padding: 8pt 9pt; border-bottom: 1px solid {RULE}; vertical-align: top; font-size: 8.4pt; }}
td.price {{ text-align: right; color: {ACCENT}; font-weight: 700; white-space: nowrap; }}
td .sub {{ display: block; color: {GRAY}; font-size: 7.4pt; margin-top: 2pt; }}
.pie {{ font-style: italic; color: {GRAY}; font-size: 7.4pt; margin: 6pt 0 0; }}
.eyebrow {{ color: {ACCENT}; font-size: 6.8pt; font-weight: 700; letter-spacing: 1pt;
            text-transform: uppercase; margin: 0 0 6pt; }}
.banda {{ background: {LAV_SOFT}; padding: 6pt 10pt; font-weight: 700; font-size: 8.8pt;
          border-radius: 3px; margin-bottom: 8pt; }}
.item {{ margin-bottom: 7pt; }} .item p {{ margin: 1pt 0 0; color: #444; }}
.caja {{ background: {LAV_SOFT}; padding: 10pt 12pt; border-radius: 5px; font-size: 8.2pt; }}
.caja.terms {{ background: {LAV_TERMS}; }}
.caja.terms .tt {{ color: {ACCENT}; font-weight: 700; font-size: 8.4pt; margin: 0 0 6pt; }}
.caja.terms ul {{ margin: 0; padding-left: 12pt; }}
.caja.terms li {{ margin-bottom: 3.5pt; }}
.caja.terms li::marker {{ color: {ACCENT}; }}
.specs {{ display: flex; flex-wrap: wrap; }}
.spec {{ width: 50%; padding: 2.5pt 0; }}
.sl {{ color: {ACCENT}; font-weight: 700; font-size: 6.8pt; letter-spacing: .5pt;
       text-transform: uppercase; display: block; }}
.sv {{ font-size: 8.4pt; }}
.tot-wrap {{ width: 56%; margin-left: auto; }}
.trow {{ display: flex; justify-content: space-between; padding: 5pt 12pt;
         border-bottom: 1px solid {RULE}; font-size: 8.6pt; }}
.trow.total {{ background: {ACCENT}; color: #FFF; font-weight: 700; font-size: 14pt;
               font-style: normal; border: 0; border-radius: 4px; padding: 9pt 12pt;
               margin-top: 5pt; }}
</style></head><body>
<img class="wm" src="{b64('connectia-gray.png')}">
<header>
  <div class="logos"><img class="lp" src="{b64('connectia-purple.png')}">{logo_cli}</div>
  <div class="emisor">{EMISOR}</div>
</header>
<div class="cliente"><b>{cli['razon_social']}</b>{dir_cli}</div>
<h1>Cotización {d['folio']}{suf}</h1>
<div class="meta">
  <div><span class="ml">Su referencia</span><span class="mv">{d['referencia']}</span></div>
  <div><span class="ml">Fecha de la cotización</span><span class="mv">{d['fecha']}</span></div>
  <div><span class="ml">Vigencia</span><span class="mv">{d['vigencia']}</span></div>
</div>
{cuerpo}
</body></html>"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("uso: generate_cotizador.py contenido.json salida.pdf")
    from weasyprint import HTML
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    HTML(string=build(data), base_url=str(BASE)).write_pdf(sys.argv[2])
    print(f"PDF generado: {sys.argv[2]}")
