'use client'

import { useEffect, useState } from 'react'
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  XCircle,
  Play,
  ChevronDown,
  ChevronUp,
  Loader2,
  RefreshCw
} from 'lucide-react'
import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'

const statusConfig: Record<string, { icon: any; color: string; bg: string }> = {
  completed: { icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  running: { icon: Play, color: 'text-blue-600', bg: 'bg-blue-50' },
  pending: { icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
  awaiting_approval: { icon: Clock, color: 'text-purple-600', bg: 'bg-purple-50' },
  failed: { icon: XCircle, color: 'text-red-600', bg: 'bg-red-50' },
  cancelled: { icon: AlertCircle, color: 'text-slate-600', bg: 'bg-slate-50' },
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedTask, setExpandedTask] = useState<string | null>(null)
  const [filter, setFilter] = useState('all')

  const loadTasks = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      api.setToken(session.access_token)
      try {
        const options: any = { limit: 50 }
        if (filter !== 'all') options.status = filter
        const data = await api.getTasks(options)
        setTasks(data.tasks)
      } catch (error) {
        console.error('Failed to load tasks:', error)
      }
    }
    setLoading(false)
  }

  useEffect(() => {
    loadTasks()
  }, [filter])

  const handleApprove = async (taskId: string, approved: boolean) => {
    try {
      await api.approveTask(taskId, approved)
      loadTasks()
    } catch (error) {
      console.error('Failed to approve task:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Tasks</h1>
          <p className="text-slate-600">Monitor and manage your AI agent tasks.</p>
        </div>
        <button 
          onClick={loadTasks}
          className="flex items-center gap-2 px-4 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {['all', 'pending', 'running', 'awaiting_approval', 'completed', 'failed'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition ${
              filter === status
                ? 'bg-primary-600 text-white'
                : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
            }`}
          >
            {status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      {tasks.length > 0 ? (
        <div className="space-y-4">
          {tasks.map((task) => {
            const config = statusConfig[task.status] || statusConfig.pending
            const StatusIcon = config.icon
            const isExpanded = expandedTask === task.id

            return (
              <div key={task.id} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <div 
                  className="p-6 cursor-pointer hover:bg-slate-50 transition"
                  onClick={() => setExpandedTask(isExpanded ? null : task.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className={`w-10 h-10 ${config.bg} ${config.color} rounded-lg flex items-center justify-center`}>
                        <StatusIcon className="w-5 h-5" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{task.task}</p>
                        <p className="text-sm text-slate-500">
                          {task.agent_type} • {new Date(task.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 ${config.bg} ${config.color} text-sm font-medium rounded-full`}>
                        {task.status.replace('_', ' ')}
                      </span>
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                      )}
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="px-6 pb-6 border-t border-slate-100">
                    <div className="pt-4 space-y-4">
                      {task.context && Object.keys(task.context).length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-slate-700 mb-2">Context</h4>
                          <pre className="bg-slate-50 p-3 rounded-lg text-sm text-slate-600 overflow-x-auto">
                            {JSON.stringify(task.context, null, 2)}
                          </pre>
                        </div>
                      )}

                      {task.result && (
                        <div>
                          <h4 className="text-sm font-medium text-slate-700 mb-2">Result</h4>
                          <pre className="bg-slate-50 p-3 rounded-lg text-sm text-slate-600 overflow-x-auto">
                            {typeof task.result === 'string' ? task.result : JSON.stringify(task.result, null, 2)}
                          </pre>
                        </div>
                      )}

                      {task.error && (
                        <div>
                          <h4 className="text-sm font-medium text-red-700 mb-2">Error</h4>
                          <pre className="bg-red-50 p-3 rounded-lg text-sm text-red-600 overflow-x-auto">
                            {task.error}
                          </pre>
                        </div>
                      )}

                      {task.status === 'awaiting_approval' && (
                        <div className="flex gap-3 pt-2">
                          <button
                            onClick={(e) => { e.stopPropagation(); handleApprove(task.id, true); }}
                            className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition"
                          >
                            Approve
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleApprove(task.id, false); }}
                            className="flex-1 px-4 py-2 border border-red-300 text-red-600 rounded-lg font-medium hover:bg-red-50 transition"
                          >
                            Reject
                          </button>
                        </div>
                      )}

                      <div className="text-xs text-slate-400 pt-2">
                        Task ID: {task.id}
                        {task.completed_at && ` • Completed: ${new Date(task.completed_at).toLocaleString()}`}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
          <Clock className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No tasks found</h3>
          <p className="text-slate-600">
            {filter === 'all' 
              ? 'Tasks will appear here once your agents start working.'
              : `No ${filter.replace('_', ' ')} tasks found.`
            }
          </p>
        </div>
      )}
    </div>
  )
}
