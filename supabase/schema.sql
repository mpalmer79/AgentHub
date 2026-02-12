-- AgentHub Database Schema
-- Run this in Supabase SQL Editor

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    company_name TEXT,
    stripe_customer_id TEXT,
    subscription_status TEXT DEFAULT 'trial',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent subscriptions
CREATE TABLE public.agent_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cancelled_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, agent_type, status)
);

-- Agent tasks
CREATE TABLE public.agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL,
    task TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending',
    result JSONB,
    error TEXT,
    approval_feedback TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    retried_at TIMESTAMP WITH TIME ZONE
);

-- User integrations (OAuth tokens)
CREATE TABLE public.user_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    integration_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at DOUBLE PRECISION,
    realm_id TEXT,
    account_name TEXT,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    disconnected_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, integration_type)
);

-- OAuth states (temporary, for OAuth flow)
CREATE TABLE public.oauth_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state TEXT NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    integration_type TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pending categorizations (for bookkeeper agent)
CREATE TABLE public.pending_categorizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    transaction_id TEXT NOT NULL,
    new_category TEXT NOT NULL,
    account_id TEXT,
    memo TEXT,
    status TEXT DEFAULT 'pending_approval',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE
);

-- Flagged transactions (for bookkeeper agent)
CREATE TABLE public.flagged_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    transaction_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    suggested_action TEXT,
    status TEXT DEFAULT 'pending_review',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Email drafts (for inbox commander agent)
CREATE TABLE public.email_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    draft_id TEXT NOT NULL,
    original_email_id TEXT,
    subject TEXT,
    to_address TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE
);

-- Email follow-ups (for inbox commander agent)
CREATE TABLE public.email_followups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    email_id TEXT NOT NULL,
    thread_id TEXT,
    subject TEXT,
    from_address TEXT,
    followup_date DATE NOT NULL,
    followup_note TEXT,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Webhook events
CREATE TABLE public.webhook_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    integration_type TEXT NOT NULL,
    event_type TEXT,
    entity_type TEXT,
    entity_id TEXT,
    payload JSONB,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent task queue (for async processing)
CREATE TABLE public.agent_task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES public.agent_tasks(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'queued',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_agent_subscriptions_user ON public.agent_subscriptions(user_id);
CREATE INDEX idx_agent_subscriptions_status ON public.agent_subscriptions(status);
CREATE INDEX idx_agent_tasks_user ON public.agent_tasks(user_id);
CREATE INDEX idx_agent_tasks_status ON public.agent_tasks(status);
CREATE INDEX idx_agent_tasks_created ON public.agent_tasks(created_at DESC);
CREATE INDEX idx_user_integrations_user ON public.user_integrations(user_id);
CREATE INDEX idx_oauth_states_state ON public.oauth_states(state);
CREATE INDEX idx_webhook_events_processed ON public.webhook_events(processed);

-- Row Level Security (RLS) Policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pending_categorizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flagged_transactions ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own subscriptions" ON public.agent_subscriptions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own subscriptions" ON public.agent_subscriptions FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own tasks" ON public.agent_tasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own tasks" ON public.agent_tasks FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own integrations" ON public.user_integrations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own integrations" ON public.user_integrations FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own pending categorizations" ON public.pending_categorizations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own pending categorizations" ON public.pending_categorizations FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own flagged transactions" ON public.flagged_transactions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own flagged transactions" ON public.flagged_transactions FOR ALL USING (auth.uid() = user_id);

-- Scheduled appointments (for appointment agent)
CREATE TABLE public.scheduled_appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    event_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    attendees JSONB DEFAULT '[]',
    status TEXT DEFAULT 'confirmed',
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    rescheduled_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

-- Appointment reminders (for appointment agent)
CREATE TABLE public.appointment_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    event_id TEXT NOT NULL,
    summary TEXT,
    start_time TEXT,
    attendees JSONB DEFAULT '[]',
    reminder_message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS for appointment tables
ALTER TABLE public.scheduled_appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointment_reminders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own scheduled appointments" ON public.scheduled_appointments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own scheduled appointments" ON public.scheduled_appointments FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own appointment reminders" ON public.appointment_reminders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own appointment reminders" ON public.appointment_reminders FOR ALL USING (auth.uid() = user_id);

-- Indexes for appointment tables
CREATE INDEX idx_scheduled_appointments_user ON public.scheduled_appointments(user_id);
CREATE INDEX idx_scheduled_appointments_event ON public.scheduled_appointments(event_id);
CREATE INDEX idx_appointment_reminders_user ON public.appointment_reminders(user_id);

-- Candidate screenings (for hire well agent)
CREATE TABLE public.candidate_screenings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    email_id TEXT NOT NULL,
    candidate_email TEXT,
    subject TEXT,
    required_matches JSONB DEFAULT '[]',
    required_missing JSONB DEFAULT '[]',
    preferred_matches JSONB DEFAULT '[]',
    required_score NUMERIC(5,2),
    preferred_score NUMERIC(5,2),
    overall_score NUMERIC(5,2),
    recommendation TEXT,
    status TEXT DEFAULT 'screened',
    screened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Interview schedule (for hire well agent)
CREATE TABLE public.interview_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    event_id TEXT,
    candidate_email TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    interview_type TEXT,
    scheduled_time TEXT,
    duration_minutes INTEGER DEFAULT 60,
    interviewers JSONB DEFAULT '[]',
    status TEXT DEFAULT 'scheduled',
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Scheduled interviews (legacy/alternate - for hire well agent)
CREATE TABLE public.scheduled_interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    event_id TEXT,
    candidate_email TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    interview_type TEXT,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    interviewers JSONB DEFAULT '[]',
    status TEXT DEFAULT 'scheduled',
    feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Candidate communications (for hire well agent)
CREATE TABLE public.candidate_communications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    candidate_email TEXT NOT NULL,
    candidate_name TEXT,
    job_title TEXT,
    communication_type TEXT,
    status TEXT,
    message_id TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reference checks (for hire well agent)
CREATE TABLE public.reference_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    candidate_email TEXT NOT NULL,
    candidate_name TEXT NOT NULL,
    reference_email TEXT NOT NULL,
    reference_name TEXT NOT NULL,
    job_title TEXT,
    message_id TEXT,
    status TEXT DEFAULT 'sent',
    response TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    responded_at TIMESTAMP WITH TIME ZONE
);

-- RLS for hiring tables
ALTER TABLE public.candidate_screenings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.interview_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reference_checks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own candidate screenings" ON public.candidate_screenings FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own candidate screenings" ON public.candidate_screenings FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own interview schedule" ON public.interview_schedule FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own interview schedule" ON public.interview_schedule FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own scheduled interviews" ON public.scheduled_interviews FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own scheduled interviews" ON public.scheduled_interviews FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own candidate communications" ON public.candidate_communications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own candidate communications" ON public.candidate_communications FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own reference checks" ON public.reference_checks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own reference checks" ON public.reference_checks FOR ALL USING (auth.uid() = user_id);

-- Indexes for hiring tables
CREATE INDEX idx_candidate_screenings_user ON public.candidate_screenings(user_id);
CREATE INDEX idx_interview_schedule_user ON public.interview_schedule(user_id);
CREATE INDEX idx_scheduled_interviews_user ON public.scheduled_interviews(user_id);
CREATE INDEX idx_candidate_communications_user ON public.candidate_communications(user_id);
CREATE INDEX idx_reference_checks_user ON public.reference_checks(user_id);

-- Cash flow projections (for cashflow commander agent)
CREATE TABLE public.cashflow_projections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    projection_days INTEGER,
    current_cash NUMERIC(15,2),
    projections JSONB DEFAULT '[]',
    cash_crunches JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoice reminders (for cashflow commander agent)
CREATE TABLE public.invoice_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    customer_name TEXT NOT NULL,
    invoice_number TEXT NOT NULL,
    amount NUMERIC(15,2),
    days_overdue INTEGER,
    reminder_type TEXT,
    customer_email TEXT,
    status TEXT DEFAULT 'generated',
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS for cashflow tables
ALTER TABLE public.cashflow_projections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoice_reminders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own cashflow projections" ON public.cashflow_projections FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own cashflow projections" ON public.cashflow_projections FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own invoice reminders" ON public.invoice_reminders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own invoice reminders" ON public.invoice_reminders FOR ALL USING (auth.uid() = user_id);

-- Indexes for cashflow tables
CREATE INDEX idx_cashflow_projections_user ON public.cashflow_projections(user_id);
CREATE INDEX idx_invoice_reminders_user ON public.invoice_reminders(user_id);

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Clean up old OAuth states (run periodically)
CREATE OR REPLACE FUNCTION cleanup_old_oauth_states()
RETURNS void AS $$
BEGIN
    DELETE FROM public.oauth_states WHERE created_at < NOW() - INTERVAL '1 hour';
END;
$$ LANGUAGE plpgsql;
