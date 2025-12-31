# JobMatch Platform - Architecture Document

## Executive Summary

JobMatch is an educational job search platform designed for teaching ML/DS concepts through hands-on problem-solving. The platform uses a microservices architecture with baseline rule-based services that students can replace with their own ML models to observe real-time improvements.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                    │
│   │  Candidate  │    │  Recruiter  │    │  Dashboard  │                    │
│   │    Views    │    │    Views    │    │  (Monitor)  │                    │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                    │
│          │                  │                  │                            │
└──────────┼──────────────────┼──────────────────┼────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WEB APPLICATION                                    │
│                          (FastAPI - Port 8000)                              │
│                                                                             │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  Routes: Auth | Jobs | Candidates | Recruiters | Applications    │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  Templates: Jinja2 HTML | Session Auth | Form Handling           │     │
│   └──────────────────────────────────────────────────────────────────┘     │
│   ┌──────────────────────────────────────────────────────────────────┐     │
│   │  Database: SQLite + SQLAlchemy ORM                               │     │
│   └──────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  │ HTTP (ML Service Calls)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SERVICE GATEWAY                                     │
│                         (FastAPI - Port 8001)                               │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │  Hot-Reload Config (services.yaml) | Routing | Metrics | Fallback  │   │
│   └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Students edit config/services.yaml to point to their ML endpoints         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  Job Recommender  │ │ Salary Predictor  │ │ Candidate Ranker  │
│    Port 5001      │ │    Port 5002      │ │    Port 5003      │
│                   │ │                   │ │                   │
│ Baseline: Recent  │ │ Baseline: Lookup  │ │ Baseline: FIFO    │
│ ML: Collaborative │ │ ML: Regression    │ │ ML: Classification│
└───────────────────┘ └───────────────────┘ └───────────────────┘

┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  Resume Parser    │ │ Demand Forecaster │ │ Cand. Segmenter   │
│    Port 5004      │ │    Port 5005      │ │    Port 5006      │
│                   │ │                   │ │                   │
│ Baseline: Keyword │ │ Baseline: Flat    │ │ Baseline: Category│
│ ML: NER/NLP       │ │ ML: Time Series   │ │ ML: Clustering    │
└───────────────────┘ └───────────────────┘ └───────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         MONITORING DASHBOARD                                 │
│                          (FastAPI - Port 8002)                              │
│                                                                             │
│   Real-time metrics | Service health | Baseline vs ML comparison            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Web Application (`webapp/`)

The main user-facing application built with FastAPI and Jinja2 templates.

**Technology Stack:**
- FastAPI (web framework)
- Jinja2 (templating)
- SQLAlchemy (ORM)
- SQLite (database)
- Passlib/PBKDF2 (password hashing)

**Directory Structure:**
```
webapp/
├── app/
│   ├── main.py              # FastAPI app, all web routes
│   ├── config.py            # Settings management
│   ├── database.py          # SQLAlchemy setup
│   ├── models/              # Database models
│   │   ├── candidate.py     # Candidate model
│   │   ├── company.py       # Company model
│   │   ├── job.py           # Job model
│   │   ├── application.py   # Application model
│   │   ├── skill.py         # Skill model
│   │   └── interaction.py   # User interaction tracking
│   ├── schemas/             # Pydantic schemas
│   │   ├── candidate.py
│   │   ├── company.py
│   │   ├── job.py
│   │   └── application.py
│   ├── routers/             # API routers
│   │   ├── auth.py          # Authentication
│   │   ├── candidates.py    # Candidate CRUD
│   │   ├── companies.py     # Company CRUD
│   │   ├── jobs.py          # Job CRUD
│   │   └── applications.py  # Application CRUD
│   ├── services/
│   │   └── auth.py          # Password hashing
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html        # Base layout
│       ├── index.html       # Home page
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── jobs/
│       │   ├── list.html
│       │   ├── detail.html
│       │   └── apply.html
│       ├── candidate/
│       │   ├── dashboard.html
│       │   └── profile.html
│       └── recruiter/
│           ├── dashboard.html
│           ├── applicants.html
│           └── post_job.html
```

**Key Features:**
- Session-based authentication (cookies)
- Candidate registration and profile management
- Job browsing, search, and filtering
- Job application submission
- Recruiter job posting and applicant management
- Integration with gateway for ML predictions

---

### 2. Service Gateway (`gateway/`)

The routing layer that directs requests to ML services with automatic fallback.

**Technology Stack:**
- FastAPI
- HTTPX (async HTTP client)
- PyYAML (configuration)

**Directory Structure:**
```
gateway/
├── app/
│   ├── main.py       # FastAPI app, ML endpoints
│   ├── config.py     # Hot-reload configuration
│   ├── router.py     # Service routing logic
│   └── fallback.py   # Baseline implementations
```

**Key Features:**
- Hot-reload configuration (edit `services.yaml`, no restart needed)
- Automatic fallback to baseline when ML services fail
- Request metrics and latency tracking
- Service health monitoring

**Configuration (`config/services.yaml`):**
```yaml
services:
  job_recommender:
    endpoint: "http://localhost:5001/recommend"
    timeout: 5.0
    enabled: true
  salary_predictor:
    endpoint: "http://localhost:5002/predict"
    timeout: 5.0
    enabled: true
  # ... more services
```

---

### 3. Baseline ML Services (`services/`)

Six microservices providing baseline (rule-based) implementations.

| Service | Port | Baseline Logic | ML Opportunity |
|---------|------|----------------|----------------|
| Job Recommender | 5001 | Most recent jobs | Collaborative filtering, content-based |
| Salary Predictor | 5002 | Industry average lookup | Regression models |
| Candidate Ranker | 5003 | FIFO ordering | Classification, ranking models |
| Resume Parser | 5004 | Keyword matching | NER, NLP extraction |
| Demand Forecaster | 5005 | Flat projection | Time series forecasting |
| Candidate Segmenter | 5006 | Category grouping | K-means, clustering |

**Each Service Structure:**
```
services/{service_name}/
└── app/
    ├── __init__.py
    └── main.py    # FastAPI app with /health and main endpoint
```

---

### 4. Monitoring Dashboard (`dashboard/`)

Real-time monitoring UI for service health and performance.

**Directory Structure:**
```
dashboard/
└── app/
    ├── main.py
    └── templates/
        └── dashboard.html
```

**Features:**
- Gateway connection status
- Per-service health indicators
- Request counts and failure rates
- Fallback rate tracking
- Auto-refresh every 5 seconds

---

## Database Schema

```
┌─────────────────┐       ┌─────────────────┐
│    Candidate    │       │     Company     │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ email           │       │ email           │
│ password_hash   │       │ password_hash   │
│ first_name      │       │ name            │
│ last_name       │       │ description     │
│ headline        │       │ industry        │
│ summary         │       │ company_size    │
│ location        │       │ headquarters    │
│ phone           │       │ website         │
│ current_title   │       │ founded_year    │
│ current_company │       │ is_active       │
│ years_experience│       │ created_at      │
│ resume_text     │       │ updated_at      │
│ desired_salary  │       └────────┬────────┘
│ is_active       │                │
│ created_at      │                │ 1:N
└────────┬────────┘                │
         │                         ▼
         │ 1:N            ┌─────────────────┐
         │                │       Job       │
         │                ├─────────────────┤
         │                │ id              │
         │                │ company_id (FK) │
         │                │ title           │
         │                │ description     │
         │                │ requirements    │
         │                │ responsibilities│
         │                │ location        │
         │                │ salary_min/max  │
         │                │ job_type        │
         │                │ experience_level│
         │                │ is_remote       │
         │                │ status          │
         │                │ posted_at       │
         │                └────────┬────────┘
         │                         │
         │ N:M (via Application)   │ 1:N
         │                         │
         ▼                         ▼
┌─────────────────────────────────────────┐
│              Application                │
├─────────────────────────────────────────┤
│ id                                      │
│ candidate_id (FK)                       │
│ job_id (FK)                             │
│ status (submitted/reviewed/shortlisted) │
│ cover_letter                            │
│ resume_version                          │
│ match_score                             │
│ created_at                              │
│ updated_at                              │
└─────────────────────────────────────────┘

┌─────────────────┐       ┌─────────────────┐
│      Skill      │       │   Interaction   │
├─────────────────┤       ├─────────────────┤
│ id              │       │ id              │
│ name            │       │ candidate_id    │
│ category        │       │ job_id          │
│ is_active       │       │ interaction_type│
└─────────────────┘       │ created_at      │
                          └─────────────────┘
```

---

## API Endpoints

### Web Application (Port 8000)

**Authentication:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/login` | Login page |
| POST | `/auth/login/candidate` | Candidate login |
| POST | `/auth/login/company` | Company login |
| GET | `/auth/register` | Registration page |
| POST | `/auth/register/candidate` | Register candidate |
| POST | `/auth/register/company` | Register company |
| GET | `/auth/logout` | Logout |

**Jobs:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | Job listing with filters |
| GET | `/jobs/{id}` | Job detail + salary prediction |
| GET | `/jobs/{id}/apply` | Application form |
| POST | `/jobs/{id}/apply` | Submit application |

**Candidate:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/candidate/dashboard` | Dashboard + recommendations |
| GET | `/candidate/profile` | Profile edit form |
| POST | `/candidate/profile` | Update profile |

**Recruiter:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recruiter/dashboard` | Dashboard + job stats |
| GET | `/recruiter/post-job` | Job posting form |
| POST | `/recruiter/post-job` | Create job |
| GET | `/recruiter/jobs/{id}/applicants` | View ranked applicants |
| POST | `/recruiter/applications/{id}/status` | Update application status |

### Service Gateway (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Gateway + service health |
| GET | `/metrics` | Request metrics |
| GET | `/config` | Current configuration |
| POST | `/api/recommend` | Job recommendations |
| POST | `/api/predict-salary` | Salary prediction |
| POST | `/api/rank-candidates` | Candidate ranking |
| POST | `/api/parse-resume` | Resume parsing |
| POST | `/api/forecast-demand` | Demand forecasting |
| POST | `/api/segment-candidates` | Candidate segmentation |
| POST | `/admin/reload-config` | Force config reload |

---

## ML Service Contracts

### 1. Job Recommender
```json
// Input
{
  "candidate_id": 123,
  "candidate_profile": { ... },
  "interaction_history": [ ... ],
  "num_recommendations": 10
}

// Output
{
  "job_ids": [1, 2, 3],
  "scores": [0.95, 0.87, 0.82],
  "explanations": ["Based on your Python skills", ...],
  "baseline": false
}
```

### 2. Salary Predictor
```json
// Input
{
  "job_title": "Software Engineer",
  "location": "San Francisco, CA",
  "company_size": "501-1000",
  "industry": "Technology",
  "required_skills": ["Python", "AWS"],
  "experience_range": "3-5 years"
}

// Output
{
  "predicted_salary": 145000,
  "confidence_interval": [125000, 165000],
  "comparable_jobs": [ ... ],
  "baseline": false
}
```

### 3. Candidate Ranker
```json
// Input
{
  "job_id": 456,
  "job_requirements": { ... },
  "candidate_profiles": [
    { "id": 1, "skills": [...], ... },
    { "id": 2, "skills": [...], ... }
  ],
  "historical_hires": [ ... ]
}

// Output
{
  "ranked_candidate_ids": [2, 1],
  "match_scores": [92, 78],
  "match_reasons": ["Strong Python skills", "Good culture fit"],
  "baseline": false
}
```

### 4. Resume Parser
```json
// Input
{
  "resume_text": "Experienced Python developer...",
  "resume_format": "text"
}

// Output
{
  "skills": ["Python", "Machine Learning", "AWS"],
  "experience_years": 5,
  "education": { "degree": "MS", "field": "Computer Science" },
  "work_history": [ ... ],
  "summary": "...",
  "baseline": false
}
```

### 5. Demand Forecaster
```json
// Input
{
  "skill_category": "Machine Learning",
  "industry": "Technology",
  "location": "United States",
  "historical_postings": [ ... ],
  "forecast_horizon": 6
}

// Output
{
  "forecast_periods": ["2024-01", "2024-02", ...],
  "predicted_demand": [150, 165, 180, ...],
  "confidence_bounds": [[140, 160], [150, 180], ...],
  "baseline": false
}
```

### 6. Candidate Segmenter
```json
// Input
{
  "candidate_profiles": [ ... ],
  "feature_set": ["skills", "experience", "location"],
  "num_clusters": 5
}

// Output
{
  "cluster_assignments": [0, 2, 1, 0, 2],
  "cluster_descriptions": [
    "Senior Backend Engineers",
    "Junior Full-Stack Developers",
    ...
  ],
  "cluster_centroids": [ ... ],
  "baseline": false
}
```

---

## Project Structure

```
JobSearch_BADM576/
├── config/
│   └── services.yaml        # ML service endpoints (STUDENTS EDIT THIS)
├── data/
│   └── jobmatch.db          # SQLite database
├── docs/
│   ├── ARCHITECTURE.md      # This document
│   ├── IMPLEMENTATION_PLAN.md
│   └── notes/               # Session notes
├── webapp/                  # Main web application
├── gateway/                 # Service gateway
├── services/                # 6 baseline ML services
│   ├── job_recommender/
│   ├── salary_predictor/
│   ├── candidate_ranker/
│   ├── resume_parser/
│   ├── demand_forecaster/
│   └── candidate_segmenter/
├── dashboard/               # Monitoring UI
├── scripts/
│   ├── init_db.py          # Database initialization
│   ├── seed_data.py        # Sample data seeding
│   └── smoke_test.py       # End-to-end tests
├── tests/
│   ├── test_auth.py        # Auth unit tests
│   └── test_fallback.py    # Fallback unit tests
├── requirements.txt
├── Makefile
├── docker-compose.yml
├── README.md
└── CLAUDE.md
```

---

## Running the Platform

### Prerequisites
- Python 3.11+
- pip

### Quick Start

```bash
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Initialize database
py scripts/init_db.py

# 3. Seed sample data
py scripts/seed_data.py

# 4. Start services (3 terminals)

# Terminal 1: Gateway
py -m uvicorn gateway.app.main:app --port 8001 --reload

# Terminal 2: Webapp
py -m uvicorn webapp.app.main:app --port 8000 --reload

# Terminal 3: Dashboard
py -m uvicorn dashboard.app.main:app --port 8002 --reload
```

### Access Points
- **Web Application:** http://localhost:8000
- **Service Gateway:** http://localhost:8001
- **Dashboard:** http://localhost:8002

### Test Credentials
- **Candidate:** `candidate1@example.com` / `password123`
- **Recruiter:** `hr@techcorp.com` / `password123`

---

## For Students: Replacing Baseline with ML

### Step 1: Develop Your Model
Use the provided datasets and Jupyter notebooks to develop your ML model.

### Step 2: Deploy Your Model
Deploy to Hugging Face Spaces, AWS Lambda, or any HTTP endpoint.

### Step 3: Update Configuration
Edit `config/services.yaml`:

```yaml
services:
  job_recommender:
    endpoint: "https://your-username-job-recommender.hf.space/recommend"
    timeout: 10.0
    enabled: true
```

### Step 4: Observe Improvements
- Check the Dashboard (http://localhost:8002)
- Watch the "External Success Rate" increase
- Compare baseline vs ML performance

### Step 5: Iterate
- Improve your model
- Update the endpoint
- Measure improvements

---

## Testing

### Unit Tests
```bash
py -m pytest tests/ -v
```

### Smoke Tests
```bash
# Requires services to be running
py scripts/smoke_test.py
```

### Test Coverage
- 27 unit tests (auth + fallback)
- 13 smoke tests (services + pages)

---

## Security Considerations

- Passwords hashed with PBKDF2-SHA256
- Session-based authentication with HTTP-only cookies
- Environment variables for secrets (`.env` file)
- No hardcoded credentials in code

---

## Future Enhancements

1. **Phase 6:** Add WebSocket for real-time dashboard updates
2. **Phase 7:** Implement A/B testing framework
3. **Phase 8:** Add model versioning and rollback
4. **Phase 9:** Kubernetes deployment configuration
5. **Phase 10:** Add comprehensive logging and observability

---

*Document generated: 2025-12-31*
*Repository: https://github.com/social-engineer-ai/JobSearchDS*
