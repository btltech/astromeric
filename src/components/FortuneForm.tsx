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
          <label>Full Name</label>
          <input
            type="text"
            required
            placeholder="e.g. Jane Doe"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          {errors.name && <div className="error-text">{errors.name}</div>}
        </div>
        <div className="form-group">
          <label>Date of Birth</label>
          <input
            type="date"
            required
            value={formData.date_of_birth}
            onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
          />
          {errors.date_of_birth && <div className="error-text">{errors.date_of_birth}</div>}
        </div>
        <div className="form-group">
          <label>Time of Birth (Optional)</label>
          <input
            type="time"
            value={formData.time_of_birth}
            onChange={(e) => setFormData({ ...formData, time_of_birth: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>Place of Birth (Optional)</label>
          <LocationAutocomplete
            onSelect={handleLocationSelect}
            placeholder="Search city..."
            initialValue={formData.place_of_birth}
          />
          {formData.latitude && formData.longitude && (
            <div style={{ fontSize: 12, color: '#4ecdc4', marginTop: 4 }}>
              📍 {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(4)} •{' '}
              {formData.timezone}
            </div>
          )}
        </div>
        <button type="submit" className="btn-primary" disabled={isLoading}>
          {isLoading ? 'Reading the Stars...' : "Get Today's Prediction"}
        </button>
      </form>
    </div>
  );
}
