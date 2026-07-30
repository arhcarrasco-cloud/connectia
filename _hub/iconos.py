#!/usr/bin/env python3
"""
Genera los íconos del App Hub a partir de _hub/catalogo.json.
Escribe SVG y PNG 1024 en hub/iconos/.

No necesita librerías externas: los SVG se rasterizan con Chrome headless,
que ya está instalado. Pillow solo se usa para recortar el logo oficial.
"""
import json, os, pathlib, subprocess, sys, base64, io

ROOT   = pathlib.Path(__file__).resolve().parent.parent   # raíz del repo
CAT    = json.loads((ROOT / "_hub" / "catalogo.json").read_text(encoding="utf-8"))
DEST   = ROOT / "hub" / "iconos"
LOGO   = pathlib.Path.home() / "Connectia-Assets/connectia/logo/connectia-white.png"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

S, INSET, R = 1024, 92, 200
BOX = S - INSET * 2
DEST.mkdir(parents=True, exist_ok=True)

# ── glifos: viewBox local 512×512, trazo blanco ───────────────────────────
GLYPHS = {
"billboard": '''
  <rect x="60" y="96" width="392" height="228" rx="18" fill="none" stroke="#fff" stroke-width="30"/>
  <path d="M150 324 L128 452 M362 324 L384 452" stroke="#fff" stroke-width="30" stroke-linecap="round"/>
  <path d="M110 452 H402" stroke="#fff" stroke-width="26" stroke-linecap="round" opacity=".55"/>
  <circle cx="188" cy="196" r="34" fill="#fff"/>
  <path d="M242 262 L306 172 L370 262 Z" fill="#fff"/>''',

"pin": '''
  <circle cx="256" cy="256" r="196" fill="none" stroke="#fff" stroke-width="20" opacity=".26"/>
  <path d="M60 256 H452 M256 60 V452" stroke="#fff" stroke-width="16" opacity=".22"/>
  <path d="M256 74 C334 74 396 136 396 214 C396 322 256 452 256 452
           C256 452 116 322 116 214 C116 136 178 74 256 74 Z" fill="#fff"/>
  <circle cx="256" cy="212" r="52" fill="none" stroke="#000" stroke-width="30" opacity=".32"/>''',

"van": '''
  <path d="M46 168 H286 V352 H46 Z" fill="#fff"/>
  <path d="M286 206 H384 L466 288 V352 H286 Z" fill="#fff" opacity=".72"/>
  <circle cx="150" cy="376" r="52" fill="#fff"/><circle cx="150" cy="376" r="22" fill="#000" opacity=".32"/>
  <circle cx="386" cy="376" r="52" fill="#fff"/><circle cx="386" cy="376" r="22" fill="#000" opacity=".32"/>
  <path d="M86 216 H240" stroke="#000" stroke-width="26" opacity=".26" stroke-linecap="round"/>
  <path d="M86 272 H196" stroke="#000" stroke-width="26" opacity=".26" stroke-linecap="round"/>''',

"capas": '''
  <rect x="86" y="74"  width="340" height="88" rx="26" fill="#fff"/>
  <rect x="86" y="196" width="340" height="88" rx="26" fill="#fff" opacity=".74"/>
  <rect x="86" y="318" width="340" height="88" rx="26" fill="#fff" opacity=".48"/>
  <circle cx="150" cy="118" r="20" fill="#000" opacity=".30"/>
  <circle cx="150" cy="240" r="20" fill="#000" opacity=".26"/>
  <circle cx="150" cy="362" r="20" fill="#000" opacity=".22"/>
  <path d="M240 118 H370 M240 240 H340 M240 362 H310" stroke="#000" stroke-width="22" opacity=".22" stroke-linecap="round"/>''',

"ruta": '''
  <path d="M130 366 C130 258 380 300 380 186" fill="none" stroke="#fff" stroke-width="24"
        stroke-linecap="round" stroke-dasharray="8 44" opacity=".85"/>
  <path d="M130 156 C176 156 213 193 213 239 C213 303 130 386 130 386
           C130 386 47 303 47 239 C47 193 84 156 130 156 Z" fill="#fff"/>
  <circle cx="130" cy="238" r="34" fill="none" stroke="#000" stroke-width="22" opacity=".30"/>
  <circle cx="380" cy="150" r="72" fill="#fff"/>
  <circle cx="380" cy="150" r="30" fill="#000" opacity=".30"/>''',

"tablero": '''
  <rect x="104" y="86" width="304" height="376" rx="34" fill="#fff"/>
  <rect x="196" y="52" width="120" height="66" rx="26" fill="#fff"/>
  <rect x="196" y="52" width="120" height="66" rx="26" fill="#000" opacity=".22"/>
  <rect x="162" y="304" width="46" height="98"  rx="11" fill="#000" opacity=".34"/>
  <rect x="233" y="252" width="46" height="150" rx="11" fill="#000" opacity=".46"/>
  <rect x="304" y="196" width="46" height="206" rx="11" fill="#000" opacity=".34"/>
  <path d="M162 172 H350" stroke="#000" stroke-width="24" opacity=".22" stroke-linecap="round"/>''',

"radar": '''
  <path d="M256 56 L452 198 L377 428 L135 428 L60 198 Z" fill="none" stroke="#fff" stroke-width="18" opacity=".34"/>
  <path d="M256 56 V284 M452 198 L256 284 M377 428 L256 284 M135 428 L256 284 M60 198 L256 284"
        stroke="#fff" stroke-width="14" opacity=".26"/>
  <path d="M256 96 L412 210 L332 356 L164 328 L118 200 Z" fill="#fff"/>
  <circle cx="256" cy="96"  r="26" fill="#fff"/><circle cx="412" cy="210" r="26" fill="#fff"/>
  <circle cx="332" cy="356" r="26" fill="#fff"/><circle cx="164" cy="328" r="26" fill="#fff"/>
  <circle cx="118" cy="200" r="26" fill="#fff"/>''',

"libro": '''
  <path d="M256 168 C206 126 130 118 66 132 V400 C130 386 206 394 256 436 Z" fill="#fff"/>
  <path d="M256 168 C306 126 382 118 446 132 V400 C382 386 306 394 256 436 Z" fill="#fff" opacity=".72"/>
  <path d="M256 168 V436" stroke="#000" stroke-width="20" opacity=".22"/>
  <path d="M368 62 L384 108 L430 124 L384 140 L368 186 L352 140 L306 124 L352 108 Z" fill="#fff"/>''',

"globo": '''
  <circle cx="240" cy="230" r="176" fill="none" stroke="#fff" stroke-width="30"/>
  <path d="M64 230 H416" stroke="#fff" stroke-width="26"/>
  <path d="M240 54 C314 130 314 330 240 406 C166 330 166 130 240 54 Z" fill="none" stroke="#fff" stroke-width="26"/>
  <path d="M262 316 H470 L440 420 H292 Z" fill="#fff"/>
  <path d="M262 316 H470 L440 420 H292 Z" fill="#000" opacity=".18"/>
  <path d="M232 282 H274 L292 420" fill="none" stroke="#fff" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="318" cy="462" r="30" fill="#fff"/><circle cx="424" cy="462" r="30" fill="#fff"/>''',

"docs": '''
  <rect x="96"  y="70"  width="240" height="308" rx="30" fill="#fff" opacity=".55"/>
  <rect x="152" y="118" width="240" height="308" rx="30" fill="#fff"/>
  <path d="M198 200 H346 M198 262 H346 M198 324 H286" stroke="#000" stroke-width="26" opacity=".26" stroke-linecap="round"/>
  <circle cx="386" cy="378" r="80" fill="#fff"/>
  <path d="M348 378 L376 408 L426 350" fill="none" stroke="#000" stroke-width="32"
        stroke-linecap="round" stroke-linejoin="round" opacity=".42"/>''',

"escudo": '''
  <path d="M256 52 L430 116 V266 C430 366 350 434 256 464 C162 434 82 366 82 266 V116 Z" fill="#fff"/>
  <rect x="196" y="240" width="120" height="102" rx="18" fill="#000" opacity=".34"/>
  <path d="M218 240 V208 C218 186 235 168 256 168 C277 168 294 186 294 208 V240"
        fill="none" stroke="#000" stroke-width="26" opacity=".34" stroke-linecap="round"/>''',

"navegador": '''
  <rect x="52" y="96" width="408" height="320" rx="38" fill="#fff"/>
  <path d="M52 176 H460" stroke="#000" stroke-width="22" opacity=".24"/>
  <circle cx="104" cy="136" r="15" fill="#000" opacity=".26"/>
  <circle cx="152" cy="136" r="15" fill="#000" opacity=".26"/>
  <circle cx="200" cy="136" r="15" fill="#000" opacity=".26"/>
  <path d="M136 342 L214 342 L214 276 L292 276 L292 224 L376 224" fill="none" stroke="#000"
        stroke-width="30" opacity=".38" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M334 186 H386 V238" fill="none" stroke="#000" stroke-width="30" opacity=".38"
        stroke-linecap="round" stroke-linejoin="round"/>''',

"calculadora": '''
  <rect x="112" y="52" width="288" height="408" rx="42" fill="#fff"/>
  <rect x="156" y="98" width="200" height="88" rx="16" fill="#000" opacity=".30"/>
  <path d="M256 118 V166 M232 132 H274 C284 132 290 138 290 144 C290 150 284 156 274 156
           H238 C228 156 222 162 222 168 C222 174 228 180 238 180 H280"
        fill="none" stroke="#fff" stroke-width="13" stroke-linecap="round" opacity=".9"/>
  <circle cx="176" cy="248" r="26" fill="#000" opacity=".26"/>
  <circle cx="256" cy="248" r="26" fill="#000" opacity=".26"/>
  <circle cx="336" cy="248" r="26" fill="#000" opacity=".26"/>
  <circle cx="176" cy="326" r="26" fill="#000" opacity=".26"/>
  <circle cx="256" cy="326" r="26" fill="#000" opacity=".26"/>
  <circle cx="336" cy="326" r="26" fill="#000" opacity=".26"/>
  <circle cx="176" cy="404" r="26" fill="#000" opacity=".26"/>
  <rect x="230" y="378" width="132" height="52" rx="26" fill="#000" opacity=".40"/>''',

"etiqueta": '''
  <path d="M238 54 H430 C446 54 458 66 458 82 V274 L266 466 C252 480 232 480 218 466
           L46 294 C32 280 32 260 46 246 Z" fill="#fff"/>
  <circle cx="378" cy="134" r="42" fill="#000" opacity=".32"/>
  <path d="M212 240 V300 M182 258 H236 C248 258 256 266 256 274 C256 282 248 290 236 290
           H198 C186 290 178 298 178 306 C178 314 186 322 198 322 H244"
        fill="none" stroke="#000" stroke-width="20" stroke-linecap="round" opacity=".34"/>''',

"diana": '''
  <circle cx="240" cy="272" r="190" fill="none" stroke="#fff" stroke-width="34"/>
  <circle cx="240" cy="272" r="120" fill="none" stroke="#fff" stroke-width="34" opacity=".72"/>
  <circle cx="240" cy="272" r="46" fill="#fff"/>
  <path d="M240 272 L446 66" stroke="#fff" stroke-width="34" stroke-linecap="round"/>
  <path d="M382 66 H446 V130" fill="none" stroke="#fff" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/>''',
}

def glifo_ebook(lang):
    return f'''
  <path d="M118 66 H360 C388 66 410 88 410 116 V444 L256 386 L118 444 Z" fill="#fff"/>
  <path d="M170 152 H330 M170 214 H330 M170 276 H286" stroke="#000" stroke-width="24" opacity=".24" stroke-linecap="round"/>
  <rect x="270" y="330" width="176" height="94" rx="30" fill="#fff"/>
  <rect x="270" y="330" width="176" height="94" rx="30" fill="#000" opacity=".30"/>
  <text x="358" y="396" font-family="Helvetica,Arial,sans-serif" font-size="66" font-weight="700"
        fill="#fff" text-anchor="middle" letter-spacing="2">{lang}</text>'''

def glifo_logo():
    """Logo oficial de Connectia. Nunca se redibuja: se incrusta el PNG real."""
    if not LOGO.exists():
        sys.exit(f"FALTA el logo oficial en {LOGO} — no invento una variante, detengo.")
    from PIL import Image
    im = Image.open(LOGO).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    buf = io.BytesIO(); im.save(buf, "PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    w = BOX * 0.80
    h = w * im.size[1] / im.size[0]
    return (f'<image x="{(S-w)/2:.1f}" y="{(S-h)/2:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'xlink:href="data:image/png;base64,{b64}"/>'), True

MARCO = '''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{S}" height="{S}" viewBox="0 0 {S} {S}">
 <defs>
  <linearGradient id="t" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{hi}"/><stop offset="1" stop-color="{lo}"/></linearGradient>
  <linearGradient id="s" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".26"/>
    <stop offset=".45" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="d" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="20" stdDeviation="26" flood-color="#000" flood-opacity=".34"/></filter>
  <filter id="g" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity=".22"/></filter>
  <clipPath id="c"><rect x="{I}" y="{I}" width="{B}" height="{B}" rx="{R}"/></clipPath>
 </defs>
 <g filter="url(#d)"><rect x="{I}" y="{I}" width="{B}" height="{B}" rx="{R}" fill="url(#t)"/></g>
 <g clip-path="url(#c)"><rect x="{I}" y="{I}" width="{B}" height="{HB}" fill="url(#s)"/></g>
 <rect x="{I1}" y="{I1}" width="{B2}" height="{B2}" rx="{R1}" fill="none"
       stroke="#fff" stroke-opacity=".22" stroke-width="3"/>
 <g filter="url(#g)" transform="{tr}">{glifo}</g>
</svg>'''

ESCALA = (BOX * 0.60) / 512
OFF    = (S - 512 * ESCALA) / 2

def construir(app):
    g = app["glifo"]
    if g == "logo":
        cuerpo, sin_escala = glifo_logo()
        tr = ""
    elif g.startswith("ebook:"):
        cuerpo, tr = glifo_ebook(g.split(":")[1]), f"translate({OFF:.2f},{OFF:.2f}) scale({ESCALA:.5f})"
    else:
        if g not in GLYPHS:
            sys.exit(f"glifo desconocido '{g}' en la app '{app['id']}'")
        cuerpo, tr = GLYPHS[g], f"translate({OFF:.2f},{OFF:.2f}) scale({ESCALA:.5f})"
    return MARCO.format(S=S, I=INSET, B=BOX, R=R, HB=BOX // 2,
                        I1=INSET + 2, B2=BOX - 4, R1=R - 2,
                        hi=app["hi"], lo=app["lo"], tr=tr, glifo=cuerpo)

# ── escribir SVG ───────────────────────────────────────────────────────────
pendientes = []
for app in CAT["apps"]:
    svg = DEST / f"{app['id']}.svg"
    svg.write_text(construir(app), encoding="utf-8")
    pendientes.append(app["id"])
print(f"SVG escritos: {len(pendientes)}")

# ── rasterizar con Chrome headless (cero dependencias) ─────────────────────
if not os.path.exists(CHROME):
    sys.exit("No encuentro Google Chrome; los PNG no se pudieron generar.")

for i in pendientes:
    svg = DEST / f"{i}.svg"
    png = DEST / f"{i}.png"
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                    "--default-background-color=00000000",
                    f"--screenshot={png}", f"--window-size={S},{S}",
                    svg.as_uri()],
                   capture_output=True, timeout=90)
    if not png.exists():
        sys.exit(f"Chrome no pudo rasterizar {i}.svg")
print(f"PNG generados: {len(pendientes)} en {DEST.relative_to(ROOT)}")

# ── ícono de pantalla de inicio de iOS ─────────────────────────────────────
# iOS aplica su propia máscara redondeada, así que este va a sangre:
# sin margen y sin esquinas propias, o se ven dos redondeos encimados.
cuerpo, _ = glifo_logo()
ios = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 width="{S}" height="{S}" viewBox="0 0 {S} {S}">
 <defs>
  <linearGradient id="t" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#A93FB4"/><stop offset="1" stop-color="#5E1E64"/></linearGradient>
  <linearGradient id="s" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity=".22"/>
    <stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
 </defs>
 <rect width="{S}" height="{S}" fill="url(#t)"/>
 <rect width="{S}" height="{S//2}" fill="url(#s)"/>
 {cuerpo}
</svg>"""
(DEST / "apple-touch.svg").write_text(ios, encoding="utf-8")
subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                f"--screenshot={DEST / 'apple-touch.png'}", f"--window-size={S},{S}",
                (DEST / "apple-touch.svg").as_uri()], capture_output=True, timeout=90)
print("ícono de iPhone: apple-touch.png")
