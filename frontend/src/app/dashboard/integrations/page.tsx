'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { 
  Link2, 
  Check, 
  ExternalLink,
  Loader2,
  AlertCircle
} from 'lucide-react'
import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'

const integrationLogos: Record<string, string> = {
  quickbooks: '🧾',
  gmail: '📧',
  google_calendar: '📅',
  slack: '💬',
  zendesk: '🎫',
}

export default function IntegrationsPage() {
  const searchParams = useSearchParams()
  const [integrations, setIntegrations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [connecting, setConnecting] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    const connected = searchParams.get('connected')
    if (connected) {
      setSuccessMessage(`Successfully connected ${connected}!`)
      setTimeout(() => setSuccessMessage(''), 5000)
    }
  }, [searchParams])

  useEffect(() => {
    const loadData = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      if (session?.access_token) {
        api.setToken(session.access_token)
        try {
          const data = await api.getIntegrationStatus()
          setIntegrations(data.integrations)
        } catch (error) {
          console.error('Failed to load integrations:', error)
        }
      }
      setLoading(false)
    }
    loadData()
  }, [])

  const handleConnect = async (integrationType: string) => {
    setConnecting(integrationType)
    try {
      if (integrationType === 'quickbooks') {
        const data = await api.connectQuickBooks()
        window.location.href = data.auth_url
      }
    } catch (error) {
      console.error('Failed to connect:', error)
      setConnecting(null)
    }
  }

  const handleDisconnect = async (integrationType: string) => {
    setConnecting(integrationType)
    try {
      if (integrationType === 'quickbooks') {
        await api.disconnectQuickBooks()
        setIntegrations(prev => 
          prev.map(int => 
            int.type === integrationType 
              ? { ...int, connected: false, account_name: null }
              : int
          )
        )
      }
    } catch (error) {
      console.error('Failed to disconnect:', error)
    }
    setConnecting(null)
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
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Integrations</h1>
        <p className="text-slate-600">Connect your tools to enable your AI agents to work with your data.</p>
      </div>

      {successMessage && (
        <div className="mb-6 flex items-center gap-3 bg-emerald-50 text-emerald-700 px-4 py-3 rounded-lg">
          <Check className="w-5 h-5" />
          {successMessage}
        </div>
      )}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.map((integration) => (
          <div key={integration.type} className="bg-white rounded-xl border border-slate-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="text-4xl">{integrationLogos[integration.type] || '🔗'}</div>
              {integration.connected && (
                <span className="flex items-center gap-1 text-sm text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                  <Check className="w-4 h-4" />
                  Connected
                </span>
              )}
            </div>

            <h3 className="text-lg font-semibold text-slate-900 mb-1">{integration.name}</h3>
            <p className="text-sm text-slate-600 mb-4">{integration.description}</p>

            {integration.connected && integration.account_name && (
              <div className="mb-4 p-3 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">Connected account:</p>
                <p className="font-medium text-slate-900">{integration.account_name}</p>
              </div>
            )}

            <div className="flex gap-3">
              {integration.connected ? (
                <button
                  onClick={() => handleDisconnect(integration.type)}
                  disabled={connecting === integration.type}
                  className="flex-1 px-4 py-2 border border-red-300 text-red-600 rounded-lg font-medium hover:bg-red-50 transition disabled:opacity-50"
                >
                  {connecting === integration.type ? (
                    <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                  ) : (
                    'Disconnect'
                  )}
                </button>
              ) : (
                <button
                  onClick={() => handleConnect(integration.type)}
                  disabled={connecting === integration.type || integration.type !== 'quickbooks'}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {connecting === integration.type ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <>
                      Connect
                      <ExternalLink className="w-4 h-4" />
                    </>
                  )}
                </button>
              )}
            </div>

            {integration.type !== 'quickbooks' && !integration.connected && (
              <p className="text-xs text-slate-400 mt-3 text-center">Coming soon</p>
            )}
          </div>
        ))}
      </div>

      <div className="mt-8 bg-amber-50 border border-amber-200 rounded-xl p-6">
        <div className="flex gap-4">
          <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-amber-800 mb-1">Integration Security</h3>
            <p className="text-sm text-amber-700">
              All integrations use OAuth 2.0 for secure authentication. We never store your passwords. 
              You can revoke access at any time from this page or from the connected service's settings.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
