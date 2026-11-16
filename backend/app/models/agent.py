"""
AgentExecution and AgentLog ORM models.
Tracks every agent run with full I/O and structured logs.
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExecutionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class LogLevel(str, enum.Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus, name="execution_status"),
        nullable=False,
        default=ExecutionStatus.pending,
    )
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    triggered_by_user = relationship("User", back_populates="triggered_executions")
    logs = relationship("AgentLog", back_populates="execution", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AgentExecution id={self.id} agent={self.agent_name} status={self.status}>"


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    level: Mapped[LogLevel] = mapped_column(
        Enum(LogLevel, name="log_level"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    log_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    execution = relationship("AgentExecution", back_populates="logs")

    def __repr__(self) -> str:
        return f"<AgentLog exec={self.execution_id} level={self.level}>"
