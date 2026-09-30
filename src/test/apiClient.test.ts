import { beforeEach, describe, expect, it, vi } from 'vitest';

const fetchMock = vi.fn();

vi.mock('../api/config', () => ({
  getApiBaseUrl: () => 'https://example.test',
}));

global.fetch = fetchMock;

describe('apiFetch', () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  it('defaults GET requests to no-store cache', async () => {
    const { apiFetch } = await import('../api/client');

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success', data: [] }),
    });

    await apiFetch('/v2/profiles/');

    expect(fetchMock).toHaveBeenCalledWith(
      'https://example.test/v2/profiles/',
      expect.objectContaining({
        cache: 'no-store',
      })
    );
  });

  it('preserves an explicit cache mode when callers provide one', async () => {
    const { apiFetch } = await import('../api/client');

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success', data: [] }),
    });

    await apiFetch('/v2/profiles/', { cache: 'reload' });

    expect(fetchMock).toHaveBeenCalledWith(
      'https://example.test/v2/profiles/',
      expect.objectContaining({
        cache: 'reload',
      })
    );
  });
});

// Responses below are copied from the live API, envelope included, so these
// catch the website reading a shape the server does not send.
describe('tool endpoints read the server envelope', () => {
  beforeEach(() => {
    fetchMock.mockReset();
  });

  const reply = (data: unknown) => ({
    ok: true,
    json: async () => ({ status: 'success', data, error: null, message: 'ok' }),
  });

  it('maps a tarot draw to the card the tarot component shows', async () => {
    const { drawTarotCard } = await import('../api/client');
    fetchMock.mockResolvedValueOnce(
      reply({
        name: 'The Hermit',
        suit: 'Major Arcana',
        number: 9,
        upright: false,
        meaning: 'introspection, solitude, guidance, soul-searching',
        interpretation: "Don't isolate too long. Seek balance.",
      })
    );

    const card = await drawTarotCard();
    expect(card.card).toBe('The Hermit');
    expect(card.reversed).toBe(true);
    expect(card.keywords).toEqual(['introspection', 'solitude', 'guidance', 'soul-searching']);
    expect(card.message).toBe("Don't isolate too long. Seek balance.");
  });

  it('returns the full daily features from the daily reading', async () => {
    const { fetchDailyFeatures } = await import('../api/client');
    fetchMock.mockResolvedValueOnce(
      reply({
        affirmation: 'Every challenge is an opportunity for growth.',
        lucky_numbers: [1, 4],
        features: {
          affirmation: { text: 'Every challenge is an opportunity for growth.' },
          lucky_colors: { primary: 'Crimson', primary_hex: '#DC143C' },
          lucky_planet: { planet: 'Mars' },
          life_path: 1,
          personal_day: 1,
        },
      })
    );

    const features = await fetchDailyFeatures({ name: 'Guest', date_of_birth: '1992-04-12' });
    expect(features.affirmation.text).toBe('Every challenge is an opportunity for growth.');
    expect(features.lucky_colors.primary).toBe('Crimson');
    expect(features.lucky_planet.planet).toBe('Mars');
  });

  it('unwraps the year-ahead forecast', async () => {
    const { fetchYearAhead } = await import('../api/client');
    fetchMock.mockResolvedValueOnce(
      reply({
        year: 2026,
        personal_year: { number: 8, theme: 'Achievement', description: 'Think big.' },
        universal_year: { number: 1, theme: 'New beginnings' },
      })
    );

    const forecast = await fetchYearAhead({ name: 'Guest', date_of_birth: '1992-04-12' }, 2026);
    expect(forecast.personal_year.number).toBe(8);
    expect(forecast.universal_year.number).toBe(1);
  });
});
