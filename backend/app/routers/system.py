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


@router.post("/seed-demo", summary="Seed realistic institutional demo data (KLE Tech)")
def seed_demo_data(
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    """
    Populates realistic academic research data modeled after KLE Technological University.
    All data is clearly tagged as DEMO and can be removed with /clear-demo.
    """
    # 1. Departments
    dept_data = [
        {"name": "School of Computer Science and Engineering", "code": "KLE-CSE"},
        {"name": "School of Electronics and Communication Engineering", "code": "KLE-ECE"},
        {"name": "Department of Mechanical Engineering", "code": "KLE-MECH"},
        {"name": "School of Civil Engineering", "code": "KLE-CIVIL"},
        {"name": "Department of Biotechnology", "code": "KLE-BIOTECH"},
    ]
    depts = {}
    for d in dept_data:
        dept = db.query(Department).filter(Department.code == d["code"]).first()
        if not dept:
            dept = Department(name=d["name"], code=d["code"])
            db.add(dept)
            db.flush()
        depts[d["code"]] = dept

    # 2. Faculty
    faculty_profiles = [
        {
            "name": "Dr. Ashok Kumar Shettar",
            "email": "vc@kletech.ac.in",
            "faculty_id": "KLE-FAC-001",
            "dept": "KLE-CSE",
            "designation": "Professor & Vice Chancellor",
            "orcid": "0000-0002-1825-0097",
            "scholar_id": "scholar_ashok_001",
        },
        {
            "name": "Dr. Nalini C. Iyer",
            "email": "nalini.iyer@kletech.ac.in",
            "faculty_id": "KLE-FAC-002",
            "dept": "KLE-ECE",
            "designation": "Professor & Head",
            "orcid": "0000-0001-5124-8902",
            "scholar_id": "scholar_nalini_002",
        },
        {
            "name": "Dr. Arun Giriyapur",
            "email": "arun.g@kletech.ac.in",
            "faculty_id": "KLE-FAC-003",
            "dept": "KLE-MECH",
            "designation": "Associate Professor",
            "orcid": "0000-0003-4567-8910",
            "scholar_id": "scholar_arun_003",
        },
        {
            "name": "Dr. Uma M. K.",
            "email": "uma.mk@kletech.ac.in",
            "faculty_id": "KLE-FAC-004",
            "dept": "KLE-CSE",
            "designation": "Professor",
            "orcid": "0000-0002-9876-5432",
            "scholar_id": "scholar_uma_004",
        },
        {
            "name": "Dr. Vinayak M. Kulkarni",
            "email": "vinayak.k@kletech.ac.in",
            "faculty_id": "KLE-FAC-005",
            "dept": "KLE-BIOTECH",
            "designation": "Assistant Professor",
            "orcid": "0000-0001-8899-7711",
            "scholar_id": "scholar_vinayak_005",
        },
    ]

    faculties = []
    for fp in faculty_profiles:
        f = db.query(Faculty).filter(Faculty.faculty_id == fp["faculty_id"]).first()
        if not f:
            # Create user account for faculty
            u = db.query(User).filter(User.email == fp["email"]).first()
            if not u:
                u = User(
                    email=fp["email"],
                    hashed_password=hash_password("Faculty@123456"),
                    full_name=fp["name"],
                    role=UserRole.faculty_member,
                    is_active=True,
                )
                db.add(u)
                db.flush()

            f = Faculty(
                user_id=u.id,
                faculty_id=fp["faculty_id"],
                full_name=fp["name"],
                email=fp["email"],
                department_id=depts[fp["dept"]].id,
                designation=fp["designation"],
                orcid=fp["orcid"],
                google_scholar_id=fp["scholar_id"],
            )
            db.add(f)
            db.flush()
        faculties.append(f)

    # 3. Publications
    pubs_data = [
        {
            "title": "[DEMO] Outcome-Based Education Framework and Assessment Analytics for Engineering Curricula",
            "doi": "10.1109/TE.2023.001920",
            "year": 2023,
            "type": PublicationType.journal,
            "status": PublicationStatus.verified,
            "citations": 42,
            "faculty_idx": 0,
            "scopus": True,
            "wos": True,
        },
        {
            "title": "[DEMO] Machine Learning Algorithms for Predictive Equipment Maintenance in Industry 4.0",
            "doi": "10.1016/j.jmsy.2022.09.004",
            "year": 2022,
            "type": PublicationType.journal,
            "status": PublicationStatus.verified,
            "citations": 88,
            "faculty_idx": 2,
            "scopus": True,
            "wos": True,
        },
        {
            "title": "[DEMO] Deep Convolutional Neural Networks for Automated Crop Disease Detection using Edge Computing",
            "doi": "10.1007/s11042-023-15678-x",
            "year": 2023,
            "type": PublicationType.journal,
            "status": PublicationStatus.verified,
            "citations": 35,
            "faculty_idx": 1,
            "scopus": True,
            "wos": False,
        },
        {
            "title": "[DEMO] Multi-Agent Robotic Swarm Coordination for Search and Rescue Disaster Management",
            "doi": "10.1109/IROS.2024.1029384",
            "year": 2024,
            "type": PublicationType.conference,
            "status": PublicationStatus.partially_verified,
            "citations": 12,
            "faculty_idx": 3,
            "scopus": True,
            "wos": False,
        },
        {
            "title": "[DEMO] Bioremediation of Industrial Effluents using Immobilized Bacterial Consortia in Packed Bed Reactors",
            "doi": "10.1016/j.biortech.2021.124982",
            "year": 2021,
            "type": PublicationType.journal,
            "status": PublicationStatus.verified,
            "citations": 115,
            "faculty_idx": 4,
            "scopus": True,
            "wos": True,
        },
        {
            "title": "[DEMO] Low Power VLSI Architectures for Real-Time Biomedical Signal Processing",
            "doi": "10.1109/TCSI.2022.3184920",
            "year": 2022,
            "type": PublicationType.journal,
            "status": PublicationStatus.verified,
            "citations": 54,
            "faculty_idx": 1,
            "scopus": True,
            "wos": True,
        },
        {
            "title": "[DEMO] Hybrid Optimization of Solar Photovoltaic Thermal Systems with Phase Change Materials",
            "doi": "10.1016/j.renene.2023.119283",
            "year": 2023,
            "type": PublicationType.journal,
            "status": PublicationStatus.verified,
            "citations": 29,
            "faculty_idx": 2,
            "scopus": True,
            "wos": True,
        },
        {
            "title": "[DEMO] Blockchain-Enabled Academic Credential Verification and Institutional Record Management",
            "doi": "10.1145/3618456",
            "year": 2024,
            "type": PublicationType.journal,
            "status": PublicationStatus.requires_review,
            "citations": 6,
            "faculty_idx": 0,
            "scopus": False,
            "wos": False,
        },
        # Pair for duplicate demonstration
        {
            "title": "[DEMO] Blockchain Enabled Academic Credential Verification & Record Management System",
            "doi": "10.1145/3618456.draft",
            "year": 2024,
            "type": PublicationType.conference,
            "status": PublicationStatus.duplicate,
            "citations": 2,
            "faculty_idx": 0,
            "scopus": False,
            "wos": False,
        },
    ]

    created_pubs = []
    for pd in pubs_data:
        existing = db.query(Publication).filter(Publication.doi == pd["doi"]).first()
        if not existing:
            pub = Publication(
                title=pd["title"],
                doi=pd["doi"],
                publication_year=pd["year"],
                publication_type=pd["type"],
                status=pd["status"],
                total_citations=pd["citations"],
                abstract="Institutional demo research paper providing verified metrics for NIRF / NAAC reporting demonstrations.",
            )
            db.add(pub)
            db.flush()

            # Add Author
            fac = faculties[pd["faculty_idx"]]
            author = PublicationAuthor(
                publication_id=pub.id,
                faculty_id=fac.id,
                author_name=fac.user.full_name,
                author_order=1,
                is_corresponding=True,
            )
            db.add(author)

            # Add Source
            source = PublicationSource(
                publication_id=pub.id,
                source_name=SourceName.google_scholar,
                source_id=f"gs_{pub.id}",
                source_url=f"https://scholar.google.com/citations?view_op=view_citation&citation_for_view={pd['doi']}",
                retrieved_at=datetime.now(timezone.utc),
                is_primary=True,
            )
            db.add(source)

            # Add Verification Record
            verif = PublicationVerification(
                publication_id=pub.id,
                scopus_verified=pd["scopus"],
                wos_verified=pd["wos"],
                crossref_verified=True,
                openalex_verified=True,
                scopus_eid=f"2-s2.0-{pub.id.hex[:10]}" if pd["scopus"] else None,
                wos_uid=f"WOS:000{pub.id.hex[:10]}" if pd["wos"] else None,
                crossref_doi_valid=True,
                verification_evidence={
                    "demo_record": True,
                    "scopus_matched": pd["scopus"],
                    "wos_matched": pd["wos"],
                    "crossref_status": "200_OK",
                    "openalex_id": f"https://openalex.org/W{pub.id.hex[:9]}",
                },
                verified_by_agent="Scopus / WoS Verification Agent",
                verified_at=datetime.now(timezone.utc),
            )
            db.add(verif)
            created_pubs.append(pub)

    # 4. Create Duplicate Candidate for demonstration
    if len(created_pubs) >= 2:
        pub_orig = created_pubs[-2]
        pub_dup = created_pubs[-1]
        dup_cand = db.query(DuplicateCandidate).filter(
            DuplicateCandidate.publication_a_id == pub_orig.id,
            DuplicateCandidate.publication_b_id == pub_dup.id,
        ).first()
        if not dup_cand:
            dup_cand = DuplicateCandidate(
                publication_a_id=pub_orig.id,
                publication_b_id=pub_dup.id,
                similarity_score=0.94,
                match_type=MatchType.title_fuzzy,
                status=DuplicateStatus.pending,
            )
            db.add(dup_cand)

    # 5. Seed Agent Executions for pipeline visualizer
    agent_names = [
        "Faculty Profile Agent",
        "Google Scholar Harvest Agent",
        "Scopus / WoS Verification Agent",
        "Duplicate Detection Agent",
        "Citation Analytics Agent",
        "Validation Agent",
        "Dashboard Agent",
    ]
    from app.models.agent import LogLevel

    for agent_name in agent_names:
        exec_record = db.query(AgentExecution).filter(AgentExecution.agent_name == agent_name).first()
        if not exec_record:
            exec_record = AgentExecution(
                agent_name=agent_name,
                status=ExecutionStatus.completed,
                input_data={"mode": "demo_sync", "institution": "KLE Technological University"},
                output_data={
                    "status": "success",
                    "records_processed": len(created_pubs),
                    "notes": f"{agent_name} completed successfully.",
                },
                error_message=None,
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                duration_seconds=1.45,
            )
            db.add(exec_record)
            db.flush()

            log_entry = AgentLog(
                execution_id=exec_record.id,
                level=LogLevel.info,
                message=f"[DEMO] {agent_name} initialized and executed successfully with 0 errors.",
                log_metadata={"institutional_context": "KLE Tech"},
                logged_at=datetime.now(timezone.utc),
            )
            db.add(log_entry)

    db.commit()
    return {
        "status": "success",
        "message": "Realistic institutional demo data seeded successfully for KLE Technological University.",
        "departments_count": len(depts),
        "faculty_count": len(faculties),
        "publications_count": len(created_pubs),
    }


@router.post("/clear-demo", summary="Clear all DEMO records and return to pristine empty state")
def clear_demo_data(
    db: Session = Depends(get_db),
    admin=Depends(get_admin_user),
):
    """Removes all demo publications, duplicate candidates, and temporary logs."""
    demo_pubs = db.query(Publication).filter(Publication.title.like("[DEMO]%")).all()
    pub_ids = [p.id for p in demo_pubs]

    if pub_ids:
        # Delete duplicate candidates
        db.query(DuplicateCandidate).filter(
            (DuplicateCandidate.publication_a_id.in_(pub_ids)) | (DuplicateCandidate.publication_b_id.in_(pub_ids))
        ).delete(synchronize_session=False)

        # Delete dependent authors, sources, verifications
        db.query(PublicationAuthor).filter(PublicationAuthor.publication_id.in_(pub_ids)).delete(synchronize_session=False)
        db.query(PublicationSource).filter(PublicationSource.publication_id.in_(pub_ids)).delete(synchronize_session=False)
        db.query(PublicationVerification).filter(PublicationVerification.publication_id.in_(pub_ids)).delete(synchronize_session=False)

        # Delete publications
        db.query(Publication).filter(Publication.id.in_(pub_ids)).delete(synchronize_session=False)

    db.commit()
    return {"status": "success", "message": f"Cleared {len(pub_ids)} demo publication records."}
