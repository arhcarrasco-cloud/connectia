#!/usr/bin/env python3
"""
Captura la preview de cada app y la deja en hub/previews/<id>.jpg.

    python3 _hub/previews.py            solo las que faltan
    python3 _hub/previews.py --todas    vuelve a capturar todas

Captura desde el ARCHIVO LOCAL, no desde la URL: en esta Mac Chrome headless
no tiene salida a red, pero renderiza file:// perfecto. Cada app usa, en orden:
  1. el campo 'preview_local' del catálogo, si existe
  2. <repo>/<ruta>/index.html, si la app vive en el repo
Las que no tienen archivo local se omiten y simplemente no salen en el reel.
"""
import json, pathlib, subprocess, sys, tempfile, shutil, os, signal

ROOT   = pathlib.Path(__file__).resolve().parent.parent
CAT    = json.loads((ROOT / "_hub" / "catalogo.json").read_text(encoding="utf-8"))
DEST   = ROOT / "hub" / "previews"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

ANCHO, ALTO, SALIDA, LIMITE = 1440, 900, 1040, 45
TODAS = "--todas" in sys.argv

DEST.mkdir(parents=True, exist_ok=True)
if not pathlib.Path(CHROME).exists():
    sys.exit("No encuentro Google Chrome.")

def origen(app):
    if app.get("preview_local"):
        p = pathlib.Path(os.path.expanduser(app["preview_local"]))
        if p.exists():
            return p
    if app.get("ruta"):
        p = ROOT / app["ruta"] / "index.html"
        if p.exists():
            return p
    return None

def capturar(url, destino):
    perfil = tempfile.mkdtemp(prefix="hubshot-")
    try:
        p = subprocess.Popen(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--no-first-run", "--disable-extensions",
             f"--user-data-dir={perfil}",
             "--virtual-time-budget=6000",
             f"--window-size={ANCHO},{ALTO}",
             f"--screenshot={destino}", url],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True)
        try:
            p.wait(timeout=LIMITE)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL); p.wait()
    finally:
        shutil.rmtree(perfil, ignore_errors=True)
    return destino.exists()

ok = fallo = saltadas = sin_fuente = 0

for app in CAT["apps"]:
    jpg = DEST / f"{app['id']}.jpg"
    if jpg.exists() and not TODAS:
        saltadas += 1
        continue

    src = origen(app)
    if src is None:
        print(f"  sin archivo local  {app['nombre']}", flush=True)
        sin_fuente += 1
        continue

    tmp = pathlib.Path(tempfile.mkdtemp())
    png = tmp / "shot.png"
    hubo = capturar(src.resolve().as_uri(), png)
    if hubo:
        subprocess.run(["sips", "-Z", str(SALIDA), "-s", "format", "jpeg",
                        "-s", "formatOptions", "72", str(png), "--out", str(jpg)],
                       capture_output=True)
    shutil.rmtree(tmp, ignore_errors=True)

    if jpg.exists():
        print(f"  ok      {app['nombre']}  ({jpg.stat().st_size // 1024} KB)", flush=True)
        ok += 1
    else:
        print(f"  FALLÓ   {app['nombre']}", flush=True)
        fallo += 1

print(f"\npreviews: {ok} nuevas · {saltadas} ya estaban · {sin_fuente} sin archivo local · {fallo} fallidas")
