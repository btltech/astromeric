import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { NewProfileForm } from '../types';
import { LocationAutocomplete } from './LocationAutocomplete';

interface Props {
  onSubmit: (data: NewProfileForm) => void;
  isLoading: boolean;
}

export function FortuneForm({ onSubmit, isLoading }: Props) {
  const { t } = useTranslation();
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
    if (!formData.name.trim()) newErrors.name = t('form.errors.nameRequired');
    if (!formData.date_of_birth) newErrors.date_of_birth = t('form.errors.dobRequired');
    else {
      const dob = new Date(formData.date_of_birth);
      const today = new Date();
      if (dob > today) newErrors.date_of_birth = t('form.errors.dobFuture');
    }
    setErrors(newErrors);
    if (Object.keys(newErrors).length) return;
    onSubmit(formData);
  };

  return (
    <div className="card">
      <h2 className="form-title">{t('form.title')}</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">{t('form.fullName')}</label>
          <input
            id="name"
            type="text"
            required
            placeholder={t('form.fullNamePlaceholder')}
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            aria-invalid={!!errors.name}
            aria-describedby={errors.name ? "name-error" : undefined}
          />
          {errors.name && <div id="name-error" className="error-text" role="alert">{errors.name}</div>}
        </div>
        <div className="form-group">
          <label htmlFor="date_of_birth">{t('form.dateOfBirth')}</label>
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
          <label htmlFor="time_of_birth">{t('form.timeOfBirth')}</label>
          <input
            id="time_of_birth"
            type="time"
            value={formData.time_of_birth}
            onChange={(e) => setFormData({ ...formData, time_of_birth: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label htmlFor="place_of_birth">{t('form.placeOfBirth')}</label>
          <div id="place_of_birth">
            <LocationAutocomplete
              onSelect={handleLocationSelect}
              placeholder={t('form.searchCity')}
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
            className="save-checkbox"
          />
          <label htmlFor="saveProfile" style={{ margin: 0, cursor: 'pointer' }}>
            {t('form.saveProfile')}
          </label>
        </div>
        <div className="form-footer">
          <p className="privacy-note">
            {t('form.privacyNote')}
          </p>
          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? t('form.readingStars') : t('form.getPrediction')}
          </button>
        </div>
      </form>
    </div>
  );
}
