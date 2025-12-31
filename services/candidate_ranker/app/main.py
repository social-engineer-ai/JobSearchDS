"""Candidate Ranker Baseline Service.

This baseline uses FIFO ordering (first applied, first shown).
Students will replace this with learning-to-rank models.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Candidate Ranker Service (Baseline)",
    description="Returns candidates in FIFO order - no ML ranking",
    version="1.0.0"
)


class RankRequest(BaseModel):
    job_id: int
    job_requirements: Optional[Dict[str, Any]] = None
    candidate_profiles: List[Dict[str, Any]]
    historical_hires: Optional[List[Dict[str, Any]]] = None


class RankResponse(BaseModel):
    ranked_candidate_ids: List[int]
    match_scores: List[int]
    match_reasons: List[str]
    baseline: bool = True
    method: str = "fifo"


@app.get("/")
async def root():
    return {"service": "candidate_ranker", "type": "baseline", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "candidate_ranker"}


@app.post("/rank", response_model=RankResponse)
async def rank(request: RankRequest):
    """
    Baseline ranking: FIFO (first-in, first-out).

    In a real implementation, this would:
    1. Use classification or learning-to-rank models
    2. Match skills, experience, education to requirements
    3. Learn from historical hiring decisions
    """
    candidates = request.candidate_profiles

    # Extract IDs from profiles
    candidate_ids = []
    for i, c in enumerate(candidates):
        if isinstance(c, dict) and "id" in c:
            candidate_ids.append(c["id"])
        else:
            candidate_ids.append(i + 1)

    # FIFO ordering - all get same score
    match_scores = [50] * len(candidate_ids)
    match_reasons = ["Application order (FIFO)"] * len(candidate_ids)

    return RankResponse(
        ranked_candidate_ids=candidate_ids,
        match_scores=match_scores,
        match_reasons=match_reasons,
        baseline=True,
        method="fifo"
    )
