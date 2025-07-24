import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from '../App'

// Mock the DashboardEnhanced component to avoid deep dependency issues
vi.mock('../components/widgets/DashboardEnhanced', () => ({
  default: () => <div data-testid="dashboard-enhanced">Dashboard Enhanced Component</div>
}))

describe('App Component', () => {
  it('should render the main app structure', () => {
    render(<App />)
    
    // Check for main app elements
    expect(screen.getByText('Business Intelligence Platform')).toBeInTheDocument()
    expect(screen.getByTestId('dashboard-enhanced')).toBeInTheDocument()
  })

  it('should toggle dark mode when theme button is clicked', () => {
    render(<App />)
    
    // Find the theme toggle button
    const themeButton = screen.getByLabelText(/toggle theme/i)
    expect(themeButton).toBeInTheDocument()
    
    // Initial state should be light mode
    const lightIcon = screen.getByTestId('Brightness7Icon')
    expect(lightIcon).toBeInTheDocument()
    
    // Click to toggle dark mode
    fireEvent.click(themeButton)
    
    // Should show dark mode icon after toggle
    const darkIcon = screen.getByTestId('Brightness4Icon')
    expect(darkIcon).toBeInTheDocument()
  })

  it('should open settings menu when settings button is clicked', () => {
    render(<App />)
    
    // Find and click settings button
    const settingsButton = screen.getByLabelText(/settings/i)
    fireEvent.click(settingsButton)
    
    // Menu should be visible
    expect(screen.getByText('Theme Settings')).toBeInTheDocument()
    expect(screen.getByText('Performance Mode')).toBeInTheDocument()
  })

  it('should have proper accessibility attributes', () => {
    render(<App />)
    
    // Check for important accessibility elements
    const appBar = screen.getByRole('banner')
    expect(appBar).toBeInTheDocument()
    
    const mainContent = screen.getByRole('main')
    expect(mainContent).toBeInTheDocument()
  })

  it('should handle performance mode toggle', () => {
    render(<App />)
    
    // Open settings menu
    const settingsButton = screen.getByLabelText(/settings/i)
    fireEvent.click(settingsButton)
    
    // Find and toggle performance mode
    const performanceToggle = screen.getByLabelText(/performance mode/i)
    fireEvent.click(performanceToggle)
    
    // Should handle the toggle without errors
    expect(performanceToggle).toBeInTheDocument()
  })
})
