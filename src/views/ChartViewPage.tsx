import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();

  if (!selectedProfile) {
    return (
      <motion.div className="card" {...fadeIn}>
        <h2>🔭 Birth Chart</h2>
        <p className="empty-state">
          Select or create a profile in the Reading tab to generate a personalized chart.
        </p>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary mt-3"
          onClick={() => navigate('/')}
        >
          Create or Select Profile
        </motion.button>
      </motion.div>
    );
  }

  return (
    <motion.div {...fadeIn}>
      <ChartView profile={selectedProfile} onExportPDF={() => setError('')} />
    </motion.div>
  );
}
