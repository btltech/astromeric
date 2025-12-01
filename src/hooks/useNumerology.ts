/**
 * Custom hook for numerology profile
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { NumerologyProfile, SavedProfile } from '../types';

export function useNumerology() {
  const { numerologyProfile, setNumerologyProfile, setLoading, setError, token } = useStore();

  // Fetch numerology from profile data (for session-only profiles)
  const fetchNumerologyFromProfile = useCallback(
    async (profile: SavedProfile) => {
      setLoading(true);
      setError('');

      try {
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const data = await apiFetch<NumerologyProfile>('/numerology', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            profile: {
              name: profile.name,
              date_of_birth: profile.date_of_birth,
              time_of_birth: profile.time_of_birth,
              place_of_birth: profile.place_of_birth,
              latitude: profile.latitude,
              longitude: profile.longitude,
              timezone: profile.timezone,
              house_system: profile.house_system,
            },
          }),
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

  // Legacy: Fetch numerology by profile ID (for saved profiles)
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
    fetchNumerologyFromProfile,
  };
}
