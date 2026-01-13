import React from 'react';
import { useTranslation } from 'react-i18next';
import { Helmet } from 'react-helmet';
import './PrivacyPolicy.css';

export function PrivacyPolicy() {
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

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
          <p className="last-updated">Last updated: {new Date().toLocaleDateString()}</p>
        </header>

        <nav className="policy-toc">
          <h2>Quick Navigation</h2>
          <ul>
            <li><a href="#introduction">Introduction</a></li>
            <li><a href="#information-collection">Information Collection</a></li>
            <li><a href="#information-use">How We Use Information</a></li>
            <li><a href="#cookies">Cookies & Tracking</a></li>
            <li><a href="#security">Data Security</a></li>
            <li><a href="#rights">Your Rights</a></li>
            <li><a href="#contact">Contact Us</a></li>
          </ul>
        </nav>

        <article className="policy-content">
          <section id="introduction">
            <h2>1. Introduction</h2>
            <p>
              Astromeric ("we," "us," "our," or "Company") is committed to protecting your privacy. This Privacy
              Policy explains how we collect, use, disclose, and safeguard your information when you visit our
              website astromeric.com and our applications.
            </p>
            <p>
              Please read this Privacy Policy carefully. If you do not agree with our policies and practices, please
              do not use our services.
            </p>
          </section>

          <section id="information-collection">
            <h2>2. Information We Collect</h2>

            <h3>2.1 Information You Provide</h3>
            <ul>
              <li><strong>Account Information:</strong> Name, email address, date of birth, birth time, birth location</li>
              <li><strong>Payment Information:</strong> Processed securely through third-party payment providers</li>
              <li><strong>Communications:</strong> Messages, feedback, and support inquiries</li>
              <li><strong>Profile Data:</strong> Saved charts, readings, and preferences</li>
            </ul>

            <h3>2.2 Information Collected Automatically</h3>
            <ul>
              <li><strong>Device Information:</strong> IP address, device type, operating system</li>
              <li><strong>Usage Data:</strong> Pages visited, time spent, features used, clicks and interactions</li>
              <li><strong>Location Data:</strong> Approximate location derived from IP address (if consent given)</li>
              <li><strong>Cookies & Pixels:</strong> Persistent and session cookies, web beacons, local storage</li>
            </ul>
          </section>

          <section id="information-use">
            <h2>3. How We Use Your Information</h2>
            <p>We use collected information for:</p>
            <ul>
              <li>Providing and improving our services</li>
              <li>Creating and managing your account</li>
              <li>Processing transactions and sending related information</li>
              <li>Sending promotional communications (with your consent)</li>
              <li>Analyzing usage patterns to enhance user experience</li>
              <li>Complying with legal obligations</li>
              <li>Preventing fraud and ensuring security</li>
            </ul>
          </section>

          <section id="cookies">
            <h2>4. Cookies & Tracking Technologies</h2>

            <h3>4.1 Types of Cookies</h3>
            <p>We use three categories of cookies:</p>
            <ul>
              <li>
                <strong>Essential Cookies:</strong> Required for site functionality (authentication, preferences)
              </li>
              <li>
                <strong>Analytics Cookies:</strong> Help us understand user behavior (Google Analytics, Mixpanel)
              </li>
              <li>
                <strong>Marketing Cookies:</strong> Enable personalized advertising (Facebook Pixel, Google Ads)
              </li>
            </ul>

            <h3>4.2 Cookie Management</h3>
            <p>
              You can manage cookie preferences through our cookie consent banner. You can also disable cookies in
              your browser settings, though this may affect functionality.
            </p>

            <h3>4.3 Third-Party Pixels</h3>
            <p>We use pixels from third-party services including:</p>
            <ul>
              <li>Google Analytics (analytics@google.com)</li>
              <li>Facebook Pixel (facebook.com)</li>
              <li>Cloudflare Web Analytics</li>
            </ul>
          </section>

          <section id="security">
            <h2>5. Data Security</h2>
            <p>
              We implement industry-standard security measures including:
            </p>
            <ul>
              <li>HTTPS encryption for all data in transit</li>
              <li>AES-256 encryption for sensitive data at rest</li>
              <li>Regular security audits and penetration testing</li>
              <li>Strict access controls and authentication</li>
              <li>Secure password policies and two-factor authentication</li>
            </ul>
            <p>
              However, no security system is completely impenetrable. We cannot guarantee absolute security of your
              information.
            </p>
          </section>

          <section id="rights">
            <h2>6. Your Privacy Rights</h2>

            <h3>6.1 GDPR Rights (EU Users)</h3>
            <p>If you are located in the EU, you have the right to:</p>
            <ul>
              <li>Access your personal data</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion ("right to be forgotten")</li>
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
              <a href="mailto:privacy@astromeric.com">privacy@astromeric.com</a> with "Privacy Request" in the
              subject line. We will respond within 30 days.
            </p>
          </section>

          <section id="contact">
            <h2>7. Contact Us</h2>
            <p>
              If you have questions about this Privacy Policy or our privacy practices, please contact us:
            </p>
            <ul>
              <li>Email: <a href="mailto:privacy@astromeric.com">privacy@astromeric.com</a></li>
              <li>Address: Astromeric, Inc., Privacy Team</li>
            </ul>
          </section>

          <footer className="policy-footer">
            <p>
              © {currentYear} Astromeric, Inc. All rights reserved. This policy is subject to change at any time.
              We will notify you of significant changes via email.
            </p>
          </footer>
        </article>
      </main>
    </>
  );
}
