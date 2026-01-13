import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3 },
};

// Learning content data
const LESSONS = {
  astrology: [
    {
      id: 'intro-astrology',
      title: 'What is Astrology?',
      icon: '🌟',
      duration: '3 min',
      content: `Astrology is the study of how celestial bodies—the Sun, Moon, planets, and stars—influence life on Earth. Your birth chart (or natal chart) is a snapshot of the sky at the exact moment you were born.

**Key Concepts:**
- **Birth Chart**: A map of where all the planets were when you were born
- **Zodiac Signs**: 12 constellations the Sun travels through each year
- **Houses**: 12 life areas (career, relationships, home, etc.)
- **Aspects**: Angles between planets that create harmony or tension

Think of your birth chart as your cosmic DNA—it doesn't control you, but it reveals your natural tendencies, strengths, and growth areas.`,
    },
    {
      id: 'sun-moon-rising',
      title: 'Your Big Three: Sun, Moon & Rising',
      icon: '☀️',
      duration: '5 min',
      content: `The "Big Three" are the most important placements in your chart. Together, they paint a picture of who you are.

**☀️ Sun Sign** — Your Core Identity
This is what most people know as their "zodiac sign." It represents your ego, life purpose, and the qualities you're developing throughout life.
*Example: A Leo Sun is learning to shine, lead, and express creativity.*

**🌙 Moon Sign** — Your Emotional Nature
Your Moon sign reveals how you process emotions, what makes you feel secure, and your instinctive reactions. It's your private self.
*Example: A Scorpio Moon feels deeply, needs emotional intimacy, and may hide their vulnerability.*

**⬆️ Rising Sign (Ascendant)** — Your Outer Mask
This is the sign that was rising on the eastern horizon when you were born. It's your first impression, your appearance, and how you approach new situations.
*Example: A Libra Rising comes across as charming, diplomatic, and aesthetically aware.*

**Why They Matter:**
Someone with a Cancer Sun, Aries Moon, and Capricorn Rising might appear reserved and ambitious (Capricorn Rising), feel things impulsively and need independence (Aries Moon), but ultimately seek nurturing and emotional security (Cancer Sun).`,
    },
    {
      id: 'planets',
      title: 'The Planets & What They Rule',
      icon: '🪐',
      duration: '6 min',
      content: `Each planet in your chart governs different aspects of your personality and life.

**Personal Planets** (move quickly, affect daily life):
- **☿ Mercury** — Communication, thinking, learning style
- **♀ Venus** — Love, beauty, values, how you attract
- **♂ Mars** — Action, drive, anger, sexuality

**Social Planets** (generational themes):
- **♃ Jupiter** — Luck, expansion, beliefs, where you grow
- **♄ Saturn** — Discipline, limitations, lessons, maturity

**Outer Planets** (collective/spiritual):
- **♅ Uranus** — Revolution, innovation, sudden change
- **♆ Neptune** — Dreams, intuition, illusion, spirituality
- **♇ Pluto** — Transformation, power, death/rebirth cycles

**Example Reading:**
If your Venus is in Virgo, you show love through acts of service, appreciate practical gifts, and may be critical of partners (but also devoted). If your Mars is in Sagittarius, you take action boldly, need freedom, and fight for beliefs.`,
    },
    {
      id: 'houses',
      title: 'The 12 Houses of Life',
      icon: '🏠',
      duration: '5 min',
      content: `The houses represent different life areas. Planets in a house focus their energy there.

**Angular Houses** (action & identity):
- **1st House** — Self, appearance, first impressions
- **4th House** — Home, family, roots, private life
- **7th House** — Partnerships, marriage, open enemies
- **10th House** — Career, reputation, public image

**Succedent Houses** (resources & values):
- **2nd House** — Money, possessions, self-worth
- **5th House** — Creativity, romance, children, fun
- **8th House** — Shared resources, intimacy, transformation
- **11th House** — Friends, groups, hopes, social causes

**Cadent Houses** (learning & adaptation):
- **3rd House** — Communication, siblings, local travel
- **6th House** — Health, daily work, service, routines
- **9th House** — Higher education, travel, philosophy
- **12th House** — Subconscious, secrets, spirituality, isolation

**Example:**
Sun in the 10th House = Your identity is tied to career and public achievement. You need recognition for your work.`,
    },
    {
      id: 'aspects',
      title: 'Understanding Aspects',
      icon: '📐',
      duration: '4 min',
      content: `Aspects are angles between planets. They show how different parts of your personality interact.

**Harmonious Aspects** (easy flow):
- **Conjunction (0°)** — Planets merge energy, intensifying both
- **Trine (120°)** — Natural talent, easy flow, gifts
- **Sextile (60°)** — Opportunities, requires some effort

**Challenging Aspects** (growth through tension):
- **Square (90°)** — Internal conflict, friction, motivation to change
- **Opposition (180°)** — Push-pull tension, need for balance

**Example:**
Moon square Mars = Your emotions (Moon) clash with your actions (Mars). You might react impulsively when upset, but this tension pushes you to develop emotional intelligence.

Venus trine Jupiter = Love and luck flow together naturally. You attract good fortune in relationships and may be generous.

**Remember:** "Hard" aspects aren't bad—they create the friction that drives growth. "Easy" aspects can lead to complacency if not consciously used.`,
    },
    {
      id: 'retrogrades',
      title: 'What Retrogrades Really Mean',
      icon: '⟲',
      duration: '4 min',
      content: `When a planet is "retrograde," it appears to move backward from Earth's perspective. It's an optical illusion, but astrologically significant.

**What Happens During Retrogrades:**
The planet's themes turn inward. It's a time for review, revision, and reflection—not starting new things in that area.

**Common Retrogrades:**

**Mercury Retrograde** (3x/year, ~3 weeks each)
- Miscommunications, tech glitches, travel delays
- Good for: Revisiting old projects, reconnecting with people, editing
- Tip: Back up data, read contracts carefully, expect the unexpected

**Venus Retrograde** (~every 18 months)
- Relationship reviews, ex-partners reappearing, beauty mishaps
- Good for: Reassessing values, inner beauty work
- Tip: Avoid cosmetic procedures, new relationships

**Mars Retrograde** (~every 2 years)
- Low energy, frustration, anger surfacing
- Good for: Reviewing goals, processing anger
- Tip: Avoid starting new projects, manage anger consciously

**Retrograde in Your Birth Chart:**
If you were born with a planet retrograde, that planet's energy expresses more internally. A natal Mercury retrograde person may be a deep thinker who processes before speaking.`,
    },
  ],
  numerology: [
    {
      id: 'intro-numerology',
      title: 'What is Numerology?',
      icon: '🔢',
      duration: '3 min',
      content: `Numerology is the study of numbers and their symbolic meanings. Each number from 1-9 (plus master numbers 11, 22, 33) carries a unique vibration and meaning.

**Core Belief:**
Numbers aren't just quantities—they're qualitative energies. Your birth date and name convert to numbers that reveal your life's blueprint.

**Key Numbers in Your Profile:**
- **Life Path** — Your life purpose (from birth date)
- **Expression** — Your talents (from full name)
- **Soul Urge** — Your inner desires (from vowels)
- **Personality** — How others see you (from consonants)
- **Personal Year/Month/Day** — Current cycles

Unlike astrology (which uses planetary positions), numerology uses mathematical reduction. Any number reduces to 1-9 by adding digits together.

*Example: 1990 → 1+9+9+0 = 19 → 1+9 = 10 → 1+0 = 1*`,
    },
    {
      id: 'life-path',
      title: 'Your Life Path Number',
      icon: '🛤️',
      duration: '6 min',
      content: `Your Life Path is the most important number in numerology. It reveals your life purpose and the lessons you're here to learn.

**How to Calculate:**
Add all digits of your birth date, then reduce to a single digit (or master number).

*Example: March 15, 1990*
*Month: 3*
*Day: 1+5 = 6*
*Year: 1+9+9+0 = 19 → 1+9 = 10 → 1+0 = 1*
*Total: 3+6+1 = 10 → 1+0 = **1***

**The Life Paths:**
**1** — The Leader: Independence, innovation, pioneering
**2** — The Diplomat: Partnership, sensitivity, cooperation
**3** — The Communicator: Creativity, expression, joy
**4** — The Builder: Stability, hard work, foundations
**5** — The Freedom Seeker: Change, adventure, versatility
**6** — The Nurturer: Responsibility, love, domestic harmony
**7** — The Seeker: Spirituality, analysis, inner wisdom
**8** — The Powerhouse: Abundance, authority, achievement
**9** — The Humanitarian: Compassion, completion, service

**Master Numbers** (don't reduce):
**11** — The Intuitive: Spiritual messenger, high nervous energy
**22** — The Master Builder: Dreams into reality, practical visionary
**33** — The Master Teacher: Healing through love, selfless service`,
    },
    {
      id: 'personal-cycles',
      title: 'Personal Year, Month & Day',
      icon: '📅',
      duration: '5 min',
      content: `Beyond your fixed numbers, numerology tracks your current cycles. These help you understand the energy available to you now.

**Personal Year** (January to December)
Add your birth month + birth day + current year, reduce to single digit.

*Example: Born March 15, in year 2024*
*3 + 15 + 2024 = 3 + 6 + 8 = 17 → 1+7 = **8***

**The 9-Year Cycle:**
- **Year 1** — New beginnings, plant seeds, take initiative
- **Year 2** — Patience, partnerships, wait and cooperate
- **Year 3** — Creativity, self-expression, social expansion
- **Year 4** — Hard work, building foundations, discipline
- **Year 5** — Change, freedom, unexpected opportunities
- **Year 6** — Responsibility, home, relationships, service
- **Year 7** — Reflection, rest, spiritual growth, solitude
- **Year 8** — Harvest, power, financial focus, karma
- **Year 9** — Completion, release, endings, preparation

**Personal Month:** Add Personal Year + calendar month number
**Personal Day:** Add Personal Month + calendar day

**Practical Use:**
In a Personal Year 1, start new projects. In Year 9, let go and complete old business. Don't fight the current—work with it.`,
    },
    {
      id: 'expression-soul',
      title: 'Expression & Soul Urge Numbers',
      icon: '✨',
      duration: '5 min',
      content: `While Life Path comes from your birth date, Expression and Soul Urge come from your **name**.

**Letter-to-Number Conversion:**
A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9
J=1, K=2, L=3, M=4, N=5, O=6, P=7, Q=8, R=9
S=1, T=2, U=3, V=4, W=5, X=6, Y=7, Z=8

**Expression Number** (Destiny Number)
Uses ALL letters in your full birth name. Reveals your talents, abilities, and what you're meant to express in this life.

*Example: JOHN DOE*
*J(1)+O(6)+H(8)+N(5) = 20 → 2*
*D(4)+O(6)+E(5) = 15 → 6*
*Total: 2+6 = **8***

**Soul Urge Number** (Heart's Desire)
Uses only VOWELS (A, E, I, O, U). Reveals your inner motivations, what your soul truly craves.

*Example: JOHN DOE → O, O, E*
*O(6)+O(6)+E(5) = 17 → 1+7 = **8***

**Personality Number**
Uses only CONSONANTS. Shows how others perceive you—your outer personality.

**Tip:** If your Life Path and Expression differ greatly, you may feel pulled between who you are and what you're meant to do. Understanding both helps integration.`,
    },
    {
      id: 'master-numbers',
      title: 'Master Numbers: 11, 22, 33',
      icon: '🌟',
      duration: '4 min',
      content: `Master Numbers carry intensified energy and greater potential—but also greater challenges.

**11 — The Intuitive Messenger**
The 11 is a 2 at its core (1+1=2) but amplified. Highly intuitive, spiritually aware, and often psychic. The challenge is nervous tension and self-doubt.
- **Gifts:** Inspiration, spiritual insight, channel for higher wisdom
- **Challenges:** Anxiety, impracticality, feeling "different"
- **Lesson:** Trust your intuition while staying grounded

**22 — The Master Builder**
The 22 is a 4 amplified—practical visionary who can manifest dreams into reality on a large scale.
- **Gifts:** Turning big ideas into tangible results, leadership
- **Challenges:** Overwhelm, setting the bar too high
- **Lesson:** Build step by step; the foundation matters

**33 — The Master Teacher**
The 33 is a 6 amplified—the healer, nurturer, and spiritual teacher. Often found in those who dedicate their lives to service.
- **Gifts:** Healing presence, unconditional love, inspiring others
- **Challenges:** Martyrdom, over-giving, neglecting self
- **Lesson:** You can't pour from an empty cup

**Living a Master Number:**
Not everyone with a master number in their chart lives at that vibration constantly. Many oscillate between the master and its base number (11/2, 22/4, 33/6). That's normal—master numbers are aspirational energies.`,
    },
    {
      id: 'daily-use',
      title: 'Using Numerology Daily',
      icon: '🌅',
      duration: '4 min',
      content: `Here's how to apply numerology to everyday decisions:

**Check Your Personal Day**
Each day has a specific energy. Align your activities:
- **1 Day:** Start new things, take initiative
- **2 Day:** Collaborate, be patient, handle details
- **3 Day:** Be creative, socialize, communicate
- **4 Day:** Organize, work hard, build structure
- **5 Day:** Embrace change, try something new
- **6 Day:** Focus on home, family, relationships
- **7 Day:** Rest, reflect, study, meditate
- **8 Day:** Handle finances, assert authority
- **9 Day:** Complete projects, release, give

**Lucky Numbers**
Your Life Path and Personal Year numbers are generally favorable for you. Consider them for:
- Scheduling important meetings (on matching days)
- Choosing addresses or phone numbers
- Timing big decisions

**Combine with Astrology**
Your Personal Day energy + current Moon sign + planetary transits = a fuller picture of the day's energy.

**Warning:**
Don't become a "number slave." Numerology is a tool for awareness, not a rigid rulebook. Use it to understand energy, not to avoid living.`,
    },
  ],
};

type Category = 'astrology' | 'numerology';

interface Lesson {
  id: string;
  title: string;
  icon: string;
  duration: string;
  content: string;
}

function formatContent(text: string): React.ReactNode[] {
  return text.split('\n\n').map((paragraph, i) => {
    const html = paragraph
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
    return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />;
  });
}

function LessonCard({
  lesson,
  isExpanded,
  onToggle,
}: {
  lesson: Lesson;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  return (
    <motion.div
      className={`lesson-card ${isExpanded ? 'expanded' : ''}`}
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <button className="lesson-header" onClick={onToggle} aria-expanded={isExpanded}>
        <span className="lesson-icon">{lesson.icon}</span>
        <div className="lesson-info">
          <h4>{lesson.title}</h4>
          <span className="lesson-duration">⏱ {lesson.duration}</span>
        </div>
        <span className="lesson-toggle">{isExpanded ? '−' : '+'}</span>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="lesson-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="lesson-body">{formatContent(lesson.content)}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function LearnView() {
  const [activeCategory, setActiveCategory] = useState<Category>('astrology');
  const [expandedLesson, setExpandedLesson] = useState<string | null>(null);
  const [completedLessons, setCompletedLessons] = useState<Set<string>>(() => {
    const saved =
      localStorage.getItem('astromeric_completedLessons') ||
      localStorage.getItem('astronumeric_completedLessons');
    return saved ? new Set(JSON.parse(saved)) : new Set();
  });

  const lessons = LESSONS[activeCategory];
  const completedCount = lessons.filter((l) => completedLessons.has(l.id)).length;
  const progress = Math.round((completedCount / lessons.length) * 100);
  const nextLesson = lessons.find((l) => !completedLessons.has(l.id)) || null;

  const toggleLesson = (id: string) => {
    if (expandedLesson === id) {
      setExpandedLesson(null);
    } else {
      setExpandedLesson(id);
      // Mark as completed when opened
      const newCompleted = new Set(completedLessons);
      newCompleted.add(id);
      setCompletedLessons(newCompleted);
      localStorage.setItem('astronumeric_completedLessons', JSON.stringify([...newCompleted]));
    }
  };

  const totalLessons = LESSONS.astrology.length + LESSONS.numerology.length;
  const totalCompleted = [...completedLessons].filter(
    (id) =>
      LESSONS.astrology.some((l) => l.id === id) || LESSONS.numerology.some((l) => l.id === id)
  ).length;

  return (
    <motion.div className="card learn-page" {...fadeIn}>
      <h2>📚 Learn Astrology & Numerology</h2>
      <p className="learn-intro">
        Master the cosmic arts with our step-by-step lessons. Tap any topic to expand and learn.
      </p>

      {/* Category Tabs */}
      <div className="learn-tabs">
        <button
          className={`learn-tab ${activeCategory === 'astrology' ? 'active' : ''}`}
          onClick={() => {
            setActiveCategory('astrology');
            setExpandedLesson(null);
          }}
        >
          🌟 Astrology
        </button>
        <button
          className={`learn-tab ${activeCategory === 'numerology' ? 'active' : ''}`}
          onClick={() => {
            setActiveCategory('numerology');
            setExpandedLesson(null);
          }}
        >
          🔢 Numerology
        </button>
      </div>

      {/* Overall Progress */}
      <div className="learn-progress overall">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(totalCompleted / totalLessons) * 100}%` }}
          />
        </div>
        <span className="progress-text">
          {totalCompleted}/{totalLessons} lessons completed
        </span>
      </div>

      {/* Category Progress */}
      <div className="learn-progress category">
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <span className="progress-text">
          {activeCategory === 'astrology' ? '🌟' : '🔢'} {completedCount}/{lessons.length} in{' '}
          {activeCategory}
        </span>
      </div>

      <div className="next-lesson" style={{ marginBottom: '1rem' }}>
        {nextLesson ? (
          <p className="text-muted" style={{ margin: 0 }}>
            Next up:{' '}
            <strong>
              {nextLesson.icon} {nextLesson.title}
            </strong>{' '}
            — tap to continue your path.
          </p>
        ) : (
          <p className="text-muted" style={{ margin: 0 }}>
            You have completed this track. Switch categories or revisit any lesson for a refresher.
          </p>
        )}
      </div>

      {/* Lessons */}
      <div className="lessons-list">
        {lessons.map((lesson) => (
          <LessonCard
            key={lesson.id}
            lesson={lesson}
            isExpanded={expandedLesson === lesson.id}
            onToggle={() => toggleLesson(lesson.id)}
          />
        ))}
      </div>

      {/* Completion Message */}
      {totalCompleted === totalLessons && (
        <motion.div
          className="completion-message"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          🎉 Congratulations! You've completed all lessons! You're now a cosmic scholar.
        </motion.div>
      )}
    </motion.div>
  );
}
