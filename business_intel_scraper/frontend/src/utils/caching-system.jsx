"""
Advanced React Caching System
Intelligent caching for API responses, component state, and computed values
"""

import React, { 
  createContext, 
  useContext, 
  useState, 
  useEffect, 
  useRef, 
  useCallback, 
  useMemo 
} from 'react';

// Cache Storage Interface
class CacheStorage {
  constructor(name, maxSize = 100, ttl = 300000) { // 5 minutes default TTL
    this.name = name;
    this.maxSize = maxSize;
    this.defaultTtl = ttl;
    this.cache = new Map();
    this.accessTimes = new Map();
  }

  set(key, value, ttl = this.defaultTtl) {
    const now = Date.now();
    const expiresAt = now + ttl;

    // Remove expired entries and enforce size limit
    this._cleanup();

    // If cache is full, remove least recently used
    if (this.cache.size >= this.maxSize) {
      this._evictLRU();
    }

    this.cache.set(key, {
      value,
      expiresAt,
      createdAt: now,
      accessCount: 0
    });

    this.accessTimes.set(key, now);
    return true;
  }

  get(key) {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.delete(key);
      return null;
    }

    // Update access tracking
    entry.accessCount++;
    this.accessTimes.set(key, Date.now());

    return entry.value;
  }

  has(key) {
    const entry = this.cache.get(key);
    if (!entry) return false;
    
    if (Date.now() > entry.expiresAt) {
      this.delete(key);
      return false;
    }
    
    return true;
  }

  delete(key) {
    this.cache.delete(key);
    this.accessTimes.delete(key);
    return true;
  }

  clear() {
    this.cache.clear();
    this.accessTimes.clear();
  }

  _cleanup() {
    const now = Date.now();
    const expiredKeys = [];

    for (const [key, entry] of this.cache) {
      if (now > entry.expiresAt) {
        expiredKeys.push(key);
      }
    }

    expiredKeys.forEach(key => this.delete(key));
  }

  _evictLRU() {
    let oldestKey = null;
    let oldestTime = Date.now();

    for (const [key, time] of this.accessTimes) {
      if (time < oldestTime) {
        oldestTime = time;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.delete(oldestKey);
    }
  }

  getStats() {
    this._cleanup();
    
    const entries = Array.from(this.cache.values());
    const totalAccess = entries.reduce((sum, entry) => sum + entry.accessCount, 0);
    
    return {
      name: this.name,
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate: totalAccess > 0 ? entries.filter(e => e.accessCount > 0).length / entries.length : 0,
      totalAccess,
      memoryUsage: this._estimateMemoryUsage()
    };
  }

  _estimateMemoryUsage() {
    // Rough estimation of memory usage in bytes
    let size = 0;
    for (const [key, entry] of this.cache) {
      size += JSON.stringify(key).length * 2; // Rough key size
      size += JSON.stringify(entry.value).length * 2; // Rough value size
      size += 64; // Entry metadata overhead
    }
    return size;
  }
}

// Cache Context
const CacheContext = createContext({});

export const useCache = () => {
  const context = useContext(CacheContext);
  if (!context) {
    throw new Error('useCache must be used within CacheProvider');
  }
  return context;
};

// Cache Provider Component
export const CacheProvider = ({ children, config = {} }) => {
  const caches = useRef({
    api: new CacheStorage('api', config.apiCacheSize || 50, config.apiCacheTtl || 300000),
    computed: new CacheStorage('computed', config.computedCacheSize || 100, config.computedCacheTtl || 600000),
    components: new CacheStorage('components', config.componentCacheSize || 30, config.componentCacheTtl || 900000),
    user: new CacheStorage('user', config.userCacheSize || 20, config.userCacheTtl || 1800000)
  });

  const [stats, setStats] = useState({});

  // Update cache statistics periodically
  useEffect(() => {
    const updateStats = () => {
      const newStats = {};
      Object.entries(caches.current).forEach(([name, cache]) => {
        newStats[name] = cache.getStats();
      });
      setStats(newStats);
    };

    updateStats();
    const interval = setInterval(updateStats, 10000); // Update every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  const getCache = useCallback((type = 'api') => {
    return caches.current[type] || caches.current.api;
  }, []);

  const clearCache = useCallback((type) => {
    if (type) {
      const cache = caches.current[type];
      if (cache) cache.clear();
    } else {
      Object.values(caches.current).forEach(cache => cache.clear());
    }
  }, []);

  const clearExpired = useCallback(() => {
    Object.values(caches.current).forEach(cache => cache._cleanup());
  }, []);

  const value = useMemo(() => ({
    getCache,
    clearCache,
    clearExpired,
    stats
  }), [getCache, clearCache, clearExpired, stats]);

  return (
    <CacheContext.Provider value={value}>
      {children}
    </CacheContext.Provider>
  );
};

// API Response Caching Hook
export const useCachedAPI = (url, options = {}) => {
  const { getCache } = useCache();
  const cache = getCache('api');
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const cacheKey = useMemo(() => {
    return `${url}_${JSON.stringify(options.params || {})}_${JSON.stringify(options.headers || {})}`;
  }, [url, options.params, options.headers]);

  const fetchData = useCallback(async (force = false) => {
    // Check cache first (unless forced)
    if (!force) {
      const cachedData = cache.get(cacheKey);
      if (cachedData) {
        setData(cachedData);
        setLoading(false);
        return cachedData;
      }
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Cache the successful response
      cache.set(cacheKey, result, options.cacheTtl);
      
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [url, options, cache, cacheKey]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refresh = useCallback(() => {
    return fetchData(true);
  }, [fetchData]);

  return { data, loading, error, refresh };
};

// Computed Value Caching Hook
export const useCachedComputed = (computeFn, dependencies, cacheKey, ttl = 600000) => {
  const { getCache } = useCache();
  const cache = getCache('computed');
  
  return useMemo(() => {
    const key = `${cacheKey}_${JSON.stringify(dependencies)}`;
    
    // Check cache first
    const cached = cache.get(key);
    if (cached !== null) {
      return cached;
    }

    // Compute and cache
    const result = computeFn();
    cache.set(key, result, ttl);
    
    return result;
  }, [computeFn, dependencies, cacheKey, ttl, cache]);
};

// Component State Caching Hook
export const useCachedState = (key, initialValue, ttl = 900000) => {
  const { getCache } = useCache();
  const cache = getCache('components');
  
  const [state, setState] = useState(() => {
    const cached = cache.get(key);
    return cached !== null ? cached : initialValue;
  });

  const setCachedState = useCallback((newState) => {
    const value = typeof newState === 'function' ? newState(state) : newState;
    setState(value);
    cache.set(key, value, ttl);
  }, [state, cache, key, ttl]);

  useEffect(() => {
    // Update cache when state changes
    cache.set(key, state, ttl);
  }, [state, cache, key, ttl]);

  return [state, setCachedState];
};

// User Preference Caching Hook
export const useCachedUserPreference = (key, defaultValue) => {
  const { getCache } = useCache();
  const cache = getCache('user');
  
  const [preference, setPreferenceState] = useState(() => {
    // Try cache first, then localStorage, then default
    const cached = cache.get(key);
    if (cached !== null) return cached;
    
    const stored = localStorage.getItem(`pref_${key}`);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        cache.set(key, parsed, 1800000); // 30 minutes
        return parsed;
      } catch (e) {
        // Invalid JSON in localStorage
      }
    }
    
    return defaultValue;
  });

  const setPreference = useCallback((newValue) => {
    setPreferenceState(newValue);
    cache.set(key, newValue, 1800000); // 30 minutes
    localStorage.setItem(`pref_${key}`, JSON.stringify(newValue));
  }, [cache, key]);

  return [preference, setPreference];
};

// Batch Cache Operations
export const useBatchCache = () => {
  const { getCache } = useCache();
  
  const batchSet = useCallback((operations, cacheType = 'api') => {
    const cache = getCache(cacheType);
    const results = [];
    
    operations.forEach(({ key, value, ttl }) => {
      const success = cache.set(key, value, ttl);
      results.push({ key, success });
    });
    
    return results;
  }, [getCache]);

  const batchGet = useCallback((keys, cacheType = 'api') => {
    const cache = getCache(cacheType);
    const results = {};
    
    keys.forEach(key => {
      results[key] = cache.get(key);
    });
    
    return results;
  }, [getCache]);

  const batchDelete = useCallback((keys, cacheType = 'api') => {
    const cache = getCache(cacheType);
    const results = [];
    
    keys.forEach(key => {
      const success = cache.delete(key);
      results.push({ key, success });
    });
    
    return results;
  }, [getCache]);

  return { batchSet, batchGet, batchDelete };
};

// Cache Invalidation Hook
export const useCacheInvalidation = () => {
  const { getCache, clearCache } = useCache();
  
  const invalidatePattern = useCallback((pattern, cacheType = 'api') => {
    const cache = getCache(cacheType);
    const keysToDelete = [];
    
    // Find keys matching the pattern
    for (const [key] of cache.cache) {
      if (key.includes(pattern)) {
        keysToDelete.push(key);
      }
    }
    
    // Delete matching keys
    keysToDelete.forEach(key => cache.delete(key));
    
    return keysToDelete.length;
  }, [getCache]);

  const invalidateTags = useCallback((tags, cacheType = 'api') => {
    const cache = getCache(cacheType);
    const keysToDelete = [];
    
    // Find keys with matching tags (assuming tags are in key format)
    for (const [key] of cache.cache) {
      if (tags.some(tag => key.includes(tag))) {
        keysToDelete.push(key);
      }
    }
    
    keysToDelete.forEach(key => cache.delete(key));
    
    return keysToDelete.length;
  }, [getCache]);

  const invalidateAll = useCallback((cacheType) => {
    clearCache(cacheType);
  }, [clearCache]);

  return { invalidatePattern, invalidateTags, invalidateAll };
};

// Cache Statistics Component
export const CacheStatistics = ({ showDetails = false }) => {
  const { stats } = useCache();
  
  if (!showDetails) {
    const totalEntries = Object.values(stats).reduce((sum, stat) => sum + (stat.size || 0), 0);
    const avgHitRate = Object.values(stats).reduce((sum, stat) => sum + (stat.hitRate || 0), 0) / Object.keys(stats).length;
    
    return (
      <div style={{ padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '4px', fontSize: '12px' }}>
        Cache: {totalEntries} entries, {(avgHitRate * 100).toFixed(1)}% hit rate
      </div>
    );
  }

  return (
    <div style={{ padding: '15px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
      <h3>Cache Statistics</h3>
      {Object.entries(stats).map(([name, stat]) => (
        <div key={name} style={{ marginBottom: '10px', padding: '10px', backgroundColor: 'white', borderRadius: '4px' }}>
          <h4>{stat.name || name}</h4>
          <div>Size: {stat.size || 0} / {stat.maxSize || 0}</div>
          <div>Hit Rate: {((stat.hitRate || 0) * 100).toFixed(1)}%</div>
          <div>Total Access: {stat.totalAccess || 0}</div>
          <div>Memory: {Math.round((stat.memoryUsage || 0) / 1024)}KB</div>
        </div>
      ))}
    </div>
  );
};

// Cache Management Component
export const CacheManager = () => {
  const { clearCache, clearExpired, stats } = useCache();
  
  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
      <h3>Cache Management</h3>
      
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button onClick={() => clearCache('api')}>Clear API Cache</button>
        <button onClick={() => clearCache('computed')}>Clear Computed Cache</button>
        <button onClick={() => clearCache('components')}>Clear Component Cache</button>
        <button onClick={() => clearCache()}>Clear All Caches</button>
        <button onClick={clearExpired}>Clear Expired</button>
      </div>
      
      <CacheStatistics showDetails={true} />
    </div>
  );
};

// Smart Cache Key Generator
export const generateCacheKey = (prefix, params) => {
  const sortedParams = Object.keys(params || {})
    .sort()
    .reduce((sorted, key) => {
      sorted[key] = params[key];
      return sorted;
    }, {});
  
  return `${prefix}_${JSON.stringify(sortedParams)}`;
};

// Cache Configuration
export const CacheConfig = {
  defaultTtl: {
    api: 300000,      // 5 minutes
    computed: 600000, // 10 minutes
    components: 900000, // 15 minutes
    user: 1800000     // 30 minutes
  },
  
  defaultSizes: {
    api: 50,
    computed: 100,
    components: 30,
    user: 20
  },
  
  strategies: {
    LRU: 'least-recently-used',
    LFU: 'least-frequently-used',
    TTL: 'time-to-live'
  }
};

export default {
  CacheProvider,
  useCache,
  useCachedAPI,
  useCachedComputed,
  useCachedState,
  useCachedUserPreference,
  useBatchCache,
  useCacheInvalidation,
  CacheStatistics,
  CacheManager,
  generateCacheKey,
  CacheConfig
};
