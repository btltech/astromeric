import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const apiFetchMock = vi.fn();

function createStorageMock() {
  const storage = new Map<string, string>();

  return {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => {
      storage.set(key, value);
    },
    removeItem: (key: string) => {
      storage.delete(key);
    },
    clear: () => {
      storage.clear();
    },
  };
}

vi.mock('../api/client', () => ({
  apiFetch: (...args: Parameters<typeof apiFetchMock>) => apiFetchMock(...args),
}));

describe('useMigrateReadings', () => {
  beforeEach(async () => {
    vi.resetModules();
    vi.clearAllMocks();

    Object.defineProperty(window, 'localStorage', {
      value: createStorageMock(),
      configurable: true,
    });

    Object.defineProperty(window, 'sessionStorage', {
      value: createStorageMock(),
      configurable: true,
    });

    window.localStorage.setItem(
      'astromeric_anon_readings',
      JSON.stringify([
        {
          id: 'reading-1',
          scope: 'daily',
          date: '2026-05-09',
          profile: {
            name: 'Avery Postfix',
            date_of_birth: '1991-06-16',
            time_of_birth: '08:45',
            timezone: 'Africa/Lagos',
          },
          content: {
            summary: 'Local smoke reading',
          },
          timestamp: 1,
        },
      ])
    );

    const { useStore } = await import('../store/useStore');

    act(() => {
      useStore.setState({
        profiles: [
          {
            id: -777,
            name: 'Avery Postfix',
            date_of_birth: '1991-06-16',
            time_of_birth: '08:45',
            place_of_birth: 'Abuja, Nigeria',
            latitude: 9.0765,
            longitude: 7.3986,
            timezone: 'Africa/Lagos',
            house_system: null,
          },
          {
            id: -778,
            name: 'Jordan Mirror',
            date_of_birth: '1992-03-04',
            time_of_birth: null,
            place_of_birth: 'Lagos, Nigeria',
            latitude: 6.5244,
            longitude: 3.3792,
            timezone: 'Africa/Lagos',
            house_system: null,
          },
        ],
        selectedProfileId: -777,
        compareProfileId: -778,
        sessionProfile: null,
        loading: false,
        error: '',
        token: 'migration-token',
        user: {
          id: '1',
          email: 'migration@example.com',
          is_paid: false,
        },
      });
    });

    apiFetchMock.mockResolvedValue({
      status: 'success',
      data: {
        migrated_profile_count: 2,
        migrated_reading_count: 1,
        skipped_reading_count: 0,
        profile_id_map: {
          '-777': 42,
          '-778': 43,
        },
      },
    });
  });

  it('promotes migrated local profile selections to backend ids', async () => {
    const { useMigrateReadings } = await import('../hooks/useMigrateReadings');
    const { useStore } = await import('../store/useStore');
    const { result } = renderHook(() => useMigrateReadings());

    await act(async () => {
      await expect(result.current.migrateReadings()).resolves.toEqual({
        success: true,
        migratedProfileCount: 2,
        migratedReadingCount: 1,
        skippedReadingCount: 0,
      });
    });

    expect(apiFetchMock).toHaveBeenCalledWith(
      '/v2/auth/migrate-local-data',
      expect.objectContaining({
        method: 'POST',
        headers: {
          Authorization: 'Bearer migration-token',
        },
      })
    );

    expect(useStore.getState().profiles).toEqual([
      expect.objectContaining({
        id: 42,
        name: 'Avery Postfix',
      }),
      expect.objectContaining({
        id: 43,
        name: 'Jordan Mirror',
      }),
    ]);
    expect(useStore.getState().selectedProfileId).toBe(42);
    expect(useStore.getState().compareProfileId).toBe(43);
    expect(window.localStorage.getItem('astromeric_anon_readings')).toBeNull();
  });

  it('promotes the active local fallback profile when explicit selection is null', async () => {
    const { useMigrateReadings } = await import('../hooks/useMigrateReadings');
    const { useStore } = await import('../store/useStore');

    act(() => {
      useStore.setState({
        profiles: [
          {
            id: -777,
            name: 'Avery Postfix',
            date_of_birth: '1991-06-16',
            time_of_birth: '08:45',
            place_of_birth: 'Abuja, Nigeria',
            latitude: 9.0765,
            longitude: 7.3986,
            timezone: 'Africa/Lagos',
            house_system: null,
          },
        ],
        selectedProfileId: null,
        compareProfileId: null,
      });
    });

    apiFetchMock.mockResolvedValueOnce({
      status: 'success',
      data: {
        migrated_profile_count: 1,
        migrated_reading_count: 1,
        skipped_reading_count: 0,
        profile_id_map: {
          '-777': 42,
        },
      },
    });

    const { result } = renderHook(() => useMigrateReadings());

    await act(async () => {
      await result.current.migrateReadings();
    });

    expect(useStore.getState().profiles).toEqual([
      expect.objectContaining({
        id: 42,
        name: 'Avery Postfix',
      }),
    ]);
    expect(useStore.getState().selectedProfileId).toBe(42);
  });
});