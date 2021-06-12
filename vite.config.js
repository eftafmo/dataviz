import * as path from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import json5 from './assets/js/lib/vite-plugin-json5.js'

// see https://vitejs.dev/config/

export default defineConfig({
  plugins: [
      vue(),
      json5(),
  ],

  resolve: {
    alias: {
      '@js': path.resolve(__dirname, 'assets/js'),
      '@css': path.resolve(__dirname, 'assets/css'),
    },
    extensions: ['.js', '.vue'],
  },

  build: {
    // publish the manifest, django uses it in templates
    manifest: true,
    // the build directory
    outDir: path.resolve(__dirname, '../build'),
    // don't minify (TODO: only when debugging?)
    minify: false,
    emptyOutDir: true,
    brotliSize: false,

    rollupOptions: {
      input: [
        'assets/entry.js',
        'assets/site.js',
      ],
    },
  },
})
