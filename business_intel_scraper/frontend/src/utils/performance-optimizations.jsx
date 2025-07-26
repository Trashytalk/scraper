"""
Frontend Performance Optimization Service
React-specific performance enhancements, caching, and bundle optimization
"""

import React, { 
  Suspense, 
  lazy, 
  memo, 
  useMemo, 
  useCallback, 
  useState, 
  useEffect, 
  useRef,
  createContext,
  useContext
} from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import { debounce, throttle } from 'lodash';

// Performance Context
const PerformanceContext = createContext({});

export const usePerformance = () => {
  const context = useContext(PerformanceContext);
  if (!context) {
    throw new Error('usePerformance must be used within PerformanceProvider');
  }
  return context;
};

// Performance Provider Component
export const PerformanceProvider = ({ children }) => {
  const [metrics, setMetrics] = useState({
    renderCount: 0,
    lastRenderTime: 0,
    memoryUsage: 0,
    bundleSize: 0
  });

  const updateMetrics = useCallback((newMetrics) => {
    setMetrics(prev => ({ ...prev, ...newMetrics }));
  }, []);

  const value = useMemo(() => ({
    metrics,
    updateMetrics
  }), [metrics, updateMetrics]);

  return (
    <PerformanceContext.Provider value={value}>
      {children}
    </PerformanceContext.Provider>
  );
};

// Enhanced Memo with Performance Tracking
export const EnhancedMemo = (Component, propsAreEqual, displayName) => {
  const MemoizedComponent = memo(Component, propsAreEqual);
  
  if (displayName) {
    MemoizedComponent.displayName = displayName;
  }

  return (props) => {
    const renderStart = performance.now();
    const { updateMetrics } = usePerformance();
    
    useEffect(() => {
      const renderTime = performance.now() - renderStart;
      updateMetrics({ 
        lastRenderTime: renderTime,
        renderCount: prev => prev.renderCount + 1 
      });
    });

    return <MemoizedComponent {...props} />;
  };
};

// Advanced Lazy Loading with Error Boundaries
export const LazyLoadWithBoundary = ({ 
  loader, 
  fallback = <div>Loading...</div>, 
  errorFallback = <div>Error loading component</div>,
  retries = 3 
}) => {
  const LazyComponent = lazy(loader);
  
  return (
    <ErrorBoundary
      fallback={errorFallback}
      onError={(error, errorInfo) => {
        console.error('Lazy load error:', error, errorInfo);
      }}
    >
      <Suspense fallback={fallback}>
        <LazyComponent />
      </Suspense>
    </ErrorBoundary>
  );
};

// Component Performance Monitor
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
  const PerformanceMonitoredComponent = (props) => {
    const renderCount = useRef(0);
    const startTime = useRef(performance.now());
    const { updateMetrics } = usePerformance();

    useEffect(() => {
      renderCount.current += 1;
      const endTime = performance.now();
      const renderTime = endTime - startTime.current;

      updateMetrics({
        [`${componentName}_renders`]: renderCount.current,
        [`${componentName}_last_render_time`]: renderTime
      });

      // Log slow renders (> 16ms)
      if (renderTime > 16) {
        console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
      }
    });

    useEffect(() => {
      startTime.current = performance.now();
    });

    return <WrappedComponent {...props} />;
  };

  PerformanceMonitoredComponent.displayName = `withPerformanceMonitoring(${componentName})`;
  return PerformanceMonitoredComponent;
};

// Virtual Scrolling for Large Lists
export const VirtualScrollList = memo(({ 
  items,
  itemHeight = 50,
  containerHeight = 400,
  renderItem,
  overscan = 5 
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const scrollElementRef = useRef();

  const visibleRange = useMemo(() => {
    const start = Math.floor(scrollTop / itemHeight);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = Math.min(start + visibleCount + overscan, items.length);
    
    return {
      start: Math.max(0, start - overscan),
      end
    };
  }, [scrollTop, itemHeight, containerHeight, overscan, items.length]);

  const handleScroll = useCallback(
    throttle((e) => {
      setScrollTop(e.target.scrollTop);
    }, 16), // 60fps
    []
  );

  const virtualItems = useMemo(() => {
    const result = [];
    for (let i = visibleRange.start; i < visibleRange.end; i++) {
      result.push({
        index: i,
        item: items[i],
        top: i * itemHeight
      });
    }
    return result;
  }, [items, visibleRange, itemHeight]);

  return (
    <div
      ref={scrollElementRef}
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {virtualItems.map(({ index, item, top }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top,
              left: 0,
              right: 0,
              height: itemHeight
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
});

// Smart Image Loading with Optimization
export const OptimizedImage = memo(({ 
  src, 
  alt, 
  width, 
  height, 
  lazy = true,
  placeholder = null,
  quality = 85,
  format = 'webp'
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(!lazy);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef();

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (!lazy || !imgRef.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    observer.observe(imgRef.current);
    return () => observer.disconnect();
  }, [lazy]);

  // Generate optimized image URL
  const optimizedSrc = useMemo(() => {
    if (!src || !isInView) return '';
    
    // Add optimization parameters for supported services
    const url = new URL(src, window.location.origin);
    url.searchParams.set('q', quality);
    url.searchParams.set('f', format);
    if (width) url.searchParams.set('w', width);
    if (height) url.searchParams.set('h', height);
    
    return url.toString();
  }, [src, isInView, quality, format, width, height]);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  const handleError = useCallback(() => {
    setHasError(true);
  }, []);

  return (
    <div ref={imgRef} style={{ width, height, position: 'relative' }}>
      {isInView && !hasError && (
        <img
          src={optimizedSrc}
          alt={alt}
          width={width}
          height={height}
          onLoad={handleLoad}
          onError={handleError}
          style={{
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease',
            width: '100%',
            height: '100%',
            objectFit: 'cover'
          }}
        />
      )}
      
      {(!isLoaded || !isInView) && !hasError && placeholder && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f0f0f0'
        }}>
          {placeholder}
        </div>
      )}
      
      {hasError && (
        <div style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f0f0f0',
          color: '#666'
        }}>
          Failed to load image
        </div>
      )}
    </div>
  );
});

// Debounced Search Hook
export const useDebouncedSearch = (searchFunction, delay = 300) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const debouncedSearch = useCallback(
    debounce(async (term) => {
      if (!term.trim()) {
        setResults([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const searchResults = await searchFunction(term);
        setResults(searchResults);
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, delay),
    [searchFunction, delay]
  );

  useEffect(() => {
    debouncedSearch(searchTerm);
  }, [searchTerm, debouncedSearch]);

  return {
    searchTerm,
    setSearchTerm,
    results,
    loading
  };
};

// Optimized Data Fetching Hook
export const useOptimizedFetch = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const cacheRef = useRef(new Map());
  const abortControllerRef = useRef();

  const fetchData = useCallback(async () => {
    // Check cache first
    const cacheKey = `${url}_${JSON.stringify(options)}`;
    const cached = cacheRef.current.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < (options.cacheTime || 300000)) {
      setData(cached.data);
      setLoading(false);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, {
        ...options,
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Cache the result
      cacheRef.current.set(cacheKey, {
        data: result,
        timestamp: Date.now()
      });

      setData(result);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();
    
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  const refetch = useCallback(() => {
    // Clear cache for this request
    const cacheKey = `${url}_${JSON.stringify(options)}`;
    cacheRef.current.delete(cacheKey);
    fetchData();
  }, [url, options, fetchData]);

  return { data, loading, error, refetch };
};

// Component Preloader
export const ComponentPreloader = {
  preloadedComponents: new Map(),

  preload(componentLoader, componentName) {
    if (!this.preloadedComponents.has(componentName)) {
      const promise = componentLoader().then(module => {
        this.preloadedComponents.set(componentName, module.default || module);
        return module;
      });
      this.preloadedComponents.set(componentName, promise);
    }
    return this.preloadedComponents.get(componentName);
  },

  get(componentName) {
    return this.preloadedComponents.get(componentName);
  },

  preloadRoute(routeComponents) {
    Object.entries(routeComponents).forEach(([name, loader]) => {
      this.preload(loader, name);
    });
  }
};

// Bundle Size Analyzer
export const BundleAnalyzer = {
  analyzeBundleSize() {
    if (process.env.NODE_ENV === 'development') {
      // Estimate bundle size based on loaded modules
      const estimate = Object.keys(window).length * 1000; // Rough estimate
      console.info(`Estimated bundle size: ${(estimate / 1024).toFixed(2)}KB`);
      return estimate;
    }
    return null;
  },

  trackComponentLoad(componentName, size) {
    if (process.env.NODE_ENV === 'development') {
      console.info(`Component ${componentName} loaded: ~${size}KB`);
    }
  }
};

// Memory Usage Monitor
export const MemoryMonitor = {
  checkMemoryUsage() {
    if ('memory' in performance) {
      const memory = performance.memory;
      return {
        used: Math.round(memory.usedJSHeapSize / 1048576), // MB
        total: Math.round(memory.totalJSHeapSize / 1048576),
        limit: Math.round(memory.jsHeapSizeLimit / 1048576)
      };
    }
    return null;
  },

  logMemoryUsage() {
    const usage = this.checkMemoryUsage();
    if (usage) {
      console.info(`Memory usage: ${usage.used}MB / ${usage.total}MB (limit: ${usage.limit}MB)`);
      
      // Warn if memory usage is high
      if (usage.used / usage.limit > 0.8) {
        console.warn('High memory usage detected!');
      }
    }
  }
};

// Performance Optimization HOC
export const withOptimizations = (WrappedComponent, options = {}) => {
  const {
    memo: shouldMemo = true,
    monitoring = true,
    preload = false,
    errorBoundary = true
  } = options;

  let OptimizedComponent = WrappedComponent;

  // Apply memoization
  if (shouldMemo) {
    OptimizedComponent = memo(OptimizedComponent);
  }

  // Apply performance monitoring
  if (monitoring) {
    OptimizedComponent = withPerformanceMonitoring(
      OptimizedComponent, 
      WrappedComponent.name || 'Component'
    );
  }

  // Wrap with error boundary
  if (errorBoundary) {
    const ErrorBoundaryWrapper = (props) => (
      <ErrorBoundary
        fallback={<div>Something went wrong with this component.</div>}
        onError={(error, errorInfo) => {
          console.error('Component error:', error, errorInfo);
        }}
      >
        <OptimizedComponent {...props} />
      </ErrorBoundary>
    );
    OptimizedComponent = ErrorBoundaryWrapper;
  }

  return OptimizedComponent;
};

// Global Performance Configuration
export const PerformanceConfig = {
  // Image optimization defaults
  imageOptimization: {
    quality: 85,
    format: 'webp',
    lazyLoading: true
  },

  // Virtual scrolling defaults
  virtualScrolling: {
    itemHeight: 50,
    overscan: 5,
    throttleDelay: 16
  },

  // Cache settings
  cache: {
    defaultTtl: 300000, // 5 minutes
    maxEntries: 100
  },

  // Bundle optimization
  bundleOptimization: {
    preloadCriticalComponents: true,
    splitByRoute: true,
    enableTreeShaking: true
  }
};

// Initialize Performance Optimizations
export const initializePerformanceOptimizations = () => {
  // Set up global performance monitoring
  if (typeof window !== 'undefined') {
    // Monitor memory usage periodically
    setInterval(() => {
      MemoryMonitor.logMemoryUsage();
    }, 30000); // Every 30 seconds

    // Analyze bundle size on load
    window.addEventListener('load', () => {
      BundleAnalyzer.analyzeBundleSize();
    });

    // Add performance observer for Core Web Vitals
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          console.info(`${entry.name}: ${entry.value}`);
        });
      });

      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
    }
  }
};

export default {
  PerformanceProvider,
  usePerformance,
  EnhancedMemo,
  LazyLoadWithBoundary,
  withPerformanceMonitoring,
  VirtualScrollList,
  OptimizedImage,
  useDebouncedSearch,
  useOptimizedFetch,
  ComponentPreloader,
  BundleAnalyzer,
  MemoryMonitor,
  withOptimizations,
  PerformanceConfig,
  initializePerformanceOptimizations
};
