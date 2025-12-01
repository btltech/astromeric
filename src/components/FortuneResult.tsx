import React, { useState } from 'react';
import type { PredictionData } from '../types';
import { SectionGrid } from './SectionGrid';
import { fetchAiExplanation } from '../api/client';
import { downloadReadingPdf } from '../utils/pdfExport';

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
      const sections =
        data.sections?.map((section) => ({
          title: section.title,
          highlights: section.highlights,
        })) ?? [];
      const payload = {
        scope: data.scope,
        headline,
        theme: data.theme,
        sections,
        numerology_summary: data.numerology?.cycles?.personal_day?.meaning,
      };
      const response = await fetchAiExplanation(payload);
      setAiInsight(response.summary);
    } catch (err) {
      console.error('AI assist failed', err);
      setAiInsight('AI assist encountered a hiccup. Please try again soon.');
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
      {aiInsight && (
        <div className="tldr-box" style={{ background: 'rgba(158, 173, 255, 0.12)' }}>
          {aiInsight}
        </div>
      )}
      {data.sections && data.sections.length > 0 && <SectionGrid sections={data.sections} />}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
        <button
          onClick={handleAiExplain}
          className="btn-secondary"
          disabled={aiLoading}
          style={{ minWidth: 180 }}
        >
          {aiLoading ? 'Thinking…' : '✨ Explain with AI'}
        </button>
        <button
          onClick={() => downloadReadingPdf(data)}
          className="btn-secondary"
          style={{ minWidth: 180 }}
        >
          📄 Download PDF
        </button>
        <button onClick={onReset} className="btn-secondary">
          Back to Profiles
        </button>
      </div>

    </div>
  );
}
