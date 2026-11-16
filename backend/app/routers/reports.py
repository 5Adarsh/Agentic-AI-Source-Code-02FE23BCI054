"""
Reports router — NIRF/NAAC report generation, retrieval, and PDF/Excel/CSV exports.
"""
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_coordinator_or_admin, get_current_user
from app.models.publication import Publication
from app.models.report import Report, ReportStatus, ReportType
from app.schemas.report import NIRFReport, NAACReport, ReportCreate, ReportOut
from app.services.report_exporter import ReportExporter

router = APIRouter()


@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED, summary="Generate a report")
def create_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_coordinator_or_admin),
):
    # Calculate real-time database publication statistics for genuine report data
    total_pubs = db.query(Publication).count()
    verified_pubs = db.query(Publication).filter(Publication.status == "verified").count()
    pubs = db.query(Publication).all()
    total_cits = sum(p.total_citations or 0 for p in pubs)
    
    # Calculate h-index
    citations = sorted([p.total_citations or 0 for p in pubs], reverse=True)
    h_index = 0
    for idx, c in enumerate(citations, start=1):
        if c >= idx:
            h_index = idx
        else:
            break

    generated_metrics = {
        "total_publications": total_pubs,
        "verified_publications": verified_pubs,
        "total_citations": total_cits,
        "h_index": h_index,
        "academic_year": payload.academic_year or "2023-2024",
    }

    report = Report(
        report_type=payload.report_type,
        title=payload.title,
        parameters=payload.parameters or {},
        generated_data=generated_metrics,
        status=ReportStatus.completed,
        generated_by=current_user.id,
        academic_year=payload.academic_year,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.post("/nirf", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def generate_nirf_report(payload: ReportCreate, db: Session = Depends(get_db), user=Depends(get_coordinator_or_admin)):
    payload.report_type = ReportType.nirf
    return create_report(payload, db, user)


@router.post("/naac", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def generate_naac_report(payload: ReportCreate, db: Session = Depends(get_db), user=Depends(get_coordinator_or_admin)):
    payload.report_type = ReportType.naac
    return create_report(payload, db, user)


@router.get("/", response_model=List[ReportOut], summary="List reports")
def list_reports(
    report_type: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Report)
    if report_type:
        q = q.filter(Report.report_type == report_type)
    return q.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{report_id}", response_model=ReportOut, summary="Get report by ID")
def get_report(report_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report


@router.get("/{report_id}/download/pdf", summary="Download report as certified PDF")
def download_pdf(report_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    
    pubs = db.query(Publication).limit(50).all()
    pubs_data = [
        {
            "title": p.title,
            "authors": [a.author_name for a in p.authors],
            "publication_year": p.publication_year,
            "doi": p.doi,
            "total_citations": p.total_citations,
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
        }
        for p in pubs
    ]

    pdf_bytes = ReportExporter.generate_pdf_report(
        report_title=report.title,
        metrics=report.generated_data or {},
        publications=pubs_data,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="report_{report_id}.pdf"'},
    )


@router.get("/{report_id}/download/excel", summary="Download report as structured Excel workbook")
def download_excel(report_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    
    pubs = db.query(Publication).limit(100).all()
    pubs_data = [
        {
            "title": p.title,
            "authors": [a.author_name for a in p.authors],
            "publication_year": p.publication_year,
            "doi": p.doi,
            "total_citations": p.total_citations,
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
        }
        for p in pubs
    ]

    excel_bytes = ReportExporter.generate_excel_report(
        report_title=report.title,
        metrics=report.generated_data or {},
        publications=pubs_data,
    )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="report_{report_id}.xlsx"'},
    )
