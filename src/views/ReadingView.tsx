import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useProfiles, useReading } from '../hooks';
import { useStore } from '../store/useStore';
import { FortuneForm } from '../components/FortuneForm';
import { FortuneResult } from '../components/FortuneResult';
import { ReadingSkeleton } from '../components/Skeleton';
import { toast } from '../components/Toast';
import { DailyReminderToggle } from '../components/DailyReminderToggle';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export function ReadingView() {
  const { t } = useTranslation();
  const { selectedProfile, createProfile } = useProfiles();
  const { selectedScope, result, setSelectedScope, setResult, getPrediction } = useReading();
  const { loading, allowCloudHistory, setAllowCloudHistory, token } = useStore();

  const handleGetPrediction = async () => {
    if (!selectedProfile) {
      toast.error('Create or select a profile first.');
      return;
    }

    try {
      await getPrediction(selectedProfile.id);
      toast.success('Your cosmic reading is ready ✨');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate reading. Please try again.';
      toast.error(message);
    }
  };

  // Show skeleton while loading
  if (loading && !result) {
    return (
      <motion.div className="page" {...fadeIn}>
        <ReadingSkeleton />
      </motion.div>
    );
  }

  if (result) {
    return (
      <motion.div className="page" {...fadeIn}>
        <FortuneResult data={result} onReset={() => setResult(null)} />
      </motion.div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div className="page" {...fadeIn}>
        <section className="hero hero-compact" aria-label={t('hero.eyebrow')}>
          <div className="hero-copy">
            <p className="eyebrow">{t('hero.eyebrow')}</p>
            <h1>{t('hero.title')}</h1>
            <p className="lede">{t('hero.subtitle')}</p>
            <ul className="hero-benefits">
              <li>{t('hero.benefit1')}</li>
              <li>{t('hero.benefit2')}</li>
              <li>{t('hero.benefit3')}</li>
            </ul>
          </div>
        </section>

        <DailyReminderToggle />

        {/* Session Profile Active - show scope selection */}
        {selectedProfile ? (
          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h3 className="profile-highlight">✨ {selectedProfile.name}</h3>
            <p className="profile-meta">
              Born {selectedProfile.date_of_birth} • {selectedProfile.id > 0 ? 'Saved profile' : 'Session profile (not saved)'}
            </p>
            <div className="toggle-row toggle-row--mt">
              <label htmlFor="cloud-history" className="toggle-label">
                Save readings to cloud
              </label>
              <button
                id="cloud-history"
                type="button"
                className={`toggle ${allowCloudHistory ? 'on' : 'off'}`}
                onClick={() => setAllowCloudHistory(!allowCloudHistory)}
                disabled={selectedProfile.id < 1}
                aria-pressed={allowCloudHistory}
              >
                <span className="toggle-knob" />
              </button>
              <span className="text-muted toggle-hint">
                {!token
                  ? 'Sign in to sync readings'
                  : selectedProfile.id < 1
                    ? 'Save a profile to enable cloud history'
                    : allowCloudHistory
                      ? 'Synced after each reading'
                      : 'Off by default for privacy'}
              </span>
            </div>
            <h4>Select Reading Scope</h4>
            <div className="tabs" role="tablist">
              {(['daily', 'weekly', 'monthly'] as const).map((scope) => (
                <motion.button
                  key={scope}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={selectedScope === scope ? 'tab active' : 'tab'}
                  onClick={() => setSelectedScope(scope)}
                  role="tab"
                  aria-selected={selectedScope === scope}
                >
                  {scope.charAt(0).toUpperCase() + scope.slice(1)}
                </motion.button>
              ))}
            </div>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleGetPrediction}
              className="btn-primary"
              disabled={loading}
            >
              {loading
                ? 'Reading...'
                : `Get ${selectedScope.charAt(0).toUpperCase() + selectedScope.slice(1)} Reading`}
            </motion.button>
          </motion.div>
        ) : (
          /* No profile - show form */
          <FortuneForm
            onSubmit={async (data) => {
              await createProfile(data);
            }}
            isLoading={loading}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
}
