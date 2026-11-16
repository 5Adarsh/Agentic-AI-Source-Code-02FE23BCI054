"""Schemas package."""
from app.schemas.user import UserCreate, UserOut, UserUpdate, Token, TokenData  # noqa
from app.schemas.faculty import (  # noqa
    FacultyCreate, FacultyOut, FacultyUpdate,
    DepartmentCreate, DepartmentOut, DepartmentUpdate,
)
from app.schemas.publication import PublicationCreate, PublicationOut, PublicationUpdate  # noqa
from app.schemas.agent import AgentTrigger, AgentStatus, AgentLogOut  # noqa
from app.schemas.analytics import CitationMetrics, HIndexResult, DepartmentStats  # noqa
from app.schemas.report import ReportCreate, ReportOut, NIRFReport, NAACReport  # noqa
