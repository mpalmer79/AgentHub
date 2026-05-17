# Architecture

## System overview

```
┌──────────────┐      ┌────────────────┐      ┌──────────────────┐
│   Browser    │─────▶│ Next.js (Vercel)│────▶│ FastAPI (Railway)│
└──────────────┘      └────────────────┘      └────────┬─────────┘
                              │                        │
                              ▼                        ▼
                       ┌───────────────────────────────────┐
                       │  Supabase (Postgres + Auth + RLS) │
                       └───────────────────────────────────┘
                                       ▲
                                       │
                        ┌──────────────┴──────────────┐
                        │  Worker (Railway, separate) │
                        │  - polls agent_task_queue   │
                        │  - runs AgentRuntime        │
                        │  - calls Anthropic + tools  │
                        └─────────────────────────────┘
```

## Request lifecycle

1. **Auth.** Frontend gets a Supabase JWT via the JS SDK. Backend
   validates JWTs against Supabase JWKS on every protected route
   (`app/core/auth.py`). RLS in Postgres provides the second layer.
2. **Task submission.** `POST /api/agents/run` writes a row to
   `agent_tasks` (status=queued) and pushes onto `agent_task_queue`.
3. **Worker pickup.** A separate worker process polls the queue,
   atomically claims a row (best-effort: select + conditional update +
   re-read), and hands it to `AgentRuntime`.
4. **Agent loop.** The runtime calls Claude with the agent-specific
   system prompt + tool schemas. On `tool_use`, it dispatches to
   `ToolExecutor`, appends the result, and loops. Stops on `end_turn`,
   `max_iterations`, or `BUDGET_EXCEEDED`.
5. **Observability.** Every step writes a row to `agent_task_events`
   with token counts, stop reason, and tool input/result previews.

## Key abstractions

| Layer | Module | Responsibility |
|---|---|---|
| Registry | `agents/registry.py` | Static metadata for each agent (price, features, required integrations) |
| Prompts | `agents/prompts/agent_prompts.py` | System prompts, versioned via `PROMPT_VERSION` |
| Schemas | `agents/schemas/*.py` | Declarative tool definitions sent to Claude |
| Executor | `agents/executors/tool_executor.py` | Routes tool name → tool instance method |
| Tools | `agents/tools/*.py` | Async HTTP clients for QB, Gmail, Calendar, etc. |
| Runtime | `agents/runtime.py` | Claude tool-use loop + budget + event emission |
| Worker | `workers/task_worker.py` | Queue claim + retry/backoff (`workers/backoff.py`, `failure.py`) |
| API | `api/*.py` | FastAPI routers for auth, agents, integrations, tasks, webhooks |
| Core | `core/*.py` | Cross-cutting: config, db client, JWT, crypto, logging, rate limit, budget |

## Failure model

Exceptions inside the worker are classified by
`workers/failure.py::classify_failure` into stable codes:

| Code | Retryable? | Examples |
|---|---|---|
| `CONFIG_MISSING` | no | env var unset |
| `AUTH_REQUIRED` | no | OAuth token expired/invalid |
| `RATE_LIMITED` | yes | 429 from upstream |
| `PROVIDER_ERROR` | yes | 5xx from Anthropic/integration |
| `MODEL_ERROR` | yes | Anthropic returned an error |
| `TOOL_ERROR` | no | bug in a tool implementation |
| `BUDGET_EXCEEDED` | no | task hit `AGENT_MAX_TOKENS_PER_TASK` |
| `MAX_ITERATIONS` | no | task hit `AGENT_MAX_ITERATIONS` |
| `UNKNOWN` | no | fallthrough |

Retryable failures re-enter the queue with exponential backoff
(`workers/backoff.py`), capped at `max_attempts`.

## Data model

See `supabase/schema.sql` for the canonical schema. Highlights:

- `users` — extends `auth.users`, holds Stripe IDs and subscription status.
- `agent_subscriptions` — which agents a user has activated.
- `agent_tasks` — every task submitted (queued, running, completed, failed).
- `agent_task_queue` — pending work; locked by `worker_id` while running.
- `agent_task_events` — append-only audit log; one row per state change.
- `user_integrations` — encrypted OAuth tokens (Fernet via `core/crypto.py`).
- `oauth_states` — short-lived CSRF state for OAuth flows.
- `schema_migrations` — applied-migration tracker.

All user-scoped tables enable RLS. Service-role client (used by the
worker and webhooks) bypasses RLS by design.

## Why these choices

- **FastAPI + Supabase.** Lets one engineer ship auth, RLS, realtime,
  and an API in days instead of weeks. We pay for that with a polling
  job queue instead of pub/sub — acceptable until ~10k concurrent users.
- **Claude tool-use over LangChain/CrewAI.** Direct SDK gives full
  control over the loop, easy observability, and zero abstraction tax.
  Re-implementing the loop is ~50 LOC.
- **Declarative tool schemas.** Keeps tool definitions in source
  control, diff-reviewable, and decoupled from the tool implementation.
- **Fernet for OAuth tokens.** Symmetric, fast, well-vetted. Key
  rotation is manual (re-encrypt all rows) — acceptable for now.

## Known limitations

- Job queue is **polled** (2s interval), not pub/sub. Migrating to
  PG `LISTEN/NOTIFY` is the cheapest upgrade.
- Anthropic-only. OpenAI key is plumbed in config but unused. A
  `ModelProvider` interface would unlock fallback.
- Manual migrations. `scripts/apply_migrations.py` is forward-only; no
  down-migrations or transactional rollbacks across multiple files.
- Single region. Disaster recovery depends on Supabase's PITR.
