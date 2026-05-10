import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { CookieConsent } from './components/CookieConsent';
import { Footer } from './components/Footer';
import { PWAPrompt } from './components/PWAPrompt';
import { NavigationBar } from './components/home/NavigationBar';

// Lazy load views for code splitting
const HomeSupportView = React.lazy(() => import('./views/HomeSupportView'));
const ReadingView = React.lazy(() => import('./views/ReadingView'));
const JournalWorkspaceView = React.lazy(() => import('./views/JournalWorkspaceView'));
const ChartViewPage = React.lazy(() => import('./views/ChartViewPage'));
const NumerologyDeskView = React.lazy(() => import('./views/NumerologyDeskView'));
const CosmicToolsView = React.lazy(() => import('./views/CosmicToolsView'));
const YearAheadView = React.lazy(() => import('./views/YearAheadView'));
const RelationshipsView = React.lazy(() => import('./views/RelationshipsView'));
const LearnView = React.lazy(() => import('./views/LearnView'));
const ProfileView = React.lazy(() => import('./views/ProfileView'));
const SupportCenter = React.lazy(() =>
  import('./views/SupportCenter').then((m) => ({ default: m.SupportCenter }))
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

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <React.Suspense fallback={<div className="loader-overlay" />}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<HomeSupportView />} />
          <Route path="/reading" element={<ReadingView />} />
          <Route path="/journal" element={<JournalWorkspaceView />} />
          <Route path="/charts" element={<ChartViewPage />} />
          <Route path="/numerology" element={<NumerologyDeskView />} />
          <Route path="/tools" element={<CosmicToolsView />} />
          <Route path="/year-ahead" element={<YearAheadView />} />
          <Route path="/relationships" element={<RelationshipsView />} />
          <Route path="/learn" element={<LearnView />} />
          <Route path="/profile" element={<ProfileView />} />
          <Route path="/experience" element={<Navigate to="/charts" replace />} />
          <Route path="/support" element={<SupportCenter />} />
          <Route path="/help" element={<Navigate to="/support" replace />} />
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
    <div className="app-container app-shell">
      <div className="content-wrapper content-wrapper--modern">
        <NavigationBar />
        <main id="main-content" tabIndex={-1} className="site-main">
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
