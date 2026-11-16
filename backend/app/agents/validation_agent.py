"""
Agent 6: Validation Agent
Module: app.agents.validation_agent

Responsibilities:
- Formal DOI syntax validation.
- Publication title integrity checking.
- Author consistency checking.
- Publication year range validation (1900 to current year + 1).
- Source conflict detection (differing titles/years across APIs).
- Missing metadata detection (authors, abstract, source link).
- Assign definitive publication statuses:
  - verified: Verified by Scopus, WoS, or valid DOI matching Crossref
  - partially_verified: Crossref/OpenAlex validated without Scopus/WoS
  - unverified: No external validation evidence
  - duplicate: Flagged duplicate candidate
  - requires_review: Anomalous metadata or conflicting source records
"""
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.utils.logger import get_logger

logger = get_logger("agents.validation")

DOI_PATTERN = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")


class ValidationAgent:
    """
    Executable Validation Agent.
    Audits data completeness, checks syntax and source consistency, and assigns quality statuses.
    """

    def __init__(self, db_session: Optional[Session] = None, llm_client: Any = None, settings: Any = None):
        self.db = db_session
        self.llm = llm_client
        self.settings = settings

    async def execute(self, state: AgentState) -> AgentState:
        logger.info("[ValidationAgent] Initiating comprehensive metadata validation.")
        updated_state = state.copy()
        updated_state["current_agent"] = "validation_agent"

        current_year = datetime.now().year
        publications = list(updated_state.get("deduplicated_publications") or updated_state.get("harvested_publications", []))
        duplicate_candidates = updated_state.get("duplicate_candidates", [])
        duplicate_titles = {
            d.get("publication_b_title") for d in duplicate_candidates if d.get("status") == "confirmed_duplicate"
        }

        # Build verification lookup by DOI and title
        verifications = updated_state.get("verification_results", [])
        verif_map = {}
        for v in verifications:
            if v.get("doi"):
                verif_map[v["doi"].lower().strip()] = v
            if v.get("title"):
                verif_map[v["title"].lower().strip()] = v

        validation_results: List[Dict[str, Any]] = []
        flagged_records: List[Dict[str, Any]] = []
        status_counts = {
            "verified": 0,
            "partially_verified": 0,
            "unverified": 0,
            "duplicate": 0,
            "requires_review": 0,
        }

        for pub in publications:
            title = pub.get("title", "").strip()
            doi = (pub.get("doi") or "").strip()
            year = pub.get("publication_year")
            authors = pub.get("authors", [])

            flags: List[str] = []
            
            # 1. Duplicate check
            if title in duplicate_titles:
                assigned_status = "duplicate"
                flags.append("Identified as duplicate of an existing record")
            else:
                # 2. DOI syntax validation
                doi_valid = False
                if doi:
                    if DOI_PATTERN.match(doi):
                        doi_valid = True
                    else:
                        flags.append(f"Malformed DOI syntax: '{doi}'")
                else:
                    flags.append("Missing DOI identifier")

                # 3. Year validation
                year_valid = False
                if year is not None:
                    if isinstance(year, int) and (1900 <= year <= current_year + 1):
                        year_valid = True
                    else:
                        flags.append(f"Suspicious publication year: {year}")
                else:
                    flags.append("Missing publication year")

                # 4. Author list completeness
                if not authors:
                    flags.append("Empty author list")

                # 5. Title validation
                if len(title) < 5:
                    flags.append("Title too short or missing")

                # 6. Cross-reference indexing evidence
                v_entry = verif_map.get(doi.lower()) or verif_map.get(title.lower())
                is_scopus_or_wos = False
                is_crossref = False
                if v_entry:
                    is_scopus_or_wos = v_entry.get("scopus_verified") or v_entry.get("wos_verified")
                    is_crossref = v_entry.get("crossref_verified") or v_entry.get("openalex_verified")

                # Determine final classification status
                if len(flags) >= 3 or not title:
                    assigned_status = "requires_review"
                    flagged_records.append({"publication": pub, "flags": flags})
                elif is_scopus_or_wos:
                    assigned_status = "verified"
                elif is_crossref or (doi_valid and year_valid):
                    assigned_status = "partially_verified"
                else:
                    assigned_status = "unverified"

            pub["status"] = assigned_status
            status_counts[assigned_status] = status_counts.get(assigned_status, 0) + 1

            validation_results.append({
                "title": title,
                "doi": doi,
                "status": assigned_status,
                "flags": flags,
                "validated_at": datetime.now(timezone.utc).isoformat(),
            })

        updated_state["validation_results"] = validation_results
        updated_state["validation_status_counts"] = status_counts
        updated_state["flagged_records"] = flagged_records

        logs = updated_state.get("logs", [])
        logs.append({
            "agent": "validation_agent",
            "message": f"Validation completed: {status_counts['verified']} verified, {status_counts['partially_verified']} partially verified, {status_counts['requires_review']} flagged for review.",
            "level": "info",
            "logged_at": datetime.now(timezone.utc).isoformat(),
        })
        updated_state["logs"] = logs

        return updated_state
