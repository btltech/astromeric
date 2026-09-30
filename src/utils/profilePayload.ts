import type { ProfilePayload } from '../api/client';
import type { SavedProfile } from '../types';

/**
 * The sample person the desks show before anyone has made a profile. Pages
 * label it a preview. It is never mixed into a real profile: a real profile
 * that lacks a birth time or place is sent as it is, so the server can say the
 * chart is approximate instead of us charting someone else's details.
 */
export const PREVIEW_PROFILE: SavedProfile = {
  id: -1,
  name: 'Amara Lewis',
  date_of_birth: '1994-11-18',
  time_of_birth: '08:30',
  place_of_birth: 'London, UK',
  latitude: 51.5072,
  longitude: -0.1276,
  timezone: 'Europe/London',
  house_system: 'Placidus',
};

/** Request body for a profile; the sample person when there is no profile. */
export function toProfilePayload(profile: SavedProfile | null): ProfilePayload {
  const source = profile ?? PREVIEW_PROFILE;
  const hasPlace = source.latitude != null && source.longitude != null;

  return {
    name: source.name,
    date_of_birth: source.date_of_birth,
    time_of_birth: source.time_of_birth ?? undefined,
    place_of_birth: source.place_of_birth ?? undefined,
    location: hasPlace
      ? {
          latitude: source.latitude as number,
          longitude: source.longitude as number,
          timezone: source.timezone ?? undefined,
        }
      : undefined,
    house_system: source.house_system ?? 'Placidus',
  };
}

/** What a real profile is missing that makes the chart approximate. */
export function missingChartDetails(profile: SavedProfile | null): string[] {
  if (!profile) return [];
  const missing: string[] = [];
  if (!profile.time_of_birth) missing.push('birth time');
  if (profile.latitude == null || profile.longitude == null) missing.push('birthplace');
  return missing;
}
