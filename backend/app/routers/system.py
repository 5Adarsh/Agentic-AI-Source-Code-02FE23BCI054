"""
System router — external API configuration status, environment diagnostics,
and institutional DEMO data seeding/cleanup for KLE Technological University.
All seeded records are clearly identified and can be wiped cleanly.
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_admin_user, get_current_user
from app.models.agent import AgentExecution, AgentLog, ExecutionStatus
from app.models.duplicate import DuplicateCandidate, DuplicateStatus, MatchType
from app.models.faculty import Department, Faculty
from app.models.publication import (
    Publication,
    PublicationAuthor,
    PublicationSource,
    PublicationStatus,
    PublicationType,
    SourceName,
)
from app.models.user import User, UserRole
from app.models.verification import PublicationVerification
from app.utils.auth import hash_password

router = APIRouter()


class ApiStatusOut(BaseModel):
    service: str
    configured: bool
    details: str


class SystemOverviewOut(BaseModel):
    app_name: str
    version: str
    environment: str
    llm_provider: str
    database_url_type: str
    integrations: List[ApiStatusOut]


@router.get("/config-status", response_model=SystemOverviewOut, summary="Get system integrations and configuration status")
def get_config_status(_=Depends(get_current_user)):
    db_type = "SQLite" if settings.DATABASE_URL.startswith("sqlite") else "PostgreSQL"
    integrations = [
        ApiStatusOut(
            service="Crossref API",
            configured=bool(settings.CROSSREF_EMAIL),
            details=f"Polite pool email: {settings.CROSSREF_EMAIL or 'Not configured'}",
        ),
        ApiStatusOut(
            service="OpenAlex API",
            configured=bool(settings.OPENALEX_EMAIL),
            details=f"Contact email: {settings.OPENALEX_EMAIL or 'Not configured'}",
        ),
        ApiStatusOut(
            service="Semantic Scholar API",
            configured=bool(settings.SEMANTIC_SCHOLAR_API_KEY),
            details="API Key provided" if settings.SEMANTIC_SCHOLAR_API_KEY else "Public rate limits (no key)",
        ),
        ApiStatusOut(
            service="Scopus API (Elsevier)",
            configured=bool(settings.SCOPUS_API_KEY and settings.SCOPUS_API_KEY != "your_scopus_api_key_here"),
            details="Institutional API Key active" if (settings.SCOPUS_API_KEY and settings.SCOPUS_API_KEY != "your_scopus_api_key_here") else "Not configured (Manual verification enabled)",
        ),
        ApiStatusOut(
            service="Web of Science API (Clarivate)",
            configured=bool(settings.WOS_API_KEY and settings.WOS_API_KEY != "your_web_of_science_api_key_here"),
            details="Clarivate API Key active" if (settings.WOS_API_KEY and settings.WOS_API_KEY != "your_web_of_science_api_key_here") else "Not configured (Manual verification enabled)",
        ),
        ApiStatusOut(
            service="LLM Orchestration Provider",
            configured=bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY),
            details=f"Provider: {settings.LLM_PROVIDER} ({'API key loaded' if (settings.GEMINI_API_KEY or settings.OPENAI_API_KEY) else 'No API key set - fallback mode'})",
        ),
    ]

    return SystemOverviewOut(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        llm_provider=settings.LLM_PROVIDER,
        database_url_type=db_type,
        integrations=integrations,
    )


@router.post("/seed-demo", summary="Seed real institutional publication data from KLE Technological University")
def seed_demo_data(
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    """
    Populates official academic research publications from KLE Technological University
    Hubballi and Belagavi campuses.
    """
    from scripts.ingest_belagavi_data import run_unified_ingest
    run_unified_ingest()

    dept_count = db.query(Department).count()
    faculty_count = db.query(Faculty).count()
    pubs_count = db.query(Publication).count()

    return {
        "status": "success",
        "message": "Official institutional research data synchronized successfully for KLE Technological University.",
        "departments_count": dept_count,
        "faculty_count": faculty_count,
        "publications_count": pubs_count,
    }


@router.post("/clear-demo", summary="Clear all publication records and return to pristine empty state")
def clear_demo_data(
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    """Removes all publications, duplicate candidates, and temporary logs."""
    all_pubs = db.query(Publication).all()
    pub_ids = [p.id for p in all_pubs]

    if pub_ids:
        # Delete duplicate candidates
        db.query(DuplicateCandidate).delete(synchronize_session=False)

        # Delete dependent authors, sources, verifications
        db.query(PublicationAuthor).delete(synchronize_session=False)
        db.query(PublicationSource).delete(synchronize_session=False)
        db.query(PublicationVerification).delete(synchronize_session=False)

        # Delete publications
        db.query(Publication).delete(synchronize_session=False)

    db.commit()
    return {"status": "success", "message": f"Cleared {len(pub_ids)} publication records."}
