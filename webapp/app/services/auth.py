"""Authentication service - password hashing and session management."""
from passlib.context import CryptContext
from typing import Optional, Union
from sqlalchemy.orm import Session

from ..models.candidate import Candidate
from ..models.company import Company

# Password hashing context - use pbkdf2 (portable across all platforms)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_candidate(db: Session, email: str, password: str) -> Optional[Candidate]:
    """Authenticate a candidate by email and password."""
    candidate = db.query(Candidate).filter(
        Candidate.email == email,
        Candidate.is_active == True
    ).first()

    if not candidate:
        return None
    if not verify_password(password, candidate.password_hash):
        return None
    return candidate


def authenticate_company(db: Session, email: str, password: str) -> Optional[Company]:
    """Authenticate a company by email and password."""
    company = db.query(Company).filter(
        Company.email == email,
        Company.is_active == True
    ).first()

    if not company:
        return None
    if not verify_password(password, company.password_hash):
        return None
    return company


def get_user_by_session(
    db: Session,
    user_id: int,
    user_type: str
) -> Optional[Union[Candidate, Company]]:
    """Get user by ID and type from session."""
    if user_type == "candidate":
        return db.query(Candidate).filter(
            Candidate.id == user_id,
            Candidate.is_active == True
        ).first()
    elif user_type == "company":
        return db.query(Company).filter(
            Company.id == user_id,
            Company.is_active == True
        ).first()
    return None
