'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'

// ============================================================================
// AGENT CONFIGURATION - All 12 Agents with Rich Data
// ============================================================================
const AGENT_CONFIG: Record<string, any> = {
  bookkeeper: {
    title: 'BookkeeperAI',
    tagline: 'Autonomous Financial Operations',
    heroImage: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80',
    description: 'Automate transaction categorization, reconciliation, anomaly detection, and reporting. Designed for small and medium businesses that want CFO-level clarity without the overhead.',
    longDescription: 'BookkeeperAI transforms your financial operations by automatically processing transactions, categorizing expenses, reconciling accounts, and generating comprehensive reports. Using advanced machine learning, it learns your business patterns and gets smarter over time.',
    price: 199,
    category: 'Finance',
    color: 'emerald',
    features: [
      { title: 'Auto Transaction Categorization', description: 'AI automatically categorizes every transaction with 99% accuracy, learning your unique business patterns.' },
      { title: 'Bank Reconciliation', description: 'Automatically matches transactions across accounts and flags discrepancies for review.' },
      { title: 'Anomaly Detection', description: 'Real-time alerts for unusual spending, duplicate charges, or potential fraud.' },
      { title: 'Financial Reporting', description: 'Generate P&L, cash flow, and custom reports with one click.' },
      { title: 'QuickBooks Integration', description: 'Seamless two-way sync with QuickBooks Online and Desktop.' },
      { title: 'Multi-Currency Support', description: 'Handle international transactions with automatic conversion and tracking.' },
    ],
    integrations: ['QuickBooks', 'Xero', 'Stripe', 'Plaid', 'Square', 'PayPal'],
    metrics: { tasksPerMonth: '2,400+', timeSaved: '25 hrs/week', accuracy: '99.2%' },
    useCases: [
      'Automatically categorize hundreds of daily transactions',
      'Reconcile bank statements in minutes instead of hours',
      'Get instant alerts on unusual financial activity',
      'Generate investor-ready financial reports',
    ],
    faqs: [
      { q: 'How accurate is the transaction categorization?', a: 'BookkeeperAI achieves 99.2% accuracy out of the box and improves as it learns your specific business patterns. You can also create custom rules for edge cases.' },
      { q: 'Does it replace my accountant?', a: 'BookkeeperAI handles the day-to-day bookkeeping tasks, freeing your accountant to focus on strategic financial planning and tax optimization. Most customers reduce their accounting costs by 40-60%.' },
      { q: 'How long does setup take?', a: 'Most businesses are fully operational within 24 hours. Connect your bank accounts, sync your accounting software, and BookkeeperAI starts learning immediately.' },
      { q: 'Is my financial data secure?', a: 'Absolutely. We use bank-level 256-bit encryption, SOC 2 Type II compliance, and never store your banking credentials. All data is encrypted at rest and in transit.' },
    ],
    testimonial: {
      quote: "BookkeeperAI saved us 20+ hours per week on financial operations. It's like having a tireless accountant on staff 24/7.",
      author: 'Michael Torres',
      role: 'CFO',
      company: 'Meridian Consulting',
      image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&q=80'
    },
    relatedAgents: ['cashflow_commander', 'compliance_guard', 'vendor_negotiator'],
  },
  
  inbox_commander: {
    title: 'InboxCommanderAI',
    tagline: 'Email Intelligence at Scale',
    heroImage: 'https://images.unsplash.com/photo-1596526131083-e8c633c948d2?w=1600&q=80',
    description: 'Smart email triage, drafting, follow-ups, and automated action extraction. Never miss an important email again.',
    longDescription: 'InboxCommanderAI brings order to email chaos. It intelligently prioritizes your inbox, drafts contextual responses, schedules follow-ups, and extracts action items—all while learning your communication style.',
    price: 149,
    category: 'Productivity',
    color: 'blue',
    features: [
      { title: 'Priority Inbox Sorting', description: 'AI ranks emails by urgency and importance, surfacing what matters most.' },
      { title: 'Auto-Draft Responses', description: 'Generate contextually appropriate responses in your voice and tone.' },
      { title: 'Follow-Up Scheduling', description: 'Never let a conversation fall through the cracks with smart reminders.' },
      { title: 'Action Item Extraction', description: 'Automatically identifies tasks, deadlines, and commitments from emails.' },
      { title: 'Gmail & Outlook Integration', description: 'Works seamlessly with your existing email setup.' },
      { title: 'Sentiment Analysis', description: 'Flags urgent or negative emails that need immediate attention.' },
    ],
    integrations: ['Gmail', 'Outlook', 'Slack', 'Notion', 'Asana', 'Todoist'],
    metrics: { tasksPerMonth: '5,000+', timeSaved: '15 hrs/week', accuracy: '97.8%' },
    useCases: [
      'Triage hundreds of emails to find the 10 that matter',
      'Draft professional responses in seconds',
      'Never miss a follow-up or deadline',
      'Extract action items into your task manager',
    ],
    faqs: [
      { q: 'Does it read all my emails?', a: 'InboxCommanderAI processes email metadata and content to provide intelligent assistance. All processing is encrypted and we never share or sell your data.' },
      { q: 'Can it send emails on my behalf?', a: 'By default, it drafts responses for your review. You can enable auto-send for routine responses with your approval rules.' },
      { q: 'How does it learn my writing style?', a: 'It analyzes your sent emails to understand your tone, vocabulary, and communication patterns, then mirrors them in drafts.' },
      { q: 'What about confidential emails?', a: 'You can mark certain contacts or domains as confidential, and the AI will flag but not process those emails.' },
    ],
    testimonial: {
      quote: "I went from 3 hours of email daily to 45 minutes. InboxCommanderAI surfaces exactly what I need to see.",
      author: 'Jennifer Walsh',
      role: 'CEO',
      company: 'Brightside Media',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80'
    },
    relatedAgents: ['appointment_setter', 'customer_care', 'proposal_pro'],
  },

  hiring_hero: {
    title: 'HiringHeroAI',
    tagline: 'Automated Talent Acquisition',
    heroImage: 'https://images.unsplash.com/photo-1521737604893-d14cc237f11d?w=1600&q=80',
    description: 'From resume screening to interview scheduling — streamline your entire hiring pipeline.',
    longDescription: 'HiringHeroAI transforms recruiting from a time-sink into a competitive advantage. Screen thousands of resumes in minutes, engage candidates automatically, and schedule interviews without the back-and-forth.',
    price: 249,
    category: 'Human Resources',
    color: 'violet',
    features: [
      { title: 'Resume Screening & Ranking', description: 'AI evaluates candidates against job requirements and ranks by fit score.' },
      { title: 'Interview Scheduling', description: 'Automated calendar coordination eliminates scheduling ping-pong.' },
      { title: 'Candidate Communication', description: 'Personalized outreach and updates keep candidates engaged.' },
      { title: 'ATS Integration', description: 'Works with Greenhouse, Lever, Workday, and other major ATS platforms.' },
      { title: 'Skills Matching', description: 'Identifies transferable skills and non-obvious qualified candidates.' },
      { title: 'Pipeline Analytics', description: 'Track time-to-hire, source effectiveness, and conversion rates.' },
    ],
    integrations: ['Greenhouse', 'Lever', 'LinkedIn', 'Indeed', 'Calendly', 'Zoom'],
    metrics: { tasksPerMonth: '1,200+', timeSaved: '30 hrs/week', accuracy: '94.5%' },
    useCases: [
      'Screen 500 resumes in under an hour',
      'Reduce time-to-hire by 60%',
      'Keep candidates engaged throughout the process',
      'Eliminate interview scheduling headaches',
    ],
    faqs: [
      { q: 'Does it introduce bias in hiring?', a: 'HiringHeroAI is designed to reduce bias by focusing on skills and qualifications, ignoring demographic information. Regular audits ensure fair outcomes.' },
      { q: 'Can it handle high-volume recruiting?', a: 'Absolutely. It scales effortlessly from 10 to 10,000 applicants per role.' },
      { q: 'How does candidate communication work?', a: 'You set the messaging templates and rules; the AI personalizes and sends at optimal times while maintaining your employer brand voice.' },
      { q: 'What ATS platforms do you integrate with?', a: 'We integrate with Greenhouse, Lever, Workday, BambooHR, JazzHR, and can connect to others via API.' },
    ],
    testimonial: {
      quote: "HiringHeroAI screened 500 resumes in hours, not weeks. We found our perfect candidate faster than ever.",
      author: 'David Park',
      role: 'VP of People',
      company: 'GrowthLabs',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&q=80'
    },
    relatedAgents: ['inbox_commander', 'appointment_setter', 'compliance_guard'],
  },

  customer_care: {
    title: 'CustomerCareAI',
    tagline: '24/7 Intelligent Support',
    heroImage: 'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1600&q=80',
    description: 'Deliver world-class customer service with autonomous AI that handles tickets, escalations, and satisfaction tracking.',
    longDescription: 'CustomerCareAI provides enterprise-grade support capabilities to businesses of any size. It triages tickets, generates helpful responses, identifies urgent issues, and learns from every interaction to continuously improve.',
    price: 179,
    category: 'Support',
    color: 'amber',
    features: [
      { title: 'Ticket Auto-Triage', description: 'Instantly categorize and prioritize incoming support requests.' },
      { title: 'Response Generation', description: 'Draft accurate, helpful responses based on your knowledge base.' },
      { title: 'Sentiment Analysis', description: 'Identify frustrated customers before they churn.' },
      { title: 'Smart Escalation', description: 'Route complex issues to the right team member automatically.' },
      { title: 'Knowledge Base Integration', description: 'Leverage your docs to provide accurate, consistent answers.' },
      { title: 'CSAT Tracking', description: 'Monitor satisfaction scores and identify improvement areas.' },
    ],
    integrations: ['Zendesk', 'Intercom', 'Freshdesk', 'HubSpot', 'Salesforce', 'Slack'],
    metrics: { tasksPerMonth: '8,000+', timeSaved: '40 hrs/week', accuracy: '96.1%' },
    useCases: [
      'Handle 80% of support tickets automatically',
      'Reduce first response time to under 2 minutes',
      'Identify at-risk customers proactively',
      'Scale support without scaling headcount',
    ],
    faqs: [
      { q: 'Will customers know they\'re talking to AI?', a: 'You decide. Many customers prefer the instant response, but you can configure transparent disclosure or seamless handoff to humans.' },
      { q: 'What if it gives wrong information?', a: 'CustomerCareAI only answers from your approved knowledge base. Uncertain responses are flagged for human review.' },
      { q: 'How does it handle angry customers?', a: 'Sentiment analysis detects frustration and can immediately escalate to a human agent or apply de-escalation templates you approve.' },
      { q: 'Can it process refunds or account changes?', a: 'With proper integrations and approval workflows, yes. You control exactly what actions it can take.' },
    ],
    testimonial: {
      quote: "CustomerCareAI handles 80% of our tickets automatically. Our team can finally focus on complex issues.",
      author: 'Sarah Chen',
      role: 'Head of Support',
      company: 'TechStart Inc.',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&q=80'
    },
    relatedAgents: ['reputation_guardian', 'inbox_commander', 'social_pilot'],
  },

  social_pilot: {
    title: 'SocialPilotAI',
    tagline: 'Autonomous Social Media',
    heroImage: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=1600&q=80',
    description: 'Create, schedule, and optimize social content across all platforms without lifting a finger.',
    longDescription: 'SocialPilotAI is your always-on social media team. It creates engaging content tailored to each platform, schedules posts for optimal engagement, monitors trends, and provides actionable analytics.',
    price: 129,
    category: 'Marketing',
    color: 'pink',
    features: [
      { title: 'Content Creation', description: 'Generate platform-optimized posts, captions, and hashtags.' },
      { title: 'Multi-Platform Scheduling', description: 'Publish to all your social channels from one dashboard.' },
      { title: 'Engagement Tracking', description: 'Monitor likes, shares, comments, and follower growth.' },
      { title: 'Trend Monitoring', description: 'Stay ahead with real-time trend alerts in your industry.' },
      { title: 'Analytics Dashboard', description: 'Understand what content resonates and why.' },
      { title: 'Hashtag Optimization', description: 'AI-selected hashtags for maximum reach and engagement.' },
    ],
    integrations: ['Instagram', 'Twitter/X', 'LinkedIn', 'Facebook', 'TikTok', 'Buffer'],
    metrics: { tasksPerMonth: '3,500+', timeSaved: '20 hrs/week', accuracy: '92.3%' },
    useCases: [
      'Maintain consistent posting without daily effort',
      'Create platform-specific content at scale',
      'Identify trending topics to capitalize on',
      'Optimize posting times for your audience',
    ],
    faqs: [
      { q: 'Does it create original content?', a: 'Yes! SocialPilotAI generates original posts based on your brand voice, industry trends, and content themes you specify.' },
      { q: 'Can I approve posts before publishing?', a: 'Absolutely. Set up approval workflows for any or all content. Many customers auto-publish routine content and review strategic posts.' },
      { q: 'Does it respond to comments?', a: 'It can draft responses to comments and DMs. You choose whether to auto-respond or review first.' },
      { q: 'How does it handle multiple brands?', a: 'Easily. Each brand gets its own voice profile, content themes, and publishing schedule.' },
    ],
    testimonial: {
      quote: "We went from posting twice a week to twice a day. Engagement is up 340% and I spend 10 minutes on social instead of 2 hours.",
      author: 'Amanda Rodriguez',
      role: 'Marketing Director',
      company: 'Bloom Beauty',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&q=80'
    },
    relatedAgents: ['reputation_guardian', 'customer_care', 'proposal_pro'],
  },

  appointment_setter: {
    title: 'AppointmentSetterAI',
    tagline: 'Smart Scheduling',
    heroImage: 'https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=1600&q=80',
    description: 'Automated booking, reminders, and rescheduling that respects everyone\'s time.',
    longDescription: 'AppointmentSetterAI eliminates scheduling friction. It handles the back-and-forth of finding meeting times, sends smart reminders, manages reschedules, and optimizes your calendar for productivity.',
    price: 99,
    category: 'Productivity',
    color: 'cyan',
    features: [
      { title: 'Intelligent Scheduling', description: 'Find optimal meeting times considering all participants\' preferences.' },
      { title: 'Calendar Sync', description: 'Real-time sync with Google Calendar, Outlook, and Apple Calendar.' },
      { title: 'Automated Reminders', description: 'Smart reminder sequences that reduce no-shows by 80%.' },
      { title: 'Conflict Detection', description: 'Prevent double-booking and respect buffer times.' },
      { title: 'Time Zone Handling', description: 'Seamless scheduling across any time zone.' },
      { title: 'Buffer Time Management', description: 'Automatically add travel or prep time between meetings.' },
    ],
    integrations: ['Google Calendar', 'Outlook', 'Calendly', 'Zoom', 'Teams', 'Slack'],
    metrics: { tasksPerMonth: '4,200+', timeSaved: '10 hrs/week', accuracy: '99.5%' },
    useCases: [
      'Eliminate scheduling email ping-pong',
      'Reduce meeting no-shows dramatically',
      'Protect focus time with smart blocking',
      'Handle complex multi-party scheduling',
    ],
    faqs: [
      { q: 'How is this different from Calendly?', a: 'AppointmentSetterAI is proactive—it reaches out to schedule, handles rescheduling conversations, and integrates with your other AgentHub agents.' },
      { q: 'Can it handle recurring meetings?', a: 'Yes, including complex patterns and automatic rescheduling when conflicts arise.' },
      { q: 'Does it work for team scheduling?', a: 'Absolutely. It can find times that work across multiple team members\' calendars.' },
      { q: 'What about last-minute cancellations?', a: 'It automatically offers rescheduling options and can fill newly-opened slots from a waitlist.' },
    ],
    testimonial: {
      quote: "I used to spend an hour a day on scheduling. Now it just happens. AppointmentSetterAI paid for itself in the first week.",
      author: 'Robert Kim',
      role: 'Sales Director',
      company: 'Apex Solutions',
      image: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&q=80'
    },
    relatedAgents: ['inbox_commander', 'hiring_hero', 'customer_care'],
  },

  compliance_guard: {
    title: 'ComplianceGuardAI',
    tagline: 'Regulation Monitoring Engine',
    heroImage: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1600&q=80',
    description: 'Stay compliant with automated regulatory monitoring, deadline tracking, and audit preparation.',
    longDescription: 'ComplianceGuardAI keeps you ahead of regulatory requirements. It monitors changes in laws and regulations, tracks compliance deadlines, generates required documentation, and prepares you for audits.',
    price: 349,
    category: 'Legal & Compliance',
    color: 'slate',
    features: [
      { title: 'Regulatory Change Alerts', description: 'Real-time notifications when relevant regulations change.' },
      { title: 'Deadline Tracking', description: 'Never miss a filing deadline, renewal, or compliance milestone.' },
      { title: 'Document Generation', description: 'Auto-generate policies, disclosures, and compliance documents.' },
      { title: 'Audit Trail Logging', description: 'Maintain complete records for audit readiness.' },
      { title: 'Policy Management', description: 'Track policy versions, acknowledgments, and updates.' },
      { title: 'Risk Assessment', description: 'Identify compliance gaps before they become problems.' },
    ],
    integrations: ['DocuSign', 'Google Workspace', 'Microsoft 365', 'Dropbox', 'Box', 'Notion'],
    metrics: { tasksPerMonth: '800+', timeSaved: '15 hrs/week', accuracy: '99.8%' },
    useCases: [
      'Monitor regulatory changes affecting your industry',
      'Generate compliant privacy policies and terms',
      'Track license renewals and certifications',
      'Prepare comprehensive audit packages',
    ],
    faqs: [
      { q: 'What regulations do you cover?', a: 'GDPR, CCPA, HIPAA, SOX, PCI-DSS, and industry-specific regulations. We continuously expand coverage based on customer needs.' },
      { q: 'Is this legal advice?', a: 'No. ComplianceGuardAI is a monitoring and tracking tool. We recommend working with legal counsel for interpretation and strategy.' },
      { q: 'How quickly do you alert on changes?', a: 'Typically within 24-48 hours of official publication, with analysis of how it affects your business.' },
      { q: 'Can it handle multiple jurisdictions?', a: 'Yes. Track compliance across federal, state, and international requirements simultaneously.' },
    ],
    testimonial: {
      quote: "We used to spend $50K/year on compliance consultants. ComplianceGuardAI handles 80% of that work for a fraction of the cost.",
      author: 'Patricia Huang',
      role: 'General Counsel',
      company: 'Finova Capital',
      image: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=200&q=80'
    },
    relatedAgents: ['bookkeeper', 'vendor_negotiator', 'hiring_hero'],
  },

  cashflow_commander: {
    title: 'CashFlowCommanderAI',
    tagline: 'Predictive Cash Intelligence',
    heroImage: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1600&q=80',
    description: 'Project cash flow 30/60/90 days out and prevent liquidity crunches before they happen.',
    longDescription: 'CashFlowCommanderAI gives you a crystal ball for your finances. It predicts cash positions, identifies potential shortfalls, automates collections, and helps you make confident financial decisions.',
    price: 279,
    category: 'Finance',
    color: 'green',
    features: [
      { title: 'Cash Flow Forecasting', description: 'Accurate 30/60/90 day projections based on historical patterns.' },
      { title: 'Invoice Chasing', description: 'Automated reminders that get you paid faster.' },
      { title: 'Payment Predictions', description: 'Know when customers will actually pay based on their history.' },
      { title: 'Collection Automation', description: 'Escalating reminder sequences that maintain relationships.' },
      { title: 'Scenario Modeling', description: 'What-if analysis for major financial decisions.' },
      { title: 'Bank Integration', description: 'Real-time cash position across all accounts.' },
    ],
    integrations: ['QuickBooks', 'Xero', 'Stripe', 'Square', 'Plaid', 'Mercury'],
    metrics: { tasksPerMonth: '1,800+', timeSaved: '12 hrs/week', accuracy: '94.7%' },
    useCases: [
      'Predict cash shortfalls 60 days in advance',
      'Reduce average days sales outstanding (DSO)',
      'Automate invoice follow-up professionally',
      'Model the cash impact of major decisions',
    ],
    faqs: [
      { q: 'How accurate are the forecasts?', a: 'Our forecasts are typically within 5-8% of actual cash positions, improving as the system learns your business patterns.' },
      { q: 'Will it damage customer relationships?', a: 'No. Collection sequences are professional and customizable. Many customers actually appreciate the clear communication.' },
      { q: 'Can it connect to multiple bank accounts?', a: 'Yes. Get a unified view across all your bank accounts, credit cards, and payment processors.' },
      { q: 'Does it work with international currencies?', a: 'Yes. Handle multi-currency forecasting with automatic exchange rate updates.' },
    ],
    testimonial: {
      quote: "We avoided a cash crunch that would have cost us a major contract. CashFlowCommanderAI paid for 10 years of service in one month.",
      author: 'James Mitchell',
      role: 'CEO',
      company: 'BuildRight Construction',
      image: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=200&q=80'
    },
    relatedAgents: ['bookkeeper', 'vendor_negotiator', 'proposal_pro'],
  },

  vendor_negotiator: {
    title: 'VendorNegotiatorAI',
    tagline: 'Smart Procurement Automation',
    heroImage: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1600&q=80',
    description: 'Analyze contracts, benchmark prices, and optimize vendor costs automatically.',
    longDescription: 'VendorNegotiatorAI is your procurement secret weapon. It analyzes contracts for hidden costs, benchmarks prices against market rates, tracks renewals, and provides negotiation intelligence.',
    price: 299,
    category: 'Operations',
    color: 'orange',
    features: [
      { title: 'Contract Analysis', description: 'AI reads contracts to identify risks, obligations, and hidden costs.' },
      { title: 'Price Benchmarking', description: 'Compare what you pay vs. market rates for the same services.' },
      { title: 'Renewal Tracking', description: 'Never auto-renew at bad rates again with proactive alerts.' },
      { title: 'Negotiation Briefs', description: 'Get talking points and leverage data before vendor calls.' },
      { title: 'Spend Analytics', description: 'Visualize where your money goes across all vendors.' },
      { title: 'Vendor Scorecards', description: 'Track performance, reliability, and value across suppliers.' },
    ],
    integrations: ['QuickBooks', 'NetSuite', 'SAP', 'Coupa', 'Dropbox', 'Google Drive'],
    metrics: { tasksPerMonth: '600+', timeSaved: '8 hrs/week', accuracy: '91.2%' },
    useCases: [
      'Identify contracts ripe for renegotiation',
      'Benchmark SaaS spend against market rates',
      'Never miss a renewal deadline again',
      'Consolidate vendors and reduce complexity',
    ],
    faqs: [
      { q: 'How much can I actually save?', a: 'Customers typically identify 15-30% savings opportunities in their first month, especially on auto-renewed contracts.' },
      { q: 'Does it do the negotiating for me?', a: 'It provides intelligence and talking points. You (or your team) handle the actual negotiations with confidence.' },
      { q: 'Can it read any contract format?', a: 'Yes. PDF, Word, scanned documents—our OCR and NLP handle them all.' },
      { q: 'How does benchmarking work?', a: 'We aggregate anonymized pricing data across thousands of businesses to show fair market rates.' },
    ],
    testimonial: {
      quote: "VendorNegotiatorAI found $47K in annual savings in contracts we thought were competitive. ROI in the first week.",
      author: 'Lisa Park',
      role: 'Operations Director',
      company: 'ScaleUp Ventures',
      image: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=200&q=80'
    },
    relatedAgents: ['bookkeeper', 'cashflow_commander', 'compliance_guard'],
  },

  reputation_guardian: {
    title: 'ReputationGuardianAI',
    tagline: 'Online Reputation Management',
    heroImage: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1600&q=80',
    description: 'Monitor, respond, and grow your brand reputation across all review platforms.',
    longDescription: 'ReputationGuardianAI protects and enhances your online presence. It monitors reviews across all platforms, generates appropriate responses, tracks sentiment trends, and helps you build a stellar reputation.',
    price: 159,
    category: 'Marketing',
    color: 'yellow',
    features: [
      { title: 'Review Monitoring', description: 'Track reviews across Google, Yelp, Facebook, and 50+ platforms.' },
      { title: 'Response Generation', description: 'AI-drafted responses that address concerns professionally.' },
      { title: 'Sentiment Tracking', description: 'Understand how customers feel about your brand over time.' },
      { title: 'Competitor Analysis', description: 'See how your reputation compares to competitors.' },
      { title: 'Alert Notifications', description: 'Instant alerts for negative reviews requiring attention.' },
      { title: 'Reporting Dashboard', description: 'Track review volume, ratings, and trends visually.' },
    ],
    integrations: ['Google Business', 'Yelp', 'Facebook', 'TripAdvisor', 'Trustpilot', 'G2'],
    metrics: { tasksPerMonth: '2,100+', timeSaved: '12 hrs/week', accuracy: '95.3%' },
    useCases: [
      'Respond to every review within hours, not days',
      'Turn negative experiences into recovery opportunities',
      'Monitor competitor reputation for advantages',
      'Track reputation improvement over time',
    ],
    faqs: [
      { q: 'Which platforms do you monitor?', a: 'Google, Yelp, Facebook, TripAdvisor, Trustpilot, G2, Capterra, BBB, and 40+ industry-specific platforms.' },
      { q: 'Can it remove negative reviews?', a: 'No one can guarantee review removal. We focus on professional responses that show future customers you care.' },
      { q: 'Does responding to reviews help?', a: 'Absolutely. Businesses that respond to reviews see 35% higher ratings on average and build customer trust.' },
      { q: 'How fast are review alerts?', a: 'Most reviews are detected and alerted within 15-30 minutes of posting.' },
    ],
    testimonial: {
      quote: "Our Google rating went from 3.8 to 4.6 stars in four months. ReputationGuardianAI helped us respond to every review thoughtfully.",
      author: 'Marcus Johnson',
      role: 'Owner',
      company: 'Riverdale Auto Service',
      image: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&q=80'
    },
    relatedAgents: ['customer_care', 'social_pilot', 'inbox_commander'],
  },

  inventory_intel: {
    title: 'InventoryIntelAI',
    tagline: 'Demand Forecasting & Optimization',
    heroImage: 'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1600&q=80',
    description: 'Ensure the right stock at the right time with AI-powered demand forecasting.',
    longDescription: 'InventoryIntelAI eliminates stockouts and overstock situations. It predicts demand using machine learning, automates reorder points, tracks waste, and optimizes your inventory investment.',
    price: 229,
    category: 'Operations',
    color: 'indigo',
    features: [
      { title: 'Demand Forecasting', description: 'ML-powered predictions accounting for seasonality and trends.' },
      { title: 'Reorder Automation', description: 'Automatic PO generation when stock hits optimal reorder points.' },
      { title: 'Waste Tracking', description: 'Identify slow-moving and expiring inventory before it\'s too late.' },
      { title: 'Supplier Management', description: 'Track lead times and reliability across all suppliers.' },
      { title: 'Stock Optimization', description: 'Right-size inventory to free up working capital.' },
      { title: 'Multi-Location Support', description: 'Manage inventory across warehouses and retail locations.' },
    ],
    integrations: ['Shopify', 'QuickBooks', 'NetSuite', 'TradeGecko', 'ShipStation', 'Amazon'],
    metrics: { tasksPerMonth: '1,500+', timeSaved: '15 hrs/week', accuracy: '93.8%' },
    useCases: [
      'Predict holiday demand months in advance',
      'Reduce carrying costs by 20-30%',
      'Eliminate stockouts on best-sellers',
      'Identify and liquidate slow-moving inventory',
    ],
    faqs: [
      { q: 'How accurate is demand forecasting?', a: 'Typically within 8-12% for established products, improving as the system learns your specific patterns and market.' },
      { q: 'Can it handle seasonal businesses?', a: 'Yes. It learns your seasonal patterns and adjusts forecasts accordingly, including for unusual events.' },
      { q: 'Does it integrate with my POS?', a: 'We integrate with major POS and e-commerce systems including Shopify, Square, WooCommerce, and more.' },
      { q: 'What about perishable goods?', a: 'Yes. It tracks expiration dates and optimizes ordering to minimize waste while maintaining availability.' },
    ],
    testimonial: {
      quote: "We reduced inventory carrying costs by 28% while improving fill rates. InventoryIntelAI is a game-changer.",
      author: 'Kevin O\'Brien',
      role: 'Supply Chain Manager',
      company: 'Coastal Distributors',
      image: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&q=80'
    },
    relatedAgents: ['vendor_negotiator', 'cashflow_commander', 'bookkeeper'],
  },

  proposal_pro: {
    title: 'ProposalProAI',
    tagline: 'Win More Deals',
    heroImage: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80',
    description: 'Automated proposal generation, pricing optimization, and intelligent RFP responses.',
    longDescription: 'ProposalProAI turns your sales team into proposal powerhouses. It generates customized proposals in minutes, optimizes pricing based on win probability, and helps you respond to RFPs at scale.',
    price: 199,
    category: 'Sales',
    color: 'rose',
    features: [
      { title: 'Proposal Generation', description: 'Create professional, customized proposals from templates in minutes.' },
      { title: 'Pricing Analysis', description: 'AI-optimized pricing based on deal characteristics and win history.' },
      { title: 'Win Rate Tracking', description: 'Understand what proposal elements correlate with wins.' },
      { title: 'Follow-Up Automation', description: 'Smart sequences that keep deals moving forward.' },
      { title: 'Template Library', description: 'Build a library of winning proposal components.' },
      { title: 'Version Control', description: 'Track changes and maintain proposal history.' },
    ],
    integrations: ['Salesforce', 'HubSpot', 'PandaDoc', 'DocuSign', 'Pipedrive', 'Slack'],
    metrics: { tasksPerMonth: '900+', timeSaved: '18 hrs/week', accuracy: '89.4%' },
    useCases: [
      'Generate proposals 10x faster than manual creation',
      'Respond to RFPs that you\'d otherwise skip',
      'Optimize pricing to maximize win rate and revenue',
      'Keep deals moving with automated follow-up',
    ],
    faqs: [
      { q: 'How customized are the proposals?', a: 'Highly. The AI pulls from your template library and customizes based on prospect industry, size, needs, and conversation history.' },
      { q: 'Does it integrate with my CRM?', a: 'Yes. We integrate with Salesforce, HubSpot, Pipedrive, and others to pull deal context automatically.' },
      { q: 'Can it handle complex enterprise proposals?', a: 'Yes. It excels at assembling multi-section proposals with appropriate case studies, technical specs, and pricing.' },
      { q: 'How does pricing optimization work?', a: 'It analyzes your win/loss history to identify optimal price points based on deal characteristics.' },
    ],
    testimonial: {
      quote: "Our proposal turnaround went from 3 days to 3 hours. Win rate is up 23% because we can pursue more opportunities.",
      author: 'Rachel Torres',
      role: 'VP of Sales',
      company: 'Nexus Cloud',
      image: 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=200&q=80'
    },
    relatedAgents: ['inbox_commander', 'customer_care', 'cashflow_commander'],
  },
}

// ============================================================================
// DEMO SCENARIOS - Agent-specific realistic demonstrations
// ============================================================================
const DEMO_SCENARIOS: Record<string, any> = {
  bookkeeper: {
    title: 'Monthly Reconciliation',
    phases: [
      { name: 'Connecting to bank feeds...', duration: 1500 },
      { name: 'Importing 847 transactions...', duration: 2000 },
      { name: 'Categorizing expenses...', duration: 2500 },
      { name: 'Matching invoices to payments...', duration: 2000 },
      { name: 'Detecting anomalies...', duration: 1500 },
      { name: 'Generating financial reports...', duration: 1500 },
    ],
    activities: [
      { type: 'success', text: 'Categorized: Office Depot purchase → Office Supplies ($127.43)', time: '2s ago' },
      { type: 'success', text: 'Categorized: AWS monthly charge → Cloud Infrastructure ($2,847.00)', time: '3s ago' },
      { type: 'success', text: 'Matched: Invoice #1847 to Stripe payment ($4,500.00)', time: '5s ago' },
      { type: 'warning', text: 'Flagged: Duplicate charge detected - Adobe Creative Cloud', time: '7s ago' },
      { type: 'success', text: 'Categorized: Delta Airlines → Travel Expenses ($847.20)', time: '8s ago' },
      { type: 'success', text: 'Reconciled: Chase Business checking - 234 transactions', time: '10s ago' },
      { type: 'info', text: 'Generated: February P&L Statement', time: '12s ago' },
      { type: 'success', text: 'Categorized: Gusto Payroll → Salary Expenses ($45,230.00)', time: '14s ago' },
    ],
    results: {
      transactionsProcessed: 847,
      categorized: 831,
      anomaliesFound: 3,
      invoicesMatched: 47,
      reportsGenerated: 4,
      timeSaved: '4.2 hours',
      accuracy: '99.2%',
    },
  },
  inbox_commander: {
    title: 'Morning Inbox Triage',
    phases: [
      { name: 'Connecting to email server...', duration: 1000 },
      { name: 'Scanning 156 unread emails...', duration: 2000 },
      { name: 'Analyzing priority and sentiment...', duration: 2500 },
      { name: 'Extracting action items...', duration: 2000 },
      { name: 'Drafting responses...', duration: 2500 },
      { name: 'Scheduling follow-ups...', duration: 1500 },
    ],
    activities: [
      { type: 'urgent', text: 'URGENT: CEO requesting Q4 numbers - drafted response', time: '1s ago' },
      { type: 'success', text: 'Sorted: Newsletter from TechCrunch → Read Later', time: '2s ago' },
      { type: 'success', text: 'Extracted: Meeting request from Sarah → Added to calendar', time: '4s ago' },
      { type: 'success', text: 'Drafted: Response to vendor inquiry (awaiting review)', time: '5s ago' },
      { type: 'warning', text: 'Flagged: Negative sentiment from client - Michael Torres', time: '7s ago' },
      { type: 'success', text: 'Scheduled: Follow-up reminder for proposal sent 3 days ago', time: '9s ago' },
      { type: 'info', text: 'Archived: 23 promotional emails', time: '11s ago' },
      { type: 'success', text: 'Extracted: 7 action items added to task list', time: '13s ago' },
    ],
    results: {
      emailsProcessed: 156,
      prioritySorted: 156,
      responsesDrafted: 12,
      actionItemsExtracted: 7,
      followupsScheduled: 5,
      timeSaved: '2.1 hours',
      accuracy: '97.8%',
    },
  },
  hiring_hero: {
    title: 'Engineering Role Pipeline',
    phases: [
      { name: 'Loading applicant pool...', duration: 1500 },
      { name: 'Parsing 234 resumes...', duration: 2500 },
      { name: 'Scoring against job requirements...', duration: 3000 },
      { name: 'Identifying top candidates...', duration: 2000 },
      { name: 'Scheduling interviews...', duration: 2000 },
      { name: 'Sending personalized outreach...', duration: 1500 },
    ],
    activities: [
      { type: 'success', text: 'Top Match (94%): Sarah Chen - 8 yrs experience, React/Node', time: '2s ago' },
      { type: 'success', text: 'Strong Match (89%): Marcus Johnson - Ex-Google, Python expert', time: '3s ago' },
      { type: 'success', text: 'Scheduled: Interview with Sarah Chen - Tuesday 2pm', time: '5s ago' },
      { type: 'info', text: 'Sent: Personalized outreach to 15 qualified candidates', time: '7s ago' },
      { type: 'success', text: 'Good Match (82%): Emily Rodriguez - Startup experience', time: '9s ago' },
      { type: 'warning', text: 'Flagged: 3 candidates with incomplete applications', time: '11s ago' },
      { type: 'success', text: 'Updated: Candidate pipeline in Greenhouse', time: '13s ago' },
      { type: 'success', text: 'Generated: Weekly hiring report for stakeholders', time: '15s ago' },
    ],
    results: {
      resumesScanned: 234,
      qualifiedCandidates: 47,
      interviewsScheduled: 8,
      outreachSent: 15,
      topMatches: 12,
      timeSaved: '6.5 hours',
      accuracy: '94.5%',
    },
  },
  customer_care: {
    title: 'Support Queue Processing',
    phases: [
      { name: 'Loading support tickets...', duration: 1000 },
      { name: 'Analyzing 89 open tickets...', duration: 2000 },
      { name: 'Categorizing by issue type...', duration: 2000 },
      { name: 'Generating response suggestions...', duration: 2500 },
      { name: 'Identifying escalation needs...', duration: 1500 },
      { name: 'Updating knowledge base...', duration: 1500 },
    ],
    activities: [
      { type: 'success', text: 'Resolved: Password reset request - auto-sent instructions', time: '1s ago' },
      { type: 'success', text: 'Resolved: Billing inquiry - provided invoice link', time: '3s ago' },
      { type: 'warning', text: 'Escalated: Enterprise client reporting critical bug', time: '4s ago' },
      { type: 'success', text: 'Drafted: Response to feature request (awaiting review)', time: '6s ago' },
      { type: 'urgent', text: 'URGENT: VIP customer frustrated - routed to senior agent', time: '8s ago' },
      { type: 'success', text: 'Resolved: How-to question - linked to help article', time: '10s ago' },
      { type: 'info', text: 'Updated: FAQ with 3 new common questions', time: '12s ago' },
      { type: 'success', text: 'Closed: 34 tickets with automated responses', time: '14s ago' },
    ],
    results: {
      ticketsProcessed: 89,
      autoResolved: 34,
      draftedResponses: 28,
      escalated: 5,
      avgResponseTime: '47 seconds',
      timeSaved: '3.8 hours',
      accuracy: '96.1%',
    },
  },
  social_pilot: {
    title: 'Weekly Content Schedule',
    phases: [
      { name: 'Analyzing trending topics...', duration: 2000 },
      { name: 'Generating content ideas...', duration: 2500 },
      { name: 'Creating platform-specific posts...', duration: 3000 },
      { name: 'Optimizing hashtags...', duration: 1500 },
      { name: 'Scheduling for optimal times...', duration: 2000 },
      { name: 'Setting up engagement monitoring...', duration: 1500 },
    ],
    activities: [
      { type: 'success', text: 'Created: LinkedIn thought leadership post (scheduled Tue 9am)', time: '2s ago' },
      { type: 'success', text: 'Created: Instagram carousel - 5 slides on industry tips', time: '4s ago' },
      { type: 'info', text: 'Trending: #AIAutomation up 340% - incorporated into content', time: '6s ago' },
      { type: 'success', text: 'Created: Twitter thread - 8 tweets on customer success story', time: '8s ago' },
      { type: 'success', text: 'Optimized: Added 12 high-performing hashtags', time: '10s ago' },
      { type: 'success', text: 'Scheduled: 21 posts across 4 platforms for next 7 days', time: '12s ago' },
      { type: 'warning', text: 'Alert: Competitor launched campaign - analysis ready', time: '14s ago' },
      { type: 'success', text: 'Generated: Weekly content calendar exported to Notion', time: '16s ago' },
    ],
    results: {
      postsCreated: 21,
      platformsCovered: 4,
      hashtagsOptimized: 48,
      trendsIdentified: 7,
      scheduledDays: 7,
      timeSaved: '5.2 hours',
      accuracy: '92.3%',
    },
  },
  appointment_setter: {
    title: 'Calendar Optimization',
    phases: [
      { name: 'Syncing calendar data...', duration: 1000 },
      { name: 'Analyzing scheduling requests...', duration: 2000 },
      { name: 'Finding optimal time slots...', duration: 2500 },
      { name: 'Resolving conflicts...', duration: 2000 },
      { name: 'Sending confirmations...', duration: 1500 },
      { name: 'Setting up reminders...', duration: 1500 },
    ],
    activities: [
      { type: 'success', text: 'Scheduled: Sales call with Acme Corp - Wed 2:30pm', time: '1s ago' },
      { type: 'success', text: 'Resolved: Moved team standup to avoid client conflict', time: '3s ago' },
      { type: 'success', text: 'Scheduled: Product demo for 3 stakeholders - Thu 10am', time: '5s ago' },
      { type: 'info', text: 'Added: 30min buffer before investor meeting', time: '7s ago' },
      { type: 'success', text: 'Sent: Confirmation to 12 meeting participants', time: '9s ago' },
      { type: 'warning', text: 'Rescheduled: Client requested new time - found slot Fri 3pm', time: '11s ago' },
      { type: 'success', text: 'Created: Reminder sequence for tomorrow\'s board meeting', time: '13s ago' },
      { type: 'success', text: 'Optimized: Grouped 4 short meetings into focused block', time: '15s ago' },
    ],
    results: {
      meetingsScheduled: 18,
      conflictsResolved: 4,
      remindersSent: 23,
      noShowsReduced: '80%',
      bufferTimeAdded: '4.5 hours',
      timeSaved: '2.8 hours',
      accuracy: '99.5%',
    },
  },
  compliance_guard: {
    title: 'Quarterly Compliance Audit',
    phases: [
      { name: 'Scanning regulatory databases...', duration: 2000 },
      { name: 'Checking policy documents...', duration: 2500 },
      { name: 'Auditing data handling practices...', duration: 3000 },
      { name: 'Identifying compliance gaps...', duration: 2500 },
      { name: 'Generating remediation tasks...', duration: 2000 },
      { name: 'Preparing audit report...', duration: 2000 },
    ],
    activities: [
      { type: 'success', text: 'Verified: GDPR data processing agreements up to date', time: '2s ago' },
      { type: 'warning', text: 'Gap Found: Privacy policy missing new cookie requirements', time: '4s ago' },
      { type: 'success', text: 'Verified: SOC 2 controls properly documented', time: '6s ago' },
      { type: 'info', text: 'Update: CCPA amendment effective next month - action needed', time: '8s ago' },
      { type: 'success', text: 'Verified: Employee security training 98% complete', time: '10s ago' },
      { type: 'warning', text: 'Deadline: Business license renewal due in 45 days', time: '12s ago' },
      { type: 'success', text: 'Generated: Compliance checklist with 47 items', time: '14s ago' },
      { type: 'success', text: 'Created: Board-ready compliance summary report', time: '16s ago' },
    ],
    results: {
      regulationsChecked: 24,
      policiesAudited: 18,
      gapsIdentified: 3,
      deadlinesTracked: 12,
      documentsGenerated: 5,
      timeSaved: '8.5 hours',
      accuracy: '99.8%',
    },
  },
  cashflow_commander: {
    title: '90-Day Cash Forecast',
    phases: [
      { name: 'Connecting to bank accounts...', duration: 1500 },
      { name: 'Analyzing historical patterns...', duration: 2500 },
      { name: 'Processing outstanding invoices...', duration: 2500 },
      { name: 'Predicting payment dates...', duration: 2000 },
      { name: 'Running scenario models...', duration: 2500 },
      { name: 'Generating forecast report...', duration: 2000 },
    ],
    activities: [
      { type: 'success', text: 'Forecast: Positive cash position through Q2', time: '2s ago' },
      { type: 'warning', text: 'Alert: Potential shortfall in Week 8 - $24K gap', time: '4s ago' },
      { type: 'success', text: 'Sent: Payment reminder to Acme Corp ($12,500 overdue)', time: '6s ago' },
      { type: 'info', text: 'Prediction: Invoice #2847 likely to pay in 12 days (85% confidence)', time: '8s ago' },
      { type: 'success', text: 'Identified: 3 invoices eligible for early payment discount', time: '10s ago' },
      { type: 'success', text: 'Modeled: Impact of new hire on runway (-2.3 months)', time: '12s ago' },
      { type: 'success', text: 'Collected: $8,400 from automated reminder sequence', time: '14s ago' },
      { type: 'success', text: 'Generated: Cash flow report for investor update', time: '16s ago' },
    ],
    results: {
      forecastDays: 90,
      invoicesTracked: 47,
      remindersSent: 12,
      collected: '$34,200',
      shortfallsIdentified: 1,
      timeSaved: '4.2 hours',
      accuracy: '94.7%',
    },
  },
  vendor_negotiator: {
    title: 'Contract Renewal Analysis',
    phases: [
      { name: 'Loading active contracts...', duration: 1500 },
      { name: 'Analyzing pricing vs market rates...', duration: 3000 },
      { name: 'Identifying negotiation opportunities...', duration: 2500 },
      { name: 'Calculating potential savings...', duration: 2000 },
      { name: 'Generating negotiation briefs...', duration: 2500 },
      { name: 'Preparing vendor scorecards...', duration: 2000 },
    ],
    activities: [
      { type: 'success', text: 'Analyzed: AWS contract - 18% above market rate', time: '2s ago' },
      { type: 'warning', text: 'Alert: Salesforce auto-renewal in 30 days - action needed', time: '4s ago' },
      { type: 'success', text: 'Savings Found: Switch to annual billing saves $4,200/yr', time: '6s ago' },
      { type: 'info', text: 'Benchmark: Your SaaS spend is 12% above industry average', time: '8s ago' },
      { type: 'success', text: 'Generated: Negotiation brief for HubSpot renewal', time: '10s ago' },
      { type: 'success', text: 'Identified: Unused licenses worth $8,400/year', time: '12s ago' },
      { type: 'success', text: 'Created: Vendor scorecard for top 10 suppliers', time: '14s ago' },
      { type: 'warning', text: 'Risk: Single-source dependency on 2 critical vendors', time: '16s ago' },
    ],
    results: {
      contractsAnalyzed: 34,
      savingsIdentified: '$47,200',
      renewalsTracked: 8,
      negotiationBriefs: 5,
      unusedLicenses: 12,
      timeSaved: '6.2 hours',
      accuracy: '91.2%',
    },
  },
  reputation_guardian: {
    title: 'Review Monitoring & Response',
    phases: [
      { name: 'Scanning review platforms...', duration: 1500 },
      { name: 'Analyzing sentiment trends...', duration: 2500 },
      { name: 'Identifying response priorities...', duration: 2000 },
      { name: 'Generating personalized responses...', duration: 3000 },
      { name: 'Tracking competitor reviews...', duration: 2000 },
      { name: 'Updating reputation dashboard...', duration: 1500 },
    ],
    activities: [
      { type: 'urgent', text: 'NEW: 1-star review on Google - response drafted', time: '1s ago' },
      { type: 'success', text: 'Responded: 5-star review thanked on Yelp', time: '3s ago' },
      { type: 'success', text: 'Trend: Positive sentiment up 12% this month', time: '5s ago' },
      { type: 'info', text: 'Competitor Alert: Main rival dropped to 3.8 stars', time: '7s ago' },
      { type: 'success', text: 'Responded: Addressed shipping concern on Facebook', time: '9s ago' },
      { type: 'warning', text: 'Pattern: 3 reviews mention slow customer service', time: '11s ago' },
      { type: 'success', text: 'Generated: Weekly reputation report', time: '13s ago' },
      { type: 'success', text: 'Updated: Response templates based on recent feedback', time: '15s ago' },
    ],
    results: {
      reviewsMonitored: 127,
      responsesGenerated: 18,
      avgRating: '4.6 stars',
      sentimentScore: '+82%',
      competitorsTracked: 5,
      timeSaved: '3.5 hours',
      accuracy: '95.3%',
    },
  },
  inventory_intel: {
    title: 'Demand Forecast & Reorder',
    phases: [
      { name: 'Analyzing sales velocity...', duration: 2000 },
      { name: 'Processing seasonal patterns...', duration: 2500 },
      { name: 'Calculating optimal stock levels...', duration: 2500 },
      { name: 'Generating purchase orders...', duration: 2000 },
      { name: 'Identifying slow movers...', duration: 2000 },
      { name: 'Updating inventory dashboard...', duration: 1500 },
    ],
    activities: [
      { type: 'warning', text: 'Low Stock: SKU-4521 will stockout in 5 days - PO created', time: '2s ago' },
      { type: 'success', text: 'Forecast: Holiday demand +40% - inventory adjusted', time: '4s ago' },
      { type: 'success', text: 'Optimized: Reduced safety stock on 23 slow movers', time: '6s ago' },
      { type: 'info', text: 'Trend: Blue variant outselling red 3:1 - rebalancing', time: '8s ago' },
      { type: 'success', text: 'Created: Purchase order for top supplier ($12,400)', time: '10s ago' },
      { type: 'warning', text: 'Alert: 8 SKUs approaching expiration - markdown suggested', time: '12s ago' },
      { type: 'success', text: 'Saved: $8,200 by consolidating shipments', time: '14s ago' },
      { type: 'success', text: 'Generated: Inventory health report for ops team', time: '16s ago' },
    ],
    results: {
      skusAnalyzed: 847,
      reordersCreated: 12,
      stockoutsAvoided: 8,
      excessReduced: '$24,500',
      forecastAccuracy: '93.8%',
      timeSaved: '5.8 hours',
      accuracy: '93.8%',
    },
  },
  proposal_pro: {
    title: 'Enterprise RFP Response',
    phases: [
      { name: 'Analyzing RFP requirements...', duration: 2000 },
      { name: 'Matching to solution capabilities...', duration: 2500 },
      { name: 'Pulling relevant case studies...', duration: 2000 },
      { name: 'Generating pricing options...', duration: 2500 },
      { name: 'Assembling proposal document...', duration: 3000 },
      { name: 'Running win probability analysis...', duration: 2000 },
    ],
    activities: [
      { type: 'success', text: 'Matched: 47/52 RFP requirements to our capabilities', time: '2s ago' },
      { type: 'success', text: 'Selected: 3 relevant case studies (SaaS, Enterprise, Healthcare)', time: '4s ago' },
      { type: 'info', text: 'Pricing: Recommending Tier 2 ($48K) - highest win probability', time: '6s ago' },
      { type: 'success', text: 'Generated: Executive summary tailored to prospect', time: '8s ago' },
      { type: 'success', text: 'Added: Technical specifications section (12 pages)', time: '10s ago' },
      { type: 'success', text: 'Created: Custom ROI calculator for prospect', time: '12s ago' },
      { type: 'warning', text: 'Gap: Missing certification they require - flagged for review', time: '14s ago' },
      { type: 'success', text: 'Assembled: 34-page proposal ready for review', time: '16s ago' },
    ],
    results: {
      requirementsMatched: '90%',
      proposalPages: 34,
      caseStudiesIncluded: 3,
      pricingOptions: 3,
      winProbability: '72%',
      timeSaved: '8.5 hours',
      accuracy: '89.4%',
    },
  },
}

// ============================================================================
// COLOR UTILITIES
// ============================================================================
const getColorClasses = (color: string) => {
  const colors: Record<string, { bg: string, bgLight: string, text: string, border: string, gradient: string }> = {
    emerald: { bg: 'bg-emerald-500', bgLight: 'bg-emerald-100', text: 'text-emerald-600', border: 'border-emerald-200', gradient: 'from-emerald-500 to-teal-600' },
    blue: { bg: 'bg-blue-500', bgLight: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200', gradient: 'from-blue-500 to-indigo-600' },
    violet: { bg: 'bg-violet-500', bgLight: 'bg-violet-100', text: 'text-violet-600', border: 'border-violet-200', gradient: 'from-violet-500 to-purple-600' },
    amber: { bg: 'bg-amber-500', bgLight: 'bg-amber-100', text: 'text-amber-600', border: 'border-amber-200', gradient: 'from-amber-500 to-orange-600' },
    pink: { bg: 'bg-pink-500', bgLight: 'bg-pink-100', text: 'text-pink-600', border: 'border-pink-200', gradient: 'from-pink-500 to-rose-600' },
    cyan: { bg: 'bg-cyan-500', bgLight: 'bg-cyan-100', text: 'text-cyan-600', border: 'border-cyan-200', gradient: 'from-cyan-500 to-blue-600' },
    slate: { bg: 'bg-slate-500', bgLight: 'bg-slate-100', text: 'text-slate-600', border: 'border-slate-200', gradient: 'from-slate-500 to-gray-600' },
    green: { bg: 'bg-green-500', bgLight: 'bg-green-100', text: 'text-green-600', border: 'border-green-200', gradient: 'from-green-500 to-emerald-600' },
    orange: { bg: 'bg-orange-500', bgLight: 'bg-orange-100', text: 'text-orange-600', border: 'border-orange-200', gradient: 'from-orange-500 to-red-600' },
    yellow: { bg: 'bg-yellow-500', bgLight: 'bg-yellow-100', text: 'text-yellow-600', border: 'border-yellow-200', gradient: 'from-yellow-500 to-amber-600' },
    indigo: { bg: 'bg-indigo-500', bgLight: 'bg-indigo-100', text: 'text-indigo-600', border: 'border-indigo-200', gradient: 'from-indigo-500 to-violet-600' },
    rose: { bg: 'bg-rose-500', bgLight: 'bg-rose-100', text: 'text-rose-600', border: 'border-rose-200', gradient: 'from-rose-500 to-pink-600' },
  }
  return colors[color] || colors.blue
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================
export default function AgentPage() {
  const params = useParams()
  const agentName = params.agentName as string
  const agent = AGENT_CONFIG[agentName]

  const [activeTab, setActiveTab] = useState('features')
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [showDemo, setShowDemo] = useState(false)
  const [demoPhase, setDemoPhase] = useState(0)
  const [demoActivities, setDemoActivities] = useState<any[]>([])
  const [demoProgress, setDemoProgress] = useState(0)
  const [demoComplete, setDemoComplete] = useState(false)

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [agentName])

  // Get demo scenario for this agent
  const demoScenario = DEMO_SCENARIOS[agentName] || DEMO_SCENARIOS.bookkeeper

  if (!agent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Agent not found</h1>
          <p className="text-slate-600 mb-6">The agent you're looking for doesn't exist.</p>
          <Link href="/" className="btn-primary inline-flex items-center gap-2">
            Back to Home
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
        </div>
      </div>
    )
  }

  const colors = getColorClasses(agent.color)

  const runDemo = () => {
    setIsProcessing(true)
    setShowDemo(false)
    setDemoPhase(0)
    setDemoActivities([])
    setDemoProgress(0)
    setDemoComplete(false)

    // Scroll to demo section
    setTimeout(() => {
      const demoSection = document.getElementById('demo-section')
      if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }, 100)

    // Run through phases
    let totalDuration = 0
    const phases = demoScenario.phases

    phases.forEach((phase: any, index: number) => {
      setTimeout(() => {
        setDemoPhase(index + 1)
        setDemoProgress(Math.round(((index + 1) / phases.length) * 100))
      }, totalDuration)
      totalDuration += phase.duration
    })

    // After all phases, show results
    setTimeout(() => {
      setIsProcessing(false)
      setShowDemo(true)
      
      // Animate activities appearing one by one
      demoScenario.activities.forEach((activity: any, index: number) => {
        setTimeout(() => {
          setDemoActivities(prev => [...prev, activity])
        }, index * 400)
      })

      // Mark demo complete after all activities
      setTimeout(() => {
        setDemoComplete(true)
      }, demoScenario.activities.length * 400 + 500)
    }, totalDuration)
  }

  const closeDemo = () => {
    setShowDemo(false)
    setIsProcessing(false)
    setDemoActivities([])
    setDemoComplete(false)
  }

  const relatedAgentsList = agent.relatedAgents?.map((id: string) => AGENT_CONFIG[id]).filter(Boolean) || []

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16 lg:h-20">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-slate-900 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-semibold tracking-tight">AgentHub</span>
            </Link>
            
            <div className="hidden md:flex items-center gap-8">
              <Link href="/#solutions" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Solutions</Link>
              <Link href="/#how-it-works" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">How It Works</Link>
              <Link href="/#testimonials" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Testimonials</Link>
            </div>
            
            <div className="flex items-center gap-4">
              <Link href="/login" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition">Sign In</Link>
              <Link href="/signup" className="btn-primary text-sm">Get Started</Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Breadcrumb */}
      <div className="bg-slate-50 border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 py-4">
          <div className="flex items-center gap-2 text-sm">
            <Link href="/" className="text-slate-500 hover:text-slate-900 transition">Home</Link>
            <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <Link href="/#solutions" className="text-slate-500 hover:text-slate-900 transition">Agents</Link>
            <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-slate-900 font-medium">{agent.title}</span>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative py-16 lg:py-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-slate-50" />
        <div className={`absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l ${colors.bgLight} opacity-30`} />
        
        <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            {/* Left: Content */}
            <div>
              <div className={`inline-flex items-center gap-2 px-4 py-2 ${colors.bgLight} rounded-full mb-6`}>
                <span className={`w-2 h-2 ${colors.bg} rounded-full`} />
                <span className={`text-sm font-medium ${colors.text}`}>{agent.category}</span>
              </div>
              
              <h1 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-slate-900 mb-4 tracking-tight">
                {agent.title}
              </h1>
              
              <p className="text-xl lg:text-2xl text-slate-600 font-medium mb-6">
                {agent.tagline}
              </p>
              
              <p className="text-lg text-slate-600 mb-8 leading-relaxed">
                {agent.longDescription}
              </p>

              {/* Pricing */}
              <div className="flex items-baseline gap-3 mb-8">
                <span className="text-5xl font-bold text-slate-900">${agent.price}</span>
                <span className="text-slate-500 text-lg">/month</span>
                <span className={`ml-4 px-3 py-1 ${colors.bgLight} ${colors.text} rounded-full text-sm font-medium`}>
                  14-day free trial
                </span>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 mb-10">
                <Link
                  href={`/signup?agent=${agentName}`}
                  className={`btn-primary inline-flex items-center justify-center gap-2 bg-gradient-to-r ${colors.gradient} border-0`}
                >
                  Start Free Trial
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
                <button
                  onClick={runDemo}
                  className="btn-secondary inline-flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Watch Demo
                </button>
              </div>

              {/* Trust Badges */}
              <div className="flex items-center gap-6 text-sm text-slate-500">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <span>SOC 2 Compliant</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <span>256-bit Encryption</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>99.9% Uptime</span>
                </div>
              </div>
            </div>

            {/* Right: Hero Image + Stats */}
            <div className="relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <Image
                  src={agent.heroImage}
                  alt={agent.title}
                  width={800}
                  height={600}
                  className="w-full h-[400px] lg:h-[500px] object-cover"
                  priority
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/60 via-transparent to-transparent" />
                
                {/* Floating Stats */}
                <div className="absolute bottom-6 left-6 right-6">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/95 backdrop-blur-sm rounded-xl p-4 text-center">
                      <p className={`text-2xl font-bold ${colors.text}`}>{agent.metrics.tasksPerMonth}</p>
                      <p className="text-xs text-slate-600">Tasks/Month</p>
                    </div>
                    <div className="bg-white/95 backdrop-blur-sm rounded-xl p-4 text-center">
                      <p className={`text-2xl font-bold ${colors.text}`}>{agent.metrics.timeSaved}</p>
                      <p className="text-xs text-slate-600">Time Saved</p>
                    </div>
                    <div className="bg-white/95 backdrop-blur-sm rounded-xl p-4 text-center">
                      <p className={`text-2xl font-bold ${colors.text}`}>{agent.metrics.accuracy}</p>
                      <p className="text-xs text-slate-600">Accuracy</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Decorative Elements */}
              <div className={`absolute -top-6 -right-6 w-32 h-32 ${colors.bgLight} rounded-full blur-3xl opacity-60`} />
              <div className={`absolute -bottom-6 -left-6 w-40 h-40 ${colors.bgLight} rounded-full blur-3xl opacity-40`} />
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section - Shows when triggered */}
      {(isProcessing || showDemo) && (
        <section id="demo-section" className="py-12 bg-slate-900">
          <div className="max-w-6xl mx-auto px-6 lg:px-8">
            {/* Close Button */}
            <div className="flex justify-end mb-4">
              <button
                onClick={closeDemo}
                className="text-slate-400 hover:text-white transition p-2"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {isProcessing ? (
              /* Processing Phase UI */
              <div className="bg-slate-800 rounded-2xl p-8 border border-slate-700">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 ${colors.bg} rounded-xl flex items-center justify-center`}>
                      <svg className="w-6 h-6 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{demoScenario.title}</h3>
                      <p className="text-slate-400 text-sm">{agent.title} is working...</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-white">{demoProgress}%</span>
                    <p className="text-slate-400 text-sm">Complete</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-8">
                  <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${colors.gradient} transition-all duration-500 ease-out`}
                      style={{ width: `${demoProgress}%` }}
                    />
                  </div>
                </div>

                {/* Phase Steps */}
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {demoScenario.phases.map((phase: any, index: number) => (
                    <div
                      key={index}
                      className={`flex items-center gap-3 p-4 rounded-xl transition-all duration-300 ${
                        demoPhase > index
                          ? 'bg-emerald-500/20 border border-emerald-500/30'
                          : demoPhase === index
                          ? 'bg-slate-700 border border-slate-600 animate-pulse'
                          : 'bg-slate-800/50 border border-slate-700/50 opacity-50'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                        demoPhase > index
                          ? 'bg-emerald-500'
                          : demoPhase === index
                          ? colors.bg
                          : 'bg-slate-600'
                      }`}>
                        {demoPhase > index ? (
                          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        ) : demoPhase === index ? (
                          <svg className="w-4 h-4 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                        ) : (
                          <span className="text-white text-xs font-bold">{index + 1}</span>
                        )}
                      </div>
                      <span className={`text-sm ${demoPhase >= index ? 'text-white' : 'text-slate-500'}`}>
                        {phase.name}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Processing Animation */}
                <div className="mt-8 flex justify-center">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 ${colors.bg} rounded-full animate-bounce`} style={{ animationDelay: '0ms' }} />
                    <div className={`w-3 h-3 ${colors.bg} rounded-full animate-bounce`} style={{ animationDelay: '150ms' }} />
                    <div className={`w-3 h-3 ${colors.bg} rounded-full animate-bounce`} style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            ) : (
              /* Results Phase UI */
              <div className="bg-slate-800 rounded-2xl border border-slate-700 overflow-hidden">
                {/* Header */}
                <div className="p-6 border-b border-slate-700">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 bg-emerald-500 rounded-xl flex items-center justify-center`}>
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-white">{demoScenario.title} Complete</h3>
                        <p className="text-slate-400 text-sm">Demo simulation finished successfully</p>
                      </div>
                    </div>
                    <span className="px-4 py-2 bg-emerald-500/20 text-emerald-400 rounded-full text-sm font-semibold">
                      ✓ Demo Complete
                    </span>
                  </div>
                </div>

                <div className="grid lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-slate-700">
                  {/* Activity Feed */}
                  <div className="p-6">
                    <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      Live Activity Feed
                    </h4>
                    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                      {demoActivities.map((activity: any, index: number) => (
                        <div
                          key={index}
                          className={`flex items-start gap-3 p-3 rounded-lg transition-all duration-300 ${
                            activity.type === 'success' ? 'bg-emerald-500/10 border border-emerald-500/20' :
                            activity.type === 'warning' ? 'bg-amber-500/10 border border-amber-500/20' :
                            activity.type === 'urgent' ? 'bg-red-500/10 border border-red-500/20' :
                            'bg-blue-500/10 border border-blue-500/20'
                          }`}
                          style={{ 
                            opacity: 1,
                            transform: 'translateX(0)',
                            animation: 'slideIn 0.3s ease-out'
                          }}
                        >
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
                            activity.type === 'success' ? 'bg-emerald-500' :
                            activity.type === 'warning' ? 'bg-amber-500' :
                            activity.type === 'urgent' ? 'bg-red-500' :
                            'bg-blue-500'
                          }`}>
                            {activity.type === 'success' && (
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                            {activity.type === 'warning' && (
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 9v2m0 4h.01" />
                              </svg>
                            )}
                            {activity.type === 'urgent' && (
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4m0 4h.01" />
                              </svg>
                            )}
                            {activity.type === 'info' && (
                              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 16h-1v-4h-1m1-4h.01" />
                              </svg>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-white text-sm">{activity.text}</p>
                            <p className="text-slate-500 text-xs mt-1">{activity.time}</p>
                          </div>
                        </div>
                      ))}
                      {demoActivities.length === 0 && (
                        <div className="text-center py-8 text-slate-500">
                          <svg className="w-8 h-8 mx-auto mb-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Loading activities...
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Results Summary */}
                  <div className="p-6">
                    <h4 className="text-white font-semibold mb-4 flex items-center gap-2">
                      <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      Session Results
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(demoScenario.results).map(([key, value]: [string, any], index: number) => (
                        <div
                          key={key}
                          className={`bg-slate-700/50 rounded-xl p-4 transition-all duration-500 ${
                            demoComplete ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
                          }`}
                          style={{ transitionDelay: `${index * 100}ms` }}
                        >
                          <p className="text-slate-400 text-xs uppercase tracking-wide mb-1">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </p>
                          <p className={`text-2xl font-bold ${
                            key.includes('time') || key.includes('saved') ? 'text-amber-400' :
                            key.includes('accuracy') || key.includes('rate') ? 'text-emerald-400' :
                            key.includes('alert') || key.includes('gap') || key.includes('shortfall') ? 'text-red-400' :
                            'text-white'
                          }`}>
                            {value}
                          </p>
                        </div>
                      ))}
                    </div>

                    {/* CTA */}
                    <div className={`mt-6 pt-6 border-t border-slate-700 transition-all duration-500 ${
                      demoComplete ? 'opacity-100' : 'opacity-0'
                    }`}>
                      <p className="text-slate-400 text-sm mb-4">
                        This is just a simulation. Deploy {agent.title} to see real results for your business.
                      </p>
                      <Link
                        href={`/signup?agent=${agentName}`}
                        className={`w-full inline-flex items-center justify-center gap-2 bg-gradient-to-r ${colors.gradient} text-white px-6 py-3 rounded-lg font-semibold hover:opacity-90 transition`}
                      >
                        Start Your Free Trial
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Tab Navigation */}
      <section className="border-b border-slate-200 sticky top-16 lg:top-20 bg-white z-40">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex gap-8 overflow-x-auto">
            {['features', 'use-cases', 'faq'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-2 text-sm font-medium border-b-2 transition whitespace-nowrap ${
                  activeTab === tab
                    ? `${colors.text} border-current`
                    : 'text-slate-500 border-transparent hover:text-slate-900'
                }`}
              >
                {tab === 'features' && 'Features'}
                {tab === 'use-cases' && 'Use Cases'}
                {tab === 'faq' && 'FAQ'}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Features Tab */}
      {activeTab === 'features' && (
        <section className="py-16 lg:py-24">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
                Everything You Need
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                {agent.title} comes packed with powerful features to automate your {agent.category.toLowerCase()} operations.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {agent.features.map((feature: any, i: number) => (
                <div
                  key={i}
                  className={`p-6 rounded-2xl border ${colors.border} bg-white hover:shadow-lg transition group`}
                >
                  <div className={`w-12 h-12 ${colors.bgLight} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                    <svg className={`w-6 h-6 ${colors.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
                  <p className="text-slate-600">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Use Cases Tab */}
      {activeTab === 'use-cases' && (
        <section className="py-16 lg:py-24 bg-slate-50">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
                Real-World Applications
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                See how businesses like yours use {agent.title} to save time and money.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
              {agent.useCases.map((useCase: string, i: number) => (
                <div
                  key={i}
                  className="flex items-start gap-4 bg-white p-6 rounded-xl border border-slate-200"
                >
                  <div className={`w-10 h-10 ${colors.bg} rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold`}>
                    {i + 1}
                  </div>
                  <p className="text-slate-700 text-lg">{useCase}</p>
                </div>
              ))}
            </div>

            {/* Testimonial */}
            {agent.testimonial && (
              <div className="mt-16 max-w-3xl mx-auto">
                <div className={`bg-gradient-to-r ${colors.gradient} rounded-2xl p-8 lg:p-12 text-white`}>
                  <svg className="w-12 h-12 opacity-30 mb-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                  </svg>
                  <blockquote className="text-xl lg:text-2xl font-medium mb-8 leading-relaxed">
                    "{agent.testimonial.quote}"
                  </blockquote>
                  <div className="flex items-center gap-4">
                    <Image
                      src={agent.testimonial.image}
                      alt={agent.testimonial.author}
                      width={56}
                      height={56}
                      className="w-14 h-14 rounded-full object-cover border-2 border-white/30"
                    />
                    <div>
                      <p className="font-semibold">{agent.testimonial.author}</p>
                      <p className="text-white/80 text-sm">{agent.testimonial.role}, {agent.testimonial.company}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <section className="py-16 lg:py-24">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
                Works With Your Stack
              </h2>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                {agent.title} integrates seamlessly with the tools you already use.
              </p>
            </div>

            <div className="flex flex-wrap justify-center gap-6 max-w-3xl mx-auto">
              {agent.integrations.map((integration: string, i: number) => (
                <div
                  key={i}
                  className="flex items-center gap-3 bg-white px-6 py-4 rounded-xl border border-slate-200 hover:border-slate-300 hover:shadow-md transition"
                >
                  <div className={`w-10 h-10 ${colors.bgLight} rounded-lg flex items-center justify-center`}>
                    <span className={`text-lg font-bold ${colors.text}`}>{integration.charAt(0)}</span>
                  </div>
                  <span className="font-medium text-slate-900">{integration}</span>
                </div>
              ))}
            </div>

            <div className="text-center mt-12">
              <p className="text-slate-600 mb-4">Don't see your tool? We likely support it via API or Zapier.</p>
              <Link href="/contact" className="text-sm font-medium text-slate-900 hover:underline">
                Contact us about custom integrations →
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* FAQ Tab */}
      {activeTab === 'faq' && (
        <section className="py-16 lg:py-24 bg-slate-50">
          <div className="max-w-3xl mx-auto px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl lg:text-4xl font-bold text-slate-900 mb-4">
                Frequently Asked Questions
              </h2>
              <p className="text-lg text-slate-600">
                Everything you need to know about {agent.title}.
              </p>
            </div>

            <div className="space-y-4">
              {agent.faqs.map((faq: any, i: number) => (
                <div
                  key={i}
                  className="bg-white rounded-xl border border-slate-200 overflow-hidden"
                >
                  <button
                    onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                    className="w-full flex items-center justify-between p-6 text-left"
                  >
                    <span className="font-semibold text-slate-900 pr-4">{faq.q}</span>
                    <svg
                      className={`w-5 h-5 text-slate-400 flex-shrink-0 transition-transform ${expandedFaq === i ? 'rotate-180' : ''}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {expandedFaq === i && (
                    <div className="px-6 pb-6">
                      <p className="text-slate-600 leading-relaxed">{faq.a}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Related Agents */}
      {relatedAgentsList.length > 0 && (
        <section className="py-16 lg:py-24 border-t border-slate-200">
          <div className="max-w-7xl mx-auto px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-2xl lg:text-3xl font-bold text-slate-900 mb-4">
                Related Agents
              </h2>
              <p className="text-slate-600">
                These agents work great together with {agent.title}.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {relatedAgentsList.map((related: any, i: number) => {
                const relatedId = agent.relatedAgents[i]
                const relatedColors = getColorClasses(related.color)
                
                return (
                  <Link
                    key={relatedId}
                    href={`/${relatedId}`}
                    className="group bg-white rounded-2xl overflow-hidden border border-slate-200 hover:shadow-xl transition"
                  >
                    <div className="relative h-40 overflow-hidden">
                      <Image
                        src={related.heroImage}
                        alt={related.title}
                        fill
                        className="object-cover group-hover:scale-105 transition duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-slate-900/70 to-transparent" />
                      <div className="absolute bottom-4 left-4">
                        <span className={`px-2 py-1 ${relatedColors.bgLight} ${relatedColors.text} rounded text-xs font-medium`}>
                          {related.category}
                        </span>
                      </div>
                    </div>
                    <div className="p-6">
                      <h3 className="text-lg font-bold text-slate-900 mb-1 group-hover:text-blue-600 transition">
                        {related.title}
                      </h3>
                      <p className="text-slate-600 text-sm mb-3">{related.tagline}</p>
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900">${related.price}<span className="text-slate-400 font-normal">/mo</span></span>
                        <span className="text-sm text-slate-500 group-hover:text-blue-600 transition flex items-center gap-1">
                          Learn More
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </span>
                      </div>
                    </div>
                  </Link>
                )
              })}
            </div>
          </div>
        </section>
      )}

      {/* Final CTA */}
      <section className={`py-20 lg:py-28 bg-gradient-to-r ${colors.gradient}`}>
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center text-white">
          <h2 className="text-3xl lg:text-4xl font-bold mb-6">
            Ready to Deploy {agent.title}?
          </h2>
          <p className="text-xl opacity-90 mb-10 max-w-2xl mx-auto">
            Start your 14-day free trial today. No credit card required. Cancel anytime.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`/signup?agent=${agentName}`}
              className="inline-flex items-center justify-center gap-2 bg-white text-slate-900 px-8 py-4 rounded-lg font-semibold hover:bg-slate-100 transition shadow-lg"
            >
              Start Free Trial
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
            <Link
              href="/#solutions"
              className="inline-flex items-center justify-center gap-2 border-2 border-white/30 text-white px-8 py-4 rounded-lg font-semibold hover:bg-white/10 transition"
            >
              View All Agents
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <span className="text-xl font-semibold">AgentHub</span>
            </Link>
            <div className="flex gap-8 text-sm text-slate-400">
              <Link href="/#solutions" className="hover:text-white transition">Solutions</Link>
              <Link href="/login" className="hover:text-white transition">Sign In</Link>
              <a href="#" className="hover:text-white transition">Privacy</a>
              <a href="#" className="hover:text-white transition">Terms</a>
            </div>
            <p className="text-sm text-slate-500">© 2026 AgentHub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
