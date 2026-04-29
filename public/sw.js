const CACHE_NAME = 'astronumeric-cache-v3';
const STATIC_ASSETS = [
  '/manifest.json',
  '/offline.html',
  '/favicon.svg',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)));
    })
  );
  self.clients.claim();
});

self.addEventListener('message', (event) => {
  if (event?.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') return;

  // Network-first for navigations/HTML so deploys aren't stuck on cached index.html
  const accept = event.request.headers.get('Accept') || '';
  const isHtmlRequest = event.request.mode === 'navigate' || accept.includes('text/html');

  if (isHtmlRequest) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.ok) {
            return caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, networkResponse.clone());
              return networkResponse;
            });
          }
          return networkResponse;
        })
        .catch(() =>
          caches.open(CACHE_NAME).then((cache) =>
            cache.match(event.request).then((cached) => {
              if (cached) return cached;
              return cache.match('/offline.html').then((offline) => {
                return offline || new Response('Offline', { status: 503, statusText: 'Offline' });
              });
            })
          )
        )
    );
    return;
  }

  // Stale-While-Revalidate strategy for static assets and HTML
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchedResponse = fetch(event.request)
          .then((networkResponse) => {
            // Only cache if response is 200 OK and it's not a redirected HTML for a JS/CSS file
            const contentType = networkResponse.headers.get('Content-Type');
            const isHtml = contentType && contentType.includes('text/html');
            const isAsset = event.request.url.match(/\.(js|css|png|jpg|svg|json|woff2)$/);

            if (networkResponse.ok && !(isAsset && isHtml)) {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch((err) => {
            // Fallback to offline page if network fails and no cache
            if (event.request.mode === 'navigate') {
              return cache.match('/offline.html').then((response) => {
                return response || new Response('Offline', { status: 503, statusText: 'Offline' });
              });
            }
            // If we can't find anything, return a simple error response
            // to avoid "Failed to convert value to 'Response'" error
            return new Response('Network error', { status: 408, statusText: 'Network Error' });
          });

        return cachedResponse || fetchedResponse;
      });
    })
  );
});

self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: data.icon || '/icons/icon-192x192.png',
      badge: '/icons/icon-192x192.png',
      data: {
        url: data.url || '/',
      },
    };
    event.waitUntil(self.registration.showNotification(data.title, options));
  }
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(clients.openWindow(event.notification.data.url));
});
