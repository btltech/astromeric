import { useEffect } from 'react';

type DocumentMetaProps = {
  title: string;
  description?: string;
  robots?: string;
};

function ensureMetaTag(name: string) {
  let tag = document.head.querySelector(`meta[name="${name}"]`) as HTMLMetaElement | null;

  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute('name', name);
    document.head.appendChild(tag);
  }

  return tag;
}

export function DocumentMeta({ title, description, robots }: DocumentMetaProps) {
  useEffect(() => {
    const previousTitle = document.title;
    const cleanupEntries: Array<{
      element: HTMLMetaElement;
      previousContent: string | null;
      created: boolean;
    }> = [];

    document.title = title;

    if (description !== undefined) {
      const existing = document.head.querySelector('meta[name="description"]') as HTMLMetaElement | null;
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
  }, [title, description, robots]);

  return null;
}