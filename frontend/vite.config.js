import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// Production build config. Test (vitest + storybook) config lives in
// vitest.config.js so this file stays free of ESM-only test-only packages.
export default defineConfig({
  plugins: [vue()],
  server: { port: 5173 }
});
