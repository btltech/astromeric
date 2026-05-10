import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SavedProfile } from '../types';

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

const remoteProfile: SavedProfile = {
  id: 42,
  name: 'Railway Profile',
  date_of_birth: '1990-05-15',
  time_of_birth: '09:30',
  place_of_birth: 'Lagos, Nigeria',
  latitude: 6.5244,
  longitude: 3.3792,
  timezone: 'Africa/Lagos',
  house_system: null,
};

describe('useProfiles auth sync hardening', () => {
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

    const { useStore } = await import('../store/useStore');

    act(() => {
      useStore.setState({
        profiles: [],
        selectedProfileId: null,
        sessionProfile: null,
        loading: false,
        error: '',
        token: null,
        user: null,
      });
    });

    apiFetchMock.mockResolvedValue({
      status: 'success',
      data: [remoteProfile],
    });
  });

  it('uses the latest store token when an older fetchProfiles closure runs after login', async () => {
    const { useProfiles } = await import('../hooks/useProfiles');
    const { useStore } = await import('../store/useStore');

    const { result } = renderHook(() => useProfiles());
    const staleFetchProfiles = result.current.fetchProfiles;

    act(() => {
      useStore.getState().setAuth('fresh-token', {
        id: '1',
        email: 'copilot@example.com',
        is_paid: false,
      });
    });

    await waitFor(() => {
      expect(apiFetchMock).toHaveBeenCalledTimes(1);
    });

    apiFetchMock.mockClear();

    await act(async () => {
      await staleFetchProfiles();
    });

    expect(apiFetchMock).toHaveBeenCalledWith(
      '/v2/profiles/',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer fresh-token',
        },
      })
    );
  });

  it('does not refetch profiles when only the selected profile changes', async () => {
    const { useProfiles } = await import('../hooks/useProfiles');
    const { useStore } = await import('../store/useStore');

    act(() => {
      useStore.getState().setAuth('steady-token', {
        id: '2',
        email: 'steady@example.com',
        is_paid: false,
      });
    });

    renderHook(() => useProfiles());

    await waitFor(() => {
      expect(apiFetchMock).toHaveBeenCalledTimes(1);
    });

    act(() => {
      useStore.getState().setSelectedProfileId(remoteProfile.id);
    });

    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(apiFetchMock).toHaveBeenCalledTimes(1);
  });

  it('forces a fresh profile fetch after migration even when an earlier auth-triggered fetch is still in flight', async () => {
    const { useProfiles } = await import('../hooks/useProfiles');
    const { useStore } = await import('../store/useStore');

    let resolveInitialFetch: ((value: { status: string; data: SavedProfile[] }) => void) | null = null;
    let resolveForcedFetch: ((value: { status: string; data: SavedProfile[] }) => void) | null = null;

    apiFetchMock
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveInitialFetch = resolve;
          })
      )
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveForcedFetch = resolve;
          })
      );

    const { result } = renderHook(() => useProfiles());

    act(() => {
      useStore.getState().setAuth('race-token', {
        id: '3',
        email: 'race@example.com',
        is_paid: false,
      });
    });

    await waitFor(() => {
      expect(apiFetchMock).toHaveBeenCalledTimes(1);
    });

    const forcedFetchPromise = result.current.fetchProfiles({ force: true });

    await waitFor(() => {
      expect(apiFetchMock).toHaveBeenCalledTimes(2);
    });

    resolveForcedFetch?.({
      status: 'success',
      data: [remoteProfile],
    });

    await act(async () => {
      await forcedFetchPromise;
    });

    resolveInitialFetch?.({
      status: 'success',
      data: [],
    });

    await act(async () => {
      await Promise.resolve();
    });

    expect(useStore.getState().profiles).toEqual([remoteProfile]);
    expect(useStore.getState().selectedProfileId).toBe(remoteProfile.id);
  });

  it('can suppress the next auth-triggered auto-fetch so migration can own the first refresh', async () => {
    const { useProfiles } = await import('../hooks/useProfiles');
    const { useStore } = await import('../store/useStore');

    const { result } = renderHook(() => useProfiles());

    act(() => {
      result.current.suppressNextAutoFetch();
      useStore.getState().setAuth('suppressed-token', {
        id: '4',
        email: 'suppressed@example.com',
        is_paid: false,
      });
    });

    await act(async () => {
      await Promise.resolve();
    });

    expect(apiFetchMock).not.toHaveBeenCalled();

    await act(async () => {
      await result.current.fetchProfiles({ force: true });
    });

    expect(apiFetchMock).toHaveBeenCalledTimes(1);
    expect(apiFetchMock).toHaveBeenCalledWith(
      '/v2/profiles/',
      expect.objectContaining({
        headers: {
          Authorization: 'Bearer suppressed-token',
        },
      })
    );
  });
});