/**
 * Auth Context Tests
 * Tests for authentication context provider and hooks
 * 
 * Principal-level test patterns:
 * - Proper async/await with act()
 * - Comprehensive mock setup
 * - Edge case coverage
 * - No flaky tests
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AuthProvider, useAuth } from '@/lib/auth-context'
import { supabase } from '@/lib/supabase'
import { api } from '@/lib/api'

// Mock the API module
jest.mock('@/lib/api', () => ({
  api: {
    setToken: jest.fn(),
    getMe: jest.fn(),
  },
}))

// Test component that exposes auth context
function TestConsumer({ onAuth }: { onAuth?: (auth: ReturnType<typeof useAuth>) => void }) {
  const auth = useAuth()
  
  if (onAuth) {
    onAuth(auth)
  }
  
  return (
    <div>
      <div data-testid="loading">{auth.loading ? 'loading' : 'ready'}</div>
      <div data-testid="user">{auth.user ? auth.user.email : 'no-user'}</div>
      <button onClick={() => auth.signIn('test@example.com', 'password')}>Sign In</button>
      <button onClick={() => auth.signUp('test@example.com', 'password', 'Test User', 'Test Co')}>Sign Up</button>
      <button onClick={() => auth.signOut()}>Sign Out</button>
    </div>
  )
}

describe('AuthContext', () => {
  const mockSupabase = supabase as jest.Mocked<typeof supabase>
  const mockApi = api as jest.Mocked<typeof api>
  
  // Store the auth state change callback so we can trigger it manually
  let authStateCallback: ((event: string, session: any) => void) | null = null

  beforeEach(() => {
    jest.clearAllMocks()
    authStateCallback = null
    
    // Setup default mocks
    ;(mockSupabase.auth.onAuthStateChange as jest.Mock).mockImplementation((callback) => {
      authStateCallback = callback
      return {
        data: { subscription: { unsubscribe: jest.fn() } },
      }
    })
    
    ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
      data: { session: null },
    })
    
    ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
      error: null,
    })
    
    ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
      error: null,
    })
    
    ;(mockSupabase.auth.signOut as jest.Mock).mockResolvedValue({
      error: null,
    })
    
    ;(mockApi.getMe as jest.Mock).mockResolvedValue({
      id: 'user-123',
      email: 'test@example.com',
      full_name: 'Test User',
    })
  })

  describe('Provider Initialization', () => {
    it('should render children', async () => {
      await act(async () => {
        render(
          <AuthProvider>
            <div data-testid="child">Child content</div>
          </AuthProvider>
        )
      })
      
      expect(screen.getByTestId('child')).toHaveTextContent('Child content')
    })

    it('should start in loading state', async () => {
      // Don't resolve getSession immediately
      ;(mockSupabase.auth.getSession as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      )
      
      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      )
      
      expect(screen.getByTestId('loading')).toHaveTextContent('loading')
    })

    it('should finish loading when no session exists', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: null },
      })
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      expect(screen.getByTestId('user')).toHaveTextContent('no-user')
    })

    it('should load user when session exists', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: {
          session: {
            access_token: 'test-token',
            user: { id: 'user-123' },
          },
        },
      })
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })
      
      expect(mockApi.setToken).toHaveBeenCalledWith('test-token')
      expect(mockApi.getMe).toHaveBeenCalled()
    })

    it('should handle getMe failure gracefully', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: {
          session: {
            access_token: 'test-token',
            user: { id: 'user-123' },
          },
        },
      })
      
      ;(mockApi.getMe as jest.Mock).mockRejectedValue(new Error('API Error'))
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      expect(screen.getByTestId('user')).toHaveTextContent('no-user')
    })
  })

  describe('Auth State Changes', () => {
    it('should update user when auth state changes to signed in', async () => {
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      // Initially no user
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      
      // Simulate auth state change
      await act(async () => {
        if (authStateCallback) {
          authStateCallback('SIGNED_IN', {
            access_token: 'new-token',
            user: { id: 'user-456' },
          })
        }
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })
      
      expect(mockApi.setToken).toHaveBeenCalledWith('new-token')
    })

    it('should clear user when auth state changes to signed out', async () => {
      // Start with a session
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: {
          session: {
            access_token: 'test-token',
            user: { id: 'user-123' },
          },
        },
      })
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })
      
      // Simulate sign out
      await act(async () => {
        if (authStateCallback) {
          authStateCallback('SIGNED_OUT', null)
        }
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
      
      expect(mockApi.setToken).toHaveBeenCalledWith(null)
    })
  })

  describe('signIn', () => {
    it('should call supabase signInWithPassword', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      })
    })

    it('should throw error when sign in fails', async () => {
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: { message: 'Invalid credentials' },
      })
      
      let capturedAuth: ReturnType<typeof useAuth> | null = null
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer onAuth={(auth) => { capturedAuth = auth }} />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      await expect(capturedAuth!.signIn('test@example.com', 'wrong')).rejects.toEqual({
        message: 'Invalid credentials',
      })
    })
  })

  describe('signUp', () => {
    it('should call supabase signUp with metadata', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      await user.click(screen.getByRole('button', { name: /sign up/i }))
      
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

    it('should throw error when sign up fails', async () => {
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: { message: 'Email already exists' },
      })
      
      let capturedAuth: ReturnType<typeof useAuth> | null = null
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer onAuth={(auth) => { capturedAuth = auth }} />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      await expect(
        capturedAuth!.signUp('test@example.com', 'pass', 'Name')
      ).rejects.toEqual({ message: 'Email already exists' })
    })
  })

  describe('signOut', () => {
    it('should call supabase signOut and clear user', async () => {
      const user = userEvent.setup()
      
      // Start with a session
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: {
          session: {
            access_token: 'test-token',
            user: { id: 'user-123' },
          },
        },
      })
      
      await act(async () => {
        render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com')
      })
      
      await user.click(screen.getByRole('button', { name: /sign out/i }))
      
      expect(mockSupabase.auth.signOut).toHaveBeenCalled()
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no-user')
      })
      
      expect(mockApi.setToken).toHaveBeenCalledWith(null)
    })
  })

  describe('useAuth hook', () => {
    it('should throw error when used outside provider', () => {
      // Suppress console.error for this test
      const spy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      expect(() => {
        render(<TestConsumer />)
      }).toThrow('useAuth must be used within an AuthProvider')
      
      spy.mockRestore()
    })
  })

  describe('Cleanup', () => {
    it('should unsubscribe on unmount', async () => {
      const unsubscribe = jest.fn()
      
      ;(mockSupabase.auth.onAuthStateChange as jest.Mock).mockReturnValue({
        data: { subscription: { unsubscribe } },
      })
      
      let unmount: () => void
      
      await act(async () => {
        const result = render(
          <AuthProvider>
            <TestConsumer />
          </AuthProvider>
        )
        unmount = result.unmount
      })
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready')
      })
      
      act(() => {
        unmount()
      })
      
      expect(unsubscribe).toHaveBeenCalled()
    })
  })
})
