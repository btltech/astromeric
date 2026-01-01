import React, { useState, useEffect } from 'react';
import { toast } from './Toast';
import {
  fetchHabitCategories,
  fetchLunarHabitGuidance,
  fetchHabitRecommendations,
  fetchHabitAlignment,
  createHabit,
  logHabitCompletion,
  fetchHabitStreak,
  fetchTodayHabitForecast,
} from '../api/client';
import type {
  HabitCategory,
  LunarHabitGuidance,
  Habit,
  HabitCompletion,
  HabitStreak,
  HabitForecast,
  LunarAlignment,
} from '../types';

type TabType = 'today' | 'habits' | 'create' | 'insights';

// Demo moon phases for display
const MOON_PHASES = [
  { key: 'new_moon', name: 'New Moon', emoji: '🌑' },
  { key: 'waxing_crescent', name: 'Waxing Crescent', emoji: '🌒' },
  { key: 'first_quarter', name: 'First Quarter', emoji: '🌓' },
  { key: 'waxing_gibbous', name: 'Waxing Gibbous', emoji: '🌔' },
  { key: 'full_moon', name: 'Full Moon', emoji: '🌕' },
  { key: 'waning_gibbous', name: 'Waning Gibbous', emoji: '🌖' },
  { key: 'last_quarter', name: 'Last Quarter', emoji: '🌗' },
  { key: 'waning_crescent', name: 'Waning Crescent', emoji: '🌘' },
];

export function HabitTracker() {
  const [activeTab, setActiveTab] = useState<TabType>('today');
  const [categories, setCategories] = useState<HabitCategory[]>([]);
  const [phaseGuidance, setPhaseGuidance] = useState<Record<string, LunarHabitGuidance>>({});
  const [currentPhase, setCurrentPhase] = useState<string>('new_moon');
  const [habits, setHabits] = useState<Habit[]>([]);
  const [completions, setCompletions] = useState<HabitCompletion[]>([]);
  const [forecast, setForecast] = useState<HabitForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state for creating habits
  const [newHabitName, setNewHabitName] = useState('');
  const [newHabitCategory, setNewHabitCategory] = useState('');
  const [newHabitFrequency, setNewHabitFrequency] = useState<'daily' | 'weekly' | 'lunar_cycle'>('daily');
  const [newHabitDescription, setNewHabitDescription] = useState('');
  const [createSuccess, setCreateSuccess] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);

        const [categoriesRes, guidanceRes] = await Promise.all([
          fetchHabitCategories(),
          fetchLunarHabitGuidance(),
        ]);

        setCategories(categoriesRes.categories);
        setPhaseGuidance(guidanceRes.phases);

        // Set default category
        if (categoriesRes.categories.length > 0) {
          setNewHabitCategory(categoriesRes.categories[0].id);
        }

        // Load demo habits from localStorage
        const savedHabits = localStorage.getItem('astromeric_habits')
          || localStorage.getItem('astronumeric_habits');
        if (savedHabits) {
          setHabits(JSON.parse(savedHabits));
        }

        const savedCompletions = localStorage.getItem('astromeric_completions')
          || localStorage.getItem('astronumeric_completions');
        if (savedCompletions) {
          setCompletions(JSON.parse(savedCompletions));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  // Load forecast when habits or phase changes
  useEffect(() => {
    if (habits.length > 0 && activeTab === 'today') {
      const todayCompletions = completions
        .filter((c) => c.date === new Date().toISOString().split('T')[0])
        .map((c) => c.habit_id);

      fetchTodayHabitForecast(habits, currentPhase, todayCompletions)
        .then(setForecast)
        .catch(() => toast.error('Failed to load habit forecast'));
    }
  }, [habits, currentPhase, completions, activeTab]);

  // Save habits to localStorage
  useEffect(() => {
    if (habits.length > 0) {
      localStorage.setItem('astronumeric_habits', JSON.stringify(habits));
    }
  }, [habits]);

  // Save completions to localStorage
  useEffect(() => {
    if (completions.length > 0) {
      localStorage.setItem('astronumeric_completions', JSON.stringify(completions));
    }
  }, [completions]);

  async function handleCreateHabit(e: React.FormEvent) {
    e.preventDefault();
    if (!newHabitName.trim() || !newHabitCategory) return;

    try {
      const res = await createHabit(
        {
          name: newHabitName.trim(),
          category: newHabitCategory,
          frequency: newHabitFrequency,
          description: newHabitDescription.trim(),
        },
        currentPhase
      );

      if (res.success) {
        const newHabit: Habit = {
          ...res.habit,
          id: Date.now(), // Local ID
        };
        setHabits((prev) => [...prev, newHabit]);
        setNewHabitName('');
        setNewHabitDescription('');
        setCreateSuccess(`✨ "${newHabit.name}" created! Perfect for this lunar phase.`);
        setTimeout(() => setCreateSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Failed to create habit:', err);
      // Create locally anyway
      const newHabit: Habit = {
        id: Date.now(),
        name: newHabitName.trim(),
        category: newHabitCategory,
        frequency: newHabitFrequency,
        target_count: 1,
        description: newHabitDescription.trim(),
        created_at: new Date().toISOString(),
        is_active: true,
      };
      setHabits((prev) => [...prev, newHabit]);
      setNewHabitName('');
      setNewHabitDescription('');
      setCreateSuccess(`✨ "${newHabit.name}" created locally!`);
      setTimeout(() => setCreateSuccess(null), 3000);
    }
  }

  async function handleLogCompletion(habit: Habit) {
    const today = new Date().toISOString().split('T')[0];
    const alreadyCompleted = completions.some(
      (c) => c.habit_id === habit.id && c.date === today
    );

    if (alreadyCompleted) {
      // Remove completion
      setCompletions((prev) =>
        prev.filter((c) => !(c.habit_id === habit.id && c.date === today))
      );
    } else {
      // Add completion
      try {
        const res = await logHabitCompletion(habit.id, currentPhase);
        setCompletions((prev) => [...prev, res.completion]);
      } catch (err) {
        // Create locally
        const completion: HabitCompletion = {
          habit_id: habit.id,
          completed_at: new Date().toISOString(),
          date: today,
          weekday: new Date().toLocaleDateString('en-US', { weekday: 'long' }),
          moon_phase: currentPhase,
        };
        setCompletions((prev) => [...prev, completion]);
      }
    }
  }

  function handleDeleteHabit(habitId: number) {
    setHabits((prev) => prev.filter((h) => h.id !== habitId));
    setCompletions((prev) => prev.filter((c) => c.habit_id !== habitId));
  }

  function getAlignmentColor(score: number): string {
    if (score >= 80) return 'var(--color-success)';
    if (score >= 60) return 'var(--color-info)';
    if (score >= 40) return 'var(--color-warning)';
    return 'var(--color-error)';
  }

  function getStreakForHabit(habitId: number): { current: number; emoji: string } {
    const habitCompletions = completions
      .filter((c) => c.habit_id === habitId)
      .sort((a, b) => b.date.localeCompare(a.date));

    if (habitCompletions.length === 0) return { current: 0, emoji: '🌱' };

    let streak = 0;
    let expectedDate = new Date();
    expectedDate.setHours(0, 0, 0, 0);

    for (const comp of habitCompletions) {
      const compDate = new Date(comp.date);
      compDate.setHours(0, 0, 0, 0);

      const dayDiff = Math.floor(
        (expectedDate.getTime() - compDate.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (dayDiff <= 1) {
        streak++;
        expectedDate = new Date(compDate);
        expectedDate.setDate(expectedDate.getDate() - 1);
      } else {
        break;
      }
    }

    const emoji =
      streak >= 30 ? '🏆' : streak >= 14 ? '🔥' : streak >= 7 ? '⭐' : streak >= 1 ? '✨' : '🌱';

    return { current: streak, emoji };
  }

  function getCurrentPhaseInfo() {
    const phase = MOON_PHASES.find((p) => p.key === currentPhase);
    const guidance = phaseGuidance[currentPhase];
    return { phase, guidance };
  }

  if (loading) {
    return (
      <div className="habit-tracker loading">
        <div className="loading-spinner">🌙</div>
        <p>Loading habit tracker...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="habit-tracker error">
        <p className="error-message">❌ {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  const { phase: currentPhaseInfo, guidance } = getCurrentPhaseInfo();

  return (
    <div className="habit-tracker">
      <header className="tracker-header">
        <h2>🌙 Lunar Habit Tracker</h2>
        <p className="subtitle">Align your habits with the Moon's energy</p>
      </header>

      {/* Moon Phase Selector */}
      <div className="phase-selector">
        <label>Current Moon Phase:</label>
        <div className="phase-buttons">
          {MOON_PHASES.map((phase) => (
            <button
              key={phase.key}
              className={currentPhase === phase.key ? 'active' : ''}
              onClick={() => setCurrentPhase(phase.key)}
              title={phase.name}
            >
              {phase.emoji}
            </button>
          ))}
        </div>
        {currentPhaseInfo && (
          <div className="current-phase-info">
            <strong>
              {currentPhaseInfo.emoji} {currentPhaseInfo.name}
            </strong>
            {guidance && <span className="energy">• {guidance.energy_level} Energy</span>}
          </div>
        )}
      </div>

      {/* Phase Guidance Banner */}
      {guidance && (
        <div className="phase-guidance-banner">
          <h3>{guidance.theme}</h3>
          <p>💡 {guidance.ritual_suggestion}</p>
          <div className="guidance-tags">
            {guidance.ideal_habits.map((habit) => (
              <span key={habit} className="tag ideal">
                ✓ {habit}
              </span>
            ))}
            {guidance.avoid.slice(0, 2).map((item) => (
              <span key={item} className="tag avoid">
                ✗ {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <nav className="tracker-tabs" role="tablist" aria-label="Habit tracker sections">
        <button
          role="tab"
          aria-selected={activeTab === 'today'}
          aria-controls="today-panel"
          id="today-tab"
          tabIndex={activeTab === 'today' ? 0 : -1}
          className={activeTab === 'today' ? 'active' : ''}
          onClick={() => setActiveTab('today')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') {
              setActiveTab('habits');
            } else if (e.key === 'ArrowLeft') {
              setActiveTab('insights');
            }
          }}
        >
          📅 Today
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'habits'}
          aria-controls="habits-panel"
          id="habits-tab"
          tabIndex={activeTab === 'habits' ? 0 : -1}
          className={activeTab === 'habits' ? 'active' : ''}
          onClick={() => setActiveTab('habits')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') {
              setActiveTab('create');
            } else if (e.key === 'ArrowLeft') {
              setActiveTab('today');
            }
          }}
        >
          📋 My Habits
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'create'}
          aria-controls="create-panel"
          id="create-tab"
          tabIndex={activeTab === 'create' ? 0 : -1}
          className={activeTab === 'create' ? 'active' : ''}
          onClick={() => setActiveTab('create')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') {
              setActiveTab('insights');
            } else if (e.key === 'ArrowLeft') {
              setActiveTab('habits');
            }
          }}
        >
          ➕ Create
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'insights'}
          aria-controls="insights-panel"
          id="insights-tab"
          tabIndex={activeTab === 'insights' ? 0 : -1}
          className={activeTab === 'insights' ? 'active' : ''}
          onClick={() => setActiveTab('insights')}
          onKeyDown={(e) => {
            if (e.key === 'ArrowRight') {
              setActiveTab('today');
            } else if (e.key === 'ArrowLeft') {
              setActiveTab('create');
            }
          }}
        >
          📊 Insights
        </button>
      </nav>

      {/* Tab Content */}
      <div className="tab-content">
        {/* Today Tab */}
        {activeTab === 'today' && (
          <div className="today-tab">
            {habits.length === 0 ? (
              <div className="empty-state">
                <span className="emoji">🌱</span>
                <h3>No habits yet</h3>
                <p>Create your first lunar-aligned habit to get started!</p>
                <button onClick={() => setActiveTab('create')}>
                  ➕ Create Habit
                </button>
              </div>
            ) : (
              <>
                {forecast && (
                  <div className="forecast-summary">
                    <div className="stat">
                      <span className="value">{forecast.summary.completed}</span>
                      <span className="label">Completed</span>
                    </div>
                    <div className="stat">
                      <span className="value">{forecast.summary.total_habits}</span>
                      <span className="label">Total</span>
                    </div>
                    <div className="stat">
                      <span className="value">{forecast.summary.high_alignment}</span>
                      <span className="label">High Alignment</span>
                    </div>
                  </div>
                )}

                <div className="habits-list today-list">
                  {habits
                    .filter((h) => h.is_active)
                    .map((habit) => {
                      const today = new Date().toISOString().split('T')[0];
                      const isCompleted = completions.some(
                        (c) => c.habit_id === habit.id && c.date === today
                      );
                      const streak = getStreakForHabit(habit.id);
                      const category = categories.find((c) => c.id === habit.category);

                      return (
                        <div
                          key={habit.id}
                          className={`habit-item ${isCompleted ? 'completed' : ''}`}
                        >
                          <button
                            className="check-button"
                            onClick={() => handleLogCompletion(habit)}
                          >
                            {isCompleted ? '✅' : '⭕'}
                          </button>
                          <div className="habit-info">
                            <span className="name">
                              {category?.emoji} {habit.name}
                            </span>
                            <span className="streak">
                              {streak.emoji} {streak.current} day streak
                            </span>
                          </div>
                          <span className="frequency">{habit.frequency}</span>
                        </div>
                      );
                    })}
                </div>
              </>
            )}
          </div>
        )}

        {/* My Habits Tab */}
        {activeTab === 'habits' && (
          <div className="habits-tab">
            {habits.length === 0 ? (
              <div className="empty-state">
                <span className="emoji">📋</span>
                <h3>Your habit library is empty</h3>
                <button onClick={() => setActiveTab('create')}>
                  ➕ Create Your First Habit
                </button>
              </div>
            ) : (
              <div className="habits-grid">
                {habits.map((habit) => {
                  const category = categories.find((c) => c.id === habit.category);
                  const streak = getStreakForHabit(habit.id);
                  const totalCompletions = completions.filter(
                    (c) => c.habit_id === habit.id
                  ).length;

                  return (
                    <div key={habit.id} className="habit-card">
                      <div className="card-header">
                        <span className="category-emoji">
                          {category?.emoji || '📌'}
                        </span>
                        <button
                          className="delete-btn"
                          onClick={() => handleDeleteHabit(habit.id)}
                          title="Delete habit"
                        >
                          ×
                        </button>
                      </div>
                      <h4>{habit.name}</h4>
                      <p className="category-name">{category?.name}</p>
                      {habit.description && (
                        <p className="description">{habit.description}</p>
                      )}
                      <div className="habit-stats">
                        <span className="streak">
                          {streak.emoji} {streak.current} streak
                        </span>
                        <span className="total">
                          {totalCompletions} total
                        </span>
                      </div>
                      <span className="frequency-badge">{habit.frequency}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Create Tab */}
        {activeTab === 'create' && (
          <div className="create-tab">
            <form onSubmit={handleCreateHabit} className="create-form">
              {createSuccess && (
                <div className="success-message">{createSuccess}</div>
              )}

              <div className="form-group">
                <label htmlFor="habit-name">Habit Name</label>
                <input
                  type="text"
                  id="habit-name"
                  value={newHabitName}
                  onChange={(e) => setNewHabitName(e.target.value)}
                  placeholder="e.g., Morning Meditation"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="habit-category">Category</label>
                <select
                  id="habit-category"
                  value={newHabitCategory}
                  onChange={(e) => setNewHabitCategory(e.target.value)}
                  required
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.emoji} {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="habit-frequency">Frequency</label>
                <select
                  id="habit-frequency"
                  value={newHabitFrequency}
                  onChange={(e) =>
                    setNewHabitFrequency(
                      e.target.value as 'daily' | 'weekly' | 'lunar_cycle'
                    )
                  }
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="lunar_cycle">Lunar Cycle</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="habit-description">Description (optional)</label>
                <textarea
                  id="habit-description"
                  value={newHabitDescription}
                  onChange={(e) => setNewHabitDescription(e.target.value)}
                  placeholder="Add details about your habit..."
                  rows={3}
                />
              </div>

              <button type="submit" className="create-btn" disabled={!newHabitName.trim()}>
                🌙 Create Lunar-Aligned Habit
              </button>
            </form>

            {/* Category Reference */}
            <div className="category-reference">
              <h3>Category Guide</h3>
              <div className="categories-grid">
                {categories.map((cat) => (
                  <div
                    key={cat.id}
                    className={`category-card ${newHabitCategory === cat.id ? 'selected' : ''}`}
                    onClick={() => setNewHabitCategory(cat.id)}
                  >
                    <span className="emoji">{cat.emoji}</span>
                    <h4>{cat.name}</h4>
                    <p>{cat.description}</p>
                    <div className="best-phases">
                      Best: {cat.best_phases.join(', ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="insights-tab">
            {habits.length === 0 ? (
              <div className="empty-state">
                <span className="emoji">📊</span>
                <h3>No data yet</h3>
                <p>Create habits and log completions to see insights!</p>
              </div>
            ) : (
              <>
                <div className="insights-summary">
                  <div className="insight-card">
                    <span className="emoji">📌</span>
                    <span className="value">{habits.length}</span>
                    <span className="label">Active Habits</span>
                  </div>
                  <div className="insight-card">
                    <span className="emoji">✅</span>
                    <span className="value">{completions.length}</span>
                    <span className="label">Total Completions</span>
                  </div>
                  <div className="insight-card">
                    <span className="emoji">🔥</span>
                    <span className="value">
                      {Math.max(...habits.map((h) => getStreakForHabit(h.id).current), 0)}
                    </span>
                    <span className="label">Longest Streak</span>
                  </div>
                </div>

                <div className="phase-distribution">
                  <h3>Completions by Moon Phase</h3>
                  <div className="phase-bars">
                    {MOON_PHASES.map((phase) => {
                      const count = completions.filter(
                        (c) => c.moon_phase === phase.key
                      ).length;
                      const maxCount = Math.max(
                        ...MOON_PHASES.map(
                          (p) => completions.filter((c) => c.moon_phase === p.key).length
                        ),
                        1
                      );
                      const percentage = (count / maxCount) * 100;

                      return (
                        <div key={phase.key} className="phase-bar">
                          <span className="phase-emoji">{phase.emoji}</span>
                          <div className="bar-container">
                            <div
                              className="bar-fill"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                          <span className="count">{count}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className="habit-rankings">
                  <h3>Habit Performance</h3>
                  <div className="rankings-list">
                    {habits
                      .map((habit) => ({
                        habit,
                        completions: completions.filter((c) => c.habit_id === habit.id).length,
                        streak: getStreakForHabit(habit.id),
                      }))
                      .sort((a, b) => b.completions - a.completions)
                      .map(({ habit, completions: count, streak }) => {
                        const category = categories.find((c) => c.id === habit.category);
                        return (
                          <div key={habit.id} className="ranking-item">
                            <span className="rank-emoji">{streak.emoji}</span>
                            <span className="habit-name">
                              {category?.emoji} {habit.name}
                            </span>
                            <span className="completions">{count} completions</span>
                            <span className="streak">{streak.current} day streak</span>
                          </div>
                        );
                      })}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default HabitTracker;
