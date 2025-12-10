import React, { useState, useEffect } from 'react';
import { 
  fetchLearningModules, 
  fetchLearningModule, 
  fetchCourse, 
  fetchLesson,
  type LearningModule 
} from '../api/client';

interface CourseLesson {
  title: string;
  content: string[];
  exercise?: string;
  key_takeaway: string;
}

interface Course {
  title: string;
  description: string;
  lessons: Record<string, CourseLesson>;
}

type ViewState = 
  | { type: 'modules' }
  | { type: 'module'; moduleId: string; data: Record<string, unknown> }
  | { type: 'course'; courseId: string; data: Course }
  | { type: 'lesson'; courseId: string; lessonNumber: number; data: CourseLesson };

export function LearningCenter() {
  const [modules, setModules] = useState<LearningModule[]>([]);
  const [view, setView] = useState<ViewState>({ type: 'modules' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadModules() {
      try {
        const response = await fetchLearningModules();
        setModules(response.modules);
      } catch (err) {
        console.error('Failed to load modules:', err);
        setError('Could not load learning content');
      } finally {
        setLoading(false);
      }
    }
    loadModules();
  }, []);

  const openModule = async (moduleId: string) => {
    setLoading(true);
    try {
      const data = await fetchLearningModule(moduleId);
      setView({ type: 'module', moduleId, data });
    } catch (err) {
      console.error('Failed to load module:', err);
    } finally {
      setLoading(false);
    }
  };

  const openCourse = async (courseId: string) => {
    setLoading(true);
    try {
      const data = await fetchCourse(courseId) as unknown as Course;
      setView({ type: 'course', courseId, data });
    } catch (err) {
      console.error('Failed to load course:', err);
    } finally {
      setLoading(false);
    }
  };

  const openLesson = async (courseId: string, lessonNumber: number) => {
    setLoading(true);
    try {
      const data = await fetchLesson(courseId, lessonNumber) as unknown as CourseLesson;
      setView({ type: 'lesson', courseId, lessonNumber, data });
    } catch (err) {
      console.error('Failed to load lesson:', err);
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    if (view.type === 'lesson') {
      openCourse(view.courseId);
    } else {
      setView({ type: 'modules' });
    }
  };

  if (loading && view.type === 'modules') {
    return (
      <div className="learning-center loading">
        <div className="loading-spinner">📚</div>
        <p>Loading cosmic knowledge...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="learning-center error">
        <p>{error}</p>
      </div>
    );
  }

  // Render modules list
  if (view.type === 'modules') {
    return (
      <div className="learning-center">
        <h2 className="learning-title">📚 Cosmic Learning Center</h2>
        <p className="learning-subtitle">
          Expand your astrological wisdom with our in-depth guides and courses
        </p>

        <div className="modules-grid">
          {modules.map((module) => (
            <div 
              key={module.id} 
              className="module-card"
              onClick={() => {
                if (module.id === 'courses') {
                  openCourse('astrology_basics');
                } else {
                  openModule(module.id);
                }
              }}
            >
              <div className="module-icon">
                {module.id === 'moon_signs' && '🌙'}
                {module.id === 'rising_signs' && '⬆️'}
                {module.id === 'elements' && '🔥'}
                {module.id === 'retrogrades' && '⏪'}
                {module.id === 'courses' && '🎓'}
              </div>
              <h3 className="module-title">{module.title}</h3>
              <p className="module-description">{module.description}</p>
              <span className="module-count">{module.item_count} topics</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Render module content
  if (view.type === 'module') {
    const isSignModule = view.moduleId === 'moon_signs' || view.moduleId === 'rising_signs';
    const entries = Object.entries(view.data);

    return (
      <div className="learning-center module-view">
        <button className="back-button" onClick={goBack}>
          ← Back to Modules
        </button>

        <h2 className="module-header">
          {view.moduleId === 'moon_signs' && '🌙 Moon Signs'}
          {view.moduleId === 'rising_signs' && '⬆️ Rising Signs'}
          {view.moduleId === 'elements' && '🔥 Elements & Modalities'}
          {view.moduleId === 'retrogrades' && '⏪ Planetary Retrogrades'}
        </h2>

        <div className={`content-grid ${isSignModule ? 'signs-grid' : ''}`}>
          {entries.map(([key, value]) => {
            const item = value as Record<string, unknown>;
            return (
              <div key={key} className="content-card">
                <h3 className="content-title">
                  {(item.symbol as string) || ''} {key}
                </h3>
                
                {item.title && <h4 className="content-subtitle">{item.title as string}</h4>}
                
                {item.emotional_nature && (
                  <div className="content-section">
                    <span className="section-label">Emotional Nature</span>
                    <p>{item.emotional_nature as string}</p>
                  </div>
                )}

                {item.needs && (
                  <div className="content-section">
                    <span className="section-label">Core Needs</span>
                    <p>{item.needs as string}</p>
                  </div>
                )}

                {item.first_impression && (
                  <div className="content-section">
                    <span className="section-label">First Impression</span>
                    <p>{item.first_impression as string}</p>
                  </div>
                )}

                {item.appearance_vibe && (
                  <div className="content-section">
                    <span className="section-label">Appearance & Vibe</span>
                    <p>{item.appearance_vibe as string}</p>
                  </div>
                )}

                {item.effects && (
                  <div className="content-section">
                    <span className="section-label">Effects</span>
                    <p>{item.effects as string}</p>
                  </div>
                )}

                {item.duration && (
                  <div className="content-section">
                    <span className="section-label">Duration</span>
                    <p>{item.duration as string}</p>
                  </div>
                )}

                {item.tips && Array.isArray(item.tips) && (
                  <div className="content-section tips">
                    <span className="section-label">Tips</span>
                    <ul>
                      {(item.tips as string[]).map((tip, i) => (
                        <li key={i}>{tip}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Render course overview
  if (view.type === 'course') {
    const lessonKeys = Object.keys(view.data.lessons || {});

    return (
      <div className="learning-center course-view">
        <button className="back-button" onClick={goBack}>
          ← Back to Modules
        </button>

        <div className="course-header">
          <span className="course-icon">🎓</span>
          <h2 className="course-title">{view.data.title}</h2>
          <p className="course-description">{view.data.description}</p>
        </div>

        <div className="lessons-list">
          {lessonKeys.map((key, index) => {
            const lesson = view.data.lessons[key];
            return (
              <div 
                key={key} 
                className="lesson-item"
                onClick={() => openLesson(view.courseId, index + 1)}
              >
                <span className="lesson-number">{index + 1}</span>
                <div className="lesson-info">
                  <h4 className="lesson-title">{lesson.title}</h4>
                  <p className="lesson-preview">
                    {lesson.content[0]?.substring(0, 80)}...
                  </p>
                </div>
                <span className="lesson-arrow">→</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Render lesson content
  if (view.type === 'lesson') {
    return (
      <div className="learning-center lesson-view">
        <button className="back-button" onClick={goBack}>
          ← Back to Course
        </button>

        <div className="lesson-header">
          <span className="lesson-badge">Lesson {view.lessonNumber}</span>
          <h2 className="lesson-title">{view.data.title}</h2>
        </div>

        <div className="lesson-content">
          {view.data.content.map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
        </div>

        {view.data.exercise && (
          <div className="lesson-exercise">
            <span className="exercise-label">✏️ Practice Exercise</span>
            <p>{view.data.exercise}</p>
          </div>
        )}

        <div className="lesson-takeaway">
          <span className="takeaway-label">💡 Key Takeaway</span>
          <p>{view.data.key_takeaway}</p>
        </div>

        <div className="lesson-navigation">
          {view.lessonNumber > 1 && (
            <button 
              className="prev-lesson"
              onClick={() => openLesson(view.courseId, view.lessonNumber - 1)}
            >
              ← Previous Lesson
            </button>
          )}
          <button 
            className="next-lesson"
            onClick={() => openLesson(view.courseId, view.lessonNumber + 1)}
          >
            Next Lesson →
          </button>
        </div>
      </div>
    );
  }

  return null;
}
