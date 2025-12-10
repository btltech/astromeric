import React from 'react';
import { useTranslation } from 'react-i18next';
import type { SavedProfile } from '../types';

interface Props {
  profiles: SavedProfile[];
  selectedProfile: number | null;
  onSelectProfile: (id: number) => void;
  showCreateForm: boolean;
  onToggleCreate: () => void;
}

export function ProfileSelector({
  profiles,
  selectedProfile,
  onSelectProfile,
  showCreateForm,
  onToggleCreate,
}: Props) {
  const { t } = useTranslation();

  return (
    <div className="card">
      <h2>{t('profile.selectOrCreate')}</h2>
      {profiles.length > 0 && (
        <div className="form-group">
          <label>{t('profile.selectProfile')}</label>
          <select
            value={selectedProfile || ''}
            onChange={(e) => onSelectProfile(Number(e.target.value))}
          >
            <option value="">{t('profile.choose')}</option>
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.date_of_birth})
              </option>
            ))}
          </select>
        </div>
      )}
      <button onClick={onToggleCreate} className="btn-secondary">
        {showCreateForm ? t('common.cancel') : t('profile.createNew')}
      </button>
    </div>
  );
}
