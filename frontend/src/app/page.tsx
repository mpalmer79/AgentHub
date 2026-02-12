'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'

const metrics = [
  { value: '10,000+', label: 'Tasks Automated' },
  { value: '500+', label: 'Businesses Served' },
  { value: '99.9%', label: 'Uptime Reliability' },
  { value: '24/7', label: 'Autonomous Operation' },
]

const agents = [
  {
    id: 'bookkeeper',
    name: 'BookkeeperAI',
    description: 'Autonomous financial operations. Transaction categorization, reconciliation, and reporting—handled.',
    price: 199,
    capabilities: ['Transaction categorization', 'Bank reconciliation', 'Anomaly detection', 'Financial reporting'],
    category: 'Finance',
    image: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80',
    available: true
  },
  {
    id: 'inbox_commander',
    name: 'InboxCommanderAI',
    description: 'Your email, intelligently managed. Smart triage, drafted responses, and automated follow-ups.',
    price: 149,
    capabilities: ['Email triage', 'Auto-drafting', 'Follow-up scheduling', 'Priority detection'],
    category: 'Communications',
    image: 'https://images.unsplash.com/photo-1596526131083-e8c633c948d2?w=800&q=80',
    available: true
  },
  {
    id: 'hiring_hero',
    name: 'HiringHeroAI',
    description: 'From job post to offer letter. Resume screening, scheduling, and candidate communication—automated.',
    price: 249,
    capabilities: ['Resume screening', 'Interview scheduling', 'Candidate outreach', 'Pipeline management'],
    category: 'HR',
    image: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=800&q=80',
    available: true
  },
  {
    id: 'customer_care',
    name: 'CustomerCareAI',
    description: 'Support that never sleeps. Ticket triage, response generation, and escalation routing.',
    price: 179,
    capabilities: ['Ticket triage', 'Auto-responses', 'Sentiment analysis', 'Smart escalation'],
    category: 'Support',
    image: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800&q=80',
    available: true
  },
  {
    id: 'social_pilot',
    name: 'SocialPilotAI',
    description: 'Social media on autopilot. Content creation, scheduling, and engagement—without the effort.',
    price: 129,
    capabilities: ['Content creation', 'Post scheduling', 'Engagement tracking', 'Trend monitoring'],
    category: 'Marketing',
    image: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&q=80',
    available: true
  },
  {
    id: 'appointment_setter',
    name: 'AppointmentSetterAI',
    description: 'Calendar chaos, solved. Intelligent scheduling that respects your time and preferences.',
    price: 99,
    capabilities: ['Smart scheduling', 'Calendar optimization', 'Reminder automation', 'Conflict resolution'],
    category: 'Productivity',
    image: 'https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800&q=80',
    available: true
  },
  {
    id: 'compliance_guard',
    name: 'ComplianceGuardAI',
    description: 'Stay compliant, stay confident. Regulatory monitoring, deadline tracking, and audit preparation.',
    price: 349,
    capabilities: ['Regulatory monitoring', 'Deadline tracking', 'Document generation', 'Audit preparation'],
    category: 'Legal',
    image: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80',
    available: true
  },
  {
    id: 'cashflow_commander',
    name: 'CashFlowCommanderAI',
    description: 'Master your money flow. Invoice chasing, payment predictions, and cash flow optimization.',
    price: 279,
    capabilities: ['Invoice management', 'Payment prediction', 'Cash flow forecasting', 'Collection automation'],
    category: 'Finance',
    image: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&q=80',
    available: true
  },
  {
    id: 'vendor_negotiator',
    name: 'VendorNegotiatorAI',
    description: 'Better deals, less effort. Contract analysis, renewal tracking, and negotiation support.',
    price: 299,
    capabilities: ['Contract analysis', 'Price benchmarking', 'Renewal tracking', 'Negotiation briefs'],
    category: 'Operations',
    image: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&q=80',
    available: true
  },
  {
    id: 'reputation_guardian',
    name: 'ReputationGuardianAI',
    description: 'Protect and grow your reputation. Review monitoring, response generation, and sentiment tracking.',
    price: 159,
    capabilities: ['Review monitoring', 'Response generation', 'Sentiment analysis', 'Competitor tracking'],
    category: 'Marketing',
    image: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&q=80',
    available: true
  },
  {
    id: 'inventory_intel',
    name: 'InventoryIntelAI',
    description: 'Stock smarter, not harder. Demand forecasting, reorder automation, and waste reduction.',
    price: 229,
    capabilities: ['Demand forecasting', 'Reorder automation', 'Waste tracking', 'Supplier management'],
    category: 'Operations',
    image: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80',
    available: true
  },
  {
    id: 'proposal_pro',
    name: 'ProposalProAI',
    description: 'Win more deals. Proposal generation, pricing optimization, and follow-up automation.',
    price: 199,
    capabilities: ['Proposal generation', 'Pricing analysis', 'Win rate tracking', 'Follow-up automation'],
    category: 'Sales',
    image: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80',
    available: true
  },
]

const testimonials = [
  {
    quote: "AgentHub's BookkeeperAI saved us 20+ hours per week on financial operations. It's like having a tireless accountant on staff.",
    author: 'Michael Torres',
    role: 'CFO',
    company: 'Meridian Consulting',
    image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&q=80'
  },
  {
    quote: "The CustomerCareAI handles 80% of our support tickets automatically. Our team can finally focus on complex issues that matter.",
    author: 'Sarah Chen',
    role: 'Head of Support',
    company: 'TechStart Inc.',
    image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80'
  },
  {
    quote: "HiringHeroAI screened 500 resumes in hours, not weeks. We found our perfect candidate faster than ever before.",
    author: 'David Park',
    role: 'VP of People',
    company: 'GrowthLabs',
    image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80'
  },
]

const howItWorks = [
  {
    step: '01',
    title: 'Connect Your Tools',
    description: 'Integrate with QuickBooks, Gmail, Slack, and 50+ other business tools in minutes.'
  },
  {
    step: '02',
    title: 'Deploy Your Agents',
    description: 'Choose the AI agents that match your needs. Each is pre-trained for its specific domain.'
  },
  {
    step: '03',
    title: 'Review & Approve',
    description: 'Agents work autonomously but you stay in control. Approve actions when needed.'
  },
]

export default function HomePage() {
  const [scrolled, setScrolled] = useState(false)
  const [activeCategory, setActiveCategory] = useState('All')

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const categories = ['All', ...new Set(agents.map(a => a.category))]
  const filteredAgents = activeCategory === 'All' 
    ? agents 
    : agents.filter(a => a.category === activeCategory)

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-white/90 backdrop-blur-xl shadow-sm' : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-semibold tracking-tight">AgentHub</span>
            </Link>
            
            <div className="hidden md:flex items-center gap-10">
              <a href="#solutions" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Solutions</a>
              <a href="#how-it-works" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">How It Works</a>
              <a href="#testimonials" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Testimonials</a>
            </div>
            
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">
                Sign In
              </Link>
              <Link href="/signup" className="btn-primary text-sm">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 lg:pt-40 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-slate-50 to-white" />
        <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-blue-50/50 to-transparent" />
        
        <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="opacity-0 animate-fade-in-up">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-100 rounded-full mb-8">
                <span className="w-2 h-2 bg-emerald-500 rounded-full status-pulse" />
                <span className="text-sm font-medium text-slate-700">Now accepting beta users</span>
              </div>
              
              <h1 className="text-display font-bold text-slate-900 mb-6">
                Autonomous AI<br />
                <span className="gradient-text-accent">for Modern Business</span>
              </h1>
              
              <p className="text-subheadline text-slate-600 mb-10 max-w-lg">
                Deploy intelligent agents that handle your bookkeeping, email, hiring, and customer support—autonomously.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/signup" className="btn-primary inline-flex items-center justify-center gap-2">
                  Start Free Trial
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
                <a href="#solutions" className="btn-secondary inline-flex items-center justify-center gap-2">
                  View All Agents
                </a>
              </div>
            </div>
            
            <div className="relative opacity-0 animate-fade-in-up animate-delay-200">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <Image
                  src="https://images.unsplash.com/photo-1551434678-e076c223a692?w=1200&q=80"
                  alt="Team collaborating with AI"
                  width={600}
                  height={400}
                  className="w-full object-cover"
                  priority
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 to-transparent" />
                
                {/* Floating metrics card */}
                <div className="absolute bottom-6 left-6 right-6 glass rounded-xl p-4">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-slate-900">247 tasks completed today</p>
                      <p className="text-xs text-slate-600">Across all active agents</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-blue-100 rounded-full blur-3xl opacity-60" />
              <div className="absolute -bottom-4 -left-4 w-32 h-32 bg-purple-100 rounded-full blur-3xl opacity-60" />
            </div>
          </div>
        </div>
      </section>

      {/* Metrics Bar */}
      <section className="py-12 bg-slate-900">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {metrics.map((metric, i) => (
              <div key={i} className="text-center">
                <p className="text-3xl lg:text-4xl font-bold text-white mb-1">{metric.value}</p>
                <p className="text-sm text-slate-400">{metric.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solutions / Agents Grid */}
      <section id="solutions" className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-headline font-bold text-slate-900 mb-4">
              AI Agents for Every Business Function
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Choose from our library of purpose-built AI agents. Each is trained for its specific domain and integrates seamlessly with your existing tools.
            </p>
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-2 mb-12">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                  activeCategory === cat
                    ? 'bg-slate-900 text-white'
                    : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Agents Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredAgents.map((agent, i) => (
              <Link
                key={agent.id}
                href={`/${agent.id}`}
                className="group bg-white rounded-2xl overflow-hidden shadow-soft card-hover border border-slate-100"
              >
                <div className="relative h-48 overflow-hidden">
                  <Image
                    src={agent.image}
                    alt={agent.name}
                    fill
                    className="object-cover group-hover:scale-105 transition duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/20 to-transparent" />
                  <div className="absolute top-4 left-4">
                    <span className="px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full text-xs font-medium text-slate-700">
                      {agent.category}
                    </span>
                  </div>
                  <div className="absolute bottom-4 left-4 right-4">
                    <h3 className="text-xl font-bold text-white mb-1">{agent.name}</h3>
                    <p className="text-sm text-white/80 line-clamp-2">{agent.description}</p>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="flex flex-wrap gap-2 mb-4">
                    {agent.capabilities.slice(0, 3).map((cap, j) => (
                      <span key={j} className="px-2 py-1 bg-slate-100 rounded text-xs text-slate-600">
                        {cap}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-2xl font-bold text-slate-900">${agent.price}</span>
                      <span className="text-sm text-slate-500">/month</span>
                    </div>
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-slate-900 group-hover:text-blue-600 transition">
                      Learn More
                      <svg className="w-4 h-4 group-hover:translate-x-1 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                      </svg>
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-headline font-bold text-slate-900 mb-4">
              Up and Running in Minutes
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              No complex setup. No coding required. Just connect, deploy, and let AI handle the rest.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {howItWorks.map((item, i) => (
              <div key={i} className="relative">
                <div className="text-6xl font-bold text-slate-100 mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">{item.title}</h3>
                <p className="text-slate-600">{item.description}</p>
                
                {i < howItWorks.length - 1 && (
                  <div className="hidden md:block absolute top-10 right-0 w-1/2 h-px bg-slate-200" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 bg-slate-900">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-headline font-bold text-white mb-4">
              Trusted by Growing Businesses
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              See how companies are transforming their operations with AgentHub.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, i) => (
              <div key={i} className="bg-slate-800/50 rounded-2xl p-8 border border-slate-700">
                <div className="flex items-center gap-1 mb-6">
                  {[...Array(5)].map((_, j) => (
                    <svg key={j} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                
                <blockquote className="text-lg text-white mb-6 leading-relaxed">
                  "{testimonial.quote}"
                </blockquote>
                
                <div className="flex items-center gap-4">
                  <div className="relative w-12 h-12 rounded-full overflow-hidden">
                    <Image
                      src={testimonial.image}
                      alt={testimonial.author}
                      fill
                      className="object-cover"
                    />
                  </div>
                  <div>
                    <p className="font-semibold text-white">{testimonial.author}</p>
                    <p className="text-sm text-slate-400">{testimonial.role}, {testimonial.company}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <h2 className="text-headline font-bold text-slate-900 mb-6">
            Ready to Transform Your Operations?
          </h2>
          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
            Join forward-thinking businesses that are automating operations and scaling efficiently with AgentHub.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/signup" className="btn-primary inline-flex items-center justify-center gap-2">
              Start Free Trial
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
            <a href="#solutions" className="btn-secondary inline-flex items-center justify-center gap-2">
              View All Agents
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 bg-slate-50 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <Link href="/" className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">A</span>
                </div>
                <span className="text-xl font-semibold">AgentHub</span>
              </Link>
              <p className="text-slate-600 text-sm">
                Autonomous AI agents for modern business operations.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold text-slate-900 mb-4">Product</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#solutions" className="text-slate-600 hover:text-slate-900 transition">All Agents</a></li>
                <li><a href="#how-it-works" className="text-slate-600 hover:text-slate-900 transition">How It Works</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Pricing</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Integrations</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-slate-900 mb-4">Company</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">About</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Blog</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Careers</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold text-slate-900 mb-4">Legal</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Privacy Policy</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Terms of Service</a></li>
                <li><a href="#" className="text-slate-600 hover:text-slate-900 transition">Security</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-slate-200 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-500">© 2026 AgentHub. All rights reserved.</p>
            <div className="flex gap-6">
              <a href="#" className="text-slate-400 hover:text-slate-600 transition">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
              </a>
              <a href="#" className="text-slate-400 hover:text-slate-600 transition">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
