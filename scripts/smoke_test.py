"""Smoke tests for JobMatch platform.

Run this script to verify all services are working correctly.
Usage: py scripts/smoke_test.py
"""
import sys
import httpx
import asyncio
from typing import Tuple, List

# Service URLs
WEBAPP_URL = "http://localhost:8000"
GATEWAY_URL = "http://localhost:8001"
DASHBOARD_URL = "http://localhost:8002"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def success(msg: str):
    print(f"{Colors.GREEN}[PASS]{Colors.END} {msg}")


def fail(msg: str):
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")


def warn(msg: str):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")


def info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")


async def test_service(name: str, url: str, endpoint: str = "/health") -> Tuple[bool, str]:
    """Test if a service is responding."""
    full_url = f"{url}{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(full_url, timeout=5.0)
            if response.status_code == 200:
                return True, f"{name} is healthy"
            else:
                return False, f"{name} returned status {response.status_code}"
    except httpx.ConnectError:
        return False, f"{name} is not running at {url}"
    except Exception as e:
        return False, f"{name} error: {str(e)}"


async def test_gateway_service(service_name: str, endpoint: str, payload: dict) -> Tuple[bool, str]:
    """Test a specific ML service through the gateway."""
    url = f"{GATEWAY_URL}{endpoint}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                source = data.get("_meta", {}).get("source", data.get("method", "unknown"))
                return True, f"{service_name} responded (source: {source})"
            else:
                return False, f"{service_name} returned status {response.status_code}"
    except httpx.ConnectError:
        return False, f"Gateway not running at {GATEWAY_URL}"
    except Exception as e:
        return False, f"{service_name} error: {str(e)}"


async def run_smoke_tests() -> bool:
    """Run all smoke tests."""
    print("\n" + "=" * 60)
    print("JobMatch Platform - Smoke Tests")
    print("=" * 60 + "\n")

    all_passed = True
    results: List[Tuple[bool, str]] = []

    # Test core services
    info("Testing core services...")

    # Webapp
    passed, msg = await test_service("Webapp", WEBAPP_URL)
    results.append((passed, msg))
    if passed:
        success(msg)
    else:
        fail(msg)
        all_passed = False

    # Gateway
    passed, msg = await test_service("Gateway", GATEWAY_URL)
    results.append((passed, msg))
    if passed:
        success(msg)
    else:
        fail(msg)
        all_passed = False

    # Dashboard
    passed, msg = await test_service("Dashboard", DASHBOARD_URL)
    results.append((passed, msg))
    if passed:
        success(msg)
    else:
        fail(msg)
        all_passed = False

    print()

    # Test ML services through gateway (if gateway is running)
    gateway_running = results[1][0]

    if gateway_running:
        info("Testing ML services through gateway...")

        # Job Recommender
        passed, msg = await test_gateway_service(
            "Job Recommender",
            "/api/recommend",
            {"candidate_id": 1, "num_recommendations": 5}
        )
        results.append((passed, msg))
        if passed:
            success(msg)
        else:
            fail(msg)
            all_passed = False

        # Salary Predictor
        passed, msg = await test_gateway_service(
            "Salary Predictor",
            "/api/predict-salary",
            {"job_title": "Software Engineer", "location": "San Francisco"}
        )
        results.append((passed, msg))
        if passed:
            success(msg)
        else:
            fail(msg)
            all_passed = False

        # Candidate Ranker
        passed, msg = await test_gateway_service(
            "Candidate Ranker",
            "/api/rank-candidates",
            {"job_id": 1, "candidate_profiles": [{"id": 1}, {"id": 2}]}
        )
        results.append((passed, msg))
        if passed:
            success(msg)
        else:
            fail(msg)
            all_passed = False

        # Resume Parser
        passed, msg = await test_gateway_service(
            "Resume Parser",
            "/api/parse-resume",
            {"resume_text": "Experienced Python developer with 5 years experience in machine learning"}
        )
        results.append((passed, msg))
        if passed:
            success(msg)
        else:
            fail(msg)
            all_passed = False

        # Demand Forecaster
        passed, msg = await test_gateway_service(
            "Demand Forecaster",
            "/api/forecast-demand",
            {"skill_category": "Python", "forecast_horizon": 3}
        )
        results.append((passed, msg))
        if passed:
            success(msg)
        else:
            fail(msg)
            all_passed = False

        # Candidate Segmenter
        passed, msg = await test_gateway_service(
            "Candidate Segmenter",
            "/api/segment-candidates",
            {"candidate_profiles": [{"id": 1}, {"id": 2}, {"id": 3}], "num_clusters": 2}
        )
        results.append((passed, msg))
        if passed:
            success(msg)
        else:
            fail(msg)
            all_passed = False

    else:
        warn("Skipping ML service tests (gateway not running)")

    # Test webapp pages
    print()
    info("Testing webapp pages...")

    webapp_running = results[0][0]
    if webapp_running:
        pages = [
            ("/", "Home page"),
            ("/jobs", "Jobs listing"),
            ("/auth/login", "Login page"),
            ("/auth/register", "Register page"),
        ]
        for endpoint, name in pages:
            passed, msg = await test_service(name, WEBAPP_URL, endpoint)
            results.append((passed, msg))
            if passed:
                success(msg)
            else:
                fail(msg)
                all_passed = False
    else:
        warn("Skipping webapp page tests (webapp not running)")

    # Summary
    print("\n" + "=" * 60)
    passed_count = sum(1 for r in results if r[0])
    total_count = len(results)

    if all_passed:
        success(f"All tests passed! ({passed_count}/{total_count})")
    else:
        fail(f"Some tests failed ({passed_count}/{total_count} passed)")

    print("=" * 60 + "\n")

    return all_passed


def main():
    """Main entry point."""
    try:
        all_passed = asyncio.run(run_smoke_tests())
        sys.exit(0 if all_passed else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
