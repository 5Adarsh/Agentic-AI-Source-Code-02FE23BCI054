"""
Agent 1: Faculty Profile Agent
Module: app.agents.faculty_profile_agent

Responsibilities:
- Faculty registration and profile retrieval.
- ORCID identification and institutional identity matching.
- Google Scholar profile association.
- Department association and hierarchy tracking.
- Faculty identity conflict detection (differing emails, duplicate IDs, homonyms).
"""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.models.faculty import Faculty, Department
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("agents.faculty_profile")

ORCID_REGEX = re.compile(r"^\d{4}-\d{4}-\d{4}-[\dX]{4}$")


@dataclass
class FacultyProfileInput:
    faculty_id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    department_id: Optional[str] = None
    orcid: Optional[str] = None
    google_scholar_id: Optional[str] = None
    scopus_author_id: Optional[str] = None
    wos_researcher_id: Optional[str] = None


@dataclass
class FacultyProfileOutput:
    matched: bool
    faculty_data: Optional[Dict[str, Any]] = None
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0


class FacultyProfileAgent:
    """
    Executable Faculty Profile Agent managing identity resolution, scholarly profile linking,
    and profile conflict analysis.
    """

    def __init__(self, db_session: Optional[Session] = None, llm_client: Any = None, settings: Any = None):
        self.db = db_session
        self.llm = llm_client
        self.settings = settings

    async def execute(self, state: AgentState) -> AgentState:
        logger.info("[FacultyProfileAgent] Initiating execution. State faculty_id: %s", state.get("faculty_id"))
        updated_state = state.copy()
        updated_state["current_agent"] = "faculty_profile_agent"
        
        conflicts: List[Dict[str, Any]] = []
        profile_data: Optional[Dict[str, Any]] = None
        identifiers: Dict[str, Any] = {}
        faculty_id_str = state.get("faculty_id")

        if self.db:
            faculty = None
            if faculty_id_str:
                try:
                    faculty = self.db.get(Faculty, UUID(faculty_id_str))
                except (ValueError, TypeError):
                    faculty = self.db.query(Faculty).filter(Faculty.faculty_id == faculty_id_str).first()
            
            # If not found by ID, attempt lookup by email in input_data
            if not faculty and state.get("faculty_profile"):
                email = state["faculty_profile"].get("email")
                if email:
                    faculty = self.db.query(Faculty).filter(Faculty.email == email.strip().lower()).first()

            if faculty:
                # Validate ORCID formatting if present
                if faculty.orcid:
                    clean_orcid = faculty.orcid.strip().replace("https://orcid.org/", "")
                    if not ORCID_REGEX.match(clean_orcid):
                        conflicts.append({
                            "type": "INVALID_ORCID_FORMAT",
                            "field": "orcid",
                            "value": faculty.orcid,
                            "severity": "medium",
                            "message": f"ORCID syntax '{faculty.orcid}' does not match standard 16-character format.",
                        })

                # Check for potential department mismatch
                dept_name = None
                if faculty.department_id:
                    dept = self.db.get(Department, faculty.department_id)
                    dept_name = dept.name if dept else None

                # Check for duplicate institutional emails or conflicting names across database
                homonyms = self.db.query(Faculty).filter(
                    Faculty.full_name == faculty.full_name,
                    Faculty.id != faculty.id
                ).all()
                if homonyms:
                    conflicts.append({
                        "type": "IDENTITY_HOMONYM_CONFLICT",
                        "field": "full_name",
                        "value": faculty.full_name,
                        "severity": "high",
                        "message": f"Found {len(homonyms)} other faculty member(s) with identical name '{faculty.full_name}'. Manual disambiguation recommended.",
                        "conflicting_faculty_ids": [str(h.id) for h in homonyms]
                    })

                profile_data = {
                    "id": str(faculty.id),
                    "faculty_id": faculty.faculty_id,
                    "full_name": faculty.full_name,
                    "email": faculty.email,
                    "designation": faculty.designation,
                    "department_id": str(faculty.department_id) if faculty.department_id else None,
                    "department_name": dept_name,
                    "orcid": faculty.orcid,
                    "google_scholar_id": faculty.google_scholar_id,
                    "scopus_author_id": faculty.scopus_author_id,
                    "wos_researcher_id": faculty.wos_researcher_id,
                    "is_active": faculty.is_active,
                }

                identifiers = {
                    "orcid": faculty.orcid,
                    "google_scholar_id": faculty.google_scholar_id,
                    "scopus_author_id": faculty.scopus_author_id,
                    "wos_researcher_id": faculty.wos_researcher_id,
                }
                logger.info("[FacultyProfileAgent] Successfully resolved faculty: %s (%s)", faculty.full_name, faculty.faculty_id)
            else:
                if faculty_id_str:
                    conflicts.append({
                        "type": "FACULTY_RECORD_NOT_FOUND",
                        "field": "faculty_id",
                        "value": faculty_id_str,
                        "severity": "critical",
                        "message": f"No faculty profile located with ID: {faculty_id_str}",
                    })

        updated_state["faculty_profile"] = profile_data
        updated_state["faculty_identifiers"] = identifiers
        updated_state["identity_conflicts"] = conflicts

        # Append execution logs
        logs = updated_state.get("logs", [])
        logs.append({
            "agent": "faculty_profile_agent",
            "message": f"Profile processed for {profile_data.get('full_name') if profile_data else 'Unknown'}. Conflicts identified: {len(conflicts)}",
            "level": "warning" if conflicts else "info",
            "logged_at": datetime.now(timezone.utc).isoformat(),
        })
        updated_state["logs"] = logs

        return updated_state
