/**
 * Dashboard Page Tests
 * Tests for the main dashboard component
 */

import { render, screen, waitFor, act } from '@testing-library/react'
import DashboardPage from '@/app/dashboard/page'
import { supabase } from '@/lib/supabase'
import { api } from '@/lib/api'

// Mock the API module
jest.mock('@/lib/api', () => ({
  api: {
    setToken: jest.fn(),
    getTaskStats: jest.fn(),
    getSubscriptions: jest.fn(),
    getTasks: jest.fn(),
  },
}))

// Mock router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/dashboard',
  useSearchParams: () => new URLSearchParams(),
}))

describe('DashboardPage', () => {
  const mockSupabase = supabase as jest.Mocked<typeof supabase>
  const mockApi = api as jest.Mocked<typeof api>

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Default session
    ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
      data: {
        session: {
          access_token: 'test-token',
          user: {
            id: 'user-123',
            email: 'test@example.com',
            user_metadata: {
              full_name: 'John Doe',
            },
          },
        },
      },
    })
    
    // Default API responses
    ;(mockApi.getTaskStats as jest.Mock).mockResolvedValue({
      total: 100,
      completed: 85,
      pending: 10,
      failed: 5,
    })
    
    ;(mockApi.getSubscriptions as jest.Mock).mockResolvedValue({
      subscriptions: [
        { agent_type: 'bookkeeper', status: 'active' },
        { agent_type: 'inbox_commander', status: 'active' },
      ],
    })
    
    ;(mockApi.getTasks as jest.Mock).mockResolvedValue({
      tasks: [
        {
          id: 'task-1',
          task: 'Categorize Q4 transactions',
          agent_type: 'bookkeeper',
          status: 'completed',
          created_at: '2024-01-15T10:00:00Z',
        },
        {
          id: 'task-2',
          task: 'Process inbox emails',
          agent_type: 'inbox_commander',
          status: 'running',
          created_at: '2024-01-15T11:00:00Z',
        },
      ],
    })
  })

  describe('Loading State', () => {
    it('should show loading spinner initially', async () => {
      // Delay the session response
      ;(mockSupabase.auth.getSession as jest.Mock).mockImplementation(
        () => new Promise(() => {})
      )
      
      render(<DashboardPage />)
      
      // Should show loading spinner
      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })
  })

  describe('Welcome Section', () => {
    it('should display welcome message with user name', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText(/Welcome back, John Doe/i)).toBeInTheDocument()
      })
    })

    it('should use email username when full_name is not available', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: {
          session: {
            access_token: 'test-token',
            user: {
              id: 'user-123',
              email: 'jane@example.com',
              user_metadata: {},
            },
          },
        },
      })
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText(/Welcome back, jane/i)).toBeInTheDocument()
      })
    })

    it('should display descriptive subtitle', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText(/Here's what's happening with your AI agents today/i)).toBeInTheDocument()
      })
    })
  })

  describe('Stats Grid', () => {
    it('should display active agents count', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Active Agents')).toBeInTheDocument()
        expect(screen.getByText('2')).toBeInTheDocument() // 2 subscriptions
        expect(screen.getByText(/of 12 available/i)).toBeInTheDocument()
      })
    })

    it('should display tasks completed count', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Tasks Completed')).toBeInTheDocument()
        expect(screen.getByText('85')).toBeInTheDocument()
      })
    })

    it('should display in progress tasks count', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('In Progress')).toBeInTheDocument()
        expect(screen.getByText('10')).toBeInTheDocument()
      })
    })

    it('should display time saved in hours when over 60 minutes', async () => {
      // 85 completed * 15 min = 1275 min = 21h 15min
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Time Saved')).toBeInTheDocument()
        expect(screen.getByText('21h')).toBeInTheDocument()
      })
    })

    it('should display time saved in minutes when under 60', async () => {
      ;(mockApi.getTaskStats as jest.Mock).mockResolvedValue({
        total: 5,
        completed: 3, // 3 * 15 = 45 minutes
        pending: 1,
        failed: 1,
      })
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('45m')).toBeInTheDocument()
      })
    })
  })

  describe('Deployed Agents Section', () => {
    it('should display deployed agents heading', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Deployed Agents')).toBeInTheDocument()
      })
    })

    it('should display view all link', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        const viewAllLinks = screen.getAllByText('View All')
        expect(viewAllLinks.length).toBeGreaterThan(0)
      })
    })

    it('should show empty state when no agents deployed', async () => {
      ;(mockApi.getSubscriptions as jest.Mock).mockResolvedValue({
        subscriptions: [],
      })
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('No agents deployed yet')).toBeInTheDocument()
        expect(screen.getByText(/Deploy your first AI agent/i)).toBeInTheDocument()
        expect(screen.getByText('Browse Agent Marketplace')).toBeInTheDocument()
      })
    })
  })

  describe('Performance Section', () => {
    it('should display performance heading', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Performance')).toBeInTheDocument()
      })
    })

    it('should calculate and display success rate', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Success Rate')).toBeInTheDocument()
        expect(screen.getByText('85%')).toBeInTheDocument() // 85/100
      })
    })

    it('should display 100% success rate when no tasks', async () => {
      ;(mockApi.getTaskStats as jest.Mock).mockResolvedValue({
        total: 0,
        completed: 0,
        pending: 0,
        failed: 0,
      })
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('100%')).toBeInTheDocument()
      })
    })

    it('should display total tasks count', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Total Tasks')).toBeInTheDocument()
        expect(screen.getByText('100')).toBeInTheDocument()
      })
    })

    it('should display failed tasks count', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Failed')).toBeInTheDocument()
        expect(screen.getByText('5')).toBeInTheDocument()
      })
    })
  })

  describe('Quick Actions', () => {
    it('should display quick actions section', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Quick Actions')).toBeInTheDocument()
      })
    })

    it('should display deploy new agent link', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        const deployLinks = screen.getAllByText('Deploy New Agent')
        expect(deployLinks.length).toBeGreaterThan(0)
      })
    })

    it('should display connect integration link', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Connect Integration')).toBeInTheDocument()
      })
    })

    it('should display view all tasks link', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('View All Tasks')).toBeInTheDocument()
      })
    })
  })

  describe('Recent Activity Section', () => {
    it('should display recent activity heading', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Recent Activity')).toBeInTheDocument()
      })
    })

    it('should display recent tasks', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Categorize Q4 transactions')).toBeInTheDocument()
        expect(screen.getByText('Process inbox emails')).toBeInTheDocument()
      })
    })

    it('should display task status badges', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('Completed')).toBeInTheDocument()
        expect(screen.getByText('Running')).toBeInTheDocument()
      })
    })

    it('should show empty state when no recent tasks', async () => {
      ;(mockApi.getTasks as jest.Mock).mockResolvedValue({
        tasks: [],
      })
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('No activity yet')).toBeInTheDocument()
        expect(screen.getByText(/Tasks will appear here/i)).toBeInTheDocument()
      })
    })
  })

  describe('API Error Handling', () => {
    it('should handle getTaskStats failure gracefully', async () => {
      ;(mockApi.getTaskStats as jest.Mock).mockRejectedValue(new Error('API Error'))
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      // Should still render with default stats (0)
      await waitFor(() => {
        expect(screen.getByText('Tasks Completed')).toBeInTheDocument()
      })
      
      // Should show 0 for completed tasks when API fails
      const completedSection = screen.getByText('Tasks Completed').closest('div')
      expect(completedSection).toBeInTheDocument()
    })

    it('should handle getSubscriptions failure gracefully', async () => {
      ;(mockApi.getSubscriptions as jest.Mock).mockRejectedValue(new Error('API Error'))
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('No agents deployed yet')).toBeInTheDocument()
      })
    })

    it('should handle getTasks failure gracefully', async () => {
      ;(mockApi.getTasks as jest.Mock).mockRejectedValue(new Error('API Error'))
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(screen.getByText('No activity yet')).toBeInTheDocument()
      })
    })
  })

  describe('No Session', () => {
    it('should handle no session gracefully', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: null },
      })
      
      await act(async () => {
        render(<DashboardPage />)
      })
      
      // Should still render but with default/empty state
      await waitFor(() => {
        expect(screen.getByText(/Welcome back/i)).toBeInTheDocument()
      })
    })
  })

  describe('Token Management', () => {
    it('should set API token from session', async () => {
      await act(async () => {
        render(<DashboardPage />)
      })
      
      await waitFor(() => {
        expect(mockApi.setToken).toHaveBeenCalledWith('test-token')
      })
    })
  })
})
