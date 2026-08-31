"""
Geometria volumetrica de las dos piezas, como campo de distancia con signo.

No es el esculpido final: es la MAQUETA de volumen. Fija escala, poses,
proporciones, footprint y masa. El detalle facial, la ropa y el pelo los pone
el escultor encima de este volumen, y mueven la masa menos del 8% porque el
detalle de un figurin vive en los primeros milimetros de superficie.

    Pieza A  familia de cuatro + mesa con pastel y bolsas
    Pieza B  personaje estilo Pixar con gorra + bulldog sentado

Todas las cotas en mm. Z = 0 es la cama de impresion.
"""

import numpy as np

F = np.float32


# --- primitivas -------------------------------------------------------------
def sd_sphere(p, c, r):
    return np.sqrt(((p - F(c)) ** 2).sum(-1)) - F(r)


def sd_ellipsoid(p, c, r):
    q = (p - F(c)) / F(r)
    k0 = np.sqrt((q ** 2).sum(-1))
    k1 = np.sqrt(((q / F(r)) ** 2).sum(-1))
    return np.where(k0 > 1e-6, k0 * (k0 - 1.0) / np.maximum(k1, 1e-6), -min(r))


def sd_round_box(p, c, b, r):
    q = np.abs(p - F(c)) - (F(b) - F(r))
    return (np.sqrt((np.maximum(q, 0.0) ** 2).sum(-1))
            + np.minimum(q.max(-1), 0.0) - F(r))


def sd_capsule(p, a, b, ra, rb=None):
    """Capsula de radio variable entre los puntos a y b (tronco de cono redondeado)."""
    rb = ra if rb is None else rb
    a, b = np.array(a, np.float32), np.array(b, np.float32)
    pa = p - a
    ba = b - a
    L2 = float((ba ** 2).sum())
    h = np.clip((pa * ba).sum(-1) / L2, 0.0, 1.0)
    d = np.sqrt(((pa - ba * h[..., None]) ** 2).sum(-1))
    return d - (F(ra) + (F(rb) - F(ra)) * h)


def sd_cylinder_z(p, c, r, hh):
    d = np.sqrt(((p[..., :2] - F(c[:2])) ** 2).sum(-1)) - F(r)
    w = np.abs(p[..., 2] - F(c[2])) - F(hh)
    return (np.minimum(np.maximum(d, w), 0.0)
            + np.sqrt(np.maximum(d, 0.0) ** 2 + np.maximum(w, 0.0) ** 2))


def smin(a, b, k):
    """Union suave: la carne que un escultor deja en cada juntura."""
    k = F(k)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def umin(*ds):
    out = ds[0]
    for d in ds[1:]:
        out = np.minimum(out, d)
    return out


# --- figura humana estilizada ----------------------------------------------
def figura(p, x0, y0, h, ancho=1.0, brazo_izq="lado", brazo_der="lado",
           pelo="corto", falda=False, gorra=False):
    """Un cuerpo completo de altura h apoyado en z=0, centrado en (x0, y0).

    Proporciones de figurin coleccionable: 6.5 cabezas, no 7.5 anatomicas.
    Un figurin con proporcion real se ve enfermo a 140 mm; el cliente compra
    la version de 6.5 cabezas aunque no sepa nombrarla.
    """
    u = h / 100.0                     # todo escalado a la altura
    w = ancho
    cab_r = 9.5 * u
    z_cab = h - cab_r * 1.05
    z_hom = z_cab - cab_r * 1.30
    z_cad = h * 0.47
    z_rod = h * 0.26

    d = sd_capsule(p, (x0, y0, z_cad), (x0, y0, z_hom),
                   10.5 * u * w, 12.0 * u * w)                 # torso
    d = smin(d, sd_capsule(p, (x0, y0, z_hom - 1 * u),
                           (x0, y0, z_cab - cab_r * 0.55), 5.0 * u), 3.0 * u)
    d = smin(d, sd_sphere(p, (x0, y0 + 0.6 * u, z_cab), cab_r), 2.5 * u)

    # el pelo va DETRAS de la cara: la figura mira hacia -y (los pies apuntan alli)
    if pelo == "largo":
        d = smin(d, sd_capsule(p, (x0, y0 + 1.5 * u, z_cab + cab_r * 0.35),
                               (x0, y0 + 3.0 * u, z_hom - 6 * u),
                               cab_r * 0.92, cab_r * 0.62), 2.0 * u)
    else:
        d = smin(d, sd_sphere(p, (x0, y0 + 1.4 * u, z_cab + cab_r * 0.20),
                              cab_r * 1.00), 1.5 * u)
    if gorra:
        d = umin(d, sd_cylinder_z(p, (x0, y0 + 0.6 * u, z_cab + cab_r * 0.50),
                                  cab_r * 1.04, cab_r * 0.30))
        d = smin(d, sd_sphere(p, (x0, y0 + 0.6 * u, z_cab + cab_r * 0.18),
                              cab_r * 1.05), 1.0 * u)
        d = umin(d, sd_round_box(p, (x0, y0 - cab_r * 1.00, z_cab + cab_r * 0.34),
                                 (cab_r * 0.62, cab_r * 0.52, 1.2 * u), 1.0 * u))

    # piernas
    dx = 5.2 * u * w
    if falda:
        d = smin(d, sd_capsule(p, (x0, y0, z_cad + 3 * u),
                               (x0, y0, z_cad - 12 * u),
                               11.0 * u * w, 14.5 * u * w), 3.0 * u)
        z_pie = z_cad - 12 * u
    else:
        z_pie = z_cad
    for s in (-1, 1):
        d = smin(d, sd_capsule(p, (x0 + s * dx, y0, min(z_cad, z_pie)),
                               (x0 + s * dx * 0.92, y0, z_rod),
                               6.4 * u * w, 5.2 * u * w), 2.5 * u)
        d = smin(d, sd_capsule(p, (x0 + s * dx * 0.92, y0, z_rod),
                               (x0 + s * dx * 0.88, y0, 2.6 * u),
                               5.0 * u * w, 4.0 * u * w), 2.0 * u)
        d = smin(d, sd_round_box(p, (x0 + s * dx * 0.88, y0 - 2.4 * u, 2.2 * u),
                                 (4.6 * u, 6.6 * u, 2.2 * u), 1.8 * u), 2.0 * u)

    # brazos
    hx = 11.5 * u * w
    for s, modo in ((-1, brazo_izq), (1, brazo_der)):
        hombro = (x0 + s * hx, y0, z_hom - 1.5 * u)
        if modo == "abrazo":                     # sobre el hombro del de al lado
            codo = (x0 + s * (hx + 9 * u), y0 - 1 * u, z_hom - 8 * u)
            mano = (x0 + s * (hx + 22 * u), y0 + 1 * u, z_hom + 1.5 * u)
        elif modo == "bolsillo":
            codo = (x0 + s * (hx + 7 * u), y0 - 2 * u, z_hom - 16 * u)
            mano = (x0 + s * (hx - 1 * u), y0 - 3 * u, z_cad + 3 * u)
        else:                                     # colgando
            codo = (x0 + s * (hx + 2 * u), y0 - 1 * u, z_hom - 15 * u)
            mano = (x0 + s * (hx + 3 * u), y0 - 1 * u, z_cad - 2 * u)
        d = smin(d, sd_capsule(p, hombro, codo, 4.6 * u * w, 3.9 * u), 2.6 * u)
        d = smin(d, sd_capsule(p, codo, mano, 3.9 * u, 3.2 * u), 2.0 * u)
        d = smin(d, sd_sphere(p, mano, 3.6 * u), 1.6 * u)
    return d


# --- bulldog ----------------------------------------------------------------
def bulldog(p, x0, y0, h=52.0):
    """Bulldog sentado, alto total h, apoyado en z=0."""
    u = h / 52.0
    z_gr = 20 * u
    d = sd_capsule(p, (x0, y0 + 9 * u, z_gr + 3 * u),
                   (x0, y0 - 6 * u, z_gr + 9 * u), 13.5 * u, 12.0 * u)
    d = smin(d, sd_ellipsoid(p, (x0, y0 + 8 * u, 10 * u),
                             (14 * u, 13 * u, 10 * u)), 4 * u)     # ancas
    cab = (x0, y0 - 10 * u, h - 10.5 * u)
    d = smin(d, sd_capsule(p, (x0, y0 - 4 * u, z_gr + 11 * u), cab,
                           7.5 * u, 10.5 * u), 4.0 * u)            # cuello
    d = smin(d, sd_ellipsoid(p, cab, (12.0 * u, 10.5 * u, 10.0 * u)), 2 * u)
    d = smin(d, sd_ellipsoid(p, (x0, y0 - 18.0 * u, h - 13.0 * u),
                             (8.4 * u, 5.4 * u, 5.6 * u)), 3.2 * u)  # hocico
    for s in (-1, 1):
        # oreja de rosa: pegada al craneo y caida, no de peluche parado
        d = smin(d, sd_ellipsoid(p, (x0 + s * 9.2 * u, y0 - 8 * u, h - 6.0 * u),
                                 (2.2 * u, 4.2 * u, 4.6 * u)), 2.2 * u)
        d = smin(d, sd_capsule(p, (x0 + s * 9.0 * u, y0 - 12 * u, z_gr - 1 * u),
                               (x0 + s * 9.5 * u, y0 - 14 * u, 3.0 * u),
                               5.4 * u, 5.0 * u), 3.0 * u)          # patas del.
        d = smin(d, sd_round_box(p, (x0 + s * 9.5 * u, y0 - 17 * u, 2.6 * u),
                                 (5.0 * u, 6.5 * u, 2.6 * u), 2.2 * u), 2.0 * u)
        d = smin(d, sd_ellipsoid(p, (x0 + s * 12 * u, y0 + 8 * u, 5.5 * u),
                                 (4.5 * u, 8.0 * u, 5.0 * u)), 3.0 * u)  # patas tr.
    return d


# ============================================================================
#  PIEZA A — familia de cuatro + mesa con pastel y bolsas
# ============================================================================
A_W, A_D, A_T = 196.0, 112.0, 8.0
A_H = 152.0

_A_FIG = [
    # x0     alto  ancho  izq        der        pelo     falda
    (-72.0, 128.0, 0.92, "lado",    "abrazo",  "largo", True),
    (-26.0, 140.0, 1.06, "abrazo",  "abrazo",  "corto", False),
    (26.0, 126.0, 0.94, "abrazo",  "lado",    "largo", False),
    (72.0, 145.0, 1.04, "abrazo",  "bolsillo", "corto", False),
]
_A_YF = 25.0
_A_YM = -22.0
_A_MESA_Z = 46.0


def pieza_a(p):
    base = sd_round_box(p, (0, 0, A_T / 2), (A_W / 2, A_D / 2, A_T / 2), 7.0)
    d = base
    for x0, h, w, bi, bd, pl, fa in _A_FIG:
        f = figura(p - np.array([0, 0, A_T], np.float32), x0, _A_YF, h,
                   ancho=w, brazo_izq=bi, brazo_der=bd, pelo=pl, falda=fa)
        d = smin(d, f, 3.5)

    # mesa: cubierta delgada sobre dos soportes que llegan a la base
    z = _A_MESA_Z + A_T
    mesa = sd_round_box(p, (0, _A_YM, z), (74.0, 26.0, 2.6), 2.2)
    for s in (-1, 1):
        mesa = umin(mesa, sd_round_box(p, (s * 58.0, _A_YM, (z + A_T) / 2),
                                       (4.0, 4.0, (z - A_T) / 2 + 1), 3.0))
    d = umin(d, mesa)

    # pastel + vela
    ztop = z + 2.6
    pastel = sd_cylinder_z(p, (0, _A_YM, ztop + 9.0), 20.0, 9.0)
    pastel = smin(pastel, sd_cylinder_z(p, (0, _A_YM, ztop + 1.6), 24.0, 1.6), 1.5)
    vela = sd_cylinder_z(p, (0, _A_YM, ztop + 18 + 9.0), 2.4, 9.0)
    vela = umin(vela, sd_sphere(p, (0, _A_YM, ztop + 27.5), 2.0))
    d = umin(d, pastel, vela)

    # bolsas de regalo, con asa
    for s in (-1, 1):
        bx = s * 45.0
        bolsa = sd_round_box(p, (bx, _A_YM, ztop + 14.0), (13.0, 6.5, 14.0), 1.6)
        asa = sd_capsule(p, (bx - 6.0, _A_YM, ztop + 28.0),
                         (bx, _A_YM, ztop + 33.0), 1.5)
        asa = umin(asa, sd_capsule(p, (bx, _A_YM, ztop + 33.0),
                                   (bx + 6.0, _A_YM, ztop + 28.0), 1.5))
        d = umin(d, bolsa, asa)
    return d


# ============================================================================
#  PIEZA B — personaje con gorra + bulldog
# ============================================================================
B_W, B_D, B_T = 124.0, 92.0, 8.0
B_H = 158.0
_B_XP, _B_YP, _B_HP = -20.0, 6.0, 148.0
_B_XD, _B_YD, _B_HD = 36.0, -14.0, 54.0


def pieza_b(p):
    d = sd_round_box(p, (0, 0, B_T / 2), (B_W / 2, B_D / 2, B_T / 2), 7.0)
    q = p - np.array([0, 0, B_T], np.float32)
    d = smin(d, figura(q, _B_XP, _B_YP, _B_HP, ancho=1.10,
                       brazo_izq="bolsillo", brazo_der="bolsillo",
                       pelo="corto", gorra=True), 3.5)
    d = smin(d, bulldog(q, _B_XD, _B_YD, _B_HD), 3.5)
    return d


PIEZAS = {
    "A": dict(f=pieza_a, w=A_W, d=A_D, h=A_H,
              nombre="Familia de cuatro con pastel"),
    "B": dict(f=pieza_b, w=B_W, d=B_D, h=B_H,
              nombre="Personaje con gorra y bulldog"),
}
