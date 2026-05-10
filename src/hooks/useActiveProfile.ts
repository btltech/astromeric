import { useMemo } from 'react';
import { useStore } from '../store/useStore';
import type { SavedProfile } from '../types';

export type ActiveProfileSource = 'session' | 'local' | 'railway' | 'guest';

export function resolveActiveProfile(
  profiles: SavedProfile[],
  selectedProfileId: number | null,
  sessionProfile: SavedProfile | null
) {
  if (sessionProfile) {
    return sessionProfile;
  }

  return profiles.find((profile) => profile.id === selectedProfileId) ?? profiles[0] ?? null;
}

export function getActiveProfileSource(
  activeProfile: SavedProfile | null,
  sessionProfile: SavedProfile | null
): ActiveProfileSource {
  if (!activeProfile) {
    return 'guest';
  }

  if (sessionProfile) {
    return 'session';
  }

  return activeProfile.id < 0 ? 'local' : 'railway';
}

export function getActiveProfileSourceLabel(source: ActiveProfileSource) {
  switch (source) {
    case 'session':
      return 'Browser session';
    case 'local':
      return 'Saved on this device';
    case 'railway':
      return 'Railway profile';
    default:
      return 'Guest defaults';
  }
}

export function useActiveProfile() {
  const { profiles, selectedProfileId, sessionProfile } = useStore();

  const activeProfile = useMemo(
    () => resolveActiveProfile(profiles, selectedProfileId, sessionProfile),
    [profiles, selectedProfileId, sessionProfile]
  );
  const activeProfileSource = useMemo(
    () => getActiveProfileSource(activeProfile, sessionProfile),
    [activeProfile, sessionProfile]
  );

  return {
    activeProfile,
    activeProfileSource,
    activeProfileSourceLabel: getActiveProfileSourceLabel(activeProfileSource),
    hasActiveProfile: activeProfile !== null,
    isGuestProfile: activeProfileSource === 'guest',
    isLocalProfile: activeProfileSource === 'local',
    isRailwayProfile: activeProfileSource === 'railway',
    isSessionProfile: activeProfileSource === 'session',
    profiles,
    selectedProfileId,
    sessionProfile,
  };
}