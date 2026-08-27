# Herdez × Nestlé Helados — Propuesta de vinil de congelador y copete

Presentación Connectia (13 láminas 16:9) para la producción e instalación de vinil
en congeladores Nestlé Helados en punto de venta.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | Deck listo para presentar. Logo Connectia embebido — abre sin dependencias. |
| `deck.src.html` | Fuente editable. El logo entra por el token `__LOGO_WHITE__`. |
| `Connectia_Herdez_Nestle_Helados.pdf` | Export 1600 × 900, una lámina por página. |

Para regenerar el HTML y el PDF después de editar la fuente, ver `build.py`.

## Medidas de referencia

Tomadas de la medición en sitio.

| Cara | Neto | Con sangrado (+1 cm) | m² neto |
|---|---|---|---|
| Frente | 99 × 70 cm | 101 × 72 cm | 0.693 |
| Lateral × 2 | 65 × 70 cm | 67 × 72 cm | 0.455 c/u |
| Copete | 88 × 44 cm | 90 × 46 cm | 0.387 |

Refrigerador (3 caras): **1.603 m²** · Total impreso con sangrado: **2.106 m²**

## Escalera de volumen

Base 20,000 piezas. Los ajustes se aplican **sobre el precio base**, no de forma acumulada.

### Cotización 01 · Vinil UVE 1440 dpi, instalado

| Volumen | Ajuste | Refrigerador 3 caras | Copete 1 cara | Paquete |
|---|---|---|---|---|
| 20,000 | base | $1,300.00 | $608.00 | $1,908.00 |
| 10,000 | +10 % | $1,430.00 | $668.80 | $2,098.80 |
| 5,000 | +30 % | $1,690.00 | $790.40 | $2,480.40 |

### Cotización 02 · Copete en coroplast, instalado

| Volumen | Ajuste | 1 cara | 2 caras |
|---|---|---|---|
| 20,000 | base | $900.00 | $1,100.00 |
| 10,000 | +10 % | $990.00 | $1,210.00 |
| 5,000 | +30 % | $1,170.00 | $1,430.00 |

Todos los precios en MXN, **más IVA**. Vigencia 30 días.

## Disclaimer

La cotización está calculada sobre la base de **instalación en un solo lugar de la CDMX**.
Cualquier dispersión de unidades requiere recotización de logística e instalación.

## Datos abiertos de esta versión

1. **Tercer escalón de volumen.** Se presenta en 5,000 piezas. El brief decía "por 20,000
   otro 30 %", y 20,000 es el volumen base — falta confirmar el volumen real del escalón.
2. **Fondo del refrigerador.** Se usó 65 cm, leído de la medición de referencia donde la
   cota quedó parcialmente oculta. Sujeto a validación en la primera unidad.
3. **Logos de cliente.** El co-branding va tipografiado. Faltan los archivos oficiales de
   Herdez y Nestlé Helados para sustituirlos.
4. **Arte de las caras.** La composición del deck es ilustrativa: reproduce el lenguaje
   gráfico del equipo de referencia y marca las zonas de marca. El arte final lo entrega
   el cliente.

## Tipografía

Coplette y Cooper Hewitt no están disponibles en este entorno de build. El deck usa
**Inter Tight**, la misma familia que corre en connectia.mx, declarada como fallback
técnico según el brandbook.
