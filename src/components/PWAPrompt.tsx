import React from 'react';
import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { usePWA } from '../hooks/usePWA';

const INSTALL_DISMISS_KEY = 'astro-pwa-install-dismissed';
const UPDATE_DISMISS_KEY = 'astro-pwa-update-dismissed';

export function PWAPrompt() {
  const { isInstallable, isUpdateAvailable, installApp, updateApp, isOnline } = usePWA();
  const prefersReducedMotion = useReducedMotion();
  const [dismissed, setDismissed] = React.useState(() => {
    if (typeof window === 'undefined') {
      return false;
    }

    return window.localStorage.getItem(INSTALL_DISMISS_KEY) === '1';
  });
  const [showUpdateBanner, setShowUpdateBanner] = React.useState(() => {
    if (typeof window === 'undefined') {
      return true;
    }

    return window.localStorage.getItem(UPDATE_DISMISS_KEY) !== '1';
  });
  const [hasConsentChoice, setHasConsentChoice] = React.useState(() => {
    if (typeof window === 'undefined') {
      return false;
    }

    return Boolean(window.localStorage.getItem('cookie-consent'));
  });
  const [canShowInstallPrompt, setCanShowInstallPrompt] = React.useState(false);

  React.useEffect(() => {
    const handleConsentSaved = () => {
      setHasConsentChoice(Boolean(window.localStorage.getItem('cookie-consent')));
    };

    window.addEventListener('astro-cookie-consent-saved', handleConsentSaved as EventListener);
    return () => {
      window.removeEventListener('astro-cookie-consent-saved', handleConsentSaved as EventListener);
    };
  }, []);

  React.useEffect(() => {
    if (!isUpdateAvailable && typeof window !== 'undefined') {
      window.localStorage.removeItem(UPDATE_DISMISS_KEY);
      setShowUpdateBanner(true);
    }
  }, [isUpdateAvailable]);

  React.useEffect(() => {
    if (!hasConsentChoice || !isInstallable || dismissed || isUpdateAvailable || typeof window === 'undefined') {
      setCanShowInstallPrompt(false);
      return undefined;
    }

    let timeoutId: number | undefined;

    const reveal = () => setCanShowInstallPrompt(true);
    const handleScroll = () => {
      if (window.scrollY > 400) {
        reveal();
      }
    };

    if (window.scrollY > 400) {
      reveal();
    } else {
      timeoutId = window.setTimeout(reveal, 10000);
      window.addEventListener('scroll', handleScroll, { passive: true });
    }

    return () => {
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
      window.removeEventListener('scroll', handleScroll);
    };
  }, [dismissed, hasConsentChoice, isInstallable, isUpdateAvailable]);

  const dismissInstallPrompt = React.useCallback(() => {
    setDismissed(true);
    setCanShowInstallPrompt(false);
    window.localStorage.setItem(INSTALL_DISMISS_KEY, '1');
  }, []);

  const dismissUpdateBanner = React.useCallback(() => {
    setShowUpdateBanner(false);
    window.localStorage.setItem(UPDATE_DISMISS_KEY, '1');
  }, []);

  if (dismissed && !isUpdateAvailable) {
    return null;
  }

  return (
    <>
      {/* Install Prompt */}
      <AnimatePresence>
        {hasConsentChoice && isInstallable && !isUpdateAvailable && !dismissed && canShowInstallPrompt && (
          <motion.div
            className="pwa-install-prompt"
            initial={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 16 }}
            transition={prefersReducedMotion ? { duration: 0.12 } : { type: 'spring', stiffness: 300, damping: 30 }}
          >
            <div className="pwa-install-content">
              <span className="pwa-install-icon" aria-hidden="true">+</span>
              <div className="pwa-install-text">
                <strong>Install AstroNumeric</strong>
                <p>Save it to your home screen for faster access and daily check-ins.</p>
              </div>
            </div>
            <div className="pwa-install-actions">
              <button
                className="pwa-dismiss-btn"
                onClick={dismissInstallPrompt}
                aria-label="Dismiss install prompt"
              >
                Later
              </button>
              <button
                className="pwa-install-btn"
                aria-label="Install AstroNumeric"
                onClick={async () => {
                  const installed = await installApp();
                  if (!installed) {
                    dismissInstallPrompt();
                  }
                }}
              >
                Install
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Update Available Banner */}
      <AnimatePresence>
        {isUpdateAvailable && showUpdateBanner && (
          <motion.div
            className="pwa-update-banner"
            initial={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: -12 }}
            transition={prefersReducedMotion ? { duration: 0.12 } : undefined}
          >
            <span>A new version is ready.</span>
            <div className="pwa-update-actions">
              <button className="pwa-update-dismiss" onClick={dismissUpdateBanner}>
                Later
              </button>
              <button className="pwa-update-btn" aria-label="Update AstroNumeric now" onClick={updateApp}>
                Update Now
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Offline Indicator */}
      <AnimatePresence>
        {!isOnline && (
          <motion.div
            className="pwa-offline-indicator"
            initial={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={prefersReducedMotion ? { opacity: 0 } : { opacity: 0, scale: 0.92 }}
            transition={prefersReducedMotion ? { duration: 0.12 } : undefined}
          >
            <span className="offline-dot" />
            Offline
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .pwa-install-prompt {
          position: fixed;
          right: 1rem;
          bottom: 1rem;
          background: rgba(8, 15, 24, 0.95);
          backdrop-filter: blur(16px);
          border: 1px solid rgba(118, 148, 181, 0.18);
          border-radius: 1rem;
          padding: 0.8rem 0.9rem;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          max-width: 320px;
          width: min(320px, calc(100% - 2rem));
          z-index: 1000;
          box-shadow: 0 18px 36px rgba(2, 8, 18, 0.34);
        }

        body.nav-menu-open .pwa-install-prompt,
        body.nav-menu-open .pwa-update-banner {
          opacity: 0;
          pointer-events: none;
        }

        .pwa-install-content {
          display: flex;
          align-items: center;
          gap: 0.7rem;
          flex: 1;
        }

        .pwa-install-icon {
          width: 28px;
          height: 28px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border-radius: 999px;
          background: rgba(76, 207, 255, 0.16);
          color: #9ae7ff;
          font-size: 1rem;
          font-weight: 700;
          flex-shrink: 0;
        }

        .pwa-install-text {
          flex: 1;
        }

        .pwa-install-text strong {
          display: block;
          color: #f1f5f9;
          font-size: 0.88rem;
        }

        .pwa-install-text p {
          color: #d8e3ee;
          font-size: 0.78rem;
          margin: 0.125rem 0 0;
          line-height: 1.5;
        }

        .pwa-install-actions {
          display: flex;
          gap: 0.5rem;
        }

        .pwa-dismiss-btn {
          background: transparent;
          border: 1px solid rgba(118, 148, 181, 0.18);
          color: #d8e3ee;
          padding: 0.5rem 0.7rem;
          border-radius: 0.5rem;
          font-size: 0.76rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .pwa-dismiss-btn:focus-visible,
        .pwa-install-btn:focus-visible,
        .pwa-update-dismiss:focus-visible,
        .pwa-update-btn:focus-visible {
          outline: 2px solid rgba(76, 207, 255, 0.95);
          outline-offset: 3px;
        }

        .pwa-dismiss-btn:hover {
          background: rgba(118, 148, 181, 0.1);
          color: #e2e8f0;
        }

        .pwa-install-btn {
          background: linear-gradient(135deg, #4ccfff 0%, #2f87ff 100%);
          border: none;
          color: #071018;
          padding: 0.5rem 0.9rem;
          border-radius: 0.5rem;
          font-size: 0.78rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .pwa-install-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(47, 135, 255, 0.3);
        }

        .pwa-update-banner {
          position: fixed;
          top: 86px;
          right: 1rem;
          background: rgba(8, 15, 24, 0.96);
          border: 1px solid rgba(118, 148, 181, 0.18);
          border-radius: 1rem;
          color: #f3f8fd;
          padding: 0.75rem 1rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
          z-index: 1001;
          font-size: 0.875rem;
          box-shadow: 0 18px 36px rgba(2, 8, 18, 0.34);
        }

        .pwa-update-actions {
          display: flex;
          gap: 0.5rem;
        }

        .pwa-update-dismiss {
          background: transparent;
          border: 1px solid rgba(118, 148, 181, 0.18);
          color: #c7d4e2;
          padding: 0.25rem 0.75rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          cursor: pointer;
        }

        .pwa-update-btn {
          background: linear-gradient(135deg, #4ccfff 0%, #2f87ff 100%);
          border: none;
          color: #071018;
          padding: 0.25rem 0.75rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 600;
          cursor: pointer;
        }

        .pwa-offline-indicator {
          position: fixed;
          top: 1rem;
          right: 1rem;
          background: rgba(185, 28, 28, 0.92);
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 2rem;
          font-size: 0.75rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          z-index: 1000;
        }

        .offline-dot {
          width: 8px;
          height: 8px;
          background: white;
          border-radius: 50%;
          animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @media (max-width: 480px) {
          .pwa-install-prompt {
            left: auto;
            right: 10px;
            width: min(220px, calc(100vw - 20px));
            padding: 0.72rem;
          }

          .pwa-update-banner {
            flex-direction: column;
            align-items: stretch;
          }

          .pwa-install-content {
            align-items: flex-start;
          }

          .pwa-install-text p {
            display: none;
          }

          .pwa-install-actions {
            justify-content: stretch;
          }

          .pwa-update-dismiss,
          .pwa-update-btn {
            width: 100%;
          }

          .pwa-dismiss-btn {
            min-width: 60px;
          }

          .pwa-update-banner {
            top: 82px;
            left: 10px;
            right: 10px;
          }
        }

        @media (prefers-reduced-motion: reduce) {
          .offline-dot,
          .pwa-dismiss-btn,
          .pwa-install-btn {
            animation: none;
            transition: none;
          }

          .pwa-install-btn:hover {
            transform: none;
            box-shadow: none;
          }
        }
      `}</style>
    </>
  );
}
