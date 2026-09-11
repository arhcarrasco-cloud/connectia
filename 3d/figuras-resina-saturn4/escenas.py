"""
Las dos escenas completas, cada una como una funcion del campo.

    ESCENAS["duo"]   figura A - mujer con pandero + hombre con guitarra
    ESCENAS["diploma"] figura B - hombre de traje frente a la placa

Cada escena declara tambien su caja de trabajo y los barrenos de desfogue,
que es lo que verificar.py y costear.py necesitan saber.
"""

import numpy as np

import figuras as F
import sdf as S

PEANA_T = F.PEANA_T


# =============================================================================
# FIGURA A - duo de alabanza
# =============================================================================
A_PEANA = (78.0, 46.0)

# Reparto del cuadro, igual que en la foto: la mujer a la IZQUIERDA (x
# negativa, porque con la camara en -Y el eje +X cae a la derecha del cuadro)
# y el hombre a la derecha. El mastil de la guitarra sale hacia +X, o sea
# hacia el borde del cuadro y no hacia ella -- que ademas es como cuelga una
# guitarra DIESTRA: el mastil va a la izquierda del que toca.
A_MUJER = dict(
    H=158.0, z0=PEANA_T, origen=(-38.0, 2.0), sexo="f",
    pelo="largo", lentes=True, zapato="vestir",
    holgura_ropa=1.7, dobladillo=0.60,
    muneca_x_pos=(-21.0, -36.0, 133.0),     # golpea el parche
    muneca_x_neg=(-40.0, -28.0, 121.0),     # sostiene el aro
)
A_HOMBRE = dict(
    H=172.0, z0=PEANA_T, origen=(40.0, 2.0), sexo="m",
    pelo="corto", lentes=True, barba=True, zapato="tenis",
    holgura_ropa=1.1, dobladillo=0.58,
    muneca_x_pos=(70.7, -20.0, 118.0),      # su izquierda: sobre el mastil
    muneca_x_neg=(33.0, -17.0, 154.0),      # su derecha: alzada junto al rostro
)
A_PANDERO = dict(c=(-31.0, -32.0, 127.0), diam=26.0, canto=7.0,
                 yaw=18.0, roll=76.0)
# La caja queda centrada en (28, -20, 96) y el clavijero sale a x = 93.
A_GUITARRA = dict(c=(54.7, -20.0, 109.6), largo=100.0, yaw=-12.0, roll=63.0)

# CANALES internos: comunican la cavidad de cada pierna con la de la peana
# atravesando el zapato, que por delgado se queda macizo. No salen al exterior:
# la cara inferior de la peana queda entera.
# Ya en coordenadas de MUNDO, o sea despues del espejo de duo(): la mujer
# queda en x negativa y el hombre en x positiva.
A_CANALES = [
    ((-46.1, 2.6, 3.0), (-46.1, 2.6, 37.0), 2.0),   # mujer, pierna exterior
    ((-29.9, 2.6, 3.0), (-29.9, 2.6, 37.0), 2.0),   # mujer, pierna interior
    ((31.2, 2.7, 3.0), (31.2, 2.7, 39.0), 2.0),     # hombre, pierna interior
    ((48.8, 2.7, 3.0), (48.8, 2.7, 39.0), 2.0),     # hombre, pierna exterior
]
# RESPIRADEROS: salen por el canto TRASERO de la peana, no por la cara de
# abajo. Es la diferencia entre una pieza que desagua y una ventosa: apoyada
# en la placa, un barreno inferior queda sellado y la cavidad forma vacio.
A_RESPIRADEROS = [
    ((35.0, 52.0, 6.0), (35.0, 22.0, 6.0), 2.0),
    ((-35.0, 52.0, 6.0), (-35.0, 22.0, 6.0), 2.0),
]


def duo(X, Y, Z):
    d = F.peana(X, Y, Z, *A_PEANA)
    d = S.sunion(d, F.cuerpo(X, Y, Z, A_MUJER), 2.0)
    d = S.sunion(d, F.cuerpo(X, Y, Z, A_HOMBRE), 2.0)
    d = S.union(d, F.pandero(X, Y, Z, **A_PANDERO))
    d = S.union(d, F.guitarra(X, Y, Z, **A_GUITARRA))
    return d



# =============================================================================
# FIGURA B - reconocimiento
# =============================================================================
B_PEANA = (78.0, 52.0)
B_HOMBRE = dict(
    H=168.0, z0=PEANA_T, origen=(0.0, -6.0), sexo="m",
    pelo="corto", lentes=True, zapato="vestir",
    holgura_ropa=1.7, dobladillo=0.55,       # el saco
    muneca_x_pos=(19.5, -8.0, 93.5),
    muneca_x_neg=(-19.5, -8.0, 93.5),
)
B_PLACA = dict(c=(0.0, 30.0, 130.0), W=150.0, Hh=100.0, T=9.0)
B_POSTES = [(58.0, 26.0, 0.0, 176.0, 4.6), (-58.0, 26.0, 0.0, 176.0, 4.6)]

B_CANALES = [
    ((8.6, -5.3, 3.0), (8.6, -5.3, 38.0), 2.0),     # pierna +x
    ((-8.6, -5.3, 3.0), (-8.6, -5.3, 38.0), 2.0),   # pierna -x
]
B_RESPIRADEROS = [
    ((35.0, 58.0, 6.0), (35.0, 26.0, 6.0), 2.0),
    ((-35.0, 58.0, 6.0), (-35.0, 26.0, 6.0), 2.0),
]


def _traje(X, Y, Z, cfg):
    """Los detalles del traje: solapa en V, corbata y cuello de camisa."""
    H, z0 = cfg["H"], cfg["z0"]
    ox, oy = cfg["origen"]
    z_cuello = z0 + 0.822 * H
    y_frente = oy - 0.070 * H

    # corbata: dos cajas afiladas, nudo arriba
    nudo = S.caja(X, Y, Z, (ox, y_frente + 0.6, z_cuello - 3.0),
                  (3.4, 2.2, 3.4), 1.0)
    pala = S.cono_redondo(X, Y, Z,
                          (ox, y_frente + 1.2, z_cuello - 6.0), 2.6,
                          (ox, y_frente + 3.4, z0 + 0.672 * H), 4.6)
    corbata = S.union(nudo, pala)

    # cuello de camisa: dos aletas
    cuello = None
    for s in (+1, -1):
        aleta = S.capsula(X, Y, Z,
                          (ox + s * 7.5, y_frente + 5.0, z_cuello + 3.0),
                          (ox + s * 2.6, y_frente + 1.8, z_cuello - 4.5), 1.6)
        cuello = aleta if cuello is None else S.union(cuello, aleta)
    return S.union(corbata, cuello)


def _solapa(X, Y, Z, cfg):
    """Surco en V del saco, tallado sobre la piel del torso."""
    H, z0 = cfg["H"], cfg["z0"]
    ox, oy = cfg["origen"]
    v = None
    for s in (+1, -1):
        rama = S.capsula(X, Y, Z,
                         (ox + s * 11.0, oy - 0.072 * H, z0 + 0.798 * H),
                         (ox + s * 2.5, oy - 0.070 * H, z0 + 0.690 * H), 1.0)
        v = rama if v is None else S.union(v, rama)
    return v


def diploma(X, Y, Z):
    d = F.peana(X, Y, Z, *B_PEANA)
    cuerpo = F.cuerpo(X, Y, Z, B_HOMBRE)
    cuerpo = S.resta(cuerpo, S.interseccion(S.cascara(cuerpo, 1.1),
                                            _solapa(X, Y, Z, B_HOMBRE)))
    cuerpo = S.sunion(cuerpo, _traje(X, Y, Z, B_HOMBRE), 1.6)
    d = S.sunion(d, cuerpo, 2.0)
    for cx, cy, z0, z1, r in B_POSTES:
        d = S.sunion(d, F.poste(X, Y, Z, cx, cy, z0, z1, r), 2.0)
    d = S.union(d, F.placa_diploma(X, Y, Z, **B_PLACA))
    return d


# =============================================================================
ESCENAS = {
    "duo": dict(
        nombre="Duo de alabanza",
        f=duo,
        caja=((-86.0, 104.0), (-62.0, 60.0), (-1.0, 192.0)),
        canales=A_CANALES,
        respiraderos=A_RESPIRADEROS,
        alto_total=PEANA_T + A_HOMBRE["H"],
        detalle_min=2 * 0.0055 * A_MUJER["H"],   # aro de los lentes
    ),
    "diploma": dict(
        nombre="Reconocimiento",
        f=diploma,
        caja=((-80.0, 80.0), (-60.0, 64.0), (-1.0, 188.0)),
        canales=B_CANALES,
        respiraderos=B_RESPIRADEROS,
        alto_total=PEANA_T + B_HOMBRE["H"],
        detalle_min=2 * 0.0055 * B_HOMBRE["H"],  # aro de los lentes
    ),
}
