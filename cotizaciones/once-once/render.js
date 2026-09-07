// Convierte cada HTML de ./out/manifest.json a PDF Letter (y PNG de revisión) con Chromium.
// Uso: NODE_PATH=/opt/node22/lib/node_modules node render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const out = path.join(__dirname, 'out');
  const files = JSON.parse(fs.readFileSync(path.join(out, 'manifest.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 816, height: 1056 } });
  for (const f of files) {
    await page.goto('file://' + f, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const base = f.replace(/\.html$/, '');
    // preferCSSPageSize respeta @page (letter + margen 11mm) de la plantilla once LAB
    await page.pdf({ path: base + '.pdf', preferCSSPageSize: true, printBackground: true });
    await page.screenshot({ path: base + '.png', fullPage: true });
    console.log('rendered', base + '.pdf');
  }
  await browser.close();
})();
