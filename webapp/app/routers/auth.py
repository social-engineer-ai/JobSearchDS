"""Authentication routes - login, register, logout."""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.candidate import Candidate
from ..models.company import Company
from ..services.auth import (
    hash_password,
    authenticate_candidate,
    authenticate_company
)

router = APIRouter()

# Session cookie name
SESSION_COOKIE = "jobmatch_session"


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current logged-in user from session cookie."""
    session_data = request.cookies.get(SESSION_COOKIE)
    if not session_data:
        return None

    try:
        # Format: "user_type:user_id"
        user_type, user_id = session_data.split(":")
        user_id = int(user_id)

        if user_type == "candidate":
            return {"type": "candidate", "user": db.query(Candidate).filter(Candidate.id == user_id).first()}
        elif user_type == "company":
            return {"type": "company", "user": db.query(Company).filter(Company.id == user_id).first()}
    except:
        pass
    return None


def require_auth(request: Request, db: Session = Depends(get_db)):
    """Dependency that requires authentication."""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def require_candidate(request: Request, db: Session = Depends(get_db)):
    """Dependency that requires candidate authentication."""
    user = get_current_user(request, db)
    if not user or user["type"] != "candidate":
        raise HTTPException(status_code=401, detail="Candidate authentication required")
    return user["user"]


def require_company(request: Request, db: Session = Depends(get_db)):
    """Dependency that requires company authentication."""
    user = get_current_user(request, db)
    if not user or user["type"] != "company":
        raise HTTPException(status_code=401, detail="Company authentication required")
    return user["user"]


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/login/candidate")
async def login_candidate(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login as a candidate."""
    candidate = authenticate_candidate(db, email, password)
    if not candidate:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Set session cookie
    response = RedirectResponse(url="/candidate/dashboard", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=f"candidate:{candidate.id}",
        httponly=True,
        max_age=86400 * 7  # 7 days
    )
    return response


@router.post("/login/company")
async def login_company(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login as a company/recruiter."""
    company = authenticate_company(db, email, password)
    if not company:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Set session cookie
    response = RedirectResponse(url="/recruiter/dashboard", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=f"company:{company.id}",
        httponly=True,
        max_age=86400 * 7  # 7 days
    )
    return response


@router.post("/register/candidate")
async def register_candidate(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Register a new candidate."""
    # Check if email exists
    if db.query(Candidate).filter(Candidate.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create candidate
    candidate = Candidate(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Auto-login
    response = RedirectResponse(url="/candidate/dashboard", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=f"candidate:{candidate.id}",
        httponly=True,
        max_age=86400 * 7
    )
    return response


@router.post("/register/company")
async def register_company(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    industry: str = Form(None),
    db: Session = Depends(get_db)
):
    """Register a new company."""
    # Check if email exists
    if db.query(Company).filter(Company.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create company
    company = Company(
        email=email,
        password_hash=hash_password(password),
        name=name,
        industry=industry
    )
    db.add(company)
    db.commit()
    db.refresh(company)

    # Auto-login
    response = RedirectResponse(url="/recruiter/dashboard", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=f"company:{company.id}",
        httponly=True,
        max_age=86400 * 7
    )
    return response


@router.get("/logout")
async def logout():
    """Logout and clear session."""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


@router.get("/me")
async def get_current_user_info(user = Depends(require_auth)):
    """Get current user info."""
    return {
        "type": user["type"],
        "id": user["user"].id,
        "email": user["user"].email,
        "name": user["user"].name if user["type"] == "company" else f"{user['user'].first_name} {user['user'].last_name}"
    }
