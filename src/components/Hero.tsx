import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import './Hero.css';

export function Hero() {
  return (
    <section className="hero">
      <motion.div
        className="hero-content"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <h1 className="hero-title">
          Discover Your <span className="highlight">Cosmic Blueprint</span>
        </h1>

        <p className="hero-subtitle">
          AI-powered astrology & numerology to unlock your celestial potential and navigate
          life&apos;s cosmic rhythms
        </p>

        <div className="hero-features">
          <motion.div
            className="feature"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <span className="feature-icon">✨</span>
            <span>Personalized Charts</span>
          </motion.div>

          <motion.div
            className="feature"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <span className="feature-icon">🔮</span>
            <span>Daily Guidance</span>
          </motion.div>

          <motion.div
            className="feature"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
          >
            <span className="feature-icon">🌙</span>
            <span>Real-time Transits</span>
          </motion.div>
        </div>

        <motion.div
          className="hero-cta"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <Link to="/reading" className="btn btn-primary">
            Generate Your Chart
          </Link>
          <Link to="/learn" className="btn btn-outline">
            Learn More
          </Link>
        </motion.div>

        <p className="hero-cta-text">Free • No signup required • Instant results</p>
      </motion.div>

      <motion.div
        className="hero-visualization"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="cosmic-orb">
          <div className="orb-ring"></div>
          <div className="orb-ring"></div>
          <div className="orb-ring"></div>
        </div>
      </motion.div>
    </section>
  );
}
