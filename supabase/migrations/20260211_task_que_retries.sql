-- 1) agent_task_queue: retry + locking + scheduling
alter table if exists public.agent_task_queue
  add column if not exists attempts int not null default 0,
  add column if not exists max_attempts int not null default 3,
  add column if not exists next_run_at timestamptz not null default now(),
  add column if not exists last_error text null,
  add column if not exists locked_at timestamptz null,
  add column if not exists locked_by text null;

create index if not exists idx_agent_task_queue_status_next_run
  on public.agent_task_queue (status, next_run_at);

create index if not exists idx_agent_task_queue_locked_at
  on public.agent_task_queue (locked_at);

-- 2) agent_tasks: failure classification + retryability
alter table if exists public.agent_tasks
  add column if not exists failure_code text null,
  add column if not exists error_detail text null,
  add column if not exists retryable boolean not null default false;

-- Optional: If you want stricter enums later, keep this as text for now (fast iteration).

-- 3) sensible defaults for existing queued records
update public.agent_task_queue
set next_run_at = now()
where next_run_at is null;

-- 4) (Recommended) prevent attempts from going negative
alter table public.agent_task_queue
  add constraint if not exists chk_agent_task_queue_attempts_nonnegative
  check (attempts >= 0 and max_attempts >= 1);
