-- Track applied migrations so we stop relying on humans to remember.
--
-- Usage:
--   1. Apply this file once via `psql $DATABASE_URL -f 20260517_schema_migrations.sql`
--      or the Supabase SQL editor.
--   2. For every subsequent migration, append a row at the bottom of the file:
--          INSERT INTO public.schema_migrations (version, name)
--          VALUES ('20260601_something', 'something')
--          ON CONFLICT (version) DO NOTHING;
--   3. `scripts/apply_migrations.py` reads the migrations/ directory and only
--      applies files whose stem is not yet in schema_migrations.

CREATE TABLE IF NOT EXISTS public.schema_migrations (
    version TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Record the baselines that already exist in production. Safe to re-run.
INSERT INTO public.schema_migrations (version, name) VALUES
    ('00000000_baseline_schema', 'Initial schema.sql baseline'),
    ('20260211_task_que_retries', 'Add retry/backoff columns to agent_task_queue'),
    ('20260517_schema_migrations', 'Track applied migrations')
ON CONFLICT (version) DO NOTHING;
