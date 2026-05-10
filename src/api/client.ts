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
  place_of_birth?: string;
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

export interface LiveProfileIdentity {
  name: string;
  date_of_birth: string;
  time_of_birth?: string | null;
  place_of_birth?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  house_system?: string | null;
  date?: string | null;
}

export interface LiveChartPlanet {
  name: string;
  sign: string;
  degree: number;
  absolute_degree: number;
  ecliptic_latitude?: number;
  house: number;
  retrograde: boolean;
  dignity?: string | null;
}

export interface LiveChartHouse {
  house: number;
  sign: string;
  degree: number;
}

export interface LiveChartAspect {
  planet_a: string;
  planet_b: string;
  type: string;
  orb: number;
  strength?: number;
}

export interface LiveNatalProfile {
  profile: LiveProfileIdentity;
  chart: {
    metadata: {
      chart_type: string;
      datetime: string;
      house_system: string;
      provider: string;
      birth_time_assumed?: boolean;
      time_confidence?: string;
      data_quality?: string;
      location_assumed?: boolean;
      moon_sign_uncertain?: boolean;
    };
    planets: LiveChartPlanet[];
    houses: LiveChartHouse[];
    aspects: LiveChartAspect[];
  };
}

export interface LiveCompatibilityDimension {
  name: string;
  score: number;
  interpretation: string;
}

export interface LiveCompatibilityResult {
  person_a: LiveProfileIdentity;
  person_b: LiveProfileIdentity;
  overall_score: number;
  summary: string;
  dimensions: LiveCompatibilityDimension[];
  strengths: string[];
  challenges: string[];
  recommendations: string[];
  confidence?: number;
  data_quality_note?: string | null;
}

export interface LiveNumerologyMeaning {
  number: number;
  meaning: string;
  traits?: string[];
  life_purpose?: string;
}

export interface LiveNumerologyCycle {
  year: number;
  cycle_number: number;
  interpretation: string;
  focus_areas: string[];
}

export interface LiveNumerologyArc {
  number: number;
  ages: string;
  meaning: string;
}

export interface LiveKarmicDebt {
  raw: number;
  sources: string[];
  label: string;
  theme: string;
  description: string;
}

export interface LiveNumerologySynthesis {
  summary: string;
  strengths: string[];
  growth_edges: string[];
  current_focus: string;
  affirmation: string;
}

export interface LiveNumerologyProfile {
  profile: LiveProfileIdentity;
  life_path: LiveNumerologyMeaning;
  destiny_number: number;
  destiny_interpretation: string;
  personal_year: LiveNumerologyCycle;
  compatibility_number?: number | null;
  compatibility_interpretation?: string | null;
  lucky_numbers: number[];
  auspicious_days: number[];
  numerology_insights: {
    soul_urge?: string;
    personality?: string;
    personal_month?: string;
    personal_day?: string;
  };
  pinnacles: LiveNumerologyArc[];
  challenges: LiveNumerologyArc[];
  karmic_debts?: LiveKarmicDebt[];
  synthesis?: LiveNumerologySynthesis;
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

function unwrapResponseData<T>(response: ApiResponse<T>, fallbackMessage: string): T {
  if (response.status === 'success' && response.data !== undefined) {
    return response.data;
  }

  throw new Error(response.message || fallbackMessage);
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

function toErrorDetail(value: unknown): string {
  if (typeof value === 'string') {
    return value;
  }

  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    if (typeof record.message === 'string') {
      return record.message;
    }
    if (typeof record.error === 'string') {
      return record.error;
    }

    try {
      return JSON.stringify(value);
    } catch {
      return 'Request failed';
    }
  }

  return 'Request failed';
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const method = (options.method ?? 'GET').toUpperCase();
  const cache = options.cache ?? (method === 'GET' ? 'no-store' : undefined);

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
    cache,
    headers: mergedHeaders,
  });
  if (!resp.ok) {
    let detail = 'Request failed';
    try {
      const body = await resp.json();
      detail = toErrorDetail(body?.detail ?? body?.error ?? body);
    } catch {
      const text = await resp.text();
      detail = text || detail;
    }
    throw new ApiError(resp.status, detail);
  }
  return resp.json() as Promise<T>;
}

function getResolvedLocation(profile: ProfilePayload) {
  return {
    latitude: profile.location?.latitude ?? 0,
    longitude: profile.location?.longitude ?? 0,
    timezone: profile.location?.timezone ?? 'UTC',
  };
}

function toFlatProfilePayload(profile: ProfilePayload) {
  const location = getResolvedLocation(profile);

  return {
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth,
    place_of_birth: profile.place_of_birth,
    latitude: location.latitude,
    longitude: location.longitude,
    timezone: location.timezone,
    house_system: profile.house_system ?? 'Placidus',
  };
}

export async function fetchForecast(
  profile: ProfilePayload,
  scope: 'daily' | 'weekly' | 'monthly' = 'daily'
): Promise<ForecastResponse> {
  const response = await apiFetch<ApiResponse<ForecastResponse>>(`/v2/forecasts/${scope}`, {
    method: 'POST',
    body: JSON.stringify({
      profile: toFlatProfilePayload(profile),
      scope,
    }),
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

export async function fetchNatalProfile(profile: ProfilePayload): Promise<LiveNatalProfile> {
  const location = getResolvedLocation(profile);

  const response = await apiFetch<ApiResponse<LiveNatalProfile>>('/v2/profiles/natal', {
    method: 'POST',
    body: JSON.stringify({
      profile: {
        name: profile.name,
        date_of_birth: profile.date_of_birth,
        time_of_birth: profile.time_of_birth,
        location,
        house_system: profile.house_system ?? 'Placidus',
      },
    }),
  });
  if (response.status === 'success' && response.data) {
    return response.data;
  }
  throw new Error(response.message || 'Failed to fetch natal profile');
}

export async function fetchCompatibility(
  person_a: ProfilePayload,
  person_b: ProfilePayload
): Promise<LiveCompatibilityResult> {
  const response = await apiFetch<ApiResponse<LiveCompatibilityResult>>('/v2/compatibility/romantic', {
    method: 'POST',
    body: JSON.stringify({
      person_a: toFlatProfilePayload(person_a),
      person_b: toFlatProfilePayload(person_b),
    }),
  });
  if (response.status === 'success' && response.data) {
    return response.data;
  }
  throw new Error(response.message || 'Failed to fetch compatibility');
}

export async function fetchNumerologyProfile(profile: ProfilePayload): Promise<LiveNumerologyProfile> {
  const response = await apiFetch<ApiResponse<LiveNumerologyProfile>>('/v2/numerology/profile', {
    method: 'POST',
    body: JSON.stringify({
      profile: toFlatProfilePayload(profile),
    }),
  });

  if (response.status === 'success' && response.data) {
    return response.data;
  }

  throw new Error(response.message || 'Failed to fetch numerology profile');
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
  category?: string;
  difficulty?: string;
  duration_minutes?: number;
  content?: string;
  keywords?: string[];
  related_modules?: string[];
}

export interface LearningModulesResponse {
  modules: LearningModule[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface LearningGlossaryEntry {
  term: string;
  definition: string;
  category: string;
  usage_example: string;
  related_terms: string[];
}

export interface LearningGlossaryResponse {
  entries: LearningGlossaryEntry[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

interface LearningLegacyPageResponse<T> {
  data: T[];
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface RawLearningModule {
  id: string;
  title: string;
  description: string;
  item_count?: number;
  category?: string;
  difficulty?: string;
  duration_minutes?: number;
  content?: string;
  keywords?: string[];
  related_modules?: string[];
}

function normalizeLearningModule(module: RawLearningModule): LearningModule {
  return {
    ...module,
    item_count:
      module.item_count ?? module.keywords?.length ?? module.related_modules?.length ?? 1,
  };
}

export function fetchLearningModules(category?: string, difficulty?: string) {
  const params = new URLSearchParams();
  if (category) {
    params.set('category', category);
  }
  if (difficulty) {
    params.set('difficulty', difficulty);
  }

  const query = params.toString();

  return apiFetch<LearningLegacyPageResponse<RawLearningModule>>(
    `/v2/learning/modules${query ? `?${query}` : ''}`,
    {
    method: 'GET',
    }
  ).then((response) => ({
    modules: response.data.map(normalizeLearningModule),
    total: response.total,
    page: response.page,
    pageSize: response.page_size,
    hasNext: response.has_next,
    hasPrev: response.has_prev,
  }));
}

export function fetchLearningModule(moduleId: string) {
  return apiFetch<ApiResponse<RawLearningModule>>(`/v2/learning/module/${moduleId}`, {
    method: 'GET',
  }).then((response) => unwrapResponseData(response, 'Learning module could not be loaded.'));
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

export function fetchLearningGlossary(search?: string, category?: string) {
  const params = new URLSearchParams();
  if (search) {
    params.set('search', search);
  }
  if (category && category !== 'all') {
    params.set('category', category);
  }

  const query = params.toString();

  return apiFetch<LearningLegacyPageResponse<LearningGlossaryEntry>>(
    `/v2/learning/glossary${query ? `?${query}` : ''}`,
    {
      method: 'GET',
    }
  ).then((response) => ({
    entries: response.data,
    total: response.total,
    page: response.page,
    pageSize: response.page_size,
    hasNext: response.has_next,
    hasPrev: response.has_prev,
  }));
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
  return apiFetch<ApiResponse<MoonPhaseInfo>>('/v2/moon/phase', {
    method: 'GET',
  }).then((response) => {
    if (response.status === 'success' && response.data) {
      return response.data;
    }

    throw new Error(response.message || 'Failed to fetch current moon phase');
  });
}

export function fetchUpcomingMoonEvents(days: number = 30) {
  return apiFetch<ApiResponse<{ events: MoonEvent[]; days_ahead: number }>>(`/v2/moon/upcoming?days=${days}`, {
    method: 'GET',
  }).then((response) => {
    if (response.status === 'success' && response.data) {
      return response.data.events ?? [];
    }
    throw new Error(response.message || 'Failed to fetch upcoming moon events');
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
  return apiFetch<ApiResponse<TimingAdviceResult>>('/v2/timing/advice', {
    method: 'POST',
    body: JSON.stringify(request),
  }).then((response) => {
    if (response.status === 'success' && response.data) {
      return response.data;
    }

    throw new Error(response.message || 'Failed to fetch timing advice');
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
  return apiFetch<ApiResponse<BestDaysResult>>('/v2/timing/best-days', {
    method: 'POST',
    body: JSON.stringify(request),
  }).then((response) => {
    if (response.status === 'success' && response.data) {
      return response.data;
    }

    throw new Error(response.message || 'Failed to fetch best days');
  });
}

export function fetchTimingActivities() {
  return apiFetch<ApiResponse<{ activities: TimingActivity[] }>>('/v2/timing/activities', {
    method: 'GET',
  }).then((response) => {
    if (response.status === 'success' && response.data) {
      return response.data;
    }

    throw new Error(response.message || 'Failed to fetch timing activities');
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
  return apiFetch<ApiResponse<{ success: boolean; message: string; entry: JournalEntry }>>(
    '/v2/journal/entry',
    {
    method: 'POST',
    body: JSON.stringify(request),
    headers: {
      Authorization: `Bearer ${token}`,
    },
    }
  ).then((response) => unwrapResponseData(response, 'Journal entry could not be saved.'));
}

/**
 * Record whether a prediction came true
 * Requires authentication
 */
export function recordOutcome(request: OutcomeRequest, token: string) {
  return apiFetch<ApiResponse<{ success: boolean; message: string; outcome: OutcomeRecord }>>(
    '/v2/journal/outcome',
    {
      method: 'POST',
      body: JSON.stringify(request),
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  ).then((response) => unwrapResponseData(response, 'Outcome could not be recorded.'));
}

/**
 * Get readings for journaling view with pagination
 * Requires authentication
 */
export function fetchJournalReadings(profileId: number, token: string, limit = 20, offset = 0) {
  return apiFetch<ApiResponse<JournalReadingsResponse>>(
    `/v2/journal/readings/${profileId}?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  ).then((response) => unwrapResponseData(response, 'Journal readings could not be loaded.'));
}

/**
 * Get a single reading with full journal and content
 * Requires authentication
 */
export function fetchJournalReading(readingId: number, token: string) {
  return apiFetch<
    ApiResponse<{
      id: number;
      scope: string;
      date: string;
      content: Record<string, unknown>;
      feedback: string | null;
      journal: string;
      created_at: string | null;
    }>
  >(`/v2/journal/reading/${readingId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then((response) => unwrapResponseData(response, 'Journal reading could not be loaded.'));
}

/**
 * Get accuracy statistics for a profile's readings
 * Requires authentication
 */
export function fetchJournalStats(profileId: number, token: string) {
  return apiFetch<ApiResponse<JournalStatsResponse>>(`/v2/journal/stats/${profileId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then((response) => unwrapResponseData(response, 'Journal stats could not be loaded.'));
}

/**
 * Analyze prediction patterns over time
 * Requires authentication
 */
export function fetchJournalPatterns(profileId: number, token: string) {
  return apiFetch<ApiResponse<JournalPatternsResponse>>(`/v2/journal/patterns/${profileId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then((response) => unwrapResponseData(response, 'Journal patterns could not be loaded.'));
}

/**
 * Generate comprehensive accountability report
 * Requires authentication
 */
export function fetchAccountabilityReport(request: AccountabilityReportRequest, token: string) {
  return apiFetch<ApiResponse<AccountabilityReportResponse>>('/v2/journal/report', {
    method: 'POST',
    body: JSON.stringify(request),
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }).then((response) => unwrapResponseData(response, 'Accountability report could not be loaded.'));
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
  return apiFetch<ApiResponse<JournalPromptsResponse>>(`/v2/journal/prompts?${params.toString()}`, {
    method: 'GET',
  }).then((response) => unwrapResponseData(response, 'Journal prompts could not be loaded.'));
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
