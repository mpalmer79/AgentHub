/**
 * Home Page Tests
 * Tests for the main landing page
 */

import { render, screen, act } from '@testing-library/react'
import Home from '@/app/page'

// Mock next/navigation
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

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: React.ImgHTMLAttributes<HTMLImageElement> & { fill?: boolean }) => {
    const { fill, ...rest } = props
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...rest} alt={rest.alt || ''} />
  },
}))

describe('Home Page', () => {
  describe('Hero Section', () => {
    it('should render the main headline', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText(/AI Agents That Work/i)).toBeInTheDocument()
      expect(screen.getByText(/While You Sleep/i)).toBeInTheDocument()
    })

    it('should render the value proposition', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      // Text is split across elements, check for key phrases
      expect(screen.getByText(/Deploy autonomous AI agents/i)).toBeInTheDocument()
    })

    it('should render CTA buttons', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const trialLinks = screen.getAllByRole('link', { name: /Start Free Trial/i })
      expect(trialLinks.length).toBeGreaterThan(0)
      
      expect(screen.getByText(/Explore Agents/i)).toBeInTheDocument()
    })

    it('should have signup link in hero CTA', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const startTrialLinks = screen.getAllByRole('link', { name: /Start Free Trial/i })
      expect(startTrialLinks[0]).toHaveAttribute('href', '/signup')
    })
  })

  describe('Metrics Section', () => {
    it('should display tasks automated metric', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('10,000+')).toBeInTheDocument()
      expect(screen.getByText('Tasks Automated')).toBeInTheDocument()
    })

    it('should display businesses served metric', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('500+')).toBeInTheDocument()
      expect(screen.getByText('Businesses Served')).toBeInTheDocument()
    })

    it('should display uptime metric', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('99.9%')).toBeInTheDocument()
      expect(screen.getByText('Uptime Reliability')).toBeInTheDocument()
    })

    it('should display 24/7 operation metric', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('24/7')).toBeInTheDocument()
      expect(screen.getByText('Autonomous Operation')).toBeInTheDocument()
    })
  })

  describe('Pricing Section', () => {
    it('should display pricing plans', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('Starter')).toBeInTheDocument()
      expect(screen.getByText('Professional')).toBeInTheDocument()
      expect(screen.getByText('Enterprise')).toBeInTheDocument()
    })

    it('should display setup fee information', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      // Multiple elements may contain these values
      expect(screen.getAllByText(/750/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/1,500/).length).toBeGreaterThan(0)
    })

    it('should display package prices', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      // Multiple elements may contain these price values
      expect(screen.getAllByText(/399/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/499/).length).toBeGreaterThan(0)
      expect(screen.getAllByText(/799/).length).toBeGreaterThan(0)
    })
  })

  describe('Agents Section', () => {
    it('should display all 12 agents', async () => {
      await act(async () => {
        render(<Home />)
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
        render(<Home />)
      })
      
      expect(screen.getByText(/Autonomous financial operations/i)).toBeInTheDocument()
      expect(screen.getByText(/Your email, intelligently managed/i)).toBeInTheDocument()
    })

    it('should display agent prices', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const prices = screen.getAllByText(/\$\d+/)
      expect(prices.length).toBeGreaterThan(0)
    })

    it('should display agent categories', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getAllByText('Finance').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Marketing').length).toBeGreaterThan(0)
      expect(screen.getAllByText('HR').length).toBeGreaterThan(0)
    })
  })

  describe('How It Works Section', () => {
    it('should display how it works steps', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('Connect Your Tools')).toBeInTheDocument()
      expect(screen.getByText('Deploy Your Agents')).toBeInTheDocument()
      expect(screen.getByText('Watch Them Work')).toBeInTheDocument()
    })

    it('should display step numbers', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('01')).toBeInTheDocument()
      expect(screen.getByText('02')).toBeInTheDocument()
      expect(screen.getByText('03')).toBeInTheDocument()
    })
  })

  describe('Testimonials Section', () => {
    it('should display testimonials', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText(/Michael Torres/i)).toBeInTheDocument()
      expect(screen.getByText(/Sarah Chen/i)).toBeInTheDocument()
      expect(screen.getByText(/David Park/i)).toBeInTheDocument()
    })

    it('should display testimonial quotes', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText(/saved us 20\+ hours per week/i)).toBeInTheDocument()
      expect(screen.getByText(/handles 80% of our support tickets/i)).toBeInTheDocument()
    })
  })

  describe('Navigation', () => {
    it('should display AgentHub logo', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const brandElements = screen.getAllByText('AgentHub')
      expect(brandElements.length).toBeGreaterThan(0)
    })

    it('should have admin login link pointing to /login', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const loginLink = screen.getByRole('link', { name: /Admin Login/i })
      expect(loginLink).toHaveAttribute('href', '/login')
    })

    it('should have navigation links', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('Agents')).toBeInTheDocument()
      expect(screen.getByText('Pricing')).toBeInTheDocument()
      expect(screen.getByText('How It Works')).toBeInTheDocument()
      expect(screen.getByText('Testimonials')).toBeInTheDocument()
    })
  })

  describe('Footer', () => {
    it('should display copyright', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText(/2026 AgentHub/i)).toBeInTheDocument()
    })

    it('should display footer links', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument()
      expect(screen.getByText('Terms of Service')).toBeInTheDocument()
      expect(screen.getByText('Security')).toBeInTheDocument()
    })

    it('should display product links', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText('All Agents')).toBeInTheDocument()
      expect(screen.getByText('Integrations')).toBeInTheDocument()
    })
  })

  describe('CTA Section', () => {
    it('should display CTA headline', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      expect(screen.getByText(/Ready to Transform Your Operations/i)).toBeInTheDocument()
    })

    it('should have View All Agents link', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const viewAgentsLinks = screen.getAllByText(/View All Agents/i)
      expect(viewAgentsLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const h1 = document.querySelector('h1')
      expect(h1).toBeInTheDocument()
    })

    it('should have alt text on images', async () => {
      await act(async () => {
        render(<Home />)
      })
      
      const images = document.querySelectorAll('img')
      images.forEach(img => {
        expect(img).toHaveAttribute('alt')
      })
    })
  })
})
