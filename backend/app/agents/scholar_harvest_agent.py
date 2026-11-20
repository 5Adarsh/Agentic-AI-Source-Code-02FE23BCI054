"""
Agent 2: Google Scholar Harvest Agent
Module: app.agents.scholar_harvest_agent

Responsibilities:
- Supported Scholar data integration and CSV processing.
- Publication metadata extraction (title, authors, year, DOI, citations, source URL).
- Metadata normalization and cleaning (trimming, case normalization, author list splitting).
- Missing-field handling and source provenance recording with retrieval timestamps.
- Strictly adheres to authorized integration policies (no unauthorized web scraping).
"""
import csv
import io
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.integrations.crossref import CrossrefClient
from app.integrations.openalex import OpenAlexClient
from app.utils.logger import get_logger

logger = get_logger("agents.scholar_harvest")

DOI_REGEX = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")


class ScholarHarvestAgent:
    """
    Executable Google Scholar Harvest Agent.
    Ingests publications from faculty-provided Scholar CSV files and links external
    open identifiers via Crossref and OpenAlex.
    """

    def __init__(self, db_session: Optional[Session] = None, llm_client: Any = None, settings: Any = None):
        self.db = db_session
        self.llm = llm_client
        self.settings = settings
        self.crossref = CrossrefClient()
        self.openalex = OpenAlexClient()

    async def execute(self, state: AgentState) -> AgentState:
        logger.info("[ScholarHarvestAgent] Starting publication harvest.")
        updated_state = state.copy()
        updated_state["current_agent"] = "scholar_harvest_agent"

        existing_pubs: List[Dict[str, Any]] = list(updated_state.get("harvested_publications", []))
        newly_harvested: List[Dict[str, Any]] = []
        csv_content = state.get("scholar_csv_content")
        errors: List[Dict[str, Any]] = list(updated_state.get("errors", []))

        # Fallback to local real_google_scholar_export.csv if neither csv nor existing pubs are provided
        if not csv_content and not existing_pubs:
            for pth in ["real_google_scholar_export.csv", "../real_google_scholar_export.csv", "backend/scripts/belagavi_raw.csv"]:
                if os.path.exists(pth):
                    try:
                        with open(pth, "r", encoding="utf-8") as f:
                            csv_content = f.read()
                            logger.info("[ScholarHarvestAgent] Ingested fallback source from %s", pth)
                            break
                    except Exception:
                        pass

        # 1. Process Scholar CSV export if provided
        if csv_content:
            try:
                reader = csv.DictReader(io.StringIO(csv_content))
                row_count = 0
                for row in reader:
                    row_count += 1
                    # Extract fields handling common Google Scholar / generic bibliographic CSV headers
                    title = (
                        row.get("title")
                        or row.get("Title")
                        or row.get("publication_title")
                        or row.get("Article Title")
                        or ""
                    ).strip()

                    if not title:
                        continue

                    authors_raw = (
                        row.get("authors")
                        or row.get("Authors")
                        or row.get("author")
                        or row.get("Author")
                        or ""
                    ).strip()

                    # Handle author separation (comma or semicolon)
                    authors_list = []
                    if authors_raw:
                        sep = ";" if ";" in authors_raw else ","
                        authors_list = [a.strip() for a in authors_raw.split(sep) if a.strip()]

                    # Year extraction and sanitation
                    year_val = (
                        row.get("year")
                        or row.get("Year")
                        or row.get("publication_year")
                        or row.get("Publication date")
                        or row.get("Publication Date")
                        or row.get("publication_date")
                        or row.get("date")
                        or row.get("Date")
                        or None
                    )
                    pub_year = None
                    if year_val:
                        digits = re.findall(r"\b(19\d\d|20\d\d)\b", str(year_val))
                        if digits:
                            pub_year = int(digits[0])

                    # Citations
                    citations_raw = (
                        row.get("citations")
                        or row.get("Citations")
                        or row.get("Total citations")
                        or row.get("cited_by")
                        or 0
                    )
                    try:
                        total_citations = int(re.sub(r"[^\d]", "", str(citations_raw)) or 0)
                    except ValueError:
                        total_citations = 0

                    # Source link / URL
                    source_url = (
                        row.get("url")
                        or row.get("URL")
                        or row.get("link")
                        or row.get("Link")
                        or None
                    )

                    # Extract DOI if present in row or title
                    doi = row.get("doi") or row.get("DOI") or None
                    if not doi and source_url:
                        doi_match = DOI_REGEX.search(source_url)
                        if doi_match:
                            doi = doi_match.group(0)

                    newly_harvested.append({
                        "title": title,
                        "doi": doi.strip() if doi else None,
                        "authors": authors_list,
                        "publication_year": pub_year,
                        "total_citations": total_citations,
                        "source": "google_scholar",
                        "source_url": source_url,
                        "publication_type": "journal",
                        "raw_data": dict(row),
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    })
                logger.info("[ScholarHarvestAgent] Ingested %d publication rows from Scholar CSV", len(newly_harvested))
            except Exception as e:
                logger.error("[ScholarHarvestAgent] CSV parsing exception: %s", str(e))
                errors.append({"agent": "scholar_harvest_agent", "stage": "csv_parsing", "error": str(e)})

        # 2. Enrich with OpenAlex by ORCID if faculty profile has ORCID and no publications yet
        faculty_profile = updated_state.get("faculty_profile")
        if not newly_harvested and not existing_pubs and faculty_profile and faculty_profile.get("orcid"):
            orcid = faculty_profile["orcid"]
            logger.info("[ScholarHarvestAgent] Attempting open scholarly harvesting via OpenAlex for ORCID %s", orcid)
            try:
                openalex_works = await self.openalex.get_works_by_author_orcid(orcid, limit=20)
                if openalex_works:
                    newly_harvested.extend(openalex_works)
                    logger.info("[ScholarHarvestAgent] Retrieved %d works from OpenAlex", len(openalex_works))
            except Exception as e:
                logger.warning("[ScholarHarvestAgent] OpenAlex fallback harvest failed: %s", str(e))

        # Persist newly harvested items to DB if requested and database session exists
        if self.db and newly_harvested and state.get("persist_to_db", False):
            from app.models.publication import Publication, PublicationAuthor, PublicationType
            from app.models.verification import PublicationVerification
            faculty_id_val = updated_state.get("faculty_id")
            fac_uuid = None
            if faculty_id_val:
                try:
                    fac_uuid = UUID(str(faculty_id_val))
                except Exception:
                    pass

            for item in newly_harvested:
                doi = item.get("doi")
                title = item.get("title", "").strip()
                existing = None
                if doi:
                    existing = self.db.query(Publication).filter(Publication.doi == doi).first()
                if not existing and title:
                    existing = self.db.query(Publication).filter(Publication.title == title).first()

                if not existing and title:
                    pub_year = item.get("publication_year") or datetime.now(timezone.utc).year
                    new_pub = Publication(
                        title=title,
                        doi=doi,
                        publication_year=int(pub_year),
                        total_citations=item.get("total_citations", 0),
                        publication_type=PublicationType.journal,
                    )
                    self.db.add(new_pub)
                    self.db.flush()

                    if fac_uuid:
                        pa = PublicationAuthor(
                            publication_id=new_pub.id,
                            faculty_id=fac_uuid,
                            author_name=item.get("authors", ["Faculty Author"])[0] if item.get("authors") else "Faculty Author",
                            author_order=1,
                        )
                        self.db.add(pa)

                    pv = PublicationVerification(
                        publication_id=new_pub.id,
                        crossref_verified=False,
                        scopus_verified=False,
                        wos_verified=False,
                    )
                    self.db.add(pv)
            try:
                self.db.commit()
            except Exception as e:
                logger.error("[ScholarHarvestAgent] DB commit error: %s", str(e))
                self.db.rollback()

        all_publications = existing_pubs + newly_harvested
        updated_state["harvested_publications"] = all_publications
        updated_state["scholar_harvest_source"] = "scholar_csv" if csv_content else "scholarly_api"
        updated_state["harvest_summary"] = {
            "total_harvested": len(all_publications),
            "newly_added": len(newly_harvested),
            "source": updated_state["scholar_harvest_source"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        updated_state["errors"] = errors

        logs = updated_state.get("logs", [])
        logs.append({
            "agent": "scholar_harvest_agent",
            "message": f"Harvest completed with {len(all_publications)} total publications ({len(newly_harvested)} new).",
            "level": "info",
            "logged_at": datetime.now(timezone.utc).isoformat(),
        })
        updated_state["logs"] = logs

        return updated_state
