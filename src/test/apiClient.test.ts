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