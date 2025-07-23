import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
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
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
  Grid,
  Paper,
  Badge,
  Tooltip,
  Alert,
  Tabs,
  Tab,
  AvatarGroup,
  LinearProgress,
  Menu,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  People,
  PersonAdd,
  Settings,
  MoreVert,
  Edit,
  Delete,
  Share,
  Comment,
  Visibility,
  VisibilityOff,
  Security,
  AdminPanelSettings,
  Work,
  Notifications,
  Chat,
  Assignment,
  History,
  CheckCircle,
  Error,
  Warning,
  AccessTime,
  Group,
  Person,
  Email,
  Phone
} from '@mui/icons-material';
import { useNotifications } from './NotificationSystem';
import { useAuth } from './AuthSystem';

// Role definitions
const ROLES = {
  admin: {
    name: 'Administrator',
    icon: <AdminPanelSettings />,
    color: '#f44336',
    permissions: ['read', 'write', 'delete', 'manage_users', 'manage_settings']
  },
  manager: {
    name: 'Manager',
    icon: <Group />,
    color: '#ff9800',
    permissions: ['read', 'write', 'manage_jobs']
  },
  developer: {
    name: 'Developer',
    icon: <Work />,
    color: '#2196f3',
    permissions: ['read', 'write']
  },
  viewer: {
    name: 'Viewer',
    icon: <Visibility />,
    color: '#4caf50',
    permissions: ['read']
  }
};

// User Management Component
const UserManagement = ({ users, onAddUser, onEditUser, onDeleteUser, currentUser }) => {
  const [addUserDialog, setAddUserDialog] = useState(false);
  const [editUserDialog, setEditUserDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newUser, setNewUser] = useState({
    email: '',
    name: '',
    role: 'viewer'
  });

  const handleAddUser = () => {
    onAddUser(newUser);
    setNewUser({ email: '', name: '', role: 'viewer' });
    setAddUserDialog(false);
  };

  const handleEditUser = (user) => {
    setSelectedUser(user);
    setEditUserDialog(true);
  };

  const getUserStatusColor = (status) => {
    switch (status) {
      case 'online': return 'success';
      case 'away': return 'warning';
      case 'offline': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Team Members</Typography>
        <Button
          variant="contained"
          startIcon={<PersonAdd />}
          onClick={() => setAddUserDialog(true)}
        >
          Add Member
        </Button>
      </Box>

      <List>
        {users.map((user) => (
          <ListItem key={user.id} divider>
            <ListItemAvatar>
              <Badge
                color={getUserStatusColor(user.status)}
                variant="dot"
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              >
                <Avatar sx={{ bgcolor: ROLES[user.role]?.color }}>
                  {user.name?.charAt(0) || user.email.charAt(0)}
                </Avatar>
              </Badge>
            </ListItemAvatar>
            
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle1">
                    {user.name || user.email}
                  </Typography>
                  <Chip
                    icon={ROLES[user.role]?.icon}
                    label={ROLES[user.role]?.name}
                    size="small"
                    sx={{ 
                      bgcolor: `${ROLES[user.role]?.color}20`,
                      color: ROLES[user.role]?.color
                    }}
                  />
                  {user.id === currentUser?.id && (
                    <Chip label="You" size="small" variant="outlined" />
                  )}
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {user.email}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Last active: {user.lastActive ? new Date(user.lastActive).toLocaleDateString() : 'Never'}
                  </Typography>
                </Box>
              }
            />
            
            <ListItemSecondaryAction>
              <IconButton onClick={() => handleEditUser(user)}>
                <Edit />
              </IconButton>
              {user.id !== currentUser?.id && (
                <IconButton onClick={() => onDeleteUser(user.id)}>
                  <Delete />
                </IconButton>
              )}
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>

      {/* Add User Dialog */}
      <Dialog open={addUserDialog} onClose={() => setAddUserDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Invite Team Member</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={newUser.email}
              onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label="Full Name"
              value={newUser.name}
              onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth>
              <InputLabel>Role</InputLabel>
              <Select
                value={newUser.role}
                onChange={(e) => setNewUser(prev => ({ ...prev, role: e.target.value }))}
              >
                {Object.entries(ROLES).map(([key, role]) => (
                  <MenuItem key={key} value={key}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {role.icon}
                      {role.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddUserDialog(false)}>Cancel</Button>
          <Button onClick={handleAddUser} variant="contained">
            Send Invitation
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Project Sharing Component
const ProjectSharing = ({ projects, onShareProject }) => {
  const [shareDialog, setShareDialog] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [shareSettings, setShareSettings] = useState({
    users: [],
    permissions: 'read',
    expiry: '',
    public: false
  });

  const handleShare = (project) => {
    setSelectedProject(project);
    setShareDialog(true);
  };

  const shareProject = () => {
    onShareProject(selectedProject.id, shareSettings);
    setShareDialog(false);
    setShareSettings({
      users: [],
      permissions: 'read',
      expiry: '',
      public: false
    });
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Shared Projects
      </Typography>

      <Grid container spacing={2}>
        {projects.map((project) => (
          <Grid item xs={12} md={6} lg={4} key={project.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Typography variant="h6">{project.name}</Typography>
                  <IconButton onClick={() => handleShare(project)}>
                    <Share />
                  </IconButton>
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  {project.description}
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <AvatarGroup max={4}>
                    {project.collaborators?.map((user) => (
                      <Avatar key={user.id} sx={{ width: 24, height: 24 }}>
                        {user.name?.charAt(0) || user.email.charAt(0)}
                      </Avatar>
                    ))}
                  </AvatarGroup>
                  
                  <Chip
                    label={project.visibility || 'Private'}
                    size="small"
                    color={project.visibility === 'public' ? 'primary' : 'default'}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Share Dialog */}
      <Dialog open={shareDialog} onClose={() => setShareDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Share Project: {selectedProject?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Share with team members
            </Typography>
            
            <TextField
              fullWidth
              label="Email addresses (comma separated)"
              placeholder="user1@example.com, user2@example.com"
              multiline
              rows={2}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Permission Level</InputLabel>
              <Select
                value={shareSettings.permissions}
                onChange={(e) => setShareSettings(prev => ({ ...prev, permissions: e.target.value }))}
              >
                <MenuItem value="read">View Only</MenuItem>
                <MenuItem value="write">Can Edit</MenuItem>
                <MenuItem value="admin">Full Access</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Expiry Date (optional)"
              type="date"
              InputLabelProps={{ shrink: true }}
              sx={{ mb: 2 }}
            />
            
            <FormControlLabel
              control={
                <Switch
                  checked={shareSettings.public}
                  onChange={(e) => setShareSettings(prev => ({ ...prev, public: e.target.checked }))}
                />
              }
              label="Make project publicly accessible"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialog(false)}>Cancel</Button>
          <Button onClick={shareProject} variant="contained">
            Share Project
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Activity Feed Component
const ActivityFeed = ({ activities }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'user_joined': return <PersonAdd />;
      case 'project_shared': return <Share />;
      case 'job_completed': return <CheckCircle />;
      case 'job_failed': return <Error />;
      case 'comment_added': return <Comment />;
      default: return <Notifications />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'user_joined': return 'primary';
      case 'project_shared': return 'info';
      case 'job_completed': return 'success';
      case 'job_failed': return 'error';
      case 'comment_added': return 'default';
      default: return 'default';
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Team Activity
        </Typography>
        
        <List>
          {activities.map((activity, index) => (
            <ListItem key={index} divider={index < activities.length - 1}>
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: `${getActivityColor(activity.type)}.main` }}>
                  {getActivityIcon(activity.type)}
                </Avatar>
              </ListItemAvatar>
              
              <ListItemText
                primary={activity.title}
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {activity.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(activity.timestamp).toLocaleDateString()} • {activity.user}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

// Main Team Collaboration Component
export const TeamCollaboration = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [users, setUsers] = useState([
    {
      id: '1',
      name: 'John Doe',
      email: 'john@example.com',
      role: 'admin',
      status: 'online',
      lastActive: new Date().toISOString()
    },
    {
      id: '2',
      name: 'Jane Smith',
      email: 'jane@example.com',
      role: 'manager',
      status: 'away',
      lastActive: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: '3',
      name: 'Bob Wilson',
      email: 'bob@example.com',
      role: 'developer',
      status: 'offline',
      lastActive: new Date(Date.now() - 86400000).toISOString()
    }
  ]);
  
  const [projects, setProjects] = useState([
    {
      id: '1',
      name: 'E-commerce Analysis',
      description: 'Scraping product data from major e-commerce sites',
      visibility: 'private',
      collaborators: [
        { id: '1', name: 'John Doe', email: 'john@example.com' },
        { id: '2', name: 'Jane Smith', email: 'jane@example.com' }
      ]
    },
    {
      id: '2',
      name: 'News Monitoring',
      description: 'Real-time news tracking and sentiment analysis',
      visibility: 'public',
      collaborators: [
        { id: '1', name: 'John Doe', email: 'john@example.com' },
        { id: '3', name: 'Bob Wilson', email: 'bob@example.com' }
      ]
    }
  ]);

  const [activities, setActivities] = useState([
    {
      type: 'job_completed',
      title: 'Product scraping job completed',
      description: 'Successfully scraped 1,250 products from target site',
      user: 'Jane Smith',
      timestamp: new Date().toISOString()
    },
    {
      type: 'user_joined',
      title: 'New team member joined',
      description: 'Bob Wilson has been added to the development team',
      user: 'John Doe',
      timestamp: new Date(Date.now() - 3600000).toISOString()
    },
    {
      type: 'project_shared',
      title: 'Project shared',
      description: 'E-commerce Analysis project shared with external stakeholders',
      user: 'Jane Smith',
      timestamp: new Date(Date.now() - 7200000).toISOString()
    }
  ]);

  const { user: currentUser } = useAuth();
  const { showNotification } = useNotifications();

  const handleAddUser = (newUser) => {
    const user = {
      id: Date.now().toString(),
      ...newUser,
      status: 'offline',
      lastActive: null
    };
    
    setUsers(prev => [...prev, user]);
    
    const activity = {
      type: 'user_joined',
      title: 'New team member invited',
      description: `${newUser.name || newUser.email} has been invited to join the team`,
      user: currentUser?.name || 'You',
      timestamp: new Date().toISOString()
    };
    
    setActivities(prev => [activity, ...prev]);
    showNotification('Team member invited successfully', 'success');
  };

  const handleEditUser = (userId, updates) => {
    setUsers(prev => prev.map(user => 
      user.id === userId ? { ...user, ...updates } : user
    ));
    showNotification('User updated successfully', 'success');
  };

  const handleDeleteUser = (userId) => {
    setUsers(prev => prev.filter(user => user.id !== userId));
    showNotification('User removed from team', 'info');
  };

  const handleShareProject = (projectId, settings) => {
    const activity = {
      type: 'project_shared',
      title: 'Project shared',
      description: `Project shared with ${settings.permissions} permissions`,
      user: currentUser?.name || 'You',
      timestamp: new Date().toISOString()
    };
    
    setActivities(prev => [activity, ...prev]);
    showNotification('Project shared successfully', 'success');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Team Collaboration
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Collaborate with your team members, share projects, and track activities in real-time.
      </Alert>

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab icon={<People />} label="Team Members" />
        <Tab icon={<Share />} label="Shared Projects" />
        <Tab icon={<History />} label="Activity Feed" />
      </Tabs>

      {activeTab === 0 && (
        <UserManagement
          users={users}
          onAddUser={handleAddUser}
          onEditUser={handleEditUser}
          onDeleteUser={handleDeleteUser}
          currentUser={currentUser}
        />
      )}

      {activeTab === 1 && (
        <ProjectSharing
          projects={projects}
          onShareProject={handleShareProject}
        />
      )}

      {activeTab === 2 && (
        <ActivityFeed activities={activities} />
      )}
    </Box>
  );
};

export default TeamCollaboration;
