"""
SK AgentCorp — FastAPI Application Entry Point

Initializes the app, registers routers, starts the heartbeat,
and serves both the API and WebSocket endpoints.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import close_db, init_db
from backend.engine.heartbeat import start_heartbeat, stop_heartbeat
from backend.routers import agents, budget, companies, dashboard, tasks, websocket

# ── Logging ──────────────────────────────────────────────────────────
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s │ %(levelname)-8s │ %(name)-30s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    # Startup
    logger.info("=" * 60)
    logger.info(f"  🚀 {settings.app_name} v{settings.app_version}")
    logger.info(f"  📊 Dashboard: http://localhost:8000")
    logger.info(f"  📡 API Docs:  http://localhost:8000/docs")
    logger.info("=" * 60)

    await init_db()
    logger.info("Database initialized")

    start_heartbeat()
    logger.info("Heartbeat scheduler started")

    yield

    # Shutdown
    stop_heartbeat()
    await close_db()
    logger.info("SK AgentCorp shutdown complete")


# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "SK AgentCorp — The Next-Gen Zero-Human Company Operating System. "
        "Run entire companies with AI agents 24/7."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────────────────
app.include_router(companies.router)
app.include_router(agents.router)
app.include_router(tasks.router)
app.include_router(budget.router)
app.include_router(dashboard.router)
app.include_router(websocket.router)


# ── Health Check ─────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/")
async def root():
    """Root redirect to docs."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "dashboard": "http://localhost:5173",
    }
