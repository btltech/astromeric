import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../hooks';
import { useStore } from '../store/useStore';
import { toast } from '../components/Toast';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export function AuthView() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState('');

  const { login, register, isAuthenticated } = useAuth();
  const { loading, error, user } = useStore();

  // Redirect to profile if already authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      toast.success(t('auth.welcomeBack', { email: user.email }));
      navigate('/profile');
    }
  }, [isAuthenticated, user, navigate, t]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');

    if (!email || !password) {
      setLocalError(t('auth.errors.fillAllFields'));
      return;
    }

    if (mode === 'register' && password !== confirmPassword) {
      setLocalError(t('auth.errors.passwordsMismatch'));
      return;
    }

    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password);
      }
      // Navigation will happen via useEffect when isAuthenticated changes
    } catch {
      // Error is handled in the hook and stored in useStore
    }
  };

  return (
    <motion.div className="card" {...fadeIn}>
      <h2>{mode === 'login' ? t('auth.signIn') : t('auth.createAccount')}</h2>
      <p className="section-subtitle mb-3">
        {mode === 'login'
          ? t('auth.signInSubtitle')
          : t('auth.createSubtitle')}
      </p>

      <div className="auth-benefit">
        {t('auth.benefitText')}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">{t('auth.email')}</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t('auth.emailPlaceholder')}
            autoComplete="email"
            aria-required="true"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">{t('auth.password')}</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            aria-required="true"
          />
        </div>

        <AnimatePresence>
          {mode === 'register' && (
            <motion.div
              className="form-group"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <label htmlFor="confirmPassword">{t('auth.confirmPassword')}</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="new-password"
              />
            </motion.div>
          )}
        </AnimatePresence>

        {(localError || error) && (
          <motion.div
            className="error-text"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{ marginBottom: '1rem', textAlign: 'center' }}
          >
            {localError || error}
          </motion.div>
        )}

        <motion.button
          type="submit"
          className="btn-primary"
          disabled={loading}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? t('common.loading') : mode === 'login' ? t('auth.signInButton') : t('auth.createAccount')}
        </motion.button>
      </form>

      <div className="auth-toggle">
        <span className="text-muted">
          {mode === 'login' ? t('auth.noAccount') + ' ' : t('auth.hasAccount') + ' '}
        </span>
        <motion.button
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setLocalError('');
          }}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--primary)',
            cursor: 'pointer',
            textDecoration: 'underline',
          }}
          whileHover={{ scale: 1.05 }}
        >
          {mode === 'login' ? t('auth.register') : t('auth.signInButton')}
        </motion.button>
      </div>

      <div className="guest-section">
        <div className="divider-text"><span>or</span></div>
        <motion.a
          href="/"
          className="btn-secondary guest-btn"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {t('auth.continueAsGuest')}
        </motion.a>
        <p className="guest-note">{t('auth.guestNote')}</p>
      </div>
    </motion.div>
  );
}
