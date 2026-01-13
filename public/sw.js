const CACHE_NAME = 'astronumeric-cache-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/offline.html',
  '/favicon.svg',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
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
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') return;

  // Stale-While-Revalidate strategy for static assets and HTML
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchedResponse = fetch(event.request).then((networkResponse) => {
          if (networkResponse.ok) {
            cache.put(event.request, networkResponse.clone());
          }
          return networkResponse;
        }).catch((err) => {
          // Fallback to offline page if network fails and no cache
          if (event.request.mode === 'navigate') {
            return cache.match('/offline.html').then(response => {
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
        url: data.url || '/'
      }
    };
    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
