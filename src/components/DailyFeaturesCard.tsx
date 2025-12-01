import React, { useState, useEffect } from 'react';
import { fetchDailyFeatures, type DailyFeaturesResponse } from '../api/client';

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

  useEffect(() => {
    async function loadFeatures() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchDailyFeatures(birthDate, sunSign);
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
    return (
      <div className="daily-features-card loading">
        <div className="loading-spinner">✨</div>
        <p>Consulting the cosmos...</p>
      </div>
    );
  }

  if (error || !features) {
    return (
      <div className="daily-features-card error">
        <p>{error || 'Unable to load daily features'}</p>
      </div>
    );
  }

  return (
    <div className="daily-features-card">
      <h3 className="card-title">✨ Your Daily Cosmic Guide</h3>
      
      <div className="features-grid">
        {/* Lucky Numbers */}
        <div className="feature-item lucky-number">
          <div className="feature-icon">🔢</div>
          <div className="feature-content">
            <span className="feature-label">Lucky Numbers</span>
            <span className="feature-value">{features.lucky_numbers.join(', ')}</span>
            <span className="feature-meaning">Life Path: {features.life_path}</span>
          </div>
        </div>

        {/* Lucky Color */}
        <div className="feature-item lucky-color">
          <div 
            className="feature-icon color-swatch"
            style={{ backgroundColor: features.lucky_colors.primary_hex }}
          />
          <div className="feature-content">
            <span className="feature-label">Lucky Color</span>
            <span className="feature-value">{features.lucky_colors.primary}</span>
            <span className="feature-meaning">{features.lucky_colors.description}</span>
          </div>
        </div>

        {/* Ruling Planet */}
        <div className="feature-item ruling-planet">
          <div className="feature-icon">{PLANET_SYMBOLS[features.lucky_planet.planet] || '🌟'}</div>
          <div className="feature-content">
            <span className="feature-label">Today's Ruling Planet</span>
            <span className="feature-value">{features.lucky_planet.planet}</span>
            <span className="feature-meaning">{features.lucky_planet.message}</span>
          </div>
        </div>

        {/* Tarot Energy */}
        <div className="feature-item tarot-energy">
          <div className="feature-icon">🃏</div>
          <div className="feature-content">
            <span className="feature-label">Today's Tarot Energy</span>
            <span className="feature-value">{features.tarot.card}{features.tarot.reversed ? ' (Reversed)' : ''}</span>
            <span className="feature-meaning">{features.tarot.message}</span>
          </div>
        </div>

        {/* Mood Forecast */}
        <div className="feature-item mood-forecast">
          <div className="feature-icon">{features.mood_forecast.emoji}</div>
          <div className="feature-content">
            <span className="feature-label">Mood Forecast</span>
            <span className="feature-value">{features.mood_forecast.mood} ({features.mood_forecast.score}/10)</span>
            <span className="feature-meaning">{features.mood_forecast.description}</span>
          </div>
        </div>

        {/* Personal Day */}
        <div className="feature-item personal-day">
          <div className="feature-icon">📅</div>
          <div className="feature-content">
            <span className="feature-label">Personal Day</span>
            <span className="feature-value">{features.personal_day}</span>
            <span className="feature-meaning">Peak hours: {features.mood_forecast.peak_hours}</span>
          </div>
        </div>
      </div>

      {/* Daily Affirmation */}
      <div className="daily-affirmation">
        <span className="affirmation-label">🌟 Your Daily Affirmation ({features.affirmation.category})</span>
        <blockquote className="affirmation-text">
          "{features.affirmation.text}"
        </blockquote>
        <p className="affirmation-instruction">{features.affirmation.instruction}</p>
      </div>

      {/* Manifestation Focus */}
      <div className="manifestation-focus">
        <span className="manifestation-label">🎯 Manifestation Focus: {features.manifestation.focus}</span>
        <p className="manifestation-text">{features.manifestation.prompt}</p>
        <p className="manifestation-practice">{features.manifestation.practice}</p>
      </div>

      {/* Best For Today */}
      <div className="cosmic-tip">
        <span className="tip-icon">💫 Best Activities for Today</span>
        <p className="tip-text">{features.lucky_planet.best_for.join(' • ')}</p>
      </div>

      {/* Retrograde Alerts */}
      {features.retrograde_alerts.length > 0 && (
        <div className="retrograde-alert">
          <span className="alert-icon">⚠️ Retrograde Alert</span>
          {features.retrograde_alerts.map((alert, i) => (
            <div key={i} className="alert-content">
              <p className="alert-planet">{alert.planet} {alert.status}</p>
              <p className="alert-message">{alert.message}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
