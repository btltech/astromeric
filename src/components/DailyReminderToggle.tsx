import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';

// Register service worker and schedule push subscription
async function registerPushSubscription(cadence: string): Promise<boolean> {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    return false;
  }
  try {
    const registration = await navigator.serviceWorker.ready;
    // Check for existing subscription
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      // In production, fetch VAPID public key from backend
      const vapidKey = import.meta.env.VITE_VAPID_PUBLIC_KEY;
      if (vapidKey) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: vapidKey,
        });
      }
    }
    if (subscription) {
      // Send subscription + cadence to backend for scheduling
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      await fetch(`${baseUrl}/reminders/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subscription: subscription.toJSON(), cadence }),
      });
      return true;
    }
  } catch (err) {
    console.error('Push subscription failed:', err);
  }
  return false;
}

async function unregisterPushSubscription(): Promise<void> {
  if (!('serviceWorker' in navigator)) return;
  try {
    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      await subscription.unsubscribe();
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001';
      await fetch(`${baseUrl}/reminders/unsubscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ endpoint: subscription.endpoint }),
      });
    }
  } catch (err) {
    console.error('Push unsubscribe failed:', err);
  }
}

export function DailyReminderToggle() {
  const { dailyReminderEnabled, reminderCadence, setDailyReminder, setReminderCadence } = useStore();
  const [status, setStatus] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  // Re-register when cadence changes while enabled
  useEffect(() => {
    if (dailyReminderEnabled) {
      registerPushSubscription(reminderCadence);
    }
  }, [dailyReminderEnabled, reminderCadence]);

  const requestPermission = async (): Promise<NotificationPermission> => {
    if (typeof Notification === 'undefined') return 'denied';
    const current = Notification.permission;
    if (current === 'granted' || current === 'denied') return current;
    return Notification.requestPermission();
  };

  const handleToggle = async () => {
    if (!dailyReminderEnabled) {
      const permission = await requestPermission();
      if (permission !== 'granted') {
        setStatus('Enable browser notifications to receive your daily vibe reminder.');
        setDailyReminder(false);
        return;
      }
      const ok = await registerPushSubscription(reminderCadence);
      if (ok) {
        setStatus(`Push scheduled — cadence: ${reminderCadence}.`);
      } else {
        setStatus('Reminder enabled (push not available in this browser).');
      }
    } else {
      await unregisterPushSubscription();
      setStatus('Daily reminder disabled.');
    }
    setDailyReminder(!dailyReminderEnabled);
  };

  const unsupported = typeof Notification === 'undefined';
  const permission = unsupported ? 'denied' : Notification.permission;

  return (
    <div className={`reminder-toggle card ${isOpen ? 'open' : 'closed'}`} aria-live="polite">
      <div className="reminder-heading">
        <div>
          <p className="eyebrow" style={{ marginBottom: 2 }}>Reminder</p>
          {isOpen && (
            <p className="text-muted compact-desc">Tiny nudge to check in. ({permission})</p>
          )}
        </div>
        <div className="reminder-actions">
          <button
            type="button"
            className={`toggle ${dailyReminderEnabled ? 'on' : 'off'}`}
            onClick={handleToggle}
            disabled={unsupported}
            aria-pressed={dailyReminderEnabled}
            aria-label={dailyReminderEnabled ? 'Disable reminder' : 'Enable reminder'}
          >
            <span className="toggle-knob" />
          </button>
          <button
            type="button"
            className="reminder-expand"
            onClick={() => setIsOpen((prev) => !prev)}
            aria-expanded={isOpen}
            aria-label={isOpen ? 'Collapse reminder settings' : 'Expand reminder settings'}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s ease' }}
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="reminder-body">
          <div className="toggle-row" style={{ marginTop: '0.2rem', display: 'flex', gap: '0.25rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <label htmlFor="reminder-cadence" className="text-muted" style={{ minWidth: 70, fontSize: '0.78rem' }}>
              Cadence
            </label>
            <select
              id="reminder-cadence"
              value={reminderCadence}
              onChange={(e) => setReminderCadence(e.target.value as typeof reminderCadence)}
              disabled={unsupported}
              aria-label="Reminder cadence"
            >
              <option value="daily">Daily</option>
              <option value="weekdays">Weekdays</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
          {unsupported && (
            <p className="text-muted status-text" style={{ marginTop: '0.25rem' }}>
              Notifications are not supported in this browser context.
            </p>
          )}
          {status && <p className="text-muted status-text" style={{ marginTop: '0.25rem' }}>{status}</p>}
        </div>
      )}
    </div>
  );
}
