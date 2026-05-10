import React, { useState } from 'react';
import type { CompatibilityResult } from '../types';

interface Props {
  data: CompatibilityResult;
}

// Helper to get score color
const getScoreColor = (score: number) => {
  if (score >= 80) return '#4ade80'; // Green
  if (score >= 60) return '#facc15'; // Yellow
  if (score >= 40) return '#f97316'; // Orange
  return '#ef4444'; // Red
};

// Helper to get score label
const getScoreLabel = (score: number) => {
  if (score >= 90) return 'Exceptional Match';
  if (score >= 80) return 'Strong Match';
  if (score >= 70) return 'Good Match';
  if (score >= 60) return 'Promising — Needs Effort';
  if (score >= 50) return 'Workable with Effort';
  if (score >= 40) return 'Challenging';
  return 'Major Differences';
};

// Generate red flags based on scores and challenges
const getRedFlags = (data: CompatibilityResult): string[] => {
  const redFlags: string[] = [];
  const overallScore = Math.round(
    (Object.values(data.topic_scores).reduce((a, b) => a + b, 0) /
      Object.values(data.topic_scores).length) *
      10
  );

  // Add red flags based on low scores
  if (data.topic_scores.communication < 4) {
    redFlags.push('Communication styles may clash - requires extra patience');
  }
  if (data.topic_scores.emotional < 4) {
    redFlags.push('Emotional needs differ significantly - discuss expectations early');
  }
  if (data.topic_scores.values < 4) {
    redFlags.push('Core values may not align - have honest conversations about life goals');
  }
  if (overallScore < 50) {
    redFlags.push('Overall compatibility is low — focus on one shared goal first and see if you can move forward on that before everything else.');
  }

  // Add specific element-based red flags
  if (
    data.challenges.some(
      (c) => c.toLowerCase().includes('control') || c.toLowerCase().includes('power')
    )
  ) {
    redFlags.push('Power dynamics may come up — decide early on who handles what so it does not become a daily source of friction.');
  }
  if (
    data.challenges.some(
      (c) => c.toLowerCase().includes('trust') || c.toLowerCase().includes('jealous')
    )
  ) {
    redFlags.push('Trust issues may arise - prioritize transparency');
  }

  return redFlags.slice(0, 3); // Limit to top 3
};

// Plain-English verdict that directly answers "Is this a good match?"
const getCompatSummary = (score: number): string => {
  if (score >= 80) return 'Yes — strong natural connection that flows easily with minimal effort.';
  if (score >= 60) return 'Promising, but communication is the make-or-break factor here.';
  if (score >= 40) return 'More work than easy — worth it only if both actively choose it.';
  return 'Fundamentally different approaches to life — can work, but takes consistent effort from both.';
};

// Dynamic action tips based on weakest areas
const getActionTips = (data: CompatibilityResult, score: number): string[] => {
  const tips: string[] = [];

  if (data.topic_scores.communication < 6) {
    tips.push('Set a weekly 15-minute check-in where each person shares one concern without interruption');
  } else {
    tips.push('Use your communication strength — be the one who raises issues before they become problems');
  }

  if (data.topic_scores.emotional < 6) {
    tips.push('Ask each other “what do you need right now?” — your emotional styles differ more than you think');
  } else if (data.topic_scores.values < 6) {
    tips.push('Write down your three relationship non-negotiables and share them openly');
  } else {
    tips.push('Plan one activity per month that is completely new to both of you');
  }

  if (score < 60) {
    tips.push('Agree on one shared goal — having a common direction reduces day-to-day friction');
  } else {
    tips.push('Focus on what you are building together, not just what feels good in the moment');
  }

  return tips;
};

// Category definitions for detailed breakdown
const CATEGORIES = [
  { key: 'general', label: 'Overall Chemistry', icon: '💫' },
  { key: 'emotional', label: 'Emotional Bond', icon: '💕' },
  { key: 'communication', label: 'Communication', icon: '💬' },
  { key: 'values', label: 'Shared Values', icon: '🎯' },
  { key: 'intimacy', label: 'Physical Connection', icon: '🔥' },
  { key: 'growth', label: 'Growth Potential', icon: '🌱' },
  { key: 'spiritual', label: 'Spiritual Alignment', icon: '✨' },
];

type TabType = 'overview' | 'details' | 'advice';

export function CompatibilityCard({ data }: Props) {
  const [detailsOpen, setDetailsOpen] = useState(false);

  // Calculate overall score (0-100 scale)
  const rawScore =
    Object.values(data.topic_scores).reduce((a, b) => a + b, 0) /
    Object.values(data.topic_scores).length;
  const overallScore = Math.min(Math.round(rawScore * 10), 100);
  const scoreColor = getScoreColor(overallScore);
  const scoreLabel = getScoreLabel(overallScore);
  const redFlags = getRedFlags(data);

  return (
    <div className="compatibility-enhanced">
      {/* Header — names + plain outcome */}
      <div className="compat-header">
        <div className="compat-names">
          <span className="person-name">{data.people[0].name}</span>
          <span className="heart-icon">💕</span>
          <span className="person-name">{data.people[1].name}</span>
        </div>

        <div className="compat-outcome-banner" style={{ borderColor: scoreColor }}>
          <span className="compat-outcome-label" style={{ color: scoreColor }}>{scoreLabel}</span>
          <p className="compat-outcome-summary">{getCompatSummary(overallScore)}</p>
        </div>
      </div>

      {/* WHAT TO DO */}
      <div className="compat-action-section">
        <h4 className="compat-action-title">🎯 What to do</h4>
        <p className="compat-advice-text">{data.advice}</p>
        <div className="tips-grid">
          {getActionTips(data, overallScore).map((tip, i) => (
            <div key={i} className="tip-card">
              <span className="tip-number">{i + 1}</span>
              <p>{tip}</p>
            </div>
          ))}
        </div>

        <div className="cosmic-timing" style={{ marginTop: '1rem' }}>
          <strong>When to spend time together: </strong>
          {overallScore >= 70
            ? 'Any time works — small daily moments build this connection more than big occasions.'
            : 'One-on-one time with no distractions matters more here than how often you see each other.'}
        </div>
      </div>

      {/* WHAT TO WATCH OUT FOR */}
      {(redFlags.length > 0 || data.challenges.length > 0) && (
        <div className="compat-list challenges" style={{ marginTop: '1rem' }}>
          <h4>⚡ Watch out for</h4>
          <ul>
            {redFlags.length > 0
              ? redFlags.map((rf, i) => (
                  <li key={i}>
                    <span className="list-icon">⚠</span>
                    {rf}
                  </li>
                ))
              : data.challenges.slice(0, 3).map((c, i) => (
                  <li key={i}>
                    <span className="list-icon">!</span>
                    {c}
                  </li>
                ))}
          </ul>
        </div>
      )}

      {/* STRENGTHS */}
      <div className="compat-list strengths" style={{ marginTop: '1rem' }}>
        <h4>💪 Where you're strong together</h4>
        <ul>
          {data.strengths.map((s, i) => (
            <li key={i}>
              <span className="list-icon">✓</span>
              {s}
            </li>
          ))}
        </ul>
      </div>

      {/* DETAILS — collapsible (scores, breakdown) */}
      <div className="compat-details-toggle-wrapper">
        <button
          className="compat-details-toggle"
          onClick={() => setDetailsOpen((v) => !v)}
          aria-expanded={detailsOpen}
        >
          <span>See compatibility breakdown</span>
          <span className={`compat-toggle-chevron ${detailsOpen ? 'open' : ''}`}>▾</span>
        </button>

        {detailsOpen && (
          <div className="compat-details-panel">
            {/* Score ring — de-emphasised in details */}
            <div className="score-display-compact" style={{ '--score-color': scoreColor } as React.CSSProperties}>
              <div className="score-ring-small">
                <svg viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(136,192,208,0.1)" strokeWidth="6" />
                  <circle
                    cx="40" cy="40" r="34" fill="none"
                    stroke={scoreColor} strokeWidth="6"
                    strokeDasharray={`${(overallScore / 100) * 213.628} 213.628`}
                    strokeLinecap="round"
                    transform="rotate(-90 40 40)"
                  />
                </svg>
                <div className="score-value-small">
                  <span style={{ fontSize: '1.4rem', fontWeight: 700, color: scoreColor }}>{overallScore}</span>
                  <span style={{ fontSize: '0.75rem', color: scoreColor }}>%</span>
                </div>
              </div>
              <p className="score-detail-note">Overall compatibility score</p>
            </div>

            {/* Category scores */}
            <div className="detailed-scores">
              {CATEGORIES.map((cat) => {
                const score = (data.topic_scores[cat.key] || 5) * 10;
                const catColor = getScoreColor(score);
                return (
                  <div key={cat.key} className="category-score">
                    <div className="category-header">
                      <span className="category-icon">{cat.icon}</span>
                      <span className="category-label">{cat.label}</span>
                      <span className="category-value" style={{ color: catColor }}>
                        {Math.round(score)}%
                      </span>
                    </div>
                    <div className="category-bar">
                      <div className="category-fill" style={{ width: `${score}%`, background: catColor }} />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Element dynamics */}
            <div className="element-harmony" style={{ marginTop: '1rem' }}>
              <h4>🌀 How your energies interact</h4>
              <div className="elements-display">
                <span className="element-badge">
                  {(data.people[0] as any).sign} ({(data.people[0] as any).sign && getElement((data.people[0] as any).sign)})
                </span>
                <span className="element-connector">×</span>
                <span className="element-badge">
                  {(data.people[1] as any).sign} ({(data.people[1] as any).sign && getElement((data.people[1] as any).sign)})
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .compatibility-enhanced {
          background: var(--card-bg);
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid rgba(136, 192, 208, 0.2);
        }

        .compat-header {
          text-align: center;
          margin-bottom: 1.5rem;
        }

        .compat-names {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
          margin-bottom: 1.5rem;
        }

        .person-name {
          font-size: 1.25rem;
          font-weight: 600;
          color: var(--text);
        }

        .heart-icon {
          font-size: 1.5rem;
        }

        .score-display {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
        }

        .score-ring {
          position: relative;
          width: 120px;
          height: 120px;
        }

        .score-ring svg {
          width: 100%;
          height: 100%;
        }

        .score-progress {
          transition: stroke-dasharray 1s ease-out;
        }

        .score-value {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          display: flex;
          align-items: baseline;
        }

        .score-number {
          font-size: 2.5rem;
          font-weight: 700;
          color: var(--score-color);
        }

        .score-percent {
          font-size: 1rem;
          color: var(--score-color);
        }

        .score-label {
          font-size: 0.9rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .compat-tabs {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          border-bottom: 1px solid rgba(136, 192, 208, 0.2);
          padding-bottom: 1rem;
        }

        .compat-tab {
          flex: 1;
          padding: 0.75rem;
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(136, 192, 208, 0.2);
          border-radius: 8px;
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.9rem;
        }

        .compat-tab:hover {
          border-color: rgba(136, 192, 208, 0.4);
        }

        .compat-tab.active {
          background: rgba(136, 192, 208, 0.2);
          border-color: var(--primary);
          color: var(--primary);
        }

        .quick-stats {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .stat-item {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 1rem;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 12px;
        }

        .stat-emoji {
          font-size: 1.5rem;
          margin-bottom: 0.5rem;
        }

        .stat-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          margin-bottom: 0.25rem;
        }

        .stat-value {
          font-size: 0.95rem;
          color: var(--text);
          font-weight: 500;
        }

        .compat-list {
          margin-bottom: 1.25rem;
          padding: 1rem;
          border-radius: 12px;
        }

        .compat-list.strengths {
          background: rgba(74, 222, 128, 0.1);
          border: 1px solid rgba(74, 222, 128, 0.2);
        }

        .compat-list.challenges {
          background: rgba(250, 204, 21, 0.1);
          border: 1px solid rgba(250, 204, 21, 0.2);
        }

        .compat-list.red-flags {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .compat-list h4 {
          margin: 0 0 0.75rem;
          font-size: 1rem;
        }

        .compat-list ul {
          margin: 0;
          padding: 0;
          list-style: none;
        }

        .compat-list li {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
          color: var(--text-muted);
        }

        .compat-list li:last-child {
          margin-bottom: 0;
        }

        .list-icon {
          flex-shrink: 0;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          font-size: 0.7rem;
          font-weight: 600;
        }

        .strengths .list-icon {
          background: rgba(74, 222, 128, 0.2);
          color: #4ade80;
        }

        .challenges .list-icon {
          background: rgba(250, 204, 21, 0.2);
          color: #facc15;
        }

        .red-flags .list-icon {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
        }

        .detailed-scores {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .category-score {
          padding: 0.75rem;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 8px;
        }

        .category-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .category-icon {
          font-size: 1.1rem;
        }

        .category-label {
          flex: 1;
          font-size: 0.9rem;
          color: var(--text);
        }

        .category-value {
          font-weight: 600;
        }

        .category-bar {
          height: 8px;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 4px;
          overflow: hidden;
        }

        .category-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.5s ease-out;
        }

        .element-harmony {
          margin-top: 1.5rem;
          padding: 1rem;
          background: rgba(136, 192, 208, 0.1);
          border-radius: 12px;
        }

        .element-harmony h4 {
          margin: 0 0 0.75rem;
        }

        .elements-display {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.75rem;
        }

        .element-badge {
          padding: 0.5rem 1rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 20px;
          font-size: 0.9rem;
        }

        .element-connector {
          font-size: 1.25rem;
          color: var(--primary);
        }

        .advice-section {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .main-advice {
          display: flex;
          gap: 1rem;
          padding: 1.25rem;
          background: linear-gradient(135deg, rgba(136, 192, 208, 0.1), rgba(191, 97, 106, 0.1));
          border-radius: 12px;
        }

        .advice-icon {
          font-size: 2rem;
          flex-shrink: 0;
        }

        .main-advice p {
          margin: 0;
          color: var(--text);
          line-height: 1.6;
        }

        .action-tips h4,
        .cosmic-timing h4 {
          margin: 0 0 1rem;
          color: var(--primary);
        }

        .tips-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 0.75rem;
        }

        .tip-card {
          display: flex;
          gap: 0.75rem;
          padding: 1rem;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 10px;
        }

        .tip-number {
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--primary);
          color: var(--bg-dark);
          border-radius: 50%;
          font-size: 0.85rem;
          font-weight: 600;
          flex-shrink: 0;
        }

        .tip-card p {
          margin: 0;
          font-size: 0.85rem;
          color: var(--text-muted);
          line-height: 1.4;
        }

        .cosmic-timing {
          padding: 1rem;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 12px;
        }

        .cosmic-timing p {
          margin: 0;
          font-size: 0.9rem;
          color: var(--text-muted);
          line-height: 1.5;
        }

        @media (max-width: 600px) {
          .compat-names {
            flex-direction: column;
          }

          .quick-stats {
            flex-direction: column;
          }

          .tips-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

// Helper function to get element from sign
function getElement(sign: string): string {
  const elements: Record<string, string> = {
    Aries: 'Fire',
    Taurus: 'Earth',
    Gemini: 'Air',
    Cancer: 'Water',
    Leo: 'Fire',
    Virgo: 'Earth',
    Libra: 'Air',
    Scorpio: 'Water',
    Sagittarius: 'Fire',
    Capricorn: 'Earth',
    Aquarius: 'Air',
    Pisces: 'Water',
  };
  return elements[sign] || 'Unknown';
}
