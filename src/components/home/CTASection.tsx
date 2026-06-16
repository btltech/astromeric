import React from 'react';

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
          <a
            href="mailto:support@astromeric.com"
            style={{ color: '#4ccfff', textDecoration: 'none' }}
          >
            support@astromeric.com
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
        <a
          href="#app-store-download"
          className="home-button home-button--primary"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '12px 20px',
            borderRadius: '12px',
            textDecoration: 'none',
            fontSize: '0.88rem',
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          {/* Custom SVG App Store Icon */}
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="currentColor"
            style={{ marginTop: '-2px' }}
          >
            <path d="M18.71,19.5C17.88,20.74 17,21.95 15.66,22C14.32,22.05 13.89,21.24 12.37,21.24C10.84,21.24 10.37,21.97 9.1,22C7.79,22.05 6.8,20.68 5.96,19.47C4.25,17 2.94,12.45 4.7,9.39C5.57,7.87 7.13,6.91 8.82,6.88C10.1,6.86 11.32,7.75 12.11,7.75C12.89,7.75 14.37,6.68 15.92,6.84C16.57,6.87 18.39,7.1 19.56,8.82C19.47,8.88 17.39,10.1 17.41,12.63C17.44,15.65 20.06,16.66 20.1,16.67C20.08,16.74 19.67,18.11 18.71,19.5M15.97,4.17C16.63,3.37 17.07,2.28 16.95,1C16,1.04 14.9,1.6 14.24,2.38C13.68,3.04 13.19,4.14 13.34,5.39C14.39,5.47 15.4,4.88 15.97,4.17Z" />
          </svg>
          Get on App Store
        </a>
        <a
          href="#google-play-download"
          className="home-button home-button--secondary"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '12px 20px',
            borderRadius: '12px',
            textDecoration: 'none',
            fontSize: '0.88rem',
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          {/* Custom SVG Google Play Icon */}
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="currentColor"
            style={{ marginTop: '-1px' }}
          >
            <path d="M5,3.14L15.42,13.56L18.43,10.55C19.06,9.92 19.06,8.9 18.43,8.27L15.34,5.18C14.07,3.91 12.02,3.91 10.75,5.18L5,3.14M16.5,14.64L6.07,4.21L3.14,7.14C2.5,7.78 2.5,8.8 3.14,9.43L6.23,12.53C7.5,13.8 9.55,13.8 10.82,12.53L16.5,14.64M11.9,11.38L21.31,20.79C21.94,20.16 21.94,19.14 21.31,18.51L18.22,15.42C16.95,14.15 14.9,14.15 13.63,15.42L11.9,11.38M20.21,22L9.79,11.58L6.78,14.59C6.15,15.22 6.15,16.24 6.78,16.87L9.87,19.96C11.14,21.23 13.19,21.23 14.46,19.96L20.21,22Z" />
          </svg>
          Get on Play Store
        </a>
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
