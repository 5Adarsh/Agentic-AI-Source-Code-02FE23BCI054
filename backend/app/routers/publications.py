"""
Publications router — CRUD, Scholar CSV upload processing, and agent-driven import.
"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_coordinator_or_admin, get_current_user
from app.models.publication import Publication, PublicationAuthor, PublicationSource, PublicationType, SourceName
from app.models.faculty import Faculty
from app.schemas.publication import (
    PublicationCreate, PublicationImportRequest, PublicationOut, PublicationUpdate,
)
from app.agents.scholar_harvest_agent import ScholarHarvestAgent

router = APIRouter()


@router.get("/", response_model=List[PublicationOut], summary="List publications")
def list_publications(
    faculty_id: Optional[UUID] = None,
    year: Optional[int] = None,
    pub_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Publication)
    if year:
        q = q.filter(Publication.publication_year == year)
    if pub_type:
        q = q.filter(Publication.publication_type == pub_type)
    if status_filter:
        q = q.filter(Publication.status == status_filter)
    if faculty_id:
        q = q.join(Publication.authors).filter(PublicationAuthor.faculty_id == faculty_id)
    return q.order_by(Publication.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=PublicationOut, status_code=status.HTTP_201_CREATED)
def create_publication(
    payload: PublicationCreate,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    pub_data = payload.model_dump(exclude={"authors"})
    pub = Publication(**pub_data)
    db.add(pub)
    db.commit()
    db.refresh(pub)

    if payload.authors:
        for idx, author_in in enumerate(payload.authors, start=1):
            pa = PublicationAuthor(
                publication_id=pub.id,
                author_name=author_in.author_name,
                author_order=author_in.author_order or idx,
                is_corresponding=author_in.is_corresponding or False,
                faculty_id=author_in.faculty_id,
            )
            db.add(pa)
        db.commit()
        db.refresh(pub)

    return pub


@router.post("/import/scholar-csv", summary="Upload Scholar CSV and harvest records")
async def upload_scholar_csv(
    file: UploadFile = File(...),
    faculty_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_coordinator_or_admin),
):
    """
    Direct CSV upload endpoint for faculty Google Scholar publications.
    Executes ScholarHarvestAgent and saves harvested publications to database.
    """
    content_bytes = await file.read()
    csv_str = content_bytes.decode("utf-8", errors="replace")

    agent = ScholarHarvestAgent(db_session=db)
    state = {
        "scholar_csv_content": csv_str,
        "faculty_id": faculty_id,
        "harvested_publications": [],
        "logs": [],
        "errors": [],
    }

    result = await agent.execute(state)
    harvested = result.get("harvested_publications", [])
    
    saved_count = 0
    faculty_uuid = UUID(faculty_id) if faculty_id else None

    for item in harvested:
        doi = item.get("doi")
        existing = db.query(Publication).filter(Publication.doi == doi).first() if doi else None
        if not existing:
            pub = Publication(
                title=item.get("title", ""),
                doi=doi,
                publication_year=item.get("publication_year"),
                total_citations=item.get("total_citations", 0),
                publication_type=PublicationType.journal,
            )
            db.add(pub)
            db.flush()

            # Record source provenance
            ps = PublicationSource(
                publication_id=pub.id,
                source_name=SourceName.google_scholar,
                source_url=item.get("source_url"),
                raw_data=item.get("raw_data") or {},
                retrieved_at=datetime.now(timezone.utc),
                is_primary=True,
            )
            db.add(ps)

            # Record author entries
            for order, a_name in enumerate(item.get("authors", []), start=1):
                db.add(PublicationAuthor(
                    publication_id=pub.id,
                    author_name=a_name,
                    author_order=order,
                    faculty_id=faculty_uuid,
                ))
            saved_count += 1

    db.commit()

    return {
        "status": "success",
        "total_parsed": len(harvested),
        "saved_to_database": saved_count,
        "harvest_summary": result.get("harvest_summary"),
    }


@router.get("/{pub_id}", response_model=PublicationOut)
def get_publication(pub_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    pub = db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found.")
    return pub


@router.patch("/{pub_id}", response_model=PublicationOut)
def update_publication(
    pub_id: UUID,
    payload: PublicationUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    pub = db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(pub, k, v)
    db.commit()
    db.refresh(pub)
    return pub


@router.delete("/{pub_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_publication(
    pub_id: UUID,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    pub = db.get(Publication, pub_id)
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found.")
    db.delete(pub)
    db.commit()
