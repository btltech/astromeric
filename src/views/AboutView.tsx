import React from 'react';
import { Helmet } from 'react-helmet';
import { motion } from 'framer-motion';
import './AboutView.css';

export function AboutView() {
  return (
    <>
      <Helmet>
        <title>About Astromeric</title>
        <meta
          name="description"
          content="Learn about Astromeric - AI-powered astrology and numerology for your cosmic blueprint."
        />
      </Helmet>

      <main className="about-view">
        <div className="about-header">
          <h1>About Astromeric</h1>
          <p>Bridging ancient wisdom with modern AI</p>
        </div>

        <motion.section
          className="about-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h2>Our Mission</h2>
          <p>
            Astromeric empowers you to understand yourself and navigate life&apos;s journey through
            the fusion of celestial wisdom and advanced artificial intelligence. We believe that
            everyone deserves access to personalized astrological and numerological insights.
          </p>
        </motion.section>

        <motion.section
          className="about-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2>What We Offer</h2>
          <div className="features-grid">
            <div className="feature-card">
              <span className="feature-icon">🌟</span>
              <h3>Natal Charts</h3>
              <p>Discover your complete birth chart and cosmic blueprint instantly</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">📈</span>
              <h3>Real-Time Transits</h3>
              <p>Track planetary movements and their influence on your life daily</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">🔮</span>
              <h3>Daily Guidance</h3>
              <p>Receive personalized daily readings based on cosmic events</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">💑</span>
              <h3>Compatibility</h3>
              <p>Analyze astrological compatibility with loved ones</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">🔢</span>
              <h3>Numerology</h3>
              <p>Explore the mystical meaning behind numbers in your life</p>
            </div>

            <div className="feature-card">
              <span className="feature-icon">🌍</span>
              <h3>3D Planetarium</h3>
              <p>Visualize planets in real-time with our interactive 3D model</p>
            </div>
          </div>
        </motion.section>

        <motion.section
          className="about-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2>Our Technology</h2>
          <p>
            We combine rigorous astronomical calculations using Swiss Ephemeris data with
            cutting-edge AI to deliver accurate, insightful interpretations. Our algorithms
            calculate planetary positions, aspects, and transits with precision, while our AI
            provides personalized guidance tailored to your unique cosmic profile.
          </p>
        </motion.section>

        <motion.section
          className="about-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2>Privacy & Safety</h2>
          <p>
            Your privacy is paramount. We never share your personal data with third parties without
            explicit consent. All birth data is encrypted and stored securely. You maintain complete
            control over your information.
          </p>
          <p>
            Read our <a href="/privacy-policy">Privacy Policy</a> and{' '}
            <a href="/cookie-policy">Cookie Policy</a> to learn more about how we protect your data.
          </p>
        </motion.section>

        <motion.section
          className="about-section contact-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2>Get In Touch</h2>
          <p>Have questions or feedback? We&apos;d love to hear from you!</p>
          <div className="contact-methods">
            <a href="mailto:support@astromeric.com" className="contact-link">
              📧 Email: support@astromeric.com
            </a>
            <a href="mailto:privacy@astromeric.com" className="contact-link">
              🔐 Privacy: privacy@astromeric.com
            </a>
          </div>
        </motion.section>
      </main>
    </>
  );
}
