import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { fetchWeeklyForecast, type ForecastDay, type ProfilePayload } from '../api/client';
import { getComparisonUrl } from '../utils/comparison';
import { toast } from './Toast';

interface Props {
  profile: ProfilePayload;
  showShare?: boolean;
}

export function WeeklyVibe({ profile, showShare = true }: Props) {
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const latitude = profile.location?.latitude;
  const longitude = profile.location?.longitude;
  const timezone = profile.location?.timezone;
  const canShareComparison = latitude != null && longitude != null && Boolean(timezone);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchWeeklyForecast(profile);
        if (!cancelled) {
          setForecast(data.days);
        }
      } catch (err) {
        console.error('Failed to load weekly vibe:', err);
        if (!cancelled) {
          setForecast([]);
          setError(err instanceof Error ? err.message : 'Weekly forecast unavailable right now.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [profile]);

  const bestDay = useMemo(
    () =>
      forecast.length > 0
        ? forecast.reduce((best, day) => (day.score > best.score ? day : best))
        : null,
    [forecast]
  );
  const lowestDay = useMemo(
    () =>
      forecast.length > 0
        ? forecast.reduce((lowest, day) => (day.score < lowest.score ? day : lowest))
        : null,
    [forecast]
  );
  const rhythm = useMemo(() => buildWeeklyRhythm(forecast), [forecast]);

  async function handleShareComparison() {
    if (!canShareComparison || latitude == null || longitude == null || !timezone) {
      toast.error('Add birth location details to enable comparison sharing.');
      return;
    }

    try {
      const url = getComparisonUrl({
        name: profile.name,
        dob: profile.date_of_birth,
        tob: profile.time_of_birth,
        lat: latitude,
        lng: longitude,
        tz: timezone,
      });

      await navigator.clipboard.writeText(url);
      toast.success('Comparison link copied! Send it to a friend.');
    } catch (err) {
      console.error('Failed to copy comparison link:', err);
      toast.error('Could not copy the comparison link.');
    }
  }

  if (loading) {
    return (
      <section className="weekly-vibe-section weekly-vibe-section--loading" aria-busy="true">
        <div className="weekly-vibe-header">
          <div className="weekly-vibe-heading">
            <span className="weekly-vibe-eyebrow">Live weekly desk</span>
            <h3 className="weekly-vibe-title">Loading your week ahead</h3>
            <p className="weekly-vibe-copy">
              Pulling the latest daily forecast signals from the backend.
            </p>
          </div>
        </div>

        <div className="weekly-vibe-overview weekly-vibe-overview--loading">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="weekly-vibe-metric weekly-vibe-metric--loading">
              <div className="skeleton-line weekly-vibe-skeleton weekly-vibe-skeleton--label" />
              <div className="skeleton-line weekly-vibe-skeleton weekly-vibe-skeleton--value" />
              <div className="skeleton-line weekly-vibe-skeleton weekly-vibe-skeleton--copy" />
            </div>
          ))}
        </div>

        <div className="vibe-timeline">
          {Array.from({ length: 7 }).map((_, index) => (
            <div key={index} className="vibe-day-card vibe-day-card--loading">
              <div className="skeleton-line weekly-vibe-skeleton weekly-vibe-skeleton--tiny" />
              <div className="skeleton-circle weekly-vibe-skeleton weekly-vibe-skeleton--orb" />
              <div className="skeleton-line weekly-vibe-skeleton weekly-vibe-skeleton--label" />
            </div>
          ))}
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="weekly-vibe-section weekly-vibe-section--empty" role="status">
        <div className="weekly-vibe-header">
          <div className="weekly-vibe-heading">
            <span className="weekly-vibe-eyebrow">Live weekly desk</span>
            <h3 className="weekly-vibe-title">Weekly forecast unavailable</h3>
            <p className="weekly-vibe-copy">{error}</p>
          </div>
        </div>
      </section>
    );
  }

  if (forecast.length === 0 || !bestDay || !lowestDay) {
    return (
      <section className="weekly-vibe-section weekly-vibe-section--empty" role="status">
        <div className="weekly-vibe-header">
          <div className="weekly-vibe-heading">
            <span className="weekly-vibe-eyebrow">Live weekly desk</span>
            <h3 className="weekly-vibe-title">No weekly outlook yet</h3>
            <p className="weekly-vibe-copy">
              Generate or refresh the forecast to see the strongest and lightest days of the week.
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="weekly-vibe-section" aria-labelledby="weekly-vibe-title">
      <div className="weekly-vibe-header">
        <div className="weekly-vibe-heading">
          <span className="weekly-vibe-eyebrow">Live weekly desk</span>
          <h3 id="weekly-vibe-title" className="weekly-vibe-title">Your week ahead</h3>
          <p className="weekly-vibe-copy">{getWeeklySummary(forecast)}</p>
        </div>
        {showShare && (
          <button
            className="btn-aura-share weekly-vibe-share"
            type="button"
            onClick={handleShareComparison}
            disabled={!canShareComparison}
            title={
              canShareComparison
                ? 'Copy a comparison link'
                : 'Add a birth location to enable comparison sharing'
            }
          >
            Share & Compare
          </button>
        )}
      </div>

      <div className="weekly-vibe-overview">
        <article className="weekly-vibe-metric weekly-vibe-metric--best">
          <span className="weekly-vibe-metric__label">Strongest day</span>
          <strong>
            {formatWeekday(bestDay.date, 'long')} · {bestDay.score}%
          </strong>
          <p>{bestDay.recommendation || `${bestDay.vibe} energy is your clearest opening.`}</p>
        </article>

        <article className="weekly-vibe-metric weekly-vibe-metric--watch">
          <span className="weekly-vibe-metric__label">Lightest day</span>
          <strong>
            {formatWeekday(lowestDay.date, 'long')} · {lowestDay.score}%
          </strong>
          <p>
            {lowestDay.recommendation || `Keep ${formatWeekday(lowestDay.date, 'long')} for lighter commitments.`}
          </p>
        </article>

        <article className="weekly-vibe-metric weekly-vibe-metric--rhythm">
          <span className="weekly-vibe-metric__label">Week rhythm</span>
          <strong>
            {rhythm.strong} strong · {rhythm.steady} steady · {rhythm.watch} watch
          </strong>
          <div className="weekly-vibe-rhythm-bar" aria-hidden="true">
            <span
              className="weekly-vibe-rhythm-segment weekly-vibe-rhythm-segment--strong"
              style={{ width: `${(rhythm.strong / forecast.length) * 100}%` }}
            />
            <span
              className="weekly-vibe-rhythm-segment weekly-vibe-rhythm-segment--steady"
              style={{ width: `${(rhythm.steady / forecast.length) * 100}%` }}
            />
            <span
              className="weekly-vibe-rhythm-segment weekly-vibe-rhythm-segment--watch"
              style={{ width: `${(rhythm.watch / forecast.length) * 100}%` }}
            />
          </div>
          <p>{rhythm.copy}</p>
        </article>
      </div>

      <div className="vibe-timeline">
        {(() => {
          const bestIdx = forecast.reduce((bi, d, i, a) => (d.score > a[bi].score ? i : bi), 0);
          const worstIdx = forecast.reduce((wi, d, i, a) => (d.score < a[wi].score ? i : wi), 0);
          // Only show best/worst badges when scores are meaningfully different
          const scoresVary = forecast[bestIdx].score !== forecast[worstIdx].score;

          return forecast.map((day, i) => {
            const dateObj = new Date(day.date);
            const isToday = i === 0;
            const isBest = scoresVary && i === bestIdx;
            const isWorst = scoresVary && i === worstIdx && worstIdx !== bestIdx;

            return (
              <motion.div
                key={day.date}
                className={`vibe-day-card ${isToday ? 'today' : ''} ${isBest ? 'vibe-day-card--best' : ''} ${isWorst ? 'vibe-day-card--worst' : ''}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="vibe-day-header">
                  <span className="vibe-weekday">
                    {dateObj.toLocaleDateString(undefined, { weekday: 'short' })}
                  </span>
                  <span className="vibe-daynum">{dateObj.getDate()}</span>
                </div>
                {isBest && <span className="vibe-badge vibe-badge--best">Best</span>}
                {isWorst && <span className="vibe-badge vibe-badge--worst">Watch</span>}

                <div className="vibe-display" title={day.recommendation}>
                  <div
                    className="vibe-glow"
                    style={{ backgroundColor: getScoreColor(day.score) }}
                  ></div>
                  <span className="vibe-emoji">{day.icon}</span>
                </div>

                <div className="vibe-meta">
                  <span className="vibe-label">{day.vibe}</span>
                  <div className="vibe-dot-container">
                    <div
                      className="vibe-dot"
                      style={{ backgroundColor: getScoreColor(day.score) }}
                    ></div>
                    <span className="vibe-score">{day.score}%</span>
                  </div>
                </div>

                <div className="vibe-strength" aria-hidden="true">
                  <span
                    className="vibe-strength-fill"
                    style={{
                      width: `${Math.max(day.score, 12)}%`,
                      backgroundColor: getScoreColor(day.score),
                    }}
                  />
                </div>

                {day.recommendation && (
                  <p className="vibe-recommendation">{summarizeRecommendation(day.recommendation)}</p>
                )}
              </motion.div>
            );
          });
        })()}
      </div>
    </section>
  );
}

function getWeeklySummary(days: ForecastDay[]): string {
  const best = days.reduce((a, b) => (a.score > b.score ? a : b));
  const worst = days.reduce((a, b) => (a.score < b.score ? a : b));
  // If all days have the same score, no standout day exists
  if (best.score === worst.score) {
    return 'Your energy is steady throughout the week — a good time to keep a consistent routine.';
  }
  const bestDay = new Date(best.date).toLocaleDateString(undefined, { weekday: 'long' });
  const worstDay = new Date(worst.date).toLocaleDateString(undefined, { weekday: 'long' });
  return `Push your most important work to ${bestDay}. Keep ${worstDay} light — your energy will be lower.`;
}

function formatWeekday(date: string, style: 'short' | 'long' = 'short') {
  return new Date(date).toLocaleDateString(undefined, { weekday: style });
}

function buildWeeklyRhythm(days: ForecastDay[]) {
  const strong = days.filter((day) => day.score >= 80).length;
  const steady = days.filter((day) => day.score >= 60 && day.score < 80).length;
  const watch = days.filter((day) => day.score < 60).length;

  if (strong >= 3) {
    return {
      strong,
      steady,
      watch,
      copy: 'This week has multiple strong windows. Batch the heavier decisions instead of spreading them out.',
    };
  }

  if (watch >= 3) {
    return {
      strong,
      steady,
      watch,
      copy: 'The week is uneven. Protect your calendar and leave room to recover when the energy dips.',
    };
  }

  return {
    strong,
    steady,
    watch,
    copy: 'The pattern is mostly steady. Use the standout day for action and let the rest of the week support follow-through.',
  };
}

function summarizeRecommendation(recommendation: string) {
  const firstSentence = recommendation.split('.').find((part) => part.trim().length > 0)?.trim();

  if (!firstSentence) {
    return recommendation;
  }

  if (firstSentence.length <= 64) {
    return `${firstSentence}.`;
  }

  return `${firstSentence.slice(0, 61).trimEnd()}...`;
}

function getScoreColor(score: number) {
  if (score >= 80) return '#ffcc33'; // Gold
  if (score >= 60) return '#a29bfe'; // Purple
  return '#ff5e57'; // Red
}
