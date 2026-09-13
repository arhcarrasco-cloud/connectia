# Guion — reel de catálogo de hogar

**Pieza:** un reel vertical con todo el catálogo de productos de hogar.
**Formato:** 1080×1920, 30 fps, H.264 + AAC.
**Marca:** Once Once Lab.
**Dónde:** Instagram Reels (60–90 s, donde hay engagement) y un corte de TikTok
de 24–38 s con los mismos productos y otro copy.

> **Dos huecos que solo tú puedes cerrar.**
> 1. El reel de referencia de Instagram no se pudo ver desde la sesión en la
>    nube. La estructura de abajo es una propuesta.
> 2. **De Once Once Lab no hay nada** en el repo, en las skills ni en la
>    memoria: ni brandbook, ni logo, ni tipografía, ni rutas del material. Lo
>    que sigue es estructura de reel, no dirección de arte de la marca. Los
>    campos de marca están vacíos en `marcas/once-once-lab.json` a propósito.

---

## Estructura

| Tramo | Duración | Qué pasa |
|---|---|---|
| **Gancho** | 0 – 2.5 s | El producto más fuerte del catálogo, ya **en uso**. Nada de logo ni claim antes del producto: Instagram te prueba con desconocidos y los primeros dos segundos deciden. |
| **Recorrido** | 2.5 s → −2.5 s | Un producto por plano, paneo-zoom lento de 6%, fundido de 0.3 s entre planos. El nombre aparece abajo, pequeño, dentro de la zona segura. |
| **Cierre** | últimos 2.5 s | Tarjeta con la línea de la marca y la liga de compra. |

El orden del recorrido es alfabético. Para ordenarlo por categoría o por lo que
más se mueve, se pasa `--solo` con la lista en el orden que quieras.

## Ritmo

Con ~3 s por producto, un reel de 90 s aguanta unos **28 productos**. Si el
catálogo pasa de ahí, el script avisa y hay que partirlo: la salida no es
apretar los planos a 1 s. El ritmo calmado deja ver el producto; el corte
rápido solo deja ver que hay muchos.

## Tratamiento visual

- Producto ocupando entre 40% y 60% del cuadro, el entorno respira.
- Producto **en uso** desde el primer frame, no en bodegón.
- Sin texto gritón: el nombre va en 46 px, blanco al 94%, con sombra suave.
  Nada de cintillos ni precios en pantalla.
- Nada de fondo blanco de marketplace en el cuerpo del reel: esa foto es para
  la ficha de producto. Si un producto solo tiene esa, el script lo marca y hay
  que generarle una toma de contexto antes de publicar.

**Falta definir, y es de Once Once Lab:** paleta, tipografía oficial, si el logo
entra y dónde, si hay intro/outro de marca, y el tono de la luz. Sin eso el
reel sale correcto de forma pero neutro de marca.

## Zona segura 9:16

Nada de texto en los **250 px de arriba** ni en los **350 px de abajo**. El
rótulo va a 1480 px y la tarjeta de cierre al centro. Ahí es donde IG y TikTok
montan su propia interfaz.

## Copy

Reglas que aplican a cualquier marca:

- **3 a 5 hashtags máximo.** Sin hashtags suele rendir más — vale probar.
- **Copy nativo y distinto por red.** No se recicla el de IG en TikTok.
- **Un gancho no puede afirmar un hecho falso.** Si el copy dice "liga en bio",
  la bio tiene que tener liga. Si describe un color, tiene que ser el color que
  se ve en el cuadro.
- **No se inventan testimonios.** Prueba social solo con clientes reales.

Plantilla para llenar con lo que sí es cierto el día que se publique:

```
IG Reels
  Gancho   : <el problema que resuelve el primer producto, en una línea>
  Cuerpo   : <2 líneas: materia, acabado, cómo se ve en tu espacio>
  Cierre   : <línea de marca>. <liga>
  Hashtags : <3 a 5, o ninguno>

TikTok
  Gancho   : <más directo, la pregunta que se hace quien lo necesita>
  Cierre   : <liga> — bio máximo 80 caracteres
```

**Si Once Once Lab tiene algo que nunca dice** —como MPMX, que jamás menciona
impresión 3D— va en `palabras_prohibidas` del perfil y el script se detiene
solo cuando aparezca.

## Antes de publicar

1. **Abrir el MP4 completo**, con audio. No el nombre del archivo, no el
   timestamp: el video.
2. **Abrir la hoja de contacto** que deja el script en `qc/`. Tienen que
   aparecer todos los productos y ningún cuadro en blanco.
3. **Verificar que no haya duplicado**: si ya hay una pieza de estos productos
   en esa red, no se publica.
4. **Verificar la liga** abriéndola, y la bio si el copy la menciona.
5. Si el reel lleva voz en off, **escucharla completa** y cotejar cada dato que
   afirme contra lo publicado: medidas, materiales, colores.

## Pendiente

- Llenar `marcas/once-once-lab.json`: ruta del material, línea de cierre, liga,
  colores y tipografía.
- La pista de música.
- Los clips de intro y outro, si Once Once Lab los tiene. Si existen, se pasan
  con `--intro` / `--outro` y el script solo los conforma, nunca los regenera.
