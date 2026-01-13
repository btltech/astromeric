import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { DailyGuidance } from '../components/DailyGuidance';
import type { DailyGuidance as DailyGuidanceType } from '../types';

describe('DailyGuidance', () => {
  const mockGuidance: DailyGuidanceType = {
    avoid: {
      activities: ['Procrastination', 'Conflict'],
      colors: ['Black', 'Grey'],
      numbers: [1, 5],
    },
    embrace: {
      activities: ['Action', 'Harmony'],
      colors: ['Red', 'Gold'],
      time: '10:00 AM - 11:00 AM',
    },
    retrogrades: [],
    void_of_course_moon: {
      is_void: false,
      current_sign: 'Taurus',
      advice: 'Moon is active',
    },
    current_planetary_hour: null,
  };

  it('renders the guidance title', () => {
    render(<DailyGuidance guidance={mockGuidance} />);
    expect(screen.getByText(/Daily Cosmic Guidance/i)).toBeInTheDocument();
  });

  it('renders embrace section correctly', () => {
    render(<DailyGuidance guidance={mockGuidance} />);

    // Check tab label
    expect(screen.getByText('Embrace')).toBeInTheDocument();

    // Check activities
    expect(screen.getByText('Action')).toBeInTheDocument();
    expect(screen.getByText('Harmony')).toBeInTheDocument();

    // Check power hour
    expect(screen.getByText('10:00 AM - 11:00 AM')).toBeInTheDocument();

    // Check colors (by title attribute)
    expect(screen.getByTitle('Red')).toBeInTheDocument();
    expect(screen.getByTitle('Gold')).toBeInTheDocument();
  });

  it('renders avoid section correctly', async () => {
    render(<DailyGuidance guidance={mockGuidance} />);

    // Switch to avoid tab
    const avoidTab = screen.getByRole('tab', { name: /Avoid/i });
    fireEvent.click(avoidTab);

    // Check activities
    expect(await screen.findByText('Procrastination')).toBeInTheDocument();
    expect(await screen.findByText('Conflict')).toBeInTheDocument();

    // Check colors
    expect(screen.getByTitle('Black')).toBeInTheDocument();
    expect(screen.getByTitle('Grey')).toBeInTheDocument();

    // Check challenge numbers
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('handles empty lists gracefully', () => {
    const emptyGuidance: DailyGuidanceType = {
      avoid: { activities: [], colors: [], numbers: [] },
      embrace: { activities: [], colors: [], time: '' },
      retrogrades: [],
      void_of_course_moon: { is_void: false, current_sign: 'Aries', advice: '' },
      current_planetary_hour: null,
    };

    render(<DailyGuidance guidance={emptyGuidance} />);

    expect(screen.getByText('Embrace')).toBeInTheDocument();
    expect(screen.getByText('Avoid')).toBeInTheDocument();

    // Should not find any list items or badges
    expect(screen.queryByTitle('Red')).not.toBeInTheDocument();
    expect(screen.queryByText('1')).not.toBeInTheDocument();
  });

  it('displays retrogrades when present', () => {
    const guidanceWithRetrogrades: DailyGuidanceType = {
      ...mockGuidance,
      retrogrades: [
        {
          planet: 'Mercury',
          sign: 'Virgo',
          impact: 'Communication delays, tech issues',
          avoid: ['Signing contracts'],
          embrace: ['Review past work'],
        },
      ],
    };

    render(<DailyGuidance guidance={guidanceWithRetrogrades} />);

    expect(screen.getByText(/Cosmic Context/i)).toBeInTheDocument();
    expect(screen.getByText(/Mercury Retrograde/)).toBeInTheDocument();
    expect(screen.getByText(/in Virgo/)).toBeInTheDocument();

    // Need to expand card to see impact
    const card = screen.getByRole('button', { name: /Mercury Retrograde/i });
    fireEvent.click(card);

    expect(screen.getByText(/Communication delays/i)).toBeInTheDocument();
  });

  it('displays VOC Moon warning when active', () => {
    const guidanceWithVOC: DailyGuidanceType = {
      ...mockGuidance,
      void_of_course_moon: {
        is_void: true,
        current_sign: 'Scorpio',
        moon_degree: 29.5,
        next_sign: 'Sagittarius',
        hours_until_sign_change: 2,
        advice: 'Avoid starting new projects',
      },
    };

    render(<DailyGuidance guidance={guidanceWithVOC} />);

    expect(screen.getByText(/Void-of-Course Moon/i)).toBeInTheDocument();

    // Need to expand card to see details
    const card = screen.getByRole('button', { name: /Void-of-Course Moon/i });
    fireEvent.click(card);

    expect(screen.getByText(/Scorpio/)).toBeInTheDocument();
    expect(screen.getByText(/Sagittarius/)).toBeInTheDocument();
  });

  it('displays current planetary hour when provided', () => {
    const guidanceWithHour: DailyGuidanceType = {
      ...mockGuidance,
      current_planetary_hour: {
        planet: 'Jupiter',
        start: '2:00 PM',
        end: '3:00 PM',
        quality: 'Favorable',
        suggestion: 'Good time for important actions',
      },
    };

    render(<DailyGuidance guidance={guidanceWithHour} />);

    expect(screen.getByText(/Jupiter Hour/i)).toBeInTheDocument();
    expect(screen.getByText('2:00 PM - 3:00 PM')).toBeInTheDocument();

    // Need to expand to see quality and suggestion
    const card = screen.getByRole('button', { name: /Jupiter Hour/i });
    fireEvent.click(card);

    expect(screen.getByText(/Favorable/i)).toBeInTheDocument();
    expect(screen.getByText(/Good time for/i)).toBeInTheDocument();
  });

  it('does not display alerts row when no retrogrades and VOC is false', () => {
    render(<DailyGuidance guidance={mockGuidance} />);

    expect(screen.queryByText(/Retrograde/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Void-of-Course Moon/i)).not.toBeInTheDocument();
  });

  it('displays house-specific impact when available', () => {
    const guidanceWithHouseImpact: DailyGuidanceType = {
      ...mockGuidance,
      retrogrades: [
        {
          planet: 'Venus',
          sign: 'Leo',
          impact: 'Relationship reviews',
          house_impact: 'Partnership commitments questioned',
          avoid: [],
          embrace: [],
        },
      ],
    };

    render(<DailyGuidance guidance={guidanceWithHouseImpact} />);

    // Expand card
    const card = screen.getByRole('button', { name: /Venus Retrograde/i });
    fireEvent.click(card);

    expect(screen.getByText(/Partnership commitments questioned/i)).toBeInTheDocument();
  });
});
