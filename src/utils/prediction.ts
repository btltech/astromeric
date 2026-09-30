import type { ForecastResponse, LiveNatalProfile } from '../api/client';
import type { PredictionData, TopFactor } from '../types';

const SIGN_ELEMENT: Record<string, string> = {
  Aries: 'Fire',
  Leo: 'Fire',
  Sagittarius: 'Fire',
  Taurus: 'Earth',
  Virgo: 'Earth',
  Capricorn: 'Earth',
  Gemini: 'Air',
  Libra: 'Air',
  Aquarius: 'Air',
  Cancer: 'Water',
  Scorpio: 'Water',
  Pisces: 'Water',
};

const ASPECT_TONE: Record<string, { impact: string; feel: string }> = {
  conjunction: { impact: 'Intense', feel: 'blends with and amplifies' },
  sextile: { impact: 'Supportive', feel: 'opens an easy opportunity with' },
  trine: { impact: 'Supportive', feel: 'flows smoothly with' },
  square: { impact: 'Challenging', feel: 'pushes against' },
  opposition: { impact: 'Challenging', feel: 'pulls opposite' },
};

/** The server's active transits, worded for the "reading drivers" rows. */
function transitFactors(transits: ForecastResponse['active_transits']): TopFactor[] {
  return (transits ?? []).map((t) => {
    const tone = ASPECT_TONE[t.aspect];
    return {
      aspect: `${t.transit_planet} ${t.aspect} ${t.natal_planet}`,
      impact: tone?.impact,
      description: `Transiting ${t.transit_planet} ${
        tone?.feel ?? `is in ${t.aspect} with`
      } your natal ${t.natal_planet} (orb ${t.orb.toFixed(1)}°).`,
    };
  });
}

/**
 * Turns the server's forecast (and, when it arrived, the birth chart) into the
 * shape the reading page renders. The forecast has no signs of its own, so the
 * Sun, Moon and rising come from the chart.
 */
export function buildPredictionData(
  forecast: ForecastResponse,
  natal?: LiveNatalProfile | null
): PredictionData {
  const chart = natal?.chart;
  const sun = chart?.planets.find((p) => p.name === 'Sun');

  return {
    ...(forecast as unknown as PredictionData),
    tldr: forecast.tldr,
    overall_score: forecast.overall_score,
    active_transits: forecast.active_transits,
    birth_time_assumed: forecast.birth_time_assumed ?? chart?.metadata.birth_time_assumed,
    moon_sign_uncertain: chart?.metadata.moon_sign_uncertain,
    summary: {
      headline: forecast.tldr,
      top_factors: transitFactors(forecast.active_transits),
    },
    sign: sun?.sign,
    element: sun ? SIGN_ELEMENT[sun.sign] : undefined,
    charts: chart
      ? {
          natal: {
            planets: chart.planets.map((p) => ({
              name: p.name,
              sign: p.sign,
              degree: p.degree,
              house: p.house,
            })),
            houses: chart.houses.map((h) => ({ house: h.house, sign: h.sign, degree: h.degree })),
          },
        }
      : undefined,
  };
}
