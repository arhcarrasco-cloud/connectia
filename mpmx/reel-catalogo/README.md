# Reel de catálogo — Market Pulse MX

Arma un reel vertical 1080×1920 con **todo el catálogo de productos de hogar**
a partir de `~/Documents/Market-Pulse-MX/01-PRODUCTOS/`, sin tocar a mano ni un
clip. Recorre los SKUs, elige la mejor toma de cada uno, la anima con un
paneo-zoom lento, encadena todo con fundidos, pega la música y cierra con la
liga de compra.

> ⚠️ **El formato es una propuesta, no una copia del reel de referencia.**
> El reel de Instagram que originó este encargo no se pudo abrir desde la
> sesión en la nube (Instagram está bloqueado por el proxy de red), así que la
> estructura sale de las reglas de MPMX: ritmo calmado, producto en uso, luz
> cálida, sin texto gritón. Si el reel de referencia hace otra cosa —cortes al
> beat, voz en off, manos entrando a cuadro— se ajusta con los parámetros de
> abajo o se cambia el guion.

## Correr

```bash
cd ~/Documents/Claude/projects/connectia-repo/mpmx/reel-catalogo

python3 armar-reel.py \
  --red reels \
  --audio ~/Documents/Market-Pulse-MX/00-MARCA/musica/pista.m4a \
  --liga marketpulse.mx
```

Sale en `02-CONTENIDO/<hoy>/<red>/CATALOGO_<destino>_todos_v1.mp4`, con la hoja
de contacto de QC junto a él.

### Parámetros que importan

| Parámetro | Para qué |
|---|---|
| `--red reels\|tiktok` | Fija la ventana de duración y el sufijo del archivo (`IG-reel` / `TT-reel`). |
| `--seg N` | Segundos por producto. Si no lo pasas, se calcula para caer dentro de la ventana de la red, con piso de 1.4 s y techo de 3.5 s. |
| `--transicion fundido\|corte` | Fundido de 0.3 s (por omisión) o corte seco. |
| `--encuadre auto\|cover\|blur` | `cover` recorta al centro a sangre; `blur` encaja la foto completa sobre un fondo difuso. `auto` usa cover en tomas verticales y blur en horizontales. |
| `--liga` | Liga de compra de la tarjeta de cierre. **Sin ella el reel sale sin liga y el script avisa.** |
| `--intro` / `--outro` | Clips oficiales de marca. Se conforman a 1080×1920/30 fps, nunca se regeneran. |
| `--solo` / `--excluir` | SKUs por coma, para partir el catálogo en varios reels. |
| `--sin-rotulo` | Quita el nombre del producto en pantalla. |
| `--dry-run` | Imprime los comandos de ffmpeg sin escribir nada. |

## Qué toma de cada producto

En este orden, y lo dice en pantalla al arrancar:

1. `video/*.mp4` — clip real, es lo mejor
2. `fotos/**/*_IG-reel_*` o `*_TT-reel_*` — derivada 9:16 que ya existe
3. `fotos/contexto/` con `mano` o `uso` en el nombre — producto en uso desde el primer frame
4. `fotos/contexto/` cualquiera
5. `fotos/pinterest/` — 2:3, recorta bien a 9:16
6. `fotos/marketplace/` — fondo blanco, **último recurso y lo marca**: esa foto es para el marketplace, no para un reel

El nombre en pantalla sale del primer encabezado de `ficha/FICHA-CANONICA.md`;
si no hay ficha, del SKU sin su código.

## Lo que el script no te deja hacer

- **Decir que hacemos 3D.** Si el nombre de un producto trae `3d`, `impres`,
  `filamento`, `PLA`, `PETG`, `capa por capa` o `bajo demanda`, se detiene y te
  manda a corregir la ficha.
- **Publicar a ciegas.** Al final corre ffprobe y genera una hoja de contacto de
  30 cuadros. Un archivo no es el que crees hasta que lo abres.
- **Salirte de la zona segura.** El rótulo va a 1480 px: ni los 250 px de
  arriba ni los 350 px de abajo se tocan.
- **Inventar.** Sin liga, sin música o sin Cooper Hewitt no se detiene, pero lo
  dice fuerte: son decisiones tuyas, no defaults silenciosos.

## Requisitos

`ffmpeg` y `ffprobe` en el PATH, y Python 3.10+. Nada más — no usa librerías
externas.

## Probado

Con un catálogo sintético de 7 productos que cubre los casos feos: foto 4:5 de
contexto, 2:3 de Pinterest, 1:1 de marketplace, horizontal 16:9, clip de video
real, producto sin material, y ficha con palabra prohibida. Los tres caminos
(fundido, corte, con intro/outro de otra resolución y fps) salen a 1080×1920,
30 fps, con la duración exacta que anuncia el bloque de ritmo.
