import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  fetchCompatibility,
  type LiveCompatibilityResult,
  type ProfilePayload,
} from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { useProfiles } from '../hooks';
import { useStore } from '../store/useStore';
import type { SavedProfile } from '../types';
import './ProductDesk.css';

type RelationshipSummary = {
  profile: SavedProfile;
  result: LiveCompatibilityResult;
};

const scoreBuckets = {
  strong: { label: 'Strong match', min: 80 },
  promising: { label: 'Promising match', min: 65 },
  complex: { label: 'Complex match', min: 0 },
} as const;

function toProfilePayload(profile: SavedProfile): ProfilePayload {
  return {
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth ?? undefined,
    place_of_birth: profile.place_of_birth ?? undefined,
    location: {
      latitude: profile.latitude ?? undefined,
      longitude: profile.longitude ?? undefined,
      timezone: profile.timezone ?? undefined,
    },
    house_system: profile.house_system ?? undefined,
  };
}

function formatScore(score: number) {
  if (score >= scoreBuckets.strong.min) return scoreBuckets.strong.label;
  if (score >= scoreBuckets.promising.min) return scoreBuckets.promising.label;
  return scoreBuckets.complex.label;
}

function formatDimensionLabel(name: string) {
  return name.replace(/_/g, ' ');
}

export function RelationshipsView() {
  const { profiles, selectedProfile, activeProfileSourceLabel } = useProfiles();
  const { compareProfileId, setCompareProfileId } = useStore();
  const [summaries, setSummaries] = useState<RelationshipSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const profileMode = selectedProfile ? activeProfileSourceLabel : 'No active profile';
  const candidateProfiles = useMemo(
    () => profiles.filter((profile) => profile.id !== selectedProfile?.id),
    [profiles, selectedProfile?.id]
  );

  useEffect(() => {
    if (!selectedProfile || candidateProfiles.length === 0) {
      setSummaries([]);
      setError(null);
      setLoading(false);
      return;
    }

    let isCancelled = false;

    async function loadSummaries() {
      setLoading(true);
      setError(null);

      const baseProfile = toProfilePayload(selectedProfile);
      const results = await Promise.allSettled(
        candidateProfiles.map(async (profile) => ({
          profile,
          result: await fetchCompatibility(baseProfile, toProfilePayload(profile)),
        }))
      );

      if (isCancelled) {
        return;
      }

      const fulfilled = results
        .filter(
          (
            entry
          ): entry is PromiseFulfilledResult<RelationshipSummary> => entry.status === 'fulfilled'
        )
        .map((entry) => entry.value)
        .sort((left, right) => right.result.overall_score - left.result.overall_score);

      setSummaries(fulfilled);
      setLoading(false);

      if (fulfilled.length === 0) {
        setError('Compatibility summaries could not be loaded for the saved people on this route.');
      }
    }

    loadSummaries();

    return () => {
      isCancelled = true;
    };
  }, [candidateProfiles, selectedProfile]);

  useEffect(() => {
    if (
      compareProfileId !== null &&
      !candidateProfiles.some((profile) => profile.id === compareProfileId)
    ) {
      setCompareProfileId(null);
    }
  }, [candidateProfiles, compareProfileId, setCompareProfileId]);

  const averageScore = summaries.length
    ? Math.round(
        summaries.reduce((total, item) => total + item.result.overall_score, 0) / summaries.length
      )
    : null;
  const strongestMatch = summaries[0] ?? null;
  const selectedPairing = summaries.find((item) => item.profile.id === compareProfileId) ?? null;
  const topFollowThrough = summaries.slice(0, 3);

  return (
    <div className="product-desk">
      <DocumentMeta
        title="AstroNumeric — Relationships Desk"
        description="Track relationship timing, compatibility scores, and your strongest connections."
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Relationships desk</span>
        <h1>Compatibility and synastry — in one place.</h1>
        <p>
          Save people, track compatibility over time, and spot your strongest connection windows.
        </p>
        <div className="product-desk__chips">
          <span className="product-desk__chip">Saved people</span>
          <span className="product-desk__chip">Live pair scores</span>
          <span className="product-desk__chip">Strongest matches</span>
          <span className="product-desk__chip">Charts follow-through</span>
        </div>
        <div className="product-desk__actions">
          <Link to="/charts" className="btn-primary product-desk__action">
            Open compatibility desk
          </Link>
          <Link to="/reading" className="btn-secondary product-desk__action">
            Return to reading
          </Link>
        </div>
      </section>

      <section className="product-desk__grid">
        <article className="product-desk__panel">
          <h2>Current context</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Active profile</span>
              <span className="product-desk__value">{selectedProfile?.name ?? 'Waiting for profile input'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Profile source</span>
              <span className="product-desk__value">{profileMode}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Saved people</span>
              <span className="product-desk__value">{candidateProfiles.length}</span>
            </div>
          </div>
          <p className="product-desk__note">
            {selectedProfile
              ? 'Compatibility scores are ranked against your active profile.'
              : 'Select an active profile to rank saved people by compatibility.'}
          </p>
        </article>

        <article className="product-desk__panel">
          <h2>How to use this suite</h2>
          <ul className="product-desk__list">
            <li className="product-desk__list-item">
              <div>
                <strong>Lock the primary</strong>
                <span className="product-desk__meta">Set your active profile first — everyone else is ranked against it.</span>
              </div>
            </li>
            <li className="product-desk__list-item">
              <div>
                <strong>Review the field</strong>
                <span className="product-desk__meta">Use score, strongest dimension, and summary copy to decide which pairing deserves deeper time.</span>
              </div>
            </li>
            <li className="product-desk__list-item">
              <div>
                <strong>Hand off to charts</strong>
                <span className="product-desk__meta">Selecting a person here opens their full compatibility chart.</span>
              </div>
            </li>
          </ul>
        </article>

        <article className="product-desk__panel product-desk__panel--full">
          <h2>Desk stats</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Loaded pairings</span>
              <span className="product-desk__value">{loading ? 'Loading...' : summaries.length}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Average score</span>
              <span className="product-desk__value">{averageScore !== null ? `${averageScore}%` : '...'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Strongest match</span>
              <span className="product-desk__value">{strongestMatch?.profile.name ?? 'Waiting on summaries'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Selected pairing</span>
              <span className="product-desk__value">{selectedPairing?.profile.name ?? 'None selected'}</span>
            </div>
          </div>
          {error && <p className="product-desk__note">{error}</p>}
        </article>

        <article className="product-desk__panel product-desk__panel--full">
          <h2>Saved people</h2>
          {candidateProfiles.length > 0 ? (
            <div className="product-desk__linkgrid">
              {candidateProfiles.map((profile) => {
                const summary = summaries.find((item) => item.profile.id === profile.id);
                const strongestDimension = summary?.result.dimensions[0] ?? null;
                const score = summary ? Math.round(summary.result.overall_score) : null;

                return (
                  <Link
                    key={profile.id}
                    to="/charts#compatibility-board"
                    className="product-desk__linkcard"
                    onClick={() => setCompareProfileId(profile.id)}
                  >
                    <strong>{profile.name}</strong>
                    <span>
                      {summary
                        ? `${score}% · ${formatScore(score ?? 0)}`
                        : loading
                          ? 'Loading live compatibility summary'
                          : 'Compatibility summary unavailable'}
                    </span>
                    <span>
                      {summary
                        ? strongestDimension
                          ? `${formatDimensionLabel(strongestDimension.name)} leads this pairing.`
                          : summary.result.summary
                        : 'Open this pairing in charts once the suite finishes loading.'}
                    </span>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="product-desk__empty">
              Add a saved profile in the reading desk to see compatibility scores here.
            </div>
          )}
        </article>

        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Follow-through queue</h2>
          {topFollowThrough.length > 0 ? (
            <ul className="product-desk__list">
              {topFollowThrough.map((item) => {
                const score = Math.round(item.result.overall_score);
                const strongestDimension = item.result.dimensions[0] ?? null;

                return (
                  <li key={item.profile.id} className="product-desk__list-item">
                    <div>
                      <strong>{item.profile.name}</strong>
                      <span className="product-desk__meta">
                        {strongestDimension
                          ? `${formatDimensionLabel(strongestDimension.name)} is currently the strongest dimension.`
                          : item.result.summary}
                      </span>
                    </div>
                    <span className="product-desk__badge">{`${score}%`}</span>
                  </li>
                );
              })}
            </ul>
          ) : (
            <p className="product-desk__note">
              {loading
                ? 'Building the live compatibility queue for saved people.'
                : 'Add a second profile to build your compatibility queue.'}
            </p>
          )}
        </article>

        <article className="product-desk__panel">
          <h2>Next move</h2>
          <p className="product-desk__note">
            {selectedPairing
              ? `The pairing with ${selectedPairing.profile.name} is primed for the deeper charts board.`
              : strongestMatch
                ? `Start with ${strongestMatch.profile.name}, then open charts for the full compatibility board.`
                : 'Add a second profile to unlock chart comparisons.'}
          </p>
          <div className="product-desk__actions">
            <Link to="/charts#compatibility-board" className="btn-primary product-desk__action">
              Open charts board
            </Link>
            <Link to="/reading" className="btn-secondary product-desk__action">
              Add another profile
            </Link>
          </div>
        </article>
      </section>
    </div>
  );
}

export default RelationshipsView;