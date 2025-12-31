"""Demand Forecaster Baseline Service.

This baseline returns flat projections (no actual forecasting).
Students will replace this with time series models.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Demand Forecaster Service (Baseline)",
    description="Returns flat projections - no time series forecasting",
    version="1.0.0"
)


class ForecastRequest(BaseModel):
    skill_category: str
    industry: Optional[str] = None
    location: Optional[str] = None
    historical_postings: Optional[List[Dict[str, Any]]] = None
    forecast_horizon: int = 6  # months


class ForecastResponse(BaseModel):
    forecast_periods: List[str]
    predicted_demand: List[int]
    confidence_bounds: List[List[int]]
    baseline: bool = True
    method: str = "flat_projection"


@app.get("/")
async def root():
    return {"service": "demand_forecaster", "type": "baseline", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "demand_forecaster"}


@app.post("/forecast", response_model=ForecastResponse)
async def forecast(request: ForecastRequest):
    """
    Baseline forecasting: flat projection of current demand.

    In a real implementation, this would:
    1. Use ARIMA, Prophet, or LSTM models
    2. Consider seasonality and trends
    3. Factor in economic indicators
    """
    horizon = request.forecast_horizon

    # Baseline: assume constant demand
    current_demand = 100

    # Generate periods
    periods = [f"month_{i+1}" for i in range(horizon)]

    # Flat projection
    predicted = [current_demand] * horizon

    # Wide confidence bounds
    bounds = [[int(current_demand * 0.6), int(current_demand * 1.4)] for _ in range(horizon)]

    return ForecastResponse(
        forecast_periods=periods,
        predicted_demand=predicted,
        confidence_bounds=bounds,
        baseline=True,
        method="flat_projection"
    )
