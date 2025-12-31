# JobMatch Platform

An educational job search platform for teaching ML/DS concepts through hands-on problem-solving.

## Overview

JobMatch is a "deliberately old school" job search platform with baseline rule-based services. Students analyze the platform's pain points, then develop and deploy ML models to replace the baseline logic, observing real-time improvements through the integrated dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Application                          │
│                    (Candidate & Recruiter UI)                   │
│                         Port 8000                               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Service Gateway                           │
│            (Routing, Fallback, Logging)                         │
│                         Port 8001                               │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Job Recommender│    │Salary Predictor│    │Candidate Ranker│
│   Port 5001   │    │   Port 5002    │    │   Port 5003    │
└───────────────┘    └───────────────┘    └───────────────┘

┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Resume Parser │    │Demand Forecast │    │Cand. Segmenter│
│   Port 5004   │    │   Port 5005    │    │   Port 5006   │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd JobSearch_BADM576

# Install dependencies
py -m pip install -r requirements.txt

# Initialize database
py scripts/init_db.py

# Seed sample data
py scripts/seed_data.py
```

### Running Locally

**Option 1: Using Python directly**

```bash
# Terminal 1: Start the gateway
py -m uvicorn gateway.app.main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2: Start the webapp
py -m uvicorn webapp.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Start the dashboard
py -m uvicorn dashboard.app.main:app --host 0.0.0.0 --port 8002 --reload
```

**Option 2: Using Make commands**

```bash
make dev-webapp     # Start webapp
make dev-gateway    # Start gateway
make dev-dashboard  # Start dashboard
```

**Option 3: Using Docker**

```bash
make run
```

### Access Points
- **Web Application:** http://localhost:8000
- **Service Gateway:** http://localhost:8001
- **Dashboard:** http://localhost:8002

### Running Smoke Tests

```bash
# Verify all services are running correctly
py scripts/smoke_test.py
```

### Sample Users (after seeding)

Register new accounts or use these test credentials:

**Candidates:**
- Register at `/auth/register` selecting "Candidate"
- Browse jobs, apply to positions, view recommendations

**Recruiters:**
- Register at `/auth/register` selecting "Recruiter"
- Create a company during registration
- Post jobs, view applicants, see ML-powered rankings

## For Students

### Deploying Your ML Model

1. Develop your ML model in Jupyter notebooks using the provided datasets
2. Deploy to Hugging Face Spaces (or similar hosting)
3. Edit `config/services.yaml` - change ONE line:

```yaml
services:
  job_recommender:
    endpoint: "https://your-username-job-recommender.hf.space/recommend"  # Your endpoint
```

4. Save the file - the gateway hot-reloads automatically
5. Check the dashboard to observe improvements

### ML Services Available for Improvement

| Service | Pain Point | Baseline |
|---------|------------|----------|
| Job Recommender | Irrelevant job suggestions | Most recent jobs |
| Salary Predictor | No salary expectations | Industry average |
| Candidate Ranker | Unqualified applicants first | FIFO order |
| Resume Parser | Missed skills | Keyword matching |
| Demand Forecaster | No market insights | Current count only |
| Candidate Segmenter | No talent pools | Category tags |

## Project Structure

```
JobSearch_BADM576/
├── config/
│   └── services.yaml       # ML service endpoints (EDIT THIS)
├── webapp/                 # Main web application
├── gateway/                # Service gateway with fallback
├── services/               # Baseline ML services
│   ├── job_recommender/
│   ├── salary_predictor/
│   ├── candidate_ranker/
│   ├── resume_parser/
│   ├── demand_forecaster/
│   └── candidate_segmenter/
├── dashboard/              # Monitoring dashboard
├── scripts/                # Utility scripts
├── data/                   # SQLite database & seed data
├── docs/                   # Documentation
└── tests/                  # Test suites
```

## Commands

```bash
make setup          # Install all dependencies
make run            # Start with Docker
make dev-webapp     # Start webapp (development)
make dev-gateway    # Start gateway (development)
make dev-services   # Start baseline services
make test           # Run all tests
make smoke          # Run smoke tests
make lint           # Check code style
make reset-db       # Reset database with fresh data
```

## API Documentation

When running, visit:
- Webapp API docs: http://localhost:8000/docs
- Gateway API docs: http://localhost:8001/docs

## License

Educational use only - BADM 576 Course Project
