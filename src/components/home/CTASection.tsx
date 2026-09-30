import React from 'react';

import { SUPPORT_EMAIL } from '../../config/appLinks';
import { AppDownloadButton } from '../AppDownloadButton';

const storeButtonStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: '8px',
  padding: '12px 20px',
  borderRadius: '12px',
  textDecoration: 'none',
  fontSize: '0.88rem',
  fontWeight: 700,
};

type CTASectionProps = {
  eyebrow: string;
  title: string;
  description: string;
  primaryLabel: string;
  primaryTo: string;
  secondaryLabel: string;
  secondaryTo: string;
};

export function CTASection(_props: CTASectionProps) {
  return (
    <section
      className="cta-section home-premium__panel"
      style={{
        display: 'grid',
        gridTemplateColumns: 'auto 1fr auto',
        gap: '32px',
        alignItems: 'center',
        padding: '40px',
        background:
          'radial-gradient(circle at 100% 0%, rgba(76, 207, 255, 0.12), transparent 45%), linear-gradient(180deg, rgba(13, 23, 34, 0.98), rgba(7, 16, 24, 0.95))',
        border: '1px solid rgba(118, 148, 181, 0.22)',
        borderRadius: '24px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Premium App Icon Mockup */}
      <div
        className="cta-app-icon"
        style={{
          width: '80px',
          height: '80px',
          borderRadius: '18px',
          background: 'linear-gradient(135deg, #1b1b3a, #0b0b18)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          boxShadow: '0 12px 24px rgba(0, 0, 0, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.05)',
          display: 'grid',
          placeItems: 'center',
          flexShrink: 0,
        }}
      >
        {/* Celestial Star SVG */}
        <svg
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 2L14.8 8.4L21.8 9.8L17 14.8L18.2 21.8L12 18.2L5.8 21.8L7 14.8L2.2 9.8L9.2 8.4L12 2Z"
            fill="url(#starGrad)"
            stroke="rgba(255,255,255,0.2)"
            strokeWidth="0.5"
          />
          <defs>
            <linearGradient
              id="starGrad"
              x1="2"
              y1="2"
              x2="22"
              y2="22"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stopColor="#4ccfff" />
              <stop offset="100%" stopColor="#2f87ff" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Copy content */}
      <div className="cta-section__copy" style={{ maxWidth: '640px' }}>
        <span
          className="cta-section__eyebrow"
          style={{
            display: 'block',
            fontSize: '0.72rem',
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            color: 'rgba(255, 201, 138, 0.92)',
            fontWeight: 700,
            marginBottom: '8px',
          }}
        >
          Mobile Companion
        </span>
        <h2
          className="cta-section__title"
          style={{
            margin: '0 0 10px',
            fontSize: 'clamp(1.4rem, 2.5vw, 1.8rem)',
            fontFamily: 'var(--font-display)',
            color: '#f7fbff',
            letterSpacing: '-0.04em',
            lineHeight: 1.2,
          }}
        >
          AstroNumeric for iOS & Android
        </h2>
        <p
          className="cta-section__description"
          style={{
            margin: 0,
            fontSize: '0.92rem',
            color: 'rgba(233, 241, 248, 0.78)',
            lineHeight: 1.6,
          }}
        >
          Take your daily timing, birth chart, and cycles with you. Features high-resolution home
          widgets, daily push notifications, and full offline calculations powered by Swiss
          Ephemeris.
        </p>
        <div style={{ marginTop: '14px', fontSize: '0.82rem', color: 'rgba(233, 241, 248, 0.45)' }}>
          Support & feedback:{' '}
          <a href={`mailto:${SUPPORT_EMAIL}`} style={{ color: '#4ccfff', textDecoration: 'none' }}>
            {SUPPORT_EMAIL}
          </a>
        </div>
      </div>

      {/* App Store Badge CTA */}
      <div
        className="cta-section__actions"
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          alignItems: 'stretch',
          justifyContent: 'center',
          minWidth: '160px',
        }}
      >
        <AppDownloadButton
          store="app-store"
          className="home-button home-button--primary"
          style={storeButtonStyle}
        />
        <AppDownloadButton
          store="google-play"
          className="home-button home-button--secondary"
          style={storeButtonStyle}
        />
      </div>

      {/* Styled Responsive overrides using inline media queries in head */}
      <style
        dangerouslySetInnerHTML={{
          __html: `
        @media (max-width: 1024px) {
          .cta-section {
            grid-template-columns: 1fr !important;
            text-align: center !important;
            gap: 20px !important;
          }
          .cta-app-icon {
            margin: 0 auto !important;
          }
          .cta-section__copy {
            margin: 0 auto !important;
          }
          .cta-section__actions {
            width: 100% !important;
            max-width: 280px !important;
            margin: 0 auto !important;
          }
        }
      `,
        }}
      />
    </section>
  );
}

export default CTASection;
