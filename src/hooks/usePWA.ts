import { useState, useEffect, useCallback } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

interface UsePWAReturn {
  isInstallable: boolean;
  isInstalled: boolean;
  isOnline: boolean;
  isUpdateAvailable: boolean;
  installApp: () => Promise<boolean>;
  updateApp: () => void;
}

export function usePWA(): UsePWAReturn {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null);

  // Check if app is already installed
  useEffect(() => {
    // Check display-mode
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    // Check iOS standalone
    const isIOSStandalone = (navigator as unknown as { standalone?: boolean }).standalone === true;

    setIsInstalled(isStandalone || isIOSStandalone);
  }, []);

  // Listen for install prompt
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e as BeforeInstallPromptEvent);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  // Listen for app installed event
  useEffect(() => {
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setInstallPrompt(null);
      console.log('PWA installed successfully');
    };

    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Register service worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('Service Worker registered:', reg.scope);
          setRegistration(reg);

          // Check for updates
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  setIsUpdateAvailable(true);
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });

      // Listen for controller change (new SW activated)
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        window.location.reload();
      });
    }
  }, []);

  // Install the app
  const installApp = useCallback(async (): Promise<boolean> => {
    if (!installPrompt) {
      console.log('Install prompt not available');
      return false;
    }

    try {
      await installPrompt.prompt();
      const { outcome } = await installPrompt.userChoice;

      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
        setInstallPrompt(null);
        return true;
      } else {
        console.log('User dismissed the install prompt');
        return false;
      }
    } catch (error) {
      console.error('Install failed:', error);
      return false;
    }
  }, [installPrompt]);

  // Update the app (skip waiting)
  const updateApp = useCallback(() => {
    if (registration?.waiting) {
      registration.waiting.postMessage({ type: 'SKIP_WAITING' });
    }
  }, [registration]);

  return {
    isInstallable: !!installPrompt && !isInstalled,
    isInstalled,
    isOnline,
    isUpdateAvailable,
    installApp,
    updateApp,
  };
}
