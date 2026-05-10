import React, { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  fetchCompatibility,
  fetchNatalProfile,
  fetchNumerologyProfile,
  fetchWeeklyForecast,
  type ForecastDay,
  type LiveChartPlanet,
  type LiveCompatibilityResult,
  type LiveNatalProfile,
  type LiveNumerologyProfile,
  type ProfilePayload,
} from '../api/client';
import { ChartWheel } from '../components/ChartWheel';
import { DocumentMeta } from '../components/DocumentMeta';
import { useActiveProfile } from '../hooks';
import { useStore } from '../store/useStore';
import type { SavedProfile } from '../types';
import './ProductExperienceView.css';

type ChartWheelData = React.ComponentProps<typeof ChartWheel>['chartData'];

type ExperienceSignal = {
  label: string;
  value: string;
  note: string;
};

type ExperienceInsight = {
  label: string;
  text: string;
};

type ChartQualityState = {
  label: string;
  message: string;
  tone: 'stable' | 'warning' | 'info';
};

type BigThreeSignal = {
  label: string;
  value: string;
  reliability: string;
  tone: 'confirmed' | 'approximate' | 'uncertain' | 'pending';
};

type WorkflowLaneTone = 'chart' | 'numerology' | 'compatibility';

type WorkflowLane = {
  href: string;
  label: string;
  title: string;
  status: string;
  note: string;
  action: string;
  tone: WorkflowLaneTone;
};

type WorkflowStep = {
  label: string;
  detail: string;
};

const previewProfile: SavedProfile = {
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

const previewCompareProfile: SavedProfile = {
  id: -2,
  name: 'Noah Hart',
  date_of_birth: '1992-04-05',
  time_of_birth: '09:15',
  place_of_birth: 'New York, USA',
  latitude: 40.7128,
  longitude: -74.006,
  timezone: 'America/New_York',
  house_system: 'Placidus',
};

const surfaceTags = ['Chart desk', 'Numerology desk', 'Compatibility board', 'Daily brief'] as const;
const featuredPlanetNames = ['Sun', 'Moon', 'Mercury'] as const;

function toProfilePayload(profile: SavedProfile | null): ProfilePayload {
  const source = profile ?? previewProfile;

  return {
    name: source.name,
    date_of_birth: source.date_of_birth,
    time_of_birth: source.time_of_birth ?? previewProfile.time_of_birth ?? undefined,
    place_of_birth: source.place_of_birth ?? previewProfile.place_of_birth ?? undefined,
    location: {
      latitude: source.latitude ?? previewProfile.latitude ?? 0,
      longitude: source.longitude ?? previewProfile.longitude ?? 0,
      timezone: source.timezone ?? previewProfile.timezone ?? 'UTC',
    },
    house_system: source.house_system ?? previewProfile.house_system ?? 'Placidus',
  };
}

function formatScore(score: number) {
  if (score >= 80) return 'Strong';
  if (score >= 65) return 'Promising';
  return 'Complex';
}

function formatAspectType(aspect: string) {
  return aspect.replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDimensionLabel(name: string) {
  return name.replace(/_/g, ' ');
}

function formatLocationLabel(profile: ProfilePayload) {
  return profile.place_of_birth ?? profile.location?.timezone ?? 'Location pending';
}

function getPlanetInsightText(planet: LiveChartPlanet) {
  const baseCopy: Record<string, string> = {
    Sun: 'Your core identity serves as the leading theme for your astrological makeup.',
    Moon: 'Your emotional tone shapes how you process underlying feelings and reactions.',
    Mercury: 'Your communication and decision style is a practical, everyday reflection of your intellect.',
    Venus: 'Your relationship style defines your romantic and social connections in grounded ways.',
    Mars: 'Your action strategy is one of the clearest indicators of how you turn energy into motion.',
  };

  const base = baseCopy[planet.name] ?? 'This placement serves as a clear, trustworthy signal in your chart.';
  return planet.retrograde ? `${base} Retrograde motion adds a more internal and reflective edge.` : base;
}

function toChartWheelData(natalProfile: LiveNatalProfile | null): ChartWheelData | null {
  if (!natalProfile) {
    return null;
  }

  const planets = Object.fromEntries(
    natalProfile.chart.planets.map((planet) => [
      planet.name,
      {
        name: planet.name,
        sign: planet.sign,
        degree: Number(planet.degree.toFixed(1)),
        house: planet.house,
      },
    ])
  );

  const houses = Object.fromEntries(
    natalProfile.chart.houses.map((house) => [
      String(house.house),
      {
        cusp: Number(house.degree.toFixed(1)),
        sign: house.sign,
      },
    ])
  );

  const aspects = natalProfile.chart.aspects
    .filter((aspect) => planets[aspect.planet_a] && planets[aspect.planet_b])
    .map((aspect) => ({
      planet1: aspect.planet_a,
      planet2: aspect.planet_b,
      aspect: aspect.type,
      orb: Number(aspect.orb.toFixed(1)),
    }));

  const ascendant = natalProfile.chart.houses.find((house) => house.house === 1);
  const midheaven = natalProfile.chart.houses.find((house) => house.house === 10);

  return {
    planets,
    houses,
    aspects,
    ascendant: ascendant
      ? { sign: ascendant.sign, degree: Number(ascendant.degree.toFixed(1)) }
      : undefined,
    midheaven: midheaven
      ? { sign: midheaven.sign, degree: Number(midheaven.degree.toFixed(1)) }
      : undefined,
  };
}

function buildChartInsights(natalProfile: LiveNatalProfile | null): ExperienceInsight[] {
  if (!natalProfile) {
    return [
      {
        label: 'Chart feed unavailable',
        text: 'Your chart data is not yet available, so the chart preview cannot render yet.',
      },
    ];
  }

  const planetInsights = featuredPlanetNames
    .map((name) => natalProfile.chart.planets.find((planet) => planet.name === name))
    .filter((planet): planet is LiveChartPlanet => Boolean(planet))
    .map((planet) => ({
      label: `${planet.name} in ${planet.sign} · House ${planet.house}`,
      text: getPlanetInsightText(planet),
    }));

  const strongestAspect = [...natalProfile.chart.aspects].sort(
    (left, right) => (right.strength ?? 0) - (left.strength ?? 0)
  )[0];

  if (strongestAspect) {
    planetInsights.push({
      label: `${strongestAspect.planet_a} ${formatAspectType(strongestAspect.type)} ${strongestAspect.planet_b}`,
      text: `A tight ${strongestAspect.orb.toFixed(1)}° orb makes this one of the most prominent connections in your chart, offering clear and practical guidance.`,
    });
  }

  return planetInsights.slice(0, 3);
}

function buildChartQualityStates(natalProfile: LiveNatalProfile | null): ChartQualityState[] {
  if (!natalProfile) {
    return [
      {
        label: 'Chart feed unavailable',
        message: 'Your chart data is not yet available, so the trust cues are waiting on fresh chart data.',
        tone: 'warning',
      },
    ];
  }

  const { metadata } = natalProfile.chart;
  const states: ChartQualityState[] = [];

  if (metadata.location_assumed) {
    states.push({
      label: 'Location missing',
      message: 'Birth location is missing, so an estimated location is being used for your houses and rising sign.',
      tone: 'warning',
    });
  } else if (metadata.birth_time_assumed) {
    states.push({
      label: 'Birth time estimated',
      message: 'Rising sign and houses are approximate because the chart is using an assumed birth time for this profile.',
      tone: 'warning',
    });
  }

  if (metadata.moon_sign_uncertain) {
    states.push({
      label: 'Moon may shift',
      message: 'The Moon changed sign on this birth date, so the lunar reading can move with an exact birth time.',
      tone: 'info',
    });
  }

  if (states.length === 0) {
    states.push({
      label: 'Chart confidence',
      message: 'Birth time and location are present, so the Big Three and houses are running on the live chart data.',
      tone: 'stable',
    });
  }

  return states;
}

function buildBigThreeSignals(natalProfile: LiveNatalProfile | null): BigThreeSignal[] {
  const sunPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Sun');
  const moonPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Moon');
  const risingSign = natalProfile?.chart.houses.find((house) => house.house === 1)?.sign;
  const metadata = natalProfile?.chart.metadata;

  return [
    {
      label: 'Sun',
      value: sunPlacement ? `${sunPlacement.sign} · House ${sunPlacement.house}` : 'Pending',
      reliability: sunPlacement ? 'Confirmed placement' : 'Waiting for chart data',
      tone: sunPlacement ? 'confirmed' : 'pending',
    },
    {
      label: 'Moon',
      value: moonPlacement ? `${moonPlacement.sign} · House ${moonPlacement.house}` : 'Pending',
      reliability: moonPlacement
        ? metadata?.moon_sign_uncertain
          ? 'May shift without exact time'
          : 'Confirmed placement'
        : 'Waiting for chart data',
      tone: moonPlacement ? (metadata?.moon_sign_uncertain ? 'uncertain' : 'confirmed') : 'pending',
    },
    {
      label: 'Rising',
      value: risingSign ? `${risingSign} rising` : 'Pending',
      reliability: risingSign
        ? metadata?.location_assumed
          ? 'Estimated location in use'
          : metadata?.birth_time_assumed
            ? 'Estimated from assumed time'
            : 'Confirmed placement'
        : 'Waiting for chart data',
      tone: risingSign
        ? metadata?.location_assumed || metadata?.birth_time_assumed
          ? 'approximate'
          : 'confirmed'
        : 'pending',
    },
  ];
}

function buildHeroSignals(
  weeklyForecast: ForecastDay[],
  natalProfile: LiveNatalProfile | null,
  numerologyProfile: LiveNumerologyProfile | null,
  compatibilityResult: LiveCompatibilityResult | null
): ExperienceSignal[] {
  const sunPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Sun');
  const today = weeklyForecast[0];
  const overallCompatibility = compatibilityResult ? Math.round(compatibilityResult.overall_score) : null;

  return [
    {
      label: 'Signal of the day',
      value: today ? `${today.icon} ${today.vibe}` : 'Loading daily timing',
      note: today?.recommendation ?? "Your daily forecast will appear here once it is ready.",
    },
    {
      label: 'Chart focus',
      value: sunPlacement ? `${sunPlacement.sign} Sun · House ${sunPlacement.house}` : 'Waiting for chart data',
      note: sunPlacement
        ? 'Your specific astrological placements dictate the strongest core signals shown here.'
        : 'Your strongest personal chart placement will appear here.',
    },
    {
      label: 'Timing read',
      value: numerologyProfile ? `Year ${numerologyProfile.personal_year.cycle_number}` : 'Numerology loading',
      note:
        numerologyProfile?.personal_year.interpretation ??
        'Your live numerology cycle will provide the timing insight for this desk.',
    },
    {
      label: 'Relationship board',
      value:
        overallCompatibility !== null
          ? `${overallCompatibility}% ${formatScore(overallCompatibility)}`
          : 'Choose a profile to compare',
      note:
        compatibilityResult?.summary ??
        'Pick a second saved profile to see real compatibility insights instead of preview text.',
    },
  ];
}

export function ProductExperienceView() {
  const {
    activeProfile,
    activeProfileSourceLabel,
    profiles,
    selectedProfileId,
    sessionProfile,
  } = useActiveProfile();
  const { compareProfileId, setSelectedProfileId, setCompareProfileId, setSessionProfile } = useStore();
  const [natalProfile, setNatalProfile] = useState<LiveNatalProfile | null>(null);
  const [numerologyProfile, setNumerologyProfile] = useState<LiveNumerologyProfile | null>(null);
  const [compatibilityResult, setCompatibilityResult] = useState<LiveCompatibilityResult | null>(null);
  const [weeklyForecast, setWeeklyForecast] = useState<ForecastDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [issues, setIssues] = useState<string[]>([]);
  const sessionPrimaryBackup = useRef<SavedProfile | null>(sessionProfile);

  useEffect(() => {
    if (sessionProfile) {
      sessionPrimaryBackup.current = sessionProfile;
    }
  }, [sessionProfile]);

  useEffect(() => {
    if (selectedProfileId !== null && !profiles.some((profile) => profile.id === selectedProfileId)) {
      setSelectedProfileId(null);
    }
  }, [profiles, selectedProfileId, setSelectedProfileId]);

  const availableComparisonProfiles = useMemo(
    () => profiles.filter((profile) => profile.id !== activeProfile?.id),
    [activeProfile?.id, profiles]
  );

  useEffect(() => {
    if (
      compareProfileId !== null &&
      !availableComparisonProfiles.some((profile) => profile.id === compareProfileId)
    ) {
      setCompareProfileId(null);
    }
  }, [availableComparisonProfiles, compareProfileId, setCompareProfileId]);

  const comparisonProfile = useMemo(() => {
    if (compareProfileId !== null) {
      return availableComparisonProfiles.find((profile) => profile.id === compareProfileId) ?? null;
    }

    return null;
  }, [availableComparisonProfiles, compareProfileId]);

  const primaryPayload = useMemo(() => toProfilePayload(activeProfile), [activeProfile]);
  const comparisonPayload = useMemo(
    () => (comparisonProfile ? toProfilePayload(comparisonProfile) : null),
    [comparisonProfile]
  );

  useEffect(() => {
    let isCancelled = false;

    async function loadExperience() {
      setLoading(true);
      setIssues([]);

      const [natalResult, numerologyResult, compatibilityFeed, forecastFeed] = await Promise.allSettled([
        fetchNatalProfile(primaryPayload),
        fetchNumerologyProfile(primaryPayload),
        comparisonPayload ? fetchCompatibility(primaryPayload, comparisonPayload) : Promise.resolve(null),
        fetchWeeklyForecast(primaryPayload),
      ]);

      if (isCancelled) {
        return;
      }

      const nextIssues: string[] = [];

      if (natalResult.status === 'fulfilled') {
        setNatalProfile(natalResult.value);
      } else {
        setNatalProfile(null);
        nextIssues.push('Chart desk could not load live natal data.');
      }

      if (numerologyResult.status === 'fulfilled') {
        setNumerologyProfile(numerologyResult.value);
      } else {
        setNumerologyProfile(null);
        nextIssues.push('Numerology desk could not load live cycle data.');
      }

      if (compatibilityFeed.status === 'fulfilled' && compatibilityFeed.value) {
        setCompatibilityResult(compatibilityFeed.value);
      } else if (compatibilityFeed.status === 'rejected') {
        setCompatibilityResult(null);
        nextIssues.push('Compatibility board could not load the selected pairing.');
      } else {
        setCompatibilityResult(null);
      }

      if (forecastFeed.status === 'fulfilled') {
        setWeeklyForecast(forecastFeed.value.days);
      } else {
        setWeeklyForecast([]);
        nextIssues.push('Daily brief could not load the live weekly forecast.');
      }

      setIssues(nextIssues);
      setLoading(false);
    }

    loadExperience();

    return () => {
      isCancelled = true;
    };
  }, [comparisonPayload, primaryPayload]);

  const chartData = useMemo(() => toChartWheelData(natalProfile), [natalProfile]);
  const chartInsights = useMemo(() => buildChartInsights(natalProfile), [natalProfile]);
  const chartQualityStates = useMemo(() => buildChartQualityStates(natalProfile), [natalProfile]);
  const bigThreeSignals = useMemo(() => buildBigThreeSignals(natalProfile), [natalProfile]);
  const heroSignals = useMemo(
    () => buildHeroSignals(weeklyForecast, natalProfile, numerologyProfile, compatibilityResult),
    [compatibilityResult, natalProfile, numerologyProfile, weeklyForecast]
  );

  const sunPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Sun');
  const moonPlacement = natalProfile?.chart.planets.find((planet) => planet.name === 'Moon');
  const overallScore = compatibilityResult ? Math.round(compatibilityResult.overall_score) : null;
  const overallTone = overallScore !== null ? formatScore(overallScore) : 'Pending';
  const compatibilityBreakdown = compatibilityResult?.dimensions ?? [];
  const chartAuthorityStats = [
    { label: 'Planets', value: natalProfile ? String(natalProfile.chart.planets.length) : '...' },
    { label: 'Houses', value: natalProfile ? String(natalProfile.chart.houses.length) : '...' },
    { label: 'Aspects', value: natalProfile ? String(natalProfile.chart.aspects.length) : '...' },
  ];
  const lifePurposeLead = numerologyProfile?.life_path.life_purpose ?? null;
  const numerologyStrengths = numerologyProfile?.synthesis?.strengths.slice(0, 3) ?? [];
  const numerologyCurrentFocus =
    numerologyProfile?.synthesis?.current_focus ?? numerologyProfile?.personal_year.interpretation ?? null;
  const numerologyGrowthEdge = numerologyProfile?.synthesis?.growth_edges[0] ?? null;
  const numerologyAffirmation = numerologyProfile?.synthesis?.affirmation ?? null;
  const topChartInsight = chartInsights[0] ?? null;
  const topCompatibilityDimension = compatibilityBreakdown[0] ?? null;
  const bigThreeSummary = bigThreeSignals
    .map((item) => `${item.label}: ${item.value}`)
    .join(' · ');
  const primarySourceLabel = activeProfile ? activeProfileSourceLabel : 'Preview profile';
  const comparisonSourceLabel = comparisonProfile
    ? 'Selected compare profile'
    : availableComparisonProfiles.length > 0
      ? 'Choose compare profile'
      : 'No compare profile';
  const qualityNote = natalProfile?.chart.metadata.location_assumed
    ? 'Birth location is missing, so the chart is using fallback coordinates.'
    : null;
  const compatibilityPrompt = availableComparisonProfiles.length > 0
    ? 'Choose a saved second profile to load real compatibility for this route.'
    : 'Add a second profile in the reading desk to unlock live compatibility on this route.';
  const compatibilitySetupHeadline = availableComparisonProfiles.length > 0
    ? 'Select a saved partner to unlock the live pairing board.'
    : 'Add a second profile to start compatibility.';
  const compatibilitySetupSteps = availableComparisonProfiles.length > 0
    ? [
        'Choose the primary profile in the hero card if the wrong person is driving the route.',
        'Use the Compare with selector in the partner card to choose a saved second profile.',
        'The board will switch from setup state to live score, breakdown, and strengths as soon as the pair is set.',
      ]
    : [
        'Create or save a second profile in the reading desk so this screen has a real partner to compare.',
        'Keep the primary selector pointed at the person you want as Person A.',
        'When another saved profile exists, the live pairing board unlocks automatically.',
      ];
  const hasPrimarySelectorOptions = profiles.length > 0 || sessionPrimaryBackup.current !== null;
  const primaryPrompt = hasPrimarySelectorOptions
    ? 'Choose which profile should drive the live chart, numerology, and forecast desks.'
    : 'Create a profile in the reading desk to switch this route away from the preview chart.';
  const chartWorkflowStatus = !natalProfile
    ? loading
      ? 'Loading chart feed'
      : 'Chart feed delayed'
    : natalProfile.chart.metadata.location_assumed
      ? 'Approximate houses'
      : natalProfile.chart.metadata.birth_time_assumed
        ? 'Estimated rising sign'
        : 'Chart confidence locked';
  const numerologyWorkflowStatus = !numerologyProfile
    ? loading
      ? 'Loading numerology'
      : 'Numerology delayed'
    : `Life Path ${numerologyProfile.life_path.number} · Year ${numerologyProfile.personal_year.cycle_number}`;
  const compatibilityWorkflowStatus = !comparisonProfile
    ? availableComparisonProfiles.length > 0
      ? 'Choose second profile'
      : 'Need another profile'
    : compatibilityResult
      ? `${overallTone} · ${overallScore}%`
      : loading
        ? 'Loading pairing'
        : 'Pairing delayed';
  const workflowLanes: WorkflowLane[] = [
    {
      href: '#chart-desk',
      label: 'Chart workflow',
      title: 'Validate the chart before reading meaning',
      status: chartWorkflowStatus,
      note:
        chartQualityStates[0]?.message ??
        'Use trust cues first, then scan the Big Three, then move into the strongest aspect.',
      action: 'Open chart desk',
      tone: 'chart',
    },
    {
      href: '/numerology',
      label: 'Numerology workflow',
      title: 'Use numbers as timing, not decoration',
      status: numerologyWorkflowStatus,
      note:
        numerologyCurrentFocus ??
        numerologyProfile?.personal_year.interpretation ??
        'Lock the core numbers first, then use the current cycle and purpose brief as the next move.',
      action: 'Open numerology desk',
      tone: 'numerology',
    },
    {
      href: '#compatibility-board',
      label: 'Compatibility workflow',
      title: 'Compare two real profiles with follow-through',
      status: compatibilityWorkflowStatus,
      note: comparisonProfile
        ? compatibilityResult?.summary ?? 'The paired board is waiting on the live compatibility response.'
        : compatibilityPrompt,
      action: 'Open compatibility board',
      tone: 'compatibility',
    },
  ];
  const chartPlaybook: WorkflowStep[] = [
    {
      label: 'Trust first',
      detail:
        chartQualityStates[0]?.message ??
        'Check whether birth time or location is assumed before using houses or rising sign.',
    },
    {
      label: 'Big Three scan',
      detail: bigThreeSummary,
    },
    {
      label: 'Next drill-down',
      detail: topChartInsight
        ? `${topChartInsight.label} is the cleanest next signal to unpack after the first scan.`
        : 'The strongest live chart signal will surface here once the natal feed resolves.',
    },
  ];
  const numerologyPlaybook: WorkflowStep[] = [
    {
      label: 'Lock core numbers',
      detail: numerologyProfile
        ? `Life Path ${numerologyProfile.life_path.number}, Destiny ${numerologyProfile.destiny_number}, and Personal Year ${numerologyProfile.personal_year.cycle_number} set the baseline.`
        : 'Core numbers will populate here once the live numerology feed resolves.',
    },
    {
      label: 'Use current timing',
      detail:
        numerologyCurrentFocus ??
        numerologyProfile?.personal_year.interpretation ??
        'The live cycle feed will surface the current timing posture here.',
    },
    {
      label: 'Carry the brief',
      detail:
        numerologyAffirmation ??
        lifePurposeLead ??
        'Use the purpose brief to connect long-range meaning back to the current cycle.',
    },
  ];
  const compatibilityPlaybook: WorkflowStep[] = comparisonProfile
    ? [
        {
          label: 'Pair locked',
          detail: `${primaryPayload.name} and ${comparisonProfile.name} are the active pairing on this route.`,
        },
        {
          label: 'Start with the split',
          detail: topCompatibilityDimension
            ? `${formatDimensionLabel(topCompatibilityDimension.name)} currently leads the board at ${Math.round(topCompatibilityDimension.score)}%.`
            : 'The topic-by-topic breakdown will surface here once the pairing feed resolves.',
        },
        {
          label: 'Carry the watch-out',
          detail:
            compatibilityResult?.recommendations[0] ??
            compatibilityResult?.summary ??
            'The first live recommendation becomes the next follow-through item.',
        },
      ]
    : [
        {
          label: 'Primary profile',
          detail: `${primaryPayload.name} is driving the charts route right now.`,
        },
        {
          label: 'Choose partner',
          detail: compatibilityPrompt,
        },
        {
          label: 'Unlock board',
          detail:
            'Once the second profile is set, this desk opens into score, breakdown, strengths, and watch-outs.',
        },
      ];
  const primarySelectorValue = sessionProfile
    ? 'session'
    : activeProfile
      ? String(activeProfile.id)
      : sessionPrimaryBackup.current
        ? 'session'
        : '';

  function handlePrimaryProfileChange(nextValue: string) {
    if (nextValue === 'session') {
      setSelectedProfileId(null);

      if (sessionPrimaryBackup.current) {
        setSessionProfile(sessionPrimaryBackup.current);
      }
      return;
    }

    setSessionProfile(null);
    setSelectedProfileId(Number(nextValue));
  }

  return (
    <>
      <DocumentMeta
        title="AstroNumeric — Charts Desk"
        description="A live charts desk for natal chart, numerology, compatibility, and timing data built around the active profile."
      />

      <div className="experience-page">
        <motion.section
          className="experience-hero"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="experience-hero__copy">
            <span className="experience-label">Charts desk</span>
            <h1>Your birth chart, numerology, and compatibility — in one place.</h1>
            <p>
              Everything calculated from your active profile. Scroll to explore your natal chart, core numbers,
              relationship compatibility, and more.
            </p>

            <div className="experience-hero__actions">
              <a href="#chart-desk" className="experience-action experience-action--primary">
                Open chart desk
              </a>
              <Link to="/numerology" className="experience-action experience-action--secondary">
                Open numerology desk
              </Link>
              <a href="#compatibility-board" className="experience-action experience-action--secondary">
                Jump to compatibility
              </a>
            </div>

            <div className="experience-chip-row">
              {surfaceTags.map((tag) => (
                <span key={tag} className="experience-chip">
                  {tag}
                </span>
              ))}
            </div>

            {qualityNote && <p className="experience-status-note">{qualityNote}</p>}
            {issues.length > 0 && (
              <div className="experience-alert">
                <strong>Partial live data</strong>
                <p>{issues.join(' ')}</p>
              </div>
            )}
          </div>

          <div className="experience-hero__meta">
            <div className="experience-profile-card">
              <span className="experience-profile-card__eyebrow">{primarySourceLabel}</span>
              <strong>{primaryPayload.name}</strong>
              <p>
                {primaryPayload.date_of_birth} · {formatLocationLabel(primaryPayload)}
              </p>
              <div className="experience-profile-stats">
                <div className="experience-profile-stat">
                  <span>Sun</span>
                  <strong>{sunPlacement?.sign ?? '...'}</strong>
                </div>
                <div className="experience-profile-stat">
                  <span>Moon</span>
                  <strong>{moonPlacement?.sign ?? '...'}</strong>
                </div>
                <div className="experience-profile-stat">
                  <span>Life Path</span>
                  <strong>{numerologyProfile?.life_path.number ?? '...'}</strong>
                </div>
              </div>

              {hasPrimarySelectorOptions ? (
                <label className="experience-profile-selector">
                  <span className="experience-profile-selector__label">Drive route with</span>
                  <select
                    value={primarySelectorValue}
                    onChange={(event) => handlePrimaryProfileChange(event.target.value)}
                  >
                    {sessionPrimaryBackup.current && (
                      <option value="session">{`Session profile · ${sessionPrimaryBackup.current.name}`}</option>
                    )}
                    {profiles.map((profile) => (
                      <option key={profile.id} value={profile.id}>
                        {`${profile.name} (${profile.date_of_birth})`}
                      </option>
                    ))}
                  </select>
                </label>
              ) : (
                <div className="experience-profile-selector experience-profile-selector--empty">
                  <span className="experience-profile-selector__label">Drive route with</span>
                  <div className="experience-profile-selector__empty-state">
                    <span>{primaryPrompt}</span>
                    <Link to="/reading?compose=1" className="experience-inline-link">
                      Create live profile
                    </Link>
                  </div>
                </div>
              )}
            </div>

            <div className="experience-profile-card experience-profile-card--accent">
              <span className="experience-profile-card__eyebrow">{comparisonSourceLabel}</span>
              <strong>{comparisonProfile?.name ?? 'Select a second profile'}</strong>
              <p>
                {comparisonProfile
                  ? `Compatibility is using ${comparisonProfile.name} for the live pairing.`
                  : compatibilityPrompt}
              </p>

              {availableComparisonProfiles.length > 0 ? (
                <label className="experience-compare-selector">
                  <span className="experience-compare-selector__label">Compare with</span>
                  <select
                    value={compareProfileId ?? ''}
                    onChange={(event) =>
                      setCompareProfileId(
                        event.target.value ? Number(event.target.value) : null
                      )
                    }
                  >
                    <option value="">Choose a saved profile</option>
                    {availableComparisonProfiles.map((profile) => (
                      <option key={profile.id} value={profile.id}>
                        {`${profile.name} (${profile.date_of_birth})`}
                      </option>
                    ))}
                  </select>
                </label>
              ) : (
                <div className="experience-compare-selector experience-compare-selector--empty">
                  <span className="experience-compare-selector__label">Compare with</span>
                  <div className="experience-compare-selector__empty-state">
                    <span>Use the reading desk to add another real profile for live compatibility.</span>
                    <Link to="/reading?compose=1" className="experience-inline-link">
                      Add second profile
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.section>

        <section className="experience-signal-strip" aria-label="Product signal strip">
          {heroSignals.map((item) => (
            <article key={item.label} className="experience-signal-card">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
              <p>{item.note}</p>
            </article>
          ))}
        </section>

        <section className="experience-workflow-rail" aria-label="Charts workflows">
          {workflowLanes.map((lane) => (
            <Link
              key={`${lane.label}-${lane.href}`}
              to={lane.href}
              className={`experience-workflow-card experience-workflow-card--${lane.tone}`}
            >
              <span>{lane.label}</span>
              <strong>{lane.title}</strong>
              <p>{lane.note}</p>
              <div className="experience-workflow-card__meta">
                <span className="experience-workflow-card__status">{lane.status}</span>
                <span className="experience-workflow-card__jump">{lane.action}</span>
              </div>
            </Link>
          ))}
        </section>

        <section id="chart-desk" className="experience-section">
          <div className="experience-section__heading">
            <span className="experience-label">Chart desk</span>
            <h2>The chart page becomes a signal board you can scan in seconds instead of a floating cosmic toy.</h2>
            <p>The primary chart route should feel decisive, structured, and editorial before it feels mystical.</p>
          </div>

          <article className="experience-card experience-card--playbook">
            <div className="experience-card__header">
              <span>Chart playbook</span>
              <strong>How to use this desk</strong>
            </div>
            <div className="experience-playbook-steps">
              {chartPlaybook.map((step) => (
                <div key={step.label} className="experience-playbook-step">
                  <span>{step.label}</span>
                  <p>{step.detail}</p>
                </div>
              ))}
            </div>
          </article>

          <div className="experience-chart-grid">
            <article className="experience-card experience-card--chart">
              <div className="experience-card__header">
                <span>Birth chart desk</span>
                <strong>
                  {chartData ? 'Live natal signal map' : loading ? 'Loading natal data' : 'Natal feed unavailable'}
                </strong>
              </div>
              <div className="experience-chart-wheel-wrap">
                {chartData ? (
                  <ChartWheel chartData={chartData} size={420} interactive={false} />
                ) : (
                  <div className="experience-empty-state">
                    <strong>{loading ? 'Loading chart desk...' : 'Natal chart unavailable'}</strong>
                    <p>The chart wheel will appear here when the live natal payload resolves.</p>
                  </div>
                )}
              </div>
            </article>

            <article className="experience-card">
              <div className="experience-card__header">
                <span>Chart benchmark</span>
                <strong>Big Three + trust cues</strong>
              </div>

              <div className="experience-quality-stack">
                {chartQualityStates.map((item) => (
                  <div key={item.label} className={`experience-quality-banner experience-quality-banner--${item.tone}`}>
                    <span>{item.label}</span>
                    <p>{item.message}</p>
                  </div>
                ))}
              </div>

              <div className="experience-authority-grid">
                {chartAuthorityStats.map((item) => (
                  <div key={item.label} className="experience-authority-stat">
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                  </div>
                ))}
              </div>

              <div className="experience-big-three-grid">
                {bigThreeSignals.map((item) => (
                  <div key={item.label} className={`experience-big-three-card experience-big-three-card--${item.tone}`}>
                    <span>{item.label}</span>
                    <strong>{item.value}</strong>
                    <p>{item.reliability}</p>
                  </div>
                ))}
              </div>

              <div className="experience-insight-stack">
                {chartInsights.map((insight) => (
                  <div key={insight.label} className="experience-insight-item">
                    <h3>{insight.label}</h3>
                    <p>{insight.text}</p>
                  </div>
                ))}
              </div>
            </article>
          </div>
        </section>

        <section id="numerology-desk" className="experience-section">
          <div className="experience-section__heading">
            <span className="experience-label">Numerology desk</span>
            <h2>The numerology page can feel premium, structured, and genuinely useful.</h2>
            <p>The live numerology feed now decides the numbers, timing, and long-range arc on this route.</p>
          </div>

          <article className="experience-card experience-card--playbook">
            <div className="experience-card__header">
              <span>Numerology playbook</span>
              <strong>Use the desk like a timing surface</strong>
            </div>
            <div className="experience-playbook-steps">
              {numerologyPlaybook.map((step) => (
                <div key={step.label} className="experience-playbook-step">
                  <span>{step.label}</span>
                  <p>{step.detail}</p>
                </div>
              ))}
            </div>
          </article>

          <div className="experience-numerology-grid">
            <article className="experience-card experience-card--numerology-hero">
              <div className="experience-card__header">
                <span>Core numbers</span>
                <strong>
                  {numerologyProfile
                    ? `Life Path ${numerologyProfile.life_path.number}`
                    : loading
                      ? 'Loading numerology'
                      : 'Numerology unavailable'}
                </strong>
              </div>
              <div className="experience-number-grid">
                {[
                  ['Life Path', numerologyProfile?.life_path.number ?? '...'],
                  ['Destiny', numerologyProfile?.destiny_number ?? '...'],
                  ['Year', numerologyProfile?.personal_year.cycle_number ?? '...'],
                  ['Lucky set', numerologyProfile?.lucky_numbers.slice(0, 2).join(' · ') || '...'],
                ].map(([label, value]) => (
                  <div key={label} className="experience-number-chip">
                    <span>{label}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
              <p className="experience-muted-copy">
                {numerologyProfile?.synthesis?.summary ??
                  numerologyProfile?.life_path.meaning ??
                  'Your numerology summary will appear here once your profile is analyzed.'}
              </p>
            </article>

            <article className="experience-card">
              <div className="experience-card__header">
                <span>Current timing</span>
                <strong>
                  {numerologyProfile
                    ? `Personal Year ${numerologyProfile.personal_year.cycle_number}`
                    : 'Timing calculations'}
                </strong>
              </div>
              <div className="experience-cycle-list">
                <div>
                  <span>Personal Year</span>
                  <p>
                    {numerologyProfile?.personal_year.interpretation ??
                      'Year-level cycle guidance will appear here.'}
                  </p>
                </div>
                <div>
                  <span>Personal Month</span>
                  <p>
                    {numerologyProfile?.numerology_insights.personal_month ??
                      'Month-level live timing will appear here.'}
                  </p>
                </div>
                <div>
                  <span>Personal Day</span>
                  <p>
                    {numerologyProfile?.numerology_insights.personal_day ??
                      'Day-level live timing will appear here.'}
                  </p>
                </div>
              </div>
            </article>

            <article className="experience-card">
              <div className="experience-card__header">
                <span>Long-range arc</span>
                <strong>Pinnacles &amp; challenges</strong>
              </div>

              <div className="experience-pillars-grid">
                {numerologyProfile ? (
                  <>
                    {numerologyProfile.pinnacles.map((item, index) => (
                      <div key={`p-${item.number}-${index}`} className="experience-pillar">
                        <span>{`Pinnacle ${index + 1} · ${item.ages}`}</span>
                        <strong>{item.number}</strong>
                      </div>
                    ))}
                    {numerologyProfile.challenges.map((item, index) => (
                      <div
                        key={`c-${item.number}-${index}`}
                        className="experience-pillar experience-pillar--muted"
                      >
                        <span>{`Challenge ${index + 1} · ${item.ages}`}</span>
                        <strong>{item.number}</strong>
                      </div>
                    ))}
                  </>
                ) : (
                  <div className="experience-empty-state experience-empty-state--wide">
                    <strong>{loading ? 'Loading long-range arc...' : 'Numerology arc unavailable'}</strong>
                    <p>Pinnacles and challenges will render here when the live numerology response arrives.</p>
                  </div>
                )}
              </div>
            </article>

            <article className="experience-card experience-card--numerology-brief">
              <div className="experience-card__header">
                <span>Purpose brief</span>
                <strong>
                  {numerologyProfile
                    ? `Life Purpose ${numerologyProfile.life_path.number}`
                    : loading
                      ? 'Loading synthesis'
                      : 'Purpose + synthesis'}
                </strong>
              </div>

              {numerologyProfile ? (
                <>
                  <div className="experience-purpose-hero">
                    <strong>{lifePurposeLead ?? numerologyProfile.life_path.meaning}</strong>
                    <p>
                      {numerologyProfile.synthesis?.summary ??
                        numerologyProfile.life_path.meaning ??
                        numerologyProfile.destiny_interpretation}
                    </p>
                  </div>

                  {numerologyStrengths.length > 0 && (
                    <div className="experience-strength-pills">
                      {numerologyStrengths.map((item) => (
                        <span key={item} className="experience-strength-pill">
                          {item}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="experience-numerology-brief-grid">
                    <div className="experience-numerology-brief-block">
                      <span>Current focus</span>
                      <p>{numerologyCurrentFocus ?? 'The live synthesis will surface the current focus here.'}</p>
                    </div>
                    <div className="experience-numerology-brief-block">
                      <span>Growth edge</span>
                      <p>{numerologyGrowthEdge ?? 'The first practical growth edge will appear here once synthesis resolves.'}</p>
                    </div>
                    <div className="experience-numerology-brief-block experience-numerology-brief-block--accent">
                      <span>Affirmation</span>
                      <p>{numerologyAffirmation ?? 'The numerology affirmation will anchor this section once the live synthesis resolves.'}</p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="experience-empty-state experience-empty-state--wide">
                  <strong>{loading ? 'Loading purpose brief...' : 'Purpose brief unavailable'}</strong>
                  <p>The iOS benchmark leads with synthesis and life purpose, so that summary card will render here once the live numerology response arrives.</p>
                </div>
              )}
            </article>
          </div>
        </section>

        <section id="compatibility-board" className="experience-section">
          <div className="experience-section__heading">
            <span className="experience-label">Compatibility board</span>
            <h2>The compatibility page becomes editorial, comparative, and much easier to trust.</h2>
            <p>
              This board is now calculated from the active profile and the current comparison partner instead of a canned match score.
            </p>
          </div>

          <article className="experience-card experience-card--playbook">
            <div className="experience-card__header">
              <span>Compatibility playbook</span>
              <strong>Two-profile workflow</strong>
            </div>
            <div className="experience-playbook-steps">
              {compatibilityPlaybook.map((step) => (
                <div key={step.label} className="experience-playbook-step">
                  <span>{step.label}</span>
                  <p>{step.detail}</p>
                </div>
              ))}
            </div>
          </article>

          <div className="experience-compat-grid">
            {comparisonProfile ? (
              <>
                <article className="experience-card experience-card--compat-score">
                  <div className="experience-card__header">
                    <span>Overall read</span>
                    <strong>{overallTone}</strong>
                  </div>
                  <div
                    className="experience-score-circle"
                    style={{
                      background:
                        overallScore !== null
                          ? `radial-gradient(circle at center, rgba(10, 17, 28, 0.92) 52%, transparent 53%), conic-gradient(from 180deg, #39b8ff, #5383ff, #f6b45e ${overallScore}%, rgba(255, 255, 255, 0.08) 0)`
                          : undefined,
                    }}
                  >
                    <strong>{overallScore !== null ? `${overallScore}%` : '...'}</strong>
                  </div>
                  <p className="experience-muted-copy">
                    {compatibilityResult
                      ? compatibilityResult.recommendations[0] ?? compatibilityResult.summary
                      : compatibilityPrompt}
                  </p>
                </article>

                <article className="experience-card">
                  <div className="experience-card__header">
                    <span>Signal breakdown</span>
                    <strong>Topic by topic</strong>
                  </div>
                  <div className="experience-bars">
                    {compatibilityBreakdown.length > 0 ? (
                      compatibilityBreakdown.map((item) => {
                        const value = Math.round(item.score);

                        return (
                          <div key={item.name} className="experience-bar-row">
                            <div className="experience-bar-row__meta">
                              <span>{formatDimensionLabel(item.name)}</span>
                              <strong>{value}%</strong>
                            </div>
                            <div className="experience-bar-track">
                              <div className="experience-bar-fill" style={{ width: `${value}%` }} />
                            </div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="experience-empty-state experience-empty-state--wide">
                        <strong>
                          {loading ? 'Loading compatibility breakdown...' : 'Compatibility breakdown unavailable'}
                        </strong>
                        <p>The live dimension scores will render here when the pairing response arrives.</p>
                      </div>
                    )}
                  </div>
                </article>

                <article className="experience-card">
                  <div className="experience-card__header">
                    <span>What works</span>
                    <strong>Strengths &amp; friction</strong>
                  </div>
                  <div className="experience-list-grid">
                    <div>
                      <span className="experience-list-title">Strengths</span>
                      <ul>
                        {(
                          compatibilityResult?.strengths.length
                            ? compatibilityResult.strengths
                            : ['Live strengths will appear here once compatibility resolves.']
                        ).map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <span className="experience-list-title">Watch outs</span>
                      <ul>
                        {(
                          compatibilityResult?.challenges.length
                            ? compatibilityResult.challenges
                            : compatibilityResult?.recommendations.length
                              ? compatibilityResult.recommendations
                              : ['Live compatibility guidance will appear here once the pairing resolves.']
                        ).map((item) => (
                          <li key={item}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </article>
              </>
            ) : (
              <article className="experience-card experience-card--compat-setup">
                <div className="experience-card__header">
                  <span>Pairing setup</span>
                  <strong>Input state</strong>
                </div>

                <div className="experience-compat-setup-hero">
                  <strong>{compatibilitySetupHeadline}</strong>
                  <p>{compatibilityPrompt}</p>
                </div>

                <div className="experience-compat-setup-grid">
                  <div className="experience-compat-setup-block">
                    <span>Primary</span>
                    <strong>{primaryPayload.name}</strong>
                    <p>{primarySourceLabel}</p>
                  </div>
                  <div className="experience-compat-setup-block">
                    <span>Partner</span>
                    <strong>{availableComparisonProfiles.length > 0 ? 'Saved profiles available' : 'No saved partner yet'}</strong>
                    <p>
                      {availableComparisonProfiles.length > 0
                        ? 'Use the Compare with selector in the hero to choose the second profile.'
                        : 'Create one more profile in the reading desk to unlock live compatibility.'}
                    </p>
                    {availableComparisonProfiles.length === 0 && (
                      <Link to="/reading?compose=1" className="experience-inline-link">
                        Add second profile
                      </Link>
                    )}
                  </div>
                  <div className="experience-compat-setup-block experience-compat-setup-block--accent">
                    <span>When ready</span>
                    <strong>Live score + breakdown</strong>
                    <p>The board switches to score, topic breakdown, strengths, and watch-outs as soon as the pairing is set.</p>
                  </div>
                </div>

                <ol className="experience-compat-setup-list">
                  {compatibilitySetupSteps.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </article>
            )}
          </div>
        </section>
      </div>
    </>
  );
}

export default ProductExperienceView;
