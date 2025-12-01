import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CosmicBackground } from './components/CosmicBackground';
import { ReadingView, NumerologyView, CompatibilityView, LearnView, AuthView } from './views';
import { useProfiles, useAuth } from './hooks';
import { useStore } from './store/useStore';
// styles.css is imported at the root level (index.tsx)

function NavBar() {
  const { selectedProfileId } = useProfiles();
  const { isAuthenticated, user, logout } = useAuth();

  // Only show nav when a profile is selected (or authenticated)
  const showNav = selectedProfileId || isAuthenticated;

  return (
    <header>
      <h1 className="logo">
        ASTRO<span>NUMEROLOGY</span>
      </h1>

      {isAuthenticated && user && (
        <div className="user-bar">
          <span className="user-email">{user.email}</span>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={logout}
            className="btn-logout"
            aria-label="Sign out"
          >
            Sign Out
          </motion.button>
        </div>
      )}

      {showNav && (
        <nav className="main-nav" role="navigation" aria-label="Main navigation">
          <NavLink to="/" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}>
            📖 Reading
          </NavLink>
          <NavLink
            to="/numerology"
            className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}
          >
            🔢 Numerology
          </NavLink>
          <NavLink
            to="/compatibility"
            className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}
          >
            💕 Compatibility
          </NavLink>
          <NavLink to="/learn" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}>
            📚 Learn
          </NavLink>
          {!isAuthenticated && (
            <NavLink to="/auth" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}>
              🔑 Sign In
            </NavLink>
          )}
        </nav>
      )}
    </header>
  );
}

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<ReadingView />} />
        <Route path="/numerology" element={<NumerologyView />} />
        <Route path="/compatibility" element={<CompatibilityView />} />
        <Route path="/learn" element={<LearnView />} />
        <Route path="/auth" element={<AuthView />} />
      </Routes>
    </AnimatePresence>
  );
}

function LoadingOverlay() {
  const { loading } = useStore();

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          className="loader-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          aria-live="polite"
        >
          <motion.div
            className="spinner"
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
            aria-hidden="true"
          />
          <span>Consulting the stars...</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function ErrorBanner() {
  const { error, setError } = useStore();

  if (!error) return null;

  return (
    <motion.div
      className="error-banner"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      role="alert"
    >
      {error}
      <button
        onClick={() => setError('')}
        style={{
          marginLeft: '1rem',
          background: 'none',
          border: 'none',
          color: 'inherit',
          cursor: 'pointer',
        }}
        aria-label="Dismiss error"
      >
        ✕
      </button>
    </motion.div>
  );
}

export function App() {
  const { fetchProfiles } = useProfiles();
  const { result } = useStore();

  useEffect(() => {
    fetchProfiles();
  }, [fetchProfiles]);

  return (
    <BrowserRouter>
      <div className="app-container">
        <CosmicBackground element={result?.element} />

        <div className="content-wrapper">
          <NavBar />
          <ErrorBanner />
          <AnimatedRoutes />
        </div>

        <LoadingOverlay />
      </div>
    </BrowserRouter>
  );
}
