"""
Pydantic schemas for Reports (NIRF, NAAC, faculty, department, institutional).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.report import ReportStatus, ReportType


class ReportCreate(BaseModel):
    report_type: ReportType
    title: str
    parameters: Dict[str, Any] = {}
    academic_year: Optional[str] = None


class ReportOut(BaseModel):
    id: UUID
    report_type: ReportType
    title: str
    parameters: Dict[str, Any]
    generated_data: Dict[str, Any]
    status: ReportStatus
    generated_by: UUID
    academic_year: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── NIRF-specific schema ──────────────────────────────────────────────────────

class NIRFPublicationEntry(BaseModel):
    title: str
    journal_name: Optional[str]
    year: int
    doi: Optional[str]
    scopus_indexed: bool
    wos_indexed: bool
    citation_count: int
    authors: List[str]


class NIRFReport(BaseModel):
    """
    NIRF (National Institutional Ranking Framework) publication data.
    Maps to NIRF data template 3.4 — Research Publications.
    """
    academic_year: str
    institution_name: str
    total_publications: int
    scopus_indexed: int
    wos_indexed: int
    total_citations: int
    h_index: float
    publications: List[NIRFPublicationEntry]


# ── NAAC-specific schema ──────────────────────────────────────────────────────

class NAACCriterionEntry(BaseModel):
    criterion: str  # e.g. "3.4.3"
    description: str
    metric_value: Any
    supporting_data: List[Dict[str, Any]]


class NAACReport(BaseModel):
    """
    NAAC (National Assessment and Accreditation Council) research metrics.
    Covers Criterion 3 — Research, Innovations and Extension.
    """
    academic_year: str
    institution_name: str
    criteria: List[NAACCriterionEntry]
    summary: Dict[str, Any]
