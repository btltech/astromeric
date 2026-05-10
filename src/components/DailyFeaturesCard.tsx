import React, { useState, useEffect } from 'react';
import { fetchDailyFeatures, type DailyFeaturesResponse } from '../api/client';
import { FeatureCardSkeleton } from './Skeleton';

interface Props {
  birthDate: string;
  sunSign?: string;
}

const PLANET_SYMBOLS: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
};

export function DailyFeaturesCard({ birthDate, sunSign }: Props) {
  const [features, setFeatures] = useState<DailyFeaturesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    async function loadFeatures() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchDailyFeatures({
          name: 'Guest',
          date_of_birth: birthDate,
          sun_sign: sunSign,
        } as any);
        setFeatures(data);
      } catch (err) {
        console.error('Failed to fetch daily features:', err);
        setError('Could not load your daily cosmic features');
      } finally {
        setLoading(false);
      }
    }

    if (birthDate) {
      loadFeatures();
    }
  }, [birthDate, sunSign]);

  if (loading) {
    return <FeatureCardSkeleton />;
  }

  if (error || !features) {
    return (
      <div className="daily-features-card error">
        <p>{error || 'Unable to load daily features'}</p>
      </div>
    );
  }

  const affirmationText =
    features.affirmation?.text ??
    'The daily signal is still coming into focus. Reopen this card in a moment.';
  const moodForecast = features.mood_forecast;
  const luckyColors = features.lucky_colors;
  const luckyPlanet = features.lucky_planet;
  const retrogradeAlerts = features.retrograde_alerts ?? [];
  const luckyNumbers = features.lucky_numbers ?? [];
  const focusPlanet = luckyPlanet?.planet ?? 'Pending';
  const focusPlanetSymbol = PLANET_SYMBOLS[focusPlanet] || '🌟';

  return (
    <div className="daily-features-card">
      <h3 className="card-title">Your Daily Snapshot</h3>

      {/* AFFIRMATION — primary message for the day */}
      <div className="daily-affirmation daily-affirmation--primary">
        <blockquote className="affirmation-text">&quot;{affirmationText}&quot;</blockquote>
      </div>

      {/* MOOD — how today feels */}
      <div className="daily-meaning-row">
        <span className="daily-meaning-emoji">{moodForecast?.emoji ?? '✨'}</span>
        <div className="daily-meaning-content">
          <span className="daily-meaning-label">How today feels</span>
          <span className="daily-meaning-value">{moodForecast?.mood ?? 'Steady'}</span>
          <span className="daily-meaning-note">
            {moodForecast?.description ??
              'The live daily feature payload is partial right now, so this card is showing the safest fallback guidance.'}
          </span>
        </div>
      </div>

      {/* BEST USE OF TODAY — peak hours + lucky color */}
      <div className="daily-action-row">
        <div className="daily-action-item">
          <span className="daily-action-icon">⚡</span>
          <div>
            <span className="daily-action-label">Best time to work</span>
            <span className="daily-action-value">
              {moodForecast?.peak_hours ?? 'Check back shortly'}
            </span>
          </div>
        </div>
        <div className="daily-action-item">
          <div
            className="daily-action-icon color-swatch"
            style={{
              backgroundColor: luckyColors?.primary_hex ?? '#88c0d0',
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              flexShrink: 0,
            }}
          />
          <div>
            <span className="daily-action-label">Wear or use today</span>
            <span className="daily-action-value">{luckyColors?.primary ?? 'Cosmic blue'}</span>
            <span className="daily-action-note">
              {luckyColors?.description ?? 'Use a calming color cue while the daily palette finishes loading.'}
            </span>
          </div>
        </div>
      </div>

      {/* RETROGRADE ALERTS — only if any */}
      {retrogradeAlerts.length > 0 && (
        <div className="retrograde-alert">
          <span className="alert-icon">⚠️ Heads up</span>
          {retrogradeAlerts.map((alert, i) => (
            <div key={i} className="alert-content">
              <p className="alert-planet">
                {alert.planet} {alert.status}
              </p>
              <p className="alert-message">{alert.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* NUMBERS & DETAILS — collapsible */}
      <div className="daily-details-toggle-wrapper">
        <button
          className="daily-details-toggle"
          onClick={() => setDetailsOpen((v) => !v)}
          aria-expanded={detailsOpen}
        >
          <span>Numbers &amp; details</span>
          <span className={`daily-details-chevron ${detailsOpen ? 'open' : ''}`}>▾</span>
        </button>

        {detailsOpen && (
          <div className="features-grid features-grid--secondary">
            {/* Lucky Numbers */}
            <div className="feature-item lucky-number">
              <div className="feature-icon">🔢</div>
              <div className="feature-content">
                <span className="feature-label">Lucky Numbers</span>
                <span className="feature-value">
                  {luckyNumbers.length > 0 ? luckyNumbers.join(', ') : 'Still loading'}
                </span>
                <span className="feature-meaning">
                  Your numerology number: {features.life_path ?? 'Pending'}
                </span>
              </div>
            </div>

            {/* Ruling Planet */}
            <div className="feature-item ruling-planet">
              <div className="feature-icon">{focusPlanetSymbol}</div>
              <div className="feature-content">
                <span className="feature-label">Focus Planet</span>
                <span className="feature-value">{focusPlanet}</span>
                <span className="feature-meaning">
                  {luckyPlanet?.message ?? 'The focus planet is still resolving from the daily feature feed.'}
                </span>
              </div>
            </div>

            {/* Personal Day */}
            <div className="feature-item personal-day">
              <div className="feature-icon">📅</div>
              <div className="feature-content">
                <span className="feature-label">Day Number</span>
                <span className="feature-value">{features.personal_day ?? 'Pending'}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
