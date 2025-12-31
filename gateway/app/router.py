"""Service router - routes requests to ML services with fallback."""
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .config import get_config, ServiceConfig
from .fallback import get_fallback

logger = logging.getLogger(__name__)


class ServiceRouter:
    """Routes requests to ML services with fallback support."""

    def __init__(self):
        self.config = get_config()
        self.metrics: Dict[str, Dict[str, Any]] = {}

    async def call_service(
        self,
        service_name: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an ML service with automatic fallback.

        Args:
            service_name: Name of the service (e.g., 'job_recommender')
            request_data: Request payload to send to the service

        Returns:
            Response from the service or fallback
        """
        # Check for config updates
        self.config.check_reload()

        # Get service configuration
        service_config = self.config.get_service(service_name)

        # Record request
        self._record_request(service_name)

        # Try external endpoint first
        if service_config and service_config.enabled:
            try:
                result = await self._call_external(
                    service_name,
                    service_config,
                    request_data
                )
                self._record_success(service_name, external=True)
                return result

            except Exception as e:
                logger.warning(f"External service {service_name} failed: {e}")
                self._record_failure(service_name, str(e))

                # Fall back if enabled
                if self.config.gateway.fallback_enabled:
                    return await self._call_fallback(service_name, request_data)
                else:
                    raise

        # No external endpoint configured, use fallback
        return await self._call_fallback(service_name, request_data)

    async def _call_external(
        self,
        service_name: str,
        config: ServiceConfig,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an external ML service endpoint."""
        start_time = datetime.utcnow()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.endpoint,
                json=request_data,
                timeout=config.timeout
            )
            response.raise_for_status()
            result = response.json()

        # Record latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._record_latency(service_name, latency_ms)

        # Add metadata
        result["_meta"] = {
            "source": "external",
            "endpoint": config.endpoint,
            "latency_ms": latency_ms
        }

        return result

    async def _call_fallback(
        self,
        service_name: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call the baseline fallback implementation."""
        start_time = datetime.utcnow()

        fallback_handler = get_fallback(service_name)
        if not fallback_handler:
            raise ValueError(f"No fallback handler for service: {service_name}")

        result = fallback_handler(request_data)

        # Record latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._record_latency(service_name, latency_ms)
        self._record_success(service_name, external=False)

        # Add metadata
        result["_meta"] = {
            "source": "fallback",
            "latency_ms": latency_ms
        }

        return result

    def _record_request(self, service_name: str) -> None:
        """Record a request to a service."""
        if service_name not in self.metrics:
            self.metrics[service_name] = {
                "total_requests": 0,
                "external_success": 0,
                "fallback_success": 0,
                "failures": 0,
                "latencies": [],
                "last_error": None
            }
        self.metrics[service_name]["total_requests"] += 1

    def _record_success(self, service_name: str, external: bool) -> None:
        """Record a successful response."""
        if external:
            self.metrics[service_name]["external_success"] += 1
        else:
            self.metrics[service_name]["fallback_success"] += 1

    def _record_failure(self, service_name: str, error: str) -> None:
        """Record a failed request."""
        self.metrics[service_name]["failures"] += 1
        self.metrics[service_name]["last_error"] = {
            "message": error,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _record_latency(self, service_name: str, latency_ms: float) -> None:
        """Record response latency."""
        latencies = self.metrics[service_name]["latencies"]
        latencies.append(latency_ms)
        # Keep only last 100 latencies
        if len(latencies) > 100:
            self.metrics[service_name]["latencies"] = latencies[-100:]

    def get_metrics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for services."""
        if service_name:
            return self.metrics.get(service_name, {})
        return self.metrics

    def get_health(self) -> Dict[str, Any]:
        """Get health status for all services."""
        health = {}
        for name, config in self.config.services.items():
            metrics = self.metrics.get(name, {})

            # Calculate health status
            total = metrics.get("total_requests", 0)
            failures = metrics.get("failures", 0)

            if total == 0:
                status = "unknown"
            elif failures / total > 0.5:
                status = "degraded"
            elif failures / total > 0.1:
                status = "warning"
            else:
                status = "healthy"

            health[name] = {
                "status": status,
                "endpoint": config.endpoint,
                "enabled": config.enabled,
                "total_requests": total,
                "failure_rate": failures / total if total > 0 else 0,
                "last_error": metrics.get("last_error")
            }

        return health


# Global router instance
service_router = ServiceRouter()


def get_router() -> ServiceRouter:
    """Get the service router instance."""
    return service_router
