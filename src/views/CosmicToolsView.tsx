import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { CosmicGuideChat } from '../components/CosmicGuideChat';
import { DailyFeaturesCard } from '../components/DailyFeaturesCard';
import { DocumentMeta } from '../components/DocumentMeta';
import { MoonPhaseCard } from '../components/MoonPhaseCard';
import { OracleYesNo } from '../components/OracleYesNo';
import { TarotCard } from '../components/TarotCard';
import TimingAdvisor from '../components/TimingAdvisor';
import { useProfiles } from '../hooks';
import type { NewProfileForm } from '../types';
import './ProductDesk.css';

const fallbackBirthDate = '1994-11-18';

export function CosmicToolsView() {
  const { selectedProfile, activeProfileSourceLabel } = useProfiles();

  const timingProfile = useMemo<NewProfileForm | null>(() => {
    if (!selectedProfile) {
      return null;
    }

    return {
      name: selectedProfile.name,
      date_of_birth: selectedProfile.date_of_birth,
      time_of_birth: selectedProfile.time_of_birth ?? undefined,
      place_of_birth: selectedProfile.place_of_birth ?? undefined,
      latitude: selectedProfile.latitude ?? undefined,
      longitude: selectedProfile.longitude ?? undefined,
      timezone: selectedProfile.timezone ?? undefined,
      house_system: selectedProfile.house_system ?? undefined,
    };
  }, [selectedProfile]);

  const profileMode = selectedProfile ? activeProfileSourceLabel : 'Guest defaults';
  const planningPosture = selectedProfile ? 'Profile-aware' : 'Guest defaults';
  const timePrecision = selectedProfile?.time_of_birth ? 'Exact birth time' : 'Birth time missing';
  const locationPrecision = selectedProfile?.place_of_birth
    ? 'Birth place locked'
    : selectedProfile?.timezone
      ? 'Timezone only'
      : 'Location missing';
  const planningNote = selectedProfile
    ? selectedProfile.place_of_birth && selectedProfile.time_of_birth
      ? 'Timing windows can lean on both birth time and location, so the planning lane is running with the strongest profile context available on the web right now.'
      : 'The planning lane is live, but it will sharpen further once this profile has both birth place and birth time.'
    : 'Guest mode still works for quick pulls, but the timing lane becomes materially stronger once a profile is active.';

  return (
    <div className="product-desk cosmic-tools-view">
      <DocumentMeta
        title="AstroNumeric — Tools Desk"
        description="Timing, tarot, daily signal, oracle, and planning tools in one place."
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Tools desk</span>
        <h1>Cosmic tools, all in one place.</h1>
        <p>
          Timing windows, tarot, daily signal cards, oracle guidance, and follow-up
          interpretation — the fast-use tools in one desk.
        </p>
        <div className="product-desk__chips">
          <span className="product-desk__chip">Timing windows</span>
          <span className="product-desk__chip">Daily signal pack</span>
          <span className="product-desk__chip">Tarot + oracle</span>
          <span className="product-desk__chip">Guide follow-ups</span>
        </div>
        <div className="product-desk__actions">
          <Link to="/reading" className="btn-primary product-desk__action">
            Open reading desk
          </Link>
          <Link to="/profile" className="btn-secondary product-desk__action">
            Check profile state
          </Link>
          <a href="#daily-tools" className="btn-secondary product-desk__action">
            Jump to daily tools
          </a>
        </div>
      </section>

      <section className="product-desk__grid">
        <article className="product-desk__panel">
          <h2>Current context</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Active profile</span>
              <span className="product-desk__value">{selectedProfile?.name ?? 'Guest mode'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Source</span>
              <span className="product-desk__value">{profileMode}</span>
            </div>
          </div>
          <p className="product-desk__note">
            {selectedProfile
              ? 'Timing and daily tools are personalised to your active profile.'
              : 'The desk works without a profile, but timing and daily layers are more accurate with one active.'}
          </p>
        </article>

        <article className="product-desk__panel">
          <h2>Tool lanes</h2>
          <div className="product-desk__linkgrid">
            <a href="#daily-tools" className="product-desk__linkcard">
              <strong>Daily tools</strong>
              <span>Tarot, oracle, lunar pulse, and your daily signal pack.</span>
            </a>
            <a href="#timing-planning" className="product-desk__linkcard">
              <strong>Timing &amp; planning</strong>
              <span>Activity windows and planning posture side by side.</span>
            </a>
            <Link to="/charts" className="product-desk__linkcard">
              <strong>Chart follow-through</strong>
              <span>Move into charts when a tool exposes a pattern worth unpacking in natal or numerology detail.</span>
            </Link>
          </div>
        </article>

        <article id="daily-tools" className="product-desk__panel product-desk__panel--full">
          <span className="product-desk__eyebrow">Daily tools</span>
          <h2>Symbolic, fast, and easy to revisit.</h2>
          <p>
            This lane groups the tools that should feel habit-forming on web: lunar pulse, daily
            signals, tarot reflection, and quick oracle guidance.
          </p>
        </article>

        <article className="product-desk__panel">
          <MoonPhaseCard />
        </article>

        <article className="product-desk__panel">
          <div className="tools-content">
            <DailyFeaturesCard birthDate={selectedProfile?.date_of_birth ?? fallbackBirthDate} />
          </div>
        </article>

        <article className="product-desk__panel">
          <div className="tools-content">
            <OracleYesNo birthDate={selectedProfile?.date_of_birth} />
          </div>
        </article>

        <article className="product-desk__panel">
          <div className="tools-content">
            <TarotCard />
          </div>
        </article>

        <article id="timing-planning" className="product-desk__panel product-desk__panel--full">
          <span className="product-desk__eyebrow">Timing &amp; planning</span>
          <h2>Calculated windows, not just symbolic pulls.</h2>
          <p>
            Live sky scoring and planning posture, so you can move from a question to a better-timed decision.
          </p>
        </article>

        <article className="product-desk__panel product-desk__panel--wide product-desk__component-shell">
          <TimingAdvisor profile={timingProfile} />
        </article>

        <article className="product-desk__panel">
          <h2>Planning posture</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Timing source</span>
              <span className="product-desk__value">{planningPosture}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Birth time</span>
              <span className="product-desk__value">{timePrecision}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Location</span>
              <span className="product-desk__value">{locationPrecision}</span>
            </div>
          </div>
          <p className="product-desk__note">{planningNote}</p>
          <div className="product-desk__actions">
            <Link to="/reading" className="btn-secondary product-desk__action">
              Tighten profile data
            </Link>
          </div>
        </article>

        <article className="product-desk__panel product-desk__panel--full">
          <div className="tools-content">
            <CosmicGuideChat />
          </div>
        </article>
      </section>
    </div>
  );
}

export default CosmicToolsView;