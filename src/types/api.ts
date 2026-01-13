/**
 * Generated TypeScript types for API responses
 * These replace the generic Record<string, unknown> types
 */

// ============================================================================
// CORE TYPES
// ============================================================================

export interface Profile {
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
}

export interface ApiResponseMeta {
  request_id?: string;
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  field?: string;
  [key: string]: unknown;
}

// ============================================================================
// NATAL CHART TYPES
// ============================================================================

export interface PlanetPosition {
  name: string;
  longitude: number;
  latitude: number;
  speed: number;
  house: number;
}

export interface AspectData {
  planet1: string;
  planet2: string;
  type: string;
  orb: number;
  applying: boolean;
}

export interface NatalChartData {
  sun_sign: string;
  moon_sign: string;
  rising_sign: string;
  houses: Record<string, unknown>;
  aspects: AspectData[];
  asteroids?: Record<string, unknown>[];
}

export interface NatalProfileData {
  profile: Profile;
  chart: NatalChartData;
  interpretation: Record<string, string>;
  generated_at: string;
}

export interface ApiResponse<T = unknown> {
  status: 'success' | 'error' | 'partial';
  data?: T;
  error?: ApiError;
  message?: string;
  request_id?: string;
  timestamp: string;
}

// ============================================================================
// FORECAST TYPES
// ============================================================================

export interface DailyForecastReading {
  date: string;
  energy_level: number;
  themes: string[];
  planetary_aspects: AspectData[];
  recommendation: string;
}

export interface ForecastData {
  profile: Profile;
  scope: 'daily' | 'weekly' | 'monthly' | 'yearly';
  readings: DailyForecastReading[];
  generated_at: string;
}

// ============================================================================
// COMPATIBILITY TYPES
// ============================================================================

export interface CompatibilityScore {
  emotional: number;
  intellectual: number;
  physical: number;
  spiritual: number;
  overall: number;
}

export interface CompatibilityData {
  person_a: Profile;
  person_b: Profile;
  relationship_type: 'romantic' | 'friendship' | 'business';
  synastry: Record<string, unknown>;
  scores: CompatibilityScore;
  summary: string;
  strengths: string[];
  challenges: string[];
  generated_at: string;
}

// ============================================================================
// NUMEROLOGY TYPES
// ============================================================================

export interface NumerologyNumber {
  number: number;
  meaning: string;
  keywords: string[];
  color?: string;
}

export interface NumerologyData {
  profile: Profile;
  life_path: NumerologyNumber;
  expression: NumerologyNumber;
  personal_year: NumerologyNumber;
  challenge_numbers: NumerologyNumber[];
  generated_at: string;
}

// ============================================================================
// DAILY FEATURES TYPES
// ============================================================================

export interface LuckyColor {
  primary: string;
  primary_hex: string;
  accent: string;
  description: string;
}

export interface TarotData {
  card: string;
  card_number: number;
  keywords: string[];
  message: string;
  reversed: boolean;
  daily_advice: string;
}

export interface DailyFeaturesData {
  date: string;
  lucky_numbers: number[];
  lucky_colors: LuckyColor;
  lucky_planet: Record<string, unknown>;
  affirmation: Record<string, string>;
  tarot: TarotData;
  manifestation: Record<string, string>;
  mood_forecast: Record<string, unknown>;
  retrograde_alerts: Array<{
    planet: string;
    status: string;
    message: string;
    advice: string[];
  }>;
  personal_day: number;
  life_path: number;
}

// ============================================================================
// LEARNING TYPES
// ============================================================================

export interface LearningModule {
  id: string;
  title: string;
  description: string;
  item_count: number;
  content?: Record<string, unknown>;
}

export interface LearningModulesResponse {
  modules: LearningModule[];
}

// ============================================================================
// TAROT & ORACLE TYPES
// ============================================================================

export interface TarotCardResponse {
  card: string;
  card_number: number;
  keywords: string[];
  message: string;
  reversed: boolean;
  daily_advice: string;
  drawn_at: string;
}

export interface YesNoResponse {
  question: string;
  answer: 'Yes' | 'No' | 'Maybe' | 'Wait';
  emoji: string;
  confidence: number;
  message: string;
  reasoning: string;
  timing: string;
  asked_at: string;
}

// ============================================================================
// MOON PHASE TYPES
// ============================================================================

export interface MoonPhaseInfo {
  current_phase: string;
  illumination: number;
  days_in_cycle: number;
  phase_description: string;
  next_new_moon: string;
  next_full_moon: string;
}

export interface MoonEvent {
  date: string;
  event_type: 'new_moon' | 'full_moon' | 'first_quarter' | 'last_quarter';
  sign: string;
  description: string;
}

// ============================================================================
// TIMING ADVISOR TYPES
// ============================================================================

export interface TimingActivity {
  key: string;
  name: string;
  description: string;
  favorable_moon_phases: string[];
  favorable_signs: string[];
}

export interface BestDayTiming {
  date: string;
  score: number;
  reason: string;
  planetary_support: string[];
}

export interface TimingAdviceResult {
  activity: string;
  today: BestDayTiming;
  best_upcoming: BestDayTiming[];
  advice: string[];
}

// ============================================================================
// HABIT TRACKER TYPES
// ============================================================================

export interface HabitCategory {
  key: string;
  name: string;
  description: string;
  icon: string;
}

export interface Habit {
  id?: string;
  category: string;
  name: string;
  description?: string;
  frequency: 'daily' | 'weekly' | 'lunar_cycle';
  created_at?: string;
}

export interface HabitCompletion {
  habit_id: string;
  date: string;
  completed: boolean;
  notes?: string;
}

// ============================================================================
// RELATIONSHIP TYPES
// ============================================================================

export interface RelationshipEvent {
  date: string;
  event_type: string;
  description: string;
  astrological_reason: string;
}

export interface BestRelationshipDay {
  date: string;
  score: number;
  activity_type: string;
  moon_phase: string;
  venus_status: string;
}

// ============================================================================
// HEALTH CHECK TYPES
// ============================================================================

export interface HealthCheckResponse {
  status: 'ok';
  ephemeris_path: string;
  flatlib_available: boolean;
  redis_status: 'connected' | 'disconnected' | 'disabled' | 'error';
  gemini_status: 'configured' | 'no_api_key' | 'not_installed' | 'disabled';
  cache: Record<string, unknown>;
  features: Record<string, boolean>;
  timestamp: string;
}
