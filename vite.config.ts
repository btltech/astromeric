import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig(({ mode: _mode }) => {
  return {
    server: {
      port: 3000,
      host: '0.0.0.0',
    },
    plugins: [react(), visualizer({ open: true, filename: 'dist/stats.html' })],
    define: {
      // Remove API key exposure to client-side
      // 'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
      // 'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    build: {
      target: 'esnext',
      minify: 'terser',
      cssCodeSplit: true,
      rollupOptions: {
        output: {
          entryFileNames: 'js/[name].[hash].js',
          chunkFileNames: 'js/[name].[hash].js',
          assetFileNames: 'assets/[name].[hash][extname]',
          manualChunks: {
            'vendor-react': ['react', 'react-dom', 'react-router-dom', 'zustand'],
            'vendor-three': ['three', '@react-three/fiber', '@react-three/drei'],
            'vendor-utils': ['jspdf', 'html-to-image', 'i18next'],
          },
        },
      },
    },
  };
});
