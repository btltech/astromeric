import { beforeEach, describe, expect, it, vi } from 'vitest';

import { missingChartDetails, PREVIEW_PROFILE, toProfilePayload } from '../utils/profilePayload';

const fetchMock = vi.fn();

vi.mock('../api/config', () => ({
  getApiBaseUrl: () => 'https://example.test',
}));

global.fetch = fetchMock;

const real = { id: -7, name: 'Ada', date_of_birth: '1990-06-15' };

describe('toProfilePayload', () => {
  it('shows the sample person only when there is no profile', () => {
    const guest = toProfilePayload(null);
    expect(guest.name).toBe(PREVIEW_PROFILE.name);
    expect(guest.time_of_birth).toBe('08:30');
    expect(guest.location?.latitude).toBe(51.5072);
  });

  it('never fills a real profile with the sample person’s time or place', () => {
    const payload = toProfilePayload(real);
    expect(payload).toMatchObject({ name: 'Ada', date_of_birth: '1990-06-15' });
    expect(payload.time_of_birth).toBeUndefined();
    expect(payload.place_of_birth).toBeUndefined();
    expect(payload.location).toBeUndefined();
  });

  it('keeps what the profile does have', () => {
    const payload = toProfilePayload({
      ...real,
      time_of_birth: '14:30',
      place_of_birth: 'Lagos, Nigeria',
      latitude: 6.45,
      longitude: 3.39,
      timezone: 'Africa/Lagos',
    });
    expect(payload.time_of_birth).toBe('14:30');
    expect(payload.location).toEqual({ latitude: 6.45, longitude: 3.39, timezone: 'Africa/Lagos' });
  });

  it('treats a coordinate of 0 as a real place', () => {
    const payload = toProfilePayload({ ...real, latitude: 0, longitude: 0, timezone: 'UTC' });
    expect(payload.location).toEqual({ latitude: 0, longitude: 0, timezone: 'UTC' });
  });
});

describe('missingChartDetails', () => {
  it('names what is missing, and nothing for the guest preview', () => {
    expect(missingChartDetails(null)).toEqual([]);
    expect(missingChartDetails(real)).toEqual(['birth time', 'birthplace']);
    expect(missingChartDetails({ ...real, time_of_birth: '09:00' })).toEqual(['birthplace']);
    expect(
      missingChartDetails({ ...real, time_of_birth: '09:00', latitude: 1, longitude: 2 })
    ).toEqual([]);
  });
});

describe('requests to the server', () => {
  beforeEach(() => fetchMock.mockReset());

  it('leave out a birthplace that is unknown instead of sending 0°, 0° UTC', async () => {
    const { fetchYearAhead } = await import('../api/client');
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'success', data: {} }),
    });

    await fetchYearAhead(toProfilePayload(real));

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.profile.latitude).toBeUndefined();
    expect(body.profile.longitude).toBeUndefined();
    expect(body.profile.timezone).toBeUndefined();
    expect(body.profile.time_of_birth).toBeUndefined();
  });
});
