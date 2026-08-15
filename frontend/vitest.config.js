/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';
import { playwright } from '@vitest/browser-playwright';

const dirname = typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

// Test-only config (vitest + storybook). Kept separate from vite.config.js so the
// production build does not load ESM-only test packages.
export default defineConfig({
  plugins: [vue()],
  test: {
    projects: [
      { extends: true, test: { name: 'unit', environment: 'happy-dom', include: ['src/**/*.{test,spec}.{js,ts}'], globals: true } },
      {
        extends: true,
        plugins: [storybookTest({ configDir: path.join(dirname, '.storybook') })],
        test: { name: 'storybook', browser: { enabled: true, headless: true, provider: playwright({}), instances: [{ browser: 'chromium' }] } }
      }
    ]
  }
});
