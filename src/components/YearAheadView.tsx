import React, { useState } from 'react';
import type { YearAheadForecast, YearAheadMonthlyForecast } from '../types';

interface Props {
  forecast: YearAheadForecast;
}

function MonthCard({ month }: { month: YearAheadMonthlyForecast }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`month-card ${expanded ? 'expanded' : ''}`}>
      <div className="month-header" onClick={() => setExpanded(!expanded)}>
        <div className="month-name">{month.month_name}</div>
        <div className="month-meta">
          <span className="personal-month">PM {month.personal_month}</span>
          <span className="element">{month.element}</span>
        </div>
        <span className="expand-icon">{expanded ? '−' : '+'}</span>
      </div>

      {expanded && (
        <div className="month-content">
          <div className="month-focus">
            <strong>Focus:</strong> {month.focus}
          </div>
          <div className="month-season">
            <strong>Season:</strong> {month.season}
          </div>

          {month.eclipses.length > 0 && (
            <div className="month-eclipses">
              <h6>🌑 Eclipses This Month</h6>
              {month.eclipses.map((ecl, i) => (
                <div key={i} className="eclipse-item">
                  {ecl.type} in {ecl.sign} ({ecl.date})
                </div>
              ))}
            </div>
          )}

          {month.ingresses.length > 0 && (
            <div className="month-ingresses">
              <h6>🔄 Major Ingresses</h6>
              {month.ingresses.map((ing, i) => (
                <div key={i} className="ingress-item">
                  {ing.planet} → {ing.sign} ({ing.date})
                </div>
              ))}
            </div>
          )}

          <div className="month-highlights">
            <h6>✨ Highlights</h6>
            <ul>
              {month.highlights.map((h, i) => (
                <li key={i}>{h}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export function YearAheadView({ forecast }: Props) {
  const [activeTab, setActiveTab] = useState<'overview' | 'months' | 'eclipses'>('overview');

  return (
    <div className="year-ahead-container">
      <h2 className="year-title">
        🔮 {forecast.year} Year Ahead Forecast
      </h2>

      {/* Tabs */}
      <div className="year-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'months' ? 'active' : ''}`}
          onClick={() => setActiveTab('months')}
        >
          Monthly
        </button>
        <button 
          className={`tab ${activeTab === 'eclipses' ? 'active' : ''}`}
          onClick={() => setActiveTab('eclipses')}
        >
          Eclipses
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="year-overview">
          {/* Personal Year */}
          <div className="year-section personal-year">
            <div className="section-header">
              <span className="year-number">{forecast.personal_year.number}</span>
              <h3>{forecast.personal_year.theme}</h3>
            </div>
            <p className="year-description">{forecast.personal_year.description}</p>
          </div>

          {/* Solar Return */}
          <div className="year-section solar-return">
            <h4>☀️ Solar Return</h4>
            <div className="solar-date">{forecast.solar_return.date}</div>
            <p>{forecast.solar_return.description}</p>
          </div>

          {/* Universal Year */}
          <div className="year-section universal-year">
            <h4>🌍 Universal Year {forecast.universal_year.number}</h4>
            <p>{forecast.universal_year.theme}</p>
          </div>

          {/* Key Themes */}
          <div className="year-section key-themes">
            <h4>🎯 Key Themes</h4>
            <ul>
              {forecast.key_themes.map((theme, i) => (
                <li key={i}>{theme}</li>
              ))}
            </ul>
          </div>

          {/* Advice */}
          <div className="year-section advice">
            <h4>💡 Guidance</h4>
            <ul>
              {forecast.advice.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Major Ingresses */}
          {forecast.ingresses.length > 0 && (
            <div className="year-section ingresses">
              <h4>🔄 Major Planetary Shifts</h4>
              <div className="ingress-list">
                {forecast.ingresses.map((ing, i) => (
                  <div key={i} className="ingress-card">
                    <div className="ingress-planet">{ing.planet}</div>
                    <div className="ingress-arrow">→</div>
                    <div className="ingress-sign">{ing.sign}</div>
                    <div className="ingress-date">{ing.date}</div>
                    <div className="ingress-impact">{ing.impact}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Monthly Tab */}
      {activeTab === 'months' && (
        <div className="year-months">
          <div className="months-grid">
            {forecast.monthly_forecasts.map((month) => (
              <MonthCard key={month.month} month={month} />
            ))}
          </div>
        </div>
      )}

      {/* Eclipses Tab */}
      {activeTab === 'eclipses' && (
        <div className="year-eclipses">
          <div className="all-eclipses">
            <h4>🌑 All Eclipses in {forecast.year}</h4>
            <div className="eclipse-timeline">
              {forecast.eclipses.all.map((ecl, i) => (
                <div key={i} className="eclipse-card">
                  <div className="eclipse-type">{ecl.type}</div>
                  <div className="eclipse-sign">{ecl.sign} {ecl.degree.toFixed(1)}°</div>
                  <div className="eclipse-date">{ecl.date}</div>
                </div>
              ))}
            </div>
          </div>

          {forecast.eclipses.personal_impacts.length > 0 && (
            <div className="personal-impacts">
              <h4>⚡ Personal Eclipse Impacts</h4>
              <p className="impact-intro">
                These eclipses activate sensitive points in your chart:
              </p>
              {forecast.eclipses.personal_impacts.map((impact, i) => (
                <div key={i} className="impact-card">
                  <div className="impact-eclipse">
                    {impact.eclipse.type} in {impact.eclipse.sign} ({impact.eclipse.date})
                  </div>
                  <div className="impact-targets">
                    {impact.impacts.map((imp, j) => (
                      <span key={j} className="impact-target">
                        {imp.name} ({imp.orb}° orb)
                      </span>
                    ))}
                  </div>
                  <div className="impact-significance">{impact.significance}</div>
                </div>
              ))}
            </div>
          )}

          {forecast.eclipses.personal_impacts.length === 0 && (
            <div className="no-impacts">
              <p>No eclipses directly activate your natal chart this year. 
              You may still feel their effects through house transits.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
