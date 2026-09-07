#!/usr/bin/env python3
"""Genera las dos cotizaciones para Once Once (HTML autocontenido, Letter).

Uso:  python3 build.py            -> escribe *.html en ./out
      node render.js              -> convierte cada HTML a PDF
"""
import base64
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode((HERE / path).read_bytes()).decode()


FONTS = {
    "bebas": b64("fonts/BebasNeue-400.ttf", "font/ttf"),
    "m400": b64("fonts/Montserrat-400.ttf", "font/ttf"),
    "m500": b64("fonts/Montserrat-500.ttf", "font/ttf"),
    "m600": b64("fonts/Montserrat-600.ttf", "font/ttf"),
    "m700": b64("fonts/Montserrat-700.ttf", "font/ttf"),
    "m800": b64("fonts/Montserrat-800.ttf", "font/ttf"),
}
LOGO = b64("img/connectia-white.png", "image/png")
LOGO_FOOT = b64("img/connectia-purple.png", "image/png")

IVA = 0.16


def money(x):
    return f"${x:,.2f}"


def importe_letra(total):
    """Importe con letra en pesos mexicanos (suficiente hasta millones)."""
    unidades = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE",
                "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", "DIECISIETE",
                "DIECIOCHO", "DIECINUEVE", "VEINTE", "VEINTIUN", "VEINTIDÓS", "VEINTITRÉS",
                "VEINTICUATRO", "VEINTICINCO", "VEINTISÉIS", "VEINTISIETE", "VEINTIOCHO", "VEINTINUEVE"]
    decenas = ["", "", "", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", "SETENTA", "OCHENTA", "NOVENTA"]
    centenas = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]

    def hasta_999(n):
        if n == 0:
            return ""
        if n == 100:
            return "CIEN"
        s = centenas[n // 100]
        r = n % 100
        if r < 30:
            s += (" " if s else "") + unidades[r] if r else ""
        else:
            s += (" " if s else "") + decenas[r // 10]
            if r % 10:
                s += " Y " + unidades[r % 10]
        return s.strip()

    entero = int(total)
    cent = int(round((total - entero) * 100))
    if cent == 100:
        entero, cent = entero + 1, 0
    miles, resto = divmod(entero, 1000)
    partes = []
    if miles == 1:
        partes.append("MIL")
    elif miles > 1:
        partes.append(hasta_999(miles) + " MIL")
    if resto:
        partes.append(hasta_999(resto))
    txt = " ".join(partes) or "CERO"
    return f"{txt} PESOS {cent:02d}/100 M.N."


CSS = """
@font-face{font-family:'Bebas Neue';src:url(__bebas__) format('truetype');font-weight:400}
@font-face{font-family:'Montserrat';src:url(__m400__) format('truetype');font-weight:400}
@font-face{font-family:'Montserrat';src:url(__m500__) format('truetype');font-weight:500}
@font-face{font-family:'Montserrat';src:url(__m600__) format('truetype');font-weight:600}
@font-face{font-family:'Montserrat';src:url(__m700__) format('truetype');font-weight:700}
@font-face{font-family:'Montserrat';src:url(__m800__) format('truetype');font-weight:800}
:root{
  --navy:#182340; --navy2:#22304F; --gold:#C9A961; --gold2:#E6CF86; --cream:#F4EFE3;
  --cream2:#EAE3D2; --ink:#1B1B1B; --gray:#6B6F7A; --line:#D9D3C4;
}
*{box-sizing:border-box;margin:0;padding:0}
@page{size:Letter;margin:0}
html,body{width:8.5in;height:11in;background:#fff;color:var(--ink);
  font-family:'Montserrat',Helvetica,Arial,sans-serif;font-size:9.5pt;line-height:1.4;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{position:relative;width:8.5in;height:11in;overflow:hidden;display:flex;flex-direction:column}
.display{font-family:'Bebas Neue','Montserrat',sans-serif;font-weight:400;letter-spacing:.02em}

/* ---------- header ---------- */
.hero{background:var(--navy);color:#fff;padding:.42in .55in .34in;position:relative;overflow:hidden}
.hero svg.tactics{position:absolute;right:-.7in;top:1.05in;width:4.6in;height:2.6in;opacity:.42}
.hero .row{display:flex;justify-content:space-between;align-items:flex-start;position:relative}
.hero .eyebrow{color:var(--gold);font-size:8pt;font-weight:700;letter-spacing:.28em;text-transform:uppercase}
.hero h1{font-size:40pt;line-height:.92;margin-top:.08in;color:#fff}
.hero h1 em{font-style:normal;color:var(--gold)}
.hero .sub{margin-top:.1in;font-size:9pt;color:#D9DCE6;max-width:4.4in}
.hero .brand{text-align:right;position:relative;z-index:2}
.hero .brand img{height:.36in;display:block;margin-left:auto}
.hero .brand .addr{margin-top:.08in;font-size:7pt;color:#B9BFCF;line-height:1.45}
.goldrule{height:3px;background:linear-gradient(90deg,var(--gold),var(--gold2) 60%,var(--gold))}

/* ---------- meta band ---------- */
.meta{display:grid;grid-template-columns:1.7fr 1fr 1fr 1fr;background:var(--cream);
  padding:.14in .55in;border-bottom:1px solid var(--line)}
.meta div+div{border-left:1px solid var(--line);padding-left:.18in;margin-left:.18in}
.meta .k{font-size:6.8pt;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--navy2)}
.meta .v{font-size:9.5pt;font-weight:600;margin-top:2px}
.meta .v small{display:block;font-weight:400;font-size:8pt;color:var(--gray)}

/* ---------- body ---------- */
.body{padding:.28in .55in 0;flex:1;display:flex;flex-direction:column;gap:.2in}
.intro{display:grid;grid-template-columns:2.85in 1fr;gap:.3in;align-items:stretch}
.render{border:2px solid var(--gold);padding:5px;background:#fff;position:relative}
.render img{width:100%;display:block}
.render .tag{position:absolute;left:-2px;top:-2px;background:var(--gold);color:var(--navy);
  font-size:6.5pt;font-weight:800;letter-spacing:.2em;text-transform:uppercase;padding:3px 8px}
.desc h2{font-size:20pt;color:var(--navy);line-height:1}
.desc p{margin-top:.08in;font-size:9pt;color:#3A3D46}
.desc ul{margin-top:.1in;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:4px 12px}
.desc li{font-size:8.4pt;padding-left:12px;position:relative;color:#2E3140}
.desc li:before{content:"";position:absolute;left:0;top:6px;width:6px;height:6px;background:var(--gold);transform:rotate(45deg)}

table{width:100%;border-collapse:collapse}
thead th{background:var(--navy);color:#fff;font-size:7pt;font-weight:700;letter-spacing:.18em;
  text-transform:uppercase;padding:7px 10px;text-align:left}
thead th.r,td.r{text-align:right}
tbody td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top;font-size:9pt}
tbody td .t{font-weight:700;color:var(--navy)}
tbody td .s{display:block;font-size:8pt;color:var(--gray);margin-top:2px}
tbody td.price{color:var(--navy);font-weight:700;white-space:nowrap}
tbody tr.once td{background:#FBF9F3}
.pill{display:inline-block;border:1px solid var(--gold);color:var(--navy);font-size:6.5pt;font-weight:700;
  letter-spacing:.12em;text-transform:uppercase;padding:2px 6px;margin-left:6px;vertical-align:middle}

.bottom{display:grid;grid-template-columns:1fr 2.6in;gap:.3in;align-items:start}
.notes{background:var(--cream);padding:.16in .2in;border-left:3px solid var(--gold)}
.notes h3{font-size:7pt;letter-spacing:.22em;text-transform:uppercase;color:var(--navy2);margin-bottom:6px}
.notes li{font-size:8pt;margin-left:12px;margin-bottom:3px;color:#2E3140}
.notes li::marker{color:var(--gold)}
.totals{border:1px solid var(--line)}
.totals .ln{display:flex;justify-content:space-between;padding:7px 12px;font-size:9pt;border-bottom:1px solid var(--line)}
.totals .ln span:last-child{font-weight:600}
.totals .tot{background:var(--navy);color:#fff;padding:10px 12px;display:flex;justify-content:space-between;align-items:baseline}
.totals .tot .l{font-size:7pt;letter-spacing:.22em;text-transform:uppercase;color:var(--gold)}
.totals .tot .n{font-size:18pt;font-weight:800}
.totals .letra{font-size:7pt;color:var(--gray);padding:6px 12px;line-height:1.35}
.totals .setup{background:#FBF9F3;border-top:1px solid var(--line);padding:8px 12px}
.totals .sl{font-size:7pt;color:var(--gray);line-height:1.35}
.totals .sa{font-size:11pt;font-weight:800;color:var(--navy);margin-top:2px}
.totals .sa small{font-size:7pt;font-weight:600;color:var(--gray)}

/* ---------- footer ---------- */
.foot{margin-top:auto;padding:.14in .55in .3in;display:flex;justify-content:space-between;align-items:center;
  border-top:1px solid var(--line);font-size:7pt;color:var(--gray)}
.foot .wm img{height:.3in;display:block}
.foot .wm{line-height:1}
.foot .wm small{display:block;font-size:6.5pt;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-top:4px}
.foot .fine{text-align:right;line-height:1.5}
.watermark{position:absolute;left:50%;top:58%;transform:translate(-50%,-50%) rotate(-24deg);
  font-family:'Bebas Neue';font-size:96pt;color:var(--navy);opacity:.035;white-space:nowrap;pointer-events:none;letter-spacing:.05em}
"""

TACTICS = """
<svg class="tactics" viewBox="0 0 440 250" fill="none" stroke="#C9A961" stroke-width="1.6" stroke-linecap="round">
  <rect x="40" y="20" width="380" height="210" rx="4" stroke-opacity=".7"/>
  <line x1="230" y1="20" x2="230" y2="230" stroke-opacity=".7"/>
  <circle cx="230" cy="125" r="34" stroke-opacity=".7"/>
  <rect x="40" y="70" width="70" height="110" stroke-opacity=".7"/>
  <rect x="350" y="70" width="70" height="110" stroke-opacity=".7"/>
  <path d="M90 200 C140 150 170 160 205 110" stroke-dasharray="4 5"/>
  <path d="M205 110 l-9 -2 m9 2 l-2 9"/>
  <path d="M150 60 C190 90 240 70 300 95" stroke-dasharray="4 5"/>
  <path d="M300 95 l-9 1 m9 -1 l-5 8"/>
  <path d="M120 100 l12 12 m0 -12 l-12 12 M270 170 l12 12 m0 -12 l-12 12 M330 60 l12 12 m0 -12 l-12 12 M180 190 l12 12 m0 -12 l-12 12"/>
  <circle cx="300" cy="140" r="6"/><circle cx="360" cy="110" r="6"/><circle cx="110" cy="150" r="6"/>
</svg>
"""


def css_with_fonts():
    css = CSS
    for k, v in FONTS.items():
        css = css.replace(f'__{k}__', v)
    return css


def render(doc):
    subtotal = sum(r["qty"] * r["unit"] for r in doc["rows"])
    iva = subtotal * IVA
    total = subtotal + iva
    rows = ""
    for r in doc["rows"]:
        pill = f'<span class="pill">{r["pill"]}</span>' if r.get("pill") else ""
        rows += f"""
        <tr class="{r.get('cls','')}">
          <td><span class="t">{r['title']}</span>{pill}<span class="s">{r['sub']}</span></td>
          <td class="r">{r['qty']}</td>
          <td class="r">{money(r['unit'])}</td>
          <td class="r price">{money(r['qty']*r['unit'])}</td>
        </tr>"""
    setup = ""
    if doc.get("setup"):
        s = doc["setup"]
        setup = f"""<div class="setup"><div class="sl">{s['label']}</div><div class="sa">{money(s['amount'])} <small>+ IVA</small></div></div>"""
    bullets = "".join(f"<li>{b}</li>" for b in doc["incluye"])
    notes = "".join(f"<li>{n}</li>" for n in doc["notas"])
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>{doc['folio']} · {doc['titulo_plano']}</title><style>{css_with_fonts()}</style></head>
<body><div class="page">
  <div class="watermark">EL PLAN DE JUEGO</div>
  <div class="hero">{TACTICS}
    <div class="row">
      <div>
        <div class="eyebrow">Cotización · {doc['folio']}</div>
        <h1 class="display">{doc['titulo']}</h1>
        <div class="sub">{doc['subtitulo']}</div>
      </div>
      <div class="brand">
        <img src="{LOGO}" alt="connectia">
        <div class="addr">Facilitadores Publicitarios HS, S.A. de C.V.<br>Hacienda de Temoluco 130, Villaquietud<br>Coyoacán, CDMX · C.P. 04960</div>
      </div>
    </div>
  </div>
  <div class="goldrule"></div>
  <div class="meta">
    <div><div class="k">Preparada para</div><div class="v">Once Once · Agencia Creativa<small>Av. Paseo de la Reforma 389, Cuauhtémoc, CDMX</small></div></div>
    <div><div class="k">Fecha</div><div class="v">{doc['fecha']}</div></div>
    <div><div class="k">Vigencia</div><div class="v">15 días naturales</div></div>
    <div><div class="k">Moneda</div><div class="v">MXN + IVA</div></div>
  </div>

  <div class="body">
    <div class="intro">
      <div class="render"><span class="tag">Referencia visual</span><img src="{doc['img']}" alt=""></div>
      <div class="desc">
        <h2 class="display">{doc['h2']}</h2>
        <p>{doc['parrafo']}</p>
        <ul>{bullets}</ul>
      </div>
    </div>

    <table>
      <thead><tr><th style="width:62%">Concepto</th><th class="r">Cant.</th><th class="r">P. unitario</th><th class="r">Importe</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>

    <div class="bottom">
      <div class="notes"><h3>Condiciones</h3><ul>{notes}</ul></div>
      <div class="totals">
        <div class="ln"><span>Subtotal</span><span>{money(subtotal)}</span></div>
        <div class="ln"><span>IVA 16 %</span><span>{money(iva)}</span></div>
        <div class="tot"><span class="l">Total unitario</span><span class="n">{money(total)}</span></div>
        <div class="letra">{importe_letra(total)}</div>
        {setup}
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="wm"><img src="{LOGO_FOOT}" alt="connectia"><small>everything is connected</small></div>
    <div class="fine">Visualización preliminar sujeta a validación de artes finales de marca.<br>Precios en pesos mexicanos, más IVA. · Página 1/1</div>
  </div>
</div></body></html>"""
    return html


DOCS = [
    {
        "file": "COT-OO-2026-01_portacelular-3d",
        "folio": "OO-2026-01",
        "fecha": "7 sep 2026",
        "titulo": "Portacelular 3D<br><em>El Plan de Juego</em>",
        "titulo_plano": "Portacelular 3D El Plan de Juego",
        "subtitulo": "Pieza exclusiva impresa en 3D para el kit de obsequio · diseño personalizado Indaflex IB.",
        "img": b64("img/portacelular.jpg", "image/jpeg"),
        "h2": "Una pieza, lista para entregar",
        "parrafo": "Portacelular impreso en 3D en PLA de alta resistencia, acabado mate texturizado, con cancha táctica y leyenda en dorado al frente y marca Indaflex IB en la cara trasera. Ranura antideslizante, compatible con la mayoría de los smartphones.",
        "incluye": [
            "Medidas aprox. 14 × 7 × 6 cm",
            "Azul marino principal · gris piedra opcional",
            "Impresión bicolor integrada (sin calcomanías)",
            "Revisión de calidad pieza por pieza",
            "Empaque individual protector",
            "Fabricado bajo demanda",
        ],
        "rows": [
            {"title": "Portacelular 3D personalizado · unidad completa", "pill": "Por unidad",
             "sub": "Pieza terminada en PLA mate, dos colores, con arte El Plan de Juego / Indaflex IB. Precio unitario para tiraje mínimo de 20 piezas.",
             "qty": 1, "unit": 449.00},
        ],
        "setup": {"label": "Desarrollo del modelo 3D y prototipo aprobado (cargo único por proyecto)", "amount": 2500.00},
        "notas": [
            "Precio por unidad; el cargo único de desarrollo se cobra una sola vez por proyecto.",
            "Producción: hasta 100 piezas en 7 días hábiles a partir del prototipo aprobado.",
            "Forma de pago: 50 % al confirmar, 50 % antes de salida a producción.",
            "Entrega en CDMX incluida; foráneos se cotizan por separado.",
        ],
    },
    {
        "file": "COT-OO-2026-02_kit-de-mesa-equipo-tecnico",
        "folio": "OO-2026-02",
        "fecha": "7 sep 2026",
        "titulo": "Kit de mesa<br><em>Equipo Técnico</em>",
        "titulo_plano": "Kit de mesa Equipo Técnico El Plan de Juego",
        "subtitulo": "Kit completo por mesa para El Plan de Juego · Speaker Tour 2026. Cada caso plantea un reto; cada decisión forma parte de una estrategia.",
        "img": b64("img/kit-mesa.jpg", "image/jpeg"),
        "h2": "Todo lo que lleva una mesa",
        "parrafo": "Unidad completa lista para colocar en mesa: tablero táctico rígido impreso en 3D, cinco fichas de jugador (una por producto), identificador del Director Técnico, folder del caso clínico, block de notas con pluma metálica grabada y postal de agradecimiento.",
        "incluye": [
            "Tablero / cancha táctica 3D · 45 × 30 cm",
            "5 fichas de jugador 3D con base",
            "Identificador DT 3D (tent card)",
            "Folder del caso impreso a color",
            "Block de notas + pluma metálica grabada",
            "Postal de agradecimiento impresa",
        ],
        "rows": [
            {"title": "Kit de mesa Equipo Técnico · unidad completa", "pill": "Por unidad",
             "sub": "Tablero 3D + 5 fichas 3D + identificador DT 3D + folder + block + pluma grabada + postal, ensamblado y revisado. Precio unitario para mínimo de 5 mesas.",
             "qty": 1, "unit": 3050.00},
        ],
        "setup": {"label": "Desarrollo de modelos 3D, artes de impresión y prototipo aprobado (cargo único)", "amount": 4500.00},
        "notas": [
            "Un kit equipa una mesa. Block, pluma y postal adicionales por participante: $215 + IVA por persona.",
            "Producción: hasta 10 kits en 8 días hábiles a partir del prototipo aprobado.",
            "Forma de pago: 50 % al confirmar, 50 % antes de salida a producción.",
            "Entrega en CDMX incluida; foráneos se cotizan por separado.",
        ],
    },
]

if __name__ == "__main__":
    manifest = []
    for d in DOCS:
        p = OUT / f"{d['file']}.html"
        p.write_text(render(d), encoding="utf-8")
        manifest.append(str(p))
        print("wrote", p)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
