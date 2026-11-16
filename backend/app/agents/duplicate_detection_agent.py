"""
Agent 4: Duplicate Detection Agent
Module: app.agents.duplicate_detection_agent

Responsibilities:
- Exact normalized DOI matching.
- Normalized title matching and Levenshtein string similarity.
- Author similarity and publication year comparison.
- Multi-tier confidence assignment:
  - Exact DOI / ratio >= 0.90 -> confirmed_duplicate (auto-merge candidate)
  - 0.70 <= ratio < 0.90 -> needs_review (routes to Human Approval Queue)
  - ratio < 0.70 -> not_duplicate
- Preserves duplicate history and pairwise candidate comparisons.
"""
from difflib import SequenceMatcher
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.utils.logger import get_logger

logger = get_logger("agents.duplicate_detection")


def normalize_title(title: str) -> str:
    """Normalize string by removing punctuation, extra whitespace, and converting to lowercase."""
    if not title:
        return ""
    cleaned = re.sub(r"[^\w\s]", "", title.lower())
    return " ".join(cleaned.split())


def compute_title_similarity(title_a: str, title_b: str) -> float:
    """Compute normalized sequence similarity ratio."""
    norm_a = normalize_title(title_a)
    norm_b = normalize_title(title_b)
    if not norm_a or not norm_b:
        return 0.0
    return SequenceMatcher(None, norm_a, norm_b).ratio()


def compare_author_lists(authors_a: List[str], authors_b: List[str]) -> float:
    """Compare overlap between two author lists."""
    if not authors_a or not authors_b:
        return 0.5  # Neutral if one is missing
    set_a = {a.split()[-1].lower() for a in authors_a if a.strip()}
    set_b = {b.split()[-1].lower() for b in authors_b if b.strip()}
    if not set_a or not set_b:
        return 0.5
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return len(intersection) / len(union)


class DuplicateDetectionAgent:
    """
    Executable Duplicate Detection Agent.
    Executes tiered duplicate checks across harvested publications and existing DB records.
    """

    def __init__(self, db_session: Optional[Session] = None, llm_client: Any = None, settings: Any = None):
        self.db = db_session
        self.llm = llm_client
        self.settings = settings

    async def execute(self, state: AgentState) -> AgentState:
        logger.info("[DuplicateDetectionAgent] Executing duplicate detection analysis.")
        updated_state = state.copy()
        updated_state["current_agent"] = "duplicate_detection_agent"

        publications = list(updated_state.get("harvested_publications", []))
        duplicate_candidates: List[Dict[str, Any]] = []
        review_queue: List[Dict[str, Any]] = []
        deduplicated: List[Dict[str, Any]] = []

        seen_dois: Dict[str, Dict[str, Any]] = {}
        seen_items: List[Dict[str, Any]] = []

        for pub in publications:
            doi = (pub.get("doi") or "").strip().lower()
            title = pub.get("title") or ""
            authors = pub.get("authors", [])
            year = pub.get("publication_year")

            is_duplicate = False

            # 1. Exact DOI check
            if doi and doi in seen_dois:
                is_duplicate = True
                canonical = seen_dois[doi]
                # Merge citation counts safely: max citation count preserved
                canonical["total_citations"] = max(canonical.get("total_citations", 0), pub.get("total_citations", 0))
                
                duplicate_candidates.append({
                    "publication_a_title": canonical.get("title"),
                    "publication_b_title": title,
                    "doi": doi,
                    "similarity_score": 1.0,
                    "match_type": "exact_doi",
                    "status": "confirmed_duplicate",
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                })
            else:
                # 2. Fuzzy Title & Author Comparison
                for canonical in seen_items:
                    sim = compute_title_similarity(title, canonical.get("title", ""))
                    author_sim = compare_author_lists(authors, canonical.get("authors", []))
                    same_year = (year == canonical.get("publication_year")) if (year and canonical.get("publication_year")) else True

                    # Weighted composite similarity
                    composite_score = (sim * 0.75) + (author_sim * 0.15) + (0.10 if same_year else 0.0)

                    if sim >= 0.90:
                        is_duplicate = True
                        canonical["total_citations"] = max(canonical.get("total_citations", 0), pub.get("total_citations", 0))
                        duplicate_candidates.append({
                            "publication_a_title": canonical.get("title"),
                            "publication_b_title": title,
                            "similarity_score": round(sim, 3),
                            "match_type": "title_fuzzy",
                            "status": "confirmed_duplicate",
                            "detected_at": datetime.now(timezone.utc).isoformat(),
                        })
                        break
                    elif sim >= 0.70:
                        # Uncertain candidate: enqueued for human coordinator approval
                        review_queue.append({
                            "candidate_a": canonical,
                            "candidate_b": pub,
                            "title_similarity": round(sim, 3),
                            "composite_score": round(composite_score, 3),
                            "match_type": "needs_review",
                            "status": "pending_approval",
                            "reason": f"Title similarity {round(sim*100, 1)}% requires human review.",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        })

            if not is_duplicate:
                if doi:
                    seen_dois[doi] = pub
                seen_items.append(pub)
                deduplicated.append(pub)

        updated_state["duplicate_candidates"] = duplicate_candidates
        updated_state["deduplicated_publications"] = deduplicated
        updated_state["review_queue"] = review_queue
        updated_state["human_review_required"] = len(review_queue) > 0

        logs = updated_state.get("logs", [])
        logs.append({
            "agent": "duplicate_detection_agent",
            "message": f"Deduplication complete: {len(publications)} records analyzed -> {len(deduplicated)} canonical, {len(duplicate_candidates)} confirmed duplicates, {len(review_queue)} routed to human review queue.",
            "level": "info",
            "logged_at": datetime.now(timezone.utc).isoformat(),
        })
        updated_state["logs"] = logs

        return updated_state
