import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface TooltipPosition {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
  transformOrigin: string;
}

interface GlossaryTooltipProps {
  term: string;
  definition: string;
  category?: 'astrology' | 'numerology' | 'general';
  children?: React.ReactNode;
}

export function GlossaryTooltip({
  term,
  definition,
  category = 'general',
  children,
}: GlossaryTooltipProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [position, setPosition] = useState<TooltipPosition>({ transformOrigin: 'bottom center' });
  const triggerRef = useRef<HTMLButtonElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const calculatePosition = useCallback(() => {
    if (!triggerRef.current) return;

    const rect = triggerRef.current.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    // Determine vertical position
    const spaceBelow = viewportHeight - rect.bottom;
    const spaceAbove = rect.top;
    const tooltipHeight = 150; // Approximate

    // Determine horizontal position
    const tooltipWidth = 280;
    const spaceRight = viewportWidth - rect.left;
    const spaceLeft = rect.right;

    const newPosition: TooltipPosition = { transformOrigin: 'bottom center' };

    // Prefer below, fallback to above
    if (spaceBelow >= tooltipHeight || spaceBelow > spaceAbove) {
      newPosition.top = rect.bottom + 8;
      newPosition.transformOrigin = 'top center';
    } else {
      newPosition.bottom = viewportHeight - rect.top + 8;
      newPosition.transformOrigin = 'bottom center';
    }

    // Horizontal centering with bounds
    const centerX = rect.left + rect.width / 2;
    if (centerX - tooltipWidth / 2 < 16) {
      newPosition.left = 16;
    } else if (centerX + tooltipWidth / 2 > viewportWidth - 16) {
      newPosition.right = 16;
    } else {
      newPosition.left = centerX - tooltipWidth / 2;
    }

    setPosition(newPosition);
  }, []);

  useEffect(() => {
    if (isOpen) {
      calculatePosition();
      window.addEventListener('resize', calculatePosition);
      return () => window.removeEventListener('resize', calculatePosition);
    }
  }, [isOpen, calculatePosition]);

  // Close on click outside
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node) &&
        tooltipRef.current &&
        !tooltipRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(`${term}: ${definition}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const categoryIcons: Record<string, string> = {
    astrology: '⭐',
    numerology: '🔢',
    general: '📖',
  };

  return (
    <>
      <button
        ref={triggerRef}
        className="glossary-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-describedby={isOpen ? `tooltip-${term}` : undefined}
      >
        {children || term}
        <span className="glossary-indicator">ⓘ</span>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={tooltipRef}
            id={`tooltip-${term}`}
            className={`glossary-tooltip glossary-tooltip--${category}`}
            style={{
              position: 'fixed',
              ...position,
            }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.15 }}
            role="tooltip"
          >
            <div className="tooltip-header">
              <span className="tooltip-icon">{categoryIcons[category]}</span>
              <span className="tooltip-term">{term}</span>
              <button className="tooltip-copy" onClick={handleCopy} aria-label="Copy definition">
                {copied ? '✓' : '📋'}
              </button>
              <button className="tooltip-close" onClick={() => setIsOpen(false)} aria-label="Close">
                ×
              </button>
            </div>
            <p className="tooltip-definition">{definition}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// Hook to auto-detect and wrap glossary terms in text
export function useGlossaryTerms(
  text: string,
  glossary: Record<
    string,
    { definition: string; category?: 'astrology' | 'numerology' | 'general' }
  >
): React.ReactNode {
  if (!glossary || Object.keys(glossary).length === 0) {
    return text;
  }

  const terms = Object.keys(glossary).sort((a, b) => b.length - a.length);
  const pattern = new RegExp(
    `\\b(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`,
    'gi'
  );

  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = pattern.exec(text)) !== null) {
    // Add text before match
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    // Add tooltip for matched term
    const matchedTerm = match[1];
    const termData = glossary[matchedTerm] || glossary[matchedTerm.toLowerCase()];
    if (termData) {
      parts.push(
        <GlossaryTooltip
          key={`${matchedTerm}-${match.index}`}
          term={matchedTerm}
          definition={termData.definition}
          category={termData.category}
        />
      );
    } else {
      parts.push(matchedTerm);
    }

    lastIndex = pattern.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}
