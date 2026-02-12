/**
 * API Client Tests
 * Tests for the ApiClient class in src/lib/api.ts
 */

// We need to test the api module in isolation
const mockFetch = jest.fn()
global.fetch = mockFetch

// Import after mocking fetch
import { api } from '@/lib/api'

describe('ApiClient', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    api.setToken(null)
  })

  describe('setToken', () => {
    it('should set the auth token', () => {
      api.setToken('test-token-123')
      // Token is private, we verify it's set by making a request
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      })

      api.get('/test')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token-123',
          }),
        })
      )
    })

    it('should clear the token when set to null', () => {
      api.setToken('test-token')
      api.setToken(null)

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      })

      api.get('/test')

      const callHeaders = mockFetch.mock.calls[0][1].headers
      expect(callHeaders.Authorization).toBeUndefined()
    })
  })

  describe('get', () => {
    it('should make GET request to correct endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: 'test' }),
      })

      const result = await api.get('/api/test')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      )
      expect(result).toEqual({ data: 'test' })
    })

    it('should throw error on failed request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Not found' }),
      })

      await expect(api.get('/api/missing')).rejects.toThrow('Not found')
    })

    it('should handle non-JSON error responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.reject(new Error('Invalid JSON')),
      })

      await expect(api.get('/api/error')).rejects.toThrow('Request failed')
    })
  })

  describe('post', () => {
    it('should make POST request with body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      const data = { email: 'test@example.com', password: 'secret' }
      await api.post('/api/auth/signin', data)

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/signin',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(data),
        })
      )
    })

    it('should handle POST without body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      })

      await api.post('/api/trigger')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/trigger',
        expect.objectContaining({
          method: 'POST',
          body: undefined,
        })
      )
    })
  })

  describe('delete', () => {
    it('should make DELETE request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ deleted: true }),
      })

      await api.delete('/api/items/123')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/items/123',
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })
  })

  describe('Auth endpoints', () => {
    it('signUp should call correct endpoint with data', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ user: { id: '123' } }),
      })

      await api.signUp('test@example.com', 'password123', 'John Doe', 'Acme Inc')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/signup',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123',
            full_name: 'John Doe',
            company_name: 'Acme Inc',
          }),
        })
      )
    })

    it('signIn should call correct endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ access_token: 'token', user: {} }),
      })

      await api.signIn('test@example.com', 'password')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/signin',
        expect.objectContaining({
          method: 'POST',
        })
      )
    })

    it('getMe should call correct endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: '123', email: 'test@example.com' }),
      })

      const user = await api.getMe()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/me',
        expect.any(Object)
      )
      expect(user.id).toBe('123')
    })
  })

  describe('Agent endpoints', () => {
    it('getAgentCatalog should return agents list', async () => {
      const mockAgents = [
        { type: 'bookkeeper', name: 'BookkeeperAI', price_monthly: 199 },
      ]
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ agents: mockAgents }),
      })

      const result = await api.getAgentCatalog()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/agents/catalog',
        expect.any(Object)
      )
      expect(result.agents).toEqual(mockAgents)
    })

    it('subscribeToAgent should post to correct endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ subscription_id: 'sub_123' }),
      })

      await api.subscribeToAgent('bookkeeper', { auto_run: true })

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/agents/subscribe',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            agent_type: 'bookkeeper',
            config: { auto_run: true },
          }),
        })
      )
    })

    it('unsubscribeFromAgent should call delete endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      await api.unsubscribeFromAgent('bookkeeper')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/agents/subscribe/bookkeeper',
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })

    it('runAgent should post task correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ task_id: 'task_123' }),
      })

      const result = await api.runAgent('bookkeeper', 'categorize_transactions', {
        month: 'January',
      })

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/agents/run',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            agent_type: 'bookkeeper',
            task: 'categorize_transactions',
            context: { month: 'January' },
          }),
        })
      )
      expect(result.task_id).toBe('task_123')
    })

    it('getTasks should handle query parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ tasks: [] }),
      })

      await api.getTasks({ status: 'completed', agentType: 'bookkeeper', limit: 10 })

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/agents/tasks?status=completed&agent_type=bookkeeper&limit=10',
        expect.any(Object)
      )
    })

    it('getTasks should work without parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ tasks: [] }),
      })

      await api.getTasks()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/agents/tasks?',
        expect.any(Object)
      )
    })
  })

  describe('Integration endpoints', () => {
    it('getIntegrationStatus should return integrations', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          integrations: [{ name: 'quickbooks', connected: true }],
        }),
      })

      const result = await api.getIntegrationStatus()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/integrations/status',
        expect.any(Object)
      )
      expect(result.integrations[0].name).toBe('quickbooks')
    })

    it('connectQuickBooks should return auth URL', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ auth_url: 'https://quickbooks.com/auth' }),
      })

      const result = await api.connectQuickBooks()

      expect(result.auth_url).toBe('https://quickbooks.com/auth')
    })

    it('disconnectQuickBooks should call delete endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      await api.disconnectQuickBooks()

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/integrations/quickbooks/disconnect',
        expect.objectContaining({
          method: 'DELETE',
        })
      )
    })
  })

  describe('Task approval endpoints', () => {
    it('approveTask should post approval', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ status: 'approved' }),
      })

      await api.approveTask('task_123', true, 'Looks good!')

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/tasks/task_123/approve',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            approved: true,
            feedback: 'Looks good!',
          }),
        })
      )
    })

    it('getTaskStats should return statistics', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          total: 100,
          completed: 85,
          pending: 10,
          failed: 5,
        }),
      })

      const stats = await api.getTaskStats()

      expect(stats.total).toBe(100)
      expect(stats.completed).toBe(85)
    })
  })
})
