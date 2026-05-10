import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  addJournalEntry,
  fetchJournalPatterns,
  fetchJournalPrompts,
  fetchJournalReadings,
  fetchJournalStats,
  recordOutcome,
} from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { toast } from '../components/Toast';
import { useActiveProfile } from '../hooks';
import { useStore } from '../store/useStore';
import type { JournalPrompt, JournalReading } from '../types';
import type { AnonReading } from '../utils/anonReadingStorage';
import { getAnonReadings } from '../utils/anonReadingStorage';
import {
  createLocalJournalDraft,
  getLocalJournalProfileKey,
  getLocalJournalRecords,
  saveLocalJournalEntry,
  saveLocalJournalOutcome,
  type LocalJournalOutcome,
} from '../utils/localJournalStorage';
import './ProductDesk.css';
import './JournalWorkspaceView.css';

type PromptScope = 'daily' | 'weekly' | 'monthly';
type JournalMode = 'local' | 'railway';

type JournalWorkspaceEntry = {
  id: string;
  readingId: string;
  scope: string;
  scopeLabel: string;
  formattedDate: string;
  contentSummary: string;
  journal: string;
  outcome: LocalJournalOutcome | null;
  updatedAt: string;
  isDraft: boolean;
  mode: JournalMode;
};

type JournalWorkspaceStats = {
  linkedReadings: number;
  journaledCount: number;
  ratedCount: number;
  accuracyRate: number | null;
  journalingStreak: number;
  message: string;
  insights: string[];
  patternHighlights: string[];
};

const promptScopeOptions: Array<{ id: PromptScope; label: string }> = [
  { id: 'daily', label: 'Daily' },
  { id: 'weekly', label: 'Weekly' },
  { id: 'monthly', label: 'Monthly' },
];

const outcomeOptions: Array<{ value: LocalJournalOutcome; label: string }> = [
  { value: 'yes', label: 'Yes' },
  { value: 'partial', label: 'Partial' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'no', label: 'No' },
];

const emptyStats: JournalWorkspaceStats = {
  linkedReadings: 0,
  journaledCount: 0,
  ratedCount: 0,
  accuracyRate: null,
  journalingStreak: 0,
  message: 'Run a reading and add a reflection to get started.',
  insights: [],
  patternHighlights: [],
};

function trimCopy(text: string, maxLength = 180) {
  return text.length <= maxLength ? text : `${text.slice(0, maxLength - 1).trimEnd()}...`;
}

function formatDateLabel(value: string) {
  const nextDate = new Date(value);

  if (Number.isNaN(nextDate.getTime())) {
    return value;
  }

  return nextDate.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatScopeLabel(scope: string) {
  switch (scope) {
    case 'daily':
      return 'Daily reading';
    case 'weekly':
      return 'Weekly reading';
    case 'monthly':
      return 'Monthly reading';
    case 'compatibility':
      return 'Compatibility note';
    case 'natal':
      return 'Natal note';
    case 'forecast':
      return 'Forecast note';
    case 'year-ahead':
      return 'Year-ahead note';
    case 'journal':
      return 'Open reflection';
    default:
      return scope.replace(/-/g, ' ').replace(/\b\w/g, (character) => character.toUpperCase());
  }
}

function normalizeOutcome(value: string | null | undefined): LocalJournalOutcome | null {
  if (value === 'yes' || value === 'no' || value === 'partial' || value === 'neutral') {
    return value;
  }

  return null;
}

function formatOutcomeLabel(outcome: LocalJournalOutcome | null) {
  if (!outcome) {
    return 'Not rated';
  }

  return outcome.replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatAccuracy(value: number) {
  return value <= 1 ? Math.round(value * 100) : Math.round(value);
}

function extractContentSummary(content: unknown) {
  if (!content || typeof content !== 'object') {
    return 'Reflection context is still empty for this entry.';
  }

  const record = content as Record<string, unknown>;
  const summary = record.summary;

  if (
    summary &&
    typeof summary === 'object' &&
    'headline' in summary &&
    typeof summary.headline === 'string'
  ) {
    return trimCopy(summary.headline);
  }

  if (typeof record.theme === 'string' && record.theme.trim()) {
    return trimCopy(record.theme);
  }

  if (typeof record.advice === 'string' && record.advice.trim()) {
    return trimCopy(record.advice);
  }

  if (Array.isArray(record.sections)) {
    const sectionWithText = record.sections.find(
      (section) =>
        section &&
        typeof section === 'object' &&
        ('title' in section || 'affirmation' in section || 'summary' in section)
    ) as Record<string, unknown> | undefined;

    if (sectionWithText) {
      if (typeof sectionWithText.title === 'string' && sectionWithText.title.trim()) {
        return trimCopy(sectionWithText.title);
      }

      if (typeof sectionWithText.summary === 'string' && sectionWithText.summary.trim()) {
        return trimCopy(sectionWithText.summary);
      }

      if (typeof sectionWithText.affirmation === 'string' && sectionWithText.affirmation.trim()) {
        return trimCopy(sectionWithText.affirmation);
      }
    }
  }

  return 'The reading exists, but its summary needs to be opened from the full output.';
}

function getProfileKeyFromReading(reading: AnonReading) {
  if (!reading.profile) {
    return null;
  }

  return getLocalJournalProfileKey({
    name: reading.profile.name,
    date_of_birth: reading.profile.date_of_birth,
    time_of_birth: reading.profile.time_of_birth,
    timezone: reading.profile.timezone,
  });
}

function buildDerivedStats(entries: JournalWorkspaceEntry[], mode: JournalMode): JournalWorkspaceStats {
  if (entries.length === 0) {
    return {
      ...emptyStats,
      message:
        mode === 'railway'
          ? 'Railway has not stored any journal-ready readings for this profile yet.'
          : 'This device has no journal-ready readings for the active profile yet.',
    };
  }

  const journaledCount = entries.filter((entry) => entry.journal.trim().length > 0).length;
  const ratedEntries = entries.filter((entry) => entry.outcome !== null);
  const ratedCount = ratedEntries.length;
  const yesCount = ratedEntries.filter((entry) => entry.outcome === 'yes').length;
  const partialCount = ratedEntries.filter((entry) => entry.outcome === 'partial').length;
  const noCount = ratedEntries.filter((entry) => entry.outcome === 'no').length;
  const neutralCount = ratedEntries.filter((entry) => entry.outcome === 'neutral').length;
  const accuracyRate =
    ratedCount > 0 ? Math.round((((yesCount + partialCount * 0.5) / ratedCount) * 100)) : null;

  const scopeTallies = entries.reduce<Record<string, number>>((totals, entry) => {
    totals[entry.scope] = (totals[entry.scope] ?? 0) + 1;
    return totals;
  }, {});
  const leadingScope = Object.entries(scopeTallies).sort((left, right) => right[1] - left[1])[0]?.[0] ?? null;

  const journalDays = Array.from(
    new Set(
      entries
        .filter((entry) => entry.journal.trim().length > 0)
        .map((entry) => entry.updatedAt.slice(0, 10))
        .sort((left, right) => right.localeCompare(left))
    )
  );
  let journalingStreak = 0;
  let cursor = new Date();

  while (journalDays.includes(cursor.toISOString().slice(0, 10))) {
    journalingStreak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }

  const weekdayTallies = entries.reduce<Record<string, number>>((totals, entry) => {
    const weekday = new Date(entry.updatedAt).toLocaleDateString(undefined, { weekday: 'long' });
    totals[weekday] = (totals[weekday] ?? 0) + 1;
    return totals;
  }, {});
  const topWeekday = Object.entries(weekdayTallies).sort((left, right) => right[1] - left[1])[0]?.[0] ?? null;
  const draftCount = entries.filter((entry) => entry.isDraft).length;

  const insights = [
    leadingScope ? `${formatScopeLabel(leadingScope)} is currently the heaviest reflection lane.` : null,
    journaledCount > 0 ? `${journaledCount} entries already have written reflection attached.` : 'Write one reflection to begin a visible journal habit.',
    draftCount > 0 ? `${draftCount} open drafts still need a finished note.` : null,
  ].filter((entry): entry is string => Boolean(entry));

  const patternHighlights = [
    topWeekday ? `${topWeekday} is currently the most active reflection day on this device.` : null,
    accuracyRate !== null ? `Outcome tracking is running at ${accuracyRate}% across ${ratedCount} rated entries.` : 'Record outcomes to turn this into an accountability desk.',
  ].filter((entry): entry is string => Boolean(entry));

  return {
    linkedReadings: entries.length,
    journaledCount,
    ratedCount,
    accuracyRate,
    journalingStreak,
    message:
      ratedCount > 0
        ? `${yesCount} yes, ${partialCount} partial, ${noCount} no, and ${neutralCount} neutral outcomes are logged for the active profile.`
        : 'No outcomes logged yet. Rate a reading to start tracking accuracy.',
    insights,
    patternHighlights,
  };
}

function buildRemoteStats(
  readings: JournalWorkspaceEntry[],
  statsResult?: Awaited<ReturnType<typeof fetchJournalStats>>,
  patternsResult?: Awaited<ReturnType<typeof fetchJournalPatterns>>
) {
  if (!statsResult) {
    return buildDerivedStats(readings, 'railway');
  }

  return {
    linkedReadings: statsResult.stats.total_readings,
    journaledCount: statsResult.insights.total_journals,
    ratedCount: statsResult.stats.rated_readings,
    accuracyRate: formatAccuracy(statsResult.stats.accuracy_rate),
    journalingStreak: statsResult.insights.journaling_streak,
    message: statsResult.stats.message,
    insights: statsResult.insights.insights.slice(0, 3),
    patternHighlights: patternsResult?.patterns.patterns_found
      ? patternsResult.patterns.patterns.slice(0, 3).map((pattern) => trimCopy(pattern.insight, 140))
      : patternsResult?.patterns.message
        ? [patternsResult.patterns.message]
        : [],
  } satisfies JournalWorkspaceStats;
}

function buildRemoteEntries(readings: JournalReading[]): JournalWorkspaceEntry[] {
  return [...readings]
    .map((reading) => ({
      id: `remote-${reading.id}`,
      readingId: String(reading.id),
      scope: reading.scope,
      scopeLabel: reading.scope_label || formatScopeLabel(reading.scope),
      formattedDate: reading.formatted_date || formatDateLabel(reading.date),
      contentSummary: trimCopy(reading.content_summary || 'Open this reading to add the first journal note.'),
      journal: reading.journal_full || '',
      outcome: normalizeOutcome(reading.feedback),
      updatedAt: reading.date,
      isDraft: false,
      mode: 'railway',
    }))
    .sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
}

function buildLocalEntries(readings: AnonReading[], profileKey: string): JournalWorkspaceEntry[] {
  const records = getLocalJournalRecords(profileKey);
  const readingsForProfile = readings.filter((reading) => getProfileKeyFromReading(reading) === profileKey);
  const readingIds = new Set(readingsForProfile.map((reading) => reading.id));
  const recordByReadingId = new Map(records.map((record) => [record.readingId, record]));

  const readingEntries = readingsForProfile.map((reading) => {
    const record = recordByReadingId.get(reading.id);

    return {
      id: record?.id ?? reading.id,
      readingId: reading.id,
      scope: reading.scope,
      scopeLabel: formatScopeLabel(reading.scope),
      formattedDate: formatDateLabel(reading.date),
      contentSummary: trimCopy(record?.contentSummary || extractContentSummary(reading.content)),
      journal: record?.journal ?? '',
      outcome: record?.outcome ?? null,
      updatedAt: record?.updatedAt ?? new Date(reading.timestamp).toISOString(),
      isDraft: false,
      mode: 'local',
    } satisfies JournalWorkspaceEntry;
  });

  const draftEntries = records
    .filter((record) => record.isDraft || !readingIds.has(record.readingId))
    .map((record) => ({
      id: record.id,
      readingId: record.readingId,
      scope: record.scope,
      scopeLabel: formatScopeLabel(record.scope),
      formattedDate: formatDateLabel(record.date),
      contentSummary: trimCopy(record.contentSummary),
      journal: record.journal,
      outcome: record.outcome,
      updatedAt: record.updatedAt,
      isDraft: record.isDraft,
      mode: 'local',
    })) satisfies JournalWorkspaceEntry[];

  return [...readingEntries, ...draftEntries].sort((left, right) =>
    right.updatedAt.localeCompare(left.updatedAt)
  );
}

export function JournalWorkspaceView() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();
  const { token } = useStore();

  const [promptScope, setPromptScope] = useState<PromptScope>('daily');
  const [prompts, setPrompts] = useState<JournalPrompt[]>([]);
  const [entries, setEntries] = useState<JournalWorkspaceEntry[]>([]);
  const [stats, setStats] = useState<JournalWorkspaceStats>(emptyStats);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);
  const [entryDraft, setEntryDraft] = useState('');
  const [outcomeDraft, setOutcomeDraft] = useState<LocalJournalOutcome>('neutral');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dataIssues, setDataIssues] = useState<string[]>([]);
  const [promptIssue, setPromptIssue] = useState<string | null>(null);

  const journalMode: JournalMode = token && activeProfile && activeProfile.id > 0 ? 'railway' : 'local';
  const profileKey = useMemo(
    () => (activeProfile ? getLocalJournalProfileKey(activeProfile) : null),
    [activeProfile]
  );
  const selectedEntry = useMemo(
    () => entries.find((entry) => entry.id === selectedEntryId) ?? null,
    [entries, selectedEntryId]
  );
  const wordCount = useMemo(() => {
    const trimmed = entryDraft.trim();
    return trimmed ? trimmed.split(/\s+/).length : 0;
  }, [entryDraft]);

  const commitWorkspaceState = useCallback(
    (
      nextEntries: JournalWorkspaceEntry[],
      nextStats: JournalWorkspaceStats,
      nextIssues: string[],
      preferredSelection?: string
    ) => {
      setEntries(nextEntries);
      setStats(nextStats);
      setDataIssues(nextIssues);
      setSelectedEntryId((current) => {
        const nextSelected =
          nextEntries.find(
            (entry) => entry.id === preferredSelection || entry.readingId === preferredSelection
          ) ?? nextEntries.find((entry) => entry.id === current) ?? nextEntries[0] ?? null;

        return nextSelected?.id ?? null;
      });
    },
    []
  );

  const loadWorkspace = useCallback(
    async (preferredSelection?: string) => {
      if (!activeProfile) {
        commitWorkspaceState([], emptyStats, [], preferredSelection);
        setLoading(false);
        return;
      }

      setLoading(true);

      if (journalMode === 'local') {
        const localEntries = buildLocalEntries(getAnonReadings(), profileKey ?? '');
        const localStats = buildDerivedStats(localEntries, 'local');
        commitWorkspaceState(localEntries, localStats, [], preferredSelection);
        setLoading(false);
        return;
      }

      const nextIssues: string[] = [];
      const [readingsResult, statsResult, patternsResult] = await Promise.allSettled([
        fetchJournalReadings(activeProfile.id, token as string),
        fetchJournalStats(activeProfile.id, token as string),
        fetchJournalPatterns(activeProfile.id, token as string),
      ]);

      const remoteEntries =
        readingsResult.status === 'fulfilled' ? buildRemoteEntries(readingsResult.value.readings) : [];

      if (readingsResult.status === 'rejected') {
        nextIssues.push('Railway could not load journal readings for this profile.');
      }

      if (statsResult.status === 'rejected') {
        nextIssues.push('Railway could not load journal accountability stats.');
      }

      if (patternsResult.status === 'rejected') {
        nextIssues.push('Railway could not load reflection patterns for this profile.');
      }

      const remoteStats = buildRemoteStats(
        remoteEntries,
        statsResult.status === 'fulfilled' ? statsResult.value : undefined,
        patternsResult.status === 'fulfilled' ? patternsResult.value : undefined
      );

      commitWorkspaceState(remoteEntries, remoteStats, nextIssues, preferredSelection);
      setLoading(false);
    },
    [activeProfile, commitWorkspaceState, journalMode, profileKey, token]
  );

  useEffect(() => {
    void loadWorkspace();
  }, [loadWorkspace]);

  useEffect(() => {
    let isCancelled = false;

    async function loadPrompts() {
      try {
        const response = await fetchJournalPrompts(promptScope);

        if (!isCancelled) {
          setPrompts(response.prompts);
          setPromptIssue(null);
        }
      } catch {
        if (!isCancelled) {
          setPrompts([]);
          setPromptIssue('Reflection prompts could not load right now.');
        }
      }
    }

    void loadPrompts();

    return () => {
      isCancelled = true;
    };
  }, [promptScope]);

  useEffect(() => {
    if (!selectedEntry) {
      setEntryDraft('');
      setOutcomeDraft('neutral');
      return;
    }

    setEntryDraft(selectedEntry.journal);
    setOutcomeDraft(selectedEntry.outcome ?? 'neutral');
  }, [selectedEntry]);

  async function handleCreateDraft() {
    if (!profileKey) {
      return;
    }

    const draftRecord = createLocalJournalDraft(profileKey, {
      title: `${activeProfile?.name ?? 'Profile'} reflection`,
      contentSummary: 'Capture what landed, what missed, and what needs a follow-through note.',
    });

    await loadWorkspace(draftRecord.readingId);
  }

  async function handleSave() {
    if (!selectedEntry || !activeProfile) {
      return;
    }

    setSaving(true);

    try {
      if (journalMode === 'railway') {
        const readingId = Number(selectedEntry.readingId);

        if (!Number.isFinite(readingId)) {
          throw new Error('The selected Railway journal entry is missing a valid reading id.');
        }

        await addJournalEntry({ reading_id: readingId, entry: entryDraft.trim() }, token as string);
        await recordOutcome({ reading_id: readingId, outcome: outcomeDraft }, token as string);
        toast.success('Journal entry saved to Railway');
      } else if (profileKey) {
        const context = {
          scope: selectedEntry.scope,
          date: selectedEntry.updatedAt,
          title: selectedEntry.scopeLabel,
          contentSummary: selectedEntry.contentSummary,
        };

        saveLocalJournalEntry(profileKey, selectedEntry.readingId, context, entryDraft.trim());
        saveLocalJournalOutcome(profileKey, selectedEntry.readingId, context, outcomeDraft);
        toast.success('Journal entry saved on this device');
      }

      await loadWorkspace(selectedEntry.readingId);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Journal save failed.';
      toast.error(message);
    } finally {
      setSaving(false);
    }
  }

  const deskModeLabel =
    journalMode === 'railway' ? 'Railway journal' : hasActiveProfile ? 'Device journal' : 'No active profile';
  const modeNote = !activeProfile
    ? 'Create or select a profile in the reading desk before this workspace can tie reflections to a real person.'
    : journalMode === 'railway'
      ? 'Readings and reflections sync across your devices.'  
      : 'Your readings and reflections are saved on this device.';
  const nextMoveCopy = !activeProfile
    ? 'Start at the reading desk, then come back here once the active profile exists.'
    : journalMode === 'railway'
      ? 'Rate outcomes after each forecast to build your accuracy record.'
      : 'Run a reading and add a note to start your journal.';

  return (
    <div className="product-desk journal-workspace">
      <DocumentMeta
        title="AstroNumeric — Journal Workspace"
        description="Review saved readings, capture reflections, and track forecast accuracy over time."
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Journal workspace</span>
        <h1>Readings, reflections, and outcome tracking.</h1>
        <p>
          Log what happened after each reading, track accuracy over time, and carry
          follow-through forward.
        </p>
        <div className="product-desk__chips">
          <span className="product-desk__chip">Reflection prompts</span>
          <span className="product-desk__chip">Outcome tracking</span>
          <span className="product-desk__chip">Local and Railway modes</span>
          <span className="product-desk__chip">Reusable reading queue</span>
        </div>
        <div className="product-desk__actions">
          <Link to="/reading" className="btn-primary product-desk__action">
            Open reading desk
          </Link>
          {journalMode === 'local' && hasActiveProfile ? (
            <button type="button" className="btn-secondary product-desk__action" onClick={handleCreateDraft}>
              Create local draft
            </button>
          ) : null}
          <Link to="/profile" className="btn-secondary product-desk__action">
            Check profile state
          </Link>
        </div>
      </section>

      {dataIssues.length > 0 ? (
        <div className="journal-workspace__alert" role="status">
          <strong>Partial journal data</strong>
          <p>{dataIssues.join(' ')}</p>
        </div>
      ) : null}

      <section className="product-desk__grid">
        <article className="product-desk__panel">
          <h2>Current context</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Active profile</span>
              <span className="product-desk__value">
                {activeProfile?.name ?? 'Waiting for profile input'}
              </span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Profile source</span>
              <span className="product-desk__value">{hasActiveProfile ? activeProfileSourceLabel : 'No active profile'}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Journal mode</span>
              <span className="product-desk__value">{deskModeLabel}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Linked readings</span>
              <span className="product-desk__value">{loading ? 'Loading...' : stats.linkedReadings}</span>
            </div>
          </div>
          <p className="product-desk__note">{modeNote}</p>
        </article>

        <article className="product-desk__panel">
          <h2>Reflection prompts</h2>
          <div className="journal-workspace__prompt-tabs" role="tablist" aria-label="Prompt scopes">
            {promptScopeOptions.map((scope) => (
              <button
                key={scope.id}
                type="button"
                className={
                  promptScope === scope.id
                    ? 'journal-workspace__prompt-tab journal-workspace__prompt-tab--active'
                    : 'journal-workspace__prompt-tab'
                }
                onClick={() => setPromptScope(scope.id)}
              >
                {scope.label}
              </button>
            ))}
          </div>
          {promptIssue ? <p className="product-desk__note">{promptIssue}</p> : null}
          <ul className="product-desk__list">
            {prompts.map((prompt) => (
              <li key={`${prompt.category}-${prompt.text}`} className="product-desk__list-item">
                <div>
                  <strong>{prompt.text}</strong>
                  <span className="product-desk__meta">{prompt.category}</span>
                </div>
              </li>
            ))}
          </ul>
        </article>

        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Accountability snapshot</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Journaled</span>
              <span className="product-desk__value">{loading ? 'Loading...' : stats.journaledCount}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Rated outcomes</span>
              <span className="product-desk__value">{loading ? 'Loading...' : stats.ratedCount}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Accuracy signal</span>
              <span className="product-desk__value">
                {loading ? 'Loading...' : stats.accuracyRate !== null ? `${stats.accuracyRate}%` : 'Pending'}
              </span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Journal streak</span>
              <span className="product-desk__value">{loading ? 'Loading...' : stats.journalingStreak}</span>
            </div>
          </div>
          <p className="product-desk__note">{stats.message}</p>
          <div className="journal-workspace__insight-columns">
            <div>
              <span className="product-desk__label">Insights</span>
              <ul className="product-desk__list">
                {stats.insights.length > 0 ? (
                  stats.insights.map((insight) => (
                    <li key={insight} className="product-desk__list-item">
                      <div>
                        <strong>{insight}</strong>
                      </div>
                    </li>
                  ))
                ) : (
                  <li className="product-desk__list-item">
                    <div>
                      <strong>Insights will appear once the workspace has more material to compare.</strong>
                    </div>
                  </li>
                )}
              </ul>
            </div>
            <div>
              <span className="product-desk__label">Pattern highlights</span>
              <ul className="product-desk__list">
                {stats.patternHighlights.length > 0 ? (
                  stats.patternHighlights.map((highlight) => (
                    <li key={highlight} className="product-desk__list-item">
                      <div>
                        <strong>{highlight}</strong>
                      </div>
                    </li>
                  ))
                ) : (
                  <li className="product-desk__list-item">
                    <div>
                      <strong>Patterns need a few saved outcomes before they can say anything reliable.</strong>
                    </div>
                  </li>
                )}
              </ul>
            </div>
          </div>
        </article>

        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Journal queue</h2>
          {entries.length > 0 ? (
            <div className="journal-workspace__entry-list">
              {entries.map((entry) => (
                <button
                  key={entry.id}
                  type="button"
                  className={
                    entry.id === selectedEntryId
                      ? 'journal-workspace__entry journal-workspace__entry--active'
                      : 'journal-workspace__entry'
                  }
                  onClick={() => setSelectedEntryId(entry.id)}
                >
                  <div className="journal-workspace__entry-row">
                    <strong>{entry.scopeLabel}</strong>
                    <span>{entry.formattedDate}</span>
                  </div>
                  <p>{entry.contentSummary}</p>
                  <div className="journal-workspace__entry-row journal-workspace__entry-row--status">
                    <span className="product-desk__badge">{entry.isDraft ? 'Draft' : formatOutcomeLabel(entry.outcome)}</span>
                    <span>{entry.mode === 'railway' ? 'Railway-backed' : 'Device-local'}</span>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="product-desk__empty">
              {loading
                ? 'Loading the journal queue for this profile.'
                : hasActiveProfile
                  ? 'Run a reading first or create a local draft so this workspace has something to revisit.'
                  : 'Create a profile in the reading desk first, then this queue can bind to real readings.'}
            </div>
          )}
        </article>

        <article className="product-desk__panel journal-workspace__editor-panel">
          <h2>Entry editor</h2>
          {selectedEntry ? (
            <div className="journal-workspace__editor">
              <div className="journal-workspace__editor-header">
                <div>
                  <strong>{selectedEntry.scopeLabel}</strong>
                  <p className="product-desk__note">{selectedEntry.formattedDate}</p>
                </div>
                <span className="product-desk__badge">
                  {selectedEntry.mode === 'railway' ? 'Railway-backed' : 'Device-local'}
                </span>
              </div>
              <p className="journal-workspace__summary">{selectedEntry.contentSummary}</p>
              <div className="journal-workspace__outcomes" aria-label="Outcome selector">
                {outcomeOptions.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={
                      outcomeDraft === option.value
                        ? 'journal-workspace__outcome journal-workspace__outcome--active'
                        : 'journal-workspace__outcome'
                    }
                    onClick={() => setOutcomeDraft(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              <label className="journal-workspace__textarea-label" htmlFor="journal-entry-textarea">
                Reflection
              </label>
              <textarea
                id="journal-entry-textarea"
                className="journal-workspace__textarea"
                value={entryDraft}
                onChange={(event) => setEntryDraft(event.target.value)}
                placeholder="Write what actually happened, what matched the reading, and what changed your mind."
              />
              <div className="journal-workspace__editor-footer">
                <span>{wordCount} words</span>
                <button type="button" className="btn-primary" disabled={saving} onClick={handleSave}>
                  {saving
                    ? 'Saving...'
                    : selectedEntry.mode === 'railway'
                      ? 'Save to Railway'
                      : 'Save on this device'}
                </button>
              </div>
            </div>
          ) : (
            <p className="product-desk__note">
              Pick an entry from the queue to start writing, or create a local draft if the workspace is running in device mode.
            </p>
          )}
        </article>

        <article className="product-desk__panel">
          <h2>Next move</h2>
          <p className="product-desk__note">{nextMoveCopy}</p>
          <div className="product-desk__actions">
            <Link to="/reading" className="btn-primary product-desk__action">
              Run another reading
            </Link>
            <Link to="/charts" className="btn-secondary product-desk__action">
              Return to charts
            </Link>
          </div>
        </article>
      </section>
    </div>
  );
}

export default JournalWorkspaceView;