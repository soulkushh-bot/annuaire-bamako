/* Cache hors-ligne minimal : fichiers de l'app en cache-first, données en network-first. */
const VERSION = 'annuaire-v1';
const CORE = ['./', './index.html', './styles.css', './app.js', './manifest.webmanifest', './icons/icon.svg'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return; // tuiles OSM et Leaflet : réseau direct
  const put = (r) => { const copy = r.clone(); caches.open(VERSION).then((c) => c.put(e.request, copy)); return r; };
  if (url.pathname.endsWith('/data/annuaire.json')) {
    e.respondWith(fetch(e.request).then(put).catch(() => caches.match(e.request)));
    return;
  }
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then(put)));
});
