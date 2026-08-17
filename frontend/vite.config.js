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
  },
  build: {
    // Performance optimizations
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching and smaller initial load
manualChunks(id) {
          // Vendor chunks - rarely change, cache long-term
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('vue-router')) {
              return 'vendor-vue';
            }
            // Other vendor libs in a separate chunk
            return 'vendor';
          }
          // Design system components - separate chunk for better caching
          if (id.includes('/design-system/')) {
            return 'design-system';
          }
        }
      }
    },
    // Warn on large chunks (1MB)
    chunkSizeWarningLimit: 1000,
    // Minify for production
    minify: 'esbuild',
    // Target modern browsers for smaller bundles
    target: 'es2020'
  }
});
