"""JobMatch Service Gateway - Main Entry Point."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging

from .config import get_config
from .router import get_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="JobMatch Service Gateway",
    description="Routes requests to ML services with fallback support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize configuration on startup."""
    config = get_config()
    config.load()
    logger.info("Gateway started with configuration loaded")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "JobMatch Gateway",
        "version": "1.0.0",
        "endpoints": {
            "recommend": "/api/recommend",
            "predict-salary": "/api/predict-salary",
            "rank-candidates": "/api/rank-candidates",
            "parse-resume": "/api/parse-resume",
            "forecast-demand": "/api/forecast-demand",
            "segment-candidates": "/api/segment-candidates",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    router = get_router()
    return {
        "status": "healthy",
        "service": "gateway",
        "services": router.get_health()
    }


@app.get("/metrics")
async def metrics():
    """Get service metrics."""
    router = get_router()
    return router.get_metrics()


@app.get("/config")
async def config():
    """Get current configuration (endpoints only, no secrets)."""
    config = get_config()
    return {
        "services": {
            name: {
                "endpoint": svc.endpoint,
                "enabled": svc.enabled,
                "timeout": svc.timeout
            }
            for name, svc in config.services.items()
        },
        "gateway": config.gateway.model_dump(),
        "last_loaded": config.last_loaded.isoformat() if config.last_loaded else None
    }


# =============================================================================
# ML Service Endpoints
# =============================================================================

@app.post("/api/recommend")
async def recommend_jobs(request: Dict[str, Any]):
    """
    Job Recommender Service.

    Input: { candidate_id, candidate_profile, interaction_history, num_recommendations }
    Output: { job_ids: [], scores: [], explanations: [] }
    """
    router = get_router()
    return await router.call_service("job_recommender", request)


@app.post("/api/predict-salary")
async def predict_salary(request: Dict[str, Any]):
    """
    Salary Predictor Service.

    Input: { job_title, location, company_size, industry, required_skills, experience_range }
    Output: { predicted_salary, confidence_interval: [low, high], comparable_jobs: [] }
    """
    router = get_router()
    return await router.call_service("salary_predictor", request)


@app.post("/api/rank-candidates")
async def rank_candidates(request: Dict[str, Any]):
    """
    Candidate Ranker Service.

    Input: { job_id, job_requirements, candidate_profiles: [], historical_hires: [] }
    Output: { ranked_candidate_ids: [], match_scores: [], match_reasons: [] }
    """
    router = get_router()
    return await router.call_service("candidate_ranker", request)


@app.post("/api/parse-resume")
async def parse_resume(request: Dict[str, Any]):
    """
    Resume Parser Service.

    Input: { resume_text, resume_format }
    Output: { skills: [], experience_years, education: {}, work_history: [], summary }
    """
    router = get_router()
    return await router.call_service("resume_parser", request)


@app.post("/api/forecast-demand")
async def forecast_demand(request: Dict[str, Any]):
    """
    Demand Forecaster Service.

    Input: { skill_category, industry, location, historical_postings: [], forecast_horizon }
    Output: { forecast_periods: [], predicted_demand: [], confidence_bounds: [] }
    """
    router = get_router()
    return await router.call_service("demand_forecaster", request)


@app.post("/api/segment-candidates")
async def segment_candidates(request: Dict[str, Any]):
    """
    Candidate Segmenter Service.

    Input: { candidate_profiles: [], feature_set, num_clusters (optional) }
    Output: { cluster_assignments: [], cluster_descriptions: [], cluster_centroids: [] }
    """
    router = get_router()
    return await router.call_service("candidate_segmenter", request)


# =============================================================================
# Admin Endpoints
# =============================================================================

@app.post("/admin/reload-config")
async def reload_config():
    """Force reload of service configuration."""
    config = get_config()
    config.load()
    return {"status": "reloaded", "last_loaded": config.last_loaded.isoformat()}
