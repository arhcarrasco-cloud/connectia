# Reel de cumpleaños · Mi princesa hermosa

Reel vertical (1080×1920, 30 fps) que intercala las fotos y videos del cumple con la carta de Roger,
con fundidos, movimiento suave sobre cada foto (Ken Burns), grade cálido, viñeta, grano fino y música
de piano de fondo generada sin regalías.

## Cómo poner las fotos y videos

El álbum compartido de iCloud no es accesible desde el entorno donde se renderiza el reel, así que el
material se sube a este repositorio:

1. Entra a `reel-cumple/media/` en la rama `claude/birthday-reel-daughter-onxzko` de GitHub.
2. **Add file → Upload files** y arrastra las fotos (JPG, HEIC, PNG) y los videos (MOV, MP4).
   GitHub acepta hasta 25 MB por archivo desde el navegador; si un video pesa más, súbelo con la app
   de GitHub Desktop o compártelo por otra vía.
3. Haz *Commit changes* directo a la rama.

El orden es cronológico (fecha EXIF de la foto o del video). Para forzar un orden distinto crea
`reel-cumple/orden.txt` con un nombre de archivo por línea.

## Higgsfield: fotos que cobran vida

Higgsfield corre desde la Mac de Roger (no es accesible desde el entorno de render). El flujo:

1. Con las fotos ya en `media/`, genera la hoja de prompts:
   `python3 scripts/build_reel.py --prompts` → crea `higgsfield_prompts.md` con un prompt por foto
   (movimiento de cámara sugerido, reglas anti-alucinación, 5 s, 9:16).
2. En Higgsfield, modo **Image to Video**: sube la foto, pega su prompt, motion strength baja.
   Revisa el clip completo antes de aceptarlo (manos, rostros, objetos inventados → regenerar).
3. Guarda cada clip en `reel-cumple/higgsfield/` con el **mismo nombre base que la foto**
   (`IMG_0123.jpg` → `IMG_0123.mp4`; también se aceptan sufijos `_hf`, `_anim`, `_higgsfield`).
4. Vuelve a renderizar. El motor sustituye la foto estática por su clip animado (sin audio, máximo
   `--anim-max` segundos, 5 por defecto) y conserva la foto original como fondo de la tarjeta de texto.

No hace falta animar todas: con 4 a 6 clips en los momentos clave el reel ya se siente vivo; el resto
lleva el Ken Burns del motor.

## Cómo renderizar

```bash
cd reel-cumple
python3 scripts/build_reel.py --version V03
```

Requisitos: `ffmpeg` (6.x), `python3` con `pillow`, `pillow-heif`, `numpy`, `scipy`.
Sin material en `media/`, el script genera placeholders para previsualizar el tratamiento.

Salida: `out/REEL_CUMPLE_PRINCESA_<version>_<fecha>.mp4` y `out/timeline.json`.

## Estructura del reel

| Bloque | Contenido |
|---|---|
| Apertura | "Mi princesa hermosa…" en caligrafía con glow |
| 7 tarjetas | La carta, fragmento por fragmento, sobre la siguiente foto desenfocada |
| Entre tarjetas | Fotos (3.4 s c/u, Ken Burns) y videos (hasta 6 s, con su audio) |
| Cierre | "Feliz cumpleaños, mi princesa hermosa" sobre la última foto |

Parámetros: `--photo-dur` (segundos por foto), `--video-max` (segundos máximos por video),
`--music-gain` (volumen de la música). La música se genera con `scripts/make_music.py` a la medida
de la duración final; para usar otra canción, sustituye `out/work/music.wav` antes del ensamblaje
o cambia la ruta en `build_reel.py`.
