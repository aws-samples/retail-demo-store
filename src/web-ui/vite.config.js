import { fileURLToPath, URL } from 'url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { createHtmlPlugin } from 'vite-plugin-html'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    createHtmlPlugin()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      './runtimeConfig': './runtimeConfig.browser',
    },
  },
  server: {
    port: 8080,
  },
  optimizeDeps: { include: [ 'lodash.throttle', 'lodash.orderby' ] }
})