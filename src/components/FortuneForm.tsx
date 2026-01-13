import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import type { NewProfileForm } from '../types';
import { LocationAutocomplete } from './LocationAutocomplete';

interface Props {
  onSubmit: (data: NewProfileForm) => void;
  isLoading: boolean;
  showSaveOption?: boolean;
}

const slideVariants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 1000 : -1000,
    opacity: 0,
  }),
  center: {
    zIndex: 1,
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    zIndex: 0,
    x: direction < 0 ? 1000 : -1000,
    opacity: 0,
  }),
};

export function FortuneForm({ onSubmit, isLoading, showSaveOption = true }: Props) {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);
  const [direction, setDirection] = useState(0);
  const [formData, setFormData] = useState<NewProfileForm>({
    name: '',
    date_of_birth: '',
    time_of_birth: '',
    place_of_birth: '',
    saveProfile: false,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const nextStep = () => {
    if (step === 1 && !formData.name.trim()) {
      setErrors({ name: t('form.errors.nameRequired') });
      return;
    }
    if (step === 2 && !formData.date_of_birth) {
      setErrors({ date_of_birth: t('form.errors.dobRequired') });
      return;
    }
    setErrors({});
    setDirection(1);
    setStep((v) => v + 1);
  };

  const prevStep = () => {
    setDirection(-1);
    setStep((v) => v - 1);
  };

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

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="card wizard-card">
      <div className="wizard-progress">
        {[1, 2, 3, 4].map((s) => (
          <div
            key={s}
            className={`wizard-dot ${s === step ? 'active' : ''} ${s < step ? 'completed' : ''}`}
          />
        ))}
      </div>

      <AnimatePresence initial={false} custom={direction} mode="wait">
        <motion.div
          key={step}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            x: { type: 'spring', stiffness: 300, damping: 30 },
            opacity: { duration: 0.2 },
          }}
          className="wizard-content"
        >
          {step === 1 && (
            <div className="step-container">
              <h2>{t('wizard.step1.title', 'Welcome. What is your name?')}</h2>
              <div className="form-group">
                <input
                  autoFocus
                  type="text"
                  placeholder={t('form.fullNamePlaceholder')}
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  onKeyDown={(e) => e.key === 'Enter' && nextStep()}
                />
                {errors.name && <p className="error-text">{errors.name}</p>}
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="step-container">
              <h2>{t('wizard.step2.title', 'When were you born?')}</h2>
              <div className="form-group">
                <input
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  onKeyDown={(e) => e.key === 'Enter' && nextStep()}
                />
                {errors.date_of_birth && <p className="error-text">{errors.date_of_birth}</p>}
              </div>
              <div className="form-group">
                <label>
                  {t('form.timeOfBirth')} ({t('common.optional', 'optional')})
                </label>
                <input
                  type="time"
                  value={formData.time_of_birth}
                  onChange={(e) => setFormData({ ...formData, time_of_birth: e.target.value })}
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="step-container">
              <h2>{t('wizard.step3.title', 'Where were you born?')}</h2>
              <div className="form-group">
                <LocationAutocomplete
                  onSelect={handleLocationSelect}
                  placeholder={t('form.searchCity')}
                  initialValue={formData.place_of_birth}
                />
                {formData.timezone && <p className="geo-indicator">📍 {formData.timezone}</p>}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="step-container">
              <h2>{t('wizard.step4.title', 'Ready for your destiny?')}</h2>
              <p>{t('wizard.step4.text', 'Confirm your details and let the stars align.')}</p>
              <div className="wizard-summary">
                <p>
                  <strong>{formData.name}</strong>
                </p>
                <p>
                  {formData.date_of_birth} {formData.time_of_birth}
                </p>
                <p>{formData.place_of_birth}</p>
              </div>
              {showSaveOption && (
                <div className="form-group save-profile-row">
                  <input
                    type="checkbox"
                    id="saveProfile"
                    checked={formData.saveProfile}
                    onChange={(e) => setFormData({ ...formData, saveProfile: e.target.checked })}
                  />
                  <label htmlFor="saveProfile">{t('form.saveProfile')}</label>
                </div>
              )}
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      <div className="wizard-footer">
        {step > 1 && (
          <button className="btn-secondary" onClick={prevStep} disabled={isLoading}>
            {t('common.back', 'Back')}
          </button>
        )}
        {step < 4 ? (
          <button className="btn-primary" onClick={nextStep} style={{ marginLeft: 'auto' }}>
            {t('common.next', 'Next')}
          </button>
        ) : (
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={isLoading}
            style={{ marginLeft: 'auto' }}
          >
            {isLoading ? t('form.readingStars') : t('form.getPrediction')}
          </button>
        )}
      </div>
    </div>
  );
}
