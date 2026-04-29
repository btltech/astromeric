import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-bottom" style={{ textAlign: 'center', padding: '2rem 1rem' }}>
        <p style={{ color: 'rgba(255,255,255,0.35)', fontSize: '0.85rem', margin: '0 0 0.5rem' }}>
          &copy; {currentYear} AstroNumeric. All rights reserved.
        </p>
        <nav style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link
            to="/privacy-policy"
            style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', textDecoration: 'none' }}
          >
            Privacy Policy
          </Link>
          <Link
            to="/terms"
            style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', textDecoration: 'none' }}
          >
            Terms of Service
          </Link>
          <Link
            to="/cookie-policy"
            style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', textDecoration: 'none' }}
          >
            Cookie Policy
          </Link>
          <a
            href="mailto:support@astromeric.com"
            style={{ color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem', textDecoration: 'none' }}
          >
            Contact
          </a>
        </nav>
      </div>
    </footer>
  );
}
