"""JobMatch Dashboard Service - Monitoring and Metrics.

Provides real-time visibility into service health and business metrics.
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import httpx
import os

app = FastAPI(
    title="JobMatch Dashboard",
    description="Real-time monitoring of ML services and business metrics",
    version="1.0.0"
)

# Setup templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Gateway URL
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8001")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "JobMatch Dashboard"}
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dashboard"}


@app.get("/api/gateway-health")
async def gateway_health():
    """Fetch health status from gateway."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/health", timeout=5.0)
            return response.json()
    except Exception as e:
        return {"error": str(e), "gateway_url": GATEWAY_URL}


@app.get("/api/gateway-metrics")
async def gateway_metrics():
    """Fetch metrics from gateway."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/metrics", timeout=5.0)
            return response.json()
    except Exception as e:
        return {"error": str(e), "gateway_url": GATEWAY_URL}


@app.get("/api/gateway-config")
async def gateway_config():
    """Fetch configuration from gateway."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GATEWAY_URL}/config", timeout=5.0)
            return response.json()
    except Exception as e:
        return {"error": str(e), "gateway_url": GATEWAY_URL}
