"""Pydantic schemas for Candidate."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class CandidateBase(BaseModel):
    """Base candidate schema with common fields."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    headline: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    years_experience: Optional[float] = Field(None, ge=0)
    current_company: Optional[str] = Field(None, max_length=255)
    current_title: Optional[str] = Field(None, max_length=255)
    desired_salary_min: Optional[int] = Field(None, ge=0)
    desired_salary_max: Optional[int] = Field(None, ge=0)
    desired_location: Optional[str] = Field(None, max_length=100)
    open_to_remote: bool = True
    job_type_preference: Optional[str] = Field(None, max_length=50)


class CandidateCreate(CandidateBase):
    """Schema for creating a candidate."""
    password: str = Field(..., min_length=8)


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate (all fields optional)."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    headline: Optional[str] = Field(None, max_length=255)
    summary: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    years_experience: Optional[float] = Field(None, ge=0)
    current_company: Optional[str] = Field(None, max_length=255)
    current_title: Optional[str] = Field(None, max_length=255)
    desired_salary_min: Optional[int] = Field(None, ge=0)
    desired_salary_max: Optional[int] = Field(None, ge=0)
    desired_location: Optional[str] = Field(None, max_length=100)
    open_to_remote: Optional[bool] = None
    job_type_preference: Optional[str] = Field(None, max_length=50)
    is_open_to_opportunities: Optional[bool] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate response."""
    id: int
    is_active: bool
    is_open_to_opportunities: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateList(BaseModel):
    """Schema for paginated candidate list."""
    items: List[CandidateResponse]
    total: int
    page: int
    page_size: int
    pages: int
