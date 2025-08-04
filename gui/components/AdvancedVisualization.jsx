import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ScatterPlot,
  Scatter,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Treemap,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import { DataGrid } from '@mui/x-data-grid';
import { Download, FilterList, Refresh, Settings } from '@mui/icons-material';

// Color schemes for different chart types
const COLOR_SCHEMES = {
  default: ['#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#00BCD4', '#FFC107', '#795548'],
  pastel: ['#FFD1DC', '#E1F5FE', '#F3E5F5', '#E8F5E8', '#FFF3E0', '#FFEBEE', '#E0F2F1', '#F9FBE7'],
  vibrant: ['#FF5722', '#2196F3', '#4CAF50', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4', '#FFC107'],
  monochrome: ['#212121', '#424242', '#616161', '#757575', '#9E9E9E', '#BDBDBD', '#E0E0E0', '#F5F5F5']
};

// Chart configuration options
const CHART_TYPES = [
  { value: 'line', label: 'Line Chart', component: LineChart },
  { value: 'area', label: 'Area Chart', component: AreaChart },
  { value: 'bar', label: 'Bar Chart', component: BarChart },
  { value: 'pie', label: 'Pie Chart', component: PieChart },
  { value: 'scatter', label: 'Scatter Plot', component: ScatterPlot },
  { value: 'radar', label: 'Radar Chart', component: RadarChart },
  { value: 'treemap', label: 'Treemap', component: Treemap }
];

// Advanced Chart Component with customization options
const AdvancedChart = ({ 
  data, 
  chartType = 'line', 
  title, 
  xAxisKey, 
  yAxisKeys = [], 
  colorScheme = 'default',
  height = 400,
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  customOptions = {},
  onDataPointClick,
  isLoading = false
}) => {
  const [localChartType, setLocalChartType] = useState(chartType);
  const [localColorScheme, setLocalColorScheme] = useState(colorScheme);
  const [animationEnabled, setAnimationEnabled] = useState(true);
  
  const colors = COLOR_SCHEMES[localColorScheme] || COLOR_SCHEMES.default;
  
  // Memoized chart data processing
  const processedData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    
    return data.map((item, index) => ({
      ...item,
      index,
      _id: item.id || index
    }));
  }, [data]);
  
  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Paper sx={{ p: 2, maxWidth: 300 }}>
          <Typography variant="subtitle2" gutterBottom>
            {label}
          </Typography>
          {payload.map((entry, index) => (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  backgroundColor: entry.color,
                  mr: 1,
                  borderRadius: '50%'
                }}
              />
              <Typography variant="body2">
                {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
              </Typography>
            </Box>
          ))}
        </Paper>
      );
    }
    return null;
  };
  
  // Render different chart types
  const renderChart = () => {
    if (isLoading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: height }}>
          <CircularProgress />
        </Box>
      );
    }
    
    if (!processedData.length) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: height }}>
          <Alert severity="info">No data available to display</Alert>
        </Box>
      );
    }
    
    const commonProps = {
      width: '100%',
      height: height,
      data: processedData,
      margin: { top: 20, right: 30, left: 20, bottom: 20 },
      onClick: onDataPointClick,
      ...customOptions
    };
    
    switch (localChartType) {
      case 'line':
        return (
          <ResponsiveContainer {...commonProps}>
            <LineChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey={xAxisKey} />
              <YAxis />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              {yAxisKeys.map((key, index) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  isAnimationActive={animationEnabled}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );
      
      case 'area':
        return (
          <ResponsiveContainer {...commonProps}>
            <AreaChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey={xAxisKey} />
              <YAxis />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              {yAxisKeys.map((key, index) => (
                <Area
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stackId="1"
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.6}
                  isAnimationActive={animationEnabled}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        );
      
      case 'bar':
        return (
          <ResponsiveContainer {...commonProps}>
            <BarChart {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey={xAxisKey} />
              <YAxis />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              {yAxisKeys.map((key, index) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={colors[index % colors.length]}
                  isAnimationActive={animationEnabled}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );
      
      case 'pie':
        const pieData = yAxisKeys.length > 0 ? 
          processedData.map(item => ({
            name: item[xAxisKey],
            value: item[yAxisKeys[0]]
          })) : [];
        
        return (
          <ResponsiveContainer {...commonProps}>
            <PieChart {...commonProps}>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                outerRadius={Math.min(height * 0.3, 120)}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                isAnimationActive={animationEnabled}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              {showTooltip && <Tooltip />}
            </PieChart>
          </ResponsiveContainer>
        );
      
      case 'scatter':
        return (
          <ResponsiveContainer {...commonProps}>
            <ScatterPlot {...commonProps}>
              {showGrid && <CartesianGrid strokeDasharray="3 3" />}
              <XAxis dataKey={xAxisKey} />
              <YAxis dataKey={yAxisKeys[0]} />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              <Scatter
                data={processedData}
                fill={colors[0]}
                isAnimationActive={animationEnabled}
              />
            </ScatterPlot>
          </ResponsiveContainer>
        );
      
      case 'radar':
        return (
          <ResponsiveContainer {...commonProps}>
            <RadarChart {...commonProps}>
              <PolarGrid />
              <PolarAngleAxis dataKey={xAxisKey} />
              <PolarRadiusAxis />
              {showTooltip && <Tooltip content={<CustomTooltip />} />}
              {showLegend && <Legend />}
              {yAxisKeys.map((key, index) => (
                <Radar
                  key={key}
                  name={key}
                  dataKey={key}
                  stroke={colors[index % colors.length]}
                  fill={colors[index % colors.length]}
                  fillOpacity={0.3}
                  isAnimationActive={animationEnabled}
                />
              ))}
            </RadarChart>
          </ResponsiveContainer>
        );
      
      default:
        return <Alert severity="error">Unsupported chart type: {localChartType}</Alert>;
    }
  };
  
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        {title && (
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
        )}
        
        {/* Chart Controls */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Chart Type</InputLabel>
              <Select
                value={localChartType}
                onChange={(e) => setLocalChartType(e.target.value)}
                label="Chart Type"
              >
                {CHART_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Color Scheme</InputLabel>
              <Select
                value={localColorScheme}
                onChange={(e) => setLocalColorScheme(e.target.value)}
                label="Color Scheme"
              >
                {Object.keys(COLOR_SCHEMES).map((scheme) => (
                  <MenuItem key={scheme} value={scheme}>
                    {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControlLabel
              control={
                <Switch
                  checked={animationEnabled}
                  onChange={(e) => setAnimationEnabled(e.target.checked)}
                />
              }
              label="Animation"
            />
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button size="small" startIcon={<Download />} variant="outlined">
                Export
              </Button>
              <Button size="small" startIcon={<Refresh />} variant="outlined">
                Refresh
              </Button>
            </Box>
          </Grid>
        </Grid>
        
        {/* Chart Display */}
        <Box sx={{ width: '100%', height: height }}>
          {renderChart()}
        </Box>
      </CardContent>
    </Card>
  );
};

// Data Table with advanced features
const AdvancedDataTable = ({ 
  data, 
  columns, 
  title,
  pagination = true,
  sorting = true,
  filtering = true,
  exportable = true,
  height = 400,
  onRowClick,
  isLoading = false
}) => {
  const [pageSize, setPageSize] = useState(10);
  const [searchText, setSearchText] = useState('');
  const [filterModel, setFilterModel] = useState({ items: [] });
  const [sortModel, setSortModel] = useState([]);
  
  // Memoized filtered data
  const filteredData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    
    let filtered = data;
    
    // Apply search filter
    if (searchText) {
      filtered = filtered.filter(row =>
        Object.values(row).some(value =>
          String(value).toLowerCase().includes(searchText.toLowerCase())
        )
      );
    }
    
    return filtered;
  }, [data, searchText]);
  
  // Export functionality
  const handleExport = useCallback((format) => {
    const dataToExport = filteredData;
    
    if (format === 'csv') {
      const csv = [
        columns.map(col => col.headerName).join(','),
        ...dataToExport.map(row =>
          columns.map(col => row[col.field] || '').join(',')
        )
      ].join('\n');
      
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title || 'data'}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'json') {
      const json = JSON.stringify(dataToExport, null, 2);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${title || 'data'}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }, [filteredData, columns, title]);
  
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        {title && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              {title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                label={`${filteredData.length} records`} 
                color="primary" 
                variant="outlined" 
                size="small"
              />
              {exportable && (
                <>
                  <Button 
                    size="small" 
                    onClick={() => handleExport('csv')}
                    startIcon={<Download />}
                  >
                    CSV
                  </Button>
                  <Button 
                    size="small" 
                    onClick={() => handleExport('json')}
                    startIcon={<Download />}
                  >
                    JSON
                  </Button>
                </>
              )}
            </Box>
          </Box>
        )}
        
        <Box sx={{ height: height, width: '100%' }}>
          <DataGrid
            rows={filteredData}
            columns={columns}
            pageSize={pageSize}
            onPageSizeChange={setPageSize}
            rowsPerPageOptions={[5, 10, 25, 50, 100]}
            pagination={pagination}
            sortingOrder={sorting ? ['desc', 'asc'] : []}
            sortModel={sortModel}
            onSortModelChange={setSortModel}
            filterModel={filterModel}
            onFilterModelChange={setFilterModel}
            disableColumnFilter={!filtering}
            disableColumnMenu={false}
            loading={isLoading}
            onRowClick={onRowClick}
            sx={{
              '& .MuiDataGrid-cell:hover': {
                backgroundColor: 'action.hover',
              },
              '& .MuiDataGrid-row:hover': {
                backgroundColor: 'action.hover',
              }
            }}
            components={{
              Toolbar: filtering ? () => (
                <Box sx={{ p: 1 }}>
                  <input
                    placeholder="Search..."
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      width: '200px'
                    }}
                  />
                </Box>
              ) : undefined
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

// Dashboard with multiple visualizations
const AdvancedVisualizationDashboard = ({ data, config = {} }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [refreshInterval, setRefreshInterval] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(false);
  
  // Auto-refresh logic
  useEffect(() => {
    let interval;
    if (autoRefresh && refreshInterval > 0) {
      interval = setInterval(() => {
        // Trigger data refresh
        if (config.onRefresh) {
          config.onRefresh();
        }
      }, refreshInterval * 1000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, config]);
  
  // Sample visualization configurations
  const visualizations = [
    {
      type: 'chart',
      title: 'Scraping Jobs Over Time',
      chartType: 'line',
      xAxisKey: 'date',
      yAxisKeys: ['jobs_completed', 'jobs_failed'],
      height: 300
    },
    {
      type: 'chart',
      title: 'Success Rate by Category',
      chartType: 'bar',
      xAxisKey: 'category',
      yAxisKeys: ['success_rate'],
      height: 300
    },
    {
      type: 'chart',
      title: 'Data Distribution',
      chartType: 'pie',
      xAxisKey: 'category',
      yAxisKeys: ['count'],
      height: 300
    },
    {
      type: 'table',
      title: 'Recent Jobs',
      columns: [
        { field: 'id', headerName: 'ID', width: 100 },
        { field: 'name', headerName: 'Job Name', width: 200 },
        { field: 'status', headerName: 'Status', width: 120 },
        { field: 'created_at', headerName: 'Created', width: 180 },
        { field: 'duration', headerName: 'Duration', width: 120 }
      ],
      height: 300
    }
  ];
  
  return (
    <Box sx={{ p: 3 }}>
      {/* Dashboard Controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Data Visualization Dashboard
        </Typography>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Time Range</InputLabel>
              <Select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                label="Time Range"
              >
                <MenuItem value="1d">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
                <MenuItem value="90d">Last 90 Days</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
              }
              label="Auto Refresh"
            />
          </Grid>
          
          {autoRefresh && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography gutterBottom>Refresh Interval (seconds)</Typography>
              <Slider
                value={refreshInterval}
                onChange={(e, newValue) => setRefreshInterval(newValue)}
                min={5}
                max={300}
                step={5}
                marks={[
                  { value: 30, label: '30s' },
                  { value: 60, label: '1m' },
                  { value: 300, label: '5m' }
                ]}
                valueLabelDisplay="auto"
              />
            </Grid>
          )}
          
          <Grid item xs={12} sm={6} md={3}>
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => config.onRefresh && config.onRefresh()}
              fullWidth
            >
              Refresh Now
            </Button>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Visualizations Grid */}
      <Grid container spacing={3}>
        {visualizations.map((viz, index) => (
          <Grid item xs={12} lg={6} key={index}>
            {viz.type === 'chart' ? (
              <AdvancedChart
                data={data}
                title={viz.title}
                chartType={viz.chartType}
                xAxisKey={viz.xAxisKey}
                yAxisKeys={viz.yAxisKeys}
                height={viz.height}
                isLoading={config.isLoading}
              />
            ) : (
              <AdvancedDataTable
                data={data}
                columns={viz.columns}
                title={viz.title}
                height={viz.height}
                isLoading={config.isLoading}
              />
            )}
          </Grid>
        ))}
      </Grid>
      
      {/* Summary Statistics */}
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Summary Statistics
        </Typography>
        <Grid container spacing={2}>
          {config.summaryStats && Object.entries(config.summaryStats).map(([key, value]) => (
            <Grid item xs={6} sm={4} md={2} key={key}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', pb: '16px !important' }}>
                  <Typography variant="h4" color="primary">
                    {typeof value === 'number' ? value.toLocaleString() : value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
};

export {
  AdvancedChart,
  AdvancedDataTable,
  AdvancedVisualizationDashboard
};
