import React, { useEffect, useMemo, useState } from 'react';
import { fetchNatalProfile, type LiveNatalProfile, type ProfilePayload } from '../api/client';
import { useActiveProfile } from '../hooks';
import type { SavedProfile } from '../types';

const previewProfile: ProfilePayload = {
  name: 'Amara Lewis',
  date_of_birth: '1994-11-18',
  time_of_birth: '07:18',
  location: {
    latitude: 51.5074,
    longitude: -0.1278,
    timezone: 'Europe/London',
  },
};

function toProfilePayload(profile: SavedProfile | null): ProfilePayload {
  if (!profile) {
    return previewProfile;
  }

  return {
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth ?? previewProfile.time_of_birth,
    location: {
      latitude: profile.latitude ?? previewProfile.location?.latitude,
      longitude: profile.longitude ?? previewProfile.location?.longitude,
      timezone: profile.timezone ?? previewProfile.location?.timezone,
    },
  };
}

function formatAspectType(type: string) {
  return type
    .split(/[_-]/g)
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');
}

function getStrongestAspect(natalProfile: LiveNatalProfile | null) {
  return [...(natalProfile?.chart.aspects ?? [])].sort((left, right) => {
    const strengthDelta = (right.strength ?? 0) - (left.strength ?? 0);

    if (strengthDelta !== 0) {
      return strengthDelta;
    }

    return left.orb - right.orb;
  })[0] ?? null;
}

export function HomeChartStrip() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();

  const requestProfile = useMemo(() => toProfilePayload(activeProfile), [activeProfile]);
  const [natalProfile, setNatalProfile] = useState<LiveNatalProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadChartStrip() {
      setLoading(true);
      setError(null);

      try {
        const liveNatalProfile = await fetchNatalProfile(requestProfile);

        if (isCancelled) {
          return;
        }

        setNatalProfile(liveNatalProfile);
      } catch (err) {
        if (isCancelled) {
          return;
        }

        const message = err instanceof Error ? err.message : 'Could not load live chart data.';
        setNatalProfile(null);
        setError(message);
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    loadChartStrip();

    return () => {
      isCancelled = true;
    };
  }, [requestProfile]);

  const sunPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Sun');
  const moonPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Moon');
  const risingSign = natalProfile?.chart.houses.find((house) => house.house === 1)?.sign;
  const strongestAspect = getStrongestAspect(natalProfile);
  const sourceLabel = hasActiveProfile ? activeProfileSourceLabel : 'Preview profile';
  const liveLeadDetail = error
    ? error
    : strongestAspect
      ? `Strongest aspect: ${strongestAspect.planet_a} ${formatAspectType(strongestAspect.type)} ${strongestAspect.planet_b}`
      : loading
        ? 'Loading the live natal chart for this homepage strip.'
        : 'Live chart signals will surface here once the natal payload resolves.';

  const cards = [
    {
      label: 'Live chart desk',
      value: requestProfile.name,
      detail: `${sourceLabel} · ${liveLeadDetail}`,
    },
    {
      label: 'Solar focus',
      value: sunPlacement ? `${sunPlacement.sign} Sun` : loading ? 'Loading Sun' : 'Sun unavailable',
      detail: sunPlacement
        ? `House ${sunPlacement.house} · ${sunPlacement.retrograde ? 'Retrograde signal' : 'Direct signal'}`
        : 'The live natal feed will set the lead solar placement here.',
    },
    {
      label: 'Lunar tone',
      value: moonPlacement ? `${moonPlacement.sign} Moon` : loading ? 'Loading Moon' : 'Moon unavailable',
      detail: moonPlacement
        ? `House ${moonPlacement.house} · Emotional timing from the live chart feed.`
        : 'The live natal feed will set the Moon placement here.',
    },
    {
      label: 'Rising edge',
      value: risingSign ? `${risingSign} rising` : loading ? 'Loading rising sign' : 'Rising sign unavailable',
      detail: risingSign
        ? `${requestProfile.location?.timezone ?? 'UTC'} · First-house entry point from the natal chart.`
        : 'The first-house cusp will appear here when the chart payload resolves.',
    },
  ];

  return (
    <section className="home-modern__signal-strip" aria-label="Live chart signal strip">
      {cards.map((card) => (
        <article key={card.label} className="home-modern__signal-card">
          <span>{card.label}</span>
          <strong>{card.value}</strong>
          <p>{card.detail}</p>
        </article>
      ))}
    </section>
  );
}