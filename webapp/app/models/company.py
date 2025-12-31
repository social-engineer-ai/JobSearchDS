"""Company model - employers on the platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

from sqlalchemy.orm import relationship

from ..database import Base


class Company(Base):
    """Company/employer model."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Company details
    description = Column(Text)
    industry = Column(String(100), index=True)
    company_size = Column(String(50))  # 1-10, 11-50, 51-200, 201-500, 500+
    founded_year = Column(Integer)
    website = Column(String(500))

    # Location
    headquarters = Column(String(100))
    locations = Column(Text)  # JSON array of locations

    # Culture & Benefits
    culture_description = Column(Text)
    benefits = Column(Text)  # JSON array of benefits

    # Branding
    logo_url = Column(String(500))
    cover_image_url = Column(String(500))

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    jobs = relationship("Job", back_populates="company")

    def __repr__(self):
        return f"<Company {self.name}>"
