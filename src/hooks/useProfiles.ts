/**
 * Custom hook for profile management
 * Supports both saved profiles (opt-in) and session-only profiles (browser-session default)
 */
import { useCallback, useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { NewProfileForm, SavedProfile } from '../types';
import { toast } from '../components/Toast';
import {
  getActiveProfileSource,
  getActiveProfileSourceLabel,
  resolveActiveProfile,
} from './useActiveProfile';

// API response wrapper type
interface ApiResponse<T> {
  status: 'success' | 'error';
  data: T;
  error?: string;
  message?: string;
}

export function useProfiles() {
  const {
    profiles,
    selectedProfileId,
    setProfiles,
    setSelectedProfileId,
    addProfile,
    sessionProfile,
    setSessionProfile,
    setLoading,
    setError,
    token,
  } = useStore();

  const inflightFetchRef = useRef<Promise<SavedProfile[]> | null>(null);
  const latestFetchIdRef = useRef(0);
  const suppressNextAutoFetchRef = useRef(false);

  const syncProfilesFromBackend = useCallback((profileList: SavedProfile[]) => {
    const state = useStore.getState();
    const localProfiles = state.profiles.filter((profile) => profile.id < 0);
    const mergedProfiles = [...localProfiles, ...profileList];

    state.setProfiles(mergedProfiles);

    if (state.sessionProfile) {
      return mergedProfiles;
    }

    const hasSelectedProfile =
      typeof state.selectedProfileId === 'number' &&
      mergedProfiles.some((profile) => profile.id === state.selectedProfileId);
    const nextSelectedProfileId = hasSelectedProfile ? state.selectedProfileId : mergedProfiles[0]?.id ?? null;

    if (nextSelectedProfileId !== state.selectedProfileId) {
      state.setSelectedProfileId(nextSelectedProfileId);
    }

    return mergedProfiles;
  }, []);

  const fetchProfiles = useCallback(async ({ force = false }: { force?: boolean } = {}) => {
    if (!force && inflightFetchRef.current) {
      return inflightFetchRef.current;
    }

    const fetchId = ++latestFetchIdRef.current;

    const request = (async () => {
      const currentToken = useStore.getState().token;
      if (!currentToken) {
        return useStore.getState().profiles.filter((profile) => profile.id < 0);
      }

      const res = await apiFetch<ApiResponse<SavedProfile[]>>('/v2/profiles/', {
        headers: {
          Authorization: `Bearer ${currentToken}`,
        },
      });

      if (fetchId !== latestFetchIdRef.current) {
        return useStore.getState().profiles;
      }

      return syncProfilesFromBackend(res.data || []);
    })();

    inflightFetchRef.current = request;

    try {
      return await request;
    } finally {
      if (inflightFetchRef.current === request) {
        inflightFetchRef.current = null;
      }
    }
  }, [syncProfilesFromBackend]);

  // Auto-fetch saved profiles from backend when token is available
  useEffect(() => {
    if (!token) return;

    if (suppressNextAutoFetchRef.current) {
      suppressNextAutoFetchRef.current = false;
      return;
    }

    fetchProfiles()
      .catch((err) => console.error('Failed to auto-fetch profiles:', err));
  }, [fetchProfiles, token]);

  const suppressNextAutoFetch = useCallback(() => {
    suppressNextAutoFetchRef.current = true;
    latestFetchIdRef.current += 1;
    inflightFetchRef.current = null;
  }, []);

  const clearAutoFetchSuppression = useCallback(() => {
    suppressNextAutoFetchRef.current = false;
  }, []);

  // Get the active profile (session or saved)
  const selectedProfile = resolveActiveProfile(profiles, selectedProfileId, sessionProfile);
  const activeProfileSource = getActiveProfileSource(selectedProfile, sessionProfile);

  const createProfile = useCallback(
    async (formData: NewProfileForm) => {
      setLoading(true);
      setError('');
      try {
        // Create a session-only profile (never saved to backend)
        const sessionOnlyProfile: SavedProfile = {
          id: -Date.now(), // Negative ID = session-only
          name: formData.name,
          date_of_birth: formData.date_of_birth,
          time_of_birth: formData.time_of_birth || null,
          place_of_birth: formData.place_of_birth || null,
          latitude: formData.latitude || null,
          longitude: formData.longitude || null,
          timezone: formData.timezone || null,
          house_system: formData.house_system || null,
        };

        if (formData.saveProfile && !token) {
          addProfile(sessionOnlyProfile);
          setSelectedProfileId(sessionOnlyProfile.id);
          setSessionProfile(null);
          toast.success('Profile saved on this device');
          return sessionOnlyProfile;
        }

        // If user opts in to save, also store in backend
        if (formData.saveProfile) {
          const headers: Record<string, string> = {};
          if (token) headers['Authorization'] = `Bearer ${token}`;

          // Use trailing slash to avoid 307 redirect which loses auth headers
          const res = await apiFetch<ApiResponse<SavedProfile>>('/v2/profiles/', {
            method: 'POST',
            headers,
            body: JSON.stringify({
              name: formData.name,
              date_of_birth: formData.date_of_birth,
              time_of_birth: formData.time_of_birth,
              place_of_birth: formData.place_of_birth,
              latitude: formData.latitude,
              longitude: formData.longitude,
              timezone: formData.timezone,
              house_system: formData.house_system,
            }),
          });
          const savedData = res.data;
          addProfile(savedData);
          setSelectedProfileId(savedData.id);
          setSessionProfile(null); // Clear session profile
          toast.success('Profile saved successfully');
          return savedData;
        }

        // Session-only: keep it for the current browser session, but don't save to backend
        setSessionProfile(sessionOnlyProfile);
        setSelectedProfileId(null);
        toast.info('Profile saved for this browser session');
        return sessionOnlyProfile;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create profile';
        setError(message);
        toast.error(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [addProfile, setSelectedProfileId, setSessionProfile, setLoading, setError, token]
  );

  // Clear session profile when switching to any persisted profile
  const selectProfile = useCallback(
    (id: number | null) => {
      if (id !== null) {
        setSessionProfile(null);
      }
      setSelectedProfileId(id);
    },
    [setSelectedProfileId, setSessionProfile]
  );

  return {
    profiles,
    activeProfile: selectedProfile,
    activeProfileSource,
    activeProfileSourceLabel: getActiveProfileSourceLabel(activeProfileSource),
    hasActiveProfile: selectedProfile !== null,
    isGuestProfile: activeProfileSource === 'guest',
    isLocalProfile: activeProfileSource === 'local',
    isRailwayProfile: activeProfileSource === 'railway',
    isSessionProfile: activeProfileSource === 'session',
    selectedProfile,
    selectedProfileId,
    sessionProfile,
    setSelectedProfileId: selectProfile,
    suppressNextAutoFetch,
    clearAutoFetchSuppression,
    fetchProfiles,
    createProfile,
  };
}
