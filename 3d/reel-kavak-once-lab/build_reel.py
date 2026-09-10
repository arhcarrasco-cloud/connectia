#!/usr/bin/env python3
"""
once once LAB · Reel KAVAK (casco + cápsulas) · 1080x1920 · 30 fps · 30 s
Uso:
  python3 build_reel.py OUT.mp4 [--casco TIMELAPSE_CASCO.avi] [--capsulas TIMELAPSE_CAPSULAS.avi] [--clips CARPETA_HIGGSFIELD]
Sin --casco/--capsulas usa stand-ins (clip Bambu del banco de Reels + primera capa real P1S).
"""
import sys, os, math, subprocess, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg, io

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
ROSA = (240, 36, 107); TINTA = (21, 18, 23); BLANCO = (255, 255, 255)
CREMA = (240, 231, 211); CHICLE = (245, 110, 158)

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--casco"); ap.add_argument("--capsulas")
ap.add_argument("--clips", help="carpeta con clips Higgsfield: hook.mp4 blanco_a.mp4 blanco_b.mp4 caps.mp4 merch.mp4 claim_top.mp4")
ap.add_argument("--preview", action="store_true", help="solo exporta PNGs clave")
A = ap.parse_args()

# ---------- fuentes (manual once LAB cap. 05) ----------
def vfont(path, size, axes):
    f = ImageFont.truetype(os.path.join(HERE, "fonts", path), size)
    try:
        names = [a["name"].decode() if isinstance(a["name"], bytes) else a["name"] for a in f.get_variation_axes()]
        key = {"weight": "wght", "width": "wdth"}
        vals = [axes.get(key.get(n.lower(), n.lower()), a["default"]) for n, a in zip(names, f.get_variation_axes())]
        vals = [min(max(v, a["minimum"]), a["maximum"]) for v, a in zip(vals, f.get_variation_axes())]
        f.set_variation_by_axes(vals)
    except Exception as e:
        print("variation axes:", e)
    return f
def display(size):  # Archivo Expanded 800 · wdth 112
    return vfont("Archivo[wdth,wght].ttf", size, {"wdth": 112, "wght": 800})
def texto(size, w=500):  # Instrument Sans
    return vfont("InstrumentSans[wdth,wght].ttf", size, {"wdth": 100, "wght": w})
def mono(size):  # IBM Plex Mono SemiBold
    return ImageFont.truetype(os.path.join(HERE, "fonts", "IBMPlexMono-SemiBold.ttf"), size)

# ---------- helpers ----------
def ease(t):  # easeInOutCubic
    t = max(0.0, min(1.0, t))
    return 4*t*t*t if t < .5 else 1-((-2*t+2)**3)/2
def ease_out(t):
    t = max(0.0, min(1.0, t)); return 1-(1-t)**3
def lerp(a, b, t): return a+(b-a)*t

def draw_tracked(draw, xy, txt, font, fill, tracking=0.0):
    x, y = xy
    for ch in txt:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x
def text_width(txt, font, tracking=0.0):
    return sum(font.getlength(c)+tracking for c in txt)

def fit_display(lines, size, maxw, tracking):
    """Reduce el cuerpo hasta que la línea más ancha quepa en maxw."""
    while size > 40:
        f = display(size)
        if max(text_width(ln, f, tracking) for ln, _ in lines) <= maxw: return f
        size -= 4
    return display(size)

def layer_text(lines, font, fill, x, y_bottom, tracking=0.0, gap=8, align="left"):
    """RGBA layer con líneas apiladas hacia arriba desde y_bottom."""
    if font.path.endswith("Archivo[wdth,wght].ttf"):
        font = fit_display(lines, font.size, W - 2*x, tracking)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    asc, desc = font.getmetrics(); lh = asc + desc*0.6 + gap
    y = y_bottom - lh*len(lines)
    for ln, col in lines:
        tw = text_width(ln, font, tracking)
        xx = x if align == "left" else (W - tw)/2 if align == "center" else W - x - tw
        draw_tracked(d, (xx, y), ln, font, col or fill, tracking); y += lh
    return L

def label_pill(txt, x, y, fg=CREMA, bg=(21, 18, 23, 200), marker=ROSA):
    f = mono(30); L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    tw = f.getlength(txt); pad = 22; h = 62
    d.rounded_rectangle((x, y, x+tw+pad*2+34, y+h), radius=10, fill=bg)
    d.rectangle((x+pad, y+h/2-8, x+pad+16, y+h/2+8), fill=marker)
    d.text((x+pad+34, y+h/2-f.getmetrics()[0]/2-2), txt, font=f, fill=fg)
    return L

def scrim(strength=0.85, top=0.45):
    """degradado oscuro abajo para legibilidad."""
    g = np.linspace(0, 1, H)[:, None]
    a = np.clip((g - top)/(1-top), 0, 1)**1.4 * strength
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 0:3] = TINTA; arr[..., 3] = (a*255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def composite(base, layer, alpha=1.0):
    if alpha <= 0: return base
    if alpha < 1:
        a = layer.getchannel("A").point(lambda v: int(v*alpha)); layer = layer.copy(); layer.putalpha(a)
    return Image.alpha_composite(base, layer)

def cover(img, w=W, h=H):
    r = max(w/img.width, h/img.height); im = img.resize((math.ceil(img.width*r), math.ceil(img.height*r)), Image.LANCZOS)
    x = (im.width-w)//2; y = (im.height-h)//2; return im.crop((x, y, x+w, y+h))

def kb_frame(img, t, r0, r1, size=(W, H)):
    """Ken Burns: r = (cx, cy, scale) en fracciones; scale=1 -> imagen cubre el destino."""
    tw, th = size
    cx, cy, s = [lerp(a, b, ease(t)) for a, b in zip(r0, r1)]
    base = max(tw/img.width, th/img.height)*s
    cw, ch = tw/base, th/base
    x0 = cx*img.width - cw/2; y0 = cy*img.height - ch/2
    x0 = min(max(0, x0), img.width-cw); y0 = min(max(0, y0), img.height-ch)
    return img.crop((int(x0), int(y0), int(x0+cw), int(y0+ch))).resize((tw, th), Image.LANCZOS).convert("RGBA")

def video_frames(path, n, mode="cover", speed=None):
    """Decodifica n frames a 30fps. mode=cover (9:16 full bleed) o panel (16:9 → 1080x608)."""
    if mode == "cover":
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
        w, h = W, H
    elif mode == "half":
        w, h = W, H//2; vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    else:
        w, h = 1080, 608; vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    if speed: vf = f"setpts={speed}*PTS," + vf
    vf += f",fps={FPS}"
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8)
    k = len(frames)//(w*h*3); frames = frames[:k*w*h*3].reshape(k, h, w, 3)
    out = [Image.fromarray(frames[i]) for i in range(k)]
    while len(out) < n: out.append(out[-1])  # hold último frame
    return out, (w, h)

# ---------- logo once LAB (master SVG) ----------
svg = open(os.path.join(HERE, "brand", "oncelablogomaster.svg")).read()
def svg_png(s, px):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(), output_width=px, output_height=px))).convert("RGBA")
LOGO_PX = 760
logo_full = svg_png(svg, LOGO_PX)
# anillo punteado aparte para animarlo (misma geometría del master)
ring_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><circle cx="200" cy="200" r="152" fill="none" '
            'stroke="#F0246B" stroke-width="7" stroke-linecap="round" stroke-dasharray="0.1 15.85"/></svg>')
ring = svg_png(ring_svg, LOGO_PX)
import re
body_svg = re.sub(r'<circle cx="200" cy="200" r="152"[^>]*/>', '', svg)  # sello sin anillo
logo_body = svg_png(body_svg, LOGO_PX)

def brand_card(t, dur, outro=False):
    """Intro/outro: placa blanca, sello entra con escala+alpha, anillo gira, firma."""
    F = Image.new("RGBA", (W, H), BLANCO+(255,))
    a = ease_out(t/0.55); sc = lerp(0.86, 1.0, a)
    px = int(LOGO_PX*sc); cx, cy = W//2, int(H*0.43)
    body = logo_body.resize((px, px), Image.LANCZOS)
    rg = ring.resize((px, px), Image.LANCZOS).rotate(-t*9, resample=Image.BICUBIC)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lay.alpha_composite(body, (cx-px//2, cy-px//2)); lay.alpha_composite(rg, (cx-px//2, cy-px//2))
    F = composite(F, lay, a)
    # firma
    ta = ease_out((t-0.5)/0.5)
    f = display(58); txt = "LO HACEMOS REALIDAD"; tw = text_width(txt, f, -1.2)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    draw_tracked(d, ((W-tw)/2, cy+px//2+70+int((1-ta)*24)), txt, f, TINTA, -1.2)
    d.rectangle(((W-120)/2, cy+px//2+150, (W+120)/2, cy+px//2+156), fill=ROSA)
    F = composite(F, L, ta)
    if outro:
        ta2 = ease_out((t-1.0)/0.6)
        f2 = texto(40, 500); s1 = "Impresión 3D  ·  Sublimación  ·  CDMX"
        L2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(L2)
        d2.text(((W-f2.getlength(s1))/2, cy+px//2+190), s1, font=f2, fill=(90, 84, 92))
        f3 = mono(30); s2 = "11:11  ·  PIDE UN DESEO. LO IMPRIMIMOS."
        d2.text(((W-f3.getlength(s2))/2, H-330), s2, font=f3, fill=ROSA)
        F = composite(F, L2, ta2)
    return F

# ---------- escenas ----------
PH = {k: Image.open(os.path.join(HERE, "photos", v)).convert("RGB") for k, v in
      {"casco": "casco.jpg", "caja": "capsulas_caja.jpg", "playera": "playera.jpg",
       "blanco_a": "casco_blanco_a.jpg", "blanco_b": "casco_blanco_b.jpg", "blanco_det": "casco_blanco_detalle.jpg"}.items()}
from PIL import ImageEnhance
PH["playera"] = ImageEnhance.Contrast(ImageEnhance.Brightness(PH["playera"]).enhance(1.18)).enhance(1.08)
PH["casco"] = ImageEnhance.Color(ImageEnhance.Contrast(PH["casco"]).enhance(1.06)).enhance(1.08)

# ---------- clips generados (Higgsfield) ----------
CLIPS = {}
def load_clips():
    if not A.clips: return
    spec = {"hook": ("cover", 100), "blanco_a": ("cover", 60), "blanco_b": ("cover", 60), "caps": ("cover", 100),
            "merch": ("cover", 100), "claim_top": ("half", 100)}
    for name, (mode, n) in spec.items():
        for ext in ("mp4", "mov"):
            path = os.path.join(A.clips, f"{name}.{ext}")
            if os.path.exists(path):
                CLIPS[name] = video_frames(path, n, mode)[0]; print("clip Higgsfield:", name, path); break

def shot(clip, photo, t, dur, r0, r1, size=(W, H)):
    """Frame de la toma: clip Higgsfield si existe, si no Ken Burns sobre la foto."""
    if clip in CLIPS:
        fr = CLIPS[clip]; return fr[min(int(round(t*FPS)), len(fr)-1)].convert("RGBA")
    return kb_frame(PH[photo], t/dur, r0, r1, size)

def scene_photo(key, t, dur, r0, r1, head, label, head_size=150, y_bottom=None, scrim_s=0.88, clip=None):
    F = shot(clip or key, key, t, dur, r0, r1)
    F = composite(F, scrim(scrim_s, 0.42))
    ta = ease_out((t-0.15)/0.45)
    yb = y_bottom or H-360
    Lh = layer_text(head, display(head_size), CREMA, 84, yb+int((1-ta)*30), tracking=-3, gap=6)
    F = composite(F, Lh, ta)
    tb = ease_out((t-0.45)/0.4)
    F = composite(F, label_pill(label, 84, yb+26), tb)
    return F

def scene_clip(frames, i, t, dur, head, label, mode, sub=None):
    i = min(i, len(frames)-1)
    if mode == "cover":
        F = frames[i].convert("RGBA"); F = composite(F, scrim(0.9, 0.4))
    else:  # panel editorial: fondo tinta, clip 16:9 centrado, textos arriba/abajo
        F = Image.new("RGBA", (W, H), TINTA+(255,))
        fr = frames[i].convert("RGBA"); y0 = int(H*0.36)
        F.alpha_composite(fr, (0, y0))
        d = ImageDraw.Draw(F); d.rectangle((0, y0-6, W, y0), fill=ROSA)
    ta = ease_out((t-0.1)/0.45)
    if mode == "cover":
        F = composite(F, layer_text(head, display(150), CREMA, 84, H-360, tracking=-3), ta)
        F = composite(F, label_pill(label, 84, H-334), ease_out((t-0.4)/0.4))
    else:
        F = composite(F, layer_text(head, display(118), CREMA, 84, int(H*0.36)-40, tracking=-2.5), ta)
        F = composite(F, label_pill(label, 84, int(H*0.36)+608+40), ease_out((t-0.4)/0.4))
        if sub:
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(L).text((84, int(H*0.36)+608+125), sub, font=texto(36, 500), fill=(200, 192, 180))
            F = composite(F, L, ease_out((t-0.6)/0.4))
    return F

def scene_two_shots(keys, t, dur, kbs, head, label):
    """Dos tomas con corte seco a la mitad; titular y etiqueta persisten."""
    half = dur/2; k = 0 if t < half else 1; tt = (t - k*half)
    F = shot(keys[k], keys[k], tt, half, *kbs[k])
    F = composite(F, scrim(0.88, 0.42))
    ta = ease_out((t-0.15)/0.45); yb = H-360
    F = composite(F, layer_text(head, display(138), CREMA, 84, yb+int((1-ta)*30), tracking=-3, gap=6), ta)
    F = composite(F, label_pill(label, 84, yb+26), ease_out((t-0.45)/0.4))
    return F

def scene_claim(t, dur):
    """Split: detalle casco blanco arriba / cápsulas abajo + claim."""
    F = Image.new("RGBA", (W, H), TINTA+(255,))
    top = shot("claim_top", "blanco_det", t, dur, (0.42, 0.45, 1.02), (0.40, 0.42, 1.14), size=(W, H//2))
    bot = kb_frame(PH["caja"], t/dur, (0.5, 0.5, 1.05), (0.5, 0.5, 1.18)).crop((0, 500, W, 500+H//2))
    F.paste(top, (0, 0)); F.paste(bot, (0, H//2))
    F = composite(F, scrim(0.92, 0.35))
    d = ImageDraw.Draw(F); d.rectangle((0, H//2-4, W, H//2+4), fill=ROSA)
    ta = ease_out((t-0.1)/0.5)
    F = composite(F, layer_text([("LO IMAGINASTE.", CREMA), ("LO IMPRIMIMOS.", ROSA)], display(140), CREMA, 84, H-380, tracking=-3), ta)
    F = composite(F, label_pill("CASCO + CÁPSULAS · PROYECTO KAVAK", 84, H-354), ease_out((t-0.45)/0.4))
    return F

# ---------- clips de proceso ----------
def load_process_clips():
    n = 150 + 12  # escena + solape de crossfade
    if A.casco:
        casco_fr, _ = video_frames(A.casco, n, "panel", speed=None); casco_mode = "panel"
        casco_head = [("CAPA POR", CREMA), ("CAPA.", ROSA)]; casco_label = "TIMELAPSE · CASCO KAVAK · BAMBU LAB P1S"
    else:
        casco_fr, _ = video_frames(os.path.join(HERE, "brand", "bambu_intro.mp4"), n, "cover"); casco_mode = "cover"
        casco_head = [("CAPA POR", CREMA), ("CAPA.", ROSA)]; casco_label = "PROCESO · IMPRESIÓN 3D"
    if A.capsulas:
        caps_fr, _ = video_frames(A.capsulas, n, "panel"); caps_label = "TIMELAPSE · CÁPSULAS · PETG AZUL"
    else:
        caps_fr, _ = video_frames(os.path.join(HERE, "src", "video_2026-08-22_11-36-38.avi"), n, "panel", speed=2.85)
        caps_label = "PRIMERA CAPA · BAMBU LAB P1S · PETG"
    return casco_fr, casco_mode, casco_head, casco_label, caps_fr, caps_label

casco_fr, casco_mode, casco_head, casco_label, caps_fr, caps_label = load_process_clips()
load_clips()

# ---------- timeline (900 frames = 30.0 s) ----------
SC = [
 ("intro",  75, lambda t, d, i: brand_card(t, d)),
 ("hook",   90, lambda t, d, i: scene_photo("casco", t, d, (0.50, 0.50, 1.02), (0.52, 0.46, 1.30),
                                            [("UN CASCO", CREMA), ("KAVAK", ROSA), ("IMPRESO EN 3D", CREMA)], "ESCALA REAL · IMPRESIÓN 3D · PIEZA ÚNICA", 138, clip="hook")),
 ("blanco", 90, lambda t, d, i: scene_two_shots(["blanco_a", "blanco_b"], t, d,
                                            [((0.45, 0.55, 1.05), (0.42, 0.52, 1.22)), ((0.55, 0.48, 1.22), (0.52, 0.50, 1.04))],
                                            [("EN AZUL.", CREMA), ("Y EN BLANCO.", ROSA)], "DOS VERSIONES · MÁSCARA Y HERRAJES IMPRESOS")),
 ("proc1", 135, lambda t, d, i: scene_clip(casco_fr, i, t, d, casco_head, casco_label, casco_mode, "De archivo 3D a objeto real, capa por capa.")),
 ("caps",   90, lambda t, d, i: scene_photo("caja", t, d, (0.5, 0.62, 1.30), (0.5, 0.42, 1.06),
                                            [("CÁPSULAS", CREMA), ("A LA MEDIDA", ROSA)], "PETG · AZUL KAVAK · LOTE COMPLETO", 138, clip="caps")),
 ("proc2", 135, lambda t, d, i: scene_clip(caps_fr, i, t, d, [("LOTE TRAS", CREMA), ("LOTE.", ROSA)], caps_label, "panel",
                                            "Producción en serie con control de calidad pieza por pieza.")),
 ("merch",  90, lambda t, d, i: scene_photo("playera", t, d, (0.45, 0.55, 1.25), (0.55, 0.50, 1.04),
                                            [("Y LA", CREMA), ("ACTIVACIÓN", ROSA), ("COMPLETA", CREMA)], "ACTIVACIÓN KAVAK · MERCH", 138, clip="merch")),
 ("claim",  90, lambda t, d, i: scene_claim(t, d)),
 ("outro", 105, lambda t, d, i: brand_card(t, d, outro=True)),
]
XF = 9  # frames de crossfade entre escenas (excepto intro→hook: corte seco)
# escenas con crossfade hacia la siguiente ganan XF frames (se solapan) → salida exacta de 900 frames
SC = [(n, l + (XF if (i+1 < len(SC) and n != "intro") else 0), f) for i, (n, l, f) in enumerate(SC)]
assert sum(l for _, l, _ in SC) - XF*(len(SC)-2) == 900, sum(l for _, l, _ in SC)

def render_scene(idx, i):
    name, n, fn = SC[idx]; return fn(i/FPS, n/FPS, i)

if A.preview:
    os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
    for idx, (name, n, fn) in enumerate(SC):
        for k in (0.35, 0.8):
            render_scene(idx, int(n*k)).convert("RGB").save(os.path.join(HERE, "preview", f"{idx}_{name}_{int(k*100)}.jpg"), quality=88)
    sys.exit(0)

cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", A.out]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
gi = 0
for idx, (name, n, fn) in enumerate(SC):
    start = XF if (idx > 0 and SC[idx-1][0] != "intro") else 0  # ya se mostraron en el solape anterior
    for i in range(start, n):
        F = render_scene(idx, i)
        # crossfade con la escena siguiente en sus últimos XF frames (no aplica a intro)
        if idx+1 < len(SC) and i >= n-XF and name != "intro":
            j = i-(n-XF); a = (j+1)/(XF+1)
            G = render_scene(idx+1, j); F = Image.blend(F, G, a)
        p.stdin.write(F.convert("RGB").tobytes()); gi += 1
    print(f"{name}: ok ({gi}/900)", flush=True)
p.stdin.close(); p.wait(); print("render:", A.out, p.returncode)
