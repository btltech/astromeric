// Minimal service worker - intentionally empty
// This file exists to prevent 404 errors when the browser looks for a service worker
self.addEventListener('install', () => {
  // Nothing to install
});

self.addEventListener('activate', () => {
  // Nothing to activate
});

self.addEventListener('fetch', () => {
  // Pass through - no caching
});
