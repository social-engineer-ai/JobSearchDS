"""Application model - job applications linking candidates to jobs."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base


class Application(Base):
    """Job application model."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    # Relationships
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)

    # Application content
    cover_letter = Column(Text)
    resume_version = Column(Text)  # Snapshot of resume at application time
    answers = Column(Text)  # JSON for screening question answers

    # Status workflow
    status = Column(String(50), default="submitted", index=True)
    # Status values: submitted, reviewed, shortlisted, interviewing,
    #                offered, accepted, rejected, withdrawn

    # Recruiter notes (internal)
    recruiter_notes = Column(Text)
    match_score = Column(Integer)  # Score from candidate ranker (0-100)
    match_reasons = Column(Text)  # JSON array of match reasons

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = Column(DateTime)
    shortlisted_at = Column(DateTime)
    interviewed_at = Column(DateTime)
    offered_at = Column(DateTime)
    decided_at = Column(DateTime)  # When candidate accepted/rejected offer

    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")

    def __repr__(self):
        return f"<Application {self.candidate_id} -> {self.job_id}>"
