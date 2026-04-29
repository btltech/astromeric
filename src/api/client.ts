/**
 * api/client.ts
 * Centralized API client with typed helper functions.
 */
import type { NumerologyProfile } from '../types';
import { getApiBaseUrl } from './config';

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
  summary: string;
  topics: Record<string, number>;
  avoid: string[];
  embrace: string[];
  // Legacy fields for backwards compatibility
  rating?: number;
  highlights?: string[];
  affirmation?: string;
}

export interface ForecastResponse {
  scope: string;
  date: string;
  sections: ForecastSection[];
  overall_score: number;
  profile: ProfilePayload;
  generated_at: string;
  // Legacy fields for backwards compatibility
  theme?: string;
  ratings?: Record<string, number>;
  numerology?: NumerologyProfile;
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

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
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

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface CosmicGuideRequest {
  message: string;
  sun_sign?: string;
  moon_sign?: string;
  rising_sign?: string;
  history?: ChatMessage[];
}

export interface CosmicGuideResponse {
  response: string;
  provider: string;
  model?: string;
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
  const baseUrl = getApiBaseUrl();

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

export async function fetchForecast(
  profile: ProfilePayload,
  scope: 'daily' | 'weekly' | 'monthly' = 'daily'
): Promise<ForecastResponse> {
  const response = await apiFetch<ApiResponse<ForecastResponse>>(`/v2/forecasts/${scope}`, {
    method: 'POST',
    body: JSON.stringify({ ...profile, scope }), // Flatten profile data
  });
  if (response.status === 'success' && response.data) {
    // Transform v2 API response to match frontend expectations
    const data = response.data;
    return {
      ...data,
      sections: data.sections.map((section) => {
        // Build highlights array from summary, avoid, and embrace
        const highlights = [
          section.summary || '',
          ...(section.avoid || []).map((item) => `⚠️ Avoid: ${item}`),
          ...(section.embrace || []).map((item) => `✨ Embrace: ${item}`),
        ].filter(Boolean);

        return {
          ...section,
          highlights,
        };
      }),
    };
  }
  throw new Error(response.message || 'Failed to fetch forecast');
}

export async function fetchNatalProfile(profile: ProfilePayload) {
  const response = await apiFetch<ApiResponse<any>>('/v2/profiles/natal', {
    method: 'POST',
    body: JSON.stringify(profile), // Send flat
  });
  if (response.status === 'success' && response.data) {
    return response.data;
  }
  throw new Error(response.message || 'Failed to fetch natal profile');
}

export async function fetchCompatibility(person_a: ProfilePayload, person_b: ProfilePayload) {
  const response = await apiFetch<ApiResponse<any>>('/v2/compatibility/romantic', {
    method: 'POST',
    body: JSON.stringify({ person_a, person_b }),
  });
  if (response.status === 'success' && response.data) {
    return response.data;
  }
  throw new Error(response.message || 'Failed to fetch compatibility');
}

export async function fetchAiExplanation(
  payload: AiExplainPayload,
  token?: string
): Promise<AiExplainResponse> {
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const response = await apiFetch<ApiResponse<AiExplainResponse>>('/v2/ai/explain', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
  if (response.status === 'success' && response.data) {
    return response.data;
  }
  throw new Error(response.message || 'Failed to get AI explanation');
}

export function sendSectionFeedback(payload: SectionFeedbackPayload, token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return apiFetch<{ status: string }>('/v2/feedback/section', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
}

export function saveReading(payload: SaveReadingPayload, token?: string) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return apiFetch<{ id: number; status?: string }>('/v2/journal/reading', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
}

export function chatWithCosmicGuide(
  message: string,
  sunSign?: string,
  moonSign?: string,
  risingSign?: string,
  history?: ChatMessage[],
  token?: string
) {
  const headers: Record<string, string> = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const payload: CosmicGuideRequest = {
    message,
    sun_sign: sunSign,
    moon_sign: moonSign,
    rising_sign: risingSign,
    history: history?.map((h) => ({ role: h.role, content: h.content })),
  };

  return apiFetch<{ status: string; data: CosmicGuideResponse }>('/v2/cosmic-guide/chat', {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  }).then((res) => res.data);
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

export function fetchDailyFeatures(profile: ProfilePayload) {
  return apiFetch<DailyFeaturesResponse>('/v2/daily/reading', {
    method: 'POST',
    body: JSON.stringify(profile), // Send flat, not {profile: ...}
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
  return apiFetch<TarotCardResponse>('/v2/daily/tarot', {
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
  return apiFetch<YesNoResponse>('/v2/daily/yes-no', {
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

export interface QuickInsightResponse {
  insight: string;
}

export function fetchQuickInsight(topic: string, sunSign?: string) {
  return apiFetch<QuickInsightResponse>('/v2/cosmic-guide/guidance', {
    method: 'POST',
    body: JSON.stringify({ question: topic, sun_sign: sunSign }),
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
  return apiFetch<LearningModulesResponse>('/v2/learning/modules', {
    method: 'GET',
  });
}

export function fetchLearningModule(moduleId: string) {
  return apiFetch<Record<string, unknown>>(`/v2/learning/module/${moduleId}`, {
    method: 'GET',
  });
}

export function fetchCourse(courseId: string) {
  return apiFetch<Record<string, unknown>>(`/v2/learning/course/${courseId}`, {
    method: 'GET',
  });
}

export function fetchLesson(courseId: string, lessonNumber: number) {
  return apiFetch<Record<string, unknown>>(
    `/v2/learning/course/${courseId}/lesson/${lessonNumber}`,
    {
      method: 'GET',
    }
  );
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
  return apiFetch<SearchLearningResponse>('/v2/learning/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

// ========== YEAR-AHEAD FORECAST API ==========

import type { YearAheadForecast, MoonPhaseSummary, MoonPhaseInfo, MoonEvent } from '../types';

export function fetchYearAhead(profile: ProfilePayload, year?: number) {
  return apiFetch<YearAheadForecast>('/v2/year-ahead/forecast', {
    method: 'POST',
    body: JSON.stringify({ ...profile, year }), // Flatten profile data
  });
}

// ========== MOON PHASES API ==========

export function fetchCurrentMoonPhase() {
  return apiFetch<MoonPhaseInfo>('/v2/moon/phase', {
    method: 'GET',
  });
}

export function fetchUpcomingMoonEvents(days: number = 30) {
  return apiFetch<MoonEvent[]>(`/v2/moon/upcoming?days=${days}`, {
    method: 'GET',
  });
}

export function fetchMoonRitual(profile: ProfilePayload) {
  return apiFetch<MoonPhaseSummary>('/v2/moon/ritual', {
    method: 'POST',
    body: JSON.stringify(profile), // Send flat
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
  return apiFetch<TimingAdviceResult>('/v2/timing/advice', {
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
  return apiFetch<BestDaysResult>('/v2/timing/best-days', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export function fetchTimingActivities() {
  return apiFetch<{ activities: TimingActivity[] }>('/v2/timing/activities', {
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
  return apiFetch<{ success: boolean; message: string; entry: JournalEntry }>('/v2/journal/entry', {
    method: 'POST',
    body: JSON.stringify(request),
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Record whether a prediction came true
 * Requires authentication
 */
export function recordOutcome(request: OutcomeRequest, token: string) {
  return apiFetch<{ success: boolean; message: string; outcome: OutcomeRecord }>(
    '/v2/journal/outcome',
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
export function fetchJournalReadings(profileId: number, token: string, limit = 20, offset = 0) {
  return apiFetch<JournalReadingsResponse>(
    `/v2/journal/readings/${profileId}?limit=${limit}&offset=${offset}`,
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
  }>(`/v2/journal/reading/${readingId}`, {
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
  return apiFetch<JournalStatsResponse>(`/v2/journal/stats/${profileId}`, {
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
  return apiFetch<JournalPatternsResponse>(`/v2/journal/patterns/${profileId}`, {
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
export function fetchAccountabilityReport(request: AccountabilityReportRequest, token: string) {
  return apiFetch<AccountabilityReportResponse>('/v2/journal/report', {
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
  return apiFetch<JournalPromptsResponse>(`/v2/journal/prompts?${params.toString()}`, {
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
  return apiFetch<RelationshipTimeline>(`/v2/relationships/timeline${params}`, {
    method: 'GET',
  });
}

/**
 * Analyze relationship timing for a specific date
 */
export function fetchRelationshipTiming(date?: string) {
  const params = date ? `?date=${date}` : '';
  return apiFetch<RelationshipTimingAnalysis>(`/v2/relationships/timing${params}`, {
    method: 'GET',
  });
}

/**
 * Get best relationship days ahead
 */
export function fetchBestRelationshipDays(days_ahead: number = 30, min_score: number = 70) {
  const params = new URLSearchParams({
    days_ahead: days_ahead.toString(),
    min_score: min_score.toString(),
  });
  return apiFetch<{ best_days: BestRelationshipDay[] }>(
    `/v2/relationships/best-days?${params.toString()}`,
    { method: 'GET' }
  );
}

/**
 * Get upcoming relationship events
 */
export function fetchRelationshipEvents(days_ahead: number = 60) {
  return apiFetch<{ events: RelationshipDate[] }>(
    `/v2/relationships/events?days_ahead=${days_ahead}`,
    {
      method: 'GET',
    }
  );
}

/**
 * Get current Venus retrograde status
 */
export function fetchVenusStatus() {
  return apiFetch<VenusRetrogradeStatus>('/v2/relationships/venus-status', {
    method: 'GET',
  });
}

/**
 * Get relationship phases by astrological house
 */
export function fetchRelationshipPhases() {
  return apiFetch<{ phases: RelationshipPhase[] }>('/v2/relationships/phases', {
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
  return apiFetch<{ categories: HabitCategory[] }>('/v2/habits/categories', {
    method: 'GET',
  });
}

/**
 * Get lunar guidance for habits
 */
export function fetchLunarHabitGuidance() {
  return apiFetch<{ phases: Record<string, LunarHabitGuidance> }>('/v2/habits/lunar-guidance', {
    method: 'GET',
  });
}

/**
 * Get guidance for a specific moon phase
 */
export function fetchPhaseGuidance(phase: string) {
  return apiFetch<LunarHabitGuidance>(`/v2/habits/phase/${phase}`, {
    method: 'GET',
  });
}

/**
 * Check habit alignment with current moon phase
 */
export function fetchHabitAlignment(category: string, moon_phase: string) {
  const params = new URLSearchParams({ category, moon_phase });
  return apiFetch<LunarAlignment>(`/v2/habits/alignment?${params.toString()}`, {
    method: 'GET',
  });
}

/**
 * Get habit recommendations based on current moon phase
 */
export function fetchHabitRecommendations(moon_phase: string) {
  return apiFetch<{ recommendations: HabitRecommendation[]; phase_info: LunarHabitGuidance }>(
    `/v2/habits/recommendations?moon_phase=${moon_phase}`,
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
    `/v2/habits/create?moon_phase=${moon_phase}`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    }
  );
}

/**
 * Log habit completion
 */
export function logHabitCompletion(habit_id: number, moon_phase: string, notes?: string) {
  return apiFetch<{ success: boolean; completion: HabitCompletion }>(
    `/v2/habits/log?moon_phase=${moon_phase}`,
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
  return apiFetch<HabitStreak>(`/v2/habits/streak?frequency=${frequency}`, {
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
  return apiFetch<HabitForecast>(`/v2/habits/today?moon_phase=${moon_phase}`, {
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
  return apiFetch<LunarCycleReport>(`/habits/lunar-report?cycle_days=${cycle_days}`, {
    method: 'POST',
    body: JSON.stringify({ habits, completions }),
  });
}

// ========== V2 DAILY FEATURES API ==========

export interface ForecastDay {
  date: string;
  score: number;
  vibe: string;
  icon: string;
  recommendation: string;
}

export interface WeeklyForecastResponse {
  days: ForecastDay[];
}

export async function fetchWeeklyForecast(
  profile: ProfilePayload
): Promise<WeeklyForecastResponse> {
  const result = await apiFetch<ApiResponse<WeeklyForecastResponse>>('/v2/daily/forecast', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
  if (result.status === 'success' && result.data) {
    return result.data;
  }
  throw new Error(result.message || 'Failed to fetch weekly forecast');
}
