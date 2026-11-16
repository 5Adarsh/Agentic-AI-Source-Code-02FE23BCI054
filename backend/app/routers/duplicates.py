"""
Duplicates router — duplicate review, approval, and merging endpoints.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_coordinator_or_admin, get_current_user
from app.models.duplicate import DuplicateCandidate, DuplicateStatus
from app.models.publication import Publication

router = APIRouter()


class DuplicatePubAuthorOut(BaseModel):
    author_name: str
    author_order: int
    is_corresponding: bool = False

    model_config = {"from_attributes": True}


class DuplicatePubBrief(BaseModel):
    id: UUID
    title: str
    doi: Optional[str] = None
    publication_year: int
    publication_type: str
    total_citations: int = 0
    status: str
    authors: List[DuplicatePubAuthorOut] = []

    model_config = {"from_attributes": True}


class DuplicateCandidateOut(BaseModel):
    id: UUID
    publication_a_id: UUID
    publication_b_id: UUID
    similarity_score: float
    match_type: str
    status: DuplicateStatus
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    publication_a: Optional[DuplicatePubBrief] = None
    publication_b: Optional[DuplicatePubBrief] = None

    model_config = {"from_attributes": True}


class DuplicateActionPayload(BaseModel):
    action: str  # "approve" (merge) or "reject" (not duplicate)
    canonical_id: UUID | None = None


@router.get("/", response_model=List[DuplicateCandidateOut], summary="List duplicate candidates")
def list_duplicates(
    status_filter: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(DuplicateCandidate).options(
        joinedload(DuplicateCandidate.publication_a),
        joinedload(DuplicateCandidate.publication_b),
    )
    if status_filter:
        q = q.filter(DuplicateCandidate.status == status_filter)
    return q.order_by(DuplicateCandidate.similarity_score.desc()).offset(skip).limit(limit).all()


@router.post("/{candidate_id}/resolve", summary="Approve or reject duplicate candidate")
def resolve_duplicate(
    candidate_id: UUID,
    payload: DuplicateActionPayload,
    db: Session = Depends(get_db),
    current_user=Depends(get_coordinator_or_admin),
):
    candidate = db.get(DuplicateCandidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Duplicate candidate not found.")

    if payload.action == "approve":
        candidate.status = DuplicateStatus.confirmed_duplicate
        candidate.reviewed_by = current_user.id
        candidate.reviewed_at = datetime.now(timezone.utc)
        
        # Mark publication B as duplicate of publication A
        pub_b = db.get(Publication, candidate.publication_b_id)
        if pub_b:
            pub_b.status = "duplicate"
        
        db.commit()
        return {"status": "merged", "candidate_id": str(candidate_id)}

    elif payload.action == "reject":
        candidate.status = DuplicateStatus.not_duplicate
        candidate.reviewed_by = current_user.id
        candidate.reviewed_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "rejected", "candidate_id": str(candidate_id)}

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")
