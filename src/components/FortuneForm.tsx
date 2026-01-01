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
    <div className="card form-card-compact">
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
        <div className="form-row-2col">
          <div className="form-group">
            <label htmlFor="date_of_birth">{t('form.dateOfBirth')}</label>
            <input
              id="date_of_birth"
              type="date"
              required
              value={formData.date_of_birth}
              onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
              aria-invalid={!!errors.date_of_birth}
              aria-describedby={errors.date_of_birth ? "dob-error" : "dob-hint"}
            />
            <span id="dob-hint" className="field-hint">{t('form.dateOfBirthHint')}</span>
            {errors.date_of_birth && <div id="dob-error" className="error-text" role="alert">{errors.date_of_birth}</div>}
          </div>
          <div className="form-group">
            <label htmlFor="time_of_birth">{t('form.timeOfBirth')} (recommended)</label>
            <input
              id="time_of_birth"
              type="time"
              value={formData.time_of_birth}
              onChange={(e) => setFormData({ ...formData, time_of_birth: e.target.value })}
              aria-describedby="tob-hint"
            />
            <span id="tob-hint" className="field-hint">
              Birth time improves chart accuracy. Add location/timezone for best results.
            </span>
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="place_of_birth">{t('form.placeOfBirth')} (recommended)</label>
          <div id="place_of_birth">
            <LocationAutocomplete
              onSelect={handleLocationSelect}
              placeholder={t('form.searchCity')}
              initialValue={formData.place_of_birth}
            />
          </div>
          <span id="pob-hint" className="field-hint">
            Location/timezone improve accuracy and timing. You can still generate a reading without them.
          </span>
          {formData.latitude && formData.longitude && (
            <div className="geo-indicator">
              📍 {formData.latitude.toFixed(4)}, {formData.longitude.toFixed(4)} •{' '}
              {formData.timezone}
            </div>
          )}
        </div>
        <div className="form-group save-profile-row">
          <div className="save-profile-checkbox">
            <input
              type="checkbox"
              id="saveProfile"
              checked={formData.saveProfile || false}
              onChange={(e) => setFormData({ ...formData, saveProfile: e.target.checked })}
              className="save-checkbox"
            />
            <label htmlFor="saveProfile">
              {t('form.saveProfile')}
            </label>
            <span className="info-tooltip" data-tooltip={t('form.saveProfileHint')}>ⓘ</span>
          </div>
          <span className="field-hint" id="saveprofile-hint">
            {t('form.saveProfileHint')}
          </span>
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
