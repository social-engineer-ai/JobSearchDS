"""Job model - job postings on the platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Job(Base):
    """Job posting model."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    # Company relationship
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Basic info
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    responsibilities = Column(Text)

    # Classification
    category = Column(String(100), index=True)  # Engineering, Marketing, etc.
    job_type = Column(String(50))  # full-time, part-time, contract, internship
    experience_level = Column(String(50))  # entry, mid, senior, executive

    # Location
    location = Column(String(100), index=True)
    is_remote = Column(Boolean, default=False)
    remote_type = Column(String(50))  # fully-remote, hybrid, on-site

    # Compensation
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    salary_currency = Column(String(10), default="USD")
    show_salary = Column(Boolean, default=True)

    # Status
    status = Column(String(50), default="open", index=True)  # open, closed, paused, filled
    is_featured = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    posted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    closed_at = Column(DateTime)

    # Relationships
    company = relationship("Company", back_populates="jobs")
    required_skills = relationship("JobSkill", back_populates="job")
    applications = relationship("Application", back_populates="job")

    def __repr__(self):
        return f"<Job {self.title} at {self.company_id}>"
