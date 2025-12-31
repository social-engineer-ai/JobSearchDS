"""Pydantic schemas for Application."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ApplicationBase(BaseModel):
    """Base application schema with common fields."""
    cover_letter: Optional[str] = None
    answers: Optional[str] = None  # JSON string for screening question answers


class ApplicationCreate(ApplicationBase):
    """Schema for creating an application."""
    candidate_id: int
    job_id: int


class ApplicationUpdate(BaseModel):
    """Schema for updating an application (all fields optional)."""
    status: Optional[str] = Field(None, max_length=50)
    recruiter_notes: Optional[str] = None
    match_score: Optional[int] = Field(None, ge=0, le=100)
    match_reasons: Optional[str] = None  # JSON string


class ApplicationResponse(ApplicationBase):
    """Schema for application response."""
    id: int
    candidate_id: int
    job_id: int
    status: str
    match_score: Optional[int]
    created_at: datetime
    updated_at: datetime
    reviewed_at: Optional[datetime]
    shortlisted_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApplicationList(BaseModel):
    """Schema for paginated application list."""
    items: List[ApplicationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ApplicationStatusUpdate(BaseModel):
    """Schema for updating application status."""
    status: str = Field(..., max_length=50)
    notes: Optional[str] = None
