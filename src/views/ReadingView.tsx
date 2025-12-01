import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useProfiles, useReading } from '../hooks';
import { useStore } from '../store/useStore';
import { FortuneForm } from '../components/FortuneForm';
import { FortuneResult } from '../components/FortuneResult';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export function ReadingView() {
  const { profiles, selectedProfile, selectedProfileId, setSelectedProfileId, createProfile } =
    useProfiles();
  const { selectedScope, result, setSelectedScope, setResult, getPrediction } = useReading();
  const { loading, showCreateForm, setShowCreateForm } = useStore();

  const handleGetPrediction = async () => {
    if (selectedProfileId) {
      await getPrediction(selectedProfileId);
    }
  };

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
        {/* Profile Selection */}
        <div className="card">
          <h2>Select or Create Profile</h2>
          {profiles.length > 0 && (
            <div className="form-group">
              <label>Select Profile</label>
              <select
                value={selectedProfileId || ''}
                onChange={(e) => setSelectedProfileId(Number(e.target.value))}
                aria-label="Select a profile"
              >
                <option value="">Choose...</option>
                {profiles.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.date_of_birth})
                  </option>
                ))}
              </select>
            </div>
          )}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn-secondary"
          >
            {showCreateForm ? 'Cancel' : 'Create New Profile'}
          </motion.button>
        </div>

        <AnimatePresence>
          {showCreateForm && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
            >
              <FortuneForm
                onSubmit={async (data) => {
                  await createProfile(data);
                  setShowCreateForm(false);
                }}
                isLoading={loading}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Scope Selection */}
        {selectedProfile && (
          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h2>Select Scope</h2>
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
        )}
      </motion.div>
    </AnimatePresence>
  );
}
