/**
 * prerender.mjs
 * -------------
 * Build-time prerenderer for the AstroNumeric SPA.
 *
 * Vite ships a single index.html with an empty <div id="root"></div>, which means
 * crawlers and link unfurlers that do not execute JavaScript see no content and a
 * single shared <title>/description for every route. This script fixes that by
 * writing one static HTML file per public route into dist/ with:
 *   - route-specific <title>, meta description, canonical, Open Graph & Twitter tags
 *   - a crawlable content block injected into #root (React replaces it on mount)
 *   - per-route JSON-LD (WebPage + BreadcrumbList)
 * It also regenerates sitemap.xml from the same route list so they never drift.
 *
 * No headless browser and no new runtime dependencies — it runs as a postbuild
 * step and is fully compatible with the existing Cloudflare Pages deploy.
 *
 * Usage: node scripts/prerender.mjs   (wired into `npm run build`)
 */

import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';

import { routes, prerenderNav, SITE_ORIGIN, SITE_NAME } from './seo-routes.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DIST = join(__dirname, '..', 'dist');
const TEMPLATE_PATH = join(DIST, 'index.html');

/** Escape a string for safe use inside an HTML attribute value. */
const attr = (s) =>
  String(s)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

/** Replace the `content="..."` of a <meta> identified by an attr like name="x". */
function setMetaContent(html, identifier, value) {
  const re = new RegExp(`(<meta[^>]*?${identifier}[^>]*?content=")[^"]*(")`);
  if (!re.test(html)) return html;
  return html.replace(re, `$1${attr(value)}$2`);
}

function setCanonical(html, url) {
  return html.replace(/(<link[^>]*?rel="canonical"[^>]*?href=")[^"]*(")/, `$1${attr(url)}$2`);
}

function setTitle(html, title) {
  return html.replace(/<title>[^<]*<\/title>/, `<title>${attr(title)}</title>`);
}

/**
 * Collapse an already-prerendered <div id="root">…</div> back to an empty root so
 * the script is idempotent even if run repeatedly without a fresh `vite build`.
 * Anchored on the theme bootstrap <script> that always follows the root element.
 */
function normalizeTemplate(html) {
  return html.replace(
    /<div id="root">[\s\S]*?<\/div>(\s*<script>\s*\(function)/,
    '<div id="root"></div>$1'
  );
}

function canonicalFor(path) {
  return path === '/' ? `${SITE_ORIGIN}/` : `${SITE_ORIGIN}${path}`;
}

function jsonLd(route) {
  const url = canonicalFor(route.path);
  const crumbs = [{ '@type': 'ListItem', position: 1, name: 'Home', item: `${SITE_ORIGIN}/` }];
  if (route.path !== '/') {
    crumbs.push({ '@type': 'ListItem', position: 2, name: route.h1, item: url });
  }
  const blocks = [
    {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: route.title,
      description: route.description,
      url,
      isPartOf: { '@type': 'WebSite', name: SITE_NAME, url: `${SITE_ORIGIN}/` },
    },
    {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: crumbs,
    },
  ];
  return `\n    <script type="application/ld+json">${JSON.stringify(blocks)}</script>`;
}

function contentBlock(route) {
  // Injected into #root; React's createRoot replaces it on mount.
  return (
    `<div id="prerender-content" data-prerender="true">` +
    `<header><a href="/" aria-label="${attr(SITE_NAME)} home">${attr(SITE_NAME)}</a>` +
    prerenderNav() +
    `</header>` +
    `<main><h1>${attr(route.h1)}</h1>${route.body}</main>` +
    `<footer><p>${attr(SITE_NAME)} — astrology &amp; numerology in one place. ` +
    `<a href="/privacy-policy">Privacy</a> · <a href="/terms">Terms</a> · ` +
    `<a href="/support">Support</a></p></footer>` +
    `</div>`
  );
}

function renderRoute(template, route) {
  let html = template;
  const url = canonicalFor(route.path);

  html = setTitle(html, route.title);
  html = setMetaContent(html, 'name="description"', route.description);
  html = setCanonical(html, url);

  html = setMetaContent(html, 'property="og:title"', route.title);
  html = setMetaContent(html, 'property="og:description"', route.description);
  html = setMetaContent(html, 'property="og:url"', url);
  html = setMetaContent(html, 'name="twitter:title"', route.title);
  html = setMetaContent(html, 'name="twitter:description"', route.description);
  html = setMetaContent(html, 'name="twitter:url"', url);

  // Per-route structured data, added just before </head>.
  html = html.replace('</head>', `${jsonLd(route)}\n  </head>`);

  // Inject crawlable content into the empty root container.
  html = html.replace(/<div id="root">\s*<\/div>/, `<div id="root">${contentBlock(route)}</div>`);

  return html;
}

function outputPathFor(path) {
  if (path === '/') return TEMPLATE_PATH;
  const dir = join(DIST, path.replace(/^\//, ''));
  mkdirSync(dir, { recursive: true });
  return join(dir, 'index.html');
}

function buildSitemap() {
  const today = new Date().toISOString().slice(0, 10);
  const urls = routes
    .map(
      (r) =>
        `  <url>\n    <loc>${canonicalFor(r.path)}</loc>\n    <lastmod>${today}</lastmod>\n` +
        `    <changefreq>${r.changefreq}</changefreq>\n    <priority>${r.priority}</priority>\n  </url>`
    )
    .join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`;
}

function main() {
  let template;
  try {
    template = normalizeTemplate(readFileSync(TEMPLATE_PATH, 'utf8'));
  } catch {
    console.error(`[prerender] dist/index.html not found. Run \`vite build\` before prerendering.`);
    process.exit(1);
  }

  if (!/<div id="root">\s*<\/div>/.test(template)) {
    console.warn(
      '[prerender] Could not find an empty <div id="root"></div> in the template; ' +
        'content injection may be skipped. Check the build output.'
    );
  }

  let count = 0;
  for (const route of routes) {
    const html = renderRoute(template, route);
    writeFileSync(outputPathFor(route.path), html, 'utf8');
    count += 1;
  }

  writeFileSync(join(DIST, 'sitemap.xml'), buildSitemap(), 'utf8');

  console.log(`[prerender] Wrote ${count} static route(s) + sitemap.xml to dist/.`);
}

main();
