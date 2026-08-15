import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// Production build config. Test (vitest + storybook) config lives in
// vitest.config.js so this file stays free of ESM-only test-only packages.
export default defineConfig({
  plugins: [vue()],
  server: { port: 5173 },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@design-system': path.resolve(__dirname, './src/design-system')
    }
  }
});
