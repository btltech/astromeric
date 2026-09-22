import React from 'react';
import { DocumentMeta } from '../components/DocumentMeta';
import { getRouteMeta } from '../seo/routeMeta';
import './PrivacyPolicy.css';

export function PrivacyPolicy() {
  const currentYear = new Date().getFullYear();
  const lastUpdated = '2026-09-22';

  return (
    <>
      <DocumentMeta
        title={getRouteMeta('/privacy-policy').title}
        description={getRouteMeta('/privacy-policy').description}
        robots="index, follow"
      />

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
                to generate charts, numerology, and readings. In the iOS app, profiles are kept on
                your device and birth details are sent to our servers only to calculate each result.
              </li>
              <li>
                <strong>Website account (optional):</strong> If you create an account on the
                website, we store your email address, a hashed password, and an internal user ID,
                along with the profiles and readings you save while signed in. The iOS app does not
                use accounts.
              </li>
              <li>
                <strong>Journal entries (optional):</strong> In the iOS app, journal entries are
                stored on your device. On the website, entries you save while signed in are stored
                on our servers.
              </li>
              <li>
                <strong>Friends and partners:</strong> Profiles you add for other people (name,
                relationship type, and birth details) for compatibility and Cosmic Circle features
                are stored on our servers. Please only add people who are happy for you to do so.
              </li>
              <li>
                <strong>Calendar (iOS, optional):</strong> If you allow calendar access, the app
                reads upcoming events on your device. Event titles and details are never sent to us;
                see Section 4 for what the Cosmic Guide receives.
              </li>
              <li>
                <strong>Photos (iOS, optional):</strong> Add-only access, used only when you choose
                to save a reading card to your photo library.
              </li>
              <li>
                <strong>Health data:</strong> The iOS app does not access Apple Health (HealthKit)
                data.
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
                <strong>Notifications (iOS):</strong> Reminders are scheduled and shown by your
                device. The Apple Push Notification token stays on the device and is never sent to
                our backend.
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
              We do not sell your personal information. We share information with service providers
              that help us operate the service: Railway hosts our API and database, and Cloudflare
              hosts the website.
            </p>
            <p>
              <strong>Cosmic Guide (iOS app):</strong> When you ask the Cosmic Guide a question, the
              app sends your question, your recent chat messages, your profile name and birth
              details (masked if you turn on Hide Sensitive Details), your chart positions, excerpts
              of up to three matching journal entries, the names and relationship types of friends
              you have saved, and, if you turn on calendar context, the day and time of day of
              upcoming events (never their titles or details). Our server writes the answer itself:
              Cosmic Guide requests are not passed to a third-party AI provider, and we do not store
              the conversations. The same applies to the website.
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
              <a href="mailto:privacy@astromeric.app">privacy@astromeric.app</a> with &quot;Privacy
              Request&quot; in the subject line. We will respond within 30 days.
            </p>
          </section>

          <section id="retention">
            <h2>7. Retention &amp; Deletion</h2>
            <p>
              We keep server-stored data (website accounts and the profiles, readings, and journal
              entries saved to them; and friend and partner profiles) until you ask us to delete it
              or, for accounts, until the account is deleted. To delete a website account or any
              server-stored data, email{' '}
              <a href="mailto:privacy@astromeric.app">privacy@astromeric.app</a> and we will delete
              it within 30 days. We do not keep Cosmic Guide conversations. Data stored on your
              device (such as iOS profiles and journal entries) can be removed by deleting those
              items in the app or uninstalling the app.
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
                Email: <a href="mailto:privacy@astromeric.app">privacy@astromeric.app</a>
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
