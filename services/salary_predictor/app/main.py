"""Salary Predictor Baseline Service.

This baseline returns industry averages from a lookup table.
Students will replace this with regression models.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Salary Predictor Service (Baseline)",
    description="Returns industry average salaries - no ML prediction",
    version="1.0.0"
)

# Simple lookup table for average salaries
SALARY_AVERAGES = {
    "software engineer": 130000,
    "senior software engineer": 165000,
    "staff software engineer": 200000,
    "principal engineer": 230000,
    "data scientist": 140000,
    "senior data scientist": 170000,
    "machine learning engineer": 155000,
    "senior machine learning engineer": 185000,
    "product manager": 145000,
    "senior product manager": 175000,
    "frontend developer": 110000,
    "backend developer": 125000,
    "full stack developer": 130000,
    "devops engineer": 135000,
    "data analyst": 85000,
    "business analyst": 90000,
    "ux designer": 105000,
    "default": 100000
}


class PredictRequest(BaseModel):
    job_title: str
    location: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    required_skills: Optional[List[str]] = None
    experience_range: Optional[str] = None


class PredictResponse(BaseModel):
    predicted_salary: int
    confidence_interval: List[int]
    comparable_jobs: List[dict]
    baseline: bool = True
    method: str = "industry_average"


@app.get("/")
async def root():
    return {"service": "salary_predictor", "type": "baseline", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "salary_predictor"}


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    Baseline prediction: lookup table by job title.

    In a real implementation, this would:
    1. Use regression models (Linear, GBM, Neural Network)
    2. Consider location, company size, skills, experience
    3. Provide calibrated confidence intervals
    """
    # Normalize title for lookup
    title_lower = request.job_title.lower().strip()

    # Find matching salary
    base_salary = SALARY_AVERAGES.get(title_lower, SALARY_AVERAGES["default"])

    # Wide confidence interval (baseline is uncertain)
    low = int(base_salary * 0.7)
    high = int(base_salary * 1.3)

    return PredictResponse(
        predicted_salary=base_salary,
        confidence_interval=[low, high],
        comparable_jobs=[],
        baseline=True,
        method="industry_average"
    )
