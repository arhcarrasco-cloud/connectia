#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TARIFARIO · SITIOS SELECCIONADOS — Connectia
────────────────────────────────────────────
Arma Sitios-Connectia-Tarifario-Seleccion.pdf (9 pp, landscape letter) con el
look & feel Connectia: portada V10 sunset, resumen de tarifas y una ficha por
sitio. Tarifas de los sitios en catálogo tomadas de data/oportunidades.json;
Landmark Condesa y Taparrosca se capturan aquí porque no están publicados.

Uso:
    python3 build_tarifario.py
    chromium --headless --no-pdf-header-footer \
      --print-to-pdf=Sitios-Connectia-Tarifario-Seleccion.pdf file://$PWD/tarifario.html

Marca: Connectia Purple #872B90 · Indigo Deep #201040 · Lime #C8FF00 · Citrus #FF6A1A.
Tipografía: Coplette + Cooper Hewitt no están disponibles en este entorno de
build, por lo que se embebe Inter como FALLBACK TÉCNICO declarado.
"""
import base64, os, re, urllib.request

SCR  = os.path.dirname(os.path.abspath(__file__))   # SitiosConnectia/
SIT  = SCR
REPO = os.path.dirname(SCR)

def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()

LOGO_W = b64(os.path.join(REPO, "assets/logo/connectia-white.png"), "image/png")
LOGO_G = b64(os.path.join(REPO, "assets/logo/connectia-gray.png"),  "image/png")

def inter_css():
    """Embebe Inter (latin) en base64. Fallback técnico declarado: Coplette y
    Cooper Hewitt no están disponibles en este entorno de build."""
    cache = os.path.join(SCR, "inter-embed.css")
    if os.path.exists(cache):
        return open(cache).read()
    url = ("https://fonts.googleapis.com/css2?family=Inter:ital,wght@"
           "0,400;0,600;0,700;0,800;0,900;1,300&display=swap")
    ua = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    css = urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=30).read().decode()
    out = []
    for b in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        ur = re.search(r"unicode-range:\s*([^;]+);", b)
        if ur and not re.search(r"U\+0000-00FF", ur.group(1)) and not re.search(r"U\+0100-02", ur.group(1)):
            continue                                    # solo latin + latin-ext
        u = re.search(r"url\((https://[^)]+)\)", b).group(1)
        w = re.search(r"font-weight:\s*(\d+)", b).group(1)
        st = re.search(r"font-style:\s*(\w+)", b).group(1)
        data = urllib.request.urlopen(urllib.request.Request(u, headers=ua), timeout=30).read()
        out.append(f"@font-face{{font-family:'Inter';font-style:{st};font-weight:{w};"
                   f"font-display:block;src:url(data:font/woff2;base64,"
                   f"{base64.b64encode(data).decode()}) format('woff2');"
                   + (f"unicode-range:{ur.group(1)};" if ur else "") + "}")
    css_out = "\n".join(out)
    open(cache, "w").write(css_out)
    return css_out

FONTS = inter_css()

def foto(fid):
    p = os.path.join(SIT, "assets/sitios", fid + ".jpg")
    return b64(p, "image/jpeg") if os.path.exists(p) else None

def mxn(n): return "$" + format(int(n), ",d").replace(",", ",") if n else "Cotizar"

SITIOS = [
 dict(n="01", id="OPP-CUBO", cat="Landmark",
      titulo="CUBO DIGITAL MAGNOCENTRO", sub="Interlomas · Huixquilucan",
      ubic="Blvd. Magnocentro y Blvd. Interlomas", tarifa=1000000, imp="4.0 M",
      medidas="18.7 × 10 m · 4 caras · Cubo 360°", nse="ABC+", ilum="Sí", clas="AAA",
      obj="Naming del landmark + 3 lonas + 1 pantalla digital con exclusividad de categoría.",
      benef="Cubo 360° iluminado en el cruce de mayor flujo de Interlomas. Dominio total del punto: naming, tres lonas y una pantalla con dos slots.",
      zonas="Magnocentro 200 m · Interlomas 4 km · Bosques de las Lomas 4.3 km",
      web=True, foto=foto("OPP-CUBO"),
      afor="La marca aparece donde importa, no donde sobra."),
 dict(n="02", id="OPP-HAMB", cat="Landmark",
      titulo="LANDMARK HAMBURGO", sub="Col. Juárez · CDMX",
      ubic="Hamburgo esq. Florencia", tarifa=750000, imp="4.1 M",
      medidas="12.9 × 7.2 m · Pantalla LED", nse="C+ / C", ilum="No", clas="AAA",
      obj="Dominio digital 24/7 en el corredor cultural Reforma–Juárez.",
      benef="Presencia premium en el corredor Reforma–Juárez, con audiencia de alto valor y anclaje en C. Comercial Reforma 222.",
      zonas="Roma 500 m · Condesa 1 km · Buenavista 2.5 km",
      web=True, foto=foto("OPP-HAMB"),
      afor="La ciudad se convierte en el escenario de la marca."),
 dict(n="03", id="OPP-PANTALLAS", cat="Pantalla DOOH 3D",
      titulo="MULTINAMING · 6 PANTALLAS", sub="CDMX & AMCM · 6 ubicaciones",
      ubic="Interlomas · Magnocentro · Toreo · Churubusco · Viaducto · Revolución",
      tarifa=0, imp="19.7 M",
      medidas="6 pantallas LED · DOOH 3D · 2 spots c/u", nse="ABC+", ilum="Sí", clas="AAA",
      obj="Naming simultáneo en seis pantallas premium: dominio digital 24/7 en CDMX y AMCM.",
      benef="Un solo producto, seis presencias. La marca toma el naming de las 6 pantallas landmark al mismo tiempo, con arte 3D incluido y contenido pre-programado por día y hora.",
      zonas="Paseo Interlomas · Magnocentro × Interlomas · Periférico Toreo · Río Churubusco · Viaducto Miguel Alemán · Av. Revolución",
      web=True, foto=foto("OPP-PANTALLAS"),
      afor="No compramos inventario. Curamos presencia."),
 dict(n="04", id="OPP-MEGA", cat="Mega valla",
      titulo="SÚPER VALLA CHURUBUSCO", sub="Calz. de Tlalpan · Coyoacán",
      ubic="Calz. de Tlalpan esq. Río Churubusco", tarifa=630000, imp="1.2 M",
      medidas="108 × 3.05 m · Vinil / Lona", nse="C+ / C", ilum="No", clas="AAA",
      obj="Cobertura monumental de 108 metros continuos.",
      benef="La valla seguida más grande de CDMX: 108 m de dominio visual absoluto sobre uno de los cruces de mayor aforo vehicular del sur.",
      zonas="Coyoacán Centro 1.5 km · Ciudad de los Deportes 2 km · CDMX Centro 9 km",
      web=True, foto=foto("OPP-MEGA"),
      afor="La marca genera conversación, no solo mensajes."),
 dict(n="05", id="—", cat="Landmark",
      titulo="LANDMARK CONDESA", sub="Condesa · CDMX",
      ubic="Por confirmar", tarifa=750000, imp="—",
      medidas="Por confirmar", nse="ABC+", ilum="Por confirmar", clas="Por confirmar",
      obj="Landmark en el corredor de mayor consumo cultural de la ciudad.",
      benef="Sitio fuera del catálogo publicado. Tarifa confirmada por dirección comercial; ficha técnica, fotografía y disponibilidad se integran al catálogo en la siguiente actualización.",
      zonas="Condesa · Roma · Hipódromo",
      web=False, foto=None,
      afor="La marca habla el idioma de su audiencia."),
 dict(n="06", id="—", cat="Landmark",
      titulo="TAPARROSCA", sub="CDMX",
      ubic="Por confirmar", tarifa=450000, imp="—",
      medidas="Por confirmar", nse="Por confirmar", ilum="Por confirmar", clas="Por confirmar",
      obj="Landmark de estructura singular.",
      benef="Sitio fuera del catálogo publicado. Tarifa confirmada por dirección comercial; ficha técnica, fotografía y disponibilidad se integran al catálogo en la siguiente actualización.",
      zonas="Por confirmar",
      web=False, foto=None,
      afor="Out of Noise."),
]

TOTAL = sum(s["tarifa"] for s in SITIOS)

# ── constelación de la portada ──
DOTS = [(12,18,3),(21,64,2),(29,33,2),(35,79,3),(44,12,2),(52,71,2),(58,26,3),
        (66,58,2),(71,15,2),(78,74,3),(83,38,2),(88,63,2),(17,45,2),(40,52,2),
        (61,86,2),(93,24,2),(8,72,2),(74,44,2)]
def dots_html():
    h = "".join(f'<i style="left:{x}%;top:{y}%;width:{s}px;height:{s}px;opacity:{.55+ (i%4)*.15:.2f}"></i>'
                for i,(x,y,s) in enumerate(DOTS))
    h += '<i class="lime"  style="left:9%;top:88%;width:9px;height:9px"></i>'
    h += '<i class="citrus" style="left:91%;top:87%;width:9px;height:9px"></i>'
    h += '<i style="left:41%;top:31%;width:7px;height:7px;opacity:1"></i>'
    h += '<i style="left:59%;top:30%;width:6px;height:6px;opacity:1"></i>'
    return h

# ── páginas ──
def cover():
    return f"""
<section class="page cover">
  <div class="stars">{dots_html()}</div>
  <div class="chrome">
    <span class="eb">CONNECTIA · SITIOS SELECCIONADOS · TARIFARIO</span>
    <span class="eb">V1 · AGOSTO 2026</span>
  </div>
  <div class="cov-mid">
    <img class="cov-logo" src="{LOGO_W}" alt="connectia">
    <p class="cov-kicker">SEIS SITIOS · TARIFA MENSUAL · MXN SIN IVA</p>
  </div>
  <div class="cov-foot">
    <span class="slog"><em>everything is connected.</em></span>
    <span class="rs">Facilitadores Publicitarios HS, S.A. de C.V.</span>
  </div>
</section>"""

def resumen():
    rows = ""
    for s in SITIOS:
        badge = ('<span class="bdg ok">EN CATÁLOGO</span>' if s["web"]
                 else '<span class="bdg new">NO PUBLICADO</span>')
        tar = mxn(s["tarifa"])
        rows += f"""<tr>
          <td class="num">{s['n']}</td>
          <td class="ttl"><b>{s['titulo']}</b><span>{s['sub']}</span></td>
          <td class="cat">{s['cat']}</td>
          <td class="imp">{s['imp']}</td>
          <td class="st">{badge}</td>
          <td class="tar{' cot' if not s['tarifa'] else ''}">{tar}</td>
        </tr>"""
    return f"""
<section class="page dark">
  {chrome('RESUMEN DE TARIFAS','02')}
  <div class="body">
    <p class="eyebrow">01 · TARIFARIO</p>
    <h1>SITIOS SELECCIONADOS</h1>
    <table class="tbl">
      <thead><tr><th></th><th>SITIO</th><th>FORMATO</th><th>IMPACTOS / MES</th><th>ESTATUS</th><th class="r">TARIFA MENSUAL</th></tr></thead>
      <tbody>{rows}</tbody>
      <tfoot><tr class="tot"><td></td><td colspan="3">TOTAL · 5 SITIOS CON TARIFA CONFIRMADA</td><td class="mini">Multinaming a cotizar</td><td class="r">{mxn(TOTAL)}</td></tr></tfoot>
    </table>
    <p class="legal">Tarifas mensuales en MXN, sin IVA. Vigencia comercial 30 días. Disponibilidad sujeta a confirmación.
    Landmark Condesa y Taparrosca no figuran en el catálogo publicado en connectia.mx/SitiosConnectia; se integran a este tarifario por instrucción de dirección comercial.</p>
    <p class="afor"><em>No compramos inventario. Curamos presencia.</em></p>
  </div>
  {footer()}
</section>"""

def sitio(s, pg):
    if s["foto"]:
        media = f'<div class="ph" style="background-image:url({s["foto"]})"></div>'
    else:
        media = ('<div class="ph nofoto"><div class="nf">'
                 '<span class="nf-eb">SITIO NO PUBLICADO</span>'
                 '<span class="nf-t">FICHA EN INTEGRACIÓN</span>'
                 '<span class="nf-s">Fotografía, medidas y aforo pendientes<br>de alta en el catálogo</span>'
                 '</div></div>')
    badge = ('<span class="bdg ok">EN CATÁLOGO</span>' if s["web"]
             else '<span class="bdg new">NO PUBLICADO</span>')
    tar = mxn(s["tarifa"])
    return f"""
<section class="page dark sheet">
  {chrome(s['cat'].upper(), pg)}
  <div class="grid">
    <div class="left">{media}</div>
    <div class="right">
      <p class="eyebrow">{s['n']} · {s['cat'].upper()}</p>
      <h1 class="h-site">{s['titulo']}</h1>
      <p class="sub">{s['sub']}</p>
      <p class="ubic">{s['ubic']}</p>
      <div class="price">
        <span class="p-l">TARIFA MENSUAL</span>
        <span class="p-v{' cot' if not s['tarifa'] else ''}">{tar}<em>{' /mes' if s['tarifa'] else ''}</em></span>
        {badge}
      </div>
      <div class="specs">
        <div><span>MEDIDAS</span><b>{s['medidas']}</b></div>
        <div><span>IMPACTOS / MES</span><b>{s['imp']}</b></div>
        <div><span>NSE</span><b>{s['nse']}</b></div>
        <div><span>ILUMINACIÓN</span><b>{s['ilum']}</b></div>
        <div><span>CLASIFICACIÓN</span><b>{s['clas']}</b></div>
        <div class="wide"><span>ZONA DE INFLUENCIA</span><b>{s['zonas']}</b></div>
      </div>
      <p class="obj"><b>{s['obj']}</b></p>
      <p class="benef">{s['benef']}</p>
      <p class="afor"><em>{s['afor']}</em></p>
    </div>
  </div>
  {footer()}
</section>"""

def cierre():
    return f"""
<section class="page close">
  <div class="stars">{dots_html()}</div>
  <img class="cov-logo sm" src="{LOGO_W}" alt="connectia">
  <p class="cl-slog"><em>everything is connected.</em></p>
  <p class="cl-tag">CULTURAL MARKETING · MX</p>
  <div class="cl-cnt">
    <span>hola@connectia.mx</span><span>connectia.mx</span>
    <span>Hacienda de Temoluco #130 · Coyoacán · CDMX</span>
  </div>
  <p class="cl-rs">Facilitadores Publicitarios HS, S.A. de C.V.</p>
</section>"""

def chrome(eb, pg):
    return f'<div class="chrome"><span class="eb">CONNECTIA · {eb}</span><span class="eb pg">{pg}</span></div>'

def footer():
    return (f'<div class="foot"><span>SITIOS SELECCIONADOS · TARIFARIO</span>'
            f'<img src="{LOGO_G}" class="wm"><span class="fr">MXN sin IVA</span></div>')

pages = [cover(), resumen()]
for i, s in enumerate(SITIOS):
    pages.append(sitio(s, f"{i+3:02d}"))
pages.append(cierre())

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
@page{size:11in 8.5in;margin:0}
:root{
 --indigo:#201040; --violet-mid:#502090; --brand:#872B90; --hot:#7B3FF2;
 --lime:#C8FF00; --citrus:#FF6A1A; --ink:#0A0118; --mist:#E9E6F0; --slate:#6B6580;
}
html,body{background:#0A0118}
body{font-family:'Inter','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased}
.page{width:1056px;height:816px;position:relative;overflow:hidden;page-break-after:always;color:#fff}
.page:last-child{page-break-after:auto}
.dark{background:linear-gradient(135deg,#201040 0%,#2A1550 45%,#3A1B62 100%)}

/* chrome */
.chrome{position:absolute;top:34px;left:52px;right:52px;display:flex;justify-content:space-between;
 align-items:center;z-index:5}
.eb{font-size:8.5px;font-weight:600;letter-spacing:.42em;text-transform:uppercase;color:rgba(255,255,255,.72)}
.eb.pg{color:var(--lime);letter-spacing:.3em}
.foot{position:absolute;bottom:26px;left:52px;right:52px;display:flex;justify-content:space-between;
 align-items:center;font-size:7.5px;font-weight:600;letter-spacing:.28em;text-transform:uppercase;
 color:rgba(255,255,255,.4)}
.foot .wm{height:13px;opacity:.5}
.foot .fr{text-align:right}

/* portada */
.cover{background:linear-gradient(180deg,#872B90 0%,#5A1B82 25%,#E01C8A 55%,#FF2E63 78%,#FF6A1A 100%)}
.close{background:linear-gradient(160deg,#201040 0%,#502090 55%,#872B90 100%);
 display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.stars{position:absolute;inset:0;z-index:1}
.stars i{position:absolute;background:#fff;border-radius:50%;display:block}
.stars i.lime{background:var(--lime);opacity:1}
.stars i.citrus{background:var(--citrus);opacity:1}
.cov-mid{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;
 justify-content:center;z-index:3}
.cov-logo{width:430px;display:block}
.cov-logo.sm{width:300px;position:relative;z-index:3}
.cov-kicker{margin-top:26px;font-size:9.5px;font-weight:700;letter-spacing:.5em;
 color:rgba(255,255,255,.9)}
.cov-foot{position:absolute;bottom:40px;left:52px;right:52px;display:flex;justify-content:space-between;
 align-items:flex-end;z-index:5}
.slog{font-size:15px;color:rgba(255,255,255,.95);font-weight:300}
.rs{font-size:8.5px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.8)}
.cl-slog{margin-top:34px;font-size:22px;font-weight:300;color:rgba(255,255,255,.96);position:relative;z-index:3}
.cl-tag{margin-top:14px;font-size:9px;font-weight:700;letter-spacing:.5em;color:var(--lime);position:relative;z-index:3}
.cl-cnt{margin-top:46px;display:flex;gap:34px;font-size:11px;font-weight:600;
 color:rgba(255,255,255,.85);position:relative;z-index:3}
.cl-cnt span+span{border-left:1px solid rgba(255,255,255,.3);padding-left:34px}
.cl-rs{position:absolute;bottom:40px;font-size:8.5px;font-weight:600;letter-spacing:.22em;
 text-transform:uppercase;color:rgba(255,255,255,.6);z-index:3}

/* tipografía base */
.eyebrow{font-size:8.5px;font-weight:600;letter-spacing:.4em;text-transform:uppercase;color:var(--hot)}
h1{font-size:42px;font-weight:800;letter-spacing:-.02em;line-height:1;margin-top:10px;text-transform:uppercase}
.afor{font-size:13px;font-weight:300;color:rgba(255,255,255,.62)}
.legal{font-size:8.5px;line-height:1.6;color:rgba(255,255,255,.5);max-width:900px}

/* resumen */
.body{position:absolute;top:104px;left:52px;right:52px}
.tbl{width:100%;border-collapse:collapse;margin-top:26px}
.tbl th{background:var(--brand);color:#fff;font-size:8.5px;font-weight:700;letter-spacing:.16em;
 text-transform:uppercase;padding:11px 12px;text-align:left}
.tbl th.r,.tbl td.r{text-align:right}
.tbl td{padding:13px 12px;border-bottom:1px solid rgba(255,255,255,.12);vertical-align:middle}
.tbl td.num{font-size:15px;font-weight:800;color:rgba(255,255,255,.28);width:44px}
.tbl td.ttl b{display:block;font-size:13.5px;font-weight:800;letter-spacing:-.01em}
.tbl td.ttl span{display:block;font-size:10px;color:rgba(255,255,255,.55);margin-top:2px}
.tbl td.cat,.tbl td.imp{font-size:11px;color:rgba(255,255,255,.75);font-weight:600}
.tbl td.tar{font-size:17px;font-weight:800;text-align:right;white-space:nowrap}
.tbl td.tar.cot{font-size:13px;color:var(--lime)}
.bdg{display:inline-block;font-size:7.5px;font-weight:800;letter-spacing:.14em;padding:4px 9px;
 border-radius:999px;text-transform:uppercase;white-space:nowrap}
.bdg.ok{background:rgba(200,255,0,.14);color:var(--lime);border:1px solid rgba(200,255,0,.35)}
.bdg.new{background:rgba(255,106,26,.16);color:var(--citrus);border:1px solid rgba(255,106,26,.4)}
.tbl tfoot td{background:var(--hot);color:#fff;font-size:11px;font-weight:700;letter-spacing:.1em;
 text-transform:uppercase;border:none;padding:15px 12px}
.tbl tfoot td.r{font-size:22px;letter-spacing:-.01em}
.tbl tfoot td.mini{font-size:8px;font-weight:600;opacity:.85;letter-spacing:.1em;text-align:right}
.body .legal{margin-top:20px}
.body .afor{margin-top:16px}

/* ficha de sitio */
.grid{position:absolute;top:96px;left:52px;right:52px;bottom:64px;display:flex;gap:34px}
.left{width:412px;flex:none}
.ph{width:100%;height:100%;border-radius:20px;background-size:cover;background-position:center;
 box-shadow:0 18px 44px rgba(0,0,0,.45)}
.ph.nofoto{background:linear-gradient(150deg,#2A1550 0%,#502090 60%,#872B90 100%);
 display:flex;align-items:center;justify-content:center;border:1.5px dashed rgba(255,255,255,.28)}
.nf{text-align:center;padding:0 34px}
.nf-eb{display:block;font-size:8px;font-weight:700;letter-spacing:.4em;color:var(--citrus)}
.nf-t{display:block;margin-top:14px;font-size:22px;font-weight:800;letter-spacing:-.01em}
.nf-s{display:block;margin-top:12px;font-size:10.5px;line-height:1.6;color:rgba(255,255,255,.62)}
.right{flex:1;display:flex;flex-direction:column}
.h-site{font-size:34px;margin-top:8px;line-height:1.02}
.sub{margin-top:7px;font-size:13px;font-weight:600;color:var(--lime)}
.ubic{margin-top:3px;font-size:10.5px;color:rgba(255,255,255,.6)}
.price{margin-top:16px;padding:14px 18px;border-radius:14px;
 background:linear-gradient(100deg,rgba(135,43,144,.55),rgba(123,63,242,.3));
 border:1px solid rgba(123,63,242,.45);display:flex;align-items:center;gap:14px}
.p-l{font-size:7.5px;font-weight:700;letter-spacing:.3em;color:rgba(255,255,255,.72);
 text-transform:uppercase;line-height:1.3;width:64px}
.p-v{font-size:31px;font-weight:800;letter-spacing:-.02em;flex:1}
.p-v.cot{font-size:22px;color:var(--lime)}
.p-v em{font-size:11px;font-weight:600;font-style:normal;opacity:.75}
.specs{margin-top:16px;display:flex;flex-wrap:wrap;gap:9px}
.specs>div{width:calc(33.333% - 6px);background:rgba(255,255,255,.06);
 border:1px solid rgba(255,255,255,.1);border-radius:11px;padding:9px 11px}
.specs>div.wide{width:100%}
.specs span{display:block;font-size:6.8px;font-weight:700;letter-spacing:.26em;
 color:rgba(255,255,255,.5);text-transform:uppercase}
.specs b{display:block;margin-top:4px;font-size:10.5px;font-weight:700;line-height:1.35}
.obj{margin-top:16px;font-size:12.5px;line-height:1.5;color:#fff}
.benef{margin-top:8px;font-size:11px;line-height:1.6;color:rgba(255,255,255,.72)}
.sheet .afor{margin-top:auto;padding-top:14px;border-top:1px solid rgba(255,255,255,.14)}
"""

html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Sitios Connectia · Tarifario</title>
<style>{FONTS}</style><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"""

out = os.path.join(SCR, "tarifario.html")
open(out, "w").write(html)
print("HTML:", out, round(os.path.getsize(out)/1024/1024, 1), "MB")
print("TOTAL:", mxn(TOTAL))
