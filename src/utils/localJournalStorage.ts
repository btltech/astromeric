import type { SavedProfile } from '../types';

export type LocalJournalOutcome = 'yes' | 'no' | 'partial' | 'neutral';

export interface LocalJournalRecord {
  id: string;
  profileKey: string;
  readingId: string;
  scope: string;
  date: string;
  title: string;
  contentSummary: string;
  journal: string;
  outcome: LocalJournalOutcome | null;
  updatedAt: string;
  isDraft: boolean;
}

export interface LocalJournalDraftInput {
  scope?: string;
  date?: string;
  title?: string;
  contentSummary?: string;
}

const STORAGE_KEY = 'astromeric_local_journal_records';

function readRecords() {
  if (typeof window === 'undefined') {
    return [] as LocalJournalRecord[];
  }

  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored ? (JSON.parse(stored) as LocalJournalRecord[]) : [];
  } catch {
    return [] as LocalJournalRecord[];
  }
}

function writeRecords(records: LocalJournalRecord[]) {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
}

function makeTimestamp() {
  return new Date().toISOString();
}

function makeRecordId(prefix: string) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function getLocalJournalProfileKey(
  profile:
    | SavedProfile
    | Pick<SavedProfile, 'name' | 'date_of_birth' | 'time_of_birth' | 'timezone'>
) {
  return [
    profile.name.trim().toLowerCase(),
    profile.date_of_birth,
    profile.time_of_birth ?? '',
    profile.timezone ?? '',
  ].join('::');
}

export function getLocalJournalRecords(profileKey: string) {
  return readRecords()
    .filter((record) => record.profileKey === profileKey)
    .sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
}

export function getLocalJournalRecord(profileKey: string, readingId: string) {
  return readRecords().find(
    (record) => record.profileKey === profileKey && record.readingId === readingId
  );
}

export function saveLocalJournalEntry(
  profileKey: string,
  readingId: string,
  context: Pick<LocalJournalRecord, 'scope' | 'date' | 'title' | 'contentSummary'>,
  journal: string
) {
  const records = readRecords();
  const now = makeTimestamp();
  const existingIndex = records.findIndex(
    (record) => record.profileKey === profileKey && record.readingId === readingId
  );

  if (existingIndex >= 0) {
    records[existingIndex] = {
      ...records[existingIndex],
      ...context,
      journal,
      updatedAt: now,
      isDraft: false,
    };
    writeRecords(records);
    return records[existingIndex];
  }

  const nextRecord: LocalJournalRecord = {
    id: makeRecordId('journal'),
    profileKey,
    readingId,
    scope: context.scope,
    date: context.date,
    title: context.title,
    contentSummary: context.contentSummary,
    journal,
    outcome: null,
    updatedAt: now,
    isDraft: false,
  };

  records.push(nextRecord);
  writeRecords(records);
  return nextRecord;
}

export function saveLocalJournalOutcome(
  profileKey: string,
  readingId: string,
  context: Pick<LocalJournalRecord, 'scope' | 'date' | 'title' | 'contentSummary'>,
  outcome: LocalJournalOutcome
) {
  const records = readRecords();
  const now = makeTimestamp();
  const existingIndex = records.findIndex(
    (record) => record.profileKey === profileKey && record.readingId === readingId
  );

  if (existingIndex >= 0) {
    records[existingIndex] = {
      ...records[existingIndex],
      ...context,
      outcome,
      updatedAt: now,
    };
    writeRecords(records);
    return records[existingIndex];
  }

  const nextRecord: LocalJournalRecord = {
    id: makeRecordId('journal'),
    profileKey,
    readingId,
    scope: context.scope,
    date: context.date,
    title: context.title,
    contentSummary: context.contentSummary,
    journal: '',
    outcome,
    updatedAt: now,
    isDraft: false,
  };

  records.push(nextRecord);
  writeRecords(records);
  return nextRecord;
}

export function createLocalJournalDraft(profileKey: string, input: LocalJournalDraftInput = {}) {
  const records = readRecords();
  const now = makeTimestamp();
  const nextRecord: LocalJournalRecord = {
    id: makeRecordId('draft'),
    profileKey,
    readingId: makeRecordId('draft-reading'),
    scope: input.scope ?? 'journal',
    date: input.date ?? now,
    title: input.title ?? 'Open reflection',
    contentSummary: input.contentSummary ?? 'A blank local journal draft for free-form reflection.',
    journal: '',
    outcome: null,
    updatedAt: now,
    isDraft: true,
  };

  records.push(nextRecord);
  writeRecords(records);
  return nextRecord;
}