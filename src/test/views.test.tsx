import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

// ============================================
// Mock global variables for tests
// ============================================

const mockAuth = {
  isAuthenticated: false,
  user: null as { id: string; email: string; is_paid: boolean } | null,
  logout: vi.fn(),
};

const mockProfile = {
  id: 1,
  name: 'Test User',
  date_of_birth: '1990-05-15',
  time_of_birth: '14:30',
  latitude: 40.7128,
  longitude: -74.006,
  timezone: 'America/New_York',
};

const mockProfilesArray = [mockProfile];

// Mock API Client to prevent real network calls and resolve correctly
vi.mock('../api/client', () => {
  return {
    fetchWeeklyForecast: vi.fn().mockResolvedValue({ days: [] }),
    fetchDailyFeatures: vi.fn().mockResolvedValue({}),
    fetchCurrentMoonPhase: vi.fn().mockResolvedValue({}),
    fetchUpcomingMoonEvents: vi.fn().mockResolvedValue([]),
    fetchNatalProfile: vi.fn().mockResolvedValue({}),
    fetchTimingAdvice: vi.fn().mockResolvedValue({
      activity: 'business_meeting',
      advice: 'Mocked timing advice',
      today: {
        score: 75,
        rating: 'Good',
        breakdown: {},
        warnings: [],
        recommendations: [],
        best_hours: [],
        date: '2026-06-15',
        weekday: 'Monday',
        emoji: '💼',
        current_phase: 'Waxing Gibbous',
        moon_sign: 'Leo',
      },
      today_is_best: true,
      best_upcoming: null,
    }),
    fetchBestDays: vi.fn().mockResolvedValue({ best_days: [] }),
    fetchTimingActivities: vi.fn().mockResolvedValue({ activities: [] }),
    drawTarotCard: vi.fn().mockResolvedValue({}),
    askOracle: vi.fn().mockResolvedValue({}),
    chatWithCosmicGuide: vi.fn().mockResolvedValue({}),
    fetchQuickInsight: vi.fn().mockResolvedValue({}),
    fetchAiExplanation: vi.fn().mockResolvedValue({}),
    sendSectionFeedback: vi.fn().mockResolvedValue({}),
    fetchCompatibility: vi.fn().mockResolvedValue({
      overall_score: 80,
      summary: 'Strong compatibility',
      dimensions: [],
      strengths: [],
      challenges: [],
      recommendations: [],
    }),
    apiFetch: vi.fn().mockResolvedValue({}),
  };
});

// Mock hooks
vi.mock('../hooks', () => {
  return {
    useProfiles: () => ({
      profiles: mockProfilesArray,
      selectedProfile: mockProfile,
      selectedProfileId: 1,
      activeProfileSourceLabel: 'Railway profile',
      sessionProfile: null,
      createProfile: vi.fn(),
      setSelectedProfileId: vi.fn(),
      suppressNextAutoFetch: vi.fn(),
      clearAutoFetchSuppression: vi.fn(),
      fetchProfiles: vi.fn(),
    }),
    useReading: () => ({
      selectedScope: 'daily',
      result: null,
      setSelectedScope: vi.fn(),
      setResult: vi.fn(),
      getPrediction: vi.fn().mockResolvedValue({ sections: [] }),
    }),
    useAnonReadings: () => ({
      shouldShowUpsellModal: false,
      closeUpsell: vi.fn(),
      saveReading: vi.fn(),
      readings: [],
      readingCount: 5,
      refreshReadings: vi.fn(),
    }),
    useAuth: () => mockAuth,
    useMigrateReadings: () => ({
      migrateReadings: vi
        .fn()
        .mockResolvedValue({ migratedProfileCount: 0, migratedReadingCount: 0 }),
    }),
    useActiveProfile: () => ({
      activeProfile: mockProfile,
      activeProfileSource: 'railway',
      activeProfileSourceLabel: 'Railway profile',
      hasActiveProfile: true,
      isGuestProfile: false,
      isLocalProfile: false,
      isRailwayProfile: true,
      isSessionProfile: false,
      profiles: mockProfilesArray,
      selectedProfileId: 1,
      sessionProfile: null,
    }),
  };
});

vi.mock('../store/useStore', () => {
  return {
    useStore: () => ({
      loading: false,
      error: '',
      showCreateForm: false,
      setShowCreateForm: vi.fn(),
      allowCloudHistory: false,
      setAllowCloudHistory: vi.fn(),
      token: null,
      updateStreak: vi.fn(),
      streakCount: 5,
      lastVisitDate: new Date().toISOString().split('T')[0],
      profiles: mockProfilesArray,
      selectedProfileId: 1,
      sessionProfile: null,
      compareProfileId: null,
      setCompareProfileId: vi.fn(),
    }),
  };
});

// ============================================
// Test Utilities
// ============================================

const AllProviders = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <I18nextProvider i18n={i18n}>{children}</I18nextProvider>
  </BrowserRouter>
);

const renderWithProviders = (ui: React.ReactElement) => {
  return render(ui, { wrapper: AllProviders });
};

// ============================================
// Navigation Tests
// ============================================

describe('Navigation', () => {
  it('renders all navigation links', async () => {
    // Import App dynamically to avoid issues
    const { App } = await import('../App');

    render(
      <I18nextProvider i18n={i18n}>
        <App />
      </I18nextProvider>
    );

    // Wait for lazy-loaded content
    await waitFor(() => {
      expect(screen.queryAllByText(/astro/i).length > 0).toBeTruthy();
    });

    // Check main nav links exist
    expect(screen.getByRole('navigation', { name: /primary navigation/i })).toBeInTheDocument();
  });
});

// ============================================
// ReadingView Tests
// ============================================

import { ReadingView } from '../views/ReadingView';

describe('ReadingView', () => {
  beforeEach(() => {
    mockAuth.isAuthenticated = false;
    mockAuth.user = null;
    vi.clearAllMocks();
  });

  it('renders reading view with scope selector', async () => {
    renderWithProviders(<ReadingView />);

    await waitFor(() => {
      // Should show scope buttons
      expect(
        screen.queryAllByText(/daily/i).length > 0 || screen.queryAllByText(/reading/i).length > 0
      ).toBeTruthy();
    });
  });

  it('displays daily streak component', async () => {
    renderWithProviders(<ReadingView />);

    await waitFor(() => {
      expect(screen.getAllByText('5').length).toBeGreaterThan(0);
    });
  });
});

// ============================================
// ProfileView Tests
// ============================================
import { ProfileView } from '../views/ProfileView';

describe('ProfileView', () => {
  beforeEach(() => {
    mockAuth.isAuthenticated = true;
    mockAuth.user = { id: '1', email: 'test@example.com', is_paid: false };
  });

  afterEach(() => {
    mockAuth.isAuthenticated = false;
    mockAuth.user = null;
  });

  it('renders profile view for authenticated user', async () => {
    renderWithProviders(<ProfileView />);

    await waitFor(() => {
      // Should show profile-related content
      expect(
        screen.queryAllByText(/profile/i).length > 0 || screen.queryAllByText(/account/i).length > 0
      ).toBeTruthy();
    });
  });
});

// ============================================
// LearnView Tests
// ============================================
import { LearnView } from '../views/LearnView';

describe('LearnView', () => {
  it('renders learning center content', async () => {
    renderWithProviders(<LearnView />);

    await waitFor(() => {
      // Should display learning sections
      expect(
        screen.queryAllByText(/zodiac/i).length > 0 ||
          screen.queryAllByText(/numerology/i).length > 0 ||
          screen.queryAllByText(/learn/i).length > 0
      ).toBeTruthy();
    });
  });
});

// ============================================
// CompatibilityView Tests
// ============================================
import { RelationshipsView as CompatibilityView } from '../views/RelationshipsView';

describe('CompatibilityView', () => {
  it('renders compatibility input form', async () => {
    renderWithProviders(<CompatibilityView />);

    await waitFor(() => {
      // Should have profile selection or input
      expect(
        screen.queryAllByText(/compatibility/i).length > 0 ||
          screen.queryAllByText(/compare/i).length > 0
      ).toBeTruthy();
    });
  });
});

// ============================================
// CosmicToolsView Tests
// ============================================
import { CosmicToolsView } from '../views/CosmicToolsView';

describe('CosmicToolsView', () => {
  it('renders cosmic tools page', async () => {
    renderWithProviders(<CosmicToolsView />);

    await waitFor(() => {
      // Should show tools or features
      expect(
        screen.queryAllByText(/tools/i).length > 0 ||
          screen.queryAllByText(/tarot/i).length > 0 ||
          screen.queryAllByText(/moon/i).length > 0
      ).toBeTruthy();
    });
  });
});

// ============================================
// Accessibility Tests
// ============================================

describe('Accessibility', () => {
  it('navigation has proper ARIA labels', async () => {
    const { App } = await import('../App');
    render(
      <I18nextProvider i18n={i18n}>
        <App />
      </I18nextProvider>
    );

    await waitFor(() => {
      const nav = screen.getByRole('navigation', { name: /primary navigation/i });
      expect(nav).toHaveAttribute('aria-label');
    });
  });

  it('buttons have accessible names', async () => {
    renderWithProviders(<ReadingView />);

    await waitFor(() => {
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        // Each button should have accessible text
        expect(button.textContent || button.getAttribute('aria-label')).toBeTruthy();
      });
    });
  });
});

// Reset after all tests
afterEach(() => {
  vi.clearAllMocks();
});
