import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface FeedbackToggleProps {
  sectionId: string;
  question?: string;
  onFeedback?: (sectionId: string, resonates: boolean) => void;
}

// Store feedback in localStorage
const FEEDBACK_KEY = 'astronumeric_feedback';
const STREAK_KEY = 'astronumeric_streak';

interface FeedbackData {
  [sectionId: string]: {
    resonates: boolean;
    timestamp: number;
  };
}

function getFeedbackData(): FeedbackData {
  try {
    const data = localStorage.getItem(FEEDBACK_KEY);
    return data ? JSON.parse(data) : {};
  } catch {
    return {};
  }
}

function saveFeedback(sectionId: string, resonates: boolean) {
  const data = getFeedbackData();
  data[sectionId] = { resonates, timestamp: Date.now() };
  localStorage.setItem(FEEDBACK_KEY, JSON.stringify(data));
}

function getStreak(): number {
  try {
    const streak = localStorage.getItem(STREAK_KEY);
    return streak ? JSON.parse(streak).count : 0;
  } catch {
    return 0;
  }
}

function updateStreak(resonates: boolean) {
  const streakData = localStorage.getItem(STREAK_KEY);
  let count = 0;

  if (streakData) {
    const parsed = JSON.parse(streakData);
    count = parsed.count || 0;
  }

  if (resonates) {
    count += 1;
  } else {
    count = 0; // Reset streak on negative feedback
  }

  localStorage.setItem(STREAK_KEY, JSON.stringify({ count, lastUpdate: Date.now() }));
  return count;
}

export function FeedbackToggle({
  sectionId,
  question = 'Does this resonate?',
  onFeedback,
}: FeedbackToggleProps) {
  const [feedback, setFeedback] = useState<boolean | null>(null);
  const [showThanks, setShowThanks] = useState(false);

  useEffect(() => {
    // Load existing feedback for this section
    const data = getFeedbackData();
    if (data[sectionId]) {
      setFeedback(data[sectionId].resonates);
    }
  }, [sectionId]);

  const handleFeedback = (resonates: boolean) => {
    setFeedback(resonates);
    saveFeedback(sectionId, resonates);
    updateStreak(resonates);

    // Show thanks briefly
    setShowThanks(true);
    setTimeout(() => setShowThanks(false), 2000);

    onFeedback?.(sectionId, resonates);
  };

  return (
    <div className="feedback-toggle">
      <span className="feedback-question">{question}</span>

      <div className="feedback-buttons">
        <button
          className={`feedback-btn ${feedback === true ? 'selected positive' : ''}`}
          onClick={() => handleFeedback(true)}
          aria-label="Yes, this resonates"
          aria-pressed={feedback === true}
        >
          👍
        </button>
        <button
          className={`feedback-btn ${feedback === false ? 'selected negative' : ''}`}
          onClick={() => handleFeedback(false)}
          aria-label="No, this doesn't resonate"
          aria-pressed={feedback === false}
        >
          👎
        </button>
      </div>

      <AnimatePresence>
        {showThanks && (
          <motion.span
            className="feedback-thanks"
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0 }}
          >
            Thanks!
          </motion.span>
        )}
      </AnimatePresence>
    </div>
  );
}

export function AccuracyStreak() {
  const [streak, setStreak] = useState(0);

  useEffect(() => {
    setStreak(getStreak());

    // Listen for storage changes
    const handleStorage = () => {
      setStreak(getStreak());
    };

    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  if (streak === 0) return null;

  const getStreakMessage = (count: number): string => {
    if (count >= 10) return 'Cosmic connection!';
    if (count >= 5) return 'On a roll!';
    if (count >= 3) return 'Building momentum';
    return 'Resonance streak';
  };

  return (
    <motion.div
      className="accuracy-streak"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <span className="streak-badge">
        <span className="streak-icon">🔥</span>
        <span className="streak-count">{streak}</span>
      </span>
      <span className="streak-message">{getStreakMessage(streak)}</span>
    </motion.div>
  );
}

// Hook to track section feedback across a reading
export function useReadingFeedback() {
  const [sectionFeedback, setSectionFeedback] = useState<Record<string, boolean>>({});

  const recordFeedback = (sectionId: string, resonates: boolean) => {
    setSectionFeedback((prev) => ({ ...prev, [sectionId]: resonates }));
    saveFeedback(sectionId, resonates);
  };

  const getOverallAccuracy = (): number => {
    const entries = Object.values(sectionFeedback);
    if (entries.length === 0) return 0;
    const positive = entries.filter(Boolean).length;
    return Math.round((positive / entries.length) * 100);
  };

  return {
    sectionFeedback,
    recordFeedback,
    getOverallAccuracy,
    totalResponses: Object.keys(sectionFeedback).length,
  };
}
