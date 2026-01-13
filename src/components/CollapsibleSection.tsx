import React, { useState, useId } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface CollapsibleSectionProps {
  title: string;
  icon?: string;
  defaultExpanded?: boolean;
  badge?: string | number;
  progress?: number; // 0-100
  children: React.ReactNode;
}

export function CollapsibleSection({
  title,
  icon,
  defaultExpanded = false,
  badge,
  progress,
  children,
}: CollapsibleSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const contentId = useId();

  return (
    <div className={`collapsible-section ${isExpanded ? 'expanded' : ''}`}>
      <button
        className="collapsible-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-controls={contentId}
      >
        <div className="collapsible-title">
          {icon && <span className="collapsible-icon">{icon}</span>}
          <span className="collapsible-text">{title}</span>
          {badge !== undefined && <span className="collapsible-badge">{badge}</span>}
        </div>

        {progress !== undefined && (
          <div className="collapsible-progress">
            <div
              className="collapsible-progress-bar"
              style={{ width: `${progress}%` }}
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
        )}

        <span className={`collapsible-chevron ${isExpanded ? 'rotated' : ''}`}>▾</span>
      </button>

      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            id={contentId}
            className="collapsible-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="collapsible-inner">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Accordion component - only one section open at a time
interface AccordionProps {
  children: React.ReactNode;
  allowMultiple?: boolean;
}

interface AccordionItemProps extends Omit<CollapsibleSectionProps, 'defaultExpanded'> {
  id: string;
}

export function Accordion({ children, allowMultiple = false }: AccordionProps) {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set());

  const toggleSection = (id: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        if (!allowMultiple) {
          next.clear();
        }
        next.add(id);
      }
      return next;
    });
  };

  // Clone children with controlled state
  return (
    <div className="accordion">
      {React.Children.map(children, (child) => {
        if (React.isValidElement<AccordionItemProps>(child)) {
          return React.cloneElement(child, {
            // @ts-expect-error - we're passing controlled props
            isExpanded: openSections.has(child.props.id),
            onToggle: () => toggleSection(child.props.id),
          });
        }
        return child;
      })}
    </div>
  );
}

export function AccordionItem({
  id: _id,
  title,
  icon,
  badge,
  progress,
  children,
  isExpanded,
  onToggle,
}: AccordionItemProps & { isExpanded?: boolean; onToggle?: () => void }) {
  const contentId = useId();
  const expanded = isExpanded ?? false;

  return (
    <div className={`collapsible-section ${expanded ? 'expanded' : ''}`}>
      <button
        className="collapsible-header"
        onClick={onToggle}
        aria-expanded={expanded}
        aria-controls={contentId}
      >
        <div className="collapsible-title">
          {icon && <span className="collapsible-icon">{icon}</span>}
          <span className="collapsible-text">{title}</span>
          {badge !== undefined && <span className="collapsible-badge">{badge}</span>}
        </div>

        {progress !== undefined && (
          <div className="collapsible-progress">
            <div className="collapsible-progress-bar" style={{ width: `${progress}%` }} />
          </div>
        )}

        <span className={`collapsible-chevron ${expanded ? 'rotated' : ''}`}>▾</span>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            id={contentId}
            className="collapsible-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="collapsible-inner">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
