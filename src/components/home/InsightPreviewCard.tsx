import React from 'react';

export type InsightPreview = {
  label: string;
  headline: string;
  score: string;
  scoreLabel: string;
  mood: string;
  bestTime: string;
  nextAction: string;
  chartInfluence?: string;
  numerologyCycle?: string;
};

type InsightPreviewCardProps = InsightPreview & {
  compact?: boolean;
};

export function InsightPreviewCard({
  label,
  headline,
  score,
  scoreLabel,
  mood,
  bestTime,
  nextAction,
  chartInfluence,
  numerologyCycle,
  compact = false,
}: InsightPreviewCardProps) {
  const scoreNum = Math.min(100, Math.max(0, parseInt(score, 10) || 0));

  return (
    <article className={`insight-card${compact ? ' insight-card--compact' : ''}`}>
      <div className="insight-card__header">
        <div className="insight-card__copy">
          <span className="insight-card__eyebrow">{label}</span>
          <h3 className="insight-card__headline">{headline}</h3>
        </div>

        <div className="insight-card__score">
          <strong>{score}</strong>
          <span>{scoreLabel}</span>
          <div className="insight-card__score-bar" aria-hidden="true">
            <div className="insight-card__score-fill" style={{ width: `${scoreNum}%` }} />
          </div>
        </div>
      </div>

      <div className="insight-card__metrics">
        <div className="insight-card__metric">
          <span>Mood</span>
          <strong>{mood}</strong>
        </div>
        <div className="insight-card__metric">
          <span>Best time</span>
          <strong>{bestTime}</strong>
        </div>
        {chartInfluence ? (
          <div className="insight-card__metric">
            <span>Chart influence</span>
            <strong>{chartInfluence}</strong>
          </div>
        ) : null}
        {numerologyCycle ? (
          <div className="insight-card__metric">
            <span>Numerology cycle</span>
            <strong>{numerologyCycle}</strong>
          </div>
        ) : null}
        <div className="insight-card__metric insight-card__metric--wide">
          <span>Next action</span>
          <strong>{nextAction}</strong>
        </div>
      </div>
    </article>
  );
}
