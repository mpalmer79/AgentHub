/**
 * Signup Page Tests
 * Tests for the signup/registration page component
 * 
 * Actual placeholders from source:
 * - Full Name: "John Smith"
 * - Company: "Acme Inc."
 * - Email: "john@company.com"
 * - Password: "Create a strong password"
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SignUpPage from '@/app/signup/page'
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
  usePathname: () => '/signup',
  useSearchParams: () => new URLSearchParams(),
}))

describe('SignUpPage', () => {
  const mockSupabase = supabase as jest.Mocked<typeof supabase>

  beforeEach(() => {
    jest.clearAllMocks()
    mockPush.mockClear()
    mockReplace.mockClear()
    
    // Default successful signup
    ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
      error: null,
      data: { user: { id: 'user-123' } },
    })
  })

  describe('Rendering', () => {
    it('should render the signup page with create account message', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      expect(screen.getByText('Create your account')).toBeInTheDocument()
      expect(screen.getByText(/Start your 14-day free trial/i)).toBeInTheDocument()
    })

    it('should render full name input with correct placeholder', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const nameInput = screen.getByPlaceholderText('John Smith')
      expect(nameInput).toBeInTheDocument()
      expect(nameInput).toHaveAttribute('type', 'text')
      expect(nameInput).toBeRequired()
    })

    it('should render company input with correct placeholder', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const companyInput = screen.getByPlaceholderText('Acme Inc.')
      expect(companyInput).toBeInTheDocument()
      expect(companyInput).toHaveAttribute('type', 'text')
      // Company is optional
      expect(companyInput).not.toBeRequired()
    })

    it('should render email input with correct placeholder', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const emailInput = screen.getByPlaceholderText('john@company.com')
      expect(emailInput).toBeInTheDocument()
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(emailInput).toBeRequired()
    })

    it('should render password input with correct placeholder', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const passwordInput = screen.getByPlaceholderText('Create a strong password')
      expect(passwordInput).toBeInTheDocument()
      expect(passwordInput).toHaveAttribute('type', 'password')
      expect(passwordInput).toBeRequired()
      expect(passwordInput).toHaveAttribute('minLength', '8')
    })

    it('should render password requirements text', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      expect(screen.getByText(/Must be at least 8 characters/i)).toBeInTheDocument()
    })

    it('should render create account button', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const button = screen.getByRole('button', { name: /create account/i })
      expect(button).toBeInTheDocument()
      expect(button).toHaveAttribute('type', 'submit')
    })

    it('should render link to login page', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      expect(screen.getByText(/Already have an account/i)).toBeInTheDocument()
      const loginLink = screen.getByRole('link', { name: /sign in/i })
      expect(loginLink).toHaveAttribute('href', '/login')
    })

    it('should render AgentHub branding', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const brandElements = screen.getAllByText('AgentHub')
      expect(brandElements.length).toBeGreaterThan(0)
    })

    it('should render terms of service and privacy policy links', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      expect(screen.getByText(/Terms of Service/i)).toBeInTheDocument()
      expect(screen.getByText(/Privacy Policy/i)).toBeInTheDocument()
    })

    it('should render feature list', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      expect(screen.getByText('Pre-built AI Agents')).toBeInTheDocument()
      expect(screen.getByText('Seamless Integration')).toBeInTheDocument()
      expect(screen.getByText('Human-in-the-Loop')).toBeInTheDocument()
    })
  })

  describe('Form Interaction', () => {
    it('should allow typing in all fields', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      const nameInput = screen.getByPlaceholderText('John Smith')
      const companyInput = screen.getByPlaceholderText('Acme Inc.')
      const emailInput = screen.getByPlaceholderText('john@company.com')
      const passwordInput = screen.getByPlaceholderText('Create a strong password')
      
      await user.type(nameInput, 'Jane Doe')
      await user.type(companyInput, 'Test Corp')
      await user.type(emailInput, 'jane@test.com')
      await user.type(passwordInput, 'securepass123')
      
      expect(nameInput).toHaveValue('Jane Doe')
      expect(companyInput).toHaveValue('Test Corp')
      expect(emailInput).toHaveValue('jane@test.com')
      expect(passwordInput).toHaveValue('securepass123')
    })
  })

  describe('Form Submission', () => {
    it('should call signUp with all fields on form submit', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      await user.type(screen.getByPlaceholderText('Acme Inc.'), 'Test Corp')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'jane@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(mockSupabase.auth.signUp).toHaveBeenCalledWith({
          email: 'jane@test.com',
          password: 'securepass123',
          options: {
            data: {
              full_name: 'Jane Doe',
              company_name: 'Test Corp',
            },
          },
        })
      })
    })

    it('should redirect to dashboard on successful signup', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'jane@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard')
      })
    })

    it('should display error message on signup failure', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: { message: 'User already registered' },
      })
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'existing@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/User already registered/i)).toBeInTheDocument()
      })
    })

    it('should display generic error when error has no message', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signUp as jest.Mock).mockRejectedValue(new Error())
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'jane@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/Failed to create account/i)).toBeInTheDocument()
      })
    })

    it('should disable button during submission', async () => {
      const user = userEvent.setup()
      
      let resolveSignup: (value: any) => void
      const signupPromise = new Promise(resolve => {
        resolveSignup = resolve
      })
      
      ;(mockSupabase.auth.signUp as jest.Mock).mockReturnValue(signupPromise)
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'jane@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      const button = screen.getByRole('button', { name: /create account/i })
      await user.click(button)
      
      await waitFor(() => {
        expect(button).toBeDisabled()
      })
      
      // Resolve signup
      await act(async () => {
        resolveSignup!({ error: null, data: { user: {} } })
      })
      
      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })
    })

    it('should allow signup without company name', async () => {
      const user = userEvent.setup()
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      // Skip company
      await user.type(screen.getByPlaceholderText('john@company.com'), 'jane@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(mockSupabase.auth.signUp).toHaveBeenCalledWith({
          email: 'jane@test.com',
          password: 'securepass123',
          options: {
            data: {
              full_name: 'Jane Doe',
              company_name: '', // Empty string for optional field
            },
          },
        })
      })
    })

    it('should not redirect on signup error', async () => {
      const user = userEvent.setup()
      
      ;(mockSupabase.auth.signUp as jest.Mock).mockResolvedValue({
        error: { message: 'Error' },
      })
      
      await act(async () => {
        render(<SignUpPage />)
      })
      
      await user.type(screen.getByPlaceholderText('John Smith'), 'Jane Doe')
      await user.type(screen.getByPlaceholderText('john@company.com'), 'jane@test.com')
      await user.type(screen.getByPlaceholderText('Create a strong password'), 'securepass123')
      
      await user.click(screen.getByRole('button', { name: /create account/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/Error/i)).toBeInTheDocument()
      })
      
      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('Accessibility', () => {
    it('should have associated labels for all inputs', async () => {
      await act(async () => {
        render(<SignUpPage />)
      })
      
      expect(screen.getByText('Full Name')).toBeInTheDocument()
      expect(screen.getByText('Company')).toBeInTheDocument()
      expect(screen.getByText('Work Email')).toBeInTheDocument()
      expect(screen.getByText('Password')).toBeInTheDocument()
    })
  })
})
