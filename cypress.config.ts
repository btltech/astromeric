import { defineConfig } from 'cypress';

export default defineConfig({
  scrollBehavior: 'center',
  video: false,
  screenshotOnRunFailure: true,
  viewportWidth: 1440,
  viewportHeight: 960,
  e2e: {
    baseUrl: 'http://127.0.0.1:4174',
    supportFile: false,
    specPattern: 'cypress/e2e/**/*.cy.ts',
    defaultCommandTimeout: 15000,
    requestTimeout: 30000,
    responseTimeout: 30000,
  },
});