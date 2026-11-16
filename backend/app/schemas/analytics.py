"""
Pydantic schemas for citation analytics and metrics.
"""
from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.citation import CitationSource


class CitationMetrics(BaseModel):
    """Citation stats for a single publication across all tracked sources."""
    publication_id: UUID
    title: str
    doi: Optional[str]
    total_citations: int
    by_source: Dict[str, int]  # source_name -> count
    latest_snapshot_date: Optional[date]


class HIndexResult(BaseModel):
    """H-index and I10-index for a faculty member."""
    faculty_id: UUID
    full_name: str
    h_index: int
    i10_index: int
    total_citations: int
    total_publications: int
    source: CitationSource
    computed_at: date


class DepartmentStats(BaseModel):
    """Aggregated publication and citation statistics for a department."""
    department_id: UUID
    department_name: str
    total_faculty: int
    total_publications: int
    total_citations: int
    average_h_index: float
    publications_by_type: Dict[str, int]
    publications_by_year: Dict[int, int]
    top_cited_publications: List[CitationMetrics]


class InstitutionalSummary(BaseModel):
    """Institution-wide aggregated analytics."""
    total_departments: int
    total_faculty: int
    total_publications: int
    total_citations: int
    average_h_index: float
    department_breakdown: List[DepartmentStats]
    academic_year: Optional[str]
