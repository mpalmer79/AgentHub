# Developer Setup

## Prerequisites

- **Python** 3.11+
- **Node.js** 20+
- **Supabase** project (free tier is fine for dev)
- **Anthropic** API key

## First-time setup

```bash
git clone <repo>
cd AgentHub
```

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in SUPABASE_*, ANTHROPIC_API_KEY, INTEGRATION_ENCRYPTION_KEY at minimum.
# Generate the encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local  # or create one with:
# NEXT_PUBLIC_SUPABASE_URL=...
# NEXT_PUBLIC_SUPABASE_ANON_KEY=...
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Database

Two options for applying schema to a fresh Supabase project:

**A. One-shot (good for dev):**
Paste `supabase/schema.sql` into the Supabase SQL editor and run.

**B. Migration-tracked (required for production):**
```bash
export DATABASE_URL="postgresql://postgres:<pass>@db.<project>.supabase.co:5432/postgres"
python scripts/apply_migrations.py
```
This applies every file in `supabase/migrations/` once, idempotently,
tracked in the `schema_migrations` table.

## Run locally

Three terminals:

```bash
# Terminal 1: API
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: worker (processes queued agent tasks)
cd backend && python -m app.workers.task_worker

# Terminal 3: frontend
cd frontend && npm run dev
```

Visit http://localhost:3000.

## Test

```bash
# Backend tests
cd backend && PYTHONPATH=. pytest

# Backend agent evals (deterministic, no API calls)
cd backend && PYTHONPATH=. python -m evals.run

# Frontend tests
cd frontend && npm test
```

## Lint & format

```bash
cd backend && ruff check . && ruff format .
cd frontend && npm run lint
```

## Health checks

- `GET /health` — liveness; cheap, always 200.
- `GET /health/ready` — readiness; returns 503 if a required env var is
  missing. Use this as your container orchestrator's readiness probe.

## Adding a new agent

1. Append a member to `AgentType` in `backend/app/agents/registry.py`.
2. Register its metadata in `AGENT_REGISTRY`.
3. Add tools to `backend/app/agents/tools/<your_agent>.py`.
4. Add a schema file under `backend/app/agents/schemas/`.
5. Wire the tool map in `backend/app/agents/executors/tool_executor.py`.
6. Wire the runtime tuple in `TOOLS_REGISTRY` in `runtime.py`.
7. Add a system prompt to `prompts/agent_prompts.py` and bump `PROMPT_VERSION`.
8. Add at least one eval case to `backend/evals/cases.py`.

## Changing a prompt

Bump `PROMPT_VERSION` in `backend/app/agents/prompts/agent_prompts.py`.
Every task records the version that ran it, so you can attribute
regressions to a specific revision after the fact.

## Cost guardrails

Per-task token budget defaults to **200K**, configured via
`AGENT_MAX_TOKENS_PER_TASK`. The runtime aborts a task with
`failure_code=BUDGET_EXCEEDED` if a single task exceeds it. Reduce the
ceiling when running cheap agents; raise it for ones that legitimately
need more context.

## Observability

- Logs are JSON-formatted (see `app/core/logging.py`). Aggregate them in
  Datadog/Loki/CloudWatch by piping container stdout.
- Sentry is enabled when `SENTRY_DSN` is set; no-op otherwise.
- Every agent task emits structured events to `agent_task_events`
  (task_started, model_call_*, tool_called, tool_result, task_completed,
  task_failed) — build dashboards off this table.
