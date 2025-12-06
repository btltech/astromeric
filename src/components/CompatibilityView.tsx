import React from 'react';
import type { SavedProfile, CompatibilityResult } from '../types';
import { CompatibilityCard } from './CompatibilityCard';

interface Props {
  profiles: SavedProfile[];
  selectedProfile: number | null;
  compareProfile: number | null;
  onCompareSelect: (id: number) => void;
  onCalculate: () => void;
  loading: boolean;
  result: CompatibilityResult | null;
}

export function CompatibilityView({
  profiles,
  selectedProfile,
  compareProfile,
  onCompareSelect,
  onCalculate,
  loading,
  result,
}: Props) {
  return (
    <div className="card">
      <h2>💕 Compatibility Check</h2>
      <p className="section-subtitle">
        Compare your cosmic alignment with another profile
      </p>
      <div className="form-group">
        <label>Compare With</label>
        <select
          value={compareProfile || ''}
          onChange={(e) => onCompareSelect(Number(e.target.value))}
        >
          <option value="">Choose a profile...</option>
          {profiles
            .filter((p) => p.id !== selectedProfile)
            .map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.date_of_birth})
              </option>
            ))}
        </select>
      </div>
      <button onClick={onCalculate} className="btn-primary" disabled={loading || !compareProfile}>
        {loading ? 'Calculating...' : 'Calculate Compatibility'}
      </button>

      {result && <CompatibilityCard data={result} />}
    </div>
  );
}
