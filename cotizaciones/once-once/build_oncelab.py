#!/usr/bin/env python3
"""Cotizaciones once once LAB — plantilla oficial (misma que COT-2026-0162..0170).

El diseño es el de las cotizaciones previas de once LAB en Drive; sólo cambia el
contenido. Uso:
    python3 build_oncelab.py && NODE_PATH=/opt/node22/lib/node_modules node render.js
"""
import base64
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode((HERE / path).read_bytes()).decode()


LOGO = b64("img/oncelab-logo.png", "image/png")
# Datos de pago fuera del repo: copiar pago.example.json a pago.json y llenarlo.
PAGO = json.loads((HERE / "pago.json").read_text(encoding="utf-8"))
def _face(fam, w):
    src = b64("fonts/%s-%d.ttf" % (fam.replace(" ", ""), w), "font/ttf")
    return "@font-face{font-family:'%s';font-weight:%d;font-style:normal;src:url(%s) format('truetype')}\n" % (fam, w, src)


FONT_FACES = "".join(
    _face(fam, w)
    for fam, w in [("Archivo", 500), ("Archivo", 600), ("Archivo", 700),
                   ("Instrument Sans", 400), ("Instrument Sans", 500),
                   ("IBM Plex Mono", 400), ("IBM Plex Mono", 500)]
)

# CSS idéntico al de COT-2026-0164.html (plantilla once LAB); sólo se embeben las fuentes.
CSS = """
@page{size:letter;margin:11mm}*{box-sizing:border-box}
:root{--pink:#F0246B;--cream:#F0E7D3;--ink:#241f22;--muted:#8a8177;--line:#e7ddca;--card:#fffdf9}
html,body{margin:0}
body{color:var(--ink);font-family:'Instrument Sans',system-ui,sans-serif;font-size:12px;background:#fff}
.sheet{max-width:820px;margin:0 auto;padding:4px}
.top{display:flex;justify-content:space-between;align-items:flex-start;padding-bottom:12px;border-bottom:3px solid var(--pink)}
.top img{height:52px}.top .r{text-align:right}
h1{font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;font-weight:700;font-size:26px;margin:0}
.top .meta{color:var(--muted);font-size:12px;line-height:1.6;margin-top:4px}.top .meta b{color:var(--ink)}
.info{display:flex;gap:34px;padding:12px 0;color:var(--muted);font-size:12px}
.info b{color:var(--ink);display:block;font-size:10px;letter-spacing:.09em;text-transform:uppercase;margin-bottom:2px}
.info .cli{color:var(--ink);font-weight:600;font-size:14px}
table{width:100%;border-collapse:collapse;margin:4px 0}
th{background:var(--cream);text-align:left;white-space:nowrap;padding:8px 10px;font-family:Archivo;font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:#6a6258}
th.n,td.n{text-align:right}
td{padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:middle}
.pc{display:flex;gap:10px;align-items:center}
.pc img{width:40px;height:50px;object-fit:contain;border-radius:6px}
.pc span{font-weight:600}
.pc small{display:block;font-weight:400;color:var(--muted);font-size:11px;margin-top:2px}
.bot{display:flex;justify-content:space-between;align-items:flex-start;margin-top:10px;gap:24px}
.terms{color:var(--muted);font-size:11px;line-height:1.6;max-width:60%}.terms b{color:var(--ink)}
.tot{width:250px}
.tot div{display:flex;justify-content:space-between;padding:5px 0;color:var(--muted)}
.tot .g{border-top:2px solid var(--ink);margin-top:4px;padding-top:9px;color:var(--ink);font-family:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,serif;font-weight:700;font-size:17px}
.tot .g span:last-child{color:var(--pink)}
.wm{text-align:center;color:#bcae97;font-size:10px;letter-spacing:.2em;text-transform:uppercase;margin-top:14px}
.pay{margin-top:16px;border:1px solid var(--line);background:var(--card);border-radius:8px;padding:11px 14px}
.pay b{display:block;font-family:Archivo;font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:#6a6258;margin-bottom:7px}
.pay .rows{display:flex;gap:30px}
.pay .rows div{font-size:12px;color:var(--ink);font-weight:600}
.pay .rows span.k{display:block;font-size:9.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);font-weight:400;margin-bottom:1px}
.pay .clabe{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace;letter-spacing:.04em}
.badge{display:inline-block;background:var(--pink);color:#fff;font-family:Archivo;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:3px 9px;border-radius:99px;margin-top:6px}
"""

IVA = 0.16


def money(x):
    return f"${x:,.2f}"


def render(d):
    rows = ""
    subtotal = 0
    for r in d["rows"]:
        imp = r["qty"] * r["unit"]
        subtotal += imp
        sub = f"<small>{r['sub']}</small>" if r.get("sub") else ""
        rows += (f'<tr><td><div class="pc"><span>{r["name"]}{sub}</span></div></td>'
                 f'<td>{r["med"]}</td><td>{r["proc"]}</td><td class="n">{r["qty"]}</td>'
                 f'<td class="n"><b>{money(r["unit"])}</b></td><td class="n"><b>{money(imp)}</b></td></tr>')
    iva = subtotal * IVA
    total = subtotal + iva
    return f"""<!doctype html><meta charset="utf-8">
<title>Cotización {d['folio']} — once LAB</title>
<style>{FONT_FACES}{CSS}</style>
<div class="sheet">
  <div class="top">
    <img src="{LOGO}">
    <div class="r">
      <h1>Cotización</h1>
      <div class="meta"><b>Folio:</b> {d['folio']} · <b>Fecha:</b> {d['fecha']}<br><b>Vigencia:</b> 15 días naturales</div>
    </div>
  </div>
  <div class="info">
    <div><b>Para</b><span class="cli">El Plan de Juego · Speaker Tour 2026</span><br><span style='font-size:12px;color:#8a8177'>{d['ref']}</span></div>
    <div><b>De</b>once LAB · Piezas de diseño bajo pedido</div>
    <div><b>Contacto</b>hola@once-lab.mx · CDMX</div>
  </div>
  <table>
    <thead><tr><th>Producto</th><th>Medidas</th><th>Proceso</th><th class="n">Cant.</th><th class="n">P. unitario</th><th class="n">Importe</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="bot">
    <div class="terms"><b>Condiciones.</b> {d['terms']}<br><br><b>once LAB — lo hacemos realidad.</b></div>
    <div class="tot">
      <div><span>Subtotal</span><span>{money(subtotal)}</span></div>
      <div><span>IVA 16%</span><span>{money(iva)}</span></div>
      <div class="g"><span>Total</span><span>{money(total)}</span></div>
    </div>
  </div>
  <div class="pay"><b>Datos de pago</b><div class="rows">
    <div><span class="k">Beneficiario</span>{PAGO['beneficiario']}</div>
    <div><span class="k">Institución</span>{PAGO['institucion']}</div>
    <div><span class="k">CLABE interbancaria</span><span class="clabe">{PAGO['clabe']}</span></div>
  </div></div>
  <div class="wm">once once LAB · {d['folio']}</div>
</div>
"""


DOCS = [
    {
        "file": "COT-2026-0171",
        "folio": "COT-2026-0171",
        "fecha": "07-sep-2026",
        "ref": "Portacelular 3D · diseño personalizado · precio por unidad",
        "rows": [
            {"name": "Portacelular 3D personalizado · unidad completa",
             "sub": "Pieza impresa en 3D, empaque individual y gestión del proyecto incluidos",
             "med": "140 × 70 × 60 mm", "proc": "Impresión 3D", "qty": 1, "unit": 139.00},
        ],
        "terms": ("Precios en MXN. <b>Precio por unidad completa: $139.00</b> más IVA, con empaque individual "
                  "y gestión del proyecto ya incluidos; válido para lote de 200 piezas. Producción sobre pedido: "
                  "<b>50% de anticipo</b> para arrancar y saldo contra entrega. PLA mate de alta resistencia, "
                  "acabado texturizado, ranura antideslizante, compatible con la mayoría de smartphones. "
                  "Color azul marino (gris piedra como alternativa). Se entrega <b>muestra física para aprobación</b> "
                  "antes de liberar la producción. Artes finales y aprobación de claims por cuenta del cliente. "
                  "No incluye envío."),
    },
    {
        "file": "COT-2026-0172",
        "folio": "COT-2026-0172",
        "fecha": "07-sep-2026",
        "ref": "Kit de mesa · Equipo Técnico · precio por unidad",
        "rows": [
            {"name": "Kit de mesa Equipo Técnico · unidad completa",
             "sub": "Tablero táctico 3D + 5 fichas 3D + identificador DT 3D + folder + block + pluma grabada + postal, estuchado",
             "med": "Tablero 450 × 300 mm · 6 módulos", "proc": "3D + impresos", "qty": 1, "unit": 800.00},
        ],
        "terms": ("Precios en MXN. <b>Precio por kit completo: $800.00</b> más IVA, con empaque, estuchado y gestión "
                  "del proyecto ya incluidos; válido para lote de 200 kits. Producción sobre pedido: "
                  "<b>50% de anticipo</b> para arrancar y saldo contra entrega. Piezas 3D en PLA mate de alta "
                  "resistencia, acabado texturizado; el tablero se entrega en 6 módulos ensamblables sin herramienta. "
                  "Los impresos y la pluma se producen con proveedor externo bajo especificación de once LAB. "
                  "Se entrega <b>muestra física del kit para aprobación</b> antes de liberar la producción. "
                  "Artes finales, validación médica y aprobación de claims por cuenta del cliente. No incluye envío."),
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
