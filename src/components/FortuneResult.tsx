import React, { useState } from 'react';
import type { PredictionData } from '../types';
import { SectionGrid } from './SectionGrid';

interface Props {
  data: PredictionData;
  onReset: () => void;
}

// RatingBar reserved for future use
// const RatingBar = ({ value, label }: { value: number; label: string }) => (
//   <div className="rating-row">
//     <span>{label}</span>
//     <div className="stars">
//       {[...Array(5)].map((_, i) => (
//         <span key={i} className={i < value ? 'filled' : ''}>★</span>
//       ))}
//     </div>
//   </div>
// );

export function FortuneResult({ data, onReset }: Props) {
  // Derive sign from charts if not explicitly provided
  const sunSign = data.sign || data.charts?.natal?.planets?.find((p) => p.name === 'Sun')?.sign;

  // Use theme as headline if summary is missing
  const headline = data.summary?.headline || data.theme;
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const handleAiExplain = async () => {
    setAiLoading(true);
    try {
      // Placeholder summary derived locally until Gemini Flash endpoint is ready.
      const topSection = data.sections?.[0];
      const highlights = topSection?.highlights?.slice(0, 2).join(' ');
      const numerologyNote = data.numerology?.cycles?.personal_day?.meaning;
      const message =
        `Gemini Flash summary: ${headline || 'Your reading emphasizes balance.'}` +
        (highlights ? ` Key energy: ${highlights}` : '') +
        (numerologyNote ? ` Numerology cue: ${numerologyNote}` : '');
      setAiInsight(message);
    } catch (err) {
      console.error('Gemini assist failed', err);
      setAiInsight('Gemini assist encountered a hiccup. Please try again soon.');
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="header-badge">
        {data.element === 'Fire' && '🔥'}
        {data.element === 'Water' && '💧'}
        {data.element === 'Air' && '🌬️'}
        {data.element === 'Earth' && '🌱'}
      </div>
      <h1 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
        {data.scope.charAt(0).toUpperCase() + data.scope.slice(1)} Reading
      </h1>
      {sunSign && data.numerology?.core_numbers?.life_path && (
        <h3
          style={{ textAlign: 'center', color: '#88c0d0', fontWeight: 300, marginBottom: '2rem' }}
        >
          {sunSign} • Life Path {data.numerology.core_numbers.life_path.number}
        </h3>
      )}
      {headline && (
        <div className="tldr-box">
          <strong>TL;DR:</strong> {headline}
        </div>
      )}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <button
          onClick={handleAiExplain}
          className="btn-secondary"
          disabled={aiLoading}
          style={{ minWidth: 200 }}
        >
          {aiLoading ? 'Asking Gemini…' : 'Explain with Gemini Flash'}
        </button>
        <button onClick={onReset} className="btn-secondary">
          Back to Profiles
        </button>
      </div>
      {aiInsight && (
        <div className="tldr-box" style={{ background: 'rgba(158, 173, 255, 0.12)' }}>
          {aiInsight}
        </div>
      )}
      {data.sections && data.sections.length > 0 && <SectionGrid sections={data.sections} />}
    </div>
  );
}
