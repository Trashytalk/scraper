import React, { createContext, useContext, useState, useEffect } from 'react';
import { jobService, JobUpdatesSocket } from '../services/api';

// Job status types
export const JOB_STATUS = {
  IDLE: 'idle',
  PENDING: 'pending',
  RUNNING: 'running', 
  COMPLETED: 'completed',
  FAILED: 'failed',
  PAUSED: 'paused',
  STOPPED: 'stopped',
  QUEUED: 'queued'
};

// Create Job Context
const JobContext = createContext();

export const useJobs = () => {
  const context = useContext(JobContext);
  if (!context) {
    throw new Error('useJobs must be used within a JobProvider');
  }
  return context;
};

export const JobProvider = ({ children }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsSocket, setWsSocket] = useState(null);

  // Load jobs from API on mount
  useEffect(() => {
    loadJobs();
    setupWebSocket();
    
    return () => {
      if (wsSocket) {
        wsSocket.disconnect();
      }
    };
  }, []);

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const jobsData = await jobService.getJobs();
      
      // Validate jobs data
      if (!Array.isArray(jobsData)) {
        throw new Error('Invalid jobs data format received from server');
      }
      
      // Transform API data to match our frontend format
      const transformedJobs = jobsData.map((job, index) => {
        try {
          // Validate required job fields
          if (!job.id || typeof job.id !== 'number') {
            throw new Error(`Job at index ${index} missing valid ID`);
          }
          if (!job.name || typeof job.name !== 'string') {
            throw new Error(`Job ${job.id} missing valid name`);
          }
          if (!job.status || typeof job.status !== 'string') {
            throw new Error(`Job ${job.id} missing valid status`);
          }
          
          return {
            ...job,
            runtime: 0, // Will be calculated from timestamps
            logs: [], // Will be loaded separately when needed
            config: job.config || {},
            progress: typeof job.progress === 'number' ? job.progress : 0,
            items_collected: typeof job.items_collected === 'number' ? job.items_collected : 0
          };
        } catch (transformError) {
          console.error('Error transforming job data:', transformError.message);
          // Return a default job structure for invalid data
          return {
            id: job.id || `invalid-${index}`,
            name: job.name || 'Invalid Job',
            status: 'failed',
            progress: 0,
            runtime: 0,
            logs: [],
            config: {},
            items_collected: 0,
            url: job.url || '',
            scraper_type: job.scraper_type || 'unknown',
            created_at: job.created_at || new Date().toISOString(),
            last_run: job.last_run || null,
            next_run: job.next_run || null,
            schedule: job.schedule || 'manual'
          };
        }
      });
      
      setJobs(transformedJobs);
      console.log(`Successfully loaded ${transformedJobs.length} jobs`);
      
    } catch (err) {
      console.error('Failed to load jobs:', err);
      const errorMessage = err.message || 'Failed to load jobs. Please check if the backend server is running.';
      setError(errorMessage);
      
      // Fall back to empty array if API is not available
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    try {
      const socket = new JobUpdatesSocket((data) => {
        try {
          // Validate received data
          if (!data || typeof data !== 'object') {
            console.warn('Invalid WebSocket data received:', data);
            return;
          }
          
          if (data.type === 'job_update') {
            if (data.job && data.job.id) {
              updateJobFromWebSocket(data.job);
            } else {
              console.warn('Invalid job update data:', data);
            }
          } else if (data.type === 'job_progress') {
            if (typeof data.job_id === 'number' && typeof data.progress === 'number') {
              updateJobProgress(data.job_id, data.progress, data.items_collected);
            } else {
              console.warn('Invalid job progress data:', data);
            }
          } else if (data.type === 'job_log') {
            if (typeof data.job_id === 'number' && data.log) {
              addJobLog(data.job_id, data.log);
            } else {
              console.warn('Invalid job log data:', data);
            }
          } else {
            console.warn('Unknown WebSocket message type:', data.type);
          }
        } catch (handlerError) {
          console.error('Error handling WebSocket message:', handlerError);
        }
      });
      
      socket.connect();
      setWsSocket(socket);
      console.log('WebSocket connection established');
      
    } catch (err) {
      console.warn('WebSocket connection failed, falling back to polling:', err);
      // Set up polling as fallback
      setupPolling();
    }
  };

  const setupPolling = () => {
    try {
      const interval = setInterval(async () => {
        try {
          const jobsData = await jobService.getJobs();
          if (Array.isArray(jobsData)) {
            const transformedJobs = jobsData.map((job, index) => {
              try {
                return {
                  ...job,
                  runtime: calculateRuntime(job.last_run, job.status),
                  logs: [], 
                  config: job.config || {},
                  progress: typeof job.progress === 'number' ? job.progress : 0,
                  items_collected: typeof job.items_collected === 'number' ? job.items_collected : 0
                };
              } catch (transformError) {
                console.error(`Error transforming job ${job.id || index}:`, transformError);
                return job;
              }
            });
            setJobs(transformedJobs);
          }
        } catch (err) {
          console.error('Polling failed:', err);
          // Don't update error state during polling to avoid constant error messages
        }
      }, 5000); // Poll every 5 seconds
      
      // Clean up interval when component unmounts
      return () => clearInterval(interval);
    } catch (err) {
      console.error('Failed to setup polling:', err);
    }
  };

  const calculateRuntime = (lastRun, status) => {
    if (!lastRun || status !== JOB_STATUS.RUNNING) return 0;
    const startTime = new Date(lastRun);
    const now = new Date();
    return Math.max(0, now.getTime() - startTime.getTime());
  };

  const updateJobFromWebSocket = (updatedJob) => {
    setJobs(prevJobs =>
      prevJobs.map(job =>
        job.id === updatedJob.id 
          ? { ...job, ...updatedJob, runtime: calculateRuntime(updatedJob.last_run, updatedJob.status) }
          : job
      )
    );
  };

  const updateJobProgress = (jobId, progress, itemsCollected) => {
    setJobs(prevJobs =>
      prevJobs.map(job =>
        job.id === jobId
          ? { 
              ...job, 
              progress: progress || job.progress,
              items_collected: itemsCollected || job.items_collected,
              runtime: job.status === JOB_STATUS.RUNNING ? job.runtime + 1000 : job.runtime
            }
          : job
      )
    );
  };

  const addJobLog = (jobId, logEntry) => {
    setJobs(prevJobs =>
      prevJobs.map(job =>
        job.id === jobId
          ? { ...job, logs: [...(job.logs || []), logEntry] }
          : job
      )
    );
  };
  const startJob = async (jobId) => {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      
      // Check if job exists
      const job = jobs.find(j => j.id === jobId);
      if (!job) {
        throw new Error(`Job with ID ${jobId} not found`);
      }
      
      // Check if job can be started
      if (job.status === JOB_STATUS.RUNNING) {
        throw new Error('Job is already running');
      }
      
      setError(null);
      await jobService.startJob(jobId);
      
      // Optimistically update the UI
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.id === jobId
            ? {
                ...job,
                status: JOB_STATUS.RUNNING,
                progress: 0,
                runtime: 0,
                items_collected: 0,
                last_run: new Date().toISOString(),
                logs: [...(job.logs || []), `Job started at ${new Date().toLocaleTimeString()}`]
              }
            : job
        )
      );
      
      // Reload jobs to get updated data from server
      setTimeout(loadJobs, 1000);
      console.log(`Successfully started job ${jobId}`);
      
    } catch (err) {
      console.error('Failed to start job:', err);
      const errorMessage = err.message || `Failed to start job ${jobId}`;
      setError(errorMessage);
      
      // Revert optimistic update if it was made
      loadJobs();
    }
  };

  const stopJob = async (jobId) => {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      
      // Check if job exists
      const job = jobs.find(j => j.id === jobId);
      if (!job) {
        throw new Error(`Job with ID ${jobId} not found`);
      }
      
      // Check if job can be stopped
      if (job.status !== JOB_STATUS.RUNNING && job.status !== JOB_STATUS.PENDING) {
        throw new Error('Job is not currently running');
      }
      
      setError(null);
      await jobService.stopJob(jobId);
      
      // Optimistically update the UI
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.id === jobId
            ? {
                ...job,
                status: JOB_STATUS.STOPPED,
                logs: [...(job.logs || []), `Job stopped at ${new Date().toLocaleTimeString()}`]
              }
            : job
        )
      );
      
      // Reload jobs to get updated data from server
      setTimeout(loadJobs, 1000);
      console.log(`Successfully stopped job ${jobId}`);
      
    } catch (err) {
      console.error('Failed to stop job:', err);
      const errorMessage = err.message || `Failed to stop job ${jobId}`;
      setError(errorMessage);
      
      // Revert optimistic update if it was made
      loadJobs();
    }
  };

  const deleteJob = async (jobId) => {
    try {
      if (!jobId || typeof jobId !== 'number') {
        throw new Error('Invalid job ID provided');
      }
      
      // Check if job exists
      const job = jobs.find(j => j.id === jobId);
      if (!job) {
        throw new Error(`Job with ID ${jobId} not found`);
      }
      
      // Check if job can be deleted (shouldn't delete running jobs)
      if (job.status === JOB_STATUS.RUNNING) {
        throw new Error('Cannot delete a running job. Please stop it first.');
      }
      
      setError(null);
      await jobService.deleteJob(jobId);
      
      // Remove job from local state
      setJobs(prevJobs => prevJobs.filter(job => job.id !== jobId));
      console.log(`Successfully deleted job ${jobId}`);
      
    } catch (err) {
      console.error('Failed to delete job:', err);
      setError(`Failed to delete job: ${err.message}`);
    }
  };

  const createJob = async (jobData) => {
    try {
      const newJob = await jobService.createJob(jobData);
      
      // Add the new job to local state
      const transformedJob = {
        ...newJob,
        runtime: 0,
        logs: [`Job created at ${new Date().toLocaleTimeString()}`],
        config: newJob.config || {}
      };
      
      setJobs(prevJobs => [...prevJobs, transformedJob]);
      return transformedJob;
    } catch (err) {
      console.error('Failed to create job:', err);
      setError(`Failed to create job: ${err.message}`);
      throw err;
    }
  };

  const updateJob = async (jobId, updates) => {
    try {
      // For now, just update locally - we'd need a PUT endpoint on the backend
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.id === jobId ? { ...job, ...updates } : job
        )
      );
    } catch (err) {
      console.error('Failed to update job:', err);
      setError(`Failed to update job: ${err.message}`);
    }
  };

  const getJobById = (jobId) => {
    return jobs.find(job => job.id === jobId);
  };

  const loadJobLogs = async (jobId) => {
    try {
      const logsData = await jobService.getJobLogs(jobId);
      
      // Update job with logs
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.id === jobId 
            ? { ...job, logs: logsData.logs || [] }
            : job
        )
      );
      
      return logsData.logs || [];
    } catch (err) {
      console.error('Failed to load job logs:', err);
      return [];
    }
  };

  const getJobData = async (jobId, format = 'json') => {
    try {
      return await jobService.getJobData(jobId, format);
    } catch (err) {
      console.error('Failed to get job data:', err);
      throw err;
    }
  };

  const getRunningJobsCount = () => {
    return jobs.filter(job => job.status === JOB_STATUS.RUNNING).length;
  };

  const getTotalJobsCount = () => {
    return jobs.length;
  };

  const getJobStats = () => {
    const totalJobs = jobs.length;
    const runningJobs = jobs.filter(job => job.status === JOB_STATUS.RUNNING).length;
    const completedJobs = jobs.filter(job => job.status === JOB_STATUS.COMPLETED).length;
    const failedJobs = jobs.filter(job => job.status === JOB_STATUS.FAILED).length;
    const totalItemsCollected = jobs.reduce((sum, job) => sum + (job.items_collected || 0), 0);

    return {
      totalJobs,
      runningJobs,
      completedJobs,
      failedJobs,
      totalItemsCollected
    };
  };

  const refreshJobs = () => {
    loadJobs();
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    jobs,
    loading,
    error,
    startJob,
    stopJob,
    deleteJob,
    createJob,
    updateJob,
    getJobById,
    loadJobLogs,
    getJobData,
    getRunningJobsCount,
    getTotalJobsCount,
    getJobStats,
    refreshJobs,
    clearError,
    JOB_STATUS
  };

  return (
    <JobContext.Provider value={value}>
      {children}
    </JobContext.Provider>
  );
};
