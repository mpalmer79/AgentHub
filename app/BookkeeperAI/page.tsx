'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function BookkeeperAIPage() {
  const [input, setInput] = useState('')
  const [response, setResponse] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    if (!input.trim()) return
    setLoading(true)

    // Simulated demo response
    setTimeout(() => {
      setResponse(
        `📊 BookkeeperAI Analysis:\n\n• Detected expense categorization opportunity\n• Suggested reconciliation check\n• Flagged potential anomaly in transaction history\n\n(Connected to backend simulation)`
      )
      setLoading(false)
    }, 1200)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">

      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white shadow-sm">
        <h1 className="text-xl font-semibold">BookkeeperAI Demo</h1>
        <Link
          href="/"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Back to AgentHub
        </Link>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center px-4 py-10">
        <div className="w-full max-w-2xl bg-white rounded-xl shadow-md p-6">

          <h2 className="text-lg font-semibold mb-4">
            Autonomous Financial Assistant
          </h2>

          <p className="text-sm text-gray-600 mb-6">
            Try entering a financial request like:
            <br />
            <span className="italic">
              “Categorize last month’s transactions and flag anomalies.”
            </span>
          </p>

          {/* Input */}
          <textarea
            className="w-full border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={4}
            placeholder="Enter your financial request..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          {/* Button */}
          <button
            onClick={handleSubmit}
            className="mt-4 w-full bg-black text-white py-3 rounded-lg hover:opacity-90 transition"
          >
            {loading ? 'Analyzing...' : 'Run Demo'}
          </button>

          {/* Response */}
          {response && (
            <div className="mt-6 p-4 bg-gray-100 rounded-lg whitespace-pre-line text-sm">
              {response}
            </div>
          )}
        </div>
      </div>

    </div>
  )
}
