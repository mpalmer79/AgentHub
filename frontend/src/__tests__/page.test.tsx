/**
 * Home Page Tests
 * Tests for the main landing page component
 */

import { render, screen } from '@testing-library/react'
import HomePage from '@/app/page'

// Mock data from the page
const expectedAgentCount = 12
const expectedMetrics = ['10,000+', '500+', '99.9%', '24/7']

describe('HomePage', () => {
  beforeEach(() => {
    render(<HomePage />)
  })

  describe('Hero Section', () => {
    it('should render the main headline', () => {
      expect(screen.getByText(/12 AI Employees/i)).toBeInTheDocument()
    })

    it('should render the tagline', () => {
      expect(screen.getByText(/One Platform/i)).toBeInTheDocument()
    })

    it('should have a call-to-action button', () => {
      const ctaButtons = screen.getAllByText(/Start Free Trial/i)
      expect(ctaButtons.length).toBeGreaterThan(0)
    })

    it('should have links to signup and login', () => {
      const signupLinks = screen.getAllByRole('link', { name: /Start Free Trial/i })
      expect(signupLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Metrics Section', () => {
    it('should display key metrics', () => {
      expectedMetrics.forEach(metric => {
        expect(screen.getByText(metric)).toBeInTheDocument()
      })
    })

    it('should display metric labels', () => {
      expect(screen.getByText('Tasks Automated')).toBeInTheDocument()
      expect(screen.getByText('Businesses Served')).toBeInTheDocument()
      expect(screen.getByText('Uptime Reliability')).toBeInTheDocument()
      expect(screen.getByText('Autonomous Operation')).toBeInTheDocument()
    })
  })

  describe('Agents Section', () => {
    it('should display all 12 agents', () => {
      const agentNames = [
        'BookkeeperAI',
        'InboxCommanderAI',
        'HiringHeroAI',
        'CustomerCareAI',
        'SocialPilotAI',
        'AppointmentSetterAI',
        'ComplianceGuardAI',
        'CashFlowCommanderAI',
        'VendorNegotiatorAI',
        'ReputationGuardianAI',
        'InventoryIntelAI',
        'ProposalProAI',
      ]

      agentNames.forEach(name => {
        expect(screen.getByText(name)).toBeInTheDocument()
      })
    })

    it('should display agent prices', () => {
      // Check for some price displays
      expect(screen.getByText('$199')).toBeInTheDocument()
      expect(screen.getByText('$149')).toBeInTheDocument()
      expect(screen.getByText('$99')).toBeInTheDocument()
    })

    it('should display agent categories', () => {
      expect(screen.getAllByText('Finance').length).toBeGreaterThan(0)
      expect(screen.getAllByText('Marketing').length).toBeGreaterThan(0)
      expect(screen.getAllByText('HR').length).toBeGreaterThan(0)
    })

    it('should have links to individual agent pages', () => {
      const agentLinks = screen.getAllByRole('link')
      const agentPageLinks = agentLinks.filter(link => 
        link.getAttribute('href')?.startsWith('/') && 
        link.getAttribute('href') !== '/' &&
        !link.getAttribute('href')?.includes('signup') &&
        !link.getAttribute('href')?.includes('login')
      )
      expect(agentPageLinks.length).toBeGreaterThan(0)
    })
  })

  describe('How It Works Section', () => {
    it('should display step numbers', () => {
      expect(screen.getByText('01')).toBeInTheDocument()
      expect(screen.getByText('02')).toBeInTheDocument()
      expect(screen.getByText('03')).toBeInTheDocument()
    })

    it('should display step titles', () => {
      expect(screen.getByText('Connect Your Tools')).toBeInTheDocument()
      expect(screen.getByText('Deploy Your Agents')).toBeInTheDocument()
    })

    it('should mention integrations', () => {
      expect(screen.getByText(/QuickBooks/i)).toBeInTheDocument()
      expect(screen.getByText(/Gmail/i)).toBeInTheDocument()
    })
  })

  describe('Testimonials Section', () => {
    it('should display testimonial quotes', () => {
      expect(screen.getByText(/saved us 20\+ hours per week/i)).toBeInTheDocument()
      expect(screen.getByText(/handles 80% of our support tickets/i)).toBeInTheDocument()
      expect(screen.getByText(/screened 500 resumes/i)).toBeInTheDocument()
    })

    it('should display testimonial authors', () => {
      expect(screen.getByText('Michael Torres')).toBeInTheDocument()
      expect(screen.getByText('Sarah Chen')).toBeInTheDocument()
      expect(screen.getByText('David Park')).toBeInTheDocument()
    })

    it('should display company names', () => {
      expect(screen.getByText(/Meridian Consulting/i)).toBeInTheDocument()
      expect(screen.getByText(/TechStart Inc/i)).toBeInTheDocument()
      expect(screen.getByText(/GrowthLabs/i)).toBeInTheDocument()
    })

    it('should display star ratings', () => {
      // Each testimonial has 5 stars
      const starIcons = document.querySelectorAll('svg.text-yellow-400')
      expect(starIcons.length).toBe(15) // 3 testimonials x 5 stars
    })
  })

  describe('CTA Section', () => {
    it('should have final call-to-action', () => {
      expect(screen.getByText(/Ready to Transform/i)).toBeInTheDocument()
    })
  })

  describe('Footer', () => {
    it('should display copyright', () => {
      expect(screen.getByText(/© 2026 AgentHub/i)).toBeInTheDocument()
    })

    it('should have navigation links', () => {
      expect(screen.getByText('Product')).toBeInTheDocument()
      expect(screen.getByText('Company')).toBeInTheDocument()
      expect(screen.getByText('Legal')).toBeInTheDocument()
    })

    it('should have legal links', () => {
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument()
      expect(screen.getByText('Terms of Service')).toBeInTheDocument()
      expect(screen.getByText('Security')).toBeInTheDocument()
    })

    it('should have social media links', () => {
      const socialLinks = screen.getAllByRole('link').filter(link => {
        const href = link.getAttribute('href')
        return href === '#'
      })
      expect(socialLinks.length).toBeGreaterThan(0)
    })
  })

  describe('Navigation', () => {
    it('should have logo linking to home', () => {
      const logoLinks = screen.getAllByRole('link').filter(link => 
        link.getAttribute('href') === '/'
      )
      expect(logoLinks.length).toBeGreaterThan(0)
    })

    it('should display AgentHub brand name', () => {
      const brandNames = screen.getAllByText('AgentHub')
      expect(brandNames.length).toBeGreaterThan(0)
    })
  })

  describe('Accessibility', () => {
    it('should have alt text for images', () => {
      const images = screen.getAllByRole('img')
      images.forEach(img => {
        expect(img).toHaveAttribute('alt')
      })
    })

    it('should have proper heading hierarchy', () => {
      const h1 = document.querySelector('h1')
      const h2s = document.querySelectorAll('h2')
      const h3s = document.querySelectorAll('h3')
      
      expect(h1).toBeInTheDocument()
      expect(h2s.length).toBeGreaterThan(0)
      expect(h3s.length).toBeGreaterThan(0)
    })
  })
})
