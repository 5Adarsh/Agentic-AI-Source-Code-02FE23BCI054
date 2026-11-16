"""
CitationSnapshot ORM model.
Point-in-time citation count captures per publication and faculty.
"""
import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CitationSource(str, enum.Enum):
    google_scholar = "google_scholar"
    crossref = "crossref"
    openalex = "openalex"
    semantic_scholar = "semantic_scholar"
    scopus = "scopus"
    wos = "wos"


class CitationSnapshot(Base):
    __tablename__ = "citation_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publications.id"), nullable=False
    )
    faculty_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=True
    )
    citation_count: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[CitationSource] = mapped_column(
        Enum(CitationSource, name="citation_source"), nullable=False
    )
    h_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    i10_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    publication = relationship("Publication", back_populates="citation_snapshots")
    faculty = relationship("Faculty", back_populates="citation_snapshots")

    def __repr__(self) -> str:
        return f"<CitationSnapshot pub={self.publication_id} date={self.snapshot_date} count={self.citation_count}>"
