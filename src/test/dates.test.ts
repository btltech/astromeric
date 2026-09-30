import { describe, expect, it } from 'vitest';

import { parseCalendarDate } from '../utils/dates';

describe('parseCalendarDate', () => {
  it('reads a plain date as that calendar day, in any timezone', () => {
    const d = parseCalendarDate('2026-09-30');
    expect([d.getFullYear(), d.getMonth() + 1, d.getDate()]).toEqual([2026, 9, 30]);
  });

  it('keeps the first of the month in its own month', () => {
    // 1 Oct read as UTC midnight is still September west of Greenwich.
    const d = parseCalendarDate('2026-10-01');
    expect([d.getMonth() + 1, d.getDate()]).toEqual([10, 1]);
  });

  it('leaves timestamps and other values to the normal parser', () => {
    const stamp = '2026-09-30T06:44:25Z';
    expect(parseCalendarDate(stamp).getTime()).toBe(new Date(stamp).getTime());
    expect(parseCalendarDate(0).getTime()).toBe(0);
  });
});
