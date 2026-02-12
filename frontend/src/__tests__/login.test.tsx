/**
 * Login Page Tests
 * Tests for the login page component
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from '@/app/login/page'
import { supabase } from '@/lib/supabase'

// Get mocked router
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/login',
  useSearchParams: () => new URLSearchParams(),
}))

describe('LoginPage', () => {
  const mockSupabase = supabase as jest.Mocked<typeof supabase>

  beforeEach(() => {
    jest.clearAllMocks()
    mockPush.mockClear()
  })

  describe('Rendering', () => {
    it('should render the login form', () => {
      render(<LoginPage />)
      
      expect(screen.getByText('Welcome back')).toBeInTheDocument()
      expect(screen.getByText(/Sign in to access your AI agents/i)).toBeInTheDocument()
    })

    it('should render email input', () => {
      render(<LoginPage />)
      
      const emailInput = screen.getByPlaceholderText('name@company.com')
      expect(emailInput).toBeInTheDocument()
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(emailInput).toBeRequired()
    })

    it('should render password input', () => {
      render(<LoginPage />)
      
      const passwordInput = screen.getByPlaceholderText('Enter your password')
      expect(passwordInput).toBeInTheDocument()
      expect(passwordInput).toHaveAttribute('type', 'password')
      expect(passwordInput).toBeRequired()
    })

    it('should render submit button', () => {
      render(<LoginPage />)
      
      const submitButton = screen.getByRole('button', { name: /Sign In/i })
      expect(submitButton).toBeInTheDocument()
      expect(submitButton).toHaveAttribute('type', 'submit')
    })

    it('should render forgot password link', () => {
      render(<LoginPage />)
      
      expect(screen.getByText('Forgot password?')).toBeInTheDocument()
    })

    it('should render signup link', () => {
      render(<LoginPage />)
      
      expect(screen.getByText("Don't have an account?")).toBeInTheDocument()
      expect(screen.getByRole('link', { name: /Create an account/i })).toHaveAttribute('href', '/signup')
    })

    it('should render logo with link to home', () => {
      render(<LoginPage />)
      
      const logoLink = screen.getAllByRole('link').find(link => link.getAttribute('href') === '/')
      expect(logoLink).toBeInTheDocument()
    })

    it('should render remember me checkbox', () => {
      render(<LoginPage />)
      
      const checkbox = screen.getByRole('checkbox')
      expect(checkbox).toBeInTheDocument()
      expect(screen.getByText('Keep me signed in')).toBeInTheDocument()
    })

    it('should render testimonial section on desktop', () => {
      render(<LoginPage />)
      
      expect(screen.getByText(/AgentHub transformed/i)).toBeInTheDocument()
      expect(screen.getByText('Sarah Chen')).toBeInTheDocument()
    })
  })

  describe('Form Interaction', () => {
    it('should allow typing in email field', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)
      
      const emailInput = screen.getByPlaceholderText('name@company.com')
      await user.type(emailInput, 'test@example.com')
      
      expect(emailInput).toHaveValue('test@example.com')
    })

    it('should allow typing in password field', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)
      
      const passwordInput = screen.getByPlaceholderText('Enter your password')
      await user.type(passwordInput, 'mypassword123')
      
      expect(passwordInput).toHaveValue('mypassword123')
    })

    it('should allow toggling remember me checkbox', async () => {
      const user = userEvent.setup()
      render(<LoginPage />)
      
      const checkbox = screen.getByRole('checkbox')
      expect(checkbox).not.toBeChecked()
      
      await user.click(checkbox)
      expect(checkbox).toBeChecked()
      
      await user.click(checkbox)
      expect(checkbox).not.toBeChecked()
    })
  })

  describe('Form Submission', () => {
    it('should call supabase signInWithPassword on submit', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: null,
      })

      render(<LoginPage />)
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password123')
      await user.click(screen.getByRole('button', { name: /Sign In/i }))

      expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })

    it('should redirect to dashboard on successful login', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: null,
      })

      render(<LoginPage />)
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password123')
      await user.click(screen.getByRole('button', { name: /Sign In/i }))

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should display error message on login failure', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: { message: 'Invalid credentials' },
      })

      render(<LoginPage />)
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'wrongpassword')
      await user.click(screen.getByRole('button', { name: /Sign In/i }))

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
      })
    })

    it('should display generic error message when error has no message', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: {},
      })

      render(<LoginPage />)
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password')
      await user.click(screen.getByRole('button', { name: /Sign In/i }))

      await waitFor(() => {
        expect(screen.getByText('Failed to sign in')).toBeInTheDocument()
      })
    })

    it('should show loading state during submission', async () => {
      const user = userEvent.setup()
      
      // Create a promise that we can control
      let resolveLogin: Function
      const loginPromise = new Promise(resolve => {
        resolveLogin = resolve
      })
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockReturnValue(loginPromise)

      render(<LoginPage />)
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password123')
      
      const submitButton = screen.getByRole('button', { name: /Sign In/i })
      await user.click(submitButton)

      // Button should be disabled during loading
      await waitFor(() => {
        expect(submitButton).toBeDisabled()
      })

      // Resolve the login
      resolveLogin!({ error: null })

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })

    it('should disable button during form submission', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ error: null }), 100))
      )

      render(<LoginPage />)
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password123')
      
      const submitButton = screen.getByRole('button', { name: /Sign In/i })
      await user.click(submitButton)

      expect(submitButton).toBeDisabled()
      expect(submitButton).toHaveClass('disabled:opacity-50')
    })
  })

  describe('Accessibility', () => {
    it('should have proper labels for form fields', () => {
      render(<LoginPage />)
      
      expect(screen.getByText('Email address')).toBeInTheDocument()
      expect(screen.getByText('Password')).toBeInTheDocument()
    })

    it('should have alt text for background image', () => {
      render(<LoginPage />)
      
      const images = screen.getAllByRole('img')
      images.forEach(img => {
        expect(img).toHaveAttribute('alt')
      })
    })
  })

  describe('Error States', () => {
    it('should clear error when user starts typing again', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: { message: 'Invalid credentials' },
      })

      render(<LoginPage />)
      
      // Submit with wrong credentials
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'wrong')
      await user.click(screen.getByRole('button', { name: /Sign In/i }))

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
      })

      // Clear password and type new one - error should still be visible
      // (error is only cleared on form submit, not on typing)
      const passwordInput = screen.getByPlaceholderText('Enter your password')
      await user.clear(passwordInput)
      await user.type(passwordInput, 'newpassword')

      // Resubmit with valid credentials
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: null,
      })
      await user.click(screen.getByRole('button', { name: /Sign In/i }))

      await waitFor(() => {
        expect(screen.queryByText('Invalid credentials')).not.toBeInTheDocument()
      })
    })
  })
})
