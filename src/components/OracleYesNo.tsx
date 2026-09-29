import React, { useState } from 'react';
import { askOracle, type YesNoResponse } from '../api/client';

export function OracleYesNo() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<YesNoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await askOracle(question);
      setResult(response);
    } catch (err) {
      console.error('Oracle failed:', err);
      setError('The cosmic connection was disrupted. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setQuestion('');
    setError(null);
  };

  const getAnswerEmoji = (answer: string) => {
    switch (answer) {
      case 'Yes':
        return '✅';
      case 'No':
        return '❌';
      case 'Maybe':
        return '🤔';
      case 'Wait':
        return '⏳';
      default:
        return '🔮';
    }
  };

  const getAnswerColor = (answer: string) => {
    switch (answer) {
      case 'Yes':
        return '#4ade80';
      case 'No':
        return '#f87171';
      case 'Maybe':
        return '#facc15';
      case 'Wait':
        return '#a78bfa';
      default:
        return '#a78bfa';
    }
  };

  return (
    <div className="oracle-yes-no">
      <h3 className="oracle-title">🔮 Cosmic Decision Oracle</h3>
      <p className="oracle-subtitle">Ask a yes/no question and receive cosmic guidance</p>

      {!result ? (
        <form onSubmit={handleAsk} className="oracle-form">
          <div className="question-input-wrapper">
            <input
              type="text"
              className="question-input"
              placeholder="Should I..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
              maxLength={200}
            />
            <span className="input-glow" />
          </div>

          <button type="submit" className="ask-button" disabled={loading || !question.trim()}>
            {loading ? (
              <>
                <span className="crystal-animation">🔮</span>
                Consulting the cosmos...
              </>
            ) : (
              <>
                <span>✨</span> Ask the Oracle
              </>
            )}
          </button>

          {error && <p className="oracle-error">{error}</p>}

          <div className="oracle-tips">
            <p>💡 Tips for best results:</p>
            <ul>
              <li>Ask specific yes/no questions</li>
              <li>Focus on decisions you can control</li>
              <li>Trust your intuition alongside the answer</li>
            </ul>
          </div>
        </form>
      ) : (
        <div className="oracle-result">
          <div className="question-asked">
            <span className="label">You asked:</span>
            <p>&quot;{result.question}&quot;</p>
          </div>

          <div
            className="answer-reveal"
            style={{ '--answer-color': getAnswerColor(result.answer) } as React.CSSProperties}
          >
            <span className="answer-emoji">{result.emoji || getAnswerEmoji(result.answer)}</span>
            <span className="answer-text">{result.answer}</span>
            <div className="confidence-meter">
              <span className="confidence-label">Cosmic Confidence</span>
              <div className="confidence-bar">
                <div className="confidence-fill" style={{ width: `${result.confidence}%` }} />
              </div>
              <span className="confidence-value">{result.confidence}%</span>
            </div>
          </div>

          <div className="cosmic-reasoning">
            <span className="section-label">🌌 Cosmic Message</span>
            <p>{result.message}</p>
          </div>

          <div className="oracle-advice">
            <span className="section-label">💫 Reasoning</span>
            <p>{result.reasoning}</p>
          </div>

          {result.timing && (
            <div className="oracle-timing">
              <span className="section-label">⏰ Timing</span>
              <p>{result.timing}</p>
            </div>
          )}

          <button onClick={handleReset} className="reset-button">
            Ask Another Question
          </button>
        </div>
      )}
    </div>
  );
}
