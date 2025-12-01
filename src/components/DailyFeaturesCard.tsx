import React, { useState, useEffect } from 'react';
import { fetchDailyFeatures, type DailyFeaturesResponse } from '../api/client';

interface Props {
  birthDate: string;
  sunSign?: string;
}

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
        {/* Lucky Number */}
        <div className="feature-item lucky-number">
          <div className="feature-icon">🔢</div>
          <div className="feature-content">
            <span className="feature-label">Lucky Number</span>
            <span className="feature-value">{features.lucky_number}</span>
            <span className="feature-meaning">{features.lucky_number_meaning}</span>
          </div>
        </div>

        {/* Lucky Color */}
        <div className="feature-item lucky-color">
          <div 
            className="feature-icon color-swatch"
            style={{ backgroundColor: features.lucky_color.hex }}
          />
          <div className="feature-content">
            <span className="feature-label">Lucky Color</span>
            <span className="feature-value">{features.lucky_color.name}</span>
            <span className="feature-meaning">{features.lucky_color.meaning}</span>
          </div>
        </div>

        {/* Ruling Planet */}
        <div className="feature-item ruling-planet">
          <div className="feature-icon">{features.ruling_planet.symbol}</div>
          <div className="feature-content">
            <span className="feature-label">Today's Ruling Planet</span>
            <span className="feature-value">{features.ruling_planet.name}</span>
            <span className="feature-meaning">{features.ruling_planet.focus}</span>
          </div>
        </div>

        {/* Tarot Energy */}
        <div className="feature-item tarot-energy">
          <div className="feature-icon">🃏</div>
          <div className="feature-content">
            <span className="feature-label">Today's Tarot Energy</span>
            <span className="feature-value">{features.tarot_energy.name}</span>
            <span className="feature-meaning">{features.tarot_energy.meaning}</span>
          </div>
        </div>
      </div>

      {/* Daily Affirmation */}
      <div className="daily-affirmation">
        <span className="affirmation-label">🌟 Your Daily Affirmation</span>
        <blockquote className="affirmation-text">
          "{features.daily_affirmation}"
        </blockquote>
      </div>

      {/* Manifestation Focus */}
      <div className="manifestation-focus">
        <span className="manifestation-label">🎯 Manifestation Focus</span>
        <p className="manifestation-text">{features.manifestation_focus}</p>
      </div>

      {/* Cosmic Tip */}
      <div className="cosmic-tip">
        <span className="tip-icon">💫</span>
        <p className="tip-text">{features.cosmic_tip}</p>
      </div>
    </div>
  );
}
