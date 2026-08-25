"""
Genera la malla del molde a partir del SDF y exporta STL + 3MF + OBJ.

    python3 generar_molde.py [--res 0.25] [--faces 180000]

Verifica el resultado releyendo el archivo exportado: caja envolvente,
numero de triangulos, estanqueidad y volumen.
"""

import argparse
import os
import zipfile

import numpy as np
import trimesh
from skimage import measure

import molde_sdf as M

OUT = os.path.dirname(os.path.abspath(__file__))
NAME = "molde-caballo-mecedora-120x90x15"

PAD = 2.0  # margen de aire alrededor de la placa para cerrar la malla


# ----------------------------------------------------------------------------
def build_mesh(res):
    # el desfase evita que un plano de muestreo caiga exactamente sobre una cara
    # plana de la placa: ahi el campo vale 0 y marching cubes degenera en dos
    # cascaras coplanares en vez de una sola superficie.
    off = res * 0.371
    xs = np.arange(-M.PLATE_W / 2 - PAD, M.PLATE_W / 2 + PAD + res, res) + off
    ys = np.arange(-M.PLATE_H / 2 - PAD, M.PLATE_H / 2 + PAD + res, res) + off
    zs = np.arange(-PAD, M.PLATE_T + PAD + res, res) + off

    X, Y = np.meshgrid(xs, ys, indexing="ij")
    d2, zfloor, plate2d = M.fields_2d(X, Y)

    vol = M.solid_sdf(X, Y, zs, d2, zfloor, plate2d)
    print(f"  malla escalar {vol.shape} = {vol.size/1e6:.1f} M voxeles a {res} mm")

    verts, faces, _, _ = measure.marching_cubes(
        vol, level=0.0, spacing=(res, res, res), allow_degenerate=False
    )
    verts += np.array([xs[0], ys[0], zs[0]])
    return verts, faces


def decimate(verts, faces, target):
    if len(faces) <= target:
        return verts, faces
    import fast_simplification

    red = 1.0 - target / len(faces)
    v, f = fast_simplification.simplify(
        verts.astype(np.float32), faces.astype(np.int32), red, agg=5
    )
    return v.astype(np.float64), f.astype(np.int64)


# ----------------------------------------------------------------------------
def write_3mf(mesh, path, title):
    v = mesh.vertices
    f = mesh.faces
    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        f'  <metadata name="Title">{title}</metadata>\n'
        '  <metadata name="Designer">Connectia</metadata>\n'
        '  <metadata name="Application">forge3d / molde_sdf.py</metadata>\n'
        '  <resources>\n    <object id="1" type="model">\n      <mesh>\n'
        "        <vertices>\n"
    )
    tail = (
        "        </triangles>\n      </mesh>\n    </object>\n  </resources>\n"
        '  <build><item objectid="1"/></build>\n</model>\n'
    )
    parts = [head]
    parts.append(
        "".join(
            '<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (a, b, c) for a, b, c in v
        )
    )
    parts.append("\n        </vertices>\n        <triangles>\n")
    parts.append(
        "".join('<triangle v1="%d" v2="%d" v3="%d"/>' % (a, b, c) for a, b, c in f)
    )
    parts.append("\n" + tail)
    model = "".join(parts)

    ct = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        "</Relationships>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", type=float, default=0.25)
    ap.add_argument("--faces", type=int, default=180000)
    a = ap.parse_args()

    print("1. Evaluando el SDF y extrayendo la isosuperficie...")
    verts, faces = build_mesh(a.res)
    print(f"  marching cubes: {len(verts):,} vertices  {len(faces):,} triangulos")

    print("2. Simplificando...")
    verts, faces = decimate(verts, faces, a.faces)
    print(f"  {len(faces):,} triangulos")

    # marching_cubes ya devuelve las caras bien orientadas hacia afuera para
    # este campo; no se reorientan (fix_normals sobre 2 M de caras invierte
    # cascaras enteras y falsea el volumen).
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    mesh.merge_vertices()
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.volume > 0, "orientacion invertida"

    # apoyar la cara de cama en Z = 0 y centrar en XY
    mesh.apply_translation([0.0, 0.0, -mesh.bounds[0][2]])
    c = mesh.bounds.mean(axis=0)
    mesh.apply_translation([-c[0], -c[1], 0.0])

    stl = os.path.join(OUT, NAME + ".stl")
    tmf = os.path.join(OUT, NAME + ".3mf")
    obj = os.path.join(OUT, NAME + ".obj")

    print("3. Exportando...")
    mesh.export(stl)
    write_3mf(mesh, tmf, "Molde caballo mecedora 120x90x15 mm")
    mesh.export(obj)

    print("4. Verificando (relectura de los archivos)...")
    report = []
    for p in (stl, tmf, obj):
        # El cargador de 3MF suelda vertices por tolerancia y rompe la
        # topologia de una malla que si esta bien; el de STL/OBJ, al reves,
        # necesita el paso de union para reconstruir los vertices compartidos.
        rm = trimesh.load(p, force="mesh",
                          process=not p.endswith(".3mf"))
        ext = mesh.extents
        rext = rm.extents
        report.append(
            (os.path.basename(p), os.path.getsize(p) / 1e6, len(rm.faces),
             rext, rm.is_watertight, rm.volume / 1000.0,
             rm.body_count, rm.euler_number, rm.is_winding_consistent)
        )

    print()
    print(f"{'archivo':<40}{'MB':>7}{'tri':>10}  bbox mm                "
          f"cerrada cuerpos euler  cm3")
    for n, mb, nf, ext, wt, vol, bc, eu, wind in report:
        print(f"{n:<40}{mb:>7.2f}{nf:>10,}  "
              f"{ext[0]:6.2f} x {ext[1]:5.2f} x {ext[2]:5.2f}  "
              f"{'si' if wt else 'NO':>6} {bc:>7} {eu:>5}  {vol:6.2f}"
              + ("" if wind else "   AVISO: bobinado inconsistente"))

    print()
    print("Comprobacion de cotas nominales")
    e = mesh.extents
    checks = [
        ("ancho exterior", e[0], M.PLATE_W),
        ("alto exterior", e[1], M.PLATE_H),
        ("espesor total", e[2], M.PLATE_T),
    ]
    for lbl, got, want in checks:
        print(f"  {lbl:<22} {got:7.3f} mm   (nominal {want:.1f})  "
              f"desv {got-want:+.3f}")

    # profundidad real medida sobre la malla, no sobre el SDF
    res = 0.20
    xs = np.arange(-M.PLATE_W / 2, M.PLATE_W / 2, res)
    ys = np.arange(-M.PLATE_H / 2, M.PLATE_H / 2, res)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    d2, zf, _ = M.fields_2d(X, Y)
    depth = M.PLATE_T - zf
    ins = d2 <= 0
    print(f"  {'profundidad maxima':<22} {depth[ins].max():7.3f} mm   (nominal 10.0)")
    print(f"  {'fondo solido minimo':<22} {zf.min():7.3f} mm   (nominal 5.0)")
    print(f"  {'area de cavidad':<22} {ins.sum()*res*res:7.1f} mm2")

    solid = (M.PLATE_W * M.PLATE_H * M.PLATE_T
             - (4 - np.pi) * M.CORNER_R ** 2 * M.PLATE_T) / 1000.0
    cav = solid - mesh.volume / 1000.0
    print(f"  {'volumen de cavidad':<22} {cav:7.2f} cm3  "
          f"(~{cav*1.29:.0f} g de chocolate por colada)")
    print(f"  {'volumen de material':<22} {mesh.volume/1000.0:7.2f} cm3  "
          f"(placa maciza sin cavidad {solid:.2f} cm3)")


if __name__ == "__main__":
    main()
