import routeMeta from '../../src/seo/routeMeta.json';

describe('AstroNumeric critical route smoke', () => {
  const apiUrl = Cypress.env('API_URL') || 'https://astromeric-backend-production.up.railway.app';
  const expectedTitle = (path: keyof typeof routeMeta) => routeMeta[path].title;

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
    })
      .its('status')
      .should('eq', 200);
  });

  beforeEach(() => {
    cy.viewport(1280, 720);
  });

  it('renders the home product shell with live route links', () => {
    visitRoute('/');

    cy.title().should('eq', expectedTitle('/'));
    cy.contains('h1', 'Your birth chart, core numbers, and daily timing').should('be.visible');
    cy.contains('From profile to insight in under a minute.').should('be.visible');
    cy.get('nav').contains('Daily Insight').should('have.attr', 'href', '/reading');
    cy.get('nav').contains('Birth Chart').should('have.attr', 'href', '/charts');
  });

  it('renders the reading desk account and profile workflow', () => {
    visitRoute('/reading');

    cy.title().should('eq', expectedTitle('/reading'));
    cy.contains('h1', 'Your daily reading').should('be.visible');
    cy.contains('Select or Create Profile').should('be.visible');
    cy.get("input[placeholder='you@example.com']").should('exist');
    cy.get("input[placeholder='Password']").should('exist');
    cy.contains('button', 'Create account').should('exist');
  });

  it('renders the numerology desk in preview mode', () => {
    visitRoute('/numerology');

    cy.title().should('eq', expectedTitle('/numerology'));
    cy.contains('h1', 'Numbers, cycles, and timing').should('be.visible');
    cy.contains('h2', 'Current context').should('be.visible');
    cy.contains('h2', 'Core numbers').should('be.visible');
  });

  it('renders the relationships desk shell', () => {
    visitRoute('/relationships');

    cy.title().should('eq', expectedTitle('/relationships'));
    cy.contains('h1', 'Compatibility and synastry').should('be.visible');
    cy.contains('h2', 'Current context').should('be.visible');
    cy.contains('h2', 'How to use this suite').should('be.visible');
  });

  it('renders the charts desk shell', () => {
    visitRoute('/charts');

    cy.title().should('eq', expectedTitle('/charts'));
    cy.contains('h1', 'Your birth chart, numerology, and compatibility').should('be.visible');
    cy.contains('How to use this desk').should('be.visible');
  });

  it('renders the learn desk shell', () => {
    visitRoute('/learn');

    cy.title().should('eq', expectedTitle('/learn'));
    cy.contains('h1', 'Astrology and numerology').should('be.visible');
    cy.contains('h2', 'Study context').should('be.visible');
    cy.contains('h2', 'Lesson library').should('be.visible');
  });

  it('keeps the reading desk usable on mobile', () => {
    cy.viewport('iphone-x');
    visitRoute('/reading');

    cy.contains('h1', 'Your daily reading').should('be.visible');
    cy.get("input[placeholder='you@example.com']").should('exist');
    cy.contains('button', 'Create account').should('exist');
  });
});
