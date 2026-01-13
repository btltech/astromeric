/**
 * SaveReadingsPrompt.tsx
 * Non-blocking upsell modal shown after 3rd anonymous reading
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import './SaveReadingsPrompt.css';

interface SaveReadingsPromptProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SaveReadingsPrompt({ isOpen, onClose }: SaveReadingsPromptProps) {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="save-readings-modal"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose} aria-label="Close">
          ✕
        </button>

        <div className="modal-content">
          <motion.div
            className="modal-icon"
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
          >
            ✨
          </motion.div>

          <h2>{t('upsell.title', 'Save Your Readings')}</h2>

          <p>
            {t(
              'upsell.subtitle',
              "You've created 3 readings! Sign up to save them and get personalized insights."
            )}
          </p>

          <ul className="benefits">
            <li>💾 {t('upsell.benefit1', 'Save all your readings')}</li>
            <li>📊 {t('upsell.benefit2', 'Track patterns over time')}</li>
            <li>🔔 {t('upsell.benefit3', 'Get daily horoscopes')}</li>
            <li>⭐ {t('upsell.benefit4', 'Premium features')}</li>
          </ul>

          <div className="modal-actions">
            <Link to="/auth" className="btn btn-primary" onClick={onClose}>
              {t('upsell.cta', 'Create Account')}
            </Link>
            <button className="btn btn-secondary" onClick={onClose}>
              {t('upsell.later', 'Keep Exploring')}
            </button>
          </div>

          <p className="modal-hint">
            {t('upsell.hint', 'You can always save your readings later')}
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
