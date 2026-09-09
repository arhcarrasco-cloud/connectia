# Reel KAVAK · casco + cápsulas · once once LAB

Reel comercial vertical (1080×1920, 30 fps, 30 s) con intro y outro de **once once LAB**
y el proyecto KAVAK (casco impreso en 3D + lote de cápsulas PETG).

## Estructura (30.0 s)

| t | Escena | Fuente |
|---|---|---|
| 0.0–2.5 | Intro once once LAB (sello master, anillo girando, "LO HACEMOS REALIDAD") | `brand/oncelablogomaster.svg` |
| 2.5–6.0 | Hook: casco KAVAK, push-in | `photos/casco.jpg` |
| 6.0–11.0 | **Slot timelapse casco** (`--casco`) | stand-in: `brand/bambu_intro.mp4` |
| 11.0–14.0 | Cápsulas a la medida, pan | `photos/capsulas_caja.jpg` |
| 14.0–19.0 | **Slot timelapse cápsulas** (`--capsulas`) | stand-in: primera capa real P1S `src/video_2026-08-22_11-36-38.avi` |
| 19.0–23.0 | Activación / merch | `photos/playera.jpg` |
| 23.0–26.5 | Claim split casco + cápsulas: "Lo imaginaste. Lo imprimimos." | fotos |
| 26.5–30.0 | Outro once once LAB + "Impresión 3D · Sublimación · CDMX" | logo master |

## Render

```bash
pip install pillow numpy cairosvg imageio-ffmpeg   # ffmpeg en PATH
python3 build_reel.py OUT.mp4                       # versión V01 con stand-ins
python3 build_reel.py OUT.mp4 \
  --casco    "~/Bambu/timelapse/P1S UNO/video_2026-08-16_05-23-14.avi" \
  --capsulas "~/Bambu/timelapse/P1S DOS/video_2026-08-18_12-26-10.avi"
```

Los timelapses de Bambu (1280×720 MJPEG) entran en el layout "panel editorial"
(fondo Negro Tinta, clip 16:9 centrado, titular arriba, etiqueta mono abajo) sin
reencuadre destructivo. Se toman los primeros 5.4 s del archivo; si el timelapse es
largo, recórtalo antes con `ffmpeg -ss … -t 5.4` o acelera con `setpts`.

## Timelapses candidatos en Drive (`once once LAB/Timelapses`)

El tamaño del `.avi` es proporcional al número de capas:

- **Casco** (impresión alta, ~1000 capas): `P1S UNO/video_2026-08-16_05-23-14.avi` (74 MB)
  y `P1S TRES/video_2026-08-17_13-30-28.avi` (66 MB, probable máscara/segunda pieza).
- **Cápsulas** (placas de medias esferas, lotes repetidos 18–20 ago, 13–16 MB):
  `P1S DOS/video_2026-08-18_12-26-10.avi`, `…08-18_11-05-28.avi`, `…08-19_23-14-50.avi`,
  `…08-20_08-15-03.avi`, `P1S UNO/video_2026-08-19_22-12-19.avi`.

Los archivos < 3 MB de esa carpeta son impresiones abortadas (cama vacía).

## Marca (Manual de identidad once LAB v2.1)

- Rosa Once `#F0246B` · Negro Tinta `#151217` · Blanco Placa · Crema Matte `#F0E7D3`
- Display: Archivo ExtraBold 800, wdth 112 · Texto: Instrument Sans · Técnica: IBM Plex Mono
- Logo: siempre el sello master completo (círculo + anillo punteado + 11/once/LAB).

## Higgsfield (mejora de intro/outro y hero shots)

Prompts listos para generar en Higgsfield y sustituir las fotos fijas:

1. **Casco hero (image-to-video, `photos/casco.jpg`)** — "Slow cinematic orbit around a matte
   blue American football helmet with white facemask on a wooden desk, soft studio light,
   shallow depth of field, product commercial, keep helmet logo and colors exactly as in the
   photo, no new objects." Motion: *Orbit right, 5 s*.
2. **Cápsulas (image-to-video, `photos/capsulas_caja.jpg`)** — "Macro push-in over a cardboard
   box full of glossy blue 3D-printed spheres, natural window light, subtle parallax, keep every
   sphere as in the photo." Motion: *Dolly in, 4 s*.
3. **Intro/outro (text-to-video, placa blanca)** — "Minimal white studio, a single blue sphere
   rolls into frame and stops at center, soft shadow, clean commercial lighting, 3 s" y encima se
   compone el sello once LAB con el script (el logo nunca se genera con IA).
