/* Cache hors-ligne minimal : l'app est servie depuis le cache puis rafraîchie en arrière-plan
   (stale-while-revalidate), les données sont prises sur le réseau en priorité. */
const VERSION = 'danaya-v3';
const CORE = ['./', './index.html', './styles.css', './app.js', './manifest.webmanifest', './icons/icon.svg', './favicon.ico'];

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
  // Les filtres vivent dans la query string (?q=…&cat=…) mais renvoient toujours la même page :
  // on sert l'unique copie en cache, sinon chaque recherche partagée créerait une entrée de plus.
  const key = e.request.mode === 'navigate' ? './index.html' : e.request;
  // Servi depuis le cache, mais rafraîchi en arrière-plan : sans cela, une mise à jour de
  // app.js ou styles.css ne serait jamais reprise par un visiteur déjà venu.
  e.respondWith(caches.match(key).then((hit) => {
    const net = fetch(e.request).then((r) => {
      if (r.ok) { const copy = r.clone(); caches.open(VERSION).then((c) => c.put(key, copy)); }
      return r;
    });
    return hit || net;
  }));
});
