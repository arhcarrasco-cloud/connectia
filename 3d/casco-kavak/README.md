# Casco KAVAK — medidas para el logo

Modelo que se está imprimiendo en la P1S: **"Full size football helmet."** de **Kish82** (MakerWorld, licencia BY-NC),
perfil *"P1s size print, unchopped 0.2mm layer, 2 walls, 15% infill"*. El archivo es `Casco.3mf` en Drive
(Mi unidad, 29-ago-2026); no se versiona aquí por ser modelo de terceros.

Medidas tomadas de la malla del 3MF con las transformaciones reales del proyecto (el modelo va escalado
a 95 % en ancho para caber en la P1S), en la pose de apoyo de la foto (máscara + borde trasero sobre la mesa).

## Casco impreso

| Medida | cm |
|---|---|
| Ancho (oreja a oreja) | 24.0 |
| Largo del casco sin máscara | 25.9 |
| Largo con máscara | ≈ 34.7 |
| Alto | 25.4 |
| Oído (agujero lateral) | Ø 4.0 |
| Suelo → borde inferior del oído | 6.5 |

## Logo KAVAK (por lado, espejo en el izquierdo)

| Medida | cm |
|---|---|
| Ancho del logotipo | **12.0** |
| Alto del logotipo | **3.1** (proporción 3.87:1 del wordmark) |
| Borde inferior del logo → borde superior del oído | 0.5 |
| Borde trasero del logo → centro del oído | 9.4 |
| Borde delantero del logo → centro del oído | 2.6 (adelante) |
| Arco real sobre la superficie a lo largo del logo | 12.5 |

Zona plana útil del lateral (inclinación ≤ 30°): de 8 cm atrás del oído a 3 cm adelante, y de 5 a 19 cm
sobre el suelo. Con 12 cm de ancho el logo queda con inclinación 35° en la K trasera, 3° al centro y 18° al frente.
Máximo recomendable si se quiere más grande: 14 × 3.6 cm (la última K envuelve la curva trasera).

## Reproducir

```bash
python3 medir_casco.py Casco.3mf "Logo Kavak .png" casco_kavak_logo_medidas.png
```
