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
      return { title: "This Week's Guidance", period: 'This Week', periodLong: 'this week' };
    case 'monthly':
      return { title: "This Month's Guidance", period: 'This Month', periodLong: 'this month' };
    default:
      return { title: "Today's Guidance", period: 'Today', periodLong: 'today' };
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
      subtitle="Tap to see what to watch for"
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
    <ContextCard icon="☽" title="Moon Energy Is Low" subtitle={timeInfo} severity="warning">
      <p className="context-detail">
        Not a good time to start new things or make big decisions.
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

  const windowSubtitle =
    hour.quality.toLowerCase() === 'challenging' || hour.quality.toLowerCase() === 'difficult'
      ? 'Demanding window — take it steady'
      : 'Good time to do focused work';

  return (
    <ContextCard
      icon={PLANET_EMOJI[hour.planet] || '⚹'}
      title={`Focus window: ${hour.start}–${hour.end}`}
      subtitle={windowSubtitle}
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

export function DailyGuidance({ guidance, scope = 'daily' }: Props) {
  const { avoid, embrace, retrogrades, void_of_course_moon, current_planetary_hour } = guidance;
  const { title } = getScopeLabel(scope);
  const [whyOpen, setWhyOpen] = useState(false);

  const alertCount = (retrogrades?.length || 0) + (void_of_course_moon?.is_void ? 1 : 0);
  const hasInfluences = alertCount > 0 || !!current_planetary_hour;

  return (
    <div className="guidance-container">
      <h3 className="guidance-title">{title}</h3>

      {/* WHAT TO DO */}
      <div className="guidance-section guidance-section--do">
        <div className="guidance-section-header">
          <span className="guidance-section-icon">✅</span>
          <span className="guidance-section-label">What to do</span>
        </div>

        {embrace.time && scope === 'daily' && (
          <div className="power-hour-highlight">
            <span className="power-icon">⚡</span>
            <span className="power-label">Peak Time</span>
            <span className="power-time">{embrace.time}</span>
          </div>
        )}

        <GuidanceList items={embrace.activities} type="embrace" />

        {embrace.colors.length > 0 && (
          <div className="color-palette">
            <span className="palette-label">
              {scope === 'weekly' ? 'Best Colors This Week' : scope === 'monthly' ? 'Best Colors This Month' : 'Best Colors Today'}
            </span>
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

      {/* WHAT TO AVOID */}
      <div className="guidance-section guidance-section--avoid">
        <div className="guidance-section-header">
          <span className="guidance-section-icon">🚫</span>
          <span className="guidance-section-label">What to avoid</span>
        </div>

        <GuidanceList items={avoid.activities} type="avoid" />

        {avoid.colors.length > 0 && (
          <div className="color-palette color-palette--avoid">
            <span className="palette-label">Colors to skip</span>
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
            <span className="palette-label">Numbers to avoid</span>
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

      {/* WHY THESE RECOMMENDATIONS — collapsible */}
      {hasInfluences && (
        <div className="guidance-why">
          <button
            className="guidance-why-toggle"
            onClick={() => setWhyOpen((v) => !v)}
            aria-expanded={whyOpen}
          >
            <span>Why these recommendations?</span>
            <span className={`guidance-why-chevron ${whyOpen ? 'open' : ''}`}>▾</span>
          </button>
          <AnimatePresence>
            {whyOpen && (
              <motion.div
                className="context-cards-grid"
                key="why-panel"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                style={{ overflow: 'hidden' }}
              >
                {current_planetary_hour && <PowerHourCard hour={current_planetary_hour} />}
                {void_of_course_moon?.is_void && <VocMoonCard voc={void_of_course_moon} />}
                {retrogrades?.map((r, i) => (
                  <RetrogradeBadge key={i} retro={r} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
