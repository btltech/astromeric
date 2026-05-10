import React, { useEffect, useState } from 'react';
import { fetchCurrentMoonPhase, fetchUpcomingMoonEvents } from '../api/client';
import type { MoonEvent, MoonPhaseInfo } from '../types';

export function MoonPhaseCard() {
  const [phase, setPhase] = useState<MoonPhaseInfo | null>(null);
  const [upcomingEvents, setUpcomingEvents] = useState<MoonEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadMoonSignals() {
      setLoading(true);
      setError(null);

      const [phaseResult, eventsResult] = await Promise.allSettled([
        fetchCurrentMoonPhase(),
        fetchUpcomingMoonEvents(7),
      ]);

      if (isCancelled) {
        return;
      }

      if (phaseResult.status === 'fulfilled') {
        setPhase(phaseResult.value);
      } else {
        setPhase(null);
        setError('The lunar signal is still resolving. Reopen this panel in a moment.');
      }

      if (eventsResult.status === 'fulfilled') {
        setUpcomingEvents(eventsResult.value.slice(0, 3));
      } else {
        setUpcomingEvents([]);
      }

      setLoading(false);
    }

    loadMoonSignals();

    return () => {
      isCancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="product-desk__stack">
        <div>
          <h2>Moon phase</h2>
          <p className="product-desk__note">Loading the current lunar phase and next handoff.</p>
        </div>
      </div>
    );
  }

  if (error || !phase) {
    return (
      <div className="product-desk__stack">
        <div>
          <h2>Moon phase</h2>
          <p className="product-desk__note">{error ?? 'Moon phase data is unavailable right now.'}</p>
        </div>
      </div>
    );
  }

  const direction = phase.is_waxing ? 'Waxing' : phase.is_waning ? 'Waning' : 'Balanced';

  return (
    <div className="product-desk__stack">
      <div>
        <h2>Moon phase</h2>
        <p className="product-desk__note">Current lunar weather, phase strength, and the next notable handoff.</p>
      </div>

      <div className="product-desk__stats">
        <div className="product-desk__stat">
          <span className="product-desk__label">Current phase</span>
          <span className="product-desk__value">{`${phase.emoji} ${phase.phase_name}`}</span>
        </div>
        <div className="product-desk__stat">
          <span className="product-desk__label">Illumination</span>
          <span className="product-desk__value">{`${Math.round(phase.illumination)}% lit`}</span>
        </div>
        <div className="product-desk__stat">
          <span className="product-desk__label">Direction</span>
          <span className="product-desk__value">{direction}</span>
        </div>
      </div>

      <p className="product-desk__note">
        {phase.days_until_next_phase > 0
          ? `${phase.days_until_next_phase} day${phase.days_until_next_phase === 1 ? '' : 's'} until the next phase transition.`
          : 'A phase transition is imminent.'}
      </p>

      {upcomingEvents.length > 0 && (
        <ul className="product-desk__list">
          {upcomingEvents.map((event) => (
            <li key={`${event.type}-${event.date}`} className="product-desk__list-item">
              <div>
                <strong>{`${event.emoji} ${event.type}`}</strong>
                <span className="product-desk__meta">{`${event.sign} · ${event.days_away} day${event.days_away === 1 ? '' : 's'} away`}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MoonPhaseCard;