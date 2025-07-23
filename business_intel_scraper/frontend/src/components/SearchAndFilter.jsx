import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  TextField,
  InputAdornment,
  IconButton,
  Button,
  Chip,
  Menu,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Slider,
  Typography,
  Divider,
  Autocomplete,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  DateRange as DateRangeIcon,
  Category as CategoryIcon,
  Schedule as ScheduleIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const SearchAndFilter = ({ 
  data = [], 
  onFilteredDataChange, 
  placeholder = "Search...",
  searchFields = ['name', 'description'],
  filterConfig = {},
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [filterMenuAnchor, setFilterMenuAnchor] = useState(null);
  const [activeFilters, setActiveFilters] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);

  // Default filter configuration
  const defaultFilterConfig = {
    status: {
      type: 'select',
      label: 'Status',
      options: ['pending', 'running', 'completed', 'failed', 'cancelled'],
      icon: <ScheduleIcon />
    },
    dateRange: {
      type: 'dateRange',
      label: 'Date Range',
      icon: <DateRangeIcon />
    },
    category: {
      type: 'multiSelect',
      label: 'Category',
      options: [],
      icon: <CategoryIcon />
    },
    priority: {
      type: 'slider',
      label: 'Priority',
      min: 1,
      max: 10,
      icon: <TimelineIcon />
    }
  };

  const mergedFilterConfig = { ...defaultFilterConfig, ...filterConfig };

  // Extract unique values for filter options
  const extractFilterOptions = useCallback((field) => {
    const uniqueValues = [...new Set(
      data
        .map(item => item[field])
        .filter(value => value !== null && value !== undefined)
    )];
    return uniqueValues.sort();
  }, [data]);

  // Update filter options based on data
  useEffect(() => {
    Object.keys(mergedFilterConfig).forEach(key => {
      if (mergedFilterConfig[key].type === 'select' || 
          mergedFilterConfig[key].type === 'multiSelect') {
        if (!mergedFilterConfig[key].options.length) {
          mergedFilterConfig[key].options = extractFilterOptions(key);
        }
      }
    });
  }, [data, extractFilterOptions, mergedFilterConfig]);

  // Search functionality
  const searchFilter = useCallback((item) => {
    if (!searchTerm.trim()) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return searchFields.some(field => {
      const value = item[field];
      if (typeof value === 'string') {
        return value.toLowerCase().includes(searchLower);
      }
      if (typeof value === 'number') {
        return value.toString().includes(searchLower);
      }
      return false;
    });
  }, [searchTerm, searchFields]);

  // Filter functionality
  const applyFilters = useCallback((item) => {
    return Object.entries(filters).every(([key, value]) => {
      if (!value || (Array.isArray(value) && value.length === 0)) return true;
      
      const config = mergedFilterConfig[key];
      const itemValue = item[key];
      
      switch (config?.type) {
        case 'select':
          return itemValue === value;
        case 'multiSelect':
          return Array.isArray(value) ? value.includes(itemValue) : itemValue === value;
        case 'dateRange':
          if (!value.start && !value.end) return true;
          const itemDate = new Date(itemValue);
          if (value.start && itemDate < value.start) return false;
          if (value.end && itemDate > value.end) return false;
          return true;
        case 'slider':
          const [min, max] = Array.isArray(value) ? value : [value, value];
          return itemValue >= min && itemValue <= max;
        default:
          return true;
      }
    });
  }, [filters, mergedFilterConfig]);

  // Combined filtering
  const filteredData = useMemo(() => {
    return data.filter(item => searchFilter(item) && applyFilters(item));
  }, [data, searchFilter, applyFilters]);

  // Notify parent of filtered data changes
  useEffect(() => {
    onFilteredDataChange?.(filteredData);
  }, [filteredData, onFilteredDataChange]);

  // Update active filters display
  useEffect(() => {
    const active = [];
    
    if (searchTerm.trim()) {
      active.push({
        type: 'search',
        label: `Search: "${searchTerm}"`,
        value: searchTerm
      });
    }
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value && (Array.isArray(value) ? value.length > 0 : true)) {
        const config = mergedFilterConfig[key];
        let label = config?.label || key;
        
        if (Array.isArray(value)) {
          label += `: ${value.join(', ')}`;
        } else if (typeof value === 'object' && value.start && value.end) {
          label += `: ${value.start.toLocaleDateString()} - ${value.end.toLocaleDateString()}`;
        } else {
          label += `: ${value}`;
        }
        
        active.push({
          type: 'filter',
          key,
          label,
          value
        });
      }
    });
    
    setActiveFilters(active);
  }, [searchTerm, filters, mergedFilterConfig]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleClearSearch = () => {
    setSearchTerm('');
  };

  const handleClearFilter = (filterKey) => {
    setFilters(prev => {
      const updated = { ...prev };
      delete updated[filterKey];
      return updated;
    });
  };

  const handleClearAllFilters = () => {
    setSearchTerm('');
    setFilters({});
  };

  const handleSaveSearch = () => {
    const searchConfig = {
      id: Date.now(),
      name: `Search ${savedSearches.length + 1}`,
      searchTerm,
      filters,
      timestamp: new Date()
    };
    
    setSavedSearches(prev => [...prev, searchConfig]);
  };

  const handleLoadSearch = (searchConfig) => {
    setSearchTerm(searchConfig.searchTerm);
    setFilters(searchConfig.filters);
    setFilterMenuAnchor(null);
  };

  const renderFilterControl = (key, config) => {
    const value = filters[key];
    
    switch (config.type) {
      case 'select':
        return (
          <Autocomplete
            options={config.options}
            value={value || ''}
            onChange={(_, newValue) => handleFilterChange(key, newValue)}
            renderInput={(params) => (
              <TextField {...params} label={config.label} size="small" />
            )}
            sx={{ minWidth: 200 }}
          />
        );
      
      case 'multiSelect':
        return (
          <Autocomplete
            multiple
            options={config.options}
            value={value || []}
            onChange={(_, newValue) => handleFilterChange(key, newValue)}
            renderInput={(params) => (
              <TextField {...params} label={config.label} size="small" />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip variant="outlined" label={option} {...getTagProps({ index })} />
              ))
            }
            sx={{ minWidth: 250 }}
          />
        );
      
      case 'dateRange':
        return (
          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <DatePicker
                label="Start Date"
                value={value?.start || null}
                onChange={(newValue) => 
                  handleFilterChange(key, { ...value, start: newValue })
                }
                slotProps={{ textField: { size: 'small' } }}
              />
              <DatePicker
                label="End Date"
                value={value?.end || null}
                onChange={(newValue) => 
                  handleFilterChange(key, { ...value, end: newValue })
                }
                slotProps={{ textField: { size: 'small' } }}
              />
            </Box>
          </LocalizationProvider>
        );
      
      case 'slider':
        return (
          <Box sx={{ minWidth: 200, px: 2 }}>
            <Typography variant="body2" gutterBottom>
              {config.label}: {Array.isArray(value) ? `${value[0]} - ${value[1]}` : config.min + ' - ' + config.max}
            </Typography>
            <Slider
              value={value || [config.min, config.max]}
              onChange={(_, newValue) => handleFilterChange(key, newValue)}
              valueLabelDisplay="auto"
              min={config.min}
              max={config.max}
              step={1}
            />
          </Box>
        );
      
      default:
        return null;
    }
  };

  return (
    <Box className={className}>
      {/* Search Bar */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <TextField
          fullWidth
          placeholder={placeholder}
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton onClick={handleClearSearch} size="small">
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            )
          }}
          size="small"
        />
        
        <Tooltip title="Filters">
          <IconButton
            onClick={(e) => setFilterMenuAnchor(e.currentTarget)}
            color={Object.keys(filters).length > 0 ? 'primary' : 'default'}
          >
            <Badge badgeContent={Object.keys(filters).length} color="primary">
              <FilterIcon />
            </Badge>
          </IconButton>
        </Tooltip>
      </Box>

      {/* Active Filters */}
      {activeFilters.length > 0 && (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
          {activeFilters.map((filter, index) => (
            <Chip
              key={index}
              label={filter.label}
              onDelete={
                filter.type === 'search' 
                  ? handleClearSearch 
                  : () => handleClearFilter(filter.key)
              }
              color={filter.type === 'search' ? 'primary' : 'default'}
              variant="outlined"
              size="small"
            />
          ))}
          {activeFilters.length > 1 && (
            <Button
              size="small"
              onClick={handleClearAllFilters}
              startIcon={<ClearIcon />}
            >
              Clear All
            </Button>
          )}
        </Box>
      )}

      {/* Filter Menu */}
      <Menu
        anchorEl={filterMenuAnchor}
        open={Boolean(filterMenuAnchor)}
        onClose={() => setFilterMenuAnchor(null)}
        PaperProps={{
          sx: { minWidth: 400, maxWidth: 600, maxHeight: 500, overflow: 'auto' }
        }}
      >
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          
          {Object.entries(mergedFilterConfig).map(([key, config]) => (
            <Box key={key} sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {config.icon}
                <Typography variant="subtitle2">
                  {config.label}
                </Typography>
              </Box>
              {renderFilterControl(key, config)}
            </Box>
          ))}
          
          <Divider sx={{ my: 2 }} />
          
          {/* Saved Searches */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">
                Saved Searches ({savedSearches.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              {savedSearches.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No saved searches
                </Typography>
              ) : (
                savedSearches.map((search) => (
                  <MenuItem
                    key={search.id}
                    onClick={() => handleLoadSearch(search)}
                  >
                    <Box>
                      <Typography variant="body2">{search.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {search.timestamp.toLocaleDateString()}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))
              )}
              <Divider sx={{ my: 1 }} />
              <Button
                size="small"
                onClick={handleSaveSearch}
                disabled={!searchTerm && Object.keys(filters).length === 0}
              >
                Save Current Search
              </Button>
            </AccordionDetails>
          </Accordion>
        </Box>
      </Menu>

      {/* Results Summary */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {filteredData.length} of {data.length} items
        </Typography>
        
        {(searchTerm || Object.keys(filters).length > 0) && (
          <Typography variant="body2" color="primary">
            {((filteredData.length / data.length) * 100).toFixed(1)}% match
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default SearchAndFilter;
