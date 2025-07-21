// User Experience Enhancements
// Mobile responsiveness, drag-and-drop interface, and advanced search

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useMediaQuery, useTheme } from '@mui/material';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { TouchBackend } from 'react-dnd-touch-backend';
import Fuse from 'fuse.js';
import debounce from 'lodash.debounce';
import './styles/responsive.css';
import './styles/drag-drop.css';

// Mobile detection and responsive utilities
export const useResponsive = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery('(max-width: 768px)');
  const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)');
  const isDesktop = useMediaQuery('(min-width: 1025px)');
  const isLandscape = useMediaQuery('(orientation: landscape)');
  const isPortrait = useMediaQuery('(orientation: portrait)');
  
  // Detect touch device
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  
  // Get device type
  const deviceType = useMemo(() => {
    if (isMobile) return 'mobile';
    if (isTablet) return 'tablet';
    return 'desktop';
  }, [isMobile, isTablet]);
  
  // Responsive breakpoints
  const breakpoints = {
    xs: useMediaQuery(theme.breakpoints.down('xs')),
    sm: useMediaQuery(theme.breakpoints.down('sm')),
    md: useMediaQuery(theme.breakpoints.down('md')),
    lg: useMediaQuery(theme.breakpoints.down('lg')),
    xl: useMediaQuery(theme.breakpoints.down('xl'))
  };
  
  // Responsive grid columns
  const getGridColumns = useCallback(() => {
    if (isMobile) return 1;
    if (isTablet) return 2;
    return isLandscape ? 4 : 3;
  }, [isMobile, isTablet, isLandscape]);
  
  // Responsive component size
  const getComponentSize = useCallback((baseSize = 'medium') => {
    if (isMobile) return 'small';
    if (isTablet) return 'medium';
    return baseSize;
  }, [isMobile, isTablet]);
  
  return {
    isMobile,
    isTablet,
    isDesktop,
    isLandscape,
    isPortrait,
    isTouchDevice,
    deviceType,
    breakpoints,
    getGridColumns,
    getComponentSize
  };
};

// Advanced responsive layout component
export const ResponsiveLayout = ({ 
  children, 
  mobileLayout, 
  tabletLayout, 
  desktopLayout,
  className = '' 
}) => {
  const { deviceType } = useResponsive();
  
  const getLayoutClass = () => {
    switch (deviceType) {
      case 'mobile':
        return `responsive-layout mobile-layout ${mobileLayout || ''} ${className}`;
      case 'tablet':
        return `responsive-layout tablet-layout ${tabletLayout || ''} ${className}`;
      default:
        return `responsive-layout desktop-layout ${desktopLayout || ''} ${className}`;
    }
  };
  
  return (
    <div className={getLayoutClass()}>
      {children}
    </div>
  );
};

// Responsive grid system
export const ResponsiveGrid = ({ 
  items, 
  renderItem, 
  minItemWidth = 250,
  gap = 16,
  className = '' 
}) => {
  const [containerWidth, setContainerWidth] = useState(0);
  const { isMobile, isTablet } = useResponsive();
  
  useEffect(() => {
    const updateWidth = () => {
      const container = document.querySelector(`.responsive-grid.${className}`);
      if (container) {
        setContainerWidth(container.offsetWidth);
      }
    };
    
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, [className]);
  
  const columns = useMemo(() => {
    if (isMobile) return 1;
    if (isTablet) return 2;
    return Math.floor(containerWidth / (minItemWidth + gap)) || 1;
  }, [containerWidth, minItemWidth, gap, isMobile, isTablet]);
  
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gap: `${gap}px`,
    width: '100%'
  };
  
  return (
    <div className={`responsive-grid ${className}`} style={gridStyle}>
      {items.map((item, index) => (
        <div key={index} className="grid-item">
          {renderItem(item, index)}
        </div>
      ))}
    </div>
  );
};

// Drag and drop utilities
const DragDropTypes = {
  WIDGET: 'widget',
  CARD: 'card',
  NODE: 'node',
  FILE: 'file'
};

// Draggable component wrapper
export const DraggableItem = ({ 
  type = DragDropTypes.WIDGET, 
  item, 
  children, 
  onDragStart,
  onDragEnd,
  canDrag = true 
}) => {
  const [{ isDragging }, drag] = useDrag({
    type,
    item: () => {
      if (onDragStart) onDragStart(item);
      return { ...item, id: item.id || Math.random().toString(36) };
    },
    end: (draggedItem, monitor) => {
      if (onDragEnd) onDragEnd(draggedItem, monitor.didDrop());
    },
    canDrag,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });
  
  return (
    <div
      ref={drag}
      className={`draggable-item ${isDragging ? 'dragging' : ''} ${!canDrag ? 'disabled' : ''}`}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: canDrag ? 'move' : 'default'
      }}
    >
      {children}
    </div>
  );
};

// Drop zone component
export const DropZone = ({ 
  acceptedTypes = [DragDropTypes.WIDGET], 
  onDrop, 
  children, 
  className = '',
  canDrop = true 
}) => {
  const [{ isOver, canDropHere }, drop] = useDrop({
    accept: acceptedTypes,
    drop: (item, monitor) => {
      if (onDrop && canDrop) {
        onDrop(item, monitor.getDropResult());
      }
    },
    canDrop: () => canDrop,
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDropHere: monitor.canDrop(),
    }),
  });
  
  const dropZoneClass = `drop-zone ${className} ${
    isOver && canDropHere ? 'drag-over' : ''
  } ${canDropHere ? 'can-drop' : 'cannot-drop'}`;
  
  return (
    <div ref={drop} className={dropZoneClass}>
      {children}
      {isOver && canDropHere && (
        <div className="drop-indicator">Drop here</div>
      )}
    </div>
  );
};

// Sortable list component
export const SortableList = ({ 
  items, 
  onReorder, 
  renderItem, 
  keyExtractor = (item, index) => item.id || index 
}) => {
  const moveItem = useCallback((dragIndex, hoverIndex) => {
    const dragItem = items[dragIndex];
    const newItems = [...items];
    newItems.splice(dragIndex, 1);
    newItems.splice(hoverIndex, 0, dragItem);
    onReorder(newItems);
  }, [items, onReorder]);
  
  return (
    <div className="sortable-list">
      {items.map((item, index) => (
        <SortableItem
          key={keyExtractor(item, index)}
          index={index}
          item={item}
          moveItem={moveItem}
        >
          {renderItem(item, index)}
        </SortableItem>
      ))}
    </div>
  );
};

// Sortable item component
const SortableItem = ({ item, index, moveItem, children }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'SORTABLE_ITEM',
    item: { index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });
  
  const [, drop] = useDrop({
    accept: 'SORTABLE_ITEM',
    hover: (draggedItem) => {
      if (draggedItem.index !== index) {
        moveItem(draggedItem.index, index);
        draggedItem.index = index;
      }
    },
  });
  
  return (
    <div
      ref={(node) => drag(drop(node))}
      className={`sortable-item ${isDragging ? 'dragging' : ''}`}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      {children}
    </div>
  );
};

// Advanced search functionality
export class AdvancedSearch {
  constructor(options = {}) {
    this.options = {
      threshold: 0.3,
      includeScore: true,
      includeMatches: true,
      ignoreLocation: true,
      findAllMatches: true,
      minMatchCharLength: 2,
      ...options
    };
    
    this.searchIndex = null;
    this.searchHistory = [];
    this.savedSearches = [];
    this.filters = {};
    this.sortOptions = {
      field: 'relevance',
      direction: 'desc'
    };
  }
  
  initialize(data, searchFields) {
    const fuseOptions = {
      ...this.options,
      keys: searchFields.map(field => 
        typeof field === 'string' ? field : field
      )
    };
    
    this.searchIndex = new Fuse(data, fuseOptions);
    return this;
  }
  
  search(query, options = {}) {
    if (!this.searchIndex || !query.trim()) {
      return { results: [], query, totalResults: 0 };
    }
    
    // Add to search history
    this.addToHistory(query);
    
    // Perform search
    let results = this.searchIndex.search(query);
    
    // Apply filters
    if (Object.keys(this.filters).length > 0) {
      results = this.applyFilters(results);
    }
    
    // Apply sorting
    results = this.applySorting(results);
    
    // Apply pagination
    const page = options.page || 1;
    const pageSize = options.pageSize || 50;
    const startIndex = (page - 1) * pageSize;
    const paginatedResults = results.slice(startIndex, startIndex + pageSize);
    
    return {
      results: paginatedResults,
      query,
      totalResults: results.length,
      page,
      pageSize,
      totalPages: Math.ceil(results.length / pageSize),
      searchTime: Date.now()
    };
  }
  
  applyFilters(results) {
    return results.filter(result => {
      const item = result.item;
      
      return Object.entries(this.filters).every(([field, filterConfig]) => {
        const value = this.getNestedValue(item, field);
        
        switch (filterConfig.type) {
          case 'exact':
            return value === filterConfig.value;
          case 'contains':
            return String(value).toLowerCase().includes(String(filterConfig.value).toLowerCase());
          case 'range':
            return value >= filterConfig.min && value <= filterConfig.max;
          case 'in':
            return filterConfig.values.includes(value);
          case 'regex':
            return new RegExp(filterConfig.pattern, filterConfig.flags || 'i').test(String(value));
          default:
            return true;
        }
      });
    });
  }
  
  applySorting(results) {
    return results.sort((a, b) => {
      const { field, direction } = this.sortOptions;
      
      let valueA, valueB;
      
      if (field === 'relevance') {
        valueA = a.score;
        valueB = b.score;
      } else {
        valueA = this.getNestedValue(a.item, field);
        valueB = this.getNestedValue(b.item, field);
      }
      
      // Handle different data types
      if (typeof valueA === 'string' && typeof valueB === 'string') {
        valueA = valueA.toLowerCase();
        valueB = valueB.toLowerCase();
      }
      
      let comparison = 0;
      if (valueA > valueB) comparison = 1;
      if (valueA < valueB) comparison = -1;
      
      return direction === 'asc' ? comparison : -comparison;
    });
  }
  
  getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }
  
  addFilter(field, type, value, options = {}) {
    this.filters[field] = { type, value, ...options };
    return this;
  }
  
  removeFilter(field) {
    delete this.filters[field];
    return this;
  }
  
  clearFilters() {
    this.filters = {};
    return this;
  }
  
  setSorting(field, direction = 'asc') {
    this.sortOptions = { field, direction };
    return this;
  }
  
  addToHistory(query) {
    const historyItem = {
      query,
      timestamp: Date.now(),
      resultsCount: 0 // Will be updated after search
    };
    
    this.searchHistory.unshift(historyItem);
    
    // Keep only last 50 searches
    if (this.searchHistory.length > 50) {
      this.searchHistory = this.searchHistory.slice(0, 50);
    }
  }
  
  saveSearch(name, query, filters = {}) {
    const savedSearch = {
      id: Math.random().toString(36).substr(2, 9),
      name,
      query,
      filters,
      savedAt: Date.now()
    };
    
    this.savedSearches.push(savedSearch);
    return savedSearch.id;
  }
  
  loadSavedSearch(searchId) {
    const savedSearch = this.savedSearches.find(s => s.id === searchId);
    if (savedSearch) {
      this.filters = { ...savedSearch.filters };
      return savedSearch.query;
    }
    return null;
  }
  
  getSuggestions(query, limit = 5) {
    if (!query.trim()) return [];
    
    const suggestions = [];
    
    // Add from search history
    const historyMatches = this.searchHistory
      .filter(item => item.query.toLowerCase().includes(query.toLowerCase()))
      .slice(0, limit)
      .map(item => ({
        text: item.query,
        type: 'history',
        score: item.resultsCount
      }));
    
    suggestions.push(...historyMatches);
    
    // Add from saved searches
    const savedMatches = this.savedSearches
      .filter(item => 
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.query.toLowerCase().includes(query.toLowerCase())
      )
      .slice(0, limit - suggestions.length)
      .map(item => ({
        text: item.query,
        type: 'saved',
        name: item.name
      }));
    
    suggestions.push(...savedMatches);
    
    return suggestions.slice(0, limit);
  }
  
  getSearchAnalytics() {
    return {
      totalSearches: this.searchHistory.length,
      uniqueQueries: new Set(this.searchHistory.map(h => h.query)).size,
      savedSearches: this.savedSearches.length,
      topQueries: this.getTopQueries(),
      averageResultsPerSearch: this.searchHistory.reduce(
        (sum, h) => sum + h.resultsCount, 0
      ) / this.searchHistory.length || 0
    };
  }
  
  getTopQueries(limit = 10) {
    const queryCounts = {};
    this.searchHistory.forEach(h => {
      queryCounts[h.query] = (queryCounts[h.query] || 0) + 1;
    });
    
    return Object.entries(queryCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, limit)
      .map(([query, count]) => ({ query, count }));
  }
}

// Advanced search hook
export const useAdvancedSearch = (data, searchFields, options = {}) => {
  const [searchInstance] = useState(() => new AdvancedSearch(options));
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Initialize search index when data changes
  useEffect(() => {
    if (data && searchFields) {
      searchInstance.initialize(data, searchFields);
    }
  }, [data, searchFields, searchInstance]);
  
  // Debounced search function
  const debouncedSearch = useMemo(
    () => debounce((query, options) => {
      if (!query.trim()) {
        setSearchResults(null);
        setLoading(false);
        return;
      }
      
      const results = searchInstance.search(query, options);
      setSearchResults(results);
      setLoading(false);
    }, 300),
    [searchInstance]
  );
  
  const search = useCallback((query, options = {}) => {
    setLoading(true);
    debouncedSearch(query, options);
  }, [debouncedSearch]);
  
  const addFilter = useCallback((field, type, value, options = {}) => {
    searchInstance.addFilter(field, type, value, options);
  }, [searchInstance]);
  
  const removeFilter = useCallback((field) => {
    searchInstance.removeFilter(field);
  }, [searchInstance]);
  
  const clearFilters = useCallback(() => {
    searchInstance.clearFilters();
  }, [searchInstance]);
  
  const setSorting = useCallback((field, direction = 'asc') => {
    searchInstance.setSorting(field, direction);
  }, [searchInstance]);
  
  const getSuggestions = useCallback((query, limit = 5) => {
    return searchInstance.getSuggestions(query, limit);
  }, [searchInstance]);
  
  return {
    search,
    searchResults,
    loading,
    addFilter,
    removeFilter,
    clearFilters,
    setSorting,
    getSuggestions,
    searchHistory: searchInstance.searchHistory,
    savedSearches: searchInstance.savedSearches,
    analytics: searchInstance.getSearchAnalytics()
  };
};

// Touch gesture utilities
export const useTouchGestures = () => {
  const [touchState, setTouchState] = useState({
    isTouch: false,
    startX: 0,
    startY: 0,
    currentX: 0,
    currentY: 0,
    direction: null
  });
  
  const handleTouchStart = useCallback((e) => {
    const touch = e.touches[0];
    setTouchState({
      isTouch: true,
      startX: touch.clientX,
      startY: touch.clientY,
      currentX: touch.clientX,
      currentY: touch.clientY,
      direction: null
    });
  }, []);
  
  const handleTouchMove = useCallback((e) => {
    if (!touchState.isTouch) return;
    
    const touch = e.touches[0];
    const deltaX = touch.clientX - touchState.startX;
    const deltaY = touch.clientY - touchState.startY;
    
    let direction = null;
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      direction = deltaX > 0 ? 'right' : 'left';
    } else {
      direction = deltaY > 0 ? 'down' : 'up';
    }
    
    setTouchState(prev => ({
      ...prev,
      currentX: touch.clientX,
      currentY: touch.clientY,
      direction
    }));
  }, [touchState.isTouch, touchState.startX, touchState.startY]);
  
  const handleTouchEnd = useCallback(() => {
    setTouchState(prev => ({ ...prev, isTouch: false }));
  }, []);
  
  return {
    touchState,
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd
  };
};

// Responsive drag and drop provider
export const ResponsiveDndProvider = ({ children }) => {
  const { isTouchDevice } = useResponsive();
  
  // Use different backends for touch vs mouse
  const backend = isTouchDevice ? TouchBackend : HTML5Backend;
  
  return (
    <DndProvider backend={backend}>
      {children}
    </DndProvider>
  );
};

export default {
  useResponsive,
  ResponsiveLayout,
  ResponsiveGrid,
  DraggableItem,
  DropZone,
  SortableList,
  AdvancedSearch,
  useAdvancedSearch,
  useTouchGestures,
  ResponsiveDndProvider
};
