import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePWA } from '../hooks/usePWA';

export function PWAPrompt() {
  const { isInstallable, isUpdateAvailable, installApp, updateApp, isOnline } = usePWA();
  const [dismissed, setDismissed] = React.useState(false);
  const [showUpdateBanner, setShowUpdateBanner] = React.useState(true);

  // Don't show if user dismissed or app is already installed
  if (dismissed && !isUpdateAvailable) {
    return null;
  }

  return (
    <>
      {/* Install Prompt */}
      <AnimatePresence>
        {isInstallable && !dismissed && (
          <motion.div
            className="pwa-install-prompt"
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            <div className="pwa-install-content">
              <div className="pwa-install-icon">✨</div>
              <div className="pwa-install-text">
                <strong>Install AstroNumeric</strong>
                <p>Add to home screen for the best experience</p>
              </div>
            </div>
            <div className="pwa-install-actions">
              <button
                className="pwa-dismiss-btn"
                onClick={() => setDismissed(true)}
                aria-label="Dismiss install prompt"
              >
                Not now
              </button>
              <button
                className="pwa-install-btn"
                onClick={async () => {
                  const installed = await installApp();
                  if (!installed) {
                    setDismissed(true);
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
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
          >
            <span>🚀 A new version is available!</span>
            <div className="pwa-update-actions">
              <button className="pwa-update-dismiss" onClick={() => setShowUpdateBanner(false)}>
                Later
              </button>
              <button className="pwa-update-btn" onClick={updateApp}>
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
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
          >
            <span className="offline-dot" />
            Offline
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        .pwa-install-prompt {
          position: fixed;
          bottom: 1.5rem;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(30, 41, 59, 0.95);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(139, 92, 246, 0.3);
          border-radius: 1rem;
          padding: 1rem 1.25rem;
          display: flex;
          align-items: center;
          gap: 1rem;
          max-width: 420px;
          width: calc(100% - 2rem);
          z-index: 1000;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }

        .pwa-install-content {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex: 1;
        }

        .pwa-install-icon {
          font-size: 1.5rem;
        }

        .pwa-install-text {
          flex: 1;
        }

        .pwa-install-text strong {
          display: block;
          color: #f1f5f9;
          font-size: 0.9375rem;
        }

        .pwa-install-text p {
          color: #94a3b8;
          font-size: 0.8125rem;
          margin: 0.125rem 0 0;
        }

        .pwa-install-actions {
          display: flex;
          gap: 0.5rem;
        }

        .pwa-dismiss-btn {
          background: transparent;
          border: 1px solid rgba(148, 163, 184, 0.3);
          color: #94a3b8;
          padding: 0.5rem 0.875rem;
          border-radius: 0.5rem;
          font-size: 0.8125rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .pwa-dismiss-btn:hover {
          background: rgba(148, 163, 184, 0.1);
          color: #e2e8f0;
        }

        .pwa-install-btn {
          background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
          border: none;
          color: white;
          padding: 0.5rem 1rem;
          border-radius: 0.5rem;
          font-size: 0.8125rem;
          font-weight: 600;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .pwa-install-btn:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }

        .pwa-update-banner {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
          color: white;
          padding: 0.75rem 1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          z-index: 1001;
          font-size: 0.875rem;
        }

        .pwa-update-actions {
          display: flex;
          gap: 0.5rem;
        }

        .pwa-update-dismiss {
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.4);
          color: white;
          padding: 0.25rem 0.75rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          cursor: pointer;
        }

        .pwa-update-btn {
          background: white;
          border: none;
          color: #6366f1;
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
          background: rgba(239, 68, 68, 0.9);
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
            flex-direction: column;
            align-items: stretch;
            text-align: center;
          }

          .pwa-install-content {
            flex-direction: column;
          }

          .pwa-install-actions {
            justify-content: center;
          }
        }
      `}</style>
    </>
  );
}
