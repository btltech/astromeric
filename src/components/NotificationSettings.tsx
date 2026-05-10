import React, { useEffect, useState } from 'react';
import {
  fetchVapidKey,
  getAlertPreferences,
  subscribePush,
  testPushNotification,
  updateAlertPreferences,
} from '../api/client';
import './NotificationSettings.css';

type PermissionState = 'default' | 'granted' | 'denied';
type SubState = 'idle' | 'subscribing' | 'subscribed' | 'error';

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

const FREQ_OPTIONS = [
  { value: 'every_retrograde', label: 'Every retrograde & major transit' },
  { value: 'weekly_digest', label: 'Weekly digest only' },
  { value: 'once_per_year', label: 'Once per year (major events only)' },
  { value: 'none', label: 'No alerts' },
];

export function NotificationSettings({ token }: { token?: string | null }) {
  const supported = 'serviceWorker' in navigator && 'PushManager' in window;
  const [permission, setPermission] = useState<PermissionState>(
    supported ? (Notification.permission as PermissionState) : 'denied',
  );
  const [subState, setSubState] = useState<SubState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [testSent, setTestSent] = useState(false);
  const [prefs, setPrefs] = useState<{
    alert_mercury_retrograde: boolean;
    alert_frequency: string;
  } | null>(null);
  const [savingPrefs, setSavingPrefs] = useState(false);

  // Load preferences if logged in
  useEffect(() => {
    if (!token) return;
    getAlertPreferences()
      .then((p) => setPrefs(p))
      .catch(() => {/* ignore */});
  }, [token]);

  async function handleSubscribe() {
    setError(null);
    setSubState('subscribing');
    try {
      const vapidKey = await fetchVapidKey();
      const reg = await navigator.serviceWorker.ready;
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidKey),
      });
      await subscribePush(sub.toJSON() as PushSubscriptionJSON);
      setSubState('subscribed');
      setPermission('granted');
    } catch (err) {
      setSubState('error');
      setError(err instanceof Error ? err.message : 'Subscription failed');
    }
  }

  async function handleRequestPermission() {
    const result = await Notification.requestPermission();
    setPermission(result as PermissionState);
    if (result === 'granted') {
      await handleSubscribe();
    }
  }

  async function handleTest() {
    setTestSent(false);
    setError(null);
    try {
      await testPushNotification();
      setTestSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Test failed');
    }
  }

  async function handleSavePrefs() {
    if (!prefs) return;
    setSavingPrefs(true);
    try {
      await updateAlertPreferences(prefs);
    } catch {
      setError('Failed to save preferences');
    } finally {
      setSavingPrefs(false);
    }
  }

  if (!supported) {
    return (
      <div className="notif-settings notif-settings--unsupported">
        <p>Push notifications are not supported in this browser.</p>
      </div>
    );
  }

  return (
    <div className="notif-settings">
      <h3 className="notif-settings__title">🔔 Cosmic Alerts</h3>
      <p className="notif-settings__desc">
        Get notified about Mercury retrograde, major eclipses, and important planetary transits.
      </p>

      {permission === 'denied' && (
        <div className="notif-settings__blocked">
          Notifications are blocked in your browser. To enable them, update your
          browser's site settings and reload.
        </div>
      )}

      {permission === 'default' && (
        <button className="btn btn-primary" onClick={handleRequestPermission} disabled={subState === 'subscribing'}>
          {subState === 'subscribing' ? 'Subscribing…' : 'Enable Notifications'}
        </button>
      )}

      {permission === 'granted' && subState !== 'subscribed' && (
        <button className="btn btn-primary" onClick={handleSubscribe} disabled={subState === 'subscribing'}>
          {subState === 'subscribing' ? 'Subscribing…' : 'Activate Alerts'}
        </button>
      )}

      {(permission === 'granted' && subState === 'subscribed') && (
        <div className="notif-settings__active">
          <span className="notif-settings__badge">✓ Alerts active</span>
          <button
            className="btn btn-secondary notif-settings__test-btn"
            onClick={handleTest}
          >
            Send test notification
          </button>
          {testSent && <p className="notif-settings__test-ok">Test sent! Check your notifications.</p>}
        </div>
      )}

      {error && <p className="notif-settings__error">{error}</p>}

      {/* Preferences — only shown when logged in */}
      {token && prefs && (
        <div className="notif-settings__prefs">
          <h4 className="notif-settings__prefs-title">Alert preferences</h4>

          <label className="notif-settings__check">
            <input
              type="checkbox"
              checked={prefs.alert_mercury_retrograde}
              onChange={(e) =>
                setPrefs({ ...prefs, alert_mercury_retrograde: e.target.checked })
              }
            />
            Mercury retrograde alerts
          </label>

          <div className="notif-settings__freq">
            <label htmlFor="alert-freq">Frequency</label>
            <select
              id="alert-freq"
              value={prefs.alert_frequency}
              onChange={(e) => setPrefs({ ...prefs, alert_frequency: e.target.value })}
            >
              {FREQ_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>

          <button
            className="btn btn-secondary"
            onClick={handleSavePrefs}
            disabled={savingPrefs}
          >
            {savingPrefs ? 'Saving…' : 'Save preferences'}
          </button>
        </div>
      )}
    </div>
  );
}
