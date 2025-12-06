/**
 * Journal.tsx
 * Journal & Accountability component for tracking prediction outcomes
 * and personal reflections.
 */
import { useState, useEffect } from 'react';
import type {
  JournalReading,
  JournalPromptsResponse,
  AccuracyStats,
  JournalInsights,
  AccountabilityReport,
} from '../types';
import {
  fetchJournalPrompts,
  fetchJournalReadings,
  fetchJournalStats,
  fetchAccountabilityReport,
  addJournalEntry,
  recordOutcome,
} from '../api/client';

interface JournalProps {
  profileId?: number;
  token?: string;
  onClose?: () => void;
}

type View = 'overview' | 'readings' | 'report';
type OutcomeType = 'yes' | 'no' | 'partial' | 'neutral';

const OUTCOME_OPTIONS: { value: OutcomeType; emoji: string; label: string }[] = [
  { value: 'yes', emoji: '✅', label: 'Accurate' },
  { value: 'partial', emoji: '🔶', label: 'Partially' },
  { value: 'no', emoji: '❌', label: 'Not Really' },
  { value: 'neutral', emoji: '➖', label: 'Neutral' },
];

export function Journal({ profileId, token, onClose }: JournalProps) {
  const [view, setView] = useState<View>('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [prompts, setPrompts] = useState<JournalPromptsResponse | null>(null);
  const [readings, setReadings] = useState<JournalReading[]>([]);
  const [totalReadings, setTotalReadings] = useState(0);
  const [stats, setStats] = useState<AccuracyStats | null>(null);
  const [insights, setInsights] = useState<JournalInsights | null>(null);
  const [report, setReport] = useState<AccountabilityReport | null>(null);

  // UI states
  const [selectedReading, setSelectedReading] = useState<JournalReading | null>(null);
  const [journalText, setJournalText] = useState('');
  const [reportPeriod, setReportPeriod] = useState<'week' | 'month' | 'year'>('month');
  const [promptScope, setPromptScope] = useState<'daily' | 'weekly' | 'monthly'>('daily');

  // Fetch prompts (no auth needed)
  useEffect(() => {
    fetchJournalPrompts(promptScope)
      .then(setPrompts)
      .catch((err) => console.error('Failed to fetch prompts:', err));
  }, [promptScope]);

  // Fetch authenticated data when we have profile and token
  useEffect(() => {
    if (!profileId || !token) return;

    setLoading(true);
    setError(null);

    Promise.all([
      fetchJournalReadings(profileId, token, 10),
      fetchJournalStats(profileId, token),
    ])
      .then(([readingsRes, statsRes]) => {
        setReadings(readingsRes.readings);
        setTotalReadings(readingsRes.total);
        setStats(statsRes.stats);
        setInsights(statsRes.insights);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load journal data');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [profileId, token]);

  // Load accountability report
  const loadReport = async () => {
    if (!profileId || !token) return;

    setLoading(true);
    try {
      const res = await fetchAccountabilityReport(
        { profile_id: profileId, period: reportPeriod },
        token
      );
      setReport(res.report);
      setView('report');
    } catch (err) {
      setError((err as Error).message || 'Failed to load report');
    } finally {
      setLoading(false);
    }
  };

  // Save journal entry
  const saveJournal = async () => {
    if (!selectedReading || !token || !journalText.trim()) return;

    setLoading(true);
    try {
      await addJournalEntry({ reading_id: selectedReading.id, entry: journalText }, token);
      // Refresh readings
      if (profileId) {
        const res = await fetchJournalReadings(profileId, token, 10);
        setReadings(res.readings);
      }
      setSelectedReading(null);
      setJournalText('');
    } catch (err) {
      setError((err as Error).message || 'Failed to save journal');
    } finally {
      setLoading(false);
    }
  };

  // Record outcome
  const saveOutcome = async (readingId: number, outcome: OutcomeType) => {
    if (!token) return;

    try {
      await recordOutcome({ reading_id: readingId, outcome }, token);
      // Refresh readings and stats
      if (profileId) {
        const [readingsRes, statsRes] = await Promise.all([
          fetchJournalReadings(profileId, token, 10),
          fetchJournalStats(profileId, token),
        ]);
        setReadings(readingsRes.readings);
        setStats(statsRes.stats);
        setInsights(statsRes.insights);
      }
    } catch (err) {
      setError((err as Error).message || 'Failed to record outcome');
    }
  };

  // Render accuracy gauge
  const renderAccuracyGauge = (rate: number) => {
    const radius = 60;
    const circumference = 2 * Math.PI * radius;
    const progress = (rate / 100) * circumference;
    const color =
      rate >= 75 ? '#22c55e' : rate >= 50 ? '#eab308' : rate >= 25 ? '#f97316' : '#ef4444';

    return (
      <div className="journal-gauge">
        <svg viewBox="0 0 150 150" className="gauge-svg">
          <circle
            cx="75"
            cy="75"
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="12"
          />
          <circle
            cx="75"
            cy="75"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            strokeLinecap="round"
            transform="rotate(-90 75 75)"
            className="gauge-progress"
          />
          <text x="75" y="70" textAnchor="middle" className="gauge-value">
            {rate.toFixed(0)}%
          </text>
          <text x="75" y="90" textAnchor="middle" className="gauge-label">
            Accuracy
          </text>
        </svg>
      </div>
    );
  };

  // Render reading card
  const renderReadingCard = (reading: JournalReading) => (
    <div
      key={reading.id}
      className={`journal-reading-card ${selectedReading?.id === reading.id ? 'selected' : ''}`}
      onClick={() => {
        setSelectedReading(reading);
        setJournalText(reading.journal_full || '');
      }}
    >
      <div className="reading-header">
        <span className="reading-scope">{reading.scope_label}</span>
        <span className="reading-date">{reading.formatted_date}</span>
      </div>
      <div className="reading-summary">{reading.content_summary || 'No summary available'}</div>
      <div className="reading-footer">
        <span className="reading-feedback">
          {reading.feedback_emoji || '⏳'}{' '}
          {reading.feedback ? reading.feedback.charAt(0).toUpperCase() + reading.feedback.slice(1) : 'Pending'}
        </span>
        <span className="reading-journal-status">
          {reading.has_journal ? '📝 Journaled' : '✏️ Add notes'}
        </span>
      </div>
    </div>
  );

  // Overview view
  const renderOverview = () => (
    <div className="journal-overview">
      {/* Stats Section */}
      {stats && (
        <div className="journal-stats-section">
          <h3>📊 Your Accuracy</h3>
          {renderAccuracyGauge(stats.accuracy_rate)}
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-value">{stats.total_readings}</span>
              <span className="stat-label">Total Readings</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.rated_readings}</span>
              <span className="stat-label">Rated</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.trend_emoji}</span>
              <span className="stat-label">{stats.trend}</span>
            </div>
          </div>
          <p className="stats-message">{stats.message}</p>
        </div>
      )}

      {/* Insights Section */}
      {insights && insights.insights.length > 0 && (
        <div className="journal-insights-section">
          <h3>💡 Insights</h3>
          <ul className="insights-list">
            {insights.insights.map((insight, idx) => (
              <li key={idx}>{insight}</li>
            ))}
          </ul>
          {insights.journaling_streak > 0 && (
            <div className="streak-badge">
              🔥 {insights.journaling_streak}-day journaling streak!
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <div className="journal-actions">
        <button className="journal-btn primary" onClick={() => setView('readings')}>
          📖 View Readings
        </button>
        <button className="journal-btn secondary" onClick={loadReport}>
          📋 Generate Report
        </button>
      </div>

      {/* Journal Prompts */}
      {prompts && (
        <div className="journal-prompts-section">
          <h3>✍️ Reflection Prompts</h3>
          <div className="prompt-scope-tabs">
            {(['daily', 'weekly', 'monthly'] as const).map((scope) => (
              <button
                key={scope}
                className={`prompt-tab ${promptScope === scope ? 'active' : ''}`}
                onClick={() => setPromptScope(scope)}
              >
                {scope.charAt(0).toUpperCase() + scope.slice(1)}
              </button>
            ))}
          </div>
          <ul className="prompts-list">
            {prompts.prompts.map((prompt, idx) => (
              <li key={idx} className="prompt-item">
                <span className="prompt-category">{prompt.category}</span>
                <span className="prompt-text">{prompt.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  // Readings view
  const renderReadings = () => (
    <div className="journal-readings-view">
      <div className="readings-header">
        <button className="back-btn" onClick={() => setView('overview')}>
          ← Back
        </button>
        <h3>📖 Your Readings ({totalReadings})</h3>
      </div>

      <div className="readings-layout">
        <div className="readings-list">
          {readings.map(renderReadingCard)}
          {readings.length === 0 && (
            <p className="no-readings">No readings yet. Get your first reading to start tracking!</p>
          )}
        </div>

        {selectedReading && (
          <div className="reading-detail">
            <h4>{selectedReading.scope_label} Reading</h4>
            <p className="detail-date">{selectedReading.formatted_date}</p>

            {/* Outcome Rating */}
            <div className="outcome-section">
              <h5>How accurate was this reading?</h5>
              <div className="outcome-buttons">
                {OUTCOME_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    className={`outcome-btn ${selectedReading.feedback === opt.value ? 'selected' : ''}`}
                    onClick={() => saveOutcome(selectedReading.id, opt.value)}
                  >
                    <span className="outcome-emoji">{opt.emoji}</span>
                    <span className="outcome-label">{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Journal Entry */}
            <div className="journal-entry-section">
              <h5>Your Reflection</h5>
              <textarea
                className="journal-textarea"
                placeholder="Write your thoughts, experiences, and reflections..."
                value={journalText}
                onChange={(e) => setJournalText(e.target.value)}
                rows={6}
              />
              <div className="journal-entry-footer">
                <span className="word-count">{journalText.split(/\s+/).filter(Boolean).length} words</span>
                <button
                  className="save-journal-btn"
                  onClick={saveJournal}
                  disabled={!journalText.trim() || loading}
                >
                  {loading ? 'Saving...' : 'Save Entry'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Report view
  const renderReport = () => (
    <div className="journal-report-view">
      <div className="report-header">
        <button className="back-btn" onClick={() => setView('overview')}>
          ← Back
        </button>
        <h3>📋 Accountability Report</h3>
      </div>

      {/* Period selector */}
      <div className="report-period-selector">
        {(['week', 'month', 'year'] as const).map((period) => (
          <button
            key={period}
            className={`period-btn ${reportPeriod === period ? 'active' : ''}`}
            onClick={() => {
              setReportPeriod(period);
              loadReport();
            }}
          >
            {period.charAt(0).toUpperCase() + period.slice(1)}
          </button>
        ))}
      </div>

      {report && (
        <div className="report-content">
          {/* Summary */}
          <div className="report-summary">
            <h4>Summary ({report.period})</h4>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-value">{report.summary.total_readings}</span>
                <span className="summary-label">Readings</span>
              </div>
              <div className="summary-item">
                <span className="summary-value">{report.summary.with_feedback}</span>
                <span className="summary-label">Rated</span>
              </div>
              <div className="summary-item">
                <span className="summary-value">{report.summary.with_journal}</span>
                <span className="summary-label">Journaled</span>
              </div>
              <div className="summary-item">
                <span className="summary-value">{report.summary.engagement_score}%</span>
                <span className="summary-label">Engagement</span>
              </div>
            </div>
            <div className="engagement-rating">
              Rating: <strong>{report.summary.engagement_rating}</strong>
            </div>
          </div>

          {/* Accuracy */}
          <div className="report-accuracy">
            <h4>Accuracy Analysis</h4>
            {renderAccuracyGauge(report.accuracy.accuracy_rate)}
            <div className="accuracy-breakdown">
              {Object.entries(report.accuracy.by_outcome).map(([outcome, count]) => (
                <div key={outcome} className="breakdown-item">
                  <span>{outcome === 'yes' ? '✅' : outcome === 'no' ? '❌' : outcome === 'partial' ? '🔶' : '➖'}</span>
                  <span>{count} readings</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {report.recommendations.length > 0 && (
            <div className="report-recommendations">
              <h4>💡 Recommendations</h4>
              <ul>
                {report.recommendations.map((rec, idx) => (
                  <li key={idx}>{rec.text}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // No auth message
  const renderNoAuth = () => (
    <div className="journal-no-auth">
      <h3>📔 Journal & Accountability</h3>
      <p>Track your cosmic journey and see how accurate your readings are!</p>

      {/* Show prompts even without auth */}
      {prompts && (
        <div className="journal-prompts-section">
          <h4>✍️ Reflection Prompts</h4>
          <div className="prompt-scope-tabs">
            {(['daily', 'weekly', 'monthly'] as const).map((scope) => (
              <button
                key={scope}
                className={`prompt-tab ${promptScope === scope ? 'active' : ''}`}
                onClick={() => setPromptScope(scope)}
              >
                {scope.charAt(0).toUpperCase() + scope.slice(1)}
              </button>
            ))}
          </div>
          <ul className="prompts-list">
            {prompts.prompts.map((prompt, idx) => (
              <li key={idx} className="prompt-item">
                <span className="prompt-category">{prompt.category}</span>
                <span className="prompt-text">{prompt.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="login-prompt">
        <strong>Sign in</strong> to track your readings and build your personal accuracy profile!
      </p>
    </div>
  );

  return (
    <div className="journal-container">
      <div className="journal-header">
        <h2>📔 Journal & Accountability</h2>
        {onClose && (
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        )}
      </div>

      {error && <div className="journal-error">{error}</div>}

      {loading && <div className="journal-loading">Loading...</div>}

      {!loading && !profileId && renderNoAuth()}

      {!loading && profileId && token && (
        <>
          {view === 'overview' && renderOverview()}
          {view === 'readings' && renderReadings()}
          {view === 'report' && renderReport()}
        </>
      )}
    </div>
  );
}

export default Journal;
