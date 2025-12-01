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
