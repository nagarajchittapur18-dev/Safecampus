"""
SafeCampus AI — FastAPI Application Entry Point
================================================
SafeCampus AI backend application.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, crowd, health, locations, routes
from app.services.crowd_service import (
    get_crowd_service,
    reset_crowd_service,
)
from app.services.graph_service import (
    load_graph,
    reset_graph,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize database, campus graph,
    and ML crowd model when the application starts.
    """

    # Initialize database
    await init_db()

    # Load campus graph
    try:
        load_graph()
        logger.info("Campus graph loaded successfully.")
    except Exception as exc:
        logger.error(
            "Failed to load campus graph: %s",
            exc
        )
        raise

    # Load crowd ML model
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

    # Cleanup
    reset_graph()
    reset_crowd_service()


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="SafeCampus AI",

    description=(
        "Multi-Objective AI-Based Personalized Safe Route "
        "Recommendation Framework for Smart Campus Navigation"
    ),

    version="0.6.0",

    docs_url="/docs",
    redoc_url="/redoc",

    lifespan=lifespan,
)


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------

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

logger.info(
    "CORS allowed origins: %s",
    allowed_origins
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# --------------------------------------------------
# API Routers
# --------------------------------------------------

app.include_router(
    health.router,
    prefix="/api",
    tags=["Health"]
)

app.include_router(
    locations.router,
    prefix="/api/locations",
    tags=["Locations"]
)

app.include_router(
    routes.router,
    prefix="/api/routes",
    tags=["Routes"]
)

app.include_router(
    crowd.router,
    prefix="/api/crowd",
    tags=["Crowd"]
)

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Auth"]
)


# Future routers can be added here
# app.include_router(
#     events.router,
#     prefix="/api/events",
#     tags=["Events"]
# )