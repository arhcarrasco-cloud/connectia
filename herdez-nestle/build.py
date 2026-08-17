#!/usr/bin/env python3
"""Compila deck.src.html -> index.html (logo embebido) y exporta el PDF.

    python3 herdez-nestle/build.py

Se corre desde la raiz del repo. El PDF necesita playwright + chromium.
"""
import base64
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
PDF = ROOT / "Connectia_Herdez_Nestle_Helados.pdf"

logo = base64.b64encode((REPO / "assets/logo/connectia-white.png").read_bytes()).decode()
html = (ROOT / "deck.src.html").read_text().replace(
    "__LOGO_WHITE__", "data:image/png;base64," + logo
)
(ROOT / "index.html").write_text(html)
print("index.html ->", len(html), "bytes")

script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch();
  const p = await b.newPage({{ viewport: {{ width: 1640, height: 1000 }} }});
  await p.goto('file://{ROOT / "index.html"}');
  await p.waitForTimeout(2500);
  await p.pdf({{ path: '{PDF}', width: '1600px', height: '900px', printBackground: true }});
  await b.close();
}})();
"""
# Hereda el entorno para que playwright encuentre su chromium. Si node no
# resuelve playwright por si solo, se le apunta a un global conocido.
env = dict(os.environ)
for candidate in ("/opt/node22/lib/node_modules", "/usr/local/lib/node_modules"):
    if pathlib.Path(candidate, "playwright").is_dir():
        env["NODE_PATH"] = os.pathsep.join(
            filter(None, [env.get("NODE_PATH"), candidate])
        )
        break

try:
    subprocess.run(["node", "-e", script], check=True, env=env)
    print("PDF ->", PDF.name)
except (subprocess.CalledProcessError, FileNotFoundError) as exc:
    print(f"PDF omitido: {exc}", file=sys.stderr)
    print(
        "El HTML si quedo. Para el PDF: npm i -D playwright && npx playwright install chromium,\n"
        "o abre index.html en el navegador e imprime a PDF (1600 x 900, sin margen).",
        file=sys.stderr,
    )
