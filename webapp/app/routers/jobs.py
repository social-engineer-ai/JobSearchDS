"""Job API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models.job import Job
from ..models.company import Company
from ..schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobList,
    JobSearch
)

router = APIRouter()


@router.get("/", response_model=JobList)
def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    experience_level: Optional[str] = None,
    is_remote: Optional[bool] = None,
    salary_min: Optional[int] = None,
    company_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List jobs with pagination and filters."""
    db_query = db.query(Job).filter(Job.status == "open")

    # Text search
    if query:
        search_filter = or_(
            Job.title.ilike(f"%{query}%"),
            Job.description.ilike(f"%{query}%")
        )
        db_query = db_query.filter(search_filter)

    # Filters
    if category:
        db_query = db_query.filter(Job.category.ilike(f"%{category}%"))
    if location:
        db_query = db_query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        db_query = db_query.filter(Job.job_type == job_type)
    if experience_level:
        db_query = db_query.filter(Job.experience_level == experience_level)
    if is_remote is not None:
        db_query = db_query.filter(Job.is_remote == is_remote)
    if salary_min:
        db_query = db_query.filter(Job.salary_max >= salary_min)
    if company_id:
        db_query = db_query.filter(Job.company_id == company_id)

    # Order by most recent
    db_query = db_query.order_by(Job.posted_at.desc())

    total = db_query.count()
    pages = (total + page_size - 1) // page_size

    jobs = db_query.offset((page - 1) * page_size).limit(page_size).all()

    return JobList(
        items=jobs,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Create a new job posting."""
    # Verify company exists
    company = db.query(Company).filter(Company.id == job.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    db_job = Job(
        company_id=job.company_id,
        title=job.title,
        description=job.description,
        requirements=job.requirements,
        responsibilities=job.responsibilities,
        category=job.category,
        job_type=job.job_type,
        experience_level=job.experience_level,
        location=job.location,
        is_remote=job.is_remote,
        remote_type=job.remote_type,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        show_salary=job.show_salary
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    db: Session = Depends(get_db)
):
    """Update a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Close a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "closed"
    db.commit()
    return None


@router.post("/{job_id}/close", response_model=JobResponse)
def close_job(job_id: int, db: Session = Depends(get_db)):
    """Close a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "closed"
    db.commit()
    db.refresh(job)
    return job
