'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { supabase } from '@/lib/supabase'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const { error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (signInError) throw signInError
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 lg:p-16">
        <div className="w-full max-w-md">
          <Link href="/" className="flex items-center gap-3 mb-12">
            <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <span className="text-xl font-semibold tracking-tight">AgentHub</span>
          </Link>

          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome back</h1>
            <p className="text-slate-600">Sign in to access your AI agents and dashboard.</p>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-slate-900 outline-none transition text-slate-900 placeholder:text-slate-400"
                placeholder="name@company.com"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-slate-700">Password</label>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition">
                  Forgot password?
                </a>
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3.5 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-slate-900 outline-none transition text-slate-900"
                placeholder="Enter your password"
              />
            </div>

            <div className="flex items-center gap-2">
              <input 
                type="checkbox" 
                id="remember"
                className="w-4 h-4 rounded border-slate-300 text-slate-900 focus:ring-slate-900" 
              />
              <label htmlFor="remember" className="text-sm text-slate-600">
                Keep me signed in
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-4 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                <>
                  Sign In
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </>
              )}
            </button>
          </form>

          <p className="text-sm text-slate-600 mt-8 text-center">
            Don't have an account?{' '}
            <Link href="/signup" className="font-medium text-slate-900 hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>

      {/* Right side - Image */}
      <div className="hidden lg:block lg:flex-1 relative">
        <Image
          src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80"
          alt="Modern office"
          fill
          className="object-cover"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-r from-slate-900/80 to-slate-900/40" />
        
        <div className="absolute inset-0 flex items-center justify-center p-16">
          <div className="max-w-md text-white">
            <blockquote className="text-2xl font-medium leading-relaxed mb-8">
              "AgentHub transformed how we handle operations. What used to take our team hours now happens automatically."
            </blockquote>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
                <span className="text-lg font-semibold">SC</span>
              </div>
              <div>
                <p className="font-semibold">Sarah Chen</p>
                <p className="text-sm text-white/70">CFO, TechStart Inc.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
