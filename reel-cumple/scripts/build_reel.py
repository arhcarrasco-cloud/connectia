#!/usr/bin/env python3
"""Arma el reel emotivo de cumpleaños (1080x1920, 30 fps) a partir de fotos/videos + la carta de Roger.

Uso:
  python3 scripts/build_reel.py                 # usa reel-cumple/media/ (o placeholders si está vacía)
  python3 scripts/build_reel.py --placeholders  # fuerza placeholders de previsualización

Salida: reel-cumple/out/REEL_CUMPLE_PRINCESA_<version>.mp4 + out/timeline.json
Orden opcional: reel-cumple/orden.txt (un nombre de archivo por línea) manda sobre el orden cronológico.
"""
import os, sys, json, glob, math, argparse, subprocess, datetime, shutil, random
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
try:
    import pillow_heif; pillow_heif.register_heif_opener()
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
XF = 0.9            # duración de cada fundido entre segmentos
PHOTO_DUR = 3.4     # segundos por foto (sin contar fundidos)
VIDEO_MAX = 6.0     # máximo por clip de video
FONTS = {
    "script": os.path.join(ROOT, "fonts", "GreatVibes-Regular.ttf"),
    "body": os.path.join(ROOT, "fonts", "CormorantGaramond-MediumItalic.ttf"),
    "body_up": os.path.join(ROOT, "fonts", "CormorantGaramond-Medium.ttf"),
    "small": os.path.join(ROOT, "fonts", "Montserrat-Regular.ttf"),
}
IMG_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}
VID_EXT = {".mp4", ".mov", ".m4v", ".hevc", ".avi", ".mkv", ".3gp"}

# ---------------------------------------------------------------- texto (palabras de Roger, solo puntuación)
CARDS = [
    {"kind": "title", "text": "Mi princesa hermosa…"},
    {"kind": "body", "text": "No te puedo explicar lo largas que fueron esas primeras dos semanas cuando naciste y no pudimos tenerte en casa…"},
    {"kind": "body", "text": "Pero ¿sabes? Desde ahí, desde el día cero, nos diste una lección enorme de fuerza y ganas de avanzar."},
    {"kind": "body", "text": "Llegaste a darnos luz en el momento exacto."},
    {"kind": "body", "text": "Gracias por darnos todos los días esa sonrisa llena de vida y amor, y por hacer que despertarse cada mañana y verte gritar sea un motivo más."},
    {"kind": "body", "text": "Gracias por tu sonrisa, por tu felicidad y por hacernos los más felices del mundo."},
    {"kind": "body", "text": "No sé qué hice en otra vida, pero definitivamente algo muy bueno."},
    {"kind": "body", "text": "Soy bendecido en tener a tu mami, a tu hermano, a los peludos y a ti, mi amor."},
    {"kind": "final", "text": "Feliz cumpleaños,|mi princesa hermosa"},
]

def run(cmd, quiet=True):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        print("\n".join(cmd)); print(r.stderr[-4000:]); raise SystemExit(f"ffmpeg falló: {cmd[-1]}")
    return r

def ffprobe_json(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
                       stdout=subprocess.PIPE, text=True)
    return json.loads(r.stdout or "{}")

# ---------------------------------------------------------------- ingesta
def media_date(path, kind):
    try:
        if kind == "photo":
            im = Image.open(path)
            ex = im.getexif()
            d = ex.get(36867) or ex.get(306)
            if not d:
                try:
                    d = ex.get_ifd(0x8769).get(36867)
                except Exception:
                    d = None
            if d:
                return datetime.datetime.strptime(str(d)[:19], "%Y:%m:%d %H:%M:%S")
        else:
            info = ffprobe_json(path)
            tags = info.get("format", {}).get("tags", {})
            d = tags.get("creation_time") or tags.get("com.apple.quicktime.creationdate")
            if d:
                return datetime.datetime.fromisoformat(d.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        pass
    return datetime.datetime.fromtimestamp(os.path.getmtime(path))

def scan_media(folder):
    items = []
    for p in sorted(glob.glob(os.path.join(folder, "*"))):
        ext = os.path.splitext(p)[1].lower()
        if ext in IMG_EXT:
            items.append({"path": p, "kind": "photo"})
        elif ext in VID_EXT:
            items.append({"path": p, "kind": "video"})
    for it in items:
        it["date"] = media_date(it["path"], it["kind"])
    order_file = os.path.join(folder, "..", "orden.txt")
    if os.path.exists(order_file):
        wanted = [l.strip() for l in open(order_file, encoding="utf-8") if l.strip() and not l.startswith("#")]
        by_name = {os.path.basename(i["path"]): i for i in items}
        ordered = [by_name[n] for n in wanted if n in by_name]
        rest = [i for i in items if os.path.basename(i["path"]) not in wanted]
        rest.sort(key=lambda i: i["date"])
        items = ordered + rest
    else:
        items.sort(key=lambda i: i["date"])
    return items

# ---------------------------------------------------------------- placeholders de previsualización
def make_placeholders(folder, n_photos=10, n_videos=2):
    os.makedirs(folder, exist_ok=True)
    pal = [((255, 214, 196), (214, 181, 224)), ((255, 228, 214), (186, 214, 235)), ((250, 205, 215), (255, 236, 200)),
           ((222, 205, 240), (255, 220, 214)), ((255, 240, 218), (214, 226, 246))]
    font = ImageFont.truetype(FONTS["small"], 44)
    big = ImageFont.truetype(FONTS["script"], 220)
    k = 0
    for i in range(n_photos):
        c1, c2 = pal[i % len(pal)]
        w, h = (1080, 1440) if i % 3 else (1440, 1080)
        im = Image.new("RGB", (w, h))
        px = im.load()
        for y in range(h):
            t = y / h
            col = tuple(int(c1[j] * (1 - t) + c2[j] * t) for j in range(3))
            for x in range(w):
                px[x, y] = col
        d = ImageDraw.Draw(im)
        d.text((w / 2, h / 2 - 60), f"{i+1}", fill=(255, 255, 255), font=big, anchor="mm")
        d.text((w / 2, h / 2 + 120), f"FOTO {i+1:02d} · aquí va tu foto", fill=(255, 255, 255), font=font, anchor="mm")
        p = os.path.join(folder, f"placeholder_{k:02d}.jpg"); k += 1
        im.save(p, quality=90)
        t0 = datetime.datetime(2025, 9, 9, 10, 0) + datetime.timedelta(days=30 * i)
        os.utime(p, (t0.timestamp(), t0.timestamp()))
    for i in range(n_videos):
        p = os.path.join(folder, f"placeholder_video_{i+1:02d}.mp4")
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x{'d6b5e0' if i==0 else 'ffd6c4'}:s=1080x1920:r=30:d=5",
             "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000:duration=5",
             "-vf", f"drawtext=fontfile={FONTS['small']}:text='VIDEO {i+1:02d} · aquí va tu video':fontsize=44:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
             "-af", "volume=0.15", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", p])
        t0 = datetime.datetime(2025, 9, 9, 10, 0) + datetime.timedelta(days=30 * (4 + 4 * i), hours=1)
        os.utime(p, (t0.timestamp(), t0.timestamp()))

# ---------------------------------------------------------------- composición de imagen (fondo desenfocado + foto)
def compose_photo(src, dst, scale=2):
    """Foto ajustada a lo ancho sobre un fondo desenfocado y oscurecido. Salida 2x para un Ken Burns suave."""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    cw, ch = W * scale, H * scale
    # fondo
    bg = ImageOps.fit(im, (cw // 4, ch // 4), method=Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
    bg = bg.resize((cw, ch), Image.BICUBIC)
    bg = Image.blend(bg, Image.new("RGB", (cw, ch), (12, 8, 10)), 0.42)
    # foto
    r = min(cw / im.width, ch / im.height)
    fw, fh = int(im.width * r), int(im.height * r)
    if fw < cw and fh < ch:  # no cabe a lo ancho ni a lo alto: ajustar a lo ancho
        r = cw / im.width; fw, fh = cw, int(im.height * r)
    fg = im.resize((fw, min(fh, ch)), Image.LANCZOS)
    if fh > ch:
        fg = ImageOps.fit(im, (cw, ch), method=Image.LANCZOS)
    # sombra suave
    if fg.height < ch or fg.width < cw:
        sh = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        x0, y0 = (cw - fg.width) // 2, (ch - fg.height) // 2
        d.rectangle([x0 - 6, y0 + 10, x0 + fg.width + 6, y0 + fg.height + 26], fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(24))
        bg = Image.alpha_composite(bg.convert("RGBA"), sh).convert("RGB")
    bg.paste(fg, ((cw - fg.width) // 2, (ch - fg.height) // 2))
    bg.save(dst, quality=94)
    return dst

def blurred_bg(src, dst):
    """Fondo para tarjetas de texto: la foto vecina, desenfocada y muy oscurecida (2x)."""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    cw, ch = W * 2, H * 2
    bg = ImageOps.fit(im, (cw // 4, ch // 4), method=Image.LANCZOS).filter(ImageFilter.GaussianBlur(22))
    bg = bg.resize((cw, ch), Image.BICUBIC)
    bg = Image.blend(bg, Image.new("RGB", (cw, ch), (10, 6, 9)), 0.66)
    bg.save(dst, quality=92)
    return dst

def video_still(src, dst):
    run(["ffmpeg", "-y", "-ss", "1", "-i", src, "-frames:v", "1", "-q:v", "2", dst])
    return dst

# ---------------------------------------------------------------- texto
def wrap(text, font_path, size, max_w):
    font = ImageFont.truetype(font_path, size)
    lines = []
    for para in text.split("|"):
        words, cur = para.split(), ""
        for w_ in words:
            t = (cur + " " + w_).strip()
            if font.getlength(t) <= max_w or not cur:
                cur = t
            else:
                lines.append(cur); cur = w_
        if cur:
            lines.append(cur)
    return lines

def esc(s):
    return s.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "\\%").replace(",", "\\,")

def drawtext_lines(lines, font_path, size, color, y_center, dur, fade=0.9, spacing=1.32, delay=0.0, extra=""):
    alpha = f"if(lt(t\\,{delay}),0,if(lt(t\\,{delay+fade}),(t-{delay})/{fade},if(lt(t\\,{dur-fade}),1,max(0\\,({dur}-t)/{fade}))))"
    lh = size * spacing
    total = lh * len(lines)
    y0 = y_center - total / 2
    parts = []
    for i, ln in enumerate(lines):
        y = y0 + i * lh
        parts.append(f"drawtext=fontfile='{font_path}':text='{esc(ln)}':fontsize={size}:fontcolor={color}:"
                     f"x=(w-text_w)/2:y={y:.0f}:alpha='{alpha}'{extra}")
    return ",".join(parts)

def zoompan_expr(frames, mode):
    """Ken Burns: (z_ini, z_fin, pan) suaves con easing."""
    z0, z1, px0, px1, py0, py1 = {
        "in_center": (1.00, 1.14, .5, .5, .5, .5), "in_up": (1.00, 1.16, .5, .5, .58, .42),
        "out_center": (1.15, 1.00, .5, .5, .5, .5), "out_down": (1.16, 1.02, .5, .5, .42, .56),
        "pan_lr": (1.12, 1.12, .32, .68, .5, .5), "pan_rl": (1.12, 1.12, .68, .32, .5, .5),
        "in_left": (1.00, 1.15, .5, .38, .5, .5), "slow": (1.00, 1.06, .5, .5, .5, .5),
    }[mode]
    p = f"(1-cos(PI*on/{frames}))/2"  # easing in-out 0→1
    z = f"({z0}+({z1}-{z0})*{p})"
    px = f"({px0}+({px1}-{px0})*{p})"
    py = f"({py0}+({py1}-{py0})*{p})"
    return f"zoompan=z='{z}':x='(iw-iw/zoom)*{px}':y='(ih-ih/zoom)*{py}':d={frames}:s={W}x{H}:fps={FPS}"

# ---------------------------------------------------------------- segmentos
ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

def seg_photo(comp, dst, dur, mode):
    frames = int(round(dur * FPS))
    vf = f"{zoompan_expr(frames, mode)},format=yuv420p"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", comp, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-t", f"{dur:.3f}", "-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "1:a", *ENC, dst])
    return dur

def seg_video(src, dst, maxdur):
    info = ffprobe_json(src)
    d = float(info.get("format", {}).get("duration", maxdur))
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    take = min(maxdur, d)
    start = max(0.0, min(d - take, d * 0.12)) if d > maxdur else 0.0
    vf = (f"[0:v]fps={FPS},split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=30,"
          f"colorlevels=rimax=0.6:gimax=0.6:bimax=0.6[bg];"
          f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]")
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-t", f"{take:.3f}", "-i", src]
    if has_audio:
        af = "[0:a]aresample=48000,dynaudnorm=g=11:p=0.85,volume=0.9,afade=t=in:d=0.5[a]"
        cmd += ["-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex", vf, "-map", "[v]", "-map", "1:a"]
    cmd += ["-t", f"{take:.3f}", *ENC, dst]
    run(cmd)
    return take

def seg_card(bg2x, dst, card, dur):
    frames = int(round(dur * FPS))
    base = f"[0:v]{zoompan_expr(frames, 'slow')},format=rgba"
    if card["kind"] == "title":
        lines = wrap(card["text"], FONTS["script"], 150, 960)
        glow = drawtext_lines(lines, FONTS["script"], 150, "0xFFE6C8@0.9", H * 0.47, dur, spacing=1.1)
        txt = drawtext_lines(lines, FONTS["script"], 150, "0xFFF6EA", H * 0.47, dur, spacing=1.1)
        fc = (f"{base}[bg];color=c=black@0.0:s={W}x{H}:r={FPS}:d={dur:.3f},format=rgba,{glow},gblur=sigma=26[gl];"
              f"[bg][gl]overlay=format=auto[b2];[b2]{txt},format=yuv420p[v]")
    elif card["kind"] == "final":
        lines = wrap(card["text"], FONTS["script"], 132, 980)
        glow = drawtext_lines(lines, FONTS["script"], 132, "0xFFD9B0@0.95", H * 0.50, dur, spacing=1.12)
        txt = drawtext_lines(lines, FONTS["script"], 132, "0xFFFBF3", H * 0.50, dur, spacing=1.12)
        fc = (f"{base}[bg];color=c=black@0.0:s={W}x{H}:r={FPS}:d={dur:.3f},format=rgba,{glow},gblur=sigma=30[gl];"
              f"[bg][gl]overlay=format=auto[b2];[b2]{txt},format=yuv420p[v]")
    else:
        size = 76 if len(card["text"]) < 90 else 68
        lines = wrap(card["text"], FONTS["body"], size, 920)
        txt = drawtext_lines(lines, FONTS["body"], size, "0xFFF4E6", H * 0.5, dur, spacing=1.34,
                             extra=":shadowcolor=black@0.45:shadowx=0:shadowy=2")
        line = (f"drawbox=x={W//2-40}:y={int(H*0.5 - size*1.34*len(lines)/2 - 46)}:w=80:h=2:color=0xFFD9B0@0.7:t=fill:"
                f"enable='between(t\\,0.9\\,{dur-0.9:.2f})'")
        fc = f"{base},{line},{txt},format=yuv420p[v]"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", bg2x, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-t", f"{dur:.3f}", "-filter_complex", fc, "-map", "[v]", "-map", "1:a", *ENC, dst])
    return dur

def card_duration(card):
    if card["kind"] == "title":
        return 4.2
    if card["kind"] == "final":
        return 7.0
    words = len(card["text"].split())
    return max(4.2, min(7.5, 1.9 + words * 0.26))

# ---------------------------------------------------------------- plan
def plan(media):
    """Intercala las tarjetas con el material, en orden cronológico."""
    slots = len(CARDS) - 1
    n = len(media)
    groups = [[] for _ in range(slots)]
    if n:
        for i, m in enumerate(media):
            groups[min(slots - 1, i * slots // n)].append(m)
    timeline = []
    for ci, card in enumerate(CARDS):
        timeline.append({"type": "card", "card": card})
        if ci < slots:
            for m in groups[ci]:
                timeline.append({"type": m["kind"], "path": m["path"]})
    return timeline

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", default=os.path.join(ROOT, "media"))
    ap.add_argument("--placeholders", action="store_true")
    ap.add_argument("--version", default="V01")
    ap.add_argument("--photo-dur", type=float, default=PHOTO_DUR)
    ap.add_argument("--video-max", type=float, default=VIDEO_MAX)
    ap.add_argument("--music-gain", type=float, default=1.0)
    args = ap.parse_args()

    out = os.path.join(ROOT, "out"); work = os.path.join(out, "work"); segd = os.path.join(out, "segs")
    for d in (out, work, segd):
        os.makedirs(d, exist_ok=True)
    media = [] if args.placeholders else scan_media(args.media)
    if not media:
        ph = os.path.join(work, "placeholders")
        if not glob.glob(os.path.join(ph, "*")):
            make_placeholders(ph)
        media = scan_media(ph)
        print(f"Sin material en {args.media}: usando {len(media)} placeholders de previsualización.")
    print(f"Material: {len(media)} archivos ({sum(m['kind']=='photo' for m in media)} fotos, {sum(m['kind']=='video' for m in media)} videos)")

    tl = plan(media)
    # stills para fondos de tarjetas
    stills = {}
    for i, it in enumerate(tl):
        if it["type"] == "video":
            stills[it["path"]] = video_still(it["path"], os.path.join(work, f"still_{i:02d}.jpg"))
        elif it["type"] == "photo":
            stills[it["path"]] = it["path"]
    modes = ["in_center", "pan_lr", "out_center", "in_up", "pan_rl", "out_down", "in_left"]
    segs = []
    for i, it in enumerate(tl):
        dst = os.path.join(segd, f"seg_{i:02d}.mp4")
        if it["type"] == "card":
            # fondo: la siguiente foto/video; si no hay, la anterior
            nb = next((tl[j] for j in range(i + 1, len(tl)) if tl[j]["type"] != "card"), None) or \
                 next((tl[j] for j in range(i - 1, -1, -1) if tl[j]["type"] != "card"), None)
            bg = blurred_bg(stills[nb["path"]], os.path.join(work, f"cardbg_{i:02d}.jpg"))
            dur = seg_card(bg, dst, it["card"], card_duration(it["card"]))
            label = it["card"]["text"][:40]
        elif it["type"] == "photo":
            comp = compose_photo(it["path"], os.path.join(work, f"comp_{i:02d}.jpg"))
            dur = seg_photo(comp, dst, args.photo_dur, modes[i % len(modes)])
            label = os.path.basename(it["path"])
        else:
            dur = seg_video(it["path"], dst, args.video_max)
            label = os.path.basename(it["path"])
        segs.append({"i": i, "type": it["type"], "file": dst, "dur": dur, "label": label})
        print(f"  [{i:02d}] {it['type']:5s} {dur:5.2f}s  {label}")

    # línea de tiempo con fundidos
    total = sum(s["dur"] for s in segs) - XF * (len(segs) - 1)
    t = 0.0
    for k, s in enumerate(segs):
        s["start"] = t
        t += s["dur"] - (XF if k < len(segs) - 1 else 0)
    print(f"Duración total: {total:.1f}s")

    # música a la medida
    music = os.path.join(out, "work", "music.wav")
    run(["python3", os.path.join(ROOT, "scripts", "make_music.py"), music, f"{total + 0.5:.2f}"])

    # ensamblaje: xfade + acrossfade encadenados, grade, grano, mezcla con ducking
    inputs = []
    for s in segs:
        inputs += ["-i", s["file"]]
    inputs += ["-i", music]
    n = len(segs)
    fc = []
    vprev, aprev, off = "[0:v]", "[0:a]", 0.0
    transitions = ["fade", "fade", "fade", "fadeblack", "fade", "dissolve"]
    for k in range(1, n):
        off += segs[k - 1]["dur"] - XF
        tr = "fadeblack" if (segs[k]["type"] == "card" and segs[k]["card"] if False else False) else transitions[k % len(transitions)]
        if segs[k]["type"] == "card":
            tr = "fade"
        fc.append(f"{vprev}[{k}:v]xfade=transition={tr}:duration={XF}:offset={off:.3f}[v{k}]")
        fc.append(f"{aprev}[{k}:a]acrossfade=d={XF}:c1=tri:c2=tri[a{k}]")
        vprev, aprev = f"[v{k}]", f"[a{k}]"
    grade = ("colorbalance=rs=0.02:gs=0.0:bs=-0.03:rm=0.02:bm=-0.02:rh=0.03:bh=-0.02,"
             "eq=saturation=1.06:contrast=1.04:brightness=0.005,"
             "vignette=angle=PI/4.6:mode=forward,"
             "noise=alls=5:allf=t+u,"
             f"fade=t=in:st=0:d=1.2,fade=t=out:st={total-1.5:.2f}:d=1.5,format=yuv420p")
    fc.append(f"{vprev}{grade}[vout]")
    fc.append(f"[{n}:a]volume={0.85*args.music_gain:.2f},afade=t=in:d=2.5,afade=t=out:st={total-4:.2f}:d=4[m]")
    fc.append(f"{aprev}asplit[ac1][ac2]")
    fc.append("[m][ac2]sidechaincompress=threshold=0.035:ratio=5:attack=250:release=1200:makeup=1[md]")
    fc.append("[ac1][md]amix=inputs=2:duration=first:dropout_transition=3:normalize=0,alimiter=limit=0.95,aresample=48000[aout]")
    final = os.path.join(out, f"REEL_CUMPLE_PRINCESA_{args.version}_{datetime.date.today().isoformat()}.mp4")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
         "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-level", "4.1",
         "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", final])
    json.dump({"total": total, "segments": segs, "xfade": XF}, open(os.path.join(out, "timeline.json"), "w"), indent=2, ensure_ascii=False)
    print(f"\nListo: {final}")

if __name__ == "__main__":
    main()
