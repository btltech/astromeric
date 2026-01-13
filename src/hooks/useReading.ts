/**
 * Custom hook for reading/forecast management
 * Supports both saved profiles and session-only profiles
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { ApiError, fetchForecast, saveReading } from '../api/client';
import type { PredictionData, SavedProfile } from '../types';

export function useReading() {
  const {
    selectedScope,
    result,
    setSelectedScope,
    setResult,
    setLoading,
    setError,
    profiles,
    sessionProfile,
    token,
    allowCloudHistory,
  } = useStore();

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
        const hasCoordinates =
          typeof profile.latitude === 'number' &&
          typeof profile.longitude === 'number' &&
          profile.latitude !== null &&
          profile.longitude !== null;

        const payload = {
          name: profile.name,
          date_of_birth: profile.date_of_birth,
          time_of_birth: profile.time_of_birth || undefined,
          location: hasCoordinates
            ? {
                latitude: profile.latitude as number,
                longitude: profile.longitude as number,
                timezone: profile.timezone || 'UTC',
              }
            : undefined,
          house_system: profile.house_system || 'Placidus',
        };

        const data = await fetchForecast(payload, selectedScope);
        // Persist reading only when the user opted in and the profile is saved (positive ID)
        if (allowCloudHistory && profileId > 0) {
          const date = (data as PredictionData).date || new Date().toISOString();
          saveReading(
            {
              profile_id: profileId,
              scope: selectedScope,
              content: data,
              date,
            },
            token || undefined
          ).catch((err) => {
            console.warn('Cloud history save failed (non-blocking):', err);
          });
        }
        setResult(data as unknown as PredictionData);
        return data;
      } catch (err) {
        console.error('Prediction error:', err);
        if (err instanceof ApiError) {
          setError(err.detail || err.message);
        } else {
          const message = err instanceof Error ? err.message : 'Failed to get reading';
          // Browser fetch failures usually surface as TypeError("Failed to fetch")
          const isNetworkFailure =
            err instanceof TypeError ||
            message.includes('Failed to fetch') ||
            message.includes('NetworkError');

          setError(
            isNetworkFailure ? 'Connection lost. Please check your network and try again.' : message
          );
        }
        throw err; // Re-throw so the calling code knows it failed
      } finally {
        setLoading(false);
      }
    },
    [
      allowCloudHistory,
      profiles,
      sessionProfile,
      selectedScope,
      setResult,
      setLoading,
      setError,
      token,
    ]
  );

  return {
    selectedScope,
    result,
    setSelectedScope,
    setResult,
    getPrediction,
  };
}
