import React from 'react';

import { AppDownloadButton } from './AppDownloadButton';

/** The Oracle lives in the app; the website shows what it does. */
export function OracleAppShowcase() {
  return (
    <section className="oracle-showcase" aria-labelledby="oracle-showcase-title">
      <span className="product-desk__eyebrow">In the AstroNumeric app</span>
      <h2 id="oracle-showcase-title">🔮 The Oracle</h2>
      <p>
        Ask a yes-or-no question and the Oracle casts a chart for the moment and place you ask it,
        then judges it the classical way, by the horary rules astrologers have used since the 1600s.
      </p>
      <ul className="oracle-showcase__points">
        <li>
          <strong>Reads what you&apos;re asking about.</strong> Love, career, money, travel, home,
          children, friends and wellbeing each point to their own part of the chart.
        </li>
        <li>
          <strong>Shows how it decided.</strong> Which planet stands for you, which for your
          question, whether they meet, and what helps or gets in the way.
        </li>
        <li>
          <strong>Knows when to say wait.</strong> If the sky says the chart isn&apos;t ready to
          judge, it tells you when to ask again.
        </li>
        <li>
          <strong>Private.</strong> The chart is cast on your phone, and your location never leaves
          it.
        </li>
      </ul>
      <div className="oracle-showcase__actions">
        <AppDownloadButton store="app-store" className="btn-primary product-desk__action" />
      </div>
    </section>
  );
}
