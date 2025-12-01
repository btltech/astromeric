import React from 'react';
import type { CompatibilityResult } from '../types';

interface Props {
  data: CompatibilityResult;
}

export function CompatibilityCard({ data }: Props) {
  // Calculate an overall score from topic scores if not provided directly
  const overallScore = Math.round(
    (Object.values(data.topic_scores).reduce((a, b) => a + b, 0) /
      Object.values(data.topic_scores).length) *
      10 // Scale to 100 roughly
  );

  return (
    <div className="compatibility-result">
      <div className="compat-score">
        <div
          className="score-circle"
          style={{
            background: `conic-gradient(#88c0d0 ${Math.min(overallScore, 100)}%, #2d3748 0)`,
          }}
        >
          <span>{Math.min(overallScore, 100)}%</span>
        </div>
        <h3>Overall Compatibility</h3>
      </div>

      <div className="compat-breakdown">
        <div className="compat-section">
          <h4>🌟 Astrology</h4>
          <div className="score-bar">
            <div
              className="bar-fill"
              style={{
                width: `${Math.min(data.topic_scores.general * 10, 100)}%`,
              }}
            ></div>
          </div>
          <p>
            {data.people[0].name} and {data.people[1].name} have a{' '}
            {overallScore > 70 ? 'strong' : overallScore > 40 ? 'moderate' : 'challenging'} cosmic
            connection.
          </p>
        </div>
        <div className="compat-section">
          <h4>🔢 Numerology</h4>
          <div className="score-bar">
            <div
              className="bar-fill"
              style={{
                width: `${Math.min(data.topic_scores.spiritual * 20, 100)}%`,
              }}
            ></div>
          </div>
          <p>
            Life Path {data.numerology.a.core_numbers.life_path.number} + Life Path{' '}
            {data.numerology.b.core_numbers.life_path.number}
          </p>
        </div>
      </div>

      <div className="compat-lists">
        <div className="compat-list strengths">
          <h4>💪 Strengths</h4>
          <ul>
            {data.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
        <div className="compat-list challenges">
          <h4>⚡ Challenges</h4>
          <ul>
            {data.challenges.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="compat-advice">
        <strong>💡 Advice:</strong> {data.advice}
      </div>
    </div>
  );
}
