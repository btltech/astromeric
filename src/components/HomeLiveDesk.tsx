import React, { useEffect, useMemo, useState } from 'react';
import {
  fetchCurrentMoonPhase,
  fetchWeeklyForecast,
  type ForecastDay,
  type ProfilePayload,
} from '../api/client';
import { useActiveProfile } from '../hooks';
import type { MoonPhaseInfo, SavedProfile } from '../types';
import './HomeLiveDesk.css';

const previewProfile: ProfilePayload = {
  name: 'Amara Lewis',
  date_of_birth: '1994-11-18',
  time_of_birth: '07:18',
  location: {
    latitude: 51.5074,
    longitude: -0.1278,
    timezone: 'Europe/London',
  },
};

function toProfilePayload(profile: SavedProfile | null): ProfilePayload {
  if (!profile) {
    return previewProfile;
  }

  return {
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth ?? previewProfile.time_of_birth,
    location: {
      latitude: profile.latitude ?? previewProfile.location?.latitude,
      longitude: profile.longitude ?? previewProfile.location?.longitude,
      timezone: profile.timezone ?? previewProfile.location?.timezone,
    },
  };
}

function formatDayLabel(date: string) {
  return new Date(date).toLocaleDateString(undefined, { weekday: 'short' });
}

function getScoreTone(score: number) {
  if (score >= 80) return 'strong';
  if (score >= 60) return 'steady';
  return 'watch';
}

export function HomeLiveDesk() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();

  const requestProfile = useMemo(() => toProfilePayload(activeProfile), [activeProfile]);
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [moonPhase, setMoonPhase] = useState<MoonPhaseInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadLiveDesk() {
      setLoading(true);
      setError(null);

      try {
        const [weeklyData, currentMoonPhase] = await Promise.all([
          fetchWeeklyForecast(requestProfile),
          fetchCurrentMoonPhase(),
        ]);

        if (isCancelled) {
          return;
        }

        setForecast(weeklyData.days);
        setMoonPhase(currentMoonPhase);
      } catch (err) {
        if (isCancelled) {
          return;
        }

        const message = err instanceof Error ? err.message : 'Could not load live timing data.';
        setError(message);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    loadLiveDesk();

    return () => {
      isCancelled = true;
    };
  }, [requestProfile]);

  const strongestDay = forecast.reduce<ForecastDay | null>((best, day) => {
    if (!best || day.score > best.score) {
      return day;
    }
    return best;
  }, null);

  const today = forecast[0] ?? null;
  const sourceLabel = hasActiveProfile ? activeProfileSourceLabel : 'Preview profile';

  return (
    <section className="live-desk" aria-labelledby="live-desk-title">
      <div className="live-desk__header">
        <div>
          <span className="live-desk__eyebrow">This week</span>
          <h2 id="live-desk-title">Your weekly timing, at a glance.</h2>
          <p>
            Live forecast data for the week ahead — score, mood, and the strongest window to act on.
          </p>
        </div>

        <div className="live-desk__status-row">
          <span className="live-desk__status live-desk__status--live">Live API</span>
          <span className="live-desk__status">{sourceLabel}</span>
        </div>
      </div>

      {loading ? (
        <div className="live-desk__loading">
          <div className="live-desk__loading-card" />
          <div className="live-desk__loading-rail">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="live-desk__loading-day" />
            ))}
          </div>
        </div>
      ) : error ? (
        <div className="live-desk__error">
          <strong>Live timing feed unavailable.</strong>
          <p>{error}</p>
        </div>
      ) : (
        <>
          <div className="live-desk__board">
            <article className="live-desk__lead-card">
              <span className="live-desk__card-label">Today</span>
              <strong>
                {today ? `${today.icon} ${today.vibe}` : 'Waiting for forecast'}
              </strong>
              <p>
                {today?.recommendation ?? 'Live daily timing guidance will appear here when available.'}
              </p>

              {moonPhase && (
                <div className="live-desk__phase-pill">
                  <span>{moonPhase.emoji}</span>
                  <span>{moonPhase.phase_name}</span>
                  <span>{Math.round(moonPhase.illumination)}% lit</span>
                </div>
              )}
            </article>

            <article className="live-desk__signal-card">
              <span className="live-desk__card-label">Best of the week</span>
              <strong>
                {strongestDay
                  ? `${formatDayLabel(strongestDay.date)} · ${strongestDay.score}%`
                  : 'No standout day yet'}
              </strong>
              <p>
                {strongestDay?.recommendation ?? 'Check back tomorrow for the strongest window of the week.'}
              </p>
            </article>

            <article className="live-desk__signal-card">
              <span className="live-desk__card-label">Live profile</span>
              <strong>{requestProfile.name}</strong>
              <p>
                {requestProfile.location?.timezone ?? 'UTC'} · {requestProfile.date_of_birth}
              </p>
            </article>
          </div>

          <div className="live-desk__rail">
            {forecast.slice(0, 5).map((day) => (
              <article
                key={day.date}
                className={`live-desk__day live-desk__day--${getScoreTone(day.score)}`}
              >
                <span className="live-desk__day-name">{formatDayLabel(day.date)}</span>
                <strong>{day.icon}</strong>
                <span className="live-desk__day-score">{day.score}%</span>
                <p>{day.vibe}</p>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}