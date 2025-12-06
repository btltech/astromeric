import React from 'react';
import type { MoonPhaseSummary } from '../types';

interface Props {
  moonData: MoonPhaseSummary;
}

export function MoonPhaseCard({ moonData }: Props) {
  const { current_phase, moon_sign, ritual, upcoming_events } = moonData;

  return (
    <div className="moon-phase-container">
      <h3 className="moon-title">🌙 Lunar Guidance</h3>

      {/* Current Phase Display */}
      <div className="moon-phase-display">
        <div className="phase-emoji">{current_phase.emoji}</div>
        <div className="phase-info">
          <div className="phase-name">{current_phase.phase_name}</div>
          <div className="moon-sign">Moon in {moon_sign}</div>
          <div className="illumination">
            {current_phase.illumination}% illuminated
          </div>
        </div>
        <div className="phase-timing">
          <span className={`phase-badge ${current_phase.is_waxing ? 'waxing' : 'waning'}`}>
            {current_phase.is_waxing ? '↑ Waxing' : '↓ Waning'}
          </span>
          <span className="days-info">
            {current_phase.days_until_next_phase.toFixed(1)} days to next phase
          </span>
        </div>
      </div>

      {/* Ritual Recommendations */}
      <div className="ritual-section">
        <div className="ritual-header">
          <h4>✨ {ritual.theme}</h4>
          <p className="ritual-energy">{ritual.energy}</p>
        </div>

        <div className="ritual-grid">
          {/* Activities */}
          <div className="ritual-card activities">
            <h5>🎯 Recommended Activities</h5>
            <ul>
              {ritual.activities.map((act, i) => (
                <li key={i}>{act}</li>
              ))}
            </ul>
          </div>

          {/* Avoid */}
          <div className="ritual-card avoid">
            <h5>🚫 Best to Avoid</h5>
            <ul>
              {ritual.avoid.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Ritual Enhancements */}
        <div className="ritual-enhancements">
          <div className="enhancement-item">
            <span className="label">Element Boost:</span>
            <span className="value">{ritual.element_boost}</span>
          </div>
          <div className="enhancement-item">
            <span className="label">Body Focus:</span>
            <span className="value">{ritual.body_focus}</span>
          </div>
          <div className="enhancement-row">
            <span className="label">Crystals:</span>
            <div className="tags">
              {ritual.crystals.map((c, i) => (
                <span key={i} className="tag crystal">{c}</span>
              ))}
            </div>
          </div>
          <div className="enhancement-row">
            <span className="label">Colors:</span>
            <div className="swatches">
              {ritual.colors.map((c, i) => (
                <span 
                  key={i} 
                  className="color-swatch" 
                  style={{ backgroundColor: c.toLowerCase() }}
                  title={c}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Affirmation */}
        <div className="affirmation-box">
          <span className="affirmation-label">🔮 Affirmation</span>
          <p className="affirmation-text">"{ritual.affirmation}"</p>
        </div>

        {/* Personal Insights */}
        {(ritual.natal_insight || ritual.numerology_insight) && (
          <div className="personal-insights">
            {ritual.natal_insight && (
              <div className="insight">{ritual.natal_insight}</div>
            )}
            {ritual.numerology_insight && (
              <div className="insight">🔢 {ritual.numerology_insight}</div>
            )}
          </div>
        )}
      </div>

      {/* Upcoming Events */}
      {upcoming_events.length > 0 && (
        <div className="upcoming-events">
          <h5>📅 Upcoming Lunar Events</h5>
          <div className="events-list">
            {upcoming_events.map((event, i) => (
              <div key={i} className="event-item">
                <span className="event-emoji">{event.emoji}</span>
                <span className="event-type">{event.type}</span>
                <span className="event-sign">in {event.sign}</span>
                <span className="event-date">{event.date}</span>
                <span className="event-days">{event.days_away} days</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
