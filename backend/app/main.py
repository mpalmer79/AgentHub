from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import auth, agents, integrations, tasks, webhooks
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 AgentHub API starting up...")
    yield
    print("👋 AgentHub API shutting down...")


app = FastAPI(
    title="AgentHub API",
    description="AI Agent Marketplace for SMB Operations",
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

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
    return {"status": "healthy", "service": "agenthub-api"}
