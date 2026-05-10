import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  fetchNumerologyProfile,
  type LiveNumerologyProfile,
  type ProfilePayload,
} from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { useActiveProfile } from '../hooks';
import type { SavedProfile } from '../types';
import './ProductDesk.css';

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
    house_system: source.house_system ?? previewProfile.house_system ?? 'Placidus',
  };
}

function formatArcLabel(kind: 'Pinnacle' | 'Challenge', index: number, ages: string) {
  return `${kind} ${index + 1} · ${ages}`;
}

export function NumerologyDeskView() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();
  const [numerologyProfile, setNumerologyProfile] = useState<LiveNumerologyProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const requestProfile = useMemo(() => toProfilePayload(activeProfile), [activeProfile]);

  useEffect(() => {
    let isCancelled = false;

    async function loadNumerologyDesk() {
      setLoading(true);
      setError(null);

      try {
        const liveNumerology = await fetchNumerologyProfile(requestProfile);

        if (isCancelled) {
          return;
        }

        setNumerologyProfile(liveNumerology);
      } catch (err) {
        if (isCancelled) {
          return;
        }

        const message = err instanceof Error ? err.message : 'Could not load live numerology data.';
        setNumerologyProfile(null);
        setError(message);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    loadNumerologyDesk();

    return () => {
      isCancelled = true;
    };
  }, [requestProfile]);

  const sourceLabel = hasActiveProfile ? activeProfileSourceLabel : 'Preview profile';
  const coreNumbers = [
    { label: 'Life Path', value: numerologyProfile?.life_path.number ?? '...' },
    { label: 'Destiny', value: numerologyProfile?.destiny_number ?? '...' },
    { label: 'Personal Year', value: numerologyProfile?.personal_year.cycle_number ?? '...' },
    {
      label: 'Lucky set',
      value: numerologyProfile?.lucky_numbers.slice(0, 3).join(' · ') || '...',
    },
  ];
  const playbookSteps = [
    {
      label: 'Lock the baseline',
      detail: numerologyProfile
        ? `Life Path ${numerologyProfile.life_path.number}, Destiny ${numerologyProfile.destiny_number}, and Personal Year ${numerologyProfile.personal_year.cycle_number} define the desk.`
        : 'The core number set will appear here once the live numerology feed resolves.',
    },
    {
      label: 'Read the current cycle',
      detail:
        numerologyProfile?.synthesis?.current_focus ??
        numerologyProfile?.personal_year.interpretation ??
        'The active timing layer will surface the strongest current focus here.',
    },
    {
      label: 'Carry the longer arc',
      detail:
        numerologyProfile?.life_path.life_purpose ??
        numerologyProfile?.synthesis?.affirmation ??
        'Use the purpose brief, pinnacles, and challenges to move from today into the longer arc.',
    },
  ];
  const synthesisCards = [
    {
      label: 'Summary',
      value:
        numerologyProfile?.synthesis?.summary ??
        numerologyProfile?.life_path.meaning ??
        'Your synthesis summary will appear here.',
    },
    {
      label: 'Current focus',
      value:
        numerologyProfile?.synthesis?.current_focus ??
        numerologyProfile?.personal_year.interpretation ??
        'Current-cycle emphasis will surface here.',
    },
    {
      label: 'Affirmation',
      value:
        numerologyProfile?.synthesis?.affirmation ??
        'Your affirmation will appear here once synthesis loads.',
    },
  ];

  return (
    <div className="product-desk">
      <DocumentMeta
        title="AstroNumeric — Numerology Desk"
        description="Your core numbers, personal cycles, lucky days, and long-range arc."
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Numerology desk</span>
        <h1>Numbers, cycles, and timing — in one place.</h1>
        <p>
          Core numbers, live personal cycles, lucky days, and your long-range arc — all on a
          single focused desk.
        </p>
        <div className="product-desk__chips">
          <span className="product-desk__chip">Core numbers</span>
          <span className="product-desk__chip">Current cycles</span>
          <span className="product-desk__chip">Lucky numbers + days</span>
          <span className="product-desk__chip">Long-range arc</span>
        </div>
        <div className="product-desk__actions">
          <Link to="/charts" className="btn-primary product-desk__action">
            Return to charts
          </Link>
          <Link to="/reading" className="btn-secondary product-desk__action">
            Refine profile data
          </Link>
        </div>
      </section>

      <section className="product-desk__grid">
        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Current context</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Driving profile</span>
              <span className="product-desk__value">{requestProfile.name}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Source</span>
              <span className="product-desk__value">{sourceLabel}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Desk state</span>
              <span className="product-desk__value">
                {loading ? 'Loading live numerology' : error ? 'Feed delayed' : 'Live numerology ready'}
              </span>
            </div>
          </div>
          <p className="product-desk__note">
            {hasActiveProfile
              ? 'Your numerology feed is live — timing and synthesis update with your active profile.'
              : 'Select an active profile in the reading desk to load your personal numerology feed.'}
          </p>
          {error && <p className="product-desk__note">{error}</p>}
        </article>

        <article className="product-desk__panel">
          <h2>How to use this desk</h2>
          <ul className="product-desk__list">
            {playbookSteps.map((step) => (
              <li key={step.label} className="product-desk__list-item">
                <div>
                  <strong>{step.label}</strong>
                  <span className="product-desk__meta">{step.detail}</span>
                </div>
              </li>
            ))}
          </ul>
        </article>

        <article className="product-desk__panel product-desk__panel--full">
          <h2>Core numbers</h2>
          <div className="product-desk__stats">
            {coreNumbers.map((item) => (
              <div key={item.label} className="product-desk__stat">
                <span className="product-desk__label">{item.label}</span>
                <span className="product-desk__value">{item.value}</span>
              </div>
            ))}
          </div>
          <p className="product-desk__note">
            {numerologyProfile?.life_path.meaning ??
              'The meaning attached to the lead number will surface here once the live numerology feed resolves.'}
          </p>
        </article>

        <article className="product-desk__panel">
          <h2>Current timing</h2>
          <ul className="product-desk__list">
            <li className="product-desk__list-item">
              <div>
                <strong>Personal Year</strong>
                <span className="product-desk__meta">
                  {numerologyProfile?.personal_year.interpretation ??
                    'The current year cycle will appear here.'}
                </span>
              </div>
            </li>
            <li className="product-desk__list-item">
              <div>
                <strong>Personal Month</strong>
                <span className="product-desk__meta">
                  {numerologyProfile?.numerology_insights.personal_month ??
                    'Month-level timing will appear here.'}
                </span>
              </div>
            </li>
            <li className="product-desk__list-item">
              <div>
                <strong>Personal Day</strong>
                <span className="product-desk__meta">
                  {numerologyProfile?.numerology_insights.personal_day ??
                    'Day-level timing will appear here.'}
                </span>
              </div>
            </li>
          </ul>
        </article>

        <article className="product-desk__panel">
          <h2>Luck surface</h2>
          <div className="product-desk__stack">
            <div>
              <span className="product-desk__label">Lucky numbers</span>
              <div className="product-desk__chips">
                {(numerologyProfile?.lucky_numbers.length
                  ? numerologyProfile.lucky_numbers
                  : ['...']
                ).map((item) => (
                  <span key={String(item)} className="product-desk__badge">
                    {item}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="product-desk__label">Auspicious days</span>
              <div className="product-desk__chips">
                {(numerologyProfile?.auspicious_days.length
                  ? numerologyProfile.auspicious_days
                  : ['...']
                ).map((item) => (
                  <span key={String(item)} className="product-desk__badge">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </article>

        <article className="product-desk__panel product-desk__panel--full">
          <h2>Synthesis brief</h2>
          <div className="product-desk__linkgrid">
            {synthesisCards.map((item) => (
              <div key={item.label} className="product-desk__linkcard">
                <strong>{item.label}</strong>
                <span>{item.value}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Long-range arc</h2>
          <ul className="product-desk__list">
            {(numerologyProfile?.pinnacles.length ? numerologyProfile.pinnacles : []).map((item, index) => (
              <li key={`p-${item.number}-${index}`} className="product-desk__list-item">
                <div>
                  <strong>{formatArcLabel('Pinnacle', index, item.ages)}</strong>
                  <span className="product-desk__meta">{item.meaning}</span>
                </div>
                <span className="product-desk__badge">{item.number}</span>
              </li>
            ))}
            {(numerologyProfile?.challenges.length ? numerologyProfile.challenges : []).map((item, index) => (
              <li key={`c-${item.number}-${index}`} className="product-desk__list-item">
                <div>
                  <strong>{formatArcLabel('Challenge', index, item.ages)}</strong>
                  <span className="product-desk__meta">{item.meaning}</span>
                </div>
                <span className="product-desk__badge">{item.number}</span>
              </li>
            ))}
          </ul>
          {!numerologyProfile && !loading && (
            <p className="product-desk__note">Long-range numerology arc data is unavailable right now.</p>
          )}
        </article>

        <article className="product-desk__panel">
          <h2>Karmic debts</h2>
          {numerologyProfile?.karmic_debts?.length ? (
            <ul className="product-desk__list">
              {numerologyProfile.karmic_debts.map((item) => (
                <li key={`${item.raw}-${item.label}`} className="product-desk__list-item">
                  <div>
                    <strong>{item.label}</strong>
                    <span className="product-desk__meta">{item.description}</span>
                  </div>
                  <span className="product-desk__badge">{item.raw}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="product-desk__note">
              {loading
                ? 'Checking the live numerology response for karmic debt markers.'
                : 'No karmic debt markers are currently surfaced for this profile.'}
            </p>
          )}
        </article>
      </section>
    </div>
  );
}

export default NumerologyDeskView;