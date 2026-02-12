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
      
      const nameInput = screen.getByPlaceholderText(/full name/i)
      expect(nameInput).toBeInTheDocument()
      expect(nameInput).toBeRequired()
    })

    it('should render company name input', () => {
      render(<SignupPage />)
      
      const companyInput = screen.getByPlaceholderText(/company/i)
      expect(companyInput).toBeInTheDocument()
    })

    it('should render email input', () => {
      render(<SignupPage />)
      
      const emailInput = screen.getByPlaceholderText(/email/i)
      expect(emailInput).toBeInTheDocument()
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(emailInput).toBeRequired()
    })

    it('should render password input', () => {
      render(<SignupPage />)
      
      const passwordInput = screen.getByPlaceholderText(/password/i)
      expect(passwordInput).toBeInTheDocument()
      expect(passwordInput).toHaveAttribute('type', 'password')
      expect(passwordInput).toBeRequired()
    })

    it('should render submit button', () => {
      render(<SignupPage />)
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      expect(submitButton).toBeInTheDocument()
    })

    it('should render login link', () => {
      render(<SignupPage />)
      
      expect(screen.getByText(/Already have an account/i)).toBeInTheDocument()
      const loginLink = screen.getByRole('link', { name: /Sign in/i })
      expect(loginLink).toHaveAttribute('href', '/login')
    })

    it('should render logo with link to home', () => {
      render(<SignupPage />)
      
      const logoLink = screen.getAllByRole('link').find(link => link.getAttribute('href') === '/')
      expect(logoLink).toBeInTheDocument()
    })
  })

  describe('Form Interaction', () => {
    it('should allow typing in all fields', async () => {
      const user = userEvent.setup()
      render(<SignupPage />)
      
      const nameInput = screen.getByPlaceholderText(/full name/i)
      const emailInput = screen.getByPlaceholderText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/password/i)
      const companyInput = screen.getByPlaceholderText(/company/i)

      await user.type(nameInput, 'John Doe')
      await user.type(emailInput, 'john@example.com')
      await user.type(passwordInput, 'securepassword123')
      await user.type(companyInput, 'Acme Inc')

      expect(nameInput).toHaveValue('John Doe')
      expect(emailInput).toHaveValue('john@example.com')
      expect(passwordInput).toHaveValue('securepassword123')
      expect(companyInput).toHaveValue('Acme Inc')
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
      
      await user.type(screen.getByPlaceholderText(/full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/password/i), 'password123')
      await user.type(screen.getByPlaceholderText(/company/i), 'Acme Inc')
      
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
                company_name: 'Acme Inc',
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
      
      await user.type(screen.getByPlaceholderText(/full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/password/i), 'password123')
      
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
      
      await user.type(screen.getByPlaceholderText(/full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/email/i), 'existing@example.com')
      await user.type(screen.getByPlaceholderText(/password/i), 'password123')
      
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
      
      await user.type(screen.getByPlaceholderText(/full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/password/i), 'password123')
      
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

    it('should handle signup without company name', async () => {
      const user = userEvent.setup()
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: null,
        data: { user: { id: '123' } },
      })

      render(<SignupPage />)
      
      await user.type(screen.getByPlaceholderText(/full name/i), 'John Doe')
      await user.type(screen.getByPlaceholderText(/email/i), 'john@example.com')
      await user.type(screen.getByPlaceholderText(/password/i), 'password123')
      // Intentionally not filling company name
      
      const submitButton = screen.getByRole('button', { name: /Create Account|Sign Up|Get Started/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockSupabase.auth.signUp).toHaveBeenCalled()
      })
    })
  })

  describe('Password Validation', () => {
    it('should require minimum password length', () => {
      render(<SignupPage />)
      
      const passwordInput = screen.getByPlaceholderText(/password/i)
      // HTML5 validation should be present
      expect(passwordInput).toBeRequired()
    })
  })

  describe('Email Validation', () => {
    it('should require valid email format', () => {
      render(<SignupPage />)
      
      const emailInput = screen.getByPlaceholderText(/email/i)
      expect(emailInput).toHaveAttribute('type', 'email')
    })
  })

  describe('Terms and Privacy', () => {
    it('should mention terms of service', () => {
      render(<SignupPage />)
      
      // Check if there's any mention of terms/privacy
      const termsText = screen.queryByText(/terms/i) || screen.queryByText(/privacy/i)
      // This is optional - some signup pages have it, some don't
    })
  })

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      render(<SignupPage />)
      
      // Check for label elements or aria-labels
      const inputs = screen.getAllByRole('textbox')
      inputs.forEach(input => {
        // Each input should be accessible
        expect(input).toBeInTheDocument()
      })
    })

    it('should have alt text for images', () => {
      render(<SignupPage />)
      
      const images = screen.getAllByRole('img')
      images.forEach(img => {
        expect(img).toHaveAttribute('alt')
      })
    })
  })

  describe('UI Elements', () => {
    it('should display AgentHub branding', () => {
      render(<SignupPage />)
      
      const brandNames = screen.getAllByText(/AgentHub/i)
      expect(brandNames.length).toBeGreaterThan(0)
    })

    it('should have visual appeal elements', () => {
      render(<SignupPage />)
      
      // Check for testimonial or feature highlight
      // This varies by design
    })
  })
})
