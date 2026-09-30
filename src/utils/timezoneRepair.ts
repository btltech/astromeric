/**
 * Profiles saved before the timezone lookup worked were stored as "UTC" (the
 * lookup route didn't exist) or as a rough Etc/GMT guess, so their birth
 * times are read in the wrong zone. Look each one up again, once.
 */
import { getApiBaseUrl } from '../api/config';
import { useStore } from '../store/useStore';
import type { SavedProfile } from '../types';

export function needsTimezoneRepair(profile: SavedProfile | null | undefined): boolean {
  if (!profile || profile.latitude == null || profile.longitude == null) return false;
  const tz = profile.timezone ?? '';
  return tz === '' || tz === 'UTC' || tz.startsWith('Etc/GMT');
}

async function lookUpTimezone(lat: number, lon: number): Promise<string | null> {
  try {
    const resp = await fetch(`${getApiBaseUrl()}/v2/geocode/timezone?lat=${lat}&lon=${lon}`);
    if (!resp.ok) return null;
    const data = await resp.json();
    // Only trust a real answer, not the server's longitude estimate.
    return !data.estimated && typeof data.timezone === 'string' ? data.timezone : null;
  } catch {
    return null;
  }
}

async function repaired(profile: SavedProfile): Promise<SavedProfile | null> {
  if (!needsTimezoneRepair(profile)) return null;
  const tz = await lookUpTimezone(profile.latitude as number, profile.longitude as number);
  return tz && tz !== profile.timezone ? { ...profile, timezone: tz } : null;
}

let started = false;

/** Fixes the timezones of profiles kept in this browser. Runs once per page load. */
export async function repairSavedTimezones(): Promise<void> {
  if (started) return;
  started = true;
  const { profiles, sessionProfile } = useStore.getState();

  // Profiles with positive ids belong to an account and live on the server.
  for (const profile of profiles.filter((p) => p.id < 0)) {
    const fixed = await repaired(profile);
    if (fixed) useStore.getState().updateProfile(fixed.id, { timezone: fixed.timezone });
  }
  const fixedSession = sessionProfile ? await repaired(sessionProfile) : null;
  if (fixedSession) useStore.getState().setSessionProfile(fixedSession);
}
