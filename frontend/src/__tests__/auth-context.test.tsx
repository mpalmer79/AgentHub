/**
 * Auth Context Tests
 * Tests for AuthProvider and useAuth hook
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from '@/lib/auth-context'
import { supabase } from '@/lib/supabase'
import { api } from '@/lib/api'

// Mock the api module
jest.mock('@/lib/api', () => ({
  api: {
    setToken: jest.fn(),
    getMe: jest.fn(),
  },
}))

// Test component that uses the auth hook
function TestConsumer() {
  const { user, loading, signIn, signUp, signOut } = useAuth()
  
  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'ready'}</div>
      <div data-testid="user">{user ? user.email : 'no-user'}</div>
      <button onClick={() => signIn('test@example.com', 'password')}>Sign In</button>
      <button onClick={() => signUp('test@example.com', 'password', 'Test User', 'Test Co')}>Sign Up</button>
      <button onClick={signOut}>Sign Out</button>
    </div>
  )
}

describe('AuthContext', () => {
  const mockSupabase = supabase as jest.Mocked<typeof supabase>
  const mockApi = api as jest.Mocked<typeof api>
  
  beforeEach(() => {
    jest.clearAllMocks()
    
    // Default mock implementations
    ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
      data: { session: null },
    })
    ;(mockSupabase.auth.onAuthStateChange as jest.Mock).mockReturnValue({
      data: { subscription: { unsubscribe: jest.fn() } },
    })
  })

  describe('AuthProvider', () => {
    it('should render children', () => {
      render(
        <AuthProvider>
          <div>Test Child</div>
        </AuthProvider>
      )

      expect(screen.getByText('Test Child')).toBeInTheDocument()
    })

    it('should start in loading state', () => {
      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      expect(screen.getByTestId('loading')).toHaveTextContent('loading')
    })

    it('should set user to null when no session', async () => {
      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })

      expect(screen.getByTestId('user')).toHaveTextContent('no-user')
    })

    it('should fetch user when session exists', async () => {
      const mockSession = {
        access_token: 'test-token',
        user: { id: '123', email: 'test@example.com' },
      }
      
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: mockSession },
      })
      
      mockApi.getMe.mockResolvedValue({
        id: '123',
        email: 'test@example.com',
        full_name: 'Test User',
      })

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })

      expect(mockApi.setToken).toHaveBeenCalledWith('test-token')
      expect(mockApi.getMe).toHaveBeenCalled()
    })

    it('should handle auth state changes', async () => {
      let authChangeCallback: Function | null = null
      
      ;(mockSupabase.auth.onAuthStateChange as jest.Mock).mockImplementation((callback) => {
        authChangeCallback = callback
        return { data: { subscription: { unsubscribe: jest.fn() } } }
      })

      mockApi.getMe.mockResolvedValue({
        id: '123',
        email: 'user@example.com',
      })

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      // Simulate auth state change with new session
      await act(async () => {
        if (authChangeCallback) {
          authChangeCallback('SIGNED_IN', {
            access_token: 'new-token',
            user: { id: '123' },
          })
        }
      })

      await waitFor(() => {
        expect(mockApi.setToken).toHaveBeenCalledWith('new-token')
      })
    })

    it('should clear token on sign out via auth state change', async () => {
      let authChangeCallback: Function | null = null
      
      ;(mockSupabase.auth.onAuthStateChange as jest.Mock).mockImplementation((callback) => {
        authChangeCallback = callback
        return { data: { subscription: { unsubscribe: jest.fn() } } }
      })

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      // Simulate sign out
      await act(async () => {
        if (authChangeCallback) {
          authChangeCallback('SIGNED_OUT', null)
        }
      })

      await waitFor(() => {
        expect(mockApi.setToken).toHaveBeenCalledWith(null)
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
    })

    it('should handle getMe failure gracefully', async () => {
      const mockSession = {
        access_token: 'test-token',
        user: { id: '123' },
      }
      
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: mockSession },
      })
      
      mockApi.getMe.mockRejectedValue(new Error('Network error'))

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
    })
  })

  describe('signIn', () => {
    it('should call supabase signInWithPassword', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: null,
      })

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })

      await user.click(screen.getByText('Sign In'))

      expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      })
    })

    it('should throw error on sign in failure', async () => {
      const user = userEvent.setup()
      const testError = new Error('Invalid credentials')
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: testError,
      })

      // Wrapper to catch the error
      const ErrorBoundary = ({ children }: { children: React.ReactNode }) => {
        return <>{children}</>
      }

      render(
        <AuthProvider>
          <ErrorBoundary>
            <TestConsumer />
          </ErrorBoundary>
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })

      // The click will cause an unhandled promise rejection
      // In a real app, this would be caught by error handling
      await expect(async () => {
        await user.click(screen.getByText('Sign In'))
      }).rejects.toThrow()
    })
  })

  describe('signUp', () => {
    it('should call supabase signUp with user metadata', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: null,
      })

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })

      await user.click(screen.getByText('Sign Up'))

      expect(mockSupabase.auth.signUp).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
        options: {
          data: {
            full_name: 'Test User',
            company_name: 'Test Co',
          },
        },
      })
    })
  })

  describe('signOut', () => {
    it('should call supabase signOut and clear state', async () => {
      const user = userEvent.setup()
      
      // Start with a logged in user
      const mockSession = {
        access_token: 'test-token',
        user: { id: '123', email: 'test@example.com' },
      }
      
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: mockSession },
      })
      
      mockApi.getMe.mockResolvedValue({
        id: '123',
        email: 'test@example.com',
      })
      
      ;(mockSupabase.auth.signOut as jest.Mock).mockResolvedValue({})

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })

      await user.click(screen.getByText('Sign Out'))

      expect(mockSupabase.auth.signOut).toHaveBeenCalled()
      expect(mockApi.setToken).toHaveBeenCalledWith(null)
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
    })
  })

  describe('useAuth hook', () => {
    it('should throw error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        render(<TestConsumer />)
      }).toThrow('useAuth must be used within an AuthProvider')
      
      consoleSpy.mockRestore()
    })
  })
})
