// routeMeta.ts
// Single source of truth for per-route SEO metadata (title + description),
// shared by the in-app views (via DocumentMeta) and the build-time prerenderer
// (scripts/seo-routes.mjs reads the same routeMeta.json). Keeping both on one
// file prevents the runtime <title>/OG tags from drifting away from the static
// prerendered tags that crawlers and link unfurlers see.

import routeMeta from './routeMeta.json';

export type RouteMeta = { title: string; description: string };

const META: Record<string, RouteMeta> = routeMeta as Record<string, RouteMeta>;

const FALLBACK: RouteMeta = META['/'];

/** Look up SEO metadata for a route path (e.g. "/numerology"). */
export function getRouteMeta(path: string): RouteMeta {
  return META[path] ?? FALLBACK;
}

export default META;
