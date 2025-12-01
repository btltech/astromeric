/**
 * Custom hook for numerology profile
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { NumerologyProfile } from '../types';

export function useNumerology() {
  const { numerologyProfile, setNumerologyProfile, setLoading, setError, token } = useStore();

  const fetchNumerologyProfile = useCallback(
    async (profileId: number) => {
      setLoading(true);
      setError('');

      try {
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const data = await apiFetch<NumerologyProfile>(`/numerology/profile/${profileId}`, {
          headers,
        });
        setNumerologyProfile(data);
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to load numerology profile';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [setNumerologyProfile, setLoading, setError, token]
  );

  return {
    numerologyProfile,
    setNumerologyProfile,
    fetchNumerologyProfile,
  };
}
