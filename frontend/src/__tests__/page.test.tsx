/**
 * Home Page Tests
 * Tests for the main landing page
 */

import { render, screen, act } from '@testing-library/react'
import HomePage from '@/app/page'

// Mock router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/',
  useSearchParams: () => new URLSearchParams(),
}))

describe('HomePage', () => {
  describe('Hero Section', () => {
    it('should render the main headline', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      // Multiple elements contain "Autonomous AI", so use getAllBy
      const elements = screen.getAllByText(/Autonomous AI/i)
      expect(elements.length).toBeGreaterThan(0)
    })

    it('should render the value proposition', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText(/Deploy intelligent agents that handle your bookkeeping/i)).toBeInTheDocument()
    })

    it('should render CTA buttons', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      // Multiple "Start Free Trial" and "View All Agents" links exist
      const trialLinks = screen.getAllByRole('link', { name: /Start Free Trial/i })
      expect(trialLinks.length).toBeGreaterThan(0)
      
      const viewAgentsLinks = screen.getAllByRole('link', { name: /View All Agents/i })
      expect(viewAgentsLinks.length).toBeGreaterThan(0)
    })

    it('should have signup link in hero CTA', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      const startTrialLinks = screen.getAllByRole('link', { name: /Start Free Trial/i })
      expect(startTrialLinks[0]).toHaveAttribute('href', '/signup')
    })
  })

  describe('Metrics Section', () => {
    it('should display tasks automated metric', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText('10,000+')).toBeInTheDocument()
      expect(screen.getByText('Tasks Automated')).toBeInTheDocument()
    })

    it('should display businesses served metric', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText('500+')).toBeInTheDocument()
      expect(screen.getByText('Businesses Served')).toBeInTheDocument()
    })

    it('should display uptime metric', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText('99.9%')).toBeInTheDocument()
      expect(screen.getByText('Uptime Reliability')).toBeInTheDocument()
    })

    it('should display 24/7 operation metric', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText('24/7')).toBeInTheDocument()
      expect(screen.getByText('Autonomous Operation')).toBeInTheDocument()
    })
  })

  describe('Agents Section', () => {
    it('should display all 12 agents', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText('BookkeeperAI')).toBeInTheDocument()
      expect(screen.getByText('InboxCommanderAI')).toBeInTheDocument()
      expect(screen.getByText('HiringHeroAI')).toBeInTheDocument()
      expect(screen.getByText('CustomerCareAI')).toBeInTheDocument()
      expect(screen.getByText('SocialPilotAI')).toBeInTheDocument()
      expect(screen.getByText('AppointmentSetterAI')).toBeInTheDocument()
      expect(screen.getByText('ComplianceGuardAI')).toBeInTheDocument()
      expect(screen.getByText('CashFlowCommanderAI')).toBeInTheDocument()
      expect(screen.getByText('VendorNegotiatorAI')).toBeInTheDocument()
      expect(screen.getByText('ReputationGuardianAI')).toBeInTheDocument()
      expect(screen.getByText('InventoryIntelAI')).toBeInTheDocument()
      expect(screen.getByText('ProposalProAI')).toBeInTheDocument()
    })

    it('should display agent descriptions', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText(/Autonomous financial operations/i)).toBeInTheDocument()
      expect(screen.getByText(/Your email, intelligently managed/i)).toBeInTheDocument()
    })

    it('should display agent prices', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      // Prices are displayed as separate "$199" and "/month" elements
      const prices = screen.getAllByText(/\$\d+/)
      expect(prices.length).toBeGreaterThan(0)
    })

    it('should display agent categories', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getAllByText('Finance').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Marketing').length).toBeGreaterThan(0)
      expect(screen.getAllByText('HR').length).toBeGreaterThan(0)
    })
  })

  describe('How It Works Section', () => {
    it('should display how it works nav link', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getAllByText(/How It Works/i).length).toBeGreaterThan(0)
    })
  })

  describe('Testimonials Section', () => {
    it('should display testimonials', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText(/Michael Torres/i)).toBeInTheDocument()
      expect(screen.getByText(/Sarah Chen/i)).toBeInTheDocument()
    })

    it('should display testimonial quotes', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText(/saved us 20\+ hours per week/i)).toBeInTheDocument()
      expect(screen.getByText(/handles 80% of our support tickets/i)).toBeInTheDocument()
    })
  })

  describe('Navigation', () => {
    it('should display AgentHub logo', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      const brandElements = screen.getAllByText('AgentHub')
      expect(brandElements.length).toBeGreaterThan(0)
    })

    it('should have sign in link pointing to /login', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      const loginLink = screen.getByRole('link', { name: /Sign In/i })
      expect(loginLink).toHaveAttribute('href', '/login')
    })
  })

  describe('Footer', () => {
    it('should display copyright', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText(/© 2026 AgentHub/i)).toBeInTheDocument()
    })

    it('should display footer links', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument()
      expect(screen.getByText('Terms of Service')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', async () => {
      await act(async () => {
        render(<HomePage />)
      })
      
      const h1 = document.querySelector('h1')
      expect(h1).toBeInTheDocument()
    })
  })
})
