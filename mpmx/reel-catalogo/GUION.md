# Guion — reel de catálogo de hogar

**Pieza:** un reel vertical con todo el catálogo actual de Market Pulse MX.
**Formato:** 1080×1920, 30 fps, H.264 + AAC.
**Dónde:** Instagram Reels (60–90 s, que es donde hay engagement) y un corte de
TikTok de 24–38 s con los mismos productos y otro copy.

> El reel de referencia de Instagram no se pudo ver desde la sesión en la nube.
> Este guion sale de las reglas editoriales de MPMX. Si la referencia va por
> otro lado, lo que cambia es el bloque de ritmo, no la estructura.

---

## Estructura

| Tramo | Duración | Qué pasa |
|---|---|---|
| **Gancho** | 0 – 2.5 s | El producto más fuerte del catálogo, ya **en uso**, mano real en cuadro. Nada de logo ni claim antes del producto: Instagram te prueba con desconocidos y los primeros dos segundos deciden. |
| **Recorrido** | 2.5 s → −2.5 s | Un producto por plano, paneo-zoom lento de 6%, fundido de 0.3 s entre planos. El nombre aparece abajo, pequeño, dentro de la zona segura. |
| **Cierre** | últimos 2.5 s | Fondo `#1A1A18`, la línea *hecho por pedido en México* y la liga de compra. |

El orden del recorrido es el alfabético de los SKUs. Para ordenarlo por
categoría o por lo que más se mueve, se pasa `--solo` con la lista en el orden
que quieras.

## Ritmo

Con ~3 s por producto, un reel de 90 s aguanta unos **28 productos**. Si el
catálogo pasa de ahí, el script avisa y hay que partirlo: la salida no es
apretar los planos a 1 s, porque el ritmo calmado es la regla, no una
preferencia.

Reparto sugerido si hay que partir:

- **Reel 1 — Cocina y baño**, que son las categorías que empujan Pinterest e IG.
- **Reel 2 — Escritorio, gamers y recámara**, que es material de TikTok.

## Tratamiento visual

- Luz cálida natural, paleta Japandi: maderas claras, lino, piedra, verde
  planta, ámbar.
- Producto ocupando entre 40% y 60% del cuadro, el entorno respira.
- **Nada de taller en cuadro**: ni impresoras, ni carretes, ni herramientas.
- **Nada de fondo blanco de marketplace** en el cuerpo del reel. Esa foto es
  para Amazon y Mercado Libre. Si un SKU solo tiene esa, el script lo marca y
  hay que generarle una toma de contexto antes de publicar.
- Sin texto gritón: el nombre del producto va en 46 px, blanco al 94%, con
  sombra suave. Nada de cintillos ni precios en pantalla.

## Zona segura 9:16

Nada de texto en los **250 px de arriba** ni en los **350 px de abajo**. El
rótulo va a 1480 px y la tarjeta de cierre al centro. Ahí es donde IG y TikTok
montan su propia interfaz.

## Copy

Reglas que no se negocian:

- **Nunca decimos que hacemos 3D.** Ni impresión, ni filamento, ni PLA, ni
  PETG, ni capas, ni "bajo demanda". Se dice **hecho por pedido**.
- **3 a 5 hashtags máximo.** Sin hashtags rinde 23% más — probar sin ellos.
- **Copy nativo y distinto por red.** No se recicla el de IG en TikTok.
- **Un gancho no puede afirmar un hecho falso.** Si el copy dice "liga en bio",
  la bio tiene que tener liga. Si describe un color, tiene que ser el color que
  se ve.
- **No se inventan testimonios.** Prueba social solo con clientes reales.

Plantilla para llenar con lo que sí es cierto el día que se publique:

```
IG Reels
  Gancho   : <el problema que resuelve el primer producto, en una línea>
  Cuerpo   : <2 líneas: orden, acabado, cómo se ve en tu espacio>
  Cierre   : Hecho por pedido en México. <liga>
  Hashtags : <3 a 5, o ninguno>

TikTok
  Gancho   : <más directo, la pregunta que se hace quien lo necesita>
  Cierre   : <liga> — bio máximo 80 caracteres
```

La liga de compra va en **toda** pieza: bio, primer comentario fijado, y dentro
del video (por eso la tarjeta de cierre).

## Antes de publicar

1. **Abrir el MP4 completo.** No el nombre del archivo, no el timestamp: el
   video, con audio.
2. **Abrir la hoja de contacto** que deja el script en `qc/`. Tienen que
   aparecer todos los productos y ningún cuadro en blanco.
3. **Verificar que no haya duplicado** — Regla Cero. Consultar `igRecentMedia` /
   `myListings` / `C.posts`: si ya hay una pieza de estos productos en esa red,
   no se publica, se reporta y se pregunta.
4. **Verificar la liga** abriéndola, y la bio si el copy la menciona.
5. Si el reel lleva voz en off, **escucharla completa**: el 15-ago-2026 un
   `REEL-01` pasó el QC visual con una locución que decía "impreso en 3D capa
   por capa" y hablaba de 18 cm cuando lo publicado decía 20 cm.

## Pendiente

- La música. El script la normaliza a −14 LUFS y le pone fundido de salida,
  pero la pista la eliges tú: no hay una de marca definida en `00-MARCA/`.
- Los clips de intro y outro oficiales, si es que MPMX ya los tiene. Si
  existen, se pasan con `--intro` / `--outro` y el script solo los conforma,
  nunca los regenera.
