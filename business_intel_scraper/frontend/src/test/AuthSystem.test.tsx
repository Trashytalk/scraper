import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AuthProvider, useAuth } from '../components/AuthSystem'

// Mock API service
vi.mock('../services/api', () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
    getCurrentUser: vi.fn(),
    refreshToken: vi.fn()
  }
}))

// Test component that uses the auth hook
const TestAuthComponent = () => {
  const { user, isAuthenticated, login, logout, loading } = useAuth()

  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
      </div>
      <div data-testid="loading-status">
        {loading ? 'Loading' : 'Ready'}
      </div>
      {user && (
        <div data-testid="user-info">
          Welcome, {user.username}
        </div>
      )}
      <button onClick={() => login('test@example.com', 'password')}>
        Login
      </button>
      <button onClick={logout}>
        Logout
      </button>
    </div>
  )
}

describe('AuthSystem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('should provide initial unauthenticated state', () => {
    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
    expect(screen.getByTestId('loading-status')).toHaveTextContent('Ready')
  })

  it('should handle successful login', async () => {
    const { authService } = await import('../services/api')
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: 'mock-token'
    })

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByText('Login')
    fireEvent.click(loginButton)

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated')
      expect(screen.getByTestId('user-info')).toHaveTextContent('Welcome, testuser')
    })

    expect(authService.login).toHaveBeenCalledWith('test@example.com', 'password')
  })

  it('should handle login failure', async () => {
    const { authService } = await import('../services/api')
    authService.login = vi.fn().mockRejectedValue(new Error('Invalid credentials'))

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByText('Login')
    fireEvent.click(loginButton)

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
    })
  })

  it('should handle logout', async () => {
    const { authService } = await import('../services/api')
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
    
    authService.login = vi.fn().mockResolvedValue({
      user: mockUser,
      token: 'mock-token'
    })
    authService.logout = vi.fn().mockResolvedValue({})

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    // First login
    const loginButton = screen.getByText('Login')
    fireEvent.click(loginButton)

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated')
    })

    // Then logout
    const logoutButton = screen.getByText('Logout')
    fireEvent.click(logoutButton)

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated')
    })

    expect(authService.logout).toHaveBeenCalled()
  })

  it('should persist authentication state', async () => {
    const mockToken = 'mock-stored-token'
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
    
    // Set up localStorage with existing token
    localStorage.setItem('authToken', mockToken)
    
    const { authService } = await import('../services/api')
    authService.getCurrentUser = vi.fn().mockResolvedValue(mockUser)

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated')
      expect(screen.getByTestId('user-info')).toHaveTextContent('Welcome, testuser')
    })

    expect(authService.getCurrentUser).toHaveBeenCalled()
  })

  it('should handle token refresh', async () => {
    const { authService } = await import('../services/api')
    const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' }
    
    authService.getCurrentUser = vi.fn().mockRejectedValue(new Error('Token expired'))
    authService.refreshToken = vi.fn().mockResolvedValue({
      user: mockUser,
      token: 'new-token'
    })

    localStorage.setItem('authToken', 'expired-token')

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(authService.refreshToken).toHaveBeenCalled()
    })
  })

  it('should show loading state during authentication', async () => {
    const { authService } = await import('../services/api')
    authService.login = vi.fn().mockImplementation(() => new Promise(() => {})) // Never resolves

    render(
      <AuthProvider>
        <TestAuthComponent />
      </AuthProvider>
    )

    const loginButton = screen.getByText('Login')
    fireEvent.click(loginButton)

    expect(screen.getByTestId('loading-status')).toHaveTextContent('Loading')
  })
})
