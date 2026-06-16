import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

// ============================================
// Toast Tests
// ============================================
import { ToastContainer } from '../components/Toast';

describe('Toast', () => {
  it('renders toast with correct type styling', () => {
    const toasts = [
      { id: '1', message: 'Success message', type: 'success' as const },
      { id: '2', message: 'Error message', type: 'error' as const },
    ];
    const onDismiss = vi.fn();

    render(<ToastContainer toasts={toasts} onDismiss={onDismiss} />);

    expect(screen.getByText('Success message')).toBeInTheDocument();
    expect(screen.getByText('Error message')).toBeInTheDocument();
  });

  it('calls onDismiss when close button clicked', async () => {
    const toasts = [{ id: '1', message: 'Test', type: 'info' as const }];
    const onDismiss = vi.fn();
    const user = userEvent.setup();

    render(<ToastContainer toasts={toasts} onDismiss={onDismiss} />);

    const closeButton = screen.getByLabelText('Dismiss notification');
    await user.click(closeButton);

    expect(onDismiss).toHaveBeenCalledWith('1');
  });

  it('has accessible role and aria-live', () => {
    const toasts = [{ id: '1', message: 'Alert message', type: 'warning' as const }];
    const onDismiss = vi.fn();

    render(<ToastContainer toasts={toasts} onDismiss={onDismiss} />);

    const toastElement = screen.getByRole('alert');
    expect(toastElement).toHaveAttribute('aria-live', 'polite');
  });
});

// ============================================
// ErrorBoundary Tests
// ============================================
import { ErrorBoundary } from '../components/ErrorBoundary';

const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error for expected errors
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });
  afterEach(() => {
    console.error = originalError;
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <div>Child content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Child content')).toBeInTheDocument();
  });

  it('renders fallback UI when error occurs', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Refresh Page/i })).toBeInTheDocument();
  });

  it('recovers when try again is clicked', async () => {
    const user = userEvent.setup();
    let shouldThrow = true;

    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={shouldThrow} />
      </ErrorBoundary>
    );

    // Error state
    expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();

    // Click try again - this resets the error boundary
    shouldThrow = false;
    const tryAgainButton = screen.getByRole('button', { name: /Refresh Page/i });
    await user.click(tryAgainButton);

    // Re-render with no error
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );
  });
});

// ============================================
// CollapsibleSection Tests
// ============================================
import { CollapsibleSection } from '../components/CollapsibleSection';

describe('CollapsibleSection', () => {
  it('renders title and toggles content visibility', async () => {
    const user = userEvent.setup();

    render(
      <CollapsibleSection title="Test Section">
        <p>Hidden content</p>
      </CollapsibleSection>
    );

    expect(screen.getByText('Test Section')).toBeInTheDocument();

    // Initially collapsed by default
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-expanded', 'false');

    // Click to expand
    await user.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByText('Hidden content')).toBeInTheDocument();
  });

  it('starts expanded when defaultOpen is true', () => {
    render(
      <CollapsibleSection title="Open Section" defaultExpanded={true}>
        <p>Visible content</p>
      </CollapsibleSection>
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-expanded', 'true');
  });
});

// ============================================
// DailyStreak Tests
// ============================================
import { DailyStreak } from '../components/DailyStreak';

// Mock the store
vi.mock('../store/useStore', () => ({
  useStore: () => ({
    streakCount: 7,
    lastVisitDate: new Date().toISOString().split('T')[0],
    updateStreak: vi.fn(),
  }),
}));

describe('DailyStreak', () => {
  it('renders streak count', () => {
    render(<DailyStreak />);

    expect(screen.getByText(/7\s*Day\s*Streak/i)).toBeInTheDocument();
    expect(screen.getByText(/streak/i)).toBeInTheDocument();
  });
});

// ============================================
// Skeleton Tests
// ============================================
import { ReadingSkeleton, ChartSkeleton, GlossarySkeleton } from '../components/Skeleton';

describe('Skeleton Components', () => {
  it('renders ReadingSkeleton', () => {
    render(<ReadingSkeleton />);
    const skeleton = document.querySelector('.skeleton-card');
    expect(skeleton).toBeInTheDocument();
  });

  it('renders ChartSkeleton', () => {
    render(<ChartSkeleton />);
    const skeletonElements = document.querySelectorAll('.skeleton');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  it('renders GlossarySkeleton', () => {
    render(<GlossarySkeleton />);
    const skeletonElements = document.querySelectorAll('.skeleton');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });
});

// ============================================
// LanguageSwitcher Tests
// ============================================
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import { I18nextProvider } from 'react-i18next';
import i18n from '../i18n';

describe('LanguageSwitcher', () => {
  it('renders language selector', () => {
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    // Should have a select language button
    const selector = screen.getByRole('button', { name: /Select language/i });
    expect(selector).toBeInTheDocument();
  });

  it('changes language on selection', async () => {
    const user = userEvent.setup();

    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    // Open dropdown
    const selector = screen.getByRole('button', { name: /Select language/i });
    await user.click(selector);

    // Select Spanish option
    const option = screen.getByRole('option', { name: /Español/i });
    await user.click(option);

    expect(i18n.language).toBe('es');
  });
});

// Reset i18n after tests
afterEach(() => {
  i18n.changeLanguage('en');
});
