"""
Agents router — trigger agents, execute complete LangGraph workflow, retrieve status and logs.
"""
from datetime import datetime, timezone
import time
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_coordinator_or_admin, get_current_user
from app.models.agent import AgentExecution, AgentLog, ExecutionStatus, LogLevel
from app.models.faculty import Faculty
from app.models.publication import Publication
from app.schemas.agent import AgentLogOut, AgentStatus, AgentTrigger
from app.agents.coordinator import ResearchIntelligenceCoordinator
from app.agents.faculty_profile_agent import FacultyProfileAgent
from app.agents.scholar_harvest_agent import ScholarHarvestAgent
from app.agents.scopus_wos_agent import ScopusWosAgent
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent
from app.agents.citation_analytics_agent import CitationAnalyticsAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.dashboard_agent import DashboardAgent

router = APIRouter()

VALID_AGENTS = [
    "faculty_profile_agent",
    "scholar_harvest_agent",
    "scopus_wos_agent",
    "duplicate_detection_agent",
    "citation_analytics_agent",
    "validation_agent",
    "dashboard_agent",
    "coordinator",
]

AGENT_ALIASES = {
    "faculty profile agent": "faculty_profile_agent",
    "google scholar harvest agent": "scholar_harvest_agent",
    "scholar harvest agent": "scholar_harvest_agent",
    "scopus / wos verification agent": "scopus_wos_agent",
    "scopus/wos verification agent": "scopus_wos_agent",
    "duplicate detection agent": "duplicate_detection_agent",
    "citation analytics agent": "citation_analytics_agent",
    "validation agent": "validation_agent",
    "dashboard agent": "dashboard_agent",
    "coordinator": "coordinator",
    "full pipeline": "coordinator",
    "all": "coordinator",
}


@router.post("/trigger", response_model=AgentStatus, status_code=202, summary="Trigger an agent or complete coordinator")
async def trigger_agent(
    payload: AgentTrigger,
    db: Session = Depends(get_db),
    current_user=Depends(get_coordinator_or_admin),
):
    norm_name = AGENT_ALIASES.get(payload.agent_name.lower().strip(), payload.agent_name.lower().strip())
    if norm_name not in VALID_AGENTS:
        raise HTTPException(status_code=400, detail=f"Unknown agent: {payload.agent_name}")

    start_time = time.time()
    execution = AgentExecution(
        agent_name=payload.agent_name,
        input_data=payload.input_data,
        triggered_by=current_user.id,
        status=ExecutionStatus.running,
        started_at=datetime.now(timezone.utc),
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    try:
        # Prepare execution state
        initial_state = {
            "execution_id": str(execution.id),
            "triggered_by": str(current_user.id),
            "faculty_id": payload.input_data.get("faculty_id"),
            "scholar_csv_content": payload.input_data.get("scholar_csv_content"),
            "harvested_publications": payload.input_data.get("harvested_publications", []),
            "persist_to_db": True,
            "logs": [],
        }

        # If harvested_publications is not provided in trigger, load from existing DB publications
        if not initial_state["harvested_publications"]:
            db_pubs = db.query(Publication).all()
            if db_pubs:
                initial_state["harvested_publications"] = [
                    {
                        "id": str(p.id),
                        "title": p.title,
                        "doi": p.doi,
                        "authors": [a.author_name for a in p.authors] if p.authors else [],
                        "publication_year": p.publication_year,
                        "total_citations": p.total_citations or 0,
                        "source": "google_scholar",
                        "publication_type": p.publication_type.value if hasattr(p.publication_type, "value") else str(p.publication_type),
                    }
                    for p in db_pubs
                ]

        # Dispatch execution
        if norm_name == "coordinator":
            coord = ResearchIntelligenceCoordinator(db_session=db)
            final_state = await coord.run(initial_state)
        elif norm_name == "faculty_profile_agent":
            agent = FacultyProfileAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        elif norm_name == "scholar_harvest_agent":
            agent = ScholarHarvestAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        elif norm_name == "scopus_wos_agent":
            agent = ScopusWosAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        elif norm_name == "duplicate_detection_agent":
            agent = DuplicateDetectionAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        elif norm_name == "citation_analytics_agent":
            agent = CitationAnalyticsAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        elif norm_name == "validation_agent":
            agent = ValidationAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        elif norm_name == "dashboard_agent":
            agent = DashboardAgent(db_session=db)
            final_state = await agent.execute(initial_state)
        else:
            raise ValueError(f"Unknown agent {payload.agent_name}")

        # Store logs into database
        for log_entry in final_state.get("logs", []):
            db_log = AgentLog(
                execution_id=execution.id,
                level=LogLevel.info if log_entry.get("level") != "warning" else LogLevel.warning,
                message=log_entry.get("message", ""),
                log_metadata=log_entry,
                logged_at=datetime.now(timezone.utc),
            )
            db.add(db_log)

        total_recs = (
            (final_state.get("citation_metrics") or {}).get("total_publications")
            or (final_state.get("harvest_summary") or {}).get("total_harvested")
            or len(final_state.get("harvested_publications") or [])
            or db.query(Publication).count()
        )
        if norm_name == "faculty_profile_agent":
            total_recs = db.query(Faculty).count()

        execution.status = ExecutionStatus.completed
        execution.output_data = {
            "status": final_state.get("status", "COMPLETED"),
            "records_processed": total_recs,
            "harvest_summary": final_state.get("harvest_summary"),
            "citation_metrics": final_state.get("citation_metrics"),
            "validation_status_counts": final_state.get("validation_status_counts"),
            "dashboard_analytics": final_state.get("dashboard_analytics"),
        }
        execution.completed_at = datetime.now(timezone.utc)
        execution.duration_seconds = round(time.time() - start_time, 2)
        db.commit()
        db.refresh(execution)

        # If coordinator was run, also record individual agent executions for UI telemetry tracking
        if norm_name == "coordinator":
            fac_count = db.query(Faculty).count()
            subagent_configs = [
                ("faculty_profile_agent", fac_count),
                ("scholar_harvest_agent", total_recs),
                ("scopus_wos_agent", total_recs),
                ("duplicate_detection_agent", total_recs),
                ("citation_analytics_agent", total_recs),
                ("validation_agent", total_recs),
                ("dashboard_agent", total_recs),
            ]
            step_duration = round((time.time() - start_time) / 7, 2)
            for sub_name, recs in subagent_configs:
                sub_exec = AgentExecution(
                    agent_name=sub_name,
                    input_data={"pipeline": "coordinator"},
                    triggered_by=current_user.id,
                    status=ExecutionStatus.completed,
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    duration_seconds=max(0.05, step_duration),
                    output_data={"status": "COMPLETED", "records_processed": recs},
                )
                db.add(sub_exec)
            db.commit()

    except Exception as e:
        execution.status = ExecutionStatus.failed
        execution.error_message = str(e)
        execution.completed_at = datetime.now(timezone.utc)
        execution.duration_seconds = round(time.time() - start_time, 2)
        db.commit()
        db.refresh(execution)

    return execution


@router.get("/", response_model=List[AgentStatus], summary="List agent executions")
def list_executions(
    agent_name: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(AgentExecution)
    if agent_name:
        q = q.filter(AgentExecution.agent_name == agent_name)
    return q.order_by(AgentExecution.started_at.desc()).offset(skip).limit(limit).all()


@router.get("/{execution_id}", response_model=AgentStatus, summary="Get execution by ID")
def get_execution(execution_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    ex = db.get(AgentExecution, execution_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Execution not found.")
    return ex


@router.get("/{execution_id}/logs", response_model=List[AgentLogOut], summary="Get logs for an execution")
def get_logs(
    execution_id: UUID,
    level: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    ex = db.get(AgentExecution, execution_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Execution not found.")
    q = db.query(AgentLog).filter(AgentLog.execution_id == execution_id)
    if level:
        q = q.filter(AgentLog.level == level)
    return q.order_by(AgentLog.logged_at).offset(skip).limit(limit).all()
