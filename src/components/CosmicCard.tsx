import React, { useRef } from 'react';
import { toPng } from 'html-to-image';
import { motion } from 'framer-motion';
import { QRCodeSVG } from 'qrcode.react';
import type { PredictionData } from '../types';

interface Props {
  data: PredictionData;
  userName: string;
}

export const CosmicCard: React.FC<Props> = ({ data, userName }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const shareUrl = 'https://astronumeric.com/reading';

  const downloadImage = async () => {
    if (cardRef.current === null) return;
    try {
      const dataUrl = await toPng(cardRef.current, { cacheBust: true });
      const link = document.createElement('a');
      link.download = `cosmic-aura-${userName.toLowerCase()}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error('Failed to generate sharing image', err);
    }
  };

  const sunSign =
    data.sign || data.charts?.natal?.planets?.find((p) => p.name === 'Sun')?.sign || 'Star';
  const moonSign = data.charts?.natal?.planets?.find((p) => p.name === 'Moon')?.sign || 'Shadow';
  const dominantElement = data.element || 'Aether';

  return (
    <div className="cosmic-share-container">
      <div className="cosmic-aura-card" ref={cardRef}>
        <div className="aura-background" data-element={dominantElement}></div>
        <div className="aura-content">
          <header>
            <span className="aura-brand">ASTROMERIC</span>
            <span className="aura-date">
              {new Date().toLocaleDateString(undefined, {
                month: 'long',
                day: 'numeric',
                year: 'numeric',
              })}
            </span>
          </header>

          <main>
            <div className="aura-user-info">
              <h1>{userName}’s Cosmic Aura</h1>
              <p className="aura-subtitle">{data.theme || 'Celestial Alignment'}</p>
            </div>

            <div className="aura-stats-grid">
              <div className="aura-stat">
                <span className="stat-label">SUN SIGN</span>
                <span className="stat-value">{sunSign}</span>
              </div>
              <div className="aura-stat">
                <span className="stat-label">MOON SIGN</span>
                <span className="stat-value">{moonSign}</span>
              </div>
              <div className="aura-stat">
                <span className="stat-label">LUCKY NUMBERS</span>
                <div className="stat-numbers">
                  {data.lucky_numbers?.slice(0, 3).map((n: number) => (
                    <span key={n} className="mini-hex">
                      {n}
                    </span>
                  ))}
                </div>
              </div>
              <div className="aura-stat">
                <span className="stat-label">VIBE</span>
                <span className="stat-value">{data.mood || 'Intense'}</span>
              </div>
            </div>

            <div className="aura-quote">
              <p>
                &quot;
                {data.summary?.headline ||
                  (data.advice
                    ? data.advice.slice(0, 100) + '...'
                    : 'Your cosmic path is unfolding with purpose.')}
                &quot;
              </p>
            </div>
          </main>

          <footer>
            <div className="aura-qr-block">
              <div className="aura-qr-code" aria-hidden="true">
                <QRCodeSVG
                  value={shareUrl}
                  size={56}
                  level="M"
                  includeMargin
                  bgColor="transparent"
                  fgColor="#08101f"
                />
              </div>
              <div className="aura-qr-copy">
                <span className="aura-qr-label">Scan to start your reading</span>
                <span className="aura-qr-link">astronumeric.com/reading</span>
              </div>
            </div>
            <div className="aura-url">astronumeric.com</div>
          </footer>
        </div>
      </div>

      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={downloadImage}
        className="btn-aura-share"
      >
        <span>📸 Share Your Aura</span>
      </motion.button>
    </div>
  );
};
