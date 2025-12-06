import React, { useState, useRef, useEffect } from 'react';
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
  const tabRefs = useRef<{ [key: string]: HTMLButtonElement | null }>({});

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'daily', label: 'Daily Cosmic', icon: '✨' },
    { id: 'tarot', label: 'Tarot', icon: '🃏' },
    { id: 'oracle', label: 'Oracle', icon: '🔮' },
    { id: 'guide', label: 'Cosmic Guide', icon: '💫' },
  ];

  const handleKeyDown = (e: React.KeyboardEvent, currentIndex: number) => {
    let newIndex = currentIndex;
    if (e.key === 'ArrowRight') {
      newIndex = (currentIndex + 1) % tabs.length;
    } else if (e.key === 'ArrowLeft') {
      newIndex = (currentIndex - 1 + tabs.length) % tabs.length;
    } else {
      return;
    }
    const newTab = tabs[newIndex];
    setActiveTab(newTab.id);
    tabRefs.current[newTab.id]?.focus();
  };

  return (
    <div className="cosmic-tools-view">
      <h2 className="view-title">🌟 Cosmic Tools & Entertainment</h2>
      <p className="view-subtitle">
        Explore mystical insights, draw tarot cards, consult the oracle, or chat with your AI guide
      </p>

      <div className="tools-tabs" role="tablist" aria-label="Cosmic tools">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            ref={(el) => { tabRefs.current[tab.id] = el; }}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`${tab.id}-panel`}
            id={`${tab.id}-tab`}
            tabIndex={activeTab === tab.id ? 0 : -1}
            className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            onKeyDown={(e) => handleKeyDown(e, index)}
          >
            <span className="tab-icon" aria-hidden="true">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="tools-content">
        <div
          role="tabpanel"
          id="daily-panel"
          aria-labelledby="daily-tab"
          hidden={activeTab !== 'daily'}
        >
          {activeTab === 'daily' && birthDate && (
            <DailyFeaturesCard birthDate={birthDate} sunSign={sunSign} />
          )}
          {activeTab === 'daily' && !birthDate && (
            <div className="placeholder-message">
              <p>Enter your birth date in your Reading to unlock Daily Cosmic features</p>
            </div>
          )}
        </div>

        <div
          role="tabpanel"
          id="tarot-panel"
          aria-labelledby="tarot-tab"
          hidden={activeTab !== 'tarot'}
        >
          {activeTab === 'tarot' && <TarotCard />}
        </div>

        <div
          role="tabpanel"
          id="oracle-panel"
          aria-labelledby="oracle-tab"
          hidden={activeTab !== 'oracle'}
        >
          {activeTab === 'oracle' && <OracleYesNo birthDate={birthDate} />}
        </div>

        <div
          role="tabpanel"
          id="guide-panel"
          aria-labelledby="guide-tab"
          hidden={activeTab !== 'guide'}
        >
          {activeTab === 'guide' && (
            <CosmicGuideChat
              sunSign={sunSign}
              moonSign={moonSign}
              risingSign={risingSign}
            />
          )}
        </div>
      </div>
    </div>
  );
}
