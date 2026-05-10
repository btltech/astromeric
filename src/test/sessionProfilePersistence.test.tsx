import { renderHook, act } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { SavedProfile } from '../types';

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
  };
}

const sessionProfileFixture: SavedProfile = {
  id: -101,
  name: 'Session User',
  date_of_birth: '1990-05-15',
  time_of_birth: '14:30',
  place_of_birth: 'New York, United States',
  latitude: 40.7128,
  longitude: -74.006,
  timezone: 'America/New_York',
  house_system: null,
};

describe('session profile persistence', () => {
  beforeEach(() => {
    vi.resetModules();

    Object.defineProperty(window, 'localStorage', {
      value: createStorageMock(),
      configurable: true,
    });

    Object.defineProperty(window, 'sessionStorage', {
      value: createStorageMock(),
      configurable: true,
    });
  });

  it('rehydrates the session profile from sessionStorage on store init', async () => {
    window.sessionStorage.setItem('astro-session-profile', JSON.stringify(sessionProfileFixture));

    const { useStore } = await import('../store/useStore');

    expect(useStore.getState().sessionProfile).toEqual(sessionProfileFixture);
  });

  it('keeps session profile updates synced to sessionStorage', async () => {
    const { useStore } = await import('../store/useStore');

    act(() => {
      useStore.getState().setSessionProfile(sessionProfileFixture);
    });

    expect(JSON.parse(window.sessionStorage.getItem('astro-session-profile') || 'null')).toEqual(
      sessionProfileFixture
    );

    act(() => {
      useStore.getState().setSessionProfile(null);
    });

    expect(window.sessionStorage.getItem('astro-session-profile')).toBeNull();
  });

  it('clears the session profile when selecting any persisted profile', async () => {
    const { useStore } = await import('../store/useStore');
    const { useProfiles } = await import('../hooks/useProfiles');

    act(() => {
      useStore.getState().setSessionProfile(sessionProfileFixture);
      useStore.getState().setProfiles([
        {
          id: -202,
          name: 'Saved Local Profile',
          date_of_birth: '1988-08-08',
          time_of_birth: null,
          place_of_birth: 'Lagos, Nigeria',
          latitude: 6.5244,
          longitude: 3.3792,
          timezone: 'Africa/Lagos',
          house_system: null,
        },
      ]);
    });

    const { result } = renderHook(() => useProfiles());

    act(() => {
      result.current.setSelectedProfileId(-202);
    });

    expect(useStore.getState().sessionProfile).toBeNull();
    expect(useStore.getState().selectedProfileId).toBe(-202);
    expect(window.sessionStorage.getItem('astro-session-profile')).toBeNull();
  });

  it('keeps the session profile active when logging out of Railway', async () => {
    const { useStore } = await import('../store/useStore');

    act(() => {
      useStore.getState().setSessionProfile(sessionProfileFixture);
      useStore.getState().setProfiles([
        {
          id: -202,
          name: 'Saved Local Profile',
          date_of_birth: '1988-08-08',
          time_of_birth: null,
          place_of_birth: 'Lagos, Nigeria',
          latitude: 6.5244,
          longitude: 3.3792,
          timezone: 'Africa/Lagos',
          house_system: null,
        },
      ]);
      useStore.getState().setSelectedProfileId(null);
      useStore.getState().setAuth('token', {
        id: 1,
        email: 'copilot@example.com',
      });
      useStore.getState().logout();
    });

    expect(useStore.getState().token).toBeNull();
    expect(useStore.getState().sessionProfile).toEqual(sessionProfileFixture);
    expect(useStore.getState().selectedProfileId).toBeNull();
    expect(JSON.parse(window.sessionStorage.getItem('astro-session-profile') || 'null')).toEqual(
      sessionProfileFixture
    );
  });

  it('derives one shared active profile contract across fallback, selected, session, and guest states', async () => {
    const { useStore } = await import('../store/useStore');
    const { useActiveProfile } = await import('../hooks/useActiveProfile');

    act(() => {
      useStore.getState().setProfiles([
        {
          id: -202,
          name: 'Saved Local Profile',
          date_of_birth: '1988-08-08',
          time_of_birth: null,
          place_of_birth: 'Lagos, Nigeria',
          latitude: 6.5244,
          longitude: 3.3792,
          timezone: 'Africa/Lagos',
          house_system: null,
        },
        {
          id: 55,
          name: 'Railway Profile',
          date_of_birth: '1992-02-02',
          time_of_birth: '06:15',
          place_of_birth: 'London, UK',
          latitude: 51.5072,
          longitude: -0.1276,
          timezone: 'Europe/London',
          house_system: null,
        },
      ]);
      useStore.getState().setSelectedProfileId(null);
      useStore.getState().setSessionProfile(null);
    });

    const { result } = renderHook(() => useActiveProfile());

    expect(result.current.activeProfile?.id).toBe(-202);
    expect(result.current.activeProfileSource).toBe('local');
    expect(result.current.activeProfileSourceLabel).toBe('Saved on this device');

    act(() => {
      useStore.getState().setSelectedProfileId(55);
    });

    expect(result.current.activeProfile?.id).toBe(55);
    expect(result.current.activeProfileSource).toBe('railway');
    expect(result.current.activeProfileSourceLabel).toBe('Railway profile');

    act(() => {
      useStore.getState().setSessionProfile(sessionProfileFixture);
    });

    expect(result.current.activeProfile?.id).toBe(sessionProfileFixture.id);
    expect(result.current.activeProfileSource).toBe('session');
    expect(result.current.activeProfileSourceLabel).toBe('Browser session');

    act(() => {
      useStore.getState().setSessionProfile(null);
      useStore.getState().setProfiles([]);
      useStore.getState().setSelectedProfileId(null);
    });

    expect(result.current.activeProfile).toBeNull();
    expect(result.current.activeProfileSource).toBe('guest');
    expect(result.current.activeProfileSourceLabel).toBe('Guest defaults');
  });
});