import React, { useMemo, useState } from 'react';
import type { PredictionData } from '../types';
import { SectionGrid } from './SectionGrid';
import { DailyGuidance } from './DailyGuidance';
import { ApiError, fetchAiExplanation, chatWithCosmicGuide } from '../api/client';
import { useStore } from '../store/useStore';
import { useProfiles } from '../hooks';
import { toast } from './Toast';
import { CosmicCard } from './CosmicCard';

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
  const isPaid = !!user?.is_paid;

  // Derive sign from charts if not explicitly provided
  const sunSign = data.sign || data.charts?.natal?.planets?.find((p) => p.name === 'Sun')?.sign;

  // Get birth month for birthstone
  const birthMonth = data.numerology?.birth_date
    ? new Date(data.numerology.birth_date).getMonth() + 1
    : null;

  // Get zodiac stones data
  const zodiacStones = sunSign ? ZODIAC_STONES[sunSign] : null;
  const birthstone = birthMonth ? BIRTHSTONES[birthMonth] : null;

  // Use theme as headline if summary is missing
  const headline = data.summary?.headline || data.theme;
  const [aiInsight, setAiInsight] = useState<string | null>(null);
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
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        setAiInsight('Please sign in with a paid account to use AI insights.');
      } else {
        console.error('AI assist failed', err);
        setAiInsight('AI assist encountered a hiccup. Please try again soon.');
      }
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
      const risingSign = data.charts?.natal?.houses?.find((h: any) => h.house === 1)?.sign;
      const moonSign = data.charts?.natal?.planets?.find((p: any) => p.name === 'Moon')?.sign;

      const response = await chatWithCosmicGuide(
        {
          message: userMessage,
          sun_sign: sunSign,
          moon_sign: moonSign,
          rising_sign: risingSign,
          history: messages,
        },
        token ?? undefined
      );

      setMessages((prev) => [...prev, { role: 'assistant', content: response.response }]);
    } catch (err) {
      console.error('Chat failed', err);
      toast.error('The Cosmic Guide is currently meditating. Please try again.');
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

      <div className="header-badge">
        {data.element === 'Fire' && '🔥'}
        {data.element === 'Water' && '💧'}
        {data.element === 'Air' && '🌬️'}
        {data.element === 'Earth' && '🌱'}
      </div>
      <h1 className="text-center mb-1">
        {data.scope.charAt(0).toUpperCase() + data.scope.slice(1)} Reading
      </h1>
      {sunSign && data.numerology?.core_numbers?.life_path && (
        <h3 className="reading-subtitle">
          {sunSign} • Life Path {data.numerology.core_numbers.life_path.number}
        </h3>
      )}

      {/* Cosmic Stones Section */}
      {(zodiacStones || birthstone) && (
        <div className="cosmic-stones-section">
          <h4 className="cosmic-stones-title">💎 Your Cosmic Stones</h4>
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
        </div>
      )}

      {headline && (
        <div className="tldr-box">
          <strong>TL;DR:</strong> {headline}
        </div>
      )}

      {(keyTakeaways.length > 0 || headline) && (
        <div className="reading-summary">
          {keyTakeaways.length > 0 && (
            <>
              <h3 className="reading-summary-title">Key takeaways</h3>
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

      {aiInsight && <div className="tldr-box ai-insight">{aiInsight}</div>}
      {showUpgradeMessage && (
        <div className="tldr-box upgrade-message">
          ✨ <strong>Premium Feature</strong> — AI insights are available for premium members.
          Upgrade to unlock personalized cosmic explanations, longer guidance, and saved insight
          history.
        </div>
      )}
      {!isPaid && (
        <div className="upgrade-ribbon" role="note">
          <p className="eyebrow">Premium locked</p>
          <p style={{ margin: 0 }}>
            Unlock AI explanations, richer affirmations, and cloud backup for your readings.
          </p>
        </div>
      )}

      {data.guidance && <DailyGuidance guidance={data.guidance} scope={data.scope} />}

      {data.sections && data.sections.length > 0 && (
        <SectionGrid
          sections={data.sections}
          scope={data.scope}
          profileId={selectedProfile?.id || null}
        />
      )}

      {/* Cosmic Guide Chat UI */}
      <div className="cosmic-guide-container">
        <h3 className="cosmic-guide-title">✨ Ask the Cosmic Guide</h3>
        <p className="cosmic-guide-subtitle">
          Ask follow-up questions about your reading or seek mystical advice.
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
            placeholder="Ask the stars anything..."
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
          aria-label="Explain this reading with AI"
          aria-busy={aiLoading}
          type="button"
        >
          {aiLoading ? 'Thinking…' : isPaid ? '✨ Explain with AI' : '🔒 Premium AI Insight'}
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
