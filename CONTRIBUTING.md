# Contributing

## Workflow

1. Branch from `main`: `git checkout -b feat/<short-description>`.
2. Make your changes. Keep commits small and focused.
3. Run the full local check:
   ```bash
   cd backend && ruff check . && ruff format --check . && PYTHONPATH=. pytest && PYTHONPATH=. python -m evals.run
   cd frontend && npm run lint && npm test -- --ci --passWithNoTests
   ```
4. Open a PR. CI must be green before review.

## What CI enforces

- **Backend lint** (`ruff check`, `ruff format --check`) — hard fail.
- **Backend type check** (`mypy`) — soft warning, becoming hard once
  coverage reaches 100%.
- **Backend tests** with `--cov-fail-under=70` — hard fail.
- **Backend evals** (`python -m evals.run`) — hard fail.
- **Security scan** (`pip-audit --strict`, `npm audit --audit-level=high`) — hard fail.
- **Frontend lint, typecheck, build, tests** — all hard fail.

If you raise the coverage floor in this PR, raise the threshold in
`.github/workflows/ci.yml` too.

## Code style

- Type-hint everything. The mypy gate will tighten over time.
- Default to no comments. Add a comment only when *why* is non-obvious.
- One responsibility per module. New agents follow the layout in
  [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#adding-a-new-agent).
- Keep functions short; prefer pure helpers over class methods when
  there is no state.

## Prompts

Changing any agent prompt requires bumping `PROMPT_VERSION` in
`backend/app/agents/prompts/agent_prompts.py`. The version is recorded
on every task, so support engineers can attribute regressions to a
specific revision.

## Evals

Add a new case to `backend/evals/cases.py` whenever:

- A customer reports an agent behaving badly (lock in the fix).
- A new safety guideline is added to a prompt.
- A new tool is added (at least one happy-path case).

See [`backend/evals/README.md`](backend/evals/README.md).

## Security

- Never commit `.env` files or secrets.
- All new endpoints that accept user input should use a Pydantic model
  for validation.
- All user-scoped Supabase queries must use `get_supabase(user.token)`
  so RLS applies. Service-role client is only for workers and webhooks.
- Rate-limit any unauthenticated endpoint with `@limiter.limit(...)`.

## Migrations

Add a new file to `supabase/migrations/` named
`YYYYMMDD_short_description.sql`. It will be applied by
`scripts/apply_migrations.py` on the next deploy. Forward-only; no
down-migrations.

## Reporting vulnerabilities

Email the maintainer directly rather than opening a public issue.
