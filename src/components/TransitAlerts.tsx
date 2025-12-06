/**
 * TransitAlerts.tsx
 * Display daily transit alerts for a profile
 */
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiFetch } from '../api/client';
import type { SavedProfile } from '../types';

interface TransitAspect {
  transit_planet: string;
  natal_point: string;
  aspect: string;
  orb: number;
  interpretation?: string;
  transit_sign: string;
  natal_sign: string;
}

interface TransitData {
  date: string;
  profile_name: string;
  transits: TransitAspect[];
  highlights: TransitAspect[];
  total_aspects: number;
  alert_level: 'low' | 'medium' | 'high';
}

interface Props {
  profile: SavedProfile;
}

const ASPECT_SYMBOLS: Record<string, string> = {
  conjunction: '☌',
  opposition: '☍',
  trine: '△',
  square: '□',
  sextile: '⚹',
};

const PLANET_SYMBOLS: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
  Uranus: '♅',
  Neptune: '♆',
  Pluto: '♇',
};

export function TransitAlerts({ profile }: Props) {
  const [transitData, setTransitData] = useState<TransitData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchTransits = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await apiFetch<TransitData>('/transits/daily', {
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
        setTransitData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load transits');
      } finally {
        setLoading(false);
      }
    };

    fetchTransits();
  }, [profile]);

  if (loading) {
    return (
      <div className="transit-loading text-center" style={{ padding: 20 }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          style={{ fontSize: 32 }}
        >
          🌙
        </motion.div>
        <p className="loading-text mt-1">Checking transits...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-state">⚠️ {error}</div>;
  }

  if (!transitData) return null;

  const alertColors = {
    low: 'var(--primary)',
    medium: 'var(--accent-warning)',
    high: 'var(--accent)',
  };

  const alertEmojis = {
    low: '🟢',
    medium: '🟡',
    high: '🔴',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="transit-alerts"
      style={{
        background: 'rgba(26, 26, 46, 0.8)',
        borderRadius: 16,
        padding: 20,
        border: `1px solid ${alertColors[transitData.alert_level]}33`,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
        }}
      >
        <div>
          <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            {alertEmojis[transitData.alert_level]} Daily Transits
          </h3>
          <p style={{ color: '#888', fontSize: 12, margin: '4px 0 0' }}>{transitData.date}</p>
        </div>
        <div
          style={{
            background: `${alertColors[transitData.alert_level]}22`,
            color: alertColors[transitData.alert_level],
            padding: '6px 12px',
            borderRadius: 20,
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          {transitData.alert_level.toUpperCase()} ACTIVITY
        </div>
      </div>

      {/* Highlights */}
      <div style={{ marginBottom: 16 }}>
        {transitData.highlights.map((transit, i) => {
          const isChallenging = ['square', 'opposition'].includes(transit.aspect);
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              style={{
                background: isChallenging ? 'rgba(255,107,107,0.1)' : 'rgba(78,205,196,0.1)',
                borderLeft: `3px solid ${isChallenging ? '#ff6b6b' : '#4ecdc4'}`,
                padding: '12px 16px',
                marginBottom: 8,
                borderRadius: '0 8px 8px 0',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 18 }}>
                  {PLANET_SYMBOLS[transit.transit_planet] || '⭐'}
                </span>
                <span style={{ fontWeight: 600 }}>
                  {transit.transit_planet} {ASPECT_SYMBOLS[transit.aspect]} {transit.natal_point}
                </span>
                <span style={{ color: '#888', fontSize: 12 }}>({transit.orb.toFixed(1)}°)</span>
              </div>
              {transit.interpretation && (
                <p style={{ margin: '8px 0 0', fontSize: 13, color: '#aaa', lineHeight: 1.5 }}>
                  {transit.interpretation}
                </p>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Expand/Collapse */}
      {transitData.transits.length > 3 && (
        <>
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                style={{ overflow: 'hidden' }}
              >
                {transitData.transits.slice(3).map((transit, i) => (
                  <div
                    key={i + 3}
                    style={{
                      padding: '8px 12px',
                      background: 'rgba(255,255,255,0.03)',
                      marginBottom: 4,
                      borderRadius: 6,
                      fontSize: 13,
                    }}
                  >
                    {PLANET_SYMBOLS[transit.transit_planet]} {transit.transit_planet}{' '}
                    {ASPECT_SYMBOLS[transit.aspect]} {transit.natal_point}
                    <span style={{ color: '#666', marginLeft: 8 }}>
                      ({transit.orb.toFixed(1)}°)
                    </span>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              background: 'none',
              border: 'none',
              color: '#4ecdc4',
              cursor: 'pointer',
              fontSize: 13,
              padding: '8px 0',
              width: '100%',
              textAlign: 'center',
            }}
          >
            {expanded ? '▲ Show less' : `▼ Show ${transitData.transits.length - 3} more transits`}
          </button>
        </>
      )}

      {/* Summary */}
      <div
        style={{
          marginTop: 12,
          paddingTop: 12,
          borderTop: '1px solid #333',
          fontSize: 12,
          color: '#666',
          textAlign: 'center',
        }}
      >
        {transitData.total_aspects} active aspects today
      </div>
    </motion.div>
  );
}

export default TransitAlerts;
