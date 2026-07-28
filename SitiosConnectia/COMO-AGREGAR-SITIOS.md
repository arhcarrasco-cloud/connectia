# Sitios Connectia — archivo fuente y cómo agregar más

**Liga viva:** https://connectia.mx/SitiosConnectia/
**File de venta:** `Sitios-Connectia-File-de-Venta.pdf` (se regenera con un comando)

---

## Dónde vive cada cosa

| Archivo | Qué es |
|---|---|
| `data/oportunidades.json` | **La fuente de verdad.** Aquí viven los 11 sitios. Editando esto cambia el sitio web Y el PDF. |
| `data/videos.json` | Los 13 videos de la pestaña Videos (fuente: Google Drive o mp4 propio). |
| `assets/sitios/` | Las fotos con el mockup de campaña aplicado. |
| `index.html` | El sitio. No necesitas tocarlo para agregar sitios. |
| `build_pdf.py` | Genera el file de venta desde el JSON. |

---

## Agregar un sitio nuevo

**1.** Deja la foto en `assets/sitios/` (JPG, horizontal, mínimo 1600 px de ancho).

**2.** Abre `data/oportunidades.json` y copia este bloque al final de la lista (antes del `]`), poniéndole coma al bloque anterior:

```json
{
  "id": "OPP-NUEVO",
  "cat": "landmark",
  "titulo": "Nombre del sitio · Zona",
  "ubic": "Avenida y cruce · Ciudad",
  "tarifa": 500000,
  "medidas": "20.00 × 6.00 m",
  "imp": "alto",
  "impMes": 3000000,
  "aud": "NSE ABC+ · Zona",
  "obj": "Qué logra este sitio en una línea",
  "beneficio": "Por qué le conviene al cliente, en dos líneas.",
  "estatus": "disponible",
  "campanas": ["Buen Fin", "Hot Sale"],
  "foto": "assets/sitios/OPP-NUEVO.jpg",
  "fotoWm": "assets/sitios/OPP-NUEVO.jpg",
  "dir": "Dirección completa para el mapa",
  "lat": 19.4200,
  "lng": -99.1600
}
```

**3.** Corre en la Terminal:

```bash
cd ~/Documents/Claude/projects/"Plataforma Recorridos"/SitiosConnectia
python3 build_pdf.py
```

**4.** Publica (mismo repo que connectia.mx):

```bash
cd ~/ruta/al/clon/de/connectia
cp -R ~/Documents/Claude/projects/"Plataforma Recorridos"/SitiosConnectia .
git add SitiosConnectia && git commit -m "Sitios Connectia" && git push
```

---

## Diccionario de campos

| Campo | Valores | Nota |
|---|---|---|
| `id` | texto único | No repetir. Se usa para la selección del cliente. |
| `cat` | `landmark` · `mega` · `dooh` | Define el filtro donde aparece. |
| `tarifa` | número, sin comas ni `$` | `0` o quitarlo = muestra "Cotizar". |
| `imp` | `alto` · `medio` · `tactico` | Solo pinta el color del chip. |
| `impMes` | número | Impactos mensuales. `4100000` se muestra como `4.1 M`. |
| `estatus` | `disponible` · `bloqueada` · `no_disponible` | Semáforo verde / naranja / rojo. |
| `campanas` | lista de textos | Chips amarillos al pie de la ficha. |
| `fotoWm` | ruta | La que se ve. Si no hay mockup, repite el valor de `foto`. |
| `lat` / `lng` | decimales | Alimentan el botón "Ver en mapa" (Geonexa). |
| `video` | ID de Drive o ruta .mp4 | Opcional. Agrega el botón "Ver video". |
| `pdf` | URL | Opcional. Agrega el botón "Ver presentación". |
| `gallery` | lista de rutas | Opcional. Mosaico de fotos extra (lo usa el paquete DOOH). |

---

## Agregar un video

En `data/videos.json`:

```json
{
  "id": "v14",
  "titulo": "Nombre del caso",
  "cat": "Landmark",
  "drive": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
  "poster": "assets/sitios/OPP-NUEVO.jpg",
  "desc": "Una línea de contexto."
}
```

- `drive` = el ID del archivo en Google Drive (el pedazo entre `/d/` y `/view` de la liga).
  La carpeta debe estar compartida como **"Cualquier persona con el enlace"**.
- Si el video es propio, usa `"mp4": "https://connectia.mx/RecorridoAdri/assets/videos/archivo.mp4"` en lugar de `drive`.
- `poster` es la miniatura. Sin ella sale un degradado morado.

---

## De dónde salió el contenido actual

- **Fotos e info de sitios:** `_fuentes/PRESENTACION LANDMARK 2025.pdf`, `Landmark Hamburgo.pdf`,
  `Landmark Mega valla_FichaTecnica.pdf`, `Landmark Interlomas (1).pdf`, `Pantallas Landmark.pdf`.
- **Mockups de campaña:** generados sobre la foto real con el pipeline `_fuentes/walmartize*.py`
  y con la skill de sustitución de marca.
- **Videos:** carpeta de Drive "Videos Comerciales" + `assets/videos/*.mp4` propios.

> Ojo: los PDFs originales del proveedor traen tarifas de compra. Las tarifas del JSON son
> las de venta al cliente — no publicar las del PDF fuente.
