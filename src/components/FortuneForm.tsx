import React, { useState } from 'react';
import type { NewProfileForm } from '../types';
import { LocationAutocomplete } from './LocationAutocomplete';

interface Props {
  onSubmit: (data: NewProfileForm) => void;
  isLoading: boolean;
}

export function FortuneForm({ onSubmit, isLoading }: Props) {
  const [formData, setFormData] = useState<NewProfileForm>({
    name: '',
    date_of_birth: '',
    time_of_birth: '',
    place_of_birth: '',
    saveProfile: false, // Default: do NOT save profile
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleLocationSelect = (location: {
    name: string;
    latitude: number;
    longitude: number;
    timezone: string;
  }) => {
    setFormData({
      ...formData,
      place_of_birth: location.name,
      latitude: location.latitude,
      longitude: location.longitude,
      timezone: location.timezone,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = 'Please enter your full name.';
    if (!formData.date_of_birth) newErrors.date_of_birth = 'Please provide your date of birth.';
    else {
      const dob = new Date(formData.date_of_birth);
      const today = new Date();
      if (dob > today) newErrors.date_of_birth = 'Date of birth cannot be in the future.';
    }
    setErrors(newErrors);
    if (Object.keys(newErrors).length) return;
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2 className="form-title">Enter Your Details</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Full Name</label>
          <input
            id="name"
            type="text"
            required
            placeholder="e.g. Jane Doe"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? "name-error" : undefined}
          />
          {errors.name && <div id="name-error" className="error-text" role="alert">{errors.name}</div>}
        </div>
        <div className="form-group">
          <label htmlFor="date_of_birth">Date of Birth</label>
          <input
            id="date_of_birth"
            type="date"
            required
            value={formData.date_of_birth}
            onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
            aria-invalid={!!errors.date_of_birth}
            aria-describedby={errors.date_of_birth ? "dob-error" : undefined}
          />
          {errors.date_of_birth && <div id="dob-error" className="error-text" role="alert">{errors.date_of_birth}</div>}
        </div>
        <div className="form-group">
          <label htmlFor="time_of_birth">Time of Birth (Optional)</label>
          <input
            id="time_of_birth"
            type="time"
            value={formData.time_of_birth}
            onChange={(e) => setFormData({ ...formData, time_of_birth: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="place_of_birth">Place of Birth (Optional)</label>
          <div id="place_of_birth">
            <LocationAutocomplete
              onSelect={handleLocationSelect}
              placeholder="Search city..."
              initialValue={formData.place_of_birth}
            />
          </div>
          {formData.latitude && formData.longitude && (
            <div className="geo-indicator">
              📍 {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(4)} •{' '}
              {formData.timezone}
            </div>
          )}
        </div>
        <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="checkbox"
            id="saveProfile"
            checked={formData.saveProfile || false}
            onChange={(e) => setFormData({ ...formData, saveProfile: e.target.checked })}
            style={{ width: 'auto', margin: 0 }}
          />
          <label htmlFor="saveProfile" style={{ margin: 0, cursor: 'pointer' }}>
            Save my profile for future readings
          </label>
        </div>
        <p className="privacy-note">
          Your data is only used to generate your reading. Check the box above to save your profile for future visits.
        </p>
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? 'Reading the Stars...' : "Get Today's Prediction"}
        </button>
      </form>
    </div>
  );
}
