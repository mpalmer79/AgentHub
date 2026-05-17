# Agent Evals

Behavioral regression tests for agents. Hermetic and free — no Anthropic
API key required, no network calls.

## Run locally

```bash
cd backend
PYTHONPATH=. python -m evals.run
```

Exit code is non-zero if any case fails, so this is wired into CI as a
required check.

## Add a case

1. Open `evals/cases.py`.
2. Append a `Case(...)`:
   - `agent`: which `AgentType` to instantiate.
   - `task`: the user request.
   - `scripted_responses`: ordered list of fake Claude responses. Use
     `tool_call(id, name, args)` or `text("...")` helpers.
   - `tool_responses`: what the executor returns for each tool the model
     tries to invoke.
   - `expect_tools`: tool names that **must** have been called.
   - `assert_fn`: optional callable that receives the runtime result
     and can `assert` on its shape/content.

## When to add a case

- A customer reports an agent doing something stupid → add a case that
  fails today, then fix the prompt/code until it passes.
- A new safety guideline is added to a prompt → add a case that proves
  the agent honors it.
- A new tool is added to an agent → add at least one case that exercises
  the happy path.
