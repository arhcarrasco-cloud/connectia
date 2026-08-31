# Figurines de retrato desde foto — cotización

Dos piezas independientes, pedidas a partir de dos fotos: un grupo familiar de
cuatro con pastel, y un personaje estilo Pixar con gorra de béisbol junto a un
bulldog. Se cotizan **por separado**, cada una con su costo y su precio.

Filamento **PLA a $300/kg = $0.30/g**, dato del cliente.

## Lo primero, porque cambia toda la lectura del número

Un figurín de retrato **no se vende por el plástico**. El PLA es el 20% del
costo de producción de la pieza A y el 15% de la B, y menos del 3% del precio
final de una pieza única. Lo que se cobra son las **horas de escultura**:
sacar volumen, proporción y parecido de una foto plana, que es un trabajo
manual que no tiene atajo.

Por eso el costeo separa dos cosas que casi siempre se confunden:

| | qué es | se repite |
|---|---|---|
| **Ingeniería** | esculpir el modelo desde la foto | **no**, se paga una vez |
| **Producción** | imprimir, quitar soporte, lijar, sellar, empacar | sí, en cada copia |

La consecuencia práctica: **la copia 2 cuesta una fracción de la copia 1.**
Si la pieza A va a ser un regalo para los cuatro de la foto, se piden cuatro y
el precio unitario cae de $7,210 a $2,410. Ese es el único descuento real que
existe aquí, y no es un descuento: es que la escultura ya está pagada.

## Números

Todo **ESTIMADO**, no medido — ver la advertencia al final.

### Pieza A — familia de cuatro con pastel

`196 × 112 × 152 mm` · PLA · capa 0.20 mm · 3 paredes · relleno gyroid 12%

```
Consumo                     243.4 g   ·   6.6 h de máquina (banda 4.4 – 8.9 h)
                            196.3 cm3 de filamento, soporte de árbol incluido

Costo de producción, por copia
  filamento PLA 243 g @ $0.30/g   $    73.02
  depreciación de máquina         $    16.87
  energía                         $     1.59
  merma 8%                        $     7.32
  reimpresión (8% de fallo)       $     8.59
  posproceso 1.6 h @ $120/h       $   192.00
  empaque                         $    65.00
  ------------------------------------------
  COSTO DE PRODUCCIÓN             $   364.39

Costo de ingeniería, una sola vez
  escultura desde foto 16 h @ $260/h  $ 4,160.00
```

| tiraje | ing./pieza | costo | **precio** | utilidad | margen |
|---:|---:|---:|---:|---:|---:|
| 1 | 4,160 | 4,524 | **7,210** | 2,685 | 37% |
| 4 | 1,040 | 1,404 | **2,410** | 1,005 | 42% |
| 10 | 416 | 780 | **1,450** | 669 | 46% |
| 25 | 166 | 531 | **1,066** | 535 | 50% |

### Pieza B — personaje con gorra y bulldog

`124 × 92 × 158 mm` · mismos parámetros

```
Consumo                      98.6 g   ·   2.7 h de máquina (banda 1.8 – 3.6 h)
                             79.5 cm3 de filamento, soporte incluido

Costo de producción, por copia
  filamento PLA 99 g @ $0.30/g    $    29.58
  depreciación de máquina         $     6.82
  energía                         $     0.64
  merma 8%                        $     2.96
  reimpresión (8% de fallo)       $     3.48
  posproceso 0.9 h @ $120/h       $   108.00
  empaque                         $    45.00
  ------------------------------------------
  COSTO DE PRODUCCIÓN             $   196.48

Costo de ingeniería, una sola vez
  escultura desde foto 8 h @ $260/h   $ 2,080.00
```

| tiraje | ing./pieza | costo | **precio** | utilidad | margen |
|---:|---:|---:|---:|---:|---:|
| 1 | 2,080 | 2,276 | **3,637** | 1,360 | 37% |
| 4 | 520 | 716 | **1,237** | 520 | 42% |
| 10 | 208 | 404 | **757** | 352 | 47% |
| 25 | 83 | 280 | **565** | 285 | 50% |

### Las dos juntas, una copia de cada una

| | g | h | producción | ingeniería | **costo** | **precio** |
|---|---:|---:|---:|---:|---:|---:|
| A | 243 | 6.6 | 364 | 4,160 | 4,524 | 7,210 |
| B | 99 | 2.7 | 196 | 2,080 | 2,276 | 3,637 |
| **A+B** | | | | | **6,801** | **10,846** |

Sin IVA. Con factura son **$12,582**.

La pieza A no cuesta cuatro veces la B aunque tenga cuatro figuras: el cuerpo
base se reusa entre las cuatro y solo la cabeza, el pelo y la ropa se esculpen
desde cero en cada una. 16 h contra 8 h, no 32 contra 8.

## Los supuestos, para que se puedan discutir

Están todos en la cabecera de `costeo_figuras.py` y se cambian ahí.

| supuesto | valor | de dónde sale |
|---|---|---|
| PLA | $0.30/g | dato del cliente, $300/kg |
| depreciación de máquina | $2.54/h | P1S a 5 años, 2000 h/año |
| soporte de árbol | 17% del volumen | axilas, barbilla, hocico, visera, asas |
| tasa de fallo | 8% | una torre de 150 mm falla más que una placa |
| posproceso | $120/h de taller | 1.6 h la A, 0.9 h la B |
| escultura | $260/h freelance MX | 16 h la A, 8 h la B |
| margen de ingeniería | 35% | es servicio, se entrega una vez, no se revende |
| margen de producción | 55% | esto sí es producto |

El margen de reimpresión son `1/(1−0.08)` intentos, no `1.08`. Es una
diferencia chica en esta pieza y grande en una con 20% de fallo.

Dos supuestos son los que mueven el precio de verdad, y ninguno de los dos es
una medición: **las horas de escultura** y **el margen de ingeniería**. Si el
modelador cobra $180/h en vez de $260, la pieza A única baja a $5,244.

## Qué hay en esta carpeta

```
figuras_sdf.py      geometría de las dos piezas como campo de distancia
render_figuras.py   render por ray marching sobre el campo → PNG
costeo_figuras.py   rebanado simulado + costeo → los números de arriba
exportar_stl.py     marching cubes → STL, para rebanar en Bambu Studio
```

```bash
python3 render_figuras.py                  # renders a 1400 px
python3 costeo_figuras.py                  # cotización (usa cache del rebanado)
python3 costeo_figuras.py --rebanar        # ignora el cache, ~7 min
python3 exportar_stl.py --res 0.55         # STL, ~3 min, no se versionan
```

El rebanado tarda minutos y su resultado solo depende de la geometría y de los
parámetros de proceso, así que se cachea en `.rebanado.json` con una huella de
los dos. Si cambia `figuras_sdf.py` o cualquier parámetro, el cache se invalida
solo.

## Lo que estos archivos SÍ son y lo que NO son

**Son la maqueta de volumen.** Fijan escala, pose, footprint, masa y tiempo de
máquina, que es exactamente lo que hace falta para cotizar. La geometría se
verifica al releer el STL: triángulos, caja envolvente y volumen por el teorema
de la divergencia.

**No son el esculpido final.** No hay parecido facial, ni ropa, ni textura de
pelo. Eso lo pone el escultor encima de este volumen, y mueve la masa menos del
8% porque el detalle de un figurín vive en los primeros milímetros de
superficie. El render sirve para aprobar composición y tamaño antes de pagar
las horas caras, no para enseñar cómo va a quedar la cara.

## ⚠ Antes de mandarle esto a un cliente como cotización en firme

Los gramos y las horas son **ESTIMADO, no MEDIDO**. El rebanado de
`costeo_figuras.py` es una simulación sobre el campo de distancia — separa
perímetro, cáscara sólida y relleno capa por capa, y calcula el tiempo por
longitud de trayectoria contra dos juegos de velocidad — pero **no es
CuraEngine**. La banda de tiempo de la pieza A va de 4.4 a 8.9 h; esa
dispersión es real y es la razón de no presentarlo como cifra dura.

Para cerrarlo:

```bash
python3 exportar_stl.py                    # genera pieza-A.stl y pieza-B.stl
# abre los dos en Bambu Studio, rebana, anota gramos y horas
python3 costeo_figuras.py --medido A 251 7.2 --medido B 103 2.9
```

Ahí el encabezado cambia de `[ESTIMADO]` a `[MEDIDO]` y el número se puede
firmar. Las horas de escultura siguen siendo un supuesto de taller aunque el
rebanado ya esté medido: ésas se ajustan al modelador que se vaya a usar.
