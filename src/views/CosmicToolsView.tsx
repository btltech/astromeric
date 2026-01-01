import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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

type ExpandedTool = 'daily' | 'tarot' | 'oracle' | 'guide' | null;

export function CosmicToolsView({ birthDate, sunSign, moonSign, risingSign }: Props) {
  const { t } = useTranslation();
  const [expandedTool, setExpandedTool] = useState<ExpandedTool>(null);

  const toggleTool = (tool: ExpandedTool) => {
    setExpandedTool(expandedTool === tool ? null : tool);
  };

  // Show gating panel if no birth date
  if (!birthDate) {
    return (
      <div className="gating-panel">
        <div className="gating-icon">🔮</div>
        <h2 className="gating-title">{t('tools.gatingTitle')}</h2>
        <p className="gating-subtitle">{t('tools.gatingSubtitle')}</p>
        <ul className="gating-benefits">
          <li>✓ {t('tools.gatingBenefit1')}</li>
          <li>✓ {t('tools.gatingBenefit2')}</li>
          <li>✓ {t('tools.gatingBenefit3')}</li>
        </ul>
        <Link to="/" className="btn-primary gating-cta">
          {t('tools.goToReading')}
        </Link>
      </div>
    );
  }

  return (
    <div className="cosmic-tools-view redesigned">
      <h2 className="view-title">🌟 Cosmic Tools</h2>
      
      <div className="tools-grid">
        {/* Compatibility Link Card */}
        <Link to="/compatibility" className="tool-card tool-link-card">
          <div className="tool-card-header" style={{ cursor: 'pointer' }}>
            <div className="tool-info">
              <span className="tool-icon">💕</span>
              <div className="tool-text">
                <h3>Compatibility</h3>
                <p>Check your cosmic match</p>
              </div>
            </div>
            <span className="expand-icon">→</span>
          </div>
        </Link>

        {/* Daily Cosmic Card */}
        <div className={`tool-card ${expandedTool === 'daily' ? 'expanded' : ''}`}>
          <button 
            className="tool-card-header"
            onClick={() => toggleTool('daily')}
            aria-expanded={expandedTool === 'daily'}
          >
            <div className="tool-info">
              <span className="tool-icon">✨</span>
              <div className="tool-text">
                <h3>Daily Cosmic</h3>
                <p>Lucky numbers, colors & mood</p>
              </div>
            </div>
            <span className="expand-icon">{expandedTool === 'daily' ? '−' : '+'}</span>
          </button>
          {expandedTool === 'daily' && (
            <div className="tool-card-content">
              {birthDate ? (
                <DailyFeaturesCard birthDate={birthDate} sunSign={sunSign} />
              ) : (
                <p className="tool-placeholder">Enter your birth date in Reading to unlock</p>
              )}
            </div>
          )}
        </div>

        {/* Tarot Card */}
        <div className={`tool-card ${expandedTool === 'tarot' ? 'expanded' : ''}`}>
          <button 
            className="tool-card-header"
            onClick={() => toggleTool('tarot')}
            aria-expanded={expandedTool === 'tarot'}
          >
            <div className="tool-info">
              <span className="tool-icon">🃏</span>
              <div className="tool-text">
                <h3>Tarot Draw</h3>
                <p>Draw a card for guidance</p>
              </div>
            </div>
            <span className="expand-icon">{expandedTool === 'tarot' ? '−' : '+'}</span>
          </button>
          {expandedTool === 'tarot' && (
            <div className="tool-card-content">
              <TarotCard />
            </div>
          )}
        </div>

        {/* Oracle Card */}
        <div className={`tool-card ${expandedTool === 'oracle' ? 'expanded' : ''}`}>
          <button 
            className="tool-card-header"
            onClick={() => toggleTool('oracle')}
            aria-expanded={expandedTool === 'oracle'}
          >
            <div className="tool-info">
              <span className="tool-icon">🔮</span>
              <div className="tool-text">
                <h3>Yes/No Oracle</h3>
                <p>Ask a cosmic question</p>
              </div>
            </div>
            <span className="expand-icon">{expandedTool === 'oracle' ? '−' : '+'}</span>
          </button>
          {expandedTool === 'oracle' && (
            <div className="tool-card-content">
              <OracleYesNo birthDate={birthDate} />
            </div>
          )}
        </div>

        {/* AI Guide Card */}
        <div className={`tool-card ${expandedTool === 'guide' ? 'expanded' : ''}`}>
          <button 
            className="tool-card-header"
            onClick={() => toggleTool('guide')}
            aria-expanded={expandedTool === 'guide'}
          >
            <div className="tool-info">
              <span className="tool-icon">💫</span>
              <div className="tool-text">
                <h3>AI Cosmic Guide</h3>
                <p>Chat with your AI advisor</p>
              </div>
            </div>
            <span className="expand-icon">{expandedTool === 'guide' ? '−' : '+'}</span>
          </button>
          {expandedTool === 'guide' && (
            <div className="tool-card-content">
              <CosmicGuideChat
                sunSign={sunSign}
                moonSign={moonSign}
                risingSign={risingSign}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
