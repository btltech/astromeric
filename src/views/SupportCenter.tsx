import React from 'react';
import { Link } from 'react-router-dom';
import { DocumentMeta } from '../components/DocumentMeta';
import './PrivacyPolicy.css';

const supportEmail = 'support@astromeric.app';
const privacyEmail = 'privacy@astromeric.app';

export function SupportCenter() {
  const currentYear = new Date().getFullYear();

  return (
    <>
      <DocumentMeta
        title="Support - AstroNumeric"
        description="Support information for AstroNumeric on iOS, Android, and web."
        robots="index, follow"
      />

      <main className="privacy-policy-container">
        <header className="policy-header">
          <h1>Support</h1>
          <p className="last-updated">Last updated: 2026-05-09</p>
        </header>

        <nav className="policy-toc">
          <h2>Quick Navigation</h2>
          <ul>
            <li>
              <a href="#contact-support">Contact support</a>
            </li>
            <li>
              <a href="#privacy-requests">Privacy requests</a>
            </li>
            <li>
              <a href="#self-serve">Self-serve help</a>
            </li>
          </ul>
        </nav>

        <article className="policy-content">
          <section id="contact-support">
            <h2>1. Contact support</h2>
            <p>
              AstroNumeric support is available for iOS, Android, and web app questions. If you
              need help with a bug, billing issue, account problem, or feature question, email{' '}
              <a href={`mailto:${supportEmail}`}>{supportEmail}</a>.
            </p>
            <p>
              When you write in, include the device type, OS version, app version, and the steps
              that led to the problem so the issue can be reproduced quickly.
            </p>
          </section>

          <section id="privacy-requests">
            <h2>2. Privacy requests</h2>
            <p>
              For privacy questions, deletion requests, or concerns about backend-held data, email{' '}
              <a href={`mailto:${privacyEmail}`}>{privacyEmail}</a>.
            </p>
            <p>
              The full privacy policy is available at <Link to="/privacy-policy">/privacy-policy</Link>,
              and the service terms are available at <Link to="/terms">/terms</Link>.
            </p>
          </section>

          <section id="self-serve">
            <h2>3. Self-serve help</h2>
            <ul>
              <li>
                Visit <Link to="/privacy-policy">Privacy Policy</Link> for data handling,
                retention, and deletion details.
              </li>
              <li>
                Visit <Link to="/terms">Terms of Service</Link> for service usage and account
                expectations.
              </li>
              <li>
                Visit <Link to="/cookie-policy">Cookie Policy</Link> for browser storage and
                consent details on the web app.
              </li>
            </ul>
          </section>

          <footer className="policy-footer">
            <p>© {currentYear} AstroNumeric. All rights reserved.</p>
          </footer>
        </article>
      </main>
    </>
  );
}

export default SupportCenter;