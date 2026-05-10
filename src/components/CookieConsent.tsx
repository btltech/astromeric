import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CookieConsent.css';

export function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false);
  const [preferences, setPreferences] = useState({
    essential: true, // Always required
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    const stored = localStorage.getItem('cookie-consent');
    if (!stored) {
      setIsVisible(true);
    } else {
      try {
        const saved = JSON.parse(stored);
        setPreferences(saved);
      } catch {
        setIsVisible(true);
      }
    }
  }, []);

  const handleDismiss = () => {
    saveCookieConsent({ essential: true, analytics: false, marketing: false });
  };

  const handleAcceptAll = () => {
    const newPrefs = {
      essential: true,
      analytics: true,
      marketing: true,
    };
    saveCookieConsent(newPrefs);
  };

  const handleRejectAll = () => {
    const newPrefs = {
      essential: true,
      analytics: false,
      marketing: false,
    };
    saveCookieConsent(newPrefs);
  };

  const handleSavePreferences = () => {
    saveCookieConsent(preferences);
  };

  const saveCookieConsent = (prefs: typeof preferences) => {
    localStorage.setItem('cookie-consent', JSON.stringify(prefs));
    setPreferences(prefs);
    setIsVisible(false);
    window.dispatchEvent(new CustomEvent('astro-cookie-consent-saved'));

    // Load analytics if accepted
    if (prefs.analytics) {
      loadGoogleAnalytics();
    }

    // Load marketing pixels if accepted
    if (prefs.marketing) {
      loadMarketingPixels();
    }
  };

  const loadGoogleAnalytics = () => {
    // Google Analytics integration (placeholder)
    if (window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: 'granted',
      });
    }
  };

  const loadMarketingPixels = () => {
    // Marketing pixels (placeholder)
    if (window.fbq) {
      window.fbq('consent', 'grant');
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="cookie-consent-shell"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="cookie-consent-banner"
            initial={{ y: 24, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 24, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            <div className="cookie-consent__header">
              <div>
                <span className="cookie-consent__eyebrow">Privacy choice</span>
                <h2>Cookie preferences</h2>
              </div>
              <button
                type="button"
                className="cookie-consent__close"
                onClick={handleDismiss}
                aria-label="Use essential cookies only"
              >
                Close
              </button>
            </div>

            <p className="cookie-consent__summary">
              Essential cookies stay on. Choose whether you also want analytics and marketing cookies.
            </p>

            <div className="cookie-consent__options">
              <div className="cookie-consent__option">
                <h3>Essential Cookies</h3>
                <p>Required for site functionality. Cannot be disabled.</p>
                <label className="cookie-consent__toggle">
                  <input
                    type="checkbox"
                    checked={true}
                    disabled
                    aria-label="Essential cookies (required)"
                  />
                  <span>Always On</span>
                </label>
              </div>

              <div className="cookie-consent__option">
                <h3>Analytics Cookies</h3>
                <p>Help us understand how you use the site to improve your experience.</p>
                <label className="cookie-consent__toggle">
                  <input
                    type="checkbox"
                    checked={preferences.analytics}
                    onChange={(e) =>
                      setPreferences({ ...preferences, analytics: e.target.checked })
                    }
                    aria-label="Analytics cookies"
                  />
                  <span>{preferences.analytics ? 'Enabled' : 'Disabled'}</span>
                </label>
              </div>

              <div className="cookie-consent__option">
                <h3>Marketing Cookies</h3>
                <p>Allow us to personalize ads and track conversions.</p>
                <label className="cookie-consent__toggle">
                  <input
                    type="checkbox"
                    checked={preferences.marketing}
                    onChange={(e) =>
                      setPreferences({ ...preferences, marketing: e.target.checked })
                    }
                    aria-label="Marketing cookies"
                  />
                  <span>{preferences.marketing ? 'Enabled' : 'Disabled'}</span>
                </label>
              </div>
            </div>

            <div className="cookie-consent__actions">
              <button
                className="cookie-consent__button cookie-consent__button--secondary"
                onClick={handleRejectAll}
                aria-label="Reject all optional cookies"
              >
                Only Essential
              </button>
              <button
                className="cookie-consent__button cookie-consent__button--outline"
                onClick={handleSavePreferences}
                aria-label="Save cookie preferences"
              >
                Save Preferences
              </button>
              <button
                className="cookie-consent__button cookie-consent__button--primary"
                onClick={handleAcceptAll}
                aria-label="Accept all cookies"
              >
                Accept All
              </button>
            </div>

            <p className="cookie-consent__notice">
              Read our <a href="/privacy-policy">privacy policy</a> and{' '}
              <a href="/cookie-policy">cookie policy</a>.
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
