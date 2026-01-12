/**
 * anonReadingStorage.ts
 * Manages anonymous reading history in localStorage with 10-item limit
 */

export interface AnonReading {
  id: string;
  scope: 'daily' | 'weekly' | 'monthly' | 'forecast' | 'compatibility' | 'natal' | 'year-ahead';
  date: string;
  profile?: {
    name: string;
    date_of_birth: string;
    time_of_birth?: string;
    timezone?: string;
  };
  content: unknown;
  timestamp: number;
}

const STORAGE_KEY = 'astromeric_anon_readings';
const MAX_READINGS = 10;

/**
 * Get all anonymous readings from localStorage
 */
export function getAnonReadings(): AnonReading[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

/**
 * Add a new anonymous reading, auto-delete oldest if limit exceeded
 */
export function addAnonReading(reading: Omit<AnonReading, 'id' | 'timestamp'>): AnonReading {
  const readings = getAnonReadings();
  
  const newReading: AnonReading = {
    ...reading,
    id: `reading_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: Date.now(),
  };

  readings.push(newReading);

  // If over limit, remove oldest readings
  if (readings.length > MAX_READINGS) {
    const toRemove = readings.length - MAX_READINGS;
    readings.splice(0, toRemove);
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(readings));
  return newReading;
}

/**
 * Get reading count (for upsell trigger)
 */
export function getAnonReadingCount(): number {
  return getAnonReadings().length;
}

/**
 * Check if should show upsell (after 3rd reading)
 */
export function shouldShowUpsell(): boolean {
  return getAnonReadingCount() >= 3;
}

/**
 * Clear all anonymous readings
 */
export function clearAnonReadings(): void {
  localStorage.removeItem(STORAGE_KEY);
}

/**
 * Get readings to migrate (when user signs up)
 */
export function getReadingsForMigration(): AnonReading[] {
  return getAnonReadings();
}

/**
 * Clear readings after successful migration
 */
export function clearReadingsAfterMigration(): void {
  clearAnonReadings();
}

/**
 * Track that upsell has been shown this session (to avoid spam)
 */
export function markUpsellShown(): void {
  sessionStorage.setItem('astromeric_upsell_shown', 'true');
}

/**
 * Check if upsell has been shown this session
 */
export function hasUpsellBeenShown(): boolean {
  return sessionStorage.getItem('astromeric_upsell_shown') === 'true';
}
