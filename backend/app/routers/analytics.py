"""
Analytics router — real DB aggregations for institutional dashboard,
faculty metrics, citation trends, h-index, and department comparisons.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.duplicate import DuplicateCandidate, DuplicateStatus
from app.models.faculty import Department, Faculty
from app.models.publication import Publication, PublicationAuthor, PublicationStatus, PublicationType
from app.models.verification import PublicationVerification

router = APIRouter()


def _compute_h_index(citation_counts: List[int]) -> int:
    """Deterministic calculation of h-index."""
    sorted_citations = sorted(citation_counts, reverse=True)
    h = 0
    for i, c in enumerate(sorted_citations, start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def _compute_i10_index(citation_counts: List[int]) -> int:
    """Count of papers with at least 10 citations."""
    return sum(1 for c in citation_counts if c >= 10)


@router.get("/dashboard", summary="Dashboard institutional KPI metrics")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> Dict[str, Any]:
    total_faculty = db.query(Faculty).count()
    total_publications = db.query(Publication).count()
    total_citations = db.query(func.coalesce(func.sum(Publication.total_citations), 0)).scalar() or 0

    avg_citations = round(total_citations / total_publications, 2) if total_publications > 0 else 0.0

    # Institutional h-index
    citation_rows = db.query(Publication.total_citations).all()
    all_citations = [r[0] for r in citation_rows if r[0] is not None]
    inst_h_index = _compute_h_index(all_citations)
    inst_i10_index = _compute_i10_index(all_citations)

    # Verification stats
    verified_count = db.query(Publication).filter(Publication.status == PublicationStatus.verified).count()
    review_count = db.query(Publication).filter(
        (Publication.status == PublicationStatus.requires_review) |
        (Publication.status == PublicationStatus.unverified)
    ).count()

    duplicate_candidates = db.query(DuplicateCandidate).filter(
        DuplicateCandidate.status == DuplicateStatus.pending
    ).count()

    return {
        "total_faculty": total_faculty,
        "total_publications": total_publications,
        "total_citations": total_citations,
        "avg_citations_per_pub": avg_citations,
        "h_index": inst_h_index,
        "i10_index": inst_i10_index,
        "verified_publications": verified_count,
        "requires_review_publications": review_count,
        "duplicate_candidates": duplicate_candidates,
    }


@router.get("/publications-by-year", summary="Publication count grouped by year")
def get_publications_by_year(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(Publication.publication_year, func.count(Publication.id))
        .group_by(Publication.publication_year)
        .order_by(Publication.publication_year.asc())
        .all()
    )
    return [{"year": r[0], "count": r[1]} for r in rows if r[0] is not None]


@router.get("/citation-trends", summary="Total citations grouped by year")
def get_citation_trends(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(Publication.publication_year, func.coalesce(func.sum(Publication.total_citations), 0))
        .group_by(Publication.publication_year)
        .order_by(Publication.publication_year.asc())
        .all()
    )
    return [{"year": r[0], "citations": r[1]} for r in rows if r[0] is not None]


@router.get("/department-comparison", summary="Compare departments by publications, citations, and faculty")
def get_department_comparison(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    departments = db.query(Department).all()
    result = []

    for dept in departments:
        faculty_ids = [f.id for f in dept.faculty_members]
        if not faculty_ids:
            result.append({
                "department": dept.name,
                "code": dept.code,
                "faculty_count": 0,
                "publications": 0,
                "citations": 0,
            })
            continue

        # Find distinct publication IDs for this department's faculty
        pub_ids = (
            db.query(PublicationAuthor.publication_id)
            .filter(PublicationAuthor.faculty_id.in_(faculty_ids))
            .distinct()
            .all()
        )
        pub_id_list = [p[0] for p in pub_ids]

        if pub_id_list:
            total_cites = (
                db.query(func.coalesce(func.sum(Publication.total_citations), 0))
                .filter(Publication.id.in_(pub_id_list))
                .scalar()
                or 0
            )
        else:
            total_cites = 0

        result.append({
            "department": dept.name,
            "code": dept.code,
            "faculty_count": len(faculty_ids),
            "publications": len(pub_id_list),
            "citations": total_cites,
        })

    return result


@router.get("/h-index", summary="Institutional and per-faculty h-index distribution")
def get_h_index_breakdown(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> Dict[str, Any]:
    # All citations
    citation_rows = db.query(Publication.total_citations).all()
    all_citations = [r[0] for r in citation_rows if r[0] is not None]

    inst_h = _compute_h_index(all_citations)
    inst_i10 = _compute_i10_index(all_citations)

    # Per faculty h-index
    faculties = db.query(Faculty).all()
    faculty_metrics = []

    for f in faculties:
        pub_ids = (
            db.query(PublicationAuthor.publication_id)
            .filter(PublicationAuthor.faculty_id == f.id)
            .distinct()
            .all()
        )
        pid_list = [p[0] for p in pub_ids]
        if pid_list:
            f_cites = [
                r[0]
                for r in db.query(Publication.total_citations)
                .filter(Publication.id.in_(pid_list))
                .all()
                if r[0] is not None
            ]
        else:
            f_cites = []

        h = _compute_h_index(f_cites)
        i10 = _compute_i10_index(f_cites)
        total_c = sum(f_cites)

        faculty_metrics.append({
            "faculty_id": str(f.id),
            "faculty_name": f.user.full_name if f.user else f.full_name,
            "department": f.department.name if f.department else "Unassigned",
            "publications_count": len(pid_list),
            "total_citations": total_c,
            "h_index": h,
            "i10_index": i10,
        })

    return {
        "institutional_h_index": inst_h,
        "institutional_i10_index": inst_i10,
        "faculty_breakdown": faculty_metrics,
    }


@router.get("/publication-types", summary="Publication type distribution")
def get_publication_type_distribution(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(Publication.publication_type, func.count(Publication.id))
        .group_by(Publication.publication_type)
        .all()
    )
    return [{"type": str(r[0].value if hasattr(r[0], "value") else r[0]), "count": r[1]} for r in rows]


@router.get("/verification-distribution", summary="Distribution of publication verification statuses")
def get_verification_distribution(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> List[Dict[str, Any]]:
    rows = (
        db.query(Publication.status, func.count(Publication.id))
        .group_by(Publication.status)
        .all()
    )
    return [{"status": str(r[0].value if hasattr(r[0], "value") else r[0]), "count": r[1]} for r in rows]
