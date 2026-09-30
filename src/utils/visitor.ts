/**
 * Identifies this browser for the one free AI answer a day.
 *
 * Browsers don't let a website read a hardware or MAC address, so the server
 * combines two things (see backend/app/free_ai.py):
 * - a random device ID made on the first visit and kept in this browser;
 * - a signature of stable browser details, which the server pairs with the
 *   network address, so clearing browser data on the same network doesn't
 *   give a second answer.
 * The server stores only keyed hashes of these, for a day.
 */

const DEVICE_KEY = 'astro_device_id';
const DB_NAME = 'astronumeric';
const STORE = 'visitor';

let deviceIdPromise: Promise<string> | null = null;
let signaturePromise: Promise<string> | null = null;

function randomId(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

function readLocal(): string | null {
  try {
    return localStorage.getItem(DEVICE_KEY);
  } catch {
    return null;
  }
}

function writeLocal(id: string) {
  try {
    localStorage.setItem(DEVICE_KEY, id);
  } catch {
    /* storage blocked: the IndexedDB copy or this session's ID still works */
  }
}

// A second copy in IndexedDB, so clearing only localStorage doesn't reset it.
function withStore<T>(mode: IDBTransactionMode, run: (store: IDBObjectStore) => IDBRequest<T>) {
  return new Promise<T | null>((resolve) => {
    try {
      const open = indexedDB.open(DB_NAME, 1);
      open.onupgradeneeded = () => open.result.createObjectStore(STORE);
      open.onerror = () => resolve(null);
      open.onsuccess = () => {
        try {
          const request = run(open.result.transaction(STORE, mode).objectStore(STORE));
          request.onsuccess = () => resolve(request.result ?? null);
          request.onerror = () => resolve(null);
        } catch {
          resolve(null);
        }
      };
    } catch {
      resolve(null);
    }
  });
}

const VALID_ID = /^[A-Za-z0-9_-]{16,128}$/;

export function getDeviceId(): Promise<string> {
  deviceIdPromise ??= (async () => {
    const local = readLocal();
    const stored = await withStore<string>('readonly', (s) => s.get(DEVICE_KEY));
    const id = [local, stored].find((v): v is string => !!v && VALID_ID.test(v)) ?? randomId();
    if (id !== local) writeLocal(id);
    if (id !== stored) await withStore('readwrite', (s) => s.put(id, DEVICE_KEY));
    return id;
  })();
  return deviceIdPromise;
}

function canvasTrace(): string {
  try {
    const canvas = document.createElement('canvas');
    canvas.width = 220;
    canvas.height = 40;
    const ctx = canvas.getContext('2d');
    if (!ctx) return '';
    ctx.textBaseline = 'top';
    ctx.font = "16px 'Arial'";
    ctx.fillStyle = '#7c3aed';
    ctx.fillRect(0, 0, 110, 20);
    ctx.fillStyle = '#10b981';
    ctx.fillText('AstroNumeric ✨ 1.0', 4, 12);
    return canvas.toDataURL();
  } catch {
    return '';
  }
}

function graphicsCard(): string {
  try {
    const gl = document.createElement('canvas').getContext('webgl');
    if (!gl) return '';
    const info = gl.getExtension('WEBGL_debug_renderer_info');
    return info
      ? `${gl.getParameter(info.UNMASKED_VENDOR_WEBGL)}|${gl.getParameter(
          info.UNMASKED_RENDERER_WEBGL
        )}`
      : `${gl.getParameter(gl.VENDOR)}|${gl.getParameter(gl.RENDERER)}`;
  } catch {
    return '';
  }
}

async function sha256(text: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, '0')).join('');
}

export function getBrowserSignature(): Promise<string> {
  signaturePromise ??= (async () => {
    const nav = navigator as Navigator & { deviceMemory?: number };
    const traits = [
      nav.userAgent,
      nav.language,
      (nav.languages ?? []).join(','),
      Intl.DateTimeFormat().resolvedOptions().timeZone,
      `${screen.width}x${screen.height}x${screen.colorDepth}`,
      String(window.devicePixelRatio),
      String(nav.hardwareConcurrency ?? ''),
      String(nav.deviceMemory ?? ''),
      String(nav.maxTouchPoints ?? ''),
      graphicsCard(),
      canvasTrace(),
    ];
    try {
      return await sha256(traits.join('\n'));
    } catch {
      return '';
    }
  })();
  return signaturePromise;
}

/** Headers the server needs to hand out (and limit) the free AI answer. */
export async function visitorHeaders(): Promise<Record<string, string>> {
  const [deviceId, signature] = await Promise.all([getDeviceId(), getBrowserSignature()]);
  const headers: Record<string, string> = { 'X-Device-Id': deviceId };
  if (signature) headers['X-Device-Signature'] = signature;
  return headers;
}
