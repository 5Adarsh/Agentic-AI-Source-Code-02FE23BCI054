"""
Verification router — verification evidence inspection and manual audit workflows.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_coordinator_or_admin, get_current_user
from app.models.publication import Publication
from app.models.verification import PublicationVerification

router = APIRouter()


class VerificationEvidenceIn(BaseModel):
    scopus_verified: bool = False
    wos_verified: bool = False
    notes: str
    evidence_url: str | None = None


class VerificationPubBrief(BaseModel):
    id: UUID
    title: str
    doi: Optional[str] = None
    publication_year: int
    status: str

    model_config = {"from_attributes": True}


class VerificationOut(BaseModel):
    id: UUID
    publication_id: UUID
    scopus_verified: bool
    wos_verified: bool
    crossref_verified: bool
    openalex_verified: bool
    scopus_eid: Optional[str] = None
    wos_uid: Optional[str] = None
    crossref_doi_valid: bool = False
    verification_evidence: Dict[str, Any] | None = None
    verified_at: datetime | None = None
    verified_by_agent: Optional[str] = None
    publication: Optional[VerificationPubBrief] = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[VerificationOut], summary="List all publication verifications")
def list_verifications(
    status_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(PublicationVerification).join(PublicationVerification.publication)
    if status_filter:
        q = q.filter(Publication.status == status_filter)
    return q.offset(skip).limit(limit).all()


@router.get("/{publication_id}", response_model=VerificationOut, summary="Get verification record for a publication")
def get_verification(publication_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    verif = db.query(PublicationVerification).filter(PublicationVerification.publication_id == publication_id).first()
    if not verif:
        raise HTTPException(status_code=404, detail="No verification record found for this publication.")
    return verif


@router.post("/{publication_id}/manual", response_model=VerificationOut, summary="Submit manual verification evidence")
def submit_manual_verification(
    publication_id: UUID,
    payload: VerificationEvidenceIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_coordinator_or_admin),
):
    pub = db.get(Publication, publication_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found.")

    verif = db.query(PublicationVerification).filter(PublicationVerification.publication_id == publication_id).first()
    if not verif:
        verif = PublicationVerification(
            publication_id=publication_id,
            scopus_verified=payload.scopus_verified,
            wos_verified=payload.wos_verified,
            verification_evidence={
                "manual_verification": True,
                "verified_by": str(current_user.id),
                "notes": payload.notes,
                "evidence_url": payload.evidence_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            verified_by_agent="manual_curator",
            verified_at=datetime.now(timezone.utc),
        )
        db.add(verif)
    else:
        verif.scopus_verified = payload.scopus_verified
        verif.wos_verified = payload.wos_verified
        verif.verification_evidence = {
            "manual_verification": True,
            "verified_by": str(current_user.id),
            "notes": payload.notes,
            "evidence_url": payload.evidence_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        verif.verified_at = datetime.now(timezone.utc)

    # Update publication status accordingly
    if payload.scopus_verified or payload.wos_verified:
        pub.status = "verified"
    else:
        pub.status = "partially_verified"

    db.commit()
    db.refresh(verif)
    return verif
