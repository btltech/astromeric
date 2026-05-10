import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchYearAhead, type ProfilePayload } from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { useActiveProfile } from '../hooks';
import type { SavedProfile, YearAheadForecast, YearAheadMonthlyForecast } from '../types';
import './ProductDesk.css';
import './YearAheadView.css';

const previewProfile: SavedProfile = {
  id: -1,
  name: 'Amara Lewis',
  date_of_birth: '1994-11-18',
  time_of_birth: '08:30',
  place_of_birth: 'London, UK',
  latitude: 51.5072,
  longitude: -0.1276,
  timezone: 'Europe/London',
  house_system: 'Placidus',
};

function toProfilePayload(profile: SavedProfile | null): ProfilePayload {
  const source = profile ?? previewProfile;
  return {
    name: source.name,
    date_of_birth: source.date_of_birth,
    time_of_birth: source.time_of_birth ?? undefined,
    place_of_birth: source.place_of_birth ?? undefined,
    location: {
      latitude: source.latitude ?? previewProfile.latitude ?? 0,
      longitude: source.longitude ?? previewProfile.longitude ?? 0,
      timezone: source.timezone ?? previewProfile.timezone ?? 'UTC',
    },
    house_system: source.house_system ?? 'Placidus',
  };
}

const MONTH_ABBR = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const ELEMENT_EMOJI: Record<string, string> = {
  Fire: '🔥',
  Earth: '🌿',
  Air: '💨',
  Water: '💧',
};

function MonthCard({ m }: { m: YearAheadMonthlyForecast }) {
  const [expanded, setExpanded] = useState(false);
  const monthLabel = MONTH_ABBR[m.month - 1] ?? `Month ${m.month}`;
  const elemEmoji = ELEMENT_EMOJI[m.element] ?? '✨';

  return (
    <div className={`ya-month-card${expanded ? ' ya-month-card--open' : ''}`}>
      <button
        className="ya-month-card__header"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span className="ya-month-card__label">
          {monthLabel} <span className="ya-month-card__num">#{m.personal_month}</span>
        </span>
        <span className="ya-month-card__focus">{m.focus}</span>
        <span className="ya-month-card__elem">{elemEmoji}</span>
        <span className="ya-month-card__chevron">{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div className="ya-month-card__body">
          {m.highlights.length > 0 && (
            <ul className="ya-month-card__highlights">
              {m.highlights.map((h, i) => (
                <li key={i}>{h}</li>
              ))}
            </ul>
          )}
          {m.eclipses.length > 0 && (
            <div className="ya-month-card__eclipses">
              <strong>Eclipses:</strong>{' '}
              {m.eclipses.map((e) => `${e.type} in ${e.sign} (${e.date})`).join(', ')}
            </div>
          )}
          {m.ingresses.length > 0 && (
            <div className="ya-month-card__ingresses">
              <strong>Ingresses:</strong>{' '}
              {m.ingresses.map((ing) => `${ing.planet} → ${ing.sign}`).join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function YearAheadView() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();
  const [forecast, setForecast] = useState<YearAheadForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [year] = useState(() => new Date().getFullYear());

  const requestProfile = useMemo(() => toProfilePayload(activeProfile), [activeProfile]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchYearAhead(requestProfile, year);
        if (!cancelled) setForecast(result);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load year-ahead forecast');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => { cancelled = true; };
  }, [requestProfile, year]);

  const isPreview = !hasActiveProfile;

  return (
    <>
      <DocumentMeta
        title="Year Ahead Forecast — AstroNumeric"
        description="Your personalised astrology and numerology forecast for the full year ahead."
      />

      <div className="product-desk">
        <header className="product-desk__header">
          <div className="product-desk__header-top">
            <Link to="/" className="product-desk__back">← Home</Link>
            {isPreview && (
              <Link to="/profile" className="product-desk__cta-link">
                Add your profile for a personal reading →
              </Link>
            )}
          </div>
          <h1 className="product-desk__title">Year Ahead {year}</h1>
          {activeProfile && (
            <p className="product-desk__subtitle">
              {activeProfile.name} · {activeProfileSourceLabel}
            </p>
          )}
        </header>

        {loading && (
          <div className="product-desk__loading">
            <div className="spinner" />
            <p>Calculating your year ahead…</p>
          </div>
        )}

        {error && !loading && (
          <div className="product-desk__error">
            <p>{error}</p>
            <button className="btn btn-secondary" onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        )}

        {forecast && !loading && (
          <div className="ya-layout">
            {/* Personal Year banner */}
            <section className="product-desk__panel ya-banner">
              <div className="ya-banner__number">{forecast.personal_year.number}</div>
              <div className="ya-banner__content">
                <h2 className="ya-banner__theme">{forecast.personal_year.theme}</h2>
                <p className="ya-banner__desc">{forecast.personal_year.description}</p>
              </div>
            </section>

            {/* Two column: solar return + universal year */}
            <div className="ya-row">
              <section className="product-desk__panel ya-card">
                <h3 className="ya-card__title">☀️ Solar Return</h3>
                <p className="ya-card__date">{forecast.solar_return.date}</p>
                <p className="ya-card__text">{forecast.solar_return.description}</p>
              </section>

              <section className="product-desk__panel ya-card">
                <h3 className="ya-card__title">🌍 Universal Year {forecast.universal_year.number}</h3>
                <p className="ya-card__text">{forecast.universal_year.theme}</p>
              </section>
            </div>

            {/* Key themes */}
            {forecast.key_themes.length > 0 && (
              <section className="product-desk__panel ya-themes">
                <h3 className="ya-themes__title">Key Themes</h3>
                <ul className="ya-themes__list">
                  {forecast.key_themes.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </section>
            )}

            {/* Advice */}
            {forecast.advice.length > 0 && (
              <section className="product-desk__panel ya-advice">
                <h3 className="ya-advice__title">Guidance for {year}</h3>
                <ul className="ya-advice__list">
                  {forecast.advice.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </section>
            )}

            {/* Monthly breakdown */}
            {forecast.monthly_forecasts.length > 0 && (
              <section className="product-desk__panel ya-months">
                <h3 className="ya-months__title">Month by Month</h3>
                <div className="ya-months__grid">
                  {forecast.monthly_forecasts.map((m) => (
                    <MonthCard key={m.month} m={m} />
                  ))}
                </div>
              </section>
            )}

            {/* Eclipses */}
            {forecast.eclipses.all.length > 0 && (
              <section className="product-desk__panel ya-eclipses">
                <h3 className="ya-eclipses__title">🌑 Eclipses in {year}</h3>
                <ul className="ya-eclipses__list">
                  {forecast.eclipses.all.map((e, i) => (
                    <li key={i}>
                      <span className="ya-eclipse__type">{e.type}</span> in{' '}
                      <span className="ya-eclipse__sign">{e.sign}</span> at {e.degree.toFixed(1)}°
                      <span className="ya-eclipse__date"> · {e.date}</span>
                    </li>
                  ))}
                </ul>
                {forecast.eclipses.personal_impacts.length > 0 && (
                  <div className="ya-eclipses__impacts">
                    <strong>Personal impacts:</strong>
                    <ul>
                      {forecast.eclipses.personal_impacts.map((impact, i) => (
                        <li key={i}>{impact.significance}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </section>
            )}

            {/* Ingresses */}
            {forecast.ingresses.length > 0 && (
              <section className="product-desk__panel ya-ingresses">
                <h3 className="ya-ingresses__title">🪐 Major Planetary Ingresses</h3>
                <ul className="ya-ingresses__list">
                  {forecast.ingresses.map((ing, i) => (
                    <li key={i}>
                      <span className="ya-ingress__planet">{ing.planet}</span> enters{' '}
                      <span className="ya-ingress__sign">{ing.sign}</span>
                      <span className="ya-ingress__date"> · {ing.date}</span>
                      {ing.impact && <p className="ya-ingress__impact">{ing.impact}</p>}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </>
  );
}

export default YearAheadView;
