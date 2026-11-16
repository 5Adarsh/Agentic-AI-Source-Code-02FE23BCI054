"""
Report ORM model.
Generated NIRF, NAAC, faculty, department, and institutional reports.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReportType(str, enum.Enum):
    nirf = "nirf"
    naac = "naac"
    faculty = "faculty"
    department = "department"
    institutional = "institutional"


class ReportStatus(str, enum.Enum):
    generating = "generating"
    completed = "completed"
    failed = "failed"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, name="report_type"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    generated_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, name="report_status"),
        nullable=False,
        default=ReportStatus.generating,
    )
    generated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    academic_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    generated_by_user = relationship("User", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report id={self.id} type={self.report_type} status={self.status}>"
