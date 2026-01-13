import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import './CookieConsent.css';

export function CookieConsent() {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [preferences, setPreferences] = useState({
    essential: true, // Always required
    analytics: false,
    marketing: false,
  });

  useEffect(() => {
    // Check if user has already made a choice
    const stored = localStorage.getItem('cookie-consent');
    if (!stored) {
      setIsVisible(true);
    } else {
      const saved = JSON.parse(stored);
      setPreferences(saved);
    }
  }, []);

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
        'analytics_storage': 'granted'
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
          className="cookie-consent-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              // Allow closing by clicking outside
            }
          }}
        >
          <motion.div
            className="cookie-consent-modal"
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 50, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            <div className="cookie-header">
              <h2>🍪 Cookie Preferences</h2>
              <p className="cookie-subtitle">
                We use cookies to enhance your experience and analyze site usage.
              </p>
            </div>

            <div className="cookie-content">
              <div className="cookie-section">
                <h3>Essential Cookies</h3>
                <p>Required for site functionality. Cannot be disabled.</p>
                <label className="cookie-toggle">
                  <input
                    type="checkbox"
                    checked={true}
                    disabled
                    aria-label="Essential cookies (required)"
                  />
                  <span>Always On</span>
                </label>
              </div>

              <div className="cookie-section">
                <h3>Analytics Cookies</h3>
                <p>Help us understand how you use the site to improve your experience.</p>
                <label className="cookie-toggle">
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

              <div className="cookie-section">
                <h3>Marketing Cookies</h3>
                <p>Allow us to personalize ads and track conversions.</p>
                <label className="cookie-toggle">
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

              <p className="cookie-notice text-small">
                Read our{' '}
                <a href="/privacy-policy" className="cookie-link">
                  full privacy policy
                </a>{' '}
                and{' '}
                <a href="/cookie-policy" className="cookie-link">
                  cookie policy
                </a>
                .
              </p>
            </div>

            <div className="cookie-actions">
              <button
                className="btn btn-secondary"
                onClick={handleRejectAll}
                aria-label="Reject all optional cookies"
              >
                Reject All
              </button>
              <button
                className="btn btn-outline"
                onClick={handleSavePreferences}
                aria-label="Save cookie preferences"
              >
                Save Preferences
              </button>
              <button
                className="btn btn-primary"
                onClick={handleAcceptAll}
                aria-label="Accept all cookies"
              >
                Accept All
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
