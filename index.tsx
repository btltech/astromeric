import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './src/App';
import './src/i18n'; // Initialize i18n
import './styles.css';

// Unregister any service worker during local development to avoid stale caches.
const _meta = import.meta as unknown as { env?: { DEV?: boolean } };
if (typeof window !== 'undefined' && _meta.env?.DEV && 'serviceWorker' in navigator) {
  try {
    navigator.serviceWorker.getRegistrations().then((regs) => regs.forEach((r) => r.unregister()));
    if ('caches' in window) {
      caches.keys().then((keys) => keys.forEach((k) => caches.delete(k)));
    }
  } catch (e) {
    // ignore
  }
}

const root = createRoot(document.getElementById('root')!);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
