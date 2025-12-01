import React, { useState } from 'react';
import { drawTarotCard, type TarotCardResponse } from '../api/client';

export function TarotCard() {
  const [card, setCard] = useState<TarotCardResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [isFlipped, setIsFlipped] = useState(false);

  const handleDraw = async () => {
    setLoading(true);
    setIsFlipped(false);
    try {
      const result = await drawTarotCard();
      setCard(result);
      // Delay flip for animation effect
      setTimeout(() => setIsFlipped(true), 300);
    } catch (err) {
      console.error('Failed to draw tarot card:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCard(null);
    setIsFlipped(false);
  };

  return (
    <div className="tarot-card-component">
      <h3 className="tarot-title">🃏 Daily Tarot Draw</h3>
      <p className="tarot-subtitle">
        Draw a card for cosmic guidance and reflection
      </p>

      {!card ? (
        <div className="tarot-draw-area">
          <button 
            className="draw-button"
            onClick={handleDraw}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="shuffle-animation">🔮</span>
                Shuffling the deck...
              </>
            ) : (
              <>
                <span className="card-icon">🃏</span>
                Draw Your Card
              </>
            )}
          </button>
          
          <div className="tarot-deck">
            {[...Array(5)].map((_, i) => (
              <div 
                key={i} 
                className="deck-card"
                style={{ 
                  transform: `translateX(${i * 2}px) rotate(${(i - 2) * 3}deg)`,
                  zIndex: 5 - i
                }}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className={`tarot-reveal ${isFlipped ? 'flipped' : ''}`}>
          <div className="card-container">
            <div className="card-inner">
              {/* Card Back */}
              <div className="card-back">
                <div className="card-design">
                  <span className="mystical-symbol">☆</span>
                </div>
              </div>
              
              {/* Card Front */}
              <div className="card-front">
                <div className="card-header">
                  <h4 className="card-name">{card.card}{card.reversed ? ' (Reversed)' : ''}</h4>
                </div>
                <div className="card-body">
                  <div className="card-keywords">
                    <span className="keywords-label">Keywords</span>
                    <p>{card.keywords.join(' • ')}</p>
                  </div>
                  <div className="card-meaning">
                    <span className="meaning-label">Message</span>
                    <p>{card.message}</p>
                  </div>
                  <div className="card-advice">
                    <span className="advice-label">Advice</span>
                    <p>{card.daily_advice}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <button className="draw-again-button" onClick={handleReset}>
            <span>🔄</span> Draw Another Card
          </button>
        </div>
      )}
    </div>
  );
}
