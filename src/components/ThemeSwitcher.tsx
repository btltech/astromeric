import React from 'react';
import { motion } from 'framer-motion';
import { useStore } from '../store/useStore';

const THEMES = [
  { id: 'default', name: 'Cosmic Violet', colors: ['#8b5cf6', '#0a0c18'] },
  { id: 'ocean', name: 'Ocean Depths', colors: ['#14b8a6', '#0c1418'] },
  { id: 'midnight', name: 'Midnight Coral', colors: ['#a855f7', '#fb7185'] },
  { id: 'sage', name: 'Sage Garden', colors: ['#84cc16', '#d4a574'] },
] as const;

export function ThemeSwitcher() {
  const { theme, setTheme } = useStore();

  return (
    <div className="theme-switcher">
      <span className="theme-label">Theme</span>
      <div className="theme-options">
        {THEMES.map((t) => (
          <motion.button
            key={t.id}
            className={`theme-option ${theme === t.id ? 'active' : ''}`}
            onClick={() => setTheme(t.id as typeof theme)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title={t.name}
            aria-pressed={theme === t.id}
          >
            <span
              className="theme-preview"
              style={{
                background: `linear-gradient(135deg, ${t.colors[0]} 0%, ${t.colors[1]} 100%)`,
              }}
            />
            <span className="theme-name">{t.name}</span>
          </motion.button>
        ))}
      </div>
    </div>
  );
}

export function ToneSlider() {
  const { tonePreference, setTonePreference } = useStore();

  const getToneLabel = (value: number): string => {
    if (value < 25) return 'Practical';
    if (value < 50) return 'Balanced-Practical';
    if (value < 75) return 'Balanced-Mystical';
    return 'Mystical';
  };

  return (
    <div className="tone-slider">
      <div className="tone-header">
        <span className="tone-label">Reading Tone</span>
        <span className="tone-value">{getToneLabel(tonePreference)}</span>
      </div>
      <div className="tone-track-container">
        <span className="tone-end">🔧 Practical</span>
        <input
          type="range"
          min="0"
          max="100"
          value={tonePreference}
          onChange={(e) => setTonePreference(Number(e.target.value))}
          className="tone-range"
          aria-label="Reading tone preference"
        />
        <span className="tone-end">✨ Mystical</span>
      </div>
    </div>
  );
}
