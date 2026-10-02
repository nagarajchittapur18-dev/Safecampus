"""
SafeCampus AI — FastAPI Application Entry Point
================================================
Phase 1: Basic application scaffold with health endpoint.
Phase 2: Campus graph loaded at startup; locations endpoint added.
Phase 3-5: Dijkstra, A*, and Personalized Multi-Objective A* routing added.
Phase 6: Campus crowd ML model loaded and prediction endpoint added.
"""

import logging
import os
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

    # Initialise database
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
        logger.info(
            "Crowd ML model initialized: %s",
            crowd_service.model_name
        )
    except Exception as exc:
        logger.warning(
            "Could not pre-load crowd ML model at startup: %s",
            exc
        )

    yield

    # Cleanup on shutdown
    reset_graph()
    reset_crowd_service()


# ---------------------------------------------------------------------------
# Application
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
# CORS Configuration
# ---------------------------------------------------------------------------
#
# Production:
#   Render Environment Variable:
#
#   ALLOWED_ORIGINS=
#   https://safecampus-mobile-nine.vercel.app
#
# Development:
#   http://localhost:8000
#   http://127.0.0.1:8000
#
# Multiple origins can be separated with commas.
# ---------------------------------------------------------------------------

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        (
            "http://localhost:8000,"
            "http://127.0.0.1:8000,"
            "http://localhost:5000,"
            "http://127.0.0.1:5000"
        ),
    ).split(",")
    if origin.strip()
]

logger.info("CORS allowed origins: %s", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(
    health.router,
    prefix="/api",
    tags=["Health"],
)

app.include_router(
    locations.router,
    prefix="/api/locations",
    tags=["Locations"],
)

app.include_router(
    routes.router,
    prefix="/api/routes",
    tags=["Routes"],
)

app.include_router(
    crowd.router,
    prefix="/api/crowd",
    tags=["Crowd"],
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"],
)

# Future:
# app.include_router(events.router, prefix="/api/events", tags=["Events"])