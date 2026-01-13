import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type {
  PredictionData,
  RetrogradeInfo,
  VoidOfCourseMoon,
  PlanetaryHourInfo,
  ColorInfo,
} from '../types';

// Helper to get color hex and name from color data (supports both string and object formats)
function getColorData(color: string | ColorInfo): { hex: string; name: string } {
  if (typeof color === 'string') {
    return { hex: color.toLowerCase(), name: color };
  }
  return { hex: color.hex, name: color.name };
}

// Scope-aware text helpers
function getScopeLabel(scope: string): { title: string; period: string; periodLong: string } {
  switch (scope) {
    case 'weekly':
      return { title: 'Weekly Cosmic Guidance', period: 'This Week', periodLong: 'this week' };
    case 'monthly':
      return { title: 'Monthly Cosmic Guidance', period: 'This Month', periodLong: 'this month' };
    default:
      return { title: 'Daily Cosmic Guidance', period: 'Today', periodLong: 'today' };
  }
}

interface Props {
  guidance: NonNullable<PredictionData['guidance']>;
  scope?: string;
}

// Planet emoji map
const PLANET_EMOJI: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
  Uranus: '♅',
  Neptune: '♆',
  Pluto: '♇',
};

// Severity levels for context cards
type Severity = 'info' | 'caution' | 'warning';

function getSeverityClass(severity: Severity): string {
  return `context-card--${severity}`;
}

// Compact context card component for alerts
function ContextCard({
  icon,
  title,
  subtitle,
  severity = 'info',
  children,
}: {
  icon: string;
  title: string;
  subtitle?: string;
  severity?: Severity;
  children?: React.ReactNode;
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div className={`context-card ${getSeverityClass(severity)}`} layout>
      <button
        className="context-card-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className="context-icon">{icon}</span>
        <div className="context-titles">
          <span className="context-title">{title}</span>
          {subtitle && <span className="context-subtitle">{subtitle}</span>}
        </div>
        <span className={`context-chevron ${isExpanded ? 'expanded' : ''}`}>▾</span>
      </button>
      <AnimatePresence>
        {isExpanded && children && (
          <motion.div
            className="context-card-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function RetrogradeBadge({ retro }: { retro: RetrogradeInfo }) {
  return (
    <ContextCard
      icon={`${PLANET_EMOJI[retro.planet] || '⚹'}℞`}
      title={`${retro.planet} Retrograde`}
      subtitle={`in ${retro.sign}`}
      severity="caution"
    >
      <p className="context-detail">{retro.impact}</p>
      {retro.house_impact && (
        <p className="context-personal">
          <span className="personal-tag">For you:</span> {retro.house_impact}
        </p>
      )}
    </ContextCard>
  );
}

function VocMoonCard({ voc }: { voc: VoidOfCourseMoon }) {
  if (!voc.is_void) return null;

  const timeInfo = voc.hours_until_sign_change
    ? `~${voc.hours_until_sign_change}h until ${voc.next_sign}`
    : voc.next_sign
    ? `→ ${voc.next_sign}`
    : undefined;

  return (
    <ContextCard icon="☽" title="Void-of-Course Moon" subtitle={timeInfo} severity="warning">
      <p className="context-detail">
        Moon in {voc.current_sign} {voc.moon_degree ? `at ${voc.moon_degree}°` : ''}
      </p>
      <p className="context-advice">{voc.advice}</p>
    </ContextCard>
  );
}

function PowerHourCard({ hour }: { hour: PlanetaryHourInfo }) {
  const qualityMap: Record<string, Severity> = {
    excellent: 'info',
    good: 'info',
    neutral: 'info',
    challenging: 'caution',
    difficult: 'warning',
  };
  const severity = qualityMap[hour.quality.toLowerCase()] || 'info';

  return (
    <ContextCard
      icon={PLANET_EMOJI[hour.planet] || '⚹'}
      title={`${hour.planet} Hour`}
      subtitle={`${hour.start} - ${hour.end}`}
      severity={severity}
    >
      <p className="context-detail">{hour.suggestion}</p>
      <span className={`quality-pill quality-${hour.quality.toLowerCase()}`}>{hour.quality}</span>
    </ContextCard>
  );
}

// Maximum items to show before "Show More"
const MAX_VISIBLE_ITEMS = 4;

interface GuidanceListProps {
  items: string[];
  type: 'embrace' | 'avoid';
}

function GuidanceList({ items, type }: GuidanceListProps) {
  const [showAll, setShowAll] = useState(false);

  const visibleItems = showAll ? items : items.slice(0, MAX_VISIBLE_ITEMS);
  const hiddenCount = items.length - MAX_VISIBLE_ITEMS;
  const hasMore = items.length > MAX_VISIBLE_ITEMS;

  return (
    <div className="guidance-list-container">
      <ul className="guidance-list" role="list">
        {visibleItems.map((item, i) => (
          <motion.li
            key={i}
            className={`guidance-item guidance-item--${type}`}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <span className="guidance-icon">{type === 'embrace' ? '✓' : '✗'}</span>
            <span className="guidance-text">{item}</span>
          </motion.li>
        ))}
      </ul>

      <AnimatePresence>
        {hasMore && (
          <motion.button
            className="show-more-btn"
            onClick={() => setShowAll(!showAll)}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            aria-expanded={showAll}
          >
            {showAll ? 'Show Less' : `+${hiddenCount} more`}
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}

type GuidanceTab = 'embrace' | 'avoid';

export function DailyGuidance({ guidance, scope = 'daily' }: Props) {
  const { avoid, embrace, retrogrades, void_of_course_moon, current_planetary_hour } = guidance;
  const { title, period } = getScopeLabel(scope);
  const [activeTab, setActiveTab] = useState<GuidanceTab>('embrace');

  // Count alerts for badge
  const alertCount = (retrogrades?.length || 0) + (void_of_course_moon?.is_void ? 1 : 0);

  return (
    <div className="guidance-container">
      <h3 className="guidance-title">✨ {title}</h3>

      {/* Cosmic Alerts Section - Compact Cards */}
      {(alertCount > 0 || current_planetary_hour) && (
        <div className="cosmic-alerts">
          <div className="alerts-header">
            <span className="alerts-label">Cosmic Context</span>
            {alertCount > 0 && (
              <span className="alerts-badge">
                {alertCount} alert{alertCount > 1 ? 's' : ''}
              </span>
            )}
          </div>

          <div className="context-cards-grid">
            {/* Power Hour first - most actionable */}
            {current_planetary_hour && <PowerHourCard hour={current_planetary_hour} />}

            {/* VOC Moon - time-sensitive */}
            {void_of_course_moon?.is_void && <VocMoonCard voc={void_of_course_moon} />}

            {/* Retrogrades */}
            {retrogrades?.map((r, i) => (
              <RetrogradeBadge key={i} retro={r} />
            ))}
          </div>
        </div>
      )}

      {/* Guidance Tabs - Embrace / Avoid */}
      <div className="guidance-tabs-container">
        <div className="guidance-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === 'embrace'}
            className={`guidance-tab guidance-tab--embrace ${
              activeTab === 'embrace' ? 'active' : ''
            }`}
            onClick={() => setActiveTab('embrace')}
          >
            <span className="tab-icon">✅</span>
            <span className="tab-label">Embrace</span>
            <span className="tab-count">{embrace.activities.length}</span>
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'avoid'}
            className={`guidance-tab guidance-tab--avoid ${activeTab === 'avoid' ? 'active' : ''}`}
            onClick={() => setActiveTab('avoid')}
          >
            <span className="tab-icon">🚫</span>
            <span className="tab-label">Avoid</span>
            <span className="tab-count">{avoid.activities.length}</span>
          </button>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            className="guidance-tab-content"
            role="tabpanel"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
          >
            {activeTab === 'embrace' ? (
              <div className="guidance-panel embrace-panel">
                {embrace.time && scope === 'daily' && (
                  <div className="power-hour-highlight">
                    <span className="power-icon">⚡</span>
                    <span className="power-label">Power Hour</span>
                    <span className="power-time">{embrace.time}</span>
                  </div>
                )}

                <GuidanceList items={embrace.activities} type="embrace" />

                {embrace.colors.length > 0 && (
                  <div className="color-palette">
                    <span className="palette-label">Power Colors</span>
                    <div className="swatches">
                      {embrace.colors.map((c, i) => {
                        const { hex, name } = getColorData(c);
                        return (
                          <div key={i} className="color-chip" title={name}>
                            <span className="chip-swatch" style={{ backgroundColor: hex }} />
                            <span className="chip-name">{name}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="guidance-panel avoid-panel">
                <GuidanceList items={avoid.activities} type="avoid" />

                {avoid.colors.length > 0 && (
                  <div className="color-palette color-palette--avoid">
                    <span className="palette-label">Avoid Colors</span>
                    <div className="swatches">
                      {avoid.colors.map((c, i) => {
                        const { hex, name } = getColorData(c);
                        return (
                          <div key={i} className="color-chip color-chip--avoid" title={name}>
                            <span className="chip-swatch" style={{ backgroundColor: hex }} />
                            <span className="chip-name">{name}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {avoid.numbers.length > 0 && (
                  <div className="challenge-numbers">
                    <span className="palette-label">Challenge Numbers</span>
                    <div className="numbers-row">
                      {avoid.numbers.map((n, i) => (
                        <span key={i} className="number-badge number-badge--warning">
                          {n}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
