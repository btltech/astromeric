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

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    const text = await resp.text();
    throw new Error(`API error ${resp.status}: ${text}`);
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

export function fetchAiExplanation(payload: AiExplainPayload) {
  return apiFetch<AiExplainResponse>('/ai/explain', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ========== DAILY FEATURES API ==========

export interface DailyFeaturesResponse {
  date: string;
  lucky_number: number;
  lucky_number_meaning: string;
  lucky_color: { name: string; hex: string; meaning: string };
  ruling_planet: { name: string; symbol: string; energy: string; focus: string };
  daily_affirmation: string;
  tarot_energy: { name: string; meaning: string; advice: string };
  manifestation_focus: string;
  cosmic_tip: string;
}

export function fetchDailyFeatures(birthDate: string, sunSign?: string) {
  return apiFetch<DailyFeaturesResponse>('/daily-features', {
    method: 'POST',
    body: JSON.stringify({ birth_date: birthDate, sun_sign: sunSign }),
  });
}

// ========== TAROT API ==========

export interface TarotCardResponse {
  name: string;
  meaning: string;
  advice: string;
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
  answer: 'Yes' | 'No' | 'Maybe';
  confidence: number;
  cosmic_reasoning: string;
  advice: string;
  timing: string;
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
