import { describe, expect, it } from 'vitest';
import { freeAIBanner, freeAIReplyNote, timeUntil } from '../utils/freeAI';

const now = new Date('2026-09-30T12:00:00Z');
const resets = '2026-09-30T17:12:00Z';

describe('free AI answer messages', () => {
  it('counts down to the reset', () => {
    expect(timeUntil(resets, now)).toBe('5 h 12 m');
    expect(timeUntil('2026-09-30T12:40:00Z', now)).toBe('40 m');
    expect(timeUntil(undefined, now)).toBe('tomorrow');
  });

  it('says what the visitor has left before asking', () => {
    expect(freeAIBanner({ status: 'available', resets_at: resets }, now)).toBe(
      '✨ You have 1 free AI answer today.'
    );
    expect(freeAIBanner({ status: 'used', resets_at: resets }, now)).toContain('5 h 12 m');
    expect(freeAIBanner({ status: 'pool_empty', resets_at: resets }, now)).toContain(
      'all been given out'
    );
    expect(freeAIBanner({ status: 'not_offered' }, now)).toBeNull();
    expect(freeAIBanner(null, now)).toBeNull();
  });

  it('labels where each reply came from', () => {
    expect(freeAIReplyNote({ status: 'answered', resets_at: resets }, now)).toContain(
      'That was your free AI answer for today'
    );
    expect(freeAIReplyNote({ status: 'used', resets_at: resets }, now)).toContain('built-in guide');
    expect(freeAIReplyNote({ status: 'unavailable', resets_at: resets }, now)).toContain(
      'still waiting'
    );
    expect(freeAIReplyNote(undefined, now)).toBeNull();
  });
});
