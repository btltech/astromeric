import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastProps {
  toast: ToastItem;
  onDismiss: (id: string) => void;
}

const ICONS: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  info: 'ℹ',
  warning: '⚠',
};

const Toast: React.FC<ToastProps> = ({ toast, onDismiss }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id);
    }, toast.duration || 4000);
    return () => clearTimeout(timer);
  }, [toast, onDismiss]);

  return (
    <motion.div
      className={`toast toast-${toast.type}`}
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.9 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      role="alert"
      aria-live="polite"
    >
      <span className="toast-icon">{ICONS[toast.type]}</span>
      <span className="toast-message">{toast.message}</span>
      <button
        className="toast-close"
        onClick={() => onDismiss(toast.id)}
        aria-label="Dismiss notification"
      >
        ✕
      </button>
    </motion.div>
  );
};

// Toast container that renders all active toasts
export const ToastContainer: React.FC<{
  toasts: ToastItem[];
  onDismiss: (id: string) => void;
}> = ({ toasts, onDismiss }) => {
  return (
    <div className="toast-container" aria-label="Notifications">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onDismiss={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  );
};

// Hook for managing toasts
let toastId = 0;

type ToastStore = {
  toasts: ToastItem[];
  listeners: Set<() => void>;
};

const store: ToastStore = {
  toasts: [],
  listeners: new Set(),
};

function notify() {
  store.listeners.forEach((listener) => listener());
}

export function toast(message: string, type: ToastType = 'info', duration?: number) {
  const id = `toast-${++toastId}`;
  store.toasts = [...store.toasts, { id, message, type, duration }];
  notify();
  return id;
}

toast.success = (message: string, duration?: number) => toast(message, 'success', duration);
toast.error = (message: string, duration?: number) => toast(message, 'error', duration);
toast.info = (message: string, duration?: number) => toast(message, 'info', duration);
toast.warning = (message: string, duration?: number) => toast(message, 'warning', duration);

export function useToasts() {
  const [toasts, setToasts] = useState<ToastItem[]>(store.toasts);

  useEffect(() => {
    const listener = () => setToasts([...store.toasts]);
    store.listeners.add(listener);
    return () => {
      store.listeners.delete(listener);
    };
  }, []);

  const dismiss = useCallback((id: string) => {
    store.toasts = store.toasts.filter((t) => t.id !== id);
    notify();
  }, []);

  return { toasts, dismiss };
}

export default Toast;
