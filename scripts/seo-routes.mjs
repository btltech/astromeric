/**
 * seo-routes.mjs
 * --------------
 * Single source of truth for prerendered public routes.
 *
 * Each entry drives BOTH the per-route <head> metadata and the crawlable HTML
 * content that is injected into #root at build time (see scripts/prerender.mjs).
 * React replaces this content on hydration, so it is a fallback for crawlers /
 * no-JS clients and a faster first contentful paint — never the live UI.
 *
 * Keep this list in sync with the routes declared in src/App.tsx.
 */

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const SITE_ORIGIN = 'https://astronumeric.com';
export const SITE_NAME = 'AstroNumeric';

// Shared single source of truth for per-route title/description, also consumed
// by the in-app views via src/seo/routeMeta.ts. Keeps static (prerendered) and
// runtime <title>/OG/Twitter tags from drifting apart.
const _dir = dirname(fileURLToPath(import.meta.url));
const ROUTE_META = JSON.parse(
  readFileSync(join(_dir, '..', 'src', 'seo', 'routeMeta.json'), 'utf8')
);

const ZODIAC = [
  ['Aries', 'The Ram · Mar 21 – Apr 19 · Fire · Cardinal'],
  ['Taurus', 'The Bull · Apr 20 – May 20 · Earth · Fixed'],
  ['Gemini', 'The Twins · May 21 – Jun 20 · Air · Mutable'],
  ['Cancer', 'The Crab · Jun 21 – Jul 22 · Water · Cardinal'],
  ['Leo', 'The Lion · Jul 23 – Aug 22 · Fire · Fixed'],
  ['Virgo', 'The Maiden · Aug 23 – Sep 22 · Earth · Mutable'],
  ['Libra', 'The Scales · Sep 23 – Oct 22 · Air · Cardinal'],
  ['Scorpio', 'The Scorpion · Oct 23 – Nov 21 · Water · Fixed'],
  ['Sagittarius', 'The Archer · Nov 22 – Dec 21 · Fire · Mutable'],
  ['Capricorn', 'The Goat · Dec 22 – Jan 19 · Earth · Cardinal'],
  ['Aquarius', 'The Water Bearer · Jan 20 – Feb 18 · Air · Fixed'],
  ['Pisces', 'The Fish · Feb 19 – Mar 20 · Water · Mutable'],
];

const NUMEROLOGY = [
  ['1', 'The Leader — independence, initiative, drive'],
  ['2', 'The Diplomat — partnership, balance, sensitivity'],
  ['3', 'The Communicator — creativity, expression, joy'],
  ['4', 'The Builder — structure, discipline, stability'],
  ['5', 'The Explorer — freedom, change, adventure'],
  ['6', 'The Nurturer — responsibility, care, harmony'],
  ['7', 'The Seeker — analysis, intuition, depth'],
  ['8', 'The Powerhouse — ambition, authority, abundance'],
  ['9', 'The Humanitarian — compassion, completion, wisdom'],
  ['11', 'Master Number — intuition, inspiration, vision'],
  ['22', 'Master Number — the master builder, large-scale impact'],
  ['33', 'Master Number — the master teacher, selfless service'],
];

const li = (items) => items.map(([t, d]) => `<li><strong>${t}:</strong> ${d}</li>`).join('');

/**
 * Shared internal navigation injected on every prerendered page so crawlers can
 * reach all public sections regardless of which page they land on.
 */
const navLinks = [
  ['/', 'Home'],
  ['/reading', 'Daily Readings'],
  ['/charts', 'Birth Chart'],
  ['/numerology', 'Numerology'],
  ['/relationships', 'Compatibility'],
  ['/tools', 'Cosmic Tools'],
  ['/year-ahead', 'Year Ahead'],
  ['/learn', 'Learn'],
];

export function prerenderNav() {
  return `<nav aria-label="Primary"><ul>${navLinks
    .map(([href, label]) => `<li><a href="${href}">${label}</a></li>`)
    .join('')}</ul></nav>`;
}

const routeDefs = [
  {
    path: '/',
    priority: '1.0',
    changefreq: 'weekly',
    h1: 'Astrology + Numerology in one clear daily signal',
    body: `
      <p>AstroNumeric blends your birth chart, numerology core numbers, compatibility,
      and planetary timing into a single daily reading — so you get one clear signal
      instead of five scattered horoscopes.</p>
      <section>
        <h2>What you get</h2>
        <ul>
          <li><a href="/reading">Daily, weekly &amp; monthly readings</a> across five life tracks</li>
          <li><a href="/charts">An accurate birth chart</a> with planets, houses and aspects</li>
          <li><a href="/numerology">Your full numerology profile</a> — Life Path, Expression and more</li>
          <li><a href="/relationships">Compatibility</a> blending astrology synastry and numerology</li>
          <li><a href="/tools">Moon phases and timing guidance</a> for when to act</li>
        </ul>
      </section>`,
  },
  {
    path: '/reading',
    title: 'Daily, Weekly & Monthly Readings | AstroNumeric',
    description:
      'Personalized daily, weekly, and monthly readings across five life tracks — General, Love, Money, Health, and Spiritual — with a TL;DR, affirmations, and a daily action.',
    priority: '0.9',
    changefreq: 'daily',
    h1: 'Daily, weekly & monthly readings',
    body: `
      <p>Get a personalized horoscope for the day, week, or month, tuned to your full
      chart and numerology rather than your sun sign alone.</p>
      <section>
        <h2>Five life tracks</h2>
        <ul>
          <li><strong>General:</strong> the overall theme and energy of the period</li>
          <li><strong>Love:</strong> relationships, connection, and timing in matters of the heart</li>
          <li><strong>Money:</strong> work, finances, and opportunity</li>
          <li><strong>Health:</strong> energy, rest, and wellbeing</li>
          <li><strong>Spiritual:</strong> growth, intuition, and inner work</li>
        </ul>
        <p>Each reading includes a TL;DR summary, a personalized affirmation, and a
        suggested daily action you can actually take.</p>
      </section>`,
  },
  {
    path: '/charts',
    title: 'Birth Chart & Natal Astrology | AstroNumeric',
    description:
      'Calculate an accurate natal birth chart with planetary positions, houses, aspects, ascendant, and midheaven — powered by the Swiss Ephemeris.',
    priority: '0.8',
    changefreq: 'weekly',
    h1: 'Your birth chart, calculated accurately',
    body: `
      <p>AstroNumeric computes your natal chart from your date, time, and place of
      birth using the Swiss Ephemeris for professional-grade accuracy.</p>
      <section>
        <h2>What your chart includes</h2>
        <ul>
          <li>Positions of the Sun, Moon, and planets by sign and house</li>
          <li>House cusps across your preferred house system (Placidus by default)</li>
          <li>Major aspects between planets, with orbs</li>
          <li>Your Ascendant (rising sign) and Midheaven</li>
        </ul>
      </section>`,
  },
  {
    path: '/numerology',
    title: 'Numerology Calculator — Life Path & Core Numbers | AstroNumeric',
    description:
      'A complete numerology profile: Life Path, Expression, Soul Urge, Personality, and Maturity numbers, plus Personal Year/Month/Day cycles, Pinnacles, and Challenges.',
    priority: '0.8',
    changefreq: 'weekly',
    h1: 'Your full numerology profile',
    body: `
      <p>Go beyond a single life-path number. AstroNumeric calculates your complete
      numerology profile from your name and birth date.</p>
      <section>
        <h2>Core numbers</h2>
        <ul>
          <li><strong>Life Path:</strong> your central life lesson and direction</li>
          <li><strong>Expression:</strong> your natural talents and how you express them</li>
          <li><strong>Soul Urge:</strong> your heart's deepest desires</li>
          <li><strong>Personality:</strong> how others first perceive you</li>
          <li><strong>Maturity:</strong> the self that emerges later in life</li>
        </ul>
        <h2>Cycles &amp; turning points</h2>
        <ul>
          <li>Personal Year, Month, and Day energies</li>
          <li>Pinnacles and Challenges across life's major chapters</li>
        </ul>
      </section>`,
  },
  {
    path: '/relationships',
    title: 'Compatibility — Astrology & Numerology Synastry | AstroNumeric',
    description:
      'Compare two people with astrology synastry and numerology compatibility for a combined relationship score, strengths, friction points, and practical advice.',
    priority: '0.7',
    changefreq: 'weekly',
    h1: 'Compatibility, blended across systems',
    body: `
      <p>See how two charts relate using both astrology and numerology, combined into
      a single, readable compatibility picture.</p>
      <section>
        <h2>How it works</h2>
        <ul>
          <li><strong>Astrology:</strong> sign, element, and modality comparison plus synastry</li>
          <li><strong>Numerology:</strong> Life Path and Expression number compatibility</li>
          <li><strong>Combined:</strong> an overall score with strengths, friction, and advice</li>
        </ul>
      </section>`,
  },
  {
    path: '/tools',
    title: 'Cosmic Tools — Moon Phases & Timing | AstroNumeric',
    description:
      'Track the current moon phase, find favourable timing for what matters, and follow live planetary movements and transits.',
    priority: '0.7',
    changefreq: 'daily',
    h1: 'Cosmic tools & timing',
    body: `
      <p>Know not just what is happening, but when to act on it.</p>
      <section>
        <h2>In the toolkit</h2>
        <ul>
          <li><strong>Moon phase tracker:</strong> the current phase, illumination, and rituals</li>
          <li><strong>Timing advisor:</strong> favourable windows for key activities</li>
          <li><strong>Transits:</strong> live planetary movements against your chart</li>
        </ul>
      </section>`,
  },
  {
    path: '/year-ahead',
    title: 'Year Ahead Forecast | AstroNumeric',
    description:
      'A forward look at your year: personal year cycle, month-by-month themes, and the timing of major turning points.',
    priority: '0.7',
    changefreq: 'weekly',
    h1: 'Your year ahead',
    body: `
      <p>Plan with the bigger picture in view. The year-ahead forecast maps your
      personal cycles onto the months to come.</p>
      <section>
        <h2>What it covers</h2>
        <ul>
          <li>Your Personal Year theme and what it asks of you</li>
          <li>Month-by-month outlook and shifting energies</li>
          <li>Timing of notable transits and turning points</li>
        </ul>
      </section>`,
  },
  {
    path: '/learn',
    title: 'Learning Center — Zodiac & Numerology Glossary | AstroNumeric',
    description:
      'Learn the meaning of all 12 zodiac signs and every numerology number, from Life Path 1 to the master numbers 11, 22, and 33.',
    priority: '0.6',
    changefreq: 'monthly',
    h1: 'Learning center',
    body: `
      <p>Plain-language explanations of the building blocks of astrology and
      numerology.</p>
      <section>
        <h2>The 12 zodiac signs</h2>
        <ul>${li(ZODIAC)}</ul>
      </section>
      <section>
        <h2>Numerology numbers</h2>
        <ul>${li(NUMEROLOGY)}</ul>
      </section>`,
  },
  {
    path: '/support',
    title: 'Support Center | AstroNumeric',
    description:
      'Help and answers for AstroNumeric — accounts, profiles, readings, charts, and billing.',
    priority: '0.4',
    changefreq: 'monthly',
    h1: 'Support center',
    body: `
      <p>Find answers about accounts and profiles, how readings and charts are
      calculated, and managing your data. Need more help? Reach the team from inside
      the app.</p>`,
  },
  {
    path: '/privacy-policy',
    title: 'Privacy Policy | AstroNumeric',
    description:
      'How AstroNumeric collects, uses, and protects your data, including birth details used to calculate your chart.',
    priority: '0.3',
    changefreq: 'yearly',
    h1: 'Privacy policy',
    body: `<p>This page explains what data AstroNumeric collects, how birth details
      are used to calculate your chart and readings, and the choices you have over
      your information.</p>`,
  },
  {
    path: '/terms',
    title: 'Terms of Service | AstroNumeric',
    description: 'The terms that govern your use of AstroNumeric.',
    priority: '0.3',
    changefreq: 'yearly',
    h1: 'Terms of service',
    body: `<p>These terms govern your access to and use of AstroNumeric, including
      acceptable use, content, and the limits of guidance provided for entertainment
      and self-reflection.</p>`,
  },
  {
    path: '/cookie-policy',
    title: 'Cookie Policy | AstroNumeric',
    description: 'How AstroNumeric uses cookies and similar technologies.',
    priority: '0.3',
    changefreq: 'yearly',
    h1: 'Cookie policy',
    body: `<p>This page describes the cookies and similar technologies AstroNumeric
      uses, what they do, and how you can control them.</p>`,
  },
];

// Apply the shared SEO title/description (single source of truth in
// src/seo/routeMeta.json) over any inline defaults, then export.
export const routes = routeDefs.map((r) => ({
  ...r,
  title: ROUTE_META[r.path]?.title ?? r.title,
  description: ROUTE_META[r.path]?.description ?? r.description,
}));
