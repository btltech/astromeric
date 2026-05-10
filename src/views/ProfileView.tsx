import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { DocumentMeta } from '../components/DocumentMeta';
import { useProfiles } from '../hooks';
import { useStore } from '../store/useStore';
import type { SavedProfile } from '../types';
import './ProductDesk.css';

function formatProfileMeta(profile: SavedProfile) {
  const bits = [profile.date_of_birth];

  if (profile.time_of_birth) {
    bits.push(profile.time_of_birth);
  }

  if (profile.place_of_birth) {
    bits.push(profile.place_of_birth);
  } else if (profile.timezone) {
    bits.push(profile.timezone);
  }

  return bits.join(' · ');
}

export function ProfileView() {
  const {
    profiles,
    selectedProfile,
    sessionProfile,
    activeProfileSource,
    activeProfileSourceLabel,
  } = useProfiles();
  const { token, user, allowCloudHistory } = useStore();

  const profileSourceLabel = selectedProfile ? activeProfileSourceLabel : 'No active profile';

  const localProfiles = useMemo(() => profiles.filter((profile) => profile.id < 0), [profiles]);
  const cloudProfiles = useMemo(() => profiles.filter((profile) => profile.id > 0), [profiles]);

  return (
    <div className="product-desk">
      <DocumentMeta
        title="AstroNumeric — Profile Desk"
        description="Your active profile, storage source, and sync status."
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Profile desk</span>
        <h1>Your profile and account settings.</h1>
        <p>
          Active identity, storage source, and sync status in one place.
        </p>
        <div className="product-desk__chips">
          <span className="product-desk__chip">Active profile</span>
          <span className="product-desk__chip">Local vs session vs cloud</span>
          <span className="product-desk__chip">Railway status</span>
          <span className="product-desk__chip">Cross-route reuse</span>
        </div>
        <div className="product-desk__actions">
          <Link to="/reading" className="btn-primary product-desk__action">
            Open profile workflow
          </Link>
          <Link to="/charts" className="btn-secondary product-desk__action">
            Use active profile in charts
          </Link>
        </div>
      </section>

      <section className="product-desk__grid">
        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Current setup</h2>
          {selectedProfile ? (
            <div className="product-desk__stack">
              <div className="product-desk__stats">
                <div className="product-desk__stat">
                  <span className="product-desk__label">Active profile</span>
                  <span className="product-desk__value">{selectedProfile.name}</span>
                </div>
                <div className="product-desk__stat">
                  <span className="product-desk__label">Source</span>
                  <span className="product-desk__value">{profileSourceLabel}</span>
                </div>
                <div className="product-desk__stat">
                  <span className="product-desk__label">Birth data</span>
                  <span className="product-desk__value">{formatProfileMeta(selectedProfile)}</span>
                </div>
              </div>
              <p className="product-desk__note">
                {activeProfileSource === 'session'
                  ? 'This is a session profile. Save it to keep it across browser sessions.'
                  : activeProfileSource === 'local'
                    ? 'This profile is saved on your device. Sign in to sync it across devices.'
                    : 'This profile is saved to your account and available across devices.'}
              </p>
            </div>
          ) : (
            <div className="product-desk__empty">
              No profile is active yet. Start on the reading desk to create one and bring the rest of
              the product to life.
            </div>
          )}
        </article>

        <article className="product-desk__panel">
          <h2>Sync posture</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Account</span>
              <span className="product-desk__value">{token ? user?.email ?? 'Connected' : 'Not connected'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Cloud history</span>
              <span className="product-desk__value">{allowCloudHistory ? 'On' : 'Off'}</span>
            </div>
          </div>
          <p className="product-desk__note">
            Phase 1 keeps auth and migration behavior visible from here, even before the dedicated
            settings and diagnostics layer is built.
          </p>
        </article>

        <article className="product-desk__panel product-desk__panel--full">
          <h2>Saved profiles</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Browser session</span>
              <span className="product-desk__value">{sessionProfile ? '1 active' : 'None active'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Device-local</span>
              <span className="product-desk__value">{localProfiles.length}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Railway-backed</span>
              <span className="product-desk__value">{cloudProfiles.length}</span>
            </div>
          </div>

          <ul className="product-desk__list">
            {sessionProfile && (
              <li className="product-desk__list-item">
                <div>
                  <strong>{sessionProfile.name}</strong>
                  <span className="product-desk__meta">{formatProfileMeta(sessionProfile)}</span>
                </div>
                <span className="product-desk__badge">Browser session</span>
              </li>
            )}

            {profiles.map((profile) => (
              <li key={profile.id} className="product-desk__list-item">
                <div>
                  <strong>{profile.name}</strong>
                  <span className="product-desk__meta">{formatProfileMeta(profile)}</span>
                </div>
                <span className="product-desk__badge">
                  {profile.id < 0 ? 'Saved on device' : 'Railway-backed'}
                </span>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}

export default ProfileView;