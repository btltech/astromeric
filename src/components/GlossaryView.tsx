import React from 'react';

interface ZodiacInfo {
  symbol: string;
  dates: string;
  element: string;
  modality: string;
  description?: string;
}

interface NumerologyInfo {
  meaning?: string;
  description?: string;
}

interface GlossaryData {
  zodiac: Record<string, ZodiacInfo>;
  numerology: Record<string, NumerologyInfo>;
  [key: string]: unknown;
}

interface Props {
  glossary: GlossaryData | null;
  zodiacEntries: Array<[string, ZodiacInfo]>;
  numerologyEntries: Array<[string, NumerologyInfo]>;
  onLoadMoreSigns: () => void;
  onLoadMoreNumbers: () => void;
  hasMoreSigns: boolean;
  hasMoreNumbers: boolean;
}

export function GlossaryView({
  glossary,
  zodiacEntries,
  numerologyEntries,
  onLoadMoreSigns,
  onLoadMoreNumbers,
  hasMoreSigns,
  hasMoreNumbers,
}: Props) {
  if (!glossary) return <p style={{ textAlign: 'center', color: '#888' }}>Loading glossary...</p>;

  return (
    <div className="learn-content">
      <div className="learn-section">
        <h3>♈ Zodiac Signs</h3>
        <div className="glossary-grid">
          {zodiacEntries.map(([sign, info]) => (
            <div key={sign} className="glossary-item">
              <h4>
                {info.symbol} {sign}
              </h4>
              <p className="dates">{info.dates}</p>
              <p className="element">
                {info.element} • {info.modality}
              </p>
              <p>{info.description?.slice(0, 100)}...</p>
            </div>
          ))}
        </div>
        {hasMoreSigns && (
          <div className="load-more">
            <button className="btn-secondary" onClick={onLoadMoreSigns}>
              Load more signs
            </button>
          </div>
        )}
      </div>
      <div className="learn-section">
        <h3>🔢 Life Path Numbers</h3>
        <div className="glossary-grid">
          {numerologyEntries.map(([key, info]) => (
            <div key={key} className="glossary-item">
              <h4>{key}</h4>
              <p>{info.meaning?.slice(0, 100) || info.description?.slice(0, 100)}...</p>
            </div>
          ))}
        </div>
        {hasMoreNumbers && (
          <div className="load-more">
            <button className="btn-secondary" onClick={onLoadMoreNumbers}>
              Load more numbers
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
