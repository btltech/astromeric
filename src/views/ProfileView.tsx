import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useStore } from '../store/useStore';
import { useProfiles } from '../hooks';
import { toast } from '../components/Toast';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 },
};

interface ProfileFormData {
  name: string;
  date_of_birth: string;
  time_of_birth: string;
  place_of_birth: string;
  latitude: number | null;
  longitude: number | null;
  timezone: string;
}

export function ProfileView() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, token } = useStore();
  const { profiles, selectedProfile, createProfile, fetchProfiles } = useProfiles();

  const [formData, setFormData] = useState<ProfileFormData>({
    name: '',
    date_of_birth: '',
    time_of_birth: '',
    place_of_birth: '',
    latitude: null,
    longitude: null,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  });
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);

  // Redirect if not logged in
  useEffect(() => {
    if (!token) {
      navigate('/auth');
    }
  }, [token, navigate]);

  // Load existing profile data if available
  useEffect(() => {
    if (selectedProfile) {
      setFormData({
        name: selectedProfile.name || '',
        date_of_birth: selectedProfile.date_of_birth || '',
        time_of_birth: selectedProfile.time_of_birth || '',
        place_of_birth: selectedProfile.place_of_birth || '',
        latitude: selectedProfile.latitude || null,
        longitude: selectedProfile.longitude || null,
        timezone: selectedProfile.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
    }
  }, [selectedProfile]);

  // Fetch profiles on mount
  useEffect(() => {
    if (token) {
      fetchProfiles();
    }
  }, [token, fetchProfiles]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.date_of_birth) {
      toast.error(t('profile.errors.requiredFields'));
      return;
    }

    setSaving(true);
    try {
      await createProfile({
        name: formData.name,
        date_of_birth: formData.date_of_birth,
        time_of_birth: formData.time_of_birth || undefined,
        place_of_birth: formData.place_of_birth || undefined,
        latitude: formData.latitude || undefined,
        longitude: formData.longitude || undefined,
        timezone: formData.timezone,
        saveProfile: true,
      });
      toast.success(t('profile.saved'));
      setEditMode(false);
      // Navigate to reading page after saving
      navigate('/');
    } catch (err) {
      toast.error(t('profile.errors.saveFailed'));
    } finally {
      setSaving(false);
    }
  };

  const hasProfile = profiles.length > 0 || selectedProfile;

  if (!user) {
    return null;
  }

  return (
    <motion.div className="page profile-view" {...fadeIn}>
      {/* Account Info Card */}
      <div className="card profile-card">
        <div className="profile-header">
          <div className="profile-avatar">{user.email.charAt(0).toUpperCase()}</div>
          <div className="profile-info">
            <h2>{t('profile.title')}</h2>
            <p className="profile-email">{user.email}</p>
            {user.is_paid && <span className="premium-badge">✨ {t('profile.premium')}</span>}
          </div>
        </div>
      </div>

      {/* Profile Details Card */}
      <div className="card">
        <div className="card-header-row">
          <h3>{t('profile.birthDetails')}</h3>
          {hasProfile && !editMode && (
            <button className="btn-secondary btn-sm btn-inline" onClick={() => setEditMode(true)}>
              {t('profile.edit')}
            </button>
          )}
        </div>

        {!hasProfile || editMode ? (
          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-group">
              <label htmlFor="name">{t('form.fullName')} *</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder={t('form.fullNamePlaceholder')}
                required
              />
            </div>

            <div className="form-row-2col">
              <div className="form-group">
                <label htmlFor="date_of_birth">{t('form.dateOfBirth')} *</label>
                <input
                  id="date_of_birth"
                  type="date"
                  value={formData.date_of_birth}
                  onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  required
                />
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
            </div>

            <div className="form-group">
              <label htmlFor="place_of_birth">{t('form.placeOfBirth')}</label>
              <input
                id="place_of_birth"
                type="text"
                value={formData.place_of_birth}
                onChange={(e) => setFormData({ ...formData, place_of_birth: e.target.value })}
                placeholder={t('form.searchCity')}
              />
            </div>

            <div className="form-actions">
              {editMode && (
                <button
                  type="button"
                  className="btn-secondary btn-inline"
                  onClick={() => setEditMode(false)}
                >
                  {t('common.cancel')}
                </button>
              )}
              <button type="submit" className="btn-primary btn-inline" disabled={saving}>
                {saving ? t('common.loading') : t('profile.saveProfile')}
              </button>
            </div>
          </form>
        ) : (
          <div className="profile-details">
            <div className="detail-row">
              <span className="detail-label">{t('form.fullName')}</span>
              <span className="detail-value">{selectedProfile?.name || '—'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">{t('form.dateOfBirth')}</span>
              <span className="detail-value">{selectedProfile?.date_of_birth || '—'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">{t('form.timeOfBirth')}</span>
              <span className="detail-value">{selectedProfile?.time_of_birth || '—'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">{t('form.placeOfBirth')}</span>
              <span className="detail-value">{selectedProfile?.place_of_birth || '—'}</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3>{t('profile.quickActions')}</h3>
        <div className="quick-actions">
          <button className="btn-primary" onClick={() => navigate('/')}>
            ✨ {t('nav.reading')}
          </button>
          <button className="btn-secondary" onClick={() => navigate('/numerology')}>
            🔢 {t('nav.numbers')}
          </button>
          <button className="btn-secondary" onClick={() => navigate('/tools')}>
            🔮 {t('nav.tools')}
          </button>
        </div>
      </div>
    </motion.div>
  );
}
