"""Pydantic schemas for request/response validation."""
from .candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateList
)
from .company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyList
)
from .job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobList,
    JobSearch
)
from .application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationList
)

__all__ = [
    # Candidate
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateResponse",
    "CandidateList",
    # Company
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyList",
    # Job
    "JobCreate",
    "JobUpdate",
    "JobResponse",
    "JobList",
    "JobSearch",
    # Application
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "ApplicationList"
]
