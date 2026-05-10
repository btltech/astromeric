describe('Reading Desk Railway auth sync', () => {
  const apiUrl =
    Cypress.env('API_URL') || 'https://astromeric-backend-production.up.railway.app';

  const localProfile = {
    id: -777,
    name: 'Avery Postfix',
    date_of_birth: '1991-06-16',
    time_of_birth: '08:45',
    place_of_birth: 'Abuja, Nigeria',
    latitude: 9.0765,
    longitude: 7.3986,
    timezone: 'Africa/Lagos',
    house_system: null,
  };

  const localReading = {
    id: 'reading_smoke_local_cypress',
    scope: 'daily',
    date: '2026-05-09',
    profile: {
      name: 'Avery Postfix',
      date_of_birth: '1991-06-16',
      time_of_birth: '08:45',
      timezone: 'Africa/Lagos',
      place_of_birth: 'Abuja, Nigeria',
    },
    content: {
      scope: 'daily',
      date: '2026-05-09',
      overall_score: 82,
      sections: [
        {
          title: 'Timing',
          summary: 'Cypress smoke reading ready for migration.',
          topics: { work: 9, relationships: 6 },
          avoid: ['Overcommitting'],
          embrace: ['Finishing the handoff'],
        },
      ],
    },
    timestamp: Date.now(),
  };

  let cleanupToken: string | null = null;

  function seedLocalState(win: Window) {
    win.localStorage.setItem(
      'cookie-consent',
      JSON.stringify({
        essential: true,
        analytics: false,
        marketing: false,
      })
    );

    win.localStorage.setItem(
      'astro-storage',
      JSON.stringify({
        state: {
          profiles: [localProfile],
          selectedProfileId: localProfile.id,
          compareProfileId: null,
          selectedScope: 'daily',
          token: null,
          user: null,
          theme: 'default',
          tonePreference: 50,
          dailyReminderEnabled: false,
          reminderCadence: 'daily',
          allowCloudHistory: false,
          streakCount: 1,
          lastVisitDate: '2026-05-09',
        },
        version: 0,
      })
    );

    win.localStorage.setItem('astromeric_anon_readings', JSON.stringify([localReading]));
    win.sessionStorage.removeItem('astro-session-profile');
  }

  beforeEach(() => {
    cleanupToken = null;
    cy.request({
      method: 'GET',
      url: `${apiUrl}/health`,
      failOnStatusCode: false,
    }).its('status').should('eq', 200);
  });

  afterEach(() => {
    if (!cleanupToken) {
      return;
    }

    cy.request({
      method: 'DELETE',
      url: `${apiUrl}/v2/auth/account`,
      headers: {
        Authorization: `Bearer ${cleanupToken}`,
      },
      failOnStatusCode: false,
    });
  });

  it('hydrates the migrated Railway profile immediately after account creation', () => {
    const timestamp = Date.now();
    const email = `qa-cypress-${timestamp}@example.com`;
    const password = `AstroSmoke${timestamp}!A`;

    cy.visit('/reading', {
      onBeforeLoad(win) {
        seedLocalState(win);
      },
    });

    cy.window().then((win) => {
      const unregisterServiceWorkers =
        'serviceWorker' in win.navigator
          ? win.navigator.serviceWorker
              .getRegistrations()
              .then((registrations) => Promise.all(registrations.map((registration) => registration.unregister())))
          : Promise.resolve([]);
      const clearCaches =
        'caches' in win
          ? win.caches.keys().then((keys) => Promise.all(keys.map((key) => win.caches.delete(key))))
          : Promise.resolve([]);

      return Promise.all([unregisterServiceWorkers, clearCaches]);
    });

    cy.reload(true);

    cy.contains('1 local profiles and 1 local readings are currently waiting on this device.').should(
      'be.visible'
    );

    cy.contains('.reading-account-form', 'Connect Railway once, then keep this desk portable.')
      .scrollIntoView()
      .should('be.visible');

    cy.get("input[placeholder='you@example.com']").should('be.visible').click().type(email);
    cy.get("input[placeholder='Minimum account password']")
      .should('be.visible')
      .click()
      .type(password, { log: false });
    cy.contains('button', 'Create Railway account').click();

    cy.contains('Railway sync complete: 1 profiles and 1 readings migrated.', {
      timeout: 30000,
    }).should('be.visible');
    cy.contains(
      '.reading-account-card p',
      'Railway cloud sync is active. New saved profiles and cloud-history readings now target the backend.'
    ).should('be.visible');
    cy.contains(
      '.reading-account-inline-note',
      'Cloud history is active, so future saved readings can go straight to Railway.'
    ).should('be.visible');
    cy.contains('.reading-history-summary, .reading-panel', 'No local readings yet').should(
      'be.visible'
    );

    cy.get('.reading-account-stat').eq(0).should('contain.text', '0').and('contain.text', 'already clear');
    cy.get('.reading-account-stat').eq(1).should('contain.text', '0').and('contain.text', 'already clear');

    cy.window().should((win) => {
      const persisted = JSON.parse(win.localStorage.getItem('astro-storage') || '{}');
      const state = persisted.state || {};

      expect(state.token, 'cleanup token').to.be.a('string');
      expect(state.allowCloudHistory).to.equal(true);
      expect(state.user?.email).to.equal(email);
      expect(win.localStorage.getItem('astromeric_anon_readings')).to.equal(null);
    });

    cy.window().then((win) => {
      const persisted = JSON.parse(win.localStorage.getItem('astro-storage') || '{}');
      const state = persisted.state || {};

      cleanupToken = state.token ?? null;

      return cy
        .request({
          method: 'GET',
          url: `${apiUrl}/v2/profiles/`,
          headers: {
            Authorization: `Bearer ${cleanupToken}`,
          },
        })
        .its('body.data')
        .should((profiles) => {
          expect(profiles).to.have.length(1);
          expect(profiles[0].name).to.equal(localProfile.name);
          expect(profiles[0].date_of_birth).to.equal(localProfile.date_of_birth);
        });
    });

    cy.scrollTo('top');
    cy.get('.reading-profile-summary').scrollIntoView().should('contain.text', localProfile.name);
    cy.get('.reading-profile-summary').should('contain.text', 'Railway profile');
  });
});