import React from 'react';
import type { PredictionData, RetrogradeInfo, VoidOfCourseMoon, PlanetaryHourInfo, ColorInfo } from '../types';

// Helper to get color hex and name from color data (supports both string and object formats)
function getColorData(color: string | ColorInfo): { hex: string; name: string } {
  if (typeof color === 'string') {
    // Old format: string color name - use CSS name or fallback
    return { hex: color.toLowerCase(), name: color };
  }
  // New format: object with name and hex
  return { hex: color.hex, name: color.name };
}

// Scope-aware text helpers
function getScopeLabel(scope: string): { title: string; period: string; periodLong: string } {
  switch (scope) {
    case 'weekly':
      return { title: 'Weekly Cosmic Guidance', period: 'This Week', periodLong: 'this week' };
    case 'monthly':
      return { title: 'Monthly Cosmic Guidance', period: 'This Month', periodLong: 'this month' };
    default:
      return { title: 'Daily Cosmic Guidance', period: 'Today', periodLong: 'today' };
  }
}

interface Props {
  guidance: NonNullable<PredictionData['guidance']>;
  scope?: string;
}

// Planet emoji map
const PLANET_EMOJI: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
  Uranus: '♅',
  Neptune: '♆',
  Pluto: '♇',
};

function RetrogradeBadge({ retro }: { retro: RetrogradeInfo }) {
  return (
    <div className="retrograde-badge">
      <div className="retrograde-header">
        <span className="planet-symbol">{PLANET_EMOJI[retro.planet] || '⚹'}</span>
        <span className="planet-name">{retro.planet} ℞</span>
        <span className="planet-sign">in {retro.sign}</span>
      </div>
      <div className="retrograde-impact">{retro.impact}</div>
      {retro.house_impact && (
        <div className="retrograde-house-impact">
          <small>For you: {retro.house_impact}</small>
        </div>
      )}
    </div>
  );
}

function VocMoonCard({ voc }: { voc: VoidOfCourseMoon }) {
  if (!voc.is_void) return null;
  
  return (
    <div className="voc-moon-card">
      <div className="voc-header">
        <span className="icon">☽</span>
        <span className="label">Void-of-Course Moon</span>
      </div>
      <div className="voc-content">
        <p className="voc-sign">
          Moon in {voc.current_sign} {voc.moon_degree ? `at ${voc.moon_degree}°` : ''}
        </p>
        {voc.next_sign && (
          <p className="voc-next">
            → Entering {voc.next_sign}
            {voc.hours_until_sign_change && ` in ~${voc.hours_until_sign_change}h`}
          </p>
        )}
        <p className="voc-advice">{voc.advice}</p>
      </div>
    </div>
  );
}

function PlanetaryHourCard({ hour }: { hour: PlanetaryHourInfo }) {
  const qualityClass = hour.quality.toLowerCase();
  
  return (
    <div className={`planetary-hour-card ${qualityClass}`}>
      <div className="hour-header">
        <span className="planet-symbol">{PLANET_EMOJI[hour.planet] || '⚹'}</span>
        <span className="hour-planet">{hour.planet} Hour</span>
        <span className={`quality-badge ${qualityClass}`}>{hour.quality}</span>
      </div>
      <div className="hour-time">{hour.start} - {hour.end}</div>
      <div className="hour-suggestion">{hour.suggestion}</div>
    </div>
  );
}

export function DailyGuidance({ guidance, scope = 'daily' }: Props) {
  const { avoid, embrace, retrogrades, void_of_course_moon, current_planetary_hour } = guidance;
  const { title, period } = getScopeLabel(scope);

  return (
    <div className="guidance-container">
      <h3 className="guidance-title">✨ {title}</h3>
      
      {/* Alerts Row: Retrogrades + VOC Moon */}
      {(retrogrades?.length > 0 || void_of_course_moon?.is_void) && (
        <div className="alerts-row">
          {retrogrades?.length > 0 && (
            <div className="retrogrades-section">
              <h5 className="alert-heading">⚠️ Current Retrogrades</h5>
              <div className="retrograde-badges">
                {retrogrades.map((r, i) => (
                  <RetrogradeBadge key={i} retro={r} />
                ))}
              </div>
            </div>
          )}
          
          {void_of_course_moon?.is_void && (
            <VocMoonCard voc={void_of_course_moon} />
          )}
        </div>
      )}

      {/* Current Planetary Hour */}
      {current_planetary_hour && (
        <div className="planetary-hour-section">
          <h5 className="section-heading">🕐 Current Planetary Hour</h5>
          <PlanetaryHourCard hour={current_planetary_hour} />
        </div>
      )}

      <div className="guidance-grid">
        {/* Embrace Section */}
        <div className="guidance-card embrace-card">
          <div className="guidance-header">
            <span className="icon">✅</span>
            <h4>Embrace {period}</h4>
          </div>
          
          <div className="guidance-content">
            {embrace.time && scope === 'daily' && (
              <div className="power-hour">
                <span className="label">⚡ Power Hour</span>
                <span className="value">{embrace.time}</span>
              </div>
            )}

            <div className="guidance-list">
              {embrace.activities.map((act, i) => (
                <div key={i} className="guidance-item embrace-item">{act}</div>
              ))}
            </div>

            {embrace.colors.length > 0 && (
              <div className="color-row">
                <span className="label">Power Colors:</span>
                <div className="swatches">
                  {embrace.colors.map((c, i) => {
                    const { hex, name } = getColorData(c);
                    return (
                      <div key={i} className="color-swatch-labeled">
                        <span 
                          className="color-swatch" 
                          style={{ backgroundColor: hex }}
                          title={name}
                        />
                        <span className="color-name">{name}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Avoid Section */}
        <div className="guidance-card avoid-card">
          <div className="guidance-header">
            <span className="icon">🛑</span>
            <h4>Avoid {period}</h4>
          </div>

          <div className="guidance-content">
            <div className="guidance-list">
              {avoid.activities.map((act, i) => (
                <div key={i} className="guidance-item avoid-item">{act}</div>
              ))}
            </div>

            {avoid.colors.length > 0 && (
              <div className="color-row">
                <span className="label">Avoid Colors:</span>
                <div className="swatches">
                  {avoid.colors.map((c, i) => {
                    const { hex, name } = getColorData(c);
                    return (
                      <div key={i} className="color-swatch-labeled">
                        <span 
                          className="color-swatch" 
                          style={{ backgroundColor: hex }}
                          title={name}
                        />
                        <span className="color-name">{name}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {avoid.numbers.length > 0 && (
              <div className="number-row">
                <span className="label">Challenge Numbers:</span>
                <div className="numbers">
                  {avoid.numbers.map((n, i) => (
                    <span key={i} className="num-badge warning">{n}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
