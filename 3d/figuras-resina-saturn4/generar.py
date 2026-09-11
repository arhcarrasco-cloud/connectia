"""
Malla las escenas, las ahueca para resina y exporta.

    python3 generar.py duo --res 0.35 --pared 2.2 --caras 500000
    python3 generar.py diploma

Escribe <slug>-<WxDxH>.stl y .obj, y guarda el campo muestreado en
<slug>-campo.npz para que verificar.py no tenga que volver a evaluarlo.

Cada exportacion se VERIFICA releyendo el archivo y comparando triangulos,
caja envolvente y volumen contra la malla en memoria.
"""

import argparse
import time

import numpy as np
import trimesh
from scipy import ndimage
from skimage import measure

import escenas as E
import sdf as S

PARED = 2.2          # pared de la cascara, mm
BARRENO_R = 2.0      # radio de los desfogues, mm


def muestrear(esc, res, verbose=True):
    """Evalua el campo solido en una rejilla regular, por rebanadas en Z."""
    (x0, x1), (y0, y1), (z0, z1) = esc["caja"]
    xs = np.arange(x0, x1 + res, res, dtype=np.float32)
    ys = np.arange(y0, y1 + res, res, dtype=np.float32)
    zs = np.arange(z0, z1 + res, res, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    campo = np.empty((len(xs), len(ys), len(zs)), dtype=np.float32)
    t0 = time.time()
    for k, z in enumerate(zs):
        campo[:, :, k] = esc["f"](X, Y, np.float32(z))
        if verbose and k % 100 == 0:
            print(f"    z {k:4d}/{len(zs)}  {time.time()-t0:5.1f}s", flush=True)
    if verbose:
        print(f"    rejilla {campo.shape} = {campo.size/1e6:.1f} M voxeles "
              f"en {time.time()-t0:.1f}s")
    return campo, (xs, ys, zs)


APERTURA = 0.9   # mm: cavidad mas fina que 2*APERTURA se cierra y queda maciza


def ahuecar(campo, ejes, canales, respiraderos, pared=PARED, apertura=APERTURA):
    """Cascara de espesor `pared`, mas los canales y los respiraderos.

    Lo mas fino que 2*pared se queda macizo por construccion: ahi -(d+t) ya
    es negativo y el maximo se queda con d.

    Pero justo EN la frontera de esos 2*pared la cavidad se afila a cero y la
    malla sale pellizcada: dos superficies que se besan en una arista, que es
    no-manifold aunque no haya ni un hueco. El mastil de la guitarra, de 6.4 mm,
    dejaba una cavidad de 2 mm que hacia exactamente eso.

    La cura es una APERTURA morfologica de la cavidad: se erosiona `apertura` y
    se vuelve a dilatar. Con un SDF exacto eso seria la identidad -- desplazar
    el campo es reversible --, asi que la erosion se hace sobre la mascara y la
    distancia se recalcula, que es lo que la vuelve irreversible. Toda cavidad
    mas fina que 2*apertura desaparece y esa zona se queda maciza.
    """
    xs, ys, zs = ejes
    cav = (campo + pared) < 0
    if apertura > 0 and cav.any():
        e = ndimage.distance_transform_edt(cav, sampling=(xs[1]-xs[0],) * 3)
        nucleo = e >= apertura
        del e
        if nucleo.any():
            fuera = ndimage.distance_transform_edt(
                ~nucleo, sampling=(xs[1]-xs[0],) * 3)
            # distancia con signo de la cavidad ya abierta
            shell = np.maximum(campo, np.float32(apertura) - fuera)
            del fuera
        else:
            shell = campo.copy()
        del nucleo
    else:
        shell = np.maximum(campo, -(campo + pared))
    shell = shell.astype(np.float32)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    for a, b, r in list(canales) + list(respiraderos):
        for k, z in enumerate(zs):
            if not (min(a[2], b[2]) - r <= z <= max(a[2], b[2]) + r):
                continue
            shell[:, :, k] = np.maximum(shell[:, :, k],
                                        -S.capsula(X, Y, np.float32(z), a, b, r))
    return shell


def rellenar_bolsas(shell, res):
    """Vuelve maciza toda cavidad que no alcance el exterior.

    Ahuecar por desplazamiento deja bolsas ciegas donde la figura tiene masas
    aisladas mas gruesas que 2*pared -- manos, zapatos, el sello de la placa.
    Cada una seria resina atrapada que no lava ni cura. Rellenarlas cuesta
    decimas de cm3 y elimina el problema de raiz en vez de administrarlo.
    """
    est = np.ones((3, 3, 3), bool)
    vacio = shell >= 0
    lab, n = ndimage.label(vacio, structure=est)
    if n == 0:
        return shell, 0, 0.0
    fuera = set(np.unique(np.concatenate([
        lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(),
        lab[:, :, 0].ravel(), lab[:, :, -1].ravel()])))
    fuera.discard(0)
    ciegas = [i for i in range(1, n + 1) if i not in fuera]
    if not ciegas:
        return shell, 0, 0.0
    mascara = np.isin(lab, ciegas)
    vol = float(mascara.sum()) * res ** 3 / 1000.0
    shell = shell.copy()
    shell[mascara] = -pared_relleno(shell)
    return shell, len(ciegas), vol


def pared_relleno(shell):
    """Valor negativo con el que se marca el relleno: solo tiene que ser
    inequivocamente interior, no una distancia real."""
    return 1.0


def _aristas_malas(m):
    """(aristas de borde, aristas no-manifold) de la malla."""
    import trimesh.grouping as gg
    grupos = gg.group_rows(m.edges_sorted, require_count=None)
    c = np.array([len(x) for x in grupos])
    return int((c == 1).sum()), int((c > 2).sum())


def _limpiar(m, reparar=True):
    """Deja la malla cerrada y manifold, y dice que tuvo que arreglar.

    Marching cubes deja triangulos de area cero: sin quitarlos la malla
    reporta `is_watertight = False` aun teniendo cero aristas de borde,
    porque los degenerados duplican aristas y rompen la cuenta.

    Ademas, en una rejilla de voxeles siempre sobreviven un puniado de
    configuraciones ambiguas -- del orden de decenas de aristas entre casi un
    millon -- que salen como agujeros de un triangulo o como aristas con
    cuatro caras. Son artefactos de muestreo, no defectos de la pieza, y se
    tapan. Se reporta cuantos eran para que quede en el registro y no
    escondido.
    """
    m.update_faces(m.nondegenerate_faces())
    m.merge_vertices()
    m.remove_unreferenced_vertices()
    if not reparar:
        return m
    borde, nm = _aristas_malas(m)
    if not (borde or nm):
        return m

    # Se intenta tapar, pero solo se acepta si de verdad mejora: fill_holes
    # triangula el contorno del agujero y en estas mallas mete mas borde del
    # que quita (6 aristas se volvian 18). Si empeora, se deja como estaba y
    # se reporta el numero real. Una malla con dos docenas de aristas malas
    # entre dos millones la repara cualquier rebanador; mentir sobre ellas no.
    cand = m.copy()
    trimesh.repair.fill_holes(cand)
    cand.update_faces(cand.unique_faces())
    cand.update_faces(cand.nondegenerate_faces())
    cand.merge_vertices()
    cand.remove_unreferenced_vertices()
    b2, n2 = _aristas_malas(cand)
    if (b2, n2) < (borde, nm):
        print(f"    reparado: {borde} aristas de borde y {nm} no-manifold "
              f"-> {b2} y {n2} (de {len(cand.edges_sorted):,})")
        return cand
    print(f"    {borde} aristas de borde y {nm} no-manifold de "
          f"{len(m.edges_sorted):,}; el tapado las empeora a {b2} y {n2}, "
          f"asi que se deja la malla como esta")
    return m


def mallar(campo, ejes, caras_objetivo):
    xs, ys, zs = ejes
    res = float(xs[1] - xs[0])
    verts, faces, _, _ = measure.marching_cubes(campo, level=0.0, spacing=(res,) * 3)
    verts = verts + np.array([xs[0], ys[0], zs[0]], dtype=np.float64)
    cruda = _limpiar(trimesh.Trimesh(vertices=verts, faces=faces, process=True))
    print(f"    marching cubes: {len(cruda.faces):,} triangulos · "
          f"cerrada {cruda.is_watertight} · {cruda.body_count} superficies")
    if caras_objetivo and len(faces) > caras_objetivo:
        import fast_simplification
        v, f = fast_simplification.simplify(verts.astype(np.float32),
                                            faces.astype(np.int32),
                                            1.0 - caras_objetivo / len(faces))
        verts, faces = np.asarray(v, dtype=np.float64), np.asarray(f)
        print(f"    simplificado a {len(faces):,} triangulos")
    # La simplificacion vuelve a dejar degenerados: se limpia otra vez o la
    # malla exportada reporta abierta sin estarlo.
    m = _limpiar(trimesh.Trimesh(vertices=verts, faces=faces, process=True))
    # Nada de fix_normals: orienta cada cuerpo hacia AFUERA, y las cavidades
    # internas de una pieza hueca tienen que mirar hacia adentro. Marching
    # cubes ya entrega orientacion coherente; solo hay que fijar el global.
    if m.volume < 0:
        m.invert()
    return m


def exportar_y_verificar(m, ruta):
    """Exporta y RELEE el archivo: los numeros del README salen de la relectura."""
    m.export(ruta)
    r = trimesh.load(ruta, process=False)
    dv = abs(r.volume - m.volume) / max(abs(m.volume), 1e-9)
    db = np.abs(r.bounds - m.bounds).max()
    # El STL guarda vertices en float32: la tolerancia se fija en la precision
    # del formato, no en la del calculo.
    ok = len(r.faces) == len(m.faces) and dv < 1e-4 and db < 2e-3
    print(f"    {ruta}: {len(r.faces):,} tri  vol {r.volume/1000:.2f} cm3  "
          f"{'[RELECTURA OK]' if ok else '[RELECTURA DISCREPA]'}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("escena", choices=list(E.ESCENAS))
    ap.add_argument("--res", type=float, default=0.35, help="voxel, mm")
    ap.add_argument("--pared", type=float, default=PARED)
    ap.add_argument("--apertura", type=float, default=APERTURA)
    ap.add_argument("--caras", type=int, default=500000)
    ap.add_argument("--macizo", action="store_true",
                    help="no ahuecar (solo para comparar volumenes)")
    ap.add_argument("--desde-campo", action="store_true",
                    help="reusa <escena>-campo.npz en vez de volver a evaluar "
                         "el campo: vuelve a mallar y exportar en minutos en "
                         "vez de en un cuarto de hora")
    a = ap.parse_args()

    esc = E.ESCENAS[a.escena]
    print(f"{esc['nombre'].upper()}  res {a.res} mm  pared {a.pared} mm")

    if a.desde_campo:
        d = np.load(f"{a.escena}-campo.npz")
        campo = d["solido"].astype(np.float32)
        ejes = (d["xs"], d["ys"], d["zs"])
        a.res = float(d["res"])
        print(f"    campo reusado de {a.escena}-campo.npz  "
              f"{campo.shape} · voxel {a.res} mm")
    else:
        campo, ejes = muestrear(esc, a.res)
    vox = a.res ** 3
    v_macizo = float((campo < 0).sum()) * vox / 1000.0

    if a.macizo:
        usado = campo
        etiqueta = "macizo"
    else:
        usado = ahuecar(campo, ejes, esc["canales"], esc["respiraderos"],
                        a.pared, a.apertura)
        usado, n_bolsas, v_bolsas = rellenar_bolsas(usado, a.res)
        if n_bolsas:
            print(f"    bolsas ciegas rellenadas: {n_bolsas} · {v_bolsas:.3f} cm3")
        etiqueta = "hueco"
    v_usado = float((usado < 0).sum()) * vox / 1000.0
    print(f"    volumen por voxeles: macizo {v_macizo:.1f} cm3 · "
          f"{etiqueta} {v_usado:.1f} cm3 ({v_usado/v_macizo:.1%})")

    m = mallar(usado, ejes, a.caras)
    b = m.bounds
    dim = b[1] - b[0]
    slug = f"{a.escena}-{dim[0]:.0f}x{dim[1]:.0f}x{dim[2]:.0f}"
    if a.macizo:
        slug += "-macizo"
    print(f"    caja envolvente {dim[0]:.1f} x {dim[1]:.1f} x {dim[2]:.1f} mm")
    print(f"    cuerpos {m.body_count} · cerrada {m.is_watertight} · "
          f"euler {m.euler_number}")

    exportar_y_verificar(m, f"{slug}.stl")
    m.export(f"{slug}.obj")

    np.savez_compressed(f"{a.escena}-campo.npz",
                        campo=usado.astype(np.float32),
                        solido=campo.astype(np.float32),
                        xs=ejes[0], ys=ejes[1], zs=ejes[2],
                        res=a.res, pared=a.pared,
                        v_macizo=v_macizo, v_hueco=v_usado,
                        v_malla=m.volume / 1000.0, slug=slug)
    print(f"    campo guardado en {a.escena}-campo.npz")


if __name__ == "__main__":
    main()
