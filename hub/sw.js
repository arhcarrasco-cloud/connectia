/* App Hub — service worker
   HTML: red primero, caché como red de seguridad si estás sin señal.
   Íconos y previews: caché primero, porque su URL lleva ?v=<build> y
   cambia sola en cada publicación. Así el hub abre al instante y offline,
   pero nunca se queda con una versión vieja. */

const CACHE = "hub-v1";
const BASE  = new URL("./", self.location).pathname;

self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll([BASE, BASE + "manifest.json"]).catch(() => {}))
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  const esImagen = /\.(png|jpg|jpeg|svg|webp)$/i.test(url.pathname);

  if (esImagen) {
    e.respondWith(
      caches.match(req).then(hit =>
        hit || fetch(req).then(res => {
          const copia = res.clone();
          caches.open(CACHE).then(c => c.put(req, copia));
          return res;
        })
      )
    );
    return;
  }

  e.respondWith(
    fetch(req)
      .then(res => {
        const copia = res.clone();
        caches.open(CACHE).then(c => c.put(req, copia));
        return res;
      })
      .catch(() => caches.match(req).then(hit => hit || caches.match(BASE)))
  );
});
