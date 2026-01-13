export interface SharedProfile {
  name: string;
  dob: string;
  tob?: string;
  lat: number;
  lng: number;
  tz: string;
}

export function encodeProfile(profile: SharedProfile): string {
  const data = JSON.stringify(profile);
  return btoa(data);
}

export function decodeProfile(hash: string): SharedProfile | null {
  try {
    const data = atob(hash);
    return JSON.parse(data);
  } catch (e) {
    console.error('Failed to decode shared profile', e);
    return null;
  }
}

export function getComparisonUrl(profile: SharedProfile): string {
  const hash = encodeProfile(profile);
  const url = new URL(window.location.href);
  url.pathname = '/compare';
  url.searchParams.set('p', hash);
  return url.toString();
}
