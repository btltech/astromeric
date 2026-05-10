import React, { useMemo, useState } from 'react';
import type { PredictionData } from '../types';
import { SectionGrid } from './SectionGrid';
import { DailyGuidance } from './DailyGuidance';
import { ApiError, fetchAiExplanation, chatWithCosmicGuide } from '../api/client';
import { useStore } from '../store/useStore';
import { useProfiles } from '../hooks';
import { toast } from './Toast';
import { CosmicCard } from './CosmicCard';
import { MarkdownText } from './MarkdownText';
import { CollapsibleSection } from './CollapsibleSection';

interface Props {
  data: PredictionData;
  onReset: () => void;
}

// Zodiac crystals by sun sign
const ZODIAC_STONES: Record<string, { stones: string[]; meaning: string }> = {
  Aries: { stones: ['Carnelian', 'Red Jasper', 'Diamond'], meaning: 'Courage & vitality' },
  Taurus: { stones: ['Rose Quartz', 'Emerald', 'Lapis Lazuli'], meaning: 'Love & abundance' },
  Gemini: { stones: ['Citrine', "Tiger's Eye", 'Agate'], meaning: 'Communication & clarity' },
  Cancer: { stones: ['Moonstone', 'Pearl', 'Ruby'], meaning: 'Intuition & protection' },
  Leo: { stones: ['Sunstone', 'Peridot', 'Amber'], meaning: 'Confidence & creativity' },
  Virgo: { stones: ['Amazonite', 'Moss Agate', 'Sapphire'], meaning: 'Healing & precision' },
  Libra: { stones: ['Opal', 'Rose Quartz', 'Tourmaline'], meaning: 'Balance & harmony' },
  Scorpio: { stones: ['Obsidian', 'Malachite', 'Topaz'], meaning: 'Transformation & power' },
  Sagittarius: { stones: ['Turquoise', 'Amethyst', 'Tanzanite'], meaning: 'Wisdom & adventure' },
  Capricorn: { stones: ['Garnet', 'Onyx', 'Black Tourmaline'], meaning: 'Discipline & success' },
  Aquarius: { stones: ['Aquamarine', 'Labradorite', 'Amethyst'], meaning: 'Innovation & insight' },
  Pisces: { stones: ['Amethyst', 'Aquamarine', 'Fluorite'], meaning: 'Dreams & intuition' },
};

// Traditional birthstones by month
const BIRTHSTONES: Record<number, { stone: string; color: string }> = {
  1: { stone: 'Garnet', color: '#8B0000' },
  2: { stone: 'Amethyst', color: '#9966CC' },
  3: { stone: 'Aquamarine', color: '#7FFFD4' },
  4: { stone: 'Diamond', color: '#B9F2FF' },
  5: { stone: 'Emerald', color: '#50C878' },
  6: { stone: 'Pearl', color: '#FDEEF4' },
  7: { stone: 'Ruby', color: '#E0115F' },
  8: { stone: 'Peridot', color: '#E6E200' },
  9: { stone: 'Sapphire', color: '#0F52BA' },
  10: { stone: 'Opal', color: '#A8C3BC' },
  11: { stone: 'Topaz', color: '#FFC87C' },
  12: { stone: 'Tanzanite', color: '#4D5BA8' },
};

// RatingBar reserved for future use
// const RatingBar = ({ value, label }: { value: number; label: string }) => (
//   <div className="rating-row">
//     <span>{label}</span>
//     <div className="stars">
//       {[...Array(5)].map((_, i) => (
//         <span key={i} className={i < value ? 'filled' : ''}>★</span>
//       ))}
//     </div>
//   </div>
// );

export function FortuneResult({ data, onReset }: Props) {
  // Get user and token from store for paid check
  const { user, token } = useStore();
  const { selectedProfile } = useProfiles();
  const isPaid = true; // All features are free now

  const scopeLabel =
    typeof data.scope === 'string' && data.scope.length > 0
      ? data.scope.charAt(0).toUpperCase() + data.scope.slice(1)
      : 'Daily';

  // Derive sign from charts if not explicitly provided
  const sunSign = data.sign || data.charts?.natal?.planets?.find((p) => p.name === 'Sun')?.sign;

  // Get birth month for birthstone
  const birthMonth = selectedProfile?.date_of_birth
    ? new Date(selectedProfile.date_of_birth).getMonth() + 1
    : null;

  // Get zodiac stones data
  const zodiacStones = sunSign ? ZODIAC_STONES[sunSign] : null;
  const birthstone = birthMonth ? BIRTHSTONES[birthMonth] : null;

  // Use theme as headline if summary is missing
  const headline = data.summary?.headline || data.theme;
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [aiInsightProvider, setAiInsightProvider] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [showUpgradeMessage, setShowUpgradeMessage] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);

  // Cosmic Guide Chat State
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const keyTakeaways = useMemo(() => {
    const factors = data.summary?.top_factors ?? [];
    return factors.slice(0, 3);
  }, [data.summary?.top_factors]);

  const summaryChips = useMemo(() => {
    const chips: string[] = [];

    if (sunSign) chips.push(`${sunSign} sun`);
    if (typeof data.life_path_number === 'number') chips.push(`Life Path ${data.life_path_number}`);
    if (data.lucky_numbers?.length) chips.push(`Lucky ${data.lucky_numbers.slice(0, 2).join(' · ')}`);

    return chips.slice(0, 3);
  }, [data.life_path_number, data.lucky_numbers, sunSign]);

  const actionSignals = useMemo(() => {
    const sectionHighlights = data.sections.flatMap((section) => section.highlights ?? []);
    const bestMoveFromHighlights = sectionHighlights.find((item) => item.startsWith('✨ Embrace:'));
    const watchForFromHighlights = sectionHighlights.find((item) => item.startsWith('⚠️ Avoid:'));

    return {
      bestMove:
        data.guidance?.embrace.activities[0] ??
        bestMoveFromHighlights?.replace(/^✨ Embrace:\s*/, '') ??
        keyTakeaways[0]?.description ??
        headline ??
        'Use the strongest opening in this reading first.',
      watchFor:
        data.guidance?.avoid.activities[0] ??
        watchForFromHighlights?.replace(/^⚠️ Avoid:\s*/, '') ??
        keyTakeaways[1]?.description ??
        'Watch where the reading repeats caution or friction.',
    };
  }, [data.guidance, data.sections, headline, keyTakeaways]);

  const readingDrivers = useMemo(() => {
    const rows = keyTakeaways.map((factor) => ({
      title: [factor.aspect, factor.impact].filter(Boolean).join(' · ') || 'Forecast driver',
      detail: factor.description ?? headline ?? 'The reading engine elevated this theme as one of the main drivers.',
    }));

    if (rows.length < 3) {
      for (const section of data.sections) {
        if (rows.length >= 3) break;

        const topTopic = Object.entries(section.topic_scores ?? {}).sort((left, right) => right[1] - left[1])[0];
        rows.push({
          title: topTopic ? `${section.title} · ${topTopic[0].replace(/_/g, ' ')}` : section.title,
          detail:
            section.highlights[0] ??
            section.affirmation ??
            'This section is one of the active layers shaping the forecast.',
        });
      }
    }

    return rows.slice(0, 3);
  }, [data.sections, headline, keyTakeaways]);

  const sectionPreviews = useMemo(
    () =>
      data.sections.map((section) => {
        const embrace = section.highlights
          .filter((item) => item.startsWith('✨ Embrace:'))
          .map((item) => item.replace(/^✨ Embrace:\s*/, ''))
          .slice(0, 2);
        const avoid = section.highlights
          .filter((item) => item.startsWith('⚠️ Avoid:'))
          .map((item) => item.replace(/^⚠️ Avoid:\s*/, ''))
          .slice(0, 2);
        const lead =
          section.highlights.find(
            (item) => !item.startsWith('✨ Embrace:') && !item.startsWith('⚠️ Avoid:')
          ) ?? section.affirmation;

        return {
          title: section.title,
          lead,
          embrace,
          avoid,
        };
      }),
    [data.sections]
  );

  const readingText = useMemo(() => {
    const lines: string[] = [];
    lines.push(
      `${data.scope?.toUpperCase?.() ?? 'READING'} — ${new Date(
        data.date || Date.now()
      ).toLocaleDateString()}`
    );
    if (headline) lines.push(`\nTL;DR: ${headline}`);

    if (keyTakeaways.length) {
      lines.push('\nKey takeaways:');
      for (const factor of keyTakeaways) {
        const parts = [factor.aspect, factor.impact].filter(Boolean).join(' — ');
        const detail = factor.description ? `: ${factor.description}` : '';
        lines.push(`- ${parts}${detail}`);
      }
    }

    if (data.sections?.length) {
      lines.push('\nDetails:');
      for (const section of data.sections) {
        lines.push(`\n${section.title}`);
        for (const highlight of (section.highlights ?? []).slice(0, 5)) {
          lines.push(`- ${highlight}`);
        }
      }
    }

    return lines.join('\n');
  }, [data.date, data.scope, data.sections, headline, keyTakeaways]);

  const journalPrompt = useMemo(() => {
    const base = headline || data.theme || 'your reading';
    return `Journal prompt: What is one concrete action you can take today to align with “${base}”?`;
  }, [data.theme, headline]);

  const handleCopyReading = async () => {
    try {
      await navigator.clipboard.writeText(readingText);
      toast.success('Copied reading to clipboard.');
    } catch (err) {
      console.warn('Copy failed', err);
      toast.error('Could not copy. Your browser may block clipboard access.');
    }
  };

  const handleShareReading = async () => {
    try {
      const sharePayload = {
        title: 'Astronumeric Reading',
        text: readingText,
      };
      if (navigator.share) {
        await navigator.share(sharePayload);
        return;
      }
      await handleCopyReading();
    } catch (err) {
      // User cancel is not an error worth surfacing.
      console.warn('Share failed', err);
    }
  };

  const handleCopyJournalPrompt = async () => {
    try {
      await navigator.clipboard.writeText(journalPrompt);
      toast.success('Copied journal prompt.');
    } catch (err) {
      console.warn('Copy prompt failed', err);
      toast.error('Could not copy journal prompt.');
    }
  };

  const handleDownloadPdf = async () => {
    setPdfLoading(true);
    try {
      const mod = await import('../utils/pdfExport');
      mod.downloadReadingPdf(data);
    } catch (err) {
      console.error('PDF export failed', err);
      toast.error('PDF export failed. Please try again.');
    } finally {
      setPdfLoading(false);
    }
  };

  const handleAiExplain = async () => {
    // Check if user is paid
    if (!isPaid) {
      setShowUpgradeMessage(true);
      return;
    }

    setAiLoading(true);
    try {
      const sections =
        data.sections?.map((section) => ({
          title: section.title,
          highlights: section.highlights,
        })) ?? [];
      const payload = {
        scope: data.scope,
        headline,
        theme: data.theme,
        sections,
        numerology_summary: data.numerology?.cycles?.personal_day?.meaning,
      };
      const response = await fetchAiExplanation(payload, token ?? undefined);
      setAiInsight(response.summary);
      setAiInsightProvider(response.provider);
    } finally {
      setAiLoading(false);
    }
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    if (!isPaid) {
      setShowUpgradeMessage(true);
      return;
    }

    const userMessage = chatInput.trim();
    setChatInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    try {
      const risingSign = data.charts?.natal?.houses?.find((h) => h.house === 1)?.sign;
      const moonSign = data.charts?.natal?.planets?.find((p) => p.name === 'Moon')?.sign;

      const response = await chatWithCosmicGuide(
        userMessage,
        sunSign,
        moonSign,
        risingSign,
        messages as any, // Cast for now if types mismatch slightly
        token ?? undefined
      );

      setMessages((prev) => [...prev, { role: 'assistant', content: response.response }]);
    } catch (err) {
      console.error('Chat failed', err);
      toast.error('Something went wrong. Please try again.');
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="card">
      {/* Top navigation bar for easy access */}
      <div className="reading-top-nav">
        <button
          onClick={onReset}
          className="btn-link"
          aria-label="Go back to profiles"
          type="button"
        >
          ← Back to Profiles
        </button>
      </div>

      <section className="reading-hero-card">
        <div className="reading-hero-card__eyebrow-row">
          <span className="reading-hero-card__eyebrow">{scopeLabel} reading</span>
          <span className="reading-hero-card__badge">
            {data.element === 'Fire' && '🔥 Fire-led'}
            {data.element === 'Water' && '💧 Water-led'}
            {data.element === 'Air' && '🌬️ Air-led'}
            {data.element === 'Earth' && '🌱 Earth-led'}
            {!data.element && 'Live forecast'}
          </span>
        </div>

        <h1 className="reading-hero-card__title">{headline ?? `${scopeLabel} outlook ready`}</h1>
        <p className="reading-hero-card__body">
          {data.sections[0]?.highlights[0] ??
            keyTakeaways[0]?.description ??
            'The strongest forecast signal is summarized here first so the user can act before scrolling into the deeper reading.'}
        </p>

        {summaryChips.length > 0 && (
          <div className="reading-hero-card__chips">
            {summaryChips.map((chip) => (
              <span key={chip} className="reading-hero-card__chip">
                {chip}
              </span>
            ))}
          </div>
        )}
      </section>

      <section className="reading-signal-grid" aria-label="Action signals">
        <article className="reading-signal-card reading-signal-card--positive">
          <span className="reading-signal-card__label">Best move</span>
          <strong>{actionSignals.bestMove}</strong>
          <p>Start with the strongest opening the forecast is giving you instead of reading every section equally.</p>
        </article>

        <article className="reading-signal-card reading-signal-card--warning">
          <span className="reading-signal-card__label">Watch for</span>
          <strong>{actionSignals.watchFor}</strong>
          <p>This is the friction signal to keep visible while you use the rest of the guidance.</p>
        </article>
      </section>

      {readingDrivers.length > 0 && (
        <section className="reading-drivers-card">
          <div className="reading-drivers-card__header">
            <span>Reading drivers</span>
            <strong>Why this forecast is leaning the way it is</strong>
          </div>

          <div className="reading-drivers-card__rows">
            {readingDrivers.map((driver) => (
              <div key={`${driver.title}-${driver.detail}`} className="reading-driver-row">
                <strong>{driver.title}</strong>
                <p>{driver.detail}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {(keyTakeaways.length > 0 || headline) && (
        <div className="reading-summary">
          {keyTakeaways.length > 0 && (
            <>
              <h3 className="reading-summary-title">What to focus on next</h3>
              <ul className="reading-takeaways">
                {keyTakeaways.map((factor, idx) => {
                  const label = [factor.aspect, factor.impact].filter(Boolean).join(' — ');
                  return (
                    <li key={idx}>
                      <strong>{label || 'Focus'}</strong>
                      {factor.description ? ` — ${factor.description}` : ''}
                    </li>
                  );
                })}
              </ul>
            </>
          )}

          <div className="reading-actions" role="group" aria-label="Next steps">
            <button type="button" className="thumb-btn" onClick={handleCopyReading}>
              Copy
            </button>
            <button type="button" className="thumb-btn" onClick={handleShareReading}>
              Share
            </button>
            <button type="button" className="thumb-btn" onClick={handleCopyJournalPrompt}>
              Journal prompt
            </button>
            <button
              type="button"
              className="thumb-btn"
              onClick={handleDownloadPdf}
              disabled={pdfLoading}
              aria-busy={pdfLoading}
            >
              {pdfLoading ? 'Preparing PDF…' : 'Download PDF'}
            </button>
          </div>
        </div>
      )}

      {sectionPreviews.length > 0 && (
        <section className="reading-sections-preview">
          <div className="reading-sections-preview__header">
            <span>Forecast sections</span>
            <strong>Scan the section-level guidance before opening the full detail grid</strong>
          </div>

          <div className="reading-sections-preview__grid">
            {sectionPreviews.map((section) => (
              <article key={section.title} className="reading-section-preview-card">
                <strong>{section.title}</strong>
                {section.lead && <p>{section.lead}</p>}

                {section.embrace.length > 0 && (
                  <div className="reading-section-preview-card__list">
                    <span>Embrace</span>
                    <ul>
                      {section.embrace.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {section.avoid.length > 0 && (
                  <div className="reading-section-preview-card__list reading-section-preview-card__list--warning">
                    <span>Avoid</span>
                    <ul>
                      {section.avoid.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      {aiInsight && (
        <CollapsibleSection title="Deeper Explanation" icon="🔍" defaultExpanded={true}>
          <MarkdownText text={aiInsight} />
        </CollapsibleSection>
      )}

      {data.guidance && <DailyGuidance guidance={data.guidance} scope={data.scope} />}

      {data.sections && data.sections.length > 0 && (
        <CollapsibleSection title="Full Reading Details" icon="📖" defaultExpanded={false}>
          <SectionGrid
            sections={data.sections}
            scope={data.scope}
            profileId={selectedProfile?.id || null}
          />
        </CollapsibleSection>
      )}

      {/* Crystals & Stones — moved after main content */}
      {(zodiacStones || birthstone) && (
        <CollapsibleSection title="Your Crystals & Stones" icon="💎" defaultExpanded={false}>
          <div className="stones-grid">
            {zodiacStones && (
              <div className="stone-category">
                <span className="stone-label">{sunSign} Crystals</span>
                <div className="stone-list">
                  {zodiacStones.stones.map((stone, i) => (
                    <span key={i} className="stone-tag">
                      {stone}
                    </span>
                  ))}
                </div>
                <span className="stone-meaning">{zodiacStones.meaning}</span>
              </div>
            )}
            {birthstone && (
              <div className="stone-category birthstone">
                <span className="stone-label">Birthstone</span>
                <span
                  className="stone-tag birthstone-tag"
                  style={{ '--stone-color': birthstone.color } as React.CSSProperties}
                >
                  {birthstone.stone}
                </span>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Cosmic Guide Chat UI */}
      <div className="cosmic-guide-container">
        <h3 className="cosmic-guide-title">Ask a Follow-Up Question</h3>
        <p className="cosmic-guide-subtitle">
          Your reading is already loaded. Ask anything specific about it.
        </p>

        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-placeholder">
              &quot;What does this reading mean for my career?&quot;
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {chatLoading && (
            <div className="chat-bubble assistant loading">
              <span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </div>
          )}
        </div>

        <form onSubmit={handleChatSubmit} className="chat-input-container">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="What would you like to understand?"
            className="chat-input"
            disabled={chatLoading}
          />
          <button
            type="submit"
            className="chat-send-btn"
            disabled={chatLoading || !chatInput.trim()}
          >
            {chatLoading ? '...' : 'Send'}
          </button>
        </form>
      </div>

      <CosmicCard data={data} userName={selectedProfile?.name || 'Seeker'} />

      <div className="action-buttons">
        <button
          onClick={handleAiExplain}
          className={`btn-secondary btn-wide ${!isPaid ? 'locked' : ''}`}
          disabled={aiLoading}
          aria-label="Explain this reading"
          aria-busy={aiLoading}
          type="button"
        >
          {aiLoading ? 'Thinking…' : 'Explain This Reading'}
        </button>
        <button
          onClick={onReset}
          className="btn-secondary"
          aria-label="Go back to profiles"
          type="button"
        >
          Back to Profiles
        </button>
      </div>
    </div>
  );
}
