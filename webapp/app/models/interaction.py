"""Interaction model - logs user actions for analytics and ML training."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

from ..database import Base


class Interaction(Base):
    """User interaction log for analytics and recommendations."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    # Who
    candidate_id = Column(Integer, ForeignKey("candidates.id"), index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)

    # What
    action_type = Column(String(50), nullable=False, index=True)
    # Action types:
    # - job_view, job_click, job_save, job_apply, job_share
    # - search, filter_apply
    # - profile_view (recruiter viewing candidate)
    # - recommendation_view, recommendation_click

    # Target
    target_type = Column(String(50))  # job, candidate, company, search
    target_id = Column(Integer)

    # Context
    session_id = Column(String(100), index=True)
    source = Column(String(50))  # search, recommendation, direct, email
    position = Column(Integer)  # Position in list (for ranking analysis)

    # Search context (if action is search-related)
    search_query = Column(Text)
    filters_applied = Column(Text)  # JSON of filters

    # Recommendation context
    recommendation_score = Column(Float)
    recommendation_explanation = Column(Text)

    # Outcome (for training data)
    outcome = Column(String(50))  # applied, hired, rejected, no_action
    outcome_at = Column(DateTime)

    # Metadata
    user_agent = Column(String(500))
    ip_address = Column(String(50))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="interactions")

    def __repr__(self):
        return f"<Interaction {self.action_type} by {self.candidate_id or self.company_id}>"
