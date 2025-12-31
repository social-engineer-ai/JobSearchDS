# JobMatch Platform - Implementation Plan

## Overview

Build an educational job search platform with clean microservices architecture where:
- Baseline services use simple rule-based logic
- Students can replace any service by changing ONE config line
- Dashboard shows real-time impact of ML improvements

---

## Phase 0: Project Foundation (Current)

### Goal
Set up project structure, tooling, and development environment.

### Deliverables

#### 0.1 Project Structure
```
JobSearch_BADM576/
├── docker-compose.yml          # Orchestrates all services
├── Makefile                    # Build commands
├── README.md                   # Project documentation
├── requirements.txt            # Shared Python dependencies
├── .env.example                # Environment template
├── config/
│   └── services.yaml           # ML service endpoints (students edit this)
├── webapp/                     # Main web application
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI entry point
│   │   ├── config.py           # Configuration loader
│   │   ├── database.py         # Database connection
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── routers/            # API routes
│   │   ├── services/           # Business logic
│   │   └── templates/          # Jinja2 templates (if using SSR)
│   └── tests/
├── gateway/                    # Service gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── router.py           # Routes to ML services
│       ├── fallback.py         # Baseline implementations
│       └── config.py           # Hot-reload config
├── services/                   # Baseline ML services
│   ├── job_recommender/
│   ├── salary_predictor/
│   ├── candidate_ranker/
│   ├── resume_parser/
│   ├── demand_forecaster/
│   └── candidate_segmenter/
├── dashboard/                  # Monitoring dashboard
│   ├── Dockerfile
│   └── app/
├── scripts/
│   ├── init_db.py              # Database initialization
│   ├── seed_data.py            # Sample data loader
│   └── smoke_test.py           # End-to-end tests
├── data/
│   └── seed/                   # Sample CSV data
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   ├── architecture.md
│   └── notes/
└── tests/
    └── integration/
```

#### 0.2 Files to Create
1. `Makefile` - Build/run commands
2. `docker-compose.yml` - Service orchestration
3. `README.md` - Project documentation
4. `.env.example` - Environment template
5. `config/services.yaml` - Service configuration
6. `requirements.txt` - Base dependencies

#### 0.3 Risks/Assumptions
- Assuming Docker is available on development machine
- Using PostgreSQL (can fallback to SQLite for simplicity)
- Jinja2 templates for MVP frontend (React can come later)

---

## Phase 1: Database & Core Models

### Goal
Define database schema and SQLAlchemy models for all core entities.

### Deliverables

#### 1.1 Database Models
- `Candidate` - job seekers with profiles, skills, preferences
- `Company` - employers with industry, size, culture info
- `Job` - job postings with requirements, salary range
- `Application` - links candidates to jobs with status tracking
- `Skill` - normalized skill taxonomy
- `Interaction` - logs user actions for analytics

#### 1.2 Files to Create
1. `webapp/app/models/candidate.py`
2. `webapp/app/models/company.py`
3. `webapp/app/models/job.py`
4. `webapp/app/models/application.py`
5. `webapp/app/models/skill.py`
6. `webapp/app/models/interaction.py`
7. `webapp/app/database.py`
8. `scripts/init_db.py`

#### 1.3 Pydantic Schemas
- Request/response schemas for all entities
- Matches ML service contracts exactly

---

## Phase 2: Web Application Core

### Goal
Build the main FastAPI application with candidate and recruiter interfaces.

### Deliverables

#### 2.1 Candidate Features
- Browse/search jobs
- View job details
- Submit applications
- View application status
- Profile management

#### 2.2 Recruiter Features
- Post new jobs
- View applicants per job
- Update application status
- Search candidates
- Company profile management

#### 2.3 API Routes
1. `routers/candidates.py` - Candidate CRUD + profile
2. `routers/companies.py` - Company CRUD
3. `routers/jobs.py` - Job CRUD + search
4. `routers/applications.py` - Application workflow
5. `routers/auth.py` - Simple authentication

#### 2.4 Templates (MVP)
- Home page
- Job listing page
- Job detail page
- Candidate dashboard
- Recruiter dashboard
- Application form

---

## Phase 3: Service Gateway

### Goal
Build the routing layer that forwards requests to ML services with fallback logic.

### Deliverables

#### 3.1 Gateway Features
- Read `config/services.yaml` for endpoint URLs
- Hot-reload config without restart
- Timeout handling (default 5s)
- Fallback to baseline if external endpoint fails
- Request/response logging for dashboard

#### 3.2 Files to Create
1. `gateway/app/main.py` - FastAPI app
2. `gateway/app/config.py` - Config loader with hot-reload
3. `gateway/app/router.py` - Service routing logic
4. `gateway/app/fallback.py` - All baseline implementations
5. `gateway/app/logging.py` - Request/response logging

#### 3.3 Service Endpoints
```
POST /api/recommend      -> job_recommender
POST /api/predict-salary -> salary_predictor
POST /api/rank-candidates -> candidate_ranker
POST /api/parse-resume   -> resume_parser
POST /api/forecast-demand -> demand_forecaster
POST /api/segment-candidates -> candidate_segmenter
```

---

## Phase 4: Baseline Services

### Goal
Implement simple rule-based versions of each ML service.

### Deliverables

#### 4.1 Job Recommender (Baseline)
- Returns most recent jobs matching candidate's preferred category
- No personalization

#### 4.2 Salary Predictor (Baseline)
- Returns industry average based on job title lookup table
- Wide confidence interval

#### 4.3 Candidate Ranker (Baseline)
- FIFO ordering by application date
- No skill matching

#### 4.4 Resume Parser (Baseline)
- Exact keyword matching against predefined skill list
- Simple regex for experience years

#### 4.5 Demand Forecaster (Baseline)
- Returns current job count (no actual forecasting)
- Static response

#### 4.6 Candidate Segmenter (Baseline)
- Groups by primary job category only
- No clustering

---

## Phase 5: Dashboard Service

### Goal
Build real-time monitoring dashboard showing service health and business metrics.

### Deliverables

#### 5.1 Service Health Panel
- Endpoint status (up/down/degraded)
- Response latency (p50, p95, p99)
- Error rate and fallback frequency
- Request volume per service

#### 5.2 Business Metrics Panel
- Application rate
- Time to first application
- Jobs viewed per session
- Recruiter: time to shortlist

#### 5.3 Files to Create
1. `dashboard/app/main.py` - FastAPI app
2. `dashboard/app/metrics.py` - Metrics collection
3. `dashboard/app/templates/` - Dashboard UI

---

## Phase 6: Integration & Testing

### Goal
End-to-end testing and documentation.

### Deliverables

#### 6.1 Tests
- Unit tests for each service
- Integration tests for gateway
- Smoke test script

#### 6.2 Documentation
- README with setup instructions
- Architecture diagram
- API documentation (auto-generated from FastAPI)

---

## Implementation Order

| Step | Description | Est. Files |
|------|-------------|------------|
| 0.1 | Project structure + Makefile + docker-compose | 5 |
| 0.2 | README + .env.example + config/services.yaml | 3 |
| 1.1 | Database models + init script | 8 |
| 1.2 | Pydantic schemas | 6 |
| 2.1 | FastAPI app skeleton + config | 4 |
| 2.2 | API routes (CRUD) | 5 |
| 2.3 | Templates (MVP frontend) | 8 |
| 3.1 | Gateway service | 5 |
| 4.1 | Baseline services (6 services) | 12 |
| 5.1 | Dashboard service | 4 |
| 6.1 | Tests + smoke script | 4 |

**Total: ~64 files**

---

## Decision: Where to Start?

I recommend implementing in this order:
1. **Phase 0** first (project structure) - enables everything else
2. **Phase 1** next (database) - foundation for data
3. **Phase 2** (web app) - the main product
4. **Phase 3** (gateway) - enables service swapping
5. **Phase 4** (baseline services) - makes platform functional
6. **Phase 5** (dashboard) - enables observability
7. **Phase 6** (testing) - ensures quality

---

**Ready to proceed with Phase 0?**
