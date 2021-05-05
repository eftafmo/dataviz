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
      '@js': path.resolve(__dirname, './assets/js'),
    },
    extensions: ['.js', '.vue'],
  },
})
