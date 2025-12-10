import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CosmicBackground } from './components/CosmicBackground';
import { useProfiles, useAuth } from './hooks';
import { useStore } from './store/useStore';
import { ToastContainer, useToasts } from './components/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { PWAPrompt } from './components/PWAPrompt';

// Lazy load views for code splitting
const ReadingView = React.lazy(() => import('./views/ReadingView').then(m => ({ default: m.ReadingView })));
const NumerologyView = React.lazy(() => import('./views/NumerologyView').then(m => ({ default: m.NumerologyView })));
const CompatibilityView = React.lazy(() => import('./views/CompatibilityView').then(m => ({ default: m.CompatibilityView })));
const LearnView = React.lazy(() => import('./views/LearnView').then(m => ({ default: m.LearnView })));
const AuthView = React.lazy(() => import('./views/AuthView').then(m => ({ default: m.AuthView })));
const ChartViewPage = React.lazy(() => import('./views/ChartViewPage').then(m => ({ default: m.ChartViewPage })));
const CosmicToolsView = React.lazy(() => import('./views/CosmicToolsView').then(m => ({ default: m.CosmicToolsView })));
// styles.css is imported at the root level (index.tsx)

function NavBar() {
  const { sessionProfile } = useProfiles();
  const { isAuthenticated, user, logout } = useAuth();
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <header>
      <NavLink to="/" className="logo-link">
        <div className="logo" aria-label="Astromeric home">
          ASTRO<span>MERIC</span>
        </div>
      </NavLink>

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

      <button
        className="nav-toggle"
        aria-label="Toggle navigation"
        aria-expanded={isOpen}
        onClick={() => setIsOpen((v) => !v)}
      >
        {isOpen ? '✕' : '☰'}
      </button>

      <nav className={`main-nav ${isOpen ? 'open' : ''}`} role="navigation" aria-label="Main navigation">
        <NavLink to="/" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          ✨ Reading
        </NavLink>
        <NavLink
          to="/numerology"
          className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}
          onClick={() => setIsOpen(false)}
        >
          🔢 Numbers
        </NavLink>
        <NavLink
          to="/tools"
          className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`}
          onClick={() => setIsOpen(false)}
        >
          🔮 Tools
        </NavLink>
        <NavLink to="/learn" className={({ isActive }) => `nav-btn ${isActive ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
          📚 Learn
        </NavLink>
        {!isAuthenticated && (
          <NavLink to="/auth" className={({ isActive }) => `nav-btn nav-btn-secondary ${isActive ? 'active' : ''}`} onClick={() => setIsOpen(false)}>
            Sign In
          </NavLink>
        )}
      </nav>
    </header>
  );
}

function AnimatedRoutes() {
  const location = useLocation();
  const { result } = useStore();
  const { sessionProfile } = useProfiles();

  // Extract chart data for cosmic tools
  const chartData = result?.charts?.natal;
  const sunSign = chartData?.planets?.find((p: { name: string }) => p.name === 'Sun')?.sign;
  const moonSign = chartData?.planets?.find((p: { name: string }) => p.name === 'Moon')?.sign;
  // Rising sign may be in ascendant or in planets array depending on backend
  const risingSign = (result?.charts?.natal as { ascendant?: { sign?: string } })?.ascendant?.sign 
    || chartData?.planets?.find((p: { name: string }) => p.name === 'Ascendant')?.sign;
  const birthDate = sessionProfile?.date_of_birth;

  return (
    <ErrorBoundary>
      <AnimatePresence mode="wait">
        <React.Suspense fallback={<LoadingOverlay forceVisible />}>
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<ReadingView />} />
            <Route path="/numerology" element={<NumerologyView />} />
            <Route path="/compatibility" element={<CompatibilityView />} />
            <Route path="/chart" element={<ChartViewPage />} />
            <Route path="/tools" 
              element={
                <CosmicToolsView 
                  birthDate={birthDate}
                  sunSign={sunSign}
                  moonSign={moonSign}
                  risingSign={risingSign}
                />
              } 
            />
            <Route path="/learn" element={<LearnView />} />
            <Route path="/auth" element={<AuthView />} />
          </Routes>
        </React.Suspense>
      </AnimatePresence>
    </ErrorBoundary>
  );
}

function LoadingOverlay({ forceVisible = false }: { forceVisible?: boolean }) {
  const { loading } = useStore();
  const isVisible = loading || forceVisible;

  return (
    <AnimatePresence>
      {isVisible && (
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

function Layout() {
  const { result } = useStore();
  const { toasts, dismiss } = useToasts();

  return (
    <div className="app-container">
      {/* Skip link for keyboard navigation */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      
      <CosmicBackground element={result?.element} />

      <div className="content-wrapper">
        <NavBar />
        <ErrorBanner />
        <main id="main-content" tabIndex={-1}>
          <AnimatedRoutes />
        </main>
      </div>

      <LoadingOverlay />
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
      <PWAPrompt />
    </div>
  );
}

export function App() {
  // No fetchProfiles - all profiles are session-only for privacy
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}
