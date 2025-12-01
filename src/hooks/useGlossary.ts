/**
 * Custom hook for glossary/learning content with pagination
 */
import { useCallback, useState } from 'react';
import { useStore } from '../store/useStore';
import { apiFetch } from '../api/client';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export function useGlossary() {
  const { glossary, setGlossary, setLoading } = useStore();
  const [zodiacPage, setZodiacPage] = useState(0);
  const [numerologyPage, setNumerologyPage] = useState(0);
  const [hasMoreZodiac, setHasMoreZodiac] = useState(true);
  const [hasMoreNumerology, setHasMoreNumerology] = useState(true);

  const PAGE_SIZE = 6;

  const fetchGlossary = useCallback(async () => {
    if (glossary) return glossary;

    setLoading(true);
    try {
      // Try paginated endpoints first, fallback to legacy
      let zodiacData: Record<string, unknown> = {};
      let numerologyData: Record<string, unknown> = {};

      try {
        const zodiacRes = await apiFetch<PaginatedResponse<{ key: string; data: unknown }>>(
          `/learn/zodiac?limit=${PAGE_SIZE}&offset=0`
        );
        zodiacData = zodiacRes.items.reduce((acc, item) => ({ ...acc, [item.key]: item.data }), {});
        setHasMoreZodiac(zodiacRes.has_more);
      } catch {
        // Fallback to legacy endpoint
        zodiacData = await apiFetch<Record<string, unknown>>('/learn/zodiac');
        setHasMoreZodiac(false);
      }

      try {
        const numRes = await apiFetch<PaginatedResponse<{ key: string; data: unknown }>>(
          `/learn/numerology?limit=${PAGE_SIZE}&offset=0`
        );
        numerologyData = numRes.items.reduce(
          (acc, item) => ({ ...acc, [item.key]: item.data }),
          {}
        );
        setHasMoreNumerology(numRes.has_more);
      } catch {
        // Fallback to legacy endpoint
        numerologyData = await apiFetch<Record<string, unknown>>('/learn/numerology');
        setHasMoreNumerology(false);
      }

      const newGlossary = { zodiac: zodiacData, numerology: numerologyData };
      setGlossary(newGlossary);
      return newGlossary;
    } catch (err) {
      console.error('Failed to fetch glossary:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [glossary, setGlossary, setLoading]);

  const loadMoreZodiac = useCallback(async () => {
    if (!hasMoreZodiac) return;

    const newOffset = (zodiacPage + 1) * PAGE_SIZE;
    try {
      const res = await apiFetch<PaginatedResponse<{ key: string; data: unknown }>>(
        `/learn/zodiac?limit=${PAGE_SIZE}&offset=${newOffset}`
      );
      const newItems = res.items.reduce((acc, item) => ({ ...acc, [item.key]: item.data }), {});

      setGlossary({
        zodiac: { ...glossary?.zodiac, ...newItems },
        numerology: glossary?.numerology || {},
      });
      setZodiacPage((p) => p + 1);
      setHasMoreZodiac(res.has_more);
    } catch {
      setHasMoreZodiac(false);
    }
  }, [glossary, zodiacPage, hasMoreZodiac, setGlossary]);

  const loadMoreNumerology = useCallback(async () => {
    if (!hasMoreNumerology) return;

    const newOffset = (numerologyPage + 1) * PAGE_SIZE;
    try {
      const res = await apiFetch<PaginatedResponse<{ key: string; data: unknown }>>(
        `/learn/numerology?limit=${PAGE_SIZE}&offset=${newOffset}`
      );
      const newItems = res.items.reduce((acc, item) => ({ ...acc, [item.key]: item.data }), {});

      setGlossary({
        zodiac: glossary?.zodiac || {},
        numerology: { ...glossary?.numerology, ...newItems },
      });
      setNumerologyPage((p) => p + 1);
      setHasMoreNumerology(res.has_more);
    } catch {
      setHasMoreNumerology(false);
    }
  }, [glossary, numerologyPage, hasMoreNumerology, setGlossary]);

  return {
    glossary,
    fetchGlossary,
    loadMoreZodiac,
    loadMoreNumerology,
    hasMoreZodiac,
    hasMoreNumerology,
  };
}
