const CACHE_NAME = 'SmileSlot-V01.02'; // bump version on changes
const OFFLINE_URL = '/offline';      // be consistent (no trailing slash)
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/app.js',
  '/static/11_11.js',
  '/static/icon/smiles.png',
  OFFLINE_URL
];

// Install: cache shell and offline page
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .catch(err => console.error('Cache addAll failed:', err))
  );
  // Wait to be activated immediately on next load
  self.skipWaiting();
});

// Activate: cleanup old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(name => (name !== CACHE_NAME) ? caches.delete(name) : null)
      )
    )
  );
  self.clients.claim();
});

// Fetch: network-first for navigations (HTML). cache-first for static assets.
self.addEventListener('fetch', event => {
  const req = event.request;

  // Only handle GET requests
  if (req.method !== 'GET') return;

  // Network-first for navigation requests (pages)
  if (req.mode === 'navigate' || (req.destination === 'document')) {
    event.respondWith(
      fetch(req)
        .then(networkResponse => {
          // Optionally update cache for the page
          caches.open(CACHE_NAME).then(cache => {
            // clone to avoid locking stream
            cache.put(req, networkResponse.clone());
          });
          return networkResponse;
        })
        .catch(() => {
          // If network fails, return cached page or offline fallback
          return caches.match(req).then(resp => resp || caches.match(OFFLINE_URL));
        })
    );
    return;
  }

  // For same-origin static resources: cache-first, fallback to network
  const url = new URL(req.url);
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req)
        .then(cached => cached || fetch(req).then(networkResp => {
          // Optionally cache the fetched resource (runtime caching)
          // but keep it small to avoid filling quota
          if (req.destination === 'script' || req.destination === 'style' || req.destination === 'image') {
            caches.open(CACHE_NAME).then(cache => {
              cache.put(req, networkResp.clone());
            });
          }
          return networkResp;
        }).catch(() => {
          // fallback for images to a placeholder (optional)
          if (req.destination === 'image') {
            return caches.match('/static/icon/smiles.png');
          }
          return caches.match(OFFLINE_URL);
        }))
    );
    return;
  }

  // For cross-origin: just try network, fallback to cache if present
  event.respondWith(
    fetch(req)
      .catch(() => caches.match(req))
  );
});

// Optional: allow clients to trigger skipWaiting on update
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
