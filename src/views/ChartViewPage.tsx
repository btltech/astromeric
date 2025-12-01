import React from 'react';
import { motion } from 'framer-motion';
import ChartView from '../components/ChartView';
import { useProfiles } from '../hooks';
import { useStore } from '../store/useStore';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

export function ChartViewPage() {
  const { selectedProfile } = useProfiles();
  const { setError } = useStore();

  if (!selectedProfile) {
    return (
      <motion.div className="card" {...fadeIn}>
        <h2>🔭 Birth Chart</h2>
        <p style={{ color: '#aaa', textAlign: 'center' }}>
          Select or create a profile in the Reading tab to generate a personalized chart.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div {...fadeIn}>
      <ChartView
        profile={selectedProfile}
        onExportPDF={() => setError('')}
      />
    </motion.div>
  );
}
