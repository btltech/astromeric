import React, { useState } from 'react';
import { Helmet } from 'react-helmet';
import { motion } from 'framer-motion';

// ─── Data ────────────────────────────────────────────────────────────────────

const ZODIAC = [
  {
    sign: 'Aries',
    symbol: '♈',
    dates: 'Mar 21 – Apr 19',
    element: 'Fire',
    ruling: 'Mars',
    trait: 'Bold, direct, motivated by action. The initiator of the zodiac.',
  },
  {
    sign: 'Taurus',
    symbol: '♉',
    dates: 'Apr 20 – May 20',
    element: 'Earth',
    ruling: 'Venus',
    trait: 'Patient, sensory, drawn to beauty and stability. Understands value.',
  },
  {
    sign: 'Gemini',
    symbol: '♊',
    dates: 'May 21 – Jun 20',
    element: 'Air',
    ruling: 'Mercury',
    trait: 'Curious, adaptive, quick-minded. Connects ideas across contexts.',
  },
  {
    sign: 'Cancer',
    symbol: '♋',
    dates: 'Jun 21 – Jul 22',
    element: 'Water',
    ruling: 'Moon',
    trait: 'Intuitive, protective, emotionally perceptive. Roots run deep.',
  },
  {
    sign: 'Leo',
    symbol: '♌',
    dates: 'Jul 23 – Aug 22',
    element: 'Fire',
    ruling: 'Sun',
    trait: 'Expressive, generous, drawn to recognition and creative output.',
  },
  {
    sign: 'Virgo',
    symbol: '♍',
    dates: 'Aug 23 – Sep 22',
    element: 'Earth',
    ruling: 'Mercury',
    trait: 'Analytical, precise, service-oriented. Finds meaning in detail.',
  },
  {
    sign: 'Libra',
    symbol: '♎',
    dates: 'Sep 23 – Oct 22',
    element: 'Air',
    ruling: 'Venus',
    trait: 'Balanced, relational, attuned to fairness and aesthetic harmony.',
  },
  {
    sign: 'Scorpio',
    symbol: '♏',
    dates: 'Oct 23 – Nov 21',
    element: 'Water',
    ruling: 'Pluto',
    trait: 'Intense, perceptive, drawn toward depth, transformation, and truth.',
  },
  {
    sign: 'Sagittarius',
    symbol: '♐',
    dates: 'Nov 22 – Dec 21',
    element: 'Fire',
    ruling: 'Jupiter',
    trait: 'Expansive, philosophical, drawn to freedom and big-picture meaning.',
  },
  {
    sign: 'Capricorn',
    symbol: '♑',
    dates: 'Dec 22 – Jan 19',
    element: 'Earth',
    ruling: 'Saturn',
    trait: 'Disciplined, ambitious, motivated by structure and long-term goals.',
  },
  {
    sign: 'Aquarius',
    symbol: '♒',
    dates: 'Jan 20 – Feb 18',
    element: 'Air',
    ruling: 'Uranus',
    trait: 'Independent, idealistic, drawn to collective progress and innovation.',
  },
  {
    sign: 'Pisces',
    symbol: '♓',
    dates: 'Feb 19 – Mar 20',
    element: 'Water',
    ruling: 'Neptune',
    trait: 'Empathic, imaginative, permeable to emotion and spiritual undercurrent.',
  },
];

const PLANETS = [
  {
    name: 'Sun',
    symbol: '☉',
    governs: 'Core identity, vitality, ego, life force. Where you shine.',
  },
  {
    name: 'Moon',
    symbol: '☽',
    governs: 'Emotional nature, instincts, memory, what makes you feel safe.',
  },
  {
    name: 'Mercury',
    symbol: '☿',
    governs: 'Communication, thinking style, how you process and share ideas.',
  },
  {
    name: 'Venus',
    symbol: '♀',
    governs: 'Love, beauty, values, what you find pleasurable and meaningful.',
  },
  {
    name: 'Mars',
    symbol: '♂',
    governs: 'Drive, aggression, desire, how you pursue what you want.',
  },
  {
    name: 'Jupiter',
    symbol: '♃',
    governs: 'Expansion, growth, luck, where life tends to open up for you.',
  },
  {
    name: 'Saturn',
    symbol: '♄',
    governs: 'Discipline, limits, responsibility, long-term lessons.',
  },
  {
    name: 'Uranus',
    symbol: '⛢',
    governs: 'Disruption, originality, sudden change, breaking with convention.',
  },
  {
    name: 'Neptune',
    symbol: '♆',
    governs: 'Illusion, intuition, spirituality, the dissolving of boundaries.',
  },
  {
    name: 'Pluto',
    symbol: '♇',
    governs: 'Transformation, power, death and rebirth, the unseen forces.',
  },
];

const LIFE_PATHS: Record<number, { keyword: string; description: string }> = {
  1: {
    keyword: 'The Pioneer',
    description:
      'Independent, self-directed, driven to lead and originate. Works best when given autonomy.',
  },
  2: {
    keyword: 'The Mediator',
    description:
      'Cooperative, sensitive, attuned to others. Finds strength in collaboration and quiet influence.',
  },
  3: {
    keyword: 'The Creator',
    description:
      'Expressive, social, imaginative. Drawn to art, communication, and bringing ideas to life.',
  },
  4: {
    keyword: 'The Builder',
    description:
      'Practical, disciplined, reliable. Thrives on structure, systems, and long-term work.',
  },
  5: {
    keyword: 'The Free Spirit',
    description:
      'Adaptive, curious, drawn to variety and change. Needs freedom to explore and experience.',
  },
  6: {
    keyword: 'The Nurturer',
    description:
      'Responsible, caring, community-oriented. Finds purpose in service and harmonious relationships.',
  },
  7: {
    keyword: 'The Seeker',
    description:
      'Analytical, introspective, drawn to knowledge and truth. Needs solitude to think deeply.',
  },
  8: {
    keyword: 'The Achiever',
    description: 'Ambitious, resourceful, motivated by material mastery and recognition of effort.',
  },
  9: {
    keyword: 'The Sage',
    description:
      'Compassionate, wise, drawn to universal service. Often carries a broad, humanitarian perspective.',
  },
  11: {
    keyword: 'The Intuitive',
    description:
      'Master number. Heightened sensitivity and spiritual awareness. Potential for visionary insight.',
  },
  22: {
    keyword: 'The Architect',
    description:
      'Master number. Rare capacity to turn idealistic visions into large-scale, lasting structures.',
  },
  33: {
    keyword: 'The Teacher',
    description:
      'Master number. Deep capacity for compassion and selfless service. A rare and demanding path.',
  },
};

const ELEMENTS = [
  {
    name: 'Fire',
    emoji: '🔥',
    signs: 'Aries · Leo · Sagittarius',
    quality: 'Action, passion, initiative, enthusiasm. Oriented toward the future.',
  },
  {
    name: 'Earth',
    emoji: '🌍',
    signs: 'Taurus · Virgo · Capricorn',
    quality: 'Practicality, stability, patience. Oriented toward the tangible and lasting.',
  },
  {
    name: 'Air',
    emoji: '💨',
    signs: 'Gemini · Libra · Aquarius',
    quality: 'Intellect, communication, connection. Oriented toward ideas and exchange.',
  },
  {
    name: 'Water',
    emoji: '🌊',
    signs: 'Cancer · Scorpio · Pisces',
    quality: 'Emotion, intuition, depth. Oriented toward feeling and the unseen.',
  },
];

// ─── LP Calculator ───────────────────────────────────────────────────────────

function reduceNum(n: number, keepMaster = true): number {
  while (n > 9) {
    if (keepMaster && (n === 11 || n === 22 || n === 33)) break;
    n = String(n)
      .split('')
      .reduce((s, d) => s + parseInt(d), 0);
  }
  return n;
}

function calcLifePath(dateStr: string): number | null {
  const parts = dateStr.split('-');
  if (parts.length !== 3) return null;
  const [y, m, d] = parts.map(Number);
  if (!y || !m || !d) return null;
  const rY = reduceNum(y);
  const rM = reduceNum(m);
  const rD = reduceNum(d);
  return reduceNum(rY + rM + rD);
}

function LifePathCalc() {
  const [dob, setDob] = useState('');
  const [result, setResult] = useState<number | null>(null);

  const handleCalc = () => {
    const lp = calcLifePath(dob);
    setResult(lp);
  };

  const info = result !== null ? LIFE_PATHS[result] ?? LIFE_PATHS[reduceNum(result, false)] : null;

  return (
    <div style={{ maxWidth: '420px', margin: '0 auto', textAlign: 'center' }}>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1rem' }}>
        Enter your date of birth to calculate your Life Path number.
      </p>
      <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
        <input
          type="date"
          value={dob}
          onChange={(e) => {
            setDob(e.target.value);
            setResult(null);
          }}
          style={{
            padding: '0.65rem 1rem',
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: '8px',
            color: 'var(--text)',
            fontSize: '0.95rem',
            outline: 'none',
          }}
        />
        <button
          onClick={handleCalc}
          disabled={!dob}
          style={{
            padding: '0.65rem 1.5rem',
            background: 'var(--primary)',
            border: 'none',
            borderRadius: '8px',
            color: '#fff',
            fontWeight: 600,
            fontSize: '0.95rem',
            cursor: dob ? 'pointer' : 'not-allowed',
            opacity: dob ? 1 : 0.5,
          }}
        >
          Calculate
        </button>
      </div>

      {result !== null && info && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            marginTop: '1.5rem',
            padding: '1.5rem',
            background: 'rgba(139, 92, 246, 0.1)',
            border: '1px solid rgba(139, 92, 246, 0.25)',
            borderRadius: '12px',
          }}
        >
          <div
            style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--primary)', lineHeight: 1 }}
          >
            {result}
          </div>
          <div
            style={{
              fontWeight: 600,
              color: 'var(--text)',
              marginTop: '0.4rem',
              fontSize: '1.05rem',
            }}
          >
            {info.keyword}
          </div>
          <p
            style={{
              color: 'var(--text-muted)',
              fontSize: '0.9rem',
              marginTop: '0.5rem',
              marginBottom: 0,
            }}
          >
            {info.description}
          </p>
        </motion.div>
      )}
      {result !== null && !info && (
        <div style={{ marginTop: '1rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          Check the date format — try YYYY-MM-DD.
        </div>
      )}
    </div>
  );
}

// ─── Section wrapper ─────────────────────────────────────────────────────────

function Section({
  id,
  children,
  style,
}: {
  id?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <motion.section
      id={id}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5 }}
      style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '5rem 1.5rem',
        ...style,
      }}
    >
      {children}
    </motion.section>
  );
}

function SectionHeading({ eyebrow, title, sub }: { eyebrow: string; title: string; sub?: string }) {
  return (
    <div style={{ marginBottom: '2.5rem' }}>
      <div
        style={{
          fontSize: '0.75rem',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
          color: 'var(--primary)',
          fontWeight: 600,
          marginBottom: '0.6rem',
        }}
      >
        {eyebrow}
      </div>
      <h2
        style={{
          fontSize: 'clamp(1.5rem, 4vw, 2rem)',
          fontFamily: 'var(--font-display)',
          fontWeight: 600,
          color: 'var(--text)',
          margin: 0,
          lineHeight: 1.25,
        }}
      >
        {title}
      </h2>
      {sub && (
        <p
          style={{
            marginTop: '0.75rem',
            color: 'var(--text-muted)',
            fontSize: '1rem',
            maxWidth: '600px',
            lineHeight: 1.6,
          }}
        >
          {sub}
        </p>
      )}
    </div>
  );
}

// ─── Main view ───────────────────────────────────────────────────────────────

const ELEMENT_COLORS: Record<string, string> = {
  Fire: '#f97316',
  Earth: '#84cc16',
  Air: '#38bdf8',
  Water: '#818cf8',
};

export function HomeSupportView() {
  const [activeSign, setActiveSign] = useState<number | null>(null);

  return (
    <>
      <Helmet>
        <title>AstroNumeric — Learn Astrology & Numerology</title>
        <meta
          name="description"
          content="A clear, honest guide to astrology and numerology. Understand birth charts, zodiac signs, planets, houses, and how numerology works."
        />
      </Helmet>

      {/* ── Hero ── */}
      <section
        style={{
          textAlign: 'center',
          padding: '6rem 1.5rem 4rem',
          maxWidth: '700px',
          margin: '0 auto',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--primary)',
              fontWeight: 600,
              marginBottom: '1rem',
            }}
          >
            A guide for curious minds
          </div>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'clamp(2rem, 6vw, 3.2rem)',
              fontWeight: 700,
              lineHeight: 1.15,
              margin: '0 0 1.25rem',
              color: 'var(--text)',
            }}
          >
            Understanding Astrology
            <br />& Numerology
          </h1>
          <p
            style={{
              color: 'var(--text-muted)',
              fontSize: '1.1rem',
              lineHeight: 1.7,
              maxWidth: '520px',
              margin: '0 auto 2rem',
            }}
          >
            These are symbolic languages — not predictions. They offer frameworks for
            self-reflection. Here&apos;s what they actually say.
          </p>
          <div
            style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}
          >
            {[
              ['#astrology', 'Astrology'],
              ['#numerology', 'Numerology'],
              ['#calculator', 'Find Your Number'],
            ].map(([href, label]) => (
              <a
                key={href}
                href={href}
                style={{
                  padding: '0.6rem 1.25rem',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: '8px',
                  color: 'var(--text-muted)',
                  textDecoration: 'none',
                  fontSize: '0.9rem',
                  transition: 'border-color 0.2s',
                }}
              >
                {label}
              </a>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── Divider ── */}
      <div
        style={{
          maxWidth: '900px',
          margin: '0 auto',
          borderTop: '1px solid rgba(255,255,255,0.06)',
        }}
      />

      {/* ── What is astrology ── */}
      <Section id="astrology">
        <SectionHeading
          eyebrow="Astrology"
          title="What a birth chart actually is"
          sub="A birth chart — or natal chart — is a map of where the planets were at the exact moment you were born, from the perspective of your location on Earth. It's not a prediction. It's a symbolic snapshot."
        />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '1rem',
          }}
        >
          {[
            {
              label: 'Three core placements',
              body: 'Your Sun sign (conscious identity), Moon sign (emotional nature), and Rising sign (Ascendant — how you meet the world). These three alone explain most of the complexity people attribute to "just" a Sun sign.',
            },
            {
              label: 'Planets in signs',
              body: 'Every planet occupies a zodiac sign at birth. Mercury shows how you think. Venus shows what you value. Mars shows how you act. Each planet in its sign colours that area of life.',
            },
            {
              label: 'Houses',
              body: 'The chart is divided into 12 houses representing areas of life — career, relationships, home, money, and so on. The sign on each house cusp and any planets within it describe the tone of that area.',
            },
            {
              label: 'Aspects',
              body: 'Planets form geometric angles (aspects) to each other. A conjunction means two energies merge. A square creates tension. A trine flows easily. Aspects show how planetary energies interact.',
            },
          ].map(({ label, body }) => (
            <div
              key={label}
              style={{
                padding: '1.5rem',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '12px',
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  color: 'var(--text)',
                  marginBottom: '0.5rem',
                  fontSize: '0.95rem',
                }}
              >
                {label}
              </div>
              <p
                style={{
                  color: 'var(--text-muted)',
                  fontSize: '0.88rem',
                  lineHeight: 1.6,
                  margin: 0,
                }}
              >
                {body}
              </p>
            </div>
          ))}
        </div>
      </Section>

      {/* ── Elements ── */}
      <div
        style={{
          background: 'rgba(255,255,255,0.02)',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <Section>
          <SectionHeading
            eyebrow="The Four Elements"
            title="Fire, Earth, Air, Water"
            sub="Every sign belongs to one of four elements. The element shapes the fundamental quality of energy — before the specific sign characteristics apply."
          />
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
            }}
          >
            {ELEMENTS.map((el) => (
              <div
                key={el.name}
                style={{
                  padding: '1.5rem',
                  borderRadius: '12px',
                  border: `1px solid ${ELEMENT_COLORS[el.name]}22`,
                  background: `${ELEMENT_COLORS[el.name]}08`,
                }}
              >
                <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>{el.emoji}</div>
                <div
                  style={{
                    fontWeight: 700,
                    color: ELEMENT_COLORS[el.name],
                    marginBottom: '0.25rem',
                  }}
                >
                  {el.name}
                </div>
                <div
                  style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.6rem' }}
                >
                  {el.signs}
                </div>
                <p
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-muted)',
                    margin: 0,
                    lineHeight: 1.55,
                  }}
                >
                  {el.quality}
                </p>
              </div>
            ))}
          </div>
        </Section>
      </div>

      {/* ── Zodiac signs ── */}
      <Section>
        <SectionHeading
          eyebrow="The 12 Signs"
          title="The zodiac wheel"
          sub="Each sign occupies 30° of the 360° zodiac. The sign the Sun occupied at your birth is your 'Sun sign' — the one most commonly used in popular astrology. Tap any sign to read more."
        />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
            gap: '0.75rem',
            marginBottom: '1.5rem',
          }}
        >
          {ZODIAC.map((z, i) => (
            <button
              key={z.sign}
              onClick={() => setActiveSign(activeSign === i ? null : i)}
              style={{
                padding: '1rem 0.75rem',
                background: activeSign === i ? 'rgba(139,92,246,0.15)' : 'rgba(255,255,255,0.03)',
                border:
                  activeSign === i
                    ? '1px solid rgba(139,92,246,0.4)'
                    : '1px solid rgba(255,255,255,0.08)',
                borderRadius: '10px',
                cursor: 'pointer',
                textAlign: 'center',
                transition: 'all 0.2s',
              }}
            >
              <div style={{ fontSize: '1.5rem', color: ELEMENT_COLORS[z.element] }}>{z.symbol}</div>
              <div
                style={{
                  fontWeight: 600,
                  color: 'var(--text)',
                  fontSize: '0.85rem',
                  marginTop: '0.3rem',
                }}
              >
                {z.sign}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.15rem' }}>
                {z.element}
              </div>
            </button>
          ))}
        </div>
        {activeSign !== null && (
          <motion.div
            key={activeSign}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            style={{
              padding: '1.5rem',
              background: 'rgba(139,92,246,0.07)',
              border: '1px solid rgba(139,92,246,0.2)',
              borderRadius: '12px',
            }}
          >
            <div
              style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', flexWrap: 'wrap' }}
            >
              <div
                style={{ fontSize: '2.5rem', color: ELEMENT_COLORS[ZODIAC[activeSign].element] }}
              >
                {ZODIAC[activeSign].symbol}
              </div>
              <div>
                <div style={{ fontWeight: 700, color: 'var(--text)', fontSize: '1.1rem' }}>
                  {ZODIAC[activeSign].sign}
                </div>
                <div
                  style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}
                >
                  {ZODIAC[activeSign].dates} · {ZODIAC[activeSign].element} · Ruled by{' '}
                  {ZODIAC[activeSign].ruling}
                </div>
                <p
                  style={{
                    color: 'var(--text-muted)',
                    fontSize: '0.9rem',
                    marginTop: '0.6rem',
                    lineHeight: 1.6,
                    marginBottom: 0,
                  }}
                >
                  {ZODIAC[activeSign].trait}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </Section>

      {/* ── Planets ── */}
      <div
        style={{
          background: 'rgba(255,255,255,0.02)',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <Section>
          <SectionHeading
            eyebrow="Planetary Influences"
            title="What each planet governs"
            sub="In a birth chart, each planet represents a different dimension of experience. The sign it occupies colours how that energy expresses."
          />
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
              gap: '0.75rem',
            }}
          >
            {PLANETS.map((p) => (
              <div
                key={p.name}
                style={{
                  display: 'flex',
                  gap: '1rem',
                  alignItems: 'flex-start',
                  padding: '1rem 1.25rem',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: '10px',
                }}
              >
                <div
                  style={{
                    fontSize: '1.4rem',
                    flexShrink: 0,
                    color: 'var(--primary)',
                    width: '2rem',
                    textAlign: 'center',
                    marginTop: '2px',
                  }}
                >
                  {p.symbol}
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.9rem' }}>
                    {p.name}
                  </div>
                  <p
                    style={{
                      color: 'var(--text-muted)',
                      fontSize: '0.82rem',
                      margin: '0.25rem 0 0',
                      lineHeight: 1.5,
                    }}
                  >
                    {p.governs}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>

      {/* ── Numerology intro ── */}
      <Section id="numerology">
        <SectionHeading
          eyebrow="Numerology"
          title="What numerology actually does"
          sub="Numerology assigns meaning to numbers derived from your date of birth and name. The most widely used system is Pythagorean. It's a symbolic framework — not a prediction system."
        />
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: '1rem',
            marginBottom: '2rem',
          }}
        >
          {[
            {
              label: 'Life Path Number',
              body: 'Calculated from your full date of birth. Considered the most significant number — it reflects the overarching theme of your life and the qualities you are here to develop.',
            },
            {
              label: 'Expression (Destiny) Number',
              body: 'Derived from all the letters in your full birth name. Reflects your natural abilities — what you are naturally inclined toward and capable of.',
            },
            {
              label: 'Soul Urge Number',
              body: 'Calculated from the vowels in your name only. Said to reflect your inner motivation — what you genuinely want beneath the surface.',
            },
            {
              label: 'Personal Year Number',
              body: 'Changes annually. Calculated from your birth month, birth day, and the current year. Reflects the general theme of a given 12-month cycle in your life.',
            },
          ].map(({ label, body }) => (
            <div
              key={label}
              style={{
                padding: '1.5rem',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.08)',
                borderRadius: '12px',
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  color: 'var(--text)',
                  marginBottom: '0.5rem',
                  fontSize: '0.95rem',
                }}
              >
                {label}
              </div>
              <p
                style={{
                  color: 'var(--text-muted)',
                  fontSize: '0.88rem',
                  lineHeight: 1.6,
                  margin: 0,
                }}
              >
                {body}
              </p>
            </div>
          ))}
        </div>

        <div
          style={{
            padding: '1.25rem 1.5rem',
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '12px',
            fontSize: '0.875rem',
            color: 'var(--text-muted)',
            lineHeight: 1.65,
          }}
        >
          <strong style={{ color: 'var(--text)' }}>How Life Path is calculated:</strong> Reduce each
          part of your birth date to a single digit (or master number: 11, 22, 33), then add them
          together and reduce again. Example: April 15, 1990 → Month 4 + Day 6 (1+5) + Year 1
          (1+9+9+0=19→10→1) = 11. Life Path 11.
        </div>
      </Section>

      {/* ── LP Numbers reference ── */}
      <div
        style={{
          background: 'rgba(255,255,255,0.02)',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <Section>
          <SectionHeading
            eyebrow="Life Path Numbers"
            title="What each number means"
            sub="Each Life Path number carries a particular set of themes. These are tendencies — not fixed destinies."
          />
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
              gap: '0.75rem',
            }}
          >
            {Object.entries(LIFE_PATHS).map(([num, { keyword, description }]) => (
              <div
                key={num}
                style={{
                  display: 'flex',
                  gap: '1rem',
                  padding: '1rem 1.25rem',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.07)',
                  borderRadius: '10px',
                  alignItems: 'flex-start',
                }}
              >
                <div
                  style={{
                    fontWeight: 700,
                    fontSize: '1.2rem',
                    color: 'var(--primary)',
                    width: '2rem',
                    flexShrink: 0,
                    textAlign: 'center',
                    marginTop: '2px',
                  }}
                >
                  {num}
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem' }}>
                    {keyword}
                  </div>
                  <p
                    style={{
                      color: 'var(--text-muted)',
                      fontSize: '0.82rem',
                      margin: '0.25rem 0 0',
                      lineHeight: 1.5,
                    }}
                  >
                    {description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Section>
      </div>

      {/* ── Calculator ── */}
      <Section id="calculator">
        <SectionHeading
          eyebrow="Try it"
          title="Calculate your Life Path number"
          sub="Enter your date of birth. The calculation runs locally — nothing is sent anywhere."
        />
        <LifePathCalc />
      </Section>

      {/* ── Honesty note ── */}
      <div
        style={{
          background: 'rgba(255,255,255,0.02)',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          borderBottom: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <Section style={{ padding: '3rem 1.5rem' }}>
          <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center' }}>
            <div
              style={{
                fontSize: '0.75rem',
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                color: 'var(--text-dim)',
                fontWeight: 600,
                marginBottom: '0.75rem',
              }}
            >
              A note on what this is
            </div>
            <p
              style={{
                color: 'var(--text-muted)',
                fontSize: '0.95rem',
                lineHeight: 1.7,
                margin: 0,
              }}
            >
              Astrology and numerology are symbolic systems. They don&apos;t predict events or
              determine outcomes. They offer frameworks for reflection — ways of noticing patterns
              and tendencies. Use them as a lens, not a rulebook.
            </p>
          </div>
        </Section>
      </div>

      {/* ── iOS CTA ── */}
      <Section style={{ padding: '5rem 1.5rem 6rem', textAlign: 'center' }}>
        <div
          style={{
            fontSize: '0.75rem',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--primary)',
            fontWeight: 600,
            marginBottom: '0.75rem',
          }}
        >
          AstroNumeric for iOS
        </div>
        <h2
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(1.4rem, 4vw, 1.9rem)',
            fontWeight: 600,
            color: 'var(--text)',
            margin: '0 0 0.75rem',
            lineHeight: 1.3,
          }}
        >
          Get personalised guidance based on your chart
        </h2>
        <p
          style={{
            color: 'var(--text-muted)',
            fontSize: '0.95rem',
            maxWidth: '420px',
            margin: '0 auto 2rem',
            lineHeight: 1.6,
          }}
        >
          Daily guidance, birth chart readings, and numerology — all calculated from your actual
          natal data. Coming to the App Store shortly.
        </p>
        <div
          style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', alignItems: 'center' }}
        >
          <a
            href="mailto:support@astromeric.com"
            style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none' }}
          >
            Questions: support@astromeric.com
          </a>
        </div>
      </Section>
    </>
  );
}
