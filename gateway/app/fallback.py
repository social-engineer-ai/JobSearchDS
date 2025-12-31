"""Baseline (fallback) implementations for all ML services.

These are simple rule-based implementations that provide basic functionality
when ML services are unavailable or student endpoints fail.
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random


class BaselineFallbacks:
    """Collection of baseline implementations for ML services."""

    @staticmethod
    def job_recommender(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baseline job recommender - returns most recent jobs.

        Input: { candidate_id, candidate_profile, interaction_history, num_recommendations }
        Output: { job_ids: [], scores: [], explanations: [] }
        """
        num_recommendations = request.get("num_recommendations", 10)

        # In baseline, we just return sequential IDs (would query DB in real impl)
        job_ids = list(range(1, num_recommendations + 1))
        scores = [1.0 / (i + 1) for i in range(num_recommendations)]  # Decreasing scores
        explanations = ["Based on recency"] * num_recommendations

        return {
            "job_ids": job_ids,
            "scores": scores,
            "explanations": explanations,
            "baseline": True,
            "method": "most_recent"
        }

    @staticmethod
    def salary_predictor(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baseline salary predictor - returns industry averages.

        Input: { job_title, location, company_size, industry, required_skills, experience_range }
        Output: { predicted_salary, confidence_interval: [low, high], comparable_jobs: [] }
        """
        # Simple lookup table for average salaries by title
        title_averages = {
            "software engineer": 130000,
            "senior software engineer": 165000,
            "data scientist": 140000,
            "machine learning engineer": 155000,
            "product manager": 145000,
            "frontend developer": 110000,
            "backend developer": 125000,
            "devops engineer": 135000,
            "default": 100000
        }

        job_title = request.get("job_title", "").lower()
        base_salary = title_averages.get(job_title, title_averages["default"])

        # Wide confidence interval (baseline is uncertain)
        low = int(base_salary * 0.7)
        high = int(base_salary * 1.3)

        return {
            "predicted_salary": base_salary,
            "confidence_interval": [low, high],
            "comparable_jobs": [],
            "baseline": True,
            "method": "industry_average"
        }

    @staticmethod
    def candidate_ranker(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baseline candidate ranker - FIFO ordering.

        Input: { job_id, job_requirements, candidate_profiles: [], historical_hires: [] }
        Output: { ranked_candidate_ids: [], match_scores: [], match_reasons: [] }
        """
        candidates = request.get("candidate_profiles", [])

        # Extract IDs if candidates are dicts, otherwise use as-is
        if candidates and isinstance(candidates[0], dict):
            candidate_ids = [c.get("id", i) for i, c in enumerate(candidates)]
        else:
            candidate_ids = list(range(len(candidates)))

        # FIFO ordering with uniform scores
        return {
            "ranked_candidate_ids": candidate_ids,
            "match_scores": [50] * len(candidate_ids),  # All get same score
            "match_reasons": ["Application order (FIFO)"] * len(candidate_ids),
            "baseline": True,
            "method": "fifo"
        }

    @staticmethod
    def resume_parser(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baseline resume parser - keyword matching.

        Input: { resume_text, resume_format }
        Output: { skills: [], experience_years, education: {}, work_history: [], summary }
        """
        resume_text = request.get("resume_text", "").lower()

        # Simple keyword matching for skills
        skill_keywords = [
            "python", "javascript", "java", "sql", "react", "node.js",
            "aws", "docker", "kubernetes", "machine learning", "data science",
            "tensorflow", "pytorch", "pandas", "git", "agile"
        ]

        found_skills = [skill for skill in skill_keywords if skill in resume_text]

        # Try to extract years of experience with simple pattern
        experience_years = 0
        import re
        year_patterns = re.findall(r'(\d+)\+?\s*years?', resume_text)
        if year_patterns:
            experience_years = max(int(y) for y in year_patterns)

        return {
            "skills": found_skills,
            "experience_years": experience_years,
            "education": {},
            "work_history": [],
            "summary": resume_text[:200] if resume_text else "",
            "baseline": True,
            "method": "keyword_matching"
        }

    @staticmethod
    def demand_forecaster(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baseline demand forecaster - returns current count only.

        Input: { skill_category, industry, location, historical_postings: [], forecast_horizon }
        Output: { forecast_periods: [], predicted_demand: [], confidence_bounds: [] }
        """
        forecast_horizon = request.get("forecast_horizon", 3)

        # No actual forecasting - just returns flat projection
        current_demand = 100  # Placeholder

        periods = [f"month_{i+1}" for i in range(forecast_horizon)]
        demands = [current_demand] * forecast_horizon
        bounds = [[current_demand * 0.8, current_demand * 1.2]] * forecast_horizon

        return {
            "forecast_periods": periods,
            "predicted_demand": demands,
            "confidence_bounds": bounds,
            "baseline": True,
            "method": "flat_projection"
        }

    @staticmethod
    def candidate_segmenter(request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Baseline candidate segmenter - groups by category only.

        Input: { candidate_profiles: [], feature_set, num_clusters (optional) }
        Output: { cluster_assignments: [], cluster_descriptions: [], cluster_centroids: [] }
        """
        candidates = request.get("candidate_profiles", [])
        num_clusters = request.get("num_clusters", 3)

        # Simple assignment based on index modulo
        assignments = [i % num_clusters for i in range(len(candidates))]

        descriptions = [
            "General candidates - Group A",
            "General candidates - Group B",
            "General candidates - Group C",
        ][:num_clusters]

        return {
            "cluster_assignments": assignments,
            "cluster_descriptions": descriptions,
            "cluster_centroids": [],
            "baseline": True,
            "method": "category_grouping"
        }


# Mapping of service names to fallback functions
FALLBACK_HANDLERS = {
    "job_recommender": BaselineFallbacks.job_recommender,
    "salary_predictor": BaselineFallbacks.salary_predictor,
    "candidate_ranker": BaselineFallbacks.candidate_ranker,
    "resume_parser": BaselineFallbacks.resume_parser,
    "demand_forecaster": BaselineFallbacks.demand_forecaster,
    "candidate_segmenter": BaselineFallbacks.candidate_segmenter,
}


def get_fallback(service_name: str):
    """Get the fallback handler for a service."""
    return FALLBACK_HANDLERS.get(service_name)
