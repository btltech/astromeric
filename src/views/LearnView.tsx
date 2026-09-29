import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import lessonLibrary from '../../backend/app/interpretation/library/lessons.json';
import {
  fetchLearningGlossary,
  type LearningGlossaryEntry,
  type LearningModule,
} from '../api/client';
import { DocumentMeta } from '../components/DocumentMeta';
import { getRouteMeta } from '../seo/routeMeta';
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

// The lessons are fixed text shared with the app and the API
// (backend/app/interpretation/library/lessons.json), so the website ships
// them instead of spending a visitor's daily API allowance on them.
const modulesByCategory = (lessonLibrary as Omit<LearningModule, 'item_count'>[]).reduce(
  (byCategory, lesson) => {
    const category = lesson.category as LearnCategoryId;
    byCategory[category].push({ ...lesson, item_count: lesson.keywords?.length ?? 1 });
    return byCategory;
  },
  { astrology: [], numerology: [], zodiac: [], elements: [] } as Record<
    LearnCategoryId,
    LearningModule[]
  >
);

const fallbackGlossaryEntries: LearningGlossaryEntry[] = [
  {
    term: 'Aspect',
    definition:
      'The angular relationship between two planets and the tension or harmony it creates.',
    category: 'astrology',
    usage_example: 'A trine usually reads as easier flow between two planetary functions.',
    related_terms: ['conjunction', 'trine', 'opposition'],
  },
  {
    term: 'House',
    definition: 'One of the twelve life areas used to place planetary experience into context.',
    category: 'astrology',
    usage_example:
      'The seventh house tends to frame partnerships, contracts, and one-to-one dynamics.',
    related_terms: ['cusp', 'ruler'],
  },
  {
    term: 'Life Path',
    definition:
      'The core numerology number derived from the birth date that frames long-arc direction.',
    category: 'numerology',
    usage_example: 'A Life Path 6 often emphasizes care, responsibility, and relational duty.',
    related_terms: ['destiny number', 'personal year'],
  },
  {
    term: 'Rising Sign',
    definition:
      'The zodiac sign on the eastern horizon at birth, used to frame how life arrives and how a person presents.',
    category: 'zodiac',
    usage_example:
      'The Rising sign often shapes the first impression before the Sun sign becomes visible.',
    related_terms: ['ascendant', 'houses'],
  },
  {
    term: 'Personal Year',
    definition:
      'A numerology cycle that describes the main annual timing theme a person is moving through.',
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
    return stored ? (JSON.parse(stored) as string[]).filter(Boolean) : [];
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

// Lessons use a tiny markup shared with the app: blank-line-separated blocks,
// "## " headings and "• " bullet lines. Rendered as real elements so the
// paragraphs don't collapse into one run of text.
function LessonBody({ text }: { text: string }) {
  const blocks = text
    .split(/\n\s*\n/)
    .map((block) => block.trim())
    .filter(Boolean);
  return (
    <div className="learn-view__drawer-content">
      {blocks.map((block, index) => {
        if (block.startsWith('## ')) {
          return <h3 key={index}>{block.slice(3)}</h3>;
        }
        const lines = block.split('\n');
        if (lines.every((line) => line.startsWith('• '))) {
          return (
            <ul key={index}>
              {lines.map((line, i) => (
                <li key={i}>{line.slice(2)}</li>
              ))}
            </ul>
          );
        }
        return <p key={index}>{block}</p>;
      })}
    </div>
  );
}

// Reading time from the lesson's length (about 200 words a minute). The
// hand-typed duration_minutes values overstated it 5-12 times.
function formatDuration(module: { content?: string; duration_minutes?: number }) {
  const words = module.content?.trim().split(/\s+/).length ?? 0;
  if (words > 0) return `${Math.max(1, Math.round(words / 200))} min read`;
  return module.duration_minutes ? `${module.duration_minutes} min read` : 'Flexible';
}

function trimCopy(text: string, maxLength = 170) {
  return text.length <= maxLength ? text : `${text.slice(0, maxLength - 1).trimEnd()}...`;
}

export function LearnView() {
  const { activeProfile, activeProfileSourceLabel, hasActiveProfile } = useActiveProfile();
  const [selectedCategory, setSelectedCategory] = useState<LearnCategoryId>('astrology');
  const [modules, setModules] = useState<LearningModule[]>(modulesByCategory.astrology);
  const [selectedModuleId, setSelectedModuleId] = useState<string | null>(null);
  const [lessonOpen, setLessonOpen] = useState(false);
  const [glossaryEntries, setGlossaryEntries] = useState<LearningGlossaryEntry[]>([]);
  const [selectedGlossaryTerm, setSelectedGlossaryTerm] = useState<string | null>(null);
  const [glossarySearch, setGlossarySearch] = useState('');
  const [selectedGlossaryCategory, setSelectedGlossaryCategory] = useState('all');
  const [completedModuleIds, setCompletedModuleIds] = useState<string[]>(() =>
    readCompletedModuleIds()
  );
  const [loadingGlossary, setLoadingGlossary] = useState(true);
  const [glossaryIssue, setGlossaryIssue] = useState<string | null>(null);
  const lessonDrawerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const nextModules = modulesByCategory[selectedCategory];
    setModules(nextModules);
    setSelectedModuleId((current) =>
      nextModules.some((module) => module.id === current) ? current : nextModules[0]?.id ?? null
    );
  }, [selectedCategory]);

  useEffect(() => {
    let isCancelled = false;

    async function loadGlossary() {
      setLoadingGlossary(true);

      try {
        const response = await fetchLearningGlossary();
        const nextEntries =
          response.entries.length > 0 ? response.entries : fallbackGlossaryEntries;

        if (!isCancelled) {
          setGlossaryEntries(nextEntries);
          setSelectedGlossaryTerm((current) =>
            nextEntries.some((entry) => entry.term === current)
              ? current
              : nextEntries[0]?.term ?? null
          );
          setGlossaryIssue(
            response.entries.length > 0 ? null : 'Showing built-in glossary entries.'
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
    () =>
      learnCategories.find((category) => category.id === selectedCategory) ?? learnCategories[0],
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
  const completionRate =
    modules.length > 0 ? Math.round((completedInCategory / modules.length) * 100) : 0;
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
        const matchesCategory =
          selectedGlossaryCategory === 'all' || entry.category === selectedGlossaryCategory;
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
    () =>
      filteredGlossaryEntries.find((entry) => entry.term === selectedGlossaryTerm) ??
      filteredGlossaryEntries[0] ??
      null,
    [filteredGlossaryEntries, selectedGlossaryTerm]
  );
  const profileLabel = hasActiveProfile ? activeProfile?.name ?? 'Connected' : 'Optional';
  const profileSourceLabel = hasActiveProfile ? activeProfileSourceLabel : 'No active profile';
  const learnIssues = [glossaryIssue].filter((issue): issue is string => Boolean(issue));

  function handleToggleComplete(moduleId: string) {
    setCompletedModuleIds((current) => {
      const next = current.includes(moduleId)
        ? current.filter((id) => id !== moduleId)
        : [...current, moduleId];
      writeCompletedModuleIds(next);
      return next;
    });
  }

  function handleOpenLesson(moduleId: string) {
    setSelectedModuleId(moduleId);
    setLessonOpen(true);
    // On mobile, scroll drawer into view after it opens
    requestAnimationFrame(() => {
      lessonDrawerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  function handleCloseLesson() {
    setLessonOpen(false);
  }

  return (
    <div className="product-desk learn-view">
      <DocumentMeta
        title={getRouteMeta('/learn').title}
        description={getRouteMeta('/learn').description}
      />

      <section className="product-desk__hero">
        <span className="product-desk__eyebrow">Learn desk</span>
        <h1>Astrology and numerology — explained.</h1>
        <p>
          Lessons, glossary, and study progress in one place. Start with a category, go deep on a
          lesson, then look up any term that needs more context.
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
              <span className="product-desk__value">{completionRate}%</span>
            </div>
          </div>
          <p className="product-desk__note">
            Explore a category after running a reading, chart pass, or compatibility check to
            understand what drove the result.
          </p>
        </article>

        <article className="product-desk__panel product-desk__panel--wide">
          <h2>Category lanes</h2>
          <p className="product-desk__note">
            Pick the learning lane that matches the desk the user just came from.
          </p>
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
              <span className="product-desk__value">{modules.length}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Completed here</span>
              <span className="product-desk__value">{completedInCategory}</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Next lesson</span>
              <span className="product-desk__value">
                {nextLesson?.title ?? 'Waiting on lessons'}
              </span>
            </div>
          </div>
          <div className="learn-view__module-grid">
            {modules.map((module) => {
              const completed = completedModuleIdSet.has(module.id);
              const isActive = module.id === selectedModuleId && lessonOpen;

              return (
                <button
                  key={module.id}
                  type="button"
                  className={
                    isActive
                      ? 'learn-view__module-card learn-view__module-card--active'
                      : 'learn-view__module-card'
                  }
                  onClick={() => handleOpenLesson(module.id)}
                >
                  <div className="learn-view__module-topline">
                    <span className="product-desk__badge">
                      {formatDifficulty(module.difficulty)}
                    </span>
                    <span>{formatDuration(module)}</span>
                  </div>
                  <strong>{module.title}</strong>
                  <p>{trimCopy(module.description, 120)}</p>
                  <div className="learn-view__module-topline learn-view__module-topline--foot">
                    <span>{module.category ?? selectedCategoryMeta.label}</span>
                    <span className="learn-view__open-cta">
                      {completed ? '✓ Completed' : 'Open lesson →'}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Inline lesson drawer — opens below the grid when a card is clicked */}
          {lessonOpen && selectedModule ? (
            <div
              ref={lessonDrawerRef}
              className="learn-view__drawer"
              role="region"
              aria-label="Lesson detail"
            >
              <div className="learn-view__drawer-header">
                <div className="learn-view__drawer-title-row">
                  <div>
                    <span className="product-desk__badge">
                      {formatDifficulty(selectedModule.difficulty)}
                    </span>
                    <h3 className="learn-view__drawer-title">{selectedModule.title}</h3>
                    <p className="learn-view__drawer-subtitle">{selectedModule.description}</p>
                  </div>
                  <button
                    type="button"
                    className="learn-view__drawer-close"
                    onClick={handleCloseLesson}
                    aria-label="Close lesson"
                  >
                    ✕
                  </button>
                </div>
                <div className="learn-view__detail-meta">
                  <span>{formatDuration(selectedModule)}</span>
                  <span>{selectedModule.category ?? selectedCategoryMeta.label}</span>
                  <span>
                    {completedModuleIdSet.has(selectedModule.id)
                      ? '✓ Completed'
                      : 'Not yet completed'}
                  </span>
                </div>
              </div>

              <div className="learn-view__drawer-body">
                <LessonBody text={selectedModule.content ?? selectedModule.description} />

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
                      {relatedModules.map((mod) => (
                        <button
                          key={mod.id}
                          type="button"
                          className="product-desk__linkcard learn-view__related-card"
                          onClick={() => handleOpenLesson(mod.id)}
                        >
                          <strong>{mod.title}</strong>
                          <span>{trimCopy(mod.description, 90)}</span>
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
                  {completedModuleIdSet.has(selectedModule.id)
                    ? 'Mark as not completed'
                    : 'Mark lesson completed'}
                </button>
              </div>
            </div>
          ) : null}
        </article>

        <article className="product-desk__panel">
          <h2>Progress</h2>
          <div className="product-desk__stats">
            <div className="product-desk__stat">
              <span className="product-desk__label">Category progress</span>
              <span className="product-desk__value">{completionRate}%</span>
            </div>
            <div className="product-desk__stat">
              <span className="product-desk__label">Completed</span>
              <span className="product-desk__value">
                {completedInCategory} / {modules.length}
              </span>
            </div>
          </div>
          <p className="product-desk__note">
            {nextLesson ? `Next up: ${nextLesson.title}` : 'All lessons in this lane completed.'}
          </p>
          {!lessonOpen ? (
            <p
              className="product-desk__note"
              style={{ color: 'rgba(136,192,208,0.8)', marginTop: '0.5rem' }}
            >
              ← Click any lesson card to open it here.
            </p>
          ) : null}
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
                <p className="product-desk__note">
                  Pick a glossary term to open its definition and usage.
                </p>
              )}
            </div>
          </div>
        </article>

        <article className="product-desk__panel">
          <h2>Suggested loop</h2>
          <div className="product-desk__linkgrid">
            <Link to="/reading" className="product-desk__linkcard">
              <strong>Generate a reading</strong>
              <span>
                Start with a live result, then open learn when a term or pattern needs context.
              </span>
            </Link>
            <Link to="/journal" className="product-desk__linkcard">
              <strong>Capture the lesson</strong>
              <span>
                Move from study into the journal workspace once the user has something to test or
                apply.
              </span>
            </Link>
            <Link to="/tools" className="product-desk__linkcard">
              <strong>Use the tools desk</strong>
              <span>
                Take sharper questions into tarot, timing, or guide flows after the concept is
                clear.
              </span>
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
