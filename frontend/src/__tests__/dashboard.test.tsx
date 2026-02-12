/**
 * Dashboard Page Tests
 * Tests for the main dashboard component
 */

import { render, screen, waitFor } from '@testing-library/react'
import DashboardPage from '@/app/dashboard/page'
import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'

// Mock the api module
jest.mock('@/lib/api', () => ({
  api: {
    setToken: jest.fn(),
    getTaskStats: jest.fn(),
    getSubscriptions: jest.fn(),
    getTasks: jest.fn(),
  },
}))

describe('DashboardPage', () => {
  const mockApi = api as jest.Mocked<typeof api>
  const mockSupabase = supabase as jest.Mocked<typeof supabase>

  beforeEach(() => {
    jest.clearAllMocks()
    
    // Default: user is logged in
    ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
      data: {
        session: {
          access_token: 'test-token',
          user: {
            email: 'test@example.com',
            user_metadata: { full_name: 'Test User' },
          },
        },
      },
    })

    // Default API responses
    mockApi.getTaskStats.mockResolvedValue({
      total: 100,
      completed: 85,
      pending: 10,
      failed: 5,
    })

    mockApi.getSubscriptions.mockResolvedValue({
      subscriptions: [
        { agent_type: 'bookkeeper', status: 'active', created_at: '2024-01-01' },
        { agent_type: 'inbox_commander', status: 'active', created_at: '2024-01-02' },
      ],
    })

    mockApi.getTasks.mockResolvedValue({
      tasks: [
        {
          id: 'task-1',
          agent_type: 'bookkeeper',
          task: 'Categorize January transactions',
          status: 'completed',
          created_at: '2024-01-15T10:00:00Z',
        },
        {
          id: 'task-2',
          agent_type: 'inbox_commander',
          task: 'Process morning emails',
          status: 'running',
          created_at: '2024-01-15T11:00:00Z',
        },
      ],
    })
  })

  describe('Loading State', () => {
    it('should show loading spinner initially', () => {
      render(<DashboardPage />)
      
      const spinner = document.querySelector('.animate-spin')
      expect(spinner).toBeInTheDocument()
    })
  })

  describe('Welcome Section', () => {
    it('should display welcome message with user name', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Welcome back, Test User/i)).toBeInTheDocument()
      })
    })

    it('should fall back to email prefix if no full name', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: {
          session: {
            access_token: 'test-token',
            user: {
              email: 'john@example.com',
              user_metadata: {},
            },
          },
        },
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Welcome back, john/i)).toBeInTheDocument()
      })
    })

    it('should display dashboard subtitle', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText(/Here's what's happening/i)).toBeInTheDocument()
      })
    })
  })

  describe('Stats Grid', () => {
    it('should display active agents count', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Active Agents')).toBeInTheDocument()
        expect(screen.getByText('2')).toBeInTheDocument() // 2 subscriptions
      })
    })

    it('should display tasks completed count', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Tasks Completed')).toBeInTheDocument()
        expect(screen.getByText('85')).toBeInTheDocument()
      })
    })

    it('should display in progress count', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('In Progress')).toBeInTheDocument()
        expect(screen.getByText('10')).toBeInTheDocument()
      })
    })

    it('should display time saved estimate', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Time Saved')).toBeInTheDocument()
        // 85 completed * 15 min = 1275 min = 21h 15m, displays as 21h
        expect(screen.getByText('21h')).toBeInTheDocument()
      })
    })

    it('should display minutes when under 1 hour', async () => {
      mockApi.getTaskStats.mockResolvedValue({
        total: 3,
        completed: 3,
        pending: 0,
        failed: 0,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        // 3 completed * 15 min = 45 min
        expect(screen.getByText('45m')).toBeInTheDocument()
      })
    })
  })

  describe('Deployed Agents Section', () => {
    it('should display deployed agents heading', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Deployed Agents')).toBeInTheDocument()
      })
    })

    it('should display agent cards for subscriptions', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('BookkeeperAI')).toBeInTheDocument()
        expect(screen.getByText('InboxCommanderAI')).toBeInTheDocument()
      })
    })

    it('should display empty state when no agents deployed', async () => {
      mockApi.getSubscriptions.mockResolvedValue({
        subscriptions: [],
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('No agents deployed yet')).toBeInTheDocument()
        expect(screen.getByText(/Deploy your first AI agent/i)).toBeInTheDocument()
      })
    })

    it('should have link to agents marketplace', async () => {
      mockApi.getSubscriptions.mockResolvedValue({
        subscriptions: [],
      })

      render(<DashboardPage />)

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /Browse Agent Marketplace/i })
        expect(link).toHaveAttribute('href', '/dashboard/agents')
      })
    })

    it('should have View All link to agents page', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const viewAllLink = screen.getByRole('link', { name: /View All/i })
        expect(viewAllLink).toHaveAttribute('href', '/dashboard/agents')
      })
    })
  })

  describe('Performance Section', () => {
    it('should display performance heading', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Performance')).toBeInTheDocument()
      })
    })

    it('should calculate and display success rate', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Success Rate')).toBeInTheDocument()
        // 85 completed / 100 total = 85%
        expect(screen.getByText('85%')).toBeInTheDocument()
      })
    })

    it('should display 100% when no tasks', async () => {
      mockApi.getTaskStats.mockResolvedValue({
        total: 0,
        completed: 0,
        pending: 0,
        failed: 0,
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('100%')).toBeInTheDocument()
      })
    })

    it('should display total tasks count', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Total Tasks')).toBeInTheDocument()
        expect(screen.getByText('100')).toBeInTheDocument()
      })
    })

    it('should display failed tasks count', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Failed')).toBeInTheDocument()
        expect(screen.getByText('5')).toBeInTheDocument()
      })
    })
  })

  describe('Quick Actions Section', () => {
    it('should display quick actions heading', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Quick Actions')).toBeInTheDocument()
      })
    })

    it('should have link to deploy new agent', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /Deploy New Agent/i })
        expect(link).toHaveAttribute('href', '/dashboard/agents')
      })
    })

    it('should have link to connect integration', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /Connect Integration/i })
        expect(link).toHaveAttribute('href', '/dashboard/integrations')
      })
    })

    it('should have link to view all tasks', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /View All Tasks/i })
        expect(link).toHaveAttribute('href', '/dashboard/tasks')
      })
    })
  })

  describe('Recent Activity Section', () => {
    it('should display recent activity heading', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Recent Activity')).toBeInTheDocument()
      })
    })

    it('should display recent tasks', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Categorize January transactions')).toBeInTheDocument()
        expect(screen.getByText('Process morning emails')).toBeInTheDocument()
      })
    })

    it('should display task status badges', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Completed')).toBeInTheDocument()
        expect(screen.getByText('Running')).toBeInTheDocument()
      })
    })

    it('should display empty state when no tasks', async () => {
      mockApi.getTasks.mockResolvedValue({
        tasks: [],
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('No activity yet')).toBeInTheDocument()
        expect(screen.getByText(/Tasks will appear here/i)).toBeInTheDocument()
      })
    })

    it('should display agent name with task', async () => {
      render(<DashboardPage />)

      await waitFor(() => {
        // Tasks should show agent name
        const taskItems = screen.getAllByText(/BookkeeperAI|InboxCommanderAI/)
        expect(taskItems.length).toBeGreaterThan(0)
      })
    })
  })

  describe('API Error Handling', () => {
    it('should handle getTaskStats failure gracefully', async () => {
      mockApi.getTaskStats.mockRejectedValue(new Error('API Error'))

      render(<DashboardPage />)

      await waitFor(() => {
        // Should still render with default/fallback values
        expect(screen.getByText('Active Agents')).toBeInTheDocument()
      })
    })

    it('should handle getSubscriptions failure gracefully', async () => {
      mockApi.getSubscriptions.mockRejectedValue(new Error('API Error'))

      render(<DashboardPage />)

      await waitFor(() => {
        // Should show empty state
        expect(screen.getByText('No agents deployed yet')).toBeInTheDocument()
      })
    })

    it('should handle getTasks failure gracefully', async () => {
      mockApi.getTasks.mockRejectedValue(new Error('API Error'))

      render(<DashboardPage />)

      await waitFor(() => {
        // Should show empty activity state
        expect(screen.getByText('No activity yet')).toBeInTheDocument()
      })
    })
  })

  describe('No Session', () => {
    it('should handle missing session', async () => {
      ;(mockSupabase.auth.getSession as jest.Mock).mockResolvedValue({
        data: { session: null },
      })

      render(<DashboardPage />)

      await waitFor(() => {
        // Should still render but with default name
        expect(screen.getByText(/Welcome back, there/i)).toBeInTheDocument()
      })
    })
  })

  describe('Task Status Colors', () => {
    it('should display correct colors for different task statuses', async () => {
      mockApi.getTasks.mockResolvedValue({
        tasks: [
          { id: '1', agent_type: 'bookkeeper', task: 'Task 1', status: 'completed', created_at: '2024-01-01' },
          { id: '2', agent_type: 'bookkeeper', task: 'Task 2', status: 'pending', created_at: '2024-01-01' },
          { id: '3', agent_type: 'bookkeeper', task: 'Task 3', status: 'failed', created_at: '2024-01-01' },
          { id: '4', agent_type: 'bookkeeper', task: 'Task 4', status: 'running', created_at: '2024-01-01' },
        ],
      })

      render(<DashboardPage />)

      await waitFor(() => {
        expect(screen.getByText('Completed')).toHaveClass('bg-emerald-100', 'text-emerald-700')
        expect(screen.getByText('Pending')).toHaveClass('bg-amber-100', 'text-amber-700')
        expect(screen.getByText('Failed')).toHaveClass('bg-red-100', 'text-red-700')
        expect(screen.getByText('Running')).toHaveClass('bg-blue-100', 'text-blue-700')
      })
    })
  })
})
