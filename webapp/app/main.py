"""JobMatch Web Application - Main Entry Point."""
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pathlib import Path
from typing import Optional
import httpx

from .config import get_settings
from .database import init_db, get_db
from .models.candidate import Candidate
from .models.company import Company
from .models.job import Job
from .models.application import Application
from .routers import candidates, companies, jobs, applications, auth
from .routers.auth import get_current_user, SESSION_COOKIE
from .services.auth import hash_password

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Educational job search platform for ML/DS learning",
    version="1.0.0",
    debug=settings.debug
)

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Include API routers
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(companies.router, prefix="/api/companies", tags=["Companies"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


# =============================================================================
# Helper Functions
# =============================================================================

def get_user_context(request: Request, db: Session):
    """Get user context for templates."""
    user_data = get_current_user(request, db)
    if user_data:
        return {
            "type": user_data["type"],
            "user": user_data["user"],
            "name": user_data["user"].name if user_data["type"] == "company" else f"{user_data['user'].first_name} {user_data['user'].last_name}"
        }
    return None


# =============================================================================
# Home & Health
# =============================================================================

@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page."""
    user = get_user_context(request, db)

    # Get featured jobs
    featured_jobs = db.query(Job).filter(
        Job.status == "open"
    ).order_by(Job.posted_at.desc()).limit(6).all()

    # Get stats
    job_count = db.query(Job).filter(Job.status == "open").count()
    company_count = db.query(Company).filter(Company.is_active == True).count()
    candidate_count = db.query(Candidate).filter(Candidate.is_active == True).count()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "featured_jobs": featured_jobs,
        "job_count": job_count,
        "company_count": company_count,
        "candidate_count": candidate_count
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "webapp"}


# =============================================================================
# Auth Pages
# =============================================================================

@app.get("/auth/login")
async def login_page(request: Request, db: Session = Depends(get_db)):
    """Login page."""
    user = get_user_context(request, db)
    if user:
        if user["type"] == "candidate":
            return RedirectResponse(url="/candidate/dashboard", status_code=303)
        return RedirectResponse(url="/recruiter/dashboard", status_code=303)

    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "user": None,
        "login_type": "candidate"
    })


@app.get("/auth/register")
async def register_page(request: Request, db: Session = Depends(get_db)):
    """Registration page."""
    user = get_user_context(request, db)
    if user:
        if user["type"] == "candidate":
            return RedirectResponse(url="/candidate/dashboard", status_code=303)
        return RedirectResponse(url="/recruiter/dashboard", status_code=303)

    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "user": None
    })


# =============================================================================
# Job Pages
# =============================================================================

@app.get("/jobs")
async def jobs_list(
    request: Request,
    db: Session = Depends(get_db),
    query: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    is_remote: Optional[bool] = None,
    page: int = 1
):
    """Job listing page."""
    user = get_user_context(request, db)
    page_size = 20

    # Build query
    db_query = db.query(Job).filter(Job.status == "open")

    if query:
        db_query = db_query.filter(
            or_(
                Job.title.ilike(f"%{query}%"),
                Job.description.ilike(f"%{query}%")
            )
        )
    if category:
        db_query = db_query.filter(Job.category.ilike(f"%{category}%"))
    if location:
        db_query = db_query.filter(Job.location.ilike(f"%{location}%"))
    if is_remote:
        db_query = db_query.filter(Job.is_remote == True)

    # Order and paginate
    db_query = db_query.order_by(Job.posted_at.desc())
    total = db_query.count()
    pages = (total + page_size - 1) // page_size
    jobs = db_query.offset((page - 1) * page_size).limit(page_size).all()

    # Load company for each job
    for job in jobs:
        job.company = db.query(Company).filter(Company.id == job.company_id).first()

    return templates.TemplateResponse("jobs/list.html", {
        "request": request,
        "user": user,
        "jobs": jobs,
        "total": total,
        "page": page,
        "pages": pages,
        "query": query,
        "category": category,
        "location": location,
        "is_remote": is_remote
    })


@app.get("/jobs/{job_id}")
async def job_detail(request: Request, job_id: int, db: Session = Depends(get_db)):
    """Job detail page."""
    user = get_user_context(request, db)

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.company = db.query(Company).filter(Company.id == job.company_id).first()

    # Check if user already applied
    already_applied = False
    if user and user["type"] == "candidate":
        existing = db.query(Application).filter(
            Application.candidate_id == user["user"].id,
            Application.job_id == job_id
        ).first()
        already_applied = existing is not None

    # Get salary prediction from gateway
    salary_prediction = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.gateway_url}/api/predict-salary",
                json={"job_title": job.title, "location": job.location},
                timeout=3.0
            )
            if response.status_code == 200:
                salary_prediction = response.json()
    except:
        pass

    return templates.TemplateResponse("jobs/detail.html", {
        "request": request,
        "user": user,
        "job": job,
        "already_applied": already_applied,
        "salary_prediction": salary_prediction
    })


@app.get("/jobs/{job_id}/apply")
async def apply_page(request: Request, job_id: int, db: Session = Depends(get_db)):
    """Job application page."""
    user = get_user_context(request, db)

    if not user or user["type"] != "candidate":
        return RedirectResponse(url="/auth/login", status_code=303)

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.company = db.query(Company).filter(Company.id == job.company_id).first()

    # Check if already applied
    existing = db.query(Application).filter(
        Application.candidate_id == user["user"].id,
        Application.job_id == job_id
    ).first()
    if existing:
        return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)

    return templates.TemplateResponse("jobs/apply.html", {
        "request": request,
        "user": user,
        "job": job,
        "candidate": user["user"]
    })


@app.post("/jobs/{job_id}/apply")
async def submit_application(
    request: Request,
    job_id: int,
    cover_letter: str = Form(None),
    db: Session = Depends(get_db)
):
    """Submit job application."""
    user = get_user_context(request, db)

    if not user or user["type"] != "candidate":
        return RedirectResponse(url="/auth/login", status_code=303)

    # Check job exists and is open
    job = db.query(Job).filter(Job.id == job_id, Job.status == "open").first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or closed")

    # Check not already applied
    existing = db.query(Application).filter(
        Application.candidate_id == user["user"].id,
        Application.job_id == job_id
    ).first()
    if existing:
        return RedirectResponse(url="/candidate/dashboard", status_code=303)

    # Create application
    application = Application(
        candidate_id=user["user"].id,
        job_id=job_id,
        cover_letter=cover_letter,
        resume_version=user["user"].resume_text
    )
    db.add(application)
    db.commit()

    return RedirectResponse(url="/candidate/dashboard?success=Application submitted!", status_code=303)


# =============================================================================
# Candidate Pages
# =============================================================================

@app.get("/candidate/dashboard")
async def candidate_dashboard(request: Request, db: Session = Depends(get_db)):
    """Candidate dashboard."""
    user = get_user_context(request, db)

    if not user or user["type"] != "candidate":
        return RedirectResponse(url="/auth/login", status_code=303)

    candidate = user["user"]

    # Get applications with job info
    applications = db.query(Application).filter(
        Application.candidate_id == candidate.id
    ).order_by(Application.created_at.desc()).all()

    for app in applications:
        app.job = db.query(Job).filter(Job.id == app.job_id).first()
        if app.job:
            app.job.company = db.query(Company).filter(Company.id == app.job.company_id).first()

    # Get recommendations from gateway
    recommendations = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.gateway_url}/api/recommend",
                json={"candidate_id": candidate.id, "num_recommendations": 5},
                timeout=3.0
            )
            if response.status_code == 200:
                data = response.json()
                job_ids = data.get("job_ids", [])
                for jid in job_ids:
                    job = db.query(Job).filter(Job.id == jid, Job.status == "open").first()
                    if job:
                        job.company = db.query(Company).filter(Company.id == job.company_id).first()
                        recommendations.append(job)
    except:
        # Fallback: just get recent jobs
        recommendations = db.query(Job).filter(Job.status == "open").order_by(Job.posted_at.desc()).limit(5).all()
        for job in recommendations:
            job.company = db.query(Company).filter(Company.id == job.company_id).first()

    return templates.TemplateResponse("candidate/dashboard.html", {
        "request": request,
        "user": user,
        "candidate": candidate,
        "applications": applications,
        "recommendations": recommendations
    })


@app.get("/candidate/profile")
async def candidate_profile_page(request: Request, db: Session = Depends(get_db)):
    """Candidate profile edit page."""
    user = get_user_context(request, db)

    if not user or user["type"] != "candidate":
        return RedirectResponse(url="/auth/login", status_code=303)

    return templates.TemplateResponse("candidate/profile.html", {
        "request": request,
        "user": user,
        "candidate": user["user"]
    })


@app.post("/candidate/profile")
async def update_candidate_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    headline: str = Form(None),
    summary: str = Form(None),
    location: str = Form(None),
    phone: str = Form(None),
    current_title: str = Form(None),
    current_company: str = Form(None),
    years_experience: int = Form(None),
    desired_salary_min: int = Form(None),
    desired_salary_max: int = Form(None),
    desired_location: str = Form(None),
    job_type_preference: str = Form(None),
    open_to_remote: bool = Form(False),
    is_open_to_opportunities: bool = Form(False),
    resume_text: str = Form(None),
    db: Session = Depends(get_db)
):
    """Update candidate profile."""
    user = get_user_context(request, db)

    if not user or user["type"] != "candidate":
        return RedirectResponse(url="/auth/login", status_code=303)

    candidate = user["user"]
    candidate.first_name = first_name
    candidate.last_name = last_name
    candidate.headline = headline
    candidate.summary = summary
    candidate.location = location
    candidate.phone = phone
    candidate.current_title = current_title
    candidate.current_company = current_company
    candidate.years_experience = years_experience
    candidate.desired_salary_min = desired_salary_min
    candidate.desired_salary_max = desired_salary_max
    candidate.desired_location = desired_location
    candidate.job_type_preference = job_type_preference
    candidate.open_to_remote = open_to_remote
    candidate.is_open_to_opportunities = is_open_to_opportunities
    candidate.resume_text = resume_text

    db.commit()

    return RedirectResponse(url="/candidate/dashboard?success=Profile updated!", status_code=303)


# =============================================================================
# Recruiter Pages
# =============================================================================

@app.get("/recruiter/dashboard")
async def recruiter_dashboard(request: Request, db: Session = Depends(get_db)):
    """Recruiter dashboard."""
    user = get_user_context(request, db)

    if not user or user["type"] != "company":
        return RedirectResponse(url="/auth/login", status_code=303)

    company = user["user"]

    # Get company's jobs
    jobs = db.query(Job).filter(
        Job.company_id == company.id
    ).order_by(Job.posted_at.desc()).all()

    # Load applications for each job
    total_applications = 0
    pending_review = 0
    shortlisted = 0

    for job in jobs:
        job.applications = db.query(Application).filter(Application.job_id == job.id).all()
        total_applications += len(job.applications)
        pending_review += len([a for a in job.applications if a.status == "submitted"])
        shortlisted += len([a for a in job.applications if a.status == "shortlisted"])

    return templates.TemplateResponse("recruiter/dashboard.html", {
        "request": request,
        "user": user,
        "company": company,
        "jobs": jobs,
        "total_applications": total_applications,
        "pending_review": pending_review,
        "shortlisted": shortlisted
    })


@app.get("/recruiter/post-job")
async def post_job_page(request: Request, db: Session = Depends(get_db)):
    """Post job page."""
    user = get_user_context(request, db)

    if not user or user["type"] != "company":
        return RedirectResponse(url="/auth/login", status_code=303)

    return templates.TemplateResponse("recruiter/post_job.html", {
        "request": request,
        "user": user,
        "company": user["user"]
    })


@app.post("/recruiter/post-job")
async def create_job_posting(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    requirements: str = Form(None),
    responsibilities: str = Form(None),
    category: str = Form(None),
    job_type: str = Form("full-time"),
    experience_level: str = Form(None),
    location: str = Form(None),
    is_remote: bool = Form(False),
    remote_type: str = Form(None),
    salary_min: int = Form(None),
    salary_max: int = Form(None),
    show_salary: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Create a new job posting."""
    user = get_user_context(request, db)

    if not user or user["type"] != "company":
        return RedirectResponse(url="/auth/login", status_code=303)

    job = Job(
        company_id=user["user"].id,
        title=title,
        description=description,
        requirements=requirements,
        responsibilities=responsibilities,
        category=category,
        job_type=job_type,
        experience_level=experience_level,
        location=location,
        is_remote=is_remote,
        remote_type=remote_type,
        salary_min=salary_min,
        salary_max=salary_max,
        show_salary=show_salary,
        status="open"
    )
    db.add(job)
    db.commit()

    return RedirectResponse(url="/recruiter/dashboard?success=Job posted!", status_code=303)


@app.get("/recruiter/jobs/{job_id}/applicants")
async def job_applicants(request: Request, job_id: int, db: Session = Depends(get_db)):
    """View applicants for a job."""
    user = get_user_context(request, db)

    if not user or user["type"] != "company":
        return RedirectResponse(url="/auth/login", status_code=303)

    # Verify job belongs to this company
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.company_id == user["user"].id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get applications
    applications = db.query(Application).filter(Application.job_id == job_id).all()

    # Load candidates
    for app in applications:
        app.candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()

    # Try to get rankings from gateway
    is_baseline = True
    try:
        candidate_profiles = [
            {"id": app.candidate.id, "name": f"{app.candidate.first_name} {app.candidate.last_name}"}
            for app in applications if app.candidate
        ]

        if candidate_profiles:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.gateway_url}/api/rank-candidates",
                    json={
                        "job_id": job_id,
                        "candidate_profiles": candidate_profiles
                    },
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    is_baseline = data.get("baseline", True)

                    # Create a mapping of candidate_id to score/reason
                    ranked_ids = data.get("ranked_candidate_ids", [])
                    scores = data.get("match_scores", [])
                    reasons = data.get("match_reasons", [])

                    for app in applications:
                        if app.candidate and app.candidate.id in ranked_ids:
                            idx = ranked_ids.index(app.candidate.id)
                            app.match_score = scores[idx] if idx < len(scores) else None
                            app.match_reasons = reasons[idx] if idx < len(reasons) else None

                    # Sort by match_score descending
                    applications.sort(key=lambda a: a.match_score or 0, reverse=True)
    except:
        pass

    return templates.TemplateResponse("recruiter/applicants.html", {
        "request": request,
        "user": user,
        "job": job,
        "ranked_applications": applications,
        "is_baseline": is_baseline
    })


@app.post("/recruiter/applications/{application_id}/status")
async def update_application_status(
    request: Request,
    application_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update application status."""
    user = get_user_context(request, db)

    if not user or user["type"] != "company":
        return RedirectResponse(url="/auth/login", status_code=303)

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Verify job belongs to this company
    job = db.query(Job).filter(
        Job.id == application.job_id,
        Job.company_id == user["user"].id
    ).first()
    if not job:
        raise HTTPException(status_code=403, detail="Not authorized")

    application.status = status
    db.commit()

    return RedirectResponse(url=f"/recruiter/jobs/{job.id}/applicants", status_code=303)


@app.post("/recruiter/jobs/{job_id}/close")
async def close_job(request: Request, job_id: int, db: Session = Depends(get_db)):
    """Close a job posting."""
    user = get_user_context(request, db)

    if not user or user["type"] != "company":
        return RedirectResponse(url="/auth/login", status_code=303)

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.company_id == user["user"].id
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "closed"
    db.commit()

    return RedirectResponse(url="/recruiter/dashboard", status_code=303)


# =============================================================================
# API Root
# =============================================================================

@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {
        "message": "Welcome to JobMatch API",
        "version": "1.0.0",
        "endpoints": {
            "candidates": "/api/candidates",
            "companies": "/api/companies",
            "jobs": "/api/jobs",
            "applications": "/api/applications"
        }
    }
