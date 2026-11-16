"""
LangGraph State schema for the Research Intelligence & Publication Analytics multi-agent workflow.
"""
from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """
    Central shared state passed between all 7 LangGraph agent nodes.
    Each agent reads from and updates relevant slices of this state.
    """
    # Execution metadata
    execution_id: str
    triggered_by: Optional[str]
    current_agent: str
    status: str
    errors: List[Dict[str, Any]]
    logs: List[Dict[str, Any]]

    # 1. Faculty Profile Agent
    faculty_id: Optional[str]
    faculty_profile: Optional[Dict[str, Any]]
    faculty_identifiers: Optional[Dict[str, Any]]  # orcid, scholar_id, scopus_id, etc.
    identity_conflicts: List[Dict[str, Any]]

    # 2. Google Scholar Harvest Agent
    scholar_harvest_source: Optional[str]  # "api" or "csv"
    scholar_csv_content: Optional[str]
    harvested_publications: List[Dict[str, Any]]
    harvest_summary: Optional[Dict[str, Any]]

    # 3. Scopus / WoS Verification Agent
    verification_targets: List[Dict[str, Any]]
    verification_results: List[Dict[str, Any]]
    unverified_publications: List[Dict[str, Any]]

    # 4. Duplicate Detection Agent
    duplicate_candidates: List[Dict[str, Any]]
    deduplicated_publications: List[Dict[str, Any]]
    human_review_required: bool
    review_queue: List[Dict[str, Any]]

    # 5. Citation Analytics Agent
    citation_metrics: Optional[Dict[str, Any]]  # total_pubs, total_citations, h_index, i10_index
    yearly_citations: List[Dict[str, Any]]
    department_metrics: Optional[Dict[str, Any]]

    # 6. Validation Agent
    validation_results: List[Dict[str, Any]]
    validation_status_counts: Dict[str, int]
    flagged_records: List[Dict[str, Any]]

    # 7. Dashboard Agent
    dashboard_analytics: Optional[Dict[str, Any]]
    nirf_report_data: Optional[Dict[str, Any]]
    naac_report_data: Optional[Dict[str, Any]]
    export_payload: Optional[Dict[str, Any]]
