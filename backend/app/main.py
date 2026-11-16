"""
FastAPI application entry point.
Configures middleware, routers, exception handlers, and startup events.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.utils.logger import get_logger
from app.routers import auth, users, faculty, publications, agents, analytics, reports, duplicates, verification, system

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Starting Research Portal API v%s [%s]", settings.APP_VERSION, settings.ENVIRONMENT)
    try:
        from app.database import engine, Base
        import app.models  # noqa: F401
        Base.metadata.create_all(bind=engine)

        from app.database import SessionLocal
        from app.models.user import User, UserRole
        from app.utils.auth import hash_password
        with SessionLocal() as db:
            admin_user = db.query(User).filter(User.email == "admin@university.edu").first()
            if not admin_user:
                admin_user = User(
                    email="admin@university.edu",
                    hashed_password=hash_password("Admin@123456"),
                    full_name="System Administrator",
                    role=UserRole.admin,
                    is_active=True,
                )
                db.add(admin_user)
                db.commit()
                logger.info("Default administrator account initialized (admin@university.edu)")
    except Exception as exc:
        logger.warning("Database startup notice: %s", exc)
    yield
    logger.info("Shutting down Research Portal API.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Research Intelligence & Publication Analytics Portal — "
        "multi-agent backend for faculty publication tracking, "
        "citation analytics, duplicate detection, and NIRF/NAAC reporting."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{API_PREFIX}/users", tags=["Users"])
app.include_router(faculty.router, prefix=f"{API_PREFIX}/faculty", tags=["Faculty"])
app.include_router(publications.router, prefix=f"{API_PREFIX}/publications", tags=["Publications"])
app.include_router(agents.router, prefix=f"{API_PREFIX}/agents", tags=["Agents"])
app.include_router(analytics.router, prefix=f"{API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(reports.router, prefix=f"{API_PREFIX}/reports", tags=["Reports"])
app.include_router(duplicates.router, prefix=f"{API_PREFIX}/duplicates", tags=["Duplicates"])
app.include_router(verification.router, prefix=f"{API_PREFIX}/verification", tags=["Verification"])
app.include_router(system.router, prefix=f"{API_PREFIX}/system", tags=["System"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}
