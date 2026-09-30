/**
 * Custom hook for reading/forecast management
 * Supports both saved profiles and session-only profiles
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { ApiError, fetchForecast, fetchNatalProfile, saveReading } from '../api/client';
import { buildPredictionData } from '../utils/prediction';
import { toProfilePayload } from '../utils/profilePayload';
import type { SavedProfile } from '../types';

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
    async (profileId: number, profileOverride?: SavedProfile) => {
      // Find profile: check session profile first (negative ID), then saved profiles
      let profile: SavedProfile | undefined = profileOverride;
      if (!profile && sessionProfile && profileId < 0) {
        profile = sessionProfile;
      } else if (!profile) {
        profile = profiles.find((p) => p.id === profileId);
      }

      if (!profile) {
        setError('Profile not found. Please select or create a profile.');
        return null;
      }

      setLoading(true);
      setError('');

      try {
        // Forecasts are worked out for a place, so a profile without one can't get a reading.
        // Nothing is made up: a missing birth time is sent as missing, and the server
        // marks the reading as estimated.
        const payload = toProfilePayload(profile);
        if (!payload.location) {
          setError('Add a birthplace to this profile to get a reading.');
          return null;
        }

        // The forecast has no signs of its own; the birth chart supplies them. If the
        // chart fails the reading still shows, just without the signs.
        const [forecast, natal] = await Promise.all([
          fetchForecast(payload, selectedScope),
          fetchNatalProfile(payload).catch(() => null),
        ]);
        const data = buildPredictionData(forecast, natal);
        // Persist reading only when the user opted in and the profile is saved (positive ID)
        if (allowCloudHistory && profileId > 0) {
          const date = data.date || new Date().toISOString();
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
        setResult(data);
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
