.PHONY: help install test lint format evals dev worker frontend-dev frontend-test ready

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install:  ## Install backend + frontend dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm ci

test:  ## Run backend pytest with coverage gate
	cd backend && PYTHONPATH=. python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=70

evals:  ## Run agent evals (deterministic, no API calls)
	cd backend && PYTHONPATH=. python -m evals.run

lint:  ## Lint backend + frontend
	cd backend && ruff check .
	cd frontend && npm run lint

format:  ## Auto-format backend code
	cd backend && ruff format .

dev:  ## Run backend API with reload
	cd backend && uvicorn app.main:app --reload --port 8000

worker:  ## Run the agent task worker
	cd backend && python -m app.workers.task_worker

frontend-dev:  ## Run Next.js dev server
	cd frontend && npm run dev

frontend-test:  ## Run frontend tests
	cd frontend && npm test -- --ci --passWithNoTests

ready:  ## Run everything CI runs, locally
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) evals
	$(MAKE) frontend-test
