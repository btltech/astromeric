import React from 'react';
import { Helmet } from 'react-helmet';
import './CookiePolicy.css';

export function CookiePolicy() {
  return (
    <>
      <Helmet>
        <title>Cookie Policy - Astromeric</title>
        <meta
          name="description"
          content="Understand how Astromeric uses cookies and tracking technologies."
        />
        <meta name="robots" content="index, follow" />
      </Helmet>

      <main className="cookie-policy-container">
        <header className="policy-header">
          <h1>🍪 Cookie Policy</h1>
          <p className="last-updated">Last updated: {new Date().toLocaleDateString()}</p>
        </header>

        <nav className="policy-toc">
          <h2>Quick Navigation</h2>
          <ul>
            <li>
              <a href="#what-are-cookies">What Are Cookies?</a>
            </li>
            <li>
              <a href="#cookies-used">Cookies We Use</a>
            </li>
            <li>
              <a href="#managing-cookies">Managing Cookies</a>
            </li>
            <li>
              <a href="#third-party">Third-Party Cookies</a>
            </li>
            <li>
              <a href="#do-not-track">Do Not Track</a>
            </li>
          </ul>
        </nav>

        <article className="policy-content">
          <section id="what-are-cookies">
            <h2>1. What Are Cookies?</h2>
            <p>
              Cookies are small files stored on your device that allow websites to recognize and
              remember your preferences, login information, and browsing behavior. They can be
              &quot;persistent&quot; (stored until you delete them) or &quot;session&quot; (deleted
              when you close your browser).
            </p>
          </section>

          <section id="cookies-used">
            <h2>2. Cookies We Use</h2>

            <h3>2.1 Essential Cookies (Required)</h3>
            <p>
              These cookies are necessary for the website to function properly. They cannot be
              disabled without affecting site functionality.
            </p>
            <table className="cookie-table">
              <thead>
                <tr>
                  <th>Cookie Name</th>
                  <th>Purpose</th>
                  <th>Expiration</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>session-id</td>
                  <td>Maintains your login session</td>
                  <td>Session</td>
                </tr>
                <tr>
                  <td>csrf-token</td>
                  <td>Protects against CSRF attacks</td>
                  <td>Session</td>
                </tr>
                <tr>
                  <td>theme-preference</td>
                  <td>Remembers your theme choice (light/dark)</td>
                  <td>1 year</td>
                </tr>
                <tr>
                  <td>language-preference</td>
                  <td>Stores your language selection</td>
                  <td>1 year</td>
                </tr>
                <tr>
                  <td>cookie-consent</td>
                  <td>Records your cookie preferences</td>
                  <td>1 year</td>
                </tr>
              </tbody>
            </table>

            <h3>2.2 Analytics Cookies (Optional)</h3>
            <p>
              These cookies help us understand how users interact with our site, allowing us to
              improve features and user experience. You can disable these through our cookie
              preferences.
            </p>
            <table className="cookie-table">
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Cookies</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Google Analytics</td>
                  <td>_ga, _gat, _gid</td>
                  <td>Track user sessions and page views</td>
                </tr>
                <tr>
                  <td>Mixpanel</td>
                  <td>mp_*, mixpanel_</td>
                  <td>Analyze user events and funnels</td>
                </tr>
                <tr>
                  <td>Cloudflare Analytics</td>
                  <td>__cf_bm</td>
                  <td>Measure site performance and security</td>
                </tr>
              </tbody>
            </table>

            <h3>2.3 Marketing Cookies (Optional)</h3>
            <p>
              These cookies enable personalized advertising and conversion tracking across
              platforms. You can disable these through our cookie preferences.
            </p>
            <table className="cookie-table">
              <thead>
                <tr>
                  <th>Service</th>
                  <th>Cookies</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Facebook Pixel</td>
                  <td>_fbp, act, c_user</td>
                  <td>Track conversions and show targeted ads</td>
                </tr>
                <tr>
                  <td>Google Ads</td>
                  <td>NID, Conversion</td>
                  <td>Track ad conversions and personalize ads</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section id="managing-cookies">
            <h2>3. Managing Your Cookies</h2>

            <h3>3.1 Using Our Cookie Consent Banner</h3>
            <p>
              When you first visit Astromeric, you&apos;ll see our cookie consent banner. You can:
            </p>
            <ul>
              <li>
                <strong>Accept All:</strong> Enable all optional cookies
              </li>
              <li>
                <strong>Reject All:</strong> Disable all optional cookies (essentials remain
                enabled)
              </li>
              <li>
                <strong>Save Preferences:</strong> Choose exactly which types of cookies to allow
              </li>
            </ul>

            <h3>3.2 Browser Cookie Settings</h3>
            <p>You can also manage cookies through your browser:</p>
            <ul>
              <li>
                <strong>Chrome:</strong> Settings → Privacy and Security → Cookies and other site
                data
              </li>
              <li>
                <strong>Firefox:</strong> Settings → Privacy & Security → Cookies and Site Data
              </li>
              <li>
                <strong>Safari:</strong> Preferences → Privacy → Cookies and Website Data
              </li>
              <li>
                <strong>Edge:</strong> Settings → Privacy, search, and services → Clear browsing
                data
              </li>
            </ul>

            <h3>3.3 Disabling Cookies</h3>
            <p>
              While you can disable cookies in your browser, please note that some features of
              Astromeric may not function properly without essential cookies enabled.
            </p>
          </section>

          <section id="third-party">
            <h2>4. Third-Party Cookies & Services</h2>

            <h3>4.1 Third-Party Analytics</h3>
            <p>
              We use third-party services to analyze traffic and usage. These services may set their
              own cookies:
            </p>
            <ul>
              <li>
                <strong>Google Analytics:</strong>{' '}
                <a
                  href="https://policies.google.com/technologies/cookies"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Learn more
                </a>
              </li>
              <li>
                <strong>Cloudflare:</strong>{' '}
                <a
                  href="https://www.cloudflare.com/privacypolicy/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Learn more
                </a>
              </li>
            </ul>

            <h3>4.2 Third-Party Advertising</h3>
            <p>
              We may allow third-party advertising networks to set cookies on our site. These
              services comply with their own privacy policies:
            </p>
            <ul>
              <li>
                <strong>Facebook:</strong>{' '}
                <a
                  href="https://www.facebook.com/policies/cookies/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Learn more
                </a>
              </li>
              <li>
                <strong>Google Ads:</strong>{' '}
                <a
                  href="https://policies.google.com/technologies/ads"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Learn more
                </a>
              </li>
            </ul>

            <h3>4.3 Opt-Out Options</h3>
            <p>You can opt-out of interest-based advertising from these providers:</p>
            <ul>
              <li>
                <a
                  href="https://www.aboutads.info/choices/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Digital Advertising Alliance (DAA)
                </a>
              </li>
              <li>
                <a
                  href="https://optout.networkadvertising.org/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Network Advertising Initiative (NAI)
                </a>
              </li>
            </ul>
          </section>

          <section id="do-not-track">
            <h2>5. Do Not Track Signals</h2>
            <p>
              Some browsers include a &quot;Do Not Track&quot; feature. Currently, there is no
              industry standard for recognizing Do Not Track signals, and we do not respond to such
              signals. However, you can use the other methods described in this policy to control
              cookies.
            </p>
          </section>

          <section className="policy-contact">
            <h2>Questions About Our Cookie Policy?</h2>
            <p>
              If you have questions or concerns about our use of cookies, please contact us at{' '}
              <a href="mailto:privacy@astromeric.com">privacy@astromeric.com</a>.
            </p>
          </section>

          <footer className="policy-footer">
            <p>
              © {new Date().getFullYear()} Astromeric, Inc. All rights reserved. This policy is
              subject to change at any time. We recommend reviewing this policy periodically for
              updates.
            </p>
          </footer>
        </article>
      </main>
    </>
  );
}
