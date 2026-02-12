'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'
import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'

const agentImages: Record<string, string> = {
  // Original 6
  bookkeeper: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80',
  inbox_commander: 'https://images.unsplash.com/photo-1596526131083-e8c633c948d2?w=800&q=80',
  hire_well: 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&q=80',
  customer_care: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800&q=80',
  social_pilot: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&q=80',
  appointment: 'https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800&q=80',
  // New 6
  compliance_guard: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80',
  vendor_negotiator: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&q=80',
  proposal_pro: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=80',
  inventory_iq: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80',
  reputation_shield: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80',
  cashflow_commander: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&q=80',
}

const categories = ['All', 'Finance', 'Productivity', 'Sales', 'Marketing', 'Operations', 'Human Resources', 'Support', 'Legal & Compliance', 'Procurement']

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([])
  const [subscriptions, setSubscriptions] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [subscribing, setSubscribing] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState('All')

  const refreshToken = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      api.setToken(session.access_token)
      return true
    }
    return false
  }

  useEffect(() => {
    const loadData = async () => {
      try {
        const catalogData = await api.getAgentCatalog()
        setAgents(catalogData.agents)

        const hasToken = await refreshToken()
        if (hasToken) {
          try {
            const subsData = await api.getSubscriptions()
            setSubscriptions(new Set(subsData.subscriptions.map((s: any) => s.agent_type)))
          } catch (error) {
            console.error('Failed to load subscriptions:', error)
          }
        }
      } catch (error) {
        console.error('Failed to load agents:', error)
      }
      setLoading(false)
    }
    loadData()
  }, [])

  const handleSubscribe = async (agentType: string) => {
    setSubscribing(agentType)
    try {
      await refreshToken()
      await api.subscribeToAgent(agentType)
      setSubscriptions(prev => new Set([...prev, agentType]))
    } catch (error) {
      console.error('Failed to subscribe:', error)
    }
    setSubscribing(null)
  }

  const handleUnsubscribe = async (agentType: string) => {
    setSubscribing(agentType)
    try {
      await refreshToken()
      await api.unsubscribeFromAgent(agentType)
      setSubscriptions(prev => {
        const next = new Set(prev)
        next.delete(agentType)
        return next
      })
    } catch (error) {
      console.error('Failed to unsubscribe:', error)
    }
    setSubscribing(null)
  }

  const filteredAgents = selectedCategory === 'All'
    ? agents
    : agents.filter(a => a.category === selectedCategory)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-slate-200 border-t-slate-900"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Agent Marketplace</h1>
        <p className="text-slate-600">Deploy specialized AI agents to automate your business operations.</p>
      </div>

      {/* Stats Bar */}
      <div className="bg-slate-900 rounded-xl p-6 mb-8">
        <div className="flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-8">
            <div>
              <p className="text-2xl font-bold text-white">{subscriptions.size}</p>
              <p className="text-sm text-slate-400">Agents Deployed</p>
            </div>
            <div className="h-10 w-px bg-slate-700" />
            <div>
              <p className="text-2xl font-bold text-white">{agents.filter(a => a.status === 'available').length}</p>
              <p className="text-sm text-slate-400">Available Now</p>
            </div>
            <div className="h-10 w-px bg-slate-700" />
            <div>
              <p className="text-2xl font-bold text-white">{agents.length}</p>
              <p className="text-sm text-slate-400">Total Agents</p>
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              selectedCategory === category
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      {/* Agents Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {filteredAgents.map((agent) => {
          const isSubscribed = subscriptions.has(agent.type)
          const isAvailable = agent.status === 'available'
          const image = agentImages[agent.type] || 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=800&q=80'

          return (
            <div 
              key={agent.type} 
              className={`group bg-white border border-slate-200 rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-xl ${!isAvailable ? 'opacity-70' : ''}`}
            >
              <div className="aspect-[2/1] relative overflow-hidden">
                <Image
                  src={image}
                  alt={agent.name}
                  fill
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent" />
                
                {/* Category Badge */}
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 bg-white/90 backdrop-blur-sm text-slate-900 text-xs font-medium rounded-full">
                    {agent.category}
                  </span>
                </div>
                
                {/* Status Badge */}
                {isSubscribed && (
                  <div className="absolute top-4 right-4">
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500 text-white text-xs font-medium rounded-full">
                      <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                      Active
                    </span>
                  </div>
                )}
                
                {/* Title Overlay */}
                <div className="absolute bottom-4 left-4 right-4">
                  <h3 className="text-2xl font-bold text-white mb-1">{agent.name}</h3>
                  <p className="text-sm text-white/80 line-clamp-1">{agent.description}</p>
                </div>
              </div>
              
              <div className="p-6">
                {/* Features */}
                <div className="grid grid-cols-2 gap-3 mb-6">
                  {agent.features.slice(0, 4).map((feature: string, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-sm text-slate-600">
                      <svg className="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="truncate">{feature}</span>
                    </div>
                  ))}
                </div>
                
                {/* Integrations */}
                <div className="flex items-center gap-2 mb-6 pb-6 border-b border-slate-100">
                  <span className="text-xs text-slate-500">Integrates with:</span>
                  <div className="flex gap-1 flex-wrap">
                    {agent.integrations.slice(0, 3).map((integration: string) => (
                      <span key={integration} className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                        {integration}
                      </span>
                    ))}
                    {agent.integrations.length > 3 && (
                      <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded">
                        +{agent.integrations.length - 3}
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Price & Action */}
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-3xl font-bold text-slate-900">${agent.price_monthly}</span>
                    <span className="text-slate-500 ml-1">/month</span>
                  </div>
                  
                  {isAvailable ? (
                    isSubscribed ? (
                      <button
                        onClick={() => handleUnsubscribe(agent.type)}
                        disabled={subscribing === agent.type}
                        className="px-6 py-3 border border-slate-300 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition disabled:opacity-50 flex items-center gap-2"
                      >
                        {subscribing === agent.type ? (
                          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                        ) : (
                          'Unsubscribe'
                        )}
                      </button>
                    ) : (
                      <button
                        onClick={() => handleSubscribe(agent.type)}
                        disabled={subscribing === agent.type}
                        className="btn-primary py-3 px-6 disabled:opacity-50 flex items-center gap-2"
                      >
                        {subscribing === agent.type ? (
                          <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                        ) : (
                          <>
                            Deploy Agent
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </svg>
                          </>
                        )}
                      </button>
                    )
                  ) : (
                    <span className="px-6 py-3 text-slate-400 font-medium">Coming Soon</span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {filteredAgents.length === 0 && (
        <div className="text-center py-12">
          <p className="text-slate-500">No agents found in this category.</p>
          <button 
            onClick={() => setSelectedCategory('All')}
            className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            View all agents
          </button>
        </div>
      )}
    </div>
  )
}
