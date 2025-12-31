"""Tests for gateway fallback implementations."""
import pytest
from gateway.app.fallback import BaselineFallbacks, get_fallback, FALLBACK_HANDLERS


class TestJobRecommender:
    """Test job recommender fallback."""

    def test_returns_correct_structure(self):
        """Test that response has required fields."""
        result = BaselineFallbacks.job_recommender({"candidate_id": 1})
        assert "job_ids" in result
        assert "scores" in result
        assert "explanations" in result
        assert result["baseline"] is True
        assert result["method"] == "most_recent"

    def test_respects_num_recommendations(self):
        """Test that num_recommendations is respected."""
        result = BaselineFallbacks.job_recommender({"num_recommendations": 5})
        assert len(result["job_ids"]) == 5
        assert len(result["scores"]) == 5
        assert len(result["explanations"]) == 5

    def test_default_recommendations(self):
        """Test default number of recommendations."""
        result = BaselineFallbacks.job_recommender({})
        assert len(result["job_ids"]) == 10  # Default


class TestSalaryPredictor:
    """Test salary predictor fallback."""

    def test_returns_correct_structure(self):
        """Test that response has required fields."""
        result = BaselineFallbacks.salary_predictor({"job_title": "Software Engineer"})
        assert "predicted_salary" in result
        assert "confidence_interval" in result
        assert len(result["confidence_interval"]) == 2
        assert result["baseline"] is True

    def test_known_title_salary(self):
        """Test known job title returns correct average."""
        result = BaselineFallbacks.salary_predictor({"job_title": "software engineer"})
        assert result["predicted_salary"] == 130000

    def test_unknown_title_uses_default(self):
        """Test unknown job title uses default salary."""
        result = BaselineFallbacks.salary_predictor({"job_title": "unknown job"})
        assert result["predicted_salary"] == 100000

    def test_confidence_interval_bounds(self):
        """Test confidence interval is properly calculated."""
        result = BaselineFallbacks.salary_predictor({"job_title": "data scientist"})
        salary = result["predicted_salary"]
        low, high = result["confidence_interval"]
        assert low == int(salary * 0.7)
        assert high == int(salary * 1.3)


class TestCandidateRanker:
    """Test candidate ranker fallback."""

    def test_returns_correct_structure(self):
        """Test that response has required fields."""
        result = BaselineFallbacks.candidate_ranker({
            "job_id": 1,
            "candidate_profiles": [{"id": 1}, {"id": 2}]
        })
        assert "ranked_candidate_ids" in result
        assert "match_scores" in result
        assert "match_reasons" in result
        assert result["baseline"] is True
        assert result["method"] == "fifo"

    def test_extracts_candidate_ids(self):
        """Test that candidate IDs are extracted from dicts."""
        result = BaselineFallbacks.candidate_ranker({
            "candidate_profiles": [{"id": 10}, {"id": 20}, {"id": 30}]
        })
        assert result["ranked_candidate_ids"] == [10, 20, 30]

    def test_uniform_scores(self):
        """Test all candidates get same score (FIFO)."""
        result = BaselineFallbacks.candidate_ranker({
            "candidate_profiles": [{"id": 1}, {"id": 2}, {"id": 3}]
        })
        assert result["match_scores"] == [50, 50, 50]


class TestResumeParser:
    """Test resume parser fallback."""

    def test_returns_correct_structure(self):
        """Test that response has required fields."""
        result = BaselineFallbacks.resume_parser({"resume_text": "Python developer"})
        assert "skills" in result
        assert "experience_years" in result
        assert "education" in result
        assert "work_history" in result
        assert result["baseline"] is True

    def test_finds_skills(self):
        """Test that skills are extracted from text."""
        result = BaselineFallbacks.resume_parser({
            "resume_text": "Expert in Python, JavaScript, and React with AWS experience"
        })
        assert "python" in result["skills"]
        assert "javascript" in result["skills"]
        assert "react" in result["skills"]
        assert "aws" in result["skills"]

    def test_extracts_experience_years(self):
        """Test that experience years are extracted."""
        result = BaselineFallbacks.resume_parser({
            "resume_text": "5 years of experience in software development"
        })
        assert result["experience_years"] == 5

    def test_empty_resume(self):
        """Test handling of empty resume."""
        result = BaselineFallbacks.resume_parser({"resume_text": ""})
        assert result["skills"] == []
        assert result["experience_years"] == 0


class TestDemandForecaster:
    """Test demand forecaster fallback."""

    def test_returns_correct_structure(self):
        """Test that response has required fields."""
        result = BaselineFallbacks.demand_forecaster({"skill_category": "Python"})
        assert "forecast_periods" in result
        assert "predicted_demand" in result
        assert "confidence_bounds" in result
        assert result["baseline"] is True
        assert result["method"] == "flat_projection"

    def test_respects_forecast_horizon(self):
        """Test that forecast_horizon is respected."""
        result = BaselineFallbacks.demand_forecaster({"forecast_horizon": 6})
        assert len(result["forecast_periods"]) == 6
        assert len(result["predicted_demand"]) == 6


class TestCandidateSegmenter:
    """Test candidate segmenter fallback."""

    def test_returns_correct_structure(self):
        """Test that response has required fields."""
        result = BaselineFallbacks.candidate_segmenter({
            "candidate_profiles": [{"id": 1}, {"id": 2}]
        })
        assert "cluster_assignments" in result
        assert "cluster_descriptions" in result
        assert result["baseline"] is True

    def test_respects_num_clusters(self):
        """Test that num_clusters is respected."""
        result = BaselineFallbacks.candidate_segmenter({
            "candidate_profiles": [{"id": i} for i in range(10)],
            "num_clusters": 2
        })
        assert len(result["cluster_descriptions"]) == 2
        assert all(a in [0, 1] for a in result["cluster_assignments"])


class TestGetFallback:
    """Test fallback handler lookup."""

    def test_all_services_have_handlers(self):
        """Test that all services have fallback handlers."""
        services = [
            "job_recommender",
            "salary_predictor",
            "candidate_ranker",
            "resume_parser",
            "demand_forecaster",
            "candidate_segmenter"
        ]
        for service in services:
            handler = get_fallback(service)
            assert handler is not None, f"Missing handler for {service}"
            assert callable(handler)

    def test_unknown_service_returns_none(self):
        """Test that unknown service returns None."""
        assert get_fallback("unknown_service") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
