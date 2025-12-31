"""Candidate model - job seekers on the platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import relationship

from ..database import Base


class Candidate(Base):
    """Candidate/job seeker model."""

    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # Profile
    headline = Column(String(255))  # e.g., "Senior Software Engineer"
    summary = Column(Text)
    location = Column(String(100))
    phone = Column(String(20))

    # Experience
    years_experience = Column(Float, default=0)
    current_company = Column(String(255))
    current_title = Column(String(255))

    # Preferences
    desired_salary_min = Column(Integer)
    desired_salary_max = Column(Integer)
    desired_location = Column(String(100))
    open_to_remote = Column(Boolean, default=True)
    job_type_preference = Column(String(50))  # full-time, part-time, contract

    # Resume
    resume_text = Column(Text)  # Parsed resume content
    resume_file_path = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_open_to_opportunities = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    skills = relationship("CandidateSkill", back_populates="candidate")
    applications = relationship("Application", back_populates="candidate")
    interactions = relationship("Interaction", back_populates="candidate")

    def __repr__(self):
        return f"<Candidate {self.email}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
