import { act, renderHook } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

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

describe('useAnonReadings', () => {
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

  it('refreshes local reading counts after migration clears storage', async () => {
    window.localStorage.setItem(
      'astromeric_anon_readings',
      JSON.stringify([
        {
          id: 'reading-1',
          scope: 'daily',
          date: '2026-05-09',
          content: { summary: 'Local smoke reading' },
          timestamp: 1,
        },
      ])
    );

    const { useAnonReadings } = await import('../hooks/useAnonReadings');
    const { result } = renderHook(() => useAnonReadings());

    expect(result.current.readingCount).toBe(1);

    act(() => {
      result.current.migrateReadings();
      result.current.refreshReadings();
    });

    expect(result.current.readingCount).toBe(0);
    expect(result.current.readings).toEqual([]);
    expect(window.localStorage.getItem('astromeric_anon_readings')).toBeNull();
  });
});