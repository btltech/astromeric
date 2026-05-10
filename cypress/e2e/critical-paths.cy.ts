describe('AstroNumeric critical route smoke', () => {
  const apiUrl = Cypress.env('API_URL') || 'https://astromeric-backend-production.up.railway.app';

  function visitRoute(path: string) {
    cy.visit(path, {
      onBeforeLoad(win) {
        win.localStorage.clear();
        win.sessionStorage.removeItem('astro-session-profile');
        win.localStorage.setItem(
          'cookie-consent',
          JSON.stringify({
            essential: true,
            analytics: false,
            marketing: false,
          })
        );
      },
    });
  }

  before(() => {
    cy.request({
      method: 'GET',
      url: `${apiUrl}/health`,
      failOnStatusCode: false,
    }).its('status').should('eq', 200);
  });

  beforeEach(() => {
    cy.viewport(1280, 720);
  });

  it('renders the home product shell with live route links', () => {
    visitRoute('/');

    cy.title().should('eq', 'AstroNumeric — Redesign Preview');
    cy.contains(
      'AstroNumeric can feel like a serious modern prediction product instead of a mystical brochure.'
    ).should('be.visible');
    cy.contains('FixtureCast-inspired product rhythm').should('be.visible');
    cy.get('nav').contains('Reading').should('have.attr', 'href', '/reading');
    cy.get('nav').contains('Charts').should('have.attr', 'href', '/charts');
  });

  it('renders the reading desk account and profile workflow', () => {
    visitRoute('/reading');

    cy.title().should('eq', 'AstroNumeric — Reading Desk');
    cy.contains('The reading route is back as a real product flow: profile in, live guidance out.')
      .should('be.visible');
    cy.contains('Profile setup').should('be.visible');
    cy.contains('Railway backend').should('be.visible');
    cy.get("input[placeholder='you@example.com']").should('be.visible');
    cy.get("input[placeholder='Minimum account password']").should('be.visible');
    cy.contains('button', 'Create Railway account').should('be.visible');
  });

  it('renders the numerology desk in preview mode', () => {
    visitRoute('/numerology');

    cy.title().should('eq', 'AstroNumeric — Numerology Desk');
    cy.contains('Give numerology its own route so timing and meaning stop hiding inside charts.')
      .should('be.visible');
    cy.contains('Current context').should('be.visible');
    cy.contains('Core numbers').should('be.visible');
  });

  it('renders the relationships desk shell', () => {
    visitRoute('/relationships');

    cy.title().should('eq', 'AstroNumeric — Relationships Desk');
    cy.contains('Turn compatibility into a place users can return to, not a one-off calculation.')
      .should('be.visible');
    cy.contains('Current context').should('be.visible');
    cy.contains('How to use this suite').should('be.visible');
  });

  it('renders the charts desk shell', () => {
    visitRoute('/charts');

    cy.title().should('eq', 'AstroNumeric — Charts Desk');
    cy.contains(
      'AstroNumeric can turn natal, numerology, and compatibility into a real chart desk instead of a demo surface.'
    ).should('be.visible');
    cy.contains('Open chart desk').should('be.visible');
    cy.contains('Birth chart desk').should('be.visible');
  });

  it('renders the learn desk shell', () => {
    visitRoute('/learn');

    cy.title().should('eq', 'AstroNumeric — Learn Desk');
    cy.contains(
      'Make learning a real routed workspace with lessons, glossary context, and visible study progress.'
    ).should('be.visible');
    cy.contains('Study context').should('be.visible');
    cy.contains('Lesson library').should('be.visible');
  });

  it('keeps the reading desk usable on mobile', () => {
    cy.viewport('iphone-x');
    visitRoute('/reading');

    cy.contains('Profile setup').should('be.visible');
    cy.contains('Railway backend').should('be.visible');
    cy.contains('button', 'Create Railway account').should('be.visible');
  });
});
