"""
DuplicateCandidate ORM model.
Pairs of publications flagged as potential duplicates with similarity scores.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MatchType(str, enum.Enum):
    exact_doi = "exact_doi"
    title_fuzzy = "title_fuzzy"
    embedding = "embedding"
    author_year = "author_year"


class DuplicateStatus(str, enum.Enum):
    pending = "pending"
    confirmed_duplicate = "confirmed_duplicate"
    not_duplicate = "not_duplicate"
    needs_review = "needs_review"


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publications.id"), nullable=False
    )
    publication_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("publications.id"), nullable=False
    )
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_type: Mapped[MatchType] = mapped_column(
        Enum(MatchType, name="match_type"), nullable=False
    )
    status: Mapped[DuplicateStatus] = mapped_column(
        Enum(DuplicateStatus, name="duplicate_status"),
        nullable=False,
        default=DuplicateStatus.pending,
    )
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    publication_a = relationship(
        "Publication", foreign_keys=[publication_a_id], back_populates="duplicate_a"
    )
    publication_b = relationship(
        "Publication", foreign_keys=[publication_b_id], back_populates="duplicate_b"
    )
    reviewer = relationship("User", back_populates="reviewed_duplicates")

    def __repr__(self) -> str:
        return f"<DuplicateCandidate a={self.publication_a_id} b={self.publication_b_id} score={self.similarity_score:.2f}>"
