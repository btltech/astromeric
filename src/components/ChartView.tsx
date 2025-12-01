/**
 * ChartView.tsx
 * Full natal chart view with interactive wheel and interpretations
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ChartWheel } from './ChartWheel';
import { apiFetch } from '../api/client';
import type { SavedProfile } from '../types';

interface Props {
  profile: SavedProfile;
  onExportPDF?: () => void;
}

interface ChartData {
  planets: Record<string, { name: string; sign: string; degree: number; house: number }>;
  houses: Record<string, { cusp: number; sign: string }>;
  aspects: Array<{ planet1: string; planet2: string; aspect: string; orb: number }>;
  ascendant?: { sign: string; degree: number };
  midheaven?: { sign: string; degree: number };
}

export function ChartView({ profile, onExportPDF }: Props) {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

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

      onExportPDF?.();
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Failed to export PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40 }}>
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          style={{ fontSize: 48 }}
        >
          ✨
        </motion.div>
        <p style={{ color: '#888', marginTop: 16 }}>Calculating chart...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#ff6b6b' }}>
        <p>⚠️ {error}</p>
      </div>
    );
  }

  if (!chartData) return null;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="chart-view">
      <div style={{ textAlign: 'center', marginBottom: 20 }}>
        <h2 style={{ marginBottom: 8 }}>{profile.name}&apos;s Natal Chart</h2>
        <p style={{ color: '#888', fontSize: 14 }}>
          {profile.date_of_birth} {profile.time_of_birth && `at ${profile.time_of_birth}`}
          {profile.place_of_birth && ` • ${profile.place_of_birth}`}
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
        <ChartWheel chartData={chartData} size={450} interactive={true} />
      </div>

      {/* Quick Stats */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: 12,
          marginBottom: 24,
        }}
      >
        {chartData.planets.Sun && (
          <div className="stat-card">
            <span style={{ fontSize: 24 }}>☉</span>
            <div>Sun in {chartData.planets.Sun.sign}</div>
          </div>
        )}
        {chartData.planets.Moon && (
          <div className="stat-card">
            <span style={{ fontSize: 24 }}>☽</span>
            <div>Moon in {chartData.planets.Moon.sign}</div>
          </div>
        )}
        {chartData.ascendant && (
          <div className="stat-card">
            <span style={{ fontSize: 24 }}>↑</span>
            <div>{chartData.ascendant.sign} Rising</div>
          </div>
        )}
      </div>

      {/* Export Button */}
      <div style={{ textAlign: 'center' }}>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleExportPDF}
          disabled={exporting}
          className="btn-secondary"
          style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}
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
        .stat-card {
          background: rgba(78, 205, 196, 0.1);
          border: 1px solid rgba(78, 205, 196, 0.3);
          border-radius: 12px;
          padding: 16px;
          text-align: center;
        }
        .stat-card div {
          margin-top: 8px;
          font-size: 14px;
          color: #ddd;
        }
      `}</style>
    </motion.div>
  );
}

export default ChartView;
