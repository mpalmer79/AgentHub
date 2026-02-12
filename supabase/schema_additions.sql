-- ============================================================
-- AGENT TASK EVENTS - FOR REAL-TIME STREAMING
-- ============================================================

CREATE TABLE IF NOT EXISTS public.agent_task_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES public.agent_tasks(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    message TEXT,
    payload JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.agent_task_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own task events" ON public.agent_task_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own task events" ON public.agent_task_events FOR ALL USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_agent_task_events_task ON public.agent_task_events(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_task_events_user ON public.agent_task_events(user_id);


-- ============================================================
-- CUSTOMERCARE AI - DATABASE SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS public.ticket_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ticket_id TEXT NOT NULL,
    response TEXT,
    is_internal BOOLEAN DEFAULT FALSE,
    new_status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.ticket_escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    ticket_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    escalation_level TEXT DEFAULT 'tier2',
    assigned_to TEXT,
    status TEXT DEFAULT 'escalated',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.ticket_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticket_escalations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own ticket responses" ON public.ticket_responses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own ticket responses" ON public.ticket_responses FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own ticket escalations" ON public.ticket_escalations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own ticket escalations" ON public.ticket_escalations FOR ALL USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_ticket_responses_user ON public.ticket_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_ticket_responses_ticket ON public.ticket_responses(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_escalations_user ON public.ticket_escalations(user_id);
CREATE INDEX IF NOT EXISTS idx_ticket_escalations_ticket ON public.ticket_escalations(ticket_id);


-- ============================================================
-- SOCIALPILOT AI - DATABASE SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS public.social_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    content TEXT NOT NULL,
    media_url TEXT,
    link TEXT,
    status TEXT DEFAULT 'draft',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.scheduled_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    content TEXT NOT NULL,
    media_url TEXT,
    scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status TEXT DEFAULT 'scheduled',
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.social_comment_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    post_id TEXT NOT NULL,
    comment_id TEXT NOT NULL,
    response TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    posted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheduled_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_comment_responses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own social posts" ON public.social_posts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own social posts" ON public.social_posts FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own scheduled posts" ON public.scheduled_posts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own scheduled posts" ON public.scheduled_posts FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own comment responses" ON public.social_comment_responses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own comment responses" ON public.social_comment_responses FOR ALL USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_social_posts_user ON public.social_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON public.social_posts(platform);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user ON public.scheduled_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_time ON public.scheduled_posts(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_social_comment_responses_user ON public.social_comment_responses(user_id);


-- ============================================================
-- REPUTATION SHIELD AI - DATABASE SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS public.review_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    review_id TEXT NOT NULL,
    reviewer_name TEXT,
    rating INTEGER,
    response TEXT NOT NULL,
    status TEXT DEFAULT 'draft',
    posted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.review_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    customer_email TEXT NOT NULL,
    customer_name TEXT,
    platform TEXT,
    message_id TEXT,
    status TEXT DEFAULT 'sent',
    clicked_at TIMESTAMP WITH TIME ZONE,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.competitor_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    competitor_name TEXT NOT NULL,
    platform TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE public.review_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.review_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competitor_tracking ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own review responses" ON public.review_responses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own review responses" ON public.review_responses FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own review requests" ON public.review_requests FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own review requests" ON public.review_requests FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own competitor tracking" ON public.competitor_tracking FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own competitor tracking" ON public.competitor_tracking FOR ALL USING (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS idx_review_responses_user ON public.review_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_review_requests_user ON public.review_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_competitor_tracking_user ON public.competitor_tracking(user_id);
