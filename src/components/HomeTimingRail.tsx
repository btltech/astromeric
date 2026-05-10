import React, { useEffect, useMemo, useState } from 'react';
import {
  fetchTimingActivities,
  fetchTimingAdvice,
  type ProfilePayload,
} from '../api/client';
import { useActiveProfile } from '../hooks';
import type { SavedProfile, TimingActivity, TimingAdviceResult } from '../types';
import './HomeTimingRail.css';

const previewProfile: ProfilePayload = {
  name: 'Amara Lewis',
  date_of_birth: '1994-11-18',
  time_of_birth: '08:30',
  place_of_birth: 'London, UK',
  location: {
    latitude: 51.5072,
    longitude: -0.1276,
    timezone: 'Europe/London',
  },
  house_system: 'Placidus',
};

const fallbackActivities: TimingActivity[] = [
  { id: 'business_meeting', name: 'Business Meeting' },
  { id: 'financial_decision', name: 'Financial Decision' },
  { id: 'romance_date', name: 'Romantic Date' },
];

const preferredActivityIds = new Set(fallbackActivities.map((activity) => activity.id));

function toProfilePayload(profile: SavedProfile | null): ProfilePayload {
  if (!profile) {
    return previewProfile;
  }

  return {
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth ?? previewProfile.time_of_birth,
    place_of_birth: profile.place_of_birth ?? previewProfile.place_of_birth,
    location: {
      latitude: profile.latitude ?? previewProfile.location?.latitude,
      longitude: profile.longitude ?? previewProfile.location?.longitude,
      timezone: profile.timezone ?? previewProfile.location?.timezone,
    },
    house_system: profile.house_system ?? previewProfile.house_system,
  };
}

function formatWeekday(date: string, weekday?: string) {
  return weekday ?? new Date(date).toLocaleDateString(undefined, { weekday: 'short' });
}

function getScoreTone(score: number) {
  if (score >= 80) return 'strong';
  if (score >= 65) return 'steady';
  return 'watch';
}

export function HomeTimingRail() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();

  const requestProfile = useMemo(() => toProfilePayload(activeProfile), [activeProfile]);
  const [activities, setActivities] = useState<TimingActivity[]>(fallbackActivities);
  const [selectedActivity, setSelectedActivity] = useState<string>(fallbackActivities[0].id);
  const [timingResult, setTimingResult] = useState<TimingAdviceResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadActivities() {
      try {
        const data = await fetchTimingActivities();
        if (isCancelled) {
          return;
        }

        const filtered = data.activities.filter((activity) => preferredActivityIds.has(activity.id));
        const nextActivities = filtered.length > 0 ? filtered : fallbackActivities;

        setActivities(nextActivities);
        setSelectedActivity((current) =>
          nextActivities.some((activity) => activity.id === current) ? current : nextActivities[0].id
        );
      } catch {
        if (!isCancelled) {
          setActivities(fallbackActivities);
        }
      }
    }

    loadActivities();

    return () => {
      isCancelled = true;
    };
  }, []);

  useEffect(() => {
    let isCancelled = false;

    async function loadTiming() {
      setLoading(true);
      setError(null);

      try {
        const result = await fetchTimingAdvice({
          activity: selectedActivity,
          latitude: requestProfile.location?.latitude ?? 0,
          longitude: requestProfile.location?.longitude ?? 0,
          tz: requestProfile.location?.timezone ?? 'UTC',
          profile: requestProfile,
        });

        if (isCancelled) {
          return;
        }

        setTimingResult(result);
      } catch (err) {
        if (isCancelled) {
          return;
        }

        const message = err instanceof Error ? err.message : 'Could not load live timing windows.';
        setTimingResult(null);
        setError(message);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    loadTiming();

    return () => {
      isCancelled = true;
    };
  }, [requestProfile, selectedActivity]);

  const sourceLabel = hasActiveProfile ? activeProfileSourceLabel : 'Preview profile';
  const bestHours = timingResult?.today.best_hours.slice(0, 3) ?? [];
  const nextDays = timingResult?.all_days.slice(0, 5) ?? [];

  return (
    <section className="timing-rail" aria-labelledby="timing-rail-title">
      <div className="timing-rail__header">
        <div>
          <span className="timing-rail__eyebrow">Live decision windows</span>
          <h2 id="timing-rail-title">The best time to act — for whatever you're planning next.</h2>
          <p>
            Activity-specific timing scores, best hours, and upcoming windows — updated daily.
          </p>
        </div>

        <div className="timing-rail__status-row">
          <span className="timing-rail__status timing-rail__status--live">Live API</span>
          <span className="timing-rail__status">{sourceLabel}</span>
        </div>
      </div>

      <div className="timing-rail__tabs" role="tablist" aria-label="Timing activities">
        {activities.map((activity) => (
          <button
            key={activity.id}
            type="button"
            className={`timing-rail__tab ${selectedActivity === activity.id ? 'timing-rail__tab--active' : ''}`}
            onClick={() => setSelectedActivity(activity.id)}
          >
            {activity.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="timing-rail__loading">
          <div className="timing-rail__loading-card" />
          <div className="timing-rail__loading-days">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className="timing-rail__loading-day" />
            ))}
          </div>
        </div>
      ) : error || !timingResult ? (
        <div className="timing-rail__error">
          <strong>Live timing windows unavailable.</strong>
          <p>{error ?? 'The timing advisor feed did not return a result.'}</p>
        </div>
      ) : (
        <>
          <div className="timing-rail__grid">
            <article className="timing-rail__hero-card">
              <span className="timing-rail__card-label">Today</span>
              <strong>{`${timingResult.today.emoji} ${timingResult.today.rating} · ${timingResult.today.score}%`}</strong>
              <p>{timingResult.advice}</p>

              <div className="timing-rail__meta-row">
                <span>{timingResult.activity}</span>
                <span>{timingResult.today.current_phase}</span>
                <span>{`Moon in ${timingResult.today.moon_sign}`}</span>
              </div>
            </article>

            <article className="timing-rail__signal-card">
              <span className="timing-rail__card-label">Best upcoming</span>
              <strong>{`${formatWeekday(timingResult.best_upcoming.date, timingResult.best_upcoming.weekday)} · ${timingResult.best_upcoming.score}%`}</strong>
              <p>
                {timingResult.today_is_best
                  ? 'Today already holds the strongest window for this activity.'
                  : timingResult.best_upcoming.recommendations[0] ?? 'No standout window found for this activity yet.'}
              </p>
            </article>

            <article className="timing-rail__signal-card">
              <span className="timing-rail__card-label">Best hours</span>
              <div className="timing-rail__hours">
                {bestHours.map((hour) => (
                  <div key={`${hour.start}-${hour.planet}`} className="timing-rail__hour-pill">
                    <strong>{`${hour.start} - ${hour.end}`}</strong>
                    <span>{hour.planet}</span>
                  </div>
                ))}
              </div>
            </article>
          </div>

          <div className="timing-rail__days">
            {nextDays.map((day) => (
              <article key={day.date} className={`timing-rail__day timing-rail__day--${getScoreTone(day.score)}`}>
                <span className="timing-rail__day-name">{formatWeekday(day.date, day.weekday)}</span>
                <strong>{day.emoji}</strong>
                <span className="timing-rail__day-score">{`${day.score}%`}</span>
                <p>{day.rating}</p>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}