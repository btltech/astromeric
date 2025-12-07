import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { useNumerology, useProfiles } from '../hooks';
import { useStore } from '../store/useStore';

// Tooltip component for explaining numerology terms
function Tooltip({ term, children }: { term: string; children: React.ReactNode }) {
  const [show, setShow] = useState(false);
  
  const explanations: Record<string, string> = {
    'Life Path': 'Your Life Path number reveals your life purpose and the path you walk. It\'s calculated from your full birth date.',
    'Expression': 'Your Expression number shows your natural talents and abilities. It\'s derived from all the letters in your full name.',
    'Soul Urge': 'Your Soul Urge reveals your inner desires and what truly motivates you. It comes from the vowels in your name.',
    'Personality': 'Your Personality number shows how others perceive you. It\'s calculated from the consonants in your name.',
    'Maturity': 'Your Maturity number reveals goals that emerge in the second half of life. It\'s the sum of Life Path and Expression.',
    'Personal Year': 'Your Personal Year shows the theme and energy for your current year cycle (1-9).',
    'Personal Month': 'Your Personal Month reveals the specific energy and focus for this month within your year cycle.',
    'Personal Day': 'Your Personal Day shows the energy available today within your monthly and yearly cycles.',
    'Life Pinnacles': 'Pinnacles are four long-term cycles that represent major life phases and lessons. Each phase can last 9+ years.',
    'Life Challenges': 'Challenges represent obstacles and growth opportunities across your life phases.',
  };
  
  return (
    <span 
      className="tooltip-wrapper"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
      onClick={() => setShow(!show)}
    >
      {children}
      <span className="tooltip-icon" aria-label="More info">ⓘ</span>
      {show && (
        <span className="tooltip-content" role="tooltip">
          {explanations[term] || `Learn more about ${term}`}
        </span>
      )}
    </span>
  );
}

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
  const { selectedProfile } = useProfiles();
  const { numerologyProfile, fetchNumerologyFromProfile, fetchNumerologyProfile } = useNumerology();
  const { loading } = useStore();
  const lastFetchedId = useRef<number | null>(null);

  useEffect(() => {
    if (selectedProfile && !numerologyProfile && lastFetchedId.current !== selectedProfile.id) {
      lastFetchedId.current = selectedProfile.id;
      
      // Use session-based fetch for session profiles (negative IDs) or saved profiles
      if (selectedProfile.id < 0) {
        // Session profile - use POST endpoint with profile data
        fetchNumerologyFromProfile(selectedProfile);
      } else {
        // Saved profile - use GET endpoint with ID
        fetchNumerologyProfile(selectedProfile.id);
      }
    }
  }, [selectedProfile, numerologyProfile, fetchNumerologyFromProfile, fetchNumerologyProfile]);

  if (!selectedProfile) {
    return (
      <motion.div className="card" {...fadeIn}>
        <p className="empty-state">
          Please enter your birth details first from the Reading tab.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div className="card" {...fadeIn}>
      <h2>🔢 Your Numerology Profile</h2>
      {loading && !numerologyProfile && (
        <p className="loading-text">Loading numerology profile...</p>
      )}
      {numerologyProfile && (
        <motion.div
          className="numerology-grid"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          <motion.div className="num-card" variants={staggerItem}>
            <h4><Tooltip term="Life Path">Life Path</Tooltip></h4>
            <div className="num-value">{numerologyProfile.core_numbers.life_path.number}</div>
            <p>{numerologyProfile.core_numbers.life_path.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4><Tooltip term="Expression">Expression</Tooltip></h4>
            <div className="num-value">{numerologyProfile.core_numbers.expression.number}</div>
            <p>{numerologyProfile.core_numbers.expression.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4><Tooltip term="Soul Urge">Soul Urge</Tooltip></h4>
            <div className="num-value">{numerologyProfile.core_numbers.soul_urge.number}</div>
            <p>{numerologyProfile.core_numbers.soul_urge.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4><Tooltip term="Personality">Personality</Tooltip></h4>
            <div className="num-value">{numerologyProfile.core_numbers.personality.number}</div>
            <p>{numerologyProfile.core_numbers.personality.meaning}</p>
          </motion.div>
          {numerologyProfile.core_numbers.maturity && (
            <motion.div className="num-card" variants={staggerItem}>
              <h4><Tooltip term="Maturity">Maturity</Tooltip></h4>
              <div className="num-value">{numerologyProfile.core_numbers.maturity.number}</div>
              <p>{numerologyProfile.core_numbers.maturity.meaning}</p>
            </motion.div>
          )}
          <motion.div className="num-card highlight" variants={staggerItem}>
            <h4><Tooltip term="Personal Year">Personal Year</Tooltip></h4>
            <div className="num-value">{numerologyProfile.cycles.personal_year.number}</div>
            <p>{numerologyProfile.cycles.personal_year.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4><Tooltip term="Personal Month">Personal Month</Tooltip></h4>
            <div className="num-value">{numerologyProfile.cycles.personal_month.number}</div>
            <p>{numerologyProfile.cycles.personal_month.meaning}</p>
          </motion.div>
          <motion.div className="num-card" variants={staggerItem}>
            <h4><Tooltip term="Personal Day">Personal Day</Tooltip></h4>
            <div className="num-value">{numerologyProfile.cycles.personal_day.number}</div>
            <p>{numerologyProfile.cycles.personal_day.meaning}</p>
          </motion.div>
          {numerologyProfile.pinnacles && numerologyProfile.pinnacles.length > 0 && (
            <motion.div className="num-card wide" variants={staggerItem}>
              <h4><Tooltip term="Life Pinnacles">Life Pinnacles</Tooltip></h4>
              <div className="pinnacles-row">
                {numerologyProfile.pinnacles.map((p, i) => (
                  <div key={i} className="pinnacle" title={`Pinnacle ${i + 1}: Major life phase`}>
                    <span className="pinnacle-num">{p.number}</span>
                    <span className="pinnacle-label">Phase {i + 1}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
          {numerologyProfile.challenges && numerologyProfile.challenges.length > 0 && (
            <motion.div className="num-card wide" variants={staggerItem}>
              <h4><Tooltip term="Life Challenges">Life Challenges</Tooltip></h4>
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
