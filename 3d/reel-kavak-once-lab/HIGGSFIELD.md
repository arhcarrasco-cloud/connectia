# Hoja de trabajo Higgsfield · Reel KAVAK once once LAB

Higgsfield no es operable desde la sesión remota (sin conector MCP, sin API key y con
higgsfield.ai bloqueado por la política de red). Se genera en la Mac de Roger con la
extensión de Claude para Chrome sobre `https://higgsfield.ai` (flujo `editor-de-video`
§3: automatización de navegador, verificar cada generación y registrar prompt + ID).

Todos los clips: **9:16, 1080×1920 o superior, 5 s, sin texto, sin logos nuevos, sin
objetos nuevos**. Guardar en una carpeta (p. ej. `clips_higgsfield/`) con el nombre de
archivo exacto de la tabla y renderizar:

```bash
python3 build_reel.py ONCELAB_REEL_KAVAK_V03.mp4 --clips clips_higgsfield \
  --casco "…/P1S UNO/video_2026-08-16_05-23-14.avi" --capsulas "…/P1S DOS/video_2026-08-18_12-26-10.avi"
```

Si falta un clip, el script cae al Ken Burns sobre la foto para esa escena.

## Tomas (image-to-video, imagen de `photos/`)

| Archivo | Imagen fuente | Movimiento (preset) | Prompt |
|---|---|---|---|
| `hook.mp4` | `casco.jpg` | Dolly in lento + ligero orbit derecha | Cinematic slow dolly-in on a matte blue American football helmet with a white facemask resting on a wooden desk, soft warm interior light, shallow depth of field, premium product commercial. Keep the KAVAK lettering, colors, helmet shape and every object exactly as in the photo. Do not add any new object, logo, text or person. The result must look like the same photograph coming to life through natural camera movement only. |
| `blanco_a.mp4` | `casco_blanco_a.jpg` | Orbit izquierda suave | Slow cinematic orbit to the left around a glossy white American football helmet with a navy blue facemask on a beige tile floor, soft daylight, product commercial look. Keep the KAVAK lettering, the blue facemask, the white clips and screws exactly as in the photo. Do not add any new object, logo, text or person. Same photograph coming to life through camera movement only. |
| `blanco_b.mp4` | `casco_blanco_b.jpg` | Push-in hacia el logo | Slow push-in toward the KAVAK lettering on a glossy white football helmet with a navy facemask, sofa out of focus in the background, natural daylight, shallow depth of field. Keep every element, color and reflection as in the photo. No new objects, logos, text or people. Camera movement only. |
| `caps.mp4` | `capsulas_caja.jpg` | Dolly in + tilt down leve | Macro dolly-in over a cardboard box filled with glossy blue 3D-printed spheres, window backlight, subtle parallax between spheres, premium product commercial. Keep every sphere, the box and the light exactly as in the photo. Do not add any new object, text or logo. Same photograph coming to life through camera movement only. |
| `merch.mp4` | `playera.jpg` | Pan derecha lento | Slow pan to the right across white t-shirts laid flat with a blue football player print, soft top light, fabric texture visible, clean commercial look. Keep the print, colors and tags exactly as in the photo. No new objects, logos, text or people. Camera movement only. |
| `claim_top.mp4` | `casco_blanco_detalle.jpg` | Orbit derecha muy lento (se recorta a la mitad superior) | Very slow cinematic orbit to the right around the top of a white football helmet with KAVAK lettering and a navy facemask, tile floor, soft daylight, shallow depth of field. Keep lettering, colors and every element as in the photo. No new objects, logos, text or people. Camera movement only. |

## Reglas de QC antes de aceptar cada clip (obligatorias)

1. Extraer frames: `ffmpeg -y -i clip.mp4 -vf fps=2 f_%02d.jpg` y revisar TODOS.
2. Rechazar si aparece: letras KAVAK deformadas o reescritas, un segundo casco, esferas
   que se funden, manos, personas, texto nuevo, cambio de color del casco o de la máscara.
3. Regenerar con el mismo prompt reforzando la fidelidad; nunca "arreglar en post".

## Intro y outro

Se quedan con el sello master de once LAB renderizado por el script (el logo nunca se
genera con IA). Si se quiere fondo en movimiento para la placa, generar text-to-video
"Minimal white studio, a single glossy blue sphere rolls in from the left and stops at
center, soft shadow, clean commercial lighting, 3 s, 9:16" y componer el sello encima.
