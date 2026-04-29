import React from 'react';
import { Helmet } from 'react-helmet';
import './PrivacyPolicy.css';

export function PrivacyPolicy() {
  const currentYear = new Date().getFullYear();
  const lastUpdated = '2026-02-04';

  return (
    <>
      <Helmet>
        <title>Privacy Policy - Astromeric</title>
        <meta
          name="description"
          content="Learn how Astromeric collects, uses, and protects your personal data."
        />
        <meta name="robots" content="index, follow" />
      </Helmet>

      <main className="privacy-policy-container">
        <header className="policy-header">
          <h1>Privacy Policy</h1>
          <p className="last-updated">Last updated: {lastUpdated}</p>
        </header>

        <nav className="policy-toc">
          <h2>Quick Navigation</h2>
          <ul>
            <li>
              <a href="#introduction">Introduction</a>
            </li>
            <li>
              <a href="#information-collection">Information Collection</a>
            </li>
            <li>
              <a href="#information-use">How We Use Information</a>
            </li>
            <li>
              <a href="#sharing">Sharing</a>
            </li>
            <li>
              <a href="#security">Data Security</a>
            </li>
            <li>
              <a href="#rights">Your Rights</a>
            </li>
            <li>
              <a href="#retention">Retention & Deletion</a>
            </li>
            <li>
              <a href="#contact">Contact Us</a>
            </li>
          </ul>
        </nav>

        <article className="policy-content">
          <section id="introduction">
            <h2>1. Introduction</h2>
            <p>
              Astromeric (&quot;we,&quot; &quot;us,&quot; or &quot;our&quot;) is committed to
              protecting your privacy. This policy explains how we collect, use, and protect
              information when you use our website and iOS app.
            </p>
            <p>
              Please read this Privacy Policy carefully. If you do not agree with our policies and
              practices, please do not use our services.
            </p>
          </section>

          <section id="information-collection">
            <h2>2. Information We Collect</h2>

            <h3>2.1 Information You Provide</h3>
            <ul>
              <li>
                <strong>Profile information:</strong> Name, date of birth, and (if you provide it)
                birth time and birthplace (including latitude/longitude and timezone). This is used
                to generate charts, numerology, and readings.
              </li>
              <li>
                <strong>Account information (optional):</strong> If you create an account, we store
                your email address and an internal user ID. Apple Sign‑In may provide your email
                (sometimes via a private relay address).
              </li>
              <li>
                <strong>Journal entries (optional):</strong> Notes you write in the journal feature
                are stored on-device and may be stored on our servers if you are signed in and use
                server-backed features.
              </li>
              <li>
                <strong>Communications:</strong> Messages, feedback, and support requests you send
                us.
              </li>
            </ul>

            <h3>2.2 Information Collected Automatically</h3>
            <ul>
              <li>
                <strong>Basic technical data:</strong> IP address and basic request metadata needed
                to operate and secure the service (e.g., rate limiting and abuse prevention).
              </li>
              <li>
                <strong>Website storage:</strong> We may store essential preferences (like cookie
                consent) in your browser&apos;s local storage. We do not run advertising trackers by
                default.
              </li>
              <li>
                <strong>Notifications (iOS):</strong> If you enable notifications, the app may
                register an Apple Push Notification token with our backend to deliver alerts.
              </li>
            </ul>
          </section>

          <section id="information-use">
            <h2>3. How We Use Your Information</h2>
            <p>We use collected information for:</p>
            <ul>
              <li>Providing and improving our services</li>
              <li>Creating and managing your account</li>
              <li>Generating charts, readings, numerology, and related outputs</li>
              <li>Providing notifications you request</li>
              <li>Preventing fraud and ensuring security</li>
              <li>Complying with legal obligations</li>
            </ul>
          </section>

          <section id="sharing">
            <h2>4. Sharing</h2>
            <p>
              We do not sell your personal information. We may share information with service
              providers that help us operate the app (for example hosting providers). When you use
              AI explanations (if available), the content you request to explain may be processed by
              an AI provider to generate a response.
            </p>
          </section>

          <section id="security">
            <h2>5. Data Security</h2>
            <p>We use reasonable security measures including:</p>
            <ul>
              <li>HTTPS encryption for all data in transit</li>
              <li>Strict access controls and authentication</li>
              <li>Secure password hashing for password-based accounts</li>
            </ul>
            <p>
              However, no security system is completely impenetrable. We cannot guarantee absolute
              security of your information.
            </p>
          </section>

          <section id="rights">
            <h2>6. Your Privacy Rights</h2>

            <h3>6.1 GDPR Rights (EU Users)</h3>
            <p>If you are located in the EU, you have the right to:</p>
            <ul>
              <li>Access your personal data</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion (&quot;right to be forgotten&quot;)</li>
              <li>Restrict processing of your data</li>
              <li>Receive your data in a portable format</li>
              <li>Object to processing</li>
              <li>Withdraw consent at any time</li>
            </ul>

            <h3>6.2 CCPA Rights (California Users)</h3>
            <p>If you are a California resident, you have the right to:</p>
            <ul>
              <li>Know what personal information is collected</li>
              <li>Know whether personal information is sold or shared</li>
              <li>Delete personal information collected from you</li>
              <li>Opt-out of the sale or sharing of your personal information</li>
              <li>Non-discrimination for exercising your CCPA rights</li>
            </ul>

            <h3>6.3 How to Exercise Your Rights</h3>
            <p>
              To exercise any of these rights, please contact us at{' '}
              <a href="mailto:privacy@astromeric.com">privacy@astromeric.com</a> with &quot;Privacy
              Request&quot; in the subject line. We will respond within 30 days.
            </p>
          </section>

          <section id="retention">
            <h2>7. Retention &amp; Deletion</h2>
            <p>
              We keep server-stored data for as long as your account is active or as needed to
              provide services. You can delete your account from within the iOS app (Profile →
              Account → Delete Account) which removes your server account and associated
              profiles/readings. Data stored locally on your device (like local profiles and journal
              entries) can be removed by deleting those items in-app or uninstalling the app.
            </p>
          </section>

          <section id="contact">
            <h2>8. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or our privacy practices, please
              contact us:
            </p>
            <ul>
              <li>
                Email: <a href="mailto:privacy@astromeric.com">privacy@astromeric.com</a>
              </li>
            </ul>
          </section>

          <footer className="policy-footer">
            <p>
              © {currentYear} Astromeric. All rights reserved. This policy may change; we will post
              updates here.
            </p>
          </footer>
        </article>
      </main>
    </>
  );
}
