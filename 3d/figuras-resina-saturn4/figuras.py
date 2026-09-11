"""
Las dos estatuillas, definidas como campo analitico.

    figura_a(X, Y, Z)  duo de alabanza  - mujer con pandero + hombre con guitarra
    figura_b(X, Y, Z)  reconocimiento   - hombre de traje frente a la placa

Marco: Z arriba, Z=0 en la cama. El personaje mira hacia -Y.
El espectador vive en -Y mirando hacia +Y, asi que ve +X a su IZQUIERDA.
En la foto la mujer esta a la izquierda del cuadro -> vive en +X.

TODAS las cotas son constantes con nombre al inicio de cada bloque. Cambiar
una y volver a correr generar.py y verificar.py es el flujo previsto.
"""

import numpy as np

import sdf as S

# --- escala general ----------------------------------------------------------
# Altura del personaje, de la planta del pie a la coronilla. La estatuilla
# completa mide esto mas el espesor de la peana.
H_PERSONA = 168.0
PEANA_T = 14.0            # espesor de la peana
K_MEZCLA = 3.2            # radio de la union suave entre miembros

# Proporciones canonicas (fraccion de H, medidas desde la planta del pie)
Z_TOBILLO, Z_RODILLA, Z_CADERA = 0.045, 0.285, 0.520
Z_CINTURA, Z_PECHO, Z_HOMBRO = 0.620, 0.730, 0.815
Z_MENTON, Z_CORONILLA = 0.868, 1.000


def _n(v):
    v = np.asarray(v, dtype=float)
    return v / (np.linalg.norm(v) + 1e-12)


def ik_codo(hombro, muneca, l1, l2, polo):
    """IK de dos huesos: dada la muneca, devuelve el codo.

    Colocar la mano y deducir el codo es mucho mas controlable que encadenar
    angulos: las poses de la foto se transcriben como coordenadas de mano.
    """
    hombro, muneca = np.asarray(hombro, float), np.asarray(muneca, float)
    v = muneca - hombro
    d = np.linalg.norm(v)
    d = float(np.clip(d, abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3))
    u = v / (np.linalg.norm(v) + 1e-12)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = np.sqrt(max(l1 * l1 - a * a, 0.0))
    polo = np.asarray(polo, float)
    perp = _n(polo - np.dot(polo, u) * u)
    return hombro + u * a + perp * h


# =============================================================================
# CUERPO
# =============================================================================
def cuerpo(X, Y, Z, cfg):
    """Un personaje completo. cfg trae origen, sexo, ropa y las dos munecas."""
    H = cfg["H"]
    z0 = cfg["z0"]                      # cota de la planta del pie
    ox, oy = cfg["origen"]
    f = cfg.get("holgura_ropa", 0.0)    # engorda torso y brazos: la ropa
    m = cfg["sexo"] == "m"

    def P(fx, fy, fz):
        return (ox + fx * H, oy + fy * H, z0 + fz * H)

    # --- anchos ---
    r_hombro = (0.113 if m else 0.099) * H
    r_pecho = ((0.104 if m else 0.094) * H, 0.066 * H, 0.095 * H)
    r_cint = ((0.083 if m else 0.077) * H, 0.058 * H, 0.070 * H)
    r_cadera = ((0.091 if m else 0.099) * H, 0.062 * H, 0.075 * H)
    r_muslo, r_pant, r_tob = 0.058 * H, 0.037 * H, 0.026 * H
    r_bsup, r_binf, r_mun = 0.037 * H, 0.029 * H, 0.021 * H
    r_cuello = 0.047 * H
    r_cabeza = (0.062 * H, 0.068 * H, 0.079 * H)

    # --- torso: tres elipsoides fundidos + los hombros ---
    c_pecho = P(0, 0, Z_PECHO)
    c_cint = P(0, 0, Z_CINTURA)
    c_cad = P(0, 0, Z_CADERA + 0.02)
    torso = S.sunion_lista([
        S.elipsoide(X, Y, Z, c_pecho, tuple(v + f for v in r_pecho)),
        S.elipsoide(X, Y, Z, c_cint, tuple(v + f for v in r_cint)),
        S.elipsoide(X, Y, Z, c_cad, tuple(v + f for v in r_cadera)),
    ], K_MEZCLA * 2.2)

    hombro_i = P(+(r_hombro - 0.022 * H) / H, 0, Z_HOMBRO)
    hombro_d = P(-(r_hombro - 0.022 * H) / H, 0, Z_HOMBRO)
    torso = S.sunion_lista([
        torso,
        S.esfera(X, Y, Z, hombro_i, 0.043 * H + f),
        S.esfera(X, Y, Z, hombro_d, 0.043 * H + f),
    ], K_MEZCLA * 1.6)

    piezas = [torso]

    # --- cuello y cabeza ---
    c_cabeza = P(0, -0.004, (Z_MENTON + Z_CORONILLA) / 2 - 0.008)
    piezas.append(S.capsula(X, Y, Z, P(0, 0.004, Z_HOMBRO - 0.005),
                            P(0, 0.0, Z_MENTON - 0.012), r_cuello))
    cabeza = S.elipsoide(X, Y, Z, c_cabeza, r_cabeza)
    # menton: un elipsoide chico al frente y abajo baja la mandibula
    cabeza = S.sunion(cabeza, S.elipsoide(
        X, Y, Z, P(0, -0.022, Z_MENTON + 0.020),
        (0.049 * H, 0.043 * H, 0.038 * H)), K_MEZCLA)
    # nariz
    cabeza = S.sunion(cabeza, S.elipsoide(
        X, Y, Z, P(0, -0.064, Z_MENTON + 0.048),
        (0.013 * H, 0.017 * H, 0.016 * H)), 1.2)
    # orejas
    for s in (+1, -1):
        cabeza = S.sunion(cabeza, S.elipsoide(
            X, Y, Z, P(s * 0.060, 0.004, Z_MENTON + 0.052),
            (0.010 * H, 0.016 * H, 0.021 * H)), 1.4)
    piezas.append(cabeza)

    # --- pelo ---
    pelo_cfg = cfg.get("pelo", "corto")
    z_ojos = z0 + (Z_MENTON + 0.055) * H
    if pelo_cfg == "largo":
        casco = S.elipsoide(X, Y, Z, c_cabeza,
                            tuple(v * 1.085 + 1.1 for v in r_cabeza))
        # melena: cae por atras hasta el omoplato
        melena = S.elipsoide(X, Y, Z, P(0, 0.028, Z_HOMBRO + 0.048),
                             (0.070 * H, 0.055 * H, 0.075 * H))
        pelo = S.sunion(casco, melena, 4.0)
        # abre la cara: quita el frente por debajo de la linea de la frente
        pelo = S.resta(pelo, S.caja(X, Y, Z, P(0, -0.075, Z_MENTON + 0.030),
                                    (0.075 * H, 0.055 * H, 0.055 * H), 3.0))
        piezas.append(pelo)
    else:
        casco = S.elipsoide(X, Y, Z, P(0, 0.006, Z_CORONILLA - 0.046),
                            (r_cabeza[0] * 1.06 + 1.0, r_cabeza[1] * 1.06 + 1.0,
                             r_cabeza[2] * 0.92))
        casco = S.interseccion(casco, S.plano_z(Z, z_ojos + 0.016 * H))
        nuca = S.elipsoide(X, Y, Z, P(0, 0.040, Z_MENTON + 0.056),
                           (0.052 * H, 0.030 * H, 0.040 * H))
        piezas.append(S.sunion(casco, nuca, 2.5))

    if cfg.get("barba"):
        barba = S.elipsoide(X, Y, Z, P(0, -0.018, Z_MENTON + 0.026),
                            (0.054 * H, 0.049 * H, 0.046 * H))
        barba = S.resta(barba, S.elipsoide(
            X, Y, Z, P(0, -0.018, Z_MENTON + 0.026),
            (0.054 * H - 1.6, 0.049 * H - 1.6, 0.046 * H - 1.6)))
        barba = S.interseccion(barba, -S.plano_z(Z, z0 + (Z_MENTON + 0.060) * H))
        piezas.append(barba)

    # --- lentes: los dos de la foto los traen ---
    if cfg.get("lentes"):
        rl, tl = 0.019 * H, 0.0055 * H       # aro y grosor del aro
        y_lente = oy - r_cabeza[1] * 0.94
        for s in (+1, -1):
            piezas.append(S.toro(X, Y, Z, (ox + s * 0.021 * H, y_lente, z_ojos),
                                 rl, tl, eje="y"))
        piezas.append(S.capsula(X, Y, Z,
                                (ox - 0.006 * H, y_lente, z_ojos),
                                (ox + 0.006 * H, y_lente, z_ojos), tl * 0.85))
        for s in (+1, -1):
            piezas.append(S.capsula(
                X, Y, Z,
                (ox + s * 0.040 * H, y_lente + 0.002 * H, z_ojos),
                (ox + s * 0.062 * H, oy + 0.026 * H, z_ojos + 0.006 * H),
                tl * 0.80))

    # --- piernas ---
    for s, lado in ((+1, "x_pos"), (-1, "x_neg")):
        cad = P(s * 0.051, 0, Z_CADERA)
        rod = P(s * 0.047, -0.004, Z_RODILLA)
        tob = P(s * 0.043, 0.004, Z_TOBILLO)
        piezas.append(S.cono_redondo(X, Y, Z, cad, r_muslo, rod, r_pant * 1.06))
        piezas.append(S.cono_redondo(X, Y, Z, rod, r_pant, tob, r_tob))
        # zapato
        za = cfg.get("zapato", "vestir")
        largo = 0.150 if za == "tenis" else 0.142
        alto = 0.048 if za == "tenis" else 0.042
        ancho = 0.062 if za == "tenis" else 0.058
        piezas.append(S.caja(
            X, Y, Z,
            (ox + s * 0.041 * H, oy - largo * H * 0.32, z0 + alto * H / 2),
            (ancho * H / 2, largo * H / 2, alto * H / 2), 0.011 * H))

    # --- brazos: la muneca viene dada, el codo sale de IK ---
    l1, l2 = 0.186 * H, 0.157 * H
    for s, key in ((+1, "muneca_x_pos"), (-1, "muneca_x_neg")):
        hom = np.array(hombro_i if s > 0 else hombro_d)
        mun = np.array(cfg[key], dtype=float)
        codo = ik_codo(hom, mun, l1, l2, (s * 0.35, 0.90, -0.25))
        piezas.append(S.cono_redondo(X, Y, Z, tuple(hom), r_bsup + f,
                                     tuple(codo), r_binf + f * 0.6))
        piezas.append(S.cono_redondo(X, Y, Z, tuple(codo), r_binf + f * 0.6,
                                     tuple(mun), r_mun))
        # mano: un elipsoide orientado segun el antebrazo, apenas mas alla
        d = _n(mun - codo)
        piezas.append(S.capsula(X, Y, Z, tuple(mun), tuple(mun + d * 0.052 * H),
                                r_mun * 1.28))

    cuerpo_d = S.sunion_lista(piezas, K_MEZCLA)

    # --- lineas de ropa: surcos poco profundos, no cambian el volumen ---
    if cfg.get("dobladillo") is not None:
        # El surco se talla sobre la PIEL del cuerpo: la cascara exterior de
        # 0.9 mm, recortada a una banda en Z y al ancho del torso para que no
        # se convierta en una pulsera cuando la mano pasa a esa altura.
        zd = z0 + cfg["dobladillo"] * H
        piel = S.cascara(cuerpo_d, 0.9)
        banda = S.caja(X, Y, Z, (ox, oy, zd), (0.125 * H, 0.30 * H, 0.9), 0.2)
        cuerpo_d = S.resta(cuerpo_d, S.interseccion(piel, banda))

    return cuerpo_d


# =============================================================================
# UTILERIA
# =============================================================================
def pandero(X, Y, Z, c, diam=26.0, canto=7.0, yaw=0.0, roll=0.0):
    """Aro con parche y seis sonajas: un pandero de 26 cm a escala 1:10.

    Marco local: el plano del aro es XY, el eje del aro es +z.
    """
    x, y, z = S.local(X, Y, Z, c, yaw=yaw, roll=roll)
    R = diam / 2.0
    aro = S.resta(S.cilindro_z(x, y, z, (0, 0), R, -canto / 2, canto / 2, 0.8),
                  S.cilindro_z(x, y, z, (0, 0), R - 2.0, -canto, canto))
    parche = S.cilindro_z(x, y, z, (0, 0), R - 1.6,
                          canto / 2 - 1.4, canto / 2 - 0.4, 0.3)
    d = S.union(aro, parche)
    for i in range(6):
        a = 2 * np.pi * i / 6 + 0.4
        d = S.union(d, S.cilindro_z(x, y, z,
                                    ((R - 1.0) * np.cos(a), (R - 1.0) * np.sin(a)),
                                    2.1, -1.1, 1.1, 0.5))
    return d


def guitarra(X, Y, Z, c, largo=100.0, yaw=0.0, pitch=0.0, roll=0.0):
    """Guitarra clasica a escala 1:10 (100 mm de largo total).

    Marco local: +z del puente al clavijero, +x el ancho de la caja,
    +y el canto. La tapa mira hacia -y.
    La boca es un agujero PASANTE a proposito: en resina es el desfogue
    natural de la cavidad de la caja.
    """
    x, y, z = S.local(X, Y, Z, c, yaw=yaw, pitch=pitch, roll=roll)
    L = largo / 100.0
    canto = 9.5 * L
    caja_inf = S.elipsoide(x, y, z, (0, 0, -30 * L),
                           (18.5 * L, canto / 2, 15.0 * L))
    caja_sup = S.elipsoide(x, y, z, (0, 0, -8.0 * L),
                           (15.0 * L, canto / 2, 12.0 * L))
    cuerpo_g = S.sunion(caja_inf, caja_sup, 7.0 * L)
    # el talle: dos cilindros con eje en +y muerden los costados
    for s in (+1, -1):
        cuerpo_g = S.sresta(cuerpo_g,
                            S.cilindro_z(x, z, y, (s * 27.0 * L, -19.0 * L),
                                         12.0 * L, -60.0, 60.0),
                            3.0 * L)
    boca = S.cilindro_z(x, z, y, (0.0, -13.0 * L), 5.2 * L, -60.0, 60.0)
    cuerpo_g = S.resta(cuerpo_g, boca)
    puente = S.caja(x, y, z, (0, -canto / 2 + 0.7, -33 * L),
                    (7.5 * L, 1.5, 2.2 * L), 0.6)
    mastil = S.caja(x, y, z, (0, -2.2 * L, 12.0 * L),
                    (4.4 * L, 2.0 * L, 26.0 * L), 1.2 * L)
    clavijero = S.caja(x, y, z, (0, -2.2 * L, 40.0 * L),
                       (5.2 * L, 1.8 * L, 6.0 * L), 1.0 * L)
    return S.union(cuerpo_g, puente, mastil, clavijero)


def peana(X, Y, Z, rx, ry, t=PEANA_T):
    """Peana ovalada de rx x ry con chaflan superior de 2 mm."""
    d = (np.sqrt((X / rx) ** 2 + (Y / ry) ** 2 + 1e-9) - 1.0) * min(rx, ry)
    chaflan = (d + (Z - (t - 2.0))) * 0.7071
    return S.interseccion(d, -Z, Z - t, chaflan)


def placa_diploma(X, Y, Z, c, W=150.0, Hh=100.0, T=9.0):
    """La placa enmarcada del reconocimiento.

    Marco, panel hundido, moldura, ornamento de esquina, banda superior,
    cinco renglones y el sello con liston. La cara util mira a -y.
    """
    x, y, z = S.local(X, Y, Z, c)
    marco_w = 9.0
    fondo = S.caja(x, y, z, (0, 0, 0), (W / 2, T / 2, Hh / 2), 2.0)
    panel = S.caja(x, y, z, (0, -T / 2, 0),
                   (W / 2 - marco_w, 2.6, Hh / 2 - marco_w), 1.5)
    d = S.resta(fondo, panel)

    # moldura del marco
    for s in (+1, -1):
        d = S.union(d, S.caja(x, y, z,
                              (s * (W / 2 - marco_w / 2), -T / 2 + 1.2, 0),
                              (marco_w / 2, 1.8, Hh / 2 - 1.0), 0.9))
        d = S.union(d, S.caja(x, y, z,
                              (0, -T / 2 + 1.2, s * (Hh / 2 - marco_w / 2)),
                              (W / 2 - 1.0, 1.8, marco_w / 2), 0.9))

    # ornamento de esquina: tres lobulos fundidos
    for sx in (+1, -1):
        for sz in (+1, -1):
            cx, cz = sx * (W / 2 - marco_w), sz * (Hh / 2 - marco_w)
            for dx, dz, r in ((0.0, 0.0, 5.2), (-sx * 7.0, 0.0, 3.4),
                              (0.0, -sz * 6.2, 3.2)):
                d = S.sunion(d, S.elipsoide(x, y, z,
                                            (cx + dx, -T / 2 + 1.0, cz + dz),
                                            (r, 2.0, r)), 1.6)

    # banda superior, perfilada (hueca por dentro como en la referencia)
    banda = S.caja(x, y, z, (0, -T / 2 + 1.4, Hh * 0.27),
                   (W * 0.24, 2.0, Hh * 0.075), 2.5)
    hueco = S.caja(x, y, z, (0, -T / 2, Hh * 0.27),
                   (W * 0.24 - 5.0, 4.0, Hh * 0.075 - 2.0), 2.0)
    d = S.union(d, S.resta(banda, hueco))

    # renglones
    for ancho, zz in ((0.62, 0.10), (0.70, 0.02), (0.70, -0.06),
                      (0.44, -0.14), (0.30, -0.22)):
        d = S.union(d, S.caja(x, y, z, (0, -T / 2 + 1.3, Hh * zz),
                              (W * ancho / 2, 1.7, 1.9), 0.8))

    # sello con liston
    sx_, sz_ = W * 0.30, -Hh * 0.20
    sello = S.elipsoide(x, y, z, (sx_, -T / 2 + 1.2, sz_), (9.0, 2.4, 9.0))
    for i in range(16):
        a = 2 * np.pi * i / 16
        sello = S.sunion(sello, S.elipsoide(
            x, y, z,
            (sx_ + 9.0 * np.cos(a), -T / 2 + 1.0, sz_ + 9.0 * np.sin(a)),
            (2.2, 1.8, 2.2)), 1.0)
    d = S.union(d, sello)
    for s in (+1, -1):
        d = S.union(d, S.caja(x, y, z, (sx_ + s * 4.0, -T / 2 + 1.0, sz_ - 12.0),
                              (2.6, 1.6, 7.0), 1.0))
    return d


def poste(X, Y, Z, cx, cy, z0, z1, r=5.0):
    """Poste de la placa: caja redondeada, no cilindro, para que agarre bien."""
    return S.caja(X, Y, Z, (cx, cy, (z0 + z1) / 2), (r, r, (z1 - z0) / 2), r * 0.5)
