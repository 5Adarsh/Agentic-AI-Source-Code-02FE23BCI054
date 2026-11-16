"""
Publication, PublicationAuthor, and PublicationSource ORM models.
Includes pgvector Vector column for semantic duplicate detection.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

try:
    from pgvector.sqlalchemy import Vector
    _VECTOR_AVAILABLE = True
except ImportError:
    _VECTOR_AVAILABLE = False


class PublicationType(str, enum.Enum):
    journal = "journal"
    conference = "conference"
    book = "book"
    book_chapter = "book_chapter"
    thesis = "thesis"
    patent = "patent"
    other = "other"


class PublicationStatus(str, enum.Enum):
    verified = "verified"
    partially_verified = "partially_verified"
    unverified = "unverified"
    duplicate = "duplicate"
    requires_review = "requires_review"


class SourceName(str, enum.Enum):
    google_scholar = "google_scholar"
    crossref = "crossref"
    openalex = "openalex"
    semantic_scholar = "semantic_scholar"
    scopus = "scopus"
    wos = "wos"
    manual = "manual"


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True, index=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    publication_type: Mapped[PublicationType] = mapped_column(
        Enum(PublicationType, name="publication_type"), nullable=False
    )
    status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus, name="publication_status"),
        nullable=False,
        default=PublicationStatus.unverified,
    )
    total_citations: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    # pgvector embedding column (1536-dim for OpenAI/Gemini text-embedding-3-small)
    if _VECTOR_AVAILABLE:
        title_embedding: Mapped[list | None] = mapped_column(Vector(1536), nullable=True)

    # Relationships
    authors = relationship("PublicationAuthor", back_populates="publication", lazy="selectin")
    sources = relationship("PublicationSource", back_populates="publication", lazy="selectin")
    verification = relationship(
        "PublicationVerification", back_populates="publication", uselist=False
    )
    citation_snapshots = relationship("CitationSnapshot", back_populates="publication", lazy="dynamic")
    duplicate_a = relationship(
        "DuplicateCandidate",
        foreign_keys="DuplicateCandidate.publication_a_id",
        back_populates="publication_a",
        lazy="dynamic",
    )
    duplicate_b = relationship(
        "DuplicateCandidate",
        foreign_keys="DuplicateCandidate.publication_b_id",
        back_populates="publication_b",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Publication id={self.id} year={self.publication_year}>"


class PublicationAuthor(Base):
    __tablename__ = "publication_authors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publications.id", ondelete="CASCADE"), nullable=False
    )
    faculty_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty.id"), nullable=True
    )
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)
    author_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    publication = relationship("Publication", back_populates="authors")
    faculty = relationship("Faculty", back_populates="publication_authors")


class PublicationSource(Base):
    __tablename__ = "publication_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publications.id", ondelete="CASCADE"), nullable=False
    )
    source_name: Mapped[SourceName] = mapped_column(
        Enum(SourceName, name="source_name"), nullable=False
    )
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    publication = relationship("Publication", back_populates="sources")
