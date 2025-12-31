"""Pydantic schemas for Company."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class CompanyBase(BaseModel):
    """Base company schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)
    website: Optional[str] = Field(None, max_length=500)
    headquarters: Optional[str] = Field(None, max_length=100)
    culture_description: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    password: str = Field(..., min_length=8)


class CompanyUpdate(BaseModel):
    """Schema for updating a company (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    company_size: Optional[str] = Field(None, max_length=50)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)
    website: Optional[str] = Field(None, max_length=500)
    headquarters: Optional[str] = Field(None, max_length=100)
    culture_description: Optional[str] = None
    benefits: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyList(BaseModel):
    """Schema for paginated company list."""
    items: List[CompanyResponse]
    total: int
    page: int
    page_size: int
    pages: int
