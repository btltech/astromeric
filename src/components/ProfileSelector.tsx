import React from 'react';
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
  return (
    <div className="card">
      <h2>Select or Create Profile</h2>
      {profiles.length > 0 && (
        <div className="form-group">
          <label>Select Profile</label>
          <select
            value={selectedProfile || ''}
            onChange={(e) => onSelectProfile(Number(e.target.value))}
          >
            <option value="">Choose...</option>
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.date_of_birth})
              </option>
            ))}
          </select>
        </div>
      )}
      <button onClick={onToggleCreate} className="btn-secondary">
        {showCreateForm ? 'Cancel' : 'Create New Profile'}
      </button>
    </div>
  );
}
