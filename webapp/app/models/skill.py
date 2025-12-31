"""Skill models - normalized skill taxonomy and associations."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from ..database import Base


class Skill(Base):
    """Normalized skill taxonomy."""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)  # Programming, Design, Marketing, etc.
    description = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Skill {self.name}>"


class CandidateSkill(Base):
    """Association between candidates and skills."""

    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    # Skill details
    proficiency_level = Column(String(50))  # beginner, intermediate, advanced, expert
    years_experience = Column(Integer)
    is_primary = Column(Boolean, default=False)  # Primary/highlighted skill

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill")

    def __repr__(self):
        return f"<CandidateSkill {self.candidate_id}:{self.skill_id}>"


class JobSkill(Base):
    """Association between jobs and required skills."""

    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    # Requirement details
    is_required = Column(Boolean, default=True)  # Required vs. nice-to-have
    minimum_years = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="required_skills")
    skill = relationship("Skill")

    def __repr__(self):
        return f"<JobSkill {self.job_id}:{self.skill_id}>"
