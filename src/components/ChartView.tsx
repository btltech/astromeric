/**
 * ChartView.tsx
 * Full natal chart view with interactive wheel, planetary placements, and personality traits
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ChartWheel } from './ChartWheel';
import { ChartSkeleton } from './Skeleton';
import { toast } from './Toast';
import { apiFetch } from '../api/client';
import type { SavedProfile } from '../types';

interface Props {
  profile: SavedProfile;
  onExportPDF?: () => void;
}

interface PlanetData {
  name: string;
  sign: string;
  degree: number;
  house: number;
}

interface ChartData {
  planets: Record<string, PlanetData>;
  houses: Record<string, { cusp: number; sign: string }>;
  aspects: Array<{ planet1: string; planet2: string; aspect: string; orb: number }>;
  ascendant?: { sign: string; degree: number };
  midheaven?: { sign: string; degree: number };
}

// Planet symbols and tooltips
const PLANET_INFO: Record<string, { symbol: string; meaning: string; rules: string }> = {
  Sun: { symbol: '☉', meaning: 'Core identity, ego, vitality', rules: 'Leo' },
  Moon: { symbol: '☽', meaning: 'Emotions, instincts, inner self', rules: 'Cancer' },
  Mercury: { symbol: '☿', meaning: 'Communication, thinking, learning', rules: 'Gemini, Virgo' },
  Venus: { symbol: '♀', meaning: 'Love, beauty, values, pleasure', rules: 'Taurus, Libra' },
  Mars: { symbol: '♂', meaning: 'Action, desire, energy, courage', rules: 'Aries, Scorpio' },
  Jupiter: {
    symbol: '♃',
    meaning: 'Growth, luck, wisdom, expansion',
    rules: 'Sagittarius, Pisces',
  },
  Saturn: {
    symbol: '♄',
    meaning: 'Discipline, structure, limitations',
    rules: 'Capricorn, Aquarius',
  },
  Uranus: { symbol: '♅', meaning: 'Innovation, rebellion, sudden change', rules: 'Aquarius' },
  Neptune: { symbol: '♆', meaning: 'Dreams, intuition, spirituality', rules: 'Pisces' },
  Pluto: { symbol: '♇', meaning: 'Transformation, power, rebirth', rules: 'Scorpio' },
  Ascendant: { symbol: 'AC', meaning: 'Your rising sign, first impressions', rules: '1st House' },
  Midheaven: { symbol: 'MC', meaning: 'Career, public image, aspirations', rules: '10th House' },
};

// Sign element and modality
const SIGN_INFO: Record<string, { element: string; modality: string; emoji: string }> = {
  Aries: { element: 'Fire', modality: 'Cardinal', emoji: '♈' },
  Taurus: { element: 'Earth', modality: 'Fixed', emoji: '♉' },
  Gemini: { element: 'Air', modality: 'Mutable', emoji: '♊' },
  Cancer: { element: 'Water', modality: 'Cardinal', emoji: '♋' },
  Leo: { element: 'Fire', modality: 'Fixed', emoji: '♌' },
  Virgo: { element: 'Earth', modality: 'Mutable', emoji: '♍' },
  Libra: { element: 'Air', modality: 'Cardinal', emoji: '♎' },
  Scorpio: { element: 'Water', modality: 'Fixed', emoji: '♏' },
  Sagittarius: { element: 'Fire', modality: 'Mutable', emoji: '♐' },
  Capricorn: { element: 'Earth', modality: 'Cardinal', emoji: '♑' },
  Aquarius: { element: 'Air', modality: 'Fixed', emoji: '♒' },
  Pisces: { element: 'Water', modality: 'Mutable', emoji: '♓' },
};

// Personality trait interpretations based on placements
const getPersonalityTraits = (chartData: ChartData) => {
  const traits: { category: string; trait: string; description: string }[] = [];

  // Sun sign core trait
  if (chartData.planets.Sun) {
    const sign = chartData.planets.Sun.sign;
    const signData = SIGN_INFO[sign];
    traits.push({
      category: 'Core Self',
      trait: `${sign} Energy`,
      description: `Your fundamental nature is ${
        signData?.element?.toLowerCase() || 'dynamic'
      } and ${signData?.modality?.toLowerCase() || 'adaptable'}.`,
    });
  }

  // Moon emotional style
  if (chartData.planets.Moon) {
    const sign = chartData.planets.Moon.sign;
    traits.push({
      category: 'Emotional Style',
      trait: `${sign} Moon`,
      description: `You process emotions through ${sign} energy, seeking ${getEmotionalNeed(
        sign
      )}.`,
    });
  }

  // Mercury communication
  if (chartData.planets.Mercury) {
    const sign = chartData.planets.Mercury.sign;
    traits.push({
      category: 'Communication',
      trait: `${sign} Mind`,
      description: `You think and communicate in a ${getCommunicationStyle(sign)} manner.`,
    });
  }

  // Venus love style
  if (chartData.planets.Venus) {
    const sign = chartData.planets.Venus.sign;
    traits.push({
      category: 'Love Language',
      trait: `${sign} Heart`,
      description: `In love, you value ${getLoveValue(sign)}.`,
    });
  }

  // Mars drive
  if (chartData.planets.Mars) {
    const sign = chartData.planets.Mars.sign;
    traits.push({
      category: 'Drive & Energy',
      trait: `${sign} Action`,
      description: `You take action with ${getActionStyle(sign)} energy.`,
    });
  }

  return traits;
};

const getEmotionalNeed = (sign: string): string => {
  const needs: Record<string, string> = {
    Aries: 'independence and excitement',
    Taurus: 'security and comfort',
    Gemini: 'mental stimulation and variety',
    Cancer: 'nurturing and belonging',
    Leo: 'recognition and warmth',
    Virgo: 'order and purpose',
    Libra: 'harmony and partnership',
    Scorpio: 'depth and transformation',
    Sagittarius: 'freedom and adventure',
    Capricorn: 'achievement and respect',
    Aquarius: 'uniqueness and community',
    Pisces: 'connection and transcendence',
  };
  return needs[sign] || 'balance and growth';
};

const getCommunicationStyle = (sign: string): string => {
  const styles: Record<string, string> = {
    Aries: 'direct and assertive',
    Taurus: 'practical and deliberate',
    Gemini: 'quick and versatile',
    Cancer: 'intuitive and caring',
    Leo: 'dramatic and confident',
    Virgo: 'analytical and precise',
    Libra: 'diplomatic and balanced',
    Scorpio: 'probing and intense',
    Sagittarius: 'philosophical and honest',
    Capricorn: 'structured and authoritative',
    Aquarius: 'innovative and unconventional',
    Pisces: 'imaginative and empathetic',
  };
  return styles[sign] || 'thoughtful';
};

const getLoveValue = (sign: string): string => {
  const values: Record<string, string> = {
    Aries: 'passion and spontaneity',
    Taurus: 'loyalty and sensuality',
    Gemini: 'intellectual connection and playfulness',
    Cancer: 'emotional depth and devotion',
    Leo: 'romance and admiration',
    Virgo: 'service and reliability',
    Libra: 'partnership and beauty',
    Scorpio: 'intensity and soul bonds',
    Sagittarius: 'adventure and growth',
    Capricorn: 'commitment and stability',
    Aquarius: 'friendship and freedom',
    Pisces: 'spiritual union and compassion',
  };
  return values[sign] || 'connection and love';
};

const getActionStyle = (sign: string): string => {
  const styles: Record<string, string> = {
    Aries: 'bold and pioneering',
    Taurus: 'steady and determined',
    Gemini: 'adaptable and quick',
    Cancer: 'protective and tenacious',
    Leo: 'confident and creative',
    Virgo: 'methodical and efficient',
    Libra: 'strategic and fair',
    Scorpio: 'focused and powerful',
    Sagittarius: 'adventurous and optimistic',
    Capricorn: 'disciplined and ambitious',
    Aquarius: 'revolutionary and detached',
    Pisces: 'intuitive and flexible',
  };
  return styles[sign] || 'dynamic';
};

// Calculate element balance
const getElementBalance = (chartData: ChartData) => {
  const elements: Record<string, number> = { Fire: 0, Earth: 0, Air: 0, Water: 0 };

  Object.values(chartData.planets).forEach((planet) => {
    const signInfo = SIGN_INFO[planet.sign];
    if (signInfo?.element) {
      elements[signInfo.element]++;
    }
  });

  return elements;
};

export function ChartView({ profile, onExportPDF }: Props) {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'placements' | 'traits' | 'elements'>('placements');

  useEffect(() => {
    const fetchChart = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await apiFetch<ChartData>('/chart/natal', {
          method: 'POST',
          body: JSON.stringify({
            profile: {
              name: profile.name,
              date_of_birth: profile.date_of_birth,
              time_of_birth: profile.time_of_birth,
              location: {
                latitude: profile.latitude || 0,
                longitude: profile.longitude || 0,
                timezone: profile.timezone || 'UTC',
              },
              house_system: profile.house_system || 'Placidus',
            },
          }),
        });
        setChartData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load chart');
      } finally {
        setLoading(false);
      }
    };

    fetchChart();
  }, [profile]);

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/export/natal-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profile: {
            name: profile.name,
            date_of_birth: profile.date_of_birth,
            time_of_birth: profile.time_of_birth,
            location: {
              latitude: profile.latitude || 0,
              longitude: profile.longitude || 0,
              timezone: profile.timezone || 'UTC',
            },
            house_system: profile.house_system || 'Placidus',
          },
        }),
      });

      if (!response.ok) throw new Error('PDF export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `natal_report_${profile.name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success('Chart exported successfully');
      onExportPDF?.();
    } catch (err) {
      console.error('PDF export failed:', err);
      toast.error('Failed to export PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return <ChartSkeleton />;
  }

  if (error) {
    return (
      <div className="error-state">
        <p>⚠️ {error}</p>
      </div>
    );
  }

  if (!chartData) return null;

  const elementBalance = getElementBalance(chartData);
  const personalityTraits = getPersonalityTraits(chartData);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="chart-view-enhanced">
      <div className="chart-header">
        <h2>{profile.name}&apos;s Natal Chart</h2>
        <p className="chart-meta">
          {profile.date_of_birth} {profile.time_of_birth && `at ${profile.time_of_birth}`}
          {profile.place_of_birth && ` • ${profile.place_of_birth}`}
        </p>
      </div>

      {/* Big Three */}
      <div className="big-three-grid">
        {chartData.planets.Sun && (
          <div
            className="big-three-card sun"
            onMouseEnter={() => setActiveTooltip('Sun')}
            onMouseLeave={() => setActiveTooltip(null)}
          >
            <span className="planet-symbol">☉</span>
            <div className="placement-info">
              <span className="placement-label">Sun Sign</span>
              <span className="placement-sign">
                {SIGN_INFO[chartData.planets.Sun.sign]?.emoji} {chartData.planets.Sun.sign}
              </span>
              <span className="placement-degree">{chartData.planets.Sun.degree.toFixed(1)}°</span>
            </div>
            {activeTooltip === 'Sun' && <div className="tooltip">{PLANET_INFO.Sun.meaning}</div>}
          </div>
        )}
        {chartData.planets.Moon && (
          <div
            className="big-three-card moon"
            onMouseEnter={() => setActiveTooltip('Moon')}
            onMouseLeave={() => setActiveTooltip(null)}
          >
            <span className="planet-symbol">☽</span>
            <div className="placement-info">
              <span className="placement-label">Moon Sign</span>
              <span className="placement-sign">
                {SIGN_INFO[chartData.planets.Moon.sign]?.emoji} {chartData.planets.Moon.sign}
              </span>
              <span className="placement-degree">{chartData.planets.Moon.degree.toFixed(1)}°</span>
            </div>
            {activeTooltip === 'Moon' && <div className="tooltip">{PLANET_INFO.Moon.meaning}</div>}
          </div>
        )}
        {chartData.ascendant && (
          <div
            className="big-three-card rising"
            onMouseEnter={() => setActiveTooltip('Ascendant')}
            onMouseLeave={() => setActiveTooltip(null)}
          >
            <span className="planet-symbol">↑</span>
            <div className="placement-info">
              <span className="placement-label">Rising Sign</span>
              <span className="placement-sign">
                {SIGN_INFO[chartData.ascendant.sign]?.emoji} {chartData.ascendant.sign}
              </span>
              <span className="placement-degree">{chartData.ascendant.degree.toFixed(1)}°</span>
            </div>
            {activeTooltip === 'Ascendant' && (
              <div className="tooltip">{PLANET_INFO.Ascendant.meaning}</div>
            )}
          </div>
        )}
      </div>

      {/* Chart Wheel */}
      <div className="chart-wheel-container">
        <ChartWheel chartData={chartData} size={400} interactive={true} />
      </div>

      {/* Tab Navigation */}
      <div className="chart-tabs">
        <button
          className={`chart-tab ${activeTab === 'placements' ? 'active' : ''}`}
          onClick={() => setActiveTab('placements')}
        >
          🪐 All Placements
        </button>
        <button
          className={`chart-tab ${activeTab === 'traits' ? 'active' : ''}`}
          onClick={() => setActiveTab('traits')}
        >
          ✨ Personality Traits
        </button>
        <button
          className={`chart-tab ${activeTab === 'elements' ? 'active' : ''}`}
          onClick={() => setActiveTab('elements')}
        >
          🔥 Elements
        </button>
      </div>

      {/* Tab Content */}
      <div className="chart-tab-content">
        {activeTab === 'placements' && (
          <div className="placements-grid">
            {Object.entries(chartData.planets).map(([name, data]) => {
              const info = PLANET_INFO[name];
              const signInfo = SIGN_INFO[data.sign];
              return (
                <div
                  key={name}
                  className="placement-card"
                  onMouseEnter={() => setActiveTooltip(name)}
                  onMouseLeave={() => setActiveTooltip(null)}
                >
                  <div className="placement-header">
                    <span className="planet-glyph">{info?.symbol || '●'}</span>
                    <span className="planet-name">{name}</span>
                  </div>
                  <div className="placement-details">
                    <span className="sign-badge" data-element={signInfo?.element?.toLowerCase()}>
                      {signInfo?.emoji} {data.sign}
                    </span>
                    <span className="degree-text">{data.degree.toFixed(1)}°</span>
                    <span className="house-text">House {data.house}</span>
                  </div>
                  {activeTooltip === name && info && (
                    <div className="tooltip">
                      <strong>{name}</strong>: {info.meaning}
                      <br />
                      <small>Rules: {info.rules}</small>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {activeTab === 'traits' && (
          <div className="traits-grid">
            {personalityTraits.map((trait, index) => (
              <div key={index} className="trait-card">
                <span className="trait-category">{trait.category}</span>
                <h4 className="trait-title">{trait.trait}</h4>
                <p className="trait-description">{trait.description}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'elements' && (
          <div className="elements-display">
            <div className="elements-chart">
              {Object.entries(elementBalance).map(([element, count]) => (
                <div key={element} className="element-bar-container">
                  <span className="element-label" data-element={element.toLowerCase()}>
                    {element === 'Fire' && '🔥'}
                    {element === 'Earth' && '🌍'}
                    {element === 'Air' && '💨'}
                    {element === 'Water' && '💧'}
                    {element}
                  </span>
                  <div className="element-bar">
                    <div
                      className="element-bar-fill"
                      data-element={element.toLowerCase()}
                      style={{ width: `${(count / 10) * 100}%` }}
                    />
                  </div>
                  <span className="element-count">{count}</span>
                </div>
              ))}
            </div>
            <div className="element-interpretation">
              {Object.entries(elementBalance).map(([element, count]) => {
                if (count >= 4) {
                  return (
                    <p key={element} className="element-note strong">
                      <strong>
                        {element} Dominant ({count})
                      </strong>
                      :
                      {element === 'Fire' && ' You are passionate, energetic, and action-oriented.'}
                      {element === 'Earth' && ' You are practical, grounded, and security-focused.'}
                      {element === 'Air' &&
                        ' You are intellectual, communicative, and socially adept.'}
                      {element === 'Water' &&
                        ' You are emotional, intuitive, and deeply sensitive.'}
                    </p>
                  );
                }
                if (count <= 1) {
                  return (
                    <p key={element} className="element-note weak">
                      <strong>
                        {element} Lacking ({count})
                      </strong>
                      :{element === 'Fire' && ' May struggle with motivation and self-assertion.'}
                      {element === 'Earth' &&
                        ' May need to work on practical matters and stability.'}
                      {element === 'Air' && ' May need to develop communication and objectivity.'}
                      {element === 'Water' &&
                        ' May need to connect more with emotions and intuition.'}
                    </p>
                  );
                }
                return null;
              })}
            </div>
          </div>
        )}
      </div>

      {/* Export Button */}
      <div className="chart-actions">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleExportPDF}
          disabled={exporting}
          className="btn-export"
        >
          {exporting ? (
            <>
              <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}>
                ⏳
              </motion.span>
              Generating PDF...
            </>
          ) : (
            <>📄 Export PDF Report</>
          )}
        </motion.button>
      </div>

      <style>{`
        .chart-view-enhanced {
          background: var(--card-bg);
          border-radius: 16px;
          padding: 1.5rem;
        }
        
        .chart-header {
          text-align: center;
          margin-bottom: 1.5rem;
        }
        
        .chart-header h2 {
          margin: 0 0 0.5rem;
          color: var(--primary);
        }
        
        .chart-meta {
          color: var(--text-muted);
          font-size: 0.9rem;
          margin: 0;
        }
        
        .big-three-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1rem;
          margin-bottom: 1.5rem;
        }
        
        .big-three-card {
          position: relative;
          padding: 1.25rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          border: 1px solid rgba(136, 192, 208, 0.2);
          text-align: center;
          cursor: pointer;
          transition: border-color 0.2s, transform 0.2s;
        }
        
        .big-three-card:hover {
          border-color: var(--primary);
          transform: translateY(-2px);
        }
        
        .big-three-card .planet-symbol {
          font-size: 2rem;
          display: block;
          margin-bottom: 0.5rem;
        }
        
        .big-three-card.sun .planet-symbol { color: #fbbf24; }
        .big-three-card.moon .planet-symbol { color: #c0c0c0; }
        .big-three-card.rising .planet-symbol { color: var(--primary); }
        
        .placement-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        
        .placement-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .placement-sign {
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--text);
        }
        
        .placement-degree {
          font-size: 0.85rem;
          color: var(--text-muted);
        }
        
        .tooltip {
          position: absolute;
          bottom: 100%;
          left: 50%;
          transform: translateX(-50%);
          padding: 0.75rem;
          background: rgba(0, 0, 0, 0.9);
          border: 1px solid var(--primary);
          border-radius: 8px;
          font-size: 0.85rem;
          color: var(--text);
          white-space: nowrap;
          z-index: 100;
          margin-bottom: 0.5rem;
        }
        
        .chart-wheel-container {
          display: flex;
          justify-content: center;
          margin-bottom: 1.5rem;
        }
        
        .chart-tabs {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid rgba(136, 192, 208, 0.2);
        }
        
        .chart-tab {
          flex: 1;
          padding: 0.75rem;
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(136, 192, 208, 0.2);
          border-radius: 8px;
          color: var(--text-muted);
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .chart-tab:hover {
          border-color: rgba(136, 192, 208, 0.4);
        }
        
        .chart-tab.active {
          background: rgba(136, 192, 208, 0.2);
          border-color: var(--primary);
          color: var(--primary);
        }
        
        .chart-tab-content {
          min-height: 200px;
        }
        
        .placements-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
          gap: 0.75rem;
        }
        
        .placement-card {
          position: relative;
          padding: 1rem;
          background: rgba(0, 0, 0, 0.2);
          border: 1px solid rgba(136, 192, 208, 0.15);
          border-radius: 10px;
          cursor: pointer;
          transition: border-color 0.2s;
        }
        
        .placement-card:hover {
          border-color: var(--primary);
        }
        
        .placement-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }
        
        .planet-glyph {
          font-size: 1.25rem;
        }
        
        .planet-name {
          font-weight: 500;
          color: var(--text);
        }
        
        .placement-details {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          font-size: 0.85rem;
        }
        
        .sign-badge {
          padding: 0.25rem 0.5rem;
          background: rgba(136, 192, 208, 0.1);
          border-radius: 4px;
        }
        
        .sign-badge[data-element="fire"] { background: rgba(239, 68, 68, 0.2); }
        .sign-badge[data-element="earth"] { background: rgba(34, 197, 94, 0.2); }
        .sign-badge[data-element="air"] { background: rgba(59, 130, 246, 0.2); }
        .sign-badge[data-element="water"] { background: rgba(168, 85, 247, 0.2); }
        
        .degree-text, .house-text {
          color: var(--text-muted);
        }
        
        .traits-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 1rem;
        }
        
        .trait-card {
          padding: 1.25rem;
          background: rgba(0, 0, 0, 0.2);
          border: 1px solid rgba(136, 192, 208, 0.15);
          border-radius: 12px;
        }
        
        .trait-category {
          font-size: 0.75rem;
          color: var(--primary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        
        .trait-title {
          margin: 0.5rem 0;
          font-size: 1.1rem;
          color: var(--text);
        }
        
        .trait-description {
          margin: 0;
          font-size: 0.9rem;
          color: var(--text-muted);
          line-height: 1.5;
        }
        
        .elements-display {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        
        .elements-chart {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        
        .element-bar-container {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .element-label {
          width: 80px;
          font-size: 0.9rem;
        }
        
        .element-bar {
          flex: 1;
          height: 12px;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 6px;
          overflow: hidden;
        }
        
        .element-bar-fill {
          height: 100%;
          border-radius: 6px;
          transition: width 0.5s ease-out;
        }
        
        .element-bar-fill[data-element="fire"] { background: linear-gradient(90deg, #ef4444, #f97316); }
        .element-bar-fill[data-element="earth"] { background: linear-gradient(90deg, #22c55e, #84cc16); }
        .element-bar-fill[data-element="air"] { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
        .element-bar-fill[data-element="water"] { background: linear-gradient(90deg, #a855f7, #6366f1); }
        
        .element-count {
          width: 24px;
          text-align: center;
          font-weight: 600;
          color: var(--text);
        }
        
        .element-interpretation {
          padding: 1rem;
          background: rgba(0, 0, 0, 0.2);
          border-radius: 12px;
        }
        
        .element-note {
          margin: 0 0 0.75rem;
          font-size: 0.9rem;
          line-height: 1.5;
        }
        
        .element-note:last-child {
          margin-bottom: 0;
        }
        
        .element-note.strong {
          color: var(--text);
        }
        
        .element-note.weak {
          color: var(--text-muted);
        }
        
        .chart-actions {
          text-align: center;
          margin-top: 1.5rem;
        }
        
        .btn-export {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: linear-gradient(135deg, var(--primary), #5e81ac);
          color: var(--bg-dark);
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn-export:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 20px rgba(136, 192, 208, 0.4);
        }
        
        .btn-export:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        
        @media (max-width: 600px) {
          .big-three-grid {
            grid-template-columns: 1fr;
          }
          
          .chart-tabs {
            flex-wrap: wrap;
          }
          
          .placements-grid {
            grid-template-columns: repeat(2, 1fr);
          }
          
          .traits-grid {
            grid-template-columns: 1fr;
          }
          
          .tooltip {
            white-space: normal;
            min-width: 200px;
          }
        }
      `}</style>
    </motion.div>
  );
}

export default ChartView;
