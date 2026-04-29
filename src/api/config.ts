const PRODUCTION_API_URL = 'https://astromeric-backend-production.up.railway.app';

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '');
}

export function getApiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_URL?.trim();
  return trimTrailingSlash(configured || PRODUCTION_API_URL);
}

export const API_BASE_URL = getApiBaseUrl();
