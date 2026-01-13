import React, { useState, useEffect, useCallback } from 'react';
import type { TimingAdviceResult, TimingActivity, TimingDayResult, NewProfileForm } from '../types';
import { fetchTimingAdvice, fetchBestDays, fetchTimingActivities } from '../api/client';

interface TimingAdvisorProps {
  profile?: NewProfileForm | null;
  defaultLatitude?: number;
  defaultLongitude?: number;
  onClose?: () => void;
}

// Activity icons mapping
const ACTIVITY_ICONS: Record<string, string> = {
  business_meeting: '💼',
  travel: '✈️',
  romance_date: '❤️',
  signing_contracts: '📝',
  job_interview: '🎯',
  starting_project: '🚀',
  creative_work: '🎨',
  medical_procedure: '⚕️',
  financial_decision: '💰',
  meditation_spiritual: '🧘',
};

// Rating colors
const RATING_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  Excellent: { bg: 'rgba(46, 213, 115, 0.15)', border: '#2ed573', text: '#2ed573' },
  Good: { bg: 'rgba(74, 222, 128, 0.15)', border: '#4ade80', text: '#4ade80' },
  Moderate: { bg: 'rgba(251, 191, 36, 0.15)', border: '#fbbf24', text: '#fbbf24' },
  Challenging: { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', text: '#ef4444' },
};

export default function TimingAdvisor({
  profile,
  defaultLatitude = 40.7128,
  defaultLongitude = -74.006,
  onClose,
}: TimingAdvisorProps) {
  const [activities, setActivities] = useState<TimingActivity[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<string>('business_meeting');
  const [timingResult, setTimingResult] = useState<TimingAdviceResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'today' | 'week'>('today');
  const [weekResults, setWeekResults] = useState<TimingDayResult[]>([]);

  // Fetch available activities on mount
  useEffect(() => {
    fetchTimingActivities()
      .then((data) => {
        setActivities(data.activities);
        if (data.activities.length > 0) {
          setSelectedActivity(data.activities[0].id);
        }
      })
      .catch((err) => {
        console.error('Failed to fetch activities:', err);
      });
  }, []);

  // Fetch timing advice when activity changes
  const fetchAdvice = useCallback(async () => {
    if (!selectedActivity) return;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchTimingAdvice({
        activity: selectedActivity,
        latitude: profile?.latitude ?? defaultLatitude,
        longitude: profile?.longitude ?? defaultLongitude,
        tz: profile?.timezone ?? 'UTC',
        profile: profile
          ? {
              name: profile.name,
              date_of_birth: profile.date_of_birth,
              time_of_birth: profile.time_of_birth ?? '12:00',
              location: {
                latitude: profile.latitude ?? defaultLatitude,
                longitude: profile.longitude ?? defaultLongitude,
                timezone: profile.timezone ?? 'UTC',
              },
            }
          : undefined,
      });
      setTimingResult(result);

      // Also fetch week view
      const weekData = await fetchBestDays({
        activity: selectedActivity,
        days_ahead: 7,
        latitude: profile?.latitude ?? defaultLatitude,
        longitude: profile?.longitude ?? defaultLongitude,
        tz: profile?.timezone ?? 'UTC',
        profile: profile
          ? {
              name: profile.name,
              date_of_birth: profile.date_of_birth,
              time_of_birth: profile.time_of_birth ?? '12:00',
              location: {
                latitude: profile.latitude ?? defaultLatitude,
                longitude: profile.longitude ?? defaultLongitude,
                timezone: profile.timezone ?? 'UTC',
              },
            }
          : undefined,
      });
      setWeekResults(weekData.best_days);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch timing advice');
    } finally {
      setLoading(false);
    }
  }, [selectedActivity, profile, defaultLatitude, defaultLongitude]);

  useEffect(() => {
    fetchAdvice();
  }, [fetchAdvice]);

  const renderScoreCircle = (score: number, rating: string, size: 'small' | 'large' = 'large') => {
    const colors = RATING_COLORS[rating] || RATING_COLORS.Moderate;
    const circumference = 2 * Math.PI * (size === 'large' ? 45 : 25);
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
      <div
        className={`timing-score-circle timing-score-circle--${size}`}
        style={{ '--score-color': colors.text } as React.CSSProperties}
      >
        <svg viewBox="0 0 100 100">
          <circle className="timing-score-bg" cx="50" cy="50" r={size === 'large' ? 45 : 25} />
          <circle
            className="timing-score-progress"
            cx="50"
            cy="50"
            r={size === 'large' ? 45 : 25}
            style={{
              strokeDasharray: circumference,
              strokeDashoffset,
              stroke: colors.text,
            }}
          />
        </svg>
        <div className="timing-score-value">
          <span className="timing-score-number">{score}</span>
          {size === 'large' && <span className="timing-score-label">{rating}</span>}
        </div>
      </div>
    );
  };

  const renderBreakdown = (breakdown: TimingDayResult['breakdown']) => {
    const factors = [
      { key: 'planetary_hour', label: 'Planetary Hour', icon: '🪐' },
      { key: 'moon_phase', label: 'Moon Phase', icon: '🌙' },
      { key: 'moon_sign', label: 'Moon Sign', icon: '♈' },
      { key: 'retrograde', label: 'Retrogrades', icon: '↩️' },
      { key: 'voc_moon', label: 'VOC Moon', icon: '⚠️' },
      { key: 'personal_day', label: 'Personal Day', icon: '🔢' },
    ];

    return (
      <div className="timing-breakdown">
        {factors.map(({ key, label, icon }) => {
          const value = breakdown[key as keyof typeof breakdown];
          if (value === undefined) return null;

          const barWidth = Math.max(0, Math.min(100, value));
          const barColor = value >= 70 ? '#2ed573' : value >= 50 ? '#fbbf24' : '#ef4444';

          return (
            <div key={key} className="timing-breakdown-item">
              <div className="timing-breakdown-label">
                <span className="timing-breakdown-icon">{icon}</span>
                <span>{label}</span>
              </div>
              <div className="timing-breakdown-bar">
                <div
                  className="timing-breakdown-fill"
                  style={{ width: `${barWidth}%`, backgroundColor: barColor }}
                />
              </div>
              <span className="timing-breakdown-value">{value}</span>
            </div>
          );
        })}
      </div>
    );
  };

  const renderDayCard = (day: TimingDayResult, isToday = false) => {
    const colors = RATING_COLORS[day.rating] || RATING_COLORS.Moderate;
    const activityIcon = ACTIVITY_ICONS[day.activity] || '📅';

    return (
      <div
        className={`timing-day-card ${isToday ? 'timing-day-card--today' : ''}`}
        style={{ borderColor: colors.border, backgroundColor: colors.bg }}
      >
        <div className="timing-day-header">
          <div className="timing-day-date">
            <span className="timing-day-weekday">{day.weekday || 'Today'}</span>
            <span className="timing-day-full-date">{day.date}</span>
          </div>
          {renderScoreCircle(day.score, day.rating, 'small')}
        </div>

        <div className="timing-day-info">
          <div className="timing-day-emoji">{day.emoji}</div>
          <div className="timing-day-details">
            <span className="timing-day-phase">🌙 {day.current_phase}</span>
            <span className="timing-day-moon-sign">Moon in {day.moon_sign}</span>
          </div>
        </div>

        {day.warnings.length > 0 && (
          <div className="timing-day-warnings">
            {day.warnings.slice(0, 2).map((warning, i) => (
              <span key={i} className="timing-warning-tag">
                ⚠️ {warning}
              </span>
            ))}
          </div>
        )}

        {day.recommendations.length > 0 && (
          <div className="timing-day-recommendations">
            {day.recommendations.slice(0, 2).map((rec, i) => (
              <span key={i} className="timing-rec-tag">
                ✓ {rec}
              </span>
            ))}
          </div>
        )}

        {day.best_hours.length > 0 && (
          <div className="timing-best-hours">
            <span className="timing-best-hours-label">Best Hours:</span>
            {day.best_hours.slice(0, 3).map((hour, i) => (
              <span key={i} className="timing-hour-chip">
                {hour.start}-{hour.end} ({hour.planet})
              </span>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="timing-advisor">
      <div className="timing-advisor-header">
        <h2>⏰ Timing Advisor</h2>
        <p>Find the best time for your activities based on cosmic alignments</p>
        {onClose && (
          <button className="timing-close-btn" onClick={onClose}>
            ✕
          </button>
        )}
      </div>

      {/* Activity Selector */}
      <div className="timing-activity-selector">
        <label>What would you like to do?</label>
        <div className="timing-activity-grid">
          {activities.map((activity) => (
            <button
              key={activity.id}
              className={`timing-activity-btn ${
                selectedActivity === activity.id ? 'timing-activity-btn--active' : ''
              }`}
              onClick={() => setSelectedActivity(activity.id)}
            >
              <span className="timing-activity-icon">{ACTIVITY_ICONS[activity.id] || '📅'}</span>
              <span className="timing-activity-name">{activity.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* View Mode Tabs */}
      <div className="timing-view-tabs">
        <button
          className={`timing-tab ${viewMode === 'today' ? 'timing-tab--active' : ''}`}
          onClick={() => setViewMode('today')}
        >
          Today's Analysis
        </button>
        <button
          className={`timing-tab ${viewMode === 'week' ? 'timing-tab--active' : ''}`}
          onClick={() => setViewMode('week')}
        >
          Week Overview
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="timing-loading">
          <div className="timing-spinner" />
          <span>Analyzing cosmic alignments...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="timing-error">
          <span>❌ {error}</span>
          <button onClick={fetchAdvice}>Try Again</button>
        </div>
      )}

      {/* Today's Analysis */}
      {!loading && !error && timingResult && viewMode === 'today' && (
        <div className="timing-today-view">
          {/* Main Score */}
          <div className="timing-main-result">
            <div className="timing-score-container">
              {renderScoreCircle(timingResult.today.score, timingResult.today.rating)}
              <div className="timing-activity-label">
                <span className="timing-activity-emoji">
                  {ACTIVITY_ICONS[selectedActivity] || '📅'}
                </span>
                <span>{timingResult.activity}</span>
              </div>
            </div>

            {/* Advice */}
            <div className="timing-advice-box">
              <p>{timingResult.advice}</p>
            </div>
          </div>

          {/* Today's Card */}
          {renderDayCard(timingResult.today, true)}

          {/* Score Breakdown */}
          <div className="timing-breakdown-section">
            <h3>Score Breakdown</h3>
            {renderBreakdown(timingResult.today.breakdown)}
          </div>

          {/* Best Upcoming */}
          {!timingResult.today_is_best && timingResult.best_upcoming && (
            <div className="timing-best-day-section">
              <h3>✨ Better Day Available</h3>
              <p>
                Consider {timingResult.best_upcoming.weekday} for better results (score:{' '}
                {timingResult.best_upcoming.score})
              </p>
              {renderDayCard(timingResult.best_upcoming)}
            </div>
          )}
        </div>
      )}

      {/* Week Overview */}
      {!loading && !error && weekResults.length > 0 && viewMode === 'week' && (
        <div className="timing-week-view">
          <div className="timing-week-grid">
            {weekResults.map((day, i) => (
              <div key={i} className="timing-week-item">
                {renderDayCard(day, day.date === timingResult?.today.date)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tips Section */}
      <div className="timing-tips">
        <h3>💡 Timing Tips</h3>
        <ul>
          <li>
            <strong>Planetary Hours:</strong> Each hour of the day is ruled by a planet. Jupiter
            hours are great for expansion, Mercury for communication.
          </li>
          <li>
            <strong>Moon Phase:</strong> Waxing moon (New to Full) is best for new beginnings.
            Waning moon (Full to New) is best for releasing and completing.
          </li>
          <li>
            <strong>VOC Moon:</strong> Avoid starting important activities when the Moon is
            void-of-course.
          </li>
          <li>
            <strong>Retrogrades:</strong> Mercury retrograde suggests review and revision rather
            than new contracts or purchases.
          </li>
        </ul>
      </div>
    </div>
  );
}
