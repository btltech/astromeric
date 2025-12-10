import React from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();

  return (
    <div className="card">
      <h2>{t('compatibility.title')}</h2>
      <p className="section-subtitle">
        {t('compatibility.subtitle')}
      </p>
      <div className="form-group">
        <label>{t('compatibility.compareWith')}</label>
        <select
          value={compareProfile || ''}
          onChange={(e) => onCompareSelect(Number(e.target.value))}
        >
          <option value="">{t('compatibility.chooseProfile')}</option>
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
        {loading ? t('compatibility.calculating') : t('compatibility.calculate')}
      </button>

      {result && <CompatibilityCard data={result} />}
    </div>
  );
}
