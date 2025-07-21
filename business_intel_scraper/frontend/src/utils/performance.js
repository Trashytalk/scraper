// Frontend Performance Optimization
// Bundle splitting, lazy loading, and performance monitoring

import React, { Suspense, lazy, useEffect, useState, useMemo } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

// Performance monitoring
class PerformanceTracker {
  static instance = null;
  
  constructor() {
    if (PerformanceTracker.instance) {
      return PerformanceTracker.instance;
    }
    
    this.metrics = {};
    this.observers = [];
    this.vitalsReported = false;
    
    // Initialize performance observers
    this.initializeObservers();
    
    PerformanceTracker.instance = this;
  }
  
  static getInstance() {
    if (!PerformanceTracker.instance) {
      PerformanceTracker.instance = new PerformanceTracker();
    }
    return PerformanceTracker.instance;
  }
  
  initializeObservers() {
    // Core Web Vitals tracking
    if ('PerformanceObserver' in window) {
      // Largest Contentful Paint (LCP)
      const lcpObserver = new PerformanceObserver((entryList) => {
        const lcpEntry = entryList.getEntries()[entryList.getEntries().length - 1];
        this.recordMetric('LCP', lcpEntry.startTime);
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      
      // First Input Delay (FID)
      const fidObserver = new PerformanceObserver((entryList) => {
        entryList.getEntries().forEach((entry) => {
          this.recordMetric('FID', entry.processingStart - entry.startTime);
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      
      // Cumulative Layout Shift (CLS)
      const clsObserver = new PerformanceObserver((entryList) => {
        let clsValue = 0;
        entryList.getEntries().forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });
        this.recordMetric('CLS', clsValue);
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
      
      // Long Task tracking
      const longTaskObserver = new PerformanceObserver((entryList) => {
        entryList.getEntries().forEach((entry) => {
          this.recordMetric('LONG_TASK', entry.duration, {
            name: entry.name,
            startTime: entry.startTime
          });
        });
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });
      
      this.observers.push(lcpObserver, fidObserver, clsObserver, longTaskObserver);
    }
    
    // Navigation timing
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
          this.recordMetric('DOM_CONTENT_LOADED', navigation.domContentLoadedEventEnd - navigation.navigationStart);
          this.recordMetric('LOAD_COMPLETE', navigation.loadEventEnd - navigation.navigationStart);
          this.recordMetric('TTFB', navigation.responseStart - navigation.requestStart);
        }
      }, 0);
    });
  }
  
  recordMetric(name, value, metadata = {}) {
    const timestamp = Date.now();
    
    if (!this.metrics[name]) {
      this.metrics[name] = [];
    }
    
    this.metrics[name].push({
      value,
      timestamp,
      metadata
    });
    
    // Report to analytics if configured
    if (window.gtag) {
      window.gtag('event', 'performance_metric', {
        metric_name: name,
        metric_value: Math.round(value),
        custom_parameter: JSON.stringify(metadata)
      });
    }
    
    // Console logging in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`Performance Metric: ${name} = ${value.toFixed(2)}ms`, metadata);
    }
  }
  
  startTiming(label) {
    const startTime = performance.now();
    return () => {
      const endTime = performance.now();
      this.recordMetric(`CUSTOM_${label.toUpperCase()}`, endTime - startTime);
    };
  }
  
  getMetrics() {
    return this.metrics;
  }
  
  generateReport() {
    const report = {
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      metrics: {}
    };
    
    // Calculate averages and summaries
    Object.entries(this.metrics).forEach(([metricName, values]) => {
      const numericValues = values.map(v => v.value).filter(v => typeof v === 'number');
      
      report.metrics[metricName] = {
        count: values.length,
        average: numericValues.length > 0 ? numericValues.reduce((a, b) => a + b, 0) / numericValues.length : 0,
        min: numericValues.length > 0 ? Math.min(...numericValues) : 0,
        max: numericValues.length > 0 ? Math.max(...numericValues) : 0,
        latest: values[values.length - 1]
      };
    });
    
    return report;
  }
  
  cleanup() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers = [];
  }
}

// Lazy loading utilities
export const LazyComponent = ({ loader, fallback = null, errorFallback = null }) => {
  const [Component, setComponent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    let isMounted = true;
    
    loader()
      .then((module) => {
        if (isMounted) {
          setComponent(() => module.default || module);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err);
          setLoading(false);
        }
      });
    
    return () => {
      isMounted = false;
    };
  }, [loader]);
  
  if (loading) {
    return fallback || <div className="loading-spinner">Loading...</div>;
  }
  
  if (error) {
    return errorFallback || <div className="error-message">Failed to load component</div>;
  }
  
  return Component ? <Component /> : null;
};

// Code splitting for major routes
export const LazyNetworkView = lazy(() => 
  import('../components/NetworkView').catch(error => ({
    default: () => <div>Error loading Network View: {error.message}</div>
  }))
);

export const LazyTimelineView = lazy(() => 
  import('../components/TimelineView').catch(error => ({
    default: () => <div>Error loading Timeline View: {error.message}</div>
  }))
);

export const LazyMapView = lazy(() => 
  import('../components/MapView').catch(error => ({
    default: () => <div>Error loading Map View: {error.message}</div>
  }))
);

export const LazyDashboard = lazy(() => 
  import('../components/Dashboard').catch(error => ({
    default: () => <div>Error loading Dashboard: {error.message}</div>
  }))
);

export const LazyDataViewer = lazy(() => 
  import('../../gui/components/DataViewer').catch(error => ({
    default: () => <div>Error loading Data Viewer: {error.message}</div>
  }))
);

// Performance optimized component wrapper
export const OptimizedComponent = React.memo(({ children, trackingLabel }) => {
  const tracker = PerformanceTracker.getInstance();
  
  useEffect(() => {
    const stopTiming = tracker.startTiming(`component_render_${trackingLabel}`);
    return stopTiming;
  }, [tracker, trackingLabel]);
  
  return <>{children}</>;
});

// Intersection Observer for lazy loading
export const useIntersectionObserver = (options = {}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [element, setElement] = useState(null);
  
  useEffect(() => {
    if (!element || !('IntersectionObserver' in window)) {
      return;
    }
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options
      }
    );
    
    observer.observe(element);
    
    return () => observer.disconnect();
  }, [element, options]);
  
  return [setElement, isVisible];
};

// Image lazy loading component
export const LazyImage = ({ src, alt, className, placeholder }) => {
  const [setRef, isVisible] = useIntersectionObserver();
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  
  const shouldLoad = isVisible || loaded;
  
  return (
    <div ref={setRef} className={`lazy-image ${className || ''}`}>
      {shouldLoad && !error && (
        <img
          src={src}
          alt={alt}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
          style={{ 
            opacity: loaded ? 1 : 0,
            transition: 'opacity 0.3s ease'
          }}
        />
      )}
      {!loaded && !error && (
        <div className="image-placeholder">
          {placeholder || <div className="placeholder-shimmer" />}
        </div>
      )}
      {error && (
        <div className="image-error">Failed to load image</div>
      )}
    </div>
  );
};

// Virtual scrolling for large datasets
export const VirtualList = ({ 
  items, 
  renderItem, 
  itemHeight = 50, 
  containerHeight = 400,
  overscan = 5 
}) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + overscan,
      items.length
    );
    
    return items.slice(
      Math.max(0, startIndex - overscan),
      endIndex
    ).map((item, index) => ({
      item,
      index: startIndex + index - overscan,
      top: (startIndex + index - overscan) * itemHeight
    }));
  }, [items, scrollTop, itemHeight, containerHeight, overscan]);
  
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };
  
  return (
    <div 
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map(({ item, index, top }) => (
          <div
            key={index}
            style={{
              position: 'absolute',
              top,
              width: '100%',
              height: itemHeight
            }}
          >
            {renderItem(item, index)}
          </div>
        ))}
      </div>
    </div>
  );
};

// Bundle analyzer utility
export const BundleAnalyzer = {
  async analyzeBundle() {
    if (process.env.NODE_ENV !== 'development') {
      return { message: 'Bundle analysis only available in development' };
    }
    
    try {
      const modules = await import.meta.glob('**/*.{js,jsx,ts,tsx}');
      const analysis = {
        totalModules: Object.keys(modules).length,
        modulesByType: {},
        estimatedSizes: {}
      };
      
      // Categorize modules
      Object.keys(modules).forEach(path => {
        const ext = path.split('.').pop();
        analysis.modulesByType[ext] = (analysis.modulesByType[ext] || 0) + 1;
      });
      
      return analysis;
    } catch (error) {
      return { error: error.message };
    }
  },
  
  logPerformanceTimings() {
    if ('performance' in window) {
      const timing = performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      const domReady = timing.domContentLoadedEventEnd - timing.navigationStart;
      const firstByte = timing.responseStart - timing.requestStart;
      
      console.group('Performance Timings');
      console.log(`Total Load Time: ${loadTime}ms`);
      console.log(`DOM Ready: ${domReady}ms`);
      console.log(`Time to First Byte: ${firstByte}ms`);
      console.groupEnd();
    }
  }
};

// Performance monitoring hook
export const usePerformanceMonitoring = (componentName) => {
  const tracker = PerformanceTracker.getInstance();
  
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      tracker.recordMetric(`component_lifecycle_${componentName}`, endTime - startTime);
    };
  }, [tracker, componentName]);
  
  const trackEvent = (eventName, data = {}) => {
    tracker.recordMetric(`event_${eventName}`, performance.now(), {
      component: componentName,
      ...data
    });
  };
  
  const getReport = () => tracker.generateReport();
  
  return { trackEvent, getReport };
};

// Resource preloading utilities
export const ResourcePreloader = {
  preloadRoute(routePath) {
    // Preload route chunks
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        import(`../routes${routePath}`).catch(() => {
          // Ignore preload failures
        });
      });
    }
  },
  
  preloadImage(src) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = src;
    document.head.appendChild(link);
  },
  
  preloadFont(href) {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'font';
    link.type = 'font/woff2';
    link.crossOrigin = 'anonymous';
    link.href = href;
    document.head.appendChild(link);
  }
};

// Initialize performance tracking
let performanceTracker = null;

export const initializePerformanceTracking = () => {
  if (!performanceTracker) {
    performanceTracker = PerformanceTracker.getInstance();
    
    // Report vitals periodically
    setInterval(() => {
      if (document.visibilityState === 'visible') {
        const report = performanceTracker.generateReport();
        
        // Send to analytics endpoint
        if (process.env.REACT_APP_ANALYTICS_ENDPOINT) {
          fetch(process.env.REACT_APP_ANALYTICS_ENDPOINT, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(report)
          }).catch(() => {
            // Ignore analytics errors
          });
        }
      }
    }, 30000); // Report every 30 seconds
  }
  
  return performanceTracker;
};

export default PerformanceTracker;
