"""
Molde solido para chocolate — cavidad negativa de caballo mecedora.

Define el modelo como un campo de distancia con signo (SDF) parametrico.
Todas las cotas estan en milimetros y son las cotas nominales del brief:

    Placa exterior .................. 120.0 x 90.0 mm
    Espesor total ................... 15.0 mm
    Cavidad (bbox de la silueta) .... 100.0 x 70.0 mm
    Profundidad maxima .............. 10.0 mm
    Fondo solido bajo la cavidad .... 5.0 mm
    Margen perimetral ............... 10.0 mm
    Radio esquinas exteriores ....... 6.0 mm
    Redondeo aristas interiores ..... 2.0 mm
    Angulo de salida (draft) ........ 3.0 grados

Convencion de ejes: X = ancho (120), Y = alto de la placa (90),
Z = espesor (0 = cara de cama, 15 = cara superior plana donde abre la cavidad).
"""

import numpy as np

# ----------------------------------------------------------------------------
# Cotas nominales
# ----------------------------------------------------------------------------
PLATE_W = 120.0          # ancho exterior
PLATE_H = 90.0           # alto exterior
PLATE_T = 15.0           # espesor total
CAV_W = 100.0            # ancho de la cavidad
CAV_H = 70.0             # alto de la cavidad
CAV_DEPTH = 10.0         # profundidad maxima
FLOOR = PLATE_T - CAV_DEPTH   # 5.0 mm de fondo solido
CORNER_R = 6.0           # radio de esquinas exteriores
FILLET_R = 2.0           # redondeo de aristas interiores
DRAFT_DEG = 3.0          # angulo de salida
TAN_DRAFT = np.tan(np.radians(DRAFT_DEG))

# El fondo es plano con un realce corto contra la pared: DOME_R es el ancho de
# ese realce. Si se agranda, el retiro del contorno lo dicta el realce y no el
# angulo de salida, y la pared deja de tener los 3 grados pedidos.
DOME_R = 0.05            # ancho de la transicion pared->fondo
DOME_MAX = 9.5           # profundidad del fondo plano (sin grabados)  
DETAIL_MAX = 0.5         # profundidad extra maxima de los grabados

# La cavidad se prolonga por encima de la cara superior. Si se cortara justo en
# Z = PLATE_T el campo valdria exactamente 0 en todo ese plano sobre la cavidad
# (max(0, -0)) y dejaria de ser una distancia util: marching cubes generaria dos
# cascaras coplanares y el ray marching se detendria en la tapa en vez de entrar.
CAV_TOP_EXT = 6.0


# ----------------------------------------------------------------------------
# Primitivas 2D
# ----------------------------------------------------------------------------
def _dot2(x, y):
    return x * x + y * y


def sd_circle(px, py, c, r):
    return np.sqrt(_dot2(px - c[0], py - c[1])) - r


def sd_capsule(px, py, a, b, r):
    pax, pay = px - a[0], py - a[1]
    bax, bay = b[0] - a[0], b[1] - a[1]
    h = np.clip((pax * bax + pay * bay) / (bax * bax + bay * bay), 0.0, 1.0)
    return np.sqrt(_dot2(pax - bax * h, pay - bay * h)) - r


def sd_round_cone(px, py, a, b, r1, r2):
    """Capsula conica (radio r1 en a, r2 en b). Formula de Inigo Quilez."""
    bax, bay = b[0] - a[0], b[1] - a[1]
    l2 = bax * bax + bay * bay
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2

    pax, pay = px - a[0], py - a[1]
    y = pax * bax + pay * bay
    z = y - l2
    x2 = _dot2(pax * l2 - bax * y, pay * l2 - bay * y)
    y2 = y * y * l2
    z2 = z * z * l2

    k = np.sign(rr) * rr * rr * x2
    out = (np.sqrt(x2 * a2 * il2) + y * rr) * il2 - r1
    out = np.where(np.sign(y) * a2 * y2 < k, np.sqrt(x2 + y2) * il2 - r1, out)
    out = np.where(np.sign(z) * a2 * z2 > k, np.sqrt(x2 + z2) * il2 - r2, out)
    return out


def sd_polyline(px, py, pts, r):
    d = None
    for a, b in zip(pts[:-1], pts[1:]):
        s = sd_capsule(px, py, a, b, r)
        d = s if d is None else np.minimum(d, s)
    return d


def smin(a, b, k):
    """Union suave polinomica."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1.0 - h) + a * h - k * h * (1.0 - h)


def sd_rounded_rect(px, py, w, h, r):
    qx = np.abs(px) - (w * 0.5 - r)
    qy = np.abs(py) - (h * 0.5 - r)
    return (np.sqrt(_dot2(np.maximum(qx, 0.0), np.maximum(qy, 0.0)))
            + np.minimum(np.maximum(qx, qy), 0.0) - r)


def op_intersect_round(a, b, r):
    """Interseccion con la arista convexa redondeada de radio r."""
    ua = np.maximum(r + a, 0.0)
    ub = np.maximum(r + b, 0.0)
    return np.minimum(-r, np.maximum(a, b)) + np.sqrt(_dot2(ua, ub))


# ----------------------------------------------------------------------------
# Silueta del caballo mecedora (coordenadas de diseno, mira a la IZQUIERDA)
# ----------------------------------------------------------------------------
_ROCK_R = 105.1          # radio del arco de la base mecedora
_ROCK_CY = 73.5          # centro del arco
_ROCK_HALF = 46.0        # semi-luz de la base
_ROCK_T = 3.4            # semi-espesor de la base


def _rocker_pts(n=48):
    xs = np.linspace(-_ROCK_HALF, _ROCK_HALF, n)
    ys = _ROCK_CY - np.sqrt(_ROCK_R ** 2 - xs ** 2)
    return list(zip(xs.tolist(), ys.tolist()))


# Grupos de piezas. Cada entrada: (callable(px,py), k_de_union)
def _horse_parts():
    P = []
    add = lambda f, k=1.8: P.append((f, k))

    # --- cuerpo compacto -----------------------------------------------------
    add(lambda x, y: sd_round_cone(x, y, (-13.0, 2.0), (16.0, 0.5), 10.5, 11.0), 1.6)
    add(lambda x, y: sd_circle(x, y, (17.5, 0.5), 10.6), 2.2)   # anca

    # --- cuello curvo --------------------------------------------------------
    add(lambda x, y: sd_round_cone(x, y, (-13.0, 6.0), (-27.0, 24.0), 8.8, 6.4), 2.8)

    # --- cabeza redondeada + hocico -----------------------------------------
    add(lambda x, y: sd_round_cone(x, y, (-26.5, 25.5), (-40.0, 18.5), 7.6, 4.8), 1.8)

    # --- orejas pequenas -----------------------------------------------------
    add(lambda x, y: sd_round_cone(x, y, (-25.5, 29.6), (-23.8, 33.8), 2.7, 1.55), 1.0)
    add(lambda x, y: sd_round_cone(x, y, (-29.6, 29.2), (-29.0, 33.0), 2.5, 1.45), 1.0)

    # --- melena --------------------------------------------------------------
    add(lambda x, y: sd_polyline(
        x, y,
        [(-26.5, 30.5), (-22.5, 27.5), (-17.5, 21.0), (-12.6, 14.6), (-9.0, 11.4)],
        3.5), 1.4)

    # --- montura -------------------------------------------------------------
    add(lambda x, y: sd_round_cone(x, y, (0.6, 12.0), (10.4, 11.8), 3.4, 3.4), 1.0)
    add(lambda x, y: sd_circle(x, y, (0.2, 13.0), 2.7), 0.9)    # borren delantero
    add(lambda x, y: sd_circle(x, y, (11.0, 13.4), 2.9), 0.9)   # borren trasero

    # --- patas gruesas + cascos ---------------------------------------------
    # delantera lejana
    add(lambda x, y: sd_round_cone(x, y, (-3.0, -3.0), (-6.0, -18.0), 4.4, 3.6), 3.0)
    add(lambda x, y: sd_circle(x, y, (-7.0, -27.0), 3.8), 1.3)
    add(lambda x, y: sd_round_cone(x, y, (-6.0, -18.0), (-7.0, -26.0), 3.6, 3.7), 1.3)
    # delantera cercana
    add(lambda x, y: sd_round_cone(x, y, (-12.0, -3.0), (-19.0, -18.0), 5.2, 4.2), 3.0)
    add(lambda x, y: sd_round_cone(x, y, (-19.0, -18.0), (-21.0, -25.0), 4.2, 4.4), 1.4)
    add(lambda x, y: sd_circle(x, y, (-21.5, -26.4), 4.6), 1.4)
    # trasera lejana
    add(lambda x, y: sd_round_cone(x, y, (5.0, -3.0), (9.0, -18.0), 4.6, 3.7), 3.0)
    add(lambda x, y: sd_round_cone(x, y, (9.0, -18.0), (10.0, -26.0), 3.7, 3.8), 1.3)
    add(lambda x, y: sd_circle(x, y, (10.0, -27.0), 3.9), 1.3)
    # trasera cercana
    add(lambda x, y: sd_round_cone(x, y, (14.0, -3.0), (22.0, -18.0), 5.4, 4.3), 3.0)
    add(lambda x, y: sd_round_cone(x, y, (22.0, -18.0), (24.0, -25.0), 4.3, 4.4), 1.4)
    add(lambda x, y: sd_circle(x, y, (24.5, -26.3), 4.6), 1.4)

    # --- cola curva ----------------------------------------------------------
    add(lambda x, y: sd_round_cone(x, y, (22.0, 8.5), (34.5, 3.0), 4.8, 3.6), 2.6)
    add(lambda x, y: sd_round_cone(x, y, (34.5, 3.0), (37.2, -5.0), 3.6, 3.0), 1.6)
    add(lambda x, y: sd_round_cone(x, y, (37.0, -5.0), (35.2, -14.0), 3.0, 2.6), 1.6)

    # --- base mecedora continua ---------------------------------------------
    rp = _rocker_pts()
    add(lambda x, y: sd_polyline(x, y, rp, _ROCK_T), 3.0)

    return P


_PARTS = _horse_parts()


def horse_sd_design(px, py):
    """SDF de la silueta en coordenadas de diseno."""
    d = None
    for f, k in _PARTS:
        s = f(px, py)
        d = s if d is None else smin(d, s, k)
    return d


# ----------------------------------------------------------------------------
# Ajuste exacto de la silueta a 100 x 70 mm, centrada en la placa
# ----------------------------------------------------------------------------
def _measure(n=1400):
    xs = np.linspace(-60.0, 60.0, n)
    ys = np.linspace(-45.0, 45.0, int(n * 0.75))
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    D = horse_sd_design(X, Y)
    inside = D <= 0.0
    xi = np.where(inside.any(axis=1))[0]
    yi = np.where(inside.any(axis=0))[0]
    # refinamiento sub-pixel usando el valor del SDF en el borde
    x0, x1 = xs[xi[0]], xs[xi[-1]]
    y0, y1 = ys[yi[0]], ys[yi[-1]]
    return x0, x1, y0, y1


_X0, _X1, _Y0, _Y1 = _measure()
SX = CAV_W / (_X1 - _X0)
SY = CAV_H / (_Y1 - _Y0)
CXD = 0.5 * (_X0 + _X1)
CYD = 0.5 * (_Y0 + _Y1)
_S_METRIC = min(SX, SY)


def design_to_plate(px, py):
    """Convierte coordenadas de diseno a coordenadas de placa."""
    return (px - CXD) * SX, (py - CYD) * SY


def plate_to_design(X, Y):
    return X / SX + CXD, Y / SY + CYD


def horse_sd(X, Y):
    """SDF de la silueta ya escalada al plano de la placa (mm reales)."""
    px, py = plate_to_design(X, Y)
    return horse_sd_design(px, py) * _S_METRIC


# ----------------------------------------------------------------------------
# Grabados (detalles hundidos hacia el interior de la cavidad)
# ----------------------------------------------------------------------------
def _detail_sd_list(px, py):
    """Lista de (sdf, radio_de_la_ranura, amplitud) en coords de diseno."""
    out = []

    # ojo
    out.append((sd_circle(px, py, (-30.0, 25.4), 1.9), 1.9, 0.70))
    # ollar
    out.append((sd_circle(px, py, (-38.8, 19.6), 0.95), 0.95, 0.45))
    # hocico sonriente
    out.append((sd_polyline(px, py,
                            [(-43.6, 17.4), (-41.4, 15.6), (-38.6, 15.4), (-36.4, 16.6)],
                            0.80), 0.80, 0.55))
    # mechones de la melena
    manes = [
        [(-26.8, 31.0), (-23.6, 27.4), (-20.0, 22.4)],
        [(-24.4, 30.4), (-20.8, 25.6), (-17.2, 20.6)],
        [(-20.4, 25.2), (-16.6, 20.4), (-12.8, 15.6)],
        [(-16.0, 20.0), (-12.4, 15.6), (-8.6, 12.0)],
    ]
    for m in manes:
        out.append((sd_polyline(px, py, m, 0.78), 0.78, 0.55))

    # contorno de la montura
    out.append((sd_polyline(px, py,
                            [(-1.2, 7.0), (-1.8, 12.0), (1.0, 14.8), (6.2, 15.4),
                             (11.4, 14.6), (13.2, 11.2), (12.8, 7.2)],
                            0.80), 0.80, 0.55))
    # cincha
    out.append((sd_polyline(px, py, [(3.4, 12.4), (2.2, 2.0), (3.6, -7.4)], 0.80), 0.80, 0.55))

    # linea de cascos
    hooves = [
        [(-25.8, -22.6), (-17.4, -22.6)],
        [(-10.6, -23.4), (-3.6, -23.4)],
        [(20.6, -22.4), (28.6, -22.4)],
        [(6.6, -23.4), (13.6, -23.4)],
    ]
    for h in hooves:
        out.append((sd_polyline(px, py, h, 0.75), 0.75, 0.50))

    # franja de la base mecedora
    out.append((sd_polyline(px, py, _rocker_pts(), 0.80), 0.80, 0.50))

    return out


def detail_depth(px, py):
    """Profundidad extra de los grabados, perfil de seccion redondeada."""
    extra = np.zeros_like(px)
    for d, r, amp in _detail_sd_list(px, py):
        t = np.clip((d + r) / r, 0.0, 1.0)          # 0 en el eje, 1 en el borde
        prof = np.sqrt(np.maximum(0.0, 1.0 - t * t))
        extra = np.maximum(extra, amp * prof)
    return np.minimum(extra, DETAIL_MAX)


# ----------------------------------------------------------------------------
# Campos 2D de la placa
# ----------------------------------------------------------------------------
def fields_2d(X, Y):
    """Devuelve (sdf_silueta, z_del_fondo_de_la_cavidad, sdf_contorno_placa)."""
    d2 = horse_sd(X, Y)

    px, py = plate_to_design(X, Y)
    extra = detail_depth(px, py)

    t = np.clip(-d2 / DOME_R, 0.0, 1.0)
    dome = DOME_MAX * np.sqrt(np.maximum(0.0, 1.0 - (1.0 - t) ** 2))
    depth = np.minimum(dome + extra * np.clip(t, 0.0, 1.0), CAV_DEPTH)

    zfloor = PLATE_T - depth
    plate2d = sd_rounded_rect(X, Y, PLATE_W, PLATE_H, CORNER_R)
    return d2, zfloor, plate2d


def solid_sdf(X, Y, Z, d2=None, zfloor=None, plate2d=None):
    """SDF 3D del molde. X,Y en 2D (nx,ny); Z en 1D (nz). Devuelve (nx,ny,nz)."""
    if d2 is None:
        d2, zfloor, plate2d = fields_2d(X, Y)

    d2 = d2[:, :, None].astype(np.float32)
    zf = zfloor[:, :, None].astype(np.float32)
    pl = plate2d[:, :, None].astype(np.float32)
    z = Z[None, None, :].astype(np.float32)

    plate = np.maximum(pl, np.abs(z - PLATE_T * 0.5) - PLATE_T * 0.5)

    wall = d2 + np.float32(TAN_DRAFT) * (np.float32(PLATE_T) - z)
    floor = zf - z
    cav = op_intersect_round(wall, floor, np.float32(FILLET_R))
    cav = np.maximum(cav, z - np.float32(PLATE_T + CAV_TOP_EXT))

    return np.maximum(plate, -cav)


def solid_sdf_points(P):
    """SDF 3D para una nube de puntos arbitraria (N,3). Usado por el render."""
    X, Y, Z = P[..., 0], P[..., 1], P[..., 2]
    d2, zfloor, plate2d = fields_2d(X, Y)

    plate = np.maximum(plate2d, np.abs(Z - PLATE_T * 0.5) - PLATE_T * 0.5)
    wall = d2 + TAN_DRAFT * (PLATE_T - Z)
    cav = op_intersect_round(wall, zfloor - Z, FILLET_R)
    cav = np.maximum(cav, Z - (PLATE_T + CAV_TOP_EXT))
    return np.maximum(plate, -cav)
