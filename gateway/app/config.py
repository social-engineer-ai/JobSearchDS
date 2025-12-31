"""Gateway configuration with hot-reload support."""
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ServiceConfig(BaseModel):
    """Configuration for a single ML service."""
    endpoint: str
    timeout: float = 5.0
    enabled: bool = True


class GatewaySettings(BaseModel):
    """Gateway-level settings."""
    fallback_enabled: bool = True
    log_requests: bool = True
    log_responses: bool = True
    max_retries: int = 1


class ConfigManager:
    """Manages service configuration with hot-reload."""

    def __init__(self, config_path: str = "config/services.yaml"):
        self.config_path = Path(config_path)
        self.services: Dict[str, ServiceConfig] = {}
        self.gateway: GatewaySettings = GatewaySettings()
        self.last_loaded: Optional[datetime] = None
        self._last_mtime: float = 0

    def load(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            self._load_defaults()
            return

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Parse services
            services_config = config.get('services', {})
            self.services = {}
            for name, settings in services_config.items():
                if isinstance(settings, dict):
                    self.services[name] = ServiceConfig(**settings)
                elif isinstance(settings, str):
                    # Simple endpoint string
                    self.services[name] = ServiceConfig(endpoint=settings)

            # Parse gateway settings
            gateway_config = config.get('gateway', {})
            self.gateway = GatewaySettings(**gateway_config)

            self.last_loaded = datetime.utcnow()
            self._last_mtime = self.config_path.stat().st_mtime
            logger.info(f"Loaded configuration from {self.config_path}")

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default configuration."""
        self.services = {
            "job_recommender": ServiceConfig(endpoint="http://localhost:5001/recommend"),
            "salary_predictor": ServiceConfig(endpoint="http://localhost:5002/predict"),
            "candidate_ranker": ServiceConfig(endpoint="http://localhost:5003/rank"),
            "resume_parser": ServiceConfig(endpoint="http://localhost:5004/parse", timeout=10.0),
            "demand_forecaster": ServiceConfig(endpoint="http://localhost:5005/forecast"),
            "candidate_segmenter": ServiceConfig(endpoint="http://localhost:5006/segment"),
        }
        self.gateway = GatewaySettings()
        logger.info("Loaded default configuration")

    def check_reload(self) -> bool:
        """Check if config file has changed and reload if needed."""
        if not self.config_path.exists():
            return False

        current_mtime = self.config_path.stat().st_mtime
        if current_mtime > self._last_mtime:
            logger.info("Configuration file changed, reloading...")
            self.load()
            return True
        return False

    def get_service(self, name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service."""
        return self.services.get(name)

    def get_endpoint(self, name: str) -> Optional[str]:
        """Get endpoint URL for a service."""
        service = self.get_service(name)
        return service.endpoint if service and service.enabled else None


# Global config instance
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """Get the configuration manager instance."""
    return config_manager
