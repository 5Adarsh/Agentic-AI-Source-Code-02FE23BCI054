"""
Pydantic schemas for Faculty and Department.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Department schemas ────────────────────────────────────────────────────────

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)


class DepartmentCreate(DepartmentBase):
    head_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    head_id: Optional[UUID] = None


class DepartmentOut(DepartmentBase):
    id: UUID
    head_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Faculty schemas ───────────────────────────────────────────────────────────

class FacultyBase(BaseModel):
    faculty_id: str = Field(..., min_length=1, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    department_id: Optional[UUID] = None
    designation: str = Field(..., min_length=1, max_length=255)


class FacultyCreate(FacultyBase):
    user_id: Optional[UUID] = None
    orcid: Optional[str] = None
    google_scholar_id: Optional[str] = None
    scopus_author_id: Optional[str] = None
    wos_researcher_id: Optional[str] = None


class FacultyUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department_id: Optional[UUID] = None
    designation: Optional[str] = None
    orcid: Optional[str] = None
    google_scholar_id: Optional[str] = None
    scopus_author_id: Optional[str] = None
    wos_researcher_id: Optional[str] = None
    is_active: Optional[bool] = None


class FacultyOut(FacultyBase):
    id: UUID
    user_id: UUID
    orcid: Optional[str]
    google_scholar_id: Optional[str]
    scopus_author_id: Optional[str]
    wos_researcher_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
