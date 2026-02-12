'use client'

import { useEffect, useState } from 'react'
import { User, Building, Bell, Shield, Loader2, Save } from 'lucide-react'
import { supabase } from '@/lib/supabase'

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    fullName: '',
    companyName: '',
    email: ''
  })
  const [message, setMessage] = useState({ type: '', text: '' })

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user)
        setFormData({
          fullName: session.user.user_metadata?.full_name || '',
          companyName: session.user.user_metadata?.company_name || '',
          email: session.user.email || ''
        })
      }
      setLoading(false)
    })
  }, [])

  const handleSave = async () => {
    setSaving(true)
    setMessage({ type: '', text: '' })
    try {
      const { error } = await supabase.auth.updateUser({
        data: { full_name: formData.fullName, company_name: formData.companyName }
      })
      if (error) throw error
      setMessage({ type: 'success', text: 'Settings saved successfully!' })
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to save settings' })
    }
    setSaving(false)
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
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-600">Manage your account and preferences.</p>
      </div>

      {message.text && (
        <div className={`mb-6 px-4 py-3 rounded-lg ${message.type === 'success' ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700'}`}>
          {message.text}
        </div>
      )}

      <div className="space-y-6">
        <div className="bg-white rounded-xl border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <User className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-900">Profile</h2>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
              <input type="text" value={formData.fullName} onChange={(e) => setFormData({ ...formData, fullName: e.target.value })} className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
              <input type="email" value={formData.email} disabled className="w-full px-4 py-2 border border-slate-200 rounded-lg bg-slate-50 text-slate-500" />
              <p className="text-sm text-slate-500 mt-1">Contact support to change your email</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <Building className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-900">Company</h2>
            </div>
          </div>
          <div className="p-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Company Name</label>
              <input type="text" value={formData.companyName} onChange={(e) => setFormData({ ...formData, companyName: e.target.value })} className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <Bell className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-900">Notifications</h2>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <label className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">Task Completions</p>
                <p className="text-sm text-slate-500">Get notified when agents complete tasks</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
            </label>
            <label className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">Approval Requests</p>
                <p className="text-sm text-slate-500">Get notified when agents need your approval</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
            </label>
            <label className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">Weekly Reports</p>
                <p className="text-sm text-slate-500">Receive weekly summaries of agent activity</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
            </label>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200">
          <div className="p-6 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-slate-600" />
              <h2 className="text-lg font-semibold text-slate-900">Security</h2>
            </div>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">Password</p>
                <p className="text-sm text-slate-500">Last changed: Never</p>
              </div>
              <button className="px-4 py-2 text-primary-600 font-medium hover:bg-primary-50 rounded-lg transition">Change Password</button>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-slate-900">Two-Factor Authentication</p>
                <p className="text-sm text-slate-500">Add an extra layer of security</p>
              </div>
              <button className="px-4 py-2 text-primary-600 font-medium hover:bg-primary-50 rounded-lg transition">Enable 2FA</button>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button onClick={handleSave} disabled={saving} className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50">
            {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
            Save Changes
          </button>
        </div>
      </div>
    </div>
  )
}
