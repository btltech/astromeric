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

interface AppState {
  // Profiles (saved to backend - opt-in only)
  profiles: SavedProfile[];
  selectedProfileId: number | null;
  setProfiles: (profiles: SavedProfile[]) => void;
  setSelectedProfileId: (id: number | null) => void;
  addProfile: (profile: SavedProfile) => void;

  // Session profile (never saved to backend or localStorage)
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

  // Auth (new)
  token: string | null;
  user: { id: string; email: string; is_paid: boolean } | null;
  setAuth: (token: string | null, user: { id: string; email: string; is_paid: boolean } | null) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // Profiles (saved to backend - opt-in only)
      profiles: [],
      selectedProfileId: null,
      setProfiles: (profiles) => set({ profiles }),
      setSelectedProfileId: (id) => set({ selectedProfileId: id }),
      addProfile: (profile) => set((state) => ({ profiles: [...state.profiles, profile] })),

      // Session profile (never saved)
      sessionProfile: null,
      setSessionProfile: (profile) => set({ sessionProfile: profile }),

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

      // Auth
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null, profiles: [], selectedProfileId: null }),
    }),
    {
      name: 'astro-storage',
      // Persist UI preferences and auth
      partialize: (state) => ({
        selectedScope: state.selectedScope,
        token: state.token,
        user: state.user,
        theme: state.theme,
        tonePreference: state.tonePreference,
        dailyReminderEnabled: state.dailyReminderEnabled,
        reminderCadence: state.reminderCadence,
        allowCloudHistory: state.allowCloudHistory,
      }),
      onRehydrateStorage: () => (state) => {
        // Reapply theme on page load
        if (state?.theme && state.theme !== 'default') {
          document.documentElement.setAttribute('data-theme', state.theme);
        }
      },
    }
  )
);
