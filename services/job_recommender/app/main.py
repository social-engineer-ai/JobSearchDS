"""Job Recommender Baseline Service.

This baseline returns most recent jobs without personalization.
Students will replace this with ML-based recommendations.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Job Recommender Service (Baseline)",
    description="Returns most recent jobs - no ML personalization",
    version="1.0.0"
)


class RecommendRequest(BaseModel):
    candidate_id: int
    candidate_profile: Optional[Dict[str, Any]] = None
    interaction_history: Optional[List[Dict[str, Any]]] = None
    num_recommendations: int = 10


class RecommendResponse(BaseModel):
    job_ids: List[int]
    scores: List[float]
    explanations: List[str]
    baseline: bool = True
    method: str = "most_recent"


@app.get("/")
async def root():
    return {"service": "job_recommender", "type": "baseline", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "job_recommender"}


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    Baseline recommendation: returns job IDs 1 to N.

    In a real implementation, this would:
    1. Query the database for recent jobs
    2. Apply collaborative filtering or content-based filtering
    3. Personalize based on candidate profile and history
    """
    n = request.num_recommendations

    # Baseline: sequential IDs with decreasing relevance scores
    job_ids = list(range(1, n + 1))
    scores = [round(1.0 / (i + 1), 3) for i in range(n)]
    explanations = ["Most recent posting"] * n

    return RecommendResponse(
        job_ids=job_ids,
        scores=scores,
        explanations=explanations,
        baseline=True,
        method="most_recent"
    )
