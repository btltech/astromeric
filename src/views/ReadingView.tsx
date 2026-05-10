import React, { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import type { ProfilePayload } from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { FortuneForm } from '../components/FortuneForm';
import { FortuneResult } from '../components/FortuneResult';
import { ProfileSelector } from '../components/ProfileSelector';
import { WeeklyVibe } from '../components/WeeklyVibe';
import { useAnonReadings, useAuth, useMigrateReadings, useProfiles, useReading } from '../hooks';
import { useStore } from '../store/useStore';
import type { NewProfileForm, SavedProfile } from '../types';
import './ReadingView.css';

const scopeOptions = [
  { id: 'daily', label: 'Daily' },
  { id: 'weekly', label: 'Weekly' },
  { id: 'monthly', label: 'Monthly' },
] as const;

function formatRecentDate(date: string) {
  return new Date(date).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
  });
}

function formatProfileMeta(profile: SavedProfile) {
  const bits = [profile.date_of_birth];

  if (profile.time_of_birth) {
    bits.push(profile.time_of_birth);
  }

  if (profile.place_of_birth) {
    bits.push(profile.place_of_birth);
  } else if (profile.timezone) {
    bits.push(profile.timezone);
  }

  return bits.join(' · ');
}

function toProfilePayload(profile: SavedProfile): ProfilePayload {
  return {
    name: profile.name,
    date_of_birth: profile.date_of_birth,
    time_of_birth: profile.time_of_birth ?? undefined,
    place_of_birth: profile.place_of_birth ?? undefined,
    location: {
      latitude: profile.latitude ?? undefined,
      longitude: profile.longitude ?? undefined,
      timezone: profile.timezone ?? undefined,
    },
    house_system: profile.house_system ?? undefined,
  };
}

interface AccountMessage {
  tone: 'success' | 'error' | 'info';
  text: string;
}

function getScopePreview(scope: 'daily' | 'weekly' | 'monthly') {
  if (scope === 'weekly') {
    return 'Week pacing, strongest day, and lighter windows load into the result stack.';
  }

  if (scope === 'monthly') {
    return 'Longer-range themes, pressure points, and guidance load into the result stack.';
  }

  return 'Fast forecast, action signals, and follow-up prompts load into the result stack.';
}

export function ReadingView() {
  const [searchParams] = useSearchParams();
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authAction, setAuthAction] = useState<'login' | 'register' | 'sync' | null>(null);
  const [accountMessage, setAccountMessage] = useState<AccountMessage | null>(null);
  const {
    loading,
    error,
    showCreateForm,
    setShowCreateForm,
    allowCloudHistory,
    setAllowCloudHistory,
    token,
    updateStreak,
    streakCount,
  } = useStore();
  const {
    profiles,
    selectedProfile,
    selectedProfileId,
    createProfile,
    sessionProfile,
    setSelectedProfileId,
    suppressNextAutoFetch,
    clearAutoFetchSuppression,
    fetchProfiles,
  } = useProfiles();
  const { selectedScope, result, setSelectedScope, setResult, getPrediction } = useReading();
  const { readings, readingCount, saveReading, refreshReadings } = useAnonReadings();
  const { user, isAuthenticated, login, register, logout } = useAuth();
  const { migrateReadings } = useMigrateReadings();

  useEffect(() => {
    updateStreak();
  }, [updateStreak]);

  useEffect(() => {
    if (searchParams.get('compose') === '1') {
      setShowCreateForm(true);
      setResult(null);
    }
  }, [searchParams, setResult, setShowCreateForm]);

  const recentReadings = useMemo(() => [...readings].slice(-3).reverse(), [readings]);
  const latestLocalReading = recentReadings[0] ?? null;
  const activeProfileLabel = selectedProfile ? formatProfileMeta(selectedProfile) : 'No active profile yet';
  const profileStorageLabel = useMemo(() => {
    if (!selectedProfile) {
      return null;
    }

    if (sessionProfile) {
      return 'Browser session';
    }

    return selectedProfile.id < 0 ? 'Saved on this device' : 'Railway profile';
  }, [selectedProfile, sessionProfile]);
  const selectedProfileFacts = useMemo(() => {
    if (!selectedProfile) {
      return [];
    }

    return [
      {
        label: 'Birth date',
        value: selectedProfile.date_of_birth,
      },
      {
        label: 'Birth time',
        value: selectedProfile.time_of_birth || 'Not added',
      },
      {
        label: 'Birth place',
        value: selectedProfile.place_of_birth || selectedProfile.timezone || 'Add a location for chart timing',
      },
    ];
  }, [selectedProfile]);
  const profilePersistenceNote = useMemo(() => {
    if (!selectedProfile) {
      return 'Session-only profiles now survive reloads in this browser session. Save them on this device if you want them queued for Railway sync.';
    }

    if (sessionProfile) {
      return 'This browser-session profile survives reloads here, but Railway sync ignores it until you save it on this device.';
    }

    if (selectedProfile.id < 0) {
      return isAuthenticated
        ? 'This profile is saved on this device and is ready to move into Railway the next time you sync.'
        : 'This profile is saved on this device and will be ready to sync once you connect Railway.';
    }

    return 'This profile already belongs to your Railway account and can follow you across devices.';
  }, [isAuthenticated, selectedProfile, sessionProfile]);
  const profileReadinessNote = useMemo(() => {
    if (!selectedProfile) {
      return null;
    }

    if (!selectedProfile.place_of_birth) {
      return 'This profile is usable for quick readings, but add a birth place before leaning on chart timing or location-aware desks.';
    }

    if (!selectedProfile.time_of_birth) {
      return 'Birth place is locked in. Add birth time later if you want sharper house placement and timing views.';
    }

    return 'This profile is complete enough for the reading desk, chart views, and deeper timing surfaces.';
  }, [selectedProfile]);
  const weeklyVibeProfile = useMemo(
    () => (selectedProfile ? toProfilePayload(selectedProfile) : null),
    [selectedProfile]
  );
  const cloudHistoryEnabled = Boolean(token) && allowCloudHistory;
  const localProfileCount = useMemo(
    () => profiles.filter((profile) => profile.id < 0).length,
    [profiles]
  );
  const hasPendingRailwaySync = localProfileCount > 0 || readingCount > 0;
  const accountPreviewCopy = useMemo(() => {
    if (hasPendingRailwaySync) {
      const base = `${localProfileCount} local profiles and ${readingCount} local readings are currently waiting on this device.`;

      return sessionProfile
        ? `${base} The active profile is still browser-session only until you save it on this device.`
        : base;
    }

    if (sessionProfile) {
      return 'The active profile is browser-session only for now. Save it on this device before expecting Railway sync or cross-device access.';
    }

    return 'Sign in to keep your profiles and readings across devices.';
  }, [hasPendingRailwaySync, localProfileCount, readingCount, sessionProfile]);
  const connectedAccountCopy = useMemo(() => {
    if (hasPendingRailwaySync) {
      const base = `${localProfileCount} local profiles and ${readingCount} local readings are ready to move into Railway.`;

      return sessionProfile
        ? `${base} The active profile is still browser-session only until you save it on this device.`
        : base;
    }

    if (sessionProfile) {
      return 'Railway cloud sync is active, but the active profile is still browser-session only until you save it on this device.';
    }

    return 'Railway cloud sync is active. New saved profiles and cloud-history readings now target the backend.';
  }, [hasPendingRailwaySync, localProfileCount, readingCount, sessionProfile]);
  const connectedAccountNote = useMemo(() => {
    if (sessionProfile) {
      return hasPendingRailwaySync
        ? 'Sync now to move device-local readings into Railway. The active browser-session profile itself still needs a saved copy.'
        : 'Cloud history is active, but the active browser-session profile still needs a saved copy before it can move into Railway.';
    }

    if (hasPendingRailwaySync) {
      return 'Sync now to move device-local profiles and readings into your Railway account.';
    }

    return allowCloudHistory
      ? 'Cloud history is active, so future saved readings can go straight to Railway.'
      : 'Cloud history is off, so future readings stay local until you switch it back on in the profile panel.';
  }, [allowCloudHistory, hasPendingRailwaySync, sessionProfile]);
  const trimmedAuthEmail = authEmail.trim();
  const trimmedAuthPassword = authPassword.trim();
  const authEmailIsValid =
    trimmedAuthEmail.length === 0 || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedAuthEmail);
  const canSubmitAuth =
    trimmedAuthEmail.length > 0 && trimmedAuthPassword.length > 0 && authEmailIsValid && authAction === null;
  const accountStats = useMemo(() => {
    if (isAuthenticated) {
      return [
        {
          label: 'Local profiles',
          value: String(localProfileCount),
          detail: localProfileCount ? 'ready to migrate' : 'already clear',
        },
        {
          label: 'Local readings',
          value: String(readingCount),
          detail: readingCount ? 'ready to migrate' : 'already clear',
        },
        {
          label: 'Cloud history',
          value: allowCloudHistory ? 'On' : 'Off',
          detail: allowCloudHistory ? 'future saves can target Railway' : 'future saves stay local',
        },
      ];
    }

    return [
      {
        label: 'Local profiles',
        value: String(localProfileCount),
        detail: localProfileCount ? 'waiting on this device' : 'none queued yet',
      },
      {
        label: 'Local readings',
        value: String(readingCount),
        detail: readingCount ? 'waiting on this device' : 'none queued yet',
      },
      {
        label: 'After connect',
        value: 'Cloud',
        detail: 'future saved readings can target Railway',
      },
    ];
  }, [allowCloudHistory, isAuthenticated, localProfileCount, readingCount]);

  async function storeAnonymousReading(profile: SavedProfile, date: string, content: unknown) {
    saveReading({
      scope: selectedScope,
      date,
      profile: {
        name: profile.name,
        date_of_birth: profile.date_of_birth,
        time_of_birth: profile.time_of_birth ?? undefined,
        timezone: profile.timezone ?? undefined,
      },
      content,
    });
  }

  async function runReadingForProfile(profile: SavedProfile) {
    const data = await getPrediction(profile.id, profile);

    if (data && (!cloudHistoryEnabled || profile.id < 0)) {
      await storeAnonymousReading(profile, data.date, data);
    }
  }

  async function handleProfileCreate(formData: NewProfileForm) {
    try {
      const nextProfile = await createProfile(formData);
      setShowCreateForm(false);
      setResult(null);
      await runReadingForProfile(nextProfile);
    } catch {
      // Store and toast already carry the actionable error state.
    }
  }

  async function handleGenerateReading() {
    if (!selectedProfile) {
      setShowCreateForm(true);
      return;
    }

    try {
      await runReadingForProfile(selectedProfile);
    } catch {
      // Store and toast already carry the actionable error state.
    }
  }

  function handleSelectProfile(id: number) {
    setSelectedProfileId(id);
    setShowCreateForm(false);
    setResult(null);
  }

  function handleReset() {
    setResult(null);
  }

  async function handleAuthSubmit(mode: 'login' | 'register') {
    if (!trimmedAuthEmail || !trimmedAuthPassword) {
      setAccountMessage({
        tone: 'error',
        text: 'Email and password are required to sign in.',
      });
      return;
    }

    if (!authEmailIsValid) {
      setAccountMessage({
        tone: 'error',
        text: 'Enter a valid email address.',
      });
      return;
    }

    setAuthAction(mode);
    setAccountMessage(null);

    try {
      suppressNextAutoFetch();

      if (mode === 'login') {
        await login(trimmedAuthEmail, trimmedAuthPassword);
      } else {
        await register(trimmedAuthEmail, trimmedAuthPassword);
      }

      const syncResult = await migrateReadings();
      refreshReadings();
      await fetchProfiles({ force: true });
      setAllowCloudHistory(true);
      setAuthPassword('');

      setAccountMessage(
        syncResult.migratedProfileCount || syncResult.migratedReadingCount
          ? {
              tone: 'success',
              text: `Railway sync complete: ${syncResult.migratedProfileCount} profiles and ${syncResult.migratedReadingCount} readings migrated.`,
            }
          : {
              tone: 'success',
              text: 'Connected to the Railway backend. Cloud history is ready for future readings.',
            }
      );
    } catch (authError) {
        clearAutoFetchSuppression();
      const message = authError instanceof Error ? authError.message : 'Account connection failed.';
      setAccountMessage({ tone: 'error', text: message });
    } finally {
      setAuthAction(null);
    }
  }

  async function handleRailwaySync() {
    setAuthAction('sync');
    setAccountMessage(null);

    try {
      const syncResult = await migrateReadings();
      refreshReadings();
      await fetchProfiles({ force: true });
      setAccountMessage(
        syncResult.migratedProfileCount || syncResult.migratedReadingCount
          ? {
              tone: 'success',
              text: `Railway sync complete: ${syncResult.migratedProfileCount} profiles and ${syncResult.migratedReadingCount} readings migrated.`,
            }
          : {
              tone: 'info',
              text: 'Railway is already in sync with local device data.',
            }
      );
    } catch (syncError) {
      const message = syncError instanceof Error ? syncError.message : 'Railway sync failed.';
      setAccountMessage({ tone: 'error', text: message });
    } finally {
      setAuthAction(null);
    }
  }

  return (
    <>
      <DocumentMeta
        title="AstroNumeric — Reading Desk"
        description="Create a profile and run daily, weekly, or monthly readings."
      />

      <div className="reading-page">
        <section className="reading-hero">
          <div className="reading-hero__copy">
            <span className="reading-eyebrow">Daily reading desk</span>
            <h1>Your daily reading</h1>
            <p>
              Select a profile and run a daily, weekly, or monthly reading. All readings are tied
              to live forecast data.
            </p>

            <div className="reading-hero__actions">
              <button
                type="button"
                className="btn-primary"
                onClick={() => {
                  setShowCreateForm(true);
                  setResult(null);
                }}
              >
                Create a profile
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={handleGenerateReading}
              >
                Run {selectedScope} reading
              </button>
            </div>

            <div className="reading-link-row">
              <Link to="/charts" className="reading-inline-link">
                Open chart, numerology, and compatibility desks
              </Link>
              <Link to="/journal" className="reading-inline-link">
                Open the journal workspace
              </Link>
            </div>
          </div>

          <div className="reading-hero__meta">
            <div className="reading-hero__stats">
              <article className="reading-hero__stat">
                <span>Streak</span>
                <strong>{streakCount}</strong>
                <p>Daily return rhythm carried over from the shared store.</p>
              </article>
              <article className="reading-hero__stat">
                <span>Profiles</span>
                <strong>{profiles.length}</strong>
                <p>Saved profiles synced from the backend when authentication is active.</p>
              </article>
              <article className="reading-hero__stat">
                <span>Recent reads</span>
                <strong>{readingCount}</strong>
                <p>Session and anonymous history stays available locally.</p>
              </article>
            </div>

            <div className="reading-hero__profile-card">
              <span className="reading-hero__profile-label">Active profile</span>
              <strong>{selectedProfile?.name ?? 'Waiting for profile input'}</strong>
              <p>{activeProfileLabel}</p>
            </div>
          </div>
        </section>

        <section className="reading-scope-row" aria-label="Reading scope selector">
          {scopeOptions.map((scope) => (
            <button
              key={scope.id}
              type="button"
              className={
                selectedScope === scope.id
                  ? 'reading-scope-pill reading-scope-pill--active'
                  : 'reading-scope-pill'
              }
              onClick={() => setSelectedScope(scope.id)}
            >
              {scope.label}
            </button>
          ))}
        </section>

        {error && (
          <div className="reading-alert" role="alert">
            <strong>Reading issue</strong>
            <p>{error}</p>
          </div>
        )}

        <div className="reading-layout">
          <div className="reading-control-stack">
            <section className="reading-panel">
              <div className="reading-panel__header">
                <span>Profile setup</span>
                <strong>Create once, reuse anywhere</strong>
              </div>

              <ProfileSelector
                profiles={profiles}
                selectedProfile={selectedProfileId}
                onSelectProfile={handleSelectProfile}
                showCreateForm={showCreateForm}
                onToggleCreate={() => {
                  setShowCreateForm(!showCreateForm);
                  setResult(null);
                }}
              />

              {showCreateForm ? (
                <FortuneForm
                  onSubmit={handleProfileCreate}
                  isLoading={loading}
                  showSaveOption
                />
              ) : (
                <div className="reading-profile-summary">
                  <div className="reading-profile-summary__meta">
                    <span className="reading-profile-summary__label">Current setup</span>
                    {profileStorageLabel && (
                      <span className="reading-profile-summary__source">{profileStorageLabel}</span>
                    )}
                  </div>
                  <strong>{selectedProfile?.name ?? 'No profile selected yet'}</strong>
                  <p>
                    {selectedProfile
                      ? activeProfileLabel
                      : 'Create a session profile to unlock chart, numerology, compatibility, and daily guidance.'}
                  </p>

                  {selectedProfile && (
                    <div className="reading-profile-summary__facts">
                      {selectedProfileFacts.map((fact) => (
                        <article key={fact.label} className="reading-profile-summary__fact">
                          <span>{fact.label}</span>
                          <strong>{fact.value}</strong>
                        </article>
                      ))}
                    </div>
                  )}

                  <div className="reading-profile-summary__note">
                    <p>{profilePersistenceNote}</p>
                    {profileReadinessNote && <p>{profileReadinessNote}</p>}
                  </div>

                  <div className="reading-profile-summary__actions">
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={handleGenerateReading}
                      disabled={loading}
                    >
                      {loading ? 'Loading reading...' : `Generate ${selectedScope} reading`}
                    </button>

                    {selectedProfile && (
                      <button
                        type="button"
                        className="btn-secondary"
                        onClick={() => {
                          setShowCreateForm(true);
                          setResult(null);
                        }}
                      >
                        Create another profile
                      </button>
                    )}

                    {token ? (
                      <label className="reading-toggle">
                        <input
                          type="checkbox"
                          checked={allowCloudHistory}
                          onChange={(event) => setAllowCloudHistory(event.target.checked)}
                        />
                        <span>Save future readings to cloud history</span>
                      </label>
                    ) : (
                      <p className="reading-helper-copy">
                        Saved profiles stay on this device until authentication is connected for cloud sync.
                      </p>
                    )}
                  </div>
                </div>
              )}
            </section>

            <section className="reading-panel">
              <div className="reading-panel__header">
                <span>Recent local history</span>
                <strong>Useful continuity while account flows are still thin</strong>
              </div>

              <div className="reading-history-summary">
                <div className="reading-history-summary__metrics">
                  <article className="reading-history-summary__metric">
                    <span>Stored locally</span>
                    <strong>{readingCount}</strong>
                    <p>{readingCount ? 'waiting on this browser' : 'no readings buffered yet'}</p>
                  </article>

                  <article className="reading-history-summary__metric">
                    <span>Latest save</span>
                    <strong>{latestLocalReading ? formatRecentDate(latestLocalReading.date) : 'Not yet'}</strong>
                    <p>
                      {latestLocalReading
                        ? latestLocalReading.profile?.name ?? 'Session reading'
                        : selectedProfile
                          ? `Ready for ${selectedProfile.name}`
                          : 'Create a profile to start'}
                    </p>
                  </article>
                </div>

                <p className="reading-history-summary__copy">
                  {isAuthenticated
                    ? hasPendingRailwaySync
                      ? 'These local readings will sync to your account on next sync.'
                      : 'Your reading history is clear right now.'
                    : 'Your recent readings are saved on this device. Sign in to keep them across devices.'}
                </p>
              </div>

              {recentReadings.length > 0 ? (
                <div className="reading-history-list">
                  {recentReadings.map((reading) => (
                    <article key={reading.id} className="reading-history-item">
                      <div className="reading-history-item__meta">
                        <span>{reading.scope}</span>
                        <strong>{reading.profile?.name ?? 'Session reading'}</strong>
                        <p>Saved locally for later sync or reuse.</p>
                      </div>
                      <div className="reading-history-item__status">
                        <p>{formatRecentDate(reading.date)}</p>
                        <span className="reading-history-item__chip">Local</span>
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="reading-empty-state reading-empty-state--history">
                  <strong>No local readings yet</strong>
                  <p>
                    Your first reading is saved on this device. Sign in later to sync it across devices.
                  </p>

                  <div className="reading-empty-state__pills">
                    <span className="reading-empty-state__pill">Daily, weekly, or monthly</span>
                    <span className="reading-empty-state__pill">Stored on this browser</span>
                    <span className="reading-empty-state__pill">Ready to sync later</span>
                  </div>

                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={selectedProfile ? handleGenerateReading : () => setShowCreateForm(true)}
                  >
                    {selectedProfile ? `Generate first ${selectedScope} reading` : 'Create a profile first'}
                  </button>
                </div>
              )}
            </section>

            <section className="reading-panel">
              <div className="reading-panel__header">
                <span>Railway backend</span>
                <strong>Account sync for profiles and saved readings</strong>
              </div>

              {isAuthenticated ? (
                <div className="reading-account-card">
                  <div className="reading-account-card__meta">
                    <span className="reading-account-card__eyebrow">Connected account</span>
                    <strong>{user?.email ?? 'Authenticated user'}</strong>
                    <p>{connectedAccountCopy}</p>
                  </div>

                  <div className="reading-account-stats">
                    {accountStats.map((stat) => (
                      <article key={stat.label} className="reading-account-stat">
                        <span>{stat.label}</span>
                        <strong>{stat.value}</strong>
                        <p>{stat.detail}</p>
                      </article>
                    ))}
                  </div>

                  <div className="reading-account-inline-note">
                    {connectedAccountNote}
                  </div>

                  <div className="reading-account-card__actions">
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={handleRailwaySync}
                      disabled={authAction === 'sync'}
                    >
                      {authAction === 'sync'
                        ? 'Syncing to Railway...'
                        : hasPendingRailwaySync
                          ? 'Sync local data now'
                          : 'Check Railway sync'}
                    </button>
                    <button type="button" className="btn-secondary" onClick={logout}>
                      Disconnect account
                    </button>
                  </div>
                </div>
              ) : (
                <div className="reading-account-form">
                  <div className="reading-account-intro">
                    <span className="reading-account-card__eyebrow">Sync preview</span>
                    <strong>Sign in to sync across devices</strong>
                    <p className="reading-helper-copy">{accountPreviewCopy}</p>
                  </div>

                  <div className="reading-account-stats">
                    {accountStats.map((stat) => (
                      <article key={stat.label} className="reading-account-stat">
                        <span>{stat.label}</span>
                        <strong>{stat.value}</strong>
                        <p>{stat.detail}</p>
                      </article>
                    ))}
                  </div>

                  <div className="reading-account-benefits">
                    <span className="reading-account-benefit">Migrate device-local profiles into Railway</span>
                    <span className="reading-account-benefit">Keep reading history beyond this browser</span>
                    <span className="reading-account-benefit">Enable cloud history for future saves</span>
                  </div>

                  <label className="reading-account-field">
                    <span>Email</span>
                    <input
                      type="email"
                      value={authEmail}
                      onChange={(event) => setAuthEmail(event.target.value)}
                      placeholder="you@example.com"
                      autoComplete="email"
                    />
                  </label>

                  <label className="reading-account-field">
                    <span>Password</span>
                    <input
                      type="password"
                      value={authPassword}
                      onChange={(event) => setAuthPassword(event.target.value)}
                      placeholder="Password"
                      autoComplete="current-password"
                    />
                  </label>

                  {!authEmailIsValid && trimmedAuthEmail.length > 0 && (
                    <p className="reading-account-validation">
                      Enter a valid email address before connecting to Railway.
                    </p>
                  )}

                  {trimmedAuthEmail.length > 0 && trimmedAuthPassword.length === 0 && (
                    <p className="reading-account-validation">
                      Add a password to continue.
                    </p>
                  )}

                  <div className="reading-account-card__actions">
                    <button
                      type="button"
                      className="btn-primary"
                      onClick={() => handleAuthSubmit('register')}
                      disabled={!canSubmitAuth}
                    >
                      {authAction === 'register' ? 'Creating account...' : 'Create account'}
                    </button>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => handleAuthSubmit('login')}
                      disabled={!canSubmitAuth}
                    >
                      {authAction === 'login' ? 'Signing in...' : 'Sign in'}
                    </button>
                  </div>

                  <p className="reading-helper-copy">
                    Use the same account later to bring this reading history onto another device.
                  </p>
                </div>
              )}

              {accountMessage && (
                <p
                  className={`reading-account-message reading-account-message--${accountMessage.tone}`}
                  role={accountMessage.tone === 'error' ? 'alert' : 'status'}
                >
                  {accountMessage.text}
                </p>
              )}
            </section>
          </div>

          <section className="reading-result-panel">
            {result ? (
              <FortuneResult data={result} onReset={handleReset} />
            ) : (
              <div className="reading-result-stack">
                {weeklyVibeProfile && (
                  <div className="reading-panel reading-panel--weekly">
                    <WeeklyVibe profile={weeklyVibeProfile} />
                  </div>
                )}

                <div className="reading-panel reading-panel--empty">
                  <div className="reading-panel__header">
                    <span>Reading output</span>
                    <strong>Your reading appears here</strong>
                  </div>

                  <div className="reading-empty-state reading-empty-state--large">
                    <div className="reading-empty-state__intro">
                      <span className="reading-empty-state__eyebrow">Idle desk</span>
                      <strong>{selectedProfile ? `Ready for ${selectedProfile.name}` : 'Start with profile input'}</strong>
                      <p>
                        {selectedProfile
                          ? `Ready for ${selectedScope} reading.`
                          : 'Create or select a profile first, then this panel switches from preview state to live guidance.'}
                      </p>
                    </div>

                    <div className="reading-idle-grid">
                      <article className="reading-idle-card">
                        <span>Profile</span>
                        <strong>{selectedProfile?.name ?? 'Waiting on setup'}</strong>
                        <p>
                          {selectedProfile
                            ? activeProfileLabel
                            : 'Select a profile to get started.'}
                        </p>
                      </article>

                      <article className="reading-idle-card">
                        <span>Selected scope</span>
                        <strong>{scopeOptions.find((scope) => scope.id === selectedScope)?.label ?? 'Daily'}</strong>
                        <p>{getScopePreview(selectedScope)}</p>
                      </article>

                      <article className="reading-idle-card">
                        <span>Next unlock</span>
                        <strong>{selectedProfile ? 'Live result stack' : 'Profile + result stack'}</strong>
                        <p>
                          {selectedProfile
                            ? `Run the ${selectedScope} reading to load summary, drivers, and follow-up tools.`
                            : 'Once a profile is ready, this column switches from preview copy to a live reading output.'}
                        </p>
                      </article>
                    </div>

                    <div className="reading-empty-state__actions">
                      <button
                        type="button"
                        className="btn-primary"
                        onClick={selectedProfile ? handleGenerateReading : () => setShowCreateForm(true)}
                      >
                        {selectedProfile ? `Generate ${selectedScope} reading` : 'Create a profile'}
                      </button>

                      <Link to="/charts" className="btn-secondary reading-empty-state__link">
                        Open chart, numerology, and compatibility desks
                      </Link>
                    </div>

                    <div className="reading-empty-state__workflow">
                      <span className="reading-empty-state__eyebrow">Workflow</span>
                      <ol className="reading-empty-state__steps">
                        <li>Enter birth details with the profile form.</li>
                        <li>Choose daily, weekly, or monthly scope.</li>
                        <li>Generate the reading and branch into the deeper desks from there.</li>
                      </ol>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </>
  );
}

export default ReadingView;