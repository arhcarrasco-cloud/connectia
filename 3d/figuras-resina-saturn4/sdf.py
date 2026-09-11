"""
Libreria de campos de distancia con signo (SDF), vectorizada sobre numpy.

Todas las funciones reciben (X, Y, Z) como arreglos de la misma forma y
devuelven la distancia con signo: negativa dentro del solido, positiva fuera.

Convencion del proyecto:
    Z hacia arriba, Z = 0 en la cama de impresion.
    El personaje mira hacia -Y (la camara de frente vive en -Y).
    +X es la izquierda del espectador.
"""

import numpy as np

EPS = 1e-9


# --- utilidades --------------------------------------------------------------
def _d2(*comps):
    """Suma de cuadrados."""
    out = comps[0] * comps[0]
    for c in comps[1:]:
        out = out + c * c
    return out


def _norm(*comps):
    return np.sqrt(_d2(*comps) + EPS)


def local(X, Y, Z, origen=(0.0, 0.0, 0.0), yaw=0.0, pitch=0.0, roll=0.0):
    """Lleva el punto al marco local de una pieza rotada.

    yaw   gira alrededor de Z (apunta el personaje o el brazo de lado)
    pitch gira alrededor de X (inclina hacia adelante/atras)
    roll  gira alrededor de Y (ladea)

    Rota el PUNTO por la inversa, que es como se transforma un SDF.
    """
    x = X - origen[0]
    y = Y - origen[1]
    z = Z - origen[2]
    if yaw:
        c, s = np.cos(np.radians(yaw)), np.sin(np.radians(yaw))
        x, y = c * x + s * y, -s * x + c * y
    if pitch:
        c, s = np.cos(np.radians(pitch)), np.sin(np.radians(pitch))
        y, z = c * y + s * z, -s * y + c * z
    if roll:
        c, s = np.cos(np.radians(roll)), np.sin(np.radians(roll))
        x, z = c * x - s * z, s * x + c * z
    return x, y, z


# --- primitivas --------------------------------------------------------------
def esfera(X, Y, Z, c, r):
    return _norm(X - c[0], Y - c[1], Z - c[2]) - r


def elipsoide(X, Y, Z, c, r):
    """SDF aproximado de iq: exacto en la superficie, Lipschitz cerca de 1."""
    px, py, pz = X - c[0], Y - c[1], Z - c[2]
    k0 = _norm(px / r[0], py / r[1], pz / r[2])
    k1 = _norm(px / r[0] ** 2, py / r[1] ** 2, pz / r[2] ** 2)
    return k0 * (k0 - 1.0) / k1


def caja(X, Y, Z, c, half, r=0.0):
    """Caja redondeada. `half` son los semilados TOTALES (radio incluido)."""
    qx = np.abs(X - c[0]) - (half[0] - r)
    qy = np.abs(Y - c[1]) - (half[1] - r)
    qz = np.abs(Z - c[2]) - (half[2] - r)
    fuera = _norm(np.maximum(qx, 0), np.maximum(qy, 0), np.maximum(qz, 0))
    dentro = np.minimum(np.maximum(np.maximum(qx, qy), qz), 0.0)
    return fuera + dentro - r


def capsula(X, Y, Z, a, b, r):
    ax, ay, az = a
    bax, bay, baz = b[0] - ax, b[1] - ay, b[2] - az
    l2 = bax * bax + bay * bay + baz * baz + EPS
    pax, pay, paz = X - ax, Y - ay, Z - az
    h = np.clip((pax * bax + pay * bay + paz * baz) / l2, 0.0, 1.0)
    return _norm(pax - bax * h, pay - bay * h, paz - baz * h) - r


def cono_redondo(X, Y, Z, a, ra, b, rb):
    """Tronco de cono con extremos esfericos (iq). El miembro basico del cuerpo."""
    ax, ay, az = a
    bax, bay, baz = b[0] - ax, b[1] - ay, b[2] - az
    l2 = bax * bax + bay * bay + baz * baz + EPS
    rr = ra - rb
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pax, pay, paz = X - ax, Y - ay, Z - az
    y = pax * bax + pay * bay + paz * baz
    z = y - l2
    x2 = _d2(pax * l2 - bax * y, pay * l2 - bay * y, paz * l2 - baz * y)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    tapa_b = np.sign(z) * a2 * z2 > k
    tapa_a = np.sign(y) * a2 * y2 < k
    lado = (np.sqrt(np.maximum(x2 * a2 * il2, 0.0)) + y * rr) * il2 - ra
    out = np.where(tapa_b, np.sqrt(np.maximum(x2 + z2, 0.0)) * il2 - rb, lado)
    return np.where(~tapa_b & tapa_a,
                    np.sqrt(np.maximum(x2 + y2, 0.0)) * il2 - ra, out)


def toro(X, Y, Z, c, R, r, eje="z"):
    px, py, pz = X - c[0], Y - c[1], Z - c[2]
    if eje == "z":
        q = _norm(px, py) - R
        return _norm(q, pz) - r
    if eje == "y":
        q = _norm(px, pz) - R
        return _norm(q, py) - r
    q = _norm(py, pz) - R
    return _norm(q, px) - r


def cilindro_z(X, Y, Z, c, r, z0, z1, redondeo=0.0):
    """Cilindro vertical entre z0 y z1, con arista redondeada opcional."""
    d = _norm(X - c[0], Y - c[1]) - (r - redondeo)
    h = np.abs(Z - (z0 + z1) / 2.0) - ((z1 - z0) / 2.0 - redondeo)
    fuera = _norm(np.maximum(d, 0), np.maximum(h, 0))
    return fuera + np.minimum(np.maximum(d, h), 0.0) - redondeo


def plano_z(Z, z0):
    """Semiespacio Z >= z0 (material arriba de z0)."""
    return z0 - Z


# --- operadores --------------------------------------------------------------
def union(*ds):
    out = ds[0]
    for d in ds[1:]:
        out = np.minimum(out, d)
    return out


def sunion(a, b, k):
    """Union suave polinomica: mezcla los miembros sin arista viva."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * h - k * h * (1.0 - h)


def sunion_lista(ds, k):
    out = ds[0]
    for d in ds[1:]:
        out = sunion(out, d, k)
    return out


def resta(a, b):
    """a menos b."""
    return np.maximum(a, -b)


def sresta(a, b, k):
    h = np.clip(0.5 - 0.5 * (b + a) / k, 0.0, 1.0)
    return a + (-b - a) * h + k * h * (1.0 - h)


def interseccion(*ds):
    out = ds[0]
    for d in ds[1:]:
        out = np.maximum(out, d)
    return out


def cascara(d, t):
    """Ahueca dejando pared `t`. Lo mas fino que 2t se queda macizo solo."""
    return np.maximum(d, -(d + t))
