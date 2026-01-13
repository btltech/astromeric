import React from 'react';
import { useTranslation } from 'react-i18next';
import type { NumerologyProfile } from '../types';

interface Props {
  profile: NumerologyProfile | null;
}

export function NumerologyView({ profile }: Props) {
  const { t } = useTranslation();

  return (
    <div className="card">
      <h2>{t('numerology.title')}</h2>
      {profile ? (
        <div className="numerology-grid">
          {renderCore(
            t('numerology.lifePath'),
            profile.life_path.number,
            profile.life_path.meaning
          )}
          {renderCore(
            t('numerology.expression'),
            profile.expression.number,
            profile.expression.meaning
          )}
          {renderCore(
            t('numerology.soulUrge'),
            profile.soul_urge.number,
            profile.soul_urge.meaning
          )}
          {renderCore(
            t('numerology.personality'),
            profile.personality.number,
            profile.personality.meaning
          )}
          {renderCore(t('numerology.maturity'), profile.maturity.number, profile.maturity.meaning)}
          {renderCore(
            t('numerology.personalYear'),
            profile.personal_year.number,
            profile.personal_year.meaning,
            true
          )}
          {renderCore(
            t('numerology.personalMonth'),
            profile.personal_month.number,
            profile.personal_month.meaning
          )}
          {renderCore(
            t('numerology.personalDay'),
            profile.personal_day.number,
            profile.personal_day.meaning
          )}
          {profile.pinnacles?.length ? renderPinnacles(profile.pinnacles, t) : null}
          {profile.challenges?.length ? renderChallenges(profile.challenges, t) : null}
        </div>
      ) : (
        <p className="loading-text">{t('numerology.loading')}</p>
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

function renderPinnacles(
  pinnacles: Array<{ number: number; meaning: string }>,
  t: (key: string, options?: Record<string, unknown>) => string
) {
  return (
    <div className="num-card wide">
      <h4>{t('numerology.lifePinnacles')}</h4>
      <div className="pinnacles-row">
        {pinnacles.map((p, i) => (
          <div key={i} className="pinnacle">
            <span className="pinnacle-num">{p.number}</span>
            <span className="pinnacle-label">{t('numerology.phase', { number: i + 1 })}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function renderChallenges(
  challenges: Array<{ number: number; meaning: string }>,
  t: (key: string, options?: Record<string, unknown>) => string
) {
  return (
    <div className="num-card wide">
      <h4>{t('numerology.lifeChallenges')}</h4>
      <div className="pinnacles-row">
        {challenges.map((c, i) => (
          <div key={i} className="pinnacle challenge">
            <span className="pinnacle-num">{c.number}</span>
            <span className="pinnacle-label">{t('numerology.challenge', { number: i + 1 })}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
