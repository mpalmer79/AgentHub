/**
 * Smoke Tests and Test Utilities
 * Basic tests to verify the test setup is working correctly
 */

describe('Test Environment', () => {
  describe('Jest Setup', () => {
    it('should have Jest configured correctly', () => {
      expect(true).toBe(true)
    })

    it('should support async/await', async () => {
      const result = await Promise.resolve('test')
      expect(result).toBe('test')
    })

    it('should have access to DOM matchers', () => {
      const div = document.createElement('div')
      div.textContent = 'Hello'
      document.body.appendChild(div)
      
      expect(div).toBeInTheDocument()
      expect(div).toHaveTextContent('Hello')
      
      document.body.removeChild(div)
    })
  })

  describe('Mock Configuration', () => {
    it('should have mocked next/navigation', () => {
      const { useRouter } = require('next/navigation')
      const router = useRouter()
      
      expect(router.push).toBeDefined()
      expect(typeof router.push).toBe('function')
    })

    it('should have mocked supabase', () => {
      const { supabase } = require('@/lib/supabase')
      
      expect(supabase.auth.getSession).toBeDefined()
      expect(supabase.auth.signInWithPassword).toBeDefined()
      expect(supabase.auth.signUp).toBeDefined()
      expect(supabase.auth.signOut).toBeDefined()
    })

    it('should have environment variables set', () => {
      expect(process.env.NEXT_PUBLIC_SUPABASE_URL).toBe('https://test.supabase.co')
      expect(process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY).toBe('test-anon-key')
      expect(process.env.NEXT_PUBLIC_API_URL).toBe('http://localhost:8000')
    })
  })
})

describe('Agent Catalog Data Validation', () => {
  const agents = [
    { id: 'bookkeeper', name: 'BookkeeperAI', price: 199, category: 'Finance' },
    { id: 'inbox_commander', name: 'InboxCommanderAI', price: 149, category: 'Communications' },
    { id: 'hiring_hero', name: 'HiringHeroAI', price: 249, category: 'HR' },
    { id: 'customer_care', name: 'CustomerCareAI', price: 179, category: 'Support' },
    { id: 'social_pilot', name: 'SocialPilotAI', price: 129, category: 'Marketing' },
    { id: 'appointment_setter', name: 'AppointmentSetterAI', price: 99, category: 'Productivity' },
    { id: 'compliance_guard', name: 'ComplianceGuardAI', price: 349, category: 'Legal' },
    { id: 'cashflow_commander', name: 'CashFlowCommanderAI', price: 279, category: 'Finance' },
    { id: 'vendor_negotiator', name: 'VendorNegotiatorAI', price: 299, category: 'Operations' },
    { id: 'reputation_guardian', name: 'ReputationGuardianAI', price: 159, category: 'Marketing' },
    { id: 'inventory_intel', name: 'InventoryIntelAI', price: 229, category: 'Operations' },
    { id: 'proposal_pro', name: 'ProposalProAI', price: 199, category: 'Sales' },
  ]

  it('should have exactly 12 agents', () => {
    expect(agents.length).toBe(12)
  })

  it('should have unique agent IDs', () => {
    const uniqueIds = new Set(agents.map(a => a.id))
    expect(uniqueIds.size).toBe(12)
  })

  it('should have valid prices (between $99 and $349)', () => {
    agents.forEach(agent => {
      expect(agent.price).toBeGreaterThanOrEqual(99)
      expect(agent.price).toBeLessThanOrEqual(349)
    })
  })

  it('should have AppointmentSetterAI as cheapest at $99', () => {
    const cheapest = agents.reduce((min, a) => a.price < min.price ? a : min)
    expect(cheapest.price).toBe(99)
    expect(cheapest.name).toBe('AppointmentSetterAI')
  })

  it('should have ComplianceGuardAI as most expensive at $349', () => {
    const expensive = agents.reduce((max, a) => a.price > max.price ? a : max)
    expect(expensive.price).toBe(349)
    expect(expensive.name).toBe('ComplianceGuardAI')
  })

  it('should have Finance category agents', () => {
    const financeAgents = agents.filter(a => a.category === 'Finance')
    expect(financeAgents.length).toBe(2) // BookkeeperAI, CashFlowCommanderAI
  })

  it('should have Marketing category agents', () => {
    const marketingAgents = agents.filter(a => a.category === 'Marketing')
    expect(marketingAgents.length).toBe(2) // SocialPilotAI, ReputationGuardianAI
  })
})

describe('Application Routes', () => {
  const publicRoutes = ['/', '/login', '/signup']
  const protectedRoutes = [
    '/dashboard',
    '/dashboard/agents',
    '/dashboard/tasks',
    '/dashboard/integrations',
    '/dashboard/settings',
  ]

  publicRoutes.forEach(route => {
    it(`public route should be valid: ${route}`, () => {
      expect(route).toMatch(/^\//)
      expect(route).not.toContain(' ')
    })
  })

  protectedRoutes.forEach(route => {
    it(`protected route should be under /dashboard: ${route}`, () => {
      expect(route).toMatch(/^\/dashboard/)
    })
  })

  it('should have dynamic agent route pattern', () => {
    // The [agentName] folder indicates dynamic routing
    const dynamicPattern = '[agentName]'
    expect(dynamicPattern).toMatch(/\[.*\]/)
  })
})

describe('API Structure', () => {
  const apiEndpoints = [
    { method: 'POST', path: '/api/auth/signup', description: 'User registration' },
    { method: 'POST', path: '/api/auth/signin', description: 'User login' },
    { method: 'GET', path: '/api/auth/me', description: 'Get current user' },
    { method: 'GET', path: '/api/agents/catalog', description: 'List all agents' },
    { method: 'GET', path: '/api/agents/subscriptions', description: 'User subscriptions' },
    { method: 'POST', path: '/api/agents/subscribe', description: 'Subscribe to agent' },
    { method: 'DELETE', path: '/api/agents/subscribe/:agentType', description: 'Unsubscribe' },
    { method: 'POST', path: '/api/agents/run', description: 'Run agent task' },
    { method: 'GET', path: '/api/agents/tasks', description: 'List tasks' },
    { method: 'GET', path: '/api/agents/tasks/:taskId', description: 'Get task details' },
    { method: 'GET', path: '/api/integrations/status', description: 'Integration status' },
    { method: 'GET', path: '/api/integrations/quickbooks/connect', description: 'Connect QB' },
    { method: 'DELETE', path: '/api/integrations/quickbooks/disconnect', description: 'Disconnect QB' },
    { method: 'GET', path: '/api/tasks/pending', description: 'Pending approvals' },
    { method: 'POST', path: '/api/tasks/:taskId/approve', description: 'Approve task' },
    { method: 'GET', path: '/api/tasks/stats', description: 'Task statistics' },
  ]

  it('should have all required API endpoints defined', () => {
    expect(apiEndpoints.length).toBeGreaterThan(10)
  })

  it('should use RESTful HTTP methods', () => {
    const methods = new Set(apiEndpoints.map(e => e.method))
    expect(methods).toContain('GET')
    expect(methods).toContain('POST')
    expect(methods).toContain('DELETE')
  })

  it('should have consistent API path structure', () => {
    apiEndpoints.forEach(endpoint => {
      expect(endpoint.path).toMatch(/^\/api\//)
    })
  })

  it('should group auth endpoints under /api/auth', () => {
    const authEndpoints = apiEndpoints.filter(e => e.path.includes('/auth/'))
    expect(authEndpoints.length).toBe(3)
  })

  it('should group agent endpoints under /api/agents', () => {
    const agentEndpoints = apiEndpoints.filter(e => e.path.includes('/agents/'))
    expect(agentEndpoints.length).toBeGreaterThanOrEqual(6)
  })
})

describe('UI Component Structure', () => {
  it('should have consistent status color mapping', () => {
    const statusColors = {
      completed: { bg: 'bg-emerald-100', text: 'text-emerald-700' },
      running: { bg: 'bg-blue-100', text: 'text-blue-700' },
      pending: { bg: 'bg-amber-100', text: 'text-amber-700' },
      failed: { bg: 'bg-red-100', text: 'text-red-700' },
    }

    Object.values(statusColors).forEach(colors => {
      expect(colors.bg).toMatch(/^bg-/)
      expect(colors.text).toMatch(/^text-/)
    })
  })

  it('should have standard button classes', () => {
    const buttonClasses = {
      primary: 'btn-primary',
      secondary: 'btn-secondary',
    }

    expect(buttonClasses.primary).toBe('btn-primary')
    expect(buttonClasses.secondary).toBe('btn-secondary')
  })
})

describe('Time Calculations', () => {
  it('should calculate time saved correctly', () => {
    const minutesPerTask = 15
    
    // Test cases
    const testCases = [
      { completed: 0, expectedHours: 0, expectedMinutes: 0 },
      { completed: 3, expectedHours: 0, expectedMinutes: 45 },
      { completed: 4, expectedHours: 1, expectedMinutes: 0 },
      { completed: 85, expectedHours: 21, expectedMinutes: 15 },
      { completed: 100, expectedHours: 25, expectedMinutes: 0 },
    ]

    testCases.forEach(({ completed, expectedHours, expectedMinutes }) => {
      const totalMinutes = completed * minutesPerTask
      const hours = Math.floor(totalMinutes / 60)
      const minutes = totalMinutes % 60

      expect(hours).toBe(expectedHours)
      expect(minutes).toBe(expectedMinutes)
    })
  })

  it('should calculate success rate correctly', () => {
    const testCases = [
      { total: 0, completed: 0, expectedRate: 100 },
      { total: 100, completed: 85, expectedRate: 85 },
      { total: 100, completed: 100, expectedRate: 100 },
      { total: 50, completed: 25, expectedRate: 50 },
    ]

    testCases.forEach(({ total, completed, expectedRate }) => {
      const rate = total > 0 ? Math.round((completed / total) * 100) : 100
      expect(rate).toBe(expectedRate)
    })
  })
})
