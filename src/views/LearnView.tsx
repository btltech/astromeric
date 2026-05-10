import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  fetchLearningGlossary,
  fetchLearningModules,
  type LearningGlossaryEntry,
  type LearningModule,
} from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { useActiveProfile } from '../hooks';
import './ProductDesk.css';
import './LearnView.css';

type LearnCategoryId = 'astrology' | 'numerology' | 'zodiac' | 'elements';

type LearnCategory = {
  id: LearnCategoryId;
  label: string;
  icon: string;
  detail: string;
};

const COMPLETED_LESSON_STORAGE_KEY = 'astromeric_learning_progress_v1';

const learnCategories: LearnCategory[] = [
  {
    id: 'astrology',
    label: 'Astrology',
    icon: 'Spark',
    detail: 'Core chart literacy, planets, houses, and the reading language behind the chart desk.',
  },
  {
    id: 'numerology',
    label: 'Numerology',
    icon: 'Number',
    detail: 'Life Path, timing cycles, and the number logic behind the numerology desk.',
  },
  {
    id: 'zodiac',
    label: 'Zodiac',
    icon: 'Signs',
    detail: 'Sun, Moon, Rising, and sign archetypes for faster interpretation.',
  },
  {
    id: 'elements',
    label: 'Elements',
    icon: 'Elements',
    detail: 'Fire, Earth, Air, and Water as practical compatibility and temperament language.',
  },
];

const fallbackModulesByCategory: Record<LearnCategoryId, LearningModule[]> = {
  astrology: [
    {
      id: 'astro-1',
      title: 'What is Astrology?',
      description: 'Understand the system before trying to interpret the signal.',
      category: 'astrology',
      difficulty: 'beginner',
      duration_minutes: 5,
      content:
        'Astrology treats the sky as a symbolic map. The point is not decoration. The point is learning how planets, signs, houses, and aspects combine into a readable pattern you can actually use.',
      keywords: ['astrology', 'basics', 'patterns'],
      related_modules: ['astro-2', 'astro-3'],
      item_count: 3,
    },
    {
      id: 'astro-2',
      title: 'The Birth Chart',
      description: 'Read the chart as a system instead of a pile of isolated facts.',
      category: 'astrology',
      difficulty: 'beginner',
      duration_minutes: 8,
      content:
        'A natal chart is a snapshot of the sky at birth. Signs describe style, planets describe functions, houses describe life areas, and aspects describe relationships between signals. Meaning comes from the combination.',
      keywords: ['birth chart', 'natal chart', 'houses'],
      related_modules: ['astro-1', 'astro-3'],
      item_count: 3,
    },
    {
      id: 'astro-3',
      title: 'Planets and Meanings',
      description: 'Know what each planetary voice is actually responsible for.',
      category: 'astrology',
      difficulty: 'intermediate',
      duration_minutes: 10,
      content:
        'The Sun is identity, the Moon is emotional regulation, Mercury is thinking and language, Venus is attraction and taste, and Mars is action. Interpreting a chart gets easier when each planet keeps a clear job.',
      keywords: ['planets', 'sun', 'moon', 'mercury'],
      related_modules: ['astro-2'],
      item_count: 4,
    },
  ],
  numerology: [
    {
      id: 'num-1',
      title: 'Introduction to Numerology',
      description: 'Treat numbers as a timing language, not a novelty add-on.',
      category: 'numerology',
      difficulty: 'beginner',
      duration_minutes: 5,
      content:
        'Numerology maps recurring number patterns to character, timing, and life cycles. The strongest web use case is practical: connect core numbers to the present cycle and turn them into an action read.',
      keywords: ['numerology', 'timing', 'cycles'],
      related_modules: ['num-2', 'num-3'],
      item_count: 3,
    },
    {
      id: 'num-2',
      title: 'Life Path Number',
      description: 'Use the Life Path as the long-arc lens, not the whole story.',
      category: 'numerology',
      difficulty: 'beginner',
      duration_minutes: 7,
      content:
        'The Life Path frames the long-term orientation of a person: how they move, what they are learning, and what patterns repeat. It becomes most useful when paired with the active Personal Year.',
      keywords: ['life path', 'destiny', 'purpose'],
      related_modules: ['num-1', 'num-3'],
      item_count: 3,
    },
    {
      id: 'num-3',
      title: 'Personal Year Cycles',
      description: 'Translate annual number themes into present-tense decisions.',
      category: 'numerology',
      difficulty: 'intermediate',
      duration_minutes: 8,
      content:
        'Personal Years run in nine-year cycles. A Year 1 resets, a Year 5 disrupts, and a Year 9 closes. The useful move is to treat the cycle as a timing posture, then test it against what is actually happening.',
      keywords: ['personal year', 'cycles', 'timing'],
      related_modules: ['num-2'],
      item_count: 3,
    },
  ],
  zodiac: [
    {
      id: 'zodiac-1',
      title: 'The 12 Signs',
      description: 'Learn the signs as archetypes with different operating styles.',
      category: 'zodiac',
      difficulty: 'beginner',
      duration_minutes: 10,
      content:
        'Signs are styles, not total identities. Aries initiates, Taurus stabilizes, Gemini connects, Cancer protects, Leo radiates, Virgo refines, Libra balances, Scorpio intensifies, Sagittarius expands, Capricorn structures, Aquarius reframes, and Pisces dissolves.',
      keywords: ['zodiac', 'signs', 'archetypes'],
      related_modules: ['zodiac-2', 'zodiac-3'],
      item_count: 3,
    },
    {
      id: 'zodiac-2',
      title: 'Sun, Moon, and Rising',
      description: 'Read the Big Three before you chase deeper detail.',
      category: 'zodiac',
      difficulty: 'intermediate',
      duration_minutes: 8,
      content:
        'The Sun shows identity, the Moon shows emotional patterning, and the Rising sign shapes presentation and how experience arrives. This is the fastest reliable shorthand when the full chart is still loading in the user’s head.',
      keywords: ['sun', 'moon', 'rising'],
      related_modules: ['zodiac-1'],
      item_count: 3,
    },
    {
      id: 'zodiac-3',
      title: 'Sign Compatibility',
      description: 'Use signs for quick pattern recognition, not final verdicts.',
      category: 'zodiac',
      difficulty: 'intermediate',
      duration_minutes: 10,
      content:
        'Sign compatibility is useful as a first scan. It helps you see natural ease, friction style, and pacing differences. It becomes trustworthy only after you add elements, modalities, and the deeper pairing context.',
      keywords: ['compatibility', 'signs', 'elements'],
      related_modules: ['zodiac-2'],
      item_count: 3,
    },
  ],
  elements: [
    {
      id: 'elem-1',
      title: 'Fire Signs',
      description: 'Aries, Leo, and Sagittarius prioritize motion, courage, and momentum.',
      category: 'elements',
      difficulty: 'beginner',
      duration_minutes: 6,
      content:
        'Fire signs move by desire and energy. They respond quickly, prefer momentum over hesitation, and bring heat into every system they touch. That makes them useful to spot in both chart reading and compatibility.',
      keywords: ['fire', 'aries', 'leo', 'sagittarius'],
      related_modules: ['elem-2', 'elem-3', 'elem-4'],
      item_count: 4,
    },
    {
      id: 'elem-2',
      title: 'Earth Signs',
      description: 'Taurus, Virgo, and Capricorn stabilize, structure, and measure results.',
      category: 'elements',
      difficulty: 'beginner',
      duration_minutes: 6,
      content:
        'Earth signs move through reliability, material reality, and practical improvement. They help the system settle and become legible. In compatibility, they often show where grounding or friction around pacing appears.',
      keywords: ['earth', 'taurus', 'virgo', 'capricorn'],
      related_modules: ['elem-1', 'elem-3', 'elem-4'],
      item_count: 4,
    },
    {
      id: 'elem-3',
      title: 'Air Signs',
      description: 'Gemini, Libra, and Aquarius process experience through ideas and exchange.',
      category: 'elements',
      difficulty: 'beginner',
      duration_minutes: 6,
      content:
        'Air signs track thought, language, pattern recognition, and social motion. They are helpful for understanding how a chart speaks, negotiates, and reframes. In pairings they often surface intellectual affinity.',
      keywords: ['air', 'gemini', 'libra', 'aquarius'],
      related_modules: ['elem-1', 'elem-2', 'elem-4'],
      item_count: 4,
    },
    {
      id: 'elem-4',
      title: 'Water Signs',
      description: 'Cancer, Scorpio, and Pisces experience the world through feeling and depth.',
      category: 'elements',
      difficulty: 'beginner',
      duration_minutes: 6,
      content:
        'Water signs register emotional atmosphere, intuition, and undercurrents first. They are essential for interpreting sensitivity, bonding, and emotional pacing. In compatibility they often show where attunement or overwhelm lives.',
      keywords: ['water', 'cancer', 'scorpio', 'pisces'],
      related_modules: ['elem-1', 'elem-2', 'elem-3'],
      item_count: 4,
    },
  ],
};

const fallbackGlossaryEntries: LearningGlossaryEntry[] = [
  {
    term: 'Aspect',
    definition: 'The angular relationship between two planets and the tension or harmony it creates.',
    category: 'astrology',
    usage_example: 'A trine usually reads as easier flow between two planetary functions.',
    related_terms: ['conjunction', 'trine', 'opposition'],
  },
  {
    term: 'House',
    definition: 'One of the twelve life areas used to place planetary experience into context.',
    category: 'astrology',
    usage_example: 'The seventh house tends to frame partnerships, contracts, and one-to-one dynamics.',
    related_terms: ['cusp', 'ruler'],
  },
  {
    term: 'Life Path',
    definition: 'The core numerology number derived from the birth date that frames long-arc direction.',
    category: 'numerology',
    usage_example: 'A Life Path 6 often emphasizes care, responsibility, and relational duty.',
    related_terms: ['destiny number', 'personal year'],
  },
  {
    term: 'Rising Sign',
    definition: 'The zodiac sign on the eastern horizon at birth, used to frame how life arrives and how a person presents.',
    category: 'zodiac',
    usage_example: 'The Rising sign often shapes the first impression before the Sun sign becomes visible.',
    related_terms: ['ascendant', 'houses'],
  },
  {
    term: 'Personal Year',
    definition: 'A numerology cycle that describes the main annual timing theme a person is moving through.',
    category: 'numerology',
    usage_example: 'A Personal Year 9 often brings completion, closure, or necessary release.',
    related_terms: ['life path', 'cycles'],
  },
];

function readCompletedModuleIds() {
  if (typeof window === 'undefined') {
    return [] as string[];
  }

  try {
    const stored = window.localStorage.getItem(COMPLETED_LESSON_STORAGE_KEY);
    return stored ? ((JSON.parse(stored) as string[]).filter(Boolean)) : [];
  } catch {
    return [] as string[];
  }
}

function writeCompletedModuleIds(moduleIds: string[]) {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.setItem(COMPLETED_LESSON_STORAGE_KEY, JSON.stringify(moduleIds));
}

function formatDifficulty(value?: string) {
  if (!value) {
    return 'Open level';
  }

  return value.replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatDuration(value?: number) {
  return value ? `${value} min` : 'Flexible';
}

function trimCopy(text: string, maxLength = 170) {
  return text.length <= maxLength ? text : `${text.slice(0, maxLength - 1).trimEnd()}...`;
}

export function LearnView() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();
  const [selectedCategory, setSelectedCategory] = useState<LearnCategoryId>('astrology');
  const [modules, setModules] = useState<LearningModule[]>(fallbackModulesByCategory.astrology);
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(
    fallbackModulesByCategory.astrology[0]?.id ?? null
  );
  const [glossaryEntries, setGlossaryEntries] = useState<LearningGlossaryEntry[]>([]);
  const [selectedGlossaryTerm, setSelectedGlossaryTerm] = useState<string | null>(null);
  const [glossarySearch, setGlossarySearch] = useState('');
  const [selectedGlossaryCategory, setSelectedGlossaryCategory] = useState('all');
  const [completedModuleIds, setCompletedModuleIds] = useState<string[]>(() =>
    readCompletedModuleIds()
  );
  const [loadingModules, setLoadingModules] = useState(true);
  const [loadingGlossary, setLoadingGlossary] = useState(true);
  const [moduleIssue, setModuleIssue] = useState<string | null>(null);
  const [glossaryIssue, setGlossaryIssue] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadModules() {
      setLoadingModules(true);

      try {
        const response = await fetchLearningModules(selectedCategory);
        const nextModules =
          response.modules.length > 0
            ? response.modules
            : fallbackModulesByCategory[selectedCategory];

        if (!isCancelled) {
          setModules(nextModules);
          setSelectedModuleId((current) =>
            nextModules.some((module) => module.id === current) ? current : nextModules[0]?.id ?? null
          );
          setModuleIssue(
            response.modules.length > 0
              ? null
              : 'Showing built-in lessons for this category.'
          );
        }
      } catch {
        if (!isCancelled) {
          const fallbackModules = fallbackModulesByCategory[selectedCategory];
          setModules(fallbackModules);
          setSelectedModuleId((current) =>
            fallbackModules.some((module) => module.id === current)
              ? current
              : fallbackModules[0]?.id ?? null
          );
          setModuleIssue(
            'Lesson content is temporarily unavailable. Showing built-in lessons instead.'
          );
        }
      } finally {
        if (!isCancelled) {
          setLoadingModules(false);
        }
      }
    }

    void loadModules();

    return () => {
      isCancelled = true;
    };
  }, [selectedCategory]);

  useEffect(() => {
    let isCancelled = false;

    async function loadGlossary() {
      setLoadingGlossary(true);

      try {
        const response = await fetchLearningGlossary();
        const nextEntries = response.entries.length > 0 ? response.entries : fallbackGlossaryEntries;

        if (!isCancelled) {
          setGlossaryEntries(nextEntries);
          setSelectedGlossaryTerm((current) =>
            nextEntries.some((entry) => entry.term === current) ? current : nextEntries[0]?.term ?? null
          );
          setGlossaryIssue(
            response.entries.length > 0
              ? null
              : 'Showing built-in glossary entries.'
          );
        }
      } catch {
        if (!isCancelled) {
          setGlossaryEntries(fallbackGlossaryEntries);
          setSelectedGlossaryTerm((current) =>
            fallbackGlossaryEntries.some((entry) => entry.term === current)
              ? current
              : fallbackGlossaryEntries[0]?.term ?? null
          );
          setGlossaryIssue(
            'Glossary is temporarily unavailable. Showing built-in entries instead.'
          );
        }
      } finally {
        if (!isCancelled) {
          setLoadingGlossary(false);
        }
      }
    }

    void loadGlossary();

    return () => {
      isCancelled = true;
    };
  }, []);

  const selectedCategoryMeta = useMemo(
    () => learnCategories.find((category) => category.id === selectedCategory) ?? learnCategories[0],
    [selectedCategory]
  );
  const completedModuleIdSet = useMemo(() => new Set(completedModuleIds), [completedModuleIds]);
  const selectedModule = useMemo(
    () => modules.find((module) => module.id === selectedModuleId) ?? modules[0] ?? null,
    [modules, selectedModuleId]
  );
  const completedInCategory = useMemo(
    () => modules.filter((module) => completedModuleIdSet.has(module.id)).length,
    [completedModuleIdSet, modules]
  );
  const completionRate = modules.length > 0 ? Math.round((completedInCategory / modules.length) * 100) : 0;
  const nextLesson = useMemo(
    () => modules.find((module) => !completedModuleIdSet.has(module.id)) ?? modules[0] ?? null,
    [completedModuleIdSet, modules]
  );
  const relatedModules = useMemo(
    () =>
      (selectedModule?.related_modules ?? [])
        .map((relatedId) => modules.find((module) => module.id === relatedId) ?? null)
        .filter((module): module is LearningModule => Boolean(module)),
    [modules, selectedModule?.related_modules]
  );
  const glossaryCategories = useMemo(
    () => ['all', ...Array.from(new Set(glossaryEntries.map((entry) => entry.category))).sort()],
    [glossaryEntries]
  );
  const filteredGlossaryEntries = useMemo(
    () =>
      glossaryEntries.filter((entry) => {
        const matchesCategory = selectedGlossaryCategory === 'all' || entry.category === selectedGlossaryCategory;
        const matchesSearch =
          glossarySearch.trim().length === 0 ||
          entry.term.toLowerCase().includes(glossarySearch.trim().toLowerCase()) ||
          entry.definition.toLowerCase().includes(glossarySearch.trim().toLowerCase());

        return matchesCategory && matchesSearch;
      }),
    [glossaryEntries, glossarySearch, selectedGlossaryCategory]
  );

  useEffect(() => {
    setSelectedGlossaryTerm((current) =>
      filteredGlossaryEntries.some((entry) => entry.term === current)
        ? current
        : filteredGlossaryEntries[0]?.term ?? null
    );
  }, [filteredGlossaryEntries]);

  const selectedGlossaryEntry = useMemo(
    () => filteredGlossaryEntries.find((entry) => entry.term === selectedGlossaryTerm) ?? filteredGlossaryEntries[0] ?? null,
    [filteredGlossaryEntries, selectedGlossaryTerm]
  );
  const profileLabel = hasActiveProfile ? activeProfile?.name ?? 'Connected' : 'Optional';
  const profileSourceLabel = hasActiveProfile ? activeProfileSourceLabel : 'No active profile';
  const learnIssues = [moduleIssue, glossaryIssue].filter((issue): issue is string => Boolean(issue));

  function handleToggleComplete(moduleId: string) {
    setCompletedModuleIds((current) => {
      const next = current.includes(moduleId)
        ? current.filter((id) => id !== moduleId)
        : [...current, moduleId];
      writeCompletedModuleIds(next);
      return next;
    });
  }

  return (
    <div className="product-desk learn-view">
      <DocumentMeta
        title="AstroNumeric — Learn Desk"
        description="Lessons, glossary, and study progress for astrology and numerology."
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Learn desk</span>
        <h1>Astrology and numerology — explained.</h1>
        <p>
          Lessons, glossary, and study progress in one place. Start with a category, go deep on
          a lesson, then look up any term that needs more context.
        </p>
        <div className="product-desk__chips">
          <span className="product-desk__chip">Category lanes</span>
          <span className="product-desk__chip">Lesson detail</span>
          <span className="product-desk__chip">Glossary search</span>
          <span className="product-desk__chip">Progress tracking</span>
        </div>
        <div className="product-desk__actions">
          <a href="#lesson-library" className="btn-primary product-desk__action">
            Open lesson library
          </a>
          <a href="#glossary-lane" className="btn-secondary product-desk__action">
            Open glossary lane
          </a>
          <Link to="/charts" className="btn-secondary product-desk__action">
            Return to charts
          </Link>
        </div>
      </section>

      {learnIssues.length > 0 ? (
        <div className="learn-view__alert" role="status">
          <strong>Partial learning data</strong>
          <p>{learnIssues.join(' ')}</p>
        </div>
      ) : null}

      <section className="product-desk__grid">
        <article className="product-desk__panel">
          <h2>Study context</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Active profile</span>
              <span className="product-desk__value">{profileLabel}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Profile source</span>
              <span className="product-desk__value">{profileSourceLabel}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Current lane</span>
              <span className="product-desk__value">{selectedCategoryMeta.label}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Category progress</span>
              <span className="product-desk__value">{loadingModules ? 'Loading...' : `${completionRate}%`}</span>
            </div>
          </div>
          <p className="product-desk__note">
            Explore a category after running a reading, chart pass, or compatibility check to understand what drove the result.
          </p>
        </article>

        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Category lanes</h2>
          <p className="product-desk__note">Pick the learning lane that matches the desk the user just came from.</p>
          <div className="learn-view__category-row" role="tablist" aria-label="Learn categories">
            {learnCategories.map((category) => (
              <button
                key={category.id}
                type="button"
                className={
                  selectedCategory === category.id
                    ? 'learn-view__category-chip learn-view__category-chip--active'
                    : 'learn-view__category-chip'
                }
                onClick={() => setSelectedCategory(category.id)}
              >
                <span>{category.icon}</span>
                <strong>{category.label}</strong>
                <small>{category.detail}</small>
              </button>
            ))}
          </div>
        </article>

        <article id="lesson-library" className="product-desk__panel product-desk__panel--wide">
          <h2>Lesson library</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Lessons in lane</span>
              <span className="product-desk__value">{loadingModules ? 'Loading...' : modules.length}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Completed here</span>
              <span className="product-desk__value">{loadingModules ? 'Loading...' : completedInCategory}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Next lesson</span>
              <span className="product-desk__value">{nextLesson?.title ?? 'Waiting on lessons'}</span>
            </div>
          </div>
          <div className="learn-view__module-grid">
            {modules.map((module) => {
              const completed = completedModuleIdSet.has(module.id);

              return (
                <button
                  key={module.id}
                  type="button"
                  className={
                    module.id === selectedModule?.id
                      ? 'learn-view__module-card learn-view__module-card--active'
                      : 'learn-view__module-card'
                  }
                  onClick={() => setSelectedModuleId(module.id)}
                >
                  <div className="learn-view__module-topline">
                    <span className="product-desk__badge">{formatDifficulty(module.difficulty)}</span>
                    <span>{formatDuration(module.duration_minutes)}</span>
                  </div>
                  <strong>{module.title}</strong>
                  <p>{trimCopy(module.description, 120)}</p>
                  <div className="learn-view__module-topline learn-view__module-topline--foot">
                    <span>{module.category ?? selectedCategoryMeta.label}</span>
                    <span>{completed ? 'Completed' : 'Open lesson'}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </article>

        <article className="product-desk__panel">
          <h2>Lesson detail</h2>
          {selectedModule ? (
            <div className="learn-view__detail-stack">
              <div className="learn-view__detail-header">
                <span className="product-desk__badge">{formatDifficulty(selectedModule.difficulty)}</span>
                <strong>{selectedModule.title}</strong>
                <p>{selectedModule.description}</p>
              </div>
              <div className="learn-view__detail-meta">
                <span>{formatDuration(selectedModule.duration_minutes)}</span>
                <span>{selectedModule.category ?? selectedCategoryMeta.label}</span>
                <span>{completedModuleIdSet.has(selectedModule.id) ? 'Completed' : 'Not completed'}</span>
              </div>
              <p className="product-desk__note">{selectedModule.content ?? selectedModule.description}</p>

              {(selectedModule.keywords ?? []).length > 0 ? (
                <div className="learn-view__keyword-row">
                  {(selectedModule.keywords ?? []).map((keyword) => (
                    <span key={keyword} className="learn-view__keyword">
                      {keyword}
                    </span>
                  ))}
                </div>
              ) : null}

              {relatedModules.length > 0 ? (
                <div className="learn-view__related-row">
                  <span className="product-desk__label">Related lessons</span>
                  <div className="product-desk__linkgrid">
                    {relatedModules.map((module) => (
                      <button
                        key={module.id}
                        type="button"
                        className="product-desk__linkcard learn-view__related-card"
                        onClick={() => setSelectedModuleId(module.id)}
                      >
                        <strong>{module.title}</strong>
                        <span>{trimCopy(module.description, 90)}</span>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              <button
                type="button"
                className={
                  completedModuleIdSet.has(selectedModule.id)
                    ? 'btn-secondary learn-view__complete-button'
                    : 'btn-primary learn-view__complete-button'
                }
                onClick={() => handleToggleComplete(selectedModule.id)}
              >
                {completedModuleIdSet.has(selectedModule.id) ? 'Mark as not completed' : 'Mark lesson completed'}
              </button>
            </div>
          ) : (
            <p className="product-desk__note">Pick a lesson from the library to open its detail view.</p>
          )}
        </article>

        <article id="glossary-lane" className="product-desk__panel product-desk__panel--full">
          <h2>Glossary lane</h2>
          <div className="learn-view__glossary-controls">
            <input
              type="search"
              value={glossarySearch}
              onChange={(event) => setGlossarySearch(event.target.value)}
              className="learn-view__search"
              placeholder="Search terms, definitions, or desk language..."
            />
            <div className="learn-view__glossary-filters">
              {glossaryCategories.map((category) => (
                <button
                  key={category}
                  type="button"
                  className={
                    selectedGlossaryCategory === category
                      ? 'learn-view__filter-chip learn-view__filter-chip--active'
                      : 'learn-view__filter-chip'
                  }
                  onClick={() => setSelectedGlossaryCategory(category)}
                >
                  {category === 'all' ? 'All terms' : category}
                </button>
              ))}
            </div>
          </div>

          <div className="learn-view__glossary-layout">
            <div className="learn-view__term-list">
              {loadingGlossary && glossaryEntries.length === 0 ? (
                <p className="product-desk__note">Loading glossary terms...</p>
              ) : filteredGlossaryEntries.length > 0 ? (
                filteredGlossaryEntries.map((entry) => (
                  <button
                    key={entry.term}
                    type="button"
                    className={
                      selectedGlossaryEntry?.term === entry.term
                        ? 'learn-view__term-button learn-view__term-button--active'
                        : 'learn-view__term-button'
                    }
                    onClick={() => setSelectedGlossaryTerm(entry.term)}
                  >
                    <strong>{entry.term}</strong>
                    <span>{entry.category}</span>
                  </button>
                ))
              ) : (
                <p className="product-desk__note">No glossary entries match the current filters.</p>
              )}
            </div>

            <div className="learn-view__glossary-detail">
              {selectedGlossaryEntry ? (
                <>
                  <div className="learn-view__detail-header">
                    <span className="product-desk__badge">{selectedGlossaryEntry.category}</span>
                    <strong>{selectedGlossaryEntry.term}</strong>
                    <p>{selectedGlossaryEntry.definition}</p>
                  </div>
                  <div className="learn-view__definition-block">
                    <span className="product-desk__label">Usage example</span>
                    <p>{selectedGlossaryEntry.usage_example}</p>
                  </div>
                  {selectedGlossaryEntry.related_terms.length > 0 ? (
                    <div className="learn-view__definition-block">
                      <span className="product-desk__label">Related terms</span>
                      <div className="learn-view__keyword-row">
                        {selectedGlossaryEntry.related_terms.map((term) => (
                          <span key={term} className="learn-view__keyword">
                            {term}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </>
              ) : (
                <p className="product-desk__note">Pick a glossary term to open its definition and usage.</p>
              )}
            </div>
          </div>
        </article>

        <article className="product-desk__panel">
          <h2>Suggested loop</h2>
          <div className="product-desk__linkgrid">
            <Link to="/reading" className="product-desk__linkcard">
              <strong>Generate a reading</strong>
              <span>Start with a live result, then open learn when a term or pattern needs context.</span>
            </Link>
            <Link to="/journal" className="product-desk__linkcard">
              <strong>Capture the lesson</strong>
              <span>Move from study into the journal workspace once the user has something to test or apply.</span>
            </Link>
            <Link to="/tools" className="product-desk__linkcard">
              <strong>Use the tools desk</strong>
              <span>Take sharper questions into tarot, timing, or guide flows after the concept is clear.</span>
            </Link>
          </div>
        </article>

        <article className="product-desk__panel">
          <h2>Next move</h2>
          <p className="product-desk__note">
            {nextLesson
              ? `Continue with ${nextLesson.title} in the ${selectedCategoryMeta.label} lane, then use the glossary lane to clear up any terms that still feel fuzzy.`
              : 'Pick a category lane first, then use the glossary lane to ground the vocabulary before you return to the desks.'}
          </p>
        </article>
      </section>
    </div>
  );
}

export default LearnView;