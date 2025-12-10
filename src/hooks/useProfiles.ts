/**
 * Custom hook for profile management
 * Supports both saved profiles (opt-in) and session-only profiles (default)
 */
import { useCallback, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { NewProfileForm, SavedProfile } from '../types';
import { toast } from '../components/Toast';

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

  // Auto-fetch saved profiles from backend when token is available
  useEffect(() => {
    if (!token) return;
    const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
    apiFetch<SavedProfile[]>('/profiles', { headers })
      .then(setProfiles)
      .catch((err) => console.error('Failed to auto-fetch profiles:', err));
  }, [token, setProfiles]);

  // Get the active profile (session or saved)
  const selectedProfile = sessionProfile || profiles.find((p) => p.id === selectedProfileId) || null;

  const fetchProfiles = useCallback(async () => {
    try {
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const data = await apiFetch<SavedProfile[]>('/profiles', { headers });
      setProfiles(data);
    } catch (err) {
      console.error('Failed to fetch profiles:', err);
    }
  }, [setProfiles, token]);

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

        // If user opts in to save, also store in backend
        if (formData.saveProfile) {
          const headers: Record<string, string> = {};
          if (token) headers['Authorization'] = `Bearer ${token}`;

          const savedData = await apiFetch<SavedProfile>('/profiles', {
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
          addProfile(savedData);
          setSelectedProfileId(savedData.id);
          setSessionProfile(null); // Clear session profile
          toast.success('Profile saved successfully');
          return savedData;
        }

        // Session-only: store in memory, don't save to backend
        setSessionProfile(sessionOnlyProfile);
        setSelectedProfileId(null);
        toast.info('Profile created for this session');
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

  // Clear session profile when switching to a saved profile
  const selectProfile = useCallback((id: number | null) => {
    if (id !== null && id > 0) {
      setSessionProfile(null);
    }
    setSelectedProfileId(id);
  }, [setSelectedProfileId, setSessionProfile]);

  return {
    profiles,
    selectedProfile,
    selectedProfileId,
    sessionProfile,
    setSelectedProfileId: selectProfile,
    fetchProfiles,
    createProfile,
  };
}
