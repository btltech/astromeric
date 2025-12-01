/**
 * Custom hook for reading/forecast management
 * Supports both saved profiles and session-only profiles
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { fetchForecast } from '../api/client';
import type { PredictionData, SavedProfile } from '../types';

export function useReading() {
  const { selectedScope, result, setSelectedScope, setResult, setLoading, setError, profiles, sessionProfile } =
    useStore();

  const getPrediction = useCallback(
    async (profileId: number) => {
      // Find profile: check session profile first (negative ID), then saved profiles
      let profile: SavedProfile | undefined;
      if (sessionProfile && profileId < 0) {
        profile = sessionProfile;
      } else {
        profile = profiles.find((p) => p.id === profileId);
      }

      if (!profile) {
        setError('Profile not found. Please select or create a profile.');
        return null;
      }

      setLoading(true);
      setError('');

      try {
        const payload = {
          name: profile.name,
          date_of_birth: profile.date_of_birth,
          time_of_birth: profile.time_of_birth || undefined,
          location: {
            latitude: profile.latitude || 0,
            longitude: profile.longitude || 0,
            timezone: profile.timezone || 'UTC',
          },
          house_system: profile.house_system || 'Placidus',
        };

        const data = await fetchForecast(payload, selectedScope);
        setResult(data as unknown as PredictionData);
        return data;
      } catch (err) {
        console.error(err);
        const message = err instanceof Error ? err.message : 'Failed to get reading';
        if (message.includes('Failed to fetch')) {
          setError('Connection lost. Please check your network and try again.');
        } else {
          setError(message);
        }
        return null;
      } finally {
        setLoading(false);
      }
    },
    [profiles, sessionProfile, selectedScope, setResult, setLoading, setError]
  );

  return {
    selectedScope,
    result,
    setSelectedScope,
    setResult,
    getPrediction,
  };
}
