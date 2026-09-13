# Reel de catálogo

Arma un reel vertical 1080×1920 con **todo un catálogo de producto**, sin
edición manual: recorre los productos de una marca, elige la mejor toma de cada
uno, la anima con un paneo-zoom lento, encadena con fundidos, pega la música y
cierra con la liga de compra.

Nada de la marca está cableado en el código: rutas, copy de cierre, colores,
tipografía y palabras prohibidas viven en `marcas/<marca>.json`.

> ⚠️ **El formato es una propuesta, no una copia del reel de referencia.**
> El reel de Instagram que originó el encargo no se pudo abrir desde la sesión
> en la nube (Instagram está bloqueado por el proxy de red). La estructura sale
> del guion en `GUION.md` y se ajusta con los parámetros de abajo.

## Correr

```bash
python3 armar-reel.py --marca once-once-lab \
  --audio <pista> \
  --liga <liga de compra>
```

El MP4 sale en la ruta que define el perfil, con su hoja de contacto de QC al
lado.

## Marcas

| Perfil | Estado |
|---|---|
| `marcas/mpmx.json` | Listo. Market Pulse MX, estructura `01-PRODUCTOS/`. |
| `marcas/once-once-lab.json` | Colores, tipografía, firma, palabras prohibidas, ventanas por red y nombres de producto, tomados del Manual de Identidad v2.0. **Faltan `raiz`, `liga` y el .ttf de Archivo** — el script se detiene y te dice cuál. |

Para una marca nueva se copia un perfil y se llena. Los campos están
documentados dentro de `once-once-lab.json`.

## Formas de catálogo que acepta

Se detectan solas, en este orden:

1. **Una carpeta por producto con `fotos/` dentro** — la estructura de MPMX,
   con preferencia por `video/` > derivada 9:16 > contexto con mano > contexto >
   Pinterest > marketplace.
2. **Una carpeta por producto** con las imágenes sueltas adentro.
3. **Una sola carpeta con un archivo por producto.**

El nombre en pantalla sale del primer encabezado de `ficha/FICHA-CANONICA.md`
si existe; si no, del nombre de la carpeta o del archivo, sin su código de SKU.

## Parámetros

| Parámetro | Para qué |
|---|---|
| `--marca` | Perfil de `marcas/`, o ruta a un `.json`. |
| `--raiz` | Anula la ruta del material que trae el perfil. |
| `--red reels\|tiktok` | Ventana de duración y sufijo del archivo (`IG-reel` / `TT-reel`). |
| `--seg N` | Segundos por producto. Si no lo pasas, se calcula para caer en la ventana de la red, con el piso y techo de ritmo del perfil. |
| `--transicion fundido\|corte` | Fundido de 0.3 s (por omisión) o corte seco. |
| `--encuadre auto\|cover\|blur` | `cover` recorta al centro a sangre; `blur` encaja la foto completa sobre fondo difuso; `auto` elige según la toma. |
| `--liga` / `--cta` | Anulan los del perfil. |
| `--intro` / `--outro` | Clips oficiales. Se conforman a 1080×1920/30 fps, **nunca se regeneran**. |
| `--solo` / `--excluir` | Productos por coma, para partir el catálogo en varios reels. |
| `--sin-rotulo` | Quita el nombre del producto en pantalla. |
| `--dry-run` | Imprime los comandos de ffmpeg sin escribir nada. |

## Lo que el script no te deja hacer

- **Decir lo que la marca no dice.** Si el nombre de un producto contiene una
  palabra de `palabras_prohibidas`, se detiene y te manda a corregirlo.
- **Publicar a ciegas.** Al final corre ffprobe contra la duración esperada y
  genera una hoja de contacto de 30 cuadros. Un archivo no es el que crees
  hasta que lo abres.
- **Salirte de la zona segura.** El rótulo va a 1480 px: ni los 250 px de
  arriba ni los 350 px de abajo se tocan.
- **Inventar un dato de marca.** Sin liga, sin música, sin tipografía o sin
  perfil llenado, avisa fuerte o se detiene. No rellena con defaults.

## Requisitos

`ffmpeg` y `ffprobe` en el PATH, Python 3.10+. Sin librerías externas.

## Probado

Con dos catálogos sintéticos. Uno con la estructura de MPMX y los casos feos
—foto 4:5 de contexto, 2:3 de Pinterest, 1:1 de marketplace, horizontal 16:9,
clip de video real, producto sin material, ficha con palabra prohibida— y otro
plano, de cinco archivos sueltos. Caminos verificados: fundido, corte seco,
intro/outro de otra resolución y fps, perfil sin llenar y perfil inexistente.
Todos salen a 1080×1920, 30 fps, con la duración exacta que anuncia el bloque
de ritmo.
