/**
 * `new Date('2026-09-30')` is midnight UTC, which is still the 29th anywhere
 * west of Greenwich. Dates from the server and birth dates are calendar days,
 * so a plain YYYY-MM-DD is read as local midnight instead. Anything else
 * (timestamps, numbers, Dates) is left to the normal parser.
 */
export function parseCalendarDate(value: string | number | Date): Date {
  if (typeof value === 'string') {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
    if (match) return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
  }
  return new Date(value);
}
