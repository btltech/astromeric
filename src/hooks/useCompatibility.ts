/**
 * Custom hook for compatibility checks
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { CompatibilityResult, SavedProfile } from '../types';

// Profile payload for compatibility API
interface ProfilePayload {
  name: string;
  date_of_birth: string;
  time_of_birth?: string | null;
  place_of_birth?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  house_system?: string | null;
}

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

  // Legacy: fetch compatibility by profile IDs (for saved profiles)
  const fetchCompatibility = useCallback(
    async (profileId1: number, profileId2: number) => {
      setLoading(true);
      setError('');

      try {
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const data = await apiFetch<CompatibilityResult>('/compatibility', {
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

  // Convert SavedProfile to ProfilePayload
  const toPayload = (profile: SavedProfile): ProfilePayload => ({
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth,
    place_of_birth: profile.place_of_birth,
    latitude: profile.latitude,
    longitude: profile.longitude,
    timezone: profile.timezone,
    house_system: profile.house_system,
  });

  // Fetch compatibility from profile data (for session profiles)
  const fetchCompatibilityFromProfiles = useCallback(
    async (personA: SavedProfile, personB: SavedProfile) => {
      setLoading(true);
      setError('');

      try {
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const data = await apiFetch<CompatibilityResult>('/compatibility', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            person_a: toPayload(personA),
            person_b: toPayload(personB),
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
    fetchCompatibilityFromProfiles,
  };
}
