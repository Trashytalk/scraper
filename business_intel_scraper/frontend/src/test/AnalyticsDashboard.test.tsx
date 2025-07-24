import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import AnalyticsDashboard from '../components/AnalyticsDashboard'

// Mock the services and hooks
vi.mock('../services/api', () => ({
  analyticsService: {
    getDashboardData: vi.fn(),
    getMetrics: vi.fn()
  }
}))

vi.mock('../components/AuthSystem', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: 1, username: 'test' }
  })
}))

// Mock recharts components
vi.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />
}))

describe('AnalyticsDashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state initially', () => {
    render(<AnalyticsDashboard />)
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument()
  })

  it('should render dashboard when data is loaded', async () => {
    const mockData = {
      totalJobs: 100,
      activeJobs: 25,
      completedJobs: 75,
      errorRate: 5
    }

    const { analyticsService } = await import('../services/api')
    analyticsService.getDashboardData = vi.fn().mockResolvedValue(mockData)

    render(<AnalyticsDashboard />)

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()
    })

    // Should display dashboard content
    expect(screen.getByText(/analytics dashboard/i)).toBeInTheDocument()
  })

  it('should handle authentication requirement', () => {
    // Mock unauthenticated state
    vi.doMock('../components/AuthSystem', () => ({
      useAuth: () => ({
        isAuthenticated: false,
        user: null
      })
    }))

    render(<AnalyticsDashboard />)
    
    // Should show authentication message or redirect
    expect(screen.getByText(/please log in/i) || screen.getByText(/authentication required/i))
      .toBeInTheDocument()
  })

  it('should handle API errors gracefully', async () => {
    const { analyticsService } = await import('../services/api')
    analyticsService.getDashboardData = vi.fn().mockRejectedValue(new Error('API Error'))

    render(<AnalyticsDashboard />)

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })
  })

  it('should render charts when data is available', async () => {
    const mockData = {
      performanceData: [
        { time: '10:00', cpu: 45, memory: 60 },
        { time: '11:00', cpu: 50, memory: 65 }
      ]
    }

    const { analyticsService } = await import('../services/api')
    analyticsService.getDashboardData = vi.fn().mockResolvedValue(mockData)

    render(<AnalyticsDashboard />)

    await waitFor(() => {
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
    })
  })
})
