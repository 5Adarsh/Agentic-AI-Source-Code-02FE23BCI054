"""
PublicationVerification ORM model.
Tracks cross-database verification status for each publication.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PublicationVerification(Base):
    __tablename__ = "publication_verification"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    publication_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("publications.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    scopus_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    wos_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    crossref_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    openalex_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scopus_eid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wos_uid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crossref_doi_valid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    publication = relationship("Publication", back_populates="verification")

    def __repr__(self) -> str:
        return f"<PublicationVerification pub={self.publication_id}>"
