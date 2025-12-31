"""Candidate Segmenter Baseline Service.

This baseline uses simple category grouping.
Students will replace this with clustering algorithms.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Candidate Segmenter Service (Baseline)",
    description="Groups by category - no ML clustering",
    version="1.0.0"
)


class SegmentRequest(BaseModel):
    candidate_profiles: List[Dict[str, Any]]
    feature_set: Optional[List[str]] = None
    num_clusters: Optional[int] = 3


class SegmentResponse(BaseModel):
    cluster_assignments: List[int]
    cluster_descriptions: List[str]
    cluster_centroids: List[Dict[str, Any]]
    baseline: bool = True
    method: str = "category_grouping"


@app.get("/")
async def root():
    return {"service": "candidate_segmenter", "type": "baseline", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "candidate_segmenter"}


@app.post("/segment", response_model=SegmentResponse)
async def segment(request: SegmentRequest):
    """
    Baseline segmentation: round-robin assignment.

    In a real implementation, this would:
    1. Use K-Means, DBSCAN, or hierarchical clustering
    2. Create meaningful segments based on features
    3. Generate interpretable cluster descriptions
    """
    candidates = request.candidate_profiles
    num_clusters = request.num_clusters or 3

    # Simple round-robin assignment
    assignments = [i % num_clusters for i in range(len(candidates))]

    # Generic descriptions
    descriptions = [
        f"Segment {i+1} - General candidates"
        for i in range(num_clusters)
    ]

    return SegmentResponse(
        cluster_assignments=assignments,
        cluster_descriptions=descriptions,
        cluster_centroids=[],
        baseline=True,
        method="category_grouping"
    )
