'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'

export default function BookkeeperAI() {
  const [demoOutput, setDemoOutput] = useState<string | null>(null)

  const runDemo = () => {
    setDemoOutput("Analyzing transactions...\nCategorizing expenses...\nReconciling bank statements...\n\n✅ Month-end report generated.\nCash flow stable.\n3 anomalies flagged for review.")
  }

  return (
    <div className="min-h-screen bg-white">

      {/* Top Navigation */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-6">
        <Link
          href="/"
          className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-slate-900 transition"
        >
          ← Back to Home
        </Link>
      </div>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 lg:px-8 pb-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">

          <div>
            <h1 className="text-4xl lg:text-5xl font-bold text-slate-900 mb-6">
              BookkeeperAI
            </h1>

            <p className="text-lg text-slate-600 mb-8 leading-relaxed">
              Autonomous bookkeeping built for modern businesses. Categorize transactions,
              reconcile accounts, detect anomalies, and generate real-time financial reports —
              without manual intervention.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/signup"
                className="bg-slate-900 text-white px-6 py-3 rounded-lg font-semibold hover:bg-slate-800 transition text-center"
              >
                Start BookkeeperAI
              </Link>

              <button
                onClick={runDemo}
                className="border border-slate-300 px-6 py-3 rounded-lg font-semibold hover:bg-slate-100 transition"
              >
                Run Interactive Demo
              </button>
            </div>
          </div>

          <div className="relative aspect-[4/3] rounded-2xl overflow-hidden shadow-xl">
            <Image
              src="https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80"
              alt="Financial analytics dashboard"
              fill
              className="object-cover"
              priority
            />
          </div>

        </div>
      </section>

      {/* Interactive Demo Panel */}
      {demoOutput && (
        <section className="bg-slate-50 py-12">
          <div className="max-w-4xl mx-auto px-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
              <h2 className="text-xl font-semibold text-slate-900 mb-4">
                Live Simulation Output
              </h2>
              <pre className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                {demoOutput}
              </pre>
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">

          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              What BookkeeperAI Handles
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Designed to eliminate repetitive accounting tasks while improving
              financial accuracy and visibility.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">

            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
              <div className="aspect-[16/10] relative">
                <Image
                  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80"
                  alt="Transaction analysis"
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Smart Categorization
                </h3>
                <p className="text-sm text-slate-600">
                  Automatically classifies expenses and income with high accuracy.
                </p>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
              <div className="aspect-[16/10] relative">
                <Image
                  src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1200&q=80"
                  alt="Financial team meeting"
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Real-Time Reconciliation
                </h3>
                <p className="text-sm text-slate-600">
                  Matches transactions and flags discrepancies instantly.
                </p>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
              <div className="aspect-[16/10] relative">
                <Image
                  src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80"
                  alt="Financial reporting"
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  Financial Reporting
                </h3>
                <p className="text-sm text-slate-600">
                  Generates profit/loss statements and balance sheets automatically.
                </p>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-slate-900 py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Automate Your Bookkeeping?
          </h2>
          <p className="text-slate-300 mb-8 text-lg">
            Deploy BookkeeperAI and eliminate manual accounting work starting today.
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center justify-center bg-white text-slate-900 px-8 py-4 rounded-lg font-semibold hover:bg-slate-100 transition"
          >
            Start BookkeeperAI
          </Link>
        </div>
      </section>

    </div>
  )
}
