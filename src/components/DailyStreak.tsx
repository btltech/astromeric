import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';

export function DailyStreak() {
  const { streakCount, updateStreak } = useStore();

  useEffect(() => {
    updateStreak();
  }, [updateStreak]);

  if (streakCount === 0) return null;

  return (
    <div className="streak-badge">
      <div className="streak-icon">🔥</div>
      <div className="streak-info">
        <span className="streak-count">{streakCount} Day Streak</span>
        <span className="streak-label">Your cosmic momentum is building!</span>
      </div>
      <div className="streak-progress">
        {[...Array(7)].map((_, i) => (
          <div
            key={i}
            className={`streak-dot ${i < streakCount % 8 ? 'active' : ''}`}
            title={`Day ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}
