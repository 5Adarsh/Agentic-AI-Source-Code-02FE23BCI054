"""
Pydantic schemas for Publications.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.publication import PublicationStatus, PublicationStatus, PublicationType, SourceName


# ── Author schemas ────────────────────────────────────────────────────────────

class PublicationAuthorOut(BaseModel):
    id: UUID
    faculty_id: Optional[UUID]
    author_name: str
    author_order: int
    is_corresponding: bool

    model_config = {"from_attributes": True}


class PublicationAuthorCreate(BaseModel):
    faculty_id: Optional[UUID] = None
    author_name: str = Field(..., min_length=1, max_length=255)
    author_order: int = Field(..., ge=1)
    is_corresponding: bool = False


# ── Source schemas ────────────────────────────────────────────────────────────

class PublicationSourceOut(BaseModel):
    id: UUID
    source_name: SourceName
    source_id: Optional[str]
    source_url: Optional[str]
    is_primary: bool
    retrieved_at: datetime

    model_config = {"from_attributes": True}


# ── Publication schemas ───────────────────────────────────────────────────────

class PublicationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=1000)
    doi: Optional[str] = Field(None, max_length=255)
    abstract: Optional[str] = None
    publication_year: int = Field(..., ge=1900, le=2100)
    publication_type: PublicationType


class PublicationCreate(PublicationBase):
    authors: List[PublicationAuthorCreate] = []


class PublicationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=1000)
    doi: Optional[str] = None
    abstract: Optional[str] = None
    publication_year: Optional[int] = Field(None, ge=1900, le=2100)
    publication_type: Optional[PublicationType] = None
    status: Optional[PublicationStatus] = None
    total_citations: Optional[int] = Field(None, ge=0)


class PublicationVerificationBrief(BaseModel):
    scopus_verified: bool = False
    wos_verified: bool = False
    crossref_verified: bool = False
    openalex_verified: bool = False

    model_config = {"from_attributes": True}


class PublicationOut(PublicationBase):
    id: UUID
    status: PublicationStatus
    total_citations: int
    created_at: datetime
    updated_at: datetime
    authors: List[PublicationAuthorOut] = []
    sources: List[PublicationSourceOut] = []
    verification: Optional[PublicationVerificationBrief] = None

    model_config = {"from_attributes": True}


class PublicationImportRequest(BaseModel):
    """Trigger an agent-driven import for a faculty member."""
    faculty_id: UUID
    sources: List[SourceName] = [SourceName.google_scholar, SourceName.crossref]
    year_from: Optional[int] = None
    year_to: Optional[int] = None
