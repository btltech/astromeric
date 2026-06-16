/**
 * LocationAutocomplete.tsx
 * City search with autocomplete using Nominatim (free OpenStreetMap geocoding)
 */
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getApiBaseUrl } from '../api/config';

interface LocationResult {
  display_name: string;
  lat: string;
  lon: string;
  address?: {
    city?: string;
    town?: string;
    village?: string;
    state?: string;
    country?: string;
  };
}

interface SelectedLocation {
  name: string;
  latitude: number;
  longitude: number;
  timezone: string;
}

interface Props {
  onSelect: (location: SelectedLocation) => void;
  placeholder?: string;
  initialValue?: string;
  onQueryChange?: (query: string) => void;
}

// Debounce hook
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

export function LocationAutocomplete({
  onSelect,
  placeholder = 'Search city...',
  initialValue = '',
  onQueryChange,
}: Props) {
  const [query, setQuery] = useState(initialValue);
  const [results, setResults] = useState<LocationResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Manual fallback states
  const [isManual, setIsManual] = useState(false);
  const [manualLat, setManualLat] = useState('');
  const [manualLon, setManualLon] = useState('');
  const [manualTimezone, setManualTimezone] = useState('UTC');
  const [manualError, setManualError] = useState<string | null>(null);

  const debouncedQuery = useDebounce(query, 300);

  const COMMON_TIMEZONES = [
    'UTC',
    'Africa/Lagos',
    'Africa/Cairo',
    'Africa/Johannesburg',
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'America/Sao_Paulo',
    'Asia/Kolkata',
    'Asia/Tokyo',
    'Asia/Singapore',
    'Asia/Dubai',
    'Europe/London',
    'Europe/Paris',
    'Europe/Berlin',
    'Europe/Moscow',
    'Pacific/Auckland',
  ];

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch locations from Nominatim
  useEffect(() => {
    if (isManual || debouncedQuery.length < 2) {
      setResults([]);
      return;
    }

    const fetchLocations = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?` +
            new URLSearchParams({
              q: debouncedQuery,
              format: 'json',
              addressdetails: '1',
              limit: '5',
              'accept-language': 'en',
            }),
          {
            headers: {
              'User-Agent': 'AstroNumerology/1.0',
            },
          }
        );

        if (!response.ok) throw new Error('Search failed');

        const data: LocationResult[] = await response.json();
        setResults(data);
        setIsOpen(data.length > 0);
      } catch (err) {
        setError('Failed to search locations');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLocations();
  }, [debouncedQuery, isManual]);

  // Get timezone from coordinates using backend
  const getTimezone = useCallback(async (lat: number, lon: number): Promise<string> => {
    try {
      const baseUrl = getApiBaseUrl();
      const response = await fetch(`${baseUrl}/geocode/timezone?lat=${lat}&lon=${lon}`);
      if (response.ok) {
        const data = await response.json();
        return data.timezone || 'UTC';
      }
    } catch {
      // Fallback: estimate timezone from longitude
      const offsetHours = Math.round(lon / 15);
      if (offsetHours === 0) return 'UTC';
      const sign = offsetHours > 0 ? '+' : '-';
      return `Etc/GMT${sign}${Math.abs(offsetHours)}`;
    }
    return 'UTC';
  }, []);

  const handleSelect = useCallback(
    async (result: LocationResult) => {
      const lat = parseFloat(result.lat);
      const lon = parseFloat(result.lon);

      const cityName =
        result.address?.city ||
        result.address?.town ||
        result.address?.village ||
        result.display_name.split(',')[0];

      const fullName = `${cityName}${result.address?.country ? `, ${result.address.country}` : ''}`;

      setQuery(fullName);
      setIsOpen(false);

      const timezone = await getTimezone(lat, lon);

      onSelect({
        name: fullName,
        latitude: lat,
        longitude: lon,
        timezone,
      });
    },
    [onSelect, getTimezone]
  );

  const handleManualSubmit = () => {
    setManualError(null);
    const lat = parseFloat(manualLat);
    const lon = parseFloat(manualLon);

    if (isNaN(lat) || lat < -90 || lat > 90) {
      setManualError('Latitude must be a number between -90 and 90');
      return;
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      setManualError('Longitude must be a number between -180 and 180');
      return;
    }

    const name = `Manual Coords (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
    onSelect({
      name,
      latitude: lat,
      longitude: lon,
      timezone: manualTimezone,
    });
  };

  return (
    <div ref={wrapperRef} style={{ position: 'relative', width: '100%' }}>
      {!isManual ? (
        <>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              value={query}
              onChange={(e) => {
                const nextQuery = e.target.value;
                setQuery(nextQuery);
                setIsOpen(true);
                onQueryChange?.(nextQuery);
              }}
              onFocus={() => results.length > 0 && setIsOpen(true)}
              placeholder={placeholder}
              style={{
                width: '100%',
                padding: '12px 40px 12px 16px',
                fontSize: '16px',
                border: '1px solid #3d3d5c',
                borderRadius: '8px',
                background: '#1a1a2e',
                color: '#fff',
                outline: 'none',
              }}
              aria-label="Search for a city"
              aria-autocomplete="list"
              aria-expanded={isOpen}
            />
            {isLoading && (
              <div
                style={{
                  position: 'absolute',
                  right: 12,
                  top: '50%',
                  transform: 'translateY(-50%)',
                }}
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  style={{
                    width: 20,
                    height: 20,
                    border: '2px solid #4ecdc4',
                    borderTopColor: 'transparent',
                    borderRadius: '50%',
                  }}
                />
              </div>
            )}
          </div>

          <div style={{ textAlign: 'right', marginTop: '6px' }}>
            <button
              type="button"
              onClick={() => setIsManual(true)}
              style={{
                background: 'none',
                border: 'none',
                color: '#4ecdc4',
                fontSize: '13px',
                cursor: 'pointer',
                textDecoration: 'underline',
                padding: 0,
              }}
            >
              Enter coordinates manually
            </button>
          </div>

          <AnimatePresence>
            {isOpen && results.length > 0 && (
              <motion.ul
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  marginTop: 4,
                  padding: 0,
                  listStyle: 'none',
                  background: '#1a1a2e',
                  border: '1px solid #3d3d5c',
                  borderRadius: '8px',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
                  zIndex: 1000,
                  maxHeight: 300,
                  overflowY: 'auto',
                }}
                role="listbox"
              >
                {results.map((result, index) => (
                  <motion.li
                    key={index}
                    whileHover={{ backgroundColor: 'rgba(78, 205, 196, 0.1)' }}
                    onClick={() => handleSelect(result)}
                    style={{
                      padding: '12px 16px',
                      cursor: 'pointer',
                      borderBottom: index < results.length - 1 ? '1px solid #2d2d4a' : 'none',
                    }}
                    role="option"
                  >
                    <div style={{ color: '#fff', fontSize: 14 }}>
                      {result.address?.city ||
                        result.address?.town ||
                        result.address?.village ||
                        result.display_name.split(',')[0]}
                    </div>
                    <div style={{ color: '#888', fontSize: 12, marginTop: 2 }}>
                      {result.display_name.split(',').slice(1, 3).join(',')}
                    </div>
                  </motion.li>
                ))}
              </motion.ul>
            )}
          </AnimatePresence>

          {error && <div style={{ color: '#ff6b6b', fontSize: 12, marginTop: 4 }}>{error}</div>}
        </>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '16px',
            background: '#16162a',
            border: '1px solid #3d3d5c',
            borderRadius: '8px',
          }}
        >
          <div style={{ fontWeight: 600, color: '#fff', fontSize: '14px', marginBottom: '12px' }}>
            Manual Coordinate Fallback
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '12px',
              marginBottom: '12px',
            }}
          >
            <div>
              <label
                style={{ display: 'block', color: '#888', fontSize: '11px', marginBottom: '4px' }}
              >
                Latitude (-90 to 90)
              </label>
              <input
                type="number"
                step="any"
                value={manualLat}
                onChange={(e) => setManualLat(e.target.value)}
                placeholder="e.g. 51.5074"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  fontSize: '14px',
                  border: '1px solid #3d3d5c',
                  borderRadius: '6px',
                  background: '#1a1a2e',
                  color: '#fff',
                  outline: 'none',
                }}
              />
            </div>
            <div>
              <label
                style={{ display: 'block', color: '#888', fontSize: '11px', marginBottom: '4px' }}
              >
                Longitude (-180 to 180)
              </label>
              <input
                type="number"
                step="any"
                value={manualLon}
                onChange={(e) => setManualLon(e.target.value)}
                placeholder="e.g. -0.1278"
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  fontSize: '14px',
                  border: '1px solid #3d3d5c',
                  borderRadius: '6px',
                  background: '#1a1a2e',
                  color: '#fff',
                  outline: 'none',
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label
              style={{ display: 'block', color: '#888', fontSize: '11px', marginBottom: '4px' }}
            >
              Timezone
            </label>
            <select
              value={manualTimezone}
              onChange={(e) => setManualTimezone(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                fontSize: '14px',
                border: '1px solid #3d3d5c',
                borderRadius: '6px',
                background: '#1a1a2e',
                color: '#fff',
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              {COMMON_TIMEZONES.map((tz) => (
                <option key={tz} value={tz}>
                  {tz}
                </option>
              ))}
            </select>
          </div>

          {manualError && (
            <div style={{ color: '#ff6b6b', fontSize: '12px', marginBottom: '12px' }}>
              {manualError}
            </div>
          )}

          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              type="button"
              onClick={() => {
                setIsManual(false);
                setManualError(null);
              }}
              style={{
                padding: '8px 14px',
                fontSize: '13px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '6px',
                color: '#fff',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleManualSubmit}
              disabled={!manualLat || !manualLon}
              style={{
                padding: '8px 14px',
                fontSize: '13px',
                background: '#4ecdc4',
                border: 'none',
                borderRadius: '6px',
                color: '#1a1a2e',
                fontWeight: 600,
                cursor: manualLat && manualLon ? 'pointer' : 'not-allowed',
                opacity: manualLat && manualLon ? 1 : 0.6,
              }}
            >
              Save Coordinates
            </button>
          </div>
        </motion.div>
      )}
    </div>
  );
}

export default LocationAutocomplete;
