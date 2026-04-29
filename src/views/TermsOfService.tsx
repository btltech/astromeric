import React from 'react';
import { Helmet } from 'react-helmet';

import './PrivacyPolicy.css';

export function TermsOfService() {
  const currentYear = new Date().getFullYear();

  return (
    <>
      <Helmet>
        <title>Terms of Service - Astromeric</title>
        <meta name="description" content="Terms of Service for Astromeric." />
        <meta name="robots" content="index, follow" />
      </Helmet>

      <main className="privacy-policy-container">
        <header className="policy-header">
          <h1>Terms of Service</h1>
          <p className="last-updated">Last updated: {new Date().toLocaleDateString()}</p>
        </header>

        <article className="policy-content">
          <section>
            <h2>1. Entertainment-only</h2>
            <p>
              Astromeric provides astrology, numerology, tarot, and related insights for{' '}
              <strong>entertainment and personal reflection</strong>. It is not medical, legal, or
              financial advice.
            </p>
          </section>

          <section>
            <h2>2. Your responsibility</h2>
            <p>
              You are responsible for how you use the app. If you need professional help or advice,
              consult a qualified professional.
            </p>
          </section>

          <section>
            <h2>3. Accounts</h2>
            <p>
              Creating an account is optional. If you create an account, you can request deletion
              from within the iOS app (Profile → Account → Delete Account) or by contacting us.
            </p>
          </section>

          <section>
            <h2>4. Availability</h2>
            <p>
              We may update, change, or discontinue features at any time. We do not guarantee
              uninterrupted availability.
            </p>
          </section>

          <section>
            <h2>5. Contact</h2>
            <p>
              Questions? Email <a href="mailto:privacy@astromeric.com">privacy@astromeric.com</a>.
            </p>
          </section>

          <footer className="policy-footer">
            <p>© {currentYear} Astromeric. All rights reserved.</p>
          </footer>
        </article>
      </main>
    </>
  );
}
