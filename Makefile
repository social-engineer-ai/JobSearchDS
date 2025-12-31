# JobMatch Platform - Makefile
# Use 'py' command for Python on Windows

.PHONY: setup run test lint smoke clean dev-webapp dev-gateway dev-services

# =============================================================================
# Setup
# =============================================================================

setup:
	py -m pip install -r requirements.txt
	py -m pip install -r webapp/requirements.txt
	py -m pip install -r gateway/requirements.txt
	py scripts/init_db.py

setup-dev:
	py -m pip install -r requirements.txt
	py -m pip install -r requirements-dev.txt

# =============================================================================
# Run Services
# =============================================================================

run:
	docker-compose up --build

run-local:
	@echo "Starting all services locally..."
	@start /B py -m uvicorn webapp.app.main:app --host 0.0.0.0 --port 8000 --reload
	@start /B py -m uvicorn gateway.app.main:app --host 0.0.0.0 --port 8001 --reload
	@start /B py -m uvicorn dashboard.app.main:app --host 0.0.0.0 --port 8002 --reload
	@echo "Services started: webapp(8000), gateway(8001), dashboard(8002)"

dev-webapp:
	py -m uvicorn webapp.app.main:app --host 0.0.0.0 --port 8000 --reload

dev-gateway:
	py -m uvicorn gateway.app.main:app --host 0.0.0.0 --port 8001 --reload

dev-dashboard:
	py -m uvicorn dashboard.app.main:app --host 0.0.0.0 --port 8002 --reload

dev-services:
	@echo "Starting baseline ML services..."
	@start /B py -m uvicorn services.job_recommender.app.main:app --port 5001
	@start /B py -m uvicorn services.salary_predictor.app.main:app --port 5002
	@start /B py -m uvicorn services.candidate_ranker.app.main:app --port 5003
	@start /B py -m uvicorn services.resume_parser.app.main:app --port 5004
	@start /B py -m uvicorn services.demand_forecaster.app.main:app --port 5005
	@start /B py -m uvicorn services.candidate_segmenter.app.main:app --port 5006

# =============================================================================
# Database
# =============================================================================

init-db:
	py scripts/init_db.py

seed-db:
	py scripts/seed_data.py

reset-db:
	del /F data\jobmatch.db 2>nul || true
	py scripts/init_db.py
	py scripts/seed_data.py

# =============================================================================
# Testing
# =============================================================================

test:
	py -m pytest tests/ -v

test-webapp:
	py -m pytest webapp/tests/ -v

test-gateway:
	py -m pytest gateway/tests/ -v

test-integration:
	py -m pytest tests/integration/ -v

smoke:
	py scripts/smoke_test.py

# =============================================================================
# Code Quality
# =============================================================================

lint:
	py -m flake8 webapp/ gateway/ services/ dashboard/ --max-line-length=100
	py -m black --check webapp/ gateway/ services/ dashboard/

format:
	py -m black webapp/ gateway/ services/ dashboard/

# =============================================================================
# Cleanup
# =============================================================================

clean:
	del /S /Q __pycache__ 2>nul || true
	del /S /Q *.pyc 2>nul || true
	del /S /Q .pytest_cache 2>nul || true
