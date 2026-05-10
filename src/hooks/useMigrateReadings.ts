/**
 * hooks/useMigrateReadings.ts
 * Hook for syncing device-local profiles and readings into the Railway backend.
 */

import { useCallback } from 'react';
import { apiFetch } from '../api/client';
import { useStore } from '../store/useStore';
import {
  getReadingsForMigration,
  clearReadingsAfterMigration,
} from '../utils/anonReadingStorage';

interface MigrateLocalDataResponse {
  status: 'success' | 'error';
  data: {
    migrated_profile_count: number;
    migrated_reading_count: number;
    skipped_reading_count: number;
    profile_id_map: Record<string, number>;
  };
  message?: string;
}

export function useMigrateReadings() {
  const migrateReadings = useCallback(async () => {
    try {
      const state = useStore.getState();
      const token = state.token;

      if (!token) {
        throw new Error('Sign in is required before syncing to Railway.');
      }

      const anonReadings = getReadingsForMigration();
      const localSavedProfiles = state.profiles.filter((profile) => profile.id < 0);
      const localProfiles = localSavedProfiles.map((profile) => ({
          id: profile.id,
          name: profile.name,
          date_of_birth: profile.date_of_birth,
          time_of_birth: profile.time_of_birth ?? undefined,
          place_of_birth: profile.place_of_birth ?? undefined,
          latitude: profile.latitude ?? undefined,
          longitude: profile.longitude ?? undefined,
          timezone: profile.timezone ?? undefined,
          house_system: profile.house_system ?? undefined,
        }));
      const selectedLocalProfileId =
        typeof state.selectedProfileId === 'number' &&
        localProfiles.some((profile) => profile.id === state.selectedProfileId)
          ? state.selectedProfileId
          : localProfiles[0]?.id ?? null;
      const compareLocalProfileId =
        typeof state.compareProfileId === 'number' &&
        localProfiles.some((profile) => profile.id === state.compareProfileId)
          ? state.compareProfileId
          : null;

      if (anonReadings.length === 0 && localProfiles.length === 0) {
        return {
          success: true,
          migratedProfileCount: 0,
          migratedReadingCount: 0,
          skippedReadingCount: 0,
        };
      }

      const result = await apiFetch<MigrateLocalDataResponse>('/v2/auth/migrate-local-data', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          profiles: localProfiles,
          readings: anonReadings,
        }),
      });

      if (result.status === 'success') {
        clearReadingsAfterMigration();
        const latestState = useStore.getState();
        const migratedProfileIdMap = result.data.profile_id_map ?? {};
        const promotedLocalProfiles = localSavedProfiles.flatMap((profile) => {
          const migratedId = migratedProfileIdMap[String(profile.id)];

          if (typeof migratedId !== 'number') {
            return [];
          }

          return [{
            ...profile,
            id: migratedId,
          }];
        });
        const promotedProfileIds = new Set(promotedLocalProfiles.map((profile) => profile.id));
        const retainedRemoteProfiles = latestState.profiles.filter(
          (profile) => profile.id > 0 && !promotedProfileIds.has(profile.id)
        );

        latestState.setProfiles([...retainedRemoteProfiles, ...promotedLocalProfiles]);

        if (
          selectedLocalProfileId !== null &&
          (latestState.selectedProfileId === null || latestState.selectedProfileId < 0)
        ) {
          latestState.setSelectedProfileId(
            migratedProfileIdMap[String(selectedLocalProfileId)] ?? null
          );
        }

        if (compareLocalProfileId !== null && latestState.compareProfileId !== null) {
          latestState.setCompareProfileId(
            migratedProfileIdMap[String(compareLocalProfileId)] ?? null
          );
        }
      }

      return {
        success: true,
        migratedProfileCount: result.data.migrated_profile_count,
        migratedReadingCount: result.data.migrated_reading_count,
        skippedReadingCount: result.data.skipped_reading_count,
      };
    } catch (error) {
      console.error('Failed to migrate readings:', error);
      throw error;
    }
  }, []);

  return { migrateReadings };
}
