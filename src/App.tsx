import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CosmicBackground } from './components/CosmicBackground';
import { CookieConsent } from './components/CookieConsent';
import { Footer } from './components/Footer';
import { PWAPrompt } from './components/PWAPrompt';

// Lazy load views for code splitting
const HomeSupportView = React.lazy(() =>
  import('./views/HomeSupportView').then((m) => ({ default: m.HomeSupportView }))
);
const PrivacyPolicy = React.lazy(() =>
  import('./views/PrivacyPolicy').then((m) => ({ default: m.PrivacyPolicy }))
);
const TermsOfService = React.lazy(() =>
  import('./views/TermsOfService').then((m) => ({ default: m.TermsOfService }))
);
const CookiePolicy = React.lazy(() =>
  import('./views/CookiePolicy').then((m) => ({ default: m.CookiePolicy }))
);

function NavBar() {
  return (
    <header style={{ justifyContent: 'center' }}>
      <NavLink to="/" className="logo-link" style={{ margin: '0 auto' }}>
        <div className="logo" aria-label="AstroNumeric home">
          ASTRO<span>NUMERIC</span>
        </div>
      </NavLink>
    </header>
  );
}

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <React.Suspense fallback={<div className="loader-overlay" />}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<HomeSupportView />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/privacy" element={<Navigate to="/privacy-policy" replace />} />
          <Route path="/terms" element={<TermsOfService />} />
          <Route path="/cookie-policy" element={<CookiePolicy />} />

          {/* Default redirect to home/support */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </React.Suspense>
    </AnimatePresence>
  );
}

function Layout() {
  return (
    <div className="app-container">
      <CosmicBackground element="fire" />

      <div className="content-wrapper">
        <NavBar />
        <main id="main-content" tabIndex={-1}>
          <AnimatedRoutes />
        </main>
        <Footer />
      </div>

      <PWAPrompt />
      <CookieConsent />
    </div>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}
