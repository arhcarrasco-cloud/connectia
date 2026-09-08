#!/usr/bin/env python3
"""Mide el casco "Full size football helmet" (Kish82, MakerWorld · perfil P1S)
directamente de la malla del 3MF de Bambu Studio y genera la lámina de medidas
con el logo KAVAK colocado a escala en el lateral.

Uso:
    python3 medir_casco.py Casco.3mf "Logo Kavak .png" salida.png

Requiere: numpy, scipy, pillow, matplotlib.
El 3MF vive en Drive (Mi unidad → Casco.3mf, 29-ago-2026); no se versiona aquí
porque el modelo es de terceros (licencia BY-NC).
"""
import re
import sys
import zipfile

import numpy as np
from PIL import Image
from scipy import ndimage

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

SHELL_ID, MASK_ID = "20", "24"  # Football_Helmet.STL_10 (casco) / STL_12 (máscara)
EAR = (14.0, 85.0)  # centro del oído en el marco natural (mm)
EAR_R = 20.0
LOGO_W, LOGO_H = 120.0, 31.0  # KAVAK wordmark, proporción 3.87:1
LOGO_Y0, LOGO_Z0 = -80.0, 110.0


def load_part(z, oid, asm):
    rels = z.read("3D/3dmodel.model").decode()
    comp = dict(re.findall(r'<object id="(\d+)".*?p:path="(/3D/Objects/object_\d+\.model)"', rels, re.S))
    txt = z.read(comp[oid][1:]).decode()
    v = np.array(re.findall(r'<vertex x="([-\d.eE+]+)" y="([-\d.eE+]+)" z="([-\d.eE+]+)"', txt), dtype=float)
    f = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', txt), dtype=int)
    t = np.array(asm[oid].split(), dtype=float)
    return v @ t[:9].reshape(3, 3).T + t[9:], f


def natural_frame(shell, mask):
    """Gira en el plano YZ hasta la pose de apoyo (máscara + borde trasero) y pone el suelo en z=0."""
    c = shell.mean(0)
    shell, mask = shell - c, mask - c
    best = None
    for deg in np.arange(-180, 180, 0.5):
        a = np.radians(deg)
        up = np.array([0, np.cos(a), np.sin(a)])
        fwd = np.array([0, -np.sin(a), np.cos(a)])
        pts = np.vstack([shell, mask])
        h = pts @ up
        sel = pts[h < h.min() + 1.5]
        spread = np.ptp(sel @ fwd) if len(sel) else 0
        if best is None or spread > best[0]:
            best = (spread, deg)
    a = np.radians(best[1])
    R = np.vstack([[1, 0, 0], [0, -np.sin(a), np.cos(a)], [0, np.cos(a), np.sin(a)]])
    shell, mask = shell @ R.T, mask @ R.T
    if mask[:, 1].mean() < shell[:, 1].mean():  # la máscara define el frente
        shell[:, 1] *= -1
        mask[:, 1] *= -1
    z0 = min(shell[:, 2].min(), mask[:, 2].min())
    shell[:, 2] -= z0
    mask[:, 2] -= z0
    return shell, mask


def main(path_3mf, path_logo, path_out):
    z = zipfile.ZipFile(path_3mf)
    ms = z.read("Metadata/model_settings.config").decode()
    asm = dict(re.findall(r'<assemble_item object_id="(\d+)" instance_id="0" transform="([^"]+)"', ms))
    shell, f = load_part(z, SHELL_ID, asm)
    mask, _ = load_part(z, MASK_ID, asm)
    shell, mask = natural_frame(shell, mask)

    L, W, H = np.ptp(shell[:, 1]), np.ptp(shell[:, 0]), np.ptp(shell[:, 2])
    L_total = np.ptp(np.vstack([shell, mask])[:, 1])
    print(f"Casco: largo {L/10:.1f} cm · ancho {W/10:.1f} cm · alto {H/10:.1f} cm · con máscara {L_total/10:.1f} cm")

    # mapa de altura del lateral derecho -> inclinación respecto a la vista lateral
    g = 2.0
    ys, zs = np.arange(-140, 130, g), np.arange(0, 260, g)
    Hm = np.full((len(zs), len(ys)), np.nan)
    r = shell[:, 0] > 0
    iy = ((shell[r, 1] - ys[0]) / g).astype(int)
    iz = ((shell[r, 2] - zs[0]) / g).astype(int)
    ok = (iy >= 0) & (iy < len(ys)) & (iz >= 0) & (iz < len(zs))
    for a, b, c in zip(iz[ok], iy[ok], shell[r, 0][ok]):
        if np.isnan(Hm[a, b]) or c > Hm[a, b]:
            Hm[a, b] = c
    idx = ndimage.distance_transform_edt(np.isnan(Hm), return_distances=False, return_indices=True)
    Hs = ndimage.gaussian_filter(Hm[tuple(idx)], 3)
    gz, gy = np.gradient(Hs, g)
    tilt = np.degrees(np.arctan(np.hypot(gy, gz)))
    zm = int((LOGO_Z0 + LOGO_H / 2 - zs[0]) / g)
    cols = np.arange(int((LOGO_Y0 - ys[0]) / g), int((LOGO_Y0 + LOGO_W - ys[0]) / g) + 1)
    arc = np.sum(np.hypot(np.diff(ys[cols]), np.diff(Hs[zm, cols])))
    print(f"Logo {LOGO_W/10:.1f}×{LOGO_H/10:.1f} cm · inclinación: atrás {tilt[zm, cols[0]]:.0f}°, centro "
          f"{tilt[zm, cols[len(cols)//2]]:.0f}°, frente {tilt[zm, cols[-1]]:.0f}° · arco sobre superficie {arc/10:.1f} cm")

    # render lateral con pintor
    tri = shell[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nn = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    sel = nn[:, 0] > 0
    T, sh = tri[sel], nn[sel]
    order = np.argsort(T[:, :, 0].mean(1))
    T, sh = T[order], sh[order]
    light = np.array([0.6, 0.3, 0.75]) / np.linalg.norm([0.6, 0.3, 0.75])
    col = 0.25 + 0.75 * np.clip(sh @ light, 0, 1)
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.add_collection(PolyCollection(T[:, :, 1:], facecolors=np.clip(np.array([0.0, 0.35, 0.9]) * col[:, None] * 1.15 + 0.05, 0, 1), edgecolors="none"))
    ax.scatter(mask[:, 1], mask[:, 2], s=0.6, c="0.75", alpha=0.5)

    im = np.array(Image.open(path_logo).convert("RGBA"))
    blk = (im[:, :, :3].sum(2) < 150) & (np.arange(im.shape[0])[:, None] > im.shape[0] // 2)  # versión negra (mitad inferior)
    yy, xs = np.where(blk)
    crop = np.zeros((yy.max() - yy.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    crop[..., :3] = 255
    crop[..., 3] = blk[yy.min():yy.max() + 1, xs.min():xs.max() + 1] * 255
    y0, y1, z0, z1 = LOGO_Y0, LOGO_Y0 + LOGO_W, LOGO_Z0, LOGO_Z0 + LOGO_H
    ax.imshow(crop, extent=(y0, y1, z0, z1), zorder=5)
    ax.add_patch(Rectangle((y0, z0), LOGO_W, LOGO_H, fill=False, ec="#FFD400", lw=1.5, ls="--", zorder=6))
    ax.add_patch(Circle(EAR, EAR_R, fill=False, ec="#FFD400", lw=1.2, zorder=6))

    def dim(p, q, txt, off=(0, 0), color="k"):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", color=color, lw=1.2), zorder=7)
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], txt, ha="center", va="center",
                fontsize=10, color=color, bbox=dict(fc="white", ec="none", alpha=0.85), zorder=8)

    ex, ez = EAR
    dim((y0, z1 + 12), (y1, z1 + 12), f"logo {LOGO_W/10:.1f} cm", (0, 7), "#b30000")
    dim((y1 + 10, z0), (y1 + 10, z1), f"{LOGO_H/10:.1f} cm", (16, 0), "#b30000")
    dim((ex + EAR_R + 6, ez - EAR_R), (ex + EAR_R + 6, ez + EAR_R), f"Ø {2*EAR_R/10:.1f} cm", (22, 0))
    dim((ex + EAR_R + 6, 0), (ex + EAR_R + 6, ez - EAR_R), f"{(ez-EAR_R)/10:.1f} cm\nsuelo → borde\ninferior oído", (28, 0))
    dim((ex + EAR_R + 6, ez + EAR_R), (ex + EAR_R + 6, z0), f"{(z0-ez-EAR_R)/10:.1f} cm", (18, 0))
    ax.plot([y0, y0], [z0, 58], color="k", lw=0.8, ls=":")
    ax.plot([ex, ex], [ez, 58], color="k", lw=0.8, ls=":")
    dim((y0, 60), (ex, 60), f"{(ex-y0)/10:.1f} cm (borde trasero del logo → centro del oído)", (-40, -9))
    dim((shell[:, 1].min(), -4), (shell[:, 1].max(), -4), f"largo casco {L/10:.1f} cm (con máscara ≈ {L_total/10:.1f})", (0, -8))
    dim((shell[:, 1].max() + 22, 0), (shell[:, 1].max() + 22, shell[:, 2].max()), f"alto {H/10:.1f} cm", (-16, 0))
    ax.set_xlim(-160, 240)
    ax.set_ylim(-25, 275)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f'Casco "Full size football helmet" (Kish82, MakerWorld) · perfil P1S · lateral derecho · medidas reales del 3MF\n'
                 f"Ancho del casco {W/10:.1f} cm · Logo KAVAK propuesto {LOGO_W/10:.1f} × {LOGO_H/10:.1f} cm (mismo tamaño en el lado izquierdo, espejo)", fontsize=11)
    plt.savefig(path_out, dpi=110, bbox_inches="tight", facecolor="white")
    print("guardado", path_out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
