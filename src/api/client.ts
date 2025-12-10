/**
 * api/client.ts
 * Centralized API client with typed helper functions.
 */
import type { NumerologyProfile } from '../types';

export interface ProfilePayload {
  name: string;
  date_of_birth: string;
  time_of_birth?: string;
  location?: {
    latitude?: number;
    longitude?: number;
    timezone?: string;
  };
  house_system?: string;
}

export interface ForecastSection {
  title: string;
  rating?: number;
  highlights: string[];
  affirmation?: string;
}

export interface ForecastResponse {
  scope: string;
  date: string;
  sections: ForecastSection[];
  theme: string;
  ratings: Record<string, number>;
  numerology: NumerologyProfile;
}

export interface AiExplainSectionPayload {
  title?: string;
  highlights?: string[];
}

export interface AiExplainPayload {
  scope: string;
  headline?: string;
  theme?: string;
  sections: AiExplainSectionPayload[];
  numerology_summary?: string;
}

export interface AiExplainResponse {
  summary: string;
  provider: string;
}

export interface SectionFeedbackPayload {
  scope: string;
  section: string;
  vote: 'up' | 'down';
  profile_id?: number;
}

export interface SaveReadingPayload {
  profile_id: number;
  scope: string;
  content: unknown;
  date?: string;
}

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(`API error ${status}: ${detail}`);
    this.status = status;
    this.detail = detail;
  }
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';

  // Merge headers without losing defaults when callers pass Authorization, etc.
  const mergedHeaders = new Headers(options.headers || undefined);
  if (!mergedHeaders.has('Content-Type') && options.body !== undefined) {
    mergedHeaders.set('Content-Type', 'application/json');
  }
  if (!mergedHeaders.has('Accept')) {
    mergedHeaders.set('Accept', 'application/json');
  }

  const resp = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers: mergedHeaders,
  });
  if (!resp.ok) {
    let detail = 'Request failed';
    try {
      const body = await resp.json();
      detail = (body && (body.detail || body.error || JSON.stringify(body))) || detail;
    } catch {
      const text = await resp.text();
      detail = text || detail;
    }
    throw new ApiError(resp.status, detail);
  }
  return resp.json() as Promise<T>;
}

export function fetchForecast(
  profile: ProfilePayload,
  scope: 'daily' | 'weekly' | 'monthly' = 'daily'
) {
  return apiFetch<ForecastResponse>('/forecast', {
    method: 'POST',
    body: JSON.stringify({ profile, scope }),
  });
}

export function fetchNatalProfile(profile: ProfilePayload) {
  return apiFetch('/natal-profile', {
    method: 'POST',
    body: JSON.stringify({ profile }),
  });
}

export function fetchCompatibility(person_a: ProfilePayload, person_b: ProfilePayload) {
  return apiFetch('/compatibility', {
    method: 'POST',
    body: JSON.stringify({ person_a, person_b }),
  });
}

export function fetchAiExplanation(payload: AiExplainPayload, token?: string) {
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return apiFetch<AiExplainResponse>('/ai/explain', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
}

export function sendSectionFeedback(payload: SectionFeedbackPayload, token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return apiFetch<{ status: string }>('/feedback/section', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
}

export function saveReading(payload: SaveReadingPayload, token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return apiFetch<{ id: number; status?: string }>('/journal/reading', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
}

// ========== DAILY FEATURES API ==========

export interface DailyFeaturesResponse {
  date: string;
  lucky_numbers: number[];
  lucky_colors: { 
    primary: string; 
    primary_hex: string; 
    accent: string;
    description: string;
  };
  lucky_planet: { 
    planet: string; 
    keywords: string[];
    best_for: string[];
    avoid: string[];
    message: string;
  };
  affirmation: {
    text: string;
    category: string;
    instruction: string;
  };
  tarot: { 
    card: string;
    card_number: number;
    keywords: string[];
    message: string;
    reversed: boolean;
    daily_advice: string;
  };
  manifestation: {
    prompt: string;
    focus: string;
    practice: string;
    visualization: string;
  };
  mood_forecast: {
    mood: string;
    emoji: string;
    score: number;
    description: string;
    tips: string[];
    peak_hours: string;
  };
  retrograde_alerts: Array<{
    planet: string;
    status: string;
    message: string;
    advice: string[];
  }>;
  personal_day: number;
  life_path: number;
}

export function fetchDailyFeatures(birthDate: string, sunSign?: string) {
  return apiFetch<DailyFeaturesResponse>('/daily-features', {
    method: 'POST',
    body: JSON.stringify({ birth_date: birthDate, sun_sign: sunSign }),
  });
}

// ========== TAROT API ==========

export interface TarotCardResponse {
  card: string;
  card_number: number;
  keywords: string[];
  message: string;
  reversed: boolean;
  daily_advice: string;
  drawn_at: string;
}

export function drawTarotCard() {
  return apiFetch<TarotCardResponse>('/tarot/draw', {
    method: 'POST',
  });
}

// ========== ORACLE API ==========

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

export function askOracle(question: string, birthDate?: string) {
  return apiFetch<YesNoResponse>('/oracle/yes-no', {
    method: 'POST',
    body: JSON.stringify({ question, birth_date: birthDate }),
  });
}

// ========== MOOD FORECAST API ==========

export interface MoodForecastResponse {
  date: string;
  overall_mood: string;
  energy_level: string;
  social_vibe: string;
  creative_flow: string;
  focus_areas: string[];
  caution: string;
  best_hours: string;
}

export function fetchMoodForecast(sunSign: string, moonSign?: string) {
  return apiFetch<MoodForecastResponse>('/forecast/mood', {
    method: 'POST',
    body: JSON.stringify({ sun_sign: sunSign, moon_sign: moonSign }),
  });
}

// ========== COSMIC GUIDE CHAT API ==========

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CosmicGuideResponse {
  response: string;
}

export function chatWithCosmicGuide(
  message: string,
  sunSign?: string,
  moonSign?: string,
  risingSign?: string,
  history?: ChatMessage[]
) {
  return apiFetch<CosmicGuideResponse>('/cosmic-guide/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      sun_sign: sunSign,
      moon_sign: moonSign,
      rising_sign: risingSign,
      history,
    }),
  });
}

export interface QuickInsightResponse {
  insight: string;
}

export function fetchQuickInsight(topic: string, sunSign?: string) {
  return apiFetch<QuickInsightResponse>('/cosmic-guide/insight', {
    method: 'POST',
    body: JSON.stringify({ topic, sun_sign: sunSign }),
  });
}

// ========== LEARNING API ==========

export interface LearningModule {
  id: string;
  title: string;
  description: string;
  item_count: number;
}

export interface LearningModulesResponse {
  modules: LearningModule[];
}

export function fetchLearningModules() {
  return apiFetch<LearningModulesResponse>('/learn/modules', {
    method: 'GET',
  });
}

export function fetchLearningModule(moduleId: string) {
  return apiFetch<Record<string, unknown>>(`/learn/module/${moduleId}`, {
    method: 'GET',
  });
}

export function fetchCourse(courseId: string) {
  return apiFetch<Record<string, unknown>>(`/learn/course/${courseId}`, {
    method: 'GET',
  });
}

export function fetchLesson(courseId: string, lessonNumber: number) {
  return apiFetch<Record<string, unknown>>(`/learn/course/${courseId}/lesson/${lessonNumber}`, {
    method: 'GET',
  });
}

export interface SearchResult {
  module: string;
  key: string;
  content: Record<string, unknown>;
}

export interface SearchLearningResponse {
  results: SearchResult[];
}

export function searchLearning(query: string) {
  return apiFetch<SearchLearningResponse>('/learn/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

// ========== YEAR-AHEAD FORECAST API ==========

import type { YearAheadForecast, MoonPhaseSummary, MoonPhaseInfo, MoonEvent } from '../types';

export function fetchYearAhead(profile: ProfilePayload, year?: number) {
  return apiFetch<YearAheadForecast>('/year-ahead', {
    method: 'POST',
    body: JSON.stringify({ profile, year }),
  });
}

// ========== MOON PHASES API ==========

export function fetchCurrentMoonPhase() {
  return apiFetch<MoonPhaseInfo>('/moon/current', {
    method: 'GET',
  });
}

export function fetchUpcomingMoonEvents(days: number = 30) {
  return apiFetch<MoonEvent[]>('/moon/upcoming', {
    method: 'GET',
  });
}

export function fetchMoonRitual(profile: ProfilePayload) {
  return apiFetch<MoonPhaseSummary>('/moon/ritual', {
    method: 'POST',
    body: JSON.stringify({ profile }),
  });
}

// ========== TIMING ADVISOR API ==========

import type { TimingAdviceResult, TimingActivity, BestDaysResult } from '../types';

export interface TimingAdviceRequest {
  activity: string;
  latitude: number;
  longitude: number;
  tz?: string;
  profile?: ProfilePayload;
}

export function fetchTimingAdvice(request: TimingAdviceRequest) {
  return apiFetch<TimingAdviceResult>('/timing/advice', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export interface BestDaysRequest {
  activity: string;
  days_ahead: number;
  latitude: number;
  longitude: number;
  tz?: string;
  profile?: ProfilePayload;
}

export function fetchBestDays(request: BestDaysRequest) {
  return apiFetch<BestDaysResult>('/timing/best-days', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export function fetchTimingActivities() {
  return apiFetch<{ activities: TimingActivity[] }>('/timing/activities', {
    method: 'GET',
  });
}

// ========== JOURNAL & ACCOUNTABILITY API ==========

import type {
  JournalReadingsResponse,
  JournalStatsResponse,
  JournalPatternsResponse,
  JournalPromptsResponse,
  AccountabilityReportResponse,
  JournalEntry,
  OutcomeRecord,
} from '../types';

export interface JournalEntryRequest {
  reading_id: number;
  entry: string;
}

export interface OutcomeRequest {
  reading_id: number;
  outcome: 'yes' | 'no' | 'partial' | 'neutral';
  notes?: string;
}

export interface AccountabilityReportRequest {
  profile_id: number;
  period: 'week' | 'month' | 'year';
}

/**
 * Add or update a journal entry for a reading
 * Requires authentication
 */
export function addJournalEntry(request: JournalEntryRequest, token: string) {
  return apiFetch<{ success: boolean; message: string; entry: JournalEntry }>(
    '/journal/entry',
    {
      method: 'POST',
      body: JSON.stringify(request),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

/**
 * Record whether a prediction came true
 * Requires authentication
 */
export function recordOutcome(request: OutcomeRequest, token: string) {
  return apiFetch<{ success: boolean; message: string; outcome: OutcomeRecord }>(
    '/journal/outcome',
    {
      method: 'POST',
      body: JSON.stringify(request),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

/**
 * Get readings for journaling view with pagination
 * Requires authentication
 */
export function fetchJournalReadings(
  profileId: number,
  token: string,
  limit = 20,
  offset = 0
) {
  return apiFetch<JournalReadingsResponse>(
    `/journal/readings/${profileId}?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

/**
 * Get a single reading with full journal and content
 * Requires authentication
 */
export function fetchJournalReading(readingId: number, token: string) {
  return apiFetch<{
    id: number;
    scope: string;
    date: string;
    content: Record<string, unknown>;
    feedback: string | null;
    journal: string;
    created_at: string | null;
  }>(`/journal/reading/${readingId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Get accuracy statistics for a profile's readings
 * Requires authentication
 */
export function fetchJournalStats(profileId: number, token: string) {
  return apiFetch<JournalStatsResponse>(`/journal/stats/${profileId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Analyze prediction patterns over time
 * Requires authentication
 */
export function fetchJournalPatterns(profileId: number, token: string) {
  return apiFetch<JournalPatternsResponse>(`/journal/patterns/${profileId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Generate comprehensive accountability report
 * Requires authentication
 */
export function fetchAccountabilityReport(
  request: AccountabilityReportRequest,
  token: string
) {
  return apiFetch<AccountabilityReportResponse>('/journal/report', {
    method: 'POST',
    body: JSON.stringify(request),
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Get journal prompts for reflection
 * No authentication required
 */
export function fetchJournalPrompts(
  scope: 'daily' | 'weekly' | 'monthly' = 'daily',
  themes?: string[]
) {
  const params = new URLSearchParams({ scope });
  if (themes && themes.length > 0) {
    params.set('themes', themes.join(','));
  }
  return apiFetch<JournalPromptsResponse>(`/journal/prompts?${params.toString()}`, {
    method: 'GET',
  });
}

// ========== RELATIONSHIP TIMELINE API ==========

import type {
  RelationshipTimeline,
  RelationshipTimingAnalysis,
  BestRelationshipDay,
  RelationshipDate,
  VenusRetrogradeStatus,
  RelationshipPhase,
} from '../types';

/**
 * Get complete relationship timeline for a year
 */
export function fetchRelationshipTimeline(year?: number) {
  const params = year ? `?year=${year}` : '';
  return apiFetch<RelationshipTimeline>(`/relationship/timeline${params}`, {
    method: 'GET',
  });
}

/**
 * Analyze relationship timing for a specific date
 */
export function fetchRelationshipTiming(date?: string) {
  const params = date ? `?date=${date}` : '';
  return apiFetch<RelationshipTimingAnalysis>(`/relationship/timing${params}`, {
    method: 'GET',
  });
}

/**
 * Get best relationship days ahead
 */
export function fetchBestRelationshipDays(
  days_ahead: number = 30,
  min_score: number = 70
) {
  const params = new URLSearchParams({
    days_ahead: days_ahead.toString(),
    min_score: min_score.toString(),
  });
  return apiFetch<{ best_days: BestRelationshipDay[] }>(
    `/relationship/best-days?${params.toString()}`,
    { method: 'GET' }
  );
}

/**
 * Get upcoming relationship events
 */
export function fetchRelationshipEvents(days_ahead: number = 60) {
  return apiFetch<{ events: RelationshipDate[] }>(
    `/relationship/events?days_ahead=${days_ahead}`,
    { method: 'GET' }
  );
}

/**
 * Get current Venus retrograde status
 */
export function fetchVenusStatus() {
  return apiFetch<VenusRetrogradeStatus>('/relationship/venus-status', {
    method: 'GET',
  });
}

/**
 * Get relationship phases by astrological house
 */
export function fetchRelationshipPhases() {
  return apiFetch<{ phases: RelationshipPhase[] }>('/relationship/phases', {
    method: 'GET',
  });
}

// ========== HABIT TRACKER API ==========

import type {
  HabitCategory,
  LunarHabitGuidance,
  LunarAlignment,
  HabitRecommendation,
  Habit,
  HabitCompletion,
  HabitStreak,
  HabitForecast,
  LunarCycleReport,
} from '../types';

/**
 * Get all habit categories
 */
export function fetchHabitCategories() {
  return apiFetch<{ categories: HabitCategory[] }>('/habits/categories', {
    method: 'GET',
  });
}

/**
 * Get lunar guidance for habits
 */
export function fetchLunarHabitGuidance() {
  return apiFetch<{ phases: Record<string, LunarHabitGuidance> }>(
    '/habits/lunar-guidance',
    { method: 'GET' }
  );
}

/**
 * Get guidance for a specific moon phase
 */
export function fetchPhaseGuidance(phase: string) {
  return apiFetch<LunarHabitGuidance>(`/habits/phase/${phase}`, {
    method: 'GET',
  });
}

/**
 * Check habit alignment with current moon phase
 */
export function fetchHabitAlignment(category: string, moon_phase: string) {
  const params = new URLSearchParams({ category, moon_phase });
  return apiFetch<LunarAlignment>(`/habits/alignment?${params.toString()}`, {
    method: 'GET',
  });
}

/**
 * Get habit recommendations based on current moon phase
 */
export function fetchHabitRecommendations(moon_phase: string) {
  return apiFetch<{ recommendations: HabitRecommendation[]; phase_info: LunarHabitGuidance }>(
    `/habits/recommendations?moon_phase=${moon_phase}`,
    { method: 'GET' }
  );
}

export interface CreateHabitRequest {
  name: string;
  category: string;
  frequency?: 'daily' | 'weekly' | 'lunar_cycle';
  target_count?: number;
  description?: string;
}

/**
 * Create a new habit
 */
export function createHabit(request: CreateHabitRequest, moon_phase: string) {
  return apiFetch<{ success: boolean; habit: Habit }>(
    `/habits/create?moon_phase=${moon_phase}`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    }
  );
}

/**
 * Log habit completion
 */
export function logHabitCompletion(
  habit_id: number,
  moon_phase: string,
  notes?: string
) {
  return apiFetch<{ success: boolean; completion: HabitCompletion }>(
    `/habits/log?moon_phase=${moon_phase}`,
    {
      method: 'POST',
      body: JSON.stringify({ habit_id, notes }),
    }
  );
}

/**
 * Calculate habit streak
 */
export function fetchHabitStreak(
  completions: Array<{ date: string }>,
  frequency: 'daily' | 'weekly' | 'lunar_cycle' = 'daily'
) {
  return apiFetch<HabitStreak>(`/habits/streak?frequency=${frequency}`, {
    method: 'POST',
    body: JSON.stringify({ completions }),
  });
}

/**
 * Get today's habit forecast
 */
export function fetchTodayHabitForecast(
  habits: Habit[],
  moon_phase: string,
  completions_today?: number[]
) {
  return apiFetch<HabitForecast>(`/habits/today?moon_phase=${moon_phase}`, {
    method: 'POST',
    body: JSON.stringify({ habits, completions_today }),
  });
}

/**
 * Get lunar cycle report
 */
export function fetchLunarCycleReport(
  habits: Habit[],
  completions: HabitCompletion[],
  cycle_days: number = 29
) {
  return apiFetch<LunarCycleReport>(
    `/habits/lunar-report?cycle_days=${cycle_days}`,
    {
      method: 'POST',
      body: JSON.stringify({ habits, completions }),
    }
  );
}
