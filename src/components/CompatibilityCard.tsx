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
  if (score >= 90) return 'Soulmate Potential';
  if (score >= 80) return 'Highly Compatible';
  if (score >= 70) return 'Strong Connection';
  if (score >= 60) return 'Good Potential';
  if (score >= 50) return 'Workable Match';
  if (score >= 40) return 'Challenging but Growth-Oriented';
  return 'Significant Differences';
};

// Generate red flags based on scores and challenges
const getRedFlags = (data: CompatibilityResult): string[] => {
  const redFlags: string[] = [];
  const overallScore = Math.round(
    (Object.values(data.topic_scores).reduce((a, b) => a + b, 0) /
      Object.values(data.topic_scores).length) * 10
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
    redFlags.push('Overall compatibility is low - consider if the growth is worth the effort');
  }

  // Add specific element-based red flags
  if (data.challenges.some(c => c.toLowerCase().includes('control') || c.toLowerCase().includes('power'))) {
    redFlags.push('Power dynamics may become an issue');
  }
  if (data.challenges.some(c => c.toLowerCase().includes('trust') || c.toLowerCase().includes('jealous'))) {
    redFlags.push('Trust issues may arise - prioritize transparency');
  }

  return redFlags.slice(0, 3); // Limit to top 3
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
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  // Calculate overall score (0-100 scale)
  const rawScore = Object.values(data.topic_scores).reduce((a, b) => a + b, 0) /
    Object.values(data.topic_scores).length;
  const overallScore = Math.min(Math.round(rawScore * 10), 100);
  const scoreColor = getScoreColor(overallScore);
  const scoreLabel = getScoreLabel(overallScore);
  const redFlags = getRedFlags(data);

  return (
    <div className="compatibility-enhanced">
      {/* Header with Score */}
      <div className="compat-header">
        <div className="compat-names">
          <span className="person-name">{data.people[0].name}</span>
          <span className="heart-icon">💕</span>
          <span className="person-name">{data.people[1].name}</span>
        </div>
        
        <div 
          className="score-display"
          style={{ '--score-color': scoreColor } as React.CSSProperties}
        >
          <div className="score-ring">
            <svg viewBox="0 0 120 120">
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke="rgba(136, 192, 208, 0.1)"
                strokeWidth="8"
              />
              <circle
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke={scoreColor}
                strokeWidth="8"
                strokeDasharray={`${(overallScore / 100) * 339.292} 339.292`}
                strokeLinecap="round"
                transform="rotate(-90 60 60)"
                className="score-progress"
              />
            </svg>
            <div className="score-value">
              <span className="score-number">{overallScore}</span>
              <span className="score-percent">%</span>
            </div>
          </div>
          <span className="score-label">{scoreLabel}</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="compat-tabs">
        <button 
          className={`compat-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`compat-tab ${activeTab === 'details' ? 'active' : ''}`}
          onClick={() => setActiveTab('details')}
        >
          Detailed Scores
        </button>
        <button 
          className={`compat-tab ${activeTab === 'advice' ? 'active' : ''}`}
          onClick={() => setActiveTab('advice')}
        >
          Advice
        </button>
      </div>

      {/* Tab Content */}
      <div className="compat-content">
        {activeTab === 'overview' && (
          <>
            {/* Quick Stats */}
            <div className="quick-stats">
              <div className="stat-item">
                <span className="stat-emoji">☉</span>
                <span className="stat-label">Signs</span>
                <span className="stat-value">
                  {data.people[0].sign} + {data.people[1].sign}
                </span>
              </div>
              <div className="stat-item">
                <span className="stat-emoji">🔢</span>
                <span className="stat-label">Life Paths</span>
                <span className="stat-value">
                  {data.numerology.a.core_numbers.life_path.number} + {data.numerology.b.core_numbers.life_path.number}
                </span>
              </div>
            </div>

            {/* Strengths */}
            <div className="compat-list strengths">
              <h4>💪 Your Strengths Together</h4>
              <ul>
                {data.strengths.map((s, i) => (
                  <li key={i}>
                    <span className="list-icon">✓</span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>

            {/* Challenges */}
            <div className="compat-list challenges">
              <h4>⚡ Growth Areas</h4>
              <ul>
                {data.challenges.map((c, i) => (
                  <li key={i}>
                    <span className="list-icon">!</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>

            {/* Red Flags (if any) */}
            {redFlags.length > 0 && (
              <div className="compat-list red-flags">
                <h4>🚩 Watch Out For</h4>
                <ul>
                  {redFlags.map((rf, i) => (
                    <li key={i}>
                      <span className="list-icon">⚠</span>
                      {rf}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}

        {activeTab === 'details' && (
          <div className="detailed-scores">
            {CATEGORIES.map(cat => {
              const score = (data.topic_scores[cat.key] || 5) * 10;
              const catColor = getScoreColor(score);
              return (
                <div key={cat.key} className="category-score">
                  <div className="category-header">
                    <span className="category-icon">{cat.icon}</span>
                    <span className="category-label">{cat.label}</span>
                    <span 
                      className="category-value"
                      style={{ color: catColor }}
                    >
                      {Math.round(score)}%
                    </span>
                  </div>
                  <div className="category-bar">
                    <div 
                      className="category-fill"
                      style={{ 
                        width: `${score}%`,
                        background: catColor
                      }}
                    />
                  </div>
                </div>
              );
            })}

            {/* Element Harmony */}
            <div className="element-harmony">
              <h4>🌀 Element Dynamics</h4>
              <div className="elements-display">
                <span className="element-badge">
                  {data.people[0].sign} ({data.people[0].sign && getElement(data.people[0].sign)})
                </span>
                <span className="element-connector">×</span>
                <span className="element-badge">
                  {data.people[1].sign} ({data.people[1].sign && getElement(data.people[1].sign)})
                </span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'advice' && (
          <div className="advice-section">
            <div className="main-advice">
              <span className="advice-icon">💡</span>
              <p>{data.advice}</p>
            </div>

            <div className="action-tips">
              <h4>🎯 Action Items</h4>
              <div className="tips-grid">
                <div className="tip-card">
                  <span className="tip-number">1</span>
                  <p>Schedule regular check-ins to discuss your relationship dynamics</p>
                </div>
                <div className="tip-card">
                  <span className="tip-number">2</span>
                  <p>Celebrate your differences as opportunities for growth</p>
                </div>
                <div className="tip-card">
                  <span className="tip-number">3</span>
                  <p>Create shared rituals that honor both your needs</p>
                </div>
              </div>
            </div>

            <div className="cosmic-timing">
              <h4>⏰ Best Times Together</h4>
              <p>
                {overallScore >= 70 
                  ? 'Your connection flows naturally - any time together strengthens your bond.'
                  : 'Focus on quality over quantity. Plan intentional activities that play to your strengths.'}
              </p>
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
    Aries: 'Fire', Taurus: 'Earth', Gemini: 'Air', Cancer: 'Water',
    Leo: 'Fire', Virgo: 'Earth', Libra: 'Air', Scorpio: 'Water',
    Sagittarius: 'Fire', Capricorn: 'Earth', Aquarius: 'Air', Pisces: 'Water',
  };
  return elements[sign] || 'Unknown';
}
