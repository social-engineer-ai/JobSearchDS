"""Seed the database with sample data."""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from webapp.app.database import SessionLocal
from webapp.app.models import (
    Candidate,
    Company,
    Job,
    Application,
    Skill
)


def seed_skills(db):
    """Create skill taxonomy."""
    skills_data = [
        # Programming
        ("Python", "Programming"),
        ("JavaScript", "Programming"),
        ("Java", "Programming"),
        ("C++", "Programming"),
        ("Go", "Programming"),
        ("Rust", "Programming"),
        ("TypeScript", "Programming"),
        ("SQL", "Programming"),
        # Data Science
        ("Machine Learning", "Data Science"),
        ("Deep Learning", "Data Science"),
        ("TensorFlow", "Data Science"),
        ("PyTorch", "Data Science"),
        ("Pandas", "Data Science"),
        ("Scikit-learn", "Data Science"),
        ("Statistics", "Data Science"),
        # Web Development
        ("React", "Web Development"),
        ("Node.js", "Web Development"),
        ("Django", "Web Development"),
        ("FastAPI", "Web Development"),
        ("HTML/CSS", "Web Development"),
        # Cloud
        ("AWS", "Cloud"),
        ("GCP", "Cloud"),
        ("Azure", "Cloud"),
        ("Docker", "Cloud"),
        ("Kubernetes", "Cloud"),
        # Other
        ("Project Management", "Management"),
        ("Agile", "Management"),
        ("Communication", "Soft Skills"),
        ("Leadership", "Soft Skills"),
    ]

    for name, category in skills_data:
        skill = Skill(name=name, category=category)
        db.add(skill)

    db.commit()
    print(f"Created {len(skills_data)} skills")


def seed_companies(db):
    """Create sample companies."""
    companies_data = [
        {
            "name": "TechCorp Inc.",
            "email": "hr@techcorp.com",
            "password_hash": "password123",
            "description": "Leading technology company specializing in cloud solutions.",
            "industry": "Technology",
            "company_size": "1001-5000",
            "headquarters": "San Francisco, CA",
            "founded_year": 2010,
        },
        {
            "name": "DataDriven Co.",
            "email": "careers@datadriven.com",
            "password_hash": "password123",
            "description": "Data analytics and ML consulting firm.",
            "industry": "Data Analytics",
            "company_size": "201-500",
            "headquarters": "New York, NY",
            "founded_year": 2015,
        },
        {
            "name": "StartupXYZ",
            "email": "jobs@startupxyz.com",
            "password_hash": "password123",
            "description": "Fast-growing B2B SaaS startup.",
            "industry": "Software",
            "company_size": "51-200",
            "headquarters": "Austin, TX",
            "founded_year": 2020,
        },
        {
            "name": "FinanceHub",
            "email": "talent@financehub.com",
            "password_hash": "password123",
            "description": "Fintech company revolutionizing payments.",
            "industry": "Financial Services",
            "company_size": "501-1000",
            "headquarters": "Chicago, IL",
            "founded_year": 2012,
        },
        {
            "name": "HealthTech Solutions",
            "email": "hr@healthtech.com",
            "password_hash": "password123",
            "description": "Healthcare technology innovator.",
            "industry": "Healthcare",
            "company_size": "201-500",
            "headquarters": "Boston, MA",
            "founded_year": 2018,
        },
    ]

    for data in companies_data:
        company = Company(**data)
        db.add(company)

    db.commit()
    print(f"Created {len(companies_data)} companies")


def seed_candidates(db):
    """Create sample candidates."""
    first_names = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", "Ivy", "Jack"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    locations = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Boston, MA", "Chicago, IL"]
    titles = ["Software Engineer", "Data Scientist", "Product Manager", "ML Engineer", "Frontend Developer"]

    for i in range(20):
        candidate = Candidate(
            email=f"candidate{i+1}@example.com",
            password_hash="password123",
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            headline=random.choice(titles),
            location=random.choice(locations),
            years_experience=random.uniform(1, 15),
            current_title=random.choice(titles),
            desired_salary_min=80000 + random.randint(0, 10) * 10000,
            desired_salary_max=120000 + random.randint(0, 10) * 10000,
            open_to_remote=random.choice([True, False]),
            is_open_to_opportunities=True,
        )
        db.add(candidate)

    db.commit()
    print("Created 20 candidates")


def seed_jobs(db):
    """Create sample job postings."""
    companies = db.query(Company).all()

    job_templates = [
        {
            "title": "Software Engineer",
            "category": "Engineering",
            "job_type": "full-time",
            "experience_level": "mid",
            "salary_min": 100000,
            "salary_max": 150000,
        },
        {
            "title": "Senior Software Engineer",
            "category": "Engineering",
            "job_type": "full-time",
            "experience_level": "senior",
            "salary_min": 150000,
            "salary_max": 200000,
        },
        {
            "title": "Data Scientist",
            "category": "Data Science",
            "job_type": "full-time",
            "experience_level": "mid",
            "salary_min": 120000,
            "salary_max": 160000,
        },
        {
            "title": "Machine Learning Engineer",
            "category": "Data Science",
            "job_type": "full-time",
            "experience_level": "senior",
            "salary_min": 140000,
            "salary_max": 190000,
        },
        {
            "title": "Product Manager",
            "category": "Product",
            "job_type": "full-time",
            "experience_level": "mid",
            "salary_min": 130000,
            "salary_max": 170000,
        },
        {
            "title": "Frontend Developer",
            "category": "Engineering",
            "job_type": "full-time",
            "experience_level": "entry",
            "salary_min": 80000,
            "salary_max": 110000,
        },
        {
            "title": "DevOps Engineer",
            "category": "Engineering",
            "job_type": "full-time",
            "experience_level": "mid",
            "salary_min": 110000,
            "salary_max": 150000,
        },
    ]

    locations = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Remote"]

    for company in companies:
        for template in random.sample(job_templates, k=random.randint(2, 5)):
            job = Job(
                company_id=company.id,
                title=template["title"],
                description=f"We are looking for a talented {template['title']} to join our team at {company.name}. "
                           f"This is an exciting opportunity to work on cutting-edge projects.",
                requirements=f"- {template['experience_level'].title()} level experience\n"
                            f"- Strong problem-solving skills\n"
                            f"- Excellent communication abilities",
                responsibilities="- Design and implement solutions\n"
                                "- Collaborate with cross-functional teams\n"
                                "- Mentor junior team members",
                category=template["category"],
                job_type=template["job_type"],
                experience_level=template["experience_level"],
                location=random.choice(locations),
                is_remote=random.choice([True, False]),
                salary_min=template["salary_min"],
                salary_max=template["salary_max"],
                status="open",
                posted_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            )
            db.add(job)

    db.commit()
    print(f"Created jobs for {len(companies)} companies")


def seed_applications(db):
    """Create sample applications."""
    candidates = db.query(Candidate).all()
    jobs = db.query(Job).filter(Job.status == "open").all()

    statuses = ["submitted", "reviewed", "shortlisted", "interviewing", "rejected"]

    for candidate in candidates:
        # Each candidate applies to 1-5 random jobs
        applied_jobs = random.sample(jobs, k=min(random.randint(1, 5), len(jobs)))
        for job in applied_jobs:
            application = Application(
                candidate_id=candidate.id,
                job_id=job.id,
                cover_letter=f"I am excited to apply for the {job.title} position...",
                status=random.choice(statuses),
            )
            db.add(application)

    db.commit()
    print(f"Created applications for {len(candidates)} candidates")


def seed_db():
    """Run all seed functions."""
    print("Seeding database...")

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Company).first():
            print("Database already has data. Skipping seed.")
            return

        seed_skills(db)
        seed_companies(db)
        seed_candidates(db)
        seed_jobs(db)
        seed_applications(db)

        print("Database seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
