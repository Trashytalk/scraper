import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  ToggleButton,
  ToggleButtonGroup,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Timeline,
  BarChart,
  PieChart,
  ShowChart,
  BubbleChart,
  Map,
  NetworkCheck,
  FilterList,
  Download,
  Fullscreen,
  Refresh,
  Settings,
  ZoomIn,
  ZoomOut,
  PlayArrow,
  Pause
} from '@mui/icons-material';
import * as d3 from 'd3';
import { useNotifications } from './NotificationSystem';

// Advanced Chart Component
export const AdvancedChart = ({ 
  data = [], 
  type = 'line', 
  title = '',
  width = 600,
  height = 400,
  animated = true,
  interactive = true,
  exportable = true 
}) => {
  const [chartRef, setChartRef] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const { showNotification } = useNotifications();

  useEffect(() => {
    if (chartRef && data.length > 0) {
      renderChart();
    }
  }, [chartRef, data, type, width, height]);

  const renderChart = () => {
    setLoading(true);
    
    // Clear previous chart
    d3.select(chartRef).selectAll("*").remove();

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const svg = d3.select(chartRef)
      .attr("width", width)
      .attr("height", height);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    switch (type) {
      case 'line':
        renderLineChart(g, data, chartWidth, chartHeight);
        break;
      case 'bar':
        renderBarChart(g, data, chartWidth, chartHeight);
        break;
      case 'area':
        renderAreaChart(g, data, chartWidth, chartHeight);
        break;
      case 'scatter':
        renderScatterPlot(g, data, chartWidth, chartHeight);
        break;
      case 'heatmap':
        renderHeatmap(g, data, chartWidth, chartHeight);
        break;
      default:
        renderLineChart(g, data, chartWidth, chartHeight);
    }

    setLoading(false);
  };

  const renderLineChart = (g, data, width, height) => {
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => new Date(d.timestamp)))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.value))
      .range([height, 0]);

    const line = d3.line()
      .x(d => xScale(new Date(d.timestamp)))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale));

    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add line with animation
    const path = g.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#2196f3")
      .attr("stroke-width", 2)
      .attr("d", line);

    if (animated) {
      const totalLength = path.node().getTotalLength();
      path
        .attr("stroke-dasharray", totalLength + " " + totalLength)
        .attr("stroke-dashoffset", totalLength)
        .transition()
        .duration(2000)
        .attr("stroke-dashoffset", 0);
    }

    // Add interactive dots
    if (interactive) {
      g.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", d => xScale(new Date(d.timestamp)))
        .attr("cy", d => yScale(d.value))
        .attr("r", 4)
        .attr("fill", "#2196f3")
        .on("mouseover", function(event, d) {
          d3.select(this).attr("r", 6);
          // Show tooltip
          showTooltip(event, d);
        })
        .on("mouseout", function() {
          d3.select(this).attr("r", 4);
          hideTooltip();
        });
    }
  };

  const renderBarChart = (g, data, width, height) => {
    const xScale = d3.scaleBand()
      .domain(data.map(d => d.label))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height, 0]);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale));

    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add bars with animation
    g.selectAll(".bar")
      .data(data)
      .enter().append("rect")
      .attr("class", "bar")
      .attr("x", d => xScale(d.label))
      .attr("width", xScale.bandwidth())
      .attr("fill", "#4caf50")
      .attr("y", height)
      .attr("height", 0)
      .transition()
      .duration(animated ? 1000 : 0)
      .attr("y", d => yScale(d.value))
      .attr("height", d => height - yScale(d.value));
  };

  const renderAreaChart = (g, data, width, height) => {
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => new Date(d.timestamp)))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height, 0]);

    const area = d3.area()
      .x(d => xScale(new Date(d.timestamp)))
      .y0(height)
      .y1(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale));

    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add area with gradient
    const gradient = g.append("defs")
      .append("linearGradient")
      .attr("id", "area-gradient")
      .attr("gradientUnits", "userSpaceOnUse")
      .attr("x1", 0).attr("y1", height)
      .attr("x2", 0).attr("y2", 0);

    gradient.append("stop")
      .attr("offset", "0%")
      .attr("stop-color", "#2196f3")
      .attr("stop-opacity", 0.1);

    gradient.append("stop")
      .attr("offset", "100%")
      .attr("stop-color", "#2196f3")
      .attr("stop-opacity", 0.8);

    g.append("path")
      .datum(data)
      .attr("fill", "url(#area-gradient)")
      .attr("d", area);
  };

  const renderScatterPlot = (g, data, width, height) => {
    const xScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.x))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.y))
      .range([height, 0]);

    const radiusScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.size || 1))
      .range([3, 12]);

    // Add axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(xScale));

    g.append("g")
      .call(d3.axisLeft(yScale));

    // Add circles
    g.selectAll(".bubble")
      .data(data)
      .enter().append("circle")
      .attr("class", "bubble")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", d => radiusScale(d.size || 1))
      .attr("fill", d => d.color || "#ff9800")
      .attr("opacity", 0.7)
      .on("mouseover", function(event, d) {
        d3.select(this).attr("opacity", 1);
        showTooltip(event, d);
      })
      .on("mouseout", function() {
        d3.select(this).attr("opacity", 0.7);
        hideTooltip();
      });
  };

  const renderHeatmap = (g, data, width, height) => {
    // Implementation for heatmap
    // This would require matrix data format
  };

  const showTooltip = (event, data) => {
    // Tooltip implementation
  };

  const hideTooltip = () => {
    // Hide tooltip implementation
  };

  const exportChart = () => {
    const svgData = new XMLSerializer().serializeToString(chartRef);
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = document.createElement("img");
    
    img.onload = function() {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      
      const link = document.createElement("a");
      link.download = `${title || 'chart'}.png`;
      link.href = canvas.toDataURL();
      link.click();
      
      showNotification('Chart exported successfully', 'success');
    };
    
    img.src = "data:image/svg+xml;base64," + btoa(svgData);
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">{title}</Typography>
          <Box>
            {exportable && (
              <Tooltip title="Export Chart">
                <IconButton onClick={exportChart}>
                  <Download />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title="Fullscreen">
              <IconButton onClick={() => setFullscreen(true)}>
                <Fullscreen />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Box sx={{ position: 'relative' }}>
          {loading && (
            <Box sx={{ 
              position: 'absolute', 
              top: '50%', 
              left: '50%', 
              transform: 'translate(-50%, -50%)',
              zIndex: 1
            }}>
              <CircularProgress />
            </Box>
          )}
          <svg ref={setChartRef} style={{ width: '100%', height: 'auto' }} />
        </Box>
      </CardContent>

      <Dialog 
        open={fullscreen} 
        onClose={() => setFullscreen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {title}
          <IconButton
            onClick={() => setFullscreen(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <AdvancedChart
            data={data}
            type={type}
            width={800}
            height={600}
            animated={animated}
            interactive={interactive}
            exportable={false}
          />
        </DialogContent>
      </Dialog>
    </Card>
  );
};

// Network Visualization Component
export const NetworkVisualization = ({ nodes = [], links = [], onNodeClick = () => {} }) => {
  const [svgRef, setSvgRef] = useState(null);
  const [simulation, setSimulation] = useState(null);

  useEffect(() => {
    if (svgRef && nodes.length > 0) {
      renderNetwork();
    }
  }, [svgRef, nodes, links]);

  const renderNetwork = () => {
    const svg = d3.select(svgRef);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 600;

    svg.attr("width", width).attr("height", height);

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .enter().append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", d => Math.sqrt(d.value || 1));

    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .enter().append("circle")
      .attr("r", d => d.size || 5)
      .attr("fill", d => d.color || "#69b3a2")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended))
      .on("click", (event, d) => onNodeClick(d));

    const label = svg.append("g")
      .selectAll("text")
      .data(nodes)
      .enter().append("text")
      .text(d => d.label)
      .attr("font-size", 12)
      .attr("dx", 15)
      .attr("dy", 4);

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      label
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    setSimulation(simulation);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Network Visualization
        </Typography>
        <svg ref={setSvgRef} style={{ width: '100%', border: '1px solid #ddd' }} />
      </CardContent>
    </Card>
  );
};

// Interactive Dashboard with Multiple Visualizations
export const AdvancedAnalyticsDashboard = () => {
  const [selectedMetric, setSelectedMetric] = useState('scraping_performance');
  const [dateRange, setDateRange] = useState([7, 30]); // days
  const [chartType, setChartType] = useState('line');
  const [realTimeEnabled, setRealTimeEnabled] = useState(true);
  const [data, setData] = useState([]);

  const metrics = [
    { id: 'scraping_performance', label: 'Scraping Performance', icon: <ShowChart /> },
    { id: 'success_rates', label: 'Success Rates', icon: <BarChart /> },
    { id: 'error_analysis', label: 'Error Analysis', icon: <PieChart /> },
    { id: 'resource_usage', label: 'Resource Usage', icon: <Timeline /> },
    { id: 'network_topology', label: 'Network Topology', icon: <NetworkCheck /> }
  ];

  const chartTypes = [
    { id: 'line', label: 'Line Chart', icon: <ShowChart /> },
    { id: 'bar', label: 'Bar Chart', icon: <BarChart /> },
    { id: 'area', label: 'Area Chart', icon: <Timeline /> },
    { id: 'scatter', label: 'Scatter Plot', icon: <BubbleChart /> }
  ];

  useEffect(() => {
    fetchData();
  }, [selectedMetric, dateRange]);

  const fetchData = async () => {
    // Simulate API call
    const mockData = generateMockData(selectedMetric, dateRange[1]);
    setData(mockData);
  };

  const generateMockData = (metric, days) => {
    const data = [];
    const now = new Date();
    
    for (let i = days; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      
      switch (metric) {
        case 'scraping_performance':
          data.push({
            timestamp: timestamp.toISOString(),
            value: Math.random() * 100 + 50,
            label: `Day ${days - i}`
          });
          break;
        case 'success_rates':
          data.push({
            label: `Day ${days - i}`,
            value: Math.random() * 30 + 70
          });
          break;
        case 'error_analysis':
          data.push({
            label: ['Timeout', 'Network', 'Parse', 'Auth', 'Rate Limit'][Math.floor(Math.random() * 5)],
            value: Math.random() * 20 + 5
          });
          break;
        default:
          data.push({
            timestamp: timestamp.toISOString(),
            value: Math.random() * 100,
            label: `Day ${days - i}`
          });
      }
    }
    
    return data;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Advanced Analytics Dashboard
      </Typography>

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Metric</InputLabel>
              <Select
                value={selectedMetric}
                onChange={(e) => setSelectedMetric(e.target.value)}
              >
                {metrics.map(metric => (
                  <MenuItem key={metric.id} value={metric.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {metric.icon}
                      {metric.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Chart Type</InputLabel>
              <Select
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
              >
                {chartTypes.map(type => (
                  <MenuItem key={type.id} value={type.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {type.icon}
                      {type.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography gutterBottom>Date Range (days): {dateRange[1]}</Typography>
            <Slider
              value={dateRange[1]}
              onChange={(e, value) => setDateRange([7, value])}
              min={7}
              max={90}
              marks={[
                { value: 7, label: '7d' },
                { value: 30, label: '30d' },
                { value: 90, label: '90d' }
              ]}
            />
          </Grid>

          <Grid item xs={12} md={2}>
            <FormControlLabel
              control={
                <Switch
                  checked={realTimeEnabled}
                  onChange={(e) => setRealTimeEnabled(e.target.checked)}
                />
              }
              label="Real-time"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Main Chart */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <AdvancedChart
            data={data}
            type={chartType}
            title={metrics.find(m => m.id === selectedMetric)?.label}
            width={600}
            height={400}
            animated={true}
            interactive={true}
          />
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Key Insights
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Performance
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {data.length > 0 ? Math.round(data.reduce((sum, d) => sum + d.value, 0) / data.length) : 0}%
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Trend
                  </Typography>
                  <Chip 
                    label={data.length > 1 && data[data.length - 1].value > data[0].value ? "Improving" : "Declining"}
                    color={data.length > 1 && data[data.length - 1].value > data[0].value ? "success" : "warning"}
                    size="small"
                  />
                </Box>

                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Data Points
                  </Typography>
                  <Typography variant="h6">
                    {data.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedAnalyticsDashboard;
