"""
Faculty and Department ORM models.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    # head_id resolved after Faculty is created — nullable initially
    head_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("faculty.id", use_alter=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    head = relationship("Faculty", foreign_keys=[head_id], post_update=True)
    faculty_members = relationship(
        "Faculty",
        back_populates="department",
        foreign_keys="Faculty.department_id",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<Department id={self.id} code={self.code}>"


class Faculty(Base):
    __tablename__ = "faculty"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    faculty_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
    )
    orcid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    google_scholar_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scopus_author_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    wos_researcher_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    designation: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="faculty_profile")
    department = relationship(
        "Department",
        back_populates="faculty_members",
        foreign_keys=[department_id],
    )
    publication_authors = relationship("PublicationAuthor", back_populates="faculty", lazy="dynamic")
    citation_snapshots = relationship("CitationSnapshot", back_populates="faculty", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Faculty id={self.id} faculty_id={self.faculty_id}>"
