/**
 * Zustand store for global state management
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  CompatibilityResult,
  NumerologyProfile,
  PredictionData,
  SavedProfile,
} from '../types';

const SESSION_PROFILE_STORAGE_KEY = 'astro-session-profile';

function readSessionProfile() {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const stored = window.sessionStorage.getItem(SESSION_PROFILE_STORAGE_KEY);
    return stored ? (JSON.parse(stored) as SavedProfile) : null;
  } catch {
    return null;
  }
}

function writeSessionProfile(profile: SavedProfile | null) {
  if (typeof window === 'undefined') {
    return;
  }

  try {
    if (profile) {
      window.sessionStorage.setItem(SESSION_PROFILE_STORAGE_KEY, JSON.stringify(profile));
      return;
    }

    window.sessionStorage.removeItem(SESSION_PROFILE_STORAGE_KEY);
  } catch {
    // Ignore storage failures and keep the in-memory state usable.
  }
}

interface AppState {
  // Saved profiles (backend when authenticated, device-local otherwise)
  profiles: SavedProfile[];
  selectedProfileId: number | null;
  setProfiles: (profiles: SavedProfile[]) => void;
  setSelectedProfileId: (id: number | null) => void;
  addProfile: (profile: SavedProfile) => void;

  // Session profile (never saved to backend, kept only for the current browser session)
  sessionProfile: SavedProfile | null;
  setSessionProfile: (profile: SavedProfile | null) => void;

  // Reading
  selectedScope: 'daily' | 'weekly' | 'monthly';
  result: PredictionData | null;
  setSelectedScope: (scope: 'daily' | 'weekly' | 'monthly') => void;
  setResult: (result: PredictionData | null) => void;

  // Numerology
  numerologyProfile: NumerologyProfile | null;
  setNumerologyProfile: (profile: NumerologyProfile | null) => void;

  // Compatibility
  compareProfileId: number | null;
  compatibilityResult: CompatibilityResult | null;
  setCompareProfileId: (id: number | null) => void;
  setCompatibilityResult: (result: CompatibilityResult | null) => void;

  // Glossary
  glossary: { zodiac: Record<string, unknown>; numerology: Record<string, unknown> } | null;
  setGlossary: (
    glossary: { zodiac: Record<string, unknown>; numerology: Record<string, unknown> } | null
  ) => void;

  // UI State
  loading: boolean;
  error: string;
  showCreateForm: boolean;
  setLoading: (loading: boolean) => void;
  setError: (error: string) => void;
  setShowCreateForm: (show: boolean) => void;

  // Theme
  theme: 'default' | 'ocean' | 'midnight' | 'sage';
  setTheme: (theme: 'default' | 'ocean' | 'midnight' | 'sage') => void;

  // Tone preference
  tonePreference: number; // 0 = Practical, 100 = Mystical
  setTonePreference: (tone: number) => void;

  // Reminders
  dailyReminderEnabled: boolean;
  setDailyReminder: (enabled: boolean) => void;
  reminderCadence: 'daily' | 'weekdays' | 'weekly';
  setReminderCadence: (cadence: 'daily' | 'weekdays' | 'weekly') => void;

  // Cloud history opt-in
  allowCloudHistory: boolean;
  setAllowCloudHistory: (allow: boolean) => void;

  // Streak
  streakCount: number;
  lastVisitDate: string | null;
  updateStreak: () => void;

  // Auth
  token: string | null;
  user: { id: string; email: string; is_paid: boolean } | null;
  setAuth: (
    token: string | null,
    user: { id: string; email: string; is_paid: boolean } | null
  ) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Saved profiles (backend when authenticated, device-local otherwise)
      profiles: [],
      selectedProfileId: null,
      setProfiles: (profiles) => set({ profiles }),
      setSelectedProfileId: (id) => set({ selectedProfileId: id }),
      addProfile: (profile) => set((state) => ({ profiles: [...state.profiles, profile] })),

      // Session profile (browser-session only)
      sessionProfile: readSessionProfile(),
      setSessionProfile: (profile) => {
        writeSessionProfile(profile);
        set({ sessionProfile: profile });
      },

      // Reading
      selectedScope: 'daily',
      result: null,
      setSelectedScope: (scope) => set({ selectedScope: scope }),
      setResult: (result) => set({ result }),

      // Numerology
      numerologyProfile: null,
      setNumerologyProfile: (profile) => set({ numerologyProfile: profile }),

      // Compatibility
      compareProfileId: null,
      compatibilityResult: null,
      setCompareProfileId: (id) => set({ compareProfileId: id }),
      setCompatibilityResult: (result) => set({ compatibilityResult: result }),

      // Glossary
      glossary: null,
      setGlossary: (glossary) => set({ glossary }),

      // UI State
      loading: false,
      error: '',
      showCreateForm: false,
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      setShowCreateForm: (show) => set({ showCreateForm: show }),

      // Theme
      theme: 'default',
      setTheme: (theme) => {
        // Apply theme to document
        if (theme === 'default') {
          document.documentElement.removeAttribute('data-theme');
        } else {
          document.documentElement.setAttribute('data-theme', theme);
        }
        set({ theme });
      },

      // Tone preference
      tonePreference: 50,
      setTonePreference: (tone) => set({ tonePreference: tone }),

      // Reminders
      dailyReminderEnabled: false,
      setDailyReminder: (enabled) => set({ dailyReminderEnabled: enabled }),
      reminderCadence: 'daily',
      setReminderCadence: (cadence) => set({ reminderCadence: cadence }),

      // Cloud history opt-in
      allowCloudHistory: false,
      setAllowCloudHistory: (allow) => set({ allowCloudHistory: allow }),

      // Streak
      streakCount: 0,
      lastVisitDate: null,
      updateStreak: () => {
        const today = new Date().toISOString().split('T')[0];
        set((state) => {
          if (state.lastVisitDate === today) return state;

          const yesterday = new Date();
          yesterday.setDate(yesterday.getDate() - 1);
          const yesterdayStr = yesterday.toISOString().split('T')[0];

          if (state.lastVisitDate === yesterdayStr) {
            return { streakCount: state.streakCount + 1, lastVisitDate: today };
          } else {
            return { streakCount: 1, lastVisitDate: today };
          }
        });
      },

      // Auth
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      logout: () =>
        set((state) => {
          const localProfiles = state.profiles.filter((profile) => profile.id < 0);
          const hasSessionProfile = Boolean(state.sessionProfile);
          const localSelectedProfileId =
            typeof state.selectedProfileId === 'number' && state.selectedProfileId < 0
              ? state.selectedProfileId
              : localProfiles[0]?.id ?? null;
          const localCompareProfileId =
            typeof state.compareProfileId === 'number' && state.compareProfileId < 0
              ? state.compareProfileId
              : null;

          return {
            token: null,
            user: null,
            profiles: localProfiles,
            selectedProfileId: hasSessionProfile ? null : localSelectedProfileId,
            compareProfileId: localCompareProfileId,
            sessionProfile: state.sessionProfile,
          };
        }),
    }),
    {
      name: 'astro-storage',
      // Persist saved profiles, current selectors, UI preferences, and auth
      partialize: (state) => ({
        profiles: state.profiles,
        selectedProfileId: state.selectedProfileId,
        compareProfileId: state.compareProfileId,
        selectedScope: state.selectedScope,
        token: state.token,
        user: state.user,
        theme: state.theme,
        tonePreference: state.tonePreference,
        dailyReminderEnabled: state.dailyReminderEnabled,
        reminderCadence: state.reminderCadence,
        allowCloudHistory: state.allowCloudHistory,
        streakCount: state.streakCount,
        lastVisitDate: state.lastVisitDate,
      }),
      onRehydrateStorage: () => (state) => {
        // Reapply theme on page load
        if (state?.theme && state.theme !== 'default') {
          document.documentElement.setAttribute('data-theme', state.theme);
        }

        if (state?.sessionProfile === null) {
          writeSessionProfile(null);
        }
      },
    }
  )
);
