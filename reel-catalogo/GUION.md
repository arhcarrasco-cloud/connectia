# Guion — reel de catálogo de hogar · once LAB

**Marca:** once LAB — taller de impresión 3D y sublimación.
*11:11: pides un deseo; nosotros lo hacemos realidad.*
**Pieza:** un reel vertical con las piezas de hogar del catálogo.
**Formato:** 1080×1920, 30 fps, H.264 + AAC.
**Dónde:** Instagram Reels (@once.oncelab) y TikTok, **15–30 s**, con copy
distinto en cada una.

> El reel de Instagram de referencia no se pudo abrir desde la sesión en la
> nube. La estructura de abajo sale del Manual de Identidad once LAB v2.0 y de
> sus reglas de publicación, no de la referencia.

---

## El catálogo de hogar

Lo que hay hoy en Drive → `Once Once / Productos once LAB /`:

| Producto | Imagen | Clip |
|---|---|---|
| Lámpara 1, 2 y 3 | hero + v2 + v3 | sí |
| Jarrón rosa, verde, terracota | sí | — |
| Maceta pastel | sí | — |
| Florero crema | sí | — |
| Pendant verde | sí | — |
| Portarretrato | hero + v2 + v3 | sí |
| Portahuevos | hero + v2 + v3 | sí |
| Funda AirTag | hero + v2 + v3 | sí |

**Seis productos ya tienen clip propio en `Reels/`** y esos son el mejor
material: son movimiento real, no una foto animada. Los jarrones, la maceta, el
florero y el pendant solo tienen PNG, así que entran con paneo-zoom.

En `Once Once/` también hay **Timelapses**, que es justo lo que TikTok premia
según el manual: *time-lapse de impresión, hook 3 s*.

## Estructura

| Tramo | Duración | Qué pasa |
|---|---|---|
| **Hook** | 0 – 3 s | La pieza más fuerte, ya terminada, sobre su color sólido. El manual pide hook de 3 s: el deseo cumplido primero, el proceso después. |
| **Recorrido** | 3 s → −2.5 s | Una pieza por plano, un color de la paleta por plano, fundido de 0.3 s. Nombre abajo, dentro de la zona segura. |
| **Cierre** | últimos 2.5 s | Negro Tinta, **«Lo hacemos realidad.»** en blanco y la liga en Rosa Once. |

Con 12 piezas a ~2.3 s el reel cae en 26 s, dentro de la ventana de TikTok y
cómodo para Reels.

## Tratamiento visual

Del manual, capítulo *El feed es alegría*:

- **Un objeto por plano**, protagonista y centrado, con aire.
- **Fondo = un color sólido de la paleta**, rotando plano a plano. El grid —y el
  reel— se lee como una fiesta de color, cohesivo por composición, no por tono.
- **Luz dramática, sombra larga, acabado matte.** Cero desorden.
- **Watermark «once once LAB» abajo.** Las PNG del catálogo ya lo traen
  (sufijo `_wm`); el armador no lo añade para no duplicarlo.

### El rosa se administra

`#F0246B` es la firma, no el fondo: **nunca más del 10% de la superficie**. Por
eso la tarjeta de cierre va en Negro Tinta `#151217` con la liga en rosa, y no
al revés. Sobre Rosa Once, Frambuesa o Vino se escribe en blanco; sobre Rosa
Capa o Pastel, en Vino Once o Negro Tinta. Nunca rosa sobre rosa contiguo.

### Tipografía

**Archivo ExtraBold 800** para el rótulo (ancho 112%, tracking −2%),
**Instrument Sans** para cuerpo, **IBM Plex Mono** para dato técnico. Las tres
son libres en Google Fonts. Baja el .ttf de Archivo y ponlo en `tipografia`
dentro del perfil: sin eso, ffmpeg usa su fuente por omisión y el reel pierde
la voz de la marca.

## Zona segura 9:16

Nada de texto en los **250 px de arriba** ni en los **350 px de abajo**. El
rótulo va a 1480 px y la tarjeta de cierre al centro.

## Copy

Reglas del manual, y no son negociables:

- **Copy veraz: impreso en 3D. Nunca «hecho a mano».** Es al revés que otras
  marcas del taller — aquí el 3D se dice, lo que no se dice es artesanía. Está
  en `palabras_prohibidas` y el armador se detiene si aparece.
- **Firma: «Lo hacemos realidad.»**
- **3 a 5 hashtags.** Uno por categoría al día.
- Si el copy describe un color, tiene que ser el color que se ve en el cuadro.

```
IG Reels @once.oncelab
  Hook     : <el deseo, en una línea>
  Cuerpo   : <la pieza, su color, dónde va en tu casa>
  Firma    : Lo hacemos realidad. <liga>
  Hashtags : <3 a 5>

TikTok
  Hook 3 s : <directo, con el objeto en pantalla>
  Pantalla : texto en pantalla + música trend
  Cierre   : <liga>
```

Para Pinterest, el manual pide título SEO con keywords —maceta, lámpara,
florero, decoración 3D— y tableros por categoría.

## Antes de publicar

1. **Abrir el MP4 completo**, con audio.
2. **Abrir la hoja de contacto** en `qc/`: las 12 piezas, ningún cuadro en
   blanco, ningún nombre cortado.
3. **Verificar el rosa**: que no se haya vuelto fondo en ningún plano.
4. **Verificar la liga** abriéndola.
5. Si lleva voz, escucharla completa y cotejar cada dato: medidas, material,
   color.

## Pendiente

- `raiz` en `marcas/once-once-lab.json`: la ruta local de `Productos once LAB`
  ya sincronizada.
- La liga de compra.
- El .ttf de Archivo ExtraBold.
- La pista de música trend.
