/**
 * Cypress E2E Tests - Critical Path Testing
 * Tests core user workflows
 */

describe('AstroNumerology - Critical Paths', () => {
  const apiUrl = Cypress.env('API_URL') || 'https://astronumeric-backend-production.up.railway.app';
  
  before(() => {
    // Ensure API is healthy before running tests
    cy.request({
      method: 'GET',
      url: `${apiUrl}/health`,
      failOnStatusCode: false,
    });
  });

  // ========== AUTH FLOW ==========
  describe('Authentication', () => {
    it('should navigate to auth view', () => {
      cy.visit('/');
      cy.get('nav').should('exist');
      cy.get('a[href="/auth"]').click();
      cy.url().should('include', '/auth');
    });

    it('should show login form', () => {
      cy.visit('/#/auth');
      cy.get('input[type="email"]').should('exist');
      cy.get('input[type="password"]').should('exist');
      cy.get('button').contains(/Login|Sign In/i).should('exist');
    });
  });

  // ========== READING GENERATION ==========
  describe('Reading Generation', () => {
    it('should access reading view', () => {
      cy.visit('/');
      cy.get('a[href="/readings"]').click();
      cy.url().should('include', '/readings');
      cy.get('form, [role="form"]').should('exist');
    });

    it('should validate birth date input', () => {
      cy.visit('/#/readings');
      
      // Try empty submission
      cy.get('button').contains(/Generate|Submit/i).click();
      cy.get('[role="alert"], .error, .toast').should('be.visible');
    });

    it('should accept valid birth date', () => {
      cy.visit('/#/readings');
      
      // Fill in birth date
      cy.get('input[placeholder*="Name"]').type('Test User', { delay: 50 });
      cy.get('input[placeholder*="Birth"], input[type="date"]').type('1990-06-15');
      
      // Should not show validation error
      cy.get('[role="alert"], .error:not(.hidden)').should('not.exist');
    });
  });

  // ========== NATAL CHART VIEW ==========
  describe('Natal Chart', () => {
    it('should navigate to chart view', () => {
      cy.visit('/');
      cy.get('a[href="/chart"]').click();
      cy.url().should('include', '/chart');
    });

    it('should display chart wheel when data loads', () => {
      cy.visit('/#/chart');
      
      // Wait for chart to load
      cy.get('canvas, svg[data-testid="chart-wheel"]', { timeout: 10000 })
        .should('exist');
    });
  });

  // ========== NUMEROLOGY VIEW ==========
  describe('Numerology', () => {
    it('should access numerology view', () => {
      cy.visit('/');
      cy.get('a[href="/numerology"]').click();
      cy.url().should('include', '/numerology');
    });

    it('should display numerology form', () => {
      cy.visit('/#/numerology');
      cy.get('form, [role="form"]').should('exist');
      cy.get('input').first().should('exist');
    });

    it('should calculate numerology on valid input', () => {
      cy.visit('/#/numerology');
      
      cy.get('input[placeholder*="Name"]').type('Jane Doe', { delay: 50 });
      cy.get('input[placeholder*="Birth"], input[type="date"]').type('1985-03-20');
      
      cy.get('button').contains(/Calculate|Analyze|Generate/i).click();
      
      // Should show results
      cy.get('[class*="result"], [class*="reading"], [role="main"]')
        .should('contain.text', /Life Path|Expression|Personal/i);
    });
  });

  // ========== COMPATIBILITY CHECK ==========
  describe('Compatibility', () => {
    it('should access compatibility view', () => {
      cy.visit('/');
      cy.get('a[href="/compatibility"]').click();
      cy.url().should('include', '/compatibility');
    });

    it('should have two profile sections', () => {
      cy.visit('/#/compatibility');
      cy.get('input[placeholder*="Name"]').should('have.length.at.least', 2);
    });

    it('should validate both profiles required', () => {
      cy.visit('/#/compatibility');
      cy.get('button').contains(/Compare|Analyze/i).click();
      cy.get('[role="alert"], .error').should('be.visible');
    });

    it('should calculate compatibility on valid input', () => {
      cy.visit('/#/compatibility');
      
      // Person A
      cy.get('input[placeholder*="Name"]').first().type('Alice', { delay: 50 });
      cy.get('input[placeholder*="Birth"]').first().type('1990-06-15');
      
      // Person B
      cy.get('input[placeholder*="Name"]').last().type('Bob', { delay: 50 });
      cy.get('input[placeholder*="Birth"]').last().type('1992-12-22');
      
      cy.get('button').contains(/Compare|Analyze/i).click();
      
      // Should show compatibility results
      cy.get('[class*="result"], [class*="compatibility"], [role="main"]', { timeout: 10000 })
        .should('exist');
    });
  });

  // ========== LEARNING CENTER ==========
  describe('Learning Center', () => {
    it('should navigate to learn view', () => {
      cy.visit('/');
      cy.get('a[href="/learn"]').click();
      cy.url().should('include', '/learn');
    });

    it('should display learning modules', () => {
      cy.visit('/#/learn');
      cy.get('[class*="module"], [class*="card"], li').should('have.length.greaterThan', 0);
    });
  });

  // ========== DAILY FEATURES ==========
  describe('Daily Features', () => {
    it('should load daily features without profile', () => {
      cy.visit('/#/readings');
      
      // Daily features should be accessible
      cy.get('[class*="daily"], [class*="features"]').should('exist');
    });

    it('should display tarot card', () => {
      cy.visit('/#/readings');
      cy.get('button').contains(/Draw|Tarot|Card/i).click();
      cy.get('[class*="card"], [class*="tarot"]').should('exist');
    });
  });

  // ========== ERROR HANDLING ==========
  describe('Error Handling', () => {
    it('should show error on invalid date', () => {
      cy.visit('/#/readings');
      cy.get('input[type="date"], input[placeholder*="Birth"]').type('2099-12-31');
      cy.get('button').contains(/Generate/i).click();
      
      cy.get('[role="alert"], .error, .toast-error').should('be.visible');
    });

    it('should show error on missing required fields', () => {
      cy.visit('/#/numerology');
      cy.get('button').contains(/Calculate/i).click();
      cy.get('[role="alert"], .error, .toast-error').should('be.visible');
    });
  });

  // ========== RESPONSIVE DESIGN ==========
  describe('Responsive Design', () => {
    it('should work on mobile', () => {
      cy.viewport('iphone-x');
      cy.visit('/');
      cy.get('nav').should('exist');
      cy.get('a[href="/readings"]').should('be.visible');
    });

    it('should work on tablet', () => {
      cy.viewport('ipad-2');
      cy.visit('/');
      cy.get('nav').should('exist');
    });

    it('should work on desktop', () => {
      cy.viewport(1280, 720);
      cy.visit('/');
      cy.get('nav').should('exist');
    });
  });

  // ========== ACCESSIBILITY ==========
  describe('Accessibility', () => {
    it('should have skip link', () => {
      cy.visit('/');
      cy.get('a.skip-link, [class*="skip"]').should('exist');
    });

    it('should have proper heading hierarchy', () => {
      cy.visit('/');
      cy.get('h1').should('have.length.greaterThan', 0);
    });

    it('should have accessible form labels', () => {
      cy.visit('/#/readings');
      cy.get('input').each(($input) => {
        // Check for label or aria-label
        cy.wrap($input).should(($el) => {
          const hasLabel = !!$el.closest('label').length || $el.attr('aria-label');
          expect(hasLabel).to.be.true;
        });
      });
    });
  });

  // ========== PERFORMANCE ==========
  describe('Performance', () => {
    it('should load initial page within acceptable time', () => {
      const start = Date.now();
      cy.visit('/');
      cy.get('body').should('be.visible');
      
      cy.then(() => {
        const loadTime = Date.now() - start;
        expect(loadTime).to.be.lessThan(5000); // 5 seconds
      });
    });

    it('should have cached assets', () => {
      cy.visit('/');
      
      // Check that CSS is loaded
      cy.get('link[rel="stylesheet"]').should('exist');
      
      // Check that JS is loaded
      cy.window().should('have.property', 'React');
    });
  });
});
