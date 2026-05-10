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

const wizardSteps = [
  {
    id: 1,
    label: 'Identity',
    eyebrow: 'Step 1 of 4',
    title: 'Welcome. What is your name?',
    description: 'Start the profile with the name you want tied to readings and saved history.',
    hint: 'You can rename this later if you want a cleaner label for shared or synced profiles.',
  },
  {
    id: 2,
    label: 'Birth time',
    eyebrow: 'Step 2 of 4',
    title: 'When were you born?',
    description: 'Your birth date powers the base reading. Add birth time too when you want sharper chart timing.',
    hint: 'Time of birth is optional, but it improves house placement and timing-heavy views.',
  },
  {
    id: 3,
    label: 'Birth place',
    eyebrow: 'Step 3 of 4',
    title: 'Where were you born?',
    description: 'Choose the city or town that anchors timezone and geographic context for the chart.',
    hint: 'Pick a specific place so the live reading can land in the right timezone.',
  },
  {
    id: 4,
    label: 'Confirm',
    eyebrow: 'Step 4 of 4',
    title: 'Ready for your destiny?',
    description: 'Review the profile before the reading desk turns this setup into live guidance.',
    hint: 'You can save the profile for reuse across the reading, chart, and compatibility flows.',
  },
] as const;

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
  const currentStep = wizardSteps[step - 1];
  const completionPercent = ((step - 1) / (wizardSteps.length - 1)) * 100;
  const locationIsSelected = Boolean(formData.place_of_birth && formData.timezone);

  const nextStep = () => {
    if (step === 1 && !formData.name.trim()) {
      setErrors({ name: t('form.errors.nameRequired') });
      return;
    }
    if (step === 2 && !formData.date_of_birth) {
      setErrors({ date_of_birth: t('form.errors.dobRequired') });
      return;
    }
    if (step === 3 && !locationIsSelected) {
      setErrors({ place_of_birth: 'Choose a birth place from the search results before continuing.' });
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
    setErrors((currentErrors) => {
      const nextErrors = { ...currentErrors };
      delete nextErrors.place_of_birth;
      return nextErrors;
    });

    setFormData({
      ...formData,
      place_of_birth: location.name,
      latitude: location.latitude,
      longitude: location.longitude,
      timezone: location.timezone,
    });
  };

  const handleLocationQueryChange = (query: string) => {
    setErrors((currentErrors) => {
      if (!currentErrors.place_of_birth) {
        return currentErrors;
      }

      const nextErrors = { ...currentErrors };
      delete nextErrors.place_of_birth;
      return nextErrors;
    });

    setFormData((current) => {
      if (query.trim() === current.place_of_birth) {
        return current;
      }

      if (!current.place_of_birth && !current.timezone && current.latitude == null && current.longitude == null) {
        return current;
      }

      return {
        ...current,
        place_of_birth: '',
        latitude: undefined,
        longitude: undefined,
        timezone: undefined,
      };
    });
  };

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="card wizard-card">
      <div className="wizard-shell">
        <div className="wizard-progress-header">
          <div>
            <span className="wizard-progress-header__eyebrow">{currentStep.eyebrow}</span>
            <strong>{currentStep.label}</strong>
          </div>
          <span className="wizard-progress-header__value">{Math.round(completionPercent)}%</span>
        </div>

        <div className="wizard-progress" aria-label="Profile creation progress">
          {wizardSteps.map((wizardStep) => (
            <div
              key={wizardStep.id}
              className={
                wizardStep.id === step
                  ? 'wizard-step wizard-step--active'
                  : wizardStep.id < step
                    ? 'wizard-step wizard-step--completed'
                    : 'wizard-step'
              }
            >
              <div className="wizard-dot">{wizardStep.id}</div>
              <span>{wizardStep.label}</span>
            </div>
          ))}
        </div>

        <div className="wizard-intro">
          <h2>{t(`wizard.step${step}.title`, currentStep.title)}</h2>
          <p>{currentStep.description}</p>
          <div className="wizard-hint">{currentStep.hint}</div>
        </div>
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
              <div className="form-group">
                <LocationAutocomplete
                  onSelect={handleLocationSelect}
                  onQueryChange={handleLocationQueryChange}
                  placeholder={t('form.searchCity')}
                  initialValue={formData.place_of_birth}
                />
                {errors.place_of_birth && <p className="error-text">{errors.place_of_birth}</p>}
                {formData.timezone && <p className="geo-indicator">📍 {formData.timezone}</p>}
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="step-container">
              <div className="wizard-summary">
                <article className="wizard-summary__item">
                  <span>Name</span>
                  <strong>{formData.name}</strong>
                </article>
                <article className="wizard-summary__item">
                  <span>Birth date</span>
                  <strong>
                    {formData.date_of_birth}
                    {formData.time_of_birth ? ` at ${formData.time_of_birth}` : ' · time not added'}
                  </strong>
                </article>
                <article className="wizard-summary__item">
                  <span>Birth place</span>
                  <strong>{formData.place_of_birth || 'Location not added yet'}</strong>
                </article>
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
