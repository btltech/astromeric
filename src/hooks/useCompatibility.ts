/**
 * Custom hook for compatibility checks
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { CompatibilityResult } from '../types';

export function useCompatibility() {
  const {
    compareProfileId,
    compatibilityResult,
    setCompareProfileId,
    setCompatibilityResult,
    setLoading,
    setError,
    token,
  } = useStore();

  const fetchCompatibility = useCallback(
    async (profileId1: number, profileId2: number) => {
      setLoading(true);
      setError('');

      try {
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const data = await apiFetch<CompatibilityResult>('/compatibility/combined', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            profile_id_1: profileId1,
            profile_id_2: profileId2,
            relationship_type: 'romantic',
          }),
        });
        setCompatibilityResult(data);
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to calculate compatibility';
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [setCompatibilityResult, setLoading, setError, token]
  );

  return {
    compareProfileId,
    compatibilityResult,
    setCompareProfileId,
    setCompatibilityResult,
    fetchCompatibility,
  };
}
