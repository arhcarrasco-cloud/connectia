#!/usr/bin/env python3
"""
Armador del reel de catalogo de Market Pulse MX.

Recorre 01-PRODUCTOS/, elige la mejor toma de cada producto, la anima con un
paneo-zoom lento y ensambla un reel vertical 1080x1920 listo para Reels/TikTok.

No inventa nada: si falta la liga de compra, la musica o la tipografia de marca,
lo dice y sigue sin ese elemento (o se detiene, segun el caso). Respeta las
reglas duras de MPMX: ritmo calmado, zona segura 9:16, cero mencion a impresion
3D, un archivo no esta bien hasta que se abre (QC obligatorio al final).

Uso minimo:
    python3 armar-reel.py --red reels --audio musica.m4a --liga https://...

Ver --help para todo lo demas.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

# ---------------------------------------------------------------- constantes

ANCHO, ALTO = 1080, 1920
FPS = 30

# Zona segura 9:16 de MPMX: nada de texto en 250 px arriba ni 350 px abajo.
SAFE_TOP = 250
SAFE_BOTTOM = 350

# Ventanas por plataforma (BLOQUE F del skill de MPMX).
REDES = {
    # red:      (destino nomenclatura, seg min, seg max, seg objetivo)
    "reels":    ("IG-reel", 7, 90, 70),
    "tiktok":   ("TT-reel", 24, 38, 34),
}

# Ritmo calmado: ningun producto por debajo de 1.4 s ni arriba de 3.5 s.
SEG_MIN, SEG_MAX = 1.4, 3.5

# Nunca decimos que hacemos 3D. Estas palabras no pueden salir en pantalla.
PROHIBIDAS = [
    "3d", "impres", "imprim", "filamento", "pla", "petg", "impresora",
    "capa por capa", "bajo demanda", "gramos", "boquilla", "laminado",
]

EXT_IMG = (".jpg", ".jpeg", ".png", ".webp")
EXT_VID = (".mp4", ".mov", ".m4v")


# ---------------------------------------------------------------- utilidades

def log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def aviso(msg: str) -> None:
    print(f"  [AVISO] {msg}", flush=True)


def morir(msg: str) -> None:
    print(f"\n[ALTO] {msg}\n", file=sys.stderr)
    sys.exit(1)


def correr(cmd: list[str], dry: bool = False, silencioso: bool = True) -> None:
    if dry:
        print("    $ " + " ".join(shlex.quote(c) for c in cmd))
        return
    res = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL if silencioso else None,
        stderr=subprocess.PIPE,
        text=True,
    )
    if res.returncode != 0:
        cola = "\n".join((res.stderr or "").strip().splitlines()[-12:])
        morir(f"ffmpeg fallo:\n$ {' '.join(shlex.quote(c) for c in cmd)}\n{cola}")


def dur_video(archivo: Path) -> float:
    """Duracion de la pista de video. El contenedor puede mentir si el audio es mas largo."""
    info = sondear(archivo)
    for st in info.get("streams", []):
        if st.get("codec_type") == "video":
            if st.get("duration"):
                return float(st["duration"])
            nb, rate = st.get("nb_frames"), st.get("r_frame_rate")
            if nb and rate:
                fps = float(Fraction(rate))
                if fps:
                    return int(nb) / fps
    return float(info.get("format", {}).get("duration", 0) or 0)


def sondear(archivo: Path) -> dict:
    """ffprobe en JSON. Devuelve {} si el archivo no se puede abrir."""
    cmd = [
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(archivo),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {}
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        return {}


def aspecto(archivo: Path) -> float | None:
    """Ancho/alto del archivo, o None si no se pudo leer."""
    info = sondear(archivo)
    for s in info.get("streams", []):
        if s.get("codec_type") == "video" and s.get("width") and s.get("height"):
            return int(s["width"]) / int(s["height"])
    return None


def limpiar_texto(t: str) -> str:
    """Escapa lo que drawtext interpreta."""
    return (
        t.replace("\\", r"\\")
        .replace(":", r"\:")
        .replace("'", "")
        .replace("%", r"\%")
    )


# ---------------------------------------------------------------- catalogo

class Producto:
    def __init__(self, sku: str, carpeta: Path):
        self.sku = sku
        self.carpeta = carpeta
        self.toma: Path | None = None
        self.origen = ""
        self.nombre = ""
        self.es_video = False


def nombre_desde_ficha(carpeta: Path, sku: str) -> str:
    """Primer encabezado de FICHA-CANONICA.md; si no hay, el sku legible."""
    ficha = carpeta / "ficha" / "FICHA-CANONICA.md"
    if ficha.is_file():
        for linea in ficha.read_text(encoding="utf-8", errors="replace").splitlines():
            linea = linea.strip()
            if linea.startswith("#"):
                titulo = linea.lstrip("#").strip()
                if titulo:
                    return titulo
            m = re.match(r"^(?:nombre|producto)\s*:\s*(.+)$", linea, re.I)
            if m:
                return m.group(1).strip()
    limpio = re.sub(r"^[A-Za-z]{1,3}\d{1,3}[-_ ]+", "", sku)
    return (limpio or sku).replace("-", " ").replace("_", " ").strip().title()


def elegir_toma(carpeta: Path) -> tuple[Path | None, str, bool]:
    """
    Mejor material para un reel, en orden de preferencia:
      1. clip de video real del producto  -> lo mejor, ya es movimiento real
      2. derivada 9:16 ya existente (*_IG-reel_* / *_TT-reel_*)
      3. foto de contexto con mano / uso   -> 'producto en uso desde el 1er frame'
      4. foto de contexto cualquiera
      5. foto de Pinterest (2:3, recorta bien)
      6. marketplace fondo blanco          -> ultimo recurso, avisa
    Devuelve (archivo, etiqueta_origen, es_video).
    """
    fotos = carpeta / "fotos"

    vids = sorted(
        p for p in (carpeta / "video").glob("*")
        if p.suffix.lower() in EXT_VID and p.is_file()
    )
    if vids:
        return vids[0], "video real", True

    def imgs(d: Path) -> list[Path]:
        if not d.is_dir():
            return []
        return sorted(p for p in d.rglob("*") if p.suffix.lower() in EXT_IMG and p.is_file())

    todas = imgs(fotos)

    ya_916 = [p for p in todas if re.search(r"_(IG-reel|TT-reel)_", p.name, re.I)]
    if ya_916:
        return ya_916[0], "derivada 9:16", False

    contexto = imgs(fotos / "contexto")
    en_uso = [p for p in contexto if re.search(r"mano|uso|hand|使用", p.name, re.I)]
    if en_uso:
        return en_uso[0], "contexto en uso", False
    if contexto:
        return contexto[0], "contexto", False

    pin = imgs(fotos / "pinterest")
    if pin:
        return pin[0], "pinterest 2:3", False

    mkt = imgs(fotos / "marketplace")
    if mkt:
        return mkt[0], "marketplace blanco", False

    if todas:
        return todas[0], "fotos/ (sin clasificar)", False

    return None, "", False


def leer_catalogo(raiz: Path, solo: list[str], excluir: list[str]) -> list[Producto]:
    base = raiz / "01-PRODUCTOS"
    if not base.is_dir():
        morir(
            f"No existe {base}\n"
            "Este script corre donde vive el catalogo (la Mac de Roger). "
            "Pasa la ruta correcta con --raiz."
        )

    productos: list[Producto] = []
    for carpeta in sorted(p for p in base.iterdir() if p.is_dir()):
        sku = carpeta.name
        if sku.startswith("."):
            continue
        if solo and sku not in solo:
            continue
        if sku in excluir:
            continue
        p = Producto(sku, carpeta)
        p.toma, p.origen, p.es_video = elegir_toma(carpeta)
        p.nombre = nombre_desde_ficha(carpeta, sku)
        productos.append(p)
    return productos


# ---------------------------------------------------------------- render

def filtro_encuadre(asp: float | None, modo: str, ent: str, sal: str) -> str:
    """
    Lleva cualquier toma a 9:16 sin deformarla, de la etiqueta `ent` a `sal`.
      cover -> escala para cubrir y recorta al centro (full bleed)
      blur  -> encaja completa y rellena arriba/abajo con la misma imagen difusa
      auto  -> cover si la fuente es vertical, blur si es horizontal
    Trabaja al doble de resolucion para que el zoom no ablande la imagen.
    """
    w, h = ANCHO * 2, ALTO * 2
    if modo == "auto":
        modo = "cover" if (asp is None or asp <= 0.75) else "blur"

    if modo == "cover":
        return (
            f"[{ent}]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h}[{sal}]"
        )
    # blur: fondo = la misma imagen ampliada y difusa, frente = imagen completa
    return (
        f"[{ent}]split=2[bg][fg];"
        f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
        f"gblur=sigma=42,eq=brightness=-0.06[bgb];"
        f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fgs];"
        f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2[{sal}]"
    )


def filtro_kenburns(dur: float, hacia_dentro: bool) -> str:
    """Paneo-zoom lento y lineal. Ritmo calmado: 6% de recorrido, nada mas."""
    frames = max(2, int(round(dur * FPS)))
    if hacia_dentro:
        z = f"'1+0.06*on/{frames}'"
    else:
        z = f"'1.06-0.06*on/{frames}'"
    return (
        f"zoompan=z={z}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d=1:s={ANCHO}x{ALTO}:fps={FPS}"
    )


def filtro_rotulo(texto: str, fuente: Path | None) -> str:
    """
    Nombre del producto dentro de la zona segura, sin texto griton:
    minuscula, blanco, sombra suave, abajo pero muy por encima de los 350 px.
    """
    y = ALTO - SAFE_BOTTOM - 90
    f = f"fontfile={shlex.quote(str(fuente))}:" if fuente else ""
    return (
        f"drawtext={f}text='{limpiar_texto(texto)}'"
        f":fontcolor=white@0.94:fontsize=46"
        f":shadowcolor=black@0.45:shadowx=0:shadowy=2"
        f":x=(w-text_w)/2:y={y}"
    )


def clip_de_producto(
    p: Producto, dur: float, salida: Path, modo_encuadre: str,
    fuente: Path | None, rotular: bool, hacia_dentro: bool, dry: bool,
) -> None:
    assert p.toma is not None

    # Primer tramo: encuadre a 9:16 (puede traer su propio subgrafo, p.ej. el blur).
    encuadre = filtro_encuadre(aspecto(p.toma), modo_encuadre, "0:v", "enc")

    # Segundo tramo: movimiento, rotulo y formato final, ya en cadena simple.
    resto = []
    if p.es_video:
        entrada = ["-ss", "0", "-t", f"{dur:.3f}", "-i", str(p.toma)]
        resto.append(f"fps={FPS}")
        resto.append(f"scale={ANCHO}:{ALTO}")
    else:
        entrada = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}",
                   "-i", str(p.toma)]
        resto.append(filtro_kenburns(dur, hacia_dentro))
    if rotular:
        resto.append(filtro_rotulo(p.nombre, fuente))
    resto.append("format=yuv420p")

    filtro = f"{encuadre};[enc]{','.join(resto)}[v]"

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        *entrada,
        "-f", "lavfi", "-t", f"{dur:.3f}",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-filter_complex", filtro,
        "-map", "[v]", "-map", "1:a",
        "-r", str(FPS), "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        str(salida),
    ]
    correr(cmd, dry)


def tiene_audio(archivo: Path) -> bool:
    return any(
        st.get("codec_type") == "audio" for st in sondear(archivo).get("streams", [])
    )


def normalizar_clip(origen: Path, salida: Path, dry: bool) -> None:
    """
    Deja un clip oficial (intro/outro) en 1080x1920, 30 fps, h264+aac, sin
    recortarlo ni rehacerlo: solo lo conforma para poder concatenarlo.
    Si el clip no trae audio se le pone una pista muda, porque el concat y el
    acrossfade exigen que todos los clips tengan las mismas pistas.
    """
    filtro = (
        f"[0:v]scale={ANCHO}:{ALTO}:force_original_aspect_ratio=decrease,"
        f"pad={ANCHO}:{ALTO}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"fps={FPS},format=yuv420p[v]"
    )
    con_audio = tiene_audio(origen)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(origen)]
    if not con_audio:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
    cmd += ["-filter_complex", filtro, "-map", "[v]"]
    cmd += ["-map", "0:a"] if con_audio else ["-map", "1:a", "-shortest"]
    cmd += [
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-ac", "2", "-ar", "48000", str(salida),
    ]
    correr(cmd, dry)


def tarjeta_cta(texto: str, liga: str, dur: float, salida: Path,
                fuente: Path | None, dry: bool) -> None:
    """Cierre con la liga de compra: va en toda pieza, tambien en el video."""
    f = f"fontfile={shlex.quote(str(fuente))}:" if fuente else ""
    y1 = ALTO // 2 - 70
    y2 = ALTO // 2 + 20
    filtro = (
        f"color=c=0x1A1A18:s={ANCHO}x{ALTO}:r={FPS}:d={dur:.3f},"
        f"drawtext={f}text='{limpiar_texto(texto)}'"
        f":fontcolor=white@0.95:fontsize=58:x=(w-text_w)/2:y={y1},"
        f"drawtext={f}text='{limpiar_texto(liga)}'"
        f":fontcolor=0xE8C8A0:fontsize=42:x=(w-text_w)/2:y={y2},"
        f"format=yuv420p"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", filtro,
        "-f", "lavfi", "-t", f"{dur:.3f}",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-map", "0:v", "-map", "1:a", "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        str(salida),
    ]
    correr(cmd, dry)


def unir(clips: list[Path], transicion: str, fundido: float,
         salida: Path, tmp: Path, dry: bool) -> None:
    if transicion == "corte" or len(clips) == 1:
        lista = tmp / "concat.txt"
        lista.write_text(
            "".join(f"file {shlex.quote(str(c))}\n" for c in clips), encoding="utf-8"
        )
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(lista),
            "-c", "copy", str(salida),
        ]
        correr(cmd, dry)
        return

    # Fundido: cadena de xfade + acrossfade por pares.
    entradas: list[str] = []
    for c in clips:
        entradas += ["-i", str(c)]

    duraciones = [dur_video(c) for c in clips]
    if min(duraciones) <= fundido:
        morir(f"Hay un clip de {min(duraciones):.2f} s y el fundido es de {fundido} s. "
              "Sube --seg o baja --fundido.")

    partes = []
    vprev, aprev = "0:v", "0:a"
    acum = duraciones[0] if duraciones else 0.0
    for i in range(1, len(clips)):
        vo, ao = f"v{i}", f"a{i}"
        offset = max(0.0, acum - fundido)
        partes.append(
            f"[{vprev}][{i}:v]xfade=transition=fade:duration={fundido}:offset={offset:.3f}[{vo}]"
        )
        partes.append(f"[{aprev}][{i}:a]acrossfade=d={fundido}[{ao}]")
        vprev, aprev = vo, ao
        acum = offset + (duraciones[i] if i < len(duraciones) else 0.0)

    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        *entradas,
        "-filter_complex", ";".join(partes),
        "-map", f"[{vprev}]", "-map", f"[{aprev}]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        str(salida),
    ]
    correr(cmd, dry)


def poner_musica(video: Path, audio: Path, salida: Path, dry: bool) -> None:
    """Musica a -14 LUFS, entrada suave y salida con fundido de 1.2 s."""
    dur = dur_video(video)
    filtro = (
        f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{dur:.3f},"
        f"loudnorm=I=-14:TP=-1.5:LRA=11,"
        f"afade=t=in:st=0:d=0.4,afade=t=out:st={max(0.0, dur - 1.2):.3f}:d=1.2[mus]"
    )
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(video), "-i", str(audio),
        "-filter_complex", filtro,
        "-map", "0:v", "-map", "[mus]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", f"{dur:.3f}", str(salida),
    ]
    correr(cmd, dry)


# ---------------------------------------------------------------- QC

def qc(salida: Path, red: str, esperado_prods: int, esperado_dur: float) -> None:
    """Un archivo no es el que crees hasta que lo abres."""
    print("\n== QC ==")
    info = sondear(salida)
    if not info:
        morir(f"{salida} no se puede abrir con ffprobe. No se entrega.")

    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = dur_video(salida)
    peso = int(info["format"]["size"]) / 1e6

    if not v:
        morir("El archivo no trae pista de video.")
    log(f"resolucion .... {v['width']}x{v['height']}"
        + ("  OK" if (v["width"], v["height"]) == (ANCHO, ALTO) else "  <-- NO es 1080x1920"))
    log(f"fps ........... {float(Fraction(v['r_frame_rate'])):g}")
    log(f"codec ......... {v['codec_name']} / {v.get('pix_fmt')}")
    desfase = abs(dur - esperado_dur)
    log(f"duracion ...... {dur:.2f} s  (esperado {esperado_dur:.2f} s)"
        + ("" if desfase <= 0.6 else f"  <-- se desvia {desfase:.2f} s"))
    log(f"audio ......... {a['codec_name'] + ' ' + str(a.get('channels')) + 'ch' if a else 'SIN AUDIO'}")
    log(f"peso .......... {peso:.1f} MB")

    _, smin, smax, _ = REDES[red]
    if not (smin <= dur <= smax):
        aviso(f"{dur:.1f} s queda fuera de la ventana de {red} ({smin}-{smax} s).")
    if not a:
        aviso("Sin audio: Reels y TikTok castigan el video mudo. Pasa --audio.")

    hoja = salida.parent / "qc" / f"{salida.stem}-contactsheet.jpg"
    hoja.parent.mkdir(parents=True, exist_ok=True)
    muestreo = max(0.1, 30.0 / dur) if dur else 1.0
    correr([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(salida),
        "-vf", f"fps={muestreo:.4f},scale=216:384,tile=6x5",
        "-frames:v", "1", str(hoja),
    ])
    log(f"contact sheet . {hoja}")
    print("\n  Abre el MP4 y el contact sheet antes de publicar. "
          f"Deben salir los {esperado_prods} productos y ningun cuadro en blanco.")


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Arma el reel de catalogo de Market Pulse MX (9:16, 1080x1920).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument("--raiz", type=Path,
                    default=Path.home() / "Documents" / "Market-Pulse-MX",
                    help="Raiz operativa de MPMX")
    ap.add_argument("--red", choices=sorted(REDES), default="reels")
    ap.add_argument("--audio", type=Path, help="Pista de musica (obligatoria en la practica)")
    ap.add_argument("--liga", help="Liga de compra que aparece en la tarjeta de cierre")
    ap.add_argument("--cta", default="hecho por pedido en Mexico",
                    help="Linea de cierre arriba de la liga")
    ap.add_argument("--seg", type=float,
                    help="Segundos por producto (por omision se calcula para la red)")
    ap.add_argument("--encuadre", choices=["auto", "cover", "blur"], default="auto")
    ap.add_argument("--transicion", choices=["fundido", "corte"], default="fundido")
    ap.add_argument("--fundido", type=float, default=0.3, help="Duracion del fundido")
    ap.add_argument("--sin-rotulo", action="store_true",
                    help="No poner el nombre del producto en pantalla")
    ap.add_argument("--fuente", type=Path, help="Tipografia (Cooper Hewitt de MPMX)")
    ap.add_argument("--intro", type=Path, help="Clip de intro oficial (no se regenera)")
    ap.add_argument("--outro", type=Path, help="Clip de outro oficial (no se regenera)")
    ap.add_argument("--solo", default="", help="SKUs separados por coma")
    ap.add_argument("--excluir", default="", help="SKUs a saltar, separados por coma")
    ap.add_argument("--salida", type=Path, help="MP4 de salida")
    ap.add_argument("--dry-run", action="store_true", help="Solo imprime los comandos")
    args = ap.parse_args()

    for bin_ in ("ffmpeg", "ffprobe"):
        if not shutil.which(bin_):
            morir(f"Falta {bin_} en el PATH.")

    destino, smin, smax, objetivo = REDES[args.red]

    print(f"\n== Catalogo ==")
    productos = leer_catalogo(
        args.raiz,
        [s.strip() for s in args.solo.split(",") if s.strip()],
        [s.strip() for s in args.excluir.split(",") if s.strip()],
    )
    if not productos:
        morir(f"No se encontro ningun producto en {args.raiz / '01-PRODUCTOS'}.")

    usables = [p for p in productos if p.toma]
    for p in productos:
        if not p.toma:
            aviso(f"{p.sku}: sin foto ni video usable, queda fuera.")
        else:
            marca = "  <-- fondo blanco, es para marketplace, no para reel" \
                if p.origen == "marketplace blanco" else ""
            log(f"{p.sku:<28} {p.origen:<22} {p.toma.name}{marca}")
    if not usables:
        morir("Ningun producto tiene material usable.")

    # Copy: nunca decimos que hacemos 3D, ni en pantalla.
    sucios = [
        (p.sku, w) for p in usables for w in PROHIBIDAS
        if w in p.nombre.lower()
    ]
    if sucios and not args.sin_rotulo:
        for sku, w in sucios:
            aviso(f"{sku}: el nombre contiene '{w}', palabra prohibida en pantalla.")
        morir("Corrige los nombres en las fichas o corre con --sin-rotulo.")

    # Ritmo: los segundos por producto salen de la ventana de la red.
    # Cada fundido solapa dos clips, asi que resta a la duracion final.
    n = len(usables)
    cierre = 2.5 if args.liga else 0.0
    d_intro = dur_video(args.intro) if args.intro and args.intro.is_file() else 0.0
    d_outro = dur_video(args.outro) if args.outro and args.outro.is_file() else 0.0
    fijos = cierre + d_intro + d_outro
    n_clips = n + (1 if cierre else 0) + (1 if d_intro else 0) + (1 if d_outro else 0)
    solape = args.fundido * max(0, n_clips - 1) if args.transicion == "fundido" else 0.0

    if args.seg:
        seg = args.seg
    else:
        seg = (objetivo - fijos + solape) / n
        seg = max(SEG_MIN, min(SEG_MAX, seg))
    total = seg * n + fijos - solape

    print(f"\n== Ritmo ==")
    detalle = f"{n} productos x {seg:.2f} s"
    if d_intro:
        detalle += f" + intro {d_intro:.1f} s"
    if cierre:
        detalle += f" + cierre {cierre:.1f} s"
    if d_outro:
        detalle += f" + outro {d_outro:.1f} s"
    if solape:
        detalle += f" - {solape:.1f} s de fundidos"
    log(f"{detalle} = {total:.1f} s")

    if total > smax:
        caben = int((smax - fijos + solape) / SEG_MIN)
        aviso(f"{total:.0f} s pasa el maximo de {args.red} ({smax} s). "
              f"A ritmo calmado caben ~{caben} productos: "
              f"parte el catalogo en varios reels con --solo.")
    elif total < smin:
        aviso(f"{total:.0f} s no llega al minimo de {args.red} ({smin} s). "
              "Sube --seg o suma productos.")
    if seg <= SEG_MIN + 0.01 and total <= smax:
        aviso(f"{seg:.2f} s por producto es el piso de ritmo calmado.")

    if not args.liga:
        aviso("Sin --liga: el reel sale sin liga de compra, y la liga va en toda pieza.")
    if not args.audio:
        aviso("Sin --audio: el reel sale mudo.")
    elif not args.audio.is_file():
        morir(f"No existe el audio {args.audio}")

    fuente = args.fuente
    if fuente is None:
        tipos = args.raiz / "00-MARCA" / "tipografias"
        if tipos.is_dir():
            fuente = next(
                (c for c in sorted(tipos.rglob("*"))
                 if c.suffix.lower() in (".ttf", ".otf") and "cooper" in c.name.lower()),
                None,
            )
    if fuente and not Path(fuente).is_file():
        morir(f"No existe la tipografia {fuente}")
    if fuente:
        log(f"tipografia .... {fuente.name}")
    else:
        aviso("Sin Cooper Hewitt: drawtext usara la fuente por omision de ffmpeg.")

    hoy = dt.date.today().isoformat()
    salida = args.salida or (
        args.raiz / "02-CONTENIDO" / hoy / args.red /
        f"CATALOGO_{destino}_todos_v1.mp4"
    )
    salida.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n== Render ==")
    tmp = Path(tempfile.mkdtemp(prefix="mpmx-reel-"))
    try:
        clips: list[Path] = []
        if args.intro:
            if not args.intro.is_file():
                morir(f"No existe el intro {args.intro}")
            c = tmp / "000-intro.mp4"
            log("intro oficial (se conforma, no se regenera)")
            normalizar_clip(args.intro, c, args.dry_run)
            clips.append(c)

        for i, p in enumerate(usables):
            c = tmp / f"{i:03d}-{p.sku}.mp4"
            log(f"[{i+1}/{n}] {p.sku}")
            clip_de_producto(
                p, seg, c, args.encuadre, fuente,
                not args.sin_rotulo, hacia_dentro=(i % 2 == 0), dry=args.dry_run,
            )
            clips.append(c)

        if args.liga:
            c = tmp / "zzz-cta.mp4"
            log("cierre con liga de compra")
            tarjeta_cta(args.cta, args.liga, cierre, c, fuente, args.dry_run)
            clips.append(c)

        if args.outro:
            if not args.outro.is_file():
                morir(f"No existe el outro {args.outro}")
            c = tmp / "zzzz-outro.mp4"
            log("outro oficial (se conforma, no se regenera)")
            normalizar_clip(args.outro, c, args.dry_run)
            clips.append(c)

        if args.dry_run:
            print("\n(dry-run: no se escribio nada)")
            return

        cuerpo = tmp / "cuerpo.mp4"
        log(f"uniendo {len(clips)} clips ({args.transicion})")
        unir(clips, args.transicion, args.fundido, cuerpo, tmp, args.dry_run)

        if args.audio:
            log("musica a -14 LUFS")
            poner_musica(cuerpo, args.audio, salida, args.dry_run)
        else:
            shutil.copy2(cuerpo, salida)

        print(f"\n  {salida}")
        qc(salida, args.red, n, total)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
