import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTranslation } from 'react-i18next';

interface MobileActionBarProps {
  actions: Array<{
    id: string;
    icon: string;
    label: string;
    onClick: () => void;
    primary?: boolean;
    disabled?: boolean;
  }>;
  visible?: boolean;
}

export function MobileActionBar({ actions, visible = true }: MobileActionBarProps) {
  const { t } = useTranslation();

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="mobile-action-bar"
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 400, damping: 30 }}
        >
          <div className="action-bar-inner">
            {actions.map((action) => (
              <button
                key={action.id}
                className={`action-bar-btn ${action.primary ? 'action-bar-btn--primary' : ''}`}
                onClick={action.onClick}
                disabled={action.disabled}
                aria-label={action.label}
              >
                <span className="action-icon">{action.icon}</span>
                <span className="action-label">{action.label}</span>
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Hook to detect if mobile and scrolled past threshold
export function useMobileActionBar(scrollThreshold = 200): boolean {
  const [showBar, setShowBar] = React.useState(false);
  const [isMobile, setIsMobile] = React.useState(false);

  React.useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    const handleScroll = () => {
      setShowBar(window.scrollY > scrollThreshold);
    };

    checkMobile();
    handleScroll();

    window.addEventListener('resize', checkMobile);
    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      window.removeEventListener('resize', checkMobile);
      window.removeEventListener('scroll', handleScroll);
    };
  }, [scrollThreshold]);

  return isMobile && showBar;
}
