import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useGlossary } from '../hooks';
import { useStore } from '../store/useStore';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.03,
    },
  },
};

const staggerItem = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
};

export function LearnView() {
  const {
    glossary,
    fetchGlossary,
    loadMoreZodiac,
    loadMoreNumerology,
    hasMoreZodiac,
    hasMoreNumerology,
  } = useGlossary();
  const { loading } = useStore();

  useEffect(() => {
    fetchGlossary();
  }, [fetchGlossary]);

  if (loading && !glossary) {
    return (
      <motion.div className="card" {...fadeIn}>
        <p style={{ textAlign: 'center', color: '#888' }}>Loading glossary...</p>
      </motion.div>
    );
  }

  const zodiacEntries = glossary?.zodiac ? Object.entries(glossary.zodiac) : [];
  const numerologyEntries = glossary?.numerology ? Object.entries(glossary.numerology) : [];

  return (
    <motion.div className="card" {...fadeIn}>
      <h2>📚 Learn</h2>
      {glossary ? (
        <div className="learn-content">
          <div className="learn-section">
            <h3>♈ Zodiac Signs</h3>
            <motion.div
              className="glossary-grid"
              variants={staggerContainer}
              initial="initial"
              animate="animate"
            >
              {zodiacEntries.map(([sign, info]) => {
                const infoRec = info as Record<string, unknown>;
                const symbol = typeof infoRec.symbol === 'string' ? infoRec.symbol : '';
                const dates = typeof infoRec.dates === 'string' ? infoRec.dates : '';
                const elementVal = typeof infoRec.element === 'string' ? infoRec.element : '';
                const modality = typeof infoRec.modality === 'string' ? infoRec.modality : '';
                const description =
                  typeof infoRec.description === 'string' ? infoRec.description : '';
                return (
                  <motion.div
                    key={sign}
                    className="glossary-item"
                    variants={staggerItem}
                    whileHover={{ scale: 1.02, borderColor: 'rgba(136, 192, 208, 0.5)' }}
                  >
                    <h4>
                      {symbol} {sign}
                    </h4>
                    <p className="dates">{dates}</p>
                    <p className="element">
                      {elementVal} • {modality}
                    </p>
                    <p>{description.slice(0, 100)}...</p>
                  </motion.div>
                );
              })}
            </motion.div>
            {hasMoreZodiac && (
              <div className="load-more">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="btn-secondary"
                  onClick={loadMoreZodiac}
                >
                  Load more signs
                </motion.button>
              </div>
            )}
          </div>
          <div className="learn-section">
            <h3>🔢 Life Path Numbers</h3>
            <motion.div
              className="glossary-grid"
              variants={staggerContainer}
              initial="initial"
              animate="animate"
            >
              {numerologyEntries.map(([key, info]) => {
                const infoRec = info as Record<string, unknown>;
                const meaning = typeof infoRec.meaning === 'string' ? infoRec.meaning : undefined;
                const description =
                  typeof infoRec.description === 'string' ? infoRec.description : undefined;
                return (
                  <motion.div
                    key={key}
                    className="glossary-item"
                    variants={staggerItem}
                    whileHover={{ scale: 1.02, borderColor: 'rgba(136, 192, 208, 0.5)' }}
                  >
                    <h4>{key}</h4>
                    <p>{(meaning ?? description ?? '').slice(0, 100)}...</p>
                  </motion.div>
                );
              })}
            </motion.div>
            {hasMoreNumerology && (
              <div className="load-more">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="btn-secondary"
                  onClick={loadMoreNumerology}
                >
                  Load more numbers
                </motion.button>
              </div>
            )}
          </div>
        </div>
      ) : (
        <p style={{ textAlign: 'center', color: '#888' }}>No glossary data available.</p>
      )}
    </motion.div>
  );
}
