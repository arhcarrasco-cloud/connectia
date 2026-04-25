/* Connectia Service Worker
   Estrategia: shell HTML cacheado con Network-First; el resto (Google Maps tiles,
   APIs INEGI, AI Search, etc.) NO se intercepta — pasa directo a la red.
   Razón: que la app abra en frío sin red, pero los datos siempre frescos. */
const CACHE = 'connectia-shell-v1';
const SHELL = ['./', './manifest.json', './apple-touch-icon.png',
               './icon-192.png', './icon-512.png'];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL).catch(()=>{}))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // Solo GETs: nunca interceptar POST/PUT (APIs)
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Solo manejar requests al MISMO origen (no Google Maps, no INEGI, no Anthropic, etc.)
  if (url.origin !== self.location.origin) return;

  // Solo navegaciones (request al HTML) o assets del shell
  const isNavigate = req.mode === 'navigate' ||
                     (req.headers.get('accept') || '').includes('text/html');
  const isShellAsset = SHELL.some((p) => url.pathname.endsWith(p.replace('./','')));

  if (!isNavigate && !isShellAsset) return;

  // Network-first con fallback a caché
  event.respondWith(
    fetch(req).then((res) => {
      // Solo cachear respuestas OK
      if (res && res.status === 200 && res.type === 'basic') {
        const clone = res.clone();
        caches.open(CACHE).then((c) => c.put(req, clone)).catch(()=>{});
      }
      return res;
    }).catch(() => caches.match(req).then((r) => r || caches.match('./')))
  );
});

/* Mensaje desde la página: skipWaiting bajo demanda (para forzar update). */
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
});
