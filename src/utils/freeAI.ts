import type { FreeAIStatus } from '../api/client';

/** "5 h 12 m" until the free answer resets; "a moment" when it's due. */
export function timeUntil(resetsAt?: string, now: Date = new Date()): string {
  const ms = resetsAt ? new Date(resetsAt).getTime() - now.getTime() : NaN;
  if (!Number.isFinite(ms)) return 'tomorrow';
  const minutes = Math.max(0, Math.ceil(ms / 60000));
  if (minutes < 1) return 'a moment';
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h} h ${m} m` : `${m} m`;
}

/** The line above the question box. */
export function freeAIBanner(free: FreeAIStatus | null, now?: Date): string | null {
  if (!free) return null;
  switch (free.status) {
    case 'available':
    case 'unavailable':
      return '✨ You have 1 free AI answer today.';
    case 'answered':
    case 'used':
      return `You've used today's free AI answer. Your next one is ready in ${timeUntil(
        free.resets_at,
        now
      )}.`;
    case 'pool_empty':
      return `Today's free AI answers have all been given out. Check back in ${timeUntil(
        free.resets_at,
        now
      )}.`;
    default:
      return null;
  }
}

/** The note under a reply, saying where it came from. */
export function freeAIReplyNote(free: FreeAIStatus | null | undefined, now?: Date): string | null {
  if (!free) return null;
  const wait = timeUntil(free.resets_at, now);
  switch (free.status) {
    case 'answered':
      return '✨ That was your free AI answer for today. You can keep asking; replies until tomorrow come from our built-in guide.';
    case 'used':
      return `This reply is from our built-in guide. You've used today's free AI answer; your next one is ready in ${wait}.`;
    case 'pool_empty':
      return `Today's free AI answers have all been given out, so this reply is from our built-in guide. Check back in ${wait}.`;
    case 'unavailable':
      return "The AI couldn't answer just now, so this reply is from our built-in guide. Your free AI answer is still waiting, so try again.";
    default:
      return null;
  }
}
