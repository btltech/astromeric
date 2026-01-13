import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { fetchWeeklyForecast, type ForecastDay, type ProfilePayload } from '../api/client';
import { getComparisonUrl } from '../utils/comparison';
import { toast } from './Toast';

interface Props {
  profile: ProfilePayload;
  showShare?: boolean;
}

export function WeeklyVibe({ profile, showShare = true }: Props) {
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchWeeklyForecast(profile);
        setForecast(data.days);
      } catch (err) {
        console.error('Failed to load weekly vibe:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [profile]);

  if (loading || forecast.length === 0) {
    return (
       <div className="weekly-vibe-placeholder">
         <div className="skeleton-line" style={{ width: '40%', height: '20px', marginBottom: '1rem' }}></div>
         <div style={{ display: 'flex', gap: '1rem' }}>
           {[...Array(7)].map((_, i) => (
             <div key={i} className="skeleton-circle" style={{ width: '60px', height: '80px', borderRadius: '12px' }}></div>
           ))}
         </div>
       </div>
    );
  }

  return (
    <section className="weekly-vibe-section">
      <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 className="section-title">✨ Weekly Cosmic Pulse</h3>
          <span className="section-subtitle">Your energy forecast for the next 7 days</span>
        </div>
        {showShare && (
          <button
            className="btn-aura-share"
            style={{ padding: '8px 16px', fontSize: '0.8rem' }}
            onClick={() => {
              const url = getComparisonUrl({
                name: profile.name,
                dob: profile.date_of_birth,
                tob: profile.time_of_birth,
                lat: profile.latitude,
                lng: profile.longitude,
                tz: profile.timezone,
              });
              navigator.clipboard.writeText(url);
              toast.success('Comparison link copied! Send it to a friend 👯‍♀️');
            }}
          >
            Share & Compare
          </button>
        )}
      </div>
      
      <div className="vibe-timeline">
        {forecast.map((day, i) => {
          const dateObj = new Date(day.date);
          const isToday = i === 0;
          
          return (
            <motion.div
              key={day.date}
              className={`vibe-day-card ${isToday ? 'today' : ''}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <div className="vibe-day-header">
                <span className="vibe-weekday">{dateObj.toLocaleDateString(undefined, { weekday: 'short' })}</span>
                <span className="vibe-daynum">{dateObj.getDate()}</span>
              </div>
              
              <div className="vibe-display" title={day.recommendation}>
                <div className="vibe-glow" style={{ backgroundColor: getScoreColor(day.score) }}></div>
                <span className="vibe-emoji">{day.icon}</span>
              </div>
              
              <div className="vibe-meta">
                <span className="vibe-label">{day.vibe}</span>
                <div className="vibe-dot-container">
                  <div className="vibe-dot" style={{ backgroundColor: getScoreColor(day.score) }}></div>
                  <span className="vibe-score">{day.score}%</span>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}

function getScoreColor(score: number) {
  if (score >= 80) return '#ffcc33'; // Gold
  if (score >= 60) return '#a29bfe'; // Purple
  return '#ff5e57'; // Red
}
