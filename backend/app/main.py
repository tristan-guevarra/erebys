"""
erebys intelligence suite — fastapi application
b2b analytics + dynamic pricing engine for sports academies.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.api import auth, events, bookings, analytics, pricing, experiments, organizations, admin, imports
from app.api.coaches import router as coaches_router
from app.api.evaluations import router as evaluations_router
from app.api.platform import router as platform_router

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("erebys")


# slow down anyone who's hammering the api
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Erebys Intelligence Suite starting up…")
    logger.info(f"   Environment: {settings.environment}")
    yield
    logger.info("🛑 Erebys shutting down…")


app = FastAPI(
    title="Erebys Intelligence Suite",
    description=(
        "B2B analytics dashboard + dynamic pricing engine for sports academies. "
        "Multi-tenant SaaS with RBAC, ML-powered pricing recommendations, "
        "experiment framework, and automated insights."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# hook up rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# cors so the frontend can actually talk to us
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# wire up all the routers under /api/v1
app.include_router(auth.router, prefix="/api/v1")
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(pricing.router, prefix="/api/v1")
app.include_router(experiments.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")
app.include_router(coaches_router, prefix="/api/v1")
app.include_router(evaluations_router, prefix="/api/v1")
app.include_router(platform_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "0.1.0", "service": "erebys-api"}


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "Erebys Intelligence Suite",
        "version": "0.1.0",
        "docs": "/docs",
    }
