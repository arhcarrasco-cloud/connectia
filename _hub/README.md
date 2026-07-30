# App Hub — cómo se mantiene

Todo el hub sale de un solo archivo: **`_hub/catalogo.json`**. Ahí viven las apps,
sus URLs, sus carpetas y el glifo de su ícono. Nada más hay que editar a mano.

## Publicar un cambio

```bash
cd ~/Documents/Claude/projects/connectia-repo
bash _hub/publicar.sh
```

O doble clic en **Aplicaciones › Connectia › Publicar Hub**.

Eso hace, en orden: regenera los íconos, reconstruye el hub, reconstruye las apps
del Mac, hace commit y push, espera a GitHub Pages y verifica que las 17 URLs
respondan 200. Si algo falla, te lo dice con el código y la URL.

## Los tres tipos de cambio

**Editar un sitio.** Abre su carpeta en el repo (`rh-analisis/index.html`,
`ebook-es/index.html`, …), edítala y publica. Esa carpeta *es* el sitio: no hay
copia intermedia ni original en otro lado.

**Agregar, quitar o mover una app.** Toca `_hub/catalogo.json`. Para agregar:
mete la carpeta con su `index.html` en el repo, añade una entrada al arreglo
`apps` y publica. El hub, el ícono y la app del Mac salen solos.

**Cambiar el diseño del hub.** `_hub/hub.py` genera el HTML completo;
`_hub/iconos.py` dibuja los íconos.

## Campos de una app

| campo | qué es |
|---|---|
| `id` | nombre del archivo del ícono, sin espacios |
| `nombre` | lo que se lee bajo el ícono |
| `carpeta` | debe existir en el arreglo `carpetas` |
| `ruta` | carpeta dentro del repo, o `null` si el sitio vive fuera |
| `url` | a dónde abre |
| `glifo` | símbolo del ícono (ver lista abajo) |
| `hi` / `lo` | degradado del ícono, de arriba a abajo |
| `app_mac` | `true` crea su app en el Mac |

Glifos disponibles: `logo`, `billboard`, `pin`, `van`, `capas`, `ruta`,
`tablero`, `radar`, `libro`, `globo`, `docs`, `escudo`, `navegador`, `diana`,
y `ebook:XX` donde XX es el idioma. Para uno nuevo, agrégalo al diccionario
`GLYPHS` de `iconos.py` como SVG en un lienzo de 512×512, trazo blanco.

## Reglas que el código respeta

- El logo de Connectia **nunca se dibuja**: se incrusta el PNG oficial de
  `~/Connectia-Assets/connectia/logo/`. Si el archivo falta, el script se detiene
  en vez de inventar una variante.
- Morado canónico `#872B90`. Tipografías Coplette y Cooper Hewitt, con el stack
  de sistema como fallback declarado.
- Cada publicación cambia el sello de versión, así que el navegador y las apps
  del Dock cargan lo nuevo sin que tengas que vaciar caché.

## Lo que este pipeline no toca

`flotillas.connectia.mx` y `erp.connectia.mx` son aplicaciones con su propio
deploy. El hub solo las enlaza. El Vision Board vive en el repo
`arhcarrasco-cloud/vision-board`, aparte y con `noindex`.

## En el iPhone

Safari → `connectia.mx/hub` → Compartir → Añadir a pantalla de inicio.
Queda con ícono propio y abre a pantalla completa, sin barra de Safari.
Cada vez que publicas, el iPhone ve la versión nueva al abrirlo.
