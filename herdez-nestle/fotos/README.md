# Fotos base para el montaje hiperrealista

Aquí van las fotografías del congelador real. El montaje se hace **sobre estas
fotos**, nunca regenerando la escena — la foto base es intocable y solo se
sustituye la superficie del vinil.

## Tomas necesarias

| # | Archivo | Toma |
|---|---|---|
| 01 | `01-frente.jpg` | Frente, cámara perpendicular a la cara, a media altura. Unidad completa con copete. |
| 02 | `02-tres-cuartos-izq.jpg` | 3/4 desde la izquierda, 30–45°. Se ven frente y lateral izquierdo. |
| 03 | `03-tres-cuartos-der.jpg` | 3/4 desde la derecha. Se ven frente y lateral derecho. |
| 04 | `04-lateral.jpg` | Lateral, cámara perpendicular a la cara. |
| 05 | `05-copete.jpg` | Copete de frente, llenando el encuadre. |
| 06 | `06-ambientada.jpg` | Unidad en el piso de venta, abierta, con contexto de tienda. |

Con 01, 02 y 05 ya se arma el tablero. Las demás suman vistas.

## Cómo tomarlas

- **Horizontal**, sin inclinar el teléfono — la cámara paralela a la cara evita
  la distorsión trapezoidal y hace el montaje mucho más limpio.
- Unidad completa en cuadro, con algo de piso abajo.
- Luz de tienda, **sin flash** — el flash quema el vinil y mata el reflejo del vidrio.
- **Mínimo 2000 px por lado.** Mandar el original, no la versión de WhatsApp:
  WhatsApp recomprime a ~1600 px y el resultado se nota en impresión.
- Sin dedos, bolsas ni carritos tapando las caras a vestir.

## Montaje

```
python3 tools/montaje.py fotos/01-frente.jpg arte/frente.png salida.png \
    --quad "x1,y1 x2,y2 x3,y3 x4,y4" --luz 0.55
```

Las cuatro esquinas van en orden superior-izq, superior-der, inferior-der,
inferior-izq, en píxeles de la foto. `--luz` controla cuánta iluminación del
soporte hereda el arte para que no quede como calca plana.
