"""
Pydantic schemas for Agent execution and logs.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.agent import ExecutionStatus, LogLevel


class AgentTrigger(BaseModel):
    """Request body to trigger an agent pipeline."""
    agent_name: str
    input_data: Dict[str, Any] = {}


class AgentStatus(BaseModel):
    """Response schema for an agent execution record."""
    id: UUID
    agent_name: str
    status: ExecutionStatus
    triggered_by: Optional[UUID]
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]

    model_config = {"from_attributes": True}


class AgentLogOut(BaseModel):
    """Single structured log entry from an agent execution."""
    id: UUID
    execution_id: UUID
    level: LogLevel
    message: str
    metadata: Optional[Dict[str, Any]] = Field(None, alias="log_metadata")
    logged_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class AgentExecutionList(BaseModel):
    items: List[AgentStatus]
    total: int
    page: int
    page_size: int
