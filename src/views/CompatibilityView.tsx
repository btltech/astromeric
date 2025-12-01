import React from 'react';
import { motion } from 'framer-motion';
import { useCompatibility, useProfiles } from '../hooks';
import { useStore } from '../store/useStore';
import { CompatibilityCard } from '../components/CompatibilityCard';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 },
};

export function CompatibilityView() {
  const { profiles, selectedProfileId } = useProfiles();
  const { compareProfileId, compatibilityResult, setCompareProfileId, fetchCompatibility } =
    useCompatibility();
  const { loading } = useStore();

  const handleCalculate = async () => {
    if (selectedProfileId && compareProfileId) {
      await fetchCompatibility(selectedProfileId, compareProfileId);
    }
  };

  if (!selectedProfileId) {
    return (
      <motion.div className="card" {...fadeIn}>
        <p style={{ textAlign: 'center', color: '#888' }}>
          Please select a profile first from the Reading tab.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div className="card" {...fadeIn}>
      <h2>💕 Compatibility Check</h2>
      <p style={{ textAlign: 'center', marginBottom: '1rem', color: '#aaa' }}>
        Compare your cosmic alignment with another profile
      </p>
      <div className="form-group">
        <label id="compare-label">Compare With</label>
        <select
          value={compareProfileId || ''}
          onChange={(e) => setCompareProfileId(Number(e.target.value))}
          aria-labelledby="compare-label"
        >
          <option value="">Choose a profile...</option>
          {profiles
            .filter((p) => p.id !== selectedProfileId)
            .map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.date_of_birth})
              </option>
            ))}
        </select>
      </div>
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleCalculate}
        className="btn-primary"
        disabled={loading || !compareProfileId}
      >
        {loading ? 'Calculating...' : 'Calculate Compatibility'}
      </motion.button>

      {compatibilityResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <CompatibilityCard data={compatibilityResult} />
        </motion.div>
      )}
    </motion.div>
  );
}
