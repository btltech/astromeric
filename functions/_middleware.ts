export const onRequest = async (context) => {
  const response = await context.next();
  
  // Only intercept HTML requests, ignore JS/CSS/Images
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("text/html")) {
    const url = new URL(context.request.url);
    
    // Default Tags (Matches index.html)
    let title = 'AstroNumeric | Daily Insight, Birth Chart & Numerology';
    let description = 'AstroNumeric combines astrology, numerology, compatibility, and timing in one clear daily signal.';

    // Dynamic Route Mappings
    if (url.pathname.startsWith('/reading')) {
      title = 'AstroNumeric — Reading Desk';
      description = 'Review your personalized astrological and numerological profile analysis.';
    } else if (url.pathname.startsWith('/numerology')) {
      title = 'AstroNumeric — Numerology Desk';
      description = 'Your core numbers, personal cycles, lucky days, and long-range arc.';
    } else if (url.pathname.startsWith('/relationships')) {
      title = 'AstroNumeric — Relationships Desk';
      description = 'Understand the mechanics of your connections using chart and numerology compatibility.';
    } else if (url.pathname.startsWith('/learn')) {
      title = 'AstroNumeric — Learning Desk';
      description = 'Explore astrology and numerology concepts in an easy to understand format.';
    } else if (url.pathname.startsWith('/charts')) {
      title = 'AstroNumeric — Cosmic Tools';
      description = 'Calculate birth charts, daily features, and localized astrological timing.';
    }
    
    // Edge-rewrite the HTML before sending to Twitter/Discord/iMessage
    return new HTMLRewriter()
      .on('meta[property="og:title"]', { element(e) { e.setAttribute('content', title); } })
      .on('meta[property="og:description"]', { element(e) { e.setAttribute('content', description); } })
      .on('meta[name="description"]', { element(e) { e.setAttribute('content', description); } })
      .on('title', { element(e) { e.setInnerContent(title); } })
      .transform(response);
  }
  
  return response;
};