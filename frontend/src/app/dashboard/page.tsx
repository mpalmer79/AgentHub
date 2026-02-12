'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'

const agentInfo: Record<string, { name: string, image: string, category: string }> = {
  // Original 6
  bookkeeper: { 
    name: 'BookkeeperAI', 
    image: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&q=80',
    category: 'Finance'
  },
  inbox_commander: { 
    name: 'InboxCommanderAI', 
    image: 'https://images.unsplash.com/photo-1596526131083-e8c633c948d2?w=400&q=80',
    category: 'Productivity'
  },
  hire_well: { 
    name: 'HireWellAI', 
    image: 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=400&q=80',
    category: 'Human Resources'
  },
  customer_care: { 
    name: 'CustomerCareAI', 
    image: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&q=80',
    category: 'Support'
  },
  social_pilot: { 
    name: 'SocialPilotAI', 
    image: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&q=80',
    category: 'Marketing'
  },
  appointment: { 
    name: 'AppointmentAI', 
    image: 'https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=400&q=80',
    category: 'Productivity'
  },
  // New 6
  compliance_guard: { 
    name: 'ComplianceGuardAI', 
    image: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=400&q=80',
    category: 'Legal & Compliance'
  },
  vendor_negotiator: { 
    name: 'VendorNegotiatorAI', 
    image: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&q=80',
    category: 'Procurement'
  },
  proposal_pro: { 
    name: 'ProposalProAI', 
    image: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=400&q=80',
    category: 'Sales'
  },
  inventory_iq: { 
    name: 'InventoryIQAI', 
    image: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400&q=80',
    category: 'Operations'
  },
  reputation_shield: { 
    name: 'ReputationShieldAI', 
    image: 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&q=80',
    category: 'Marketing'
  },
  cashflow_commander: { 
    name: 'CashFlowCommanderAI', 
    image: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=400&q=80',
    category: 'Finance'
  },
}

export default function DashboardPage() {
  const [stats, setStats] = useState({ total: 0, completed: 0, pending: 0, failed: 0 })
  const [subscriptions, setSubscriptions] = useState<any[]>([])
  const [recentTasks, setRecentTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [userName, setUserName] = useState('')

  useEffect(() => {
    const loadData = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session?.access_token) {
        api.setToken(session.access_token)
        
        const name = session.user?.user_metadata?.full_name || 
                     session.user?.email?.split('@')[0] || 
                     'there'
        setUserName(name)
        
        try {
          const [statsData, subsData, tasksData] = await Promise.all([
            api.getTaskStats().catch(() => ({ total: 0, completed: 0, pending: 0, failed: 0 })),
            api.getSubscriptions().catch(() => ({ subscriptions: [] })),
            api.getTasks({ limit: 5 }).catch(() => ({ tasks: [] }))
          ])
          setStats(statsData)
          setSubscriptions(subsData.subscriptions)
          setRecentTasks(tasksData.tasks)
        } catch (error) {
          console.error('Failed to load dashboard data:', error)
        }
      }
      setLoading(false)
    }
    loadData()
  }, [])

  const estimatedTimeSaved = stats.completed * 15
  const hoursSaved = Math.floor(estimatedTimeSaved / 60)
  const minutesSaved = estimatedTimeSaved % 60

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-slate-200 border-t-slate-900"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Welcome Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome back, {userName}</h1>
        <p className="text-slate-600">Here's what's happening with your AI agents today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-500 mb-1">Active Agents</p>
          <p className="text-3xl font-bold text-slate-900">{subscriptions.length}</p>
          <p className="text-xs text-slate-400 mt-1">of 12 available</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-500 mb-1">Tasks Completed</p>
          <p className="text-3xl font-bold text-emerald-600">{stats.completed}</p>
          <p className="text-xs text-slate-400 mt-1">this month</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-500 mb-1">In Progress</p>
          <p className="text-3xl font-bold text-blue-600">{stats.pending}</p>
          <p className="text-xs text-slate-400 mt-1">tasks running</p>
        </div>
        <div className="bg-white rounded-xl p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-500 mb-1">Time Saved</p>
          <p className="text-3xl font-bold text-slate-900">
            {hoursSaved > 0 ? `${hoursSaved}h` : `${minutesSaved}m`}
          </p>
          <p className="text-xs text-slate-400 mt-1">estimated</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Deployed Agents */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-900">Deployed Agents</h2>
            <Link href="/dashboard/agents" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition flex items-center gap-1">
              View All
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
          
          {subscriptions.length > 0 ? (
            <div className="grid sm:grid-cols-2 gap-4">
              {subscriptions.map((sub) => {
                const agent = agentInfo[sub.agent_type] || { 
                  name: sub.agent_type, 
                  image: 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&q=80',
                  category: 'General'
                }
                const daysSinceDeployment = Math.floor((Date.now() - new Date(sub.created_at).getTime()) / (1000 * 60 * 60 * 24))
                
                return (
                  <div key={sub.id} className="group bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-lg transition-all duration-300">
                    <div className="aspect-[16/9] relative overflow-hidden">
                      <Image
                        src={agent.image}
                        alt={agent.name}
                        fill
                        className="object-cover transition-transform duration-500 group-hover:scale-105"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 to-transparent" />
                      <div className="absolute top-4 left-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-500 text-white text-xs font-medium rounded-full">
                          <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse" />
                          Active
                        </span>
                      </div>
                      <div className="absolute bottom-4 left-4">
                        <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                      </div>
                    </div>
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-slate-500">{agent.category}</span>
                        <span className="text-xs text-slate-500">
                          {daysSinceDeployment === 0 ? 'Deployed today' : `${daysSinceDeployment}d active`}
                        </span>
                      </div>
                    </div>
                  </div>
                )
              })}
              
              {/* Add More Agent Card */}
              <Link href="/dashboard/agents" className="border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center hover:border-slate-400 hover:bg-slate-50 transition group min-h-[200px]">
                <div className="w-12 h-12 bg-slate-100 group-hover:bg-slate-200 rounded-full flex items-center justify-center mb-4 transition">
                  <svg className="w-6 h-6 text-slate-400 group-hover:text-slate-600 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <p className="font-medium text-slate-600 group-hover:text-slate-900 transition">Deploy New Agent</p>
                <p className="text-sm text-slate-400">Browse marketplace</p>
              </Link>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-xl p-12 text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">No agents deployed yet</h3>
              <p className="text-slate-600 mb-6 max-w-sm mx-auto">
                Deploy your first AI agent to start automating your business operations.
              </p>
              <Link href="/dashboard/agents" className="btn-primary inline-flex items-center gap-2">
                Browse Agent Marketplace
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </Link>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Performance Card */}
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Performance</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-600">Success Rate</span>
                  <span className="font-semibold text-slate-900">
                    {stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 100}%
                  </span>
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                    style={{ width: `${stats.total > 0 ? (stats.completed / stats.total) * 100 : 100}%` }}
                  />
                </div>
              </div>
              <div className="pt-4 border-t border-slate-100 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Total Tasks</span>
                  <span className="font-medium text-slate-900">{stats.total}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Failed</span>
                  <span className="font-medium text-red-600">{stats.failed}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-slate-900 rounded-xl p-6 text-white">
            <h3 className="font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Link href="/dashboard/agents" className="flex items-center gap-3 p-3 bg-white/10 rounded-lg hover:bg-white/20 transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                </svg>
                <span className="text-sm font-medium">Deploy New Agent</span>
              </Link>
              <Link href="/dashboard/integrations" className="flex items-center gap-3 p-3 bg-white/10 rounded-lg hover:bg-white/20 transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                <span className="text-sm font-medium">Connect Integration</span>
              </Link>
              <Link href="/dashboard/tasks" className="flex items-center gap-3 p-3 bg-white/10 rounded-lg hover:bg-white/20 transition">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span className="text-sm font-medium">View All Tasks</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-10">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-slate-900">Recent Activity</h2>
          <Link href="/dashboard/tasks" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition flex items-center gap-1">
            View All
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
        
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          {recentTasks.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {recentTasks.map((task) => {
                const agent = agentInfo[task.agent_type] || { name: task.agent_type, category: 'General' }
                
                return (
                  <div key={task.id} className="p-5 hover:bg-slate-50 transition">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                        task.status === 'completed' ? 'bg-emerald-100' :
                        task.status === 'failed' ? 'bg-red-100' :
                        task.status === 'running' ? 'bg-blue-100' :
                        'bg-amber-100'
                      }`}>
                        {task.status === 'completed' && (
                          <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                        {task.status === 'running' && (
                          <svg className="w-5 h-5 text-blue-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        )}
                        {task.status === 'pending' && (
                          <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                        {task.status === 'failed' && (
                          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-900 truncate">{task.task}</p>
                        <p className="text-sm text-slate-500 mt-1">
                          {agent.name} &middot; {new Date(task.created_at).toLocaleString()}
                        </p>
                      </div>
                      <span className={`flex-shrink-0 px-3 py-1 text-xs font-medium rounded-full ${
                        task.status === 'completed' ? 'bg-emerald-100 text-emerald-700' :
                        task.status === 'failed' ? 'bg-red-100 text-red-700' :
                        task.status === 'running' ? 'bg-blue-100 text-blue-700' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="p-12 text-center">
              <svg className="w-12 h-12 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="font-semibold text-slate-900 mb-1">No activity yet</h3>
              <p className="text-slate-500 text-sm">Tasks will appear here once your agents start processing work.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
