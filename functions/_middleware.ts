import routeMetaJson from '../src/seo/routeMeta.json';

const routeMeta = routeMetaJson as Record<string, { title: string; description: string }>;

export const onRequest = async (context: { next: () => Promise<Response>; request: Request }) => {
  const response = await context.next();

  // Only intercept HTML requests, ignore XML/JS/CSS/Images/Sitemaps
  const url = new URL(context.request.url);
  const pathname = url.pathname;

  if (
    pathname.endsWith('.xml') ||
    pathname.endsWith('.txt') ||
    pathname.endsWith('.json') ||
    pathname.endsWith('.js') ||
    pathname.endsWith('.css')
  ) {
    return response;
  }

  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('text/html')) {
    let matchedRoute = routeMeta['/'];

    // Sort keys by length descending to match longest path prefix first (e.g. /privacy-policy before /)
    const sortedRoutes = Object.keys(routeMeta).sort((a, b) => b.length - a.length);
    for (const route of sortedRoutes) {
      if (
        pathname === route ||
        pathname.startsWith(route + '/') ||
        (route !== '/' && pathname.startsWith(route))
      ) {
        matchedRoute = routeMeta[route];
        break;
      }
    }

    const title = matchedRoute.title;
    const description = matchedRoute.description;

    // Edge-rewrite the HTML before sending to Twitter/Discord/iMessage/crawlers
    return new HTMLRewriter()
      .on('meta[property="og:title"]', {
        element(e) {
          e.setAttribute('content', title);
        },
      })
      .on('meta[name="twitter:title"]', {
        element(e) {
          e.setAttribute('content', title);
        },
      })
      .on('meta[property="og:description"]', {
        element(e) {
          e.setAttribute('content', description);
        },
      })
      .on('meta[name="twitter:description"]', {
        element(e) {
          e.setAttribute('content', description);
        },
      })
      .on('meta[name="description"]', {
        element(e) {
          e.setAttribute('content', description);
        },
      })
      .on('title', {
        element(e) {
          e.setInnerContent(title);
        },
      })
      .on('link[rel="canonical"]', {
        element(e) {
          e.setAttribute('href', `https://astronumeric.com${pathname}`);
        },
      })
      .on('meta[property="og:url"]', {
        element(e) {
          e.setAttribute('content', `https://astronumeric.com${pathname}`);
        },
      })
      .transform(response);
  }

  return response;
};
