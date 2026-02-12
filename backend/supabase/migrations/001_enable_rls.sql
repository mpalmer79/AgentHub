-- Enable Row Level Security and enforce ownership using auth.uid()

alter table if exists public.agent_tasks enable row level security;
alter table if exists public.agent_task_queue enable row level security;
alter table if exists public.agent_subscriptions enable row level security;
alter table if exists public.integrations enable row level security;

-- agent_tasks: users can only see their own
drop policy if exists "agent_tasks_select_own" on public.agent_tasks;
create policy "agent_tasks_select_own"
on public.agent_tasks for select
using (user_id = auth.uid());

drop policy if exists "agent_tasks_insert_own" on public.agent_tasks;
create policy "agent_tasks_insert_own"
on public.agent_tasks for insert
with check (user_id = auth.uid());

drop policy if exists "agent_tasks_update_own" on public.agent_tasks;
create policy "agent_tasks_update_own"
on public.agent_tasks for update
using (user_id = auth.uid())
with check (user_id = auth.uid());

-- agent_subscriptions
drop policy if exists "agent_subscriptions_select_own" on public.agent_subscriptions;
create policy "agent_subscriptions_select_own"
on public.agent_subscriptions for select
using (user_id = auth.uid());

drop policy if exists "agent_subscriptions_insert_own" on public.agent_subscriptions;
create policy "agent_subscriptions_insert_own"
on public.agent_subscriptions for insert
with check (user_id = auth.uid());

drop policy if exists "agent_subscriptions_update_own" on public.agent_subscriptions;
create policy "agent_subscriptions_update_own"
on public.agent_subscriptions for update
using (user_id = auth.uid())
with check (user_id = auth.uid());

-- integrations
drop policy if exists "integrations_select_own" on public.integrations;
create policy "integrations_select_own"
on public.integrations for select
using (user_id = auth.uid());

drop policy if exists "integrations_insert_own" on public.integrations;
create policy "integrations_insert_own"
on public.integrations for insert
with check (user_id = auth.uid());

drop policy if exists "integrations_update_own" on public.integrations;
create policy "integrations_update_own"
on public.integrations for update
using (user_id = auth.uid())
with check (user_id = auth.uid());
