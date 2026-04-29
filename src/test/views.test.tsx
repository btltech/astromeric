import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

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
    const { default: App } = await import('../App');

    renderWithProviders(<App />);

    // Wait for lazy-loaded content
    await waitFor(() => {
      expect(screen.getByText('ASTRO')).toBeInTheDocument();
    });

    // Check main nav links exist
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});

// ============================================
// ReadingView Tests
// ============================================
import { ReadingView } from '../views/ReadingView';

// Mock hooks
vi.mock('../hooks', () => ({
  useProfiles: () => ({
    selectedProfile: {
      id: 1,
      name: 'Test User',
      date_of_birth: '1990-05-15',
      time_of_birth: '14:30',
      latitude: 40.7128,
      longitude: -74.006,
      timezone: 'America/New_York',
    },
    createProfile: vi.fn(),
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
  }),
  useAuth: () => ({
    isAuthenticated: false,
    user: null,
    logout: vi.fn(),
  }),
}));

vi.mock('../store/useStore', () => ({
  useStore: () => ({
    loading: false,
    allowCloudHistory: false,
    setAllowCloudHistory: vi.fn(),
    token: null,
    updateStreak: vi.fn(),
    streakCount: 5,
    lastVisitDate: new Date().toISOString().split('T')[0],
  }),
}));

describe('ReadingView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders reading view with scope selector', async () => {
    renderWithProviders(<ReadingView />);

    await waitFor(() => {
      // Should show scope buttons
      const dailyButton = screen.queryByText(/daily/i);
      expect(dailyButton || screen.queryByText(/reading/i)).toBeTruthy();
    });
  });

  it('displays daily streak component', async () => {
    renderWithProviders(<ReadingView />);

    await waitFor(() => {
      expect(screen.getByText('5')).toBeInTheDocument();
    });
  });
});

// ============================================
// ProfileView Tests
// ============================================
import { ProfileView } from '../views/ProfileView';

vi.mock('../hooks', async () => {
  const actual = await vi.importActual('../hooks');
  return {
    ...actual,
    useAuth: () => ({
      isAuthenticated: true,
      user: { id: '1', email: 'test@example.com', is_paid: false },
      logout: vi.fn(),
    }),
  };
});

describe('ProfileView', () => {
  it('renders profile view for authenticated user', async () => {
    renderWithProviders(<ProfileView />);

    await waitFor(() => {
      // Should show profile-related content
      expect(screen.queryByText(/profile/i) || screen.queryByText(/account/i)).toBeTruthy();
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
        screen.queryByText(/zodiac/i) ||
          screen.queryByText(/numerology/i) ||
          screen.queryByText(/learn/i)
      ).toBeTruthy();
    });
  });
});

// ============================================
// CompatibilityView Tests
// ============================================
import { CompatibilityView } from '../views/CompatibilityView';

describe('CompatibilityView', () => {
  it('renders compatibility input form', async () => {
    renderWithProviders(<CompatibilityView />);

    await waitFor(() => {
      // Should have profile selection or input
      expect(screen.queryByText(/compatibility/i) || screen.queryByText(/compare/i)).toBeTruthy();
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
        screen.queryByText(/tools/i) || screen.queryByText(/tarot/i) || screen.queryByText(/moon/i)
      ).toBeTruthy();
    });
  });
});

// ============================================
// NotFoundView Tests
// ============================================
import NotFoundView from '../views/NotFoundView';

describe('NotFoundView', () => {
  it('renders 404 page with navigation link', async () => {
    renderWithProviders(<NotFoundView />);

    await waitFor(() => {
      expect(screen.getByText(/404/i) || screen.getByText(/not found/i)).toBeTruthy();
    });

    // Should have a link back to home
    const homeLink = screen.queryByRole('link');
    expect(homeLink).toBeTruthy();
  });
});

// ============================================
// Accessibility Tests
// ============================================

describe('Accessibility', () => {
  it('navigation has proper ARIA labels', async () => {
    const { default: App } = await import('../App');
    renderWithProviders(<App />);

    await waitFor(() => {
      const nav = screen.getByRole('navigation');
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
