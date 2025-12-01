import React from 'react';
import type { NumerologyProfile } from '../types';

interface Props {
  profile: NumerologyProfile | null;
}

export function NumerologyView({ profile }: Props) {
  return (
    <div className="card">
      <h2>🔢 Your Numerology Profile</h2>
      {profile ? (
        <div className="numerology-grid">
          {renderCore('Life Path', profile.life_path.number, profile.life_path.meaning)}
          {renderCore('Expression', profile.expression.number, profile.expression.meaning)}
          {renderCore('Soul Urge', profile.soul_urge.number, profile.soul_urge.meaning)}
          {renderCore('Personality', profile.personality.number, profile.personality.meaning)}
          {renderCore('Maturity', profile.maturity.number, profile.maturity.meaning)}
          {renderCore(
            'Personal Year',
            profile.personal_year.number,
            profile.personal_year.meaning,
            true
          )}
          {renderCore(
            'Personal Month',
            profile.personal_month.number,
            profile.personal_month.meaning
          )}
          {renderCore('Personal Day', profile.personal_day.number, profile.personal_day.meaning)}
          {profile.pinnacles?.length ? renderPinnacles(profile.pinnacles) : null}
          {profile.challenges?.length ? renderChallenges(profile.challenges) : null}
        </div>
      ) : (
        <p style={{ textAlign: 'center', color: '#888' }}>Loading numerology profile...</p>
      )}
    </div>
  );
}

function renderCore(title: string, value: number, text: string, highlight = false) {
  return (
    <div className={`num-card ${highlight ? 'highlight' : ''}`}>
      <h4>{title}</h4>
      <div className="num-value">{value}</div>
      <p>{text}</p>
    </div>
  );
}

function renderPinnacles(pinnacles: Array<{ number: number; meaning: string }>) {
  return (
    <div className="num-card wide">
      <h4>Life Pinnacles</h4>
      <div className="pinnacles-row">
        {pinnacles.map((p, i) => (
          <div key={i} className="pinnacle">
            <span className="pinnacle-num">{p.number}</span>
            <span className="pinnacle-label">Phase {i + 1}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function renderChallenges(challenges: Array<{ number: number; meaning: string }>) {
  return (
    <div className="num-card wide">
      <h4>Life Challenges</h4>
      <div className="pinnacles-row">
        {challenges.map((c, i) => (
          <div key={i} className="pinnacle challenge">
            <span className="pinnacle-num">{c.number}</span>
            <span className="pinnacle-label">Challenge {i + 1}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
