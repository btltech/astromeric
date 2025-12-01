/**
 * SynastryView.tsx
 * Side-by-side chart comparison for compatibility analysis
 */
import React from 'react';
import { motion } from 'framer-motion';
import { ChartWheel } from './ChartWheel';

interface Planet {
  name: string;
  sign: string;
  degree: number;
  house: number;
}

interface ChartData {
  planets: Record<string, Planet>;
  houses: Record<string, { cusp: number; sign: string }>;
  aspects: Array<{ planet1: string; planet2: string; aspect: string; orb: number }>;
  ascendant?: { sign: string; degree: number };
}

interface SynastryAspect {
  person1_planet: string;
  person2_planet: string;
  aspect: string;
  orb: number;
  interpretation?: string;
}

interface Props {
  person1: {
    name: string;
    chart: ChartData;
  };
  person2: {
    name: string;
    chart: ChartData;
  };
  synastryAspects?: SynastryAspect[];
  compatibilityScore?: number;
}

const ASPECT_MEANINGS: Record<
  string,
  { emoji: string; nature: 'harmonious' | 'challenging' | 'neutral' }
> = {
  conjunction: { emoji: '☌', nature: 'neutral' },
  opposition: { emoji: '☍', nature: 'challenging' },
  trine: { emoji: '△', nature: 'harmonious' },
  square: { emoji: '□', nature: 'challenging' },
  sextile: { emoji: '⚹', nature: 'harmonious' },
};

export function SynastryView({
  person1,
  person2,
  synastryAspects = [],
  compatibilityScore,
}: Props) {
  const harmoniousAspects = synastryAspects.filter(
    (a) => ASPECT_MEANINGS[a.aspect]?.nature === 'harmonious'
  );
  const challengingAspects = synastryAspects.filter(
    (a) => ASPECT_MEANINGS[a.aspect]?.nature === 'challenging'
  );

  return (
    <div className="synastry-container">
      {/* Header with score */}
      {compatibilityScore !== undefined && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="synastry-header"
          style={{
            textAlign: 'center',
            marginBottom: 24,
            padding: '20px',
            background: 'rgba(78, 205, 196, 0.1)',
            borderRadius: 12,
          }}
        >
          <div style={{ fontSize: 14, color: '#888', marginBottom: 8 }}>Compatibility Score</div>
          <div
            style={{
              fontSize: 48,
              fontWeight: 700,
              color:
                compatibilityScore >= 70
                  ? '#4ecdc4'
                  : compatibilityScore >= 50
                  ? '#f9ca24'
                  : '#ff6b6b',
            }}
          >
            {compatibilityScore}%
          </div>
          <div style={{ fontSize: 14, color: '#aaa', marginTop: 8 }}>
            {person1.name} 💕 {person2.name}
          </div>
        </motion.div>
      )}

      {/* Charts side by side */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 24,
          marginBottom: 32,
        }}
      >
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          style={{
            background: 'rgba(26, 26, 46, 0.8)',
            borderRadius: 16,
            padding: 16,
            border: '1px solid #3d3d5c',
          }}
        >
          <h3 style={{ textAlign: 'center', marginBottom: 16, color: '#4ecdc4' }}>
            {person1.name}
          </h3>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <ChartWheel chartData={person1.chart} size={320} interactive={true} />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          style={{
            background: 'rgba(26, 26, 46, 0.8)',
            borderRadius: 16,
            padding: 16,
            border: '1px solid #3d3d5c',
          }}
        >
          <h3 style={{ textAlign: 'center', marginBottom: 16, color: '#fd79a8' }}>
            {person2.name}
          </h3>
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <ChartWheel chartData={person2.chart} size={320} interactive={true} />
          </div>
        </motion.div>
      </div>

      {/* Synastry Aspects */}
      {synastryAspects.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          style={{
            background: 'rgba(26, 26, 46, 0.6)',
            borderRadius: 16,
            padding: 24,
            border: '1px solid #3d3d5c',
          }}
        >
          <h3 style={{ marginBottom: 20, textAlign: 'center' }}>Synastry Aspects</h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
            {/* Harmonious */}
            <div>
              <h4 style={{ color: '#4ecdc4', marginBottom: 12 }}>
                ✨ Harmonious ({harmoniousAspects.length})
              </h4>
              {harmoniousAspects.map((asp, i) => (
                <div
                  key={i}
                  style={{
                    padding: '10px 14px',
                    background: 'rgba(78, 205, 196, 0.1)',
                    borderRadius: 8,
                    marginBottom: 8,
                    borderLeft: '3px solid #4ecdc4',
                  }}
                >
                  <div style={{ fontSize: 14 }}>
                    {asp.person1_planet} {ASPECT_MEANINGS[asp.aspect]?.emoji} {asp.person2_planet}
                  </div>
                  <div style={{ fontSize: 12, color: '#888' }}>
                    {asp.aspect} (orb: {asp.orb.toFixed(1)}°)
                  </div>
                </div>
              ))}
              {harmoniousAspects.length === 0 && (
                <div style={{ color: '#666', fontSize: 14 }}>None found</div>
              )}
            </div>

            {/* Challenging */}
            <div>
              <h4 style={{ color: '#ff6b6b', marginBottom: 12 }}>
                ⚡ Challenging ({challengingAspects.length})
              </h4>
              {challengingAspects.map((asp, i) => (
                <div
                  key={i}
                  style={{
                    padding: '10px 14px',
                    background: 'rgba(255, 107, 107, 0.1)',
                    borderRadius: 8,
                    marginBottom: 8,
                    borderLeft: '3px solid #ff6b6b',
                  }}
                >
                  <div style={{ fontSize: 14 }}>
                    {asp.person1_planet} {ASPECT_MEANINGS[asp.aspect]?.emoji} {asp.person2_planet}
                  </div>
                  <div style={{ fontSize: 12, color: '#888' }}>
                    {asp.aspect} (orb: {asp.orb.toFixed(1)}°)
                  </div>
                </div>
              ))}
              {challengingAspects.length === 0 && (
                <div style={{ color: '#666', fontSize: 14 }}>None found</div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      <style>{`
        .synastry-container {
          max-width: 900px;
          margin: 0 auto;
        }
        
        @media (max-width: 768px) {
          .synastry-container > div:nth-child(2) {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}

export default SynastryView;
