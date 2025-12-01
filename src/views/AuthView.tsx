import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../hooks';
import { useStore } from '../store/useStore';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export function AuthView() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState('');

  const { login, register } = useAuth();
  const { loading, error } = useStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');

    if (!email || !password) {
      setLocalError('Please fill in all fields');
      return;
    }

    if (mode === 'register' && password !== confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password);
      }
    } catch {
      // Error is handled in the hook and stored in useStore
    }
  };

  return (
    <motion.div className="card" {...fadeIn}>
      <h2>{mode === 'login' ? '🔑 Sign In' : '✨ Create Account'}</h2>
      <p style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#aaa' }}>
        {mode === 'login'
          ? 'Sign in to access your cosmic profiles'
          : 'Join to save your readings and profiles'}
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            autoComplete="email"
            aria-required="true"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
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
              <label htmlFor="confirmPassword">Confirm Password</label>
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
          {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
        </motion.button>
      </form>

      <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
        <span style={{ color: '#888' }}>
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
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
          {mode === 'login' ? 'Sign Up' : 'Sign In'}
        </motion.button>
      </div>

      <div style={{ textAlign: 'center', marginTop: '1rem' }}>
        <span style={{ color: '#666', fontSize: '0.85rem' }}>
          Or continue as guest (limited features)
        </span>
      </div>
    </motion.div>
  );
}
