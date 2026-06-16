import { useEffect } from 'react';

type DocumentMetaProps = {
  title: string;
  description?: string;
  robots?: string;
  /** Canonical path ("/charts") or absolute URL for this route. Defaults to current path. */
  canonical?: string;
  /** Absolute URL of the social share image. */
  image?: string;
};

const SITE_ORIGIN = 'https://astronumeric.com';

function ensureMetaTag(name: string) {
  let tag = document.head.querySelector(`meta[name="${name}"]`) as HTMLMetaElement | null;

  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute('name', name);
    document.head.appendChild(tag);
  }

  return tag;
}

/** Upsert a meta tag matched by an attribute (name= or property=) and set content. */
function upsertMeta(attr: 'name' | 'property', key: string, content: string) {
  let tag = document.head.querySelector(`meta[${attr}="${key}"]`) as HTMLMetaElement | null;
  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute(attr, key);
    document.head.appendChild(tag);
  }
  tag.setAttribute('content', content);
}

function upsertCanonical(href: string) {
  let link = document.head.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
  if (!link) {
    link = document.createElement('link');
    link.setAttribute('rel', 'canonical');
    document.head.appendChild(link);
  }
  link.setAttribute('href', href);
}

function resolveUrl(canonical?: string): string {
  if (canonical && /^https?:\/\//i.test(canonical)) return canonical;
  const path = canonical ?? (typeof window !== 'undefined' ? window.location.pathname : '/');
  return `${SITE_ORIGIN}${path.startsWith('/') ? path : `/${path}`}`;
}

export function DocumentMeta({ title, description, robots, canonical, image }: DocumentMetaProps) {
  useEffect(() => {
    const previousTitle = document.title;
    const cleanupEntries: Array<{
      element: HTMLMetaElement;
      previousContent: string | null;
      created: boolean;
    }> = [];

    document.title = title;

    if (description !== undefined) {
      const existing = document.head.querySelector(
        'meta[name="description"]'
      ) as HTMLMetaElement | null;
      const element = existing ?? ensureMetaTag('description');

      cleanupEntries.push({
        element,
        previousContent: element.getAttribute('content'),
        created: existing === null,
      });

      element.setAttribute('content', description);
    }

    if (robots !== undefined) {
      const existing = document.head.querySelector('meta[name="robots"]') as HTMLMetaElement | null;
      const element = existing ?? ensureMetaTag('robots');

      cleanupEntries.push({
        element,
        previousContent: element.getAttribute('content'),
        created: existing === null,
      });

      element.setAttribute('content', robots);
    }

    // Keep canonical + social tags in sync as the SPA navigates between routes.
    const url = resolveUrl(canonical);
    upsertCanonical(url);
    upsertMeta('property', 'og:title', title);
    upsertMeta('name', 'twitter:title', title);
    upsertMeta('property', 'og:url', url);
    upsertMeta('name', 'twitter:url', url);
    if (description !== undefined) {
      upsertMeta('property', 'og:description', description);
      upsertMeta('name', 'twitter:description', description);
    }
    if (image !== undefined) {
      upsertMeta('property', 'og:image', image);
      upsertMeta('name', 'twitter:image', image);
    }

    return () => {
      document.title = previousTitle;

      cleanupEntries.forEach(({ element, previousContent, created }) => {
        if (previousContent === null) {
          if (created) {
            element.remove();
            return;
          }

          element.removeAttribute('content');
          return;
        }

        element.setAttribute('content', previousContent);
      });
    };
  }, [title, description, robots, canonical, image]);

  return null;
}
