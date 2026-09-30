import { describe, expect, it } from 'vitest';

import type { ForecastResponse, LiveNatalProfile } from '../api/client';
import { buildPredictionData } from '../utils/prediction';

const forecast = {
  scope: 'daily',
  date: '2026-09-30',
  overall_score: 5.8,
  generated_at: '2026-09-30T06:44:25Z',
  profile: { name: 'T', date_of_birth: '1990-06-15' },
  tldr: '🌕 Full Moon. Today calls for Air focus.',
  birth_time_assumed: false,
  active_transits: [
    { transit_planet: 'Venus', natal_planet: 'Uranus', aspect: 'sextile', orb: 0.18 },
    { transit_planet: 'Saturn', natal_planet: 'Mars', aspect: 'square', orb: 0.5 },
  ],
  sections: [
    { title: 'Overview', summary: 's', topics: { general: 21.3 }, avoid: [], embrace: [] },
  ],
} as unknown as ForecastResponse;

const natal = {
  chart: {
    metadata: { birth_time_assumed: true, moon_sign_uncertain: true },
    planets: [
      { name: 'Sun', sign: 'Gemini', degree: 24.5, house: 11 },
      { name: 'Moon', sign: 'Pisces', degree: 3, house: 9 },
    ],
    houses: [{ house: 1, sign: 'Libra', degree: 20.1 }],
    aspects: [],
  },
} as unknown as LiveNatalProfile;

describe('buildPredictionData', () => {
  it('shows the server summary, score and transits the page used to drop', () => {
    const data = buildPredictionData(forecast, natal);
    expect(data.summary?.headline).toBe(forecast.tldr);
    expect(data.overall_score).toBe(5.8);
    expect(data.active_transits).toHaveLength(2);
  });

  it('words each transit as a driver, supportive or challenging', () => {
    const [venus, saturn] = buildPredictionData(forecast, natal).summary?.top_factors ?? [];
    expect(venus.aspect).toBe('Venus sextile Uranus');
    expect(venus.impact).toBe('Supportive');
    expect(venus.description).toContain('your natal Uranus');
    expect(venus.description).toContain('orb 0.2°');
    expect(saturn.impact).toBe('Challenging');
  });

  it('takes the signs and element from the birth chart', () => {
    const data = buildPredictionData(forecast, natal);
    expect(data.sign).toBe('Gemini');
    expect(data.element).toBe('Air');
    expect(data.charts?.natal?.houses?.[0]).toMatchObject({ house: 1, sign: 'Libra' });
    expect(data.charts?.natal?.planets.find((p) => p.name === 'Moon')?.sign).toBe('Pisces');
  });

  it('still works when the chart could not be fetched', () => {
    const data = buildPredictionData(forecast, null);
    expect(data.sign).toBeUndefined();
    expect(data.charts).toBeUndefined();
    expect(data.summary?.headline).toBe(forecast.tldr);
  });

  it('flags an estimated birth time from either the forecast or the chart', () => {
    expect(buildPredictionData(forecast, null).birth_time_assumed).toBe(false);
    expect(
      buildPredictionData({ ...forecast, birth_time_assumed: undefined }, natal).birth_time_assumed
    ).toBe(true);
    expect(buildPredictionData(forecast, natal).moon_sign_uncertain).toBe(true);
  });
});
