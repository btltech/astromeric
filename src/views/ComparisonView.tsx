import React, { useMemo } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { decodeProfile, SharedProfile } from '../utils/comparison';
import { WeeklyVibe } from '../components/WeeklyVibe';
import { useProfiles } from '../hooks';
import { ProfilePayload } from '../api/client';

export function ComparisonView() {
  const location = useLocation();
  const { selectedProfile } = useProfiles();

  const query = new URLSearchParams(location.search);
  const pHash = query.get('p');

  const friendProfile: SharedProfile | null = useMemo(() => {
    if (!pHash) return null;
    return decodeProfile(pHash);
  }, [pHash]);

  if (!friendProfile) {
    return (
      <div className="page comparison-page error">
        <h2>Invalid Comparison Link</h2>
        <p>This link seems to be broken or expired.</p>
        <Link to="/" className="btn-primary">
          Go Home
        </Link>
      </div>
    );
  }

  // Convert SharedProfile to ProfilePayload for WeeklyVibe
  const friendPayload: ProfilePayload = {
    name: friendProfile.name,
    date_of_birth: friendProfile.dob,
    time_of_birth: friendProfile.tob,
    latitude: friendProfile.lat,
    longitude: friendProfile.lng,
    timezone: friendProfile.tz,
  };

  return (
    <div className="page comparison-page">
      <section className="hero hero-compact text-center">
        <h1>Cosmic Synergy</h1>
        <p className="lede">
          Comparing your weekly vibes with <strong>{friendProfile.name}</strong>
        </p>
      </section>

      <div className="comparison-grid">
        <div className="comparison-col">
          <h3 className="col-title">✨ {friendProfile.name}&apos;s Vibe</h3>
          <WeeklyVibe profile={friendPayload} showShare={false} />
        </div>

        {selectedProfile ? (
          <div className="comparison-col">
            <h3 className="col-title">💫 Your Vibe ({selectedProfile.name})</h3>
            <WeeklyVibe
              profile={{
                name: selectedProfile.name,
                date_of_birth: selectedProfile.date_of_birth,
                time_of_birth: selectedProfile.time_of_birth || undefined,
                latitude: selectedProfile.latitude as number,
                longitude: selectedProfile.longitude as number,
                timezone: selectedProfile.timezone || 'UTC',
              }}
              showShare={false}
            />
          </div>
        ) : (
          <div className="comparison-col empty-state">
            <div className="card text-center">
              <h3>Where do you stand?</h3>
              <p>
                Create or select a profile to see your energy side-by-side with {friendProfile.name}
                .
              </p>
              <Link to="/" className="btn-primary">
                Set Up My Profile
              </Link>
            </div>
          </div>
        )}
      </div>

      <div className="synergy-footer text-center">
        <p>The stars align differently for everyone. Find your common high-energy days!</p>
      </div>
    </div>
  );
}
