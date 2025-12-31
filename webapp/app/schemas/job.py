"""Pydantic schemas for Job."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """Base job schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=10)
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    job_type: Optional[str] = Field(None, max_length=50)
    experience_level: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)
    is_remote: bool = False
    remote_type: Optional[str] = Field(None, max_length=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    salary_currency: str = "USD"
    show_salary: bool = True


class JobCreate(JobBase):
    """Schema for creating a job."""
    company_id: int


class JobUpdate(BaseModel):
    """Schema for updating a job (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    job_type: Optional[str] = Field(None, max_length=50)
    experience_level: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=100)
    is_remote: Optional[bool] = None
    remote_type: Optional[str] = Field(None, max_length=50)
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    show_salary: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)


class JobResponse(JobBase):
    """Schema for job response."""
    id: int
    company_id: int
    status: str
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    posted_at: datetime

    class Config:
        from_attributes = True


class JobList(BaseModel):
    """Schema for paginated job list."""
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    pages: int


class JobSearch(BaseModel):
    """Schema for job search parameters."""
    query: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    company_id: Optional[int] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
