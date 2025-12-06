export interface TopFactor {
  aspect?: string;
  description?: string;
  impact?: string;
}

// Retrograde information
export interface RetrogradeInfo {
  planet: string;
  sign: string;
  impact: string;
  house_impact?: string;
  avoid: string[];
  embrace: string[];
}

// Void-of-Course Moon information
export interface VoidOfCourseMoon {
  is_void: boolean;
  current_sign: string;
  moon_degree?: number;
  applying_aspects?: Array<{ planet: string; aspect: string; orb: number }>;
  next_sign?: string;
  hours_until_sign_change?: number | null;
  advice: string;
}

// Current planetary hour information
export interface PlanetaryHourInfo {
  planet: string;
  start: string;
  end: string;
  quality: 'Favorable' | 'Challenging' | 'Neutral';
  suggestion: string;
}

// Enhanced guidance structure
export interface DailyGuidance {
  avoid: {
    activities: string[];
    colors: string[];
    numbers: number[];
  };
  embrace: {
    activities: string[];
    colors: string[];
    time: string;
  };
  retrogrades: RetrogradeInfo[];
  void_of_course_moon: VoidOfCourseMoon;
  current_planetary_hour?: PlanetaryHourInfo | null;
}

export interface PredictionData {
  scope: string;
  date: string;
  theme?: string;
  summary?: { headline?: string; top_factors?: TopFactor[] };
  sections: Array<{
    title: string;
    rating?: number;
    highlights: string[];
    affirmation?: string;
    topic_scores?: Record<string, number>;
  }>;
  numerology?: NumerologyProfile;
  charts?: {
    natal?: {
      planets: Array<{ name: string; sign: string; degree: number; house: number }>;
    };
  };
  element?: string;
  sign?: string;
  life_path_number?: number;
  lucky_numbers?: number[];
  palette?: string[];
  guidance?: DailyGuidance;
}

export interface NumerologyNumber {
  number: number;
  meaning: string;
}

export interface NumerologyProfile {
  core_numbers: {
    life_path: NumerologyNumber;
    expression: NumerologyNumber;
    soul_urge: NumerologyNumber;
    personality: NumerologyNumber;
    maturity?: NumerologyNumber;
  };
  cycles: {
    personal_year: NumerologyNumber;
    personal_month: NumerologyNumber;
    personal_day: NumerologyNumber;
  };
  pinnacles?: Array<{ number: number; meaning: string }>;
  challenges?: Array<{ number: number; meaning: string }>;
}

export interface CompatibilityResult {
  people: Array<{ name: string; dob: string }>;
  topic_scores: Record<string, number>;
  strengths: string[];
  challenges: string[];
  advice: string;
  numerology: {
    a: NumerologyProfile;
    b: NumerologyProfile;
  };
}

export interface NewProfileForm {
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  place_of_birth?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  house_system?: string;
  saveProfile?: boolean; // Opt-in to save profile to database
}

export interface SavedProfile {
  id: number;
  name: string;
  date_of_birth: string;
  time_of_birth?: string | null;
  place_of_birth?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  house_system?: string | null;
}

// Year-Ahead Forecast Types
export interface YearAheadEclipse {
  date: string;
  type: string;
  sign: string;
  degree: number;
}

export interface YearAheadEclipseImpact {
  eclipse: YearAheadEclipse;
  impacts: Array<{
    type: string;
    name: string;
    aspect: string;
    orb: number;
  }>;
  significance: string;
}

export interface YearAheadIngress {
  date: string;
  planet: string;
  sign: string;
  impact: string;
}

export interface YearAheadMonthlyForecast {
  month: number;
  month_name: string;
  year: number;
  season: string;
  focus: string;
  element: string;
  personal_month: number;
  eclipses: YearAheadEclipse[];
  ingresses: YearAheadIngress[];
  highlights: string[];
}

export interface YearAheadForecast {
  year: number;
  personal_year: {
    number: number;
    theme: string;
    description: string;
  };
  universal_year: {
    number: number;
    theme: string;
  };
  solar_return: {
    date: string;
    description: string;
  };
  eclipses: {
    all: YearAheadEclipse[];
    personal_impacts: YearAheadEclipseImpact[];
  };
  ingresses: YearAheadIngress[];
  monthly_forecasts: YearAheadMonthlyForecast[];
  key_themes: string[];
  advice: string[];
}

// Moon Phase Types
export interface MoonPhaseInfo {
  phase_name: string;
  emoji: string;
  illumination: number;
  phase_angle: number;
  days_in_phase: number;
  days_until_next_phase: number;
  is_waxing: boolean;
  is_waning: boolean;
}

export interface MoonEvent {
  type: string;
  date: string;
  emoji: string;
  days_away: number;
  sign: string;
}

export interface MoonRitual {
  phase: string;
  moon_sign: string;
  theme: string;
  energy: string;
  sign_focus: string;
  activities: string[];
  avoid: string[];
  element_boost: string;
  body_focus: string;
  crystals: string[];
  colors: string[];
  affirmation: string;
  natal_insight?: string;
  numerology_insight?: string;
}

export interface MoonPhaseSummary {
  current_phase: MoonPhaseInfo;
  moon_sign: string;
  ritual: MoonRitual;
  upcoming_events: MoonEvent[];
}

// Timing Advisor Types
export interface TimingBestHour {
  start: string;
  end: string;
  planet: string;
}

export interface TimingScoreBreakdown {
  planetary_hour: number;
  moon_phase: number;
  moon_sign: number;
  retrograde: number;
  voc_moon: number;
  personal_day?: number;
}

export interface TimingDayResult {
  activity: string;
  date: string;
  weekday?: string;
  score: number;
  rating: 'Excellent' | 'Good' | 'Moderate' | 'Challenging';
  emoji: string;
  breakdown: TimingScoreBreakdown;
  current_phase: string;
  moon_sign: string;
  warnings: string[];
  recommendations: string[];
  best_hours: TimingBestHour[];
}

export interface TimingAdviceResult {
  activity: string;
  today: TimingDayResult;
  best_upcoming: TimingDayResult;
  today_is_best: boolean;
  all_days: TimingDayResult[];
  advice: string;
}

export interface TimingActivity {
  id: string;
  name: string;
}

export interface BestDaysResult {
  activity: string;
  activity_name: string;
  days_ahead: number;
  best_days: TimingDayResult[];
}

// Journal & Accountability Types
export interface JournalEntry {
  reading_id: number;
  entry: string;
  timestamp: string;
  word_count: number;
  character_count: number;
}

export interface OutcomeRecord {
  reading_id: number;
  outcome: 'yes' | 'no' | 'partial' | 'neutral';
  outcome_emoji: string;
  categories: string[];
  notes: string;
  recorded_at: string;
}

export interface JournalReading {
  id: number;
  scope: string;
  scope_label: string;
  date: string;
  formatted_date: string;
  has_journal: boolean;
  journal_preview: string;
  journal_full: string;
  feedback: string | null;
  feedback_emoji: string;
  content_summary: string;
}

export interface JournalReadingsResponse {
  profile_id: number;
  total: number;
  limit: number;
  offset: number;
  readings: JournalReading[];
}

export interface AccuracyStats {
  total_readings: number;
  rated_readings: number;
  unrated_readings: number;
  accuracy_rate: number;
  by_outcome: Record<string, number>;
  by_scope: Record<string, { accuracy: number; total: number; yes: number; no: number; partial: number }>;
  trend: 'improving' | 'declining' | 'stable' | 'neutral';
  trend_emoji: string;
  message: string;
}

export interface JournalInsights {
  total_journals: number;
  best_scope: string | null;
  best_scope_accuracy: number | null;
  worst_scope: string | null;
  worst_scope_accuracy: number | null;
  journaling_streak: number;
  insights: string[];
}

export interface JournalStatsResponse {
  profile_id: number;
  stats: AccuracyStats;
  insights: JournalInsights;
}

export interface JournalPattern {
  type: string;
  value: string;
  accuracy: number;
  insight: string;
}

export interface JournalPatternsResponse {
  profile_id: number;
  patterns: {
    patterns_found: boolean;
    patterns: JournalPattern[];
    by_day: Record<string, number>;
    sample_size: number;
    message?: string;
  };
}

export interface JournalPrompt {
  text: string;
  category: string;
}

export interface JournalPromptsResponse {
  scope: string;
  prompts: JournalPrompt[];
}

export interface AccountabilityReportSummary {
  total_readings: number;
  with_feedback: number;
  with_journal: number;
  engagement_score: number;
  engagement_rating: 'Excellent' | 'Good' | 'Growing' | 'Getting Started';
}

export interface AccountabilityRecommendation {
  type: string;
  text: string;
}

export interface AccountabilityReport {
  period: string;
  generated_at: string;
  summary: AccountabilityReportSummary;
  accuracy: AccuracyStats;
  insights: JournalInsights;
  patterns: JournalPatternsResponse['patterns'];
  recommendations: AccountabilityRecommendation[];
}

export interface AccountabilityReportResponse {
  profile_id: number;
  report: AccountabilityReport;
}

// ===========================
// Relationship Timeline Types
// ===========================

export interface VenusTransit {
  sign: string;
  start_date: string;
  end_date?: string;
  meaning: string;
  glyph: string;
  love_theme: string;
}

export interface MarsTransit {
  sign: string;
  start_date: string;
  end_date?: string;
  meaning: string;
  glyph: string;
}

export interface VenusRetrogradeStatus {
  is_retrograde: boolean;
  current_period?: {
    start: string;
    end: string;
    sign: string;
  };
  next_retrograde?: {
    start: string;
    end: string;
    sign: string;
  };
  days_until_retrograde?: number;
  days_remaining?: number;
  advice: string;
  emoji: string;
}

export interface RelationshipDate {
  date: string;
  event: string;
  type: 'venus_ingress' | 'mars_ingress' | 'retrograde_start' | 'retrograde_end';
  significance: string;
  rating: number;
}

export interface RelationshipTimingAnalysis {
  date: string;
  venus_sign: string;
  mars_sign: string;
  venus_retrograde: boolean;
  score: number;
  rating: 'Excellent' | 'Good' | 'Moderate' | 'Challenging';
  themes: string[];
  advice: string;
}

export interface BestRelationshipDay {
  date: string;
  score: number;
  venus_sign: string;
  mars_sign: string;
  reason: string;
}

export interface MonthlyRelationshipEvents {
  month: string;
  year: number;
  events: RelationshipDate[];
  venus_signs: string[];
  mars_signs: string[];
  overall_energy: string;
}

export interface RelationshipTimeline {
  generated_at: string;
  year: number;
  venus_current: VenusTransit;
  mars_current: MarsTransit;
  venus_retrograde_status: VenusRetrogradeStatus;
  monthly_overview: MonthlyRelationshipEvents[];
  best_dates: BestRelationshipDay[];
}

export interface RelationshipPhase {
  house: number;
  theme: string;
  description: string;
  timing: string;
}

// ===========================
// Habit Tracker Types
// ===========================

export interface LunarPhase {
  name: string;
  emoji: string;
  energy: string;
  focus: string;
}

export interface HabitCategory {
  id: string;
  name: string;
  emoji: string;
  description: string;
  best_phases: string[];
  avoid_phases: string[];
}

export interface LunarHabitGuidance {
  phase: string;
  theme: string;
  energy_level: string;
  ideal_habits: string[];
  avoid: string[];
  ritual_suggestion: string;
}

export interface Habit {
  id: number;
  name: string;
  category: string;
  frequency: 'daily' | 'weekly' | 'lunar_cycle';
  target_count: number;
  description?: string;
  created_at: string;
  is_active: boolean;
  current_streak?: number;
  lunar_alignment?: number;
}

export interface HabitCompletion {
  habit_id: number;
  completed_at: string;
  date: string;
  weekday: string;
  moon_phase: string;
  notes?: string;
}

export interface HabitStreak {
  current_streak: number;
  longest_streak: number;
  total_completions: number;
  last_completion?: string;
  streak_message: string;
  streak_emoji: string;
}

export interface LunarAlignment {
  score: number;
  rating: 'Excellent' | 'Good' | 'Moderate' | 'Challenging';
  guidance: string;
  boost_available: boolean;
  lunar_boost?: string[];
  emoji: string;
}

export interface HabitRecommendation {
  category: HabitCategory;
  suggestions: string[];
  why_now: string;
}

export interface HabitForecastItem {
  habit: Habit;
  alignment: LunarAlignment;
  completed_today: boolean;
}

export interface HabitForecast {
  date: string;
  moon_phase: string;
  habits: HabitForecastItem[];
  summary: {
    total_habits: number;
    completed: number;
    high_alignment: number;
    phase_theme: string;
  };
}

export interface HabitAnalytics {
  habit_id: number;
  period_days: number;
  total_completions: number;
  completion_rate: number;
  phase_distribution: Record<string, number>;
  best_day: string;
  best_phase: string;
  streak: HabitStreak;
  trend: 'improving' | 'stable' | 'declining';
}

export interface LunarCycleReport {
  cycle_start: string;
  cycle_end: string;
  habits_tracked: number;
  total_completions: number;
  phase_performance: Record<string, { completions: number; percentage: number }>;
  highlights: string[];
  areas_for_growth: string[];
}
