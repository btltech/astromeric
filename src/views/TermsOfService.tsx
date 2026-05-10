import React from 'react';
import { Link } from 'react-router-dom';
import { DocumentMeta } from '../components/DocumentMeta';

import './PrivacyPolicy.css';

export function TermsOfService() {
  const currentYear = new Date().getFullYear();

  return (
    <>
      <DocumentMeta
        title="Terms of Service — AstroNumeric"
        description="Terms of service governing your use of AstroNumeric on web, iOS, and Android."
        robots="index, follow"
      />

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
              Questions? Visit <Link to="/support">/support</Link> or email{' '}
              <a href="mailto:privacy@astromeric.app">privacy@astromeric.app</a>.
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
