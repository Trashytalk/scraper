import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Paper,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  LinearProgress
} from '@mui/material';
import {
  Add,
  PlayArrow,
  Stop,
  Save,
  Delete,
  Edit,
  ExpandMore,
  DragIndicator,
  Link,
  Schedule,
  Webhook,
  DataObject,
  FilterList,
  Transform,
  Storage,
  Email,
  Notifications,
  Code,
  BugReport,
  Security,
  Speed,
  CheckCircle,
  Error,
  Warning,
  Settings,
  Visibility,
  Download,
  Upload
} from '@mui/icons-material';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useNotifications } from './NotificationSystem';

// Workflow Node Types
const NODE_TYPES = {
  trigger: {
    name: 'Trigger',
    icon: <Schedule />,
    color: '#4caf50',
    description: 'Start workflow execution',
    category: 'triggers'
  },
  scraper: {
    name: 'Web Scraper',
    icon: <DataObject />,
    color: '#2196f3',
    description: 'Extract data from websites',
    category: 'scrapers'
  },
  filter: {
    name: 'Data Filter',
    icon: <FilterList />,
    color: '#ff9800',
    description: 'Filter and validate data',
    category: 'processors'
  },
  transform: {
    name: 'Data Transform',
    icon: <Transform />,
    color: '#9c27b0',
    description: 'Transform and clean data',
    category: 'processors'
  },
  storage: {
    name: 'Data Storage',
    icon: <Storage />,
    color: '#607d8b',
    description: 'Store data to database',
    category: 'outputs'
  },
  notification: {
    name: 'Notification',
    icon: <Notifications />,
    color: '#f44336',
    description: 'Send notifications',
    category: 'outputs'
  },
  webhook: {
    name: 'Webhook',
    icon: <Webhook />,
    color: '#795548',
    description: 'Send HTTP requests',
    category: 'outputs'
  },
  condition: {
    name: 'Condition',
    icon: <Code />,
    color: '#3f51b5',
    description: 'Conditional logic',
    category: 'logic'
  }
};

// Workflow Node Component
const WorkflowNode = ({ node, onEdit, onDelete, onConnect, isDragging }) => {
  const nodeType = NODE_TYPES[node.type];

  return (
    <Card 
      sx={{ 
        mb: 1,
        opacity: isDragging ? 0.5 : 1,
        border: `2px solid ${nodeType.color}`,
        '&:hover': {
          boxShadow: 4
        }
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DragIndicator sx={{ color: 'text.secondary', cursor: 'grab' }} />
            <Box sx={{ color: nodeType.color }}>
              {nodeType.icon}
            </Box>
            <Box>
              <Typography variant="subtitle2" fontWeight="bold">
                {node.name || nodeType.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {nodeType.description}
              </Typography>
            </Box>
          </Box>
          
          <Box>
            <Tooltip title="Edit Node">
              <IconButton size="small" onClick={() => onEdit(node)}>
                <Edit />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Node">
              <IconButton size="small" onClick={() => onDelete(node.id)}>
                <Delete />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {node.config && Object.keys(node.config).length > 0 && (
          <Box sx={{ mt: 1 }}>
            {Object.entries(node.config).slice(0, 2).map(([key, value]) => (
              <Chip 
                key={key}
                label={`${key}: ${String(value).slice(0, 20)}${String(value).length > 20 ? '...' : ''}`}
                size="small"
                variant="outlined"
                sx={{ mr: 0.5, mb: 0.5 }}
              />
            ))}
          </Box>
        )}

        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            ID: {node.id}
          </Typography>
          <Chip 
            label={node.status || 'inactive'}
            size="small"
            color={node.status === 'active' ? 'success' : 'default'}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

// Node Palette Component
const NodePalette = ({ onAddNode }) => {
  const categories = [...new Set(Object.values(NODE_TYPES).map(type => type.category))];

  return (
    <Card sx={{ height: 'fit-content' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Workflow Components
        </Typography>
        
        {categories.map(category => (
          <Accordion key={category} defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle2" sx={{ textTransform: 'capitalize' }}>
                {category}
              </Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ pt: 0 }}>
              <List dense>
                {Object.entries(NODE_TYPES)
                  .filter(([_, type]) => type.category === category)
                  .map(([key, type]) => (
                    <ListItem 
                      key={key}
                      button
                      onClick={() => onAddNode(key)}
                      sx={{ 
                        borderRadius: 1, 
                        mb: 0.5,
                        '&:hover': {
                          backgroundColor: `${type.color}20`
                        }
                      }}
                    >
                      <ListItemIcon sx={{ color: type.color, minWidth: 32 }}>
                        {type.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={type.name}
                        secondary={type.description}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                  ))}
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </CardContent>
    </Card>
  );
};

// Node Configuration Dialog
const NodeConfigDialog = ({ open, node, onClose, onSave }) => {
  const [config, setConfig] = useState({});
  const [name, setName] = useState('');

  useEffect(() => {
    if (node) {
      setConfig(node.config || {});
      setName(node.name || NODE_TYPES[node.type]?.name || '');
    }
  }, [node]);

  const handleSave = () => {
    const updatedNode = {
      ...node,
      name,
      config
    };
    onSave(updatedNode);
    onClose();
  };

  const renderConfigFields = () => {
    if (!node) return null;

    const nodeType = NODE_TYPES[node.type];
    const fields = getConfigFields(node.type);

    return fields.map(field => (
      <Box key={field.key} sx={{ mb: 2 }}>
        {field.type === 'text' && (
          <TextField
            fullWidth
            label={field.label}
            value={config[field.key] || ''}
            onChange={(e) => setConfig(prev => ({ ...prev, [field.key]: e.target.value }))}
            helperText={field.description}
          />
        )}
        
        {field.type === 'select' && (
          <FormControl fullWidth>
            <InputLabel>{field.label}</InputLabel>
            <Select
              value={config[field.key] || ''}
              onChange={(e) => setConfig(prev => ({ ...prev, [field.key]: e.target.value }))}
            >
              {field.options.map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}

        {field.type === 'boolean' && (
          <FormControlLabel
            control={
              <Switch
                checked={config[field.key] || false}
                onChange={(e) => setConfig(prev => ({ ...prev, [field.key]: e.target.checked }))}
              />
            }
            label={field.label}
          />
        )}

        {field.type === 'number' && (
          <TextField
            fullWidth
            type="number"
            label={field.label}
            value={config[field.key] || ''}
            onChange={(e) => setConfig(prev => ({ ...prev, [field.key]: parseInt(e.target.value) }))}
            helperText={field.description}
          />
        )}
      </Box>
    ));
  };

  const getConfigFields = (nodeType) => {
    const fields = {
      scraper: [
        { key: 'url', label: 'Target URL', type: 'text', description: 'Website URL to scrape' },
        { key: 'selector', label: 'CSS Selector', type: 'text', description: 'Element selector' },
        { key: 'method', label: 'HTTP Method', type: 'select', options: [
          { value: 'GET', label: 'GET' },
          { value: 'POST', label: 'POST' }
        ]},
        { key: 'delay', label: 'Delay (ms)', type: 'number', description: 'Delay between requests' }
      ],
      filter: [
        { key: 'field', label: 'Field Name', type: 'text', description: 'Field to filter' },
        { key: 'operator', label: 'Operator', type: 'select', options: [
          { value: 'equals', label: 'Equals' },
          { value: 'contains', label: 'Contains' },
          { value: 'regex', label: 'Regex Match' }
        ]},
        { key: 'value', label: 'Filter Value', type: 'text', description: 'Value to match' }
      ],
      transform: [
        { key: 'script', label: 'Transform Script', type: 'text', description: 'JavaScript transformation code' },
        { key: 'outputFormat', label: 'Output Format', type: 'select', options: [
          { value: 'json', label: 'JSON' },
          { value: 'csv', label: 'CSV' },
          { value: 'xml', label: 'XML' }
        ]}
      ],
      storage: [
        { key: 'database', label: 'Database', type: 'select', options: [
          { value: 'postgresql', label: 'PostgreSQL' },
          { value: 'mysql', label: 'MySQL' },
          { value: 'mongodb', label: 'MongoDB' }
        ]},
        { key: 'table', label: 'Table/Collection', type: 'text', description: 'Target table name' }
      ],
      notification: [
        { key: 'type', label: 'Notification Type', type: 'select', options: [
          { value: 'email', label: 'Email' },
          { value: 'slack', label: 'Slack' },
          { value: 'webhook', label: 'Webhook' }
        ]},
        { key: 'recipient', label: 'Recipient', type: 'text', description: 'Email or webhook URL' },
        { key: 'message', label: 'Message Template', type: 'text', description: 'Notification message' }
      ],
      trigger: [
        { key: 'schedule', label: 'Schedule', type: 'text', description: 'Cron expression' },
        { key: 'enabled', label: 'Enabled', type: 'boolean', description: 'Enable automatic execution' }
      ]
    };

    return fields[nodeType] || [];
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Configure {node ? NODE_TYPES[node.type]?.name : 'Node'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 1 }}>
          <TextField
            fullWidth
            label="Node Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          {renderConfigFields()}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained">
          Save Configuration
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Main Workflow Builder Component
export const WorkflowBuilder = () => {
  const [workflows, setWorkflows] = useState([]);
  const [currentWorkflow, setCurrentWorkflow] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [configDialogOpen, setConfigDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [executionProgress, setExecutionProgress] = useState(0);
  const { showNotification } = useNotifications();

  const createNewWorkflow = () => {
    const newWorkflow = {
      id: Date.now().toString(),
      name: `Workflow ${workflows.length + 1}`,
      description: 'New workflow',
      nodes: [],
      connections: [],
      created: new Date().toISOString(),
      status: 'draft'
    };
    
    setWorkflows(prev => [...prev, newWorkflow]);
    setCurrentWorkflow(newWorkflow);
    setNodes([]);
    setConnections([]);
    showNotification('New workflow created', 'success');
  };

  const addNode = (nodeType) => {
    const newNode = {
      id: `node_${Date.now()}`,
      type: nodeType,
      name: NODE_TYPES[nodeType]?.name,
      config: {},
      position: { x: 100, y: nodes.length * 120 + 100 },
      status: 'inactive'
    };

    setNodes(prev => [...prev, newNode]);
    showNotification(`${NODE_TYPES[nodeType]?.name} node added`, 'success');
  };

  const editNode = (node) => {
    setSelectedNode(node);
    setConfigDialogOpen(true);
  };

  const saveNodeConfig = (updatedNode) => {
    setNodes(prev => prev.map(node => 
      node.id === updatedNode.id ? updatedNode : node
    ));
    showNotification('Node configuration saved', 'success');
  };

  const deleteNode = (nodeId) => {
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    setConnections(prev => prev.filter(conn => 
      conn.source !== nodeId && conn.target !== nodeId
    ));
    showNotification('Node deleted', 'info');
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(nodes);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setNodes(items);
  };

  const executeWorkflow = async () => {
    if (nodes.length === 0) {
      showNotification('No nodes to execute', 'warning');
      return;
    }

    setExecuting(true);
    setExecutionProgress(0);

    try {
      // Simulate workflow execution
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        
        // Update node status
        setNodes(prev => prev.map(n => 
          n.id === node.id ? { ...n, status: 'executing' } : n
        ));

        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Update progress
        setExecutionProgress(((i + 1) / nodes.length) * 100);

        // Update node status to completed
        setNodes(prev => prev.map(n => 
          n.id === node.id ? { ...n, status: 'completed' } : n
        ));
      }

      showNotification('Workflow executed successfully', 'success');
    } catch (error) {
      showNotification('Workflow execution failed', 'error');
    } finally {
      setExecuting(false);
      setExecutionProgress(0);
    }
  };

  const saveWorkflow = () => {
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      nodes,
      connections,
      lastModified: new Date().toISOString()
    };

    setWorkflows(prev => prev.map(wf => 
      wf.id === currentWorkflow.id ? updatedWorkflow : wf
    ));

    setCurrentWorkflow(updatedWorkflow);
    showNotification('Workflow saved', 'success');
  };

  const exportWorkflow = () => {
    if (!currentWorkflow) return;

    const exportData = {
      ...currentWorkflow,
      nodes,
      connections
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentWorkflow.name.replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showNotification('Workflow exported', 'success');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Workflow Automation Builder
      </Typography>

      {/* Toolbar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={createNewWorkflow}
          >
            New Workflow
          </Button>

          <Button
            variant="outlined"
            startIcon={<PlayArrow />}
            onClick={executeWorkflow}
            disabled={executing || nodes.length === 0}
          >
            {executing ? 'Executing...' : 'Run Workflow'}
          </Button>

          <Button
            variant="outlined"
            startIcon={<Save />}
            onClick={saveWorkflow}
            disabled={!currentWorkflow}
          >
            Save Workflow
          </Button>

          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={exportWorkflow}
            disabled={!currentWorkflow}
          >
            Export
          </Button>

          {currentWorkflow && (
            <Box sx={{ ml: 'auto' }}>
              <Typography variant="body2" color="text.secondary">
                Current: {currentWorkflow.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {nodes.length} nodes
              </Typography>
            </Box>
          )}
        </Box>

        {executing && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Execution Progress: {Math.round(executionProgress)}%
            </Typography>
            <LinearProgress variant="determinate" value={executionProgress} />
          </Box>
        )}
      </Paper>

      <Grid container spacing={3}>
        {/* Node Palette */}
        <Grid item xs={12} md={3}>
          <NodePalette onAddNode={addNode} />
        </Grid>

        {/* Workflow Canvas */}
        <Grid item xs={12} md={9}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Workflow Canvas
              </Typography>

              {nodes.length === 0 ? (
                <Box sx={{ 
                  textAlign: 'center', 
                  py: 8,
                  color: 'text.secondary'
                }}>
                  <Typography variant="h6" gutterBottom>
                    No workflow nodes yet
                  </Typography>
                  <Typography variant="body2">
                    Drag components from the palette to start building your workflow
                  </Typography>
                </Box>
              ) : (
                <DragDropContext onDragEnd={handleDragEnd}>
                  <Droppable droppableId="workflow-canvas">
                    {(provided) => (
                      <Box
                        {...provided.droppableProps}
                        ref={provided.innerRef}
                        sx={{ minHeight: 400 }}
                      >
                        {nodes.map((node, index) => (
                          <Draggable 
                            key={node.id} 
                            draggableId={node.id} 
                            index={index}
                          >
                            {(provided, snapshot) => (
                              <Box
                                ref={provided.innerRef}
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                              >
                                <WorkflowNode
                                  node={node}
                                  onEdit={editNode}
                                  onDelete={deleteNode}
                                  isDragging={snapshot.isDragging}
                                />
                              </Box>
                            )}
                          </Draggable>
                        ))}
                        {provided.placeholder}
                      </Box>
                    )}
                  </Droppable>
                </DragDropContext>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Node Configuration Dialog */}
      <NodeConfigDialog
        open={configDialogOpen}
        node={selectedNode}
        onClose={() => setConfigDialogOpen(false)}
        onSave={saveNodeConfig}
      />
    </Box>
  );
};

export default WorkflowBuilder;
