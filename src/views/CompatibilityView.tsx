import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useCompatibility, useProfiles } from '../hooks';
import { useStore } from '../store/useStore';
import { CompatibilityCard } from '../components/CompatibilityCard';
import { CardSkeleton } from '../components/Skeleton';
import { toast } from '../components/Toast';
import type { SavedProfile } from '../types';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 },
};

export function CompatibilityView() {
  const { selectedProfile } = useProfiles();
  const { compatibilityResult, fetchCompatibilityFromProfiles } = useCompatibility();
  const { loading } = useStore();

  // Form state for second person
  const [partnerName, setPartnerName] = useState('');
  const [partnerDob, setPartnerDob] = useState('');
  const [partnerTimeOfBirth, setPartnerTimeOfBirth] = useState('');
  const [partnerPlaceOfBirth, setPartnerPlaceOfBirth] = useState('');

  const handleCalculate = async () => {
    if (!selectedProfile || !partnerName || !partnerDob) return;

    // Create a temporary profile for the partner
    const partnerProfile: SavedProfile = {
      id: -Date.now() - 1, // Different negative ID
      name: partnerName,
      date_of_birth: partnerDob,
      time_of_birth: partnerTimeOfBirth || null,
      place_of_birth: partnerPlaceOfBirth || null,
      latitude: null,
      longitude: null,
      timezone: null,
      house_system: null,
    };

    try {
      await fetchCompatibilityFromProfiles(selectedProfile, partnerProfile);
      toast.success('Compatibility analysis complete 💕');
    } catch {
      toast.error('Failed to calculate compatibility');
    }
  };

  if (!selectedProfile) {
    return (
      <motion.div className="card" {...fadeIn}>
        <p className="empty-state">Please enter your birth details first from the Reading tab.</p>
      </motion.div>
    );
  }

  const isFormValid = partnerName.trim() && partnerDob;

  return (
    <motion.div className="card" {...fadeIn}>
      <h2>💕 Compatibility Check</h2>
      <p className="section-subtitle">Compare your cosmic alignment with someone special</p>

      <div className="your-profile-box">
        <strong>Your Profile:</strong> {selectedProfile.name} ({selectedProfile.date_of_birth})
      </div>

      <div className="form-group">
        <label htmlFor="partner-name">Partner's Name *</label>
        <input
          id="partner-name"
          type="text"
          value={partnerName}
          onChange={(e) => setPartnerName(e.target.value)}
          placeholder="Enter their name"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="partner-dob">Partner's Date of Birth *</label>
        <input
          id="partner-dob"
          type="date"
          value={partnerDob}
          onChange={(e) => setPartnerDob(e.target.value)}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="partner-time">Time of Birth (optional)</label>
        <input
          id="partner-time"
          type="time"
          value={partnerTimeOfBirth}
          onChange={(e) => setPartnerTimeOfBirth(e.target.value)}
        />
      </div>

      <div className="form-group">
        <label htmlFor="partner-place">Place of Birth (optional)</label>
        <input
          id="partner-place"
          type="text"
          value={partnerPlaceOfBirth}
          onChange={(e) => setPartnerPlaceOfBirth(e.target.value)}
          placeholder="City, Country"
        />
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleCalculate}
        className="btn-primary"
        disabled={loading || !isFormValid}
      >
        {loading ? 'Calculating...' : 'Calculate Compatibility'}
      </motion.button>

      {loading && !compatibilityResult && <CardSkeleton />}

      {compatibilityResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <CompatibilityCard data={compatibilityResult} />
        </motion.div>
      )}
    </motion.div>
  );
}
