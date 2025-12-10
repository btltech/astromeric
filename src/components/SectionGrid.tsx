import React, { useState } from 'react';
import type { PredictionData } from '../types';
import { sendSectionFeedback } from '../api/client';
import { useStore } from '../store/useStore';

interface Props {
  sections: PredictionData['sections'];
  scope?: string;
  profileId?: number | null;
}

const RatingBar = ({ value, label }: { value: number; label: string }) => (
  <div className="rating-row">
    <span>{label}</span>
    <div className="stars">
      {[...Array(5)].map((_, i) => (
        <span key={i} className={i < value ? 'filled' : ''}>
          ★
        </span>
      ))}
    </div>
  </div>
);

const TOPIC_MAP: Record<string, string> = {
  Overview: 'general',
  'Love & Relationships': 'love',
  'Career & Money': 'career',
  'Emotional & Spiritual': 'emotional',
};

export function SectionGrid({ sections, scope, profileId }: Props) {
  const { token } = useStore();
  const [votes, setVotes] = useState<Record<number, 'up' | 'down'>>({});

  if (!sections || sections.length === 0) return null;

  const handleVote = async (index: number, direction: 'up' | 'down') => {
    setVotes((prev) => ({ ...prev, [index]: direction }));
    try {
      await sendSectionFeedback(
        {
          scope: scope || 'daily',
          section: sections[index].title,
          vote: direction,
          profile_id: profileId ?? undefined,
        },
        token || undefined
      );
    } catch (err) {
      console.error('Feedback failed', err);
    }
  };
  return (
    <div className="tracks-grid">
      {sections.map((section, idx) => {
        // Determine rating from topic_scores if not explicitly provided
        let rating = section.rating;
        if (rating === undefined && section.topic_scores) {
          const key = TOPIC_MAP[section.title] || 'general';
          const score = section.topic_scores[key] || 0;
          // Approximate mapping: score 0-15 -> 1-5 stars
          rating = Math.min(5, Math.max(1, Math.round(score / 3)));
        }

        return (
          <div key={idx} className="track-item card-section">
            <h3>{section.title}</h3>
            {section.highlights.map((h, i) => (
              <p key={i}>{h}</p>
            ))}
            {rating !== undefined ? <RatingBar label="Energy" value={rating} /> : null}
            {section.affirmation && <p className="affirmation-text">{section.affirmation}</p>}
            <div className="feedback-row" aria-label="Feedback controls">
              <button
                type="button"
                className={`thumb-btn ${votes[idx] === 'up' ? 'active' : ''}`}
                onClick={() => handleVote(idx, 'up')}
                aria-pressed={votes[idx] === 'up'}
              >
                👍
              </button>
              <button
                type="button"
                className={`thumb-btn ${votes[idx] === 'down' ? 'active' : ''}`}
                onClick={() => handleVote(idx, 'down')}
                aria-pressed={votes[idx] === 'down'}
              >
                👎
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
