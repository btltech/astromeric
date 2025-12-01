import React, { useState } from 'react';
import { DailyFeaturesCard } from '../components/DailyFeaturesCard';
import { TarotCard } from '../components/TarotCard';
import { OracleYesNo } from '../components/OracleYesNo';
import { CosmicGuideChat } from '../components/CosmicGuideChat';

interface Props {
  birthDate?: string;
  sunSign?: string;
  moonSign?: string;
  risingSign?: string;
}

type Tab = 'daily' | 'tarot' | 'oracle' | 'guide';

export function CosmicToolsView({ birthDate, sunSign, moonSign, risingSign }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('daily');

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'daily', label: 'Daily Cosmic', icon: '✨' },
    { id: 'tarot', label: 'Tarot', icon: '🃏' },
    { id: 'oracle', label: 'Oracle', icon: '🔮' },
    { id: 'guide', label: 'Cosmic Guide', icon: '💫' },
  ];

  return (
    <div className="cosmic-tools-view">
      <h2 className="view-title">🌟 Cosmic Tools & Entertainment</h2>
      <p className="view-subtitle">
        Explore mystical insights, draw tarot cards, consult the oracle, or chat with your AI guide
      </p>

      <div className="tools-tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="tools-content">
        {activeTab === 'daily' && birthDate && (
          <DailyFeaturesCard birthDate={birthDate} sunSign={sunSign} />
        )}
        {activeTab === 'daily' && !birthDate && (
          <div className="placeholder-message">
            <p>Enter your birth date in your Reading to unlock Daily Cosmic features</p>
          </div>
        )}

        {activeTab === 'tarot' && <TarotCard />}

        {activeTab === 'oracle' && <OracleYesNo birthDate={birthDate} />}

        {activeTab === 'guide' && (
          <CosmicGuideChat
            sunSign={sunSign}
            moonSign={moonSign}
            risingSign={risingSign}
          />
        )}
      </div>
    </div>
  );
}
