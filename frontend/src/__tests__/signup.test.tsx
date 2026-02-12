/**
 * Signup Page Tests
 * Tests for the signup/registration page component
 */

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignupPage from '@/app/signup/page'
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
  usePathname: () => '/signup',
  useSearchParams: () => new URLSearchParams(),
}))

describe('SignupPage', () => {
  const mockSupabase = supabase as jest.Mocked<typeof supabase>

  beforeEach(() => {
    jest.clearAllMocks()
    mockPush.mockClear()
  })

  describe('Rendering', () => {
    it('should render the signup form', () => {
      render(<SignupPage />)
      
      expect(screen.getByText(/Create your account/i)).toBeInTheDocument()
    })

    it('should render full name input', () => {
      render(<SignupPage />)
      
      // Actual placeholder is "John Smith"
      const nameInput = screen.getByPlaceholderText('John Smith')
      expect(nameInput).toBeInTheDocument()
    })

    it('should render company name input', () => {
      render(<SignupPage />)
      
      // Actual placeholder is "Acme Inc."
      const companyInput = screen.getByPlaceholderText('Acme Inc.')
      expect(companyInput).toBeInTheDocument()
    })

    it('should render email input', () => {
      render(<SignupPage />)
      
      // Actual placeholder is "john@company.com"
      const emailInput = screen.getByPlaceholderText('john@company.com')
      expect(emailInput).toBeInTheDocument()
      expect(emailInput).toHaveAttribute('type', 'email')
    })

    it('should render password input', () => {
      render(<SignupPage />)
      
      // Look for password by label instead
      const passwordInput = screen.getByLabelText(/Password/i)
      expect(passwordInput).toBeInTheDocument()
      expect(passwordInput).toHaveAttribute('type', 'password')
    })

    it('should render submit button', () => {
      render(<SignupPage />)
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      expect(submitButton).toBeInTheDocument()
    })

    it('should render login link', () => {
      render(<SignupPage />)
      
      expect(screen.getByText(/Already have an account/i)).toBeInTheDocument()
    })

    it('should render logo with link to home', () => {
      render(<SignupPage />)
      
      const logoLinks = screen.getAllByRole('link').filter(link => link.getAttribute('href') === '/')
      expect(logoLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Form Interaction', () => {
    it('should allow typing in all fields', async () => {
      const user = userEvent.setup()
      render(<SignupPage />)
      
      const nameInput = screen.getByPlaceholderText('John Smith')
      const emailInput = screen.getByPlaceholderText('john@company.com')
      const passwordInput = screen.getByLabelText(/Password/i)
      const companyInput = screen.getByPlaceholderText('Acme Inc.')

      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'securepassword123')
      await user.type(companyInput, 'Test Company')

      expect(nameInput).toHaveValue('John Doe')
      expect(emailInput).toHaveValue('john@example.com')
      expect(passwordInput).toHaveValue('securepassword123')
      expect(companyInput).toHaveValue('Test Company')
    })
  })

  describe('Form Submission', () => {
    it('should call supabase signUp on submit', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: null,
        data: { user: { id: '123' } },
      })

      render(<SignupPage />)
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'John Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'john@example.com')
      await user.type(screen.getByLabelText(/Password/i), 'password123')
      await user.type(screen.getByPlaceholderText('Acme Inc.'), 'Test Co')
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockSupabase.auth.signUp).toHaveBeenCalledWith(
          expect.objectContaining({
            email: 'john@example.com',
            password: 'password123',
            options: expect.objectContaining({
              data: expect.objectContaining({
                full_name: 'John Doe',
                company_name: 'Test Co',
              }),
            }),
          })
        )
      })
    })

    it('should redirect to dashboard on successful signup', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: null,
        data: { user: { id: '123' } },
      })

      render(<SignupPage />)
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'John Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'john@example.com')
      await user.type(screen.getByLabelText(/Password/i), 'password123')
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should display error message on signup failure', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: { message: 'Email already registered' },
      })

      render(<SignupPage />)
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'John Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'existing@example.com')
      await user.type(screen.getByLabelText(/Password/i), 'password123')
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/Email already registered/i)).toBeInTheDocument()
      })
    })

    it('should show loading state during submission', async () => {
      const user = userEvent.setup()
      
      let resolveSignup: Function
      const signupPromise = new Promise(resolve => {
        resolveSignup = resolve
      })
      
      ;(mockSupabase.auth.signUp as jest.Mock).mockReturnValue(signupPromise)

      render(<SignupPage />)
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'John Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'john@example.com')
      await user.type(screen.getByLabelText(/Password/i), 'password123')
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      await user.click(submitButton)

      // Button should be disabled during loading
      await waitFor(() => {
        expect(submitButton).toBeDisabled()
      })

      // Resolve the signup
      resolveSignup!({ error: null, data: { user: { id: '123' } } })

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      render(<SignupPage />)
      
      expect(screen.getByText('Full Name')).toBeInTheDocument()
      expect(screen.getByText('Work Email')).toBeInTheDocument()
      expect(screen.getByText('Password')).toBeInTheDocument()
      expect(screen.getByText('Company')).toBeInTheDocument()
    })
  })

  describe('UI Elements', () => {
    it('should display AgentHub branding', () => {
      render(<SignupPage />)
      
      const brandNames = screen.getAllByText(/AgentHub/i)
      expect(brandNames.length).toBeGreaterThan(0)
    })
  })
})
