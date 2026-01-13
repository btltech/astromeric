/**
 * hooks/useMigrateReadings.ts
 * Hook for migrating anonymous readings after signup
 */

import { useCallback } from 'react';
import { apiFetch } from '../api/client';
import {
  getReadingsForMigration,
  clearReadingsAfterMigration,
  type AnonReading,
} from '../utils/anonReadingStorage';

interface MigrateReadingsRequest {
  readings: AnonReading[];
  profile?: Record<string, unknown>;
}

export function useMigrateReadings() {
  const migrateReadings = useCallback(async (profileData?: Record<string, unknown>) => {
    try {
      const anonReadings = getReadingsForMigration();

      if (anonReadings.length === 0) {
        return { success: true, migratedCount: 0 };
      }

      const request: MigrateReadingsRequest = {
        readings: anonReadings,
      };

      // Include the first anon profile if available
      if (anonReadings[0]?.profile || profileData) {
        request.profile = anonReadings[0]?.profile || profileData;
      }

      const result = await apiFetch('/auth/migrate-anon-readings', {
        method: 'POST',
        body: JSON.stringify(request),
      });

      // Clear local storage after successful migration
      if (result.status === 'success') {
        clearReadingsAfterMigration();
      }

      return result;
    } catch (error) {
      console.error('Failed to migrate readings:', error);
      throw error;
    }
  }, []);

  return { migrateReadings };
}
