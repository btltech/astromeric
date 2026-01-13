import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>Astromeric</h3>
          <p>AI-powered astrology & numerology for your cosmic blueprint</p>
          <div className="footer-socials">
            <a
              href="https://twitter.com"
              aria-label="Twitter"
              target="_blank"
              rel="noopener noreferrer"
            >
              𝕏
            </a>
            <a
              href="https://instagram.com"
              aria-label="Instagram"
              target="_blank"
              rel="noopener noreferrer"
            >
              📷
            </a>
            <a
              href="https://facebook.com"
              aria-label="Facebook"
              target="_blank"
              rel="noopener noreferrer"
            >
              f
            </a>
          </div>
        </div>

        <div className="footer-section">
          <h4>Navigation</h4>
          <nav className="footer-nav">
            <Link to="/">Home</Link>
            <Link to="/about">About</Link>
            <Link to="/learn">Learn</Link>
            <Link to="/auth">Sign In</Link>
          </nav>
        </div>

        <div className="footer-section">
          <h4>Legal</h4>
          <nav className="footer-nav">
            <Link to="/privacy-policy">Privacy Policy</Link>
            <Link to="/cookie-policy">Cookie Policy</Link>
            <a href="mailto:privacy@astromeric.com">Contact</a>
          </nav>
        </div>

        <div className="footer-section">
          <h4>Support</h4>
          <nav className="footer-nav">
            <a href="mailto:support@astromeric.com">Email Support</a>
            <a href="https://astromeric.com/faq">FAQ</a>
            <a href="https://astromeric.com/status">Status Page</a>
          </nav>
        </div>
      </div>

      <div className="footer-bottom">
        <p>&copy; {currentYear} Astromeric, Inc. All rights reserved.</p>
        <p className="footer-tagline">
          Discover your cosmic blueprint through AI-powered astrology.
        </p>
      </div>
    </footer>
  );
}
