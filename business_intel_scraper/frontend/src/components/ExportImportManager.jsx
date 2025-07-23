import React, { useState, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
  FormControlLabel,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  FileDownload as ExportIcon,
  FileUpload as ImportIcon,
  Description as FileIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Schedule as ScheduleIcon,
  CloudDownload,
  CloudUpload,
  DataObject
} from '@mui/icons-material';
import { useNotifications } from './NotificationSystem';

const ExportImportManager = ({ data = [], dataType = 'jobs', onImportComplete }) => {
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [exportConfig, setExportConfig] = useState({
    format: 'json',
    includeMetadata: true,
    dateRange: 'all',
    fields: [],
    compressed: false
  });
  const [importConfig, setImportConfig] = useState({
    format: 'auto',
    mergeMode: 'append',
    validateData: true,
    createBackup: true
  });
  const [loading, setLoading] = useState(false);
  const [importResults, setImportResults] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const { showSuccess, showError, showWarning, showInfo } = useNotifications();

  // Export formats configuration
  const exportFormats = [
    { value: 'json', label: 'JSON', description: 'JavaScript Object Notation' },
    { value: 'csv', label: 'CSV', description: 'Comma Separated Values' },
    { value: 'xlsx', label: 'Excel', description: 'Microsoft Excel Spreadsheet' },
    { value: 'xml', label: 'XML', description: 'Extensible Markup Language' },
    { value: 'pdf', label: 'PDF Report', description: 'Formatted PDF Document' }
  ];

  // Available data fields for export
  const getAvailableFields = () => {
    if (!data || data.length === 0) return [];
    
    const sampleItem = data[0];
    return Object.keys(sampleItem).map(key => ({
      key,
      label: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      selected: true
    }));
  };

  const [availableFields, setAvailableFields] = useState(getAvailableFields());

  React.useEffect(() => {
    setAvailableFields(getAvailableFields());
  }, [data]);

  const handleExport = async () => {
    if (!data || data.length === 0) {
      showWarning('No data available to export');
      return;
    }

    setLoading(true);
    try {
      // Filter data based on configuration
      let filteredData = data;
      
      // Apply date range filter if applicable
      if (exportConfig.dateRange !== 'all' && data[0]?.created_at) {
        const now = new Date();
        const daysBack = exportConfig.dateRange === 'week' ? 7 : 
                         exportConfig.dateRange === 'month' ? 30 : 
                         exportConfig.dateRange === 'year' ? 365 : 0;
        
        if (daysBack > 0) {
          const cutoffDate = new Date(now.getTime() - (daysBack * 24 * 60 * 60 * 1000));
          filteredData = data.filter(item => new Date(item.created_at) >= cutoffDate);
        }
      }

      // Filter fields if specified
      const selectedFields = availableFields.filter(f => f.selected).map(f => f.key);
      if (selectedFields.length > 0) {
        filteredData = filteredData.map(item => {
          const filtered = {};
          selectedFields.forEach(field => {
            filtered[field] = item[field];
          });
          return filtered;
        });
      }

      // Add metadata if requested
      if (exportConfig.includeMetadata) {
        const metadata = {
          exportDate: new Date().toISOString(),
          totalRecords: filteredData.length,
          format: exportConfig.format,
          dataType: dataType,
          fields: selectedFields
        };
        
        if (exportConfig.format === 'json') {
          filteredData = {
            metadata,
            data: filteredData
          };
        }
      }

      // Generate export based on format
      await generateExport(filteredData, exportConfig.format);
      
      showSuccess(`Successfully exported ${Array.isArray(filteredData) ? filteredData.length : filteredData.data?.length || 0} records`);
      setExportDialogOpen(false);
      
    } catch (error) {
      console.error('Export failed:', error);
      showError(`Export failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const generateExport = async (data, format) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${dataType}_export_${timestamp}`;
    
    switch (format) {
      case 'json':
        downloadFile(
          JSON.stringify(data, null, 2),
          `${filename}.json`,
          'application/json'
        );
        break;
        
      case 'csv':
        const csvContent = convertToCSV(Array.isArray(data) ? data : data.data);
        downloadFile(csvContent, `${filename}.csv`, 'text/csv');
        break;
        
      case 'xlsx':
        // Would integrate with a library like xlsx or ExcelJS
        showInfo('Excel export feature coming soon');
        break;
        
      case 'xml':
        const xmlContent = convertToXML(Array.isArray(data) ? data : data.data);
        downloadFile(xmlContent, `${filename}.xml`, 'application/xml');
        break;
        
      case 'pdf':
        // Would integrate with a PDF generation library
        showInfo('PDF export feature coming soon');
        break;
        
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  };

  const convertToCSV = (data) => {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
      const values = headers.map(header => {
        const value = row[header];
        // Escape values that contain commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value || '';
      });
      csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
  };

  const convertToXML = (data) => {
    if (!data || data.length === 0) return '<data></data>';
    
    const xmlRows = data.map(item => {
      const itemXml = Object.entries(item).map(([key, value]) => {
        return `  <${key}>${value || ''}</${key}>`;
      }).join('\n');
      return `<item>\n${itemXml}\n</item>`;
    });
    
    return `<?xml version="1.0" encoding="UTF-8"?>\n<data>\n${xmlRows.join('\n')}\n</data>`;
  };

  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      
      // Auto-detect format
      const extension = file.name.split('.').pop().toLowerCase();
      if (['json', 'csv', 'xml'].includes(extension)) {
        setImportConfig(prev => ({ ...prev, format: extension }));
      }
    }
  };

  const handleImport = async () => {
    if (!selectedFile) {
      showWarning('Please select a file to import');
      return;
    }

    setLoading(true);
    setImportResults(null);
    
    try {
      const fileContent = await readFile(selectedFile);
      const parsedData = await parseImportData(fileContent, importConfig.format);
      
      // Validate data if requested
      if (importConfig.validateData) {
        const validation = validateImportData(parsedData);
        if (!validation.isValid) {
          throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
        }
      }
      
      // Create backup if requested
      if (importConfig.createBackup && data.length > 0) {
        await generateExport(data, 'json');
        showInfo('Backup created before import');
      }
      
      // Process import based on merge mode
      let finalData;
      switch (importConfig.mergeMode) {
        case 'append':
          finalData = [...data, ...parsedData];
          break;
        case 'replace':
          finalData = parsedData;
          break;
        case 'merge':
          // Merge by ID or name
          finalData = mergeData(data, parsedData);
          break;
        default:
          finalData = parsedData;
      }
      
      setImportResults({
        success: true,
        recordsImported: parsedData.length,
        totalRecords: finalData.length,
        duplicatesFound: data.length + parsedData.length - finalData.length
      });
      
      // Notify parent component
      if (onImportComplete) {
        onImportComplete(finalData);
      }
      
      showSuccess(`Successfully imported ${parsedData.length} records`);
      
    } catch (error) {
      console.error('Import failed:', error);
      setImportResults({
        success: false,
        error: error.message
      });
      showError(`Import failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const readFile = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  };

  const parseImportData = async (content, format) => {
    switch (format) {
      case 'json':
      case 'auto':
        try {
          const parsed = JSON.parse(content);
          return Array.isArray(parsed) ? parsed : parsed.data || [parsed];
        } catch (error) {
          if (format === 'auto') {
            // Try CSV
            return parseCSV(content);
          }
          throw new Error('Invalid JSON format');
        }
        
      case 'csv':
        return parseCSV(content);
        
      case 'xml':
        return parseXML(content);
        
      default:
        throw new Error(`Unsupported import format: ${format}`);
    }
  };

  const parseCSV = (content) => {
    const lines = content.split('\n').filter(line => line.trim());
    if (lines.length < 2) throw new Error('CSV must have at least header and one data row');
    
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim().replace(/"/g, ''));
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index] || '';
      });
      data.push(row);
    }
    
    return data;
  };

  const parseXML = (content) => {
    // Basic XML parsing - in production, would use DOMParser or xml2js
    const items = content.match(/<item>[\s\S]*?<\/item>/g) || [];
    return items.map(item => {
      const obj = {};
      const fields = item.match(/<(\w+)>(.*?)<\/\1>/g) || [];
      fields.forEach(field => {
        const match = field.match(/<(\w+)>(.*?)<\/\1>/);
        if (match) {
          obj[match[1]] = match[2];
        }
      });
      return obj;
    });
  };

  const validateImportData = (data) => {
    const errors = [];
    
    if (!Array.isArray(data)) {
      errors.push('Data must be an array');
    } else if (data.length === 0) {
      errors.push('No data found');
    } else {
      // Check required fields based on data type
      const requiredFields = dataType === 'jobs' ? ['name', 'url'] : [];
      requiredFields.forEach(field => {
        if (!data.every(item => item[field])) {
          errors.push(`Missing required field: ${field}`);
        }
      });
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  };

  const mergeData = (existing, incoming) => {
    const merged = [...existing];
    const existingIds = new Set(existing.map(item => item.id || item.name));
    
    incoming.forEach(item => {
      const id = item.id || item.name;
      if (!existingIds.has(id)) {
        merged.push(item);
      }
    });
    
    return merged;
  };

  const handleFieldToggle = (fieldKey) => {
    setAvailableFields(prev => prev.map(field => 
      field.key === fieldKey ? { ...field, selected: !field.selected } : field
    ));
  };

  return (
    <Box>
      {/* Action Buttons */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ExportIcon sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">Export Data</Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Export your data in various formats for backup or external use.
              </Typography>
              <Button
                variant="contained"
                startIcon={<CloudDownload />}
                onClick={() => setExportDialogOpen(true)}
                disabled={!data || data.length === 0}
                fullWidth
              >
                Export {dataType} ({data?.length || 0} records)
              </Button>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ImportIcon sx={{ mr: 2, color: 'secondary.main' }} />
                <Typography variant="h6">Import Data</Typography>
              </Box>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Import data from external files to restore or merge with existing data.
              </Typography>
              <Button
                variant="outlined"
                startIcon={<CloudUpload />}
                onClick={() => setImportDialogOpen(true)}
                fullWidth
              >
                Import {dataType}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Export {dataType}</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Export Format</InputLabel>
                <Select
                  value={exportConfig.format}
                  label="Export Format"
                  onChange={(e) => setExportConfig(prev => ({ ...prev, format: e.target.value }))}
                >
                  {exportFormats.map(format => (
                    <MenuItem key={format.value} value={format.value}>
                      <Box>
                        <Typography variant="body2">{format.label}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {format.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Date Range</InputLabel>
                <Select
                  value={exportConfig.dateRange}
                  label="Date Range"
                  onChange={(e) => setExportConfig(prev => ({ ...prev, dateRange: e.target.value }))}
                >
                  <MenuItem value="all">All Records</MenuItem>
                  <MenuItem value="week">Last Week</MenuItem>
                  <MenuItem value="month">Last Month</MenuItem>
                  <MenuItem value="year">Last Year</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={exportConfig.includeMetadata}
                    onChange={(e) => setExportConfig(prev => ({ ...prev, includeMetadata: e.target.checked }))}
                  />
                }
                label="Include metadata (export date, record count, etc.)"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle2">
                    Select Fields to Export ({availableFields.filter(f => f.selected).length} selected)
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={1}>
                    {availableFields.map(field => (
                      <Grid item xs={12} sm={6} md={4} key={field.key}>
                        <FormControlLabel
                          control={
                            <Checkbox
                              checked={field.selected}
                              onChange={() => handleFieldToggle(field.key)}
                            />
                          }
                          label={field.label}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleExport}
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={16} /> : <ExportIcon />}
          >
            {loading ? 'Exporting...' : 'Export'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={importDialogOpen} onClose={() => setImportDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Import {dataType}</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".json,.csv,.xml"
                style={{ display: 'none' }}
              />
              <Button
                variant="outlined"
                onClick={() => fileInputRef.current?.click()}
                startIcon={<FileIcon />}
                fullWidth
                sx={{ mb: 2 }}
              >
                {selectedFile ? selectedFile.name : 'Select File'}
              </Button>
              
              {selectedFile && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                </Alert>
              )}
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>File Format</InputLabel>
                <Select
                  value={importConfig.format}
                  label="File Format"
                  onChange={(e) => setImportConfig(prev => ({ ...prev, format: e.target.value }))}
                >
                  <MenuItem value="auto">Auto-detect</MenuItem>
                  <MenuItem value="json">JSON</MenuItem>
                  <MenuItem value="csv">CSV</MenuItem>
                  <MenuItem value="xml">XML</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Merge Mode</InputLabel>
                <Select
                  value={importConfig.mergeMode}
                  label="Merge Mode"
                  onChange={(e) => setImportConfig(prev => ({ ...prev, mergeMode: e.target.value }))}
                >
                  <MenuItem value="append">Append (add to existing)</MenuItem>
                  <MenuItem value="replace">Replace (overwrite all)</MenuItem>
                  <MenuItem value="merge">Merge (update duplicates)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={importConfig.validateData}
                    onChange={(e) => setImportConfig(prev => ({ ...prev, validateData: e.target.checked }))}
                  />
                }
                label="Validate data before import"
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={importConfig.createBackup}
                    onChange={(e) => setImportConfig(prev => ({ ...prev, createBackup: e.target.checked }))}
                  />
                }
                label="Create backup before import"
              />
            </Grid>
            
            {importResults && (
              <Grid item xs={12}>
                <Alert 
                  severity={importResults.success ? 'success' : 'error'}
                  icon={importResults.success ? <SuccessIcon /> : <ErrorIcon />}
                >
                  {importResults.success ? (
                    <Box>
                      <Typography variant="body2">
                        Import completed successfully!
                      </Typography>
                      <Typography variant="caption">
                        Records imported: {importResults.recordsImported} | 
                        Total records: {importResults.totalRecords} |
                        Duplicates skipped: {importResults.duplicatesFound}
                      </Typography>
                    </Box>
                  ) : (
                    <Typography variant="body2">
                      {importResults.error}
                    </Typography>
                  )}
                </Alert>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleImport}
            variant="contained"
            disabled={loading || !selectedFile}
            startIcon={loading ? <CircularProgress size={16} /> : <ImportIcon />}
          >
            {loading ? 'Importing...' : 'Import'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExportImportManager;
