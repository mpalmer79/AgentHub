/**
 * Login Page Tests
 * Tests for the login page component
 * 
 * Actual placeholders from source:
 * - Email: "name@company.com"
 * - Password: "Enter your password"
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from '@/app/login/page'
import { supabase } from '@/lib/supabase'

// Mock router
const mockPush = jest.fn()
const mockReplace = jest.fn()

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: mockReplace,
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
    mockReplace.mockClear()
    
    // Default successful login
    ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
      error: null,
      data: { user: { id: 'user-123' } },
    })
  })

  describe('Rendering', () => {
    it('should render the login page with welcome message', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      expect(screen.getByText('Welcome back')).toBeInTheDocument()
      expect(screen.getByText(/Sign in to access your AI agents/i)).toBeInTheDocument()
    })

    it('should render email input with correct placeholder', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      const emailInput = screen.getByPlaceholderText('name@company.com')
      expect(emailInput).toBeInTheDocument()
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(emailInput).toBeRequired()
    })

    it('should render password input with correct placeholder', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      const passwordInput = screen.getByPlaceholderText('Enter your password')
      expect(passwordInput).toBeInTheDocument()
      expect(passwordInput).toHaveAttribute('type', 'password')
      expect(passwordInput).toBeRequired()
    })

    it('should render sign in button', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      const button = screen.getByRole('button', { name: /sign in/i })
      expect(button).toBeInTheDocument()
      expect(button).toHaveAttribute('type', 'submit')
    })

    it('should render forgot password link', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      expect(screen.getByText(/forgot password/i)).toBeInTheDocument()
    })

    it('should render keep me signed in checkbox', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      const checkbox = screen.getByRole('checkbox')
      expect(checkbox).toBeInTheDocument()
      expect(screen.getByText(/keep me signed in/i)).toBeInTheDocument()
    })

    it('should render link to sign up page', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument()
      const signupLink = screen.getByRole('link', { name: /create an account/i })
      expect(signupLink).toHaveAttribute('href', '/signup')
    })

    it('should render AgentHub branding', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      expect(screen.getByText('AgentHub')).toBeInTheDocument()
    })

    it('should render home link in logo', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      const homeLinks = screen.getAllByRole('link').filter(link => 
        link.getAttribute('href') === '/'
      )
      expect(homeLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Form Interaction', () => {
    it('should allow typing in email field', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      const emailInput = screen.getByPlaceholderText('name@company.com')
      await user.type(emailInput, 'test@example.com')
      
      expect(emailInput).toHaveValue('test@example.com')
    })

    it('should allow typing in password field', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      const passwordInput = screen.getByPlaceholderText('Enter your password')
      await user.type(passwordInput, 'mypassword123')
      
      expect(passwordInput).toHaveValue('mypassword123')
    })

    it('should allow toggling remember me checkbox', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      const checkbox = screen.getByRole('checkbox')
      expect(checkbox).not.toBeChecked()
      
      await user.click(checkbox)
      expect(checkbox).toBeChecked()
      
      await user.click(checkbox)
      expect(checkbox).not.toBeChecked()
    })
  })

  describe('Form Submission', () => {
    it('should call signInWithPassword on form submit', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password123')
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
        })
      })
    })

    it('should redirect to dashboard on successful login', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password123')
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should display error message on login failure', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: { message: 'Invalid login credentials' },
      })
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'wrongpassword')
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/Invalid login credentials/i)).toBeInTheDocument()
      })
    })

    it('should display generic error message when error has no message', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockRejectedValue(new Error())
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password')
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to sign in/i)).toBeInTheDocument()
      })
    })

    it('should disable button during submission', async () => {
      const user = userEvent.setup()
      
      let resolveLogin: (value: any) => void
      const loginPromise = new Promise(resolve => {
        resolveLogin = resolve
      })
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockReturnValue(loginPromise)
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password')
      
      const button = screen.getByRole('button', { name: /sign in/i })
      await user.click(button)
      
      await waitFor(() => {
        expect(button).toBeDisabled()
      })
      
      // Resolve login
      await act(async () => {
        resolveLogin!({ error: null, data: { user: {} } })
      })
      
      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })
    })

    it('should not redirect on login error', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signInWithPassword as jest.Mock).mockResolvedValue({
        error: { message: 'Error' },
      })
      
      await act(async () => {
        render(<LoginPage />)
      })
      
      await user.type(screen.getByPlaceholderText('name@company.com'), 'test@example.com')
      await user.type(screen.getByPlaceholderText('Enter your password'), 'password')
      
      await user.click(screen.getByRole('button', { name: /sign in/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/Error/i)).toBeInTheDocument()
      })
      
      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('should have associated labels for inputs', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      expect(screen.getByText('Email address')).toBeInTheDocument()
      expect(screen.getByText('Password')).toBeInTheDocument()
    })

    it('should have descriptive button text', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      const button = screen.getByRole('button', { name: /sign in/i })
      expect(button).toBeInTheDocument()
    })
  })

  describe('UI Elements', () => {
    it('should display testimonial on large screens', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      // The testimonial content is in the DOM but may be hidden on mobile
      expect(screen.getByText(/AgentHub transformed/i)).toBeInTheDocument()
    })

    it('should display testimonial author', async () => {
      await act(async () => {
        render(<LoginPage />)
      })
      
      expect(screen.getByText('Sarah Chen')).toBeInTheDocument()
      expect(screen.getByText(/CFO, TechStart Inc/i)).toBeInTheDocument()
    })
  })
})
