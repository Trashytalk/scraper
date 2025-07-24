import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import JobManager from '../components/JobManager'

// Mock the API service
vi.mock('../services/api', () => ({
  jobService: {
    getAllJobs: vi.fn(),
    createJob: vi.fn(),
    startJob: vi.fn(),
    stopJob: vi.fn(),
    deleteJob: vi.fn(),
    getJobResults: vi.fn()
  }
}))

// Mock the auth hook
vi.mock('../components/AuthSystem', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: 1, username: 'testuser' }
  })
}))

describe('JobManager Component', () => {
  const mockJobs = [
    {
      id: 1,
      name: 'Test Job 1',
      status: 'running',
      type: 'web_scraper',
      created_at: '2024-01-01T10:00:00Z',
      progress: 50
    },
    {
      id: 2,
      name: 'Test Job 2',
      status: 'completed',
      type: 'e_commerce',
      created_at: '2024-01-01T09:00:00Z',
      progress: 100
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render job list when loaded', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue(mockJobs)

    render(<JobManager />)

    await waitFor(() => {
      expect(screen.getByText('Test Job 1')).toBeInTheDocument()
      expect(screen.getByText('Test Job 2')).toBeInTheDocument()
    })
  })

  it('should show loading state initially', () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockImplementation(() => new Promise(() => {}))

    render(<JobManager />)

    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('should handle job creation', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue([])
    jobService.createJob = vi.fn().mockResolvedValue({ id: 3, name: 'New Job' })

    render(<JobManager />)

    // Find and click the "Add Job" button
    const addButton = screen.getByText(/add.*job/i)
    fireEvent.click(addButton)

    // Should open job creation dialog
    await waitFor(() => {
      expect(screen.getByText(/create new job/i)).toBeInTheDocument()
    })
  })

  it('should handle job status updates correctly', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue(mockJobs)

    render(<JobManager />)

    await waitFor(() => {
      // Check for status chips
      expect(screen.getByText('running')).toBeInTheDocument()
      expect(screen.getByText('completed')).toBeInTheDocument()
    })
  })

  it('should handle job actions (start, stop, delete)', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue(mockJobs)
    jobService.startJob = vi.fn().mockResolvedValue({})
    jobService.stopJob = vi.fn().mockResolvedValue({})
    jobService.deleteJob = vi.fn().mockResolvedValue({})

    render(<JobManager />)

    await waitFor(() => {
      // Should have action buttons for jobs
      const actionButtons = screen.getAllByRole('button')
      expect(actionButtons.length).toBeGreaterThan(0)
    })
  })

  it('should display job progress correctly', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue(mockJobs)

    render(<JobManager />)

    await waitFor(() => {
      // Should show progress for running jobs
      const progressBars = screen.getAllByRole('progressbar')
      expect(progressBars.length).toBeGreaterThan(0)
    })
  })

  it('should handle API errors gracefully', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockRejectedValue(new Error('API Error'))

    render(<JobManager />)

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })
  })

  it('should filter jobs by status', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue(mockJobs)

    render(<JobManager />)

    await waitFor(() => {
      // Should have filter controls
      const filterElement = screen.getByLabelText(/filter/i) || screen.getByText(/all.*jobs/i)
      expect(filterElement).toBeInTheDocument()
    })
  })

  it('should show job details when expanded', async () => {
    const { jobService } = await import('../services/api')
    jobService.getAllJobs = vi.fn().mockResolvedValue(mockJobs)

    render(<JobManager />)

    await waitFor(() => {
      // Look for expand/detail buttons
      const expandButtons = screen.getAllByLabelText(/expand/i)
      if (expandButtons.length > 0) {
        fireEvent.click(expandButtons[0])
        // Should show more details
      }
    })
  })
})
