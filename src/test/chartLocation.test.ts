import { beforeEach, describe, expect, it, vi } from 'vitest';

const fetchMock = vi.fn();

vi.mock('../api/config', () => ({
  getApiBaseUrl: () => 'https://example.test',
}));

global.fetch = fetchMock;

const ok = (data: unknown) => ({ ok: true, json: async () => ({ status: 'success', data }) });

describe('natal chart birthplace', () => {
  beforeEach(() => fetchMock.mockReset());

  it('sends the birthplace at the top level, where the server reads it', async () => {
    const { fetchNatalProfile } = await import('../api/client');
    fetchMock.mockResolvedValueOnce(ok({ chart: {} }));

    await fetchNatalProfile({
      name: 'T',
      date_of_birth: '1990-06-15',
      time_of_birth: '14:30:00',
      location: { latitude: 6.45, longitude: 3.39, timezone: 'Africa/Lagos' },
    });

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.profile).toMatchObject({
      latitude: 6.45,
      longitude: 3.39,
      timezone: 'Africa/Lagos',
    });
    expect(body.profile.location).toBeUndefined();
  });

  it('leaves the place out when it is unknown, instead of sending 0°, 0°', async () => {
    const { fetchNatalProfile } = await import('../api/client');
    fetchMock.mockResolvedValueOnce(ok({ chart: {} }));

    await fetchNatalProfile({ name: 'T', date_of_birth: '1990-06-15' });

    const body = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(body.profile.latitude).toBeUndefined();
    expect(body.profile.timezone).toBeUndefined();
  });
});

describe('timezone repair', () => {
  it('only touches profiles with coordinates and a UTC or guessed zone', async () => {
    const { needsTimezoneRepair } = await import('../utils/timezoneRepair');
    const base = {
      id: -1,
      name: 'T',
      date_of_birth: '1990-06-15',
      latitude: 6.45,
      longitude: 3.39,
    };
    expect(needsTimezoneRepair({ ...base, timezone: 'UTC' })).toBe(true);
    expect(needsTimezoneRepair({ ...base, timezone: 'Etc/GMT+1' })).toBe(true);
    expect(needsTimezoneRepair({ ...base, timezone: 'Africa/Lagos' })).toBe(false);
    expect(needsTimezoneRepair({ ...base, latitude: null, timezone: 'UTC' })).toBe(false);
  });

  it('saves the looked-up zone for local profiles', async () => {
    const { useStore } = await import('../store/useStore');
    const { repairSavedTimezones } = await import('../utils/timezoneRepair');
    useStore.setState({
      profiles: [
        {
          id: -1,
          name: 'Local',
          date_of_birth: '1990-06-15',
          latitude: 6.45,
          longitude: 3.39,
          timezone: 'UTC',
        },
        {
          id: 5,
          name: 'Account',
          date_of_birth: '1990-06-15',
          latitude: 6.45,
          longitude: 3.39,
          timezone: 'UTC',
        },
      ],
      sessionProfile: null,
    });
    fetchMock.mockReset();
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ timezone: 'Africa/Lagos', estimated: false }),
    });

    await repairSavedTimezones();

    const [local, account] = useStore.getState().profiles;
    expect(local.timezone).toBe('Africa/Lagos');
    expect(account.timezone).toBe('UTC');
    expect(fetchMock).toHaveBeenCalledWith(
      'https://example.test/v2/geocode/timezone?lat=6.45&lon=3.39'
    );
  });
});
