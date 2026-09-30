import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { AppDownloadButton } from '../components/AppDownloadButton';
import { OracleAppShowcase } from '../components/OracleAppShowcase';

describe('store buttons', () => {
  it('say "Coming soon" instead of linking while the app is not in the store yet', () => {
    render(<AppDownloadButton store="app-store" />);
    expect(screen.getByText('Coming soon to App Store')).toBeInTheDocument();
    expect(screen.queryByRole('link')).toBeNull();
  });

  it('the Oracle showcase points to the app instead of answering on the web', () => {
    render(<OracleAppShowcase />);
    expect(screen.getByRole('heading', { name: /The Oracle/ })).toBeInTheDocument();
    expect(screen.queryByRole('textbox')).toBeNull();
    expect(screen.getByText(/Coming soon to App Store/)).toBeInTheDocument();
  });
});
