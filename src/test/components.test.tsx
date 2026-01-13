import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

// ============================================
// FortuneForm Tests
// ============================================
import { FortuneForm } from '../components/FortuneForm';

// Mock LocationAutocomplete since it has external dependencies
vi.mock('../components/LocationAutocomplete', () => ({
  LocationAutocomplete: ({
    onSelect,
    placeholder,
  }: {
    onSelect: (loc: unknown) => void;
    placeholder: string;
  }) => (
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

  it('renders all form fields across steps', async () => {
    const { container } = render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Step 1: Name
    expect(screen.getByText(/What is your name/i)).toBeInTheDocument();
    await user.type(screen.getByPlaceholderText(/form\.fullNamePlaceholder/i), 'John Doe');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 2: DOB
    expect(await screen.findByText(/When were you born/i)).toBeInTheDocument();
    const dateInput = container.querySelector('input[type="date"]');
    const timeInput = container.querySelector('input[type="time"]');
    expect(dateInput).toBeInTheDocument();
    expect(timeInput).toBeInTheDocument();

    await user.type(timeInput!, '14:30');
    fireEvent.change(dateInput!, { target: { value: '1990-05-15' } });
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 3: Location
    expect(await screen.findByText(/Where were you born/i)).toBeInTheDocument();
    expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
    await user.type(screen.getByTestId('location-autocomplete'), 'New York');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 4: Summary
    expect(await screen.findByText(/Ready for your destiny/i)).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /prediction/i })).toBeInTheDocument();
  });

  it('shows validation error when name is empty', async () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Try to go to next step without name
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Expect error message (translated key usually)
    expect(await screen.findByText(/form\.errors\.nameRequired/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('shows validation error when date is empty on step 2', async () => {
    render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Step 1
    await user.type(screen.getByPlaceholderText(/form\.fullNamePlaceholder/i), 'John Doe');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 2
    expect(await screen.findByText(/When were you born/i)).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /next/i }));

    expect(await screen.findByText(/form\.errors\.dobRequired/i)).toBeInTheDocument();
  });

  it('submits valid form data', async () => {
    const { container } = render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Step 1
    await user.type(screen.getByPlaceholderText(/form\.fullNamePlaceholder/i), 'Jane Doe');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 2
    expect(await screen.findByText(/When were you born/i)).toBeInTheDocument();
    const dateInput = container.querySelector('input[type="date"]');
    const timeInput = container.querySelector('input[type="time"]');
    fireEvent.change(dateInput!, { target: { value: '1990-05-15' } });
    await user.type(timeInput!, '14:30');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 3
    const locationInput = await screen.findByTestId('location-autocomplete');
    await user.type(locationInput, 'New York');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 4
    const submitButton = await screen.findByRole('button', { name: /prediction/i });
    await user.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Jane Doe',
        date_of_birth: '1990-05-15',
        time_of_birth: '14:30',
        place_of_birth: 'New York, NY, USA',
      })
    );
  });

  it('disables submit button when loading', async () => {
    const { container } = render(<FortuneForm onSubmit={mockOnSubmit} isLoading={true} />);
    const user = userEvent.setup();

    // Go to last step
    await user.type(screen.getByPlaceholderText(/form\.fullNamePlaceholder/i), 'John');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Wait for step 2
    expect(await screen.findByText(/When were you born/i)).toBeInTheDocument();
    const dateInput = container.querySelector('input[type="date"]');
    fireEvent.change(dateInput!, { target: { value: '1990-01-01' } });
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Wait for step 3
    expect(await screen.findByText(/Where were you born/i)).toBeInTheDocument();
    await user.type(await screen.findByTestId('location-autocomplete'), 'New York');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Wait for step 4
    expect(await screen.findByText(/Ready for your destiny/i)).toBeInTheDocument();
    const submitButton = await screen.findByRole('button', { name: /form\.readingStars/i });
    expect(submitButton).toBeDisabled();
  });

  it('updates location when LocationAutocomplete selects a place', async () => {
    const { container } = render(<FortuneForm onSubmit={mockOnSubmit} isLoading={false} />);
    const user = userEvent.setup();

    // Step 1
    await user.type(screen.getByPlaceholderText(/form\.fullNamePlaceholder/i), 'John');
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 2
    expect(await screen.findByText(/When were you born/i)).toBeInTheDocument();
    const dateInput = container.querySelector('input[type="date"]');
    fireEvent.change(dateInput!, { target: { value: '1990-01-01' } });
    await user.click(screen.getByRole('button', { name: /next/i }));

    // Step 3: Location
    expect(await screen.findByText(/Where were you born/i)).toBeInTheDocument();
    const locationInput = await screen.findByTestId('location-autocomplete');
    await user.type(locationInput, 'New York');

    // Check that geo indicator appears (mock returns America/New_York)
    expect(await screen.findByText(/America\/New_York/)).toBeInTheDocument();
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
import { ToastContainer } from '../components/Toast';

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

    const iconTexts = Array.from(iconSpans).map((el) => el.textContent);
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
