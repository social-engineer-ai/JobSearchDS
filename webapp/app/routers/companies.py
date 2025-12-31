"""Company API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.company import Company
from ..schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyList
)

router = APIRouter()


@router.get("/", response_model=CompanyList)
def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    industry: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List companies with pagination and filters."""
    query = db.query(Company).filter(Company.is_active == True)

    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry}%"))
    if location:
        query = query.filter(Company.headquarters.ilike(f"%{location}%"))

    total = query.count()
    pages = (total + page_size - 1) // page_size

    companies = query.offset((page - 1) * page_size).limit(page_size).all()

    return CompanyList(
        items=companies,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a company by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company."""
    # Check if email already exists
    existing = db.query(Company).filter(Company.email == company.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_company = Company(
        name=company.name,
        email=company.email,
        password_hash=company.password,  # TODO: Hash password
        description=company.description,
        industry=company.industry,
        company_size=company.company_size,
        founded_year=company.founded_year,
        website=company.website,
        headquarters=company.headquarters,
        culture_description=company.culture_description
    )

    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db)
):
    """Update a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = company_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """Delete (deactivate) a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.is_active = False
    db.commit()
    return None
