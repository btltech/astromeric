import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useProfiles, useReading } from '../hooks';
import { useStore } from '../store/useStore';
import { FortuneForm } from '../components/FortuneForm';
import { FortuneResult } from '../components/FortuneResult';
import { ReadingSkeleton } from '../components/Skeleton';
import { toast } from '../components/Toast';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export function ReadingView() {
  const { sessionProfile, createProfile } = useProfiles();
  const { selectedScope, result, setSelectedScope, setResult, getPrediction } = useReading();
  const { loading } = useStore();

  const handleGetPrediction = async () => {
    if (sessionProfile) {
      try {
        await getPrediction(sessionProfile.id);
        toast.success('Your cosmic reading is ready ✨');
      } catch {
        toast.error('Failed to generate reading. Please try again.');
      }
    }
  };

  // Show skeleton while loading
  if (loading && !result) {
    return (
      <motion.div {...fadeIn}>
        <ReadingSkeleton />
      </motion.div>
    );
  }

  if (result) {
    return (
      <motion.div {...fadeIn}>
        <FortuneResult data={result} onReset={() => setResult(null)} />
      </motion.div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div {...fadeIn}>
        {/* Session Profile Active - show scope selection */}
        {sessionProfile ? (
          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h3 className="profile-highlight">✨ {sessionProfile.name}</h3>
            <p className="profile-meta">
              Born {sessionProfile.date_of_birth} • Session only (not saved)
            </p>
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
