import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNumerology, useProfiles } from '../hooks';
import { useStore } from '../store/useStore';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const staggerItem = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
};

export function NumerologyView() {
  const { selectedProfileId } = useProfiles();
  const { numerologyProfile, fetchNumerologyProfile } = useNumerology();
  const { loading } = useStore();

  useEffect(() => {
    if (selectedProfileId && !numerologyProfile) {
      fetchNumerologyProfile(selectedProfileId);
    }
  }, [selectedProfileId, numerologyProfile, fetchNumerologyProfile]);

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
      <h2>🔢 Your Numerology Profile</h2>
      {loading && !numerologyProfile && (
        <p style={{ textAlign: 'center', color: '#888' }}>Loading numerology profile...</p>
      )}
      {numerologyProfile && (
        <motion.div
          className="numerology-grid"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          <motion.div className="num-card" variants={staggerItem}>
            <h4>Life Path</h4>
            <div className="num-value">{numerologyProfile.core_numbers.life_path.number}</div>
            <p>{numerologyProfile.core_numbers.life_path.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4>Expression</h4>
            <div className="num-value">{numerologyProfile.core_numbers.expression.number}</div>
            <p>{numerologyProfile.core_numbers.expression.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4>Soul Urge</h4>
            <div className="num-value">{numerologyProfile.core_numbers.soul_urge.number}</div>
            <p>{numerologyProfile.core_numbers.soul_urge.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4>Personality</h4>
            <div className="num-value">{numerologyProfile.core_numbers.personality.number}</div>
            <p>{numerologyProfile.core_numbers.personality.meaning}</p>
          </motion.div>
          {numerologyProfile.core_numbers.maturity && (
            <motion.div className="num-card" variants={staggerItem}>
              <h4>Maturity</h4>
              <div className="num-value">{numerologyProfile.core_numbers.maturity.number}</div>
              <p>{numerologyProfile.core_numbers.maturity.meaning}</p>
            </motion.div>
          )}
          <motion.div className="num-card highlight" variants={staggerItem}>
            <h4>Personal Year</h4>
            <div className="num-value">{numerologyProfile.cycles.personal_year.number}</div>
            <p>{numerologyProfile.cycles.personal_year.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4>Personal Month</h4>
            <div className="num-value">{numerologyProfile.cycles.personal_month.number}</div>
            <p>{numerologyProfile.cycles.personal_month.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4>Personal Day</h4>
            <div className="num-value">{numerologyProfile.cycles.personal_day.number}</div>
            <p>{numerologyProfile.cycles.personal_day.meaning}</p>
          </motion.div>
          {numerologyProfile.pinnacles && numerologyProfile.pinnacles.length > 0 && (
            <motion.div className="num-card wide" variants={staggerItem}>
              <h4>Life Pinnacles</h4>
              <div className="pinnacles-row">
                {numerologyProfile.pinnacles.map((p, i) => (
                  <div key={i} className="pinnacle">
                    <span className="pinnacle-num">{p.number}</span>
                    <span className="pinnacle-label">Phase {i + 1}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
          {numerologyProfile.challenges && numerologyProfile.challenges.length > 0 && (
            <motion.div className="num-card wide" variants={staggerItem}>
              <h4>Life Challenges</h4>
              <div className="pinnacles-row">
                {numerologyProfile.challenges.map((c, i) => (
                  <div key={i} className="pinnacle challenge">
                    <span className="pinnacle-num">{c.number}</span>
                    <span className="pinnacle-label">Challenge {i + 1}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
