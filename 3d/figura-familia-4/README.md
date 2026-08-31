# Figura familiar 4 integrantes — gris + pintada a mano

Costeo de la pieza del anuncio "Figuras 3D personalizadas · Mándanos tu foto":
grupo de 4 integrantes (2 adultos, 2 niños) sobre base circular con relieve.

Se imprime en **PLA Matte gris** (el gris es imprimación de facto: la pintura
agarra sin velar el detalle) y **se pinta a mano aparte**, figura por figura,
antes de ensamblar sobre la base.

## Uso

```bash
python3 costeo.py                      # escenario base, PRELIMINAR
python3 costeo.py --gramos 210 --horas 27 --medido    # con slice real
python3 costeo.py --sin-pintura        # variante gris crudo
python3 costeo.py --ocupacion 0.85     # piso de precio con taller saturado
```

## Resultado (PRELIMINAR · 210 g · 27 h-máquina)

| Variante | Costo con merma | Precio sin IVA | Precio con IVA |
|---|---:|---:|---:|
| Gris + pintada a mano (margen 60% mixto) | $1,219.58 | $3,264.41 | $3,786.72 |
| Solo gris, sin pintar (margen 55% 3D) | $752.18 | $1,886.97 | $2,188.89 |
| Integrante adulto adicional | $237.89 | $594.74 | $689.89 |

Precio de lista sugerido: **$3,790 con IVA, envío CDMX incluido**
(gris sin pintar **$2,190**, integrante extra **+$690**).

## Supuestos que hay que validar antes de cerrar precio

1. **CHECK A no corrido** — no hay conexión a las 6 Bambu desde esta sesión.
   El costeo va `SIN VERIFICACIÓN DE CAPACIDAD` y usa piso de precio × 0.
   Con el taller arriba de 70% el piso sube a $2,029 y sigue por debajo del
   precio por margen, así que el precio no cambia; la **fecha de entrega sí**.
2. **Gramaje y horas son estimado geométrico, no slicer.** Bambu Studio manda.
   El rango razonable es 180–240 g y 22–32 h según altura final y capa.
3. **Precios de insumos de lista (ML, 18-ago-2026).** Falta CHECK B contra el
   historial de compras real.
4. **Consumibles de pintura ($70) son estimado de taller**, no compra validada.
5. **Envío CDMX cobrado por volumétrico:** 30×20×20 cm ÷ 5,000 = 2.4 kg
   cobrables, aunque la pieza pese ~400 g. El volumen manda, no el peso.

## Dónde está el dinero

La **mano de obra es el 61% del costo directo** ($619 de $1,016) y la pintura
a mano sola son $284 (28%). El filamento es $90: ruido. Bajar el precio pasa
por bajar minutos-hombre, no por comprar filamento más barato.

Palancas, en orden de retorno:

1. **Aerógrafo + plantillas** para piel, cabello y ropa; pincel solo en cara y
   detalle. Puede tumbar la pintura de 240 a 120–140 min.
2. **Lote de 4–6 pedidos en paralelo**: la gestión ($59), el traslado a
   paquetería y el arranque de corridas se prorratean.
3. **Capa 0.12 mm solo en cabeza y manos**, 0.20 mm de la cintura para abajo:
   recorta horas-máquina sin tocar lo que el cliente mira.
4. **Base impresa aparte y en lote** — es la pieza más pesada (~60 g) y no
   necesita detalle fino.

## Límite técnico honesto

FDM a 0.12 mm no da la cara del render del anuncio. Para el nivel de la imagen
de referencia se necesita **resina (SLA/DLP)**, y en el parque actual de
CreaLab **no hay impresora de resina**. Dos caminos: vender la pieza con el
acabado FDM real (mostrar foto de producto real, no render), o meter una
resina al inventario y recostear.
