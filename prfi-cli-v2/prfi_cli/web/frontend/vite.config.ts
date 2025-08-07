import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh
      fastRefresh: true,
      // Include .jsx files
      include: "**/*.{jsx,tsx}",
    })
  ],
  
  // Configuração do servidor de desenvolvimento
  server: {
    port: 3000,
    host: true, // Permite acesso externo
    open: false, // Não abrir automaticamente
    cors: true,
    proxy: {
      // Proxy para API backend
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        ws: true, // WebSocket support
      }
    }
  },
  
  // Configuração de build
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: {
          // Separar vendor chunks para melhor cache
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query'],
          ui: ['framer-motion', 'lucide-react'],
          charts: ['recharts'],
        }
      }
    },
    // Configurações de otimização
    chunkSizeWarningLimit: 1000,
    assetsInlineLimit: 4096,
  },
  
  // Configuração de preview (produção local)
  preview: {
    port: 3000,
    host: true,
    cors: true,
  },
  
  // Resolução de paths
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/components': resolve(__dirname, 'src/components'),
      '@/pages': resolve(__dirname, 'src/pages'),
      '@/services': resolve(__dirname, 'src/services'),
      '@/utils': resolve(__dirname, 'src/utils'),
      '@/hooks': resolve(__dirname, 'src/hooks'),
      '@/types': resolve(__dirname, 'src/types'),
      '@/assets': resolve(__dirname, 'src/assets'),
    }
  },
  
  // Configuração de CSS
  css: {
    postcss: './postcss.config.js',
    devSourcemap: true,
  },
  
  // Configuração de otimização de dependências
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'framer-motion',
      'lucide-react',
      'recharts'
    ],
    exclude: ['@vite/client', '@vite/env']
  },
  
  // Configuração de environment variables
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  
  // Configuração de assets
  assetsInclude: ['**/*.svg', '**/*.png', '**/*.jpg', '**/*.jpeg', '**/*.gif'],
  
  // Configuração de worker
  worker: {
    format: 'es'
  },
  
  // Configuração de JSON
  json: {
    namedExports: true,
    stringify: false
  },
  
  // Configuração de logs
  logLevel: 'info',
  clearScreen: false,
  
  // Configuração específica para diferentes ambientes
  ...(process.env.NODE_ENV === 'development' && {
    // Configurações específicas para desenvolvimento
    esbuild: {
      sourcemap: true,
    }
  }),
  
  ...(process.env.NODE_ENV === 'production' && {
    // Configurações específicas para produção
    esbuild: {
      drop: ['console', 'debugger'],
      legalComments: 'none',
    }
  }),
})
