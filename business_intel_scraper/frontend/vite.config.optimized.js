"""
Vite Build Optimization Configuration
Advanced bundle splitting, optimization, and performance configuration
"""

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';
import { splitVendorChunkPlugin } from 'vite';

// Custom chunk splitting strategy
const customChunkSplit = {
  // Core React libraries
  'react-vendor': ['react', 'react-dom', 'react-router-dom'],
  
  // UI libraries
  'ui-vendor': ['@mui/material', '@mui/icons-material', '@mui/lab', '@emotion/react', '@emotion/styled'],
  
  // Data visualization libraries
  'viz-vendor': ['d3', 'recharts', 'cytoscape', 'cytoscape-cola', 'vis-network', 'vis-timeline'],
  
  // Utility libraries
  'utils-vendor': ['axios', 'date-fns', 'lodash', 'clsx'],
  
  // Large/optional libraries
  'optional-vendor': ['socket.io-client', 'react-beautiful-dnd', 'react-dnd']
};

export default defineConfig(({ command, mode }) => {
  const isProduction = mode === 'production';
  const isDevelopment = mode === 'development';
  
  return {
    plugins: [
      react({
        // React Fast Refresh configuration
        fastRefresh: isDevelopment,
        
        // Babel configuration for optimization
        babel: {
          plugins: isProduction ? [
            // Remove console.log in production
            ['transform-remove-console', { exclude: ['error', 'warn'] }],
            // Optimize bundle size
            ['babel-plugin-transform-react-remove-prop-types']
          ] : []
        }
      }),
      
      // Automatic vendor chunk splitting
      splitVendorChunkPlugin(),
      
      // Bundle analyzer (only in build mode)
      ...(command === 'build' ? [
        visualizer({
          filename: 'dist/bundle-analysis.html',
          open: false,
          gzipSize: true,
          brotliSize: true
        })
      ] : [])
    ],
    
    // Path resolution
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@services': resolve(__dirname, 'src/services'),
        '@hooks': resolve(__dirname, 'src/hooks')
      }
    },
    
    // Development server configuration
    server: {
      port: 3000,
      host: true,
      hmr: {
        overlay: true
      },
      // Proxy API requests to backend
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false
        },
        '/ws': {
          target: 'ws://localhost:8000',
          ws: true
        }
      }
    },
    
    // Preview server configuration
    preview: {
      port: 8080,
      host: true
    },
    
    // Build optimization
    build: {
      // Output directory
      outDir: 'dist',
      
      // Generate source maps for production debugging
      sourcemap: isProduction ? 'hidden' : true,
      
      // Minimize bundle size
      minify: isProduction ? 'terser' : false,
      
      // Terser options for better compression
      terserOptions: isProduction ? {
        compress: {
          drop_console: true,
          drop_debugger: true,
          pure_funcs: ['console.log', 'console.info'],
          passes: 2
        },
        mangle: {
          safari10: true
        },
        format: {
          comments: false
        }
      } : {},
      
      // Rollup bundle configuration
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html')
        },
        
        output: {
          // Manual chunk splitting for better caching
          manualChunks: (id) => {
            // Node modules chunking
            if (id.includes('node_modules')) {
              // Check custom chunk mapping
              for (const [chunkName, packages] of Object.entries(customChunkSplit)) {
                if (packages.some(pkg => id.includes(`node_modules/${pkg}`))) {
                  return chunkName;
                }
              }
              
              // Default vendor chunk for other node_modules
              return 'vendor';
            }
            
            // Component chunking
            if (id.includes('src/components/widgets')) {
              return 'widgets';
            }
            
            if (id.includes('src/components') && id.includes('Dashboard')) {
              return 'dashboard';
            }
            
            if (id.includes('src/utils')) {
              return 'utils';
            }
            
            if (id.includes('src/services')) {
              return 'services';
            }
          },
          
          // Naming strategy for better caching
          chunkFileNames: (chunkInfo) => {
            if (chunkInfo.name === 'main') {
              return 'assets/app-[hash].js';
            }
            return 'assets/[name]-[hash].js';
          },
          
          entryFileNames: 'assets/entry-[hash].js',
          assetFileNames: (assetInfo) => {
            const info = assetInfo.name.split('.');
            const ext = info[info.length - 1];
            
            if (/\.(png|jpe?g|gif|svg|webp|avif)$/i.test(assetInfo.name)) {
              return 'assets/images/[name]-[hash][extname]';
            }
            
            if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
              return 'assets/fonts/[name]-[hash][extname]';
            }
            
            if (ext === 'css') {
              return 'assets/styles/[name]-[hash][extname]';
            }
            
            return 'assets/[name]-[hash][extname]';
          }
        }
      },
      
      // Asset optimization
      assetsInlineLimit: 4096, // 4kb inline limit
      
      // CSS code splitting
      cssCodeSplit: true,
      
      // Chunk size warning limit
      chunkSizeWarningLimit: 1000, // 1MB warning threshold
      
      // Enable/disable reporting
      reportCompressedSize: true,
      
      // Target for browser support
      target: 'es2020'
    },
    
    // Dependency optimization
    optimizeDeps: {
      include: [
        // Pre-bundle these dependencies
        'react',
        'react-dom',
        'react-router-dom',
        '@mui/material',
        '@mui/icons-material',
        'axios',
        'date-fns'
      ],
      exclude: [
        // Don't pre-bundle these (they'll be loaded dynamically)
        '@mui/lab'
      ]
    },
    
    // CSS preprocessing
    css: {
      postcss: {
        plugins: [
          // Autoprefixer for browser compatibility
          require('autoprefixer'),
          
          // CSS optimization for production
          ...(isProduction ? [
            require('cssnano')({
              preset: ['default', {
                discardComments: { removeAll: true },
                normalizeWhitespace: true,
                minifySelectors: true
              }]
            })
          ] : [])
        ]
      },
      
      // CSS modules configuration
      modules: {
        localsConvention: 'camelCase',
        generateScopedName: isDevelopment 
          ? '[name]__[local]__[hash:base64:5]'
          : '[hash:base64:8]'
      }
    },
    
    // ESBuild configuration
    esbuild: {
      // Remove debugging code in production
      drop: isProduction ? ['console', 'debugger'] : [],
      
      // Optimize for modern browsers in production
      target: isProduction ? 'es2020' : 'esnext'
    },
    
    // Performance optimization flags
    define: {
      // Environment variables
      __DEV__: isDevelopment,
      __PROD__: isProduction,
      
      // Performance monitoring flags
      __ENABLE_PERFORMANCE_MONITORING__: JSON.stringify(isDevelopment),
      __ENABLE_BUNDLE_ANALYSIS__: JSON.stringify(isDevelopment)
    },
    
    // Worker configuration for better performance
    worker: {
      format: 'es',
      plugins: [react()]
    }
  };
});

// Build analysis script
export const analyzeBuild = () => {
  console.log('🔍 Analyzing bundle...');
  
  // This would be called as part of the build process
  const analysis = {
    timestamp: new Date().toISOString(),
    chunks: {},
    totalSize: 0,
    gzippedSize: 0
  };
  
  return analysis;
};

// Performance budget configuration
export const performanceBudget = {
  // Bundle size limits
  maxBundleSize: '1MB',      // Total bundle size
  maxChunkSize: '300KB',     // Individual chunk size
  maxAssetSize: '100KB',     // Individual asset size
  
  // Performance thresholds
  firstContentfulPaint: 1500,  // 1.5 seconds
  largestContentfulPaint: 2500, // 2.5 seconds
  firstInputDelay: 100,         // 100ms
  cumulativeLayoutShift: 0.1,   // 0.1 score
  
  // Resource hints
  preloadCriticalResources: true,
  prefetchRoutes: ['analytics', 'dashboard'],
  
  // Compression
  enableGzip: true,
  enableBrotli: true,
  
  // Caching strategy
  cacheStrategy: {
    staticAssets: '1y',     // 1 year
    appCode: '1d',          // 1 day
    apiResponses: '5m'      // 5 minutes
  }
};

// Development optimization tips
export const devOptimizationTips = {
  "Bundle Analysis": "Run 'npm run build' to generate bundle-analysis.html",
  "Performance Monitoring": "Open DevTools Performance tab during development",
  "Memory Usage": "Check Memory tab in DevTools for memory leaks",
  "Network Optimization": "Use Network tab to identify slow requests",
  "React DevTools": "Install React DevTools for component performance profiling"
};

export default defineConfig;
