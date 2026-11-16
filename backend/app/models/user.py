"""
User ORM model.
Roles: admin | research_coordinator | faculty_member
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    research_coordinator = "research_coordinator"
    faculty_member = "faculty_member"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False, default=UserRole.faculty_member
    )
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
    faculty_profile = relationship("Faculty", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic")
    triggered_executions = relationship(
        "AgentExecution", back_populates="triggered_by_user", lazy="dynamic"
    )
    reports = relationship("Report", back_populates="generated_by_user", lazy="dynamic")
    reviewed_duplicates = relationship(
        "DuplicateCandidate", back_populates="reviewer", lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
