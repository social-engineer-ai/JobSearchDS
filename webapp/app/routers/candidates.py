"""Candidate API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.candidate import Candidate
from ..schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateList
)

router = APIRouter()


@router.get("/", response_model=CandidateList)
def list_candidates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    location: Optional[str] = None,
    is_open: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List candidates with pagination and filters."""
    query = db.query(Candidate).filter(Candidate.is_active == True)

    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))
    if is_open is not None:
        query = query.filter(Candidate.is_open_to_opportunities == is_open)

    total = query.count()
    pages = (total + page_size - 1) // page_size

    candidates = query.offset((page - 1) * page_size).limit(page_size).all()

    return CandidateList(
        items=candidates,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get a candidate by ID."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/", response_model=CandidateResponse, status_code=201)
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    """Create a new candidate."""
    # Check if email already exists
    existing = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create candidate (password hashing would be added in production)
    db_candidate = Candidate(
        email=candidate.email,
        password_hash=candidate.password,  # TODO: Hash password
        first_name=candidate.first_name,
        last_name=candidate.last_name,
        headline=candidate.headline,
        summary=candidate.summary,
        location=candidate.location,
        phone=candidate.phone,
        years_experience=candidate.years_experience,
        current_company=candidate.current_company,
        current_title=candidate.current_title,
        desired_salary_min=candidate.desired_salary_min,
        desired_salary_max=candidate.desired_salary_max,
        desired_location=candidate.desired_location,
        open_to_remote=candidate.open_to_remote,
        job_type_preference=candidate.job_type_preference
    )

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db)
):
    """Update a candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    update_data = candidate_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)

    db.commit()
    db.refresh(candidate)
    return candidate


@router.delete("/{candidate_id}", status_code=204)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) a candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.is_active = False
    db.commit()
    return None
