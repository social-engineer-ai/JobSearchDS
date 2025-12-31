"""Application API routes."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.application import Application
from ..models.candidate import Candidate
from ..models.job import Job
from ..schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationList,
    ApplicationStatusUpdate
)

router = APIRouter()


@router.get("/", response_model=ApplicationList)
def list_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    candidate_id: Optional[int] = None,
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List applications with pagination and filters."""
    query = db.query(Application)

    if candidate_id:
        query = query.filter(Application.candidate_id == candidate_id)
    if job_id:
        query = query.filter(Application.job_id == job_id)
    if status:
        query = query.filter(Application.status == status)

    # Order by most recent
    query = query.order_by(Application.created_at.desc())

    total = query.count()
    pages = (total + page_size - 1) // page_size

    applications = query.offset((page - 1) * page_size).limit(page_size).all()

    return ApplicationList(
        items=applications,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    """Get an application by ID."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post("/", response_model=ApplicationResponse, status_code=201)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """Create a new application."""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == application.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Verify job exists and is open
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "open":
        raise HTTPException(status_code=400, detail="Job is not accepting applications")

    # Check for duplicate application
    existing = db.query(Application).filter(
        Application.candidate_id == application.candidate_id,
        Application.job_id == application.job_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    db_application = Application(
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        cover_letter=application.cover_letter,
        answers=application.answers,
        resume_version=candidate.resume_text  # Snapshot current resume
    )

    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update an application."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update application status with workflow tracking."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update status
    old_status = application.status
    application.status = status_update.status

    # Update workflow timestamps
    now = datetime.utcnow()
    if status_update.status == "reviewed" and not application.reviewed_at:
        application.reviewed_at = now
    elif status_update.status == "shortlisted" and not application.shortlisted_at:
        application.shortlisted_at = now
    elif status_update.status == "interviewing" and not application.interviewed_at:
        application.interviewed_at = now
    elif status_update.status == "offered" and not application.offered_at:
        application.offered_at = now
    elif status_update.status in ["accepted", "rejected"] and not application.decided_at:
        application.decided_at = now

    # Add notes if provided
    if status_update.notes:
        if application.recruiter_notes:
            application.recruiter_notes += f"\n\n[{now}] {status_update.notes}"
        else:
            application.recruiter_notes = f"[{now}] {status_update.notes}"

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=204)
def withdraw_application(application_id: int, db: Session = Depends(get_db)):
    """Withdraw an application."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application.status = "withdrawn"
    db.commit()
    return None
