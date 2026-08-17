# Prompts para generar el congelador en ChatGPT

Estos prompts generan el congelador **VACÍO**, sin marca. El arte de Nestlé se
compone después por código con `tools/montaje.py`.

**Por qué vacío.** La regla dura de la skill de mockup: nunca dejar que una IA
dibuje, aproxime ni invente un logo, ni completo ni parcial. Un text-to-image
que "intente" poner Nestlé o Mega va a producir un logo falso y letras rotas.
Se genera el escenario limpio y encima se compone el arte real.

## Cómo correrlo

1. Abre ChatGPT y pega el **Prompt 01**. Descarga el resultado.
2. En la **misma conversación**, pega los prompts 02 a 06 uno por uno. Al estar
   en el mismo hilo, ChatGPT conserva el equipo y las vistas salen del mismo
   congelador, no de seis distintos.
3. Si alguna vista cambia el equipo, responde: *"Mismo congelador exacto de la
   primera imagen, solo cambia el ángulo de cámara."*
4. Guarda todo en `herdez-nestle/fotos/` con los nombres de la tabla.

| # | Archivo | Vista |
|---|---|---|
| 01 | `01-frente.jpg` | Frente perpendicular |
| 02 | `02-tres-cuartos-izq.jpg` | 3/4 izquierdo |
| 03 | `03-tres-cuartos-der.jpg` | 3/4 derecho |
| 04 | `04-lateral.jpg` | Lateral perpendicular |
| 05 | `05-copete.jpg` | Copete de frente |
| 06 | `06-ambientada.jpg` | En piso de venta |

**Pide siempre la resolución más alta que ofrezca.** El montaje necesita mínimo
2000 px por lado.

---

## Bloque de producto — va en TODOS los prompts

> A commercial glass-top chest freezer for ice cream retail. Body proportions
> 99 cm wide × 70 cm tall × 65 cm deep. Curved clear glass sliding lids on top
> with a white interior LED strip. A flat rectangular header board 88 cm × 44 cm
> stands upright on top of the freezer, centered and set slightly back. White
> plastic trim frames the top edge of the body. Four small black caster wheels.

---

## Prompt 01 · Frente

> Photorealistic commercial product photograph of a glass-top chest freezer,
> straight-on front view, camera perpendicular to the front panel at mid-body
> height, entire unit in frame including the header board on top.
>
> [BLOQUE DE PRODUCTO]
>
> The body and the header board are COMPLETELY BLANK matte neutral grey. Absolutely
> NO logos, NO text, NO letters, NO numbers, NO graphics, NO stickers, NO branding
> of any kind anywhere in the image — every surface is a clean unwrapped panel
> ready for vinyl application. The freezer is empty inside.
>
> Neutral light grey seamless studio background, soft even softbox lighting from
> both sides, subtle contact shadow under the wheels, realistic reflections and
> refraction on the curved glass lids. Sharp focus edge to edge, commercial
> product photography, high detail, 4K.

## Prompt 02 · Tres cuartos izquierdo

> Same freezer, same studio setup, same lighting. Rotate the camera to a
> three-quarter view from the LEFT at about 35 degrees, so the front panel and
> the full left side panel are both clearly visible. Slightly above eye level.
> Still completely blank — no logos, no text, no graphics on any surface.

## Prompt 03 · Tres cuartos derecho

> Same freezer, same studio setup, same lighting. Three-quarter view from the
> RIGHT at about 35 degrees, front panel and full right side panel both clearly
> visible. Still completely blank — no logos, no text, no graphics.

## Prompt 04 · Lateral

> Same freezer, same studio setup. Pure side view, camera perpendicular to the
> left side panel at mid-body height. The full side panel fills the frame
> squarely. Still completely blank — no logos, no text, no graphics.

## Prompt 05 · Copete

> Close-up product photograph of ONLY the rectangular header board that sits on
> top of the freezer. Proportions 88 cm wide × 44 cm tall, a 2:1 landscape panel.
> Straight-on front view, the panel fills the frame. Rigid flat board with a
> visible thin edge and a simple mounting bracket at the bottom.
>
> The panel face is COMPLETELY BLANK matte white — no logos, no text, no letters,
> no graphics whatsoever. Neutral grey studio background, soft even lighting,
> subtle drop shadow. Sharp focus, commercial product photography, 4K.

## Prompt 06 · Ambientada

> Same blank freezer placed on the tiled floor of a Mexican convenience store,
> three-quarter view from the left, natural retail lighting from a daylight
> storefront. Softly blurred shelves and store interior in the background,
> shallow depth of field, freezer in sharp focus.
>
> The freezer body and header board remain COMPLETELY BLANK — no logos, no text,
> no graphics, no branding anywhere in the scene, including on the background
> shelves and products, which should be generic and out of focus.

---

## Qué revisar antes de guardar

- [ ] Cero texto y cero logos en cualquier superficie — si aparece cualquier
      letra, pide la imagen de nuevo. Una letra inventada rompe la regla de logos.
- [ ] El copete se lee como panel rígido separado, no fundido con el cuerpo.
- [ ] Proporción del cuerpo cercana a 99 × 70 cm — ancho claramente mayor que alto.
- [ ] Las cuatro esquinas de cada cara visibles y sin obstrucción.
- [ ] Mínimo 2000 px por lado.

## Después

Con las imágenes en `fotos/`, el arte se compone encima:

```
python3 tools/montaje.py fotos/01-frente.jpg arte/frente.png salida.png \
    --quad "x1,y1 x2,y2 x3,y3 x4,y4" --luz 0.55
```
