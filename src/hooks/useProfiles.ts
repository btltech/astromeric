/**
 * Custom hook for profile management
 */
import { useCallback } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';
import type { NewProfileForm, SavedProfile } from '../types';

export function useProfiles() {
  const {
    profiles,
    selectedProfileId,
    setProfiles,
    setSelectedProfileId,
    addProfile,
    setLoading,
    setError,
    token,
  } = useStore();

  const selectedProfile = profiles.find((p) => p.id === selectedProfileId) || null;

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
        const headers: Record<string, string> = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const data = await apiFetch<SavedProfile>('/profiles', {
          method: 'POST',
          headers,
          body: JSON.stringify(formData),
        });
        addProfile(data);
        setSelectedProfileId(data.id);
        return data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create profile';
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [addProfile, setSelectedProfileId, setLoading, setError, token]
  );

  return {
    profiles,
    selectedProfile,
    selectedProfileId,
    setSelectedProfileId,
    fetchProfiles,
    createProfile,
  };
}
