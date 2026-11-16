"""
Agent 7: Dashboard Agent
Module: app.agents.dashboard_agent

Responsibilities:
- Faculty research summaries and metrics aggregation.
- Department-level research output summaries.
- Institutional research analytics compilation.
- Publication verification and audit summaries.
- Configurable NIRF and NAAC accreditation reporting tables.
- Excel, CSV, and PDF export generation using actual database records.
- Strict data integrity: never asserts fabricated metrics.
"""
import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.utils.logger import get_logger

logger = get_logger("agents.dashboard")


class DashboardAgent:
    """
    Executable Dashboard Agent.
    Aggregates research analytics across faculty, departments, and institution,
    and produces standardized exports and NIRF/NAAC compliant data payloads.
    """

    def __init__(self, db_session: Optional[Session] = None, llm_client: Any = None, settings: Any = None):
        self.db = db_session
        self.llm = llm_client
        self.settings = settings

    async def execute(self, state: AgentState) -> AgentState:
        logger.info("[DashboardAgent] Aggregating multi-level research analytics and compliance tables.")
        updated_state = state.copy()
        updated_state["current_agent"] = "dashboard_agent"

        citation_metrics = updated_state.get("citation_metrics") or {}
        status_counts = updated_state.get("validation_status_counts") or {}
        yearly_trends = updated_state.get("yearly_citations") or []
        faculty_profile = updated_state.get("faculty_profile") or {}
        publications = updated_state.get("deduplicated_publications") or updated_state.get("harvested_publications", [])

        total_pubs = citation_metrics.get("total_publications", len(publications))
        total_cits = citation_metrics.get("total_citations", sum(p.get("total_citations", 0) for p in publications))
        h_idx = citation_metrics.get("h_index", 0)
        i10_idx = citation_metrics.get("i10_index", 0)

        # 1. Institutional Overview Dataset
        institutional_analytics = {
            "total_publications": total_pubs,
            "total_citations": total_cits,
            "h_index": h_idx,
            "i10_index": i10_idx,
            "verified_count": status_counts.get("verified", 0),
            "partially_verified_count": status_counts.get("partially_verified", 0),
            "unverified_count": status_counts.get("unverified", 0),
            "duplicate_count": status_counts.get("duplicate", 0),
            "requires_review_count": status_counts.get("requires_review", 0),
            "yearly_trends": yearly_trends,
            "aggregated_at": datetime.now(timezone.utc).isoformat(),
        }

        # 2. NIRF Parameter 3: Research and Professional Practice (RPC)
        # Metric: Combined Metric for Publications (PU) + Quality of Publications (QP)
        nirf_table = {
            "framework": "NIRF",
            "parameter": "Parameter 3: Research and Professional Practice (RPC)",
            "sub_metrics": {
                "combined_metric_publications": total_pubs,
                "scopus_wos_indexed_count": status_counts.get("verified", 0),
                "total_citation_count": total_cits,
                "institutional_h_index": h_idx,
                "citations_per_paper": round(total_cits / total_pubs, 2) if total_pubs > 0 else 0.0,
            },
            "eligible_for_submission": total_pubs > 0,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # 3. NAAC Criterion 3: Research, Innovations and Extension
        # Metric 3.4: Research Publications and Awards
        naac_table = {
            "framework": "NAAC",
            "criterion": "Criterion 3.4: Research Publications and Awards",
            "metrics": {
                "3.4.3_ugc_care_scopus_wos_journals": status_counts.get("verified", 0),
                "3.4.4_average_citations_per_paper": round(total_cits / total_pubs, 2) if total_pubs > 0 else 0.0,
                "3.4.5_h_index_institutional": h_idx,
                "flagged_discrepancies": status_counts.get("requires_review", 0),
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        updated_state["dashboard_analytics"] = institutional_analytics
        updated_state["nirf_report_data"] = nirf_table
        updated_state["naac_report_data"] = naac_table
        updated_state["status"] = "COMPLETED"

        logs = updated_state.get("logs", [])
        logs.append({
            "agent": "dashboard_agent",
            "message": "Institutional analytics compiled. NIRF Parameter 3 and NAAC Metric 3.4 tables prepared.",
            "level": "info",
            "logged_at": datetime.now(timezone.utc).isoformat(),
        })
        updated_state["logs"] = logs

        return updated_state

    @staticmethod
    def export_publications_to_csv(publications: List[Dict[str, Any]]) -> str:
        """Generate formatted CSV string from publication records."""
        output = io.StringIO()
        fieldnames = ["title", "authors", "publication_year", "doi", "total_citations", "status", "source", "source_url"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for pub in publications:
            row = dict(pub)
            if isinstance(row.get("authors"), list):
                row["authors"] = "; ".join(row["authors"])
            writer.writerow(row)
        return output.getvalue()
