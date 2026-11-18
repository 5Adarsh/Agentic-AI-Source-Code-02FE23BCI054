"""
Faculty router — faculty profile endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_coordinator_or_admin, get_current_user
from app.models.faculty import Department, Faculty
from app.models.publication import Publication, PublicationAuthor
from app.schemas.faculty import (
    DepartmentCreate, DepartmentOut, DepartmentUpdate,
    FacultyCreate, FacultyOut, FacultyUpdate,
)
from app.schemas.publication import PublicationOut

router = APIRouter()


# ── Department endpoints ──────────────────────────────────────────────────────

@router.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return db.query(Department).offset(skip).limit(limit).all()


@router.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    dept = Department(**payload.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/departments/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    dept = db.get(Department, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    return dept


@router.patch("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: UUID,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    dept = db.get(Department, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


# ── Faculty endpoints ─────────────────────────────────────────────────────────

@router.get("/", response_model=List[FacultyOut])
def list_faculty(
    department_id: UUID | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    q = db.query(Faculty)
    if department_id:
        q = q.filter(Faculty.department_id == department_id)
    return q.offset(skip).limit(limit).all()


@router.post("/", response_model=FacultyOut, status_code=status.HTTP_201_CREATED)
def create_faculty(
    payload: FacultyCreate,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    existing = db.query(Faculty).filter(Faculty.faculty_id == payload.faculty_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Faculty ID already exists.")

    data = payload.model_dump()
    if not data.get("department_id"):
        default_dept = db.query(Department).first()
        if not default_dept:
            default_dept = Department(name="School of Computer Science & Engineering", code="KLE-CSE")
            db.add(default_dept)
            db.flush()
        data["department_id"] = default_dept.id

    if not data.get("user_id"):
        from app.models.user import User, UserRole
        from app.utils.auth import hash_password
        u = db.query(User).filter(User.email == payload.email).first()
        if not u:
            u = User(
                email=payload.email,
                hashed_password=hash_password("Faculty@123456"),
                full_name=payload.full_name,
                role=UserRole.faculty_member,
                is_active=True,
            )
            db.add(u)
            db.flush()
        data["user_id"] = u.id

    faculty = Faculty(**data)
    db.add(faculty)
    db.commit()
    db.refresh(faculty)
    return faculty


@router.get("/{faculty_id}", response_model=FacultyOut)
def get_faculty(faculty_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    f = None
    try:
        val = UUID(faculty_id)
        f = db.get(Faculty, val)
    except (ValueError, AttributeError):
        pass
    if not f:
        f = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty not found.")
    return f


@router.get("/{faculty_id}/publications", response_model=List[PublicationOut])
def get_faculty_publications(
    faculty_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    f = None
    try:
        val = UUID(faculty_id)
        f = db.get(Faculty, val)
    except (ValueError, AttributeError):
        pass
    if not f:
        f = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty not found.")

    pubs = (
        db.query(Publication)
        .join(PublicationAuthor, PublicationAuthor.publication_id == Publication.id)
        .filter(PublicationAuthor.faculty_id == f.id)
        .order_by(Publication.publication_year.desc(), Publication.total_citations.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return pubs


@router.get("/{faculty_id}/citation-metrics")
def get_faculty_citation_metrics(
    faculty_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    f = None
    try:
        val = UUID(faculty_id)
        f = db.get(Faculty, val)
    except (ValueError, AttributeError):
        pass
    if not f:
        f = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty not found.")

    pubs = (
        db.query(Publication)
        .join(PublicationAuthor, PublicationAuthor.publication_id == Publication.id)
        .filter(PublicationAuthor.faculty_id == f.id)
        .all()
    )
    total_pubs = len(pubs)
    total_cites = sum(p.total_citations or 0 for p in pubs)
    cites_sorted = sorted([p.total_citations or 0 for p in pubs], reverse=True)
    h_idx = 0
    for idx, c in enumerate(cites_sorted, start=1):
        if c >= idx:
            h_idx = idx
        else:
            break
    i10_idx = sum(1 for c in cites_sorted if c >= 10)

    return {
        "faculty_id": f.faculty_id,
        "full_name": f.full_name,
        "total_publications": total_pubs,
        "total_citations": total_cites,
        "h_index": h_idx,
        "i10_index": i10_idx,
        "avg_citations_per_pub": round(total_cites / total_pubs, 2) if total_pubs > 0 else 0,
    }


@router.patch("/{faculty_id}", response_model=FacultyOut)
def update_faculty(
    faculty_id: str,
    payload: FacultyUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    f = None
    try:
        val = UUID(faculty_id)
        f = db.get(Faculty, val)
    except (ValueError, AttributeError):
        pass
    if not f:
        f = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty not found.")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(f, k, v)
    db.commit()
    db.refresh(f)
    return f


@router.delete("/{faculty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faculty(
    faculty_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_coordinator_or_admin),
):
    f = None
    try:
        val = UUID(faculty_id)
        f = db.get(Faculty, val)
    except (ValueError, AttributeError):
        pass
    if not f:
        f = db.query(Faculty).filter(Faculty.faculty_id == faculty_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Faculty not found.")
    f.is_active = False
    db.commit()
