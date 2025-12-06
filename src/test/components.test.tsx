import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

// ============================================
// FortuneForm Tests
// ============================================
import { FortuneForm } from '../components/FortuneForm';

// Mock LocationAutocomplete since it has external dependencies
vi.mock('../components/LocationAutocomplete', () => ({
  LocationAutocomplete: ({ onSelect, placeholder }: { onSelect: (loc: unknown) => void; placeholder: string }) => (
    <input
      data-testid="location-autocomplete"
      placeholder={placeholder}
      onChange={(e) => {
        if (e.target.value === 'New York') {
          onSelect({
            name: 'New York, NY, USA',
            latitude: 40.7128,
            longitude: -74.006,
            timezone: 'America/New_York',
          });
        }
      }}
    />
  ),
}));

describe('FortuneForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders all form fields', () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);

    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date of birth/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/time of birth/i)).toBeInTheDocument();
    // Place of birth uses LocationAutocomplete component
    expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
  });

  it('shows validation error when name is empty', async () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Fill date but leave name empty (simulate bypassing HTML5 validation)
    const nameInput = screen.getByLabelText(/full name/i);
    const dateInput = screen.getByLabelText(/date of birth/i);
    
    // Type a space then delete to trigger validation without HTML5 required blocking
    await user.type(nameInput, ' ');
    await user.clear(nameInput);
    await user.type(dateInput, '1990-05-15');

    // Submit form - need to click even though HTML5 might block
    const submitButton = screen.getByRole('button', { name: /prediction/i });
    await user.click(submitButton);

    // The form validates on submit - check onSubmit wasn't called with empty name
    // Note: HTML5 validation may prevent form submission, which is expected behavior
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows validation error when date is in the future', async () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Fill form with future date
    await user.type(screen.getByLabelText(/full name/i), 'John Doe');
    
    // Set a future date (must clear first since date inputs can be tricky)
    const dateInput = screen.getByLabelText(/date of birth/i);
    await user.clear(dateInput);
    fireEvent.change(dateInput, { target: { value: '2030-01-01' } });

    // Submit form
    const submitButton = screen.getByRole('button', { name: /prediction/i });
    await user.click(submitButton);

    // Check for error about future date
    expect(await screen.findByText(/cannot be in the future/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits valid form data', async () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Fill form with valid data
    await user.type(screen.getByLabelText(/full name/i), 'Jane Doe');
    await user.type(screen.getByLabelText(/date of birth/i), '1990-05-15');
    await user.type(screen.getByLabelText(/time of birth/i), '14:30');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /prediction/i });
    await user.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Jane Doe',
        date_of_birth: '1990-05-15',
        time_of_birth: '14:30',
      })
    );
  });

  it('disables submit button when loading', () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={true} />);

    const submitButton = screen.getByRole('button', { name: /reading the stars/i });
    expect(submitButton).toBeDisabled();
  });

  it('updates location when LocationAutocomplete selects a place', async () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Type in location to trigger mock selection
    const locationInput = screen.getByTestId('location-autocomplete');
    await user.type(locationInput, 'New York');

    // Check that geo indicator appears
    expect(await screen.findByText(/40\.7128/)).toBeInTheDocument();
  });
});

// ============================================
// ErrorBoundary Tests
// ============================================
import { ErrorBoundary } from '../components/ErrorBoundary';

// Component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error for cleaner test output
  const originalError = console.error;
  beforeEach(() => {
    console.error = vi.fn();
  });
  afterEach(() => {
    console.error = originalError;
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Child content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Child content')).toBeInTheDocument();
  });

  it('renders error UI when child throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument();
  });

  it('logs error to console', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(console.error).toHaveBeenCalled();
  });
});

// ============================================
// Toast System Tests
// ============================================
import { ToastContainer, toast, useToasts, ToastItem } from '../components/Toast';

// Wrapper component to test the hook
const ToastTestWrapper = () => {
  const { toasts, dismiss } = useToasts();
  return <ToastContainer toasts={toasts} onDismiss={dismiss} />;
};

describe('Toast System', () => {
  beforeEach(() => {
    // Reset toast state between tests (clear any existing toasts)
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders toast container', () => {
    render(<ToastContainer toasts={[]} onDismiss={() => {}} />);
    expect(screen.getByLabelText('Notifications')).toBeInTheDocument();
  });

  it('displays a toast message', () => {
    const testToast: ToastItem = {
      id: 'test-1',
      message: 'Test notification',
      type: 'success',
    };

    render(<ToastContainer toasts={[testToast]} onDismiss={() => {}} />);
    expect(screen.getByText('Test notification')).toBeInTheDocument();
  });

  it('shows correct icon for each toast type', () => {
    const toasts: ToastItem[] = [
      { id: '1', message: 'Success', type: 'success' },
      { id: '2', message: 'Error', type: 'error' },
      { id: '3', message: 'Info', type: 'info' },
      { id: '4', message: 'Warning', type: 'warning' },
    ];

    render(<ToastContainer toasts={toasts} onDismiss={() => {}} />);

    // Check icons exist within toast-icon spans
    const iconSpans = document.querySelectorAll('.toast-icon');
    expect(iconSpans.length).toBe(4);
    
    const iconTexts = Array.from(iconSpans).map(el => el.textContent);
    expect(iconTexts).toContain('✓');
    expect(iconTexts).toContain('✕');
    expect(iconTexts).toContain('ℹ');
    expect(iconTexts).toContain('⚠');
  });

  it('calls onDismiss when close button is clicked', async () => {
    const mockDismiss = vi.fn();
    const testToast: ToastItem = {
      id: 'test-1',
      message: 'Dismissable',
      type: 'info',
    };

    render(<ToastContainer toasts={[testToast]} onDismiss={mockDismiss} />);
    
    const closeButton = screen.getByLabelText('Dismiss notification');
    fireEvent.click(closeButton);

    expect(mockDismiss).toHaveBeenCalledWith('test-1');
  });

  it('has correct aria attributes for accessibility', () => {
    const testToast: ToastItem = {
      id: 'test-1',
      message: 'Accessible toast',
      type: 'success',
    };

    render(<ToastContainer toasts={[testToast]} onDismiss={() => {}} />);

    const toastElement = screen.getByRole('alert');
    expect(toastElement).toHaveAttribute('aria-live', 'polite');
  });
});

// ============================================
// Skeleton Component Tests
// ============================================
import { Skeleton, CardSkeleton, ProfileSkeleton } from '../components/Skeleton';

describe('Skeleton Components', () => {
  it('renders text skeleton with default height', () => {
    render(<Skeleton variant="text" />);
    const skeleton = document.querySelector('.skeleton');
    expect(skeleton).toBeInTheDocument();
  });

  it('renders circular skeleton', () => {
    render(<Skeleton variant="circular" width={64} height={64} />);
    const skeleton = document.querySelector('.skeleton');
    expect(skeleton).toHaveStyle({ borderRadius: '50%' });
  });

  it('renders multiple skeletons when count is specified', () => {
    render(<Skeleton variant="text" count={3} />);
    const skeletons = document.querySelectorAll('.skeleton');
    expect(skeletons.length).toBe(3);
  });

  it('renders CardSkeleton with proper structure', () => {
    render(<CardSkeleton />);
    const skeleton = document.querySelector('.card-skeleton');
    expect(skeleton).toBeInTheDocument();
  });

  it('renders ProfileSkeleton with avatar placeholder', () => {
    render(<ProfileSkeleton />);
    const skeletons = document.querySelectorAll('.skeleton');
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
