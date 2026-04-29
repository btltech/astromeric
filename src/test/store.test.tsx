import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';

// ============================================
// useStore Tests
// ============================================
import { useStore } from '../store/useStore';

describe('useStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useStore.setState({
      profiles: [],
      selectedProfileId: null,
      result: null,
      loading: false,
      error: '',
      theme: 'default',
      tonePreference: 50,
      streakCount: 0,
      token: null,
      user: null,
    });
  });

  it('manages profiles state', () => {
    const { result } = renderHook(() => useStore());

    expect(result.current.profiles).toEqual([]);

    act(() => {
      result.current.setProfiles([
        {
          id: 1,
          name: 'Test User',
          date_of_birth: '1990-05-15',
        },
      ]);
    });

    expect(result.current.profiles).toHaveLength(1);
    expect(result.current.profiles[0].name).toBe('Test User');
  });

  it('manages selected profile', () => {
    const { result } = renderHook(() => useStore());

    act(() => {
      result.current.setSelectedProfileId(1);
    });

    expect(result.current.selectedProfileId).toBe(1);
  });

  it('manages loading and error state', () => {
    const { result } = renderHook(() => useStore());

    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe('');

    act(() => {
      result.current.setLoading(true);
      result.current.setError('Test error');
    });

    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBe('Test error');
  });

  it('manages theme preference', () => {
    const { result } = renderHook(() => useStore());

    expect(result.current.theme).toBe('default');

    act(() => {
      result.current.setTheme('midnight');
    });

    expect(result.current.theme).toBe('midnight');
  });

  it('manages tone preference', () => {
    const { result } = renderHook(() => useStore());

    act(() => {
      result.current.setTonePreference(75);
    });

    expect(result.current.tonePreference).toBe(75);
  });

  it('updates streak correctly', () => {
    const { result } = renderHook(() => useStore());

    // First visit should set streak to 1
    act(() => {
      result.current.updateStreak();
    });

    expect(result.current.streakCount).toBe(1);
    expect(result.current.lastVisitDate).toBe(new Date().toISOString().split('T')[0]);
  });

  it('manages auth state', () => {
    const { result } = renderHook(() => useStore());

    expect(result.current.token).toBeNull();
    expect(result.current.user).toBeNull();

    act(() => {
      result.current.setAuth('test-token', {
        id: '1',
        email: 'test@example.com',
        is_paid: false,
      });
    });

    expect(result.current.token).toBe('test-token');
    expect(result.current.user?.email).toBe('test@example.com');
  });

  it('clears auth on logout', () => {
    const { result } = renderHook(() => useStore());

    // Set auth first
    act(() => {
      result.current.setAuth('test-token', {
        id: '1',
        email: 'test@example.com',
        is_paid: false,
      });
    });

    // Then clear
    act(() => {
      result.current.clearAuth();
    });

    expect(result.current.token).toBeNull();
    expect(result.current.user).toBeNull();
  });

  it('manages reading result', () => {
    const { result } = renderHook(() => useStore());

    const mockResult = {
      scope: 'daily',
      sections: [{ title: 'General', content: 'Test content' }],
    };

    act(() => {
      result.current.setResult(mockResult);
    });

    expect(result.current.result).toEqual(mockResult);
  });

  it('manages selected scope', () => {
    const { result } = renderHook(() => useStore());

    expect(result.current.selectedScope).toBe('daily');

    act(() => {
      result.current.setSelectedScope('weekly');
    });

    expect(result.current.selectedScope).toBe('weekly');
  });
});

// ============================================
// Store Persistence Tests
// ============================================

describe('Store Persistence', () => {
  it('persists theme preference', () => {
    const { result } = renderHook(() => useStore());

    act(() => {
      result.current.setTheme('ocean');
    });

    // Create new hook instance to test persistence
    const { result: newResult } = renderHook(() => useStore());
    expect(newResult.current.theme).toBe('ocean');
  });

  it('persists streak data', () => {
    const { result } = renderHook(() => useStore());

    act(() => {
      result.current.updateStreak();
    });

    const { result: newResult } = renderHook(() => useStore());
    expect(newResult.current.streakCount).toBeGreaterThan(0);
  });
});
