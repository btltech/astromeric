/**
 * hooks/useAnonReadings.ts
 * Hook for managing anonymous reading history and upsell
 */

import { useState, useEffect } from 'react';
import {
  getAnonReadings,
  addAnonReading,
  getAnonReadingCount,
  shouldShowUpsell,
  hasUpsellBeenShown,
  markUpsellShown,
  clearAnonReadings,
  getReadingsForMigration,
  clearReadingsAfterMigration,
  type AnonReading,
} from '../utils/anonReadingStorage';

export function useAnonReadings() {
  const [readings, setReadings] = useState<AnonReading[]>([]);
  const [readingCount, setReadingCount] = useState(0);
  const [shouldShowUpsellModal, setShouldShowUpsellModal] = useState(false);

  // Initialize from localStorage
  useEffect(() => {
    const stored = getAnonReadings();
    setReadings(stored);
    setReadingCount(stored.length);
  }, []);

  // Check if should show upsell
  useEffect(() => {
    if (shouldShowUpsell() && !hasUpsellBeenShown()) {
      setShouldShowUpsellModal(true);
      markUpsellShown();
    }
  }, [readingCount]);

  const saveReading = (reading: Omit<AnonReading, 'id' | 'timestamp'>) => {
    const newReading = addAnonReading(reading);
    setReadings(getAnonReadings());
    setReadingCount(getAnonReadingCount());
    return newReading;
  };

  const closeUpsell = () => {
    setShouldShowUpsellModal(false);
  };

  const migrateReadings = () => {
    const toMigrate = getReadingsForMigration();
    clearReadingsAfterMigration();
    setReadings([]);
    setReadingCount(0);
    return toMigrate;
  };

  const clearAll = () => {
    clearAnonReadings();
    setReadings([]);
    setReadingCount(0);
  };

  return {
    readings,
    readingCount,
    shouldShowUpsellModal,
    saveReading,
    closeUpsell,
    migrateReadings,
    clearAll,
  };
}
