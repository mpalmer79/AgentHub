import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type User = {
  id: string
  email: string
  full_name?: string
  company_name?: string
  created_at: string
}

export type AgentSubscription = {
  id: string
  user_id: string
  agent_type: string
  status: string
  config: Record<string, any>
  created_at: string
}

export type AgentTask = {
  id: string
  user_id: string
  agent_type: string
  task: string
  context: Record<string, any>
  status: string
  result?: Record<string, any>
  error?: string
  created_at: string
  completed_at?: string
}
