const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private token: string | null = null

  setToken(token: string | null) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint)
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  // Auth
  async signUp(email: string, password: string, fullName: string, companyName?: string) {
    return this.post('/api/auth/signup', { email, password, full_name: fullName, company_name: companyName })
  }

  async signIn(email: string, password: string) {
    return this.post<{ access_token: string; user: any }>('/api/auth/signin', { email, password })
  }

  async getMe() {
    return this.get<any>('/api/auth/me')
  }

  // Agents
  async getAgentCatalog() {
    return this.get<{ agents: any[] }>('/api/agents/catalog')
  }

  async getSubscriptions() {
    return this.get<{ subscriptions: any[] }>('/api/agents/subscriptions')
  }

  async subscribeToAgent(agentType: string, config?: Record<string, any>) {
    return this.post('/api/agents/subscribe', { agent_type: agentType, config })
  }

  async unsubscribeFromAgent(agentType: string) {
    return this.delete(`/api/agents/subscribe/${agentType}`)
  }

  async runAgent(agentType: string, task: string, context?: Record<string, any>) {
    return this.post<{ task_id: string }>('/api/agents/run', { agent_type: agentType, task, context })
  }

  async getTasks(options?: { status?: string; agentType?: string; limit?: number }) {
    const params = new URLSearchParams()
    if (options?.status) params.set('status', options.status)
    if (options?.agentType) params.set('agent_type', options.agentType)
    if (options?.limit) params.set('limit', options.limit.toString())
    return this.get<{ tasks: any[] }>(`/api/agents/tasks?${params}`)
  }

  async getTask(taskId: string) {
    return this.get<any>(`/api/agents/tasks/${taskId}`)
  }

  // Integrations
  async getIntegrationStatus() {
    return this.get<{ integrations: any[] }>('/api/integrations/status')
  }

  async connectQuickBooks() {
    return this.get<{ auth_url: string }>('/api/integrations/quickbooks/connect')
  }

  async disconnectQuickBooks() {
    return this.delete('/api/integrations/quickbooks/disconnect')
  }

  // Tasks
  async getPendingTasks() {
    return this.get<{ pending_tasks: any[] }>('/api/tasks/pending')
  }

  async approveTask(taskId: string, approved: boolean, feedback?: string) {
    return this.post(`/api/tasks/${taskId}/approve`, { approved, feedback })
  }

  async getTaskStats() {
    return this.get<any>('/api/tasks/stats')
  }
}

export const api = new ApiClient()
