from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api import agents, auth, integrations, tasks, webhooks
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.observability import init_sentry
from app.core.ratelimit import limiter

configure_logging(settings.LOG_LEVEL)
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_production():
        settings.validate_production_ready()
    init_sentry()
    log.info(
        "startup",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": settings.VERSION,
            "model": settings.AGENT_MODEL,
        },
    )
    yield
    log.info("shutdown")


app = FastAPI(
    title="AgentHub API",
    description="AI Agent Marketplace for SMB Operations",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


@app.middleware("http")
async def access_log(request: Request, call_next):
    """Emit one structured access-log line per request."""
    response = await call_next(request)
    log.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "client": request.client.host if request.client else None,
        },
    )
    return response


app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    return {"name": settings.PROJECT_NAME, "version": settings.VERSION, "status": "operational"}


@app.get("/health")
async def health_check():
    """Liveness probe. Always cheap; doesn't touch external systems."""
    return {"status": "healthy", "service": "agenthub-api", "version": settings.VERSION}


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe: returns 503 if a critical dependency is missing.

    Used by Railway/k8s to decide whether to route traffic. Validates
    configuration of all required external services without making
    network calls (those happen lazily and are reported in their own
    failure codes).
    """
    checks: dict[str, dict] = {}
    ok = True

    def add(name: str, healthy: bool, detail: str = ""):
        nonlocal ok
        checks[name] = {"healthy": healthy, "detail": detail}
        if not healthy:
            ok = False

    add("supabase_config", bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY),
        "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")
    add("supabase_jwks", bool(settings.resolved_jwks_url()),
        "JWKS URL could not be resolved")
    add("anthropic", bool(settings.ANTHROPIC_API_KEY),
        "ANTHROPIC_API_KEY required for agent runtime")
    add("encryption", bool(settings.INTEGRATION_ENCRYPTION_KEY),
        "INTEGRATION_ENCRYPTION_KEY required for OAuth token storage")

    status_code = 200 if ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if ok else "not_ready", "checks": checks},
    )
