import React, { useState, useEffect } from 'react';
import {
  fetchRelationshipTimeline,
  fetchRelationshipTiming,
  fetchBestRelationshipDays,
  fetchVenusStatus,
  fetchRelationshipPhases,
} from '../api/client';
import type {
  RelationshipTimeline as TimelineType,
  RelationshipTimingAnalysis,
  BestRelationshipDay,
  VenusRetrogradeStatus,
  RelationshipPhase,
} from '../types';

type TabType = 'overview' | 'timing' | 'best-days' | 'phases';

export function RelationshipTimeline() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [timeline, setTimeline] = useState<TimelineType | null>(null);
  const [timing, setTiming] = useState<RelationshipTimingAnalysis | null>(null);
  const [bestDays, setBestDays] = useState<BestRelationshipDay[]>([]);
  const [venusStatus, setVenusStatus] = useState<VenusRetrogradeStatus | null>(null);
  const [phases, setPhases] = useState<RelationshipPhase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );

  // Load initial data
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        const [timelineRes, timingRes, venusRes] = await Promise.all([
          fetchRelationshipTimeline(),
          fetchRelationshipTiming(),
          fetchVenusStatus(),
        ]);

        setTimeline(timelineRes);
        setTiming(timingRes);
        setVenusStatus(venusRes);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Load best days when tab changes
  useEffect(() => {
    if (activeTab === 'best-days' && bestDays.length === 0) {
      fetchBestRelationshipDays(30, 60)
        .then((res) => setBestDays(res.best_days))
        .catch(console.error);
    }
  }, [activeTab, bestDays.length]);

  // Load phases when tab changes
  useEffect(() => {
    if (activeTab === 'phases' && phases.length === 0) {
      fetchRelationshipPhases()
        .then((res) => setPhases(res.phases))
        .catch(console.error);
    }
  }, [activeTab, phases.length]);

  // Update timing when date changes
  async function handleDateChange(date: string) {
    setSelectedDate(date);
    try {
      const res = await fetchRelationshipTiming(date);
      setTiming(res);
    } catch (err) {
      console.error('Failed to fetch timing:', err);
    }
  }

  function getRatingColor(rating: string): string {
    switch (rating) {
      case 'Excellent':
        return 'var(--color-success)';
      case 'Good':
        return 'var(--color-info)';
      case 'Moderate':
        return 'var(--color-warning)';
      case 'Challenging':
        return 'var(--color-error)';
      default:
        return 'var(--color-text-muted)';
    }
  }

  function getScoreEmoji(score: number): string {
    if (score >= 85) return '💖';
    if (score >= 70) return '💕';
    if (score >= 50) return '💛';
    return '💔';
  }

  if (loading) {
    return (
      <div className="relationship-timeline loading">
        <div className="loading-spinner">💕</div>
        <p>Loading relationship timeline...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="relationship-timeline error">
        <p className="error-message">❌ {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="relationship-timeline">
      <header className="timeline-header">
        <h2>💕 Relationship Timeline</h2>
        <p className="subtitle">
          Venus & Mars transits guide your heart's journey
        </p>
      </header>

      {/* Venus Status Banner */}
      {venusStatus && (
        <div
          className={`venus-status-banner ${venusStatus.is_retrograde ? 'retrograde' : 'direct'}`}
        >
          <span className="venus-emoji">{venusStatus.emoji}</span>
          <div className="venus-info">
            <strong>
              Venus {venusStatus.is_retrograde ? 'Retrograde' : 'Direct'}
            </strong>
            <p>{venusStatus.advice}</p>
            {venusStatus.is_retrograde && venusStatus.days_remaining && (
              <span className="days-remaining">
                {venusStatus.days_remaining} days remaining
              </span>
            )}
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <nav className="timeline-tabs" role="tablist" aria-label="Relationship timeline sections">
        <button
          role="tab"
          aria-selected={activeTab === 'overview'}
          aria-controls="overview-panel"
          id="overview-tab"
          tabIndex={activeTab === 'overview' ? 0 : -1}
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') setActiveTab('timing');
            if (e.key === 'ArrowLeft') setActiveTab('phases');
          }}
        >
          🌟 Overview
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'timing'}
          aria-controls="timing-panel"
          id="timing-tab"
          tabIndex={activeTab === 'timing' ? 0 : -1}
          className={activeTab === 'timing' ? 'active' : ''}
          onClick={() => setActiveTab('timing')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') setActiveTab('best-days');
            if (e.key === 'ArrowLeft') setActiveTab('overview');
          }}
        >
          ⏰ Timing
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'best-days'}
          aria-controls="best-days-panel"
          id="best-days-tab"
          tabIndex={activeTab === 'best-days' ? 0 : -1}
          className={activeTab === 'best-days' ? 'active' : ''}
          onClick={() => setActiveTab('best-days')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') setActiveTab('phases');
            if (e.key === 'ArrowLeft') setActiveTab('timing');
          }}
        >
          💝 Best Days
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'phases'}
          aria-controls="phases-panel"
          id="phases-tab"
          tabIndex={activeTab === 'phases' ? 0 : -1}
          className={activeTab === 'phases' ? 'active' : ''}
          onClick={() => setActiveTab('phases')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') setActiveTab('overview');
            if (e.key === 'ArrowLeft') setActiveTab('best-days');
          }}
        >
          🏠 Phases
        </button>
      </nav>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Overview Tab */}
        {activeTab === 'overview' && timeline && (
          <div className="overview-tab">
            {/* Current Transits */}
            <section className="current-transits">
              <h3>Current Cosmic Love Weather</h3>
              <div className="transit-cards">
                <div className="transit-card venus">
                  <span className="glyph">{timeline.venus_current.glyph}</span>
                  <h4>Venus in {timeline.venus_current.sign}</h4>
                  <p className="meaning">{timeline.venus_current.meaning}</p>
                  <p className="love-theme">
                    💖 {timeline.venus_current.love_theme}
                  </p>
                </div>
                <div className="transit-card mars">
                  <span className="glyph">{timeline.mars_current.glyph}</span>
                  <h4>Mars in {timeline.mars_current.sign}</h4>
                  <p className="meaning">{timeline.mars_current.meaning}</p>
                </div>
              </div>
            </section>

            {/* Monthly Overview */}
            {timeline.monthly_overview && timeline.monthly_overview.length > 0 && (
              <section className="monthly-overview">
                <h3>Upcoming Months</h3>
                <div className="months-grid">
                  {timeline.monthly_overview.slice(0, 3).map((month) => (
                    <div key={`${month.year}-${month.month}`} className="month-card">
                      <h4>
                        {month.month} {month.year}
                      </h4>
                      <p className="energy">{month.overall_energy}</p>
                      <div className="signs">
                        <span>♀️ {month.venus_signs.join(' → ')}</span>
                        <span>♂️ {month.mars_signs.join(' → ')}</span>
                      </div>
                      {month.events.length > 0 && (
                        <div className="events-count">
                          {month.events.length} event
                          {month.events.length !== 1 ? 's' : ''}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        )}

        {/* Timing Tab */}
        {activeTab === 'timing' && (
          <div className="timing-tab">
            <div className="date-picker">
              <label htmlFor="timing-date">Check timing for:</label>
              <input
                type="date"
                id="timing-date"
                value={selectedDate}
                onChange={(e) => handleDateChange(e.target.value)}
              />
            </div>

            {timing && (
              <div className="timing-result">
                <div
                  className="score-display"
                  style={{ borderColor: getRatingColor(timing.rating) }}
                >
                  <span className="score-emoji">{getScoreEmoji(timing.score)}</span>
                  <span className="score-value">{timing.score}</span>
                  <span
                    className="score-rating"
                    style={{ color: getRatingColor(timing.rating) }}
                  >
                    {timing.rating}
                  </span>
                </div>

                <div className="timing-details">
                  <div className="planet-positions">
                    <span>♀️ Venus in {timing.venus_sign}</span>
                    <span>♂️ Mars in {timing.mars_sign}</span>
                    {timing.venus_retrograde && (
                      <span className="retrograde-badge">♀️℞ Retrograde</span>
                    )}
                  </div>

                  <div className="themes">
                    <h4>Love Themes</h4>
                    <ul>
                      {timing.themes.map((theme, i) => (
                        <li key={i}>{theme}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="advice">
                    <h4>Advice</h4>
                    <p>{timing.advice}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Best Days Tab */}
        {activeTab === 'best-days' && (
          <div className="best-days-tab">
            <h3>Best Days for Love</h3>
            <p className="tab-description">
              High-energy dates for romance, connection, and relationship moves
            </p>

            {bestDays.length === 0 ? (
              <p className="no-results">Loading best days...</p>
            ) : (
              <div className="best-days-list">
                {bestDays.map((day) => (
                  <div key={day.date} className="best-day-card">
                    <div className="day-date">
                      <span className="emoji">{getScoreEmoji(day.score)}</span>
                      <span className="date">
                        {new Date(day.date).toLocaleDateString('en-US', {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </span>
                      <span className="score">{day.score}</span>
                    </div>
                    <div className="day-details">
                      <span className="planets">
                        ♀️ {day.venus_sign} • ♂️ {day.mars_sign}
                      </span>
                      <p className="reason">{day.reason}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Phases Tab */}
        {activeTab === 'phases' && (
          <div className="phases-tab">
            <h3>Relationship Phases</h3>
            <p className="tab-description">
              How the 12 astrological houses influence your love life
            </p>

            {phases.length === 0 ? (
              <p className="no-results">Loading phases...</p>
            ) : (
              <div className="phases-grid">
                {phases.map((phase) => (
                  <div key={phase.house} className="phase-card">
                    <div className="house-number">{phase.house}</div>
                    <h4>{phase.theme}</h4>
                    <p>{phase.description}</p>
                    <span className="timing">{phase.timing}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default RelationshipTimeline;
