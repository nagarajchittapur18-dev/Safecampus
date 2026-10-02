"""
SafeCampus AI — FastAPI Application Entry Point
================================================
Phase 1: Basic application scaffold with health endpoint.
Phase 2: Campus graph loaded at startup; locations endpoint added.
Phase 3-5: Dijkstra, A*, and Personalized Multi-Objective A* routing added.
Phase 6: Campus crowd ML model loaded and prediction endpoint added.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, crowd, health, locations, routes
from app.services.crowd_service import get_crowd_service, reset_crowd_service
from app.services.graph_service import load_graph, reset_graph

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — runs on startup and shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise database, campus graph, and ML crowd models on startup."""
    await init_db()

    # Load campus graph into memory
    try:
        load_graph()
        logger.info("Campus graph loaded successfully.")
    except Exception as exc:
        logger.error("Failed to load campus graph: %s", exc)
        raise

    # Warm up ML crowd model
    try:
        crowd_service = get_crowd_service()
        logger.info("Crowd ML model initialized: %s", crowd_service.model_name)
    except Exception as exc:
        logger.warning("Could not pre-load crowd ML model at startup: %s", exc)

    yield

    # Cleanup on shutdown
    reset_graph()
    reset_crowd_service()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SafeCampus AI",
    description=(
        "Multi-Objective AI-Based Personalized Safe Route Recommendation "
        "Framework for Smart Campus Navigation"
    ),
    version="0.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow Flutter app (any origin in development)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health.router,     prefix="/api",            tags=["Health"])
app.include_router(locations.router,  prefix="/api/locations",  tags=["Locations"])
app.include_router(routes.router,     prefix="/api/routes",     tags=["Routes"])
app.include_router(crowd.router,      prefix="/api/crowd",      tags=["Crowd"])
app.include_router(auth.router,       prefix="/api/auth",       tags=["Auth"])
# app.include_router(events.router, prefix="/api/events", tags=["Events"])
